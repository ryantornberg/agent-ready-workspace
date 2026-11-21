"""Check: the always-loaded layer stays under its measured ceilings.

Every session reads the contract and the agent tools' pointer files before it starts, and every wrapper's
description is loaded into every session. Each byte there costs every session, and an added line can draw
attention from the rest (M2's longer index cost the guided arm 5 runs of 45). So the manifest sets a ceiling,
in bytes, for each group: a list of "files", or a "glob" of pages whose front-matter "field" is what loads.
The ceilings are ceilings, not targets.

Config: "limits": [{"what": name, "max_bytes": n, "files": [paths]} or {"what", "max_bytes", "glob", "field"}].
"""
import re

from wslib import markdown
from wslib.parts import finding

KIND = "check"
PAGE = "docs/layout.md"


def _glob(pattern):
    out = ""
    for char in pattern:
        out += "[^/]*" if char == "*" else re.escape(char)
    return re.compile(out + "$")


def _field(text, field):
    rows = markdown.split_front_matter(text)[0]
    for index, row in enumerate(rows):
        match = re.match(rf"^{re.escape(field)}\s*:\s*(.*)$", row)
        if match:
            value = match.group(1)
            for more in rows[index + 1:]:          # a folded value continues on indented lines
                if not more.startswith((" ", "\t")):
                    break
                value += " " + more.strip()
            return value.strip().strip("\"'")
    return ""


def run(snapshot, config):
    limits = config.get("limits", [])
    if not limits:
        return [finding("workspace.json", 1, "loaded_size sets no ceiling; give it the always-loaded groups")]
    found = []
    for limit in limits:
        what, ceiling = limit.get("what", "a group"), limit.get("max_bytes")
        if "glob" in limit:
            pattern = _glob(limit["glob"])
            texts = [snapshot.read(p) or "" for p in snapshot.paths() if pattern.match(p)]
            size = sum(len(_field(text, limit.get("field", "description")).encode("utf-8")) for text in texts)
        else:
            size = sum(len(snapshot.read_bytes(p) or b"") for p in limit.get("files", []) if snapshot.is_file(p))
        if not isinstance(ceiling, int):
            found.append(finding("workspace.json", 1, f"the ceiling for {what} is not a whole number of bytes"))
        elif size > ceiling:
            found.append(finding(limit.get("files", [limit.get("glob")])[0], 1,
                                 f"{what} loads {size} bytes into every session, over its ceiling of {ceiling}; cut "
                                 f"it, or move text to a page loaded on demand"))
    return found
