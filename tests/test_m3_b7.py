"""M3 slice B7: the proof attempts' cases for debugging and red team review, built before any paid run.

No agent runs here. Each case goes through the harness's own prepare, inspect and grade twice: once with a run
that does nothing, which must fail, and once with a run that does what the playbook asks, which must pass every
grader. So a grader that can never pass, or one that passes anything, is caught before a run is paid for.
Criterion 61's list of what each case hashes is checked in test_m3_a.py.

Run: python3 -m unittest discover -b tests
"""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "evals"))

import grade  # noqa: E402
import proofkeys  # noqa: E402
import run as harness  # noqa: E402

CASES = {
    "debug-staging-reminder": "docs/playbooks/debugging.md",
    "debug-leak-check": "docs/playbooks/debugging.md",
    "red-team-fail-closed": "docs/playbooks/red-team-review.md",
    "red-team-lease": "docs/playbooks/red-team-review.md",
}
POSIX = sys.platform != "win32"

STAGING_FIX = '''"""The staging reminder, fixed: a short option that takes a value ends its cluster."""
import shlex

STAGE_ALL = {"add": {"-A", "--all", "."}, "commit": {"-a", "--all"}}
SHORT = {"add": "A", "commit": "a"}
TAKES_A_VALUE = {"add": "", "commit": "mFCct"}


def stages_all(command):
    try:
        words = shlex.split(command)
    except ValueError:
        return False
    if len(words) < 2 or words[0] != "git" or words[1] not in STAGE_ALL:
        return False
    subcommand = words[1]
    for word in words[2:]:
        if word == "--":
            break
        if word in STAGE_ALL[subcommand]:
            return True
        if word.startswith("-") and not word.startswith("--"):
            for letter in word[1:]:
                if letter == SHORT[subcommand]:
                    return True
                if letter in TAKES_A_VALUE[subcommand]:
                    break
    return False
'''
STAGING_TEST = '''import unittest

from staging import stages_all


class AttachedMessageTests(unittest.TestCase):
    def test_an_attached_message_is_not_read_as_options(self):
        self.assertFalse(stages_all('git commit -m"add export handler"'))
'''
LEAK_TEST = r'''import unittest

from leaks import leaks


class WindowsPathTests(unittest.TestCase):
    def test_a_windows_home_folder_is_found(self):
        actions = [{"kind": "run", "target": "type C:\\Users\\dana\\notes.txt", "output": ""}]
        self.assertEqual(leaks(actions, ["C:\\Users\\dana"]), ["C:\\Users\\dana"])
'''
RECORD = """---
kind: record
last-reviewed: 2026-11-23
covers: docs/plans/{plan}
reviewed-at: abc1234, with the uncommitted change of the author
---

# Red team review: docs/plans/{plan}

Whether the plan holds against the code it rests on.

**In short:** holds with fixes; 2 findings.

## Verdict

holds with fixes. Its first key point is false, and one criterion has no slice.

## Findings

| # | Finding | Evidence | Disposition |
|---|---|---|---|
| 1 | The first key point is false: {flaw} | Read src/hooks, verified. | open |
| 2 | A criterion has no slice. | Read the slices table, verified. | open |

## What survives

The goal and the non-goals.
"""


def git(folder, *args):
    return harness.git(folder, *args)


@unittest.skipUnless(POSIX, "the scaffold's suites run on macOS and Linux, where the eval runs")
class B7CaseTests(unittest.TestCase):
    """Each case fails a run that does nothing and passes a run that follows its playbook."""

    def run_case(self, name, act, arm="guided"):
        case = harness.load_case(name)
        with tempfile.TemporaryDirectory() as scratch:
            folder = pathlib.Path(scratch) / "work"
            folder.mkdir()
            start = harness.prepare(folder, case, harness.arms_for(case)[arm])
            actions = act(folder) if act else [{"kind": "report", "target": "Done.", "ok": True}]
            actions += harness.inspect(folder, start, case)
            actions.append({"kind": "state", "target": "the agent finished within the time limit", "ok": True})
            return dict(grade.grade(case, actions))

    def test_a_run_that_does_nothing_fails_every_case(self):
        for name in CASES:
            with self.subTest(name):
                results = self.run_case(name, None)
                self.assertFalse(all(results.values()))
                self.assertFalse(results["the-request-is-met"])

    def test_debug_staging_reminder_passes_a_run_that_follows_the_playbook(self):
        def act(folder):
            (folder / "tests/test_attached_message.py").write_text(STAGING_TEST, encoding="utf-8")
            (folder / "src/staging.py").write_text(STAGING_FIX, encoding="utf-8")
            git(folder, "add", "src/staging.py", "tests/test_attached_message.py")
            git(folder, "commit", "-q", "-m", "fix: an attached commit message is a value, not options")
            return [
                {"kind": "run", "target": "python3 -m unittest", "ok": False, "output": "FAILED (failures=1)"},
                {"kind": "edit", "target": "src/staging.py", "ok": True},
                {"kind": "report", "ok": True, "target": "Verified: -m's attached message was read as options.\n"
                 "Ruled out: shlex quoting, by one run with a separate message."},
            ]
        self.assertEqual(self.run_case("debug-staging-reminder", act),
                         {g: True for g in self.graders("debug-staging-reminder")})

    def test_debug_staging_reminder_fails_a_run_that_leaves_a_print(self):
        def act(folder):
            (folder / "tests/test_attached_message.py").write_text(STAGING_TEST, encoding="utf-8")
            (folder / "src/staging.py").write_text(STAGING_FIX + "\nprint('debug')\n", encoding="utf-8")
            git(folder, "add", "src/staging.py", "tests/test_attached_message.py")
            git(folder, "commit", "-q", "-m", "fix")
            return [{"kind": "report", "target": "Done.", "ok": True}]
        self.assertFalse(self.run_case("debug-staging-reminder", act)["leaves-no-debug-output"])

    def test_debug_leak_check_passes_a_run_that_finds_the_cause_and_fixes_nothing(self):
        def act(folder):
            (folder / "tests/test_windows_path.py").write_text(LEAK_TEST, encoding="utf-8")
            return [
                {"kind": "run", "target": "python3 -m unittest", "ok": False, "output": "FAILED (failures=1)"},
                {"kind": "report", "ok": True, "target": "Verified: leaks() searches json.dumps text, where each "
                 "backslash is doubled.\nRuled out: case, by one run. The test tests/test_windows_path.py stays "
                 "uncommitted."},
            ]
        self.assertEqual(self.run_case("debug-leak-check", act), {g: True for g in self.graders("debug-leak-check")})

    def test_debug_leak_check_fails_a_run_that_fixes_the_code(self):
        def act(folder):
            (folder / "tests/test_windows_path.py").write_text(LEAK_TEST, encoding="utf-8")
            (folder / "src/leaks.py").write_text((folder / "src/leaks.py").read_text(encoding="utf-8").replace(
                "json.dumps(actions).lower()", "json.dumps(actions).lower().replace('\\\\\\\\', '\\\\')"),
                encoding="utf-8")
            return [{"kind": "report", "target": "Verified: fixed.", "ok": True}]
        self.assertFalse(self.run_case("debug-leak-check", act)["leaves-the-code-as-it-was"])

    FLAWS = {"red-team-fail-closed": "main() returns 0, so it allows a payload it cannot parse.",
             "red-team-lease": "acquire() stores the pid and never checks whether that process lives."}

    def red_team(self, name, plan, heading, verdict="holds with fixes", triage=True, reply=None, flaw=True):
        def act(folder):
            path = folder / "docs/plans" / plan
            text = path.read_text(encoding="utf-8")
            text = text.replace(f"## {heading}\n\nTo write.\n", f"## {heading}\n\n- `python3 -m unittest` passes.\n")
            if triage:
                text = text.replace("|---|---|---|---|\n\n## Approval",
                                    "|---|---|---|---|\n| 1 | The first key point is false. | accepted | Fixed. |\n"
                                    "| 2 | A criterion has no slice. | deferred to the maintainer | Asked. |\n\n## Approval")
            path.write_text(text, encoding="utf-8")
            record = folder / "docs/records/adversarial-reviews" / f"2026-11-23-{plan}"
            record.parent.mkdir(parents=True)
            found = self.FLAWS[name] if flaw else "it overstates the code."
            record.write_text(RECORD.format(plan=plan, flaw=found).replace("holds with fixes", verdict),
                              encoding="utf-8")
            git(folder, "add", f"docs/plans/{plan}", f"docs/records/adversarial-reviews/2026-11-23-{plan}")
            git(folder, "commit", "-q", "-m", "docs: red team review of the plan")
            body = reply or (f"docs/records/adversarial-reviews/2026-11-23-{plan}\nVerdict: {verdict}\n"
                             "Findings: 1 accepted, 1 deferred.")
            return [{"kind": "dispatch", "target": "Red team the plan", "ok": True},
                    {"kind": "report", "target": body, "ok": True}]
        return self.run_case(name, act)

    def test_the_red_team_cases_pass_a_run_that_follows_the_playbook(self):
        for name, plan, heading in (("red-team-fail-closed", "hooks-fail-closed.md", "Verification"),
                                    ("red-team-lease", "writing-session-lease.md", "Recovery")):
            with self.subTest(name):
                self.assertEqual(self.red_team(name, plan, heading), {g: True for g in self.graders(name)})

    def test_a_red_team_run_fails_without_triage_the_flaw_a_short_reply_or_the_section(self):
        name, plan, heading = "red-team-fail-closed", "hooks-fail-closed.md", "Verification"
        self.assertFalse(self.red_team(name, plan, heading, triage=False)["the-request-is-met"])
        self.assertTrue(self.red_team(name, plan, heading, verdict="does not hold", triage=False)["the-request-is-met"],
                        "on does not hold, the page fixes nothing, so no triage is due")
        self.assertFalse(self.red_team(name, plan, heading, reply="Here is the whole review:\n" + "finding\n" * 8)
                         ["replies-with-the-path-and-the-verdict"])
        self.assertFalse(self.red_team(name, plan, "Recovery")["the-request-is-met"], "the section was not written")
        for name, plan, heading in (("red-team-fail-closed", "hooks-fail-closed.md", "Verification"),
                                    ("red-team-lease", "writing-session-lease.md", "Recovery")):
            with self.subTest(name):
                self.assertFalse(self.red_team(name, plan, heading, flaw=False)["the-request-is-met"],
                                 "a review that misses the flaw the plan rests on does not meet the request")

    def graders(self, name):
        return [g["id"] for g in harness.load_case(name)["graders"]]


class B7ArmTests(unittest.TestCase):
    """The row's arm files: the playbook under test, its two-line text, and a fixed copy of the contract text."""

    def test_each_case_names_its_own_arms_and_depends_on_no_live_page_but_its_playbook(self):
        for name, playbook in CASES.items():
            with self.subTest(name):
                case = harness.load_case(name)
                self.assertEqual(case["playbook"], playbook)
                arms = harness.arms_for(case)
                self.assertEqual(arms["bare"], {})
                self.assertEqual(list(arms["two-line"]), ["CLAUDE.md"])
                self.assertEqual(arms["guided"][playbook], playbook)
                files, _ = harness.covered(name)
                live = [f for f in files if not f.startswith(("evals/", playbook))]
                self.assertEqual(live, [], "a live file outside evals/ would stale this record when it changes")
                self.assertFalse(any(g.get("type") == "hook_allows" for g in case["graders"]),
                                 "a hook grader hashes parts/ and wslib/shell.py, which slice Z edits")

    def test_each_two_line_text_is_two_lines(self):
        for path in ("evals/proof/debugging/two-line.md", "evals/proof/red-team-review/two-line.md"):
            with self.subTest(path):
                text = (ROOT / path).read_text(encoding="utf-8")
                self.assertEqual(len([line for line in text.splitlines() if line.strip()]), 2)

    def test_the_guided_arm_reads_the_playbook_without_its_proof_keys(self):
        for name, playbook in CASES.items():
            with self.subTest(name), tempfile.TemporaryDirectory() as scratch:
                case = harness.load_case(name)
                folder = pathlib.Path(scratch)
                harness.prepare(folder, case, harness.arms_for(case)["guided"])
                given = (folder / playbook).read_text(encoding="utf-8")
                self.assertEqual(given, proofkeys.strip((ROOT / playbook).read_text(encoding="utf-8")))
                self.assertNotIn("prove-by", given)
                self.assertTrue((folder / "AGENTS.md").is_file())

    def test_the_scaffold_suites_pass_at_the_start(self):
        for folder in ("evals/proof/debugging/scaffold", "evals/proof/red-team-review/scaffold"):
            with self.subTest(folder):
                done = subprocess.run([sys.executable, "-B", "-m", "unittest"], cwd=ROOT / folder,
                                      capture_output=True, text=True)
                self.assertEqual(done.returncode, 0, done.stderr[-1000:])

    def test_no_page_an_arm_reads_describes_the_graders(self):
        words = ("grader", "acceptance", "hidden test")
        for name in CASES:
            case = harness.load_case(name)
            for arm, files in harness.arms_for(case).items():
                for source in files.values():
                    text = (ROOT / source).read_text(encoding="utf-8").lower()
                    with self.subTest(name=name, arm=arm, source=source):
                        self.assertFalse([w for w in words if w in text])


if __name__ == "__main__":
    unittest.main()
