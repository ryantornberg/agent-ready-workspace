"""Check: a draft hand-off plan keeps its Key points block and its table cells within their word budgets.

A plan is read in full only when its budgets hold: a Key points block a person can read in a minute, and table
cells short enough that a table stays a table. Slice detail that does not fit a cell goes under a heading per
slice, below the table. docs/templates/hand-off-plan.md states the budgets.

The check reads each page in "folder" (default docs/plans, subfolders included) whose front matter has
`kind: plan` and `status: draft`. An approved, done or abandoned plan is skipped: its sections are frozen, as rule 6
of the template says. A word is a run of characters between spaces. It fails:

- a `## Key points` section, up to the next heading of level one or two, holding more than "key_points" words
  (default 200);
- a table cell holding more than "cell" words (default 60), anywhere in the plan outside a fenced block.

Config: "folder" (default docs/plans), "key_points" (default 200), "cell" (default 60).
"""
import re

from wslib import markdown
from wslib.parts import finding

KIND = "check"
PAGE = "docs/templates/hand-off-plan.md"   # the rule's page, which every finding names (criterion 34)
FOLDER = "docs/plans"
KEY_POINTS = re.compile(r"^##\s+Key points\s*$")
HEADING = re.compile(r"^#{1,2}\s")
FIELD = re.compile(r"^([A-Za-z][\w-]*)\s*:\s*(.*?)\s*$")


def front(text):
    rows, _ = markdown.split_front_matter(text or "")
    values = {}
    for row in rows:
        match = FIELD.match(row)
        if match:
            values[match.group(1)] = match.group(2)
    return values


def key_points_words(lines):
    """(line number of the heading, word count), or None when the plan has no Key points section."""
    start = next((n for n, line in enumerate(lines) if KEY_POINTS.match(line.strip())), None)
    if start is None:
        return None
    words = 0
    for line in lines[start + 1:]:
        if HEADING.match(line.strip()):
            break
        words += len(line.split())
    return start + 1, words


def long_cells(lines, limit):
    """[(line number, cell number, word count)] of table cells over the limit, outside fenced blocks."""
    found, fenced = [], False
    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            fenced = not fenced
            continue
        if fenced or not stripped.startswith("|"):
            continue
        cells = re.split(r"(?<!\\)\|", stripped.strip("|"))
        for index, cell in enumerate(cells, 1):
            count = len(cell.split())
            if count > limit:
                found.append((number, index, count))
    return found


def run(snapshot, config):
    folder = config.get("folder", FOLDER).rstrip("/")
    key_limit, cell_limit = config.get("key_points", 200), config.get("cell", 60)
    found = []
    for path in snapshot.paths((".md",), under=folder):
        text = snapshot.read(path)
        values = front(text)
        if values.get("kind") != "plan" or values.get("status") != "draft":
            continue
        lines = (text or "").replace("\r\n", "\n").split("\n")
        key = key_points_words(lines)
        if key and key[1] > key_limit:
            found.append(finding(path, key[0], f"the Key points block holds {key[1]} words, over the budget of "
                                               f"{key_limit}; keep what a person must know before approving, and "
                                               f"move the rest to the sections it belongs to; see {PAGE}"))
        for number, index, count in long_cells(lines, cell_limit):
            found.append(finding(path, number, f"table cell {index} holds {count} words, over the budget of "
                                               f"{cell_limit}; shorten it, and put slice detail under a heading per "
                                               f"slice below the table; see {PAGE}"))
    return found
