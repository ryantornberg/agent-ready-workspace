---
kind: record
last-reviewed: 2026-11-21
covers: docs/orchestration.md
reviewed-at: 166bbc7, with the uncommitted change of slice B1
---

# Instruction review: docs/orchestration.md

This records the instruction review of the B1 edits to the orchestration page, for its author and for agents who delegate work.

**In short:** 1 finding: 1 contradiction. The new stakes line and fix-round limit hold, but one new worker example falls in the mechanical tier's own definition.

## Scope

In scope: the edited Worker row, the new stakes bullet, the edited unattended-run limit and the two edited rules rows, read against the whole page. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/changing-the-machinery.md`, `docs/playbooks/instruction-review.md`, `workspace.json` and `docs/templates/hand-off-plan.md`.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | The three tiers table | The Worker row gives sweeping a page for a pattern as an example. The Mechanical row defines its work as reading, listing and sweeping. Under the rule to pick the cheapest tier that fits, the worker example belongs at mechanical. Verified: read both rows and the rule under the table. | fixed: the worker example is now rewriting a page after its review. |

## Checked with no finding

- step: the anchor `changing-the-machinery.md#what-counts-as-machinery` resolves, and `python3 ws.py check` passes the page's links.
- trigger: the purpose and In short lines are unchanged, and the new stakes line fires for tests, which the machinery table lists.
- enforcement: both edited rules rows are tagged `prose`, and the page says nothing checks that a tier fits the work.
- placement: the stakes line and the fix-round limit belong on the page about tiers.
- eval-case: the page is marked unproven with `prove-by: M4`.
