"""M3 slice C5c: the git folder and git config (criterion 55, except the parts slices C5d and C5e hold).

The parts' own cases call each decide function with the facts filled in. These tests cover what the cases cannot:
the runner's `aliases` and `git_config` facts, worked out by git on throwaway repositories, and the messages a
person or an agent reads.
"""
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from wslib import gitcall, gitrules, shellfacts  # noqa: E402


def git(folder, *args):
    subprocess.run(["git", "-C", str(folder), *args], check=True, capture_output=True, env=gitcall.environment())


class Repository(unittest.TestCase):
    """A main working copy with a linked worktree, and a home folder of its own, so no test reads the machine's."""

    def setUp(self):
        self.base = pathlib.Path(os.path.realpath(tempfile.mkdtemp(prefix="gitfolder-")))
        self.addCleanup(shutil.rmtree, self.base, ignore_errors=True)
        self.home = self.base / "home"
        self.home.mkdir()
        environ = {"HOME": str(self.home), "GIT_CONFIG_NOSYSTEM": "1"}
        for name in ("XDG_CONFIG_HOME", "GIT_CONFIG_GLOBAL", "GIT_CONFIG_SYSTEM", "GIT_DIR", "GIT_WORK_TREE"):
            environ[name] = ""
        patcher = mock.patch.dict(os.environ, environ)
        patcher.start()
        self.addCleanup(patcher.stop)
        for name in ("XDG_CONFIG_HOME", "GIT_CONFIG_GLOBAL", "GIT_CONFIG_SYSTEM", "GIT_DIR", "GIT_WORK_TREE"):
            del os.environ[name]
        self.main = self.base / "main"
        self.main.mkdir()
        git(self.main, "init", "-q", "-b", "main")
        git(self.main, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "start")
        self.linked = self.base / "linked"
        git(self.main, "worktree", "add", "-q", str(self.linked), "-b", "side")


class AliasFactTests(Repository):
    def test_aliases_from_the_repository_and_the_home_config_are_read_at_hook_time(self):
        git(self.main, "config", "alias.rh", "reset --hard")
        (self.home / ".gitconfig").write_text("[alias]\n\tSt = status --short\n", encoding="utf-8")
        facts = shellfacts.aliases(self.main, "git rh && git st && git status", str(self.main))
        self.assertEqual(facts, {".": {"aliases": {"rh": "reset --hard", "st": "status --short"}}})

    def test_a_linked_worktree_reads_the_shared_config(self):
        git(self.main, "config", "alias.pu", "push origin HEAD")
        self.assertEqual(shellfacts.aliases(self.main, "git pu", str(self.linked))["."]["aliases"].get("pu"),
                         "push origin HEAD")

    def test_each_folder_is_read_on_its_own(self):
        other = self.base / "other"
        other.mkdir()
        git(other, "init", "-q")
        git(other, "config", "alias.x", "reset --hard")
        facts = shellfacts.aliases(self.main, f"git x; git -C {other.as_posix()} x", str(self.main))
        self.assertEqual(facts["."], {"aliases": {}})
        self.assertEqual(facts[other.as_posix()], {"aliases": {"x": "reset --hard"}})

    def test_only_calls_that_need_an_alias_start_git(self):
        with mock.patch.object(shellfacts, "_run", side_effect=AssertionError("git was started")):
            self.assertEqual(shellfacts.aliases(self.main, "git status && git push -u origin HEAD && ls",
                                                str(self.main)), {})

    def test_an_unplaceable_folder_gets_no_fact(self):
        self.assertEqual(shellfacts.aliases(self.main, 'git -C "$D" st', str(self.main)), {})

    def test_the_guard_expands_the_alias_it_was_given(self):
        git(self.main, "config", "alias.rh", "reset --hard")
        event = {"command": "git rh", "aliases": shellfacts.aliases(self.main, "git rh", str(self.main))}
        calls, why = gitrules.read(event)
        self.assertIsNone(why)
        self.assertEqual((calls[0]["git"]["subcommand"], calls[0]["git"]["args"]), ("reset", ["--hard"]))

    def test_folders_whose_aliases_differ_are_unresolved(self):
        event = {"command": "git x; git -C /o x",
                 "aliases": {".": {"aliases": {"x": "status"}}, "/o": {"aliases": {"x": "reset --hard"}}}}
        calls, why = gitrules.read(event)
        self.assertIn("aliases differ", why)
        self.assertIn("aliases differ", gitrules.unresolved(calls[0], why))


class ConfigFileFactTests(Repository):
    def test_the_global_files_count_whether_or_not_they_exist(self):
        facts = shellfacts.git_config(self.main, {"HOME": str(self.home)})
        home = self.home.as_posix()
        for name in (f"{home}/.gitconfig", f"{home}/.config/git/config"):
            self.assertIn(name, facts["files"])
        self.assertIsNone(facts["unresolved"])
        self.assertEqual(facts["home"], home)

    def test_the_system_file_counts(self):
        system = self.base / "etc" / "gitconfig"
        facts = shellfacts.git_config(self.main, {"HOME": str(self.home), "GIT_CONFIG_SYSTEM": str(system)})
        self.assertIn(system.as_posix(), facts["files"])

    def test_xdg_and_git_config_global_are_read_from_the_environment(self):
        xdg, global_file = self.base / "xdg", self.base / "g.cfg"
        facts = shellfacts.git_config(self.main, {"HOME": str(self.home), "XDG_CONFIG_HOME": str(xdg),
                                                  "GIT_CONFIG_GLOBAL": str(global_file)})
        self.assertIn((xdg / "git" / "config").as_posix(), facts["files"])
        self.assertIn(global_file.as_posix(), facts["files"])

    def test_every_include_counts_relative_home_and_conditional_existing_or_not(self):
        later = (self.base / "not-yet.inc").as_posix()
        (self.home / ".gitconfig").write_text(
            f"[include]\n\tpath = ~/work.inc\n[includeIf \"gitdir:/nowhere/\"]\n\tpath = {later}\n",
            encoding="utf-8")
        git(self.main, "config", "include.path", "../shared/team.gitconfig")
        facts = shellfacts.git_config(self.main, {"HOME": str(self.home)})
        files = [gitrules.fold(name) for name in facts["files"]]
        self.assertIn(gitrules.fold((self.home / "work.inc").as_posix()), files)
        self.assertIn(gitrules.fold(later), files)
        self.assertIn(gitrules.fold((self.main / ".git" / ".." / "shared" / "team.gitconfig").resolve().as_posix()),
                      files)

    def test_a_config_git_cannot_read_leaves_the_includes_unresolved(self):
        (self.main / ".git" / "config").write_text("[broken\n", encoding="utf-8")
        facts = shellfacts.git_config(self.main, {"HOME": str(self.home)})
        self.assertIn("could not read", facts["unresolved"])
        self.assertIn((self.home / ".gitconfig").as_posix(), facts["files"])

    @unittest.skipIf(os.name == "nt", "symbolic links need a privilege on Windows")
    def test_a_symbolic_link_counts_by_its_real_path_too(self):
        real = self.base / "dotfiles" / "gitconfig"
        real.parent.mkdir()
        real.write_text("[user]\n\tname = t\n", encoding="utf-8")
        (self.home / ".gitconfig").symlink_to(real)
        facts = shellfacts.git_config(self.main, {"HOME": str(self.home)})
        self.assertIn(real.as_posix(), facts["files"])

    def test_the_shell_guard_reads_the_facts_only_for_a_write(self):
        class Event(dict):
            def get(self, key, default=None):
                if key == "git_config":
                    raise AssertionError("the config facts were read")
                return dict.get(self, key, default)

        for command in ("git status", "ls -la && git log --oneline", "git status 2>/dev/null"):
            self.assertEqual(gitrules.shell_refusals(Event(command=command, cwd="/m")), [], command)


class MessageTests(unittest.TestCase):
    def test_a_stale_index_lock_tells_a_person_to_remove_it(self):
        why = gitrules.path_refusal(".git/index.lock", "/m/.git/index.lock", set())
        self.assertIn("person", why)
        self.assertIn("remove it", why)

    def test_a_git_folder_write_names_the_path_and_who_may_write_there(self):
        why = gitrules.path_refusal(".git/hooks/pre-commit", "/m/.git/hooks/pre-commit", set())
        self.assertIn(".git/hooks/pre-commit", why)
        self.assertIn("own terminal", why)

    def test_a_config_write_names_its_key(self):
        reasons = gitrules.shell_refusals({"command": "git config remote.origin.pushurl x", "cwd": "/m",
                                           "git_config": {"home": "/h", "files": []}})
        self.assertEqual(len(reasons), 1)
        self.assertIn("remote.origin.pushurl", reasons[0])

    def test_config_write_with_every_guarded_key_judges_the_alias_by_its_expansion(self):
        from wslib import shell
        push = next(c for c in shell.analyze("git -c alias.push=status push") if c.get("git"))
        self.assertIsNone(gitrules.config_write(push, every_guarded=True))
        redirected = next(c for c in shell.analyze("git -c remote.origin.pushurl=x push") if c.get("git"))
        self.assertIsNone(gitrules.config_write(redirected))
        self.assertIn("remote.origin.pushurl", gitrules.config_write(redirected, every_guarded=True))


if __name__ == "__main__":
    unittest.main()
