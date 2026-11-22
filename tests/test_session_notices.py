"""M3 slice C5b: the session-start notices. The CI notice (criterion 69) and the handoff marker and loader
(criterion 59). See wslib/ci.py, wslib/handoff.py, parts/ci_notice.py and parts/handoff_loader.py.

The CI notice is run on gh's answers recorded from this repository (tests/records/ci-gh.json), through the parse
functions, the summary and the part; and once for real, with a stand-in gh on the path that prints those answers.
The handoff marker is written by `ws.py handoff` in throwaway repositories, and the loader is called through the
real runner with the session-start payloads both agent tools sent in a recorded run
(tests/records/session-events.json).

Run: python3 -m unittest tests.test_session_notices -b
"""
import contextlib
import copy
import io
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import ws  # noqa: E402
import wslib  # noqa: E402
from wslib import ci  # noqa: E402
from wslib import handoff  # noqa: E402
from wslib import parts as partlib  # noqa: E402

RECORD = json.loads((ROOT / "tests/records/ci-gh.json").read_text(encoding="utf-8"))
SESSIONS = json.loads((ROOT / "tests/records/session-events.json").read_text(encoding="utf-8"))
REPO = {"host": "github.com", "owner": "ryantornberg", "name": "agent-ready-workspace"}


def part(name):
    entry = {"use": name, "why": "a test needs it"}
    return partlib.load(ROOT, entry)


def answers(runs=None, jobs=None):
    """A gh caller that answers from the record, and the list of calls it was given."""
    calls = []
    runs = RECORD["recorded"]["runs"]["answer"] if runs is None else runs
    jobs = RECORD["recorded"]["jobs_red"]["answer"] if jobs is None else jobs

    def run(words, deadline):
        calls.append(words)
        if words[1:3] == ["run", "list"]:
            return json.dumps(runs)
        if words[1:3] == ["run", "view"]:
            return json.dumps(jobs)
        raise ci.Failed(f"no answer for {words}")
    return run, calls


def red(runs, count):
    """The recorded runs with the newest `count` marked failed: a shape the record's day did not hold."""
    runs = copy.deepcopy(runs)
    for run in runs[:count]:
        run["conclusion"] = "failure"
    return runs


class Repository(unittest.TestCase):
    """A throwaway workspace that borrows this repository's real parts, with git."""

    PARTS = ({"use": "ci_notice", "workflow": "ci.yml", "branch": "main"}, {"use": "handoff_loader", "branch": "main"})

    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = pathlib.Path(folder.name).resolve() / "ws"
        self.root.mkdir()
        entries = [dict(entry, why="a test needs it") for entry in self.PARTS]
        self.write("workspace.json", json.dumps({"version": wslib.VERSION, "parts": entries}))
        for entry in entries:
            for suffix in (".py", ".cases.json"):
                name = f"parts/{entry['use']}{suffix}"
                self.write(name, (ROOT / name).read_text(encoding="utf-8"))
        self.git("init", "-q", "-b", "main")
        self.git("add", "--all")
        self.git("commit", "-q", "-m", "start")
        self.notes = pathlib.Path(folder.name).resolve() / "handoffs"
        self.notes.mkdir()

    def write(self, name, text, top=None):
        path = (top or self.root) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def git(self, *args, top=None):
        return subprocess.run(["git", "-C", str(top or self.root), "-c", "user.name=t", "-c", "user.email=t@example.invalid",
                               "-c", "commit.gpgsign=false", *args], check=True, capture_output=True, text=True).stdout

    def commit(self, name, top=None):
        self.write(name, name + "\n", top)
        self.git("add", name, top=top)
        self.git("commit", "-q", "-m", name, top=top)

    def ws(self, *args, stdin="", root=None):
        out, err = io.StringIO(), io.StringIO()
        old = sys.stdin
        sys.stdin = io.StringIO(stdin)
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = ws.main(["--root", str(root or self.root), *args])
        finally:
            sys.stdin = old
        return code, out.getvalue() + err.getvalue()

    def note(self, topic, text=None):
        return self.write(f"2026-11-22-ws-{topic}.md", text or f"# Handoff: ws, 2026-11-22, {topic}\n\n## Goal\n\n"
                                                              f"The goal of {topic}.\n", self.notes)

    def start(self, tool="claude-code", cwd=None):
        """What a session start says, through the runner, from one tool's recorded SessionStart payload."""
        call = next(c for c in SESSIONS["calls"] if c["tool"] == tool and c["payload"]["hook_event_name"] == "SessionStart")
        payload = dict(call["payload"], cwd=str(cwd or self.root))
        code, out = self.ws("hook", "session-start", "--tool", tool, stdin=json.dumps(payload))
        self.assertEqual(code, 0)
        if not out.strip():
            return ""
        reply = json.loads(out)
        self.assertEqual(reply["hookSpecificOutput"]["hookEventName"], "SessionStart")
        return reply["hookSpecificOutput"]["additionalContext"]


class CiRecordedTests(unittest.TestCase):
    """Criterion 69, on gh's recorded answers: each step is a build function and a parse function."""

    def test_the_build_functions_make_the_recorded_calls(self):
        self.assertEqual(ci.build_runs(REPO, "ci.yml", "main"), RECORD["recorded"]["runs"]["call"])
        self.assertEqual(ci.build_jobs(REPO, 45065796541), RECORD["recorded"]["jobs_red"]["call"])

    def test_a_passing_newest_run_gives_nothing_and_reads_no_jobs(self):
        run, calls = answers()
        with mock.patch.object(ci, "repository", return_value=REPO):
            found = ci.fact(ROOT, "ci.yml", "main", run=run)
        self.assertEqual(found, {"failed": 0})
        self.assertEqual(len(calls), 1, "no second call when the newest run passed")
        self.assertIsNone(part("ci_notice").decide({"ci": found}))

    def test_the_recorded_red_run_is_shown_with_its_step_and_link(self):
        recorded = RECORD["recorded"]["runs"]["answer"]
        run, calls = answers(runs=recorded[1:])          # as main stood before the passing run: the merge had failed
        with mock.patch.object(ci, "repository", return_value=REPO):
            found = ci.fact(ROOT, "ci.yml", "main", run=run)
        self.assertEqual(calls[1], RECORD["recorded"]["jobs_red"]["call"])
        self.assertEqual(found["failed"], 1)
        self.assertFalse(found["at_least"])
        self.assertEqual(found["since"], recorded[1]["createdAt"])
        self.assertEqual(found["steps"], ["check (macos-latest, 3.9): Run bash wslib/launch.sh tests/hook_cases.py"])
        text = part("ci_notice").decide({"ci": found})
        self.assertIn("1 run in a row", text)
        self.assertIn(recorded[1]["createdAt"], text)
        self.assertIn("Run bash wslib/launch.sh tests/hook_cases.py", text)
        self.assertIn(recorded[1]["url"], text)

    def test_a_streak_counts_the_failures_in_a_row_and_dates_the_first(self):
        runs = red(RECORD["recorded"]["runs"]["answer"], 3)
        found = ci.summary(ci.parse_runs(json.dumps(runs)), ["j: s"])
        self.assertEqual((found["failed"], found["since"]), (3, runs[2]["createdAt"]))
        self.assertIn("3 runs in a row", part("ci_notice").decide({"ci": found}))

    def test_a_streak_as_long_as_the_runs_read_is_at_least_that_many(self):
        runs = red(RECORD["recorded"]["runs"]["answer"], 20)
        found = ci.summary(ci.parse_runs(json.dumps(runs)), [])
        self.assertTrue(found["at_least"])
        self.assertIn("at least 20 runs in a row", part("ci_notice").decide({"ci": found}))

    def test_a_full_list_ending_in_a_passed_over_run_is_still_at_least(self):
        runs = red(RECORD["recorded"]["runs"]["answer"], 20)
        runs[7]["conclusion"] = "cancelled"
        found = ci.summary(ci.parse_runs(json.dumps(runs)), [], read=len(runs))
        self.assertEqual((found["failed"], found["at_least"]), (19, True))
        self.assertIn("at least 19 runs in a row", part("ci_notice").decide({"ci": found}))

    def test_runs_that_say_nothing_about_main_are_passed_over(self):
        recorded = RECORD["recorded"]["runs"]["answer"]
        skipped = [dict(recorded[0], status="in_progress", conclusion=""), dict(recorded[0], conclusion="cancelled"),
                   dict(recorded[0], conclusion="skipped"), dict(recorded[0], event="pull_request", conclusion="failure")]
        found = ci.summary(ci.parse_runs(json.dumps(skipped + recorded[1:])))
        self.assertEqual(found["failed"], 1, "judged by the failed run behind them")
        self.assertEqual(ci.summary(ci.parse_runs(json.dumps(skipped + recorded))), {"failed": 0})

    def test_the_failing_steps_of_the_green_run_are_none(self):
        self.assertEqual(ci.parse_jobs(json.dumps(RECORD["recorded"]["jobs_green"]["answer"])), [])

    def test_a_failed_job_with_no_failed_step_is_named_alone(self):
        jobs = {"jobs": [{"name": "check (ubuntu-latest, 3.13)", "conclusion": "failure",
                          "steps": [{"name": "Set up job", "conclusion": "success"}]}]}
        self.assertEqual(ci.parse_jobs(json.dumps(jobs)), ["check (ubuntu-latest, 3.13)"])

    def test_no_run_to_judge_gives_no_fact(self):
        self.assertIsNone(ci.summary(ci.parse_runs("[]")))


class CiErrorTests(unittest.TestCase):
    """Criterion 69: on any error, nothing is shown and the session starts."""

    def fact(self, run, repo=REPO):
        with mock.patch.object(ci, "repository", return_value=repo):
            return ci.fact(ROOT, "ci.yml", "main", run=run)

    def test_no_gh_gives_nothing(self):
        with mock.patch.object(ci.shutil, "which", return_value=None):
            self.assertIsNone(self.fact(ci.call))

    def test_a_gh_that_fails_gives_nothing(self):
        def run(words, deadline):
            raise ci.Failed("gh exited 1")
        self.assertIsNone(self.fact(run))

    def test_the_time_limit_gives_nothing(self):
        self.assertIsNone(ci.fact(ROOT, "ci.yml", "main", budget=0, run=ci.call))

    def test_answers_that_cannot_be_read_give_nothing(self):
        recorded = RECORD["recorded"]["runs"]["answer"]
        for name, runs, jobs in (("not json", "{", None), ("not a list", {"runs": []}, None),
                                 ("a run with no id", [dict(recorded[0], databaseId="x")], None),
                                 ("jobs that are not a list", red(recorded, 1), {"jobs": "none"})):
            with self.subTest(name):
                def run(words, deadline, runs=runs, jobs=jobs):
                    if words[2] == "list":
                        return runs if isinstance(runs, str) else json.dumps(runs)
                    return json.dumps(jobs)
                self.assertIsNone(self.fact(run))

    def test_an_origin_that_is_a_local_path_makes_no_call(self):
        with tempfile.TemporaryDirectory() as folder:
            subprocess.run(["git", "init", "-q", folder], check=True, capture_output=True)
            for origin in (None, os.path.join(folder, "origin.git"), "file:///srv/origin.git", "git@github.com:only-one"):
                with self.subTest(origin):
                    if origin:
                        subprocess.run(["git", "-C", folder, "remote", "add" if origin.startswith(folder) else "set-url",
                                        "origin", origin], check=True, capture_output=True)
                    run, calls = answers()
                    self.assertIsNone(ci.fact(folder, "ci.yml", "main", run=run))
                    self.assertEqual(calls, [])

    def test_another_host_is_asked_and_its_failure_says_nothing(self):
        with tempfile.TemporaryDirectory() as folder:
            subprocess.run(["git", "init", "-q", folder], check=True, capture_output=True)
            subprocess.run(["git", "-C", folder, "remote", "add", "origin", "git@gitlab.com:acme/orders.git"],
                           check=True, capture_output=True)
            calls = []

            def run(words, deadline):
                calls.append(words)
                raise ci.Failed("gh exited 1")
            self.assertIsNone(ci.fact(folder, "ci.yml", "main", run=run))
            self.assertEqual(calls[0][3:5], ["-R", "gitlab.com/acme/orders"])

    def test_the_origin_read_is_inside_the_deadline(self):
        run, calls = answers()
        self.assertIsNone(ci.fact(ROOT, "ci.yml", "main", budget=0, run=run))
        self.assertEqual(calls, [], "no time left: neither git nor gh is asked")

    def test_gh_runs_without_the_variables_that_choose_a_repository(self):
        seen = {}

        class Fake:
            returncode = 0

            def __init__(self, argv, **kwargs):
                seen.update(argv=argv, env=kwargs["env"])

            def communicate(self, timeout=None):
                return b"[]", None
        with mock.patch.dict(os.environ, {"GH_REPO": "other/repo", "GH_HOST": "example.com"}), \
                mock.patch.object(ci.shutil, "which", return_value="/bin/gh"), \
                mock.patch.object(ci.subprocess, "Popen", Fake):
            ci.call(ci.build_runs(REPO, "ci.yml", "main"), time.monotonic() + 5)
        self.assertNotIn("GH_REPO", seen["env"])
        self.assertNotIn("GH_HOST", seen["env"])
        self.assertEqual(seen["env"]["GH_PROMPT_DISABLED"], "1")
        self.assertEqual(seen["argv"][1:5], ["run", "list", "-R", "github.com/ryantornberg/agent-ready-workspace"])


FAKE_GH = '''import json, os, sys, time
spec = json.load(open(os.environ["FAKE_GH"], encoding="utf-8"))
with open(os.environ["FAKE_GH"] + ".calls", "a", encoding="utf-8") as log:
    log.write(json.dumps(sys.argv[1:]) + "\\n")
time.sleep(spec.get("sleep", 0))
answer = spec.get(" ".join(sys.argv[1:3]))
if answer is None:
    sys.exit(1)
sys.stdout.write(json.dumps(answer))
'''


class CiForRealTests(Repository):
    """Criterion 69 through the real runner: a stand-in gh on the path prints the recorded answers."""

    def setUp(self):
        super().setUp()
        self.git("remote", "add", "origin", "git@github.com:ryantornberg/agent-ready-workspace.git")
        self.bin = self.notes.parent / "bin"
        self.bin.mkdir()
        (self.bin / "gh.py").write_text(FAKE_GH, encoding="utf-8")
        if os.name == "nt":
            (self.bin / "gh.bat").write_text(f'@"{sys.executable}" "%~dp0gh.py" %*\r\n', encoding="utf-8")
        else:
            (self.bin / "gh").write_text(f"#!/bin/sh\nexec \"{sys.executable}\" \"$(dirname \"$0\")/gh.py\" \"$@\"\n",
                                         encoding="utf-8")
            (self.bin / "gh").chmod(0o755)
        self.spec = self.notes.parent / "gh.json"

    def answer(self, **spec):
        self.spec.write_text(json.dumps(spec), encoding="utf-8")
        env = {"PATH": str(self.bin) + os.pathsep + os.environ.get("PATH", ""), "FAKE_GH": str(self.spec)}
        return mock.patch.dict(os.environ, env)

    def calls(self):
        log = pathlib.Path(str(self.spec) + ".calls")
        return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []

    def test_a_red_main_is_shown_at_session_start_from_both_tools(self):
        recorded = RECORD["recorded"]["runs"]["answer"]
        with self.answer(**{"run list": recorded[1:], "run view": RECORD["recorded"]["jobs_red"]["answer"]}):
            for tool in ("claude-code", "codex"):
                with self.subTest(tool):
                    text = self.start(tool)
                    self.assertIn("CI is red on main: 1 run in a row of ci.yml failed", text)
                    self.assertIn(recorded[1]["url"], text)
                    self.assertIn("check (macos-latest, 3.9): Run bash wslib/launch.sh tests/hook_cases.py", text)
        self.assertEqual(self.calls()[0], RECORD["recorded"]["runs"]["call"][1:])

    def test_a_green_main_shows_nothing(self):
        with self.answer(**{"run list": RECORD["recorded"]["runs"]["answer"]}):
            self.assertEqual(self.start(), "")
        self.assertEqual(len(self.calls()), 1)

    def test_a_gh_that_fails_shows_nothing(self):
        with self.answer():
            self.assertEqual(self.start(), "")

    def test_a_gh_past_the_time_limit_shows_nothing_and_holds_the_start_only_that_long(self):
        recorded = RECORD["recorded"]["runs"]["answer"]
        with self.answer(sleep=30, **{"run list": recorded[1:]}), mock.patch.object(ci, "BUDGET", 1.0):
            began = time.monotonic()
            self.assertEqual(self.start(), "")
            self.assertLess(time.monotonic() - began, 10.0)

    def test_no_gh_on_the_path_shows_nothing(self):
        with mock.patch.dict(os.environ, {"PATH": str(self.notes)}):
            self.assertEqual(self.start(), "")


class HandoffWriteTests(Repository):
    """Criterion 59: the marker is written by `ws.py handoff`, keyed by branch, in the working copy's git folder."""

    def marker(self, branch, top=None):
        git_dir = pathlib.Path(self.git("rev-parse", "--absolute-git-dir", top=top).strip())
        return handoff.file_of(git_dir, branch)

    def test_the_marker_names_the_note_and_lives_in_the_git_folder(self):
        note = self.note("loader")
        code, out = self.ws("handoff", str(note))
        self.assertEqual(code, 0, out)
        self.assertIn("is written", out)
        body = json.loads(self.marker("main").read_text(encoding="utf-8"))
        self.assertEqual(body["branch"], "main")
        self.assertEqual(pathlib.Path(body["note"]), note.resolve())
        self.assertTrue(str(self.marker("main")).startswith(str(self.root / ".git")))

    def test_writing_again_updates_the_marker_in_place_and_touches_no_other(self):
        self.git("checkout", "-q", "-b", "other")
        self.assertEqual(self.ws("handoff", str(self.note("other")))[0], 0)
        before = self.marker("other").read_bytes()
        self.git("checkout", "-q", "main")
        self.assertEqual(self.ws("handoff", str(self.note("first")))[0], 0)
        code, out = self.ws("handoff", str(self.note("second")))
        self.assertEqual(code, 0, out)
        self.assertIn("is updated", out)
        self.assertEqual(json.loads(self.marker("main").read_text(encoding="utf-8"))["note"],
                         str(self.note("second").resolve()))
        self.assertEqual(self.marker("other").read_bytes(), before, "another branch's marker is untouched")
        self.assertEqual(len(list(self.marker("main").parent.glob("*.json"))), 2)

    def test_a_note_that_is_not_there_is_refused(self):
        code, out = self.ws("handoff", str(self.notes / "missing.md"))
        self.assertEqual(code, 2)
        self.assertIn("Write the note first", out)

    def test_a_detached_head_is_refused(self):
        self.git("checkout", "-q", "--detach")
        code, out = self.ws("handoff", str(self.note("detached")))
        self.assertEqual(code, 2)
        self.assertIn("HEAD is detached", out)

    def test_a_branch_name_of_any_form_is_a_safe_file_name(self):
        for name in ("m3/c5b", "Fix", "feature/a.b-c"):
            self.git("checkout", "-q", "-b", name)
            self.assertEqual(self.ws("handoff", str(self.note(name.replace("/", "-"))))[0], 0)
        self.assertEqual(sorted(m["branch"] for m in handoff.markers(self.root / ".git")), ["Fix", "feature/a.b-c", "m3/c5b"])

    def test_done_clears_only_the_named_marker(self):
        self.ws("handoff", str(self.note("main")))
        self.git("checkout", "-q", "-b", "other")
        self.ws("handoff", str(self.note("other")))
        code, out = self.ws("handoff", "--done", "main")
        self.assertEqual(code, 0, out)
        self.assertFalse(self.marker("main").exists())
        self.assertTrue(self.marker("other").exists())
        self.assertIn("cleared", self.ws("handoff", "--done")[1])
        self.assertFalse(self.marker("other").exists())

    def test_a_note_and_done_together_are_refused(self):
        self.assertEqual(self.ws("handoff", str(self.note("x")), "--done")[0], 2)

    def test_a_linked_worktree_keeps_its_own_markers(self):
        tree = self.notes.parent / "tree"
        self.git("worktree", "add", "-q", "-b", "feature", str(tree))
        code, out = self.ws("handoff", str(self.note("feature")), root=tree)
        self.assertEqual(code, 0, out)
        self.assertTrue(self.marker("feature", top=tree).exists())
        self.assertIn(f"{os.sep}worktrees{os.sep}", str(self.marker("feature", top=tree)))
        self.assertIn("The goal of feature.", self.start(cwd=tree))
        self.assertEqual(self.start(), "", "the main copy's sessions are not shown a worktree's note")


class HandoffPendingTests(Repository):
    """Criterion 59: a marker is pending until its branch merges or `ws.py handoff --done` clears it."""

    def pending(self):
        return [m["branch"] for m in handoff.pending(self.root, self.root / ".git")]

    def test_a_branch_with_work_of_its_own_clears_when_it_merges(self):
        self.git("checkout", "-q", "-b", "feature")
        self.commit("feature.txt")
        self.ws("handoff", str(self.note("feature")))
        self.assertEqual(self.pending(), ["feature"])
        self.commit("more.txt")                    # work goes on after the note
        self.git("checkout", "-q", "main")
        self.git("merge", "-q", "--no-ff", "-m", "merge", "feature")
        self.assertEqual(self.pending(), [])
        self.assertIn("feature: merged", self.ws("handoff")[1])
        self.git("checkout", "-q", "feature")
        self.assertEqual(self.start(), "", "a cleared marker is not shown")

    def test_the_tip_at_writing_counts_after_the_branch_is_deleted(self):
        self.git("checkout", "-q", "-b", "feature")
        self.commit("feature.txt")
        self.ws("handoff", str(self.note("feature")))
        self.git("checkout", "-q", "main")
        self.git("merge", "-q", "--no-ff", "-m", "merge", "feature")
        self.git("branch", "-q", "-D", "feature")
        self.assertEqual(self.pending(), [])

    def test_a_merge_on_origin_counts(self):
        origin = self.notes.parent / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True, capture_output=True)
        self.git("remote", "add", "origin", str(origin))
        self.git("push", "-q", "origin", "main")
        self.git("checkout", "-q", "-b", "feature")
        self.commit("feature.txt")
        self.ws("handoff", str(self.note("feature")))
        self.git("push", "-q", "origin", "feature:main")      # merged on the remote; local main has not moved
        self.git("fetch", "-q", "origin")
        self.assertEqual(self.pending(), [])

    def test_a_branch_with_no_work_of_its_own_stays_pending(self):
        self.git("checkout", "-q", "-b", "fresh")
        self.ws("handoff", str(self.note("fresh")))
        self.git("checkout", "-q", "main")
        self.commit("main-moves.txt")
        self.assertEqual(self.pending(), ["fresh"])

    def test_a_note_on_the_default_branch_stays_pending_until_done(self):
        self.ws("handoff", str(self.note("main")))
        self.commit("later.txt")
        self.assertEqual(self.pending(), ["main"])
        self.ws("handoff", "--done")
        self.assertEqual(self.pending(), [])

    def test_a_squash_merge_leaves_the_marker_pending(self):
        self.git("checkout", "-q", "-b", "feature")
        self.commit("feature.txt")
        self.ws("handoff", str(self.note("feature")))
        self.git("checkout", "-q", "main")
        self.git("merge", "-q", "--squash", "feature")
        self.git("commit", "-q", "-m", "squash")
        self.assertEqual(self.pending(), ["feature"])


class LoaderTests(Repository):
    """Criterion 59 through the real runner, from both agent tools' recorded session-start payloads."""

    def test_one_pending_marker_shows_its_note_from_both_tools(self):
        self.ws("handoff", str(self.note("loader")))
        for tool in ("claude-code", "codex"):
            with self.subTest(tool):
                text = self.start(tool)
                self.assertIn("A handoff note is pending for the branch main", text)
                self.assertIn("The goal of loader.", text)

    def test_two_pending_markers_show_none_and_list_both(self):
        self.ws("handoff", str(self.note("first")))
        self.git("checkout", "-q", "-b", "second")
        self.ws("handoff", str(self.note("second")))
        for tool in ("claude-code", "codex"):
            with self.subTest(tool):
                text = self.start(tool)
                self.assertIn("2 handoff notes are pending", text)
                self.assertIn(str(self.note("first").resolve()), text)
                self.assertIn(str(self.note("second").resolve()), text)
                self.assertNotIn("The goal of", text)

    def test_no_marker_shows_nothing(self):
        for tool in ("claude-code", "codex"):
            with self.subTest(tool):
                self.assertEqual(self.start(tool), "")

    def test_a_cleared_marker_is_not_shown(self):
        self.ws("handoff", str(self.note("done")))
        self.ws("handoff", "--done")
        self.assertEqual(self.start(), "")

    def test_the_note_written_again_is_the_one_shown(self):
        self.ws("handoff", str(self.note("first")))
        self.ws("handoff", str(self.note("second")))
        text = self.start()
        self.assertIn("The goal of second.", text)
        self.assertNotIn("The goal of first.", text)

    def test_a_long_note_is_cut_and_says_so(self):
        self.ws("handoff", str(self.note("long", "# Handoff\n\n" + "word " * 4000)))
        text = self.start()
        self.assertIn("read the rest in the file", text)
        self.assertLess(len(text), handoff.SHOWN + 2000)

    def test_a_note_that_is_gone_is_named_not_guessed(self):
        note = self.note("gone")
        self.ws("handoff", str(note))
        note.unlink()
        text = self.start()
        self.assertIn("cannot be read", text)
        self.assertIn(str(note.resolve()), text)


class RecordedRunTests(unittest.TestCase):
    """Criterion 59, from both agent tools: one recorded run of each, with one pending marker, shows that the tool
    gave the agent the note (tests/records/handoff-loader-runs.json)."""

    def test_each_tool_gave_the_agent_the_pending_note(self):
        record = json.loads((ROOT / "tests/records/handoff-loader-runs.json").read_text(encoding="utf-8"))
        goal = "PROBE-GOAL: finish the lantern inventory for the night shift."
        for tool in ("claude-code", "codex"):
            with self.subTest(tool):
                reply = record["runs"][tool]["reply"]
                self.assertIn(goal, reply)
                self.assertEqual(reply.split(goal, 1)[1].strip(), "main", "the note's goal line, then the notice's branch")
        notice = record["runs"]["claude-code"]["notice"]
        self.assertEqual((notice["hook_event"], notice["outcome"]), ("SessionStart", "success"))
        self.assertIn(goal, notice["output"]["hookSpecificOutput"]["additionalContext"])

    def test_the_recorded_notice_is_what_the_loader_says_now(self):
        record = json.loads((ROOT / "tests/records/handoff-loader-runs.json").read_text(encoding="utf-8"))
        shown = record["runs"]["claude-code"]["notice"]["output"]["hookSpecificOutput"]["additionalContext"]
        head, _, rest = shown.partition("\n\n")
        note = rest.rsplit("\n\n[The end of the handoff note.]", 1)[0] + "\n"
        marker = {"branch": "main", "note": "/scratch/handoffs/2026-11-22-ws-probe.md",
                  "written": head.split(", written ")[1].split(". ")[0], "text": note, "cut": False}
        said = part("handoff_loader").decide({"handoffs": [marker]})
        self.assertEqual(partlib.with_page(said, part("handoff_loader").module.PAGE), shown)


class GitFolderTests(Repository):
    """Criterion 59: the marker is written through `ws.py handoff`, while an agent's own write to the git folder is
    refused."""

    PARTS = Repository.PARTS + ({"use": "git_folder"}, {"use": "git_folder_shell"})

    def test_an_edit_tool_write_to_the_marker_folder_is_refused(self):
        target = self.root / ".git" / handoff.FOLDER / "0000000000000000.json"
        payload = {"session_id": "s", "transcript_path": "/t.jsonl", "hook_event_name": "PreToolUse", "cwd": str(self.root),
                   "tool_name": "Write", "tool_input": {"file_path": str(target), "content": "{}"}}
        code, out = self.ws("hook", "before-edit", "--tool", "claude-code", stdin=json.dumps(payload))
        self.assertEqual(code, 2, out)
        self.assertIn("git_folder", out)

    def test_a_shell_write_to_the_marker_folder_is_refused_and_ws_handoff_passes(self):
        def shell(command):
            payload = {"session_id": "s", "transcript_path": "/t.jsonl", "hook_event_name": "PreToolUse",
                       "cwd": str(self.root), "tool_name": "Bash", "tool_input": {"command": command}}
            return self.ws("hook", "before-shell", "--tool", "claude-code", stdin=json.dumps(payload))
        self.assertEqual(shell("echo '{}' > .git/ws-handoff/0000000000000000.json")[0], 2)
        code, out = shell("python3 ws.py handoff ~/handoffs/2026-11-22-ws-loader.md")
        self.assertEqual(code, 0, out)
        code, out = shell("python3 ws.py handoff --done")
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main()
