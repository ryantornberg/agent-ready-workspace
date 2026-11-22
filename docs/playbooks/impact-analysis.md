---
kind: playbook
proof: unproven
prove-by: M6
last-reviewed: 2026-11-21
---

# Impact analysis

How an agent lists everything a change to a path or a name reaches. For an agent closing out a change, or planning one.

**In short:** start from the changed paths and names. Match them against INDEX.md's cross-cutting chains, find every use in the code, read their recent history and find the docs that name them. Report one ranked list that names each use you looked at and each one you did not.

## When it runs

- Step 6 of [the feature ladder](../size-the-work.md#the-feature-ladder) sends you here to close the loop on a built change.
- A person asks what a change to a path or a name would touch.
- You are writing the slices of a hand-off plan and need to know what its goal reaches.
- The [review orchestrator](review-orchestrator.md)'s docs drift dimension sends its reviewer here for the pages likely stale, which step 5 finds. That reviewer runs step 1 on the range its dispatch gives, then step 5 only, and replies in the shape its dispatch asks for. It skips step 7's offer and step 8's return, and puts any offer in its reply.
- A person asks for an impact analysis of a branch or a pull request on its own. When the request asks for a review, the review orchestrator wins and runs this page as its docs drift dimension.

Two other pages map what a change reaches on their own route, and each wins there:

| You are working through | Use |
|---|---|
| [Fix a bug](fix-a-bug.md) | Its step 4, which lists the callers of the code you changed. This page is not needed there. |
| [Safe refactor](../safe-refactor.md) | Its step 4, which maps the blast radius of the names you move. |
| Anything else | This page. |

This procedure only reads. It changes no file: a new [INDEX.md](../../INDEX.md) row the person agrees to in step 7 waits in the report for its eval run.

## Steps

1. **Name the targets.** Input: the change in the working copy, a pull request, a range of commits you were handed, or the request or plan that names what will change. For a change in the working copy, list its paths with `git diff --name-only $(git merge-base origin/main HEAD)`, which covers commits and uncommitted edits since the branch left main, and its new files with `git status --short`. For a pull request, use `gh pr diff NUMBER --name-only`. For a range, such as one a review dispatch gives, use `git diff --name-only FIRST..TIP`. For a change not made yet, take the paths and names the request or plan gives. Then add each name the change defines, renames or deletes, such as a class, a method or a setting key. Output: a list of paths and a list of names. If both lists are empty, stop and report what you were given and that it names nothing to trace.
2. **Match the chains.** Input: the paths, and what kind of change it is. Each row of [INDEX.md's cross-cutting chains](../../INDEX.md#cross-cutting-chains) is keyed by a kind of change. A row matches only when its Change column describes your change, and one of your paths equals one of the row's paths or sits under one of its folders. A path under a folder the row lists, such as `docs/`, does not match on its own. Output: each matching row, and every other path it lists. Those paths change together: each one the change leaves alone goes on the list, with the reason. Default when no row matches: write "no chain" and go on.
3. **Find every use in the code.** Input: the names. For each name, find its definition with `python3 tools/symbols.py NAME FOLDER` and its uses with `git grep -n NAME -- FOLDER`. FOLDER is `src` for code, and for machinery the folder that holds the change, such as `wslib`, `parts` or `tools`. Default when unsure: run both. For a path that defines no name, such as a settings file, search for its file name instead. Default for a name too common to search, such as `Id`: search for the form a caller writes, such as `Order.Id`, and say so. Output: each use, with the folder it sits in. A use in another folder than the change is a call across repositories, such as an interface `src/orders-web` calls. A use in `src/orders-service-v1` is a copy kept read-only for audits: list it and never change it.
4. **Read the recent history.** Input: the paths. Run `git log --all --oneline -n 10 -- PATH` for each path. Output: the recent commits that touched them, on main and on other branches. Mark a commit that fixed the same code, and a commit on a branch not yet merged: that is other work that may collide with yours.
5. **Find the docs that name them.** Input: the names and paths. Run `git grep -n NAME -- '*.md'` for each name and each path. Leave out hits under `docs/records/`, `docs/plans/` and `docs/milestones/`, and in the [question log](../question-log.md): they record what happened and are not updated. Output: the pages likely stale. A name in [INDEX.md's search aliases](../../INDEX.md#search-aliases) or in [AGENTS.md](../../AGENTS.md) is one the `aliases` check holds to the code, so a rename or delete of it changes a file the eval covers: mark it so.
6. **Rank the list.** Input: the outputs of steps 2 to 5. Put them in this order, most urgent first:
   1. Uses in the same repository as the change, which break its build or tests if they are wrong.
   2. Uses in another repository.
   3. Chain paths that change together with yours.
   4. Docs likely stale, with a name the `aliases` check holds first.
   5. Commits on branches not yet merged that touch the same paths.
   6. Read-only copies in `src/orders-service-v1`, listed and left alone.

   Mark each item "looked at" when you read it or ran a test that covers it, and "not looked at" with the reason otherwise. Output: the ranked list.
7. **Offer to write down a new relationship.** Input: any path you found that changes with yours and that no chain row lists. Make the [research ladder's offer](../research-ladder.md#offer-to-write-a-finding-down): one line naming the new row for INDEX.md's cross-cutting chains. INDEX.md is a file the eval covers, so a yes does not write it now: put the row in the report as `waits for an eval run`, for the person to batch with other such edits, as the contract says. Default with no answer: put the offer in the report. Either way, nothing is written. Output: the offer, or "no new relationship".
8. **Report.** Input: the outputs of steps 1 to 7. Give the ranked list, the chain rows, the stale docs, the commits and the offer. Mark each claim verified or inferred. When you ran this for the feature ladder, or for the impact check the [definition of done](../definition-of-done.md) asks for, the list goes into that report, and you return to the step that sent you.

Stop when the report is written. Stop early, and report, when step 1 finds nothing to trace. A lookup that finds nothing does not stop the procedure: write "none found" with the command, and go on.

## Rules

| Rule | Enforced by |
|---|---|
| The list names each use you looked at and each one you did not. | `prose` |
| Never change `src/orders-service-v1`; list its copies and leave them alone. | `shelved#an edit inside the shelved folder` |
| The procedure changes no file. A new chain row is offered in one line, and on a yes waits in the report for its eval run. | `prose` |
| Mark every claim in the report verified or inferred. | `eval:fix-a-bug` |
