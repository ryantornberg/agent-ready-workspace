---
kind: decision
status: proposed
date: 2026-11-23
deciders: each instance's DevOps owner, for the product repositories it pins
last-reviewed: 2026-11-23
lane: devops
---

# 0019: Product repositories land every fix on trunk first, with one locked release branch per release

**In short:** proposed as an example convention, not a rule here. Every fix merges to trunk first, there are no hotfix branches, each release has one locked release branch, and every pull request title carries a tracker key. Each instance's DevOps owner decides whether its product repositories adopt it. This workspace pins none, so it decides nothing here.

## Context

Teams that kept several release lines lost fixes. A fix made on a hotfix branch never reached trunk, or reached it in a different form, and the next release shipped the bug again. Without a tracker key in each pull request, nobody could trace which change shipped which fix.

This workspace has no product repositories of its own; its sample code is invented. So the convention is recorded here for an instance to adopt or refuse.

## Decision

Proposed, for an instance's DevOps owner to accept or reject for the repositories that instance pins:

- **Trunk first.** Every fix merges to trunk before it goes anywhere else.
- **No hotfix branches.** A fix for a release is cherry-picked from trunk to that release's branch.
- **One release branch per release,** locked so that only those cherry-picks land on it.
- **A tracker key in every pull request title,** so each change traces to its work item.

Rolling it out would change two pages that today allow the key in a pull request's description as well as its title: the [pull request template](../templates/pull-request.md) and [git-host operations](../playbooks/git-host-operations.md). It would also need a step that announces the change to the team.

In an instance this record is a kit file, so an edit to its status counts as drift. To accept or reject it there, first keep it with `python3 ws.py drift --keep PATH`, as [decision 0007](0007-the-kit.md) says.

## What it gave up

- **Every fix waits for trunk.** An urgent fix goes through trunk's checks before it can reach a release.
- **Cherry-picks can conflict** when a release branch has moved far from trunk.

## Options rejected

- **A branching model of the team's own.** It would be one more model to teach, with no measured gain.
- **Current habits.** They are what lost the fixes.
