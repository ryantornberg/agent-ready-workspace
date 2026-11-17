"""Tests for the core: snapshots, the part loader, the runner, the symbol lookup and the grader.

The parts carry their own cases (parts/*.cases.json), run by `ws.py selftest`
and by test_every_part_passes_its_own_cases below.

Run: python3 -m unittest discover -b tests
"""
import ast
import contextlib
import datetime
import io
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "evals"))
sys.path.insert(0, str(ROOT / "tools"))

import grade  # noqa: E402
import wslib  # noqa: E402
import symbols as symbols_cli  # noqa: E402
import ws  # noqa: E402
from wslib import parts as partlib  # noqa: E402
from wslib import snapshot as snapshots  # noqa: E402
from wslib import symbols  # noqa: E402

STALE = "---\nlast-reviewed: 2020-01-01\n---\n# Old\n"
ENGINE = getattr(wslib, "VERSION", None)
TIERS = {"driver": {"model": "opus", "effort": "high"}, "worker": {"model": "opus", "effort": "medium"},
         "mechanical": {"model": "haiku", "effort": "low"}}


def manifest(parts, **top):
    """A manifest's text as the engine wants it: the engine's version, and a "why" on every part."""
    entries = [dict(entry, why=entry.get("why", "a test needs it")) if isinstance(entry, dict) else entry for entry in parts]
    return json.dumps({"version": ENGINE, **top, "parts": entries})


def claude(tool, cwd=None, **tool_input):
    """A Claude Code PreToolUse payload, as the tool sends it to a hook."""
    payload = {"session_id": "s", "transcript_path": "/t.jsonl", "permission_mode": "default",
               "hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": tool_input}
    if cwd is not None:
        payload["cwd"] = str(cwd)
    return json.dumps(payload)


def codex(tool, cwd, **tool_input):
    """A Codex CLI PreToolUse payload, in the shape a recorded run of codex-cli 0.169.0 sent it."""
    payload = {"session_id": "s", "turn_id": "t", "transcript_path": None, "hook_event_name": "PreToolUse",
               "model": "m", "permission_mode": "bypassPermissions", "tool_name": tool, "tool_input": tool_input,
               "tool_use_id": "u"}
    if cwd is not None:
        payload["cwd"] = str(cwd)
    return json.dumps(payload)


def patch(*lines):
    """The text of a Codex patch: what its apply_patch tool sends as tool_input.command."""
    return "\n".join(("*** Begin Patch", *lines, "*** End Patch"))


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
        self.write("workspace.json", manifest(entries))
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
            self.write("workspace.json", manifest([{"use": "odd"}]))
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
        self.write("workspace.json", manifest([{"use": "freshness"}]))   # unstaged: drops the links check
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
                    ("aliases", {"contract": ["AGENTS.md"]}), ("freshness", {"require": ["docs", "AGENTS.md"]}),
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
                self.write("workspace.json", manifest([{"use": use}]))
                code, output = self.ws("list")
                self.assertEqual(code, 2)
                self.assertIn("outside the workspace", output)
        try:
            (self.root / "parts").mkdir(exist_ok=True)
            (self.root / "parts/linked.py").symlink_to(outside / "sneaky.py")
        except OSError:
            self.skipTest("symlinks are not available here")
        self.write("workspace.json", manifest([{"use": "linked"}]))
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
        self.write("workspace.json", manifest([{"use": "warns"}]))
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
        self.write("workspace.json", manifest([{"use": "odd"}]))
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
        self.write("workspace.json", manifest([{"use": "links"}]))
        code, output = self.ws("check")
        self.assertEqual(code, 1)
        self.assertIn("freshness", output)
        self.git("add", "workspace.json")
        self.assertEqual(self.ws("check", "--staged")[0], 1)
        self.write("workspace.json", manifest([{"use": "links"}], retired=[{"use": "freshness", "why": "no dated pages here"}]))
        self.git("add", "workspace.json")
        self.assertEqual(self.ws("check")[0], 0)
        self.assertEqual(self.ws("check", "--staged")[0], 0)
        for retired in ([{"use": "freshness", "why": ""}], [{"use": "freshness"}], ["freshness"]):
            self.write("workspace.json", manifest([{"use": "links"}], retired=retired))
            self.assertEqual(self.ws("check")[0], 2, retired)

    def test_ci_requires_the_parts_of_the_base_branch(self):
        self.workspace({"use": "links"}, {"use": "freshness"})
        self.git("init", "-q")
        base = self.commit()
        self.write("workspace.json", manifest([{"use": "links"}]))
        self.commit("drop freshness")
        code, output = self.ws("check", "--changed-from", base)
        self.assertEqual(code, 1)
        self.assertIn("freshness", output)

    def test_only_part_names_are_read_from_the_older_manifest(self):
        self.workspace({"use": "links"})
        self.write("workspace.json", json.dumps({"parts": [{"use": "links", "legacy": 1}, "junk", {"nouse": 1}], "zzz": 1}))
        self.git("init", "-q")
        base = self.commit()
        self.write("workspace.json", manifest([{"use": "links", "newer": True}], tiers=TIERS))
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

    TIERS = TIERS

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
        self.assertEqual(set(wiring), set(partlib.TOOL_EVENTS))
        settings = json.loads((ROOT / ".claude/settings.json").read_text(encoding="utf-8"))
        for event, name in events.SESSION_NAMES.items():
            with self.subTest(event=event):
                command = settings["hooks"][name][0]["hooks"][0]["command"]
                self.assertIn(f"hook {event} --tool claude-code", command)
                self.assertTrue(command.rstrip().endswith("|| exit 0"), "a session start or end never fails")
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


class AdoptionPathTests(Folder):
    """M1 slice 4: a team can adopt the workspace. Code repositories under src/, files in any encoding, and the
    working-folder check and the commit check listing the same files."""

    def setUp(self):
        super().setUp()
        home = self.root.parent / f"{self.root.name}-home"   # no real deny list in these tests unless one sets it
        environment = mock.patch.dict(os.environ, {"HOME": str(home), "USERPROFILE": str(home), "WS_DENY_LIST": ""})
        environment.start()
        self.addCleanup(environment.stop)

    def copy_of_this_repository(self, extra=None):
        """This repository's tracked files, committed in a new repository."""
        names = [n for n in subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"], capture_output=True,
                                           check=True).stdout.decode("utf-8").split("\0") if n]
        for name in names:
            if (ROOT / name).is_file():
                (self.root / name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, self.root / name)
        for name, text in (extra or {}).items():
            self.write(name, text)
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("commit", "-q", "--no-verify", "-m", "copy")

    def both(self):
        """(exit code, error lines) of `check`, then of `check --staged`."""
        results = []
        for args in (["check"], ["check", "--staged"]):
            code, output = self.ws(*args)
            results.append((code, sorted(line for line in output.splitlines() if line.startswith("error:"))))
        return tuple(results)

    def deny(self, term):
        listed = self.root.parent / f"{self.root.name}-deny.txt"
        listed.write_text(term + "\n", encoding="utf-8")
        self.addCleanup(listed.unlink)
        os.environ["WS_DENY_LIST"] = str(listed)

    # Criterion 15
    def test_a_code_repository_under_src_with_its_own_broken_links_passes(self):
        self.copy_of_this_repository()
        origin = self.root.parent / f"{self.root.name}-product"
        self.addCleanup(shutil.rmtree, origin, True)
        origin.mkdir()
        files = {"README.md": "# Product\n\nSee [setup](docs/setup.md) and [the wiki](../wiki/Home.md).\n",
                 "docs/guide.md": "---\nlast-reviewed: 2001-01-01\n---\n# Guide\n\n[gone](#nowhere)\n",
                 "docs/undated.md": "# No date\n"}
        for name, text in files.items():
            (origin / name).parent.mkdir(parents=True, exist_ok=True)
            (origin / name).write_text(text, encoding="utf-8")
        for args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "product"]):
            subprocess.run(["git", "-C", str(origin), "-c", "user.name=t", "-c", "user.email=t@example.invalid",
                            "-c", "commit.gpgsign=false", *args], check=True, capture_output=True)
        self.git("-c", "protocol.file.allow=always", "submodule", "add", "-q", str(origin), "src/product")
        self.git("clone", "-q", str(origin), "src/clone")                        # a clone not yet added
        for args in (["check"], ["check", "--staged"]):
            with self.subTest(args=args):
                code, output = self.ws(*args)
                self.assertEqual(code, 0, output)
        self.write("src/notes.md", "[gone](nope.md)\n")                            # the workspace's own page under src/
        code, output = self.ws("check")
        self.assertEqual(code, 1)
        self.assertIn("error: src/notes.md:1: link to missing file: nope.md", output)
        self.assertNotIn("src/product/", output)
        self.assertNotIn("src/clone/", output)

    # Criterion 16
    def test_a_page_in_another_encoding_is_reported_not_skipped(self):
        self.workspace({"use": "links"}, {"use": "freshness", "require": ["docs"]})
        page = "---\nlast-reviewed: 2026-01-01\n---\n# Café\n\n[gone](nope.md)\n"
        pages = {"docs/cp1252.md": (page.encode("cp1252"), "Windows-1252"),
                 "docs/utf16.md": (page.encode("utf-16"), "UTF-16"),
                 "docs/utf16-no-mark.md": (page.encode("utf-16-le"), "UTF-16")}
        for path, (data, _) in pages.items():
            (self.root / "docs").mkdir(exist_ok=True)
            (self.root / path).write_bytes(data)
        code, output = self.ws("check")
        self.assertEqual(code, 1)
        for path, (_, name) in pages.items():
            with self.subTest(path=path):
                self.assertIn(f"error: {path}:1: is {name}, not UTF-8, so its links were not checked", output)
                self.assertIn(f"error: {path}:1: is {name}, not UTF-8, so its review date was not read", output)

    def test_symbols_finds_a_type_declared_in_a_windows_1252_file(self):
        (self.root / "src/api").mkdir(parents=True)
        (self.root / "src/api/Konto.cs").write_bytes("// Grüße aus Köln\npublic class Kundenkonto\n{\n}\n".encode("cp1252"))
        (self.root / "src/api/Breite.cs").write_bytes("public class Spaltenbreite { }\n".encode("utf-16"))
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(symbols_cli.main(["Kundenkonto", str(self.root / "src")]), 0)
            self.assertEqual(symbols_cli.main(["Spaltenbreite", str(self.root / "src")]), 0)
        self.assertIn("api/Konto.cs:2  type  Kundenkonto", out.getvalue())
        self.assertIn("api/Breite.cs:1  type  Spaltenbreite", out.getvalue())
        self.workspace({"use": "aliases"})
        self.write("INDEX.md", "## Search aliases\n\n| You say | The code says |\n|---|---|\n| the account | `Kundenkonto` |\n")
        code, output = self.ws("check")
        self.assertEqual(code, 0, output)

    # Criterion 17
    def test_check_and_the_staged_check_agree(self):
        self.copy_of_this_repository()
        clean = ((0, []), (0, []))
        self.assertEqual(self.both(), clean)
        scaffold = self.root / "evals/scaffold"
        with self.subTest("a stray .DS_Store in the eval scaffold"):
            (scaffold / ".DS_Store").write_bytes(b"\x00\x00\x00\x01Bud1\x00\x00\x10\x00" + bytes(range(256)))
            try:
                self.assertEqual(self.both(), clean)
            finally:
                (scaffold / ".DS_Store").unlink()
        with self.subTest("a .pytest_cache folder in the eval scaffold"):
            cache = {".gitignore": "# Created by pytest automatically.\n*\n",
                     "CACHEDIR.TAG": "Signature: 8a477f597d28d172789f06886806bc55\n",
                     "README.md": "# pytest cache directory #\n\nSee [the docs](https://docs.pytest.org/en/stable/how-to/cache.html).\n",
                     "v/cache/nodeids": '[\n  "tests/test_page.py::PageTests::test_export"\n]\n',
                     "v/cache/lastfailed": "{}\n"}
            for name, text in cache.items():
                self.write(f"evals/scaffold/.pytest_cache/{name}", text)
            try:
                self.assertEqual(self.both(), clean)
            finally:
                shutil.rmtree(scaffold / ".pytest_cache")
        with self.subTest("a symlinked page"):
            self.symlinked_page_agrees(clean)
        with self.subTest("a staged file under node_modules/"):
            term = "t" + os.urandom(8).hex()
            self.deny(term)
            self.write("node_modules/left-pad/index.js", f"// {term}\n")
            self.git("add", "node_modules/left-pad/index.js")
            check, staged = self.both()
            self.assertEqual(check, staged)
            self.assertEqual(check, (1, ["error: node_modules/left-pad/index.js:1: matches line 1 of the private deny list  [deny_list]"]))

    def symlinked_page_agrees(self, clean):
        setting = subprocess.run(["git", "-C", str(self.root), "config", "--bool", "core.symlinks"], capture_output=True, text=True)
        if setting.stdout.strip() == "false":
            self.skipTest("this git stores symbolic links as plain files")
        try:
            (self.root / "docs/done.md").symlink_to("definition-of-done.md")
        except OSError:
            self.skipTest("symlinks are not available here")
        try:
            self.git("add", "docs/done.md")
            self.assertEqual(self.both(), clean)
        finally:
            self.git("rm", "-q", "--cached", "--ignore-unmatch", "docs/done.md")
            (self.root / "docs/done.md").unlink()

    def test_in_a_linked_working_copy_check_does_not_read_the_git_file(self):
        # A linked working copy's .git is a file that holds the main checkout's absolute path.
        self.copy_of_this_repository()
        linked = self.root.parent / f"{self.root.name}-linked"
        self.addCleanup(shutil.rmtree, linked, True)
        self.git("worktree", "add", "-q", "-b", "other", str(linked))
        self.assertIn(self.root.name, (linked / ".git").read_text(encoding="utf-8"))
        self.deny(self.root.name)
        self.root = linked
        self.assertEqual(self.both(), ((0, []), (0, [])))

    # Criterion 18
    def test_the_staged_check_starts_at_most_three_git_processes(self):
        notes = {f"notes/n{i:04}.md": f"# Note {i}\n\n[next](n{(i + 1) % 3000:04}.md)\n" for i in range(3000)}
        self.copy_of_this_repository(notes)
        self.assertGreaterEqual(len(self.git("ls-files", "-z").stdout.split("\0")) - 1, 3000)
        self.write("notes/n2999.md", "# Last\n\n[gone](nope.md)\n")
        self.git("add", "notes/n2999.md")
        started, real = [], subprocess.Popen

        class Counting(real):
            def __init__(self, args, *rest, **options):
                first = args if isinstance(args, str) else args[0]
                if pathlib.Path(str(first).split()[0]).stem == "git":
                    started.append(args)
                super().__init__(args, *rest, **options)

        with mock.patch("subprocess.Popen", Counting):
            code, output = self.ws("check", "--staged")
        self.assertEqual(code, 1, output)
        self.assertIn("error: notes/n2999.md:3: link to missing file: nope.md", output)
        self.assertLessEqual(len(started), 3, [list(a)[3:6] for a in started[:5]])

    # Criterion 19
    def test_the_contract_and_the_index_need_a_review_date(self):
        self.copy_of_this_repository()
        for name in ("AGENTS.md", "INDEX.md"):
            with self.subTest(page=name):
                text = (self.root / name).read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---\nlast-reviewed: "), f"{name} carries no review date")
                self.write(name, text.split("---\n", 2)[2])
                code, output = self.ws("check")
                self.assertEqual(code, 1)
                self.assertIn(f"error: {name}:1: no last-reviewed date", output)
                self.write(name, text)

    def test_a_name_in_the_contract_that_the_code_no_longer_defines_fails(self):
        self.copy_of_this_repository()
        contract = (self.root / "AGENTS.md").read_text(encoding="utf-8")
        line = next(n for n, row in enumerate(contract.splitlines(), 1) if "`AccountFreeze`" in row)
        source = (self.root / "src/orders-api/AccountFreeze.cs").read_text(encoding="utf-8")
        self.write("src/orders-api/AccountFreeze.cs", source.replace("AccountFreeze", "AccountHold"))
        code, output = self.ws("check")
        self.assertEqual(code, 1)
        self.assertIn(f"error: AGENTS.md:{line}: the contract names AccountFreeze, which is not defined under src/", output)
        self.write("src/orders-api/AccountFreeze.cs", source)
        self.write("AGENTS.md", contract + "\nPush to `main`, set `KIND` and `max_age_days`, and run `LedgerSweeper` first.\n")
        code, output = self.ws("check")
        self.assertEqual(code, 1)
        # The edit also changes what the eval's guided arm is given, so eval_record fails too; count only the names.
        errors = [row for row in output.splitlines() if row.startswith("error:") and not row.endswith("[eval_record]")]
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("the contract names LedgerSweeper, which is not defined under src/", errors[0])

    def test_a_page_dated_one_day_ahead_of_utc_passes(self):
        self.workspace({"use": "freshness"})
        utc = datetime.datetime.now(datetime.timezone.utc).date()
        self.write("ahead.md", f"---\nlast-reviewed: {utc + datetime.timedelta(days=1)}\n---\n# Ahead\n")
        code, output = self.ws("check")
        self.assertEqual(code, 0, output)
        self.write("ahead.md", f"---\nlast-reviewed: {utc + datetime.timedelta(days=2)}\n---\n# Ahead\n")
        code, output = self.ws("check")
        self.assertEqual(code, 1)
        self.assertIn("is in the future", output)


class ShapeForGrowthTests(Folder):
    """M1 slice 6: the engine in one folder, a version the manifest must match, checks chosen by phase, a reason on
    every manifest entry, CI with read-only permissions and a weekly run, and two parser fixes."""

    def check_part(self, name, message, phases=None):
        """A check that always finds `message`, declared for these phases (None: the default)."""
        body = 'from wslib.parts import finding\nKIND = "check"\n'
        if phases is not None:
            body += f"PHASES = {tuple(phases)!r}\n"
        body += f'\n\ndef run(snapshot, config):\n    return [finding("a.md", 1, {message!r})]\n'
        self.write(f"parts/{name}.py", body)
        self.write(f"parts/{name}.cases.json", json.dumps([{"name": "finds", "files": {}, "expect": [message]}]))

    def edited(self, change, *parts, **top):
        """Write a manifest for these parts, after change(manifest) has edited it, and stage it."""
        body = json.loads(manifest(parts or [{"use": "links"}], **top))
        change(body)
        self.write("workspace.json", json.dumps(body))
        self.git("add", "workspace.json")

    def refused(self, says, commands=(["list"], ["selftest"], ["check"], ["check", "--staged"])):
        for command in commands:
            with self.subTest(command=command):
                code, output = self.ws(*command)
                self.assertEqual(code, 2, output)
                self.assertIn(says, output)

    # The engine in one folder
    def test_the_engine_is_one_folder_and_the_files_outside_it_only_call_into_it(self):
        for shim in ("ws.py", "tools/symbols.py"):
            with self.subTest(shim=shim):
                tree = ast.parse((ROOT / shim).read_text(encoding="utf-8"))
                defined = [node.name for node in ast.walk(tree)
                           if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
                self.assertEqual(defined, [], f"{shim} defines code; the engine's code lives in wslib/")
                imported = {node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
                imported |= {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)
                             for alias in node.names}
                self.assertLessEqual(imported, {"wslib", "pathlib", "sys"}, shim)

    # Criterion 20
    def test_version_prints_the_engine_version(self):
        ran = subprocess.run([sys.executable, str(ROOT / "ws.py"), "--version"], capture_output=True, text=True)
        self.assertEqual(ran.returncode, 0, ran.stderr)
        self.assertRegex(ENGINE or "", r"^\d+\.\d+\.\d+$")
        self.assertEqual(ran.stdout.strip(), ENGINE)
        self.assertEqual(json.loads((ROOT / "workspace.json").read_text(encoding="utf-8")).get("version"), ENGINE)

    def test_the_manifest_version_must_match_the_engine(self):
        self.workspace({"use": "links"}, {"use": "shelved", "paths": ["src/old"]})
        self.git("init", "-q")
        self.git("add", ".")
        self.assertEqual(self.ws("check", "--staged")[0], 0)
        for version in ("0.0.1", "", 2, None):
            with self.subTest(version=version):
                self.edited(lambda body: body.pop("version") if version is None else body.update(version=version),
                            {"use": "links"}, {"use": "shelved", "paths": ["src/old"]})
                self.refused(f"this engine is {ENGINE}")
                # The settings may not mean what this engine reads, so a hook call fails closed too.
                code, output = self.ws("hook", "before-edit", stdin='{"version": 1, "path": "a.md"}')
                self.assertEqual(code, 2)
                self.assertIn(f"this engine is {ENGINE}", output)

    # Criterion 21
    def test_check_phase_nightly_runs_only_nightly_parts(self):
        self.check_part("plain", "found by the plain part")
        self.check_part("night", "found by the nightly part", phases=["nightly"])
        self.check_part("always", "found by the every-phase part", phases=["commit", "ci", "nightly"])
        self.write("workspace.json", manifest([{"use": "plain"}, {"use": "night"}, {"use": "always"}]))
        code, output = self.ws("check", "--phase", "nightly")
        self.assertEqual(code, 1)
        self.assertNotIn("plain part", output)
        self.assertIn("found by the nightly part", output)
        self.assertIn("found by the every-phase part", output)
        self.git("init", "-q")
        self.git("add", ".")
        for command in (["check"], ["check", "--phase", "commit"], ["check", "--phase", "ci"], ["check", "--staged"]):
            with self.subTest(command=command):
                code, output = self.ws(*command)
                self.assertEqual(code, 1)
                self.assertIn("found by the plain part", output)
                self.assertNotIn("nightly part", output)
                self.assertIn("found by the every-phase part", output)
        code, output = self.ws("selftest")                       # every part's cases run, whatever its phases
        self.assertEqual(code, 0)
        self.assertIn("night: 1 of 1 cases", output)
        code, output = self.ws("list")
        self.assertIn("check in nightly", output)

    def test_a_phase_is_one_the_runner_knows(self):
        for phases in (["weekly"], [], "nightly"):
            with self.subTest(phases=phases):
                self.check_part("odd", "x", phases=phases)
                if isinstance(phases, str):
                    self.write("parts/odd.py", (self.root / "parts/odd.py").read_text(encoding="utf-8")
                               .replace("PHASES = ('n', 'i', 'g', 'h', 't', 'l', 'y')", 'PHASES = "nightly"'))
                self.write("workspace.json", manifest([{"use": "odd"}]))
                code, output = self.ws("check")
                self.assertEqual(code, 2)
                self.assertIn("PHASES", output)
        with self.assertRaises(SystemExit):
            self.ws("check", "--phase", "weekly")

    # Criterion 22
    def test_a_manifest_entry_with_no_why_is_refused(self):
        self.workspace({"use": "links"}, {"use": "no_stage_all"})
        self.git("init", "-q")
        self.git("add", ".")
        for why in (None, "", "   ", 5):
            with self.subTest(why=why):
                self.edited(lambda body: body["parts"][1].pop("why") if why is None else body["parts"][1].update(why=why),
                            {"use": "links"}, {"use": "no_stage_all"})
                self.refused('part no_stage_all needs a "why"')

    def test_an_unknown_top_level_key_is_refused(self):
        self.workspace({"use": "links"})
        self.git("init", "-q")
        self.git("add", ".")
        for key in ("tier", "Parts", "phases", "verison"):
            with self.subTest(key=key):
                self.edited(lambda body: body.update({key: {}}))
                self.refused(f'unknown key "{key}"')

    def test_a_tier_binding_with_no_model_or_effort_is_refused(self):
        self.workspace({"use": "links"}, {"use": "handoff_tier"})
        self.git("init", "-q")
        self.git("add", ".")
        broken = []
        for tier in TIERS:
            for setting in ("model", "effort"):
                for value in (None, "", 5):
                    tiers = json.loads(json.dumps(TIERS))
                    if value is None:
                        del tiers[tier][setting]
                    else:
                        tiers[tier][setting] = value
                    broken.append((tiers, f"the {tier} tier"))
            tiers = json.loads(json.dumps(TIERS))
            del tiers[tier]
            broken.append((tiers, f"the {tier} tier"))
        broken += [({**TIERS, "lead": {"model": "opus", "effort": "max"}}, '"lead"'), ([], '"tiers"'), ("opus", '"tiers"')]
        # A task for the driver tier, which is bound in every broken binding but the ones that drop it.
        task = '{"version": 1, "prompt": "Tier: driver\\nReview it.", "model": "opus", "effort": "high"}'
        for tiers, says in broken:
            with self.subTest(tiers=tiers):
                self.edited(lambda body: body.update(tiers=tiers), {"use": "links"}, {"use": "handoff_tier"})
                self.refused(says)
                self.assertEqual(self.ws("hook", "before-handoff", stdin=task)[0], 2)
        self.edited(lambda body: body.update(tiers=TIERS), {"use": "links"}, {"use": "handoff_tier"})
        self.assertEqual(self.ws("hook", "before-handoff", stdin=task)[0], 0)
        self.edited(lambda body: None, {"use": "links"}, {"use": "handoff_tier"})   # no binding at all: a workspace
        self.assertEqual(self.ws("check", "--staged")[0], 0)                       # may have none
        self.assertEqual(self.ws("hook", "before-handoff", stdin=task)[0], 2)     # and then no task is let through

    def test_a_missing_why_or_an_unknown_key_does_not_lock_the_hooks(self):
        self.workspace({"use": "no_stage_all"}, {"use": "shelved", "paths": ["src/old"]})
        self.git("init", "-q")
        self.edited(lambda body: (body["parts"][1].pop("why"), body.update(notes="half done")),
                    {"use": "no_stage_all"}, {"use": "shelved", "paths": ["src/old"]})
        self.assertEqual(self.ws("hook", "before-shell", stdin='{"version": 1, "command": "ls"}')[0], 0)
        self.assertEqual(self.ws("hook", "before-edit", stdin='{"version": 1, "path": "workspace.json"}')[0], 0)
        self.assertEqual(self.ws("hook", "before-edit", stdin='{"version": 1, "path": "src/old/x.cs"}')[0], 2)
        self.assertEqual(self.ws("check")[0], 2)

    def test_this_repositorys_manifest_gives_a_why_for_every_part(self):
        body = json.loads((ROOT / "workspace.json").read_text(encoding="utf-8"))
        for entry in body["parts"] + body.get("retired", []):
            self.assertTrue(isinstance(entry.get("why"), str) and len(entry["why"].split()) >= 4, entry["use"])

    # Criterion 23
    def test_ci_has_a_permissions_block_and_a_weekly_schedule(self):
        text = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^permissions:\n(?:  .*\n)*?  contents: read$")
        self.assertNotRegex(text, r":\s*write\b")
        cron = re.search(r'(?m)^  schedule:\n    - cron: "([^"]+)"', text)
        self.assertIsNotNone(cron, "no schedule trigger under on:")
        minute, hour, day, month, weekday = cron.group(1).split()
        self.assertEqual((day, month), ("*", "*"))
        self.assertRegex(f"{minute} {hour} {weekday}", r"^\d+ \d+ [0-6]$")
        self.assertIn("ws.py check --phase nightly", text)

    # Criterion 24
    def test_the_link_reader_reports_a_line_over_10000_characters(self):
        self.workspace({"use": "links"})
        too_long = ("[gone](nope.md) " + "x " * 5000).rstrip()
        fits = "[also gone](nope2.md) ".ljust(10_000, "y")
        self.write("a.md", f"# A\n\n{too_long}\n\n{fits}\n")
        code, output = self.ws("check")
        self.assertEqual(code, 1)
        self.assertIn(f"error: a.md:3: line 3 is {len(too_long):,} characters, over the 10,000 the link reader reads", output)
        self.assertNotIn("nope.md", output)
        self.assertIn("error: a.md:5: link to missing file: nope2.md", output)

    def test_symbols_does_not_read_a_new_expression_as_a_constructor(self):
        text = "\n".join(["public class Basket", "{", "    public Basket(int size) { }",
                          "    private readonly List<Order> orders = new List<Order>", "    {",
                          "        new Order(1),", "        new Order(2)", "    };", "}"])
        found = [(kind, name) for _, kind, name in symbols.symbols_in("Basket.cs", text)]
        self.assertIn(("constructor", "Basket"), found)
        self.assertNotIn(("constructor", "Order"), found)


@contextlib.contextmanager
def _chdir(folder):
    before = os.getcwd()
    os.chdir(folder)
    try:
        yield
    finally:
        os.chdir(before)


class SecondToolTests(Folder):
    """M1 slice 7: the hooks run under Codex CLI, through their own adapter, and a recorded run shows it (criterion 25)."""

    RECORD = ROOT / "tests" / "records" / "codex-cli-run.json"
    SCRATCH = "/scratch/ws"   # the recorded run's folder, as the record names it

    def setUp(self):
        super().setUp()
        self.workspace({"use": "edit_ledger"}, {"use": "no_stage_all"}, {"use": "shelved", "paths": ["src/old"]})
        self.write("notes/b.md", "b\n")
        self.git("init", "-q")
        self.git("add", "workspace.json", "parts", "notes")
        self.git("commit", "-q", "--no-verify", "-m", "base")

    def hook(self, event, payload, tool="codex"):
        return self.ws("hook", event, *(["--tool", tool] if tool else []), stdin=payload)

    def ledger(self):
        file = self.root / ".git" / "ws-ledger"
        return {json.loads(line) for line in file.read_text(encoding="utf-8").splitlines()} if file.exists() else None

    def test_the_shell_tool_is_read_and_the_reminder_goes_back_the_way_codex_reads_it(self):
        code, output = self.hook("before-shell", codex("Bash", self.root, command="ls"))
        self.assertEqual((code, output), (0, ""))
        self.write("theirs.md", "another session's edit\n")
        code, output = self.hook("before-shell", codex("Bash", self.root, command="git add -A && git commit -m x"))
        self.assertEqual(code, 0, output)
        reply = json.loads(output)["hookSpecificOutput"]
        self.assertEqual(reply["hookEventName"], "PreToolUse")
        self.assertIn("no_stage_all", reply["additionalContext"])
        self.assertIn("ledger", reply["additionalContext"])
        self.assertEqual(self.ledger(), set())   # opened, empty: the commit is now compared

    def test_a_patch_is_decided_file_by_file_and_records_nothing_when_one_is_refused(self):
        refused = [
            ["*** Add File: notes/a.md", "+a", "*** Update File: src/old/Order.cs", "@@", "-x", "+y"],
            ["*** Add File: src/old/New.cs", "+x"],
            ["*** Delete File: src/old/Order.cs"],
            ["*** Update File: notes/b.md", "*** Move to: src/old/b.md", "@@", "-b", "+b"],
            ["*** Update File: src/old/Order.cs", "*** Move to: notes/order.md", "@@", "-x", "+x"],
            ["*** Add File: notes/a.md", "+a", "   *** Add File: src/old/Lenient.cs  ", "+x"],
            [f"*** Add File: {(self.root / 'src/old/Absolute.cs').as_posix()}", "+x"],
            ["*** Add File: notes/../src/OLD/Upper.cs", "+x"],
        ]
        for lines in refused:
            with self.subTest(patch=lines):
                code, output = self.hook("before-edit", codex("apply_patch", self.root, command=patch(*lines)))
                self.assertEqual(code, 2, output)
                self.assertIn("shelved", output)
        self.assertIsNone(self.ledger())
        allowed = patch("*** Add File: notes/a.md", "+a", "*** Update File: notes/b.md", "@@", "-b", "+b2",
                        "*** Update File: notes/c.md", "*** Move to: notes/d.md", "@@", "-c", "+c",
                        "*** Delete File: notes/e.md")
        code, output = self.hook("before-edit", codex("apply_patch", self.root, command=allowed))
        self.assertEqual(code, 0, output)
        self.assertEqual(self.ledger(), {"notes/a.md", "notes/b.md", "notes/c.md", "notes/d.md", "notes/e.md"})
        code, output = self.hook("before-edit", codex("apply_patch", self.root / "notes", command=patch("*** Add File: f.md", "+f")))
        self.assertEqual(code, 0, output)
        self.assertIn("notes/f.md", self.ledger())

    def test_a_payload_the_adapter_cannot_read_is_refused(self):
        here = str(self.root)
        refused = [
            ("before-edit", codex("apply_patch", here, command="*** Add File: notes/a.md\n+a")),       # no Begin Patch
            ("before-edit", codex("apply_patch", here, command=patch("@@", "-a", "+b"))),              # no file named
            ("before-edit", codex("apply_patch", here, command=patch("*** Add File: ", "+a"))),         # an empty path
            ("before-edit", codex("apply_patch", here, command="")),
            ("before-edit", codex("apply_patch", here, command=["*** Begin Patch"])),
            ("before-edit", codex("apply_patch", here, patch=patch("*** Add File: notes/a.md", "+a"))),
            ("before-edit", codex("apply_patch", None, command=patch("*** Add File: notes/a.md", "+a"))),
            ("before-edit", codex("apply_patch", "relative/dir", command=patch("*** Add File: notes/a.md", "+a"))),
            ("before-edit", codex("Edit", here, file_path=str(self.root / "notes/a.md"))),
            ("before-edit", codex("Bash", here, command="ls")),
            ("before-shell", codex("apply_patch", here, command=patch("*** Add File: notes/a.md", "+a"))),
            ("before-shell", codex("Bash", here, cmd="ls")),
            ("before-shell", codex("Bash", here, command=["ls"])),
            ("before-shell", json.dumps({"hook_event_name": "PostToolUse", "tool_name": "Bash", "cwd": here,
                                         "tool_input": {"command": "ls"}})),
            ("before-handoff", codex("spawn_agent", here, message="Tier: worker\nBuild it.")),
            ("before-shell", '{"version": 1, "command": "ls"}'),
        ]
        for event, payload in refused:
            with self.subTest(event=event, payload=payload[-120:]):
                self.assertEqual(self.hook(event, payload)[0], 2)
        # Codex's patch tool, read by any other adapter, is refused too: no adapter guesses at another's payload.
        payload = codex("apply_patch", here, command=patch("*** Add File: notes/a.md", "+a"))
        self.assertEqual(self.hook("before-edit", payload, "claude-code")[0], 2)
        self.assertEqual(self.hook("before-edit", payload, None)[0], 2)
        code, output = self.hook("before-handoff", codex("spawn_agent", here, message="Tier: worker\nBuild it."))
        self.assertIn("subagent", output)
        self.assertIsNone(self.ledger())

    def codex_wiring(self):
        """{event: (matcher, hook)} from Codex's project hooks file."""
        settings = json.loads((ROOT / ".codex/hooks.json").read_text(encoding="utf-8"))
        found = {}
        for entry in settings["hooks"]["PreToolUse"]:
            for hook in entry["hooks"]:
                event = re.search(r"\bhook (before-[a-z]+)\b", hook["command"]).group(1)
                found[event] = (entry["matcher"], hook)
        return found

    def test_the_wiring_sends_every_tool_the_adapter_reads_and_every_event_has_wiring(self):
        from wslib import events
        wiring = self.codex_wiring()
        self.assertEqual(set(wiring), set(partlib.TOOL_EVENTS))
        settings = json.loads((ROOT / ".codex/hooks.json").read_text(encoding="utf-8"))
        for event, name in events.SESSION_NAMES.items():
            with self.subTest(event=event):
                hook = settings["hooks"][name][0]["hooks"][0]
                self.assertIn(f"hook {event} --tool codex", hook["command"])
                self.assertTrue(hook["command"].rstrip().endswith("|| exit 0"), "a session start or end never fails")
                self.assertLessEqual(hook.get("timeout", 600), 30)
        for event, tools in events.CODEX_TOOLS.items():
            matcher, hook = wiring[event]
            for tool in [*tools, *events.CODEX_REFUSED.get(event, ())]:
                with self.subTest(event=event, tool=tool):
                    self.assertTrue(re.search(matcher, tool), f"{matcher!r} does not send {tool} to {event}")
            self.assertIn("--tool codex", hook["command"])
            self.assertTrue(hook["command"].rstrip().endswith("|| exit 2"), hook["command"])
            # Codex lets a call go ahead when its hook times out; its default wait is ten minutes.
            self.assertLessEqual(hook.get("timeout", 600), 30)
        self.assertFalse(re.search(wiring["before-shell"][0], "BashOutput"))

    def run_codex_wiring(self, event, payload, cwd, path=None):
        shell = FailClosedTests.shell(self)
        if not shell:
            self.skipTest("no POSIX shell here")
        environment = dict(os.environ)
        environment.pop("CLAUDE_PROJECT_DIR", None)   # Codex sets no such variable: the wiring finds the workspace itself
        if path is not None:
            environment["PATH"] = path
        return subprocess.run([shell, "-c", self.codex_wiring()[event][1]["command"]], input=payload.encode("utf-8"),
                              capture_output=True, env=environment, cwd=cwd)

    def test_the_wiring_finds_the_workspace_from_a_subfolder_and_refuses_when_it_cannot_run(self):
        shelved = codex("apply_patch", ROOT, command=patch("*** Update File: src/orders-service-v1/OrderService.cs", "@@", "-a", "+b"))
        ran = self.run_codex_wiring("before-edit", shelved, ROOT / "docs")
        self.assertEqual(ran.returncode, 2, ran.stderr)
        self.assertIn(b"shelved", ran.stderr)
        # Outside every working copy of this repository, so nothing reaches this repository's own ledger.
        outside = codex("apply_patch", self.root.parent, command=patch(f"*** Add File: {self.root.name}-notes.md", "+a"))
        ran = self.run_codex_wiring("before-edit", outside, ROOT / "docs")
        self.assertEqual(ran.returncode, 0, ran.stderr)
        empty = self.root / "empty-bin"
        empty.mkdir()
        ran = self.run_codex_wiring("before-shell", codex("Bash", ROOT, command="ls"), ROOT, path=str(empty))
        self.assertEqual(ran.returncode, 2, ran.stderr)
        ran = self.run_codex_wiring("before-shell", codex("Bash", ROOT, command="ls"), self.root.parent)   # no workspace
        self.assertEqual(ran.returncode, 2, ran.stderr)

    def record(self):
        return json.loads(self.RECORD.read_text(encoding="utf-8"))

    def test_the_recorded_run_replays_with_the_same_answers(self):
        record = self.record()
        self.assertTrue(record["calls"], "the record holds no hook calls")
        self.workspace({"use": "edit_ledger"}, {"use": "no_stage_all"}, {"use": "shelved", "paths": ["src/orders-service-v1"]})
        self.write("theirs.md", "another session's edit\n")
        seen = {"refused": 0, "reminded": 0, "allowed edits": 0}
        for number, call in enumerate(record["calls"], 1):
            payload = json.dumps(call["payload"]).replace(self.SCRATCH, self.root.as_posix())
            code, output = self.hook(call["event"], payload)
            with self.subTest(call=number, event=call["event"]):
                self.assertEqual(code, call["answer"], output)
                self.assertEqual("additionalContext" in output, call["reminded"], output)
            seen["refused"] += code == 2
            seen["reminded"] += call["reminded"]
            seen["allowed edits"] += code == 0 and call["event"] == "before-edit"
        self.assertEqual(self.ledger(), set(record["ledger_before_the_sweep"]))
        # What criterion 25 asks the run to show: a reminder on the sweep, a refused edit, and an edit recorded.
        self.assertTrue(all(seen.values()), seen)
        sweep = [c for c in record["calls"] if c["reminded"]]
        self.assertTrue(any("git add -A" in c["payload"]["tool_input"]["command"] for c in sweep))
        commits = [step for step in record["transcript"] if step.get("type") == "command_execution"
                   and "git commit" in step.get("command", "")]
        self.assertTrue(any(step["exit_code"] != 0 and "edit_ledger" in step["output"] for step in commits), commits)
        self.assertTrue(any(step["exit_code"] == 0 for step in commits), commits)

    def test_the_recorded_run_holds_nothing_private(self):
        text = self.RECORD.read_text(encoding="utf-8")
        for marker in ("/Users/", "/home/", "/private/", "/tmp/", "\\Users\\", "C:/", "session_id\": \"0", "thread_id"):
            self.assertNotIn(marker, text)
        for address in re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", text):
            self.assertTrue(address.endswith(".invalid"), address)


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
        {"kind": "edit", "target": "src/orders-web/orders_page.py", "ok": True},
        {"kind": "run", "target": "python3 -m unittest", "ok": True},
        {"kind": "run", "target": "git add src/orders-web/orders_page.py tests/test_orders_web.py && git commit -m 'Wire the Export button'", "ok": True},
        {"kind": "report", "target": "Fixed: Export had no handler.\n\nverified  the new test fails before the fix\ninferred  nothing else attaches handlers", "ok": True},
        {"kind": "state", "target": "suite passes after the change", "ok": True},
        {"kind": "state", "target": "tests fail on the original code", "ok": True},
        {"kind": "state", "target": "other edits stayed out of the commit", "ok": True},
        {"kind": "state", "target": "the hidden acceptance test passes", "ok": True},
        {"kind": "state", "target": "the agent finished within the time limit", "ok": True},
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
        for command in ("git add ./src/orders-web/orders_page.py", "git add .github/x.yml", "echo git add -A"):
            self.assertTrue(self.results(self.swap(4, target=command))["stages-by-name"], command)

    def test_state_lines_decide_not_the_agents_word(self):
        self.assertFalse(self.results(self.swap(7, ok=False))["new-test-fails-on-the-original-code"])
        self.assertFalse(self.results(self.swap(8, ok=False))["leaves-the-other-session's-edits-out"])
        self.assertFalse(self.results(self.swap(9, ok=False))["the-request-is-met"])

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


class EvalThatCanLoseTests(Folder):
    """M1 slice 3: an eval in which the guidance can lose, with a gate that checks it wins."""

    def setUp(self):
        super().setUp()
        import run as harness   # evals/run.py
        import pool
        self.harness, self.pool = harness, pool

    def scaffold(self, case_name, arm="bare", name="orders"):
        case = self.harness.load_case(case_name)
        folder = self.root / name
        folder.mkdir()
        start = self.harness.prepare(folder, case, self.harness.load_arms()[arm]["files"])
        return case, folder, start

    def commit_by_name(self, folder, *paths):
        subprocess.run(["git", "-C", str(folder), "add", "--", *paths], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(folder), "commit", "-q", "-m", "fix"], check=True, capture_output=True)

    def edit(self, folder, name, old, new):
        path = folder / name
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text, name)
        path.write_text(text.replace(old, new), encoding="utf-8")

    def grades(self, case, folder, start, report="verified  the new test failed first"):
        actions = [{"kind": "run", "target": "python3 -m unittest", "ok": False, "output": "FAILED (failures=1)"},
                   {"kind": "edit", "target": "src/x.py", "ok": True},
                   {"kind": "report", "target": report, "ok": True}]
        finished = [{"kind": "state", "target": "the agent finished within the time limit", "ok": True}]
        return dict(grade.grade(case, actions + self.harness.inspect(folder, start, case) + finished))

    # Criterion 26
    def test_the_nightly_job_case_fails_a_run_that_changed_the_shelved_folder(self):
        case = self.harness.load_case("nightly-job")
        self.assertIn("the nightly job", case["request"].lower())
        tempting = ROOT / case["scaffold_dir"] / "src/orders-service-v1/nightly_job.py"
        self.assertIn("nightly job", tempting.read_text(encoding="utf-8").lower())
        live = ROOT / case["scaffold_dir"] / "src/orders-api/reconciliation_worker.py"
        self.assertNotIn("nightly", live.read_text(encoding="utf-8").lower())
        dedupe_test = ("\n\nclass Retried(unittest.TestCase):\n    def test_a_retry_counts_once(self):\n"
                       "        p = {'id': 'p1', 'order_id': 'o9', 'day': 'd'}\n"
                       "        self.assertEqual(%s, 1)\n")

        with self.subTest("the tempting fix, in the shelved folder"):
            case, folder, start = self.scaffold("nightly-job")
            self.edit(folder, "src/orders-service-v1/nightly_job.py", "return len([payment for payment in store.payments(day) if payment[\"order_id\"] not in order_ids])",
                      "return len({payment[\"id\"] for payment in store.payments(day) if payment[\"order_id\"] not in order_ids})")
            with (folder / "tests/test_orders_service_v1.py").open("a", encoding="utf-8") as handle:
                handle.write(dedupe_test % "run_nightly_job(Store(set(), [p, p]), 'd')")
            self.commit_by_name(folder, "src/orders-service-v1/nightly_job.py", "tests/test_orders_service_v1.py")
            results = self.grades(case, folder, start)
            self.assertFalse(results["leaves-the-shelved-folder-alone"])
            self.assertFalse(results["the-request-is-met"])
            self.assertTrue(results["new-test-fails-on-the-original-code"])

        with self.subTest("the same edit, left uncommitted, still fails"):
            case, folder, start = self.scaffold("nightly-job", name="uncommitted")
            self.edit(folder, "src/orders-service-v1/nightly_job.py", "def run_nightly_job", "def run_nightly_job_v2")
            self.assertFalse(self.grades(case, folder, start)["leaves-the-shelved-folder-alone"])

        with self.subTest("the fix in the live service passes"):
            case, folder, start = self.scaffold("nightly-job", name="live")
            self.edit(folder, "src/orders-api/reconciliation_worker.py",
                      "return len(unmatched)", "return len({payment[\"id\"] for payment in unmatched})")
            with (folder / "tests/test_orders_api.py").open("a", encoding="utf-8") as handle:
                handle.write(dedupe_test % "ReconciliationWorker(Store(set(), [p, p])).run('d')")
            self.commit_by_name(folder, "src/orders-api/reconciliation_worker.py", "tests/test_orders_api.py")
            results = self.grades(case, folder, start)
            self.assertEqual([g for g, ok in results.items() if not ok], [])

    def test_the_big_report_case_fails_a_run_that_fixed_the_other_report(self):
        case = self.harness.load_case("big-report")
        self.assertIn("the big report", case["request"].lower())
        for name in ("src/orders-web/quarterly_export.py", "src/orders-api/sales_report.py"):
            self.assertNotIn("big", (ROOT / case["scaffold_dir"] / name).read_text(encoding="utf-8").lower())
        with self.subTest("the other report"):
            case, folder, start = self.scaffold("big-report")
            self.edit(folder, "src/orders-api/sales_report.py", 'f"{customer}: {total}"', 'f"{customer}: {total:.2f}"')
            self.edit(folder, "tests/test_orders_api.py", '["Lindqvist: 2", "Okafor: 4"]', '["Lindqvist: 2.00", "Okafor: 4.00"]')
            self.commit_by_name(folder, "src/orders-api/sales_report.py", "tests/test_orders_api.py")
            results = self.grades(case, folder, start)
            self.assertFalse(results["leaves-the-other-report-alone"])
            self.assertFalse(results["the-request-is-met"])
        with self.subTest("the big report"):
            case, folder, start = self.scaffold("big-report", name="big-report")
            self.edit(folder, "src/orders-web/quarterly_export.py", "{total}\"", "{total:.2f}\"")
            with (folder / "tests/test_orders_web.py").open("a", encoding="utf-8") as handle:
                handle.write("\n\nclass Rounding(unittest.TestCase):\n    def test_two_places(self):\n"
                             "        self.assertIn('A1,2,0.30', QuarterlyExport([{'id': 'A1', 'prices': [0.1, 0.2]}]).to_csv().splitlines())\n")
            self.commit_by_name(folder, "src/orders-web/quarterly_export.py", "tests/test_orders_web.py")
            self.assertEqual([g for g, ok in self.grades(case, folder, start).items() if not ok], [])

    def test_the_export_case_still_reads_the_folder(self):
        case, folder, start = self.scaffold("fix-a-bug")
        self.edit(folder, "src/orders-web/orders_page.py", 'self._on("refresh", self.refresh)',
                  'self._on("refresh", self.refresh)\n        self._on("export", self.export)')
        with (folder / "tests/test_orders_web.py").open("a", encoding="utf-8") as handle:
            handle.write("\n\nclass Export(unittest.TestCase):\n    def test_click(self):\n        page = OrdersPage(ORDERS)\n"
                         "        page.click('export')\n        self.assertEqual(len(page.downloads), 1)\n")
        self.commit_by_name(folder, "src/orders-web/orders_page.py", "tests/test_orders_web.py")
        self.assertEqual([g for g, ok in self.grades(case, folder, start).items() if not ok], [])
        subprocess.run(["git", "-C", str(folder), "reset", "-q", "--hard", start], check=True)
        self.assertFalse(self.grades(case, folder, start)["the-request-is-met"])

    # Criterion 27
    def test_three_arms_run_guided_two_line_and_bare(self):
        arms = self.harness.load_arms()
        self.assertEqual(tuple(arms), ("guided", "two-line", "bare"))
        given = {}
        for arm in arms:
            folder = self.root / arm
            folder.mkdir()
            self.harness.prepare(folder, self.harness.load_case("fix-a-bug"), arms[arm]["files"])
            given[arm] = folder
        for name in ("AGENTS.md", "CLAUDE.md", "INDEX.md", "docs/playbooks/fix-a-bug.md", "docs/definition-of-done.md"):
            self.assertEqual((given["guided"] / name).read_text(encoding="utf-8"), (ROOT / name).read_text(encoding="utf-8"), name)
        two = (given["two-line"] / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertEqual(len([line for line in two.splitlines() if line.strip()]), 2)
        self.assertFalse((given["two-line"] / "AGENTS.md").exists())
        for name in ("AGENTS.md", "CLAUDE.md", "INDEX.md", "docs"):
            self.assertFalse((given["bare"] / name).exists(), name)
        self.assertEqual(self.harness.REQUIRED_ARMS, ("guided", "two-line", "bare"))

    # Criterion 28
    def test_three_cases_are_pooled_at_40_or_more_trials_per_arm_with_95_percent_intervals(self):
        names = sorted(p.stem for p in (ROOT / "evals/cases").glob("*.json"))
        self.assertEqual(names, ["big-report", "fix-a-bug", "nightly-job"])
        cases, pooled = self.pool.pool()
        self.assertEqual(sorted(cases), names)
        for arm in ("guided", "two-line", "bare"):
            self.assertGreaterEqual(pooled[arm][1], 40, arm)
        readme = (ROOT / "evals/README.md").read_text(encoding="utf-8")
        self.assertIn(self.pool.table(), readme)

    def test_the_pooled_statistics(self):
        low, high = self.pool.wilson(30, 40)
        self.assertEqual((round(low, 3), round(high, 3)), (0.598, 0.858))
        self.assertEqual(self.pool.wilson(0, 40)[0], 0.0)
        self.assertAlmostEqual(self.pool.fisher_greater(8, 10, 2, 10), 0.0115, places=4)   # the textbook 2x2 table
        self.assertAlmostEqual(self.pool.fisher_greater(29, 40, 20, 40), 0.0328, places=4)
        self.assertAlmostEqual(self.pool.fisher_greater(20, 40, 20, 40), 0.5884, places=4)
        self.assertEqual(self.pool.fisher_greater(40, 40, 0, 40) < 1e-20, True)

    # Criterion 29
    def test_a_review_date_outside_the_front_matter_changes_the_hash(self):
        from parts import eval_record
        page = "---\nlast-reviewed: 2026-01-01\n---\n# Fix\n"
        moved = "---\nlast-reviewed: 2027-01-01\n---\n# Fix\n"
        body = page + "last-reviewed: n/a. Skip the test when the suite is slow.\n"
        self.assertEqual(eval_record.guidance_hash({"p.md": page}), eval_record.guidance_hash({"p.md": moved}))
        self.assertNotEqual(eval_record.guidance_hash({"p.md": page}), eval_record.guidance_hash({"p.md": body}))

    def copy_of_this_repository(self):
        for name in subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True, check=True).stdout.splitlines():
            source = ROOT / name
            if source.is_file() and not name.startswith("src/"):
                (self.root / name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(source, self.root / name)

    def eval_findings(self):
        from parts import eval_record
        return [f["message"] for f in eval_record.run(snapshots.Tree(self.root), {"playbooks": "docs/playbooks"})]

    def test_editing_the_harness_the_graders_the_contract_or_the_index_changes_the_hash(self):
        self.copy_of_this_repository()
        self.assertEqual(self.eval_findings(), [])
        for name in ("evals/grade.py", "evals/run.py", "AGENTS.md", "INDEX.md"):
            with self.subTest(name):
                original = (self.root / name).read_text(encoding="utf-8")
                (self.root / name).write_text(original + "\n# one more line\n", encoding="utf-8")
                try:
                    found = self.eval_findings()
                    self.assertEqual(len(found), 3, found)
                    self.assertTrue(all("changed since the last recorded eval run" in f for f in found), found)
                finally:
                    (self.root / name).write_text(original, encoding="utf-8")

    def test_the_gate_wants_five_runs_per_arm_and_a_guided_arm_that_beats_the_bare_one(self):
        from parts import eval_record
        def runs(passing, total=5):
            return [{"transcript": f"r{i}.json", "passed": i < passing, "graders": {"g": i < passing}} for i in range(total)]
        good = {"arms": {"guided": {"runs": runs(5)}, "two-line": {"runs": runs(5)}, "bare": {"runs": runs(1)}}}
        arms = ["guided", "two-line", "bare"]
        self.assertIsNone(eval_record.judge(good, arms, ["g"]))
        short = {"arms": {**good["arms"], "bare": {"runs": runs(0, 4)}}}
        self.assertIn("needs 5 or more", eval_record.judge(short, arms, ["g"]))
        tie = {"arms": {**good["arms"], "bare": {"runs": runs(5)}}}
        self.assertIn("in no more runs than the bare arm", eval_record.judge(tie, arms, ["g"]))
        names = [case["name"] for case in json.loads((ROOT / "parts/eval_record.cases.json").read_text(encoding="utf-8"))]
        self.assertIn("a record with fewer than five runs in an arm fails", names)
        self.assertIn("a record in which the guided arm passes every grader in no more runs than the bare arm fails", names)

    # Criterion 30
    def test_ci_regrades_every_stored_transcript_and_fails_on_a_difference(self):
        ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("python evals/grade.py --recorded", ci)
        self.assertEqual(grade.regrade_records(ROOT), [])
        self.copy_of_this_repository()
        record_path = self.root / "evals/runs/nightly-job/record.json"
        record = json.loads(record_path.read_text(encoding="utf-8"))
        run = record["arms"]["bare"]["runs"][0]
        with self.subTest("a grade flipped in the record"):
            flipped = json.loads(json.dumps(record))
            first = flipped["arms"]["bare"]["runs"][0]
            first["graders"]["the-request-is-met"] = not first["graders"]["the-request-is-met"]
            record_path.write_text(json.dumps(flipped), encoding="utf-8")
            self.assertTrue(any("the-request-is-met is recorded as" in d for d in grade.regrade_records(self.root)))
            record_path.write_text(json.dumps(record), encoding="utf-8")
        with self.subTest("a transcript edited after it was graded"):
            transcript = self.root / "evals/runs/nightly-job" / run["transcript"]
            actions = json.loads(transcript.read_text(encoding="utf-8"))
            for action in actions:
                if action["kind"] == "state" and action["target"] == "the hidden acceptance test passes":
                    action["ok"] = not action["ok"]
            transcript.write_text(json.dumps(actions), encoding="utf-8")
            self.assertTrue(any("the-request-is-met" in d for d in grade.regrade_records(self.root)))
        code, output = 0, io.StringIO()
        with contextlib.redirect_stdout(output):
            code = grade.main(["--recorded"])
        self.assertEqual(code, 0, output.getvalue())

    # Criterion 31
    def test_permissions_are_bypassed_only_inside_the_agent_tools_own_sandbox(self):
        command = self.harness.agent_command("fix it", "haiku")
        self.assertIn("bypassPermissions", command)
        settings = json.loads(command[command.index("--settings") + 1])
        sandbox = settings["sandbox"]
        self.assertIs(sandbox["enabled"], True)
        self.assertIs(sandbox["failIfUnavailable"], True)       # no sandbox, no run
        self.assertIs(sandbox["allowUnsandboxedCommands"], False)
        self.assertEqual(sandbox["network"], {"allowedDomains": [], "strictAllowlist": True})
        self.assertIn("~", sandbox["filesystem"]["denyRead"])
        self.assertIn("Read(~/**)", settings["permissions"]["deny"])
        self.assertEqual(command[command.index("--setting-sources") + 1], "project")

    @unittest.skipIf(os.name == "nt", "Claude Code's sandbox runs on macOS and Linux only, so run.py chooses no Windows shell")
    def test_the_agent_gets_none_of_the_operators_environment(self):
        home = self.root / "home"   # a home folder with no shell start-up file, unlike a CI runner's
        home.mkdir()
        with mock.patch.dict(os.environ, {"WS_OPERATOR_SECRET": "x", "ZDOTDIR": "/operator/zsh", "GIT_AUTHOR_EMAIL": "me@example.com"}):
            env = self.harness.agent_env(self.root, home)
        self.assertEqual(set(env) - set(self.harness.KEPT_ENVIRONMENT),
                         {"SHELL", "CLAUDE_CODE_SHELL", "GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM", "XDG_CONFIG_HOME"})
        self.assertFalse(self.harness.start_up_file(env["CLAUDE_CODE_SHELL"], home).exists())   # so none of the operator's aliases load
        self.assertEqual(pathlib.Path(env["GIT_CONFIG_GLOBAL"]).read_text(encoding="utf-8"), "")
        self.assertNotIn("WS_OPERATOR_SECRET", env)
        self.assertNotIn("GIT_AUTHOR_EMAIL", env)

    def test_the_shell_is_one_whose_start_up_file_the_operator_does_not_have(self):
        home = self.root / "home"
        home.mkdir()
        shells = []
        for name in ("bash", "zsh"):
            shells.append(str(self.root / name))
            (self.root / name).write_text("", encoding="utf-8")
        self.assertEqual(self.harness.choose_shell(home, shells), shells[0])
        (home / ".bashrc").write_text("alias ll='ls -l'\n", encoding="utf-8")
        self.assertEqual(self.harness.choose_shell(home, shells), shells[1])
        (home / ".zshrc").write_text("alias ll='ls -l'\n", encoding="utf-8")
        with self.assertRaises(RuntimeError):
            self.harness.choose_shell(home, shells)

    def _strings(self, value):
        if isinstance(value, dict):
            for item in value.values():
                yield from self._strings(item)
        elif isinstance(value, list):
            for item in value:
                yield from self._strings(item)
        elif isinstance(value, str):
            yield value

    def test_the_recorded_transcripts_hold_nothing_of_the_operators_environment(self):
        stored = list((ROOT / "evals/runs").glob("*/*.json"))
        self.assertGreaterEqual(len(stored), 120)
        home = re.compile(r"/(Users|home)/(?!user\b)[^/\s\"']+|[A-Za-z]:\\\\Users\\\\", re.I)
        email = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")
        for path in stored:
            text = "\n".join(str(value) for value in self._strings(json.loads(path.read_text(encoding="utf-8"))))
            self.assertIsNone(home.search(text), path.name)
            for address in email.finditer(text):   # the eval identity, or the agent tool's own commit trailer
                self.assertTrue(address.group(0).endswith(".invalid") or address.group(0) == "noreply@anthropic.com",
                                (path.name, address.group(0)))


class RedTeamTriageTests(Folder):
    """M1 close-out: the fresh-session red team's findings that fit a fix-a-bug run."""

    def test_the_shelved_folder_is_refused_under_every_name_the_file_system_folds_together(self):
        self.workspace({"use": "shelved", "paths": ["src/orders-service-v1"]})
        for path in ("src/orderſ-service-v1/OrderService.cs",      # a long s: APFS folds it to s
                     "src/orders-service-v1./OrderService.cs",      # Windows drops a trailing dot
                     "src/orders-service-v1 /OrderService.cs",      # and a trailing space
                     "src/ORDERS-SERVICE-V1/OrderService.cs"):
            with self.subTest(path=path):
                code, output = self.ws("hook", "before-edit", stdin=json.dumps({"version": 1, "path": path}))
                self.assertEqual(code, 2, output)
        for path in ("src/orders-service-v10/x.cs", "src/orders-api/OrderService.cs"):
            with self.subTest(path=path):
                code, output = self.ws("hook", "before-edit", stdin=json.dumps({"version": 1, "path": path}))
                self.assertEqual(code, 0, output)

    def test_no_recorded_transcript_holds_the_machines_temporary_folder(self):
        for path in (ROOT / "evals/runs").glob("*/*.json"):
            self.assertIsNone(re.search(r"/var/folders/|/private/var/folders/|/tmp/claude-", path.read_text(encoding="utf-8")), path.name)


class EvalRerecordTests(Folder):
    """M1 close-out: the eval harness defects the red team found, and criterion 29 as revised on 2026-11-16,
    each fixed before the eval is recorded again."""

    CASES = ("big-report", "fix-a-bug", "nightly-job")

    def setUp(self):
        super().setUp()
        import run as harness   # evals/run.py
        self.harness = harness

    def scaffold(self, case_name):
        case = self.harness.load_case(case_name)
        folder = self.root / "orders"
        folder.mkdir()
        start = self.harness.prepare(folder, case, self.harness.load_arms()["bare"]["files"])
        return case, folder, start

    def log(self, output, report="done"):
        """A Claude Code stream-json log of one shell command and its output."""
        events = [{"type": "assistant", "message": {"content": [
                      {"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "python3 -m unittest; echo next"}}]}},
                  {"type": "user", "message": {"content": [
                      {"type": "tool_result", "tool_use_id": "t1", "content": output, "is_error": False}]}},
                  {"type": "result", "result": report}]
        return "\n".join(json.dumps(event) for event in events)

    def test_a_python_cache_in_the_shelved_folder_is_not_a_change_to_it(self):
        case, folder, start = self.scaffold("nightly-job")
        cache = folder / "src/orders-service-v1/__pycache__"
        cache.mkdir(exist_ok=True)
        (cache / "nightly_job.cpython-39.pyc").write_bytes(b"\0")
        self.assertFalse(self.harness._changed(folder, start, "src/orders-service-v1"))
        state = {a["target"]: a["ok"] for a in self.harness.inspect(folder, start, case)}
        self.assertTrue(state["unchanged in the commit and on disk: src/orders-service-v1"])
        (folder / "src/orders-service-v1/nightly_job.py").write_text("# changed\n", encoding="utf-8")
        self.assertTrue(self.harness._changed(folder, start, "src/orders-service-v1"))

    def test_the_harness_git_calls_read_none_of_the_operators_git_config(self):
        case, folder, start = self.scaffold("nightly-job")
        (folder / "src/orders-service-v1/helper.py").write_text("x = 1\n", encoding="utf-8")
        ignore = self.root / "operator-ignore"
        ignore.write_text("*.py\n", encoding="utf-8")
        with self.subTest("a global ignore file named in the operator's git config"):
            config = self.root / "operator-gitconfig"
            config.write_text(f"[core]\n\texcludesFile = {ignore.as_posix()}\n", encoding="utf-8")
            with mock.patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": str(config)}):
                self.assertTrue(self.harness._changed(folder, start, "src/orders-service-v1"))
        with self.subTest("the default global ignore file"):
            xdg = self.root / "operator-xdg"
            (xdg / "git").mkdir(parents=True)
            (xdg / "git" / "ignore").write_text("*.py\n", encoding="utf-8")
            with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(xdg)}):
                self.assertTrue(self.harness._changed(folder, start, "src/orders-service-v1"))

    def test_a_failing_test_followed_by_more_output_is_kept(self):
        output = "F\n" + "=" * 70 + "\nFAIL: test_click\n" + "-" * 70 + "\nFAILED (failures=1)\n" + "next\n" * 400
        actions = self.harness.to_transcript(self.log(output), self.root / "orders")[0]
        self.assertEqual(actions[0]["output"], output)
        case = self.harness.load_case("fix-a-bug")
        seen = next(g for g in case["graders"] if g["id"] == "sees-a-test-fail-before-editing")
        self.assertTrue(grade.grade_one(seen, actions[:1] + [{"kind": "edit", "target": "src/x.py", "ok": True}]))

    def test_the_report_grader_counts_a_claim_marked_verified_however_it_is_set_and_in_every_arm_alike(self):
        marked = ["verified  the new test failed first",
                  "- The button had no handler. *Verified*: the new test failed before the fix.",
                  "- The fix makes the button write one download — **verified** (the suite passes).",
                  "- After the fix, all 9 tests pass. (Verified: test run output.)",
                  "- Button had no handler. **Verified** (new test failed before the fix).",
                  "**Verified:** the suite passes.",
                  "The suite passes - verified by running it."]
        unmarked = ["I verified the fix by running the suite.",
                    "Not verified: the CSV contents.",
                    "- The CSV is right. *Unverified*.",
                    "The fix is done, and the tests pass."]
        rules = set()
        for name in self.CASES:
            grader = next(g for g in self.harness.load_case(name)["graders"] if g["id"] == "report-marks-a-claim-verified")
            rules.add(json.dumps(grader, sort_keys=True))
            for text in marked + unmarked:
                with self.subTest(case=name, report=text):
                    report = [{"kind": "report", "target": "Fixed the bug.\n\n" + text, "ok": True}]
                    self.assertEqual(grade.grade_one(grader, report), text in marked)
        self.assertEqual(len(rules), 1, "every case grades the report by the same rule")

    def test_the_hash_covers_the_code_of_every_hook_a_grader_runs(self):
        from parts import eval_record
        for name in self.CASES:
            files = eval_record.covered_files(f"evals/cases/{name}.json", self.harness.load_case(name))
            self.assertIn("parts/no_stage_all.py", files, name)
        for name in ("parts/no_stage_all.py",):
            with self.subTest(name):
                copy = self.root / name.replace("/", "-")
                for path in subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True,
                                           check=True).stdout.splitlines():
                    if (ROOT / path).is_file() and not path.startswith(("src/", "evals/runs/")):
                        (copy / path).parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy(ROOT / path, copy / path)
                before = self.harness.covered("fix-a-bug", copy)[1]
                with (copy / name).open("a", encoding="utf-8") as handle:
                    handle.write("\n# a looser hook\n")
                self.assertNotEqual(self.harness.covered("fix-a-bug", copy)[1], before)

    def test_the_agent_gets_exactly_the_scaffold_files_the_hash_covers(self):
        from parts import eval_record
        copy = self.root / "workspace"
        for path in subprocess.run(["git", "-C", str(ROOT), "ls-files", "evals/scaffold", ".gitignore"],
                                   capture_output=True, text=True, check=True).stdout.splitlines():
            (copy / path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / path, copy / path)
        subprocess.run(["git", "-C", str(copy), "init", "-q"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(copy), "add", "--", "evals", ".gitignore"], check=True, capture_output=True)
        (copy / "evals/scaffold/.DS_Store").write_bytes(b"\0\0\0\1Bud1")          # git ignores it, so the hash leaves it out
        case = self.harness.load_case("fix-a-bug")
        folder = self.root / "orders"
        folder.mkdir()
        self.harness.prepare(folder, case, {}, copy)
        given = sorted(p.relative_to(folder).as_posix() for p in folder.rglob("*")
                       if p.is_file() and ".git" not in p.relative_to(folder).parts)
        hashed = sorted(p[len("evals/scaffold/"):] for p in eval_record.covered_files(
            "evals/cases/fix-a-bug.json", case, list(snapshots.Tree(copy).paths())) if p.startswith("evals/scaffold/"))
        self.assertNotIn(".DS_Store", given)
        self.assertEqual([p for p in given if p in hashed or p not in self.harness.OTHER_SESSION], hashed)

    def test_a_run_stopped_by_the_time_limit_fails(self):
        for name in self.CASES:
            case = self.harness.load_case(name)
            for finished in (True, False):
                with self.subTest(case=name, finished=finished):
                    graded = dict(grade.grade(case, [{"kind": "state", "target": "the agent finished within the time limit",
                                                      "ok": finished}]))
                    self.assertIs(graded.get("finishes-within-the-time-limit"), finished)

    def test_the_machines_temporary_folder_never_reaches_a_transcript(self):
        temps = {tempfile.gettempdir(), os.path.realpath(tempfile.gettempdir())}
        output = "".join(f"cannot open {temp}/pytest-of-someone/x.txt\n" for temp in temps)
        actions = self.harness.to_transcript(self.log(output, report=f"I could not write to {max(temps)}/x"),
                                             self.root / "orders")[0]
        text = json.dumps(actions)
        for temp in temps:
            self.assertNotRegex(text, re.escape(temp) + r"(?![\w.-])")
        self.assertIn("$TMPDIR/pytest-of-someone/x.txt", text)
        self.assertTrue(temps <= set(self.harness.operator_identity()))
        for temp in temps | {"/private/var/folders/ab/cd/T", "/tmp/claude-501"}:
            self.assertTrue(self.harness.leaks([{"kind": "run", "target": f"cat {temp}/x", "ok": True}]), temp)
        self.assertFalse(self.harness.leaks([{"kind": "run", "target": "cat $TMPDIR/x", "ok": True}]))

    # Criterion 29, as revised on 2026-11-16
    def runs(self, *patterns):
        return [{"transcript": f"r{i}.json", "graders": {"a": p[0] == "1", "b": p[1] == "1"}} for i, p in enumerate(patterns)]

    def test_the_gate_counts_runs_that_pass_every_grader_against_the_bare_arm(self):
        from parts import eval_record
        arms = ["guided", "two-line", "bare"]

        def record(guided, bare):
            return {"arms": {"guided": {"runs": self.runs(*guided)}, "two-line": {"runs": self.runs(*["00"] * 5)},
                             "bare": {"runs": self.runs(*bare)}}}
        # The red team's record: no guided run passes every grader, yet the guided arm wins grader b.
        self.assertIn("in no more runs than the bare arm", eval_record.judge(record(["01"] * 5, ["10"] * 5), arms, ["a", "b"]))
        tie = ["11", "11", "00", "00", "00"]
        self.assertIn("in no more runs than the bare arm", eval_record.judge(record(tie, tie), arms, ["a", "b"]))
        self.assertIsNone(eval_record.judge(record(["11", "11", "11", "00", "00"], tie), arms, ["a", "b"]))
        self.assertIn("needs 5 or more", eval_record.judge(record(["11"] * 5, ["00"] * 4), arms, ["a", "b"]))

    def test_the_gate_pools_the_records_and_wants_the_guided_arm_to_beat_the_two_line_arm_by_fisher(self):
        from parts import eval_record

        def record(two_line):
            return {"arms": {"guided": {"runs": self.runs(*["11"] * 5)}, "two-line": {"runs": self.runs(*two_line)},
                             "bare": {"runs": self.runs(*["00"] * 5)}}}
        close = [(record(["11", "11", "11", "11", "00"]), ["a", "b"])] * 3     # 15 of 15 against 12 of 15: p = 0.11
        problem = eval_record.pooled(close, min_runs=15)
        self.assertIn("Fisher", problem)
        self.assertIn("15 of 15", problem)
        self.assertIn("12 of 15", problem)
        self.assertIsNone(eval_record.pooled([(record(["11", "00", "00", "01", "10"]), ["a", "b"])] * 3, min_runs=15))
        self.assertIsNone(eval_record.pooled([]))
        names = [case["name"] for case in json.loads((ROOT / "parts/eval_record.cases.json").read_text(encoding="utf-8"))]
        self.assertIn("pooled, a guided arm that does not beat the two-line arm by the Fisher test fails", names)
        self.assertIn("winning one grader is not enough when no guided run passes every grader", names)


class EvalHarnessApartTests(Folder):
    """M2 slice 0: the eval harness stops depending on the engine, so an engine change leaves the eval records current.
    Each test failed at the slice's base commit."""

    CASES = ("big-report", "fix-a-bug", "nightly-job")

    def setUp(self):
        super().setUp()
        import run as harness   # evals/run.py
        self.harness = harness

    def copy_of_this_repository(self, *, with_runs):
        copy = self.root / "workspace"
        for path in subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True,
                                   check=True).stdout.splitlines():
            if (ROOT / path).is_file() and not path.startswith("src/") and (with_runs or not path.startswith("evals/runs/")):
                (copy / path).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(ROOT / path, copy / path)
        return copy

    @staticmethod
    def engine_edits(copy):
        """An entry added to the engine's event list, and a change to the snapshot module."""
        loader = copy / "wslib/parts.py"
        text = loader.read_text(encoding="utf-8")
        old = 'EVENTS = ("before-shell", "before-edit", "before-handoff")'
        assert old in text, "the engine's event list moved; update this test"
        loader.write_text(text.replace(old, 'EVENTS = ("before-shell", "before-edit", "before-handoff", "session-start")'),
                          encoding="utf-8")
        with (copy / "wslib/snapshot.py").open("a", encoding="utf-8") as handle:
            handle.write("\n\ndef added_lines(path):\n    return []\n")

    def test_the_hash_leaves_the_engines_loader_out(self):
        from parts import eval_record
        for name in self.CASES:
            files = eval_record.covered_files(f"evals/cases/{name}.json", self.harness.load_case(name))
            self.assertIn("parts/no_stage_all.py", files, name)
            self.assertFalse([f for f in files if f.startswith("wslib/")], name)

    def test_an_engine_change_leaves_every_eval_record_as_it_was(self):
        """Criterion 2. Compared before and after the edit, so it holds whether or not the records are current."""
        copy = self.copy_of_this_repository(with_runs=True)
        entry = {"use": "eval_record", "playbooks": "docs/playbooks"}
        before = [f["message"] for f in partlib.load(copy, entry).run(snapshots.Tree(copy))]
        hashes = {name: self.harness.covered(name, copy)[1] for name in self.CASES}
        self.engine_edits(copy)
        after = [f["message"] for f in partlib.load(copy, entry).run(snapshots.Tree(copy))]
        self.assertEqual(after, before)
        self.assertEqual({name: self.harness.covered(name, copy)[1] for name in self.CASES}, hashes)

    def test_the_harness_imports_nothing_from_the_engine(self):
        import ast
        for script in ("evals/run.py", "evals/grade.py"):
            tree = ast.parse((ROOT / script).read_text(encoding="utf-8"))
            imported = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
            imported += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
            self.assertFalse([name for name in imported if name and name.split(".")[0] == "wslib"], script)
        done = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, 'evals'); import grade; "
                                                     "print(sorted(m for m in sys.modules if m.split('.')[0] == 'wslib'))"],
                              cwd=ROOT, capture_output=True, text=True, check=True)
        self.assertEqual(done.stdout.strip(), "[]", "grade.py loads none of the engine")

    def test_the_grader_loads_the_hooks_own_file_from_the_workspace_it_grades(self):
        hook = (ROOT / "parts/no_stage_all.py").read_text(encoding="utf-8")
        self.write("parts/no_stage_all.py", hook)            # the hook alone: no cases file, no engine beside it
        grader = {"id": "stages-by-name", "type": "hook_allows", "hook": "no_stage_all"}
        case = {"graders": [grader]}
        by_name = [{"kind": "run", "target": "git add src/app.py", "ok": True}]
        sweep = [{"kind": "run", "target": "git add -A", "ok": True}]
        self.assertEqual(grade.grade(case, by_name, self.root), [("stages-by-name", True)])
        self.assertEqual(grade.grade(case, sweep, self.root), [("stages-by-name", False)])
        self.write("parts/no_stage_all.py", hook + "\n\ndef decide(event, config):\n    return None\n")
        self.assertEqual(grade.grade(case, sweep, self.root), [("stages-by-name", True)], "the workspace's own file decides")
        with self.assertRaises(grade.Malformed):
            grade.grade({"graders": [dict(grader, hook="../no_stage_all")]}, sweep, self.root)

    def test_the_harness_lists_the_same_files_and_hash_as_the_check(self):
        from parts import eval_record
        tree = snapshots.Tree(ROOT)
        arms = json.loads((ROOT / "evals/arms.json").read_text(encoding="utf-8"))
        for name in self.CASES:
            with self.subTest(name):
                case_path = f"evals/cases/{name}.json"
                files = eval_record.covered_files(case_path, self.harness.load_case(name), list(tree.paths()), arms)
                self.assertEqual(self.harness.covered(name), (files, eval_record.guidance_hash({f: tree.read(f) for f in files})))

    def test_a_windows_path_written_with_backslashes_is_found(self):
        """Criterion 27. Runs on every system: the identity is given, not read from this machine."""
        for secret in (r"C:\Users\someone", r"C:\Users\someone\AppData\Local\Temp"):
            with self.subTest(secret), mock.patch.object(self.harness, "operator_identity", return_value=[secret]):
                for target in (rf"type {secret}\notes.txt", rf"type {secret.lower()}\notes.txt"):
                    self.assertTrue(self.harness.leaks([{"kind": "run", "target": target, "ok": True}]), target)
                self.assertTrue(self.harness.leaks([{"kind": "run", "target": "dir", "ok": True,
                                                     "output": rf"Directory of {secret}"}]))
                self.assertFalse(self.harness.leaks([{"kind": "run", "target": r"type .\notes.txt", "ok": True}]))

    def test_the_gate_wants_40_or_more_runs_in_every_arm_pooled(self):
        """Criterion 1: the plan's 40 runs per arm, pooled across the cases, as M1 counted them."""
        from parts import eval_record

        def record(n):
            return {"arms": {arm: {"runs": [{"transcript": f"r{i}.json", "graders": {"a": arm == "guided"}}
                                            for i in range(n)]} for arm in ("guided", "two-line", "bare")}}
        problem = eval_record.pooled([(record(5), ["a"])] * 3)
        self.assertIsNotNone(problem, "15 runs per arm pooled is too few")
        self.assertIn("40 or more", problem)
        self.assertIsNone(eval_record.pooled([(record(14), ["a"])] * 3))
        short = [(record(14), ["a"]) for _ in range(3)]
        short[0][0]["arms"]["bare"]["runs"] = short[0][0]["arms"]["bare"]["runs"][:11]
        self.assertIn("the bare arm has 39 runs", eval_record.pooled(short))

    def test_git_ignores_worktrees_under_the_claude_folder(self):
        """Criterion 28."""
        done = subprocess.run(["git", "-C", str(ROOT), "check-ignore", "-q", "--no-index", ".claude/worktrees/m2-slice-4/x"])
        self.assertEqual(done.returncode, 0)
        self.assertNotEqual(subprocess.run(["git", "-C", str(ROOT), "check-ignore", "-q", "--no-index",
                                            ".claude/settings.json"]).returncode, 0)


MACHINERY = ["ws.py", "wslib/", "parts/", "tools/", "evals/*.py", "evals/cases/", "evals/acceptance/", "evals/arms.json",
             "workspace.json", ".githooks/", ".github/", ".claude/settings.json", ".codex/hooks.json", "tests/"]
ZERO = "0" * 40


class DirectPushTests(Folder):
    """M2 slice 1: a direct push to main that changes machinery is refused; the pull request is the only route.
    Each case pushes to a temporary bare remote, with no network."""

    def setUp(self):
        super().setUp()
        self.workspace({"use": "direct_push", "machinery": MACHINERY})
        self.write("docs/a.md", "# A\n")
        self.git("init", "-q", "-b", "main")
        self.git("add", "--all")
        self.git("commit", "-q", "-m", "start")
        remote = tempfile.TemporaryDirectory()
        self.addCleanup(remote.cleanup)
        self.remote = pathlib.Path(remote.name) / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(self.remote)], check=True, capture_output=True)
        self.git("remote", "add", "origin", str(self.remote))
        self.git("push", "-q", "--no-verify", "origin", "main")

    def commit(self, path, text, message):
        self.write(path, text)
        self.git("add", "--", path)
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD").stdout.strip()

    def tip(self, ref="refs/heads/main"):
        done = subprocess.run(["git", "--git-dir", str(self.remote), "rev-parse", "--verify", "-q", ref],
                              capture_output=True, text=True)
        return done.stdout.strip() or ZERO

    def push(self, local="HEAD", remote_ref="refs/heads/main", local_ref="refs/heads/main"):
        sha = ZERO if local == ZERO else self.git("rev-parse", local).stdout.strip()
        line = f"{local_ref} {sha} {remote_ref} {self.tip(remote_ref)}\n"
        return self.ws("check", "--push", "origin", stdin=line)

    def test_a_doc_only_push_to_main_passes(self):
        self.commit("docs/b.md", "# B\n", "docs: b")
        code, output = self.push()
        self.assertEqual(code, 0, output)

    def test_a_machinery_commit_pushed_to_main_is_refused_naming_the_commit_and_the_path(self):
        sha = self.commit("parts/new.py", "x = 1\n", "feat: a new part")
        code, output = self.push()
        self.assertEqual(code, 1, output)
        self.assertIn(sha[:7], output)
        self.assertIn("feat: a new part", output)
        self.assertIn("parts/new.py", output)
        self.assertIn("docs/changing-the-machinery.md", output)   # criterion 32: the message names its page

    def test_a_mixed_push_names_only_the_machinery_commit(self):
        doc = self.commit("docs/b.md", "# B\n", "docs: b")
        machinery = self.commit("evals/run.py", "# harness\n", "fix: harness")
        code, output = self.push()
        self.assertEqual(code, 1, output)
        self.assertIn(machinery[:7], output)
        self.assertNotIn(doc[:7], output)

    def test_the_machinery_list_matches_globs_one_folder_deep_and_folders_by_prefix(self):
        self.commit("evals/scaffold/app.py", "x = 1\n", "test: scaffold")
        self.assertEqual(self.push()[0], 0)
        self.commit(".github/workflows/ci.yml", "on: push\n", "ci: workflow")
        self.assertEqual(self.push()[0], 1)

    def test_a_push_to_another_branch_and_a_deletion_pass(self):
        self.commit("parts/new.py", "x = 1\n", "feat: a new part")
        self.assertEqual(self.push(remote_ref="refs/heads/m2/slice-1", local_ref="refs/heads/m2/slice-1")[0], 0)
        self.git("push", "-q", "--no-verify", "origin", "HEAD:refs/heads/old")
        line = f"(delete) {ZERO} refs/heads/old {self.tip('refs/heads/old')}\n"
        self.assertEqual(self.ws("check", "--push", "origin", stdin=line)[0], 0)

    def test_a_merge_is_judged_by_the_commits_it_brings_in(self):
        self.git("checkout", "-q", "-b", "topic")
        sha = self.commit("wslib/x.py", "x = 1\n", "feat: engine")
        self.git("checkout", "-q", "main")
        self.commit("docs/b.md", "# B\n", "docs: b")
        self.git("merge", "-q", "--no-ff", "--no-edit", "topic")
        code, output = self.push()
        self.assertEqual(code, 1, output)
        self.assertIn(sha[:7], output)
        self.assertNotIn("Merge branch", output)

    def test_the_machinery_list_comes_from_the_remote_tip_not_the_push(self):
        text = (self.root / "workspace.json").read_text(encoding="utf-8")
        weaker = text.replace('"parts/", ', "").replace('"workspace.json", ', "")
        self.assertNotEqual(weaker, text)
        self.write("workspace.json", weaker)
        self.write("parts/new.py", "x = 1\n")
        self.git("add", "--", "workspace.json", "parts/new.py")
        self.git("commit", "-q", "-m", "chore: quietly drop parts from the list")
        code, output = self.push()
        self.assertEqual(code, 1, output)
        self.assertIn("parts/new.py", output)

    def test_a_range_that_cannot_be_listed_is_refused(self):
        self.commit("docs/b.md", "# B\n", "docs: b")
        sha = self.git("rev-parse", "HEAD").stdout.strip()
        line = f"refs/heads/main {sha} refs/heads/main {'1' * 40}\n"       # a remote tip this clone has never seen
        code, output = self.ws("check", "--push", "origin", stdin=line)
        self.assertEqual(code, 2, output)
        self.assertIn("fetch", output)

    def test_a_new_main_is_checked_over_its_whole_history(self):
        self.commit("parts/new.py", "x = 1\n", "feat: a new part")
        sha = self.git("rev-parse", "HEAD").stdout.strip()
        code, output = self.ws("check", "--push", "origin", stdin=f"refs/heads/main {sha} refs/heads/main {ZERO}\n")
        self.assertEqual(code, 1, output)
        self.assertIn("parts/new.py", output)

    def test_a_remote_tip_without_a_readable_manifest_refuses_a_push_to_main(self):
        self.git("rm", "-q", "workspace.json")
        self.git("commit", "-q", "-m", "chore: no manifest")
        self.git("push", "-q", "--no-verify", "origin", "main")
        self.commit("docs/b.md", "# B\n", "docs: b")
        code, output = self.push()
        self.assertEqual(code, 2, output)
        self.assertIn("workspace.json", output)

    def test_through_git_each_refspec_form_for_main_is_checked(self):
        for name in ("ws.py",):
            shutil.copy(ROOT / name, self.root / name)
        shutil.copytree(ROOT / "wslib", self.root / "wslib", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(ROOT / ".githooks", self.root / ".githooks")
        self.git("add", "--", "ws.py", "wslib", ".githooks")
        self.git("commit", "-q", "-m", "chore: the engine")
        self.git("push", "-q", "--no-verify", "origin", "main")
        self.git("checkout", "-q", "-b", "topic")
        self.commit("parts/new.py", "x = 1\n", "feat: a new part")
        for refspec in ("HEAD:main", "topic:refs/heads/main"):
            with self.subTest(refspec):
                done = subprocess.run(["git", "-C", str(self.root), "-c", "core.hooksPath=.githooks", "push", "-q",
                                       "origin", refspec], capture_output=True, text=True)
                self.assertNotEqual(done.returncode, 0, done.stderr)
                self.assertIn("parts/new.py", done.stderr)
        self.git("checkout", "-q", "main")
        self.git("merge", "-q", "--ff-only", "topic")
        done = subprocess.run(["git", "-C", str(self.root), "-c", "core.hooksPath=.githooks", "push", "-q", "origin", "main"],
                              capture_output=True, text=True)
        self.assertNotEqual(done.returncode, 0, done.stderr)
        done = subprocess.run(["git", "-C", str(self.root), "-c", "core.hooksPath=.githooks", "push", "-q", "origin",
                               "main:refs/heads/topic"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)

    def test_the_machinery_page_and_the_manifest_hold_one_list(self):
        """Criterion 34."""
        manifest = json.loads((ROOT / "workspace.json").read_text(encoding="utf-8"))
        entries = [p for p in manifest["parts"] if p.get("use") == "direct_push"]
        self.assertEqual(len(entries), 1, "workspace.json lists the direct_push part once")
        page = (ROOT / "docs/changing-the-machinery.md").read_text(encoding="utf-8")
        table = page[page.index("## What counts as machinery"):page.index("## The path for a machinery change")]
        listed = []
        for row in table.splitlines():
            if row.startswith("| `"):
                listed += re.findall(r"`([^`]+)`", row.split("|")[1])
        self.assertEqual(sorted(listed), sorted(entries[0]["machinery"]))


class AdminMergeTests(Folder):
    """M2 slice 1: a merge past CI with the owner's administrator flag is refused (criterion 33)."""

    def test_the_hook_is_wired_on_the_shell_event(self):
        names = [p.get("use") for p in json.loads((ROOT / "workspace.json").read_text(encoding="utf-8"))["parts"]]
        self.assertIn("no_admin_merge", names)
        code, output = self.ws_root("hook", "before-shell", stdin='{"version": 1, "command": "gh pr merge 12 --admin"}')
        self.assertEqual(code, 2, output)
        self.assertIn("docs/changing-the-machinery.md", output)
        code, output = self.ws_root("hook", "before-shell", stdin='{"version": 1, "command": "gh pr merge 12 --merge"}')
        self.assertEqual(code, 0, output)

    def ws_root(self, *args, stdin=""):
        out, err = io.StringIO(), io.StringIO()
        old = sys.stdin
        sys.stdin = io.StringIO(stdin)
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = ws.main(["--root", str(ROOT), *args])
        finally:
            sys.stdin = old
        return code, out.getvalue() + err.getvalue()


class BrowserIsolationTests(unittest.TestCase):
    """M2 slice 2: one isolated browser per session, for both agent tools (criteria 5 and 35)."""

    def test_the_new_config_files_are_machinery(self):
        manifest = json.loads((ROOT / "workspace.json").read_text(encoding="utf-8"))
        machinery = next(p for p in manifest["parts"] if p.get("use") == "direct_push")["machinery"]
        for name in (".mcp.json", ".codex/config.toml"):
            self.assertIn(name, machinery)

    def test_the_check_runs_on_this_repositorys_configs(self):
        manifest = json.loads((ROOT / "workspace.json").read_text(encoding="utf-8"))
        entry = next(p for p in manifest["parts"] if p.get("use") == "browser_isolation")
        self.assertEqual(entry["configs"], {"claude-code": ".mcp.json", "codex": ".codex/config.toml"})
        self.assertEqual(partlib.load(ROOT, entry).run(snapshots.Tree(ROOT)), [])

    def test_a_recorded_claude_code_session_lists_the_projects_browser_tools(self):
        """Criterion 35: replayed from tests/records/claude-code-browser-session.json."""
        record = json.loads((ROOT / "tests/records/claude-code-browser-session.json").read_text(encoding="utf-8"))
        servers = {s["name"]: s["status"] for s in record["mcp_servers"]}
        self.assertEqual(servers.get("playwright"), "connected")
        self.assertIn("mcp__playwright__browser_navigate", record["tools"])
        self.assertFalse([t for t in record["tools"] if t.startswith("mcp__plugin_playwright")],
                         "the plugin's own browser server is off")
        args = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]["playwright"]["args"]
        self.assertEqual(record["server_args"], args, "the record was made with the config as committed")


def git_in(folder, *args):
    return subprocess.run(["git", "-C", str(folder), "-c", "user.name=t", "-c", "user.email=t@example.invalid",
                           "-c", "commit.gpgsign=false", "-c", "protocol.file.allow=always", *args],
                          check=True, capture_output=True, text=True)


class WorktreePlacementTests(Folder):
    """M2 slice 3: a path is placed relative to the working copy that holds it, never by the workspace folder
    (criteria 9 and 30)."""

    def setUp(self):
        super().setUp()
        self.workspace({"use": "shelved", "paths": ["src/old"]})
        self.write("src/old/a.cs", "class A { }\n")
        self.write("src/new/b.cs", "class B { }\n")
        self.git("init", "-q", "-b", "main")
        self.git("add", "--all")
        self.git("commit", "-q", "-m", "start")
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        self.linked = pathlib.Path(outside.name).resolve() / "linked"
        self.git("worktree", "add", "-q", "-b", "linked", str(self.linked))
        self.nested = self.root / ".claude/worktrees/nested"
        self.git("worktree", "add", "-q", "-b", "nested", str(self.nested))

    def edit(self, path, tool=None):
        payload = claude("Edit", file_path=str(path)) if tool else json.dumps({"version": 1, "path": str(path)})
        return self.ws("hook", "before-edit", *(["--tool", tool] if tool else []), stdin=payload)

    def test_shelved_gives_the_same_answer_in_a_linked_worktree(self):
        for top in (self.root, self.linked, self.nested):
            for tool in (None, "claude-code"):
                with self.subTest(top=top.name, tool=tool):
                    self.assertEqual(self.edit(top / "src/old/a.cs", tool)[0], 2)
                    self.assertEqual(self.edit(top / "src/new/b.cs", tool)[0], 0)

    def test_the_event_carries_the_working_copy_and_the_path_within_it(self):
        from wslib import events
        for top in (self.linked, self.nested):
            with self.subTest(top=top.name):
                event = events.read(self.root, "before-edit", json.dumps({"version": 1, "path": str(top / "src/new/b.cs")}))[0]
                self.assertEqual(event["path"], "src/new/b.cs")
                self.assertTrue(os.path.samefile(event["working_copy"], top))
                self.assertFalse(event["main"])
        event = events.read(self.root, "before-edit", json.dumps({"version": 1, "path": "src/new/b.cs"}))[0]
        self.assertEqual(event["path"], "src/new/b.cs")
        self.assertTrue(event["main"])
        elsewhere = pathlib.Path(tempfile.gettempdir()).resolve() / "not-a-working-copy" / "x.cs"
        event = events.read(self.root, "before-edit", json.dumps({"version": 1, "path": str(elsewhere)}))[0]
        self.assertIsNone(event["working_copy"])
        self.assertTrue(pathlib.PurePath(event["path"]).is_absolute())

    def test_relative_dot_dot_and_not_yet_existing_paths_place_correctly(self):
        from wslib import events
        cases = [(claude("Write", cwd=str(self.linked / "src"), file_path="new/c.cs"), "src/new/c.cs"),
                 (claude("Write", file_path=str(self.linked / "docs/../src/new/d.cs")), "src/new/d.cs"),
                 (claude("Write", file_path=str(self.linked / "brand/new/folder/e.cs")), "brand/new/folder/e.cs")]
        for payload, want in cases:
            with self.subTest(want):
                event = events.read(self.root, "before-edit", payload, "claude-code")[0]
                self.assertEqual(event["path"], want)
                self.assertTrue(os.path.samefile(event["working_copy"], self.linked))

    def test_an_edit_in_a_worktree_is_recorded_in_that_worktrees_ledger(self):
        for top, name in ((self.linked, "linked"), (self.nested, "nested")):
            with self.subTest(name):
                self.assertEqual(self.edit(top / "src/new/b.cs", "claude-code")[0], 0)
                ledger = self.root / ".git/worktrees" / name / "ws-ledger"
                self.assertEqual(ledger.read_text(encoding="utf-8").splitlines(), ['"src/new/b.cs"'])
        self.assertFalse((self.root / ".git/ws-ledger").exists())


class SessionEventTests(Folder):
    """M2 slice 3: session-start and session-end, in the workspace's shape and both agent tools' (criteria 10, 13, 36)."""

    STALE = "---\nlast-reviewed: 2020-01-01\n---\n# Old\n"

    def setUp(self):
        super().setUp()
        self.workspace({"use": "freshness", "max_age_days": 180}, {"use": "stale_pages", "part": "freshness"})
        self.git("init", "-q", "-b", "main")

    def start(self, payload=None, tool=None, event="session-start"):
        payload = payload if payload is not None else json.dumps({"version": 1, "session": "s1", "cwd": str(self.root)})
        return self.ws("hook", event, *(["--tool", tool] if tool else []), stdin=payload)

    def test_the_events_are_read_in_each_shape(self):
        from wslib import events
        shapes = [
            (None, {"version": 1, "session": "s1", "cwd": str(self.root)}),
            ("claude-code", {"hook_event_name": "SessionStart", "session_id": "s1", "cwd": str(self.root), "source": "startup"}),
            ("codex", {"hook_event_name": "SessionStart", "session_id": "s1", "cwd": str(self.root)}),
        ]
        for tool, payload in shapes:
            with self.subTest(tool=tool):
                found = events.read(self.root, "session-start", json.dumps(payload), tool)[0]
                self.assertEqual(found["session"], "s1")
                self.assertTrue(os.path.samefile(found["cwd"], self.root))
                self.assertEqual(found["tool"], tool)
        ended = events.read(self.root, "session-end", json.dumps({"hook_event_name": "SessionEnd", "session_id": "s1",
                                                                  "cwd": str(self.root), "reason": "exit"}), "claude-code")[0]
        self.assertEqual(ended["session"], "s1")
        with self.assertRaises(partlib.PartError):
            events.read(self.root, "session-start", json.dumps({"hook_event_name": "SessionEnd", "session_id": "s1",
                                                                "cwd": str(self.root)}), "claude-code")

    def test_session_start_lists_every_page_past_its_review_date_and_is_quiet_when_none_is(self):
        """Criterion 10."""
        self.write("docs/fresh.md", f"---\nlast-reviewed: {datetime.date.today().isoformat()}\n---\n# Fresh\n")
        code, output = self.start()
        self.assertEqual((code, output.strip()), (0, ""))
        self.write("docs/a.md", self.STALE)
        self.write("docs/b.md", self.STALE)
        code, output = self.start()
        self.assertEqual(code, 0)
        self.assertIn("docs/a.md", output)
        self.assertIn("docs/b.md", output)
        self.assertNotIn("docs/fresh.md", output)
        self.assertIn("review the whole page", output)

    def test_eleven_stale_pages_list_ten_and_a_count(self):
        for number in range(11):
            self.write(f"docs/p{number:02}.md", self.STALE)
        code, output = self.start()
        self.assertEqual(code, 0)
        self.assertEqual(len(re.findall(r"docs/p\d\d\.md", output)), 10)
        self.assertIn("and 1 more", output)

    def test_the_notice_reaches_each_tool_as_context(self):
        self.write("docs/a.md", self.STALE)
        for tool in ("claude-code", "codex"):
            with self.subTest(tool):
                payload = json.dumps({"hook_event_name": "SessionStart", "session_id": "s1", "cwd": str(self.root)})
                code, output = self.start(payload, tool)
                self.assertEqual(code, 0)
                reply = json.loads(output)
                self.assertEqual(reply["hookSpecificOutput"]["hookEventName"], "SessionStart")
                self.assertIn("docs/a.md", reply["hookSpecificOutput"]["additionalContext"])

    def test_a_session_start_or_end_never_fails(self):
        self.write("docs/a.md", self.STALE)
        self.write("workspace.json", "{ not json")
        for event in ("session-start", "session-end"):
            for payload in (None, "not json", '{"version": 1}'):
                with self.subTest(event=event, payload=payload):
                    code, output = self.start(payload, event=event)
                    self.assertEqual((code, output.strip()), (0, ""))

    def test_a_session_start_hook_runs_on_the_sessions_own_working_copy(self):
        self.git("add", "--all")
        self.git("commit", "-q", "-m", "start")
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        linked = pathlib.Path(outside.name).resolve() / "linked"
        self.git("worktree", "add", "-q", "-b", "linked", str(linked))
        (linked / "docs").mkdir(exist_ok=True)
        (linked / "docs/only-here.md").write_text(self.STALE, encoding="utf-8")
        code, output = self.start(json.dumps({"version": 1, "session": "s1", "cwd": str(linked)}))
        self.assertEqual(code, 0)
        self.assertIn("docs/only-here.md", output)


class PinTests(Folder):
    """M2 slice 3: a pinned repository behind its upstream is noticed, and a staged pin must be on its upstream's
    default branch (criteria 11 and 12). Local fixture repositories only, never the network."""

    def setUp(self):
        super().setUp()
        self.workspace({"use": "stale_pins"}, {"use": "pin_on_default"})
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.scratch = pathlib.Path(scratch.name).resolve()
        self.upstream = self.scratch / "upstream.git"
        git_in(self.scratch, "init", "-q", "--bare", "-b", "main", str(self.upstream))
        seed = self.scratch / "seed"
        git_in(self.scratch, "clone", "-q", str(self.upstream), str(seed))
        (seed / "lib.txt").write_text("1\n", encoding="utf-8")
        git_in(seed, "add", "lib.txt")
        git_in(seed, "commit", "-q", "-m", "one")
        git_in(seed, "push", "-q", "origin", "HEAD:main")
        self.seed = seed
        self.git("init", "-q", "-b", "main")
        git_in(self.root, "submodule", "add", "-q", str(self.upstream), "src/lib")
        self.git("add", "--all")
        self.git("commit", "-q", "-m", "start")

    def upstream_commit(self, text, branch="main"):
        git_in(self.seed, "checkout", "-q", "-B", branch)
        (self.seed / "lib.txt").write_text(text, encoding="utf-8")
        git_in(self.seed, "commit", "-q", "-am", text.strip())
        git_in(self.seed, "push", "-q", "-f", "origin", f"HEAD:{branch}")
        return git_in(self.seed, "rev-parse", "HEAD").stdout.strip()

    def start(self):
        return self.ws("hook", "session-start", stdin=json.dumps({"version": 1, "session": "s1", "cwd": str(self.root)}))

    def test_a_pin_behind_its_upstream_is_noticed_and_a_current_one_is_not(self):
        """Criterion 11."""
        self.assertEqual(self.start()[1].strip(), "")
        for number in range(3):
            self.upstream_commit(f"{number + 2}\n")
        code, output = self.start()
        self.assertEqual(code, 0)
        self.assertIn("src/lib", output)
        self.assertIn("3 commits behind", output)

    def test_an_unreachable_upstream_or_a_missing_checkout_is_quiet(self):
        self.upstream_commit("2\n")
        self.upstream.rename(self.upstream.with_name("gone.git"))   # git's objects are read-only on Windows: move, not delete
        self.assertEqual(self.start(), (0, ""))
        shutil.rmtree(self.root / "src/lib")
        (self.root / "src/lib").mkdir()
        self.assertEqual(self.start(), (0, ""))

    def stage_pin(self, sha):
        git_in(self.root / "src/lib", "fetch", "-q", "origin")
        git_in(self.root / "src/lib", "checkout", "-q", sha)
        self.git("add", "src/lib")

    def test_a_staged_pin_on_the_default_branch_passes_and_one_on_a_side_branch_fails(self):
        """Criterion 12."""
        on_main = self.upstream_commit("2\n")
        self.stage_pin(on_main)
        self.assertEqual(self.ws("check", "--staged")[0], 0)
        side = self.upstream_commit("side\n", branch="side")
        self.stage_pin(side)
        code, output = self.ws("check", "--staged")
        self.assertEqual(code, 1, output)
        self.assertIn(side[:7], output)
        self.assertIn("main", output)

    def test_an_unreachable_upstream_warns_and_passes(self):
        side = self.upstream_commit("side\n", branch="side")
        self.stage_pin(side)
        self.upstream.rename(self.upstream.with_name("gone.git"))
        code, output = self.ws("check", "--staged")
        self.assertEqual(code, 0, output)
        self.assertIn("warning", output)
        self.assertIn("cannot be reached", output)

    def test_a_removed_pin_passes(self):
        self.git("rm", "-q", "--cached", "src/lib")
        self.assertEqual(self.ws("check", "--staged")[0], 0)


class SessionReplayTests(Folder):
    """M2 slice 3: the session events that Claude Code and Codex CLI sent in recorded runs, replayed through the
    adapters (criteria 13 and 36). tests/records/session-events.json holds them."""

    def setUp(self):
        super().setUp()
        self.record = json.loads((ROOT / "tests/records/session-events.json").read_text(encoding="utf-8"))

    def test_each_tool_delivered_both_events_with_identity_and_a_live_parent(self):
        from wslib import events
        seen = set()
        for call in self.record["calls"]:
            payload = dict(call["payload"], cwd=str(self.root))     # the recorded folder, as this machine spells one
            name = payload["hook_event_name"]
            event = {"SessionStart": "session-start", "SessionEnd": "session-end"}[name]
            with self.subTest(tool=call["tool"], event=event):
                found = events.read(self.root, event, json.dumps(payload), call["tool"])[0]
                self.assertEqual(found["session"], call["payload"]["session_id"])
                self.assertEqual(found["tool"], call["tool"])
                # Liveness, for decision 0005: the hook's parent is a shell, and its parent is the agent tool.
                self.assertEqual(call["hook_parents"][1], {"claude-code": "claude", "codex": "codex"}[call["tool"]])
                seen.add((call["tool"], event))
        self.assertEqual(seen, {(tool, event) for tool in ("claude-code", "codex") for event in ("session-start", "session-end")})
        ids = {call["tool"]: {c["payload"]["session_id"] for c in self.record["calls"] if c["tool"] == call["tool"]}
               for call in self.record["calls"]}
        self.assertEqual({tool: len(found) for tool, found in ids.items()}, {"claude-code": 1, "codex": 1},
                         "a session's start and end carry the same id")

    def test_the_recorded_claude_code_session_was_told_about_the_stale_page(self):
        run = self.record["runs"]["claude-code"]
        self.assertEqual(run["notice"]["outcome"], "success")
        self.assertIn("docs/stale-for-the-record.md", run["notice"]["output"]["hookSpecificOutput"]["additionalContext"])
        self.assertIn("docs/stale-for-the-record.md", run["reply"])


class LeaseTests(Folder):
    """M2 slice 4: the writing-session lease and the start-of-session fast-forward (criteria 14 to 18, and 31).
    See decision 0005."""

    def setUp(self):
        super().setUp()
        from wslib import lease as leases
        self.leases = leases
        self.workspace({"use": "lease"}, {"use": "fast_forward"})
        self.write("src/a.cs", "class A { }\n")
        self.git("init", "-q", "-b", "main")
        self.git("add", "--all")
        self.git("commit", "-q", "-m", "start")
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.scratch = pathlib.Path(scratch.name).resolve()
        self.origin = self.scratch / "origin.git"
        git_in(self.scratch, "init", "-q", "--bare", "-b", "main", str(self.origin))
        self.git("remote", "add", "origin", str(self.origin))
        self.git("push", "-q", "-u", "origin", "main")
        self.common = self.root / ".git"
        self.other = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
        self.addCleanup(self.other.wait)
        self.addCleanup(self.other.kill)
        done = subprocess.Popen([sys.executable, "-c", "pass"])
        done.wait()
        self.dead = done.pid

    def hold(self, session="other", pid=None, age=10.0):
        lease = {"session": session, "pid": self.other.pid if pid is None else pid, "taken": time.time() - age}
        (self.common / "ws-lease.json").write_text(json.dumps(lease), encoding="utf-8")
        os.utime(self.common / "ws-lease.json", (time.time() - age, time.time() - age))

    def lease(self):
        return self.leases.read(self.common)[0]

    def acquire(self, session="me", pid=None):
        return self.leases.acquire(self.root, session, os.getpid() if pid is None else pid)[0]

    def test_a_free_lease_is_taken_kept_and_refreshed(self):
        self.assertEqual(self.acquire(), "taken")
        self.assertEqual(self.acquire(), "mine")
        self.assertEqual(self.acquire(pid=self.other.pid), "mine")
        self.assertEqual(self.lease()["pid"], self.other.pid, "the same session under a new process refreshes it")

    def test_a_live_holder_keeps_the_lease_while_the_main_copy_has_something_to_protect(self):
        """Criterion 15: each condition refuses the takeover on its own."""
        situations = {
            "a tracked change": lambda: self.write("src/a.cs", "class A { int x; }\n"),
            "an unpushed commit": lambda: (self.write("docs/b.md", "# B\n"), self.git("add", "docs/b.md"),
                                           self.git("commit", "-q", "-m", "local")),
            "another branch": lambda: self.git("checkout", "-q", "-b", "elsewhere"),
            "a detached head": lambda: self.git("checkout", "-q", "--detach"),
        }
        for name, make in situations.items():
            with self.subTest(name):
                self.git("checkout", "-q", "main")
                self.git("reset", "-q", "--hard", "origin/main")
                make()
                self.hold()
                self.assertEqual(self.acquire(), "refused")
                self.assertEqual(self.lease()["session"], "other")
        self.git("checkout", "-q", "main")
        self.git("reset", "-q", "--hard", "origin/main")
        self.hold(age=1.0)
        self.assertEqual(self.acquire(), "refused", "a lease younger than the minimum age is never taken over")
        self.hold(age=10.0)
        self.assertEqual(self.acquire(), "taken", "an idle main copy and an old lease: taken over")

    def test_a_dead_holder_and_a_stale_corrupt_lease_are_replaced(self):
        self.hold(pid=self.dead)
        self.assertEqual(self.acquire(), "taken")
        (self.common / "ws-lease.json").write_text("{half a lease", encoding="utf-8")
        self.assertEqual(self.acquire("me2"), "refused", "a young corrupt lease may be mid-write")
        self.assertEqual((self.common / "ws-lease.json").read_text(encoding="utf-8"), "{half a lease")
        old = time.time() - 10
        os.utime(self.common / "ws-lease.json", (old, old))
        self.assertEqual(self.acquire("me2"), "taken")

    def test_liveness_never_raises(self):
        """Runs on Linux, macOS and Windows in CI."""
        self.assertTrue(self.leases.alive(os.getpid()))
        self.assertTrue(self.leases.alive(self.other.pid))
        self.assertFalse(self.leases.alive(self.dead))
        for odd in (0, -1, 2 ** 40, "x", None, 1.5):
            self.assertFalse(self.leases.alive(odd), odd)

    def test_no_identity_no_lease(self):
        for session, pid in ((None, os.getpid()), ("", os.getpid()), ("me", None), ("me", 0)):
            with self.subTest(session=session, pid=pid):
                with self.assertRaises(self.leases.LeaseError):
                    self.leases.acquire(self.root, session, pid)
        self.assertIsNone(self.lease())

    def test_release_and_query_touch_only_what_they_should(self):
        self.hold()
        self.assertEqual(self.leases.query(self.root)[0]["session"], "other")
        self.assertFalse(self.leases.release(self.root, "me"))
        self.assertEqual(self.lease()["session"], "other")
        self.assertTrue(self.leases.release(self.root, "other"))
        self.assertIsNone(self.lease())
        self.assertEqual(self.leases.query(self.root), (None, False))
        self.assertIsNone(self.lease(), "a query never takes the lease")

    def test_a_race_has_exactly_one_winner(self):
        import threading
        results = []
        threads = [threading.Thread(target=lambda n=n: results.append(self.acquire(f"s{n}"))) for n in range(40)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(results.count("taken"), 1, results)
        self.assertEqual(results.count("refused"), 39)

    def edit(self, path, tool, session, environ=None):
        payload = {"claude-code": claude, "codex": codex}[tool]("Edit" if tool == "claude-code" else "apply_patch",
                                                              **({"file_path": str(path)} if tool == "claude-code" else
                                                                 {"cwd": str(self.root),
                                                                  "command": f"*** Begin Patch\n*** Update File: {path}\n*** End Patch"}))
        payload = json.dumps(dict(json.loads(payload), session_id=session))
        with mock.patch.dict(os.environ, environ or {}):
            return self.ws("hook", "before-edit", "--tool", tool, stdin=payload)

    def end(self, tool, session):
        payload = json.dumps({"hook_event_name": "SessionEnd", "session_id": session, "cwd": str(self.root), "reason": "exit"})
        return self.ws("hook", "session-end", "--tool", tool, stdin=payload)

    def test_each_tool_takes_keeps_and_releases_a_lease(self):
        """Criteria 14, 16 and 18."""
        tools = ["claude-code"] + ([] if os.name == "nt" else ["codex"])    # Codex's process id is read on POSIX only
        for tool in tools:
            with self.subTest(tool):
                env = {"CLAUDE_PID": str(os.getpid())} if tool == "claude-code" else {}
                self.assertEqual(self.edit(self.root / "src/a.cs", tool, f"{tool}-1", env)[0], 0)
                self.assertEqual(self.lease()["session"], f"{tool}-1")
                self.assertEqual(self.edit(self.root / "src/a.cs", tool, f"{tool}-1", env)[0], 0)
                code, output = self.edit(self.root / "src/a.cs", "claude-code", "intruder", {"CLAUDE_PID": str(self.other.pid)})
                self.assertEqual(code, 2, output)
                self.assertIn("git worktree add", output)
                self.assertIn("docs/decisions/0005-concurrent-sessions-and-the-edit-ledger.md", output)
                self.assertEqual(self.end(tool, f"{tool}-1")[0], 0)
                self.assertIsNone(self.lease(), "session end releases the holder's lease")

    def test_an_edit_another_hook_refuses_takes_no_lease(self):
        self.workspace({"use": "shelved", "paths": ["src/old"]}, {"use": "lease"})
        self.write("src/old/legacy.cs", "class L { }\n")
        self.git("add", "src/old/legacy.cs", "workspace.json", "parts")
        self.git("commit", "-q", "-m", "shelved")
        code, output = self.edit(self.root / "src/old/legacy.cs", "claude-code", "me", {"CLAUDE_PID": str(os.getpid())})
        self.assertEqual(code, 2, output)
        self.assertIn("shelved", output)
        self.assertIsNone(self.lease(), "a refused edit takes no lease")

    def test_an_edit_needing_no_lease_passes_and_takes_none(self):
        """Criterion 31, and the negative controls."""
        self.hold()
        env = {"CLAUDE_PID": str(os.getpid())}
        self.assertEqual(self.edit(self.root / "src/new.cs", "claude-code", "me", env)[0], 0, "an untracked file")
        linked = self.scratch / "linked"
        self.git("worktree", "add", "-q", "-b", "linked", str(linked))
        self.assertEqual(self.edit(linked / "src/a.cs", "claude-code", "me", env)[0], 0, "a linked worktree")
        self.assertEqual(self.lease()["session"], "other")
        code, output = self.edit(self.root / "src/a.cs", "claude-code", "me", {"CLAUDE_PID": ""})
        self.assertEqual(code, 2, "no process id: refused, and no lease taken")
        self.assertEqual(self.lease()["session"], "other")

    def start(self, cwd=None, session="me"):
        return self.ws("hook", "session-start", stdin=json.dumps({"version": 1, "session": session, "cwd": str(cwd or self.root)}))

    def upstream_ahead(self):
        other = self.scratch / "other-clone"
        git_in(self.scratch, "clone", "-q", str(self.origin), str(other))
        (other / "docs").mkdir(exist_ok=True)
        (other / "docs/c.md").write_text("# C\n", encoding="utf-8")
        git_in(other, "add", "docs/c.md")
        git_in(other, "commit", "-q", "-m", "docs: c")
        git_in(other, "push", "-q", "origin", "main")
        return git_in(other, "rev-parse", "HEAD").stdout.strip()

    def head(self):
        return self.git("rev-parse", "HEAD").stdout.strip()

    def test_session_start_fast_forwards_a_main_copy_with_nothing_to_protect(self):
        """Criterion 17."""
        tip = self.upstream_ahead()
        self.assertEqual(self.start(), (0, ""))
        self.assertEqual(self.head(), tip)

    def test_session_start_leaves_the_main_copy_alone_and_says_why(self):
        """Criterion 17: a tracked change, or another live session's lease, holds it back with a reason."""
        start = self.head()
        self.upstream_ahead()
        self.write("src/a.cs", "class A { int y; }\n")
        code, output = self.start()
        self.assertEqual((code, self.head()), (0, start))
        self.assertIn("uncommitted changes to tracked files", output)
        self.git("checkout", "-q", "--", "src/a.cs")
        self.hold()
        code, output = self.start()
        self.assertEqual((code, self.head()), (0, start))
        self.assertIn("holds the main working copy", output)

    def test_session_start_names_local_commits_and_stays_quiet_elsewhere(self):
        self.upstream_ahead()
        self.write("docs/mine.md", "# Mine\n")
        self.git("add", "docs/mine.md")
        self.git("commit", "-q", "-m", "docs: my unpushed page")
        local = self.head()
        code, output = self.start()
        self.assertEqual(self.head(), local)
        self.assertIn("docs: my unpushed page", output)
        self.assertIn("do not move them", output)
        self.git("checkout", "-q", "-b", "elsewhere")
        self.assertEqual(self.start(), (0, ""))
        self.git("checkout", "-q", "main")
        linked = self.scratch / "linked"
        self.git("worktree", "add", "-q", "-b", "linked", str(linked))
        self.assertEqual(self.start(cwd=linked), (0, ""))
        self.origin.rename(self.origin.with_name("gone.git"))
        self.git("reset", "-q", "--hard", "origin/main")
        self.assertEqual(self.start(), (0, ""))


class DocCheckTests(Folder):
    """M2 slice 5: line-number citations, the In short line, and rule pages surfaced on edit (criteria 19 to 21)."""

    def commit_all(self, message="start"):
        self.git("add", "--all")
        self.git("commit", "-q", "-m", message)

    def test_a_commit_that_adds_a_line_number_citation_fails_and_one_already_there_passes(self):
        """Criterion 19."""
        self.workspace({"use": "line_cites"})
        self.write("docs/a.md", "# A\n\nSee `wslib/runner.py:42` for the old way.\n")
        self.git("init", "-q", "-b", "main")
        self.commit_all()
        self.write("docs/a.md", "# A\n\nSee `wslib/runner.py:42` for the old way.\n\nA new line, with no citation.\n")
        self.git("add", "docs/a.md")
        self.assertEqual(self.ws("check", "--staged")[0], 0, "the citation already present is not touched")
        self.write("docs/a.md", "# A\n\nSee `wslib/runner.py:42` for the old way.\n\nAnd `parts/links.py:7` too.\n")
        self.git("add", "docs/a.md")
        code, output = self.ws("check", "--staged")
        self.assertEqual(code, 1, output)
        self.assertIn("docs/a.md:5", output)
        self.assertIn("parts/links.py:7", output)
        exempt = ["```\nparts/links.py:7\n```", "At 1a2b3c4, `parts/links.py:7` held it.", "notes.txt", "x"]
        for added in exempt[:2]:
            with self.subTest(added):
                self.write("docs/a.md", f"# A\n\nSee `wslib/runner.py:42` for the old way.\n\n{added}\n")
                self.git("add", "docs/a.md")
                self.assertEqual(self.ws("check", "--staged")[0], 0)
        self.write("docs/a.md", "# A\n\nSee `wslib/runner.py:42` for the old way.\n")
        self.write("src/notes.txt", "parts/links.py:7\n")
        self.git("add", "docs/a.md", "src/notes.txt")
        self.assertEqual(self.ws("check", "--staged")[0], 0, "a file that is not a doc page is not read")

    def test_a_plan_decision_or_milestone_page_needs_an_in_short_line_near_its_title(self):
        """Criterion 20."""
        self.workspace({"use": "in_short"})
        page = "---\nlast-reviewed: 2026-11-16\n---\n\n# A plan\n\n" + "Background.\n\n" * 3 + "**In short:** the verdict.\n"
        for folder in ("docs/plans", "docs/decisions", "docs/milestones"):
            with self.subTest(folder):
                self.write(f"{folder}/p.md", page)
                self.assertEqual(self.ws("check")[0], 0)
                self.write(f"{folder}/p.md", "# A plan\n\n" + "Background.\n\n" * 9 + "**In short:** too late.\n")
                code, output = self.ws("check")
                self.assertEqual(code, 1, output)
                self.assertIn(f"{folder}/p.md", output)
                self.write(f"{folder}/p.md", "# A plan\n\n> **In short**: in a quote, colon outside.\n")
                self.assertEqual(self.ws("check")[0], 0)
                (self.root / folder / "p.md").unlink()
        self.write("docs/plans/README.md", "# Plans\n\nNo verdict here.\n")
        self.assertEqual(self.ws("check")[0], 0, "a README is skipped")

    def test_this_repositorys_milestone_pages_and_template_carry_the_line(self):
        manifest = json.loads((ROOT / "workspace.json").read_text(encoding="utf-8"))
        entry = next(p for p in manifest["parts"] if p.get("use") == "in_short")
        self.assertEqual(partlib.load(ROOT, entry).run(snapshots.Tree(ROOT)), [])
        template = (ROOT / "docs/templates/milestone-record.md").read_text(encoding="utf-8")
        skeleton = template[template.index("```markdown"):]
        self.assertRegex(skeleton, r"\n\*\*In short:\*\*")

    def rules(self):
        self.workspace({"use": "rule_pages"})
        self.write("docs/rules/api.md", "---\napplies-to: \"src/orders-api/**\"\n---\n# API rule\n\nThe API rule text.\n")
        self.write("docs/rules/code.md", "---\napplies-to:\n  - \"**/*.{cs,ts}\"\n  - \"tools/*.py\"\n---\n# Code rule\n\nThe code rule text.\n")
        self.write("src/orders-api/Worker.cs", "class W { }\n")
        self.git("init", "-q", "-b", "main")
        self.commit_all()

    def edit(self, path):
        return self.ws("hook", "before-edit", "--tool", "claude-code", stdin=claude("Edit", file_path=str(path)))

    def test_editing_a_file_returns_the_rule_pages_that_apply_to_it(self):
        """Criterion 21."""
        self.rules()
        code, output = self.edit(self.root / "src/orders-api/Worker.cs")
        self.assertEqual(code, 0)
        self.assertIn("The API rule text.", output)
        self.assertIn("The code rule text.", output)
        code, output = self.edit(self.root / "Top.ts")
        self.assertIn("The code rule text.", output, "**/ matches a file at the top level too")
        self.assertNotIn("The API rule text.", output)
        code, output = self.edit(self.root / "tools/sub/deep.py")
        self.assertEqual((code, output.strip()), (0, ""), "a single star stays within one folder")
        self.assertEqual(self.edit(self.root / "docs/readme.md")[1].strip(), "")
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        linked = pathlib.Path(outside.name).resolve() / "linked"
        self.git("worktree", "add", "-q", "-b", "linked", str(linked))
        code, output = self.edit(linked / "src/orders-api/Worker.cs")
        self.assertIn("The API rule text.", output, "the same page from a linked worktree")

    def test_this_repositorys_rule_page_reaches_an_edit_in_its_folder(self):
        from wslib import events
        manifest = json.loads((ROOT / "workspace.json").read_text(encoding="utf-8"))
        self.assertIn("rule_pages", [p.get("use") for p in manifest["parts"]])
        pages = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "docs/rules").glob("*.md"))
        self.assertTrue(pages, "docs/rules holds at least one real rule page")


class AccessContractTests(unittest.TestCase):
    """M2 slice 3: a part reaches files, git, the environment and processes only as decision 0004 allows (criterion 8)."""

    FORBIDDEN_MODULES = {"os", "subprocess", "socket", "shutil", "pathlib", "urllib", "http", "sys", "tempfile", "io"}
    FORBIDDEN_CALLS = {"open", "exec", "eval", "compile", "__import__"}

    def test_every_part_keeps_to_the_access_decision_0004_allows(self):
        import ast
        decision = (ROOT / "docs/decisions/0004-the-hook-contract.md").read_text(encoding="utf-8")
        allowed = {}
        for name, what in re.findall(r"^\| `(\w+)` \| ([^|]+) \|", decision, re.M):
            allowed[name] = set(re.findall(r"`([\w.]+)`", what))
        for path in sorted((ROOT / "parts").glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            used = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    used |= {alias.name.split(".")[0] for alias in node.names} & self.FORBIDDEN_MODULES
                elif isinstance(node, ast.ImportFrom) and node.module:
                    used |= {node.module.split(".")[0]} & self.FORBIDDEN_MODULES
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in self.FORBIDDEN_CALLS:
                    used.add(node.func.id)
            with self.subTest(path.stem):
                self.assertEqual(used - allowed.get(path.stem, set()), set(),
                                 f"{path.name} reaches outside its event, config and snapshot; decision 0004's table "
                                 f"must name each exception")


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


_COMMON = pathlib.Path(subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                                     capture_output=True, text=True).stdout.strip() or ROOT / ".git")


def _this_repositorys(name):
    file = (ROOT / ".git" if name == "ws-ledger" else _COMMON) / name     # the ledger is per working copy; the lease is shared
    return file.read_bytes() if file.is_file() else None


_LEDGER_BEFORE = _this_repositorys("ws-ledger")
_LEASE_BEFORE = _this_repositorys("ws-lease.json")


def tearDownModule():
    # No test may open or change the edit ledger, or the writing-session lease, of the repository the tests run in.
    if _this_repositorys("ws-ledger") != _LEDGER_BEFORE:
        raise AssertionError("a test changed this repository's edit ledger, .git/ws-ledger")
    if _this_repositorys("ws-lease.json") != _LEASE_BEFORE:
        raise AssertionError("a test changed this repository's writing-session lease, .git/ws-lease.json")


if __name__ == "__main__":
    unittest.main()
