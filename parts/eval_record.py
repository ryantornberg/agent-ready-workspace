"""Check: a playbook ships only with a passing eval run on record for its current wording.

Each eval case names the playbook it tests. evals/run.py stores a record of the
last run, with a hash of the playbook as it was. Edit the playbook and the hash
stops matching, so this check fails until the case is run again and passes.

Config: "cases" (default evals/cases), "runs" (default evals/runs).
"""
import hashlib
import json

from wslib.parts import finding

KIND = "check"


def playbook_hash(text):
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def run(snapshot, config):
    cases = config.get("cases", "evals/cases")
    runs = config.get("runs", "evals/runs")
    found = []
    for path in snapshot.paths(suffixes=(".json",), under=cases):
        try:
            case = json.loads(snapshot.read(path) or "")
            name, playbook = case["name"], case["playbook"]
        except (ValueError, KeyError, TypeError):
            found.append(finding(path, 1, "not a readable eval case with a name and a playbook"))
            continue
        text = snapshot.read(playbook) if snapshot.is_file(playbook) else None
        if text is None:
            found.append(finding(path, 1, f"its playbook is missing: {playbook}"))
            continue

        record_path = f"{runs}/{name}/record.json"
        try:
            record = json.loads(snapshot.read(record_path) or "") if snapshot.is_file(record_path) else None
        except ValueError:
            record = {}
        if record is None:
            found.append(finding(playbook, 1, f"no eval run on record for case {name}"))
        elif record.get("playbook_sha256") != playbook_hash(text):
            found.append(finding(playbook, 1, f"changed since its last recorded eval run; run case {name} again"))
        elif not record.get("with_playbook", {}).get("passed"):
            found.append(finding(playbook, 1, f"its last recorded run of case {name} did not pass"))
    return found
