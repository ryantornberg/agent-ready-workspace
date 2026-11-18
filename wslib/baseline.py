"""Baselines: the findings a check tolerates, so a team that adopts the workspace fails only on new ones.

Each check may have one file, baselines/<check>.json, read from the snapshot being checked: the staged file at the
commit, the folder's file in CI. So the commit and CI decide the same way. A missing file tolerates nothing.

    {"tolerated": [{"fingerprint": "3f9c0d1e2a4b5c6d", "path": "docs/a.md", "message": "link to missing file: b.md"}]}

A fingerprint is a hash of the check's name, the finding's path and its message, not its line, so a finding that
only moves stays tolerated. Each entry tolerates one finding: a second copy of the same finding fails. Only the
fingerprint is compared; the path and message are there for the person reading the file. Only errors are recorded,
since a warning fails nothing. A file that cannot be read tolerates nothing and is reported as an error.

The files are machinery: they change through a pull request, like the checks they weaken.
`python3 ws.py baseline` writes them from the folder's current findings.
"""
import collections
import hashlib
import json
import re

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


def apply(snapshot, check, findings):
    """(findings that still count, how many were tolerated, a finding about the file or None)."""
    left, problem = read(snapshot, check)
    kept, tolerated = [], 0
    for found in findings:
        mark = fingerprint(check, found)
        if found["level"] == "error" and left[mark] > 0:
            left[mark] -= 1
            tolerated += 1
        else:
            kept.append(found)
    trouble = {"path": path_of(check), "line": 1, "message": problem, "level": "error"} if problem else None
    return kept, tolerated, trouble
