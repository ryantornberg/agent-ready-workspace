---
kind: record
last-reviewed: 2026-11-23
covers: evals/README.md
reviewed-at: dace91e, with the uncommitted change of the B5 slice session
---

# Instruction review: evals/README.md

This records the review of B5's added reason under the eval page's "turn the failure into a case" rule, for its author and readers.

**In short:** 2 findings, none blocking: 1 contradiction, 1 enforcement. The new reason says any guidance fix without a case leaves the failure free to return, while escape analysis fixes guidance before its case exists, and nothing enforces the rule.

## Scope

In scope: the sentence added to the first bullet of "Rules that make this worth doing", "A guidance fix with no case to replay the failure has nothing to catch the failure's return", from `git diff HEAD -- evals/README.md`. The whole page was read to judge contradictions. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/playbooks/escape-analysis.md` (steps 7 and 8, at `HEAD`), `docs/playbooks/instruction-review.md`, `docs/extend-the-workspace.md` (step 3), `evals/arms.json`, `kit/kit.json` and `kit/seed/evals-README.md`.

Runs (verified): `python3 ws.py check` in the worktree exits 0 with one `eval_record` warning. `grep` finds no mention of `evals/README.md` in `evals/arms.json`, `evals/one-time.json` or the cases, so the page is outside the eval hash and the edit stales no record.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | "Rules that make this worth doing", the first bullet; escape analysis, steps 7 and 8 | Not blocking. The bullet says to turn a failure into a case "before you fix the guidance", and the new sentence says a fix with no case "has nothing to catch the failure's return" (verified, reading). Escape analysis, the page this reason came from, applies its changes in step 7, guidance pages among them, and in step 8 only describes the replay case, since the eval system for procedures waits for M4 (verified, reading). So an agent running escape analysis fixes guidance with no case, which this page says comes second, and neither page labels the other as an exception (inferred). | fixed: the bullet says that until procedures have an eval system, planned for M4, escape analysis describes such a case in its report instead, linking it |
| 2 | enforcement | "Rules that make this worth doing", the first bullet | Not blocking. The bullet is a must, and the page states no enforcement for it: it has no rules table, and no case or part checks that a case exists before a guidance fix (verified, reading the page and `python3 ws.py rules`). The new sentence gives the reason for the must but adds nothing that holds it. | known defect, for the docs audit: the page has no rules table, and this rule predates slice B5 |

## Checked with no finding

- step: the sentence is a reason and asks no new action; the bullet's action, turn the failure into a case, is unchanged (verified, `git diff HEAD`).
- trigger: the page's opening paragraph is unchanged and still names what the page is for, a test of the guidance (verified, reading).
- placement: the reason sits beside the rule it explains, on the page that owns the rule; extend the workspace's step 3 links that section rather than restating it (verified, reading). The kit's seed, `kit/seed/evals-README.md`, keeps the bullet without the reason; it is seeded once into an instance, not synced, so the two do not contradict (verified, `kit/kit.json`).
- eval-case: the sentence asks no new behavior of an agent, and the page is not in any arm, so no eval case reads it (verified, the `grep` above).
