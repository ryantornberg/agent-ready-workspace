---
kind: record
last-reviewed: 2026-11-22
covers: docs/maintain-the-workspace.md
reviewed-at: f757aed, with the uncommitted change of the B3 builder
---

# Instruction review: docs/maintain-the-workspace.md

This records the sweep review of maintain the workspace after B3's fix round linked the lessons log, for its author and the plan's owner.

**In short:** 3 findings, none blocking: 1 step, 1 contradiction, 1 placement. A lesson for an edit the maintainer batches has no queue to ride, and steps 4 and 5 restate procedure endings and already disagree with it.

## Scope

In scope: the fix round's change, read with `git diff -- docs/maintain-the-workspace.md`, in the context of the whole page. The change rewrites the "The same mistake shows up twice" row to add a lessons-log row in the commit that makes the change. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/instruction-review.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/authoring.md`, B3's row and its 2026-11-22 entries in the M3 plan, `docs/templates/lessons-log.md`, `docs/records/lessons.md`, `docs/playbooks/escape-analysis.md` and `docs/question-log.md`. Ran `python3 ws.py check`, which passes with one warning on fix a bug's eval record.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | "Duties an event sets off", the row "The same mistake shows up twice"; "When a duty falls due", step 4 | Not blocking. The row sends the lessons-log row to the commit that makes the change, by the template. When the rule belongs on `AGENTS.md` or `INDEX.md`, step 4 does not make the change: it lists it "in your report for the maintainer to batch". The template then says the "queue line" carries the lesson, but this page keeps no queue, only one session's reply. Nothing tells the person who later makes the batch to add the row. Verified: both pages' text. Inferred: the lesson is lost. | open |
| 2 | contradiction | "When a duty falls due", step 4 | Not blocking. Step 4 says that when "a check refuses the commit for any other reason, leave the change uncommitted". Procedure endings' "The commit" says to read the refusal, fix what it names and commit again, and to leave files uncommitted only if it is still refused. Verified: both pages' text. | open |
| 3 | placement | "When a duty falls due", steps 4 and 5; Rules table, last two rows | Not blocking. Step 4 restates staging by name and the review trailer, linking commits rather than procedure endings. Step 5 restates the report's verified and inferred marks and the question-log entry. Neither names the push. The Rules table restates both. The page is edited now, so the instruction review's rule that an older page switches to the link when next edited applies. Verified: the page and procedure endings. | open |

## Checked with no finding

- trigger: the changed row fires on the event the lessons log template names for this page, "when the same mistake shows up twice". Verified.
- enforcement: the row adds no must of its own; the same-commit rule is the template's, tagged `prose`, and the row links it. Verified with `python3 ws.py rules`.
- eval-case: the page is `proof: unproven` with `prove-by: M5`. Verified from its front matter.
