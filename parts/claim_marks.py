"""Check: every claim line in a fix record's report is marked verified or inferred.

A fix record is a page in "folder" (default docs/records/fixes), other than its README. Its shape is in
docs/templates/fix-record.md. The check reads the record's `## Report` section, up to the next heading of level
one or two, and sorts each line:

- a blank line, or a fence line starting with three backticks, is skipped;
- a line starting `Fixed:` or `Not done:` is a header line;
- every other line is a claim line. After an optional `- ` or `* ` list marker and optional `**`, it must start
  with `verified` or `inferred`, followed by a space, a colon or `**`.

It fails a fix record with no `## Report` section, and each claim line not so marked. A claim recorded as true
because it was plausible, not because it was checked, is how a confident wrong answer gets merged; the mark says
which one a reader holds. A folder with no fix records passes: a workspace that has fixed nothing yet has nothing
to check.

Config: "folder" (default docs/records/fixes).
"""
import re

from wslib.parts import finding

KIND = "check"
PAGE = "docs/templates/fix-record.md"   # the rule's page, which every finding names (criterion 34)
FOLDER = "docs/records/fixes"
REPORT = re.compile(r"^##\s+Report\s*$")
HEADING = re.compile(r"^#{1,2}\s")
HEADER_LINE = re.compile(r"^(Fixed|Not done):")
MARKED = re.compile(r"^(?:[-*]\s+)?(?:\*\*)?(verified|inferred)(?=[\s:*]|$)")


def claim_lines(text):
    """[(line number, line)] of the claim lines in the report, or None when the record has no report section."""
    lines = (text or "").replace("\r\n", "\n").split("\n")
    start = next((n for n, line in enumerate(lines) if REPORT.match(line.strip())), None)
    if start is None:
        return None
    claims, fenced = [], False
    for number in range(start + 1, len(lines)):
        line = lines[number].strip()
        if line.startswith("```"):
            fenced = not fenced
            continue
        if not fenced and HEADING.match(line):
            break
        if not line or HEADER_LINE.match(line):
            continue
        claims.append((number + 1, line))
    return claims


def run(snapshot, config):
    folder = config.get("folder", FOLDER).rstrip("/")
    found = []
    for path in snapshot.paths((".md",), under=folder):
        if path.rsplit("/", 1)[-1].lower() == "readme.md":
            continue
        claims = claim_lines(snapshot.read(path))
        if claims is None:
            found.append(finding(path, 1, f"the fix record has no '## Report' section; end it with one, even when "
                                          f"the work stopped early; see {PAGE}"))
            continue
        for number, line in claims:
            if not MARKED.match(line):
                found.append(finding(path, number, f"a claim line in the report is not marked verified or inferred: "
                                                   f"{line[:60]!r}; start it with 'verified' (you ran something and saw "
                                                   f"the result) or 'inferred' (you reasoned your way there); see "
                                                   f"{PAGE}"))
    return found
