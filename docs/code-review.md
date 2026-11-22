---
kind: reference
last-reviewed: 2026-11-21
---

# Code review

What an agent's code review checks, and how to act on what it finds. For a person whose change is reviewed, or who asks for a review.

**In short:** several fresh agent sessions each review one side of a change, such as security or its tests, and their findings land in one table. Each finding is an obvious fix or a decision, with a severity. The [review orchestrator](playbooks/review-orchestrator.md) holds the steps; its machinery is planned for M4, so today an agent runs them by hand.

## What runs

The agent first builds and lints the change at its tip and at the commit it started from, and compares the two. On your own branch, a new error or a new warning stops the review until it is fixed, as the [definition of done](definition-of-done.md) counts them. On someone else's pull request, it becomes a finding.

Then each side of the change goes to its own fresh session, which sees the change and the request, never the author's reasoning. Five sides are always reviewed: code, architecture, security, test adequacy and reuse. Others are added when the change calls for them, such as accessibility for a screen in `src/orders-web`. Reuse and docs drift are advisory. [The dimensions](playbooks/review-orchestrator.md#the-dimensions) lists each one and when it runs.

The agent that runs the review collects the findings. It never fixes or settles them, and posts nothing without your yes.

## The two labels on a finding

Every finding has a kind and a severity, as [the playbook](playbooks/review-orchestrator.md#the-two-labels-on-a-finding) defines them:

| Label | Values | What it tells you |
|---|---|---|
| Kind | Obvious fix, or decision | Whether there is one right answer to apply, or a choice someone must make. |
| Severity | Blocker, should-fix, or nit | How much it matters, apart from its kind. |

The reviewer sets the kind. You may raise an obvious fix to a decision when you disagree with the reviewer's answer. You never lower a decision to an obvious fix.

## On your own branch

1. Ask the agent to review the branch before its pull request opens, and again before each later push. Until M4's planned gate exists, a review runs when you ask, a plan calls for one or another playbook's step does; a change on the [fix a bug](playbooks/fix-a-bug.md) path gets one only when you ask.
2. Read the report. Decisions come first, then every security and architecture finding, then the counts.
3. Settle each finding: fix it, defer it to a named place, or decline it with a reason a stranger could judge. The agent writes your answer in the record's Disposition column.
4. Ask for a review again. Whether the next round reads the whole branch or just what changed, and how it checks each fix, is in the [review orchestrator's steps](playbooks/review-orchestrator.md#steps).

Opening, publishing and merging the pull request follow [the contract's rules](../AGENTS.md#rules), not this review.

## On someone else's pull request

1. Ask the agent to review the pull request by its number. For a full review, it reads the pull request in a separate folder, as [review in a worktree](review-in-a-worktree.md) says, so your own working copy does not change. A review of one dimension alone, such as architecture, reads files at the tip with `git show TIP:PATH` and makes no folder.
2. The agent checks each finding again against the code and its history, matches it with the threads already open, and drafts one overview comment.
3. Read the draft. Nothing is posted without your yes, and it posts under your own sign-in. Say no, or ask for changes, as you would for your own comment.

## When you receive a review

Each comment opens with what goes wrong for a user or caller, then the detail, then a line saying `Suggested fix:` or `Decision needed:`.

To work through the comments with an agent, one at a time, use the [feedback walk-through](playbooks/feedback-walkthrough.md).

To answer a comment yourself:

| You | Reply with |
|---|---|
| Fixed it | The commit that fixes it, once that commit is pushed. |
| Disagree | Your reason, one a stranger could judge. |
| Were asked to decide | The decision, or the name of the person who decides. |
| Do not understand it | A question in the same thread. |

## What is planned

| Planned | Milestone |
|---|---|
| A review mark, and a gate that needs one before a pull request opens | M4 |
| Scripts that dispatch the reviewers, read their replies and write the findings table | M4 |
| Line comments on a pull request, and reading the request from a tracker | M8 |

## Rules

| Rule | Enforced by |
|---|---|
| Each reviewer sees the change and the request, never the author's reasoning. | `prose` |
| The agent that runs the review never fixes or settles a finding. | `prose` |
| Nothing is posted on a pull request without the person's yes. | `prose` |
| Until M4's gate exists, a change on the fix a bug path is reviewed only when the person asks. | `prose` |
| The reviewer sets a finding's kind; the author may raise it to a decision and never lowers it. | `prose` |
| A declined finding carries a reason a stranger could judge. | `prose` |
