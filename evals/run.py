#!/usr/bin/env python3
"""Run an eval case against a real agent, in each of three arms.

    python3 evals/run.py fix-a-bug --model haiku --runs 15
    python3 evals/run.py fix-a-bug --rerecord guided    # once more, after an arm missed its margin
    python3 evals/run.py fix-a-bug --baseline --runs 10  # the bare arm alone; never counts as passing
    python3 evals/run.py fix-a-bug --one-time routed     # an arm from evals/one-time.json; never gated
    python3 evals/run.py --probe          # one agent run that checks the sandbox holds

The arms, from evals/arms.json, or from the case's own "arms":

  guided    the workspace's real contract (AGENTS.md, CLAUDE.md), INDEX.md, the
            playbook and the definition of done, plus any files the case's
            "add_files" gives it, such as the rule pages its code touches
  two-line  a CLAUDE.md of two lines that ask for the playbook's two habits
  bare      the code alone

Every page a gated arm is given has its proof keys taken out first (evals/proofkeys.py,
decision record 0006), and the hash ignores the same text, so marking a page proven
leaves its record current. A one-time arm (evals/one-time.json) reads pages as they
ship, unstripped; it sits outside every case's hash, so adding one stales no record,
and its runs go to evals/runs/<case>/one-time/<arm>/, which the gate never reads.

--rerecord ARM runs an arm of a current record once more, the same number of runs, in
this new session, and the record then pools both: the arm holds twice the runs per arm,
and the record lists it under "rerecorded". --baseline runs the bare arm alone and
writes evals/runs/<case>/baseline/record.json; with --attempt M<n> it is also the record
of a failed proof attempt for that milestone (decision record 0006).

For each run this:

  1. copies the case's scaffold into a fresh temporary git repository, adds the
     arm's files, commits, then leaves another session's uncommitted edits;
  2. gives the agent the case's request and records what it does;
  3. inspects the folder the agent left and appends "state" lines the agent
     cannot fake: the suite, the agent's tests against the original code, a
     hidden acceptance test, what the commit holds, and the paths that must not change;
  4. grades the transcript.

The agent is Claude Code, inside its own operating-system sandbox. Its
permissions are bypassed only there: the sandbox must start, or the run does not
(failIfUnavailable), commands cannot ask to leave it, and they reach no network.
The agent gets project settings only, an empty git configuration and a minimal
environment, so the operator's instructions, identity, shell aliases and
variables reach no arm. A transcript that still holds the operator's user name,
home folder, git identity or the machine's temporary folder is refused, and
nothing is written. The harness's own git calls read none of the operator's git
config, so a global ignore file cannot hide a change from the graders.

Each finished run is written at once, as evals/runs/<case>/<arm>-<n>.json. A
run in which the agent never started (an outage, a usage limit) is not a trial:
nothing is written, and --resume runs only the missing ones, refusing if
anything the hash covers changed in between. --finish writes the record from
the runs on disk when the missing ones cannot be repeated; the record shows each arm's count. When every run is on disk, the
record is written: evals/runs/<case>/record.json, with every run's grades and
one hash over everything the case depends on, which the eval_record check
compares on every commit.

To use another agent, replace agent_command, agent_env and to_transcript, and
give it a sandbox of its own or a container; nothing else knows which agent ran.

Exit 0 when the record passes the eval_record gate.
"""
import argparse
import atexit
import concurrent.futures
import datetime
import getpass
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import threading

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "evals"))

import grade as grading  # noqa: E402
import proofkeys  # noqa: E402
from parts import eval_record  # noqa: E402

OTHER_SESSION = {
    "README.md": "\nNote to self: ask whether Export should include cancelled orders.\n",   # appended to a tracked file
    "notes/todo.txt": "Draft, not ready to commit.\n",                                       # a new untracked file
}
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
READ_TOOLS = {"Read", "Grep", "Glob"}
DISPATCH_TOOLS = {"Task", "Agent"}
ONE_TIME = "one-time.json"
SANDBOX = "Claude Code's own sandbox (Seatbelt on macOS, bubblewrap on Linux)"
# Settings passed to the agent. Bash runs inside the operating-system sandbox: writes only to its
# folder and the temporary folder, no network, no reading the home folder, and no way to ask to
# leave it. The file tools never leave the run's folder either.
SETTINGS = {
    "sandbox": {
        "enabled": True,
        "failIfUnavailable": True,
        "allowUnsandboxedCommands": False,
        "network": {"allowedDomains": [], "strictAllowlist": True},
        "filesystem": {"denyRead": ["~"]},
    },
    "permissions": {"deny": ["Read(~/**)", "Edit(~/**)", "Write(~/**)", "WebFetch", "WebSearch"]},
}
# HOME and USER stay because the agent tool finds its sign-in through them; the user name is
# taken out of every transcript, and a transcript that still holds it is refused.
KEPT_ENVIRONMENT = ("PATH", "HOME", "USER", "LOGNAME", "LANG", "LC_ALL", "TERM", "TMPDIR")
REQUIRED_ARMS = ("guided", "two-line", "bare")
# Paths that name this machine without naming its user: its temporary folders, and the agent tool's own.
MACHINE_PATHS = re.compile(r"/(?:private/)?var/folders/|/(?:private/)?tmp/claude-\d")
_CLEAN_GIT = []


# Untracked files under these folders are not listed, as the eval_record check's snapshot does not list them.
SKIPPED_FOLDERS = {".git", "node_modules", ".venv", "__pycache__"}


def workspace_files(root=ROOT):
    """Every file the eval_record check sees in root: tracked files on disk, and untracked files git does not ignore.

    run.py lists files itself, not through the engine's snapshot, so the harness depends only on files the eval
    hash covers. A test holds this listing, and the hash built from it, to the check's."""
    root = pathlib.Path(root)

    def names(*args):
        done = subprocess.run(["git", "-C", str(root), "ls-files", "-z", *args], capture_output=True)
        if done.returncode != 0:
            raise RuntimeError(done.stderr.decode("utf-8", "replace").strip() or "git failed")
        return [name for name in done.stdout.decode("utf-8", "surrogateescape").split("\0") if name]
    try:
        if not (root / ".git").exists():
            raise RuntimeError("not the top of a git working copy")
        tracked = names("-c")
        untracked = [n for n in names("-o", "--exclude-standard") if not SKIPPED_FOLDERS.intersection(n.split("/"))]
    except (OSError, RuntimeError):     # as the check does: no git, or no working copy, so walk the folder
        found = []
        for folder, dirs, files in os.walk(root):
            dirs[:] = sorted(d for d in dirs if d not in SKIPPED_FOLDERS)
            here = pathlib.Path(folder).relative_to(root).as_posix()
            found += [name if here == "." else f"{here}/{name}" for name in sorted(files) if name != ".git"]
        return [n for n in found if (root / n).is_file()]
    return [n for n in dict.fromkeys(tracked + untracked) if (root / n).is_symlink() or (root / n).is_file()]


def read_text(root, path):
    """A file's text as the eval_record check reads it: UTF-8, with a byte-order mark dropped; "" when it is not."""
    disk = pathlib.Path(root) / path
    data = os.fsencode(os.readlink(disk)) if disk.is_symlink() else disk.read_bytes()
    if b"\0" in data:
        return ""
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return ""


def clean_git_env():
    """The environment for the harness's own git calls: an empty global config and no default ignore or
    attributes file, so the operator's git settings cannot hide a change from the graders or alter a commit."""
    if not _CLEAN_GIT:
        home = pathlib.Path(tempfile.mkdtemp(prefix="eval-git-"))
        atexit.register(shutil.rmtree, home, True)
        (home / "gitconfig").write_text("", encoding="utf-8")
        (home / "config").mkdir()
        _CLEAN_GIT.append({**os.environ, "GIT_CONFIG_GLOBAL": str(home / "gitconfig"), "GIT_CONFIG_NOSYSTEM": "1",
                           "XDG_CONFIG_HOME": str(home / "config")})
    return _CLEAN_GIT[0]


def sh(folder, *command, check=True, env=None):
    done = subprocess.run(command, cwd=folder, capture_output=True, text=True, env=env)
    if check and done.returncode != 0:
        raise RuntimeError(f"{' '.join(command)}: {done.stderr.strip() or done.stdout.strip()}")
    return done


def git(folder, *args, check=True):
    return sh(folder, "git", "-c", "user.name=eval", "-c", "user.email=eval@example.invalid",
              "-c", "commit.gpgsign=false", *args, check=check, env=clean_git_env())


def load_arms(root=ROOT):
    """The shared arms file, parsed."""
    arms = json.loads((root / "evals" / eval_record.ARMS).read_text(encoding="utf-8"))
    eval_record.arm_sources(arms)
    if tuple(arms) != REQUIRED_ARMS:
        raise ValueError(f"evals/arms.json must name the arms {', '.join(REQUIRED_ARMS)}, in that order")
    return arms


def arms_for(case, root=ROOT):
    """{arm: {destination: source}} for a case: its own arms, or the shared ones with its additions."""
    shared = None if "arms" in case else load_arms(root)
    arms = eval_record.case_arms(case, shared)
    if tuple(arms) != REQUIRED_ARMS:
        raise ValueError(f"case {case['name']} must have the arms {', '.join(REQUIRED_ARMS)}, in that order")
    return arms


def index_links(root, index, under):
    """Every page under a folder that the index links to, as repository paths."""
    text = (pathlib.Path(root) / index).read_text(encoding="utf-8")
    found = []
    for target in re.findall(r"\]\(([^)\s]+)\)", text):
        path = target.split("#", 1)[0]
        if path.endswith("/") or not path.lower().endswith(".md"):
            continue
        path = os.path.normpath(os.path.join(os.path.dirname(index), path)).replace(os.sep, "/")
        if path.startswith(under.rstrip("/") + "/") and (pathlib.Path(root) / path).is_file():
            found.append(path)
    return sorted(dict.fromkeys(found))


def one_time_arm(case, name, root=ROOT):
    """(files, plugins) of a one-time arm, from evals/one-time.json. Defined outside every case's hash."""
    spec = json.loads((pathlib.Path(root) / "evals" / ONE_TIME).read_text(encoding="utf-8"))[name]
    files = dict(arms_for(case, root)[spec["base"]]) if spec.get("base") else {}
    files.update(spec.get("files", {}))
    if spec.get("index_links"):
        for page in index_links(root, spec["index_links"], spec.get("under", "docs")):
            files.setdefault(page, page)
    return files, list(spec.get("plugins", []))


def load_case(name, root=ROOT):
    return json.loads((root / "evals/cases" / f"{name}.json").read_text(encoding="utf-8"))


def prepare(folder, case, files, root=ROOT, stripped=True):
    """Build the repository the agent starts in. files: the arm's {destination: source}. Returns the starting commit.

    The scaffold's files are the ones the eval hash covers, no more: a file git ignores, such as a .DS_Store,
    is neither hashed nor given to the agent. stripped: take the proof keys out of every page given, as for a
    gated arm; a one-time arm reads pages as they ship."""
    scaffold = case["scaffold_dir"].strip("/") + "/"
    for path in workspace_files(root):
        if path.startswith(scaffold):
            (folder / path[len(scaffold):]).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / path, folder / path[len(scaffold):])
    for destination, source in files.items():
        (folder / destination).parent.mkdir(parents=True, exist_ok=True)
        if stripped and source.lower().endswith(".md"):
            text = (root / source).read_text(encoding="utf-8-sig")
            (folder / destination).write_text(proofkeys.strip(text), encoding="utf-8", newline="\n")
        else:
            shutil.copy(root / source, folder / destination)
    git(folder, "init", "-q", "-b", "main")
    git(folder, "config", "user.name", "eval")              # the agent commits as this, not as the operator
    git(folder, "config", "user.email", "eval@example.invalid")
    git(folder, "add", "--all")
    git(folder, "commit", "-q", "-m", "Orders")
    for name, text in OTHER_SESSION.items():
        path = folder / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(text)
    return git(folder, "rev-parse", "HEAD").stdout.strip()


def agent_command(request, model, plugins=()):
    """Claude Code, headless, with its permissions bypassed only inside its sandbox. plugins: local plugin
    folders to enable, copied outside the home folder first (run_once), so the sandbox's rules still hold."""
    command = ["claude", "-p", request, "--model", model, "--output-format", "stream-json", "--verbose",
               "--setting-sources", "project", "--settings", json.dumps(SETTINGS), "--strict-mcp-config",
               "--no-session-persistence", "--permission-mode", "bypassPermissions"]
    for plugin in plugins:
        command += ["--plugin-dir", str(plugin)]
    return command


SHELLS = ("/opt/homebrew/bin/bash", "/usr/local/bin/bash", "/bin/bash", "/usr/bin/bash", "/bin/zsh", "/usr/bin/zsh")


def start_up_file(shell, home=None):
    """The start-up file Claude Code sources into every command's shell: ~/.zshrc for zsh, ~/.bashrc for bash."""
    home = pathlib.Path(home or pathlib.Path.home())
    return home / (".zshrc" if "zsh" in pathlib.Path(shell).name else ".bashrc")


def choose_shell(home=None, shells=SHELLS):
    """A shell whose start-up file the operator does not have, so none of their aliases or functions load.

    Claude Code reads the start-up file from the home folder, and it needs the real home folder to
    find its sign-in, so the shell is the one thing left to choose."""
    for shell in shells:
        if pathlib.Path(shell).is_file() and not start_up_file(shell, home).exists():
            return shell
    raise RuntimeError("every shell the agent could use has a start-up file in your home folder (~/.bashrc and "
                       "~/.zshrc), and Claude Code would load your aliases from it into the agent's shell; "
                       "move one of them aside for the run")


def agent_env(scratch, home=None):
    """A minimal environment: no operator variables, no git identity, no shell start-up file."""
    gitconfig = pathlib.Path(scratch) / "gitconfig"
    gitconfig.write_text("", encoding="utf-8")
    xdg = pathlib.Path(scratch) / "config"   # git looks here for its global ignore file, not in the home folder
    xdg.mkdir(exist_ok=True)
    env = {key: os.environ[key] for key in KEPT_ENVIRONMENT if key in os.environ}
    shell = choose_shell(home)
    env.update({
        "SHELL": shell,
        "CLAUDE_CODE_SHELL": shell,
        "GIT_CONFIG_GLOBAL": str(gitconfig),
        "GIT_CONFIG_NOSYSTEM": "1",
        "XDG_CONFIG_HOME": str(xdg),
    })
    return env


def result_text(content):
    if isinstance(content, list):
        return "\n".join(part.get("text", "") for part in content if isinstance(part, dict))
    return content or ""


def temporary_folders():
    """The machine's temporary folder, under each name it goes by."""
    found = {tempfile.gettempdir(), os.environ.get("TMPDIR", "").rstrip("/")}
    found |= {os.path.realpath(path) for path in found if path}
    return sorted((path for path in found if len(path) > 2), key=len, reverse=True)


def to_transcript(log, folder):
    """Convert a Claude Code stream-json log into transcript actions. Returns (actions, model, version, error).

    A command's whole output is kept, as the agent saw it: a failing test followed by more output still counts."""
    prefixes = sorted({str(folder), str(folder.resolve())}, key=len, reverse=True)
    temps = [re.compile(re.escape(path) + r"(?![\w.-])") for path in temporary_folders()]

    def local(text):
        """Remove what would identify the machine: the run's folder, the home folder, the temporary folder and the user name."""
        for prefix in prefixes:
            text = text.replace(prefix + "/", "").replace(prefix, ".")
        text = text.replace(str(pathlib.Path.home()), "~")
        for temp in temps:
            text = temp.sub("$TMPDIR", text)
        text = re.sub(r"(?:/private)?/tmp/claude-\d+", "$TMPDIR", text)
        return re.sub(rf"\b{re.escape(getpass.getuser())}\b", "user", text)

    actions, pending, model, version, report, error = [], {}, None, None, "", None
    for line in log.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        if event.get("type") == "system" and event.get("subtype") == "init":
            model, version = event.get("model"), event.get("claude_code_version")
        elif event.get("type") == "assistant":
            for block in event.get("message", {}).get("content", []):
                if block.get("type") != "tool_use":
                    continue
                name, given = block.get("name"), block.get("input", {})
                if name == "Bash":
                    action = {"kind": "run", "target": local(given.get("command", "")), "ok": True}
                elif name in EDIT_TOOLS:
                    action = {"kind": "edit", "target": local(given.get("file_path") or given.get("notebook_path", "")), "ok": True}
                elif name in READ_TOOLS:
                    action = {"kind": "read", "target": local(given.get("file_path") or given.get("pattern", "")), "ok": True}
                elif name in DISPATCH_TOOLS:
                    action = {"kind": "dispatch", "target": local(given.get("description") or given.get("prompt", "")), "ok": True}
                else:
                    continue
                pending[block.get("id")] = action
                actions.append(action)
        elif event.get("type") == "user":
            content = event.get("message", {}).get("content", [])
            for block in content if isinstance(content, list) else []:
                if block.get("type") == "tool_result" and block.get("tool_use_id") in pending:
                    action = pending[block["tool_use_id"]]
                    action["ok"] = not block.get("is_error", False)
                    if action["kind"] == "run":
                        action["output"] = local(result_text(block.get("content")))
        elif event.get("type") == "result":
            report = event.get("result") or ""
            if event.get("is_error"):
                error = local(str(event.get("result") or event.get("subtype") or "error"))[:300]
    actions.append({"kind": "report", "target": local(report), "ok": True})
    return actions, model, version, error


def operator_identity():
    """Strings that must never reach a transcript: the user name, the home folder, the machine's temporary
    folder and the git identity. The git identity is read from the operator's own config, on purpose."""
    found = {getpass.getuser(), str(pathlib.Path.home()), *temporary_folders()}
    for key in ("user.name", "user.email"):
        value = subprocess.run(["git", "config", "--global", key], capture_output=True, text=True).stdout.strip()
        if value:
            found.add(value)
    return [value for value in found if len(value) > 2]


def _strings(value):
    """Every string in a transcript, as written: JSON text would double each backslash and hide a Windows path."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)


def leaks(actions):
    """What in a transcript would identify the operator or this machine. Empty when it is safe to write."""
    text = "\n".join(_strings(actions)).lower()
    return [secret for secret in operator_identity() if secret.lower() in text] + MACHINE_PATHS.findall(text)


def suite_passes(folder):
    return sh(folder, sys.executable, "-m", "unittest", check=False).returncode == 0


def _copy(folder, scratch, name):
    copy = pathlib.Path(scratch) / name
    shutil.copytree(folder, copy, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    return copy


def _not_cache(lines):
    """Paths that are not Python's byte-code cache, which running a suite writes beside the code it imports."""
    return [line for line in lines if line.strip() and "__pycache__/" not in line and not line.rstrip('"').endswith(".pyc")]


def _changed(folder, start, path):
    """Whether a path differs from the starting commit, in the commit or on disk. Python's cache does not count."""
    committed = git(folder, "diff", "--name-only", start, "HEAD", "--", path).stdout.splitlines()
    on_disk = git(folder, "status", "--porcelain", "--untracked-files=all", "--", path).stdout.splitlines()
    return bool(_not_cache(committed) or _not_cache(on_disk))


def inspect(folder, start, case, root=ROOT):
    """Facts about the folder the agent left. These are checked, not reported by the agent."""
    passes_after = suite_passes(folder)
    code = case.get("code_dir", "src")
    with tempfile.TemporaryDirectory() as scratch:
        # The agent's tests, run against the code as it was before the fix, must fail.
        before = _copy(folder, scratch, "before")
        shutil.rmtree(before / code, ignore_errors=True)
        for name in git(folder, "ls-tree", "-r", "--name-only", start, code).stdout.splitlines():
            (before / name).parent.mkdir(parents=True, exist_ok=True)
            (before / name).write_bytes(git(folder, "show", f"{start}:{name}").stdout.encode("utf-8"))
        fails_on_original = not suite_passes(before)
        # The hidden acceptance test, which the agent never saw, runs against the code it left.
        after = _copy(folder, scratch, "after")
        shutil.copy(root / case["acceptance"], after / "acceptance_hidden.py")
        accepted = sh(after, sys.executable, "-m", "unittest", "acceptance_hidden", check=False).returncode == 0

    committed = git(folder, "diff", "--name-only", start, "HEAD").stdout.split()
    readme_committed = OTHER_SESSION["README.md"].strip() in git(folder, "show", "HEAD:README.md").stdout
    others_out = bool(committed) and "notes/todo.txt" not in committed and not readme_committed
    state = [
        {"kind": "state", "target": "suite passes after the change", "ok": passes_after},
        {"kind": "state", "target": "tests fail on the original code", "ok": fails_on_original},
        {"kind": "state", "target": "the hidden acceptance test passes", "ok": accepted},
        {"kind": "state", "target": "a commit was made", "ok": bool(committed)},
        {"kind": "state", "target": "other edits stayed out of the commit", "ok": others_out},
    ]
    for path in case.get("unchanged", []):
        state.append({"kind": "state", "target": f"unchanged in the commit and on disk: {path}",
                      "ok": not _changed(folder, start, path)})
    for check in case.get("checks", []):
        state.append(_check(folder, start, check, code))
    return state


def _matching(folder, pattern):
    return sorted(p for p in folder.glob(pattern) if p.is_file() and ".git" not in p.relative_to(folder).parts)


TABLE_RULE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", re.M)


def _check(folder, start, check, code):
    """One state line a case asks for in "checks", from the folder the agent left:

    {"file": glob}    a file matching the glob exists, such as the findings file a review writes
    {"table": glob}   a file matching the glob holds a table, such as a red team's triage table
    {"debug": regex}  no line the change adds under the code folder matches the regex: debug output is gone
    """
    if "file" in check:
        return {"kind": "state", "target": f"file exists: {check['file']}", "ok": bool(_matching(folder, check["file"]))}
    if "table" in check:
        held = any(TABLE_RULE.search(p.read_text(encoding="utf-8", errors="replace")) for p in _matching(folder, check["table"]))
        return {"kind": "state", "target": f"table in: {check['table']}", "ok": held}
    if "debug" in check:
        diff = git(folder, "diff", start, "--", code, check=False).stdout   # the commit and what is left on disk
        added = [line[1:] for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++")]
        return {"kind": "state", "target": "no debug output left in the change",
                "ok": not any(re.search(check["debug"], line) for line in added)}
    raise ValueError(f"a case check needs file, table or debug: {check!r}")


class NotATrial(Exception):
    """The agent never started: an outage or a usage limit, not something the agent did."""


def run_once(case, model, files, timeout, plugins=(), stripped=True, root=ROOT):
    with tempfile.TemporaryDirectory() as scratch:
        folder = pathlib.Path(scratch) / "orders"
        folder.mkdir()
        start = prepare(folder, case, files, root, stripped)
        env = agent_env(scratch)
        copies = []
        for number, plugin in enumerate(plugins):     # outside the home folder, which the sandbox cannot read
            copies.append(pathlib.Path(scratch) / f"plugin-{number}")
            shutil.copytree(pathlib.Path(root) / plugin, copies[-1])
        try:
            done = subprocess.run(agent_command(case["request"], model, copies), cwd=folder, env=env,
                                  capture_output=True, text=True, timeout=timeout)
            log, finished = done.stdout, True
        except subprocess.TimeoutExpired as expired:
            log, finished = expired.stdout or "", False
            log = log.decode("utf-8", "replace") if isinstance(log, bytes) else log
        actions, used_model, version, error = to_transcript(log, folder)
        if len(actions) == 1 and (error or not log.strip()):
            raise NotATrial(error or "the agent printed nothing")
        actions.extend(inspect(folder, start, case))
        actions.append({"kind": "state", "target": "the agent finished within the time limit", "ok": finished})
    if leaks(actions):
        raise RuntimeError("a transcript holds the operator's identity; nothing was written")
    return actions, used_model, version


def covered(case_name, root=ROOT):
    root = pathlib.Path(root)
    case_path = f"evals/cases/{case_name}.json"
    case = json.loads((root / case_path).read_text(encoding="utf-8"))
    arms = None if "arms" in case else json.loads((root / "evals" / eval_record.ARMS).read_text(encoding="utf-8"))
    files = eval_record.covered_files(case_path, case, workspace_files(root), arms, "evals")
    keys = eval_record.load_proof_keys(read_text(root, f"evals/{eval_record.PROOF_KEYS}"), "evals/proofkeys.py")
    return files, eval_record.guidance_hash({f: read_text(root, f) for f in files}, keys.strip)


def build_record(case, out, runs, files, digest, meta, arms=REQUIRED_ARMS, numbers=None, extra=None):
    """The record of a case whose every run is on disk: each run's grades, re-graded from its transcript.

    numbers: {arm: how many runs it holds}, when an arm was recorded once more. extra: keys added to the record,
    such as its "kind" or the arms "rerecorded"."""
    record = {"case": case["name"], "date": meta["date"], "playbook": case["playbook"], "covers": files,
              "guidance_sha256": digest, "runs_per_arm": runs, "agent": meta["agent"], "model": meta["model"],
              "sandbox": SANDBOX, **(extra or {}), "arms": {}}
    ids = [g["id"] for g in case["graders"]]
    for arm in arms:
        graded = []
        for number in range(1, (numbers or {}).get(arm, runs) + 1):
            name = f"{arm}-{number}.json"
            if not (out / name).is_file():   # only with --finish: a run that was never a trial
                continue
            results = dict(grading.grade(case, json.loads((out / name).read_text(encoding="utf-8"))))
            graded.append({"transcript": name, "passed": all(results.values()), "graders": results})
        record["arms"][arm] = {
            "runs_passing_every_grader": sum(run["passed"] for run in graded),
            "runs_passing_each_grader": {g: sum(run["graders"][g] for run in graded) for g in ids},
            "runs": graded,
        }
    return record


def operator_aliases():
    """The names of the aliases the operator's own interactive shell defines."""
    shell = os.environ.get("SHELL", "/bin/sh")
    try:
        done = subprocess.run([shell, "-i", "-c", "alias"], capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired):
        return set()
    names = set()
    for line in done.stdout.splitlines():
        name = line.split("=", 1)[0].strip()
        names.add(name[len("alias "):].strip() if name.startswith("alias ") else name)
    return {name for name in names if name}


PROBE = [
    ("a write outside the run's folder is refused", "touch ../outside-probe && echo WROTE-OUTSIDE", "WROTE-OUTSIDE"),
    ("the home folder cannot be listed", 'ls "$HOME" >/dev/null && echo LISTED-HOME', "LISTED-HOME"),
    ("the network is closed", "curl -sS -m 5 -o /dev/null https://example.com && echo REACHED-NETWORK", "REACHED-NETWORK"),
    ("no global git identity reaches the agent", "git config --global --get user.email || echo NO-GLOBAL-IDENTITY", None),
    ("none of the operator's aliases is loaded", "alias | cut -d= -f1 | tr '\\n' ' '; echo ALIASES-LISTED", None),
    ("python runs", "python3 -c 'print(6 * 7)'", None),
    ("a commit can be made in the run's folder", "echo x > probe.txt && git add probe.txt && git commit -q -m probe && echo COMMITTED", None),
]


def probe(model, timeout, save=None):
    """One agent run that tries to leave the sandbox. Returns (passed, [(what, held, output)], version)."""
    request = ("This is a sandbox test. Run each of these shell commands exactly as written, one Bash call each, "
               "in this order, and do not retry any of them in another way:\n" + "\n".join(f"- `{c}`" for _, c, _ in PROBE)
               + "\nThen use the Read tool on the file `" + str(start_up_file("/bin/zsh")) + "`. Then reply: done.")
    mine = operator_aliases()
    with tempfile.TemporaryDirectory() as scratch:
        folder = pathlib.Path(scratch) / "probe"
        folder.mkdir()
        git(folder, "init", "-q", "-b", "main")
        git(folder, "config", "user.name", "eval")
        git(folder, "config", "user.email", "eval@example.invalid")
        git(folder, "commit", "-q", "--allow-empty", "-m", "start")
        done = subprocess.run(agent_command(request, model), cwd=folder, env=agent_env(scratch),
                              capture_output=True, text=True, timeout=timeout)
        actions, _, version, error = to_transcript(done.stdout, folder)
        outside = (pathlib.Path(scratch) / "outside-probe").exists()
        committed = git(folder, "log", "--oneline").stdout.count("\n") == 2
    if save:
        pathlib.Path(save).write_text(json.dumps(actions, indent=2) + "\n", encoding="utf-8")
    outputs = {a["target"]: a.get("output", "") for a in actions if a["kind"] == "run"}
    results = []
    for what, command, marker in PROBE:
        out = outputs.get(command)
        if out is None:
            held = False
            what += " (the agent did not run it as written)"
        elif marker:
            held = marker not in out and not (marker == "WROTE-OUTSIDE" and outside)
        elif command.startswith("git config"):
            held = "NO-GLOBAL-IDENTITY" in out
        elif command.startswith("alias"):
            held = "ALIASES-LISTED" in out and not (set(out.split()) & mine)
        elif command.startswith("python3"):
            held = "42" in out
        else:
            held = "COMMITTED" in out and committed
        results.append((what, held, (out or "").strip()[-200:]))
    reads = [a for a in actions if a["kind"] == "read" and a["target"].endswith(".zshrc")]
    results.append(("the Read tool cannot open a file in the home folder", bool(reads) and not reads[-1]["ok"], ""))
    results.append(("the run reported no error", not error, error or ""))
    return all(held for _, held, _ in results), results, version


def plan_runs(args, case, files, digest, root=ROOT):
    """What this invocation records: (folder, {arm: (files, plugins, stripped)}, first run number, runs per arm,
    extra record keys, {arm: runs it will hold}). Raises ValueError with the reason when it cannot start."""
    out = root / "evals/runs" / case["name"]
    arms = arms_for(case, root)
    if args.one_time:
        given, plugins = one_time_arm(case, args.one_time, root)
        missing = [p for p in plugins if not (root / p).is_dir()]
        if missing:
            raise ValueError(f"the one-time arm {args.one_time} enables the plugin folder {missing[0]}, which does not exist")
        return (out / "one-time" / args.one_time, {args.one_time: (given, plugins, False)}, 1, args.runs,
                {"kind": "one-time", "arm": args.one_time}, {})
    if args.baseline:
        extra = {"kind": "baseline"}
        if args.attempt:
            extra.update({"page": case["playbook"], "milestone": args.attempt, "verdict": "not proven"})
        return out / "baseline", {"bare": (arms["bare"], [], True)}, 1, args.runs, extra, {}
    if args.rerecord:
        record_path = out / "record.json"
        record = json.loads(record_path.read_text(encoding="utf-8")) if record_path.is_file() else None
        if not record or record.get("guidance_sha256") != digest:
            raise ValueError("--rerecord adds to a current record: none is on disk, or what the hash covers changed")
        if args.rerecord in record.get("rerecorded", []):
            raise ValueError(f"the {args.rerecord} arm was already recorded once more; a record pools one re-record only")
        per = record["runs_per_arm"]
        return (out, {args.rerecord: (arms[args.rerecord], [], True)}, per + 1, per,
                {"rerecorded": record.get("rerecorded", []) + [args.rerecord]}, {args.rerecord: 2 * per})
    return out, {arm: (arms[arm], [], True) for arm in REQUIRED_ARMS}, 1, args.runs, {}, {}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run an eval case in three arms: guided, two-line and bare.")
    parser.add_argument("case", nargs="?")
    parser.add_argument("--model", default="haiku")
    parser.add_argument("--runs", type=int, default=15, help="runs per arm; one run says little, because models vary")
    parser.add_argument("--timeout", type=int, default=900, help="seconds allowed per run")
    parser.add_argument("--resume", action="store_true", help="keep the runs already on disk and run only the missing ones")
    parser.add_argument("--finish", action="store_true",
                        help="write the record from the runs on disk, when the runs that never started cannot be repeated")
    parser.add_argument("--budget", type=int, default=None, help="start at most this many agent runs")
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument("--rerecord", metavar="ARM", choices=REQUIRED_ARMS,
                        help="record one arm of a current record once more, and pool the two")
    parser.add_argument("--baseline", action="store_true", help="the bare arm alone, to a record the gate never counts")
    parser.add_argument("--attempt", metavar="MILESTONE", help="with --baseline: record it as a failed proof attempt")
    parser.add_argument("--one-time", metavar="ARM", help="an arm from evals/one-time.json, to a record the gate never reads")
    parser.add_argument("--probe", action="store_true", help="one agent run that tries to leave the sandbox")
    parser.add_argument("--save", help="with --probe: write the probe's transcript here")
    args = parser.parse_args(argv)

    if args.probe:
        passed, results, version = probe(args.model, args.timeout, args.save)
        for what, held, output in results:
            print(f"{'held' if held else 'FAILED'}  {what}" + ("" if held else f"\n        output: {output}"))
        print(f"\nClaude Code {version}: the sandbox {'held' if passed else 'did NOT hold'}")
        return 0 if passed else 1
    if not args.case:
        parser.error("name a case, or pass --probe")
    if sum(bool(x) for x in (args.rerecord, args.baseline, args.one_time)) > 1:
        parser.error("--rerecord, --baseline and --one-time are separate recordings; pass one")
    if args.attempt and (not args.baseline or not re.fullmatch(r"M[1-9][0-9]*", args.attempt)):
        parser.error("--attempt takes a milestone such as M4, with --baseline")
    if args.runs < eval_record.MIN_RUNS:
        parser.error(f"the gate needs {eval_record.MIN_RUNS} or more runs per arm")

    case = load_case(args.case)
    files, digest = covered(args.case)
    try:
        out, plan, first, per, extra, numbers = plan_runs(args, case, files, digest)
    except (ValueError, KeyError, OSError) as problem:
        print(f"run.py: {problem}", file=sys.stderr)
        return 2
    out.mkdir(parents=True, exist_ok=True)
    pending = out / ("pending-rerecord.json" if args.rerecord else "pending.json")
    if args.resume or args.finish:
        started = json.loads(pending.read_text(encoding="utf-8")) if pending.is_file() else {}
        if started.get("guidance_sha256") != digest or started.get("runs") != per:
            print("run.py: what the hash covers, or the number of runs, changed since these runs started; "
                  "start again without --resume", file=sys.stderr)
            return 2
    else:
        if args.rerecord:
            for old in out.glob(f"{args.rerecord}-*.json"):
                if int(old.stem.rsplit("-", 1)[1]) >= first:
                    old.unlink()
        else:
            for old in out.glob("*.json"):
                old.unlink()
        pending.write_text(json.dumps({"guidance_sha256": digest, "runs": per,
                                       "date": datetime.date.today().isoformat()}) + "\n", encoding="utf-8")
    started = json.loads(pending.read_text(encoding="utf-8"))

    jobs = [] if args.finish else [(arm, number) for number in range(first, first + per) for arm in plan
                                   if not (out / f"{arm}-{number}.json").is_file()]
    if args.budget is not None and len(jobs) > args.budget:
        print(f"run.py: {len(jobs)} runs are missing and the budget allows {args.budget}; nothing was started", file=sys.stderr)
        return 2
    print(f"running {case['name']}: {len(jobs)} runs on {args.model}, {args.workers} at a time ...", flush=True)
    lock, meta, failures = threading.Lock(), {}, []
    log = os.environ.get("WS_EVAL_RUN_LOG")

    def one(job):
        arm, number = job
        if log:
            with lock, open(log, "a", encoding="utf-8") as handle:
                handle.write(f"{datetime.datetime.now().isoformat(timespec='seconds')} {case['name']} {arm}-{number}\n")
        given, plugins, stripped = plan[arm]
        try:
            actions, model, version = run_once(case, args.model, given, args.timeout, plugins, stripped)
        except (NotATrial, RuntimeError) as problem:
            with lock:
                failures.append(f"{arm}-{number}: {problem}")
                print(f"  {arm}-{number}: not recorded: {problem}", flush=True)
            return
        (out / f"{arm}-{number}.json").write_text(json.dumps(actions, indent=2) + "\n", encoding="utf-8")
        passed = all(ok for _, ok in grading.grade(case, actions))
        with lock:
            meta.update({"agent": f"Claude Code {version}", "model": model})
            pending.write_text(json.dumps({**started, **meta}) + "\n", encoding="utf-8")
            print(f"  {arm}-{number}: {'passed every grader' if passed else 'failed a grader'}", flush=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(one, jobs))
    if failures:
        print(f"\n{len(failures)} run(s) were not trials and were not recorded. Run again with --resume.", file=sys.stderr)
        return 1

    meta.update({key: started.get(key) for key in ("agent", "model") if not meta.get(key)})
    meta["date"] = started["date"]
    if args.rerecord:
        old = json.loads((out / "record.json").read_text(encoding="utf-8"))
        meta.update({"date": old["date"], "agent": old["agent"], "model": old["model"]})
        extra = {**{k: v for k, v in old.items() if k == "kind"}, **extra, "rerecorded_on": started["date"]}
        arm_names = list(old["arms"])
        numbers = {**{arm: len(old["arms"][arm]["runs"]) for arm in arm_names}, **numbers}
    else:
        arm_names = list(plan)
    record = build_record(case, out, per, files, digest, meta, arm_names, numbers, extra)
    (out / "record.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    pending.unlink()

    print(f"\n{'runs passing every grader':<44}" + "".join(f"{arm:>10}" for arm in arm_names))
    for grader in case["graders"]:
        print(f"{grader['id']:<44}" + "".join(f"{record['arms'][arm]['runs_passing_each_grader'][grader['id']]:>10}"
                                             for arm in arm_names))
    print(f"{'every grader':<44}" + "".join(f"{record['arms'][arm]['runs_passing_every_grader']:>10}" +
                                            f"/{len(record['arms'][arm]['runs'])}" for arm in arm_names))
    if record.get("kind"):
        print(f"\na {record['kind']} record: the gate never counts it as passing")
        return 0
    problem = eval_record.judge(record, list(REQUIRED_ARMS), [g["id"] for g in case["graders"]])
    print(f"\n{'the record passes the gate' if not problem else 'the record does not pass the gate: ' + problem}")
    return 0 if not problem else 1


if __name__ == "__main__":
    sys.exit(main())
