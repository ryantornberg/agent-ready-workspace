---
kind: record
last-reviewed: 2026-11-22
covers: docs/playbooks/escape-analysis.md
reviewed-at: f757aed, with the uncommitted change of the B3 builder
---

# Instruction review: docs/playbooks/escape-analysis.md

This records the sweep review of escape analysis after B3's fix round linked the new records, for its author and the plan's owner.

**In short:** 3 findings, 1 blocking: 1 step, 1 contradiction, 1 placement. Step 9 does not say where a fix record's analysis is committed, the page still knows only two places a review is on record, and step 9 restates procedure endings' marking rule.

## Scope

In scope: the fix round's change, read with `git diff -- docs/playbooks/escape-analysis.md`, in the context of the whole page. The change links the defect register in the "Deferred then lost" owner and in step 3, adds the lessons-log row to step 7, rewrites step 8 for waiting lessons, and sends step 9's analysis to the fix record. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/instruction-review.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/authoring.md`, B3's row and its 2026-11-22 entries in the M3 plan, `docs/templates/fix-record.md`, `docs/templates/defect-register.md`, `docs/templates/lessons-log.md`, `docs/records/defects.md`, `docs/records/lessons.md`, and `docs/playbooks/review-orchestrator.md` with its diff. Read `parts/claim_marks.py` and ran its `claim_lines`. Ran `python3 ws.py check`, which passes with one warning on fix a bug's eval record.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | Steps, step 9 | Blocking. Step 9 writes the analysis into the fix record's "Escape analysis" section, then says "Commit either as procedure endings says". Escape analysis starts once the fix is committed, not merged, and the fix record template commits the record on the fix's branch. Procedure endings' "Where the commit goes" puts a change of pages only on main in the main working copy, where that file does not exist yet, or on a worktree's branch. The review orchestrator's "Committing a record about a branch" sends a record about a branch to main instead. The page gives no default among the three. On main, the analysis lands in a new file with no `## Report`, which `claim_marks` refuses. Switching an unmerged branch's checkout to main is the failure the review orchestrator's record judged blocking as its finding 1. Verified: the four pages' text; `claim_lines` returns None for a record with no report section. Inferred: which path an agent takes. | open |
| 2 | contradiction | "Where a code review is on record today"; Steps, step 2 | Not blocking. The table says a code review is on record "in one of two places": a pull request, or a hand-off plan's "Results". Step 2 reads reviews "as the table above says" and lists ranges with `git grep -n "^Range:" -- docs/plans`. The review orchestrator's step 10 now also writes rounds to a fix record's "Reviews" section and to pages in `docs/records/reviews/`. Step 9 now links the fix record, whose "Reviews" section the page never reads. A fix on the fix a bug path reviewed before its pull request opens is missed, and step 2 stops with "merged with no review on record". Verified: both pages' text. Inferred: the wrong stop. | open |
| 3 | placement | Steps, step 9; Rules table, last row | Not blocking. Step 9 links procedure endings for the commit but restates its report rule, "Mark each claim verified or inferred", and names no push, which procedure endings' order runs after the commit. The Rules table restates the same rule with `eval:fix-a-bug`. The page is edited now, so the instruction review's rule that an older page switches to the link when next edited applies. Verified: the page and procedure endings' "The order" and "The report". | open |

## Checked with no finding

- trigger: the purpose line, **In short** line and "When it runs" are unchanged and still match what the page does; the lessons log template names this page as one of its two sources. Verified.
- enforcement: the new same-commit rule for a lessons-log row is held on the lessons log template, which this step links, as a `prose` row; the page adds no must of its own without a tag. Verified with `python3 ws.py rules`.
- eval-case: the page is `proof: unproven` with `prove-by: M6`, so the new steps need no eval case yet. Verified from its front matter.
