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
| Broke, not blocking: "M4 plans a script for it" has no source | not fixed in this round, which Q35 limits to the blocking items; see "Known defects". |
| First-round findings 1 to 3, on where a review record without a plan goes | withdrawn by the cut-back, which sets that place: the report, then the pull request's description. |
