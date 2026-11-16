#!/usr/bin/env python3
"""Pool the recorded runs of every case, and print the table evals/README.md carries.

    python3 evals/pool.py

A run passes when it passes every grader of its case. For each arm this gives
the pooled pass rate with its 95% interval (Wilson's), then a one-sided Fisher
exact test of whether the guided arm passes more often than each other arm.
The milestone's stop rule reads the guided arm against the two-line arm at p < 0.05.
It reads only the records; it runs no agent.
"""
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ARMS = ("guided", "two-line", "bare")
Z95 = 1.959963984540054


def wilson(passed, total, z=Z95):
    """The 95% Wilson score interval for passed of total, as (low, high)."""
    if total == 0:
        return 0.0, 1.0
    rate = passed / total
    middle = (rate + z * z / (2 * total)) / (1 + z * z / total)
    half = z * math.sqrt(rate * (1 - rate) / total + z * z / (4 * total * total)) / (1 + z * z / total)
    return max(0.0, middle - half), min(1.0, middle + half)


def fisher_greater(a, n1, b, n2):
    """One-sided Fisher exact p: the chance of a or more passes in the first group, if both groups share one rate."""
    passes, total = a + b, n1 + n2
    tail = sum(math.comb(passes, k) * math.comb(total - passes, n1 - k) for k in range(a, min(passes, n1) + 1))
    return tail / math.comb(total, n1)


def pool(root=ROOT):
    """{case: {arm: (passed, runs)}} and the pooled {arm: (passed, runs)}."""
    cases, pooled = {}, {arm: [0, 0] for arm in ARMS}
    for path in sorted((root / "evals/runs").glob("*/record.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
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


def table(root=ROOT):
    cases, pooled = pool(root)
    lines = ["| Case | Guided | Two-line | Bare |", "|---|---|---|---|"]
    for name, arms in cases.items():
        lines.append(f"| {name} | " + " | ".join(cell(*arms[arm]) for arm in ARMS) + " |")
    lines.append("| **Pooled** | " + " | ".join(f"**{cell(*pooled[arm])}**" for arm in ARMS) + " |")
    guided = pooled["guided"]
    tests = [f"Guided against {arm}, one-sided Fisher exact test: p = {fisher_greater(*guided, *pooled[arm]):.2g}."
             for arm in ("two-line", "bare") if pooled[arm][1] and guided[1]]
    return "\n".join(lines) + "\n\n" + " ".join(tests) + "\n"


def main():
    print(table(), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
