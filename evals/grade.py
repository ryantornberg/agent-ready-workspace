#!/usr/bin/env python3
"""Grade one recorded agent run against an eval case.

    python3 evals/grade.py evals/cases/fix-a-bug.json evals/runs/fix-a-bug/guided-1.json
    python3 evals/grade.py --recorded      # re-grade every stored transcript against its record; CI runs this

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
               hook imports, the shell parser wslib/shell.py, so the eval hash covers that
               module and the hook's file, and any other engine change leaves the eval
               records current.

A matcher is {"kind": ..., "match": regex, "output": regex, "ok": bool}; each part
is optional. "match" is searched in the target and "output" in the output,
ignoring case, with ^ and $ matching at line ends.

Exit 0 when every grader passes, 1 when one fails, 2 when the case or transcript is malformed.
With --recorded: exit 0 when every stored grade matches a fresh one, 1 when one differs.
"""
import json
import pathlib
import re
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


def regrade_records(root=ROOT):
    """Re-grade every stored transcript. Returns a list of differences from what the records say."""
    differences = []
    runs = root / "evals" / "runs"
    # The gated records, the baselines, and the one-time arms' records: each is re-graded from its transcripts.
    found = sorted(runs.glob("*/record.json")) + sorted(runs.glob("*/baseline/record.json")) \
        + sorted(runs.glob("*/one-time/*/record.json"))
    for record_path in found:
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


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv == ["--recorded"]:
        differences = regrade_records()
        for line in differences:
            print(line)
        print(f"re-graded every stored transcript: {'no' if not differences else len(differences)} difference(s)")
        return 1 if differences else 0
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
