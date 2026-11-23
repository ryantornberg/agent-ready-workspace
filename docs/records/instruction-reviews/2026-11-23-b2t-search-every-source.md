---
kind: record
last-reviewed: 2026-11-23
covers: docs/playbooks/search-every-source.md
reviewed-at: 18eccc5, with the uncommitted change of the B2t builder
---

# Instruction review: docs/playbooks/search-every-source.md

This records the instruction review of slice B2t's change to the federated search playbook, for its author and for agents searching outside sources.

**In short:** 3 findings: 1 trigger, 1 step, 1 placement. None is blocking.

## Scope

The change is `git diff fad9f23 -- docs/playbooks/search-every-source.md`: the title, the purpose line and the In short line, the paragraph on tracker operations in "When to use it", the question-log sentence after "Steps", the report's last line, and the question-log row of "Rules". In scope: that changed text, and anything on the page, or on a page it links to, that the change contradicts or leaves stale.

Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/procedure-endings.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/changing-the-machinery.md`, `docs/parts.md`, `docs/research-ladder.md`, `docs/question-log.md`, tracker operations, git-host operations, the playbook list, the glossary, and the plan's B2t rule on standard titles. Searched the repository for every link to `search-every-source.md`. Ran `python3 ws.py check` (no error; one unrelated eval_record warning).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | Title, with the routing rows of git-host operations and tracker operations | Not blocking. The page is now titled "Federated search", and the playbook list says so. The text that routes agents here still uses the old title as the link's name: git-host operations' and tracker operations' "which page wins" tables, the research ladder's sentence on outside sources, the glossary's "Outside source" row and the spec template. The plan's B2t rule keeps a coined term only as a search alias. The links resolve and the page says "Also called searching every source", so routing still works. Verified by searching the repository for `search-every-source.md`. | fixed: the link text on the five pages now reads federated search. |
| 2 | step | "When to use it", the paragraph on tracker operations | Not blocking. The new exception fires "when that read fails, or the person does not paste the item as its step 2 asks". In tracker operations, a failed read in step 1 is what sends step 2 to ask for the paste. Read with "or", a failed read alone lets the agent skip that ask and search without the item. Read as one path, it asks first. The page gives no default between the two. Verified by reading this paragraph and tracker operations' steps 1 and 2; how an agent reads it is inferred. | fixed: the exception asks once for the item, as tracker operations' step 2 does, before it carries on. |
| 3 | placement | "Steps", step 5 | Not blocking. The page now links procedure endings for the question-log entry, but step 5 still restates the report rule ("each claim marked verified or inferred as the definition of done says") rather than linking [procedure endings' report](../../procedure-endings.md#the-report). That section also names refusals and anything left uncommitted or unpushed, such as the log row. Verified by reading both pages. | fixed: step 5 links procedure endings' "The report". |

## Checked with no finding

- contradiction: the new exception to tracker operations is labelled as one; the purpose line, the In short line, step 5, the sentence after the steps, the report's "Written:" line and the first rules row all allow exactly one written file, a question-log entry, and agree with procedure endings' "The question-log entry".
- enforcement: no new must or never; the changed rules row stays `prose`.
- eval-case: the page is `proof: unproven`, `prove-by: M8`, so the new exception needs no eval case yet.

## Re-check

A fresh session re-read the page on 2026-11-23 after B2t's fix round, with `git diff fad9f23`, procedure endings, changing the machinery, the contract, tracker operations' steps 1 and 2, and the other five pages of this batch that share the off-`main` rule: architecture review, the review orchestrator, defect escape analysis, git-host operations and tracker operations. `python3 ws.py check` passes, with only the known warning on fix a bug's eval record. In a scratch repository with a local bare remote, `git push origin HEAD:main` from a worktree on a branch holding a code commit and then a question-log commit exited 0 and moved the remote's main to include the code commit.

| # | Verdict | Evidence |
|---|---|---|
| 1 | holds | The five pages the finding named now link the page as "federated search": git-host operations' and tracker operations' tables, the research ladder, the glossary's "Outside source" row and the spec template. The playbook list already did. Verified: `git grep` for `search-every-source.md` outside records, plans and milestones. The page no longer carries an "Also called" line, which the finding counted on for routing. That follows the reader standard's rule, as the red team review and glossary records ask, and leaves the old name to the queued `INDEX.md` row. Verified: the page. |
| 2 | holds | The exception now says, when the tracker read fails, to ask the person once to paste the item, as tracker operations' step 2 does, and with no answer to carry on without it and list the tracker as not reachable. So one path holds, and it has a default. Verified: the text. |
| 3 | holds | Step 5 links procedure endings' "The report". Verified: the text. |

Broke:

- none.

Missed:

- Blocking. The paragraph after the steps logs a question "as procedure endings says", with no exception for a branch other than `main`. Procedure endings commits the row "on the worktree's branch in a worktree", then pushes it with `git push origin HEAD:main`. A search asked for mid-task, from a fix's or a feature's worktree, has an unmerged code branch checked out, so the push carries that code to main with no pull request and no CI. That goes against procedure endings' "never on its main" for code and the contract's draft pull request rule. `direct_push` refuses only machinery paths. Git-host operations' finding 1 was this same chain, marked blocking, and was fixed there; this page got no exception. Verified: the texts of this page and procedure endings' "The commit" and "The push"; the scratch push above. Inferred: that the search runs with a code branch checked out, and that an agent follows procedure endings through to the push. The fix is the exception git-host operations has, or one rule on procedure endings for every procedure.

## Second fix round

The builder's second fix round, on 2026-11-23, under the maintainer's answer to Q42 in the workspace queue, recorded in the M3 plan. Procedure endings gained one rule, under "Off main": a procedure pushes nothing for pages when the branch checked out holds work other than its own pages, and the commits reach main with the branch's pull request. Its own review is in `2026-11-23-b2t-procedure-endings.md`. The re-check found no non-blocking item on this page.

| Item | Disposition |
|---|---|
| Re-check, missed, blocking: the question-log row is committed on any branch and pushed to main | fixed: the paragraph after the steps links procedure endings' off-main rule: on a fix's or a feature's branch, commit the row and push nothing. |

## Second re-check

A fresh driver-tier session re-checked the second fix round on 2026-11-23, narrowly. It read the contract, the instruction review's "The record", the M3 plan's Q42 entry and lane B's stop rule, `git diff HEAD` of the six pages, procedure endings and the six records, and procedure endings' "The order", "The commit", "The question-log entry", "The push" and its new "Off main". `python3 ws.py check` exits 0, with only the known warning on fix a bug's eval record. In a scratch repository with a local bare remote, `git log --format='%h %s' origin/main..HEAD` listed the code commit on a fix branch holding a code commit and then a page commit, so the test finds it off main. On a pages-only worktree it listed only the page commit, and `git push origin HEAD:main` from there put no code on the remote's main. On a fix branch with no code commit yet, it listed only the page commit. The record the round names for procedure endings, `2026-11-23-b2t-procedure-endings.md`, is not yet in the worktree (verified, `ls`); that rule is a separate reviewer's.

| Item | Verdict | Evidence |
|---|---|---|
| Re-check, missed, blocking: the question-log row is committed on any branch and pushed to main | upheld | The paragraph after the steps now says that on a fix's or a feature's branch you are off main, linking procedure endings' `#off-main`: commit the row and push nothing. Procedure endings agrees in "Where the commit goes" and its push table. So the row's push no longer carries the branch's code to main. Verified: the texts; the anchor resolves and `ws.py check` passes; the scratch test lists the code commit on a fix branch. |

Broke:

- Not blocking. The paragraph after the steps names the case by the branch, "a fix's or a feature's branch"; procedure endings decides by its test. On a fix's branch with no commit of its own yet, the test lists only the row, so procedure endings pushes it with `git push origin HEAD:main`, while the page says push nothing. On a machinery change's branch the page is silent, but its log step leads to procedure endings' push, whose test finds the branch off main. Both gaps are safe: no code reaches main either way. Verified: the texts; the scratch test on a fresh fix branch. Inferred: that the push from there carries only the row, from the log it printed.

Missed:

- Not blocking. Git-host operations, a page of this batch that holds the same shared rule, was not swept. Its step 7 and its rules row still say, "by exception to" procedure endings, that off `main` the row is left uncommitted and its text given in the report. Procedure endings now says that off main the row is committed on the branch checked out and nothing is pushed. Its "not `main`, such as a pull request's branch" also catches a pages-only worktree, which procedure endings says is not off main. Lane B's stop rule says a fix to a shared rule sweeps every page holding it. Neither path carries code to main. Verified: `grep` of git-host operations and procedure endings; the plan's stop rule.

## Known defects

The plan allows the page no further fix round, so the second re-check's non-blocking items stay here.

- Second re-check, broke: the paragraph after the steps named off main by the kind of branch while procedure endings decided by a commit test. Procedure endings' own fix round, after this re-check, made off main a matter of the branch checked out, as this page says, so the two now agree; the procedure endings record holds it.
- Second re-check, missed: git-host operations still leaves the question-log row uncommitted off `main`; see tracker operations' record. For M8.
