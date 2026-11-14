"""Check: every name in the index's alias table is still defined in the code.

The alias table maps an everyday phrase to the name the code uses. When the
code renames the thing, the table goes on sending agents to a name that is gone.

Config: "index" (default INDEX.md), "heading" (default "Search aliases"),
"code" (default src): the folder the names must be defined under.
"""
import re

from wslib import markdown, symbols
from wslib.parts import finding

KIND = "check"
NAME = re.compile(r"`([A-Za-z_$][\w$]*)`")


def run(snapshot, config):
    index = config.get("index", "INDEX.md")
    heading = markdown.slug(config.get("heading", "Search aliases"))
    code = config.get("code", "src")

    text = snapshot.read(index) if snapshot.is_file(index) else None
    if text is None:
        return [finding(index, 1, "the index is missing, so its aliases cannot be checked")]

    rows, inside = [], False
    for number, line in markdown.prose_lines(text):
        title = markdown.ATX.match(line)
        if title:
            inside = markdown.slug(title.group(2)) == heading
        elif inside and line.lstrip().startswith("|"):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) >= 2 and not set(cells[1]) <= set("-: "):
                rows.extend((number, name) for name in NAME.findall(cells[1]))
    if not rows:
        return [finding(index, 1, f"no alias table with code names under the heading #{heading}")]

    defined = {name for _, _, _, name in symbols.scan(snapshot, code)}
    return [finding(index, number, f"alias points at {name}, which is not defined under {code}/")
            for number, name in rows if name not in defined]
