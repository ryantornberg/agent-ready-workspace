#!/usr/bin/env python3
"""Grade one recorded agent run against an eval case.

    python3 evals/grade.py evals/cases/fix-a-bug.json evals/runs/fix-a-bug/with.json

A transcript is the ordered list of what one run did:

    {"kind": "read|run|edit|report|state", "target": "...", "ok": true|false, "output": "..."}

"run" is a shell command, "ok" is whether it exited zero, and "output" is the
end of what it printed. An exit code alone is not enough: `test | tail` exits
zero whatever the tests did, so a grader can match on the output instead. "report" is the
agent's final message. "state" lines are not the agent's word for anything:
evals/run.py adds them after the run, by inspecting the folder the agent left.

Grader types:

  any          at least one action matches
  none         no action matches
  before       an action matching "first" comes before the first action matching "then".
               Fails if "then" comes first, or never comes.
  hook_allows  a workspace hook allows every "run" action. The grader calls the
               hook's own decide function, so the test and the rule cannot drift apart.

A matcher is {"kind": ..., "match": regex, "output": regex, "ok": bool}; each part
is optional. "match" is searched in the target and "output" in the output,
ignoring case, with ^ and $ matching at line ends.

Exit 0 when every grader passes, 1 when one fails, 2 when the case or transcript is malformed.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from wslib import parts as partlib  # noqa: E402

MATCHER_KEYS = {"kind", "match", "output", "ok"}
GRADER_KEYS = {
    "any": {"id", "type"} | MATCHER_KEYS,
    "none": {"id", "type"} | MATCHER_KEYS,
    "before": {"id", "type", "first", "then"},
    "hook_allows": {"id", "type", "hook", "kind"},
}
KINDS = {"read", "run", "edit", "report", "state"}


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
    hook = partlib.load(root, {"use": grader["hook"]})
    return all(hook.decide({"command": a.get("target")}) is None for a in actions if a.get("kind") == "run")


def grade(case, actions, root=ROOT):
    """Return [(grader id, passed)] in the case's order."""
    validate(case, actions)
    return [(g["id"], grade_one(g, actions, root)) for g in case["graders"]]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print(__doc__)
        return 2
    try:
        case = json.loads(pathlib.Path(argv[0]).read_text(encoding="utf-8"))
        actions = json.loads(pathlib.Path(argv[1]).read_text(encoding="utf-8"))
        results = grade(case, actions)
    except (OSError, ValueError, Malformed, partlib.PartError) as error:
        print(f"grade: {error}", file=sys.stderr)
        return 2
    for grader_id, passed in results:
        print(f"{'pass' if passed else 'FAIL'}  {grader_id}")
    failed = sum(1 for _, passed in results if not passed)
    print(f"\n{case['name']}: {len(results) - failed} of {len(results)} graders passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
