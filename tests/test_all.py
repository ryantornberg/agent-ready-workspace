"""Tests for the checker, the symbol lookup and the eval grader. Run: python3 -m unittest discover -b tests"""
import datetime
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
for folder in ("checks", "tools", "evals"):
    sys.path.insert(0, str(ROOT / folder))

import check_docs  # noqa: E402
import grade  # noqa: E402
import symbols  # noqa: E402

TODAY = datetime.date(2026, 6, 30)


class Workspace(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path


class LinkTests(Workspace):
    def errors(self, **kwargs):
        return check_docs.check(self.root, today=TODAY, **kwargs)[0]

    def test_good_links_pass(self):
        self.write("a.md", "# A\n\nSee [b](docs/b.md), [its part](docs/b.md#second-part) and [here](#a).\n")
        self.write("docs/b.md", "# B\n\n## Second part\n\nBack to [a](../a.md).\n")
        self.assertEqual(self.errors(), [])

    def test_missing_file_fails_with_its_line(self):
        self.write("a.md", "# A\n\n[gone](docs/gone.md)\n")
        self.assertEqual(self.errors(), ["a.md:3: link to missing file: docs/gone.md"])

    def test_missing_heading_fails(self):
        self.write("a.md", "[x](b.md#no-such-heading)\n")
        self.write("b.md", "# B\n")
        self.assertEqual(self.errors(), ["a.md:1: no heading for #no-such-heading in b.md"])

    def test_external_links_code_and_images_are_ignored(self):
        self.write("a.md", "[site](https://example.com) [mail](mailto:a@example.com) `[x](nope.md)`\n\n"
                           "```\n[y](nope.md)\n```\n")
        self.assertEqual(self.errors(), [])

    def test_repeated_headings_get_numbered_anchors(self):
        self.write("a.md", "[one](b.md#notes) [two](b.md#notes-1) [three](b.md#notes-2)\n")
        self.write("b.md", "## Notes\n\n## Notes\n")
        self.assertEqual(self.errors(), ["a.md:1: no heading for #notes-2 in b.md"])

    def test_heading_punctuation_is_dropped_from_the_anchor(self):
        self.write("a.md", "[x](#whats-done-and-whats-next)\n\n## What's done, and what's next?\n")
        self.assertEqual(self.errors(), [])

    def test_archive_is_skipped(self):
        self.write("archive/old.md", "[gone](nope.md)\n")
        self.assertEqual(self.errors(), [])


class FreshnessTests(Workspace):
    STALE = "---\nlast-reviewed: 2025-01-01\n---\n# Old\n"

    def test_stale_page_is_a_warning(self):
        self.write("old.md", self.STALE)
        errors, warnings = check_docs.check(self.root, today=TODAY)
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1)

    def test_stale_page_is_an_error_when_the_commit_edits_it(self):
        self.write("old.md", self.STALE)
        errors, warnings = check_docs.check(self.root, changed=["old.md"], today=TODAY)
        self.assertEqual(len(errors), 1)
        self.assertEqual(warnings, [])

    def test_fresh_and_undated_pages_pass(self):
        self.write("new.md", "---\nlast-reviewed: 2026-06-01\n---\n# New\n")
        self.write("plain.md", "# No front matter\n")
        self.assertEqual(check_docs.check(self.root, changed=["new.md", "plain.md"], today=TODAY), ([], []))

    def test_exit_code(self):
        self.write("old.md", self.STALE)
        base = ["--root", str(self.root), "--today", "2026-06-30"]
        self.assertEqual(check_docs.main(base), 0)
        self.assertEqual(check_docs.main(base + ["--changed", "old.md"]), 1)


class SymbolTests(Workspace):
    def setUp(self):
        super().setUp()
        self.write("app/export.py", "class OrderExporter:\n    def run(self):\n        pass\n\nasync def export_all():\n    pass\n")
        self.write("api/OrdersController.cs",
                   "namespace Shop;\n\npublic sealed class OrdersController\n{\n"
                   "    public async Task<IActionResult> ExportOrders(int id)\n    {\n        return Ok();\n    }\n}\n")
        self.write("ui/orders.ts",
                   "export interface OrderRow { id: number }\nexport const exportOrders = async () => {};\n"
                   "export function renderOrders() {}\nclass OrderTable {}\n")
        self.write("node_modules/lib/index.js", "function exportOrders() {}\n")

    def names(self, name, **kwargs):
        return [(pathlib.Path(p).relative_to(self.root).as_posix(), line, kind)
                for p, line, kind, _ in symbols.find(name, self.root, **kwargs)]

    def test_python_class_method_and_async_function(self):
        self.assertEqual(self.names("OrderExporter"), [("app/export.py", 1, "class")])
        self.assertEqual(self.names("run"), [("app/export.py", 2, "function")])
        self.assertEqual(self.names("export_all"), [("app/export.py", 5, "function")])

    def test_csharp_type_and_method(self):
        self.assertEqual(self.names("OrdersController"), [("api/OrdersController.cs", 3, "type")])
        self.assertEqual(self.names("ExportOrders"), [("api/OrdersController.cs", 5, "method")])

    def test_typescript_declarations(self):
        self.assertEqual(self.names("OrderRow"), [("ui/orders.ts", 1, "type")])
        self.assertEqual(self.names("exportOrders"), [("ui/orders.ts", 2, "const")])
        self.assertEqual(self.names("renderOrders"), [("ui/orders.ts", 3, "function")])
        self.assertEqual(self.names("OrderTable"), [("ui/orders.ts", 4, "class")])

    def test_contains_ignores_case_and_skips_vendored_code(self):
        found = {(path, line) for path, line, _ in self.names("exportorders", contains=True)}
        self.assertEqual(found, {("api/OrdersController.cs", 5), ("ui/orders.ts", 2)})

    def test_exit_code(self):
        self.assertEqual(symbols.main(["OrderExporter", str(self.root)]), 0)
        self.assertEqual(symbols.main(["NoSuchName", str(self.root)]), 1)


class GradeTests(unittest.TestCase):
    def setUp(self):
        self.case = json.loads((ROOT / "evals/cases/fix-a-bug.json").read_text(encoding="utf-8"))

    def run_transcript(self, name):
        actions = json.loads((ROOT / "evals/transcripts" / name).read_text(encoding="utf-8"))
        return dict(grade.grade(self.case, actions))

    def test_the_playbook_run_passes_every_grader(self):
        self.assertTrue(all(self.run_transcript("fix-a-bug.pass.json").values()))

    def test_the_bare_run_fails_every_grader(self):
        self.assertFalse(any(self.run_transcript("fix-a-bug.fail.json").values()))

    def test_before_needs_the_first_action_ahead_of_the_second(self):
        grader = {"type": "before", "first": {"kind": "run"}, "then": {"kind": "edit"}}
        run, edit = {"kind": "run", "target": "t"}, {"kind": "edit", "target": "f"}
        self.assertTrue(grade.grade_one(grader, [run, edit]))
        self.assertFalse(grade.grade_one(grader, [edit, run]))
        self.assertFalse(grade.grade_one(grader, [run]))

    def test_exit_code(self):
        case = str(ROOT / "evals/cases/fix-a-bug.json")
        self.assertEqual(grade.main([case, str(ROOT / "evals/transcripts/fix-a-bug.pass.json")]), 0)
        self.assertEqual(grade.main([case, str(ROOT / "evals/transcripts/fix-a-bug.fail.json")]), 1)


class RepositoryTests(unittest.TestCase):
    def test_this_repository_passes_its_own_check(self):
        self.assertEqual(check_docs.check(ROOT)[0], [])


if __name__ == "__main__":
    unittest.main()
