"""M3 slice C4: the merge helper, `ws.py merge NUMBER` (wslib/merge.py; criterion 35). M4 slice G1 (criterion 3): it
reads only each required check's pull_request run, and retargets the open pull requests based on the merged branch
before it deletes that branch.

Every gh call the helper makes is answered from tests/records/merge-gh.json: real answers recorded on this
repository, and a few made-up ones the record names with their reason. No test reaches the network. The
fast-forward after the merge runs on real throwaway repositories with a local bare remote, and a lease held by a
live or a dead process.
"""
import copy
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

from wslib import gitcall, lease as leases, merge  # noqa: E402

RECORD = json.loads((ROOT / "tests" / "records" / "merge-gh.json").read_text(encoding="utf-8"))
REPO = {"host": "github.com", "owner": "ryantornberg", "name": "agent-ready-workspace"}
HEAD = "c57ded34de5d96d5fc296d4a756bf26993728781"
MERGE_COMMIT = "ffbdc3db3567eecba70ceee18b0321660c256f96"
NUMBER = 32


def answer(name, made_up=False):
    found = RECORD["made_up" if made_up else "recorded"][name]
    return found["exit"], found["stdout"], found["stderr"]


def edited(name, change):
    """A recorded JSON answer with one change applied: the record stays the source of every other field."""
    code, out, err = answer(name)
    data = json.loads(out)
    change(data)
    return code, json.dumps(data) + "\n", err


def edited_made_up(name, change):
    code, out, err = answer(name, made_up=True)
    data = json.loads(out)
    change(data)
    return code, json.dumps(data) + "\n", err


def git(folder, *args):
    subprocess.run(["git", "-C", str(folder), *args], check=True, capture_output=True, env=gitcall.environment())


def git_out(folder, *args):
    return subprocess.run(["git", "-C", str(folder), *args], check=True, capture_output=True,
                          env=gitcall.environment()).stdout.decode().strip()


class FakeGh:
    """Answers each gh call the helper makes by its words, and keeps the calls in order."""

    def __init__(self, **overrides):
        open_pr = edited("view", lambda d: d.update(state="OPEN"))
        self.answers = {
            "view": open_pr,
            "branch_rule": answer("branch_rule"),
            "rulesets": answer("rulesets"),
            "check_runs": answer("check_runs"),
            "workflow_runs": answer("workflow_runs"),
            "statuses": answer("statuses"),
            "merge": answer("merge", made_up=True),
            "merged": answer("merged"),
            "commit": answer("commit"),
            "dependents": answer("dependents"),
            "retarget 33": answer("retarget", made_up=True),
            "retarget 34": edited_made_up("retarget", lambda d: d.update(number=34, head={"ref": "m3/b3"})),
            "delete": answer("delete", made_up=True),
        }
        self.answers.update(overrides)
        self.calls = []

    def __call__(self, words):
        self.calls.append(list(words))
        expected = {
            "view": merge.build_view(REPO, NUMBER),
            "branch_rule": merge.build_branch_rule(REPO, "main"),
            "rulesets": merge.build_rulesets(REPO, "main"),
            "check_runs": merge.build_check_runs(REPO, HEAD),
            "workflow_runs": merge.build_workflow_runs(REPO, HEAD),
            "statuses": merge.build_statuses(REPO, HEAD),
            "merge": merge.build_merge(REPO, NUMBER, HEAD),
            "merged": merge.build_merged(REPO, NUMBER),
            "commit": merge.build_commit(REPO, MERGE_COMMIT),
            "dependents": merge.build_dependents(REPO, "m3/b1"),
            "retarget 33": merge.build_retarget(REPO, 33, "main"),
            "retarget 34": merge.build_retarget(REPO, 34, "main"),
            "delete": merge.build_delete(REPO, "m3/b1"),
        }
        for name, built in expected.items():
            if list(words) == built:
                return self.answers[name]
        raise AssertionError(f"an unexpected gh call: {words}")

    def named(self, name):
        return [call for call in self.calls if call[:3] == ["gh", "pr", name]]


class Helper(unittest.TestCase):
    def setUp(self):
        self.base = pathlib.Path(os.path.realpath(tempfile.mkdtemp(prefix="merge-")))
        self.addCleanup(shutil.rmtree, self.base, ignore_errors=True)
        self.root = self.base / "w"
        self.root.mkdir()
        git(self.root, "init", "-q", "-b", "main")
        git(self.root, "remote", "add", "origin", "git@github.com:ryantornberg/agent-ready-workspace.git")
        self.said = []

    def run_merge(self, gh, update=None):
        update = update or (lambda root: ("current", None))
        return merge.merge(self.root, NUMBER, call=gh, say=self.said.append, update=update)

    def output(self):
        return "\n".join(self.said)


class BuildTests(unittest.TestCase):
    """The build functions give the words recorded from real calls, so the recorded answers fit them."""

    def test_the_builds_match_the_recorded_calls(self):
        recorded = RECORD["recorded"]
        self.assertEqual(merge.build_branch_rule(REPO, "main"), recorded["branch_rule"]["call"])
        self.assertEqual(merge.build_rulesets(REPO, "main"), recorded["rulesets"]["call"])
        self.assertEqual(merge.build_check_runs(REPO, HEAD), recorded["check_runs"]["call"])
        self.assertEqual(merge.build_statuses(REPO, HEAD), recorded["statuses"]["call"])
        self.assertEqual(merge.build_view(REPO, NUMBER), recorded["view"]["call"])
        self.assertEqual(merge.build_merged(REPO, NUMBER), recorded["merged"]["call"])
        self.assertEqual(merge.build_commit(REPO, MERGE_COMMIT), recorded["commit"]["call"])
        self.assertEqual(merge.build_workflow_runs(REPO, HEAD), recorded["workflow_runs"]["call"])
        self.assertEqual(merge.build_workflow_runs(REPO, MERGE_COMMIT), recorded["workflow_runs_push"]["call"])
        self.assertEqual(merge.build_dependents(REPO, "m3/b1"), recorded["dependents"]["call"])

    def test_a_retarget_names_the_new_base_alone(self):
        self.assertEqual(merge.build_retarget(REPO, 33, "main"),
                         ["gh", "api", "--hostname", "github.com", "-X", "PATCH",
                          "repos/ryantornberg/agent-ready-workspace/pulls/33", "-f", "base=main"])

    def test_a_branch_name_is_one_query_value(self):
        self.assertTrue(merge.build_dependents(REPO, "a&b=c#d")[-1].endswith("base=a%26b%3Dc%23d&per_page=100"))

    def test_the_merge_is_a_merge_commit_on_the_exact_head(self):
        words = merge.build_merge(REPO, NUMBER, HEAD)
        self.assertEqual(words, ["gh", "pr", "merge", "32", "-R", "github.com/ryantornberg/agent-ready-workspace",
                                 "--merge", "--match-head-commit", HEAD])
        for flag in ("--squash", "--rebase", "--admin", "--auto", "-s", "-r", "--delete-branch", "-d"):
            self.assertNotIn(flag, words)

    def test_a_branch_name_with_a_slash_stays_one_path(self):
        self.assertEqual(merge.build_delete(REPO, "m3/c4")[-1],
                         "repos/ryantornberg/agent-ready-workspace/git/refs/heads/m3/c4")


class MergeTests(Helper):
    def test_every_required_check_passed_on_the_head_so_it_merges(self):
        gh = FakeGh()
        self.assertEqual(self.run_merge(gh), 0)
        self.assertEqual(gh.named("merge"), [merge.build_merge(REPO, NUMBER, HEAD)])
        self.assertEqual(gh.calls[-1], merge.build_delete(REPO, "m3/b1"))
        self.assertIn("5 required check(s) passed on c57ded3", self.output())
        self.assertIn("as ffbdc3d, a merge commit", self.output())
        self.assertIn("Deleted the branch m3/b1", self.output())

    def refused(self, gh, *texts):
        self.assertEqual(self.run_merge(gh), 1)
        self.assertEqual(gh.named("merge"), [], "a refused pull request must not be merged")
        for text in texts:
            self.assertIn(text, self.output())

    def test_a_failed_required_check_refuses(self):
        def fail(data):
            data["check_runs"][1]["conclusion"] = "failure"
        self.refused(FakeGh(check_runs=edited("check_runs", fail)), "check (windows-latest, 3.13): failure on c57ded3")

    def test_a_required_check_still_running_refuses(self):
        def running(data):
            data["check_runs"][0].update(status="in_progress", conclusion=None)
        self.refused(FakeGh(check_runs=edited("check_runs", running)), "check (ubuntu-latest, 3.13): still in_progress")

    def test_a_required_check_that_passed_on_another_commit_refuses(self):
        def elsewhere(data):
            data["check_runs"][2]["head_sha"] = "0" * 40
        self.refused(FakeGh(check_runs=edited("check_runs", elsewhere)),
                     "check (windows-latest, 3.9): has not run on c57ded3")

    def test_a_required_check_that_never_ran_refuses(self):
        def missing(data):
            data["check_runs"] = [r for r in data["check_runs"] if r["name"] != "check (macos-latest, 3.9)"]
            data["total_count"] = len(data["check_runs"])
        self.refused(FakeGh(check_runs=edited("check_runs", missing)), "check (macos-latest, 3.9): has not run")

    def test_a_run_from_another_app_does_not_count(self):
        def other_app(data):
            data["check_runs"][0]["app"]["id"] = 1
        self.refused(FakeGh(check_runs=edited("check_runs", other_app)), "check (ubuntu-latest, 3.13): has not run")

    def test_the_newest_run_of_a_check_decides(self):
        def rerun(passed_last):
            def change(data):
                first = dict(data["check_runs"][0])
                again = dict(first, id=first["id"] + 1, conclusion="success" if passed_last else "failure")
                first["conclusion"] = "failure" if passed_last else "success"
                data["check_runs"][0] = first
                data["check_runs"].append(again)
                data["total_count"] = len(data["check_runs"])
            return change
        self.assertEqual(self.run_merge(FakeGh(check_runs=edited("check_runs", rerun(True)))), 0)
        self.said.clear()
        self.refused(FakeGh(check_runs=edited("check_runs", rerun(False))), "check (ubuntu-latest, 3.13): failure")

    def test_more_check_runs_than_one_page_refuses(self):
        self.refused(FakeGh(check_runs=edited("check_runs", lambda d: d.update(total_count=101))),
                     "has 101 check runs", "a person merges it")

    def test_a_branch_rule_that_requires_nothing_refuses(self):
        def unprotected(data):
            data["protected"] = False
            data["protection"] = {"enabled": False, "required_status_checks": {"contexts": [], "checks": []}}
        self.refused(FakeGh(branch_rule=edited("branch_rule", unprotected)), "requires no check")

    def test_a_ruleset_adds_its_checks(self):
        gh = FakeGh(rulesets=answer("rulesets_with_checks", made_up=True))
        self.refused(gh, "lint: has not run on c57ded3")

    def test_a_legacy_status_counts_for_a_context_with_no_app(self):
        def context_only(data):
            checks = data["protection"]["required_status_checks"]
            checks["checks"] = []
            checks["contexts"] = ["ci/legacy"]
        def status(state):
            return edited("statuses", lambda d: d["statuses"].append({"context": "ci/legacy", "state": state}))
        rule = edited("branch_rule", context_only)
        self.assertEqual(self.run_merge(FakeGh(branch_rule=rule, statuses=status("success"))), 0)
        self.said.clear()
        self.refused(FakeGh(branch_rule=rule, statuses=status("failure")), "ci/legacy: failure")

    def test_a_draft_refuses_and_says_how_to_publish(self):
        view = edited("view", lambda d: d.update(state="OPEN", isDraft=True))
        self.refused(FakeGh(view=view), "is a draft", "gh pr ready 32")

    def test_a_merged_or_closed_pull_request_refuses(self):
        self.refused(FakeGh(view=answer("view")), "pull request 32 is merged, not open")
        self.said.clear()
        self.refused(FakeGh(view=edited("view", lambda d: d.update(state="CLOSED"))), "is closed, not open")

    def test_a_branch_from_another_repository_refuses(self):
        view = edited("view", lambda d: d.update(state="OPEN", isCrossRepository=True))
        self.refused(FakeGh(view=view), "another repository's branch")

    def test_a_pull_request_that_does_not_exist_is_an_error(self):
        gh = FakeGh(view=answer("view_missing"))
        with self.assertRaises(merge.MergeError) as raised:
            self.run_merge(gh)
        self.assertIn("Could not resolve to a PullRequest", str(raised.exception))
        self.assertEqual(gh.named("merge"), [])

    def test_a_head_that_moved_is_not_merged_and_the_branch_stays(self):
        gh = FakeGh(merge=answer("merge_head_moved", made_up=True))
        with self.assertRaises(merge.MergeError) as raised:
            self.run_merge(gh)
        self.assertIn("Head branch was modified", str(raised.exception))
        self.assertNotIn(merge.build_delete(REPO, "m3/b1"), gh.calls)

    def test_a_merge_that_is_not_a_merge_commit_is_an_error(self):
        one_parent = edited("commit_one_parent", lambda d: d.update(sha=MERGE_COMMIT))
        gh = FakeGh(commit=one_parent)
        with self.assertRaises(merge.MergeError) as raised:
            self.run_merge(gh)
        self.assertIn("not a merge commit", str(raised.exception))

    def test_a_branch_already_gone_is_noted(self):
        self.assertEqual(self.run_merge(FakeGh(delete=answer("delete_missing"))), 0)
        self.assertIn("The branch m3/b1 was already gone.", self.output())

    def test_the_fast_forward_note_is_shown(self):
        held = lambda root: ("held", "Another live agent session (other-se) holds the main working copy, so it was not")
        self.assertEqual(self.run_merge(FakeGh(), update=held), 0)
        self.assertIn("Merged ryantornberg/agent-ready-workspace#32", self.output())
        self.assertIn("Did not bring the main working copy up to date. Another live agent session", self.output())


PUSH_SUITE = 121642139999


def with_push_run(data):
    """The recorded workflow runs, with a newer run of the ci workflow on the same commit, made by a push."""
    data["workflow_runs"].append({"check_suite_id": PUSH_SUITE, "conclusion": "success", "event": "push",
                                  "head_sha": HEAD, "id": 44945199999, "name": "ci", "status": "completed"})
    data["total_count"] = len(data["workflow_runs"])


class PullRequestRunTests(Helper):
    """M4 criterion 3: only the pull request's own run of each required check counts, never a push run's."""

    def runs(self, change):
        return FakeGh(workflow_runs=edited("workflow_runs", with_push_run), check_runs=edited("check_runs", change))

    def test_the_recorded_runs_are_the_pull_requests_own(self):
        events = {run["event"] for run in json.loads(answer("workflow_runs")[1])["workflow_runs"]}
        self.assertEqual(events, {"pull_request"})
        events = {run["event"] for run in json.loads(answer("workflow_runs_push")[1])["workflow_runs"]}
        self.assertEqual(events, {"push"})

    def test_a_newer_push_run_that_passed_does_not_hide_a_failed_pull_request_run(self):
        def push_passes_later(data):
            first = data["check_runs"][0]
            first["conclusion"] = "failure"
            data["check_runs"].append(dict(first, id=first["id"] + 1000, conclusion="success",
                                           check_suite={"id": PUSH_SUITE}))
            data["total_count"] = len(data["check_runs"])
        gh = self.runs(push_passes_later)
        self.assertEqual(self.run_merge(gh), 1)
        self.assertEqual(gh.named("merge"), [])
        self.assertIn("check (ubuntu-latest, 3.13): failure on c57ded3", self.output())

    def test_a_check_that_passed_only_in_a_push_run_has_not_run(self):
        def push_only(data):
            data["check_runs"][0]["check_suite"] = {"id": PUSH_SUITE}
        gh = self.runs(push_only)
        self.assertEqual(self.run_merge(gh), 1)
        self.assertEqual(gh.named("merge"), [])
        self.assertIn("check (ubuntu-latest, 3.13): has not run on c57ded3 for the pull request", self.output())

    def test_an_actions_run_whose_workflow_run_is_not_listed_does_not_count(self):
        def unknown_suite(data):
            data["check_runs"][0]["check_suite"] = {"id": 1}
        self.assertEqual(self.run_merge(FakeGh(check_runs=edited("check_runs", unknown_suite))), 1)
        self.assertIn("check (ubuntu-latest, 3.13): has not run on c57ded3", self.output())

    def test_an_actions_run_with_no_check_suite_does_not_count(self):
        self.assertEqual(self.run_merge(FakeGh(check_runs=edited("check_runs",
                                                                 lambda d: d["check_runs"][0].pop("check_suite")))), 1)
        self.assertIn("check (ubuntu-latest, 3.13): has not run on c57ded3", self.output())

    def test_more_workflow_runs_than_one_page_refuses(self):
        gh = FakeGh(workflow_runs=edited("workflow_runs", lambda d: d.update(total_count=101)))
        self.assertEqual(self.run_merge(gh), 1)
        self.assertIn("has 101 workflow runs", self.output())

    def test_a_pull_request_run_still_passes_beside_a_push_run(self):
        self.assertEqual(self.run_merge(FakeGh(workflow_runs=edited("workflow_runs", with_push_run))), 0)


def stacked(data):
    """The recorded answer for the pull requests open on m3/b1, with two stacked on it."""
    data[:] = json.loads(answer("dependents_two", made_up=True)[1])


class StackedTests(Helper):
    """M4 criterion 3 and Q84: each open pull request based on the merged branch moves to the merged one's base
    before the branch is deleted, so GitHub does not close it. A retarget that fails deletes nothing."""

    def dependents(self, **overrides):
        return FakeGh(dependents=edited("dependents", stacked), **overrides)

    def test_none_open_on_the_branch_and_it_is_deleted(self):
        gh = FakeGh()
        self.assertEqual(self.run_merge(gh), 0)
        self.assertNotIn("Retargeted", self.output())
        self.assertEqual(gh.calls[-2:], [merge.build_dependents(REPO, "m3/b1"), merge.build_delete(REPO, "m3/b1")])

    def test_each_is_retargeted_to_the_merged_ones_base_before_the_branch_is_deleted(self):
        gh = self.dependents()
        self.assertEqual(self.run_merge(gh), 0)
        retargets = [gh.calls.index(merge.build_retarget(REPO, n, "main")) for n in (33, 34)]
        self.assertLess(gh.calls.index(merge.build_merge(REPO, NUMBER, HEAD)), min(retargets))
        self.assertLess(max(retargets), gh.calls.index(merge.build_delete(REPO, "m3/b1")))
        self.assertIn("Retargeted #33 (m3/b2) from m3/b1 to main.", self.output())
        self.assertIn("Retargeted #34 (m3/b3) from m3/b1 to main.", self.output())
        self.assertIn("covered the old range", self.output())
        self.assertIn("Deleted the branch m3/b1", self.output())

    def failed(self, gh, *texts):
        with self.assertRaises(merge.MergeError) as raised:
            self.run_merge(gh)
        self.assertNotIn(merge.build_delete(REPO, "m3/b1"), gh.calls, "nothing may be deleted")
        text = "\n".join(self.said + [str(raised.exception)])
        for item in ("the merge went through", "m3/b1 was not deleted", *texts):
            self.assertIn(item, text)
        return text

    def test_a_retarget_that_fails_deletes_nothing_and_says_so(self):
        text = self.failed(self.dependents(**{"retarget 34": answer("retarget_refused", made_up=True)}),
                           "#34", "Validation Failed", "Retargeted #33")
        self.assertIn("git push origin --delete m3/b1", text)

    def test_a_retarget_whose_answer_names_another_base_fails(self):
        wrong = edited_made_up("retarget", lambda d: d.update(base={"ref": "m3/b1"}))
        self.failed(self.dependents(**{"retarget 33": wrong}), "#33", "names its base as m3/b1, not main")

    def test_a_list_that_cannot_be_read_deletes_nothing(self):
        self.failed(FakeGh(dependents=(1, "", "gh: Not Found (HTTP 404)\n")), "could not be listed", "Not Found")

    def test_a_full_page_of_pull_requests_deletes_nothing(self):
        def hundred(data):
            data[:] = [{"number": n, "state": "open", "base": {"ref": "m3/b1"}, "head": {"ref": f"x{n}"}}
                       for n in range(100, 200)]
        self.failed(FakeGh(dependents=edited("dependents", hundred)), "100 or more")
        self.assertEqual([c for c in self.said if c.startswith("Retargeted")], [])

    def test_only_open_pull_requests_on_the_branch_are_moved(self):
        def mixed(data):
            stacked(data)
            data[1]["base"]["ref"] = "elsewhere"
        gh = FakeGh(dependents=edited("dependents", mixed))
        self.assertEqual(self.run_merge(gh), 0)
        self.assertIn(merge.build_retarget(REPO, 33, "main"), gh.calls)
        self.assertNotIn(merge.build_retarget(REPO, 34, "main"), gh.calls)


class RedirectTests(Helper):
    """No variable and no argument but the number changes which gh is called, on what, or with what words."""

    HOSTILE = {
        "GH_REPO": "attacker/fork", "GH_HOST": "evil.example.com", "WS_GH": "/tmp/fake-gh",
        "WS_MERGE_GH": "/tmp/fake-gh", "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "remote.origin.url",
        "GIT_CONFIG_VALUE_0": "git@github.com:attacker/fork.git",
        "GIT_CONFIG_PARAMETERS": "'remote.origin.url'='git@github.com:attacker/fork.git'",
        "GIT_DIR": "/nowhere", "GIT_CONFIG_GLOBAL": "/nowhere/config",
    }

    def test_the_repository_comes_from_the_repository_config_alone(self):
        environ = dict(os.environ, **self.HOSTILE)
        self.assertEqual(merge.repository(self.root, environ), REPO)

    def test_hostile_variables_change_no_call(self):
        calm, hostile = FakeGh(), FakeGh()
        self.assertEqual(merge.merge(self.root, NUMBER, call=calm, say=lambda _: None,
                                     update=lambda root: ("current", None)), 0)
        saved = dict(os.environ)
        try:
            os.environ.update(self.HOSTILE)
            self.assertEqual(merge.merge(self.root, NUMBER, call=hostile, say=lambda _: None,
                                         update=lambda root: ("current", None)), 0)
        finally:
            os.environ.clear()
            os.environ.update(saved)
        self.assertEqual(calm.calls, hostile.calls)
        self.assertTrue(all(call[0] == "gh" for call in hostile.calls))

    def test_gh_runs_without_the_variables_that_choose_its_repository(self):
        env = merge.gh_environment(dict(self.HOSTILE, PATH=os.environ.get("PATH", "")))
        self.assertNotIn("GH_REPO", env)
        self.assertNotIn("GH_HOST", env)
        self.assertEqual(env["GH_PROMPT_DISABLED"], "1")

    def test_the_command_takes_the_number_and_nothing_else(self):
        ws = [sys.executable, str(ROOT / "ws.py")]
        for extra in (["-R", "attacker/fork"], ["--repo", "attacker/fork"], ["--squash"], ["--admin"]):
            done = subprocess.run(ws + ["merge", "32", *extra], capture_output=True, text=True)
            self.assertEqual(done.returncode, 2, extra)
            self.assertIn("unrecognized arguments", done.stderr)
        done = subprocess.run(ws + ["merge", "abc"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 2)
        done = subprocess.run(ws + ["--root", str(self.root), "merge", "32"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 2)
        self.assertIn("cannot point it at another one", done.stderr)

    def test_a_local_origin_names_no_repository(self):
        git(self.root, "remote", "set-url", "origin", str(self.base / "bare.git"))
        with self.assertRaises(merge.MergeError):
            merge.repository(self.root)


class FastForwardTests(unittest.TestCase):
    """After the merge, the main working copy is brought up to date under the session-start conditions."""

    def setUp(self):
        self.base = pathlib.Path(os.path.realpath(tempfile.mkdtemp(prefix="merge-ff-")))
        self.addCleanup(shutil.rmtree, self.base, ignore_errors=True)
        self.bare = self.base / "origin.git"
        git(self.base, "init", "-q", "--bare", "-b", "main", str(self.bare))
        self.main = self.base / "main"
        git(self.base, "clone", "-q", str(self.bare), str(self.main))
        (self.main / "a.txt").write_text("one\n", encoding="utf-8")
        git(self.main, "add", "a.txt")
        self.commit(self.main, "start")
        git(self.main, "push", "-q", "origin", "main")
        self.linked = self.base / "linked"
        git(self.main, "worktree", "add", "-q", str(self.linked), "-b", "side")
        # GitHub's merge, as seen from here: origin/main moves on, and no working copy took part.
        other = self.base / "elsewhere"
        git(self.base, "clone", "-q", str(self.bare), str(other))
        (other / "b.txt").write_text("merged\n", encoding="utf-8")
        git(other, "add", "b.txt")
        self.commit(other, "the merge")
        git(other, "push", "-q", "origin", "main")
        self.merged = git_out(other, "rev-parse", "HEAD")
        self.start = git_out(self.main, "rev-parse", "HEAD")

    def commit(self, folder, message):
        git(folder, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", message)

    def hold(self, session, pid):
        (self.main / ".git" / leases.NAME).write_text(json.dumps({"session": session, "pid": pid, "taken": 1}),
                                                      encoding="utf-8")

    def head(self):
        return git_out(self.main, "rev-parse", "HEAD")

    def test_a_clean_main_with_the_lease_free_moves_from_a_worktree(self):
        outcome, note = leases.update_main(self.linked)
        self.assertEqual((outcome, note), ("moved", None))
        self.assertEqual(self.head(), self.merged)

    def test_while_another_live_session_holds_the_lease_it_is_skipped_with_a_note(self):
        self.hold("other-session", os.getpid())
        outcome, note = leases.update_main(self.linked, own_pid=None)
        self.assertEqual(outcome, "held")
        self.assertIn("Another live agent session (other-se)", note)
        self.assertEqual(self.head(), self.start)

    def test_the_merge_goes_ahead_and_the_fast_forward_is_skipped_with_a_note(self):
        self.hold("other-session", os.getpid())
        said = []
        root = self.linked
        git(root, "remote", "set-url", "origin", "git@github.com:ryantornberg/agent-ready-workspace.git")
        gh = FakeGh()
        self.assertEqual(merge.merge(root, NUMBER, call=gh, say=said.append,
                                     update=lambda r: leases.update_main(r, own_pid=None)), 0)
        self.assertEqual(gh.named("merge"), [merge.build_merge(REPO, NUMBER, HEAD)])
        self.assertIn("Did not bring the main working copy up to date. Another live agent session", "\n".join(said))
        self.assertEqual(self.head(), self.start)

    def test_the_callers_own_lease_does_not_hold_it_back(self):
        self.hold("this-session", os.getpid())
        self.assertEqual(leases.update_main(self.linked, own_pid=os.getpid())[0], "moved")
        self.assertEqual(self.head(), self.merged)

    def test_a_dead_holder_does_not_hold_it_back(self):
        dead = subprocess.Popen([sys.executable, "-c", "pass"])
        dead.wait()
        self.hold("gone-session", dead.pid)
        self.assertEqual(leases.update_main(self.linked)[0], "moved")

    def test_uncommitted_changes_are_left_alone_with_a_note(self):
        (self.main / "a.txt").write_text("edited\n", encoding="utf-8")
        outcome, note = leases.update_main(self.linked)
        self.assertEqual(outcome, "held")
        self.assertIn("uncommitted changes", note)
        self.assertEqual(self.head(), self.start)
        self.assertEqual((self.main / "a.txt").read_text(encoding="utf-8"), "edited\n")

    def test_another_branch_is_left_alone_with_a_note(self):
        git(self.main, "switch", "-q", "-c", "feature")
        outcome, note = leases.update_main(self.linked)
        self.assertEqual(outcome, "quiet")
        self.assertIn("on feature, not main", note)
        self.assertEqual(git_out(self.main, "rev-parse", "main"), self.start)

    def test_unpushed_commits_on_main_are_left_alone_with_a_note(self):
        (self.main / "c.txt").write_text("mine\n", encoding="utf-8")
        git(self.main, "add", "c.txt")
        self.commit(self.main, "a person's own commit")
        mine = self.head()
        outcome, note = leases.update_main(self.linked)
        self.assertEqual(outcome, "held")
        self.assertIn("a person's own commit", note)
        self.assertEqual(self.head(), mine)

    def test_the_session_start_fast_forward_keeps_its_behavior(self):
        self.hold("other-session", os.getpid())
        self.assertIn("Another live agent session", leases.fast_forward(self.main, str(self.main), "me"))
        self.assertIsNone(leases.fast_forward(self.main, str(self.linked), "me"))
        self.assertEqual(self.head(), self.start)
        self.assertIsNone(leases.fast_forward(self.main, str(self.main), "other-session"))
        self.assertEqual(self.head(), self.merged)


if __name__ == "__main__":
    unittest.main()
