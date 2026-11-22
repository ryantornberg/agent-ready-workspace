"""M3 slice C5a: the after-edit event with the chain reminder, and the stop event with the stop gate.

Criteria 37 and 41 of docs/plans/m3-reading-layer-machinery-and-kit.md, and criterion 57 for the stop gate (held by
tests/test_launcher.py, which runs every wired event). The recorded runs of both agent tools are in
tests/records/after-edit-and-stop.json; these tests replay their payloads through the real runner.

Run: python3 -m unittest discover -b tests
"""
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

from test_core import ROOT, Folder, manifest

from wslib import events
from wslib import gate as gates
from wslib import ledger as ledgers
from wslib import parts as partlib

RECORD = json.loads((ROOT / "tests/records/after-edit-and-stop.json").read_text(encoding="utf-8"))
INDEX = """---
kind: reference
last-reviewed: 2026-11-21
---

# Index

## Cross-cutting chains

| Change | Paths it touches |
|---|---|
| Write a probe note | `notes/`, `docs/probes.md` |
"""
# Imported by the stop gate's test run: it leaves a mark, so a test can tell whether the gate ran anything.
MARKER = '''import pathlib
import unittest

pathlib.Path("gate-ran.txt").write_text("ran\\n", encoding="utf-8")


class Marker(unittest.TestCase):
    def test_the_marker(self):
        self.assertFalse(pathlib.Path("fail-the-tests").exists(), "the tests were told to fail")
'''
SLOW = '''import time
import unittest


class Slow(unittest.TestCase):
    def test_slow(self):
        time.sleep(30)
'''


def recorded(tool, name):
    return [call["payload"] for call in RECORD["runs"][tool]["calls"] if call["event"] == name]


def placed(payload, root):
    """A recorded payload with its scratch folder, /scratch/ws, moved to this test's folder."""
    return json.loads(json.dumps(payload).replace("/scratch/ws", root.as_posix()))


class Workspace(Folder):
    """A workspace with this repository's engine, a chain, the two new hooks and a link check, committed."""

    tests = ("tests.test_marker",)

    def setUp(self):
        super().setUp()
        shutil.copy(ROOT / "ws.py", self.root / "ws.py")
        shutil.copytree(ROOT / "wslib", self.root / "wslib", ignore=shutil.ignore_patterns("__pycache__"))
        self.workspace({"use": "links"}, {"use": "chain_reminder"}, {"use": "stop_gate", "tests": list(self.tests)})
        self.write("INDEX.md", INDEX)
        self.write("docs/probes.md", "# Probes\n")
        self.write("tests/test_marker.py", MARKER)
        self.write("tests/test_slow.py", SLOW)
        self.git("init", "-q", "-b", "main")
        self.git("add", "--all")
        self.git("commit", "-q", "-m", "start")

    def edit(self, path, session, tool="claude-code"):
        """An edit through the before-edit hook, which records it in the ledger with its session."""
        payload = {"hook_event_name": "PreToolUse", "session_id": session, "cwd": str(self.root),
                   "tool_name": "Write", "tool_input": {"file_path": str(path), "content": "x\n"}}
        code, output = self.ws("hook", "before-edit", "--tool", tool, stdin=json.dumps(payload))
        self.assertEqual(code, 0, output)

    def stop(self, session, again=False, tool="claude-code", cwd=None):
        payload = {"hook_event_name": "Stop", "session_id": session, "cwd": str(cwd or self.root),
                   "stop_hook_active": again}
        return self.ws("hook", "stop", "--tool", tool, stdin=json.dumps(payload))

    def ran(self, top=None):
        return ((top or self.root) / "gate-ran.txt").exists()


class AfterEditTests(Workspace):
    """Criterion 37: an edit to a path in an index chain returns that chain's paths and pages after the edit, from
    both agent tools; any other path returns nothing."""

    def after(self, payload, tool):
        return self.ws("hook", "after-edit", "--tool", tool, stdin=json.dumps(payload))

    def test_the_recorded_edits_of_both_tools_are_shown_their_chain(self):
        for tool in ("claude-code", "codex"):
            with self.subTest(tool=tool):
                (payload,) = recorded(tool, "PostToolUse")
                code, output = self.after(placed(payload, self.root), tool)
                self.assertEqual(code, 0, output)
                reply = json.loads(output)["hookSpecificOutput"]
                self.assertEqual(reply["hookEventName"], "PostToolUse")
                self.assertIn("notes/probe.txt", reply["additionalContext"])
                self.assertIn("'Write a probe note' touches notes/, docs/probes.md", reply["additionalContext"])

    def test_the_recorded_edits_return_nothing_when_no_chain_names_the_path(self):
        self.write("INDEX.md", INDEX.replace("`notes/`, ", ""))
        for tool in ("claude-code", "codex"):
            with self.subTest(tool=tool):
                (payload,) = recorded(tool, "PostToolUse")
                self.assertEqual(self.after(placed(payload, self.root), tool), (0, ""))

    def test_an_after_edit_call_never_fails(self):
        for payload in ({"hook_event_name": "PostToolUse"}, {"hook_event_name": "PreToolUse", "tool_name": "Write",
                                                             "tool_input": {"file_path": "x"}}, "not json"):
            with self.subTest(payload=payload):
                self.assertEqual(self.ws("hook", "after-edit", "--tool", "claude-code",
                                         stdin=payload if isinstance(payload, str) else json.dumps(payload)), (0, ""))

    def test_the_workspace_shape_gets_a_plain_reminder(self):
        code, output = self.ws("hook", "after-edit", stdin='{"version": 1, "path": "docs/probes.md"}')
        self.assertEqual(code, 0)
        self.assertTrue(output.startswith("Reminder: chain_reminder: docs/probes.md"), output)

    def test_an_after_edit_records_nothing(self):
        (payload,) = recorded("claude-code", "PostToolUse")
        self.after(placed(payload, self.root), "claude-code")
        self.assertIsNone(ledgers.read(self.root / ".git"))


class StopGateTests(Workspace):
    """Criterion 41: with the session's own entries in the ledger and a failing check, the first stop is refused with
    the failure within 20 seconds, and the second is allowed with a report. A session with no entries of its own
    stops without anything running. The recorded runs of both tools show one refusal."""

    def break_a_link(self):
        self.write("docs/probes.md", "# Probes\n\n[gone](nowhere.md)\n")

    def test_the_recorded_runs_of_both_tools_show_one_refusal(self):
        for tool in ("claude-code", "codex"):
            calls = RECORD["runs"][tool]["calls"]
            stops = [call for call in calls if call["event"] == "Stop"]
            with self.subTest(tool=tool):
                self.assertEqual([call["payload"]["stop_hook_active"] for call in stops], [False, True])
                self.assertEqual(stops[0]["capture_hook_replied"]["decision"], "block")
                self.assertIsNone(stops[1]["capture_hook_replied"])
                self.assertEqual(RECORD["runs"][tool]["final_reply"], "acknowledged")

    def test_the_recorded_stops_are_refused_once_then_reported(self):
        self.break_a_link()
        for tool in ("claude-code", "codex"):
            first, second = recorded(tool, "Stop")
            with self.subTest(tool=tool):
                self.edit(self.root / "docs/probes.md", first["session_id"], tool="claude-code")
                started = time.monotonic()
                code, output = self.ws("hook", "stop", "--tool", tool, stdin=json.dumps(placed(first, self.root)))
                self.assertLess(time.monotonic() - started, 20)
                self.assertEqual(code, 0, output)
                reply = json.loads(output)
                self.assertEqual(reply["decision"], "block")
                self.assertIn("nowhere.md", reply["reason"])
                self.assertIn("python3 ws.py check", reply["reason"])
                code, output = self.ws("hook", "stop", "--tool", tool, stdin=json.dumps(placed(second, self.root)))
                self.assertEqual(code, 0, output)
                reply = json.loads(output)
                self.assertNotIn("decision", reply)
                self.assertIn("nowhere.md", reply["systemMessage"])

    def test_a_session_with_no_entries_of_its_own_stops_without_anything_running(self):
        self.break_a_link()
        self.edit(self.root / "docs/probes.md", "another session")
        self.assertEqual(self.stop("me"), (0, ""))
        self.assertFalse(self.ran(), "the gate ran something for a session with no entries")
        self.assertEqual(self.stop("another session")[0], 0)
        self.assertTrue(self.ran())

    def test_a_session_whose_check_and_tests_pass_stops_quietly_after_running_them(self):
        self.edit(self.root / "docs/probes.md", "me")
        self.assertEqual(self.stop("me"), (0, ""))
        self.assertTrue(self.ran())

    def test_failing_tests_refuse_too(self):
        self.write("fail-the-tests", "\n")
        self.edit(self.root / "docs/probes.md", "me")
        code, output = self.stop("me")
        reason = json.loads(output)["reason"]
        self.assertIn("python3 -m unittest -b tests.test_marker", reason)
        self.assertIn("the tests were told to fail", reason)
        self.assertNotIn("python3 ws.py check`", reason)

    def test_the_workspace_shape_is_refused_with_exit_2_and_then_reported(self):
        self.break_a_link()
        self.edit(self.root / "docs/probes.md", "me")
        event = {"version": 1, "session": "me", "cwd": str(self.root), "stop_hook_active": False}
        code, output = self.ws("hook", "stop", stdin=json.dumps(event))
        self.assertEqual(code, 2)
        self.assertTrue(output.startswith("Refused: stop_gate:"), output)
        code, output = self.ws("hook", "stop", stdin=json.dumps(dict(event, stop_hook_active=True)))
        self.assertEqual(code, 0)
        self.assertTrue(output.startswith("Report: stop_gate:"), output)

    def test_the_gate_judges_a_linked_worktree_where_its_entries_are(self):
        linked = self.root.parent / f"{self.root.name}-linked"
        self.addCleanup(shutil.rmtree, linked, True)
        self.git("worktree", "add", "-q", "-b", "side", str(linked))
        (linked / "docs/probes.md").write_text("[gone](nowhere.md)\n", encoding="utf-8")
        self.edit(linked / "docs/probes.md", "me")
        self.assertEqual(ledgers.session_entries(self.root, "me"), [(linked.resolve(), ["docs/probes.md"])])
        reason = json.loads(self.stop("me")[1])["reason"]
        self.assertIn(str(linked.resolve()), reason)
        self.assertTrue(self.ran(linked))
        self.assertFalse(self.ran(), "the main copy, which holds none of the session's entries, was judged")

    def test_an_unreadable_ledger_refuses_once_without_running_anything(self):
        (self.root / ".git" / "ws-ledger").write_text("not json\n", encoding="utf-8")
        reason = json.loads(self.stop("me")[1])["reason"]
        self.assertIn("could not run the check", reason)
        self.assertFalse(self.ran())

    def test_a_stop_never_fails(self):
        self.write("workspace.json", "{ broken")
        self.assertEqual(self.stop("me"), (0, ""))
        self.assertEqual(self.ws("hook", "stop", "--tool", "codex", stdin="not json"), (0, ""))


class GateRunTests(Workspace):
    def test_a_run_past_the_deadline_is_timed_out_and_the_rest_do_not_start(self):
        started = time.monotonic()
        runs = gates.run([self.root, self.root], ["tests.test_slow"], seconds=8)
        self.assertLess(time.monotonic() - started, 20)
        self.assertEqual([run["status"] for run in runs], ["passed", "timed-out", "timed-out", "timed-out"])
        self.assertIn("not started", runs[3]["output"])

    def test_the_commands_are_shown_as_a_person_would_run_them(self):
        self.assertEqual([shown for shown, _ in gates.commands(["tests.a", "tests.b"])],
                         ["python3 ws.py check", "python3 -m unittest -b tests.a tests.b"])
        self.assertEqual([shown for shown, _ in gates.commands([])], ["python3 ws.py check"])


class LedgerSessionTests(Folder):
    """The ledger records the session of each entry (decision 0005), and still reads entries with none."""

    def setUp(self):
        super().setUp()
        self.git("init", "-q", "-b", "main")
        self.folder = self.root / ".git"
        self.file = self.folder / ledgers.NAME

    def test_each_session_gets_its_own_entry_and_the_commit_check_reads_the_paths(self):
        ledgers.add(self.file, ["a.md"], "s1")
        ledgers.add(self.file, ["a.md"], "s1")
        ledgers.add(self.file, ["a.md", "b.md"], "s2")
        ledgers.add(self.file, ["c.md"])
        self.assertEqual(ledgers.entries(self.folder), [("a.md", "s1"), ("a.md", "s2"), ("b.md", "s2"), ("c.md", None)])
        self.assertEqual(ledgers.read(self.folder), {"a.md", "b.md", "c.md"})
        self.assertEqual(self.file.read_text(encoding="utf-8").splitlines()[-1], '"c.md"',
                         "an entry with no session keeps the format the ledger had before")

    def test_removing_a_path_removes_every_sessions_entry_and_keeps_the_rest(self):
        ledgers.add(self.file, ["a.md", "b.md"], "s1")
        ledgers.add(self.file, ["a.md"], "s2")
        self.assertEqual(ledgers.remove(self.folder, ["a.md"]), {"b.md"})
        self.assertEqual(ledgers.entries(self.folder), [("b.md", "s1")])
        ledgers.remove(self.folder, ["b.md"])
        self.assertFalse(self.file.exists())

    def test_a_line_in_neither_form_is_an_error(self):
        for line in ('{"path": "a.md"}', '{"path": "a.md", "session": ""}', "7", '{"path": "a", "session": "s", "x": 1}'):
            with self.subTest(line=line):
                self.file.write_text(line + "\n", encoding="utf-8")
                with self.assertRaises(ledgers.LedgerError):
                    ledgers.entries(self.folder)

    def test_an_edit_tool_records_its_session_and_ledger_add_records_none(self):
        self.write("workspace.json", manifest([{"use": "chains"}]))
        for suffix in (".py", ".cases.json"):
            self.write(f"parts/chains{suffix}", (ROOT / "parts" / f"chains{suffix}").read_text(encoding="utf-8"))
        payload = {"hook_event_name": "PreToolUse", "session_id": "s9", "cwd": str(self.root), "tool_name": "Edit",
                   "tool_input": {"file_path": str(self.root / "a.md")}}
        self.assertEqual(self.ws("hook", "before-edit", "--tool", "claude-code", stdin=json.dumps(payload))[0], 0)
        self.write("b.md", "made by a script\n")
        self.assertEqual(self.ws("ledger", "--add", str(self.root / "b.md"))[0], 0)
        self.assertEqual(ledgers.entries(self.folder), [("a.md", "s9"), ("b.md", None)])
        self.assertEqual(ledgers.session_entries(self.root, "s9"), [(self.root, ["a.md"])])
        self.assertEqual(ledgers.session_entries(self.root, "nobody"), [])


class EngineTests(unittest.TestCase):
    def test_the_events_and_the_ones_that_never_fail(self):
        self.assertEqual(partlib.EVENTS, ("before-shell", "before-edit", "before-handoff", "after-edit",
                                          "session-start", "session-end", "stop"))
        self.assertEqual(set(partlib.QUIET_EVENTS), set(partlib.EVENTS) - set(partlib.TOOL_EVENTS))

    def test_an_after_edit_hook_must_remind(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        folder = pathlib.Path(tmp.name)
        (folder / "parts").mkdir()
        (folder / "parts/after.py").write_text('KIND = "hook"\nEVENT = "after-edit"\n\n\ndef decide(event, config):\n'
                                               '    return "x" if event.get("path") == "a" else None\n', encoding="utf-8")
        (folder / "parts/after.cases.json").write_text(json.dumps([
            {"name": "a", "event": {"path": "a"}, "allow": False}, {"name": "b", "event": {"path": "b"}, "allow": True}]),
            encoding="utf-8")
        with self.assertRaises(partlib.PartError) as raised:
            partlib.load(folder, {"use": "after"})
        self.assertIn('must set MODE = "remind"', str(raised.exception))

    def test_both_tools_send_every_edit_tool_after_the_edit_and_the_stop_and_never_fail(self):
        claude = json.loads((ROOT / ".claude/settings.json").read_text(encoding="utf-8"))["hooks"]
        codex = json.loads((ROOT / ".codex/hooks.json").read_text(encoding="utf-8"))["hooks"]
        for tools, settings, name in ((events.CLAUDE_CODE_TOOLS, claude, "claude-code"), (events.CODEX_TOOLS, codex, "codex")):
            (entry,) = settings["PostToolUse"]
            hook = entry["hooks"][0]
            for tool in tools["after-edit"]:
                with self.subTest(name=name, tool=tool):
                    self.assertTrue(re.search(f"^(?:{entry['matcher']})$", tool), entry["matcher"])
            self.assertIn(f"hook after-edit --tool {name}", hook["command"])
            (stop,) = settings["Stop"]
            for command in (hook["command"], stop["hooks"][0]["command"]):
                with self.subTest(name=name, command=command):
                    self.assertTrue(command.rstrip().endswith("|| exit 0"), "after-edit and stop never fail")
            self.assertIn(f"hook stop --tool {name}", stop["hooks"][0]["command"])
            # The gate answers within 20 seconds; past the tool's own limit the stop would go ahead unjudged.
            self.assertGreaterEqual(stop["hooks"][0].get("timeout", 600), 25)
            self.assertLessEqual(stop["hooks"][0].get("timeout", 600), 30)

    def test_the_named_fast_tests_exist_and_finish_well_inside_the_gate(self):
        entry = next(e for e in json.loads((ROOT / "workspace.json").read_text(encoding="utf-8"))["parts"]
                     if e["use"] == "stop_gate")
        for name in entry["tests"]:
            with self.subTest(name=name):
                self.assertTrue((ROOT / (name.replace(".", "/") + ".py")).is_file(), name)
        started = time.monotonic()
        done = subprocess.run([sys.executable, "-m", "unittest", "-b", *entry["tests"]], cwd=ROOT, capture_output=True)
        self.assertEqual(done.returncode, 0, done.stderr.decode("utf-8", "replace")[-2000:])
        if os.name != "nt":     # starting processes costs several times more there; hook_cases.py reports it only
            self.assertLess(time.monotonic() - started, 10, "the fast tests leave the check too little of the 20 seconds")


if __name__ == "__main__":
    unittest.main()
