"""The hook case runner, tests/hook_cases.py (M3 slice C2, criterion 28). CI runs the runner itself as a step of
its own on all three systems, which prints every hook's time; these tests hold its rules.
Run: python3 -m unittest tests.test_hook_cases -b"""
import io
import json
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

import hook_cases  # noqa: E402
from wslib import parts as partlib  # noqa: E402


class BudgetTests(unittest.TestCase):
    def test_a_before_tool_hook_and_the_two_rows_fail_over_200_milliseconds_on_linux_and_macos(self):
        for row in ("before-shell", "before-edit", "before-handoff", "after-edit", "git push", "gh write"):
            with self.subTest(row):
                self.assertEqual(hook_cases.budget_verdict(row, 0.199, "posix"), "ok")
                self.assertEqual(hook_cases.budget_verdict(row, 0.201, "posix"), "over")

    def test_session_start_gets_2_seconds_and_stop_20(self):
        self.assertEqual(hook_cases.budget_verdict("session-start", 1.9, "posix"), "ok")
        self.assertEqual(hook_cases.budget_verdict("session-start", 2.1, "posix"), "over")
        self.assertEqual(hook_cases.budget_verdict("stop", 19.0, "posix"), "ok")
        self.assertEqual(hook_cases.budget_verdict("stop", 21.0, "posix"), "over")

    def test_windows_reports_and_does_not_fail(self):
        self.assertEqual(hook_cases.budget_verdict("before-shell", 0.9, "nt"), "report")
        self.assertEqual(hook_cases.budget_verdict("before-shell", 0.1, "nt"), "ok")

    def test_a_row_with_no_budget_is_printed_only(self):
        self.assertEqual(hook_cases.budget_verdict("session-end", 5.0, "posix"), "report")


class CaseFileTests(unittest.TestCase):
    def test_every_event_the_engine_knows_and_both_rows_have_a_case(self):
        self.assertEqual(hook_cases.missing_events(hook_cases.load_cases()), [])

    def test_a_missing_event_or_row_is_named(self):
        cases = hook_cases.load_cases()
        del cases["before-handoff"]
        cases["before-shell"] = [c for c in cases["before-shell"] if c.get("row") != "gh write"]
        self.assertEqual(hook_cases.missing_events(cases), ["before-handoff", "gh write"])

    def test_the_seeded_leases_use_a_live_and_a_dead_process(self):
        pids = {c["setup"]["lease"]["pid"] for listed in hook_cases.load_cases().values() for c in listed
                if "lease" in c.get("setup", {})}
        self.assertLessEqual({"live", "dead"}, pids)

    def malformed(self, event, case):
        with tempfile.TemporaryDirectory() as folder:
            (pathlib.Path(folder) / f"{event}.json").write_text(json.dumps([case]), encoding="utf-8")
            with self.assertRaises(hook_cases.CaseError) as raised:
                hook_cases.load_cases(folder)
            return str(raised.exception)

    def test_a_malformed_case_is_refused(self):
        good = {"name": "n", "tool": "claude-code", "payload": {}, "exit": 0}
        self.assertIn("local remote", self.malformed("session-start", good))
        self.assertIn("unknown key", self.malformed("before-shell", dict(good, expect=0)))
        self.assertIn('"row"', self.malformed("before-edit", dict(good, row="git push")))
        self.assertIn("live", self.malformed("before-edit", dict(good, setup={"lease": {"session": "s", "pid": 7}})))
        self.assertIn("not an event", self.malformed("before-everything", good))


class RunnerTests(unittest.TestCase):
    """Real calls through the launcher, in scratch repositories."""

    def run_cases(self, cases):
        out = io.StringIO()
        failures, rows = hook_cases.run(cases, out=out, repeat=1)
        return failures, rows, out.getvalue()

    def lease_case(self, pid):
        return next(c for c in hook_cases.load_cases()["before-edit"]
                    if c.get("setup", {}).get("lease", {}).get("pid") == pid and "README.md" in c["setup"].get("files", {}))

    def test_a_live_holder_refuses_and_a_dead_one_is_taken_over(self):
        failures, rows, table = self.run_cases({"before-edit": [self.lease_case("live"), self.lease_case("dead")]})
        self.assertEqual(failures, [])
        self.assertEqual(rows["before-edit"][0], 2)
        self.assertIn("before-edit", table)

    def test_a_case_whose_expectation_is_wrong_fails(self):
        live = self.lease_case("live")
        wrong = [dict(live, name="wrong exit", exit=0), dict(live, name="wrong holder", lease_after="me"),
                 dict(live, name="wrong text", output=["no such text"])]
        failures, _, _ = self.run_cases({"before-edit": wrong})
        self.assertEqual(len(failures), 3, failures)
        self.assertIn("exit 2, expected 0", failures[0])
        self.assertIn("held by 'other'", failures[1])
        self.assertIn("lacks 'no such text'", failures[2])

    def test_the_call_is_the_wiring_the_tool_runs(self):
        for tool in ("claude-code", "codex"):
            for event in partlib.EVENTS:
                with self.subTest(tool=tool, event=event):
                    command = hook_cases.wiring(ROOT, tool, event)
                    self.assertIn(f"wslib/launch.sh\" hook {event} --tool {tool}", command)


if __name__ == "__main__":
    unittest.main()
