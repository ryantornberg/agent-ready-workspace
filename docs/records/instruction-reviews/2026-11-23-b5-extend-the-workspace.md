---
kind: record
last-reviewed: 2026-11-23
covers: docs/extend-the-workspace.md
reviewed-at: dace91e, with the uncommitted change of the B5 slice session
---

# Instruction review: docs/extend-the-workspace.md

This records the review of B5's edits to step 4 of extend the workspace, on a decision record's front matter and shape, for their author.

**In short:** 1 finding: 1 contradiction, not blocking. The page says a decision record is written only on the three conditions and a person's yes, and always starts proposed; the new template also allows one an approved plan asks for.

## Scope

In scope, from `git diff HEAD -- docs/extend-the-workspace.md`: in "Steps", step 4, the bullet on front matter, its sentence on a decision record, and the bullet that starts "A decision record is written only when". The whole page was read to judge them, its rules table included. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/templates/decision-record.md`, `docs/templates/README.md`, decision interview's section "When a decision gets a record", the front matter of every record in `docs/decisions/`, and `parts/decisions.py`.

Run: `python3 ws.py check` passes with only an `eval_record` warning about `fix-a-bug.md`, so the new links resolve (verified).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | "Steps", step 4, the bullet "A decision record is written only when ..." and the front matter bullet; "Rules", the row "A decision record is written only when the three conditions hold and the person says yes" | Not blocking. This page says a record is written only when the three conditions hold and the person says yes, and that it carries `status: proposed`. The template it now links says: "Only when the three conditions ... hold and the person says yes, or when an approved plan asks for the record", and its rules table says the same (verified). The templates index row says the same (verified). Thirteen records, 0008 to 0020, were written because M3's approved plan asked, with `status: accepted` and `deciders: the maintainer, through M3's approved plan` (verified, their front matter). An agent following this page on such a plan would hold back the record or ask again, and would write it as proposed. Link the template's "When to write one" instead of restating the condition, and say the status is `proposed` unless an approved plan settles it. | fixed: an approved plan that asks for a record is the person's yes, such a record may start at `status: accepted`, and the rules row says the same; the template says it too |

## Checked with no finding

- step: the front matter keys listed, `kind`, `status`, `date`, `deciders` and `last-reviewed`, are the ones the template's "Front matter" requires; its anchor resolves (verified, `links` passes).
- trigger: the page's purpose line names decision records, and the changed bullets sit in step 4, where a writer of one reads.
- enforcement: "which the `decisions` check holds" is true: the part is in `workspace.json` and runs at the commit and in CI (verified, `python3 ws.py list`). The removed sentence, a check "planned in slice B5", is gone now that the check exists.
- placement: the page links the template for the shape, rather than restating it. The one restated rule is finding 1.
- eval-case: the page is marked unproven with `prove-by: M5` (verified, its front matter).

## Re-check

A fresh driver-tier session read the changed passages as they stand, with `git diff HEAD -- docs/extend-the-workspace.md`, beside `docs/templates/decision-record.md` ("When to write one", "Front matter", "Rules"), `docs/templates/README.md` with its diff and the front matter of decisions 0008 to 0020, and ran `python3 ws.py check` (exit 0, only the `eval_record` warning).

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | Step 4 now says "An approved plan that asks for a record is that yes", and its front matter bullet adds "one an approved plan asks for may start at `status: accepted`"; the rules row says the same (verified, reading). The template's "When to write one" and its rules row now use the same words (verified). |

What a fix broke:

- Not blocking. The fix changed the template's wording from "or when an approved plan asks for the record" to "an approved plan ... is that yes", so the three conditions now hold for a plan's record too. The templates index's new row still reads "meets the three conditions ... and the person says yes, or an approved plan asks for a record", the old alternative (verified, reading `docs/templates/README.md`). An agent reading the index may write a record a plan asks for without the three conditions; this page and the template would not (inferred).

What the first reading missed:

- None.

## Known defects

From the re-check, left for later since the plan allows one fix round:

- The templates index's decision record row still reads "three conditions and a yes, or an approved plan asks", where the template and this page now treat the plan as the yes. For the docs audit.
