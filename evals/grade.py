#!/usr/bin/env python3
"""Grade one recorded agent run against an eval case.

    python3 evals/grade.py evals/cases/fix-a-bug.json evals/runs/fix-a-bug/guided-1.json
    python3 evals/grade.py --recorded      # re-grade every stored transcript against its record; CI runs this
    python3 evals/grade.py --recorded --stamp [--base REF]   # then write the grader hash, when no grade differs

A transcript is the ordered list of what one run did:

    {"kind": "read|run|edit|dispatch|report|state", "target": "...", "ok": true|false, "output": "..."}

"run" is a shell command, "ok" is whether it exited zero, and "output" is the
end of what it printed. An exit code alone is not enough: `test | tail` exits
zero whatever the tests did, so a grader can match on the output instead. "dispatch" is a
task handed to a fresh helper session, its target the task's description. "report" is the
agent's final message. "state" lines are not the agent's word for anything:
evals/run.py adds them after the run, by inspecting the folder the agent left.

Grader types:

  any          at least one action matches
  none         no action matches
  before       an action matching "first" comes before the first action matching "then".
               Fails if "then" comes first, or never comes.
  report_brief the final report is short and gives what it must: at most "max_lines" non-blank
               lines, a match for "path" (such as the findings file) and one for "verdict".
               An adversarial review's reply gives only the file's path and its verdict.
  hook_allows  a workspace hook allows every "run" action. The grader loads the hook's
               own file, parts/<hook>.py, and calls its decide function, so the test and
               the rule cannot drift apart. Of the engine (wslib/) it loads only what the
               hook imports, the shell parser wslib/shell.py, so the grader hash covers that
               module and the hook's file, and any other engine change leaves the eval
               records current.

A matcher is {"kind": ..., "match": regex, "output": regex, "ok": bool}; each part
is optional. "match" is searched in the target and "output" in the output,
ignoring case, with ^ and $ matching at line ends.

Exit 0 when every grader passes, 1 when one fails, 2 when the case or transcript is malformed.
With --recorded: exit 0 when every stored grade matches a fresh one, 1 when one differs.

The base commit's copy judges too (M4 slice H0a). --recorded re-grades with this grade.py, and again with
grade.py as the base commit holds it when that is another text, each against this tree's hooks and parser. The
base's copy judges every run the base already holds; a run recorded since the base, whose transcript read as JSON
is new or changed, the base's copy never graded, so this grade.py alone judges it. The base is the merge base of
HEAD and --base REF; with no --base, of the base a GitHub Actions run names (the pull request's base, or the commit
before a push), else of origin/main. With none, --recorded judges with this grade.py alone and says so, and --stamp
refuses. A base whose grade.py cannot be read or cannot re-grade is a difference. The base's copy is called as
regrade_records(root), and its lines are read as "<record>: <arm> <transcript>: ...", so that call and that form
must stay; a line in another form is kept.

--stamp: when neither copy finds a difference, write the grader hash into every record whose hash over what an
agent is given is current, as the eval_record check computes both. A record already stale stays as it is. With
a difference it writes nothing: a grading rule is not changed after the runs it grades, so the case is recorded
again. A change to grade.py itself is never stamped onto runs graded before it, since this grade.py would judge
its own change: when grade.py differs from the base's, a record that held a grader hash at the base is stamped
only when its every run was recorded since the base. Each other gated record is named, and the exit is 1; a
one-time or baseline record, which the gate never reads, is left as it is and named, and does not count. CI runs this grade.py, not the base's, so that rule is
held by eval_record too; see the README's Limits. Grading imports nothing from the engine; only the stamp loads
the harness, run.py, for the hashes.
"""
import json
import os
import pathlib
import re
import subprocess
import sys
import types

ROOT = pathlib.Path(__file__).resolve().parent.parent
HOOK_NAME = re.compile(r"[A-Za-z0-9_]+")

MATCHER_KEYS = {"kind", "match", "output", "ok"}
GRADER_KEYS = {
    "any": {"id", "type"} | MATCHER_KEYS,
    "none": {"id", "type"} | MATCHER_KEYS,
    "before": {"id", "type", "first", "then"},
    "hook_allows": {"id", "type", "hook", "kind"},
    "report_brief": {"id", "type", "path", "verdict", "max_lines"},
}
KINDS = {"read", "run", "edit", "dispatch", "report", "state"}


class Malformed(Exception):
    pass


def validate(case, actions):
    graders = case.get("graders") if isinstance(case, dict) else None
    if not isinstance(graders, list) or not graders:
        raise Malformed("the case has no graders, so it would pass anything")
    for grader in graders:
        kind = grader.get("type") if isinstance(grader, dict) else None
        if kind not in GRADER_KEYS or "id" not in grader:
            raise Malformed(f"grader needs an id and a type from {sorted(GRADER_KEYS)}: {grader!r}")
        unknown = set(grader) - GRADER_KEYS[kind]
        for matcher in (grader.get("first"), grader.get("then")):
            if kind == "before" and (not isinstance(matcher, dict) or set(matcher) - MATCHER_KEYS):
                raise Malformed(f"grader {grader['id']}: first and then are matchers with keys from {sorted(MATCHER_KEYS)}")
        if unknown:
            raise Malformed(f"grader {grader['id']}: unknown key(s) {sorted(unknown)}; a typo here would pass silently")
        if kind == "report_brief" and (not isinstance(grader.get("max_lines"), int) or not grader.get("path")
                                       or not grader.get("verdict")):
            raise Malformed(f"grader {grader['id']}: report_brief needs path, verdict and max_lines")
    if not isinstance(actions, list) or not all(isinstance(a, dict) and a.get("kind") in KINDS for a in actions):
        raise Malformed(f"a transcript is a list of actions, each with a kind from {sorted(KINDS)}")


def matches(action, matcher):
    if "kind" in matcher and action.get("kind") != matcher["kind"]:
        return False
    if "ok" in matcher and action.get("ok", True) != matcher["ok"]:
        return False
    if "output" in matcher and not re.search(matcher["output"], str(action.get("output", "")), re.I | re.M):
        return False
    return re.search(matcher.get("match", ""), str(action.get("target", "")), re.I | re.M) is not None


def load_hook(root, name):
    """The hook's own module, from parts/<name>.py under root. Raises Malformed when it cannot be loaded."""
    if not isinstance(name, str) or not HOOK_NAME.fullmatch(name):
        raise Malformed(f"a hook_allows grader names a hook under parts/ by its plain name, not {name!r}")
    path = pathlib.Path(root) / "parts" / f"{name}.py"
    if str(ROOT) not in sys.path:           # a hook imports the shell parser, wslib.shell, from this repository
        sys.path.insert(0, str(ROOT))
    module = types.ModuleType(f"graded_hook_{name}")
    module.__file__ = str(path)
    try:
        exec(compile(path.read_text(encoding="utf-8-sig"), str(path), "exec"), module.__dict__)
    except Exception as error:
        raise Malformed(f"hook {name} cannot be loaded from {path.name}: {type(error).__name__}: {error}")
    if not callable(getattr(module, "decide", None)):
        raise Malformed(f"hook {name} has no decide function")
    return module


def grade_one(grader, actions, root=ROOT):
    kind = grader["type"]
    if kind == "any":
        return any(matches(a, grader) for a in actions)
    if kind == "none":
        return not any(matches(a, grader) for a in actions)
    if kind == "before":
        seen_first = False
        for action in actions:
            if matches(action, grader["then"]):
                return seen_first
            if matches(action, grader["first"]):
                seen_first = True
        return False
    if kind == "report_brief":
        reports = [a for a in actions if a.get("kind") == "report"]
        text = str(reports[-1].get("target", "")) if reports else ""
        lines = [line for line in text.splitlines() if line.strip()]
        return (0 < len(lines) <= grader["max_lines"] and re.search(grader["path"], text, re.I | re.M) is not None
                and re.search(grader["verdict"], text, re.I | re.M) is not None)
    hook = load_hook(root, grader["hook"])
    return all(hook.decide({"command": a.get("target")}, {}) is None for a in actions if a.get("kind") == "run")


def grade(case, actions, root=ROOT):
    """Return [(grader id, passed)] in the case's order."""
    validate(case, actions)
    return [(g["id"], grade_one(g, actions, root)) for g in case["graders"]]


def record_paths(root=ROOT):
    """The gated records, the baselines, and the one-time arms' records: each is re-graded from its transcripts."""
    runs = pathlib.Path(root) / "evals" / "runs"
    return sorted(runs.glob("*/record.json")) + sorted(runs.glob("*/baseline/record.json")) \
        + sorted(runs.glob("*/one-time/*/record.json"))


def regrade_records(root=ROOT):
    """Re-grade every stored transcript. Returns a list of differences from what the records say."""
    differences = []
    runs = root / "evals" / "runs"
    for record_path in record_paths(root):
        where = record_path.relative_to(root).as_posix()
        try:
            record = json.loads(record_path.read_text(encoding="utf-8"))
            case = json.loads((root / "evals" / "cases" / f"{record['case']}.json").read_text(encoding="utf-8"))
            arms = record["arms"].items()
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
            differences.append(f"{where}: cannot be read with its case: {error}")
            continue
        ids = [g["id"] for g in case["graders"]]
        for arm, given in arms:
            fresh_runs = []
            for run in given.get("runs", []):
                try:
                    actions = json.loads((record_path.parent / run["transcript"]).read_text(encoding="utf-8"))
                    fresh = dict(grade(case, actions, root))
                except (OSError, ValueError, KeyError, TypeError, Malformed) as error:
                    differences.append(f"{where}: {arm} {run.get('transcript')}: cannot be graded: {error}")
                    continue
                fresh_runs.append(fresh)
                for grader_id in ids:
                    if run.get("graders", {}).get(grader_id) != fresh[grader_id]:
                        differences.append(f"{where}: {arm} {run['transcript']}: {grader_id} is recorded as "
                                           f"{run.get('graders', {}).get(grader_id)} and grades as {fresh[grader_id]}")
                if run.get("passed") != all(fresh.values()):
                    differences.append(f"{where}: {arm} {run['transcript']}: passed is recorded as {run.get('passed')}")
            counts = {g: sum(r[g] for r in fresh_runs) for g in ids}
            if given.get("runs_passing_each_grader") != counts:
                differences.append(f"{where}: {arm}: the counts per grader differ from the runs")
            if given.get("runs_passing_every_grader") != sum(all(r.values()) for r in fresh_runs):
                differences.append(f"{where}: {arm}: the count of runs passing every grader differs from the runs")
        stored = sorted(p.name for p in record_path.parent.glob("*.json") if p.name != "record.json")
        listed = sorted(run.get("transcript") for _, given in arms for run in given.get("runs", []))
        if stored != listed:
            differences.append(f"{where}: the transcripts on disk are not the ones the record lists")
    if not differences and not any(runs.glob("*/record.json")):
        differences.append("no eval record found under evals/runs")
    return differences


def _git(root, *args):
    """git's output as bytes, or None when it fails."""
    try:
        done = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    except OSError:
        return None
    return done.stdout if done.returncode == 0 else None


def _event_base():
    """The base a GitHub Actions run names, as CI's other steps read it: the pull request's base, or the commit
    before a push. None outside Actions, on a scheduled run, or on a push that opens a branch."""
    path = os.environ.get("GITHUB_EVENT_PATH")
    try:
        event = json.loads(pathlib.Path(path).read_text(encoding="utf-8")) if path else None
    except (OSError, ValueError):
        return None
    if not isinstance(event, dict):
        return None
    sha = ((event.get("pull_request") or {}).get("base") or {}).get("sha") or event.get("before")
    return sha if isinstance(sha, str) and sha.strip("0") else None


def base_commit(root=ROOT, given=None):
    """The commit whose grade.py judges this tree, or None. See the module's docstring."""
    for ref in [given] if given else [_event_base(), "origin/main"]:
        found = _git(root, "merge-base", ref, "HEAD") if ref and not ref.startswith("-") else None
        if found and found.strip():
            return found.decode("ascii", "replace").strip()
    return None


def base_copy(root, base):
    """grade.py as the base commit holds it, loaded so that it grades root with root's own hooks and parser. None
    when the base holds this same text. Raises when git cannot read it there: nothing passes unjudged."""
    data = _git(root, "show", f"{base}:evals/grade.py")
    if data is None:
        raise RuntimeError(f"git cannot read evals/grade.py at the base commit {base[:12]}")
    text = data.decode("utf-8-sig").replace("\r\n", "\n")
    here = pathlib.Path(root) / "evals" / "grade.py"
    if here.is_file() and here.read_text(encoding="utf-8-sig").replace("\r\n", "\n") == text:
        return None
    module = types.ModuleType("grade_at_base")
    module.__file__ = str(here)          # its ROOT is root, so the hooks it loads, and their parser, are root's
    exec(compile(text, f"{base[:12]}:evals/grade.py", "exec"), module.__dict__)
    return module


def _parsed(data):
    try:
        return json.loads(data) if data else None
    except ValueError:
        return None


def new_since(root, base):
    """The transcripts under evals/runs recorded since the base: new, or holding other content, read as JSON, than
    the base's copy. A file only re-written in another layout is not new."""
    changed = _git(root, "diff", "--name-only", "--no-renames", "-z", base, "--", "evals/runs")
    added = _git(root, "ls-files", "-z", "-o", "--exclude-standard", "--", "evals/runs")
    if changed is None or added is None:
        raise RuntimeError("git cannot list what changed under evals/runs since the base")
    new = set()
    for path in {p for p in (changed + added).decode("utf-8", "surrogateescape").split("\0") if p}:
        disk = pathlib.Path(root) / path
        if not path.endswith(".json") or path.endswith("/record.json") or not disk.is_file():
            continue
        then = _parsed(_git(root, "show", f"{base}:{path}"))
        if then is None or then != _parsed(disk.read_bytes()):
            new.add(path)
    return new


def judged_by_base(line, new, arms_with_new):
    """Whether a line of the base copy's judges a run the base holds. A line on a new run, or on the counts of an
    arm that holds one, is left to this grade.py; a line in a form not read here is kept."""
    found = re.match(r"(?P<record>evals/runs/\S+/record\.json): (?P<arm>\S+)(?: (?P<run>\S+\.json))?: ", line)
    if not found:
        return True
    folder = found["record"].rsplit("/", 1)[0]
    if found["run"]:
        return f"{folder}/{found['run']}" not in new
    return (found["record"], found["arm"]) not in arms_with_new


def regrade_with_base(root, base):
    """(differences, how it was judged, whether grade.py differs from the base's, the runs new since the base):
    re-graded with this grade.py, and with the base commit's when that is another text, over the runs the base
    holds. A base copy that cannot be read, loaded or re-grade is a difference: nothing passes unjudged."""
    root = pathlib.Path(root)
    differences = regrade_records(root)
    if not base:
        return differences, "no base commit was found, so this grade.py alone judged", False, set()
    where = f"the base commit's grade.py ({base[:12]})"
    left, changed, new = 0, True, set()
    try:
        copy = base_copy(root, base)
        new = new_since(root, base)
        if copy is None:
            return differences, f"this grade.py judged; the base commit ({base[:12]}) holds the same", False, new
        arms_with_new = set()
        for record_path in record_paths(root):
            record = json.loads(record_path.read_text(encoding="utf-8"))
            folder = record_path.parent.relative_to(root).as_posix()
            for arm, given in record.get("arms", {}).items():
                if any(f"{folder}/{run.get('transcript')}" in new for run in given.get("runs", [])):
                    arms_with_new.add((record_path.relative_to(root).as_posix(), arm))
        found = []
        for line in copy.regrade_records(root):
            if judged_by_base(line, new, arms_with_new):
                found.append(line)
            else:
                left += 1
    except Exception as error:      # any failure of the base's copy fails closed
        found = [f"it cannot re-grade: {type(error).__name__}: {error}"]
    how = f"this grade.py and {where} judged"
    if left:
        how += (f"; {left} line(s) the base's copy gave on runs recorded since the base were left to this grade.py, "
                f"which the base's copy never graded")
    return differences + [f"by {where}: {line}" for line in found], how, changed, new


def stamp(root, differences, grader_changed=False, new=(), base=None):
    """Write the grader hash into each record whose hash over what an agent is given is current, when no grade
    differs. When grade.py differs from the base's, not into a record that held a grader hash at the base unless
    its every run is in new, the runs recorded since the base. Returns (stamped, left, refused), each a list of lines; writes nothing when differences is not
    empty."""
    if differences:
        return [], [], []
    refused = []
    root = pathlib.Path(root)
    if str(root / "evals") not in sys.path:
        sys.path.insert(0, str(root / "evals"))
    import run as harness            # the harness's own hash, the one run.py writes; it loads the eval_record check
    checks, paths = harness.eval_record, harness.workspace_files(root)
    known, stamped, left = set(paths), [], []
    for record_path in record_paths(root):
        where = record_path.relative_to(root).as_posix()
        record = json.loads(record_path.read_text(encoding="utf-8"))
        try:
            _, digest = harness.covered(record["case"], root)
        except (OSError, ValueError, KeyError, TypeError) as error:
            left.append(f"{where}: its case cannot be hashed ({error}), so it was left as it is")
            continue
        if record.get("guidance_sha256") != digest:
            left.append(f"{where}: stale, since what an agent is given changed after its runs; left as it is")
            continue
        folder = record_path.parent.relative_to(root).as_posix()
        runs = [f"{folder}/{run.get('transcript')}" for given in record.get("arms", {}).values()
                for run in given.get("runs", [])]
        at_base = _parsed(_git(root, "show", f"{base}:{where}")) if grader_changed else None
        if isinstance(at_base, dict) and "grader_sha256" in at_base and not all(run in new for run in runs):
            if record_path.parent.name == record["case"] and record_path.parent.parent.name == "runs":
                refused.append(f"{where}: not stamped: evals/grade.py differs from the base commit's, and its runs "
                               f"were graded before that change; record case {record['case']} again, then stamp")
            else:                    # a one-time arm's record or a baseline: the gate never reads it
                left.append(f"{where}: left as it is: evals/grade.py differs from the base commit's, and its runs were "
                            f"graded before that change; the gate does not read a one-time or baseline record, so "
                            f"this does not fail the stamp")
            continue
        case = harness.load_case(record["case"], root)
        files = checks.grading_files(case, paths, lambda path: harness.read_text(root, path), "evals")
        missing = [f for f in files if f not in known]
        if missing:
            left.append(f"{where}: a grading file is missing ({missing[0]}); left as it is")
            continue
        grader = checks.grader_hash({f: harness.read_text(root, f) for f in files})
        if record.get("grader_sha256") == grader and record.get("grader_covers") == files:
            continue
        written = {}
        for key, value in record.items():
            if key not in ("grader_covers", "grader_sha256"):
                written[key] = value
            if key == "guidance_sha256":
                written.update({"grader_covers": files, "grader_sha256": grader})
        record_path.write_text(json.dumps(written, indent=2) + "\n", encoding="utf-8")
        stamped.append(where)
    return stamped, left, refused


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["--recorded"]:
        rest = [a for a in argv[1:] if a != "--stamp"]
        stamping, given = "--stamp" in argv[1:], None
        if len(rest) == 2 and rest[0] == "--base":
            given, rest = rest[1], []
        if rest or argv.count("--stamp") > 1:
            print(__doc__)
            return 2
        base = base_commit(ROOT, given)
        if given and not base:
            print(f"grade: --base {given} names no commit that shares history with HEAD", file=sys.stderr)
            return 2
        if stamping and not base:
            print("grade: no base commit to judge this grade.py with (no GitHub event names one, and there is no "
                  "origin/main), so nothing is stamped; pass --base REF, the commit your change starts from",
                  file=sys.stderr)
            return 2
        differences, how, grader_changed, new = regrade_with_base(ROOT, base)
        for line in differences:
            print(line)
        print(f"re-graded every stored transcript: {'no' if not differences else len(differences)} difference(s); "
              f"{how}")
        if not stamping:
            return 1 if differences else 0
        if differences:
            print("nothing stamped: a grade differs, so each case it names is recorded again (python3 evals/run.py)")
            return 1
        stamped, left, refused = stamp(ROOT, differences, grader_changed, new, base)
        for line in left + refused:
            print(line)
        print(f"stamped the grader hash into {len(stamped)} record(s)" + "".join(f"\n  {w}" for w in stamped))
        return 1 if refused else 0
    if len(argv) != 2:
        print(__doc__)
        return 2
    try:
        case = json.loads(pathlib.Path(argv[0]).read_text(encoding="utf-8"))
        actions = json.loads(pathlib.Path(argv[1]).read_text(encoding="utf-8"))
        results = grade(case, actions)
    except (OSError, ValueError, Malformed) as error:
        print(f"grade: {error}", file=sys.stderr)
        return 2
    for grader_id, passed in results:
        print(f"{'pass' if passed else 'FAIL'}  {grader_id}")
    failed = sum(1 for _, passed in results if not passed)
    print(f"\n{case['name']}: {len(results) - failed} of {len(results)} graders passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
