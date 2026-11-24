#!/usr/bin/env python3
"""Pool the recorded runs of each playbook's cases, and print each playbook's table; evals/README.md carries fix-a-bug's.

    python3 evals/pool.py                                # a table for each playbook with a record
    python3 evals/pool.py docs/playbooks/debugging.md    # that playbook's table alone

Each playbook's cases are pooled on their own, as the eval_record gate pools them: a record joins the
table of the playbook it names, so one playbook's runs never move another's numbers.
A run passes when it passes every grader of its case. For each arm this gives
the pooled pass rate with its 95% interval (Wilson's), then a one-sided Fisher
exact test of whether the guided arm passes more often than each other arm.
The eval_record gate, and the milestone's stop rule, read the guided arm against
the two-line arm at p < 0.05. It reads only the records; it runs no agent.
"""
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from parts.eval_record import fisher_greater  # noqa: E402,F401  (the gate's own test, so the two cannot differ)

ARMS = ("guided", "two-line", "bare")
FIX_A_BUG = "docs/playbooks/fix-a-bug.md"
Z95 = 1.959963984540054


def wilson(passed, total, z=Z95):
    """The 95% Wilson score interval for passed of total, as (low, high)."""
    if total == 0:
        return 0.0, 1.0
    rate = passed / total
    middle = (rate + z * z / (2 * total)) / (1 + z * z / total)
    half = z * math.sqrt(rate * (1 - rate) / total + z * z / (4 * total * total)) / (1 + z * z / total)
    return max(0.0, middle - half), min(1.0, middle + half)


def records(root=ROOT):
    """Every gated record under evals/runs/, in case order. Baselines and one-time arms sit deeper and are left out."""
    return [json.loads(path.read_text(encoding="utf-8"))
            for path in sorted((root / "evals/runs").glob("*/record.json"))]


def playbooks(root=ROOT):
    """The playbooks that have a record, in order."""
    return sorted({record["playbook"] for record in records(root)})


def pool(playbook, root=ROOT):
    """{case: {arm: (passed, runs)}} and the pooled {arm: (passed, runs)}, over the playbook's records only."""
    cases, pooled = {}, {arm: [0, 0] for arm in ARMS}
    for record in records(root):
        if record["playbook"] != playbook:
            continue
        cases[record["case"]] = {}
        for arm in ARMS:
            runs = record["arms"][arm]["runs"]
            passed = sum(1 for run in runs if run["passed"])
            cases[record["case"]][arm] = (passed, len(runs))
            pooled[arm][0] += passed
            pooled[arm][1] += len(runs)
    return cases, {arm: tuple(counts) for arm, counts in pooled.items()}


def cell(passed, total):
    low, high = wilson(passed, total)
    return f"{passed} of {total}: {passed / total:.0%} ({low:.0%} to {high:.0%})" if total else "no runs"


def table(playbook, root=ROOT):
    cases, pooled = pool(playbook, root)
    lines = ["| Case | Guided | Two-line | Bare |", "|---|---|---|---|"]
    for name, arms in cases.items():
        lines.append(f"| {name} | " + " | ".join(cell(*arms[arm]) for arm in ARMS) + " |")
    lines.append("| **Pooled** | " + " | ".join(f"**{cell(*pooled[arm])}**" for arm in ARMS) + " |")
    guided = pooled["guided"]
    tests = [f"Guided against {arm}, one-sided Fisher exact test: p = {fisher_greater(*guided, *pooled[arm]):.2g}."
             for arm in ("two-line", "bare") if pooled[arm][1] and guided[1]]
    return "\n".join(lines) + "\n\n" + " ".join(tests) + "\n"


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) > 1:
        print("usage: python3 evals/pool.py [PLAYBOOK]", file=sys.stderr)
        return 2
    if argv:
        if argv[0] not in playbooks():
            print(f"no record names the playbook {argv[0]}; these do: {', '.join(playbooks())}", file=sys.stderr)
            return 1
        print(table(argv[0]), end="")
        return 0
    print("\n".join(f"{playbook}\n\n{table(playbook)}" for playbook in playbooks()), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
