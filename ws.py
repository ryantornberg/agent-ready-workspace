#!/usr/bin/env python3
"""Run a workspace's parts. The manifest, workspace.json, says which parts this workspace uses.

    python3 ws.py list                       # the parts, their kind and how many cases each has
    python3 ws.py selftest                   # run every part's own cases
    python3 ws.py check                      # run the checks on the working folder
    python3 ws.py check --staged             # run them on exactly what is staged (the commit hook)
    python3 ws.py check --changed-from REF   # treat files edited since REF as changed (CI)
    python3 ws.py hook before-shell          # decide one event, read as JSON on standard input

Exit codes: 0 clean, 1 a check found an error or a case failed, 2 a hook refused or the setup is wrong.
"""
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from wslib import parts as partlib  # noqa: E402
from wslib import snapshot as snapshots  # noqa: E402


def command_list(root, _args):
    for part in partlib.load_all(root):
        kind = part.kind if part.kind == "check" else f"hook on {part.event}"
        print(f"{part.name:<16} {kind:<22} {len(part.cases)} cases")
    return 0


def command_selftest(root, _args):
    failed = 0
    for part in partlib.load_all(root):
        failures = part.failed_cases()
        failed += len(failures)
        print(f"{'FAIL' if failures else 'ok  '}  {part.name}: {len(part.cases) - len(failures)} of {len(part.cases)} cases")
        for line in failures:
            print(f"      {line}")
    return 1 if failed else 0


def command_check(root, args):
    loaded = [part for part in partlib.load_all(root) if part.kind == "check"]
    if args.staged:
        snapshot = snapshots.Index(root)
    else:
        changed = list(args.changed)
        if args.changed_from is not None:
            since, problem = snapshots.changed_since(root, args.changed_from)
            if problem:
                print(f"warning: {problem}; no file is treated as changed")
            changed.extend(since)
        snapshot = snapshots.Tree(root, changed)

    errors = 0
    for part in loaded:
        for found in part.run(snapshot):
            errors += found["level"] == "error"
            print(f"{found['level']}: {found['path']}:{found['line']}: {found['message']}  [{part.name}]")
    if errors:
        print(f"\n{errors} error(s).")
    return 1 if errors else 0


def read_event(root, stream):
    """Read a hook event. Accepts {"command": ...} or {"path": ...}, or a Claude Code hook payload."""
    try:
        event = json.load(stream)
    except json.JSONDecodeError as error:
        raise partlib.PartError(f"hook input is not JSON: {error}")
    if isinstance(event, dict) and isinstance(event.get("tool_input"), dict):
        tool_input = event["tool_input"]
        event = {"command": tool_input.get("command"), "path": tool_input.get("file_path")}
    if not isinstance(event, dict):
        raise partlib.PartError("hook input must be a JSON object")
    path = event.get("path")
    if path and pathlib.Path(path).is_absolute():
        try:
            event["path"] = pathlib.Path(path).resolve().relative_to(root).as_posix()
        except ValueError:
            pass  # outside the workspace: leave it absolute, so no rule about workspace paths matches
    return event


def command_hook(root, args):
    event = read_event(root, sys.stdin)
    for part in partlib.load_all(root):
        if part.kind == "hook" and part.event == args.event:
            reason = part.decide(event)
            if reason is not None:
                print(f"Refused by {part.name}: {reason}", file=sys.stderr)
                return 2
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run a workspace's parts.")
    parser.add_argument("--root", default=str(ROOT), help="the workspace folder (default: where ws.py lives)")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list")
    commands.add_parser("selftest")
    check = commands.add_parser("check")
    check.add_argument("--staged", action="store_true")
    check.add_argument("--changed", nargs="*", default=[])
    check.add_argument("--changed-from", metavar="REF")
    hook = commands.add_parser("hook")
    hook.add_argument("event")
    args = parser.parse_args(argv)

    root = pathlib.Path(args.root).resolve()
    try:
        return {"list": command_list, "selftest": command_selftest,
                "check": command_check, "hook": command_hook}[args.command](root, args)
    except (partlib.PartError, NotADirectoryError, RuntimeError) as error:
        print(f"ws: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
