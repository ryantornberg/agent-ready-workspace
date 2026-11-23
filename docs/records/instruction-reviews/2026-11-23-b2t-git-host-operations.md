---
kind: record
last-reviewed: 2026-11-23
covers: docs/playbooks/git-host-operations.md
reviewed-at: 18eccc5, with the uncommitted change of the B2t builder
---

# Instruction review: docs/playbooks/git-host-operations.md

This records the instruction review of slice B2t's change to git-host operations, for its author and for agents acting on a pull request.

**In short:** 5 findings: 2 contradiction, 2 step, 1 placement. One is blocking.

## Scope

The change is `git diff fad9f23 -- docs/playbooks/git-host-operations.md`: the outward-write guard row of "What exists today and what is planned", step 7's question-log sentence, the "Create a pull request" row of "The operations", and two rows of "Rules". In scope: that changed text, and anything on the page, or on a page it links to, that the change contradicts or leaves stale.

Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/procedure-endings.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/changing-the-machinery.md`, `docs/parts.md` (the `outward_write` row and "The parts here"), the case names in `parts/outward_write.cases.json`, `outward-repos.json`, decision 0004's "The outward-write guard", `docs/research-ladder.md`, `docs/question-log.md`, and the pages the changed text links to. Ran `gh pr create --help`, `python3 ws.py check` (no error; one unrelated eval_record warning) and `python3 ws.py rules` (the new rows are listed with their tags).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | "Steps", step 7, with "The operations", "Create a pull request" | Blocking. Step 7 now sends a question-log entry to procedure endings, and the new first sentence of "Create a pull request" makes sure the checked-out branch is the pull request's branch. Procedure endings' "The commit" puts a pages-only commit "on the worktree's branch in a worktree", and its push table pushes that with `git push origin HEAD:main`. Neither page has a case for a log row committed while a pull request's branch is checked out. Followed as written in a worktree, the push carries every commit of the pull request's branch to main, past the draft pull request and the CI run the contract requires before a merge. In the main working copy, "on main" would need a checkout the page never asks for. The text of both pages is verified by reading; that the push lands the branch on main is inferred. `direct_push` would refuse it only for a branch that changes a machinery path (verified in the parts table). | fixed: off `main`, step 7 leaves the log row uncommitted and gives its text in the report, a labelled exception; a rules row holds it. |
| 2 | contradiction | "The operations", "Create a pull request" | Not blocking. The new sentence gives its reason as "the push and `gh pr create` act on the branch checked out", but the same row's command now passes `--head BRANCH`, and `gh pr create --help` says `--head` names "the branch that contains commits for your pull request (default [current branch])". With `--head`, `gh pr create` acts on the named branch, not the checked-out one; only the push acts on HEAD. Verified by `gh pr create --help`. | fixed: the reason now names the push only. |
| 3 | step | "The operations", "Create a pull request" | Not blocking. The command's `BRANCH` is never defined: the row's "where" clause defines only TARGET. The new check compares the checked-out branch with "the branch the request names", with no default when the request names none, such as a sending page's "open a pull request for it"; step 2's default, the current branch, would make the check pass by definition. Verified by reading the row and step 2. | fixed: BRANCH is defined, with the checked-out branch as its default. |
| 4 | contradiction | "What exists today and what is planned", with "Which writes need a yes" and "Rules" | Not blocking. The page still says `gh` writes work "on this repository and on repositories pinned under `src/`", and the rules row allows writes to both. The new guard row says the guard refuses a write outside `outward-repos.json`, which lists only this repository (verified: the file, and decision 0004's "This repository lists only itself"), and only a person edits it (`outward_list`, and changing the machinery's table). The page never says the list must hold each pinned repository, or that a refusal there means a person must add it. For a pinned repository not on the list, step 5's write is refused and ends in the report. The rules row's new tag, `outward_write#gh pr create on a repository outside the list is refused`, enforces the list, not the rule's set. Contents verified; how an instance's pinned repositories meet the list is inferred. | fixed: the GitHub row says a pinned repository also needs a person to add it to `outward-repos.json`. |
| 5 | placement | "Steps", step 7 | Not blocking. The changed step 7 still restates the report rule ("with each claim marked verified or inferred, as the definition of done says") rather than linking [procedure endings' report](../../procedure-endings.md#the-report), which the page now links only for the question-log entry. Procedure endings' report also names refusals and anything left uncommitted or unpushed; step 7's list does not. Verified by reading both pages. | fixed: step 7 links procedure endings' "The report". |

## Checked with no finding

- trigger: the purpose line, the In short line and the routing table were not changed; the change adds no text that decides when the page applies. The catalog row in the playbook list still matches the page.
- enforcement: every new must or never has a rules row; the new branch rule is marked `prose`; the new tag names a case that exists in `parts/outward_write.cases.json`; and the guard row's claims (a gh write or push outside the list, an approval on any repository, any `gh api graphql`) match the parts table and decision 0004.
- eval-case: the page is `proof: unproven`, `prove-by: M8`, so the new branch check needs no eval case yet.

## Re-check

A fresh session re-read the page on 2026-11-23 after B2t's fix round, with `git diff fad9f23`, procedure endings, changing the machinery, the contract, `outward-repos.json`, the `outward_write` case names, the parts table's `outward_write` row, and the other five pages of this batch that share the off-`main` rule: architecture review, the review orchestrator, defect escape analysis, tracker operations and federated search. `python3 ws.py check` passes, with only the known warning on fix a bug's eval record.

| # | Verdict | Evidence |
|---|---|---|
| 1 | holds | Step 7 now says, by exception to procedure endings, that when the branch checked out is not `main`, the log row is left uncommitted and its text goes in the report. With no commit, procedure endings' push from a pull request's branch has nothing of this page's to carry. A new rules row holds it. Verified: the text. |
| 2 | holds | The "Create a pull request" row now gives the reason as "the push acts on the branch checked out", which is true of `git push -u origin HEAD`. `gh pr create` takes `--head BRANCH`. Verified: the row and `gh pr create --help`, as the first reading ran it. |
| 3 | holds | The row now opens "BRANCH is the branch the request names; by default, the one checked out", so the command's placeholder is defined and the check has a default. A detached HEAD prints nothing for `git branch --show-current`, so it is a mismatch and opens nothing. For a pinned repository, the page's rule adds `-C src/REPO` to every `git` command, the check included. Verified: the row and the paragraph above step 1. |
| 4 | holds in part | The GitHub row of "What exists today" now says a write to a pinned repository also needs it in `outward-repos.json`, which only a person edits, and that until then the guard refuses it and the person gets the text. Verified: the row, `outward-repos.json` and the case names. Still open: the rules row "Never write to a repository other than this one and those pinned under `src/`" still carries the tag `outward_write#gh pr create on a repository outside the list is refused`. That tag enforces the list, not the rule's set, which differ when a team lists a repository it does not pin. The review orchestrator's matching row was reworded in this round to say so; this one was not. Not blocking. Verified: both rows. |
| 5 | holds | Step 7 links procedure endings' "The report" and names any refusal and anything left uncommitted or unpushed. Verified: the text. |

Broke:

- Not blocking. Two pages in this batch now give different exceptions for the same situation, a question-log row while a branch other than `main` is checked out. This page leaves the row uncommitted. Architecture review, the review orchestrator and escape analysis commit it on the branch and push nothing. Tracker operations and federated search give no exception at all; see their records. Each choice is safe on its own page, but an agent that runs a review and then opens the pull request in one session meets both. Verified: the texts of the six pages. Inferred: that one session runs both.

Missed:

- none.

## Known defects

Items found after this page's re-check, which the plan allows no further fix round. Each stays here.

- Q42's second fix round, swept by neither round: step 7 and the rules row keep their own rule, "by exception to" procedure endings, that off `main` the question-log row is left uncommitted. Procedure endings now says that off main the row is committed on the branch and nothing is pushed, and that a worktree made for pages alone is not off main, which this page's "not `main`" catches. Neither path carries code to main. Found by the second re-check of tracker operations and federated search. For M8.
