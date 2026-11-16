"""The runner: the commands ws.py offers. ws.py, at the top of the workspace, only calls main() here.

Every command but selftest runs each part's cases as it loads the part, and refuses a part with a failing case.
A hook call loads only the hooks for its event, so a broken check cannot refuse a shell command or an edit.
The commit check reads the staged manifest, parts and cases. A part an older manifest used must still be
used, or be listed under "retired" with a reason: the last commit's manifest decides locally, and the base
commit's manifest in CI.

The events are before-shell, before-edit and before-handoff. A hook reads the workspace's versioned event
shape, or one agent tool's payload through that tool's adapter (wslib/events.py), and refuses anything else.
A hook with MODE = "remind" never refuses: the agent is shown its reason and the call goes ahead.

An allowed edit is recorded in the edit ledger of the working copy that holds it (wslib/ledger.py). A
before-shell reminder opens the ledger of the folder the agent tool says its session runs in, when that
working copy has uncommitted changes. While a ledger is open, the commit check fails a staged path no edit
tool wrote (parts/edit_ledger.py).

Exit codes: 0 clean; 1 a check found an error or a case failed; 2 a hook refused, or the setup is
wrong. A hook that cannot decide exits 2 as well: it fails closed.
"""
import argparse
import pathlib
import sys

from . import VERSION
from . import events
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


def command_check(root, args):
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


def command_hook(root, args):
    if args.event not in partlib.EVENTS:
        raise partlib.PartError(f"unknown event {args.event!r}; the events are {partlib.EVENTS}")
    try:
        manifest = partlib.load_manifest(root, hook=True)   # only what a hook's answer depends on
    except partlib.PartError as error:
        raise partlib.PartError(f"{error}. Every hook call is refused until the manifest is repaired. "
                                "Repair it from your own terminal, where the agent's hooks do not run.")
    hooks = partlib.load_hooks(root, args.event, manifest)   # only this event's hooks: a broken check cannot lock it
    stream = getattr(sys.stdin, "buffer", sys.stdin)
    event, tool, cwd = events.read_call(root, args.event, stream.read(), args.tool)
    reminders = []
    for part in hooks:
        reason = part.decide(event)
        if reason is None:
            continue
        if part.mode == "remind":
            reminders.append(f"{part.name}: {reason}")
            continue
        print(f"Refused by {part.name}: {reason}", file=sys.stderr)
        return 2
    if args.event == "before-edit":
        ledgers.record(root, event["path"])   # cannot record: refused, so no edit escapes the commit check
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
    try:
        return {"list": command_list, "selftest": command_selftest, "check": command_check,
                "hook": command_hook, "ledger": command_ledger}[args.command](root, args)
    except (partlib.PartError, NotADirectoryError, RuntimeError) as error:
        print(f"ws: {error}", file=sys.stderr)
        return 2
    except Exception as error:  # never a traceback, and never exit 1 from a hook: 1 would not block
        print(f"ws: unexpected {type(error).__name__}: {error}", file=sys.stderr)
        return 2

