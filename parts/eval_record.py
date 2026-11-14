"""Check: a playbook ships only with a passing eval run on record for its current wording.

Each eval case names the playbook it tests, the guidance files an agent is
given with it, and the scaffold folder the agent works in. evals/run.py stores a
record of the last run, with one hash over all of those and the case itself.
Edit any of them and the hash stops matching, so this check fails until the
case is run again and passes. A page's last-reviewed line is left out of the
hash: reviewing a page and moving its date does not change what an agent reads.

It trusts the record file: it shows that someone ran the case on this wording.
It cannot stop a person from editing the record by hand.

Config: "cases" (default evals/cases), "runs" (default evals/runs),
"playbooks": a folder in which every page must have a case (optional).
"""
import hashlib
import json
import re

from wslib.parts import finding

KIND = "check"


def guidance_hash(texts):
    """One hash over the case and every guidance file, in a fixed order. Line endings do not count."""
    digest = hashlib.sha256()
    for name in sorted(texts):
        text = re.sub(r"(?m)^last-reviewed\s*:.*\n", "", texts[name].replace("\r\n", "\n"))
        digest.update(name.encode("utf-8") + b"\0" + text.encode("utf-8") + b"\0")
    return digest.hexdigest()


def covered_files(case_path, case, paths=()):
    """The case, its playbook, its guidance, and every file in its scaffold folder. paths: all known file paths."""
    files = [case_path, case["playbook"]] + [g for g in case.get("guidance", []) if g != case["playbook"]]
    folder = case.get("scaffold_dir")
    if folder:
        files += [p for p in paths if p.startswith(folder.strip("/") + "/") and p not in files]
    return files


def run(snapshot, config):
    cases = config.get("cases", "evals/cases")
    runs = config.get("runs", "evals/runs")
    found, tested = [], set()

    for path in snapshot.paths(suffixes=(".json",), under=cases):
        try:
            case = json.loads(snapshot.read(path) or "")
            name, playbook = case["name"], case["playbook"]
            files = covered_files(path, case, list(snapshot.paths()))
            if not all(isinstance(f, str) for f in [name] + files):
                raise TypeError
        except (ValueError, KeyError, TypeError):
            found.append(finding(path, 1, "not a readable eval case with a name and a playbook"))
            continue
        tested.add(playbook)
        texts = {f: snapshot.read(f) if snapshot.is_file(f) else None for f in files}
        missing = [f for f, text in texts.items() if text is None]
        if missing:
            found.append(finding(path, 1, f"a file the case covers is missing: {missing[0]}"))
            continue

        record_path = f"{runs}/{name}/record.json"
        if not snapshot.is_file(record_path):
            found.append(finding(playbook, 1, f"no eval run on record for case {name}"))
            continue
        try:
            record = json.loads(snapshot.read(record_path) or "")
        except ValueError:
            record = None
        if not isinstance(record, dict):
            found.append(finding(record_path, 1, "not a readable eval record"))
        elif record.get("guidance_sha256") != guidance_hash(texts):
            found.append(finding(playbook, 1, f"it, its guidance or its case changed since the last recorded eval run; run case {name} again"))
        elif not isinstance(record.get("with_guidance"), dict) or record["with_guidance"].get("passed") is not True:
            found.append(finding(playbook, 1, f"its last recorded run of case {name} did not pass"))

    folder = config.get("playbooks")
    if folder:
        for page in snapshot.paths(suffixes=(".md",), under=folder):
            if page not in tested:
                found.append(finding(page, 1, "no eval case tests this playbook"))
    return found
