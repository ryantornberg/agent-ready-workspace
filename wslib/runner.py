"""The runner: the commands ws.py offers. ws.py, at the top of the workspace, only calls main() here.

Every command but selftest runs each part's cases as it loads the part, and refuses a part with a failing case.
A hook call loads only the hooks for its event, so a broken check cannot refuse a shell command or an edit.
The commit check reads the staged manifest, parts and cases. A part an older manifest used must still be
used, or be listed under "retired" with a reason: the last commit's manifest decides locally, and the base
commit's manifest in CI.

The events are before-shell, before-edit, before-handoff, session-start and session-end. A hook reads the workspace's versioned event
shape, or one agent tool's payload through that tool's adapter (wslib/events.py), and refuses anything else.
A hook with MODE = "remind" never refuses: the agent is shown its reason and the call goes ahead.

An allowed edit is recorded in the edit ledger of the working copy that holds it (wslib/ledger.py). A
before-shell reminder opens the ledger of the folder the agent tool says its session runs in, when that
working copy has uncommitted changes. While a ledger is open, the commit check fails a staged path no edit
tool wrote (parts/edit_ledger.py).

The pre-push hook runs `check --push REMOTE`, with git's list of updated refs on standard input. For each
ref pushed, the parts and the manifest come from the remote's current tip, not from the push, so a push
cannot weaken the check that judges it. A push whose range cannot be listed, or whose remote tip holds no
readable manifest, is refused when it goes to main.

A session hook only reminds, and a session start or end never fails: on any error the runner prints
nothing and exits 0. Before the session hooks run, the runner adds the facts they declare in NEEDS:
"findings", the findings of the check each names in its config "part", run on the session's own working
copy; and "pins", for each pinned repository there, how far its checkout is behind its upstream's
default branch. See docs/decisions/0004-the-hook-contract.md.

Exit codes: 0 clean; 1 a check found an error or a case failed; 2 a hook refused, or the setup is
wrong. A hook that cannot decide exits 2 as well: it fails closed.
"""
import argparse
import os
import pathlib
import subprocess
import sys

from . import VERSION
from . import events
from . import gitcall
from . import lease as leases
from . import ledger as ledgers
from . import parts as partlib
from . import snapshot as snapshots

ROOT = pathlib.Path(__file__).resolve().parent.parent   # the workspace: the folder that holds ws.py and wslib/


def command_list(root, _args):
    for part in partlib.load_all(root):
        kind = f"check in {', '.join(part.phases)}" if part.kind == "check" else f"hook on {part.event}"
        print(f"{part.name:<16} {kind:<30} {len(part.cases)} cases")
    return 0


def command_selftest(root, _args):
    failed = 0
    for part in partlib.load_all(root, run_cases=False):
        failures = part.failed_cases()
        failed += len(failures)
        print(f"{'FAIL' if failures else 'ok  '}  {part.name}: {len(part.cases) - len(failures)} of {len(part.cases)} cases")
        for line in failures:
            print(f"      {line}")
    return 1 if failed else 0


def command_message(root, args):
    """The commit-msg hook: the message, and the author and committer, against the parts that read them."""
    try:
        message = pathlib.Path(args.message).read_bytes()
    except OSError as error:
        raise partlib.PartError(f"cannot read the commit message {args.message}: {error}")
    index = snapshots.Index(root)
    if not index.is_file(partlib.MANIFEST):
        raise partlib.PartError(f"no {partlib.MANIFEST} is staged, so the commit cannot be checked")
    manifest = partlib.parse_manifest(index.read(partlib.MANIFEST) or "", f"staged {partlib.MANIFEST}")
    snapshot = snapshots.Message(root, message)
    errors = 0
    for part in partlib.load_all(root, manifest, snapshot=index):
        if part.kind == "check" and getattr(part.module, "COMMIT_MESSAGE", False) is True:
            for found in part.run(snapshot):
                errors += found["level"] == "error"
                print(f"{found['level']}: {found['path']}:{found['line']}: {found['message']}  [{part.name}]")
    if errors:
        print(f"\n{errors} error(s). Reword the message, or fix the identity, and commit again.")
    return 1 if errors else 0


ZERO = "0" * 40
# Variables git sets for a hook; a git call on another repository must not inherit them.
GIT_VARIABLES = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_PREFIX",
                 "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_QUARANTINE_PATH")


def _git_text(root, *args):
    """A git call's output as text, or None when it fails. Carriage returns are dropped, for Git Bash on Windows."""
    env = {key: value for key, value in os.environ.items() if key not in GIT_VARIABLES}
    done = subprocess.run(["git", "-C", str(root), "-c", "core.quotePath=false", *args], capture_output=True, env=env)
    if done.returncode != 0:
        return None
    return done.stdout.decode("utf-8", "surrogateescape").replace("\r\n", "\n")


def pushed_commits(root, local, remote):
    """The commits a push adds, merges left out, each with its subject and paths. Raises PartError when it cannot list them."""
    span = [local] if remote == ZERO else [f"{remote}..{local}"]
    text = _git_text(root, "log", "--no-merges", "--format=%x01%H%x02%s", "--name-only", *span, "--")
    if text is None:
        raise partlib.PartError(f"the commits between {remote[:7]} and {local[:7]} cannot be listed. "
                                f"Fetch first (git fetch), then push again.")
    commits = []
    for block in text.split("\x01")[1:]:
        head, _, names = block.partition("\n")
        sha, _, subject = head.partition("\x02")
        commits.append({"commit": sha.strip(), "subject": subject.strip(),
                        "paths": [line for line in names.split("\n") if line.strip()]})
    return commits


def push_parts(root, base):
    """The manifest and the push checks, as the commit `base` holds them. None when it holds no readable manifest."""
    text = _git_text(root, "show", f"{base}:{partlib.MANIFEST}")
    if text is None:
        return None
    manifest = partlib.parse_manifest(text, f"{partlib.MANIFEST} at {base[:7]}")
    files = {partlib.MANIFEST: text}
    for entry in manifest["parts"]:
        relative = partlib.source_of(root, entry)[1]
        for name in (relative, relative[:-len(".py")] + ".cases.json"):
            found = _git_text(root, "show", f"{base}:{name}")
            if found is not None:
                files[name] = found
    loaded = partlib.load_all(root, manifest, snapshot=snapshots.Memory(files))
    return [part for part in loaded if part.kind == "check" and "push" in part.phases]


def command_push(root, args):
    """The pre-push hook. Standard input holds one line per ref: local ref, local hash, remote ref, remote hash."""
    errors = 0
    for line in sys.stdin.read().splitlines():
        if not line.strip():
            continue
        fields = line.split()
        if len(fields) != 4:
            raise partlib.PartError(f"pre-push: cannot read the line {line!r}")
        _, local, remote_ref, remote = fields
        if set(local) == {"0"}:
            continue                    # a deletion adds no commit
        remote = ZERO if set(remote) == {"0"} else remote
        if remote != ZERO and _git_text(root, "cat-file", "-e", f"{remote}^{{commit}}") is None:
            raise partlib.PartError(f"the remote's tip {remote[:7]} is not in this clone, so the push cannot be "
                                    f"checked. Fetch first (git fetch), then push again.")
        base = local if remote == ZERO else remote
        parts = push_parts(root, base)
        if parts is None:
            if remote_ref == "refs/heads/main":
                raise partlib.PartError(f"{partlib.MANIFEST} cannot be read at {base[:7]}, the tip this push builds on, "
                                        f"so a push to main cannot be checked; see docs/changing-the-machinery.md")
            continue
        for part in parts:
            if remote_ref != f"refs/heads/{part.config.get('branch', 'main')}":
                continue
            snapshot = snapshots.Memory({}, pushed=pushed_commits(root, local, remote))
            for found in part.run(snapshot):
                errors += found["level"] == "error"
                print(f"{found['level']}: {found['path']}:{found['line']}: {found['message']}  [{part.name}]",
                      file=sys.stderr)
    if errors:
        print(f"\n{errors} error(s). The push was refused.", file=sys.stderr)
    return 1 if errors else 0


def command_check(root, args):
    if args.push is not None:
        return command_push(root, args)
    if args.message is not None:
        return command_message(root, args)
    if args.staged:
        # The commit decides: its manifest, its parts and their cases, not the files on disk.
        # The last commit's manifest comes in the same batch read as the staged files: three git processes in all.
        last = f"HEAD:./{partlib.MANIFEST}"
        snapshot = snapshots.Index(root, extra=(last,))
        if not snapshot.is_file(partlib.MANIFEST):
            raise partlib.PartError(f"no {partlib.MANIFEST} is staged, so the commit cannot be checked")
        manifest = partlib.parse_manifest(snapshot.read(partlib.MANIFEST) or "", f"staged {partlib.MANIFEST}")
        parts = partlib.load_all(root, manifest, snapshot=snapshot)
        where = "the last commit"
        required, problem = partlib.required_from(snapshot.object(last), where)
    else:
        manifest = partlib.load_manifest(root)
        snapshot = snapshots.Tree(root, args.changed)
        required, problem = partlib.required_parts(root)
        where = "the last commit"
        if args.changed_from is not None:
            since, changed_problem = snapshots.changed_since(root, args.changed_from)
            if changed_problem:
                # Fail closed: with nothing to compare against, every file counts as changed.
                print(f"warning: {changed_problem}; every file is treated as changed")
                since = list(snapshot.paths())
            snapshot = snapshots.Tree(root, list(args.changed) + since)
            if not args.changed_from or set(args.changed_from) == {"0"}:
                required, problem = set(), None
                print("warning: no base commit, so no part is required to stay in the manifest")
            else:
                required, problem = partlib.required_parts(root, args.changed_from)
                where = args.changed_from
        parts = partlib.load_all(root, manifest)

    # Only the checks for this phase run. The commit is the default, so check and check --staged agree.
    parts = [part for part in parts if part.kind == "check" and args.phase in part.phases]
    if not parts:
        print(f"no check runs in the {args.phase} phase")
    findings = [(found, "runner") for found in partlib.dropped_parts(manifest, required, where)]
    if problem:
        # Fail closed: the parts that must stay cannot be known.
        findings.append((partlib.finding(partlib.MANIFEST, 1, f"{problem}, so the required parts are unknown"), "runner"))
    for part in parts:
        findings += [(found, part.name) for found in part.run(snapshot)]
    errors = 0
    for found, by in findings:
        errors += found["level"] == "error"
        print(f"{found['level']}: {found['path']}:{found['line']}: {found['message']}  [{by}]")
    if errors:
        print(f"\n{errors} error(s).")
    return 1 if errors else 0


def session_facts(root, hooks, event):
    """The facts the session hooks declare in NEEDS, worked out on the working copy the session runs in."""
    found = ledgers.working_copy(pathlib.Path(event["cwd"]).resolve() / "probe",
                                 ledgers.common_dir(ledgers.git_dir(root) or root))
    top = found[0] if found else root
    needs = {need for part in hooks for need in getattr(part.module, "NEEDS", ())}
    facts = {}
    tree = snapshots.Tree(top) if needs else None
    if "findings" in needs:
        manifest = partlib.load_manifest(root)
        facts["findings"] = {}
        for name in {part.config.get("part") for part in hooks if part.config.get("part")}:
            entry = next((e for e in manifest["parts"] if e.get("use") == name), None)
            if entry is not None:
                check = partlib.load(root, entry, tiers=manifest.get("tiers"))
                facts["findings"][name] = check.run(tree) if check.kind == "check" else []
    if "fast_forward" in needs:
        facts["fast_forward"] = leases.fast_forward(root, event["cwd"], event.get("session"))
    if "pins" in needs:
        facts["pins"] = []
        for path in sorted(tree.repositories):
            behind = gitcall.behind(top / path)
            facts["pins"].append({"path": path, "branch": behind[0] if behind else None,
                                  "behind": behind[1] if behind else None})
    return facts


def command_session(root, args):
    """session-start and session-end: run the session hooks, show their reminders, and never fail."""
    try:
        manifest = partlib.load_manifest(root, hook=True)
        hooks = partlib.load_hooks(root, args.event, manifest)
        stream = getattr(sys.stdin, "buffer", sys.stdin)
        found, tool, _ = events.read_call(root, args.event, stream.read(), args.tool)
        notes = []
        if args.event == "session-end" and any(e.get("use") == "lease" for e in manifest["parts"]):
            for event in found:
                leases.release(root, event.get("session"))     # only this session's own lease; never raises
        for event in found:
            event = {**event, **session_facts(root, hooks, event)}
            for part in hooks:
                reason = part.decide(event)
                if reason:
                    notes.append(reason)
        if notes:
            print(events.remind(tool, "\n\n".join(dict.fromkeys(notes)), args.event))
    except Exception:      # a session start or end is never refused, and never shows a traceback
        pass
    return 0


def lease_fact(root, event, tool):
    """Take or keep the writing-session lease for an edit to a tracked file in the main working copy.
    Any other edit needs none. See docs/decisions/0005-concurrent-sessions-and-the-edit-ledger.md."""
    if not event.get("main") or not event.get("working_copy"):
        return {"state": "not-needed"}
    found = leases.main_copy(root)
    if found is None:
        return {"state": "not-needed"}
    is_tracked = leases.tracked(found[0], event["path"])
    if is_tracked is False:
        return {"state": "not-needed"}
    pid = event.get("pid") if event.get("pid") else leases.tool_pid(tool)
    file = str(found[1] / leases.NAME)
    if is_tracked is None:
        return {"state": "error", "error": "git cannot say whether the file is tracked", "file": file}
    try:
        state, holder = leases.acquire(root, event.get("session"), pid)
    except (leases.LeaseError, OSError) as error:
        return {"state": "error", "error": str(error), "file": file}
    return {"state": state, "holder": holder, "file": file}


def command_hook(root, args):
    if args.event in partlib.SESSION_EVENTS:
        return command_session(root, args)
    if args.event not in partlib.EVENTS:
        raise partlib.PartError(f"unknown event {args.event!r}; the events are {partlib.EVENTS}")
    try:
        manifest = partlib.load_manifest(root, hook=True)   # only what a hook's answer depends on
    except partlib.PartError as error:
        raise partlib.PartError(f"{error}. Every hook call is refused until the manifest is repaired. "
                                "Repair it from your own terminal, where the agent's hooks do not run.")
    hooks = partlib.load_hooks(root, args.event, manifest)   # only this event's hooks: a broken check cannot lock it
    stream = getattr(sys.stdin, "buffer", sys.stdin)
    found, tool, cwd = events.read_call(root, args.event, stream.read(), args.tool)
    # The lease is taken only for an edit every other hook allows, so a refused edit takes no lease.
    leasing = [part for part in hooks if "lease" in getattr(part.module, "NEEDS", ())]
    ordered = [part for part in hooks if part not in leasing] + leasing
    reminders = []
    # One call can edit several files: all are decided before any is recorded. Every other hook decides every
    # file first; only then is the lease taken, so a call refused for any one file takes no lease.
    rounds = [(part, index) for part in ordered for index in range(len(found))]
    for part, index in rounds:
        if part in leasing and "lease" not in found[index]:
            found[index] = dict(found[index], lease=lease_fact(root, found[index], tool))
        reason = part.decide(found[index])
        if reason is None:
            continue
        if part.mode == "remind":
            reminders.append(f"{part.name}: {reason}")
            continue
        print(f"Refused by {part.name}: {reason}", file=sys.stderr)
        return 2
    reminders = list(dict.fromkeys(reminders))
    if args.event == "before-edit":
        for event in found:
            ledgers.record(root, event["absolute"])   # in the ledger of the working copy that holds it
    if reminders and args.event == "before-shell" and cwd:
        # The command may stage files this session did not write. The commit check compares only while a ledger is
        # open, so open it, even empty, when the working copy has uncommitted changes: an agent that wrote files only
        # through the shell must then name them. Only an agent tool says where its session runs; a person trying the
        # hook by hand opens nothing.
        if ledgers.open_at(root, cwd):
            reminders.append("The edit ledger of this working copy is open. The commit check refuses any staged "
                             "path that the agent's edit tools did not write; record a file written another way "
                             "with: python3 ws.py ledger --add PATH")
    if reminders:
        print(events.remind(tool, " ".join(reminders)))
    return 0


def command_ledger(root, args):
    folder = ledgers.git_dir(root)
    if folder is None:
        raise partlib.PartError(f"{root} is not the top of a git working copy, so it has no edit ledger")
    if args.add:
        for path in args.add:
            absolute = pathlib.Path(path).resolve()
            if ledgers.record(root, str(absolute)) is None:
                raise partlib.PartError(f"{path} is in no working copy of this repository")
    if args.committed:
        ledgers.remove(folder, ledgers.committed(root))
        return 0
    if args.close:
        ledgers.remove(folder, ledgers.read(folder) or ())   # empties it, and so deletes it
    paths = ledgers.read(folder)
    if paths is None:
        print("The edit ledger is closed: the commit check does not compare staged paths.")
    else:
        print(f"The edit ledger is open, with {len(paths)} path(s). The commit check refuses any other staged path.")
        for path in sorted(paths):
            print(f"  {path}")
    return 0


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):  # a finding may quote text the console cannot encode
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(prog="ws.py", description="Run a workspace's parts.")
    parser.add_argument("--version", action="version", version=VERSION, help="print the engine version")
    parser.add_argument("--root", default=str(ROOT), help="the workspace folder (default: where ws.py lives)")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list")
    commands.add_parser("selftest")
    check = commands.add_parser("check")
    check.add_argument("--staged", action="store_true")
    check.add_argument("--changed", nargs="*", default=[])
    check.add_argument("--changed-from", metavar="REF")
    check.add_argument("--message", metavar="FILE", help="check a commit message file, and the commit's identities")
    check.add_argument("--push", metavar="REMOTE", help="the pre-push hook: check the refs git lists on standard input")
    check.add_argument("--phase", choices=partlib.PHASES, default="commit",
                       help="run only the checks for this phase (default: commit)")
    hook = commands.add_parser("hook")
    hook.add_argument("event")
    hook.add_argument("--tool", help="read this agent tool's own payload through its adapter, such as claude-code")
    ledger = commands.add_parser("ledger")
    ledger.add_argument("--add", nargs="+", metavar="PATH", help="record files this session wrote another way")
    ledger.add_argument("--close", action="store_true", help="close the ledger, for a person's own commit")
    ledger.add_argument("--committed", action="store_true", help="drop the last commit's paths (post-commit hook)")
    args = parser.parse_args(argv)

    root = pathlib.Path(args.root).resolve()
    if args.command == "hook" and args.event in partlib.SESSION_EVENTS:
        return command_session(root, args)      # never fails, so not under the error handling below
    try:
        return {"list": command_list, "selftest": command_selftest, "check": command_check,
                "hook": command_hook, "ledger": command_ledger}[args.command](root, args)
    except (partlib.PartError, NotADirectoryError, RuntimeError) as error:
        print(f"ws: {error}", file=sys.stderr)
        return 2
    except Exception as error:  # never a traceback, and never exit 1 from a hook: 1 would not block
        print(f"ws: unexpected {type(error).__name__}: {error}", file=sys.stderr)
        return 2

