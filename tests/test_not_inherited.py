"""Criterion 46 of the M3 plan, slice C6: two weaknesses of the workspace this one was ported from are not inherited.

1. No guard turns off when one environment variable is unset. GUARDS lists each guard: every hook part that
   refuses, each named with a refusing call from tests/hooks/, and the three git hooks that refuse a commit, its
   message or a push. VARIABLES lists every variable the machinery reads by name, and the ones the programs it
   starts read to find themselves or their config. A scan of the machinery fails on a variable read by name that
   VARIABLES does not list, so a new one cannot arrive untested. Each guard's call runs for real, through the
   agent tool's own wiring and the launcher, or through the git hook, once with every listed variable set and
   once with each one removed. With one removed, the guard must still refuse, with the same reason. A few
   variables make it refuse for another reason, which is still a refusal: FAILS_CLOSED names each, and why.
2. The one intended opt-out: the deny_list check warns and checks nothing when WS_DENY_LIST is unset and no list
   is at the default path, because CI and an outside clone have no private list. With the list at the default
   path, the check runs with the variable unset.
3. Killing the commit check mid-run leaves no temporary file, worktree or lock: the pre-commit hook is killed,
   with its whole process tree, at points spread across its run, and the working copy, its git folder and the
   temporary folder are then exactly as they were.

The stop gate is not a guard here: its wiring lets a session stop when the launcher fails, by design (slice C1),
and the README says so. Session hooks and reminders never refuse.
Run: python3 -m unittest tests.test_not_inherited -b
"""
import json
import os
import pathlib
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

import hook_cases  # noqa: E402
from wslib import parts as partlib  # noqa: E402

# Each guard, and the case in tests/hooks/<event>.json whose call it must keep refusing. Each case sets no
# variable of its own but CLAUDE_PID, so removing a variable never changes what the case asks.
GUARDS = {
    "lease": ("before-edit", "lease: a lease held by a live session refuses the edit and sends it to a worktree"),
    "shelved": ("before-edit", "an edit to the shelved service is refused"),
    "git_folder": ("before-edit", "git_folder: an edit of the repository's git config is refused"),
    "outward_list": ("before-edit", "outward_list: an edit to the list of repositories is refused"),
    "handoff_tier": ("before-handoff", "a task that names no tier is refused"),
    "no_admin_merge": ("before-shell", "an admin merge is refused"),
    "no_discard": ("before-shell", "no_discard: a hard reset in the main copy is refused while another live session "
                                   "holds it"),
    "push_lease": ("before-shell", "push_lease: a push from the main copy is refused while another live session "
                                   "holds it"),
    "git_folder_shell": ("before-shell", "git_folder_shell: a redirect into the repository's git config is refused"),
    "no_force_push": ("before-shell", "no_force_push: a force push of main is refused"),
    "outward_write": ("before-shell", "outward_write: a gh write to a repository outside the list is refused"),
    "secrets_shell": ("before-shell", "secrets_shell: a read of the secrets file is refused"),
}
# The guards whose code reads a variable by name get a second call that reaches that code: git_folder_shell judges
# ~/.gitconfig through HOME, and outward_write takes gh's repository from GH_REPO when the command names none.
# Each case sets the variable it is about; removing it must still leave the call refused.
READERS = {
    "git_folder_shell": ("before-shell", "git_folder_shell: a redirect into the global git config is refused"),
    "outward_write": ("before-shell", {
        "name": "outward_write: a gh write whose repository comes from GH_REPO is refused", "tool": "claude-code",
        "env": {"GH_REPO": "them/theirs"},
        "setup": {"files": {"outward-repos.json": "{\"repositories\": [\"github.com/o/r\"]}\n"}},
        "payload": {"hook_event_name": "PreToolUse", "tool_name": "Bash",
                    "tool_input": {"command": "gh pr comment 5 --body 'Seen.'"}, "cwd": "{root}", "session_id": "me"},
        "exit": 2, "output": ["Refused by outward_write"]}),
}
# Codex's wiring finds the launcher without a variable; one guard per event shows that through it.
CODEX = {
    "before-edit": "codex: a patch into the shelved service is refused",
    "before-shell": "codex: a force push of main is refused",
    "before-handoff": "codex: a subagent is refused until a recorded run shows its prompt",
}
# The git hooks that refuse, and the check parts each must still report on the call the test makes.
GIT_HOOKS = {
    "pre-commit": ("deny_list", "secret_scan", "edit_ledger"),
    "commit-msg": ("deny_list", "commit_subject"),
    "pre-push": ("direct_push",),
}

# Every variable the machinery reads by name, then the ones the programs it starts read to find themselves or
# their config. A variable missing from the environment the test runs in is not tested: on Linux and macOS that
# is the Windows ones, and the other way round.
VARIABLES = {
    "CLAUDE_PROJECT_DIR": "Claude Code's wiring: the path of the launcher",
    "CLAUDE_PID": "the lease: Claude Code's process",
    "WS_DENY_LIST": "deny_list: where the private list is",
    "WS_SECRETS_FILE": "with-secrets and secrets_shell: where the secrets file is",
    "HOME": "git's global config, the deny list's default path, and the guards' reading of config",
    "XDG_CONFIG_HOME": "git's global config, as the guards read it",
    "GIT_CONFIG_GLOBAL": "git's global config, as git and the guards read it",
    "GIT_CONFIG_SYSTEM": "git's system config, as git and the guards read it",
    "GIT_CONFIG_NOSYSTEM": "whether git reads its system config",
    "GIT_SSH_COMMAND": "the engine's git calls: the ssh program, made non-interactive",
    "GH_REPO": "outward_write: the repository gh acts on",
    "GH_HOST": "outward_write: the host gh acts on",
    "GH_CONFIG_DIR": "gh's config, which holds its default repository",
    "PATH": "the launcher's search for Python; every program the engine starts",
    "PYTHONUTF8": "set by the launcher itself",
    "TMPDIR": "Python's temporary folder, on Linux and macOS",
    "TEMP": "Python's temporary folder, on Windows",
    "TMP": "Python's temporary folder, on Windows",
    "USERPROFILE": "the home folder, on Windows",
    "SYSTEMROOT": "Windows itself, which Python needs to start",
    "LANG": "the locale",
}
# Variables with which a guard still refuses, for a reason other than its own. (guard or "*", variable): why.
FAILS_CLOSED = {
    ("*", "CLAUDE_PROJECT_DIR"): "Claude Code's wiring cannot find the launcher, and its `|| exit 2` refuses",
    ("lease", "CLAUDE_PID"): "the session has no process id, so it cannot hold the lease, and the edit is refused",
    ("*", "PATH"): "the launcher finds no Python on an empty path where the shell has no default, and refuses",
    ("*", "SYSTEMROOT"): "Python cannot start on Windows without it, and the wiring refuses",
}
# The text a refusal for one of those reasons must still hold, when it holds any.
FAILS_CLOSED_TEXT = {("lease", "CLAUDE_PID"): "Refused by lease"}

TERM = "zorb" + "laxian"            # a made-up private term, built here so this file does not hold it
SECRET = "AKIA" + "Q" * 16          # shaped like an AWS key id, built here for the same reason
SCANNED = ("ws.py", "wslib", "parts")
SHELL_FILES = (".githooks", "wslib/launch.sh", ".claude/settings.json", ".codex/hooks.json")


def read_by_name():
    """{variable: [files]} for each variable the machinery reads by name: in Python, a literal or a NAME =
    "LITERAL" constant on a line that names the environment (`environ` or `getenv`) and does not assign to it;
    in the git hooks, the launcher and the wiring, a $NAME the file does not set itself. A read through a copy
    of the environment under another name, such as gitcall's GIT_SSH_COMMAND, is not seen: list it by hand."""
    found = {}
    files = [ROOT / "ws.py"] + sorted((ROOT / "wslib").glob("*.py")) + sorted((ROOT / "parts").glob("*.py"))
    for file in files:
        text = file.read_text(encoding="utf-8")
        constants = dict(re.findall(r'^(\w+)\s*=\s*"([A-Z][A-Z0-9_]{2,})"', text, re.MULTILINE))
        for line in text.splitlines():
            if not re.search(r"environ|getenv", line) or re.search(r"environ\[[^]]*\]\s*=[^=]", line):
                continue
            names = set(re.findall(r'["\']([A-Z][A-Z0-9_]{2,}[A-Z0-9])["\']', line))
            names |= {value for name, value in constants.items() if re.search(rf"\b{name}\b", line)}
            for name in names:
                found.setdefault(name, []).append(file.relative_to(ROOT).as_posix())
    shells = [ROOT / name for name in SHELL_FILES]
    for file in [p for s in shells for p in (sorted(s.iterdir()) if s.is_dir() else [s])]:
        text = file.read_text(encoding="utf-8")
        assigned = set(re.findall(r"^\s*([A-Za-z_]\w*)=", text, re.MULTILINE))
        for name in set(re.findall(r"\$\{?([A-Z][A-Z0-9_]*)", text)) - assigned:
            found.setdefault(name, []).append(file.relative_to(ROOT).as_posix())
    return found


def refusing_hooks(manifest):
    """The name of every hook part in the manifest that can refuse a tool call: a hook on a before- event that is
    not a reminder. The stop gate refuses a stop, not a tool call, and is left out, as the module's text says."""
    names = set()
    for entry in manifest["parts"]:
        name, relative = partlib.source_of(ROOT, entry)
        text = (ROOT / relative).read_text(encoding="utf-8")
        if partlib.declared(text, "KIND") == "hook" and (partlib.declared(text, "EVENT") or "").startswith("before-") \
                and not re.search(r'^MODE\s*=\s*"remind"', text, re.MULTILINE):
            names.add(name)
    return names


def find_case(event, name):
    for case in hook_cases.load_cases()[event]:
        if case["name"] == name:
            return case
    raise AssertionError(f"tests/hooks/{event}.json has no case named {name!r}")


def present(environment):
    """The listed variables the environment holds, in the table's order."""
    return [name for name in VARIABLES if name in environment]


class Home:
    """A home folder of the test's own, with the private list at its default path, and a list named by
    WS_DENY_LIST. Both hold TERM, so removing either variable leaves the check reading a list that holds it."""

    def __init__(self):
        self.folder = pathlib.Path(tempfile.mkdtemp(prefix="not-inherited-home-")).resolve()
        default = self.folder / ".config" / "agent-ready-workspace" / "deny-list.txt"
        default.parent.mkdir(parents=True)
        default.write_text(TERM + "\n", encoding="utf-8")
        self.named = self.folder / "named-list.txt"
        self.named.write_text(TERM + "\n", encoding="utf-8")
        (self.folder / "gitconfig").write_text("", encoding="utf-8")
        (self.folder / "gitconfig-system").write_text("", encoding="utf-8")
        (self.folder / "gh").mkdir()

    def environment(self, scratch, root):
        """The baseline: the caller's environment, as a hook case gets it, with every variable the machinery reads
        set to a value that works."""
        env = hook_cases.clean_environment()
        env.update({
            "CLAUDE_PROJECT_DIR": pathlib.Path(root).as_posix(),
            "CLAUDE_PID": str(scratch.live.pid),
            "WS_DENY_LIST": str(self.named),
            "WS_SECRETS_FILE": str(self.folder / "secrets.env"),
            "HOME": str(self.folder),
            "XDG_CONFIG_HOME": str(self.folder / ".config"),
            "GIT_CONFIG_GLOBAL": str(self.folder / "gitconfig"),
            "GIT_CONFIG_SYSTEM": str(self.folder / "gitconfig-system"),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_SSH_COMMAND": "ssh",
            "GH_REPO": "ryantornberg/agent-ready-workspace",
            "GH_HOST": "github.com",
            "GH_CONFIG_DIR": str(self.folder / "gh"),
            "PYTHONUTF8": "1",
        })
        if os.name == "nt":
            env["USERPROFILE"] = str(self.folder)
        return env

    def close(self):
        shutil.rmtree(self.folder, ignore_errors=True)


def run_hook(scratch, places, event, case, env):
    """(exit code, output) of one real call through the tool's wiring."""
    payload = scratch.fill(case["payload"], places)
    cwd = payload.get("cwd") if isinstance(payload.get("cwd"), str) and payload.get("cwd") else str(places["root"])
    command = hook_cases.wiring(places["root"], case["tool"], event)
    done = subprocess.run([hook_cases.shell(), "-c", command], input=json.dumps(payload).encode("utf-8"), cwd=cwd,
                          capture_output=True, env=env, timeout=hook_cases.CALL_TIMEOUT)
    return done.returncode, (done.stdout + done.stderr).decode("utf-8", "replace")


def without(env, name):
    return {key: value for key, value in env.items() if key != name}


class ScanTests(unittest.TestCase):
    def test_every_variable_the_machinery_reads_by_name_is_listed(self):
        unlisted = {name: files for name, files in read_by_name().items() if name not in VARIABLES}
        self.assertEqual(unlisted, {}, "a variable the machinery reads is not in VARIABLES, so no test removes it")

    def test_the_scan_finds_the_variables_known_to_be_read(self):
        found = read_by_name()
        for name in ("CLAUDE_PROJECT_DIR", "CLAUDE_PID", "WS_DENY_LIST", "WS_SECRETS_FILE", "GH_REPO", "HOME"):
            with self.subTest(name):
                self.assertIn(name, found)

    def test_the_guards_listed_are_every_hook_that_refuses(self):
        manifest = partlib.load_manifest(ROOT)
        self.assertEqual(set(GUARDS), refusing_hooks(manifest))
        for name, (event, _) in GUARDS.items():
            with self.subTest(name):
                text = (ROOT / "parts" / f"{name}.py").read_text(encoding="utf-8")
                self.assertEqual(partlib.declared(text, "EVENT"), event)

    def test_each_listed_case_refuses_by_its_own_guard_and_sets_no_variable_but_the_process_id(self):
        for name, (event, case_name) in GUARDS.items():
            with self.subTest(name):
                case = find_case(event, case_name)
                self.assertEqual(case["exit"], 2)
                self.assertIn(f"Refused by {name}", case.get("output", []))
                self.assertLessEqual(set(case.get("env", {})), {"CLAUDE_PID"})
        for event, case_name in CODEX.items():
            with self.subTest(event):
                case = find_case(event, case_name)
                self.assertEqual((case["exit"], case["tool"]), (2, "codex"))
        self.assertEqual(set(READERS), {"git_folder_shell", "outward_write"})


class HookGuardTests(unittest.TestCase):
    """Each guard's refusing call, through the agent tool's wiring, with each variable removed in turn."""

    @classmethod
    def setUpClass(cls):
        cls.scratch = hook_cases.Scratch()
        cls.home = Home()

    @classmethod
    def tearDownClass(cls):
        cls.scratch.close()
        cls.home.close()

    def judge(self, guard, case, variable, code, output):
        """None when the call refused as the guard should, else what went wrong."""
        if hook_cases.judge(case, code, output, case.get("lease_after")) is None:
            return None
        reason = FAILS_CLOSED.get((guard, variable)) or FAILS_CLOSED.get(("*", variable))
        if code == 2 and reason:
            text = FAILS_CLOSED_TEXT.get((guard, variable))
            if text is None or text in output:
                return None
        return f"exit {code}: {output.strip()[:300]}"

    def check(self, guard, event, case):
        places = self.scratch.build(case.get("setup", {}))
        env = self.home.environment(self.scratch, places["root"])
        env.update(self.scratch.fill(case.get("env", {}), places))
        failures = []
        for variable in [None] + present(env):
            self.scratch.seed(places, case.get("setup", {}))
            code, output = run_hook(self.scratch, places, event, case, without(env, variable))
            problem = self.judge(guard, case, variable, code, output)
            if problem:
                failures.append(f"{variable or 'nothing'} removed: {problem}")
        self.assertEqual(failures, [], f"{guard} stopped refusing")

    def test_each_guard_still_refuses_with_any_one_variable_removed(self):
        for guard, (event, case_name) in GUARDS.items():
            with self.subTest(guard):
                self.check(guard, event, find_case(event, case_name))

    def test_the_guards_that_read_a_variable_still_refuse_where_they_read_it(self):
        for guard, (event, case) in READERS.items():
            with self.subTest(guard):
                self.check(guard, event, case if isinstance(case, dict) else find_case(event, case))

    def test_codex_wiring_still_refuses_with_any_one_variable_removed(self):
        for event, case_name in CODEX.items():
            case = find_case(event, case_name)
            guard = next((text[len("Refused by "):] for text in case.get("output", []) if text.startswith("Refused by ")),
                         "handoff")
            with self.subTest(event):
                self.check(guard, event, case)


def git_hook(root, name, env, *args, data=None):
    """(exit code, output) of one git hook, run as git runs it: from the top of the working copy, by sh."""
    done = subprocess.run([hook_cases.shell(), f".githooks/{name}", *args], cwd=root, input=data,
                          capture_output=True, env=env, timeout=300)
    return done.returncode, (done.stdout + done.stderr).decode("utf-8", "replace")


def tagged(output):
    """The lines of a check's output that report a finding, which do not depend on the environment."""
    return sorted(line for line in output.splitlines() if re.search(r"\[[a-z_]+\]", line))


class GitHookTests(unittest.TestCase):
    """The commit check, the message check and the push check, with each variable removed in turn."""

    @classmethod
    def setUpClass(cls):
        cls.scratch = hook_cases.Scratch()
        cls.home = Home()
        cls.places = cls.scratch.build({"remote": True})
        root = cls.places["root"]
        # A commit on main that changes a part, for the push check; then a staged page that holds the private
        # term and a key id, which the agent's edit tools did not write, for the commit check.
        part = root / "parts" / "shelved.py"
        part.write_text(part.read_text(encoding="utf-8") + "# changed\n", encoding="utf-8")
        hook_cases.git(root, "commit", "-q", "--no-verify", "-am", "fix: a change to a part")
        cls.local = hook_cases.git(root, "rev-parse", "HEAD").strip()
        cls.remote = hook_cases.git(root, "rev-parse", "origin/main").strip()
        (root / "docs" / "notes.md").write_text(f"# Notes\n\n{TERM}\n\nkey = {SECRET}\n", encoding="utf-8")
        hook_cases.git(root, "add", "docs/notes.md")
        (root / ".git" / hook_cases.LEDGER).write_text(json.dumps({"path": "README.md", "session": "s"}) + "\n",
                                                       encoding="utf-8")
        (root / ".git" / "C6_MSG").write_text(f"no format here, {TERM}\n", encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.scratch.close()
        cls.home.close()

    def calls(self):
        root, origin = self.places["root"], (self.places["root"].parent / f"{self.places['root'].name}-origin.git")
        refs = f"refs/heads/main {self.local} refs/heads/main {self.remote}\n".encode("utf-8")
        return {
            "pre-commit": lambda env: git_hook(root, "pre-commit", env),
            "commit-msg": lambda env: git_hook(root, "commit-msg", env, ".git/C6_MSG"),
            "pre-push": lambda env: git_hook(root, "pre-push", env, "origin", origin.as_posix(), data=refs),
        }

    def test_each_git_hook_still_refuses_with_any_one_variable_removed(self):
        env = self.home.environment(self.scratch, self.places["root"])
        for hook, call in self.calls().items():
            with self.subTest(hook):
                code, output = call(env)
                self.assertNotEqual(code, 0, output)
                for part in GIT_HOOKS[hook]:
                    self.assertIn(f"[{part}]", output, f"{hook} does not report {part} with every variable set")
                baseline = tagged(output)
                failures = []
                for variable in present(env):
                    code, output = call(without(env, variable))
                    if code == 0:
                        failures.append(f"{variable} removed: the hook passed: {output.strip()[:300]}")
                    elif tagged(output) != baseline and not FAILS_CLOSED.get(("*", variable)):
                        failures.append(f"{variable} removed: the findings differ: {output.strip()[:600]}")
                self.assertEqual(failures, [], f"{hook} changed with one variable removed")


class DenyListOptOutTests(unittest.TestCase):
    """The one intended opt-out, and that it is the only one: see the README's checks table."""

    @classmethod
    def setUpClass(cls):
        cls.scratch = hook_cases.Scratch()
        cls.places = cls.scratch.build({})
        root = cls.places["root"]
        (root / "docs" / "notes.md").write_text(f"# Notes\n\n{TERM}\n", encoding="utf-8")
        hook_cases.git(root, "add", "docs/notes.md")

    @classmethod
    def tearDownClass(cls):
        cls.scratch.close()

    def commit_check(self, home, **extra):
        env = hook_cases.clean_environment({"HOME": str(home), "USERPROFILE": str(home)})
        env.pop("WS_DENY_LIST", None)
        env.update(extra)
        return git_hook(self.places["root"], "pre-commit", env)

    def test_unset_with_no_list_at_the_default_path_warns_and_checks_nothing(self):
        home = Home()
        try:
            (home.folder / ".config" / "agent-ready-workspace" / "deny-list.txt").unlink()
            _, output = self.commit_check(home.folder)
            self.assertIn("warning: workspace.json:1: no private deny list: WS_DENY_LIST is not set", output)
            self.assertIn("so nothing was checked", output)
            self.assertNotIn("error: docs/notes.md", "\n".join(l for l in output.splitlines() if "[deny_list]" in l))
        finally:
            home.close()

    def test_unset_with_the_list_at_the_default_path_still_checks(self):
        home = Home()
        try:
            _, output = self.commit_check(home.folder)
            self.assertIn("error: docs/notes.md", "\n".join(l for l in output.splitlines() if "[deny_list]" in l))
        finally:
            home.close()

    def test_set_to_a_missing_file_is_an_error_not_a_pass(self):
        home = Home()
        try:
            _, output = self.commit_check(home.folder, WS_DENY_LIST=str(home.folder / "no-such-list.txt"))
            self.assertIn("the private deny list cannot be read", output)
        finally:
            home.close()


def listing(folder):
    """{path: (size, modified time)} for everything under folder, folders included."""
    found = {}
    for top, folders, files in os.walk(folder):
        for name in folders + files:
            path = os.path.join(top, name)
            try:
                info = os.lstat(path)
            except OSError:
                continue
            found[os.path.relpath(path, folder)] = (info.st_size if name in files else -1, info.st_mtime_ns)
    return found


def kill_tree(process):
    """Kill the process and everything it started, as a person's terminal or an agent tool's time limit would."""
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)], capture_output=True)
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    process.wait()


class KilledCommitCheckTests(unittest.TestCase):
    """Criterion 46: killing the commit check mid-run leaves no temporary file, worktree or lock."""

    POINTS = (0.05, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9)    # fractions of one whole run

    def test_a_killed_commit_check_leaves_nothing_behind(self):
        scratch = hook_cases.Scratch()
        temporary = pathlib.Path(tempfile.mkdtemp(prefix="not-inherited-tmp-")).resolve()
        try:
            places = scratch.build({})
            root = places["root"]
            (root / "docs" / "notes.md").write_text("# Notes\n", encoding="utf-8")
            hook_cases.git(root, "add", "docs/notes.md")
            env = hook_cases.clean_environment({"TMPDIR": str(temporary), "TEMP": str(temporary),
                                                "TMP": str(temporary), "WS_DENY_LIST": ""})
            git_hook(root, "pre-commit", env)            # a first whole run compiles the engine once
            started = time.perf_counter()
            git_hook(root, "pre-commit", env)            # the second is timed, as each killed run starts warm
            whole = time.perf_counter() - started
            worktrees = hook_cases.git(root, "worktree", "list", "--porcelain")
            before, before_temporary = listing(root), listing(temporary)
            for point in self.POINTS:
                with self.subTest(point=point):
                    options = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" \
                        else {"start_new_session": True}
                    process = subprocess.Popen([hook_cases.shell(), ".githooks/pre-commit"], cwd=root, env=env,
                                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **options)
                    time.sleep(whole * point)
                    still_running = process.poll() is None
                    kill_tree(process)
                    time.sleep(0.2)
                    after = listing(root)
                    self.assertEqual(sorted(set(after) - set(before)), [], "left behind in the working copy")
                    self.assertEqual(sorted(set(before) - set(after)), [], "removed from the working copy")
                    self.assertEqual(sorted(p for p in before if after[p] != before[p]), [],
                                     "changed in the working copy")
                    self.assertEqual(listing(temporary), before_temporary, "left behind in the temporary folder")
                    self.assertEqual(hook_cases.git(root, "worktree", "list", "--porcelain"), worktrees)
                    if point <= 0.6:
                        self.assertTrue(still_running, "the check ended before it was killed, so this kill tested "
                                                       "nothing")
        finally:
            scratch.close()
            shutil.rmtree(temporary, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
