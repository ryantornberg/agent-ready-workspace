"""Criterion 47, and the kit's classes: `ws.py adopt`, `ws.py drift`, `ws.py upgrade` and the kit manifest.

An instance is made from this repository's working copy into a temporary folder, and its own ws.py runs there, as a
team would run it. The upgrade tests make a small newer kit from a copy of this repository, so nothing here changes
this working copy. Decision record 0007 says what each class means.

Run: python3 -m unittest tests.test_kit -b
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from wslib import VERSION  # noqa: E402
from wslib import kit  # noqa: E402
from wslib import kitlock  # noqa: E402

sys.path.insert(0, str(ROOT / "tools"))
import setup_steps  # noqa: E402

GIT_ENV = dict(os.environ, GIT_AUTHOR_NAME="Kit Test", GIT_AUTHOR_EMAIL="kit@example.invalid",
               GIT_COMMITTER_NAME="Kit Test", GIT_COMMITTER_EMAIL="kit@example.invalid", GIT_CONFIG_NOSYSTEM="1")


def ws(folder, *args):
    """Run the folder's own ws.py, as a person in that folder would."""
    return subprocess.run([sys.executable, "ws.py", *args], cwd=str(folder), capture_output=True, text=True,
                          env=GIT_ENV)


def git(folder, *args):
    return subprocess.run(["git", "-C", str(folder), *args], capture_output=True, text=True, env=GIT_ENV)


def files_of(folder):
    """{path: bytes} of every file under the folder, the git folder left out."""
    folder = pathlib.Path(folder)
    return {p.relative_to(folder).as_posix(): p.read_bytes() for p in folder.rglob("*")
            if p.is_file() and ".git" not in p.relative_to(folder).parts}


def copy_kit(into):
    """A git repository holding this working copy's tracked files, committed: a kit that tests may change."""
    into = pathlib.Path(into)
    for path, _ in kit.tracked(ROOT):
        source = ROOT / path
        if source.is_file():
            (into / path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(source), str(into / path))
    git(into, "init", "--quiet")
    git(into, "add", "--all")
    git(into, "-c", "core.hooksPath=/dev/null", "commit", "--quiet", "--no-verify", "-m", "chore: the kit")
    return into


class ManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest, cls.contents = kit.build(ROOT)
        cls.rules = kit.load_rules(ROOT)
        cls.tracked = [path for path, _ in kit.tracked(ROOT)]

    def test_every_tracked_file_has_a_class(self):
        unclassed = [p for p in self.tracked if kit.rule_for(self.rules, p) is None]
        self.assertEqual(unclassed, [], "add a rule to kit/kit.json for each")
        self.assertEqual(sorted(self.manifest["files"]), sorted(self.tracked))

    def test_every_rule_still_matches_a_file(self):
        unused = [r["path"] for r in self.rules if not any(kit.rule_for([r], p) for p in self.tracked)]
        self.assertEqual(unused, [], "a rule for a path that is gone; remove it from kit/kit.json")

    def test_a_tracked_file_no_rule_matches_stops_the_build(self):
        with self.assertRaisesRegex(kit.KitError, "match no rule"):
            with tempfile.TemporaryDirectory() as folder:
                source = copy_kit(folder)
                (source / "stray.txt").write_text("a file nobody classed\n", encoding="utf-8")
                git(source, "add", "stray.txt")
                kit.build(source)

    def test_each_file_has_its_class_and_hash_and_the_seeded_ones_are_named(self):
        for path, entry in self.manifest["files"].items():
            self.assertIn(entry["class"], kit.CLASSES, path)
            self.assertRegex(entry["hash"], r"^sha256:[0-9a-f]{64}$", path)
            if entry["class"] == "synced":
                self.assertEqual(entry["hash"], kitlock.digest((ROOT / path).read_bytes()), path)
        seeded = {p for p, e in self.manifest["files"].items() if e["class"] == "seeded"}
        for path in ("AGENTS.md", "INDEX.md", "README.md", "workspace.json", "docs/question-log.md", ".gitignore"):
            self.assertIn(path, seeded)
        self.assertEqual(self.manifest["files"]["README.md"]["from"], "kit/seed/README.md")

    def test_it_carries_each_synced_page_proof_state_and_the_kit_cases(self):
        self.assertEqual(self.manifest["proof"]["docs/playbooks/fix-a-bug.md"]["proof"], "proven")
        self.assertTrue(self.manifest["proof"]["docs/playbooks/fix-a-bug.md"]["proven-by"])
        self.assertEqual(self.manifest["proof"]["docs/orchestration.md#delegating"],
                         {"proof": "unproven", "prove-by": "M4"})
        self.assertIn("fix-a-bug", self.manifest["cases"])
        self.assertEqual(self.manifest["kit"]["version"], VERSION)

    def test_the_proof_states_match_this_readme_table(self):
        sys.path.insert(0, str(ROOT / "parts"))
        import proof
        table = proof._readme_table((ROOT / "README.md").read_text(encoding="utf-8"), "Proven and unproven pages")
        self.assertEqual({name: entry["proof"] for name, entry in self.manifest["proof"].items()}, table)


class AdoptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = tempfile.TemporaryDirectory()
        cls.instance = pathlib.Path(cls.folder.name) / "instance"
        cls.report = kit.adopt(ROOT, cls.instance)

    @classmethod
    def tearDownClass(cls):
        cls.folder.cleanup()

    def test_selftest_and_check_pass_in_the_instance(self):
        for args in (("selftest",), ("check",), ("drift",)):
            result = ws(self.instance, *args)
            self.assertEqual(result.returncode, 0, f"ws.py {' '.join(args)}:\n{result.stdout}{result.stderr}")

    def test_the_instance_lists_no_repository_to_write_to(self):
        listed = json.loads((self.instance / "outward-repos.json").read_text(encoding="utf-8"))
        self.assertEqual(listed, {"repositories": []})

    def test_it_gets_its_synced_and_seeded_files_and_none_of_the_rest(self):
        lock = json.loads((self.instance / kitlock.LOCK).read_text(encoding="utf-8"))
        for path, entry in lock["files"].items():
            if path == kit.LIST:     # never synced: adopt writes the instance's own, empty
                continue
            there = (self.instance / path).is_file()
            self.assertEqual(there, entry["class"] != "never", path)
        self.assertFalse((self.instance / "kit").exists())
        self.assertTrue((self.instance / ".git").is_dir())

    def test_its_manifest_builds_no_milestone_and_its_readme_holds_the_kit_proof_table(self):
        manifest = json.loads((self.instance / "workspace.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["building"], [])
        self.assertEqual(manifest["version"], VERSION)
        readme = (self.instance / "README.md").read_text(encoding="utf-8")
        self.assertNotIn(kit.PROOF_TABLE, readme)
        self.assertIn("| [docs/playbooks/fix-a-bug.md](docs/playbooks/fix-a-bug.md) | proven |", readme)

    def test_the_index_loses_only_the_rows_that_name_what_stays_here(self):
        index = (self.instance / "INDEX.md").read_text(encoding="utf-8")
        self.assertNotIn("docs/plans/", index)
        self.assertNotIn("CHANGELOG.md", index)
        self.assertIn("| the nightly job | `ReconciliationWorker` |", index)
        self.assertIn("| Add a page | `docs/layout.md`, `INDEX.md` |", index)

    def test_the_setup_steps_include_the_hooks_and_the_drift_check(self):
        script = setup_steps.script("README.md", (self.instance / "README.md").read_text(encoding="utf-8"))
        for command in ("python3 ws.py selftest", "python3 ws.py check", "python3 ws.py drift",
                        "git config core.hooksPath .githooks"):
            self.assertIn(command, script)
        self.assertIn("kit/seed/README.md", setup_steps.SETUP_PAGES)

    def test_it_refuses_a_folder_that_is_not_empty_or_is_inside_the_kit(self):
        with self.assertRaisesRegex(kit.KitError, "not empty"):
            kit.adopt(ROOT, self.instance)
        with self.assertRaisesRegex(kit.KitError, "inside the kit"):
            kit.adopt(ROOT, ROOT / "docs" / "instance")


class DriftTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.instance = pathlib.Path(self.folder.name) / "instance"
        kit.adopt(ROOT, self.instance)

    def tearDown(self):
        self.folder.cleanup()

    def test_a_hand_edit_to_a_synced_file_fails_and_is_named(self):
        with open(self.instance / "docs/parts.md", "a", encoding="utf-8") as handle:
            handle.write("\nA line the instance added.\n")
        result = ws(self.instance, "drift")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("docs/parts.md: edited", result.stdout)
        check = ws(self.instance, "check")
        self.assertNotEqual(check.returncode, 0)
        self.assertIn("docs/parts.md:1: edited since kit", check.stdout)

    def test_an_edit_to_a_seeded_file_does_not(self):
        with open(self.instance / "AGENTS.md", "a", encoding="utf-8") as handle:
            handle.write("\nA trap the team found.\n")
        result = ws(self.instance, "drift")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_kept_file_is_the_instance_own(self):
        with open(self.instance / "docs/parts.md", "a", encoding="utf-8") as handle:
            handle.write("\nA line the instance added.\n")
        kept = ws(self.instance, "drift", "--keep", "docs/parts.md")
        self.assertEqual(kept.returncode, 0, kept.stdout + kept.stderr)
        lock = json.loads((self.instance / kitlock.LOCK).read_text(encoding="utf-8"))
        self.assertEqual(lock["files"]["docs/parts.md"]["class"], "kept")
        self.assertEqual(ws(self.instance, "check").returncode, 0)

    def test_a_deleted_synced_file_fails(self):
        (self.instance / "docs/templates/epic-folder.md").unlink()
        result = ws(self.instance, "drift")
        self.assertEqual(result.returncode, 1)
        self.assertIn("docs/templates/epic-folder.md: deleted", result.stdout)


class UpgradeTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        base = pathlib.Path(self.folder.name)
        self.old = copy_kit(base / "old")
        self.instance = base / "instance"
        kit.adopt(self.old, self.instance)
        self.new = copy_kit(base / "new")
        (self.new / "docs/browsers.md").write_text(
            (self.new / "docs/browsers.md").read_text(encoding="utf-8") + "\nA line the newer kit added.\n",
            encoding="utf-8")
        (self.new / "tools/kit_test_tool.py").write_text("# a tool the newer kit ships\n", encoding="utf-8")
        (self.new / "tools/symbols.py").unlink()
        git(self.new, "add", "--all")
        git(self.new, "-c", "core.hooksPath=/dev/null", "commit", "--quiet", "--no-verify", "-m", "chore: newer")

    def tearDown(self):
        self.folder.cleanup()

    def test_it_replaces_adds_and_removes_unedited_synced_files(self):
        with open(self.instance / "AGENTS.md", "a", encoding="utf-8") as handle:
            handle.write("\nThe instance's own fact.\n")
        report = kit.upgrade(self.new, self.instance)
        self.assertIn("  replaced docs/browsers.md", report)
        self.assertEqual((self.instance / "docs/browsers.md").read_bytes(), (self.new / "docs/browsers.md").read_bytes())
        self.assertTrue((self.instance / "tools/kit_test_tool.py").is_file())
        self.assertFalse((self.instance / "tools/symbols.py").exists())
        self.assertIn("The instance's own fact.", (self.instance / "AGENTS.md").read_text(encoding="utf-8"))
        lock = json.loads((self.instance / kitlock.LOCK).read_text(encoding="utf-8"))
        self.assertEqual(lock["files"]["docs/browsers.md"]["hash"],
                         kitlock.digest((self.new / "docs/browsers.md").read_bytes()))
        self.assertEqual(kit.drift(self.instance)[0], 0)

    def test_it_refuses_on_drift_and_changes_nothing(self):
        with open(self.instance / "docs/parts.md", "a", encoding="utf-8") as handle:
            handle.write("\nA hand edit.\n")
        before = files_of(self.instance)
        with self.assertRaisesRegex(kit.KitError, r"docs/parts\.md \(edited\)"):
            kit.upgrade(self.new, self.instance)
        self.assertEqual(files_of(self.instance), before)

    def test_it_refuses_a_new_synced_file_where_the_instance_has_its_own(self):
        (self.instance / "tools/kit_test_tool.py").write_text("# the instance's own tool\n", encoding="utf-8")
        before = files_of(self.instance)
        with self.assertRaisesRegex(kit.KitError, "tools/kit_test_tool.py"):
            kit.upgrade(self.new, self.instance)
        self.assertEqual(files_of(self.instance), before)

    def test_it_leaves_a_kept_file_alone(self):
        (self.instance / "docs/browsers.md").write_text("The instance's own page.\n", encoding="utf-8")
        kit.drift(self.instance, keep=["docs/browsers.md"])
        kit.upgrade(self.new, self.instance)
        self.assertEqual((self.instance / "docs/browsers.md").read_text(encoding="utf-8"), "The instance's own page.\n")
        lock = json.loads((self.instance / kitlock.LOCK).read_text(encoding="utf-8"))
        self.assertEqual(lock["files"]["docs/browsers.md"]["class"], "kept")

    def test_it_sets_the_instance_manifest_version_to_the_engine(self):
        manifest = self.instance / "workspace.json"
        manifest.write_text(manifest.read_text(encoding="utf-8").replace(f'"version": "{VERSION}"',
                                                                         '"version": "0.0.1"', 1), encoding="utf-8")
        report = kit.upgrade(self.new, self.instance)
        self.assertIn(f'  workspace.json: "version" set to {VERSION}', report)
        self.assertEqual(json.loads(manifest.read_text(encoding="utf-8"))["version"], VERSION)


class DecisionRecordTests(unittest.TestCase):
    def test_the_kit_record_holds_the_kill_rules_and_the_credit(self):
        text = (ROOT / "docs/decisions/0007-the-kit.md").read_text(encoding="utf-8")
        self.assertIn("**Kill rules.**", text)
        self.assertIn("three instances keep their own copy of the same synced procedure within one quarter", text)
        self.assertIn("within two quarters of its first release", text)
        self.assertIn("## Credit", text)
        self.assertIn("awslabs/aidlc-workflows", text)


if __name__ == "__main__":
    unittest.main()
