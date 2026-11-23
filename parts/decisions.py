"""Check: every decision record keeps the shape the decision record template sets.

A record is a page directly in "folder" (default docs/decisions) whose name is not README.md. It fails when:
  - its file name is not a four-digit number, a hyphen and a topic in lower-case words joined by hyphens;
  - another record has the same number;
  - its front matter has no "date" that is a calendar date, YYYY-MM-DD, or no "deciders";
  - its title, the first line that starts "# ", is not "# <number>: <the decision>", with the file's number;
  - it lacks one of the sections Context, Decision, What it gave up and Options rejected ("Rejected" is that
    section's earlier name), or holds them out of that order; other sections may sit anywhere after Context;
  - the word "Amended" or "amended", outside code and outside a pair of double quotes, is not followed by a space
    and a calendar date, or that date is before the record's own date: an amendment is a dated paragraph;
  - its status is superseded and "superseded-by" does not name another record, or no line starts
    "Superseded by"; a "superseded-by" on a record of another status, or a "supersedes" that names no record.

The status values, the kind and the In short line are page_kinds' and in_short's to check, so this part does not
repeat them. It fails when the folder holds no record, so a moved folder cannot make it pass by reading nothing.

Config: "folder" (default docs/decisions).
"""
import datetime
import re

from wslib import markdown
from wslib.parts import finding

KIND = "check"
PAGE = "docs/templates/decision-record.md"
NAME = re.compile(r"^(\d{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
FIELD = re.compile(r"^([A-Za-z][\w-]*)\s*:\s*(.*?)\s*$")
TITLE = re.compile(r"^# (\d{4}): \S")
HEADING = re.compile(r"^## +(.*?)\s*#*\s*$")
SECTIONS = (("context",), ("decision",), ("what it gave up",), ("options rejected", "rejected"))
SHOWN = ("Context", "Decision", "What it gave up", "Options rejected")
WORD = re.compile(r"\b[Aa]mended\b")
DATED = re.compile(r" (\d{4}-\d{2}-\d{2})\b")
NUMBER = re.compile(r"^\d{4}$")
BANNER = re.compile(r"^\s*(?:>\s*)?(?:\*\*)?Superseded by\b")


def _date(value):
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", value or ""):
        return None
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        return None


def _front(text):
    rows, skipped = markdown.split_front_matter(text)
    found = {}
    for number, row in enumerate(rows, 2):
        match = FIELD.match(row)
        if match and match.group(1) not in found:
            found[match.group(1)] = (match.group(2).strip("\"'"), number)
    return found, skipped


def _quoted(line, start, end):
    """Whether the word at line[start:end] sits inside a pair of double quotes on its line."""
    return line[:start].count('"') % 2 == 1 and '"' in line[end:]


def _record(page, text, number, numbers, front, skipped):
    found = []
    date = None
    value, line = front.get("date", (None, 1))
    if value is None:
        found.append(finding(page, 1, f"has no date in its front matter; add 'date: YYYY-MM-DD', the day it took its "
                                      f"status; see {PAGE}"))
    else:
        date = _date(value)
        if date is None:
            found.append(finding(page, line, f"date {value!r} is not a calendar date; write YYYY-MM-DD; see {PAGE}"))
    if not front.get("deciders", ("", 1))[0]:
        found.append(finding(page, front.get("deciders", (None, 1))[1],
                             f"has no deciders in its front matter; name who decided, or who will; see {PAGE}"))

    status = front.get("status", (None, 1))[0]
    later, later_line = front.get("superseded-by", (None, 1))
    lines = text.replace("\r\n", "\n").split("\n")
    if status == "superseded":
        if later is None:
            found.append(finding(page, front["status"][1], f"is superseded but names no 'superseded-by: NNNN'; "
                                                           f"see {PAGE}"))
        elif not NUMBER.match(later) or later == number or later not in numbers:
            found.append(finding(page, later_line, f"superseded-by {later!r} names no other record in the folder; "
                                                   f"see {PAGE}"))
        if not any(BANNER.match(row) for row in lines[skipped:]):
            found.append(finding(page, front["status"][1], f"is superseded but has no line starting 'Superseded by' "
                                                           f"naming its successor and what still binds; see {PAGE}"))
    elif later is not None:
        found.append(finding(page, later_line, f"names superseded-by {later!r} but its status is {status!r}, not "
                                               f"superseded; see {PAGE}"))
    earlier, earlier_line = front.get("supersedes", (None, 1))
    if earlier is not None and (not NUMBER.match(earlier) or earlier == number or earlier not in numbers):
        found.append(finding(page, earlier_line, f"supersedes {earlier!r}, which names no other record in the "
                                                 f"folder; see {PAGE}"))

    title = None
    headings = []
    for line_number, row in markdown.prose_lines(text):
        if title is None and row.startswith("# "):
            title = (line_number, row)
        match = HEADING.match(row)
        if match:
            headings.append((line_number, match.group(1).strip().lower()))
        plain = markdown.strip_code_spans(row)
        for word in WORD.finditer(plain):
            if _quoted(plain, word.start(), word.end()):
                continue
            dated = DATED.match(plain, word.end())
            when = _date(dated.group(1)) if dated else None
            if when is None:
                found.append(finding(page, line_number, f"says {word.group(0)!r} with no date after it; an amendment "
                                                        f"reads 'Amended YYYY-MM-DD, <who>: <what changed>'; see {PAGE}"))
            elif date is not None and when < date:
                found.append(finding(page, line_number, f"has an amendment dated {when}, before the record's own date "
                                                        f"{date}; see {PAGE}"))

    if title is None:
        found.append(finding(page, 1, f"has no title; it opens '# {number}: <the decision>'; see {PAGE}"))
    else:
        match = TITLE.match(title[1])
        if not match or match.group(1) != number:
            found.append(finding(page, title[0], f"title must read '# {number}: <the decision>', with the file's "
                                                 f"number; see {PAGE}"))

    position = 0
    for index, names in enumerate(SECTIONS):
        where = next((i for i, (_, name) in enumerate(headings) if name in names), None)
        if where is None:
            found.append(finding(page, 1, f"has no '## {SHOWN[index]}' section; a record holds "
                                          f"{', '.join(SHOWN)}, in that order; see {PAGE}"))
        elif where < position:
            found.append(finding(page, headings[where][0], f"'## {SHOWN[index]}' is out of order; a record holds "
                                                           f"{', '.join(SHOWN)}, in that order; see {PAGE}"))
        else:
            position = where
    return found


def run(snapshot, config):
    folder = config.get("folder", "docs/decisions").rstrip("/")
    pages = [page for page in snapshot.pages(skip=())
             if page.startswith(folder + "/") and "/" not in page[len(folder) + 1:]
             and page.rsplit("/", 1)[-1].lower() != "readme.md"]
    if not pages:
        return [finding(folder, 1, f"holds no decision record, so nothing was checked; see {PAGE}")]
    found = []
    numbered = {}
    for page in sorted(pages):
        match = NAME.match(page.rsplit("/", 1)[-1])
        if not match:
            found.append(finding(page, 1, f"file name must be a four-digit number, a hyphen and a topic in lower-case "
                                          f"words joined by hyphens, such as 0012-one-lookup.md; see {PAGE}"))
            continue
        numbered.setdefault(match.group(1), []).append(page)
    for number, same in numbered.items():
        if len(same) > 1:
            for page in same:
                others = ", ".join(other for other in same if other != page)
                found.append(finding(page, 1, f"has number {number}, which {others} also has; give the later record "
                                              f"the next free number; see {PAGE}"))
    for number, same in sorted(numbered.items()):
        for page in same:
            text = snapshot.read(page)
            if text is None:
                found.append(finding(page, 1, f"{snapshot.not_utf8(page)}, so its shape was not checked"))
                continue
            front, skipped = _front(text)
            found += _record(page, text, number, set(numbered), front, skipped)
    return found
