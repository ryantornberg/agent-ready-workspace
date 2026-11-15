"""Check: a page past its review date fails when the commit edits it.

A page carries "last-reviewed: YYYY-MM-DD" in its front matter. A stale page is
a warning. It becomes an error when it is in the snapshot's changed set:
whoever edits a stale page reviews the whole page and moves the date.

A date may be one day ahead of today in UTC, so a page dated in a time zone
ahead of UTC passes everywhere. Pages inside a code repository under the
workspace, and symbolic links, are not read. A page that is not UTF-8 is an
error, not skipped.

Config: "max_age_days" (default 180); "require": pages, and folders whose pages,
must carry a date, so deleting the line is not a way out; "skip": folders not
checked; "today": a fixed date in UTC, for cases.
"""
import datetime
import re

from wslib import markdown
from wslib.parts import finding

KIND = "check"
FIELD = re.compile(r"^last-reviewed\s*:\s*(.*?)\s*$")


def run(snapshot, config):
    max_age = config.get("max_age_days", 180)
    today = datetime.date.fromisoformat(config["today"]) if config.get("today") \
        else datetime.datetime.now(datetime.timezone.utc).date()
    required = [entry.strip("/") for entry in config.get("require", ())]
    found = []

    for page in snapshot.pages(skip=config.get("skip", ())):
        text = snapshot.read(page)
        if text is None:
            found.append(finding(page, 1, f"{snapshot.not_utf8(page)}, so its review date was not read; save it as UTF-8"))
            continue
        value, line = None, 1
        for number, row in enumerate(markdown.split_front_matter(text)[0], 2):
            match = FIELD.match(row)
            if match:
                value, line = match.group(1).strip("\"'"), number
                break

        if value is None:
            if any(page == entry or page.startswith(entry + "/") for entry in required):
                found.append(finding(page, 1, "no last-reviewed date; pages here must carry one"))
            continue
        try:
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
                raise ValueError(value)
            reviewed = datetime.date.fromisoformat(value)
        except ValueError:
            found.append(finding(page, line, f"last-reviewed is not a date: {value}"))
            continue
        if reviewed > today + datetime.timedelta(days=1):
            found.append(finding(page, line, f"last-reviewed {reviewed} is in the future"))
        elif (today - reviewed).days > max_age:
            message = f"last reviewed {reviewed}, more than {max_age} days ago"
            if page in snapshot.changed:
                found.append(finding(page, line, message + "; this commit edits it, so review it and move the date"))
            else:
                found.append(finding(page, line, message, level="warning"))
    return found
