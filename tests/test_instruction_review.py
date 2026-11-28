"""M3 slice B1: the instruction-review trailer at the commit, the push and in CI, and the index of review records.

Criterion 17: a commit that adds or changes a guidance page names a review record that exists, or a listed skip
reason. The commit-msg hook refuses one without, the pre-push hook refuses a push to main holding one, and CI's
`check --commits` fails a range holding one. Criterion 62: the index lists a record for each page sub-batch A wrote.

Run: python3 -m unittest tests.test_instruction_review -b
"""
import json
import pathlib
import re
import shutil
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tests.test_core import Folder, manifest  # noqa: E402
from wslib import markdown  # noqa: E402
from wslib import parts as partlib  # noqa: E402

ZERO = "0" * 40
GUIDANCE = {"use": "review_trailer", "why": "test", "guidance": ["AGENTS.md", "docs/"], "except": ["docs/records/"]}
RECORD = "docs/records/instruction-reviews/2026-11-21-a.md"
RECORD_TEXT = ("---\nkind: record\nlast-reviewed: 2026-11-21\ncovers: docs/a.md\n---\n\n# Instruction review: "
               "docs/a.md\n")


class Repository(Folder):
    """A workspace with the trailer check and the subject check, committed once, with a bare remote."""

    def setUp(self):
        super().setUp()
        self.workspace(GUIDANCE, {"use": "commit_subject", "why": "test"})
        self.engine()
        self.write("docs/a.md", "# A\n")
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "t")
        self.git("config", "user.email", "t@example.invalid")
        self.git("add", ".")
        self.git("commit", "-q", "--no-verify", "-m", "chore: start")
        self.remote = self.root.parent / (self.root.name + "-remote.git")
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(self.remote)], check=True, capture_output=True)
        self.addCleanup(shutil.rmtree, str(self.remote), True)
        self.git("remote", "add", "origin", str(self.remote))
        self.git("push", "-q", "--no-verify", "origin", "main")
        self.start = self.git("rev-parse", "HEAD").stdout.strip()

    def message(self, text):
        self.write(".git/COMMIT_EDITMSG", text)
        return self.ws("check", "--message", str(self.root / ".git/COMMIT_EDITMSG"))

    def commit(self, files, message):
        for path, text in files.items():
            self.write(path, text)
            self.git("add", "--", path)
        self.git("commit", "-q", "--no-verify", "-m", message)
        return self.git("rev-parse", "HEAD").stdout.strip()

    def tip(self, ref="refs/heads/main"):
        done = subprocess.run(["git", "--git-dir", str(self.remote), "rev-parse", "--verify", "-q", ref],
                              capture_output=True, text=True)
        return done.stdout.strip() or ZERO

    def push(self, remote_ref="refs/heads/main"):
        sha = self.git("rev-parse", "HEAD").stdout.strip()
        return self.ws("check", "--push", "origin", stdin=f"refs/heads/x {sha} {remote_ref} {self.tip(remote_ref)}\n")


class CommitMessageTests(Repository):
    """The commit-msg hook's command judges the commit being made: its staged paths and staged files."""

    def test_a_staged_guidance_page_needs_a_trailer(self):
        self.write("docs/a.md", "# A\n\nMore.\n")
        self.git("add", "docs/a.md")
        code, out = self.message("docs: more on a\n")
        self.assertEqual(code, 1, out)
        self.assertIn("changes the guidance page docs/a.md with no instruction review", out)
        self.assertIn("docs/playbooks/instruction-review.md", out)
        self.assertEqual(self.message("docs: more on a\n\nInstructions-review: skipped: link or typo only\n")[0], 0)

    def test_a_staged_record_that_covers_the_page_passes_and_a_missing_one_fails(self):
        self.write("docs/a.md", "# A\n\nMore.\n")
        self.git("add", "docs/a.md")
        code, out = self.message(f"docs: more on a\n\nInstructions-review: {RECORD}\n")
        self.assertEqual(code, 1, out)
        self.assertIn("which does not exist in the commit", out)
        self.write(RECORD, RECORD_TEXT)
        code, out = self.message(f"docs: more on a\n\nInstructions-review: {RECORD}\n")
        self.assertEqual(code, 1, "a record on disk but not staged is not in the commit: " + out)
        self.git("add", RECORD)
        code, out = self.message(f"docs: more on a\n\nInstructions-review: {RECORD}\n")
        self.assertEqual(code, 0, out)

    def test_a_staged_deletion_needs_a_trailer_too(self):
        self.git("rm", "-q", "docs/a.md")
        self.assertEqual(self.message("docs: strike a\n")[0], 1)
        self.assertEqual(self.message("docs: strike a\n\nInstructions-review: skipped: strike\n")[0], 0)

    def test_a_commit_of_no_guidance_page_needs_none(self):
        self.write("src/x.py", "x = 1\n")
        self.git("add", "src/x.py")
        self.assertEqual(self.message("fix: x\n")[0], 0)

    def test_a_merge_in_progress_is_not_judged_at_the_commit(self):
        self.git("checkout", "-q", "-b", "topic")
        self.commit({"docs/a.md": "# A\n\nTopic.\n"}, "docs: topic\n\nInstructions-review: skipped: link or typo only")
        self.git("checkout", "-q", "main")
        self.commit({"src/x.py": "x = 1\n"}, "fix: x")
        self.git("merge", "-q", "--no-ff", "--no-commit", "topic")
        code, out = self.message("Merge branch 'topic'\n")
        self.assertEqual(code, 0, out)


class PushTests(Repository):
    """The pre-push hook judges every commit a push to main adds, with the part read from the remote's tip."""

    def test_a_push_to_main_holding_a_commit_without_a_trailer_is_refused(self):
        good = self.commit({"docs/a.md": "# A\n\nOne.\n"}, "docs: one\n\nInstructions-review: skipped: front matter only")
        bad = self.commit({"AGENTS.md": "# Contract\n"}, "docs: the contract")
        code, out = self.push()
        self.assertEqual(code, 1, out)
        self.assertIn(bad[:7], out)
        self.assertNotIn(good[:7], out)
        self.assertIn("AGENTS.md", out)

    def test_a_push_whose_commits_name_their_records_passes(self):
        self.commit({"docs/a.md": "# A\n\nOne.\n", RECORD: RECORD_TEXT}, f"docs: one\n\nInstructions-review: {RECORD}")
        code, out = self.push()
        self.assertEqual(code, 0, out)

    def test_a_push_to_another_branch_is_left_to_ci(self):
        self.commit({"docs/a.md": "# A\n\nOne.\n"}, "docs: one")
        code, out = self.push("refs/heads/topic")
        self.assertEqual(code, 0, out)

    def test_before_the_remote_uses_the_part_a_push_is_not_judged(self):
        self.write("workspace.json", manifest([{"use": "commit_subject", "why": "test"}]))
        self.git("add", "workspace.json")
        self.git("commit", "-q", "--no-verify", "-m", "chore: no trailer rule")
        self.git("push", "-q", "--no-verify", "origin", "main")
        self.commit({"docs/a.md": "# A\n\nOne.\n"}, "docs: one")
        self.assertEqual(self.push()[0], 0)


class RangeTests(Repository):
    """CI's `check --commits BASE..HEAD`: each commit with its own message, paths, tree and identities."""

    def test_a_range_holding_a_commit_without_a_trailer_fails(self):
        self.commit({"docs/a.md": "# A\n\nOne.\n", RECORD: RECORD_TEXT}, f"docs: one\n\nInstructions-review: {RECORD}")
        bad = self.commit({"docs/a.md": "# A\n\nTwo.\n"}, "docs: two")
        code, out = self.ws("check", "--commits", f"{self.start}..HEAD")
        self.assertEqual(code, 1, out)
        self.assertIn(f"commit {bad[:7]} \"docs: two\"", out)
        self.assertIn("2 commit(s) checked", out)

    def test_a_record_must_exist_in_the_commit_that_names_it(self):
        self.commit({"docs/a.md": "# A\n\nOne.\n"}, f"docs: one\n\nInstructions-review: {RECORD}")
        self.commit({RECORD: RECORD_TEXT}, "docs: the record, a commit late")
        code, out = self.ws("check", "--commits", f"{self.start}..HEAD")
        self.assertEqual(code, 1, out)
        self.assertIn("which does not exist in the commit", out)

    def test_every_commit_message_check_runs_over_the_range(self):
        self.commit({"src/x.py": "x = 1\n"}, "did a thing")
        code, out = self.ws("check", "--commits", f"{self.start}..HEAD")
        self.assertEqual(code, 1, out)
        self.assertIn("matches none of the accepted formats", out)

    def test_a_clean_range_passes_and_merges_are_judged_by_their_own_changes(self):
        self.git("checkout", "-q", "-b", "topic")
        self.commit({"docs/a.md": "# A\n\nTopic.\n"}, "docs: topic\n\nInstructions-review: skipped: link or typo only")
        self.git("checkout", "-q", "main")
        self.commit({"src/x.py": "x = 1\n"}, "fix: x")
        self.git("merge", "-q", "--no-ff", "--no-edit", "topic")
        code, out = self.ws("check", "--commits", f"{self.start}..HEAD")
        self.assertEqual(code, 0, out)
        self.assertIn("3 commit(s) checked", out)

    def test_commits_made_before_their_tree_used_the_rule_are_not_judged(self):
        self.write("workspace.json", manifest([{"use": "commit_subject", "why": "test"}]))
        self.git("add", "workspace.json")
        self.git("commit", "-q", "--no-verify", "-m", "chore: no trailer rule yet")
        base = self.git("rev-parse", "HEAD").stdout.strip()
        self.commit({"docs/a.md": "# A\n\nOld.\n"}, "docs: before the rule")
        self.assertEqual(self.ws("check", "--commits", f"{base}..HEAD")[0], 0)
        self.commit({"workspace.json": manifest([GUIDANCE, {"use": "commit_subject", "why": "test"}]),
                     "docs/a.md": "# A\n\nNew.\n"}, "docs: after the rule")
        self.assertEqual(self.ws("check", "--commits", f"{base}..HEAD")[0], 1)

    def test_a_range_with_no_base_checks_nothing_and_says_so(self):
        code, out = self.ws("check", "--commits", f"{ZERO}..HEAD")
        self.assertEqual(code, 0, out)
        self.assertIn("no base commit", out)


def config(name):
    for entry in partlib.load_manifest(ROOT)["parts"]:
        if entry["use"] == name:
            return entry
    raise AssertionError(f"{name} is not in the manifest")


class ThisWorkspaceTests(unittest.TestCase):
    def test_guidance_is_every_page_but_records_plans_and_milestones(self):
        """The trailer's path lists agree with the pages' kinds: a record, plan or milestone is not guidance, and
        nor is the records folder's own README, an index that each new record adds a row to."""
        entry = config("review_trailer")
        module = partlib.load(ROOT, entry, run_cases=False).module
        guidance = [module._pattern(p) for p in entry["guidance"]]
        outside = [module._pattern(p) for p in entry["except"]]
        listed = subprocess.run(["git", "-C", str(ROOT), "ls-files", "docs"], capture_output=True, text=True).stdout
        wrong = []
        for page in [p for p in listed.split("\n") if p.endswith(".md")]:
            text = (ROOT / page).read_text(encoding="utf-8")
            rows, _ = markdown.split_front_matter(text)
            kind = next((row.split(":", 1)[1].strip() for row in rows if row.startswith("kind:")), None)
            judged = any(g.fullmatch(page) for g in guidance) and not any(o.fullmatch(page) for o in outside)
            if judged == (kind in ("record", "plan", "milestone") or page.startswith("docs/records/")):
                wrong.append(f"{page} ({kind}): {'judged' if judged else 'not judged'}")
        self.assertEqual(wrong, [])
        for page in ("AGENTS.md", "CLAUDE.md", "INDEX.md", "README.md", ".github/copilot-instructions.md"):
            self.assertTrue(any(g.fullmatch(page) for g in guidance), page)

    def test_the_wrappers_are_guidance_and_their_selection_cases_are_not(self):
        """B6: a wrapper's description decides when guidance fires, so it takes the review; a selection case is
        a test input, as an eval case is, and the plugin's manifest is wiring."""
        entry = config("review_trailer")
        module = partlib.load(ROOT, entry, run_cases=False).module
        guidance = [module._pattern(p) for p in entry["guidance"]]
        listed = subprocess.run(["git", "-C", str(ROOT), "ls-files", "plugin"], capture_output=True, text=True).stdout
        paths = [p for p in listed.split("\n") if p]
        wrappers = [p for p in paths if p.startswith("plugin/skills/")]
        self.assertTrue(wrappers)
        for path in paths:
            self.assertEqual(any(g.fullmatch(path) for g in guidance), path in wrappers, path)

    def test_the_required_records_are_criterion_62_s_pages(self):
        self.assertEqual(sorted(config("review_index")["required"]), sorted([
            "AGENTS.md", "INDEX.md", "docs/layout.md", "docs/glossary.md", "docs/decisions/0006-what-proven-means.md",
            "docs/changing-the-machinery.md", "docs/definition-of-done.md", "docs/orchestration.md",
            ".github/copilot-instructions.md"]))

    def test_ci_checks_every_commit_of_a_pull_request_and_of_a_push_to_main(self):
        text = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        step = re.search(r"(?m)^ *- if: (.+)\n *run: bash wslib/launch\.sh ws\.py check --commits \"(.+)\"$", text)
        self.assertIsNotNone(step, "a step runs ws.py check --commits")
        self.assertIn("schedule", step.group(1))
        self.assertEqual(step.group(2), "${{ github.event.pull_request.base.sha || github.event.before }}.."
                                        "${{ github.event.pull_request.head.sha || github.sha }}")
        self.assertRegex(text, r"(?m)^ +fetch-depth: 0")

    def test_the_hooks_run_the_checks(self):
        self.assertIn("ws.py check --message", (ROOT / ".githooks/commit-msg").read_text(encoding="utf-8"))
        self.assertIn("ws.py check --push", (ROOT / ".githooks/pre-push").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
