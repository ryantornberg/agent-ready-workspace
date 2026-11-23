---
kind: record
last-reviewed: 2026-11-22
covers: docs/templates/pull-request.md
reviewed-at: f757aed, with the uncommitted change of the B3 builder
---

# Instruction review: docs/templates/pull-request.md

This records the instruction review of the pull request template and its bookkeeping list, for its author and anyone opening or merging a pull request.

**In short:** 8 findings, 3 of them blocking: 4 contradiction, 2 step, 1 trigger, 1 placement. The blocking three are all in the bookkeeping list: `git branch -d` runs before the worktree that holds the branch is removed, and fails; the branch row pushes a deletion with no carve-out for a team's workspace, where a person pushes; and the stacked-branches row retargets a pull request without the yes git-host operations asks for.

## Scope

In scope: the whole page, as a new template. Read in full: the page; `AGENTS.md`, `INDEX.md`, `docs/playbooks/instruction-review.md`, `docs/procedure-endings.md`, `docs/layout.md`, `docs/reader-standard.md`, `docs/authoring.md`; B3's row and the 2026-11-22 entries naming B3 in the M3 plan; `docs/templates/README.md`, `docs/playbooks/git-host-operations.md`, `docs/playbooks/tracker-operations.md`, `docs/playbooks/handoff.md`, `docs/playbooks/fix-a-bug.md`, and the linked sections of `docs/commits.md`, `docs/changing-the-machinery.md`, `docs/review-in-a-worktree.md`, `docs/playbooks/review-orchestrator.md` (step 10), `docs/templates/hand-off-plan.md`, `docs/templates/fix-record.md`, decisions 0005 and 0006. Ran `python3 ws.py check` in the worktree: it passed, with one warning about fix a bug's eval record, unrelated to this page. In a scratch repository, ran the branch row's `git branch -d` against a branch a worktree had checked out. Read GitHub's page on creating and deleting branches for what happens to pull requests based on a deleted branch.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | After the merge: the bookkeeping list, the branch row | Blocking. The row says "Delete your local branch with `git branch -d BRANCH`, and remove its worktree if it had one", in that order. While a worktree has the branch checked out, git refuses the deletion. An agent following the row runs a command that fails. The worktree must be removed first, after review in a worktree's step 6 check, which the row already links. Verified: in a scratch repository, `git branch -d feat` with a worktree on `feat` printed "cannot delete branch 'feat' used by worktree" and exited 1. | fixed: the branch row now removes the worktree first, after review in a worktree's step 6 check, then runs `git branch -d`. |
| 2 | contradiction | After the merge: the bookkeeping list, the branch row | Blocking. After a merge made another way, the row has the agent run `git push origin --delete BRANCH`, with no word on who pushes. Git-host operations' rules say "In a team's workspace, a person pushes; the agent gives the command", and procedure endings' push table says the same. The page's carve-out sentence covers only "a write outside this repository", which a push to the workspace's own remote is not. An agent in a team's workspace following the row pushes where a person should. Verified: the row's text and both pages' rules. | fixed: the branch row now says who runs `git push origin --delete` by procedure endings' push table: in a team's workspace a person runs it and the agent gives the command. |
| 3 | contradiction | After the merge: the bookkeeping list, the stacked branches row | Blocking. The "What to do" cell says that if an open pull request's base still names the deleted branch, "retarget it to `main`". The row it names, git-host operations' "Retarget", says "Ask first, unless the request names it in its own words", and a stacked pull request is often another person's, which that page always asks about. The cell gives no ask, so an agent working down the list retargets without the yes. The page's rule that "each item follows the page its row names" softens this, but the cell's own instruction is the step an agent acts on. The target is also fixed as `main`, where GitHub retargets to the merged pull request's base. Verified: both texts; GitHub's page says that deleting a head branch after its pull request merged retargets the pull requests based on it to that pull request's base. | fixed: the stacked-branches row now asks first unless the request names the retarget, as git-host operations' Retarget row says, and the target is the merged pull request's base, not a fixed `main`. |
| 4 | step | After the merge: the bookkeeping list, the branch row | Not blocking. The list covers merges in a pinned repository, as its "Pins under `src/`" row shows, but the branch row's commands, `git ls-remote --heads origin BRANCH`, `git push origin --delete BRANCH` and `git branch -d BRANCH`, name no `-C src/REPO`. Run from the workspace, they read the workspace's remote, where the branch is absent, so the row reports it gone while it stays on the pinned repository's host. Git-host operations adds `-C src/REPO` for the same case. `python3 ws.py merge` works only on this repository's `origin`, as changing the machinery says. Verified: the row's text and changing the machinery. Inferred: what an agent concludes from the empty output. | fixed: the branch row now says to add `-C src/REPO` to each `git` command for a merge in a pinned repository, and limits `python3 ws.py merge` to this repository. |
| 5 | contradiction | Filling it, the last bullet; Skeleton, What testing needs | Not blocking. "Drop a section that has nothing in it, except 'Decisions made without asking' and 'Review'". The skeleton's "What testing needs" says to write "nothing: no behavior a tester sees changed" when empty, which keeps the section. An agent cannot follow both, and two writers produce different descriptions. Verified. | fixed: "An empty heading" now lists "What testing needs" among the three headings kept with their empty text. |
| 6 | contradiction | The opening; Skeleton | Not blocking. The reader standard names the pull request description as a page kind a person reads, so the template must name the reader of each copy and give one worked example. It names only the writer, "anyone opening or merging one", and gives no worked example. It also names no word budget for the copy's top layer, beyond "one or two sentences" for the first line. Verified: the reader standard's "Who it binds" and the page's text. | fixed: the page now names a copy's readers (a reviewer, a tester and the person who merges), a top layer of title and first line within 60 words, fixed headings in a fixed order with the drop rule, and one invented worked example. |
| 7 | placement | After the merge: the bookkeeping list | Not blocking. A template is "a shape to copy", as layout says, but this section is a procedure: when to run it, six items with git and `gh` commands, writes on the host and the tracker, and an ending through procedure endings. Decision 0006 gives a template no proof mark, so this procedure carries neither `proof` nor `prove-by`, and no eval case covers it. It belongs on a playbook, or as a section of git-host operations, where it would carry `prove-by: M8` with that page. Verified: layout's kinds table, decision 0006's "a template ... carries none", and `covered()` over the three cases. | declined: the plan's B3 row places the bookkeeping list after a merge with the pull request standard; moving it to a playbook is a change of plan, not a fix |
| 8 | trigger | When to use it | Not blocking. The page fires "whenever you write or rewrite a pull request's description", but the page an agent reaches to open a pull request, git-host operations, does not link it. Its "Title and description" row gives a shorter shape of its own, "what changed, why, how it was checked", so an agent following that page never meets this template's Review, Decisions made without asking, or What testing needs sections. Only the templates index links the page. Verified with `grep -rln pull-request.md`. A missing `INDEX.md` row is left to slice Z. | fixed: git-host operations' "Title and description" row now links this template instead of giving its own shape. The `INDEX.md` row is queued for slice Z. |

## Checked with no finding

- enforcement: each rules row is tagged `prose`, and each must and never on the page has a row: narration, one bullet per change, the review link, the decisions section, the 4,000-character limit and the bookkeeping list. The merge-commit and draft rules are left to the pages that own them. Verified.
- The links resolve, since `ws.py check` passed. The Review bullet's three places match review orchestrator step 10 and the fix record template's "Reviews" section. `python3 ws.py merge` deleting the branch on GitHub matches changing the machinery. The "How it was verified" bullet links procedure endings' report rather than restating it. Verified.

## Re-check

A fresh session re-read the page on 2026-11-22, after the fix round.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | The branch row removes the worktree first, after review in a worktree's step 6 check, then runs `git branch -d`. Verified: the row's text and that step. |
| 2 | fixed | The branch row says who runs `git push origin --delete` by procedure endings' push table: in a team's workspace, a person, given the command. Verified. |
| 3 | fixed | The stacked-branches row asks first unless the request names the retarget, as git-host operations' Retarget row says, and the target is the merged pull request's base. Verified: both rows. |
| 4 | fixed | The branch row adds `-C src/REPO` to each `git` command for a merge in a pinned repository, and limits `python3 ws.py merge` to this repository. Verified. |
| 5 | fixed | "An empty heading" keeps three headings with their empty text, "What testing needs" among them, matching the skeleton. Verified. |
| 6 | fixed | The purpose sentence names a copy's readers. The top layer is the title and first line, within 60 words, and the headings are fixed with a drop rule. One worked example is marked invented. Verified: the page's own top layer is 85 words; the example's title and first line are 31 words, and its body 1,116 characters. |
| 7 | decline upheld | Slice B3's row in the M3 plan places "the bookkeeping list after a merge" with the pull request standard, so moving it is a change of plan. The finding was not blocking. Verified: the plan's slice table. |
| 8 | fixed | Git-host operations' "Title and description" row now links this template instead of giving its own shape. Verified: `git diff -- docs/playbooks/git-host-operations.md`. |

Broke: none.

Missed: none. The bookkeeping list is still not linked from the place an agent merges; that is recorded in the sweep record of git-host operations.

## Second fix round

The builder's second fix round, on 2026-11-23, under the maintainer's answer to Q35 in the workspace queue, recorded in the M3 plan. It first cut back: the rule that a review record or a kept handoff note is committed on main from a throwaway worktree is removed, a review round's record goes in the plan's "Results" or the pull request's description, and a kept handoff note waits for M4. Then it fixed the blocking items the re-check found. This page held no blocking break; the cut-back's shared rule swept it.

| Item | Disposition |
|---|---|
| The cut-back, swept: the Review bullet named a fix record's review section and `docs/records/reviews/` | fixed: the Review bullet, the skeleton's Review line and the rules row now say the record is linked from the hand-off plan or, with no plan, held in this description. |

## Second re-check

A fresh session re-read the page on 2026-11-23, after the second fix round.

It read the page whole, `git show 65a6f5c`, the review orchestrator's steps 2 and 10, git-host operations' pull request rows and Rules, the templates index and the records README.

| Item | Verdict | Evidence |
|---|---|---|
| The cut-back, swept: the Review bullet named a fix record's review section and `docs/records/reviews/` | fixed | The skeleton's Review line, the Review bullet and the rules row say the record is linked from the hand-off plan or, with no plan, pasted into the description. That matches step 10, which puts a no-plan round in the report and then the description. No text names a fix record's review section or `docs/records/reviews/`. Verified: the page and `git grep`. |

Broke:

- Not blocking. With no plan, the Review bullet pastes the whole review record into the description. The Length bullet and its rule keep a description under 4,000 characters, with "detail beyond that" going "in the plan or the record the description links". With no plan there is no such record to link. A findings table of eight columns passes 4,000 characters within a few rows. An agent cannot follow both bullets for a review of any size. Verified: the texts. Inferred: the size of a typical table.
- Not blocking. "Link the review record for the tip you are opening. It sits in a hand-off plan's Results." On planned work, the review orchestrator's step 10 commits that plan on the branch, so the record names the commit before the tip being opened. The blocking side of this mismatch, with git-host operations' tip check, is recorded in the review orchestrator's record. Verified: the texts.

Missed: none.
