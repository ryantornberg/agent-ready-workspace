---
kind: record
last-reviewed: 2026-11-21
covers: docs/size-the-work.md
reviewed-at: 9f3de36, with the uncommitted change of the B2 builder
---

# Instruction review: docs/size-the-work.md

This records the instruction review of batch 3's edits to the size-the-work page, for its author and for agents building a feature.

**In short:** 2 findings: 2 step. Step 5 now hands review to the review orchestrator, but nothing makes its input match the orchestrator's committed tip, and an incomplete review has no branch.

## Scope

In scope: the batch 3 edit to "The feature ladder", steps 5 and 6, which replace the by-hand review and impact check with links to the review orchestrator and impact analysis, and anything on the page it contradicts or leaves stale, including "The four phases" and "Rules". Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/orchestration.md` (with its batch 3 diff), `docs/layout.md`, `docs/glossary.md`, the linked pages review orchestrator, impact analysis, test first, fix a bug and the hand-off plan template, and the other batch 3 pages (reuse checklist, escape analysis, architecture review, the playbook catalog diff). Ran `git diff docs/size-the-work.md`, `grep -n -i commit` over the template, test first, size the work, the definition of done and orchestration, and `python3 ws.py check` (no finding on this page).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | "The feature ladder", step 5 | Step 5's input is "the built slices", but nothing on the ladder commits them: step 4 and test first end with the suite passing and a report, and the hand-off plan template leaves "where commits go" to each plan. The review orchestrator reviews commits only: its step 1 takes the tip as `git rev-parse HEAD` and the range `BASE..TIP`, and its step 3 makes a worktree at the tip when tracked changes exist, "so the review reads the commit and not the edits". Uncommitted slices are therefore left out of the review, with no default saying to commit them first. Verified: read the three pages and grepped them for "commit". Cause: `brief-silent-on-linked-contract` — the step pass asks each step to name its input, but not to check that what it hands a linked playbook matches that playbook's input. | fixed: step 5 now commits each built slice, staged by name, before the review, since the orchestrator reads commits. |
| 2 | step | "The feature ladder", step 5 | The review orchestrator can end with dimensions not complete (its step 7 records them in a `Not complete:` line and goes on), or stop at its pre-pass on a new build error. Step 5's output covers only findings fixed, deferred or declined, and sends back to step 4 only on a finding. It gives no branch for an incomplete review or a pre-pass stop: whether to go on to step 6, rerun, or halt and report. Verified: read step 5 and the orchestrator's steps 4, 7 and 10. Cause: `brief-silent-on-linked-contract` — the step pass reads the calling step alone, so the linked playbook's incomplete and stopped outcomes were never mapped to a branch here. | fixed: step 5 now sends a pre-pass stop back to step 4's fix and a new review, and halts and reports on a dimension still not complete, without going on to step 6. |

## Checked with no finding

- contradiction: step 5's claims (one fresh driver-tier session per dimension, no author reasoning, machinery planned for M4 and done by hand until then) match the review orchestrator's "In short", "What exists today and what is planned" and dimensions table, and "fresh context for critics". Step 6's ranked list and "each caller you looked at and each one you did not" match impact analysis's step 6 and the definition of done's impact row. The "Rules" row on a fresh session still holds.
- trigger: step 5's and step 6's links each name their condition (the review step, the impact check); the review orchestrator's "When it runs" and impact analysis's "When it runs" each list this step as a route in.
- enforcement: the edit adds no must or never; the existing `prose` row on a fresh review session still covers step 5.
- placement: the links replace restated procedure with a pointer, which is where the detail belongs.
- eval-case: the feature ladder is marked `Proof: unproven, prove-by M9.`, so the new behavior needs no case yet.
