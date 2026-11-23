---
kind: record
last-reviewed: 2026-11-22
covers: docs/templates/lessons-log.md
reviewed-at: f757aed, with the uncommitted change of the B3 builder
---

# Instruction review: docs/templates/lessons-log.md

This records the instruction review of the new lessons log template, for its author and for agents changing a page after a mistake.

**In short:** 3 findings, none blocking: 2 contradiction, 1 step. The two procedures the page names still say the log is planned, escape analysis records its lesson after the change is committed, and a change queued for a later batch leaves its lesson nowhere.

## Scope

In scope: the whole page, which is new, with the log file it describes, `docs/records/lessons.md`, read beside it. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/instruction-review.md`, `docs/procedure-endings.md`, `docs/layout.md`, `docs/reader-standard.md`, `docs/authoring.md`, and B3's row and the 2026-11-22 entries naming B3 in the M3 plan. Read the pages it links: `docs/maintain-the-workspace.md` (its event table and "When a duty falls due"), `docs/playbooks/escape-analysis.md` and `docs/research-ladder.md` ("Offer to write a finding down"), and beside them `docs/templates/spec.md`, `docs/records/README.md`, `docs/records/defects.md` and `docs/question-log.md`. Ran `python3 ws.py check` (passes, with one warning on fix a bug's eval record) and `python3 ws.py rules`.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | "When to add a row" | Not blocking. The page says two procedures end with such a change, and that the commit making it adds the row. Both pages still say the log does not exist. Maintain the workspace's row "The same mistake shows up twice" says "The lessons log for such mistakes is planned in slice B3 of M3; until then, write the lesson into the rule's text or the part's `why`". Escape analysis's step 8 says "The lessons log, planned in slice B3 of M3, gets a row once it exists. Until then, write the lesson in one line in the report." Neither page changes in this batch, so an agent following either writes no row. Verified: read both pages; `git status` shows neither modified. | fixed: maintain the workspace's row and escape analysis's step 8 now link the log instead of calling it planned |
| 2 | contradiction | Rules table, first row; "When to add a row" | Not blocking. The page's rule is that a row goes in only in the same commit as the change, and a lesson with no change is not logged. Escape analysis applies and commits its changes at step 7, each by its own route, and records the lesson at step 8, after them. Its step 8 also adds a row whatever step 7 applied, while a proposal waiting on the person's yes changes nothing. Once its "planned" text is cleared, an agent following escape analysis adds the row in a later commit, or for a change never made. Verified: read escape analysis steps 6 to 8. Inferred: that step 8's order survives the edit that clears finding 1. | fixed: escape analysis's step 7 now adds the row in the commit that applies each change, and step 8 adds none for a change not applied |
| 3 | step | "When to add a row" | Not blocking. There is no default for a change that is queued instead of made. Maintain the workspace's step 4 says a change to a file the eval covers, such as `INDEX.md` or `AGENTS.md`, is not made but listed for the maintainer to batch; a hashed page's edit goes to the M3 plan's slice Z queue. Then no commit carries the row, and the page says a lesson with no change behind it is not logged. When the batch lands, nothing tells its author to add the lesson. Verified: read maintain the workspace's step 4. Inferred: the lesson is then lost. | fixed: the page now says a queued change's queue line carries the lesson, and the commit that later makes the change adds the row, with a rules row |

## Checked with no finding

- trigger: the purpose line and **In short** line state what the log holds and when a row is added; the templates index and records README rows agree with them. Verified.
- enforcement: both musts, the same-commit rule and add-only rows, have rows tagged `prose`, which is true; no part reads `docs/records/lessons.md`. Verified with `ws.py rules`.
- placement: committing links [procedure endings](../../procedure-endings.md#the-commit) rather than restating it. Verified.
- eval-case: the behavior lands in maintain the workspace (unproven, `prove-by: M5`) and escape analysis (unproven, `prove-by: M6`), not on a proven page. Verified from their front matter.

## Re-check

A fresh session re-read the page on 2026-11-22, after the fix round.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | Maintain the workspace's row "The same mistake shows up twice" and escape analysis's steps 7 and 8 link the log and no longer call it planned. Verified: `git diff` of both pages. |
| 2 | fixed | Escape analysis's step 7 adds the row in the commit that applies each change; step 8 adds none for a change not applied, and carries the lesson on the change's report or queue line. Verified: `git diff` of escape analysis. |
| 3 | fixed, with one gap: see Broke | The page now says a queued change's queue line carries the lesson, with a rules row tagged `prose`. Verified: the page and `python3 ws.py rules`. |

Broke:

- Not blocking. The fix to finding 3 names "the maintainer's batch of edits the eval covers" as a queue whose line carries the lesson. Maintain the workspace's step 4 keeps no such queue: it lists the edit "in your report for the maintainer to batch". The lesson then lives only in one session's reply, and nothing tells the person making the batch to add the row. Verified: both pages' text. Inferred: the lesson is lost.

Missed: none.
