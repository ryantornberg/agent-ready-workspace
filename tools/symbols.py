#!/usr/bin/env python3
"""Find where a name is defined, as file:line, in one call.

    python3 tools/symbols.py ReconciliationWorker src     # exact name
    python3 tools/symbols.py --contains export src        # any name containing "export"

An agent that knows a name should not have to search for it. Python is read
with its own parser; C#, TypeScript and JavaScript by line patterns, which the
README's Limits section describes.

Prints "path:line  kind  name". Exit 0 when found, 1 when not, 2 when the folder does not exist.
"""
import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from wslib import snapshot as snapshots  # noqa: E402
from wslib import symbols  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(description="Find where a name is defined.")
    parser.add_argument("name")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--contains", action="store_true", help="match any name containing NAME, ignoring case")
    args = parser.parse_args(argv)

    try:
        tree = snapshots.Tree(args.root)
    except NotADirectoryError:
        print(f"no such folder: {args.root}", file=sys.stderr)
        return 2
    prefix = pathlib.PurePath(args.root).as_posix().rstrip("/")
    hits = symbols.find(tree, args.name, contains=args.contains)
    for path, line, kind, name in hits:
        print(f"{path if prefix in ('', '.') else prefix + '/' + path}:{line}  {kind}  {name}")
    if not hits:
        print(f"no definition of {args.name!r} under {args.root}", file=sys.stderr)
    return 0 if hits else 1


if __name__ == "__main__":
    sys.exit(main())
