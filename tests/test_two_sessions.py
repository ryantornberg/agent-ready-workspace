"""M3 slice C9: the two-session demonstration, and its replay.

Criterion 48 of docs/plans/m3-reading-layer-machinery-and-kit.md. Two headless Claude Code sessions were started at
the same moment on the main working copy of a scratch clone of this repository, whose remote was a local bare
repository. tests/records/two-sessions.json holds what each session did and was shown, every hook payload a capture
hook saw, and the scratch remote's main afterwards. RecordTests reads the record; ReplayTests replays every recorded
edit and shell call through the real runner, in the order they happened, in a scratch clone built the same way, and
checks that each hook decides as the session was shown.

Run: python3 -m unittest discover -b tests
"""
import json
import os
import pathlib
import subprocess
import sys
import unittest
from unittest import mock

from test_core import ROOT, Folder

from wslib import lease as leases

RECORD = json.loads((ROOT / "tests/records/two-sessions.json").read_text(encoding="utf-8"))
RUNS = RECORD["runs"]
CALLS = RECORD["calls"]
BRANCH = "session-b-orders-note"
REFUSED_BY_A_HOOK = "hook error"


def steps(session):
    return {step["id"]: step for step in RUNS[session]["steps"]}


def shown(call):
    """What the session was shown for this recorded call, from its transcript."""
    return steps(call["session"])[call["payload"]["tool_use_id"]]


def hook_refused(step):
    return step.get("refused", False) and REFUSED_BY_A_HOOK in step["shown"]


def tool_calls(session=None):
    return [call for call in CALLS if call["payload"]["hook_event_name"] == "PreToolUse"
            and (session is None or call["session"] == session)]


def holder_and_second():
    """(the session that kept the main copy, the session the lease refused there)."""
    refused = {call["session"] for call in tool_calls() if hook_refused(shown(call))}
    (second,) = refused
    return ("a" if second == "b" else "b"), second


class RecordTests(unittest.TestCase):
    """What the demonstration did, as its record shows."""

    def test_both_sessions_started_at_once_on_the_same_main_working_copy(self):
        starts = [call for call in CALLS if call["payload"]["hook_event_name"] == "SessionStart"]
        self.assertEqual(sorted(call["session"] for call in starts), ["a", "b"])
        self.assertLess(abs(starts[0]["at"] - starts[1]["at"]), 2)
        self.assertEqual({call["payload"]["cwd"] for call in starts}, {"/scratch/ws"})
        self.assertNotEqual(RUNS["a"]["session_id"], RUNS["b"]["session_id"])

    def test_the_second_was_refused_by_the_lease_and_only_there(self):
        holder, second = holder_and_second()
        refusals = [shown(call) for call in tool_calls() if hook_refused(shown(call))]
        self.assertEqual(len(refusals), 1, "exactly one call was refused by a hook")
        (refusal,) = refusals
        self.assertEqual(refusal["tool"], "Edit")
        self.assertTrue(refusal["input"]["file_path"].startswith("/scratch/ws/src/"), "in the main working copy")
        self.assertIn("Refused by lease", refusal["shown"])
        self.assertIn(f"session {RUNS[holder]['session_id'][:8]}", refusal["shown"])
        self.assertIn("git worktree add --no-track -b BRANCH .claude/worktrees/NAME origin/main", refusal["shown"])

    def test_the_second_then_worked_in_a_worktree_made_from_the_remotes_main(self):
        holder, second = holder_and_second()
        later = tool_calls(second)
        refused_at = next(i for i, call in enumerate(later) if hook_refused(shown(call)))
        commands = [call["payload"]["tool_input"].get("command", "") for call in later[refused_at:]]
        self.assertTrue(any(f"git worktree add --no-track -b {BRANCH} .claude/worktrees/{BRANCH} origin/main" in command
                            for command in commands), commands)
        edits = [call for call in later[refused_at + 1:] if call["payload"]["tool_name"] == "Edit"]
        self.assertTrue(edits)
        for call in edits:
            self.assertTrue(call["payload"]["tool_input"]["file_path"].startswith(f"/scratch/ws/.claude/worktrees/{BRANCH}/"))
        self.assertTrue(all(call["payload"]["tool_input"]["file_path"].startswith("/scratch/ws/src/")
                            for call in tool_calls(holder) if call["payload"]["tool_name"] == "Edit"),
                        "the holder edited only the main working copy")

    def test_both_commits_reached_the_scratch_remotes_main_and_neither_holds_the_others_files(self):
        outcome = RECORD["outcome"]
        commits = outcome["remote_main"]
        self.assertEqual([commit["parent"] for commit in commits], [outcome["base"], commits[0]["commit"]])
        self.assertEqual(sorted(commit["subject"] for commit in commits), sorted(RUNS[s]["subject"] for s in "ab"))
        for commit in commits:
            session = next(s for s in "ab" if RUNS[s]["subject"] == commit["subject"])
            self.assertEqual(commit["files"], [RUNS[session]["file"]])
        self.assertIsNone(outcome["lease_after"], "the holder's session end released the lease")

    def test_nothing_it_did_could_reach_this_repositorys_main(self):
        pushes = [call["payload"]["tool_input"]["command"] for call in tool_calls()
                  if "git push" in call["payload"]["tool_input"].get("command", "")]
        self.assertTrue(pushes)
        for command in pushes:
            self.assertRegex(command, r"git push origin (main|HEAD:main)\b")
        self.assertIn("origin is /scratch/remote.git, a local path", RECORD["setup"][0])
        for commit in RECORD["outcome"]["remote_main"]:
            found = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", commit["commit"] + "^{commit}"],
                                   capture_output=True)
            self.assertNotEqual(found.returncode, 0, f"{commit['commit']} is in this repository")

    def test_each_session_reported_what_it_was_shown(self):
        holder, second = holder_and_second()
        self.assertIn("Refused by lease", RUNS[second]["final_reply"])
        self.assertIn(".claude/worktrees/", RUNS[second]["final_reply"])
        for s in "ab":
            commit = next(c["commit"] for c in RECORD["outcome"]["remote_main"] if c["subject"] == RUNS[s]["subject"])
            self.assertIn(commit, RUNS[s]["final_reply"])


class ReplayTests(Folder):
    """Every recorded edit and shell call, replayed through the real runner in recorded order, gets the decision the
    session was shown. Each session's Claude Code process is played by a live process of its own."""

    def setUp(self):
        super().setUp()
        self.scratch = self.root
        self.remote = self.scratch / "remote.git"
        seed = self.scratch / "seed"
        self.root = seed
        self.workspace({"use": "lease"}, {"use": "no_discard"}, {"use": "push_lease"})
        self.write(".gitignore", ".claude/worktrees/\n")
        for s in "ab":
            self.write(RUNS[s]["file"], "namespace Orders.Api;\n")
        self.git("init", "-q", "-b", "main")
        self.git("add", "--all")
        self.git("commit", "-q", "-m", "start")
        self.run_git(self.scratch, "clone", "-q", "--bare", str(seed), str(self.remote))
        self.root = self.scratch / "ws"
        self.run_git(self.scratch, "clone", "-q", str(self.remote), str(self.root))
        self.worktree = self.root / ".claude" / "worktrees" / BRANCH
        self.pids = {s: self.live_process() for s in "ab"}

    def live_process(self):
        process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(300)"])
        self.addCleanup(process.wait)
        self.addCleanup(process.kill)
        return process.pid

    def run_git(self, where, *args, check=True):
        return subprocess.run(["git", "-C", str(where), "-c", "user.name=t", "-c", "user.email=t@example.invalid",
                               "-c", "commit.gpgsign=false", *args], check=check, capture_output=True, text=True)

    def placed(self, payload):
        return json.loads(json.dumps(payload).replace("/scratch", self.scratch.as_posix()))

    def hook(self, call, **changes):
        payload = dict(self.placed(call["payload"]), **changes)
        event = {"PreToolUse": "before-edit" if payload.get("tool_name") != "Bash" else "before-shell",
                 "SessionEnd": "session-end"}[payload["hook_event_name"]]
        with mock.patch.dict(os.environ, {"CLAUDE_PID": str(self.pids[call["session"]])}):
            return self.ws("hook", event, "--tool", "claude-code", stdin=json.dumps(payload))

    def act(self, call):
        """Do what the session's call did once its hooks let it through, so the next call meets the same state."""
        payload = call["payload"]
        tool = payload.get("tool_name")
        run = RUNS[call["session"]]
        if tool == "Edit":
            path = pathlib.Path(self.placed(payload)["tool_input"]["file_path"])
            path.write_text(path.read_text(encoding="utf-8") + run["line"] + "\n", encoding="utf-8")
            return
        command = payload.get("tool_input", {}).get("command", "")
        where = self.worktree if self.worktree.name in payload["cwd"] + command and "worktree add" not in command else self.root
        if "worktree add" in command:
            self.run_git(self.root, "fetch", "-q", "origin")
            self.run_git(self.root, "worktree", "add", "-q", "--no-track", "-b", BRANCH, str(self.worktree), "origin/main")
        if "git commit" in command:
            self.run_git(where, "add", run["file"])
            self.run_git(where, "commit", "-q", "-m", run["subject"])
        if "git rebase" in command:
            self.run_git(where, "fetch", "-q", "origin")
            self.run_git(where, "rebase", "-q", "origin/main")
        if "git push" in command:
            refspec = "main" if where == self.root else "HEAD:main"
            pushed = self.run_git(where, "push", "-q", "origin", refspec, check=False)
            rejected = "[rejected]" in shown(call)["shown"]
            self.assertEqual(pushed.returncode != 0, rejected, pushed.stderr)

    def test_every_recorded_call_gets_the_decision_the_session_was_shown(self):
        holder, second = holder_and_second()
        decided = 0
        for call in CALLS:
            name = call["payload"]["hook_event_name"]
            if name == "SessionStart":
                continue
            code, output = self.hook(call)
            if name == "SessionEnd":
                self.assertEqual(code, 0, output)
                if call["session"] == holder:
                    self.assertIsNone(leases.query(self.root)[0], "the holder's session end releases the lease")
                continue
            step = shown(call)
            label = f"session {call['session']}, {step['tool']} at {call['at']}s"
            if hook_refused(step):
                self.assertEqual(code, 2, f"{label}: the session was refused, the replay was not\n{output}")
                self.assertIn("Refused by lease", output)
                self.assertIn(f"session {RUNS[holder]['session_id'][:8]}", output)
                self.assertIn("git worktree add --no-track -b BRANCH .claude/worktrees/NAME origin/main", output)
            else:
                self.assertEqual(code, 0, f"{label}: the session went ahead, the replay was refused\n{output}")
                self.act(call)
            decided += 1
        self.assertEqual(decided, len(tool_calls()))
        log = self.run_git(self.remote, "log", "--format=%s", "--name-only", "main~2..main").stdout.split()
        for s in "ab":
            self.assertIn(RUNS[s]["file"], log)

    def replay_until_refused(self):
        """Replay up to the refused edit, and return it."""
        for call in tool_calls():
            if hook_refused(shown(call)):
                return call
            self.assertEqual(self.hook(call)[0], 0)
            self.act(call)
        self.fail("no refused call")

    def test_the_refusal_rests_on_the_holder_being_alive(self):
        """Negative control: with the holder's process gone, the same edit takes the lease over."""
        holder, second = holder_and_second()
        refused = self.replay_until_refused()
        dead = subprocess.Popen([sys.executable, "-c", "pass"])
        dead.wait()
        leased = json.loads((self.root / ".git" / leases.NAME).read_text(encoding="utf-8"))
        (self.root / ".git" / leases.NAME).write_text(json.dumps(dict(leased, pid=dead.pid)), encoding="utf-8")
        code, output = self.hook(refused)
        self.assertEqual(code, 0, output)
        self.assertEqual(leases.query(self.root)[0]["session"], RUNS[second]["session_id"])

    def test_the_seconds_push_from_the_main_copy_would_have_been_refused(self):
        """Negative control: the push the second made from its worktree, made from the main copy while the holder
        holds it, is refused."""
        holder, second = holder_and_second()
        self.replay_until_refused()
        push = next(call for call in tool_calls(second) if "git push" in call["payload"]["tool_input"].get("command", ""))
        code, output = self.hook(push, cwd=str(self.root))
        self.assertEqual(code, 2, output)
        self.assertIn("push_lease", output)


if __name__ == "__main__":
    unittest.main()
