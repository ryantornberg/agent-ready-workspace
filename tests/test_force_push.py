"""M3 slice C5d: the force-push guard, the push guard's worktree extension and the git folder guard's aliases, on
real git (criteria 36, 38, 55 and 65).

Each test builds a throwaway repository with a local bare remote and sets its config with `git config`, as a
person would. The runner works the facts out from that repository as it does for a real hook call
(wslib/runner.py, `shell_event`), and the part decides on them. The parts' own cases give the facts by hand; these
show the facts git really gives lead to the same answers.
"""
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import types
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from wslib import gitcall, runner, shellfacts  # noqa: E402
from parts import git_folder_shell, no_force_push, push_lease  # noqa: E402


def git(folder, *args):
    return subprocess.run(["git", "-C", str(folder), *args], check=True, capture_output=True,
                          env=gitcall.environment()).stdout.decode().strip()


def commit(folder, message):
    git(folder, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", message)


class Repository(unittest.TestCase):
    """A repository on main with a branch `feature`, and a bare remote `origin` that has both."""

    def setUp(self):
        self.base = pathlib.Path(os.path.realpath(tempfile.mkdtemp(prefix="force-push-")))
        self.addCleanup(shutil.rmtree, self.base, ignore_errors=True)
        self.remote = self.base / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", str(self.remote)], check=True, capture_output=True,
                       env=gitcall.environment())
        self.other = self.base / "other.git"
        subprocess.run(["git", "init", "-q", "--bare", str(self.other)], check=True, capture_output=True,
                       env=gitcall.environment())
        self.repo = self.base / "work"
        self.repo.mkdir()
        git(self.repo, "init", "-q", "-b", "main")
        commit(self.repo, "start")
        git(self.repo, "remote", "add", "origin", self.remote.as_posix())
        git(self.repo, "branch", "feature")
        git(self.repo, "push", "-q", "origin", "main", "feature")
        git(self.repo, "switch", "-q", "feature")

    def event(self, command, part, cwd=None, lease=None):
        cwd = (cwd or self.repo).as_posix()
        hooks = [types.SimpleNamespace(module=part)]
        event = runner.shell_event(self.repo, {"command": command, "cwd": cwd, "session": "s-this"}, hooks,
                                   "claude-code", cwd)
        if lease is not None:
            event["lease"] = lease
        return event

    def refused(self, command, cwd=None):
        return no_force_push.decide(self.event(command, no_force_push, cwd), {})

    def assertRefused(self, command, cwd=None):
        self.assertIsNotNone(self.refused(command, cwd), command)

    def assertPasses(self, command, cwd=None):
        self.assertIsNone(self.refused(command, cwd), command)


class ForcePushTests(Repository):
    def test_the_written_forms(self):
        for command in ("git push -f origin main", "git push --force origin main", "git push origin +main",
                        "git push --force-with-lease origin main", "git push -f origin feature:main",
                        "git push --all -f origin", "git push --branches --force origin", "git push --mirror origin",
                        "git push --delete origin main", "git push origin :main",
                        "git push --prune origin 'refs/heads/*:refs/heads/*'",
                        "git push -f origin 'refs/heads/*:refs/heads/*'",
                        "echo main | xargs git push -f origin"):
            self.assertRefused(command)

    def test_head_while_on_main(self):
        git(self.repo, "switch", "-q", "main")
        self.assertRefused("git push -f origin HEAD")
        self.assertRefused("git push -f")

    def test_the_allowed_forms(self):
        for command in ("git push --force-with-lease origin feature", "git push -f origin feature",
                        "git push -u origin HEAD", "git push origin main", "git push --all origin",
                        "git push -f", "git push --dry-run -f origin main"):
            self.assertPasses(command)

    def test_pushurl_redirect(self):
        git(self.repo, "remote", "add", "scratch", (self.base / "nowhere").as_posix())
        git(self.repo, "config", "remote.scratch.pushurl", self.other.as_posix())
        fact = next(iter(shellfacts.targets(self.repo, "git push -f scratch main", self.repo.as_posix()).values()))
        self.assertEqual([d.get("path") for d in fact["destinations"]], [self.other.as_posix()])
        self.assertRefused("git push -f scratch main")
        self.assertPasses("git push -f scratch feature")

    def test_insteadof_and_pushinsteadof_redirects(self):
        git(self.repo, "config", f"url.{self.other.as_posix()}.insteadOf", "mirror:")
        self.assertRefused("git push -f mirror:x main")
        git(self.repo, "config", f"url.{self.other.as_posix()}.pushInsteadOf", self.remote.as_posix())
        fact = next(iter(shellfacts.targets(self.repo, "git push -f origin main", self.repo.as_posix()).values()))
        self.assertEqual([d.get("path") for d in fact["destinations"]], [self.other.as_posix()])
        self.assertRefused("git push -f origin main")
        self.assertPasses("git push -f origin feature")

    def test_git_config_variables_on_the_push(self):
        self.assertRefused("GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=remote.origin.pushurl "
                           f"GIT_CONFIG_VALUE_0={self.other.as_posix()} git push origin feature")

    def test_push_default_upstream_sends_a_bare_push_to_main(self):
        git(self.repo, "branch", "-q", "-u", "origin/main")
        git(self.repo, "config", "push.default", "upstream")
        self.assertRefused("git push -f")
        self.assertPasses("git push")

    def test_two_pushurls(self):
        git(self.repo, "config", "--add", "remote.origin.pushurl", self.remote.as_posix())
        git(self.repo, "config", "--add", "remote.origin.pushurl", self.other.as_posix())
        fact = next(iter(shellfacts.targets(self.repo, "git push -f origin main", self.repo.as_posix()).values()))
        self.assertEqual(len(fact["destinations"]), 2)
        self.assertRefused("git push -f origin main")
        self.assertPasses("git push -f origin feature")

    def test_push_default_matching_from_a_feature_branch(self):
        git(self.repo, "config", "push.default", "matching")
        self.assertRefused("git push -f")

    def test_a_configured_remote_push_refspec(self):
        git(self.repo, "config", "remote.origin.push", "+refs/heads/feature:refs/heads/main")
        self.assertRefused("git push origin")
        self.assertRefused("git push")

    def test_a_configured_mirror(self):
        git(self.repo, "config", "remote.origin.mirror", "true")
        self.assertRefused("git push origin")

    def test_earlier_in_the_line(self):
        for command in (f"git branch -u origin/main && git push -f",
                        "git switch -q -c other --track origin/main && git push -f",
                        "git checkout main && git push -f",
                        f"git remote add backup {self.other.as_posix()} && git push -f backup feature",
                        "gh repo set-default o/r && git push -f origin feature",
                        f"git worktree add -b x {(self.base / 'w').as_posix()} origin/main && git push -f"):
            self.assertRefused(command)
        self.assertPasses("git switch -q -c fresh && git push -u origin fresh")

    def test_stored_aliases(self):
        git(self.repo, "config", "alias.fp", "push -f origin main")
        git(self.repo, "config", "alias.pb", "push origin feature")
        self.assertRefused("git fp")
        self.assertPasses("git pb")

    def test_an_alias_in_a_file_global_config_names(self):
        extra = self.base / "extra.cfg"
        extra.write_text("[alias]\n\tfp = push -f origin main\n", encoding="utf-8")
        self.assertRefused(f"GIT_CONFIG_GLOBAL={extra.as_posix()} git fp")

    def test_unresolved_commands(self):
        for command in ('git push origin "$(git branch --show-current)"', '$G push -f origin main',
                        "echo 'git push -f origin main' | sh", 'cd "$D" && git push'):
            self.assertRefused(command)
        self.assertIn("git push -u origin HEAD", self.refused('git push origin "$(git branch --show-current)"'))
        git(self.repo, "switch", "-q", "main")
        git(self.repo, "switch", "-q", "feature")
        self.assertRefused("git push -f origin @{-1}")
        self.assertPasses('cd "$D" && make')


class WorktreePushTests(Repository):
    """Criterion 36 as amended: while another live session holds the lease, a push from a linked worktree that
    sends the main copy's branch, every branch, a mirror or a glob is refused; its own branch passes."""

    HELD = {"state": "other-live", "holder": {"session": "other", "pid": 1, "taken": 0}, "file": None}

    def setUp(self):
        super().setUp()
        git(self.repo, "switch", "-q", "main")
        self.tree = self.base / "tree"
        git(self.repo, "worktree", "add", "-q", "-b", "side", self.tree.as_posix())

    def decide(self, command, lease=None):
        return push_lease.decide(self.event(command, push_lease, self.tree, lease or self.HELD), {})

    def test_what_the_main_copy_shares_is_refused(self):
        for command in ("git push origin main", "git push --all origin", "git push --branches origin",
                        "git push --mirror origin", "git push origin 'refs/heads/*:refs/heads/*'"):
            self.assertIsNotNone(self.decide(command), command)

    def test_a_switch_to_the_main_copy_s_branch_earlier_in_the_line(self):
        self.assertIsNotNone(self.decide("git switch -q --ignore-other-worktrees main && git push"))
        self.assertIsNotNone(self.decide("git push origin 'main@{0}:refs/heads/x'"))
        self.assertIsNotNone(self.decide(
            "git switch -q --ignore-other-worktrees main && git push origin 'HEAD@{0}:refs/heads/y'"))
        self.assertIsNotNone(self.decide("git push origin '@{-1}:refs/heads/y'"))
        self.assertIsNone(self.decide("git switch -q -c fresh && git push -u origin fresh"))

    def test_the_worktree_s_own_branch_passes(self):
        for command in ("git push -u origin HEAD", "git push origin side"):
            self.assertIsNone(self.decide(command), command)

    def test_a_free_lease_passes(self):
        self.assertIsNone(self.decide("git push origin main", {"state": "free", "holder": None, "file": None}))


class GitFolderAliasTests(Repository):
    """Q16 and Q17: core.hooksPath, and a stored alias that runs git config."""

    def decide(self, command):
        return git_folder_shell.decide(self.event(command, git_folder_shell), {})

    def test_core_hooks_path(self):
        self.assertIsNotNone(self.decide("git config core.hooksPath /tmp/nohooks"))
        self.assertIsNone(self.decide("git -c core.hooksPath=/tmp/nohooks status"))
        self.assertIsNotNone(self.decide("git config --remove-section core"))

    def test_a_stored_alias_to_git_config(self):
        git(self.repo, "config", "alias.cf", "config")
        self.assertIsNotNone(self.decide("git cf remote.origin.url URL"))
        self.assertIsNone(self.decide("git cf user.email a@example.com"))

    def test_an_alias_set_through_global_config_or_home(self):
        extra = self.base / "extra.cfg"
        extra.write_text("[alias]\n\tcf2 = config\n", encoding="utf-8")
        home = self.base / "home"
        home.mkdir()
        (home / ".gitconfig").write_text("[alias]\n\tcf2 = config\n", encoding="utf-8")
        self.assertIsNotNone(self.decide(f"GIT_CONFIG_GLOBAL={extra.as_posix()} git cf2 remote.origin.url URL"))
        self.assertIsNotNone(self.decide(f"HOME={home.as_posix()} git cf2 remote.origin.url URL"))


if __name__ == "__main__":
    unittest.main()
