"""Check: every page says what kind it is, carries the front matter its kind needs, and opens in one order.

The kinds, their front matter and the opening order are set out in docs/layout.md. In short:

  kind        required front matter        controlled values
  playbook    kind, last-reviewed, proof   proof: proven | unproven
  how-to      kind, last-reviewed, proof
  tutorial    kind, last-reviewed
  reference   kind, last-reviewed
  template    kind, last-reviewed
  record      kind, last-reviewed
  decision    kind, last-reviewed, status  proposed | accepted | superseded | rejected
  plan        kind, last-reviewed, status  draft | approved | done | abandoned; milestone: M<n> (optional)
  milestone   kind, last-reviewed, status  open | signed off
  any kind    lane (optional)              development | qa | product | automation | devops

The opening, after the front matter: the title (the first line, "# "), then a purpose sentence of 25 words
or fewer (a decision record may open with its In short line instead), then the **In short** line (every kind
but a playbook and a record, which may leave it out), and on a plan, "## Key points" as the first section.
The 25-word limit does not apply to an approved or done plan, an accepted or superseded decision record or a
signed-off milestone record: those are frozen. A plan changes by a dated entry under "Changes after approval"
(template rule 6), a decision or milestone record by a dated "Amended" paragraph, with the layout's two
exceptions: an amendment may also edit a decision record's In short line, and a frozen page's front matter is
not frozen.

A page in a kind's own folder (docs/playbooks, docs/decisions, docs/plans, docs/milestones, docs/templates,
docs/tutorials, docs/records) must be of that kind; a README there is a reference page.

It also holds the review-date rule that the retired `freshness` check held: a page carries
"last-reviewed: YYYY-MM-DD"; a stale page is a warning, and an error when the change edits it; a date more
than one day ahead of today in UTC is refused; the pages and folders in "require_date" must carry one.

And it refuses a proof key or section proof line in any form but its exact one, through the same file
the eval hash strips them with (evals/proofkeys.py), so a variant is hashed, not hidden (decision record 0006).

It fails when it checks no pages, so a wrong folder setting cannot turn it off. Pages under a skipped folder,
such as archive/, inside a code repository, or behind a symbolic link are not read.

Config: "require_kind" (default ["docs"]), "require_date" (default []), "skip", "max_age_days" (180),
"today" (for cases), "proof_keys" (default evals/proofkeys.py; a workspace without it checks no proof keys).
"""
import datetime
import re
import types

from wslib import markdown
from wslib.parts import finding

KIND = "check"
PAGE = "docs/layout.md"
KINDS = ("playbook", "how-to", "tutorial", "reference", "template", "record", "decision", "plan", "milestone")
STATUS = {"decision": ("proposed", "accepted", "superseded", "rejected"),
          "plan": ("draft", "approved", "done", "abandoned"),
          "milestone": ("open", "signed off")}
FROZEN = {"decision": ("accepted", "superseded"), "plan": ("approved", "done"), "milestone": ("signed off",)}
REQUIRED = {"playbook": ("proof",), "how-to": ("proof",), "decision": ("status",), "plan": ("status",),
            "milestone": ("status",)}
NO_IN_SHORT = ("playbook", "record")
LANES = ("development", "qa", "product", "automation", "devops")
FOLDERS = {"docs/playbooks": "playbook", "docs/decisions": "decision", "docs/plans": "plan",
           "docs/milestones": "milestone", "docs/templates": "template", "docs/tutorials": "tutorial",
           "docs/records": "record"}
WORDS = 25
FIELD = re.compile(r"^([A-Za-z][\w-]*)\s*:\s*(.*?)\s*$")
IN_SHORT = re.compile(r"^\s*(?:>\s*)?\*\*In short:?\*\*:?")


def _under(page, entries):
    return any(page == entry or page.startswith(entry.rstrip("/") + "/") for entry in entries)


def _front(text):
    """({key: (value, line number)}, first line after the front matter, as an index into the lines)."""
    rows, skipped = markdown.split_front_matter(text)
    found = {}
    for number, row in enumerate(rows, 2):
        match = FIELD.match(row)
        if match and match.group(1) not in found:
            found[match.group(1)] = (match.group(2).strip("\"'"), number)
    return found, skipped


def _paragraphs(lines, start):
    """[(first line number, text)] of the blocks after start, split on blank lines; code fences kept whole."""
    blocks, current, first = [], [], None
    for index in range(start, len(lines)):
        line = lines[index]
        if not line.strip():
            if current:
                blocks.append((first, current))
            current, first = [], None
            continue
        if first is None:
            first = index + 1
        current.append(line)
    if current:
        blocks.append((first, current))
    return blocks


def _first_sentence(text):
    plain = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    plain = re.sub(r"\s+", " ", plain).strip()
    match = re.search(r"[.!?](?:\s|$)", plain)
    return plain[:match.end()].strip() if match else plain


def _date_findings(page, front, snapshot, config, today):
    found = []
    value, line = front.get("last-reviewed", (None, 1))
    max_age = config.get("max_age_days", 180)
    if value is None:
        if _under(page, config.get("require_date", ())):
            found.append(finding(page, 1, f"no last-reviewed date; pages here must carry one; add "
                                          f"'last-reviewed: {today}' to its front matter; see {PAGE}"))
        return found
    try:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            raise ValueError(value)
        reviewed = datetime.date.fromisoformat(value)
    except ValueError:
        return [finding(page, line, f"last-reviewed is not a date: {value}; write YYYY-MM-DD; see {PAGE}")]
    if reviewed > today + datetime.timedelta(days=1):
        found.append(finding(page, line, f"last-reviewed {reviewed} is in the future; see {PAGE}"))
    elif (today - reviewed).days > max_age:
        message = f"last reviewed {reviewed}, more than {max_age} days ago"
        if page in snapshot.changed:
            found.append(finding(page, line, message + "; this commit edits it, so review it and move the date"))
        else:
            found.append(finding(page, line, message, level="warning"))
    return found


def _load_proof_keys(snapshot, path):
    if not snapshot.is_file(path):
        return None
    module = types.ModuleType("page_kinds_proof_keys")
    exec(compile(snapshot.read(path) or "", path, "exec"), module.__dict__)
    return module


def _kind_findings(page, text, front, skipped):
    found = []
    kind = front.get("kind", (None, 1))[0]
    if kind is None:
        return [finding(page, 1, f"no kind in its front matter; add 'kind: <one of {', '.join(KINDS)}>'; see {PAGE}")]
    line = front["kind"][1]
    if kind not in KINDS:
        return [finding(page, line, f"kind {kind!r} is not one of {', '.join(KINDS)}; see {PAGE}")]
    folder = next((f for f in FOLDERS if page.startswith(f + "/")), None)
    name = page.rsplit("/", 1)[-1].lower()
    if folder and name != "readme.md" and FOLDERS[folder] != kind:
        found.append(finding(page, line, f"is in {folder}/, whose pages are of kind {FOLDERS[folder]}, not {kind}; "
                                         f"see {PAGE}"))
    for key in REQUIRED.get(kind, ()):
        if key not in front:
            found.append(finding(page, 1, f"a {kind} needs '{key}' in its front matter; see {PAGE}"))
    status = front.get("status", (None, 1))[0]
    if kind in STATUS and status is not None and status not in STATUS[kind]:
        found.append(finding(page, front["status"][1], f"status {status!r} is not one of {', '.join(STATUS[kind])} "
                                                       f"for a {kind}; see {PAGE}"))
    if "proof" in front and front["proof"][0] not in ("proven", "unproven"):
        found.append(finding(page, front["proof"][1], f"proof is proven or unproven; see {PAGE}"))
    if "lane" in front and front["lane"][0] not in LANES:
        found.append(finding(page, front["lane"][1], f"lane {front['lane'][0]!r} is not one of {', '.join(LANES)}; "
                                                     f"see {PAGE}"))
    if "milestone" in front and not re.fullmatch(r"M[1-9][0-9]*", front["milestone"][0]):
        found.append(finding(page, front["milestone"][1], f"milestone is written M<n>, such as M3; see {PAGE}"))

    # The opening: title, purpose, In short, and Key points on a plan.
    lines = text.replace("\r\n", "\n").split("\n")
    blocks = _paragraphs(lines, skipped)
    if not blocks or not blocks[0][1][0].startswith("# "):
        return found + [finding(page, skipped + 1, f"opens without its title: the first line after the front "
                                                   f"matter is '# <title>'; see {PAGE}")]
    rest = blocks[1:]
    position = 0
    frozen = status in FROZEN.get(kind, ())
    first = rest[0] if rest else None
    opens_in_short = first is not None and IN_SHORT.match(first[1][0])
    if kind != "decision" or not opens_in_short:
        if first is None or first[1][0].startswith(("#", "|", "-", "*", ">", "```", "1.")) or opens_in_short:
            found.append(finding(page, blocks[0][0], f"has no purpose sentence under its title: say what the page "
                                                     f"is for and who reads it, in {WORDS} words or fewer; see {PAGE}"))
        else:
            words = len(_first_sentence(" ".join(first[1])).split())
            if words > WORDS and not frozen:
                found.append(finding(page, first[0], f"its purpose sentence has {words} words; the limit is {WORDS}; "
                                                     f"see {PAGE}"))
            position = 1
    after = rest[position] if len(rest) > position else None
    has_in_short = after is not None and IN_SHORT.match(after[1][0])
    anywhere = next((n for n, block in rest if IN_SHORT.match(block[0])), None)
    if kind not in NO_IN_SHORT and not has_in_short:
        found.append(finding(page, (after or blocks[0])[0], f"needs its **In short:** line right after the "
                                                            f"purpose sentence; see {PAGE}"))
    elif kind in NO_IN_SHORT and anywhere is not None and not has_in_short:
        found.append(finding(page, anywhere, f"its **In short:** line comes right after the purpose sentence; "
                                             f"see {PAGE}"))
    if kind == "plan":
        section = next((n for n, line in enumerate(lines, 1) if line.startswith("## ")), None)
        if section is None or lines[section - 1].strip() != "## Key points":
            found.append(finding(page, section or 1, f"a plan's first section is '## Key points'; see {PAGE}"))
    return found


def run(snapshot, config):
    today = datetime.date.fromisoformat(config["today"]) if config.get("today") \
        else datetime.datetime.now(datetime.timezone.utc).date()
    skip = config.get("skip", ())
    require_kind = config.get("require_kind", ["docs"])
    found, checked = [], 0
    try:
        proof = _load_proof_keys(snapshot, config.get("proof_keys", "evals/proofkeys.py"))
    except Exception as error:
        proof = None
        found.append(finding(config.get("proof_keys", "evals/proofkeys.py"), 1,
                             f"cannot be loaded ({type(error).__name__}: {error}), so no proof key was checked"))
    for page in snapshot.pages(skip=skip):
        text = snapshot.read(page)
        checked += 1
        if text is None:
            found.append(finding(page, 1, f"{snapshot.not_utf8(page)}, so its review date was not read; save it "
                                          f"as UTF-8"))
            continue
        front, skipped = _front(text)
        found += _date_findings(page, front, snapshot, config, today)
        if _under(page, require_kind):
            found += _kind_findings(page, text, front, skipped)
            if proof is not None:
                found += [finding(page, line, f"{message}; see docs/decisions/0006-what-proven-means.md")
                          for line, message in proof.problems(text)]
    if not checked:
        found.append(finding(".", 1, "checked no pages: every page is skipped, or the snapshot holds none; a check "
                                     f"that reads nothing passes everything; see {PAGE}"))
    return found
