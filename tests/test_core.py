"""Tests for the core: snapshots, the part loader, the runner, the symbol lookup and the grader.

The parts carry their own cases (parts/*.cases.json), run by `ws.py selftest`
and by test_every_part_passes_its_own_cases below.

Run: python3 -m unittest discover -b tests
"""
import contextlib
import io
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "evals"))
sys.path.insert(0, str(ROOT / "tools"))

import grade  # noqa: E402
import symbols as symbols_cli  # noqa: E402
import ws  # noqa: E402
from wslib import parts as partlib  # noqa: E402
from wslib import snapshot as snapshots  # noqa: E402
from wslib import symbols  # noqa: E402

STALE = "---\nlast-reviewed: 2020-01-01\n---\n# Old\n"


def claude(tool, cwd=None, **tool_input):
    """A Claude Code PreToolUse payload, as the tool sends it to a hook."""
    payload = {"session_id": "s", "transcript_path": "/t.jsonl", "permission_mode": "default",
               "hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": tool_input}
    if cwd is not None:
        payload["cwd"] = str(cwd)
    return json.dumps(payload)


class Folder(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name).resolve()
        self.addCleanup(self._tmp.cleanup)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), "-c", "user.name=t", "-c", "user.email=t@example.invalid",
                               "-c", "commit.gpgsign=false", *args], check=True, capture_output=True, text=True)

    def ws(self, *args, stdin=""):
        out, err = io.StringIO(), io.StringIO()
        old = sys.stdin
        sys.stdin = io.StringIO(stdin)
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = ws.main(["--root", str(self.root), *args])
        finally:
            sys.stdin = old
        return code, out.getvalue() + err.getvalue()

    def workspace(self, *entries):
        """A workspace that borrows this repository's real parts."""
        self.write("workspace.json", json.dumps({"parts": list(entries)}))
        for entry in entries:
            for suffix in (".py", ".cases.json"):
                source = ROOT / "parts" / (entry["use"] + suffix)
                self.write(f"parts/{entry['use']}{suffix}", source.read_text(encoding="utf-8"))


class SnapshotTests(Folder):
    def test_the_index_holds_what_is_staged_not_what_is_on_disk(self):
        self.git("init", "-q")
        self.write("a.md", "staged\n")
        self.git("add", "a.md")
        self.write("a.md", "edited after staging\n")
        self.write("untracked.md", "[broken](nope.md)\n")
        index = snapshots.Index(self.root)
        self.assertEqual(list(index.paths()), ["a.md"])
        self.assertEqual(index.read("a.md"), "staged\n")
        self.assertEqual(index.changed, {"a.md"})

    def test_staged_names_with_spaces_and_accents_survive(self):
        self.git("init", "-q")
        self.write("docs/my page.md", STALE)
        self.write("docs/café.md", STALE)
        self.git("add", "docs")
        self.assertEqual(snapshots.Index(self.root).changed, {"docs/my page.md", "docs/café.md"})

    def test_a_staged_submodule_is_read_from_its_pinned_checkout(self):
        code = self.root / "code"
        code.mkdir()
        (code / "Worker.cs").write_text("public class NightlyWorker { }\n", encoding="utf-8")
        for args in (["init", "-q"], ["add", "."], ["-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "-m", "code"]):
            subprocess.run(["git", "-C", str(code), *args], check=True, capture_output=True)
        work = self.root / "ws"
        work.mkdir()
        self.root = work
        self.git("init", "-q")
        self.git("-c", "protocol.file.allow=always", "submodule", "add", "-q", str(code), "src/code")
        self.write("a.md", "[the worker](src/code/Worker.cs)\n")
        self.git("add", "a.md")
        index = snapshots.Index(self.root)
        self.assertTrue(index.exists("src/code/Worker.cs"))
        self.assertEqual([s[3] for s in symbols.scan(index, "src")], ["NightlyWorker"])

    def test_a_dangling_symlink_is_not_a_file(self):
        try:
            (self.root / "ghost.md").symlink_to(self.root / "nowhere.md")
        except OSError:
            self.skipTest("symlinks are not available here")
        self.assertEqual(list(snapshots.Tree(self.root).paths()), [])

    def test_existence_is_case_sensitive_and_knows_folders(self):
        memory = snapshots.Memory({"docs/Upper.md": "x"})
        self.assertTrue(memory.exists("docs/Upper.md"))
        self.assertTrue(memory.exists("docs"))
        self.assertFalse(memory.exists("docs/upper.md"))
        self.assertFalse(memory.exists("doc"))

    def test_a_file_that_is_not_utf8_reads_as_none(self):
        self.assertIsNone(snapshots.Memory({"a.md": b"\xff\xfe\x00bad"}).read("a.md"))

    def test_a_missing_root_is_an_error_not_an_empty_pass(self):
        with self.assertRaises(NotADirectoryError):
            snapshots.Tree(self.root / "nope")

    def test_changed_since_reports_why_it_cannot_compare(self):
        self.git("init", "-q")
        self.assertEqual(snapshots.changed_since(self.root, "0" * 40)[0], [])
        self.assertIn("cannot compare", snapshots.changed_since(self.root, "no-such-ref")[1])


class LoaderTests(Folder):
    def part(self, name, body, cases):
        self.write(f"parts/{name}.py", body)
        if cases is not None:
            self.write(f"parts/{name}.cases.json", json.dumps(cases))
        return partlib.load(self.root, {"use": name}, run_cases=False)

    def test_a_part_with_no_cases_is_refused(self):
        with self.assertRaisesRegex(partlib.PartError, "refused, it has no cases file"):
            self.part("quiet", 'KIND = "check"\ndef run(snapshot, config):\n    return []\n', None)

    def test_a_check_whose_cases_never_find_anything_is_refused(self):
        with self.assertRaisesRegex(partlib.PartError, "no case shows it finding anything"):
            self.part("quiet", 'KIND = "check"\ndef run(snapshot, config):\n    return []\n',
                      [{"name": "clean", "files": {}, "expect": []}])

    def test_a_hook_must_show_both_answers(self):
        with self.assertRaisesRegex(partlib.PartError, "both allowing and refusing"):
            self.part("yes", 'KIND = "hook"\nEVENT = "before-shell"\ndef decide(event, config):\n    return None\n',
                      [{"name": "always", "event": {}, "allow": True}])

    def test_a_failing_case_is_reported_by_name(self):
        part = self.part("never", 'KIND = "check"\ndef run(snapshot, config):\n    return []\n',
                         [{"name": "should find it", "files": {"a.md": "x"}, "expect": ["something"]}])
        self.assertEqual(part.failed_cases(), ["should find it: missing ['something (error)'], unexpected []"])

    def test_a_case_that_crashes_the_part_is_a_failed_case(self):
        part = self.part("boom", 'KIND = "check"\ndef run(snapshot, config):\n    raise ValueError("no")\n',
                         [{"name": "crash", "files": {}, "expect": ["x"]}])
        self.assertEqual(part.failed_cases(), ["crash: part boom crashed: ValueError: no"])

    def test_an_unknown_part_and_a_bad_manifest_are_named(self):
        with self.assertRaisesRegex(partlib.PartError, "no file at parts/ghost.py"):
            partlib.load(self.root, {"use": "ghost"})
        with self.assertRaisesRegex(partlib.PartError, "no workspace.json"):
            partlib.load_manifest(self.root)


class RunnerTests(Folder):
    def test_check_reports_an_error_and_exits_1(self):
        self.workspace({"use": "links"})
        self.write("a.md", "[gone](nope.md)\n")
        code, output = self.ws("check")
        self.assertEqual(code, 1)
        self.assertIn("error: a.md:1: link to missing file: nope.md  [links]", output)

    def test_a_stale_page_is_a_warning_until_it_is_changed(self):
        self.workspace({"use": "freshness"})
        self.write("old.md", STALE)
        self.assertEqual(self.ws("check")[0], 0)
        self.assertEqual(self.ws("check", "--changed", "old.md")[0], 1)

    def test_staged_check_ignores_unstaged_fixes_and_untracked_files(self):
        self.workspace({"use": "links"}, {"use": "freshness"})
        self.git("init", "-q")
        self.git("add", ".")
        self.git("commit", "-q", "-m", "workspace")
        self.write("docs/my page.md", STALE)
        self.git("add", "docs")
        self.write("docs/my page.md", "---\nlast-reviewed: 2999-01-01\n---\nfixed on disk only\n")
        self.write("scratch.md", "[broken](nope.md)\n")
        code, output = self.ws("check", "--staged")
        self.assertEqual(code, 1)
        self.assertIn("docs/my page.md", output)
        self.assertNotIn("scratch.md", output)

    def test_changed_from_a_base_commit(self):
        self.workspace({"use": "freshness"})
        self.write("old.md", STALE)
        self.git("init", "-q")
        self.git("add", ".")
        self.git("commit", "-q", "-m", "base")
        base = self.git("rev-parse", "HEAD").stdout.strip()
        self.assertEqual(self.ws("check", "--changed-from", base)[0], 0)
        self.write("old.md", STALE + "\nOne more line.\n")
        self.git("commit", "-q", "-am", "edit")
        self.assertEqual(self.ws("check", "--changed-from", base)[0], 1)

    def test_hooks_refuse_with_exit_2_and_a_reason_and_remind_with_exit_0(self):
        self.workspace({"use": "no_stage_all"}, {"use": "shelved", "paths": ["src/old"]})
        code, output = self.ws("hook", "before-shell", stdin='{"version": 1, "command": "git add -A"}')
        self.assertEqual(code, 0)
        self.assertIn("Reminder: no_stage_all: This command stages more than it names", output)
        self.assertEqual(self.ws("hook", "before-shell", stdin='{"version": 1, "command": "git add a.md"}'), (0, ""))
        code, output = self.ws("hook", "before-edit", stdin='{"version": 1, "path": "src/old/x.cs"}')
        self.assertEqual(code, 2)
        self.assertIn("Refused by shelved", output)
        self.assertEqual(self.ws("hook", "before-edit", stdin='{"version": 1, "path": "src/old/x.cs"}')[0], 2)
        self.assertEqual(self.ws("hook", "before-edit", stdin='{"version": 1, "path": "src/new/x.cs"}')[0], 0)

    def test_hooks_read_an_agent_tool_payload_with_an_absolute_path(self):
        self.workspace({"use": "shelved", "paths": ["src/old"]})
        payload = claude("Edit", file_path=str(self.root / "src/old/x.cs"))
        self.assertEqual(self.ws("hook", "before-edit", "--tool", "claude-code", stdin=payload)[0], 2)
        payload = claude("Bash", command="git commit -am x")
        self.workspace({"use": "no_stage_all"})
        code, output = self.ws("hook", "before-shell", "--tool", "claude-code", stdin=payload)
        self.assertEqual(code, 0)
        context = json.loads(output)["hookSpecificOutput"]
        self.assertEqual(context["hookEventName"], "PreToolUse")
        self.assertIn("git commit -a stages every tracked change", context["additionalContext"])

    def test_a_part_whose_case_fails_is_refused_on_every_command_not_only_selftest(self):
        self.workspace({"use": "links"})
        self.write("parts/links.cases.json", json.dumps([{"name": "wrong", "files": {"a.md": "x"}, "expect": ["nothing like this"]}]))
        for command in (["check"], ["check", "--changed", "a.md"], ["list"]):
            code, output = self.ws(*command)
            self.assertEqual(code, 2, command)
            self.assertIn("refused, 1 of its 1 cases fail", output)
        self.assertEqual(self.ws("selftest")[0], 1)

    def test_a_part_that_crashes_or_returns_nonsense_is_an_error_not_a_traceback(self):
        cases = json.dumps([{"name": "c", "files": {}, "expect": ["x"]}])
        for body in ('KIND = "check"\ndef run(snapshot, config):\n    return None\n',
                     'KIND = "check"\ndef run(snapshot, config):\n    raise KeyError("boom")\n',
                     'KIND = "check"\ndef run(:\n'):
            self.write("workspace.json", json.dumps({"parts": [{"use": "odd"}]}))
            self.write("parts/odd.py", body)
            self.write("parts/odd.cases.json", cases)
            self.assertEqual(self.ws("check")[0], 2, body)
        self.write("parts/odd.cases.json", '["x"]')
        self.assertEqual(self.ws("check")[0], 2)

    def test_a_hook_on_an_unknown_event_cannot_load_and_an_unknown_event_is_refused(self):
        self.workspace({"use": "no_stage_all"})
        self.assertEqual(self.ws("hook", "before-banana", stdin='{"version": 1, "command": "ls"}')[0], 2)
        source = (ROOT / "parts/no_stage_all.py").read_text(encoding="utf-8").replace('EVENT = "before-shell"', 'EVENT = "before-shel"')
        self.write("parts/no_stage_all.py", source)
        code, output = self.ws("hook", "before-shell", stdin='{"version": 1, "command": "ls"}')
        self.assertEqual(code, 2)
        self.assertIn("EVENT must be one of", output)

    def test_a_hook_that_cannot_decide_fails_closed(self):
        self.workspace({"use": "shelved", "paths": ["src/old"]})
        self.assertEqual(self.ws("hook", "before-edit", stdin='{"version": 1, "path": 5}')[0], 2)
        self.assertEqual(self.ws("hook", "before-edit", stdin='[]')[0], 2)

    def test_ci_fails_closed_when_it_cannot_compare(self):
        self.workspace({"use": "freshness"})
        self.write("old.md", STALE)
        self.git("init", "-q")
        self.git("add", ".")
        self.git("commit", "-q", "-m", "base")
        for ref in ("0" * 40, "deadbeef" * 5):
            code, output = self.ws("check", "--changed-from", ref)
            self.assertEqual(code, 1, ref)
            self.assertIn("every file is treated as changed", output)

    def test_the_staged_manifest_decides_not_the_one_on_disk(self):
        self.workspace({"use": "links"})
        self.git("init", "-q")
        self.write("a.md", "[gone](nope.md)\n")
        self.git("add", ".")
        self.write("workspace.json", json.dumps({"parts": [{"use": "freshness"}]}))   # unstaged: drops the links check
        self.write("parts/freshness.py", (ROOT / "parts/freshness.py").read_text(encoding="utf-8"))
        self.write("parts/freshness.cases.json", (ROOT / "parts/freshness.cases.json").read_text(encoding="utf-8"))
        code, output = self.ws("check", "--staged")
        self.assertEqual(code, 1)
        self.assertIn("link to missing file", output)

    def test_setup_mistakes_exit_2(self):
        self.assertEqual(self.ws("check")[0], 2)                       # no manifest
        self.workspace({"use": "links"})
        (self.root / "parts/links.cases.json").unlink()
        code, output = self.ws("check")
        self.assertEqual(code, 2)
        self.assertIn("refused, it has no cases file", output)
        self.assertEqual(self.ws("hook", "before-shell", stdin="not json")[0], 2)


class NoSelfLockTests(Folder):
    """M1 slice 2: a broken part cannot lock the session that repairs it, and the checks cannot be quietly switched off."""

    def break_cases(self, name):
        cases = json.loads((self.root / f"parts/{name}.cases.json").read_text(encoding="utf-8"))
        if "files" in cases[0]:
            cases[0]["expect"] = ["a finding no part ever returns"]
        else:
            answer = "allow" if "allow" in cases[0] else "remind"
            cases[0][answer] = not cases[0][answer]
        self.write(f"parts/{name}.cases.json", json.dumps(cases))

    def commit(self, message="base"):
        self.git("add", "--", *[p.relative_to(self.root).as_posix() for p in self.root.rglob("*")
                                if p.is_file() and ".git" not in p.parts])
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD").stdout.strip()

    # Criterion 1
    def test_changing_a_documented_setting_leaves_the_parts_own_cases_passing(self):
        settings = [("freshness", {"max_age_days": 1}), ("freshness", {"require": ["docs", "notes"]}),
                    ("freshness", {"skip": ["docs"]}), ("aliases", {"code": "lib"}), ("aliases", {"heading": "Words"}),
                    ("aliases", {"index": "docs/INDEX.md"}), ("aliases", {"exclude": ["src/api"]}),
                    ("links", {"skip": ["docs"]}), ("eval_record", {"playbooks": "docs"}),
                    ("eval_record", {"cases": "tests/cases"}), ("shelved", {"paths": []})]
        for name, setting in settings:
            with self.subTest(part=name, setting=setting):
                self.workspace({"use": name, **setting})
                code, output = self.ws("list")
                self.assertEqual(code, 0, output)

    # Criterion 2
    def test_a_broken_check_case_does_not_lock_the_hooks(self):
        self.workspace({"use": "links"}, {"use": "no_stage_all"}, {"use": "shelved", "paths": ["src/old"]})
        self.break_cases("links")
        code, output = self.ws("hook", "before-shell", stdin='{"version": 1, "command": "ls"}')
        self.assertEqual(code, 0, output)
        self.assertEqual(self.ws("hook", "before-edit", stdin='{"version": 1, "path": "parts/links.cases.json"}')[0], 0)
        self.assertEqual(self.ws("selftest")[0], 1)
        self.assertNotEqual(self.ws("check")[0], 0)

    def test_a_broken_hook_case_refuses_its_own_event_only(self):
        self.workspace({"use": "links"}, {"use": "no_stage_all"}, {"use": "shelved", "paths": ["src/old"]})
        self.break_cases("no_stage_all")
        code, output = self.ws("hook", "before-shell", stdin='{"version": 1, "command": "ls"}')
        self.assertEqual(code, 2)
        self.assertIn("no_stage_all", output)
        self.assertEqual(self.ws("hook", "before-edit", stdin='{"version": 1, "path": "parts/no_stage_all.cases.json"}')[0], 0)

    def test_a_check_that_will_not_even_import_does_not_lock_the_hooks(self):
        self.workspace({"use": "links"}, {"use": "no_stage_all"})
        self.write("parts/links.py", (ROOT / "parts/links.py").read_text(encoding="utf-8") + "\ndef broken(:\n")
        self.assertEqual(self.ws("hook", "before-shell", stdin='{"version": 1, "command": "ls"}')[0], 0)
        self.assertEqual(self.ws("check")[0], 2)

    def test_a_part_whose_kind_cannot_be_read_without_running_it_fails_closed(self):
        self.workspace({"use": "links"}, {"use": "no_stage_all"})
        source = (ROOT / "parts/no_stage_all.py").read_text(encoding="utf-8")
        for body in (source.replace('KIND = "hook"', 'KIND = "ho" + "ok"'),         # computed: unreadable
                     source.replace('KIND = "hook"', 'KIND = "check"\nKIND = "hook"'),  # declared twice
                     None):                                                         # file missing
            with self.subTest(body=body and body[:0]):
                if body is None:
                    (self.root / "parts/no_stage_all.py").unlink()
                else:
                    self.write("parts/no_stage_all.py", body)
                self.assertEqual(self.ws("hook", "before-shell", stdin='{"version": 1, "command": "git add -A"}')[0], 2)
                self.assertEqual(self.ws("hook", "before-shell", stdin='{"version": 1, "command": "ls"}')[0], 2)

    def test_a_declared_kind_that_differs_from_the_running_one_is_refused(self):
        self.workspace({"use": "no_stage_all"})
        source = (ROOT / "parts/no_stage_all.py").read_text(encoding="utf-8")
        self.write("parts/no_stage_all.py", source + '\nglobals()["KIND"] = "check"\n')
        code, output = self.ws("selftest")
        self.assertNotEqual(code, 0)
        self.assertIn("declares", output)

    # Criterion 3
    def test_a_half_written_manifest_refuses_every_hook_call_and_names_the_manifest(self):
        self.workspace({"use": "no_stage_all"}, {"use": "shelved", "paths": ["src/old"]})
        self.write("workspace.json", '{"parts": [{"use": "no_stage_all"}, {"use": "she')
        for event, payload in (("before-shell", '{"version": 1, "command": "ls"}'), ("before-edit", '{"version": 1, "path": "workspace.json"}')):
            code, output = self.ws("hook", event, stdin=payload)
            self.assertEqual(code, 2, event)
            self.assertIn("workspace.json", output)
            self.assertIn("your own terminal", output)

    # Criterion 4
    def test_a_part_outside_the_workspace_is_refused(self):
        outside = self.root.parent / f"{self.root.name}-outside"
        outside.mkdir()
        self.addCleanup(lambda: __import__("shutil").rmtree(outside))
        (outside / "sneaky.py").write_text('KIND = "check"\ndef run(snapshot, config):\n    return []\n', encoding="utf-8")
        (outside / "sneaky.cases.json").write_text('[{"name": "c", "files": {}, "expect": ["x"]}]', encoding="utf-8")
        for use in (f"../{outside.name}/sneaky.py", str(outside / "sneaky.py")):
            with self.subTest(use=use):
                self.write("workspace.json", json.dumps({"parts": [{"use": use}]}))
                code, output = self.ws("list")
                self.assertEqual(code, 2)
                self.assertIn("outside the workspace", output)
        try:
            (self.root / "parts").mkdir(exist_ok=True)
            (self.root / "parts/linked.py").symlink_to(outside / "sneaky.py")
        except OSError:
            self.skipTest("symlinks are not available here")
        self.write("workspace.json", json.dumps({"parts": [{"use": "linked"}]}))
        code, output = self.ws("list")
        self.assertEqual(code, 2)
        self.assertIn("outside the workspace", output)

    # Criterion 5
    def test_a_check_demoted_to_warnings_fails_its_own_cases(self):
        self.workspace({"use": "links"})
        source = (ROOT / "parts/links.py").read_text(encoding="utf-8").replace(
            "from wslib.parts import finding\n",
            "from wslib.parts import finding as _finding\n\n\ndef finding(path, line, message, level='error'):\n"
            "    return _finding(path, line, message, level='warning')\n")
        self.write("parts/links.py", source)
        code, output = self.ws("selftest")
        self.assertEqual(code, 1)
        self.assertIn("(error)", output)

    def test_a_case_states_the_level_it_expects(self):
        self.write("parts/warns.py", 'from wslib.parts import finding\nKIND = "check"\n'
                   'def run(snapshot, config):\n    return [finding("a.md", 1, "soft", level="warning")]\n')
        self.write("workspace.json", json.dumps({"parts": [{"use": "warns"}]}))
        self.write("parts/warns.cases.json", json.dumps([{"name": "w", "files": {}, "expect": [{"message": "soft", "level": "warning"}]}]))
        self.assertEqual(self.ws("selftest")[0], 0)
        self.write("parts/warns.cases.json", json.dumps([{"name": "w", "files": {}, "expect": ["soft"]}]))
        self.assertEqual(self.ws("selftest")[0], 1)
        self.write("parts/warns.cases.json", json.dumps([{"name": "w", "files": {}, "expect": [{"message": "soft", "level": "loud"}]}]))
        self.assertEqual(self.ws("selftest")[0], 2)

    def test_a_finding_with_an_unknown_level_is_an_error_not_a_quiet_pass(self):
        self.write("parts/odd.py", 'KIND = "check"\ndef run(snapshot, config):\n'
                   '    return [{"path": "a.md", "line": 1, "message": "x", "level": "Error"}]\n')
        self.write("parts/odd.cases.json", json.dumps([{"name": "c", "files": {}, "expect": ["x"]}]))
        self.write("workspace.json", json.dumps({"parts": [{"use": "odd"}]}))
        self.assertEqual(self.ws("check")[0], 2)

    def test_the_repository_cases_state_every_warning_they_expect(self):
        cases = json.loads((ROOT / "parts/freshness.cases.json").read_text(encoding="utf-8"))
        stale = next(c for c in cases if c["name"].startswith("a stale page nobody edited"))
        self.assertEqual([e["level"] for e in stale["expect"]], ["warning"])

    # Criterion 6
    def test_a_manifest_that_drops_a_part_fails_locally_unless_it_is_retired(self):
        self.workspace({"use": "links"}, {"use": "freshness"})
        self.git("init", "-q")
        self.commit()
        self.write("workspace.json", json.dumps({"parts": [{"use": "links"}]}))
        code, output = self.ws("check")
        self.assertEqual(code, 1)
        self.assertIn("freshness", output)
        self.git("add", "workspace.json")
        self.assertEqual(self.ws("check", "--staged")[0], 1)
        self.write("workspace.json", json.dumps({"parts": [{"use": "links"}],
                                                 "retired": [{"use": "freshness", "why": "no dated pages here"}]}))
        self.git("add", "workspace.json")
        self.assertEqual(self.ws("check")[0], 0)
        self.assertEqual(self.ws("check", "--staged")[0], 0)
        for retired in ([{"use": "freshness", "why": ""}], [{"use": "freshness"}], ["freshness"]):
            self.write("workspace.json", json.dumps({"parts": [{"use": "links"}], "retired": retired}))
            self.assertEqual(self.ws("check")[0], 2, retired)

    def test_ci_requires_the_parts_of_the_base_branch(self):
        self.workspace({"use": "links"}, {"use": "freshness"})
        self.git("init", "-q")
        base = self.commit()
        self.write("workspace.json", json.dumps({"parts": [{"use": "links"}]}))
        self.commit("drop freshness")
        code, output = self.ws("check", "--changed-from", base)
        self.assertEqual(code, 1)
        self.assertIn("freshness", output)

    def test_only_part_names_are_read_from_the_older_manifest(self):
        self.workspace({"use": "links"})
        self.write("workspace.json", json.dumps({"parts": [{"use": "links", "legacy": 1}, "junk", {"nouse": 1}], "zzz": 1}))
        self.git("init", "-q")
        base = self.commit()
        self.write("workspace.json", json.dumps({"tiers": {}, "parts": [{"use": "links", "newer": True}]}))
        self.commit("new keys")
        self.assertEqual(self.ws("check", "--changed-from", base)[0], 0)
        self.assertEqual(self.ws("check")[0], 0)

    def test_an_unstaged_edit_to_a_parts_cases_does_not_change_the_staged_check(self):
        self.workspace({"use": "links"})
        self.git("init", "-q")
        self.commit()
        self.write("a.md", "[gone](nope.md)\n")
        self.git("add", "a.md")
        before = self.ws("check", "--staged")
        self.break_cases("links")                                  # unstaged
        self.write("parts/links.py", "this is not python (\n")     # unstaged
        self.assertEqual(self.ws("check", "--staged"), before)
        self.assertEqual(before[0], 1)

    def test_a_commit_with_no_staged_manifest_is_refused(self):
        self.workspace({"use": "links"})
        self.git("init", "-q")
        self.commit()
        self.git("rm", "-q", "--cached", "workspace.json")
        code, output = self.ws("check", "--staged")
        self.assertEqual(code, 2)
        self.assertIn("workspace.json", output)


class FailClosedTests(Folder):
    """M1 slice 1: a hook refuses whatever it cannot read, and the wiring refuses when it cannot run the hook."""

    TIERS = {"driver": {"model": "opus", "effort": "high"}, "worker": {"model": "opus", "effort": "medium"},
             "mechanical": {"model": "haiku", "effort": "low"}}

    def hooks(self, *entries, tiers=None):
        self.workspace(*entries)
        manifest = json.loads((self.root / "workspace.json").read_text(encoding="utf-8"))
        if tiers is not None:
            manifest = {"tiers": tiers, **manifest}
        self.write("workspace.json", json.dumps(manifest))

    def answer(self, event, payload, tool=None):
        return self.ws("hook", event, *(["--tool", tool] if tool else []), stdin=payload)[0]

    # Criterion 7. Each value here is harmless, so a refusal can only come from the event's shape.
    UNREADABLE = [
        ("before-edit", "{}"),
        ("before-edit", '{"tool_input": {"filePath": "src/new/x.cs"}}'),
        ("before-edit", '{"file_path": "src/new/x.cs"}'),
        ("before-edit", '{"tool_input": {"path": "src/new/x.cs"}}'),
        ("before-edit", '{"toolArgs": "{\\"path\\": \\"src/new/x.cs\\"}"}'),
        ("before-shell", "{}"),
        ("before-shell", '{"tool_input": {"cmd": "ls"}}'),
        ("before-shell", '{"tool_input": {"command": ["ls"]}}'),
        ("before-shell", '{"command": "ls"}'),
        ("before-shell", '{"version": 1, "cmd": "ls"}'),
        ("before-shell", '{"version": 2, "command": "ls"}'),
        ("before-shell", '{"version": "1", "command": "ls"}'),
        ("before-shell", '{"version": true, "command": "ls"}'),
        ("before-shell", '{"version": 1, "command": ""}'),
        ("before-shell", '{"version": 1, "command": "ls", "path": "a.md"}'),
        ("before-shell", '{"version": 1, "command": ["ls"]}'),
        ("before-edit", '{"version": 1, "command": "ls"}'),
        ("before-edit", '{"version": 1, "path": null}'),
        ("before-edit", '{"version": 1, "path": "a\\u0000b"}'),
        ("before-handoff", '{"version": 1}'),
        ("before-shell", "[]"),
        ("before-shell", '"ls"'),
        ("before-shell", ""),
        ("before-shell", "[" * 100000),
    ]

    def test_an_event_in_no_known_shape_is_refused(self):
        self.hooks({"use": "no_stage_all"}, {"use": "shelved", "paths": ["src/old"]}, {"use": "handoff_tier"}, tiers=self.TIERS)
        for event, payload in self.UNREADABLE:
            for tool in (None, "claude-code"):
                with self.subTest(event=event, payload=payload[:60], tool=tool):
                    self.assertEqual(self.answer(event, payload, tool), 2)
        self.assertEqual(self.answer("before-shell", '{"version": 1, "command": "ls"}'), 0)
        self.assertEqual(self.answer("before-edit", '{"version": 1, "path": "src/new/x.cs"}'), 0)

    def test_a_tool_payload_missing_the_field_its_kind_needs_is_refused(self):
        self.hooks({"use": "no_stage_all"}, {"use": "shelved", "paths": ["src/old"]}, {"use": "handoff_tier"}, tiers=self.TIERS)
        here = str(self.root / "src/new/x.cs")
        refused = [
            ("before-edit", claude("Edit", filePath=here)),
            ("before-edit", claude("Write", path=here)),
            ("before-edit", claude("Edit", file_path="")),
            ("before-edit", claude("NotebookEdit", file_path=here)),
            ("before-edit", claude("Read", file_path=here)),            # a tool the adapter does not map to this event
            ("before-edit", claude("Bash", command="ls")),
            ("before-shell", claude("Bash", cmd="ls")),
            ("before-shell", claude("Bash", command=["ls"])),
            ("before-shell", claude("Bash")),
            ("before-shell", claude("Edit", file_path=here)),
            ("before-handoff", claude("Agent", description="x")),
            ("before-shell", json.dumps({"hook_event_name": "PostToolUse", "tool_name": "Bash", "tool_input": {"command": "ls"}})),
            ("before-shell", json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": '{"command": "ls"}'})),
            ("before-shell", json.dumps({"tool_name": "Bash", "tool_input": {"command": "ls"}})),
            ("before-edit", claude("Edit", file_path="src/new/x.cs")),   # relative, and no cwd to place it
            ("before-edit", claude("Edit", cwd="relative/dir", file_path="x.cs")),
        ]
        for event, payload in refused:
            with self.subTest(event=event, payload=payload):
                self.assertEqual(self.answer(event, payload, "claude-code"), 2)
                self.assertEqual(self.answer(event, payload), 2)        # read the same way with no --tool
        self.assertEqual(self.answer("before-shell", claude("Bash", command="ls", description="list"), "claude-code"), 0)
        self.assertEqual(self.answer("before-edit", claude("Edit", file_path=here, old_string="a", new_string="b"), "claude-code"), 0)
        self.assertEqual(self.answer("before-edit", claude("Write", cwd=self.root, file_path="src/new/x.cs"), "claude-code"), 0)
        self.assertEqual(self.answer("before-shell", claude("Bash", command="ls"), "an-unknown-tool"), 2)

    def test_wiring_written_before_the_adapters_keeps_working_and_stays_closed(self):
        # A running session keeps the wiring it started with, which named no --tool. The upgrade must not lock it out.
        self.hooks({"use": "no_stage_all"}, {"use": "shelved", "paths": ["src/old"]})
        self.assertEqual(self.answer("before-shell", claude("Bash", command="ls")), 0)
        self.assertEqual(self.answer("before-shell", claude("Bash", command="git add -A")), 0)   # a reminder
        self.assertEqual(self.answer("before-edit", claude("Edit", file_path=str(self.root / "src/old/x.cs"))), 2)
        self.assertEqual(self.answer("before-shell", claude("Bash", cmd="ls")), 2)
        # A named tool reads only its own payload.
        self.assertEqual(self.answer("before-shell", '{"version": 1, "command": "ls"}', "claude-code"), 2)

    def test_input_that_is_not_text_is_refused_without_a_traceback(self):
        self.hooks({"use": "no_stage_all"})
        for data in (b"\xff\xfe{", b'{"version": 1, "command": "ls"\xff}'):
            ran = subprocess.run([sys.executable, str(ROOT / "ws.py"), "--root", str(self.root), "hook", "before-shell"],
                                 input=data, capture_output=True)
            self.assertEqual(ran.returncode, 2, data)
            self.assertNotIn(b"Traceback", ran.stderr)

    # Criterion 8
    def test_an_upper_cased_absolute_path_on_a_case_insensitive_file_system_is_refused(self):
        self.hooks({"use": "shelved", "paths": ["src/old"]})
        (self.root / "src/old").mkdir(parents=True)
        upper = str(self.root).upper()
        if upper == str(self.root) or not os.path.exists(upper) or not os.path.samefile(upper, self.root):
            self.skipTest("this file system tells upper and lower case apart")
        for tool, field in (("Edit", "file_path"), ("Write", "file_path"), ("NotebookEdit", "notebook_path")):
            with self.subTest(tool=tool):
                payload = claude(tool, **{field: os.path.join(upper, "SRC", "OLD", "X.CS")})
                self.assertEqual(self.answer("before-edit", payload, "claude-code"), 2)
        self.assertEqual(self.answer("before-edit", claude("Edit", file_path=os.path.join(upper, "SRC", "NEW", "X.CS")),
                                     "claude-code"), 0)

    def test_an_edit_through_a_symbolic_link_into_the_shelved_folder_is_refused(self):
        self.hooks({"use": "shelved", "paths": ["src/old"]})
        (self.root / "src/old").mkdir(parents=True)
        (self.root / "src/new").mkdir(parents=True)
        try:
            (self.root / "legacy").symlink_to(self.root / "src/old", target_is_directory=True)
            (self.root / "current").symlink_to(self.root / "src/new", target_is_directory=True)
        except OSError:
            self.skipTest("symlinks are not available here")
        self.assertEqual(self.answer("before-edit", '{"version": 1, "path": "legacy/x.cs"}'), 2)
        self.assertEqual(self.answer("before-edit", claude("Edit", file_path=str(self.root / "legacy/x.cs")), "claude-code"), 2)
        self.assertEqual(self.answer("before-edit", claude("Write", cwd=self.root / "legacy", file_path="x.cs"), "claude-code"), 2)
        self.assertEqual(self.answer("before-edit", '{"version": 1, "path": "current/x.cs"}'), 0)
        self.assertEqual(self.answer("before-edit", claude("Edit", file_path=str(self.root / "current/x.cs")), "claude-code"), 0)

    def test_the_notebook_edit_tool_is_wired_and_refused(self):
        self.hooks({"use": "shelved", "paths": ["src/old"]})
        payload = claude("NotebookEdit", notebook_path=str(self.root / "src/old/n.ipynb"), new_source="x")
        self.assertEqual(self.answer("before-edit", payload, "claude-code"), 2)
        payload = claude("NotebookEdit", notebook_path=str(self.root / "src/new/n.ipynb"), new_source="x")
        self.assertEqual(self.answer("before-edit", payload, "claude-code"), 0)

    def test_the_wiring_sends_every_tool_the_adapter_reads_and_every_event_has_wiring(self):
        from wslib import events
        wiring = self.wiring()
        self.assertEqual(set(wiring), set(partlib.EVENTS))
        for event, tools in events.CLAUDE_CODE_TOOLS.items():
            matcher, command = wiring[event]
            for tool in tools:
                with self.subTest(event=event, tool=tool):
                    self.assertTrue(re.fullmatch(matcher, tool), f"{matcher!r} does not send {tool} to {event}")
            self.assertIn("--tool claude-code", command)
            self.assertTrue(command.rstrip().endswith("|| exit 2"), command)

    # Criterion 9
    def test_a_path_inside_a_code_repository_under_src_is_decided_like_any_other(self):
        self.hooks({"use": "shelved", "paths": ["src/product/Legacy"]})
        product = self.root / "src/product"
        self.write("src/product/Legacy/Old.cs", "class Old { }\n")
        self.write("src/product/Billing/Run.cs", "class Run { }\n")
        for args in (["init", "-q"], ["add", "Legacy/Old.cs", "Billing/Run.cs"],
                     ["-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "commit.gpgsign=false", "commit", "-q", "-m", "p"]):
            subprocess.run(["git", "-C", str(product), *args], check=True, capture_output=True)
        answers = [
            ('{"version": 1, "path": "src/product/Legacy/Old.cs"}', None, 2),
            ('{"version": 1, "path": "src/product/Billing/Run.cs"}', None, 0),
            (claude("Edit", file_path=str(product / "Legacy/Old.cs")), "claude-code", 2),
            (claude("Edit", file_path=str(product / "Billing/Run.cs")), "claude-code", 0),
            (claude("Write", cwd=product, file_path="Legacy/New.cs"), "claude-code", 2),
            (claude("Write", cwd=product, file_path="Billing/New.cs"), "claude-code", 0),
            (claude("Write", cwd=product / "Billing", file_path="../Legacy/New.cs"), "claude-code", 2),
        ]
        for payload, tool, want in answers:
            with self.subTest(payload=payload):
                self.assertEqual(self.answer("before-edit", payload, tool), want)

    # Criterion 10
    def wiring(self):
        """{event: (matcher, command)} from the agent tool's settings."""
        settings = json.loads((ROOT / ".claude/settings.json").read_text(encoding="utf-8"))
        found = {}
        for entry in settings["hooks"]["PreToolUse"]:
            for hook in entry["hooks"]:
                event = re.search(r"\bhook (before-[a-z]+)\b", hook["command"]).group(1)
                found[event] = (entry["matcher"], hook["command"])
        return found

    def shell(self):
        if os.name == "nt":   # Git's own bash: the one an agent tool on Windows runs hooks with, not WSL's
            git = shutil.which("git")
            candidate = git and pathlib.Path(git).resolve().parent.parent / "bin" / "bash.exe"
            return str(candidate) if candidate and candidate.exists() else None
        return shutil.which("sh")

    def run_wiring(self, event, payload, project, path=None):
        shell = self.shell()
        if not shell:
            self.skipTest("no POSIX shell here")
        environment = dict(os.environ, CLAUDE_PROJECT_DIR=pathlib.Path(project).as_posix())
        if path is not None:
            environment["PATH"] = path
        return subprocess.run([shell, "-c", self.wiring()[event][1]], input=payload.encode("utf-8"),
                              capture_output=True, env=environment)

    def test_the_wiring_refuses_when_python_is_missing(self):
        empty = self.root / "empty-bin"
        empty.mkdir()
        # The edit is outside every working copy, so the test records nothing in this repository's edit ledger.
        for event, payload in (("before-shell", claude("Bash", command="ls")),
                               ("before-edit", claude("Edit", file_path=str(self.root / "notes.md")))):
            with self.subTest(event=event):
                ran = self.run_wiring(event, payload, ROOT)
                self.assertEqual(ran.returncode, 0, ran.stderr)                    # with Python: allowed
                ran = self.run_wiring(event, payload, ROOT, path=str(empty))
                self.assertEqual(ran.returncode, 2, ran.stderr)                    # without: refused, not 0 or 1
                self.assertIn(b"Python", ran.stderr)
        ran = self.run_wiring("before-edit", claude("Edit", file_path=str(ROOT / "src/orders-service-v1/OrderService.cs")), ROOT)
        self.assertEqual(ran.returncode, 2, ran.stderr)
        ran = self.run_wiring("before-shell", claude("Bash", command="ls"), self.root)   # no launcher there at all
        self.assertEqual(ran.returncode, 2, ran.stderr)

    # Criterion 11
    def handoff(self, tool="Agent", **tool_input):
        return self.answer("before-handoff", claude(tool, description="d", subagent_type="Explore", **tool_input), "claude-code")

    def test_a_delegated_task_must_name_its_tier_and_run_at_its_binding(self):
        self.hooks({"use": "handoff_tier"}, tiers=self.TIERS)
        named = "Tier: mechanical\nList every caller of decide()."
        self.assertEqual(self.handoff(prompt="List every caller of decide().", model="haiku", effort="low"), 2)
        self.assertEqual(self.handoff(prompt="Look up the tier in docs/orchestration.md\nTier: mechanical", model="haiku", effort="low"), 2)
        self.assertEqual(self.handoff(prompt="Tier: boss\nList.", model="haiku", effort="low"), 2)
        self.assertEqual(self.handoff(prompt=named, model="haiku", effort="low"), 0)
        self.assertEqual(self.handoff("Task", prompt=named, model="haiku", effort="low"), 0)
        self.assertEqual(self.handoff(prompt="\n  tier: Worker - build slice 1\n", model="opus", effort="medium"), 0)
        self.assertEqual(self.handoff(prompt=named, model="opus", effort="low"), 2)       # model off the binding
        self.assertEqual(self.handoff(prompt=named, model="haiku", effort="high"), 2)     # effort off the binding
        self.assertEqual(self.handoff(prompt=named, effort="low"), 2)                     # unset: it would inherit
        self.assertEqual(self.handoff(prompt=named, model="haiku"), 2)
        code, output = self.ws("hook", "before-handoff", "--tool", "claude-code", stdin=claude("Agent", prompt="List."))
        self.assertEqual(code, 2)
        self.assertIn("names no tier", output)

    def test_a_tool_that_exposes_no_model_or_effort_needs_only_the_tier(self):
        self.hooks({"use": "handoff_tier"}, tiers=self.TIERS)
        self.assertEqual(self.answer("before-handoff", '{"version": 1, "prompt": "Tier: worker\\nBuild it."}'), 0)
        self.assertEqual(self.answer("before-handoff", '{"version": 1, "prompt": "Build it."}'), 2)
        self.assertEqual(self.answer("before-handoff", '{"version": 1, "prompt": "Tier: worker", "model": "haiku"}'), 2)
        self.assertEqual(self.answer("before-handoff", '{"version": 1, "prompt": "Tier: worker", "effort": "medium"}'), 0)

    def test_the_binding_comes_from_the_manifest_only(self):
        self.hooks({"use": "handoff_tier"})                                          # no binding at all
        self.assertEqual(self.answer("before-handoff", '{"version": 1, "prompt": "Tier: worker"}'), 2)
        self.hooks({"use": "handoff_tier", "tiers": self.TIERS}, tiers=self.TIERS)   # a part may not carry its own
        code, output = self.ws("hook", "before-handoff", stdin='{"version": 1, "prompt": "Tier: worker"}')
        self.assertEqual(code, 2)
        self.assertIn("top-level", output)


class StagingAtTheCommitTests(Folder):
    """M1 slice 5: the commit compares what is staged with what the session's edit tools wrote; the shell hook reminds."""

    def setUp(self):
        super().setUp()
        self.workspace({"use": "edit_ledger"}, {"use": "no_stage_all"}, {"use": "shelved", "paths": ["src/old"]})
        for name in ("ws.py", ".gitignore", ".githooks/pre-commit", ".githooks/commit-msg", ".githooks/post-commit"):
            self.write(name, (ROOT / name).read_text(encoding="utf-8"))
            (self.root / name).chmod(0o755)
        for source in (ROOT / "wslib").glob("*.*"):
            self.write(f"wslib/{source.name}", source.read_text(encoding="utf-8"))
        self.write("a.md", "mine\n")
        self.write("theirs.md", "theirs\n")
        self.git("init", "-q")
        self.git("config", "core.hooksPath", ".githooks")
        self.commit_all()
        home = self.root.parent / f"{self.root.name}-home"   # no real deny list, and no real git config, in the hooks
        environment = mock.patch.dict(os.environ, {"HOME": str(home), "USERPROFILE": str(home), "WS_DENY_LIST": ""})
        environment.start()
        self.addCleanup(environment.stop)

    def commit_all(self):
        self.git("add", "--", *[p.relative_to(self.root).as_posix() for p in self.root.rglob("*")
                                if p.is_file() and ".git" not in p.parts])
        self.git("commit", "-q", "--no-verify", "-m", "base")

    def run_git(self, *args, cwd=None):
        """git with the fixture's own hooks, which run this branch's ws.py on the fixture."""
        return subprocess.run(["git", "-C", str(cwd or self.root), "-c", "user.name=t", "-c", "user.email=t@example.invalid",
                               "-c", "commit.gpgsign=false", *args], capture_output=True, text=True)

    def edit(self, path, cwd=None):
        """An agent's edit tool writes path: the hook is asked first, as the agent tool asks it."""
        payload = claude("Edit", cwd=cwd, file_path=str(path), old_string="a", new_string="b")
        code, output = self.ws("hook", "before-edit", "--tool", "claude-code", stdin=payload)
        self.assertEqual(code, 0, output)
        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(path).write_text("edited by the agent\n", encoding="utf-8")

    def ledger(self, folder=None):
        file = (folder or self.root / ".git") / "ws-ledger"
        return file.read_text(encoding="utf-8").split() if file.exists() else None

    # Criterion 12
    def test_each_edit_is_recorded_in_the_ledger_of_the_working_copy_that_holds_it(self):
        self.assertIsNone(self.ledger())
        self.edit(self.root / "a.md")
        self.assertEqual(self.ledger(), ['"a.md"'])
        self.edit(self.root / "a.md")                                              # once only
        self.assertEqual(self.ledger(), ['"a.md"'])
        linked = self.root.parent / f"{self.root.name}-linked"
        self.addCleanup(shutil.rmtree, linked, True)
        self.git("worktree", "add", "-q", "-b", "other", str(linked))
        self.edit(linked / "theirs.md")                                            # a linked working copy keeps its own
        self.assertEqual(self.ledger(), ['"a.md"'])
        self.assertEqual(self.ledger(self.root / ".git/worktrees" / linked.name), ['"theirs.md"'])
        outside = self.root.parent / f"{self.root.name}-scratch"
        outside.mkdir()
        self.addCleanup(shutil.rmtree, outside, True)
        self.edit(outside / "notes.md")                                            # no working copy of this repository
        self.assertEqual(self.ledger(), ['"a.md"'])
        code, output = self.ws("hook", "before-edit", stdin='{"version": 1, "path": "src/old/x.cs"}')
        self.assertEqual(code, 2)                                                  # a refused edit is not recorded
        self.assertEqual(self.ledger(), ['"a.md"'])

    def test_with_a_ledger_open_a_commit_of_a_path_no_edit_tool_wrote_fails_whatever_staged_it(self):
        self.edit(self.root / "a.md")
        self.write("theirs.md", "another session's unsaved edit\n")
        self.write("new.md", "another session's new file\n")
        sweeps = [["add", "-A"], ["add", "."], ["add", "-u"], ["stage", "--all"], ["add", "theirs.md"],
                  ["add", "--", "a.md", "new.md"], ["rm", "-q", "--cached", "theirs.md"]]
        for sweep in sweeps:
            with self.subTest(sweep=sweep):
                self.assertEqual(self.run_git(*sweep).returncode, 0)
                ran = self.run_git("commit", "-m", "fix")
                self.assertNotEqual(ran.returncode, 0, ran.stdout)
                self.assertIn("staged, but no edit tool", ran.stdout + ran.stderr)
                self.git("reset", "-q")
        for commit in (["commit", "-a", "-m", "fix"], ["commit", "-m", "fix", "--", "theirs.md"]):
            with self.subTest(commit=commit):
                ran = self.run_git(*commit)
                self.assertNotEqual(ran.returncode, 0, ran.stdout)
                self.assertIn("theirs.md:1: staged, but no edit tool", ran.stdout + ran.stderr)
        self.assertEqual(self.run_git("rev-list", "--count", "HEAD").stdout.strip(), "1")   # nothing got through
        self.git("add", "a.md")
        ran = self.run_git("commit", "-m", "fix")
        self.assertEqual(ran.returncode, 0, ran.stdout + ran.stderr)
        self.assertIsNone(self.ledger())                       # the commit took every recorded path, so it closed

    def test_with_no_ledger_a_persons_own_commit_is_not_compared(self):
        self.write("theirs.md", "the person's own edit\n")
        self.git("add", "theirs.md")
        ran = self.run_git("commit", "-m", "mine")
        self.assertEqual(ran.returncode, 0, ran.stdout + ran.stderr)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("With no ledger open, as for a person's own commit", readme, "the README must say so")

    def test_a_partial_commit_keeps_the_ledger_open_for_the_rest(self):
        self.edit(self.root / "a.md")
        self.edit(self.root / "src/new.cs")
        self.git("add", "a.md")
        self.assertEqual(self.run_git("commit", "-m", "first").returncode, 0)
        self.assertEqual(self.ledger(), ['"src/new.cs"'])
        self.write("theirs.md", "another session's edit\n")
        self.assertEqual(self.run_git("commit", "-a", "-m", "sweep").returncode, 1)
        code, output = self.ws("ledger", "--close")
        self.assertEqual(code, 0)
        self.assertIn("closed", output)
        self.assertEqual(self.run_git("commit", "-a", "-m", "the person's own").returncode, 0)

    def test_a_session_that_writes_only_through_the_shell_is_still_compared(self):
        self.write("a.md", "written by a shell command\n")
        self.write("theirs.md", "another session's edit\n")
        code, output = self.ws("hook", "before-shell", "--tool", "claude-code",
                               stdin=claude("Bash", cwd=self.root, command="git add -A && git commit -m fix"))
        self.assertEqual(code, 0)
        self.assertIn("The edit ledger of this working copy is open", json.loads(output)["hookSpecificOutput"]["additionalContext"])
        self.assertEqual(self.ledger(), [])
        self.git("reset", "-q")
        os.remove(self.root / ".git" / "ws-ledger")
        code, output = self.ws("hook", "before-shell", stdin='{"version": 1, "command": "git add -A"}')
        self.assertIn("Reminder: no_stage_all", output)
        self.assertIsNone(self.ledger())          # a person trying the hook by hand names no folder, so opens nothing
        self.ws("hook", "before-shell", "--tool", "claude-code", stdin=claude("Bash", cwd=self.root, command="git add ."))
        self.git("add", "-A")
        self.assertEqual(self.run_git("commit", "-m", "fix").returncode, 1)
        self.git("reset", "-q")
        with contextlib.chdir(self.root) if hasattr(contextlib, "chdir") else _chdir(self.root):
            self.assertEqual(self.ws("ledger", "--add", "a.md")[0], 0)
        self.git("add", "a.md")
        ran = self.run_git("commit", "-m", "fix")
        self.assertEqual(ran.returncode, 0, ran.stdout + ran.stderr)

    def test_a_reminder_opens_the_ledger_only_when_the_working_copy_has_uncommitted_changes(self):
        # The agent tool reports the folder the session started in, not where the command moves to. With nothing
        # uncommitted there, a stage-everything command elsewhere has nothing of anyone's to sweep, so nothing opens.
        command = "cd /tmp/scratch && git add ."
        code, output = self.ws("hook", "before-shell", "--tool", "claude-code", stdin=claude("Bash", cwd=self.root, command=command))
        self.assertEqual(code, 0)
        self.assertIn("stages more than it names", output)
        self.assertNotIn("ledger of this working copy is open", output, self.run_git("status", "--porcelain").stdout)
        self.assertIsNone(self.ledger())
        self.write("new.md", "someone's new file\n")                 # untracked counts: git add -A would take it
        code, output = self.ws("hook", "before-shell", "--tool", "claude-code", stdin=claude("Bash", cwd=self.root, command=command))
        self.assertIn("ledger of this working copy is open", output)
        self.assertEqual(self.ledger(), [])

    def test_a_pin_counts_as_edited_when_the_session_edited_inside_it(self):
        product = self.root / "src/product"
        product.mkdir(parents=True)
        for args in (["init", "-q"], ["commit", "-q", "--allow-empty", "-m", "p"]):
            subprocess.run(["git", "-C", str(product), "-c", "user.name=t", "-c", "user.email=t@example.invalid",
                            "-c", "commit.gpgsign=false", *args], check=True, capture_output=True)
        self.edit(product / "Run.cs")
        self.assertEqual(self.ledger(), ['"src/product/Run.cs"'])               # the workspace's ledger, not the code's
        self.assertIsNone(self.ledger(product / ".git"))
        self.git("add", "src/product")
        ran = self.run_git("commit", "-m", "move the pin")
        self.assertEqual(ran.returncode, 0, ran.stdout + ran.stderr)

    # Criterion 13
    def test_staging_commands_that_name_their_files_or_another_repository_are_allowed(self):
        quiet = ['git commit -m"add export handler"', "git add -u docs/parts.md"]
        for command in quiet:
            with self.subTest(command=command):
                code, output = self.ws("hook", "before-shell", "--tool", "claude-code",
                                       stdin=claude("Bash", cwd=self.root, command=command))
                self.assertEqual((code, output), (0, ""))
        fixture = self.root.parent / f"{self.root.name}-fixture"
        fixture.mkdir()
        self.addCleanup(shutil.rmtree, fixture, True)
        (fixture / "x.txt").write_text("x\n", encoding="utf-8")
        command = "git init -q && git add . && git commit -q -m fixture"
        code, output = self.ws("hook", "before-shell", "--tool", "claude-code", stdin=claude("Bash", cwd=fixture, command=command))
        self.assertEqual(code, 0, output)                      # allowed: a reminder at most
        self.assertIsNone(self.ledger())                       # and the workspace's ledger stays closed
        ran = subprocess.run(command, shell=True, cwd=fixture, capture_output=True, text=True,
                             env=dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
                                      GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid"))
        self.assertEqual(ran.returncode, 0, ran.stderr)

    # Criterion 14
    def test_a_commit_message_or_identity_on_the_deny_list_is_refused(self):
        self.workspace({"use": "edit_ledger"}, {"use": "deny_list"})
        self.git("add", "workspace.json", "parts")
        self.git("commit", "-q", "--no-verify", "-m", "add the deny list")
        listed = self.root.parent / f"{self.root.name}-deny.txt"
        listed.write_text("globex corp\n", encoding="utf-8")
        self.addCleanup(listed.unlink)
        os.environ["WS_DENY_LIST"] = str(listed)
        attempts = [
            (["commit", "--allow-empty", "-m", "Ship the export to Globex Corp"], "commit message:1:"),
            (["commit", "--allow-empty", "-m", "fix", "--author", "A <a@globex-corp.example>"], "author:1:"),
            (["-c", "user.email=c@globexcorp.example", "commit", "--allow-empty", "-m", "fix"], "committer:1:"),
        ]
        for args, where in attempts:
            with self.subTest(where=where):
                ran = self.run_git(*args)
                self.assertNotEqual(ran.returncode, 0, ran.stdout)
                self.assertIn(f"{where} matches line 1 of the private deny list", ran.stdout + ran.stderr)
                self.assertNotIn("globex", (ran.stdout + ran.stderr).lower())
        ran = self.run_git("commit", "--allow-empty", "-m", "fix the export")
        self.assertEqual(ran.returncode, 0, ran.stdout + ran.stderr)
        self.assertEqual(self.run_git("rev-list", "--count", "HEAD").stdout.strip(), "3")

    def test_the_message_check_cannot_be_switched_off_from_the_manifest(self):
        self.workspace({"use": "deny_list", "terms": []})
        message = self.root / "MSG"
        message.write_text("x\n", encoding="utf-8")
        self.git("add", "workspace.json", "parts")
        identity = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",   # as git sets them for its hooks;
                    "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}   # CI has no identity
        with mock.patch.dict(os.environ, identity):
            code, output = self.ws("check", "--message", str(message))
        self.assertEqual(code, 1)
        self.assertIn("only its cases may", output)


@contextlib.contextmanager
def _chdir(folder):
    before = os.getcwd()
    os.chdir(folder)
    try:
        yield
    finally:
        os.chdir(before)


class SymbolTests(unittest.TestCase):
    def names(self, path, text):
        return [(line, kind, name) for line, kind, name in symbols.symbols_in(path, text)]

    def test_csharp(self):
        text = "\n".join([
            "namespace Shop;",                                               # 1
            "public sealed class OrdersController : ControllerBase",         # 2
            "{",
            "    public OrdersController(IStore store) { }",                 # 4
            "    public async Task<IActionResult> ExportOrders(int id)",     # 5
            "    {",
            "        var rows = await store.Load(id);",
            "        if (rows.Count == 0) return NotFound();",
            "        return Ok(Map(rows));",
            "    }",
            "    public string Name { get; set; }",                          # 11
            "    public T Convert<T>(object value) => (T)value;",            # 12
            "    public (int, string) Split(string s) => (1, s);",           # 13
            "    public static implicit operator int(OrdersController c) => 0;",
            "    string Describe(int id)",                                   # 15
            "    {",
            "        throw new NotImplementedException();",
            "    }",
            "}",
            "public readonly record struct Point(int X, int Y);",            # 20
            "file class Hidden { }",                                         # 21
            "public ref struct Buffer { }",                                  # 22
            "/* public class Ghost { } */",
            "// public class Phantom { }",
            "public interface IStore",                                       # 25
            "{",
            "    Task<IList<Row>> Load(int id);",                            # 27
            "}",
        ])
        self.assertEqual(self.names("a.cs", text), [
            (2, "type", "OrdersController"), (4, "constructor", "OrdersController"), (5, "method", "ExportOrders"),
            (11, "property", "Name"), (12, "method", "Convert"), (13, "method", "Split"), (15, "method", "Describe"),
            (20, "type", "Point"), (21, "type", "Hidden"), (22, "type", "Buffer"), (25, "type", "IStore"),
            (27, "method", "Load"),
        ])

    def test_typescript(self):
        text = "\n".join([
            "export interface OrderRow { id: number }",                      # 1
            "export const exportOrders = async () => {};",                   # 2
            "export function renderOrders() {}",                             # 3
            "export const limit: number = 10;",                              # 4
            "declare function legacy(): void;",                              # 5
            "export const enum Status { Open }",                             # 6
            "namespace Billing {}",                                          # 7
            "export default class extends Base {}",
            "class OrderTable {",                                            # 9
            "  private rows: OrderRow[] = [];",
            "  async load(id: string): Promise<void> {",                     # 11
            "    if (this.rows.length) {",
            "      return;",
            "    }",
            "    items.forEach((item) => {",
            "      render(item);",
            "    });",
            "  }",
            "  static create<T>(seed: T) {",                                 # 19
            "  }",
            "}",
            "// function ghost() {}",
        ])
        self.assertEqual(self.names("a.ts", text), [
            (1, "type", "OrderRow"), (2, "const", "exportOrders"), (3, "function", "renderOrders"),
            (4, "const", "limit"), (5, "function", "legacy"), (6, "type", "Status"), (7, "type", "Billing"),
            (9, "class", "OrderTable"), (11, "method", "load"), (19, "method", "create"),
        ])

    def test_python_including_syntax_newer_than_the_interpreter(self):
        text = "class OrderExporter:\n    def run(self):\n        pass\n\nasync def export_all():\n    pass\n"
        self.assertEqual(self.names("a.py", text),
                         [(1, "class", "OrderExporter"), (5, "function", "export_all"), (2, "function", "run")])
        broken = "def before():\n    pass\n\nthis is not python (\n\nclass After:\n    pass\n"
        self.assertEqual(self.names("b.py", broken), [(1, "function", "before"), (6, "class", "After")])

    def test_vendored_folders_are_skipped_below_the_root_but_a_root_named_build_is_not(self):
        files = {"build/proj/app.py": "def f():\n    pass\n", "build/proj/node_modules/lib/x.js": "function g() {}\n"}
        memory = snapshots.Memory(files)
        self.assertEqual([s[3] for s in symbols.scan(memory, "build/proj")], ["f"])

    def test_the_command_line(self):
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(symbols_cli.main(["ReconciliationWorker", str(ROOT / "src")]), 0)
            self.assertEqual(symbols_cli.main(["NoSuchName", str(ROOT / "src")]), 1)
            self.assertEqual(symbols_cli.main(["x", str(ROOT / "no-such-folder")]), 2)
        self.assertIn("orders-api/ReconciliationWorker.cs:4  type  ReconciliationWorker", out.getvalue())


class GradeTests(unittest.TestCase):
    CASE = json.loads((ROOT / "evals/cases/fix-a-bug.json").read_text(encoding="utf-8"))
    FIRST = "sees-a-test-fail-before-editing"
    GOOD = [
        {"kind": "edit", "target": "tests/test_page.py", "ok": True},
        {"kind": "run", "target": "python3 -m unittest 2>&1 | tail -5", "ok": True, "output": "Ran 4 tests in 0.001s\n\nFAILED (failures=1)"},
        {"kind": "edit", "target": "shop/page.py", "ok": True},
        {"kind": "run", "target": "python3 -m unittest", "ok": True},
        {"kind": "run", "target": "git add shop/page.py tests/test_page.py && git commit -m 'Wire the Export button'", "ok": True},
        {"kind": "report", "target": "Fixed: Export had no handler.\n\nverified  the new test fails before the fix\ninferred  nothing else attaches handlers", "ok": True},
        {"kind": "state", "target": "suite passes after the change", "ok": True},
        {"kind": "state", "target": "tests fail on the original code", "ok": True},
        {"kind": "state", "target": "other edits stayed out of the commit", "ok": True},
    ]

    def results(self, actions):
        return dict(grade.grade(self.CASE, actions))

    def swap(self, index, **changes):
        actions = [dict(a) for a in self.GOOD]
        actions[index].update(changes)
        return actions

    def test_a_run_that_follows_the_playbook_passes_every_grader(self):
        self.assertTrue(all(self.results(self.GOOD).values()))

    def test_a_report_in_the_prescribed_multi_line_shape_passes(self):
        self.assertTrue(self.results(self.GOOD)["report-marks-a-claim-verified"])

    def test_saying_the_word_verified_in_a_sentence_is_not_marking_a_claim(self):
        gamed = self.swap(5, target="Nothing was verified; everything is inferred.")
        self.assertFalse(self.results(gamed)["report-marks-a-claim-verified"])

    def test_a_test_run_that_passed_is_not_a_reproduction(self):
        self.assertFalse(self.results(self.swap(1, output="Ran 4 tests in 0.001s\n\nOK"))[self.FIRST])
        self.assertFalse(self.results(self.swap(1, target="echo test", output="test"))[self.FIRST])
        no_tests = self.swap(1, target="python3 -m unittest no_such_module", output="Ran 1 test in 0.000s\n\nFAILED (errors=1)")
        self.assertFalse(self.results(no_tests)[self.FIRST])

    def test_a_failing_run_counts_even_when_a_pipe_hides_its_exit_code(self):
        self.assertTrue(self.GOOD[1]["ok"])
        self.assertTrue(self.results(self.GOOD)[self.FIRST])
        pytest = self.swap(1, target="pytest -q", output="=== 1 failed, 3 passed in 0.02s ===")
        self.assertTrue(self.results(pytest)[self.FIRST])

    def test_editing_the_code_first_fails(self):
        actions = [self.GOOD[2], self.GOOD[0], self.GOOD[1]] + self.GOOD[3:]
        self.assertFalse(self.results(actions)[self.FIRST])

    def test_staging_everything_fails_in_every_spelling_and_by_name_passes(self):
        for command in ("git add  -A", "git add -u", "git add *", "git commit -am fix", "npm test && git add .", "echo x\ngit add -A"):
            self.assertFalse(self.results(self.swap(4, target=command))["stages-by-name"], command)
        for command in ("git add ./shop/page.py", "git add .github/x.yml", "echo git add -A"):
            self.assertTrue(self.results(self.swap(4, target=command))["stages-by-name"], command)

    def test_state_lines_decide_not_the_agents_word(self):
        self.assertFalse(self.results(self.swap(7, ok=False))["new-test-fails-on-the-original-code"])
        self.assertFalse(self.results(self.swap(8, ok=False))["leaves-the-other-session's-edits-out"])

    def test_malformed_cases_and_transcripts_are_refused(self):
        for case in ({"graders": []}, {"graders": [{"id": "x", "type": "any", "knd": "run"}]},
                     {"graders": [{"id": "x", "type": "sometimes"}]},
                     {"graders": [{"id": "x", "type": "before", "first": {"mach": "a"}, "then": {}}]}):
            with self.assertRaises(grade.Malformed):
                grade.grade(case, [])
        with self.assertRaises(grade.Malformed):
            grade.grade(self.CASE, {"kind": "run"})
        with self.assertRaises(grade.Malformed):
            grade.grade(self.CASE, [{"kind": "ran", "target": "x"}])


class DenyListTests(Folder):
    """The deny list is read from a file the environment names, so these cases cannot be data in a cases file."""

    def setUp(self):
        super().setUp()
        self.workspace({"use": "deny_list"})
        self.list_file = self.root.parent / f"{self.root.name}-deny.txt"
        self.list_file.write_text("# private\nglobex corp\nre:\\bGLX-\\d+\\b\n", encoding="utf-8")
        self.addCleanup(self.list_file.unlink)
        home = self.root.parent / f"{self.root.name}-home"   # so the default list path is never the real one
        environment = mock.patch.dict(os.environ, {"WS_DENY_LIST": str(self.list_file), "HOME": str(home), "USERPROFILE": str(home)})
        environment.start()
        self.addCleanup(environment.stop)

    def test_a_listed_term_fails_and_the_output_never_shows_the_term(self):
        self.write("docs/a.md", "Ships to GLOBEX Corp, see GLX-42.\n")
        code, out = self.ws("check")
        self.assertEqual(code, 1)
        self.assertIn("docs/a.md:1: matches line 2 of the private deny list", out)
        self.assertIn("docs/a.md:1: matches line 3 of the private deny list", out)
        self.assertNotIn("globex", out.lower())

    def test_files_in_other_encodings_are_still_checked(self):
        (self.root / "utf16.txt").write_bytes("globex corp\n".encode("utf-16"))
        (self.root / "latin1.cs").write_bytes("// \xa9 Globex Corp\n".encode("latin-1"))
        code, out = self.ws("check")
        self.assertEqual(code, 1)
        self.assertIn("utf16.txt:1:", out)
        self.assertIn("latin1.cs:1:", out)

    def test_the_commit_check_reads_what_is_staged(self):
        self.git("init", "-q")
        self.write("a.md", "fine\n")
        self.git("add", "a.md", "workspace.json", "parts")
        self.assertEqual(self.ws("check", "--staged")[0], 0)
        self.write("a.md", "globex corp\n")
        self.assertEqual(self.ws("check", "--staged")[0], 0)   # the bad edit is not staged
        self.git("add", "a.md")
        self.assertEqual(self.ws("check", "--staged")[0], 1)

    def test_a_list_committed_by_mistake_fails_on_its_own_contents(self):
        self.write("deny.txt", self.list_file.read_text(encoding="utf-8"))
        code, out = self.ws("check")
        self.assertEqual(code, 1)
        self.assertIn("deny.txt:", out)

    def test_a_list_that_cannot_be_read_fails_closed(self):
        os.environ["WS_DENY_LIST"] = str(self.root / "missing.txt")
        code, out = self.ws("check")
        self.assertEqual(code, 1)
        self.assertIn("the private deny list cannot be read", out)
        self.assertNotIn("missing.txt", out)

    def test_no_list_set_is_a_warning_and_nothing_is_checked(self):
        del os.environ["WS_DENY_LIST"]
        self.write("a.md", "globex corp\n")
        code, out = self.ws("check")
        self.assertEqual(code, 0)
        self.assertIn("warning: workspace.json:1: no private deny list", out)

    def test_with_no_variable_the_list_at_the_default_path_is_used(self):
        del os.environ["WS_DENY_LIST"]
        default = pathlib.Path(os.environ["HOME"]) / ".config" / "agent-ready-workspace" / "deny-list.txt"
        default.parent.mkdir(parents=True)
        default.write_text("\ufeffglobex corp\n", encoding="utf-8")   # a byte-order mark must not hide the first entry
        self.addCleanup(lambda: __import__("shutil").rmtree(os.environ["HOME"]))
        self.write("a.md", "globex corp\n")
        code, out = self.ws("check")
        self.assertEqual(code, 1)
        self.assertIn("a.md:1: matches line 1 of the private deny list", out)

    def test_a_matching_file_name_is_never_printed(self):
        self.write("plans/globex-corp-rollout.md", "# Rollout\n")
        code, out = self.ws("check")
        self.assertEqual(code, 1)
        self.assertIn("plans/<name ", out)
        self.assertNotIn("globex", out.lower())

    def test_the_manifest_cannot_carry_terms_or_redirect_the_list(self):
        for setting in ({"terms": ["zzz"]}, {"list": ""}):
            self.workspace({"use": "deny_list", **setting})
            self.write("a.md", "globex corp\n")
            code, out = self.ws("check")
            # The cases run with their own settings only, so the part loads, and then refuses the manifest's.
            self.assertEqual(code, 1, setting)
            self.assertIn("only its cases may", out, setting)


class RepositoryTests(unittest.TestCase):
    def test_every_part_passes_its_own_cases(self):
        for part in partlib.load_all(ROOT):
            self.assertEqual(part.failed_cases(), [], part.name)

    def test_this_repository_passes_its_own_checks(self):
        snapshot = snapshots.Tree(ROOT)
        for part in partlib.load_all(ROOT):
            if part.kind == "check":
                errors = [f for f in part.run(snapshot) if f["level"] == "error"]
                self.assertEqual(errors, [], part.name)


def _this_repositorys_ledger():
    file = ROOT / ".git" / "ws-ledger"
    return file.read_bytes() if file.is_file() else None


_LEDGER_BEFORE = _this_repositorys_ledger()


def tearDownModule():
    # No test may open or change the edit ledger of the repository the tests run in.
    if _this_repositorys_ledger() != _LEDGER_BEFORE:
        raise AssertionError("a test changed this repository's edit ledger, .git/ws-ledger")


if __name__ == "__main__":
    unittest.main()
