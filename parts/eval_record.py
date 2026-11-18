"""Check: a playbook marked proven stays only while a recorded eval run shows its guidance beating the bare model.

Each eval case names the playbook it tests (a page, or page#section for a section merged into another page),
the scaffold folder the agent works in, and a hidden acceptance test. What each arm of the eval is given
comes from the arms file next to the cases folder (evals/arms.json), or from the case itself:

  "arms"       the case's own arm files, {arm: {"files": {destination: source}}}. They replace the shared
               arms file for this case, and only this case's hash covers them, so the case depends on no
               shared arm file.
  "add_files"  files added to a shared arm for this case only, {arm: {destination: source}}, such as the rule
               pages whose paths the case's code touches. Hashed into this case only.

evals/run.py stores a record of the last run of each case, with one hash over everything an agent or a grade
depends on: the case, the arm files, the scaffold, the acceptance test, the harness itself (run.py, grade.py
and proofkeys.py), the code of every workspace hook a grader runs, and the shell parser those hooks share
(wslib/shell.py). Edit any of them and the hash stops matching, so this check fails until the case is run
again. Two kinds of text are left out of the hash: a page's review date in its front matter, and the proof
keys of decision record 0006 (proof, prove-by, proven-by and a section's proof line) in their exact forms.
The runner takes the same keys out of every page a gated arm reads, through the same function, which lives
in evals/proofkeys.py; this check loads that file from the snapshot's text, so the text that is hashed is
exactly the text tested. So marking a page proven does not stale the record that proved it, while any other
spelling of those keys is hashed (and page_kinds fails it).

A run counts when it passes every grader of its case. A record passes when every arm has five or more runs,
and the guided arm passes more often than the bare arm. An arm may hold twice the record's runs per arm when
it was recorded once more after missing a margin ("rerecorded"); arms of different sizes are compared by
their pass rates. A baseline record (run.py --baseline) and a one-time arm's record never count as passing.

Only pages marked proven are gated here. For each one, pooled across its cases, every arm needs 40 or more
runs, and the guided arm must beat the two-line arm by a one-sided Fisher exact test at p < 0.05. A proven
playbook the bare model follows just as well fails, and so does guidance that two lines would match. Then the
guided arm is held to its own past: pooled over the cases present in both records, it may not pass more than
3 runs fewer than the previous record's guided arm (the record at the base commit), nor than the guided arm
of the record the page's proven-by names as its anchor, <sha>:evals/runs/<case>/record.json. Both sides are
put on the larger side's scale, and the margin is 6 when either side was recorded once more, else 3. With no
base commit, as in a plain `check` or a scheduled CI run, those two comparisons are skipped, and a warning
says so.

It trusts the record file: it shows that someone ran the case on this wording. CI re-grades every stored
transcript against its record (evals/grade.py --recorded).

Config: "cases" (default evals/cases), "runs" (default evals/runs), "playbooks": a folder in which every page
marked proven must have a case (optional). The arms file and the harness are found next to the cases folder,
not set here, so a manifest edit cannot take them out of the hash.
"""
import hashlib
import json
import math
import posixpath
import re
import types

from wslib.parts import finding

KIND = "check"
HARNESS = ("run.py", "grade.py", "proofkeys.py")
PROOF_KEYS = "proofkeys.py"
ARMS = "arms.json"
SHELL = "wslib/shell.py"
REQUIRED_ARMS = ("guided", "two-line", "bare")
MIN_RUNS = 5
POOLED_P = 0.05
POOLED_MIN_RUNS = 40
MARGIN, POOLED_MARGIN = 3, 6
PAGE = "evals/README.md#the-gate"
FRONT_MATTER = re.compile(r"\A---\n.*?\n---\n", re.S)


def _without_review_date(text):
    """The text with the last-reviewed line of its front matter removed, and nothing else."""
    text = text.replace("\r\n", "\n")
    head = FRONT_MATTER.match(text)
    if not head:
        return text
    return re.sub(r"(?m)^last-reviewed\s*:.*\n", "", head.group(0)) + text[head.end():]


def guidance_hash(texts, strip):
    """One hash over the case and every file it covers, in a fixed order. Line endings, a page's review date and
    its exact proof keys do not count. strip: proofkeys.strip, from the harness file the hash covers."""
    digest = hashlib.sha256()
    for name in sorted(texts):
        text = _without_review_date(texts[name])
        if name.lower().endswith(".md"):
            text = strip(text)
        digest.update(name.encode("utf-8") + b"\0" + text.encode("utf-8") + b"\0")
    return digest.hexdigest()


def load_proof_keys(text, where):
    """evals/proofkeys.py as a module, from its text: the same file the harness imports and the hash covers."""
    module = types.ModuleType("eval_proof_keys")
    exec(compile(text, where, "exec"), module.__dict__)
    for name in ("strip", "keys", "problems", "parse_list", "parse_section"):
        if not callable(module.__dict__.get(name)):
            raise TypeError(f"{where} has no {name} function")
    return module


def evals_folder(cases):
    return posixpath.dirname(cases.strip("/")) or "."


def _join(folder, name):
    return name if folder == "." else f"{folder}/{name}"


def page_of(playbook):
    """The page a case's playbook names, without its #section."""
    return playbook.split("#", 1)[0]


def _files_map(value):
    if not isinstance(value, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in value.items()):
        raise TypeError
    return value


def arm_sources(arms):
    """Every file an arms definition says to give an agent, as {arm: {destination: source}}."""
    if not isinstance(arms, dict) or not arms:
        raise TypeError
    return {arm: _files_map(spec.get("files") if isinstance(spec, dict) else None) for arm, spec in arms.items()}


def case_arms(case, shared):
    """{arm: {destination: source}} for one case: its own arms, or the shared arms with its additions."""
    if "arms" in case:
        return arm_sources(case["arms"])
    found = {arm: dict(files) for arm, files in arm_sources(shared or {}).items()}
    extra = case.get("add_files", {})
    if not isinstance(extra, dict):
        raise TypeError
    for arm, files in extra.items():
        if arm not in found:
            raise TypeError
        found[arm].update(_files_map(files))
    return found


def covered_files(case_path, case, paths=(), arms=None, folder="evals"):
    """Everything a run of the case depends on. paths: all known file paths. arms: the parsed shared arms file."""
    files = [case_path, page_of(case["playbook"])] + [_join(folder, name) for name in HARNESS]
    if "arms" not in case:
        files.append(_join(folder, ARMS))
    for given in case_arms(case, arms).values() if ("arms" in case or arms is not None) else ():
        files += sorted(given.values())
    if case.get("acceptance"):
        files.append(case["acceptance"])
    hooks = sorted({g.get("hook") for g in case.get("graders", []) if isinstance(g, dict) and g.get("type") == "hook_allows"})
    for hook in hooks:
        files.append(f"parts/{hook}.py")
    if hooks:
        files.append(SHELL)
    scaffold = case.get("scaffold_dir")
    if scaffold:
        files += sorted(p for p in paths if p.startswith(scaffold.strip("/") + "/"))
    return list(dict.fromkeys(files))


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
    if record.get("kind") in ("baseline", "one-time"):
        return f"it is a {record['kind']} record, which never counts as passing"
    given = record.get("arms")
    if not isinstance(given, dict):
        return "it holds no arms"
    per_arm = record.get("runs_per_arm")
    again = record.get("rerecorded", [])
    if not isinstance(again, list):
        return "its list of arms recorded once more is not readable"
    for arm in arm_names:
        runs = given.get(arm, {}).get("runs") if isinstance(given.get(arm), dict) else None
        if not isinstance(runs, list) or len(runs) < MIN_RUNS:
            return f"the {arm} arm has {len(runs) if isinstance(runs, list) else 0} runs; it needs {MIN_RUNS} or more"
        if isinstance(per_arm, int):
            allowed = (per_arm, 2 * per_arm) if arm in again else (per_arm,)
            if len(runs) not in allowed:
                return (f"the {arm} arm has {len(runs)} runs, but the record was made with {per_arm} per arm"
                        f"{' and this arm recorded once more' if arm in again else ''}; runs were added or dropped "
                        f"after the recording")
    if "guided" not in given or "bare" not in given:
        return "it needs a guided arm and a bare arm to compare"
    (guided, ng), (bare, nb) = ((passing(given[arm]["runs"], grader_ids), len(given[arm]["runs"])) for arm in ("guided", "bare"))
    if guided * nb <= bare * ng:
        return (f"the guided arm passes every grader in no more of its runs than the bare arm ({guided} of {ng} against "
                f"{bare} of {nb}), so the guidance does not earn its place")
    return None


def pooled(records, min_runs=POOLED_MIN_RUNS, label=""):
    """Why the records, pooled, do not show the guided arm beating the two-line arm, or None.
    records: [(record, grader ids)], each a record that passes judge(). min_runs: runs each arm needs, pooled."""
    if not records:
        return None
    where = f"for {label}, " if label else ""
    if not all("two-line" in record["arms"] for record, _ in records):
        return f"{where}the pooled comparison needs a two-line arm in every record"
    totals = {}
    for record, _ in records:
        for arm, given in record["arms"].items():
            totals[arm] = totals.get(arm, 0) + len(given["runs"])
    for arm, total in totals.items():
        if total < min_runs:
            return (f"{where}pooled across {len(records)} case(s), the {arm} arm has {total} runs; the comparison "
                    f"needs {min_runs} or more in every arm")
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
    return (f"{where}pooled across {len(records)} case(s), the guided arm passes every grader in {a} of {n1} runs and "
            f"the two-line arm in {b} of {n2}: one-sided Fisher exact p = {p:.2g}, not below {POOLED_P}, so two lines "
            f"would do as well")


def guided_counts(records, graders):
    """(passes, runs, recorded once more) of the guided arm, pooled over {case: record}. graders: {case: ids}."""
    passes = runs = 0
    again = False
    for case, record in records.items():
        arm = record["arms"]["guided"]
        passes += passing(arm["runs"], graders[case])
        runs += len(arm["runs"])
        again = again or "guided" in record.get("rerecorded", [])
    return passes, runs, again


def slipped(new, old, what, graders):
    """Why the new records' guided arm fell too far below the old records', or None. new, old: {case: record}.

    Pooled over the cases present in both. Each side is put on the larger side's scale (a 45-run count is doubled
    against a pooled 90), and the margin is 6 when either side was recorded once more, else 3."""
    common = sorted(set(new) & set(old))
    if not common:
        return None
    try:
        a, n, a_again = guided_counts({c: new[c] for c in common}, graders)
        b, m, b_again = guided_counts({c: old[c] for c in common}, graders)
    except (KeyError, TypeError, AttributeError):
        return f"the guided arm of {what} is not readable"
    if not n or not m:
        return None
    scale = max(n, m)
    margin = POOLED_MARGIN if (a_again or b_again) else MARGIN
    new_scaled, old_scaled = a * scale / n, b * scale / m
    if new_scaled >= old_scaled - margin:
        return None
    return (f"its guided arm passes {a} of {n} runs pooled over {', '.join(common)}, against {b} of {m} in {what}: "
            f"{new_scaled:g} against {old_scaled:g} on a {scale}-run scale, more than {margin} fewer. Record the "
            f"slipping arm once more (run.py --rerecord guided) and judge the two pooled, or find what changed")


def _record(text):
    try:
        found = json.loads(text or "")
    except ValueError:
        return None
    return found if isinstance(found, dict) else None


def run(snapshot, config):
    cases = config.get("cases", "evals/cases")
    runs = config.get("runs", "evals/runs")
    folder = evals_folder(cases)
    arms_path = _join(folder, ARMS)
    keys_path = _join(folder, PROOF_KEYS)
    found = []
    case_paths = list(snapshot.paths(suffixes=(".json",), under=cases))

    try:
        proof = load_proof_keys(snapshot.read(keys_path) or "", keys_path) if snapshot.is_file(keys_path) else None
    except Exception as error:       # the harness file is broken: nothing can be hashed or stripped
        proof = None
        found.append(finding(keys_path, 1, f"cannot be loaded ({type(error).__name__}: {error}); nothing can be "
                                           f"hashed until it is repaired; see {PAGE}"))
        return found
    if proof is None and case_paths:
        found.append(finding(keys_path, 1, f"missing: the eval hash and the runner take the proof keys out through "
                                           f"it; see {PAGE}"))
        return found

    shared = None
    if snapshot.is_file(arms_path):
        try:
            shared = json.loads(snapshot.read(arms_path) or "")
            arm_sources(shared)
        except (ValueError, TypeError, AttributeError):
            found.append(finding(arms_path, 1, "not a readable arms file: each arm needs \"files\", "
                                               "a map of where each file goes to where it comes from"))
            return found

    by_playbook, records, all_paths = {}, {}, list(snapshot.paths())
    for path in case_paths:
        try:
            case = json.loads(snapshot.read(path) or "")
            name, playbook = case["name"], case["playbook"]
            if "arms" not in case and shared is None:
                raise TypeError
            arms = case_arms(case, shared)
            files = covered_files(path, case, all_paths, shared, folder)
            grader_ids = [g["id"] for g in case.get("graders", [])]
            if not all(isinstance(f, str) for f in [name, playbook] + files + grader_ids):
                raise TypeError
        except (ValueError, KeyError, TypeError, AttributeError):
            found.append(finding(path, 1, "not a readable eval case with a name, a playbook and arms (its own, or "
                                          "the shared arms file)"))
            continue
        entry = {"name": name, "path": path, "arms": list(arms), "graders": grader_ids, "problem": None, "record": None}
        by_playbook.setdefault(playbook, []).append(entry)
        missing = [f for f in files if not snapshot.is_file(f)]
        if missing:
            entry["problem"] = f"a file case {name} covers is missing: {missing[0]}"
            continue
        texts = {f: snapshot.read(f) for f in files}
        unreadable = [f for f, text in texts.items() if text is None]
        if unreadable:
            entry["problem"] = (f"a file case {name} covers {snapshot.not_utf8(unreadable[0])}, so the case cannot be "
                                f"hashed: {unreadable[0]}")
            continue
        record_path = f"{runs}/{name}/record.json"
        if not snapshot.is_file(record_path):
            entry["problem"] = f"no eval run on record for case {name}; run python3 evals/run.py {name}"
            continue
        record = _record(snapshot.read(record_path))
        if record is None:
            entry["problem"] = f"{record_path} is not a readable eval record"
        elif record.get("guidance_sha256") != guidance_hash(texts, proof.strip):
            entry["problem"] = (f"it, its guidance, its case or the eval harness changed since the last recorded eval "
                                f"run; run case {name} again (python3 evals/run.py {name})")
        else:
            try:
                problem = judge(record, list(arms), grader_ids)
            except (AttributeError, TypeError, ZeroDivisionError):
                problem = "its runs are not readable"
            if problem:
                entry["problem"] = f"its last recorded run of case {name} does not pass: {problem}"
            else:
                entry["record"] = record
                records[name] = record

    for playbook, entries in sorted(by_playbook.items()):
        state, anchors = _proof_state(snapshot, proof, playbook)
        if state != "proven":
            continue
        page = page_of(playbook)
        problems = [e["problem"] for e in entries if e["problem"]]
        for problem in problems:
            found.append(finding(page, 1, f"{problem}; see {PAGE}"))
        if problems:
            continue
        try:
            problem = pooled([(e["record"], e["graders"]) for e in entries], label=playbook)
        except (AttributeError, TypeError, KeyError):
            problem = "the records' runs are not readable"
        if problem:
            found.append(finding(page, 1, f"{problem}; see {PAGE}"))
            continue
        found += _held_to_its_past(snapshot, page, runs, {e["name"]: e["record"] for e in entries}, anchors,
                                   {e["name"]: e["graders"] for e in entries})

    playbooks = config.get("playbooks")
    if playbooks:
        tested = {page_of(p) for p in by_playbook} | set(by_playbook)
        for page in snapshot.paths(suffixes=(".md",), under=playbooks):
            text = snapshot.read(page) or ""
            if proof.keys(text)[0].get("proof") == "proven" and page not in tested:
                found.append(finding(page, 1, f"marked proven, but no eval case tests this playbook; see {PAGE}"))
            for heading, line in proof.keys(text)[1]:
                key = f"{page}#{_slug(heading)}"
                if proof.parse_section(line)[0] == "proven" and key not in tested:
                    found.append(finding(page, 1, f"section {heading!r} is marked proven, but no eval case names "
                                                  f"{key}; see {PAGE}"))
    return found


def _slug(heading):
    return re.sub(r"[^\w\- ]", "", heading.lower()).strip().replace(" ", "-")


def _proof_state(snapshot, proof, playbook):
    """("proven" | "unproven" | None, [anchor (sha, path)]) of a case's page or page#section."""
    page, _, section = playbook.partition("#")
    text = snapshot.read(page) if snapshot.is_file(page) else None
    if text is None:
        return None, []
    front, sections = proof.keys(text)
    if section:
        for heading, line in sections:
            if _slug(heading) == section:
                state, value = proof.parse_section(line)
                items = proof.parse_list(value) if state == "proven" else []
                return state, [(sha, path) for sha, path in items if sha]
        return None, []
    items = proof.parse_list(front["proven-by"]) if front.get("proven-by") else []
    return front.get("proof"), [(sha, path) for sha, path in items if sha]


def _held_to_its_past(snapshot, page, runs, current, anchors, graders):
    """Findings for a proven page whose guided arm slipped below the previous record's or its anchor's."""
    if not snapshot.has_base():
        return [finding(page, 1, "no base commit to compare with, so its guided arm was not compared with the "
                                 "previous record or with the anchor its proven-by names (a plain check, or a "
                                 "scheduled run); the commit check and CI on a pull request compare them",
                        level="warning")]
    found = []
    snapshot.prefetch_history([f"{runs}/{name}/record.json" for name in current], anchors)
    previous = {}
    for name in current:
        record = _record(snapshot.base_text(f"{runs}/{name}/record.json"))
        if record is not None:
            previous[name] = record
    problem = slipped(current, previous, "the previous record, at the base commit", graders)
    if problem:
        found.append(finding(page, 1, f"{problem}; see {PAGE}"))
    anchored = {}
    for sha, path in anchors:
        match = re.fullmatch(rf"{re.escape(runs)}/([^/]+)/record\.json", path)
        if not match or match.group(1) not in current:
            continue
        record = _record(snapshot.commit_text(sha, path))
        if record is None:
            found.append(finding(page, 1, f"the anchor {sha[:12]}:{path} its proven-by names cannot be read; fetch the "
                                          f"full history (git fetch --unshallow) or correct the anchor; see {PAGE}"))
            continue
        anchored[match.group(1)] = record
    problem = slipped(current, anchored, "the anchor its proven-by names", graders)
    if problem:
        found.append(finding(page, 1, f"{problem}; see {PAGE}"))
    return found
