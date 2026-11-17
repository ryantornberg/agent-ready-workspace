"""Check: a line a commit adds to a doc page does not cite a file by line number.

A line number in a durable page goes stale with the next edit to the file it
points at. A method, a class or a heading survives. Only the lines the commit adds
are read, so a citation already on the page is not touched. Lines inside a fenced
code block are skipped. Pages in "skip" folders, such as recorded runs, are not read.

At the commit, the added lines come from the staged file against the last commit's;
in CI, against the base branch (`check --changed-from`). A working-folder check with
no base has no added lines, and reads nothing.

Config: "folders" (default "docs" and the top folder), "skip" (default "evals/runs").
"""
import re

from wslib import markdown
from wslib.parts import finding

KIND = "check"
EXTENSIONS = "py|md|cs|ts|tsx|js|jsx|json|yml|yaml|toml|sh|ps1|txt|go|java|rb|rs|sql|css|html|xml"
CITE = re.compile(rf"(?<![\w/.-])([\w./-]+\.(?:{EXTENSIONS})):(\d+)(?!\w)")
PINNED = re.compile(r"(?<![0-9A-Za-z])(?=[0-9a-f]*\d)[0-9a-f]{7,40}(?![0-9A-Za-z])")


def _in_scope(path, folders, skip):
    if not path.lower().endswith(".md") or any(path == s or path.startswith(s.rstrip("/") + "/") for s in skip):
        return False
    folder = path.rsplit("/", 1)[0] if "/" in path else "."
    return any(f == "." and folder == "." or folder == f.rstrip("/") or folder.startswith(f.rstrip("/") + "/")
               for f in folders)


def run(snapshot, config):
    folders, skip = config.get("folders", ["docs", "."]), config.get("skip", ["evals/runs"])
    found = []
    for path in sorted(snapshot.changed):
        if not _in_scope(path, folders, skip) or not snapshot.is_file(path):
            continue
        added = snapshot.added_lines(path)
        if not added:
            continue
        prose = {number for number, _ in markdown.prose_lines(snapshot.read(path) or "")}   # not in a fenced block
        for number, line in added:
            if number not in prose or PINNED.search(line):
                continue
            for match in CITE.finditer(line):
                found.append(finding(path, number, f"cites {match.group(0)} by line number, which goes stale with the "
                                                   f"next edit to that file; name the method, class or heading instead"))
    return found
