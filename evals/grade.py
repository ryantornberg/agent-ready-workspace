#!/usr/bin/env python3
"""Grade a recorded agent run against an eval case.

    python3 evals/grade.py evals/cases/fix-a-bug.json evals/transcripts/fix-a-bug.pass.json

A case names a request and a list of graders. A transcript is the ordered list
of actions one agent run took: {"kind": "read|run|edit|report", "target": "..."}.
This script does not run an agent. Record the transcript with whatever tool you
use, once with the playbook and once without it, and grade both.

Grader types:

  any     at least one action matches
  none    no action matches
  before  an action matching "first" happens before the first action matching "then".
          Fails if "then" happens with no "first" ahead of it, or never happens.

A matcher is {"kind": "...", "match": "regex"}; either part may be left out.
Exit 1 if any grader fails.
"""
import json
import re
import sys


def matches(action, matcher):
    if "kind" in matcher and action.get("kind") != matcher["kind"]:
        return False
    return re.search(matcher.get("match", ""), action.get("target", ""), re.I) is not None


def grade_one(grader, actions):
    kind = grader["type"]
    if kind == "any":
        return any(matches(a, grader) for a in actions)
    if kind == "none":
        return not any(matches(a, grader) for a in actions)
    if kind == "before":
        seen_first = False
        for action in actions:
            if matches(action, grader["first"]):
                seen_first = True
            if matches(action, grader["then"]):
                return seen_first
        return False
    raise ValueError(f"unknown grader type: {kind}")


def grade(case, actions):
    """Return [(grader id, passed)] in the case's order."""
    return [(g["id"], grade_one(g, actions)) for g in case["graders"]]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print(__doc__)
        return 2
    with open(argv[0], encoding="utf-8") as f:
        case = json.load(f)
    with open(argv[1], encoding="utf-8") as f:
        actions = json.load(f)
    results = grade(case, actions)
    for grader_id, passed in results:
        print(f"{'pass' if passed else 'FAIL'}  {grader_id}")
    failed = sum(1 for _, passed in results if not passed)
    print(f"\n{case['name']}: {len(results) - failed} of {len(results)} graders passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
