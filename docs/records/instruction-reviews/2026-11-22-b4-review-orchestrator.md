---
kind: record
last-reviewed: 2026-11-22
covers: docs/playbooks/review-orchestrator.md
reviewed-at: 31f9aaa, with the uncommitted change of the B2 builder
---

# Instruction review: docs/playbooks/review-orchestrator.md

Review of the route-in sentence M3 slice B2, batch 4, added to the review orchestrator, for its author and agents running a review.

**In short:** 1 finding: 1 contradiction. The new sentence reads a tracker request through tracker operations today, but step 5, which reads the request, still says the tracker waits for M8.

## Scope

In scope: the edit to the "What exists today and what is planned" table's tracker row, and anything on the page it contradicts or leaves stale. I read the whole page and its batch diff, and beside it `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md`, `docs/review-in-a-worktree.md`, and the batch pages it touches: `docs/playbooks/tracker-operations.md`, `docs/playbooks/git-host-operations.md` and `docs/playbooks/feedback-walkthrough.md`. I ran `python3 ws.py check`, with no finding on this page.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | What exists today and what is planned, the tracker row; Steps, step 5 | The edited row says that when the request sits on a tracker item, read it as tracker operations says, today. Step 5, which reads the request, still says "M8 plans to read it from the tracker. Until then", and lists only the plan's spec, a GitHub issue and the pull request's description, with the spec as the default. An agent with a tracker tool gets two answers, and no default between the tracker item and the spec. Verified by reading the row and step 5. Cause: route-in-edit-scope-too-narrow — the brief lets a builder edit only the one route-in sentence on an existing page, so the step that the new route changes was left stale and not reported. | fixed: step 5 now lists a tracker item, read as tracker operations says when the session has a tool, with the default order the spec, then the tracker item. |

## Checked with no finding

- Step: the new sentence names its condition (the request sits on a tracker item) and its page, and tracker operations does read a named item without writing when no write is asked.
- Trigger: the edit adds no purpose, In short, routing-table or catalog text, so the page fires on the same requests as before; the page still does not link git-host operations, as the sheet's tie-break says.
- Enforcement: the sentence adds no must or never; the existing rules rows are unchanged.
- Placement: a route to the tracker page belongs in the row on reading the request from a tracker, which is where it sits.
- Eval-case: the page is marked unproven with `prove-by: M6`.

## Re-check

A fresh session re-read the page on 2026-11-22, after the fix round.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | Step 5 no longer says the tracker waits for M8; it lists a tracker item read as tracker operations says when the session has a tool, with the default order the spec, then the tracker item, matching the table row; verified by reading both and the batch diff. |

Broke: none.
Missed: none.
