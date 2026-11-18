"""The proof keys a page carries, and the one function that takes them out before an agent reads the page.

A playbook or how-to says whether it is proven in its front matter, and a section merged into another page
says so in a line right under its heading (decision record 0006):

    proof: proven                                   front matter, one of proven or unproven
    prove-by: M6                                    front matter, on an unproven page
    proven-by: docs/milestones/m1.md, <sha>:evals/runs/fix-a-bug/record.json
                                                    front matter, on a proven page: bare paths, or
                                                    commit-pinned paths <40-hex sha>:<path>, no link text
    Proof: unproven, prove-by M6.                   the first line under a section's heading
    Proof: proven, proven-by <the same list>.

These keys are bookkeeping, not guidance. So the eval runner takes them out of every page a gated arm reads,
in exactly these forms and no others, and the eval hash ignores the same text through this same function:
marking a page proven does not stale the record that proved it. Any other spelling of these keys is left in,
so it is hashed and an agent reads it, and the page_kinds check fails it (problems() below), so a variant
cannot hide text from the hash.

The harness (run.py) imports this file. The eval_record and page_kinds checks load it from the snapshot's
text, as grade.py loads a hook's file, so the text that is hashed is exactly the text that is tested.
Standard library only, and nothing from the engine.
"""
import re

PATH = r"[A-Za-z0-9_][A-Za-z0-9_./-]*"
ITEM = rf"(?:[0-9a-f]{{40}}:)?{PATH}"
LIST = rf"{ITEM}(?:, {ITEM})*"
MILESTONE = r"M[1-9][0-9]*"

FRONT_KEYS = {
    "proof": re.compile(r"^proof: (?:proven|unproven)$"),
    "prove-by": re.compile(rf"^prove-by: {MILESTONE}$"),
    "proven-by": re.compile(rf"^proven-by: {LIST}$"),
}
SECTION_LINE = re.compile(rf"^Proof: (?:unproven, prove-by {MILESTONE}|proven, proven-by {LIST})\.$")
HEADING = re.compile(r"^#{2,6} \S")
# Anything that looks like one of these keys, in any spelling: a variant the checks must refuse.
FRONT_LIKE = re.compile(r"""^\s*["']?(?:proof|prove[-_ ]?by|proven[-_ ]?by)["']?\s*:""", re.I)
SECTION_LIKE = re.compile(r"^\W{0,4}proof\W{0,4}\s*:", re.I)


def _front_end(lines):
    """The index of the closing '---' of the front matter, or None when the page has none."""
    if not lines or lines[0] != "---":
        return None
    for index in range(1, len(lines)):
        if lines[index] in ("---", "..."):
            return index
    return None


def _section_lines(lines, start):
    """Indexes of the exact section proof lines: each the first non-blank line after a heading."""
    found, heading = [], False
    for index in range(start, len(lines)):
        line = lines[index]
        if HEADING.match(line):
            heading = True
            continue
        if not line.strip():
            continue
        if heading and SECTION_LINE.match(line):
            found.append(index)
        heading = False
    return found


def strip(text):
    """The page as a gated arm reads it: the exact proof keys and section proof lines taken out, nothing else.

    Line endings are normalized to "\\n" first, as the hash does. A section line takes the blank line after it
    with it, so the section reads as if it never had one."""
    lines = text.replace("\r\n", "\n").split("\n")
    end = _front_end(lines)
    drop = set()
    if end is not None:
        for index in range(1, end):
            if any(pattern.match(lines[index]) for pattern in FRONT_KEYS.values()):
                drop.add(index)
    for index in _section_lines(lines, 0 if end is None else end + 1):
        drop.add(index)
        if index + 1 < len(lines) and not lines[index + 1].strip() and index > 0 and not lines[index - 1].strip():
            drop.add(index + 1)
    return "\n".join(line for index, line in enumerate(lines) if index not in drop)


def keys(text):
    """{key: value} of the exact front-matter proof keys, and [(heading, line text)] of the exact section lines."""
    lines = text.replace("\r\n", "\n").split("\n")
    end = _front_end(lines)
    found = {}
    if end is not None:
        for index in range(1, end):
            for key, pattern in FRONT_KEYS.items():
                if pattern.match(lines[index]):
                    found[key] = lines[index].split(": ", 1)[1]
    sections = []
    for index in _section_lines(lines, 0 if end is None else end + 1):
        heading = next(lines[i] for i in range(index - 1, -1, -1) if HEADING.match(lines[i]))
        sections.append((heading.lstrip("#").strip(), lines[index]))
    return found, sections


def parse_list(value):
    """The items of a proven-by list: [(sha or None, path)]."""
    items = []
    for item in value.split(", "):
        sha, _, path = item.rpartition(":") if re.match(r"^[0-9a-f]{40}:", item) else ("", "", item)
        items.append((sha or None, path))
    return items


def parse_section(line):
    """(state, value) of a section proof line: ("unproven", "M6") or ("proven", "<list>")."""
    body = line[len("Proof: "):-1]
    state, _, rest = body.partition(", ")
    return state, rest.split(" ", 1)[1]


def problems(text):
    """[(line number, what is wrong)] for every proof key or line that is not in an exact form.

    A variant would be hashed and read by an agent while it looks like bookkeeping, so it is refused instead."""
    lines = text.replace("\r\n", "\n").split("\n")
    end = _front_end(lines)
    found, seen = [], {}
    if end is not None:
        for index in range(1, end):
            line = lines[index]
            if not FRONT_LIKE.match(line):
                continue
            key = next((k for k, pattern in FRONT_KEYS.items() if pattern.match(line)), None)
            if key is None:
                found.append((index + 1, f"proof key not in its exact form: {line.strip()!r}; write one of "
                                         "'proof: proven', 'proof: unproven', 'prove-by: M<n>', "
                                         "'proven-by: <path>, <40-hex sha>:<path>' (bare paths, no link text)"))
            elif key in seen:
                found.append((index + 1, f"{key} is given twice"))
            seen[key] = True
    exact = set(_section_lines(lines, 0 if end is None else end + 1))
    for index in range(0 if end is None else end + 1, len(lines)):
        line = lines[index]
        if index in exact or not SECTION_LIKE.match(line):
            continue
        if SECTION_LINE.match(line):
            found.append((index + 1, "a section proof line must be the first line under its section's heading"))
        else:
            found.append((index + 1, f"section proof line not in its exact form: {line.strip()!r}; write "
                                     "'Proof: unproven, prove-by M<n>.' or 'Proof: proven, proven-by <list>.'"))
    return found
