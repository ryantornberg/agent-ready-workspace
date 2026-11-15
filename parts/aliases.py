"""Check: every name in the index's alias table is still defined in the code.

The alias table maps an everyday phrase to the name the code uses. When the
code renames the thing, the table goes on sending agents to a name that is gone.

Each row's second column holds one simple name in backticks, such as
`ReconciliationWorker`. A row this check cannot read is an error, not a pass.
A constructor does not count as a definition: rename a class and leave its
constructor behind, and the alias is still dangling.

The contract pages named in "contract", such as AGENTS.md, are held to the
same rule: a name in backticks there must still be defined. Only names that
read as code are taken: one word of letters and digits that mixes upper and
lower case, such as `AccountFreeze` or `quarterlyExport`. A word in one case,
such as `main` or `KIND`, a name with an underscore, a path and a command are
left alone, because a contract names branches, settings and commands too.

Config: "index" (default INDEX.md), "heading" (default "Search aliases"),
"code" (default src): the folder the names must be defined under;
"exclude": folders under it that do not count, such as shelved code;
"contract": pages whose backticked code names must be defined (default none).
"""
import re

from wslib import markdown, symbols
from wslib.parts import finding

KIND = "check"
NAME = re.compile(r"^`([A-Za-z_$][\w$]*)`$")
SPAN = re.compile(r"(?<!`)`([A-Za-z][A-Za-z0-9]*)`(?!`)")


def code_names(text):
    """(line, name) for each backticked name in a page's prose that reads as code: mixed case, letters and digits."""
    for number, line in markdown.prose_lines(text):
        for match in SPAN.finditer(line):
            name = match.group(1)
            if name != name.lower() and name != name.upper():
                yield number, name


def run(snapshot, config):
    index = config.get("index", "INDEX.md")
    heading = markdown.slug(config.get("heading", "Search aliases"))
    code = config.get("code", "src")
    excluded = tuple(folder.strip("/") + "/" for folder in config.get("exclude", ()))

    if not snapshot.is_file(index):
        return [finding(index, 1, "the index is missing, so its aliases cannot be checked")]
    text = snapshot.read(index)
    if text is None:
        return [finding(index, 1, f"the index {snapshot.not_utf8(index)}, so its aliases cannot be checked")]

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

    for page in config.get("contract", ()):
        if not snapshot.is_file(page):
            found.append(finding(page, 1, "the contract page is missing, so its names cannot be checked"))
            continue
        text = snapshot.read(page)
        if text is None:
            found.append(finding(page, 1, f"the contract page {snapshot.not_utf8(page)}, so its names cannot be checked"))
            continue
        found.extend(finding(page, number, f"the contract names {name}, which is not defined under {code}/")
                     for number, name in code_names(text) if name not in defined)
    return found
