"""The hook case runner: every hook event, called for real, the way an agent tool calls it, and timed.

A part's own cases (parts/<name>.cases.json) call its decide function in this process, with the facts already
filled in. They cannot see the launcher, the wiring, the adapters, the lease file or git. This runner can: each
case builds a scratch repository from this repository's tracked files, seeds what the case needs (a lease held
by a live or a dead process, a local remote that is ahead, a linked worktree, uncommitted files), then runs the
wiring command the agent tool's own settings give for the event, through wslib/launch.sh, with the tool's own
payload on standard input. It checks the exit code and the output, and times the call.

    python3 tests/hook_cases.py            # run every case, print each row's median time, exit 1 on a failure
    python3 tests/hook_cases.py -k lease   # only the cases whose name holds "lease"

The cases are in tests/hooks/<event>.json. A case:
    {"name": text, "tool": "claude-code" | "codex", "payload": {...}, "exit": 0 | 2,
     "output": [texts the call must print], "absent": [texts it must not print],
     "env": {NAME: value}, "repeat": n (default 5), "row": "git push" | "gh write" (time it on that row),
     "setup": {"remote": true, "remote_ahead": true, "worktree": true, "files": {path: text},
               "lease": {"session": text, "pid": "live" | "dead" | "self", "age": seconds}},
     "lease_after": session id or null (who holds the lease once the call is done)}
Text in a payload or env value may name {root}, the scratch main working copy; {worktree}, its linked worktree;
{live_pid}, a process that runs for the whole case; {dead_pid}, one that has exited; and {self_pid}, this runner.
The setup is applied again before each repeat, so every repeat starts from the same state.

Each event's hooks, and the two rows of their own, are held to a time budget, as the median of every call made
for them. On Linux and macOS a median over its budget fails the run; on Windows it is reported only, since
starting a process there costs several times more. A stop hook's budget is the stop gate's own 20 seconds; a
session-start hook's is 2 seconds against a local remote, so every session-start case names one. An event the
engine knows with no case fails the run, so a new event cannot arrive untimed.
See docs/parts.md#the-hook-case-runner.
"""
import argparse
import json
import os
import pathlib
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
CASES = ROOT / "tests" / "hooks"
sys.path.insert(0, str(ROOT))

from wslib import parts as partlib  # noqa: E402

# Seconds. The before-tool hooks and after-edit run on every tool call, so they get the tightest budget.
BUDGETS = {
    "before-shell": 0.2, "before-edit": 0.2, "before-handoff": 0.2, "after-edit": 0.2,
    "git push": 0.2, "gh write": 0.2,
    "session-start": 2.0, "stop": 20.0,
}
ROWS = ("git push", "gh write")     # rows of their own, timed apart from the rest of before-shell
WIRING = {"claude-code": ".claude/settings.json", "codex": ".codex/hooks.json"}
SETUP_KEYS = {"remote", "remote_ahead", "worktree", "files", "lease"}
CASE_KEYS = {"name", "tool", "payload", "exit", "output", "absent", "env", "repeat", "row", "setup", "lease_after"}
REPEAT = 5
CALL_TIMEOUT = 60
LEASE, LEDGER = "ws-lease.json", "ws-ledger"
# Variables git sets for a hook; a scratch repository's git calls must not inherit them.
GIT_VARIABLES = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_PREFIX",
                 "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_QUARANTINE_PATH", "GIT_CONFIG_PARAMETERS")


class CaseError(Exception):
    pass


def shell():
    """The POSIX shell an agent tool runs a hook command with. On Windows, Git's own bash, never WSL's."""
    if os.name == "nt":
        git = shutil.which("git")
        candidate = git and pathlib.Path(git).resolve().parent.parent / "bin" / "bash.exe"
        if candidate and candidate.exists():
            return str(candidate)
        raise CaseError("no Git bash found next to git, so the wiring cannot be run")
    found = shutil.which("sh")
    if not found:
        raise CaseError("no sh on the path, so the wiring cannot be run")
    return found


def wiring(root, tool, event):
    """The command the tool's own settings run for the event, as written there."""
    try:
        settings = json.loads((pathlib.Path(root) / WIRING[tool]).read_text(encoding="utf-8"))
    except (KeyError, OSError, ValueError) as error:
        raise CaseError(f"cannot read the {tool} wiring: {error}")
    for entries in settings.get("hooks", {}).values():
        for entry in entries:
            for hook in entry.get("hooks", []):
                found = re.search(r"\bhook ([a-z-]+)\b", hook.get("command", ""))
                if found and found.group(1) == event:
                    return hook["command"]
    raise CaseError(f"{WIRING[tool]} wires no hook for {event}")


def budget_verdict(row, median, platform=None):
    """'ok', 'over' (fails the run) or 'report' (over budget on Windows, or a row with no budget: printed only)."""
    platform = os.name if platform is None else platform
    limit = BUDGETS.get(row)
    if limit is None or median <= limit:
        return "ok" if limit is not None else "report"
    return "report" if platform == "nt" else "over"


def load_cases(folder=CASES):
    """{event: [case, ...]} from folder/<event>.json. Raises CaseError on a malformed file or case."""
    found = {}
    for file in sorted(pathlib.Path(folder).glob("*.json")):
        event = file.stem
        if event not in partlib.EVENTS:
            raise CaseError(f"{file.name}: {event} is not an event the engine knows ({', '.join(partlib.EVENTS)})")
        try:
            cases = json.loads(file.read_text(encoding="utf-8"))
        except ValueError as error:
            raise CaseError(f"{file.name}: {error}")
        if not isinstance(cases, list) or not cases:
            raise CaseError(f"{file.name}: holds no cases")
        for case in cases:
            problem = malformed(event, case)
            if problem:
                raise CaseError(f"{file.name}: {problem}: {json.dumps(case)[:200]}")
        found[event] = cases
    return found


def malformed(event, case):
    if not isinstance(case, dict) or not isinstance(case.get("name"), str):
        return "every case needs a name"
    unknown = sorted(set(case) - CASE_KEYS)
    if unknown:
        return f"unknown key {unknown[0]!r}"
    if case.get("tool") not in WIRING:
        return f"tool must be one of {sorted(WIRING)}"
    if not isinstance(case.get("payload"), dict) or case.get("exit") not in (0, 2):
        return 'needs a "payload" object and an "exit" of 0 or 2'
    if case.get("row") is not None and (event != "before-shell" or case["row"] not in ROWS):
        return f'a "row" is one of {ROWS}, on a before-shell case'
    setup = case.get("setup", {})
    if not isinstance(setup, dict) or set(setup) - SETUP_KEYS:
        return f"setup takes only {sorted(SETUP_KEYS)}"
    lease = setup.get("lease")
    if lease is not None and (not isinstance(lease, dict) or lease.get("pid") not in ("live", "dead", "self")
                              or not isinstance(lease.get("session"), str)):
        return 'a seeded lease needs a "session" and a "pid" of "live", "dead" or "self"'
    if event == "session-start" and not setup.get("remote"):
        return "a session-start case runs against a local remote: set setup.remote"
    if not isinstance(case.get("repeat", REPEAT), int) or case.get("repeat", REPEAT) < 1:
        return '"repeat" is a whole number, 1 or more'
    return None


NO_HOOKS = pathlib.Path(tempfile.gettempdir()) / "hook-cases-no-hooks"   # setup runs no git hook, not even a global one


def git(folder, *args):
    NO_HOOKS.mkdir(exist_ok=True)
    done = subprocess.run(["git", "-C", str(folder), "-c", "user.name=hook cases", "-c", "user.email=cases@example.invalid",
                           "-c", "commit.gpgsign=false", "-c", "protocol.file.allow=always",
                           "-c", f"core.hooksPath={NO_HOOKS.as_posix()}", *args],
                          capture_output=True, env=clean_environment(), stdin=subprocess.DEVNULL)
    if done.returncode != 0:
        raise CaseError(f"git {' '.join(args)} failed in {folder}: {done.stderr.decode('utf-8', 'replace').strip()}")
    return done.stdout.decode("utf-8", "replace")


def clean_environment(extra=None):
    env = {key: value for key, value in os.environ.items() if key not in GIT_VARIABLES and not key.startswith("GIT_CONFIG_")}
    env.update(extra or {})
    return env


class Scratch:
    """A template copy of this repository, committed once; each case gets its own copy of it."""

    def __init__(self, source=ROOT):
        self.folder = pathlib.Path(tempfile.mkdtemp(prefix="hook-cases-")).resolve()
        self.template = self.folder / "template"
        names = [n for n in subprocess.run(["git", "-C", str(source), "ls-files", "-z"], capture_output=True,
                                           check=True).stdout.decode("utf-8").split("\0") if n]
        for name in names:
            if (source / name).is_file():
                (self.template / name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source / name, self.template / name)   # keeps the launcher executable
        git(self.template, "init", "-q", "-b", "main")
        git(self.template, "add", "--all")
        git(self.template, "commit", "-q", "--no-verify", "-m", "scratch copy")
        # Warm the engine's compiled files once, so no case's first call pays for compiling them.
        subprocess.run([shell(), str(self.template / "wslib" / "launch.sh"), "--version"], capture_output=True,
                       env=clean_environment(), stdin=subprocess.DEVNULL)
        self.live = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(3600)"])
        done = subprocess.Popen([sys.executable, "-c", "pass"])
        done.wait()
        self.dead = done.pid
        self.count = 0

    def close(self):
        self.live.kill()
        self.live.wait()
        shutil.rmtree(self.folder, ignore_errors=True)

    def build(self, setup):
        """A fresh copy for one case: {"root", "worktree", "common"}."""
        self.count += 1
        root = self.folder / f"case-{self.count}"
        shutil.copytree(self.template, root, symlinks=True)
        places = {"root": root, "common": root / ".git", "worktree": None}
        if setup.get("remote"):
            origin = self.folder / f"case-{self.count}-origin.git"
            git(self.folder, "init", "-q", "--bare", "-b", "main", str(origin))
            git(root, "remote", "add", "origin", str(origin))
            git(root, "push", "-q", "--no-verify", "-u", "origin", "main")
            if setup.get("remote_ahead"):
                other = self.folder / f"case-{self.count}-other"
                git(self.folder, "clone", "-q", str(origin), str(other))
                (other / "AHEAD.md").write_text("# Ahead\n", encoding="utf-8")
                git(other, "add", "AHEAD.md")
                git(other, "commit", "-q", "--no-verify", "-m", "ahead")
                git(other, "push", "-q", "--no-verify", "origin", "main")
        if setup.get("worktree"):
            worktree = self.folder / f"case-{self.count}-worktree"
            git(root, "worktree", "add", "-q", str(worktree), "-b", "side")
            places["worktree"] = worktree
        for path, text in setup.get("files", {}).items():
            (root / path).parent.mkdir(parents=True, exist_ok=True)
            (root / path).write_text(text, encoding="utf-8")
        return places

    def seed(self, places, setup):
        """The state each repeat starts from: the case's lease, or none, and no edit ledger."""
        common = places["common"]
        for folder in [common] + sorted((common / "worktrees").glob("*")):
            ledger = folder / LEDGER
            if ledger.exists():
                ledger.unlink()
        lease_file = common / LEASE
        lease = setup.get("lease")
        if lease is None:
            if lease_file.exists():
                lease_file.unlink()
            return
        pid = {"live": self.live.pid, "dead": self.dead, "self": os.getpid()}[lease["pid"]]
        taken = time.time() - float(lease.get("age", 60))
        lease_file.write_text(json.dumps({"session": lease["session"], "pid": pid, "taken": taken}), encoding="utf-8")

    def fill(self, value, places):
        """Fill the placeholders in every text inside value."""
        names = {"root": str(places["root"]), "worktree": str(places["worktree"] or ""),
                 "live_pid": str(self.live.pid), "dead_pid": str(self.dead), "self_pid": str(os.getpid())}
        if isinstance(value, str):
            return re.sub(r"\{(root|worktree|live_pid|dead_pid|self_pid)\}", lambda m: names[m.group(1)], value)
        if isinstance(value, list):
            return [self.fill(item, places) for item in value]
        if isinstance(value, dict):
            return {key: self.fill(item, places) for key, item in value.items()}
        return value


def call(scratch, places, event, case):
    """One real call: (exit code, output, seconds)."""
    root = places["root"]
    payload = scratch.fill(case["payload"], places)
    cwd = payload.get("cwd") if isinstance(payload.get("cwd"), str) and payload.get("cwd") else str(root)
    env = clean_environment({"CLAUDE_PROJECT_DIR": pathlib.Path(root).as_posix(), "WS_DENY_LIST": ""})
    env.update(scratch.fill(case.get("env", {}), places))
    command = wiring(root, case["tool"], event)
    start = time.perf_counter()
    try:
        done = subprocess.run([shell(), "-c", command], input=json.dumps(payload).encode("utf-8"), cwd=cwd,
                              capture_output=True, env=env, timeout=CALL_TIMEOUT)
    except subprocess.TimeoutExpired:
        return None, f"no answer in {CALL_TIMEOUT} seconds", float(CALL_TIMEOUT)
    seconds = time.perf_counter() - start
    output = (done.stdout + done.stderr).decode("utf-8", "replace")
    return done.returncode, output, seconds


def judge(case, code, output, holder):
    """What is wrong with one call's result, or None."""
    if code != case["exit"]:
        return f"exit {code}, expected {case['exit']}: {output.strip()[:300]}"
    missing = [text for text in case.get("output", []) if text not in output]
    if missing:
        return f"the output lacks {missing[0]!r}: {output.strip()[:300]}"
    present = [text for text in case.get("absent", []) if text in output]
    if present:
        return f"the output holds {present[0]!r}: {output.strip()[:300]}"
    if "lease_after" in case and holder != case["lease_after"]:
        return f"the lease is held by {holder!r} after the call, expected {case['lease_after']!r}"
    return None


def holder_of(places):
    try:
        return json.loads((places["common"] / LEASE).read_text(encoding="utf-8")).get("session")
    except (OSError, ValueError):
        return None


def run(cases, out=sys.stdout, platform=None, repeat=None):
    """Run the cases and print the timing table. Returns (failures, rows), where rows is
    {row: (samples, median seconds, verdict)}. A failure is "event / case: what went wrong"."""
    failures, samples = [], {}
    scratch = Scratch()
    try:
        for event, listed in cases.items():
            for case in listed:
                label = f"{event} / {case['name']}"
                try:
                    places = scratch.build(case.get("setup", {}))
                    for _ in range(case.get("repeat", REPEAT) if repeat is None else min(repeat, case.get("repeat", REPEAT))):
                        scratch.seed(places, case.get("setup", {}))
                        code, output, seconds = call(scratch, places, event, case)
                        samples.setdefault(case.get("row") or event, []).append(seconds)
                        problem = judge(case, code, output, holder_of(places))
                        if problem:
                            failures.append(f"{label}: {problem}")
                            break
                except CaseError as error:
                    failures.append(f"{label}: {error}")
    finally:
        scratch.close()
    rows = {}
    for row in list(partlib.EVENTS) + list(ROWS):
        if row not in samples:
            continue
        median = statistics.median(samples[row])
        rows[row] = (len(samples[row]), median, budget_verdict(row, median, platform))
    print(f"{'hook':<16}{'calls':>6}{'median ms':>11}{'budget ms':>11}  verdict", file=out)
    for row, (count, median, verdict) in rows.items():
        limit = BUDGETS.get(row)
        shown = {"ok": "ok", "over": "OVER BUDGET", "report": "reported only"}[verdict]
        print(f"{row:<16}{count:>6}{median * 1000:>11.0f}{'' if limit is None else f'{limit * 1000:.0f}':>11}  {shown}",
              file=out)
    return failures, rows


def missing_events(cases):
    """Events the engine knows, and rows the runner times, that no case covers."""
    rows = {case.get("row") for listed in cases.values() for case in listed}
    return [event for event in partlib.EVENTS if event not in cases] + [row for row in ROWS if row not in rows]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run every hook event for real, through the launcher, and time it.")
    parser.add_argument("-k", metavar="TEXT", help="only the cases whose name holds TEXT")
    args = parser.parse_args(argv)
    try:
        cases = load_cases()
    except CaseError as error:
        print(f"hook cases: {error}", file=sys.stderr)
        return 2
    problems = [] if args.k else [f"no case covers {name}" for name in missing_events(cases)]
    if args.k:
        cases = {event: [c for c in listed if args.k in c["name"]] for event, listed in cases.items()}
        cases = {event: listed for event, listed in cases.items() if listed}
    failures, rows = run(cases)
    over = [f"{row}: median {median * 1000:.0f} ms is over its {BUDGETS[row] * 1000:.0f} ms budget"
            for row, (_, median, verdict) in rows.items() if verdict == "over"]
    for line in problems + failures + over:
        print(f"FAIL  {line}")
    total = sum(len(listed) for listed in cases.values())
    print(f"{total - len(failures)} of {total} cases pass"   # a case stops at its first failure, so it adds one at most
          + ("; Windows: times are reported, not held to the budget" if os.name == "nt" else ""))
    return 1 if problems or failures or over else 0


if __name__ == "__main__":
    sys.exit(main())
