"""Check: every rule in a rules table says how it is enforced, and a tag that names a part or case is true.

A rule lives on the page it belongs to, in a table whose header is "| Rule | Enforced by |". The second column
holds one or more tags in backticks, separated by commas:

  `part#case`     the part, in the manifest, enforces it, and the named case of that part shows it doing so
  `eval:case`     an eval case grades it: evals/cases/<case>.json exists, or, in an instance made from the
                  kit, the kit's lock (kit.lock.json) names it among the kit's cases, which stay in the kit
  `prose`         nothing checks it; the page says it and a reader keeps it

A tag that names a part not in the manifest, a case the part does not have, or an eval case that does not
exist fails, so a rule cannot claim an enforcement it lost. `python3 ws.py rules` prints the whole register
with a count per kind of tag. The contract stays at routing and traps; the rules live on their pages.

Config: "skip": folders not read (default evals/scaffold and archive).
"""
import json
import re

from wslib import kitlock
from wslib.parts import finding

KIND = "check"
PAGE = "docs/layout.md"
HEADER = re.compile(r"^\|\s*Rule\s*\|\s*Enforced by\s*\|\s*$")


def register(snapshot, skip=("evals/scaffold", "archive")):
    """[(page, line number, rule text, [tags])] of every rules table in the workspace's pages."""
    found = []
    for page in snapshot.pages(skip=skip):
        text = snapshot.read(page)
        if text is None:
            continue
        inside = False
        for number, line in enumerate(text.replace("\r\n", "\n").split("\n"), 1):
            if HEADER.match(line.strip()):
                inside = True
                continue
            if not inside:
                continue
            if not line.strip().startswith("|"):
                inside = False
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) < 2 or set(cells[0]) <= set("-: "):
                continue
            found.append((page, number, cells[0], re.findall(r"`([^`]+)`", cells[-1])))
    return found


def kind_of(tag):
    return "prose" if tag == "prose" else "eval" if tag.startswith("eval:") else "part" if "#" in tag else None


def run(snapshot, config):
    skip = config.get("skip", ("evals/scaffold", "archive"))
    try:
        manifest = json.loads(snapshot.read("workspace.json") or "")
        used = {entry.get("use") for entry in manifest.get("parts", []) if isinstance(entry, dict)}
    except (ValueError, AttributeError):
        used = set()
    try:
        kit_cases = kitlock.cases(kitlock.read(snapshot))
    except kitlock.LockError:
        kit_cases = set()       # the proof check names the unreadable lock
    found, cases = [], {}
    for page, line, rule, tags in register(snapshot, skip):
        if not tags:
            found.append(finding(page, line, f"the rule {rule[:60]!r} has no tag; tag it `part#case`, `eval:case` or "
                                             f"`prose`; see {PAGE}"))
        for tag in tags:
            kind = kind_of(tag)
            if kind is None:
                found.append(finding(page, line, f"{tag!r} is not a tag; write `part#case`, `eval:case` or `prose`"))
            elif kind == "eval" and not snapshot.is_file(f"evals/cases/{tag[5:]}.json") and tag[5:] not in kit_cases:
                found.append(finding(page, line, f"the tag {tag} names an eval case that does not exist"))
            elif kind == "part":
                part, _, case = tag.partition("#")
                if part not in used:
                    found.append(finding(page, line, f"the tag {tag} names part {part}, which the manifest does not use; "
                                                     f"retag the rule `prose`, or restore the part"))
                    continue
                if part not in cases:
                    try:
                        cases[part] = {c.get("name") for c in json.loads(snapshot.read(f"parts/{part}.cases.json") or "")}
                    except (ValueError, AttributeError, TypeError):
                        cases[part] = set()
                if case not in cases[part]:
                    found.append(finding(page, line, f"the tag {tag} names a case part {part} does not have; name one "
                                                     f"of its cases that shows the rule enforced"))
    return found
