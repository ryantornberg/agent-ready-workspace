---
kind: record
last-reviewed: 2026-11-23
covers: docs/playbooks/tracker-operations.md
reviewed-at: 18eccc5, with the uncommitted change of the B2t builder
---

# Instruction review: docs/playbooks/tracker-operations.md

This records the instruction review of slice B2t's change to tracker operations, for its author and for agents asked to act on a ticket.

**In short:** 3 findings: 2 step, 1 placement. None is blocking.

## Scope

The change is `git diff fad9f23 -- docs/playbooks/tracker-operations.md`: the outward-write guard row of "What exists today and what is planned", steps 4, 5 and 7 of "Steps", the opening of "The post-merge security review", and the question-log row of "Rules". In scope: that changed text, and anything on the page, or on a page it links to, that the change contradicts or leaves stale.

Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/procedure-endings.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/changing-the-machinery.md`, `docs/parts.md` (the `outward_write` row and "The parts here"), the case names in `parts/outward_write.cases.json`, `outward-repos.json`, decision 0004's "The outward-write guard", `docs/research-ladder.md`, `docs/question-log.md`, `docs/templates/bug-ticket.md`, and the pages the changed text links to. Ran `python3 ws.py check` (no error; one unrelated eval_record warning).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | "Steps", step 4, with "The post-merge security review", step 1 | Not blocking. Step 4 now runs the review section's steps 1 to 4 before it asks. Those steps end in "go to step 7 of the steps" when the item links no pull request and the person gives no number, or when none is merged. Run from step 4, that exit skips the rest of step 4 and all of step 5. So the other ask-first writes are never asked, and named writes that do not depend on the review, such as a status change the request also names, are never made. Step 5's own rule stops only "a write that depends on it". Before the change the exit fired inside step 5. Verified by reading steps 4 and 5 and the section's step 1; that an agent would drop the unrelated writes is inferred. | fixed: step 4 drops the review's writes and asks about the rest when the review ends early. |
| 2 | step | "What exists today and what is planned", the outward-write guard row | Not blocking. The new row says the guard refuses a gh write to a repository outside `outward-repos.json`, "so it covers a tracker reached through `gh`". Decision 0004 and the parts table also refuse, on every repository, a gh write that acts on an account's projects, and every `gh api graphql` call. The cases show it: `gh project item-add is refused: projects belong to an account`, while `gh project item-list` is a read that goes ahead. So on a GitHub Projects tracker, step 1 finds live mode and every write in step 5 is refused, which the page does not predict; draft mode would fit. Verified by the case names and decision 0004's text; the Projects scenario is inferred. | fixed: the row says every `gh api graphql` call is refused. |
| 3 | placement | "Steps", step 7 | Not blocking. The changed step 7 still restates the report rule ("with each claim marked verified or inferred, as the definition of done says") rather than linking [procedure endings' report](../../procedure-endings.md#the-report), which the page now links only for the question-log entry. Procedure endings' report also names refusals and anything left uncommitted or unpushed; step 7's list does not. Verified by reading both pages. | fixed: step 7 links procedure endings' "The report". |

## Checked with no finding

- contradiction: the review section's new opening and steps 4 and 5 agree on where its steps 1 to 4 run; the section's step 5 still takes "the yeses from step 4"; the new question-log wording matches procedure endings' "The question-log entry" and the question log's own "Adding an entry"; the stop line's "apart from a question-log entry" still holds.
- trigger: the purpose line, the In short line and the routing table were not changed; the change adds no text that decides when the page applies.
- enforcement: no new must or never; the changed rules row stays `prose`, and the guard row claims no tag.
- eval-case: the page is `proof: unproven`, `prove-by: M8`, so the new order of the review needs no eval case yet.

## Re-check

A fresh session re-read the page on 2026-11-23 after B2t's fix round, with `git diff fad9f23`, procedure endings, changing the machinery, the contract, the parts table's `outward_write` row, the `outward_write` case names, and the other five pages of this batch that share the off-`main` rule: architecture review, the review orchestrator, defect escape analysis, git-host operations and federated search. `python3 ws.py check` passes, with only the known warning on fix a bug's eval record. In a scratch repository with a local bare remote, `git push origin HEAD:main` from a worktree on a branch holding a code commit and then a question-log commit exited 0 and moved the remote's main to include the code commit.

| # | Verdict | Evidence |
|---|---|---|
| 1 | holds | Step 4 now says that if one of the review section's steps 1 to 4 ends the review early, the review's writes are dropped from the list and the rest are asked about. So the other ask-first writes and the unrelated named writes go on to step 5. Verified: the text. A wording gap remains; see "Broke". |
| 2 | holds | The guard row now says the guard refuses every `gh api graphql` call on any repository, "which rules out GitHub Projects writes through `gh`". So the page now predicts that a Projects write is refused. Verified: the row and the parts table. The reason it gives is partly wrong; see "Broke". |
| 3 | holds | Step 7 links procedure endings' "The report" and names any refusal. Verified: the text. |

Broke:

- Not blocking. The review section's step 1 still says, twice, "go to step 7 of the steps" when no pull request is given or none is merged. Run from step 4, that jump conflicts with step 4's new "drop the review's writes from the list and ask about the rest". The section's new opening says where its steps run but does not override the jump. An agent can reconcile the two only by reading step 4's "ends the review early" as meaning that jump. Verified: the texts of step 4 and the section's opening and step 1.
- Not blocking. The guard row says `gh api graphql` refusals rule out GitHub Projects writes through `gh`. The ordinary route, `gh project item-add` and its siblings, is not a `gh api graphql` call. The guard refuses it for another reason: projects belong to an account, so the write names no listed repository. The conclusion holds and the reason does not. Verified: the case names `gh project item-add is refused: projects belong to an account` and `a plain GraphQL query is refused`.

Missed:

- Blocking. Step 7 logs a question and commits it "as procedure endings says", with no exception for a branch other than `main`. Procedure endings puts a pages-only commit "on the worktree's branch in a worktree", then pushes it with `git push origin HEAD:main`. This page is often run from a fix's or a feature's worktree, such as to move a ticket to review once its pull request opens. There HEAD is an unmerged code branch, so the push carries its code to main with no pull request and no CI. That goes against procedure endings' "never on its main" for code and the contract's draft pull request rule. `direct_push` refuses only machinery paths. Git-host operations' finding 1 was this same chain, marked blocking, and was fixed there by leaving the row uncommitted off `main`; this page got no such exception. Verified: the texts of step 7 and procedure endings' "The commit" and "The push"; the scratch push above. Inferred: that the page runs with a code branch checked out, and that an agent follows procedure endings through to the push. The fix is the same exception git-host operations has, or one rule on procedure endings for every procedure.

## Second fix round

The builder's second fix round, on 2026-11-23, under the maintainer's answer to Q42 in the workspace queue, recorded in the M3 plan. Procedure endings gained one rule, under "Off main": a procedure pushes nothing for pages when the branch checked out holds work other than its own pages, and the commits reach main with the branch's pull request. Its own review is in `2026-11-23-b2t-procedure-endings.md`. The non-blocking items of the re-check are not fixed in this round; each goes to "Known defects".

| Item | Disposition |
|---|---|
| Re-check, missed, blocking: step 7 commits the question-log row on any branch, and procedure endings then pushes it to main | fixed: step 7 links procedure endings' off-main rule: on a fix's or a feature's branch, commit the row and push nothing. |
| Re-check, broke, not blocking: the review section's "go to step 7" conflicts with step 4's new drop-and-ask | known defect, for M8. |
| Re-check, broke, not blocking: the guard row gives the wrong reason why a Projects write through `gh` is refused | known defect, for M8. |

## Second re-check

A fresh driver-tier session re-checked the second fix round on 2026-11-23, narrowly. It read the contract, the instruction review's "The record", the M3 plan's Q42 entry and lane B's stop rule, `git diff HEAD` of the six pages, procedure endings and the six records, and procedure endings' "The order", "The commit", "The question-log entry", "The push" and its new "Off main". `python3 ws.py check` exits 0, with only the known warning on fix a bug's eval record. In a scratch repository with a local bare remote, `git log --format='%h %s' origin/main..HEAD` listed the code commit on a fix branch holding a code commit and then a page commit, so the test finds it off main. On a pages-only worktree it listed only the page commit, and `git push origin HEAD:main` from there put no code on the remote's main. On a fix branch with no code commit yet, it listed only the page commit. The record the round names for procedure endings, `2026-11-23-b2t-procedure-endings.md`, is not yet in the worktree (verified, `ls`); that rule is a separate reviewer's.

| Item | Verdict | Evidence |
|---|---|---|
| Re-check, missed, blocking: step 7 commits the question-log row on any branch, and procedure endings then pushes it to main | upheld | Step 7 now says that on a fix's or a feature's branch you are off main, linking procedure endings' `#off-main`: commit the row and push nothing. Procedure endings agrees: "Where the commit goes" puts it on the branch checked out, and the push table's off-main row pushes nothing. So the row's push no longer carries the branch's code to main. Verified: the texts; the anchor resolves to `### Off main`, and `ws.py check` passes; the scratch test lists the code commit on a fix branch. |
| Re-check, broke, not blocking: "go to step 7" conflicts with step 4's drop-and-ask | upheld | Listed in "Known defects" for M8, the page's `prove-by`. Verified. |
| Re-check, broke, not blocking: the guard row's reason for refusing a Projects write | upheld | Listed in "Known defects" for M8. Verified. |

Broke:

- Not blocking. Step 7 names the case by the branch, "a fix's or a feature's branch"; procedure endings decides by its test. On a fix's branch with no commit of its own yet, the test lists only the row, so procedure endings pushes it with `git push origin HEAD:main`, while the page says push nothing. On a machinery change's branch the page is silent, but its log step leads to procedure endings' push, whose test finds the branch off main. Both gaps are safe: no code reaches main either way. Verified: the texts; the scratch test on a fresh fix branch. Inferred: that the push from there carries only the row, from the log it printed.

Missed:

- Not blocking. Git-host operations, a page of this batch that holds the same shared rule, was not swept. Its step 7 and its rules row still say, "by exception to" procedure endings, that off `main` the row is left uncommitted and its text given in the report. Procedure endings now says that off main the row is committed on the branch checked out and nothing is pushed. Its "not `main`, such as a pull request's branch" also catches a pages-only worktree, which procedure endings says is not off main. Lane B's stop rule says a fix to a shared rule sweeps every page holding it. Neither path carries code to main. Verified: `grep` of git-host operations and procedure endings; the plan's stop rule.

## Known defects

The plan allows the page no further fix round, so the re-check's non-blocking items stay here.

- Re-check, broke: the review section's step 1 still says "go to step 7" twice, which conflicts with step 4's drop-and-ask when run from step 4. For M8.
- Re-check, broke: the guard row says `gh api graphql` refusals rule out Projects writes; `gh project item-add` is refused because a project names no listed repository. The conclusion holds; the reason does not. For M8.
- Second re-check, broke: step 7 named off main by the kind of branch while procedure endings decided by a commit test. Procedure endings' own fix round, after this re-check, made off main a matter of the branch checked out, as this page says, so the two now agree; the procedure endings record holds it.
- Second re-check, missed: git-host operations still leaves the question-log row uncommitted off `main`, "by exception to" procedure endings, where procedure endings now commits it on the branch and pushes nothing. Neither carries code to main. Git-host operations' record holds it, for M8.
