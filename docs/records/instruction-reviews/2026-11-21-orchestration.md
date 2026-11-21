---
kind: record
last-reviewed: 2026-11-21
covers: docs/orchestration.md
reviewed-at: 166bbc7
---

# Instruction review: docs/orchestration.md

Review of the rules table that M3 sub-batch A added to the orchestration page, for its author and agents that plan or delegate work.

**In short:** 2 findings: 2 contradiction. The tags hold, but two rows disagree with other pages on the driver tier and the fix-round limit.

## Scope

In scope: the rules table under What enforces this, which sub-batch A added, its five rows, each row's tag, and how each row agrees with the rest of the page. I read the whole page and its sub-batch A diff. Beside it I read `AGENTS.md`, `INDEX.md`, `workspace.json`, the `handoff_tier` part and its cases, `wslib/events.py`, `docs/changing-the-machinery.md`, `docs/templates/hand-off-plan.md`, `docs/glossary.md`, and the register from `python3 ws.py rules`. The review is of commit 166bbc7.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | What enforces this, the row on the driver tier | The row puts only gate, contract and outsider-text work at the driver tier, and the page's tier table lists a test harness as worker work. The machinery page's In short line says all machinery work runs at the driver tier, and its list includes `tests/`, `tools/` and `baselines/`. A worker slice that changes `tests/` obeys one page and breaks the other. Verified by reading both pages. | fixed: the driver list now names every machinery path, and the worker examples are no longer machinery. |
| 2 | contradiction | What enforces this, the row on unattended runs | The row fixes the limit at three fix rounds. The Limits section of the hand-off plan template asks each plan to set its own fix-round limit for any unattended run. Neither page says whether a plan may set a different number, so the exception is not labelled. Verified by reading both pages. | fixed: an unattended run stops after its plan's limit, or three when the plan sets none. |

## Checked with no finding

- Step: each row names who acts and when, and the page gives the tier line's form and where the binding lives in `workspace.json`.
- Trigger: the table adds no purpose, In short or index text, and the contract and `INDEX.md` still route delegation here.
- Enforcement: the three `handoff_tier` cases refuse a prompt with no tier, a model off the binding and an effort off the binding. No part checks the three rows tagged `prose`.
- Placement: every row concerns tiers, delegation or run limits, which this page owns. Nothing was added to the always-loaded layer.
- Eval-case: the page is marked unproven with `prove-by: M4`.
