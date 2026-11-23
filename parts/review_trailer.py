"""Check: a commit that adds, changes or deletes a guidance page names the instruction review that covered it.

The commit message carries a trailer line, `Instructions-review: <record>`, naming a review record under
"folder" that the same commit adds or changes and whose `covers:` front matter lists every guidance page the
commit leaves in the tree. Or it carries `Instructions-review: skipped: <reason>`, with a reason from the
listed set: "link or typo only", "front matter only", "strike" or "as the kit wrote it". A commit may carry
several trailers. A skip reason excuses every guidance page no named record covers; a record named must still be
real.

"as the kit wrote it" is for an instance made from the kit: its first commit, and the commit of an upgrade, which
bring pages the kit's own reviews read (decision record 0007). It is checked against the commit's kit.lock.json:
each guidance page the commit leaves in the tree must match the hash that lock holds for it as synced or seeded,
and each page the commit deletes must be one that lock no longer holds. A page a record the commit names covers is
judged by that record instead, such as the README's proof table corrected in an upgrade's commit.

A guidance page is a path that matches "guidance" and not "except": patterns in the form direct_push uses (a
path ending in "/" is a folder and everything under it; "*" matches within one folder).

It judges a commit only once the commit's own tree uses this part, so commits made on a branch before the rule
reached it are not judged. A merge is judged by its own changes (its combined diff), not by what it brings in;
the commit-msg hook skips a merge, whose staged change is everything the other branch brings.

It runs in three places, all on commits the runner lists in the snapshot's `pushed`, each as
{"commit", "subject", "message", "paths", "files", "merge"}, where "files" answers `path in files` and
`files.get(path)` for the commit's tree:
  - the commit-msg hook (`ws.py check --message`), on the commit being made, its tree the staged files;
  - the pre-push hook (`ws.py check --push`), on every commit a push to main adds, read from the remote's tip;
  - CI (`ws.py check --commits BASE..HEAD`), on every commit of a pull request and of a push to main.

See docs/playbooks/instruction-review.md.
"""
import json
import re

from wslib import kitlock
from wslib import markdown
from wslib.parts import finding

KIND = "check"
PHASES = ("push",)
COMMIT_MESSAGE = True
PAGE = "docs/playbooks/instruction-review.md"
NAME = "review_trailer"
FOLDER = "docs/records/instruction-reviews"
TRAILER = re.compile(r"^Instructions-review:[ \t]*(.*?)[ \t]*$", re.I | re.M)
SKIP = re.compile(r"^skipped:[ \t]*(.*)$", re.I)
REASONS = ("link or typo only", "front matter only", "strike", "as the kit wrote it")
KIT = "as the kit wrote it"
COVERS = re.compile(r"^covers\s*:\s*(.*?)\s*$")


def _pattern(entry):
    if entry.endswith("/"):
        return re.compile(re.escape(entry) + ".*", re.S)
    return re.compile("[^/]*".join(re.escape(piece) for piece in entry.split("*")))


def _patterns(config, key):
    entries = config.get(key, [])
    if not isinstance(entries, list) or not all(isinstance(e, str) and e for e in entries):
        return None
    return [_pattern(entry) for entry in entries]


def trailers(message):
    """The values of every Instructions-review line, comment lines left out."""
    text = "\n".join(line for line in (message or "").replace("\r\n", "\n").split("\n") if not line.startswith("#"))
    return [value for value in TRAILER.findall(text)]


def covers(text):
    """The paths a record's `covers:` front matter lists, comma-separated."""
    rows, _ = markdown.split_front_matter(text or "")
    for row in rows:
        match = COVERS.match(row)
        if match:
            return {path.strip().strip("`") for path in match.group(1).split(",") if path.strip()}
    return set()


def ruled(files):
    """True unless the commit's own manifest exists and does not use this part."""
    text = files.get("workspace.json")
    if text is None:
        return True
    try:
        used = {entry.get("use") for entry in json.loads(text).get("parts", []) if isinstance(entry, dict)}
    except (ValueError, AttributeError):
        return True
    return NAME in used


def judge(commit, guidance, outside, folder):
    files = commit.get("files") or {}
    if commit.get("merge") or not ruled(files):
        return []
    paths = commit.get("paths", [])
    pages = [p for p in paths if any(g.fullmatch(p) for g in guidance) and not any(o.fullmatch(p) for o in outside)]
    if not pages:
        return []
    sha = (commit.get("commit") or "")[:7]
    name = f"commit {sha} \"{commit.get('subject', '')}\"" if sha else f"the commit \"{commit.get('subject', '')}\""
    more = f" and {len(pages) - 1} more" if len(pages) > 1 else ""
    values = trailers(commit.get("message", ""))
    if not values:
        return [finding(pages[0], 1, f"{name} changes the guidance page {pages[0]}{more} with no instruction review. "
                                     f"Run the review, then add the line 'Instructions-review: <record path>' to the "
                                     f"message, or 'Instructions-review: skipped: <reason>' with a reason from "
                                     f"{', '.join(REASONS)}; see {PAGE}")]
    found, covered, skipped, kit = [], set(), False, False
    for value in values:
        skip = SKIP.match(value)
        if skip:
            reason = skip.group(1).strip().lower()
            if reason == KIT:
                kit = skipped = True
            elif reason in REASONS:
                skipped = True
            else:
                found.append(finding(pages[0], 1, f"{name} skips the instruction review for {skip.group(1).strip()!r}, "
                                                  f"which is not a listed reason. Run the review, or give one of "
                                                  f"{', '.join(REASONS)}; see {PAGE}"))
            continue
        record = value.strip("`")
        if not record.startswith(folder.rstrip("/") + "/") or not record.endswith(".md") \
                or record.rsplit("/", 1)[-1].lower() == "readme.md":
            found.append(finding(pages[0], 1, f"{name} names {record!r}, which is not a review record in {folder}/. "
                                              f"Name the record the review wrote; see {PAGE}"))
        elif record not in files:
            found.append(finding(pages[0], 1, f"{name} names the review record {record}, which does not exist in the "
                                              f"commit. Commit the record with the pages it reviewed; see {PAGE}"))
        elif record not in paths:
            found.append(finding(pages[0], 1, f"{name} names the review record {record}, which it does not add or "
                                              f"change. A record is written for the change it reviews: run the review "
                                              f"on this change and commit its record with it; see {PAGE}"))
        else:
            covered |= covers(files.get(record))
    if kit and not found:
        found += _as_the_kit_wrote_it(name, [page for page in pages if page not in covered], files)
    if found or skipped:
        return found
    left = [page for page in pages if page in files and page not in covered]
    if left:
        more = f" and {len(left) - 1} more" if len(left) > 1 else ""
        found.append(finding(left[0], 1, f"{name} changes the guidance page {left[0]}{more}, which no review record "
                                         f"it names covers. Review it and list it in a record's covers line; see {PAGE}"))
    return found


def _as_the_kit_wrote_it(name, pages, files):
    """Findings for each guidance page the commit changes that is not as the commit's kit lock holds it."""
    if not pages:
        return []
    try:
        lock = json.loads(files.get(kitlock.LOCK) or "")
        entries = lock["files"]
        if not isinstance(entries, dict):
            raise TypeError
    except (ValueError, KeyError, TypeError, AttributeError):
        return [finding(pages[0], 1, f"{name} skips the instruction review as the kit wrote it, but the commit holds "
                                     f"no readable {kitlock.LOCK}. That reason is for an instance's first commit and "
                                     f"its upgrades; otherwise run the review; see {PAGE}")]
    found = []
    for page in pages:
        entry = entries.get(page) if isinstance(entries.get(page), dict) else {}
        held = entry.get("class") in ("synced", "seeded")
        text = files.get(page)
        if page not in files:
            if held or entry.get("class") == "kept":
                found.append(finding(page, 1, f"{name} deletes {page}, which {kitlock.LOCK} still holds, so the kit "
                                              f"did not delete it. Run the review; see {PAGE}"))
        elif not held or text is None or kitlock.digest(text) != entry.get("hash"):
            found.append(finding(page, 1, f"{name} skips the instruction review as the kit wrote it, but {page} is "
                                          f"not as {kitlock.LOCK} holds it, so the kit's reviews did not read this "
                                          f"text. Review it, and name the review's record in the same commit; see {PAGE}"))
    return found


def run(snapshot, config):
    guidance, outside = _patterns(config, "guidance"), _patterns(config, "except")
    if not guidance or outside is None:
        return [finding("workspace.json", 1, f"review_trailer needs \"guidance\", a list of paths, and \"except\" may "
                                             f"list paths; set them in the manifest; see {PAGE}")]
    folder = config.get("folder", FOLDER)
    found = []
    for commit in snapshot.pushed:
        found += judge(commit, guidance, outside, folder)
    return found
