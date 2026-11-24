---
kind: record
last-reviewed: 2026-11-24
covers: docs/templates/fix-record.md
reviewed-at: fca7d9b, with the uncommitted change of the slice Z builder
---

# Instruction review: docs/templates/fix-record.md

This records the instruction review of slice Z's change to the fix record template, for its author and agents writing a fix record.

**In short:** 3 findings, none blocking: 1 contradiction, 1 step, 1 enforcement.

## Scope

In scope: the whole page, with most attention to the diff from d2aa593: the In short line, the skeleton's `## Brief` placeholder and the "Filling it in" bullet for the brief, which now say every fix fix a bug takes has a brief, in that page's ten parts. Read beside it: `AGENTS.md` and `CLAUDE.md` with their uncommitted change, `INDEX.md`, `docs/playbooks/fix-a-bug.md` (its steps and "The fix path's gates"), `docs/definition-of-done.md` with its change, `docs/safe-refactor.md`, `docs/extend-the-workspace.md`, `docs/procedure-endings.md`, `docs/playbooks/escape-analysis.md` (step 9), `docs/templates/README.md`, `docs/records/README.md`, `docs/layout.md` (page kinds), `evals/arms.json`, the three eval cases' diffs, and `parts/claim_marks.py`. Ran the check's `claim_lines` and `MARKED` in a scratch script on a record with no `## Brief` section. `python3 ws.py check` reports no finding on this page.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | Skeleton, `## Brief`; "Filling it in", the brief bullet | Not blocking. Both say to record "any change to it after approval" under a dated line. Fix a bug, which now defines the brief, has no approval of it: with nothing blocked the agent carries on with step 1, and with something blocked it stops and reports. The word "approv" does not appear on fix a bug. An agent cannot tell which changes to the brief need a dated line, or from when. Verified: a search of `docs/playbooks/fix-a-bug.md`. Inferred: the phrase is left from the earlier text, written before the brief was defined. | fixed: the brief takes any later change under a dated line; no approval is named |
| 2 | enforcement | "Filling it in", the brief bullet; Rules table | Not blocking. The changed text makes the brief required: "Every fix that page takes has one", and the skeleton no longer says to delete the section. The rules table has no row for it, and no check holds it: `claim_marks` reads only `## Report`. A scratch record with no `## Brief` section and a marked report gave no unmarked claim line and a report section, so it passes. Verified: the scratch run and `parts/claim_marks.py`. | fixed: the rules table now holds the brief's section, tagged `prose` |
| 3 | contradiction | Skeleton; "Filling it in", the report bullet | Not blocking. Fix a bug's step 6, changed in slice Z, says that when the fix is to code a review covered, defect escape analysis runs and "its section goes in the same fix record". This page's skeleton has no such section, and it says the report is the record's last section. Escape analysis's step 9 says that outside a plan "the report is the only copy", and names no fix record. An agent cannot tell where the section goes, and the two playbooks disagree on whether it is written at all. Verified: fix a bug, step 6; escape analysis, step 9; this page's skeleton and its rules row "The report is the record's last section". | fixed: fix a bug's step 6 no longer puts the escape analysis in the fix record; it runs as its own page says |

## Checked with no finding

- trigger: the In short line, the templates index row ("You start a fix on the fix a bug path"), the records README row and `INDEX.md`'s "A fix record" row all match the changed page. A slice of a hand-off plan still needs no record; fix a bug does not take such slices, since the hand-off plan is for work too big for it, so "every fix that page takes" does not reach them. Verified.
- placement: the brief bullet links fix a bug's "The fix brief" for the ten parts instead of restating them, and the changed text restates no rule procedure endings holds. Verified.
- eval-case: the behavior the change asks, a brief in every fix's record, is owned by fix a bug's "The fix path's gates", marked `Proof: unproven, prove-by M6.` A template carries only `kind` and `last-reviewed`, by layout's page kinds table, so this page cannot carry a proof key of its own. The guided arm in `evals/arms.json` holds no copy of this page, and no grader reads a brief. Verified.
