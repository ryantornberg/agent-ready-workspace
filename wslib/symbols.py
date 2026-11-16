"""Find definitions by name: Python through its parser, C# and TypeScript by line patterns.

The patterns read one line at a time after comments are blanked out. They find
declarations written on one line in the usual style. The README lists what
they miss. That is the trade: no index to build, and nothing to go stale.
"""
import argparse
import ast
import pathlib
import re
import sys

from . import snapshot as snapshots

SKIP_DIRS = ("node_modules/", "bin/", "obj/", "dist/", "build/")

_CS_MOD = r"(?:public|internal|private|protected|static|sealed|abstract|partial|readonly|virtual|override|async|" \
          r"unsafe|extern|new|file|ref|required)"
_CS_TYPE = r"(?:\([^)]*\)|[A-Za-z_][\w.]*(?:<[^()]*>)?)(?:\[\]|\?)*"
_CS_NOT_A_NAME = {"if", "for", "foreach", "while", "switch", "catch", "using", "lock", "return", "new", "await",
                  "throw", "else", "when", "nameof", "typeof", "sizeof", "default", "base", "this", "get", "set"}
_CS_MODIFIERS = set(_CS_MOD[3:-1].split("|"))
_CS_NOT_A_TYPE = _CS_MODIFIERS | {"return", "await", "throw", "new", "else", "yield", "using", "case", "in", "is", "as", "out", "var"}

CS_TYPE = re.compile(rf"^\s*(?:{_CS_MOD}\s+)*(record\s+struct|record\s+class|class|interface|record|struct|enum)\s+([A-Za-z_]\w*)")
CS_METHOD = re.compile(rf"^\s*((?:{_CS_MOD}\s+)*)({_CS_TYPE})\s+([A-Za-z_]\w*)\s*(?:<[^()]*>)?\s*\(")
# A constructor takes only these modifiers. Not "new", so "new Order(1)," in an initializer is not one.
CS_CTOR = re.compile(r"^\s*(?:(?:public|internal|private|protected|static|extern|unsafe)\s+)+([A-Za-z_]\w*)\s*\(")
CS_PROPERTY = re.compile(rf"^\s*(?:{_CS_MOD}\s+)+{_CS_TYPE}\s+([A-Za-z_]\w*)\s*(?:\{{|=>)")

_TS_NAME = r"([A-Za-z_$][\w$]*)"
_TS_HEAD = r"^\s*(?:export\s+)?(?:default\s+)?(?:declare\s+)?"
_TS_NOT_A_NAME = {"if", "for", "while", "switch", "catch", "return", "function", "constructor", "super", "else",
                  "do", "try", "typeof", "await", "new", "throw"}
TS = [
    ("function", re.compile(_TS_HEAD + r"(?:async\s+)?function\s*\*?\s*" + _TS_NAME)),
    ("class", re.compile(_TS_HEAD + r"(?:abstract\s+)?class\s+(?!extends\b|implements\b)" + _TS_NAME)),
    ("type", re.compile(_TS_HEAD + r"(?:interface|type|(?:const\s+)?enum|namespace|module)\s+" + _TS_NAME)),
    ("const", re.compile(_TS_HEAD + r"(?:const|let|var)\s+" + _TS_NAME + r"\s*(?::[^=]+)?=(?!=)")),
]
TS_METHOD = re.compile(r"^\s+(?:(?:public|private|protected|static|async|readonly|override|abstract|get|set)\s+)*"
                       + _TS_NAME + r"\s*(?:<[^()]*>)?\s*\([^()]*\)\s*(?::[^={;]+)?\s*\{\s*$")
PY = re.compile(r"^\s*(?:async\s+)?(def|class)\s+([A-Za-z_]\w*)")

SCRIPT_SUFFIXES = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".vue")
SUFFIXES = (".py", ".cs") + SCRIPT_SUFFIXES


def blank_comments(text):
    """Replace // and /* */ comments with spaces, keeping line numbers. Strings are left alone."""
    def blank(match):
        return re.sub(r"[^\n]", " ", match.group(0))
    text = re.sub(r"/\*.*?\*/", blank, text, flags=re.S)
    return re.sub(r"(?<![:\"'])//[^\n]*", blank, text)


def python_symbols(text):
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        # Newer syntax than this interpreter knows: fall back to reading def and class lines.
        for number, line in enumerate(text.splitlines(), 1):
            match = PY.match(line)
            if match:
                yield number, "class" if match.group(1) == "class" else "function", match.group(2)
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            yield node.lineno, "class", node.name
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield node.lineno, "function", node.name


def csharp_symbols(text):
    for number, line in enumerate(blank_comments(text).splitlines(), 1):
        match = CS_TYPE.match(line)
        if match:
            yield number, "type", match.group(2)
            continue
        if re.search(r"\boperator\b", line):
            continue
        match = CS_METHOD.match(line)
        if match and match.group(3) not in _CS_NOT_A_NAME and match.group(2).split("<")[0] not in _CS_NOT_A_TYPE \
                and (match.group(1) or not line.rstrip().endswith(";") or "interface" in text):
            yield number, "method", match.group(3)
            continue
        match = CS_CTOR.match(line)
        if match and match.group(1) not in _CS_NOT_A_NAME:
            yield number, "constructor", match.group(1)
            continue
        match = CS_PROPERTY.match(line)
        if match and match.group(1) not in _CS_NOT_A_NAME:
            yield number, "property", match.group(1)


def script_symbols(text):
    for number, line in enumerate(blank_comments(text).splitlines(), 1):
        for kind, pattern in TS:
            match = pattern.match(line)
            if match:
                yield number, kind, match.group(1)
                break
        else:
            match = TS_METHOD.match(line)
            if match and match.group(1) not in _TS_NOT_A_NAME and "=>" not in line:
                yield number, "method", match.group(1)


def symbols_in(path, text):
    suffix = "." + path.rsplit(".", 1)[-1].lower() if "." in path else ""
    if suffix == ".py":
        return python_symbols(text)
    if suffix == ".cs":
        return csharp_symbols(text)
    if suffix in SCRIPT_SUFFIXES:
        return script_symbols(text)
    return ()


def scan(snapshot, under=""):
    """Yield (path, line, kind, name) for every definition in the snapshot, under a folder."""
    for path in snapshot.paths(suffixes=SUFFIXES, under=under):
        relative = path[len(under.strip("/")) + 1:] if under.strip("/") else path
        if any(("/" + relative).find("/" + skip) >= 0 for skip in SKIP_DIRS):
            continue
        text = snapshot.read_text(path)   # code in Windows-1252 or UTF-16 is read too
        if text is None:
            continue
        for line, kind, name in symbols_in(path, text):
            yield path, line, kind, name


def find(snapshot, name, under="", contains=False):
    wanted = name.lower()
    return sorted(s for s in scan(snapshot, under) if (wanted in s[3].lower() if contains else s[3] == name))


def main(argv=None):
    """The command line, tools/symbols.py: print "path:line  kind  name". Exit 0 when found, 1 when not, 2 when
    the folder does not exist."""
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
    hits = find(tree, args.name, contains=args.contains)
    for path, line, kind, name in hits:
        print(f"{path if prefix in ('', '.') else prefix + '/' + path}:{line}  {kind}  {name}")
    if not hits:
        print(f"no definition of {args.name!r} under {args.root}", file=sys.stderr)
    return 0 if hits else 1

