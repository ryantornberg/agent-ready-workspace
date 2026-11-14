#!/usr/bin/env python3
"""Fail when the docs stop matching themselves.

    python3 checks/check_docs.py                     # every markdown file under the current folder
    python3 checks/check_docs.py --changed A.md B.md # also fail if a changed page is past its review date
    python3 checks/check_docs.py --root DIR --max-age 180 --today 2026-01-31

Two checks:

  links      A relative link must point at a file that exists. A link with a
             #fragment must match a heading in that file.
  freshness  A page may carry "last-reviewed: YYYY-MM-DD" in its front matter.
             A page older than --max-age days is listed as a warning. It is an
             error only when the page is named in --changed: whoever edits a
             stale page reviews it and moves the date.

Exit 1 on any error. Standard library only.
"""
import argparse
import datetime
import pathlib
import re
import sys

SKIP_DIRS = {".git", "archive", "node_modules", ".venv"}
LINK = re.compile(r"(?<!\!)\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")
REVIEWED = re.compile(r"^last-reviewed:\s*(\d{4}-\d{2}-\d{2})\s*$")
EXTERNAL = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def prose_lines(text):
    """Yield (line number, line) for lines outside fenced code blocks."""
    fenced = False
    for number, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            fenced = not fenced
            continue
        if not fenced:
            yield number, line


def slug(heading):
    """The anchor GitHub gives a heading: lower case, punctuation dropped, spaces to hyphens."""
    heading = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading)  # a link in a heading keeps its text
    heading = re.sub(r"[`*_]", "", heading).strip().lower()
    heading = re.sub(r"[^\w\- ]", "", heading)
    return heading.replace(" ", "-")


def anchors(text):
    """Every heading anchor in a page. A repeated heading gets -1, -2, as on GitHub."""
    seen, found = {}, set()
    for _, line in prose_lines(text):
        match = HEADING.match(line)
        if not match:
            continue
        base = slug(match.group(2))
        count = seen.get(base, 0)
        seen[base] = count + 1
        found.add(base if count == 0 else f"{base}-{count}")
    return found


def reviewed_on(text):
    """The last-reviewed date from the front matter, or None."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            return None
        match = REVIEWED.match(line)
        if match:
            return datetime.date.fromisoformat(match.group(1))
    return None


def markdown_files(root):
    for path in sorted(root.rglob("*.md")):
        if not SKIP_DIRS.intersection(path.relative_to(root).parts):
            yield path


def check(root, changed=(), max_age=180, today=None):
    """Return (errors, warnings) as lists of "file:line: message" strings."""
    root = pathlib.Path(root).resolve()
    today = today or datetime.date.today()
    changed = {(root / c).resolve() for c in changed}
    texts = {}

    def read(path):
        if path not in texts:
            texts[path] = path.read_text(encoding="utf-8")
        return texts[path]

    errors, warnings = [], []
    for path in markdown_files(root):
        name = path.relative_to(root).as_posix()
        text = read(path)

        for number, line in prose_lines(text):
            line = re.sub(r"`[^`]*`", "", line)  # a link inside inline code is an example, not a link
            for target in LINK.findall(line):
                if EXTERNAL.match(target):
                    continue
                file_part, _, fragment = target.partition("#")
                dest = (path.parent / file_part).resolve() if file_part else path
                if not dest.exists():
                    errors.append(f"{name}:{number}: link to missing file: {target}")
                elif fragment and dest.suffix == ".md" and fragment.lower() not in anchors(read(dest)):
                    errors.append(f"{name}:{number}: no heading for #{fragment} in {dest.relative_to(root).as_posix()}")

        date = reviewed_on(text)
        if date and (today - date).days > max_age:
            message = f"{name}:1: last reviewed {date}, more than {max_age} days ago"
            if path in changed:
                errors.append(message + "; you edited it, so review it and move the date")
            else:
                warnings.append(message)
    return errors, warnings


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check links and review dates in markdown docs.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--changed", nargs="*", default=[], help="files in this commit; a stale one is an error")
    parser.add_argument("--max-age", type=int, default=180, help="days a review date stays fresh")
    parser.add_argument("--today", type=datetime.date.fromisoformat, help="override today's date, for tests")
    args = parser.parse_args(argv)

    errors, warnings = check(args.root, args.changed, args.max_age, args.today)
    for line in warnings:
        print(f"warning: {line}")
    for line in errors:
        print(f"error: {line}")
    if errors:
        print(f"\n{len(errors)} error(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
