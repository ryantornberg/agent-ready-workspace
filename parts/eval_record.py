"""Check: a playbook ships only while a recorded eval run shows its guidance beating the bare model.

Each eval case names the playbook it tests, the scaffold folder the agent works
in, and a hidden acceptance test. The arms file next to the cases folder
(evals/arms.json) names what each arm of the eval is given: the guided arm gets
the real contract, the index, the playbook and the definition of done. evals/run.py
stores a record of the last run of each case, with one hash over everything an
agent or a grade depends on: the case, the arms file and every file it names,
the scaffold, the acceptance test, the harness itself (run.py and grade.py), and
the code of every workspace hook a grader runs, with the loader that runs it.
Edit any of them and the hash stops matching, so this check fails until the
case is run again. A page's review date is left out of the hash, but only in its
front matter: a line that starts "last-reviewed:" in a page's body is text an agent reads.

A run counts when it passes every grader of its case. A record passes when every
arm has five or more runs, and the guided arm has more such runs than the bare
arm. A playbook the bare model follows just as well fails here, because it no
longer earns its place. Pooled across the records that pass, the guided arm must
also beat the two-line arm, by a one-sided Fisher exact test at p < 0.05: guidance
that two lines would match fails too.

It trusts the record file: it shows that someone ran the case on this wording.
It cannot stop a person from editing the record by hand. CI re-grades every
stored transcript against its record (evals/grade.py --recorded).

Config: "cases" (default evals/cases), "runs" (default evals/runs),
"playbooks": a folder in which every page must have a case (optional).
The arms file and the harness are found next to the cases folder, not set here,
so a manifest edit cannot take them out of the hash.
"""
import hashlib
import json
import math
import posixpath
import re

from wslib.parts import finding

KIND = "check"
HARNESS = ("run.py", "grade.py")
ARMS = "arms.json"
MIN_RUNS = 5
LOADER = "wslib/parts.py"   # what a hook_allows grader loads a hook through
POOLED_P = 0.05
FRONT_MATTER = re.compile(r"\A---\n.*?\n---\n", re.S)


def _without_review_date(text):
    """The text with the last-reviewed line of its front matter removed, and nothing else."""
    text = text.replace("\r\n", "\n")
    head = FRONT_MATTER.match(text)
    if not head:
        return text
    return re.sub(r"(?m)^last-reviewed\s*:.*\n", "", head.group(0)) + text[head.end():]


def guidance_hash(texts):
    """One hash over the case and every file it covers, in a fixed order. Line endings do not count."""
    digest = hashlib.sha256()
    for name in sorted(texts):
        digest.update(name.encode("utf-8") + b"\0" + _without_review_date(texts[name]).encode("utf-8") + b"\0")
    return digest.hexdigest()


def evals_folder(cases):
    return posixpath.dirname(cases.strip("/")) or "."


def _join(folder, name):
    return name if folder == "." else f"{folder}/{name}"


def arm_sources(arms):
    """Every file the arms file says to give an agent, as {arm: {destination: source}}."""
    if not isinstance(arms, dict) or not arms:
        raise TypeError
    found = {}
    for arm, spec in arms.items():
        files = spec.get("files") if isinstance(spec, dict) else None
        if not isinstance(files, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in files.items()):
            raise TypeError
        found[arm] = files
    return found


def covered_files(case_path, case, paths=(), arms=None, folder="evals"):
    """Everything a run of the case depends on. paths: all known file paths. arms: the parsed arms file."""
    files = [case_path, case["playbook"], _join(folder, ARMS)] + [_join(folder, name) for name in HARNESS]
    for given in arm_sources(arms or {}).values() if arms is not None else ():
        files += sorted(given.values())
    if case.get("acceptance"):
        files.append(case["acceptance"])
    hooks = sorted({g.get("hook") for g in case.get("graders", []) if isinstance(g, dict) and g.get("type") == "hook_allows"})
    for hook in hooks:
        files += [f"parts/{hook}.py", LOADER]
    scaffold = case.get("scaffold_dir")
    if scaffold:
        files += sorted(p for p in paths if p.startswith(scaffold.strip("/") + "/"))
    unique = []
    for name in files:
        if name not in unique:
            unique.append(name)
    return unique


def passing(runs, grader_ids):
    """How many runs pass every grader of the case."""
    return sum(1 for run in runs if all(run.get("graders", {}).get(g) is True for g in grader_ids))


def fisher_greater(a, n1, b, n2):
    """One-sided Fisher exact p: the chance of a or more passes in the first group, if both groups share one rate."""
    passes, total = a + b, n1 + n2
    tail = sum(math.comb(passes, k) * math.comb(total - passes, n1 - k) for k in range(a, min(passes, n1) + 1))
    return tail / math.comb(total, n1)


def judge(record, arm_names, grader_ids):
    """Why a record whose hash matches still does not pass, or None."""
    given = record.get("arms")
    if not isinstance(given, dict):
        return "it holds no arms"
    for arm in arm_names:
        runs = given.get(arm, {}).get("runs") if isinstance(given.get(arm), dict) else None
        if not isinstance(runs, list) or len(runs) < MIN_RUNS:
            return f"the {arm} arm has {len(runs) if isinstance(runs, list) else 0} runs; it needs {MIN_RUNS} or more"
    if "guided" not in given or "bare" not in given:
        return "it needs a guided arm and a bare arm to compare"
    guided, bare = (passing(given[arm]["runs"], grader_ids) for arm in ("guided", "bare"))
    if guided <= bare:
        return (f"the guided arm passes every grader in no more runs than the bare arm ({guided} against {bare}), "
                f"so the guidance does not earn its place")
    return None


def pooled(records):
    """Why the records, pooled, do not show the guided arm beating the two-line arm, or None.
    records: [(record, grader ids)], each a record that passes judge()."""
    if not records:
        return None
    if not all("two-line" in record["arms"] for record, _ in records):
        return "the pooled comparison needs a two-line arm in every record"
    counts = {arm: [0, 0] for arm in ("guided", "two-line")}
    for record, grader_ids in records:
        for arm in counts:
            runs = record["arms"][arm]["runs"]
            counts[arm][0] += passing(runs, grader_ids)
            counts[arm][1] += len(runs)
    (a, n1), (b, n2) = counts["guided"], counts["two-line"]
    p = fisher_greater(a, n1, b, n2)
    if p < POOLED_P:
        return None
    return (f"pooled across {len(records)} case(s), the guided arm passes every grader in {a} of {n1} runs and the "
            f"two-line arm in {b} of {n2}: one-sided Fisher exact p = {p:.2g}, not below {POOLED_P}, so two lines "
            f"would do as well")


def run(snapshot, config):
    cases = config.get("cases", "evals/cases")
    runs = config.get("runs", "evals/runs")
    folder = evals_folder(cases)
    arms_path = _join(folder, ARMS)
    found, tested, standing = [], set(), []
    case_paths = list(snapshot.paths(suffixes=(".json",), under=cases))

    arms = None
    if case_paths:
        try:
            arms = json.loads(snapshot.read(arms_path) or "")
            arm_sources(arms)
        except (ValueError, TypeError, AttributeError):
            found.append(finding(arms_path, 1, "not a readable arms file: each arm needs \"files\", "
                                               "a map of where each file goes to where it comes from"))
            return found

    for path in case_paths:
        try:
            case = json.loads(snapshot.read(path) or "")
            name, playbook = case["name"], case["playbook"]
            files = covered_files(path, case, list(snapshot.paths()), arms, folder)
            grader_ids = [g["id"] for g in case.get("graders", [])]
            if not all(isinstance(f, str) for f in [name] + files + grader_ids):
                raise TypeError
        except (ValueError, KeyError, TypeError, AttributeError):
            found.append(finding(path, 1, "not a readable eval case with a name and a playbook"))
            continue
        tested.add(playbook)
        missing = [f for f in files if not snapshot.is_file(f)]
        if missing:
            found.append(finding(path, 1, f"a file the case covers is missing: {missing[0]}"))
            continue
        texts = {f: snapshot.read(f) for f in files}
        unreadable = [f for f, text in texts.items() if text is None]
        if unreadable:
            found.append(finding(path, 1, f"a file the case covers {snapshot.not_utf8(unreadable[0])}, so the case "
                                          f"cannot be hashed: {unreadable[0]}"))
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
            found.append(finding(playbook, 1, f"it, its guidance, its case or the eval harness changed since the last "
                                              f"recorded eval run; run case {name} again"))
        else:
            try:
                problem = judge(record, list(arms), grader_ids)
            except (AttributeError, TypeError, ZeroDivisionError):
                problem = "its runs are not readable"
            if problem:
                found.append(finding(playbook, 1, f"its last recorded run of case {name} does not pass: {problem}"))
            else:
                standing.append((record, grader_ids))

    try:
        problem = pooled(standing)
    except (AttributeError, TypeError, KeyError):
        problem = "the records' runs are not readable"
    if problem:
        found.append(finding(arms_path, 1, problem))

    playbooks = config.get("playbooks")
    if playbooks:
        for page in snapshot.paths(suffixes=(".md",), under=playbooks):
            if page not in tested:
                found.append(finding(page, 1, "no eval case tests this playbook"))
    return found
