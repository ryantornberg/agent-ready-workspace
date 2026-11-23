---
kind: record
last-reviewed: 2026-11-22
covers: docs/playbooks/review-orchestrator.md
reviewed-at: f757aed, with the uncommitted change of the B3 builder
---

# Instruction review: docs/playbooks/review-orchestrator.md

This records the instruction review of B3's change to the review orchestrator's step 10, for its author and for any agent recording a review.

**In short:** 5 findings, 1 of them blocking: 3 step, 1 contradiction, 1 placement. The blocking one: committing a review record as procedure endings says either needs a branch switch that fails over tracked changes, or moves the reviewed branch's tip so the record never names the tip a pull request opens at.

## Scope

In scope: the change to step 10's second bullet, where a review with no plan is recorded, read in the context of the whole page. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/procedure-endings.md`, `docs/layout.md`, `docs/authoring.md`, `docs/reader-standard.md`, `docs/records/README.md`, `docs/templates/fix-record.md`, `docs/templates/defect-register.md`, `docs/templates/README.md`, "Which writes need a yes" and "The operations" in `docs/playbooks/git-host-operations.md`, and B3's row and its 2026-11-22 entries in the M3 plan. Ran `python3 ws.py check` in the worktree, which passed with one warning unrelated to this page. In a scratch repository, ran `git switch main` from a task branch with an uncommitted change to a file the branch had changed.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | Steps, step 10, the second bullet | Blocking. "Commit the record as procedure endings says" sends the agent to "Where the commit goes": a change of pages only goes "on main in the main working copy, or on the worktree's branch in a worktree". On your own branch, step 3 reads the tip where you work, with the branch checked out, and allows tracked changes there. In the main working copy, the record must go on main, so the agent switches branches; in a scratch repository, `git switch main` with an uncommitted change to a file the branch had changed aborted. In a worktree, the record lands on the reviewed branch and moves its tip past the `### Review of <tip commit>` it names. Git-host operations' "Create a pull request" row then finds no record naming the tip about to open and says to run this playbook first; step 2 finds no earlier review (finding 2), so a full round runs and commits again. Before the change, no record was committed on this path, so the tip held. Verified: the texts and the scratch run. Inferred: the loop, from reading the three steps together. | fixed: the fix record or review page is committed on main, in a throwaway worktree of `origin/main` when main is not checked out, per the new section "Committing a record about a branch", so the reviewed tip stays put |
| 2 | step | Steps, step 2 | Not blocking. Step 2 looks for an earlier round only in "the hand-off plan's 'Results', or the pull request's description, reviews and comments". Step 10 now also writes rounds to a fix record's "Reviews" section and to `docs/records/reviews/`. Before a pull request opens, a branch with no plan never finds its earlier round, so it never becomes a delta round, and step 9's re-check of rows marked fixed never runs. A fix record's rounds are not copied into a pull request's description at all, since that sentence follows the `docs/records/reviews/` case. Verified. | fixed: step 2 now also reads the fix record's "Reviews" and the branch's pages in `docs/records/reviews/` on `origin/main`; step 10 copies the block into the pull request either way |
| 3 | step | Steps, step 10, the second bullet | Not blocking. Each round writes "a new record page", named `<YYYY-MM-DD>-<branch or pull request>.md`. A second round on the same branch the same day gets the same name, and the page gives no default for a later round: a new page, or a new block appended to the first, as the plan's "Results" and the fix record's "Reviews" take one block per tip. The example name `2026-11-22-pr-41.md` shows a pull request, not the `/` rule it follows. Verified. | fixed: a second round the same day appends its block to the existing page, and the example now shows a branch name too |
| 4 | contradiction | What exists today and what is planned, the defect register row; Steps, step 5 | Not blocking. The table says the defect register step 5 reconciles against is "Planned for slice B3 of M3", and step 5 says the reconcile "waits for slice B3's defect register: write 'not run'". B3's batch adds that register: `docs/records/defects.md` and `docs/templates/defect-register.md`, whose "Reconciling" bullet says "step 5 of the review orchestrator is where a review checks the change against the open rows ... done by hand". An agent following this page skips the reconcile the register expects. Verified. | fixed: the table row and step 5 link the defect register and its template; step 5 reconciles by hand against its open rows |
| 5 | placement | Steps, step 10 | Not blocking. The new bullet links procedure endings for the commit, but the same step restates its rules beside it: the plan bullet says "commit the plan, staged by name", and the closing paragraph says "Mark each claim verified or inferred". The page is edited now, so procedure endings' rule that an older page switches to the link when next edited applies. Step 10 also names no push, which procedure endings' order runs after the commit. Verified. | fixed: the plan bullet links procedure endings' commit, and the closing paragraph links procedure endings for push and report |

## Checked with no finding

- trigger: the purpose line and **In short** line, "Collect the findings into one table, record it, and report", still cover where the record now goes; the templates index and the records README route a reader to step 10 for the review record. Verified.
- enforcement: the change adds no must or never; the new places are instructions under an existing step. The page's Rules table is unchanged and its tags are untouched. Verified.
- eval-case: the page is `proof: unproven` with `prove-by: M6`, so the new recording path needs no eval case yet. Verified from the front matter.

## Re-check

A fresh session re-read the page on 2026-11-22, after the fix round.

The new section "Committing a record about a branch" was run as the handoff record's re-check describes: a scratch copy with the B3 pages on main, a bare remote, and the copy's own hooks called by hand. It ran from the main copy on a task branch with an uncommitted change, and from a linked worktree while another live session held the main copy.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed for a review page in `docs/records/reviews/`; not fixed for a fix record | From both starting points, the record was written in a throwaway worktree of `origin/main`, committed and pushed to main, and the task branch's tip and uncommitted change stayed as they were. The edit ledger recorded the file in the throwaway worktree's own git folder. The commit hooks, the pre-push hook, `push_lease` and the discard guard all let it through. Verified in the scratch copy, with controls that the same guards refuse `git push origin main` from the worktree and a record written by shell. The fix record case and the plan case still break, under "Broke". |
| 2 | fixed | Step 2 reads the fix record's "Reviews" and the branch's pages in `docs/records/reviews/` on `origin/main`. Verified: `git ls-tree --name-only origin/main docs/records/reviews/` listed the record the scratch run pushed. |
| 3 | fixed | A second round the same day appends to the existing page, and the example shows a branch name and a pull request. Verified. |
| 4 | fixed | The table row and step 5 link the defect register and its template, and step 5 reconciles by hand. Verified. One new claim in the row is unsupported, under "Broke". |
| 5 | fixed | The plan bullet links procedure endings' commit, and the closing paragraph links procedure endings for the push and the report. Verified. The link opens a new gap, under "Broke". |

Broke:

- Blocking. The plan bullet now commits the plan as procedure endings says, which puts a change of pages only on main in the main working copy. Reviewing your own branch in the main copy, where step 3 allows tracked changes, the agent must switch to main, and git refuses. In a worktree, the commit goes on the reviewed branch and moves its tip. The page's own new section says a review record "never goes on the branch it is about". Verified: in a scratch repository, `git switch main` from a task branch with an uncommitted change to a file the branch changed exited 1.
- Blocking. Step 10 commits a fix record's new review block through the section, on main. The fix record template says the record is committed "with the fix, on the fix's branch", so `origin/main` has no such file to append to. Writing one there makes a second copy, and the fix branch then no longer merges. The page does not label this as an exception to the template, and step 2 does not say which copy's "Reviews" it reads. Verified: in a scratch repository, the throwaway worktree of main held no fix record, and merging the fix branch after the block was committed on main stopped with "CONFLICT (add/add)".
- Blocking. The section adds the worktree from the local `origin/main` with no `git fetch origin` first. Step 1's fetch comes before the dispatched reviews, so main can move before step 10. Then the pre-push hook refuses with "Fetch first" and git rejects the push, and the section gives no way on. Verified in the scratch copy after another clone pushed to main. Fetching, then `pull --rebase origin main` in the throwaway worktree, then the push, all passed.
- Blocking. Step 1 says that for a pull request in a repository pinned under `src/REPO`, every `git` command of this playbook runs with `-C src/REPO`. The section sits inside the playbook and does not exempt itself. Read literally, an agent adds the worktree in the pinned repository and pushes a review record to that repository's main. Procedure endings says a pinned repository's main never takes a commit. Inferred, from the texts of step 1, the section and procedure endings' "Where the commit goes".
- Not blocking. The section is copied word for word from handoff. It states an exception to procedure endings' "Where the commit goes" on two pages, not on the page that owns the rule, against the style guide's "One rule, one page". Verified: `git diff` of both pages.
- Not blocking. The defect register row now says "M4 plans a script for it". No plan in `docs/plans/` says so, and the register's template says only that no script does it yet. Inferred: the source may sit outside this repository.

Missed: none.

## Second fix round

The builder's second fix round, on 2026-11-23, under the maintainer's answer to Q35 in the workspace queue, recorded in the M3 plan. It first cut back: the rule that a review record or a kept handoff note is committed on main from a throwaway worktree is removed, a review round's record goes in the plan's "Results" or the pull request's description, and a kept handoff note waits for M4. Then it fixed the blocking items the re-check found.

| Item | Disposition |
|---|---|
| Broke, blocking: the plan bullet commits as procedure endings says, which needs a switch to main from the reviewed branch | fixed: step 10 commits the plan on the branch checked out, which in a worktree is its branch, as procedure endings says for pages, and says not to switch branches. Step 2 counts a tip as reviewed when the commits after the reviewed one change only the hand-off plan or the work's fix record, so this commit sends no round into a delta review. |
| Broke, blocking: step 10 commits a fix record's review block on main, where no fix record exists | withdrawn by the cut-back: without a plan, the record goes in the report and, once a pull request is open, in its description, as before the first round. A fix record no longer holds reviews, and step 2 no longer reads one or `docs/records/reviews/`. |
| Broke, blocking: the section adds its worktree with no fetch first | withdrawn by the cut-back: the section is removed. |
| Broke, blocking: step 1's `-C src/REPO` sends the section's push to a pinned repository's main | fixed for what is left: the section is gone, and step 10's plan bullet says the plan is committed in this workspace, without step 1's `-C`, for work in a repository pinned under `src/`. |
| Broke, not blocking: the section is copied on two pages | withdrawn by the cut-back. |
| Broke, not blocking: "M4 plans a script for it" has no source | not fixed in this round, which Q35 limits to the blocking items. It stays open: a "Known defects" section is written once no fix round is left on the page. |
| First-round findings 1 to 3, on where a review record without a plan goes | withdrawn by the cut-back, which sets that place: the report, then the pull request's description. |

## Second re-check

A fresh session re-read the page on 2026-11-23, after the second fix round.

It read the page whole, `git show 65a6f5c`, procedure endings, the contract, git-host operations, the fix record and pull request templates, escape analysis, handoff, the templates index, the records README, `workspace.json`'s `direct_push` and `review_trailer` entries, and the milestone record `docs/milestones/m3.md`. It ran git in a scratch repository with a local bare remote, under its own temp folder.

| Item | Verdict | Evidence |
|---|---|---|
| Broke, blocking: the plan bullet needs a switch to main from the reviewed branch | fixed | Step 10 commits the plan on the branch checked out and says not to switch. Verified in the scratch repository: from a task branch with an uncommitted change, committing the plan staged by name exited 0 and left the change in place, while `git switch main` exited 1. The new step 2 clause and the push that follows open gaps, under "Broke" and "Missed". |
| Broke, blocking: a fix record's review block committed on main | withdrawn-upheld | Step 10's no-plan bullet puts the record in the report, then the pull request's description. Step 2 reads only the plan's "Results" and the pull request. No page names a fix record's "Reviews" or `docs/records/reviews/`. Verified: the page, and `git grep` for `records/reviews`, `"Reviews"` and the removed anchor across `docs/` outside plans and these records. |
| Broke, blocking: the section's worktree has no fetch first | withdrawn-upheld | The section and its `record-main` worktree are gone. Verified: the same search. |
| Broke, blocking: step 1's `-C src/REPO` sends the section's push to a pinned repository's main | fixed | The section is gone, and the plan bullet says to commit the plan in this workspace, without step 1's `-C`. Verified: the text. |
| Broke, not blocking: the section is copied on two pages | withdrawn-upheld | Removed from both pages. Verified: the diff. |
| Broke, not blocking: "M4 plans a script for it" has no source | not fixed | The row still says so, and no plan in `docs/plans/` mentions a script for the defect register. Verified by search. Its disposition says "see 'Known defects'", but this record has no such section. |
| First-round findings 1 to 3, on where a review record without a plan goes | withdrawn-upheld | Q35 sets the place, and step 10, the pull request template, the templates index and the records README all name it. Verified: the four texts. As before the first round, a branch with no plan cannot find its earlier round before a pull request opens, so every run before then is a full round. That cost follows from the decision. Inferred. |

Broke:

- Blocking. On planned work, step 10's plan commit moves the branch tip past the reviewed commit. The new step 2 clause counts that tip as reviewed, then stops, writing nothing. Git-host operations' "Create a pull request" row says the record "names the tip you are about to open; if it does not, stop and run the review orchestrator first". Its Rules table says to open a pull request only once the review is on record for its tip. The record names the commit before the plan commit, so that row sends the agent back here, and step 2 stops again. The agent either loops, or opens the pull request against git-host operations' rule. The fix changed what counts as a reviewed tip on this page, but did not sweep the page that holds the same rule. Verified: both texts, and in the scratch repository `git diff --name-only REVIEWED TIP` after the plan commit listed only the plan. Inferred: which way the agent goes.
- Not blocking. In the main working copy on your own branch, the plan commit lands on that branch, against procedure endings' "Where the commit goes", which puts a change of pages only on main there. The bullet gives the reason but labels no exception, as handoff's step 2 does not either. The closing paragraph then pushes "as procedure endings says". Its push table has no row for pages committed on a task branch in the main copy: `git push origin main` does not carry the commit, and the "push is done" test, `git rev-parse HEAD` against `origin/main`, cannot pass. Verified: the texts.
- Not blocking. The step 2 clause counts a change to the hand-off plan as no change. But step 5 takes the request from that plan's Goal, Non-goals and Success criteria. If those change after the review, the tip still counts as reviewed against the old request. Code is not hidden this way. Verified in the scratch repository: after a commit to `src/`, the same diff listed the code file beside the plan, so the clause did not apply. Inferred: that a plan's spec can change after a review.

Missed:

- Blocking. When you review your own branch in a worktree, step 10 commits the plan on that branch, "as procedure endings' commit says for pages". The closing paragraph then pushes "as procedure endings says". That page's push table, for "Pages only, in a worktree", gives `git push origin HEAD:main`. HEAD is the reviewed branch, so this push publishes its unmerged code to main, with no pull request and no CI. The contract says to open a pull request as a draft and merge only after CI passes. Procedure endings says code under `src/` never goes on main. No guard stops it for code under `src/`. The pre-push checks are `direct_push`, which judges only the machinery paths in `workspace.json`, where `src/` is not listed, and `review_trailer`, which judges guidance pages. Verified in the scratch repository: from a worktree on a branch with a code commit and then a pages commit, `git push origin HEAD:main` exited 0 and moved the remote's main to include the code commit. Verified by reading: both parts' configuration. Inferred: that an agent picks that row because what it committed was pages only. The first re-check saw only that this commit moves the tip, not the push. The bullet should say to push the branch, not main, as the fix record template says for its own record.
- Not blocking. Step 11 and the table "What exists today and what is planned" still say the outward-write guard "is planned in slice C5e of M3, so today only the person's yes holds it". The milestone record says C5e is merged, and the bug report template now names the guard as live. Verified: `docs/milestones/m3.md` and both pages.

## Revert (Q41)

The builder's revert, on 2026-11-23, under the maintainer's answer to Q41 in the workspace queue, recorded in the M3 plan. No third fix round was made. The page's wording for where and how it commits and pushes went back to main's text; only its pointers to B3's new pages stay changed. Where a review commits on a branch stays unsettled, for M4.

| Item | Disposition |
|---|---|
| Second re-check, missed, blocking: in a worktree the plan commit on the reviewed branch is pushed to main by procedure endings' row for pages | withdrawn by the revert: step 10's plan bullet is main's again, "append it to the plan's 'Results', and commit the plan, staged by name", and the closing paragraph names no push. |
| Second re-check, broke, blocking: the step 2 clause stops on a tip git-host operations will not open a pull request for | withdrawn by the revert: the clause is removed, and step 2's first case is main's again. |
| Second re-check, broke, not blocking: in the main copy on a task branch, the plan commit lands on that branch and the push table has no row for it | withdrawn by the revert: the bullet no longer places the commit. Where it goes is as unsettled as before B3, for M4. |
| Second re-check, broke, not blocking: the step 2 clause counts a changed spec in the plan as no change | withdrawn by the revert: the clause is removed. |
| Second re-check, missed, not blocking: step 11 and the table still call the outward-write guard planned in C5e | deferred to B2t: it is not a B3 change, and B2t's fix round updates the B2 pages that still call the guard planned (Q31). |
| Second fix round, not blocking: "M4 plans a script for it" has no source | known defect, for M6, the page's `prove-by`: see "Known defects". |
| First-round finding 5, not blocking: step 10 restates procedure endings' commit and report rules | reverted under Q41: the plan bullet and the closing paragraph are main's text again, so they restate the rule as main does. Deferred to M4, with where a review commits. |
| Without a plan, the bullet's pointer "until slice B3's fix record exists" | changed as a stale pointer: the fix record holds no review round, so the bullet now ends at the report and the pull request's description, as main's does. |

## Known defects

The plan allows the page no third fix round, so its non-blocking items still open stay here, for M6, the page's `prove-by` milestone, unless another is named.

- The table row "Reconciling the change against the defect register in step 5" says "M4 plans a script for it", and no plan in `docs/plans/` names that script yet.
- Added after the re-check after the revert: on planned work, step 10's plan commit moves the tip past the reviewed commit, so git-host operations asks for a record naming the new tip and step 2 runs a delta round over a range that changes only the plan. Main has the same three texts; the removed step 2 clause had tried to close this. For M4, which settles where a review commits, as Q41 leaves it.

Not a known defect: step 11's text calling the outward-write guard planned in C5e. The maintainer's answer to Q31 in the workspace queue gives it to B2t's fix round, and B2t's builder records that answer in the plan.

## Re-check after the revert

A fresh session re-read the page on 2026-11-23, after the revert under Q41. It read the contract, the instruction review, procedure endings, the Q41 entry under "Changes after approval" in the M3 plan on `origin/main` (the branch does not hold that entry yet), `git diff HEAD` and `git diff origin/main` of the page, git-host operations, the defect register and its template, the templates index, the records README, the pull request template and the lessons log template. It searched `docs/` outside plans and these records for the removed clause and for review commit wording, and ran `python3 ws.py check`, which exits 0 with only the known warning on fix a bug's eval record. Verified.

Against `origin/main`, the page differs in four places, all pointers to B3's defect register or the removal of a stale one: the table row on reconciling, step 5's reconcile by hand, the stop paragraph's "such as the defect register", and step 10's no-plan bullet losing "until slice B3's fix record exists". Step 2, step 10's plan bullet and step 10's closing paragraph match main word for word, so no commit or push wording of B3's survives. Step 5 and the table row say more than a link, how the reconcile runs today, but neither places a commit, so both stay within Q41. Verified: `git diff origin/main`.

| Item | Verdict | Evidence |
|---|---|---|
| Second re-check, missed, blocking: the plan commit on the reviewed branch is pushed to main by procedure endings' row for pages | upheld | Step 10's plan bullet is main's text, the closing paragraph names no push, and the page no longer links procedure endings at all. Verified: the diff and a search of the page. Where the plan commit lands is main's open question, under "Broke". |
| Second re-check, broke, blocking: the step 2 clause stops on a tip git-host operations will not open a pull request for | upheld | The diff against `origin/main` has no change in step 2, and no page outside plans and these records describes the clause. Verified: the diff, and a search for "as reviewed", "counts a tip" and "only the hand-off plan". |
| Second re-check, broke, not blocking: in the main copy on a task branch, the plan commit lands there and the push table has no row | upheld | The bullet places no commit and names no push, as on main. Verified: the text. |
| Second re-check, broke, not blocking: the step 2 clause counts a changed spec in the plan as no change | upheld | The clause is gone. Verified: the diff. |
| Second re-check, missed, not blocking: step 11 and the table still call the outward-write guard planned in C5e | upheld | Both texts are main's: the diff has no change there, so this is not B3's change, and Q41 allows B3 only its pointers. Verified. The reason given, that B2t updates them under Q31, is not on record where this session could read it, under "Missed". |
| Second fix round, not blocking: "M4 plans a script for it" has no source | upheld | "Known defects" holds it for M6, the page's `prove-by`, as the instruction review's step 4 asks when no fix round is left. Verified: the section and the front matter. |
| First-round finding 5, not blocking: step 10 restates procedure endings' commit and report rules | upheld | The plan bullet and the closing paragraph are main's text. The closing paragraph's old B3 sentence held the push, which Q41 reverts, so its report half goes with it. Q41 leaves where a review commits for M4. Verified: the diff and the Q41 entry. |
| The no-plan bullet's pointer "until slice B3's fix record exists" | upheld | The bullet now ends as main's does after that clause, and the fix record template says a review round's record goes in the pull request's description, not in the record. Verified: both texts. |

Broke:

- Not blocking. With the step 2 clause gone, the gap it tried to close is back as main has it. On planned work, step 10 commits the plan after the review, which moves the branch tip past the reviewed commit. Git-host operations' "Create a pull request" row then asks for a record that names the tip about to open, and step 2 runs a delta round over a range that changes only the plan, whose own plan commit moves the tip again. Main holds the same three texts, so the revert does not make this worse, and Q41 leaves where a review commits for M4. Verified: the texts on the branch and on `origin/main`. Inferred: the loop.

Missed:

- Not blocking. The revert table defers step 11's stale C5e text to B2t "(Q31)". B2t's row in the M3 plan lists the tutorials and B2's 18 open items, not this text, and the question log on `origin/main` still shows Q31 as not answered. The answer may sit in the workspace queue, which this session did not read. Verified: both texts. Inferred: that the item has no home on record yet.
