---
kind: record
last-reviewed: 2026-11-21
covers: docs/changing-the-machinery.md
reviewed-at: 9f3de36, with the uncommitted change of the B2 builder
---

# Instruction review: docs/changing-the-machinery.md

This records the review of batch 3's one-sentence edit to the machinery page, which routes review comments to the feedback walk-through.

**In short:** 1 finding: 1 trigger. The new sentence sends every reviewer comment to the walk-through, which applies only when the pull request's author is present and asks to go through the comments.

## Scope

In scope: the sentence added to step 5 of "The path for a machinery change", read with `git diff docs/changing-the-machinery.md`, and anything on the page it contradicts or leaves stale. Read beside it: the whole page, `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md`, `docs/playbooks/feedback-walkthrough.md`, the batch 3 diff of `docs/playbooks/README.md`, and `docs/playbooks/instruction-review.md`. Commands run: `python3 ws.py rules` and `python3 ws.py check` (exit 0, one unrelated `eval_record` warning).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | The path for a machinery change, step 5 | The sentence fires on any reviewer comment: "When a reviewer leaves comments on it, go through them with the author". The walk-through fires only when the author wants to go through the comments, and is written "for an agent working with the author present". In this repository an agent opens, publishes and merges machinery pull requests itself, and the orchestration page's "Limits" allow unattended runs. With no author present, the walk-through's defaults skip every item and commit nothing, and step 6 then merges once CI is green, with the comments unaddressed. The sentence names no condition for the author's presence and no path without it. Verified: read both pages; the unattended merge is inferred. Cause: brief-route-in-condition-unmatched — the brief asks a route-in sentence to name a condition, but not to match the target page's own "When to use it". | fixed: the sentence now fires only when the author is present, and with no author the comments go in the report and step 6 does not merge, with a prose row in the rules table. |

## Checked with no finding

- contradiction: "in a team's workspace, a person does" for the push matches the walk-through's "In a team's workspace, a person pushes". The walk-through's new commits, never amended or squashed, agree with this page's rule that every merge is a merge commit. Verified.
- step: the link `playbooks/feedback-walkthrough.md` resolves, and `python3 ws.py check` reports no `links` finding. Verified.
- enforcement: the sentence holds no must or never, so it needs no row; the page's rules table is unchanged and `python3 ws.py rules` lists its tags. Verified.
- placement: a machinery change is the one kind of change here that goes through a pull request by rule, so this page is where its reviewer comments arrive. The sentence links the walk-through rather than restating it. Verified.
- eval-case: the page is `proof: unproven` with `prove-by: M4`, and the walk-through it points to is unproven with `prove-by: M6`. Verified.
