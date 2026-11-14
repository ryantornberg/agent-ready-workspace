"""Check: every name in the index's alias table is still defined in the code.

The alias table maps an everyday phrase to the name the code uses. When the
code renames the thing, the table goes on sending agents to a name that is gone.

Each row's second column holds one simple name in backticks, such as
`ReconciliationWorker`. A row this check cannot read is an error, not a pass.
A constructor does not count as a definition: rename a class and leave its
constructor behind, and the alias is still dangling.

Config: "index" (default INDEX.md), "heading" (default "Search aliases"),
"code" (default src): the folder the names must be defined under;
"exclude": folders under it that do not count, such as shelved code.
"""
import re

from wslib import markdown, symbols
from wslib.parts import finding

KIND = "check"
NAME = re.compile(r"^`([A-Za-z_$][\w$]*)`$")


def run(snapshot, config):
    index = config.get("index", "INDEX.md")
    heading = markdown.slug(config.get("heading", "Search aliases"))
    code = config.get("code", "src")
    excluded = tuple(folder.strip("/") + "/" for folder in config.get("exclude", ()))

    text = snapshot.read(index) if snapshot.is_file(index) else None
    if text is None:
        return [finding(index, 1, "the index is missing, so its aliases cannot be checked")]

    found, rows, inside, header_seen = [], [], False, False
    for number, line in markdown.prose_lines(text):
        title = markdown.ATX.match(line)
        if title:
            inside, header_seen = markdown.slug(title.group(2)) == heading, False
        elif inside and line.lstrip().startswith("|"):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if all(set(cell) <= set("-: ") for cell in cells):
                continue                      # the |---|---| row
            if not header_seen:
                header_seen = True            # the column titles
                continue
            name = NAME.match(cells[1]) if len(cells) == 2 else None
            if name:
                rows.append((number, name.group(1)))
            else:
                found.append(finding(index, number, "cannot read this alias row: it needs two columns, the second one name in backticks"))
    if not rows and not found:
        return [finding(index, 1, f"no alias table under the heading #{heading}")]

    defined = {name for path, _, kind, name in symbols.scan(snapshot, code)
               if kind != "constructor" and not path.startswith(excluded)}
    found.extend(finding(index, number, f"alias points at {name}, which is not defined under {code}/")
                 for number, name in rows if name not in defined)
    return found
