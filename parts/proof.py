"""Check: every proof mark holds, and none moves without the record decision record 0006 asks for.

A playbook or how-to says in its front matter whether it is proven (decision record 0006, docs/layout.md);
a section merged into another page says so in a line under its heading. This check holds those marks:

  - an unproven page or section names its milestone in prove-by; a proven one names its evidence in proven-by
    and no prove-by;
  - every proven-by item exists: a bare path in the workspace, or <sha>:<path> at a full 40-hex sha that is an
    ancestor of the commit being checked; and at least one item is a real-run record, not an eval record;
  - an unproven page fails once its prove-by milestone's record (docs/milestones/m<n>.md) is signed off;
  - against the base commit: a prove-by newly set to a milestone being built fails; a prove-by moved later
    fails unless a failed proof attempt is on record for the milestone it moves away from, under evals/runs/,
    added while that milestone was being built; a renamed page whose proof keys change fails; an existing
    anchor changed, or a proven page or section marked unproven again, fails unless an approved entry in
    "Changes after approval" of a plan whose milestone is being built says so, in a line
    "Anchor: <page> <old item> -> <new item>" or "Demote: <page>";
  - the README's table of proven and unproven pages matches the pages.

"Being built" is the manifest's "building" list. With no base commit, as in a plain `check`, the comparisons
with the base are skipped. Config: "folders" (default ["docs"]), "milestones" (docs/milestones), "plans"
(docs/plans), "readme" (README.md), "heading" (the README's heading over the table), "runs" (evals/runs),
"proof_keys" (evals/proofkeys.py).
"""
import json
import re
import types

from wslib import markdown
from wslib.parts import finding

KIND = "check"
PAGE = "docs/decisions/0006-what-proven-means.md"
ENTRY = re.compile(r"^### \d{4}-\d{2}-\d{2}\b")
APPROVED = re.compile(r"^Approved by: \S.*, \d{4}-\d{2}-\d{2}\s*$")


def _load(snapshot, path):
    module = types.ModuleType("proof_check_keys")
    exec(compile(snapshot.read(path) or "", path, "exec"), module.__dict__)
    return module


def _slug(heading):
    return re.sub(r"[^\w\- ]", "", heading.lower()).strip().replace(" ", "-")


def marks(keys, text):
    """{key: (state, prove_by, proven_by items)} for the page ("") and each marked section ("#slug")."""
    if text is None:
        return {}
    front, sections = keys.keys(text)
    found = {}
    if "proof" in front:
        items = keys.parse_list(front["proven-by"]) if front.get("proven-by") else []
        found[""] = (front["proof"], front.get("prove-by"), items)
    for heading, line in sections:
        state, value = keys.parse_section(line)
        found["#" + _slug(heading)] = (state, value if state == "unproven" else None,
                                       keys.parse_list(value) if state == "proven" else [])
    return found


def _number(milestone):
    return int(milestone[1:]) if milestone and re.fullmatch(r"M[1-9][0-9]*", milestone) else None


def _item(sha, path):
    return f"{sha}:{path}" if sha else path


def approvals(snapshot, plans, building, keys):
    """The Anchor and Demote lines of approved entries in plans whose milestone is being built."""
    lines = set()
    for plan in snapshot.paths(suffixes=(".md",), under=plans):
        text = snapshot.read(plan) or ""
        front = {}
        for row in markdown.split_front_matter(text)[0]:
            key, _, value = row.partition(":")
            front[key.strip()] = value.strip()
        if front.get("milestone") not in building:
            continue
        inside, entry, approved = False, False, False
        rows = text.replace("\r\n", "\n").split("\n")
        for index, row in enumerate(rows):
            if row.startswith("## "):
                inside, entry = row.strip() == "## Changes after approval", False
                continue
            if not inside:
                continue
            if ENTRY.match(row):
                following = next((r for r in rows[index + 1:] if r.strip()), "")
                entry, approved = True, bool(APPROVED.match(following))
                continue
            if entry and approved and row.startswith(("Anchor: ", "Demote: ")):
                lines.add(row.strip())
    return lines


def failed_attempts(snapshot, runs):
    """[(page, milestone, path)] of the failed proof attempts on record under the runs folder."""
    found = []
    for path in snapshot.paths(suffixes=(".json",), under=runs):
        try:
            record = json.loads(snapshot.read(path) or "")
        except ValueError:
            continue
        if isinstance(record, dict) and record.get("verdict") == "not proven" and record.get("page") \
                and record.get("milestone"):
            found.append((record["page"], record["milestone"], path))
    return found


def run(snapshot, config):
    keys_path = config.get("proof_keys", "evals/proofkeys.py")
    if not snapshot.is_file(keys_path):
        return [finding(keys_path, 1, f"missing, so no proof mark can be read; see {PAGE}")]
    try:
        keys = _load(snapshot, keys_path)
    except Exception as error:
        return [finding(keys_path, 1, f"cannot be loaded ({type(error).__name__}: {error}); see {PAGE}")]
    try:
        building = json.loads(snapshot.read("workspace.json") or "").get("building", [])
    except (ValueError, AttributeError):
        building = []
    folders = config.get("folders", ["docs"])
    milestones, plans = config.get("milestones", "docs/milestones"), config.get("plans", "docs/plans")
    runs = config.get("runs", "evals/runs")
    found, all_marks = [], {}
    approved, attempts = None, None
    pages = [page for page in snapshot.pages(skip=config.get("skip", ("evals/scaffold", "archive")))
             if any(page.startswith(f.rstrip("/") + "/") for f in folders)]
    anchors = []
    for page in pages:
        for _, _, items in marks(keys, snapshot.read(page)).values():
            anchors += [(sha, path) for sha, path in items if sha]
    if snapshot.has_base():
        snapshot.prefetch_history([snapshot.base_path(page) for page in pages], anchors)
    else:
        snapshot.prefetch_history((), anchors)

    for page in pages:
        current = marks(keys, snapshot.read(page))
        for key, (state, prove_by, items) in current.items():
            name = page + key
            all_marks[name] = state
            if state == "unproven":
                if not prove_by:
                    found.append(finding(page, 1, f"{name} is unproven and names no prove-by milestone; see {PAGE}"))
                    continue
                record = f"{milestones}/m{prove_by[1:]}.md"
                text = snapshot.read(record) if snapshot.is_file(record) else None
                if text and re.search(r"(?m)^status:\s*signed off\s*$", "\n".join(markdown.split_front_matter(text)[0])):
                    found.append(finding(page, 1, f"{name} is still unproven, but {prove_by}, its prove-by milestone, "
                                                  f"is signed off ({record}). Prove it, cut it, or move prove-by later "
                                                  f"with a failed attempt on record; see {PAGE}"))
            elif state == "proven":
                if prove_by:
                    found.append(finding(page, 1, f"{name} is proven and still names prove-by; remove it"))
                if not items:
                    found.append(finding(page, 1, f"{name} is proven but names no evidence in proven-by; see {PAGE}"))
                if items and all(path.startswith(runs + "/") for _, path in items):
                    found.append(finding(page, 1, f"{name} is proven but its proven-by names no real-run record, "
                                                  f"only eval records; add the record of the real run; see {PAGE}"))
                for sha, path in items:
                    if sha is None and not snapshot.is_file(path):
                        found.append(finding(page, 1, f"{name}: proven-by names {path}, which does not exist"))
                    elif sha is not None and not snapshot.is_ancestor(sha):
                        found.append(finding(page, 1, f"{name}: the anchor {sha[:12]} is not a commit in this history; "
                                                      f"an anchor's commit must be reachable from main; see {PAGE}"))
                    elif sha is not None and snapshot.commit_text(sha, path) is None:
                        found.append(finding(page, 1, f"{name}: the anchor {sha[:12]}:{path} cannot be read"))

        if not snapshot.has_base():
            continue
        before_path = snapshot.base_path(page)
        before = marks(keys, snapshot.base_text(before_path))
        if before_path != page and before != current and before:
            found.append(finding(page, 1, f"renamed from {before_path} with its proof keys changed; rename it in one "
                                          f"commit and change its proof keys in another; see {PAGE}"))
            continue
        for key, (state, prove_by, items) in current.items():
            name = page + key
            old = before.get(key)
            if state == "unproven" and prove_by in building and (old is None or old[1] != prove_by):
                found.append(finding(page, 1, f"{name}: prove-by is newly set to {prove_by}, a milestone being built "
                                              f"now; name the milestone whose work will run it; see {PAGE}"))
            if state == "unproven" and old and old[0] == "unproven" and old[1] and prove_by and \
                    (_number(prove_by) or 0) > (_number(old[1]) or 0):
                attempts = failed_attempts(snapshot, runs) if attempts is None else attempts
                licensed = [p for page_named, milestone, p in attempts if page_named == name and milestone == old[1]
                            and old[1] in snapshot.building_when_added(p)]
                if not licensed:
                    found.append(finding(page, 1, f"{name}: prove-by moves from {old[1]} to {prove_by} with no failed "
                                                  f"proof attempt on record for {old[1]}, made while {old[1]} was being "
                                                  f"built; see {PAGE}"))
            if old and old[0] == "proven":
                approved = approvals(snapshot, plans, building, keys) if approved is None else approved
                if state != "proven" and f"Demote: {name}" not in approved:
                    found.append(finding(page, 1, f"{name} was proven and is marked {state} now, which takes it out of "
                                                  f"the eval gate; that needs a line 'Demote: {name}' in an approved "
                                                  f"change entry of the plan being built; see {PAGE}"))
                if state == "proven":
                    new_items = {_item(*i) for i in items if i[0]}
                    for sha, path in old[2]:
                        if sha is None or _item(sha, path) in new_items:
                            continue
                        moved = [line for line in approved if line.startswith(f"Anchor: {name} {_item(sha, path)} -> ")
                                 and line.split(" -> ", 1)[1] in new_items]
                        if not moved:
                            found.append(finding(page, 1, f"{name}: the anchor {sha[:12]}:{path} was changed or removed "
                                                          f"with no line 'Anchor: {name} <old> -> <new>' in an approved "
                                                          f"change entry of the plan being built; see {PAGE}"))
        for key, old in before.items():
            if key not in current and old[0] == "proven":
                approved = approvals(snapshot, plans, building, keys) if approved is None else approved
                if f"Demote: {page + key}" not in approved:
                    found.append(finding(page, 1, f"{page + key} was proven and lost its proof mark, which takes it out "
                                                  f"of the eval gate; that needs a line 'Demote: {page + key}' in an "
                                                  f"approved change entry of the plan being built; see {PAGE}"))

    readme = config.get("readme", "README.md")
    heading = config.get("heading", "Proven and unproven pages")
    if snapshot.is_file(readme):
        table = _readme_table(snapshot.read(readme) or "", heading)
        if table is None:
            found.append(finding(readme, 1, f"has no table under '## {heading}'; list every marked page with its "
                                            f"state; see {PAGE}"))
        else:
            for name, state in sorted(all_marks.items()):
                if table.get(name) != state:
                    found.append(finding(readme, 1, f"its table says {table.get(name) or 'nothing'} for {name}, "
                                                    f"which is marked {state}; correct the row"))
            for name in sorted(set(table) - set(all_marks)):
                found.append(finding(readme, 1, f"its table lists {name}, which carries no proof mark"))
    return found


def _readme_table(text, heading):
    """{page or page#section: state} of the table under the heading, or None when there is none."""
    rows, inside, seen = {}, False, False
    for line in text.replace("\r\n", "\n").split("\n"):
        if line.startswith("#"):
            inside = line.lstrip("#").strip() == heading
            continue
        if not inside or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        link = re.search(r"\]\(([^)\s]+)\)", cells[0]) if cells else None
        if link and len(cells) > 1:
            seen = True
            rows[link.group(1)] = cells[1].split()[0].strip("*").lower() if cells[1].split() else ""
        elif len(cells) > 1 and set(cells[0]) <= set("-: "):
            seen = True
    return rows if seen else None
