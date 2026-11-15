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
        self.assertEqual(part.failed_cases(), ["should find it: missing ['something'], unexpected []"])

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

    def test_hooks_refuse_with_exit_2_and_a_reason(self):
        self.workspace({"use": "no_stage_all"}, {"use": "shelved", "paths": ["src/old"]})
        code, output = self.ws("hook", "before-shell", stdin='{"command": "git add -A"}')
        self.assertEqual(code, 2)
        self.assertIn("Refused by no_stage_all", output)
        self.assertEqual(self.ws("hook", "before-shell", stdin='{"command": "git add a.md"}')[0], 0)
        self.assertEqual(self.ws("hook", "before-edit", stdin='{"path": "src/old/x.cs"}')[0], 2)
        self.assertEqual(self.ws("hook", "before-edit", stdin='{"path": "src/new/x.cs"}')[0], 0)

    def test_hooks_read_an_agent_tool_payload_with_an_absolute_path(self):
        self.workspace({"use": "shelved", "paths": ["src/old"]})
        payload = json.dumps({"tool_name": "Edit", "tool_input": {"file_path": str(self.root / "src/old/x.cs")}})
        self.assertEqual(self.ws("hook", "before-edit", stdin=payload)[0], 2)
        payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git commit -am x"}})
        self.workspace({"use": "no_stage_all"})
        self.assertEqual(self.ws("hook", "before-shell", stdin=payload)[0], 2)

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
        self.assertEqual(self.ws("hook", "before-banana", stdin='{"command": "ls"}')[0], 2)
        source = (ROOT / "parts/no_stage_all.py").read_text(encoding="utf-8").replace('EVENT = "before-shell"', 'EVENT = "before-shel"')
        self.write("parts/no_stage_all.py", source)
        code, output = self.ws("hook", "before-shell", stdin='{"command": "ls"}')
        self.assertEqual(code, 2)
        self.assertIn("EVENT must be one of", output)

    def test_a_hook_that_cannot_decide_fails_closed(self):
        self.workspace({"use": "shelved", "paths": ["src/old"]})
        self.assertEqual(self.ws("hook", "before-edit", stdin='{"path": 5}')[0], 2)
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
            # Refused either way: by the part itself, or (until manifest settings stop leaking into cases) at load.
            self.assertNotEqual(code, 0, setting)
            self.assertRegex(out, "only its cases may|refused", setting)


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


if __name__ == "__main__":
    unittest.main()
