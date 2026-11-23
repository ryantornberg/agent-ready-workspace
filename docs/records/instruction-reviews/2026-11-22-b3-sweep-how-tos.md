---
kind: record
last-reviewed: 2026-11-22
covers: docs/how-tos.md
reviewed-at: f757aed, with the uncommitted change of the B3 builder
---

# Instruction review: docs/how-tos.md

This records the review of B3's fix-round rows for the style guide and the reader standard, for their author and for anyone routing a task.

**In short:** 3 findings, none blocking: 2 trigger, 1 contradiction. The style guide row reads as exempting older pages, and the new templates index has no row.

## Scope

In scope: the two rows the fix round added to "Changing the workspace", shown by `git diff -- docs/how-tos.md`, read in the context of the whole page.

Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/instruction-review.md`, `docs/procedure-endings.md`, `docs/authoring.md`, `docs/reader-standard.md`, `docs/layout.md`, `docs/templates/README.md`, and B3's row and the 2026-11-22 entries naming B3 in the M3 plan. Ran `python3 ws.py check` in the worktree: exit 0, with one unrelated `eval_record` warning on fix a bug.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | Changing the workspace, the style guide row | Not blocking. The Remember cell says "Pages written before 2026-11-22 are not retrofitted." The style guide's "Who it binds" also says "A sentence you write or change on an older page follows it." An agent editing an older page reads the row as exempting it, and skips the guide. Verified, by reading both. | open |
| 2 | contradiction | Changing the workspace, the reader standard row | Not blocking. The row fires for a template "or a copy of one", and its Remember cell says to "give one worked example". The reader standard's "The shape" rule 4 asks that of the template only. A writer of a bug report or pull request description following the row adds an example to the copy. The reader standard's first rules row says the same, and its record notes it. Verified, by reading. | open |
| 3 | trigger | The whole page; Rules, the first row | Not blocking. The new [templates index](../../templates/README.md) is a reference page a reader goes to for a task: "For anyone about to write a plan, a record or a standard text." This page has no row for it, though its first rule asks for one in the same commit as the page. Verified: the page links two templates and never `templates/README.md`. | open |

## Checked with no finding

- step: both links resolve, since `python3 ws.py check` passes with the `links` check, and each Proof cell is "reference", as both pages' front matter gives. Verified.
- enforcement: the rows state no new must or never; the page's two rules rows are unchanged and still `prose`. Verified.
- placement: each Remember cell is a one-line reminder and the row links the owning page. Neither restates a rule procedure endings states. Verified.
- eval-case: an index asks no behavior beyond choosing a row, and no eval case covers it. Verified, with `covered()` over the three cases.
