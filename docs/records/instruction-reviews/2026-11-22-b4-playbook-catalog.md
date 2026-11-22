---
kind: record
last-reviewed: 2026-11-22
covers: docs/playbooks/README.md
reviewed-at: 31f9aaa, with the uncommitted change of the B2 builder
---

# Instruction review: docs/playbooks/README.md

This records the instruction review of batch 4's edit to the playbook catalog, for its author and for critics.

**In short:** 3 findings: 1 contradiction, 2 trigger. "Before you pick one" still names safe refactor as the one exception and routes every change request to the size gate, which the new pages and rows no longer match; the prompt retrospective row drops its cadence.

## Scope

In scope: the batch 4 edit (the catalog's order line, which adds the Upkeep and Any stage stages, and the five new rows) and anything on the page it contradicts or leaves stale, chiefly "Before you pick one" and "Rules". Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md`, `docs/size-the-work.md`, and every page of batch 4, each new row checked against the page it routes to (docs audit, prompt retrospective, search every source, tracker operations, git-host operations), plus extend, maintain, adopt and machine self-check. Ran `git diff docs/playbooks/README.md`, `python3 ws.py check` (no finding on this page), and the docs audit's unrouted-playbook loop (every playbook has a row). Compared each row's Proof cell with the page's front matter (all match).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | "Before you pick one" | The paragraph says a small change goes straight to fix a bug, "whether or not it is a bug", and that safe refactor "states the one exception". Batch 4's extend the workspace, "Steps" step 1 and "What this page covers", states a second labelled exception: a page-only change that passes the gate follows extend, not fix a bug. Maintain, docs audit, search every source, git-host operations and machine self-check all route a page-only fix there. Both cannot hold. Verified: read this paragraph and extend's step 1, and grepped the batch pages for their extend routes. Cause: `exception-restatements-not-swept` — the sheet's section 2 queues only the contract's "How work flows" edit for slice Z, and names no other page that restates that routing, so the catalog's paraphrase of it was left as it was. | fixed: the paragraph now names two exceptions, safe refactor for a small refactor and extend the workspace for a small change to pages only. |
| 2 | trigger | "Before you pick one" | "A request to change something first goes through the size gate", and the paragraph's list of requests that skip it names no outward write. A request such as "move my ticket to review" or "open a draft for this branch", which the new Any stage rows send to tracker or git-host operations, reads as a change and is sent to the gate first. The gate's "Easy to reverse" fails on "a message sent", so the write climbs the ladder, or passes and lands on fix a bug. Neither operations page mentions the gate for its own writes. Verified: read this paragraph, `docs/size-the-work.md` "The gate" and both operations pages' "When to use it". Inferred: that an agent reading top-down misroutes. Cause: `orchestrator-edits-outside-passes` — the orchestrating session added the Any stage rows and the order line from builders' reports, and no pass re-reads the catalog's own routing paragraph against the new rows. | fixed: the paragraph now says a request for a tracker or git-host write skips the gate and goes to its row, whose page says which writes need a yes. |
| 3 | trigger | "The catalog", Upkeep row for prompt retrospective | The row gives no cadence, while the page's "When it runs" says it runs once per milestone before the record is signed off, and on maintain's events, such as a session that went sideways. The docs audit row beside it names its cadence, so an agent closing a milestone from the catalog finds only the audit. Verified: read the row, the page's "When it runs" and maintain's "Periodic duties". Cause: `one-line-row-narrows-trigger` — the brief asks for a one-line "when to use it" row and never asks that it carry the page's cadence and events. | fixed: the row now names its cadence, once per milestone before sign-off or after an event the maintain page lists, as the docs audit row does. |

## Checked with no finding

- step: the page has no steps; the order line's two new stage sentences name what each stage holds.
- enforcement: the "Rules" table's two rows are still true after the edit; the unrouted-playbook loop finds no playbook without a row.
- placement: the new rows sit in the stages the sheet's section 8 sets, after "After the fix"; no procedure step is restated in a row.
- eval-case: the page is a reference and not covered by the eval (the `eval_record` entry in `workspace.json` names only proven playbooks); the five pages it routes to are unproven with a `prove-by`.

## Re-check

A fresh session re-read the page on 2026-11-22, after the fix round.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | "Before you pick one" now names two exceptions, safe refactor and extend the workspace for a small change to pages only, matching extend's step 1; verified by reading both. |
| 2 | fixed | "Before you pick one" now sends a tracker or git-host write straight to its row, and both operations pages carry "Which writes need a yes"; verified by reading. |
| 3 | fixed | The prompt retrospective row now gives once per milestone before sign-off, a maintain event, or on request, matching the page's "When it runs" and maintain's periodic duties; verified by reading. |

Broke:
- "Before you pick one", the new git-host sentence: it justifies skipping the gate with "it changes no file", but git-host operations covers pushing a branch and publishing and merging, which change the target branch's files. Inferred, from reading git-host operations' operations table.

Missed: none.
