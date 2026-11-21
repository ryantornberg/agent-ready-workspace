"""Check: the index of instruction-review records lists every record, matches each one, and covers the required pages.

Each review of a guidance page leaves a record in "folder" (docs/playbooks/instruction-review.md says how). The
index, "index", holds one table with the header "| Record | Covers | Classes found |": a row per record, with a
link to the record, the pages its `covers:` front matter lists (in backticks, comma-separated), and the classes
of its findings, or "none". A finding whose disposition starts with "declined" is not counted.

It fails when a record has no row, a row names no record or a missing one, a row's pages or classes differ from
its record, a record has no covers line or covers more than one page, a finding's class is not one of the six, or a page in "required" has no
record. The stop rule counts classes from this index, so it must agree with the records.

Config: "folder" (default docs/records/instruction-reviews), "index" (default <folder>/README.md), "required":
pages that must each have a record.
"""
import re

from wslib import markdown
from wslib.parts import finding

KIND = "check"
PAGE = "docs/playbooks/instruction-review.md"
FOLDER = "docs/records/instruction-reviews"
CLASSES = ("contradiction", "step", "trigger", "enforcement", "placement", "eval-case")
INDEX_HEADER = re.compile(r"^\|\s*Record\s*\|\s*Covers\s*\|\s*Classes found\s*\|\s*$")
FINDINGS_HEADER = re.compile(r"^\|\s*#\s*\|\s*Class\s*\|\s*Where\s*\|\s*Finding\s*\|\s*Disposition\s*\|\s*$")
COVERS = re.compile(r"^covers\s*:\s*(.*?)\s*$")


def table(text, header):
    """[(line number, [cells])] of the rows of the first table whose header matches."""
    rows, inside = [], False
    for number, line in enumerate((text or "").replace("\r\n", "\n").split("\n"), 1):
        if not inside:
            inside = bool(header.match(line.strip()))
            continue
        if not line.strip().startswith("|"):
            break
        cells = [cell.strip().replace("\\|", "|") for cell in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
        if not set("".join(cells)) <= set("-: "):
            rows.append((number, cells))
    return rows if inside else None


def covers(text):
    rows, _ = markdown.split_front_matter(text or "")
    for row in rows:
        match = COVERS.match(row)
        if match:
            return {path.strip().strip("`") for path in match.group(1).split(",") if path.strip()}
    return None


def classes(text):
    """(the set of classes counted, [(line, class) not among the six]), or None when the record has no findings table."""
    rows = table(text, FINDINGS_HEADER)
    if rows is None:
        return None
    counted, odd = set(), []
    for number, cells in rows:
        if len(cells) < 5:
            continue
        name = cells[1].strip("`").strip().lower()
        if name not in CLASSES:
            odd.append((number, cells[1]))
        elif not cells[4].lower().startswith("declined"):
            counted.add(name)
    return counted, odd


def _listed(cell):
    return {part.strip().strip("`") for part in cell.split(",") if part.strip()}


def run(snapshot, config):
    folder = config.get("folder", FOLDER).rstrip("/")
    index = config.get("index", folder + "/README.md")
    required = config.get("required", [])
    if not isinstance(required, list) or not all(isinstance(page, str) and page for page in required):
        return [finding("workspace.json", 1, f"review_index's \"required\" must be a list of pages; fix it in the "
                                             f"manifest; see {PAGE}")]
    text = snapshot.read(index) if snapshot.is_file(index) else None
    rows = table(text, INDEX_HEADER) if text is not None else None
    if rows is None:
        return [finding(index, 1, f"the index of instruction-review records needs a table with the header "
                                  f"'| Record | Covers | Classes found |'; add it; see {PAGE}")]
    records = [path for path in snapshot.paths((".md",), under=folder)
               if "/" not in path[len(folder) + 1:] and path != index]
    found, listed, covered = [], set(), set()
    for number, cells in rows:
        if len(cells) < 3:
            found.append(finding(index, number, f"a row needs three cells: record, covers, classes found; fix it; "
                                                f"see {PAGE}"))
            continue
        targets = list(markdown.inline_targets(cells[0])) or re.findall(r"`([^`]+)`", cells[0])
        resolved = markdown.resolve(index, targets[0]) if targets else None
        record = resolved[0] if resolved else None
        if record is None or not snapshot.is_file(record):
            found.append(finding(index, number, f"the row {cells[0]!r} names no review record that exists; link the "
                                                f"record, or remove the row; see {PAGE}"))
            continue
        listed.add(record)
        record_text = snapshot.read(record)
        pages = covers(record_text)
        if pages is None:
            found.append(finding(record, 1, f"the review record has no 'covers:' line naming the pages it reviewed; "
                                            f"add it to its front matter; see {PAGE}"))
            continue
        covered |= pages
        if len(pages) != 1:
            found.append(finding(record, 1, f"the review record covers {len(pages)} pages; a record covers exactly one, "
                                            f"so the stop rule can count per page. Split it, one record per page; "
                                            f"see {PAGE}"))
        if _listed(cells[1]) != pages:
            found.append(finding(index, number, f"the row for {record} lists {sorted(_listed(cells[1]))}, but the "
                                                f"record covers {sorted(pages)}; make them agree; see {PAGE}"))
        got = classes(record_text)
        if got is None:
            found.append(finding(record, 1, f"the review record has no findings table "
                                            f"'| # | Class | Where | Finding | Disposition |'; add it; see {PAGE}"))
            continue
        counted, odd = got
        for line, name in odd:
            found.append(finding(record, line, f"{name!r} is not a finding class; use one of {', '.join(CLASSES)}; "
                                               f"see {PAGE}"))
        want = cells[2].strip().lower()
        stated = set() if want == "none" else _listed(want)
        if stated != counted:
            found.append(finding(index, number, f"the row for {record} gives the classes {cells[2]!r}, but the "
                                                f"record's findings count {', '.join(sorted(counted)) or 'none'}; "
                                                f"make them agree; see {PAGE}"))
    for record in records:
        if record not in listed:
            found.append(finding(record, 1, f"the review record is not in the index {index}; add its row; see {PAGE}"))
    for page in required:
        if page not in covered:
            found.append(finding(index, 1, f"no review record covers {page}, which must have one; run the review on "
                                           f"it and index the record; see {PAGE}"))
    return found
