"""Baselines: the findings a check tolerates, so a team that adopts the workspace fails only on new ones.

Each check may have one file, baselines/<check>.json, read from the snapshot being checked: the staged file at the
commit, the folder's file in CI. A missing file tolerates nothing.

An entry tolerates a finding only when the base has that finding too: the last commit, for the folder and commit
checks, or the merge base with the commit `check --changed-from` names, in CI. So a change can excuse a finding its
base already has, never one it brings, even by adding the entry in the same change or ahead of the finding. With no
base to compare with, nothing is tolerated. The commit and CI apply the same rule. The check runs a second time,
on the base, only when its baseline lists something.

    {"tolerated": [{"fingerprint": "3f9c0d1e2a4b5c6d", "path": "docs/a.md", "message": "link to missing file: b.md"}]}

A fingerprint is a hash of the check's name, the finding's path and its message, not its line, so a finding that
only moves stays tolerated. Each entry tolerates one finding: a second copy of the same finding fails. Only the
fingerprint is compared; the path and message are there for the person reading the file. Only errors are recorded,
since a warning fails nothing. A file that cannot be read tolerates nothing and is reported as an error.

The files are machinery: they change through a pull request, like the checks they weaken. A check that judges only
the lines a change adds, such as line_cites, finds nothing at a base, so its findings cannot be tolerated.
`python3 ws.py baseline` writes them from the folder's current findings.
"""
import collections
import hashlib
import json
import re

from . import snapshot as snapshots

FOLDER = "baselines"
FINGERPRINT = re.compile(r"^[0-9a-f]{16}$")


def path_of(check):
    return f"{FOLDER}/{check}.json"


def fingerprint(check, found):
    text = "\0".join((check, str(found["path"]), str(found["message"])))
    return hashlib.sha256(text.encode("utf-8", "surrogateescape")).hexdigest()[:16]


def record(check, findings):
    """The baseline file's content that tolerates every error in findings."""
    tolerated = [{"fingerprint": fingerprint(check, found), "path": found["path"], "message": found["message"]}
                 for found in findings if found["level"] == "error"]
    return {"tolerated": sorted(tolerated, key=lambda entry: (entry["path"], entry["message"]))}


def read(snapshot, check):
    """(Counter of tolerated fingerprints, problem or None). A missing file is an empty baseline."""
    path = path_of(check)
    if not snapshot.is_file(path):
        return collections.Counter(), None
    text = snapshot.read(path)
    try:
        body = json.loads(text) if text is not None else None
    except ValueError:
        body = None
    entries = body.get("tolerated") if isinstance(body, dict) else None
    if not isinstance(entries, list) or not all(
            isinstance(entry, dict) and isinstance(entry.get("fingerprint"), str)
            and FINGERPRINT.match(entry["fingerprint"]) for entry in entries):
        return collections.Counter(), (f"cannot be read as a baseline: it needs a \"tolerated\" list of entries, "
                                       f"each with a 16-character fingerprint, so every finding of {check} counts")
    return collections.Counter(entry["fingerprint"] for entry in entries), None


def at_commit(root, ref, changed=()):
    """A snapshot of the files a commit holds, read in one git batch; None when git cannot list them."""
    try:
        listed = snapshots._git(root, "ls-tree", "-r", "-z", ref)
    except RuntimeError:
        return None
    blobs, links = {}, []
    for entry in snapshots._names(listed):
        meta, _, path = entry.partition("\t")
        mode, kind, oid = meta.split()
        if kind != "blob":
            continue                              # a pinned repository's commit holds no files here
        blobs[path] = oid
        if mode == snapshots.LINK:
            links.append(path)
    try:
        output = snapshots._git(root, "cat-file", "--batch", data="".join(f"{oid}\n" for oid in blobs.values()).encode())
    except RuntimeError:
        return None
    files, at = {}, 0
    for path in blobs:
        end = output.index(b"\n", at)
        size = int(output[at:end].rsplit(b" ", 1)[1])
        files[path] = output[end + 1:end + 1 + size]
        at = end + 1 + size + 1
    return snapshots.Memory(files, changed=changed, links=links)


def apply(snapshot, check, findings, at_base):
    """(findings that still count, how many were tolerated, findings about the baseline itself).

    at_base: a function that returns the check's findings at the base, or None when there is no base. It is called
    only when the baseline lists something."""
    entries, problem = read(snapshot, check)
    notes = [{"path": path_of(check), "line": 1, "message": problem, "level": "error"}] if problem else []
    base = None
    if entries:
        found_at_base = at_base()
        if found_at_base is None:
            notes.append({"path": path_of(check), "line": 1, "level": "warning",
                          "message": "there is no base commit to compare with, or the check cannot run there, so this baseline tolerates nothing"})
        else:
            base = collections.Counter(fingerprint(check, found) for found in found_at_base if found["level"] == "error")
    left = collections.Counter() if base is None else entries & base   # only what the base has too
    kept, tolerated, brought = [], 0, 0
    for found in findings:
        mark = fingerprint(check, found)
        if found["level"] == "error" and left[mark] > 0:
            left[mark] -= 1
            tolerated += 1
        else:
            if found["level"] == "error" and entries[mark] > 0 and base is not None:
                brought += 1
            kept.append(found)
    if brought:
        notes.append({"path": path_of(check), "line": 1, "level": "warning",
                      "message": f"{brought} finding(s) it lists are not tolerated, because the base does not have "
                                 f"them: a change cannot excuse a finding it brings"})
    return kept, tolerated, notes
