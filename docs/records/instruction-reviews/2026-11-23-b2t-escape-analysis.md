---
kind: record
last-reviewed: 2026-11-23
covers: docs/playbooks/escape-analysis.md
reviewed-at: 18eccc5, with the uncommitted change of the B2t builder
---

# Instruction review: docs/playbooks/escape-analysis.md

This records the instruction review of B2t's change to defect escape analysis, for its author and for any agent recording a review.

**In short:** 2 findings, 1 of them blocking: 1 contradiction, 1 step. The blocking one: step 9 now links procedure endings, and its plan commit, made on an unmerged fix's branch in a worktree, is then carried to main by procedure endings' push for pages.

## Scope

In scope: the changed text, which is the title, the **In short** line's alias and step 9's link to procedure endings; and anything on the page, or a page it links to, that the change contradicts or leaves stale, including what the same change to architecture review and the review orchestrator, both linked from here, leaves stale on this page.

Read: the page whole; `git diff fad9f23` of it and of the two review pages; `AGENTS.md`, `CLAUDE.md`, `INDEX.md`; `docs/procedure-endings.md`; `docs/definition-of-done.md`; `docs/orchestration.md`'s "Limits"; `docs/playbooks/fix-a-bug.md`; the `outward_write` row of `docs/parts.md`; architecture review, the review orchestrator, the defect register template's "When to add a row", `docs/reader-standard.md`'s names rules, the playbook catalog's row, red team review's **In short** line, `workspace.json`'s `direct_push` entry, the record `2026-11-22-b3-sweep-escape-analysis.md`'s "Revert (Q41)" and "Re-check after the revert", and the M3 plan's "Changes after approval" of 2026-11-22 and 2026-11-23. Searched `docs/` for links to the page and for its old title. Ran `python3 ws.py check` in the worktree: it passes, with only the known warning on fix a bug's eval record. In a scratch repository with a local bare remote, ran `git push origin HEAD:main` from a worktree on a task branch holding a code commit and a plan commit.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Steps, step 9 | Blocking. When the fix came from a hand-off plan, step 9 commits the plan with no branch named; the page runs once the fix is committed, often before it merges, so in the fix's worktree the plan lands on the fix's branch. The change links procedure endings from step 9. That page's **In short** and "The order" end every procedure with a commit of every file it wrote and then a push, and for pages only, in a worktree, give `git push origin HEAD:main`, which carries the unmerged fix to main, against procedure endings' "never on its main" for code and the contract's draft pull request rule. `direct_push` stops it only for machinery paths. The record of B3's revert upheld this push's withdrawal because step 9 "no longer names the fix record, its branch or procedure endings"; this change names procedure endings again. The link targets "The report" only, and step 9 names no push, which is why the route is inferred, but the report section itself asks to name anything "left uncommitted or unpushed". Verified: the texts, that record, `workspace.json`'s `direct_push` list, and in the scratch repository the push exited 0 and moved the remote's main to include the code commit. Inferred: that an agent sent to procedure endings runs its order through the push. B2t's row asks for the link, and Q41 left where such a commit goes for M4; reconciling the two is the plan owner's choice. | fixed: step 9 pushes nothing off `main`; the plan commit reaches main with the branch's pull request. A rules row holds it. |
| 2 | step | Steps, step 3 and step 4 | Not blocking. The same change makes architecture review's alternative, on the `fix` path, a follow-up note given only in the session's report, never a finding or a row, and the review orchestrator keeps it out of the record that is copied into the pull request. A defect that such a note pointed at, left alone and later escaped, is a sighting this page cannot find or class: step 3 searches records, plans, milestones, the question log, the git log and the pull request's text, none of which holds a report-only note, and its outcomes are only "never raised, declined, deferred or marked fixed". Verified: the texts of the three pages. Inferred: that a missed follow-up note is a likely kind of sighting. | known defect, for M4: where a review's follow-up notes are kept, so that step 3 can search them, belongs to M4's review machinery. |

## Checked with no finding

- trigger: the new title "Defect escape analysis" follows the reader standard's rule to use the industry's term, and the catalog row in `docs/playbooks/README.md` already shows it. "Also called escape analysis" keeps the old name findable, as red team review does for its old name; the pages that link here with the text "Escape analysis" still route correctly, and no link targets the page's title anchor. Verified: the catalog, a search of `docs/`, and `python3 ws.py check`.
- enforcement: the change adds no must or never; the rules table's tags are unchanged and pass the `rules` check. Verified.
- placement: step 9 still restates procedure endings' commit rule, "stage the plan by name", but that wording is main's text kept under Q41, and the sweep record defers it to M4; the change moves the report rule to a link, as the instruction review asks of an edited page. Verified: the diff and that record.
- eval-case: the page is `proof: unproven` with `prove-by: M6`. Verified: the front matter.

## Known defects

The plan gives lane B one fix round, so this non-blocking finding stays open here.

- Finding 2: a `fix`-path follow-up note from architecture review lives only in a session's report, where step 3 does not search. For M4, whose review machinery decides where such notes are kept.
- Re-check, broke: on a merged branch or one with no pull request, step 9's plan commit never reaches main; the report names it. For M6.
- Re-check, item 2: finding 2 above is kept for M4, not the page's `prove-by` M6, because the plan's Q41 entry leaves where review notes and commits live to M4.
- Second re-check, broke: step 9's "push nothing, for this commit or for any step 7 made, by whatever route" reaches past pages; a machinery or code change from step 7 goes on its own branch with its own pull request. "Every page commit, step 7's included" would match the rule. For M6.
- Procedure endings' re-check: this page still says its commits reach main with the branch's pull request, without procedure endings' "only if the branch is pushed again before it merges". For M6.

## Re-check

A fresh session re-read the page on 2026-11-23 after B2t's fix round, with `git diff fad9f23`, procedure endings, changing the machinery, the instruction review, fix a bug, the size gate, the contract, the M3 plan's Q41 entry and lane B's stop rule, and the other five pages of this batch that share the off-`main` rule: architecture review, the review orchestrator, git-host operations, tracker operations and federated search. `python3 ws.py check` passes, with only the known warning on fix a bug's eval record. In a scratch repository with a local bare remote, `git push origin HEAD:main` from a worktree on a branch holding a code commit and then a docs commit exited 0 and moved the remote's main to include the code commit.

| # | Verdict | Evidence |
|---|---|---|
| 1 | holds | Step 9 now says that when the branch checked out is not `main`, it pushes nothing, and the plan commit reaches main with the branch's pull request. A new rules row holds it. So step 9's plan commit is never carried to main by procedure endings' push for pages. Verified: the text. The rule agrees in substance with architecture review's step 9 and the review orchestrator's paragraph after step 11. Its wording differs: those pages say to push as procedure endings says on `main`, and this one says nothing about `main`. Not blocking. Verified: the three pages. |
| 2 | accepted | The finding is not blocking, and the plan gives lane B one fix round, so a "Known defects" entry is the right outcome. Verified: the plan's lane B stop rule. One error: the instruction review's "The record" and the plan's stop rule send a known defect to the page's `prove-by` milestone, which is M6 here, or the docs audit. The disposition says M4. Not blocking. M4 is where the plan's Q41 entry leaves review commits, so the plan owner may keep M4, but the record should then say why. Verified: the front matter, the instruction review and the plan. |

Broke:

- Not blocking. Step 9 says the plan commit "reaches main with its pull request". This page runs after the fix is committed, and sometimes after its pull request has merged. On a merged branch, and on a branch with no pull request, the commit stays on the branch and never reaches main. The report names it, so nothing is lost silently. Verified: the text of step 9 and "When it runs". Inferred: that the analysis runs on such a branch.

Missed:

- Blocking. Step 7 applies a proposal that changes a guidance page, such as the review orchestrator's dimensions table, which needs no yes under step 6, "by the route the size gate gives it", and "a change to a guidance page gets its instruction review at the commit". The instruction review's step 7 then says to "push and report as procedure endings says". The session is in the fix's worktree, on the fix's branch, as finding 1 says. Procedure endings puts a pages-only commit "on the worktree's branch in a worktree", and its push table pushes it with `git push origin HEAD:main`. That push carries the unmerged fix to main, with no pull request and no CI. This goes against procedure endings' "never on its main" for code and the contract's draft pull request rule. Step 9's new rule names only the plan commit and comes after step 7, so it does not cover this. `direct_push` refuses only machinery paths. Verified: the texts of step 7, the instruction review's step 7 and procedure endings' "The commit" and "The push"; the scratch push above. Inferred: that an agent follows the route through to the push. The fix may extend step 9's off-`main` rule to every commit this procedure makes, step 7's included, or move the rule once to procedure endings, as findings 3 and 5 of the two review pages' records ask.

## Second fix round

The builder's second fix round, on 2026-11-23, under the maintainer's answer to Q42 in the workspace queue, recorded in the M3 plan. Procedure endings gained one rule, under "Off main": a procedure pushes nothing for pages when the branch checked out holds work other than its own pages, and the commits reach main with the branch's pull request. Its own review is in `2026-11-23-b2t-procedure-endings.md`. The non-blocking items of the re-check are not fixed in this round; each goes to "Known defects".

| Item | Disposition |
|---|---|
| Re-check, missed, blocking: step 7's page change is pushed to main from the fix's branch | fixed: procedure endings' off-main rule covers every page commit, including one a called procedure makes, such as the instruction review's at step 7. Step 9 links it and names step 7's commits. |
| Re-check, broke, not blocking: on a merged branch or one with no pull request, the plan commit never reaches main | known defect, for M6. Step 9 now applies the rule only when the fix's branch is checked out; the report still names each commit left there. |
| Re-check, item 2, not blocking: finding 2's known defect names M4, not the `prove-by` milestone M6 | known defect: kept for M4, since the plan's Q41 entry leaves where review notes and commits live to M4; this line says why. |

## Second re-check

A fresh driver-tier session re-checked the second fix round on 2026-11-23, narrowly. It read the contract, the instruction review's "The record", the M3 plan's Q42 entry and lane B's stop rule, `git diff HEAD` of the six pages, procedure endings and the six records, and procedure endings' "The order", "The commit", "The question-log entry", "The push" and its new "Off main". `python3 ws.py check` exits 0, with only the known warning on fix a bug's eval record. In a scratch repository with a local bare remote, `git log --format='%h %s' origin/main..HEAD` listed the code commit on a fix branch holding a code commit and then a page commit, so the test finds it off main. On a pages-only worktree it listed only the page commit, and `git push origin HEAD:main` from there put no code on the remote's main. On a fix branch with no code commit yet, it listed only the page commit. The record the round names for procedure endings, `2026-11-23-b2t-procedure-endings.md`, is not yet in the worktree (verified, `ls`); that rule is a separate reviewer's.

| Item | Verdict | Evidence |
|---|---|---|
| Re-check, missed, blocking: step 7's page change is pushed to main from the fix's branch | upheld | Step 7's page change ends through the instruction review's step 7, which pushes "as procedure endings says". Procedure endings' "The push" now holds "Off main": its test runs before any push of pages, the rule covers "one made by a procedure it calls", and off main nothing is pushed. Step 9 also declares the fix's branch off main and names step 7's commits, so the page does not rest on the test alone. No push of pages from the fix's branch remains. Verified: the texts; the scratch test lists the fix's code commit. |
| Re-check, broke, not blocking: on a merged branch or one with no pull request, the plan commit never reaches main | upheld | "Known defects" lists it for M6, the page's `prove-by`. Verified: the front matter and the section. |
| Re-check, item 2, not blocking: finding 2's known defect names M4, not M6 | upheld | The new "Known defects" line says why M4: the plan's Q41 entry leaves where review notes and commits live to M4. Verified: the section and the plan's Q41 entry. |

Broke:

- Not blocking. Step 9's "push nothing, for this commit or for any step 7 made, by whatever route" reaches past pages. Step 7 can send a change through changing the machinery or fix a bug, whose commits go on a branch of their own and are pushed with a draft pull request; "When it runs" says such a change "may open a pull request of its own". Step 9 and the new rules row say those commits stay on the fix's branch and reach main with its pull request, which is not where they are. Procedure endings' rule covers pages only. The error leans toward pushing nothing, so no code reaches main without a pull request. Verified: the texts of "When it runs", steps 7 and 9, the rules row and procedure endings' "Off main". Inferred: that an agent then holds back a machinery branch's push. "Every page commit, step 7's included" would match the rule.

Missed:

- none.
