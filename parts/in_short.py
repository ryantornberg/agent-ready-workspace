"""Check: a plan, decision record or milestone page says its verdict near its title.

A reporting page that opens with background makes its reader read all of it for the
answer. So each page in these folders carries a line that starts **In short:** within
LIMIT lines after its title: the first line that starts "# ". Blank lines count. The
line may sit in a block quote, and the colon may sit inside or outside the bold.
A README, a template and a page whose name starts with "_" are skipped. A page that
cannot be read fails, named.

Config: "folders" (default docs/plans, docs/decisions and docs/milestones).
"""
import re

from wslib import markdown
from wslib.parts import finding

KIND = "check"
LIMIT = 15
LINE = re.compile(r"^\s*(?:>\s*)?\*\*In short:?\*\*:?")


def run(snapshot, config):
    folders = config.get("folders", ["docs/plans", "docs/decisions", "docs/milestones"])
    found = []
    for folder in folders:
        for page in snapshot.pages(skip=()):
            if not page.startswith(folder.rstrip("/") + "/"):
                continue
            name = page.rsplit("/", 1)[-1]
            if name.lower() == "readme.md" or "template" in name.lower() or name.startswith("_"):
                continue
            text = snapshot.read(page)
            if text is None:
                found.append(finding(page, 1, f"{snapshot.not_utf8(page)}, so its In short line was not read"))
                continue
            lines = text.replace("\r\n", "\n").split("\n")
            skipped = markdown.split_front_matter(text)[1]
            title = next((n for n, line in enumerate(lines, 1) if n > skipped and line.startswith("# ")), None)
            if title is None:
                found.append(finding(page, 1, "has no title, a first line that starts \"# \", to put an In short line under"))
                continue
            if not any(LINE.match(line) for line in lines[title:title + LIMIT]):
                found.append(finding(page, title, f"has no **In short:** line within {LIMIT} lines of its title; say the "
                                                  f"verdict there, before the background"))
    return found
