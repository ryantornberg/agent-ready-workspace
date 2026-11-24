"""Tests for the shared shell parser, wslib/shell.py (M3 slice A0).

One case per command form the A0 row of the M3 plan lists, and per parser fact criteria 55 and 58 name. These test
what the parser reports, not what a guard decides on it: the guards (slices C3 and C5) come later.

Run: python3 -m unittest discover -b tests
"""
import json
import pathlib
import sys
import types
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from wslib import shell  # noqa: E402


def commands(line, **kw):
    return shell.analyze(line, **kw)


def find(line, program, nth=0, **kw):
    """The nth command running `program` in the line."""
    found = [c for c in commands(line, **kw) if c["program"] == program]
    assert len(found) > nth, f"no {program} #{nth} in {line!r}: {[c['program'] for c in commands(line, **kw)]}"
    return found[nth]


def git(line, nth=0, **kw):
    return find(line, "git", nth, **kw)["git"]


def push(line, **kw):
    return git(line, **kw)["push"]


def gh(line, nth=0, **kw):
    return find(line, "gh", nth, **kw)["gh"]


def writes(line):
    return [(w["path"], w["via"]) for c in commands(line) for w in c["writes"]]


def guarded_writes(line):
    return [w for c in commands(line) for w in c["config_writes"] if w["guarded"]]


class EnvironmentDumpTests(unittest.TestCase):
    """A0: `env` and `printenv` as commands."""

    def test_env_alone_is_a_command(self):
        self.assertEqual(find("env", "env")["args"], [])

    def test_env_with_only_options_is_a_command(self):
        self.assertEqual(find("env -0", "env")["args"], ["-0"])

    def test_printenv_is_a_command(self):
        self.assertEqual(find("printenv GH_TOKEN", "printenv")["args"], ["GH_TOKEN"])

    def test_env_in_front_of_a_command_is_a_wrapper(self):
        found = commands("env GH_PROMPT_DISABLED=1 gh pr list")
        self.assertEqual([c["program"] for c in found], ["gh"])
        self.assertEqual(found[0]["env"], {"GH_PROMPT_DISABLED": "1"})
        self.assertEqual(found[0]["wrappers"], ["env"])


class ProgramTests(unittest.TestCase):
    """The program, its arguments, wrappers and assignments."""

    def test_program_by_full_path_and_exe(self):
        self.assertEqual(find("/usr/bin/git status", "git")["args"], ["status"])
        self.assertEqual(find("git.exe status", "git")["args"], ["status"])

    def test_wrappers_are_unwrapped_and_listed(self):
        found = find("sudo -u me timeout -s KILL 5s nice -n 3 git push", "git")
        self.assertEqual(found["wrappers"], ["sudo", "timeout", "nice"])
        self.assertEqual(found["git"]["subcommand"], "push")

    def test_assignment_on_the_command(self):
        self.assertEqual(find("X=1 Y=$Z git status", "git")["env"], {"X": "1", "Y": "$Z"})
        self.assertEqual(find("X=1 Y=$Z git status", "git")["env_dynamic"], ["Y"])

    def test_env_assignment_unset_and_clear(self):
        self.assertEqual(find("env -u HOME X=1 git status", "git")["env"], {"HOME": None, "X": "1"})
        cleared = find("A=1 env -i B=2 git status", "git")
        self.assertTrue(cleared["env_cleared"])
        self.assertEqual(cleared["env"], {"B": "2"})

    def test_export_carries_to_later_commands(self):
        self.assertEqual(find("export GIT_DIR=/x; git status", "git")["env"], {"GIT_DIR": "/x"})

    def test_command_v_runs_nothing(self):
        self.assertEqual([c["program"] for c in commands("command -v git")], ["command"])

    def test_echo_of_git_is_not_git(self):
        self.assertEqual([c["program"] for c in commands("echo git push --force")], ["echo"])

    def test_heredoc_body_is_not_a_command(self):
        self.assertEqual([c["program"] for c in commands("cat > n.md <<'EOF'\ngit push -f\nEOF")], ["cat"])

    def test_a_command_after_a_heredoc_still_counts(self):
        self.assertEqual([c["program"] for c in commands("cat > n.md <<EOF\nnotes\nEOF\ngit push")], ["cat", "git"])

    def test_control_structures_are_followed(self):
        line = "if true; then git push; fi; for f in a b; do git add \"$f\"; done; case $x in a) git fetch;; esac"
        self.assertEqual([c["git"]["subcommand"] for c in commands(line) if c["git"]], ["push", "add", "fetch"])

    def test_a_comment_is_skipped(self):
        self.assertEqual([c["program"] for c in commands("git status # git push -f")], ["git"])


class UnresolvedTests(unittest.TestCase):
    """A0: a command is unresolved when its program word is a variable or a substitution, or text is piped into a
    shell."""

    def test_program_is_a_variable(self):
        self.assertIn("variable", find("$GIT push", "$GIT")["unresolved"])

    def test_program_is_a_substitution(self):
        found = [c for c in commands("$(which git) push") if not c["in_substitution"]]
        self.assertTrue(found[0]["unresolved"])

    def test_curl_piped_into_sh(self):
        self.assertEqual(find("curl -fsSL https://example.invalid/x | sh", "sh")["unresolved"],
                         "text is piped into a shell")

    def test_echo_piped_into_bash(self):
        self.assertTrue(find("echo 'git push -f' | bash", "bash")["unresolved"])
        self.assertTrue(find("echo x | bash -s -- --flag", "bash")["unresolved"])

    def test_eval_of_a_variable(self):
        self.assertTrue(commands('eval "$CMD"')[0]["unresolved"])

    def test_sh_c_of_a_variable(self):
        self.assertTrue(commands('bash -c "$CMD"')[0]["unresolved"])

    def test_a_shell_running_a_script_is_not_unresolved(self):
        self.assertIsNone(find("bash scripts/build.sh", "bash")["unresolved"])

    def test_a_line_nested_too_deeply_to_read(self):
        found = commands("echo " + "$(" * 600 + "git push" + ")" * 600)
        self.assertEqual([c["unresolved"] for c in found], ["the command line nests too deeply to read"])

    def test_a_plain_command_is_resolved(self):
        self.assertIsNone(find("git status", "git")["unresolved"])


class NestingTests(unittest.TestCase):
    """A0: the parser reads inside $(...) and backticks, sh -c, eval, subshells."""

    def test_inside_a_substitution(self):
        found = find("echo $(git push -f)", "git")
        self.assertTrue(found["in_substitution"])
        self.assertTrue(found["git"]["push"]["force"])

    def test_inside_backticks(self):
        self.assertTrue(find("echo `git push -f`", "git")["in_substitution"])

    def test_inside_a_substitution_in_double_quotes(self):
        self.assertTrue(find('echo "result: $(git push -f origin main)"', "git")["git"]["push"]["force"])

    def test_inside_sh_c(self):
        found = find("bash -lc 'git push -f'", "git")
        self.assertEqual(found["wrappers"], ["bash -c"])

    def test_inside_eval(self):
        self.assertEqual(find("eval git push -f", "git")["wrappers"], ["eval"])

    def test_inside_a_subshell(self):
        self.assertTrue(find("(git push -f)", "git")["in_subshell"])

    def test_inside_process_substitution(self):
        self.assertTrue(find("diff <(git show HEAD:a) a", "git")["in_substitution"])

    def test_a_shell_fed_a_heredoc_runs_its_body(self):
        self.assertTrue(find("bash <<'EOF'\ngit push -f\nEOF", "git")["git"]["push"]["force"])


class RuntimeArgumentTests(unittest.TestCase):
    """A0: find -exec, -execdir and xargs as wrappers whose supplied arguments are unresolved."""

    def test_xargs(self):
        found = find("git branch --format='%(refname)' | xargs git push origin --delete", "git", 1)
        self.assertEqual(found["runtime_args"], "xargs")
        self.assertEqual(found["git"]["subcommand"], "push")

    def test_xargs_with_options(self):
        self.assertEqual(find("ls | xargs -I {} -n 1 git add {}", "git")["runtime_args"], "xargs")

    def test_find_exec(self):
        found = find("find . -name '*.py' -exec git add {} \\;", "git")
        self.assertEqual(found["runtime_args"], "find -exec")
        self.assertEqual(found["wrappers"], ["find -exec"])

    def test_find_exec_plus(self):
        self.assertEqual(find("find . -type f -exec git add {} +", "git")["runtime_args"], "find -exec")

    def test_find_execdir(self):
        found = find("find . -name x -execdir git push -f \\;", "git")
        self.assertIsNone(found["runtime_args"])
        self.assertIsNone(found["git"]["folder"])

    def test_find_exec_git_from_criterion_55(self):
        self.assertEqual(git("find . -exec git push --force {} \\;")["subcommand"], "push")


class PushTests(unittest.TestCase):
    """A0: git push to a remote or a URL; + and : refspecs; --mirror; -f and --force in every form."""

    def test_push_to_a_remote(self):
        self.assertEqual(push("git push origin main")["remote"], "origin")

    def test_push_to_a_url(self):
        self.assertEqual(push("git push https://github.com/o/r.git HEAD:main")["remote"],
                         "https://github.com/o/r.git")

    def test_plus_refspec(self):
        spec = push("git push origin +main")["refspecs"][0]
        self.assertEqual((spec["src"], spec["dst"], spec["force"]), ("main", None, True))

    def test_colon_refspec(self):
        spec = push("git push origin HEAD:refs/heads/main")["refspecs"][0]
        self.assertEqual((spec["src"], spec["dst"], spec["force"], spec["delete"]),
                         ("HEAD", "refs/heads/main", False, False))

    def test_delete_refspec(self):
        self.assertTrue(push("git push origin :main")["refspecs"][0]["delete"])

    def test_glob_refspec(self):
        self.assertTrue(push("git push origin 'refs/heads/*:refs/heads/*'")["refspecs"][0]["glob"])

    def test_mirror(self):
        self.assertTrue(push("git push --mirror origin")["mirror"])

    def test_force_short(self):
        self.assertTrue(push("git push -f origin main")["force"])

    def test_force_in_a_cluster(self):
        self.assertTrue(push("git push -uf origin main")["force"])

    def test_force_long(self):
        self.assertTrue(push("git push --force origin main")["force"])

    def test_force_abbreviated_is_ambiguous(self):
        self.assertEqual(push("git push --forc origin main")["unknown_options"], ["--forc"])

    def test_no_force_resets(self):
        self.assertFalse(push("git push -f --no-force origin main")["force"])

    def test_force_with_lease(self):
        self.assertEqual(push("git push --force-with-lease origin x")["force_with_lease"], [""])
        self.assertEqual(push("git push --force-with-lease=x:abc origin x")["force_with_lease"], ["x:abc"])

    def test_force_if_includes(self):
        self.assertTrue(push("git push --force-with-lease --force-if-includes origin x")["force_if_includes"])

    def test_all_branches_delete_prune_tags(self):
        for flag, field in (("--all", "all"), ("--branches", "branches"), ("--delete", "delete"), ("-d", "delete"),
                            ("--prune", "prune"), ("--tags", "tags"), ("--follow-tags", "follow_tags")):
            with self.subTest(flag):
                self.assertTrue(push(f"git push {flag} origin")[field])

    def test_set_upstream(self):
        self.assertTrue(push("git push -u origin HEAD")["set_upstream"])

    def test_repo_option(self):
        self.assertEqual(push("git push --repo=upstream")["remote"], "upstream")

    def test_a_substituted_refspec_is_dynamic(self):
        found = find('git push origin "$(git branch --show-current)"', "git", 1)
        self.assertTrue(found["git"]["push"]["refspecs"][0]["dynamic"])
        self.assertEqual(found["dynamic_args"], [2])
        self.assertIsNone(found["unresolved"])

    def test_a_variable_remote_is_dynamic(self):
        self.assertTrue(push('git push "$REMOTE" main')["remote_dynamic"])

    def test_push_options_take_their_value(self):
        found = push("git push -o ci.skip origin main")
        self.assertEqual((found["remote"], [s["src"] for s in found["refspecs"]]), ("origin", ["main"]))


class GitGlobalOptionTests(unittest.TestCase):
    """A0: the subcommand after global options."""

    def test_subcommand_after_global_options(self):
        found = git("git --no-pager -C app -c core.pager=cat --git-dir=.git --namespace ns push origin")
        self.assertEqual(found["subcommand"], "push")
        self.assertEqual(found["config"][0]["key"], "core.pager")

    def test_a_variable_subcommand(self):
        self.assertTrue(git('git "$SUB" origin')["unresolved"])

    def test_no_subcommand(self):
        self.assertIsNone(git("git --version")["subcommand"])


class FolderTests(unittest.TestCase):
    """Criterion 58: the folder a git call acts on, from each source, and what leaves it unresolved."""

    def test_no_change(self):
        self.assertEqual(git("git status")["folder"], ".")

    def test_dash_C(self):
        self.assertEqual(git("git -C src/orders-api status")["folder"], "src/orders-api")

    def test_repeated_dash_C_composes(self):
        self.assertEqual(git("git -C src -C orders-api status")["folder"], "src/orders-api")
        self.assertEqual(git("git -C src -C /abs status")["folder"], "/abs")

    def test_git_dir(self):
        self.assertEqual(git("git --git-dir=src/x/.git status")["folder"], "src/x/.git")
        self.assertEqual(git("git --git-dir src/x/.git status")["git_dir"], "src/x/.git")

    def test_work_tree(self):
        self.assertEqual(git("git --work-tree=../wt status")["folder"], "../wt")

    def test_GIT_DIR(self):
        self.assertEqual(git("GIT_DIR=/r/.git git status")["folder"], "/r/.git")

    def test_GIT_WORK_TREE(self):
        self.assertEqual(git("GIT_WORK_TREE=wt git status")["folder"], "wt")

    def test_git_dir_is_placed_after_dash_C(self):
        self.assertEqual(git("git -C src --git-dir=.git status")["folder"], "src/.git")

    def test_leading_cd(self):
        self.assertEqual(git("cd src/orders-api && git push")["folder"], "src/orders-api")

    def test_leading_cd_first_of_the_line(self):
        self.assertEqual(git("cd app; git push")["folder"], "app")

    def test_leading_cd_composes_with_dash_C(self):
        self.assertEqual(git("cd src && git -C orders-api push")["folder"], "src/orders-api")

    def test_leading_pushd(self):
        self.assertEqual(git("pushd src/orders-api && git push")["folder"], "src/orders-api")

    def test_leading_cd_starting_an_and_chain(self):
        self.assertEqual(git("echo hi; cd app && git push")["folder"], "app")

    def test_a_cd_that_is_not_leading(self):
        found = git("make && cd app && git push")
        self.assertIsNone(found["folder"])
        self.assertIn("not the leading", found["folder_unresolved"])

    def test_a_second_cd(self):
        self.assertIsNone(git("cd a && cd b && git push")["folder"])

    def test_a_chain_cd_after_its_chain(self):
        self.assertIsNone(git("echo hi; cd app && make; git push")["folder"])

    def test_a_cd_in_a_subshell(self):
        found = git("(cd app && git push)")
        self.assertIsNone(found["folder"])
        self.assertIn("subshell", found["folder_unresolved"])

    def test_a_cd_in_a_subshell_leaves_the_outer_folder(self):
        self.assertEqual(git("(cd app && make); git push")["folder"], ".")

    def test_a_cd_to_a_variable(self):
        self.assertIsNone(git('cd "$D" && git push')["folder"])

    def test_a_variable_dash_C(self):
        self.assertIsNone(git('git -C "$D" push')["folder"])

    def test_core_worktree_by_dash_c(self):
        self.assertIsNone(git("git -c core.worktree=/x status")["folder"])

    def test_core_worktree_by_config_earlier(self):
        found = commands("git config core.worktree /x && git status")
        self.assertIsNone(found[1]["git"]["folder"])

    def test_core_worktree_by_the_environment(self):
        self.assertIsNone(git("GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.worktree GIT_CONFIG_VALUE_0=/x git status")
                          ["folder"])

    def test_GIT_INDEX_FILE(self):
        self.assertIsNone(git("GIT_INDEX_FILE=/tmp/i git add a")["folder"])

    def test_GIT_COMMON_DIR(self):
        self.assertIsNone(git("GIT_COMMON_DIR=/r/.git git status")["folder"])

    def test_env_dash_C(self):
        self.assertEqual(git("env -C app git status")["folder"], "app")


class DynamicDirectoryTests(unittest.TestCase):
    """A0 and criterion 55: `cd "$D" && make` gives a guard nothing to decide on."""

    def test_cd_variable_then_make(self):
        found = commands('cd "$D" && make')
        self.assertEqual([c["program"] for c in found], ["cd", "make"])
        self.assertFalse([c for c in found if c["git"] or c["gh"] or c["unresolved"] or c["writes"]
                          or c["config_writes"]])


class ConfigWriteTests(unittest.TestCase):
    """A0: git -c, git config and GIT_CONFIG_* or GIT_CONFIG_PARAMETERS writes to each guarded key."""

    KEYS = ("remote.origin.url", "url.https://x/.insteadOf", "push.default", "branch.main.pushRemote",
            "branch.main.merge", "remote.pushDefault", "include.path", "includeIf.gitdir:~/w/.path", "alias.p",
            "core.worktree", "core.sshCommand")

    def test_each_key_by_dash_c(self):
        for key in self.KEYS:
            with self.subTest(key):
                found = guarded_writes(f"git -c {key}=x status")
                self.assertEqual([(w["key"], w["via"]) for w in found], [(key, "git -c")])

    def test_each_key_by_git_config(self):
        for key in self.KEYS:
            with self.subTest(key):
                found = guarded_writes(f"git config {key} x")
                self.assertEqual([(w["key"], w["value"], w["op"]) for w in found], [(key, "x", "set")])

    def test_each_key_by_GIT_CONFIG_COUNT(self):
        for key in self.KEYS:
            with self.subTest(key):
                found = guarded_writes(f"GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0={key} GIT_CONFIG_VALUE_0=x git status")
                self.assertEqual([(w["key"], w["via"]) for w in found], [(key, "GIT_CONFIG_COUNT")])

    def test_each_key_by_GIT_CONFIG_PARAMETERS(self):
        for key in self.KEYS:
            with self.subTest(key):
                found = guarded_writes(f"GIT_CONFIG_PARAMETERS=\"'{key}=x'\" git status")
                self.assertEqual([(w["key"], w["via"]) for w in found], [(key, "GIT_CONFIG_PARAMETERS")])

    def test_case_of_section_and_variable_does_not_hide_a_key(self):
        self.assertTrue(guarded_writes("git -c REMOTE.origin.URL=x status"))
        self.assertTrue(guarded_writes("git -c Branch.main.PushRemote=x status"))

    def test_an_unguarded_key_is_reported_but_not_guarded(self):
        found = [w for c in commands("git -c core.pager=cat log") for w in c["config_writes"]]
        self.assertEqual([(w["key"], w["guarded"]) for w in found], [("core.pager", False)])

    def test_git_config_set_forms(self):
        for line in ("git config --global remote.origin.url x", "git config --add remote.o.url x",
                     "git config --replace-all remote.o.url x", "git config set remote.o.url x",
                     "git config --unset remote.o.url", "git config unset remote.o.url",
                     "git config --remove-section remote.o", "git config --rename-section remote.o remote.p",
                     "git config --edit", "git config -f .git/config remote.o.url x"):
            with self.subTest(line):
                self.assertTrue(guarded_writes(line))

    def test_git_config_reads_write_nothing(self):
        for line in ("git config remote.origin.url", "git config --get remote.origin.url", "git config --list",
                     "git config get remote.origin.url", "git config -l"):
            with self.subTest(line):
                self.assertEqual([w for c in commands(line) for w in c["config_writes"]], [])

    def test_git_config_file_is_a_write(self):
        self.assertIn((".git/config", "git config --file"), writes("git config --file .git/config a.b c"))

    def test_a_dynamic_count_is_an_unknown_write(self):
        found = guarded_writes('GIT_CONFIG_COUNT="$N" git status')
        self.assertEqual([w["key"] for w in found], [None])

    def test_an_environment_write_reaches_any_command(self):
        self.assertTrue(guarded_writes("GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=alias.p GIT_CONFIG_VALUE_0=push make"))

    def test_keys_guarded_only_for_a_persistent_write(self):
        """M3 slice Z, from C5d's and C5e's queues: core.hooksPath and submodule.recurse, which wslib/gitrules.py
        listed itself until now."""
        for line in ("git config core.hooksPath /tmp/x", "git config --global core.hookspath /tmp/x",
                     "git config set CORE.HOOKSPATH /tmp/x", "git config --unset core.hooksPath",
                     "git config submodule.recurse true", "git config --global submodule.recurse true"):
            with self.subTest(line):
                self.assertEqual(len(guarded_writes(line)), 1)
        for line in ("git -c core.hooksPath=/tmp/x status", "git -c submodule.recurse=true status",
                     "GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.hooksPath GIT_CONFIG_VALUE_0=x git status",
                     "git config core.hooksPath", "git config submodule.x.recurse true", "git config core.pager cat"):
            with self.subTest(line):
                self.assertEqual(guarded_writes(line), [])

    def test_a_section_removed_or_renamed(self):
        """M3 slice Z, from C5d's queue: the parser reports a renamed section's new name, and judges a rename or a
        removal by the keys the section holds or will hold."""
        def section_writes(line):
            return [(w["op"], w["key"], w.get("new_key"), w["guarded"]) for c in commands(line)
                    for w in c["config_writes"]]
        cases = {
            "git config --rename-section hooks core": [("rename-section", "hooks", "core", True)],
            "git config rename-section staged remote.origin": [("rename-section", "staged", "remote.origin", True)],
            "git config --rename-section x submodule": [("rename-section", "x", "submodule", True)],
            "git config --rename-section remote.o remote.p": [("rename-section", "remote.o", "remote.p", True)],
            "git config --rename-section old new": [("rename-section", "old", "new", False)],
            'git config --rename-section old "$N"': [("rename-section", "old", None, True)],
            "git config --rename-section old": [("rename-section", "old", None, True)],
            "git config --remove-section core": [("remove-section", "core", None, True)],
            "git config --remove-section alias": [("remove-section", "alias", None, True)],
            "git config remove-section remote.origin": [("remove-section", "remote.origin", None, True)],
            "git config --remove-section color": [("remove-section", "color", None, False)],
        }
        for line, expected in cases.items():
            with self.subTest(line):
                self.assertEqual(section_writes(line), expected)


class EnvironmentTests(unittest.TestCase):
    """A0 and criterion 55: GIT_SSH, GIT_SSH_COMMAND; HOME and the config-file variables on a git command."""

    def test_ssh_variables(self):
        self.assertEqual(find("GIT_SSH_COMMAND='ssh -i k' git push", "git")["ssh_env"], ["GIT_SSH_COMMAND"])
        self.assertEqual(find("GIT_SSH=/bin/x git push", "git")["ssh_env"], ["GIT_SSH"])

    def test_config_affecting_variables(self):
        for name in ("HOME", "XDG_CONFIG_HOME", "GIT_CONFIG_GLOBAL", "GIT_CONFIG_SYSTEM", "GIT_CONFIG_NOSYSTEM"):
            with self.subTest(name):
                self.assertEqual(find(f"{name}=/tmp/x git push", "git")["config_env"], [name])

    def test_home_cleared_by_env_i(self):
        self.assertEqual(find("env -i git push", "git")["config_env"], ["HOME"])


class RemoteTests(unittest.TestCase):
    """A0: git remote add and set-url, with the URL."""

    def test_remote_add(self):
        self.assertEqual(git("git remote add -f up https://github.com/o/r.git")["remote"],
                         {"action": "add", "name": "up", "url": "https://github.com/o/r.git", "push": False,
                          "dynamic": False})

    def test_remote_set_url(self):
        found = git("git remote set-url --push origin git@github.com:o/r.git")["remote"]
        self.assertEqual((found["action"], found["url"], found["push"]), ("set-url", "git@github.com:o/r.git", True))


class DiscardTests(unittest.TestCase):
    """A0: the forms the discard guard decides on."""

    CASES = {
        "git switch -f main": "switch --force", "git switch --discard-changes main": "switch --force",
        "git checkout -f main": "checkout --force", "git checkout --force main": "checkout --force",
        "git read-tree -u --reset HEAD": "read-tree --reset -u", "git reset --keep HEAD~1": "reset --keep",
        "git reset --hard": "reset --hard", "git rebase --autostash main": "autostash",
        "git -c rebase.autoStash=true rebase main": "autostash", "git pull --rebase --autostash": "autostash",
        "git -c rebase.autostash=true pull --rebase": "autostash", "git merge --autostash x": "autostash",
        "git stash drop": "stash drop", "git stash pop": "stash pop", "git stash clear": "stash clear",
        "git worktree remove ../wt": "worktree remove", "git worktree remove --force ../wt": "worktree remove --force",
        "git worktree prune": "worktree prune", "git clean -fd": "clean --force",
        # M3 slice Z, from C3a's queue: the forms the discard guard handled in its own file until now.
        "git checkout .": "whole-tree checkout", "git checkout -- .": "whole-tree checkout",
        "git checkout HEAD -- :/": "whole-tree checkout", "git checkout main -- '*'": "whole-tree checkout",
        "git checkout ../..": "whole-tree checkout", "git checkout --pathspec-from-file=list": "whole-tree checkout",
        "git checkout --pathspec-from-file list main": "whole-tree checkout",
        "git restore .": "whole-tree restore", "git restore --source=HEAD~1 :/": "whole-tree restore",
        "git restore -s HEAD ./": "whole-tree restore", "git restore --staged --worktree .": "whole-tree restore",
        "git restore -SW .": "whole-tree restore", "git restore --pathspec-from-file=list": "whole-tree restore",
        "git stash": "stash write", "git stash -m wip": "stash write", "git stash push -u": "stash write",
        "git stash save wip": "stash write", "git stash store abc123": "stash write",
        "git rebase main": "rebase", "git rebase --autostash --no-autostash main": "rebase",
        "git cherry-pick abc123": "cherry-pick", "git cp x": "cherry-pick",
    }

    def test_each_form(self):
        for line, expected in self.CASES.items():
            with self.subTest(line):
                self.assertIn(expected, git(line, aliases={"cp": "cherry-pick"})["discard"])

    def test_safe_forms_drop_nothing(self):
        for line in ("git switch main", "git checkout main", "git reset HEAD a.py", "git stash list",
                     "git stash show", "git stash apply abc123", "git worktree list", "git read-tree HEAD",
                     "git checkout -- a.py", "git checkout main -- src/", "git checkout -b . main",
                     "git restore a.py", "git restore --staged .", "git restore -S :/", "git restore -s . a.py",
                     "git checkout ./a", "git rebase-x"):
            with self.subTest(line):
                self.assertEqual(git(line)["discard"], [])

    def test_stash_action_defaults_to_push(self):
        self.assertEqual(git("git stash -m wip")["action"], "push")

    def test_pull_rebase(self):
        self.assertTrue(git("git pull -r")["pull_rebase"])
        self.assertTrue(git("git -c pull.rebase=true pull")["pull_rebase"])
        self.assertFalse(git("git pull --rebase=false")["pull_rebase"])

    def test_tracking(self):
        for line in ("git branch -u origin/x", "git branch --set-upstream-to=origin/x", "git switch -t origin/x",
                     "git checkout --track origin/x"):
            with self.subTest(line):
                self.assertTrue(git(line)["tracking"])


class GitAliasTests(unittest.TestCase):
    """A0 and criterion 55: git aliases as git expands them."""

    def test_a_builtin_cannot_be_aliased(self):
        found = git("git -c alias.push=status push origin main")
        self.assertEqual(found["subcommand"], "push")
        self.assertIsNone(found["alias"])

    def test_an_alias_by_dash_c_expands(self):
        found = git("git -c alias.foo=push foo origin +main")
        self.assertEqual((found["subcommand"], found["alias"]["source"]), ("push", "-c"))
        self.assertTrue(found["push"]["refspecs"][0]["force"])

    def test_an_alias_with_its_own_arguments(self):
        found = git("git -c 'alias.pf=push --force' pf origin main")
        self.assertTrue(found["push"]["force"])

    def test_a_shell_alias_is_unresolved(self):
        self.assertIn("shell", git("git -c 'alias.x=!git push -f' x")["unresolved"])

    def test_a_stored_alias_expands(self):
        found = git("git pf origin main", aliases={"pf": "push --force"})
        self.assertEqual((found["subcommand"], found["alias"]["source"]), ("push", "config"))
        self.assertTrue(found["push"]["force"])

    def test_a_stored_alias_that_pushes_a_branch(self):
        found = git("git pb", aliases={"pb": "push origin HEAD"})
        self.assertEqual(found["push"]["refspecs"][0]["src"], "HEAD")
        self.assertFalse(found["push"]["force"])

    def test_a_stored_alias_never_shadows_a_builtin(self):
        self.assertEqual(git("git push", aliases={"push": "status"})["subcommand"], "push")

    def test_neither_builtin_nor_alias_with_aliases_known(self):
        self.assertIn("neither", git("git frobnicate", aliases={})["unresolved"])

    def test_neither_builtin_nor_alias_with_aliases_not_known(self):
        found = git("git frobnicate")
        self.assertEqual((found["builtin"], found["unresolved"]), (False, None))

    def test_alias_chain_and_loop(self):
        self.assertEqual(git("git a", aliases={"a": "b", "b": "push"})["subcommand"], "push")
        self.assertIn("itself", git("git a", aliases={"a": "b", "b": "a"})["unresolved"])

    def test_an_alias_that_changes_the_environment(self):
        self.assertTrue(git("git a", aliases={"a": "-C /x push"})["unresolved"])

    def test_the_builtin_list_is_reasonably_complete(self):
        for name in ("add", "push", "commit", "stash", "worktree", "switch", "restore", "read-tree", "config",
                     "sparse-checkout", "range-diff", "maintenance", "for-each-ref", "cherry-pick"):
            self.assertIn(name, shell.GIT_BUILTINS)


class GhTests(unittest.TestCase):
    """A0: -R, --repo, GH_REPO, GH_HOST, --hostname, the subcommand path."""

    def test_path(self):
        self.assertEqual(gh("gh pr merge 12 --squash")["path"], ["pr", "merge"])
        self.assertEqual(gh("gh issue comment 3 --body hi")["path"], ["issue", "comment"])
        self.assertEqual(gh("gh repo set-default o/r")["path"], ["repo", "set-default"])
        self.assertEqual(gh("gh repo deploy-key add k.pub")["path"], ["repo", "deploy-key", "add"])

    def test_dash_R(self):
        found = gh("gh -R owner/repo pr merge 12")
        self.assertEqual((found["repo"]["owner"], found["repo"]["name"], found["repo"]["source"]),
                         ("owner", "repo", "-R"))
        self.assertEqual(found["path"], ["pr", "merge"])

    def test_dash_R_after_the_subcommand(self):
        self.assertEqual(gh("gh pr merge 12 -R o/r")["repo"]["owner"], "o")

    def test_repo_long(self):
        self.assertEqual(gh("gh pr list --repo=o/r")["repo"]["source"], "--repo")

    def test_GH_REPO(self):
        self.assertEqual(gh("GH_REPO=o/r gh pr list")["repo"]["source"], "GH_REPO")

    def test_option_wins_over_GH_REPO(self):
        self.assertEqual(gh("GH_REPO=a/b gh pr list -R o/r")["repo"]["owner"], "o")

    def test_a_dynamic_repo(self):
        self.assertTrue(gh('gh pr merge 1 -R "$R"')["repo"]["dynamic"])
        self.assertTrue(gh('GH_REPO="$R" gh pr merge 1')["repo"]["dynamic"])

    def test_an_unknown_host_from_GH_HOST(self):
        self.assertIn("ghe.example", gh("GH_HOST=ghe.example gh pr list")["unresolved"])

    def test_an_unknown_host_from_hostname(self):
        self.assertTrue(gh("gh api --hostname ghe.example user")["unresolved"])

    def test_an_unknown_host_from_dash_R(self):
        self.assertTrue(gh("gh pr list -R ghe.example/o/r")["unresolved"])

    def test_github_is_known(self):
        self.assertIsNone(gh("GH_HOST=github.com gh pr list")["unresolved"])

    def test_a_configured_host_is_known(self):
        self.assertIsNone(gh("GH_HOST=ghe.example gh pr list", hosts=("github.com", "ghe.example"))["unresolved"])

    def test_a_repo_operand(self):
        self.assertEqual(gh("gh repo edit o/r --visibility public")["repo_argument"]["name"], "r")

    def test_a_url_operand(self):
        self.assertEqual(gh("gh pr merge https://github.com/o/r/pull/12")["target_urls"],
                         [{"host": "github.com", "owner": "o", "name": "r"}])


class GhApiTests(unittest.TestCase):
    """A0: gh api with its method, field flags, --input and its path, and graphql under each spelling."""

    def api(self, line):
        return gh(line)["api"]

    def test_endpoint_and_repo(self):
        found = self.api("gh api repos/o/r/pulls/1/reviews")
        self.assertEqual((found["owner"], found["repo"], found["effective_method"]), ("o", "r", "GET"))

    def test_placeholders(self):
        self.assertEqual(self.api("gh api repos/{owner}/{repo}/issues")["placeholders"], ["owner", "repo"])

    def test_method(self):
        self.assertEqual(self.api("gh api -X DELETE repos/o/r/git/refs/heads/x")["method"], "DELETE")
        self.assertEqual(self.api("gh api --method=patch repos/o/r")["method"], "PATCH")
        self.assertEqual(self.api("gh api -XPOST repos/o/r/forks")["method"], "POST")

    def test_fields_make_it_a_post(self):
        found = self.api("gh api repos/o/r/issues -f title=x -F draft=true --raw-field body=y --field n=1")
        self.assertEqual(found["effective_method"], "POST")
        self.assertEqual([(f["flag"], f["key"], f["value"], f["raw"]) for f in found["fields"]],
                         [("-f", "title", "x", True), ("-F", "draft", "true", False),
                          ("--raw-field", "body", "y", True), ("--field", "n", "1", False)])

    def test_a_field_read_from_a_file(self):
        self.assertEqual(self.api("gh api repos/o/r/pulls/1/reviews -F body=@review.md")["fields"][0]["file"],
                         "review.md")

    def test_input(self):
        found = self.api("gh api repos/o/r/pulls/1/reviews --input review.json")
        self.assertEqual((found["input"], found["effective_method"]), ("review.json", "POST"))

    def test_graphql_spellings(self):
        for endpoint in ("graphql", "/graphql", "https://api.github.com/graphql", "graphql?x=1",
                         "https://api.github.com/graphql?x=1", "/graphql/"):
            with self.subTest(endpoint):
                self.assertTrue(self.api(f"gh api {endpoint} -f query=x")["graphql"])

    def test_not_graphql(self):
        self.assertFalse(self.api("gh api repos/o/graphql")["graphql"])

    def test_an_absolute_rest_url(self):
        found = self.api("gh api https://api.github.com/repos/o/r/issues")
        self.assertEqual((found["owner"], found["repo"]), ("o", "r"))

    def test_api_dash_F_is_a_field_not_a_message(self):
        found = find('gh api repos/o/r/issues -F body="$(cat x)"', "gh")
        self.assertEqual(found["message_args"], [])
        self.assertEqual(found["gh"]["api"]["fields"][0]["dynamic"], True)


class MessageBodyTests(unittest.TestCase):
    """A0 and criterion 55: message bodies never make a command unresolved; the heredoc idioms stay resolved."""

    COMMIT = 'git commit -m "$(cat <<\'EOF\'\nFix the export\n\nUses $(x) and `y`\nEOF\n)"'
    PR = 'gh pr create --title "Fix" --body "$(cat <<\'EOF\'\n## Summary\n- git push -f is refused\nEOF\n)"'

    def test_the_heredoc_commit_idiom(self):
        found = find(self.COMMIT, "git")
        self.assertIsNone(found["unresolved"])
        self.assertEqual((found["dynamic_args"], found["message_args"]), ([], [2]))

    def test_the_heredoc_pull_request_idiom(self):
        found = find(self.PR, "gh")
        self.assertIsNone(found["unresolved"])
        self.assertEqual(found["dynamic_args"], [])
        self.assertEqual(found["gh"]["path"], ["pr", "create"])

    def test_the_heredoc_body_runs_no_git(self):
        self.assertEqual([c["program"] for c in commands(self.PR)], ["cat", "gh"])

    def test_each_message_option(self):
        for line in ('git commit -m "$(date)"', 'git commit --message="$(date)"', 'git commit -F "$F"',
                     'git commit --file "$F"', 'git tag -a v1 -m "$M"', 'gh pr create --body "$B" --title "$T"',
                     'gh pr create -b "$B" -t "$T"', 'gh issue comment 3 --body-file "$F"',
                     'gh pr merge 3 --subject "$S" --body "$B"', 'gh release create v1 --notes "$N"'):
            with self.subTest(line):
                found = [c for c in commands(line) if c["program"] in ("git", "gh")][0]
                self.assertEqual(found["dynamic_args"], [])
                self.assertIsNone(found["unresolved"])
                self.assertTrue(found["message_args"])


class WriteTargetTests(unittest.TestCase):
    """A0 and criterion 55: the write targets the parser reports."""

    def test_each_form(self):
        cases = {
            "echo x > .git/config": [(".git/config", ">")],
            "echo x >> ~/.gitconfig": [("~/.gitconfig", ">>")],
            "echo x 2> err.log": [("err.log", ">")],
            "make &> build.log": [("build.log", "&>")],
            "echo x | tee -a a.txt b.txt": [("a.txt", "tee"), ("b.txt", "tee")],
            "cp -r a b c/": [("c/", "cp")],
            "cp -t dest a b": [("dest", "cp")],
            "mv a.txt b.txt": [("b.txt", "mv"), ("a.txt", "mv source")],
            "sed -i 's/a/b/' f.txt": [("f.txt", "sed -i")],
            "sed -i '' 's/a/b/' f.txt": [("f.txt", "sed -i")],
            "sed -Ei.bak -e 's/a/b/' f.txt g.txt": [("f.txt", "sed -i"), ("g.txt", "sed -i")],
            "sed --in-place 's/a/b/' f.txt": [("f.txt", "sed -i")],
            "dd if=/dev/zero of=disk.img bs=1": [("disk.img", "dd of=")],
            "rm -f .claude/lease.json": [(".claude/lease.json", "rm")],
            "ln -sf target link": [("link", "ln")],
            "truncate -s 0 a.log": [("a.log", "truncate")],
            "install -m 644 a /usr/local/b": [("/usr/local/b", "install")],
            "rsync -av --delete src/ dest/": [("dest/", "rsync")],
            "touch .git/index.lock": [(".git/index.lock", "touch")],
            # M3 slice Z, from C5c's queue: the removers and find -delete, which wslib/gitrules.py read itself.
            "unlink .git/HEAD": [(".git/HEAD", "unlink")],
            "rmdir -p .git/refs/x": [(".git/refs/x", "rmdir")],
            "shred -n 3 -u .git/config": [(".git/config", "shred")],
            "shred --iterations 3 a b": [("a", "shred"), ("b", "shred")],
            "find .git -name '*.lock' -delete": [(".git", "find -delete")],
            "find -L a b -type f -delete": [("a", "find -delete"), ("b", "find -delete")],
            "find -delete": [(".", "find -delete")],
            # M3 slice Z, from C5e's queue: the paths git mv, rm, checkout and restore write, which
            # parts/outward_write.py read itself until now.
            "git mv a.txt b.txt": [("a.txt", "git mv"), ("b.txt", "git mv")],
            "git rm -r --cached docs": [("docs", "git rm")],
            "git checkout HEAD~1 -- a.txt": [("HEAD~1", "git checkout"), ("a.txt", "git checkout")],
            "git checkout -b feature": [],
            "git restore --source=HEAD~1 -W a.txt": [("a.txt", "git restore")],
            "git restore -s HEAD a.txt": [("a.txt", "git restore")],
            "git -C sub -C deeper rm x": [("sub/deeper/x", "git rm")],
            "git -C sub rm /abs/x": [("/abs/x", "git rm")],
        }
        for line, expected in cases.items():
            with self.subTest(line):
                self.assertEqual(writes(line), expected)

    def test_reads_are_not_writes(self):
        for line in ("sed 's/a/b/' f.txt", "cat a", "echo x 2>&1", "grep x < in.txt",
                     "cp a", "find .git -name '*.lock'"):
            with self.subTest(line):
                self.assertEqual(writes(line), [])

    def test_a_git_write_after_a_variable_dash_C_is_dynamic(self):
        found = [w for c in commands('git -C "$D" rm x') for w in c["writes"]]
        self.assertEqual([(w["path"], w["dynamic"]) for w in found], [("x", True)])

    def test_a_dynamic_target(self):
        found = [w for c in commands('echo x > "$F"') for w in c["writes"]]
        self.assertTrue(found[0]["dynamic"])

    def test_a_redirect_on_a_group(self):
        self.assertEqual(writes("{ echo a; echo b; } > out.txt"), [("out.txt", ">")])

    def test_the_folders_a_cd_it_cannot_follow_may_have_entered(self):
        """M3 slice Z, from C5c's queue: a relative write after a cd the parser cannot follow names that cd's
        folder, so a guard can tell it may land in a git folder."""
        cases = {
            "true; cd .git; touch config": [".git"],
            "(cd .git && touch config)": [".git"],
            "true; cd .git && git status; touch config": [".git"],
            'x=1; cd "$(git rev-parse --git-dir)"; touch config': ["$(git rev-parse --git-dir)"],
            "true; cd a; pushd .git/hooks; touch pre-commit": ["a", ".git/hooks"],
        }
        for line, expected in cases.items():
            with self.subTest(line):
                found = find(line, "touch")
                self.assertIsNone(found["cwd"])
                self.assertEqual(found["cd_folders"], expected)

    def test_no_folders_when_the_folder_is_known(self):
        for line in ("cd .git && touch config", "touch config", "(cd .git); touch config", "bash -c 'cd .git'; touch c"):
            with self.subTest(line):
                self.assertEqual(find(line, "touch")["cd_folders"], [])


def reads(line):
    return [(r["path"], r["via"]) for c in commands(line) for r in c["reads"]]


class ReadTests(unittest.TestCase):
    """M3 slice Z, from C5f's queue: input redirections as reads, which parts/secrets_shell.py found itself."""

    def test_each_form(self):
        cases = {
            "wc -l < .env": [(".env", "<")],
            "exec 3<> .env": [(".env", "<>")],
            "cat 0< a.txt": [("a.txt", "<")],
            "while read -r l; do echo \"$l\"; done < .env": [(".env", "<")],
            "{ cat; } < a.txt": [("a.txt", "<")],
            "< .env": [(".env", "<")],
            'echo "$(wc -l < .env)"': [(".env", "<")],
            "sh -c 'wc -l < .env'": [(".env", "<")],
            "eval 'wc -l < .env'": [(".env", "<")],
            "bash -lc 'cat < .env'": [(".env", "<")],
            "sh -xc 'cat < .env'": [(".env", "<")],
            "bash -c -e 'cat < .env'": [(".env", "<")],
            "bash -c -o pipefail 'cat < .env'": [(".env", "<")],
            "bash -O extglob -c 'cat < .env'": [(".env", "<")],
            "bash -c 'cat' < .env": [(".env", "<")],
            "bash < script.sh": [("script.sh", "<")],
            "sudo cat < .env": [(".env", "<")],
        }
        for line, expected in cases.items():
            with self.subTest(line):
                self.assertEqual(reads(line), expected)

    def test_other_redirections_are_not_reads(self):
        for line in ("cat > a", "cat << EOF\nx\nEOF", "cat <<< text", "cat <&3", "echo x 2>&1", "cat a"):
            with self.subTest(line):
                self.assertEqual(reads(line), [])

    def test_a_dynamic_read(self):
        self.assertEqual([r["dynamic"] for c in commands('F=.env; wc -l < "$F"') for r in c["reads"]], [True])


class WithSecretsTests(unittest.TestCase):
    """M3 slice Z, from C5f's queue: `ws.py with-secrets NAME ... -- PROGRAM` is read as a wrapper, so every shell
    guard judges PROGRAM."""

    def test_the_program_is_the_child(self):
        for line in ("python3 ws.py with-secrets T -- git push --force origin main",
                     "python3 -X utf8 ws.py with-secrets T U -- git push --force origin main",
                     "./ws.py --root . with-secrets T -- git push --force origin main",
                     "wslib/launch.sh with-secrets T -- git push --force origin main",
                     "py 'C:\\w\\ws.py' with-secrets T -- git push --force origin main",
                     "sudo python3 ws.py with-secrets T -- git push --force origin main"):
            with self.subTest(line):
                found = commands(line)
                self.assertEqual([c["program"] for c in found], ["git"])
                self.assertIn("ws.py with-secrets", found[0]["wrappers"])
                self.assertTrue(found[0]["git"]["push"]["force"])

    def test_the_line_s_assignments_and_redirections_reach_the_child(self):
        found = find("WS_SECRETS_FILE=/tmp/x python3 ws.py with-secrets T -- cat < .env", "cat")
        self.assertEqual((found["env"], found["reads"][0]["path"]), ({"WS_SECRETS_FILE": "/tmp/x", "T": "$T"}, ".env"))

    def test_each_name_reaches_the_child_as_a_value_the_line_does_not_show(self):
        found = find("python3 ws.py with-secrets GH_REPO GH_TOKEN -- gh pr create --fill", "gh")
        self.assertEqual(found["env_dynamic"], ["GH_REPO", "GH_TOKEN"])
        found = find("python3 ws.py with-secrets GIT_CONFIG_COUNT -- git status", "git")
        self.assertIn("GIT_CONFIG_COUNT", found["env_dynamic"])

    def test_a_child_that_runs_another_is_unwrapped_in_turn(self):
        found = find("python3 ws.py with-secrets T -- sh -c 'gh pr merge 1 --admin'", "gh")
        self.assertEqual(found["wrappers"], ["ws.py with-secrets", "sh -c"])
        found = find("python3 ws.py with-secrets T -- python3 ws.py with-secrets U -- git push", "git")
        self.assertEqual(found["wrappers"], ["ws.py with-secrets", "ws.py with-secrets"])

    def test_not_a_wrapper(self):
        for line in ("python3 ws.py with-secrets T", "python3 ws.py with-secrets T --", "python3 ws.py check",
                     "python3 tools/other.py with-secrets T -- git push", "cat .env ws.py with-secrets -- true",
                     "rm .git/config ws.py with-secrets -- true", "python3 tools/x.py ws.py with-secrets T -- true",
                     "python3 ws.py check with-secrets T -- true"):
            with self.subTest(line):
                self.assertNotIn("git", [c["program"] for c in commands(line)])
                self.assertEqual([c["wrappers"] for c in commands(line)], [[]])


class OldParserTests(unittest.TestCase):
    """The first layer moved from no_stage_all and no_admin_merge without a change: both hooks decide exactly as
    before on their cases, and load the parser from wslib.shell."""

    @staticmethod
    def hook(name):
        path = ROOT / "parts" / f"{name}.py"
        module = types.ModuleType(f"hook_{name}")
        module.__file__ = str(path)
        exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), module.__dict__)
        return module

    def test_no_stage_all_decides_as_its_cases_say(self):
        hook = self.hook("no_stage_all")
        self.assertIs(hook.shell, shell)
        for case in json.loads((ROOT / "parts/no_stage_all.cases.json").read_text(encoding="utf-8")):
            with self.subTest(case["name"]):
                self.assertEqual(hook.decide(case["event"], {}) is not None, case["remind"])

    def test_no_admin_merge_decides_as_its_cases_say(self):
        hook = self.hook("no_admin_merge")
        self.assertIs(hook.shell, shell)
        for case in json.loads((ROOT / "parts/no_admin_merge.cases.json").read_text(encoding="utf-8")):
            with self.subTest(case["name"]):
                self.assertEqual(hook.decide(case["event"], {}) is None, case["allow"])

    def test_neither_hook_loads_another_part_file(self):
        for name in ("no_stage_all", "no_admin_merge"):
            source = (ROOT / "parts" / f"{name}.py").read_text(encoding="utf-8")
            self.assertIn("from wslib import shell", source)
            self.assertNotIn("exec(", source)

    def test_the_first_layer_reads_as_it_did(self):
        self.assertEqual(list(shell.git_calls("cd app; git -C x add -A && bash -c 'git commit -am m'")),
                         [("add", ["-A"]), ("commit", ["-am", "m"])])
        self.assertEqual(list(shell.calls("env A=1 gh -R o/r pr merge 1 --admin", "gh")),
                         [["-R", "o/r", "pr", "merge", "1", "--admin"]])
        self.assertEqual(shell.options("commit", ["-m", "add all", "-a", "."]), ({"m", "a"}, [], ["."]))


if __name__ == "__main__":
    unittest.main()
