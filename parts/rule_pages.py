"""Hook, before an edit: show the agent every rule page that applies to the file.

Some agent tools load path-scoped rule files on their own and others do not, so a
session in one that does not would never see the rules for the file it edits. A rule
page lives in the rules folder and says which files it applies to in its front matter:

    applies-to: "src/orders-api/**, tools/*.py"      one line, patterns split on commas
    applies-to:                                      or a list
      - "**/*.{cs,ts}"

A pattern is read from the top of the working copy that holds the file, so it works
the same in a linked worktree. "*" matches within one folder, "**" across folders,
"**/" at the start also matches a file at the top, and one {a,b} group lists choices;
a comma inside the braces does not split. It never refuses: it reminds, with the
pages' text. It says nothing when no page applies. The runner reads the pages fresh
on every edit, from that working copy (decision 0004).

Config: "folder" (default "docs/rules").
"""
import re

KIND = "hook"
EVENT = "before-edit"
MODE = "remind"
NEEDS = ("rule_pages",)


def _patterns(text):
    lines = text.replace("\r\n", "\n").split("\n")
    if not lines or lines[0].strip() != "---":
        return []
    found, listing = [], False
    for line in lines[1:]:
        if line.strip() in ("---", "..."):
            break
        key = re.match(r"^applies-to\s*:\s*(.*)$", line)
        if key:
            value = key.group(1).strip()
            listing = not value
            if value:
                found += _split(value.strip("\"'"))
            continue
        item = re.match(r"^\s+-\s+(.*)$", line)
        if listing and item:
            found.append(item.group(1).strip().strip("\"'"))
        elif line.strip():
            listing = False
    return [p for p in found if p]


def _split(value):
    """Split on commas outside a brace group."""
    parts, depth, current = [], 0, ""
    for char in value:
        if char == "," and depth == 0:
            parts.append(current.strip())
            current = ""
            continue
        depth += {"{": 1, "}": -1}.get(char, 0)
        current += char
    return parts + [current.strip()]


def _regex(pattern):
    group = re.search(r"\{([^{}]*)\}", pattern)
    if group:
        return "(?:" + "|".join(_regex(pattern[:group.start()] + choice + pattern[group.end():])
                                for choice in group.group(1).split(",")) + ")"
    out, index = "", 0
    while index < len(pattern):
        if pattern.startswith("**/", index):
            out, index = out + "(?:.*/)?", index + 3
        elif pattern.startswith("**", index):
            out, index = out + ".*", index + 2
        elif pattern[index] == "*":
            out, index = out + "[^/]*", index + 1
        elif pattern[index] == "?":
            out, index = out + "[^/]", index + 1
        else:
            out, index = out + re.escape(pattern[index]), index + 1
    return out


def matches(pattern, path):
    pattern = pattern.strip()
    if pattern.startswith("./"):   # only a leading "./": a dot folder such as .github keeps its dot
        pattern = pattern[2:]
    return re.fullmatch(_regex(pattern), path) is not None


def decide(event, config):
    path = event.get("path") or ""
    if not path or path.startswith("/") or re.match(r"^[A-Za-z]:", path):
        return None                 # outside every working copy of this repository
    texts = [(page, text) for page, text in sorted((event.get("rule_pages") or {}).items())
             if any(matches(pattern, path) for pattern in _patterns(text))]
    if not texts:
        return None
    return f"Rules that apply to {path}:\n\n" + "\n\n---\n\n".join(f"From {page}:\n\n{text.strip()}" for page, text in texts)
