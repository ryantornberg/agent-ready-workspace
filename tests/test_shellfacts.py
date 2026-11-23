"""M3 slice C3a: the facts the runner adds to a before-shell event (decision 0004, "Shell events"; criterion 58).

Each fact is worked out on real throwaway repositories: the kind of working copy each git call acts on, for every
way a command names its folder; the folders the parser leaves unresolved; the session; and the lease holder.
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from wslib import gitcall, shellfacts  # noqa: E402


def git(folder, *args):
    subprocess.run(["git", "-C", str(folder), *args], check=True, capture_output=True, env=gitcall.environment())


class Repositories(unittest.TestCase):
    """A main working copy, a linked worktree of it, and an unrelated repository."""

    def setUp(self):
        self.base = pathlib.Path(os.path.realpath(tempfile.mkdtemp(prefix="shellfacts-")))
        self.addCleanup(shutil.rmtree, self.base, ignore_errors=True)
        self.main = self.base / "main"
        self.main.mkdir()
        git(self.main, "init", "-q", "-b", "main")
        git(self.main, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "start")
        self.linked = self.base / "linked"
        git(self.main, "worktree", "add", "-q", str(self.linked), "-b", "side")
        self.other = self.base / "other"
        self.other.mkdir()
        git(self.other, "init", "-q")

    def facts(self, command, cwd):
        return shellfacts.working_copies(self.main, command, str(cwd))

    def kind(self, command, cwd, key):
        fact = self.facts(command, cwd).get(key)
        self.assertIsNotNone(fact, f"no fact for {key!r} in {command!r}")
        return fact.get("kind"), fact.get("top")


class KindTests(Repositories):
    def test_the_session_folder_alone(self):
        self.assertEqual(self.kind("git reset --hard", self.main, "."), ("main", self.main.as_posix()))
        self.assertEqual(self.kind("git reset --hard", self.linked, "."), ("linked", self.linked.as_posix()))
        self.assertEqual(self.kind("git reset --hard", self.other, ".")[0], "other")

    def test_dash_c(self):
        self.assertEqual(self.kind(f"git -C {self.main.as_posix()} reset --hard", self.linked, self.main.as_posix())[0], "main")
        self.assertEqual(self.kind("git -C ../linked stash drop", self.main, "../linked")[0], "linked")

    def test_git_dir_option_and_variable(self):
        target = f"{self.main.as_posix()}/.git"
        self.assertEqual(self.kind(f"git --git-dir={target} reset --hard", self.linked, target)[0], "main")
        self.assertEqual(self.kind(f"GIT_DIR={target} git clean -fdx", self.linked, target)[0], "main")
        linked_dir = f"{self.main.as_posix()}/.git/worktrees/linked"
        self.assertEqual(self.kind(f"GIT_DIR={linked_dir} git status", self.main, linked_dir)[0], "linked")

    def test_work_tree_option_and_variable(self):
        self.assertEqual(self.kind(f"git --work-tree={self.main.as_posix()} reset --hard", self.linked, self.main.as_posix())[0], "main")
        self.assertEqual(self.kind(f"GIT_WORK_TREE={self.main.as_posix()} git reset --hard", self.linked, self.main.as_posix())[0], "main")

    def test_a_leading_cd_and_pushd(self):
        self.assertEqual(self.kind(f"cd {self.main.as_posix()} && git reset --hard", self.linked, self.main.as_posix())[0], "main")
        self.assertEqual(self.kind(f"cd {self.main.as_posix()}; git reset --hard", self.linked, self.main.as_posix())[0], "main")
        self.assertEqual(self.kind(f"pushd {self.main.as_posix()} && git reset --hard", self.linked, self.main.as_posix())[0], "main")

    def test_a_worktree_remove_operand_is_keyed(self):
        facts = self.facts("git worktree remove --force ../linked", self.main)
        key = "./../linked"     # the operand joined to the call's folder, as the guard joins it
        self.assertEqual(facts[key]["kind"], "linked")
        self.assertEqual(facts[key]["top"], self.linked.as_posix())

    def test_a_folder_that_does_not_exist_is_in_no_repository(self):
        self.assertEqual(self.kind("git -C nowhere reset --hard", self.main, "nowhere")[0], "other")

    def test_a_relative_folder_without_the_session_folder_is_unresolved(self):
        facts = shellfacts.working_copies(self.main, "git reset --hard", None)
        self.assertIn("unresolved", facts["."])

    def test_git_that_does_not_answer_is_unresolved(self):
        original = shellfacts.TIMEOUT
        shellfacts.TIMEOUT = 0.000001
        try:
            fact = self.facts("git reset --hard", self.main)["."]
        finally:
            shellfacts.TIMEOUT = original
        self.assertEqual(fact, {"unresolved": "git did not answer in time"})


class OneCallTests(Repositories):
    """Slice TFIX: inside one hook call, each folder's git folders are asked of git once."""

    def lookups(self, work):
        calls = []
        original = subprocess.run

        def counted(args, *rest, **options):
            if "--git-common-dir" in args:
                calls.append(args)
            return original(args, *rest, **options)
        with mock.patch.object(shellfacts.subprocess, "run", counted):
            work()
        return len(calls)

    def push_facts(self):
        shellfacts.own_working_copy(str(self.linked))
        shellfacts.working_copies(self.main, "git push origin HEAD", str(self.linked))
        return shellfacts._branches(["-C", str(self.linked)])

    def test_the_same_folder_is_asked_once_within_a_call(self):
        def inside():
            with shellfacts.one_call():
                self.assertEqual(self.push_facts(), ("side", "main"))
        self.assertEqual(self.lookups(inside), 1)

    def test_outside_a_call_every_lookup_asks_git(self):
        self.assertEqual(self.lookups(self.push_facts), 3)
        self.assertIsNone(shellfacts._FOLDERS)

    def test_a_timeout_is_kept_as_a_timeout(self):
        original = shellfacts.TIMEOUT
        shellfacts.TIMEOUT = 0.000001
        try:
            with shellfacts.one_call():
                self.assertEqual(shellfacts.working_copies(self.main, "git status", str(self.main))["."],
                                 {"unresolved": "git did not answer in time"})
                with self.assertRaises(TimeoutError):
                    shellfacts._branches(["-C", str(self.main)])
        finally:
            shellfacts.TIMEOUT = original


class UnresolvedTests(Repositories):
    """Criterion 58: these leave the folder unresolved, so no fact is given and the guard refuses."""

    def test_each_form_leaves_no_fact(self):
        for command in [f"echo hi; cd {self.main.as_posix()}; git reset --hard", f"(cd {self.main.as_posix()} && git reset --hard)",
                        f"git -c core.worktree={self.main.as_posix()} reset --hard", "GIT_INDEX_FILE=/tmp/i git reset --hard",
                        f"GIT_COMMON_DIR={self.main.as_posix()}/.git git reset --hard", 'cd "$D" && git reset --hard']:
            with self.subTest(command):
                self.assertEqual(self.facts(command, self.linked), {}, command)


class SessionAndLeaseTests(Repositories):
    def write_lease(self, session, pid):
        (self.main / ".git" / "ws-lease.json").write_text(json.dumps({"session": session, "pid": pid, "taken": time.time()}))

    def test_the_session(self):
        found = shellfacts.session({"session": "me", "pid": 42}, None, str(self.linked))
        self.assertEqual(found, {"session": "me", "pid": 42, "cwd": str(self.linked),
                                 "own_working_copy": self.linked.as_posix()})
        found = shellfacts.session({"session": "me", "pid": None}, "claude-code", None)
        self.assertIsNone(found["own_working_copy"])

    def test_the_lease_states(self):
        self.assertEqual(shellfacts.lease(self.main, "me")["state"], "free")
        self.write_lease("me", 999999)
        self.assertEqual(shellfacts.lease(self.main, "me")["state"], "mine")
        self.write_lease("other", os.getpid())
        found = shellfacts.lease(self.linked, "me")
        self.assertEqual((found["state"], found["holder"]["session"]), ("other-live", "other"))
        dead = subprocess.Popen([sys.executable, "-c", "pass"])
        dead.wait()
        self.write_lease("other", dead.pid)
        self.assertEqual(shellfacts.lease(self.main, "me")["state"], "other-dead")
        (self.main / ".git" / "ws-lease.json").write_text("{not json")
        self.assertEqual(shellfacts.lease(self.main, "me")["state"], "unknown")

    def test_reading_the_lease_never_writes_it(self):
        self.write_lease("other", os.getpid())
        before = (self.main / ".git" / "ws-lease.json").read_text()
        shellfacts.lease(self.main, "me")
        self.assertEqual((self.main / ".git" / "ws-lease.json").read_text(), before)



class LazyFactsTests(unittest.TestCase):
    """The facts that need git are worked out only when a hook reads them, so the discard guard with the lease
    free, held by this session or by a dead one starts no git process (criterion 28's budget)."""

    def test_a_quiet_lease_reads_no_git_fact(self):
        from parts import no_discard
        from wslib.runner import LazyEvent

        def boom():
            raise AssertionError("a git fact was worked out")
        for state in ("free", "mine", "other-dead"):
            event = LazyEvent({"command": "git reset --hard", "lease": {"state": state}},
                              {"working_copies": boom, "own_working_copy": boom})
            self.assertIsNone(no_discard.decide(event, {}))

    def test_a_held_lease_reads_them_once(self):
        from parts import no_discard
        from wslib.runner import LazyEvent
        calls = []

        def copies():
            calls.append(1)
            return {".": {"kind": "main", "top": "/m"}}
        event = LazyEvent({"command": "git reset --hard && git clean -fdx", "lease": {"state": "other-live"}},
                          {"working_copies": copies, "own_working_copy": lambda: "/m"})
        self.assertIsNotNone(no_discard.decide(event, {}))
        self.assertEqual(event.get("working_copies"), {".": {"kind": "main", "top": "/m"}})
        self.assertEqual(calls, [1])


class TargetTests(Repositories):
    """Criterion 58's target repository, from each source (decision 0004, "Shell events")."""

    def setUp(self):
        super().setUp()
        git(self.main, "remote", "add", "origin", "https://github.com/acme/workspace.git")

    def target(self, command, cwd=None, environ=None):
        facts = shellfacts.targets(self.main, command, (cwd or self.main).as_posix(), environ=environ or {})
        self.assertEqual(len(facts), 1, facts)
        return next(iter(facts.values()))

    def repos(self, fact):
        self.assertIsNone(fact["unresolved"], fact)
        return [(d.get("host"), d.get("owner"), d.get("name")) if not d.get("local") else ("local", d["path"])
                for d in fact["destinations"]]

    def test_the_key_is_the_folder_and_the_words(self):
        from wslib import shell
        call = next(c for c in shell.analyze("cd /x && gh pr list -R a/b") if c.get("gh"))
        self.assertEqual(shellfacts.target_key(call), '["/x", "gh", ["pr", "list", "-R", "a/b"]]')

    def test_gh_repo_flag_and_variable(self):
        self.assertEqual(self.repos(self.target("gh pr create -R octo/one")), [("github.com", "octo", "one")])
        self.assertEqual(self.repos(self.target("gh pr create --repo octo/one")), [("github.com", "octo", "one")])
        self.assertEqual(self.repos(self.target("GH_REPO=octo/two gh pr merge 3")), [("github.com", "octo", "two")])
        self.assertEqual(self.repos(self.target("gh pr merge 3", environ={"GH_REPO": "octo/three"})),
                         [("github.com", "octo", "three")])

    def test_gh_set_default_then_the_only_remote(self):
        self.assertEqual(self.repos(self.target("gh pr list")), [("github.com", "acme", "workspace")])
        git(self.main, "remote", "add", "upstream", "git@github.com:octo/upstream.git")
        fact = self.target("gh pr create")
        self.assertEqual(fact["destinations"], [])
        self.assertIn("two or more remotes", fact["unresolved"])
        git(self.main, "config", "remote.upstream.gh-resolved", "base")
        self.assertEqual(self.repos(self.target("gh pr create")), [("github.com", "octo", "upstream")])

    def test_gh_folder_follows_the_parser(self):
        git(self.other, "remote", "add", "origin", "https://github.com/octo/other.git")
        self.assertEqual(self.repos(self.target(f"cd {self.other.as_posix()} && gh pr list")),
                         [("github.com", "octo", "other")])

    def test_gh_api_literal_path_and_placeholders(self):
        fact = self.target("gh api repos/octo/n/issues -f title=x", environ={"GH_REPO": "acme/workspace"})
        self.assertEqual(self.repos(fact), [("github.com", "octo", "n")])
        self.assertEqual(self.repos(self.target("gh api repos/{owner}/{repo}/pulls -f title=x",
                                                environ={"GH_REPO": "octo/filled"})), [("github.com", "octo", "filled")])
        self.assertEqual(self.repos(self.target("gh api repos/{owner}/{repo}/pulls -f title=x")),
                         [("github.com", "acme", "workspace")])

    def test_gh_with_no_repository(self):
        for command in ["gh api user", "gh gist create notes.md", "gh api graphql -f query=x"]:
            with self.subTest(command):
                fact = self.target(command)
                self.assertTrue(fact["no_repository"], fact)
                self.assertEqual(fact["destinations"], [])

    def test_gh_repository_operand(self):
        self.assertEqual(self.repos(self.target("gh repo view octo/r")), [("github.com", "octo", "r")])

    def test_push_with_no_refspec_follows_push_default_and_the_upstream(self):
        fact = self.target("git push")
        self.assertEqual(self.repos(fact), [("github.com", "acme", "workspace")])
        self.assertEqual(fact["remote"], "origin")
        self.assertEqual(fact["refspecs"], [{"src": "refs/heads/main", "dst": "refs/heads/main", "force": False}])
        git(self.main, "checkout", "-q", "-b", "topic")
        git(self.main, "config", "branch.topic.remote", "origin")
        git(self.main, "config", "branch.topic.merge", "refs/heads/main")
        fact = self.target("git -c push.default=upstream push -f")
        self.assertEqual(fact["refspecs"], [{"src": "refs/heads/topic", "dst": "refs/heads/main", "force": False}])
        self.assertIn("matching", self.target("git -c push.default=matching push")["unresolved"])

    def test_push_urls_and_rewrites_come_from_git(self):
        git(self.main, "config", "remote.origin.pushurl", "https://github.com/acme/a.git")
        git(self.main, "config", "--add", "remote.origin.pushurl", "git@github.com:acme/b.git")
        self.assertEqual(self.repos(self.target("git push origin main")),
                         [("github.com", "acme", "a"), ("github.com", "acme", "b")])
        git(self.main, "config", "--unset-all", "remote.origin.pushurl")
        fact = self.target("git -c url.https://github.com/octo/.pushInsteadOf=https://github.com/acme/ push origin main")
        self.assertEqual(self.repos(fact), [("github.com", "octo", "workspace")])
        env_form = ("GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=remote.origin.pushurl "
                    "GIT_CONFIG_VALUE_0=https://github.com/octo/env.git git push origin main")
        self.assertEqual(self.repos(self.target(env_form)), [("github.com", "octo", "env")])
        git(self.main, "config", "remote.pushDefault", "upstream")
        git(self.main, "remote", "add", "upstream", "https://github.com/octo/up.git")
        self.assertEqual(self.repos(self.target("git push")), [("github.com", "octo", "up")])

    def test_push_config_from_an_included_file(self):
        extra = self.base / "extra.config"
        extra.write_text('[remote "origin"]\n\tpushurl = https://github.com/octo/included.git\n')
        git(self.main, "config", "include.path", extra.as_posix())
        self.assertEqual(self.repos(self.target("git push origin main")), [("github.com", "octo", "included")])

    def test_a_url_on_the_command_line_gets_insteadof_only(self):
        git(self.main, "config", "url.https://github.com/octo/.insteadOf", "gh:")
        git(self.main, "config", "url.https://github.com/evil/.pushInsteadOf", "https://github.com/acme/")
        self.assertEqual(self.repos(self.target("git push gh:thing.git HEAD:main")), [("github.com", "octo", "thing")])
        self.assertEqual(self.repos(self.target("git push https://github.com/acme/x.git HEAD:main")),
                         [("github.com", "acme", "x")])

    def test_local_and_ssh_destinations(self):
        self.assertEqual(self.repos(self.target("git push ../bare.git main")), [("local", "../bare.git")])
        self.assertEqual(self.repos(self.target("git push file:///srv/bare.git main")), [("local", "/srv/bare.git")])
        self.assertEqual(self.repos(self.target("git push example.com:octo/x.git main")), [("example.com", "octo", "x")])

    def test_a_mirror_remote_and_configured_push_refspecs(self):
        git(self.main, "config", "remote.origin.mirror", "true")
        self.assertTrue(self.target("git push")["mirror"])
        git(self.main, "config", "--unset", "remote.origin.mirror")
        git(self.main, "config", "remote.origin.push", "+refs/heads/*:refs/heads/*")
        self.assertEqual(self.target("git push")["refspecs"],
                         [{"src": "refs/heads/*", "dst": "refs/heads/*", "force": True}])

    def test_what_is_not_modelled_is_unresolved(self):
        for command in ["HOME=/tmp git push", 'git push "$R" main', "git push origin \"$(git branch --show-current)\"",
                        'git -c "$K"=x push', 'cd "$D" && git push']:
            with self.subTest(command):
                self.assertTrue(self.target(command)["unresolved"], command)


if __name__ == "__main__":
    unittest.main()
