"""Check: a page past its review date fails when the commit edits it.

A page carries "last-reviewed: YYYY-MM-DD" in its front matter. A stale page is
a warning. It becomes an error when it is in the snapshot's changed set:
whoever edits a stale page reviews the whole page and moves the date.

Config: "max_age_days" (default 180); "require": folders whose pages must carry
a date, so deleting the line is not a way out; "skip": folders not checked;
"today": a fixed date, for cases.
"""
import datetime
import re

from wslib import markdown
from wslib.parts import finding

KIND = "check"
FIELD = re.compile(r"^last-reviewed\s*:\s*(.*?)\s*$")


def run(snapshot, config):
    max_age = config.get("max_age_days", 180)
    today = datetime.date.fromisoformat(config["today"]) if config.get("today") else datetime.date.today()
    required = tuple(folder.strip("/") + "/" for folder in config.get("require", ()))
    found = []

    for page in snapshot.paths(suffixes=(".md",), skip=config.get("skip", ())):
        text = snapshot.read(page)
        if text is None:
            continue  # the links check reports a page that is not UTF-8
        value, line = None, 1
        for number, row in enumerate(markdown.split_front_matter(text)[0], 2):
            match = FIELD.match(row)
            if match:
                value, line = match.group(1).strip("\"'"), number
                break

        if value is None:
            if page.startswith(required):
                found.append(finding(page, 1, "no last-reviewed date; pages here must carry one"))
            continue
        try:
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
                raise ValueError(value)
            reviewed = datetime.date.fromisoformat(value)
        except ValueError:
            found.append(finding(page, line, f"last-reviewed is not a date: {value}"))
            continue
        if reviewed > today:
            found.append(finding(page, line, f"last-reviewed {reviewed} is in the future"))
        elif (today - reviewed).days > max_age:
            message = f"last reviewed {reviewed}, more than {max_age} days ago"
            if page in snapshot.changed:
                found.append(finding(page, line, message + "; this commit edits it, so review it and move the date"))
            else:
                found.append(finding(page, line, message, level="warning"))
    return found
