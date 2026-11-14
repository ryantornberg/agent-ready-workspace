#!/usr/bin/env python3
"""Find where a name is defined, as file:line, in one call.

    python3 tools/symbols.py OrderExporter            # exact name
    python3 tools/symbols.py --contains export src/   # any name containing "export"

An agent that knows a name should not have to search for it. This reads Python
with the standard parser, and C#, TypeScript and JavaScript with a few line
patterns. The patterns find declarations, not every use, and they can miss
unusual formatting. That is the trade: no index to build and nothing to go stale.

Prints "path:line  kind  name", one per definition. Exit 1 if nothing matched.
"""
import argparse
import ast
import pathlib
import re
import sys

SKIP_DIRS = {".git", "node_modules", "bin", "obj", "dist", "build", ".venv", "__pycache__"}

CSHARP = [
    ("type", re.compile(r"^\s*(?:(?:public|internal|private|protected|static|sealed|abstract|partial|readonly)\s+)*"
                        r"(?:class|interface|record|struct|enum)\s+([A-Za-z_]\w*)")),
    ("method", re.compile(r"^\s*(?:(?:public|internal|private|protected|static|virtual|override|async|sealed|abstract)\s+)+"
                          r"[\w<>\[\],.? ]+?\s+([A-Za-z_]\w*)\s*\(")),
]
SCRIPT = [
    ("function", re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s*([A-Za-z_$][\w$]*)")),
    ("class", re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+([A-Za-z_$][\w$]*)")),
    ("type", re.compile(r"^\s*(?:export\s+)?(?:interface|type|enum)\s+([A-Za-z_$][\w$]*)")),
    ("const", re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=")),
]
PATTERNS = {".cs": CSHARP, ".ts": SCRIPT, ".tsx": SCRIPT, ".js": SCRIPT, ".jsx": SCRIPT, ".mjs": SCRIPT, ".vue": SCRIPT}


def python_symbols(text):
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            yield node.lineno, "class", node.name
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield node.lineno, "function", node.name


def pattern_symbols(text, patterns):
    for number, line in enumerate(text.splitlines(), 1):
        for kind, pattern in patterns:
            match = pattern.match(line)
            if match:
                yield number, kind, match.group(1)
                break


def symbols(root):
    """Yield (path, line, kind, name) for every definition under root."""
    root = pathlib.Path(root)
    files = [root] if root.is_file() else sorted(p for p in root.rglob("*") if p.is_file())
    for path in files:
        if SKIP_DIRS.intersection(path.parts):
            continue
        suffix = path.suffix.lower()
        if suffix != ".py" and suffix not in PATTERNS:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        found = python_symbols(text) if suffix == ".py" else pattern_symbols(text, PATTERNS[suffix])
        for line, kind, name in found:
            yield path.as_posix(), line, kind, name


def find(name, root=".", contains=False):
    """Definitions of name under root, sorted by path and line."""
    wanted = name.lower()
    return sorted(s for s in symbols(root) if (wanted in s[3].lower() if contains else s[3] == name))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Find where a name is defined.")
    parser.add_argument("name")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--contains", action="store_true", help="match any name containing NAME, ignoring case")
    args = parser.parse_args(argv)

    hits = find(args.name, args.root, args.contains)
    for path, line, kind, name in hits:
        print(f"{path}:{line}  {kind}  {name}")
    if not hits:
        print(f"no definition of {args.name!r} under {args.root}", file=sys.stderr)
    return 0 if hits else 1


if __name__ == "__main__":
    sys.exit(main())
