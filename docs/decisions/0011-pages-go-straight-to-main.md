---
kind: decision
status: accepted
date: 2026-11-23
deciders: the maintainer, through M3's approved plan
last-reviewed: 2026-11-23
---

# 0011: Pages go straight to main, with their checks run at the commit and the push

**In short:** a change to pages only is committed and pushed straight to main, with no pull request, except a page the eval covers or a proof anchor. The commit hook runs the checks first, the pre-push hook its own push checks, and CI all of them again on main. In a team's workspace a person pushes. Machinery takes the stricter path that [changing the machinery](../changing-the-machinery.md) sets.

## Context

Most changes here are to pages: a fixed link, a clearer step, a new record. Requiring a pull request for each would add a wait and a merge to work that is easy to read and easy to undo. Without any gate, though, a broken link or a page with no review would reach main unseen.

A broken hook is different. It reaches every session that pulls it, and can lock them all out. So the scripts, hooks and CI need CI on three systems before they land.

## Decision

- **Pages go straight to main.** A guidance page goes after its [instruction review](../playbooks/instruction-review.md), a record or plan without one. In this repository the agent pushes; in a team's workspace a person does, as [procedure endings](../procedure-endings.md#the-push) says.
- **Two exceptions.** A change to a page the eval covers, such as `INDEX.md`, waits on a branch until its eval run is on record, as step 5 of [extend the workspace](../extend-the-workspace.md#steps) says. A commit that adds or changes a proof anchor merges through a pull request, as [decision 0006](0006-what-proven-means.md) says; `direct_push` refuses it at the push.
- **Checks run on the way.** The commit hook runs the checks on the staged files. The pre-push hook runs the checks that judge a push, such as the review trailer and the machinery list, on every commit a push to main adds, and refuses the push when one fails. CI runs every check again after the push, and reports a failing run.
- **Machinery goes through a pull request,** on its own branch, merged only after CI passes on Linux, macOS and Windows. The `direct_push` check refuses a push to main that changes a machinery path, and [changing the machinery](../changing-the-machinery.md#what-counts-as-machinery) lists those paths.
- **A procedure off main pushes nothing for its pages,** as [procedure endings](../procedure-endings.md#off-main) says, so a page push never carries a branch's code with it.

## What it gave up

- **No reviewer reads a page before it lands,** beyond its instruction review and the checks. A wrong sentence can sit on main until someone notices.
- **CI on main reports after the push.** The commit hook is what stops a bad page; a commit made past it, or on a machine whose hooks are not installed, sends a broken link through, and CI then reports a red run.

## Options rejected

- **A pull request for every change.** It slows the commonest and safest change in the workspace, and pushes people to batch page fixes they would otherwise make at once.
- **No checks on pages.** Broken links and unreviewed guidance would reach every session.

## Related

When the checks were first moved to run in CI, they had never run there before, and an old repository failed them on findings nobody could fix at once. The way through was a baseline of known findings that fails only on new ones; see [baselines](../parts.md#baselines).
