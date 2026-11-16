#!/usr/bin/env python3
"""Run an eval case against a real agent, in each of three arms.

    python3 evals/run.py fix-a-bug --model haiku --runs 15
    python3 evals/run.py --probe          # one agent run that checks the sandbox holds

The arms, from evals/arms.json:

  guided    the workspace's real contract (AGENTS.md, CLAUDE.md), INDEX.md, the
            playbook and the definition of done
  two-line  a CLAUDE.md of two lines that ask for the playbook's two habits
  bare      the code alone

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
from parts import eval_record  # noqa: E402
from wslib import snapshot as snapshots  # noqa: E402

OTHER_SESSION = {
    "README.md": "\nNote to self: ask whether Export should include cancelled orders.\n",   # appended to a tracked file
    "notes/todo.txt": "Draft, not ready to commit.\n",                                       # a new untracked file
}
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
READ_TOOLS = {"Read", "Grep", "Glob"}
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
    arms = json.loads((root / "evals" / eval_record.ARMS).read_text(encoding="utf-8"))
    eval_record.arm_sources(arms)
    if tuple(arms) != REQUIRED_ARMS:
        raise ValueError(f"evals/arms.json must name the arms {', '.join(REQUIRED_ARMS)}, in that order")
    return arms


def load_case(name, root=ROOT):
    return json.loads((root / "evals/cases" / f"{name}.json").read_text(encoding="utf-8"))


def prepare(folder, case, files, root=ROOT):
    """Build the repository the agent starts in. files: the arm's {destination: source}. Returns the starting commit.

    The scaffold's files are the ones the eval hash covers, no more: a file git ignores, such as a .DS_Store,
    is neither hashed nor given to the agent."""
    scaffold = case["scaffold_dir"].strip("/") + "/"
    for path in snapshots.Tree(root).paths():
        if path.startswith(scaffold):
            (folder / path[len(scaffold):]).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / path, folder / path[len(scaffold):])
    for destination, source in files.items():
        (folder / destination).parent.mkdir(parents=True, exist_ok=True)
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


def agent_command(request, model):
    """Claude Code, headless, with its permissions bypassed only inside its sandbox."""
    return ["claude", "-p", request, "--model", model, "--output-format", "stream-json", "--verbose",
            "--setting-sources", "project", "--settings", json.dumps(SETTINGS), "--strict-mcp-config",
            "--no-session-persistence", "--permission-mode", "bypassPermissions"]


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


def leaks(actions):
    """What in a transcript would identify the operator or this machine. Empty when it is safe to write."""
    text = json.dumps(actions).lower()
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
    return state


class NotATrial(Exception):
    """The agent never started: an outage or a usage limit, not something the agent did."""


def run_once(case, model, files, timeout):
    with tempfile.TemporaryDirectory() as scratch:
        folder = pathlib.Path(scratch) / "orders"
        folder.mkdir()
        start = prepare(folder, case, files)
        env = agent_env(scratch)
        try:
            done = subprocess.run(agent_command(case["request"], model), cwd=folder, env=env,
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
    case_path = f"evals/cases/{case_name}.json"
    case = json.loads((root / case_path).read_text(encoding="utf-8"))
    tree = snapshots.Tree(root)
    arms = json.loads((root / "evals" / eval_record.ARMS).read_text(encoding="utf-8"))
    files = eval_record.covered_files(case_path, case, list(tree.paths()), arms, "evals")
    return files, eval_record.guidance_hash({f: tree.read(f) or "" for f in files})


def build_record(case, out, runs, files, digest, meta):
    """The record of a case whose every run is on disk: each run's grades, re-graded from its transcript."""
    record = {"case": case["name"], "date": meta["date"], "playbook": case["playbook"], "covers": files,
              "guidance_sha256": digest, "runs_per_arm": runs, "agent": meta["agent"], "model": meta["model"],
              "sandbox": SANDBOX, "arms": {}}
    ids = [g["id"] for g in case["graders"]]
    for arm in REQUIRED_ARMS:
        graded = []
        for number in range(1, runs + 1):
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
    if args.runs < eval_record.MIN_RUNS:
        parser.error(f"the gate needs {eval_record.MIN_RUNS} or more runs per arm")

    case = load_case(args.case)
    arms = load_arms()
    files, digest = covered(args.case)
    out = ROOT / "evals/runs" / case["name"]
    out.mkdir(parents=True, exist_ok=True)
    pending = out / "pending.json"
    if args.resume or args.finish:
        started = json.loads(pending.read_text(encoding="utf-8")) if pending.is_file() else {}
        if started.get("guidance_sha256") != digest or started.get("runs") != args.runs:
            print("run.py: what the hash covers, or the number of runs, changed since these runs started; "
                  "start again without --resume", file=sys.stderr)
            return 2
    else:
        for old in out.glob("*.json"):
            old.unlink()
        pending.write_text(json.dumps({"guidance_sha256": digest, "runs": args.runs,
                                       "date": datetime.date.today().isoformat()}) + "\n", encoding="utf-8")
    started = json.loads(pending.read_text(encoding="utf-8"))

    jobs = [] if args.finish else [(arm, number) for number in range(1, args.runs + 1) for arm in REQUIRED_ARMS
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
        try:
            actions, model, version = run_once(case, args.model, arms[arm]["files"], args.timeout)
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
    record = build_record(case, out, args.runs, files, digest, meta)
    (out / "record.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    pending.unlink()

    print(f"\n{'runs passing, of ' + str(args.runs):<44}" + "".join(f"{arm:>10}" for arm in REQUIRED_ARMS))
    for grader in case["graders"]:
        print(f"{grader['id']:<44}" + "".join(f"{record['arms'][arm]['runs_passing_each_grader'][grader['id']]:>10}"
                                             for arm in REQUIRED_ARMS))
    print(f"{'every grader':<44}" + "".join(f"{record['arms'][arm]['runs_passing_every_grader']:>10}" for arm in REQUIRED_ARMS))
    problem = eval_record.judge(record, list(arms), [g["id"] for g in case["graders"]])
    print(f"\n{'the record passes the gate' if not problem else 'the record does not pass the gate: ' + problem}")
    return 0 if not problem else 1


if __name__ == "__main__":
    sys.exit(main())
