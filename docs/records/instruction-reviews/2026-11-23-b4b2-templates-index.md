---
kind: record
last-reviewed: 2026-11-23
covers: docs/templates/README.md
reviewed-at: 4190d8d, with the uncommitted change of the B4 slice session
---

# Instruction review: docs/templates/README.md

This records the instruction review of slice B4's second-batch edit to the templates index, for its author and for critics.

**In short:** 1 finding: 1 contradiction, not blocking. The epic satellites row puts the copies "beside the epic folder's hub", where that template puts two of its three shapes inside the hub.

## Scope

In scope: the uncommitted edit to "Lane templates", which adds rows for the standup log and epic satellites templates. Also in scope: how the rows fit the rest of the page, including the epic folder row in "Templates in this folder".

Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/extend-the-workspace.md`, and the pages the new rows link, in full: the standup log template, the standup report, the epic satellites template and the epic folder template. Ran `git diff -- docs/templates/README.md` and `python3 ws.py check`, which reports nothing on this page.

The page has no `## References` heading.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Lane templates, the epic satellites row | Not blocking. The "Your copy goes" cell says "As the page says, beside the epic folder's hub", and the "Use it when" cell says the shapes go "beside its hub". The satellites template's "Where each one lives" puts questions for other teams and the tracker map in the hub, as sections of `README.md`; only the unattended-run plan is a file beside it. A section written as a page beside the hub would break the epic folder's rule that every page there but the hub is a plan. The cell opens "As the page says", so a reader who opens the page gets the place right, and the `page_kinds` check refuses such a page. Verified: the row and the satellites template's table. | fixed: the epic satellites row now places the first two shapes as sections of the epic folder's hub and the run plan as a plan beside it, and "Use it when" drops "beside its hub". |

## Checked with no finding

- contradiction: the standup log row matches its page. "A standup report saves its entry" matches the template's "The standup report writes it; nothing else does." "One file outside every repository" matches its "Where it lives". Both rows' Lane cells match the pages' `lane: product`, and both "First used in" cells match the M9 each page names. Verified: pages read.
- step: the change adds no step. Every new link resolves; the `links` check reported nothing on this page.
- trigger: each "Use it when" cell matches its template's purpose line: the standup report's save, and an epic that needs questions for other teams, a tracker map or an unattended-run plan.
- enforcement: the section's rule that a new lane template adds its row here and a line in its role's path holds for both. Verified: both are on reading paths' product path.
- placement: the rows route only; neither restates a template's shape or rules.
- eval-case: the page is a reference, and lane templates carry no proof keys, as layout's controlled values say. No eval case or arm in `evals/arms.json` reads the page.

## Re-check

A fresh session read the fix round's `git diff -- docs/templates/README.md`, the "Lane templates" table as it now stands, the epic satellites template in full and the epic folder template's naming table and last paragraph of "Filling it in". It ran `grep -rn "beside.*hub" docs` outside records and `python3 ws.py check`, which exited 0 with only the known `eval_record` warning on `fix-a-bug.md`. Verified: the "Lane templates" table keeps five columns on every row, and the epic folder link resolves. Side note, not created by this round: the satellites template's own purpose line still says all three shapes "sit beside an epic's hub", against its own table; reading paths' product item 6 repeats it. Both sit outside this record.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | Verified: the epic satellites row's "Your copy goes" cell now reads "As the page says: the first two as sections of the epic folder's hub, the run plan as a plan beside it", and "Use it when" no longer says "beside its hub". That matches the satellites template's "Where each one lives" table, and the epic folder template's fixed paragraph and new naming row say the same. |

What a fix broke:

- None.
