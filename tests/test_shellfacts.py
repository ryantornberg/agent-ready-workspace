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


if __name__ == "__main__":
    unittest.main()
