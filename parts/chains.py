"""Check: every path the index's cross-cutting chains name exists.

A chain lists, for one kind of change, every path that change touches: a new part touches its file, its
cases, the manifest and the parts page. An agent that edits one of them is shown the rest (slice C5's
reminder), so a chain that names a moved or deleted path sends it to nothing. The chains are a table under
the index's heading "Cross-cutting chains": the first column names the change, the second its paths, each
in backticks. A path that ends in "/" is a folder that must hold a file. It fails when the index has no such
table, so deleting the heading is not a way out.

Config: "index" (default INDEX.md), "heading" (default "Cross-cutting chains").
"""
import re

from wslib import markdown
from wslib.parts import finding

KIND = "check"
PAGE = "docs/layout.md"


def chains(text, heading):
    """[(line number, change, [paths])] of the chain table under the heading."""
    found, inside = [], False
    for number, line in enumerate(text.replace("\r\n", "\n").split("\n"), 1):
        if line.startswith("#"):
            inside = line.lstrip("#").strip() == heading
            continue
        if not inside or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2 or set(cells[0]) <= set("-: ") or cells[0].lower() == "change":
            continue
        found.append((number, cells[0], re.findall(r"`([^`]+)`", cells[1])))
    return found


def run(snapshot, config):
    index = config.get("index", "INDEX.md")
    heading = config.get("heading", "Cross-cutting chains")
    if not snapshot.is_file(index):
        return [finding(index, 1, f"no index, so no chain could be checked; see {PAGE}")]
    text = snapshot.read(index)
    if text is None:
        return [finding(index, 1, f"{snapshot.not_utf8(index)}, so its chains were not read")]
    rows = chains(text, heading)
    if not rows:
        return [finding(index, 1, f"has no chain table under '## {heading}'; each row names a kind of change and, "
                                  f"in backticks, every path it touches; see {PAGE}")]
    found = []
    for line, change, paths in rows:
        if not paths:
            found.append(finding(index, line, f"the chain for {change!r} names no path in backticks"))
        for path in paths:
            if not snapshot.exists(path.rstrip("/")) or (path.endswith("/") and snapshot.is_file(path.rstrip("/"))):
                found.append(finding(index, line, f"the chain for {change!r} names {path}, which does not exist; "
                                                  f"correct the path or the row"))
    return found
