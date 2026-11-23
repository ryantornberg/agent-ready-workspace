"""M3 slice C5e: the outward-write guard on real git (criteria 39, 55 and 65).

Each test builds a throwaway repository with a local bare remote and sets its config with `git config`, as a
person would, and writes the list of repositories beside it. The runner works the facts out from that repository
as it does for a real hook call (wslib/runner.py, `shell_event`), and the part decides on them. The parts' own
cases give the facts by hand; these show the facts git really gives lead to the same answers.
"""
import json
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

from wslib import gitcall, gitrules, runner, shellfacts  # noqa: E402
from parts import outward_list, outward_write  # noqa: E402

LIST = "outward-repos.json"


def git(folder, *args):
    return subprocess.run(["git", "-C", str(folder), *args], check=True, capture_output=True,
                          env=gitcall.environment()).stdout.decode().strip()


class Repository(unittest.TestCase):
    """A repository on `feature` with a local bare remote `origin`, and a list naming github.com/me/ours."""

    def setUp(self):
        self.base = pathlib.Path(os.path.realpath(tempfile.mkdtemp(prefix="outward-")))
        self.addCleanup(shutil.rmtree, self.base, ignore_errors=True)
        self.remote = self.base / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", str(self.remote)], check=True, capture_output=True,
                       env=gitcall.environment())
        self.repo = self.base / "work"
        self.repo.mkdir()
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "start")
        git(self.repo, "remote", "add", "origin", self.remote.as_posix())
        git(self.repo, "switch", "-q", "-c", "feature")
        self.write_list(["github.com/me/ours"])

    def write_list(self, entries):
        (self.repo / LIST).write_text(json.dumps({"repositories": entries}), encoding="utf-8")

    def event(self, command):
        cwd = self.repo.as_posix()
        hooks = [types.SimpleNamespace(module=outward_write, config={"list": LIST})]
        return runner.shell_event(self.repo, {"command": command, "cwd": cwd, "session": "s-this"}, hooks,
                                  "claude-code", cwd)

    def refused(self, command):
        return outward_write.decide(self.event(command), {"list": LIST})

    def assertRefused(self, command, *texts):
        why = self.refused(command)
        self.assertIsNotNone(why, command)
        for text in texts:
            self.assertIn(text, why, command)

    def assertPasses(self, command):
        self.assertIsNone(self.refused(command), command)


class PushTests(Repository):
    def test_a_local_remote_passes_and_an_unlisted_url_is_refused(self):
        self.assertPasses("git push -u origin HEAD")
        self.assertPasses("git push")
        self.assertPasses(f"git push {self.remote.as_posix()} HEAD")
        self.assertPasses(f"git push file://{self.remote.as_posix()} HEAD")
        self.assertRefused("git push git@github.com:them/theirs.git HEAD", "github.com/them/theirs")
        self.assertRefused("git push https://github.com/them/theirs HEAD", "github.com/them/theirs")
        self.assertPasses("git push git@github.com:me/ours.git HEAD")

    def test_where_config_sends_the_push_decides(self):
        git(self.repo, "remote", "set-url", "--push", "origin", "git@github.com:them/theirs.git")
        self.assertRefused("git push origin HEAD", "github.com/them/theirs")
        self.assertRefused("git push", "github.com/them/theirs")
        git(self.repo, "remote", "set-url", "--push", "origin", "git@github.com:me/ours.git")
        self.assertPasses("git push origin HEAD")
        git(self.repo, "remote", "set-url", "--add", "--push", "origin", "https://github.com/them/theirs")
        self.assertRefused("git push origin HEAD", "github.com/them/theirs")

    def test_insteadof_and_pushinsteadof(self):
        git(self.repo, "config", "url.git@github.com:them/.insteadOf", "x:")
        self.assertRefused("git push x:theirs HEAD", "github.com/them/theirs")
        git(self.repo, "config", f"url.git@github.com:them/theirs.git.pushInsteadOf", self.remote.as_posix())
        self.assertRefused("git push origin HEAD", "github.com/them/theirs")

    def test_pushinsteadof_applies_to_a_url_on_the_command_line(self):
        """The instruction review's finding: git rewrites a typed URL with pushInsteadOf for a push."""
        git(self.repo, "config", "url.https://github.com/them/.pushInsteadOf", "../")
        self.assertRefused(f"git push ../{self.remote.name} HEAD", "github.com/them/")
        self.assertRefused(f"git push --dry-run ../{self.remote.name} HEAD" + " && git push ../x HEAD")

    def test_a_nested_group_is_matched_by_its_whole_path(self):
        self.write_list(["gitlab.com/team/app"])
        git(self.repo, "remote", "add", "lab", "https://gitlab.com/team/app.git")
        git(self.repo, "remote", "add", "near", "https://gitlab.com/othergroup/team/app.git")
        self.assertPasses("git push lab HEAD")
        self.assertRefused("git push near HEAD", "gitlab.com/othergroup/team/app")

    def test_submodules_pushed_on_demand_are_refused(self):
        self.assertRefused("git push --recurse-submodules=on-demand origin HEAD", "submodule")
        self.assertRefused("git push --recurse=on-demand origin HEAD", "submodule")
        self.assertRefused("git -c submodule.recurse=true push origin HEAD", "submodule")
        self.assertPasses("git push --recurse-submodules=check origin HEAD")

    def test_a_remote_that_does_not_exist_yet_is_refused(self):
        """The re-check's finding: a remote made earlier in the line, here by a clone, read as a local path."""
        self.assertRefused("git clone https://github.com/them/theirs t && git -C t push", "does not exist yet")
        self.assertRefused("git push upstream HEAD", "no remote named upstream")
        self.assertPasses(f"git push {self.remote.as_posix()} HEAD")

    def test_push_default_and_push_remote(self):
        git(self.repo, "remote", "add", "up", "https://github.com/them/theirs.git")
        git(self.repo, "config", "remote.pushDefault", "up")
        self.assertRefused("git push", "github.com/them/theirs")
        self.assertPasses("git push origin HEAD")
        git(self.repo, "config", "--unset", "remote.pushDefault")
        git(self.repo, "config", "branch.feature.pushRemote", "up")
        self.assertRefused("git push", "github.com/them/theirs")

    def test_a_stored_alias_is_judged_as_the_push_it_runs(self):
        git(self.repo, "config", "alias.pu", "push git@github.com:them/theirs.git HEAD")
        git(self.repo, "config", "alias.po", "push -u origin HEAD")
        self.assertRefused("git pu", "github.com/them/theirs")
        self.assertPasses("git po")
        self.assertRefused("git -c alias.push=status push git@github.com:them/theirs.git HEAD")

    def test_config_written_on_the_push_is_refused(self):
        self.assertRefused("git -c remote.origin.pushurl=git@github.com:me/ours.git push origin HEAD")
        self.assertRefused("HOME=/tmp git push origin HEAD")
        self.assertRefused("GIT_CONFIG_GLOBAL=/tmp/x git push origin HEAD")

    def test_the_destinations_fact_agrees_with_the_targets_fact(self):
        git(self.repo, "remote", "add", "up", "https://github.com/them/theirs.git")
        git(self.repo, "remote", "set-url", "--add", "--push", "up", "git@github.com:me/ours.git")
        git(self.repo, "config", "url.git@github.com:them/.insteadOf", "x:")
        for command in ("git push -u origin HEAD", "git push up HEAD", "git push x:theirs HEAD", "git push",
                        "git push --all origin", f"git push {self.remote.as_posix()} HEAD"):
            cwd = self.repo.as_posix()
            targets = shellfacts.targets(self.repo, command, cwd)
            found = shellfacts.destinations(self.repo, command, cwd)
            self.assertEqual(set(targets), set(found), command)
            for key, fact in found.items():
                self.assertEqual(fact["destinations"], targets[key]["destinations"], command)


class RemoteTests(Repository):
    def test_remote_add_and_set_url(self):
        self.assertRefused("git remote add up git@github.com:them/theirs.git", "github.com/them/theirs")
        self.assertRefused("git remote set-url origin https://github.com/them/theirs", "github.com/them/theirs")
        self.assertRefused("git remote set-url --push origin them:theirs")
        self.assertPasses("git remote add mine https://github.com/me/ours.git")
        self.assertPasses(f"git remote add copy {self.remote.as_posix()}")
        self.assertPasses("git remote set-url --delete origin x")
        self.assertRefused("git remote add up git@github.com:me/ours.git && git push up HEAD", "one at a time")


class GhTests(Repository):
    def test_the_target_gh_would_use(self):
        git(self.repo, "remote", "set-url", "origin", "https://github.com/me/ours.git")
        self.assertPasses("gh pr create --fill")
        self.assertRefused("gh pr create --fill -R them/theirs", "github.com/them/theirs")
        self.assertRefused("GH_REPO=them/theirs gh pr create --fill", "github.com/them/theirs")
        self.assertRefused("GH_REPO=me/ours gh api repos/them/theirs/issues -f title=x", "github.com/them/theirs")
        self.assertPasses("gh api repos/{owner}/{repo}/issues -f title=x")
        self.assertPasses("gh pr view 5 -R them/theirs")
        self.assertRefused("gh pr review 5 --approve", "approve")
        self.assertRefused("gh api graphql -f query='query { viewer { login } }'", "graphql")

    def test_two_remotes_and_no_default_leave_a_write_unresolved(self):
        git(self.repo, "remote", "set-url", "origin", "https://github.com/me/ours.git")
        git(self.repo, "remote", "add", "up", "https://github.com/them/theirs.git")
        self.assertRefused("gh pr create --fill", "cannot be judged")
        self.assertPasses("gh pr list")
        git(self.repo, "config", "remote.up.gh-resolved", "base")
        self.assertRefused("gh pr create --fill", "github.com/them/theirs")
        git(self.repo, "config", "--unset", "remote.up.gh-resolved")
        git(self.repo, "config", "remote.origin.gh-resolved", "base")
        self.assertPasses("gh pr create --fill")


class ListTests(Repository):
    def test_a_missing_or_broken_list_lists_nothing(self):
        git(self.repo, "remote", "set-url", "origin", "https://github.com/me/ours.git")
        (self.repo / LIST).unlink()
        found = shellfacts.repositories(self.repo, LIST)
        self.assertEqual(found["repositories"], [])
        self.assertIn("does not exist", found["unresolved"])
        self.assertRefused("gh pr create --fill", "does not exist")
        for text in ("not json", '{"repositories": "github.com/me/ours"}', '{"repositories": ["me/ours"]}',
                     '{"repositories": ["github.com/me/ours", 3]}'):
            (self.repo / LIST).write_text(text, encoding="utf-8")
            found = shellfacts.repositories(self.repo, LIST)
            self.assertEqual(found["repositories"], [], text)
            self.assertTrue(found["unresolved"], text)
            self.assertRefused("gh pr create --fill")
        self.write_list([])
        self.assertRefused("git push -u origin HEAD", "github.com/me/ours")
        self.assertPasses(f"git push {self.remote.as_posix()} HEAD")

    def test_this_workspace_list_is_well_formed(self):
        found = shellfacts.repositories(ROOT, LIST)
        self.assertIsNone(found["unresolved"])
        self.assertTrue(found["repositories"])
        entries = [entry for entry in json.loads((ROOT / "workspace.json").read_text(encoding="utf-8"))["parts"]
                   if entry.get("use") in ("outward_write", "outward_list")]
        self.assertEqual(sorted(entry["use"] for entry in entries), ["outward_list", "outward_write"])
        self.assertEqual({entry.get("list") for entry in entries}, {LIST})

    def test_an_edit_and_a_shell_write_to_the_list_are_refused(self):
        self.assertIsNotNone(outward_list.decide({"path": LIST, "absolute": (self.repo / LIST).as_posix()},
                                                 {"list": LIST}))
        self.assertRefused(f"echo '{{}}' > {LIST}", "list of repositories")
        self.assertRefused(f"sed -i.bak s/me/them/ {LIST}", "list of repositories")
        self.assertPasses(f"cat {LIST}")

    def test_listed_ignores_case_and_needs_an_owner(self):
        repositories = [{"host": "github.com", "owner": "me", "name": "ours"}]
        self.assertTrue(gitrules.listed({"host": "GitHub.com", "owner": "Me", "name": "OURS"}, repositories))
        self.assertFalse(gitrules.listed({"host": "github.com", "owner": None, "name": None}, repositories))
        self.assertFalse(gitrules.listed({"local": True, "path": "x"}, repositories))


if __name__ == "__main__":
    unittest.main()
