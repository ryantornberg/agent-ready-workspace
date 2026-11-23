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

## Second fix round

The builder's second fix round, on 2026-11-23, under the maintainer's answer to Q35 in the workspace queue, recorded in the M3 plan. It first cut back: the rule that a review record or a kept handoff note is committed on main from a throwaway worktree is removed, a review round's record goes in the plan's "Results" or the pull request's description, and a kept handoff note waits for M4. Then it fixed the blocking items the re-check found.

| Item | Disposition |
|---|---|
| 1, blocking: step 9 gives no default for where an unmerged fix's analysis is committed | fixed: step 9 writes and commits the analysis where the fix record is, by default the fix's branch while the fix is unmerged, since main holds no copy yet, and main once it has merged. It labels that as the one exception to procedure endings' commit. |
| 2, not blocking: the page knows two places a review is on record | withdrawn by the cut-back: a code review is again on record only in a pull request or a hand-off plan's "Results", the two places the table names. |
| 3, not blocking: step 9 restates the report rule and names no push | not fixed in this round, which Q35 limits to the blocking items. It stays open: a "Known defects" section is written once no fix round is left on the page. |

## Second re-check

A fresh session re-read the page on 2026-11-23, after the second fix round.

It read the page whole, `git show 65a6f5c`, procedure endings, the contract, the fix record template, the review orchestrator, and `workspace.json`'s `direct_push` and `review_trailer` entries. It ran git in a scratch repository with a local bare remote, under its own temp folder.

| Item | Verdict | Evidence |
|---|---|---|
| 1, blocking: step 9 gives no default for where an unmerged fix's analysis is committed | fixed | Step 9 now has a default: the fix's branch while the fix is unmerged, and main once it has merged. It labels the exception: "except that a record on an unmerged fix's branch is committed on that branch". Verified: the text. The exception covers the commit only, and the push it leads to is under "Broke". |
| 2, not blocking: the page knows two places a review is on record | withdrawn-upheld | The review orchestrator's step 10 now writes a round only to the plan's "Results" or the pull request's description, the two places this page's table names. Verified: both texts. |
| 3, not blocking: step 9 restates the report rule and names no push | not fixed | Step 9 still says "Mark each claim verified or inferred" and names no push. Verified. Its disposition says "see 'Known defects'", but this record has no such section. The missing push now matters, under "Broke". |

Broke:

- Blocking. Step 9 commits the fix record on the unmerged fix's branch, then leaves the push to procedure endings, since its exception covers the commit only. What the agent committed is pages only, so procedure endings' push table gives, in a worktree, `git push origin HEAD:main`. HEAD there is the fix's branch, so the push publishes the unmerged fix to main, with no pull request and no CI. That goes against the contract's draft pull request rule and procedure endings' "never on its main" for code under `src/`. The same holds when the fix came from a hand-off plan and the plan is committed in that worktree. The fix record template says to push the record "on that branch". Step 9 links that template only for where the record is, not for the push. No guard stops it for code under `src/`: the pre-push checks are `direct_push`, for machinery paths only, and `review_trailer`, for guidance pages only. Verified in the scratch repository: from a worktree on a branch with a fix commit and a fix record commit, `git push origin HEAD:main` exited 0 and moved the remote's main to include the fix commit. Verified by reading: both parts' configuration in `workspace.json`. Inferred: that an agent picks the row for pages, since that is what it committed. The exception should name the push too: push the fix's branch, as the fix record template's "Committing it" says.
- Not blocking. For a fix in a repository pinned under `src/`, the fix record template says the record is a change of pages only in this workspace, committed as procedure endings' rows for pages say: on main from the main copy. Step 9's default, "while the fix is not merged, that is the fix's branch ... since main holds no copy of the record yet", is wrong for that case. The fix's branch is in the pinned repository, and main here already holds the record. The governing words "where the record is" and the link to "Committing it" lead the agent right. Verified: both texts.
- Not blocking. When the fix came from a hand-off plan, step 9 commits the plan "as procedure endings says". Handoff and the review orchestrator, in the same round, moved this kind of commit to the branch checked out. They did so because a switch to main fails from a branch with uncommitted changes. This page was not swept. The risk is low here, since the page starts only once the fix is committed. Verified: the three texts. Inferred: the likelihood.

Missed: none.

## Revert (Q41)

The builder's revert, on 2026-11-23, under the maintainer's answer to Q41 in the workspace queue, recorded in the M3 plan. No third fix round was made. The page's wording for where and how it commits and pushes went back to main's text; only its pointers to B3's new pages stay changed. Where a review commits on a branch stays unsettled, for M4.

| Item | Disposition |
|---|---|
| Second re-check, broke, blocking: the analysis committed on an unmerged fix's branch is pushed by procedure endings' row for pages to main | withdrawn by the revert: step 9 is main's text again, with its pointer to the fix record removed, since the fix record no longer has an escape analysis section. With a hand-off plan, the analysis goes under its "Results"; otherwise the report is the only copy. |
| Second re-check, broke, not blocking: step 9's default is wrong for a fix in a pinned repository | withdrawn by the revert: step 9 no longer names the fix record or its branch. |
| Second re-check, broke, not blocking: step 9's plan commit was not swept to the branch checked out | withdrawn by the revert: handoff and the review orchestrator went back to main's wording too, so the three pages agree again. |
| Second fix round, item 3, not blocking: step 9 restates the report rule and names no push | deferred to M4, with where a review commits: step 9's commit wording is main's text under Q41. |
| Steps 7 and 8, the lessons-log rows, and the table's defect register row and step 3's pointer | kept as pointer changes: they point at B3's lessons log and defect register in place of "planned in slice B3 of M3". |

## Re-check after the revert

A fresh session re-read the page on 2026-11-23, after the revert under Q41. It read the contract, the instruction review, procedure endings, the Q41 entry under "Changes after approval" in the M3 plan on `origin/main` (the branch does not hold that entry yet), `git diff HEAD` and `git diff origin/main` of the page, the fix record template, the defect register and its template, the lessons log and its template, the spec template's "Which spec", the review orchestrator and handoff. It searched `docs/` outside plans and these records for the fix record's escape analysis section, and ran `python3 ws.py check`, which exits 0 with only the known warning on fix a bug's eval record. Verified.

Against `origin/main`, the page differs in five places: the "Deferred then lost" owner and step 3 link the defect register; steps 7 and 8 add the lessons-log row; and step 9 drops main's "The fix record, planned in slice B3 of M3, will hold this analysis as a section. Until it exists:". From "When the fix came from a hand-off plan" on, step 9 matches main word for word, so no commit or push wording of B3's survives. Steps 7 and 8 say more than a link, but they carry out main's own "gets a row once it exists" and place no commit, so they stay within Q41. Verified: `git diff origin/main`.

| Item | Verdict | Evidence |
|---|---|---|
| Second re-check, broke, blocking: the analysis committed on an unmerged fix's branch is pushed to main by procedure endings' row for pages | upheld | Step 9 no longer names the fix record, its branch or procedure endings, and the fix record template has no "Escape analysis" section. Verified: the diff, the template, and a search of `docs/` that finds no other page sending the analysis to a fix record. |
| Second re-check, broke, not blocking: step 9's default is wrong for a fix in a pinned repository | upheld | Step 9 names no branch. Verified: the text. |
| Second re-check, broke, not blocking: step 9's plan commit was not swept to the branch checked out | upheld | Handoff's step 2, the review orchestrator's step 10 and this step 9 all hold main's wording again, none naming a branch. Verified: the three diffs against `origin/main`. |
| Second fix round, item 3, not blocking: step 9 restates the report rule and names no push | upheld | Step 9 is main's text, and Q41 leaves where a review commits for M4. Verified: the diff and the Q41 entry. |
| Steps 7 and 8, the lessons-log rows, and the table's defect register row and step 3's pointer | upheld | Each replaces a "planned in slice B3 of M3" line. The anchors resolve, the register holds the two tables step 3 names, and the lessons log template names this page as one of its two sources. Verified: `python3 ws.py check`, the register and the template. |

Broke: none.

Missed: none.
