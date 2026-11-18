"""M3 slice C1: a baseline of tolerated findings per check, so an adopting team fails only on new findings.

Criterion 30 of docs/plans/m3-reading-layer-machinery-and-kit.md: with a baseline of N findings for a check, those N
pass, and a new finding fails even when another was fixed, at the commit and in CI alike.

Run: python3 -m unittest discover -b tests
"""
import json
import pathlib
import unittest

from test_core import ROOT, Folder

BROKEN = "# A\n\n[one](gone-1.md)\n\n[two](gone-2.md)\n"


class BaselineTests(Folder):

    def setUp(self):
        super().setUp()
        self.workspace({"use": "links"})
        self.write("a.md", BROKEN)
        self.git("init", "-q")
        self.git("add", "--", "workspace.json", "parts/links.py", "parts/links.cases.json", "a.md")
        self.git("commit", "-q", "--no-verify", "-m", "base")
        self.base = self.git("rev-parse", "HEAD").stdout.strip()

    def baseline(self):
        return json.loads((self.root / "baselines/links.json").read_text(encoding="utf-8"))

    def fix_one_break_another(self):
        self.write("a.md", "# A\n\n[one](gone-1.md)\n\n[three](gone-3.md)\n")

    def commit(self, *paths):
        self.git("add", "--", *paths)
        self.git("commit", "-q", "--no-verify", "-m", "change")

    def test_with_no_baseline_every_finding_fails(self):
        code, output = self.ws("check")
        self.assertEqual(code, 1, output)
        self.assertIn("gone-1.md", output)
        self.assertIn("gone-2.md", output)

    def test_the_baseline_command_records_fingerprints_and_the_folder_check_then_passes(self):
        code, output = self.ws("baseline")
        self.assertEqual(code, 0, output)
        self.assertIn("baselines/links.json", output)
        tolerated = self.baseline()["tolerated"]
        self.assertEqual(len(tolerated), 2)
        self.assertTrue(all(len(entry["fingerprint"]) == 16 for entry in tolerated))
        code, output = self.ws("check")
        self.assertEqual(code, 0, output)
        self.assertIn("2 finding(s) tolerated by baselines/links.json", output)
        self.assertFalse((self.root / "baselines/aliases.json").exists(), "a check with no findings gets no file")

    def test_a_new_finding_fails_even_when_a_tolerated_one_was_fixed(self):
        self.ws("baseline")
        self.fix_one_break_another()
        code, output = self.ws("check")
        self.assertEqual(code, 1, output)
        self.assertIn("gone-3.md", output)
        self.assertNotIn("gone-1.md", output.split("tolerated")[0])

    def test_a_moved_line_keeps_its_finding_tolerated(self):
        self.ws("baseline")
        self.write("a.md", "# A\n\nMore text first.\n\n" + BROKEN.split("\n", 2)[2])
        self.assertEqual(self.ws("check")[0], 0)

    def test_one_entry_tolerates_one_finding_not_every_copy_of_it(self):
        self.ws("baseline")
        self.write("a.md", BROKEN + "\n[one again](gone-1.md)\n")
        code, output = self.ws("check")
        self.assertEqual(code, 1, output)
        self.assertIn("gone-1.md", output)

    def test_at_the_commit_the_staged_baseline_decides(self):
        self.ws("baseline")
        self.commit("baselines/links.json")
        self.assertEqual(self.ws("check", "--staged")[0], 0)
        self.fix_one_break_another()
        self.commit("a.md")
        code, output = self.ws("check", "--staged")
        self.assertEqual(code, 1, output)
        self.assertIn("gone-3.md", output)
        # A baseline written in the folder but not staged does not count at the commit.
        self.ws("baseline")
        self.assertEqual(self.ws("check")[0], 0)
        self.assertEqual(self.ws("check", "--staged")[0], 1)

    def test_in_ci_the_same_baseline_decides_the_same_way(self):
        self.ws("baseline")
        self.commit("baselines/links.json")
        self.write("a.md", BROKEN + "\nA line edited in this push.\n")
        self.commit("a.md")
        code, output = self.ws("check", "--phase", "ci", "--changed-from", self.base)
        self.assertEqual(code, 0, output)
        self.fix_one_break_another()
        self.commit("a.md")
        code, output = self.ws("check", "--phase", "ci", "--changed-from", self.base)
        self.assertEqual(code, 1, output)
        self.assertIn("gone-3.md", output)

    def test_a_baseline_that_cannot_be_read_tolerates_nothing_and_says_so(self):
        for text in ("not json", "[]", '{"tolerated": [{"fingerprint": "short"}]}', '{"tolerated": {}}'):
            with self.subTest(text=text):
                self.write("baselines/links.json", text)
                code, output = self.ws("check")
                self.assertEqual(code, 1, output)
                self.assertIn("baselines/links.json", output)
                self.assertIn("gone-1.md", output)

    def test_an_empty_baseline_tolerates_nothing(self):
        self.write("baselines/links.json", '{"tolerated": []}\n')
        self.assertEqual(self.ws("check")[0], 1)

    def test_warnings_are_not_recorded(self):
        from wslib import baseline as baselines
        found = [{"path": "a.md", "line": 1, "message": "m", "level": "warning"}]
        self.assertEqual(baselines.record("links", found)["tolerated"], [])


class ThisRepositoryTests(unittest.TestCase):

    def test_this_repository_tolerates_no_finding(self):
        folder = ROOT / "baselines"
        for path in sorted(folder.glob("*.json")) if folder.is_dir() else ():
            with self.subTest(path=path.name):
                self.assertEqual(json.loads(path.read_text(encoding="utf-8")).get("tolerated"), [])

    def test_the_baselines_are_machinery(self):
        manifest = json.loads((ROOT / "workspace.json").read_text(encoding="utf-8"))
        machinery = next(p for p in manifest["parts"] if p.get("use") == "direct_push")["machinery"]
        self.assertIn("baselines/", machinery)


if __name__ == "__main__":
    unittest.main()
