---
kind: record
last-reviewed: 2026-11-22
covers: docs/extend-the-workspace.md
reviewed-at: f757aed, with the uncommitted change of the B3 builder
---

# Instruction review: docs/extend-the-workspace.md

This records the review of B3's fix-round sweep of step 4, for its author and for anyone adding a page.

**In short:** 2 findings, none blocking: 1 contradiction, 1 placement. Steps 7 and 8 still restate procedure endings, and a rules row says every tag names a part.

## Scope

In scope: the two lines the fix round changed in step 4, shown by `git diff -- docs/extend-the-workspace.md`, read in the context of the whole page. The first adds a bullet linking the style guide. The second lets a rules-table tag name an eval case as `eval:<case>`.

Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/instruction-review.md`, `docs/procedure-endings.md`, `docs/authoring.md`, `docs/reader-standard.md`, `docs/layout.md`, `docs/question-log.md` and its diff, `docs/maintain-the-workspace.md`'s step 4, and B3's row and the 2026-11-22 entries naming B3 in the M3 plan. Ran `python3 ws.py check` in the worktree: exit 0, with one unrelated `eval_record` warning on fix a bug.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | placement | Steps, steps 7 and 8; Rules, the last two rows | Not blocking. The page was edited in this round, so by the instruction review's placement rule it now links [procedure endings](../../procedure-endings.md) instead of restating it. Step 7 still restates staging by name. Step 8 restates the report's claim marks and the question-log entry, and the last two rules rows repeat them. The copy has drifted. It has no push step and no outward-write step. It commits at step 7 and logs the question at step 8, after the commit, where procedure endings logs it before. Verified, by reading both pages. | open |
| 2 | contradiction | Rules, the row "A rules-table tag names a part the manifest uses" | Not blocking. Step 4 now names three kinds of tag: a part and a case, an eval case as `eval:<case>`, or `prose`. The rules row says a tag names a part, and the page's own last row is tagged `eval:fix-a-bug`. The row means "a tag that names a part names one the manifest uses". Verified, by reading. | open |

## Checked with no finding

- step: the new link resolves, since `python3 ws.py check` passes with the `links` check. The `eval:<case>` form matches the contract's `eval:fix-a-bug` tag. Verified.
- trigger: the purpose sentence and the **In short** line are unchanged and still fit; the change adds no route. Verified.
- enforcement: the new bullet is a pointer, not a must or a never, and the tag sentence already sits under the "Every must and never … with a true tag" row. Verified.
- eval-case: the page is unproven with `prove-by: M5`, and no eval case covers it. Verified, with `covered()` over the three cases.
