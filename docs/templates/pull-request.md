---
kind: template
last-reviewed: 2026-11-22
---

# Pull request description template

The shape of a pull request's title and description, and the bookkeeping after it merges, for anyone opening or merging one. A copy's readers are a reviewer, a tester and the person who merges.

**In short:** the title and a first line of two sentences at most form the top layer. Then six fixed headings: changes, why, verification, review, decisions made without asking, and testing. State facts; do not tell the story. After the merge, work down the bookkeeping list.

## When to use it

Use it whenever you write or rewrite a pull request's description, in this repository or one pinned under `src/`. Creating, editing and publishing the pull request are [git-host operations](../playbooks/git-host-operations.md#the-operations). That page also says where a ticket's key goes and how to link a file of this workspace. Posting on another person's pull request is an outward write: see [outward writes](../procedure-endings.md#outward-writes).

The description lives on the pull request. Write it to a file in your scratch folder and pass it with `--body-file`, as git-host operations does.

## Skeleton

```markdown
<One or two sentences: what the change does and why it matters. Link the ticket or the plan.>

## Changes

- <One bullet per change, stated as what it does now.>

## Why

<The problem or the goal, in a few sentences.>

## How it was verified

- verified: <a command you ran, and what you saw>
- inferred: <something you reasoned out and did not run>

## Review

<A link to the review record for this tip in the hand-off plan; with no plan, the record itself; or "No review ran.">

## Decisions made without asking

<Each choice you made alone: the choice, what you rejected, and why. Or "none".>

## What testing needs

<What a tester should check, where, and in which build. Or "nothing: no behavior a tester sees changed".>
```

## Filling it

The page follows the [reader standard](../reader-standard.md).

- **Order.** Keep the skeleton's headings, worded as given, in its order. Never reorder or rename them.
- **Top layer.** The title and the first line, at most 60 words together. A reviewer, a tester or the person who merges who reads only that knows what merges and why.
- **Title.** What the change does, in the form [commits](../commits.md#the-subject-line) gives a commit's subject, since the merge commit carries it. When the team's subject format puts a ticket's key first, so does the title.
- **First line.** The summary, in one or two sentences. A reader who stops there knows what merges.
- **Changes.** One bullet per change. Say what the code or page does now, not what you did first and undid.
- **How it was verified.** Mark each line verified or inferred, as a report does: see [the report](../procedure-endings.md#the-report).
- **Review.** Link the review record for the tip you are opening. It sits in a hand-off plan's Results. With no plan, paste the review orchestrator's record for the tip into this section. The [review orchestrator](../playbooks/review-orchestrator.md) writes it. On the fix a bug path, say plainly when no review ran.
- **Decisions made without asking.** The same section the [hand-off plan](hand-off-plan.md#how-to-use-it) has, for the same reason: a reviewer can see each choice and challenge it. A choice the person made is not listed here.
- **What testing needs.** For a change a tester sees: what to check, on which environment, in which build or commit.
- **Length.** Under 4,000 characters. Detail beyond that goes in the plan or the record the description links.
- **An empty heading.** Drop a heading that has nothing under it, except three. "Review" says "No review ran.", "Decisions made without asking" says "none", and "What testing needs" says "nothing: no behavior a tester sees changed".

## A worked example

The pull request below is invented: no such change was made, and ORD-117 is an invented ticket key. It fixes the bug in the [bug report template](bug-ticket.md#a-worked-example)'s example, and the code it names is real. It shows a top layer with no story, and every heading kept.

Title: `fix(orders-web): write a header line in the quarterly orders report`

```markdown
The quarterly orders report now starts with a line of column names, so the finance import loads every order. Fixes ORD-117.

## Changes

- `QuarterlyExport.toCsv` writes a header line before the order rows.
- A test checks that the first line of the report is the header.

## Why

The finance import reads the first line of the file as column names. With no header line, it skipped the first order and the quarter totals came out low.

## How it was verified

- verified: the new test passes, and the full test run passes at the tip.
- verified: a report built at the tip has 413 lines for a quarter of 412 orders.
- inferred: the finance import loads all 412, since it expects one header line; nobody ran the import.

## Review

No review ran.

## Decisions made without asking

- The column names match the order fields' names in the code. I rejected friendlier names, since the import maps columns by name and nobody gave me its mapping.

## What testing needs

On the test environment, at this pull request's commit: load a quarter's report into the finance import. Check that every order of the quarter loads.
```

## After the merge: the bookkeeping list

Work down this list once a pull request merges. Do it when you merged it, or when a person asks for the bookkeeping on a merge. Each row names the page that does the work. A write outside this repository follows [outward writes](../procedure-endings.md#outward-writes). End as [procedure endings](../procedure-endings.md) says.

| Item | What to do | The page that does it |
|---|---|---|
| The tracker item | Move the ticket on, update its test notes, and do the post-merge security review when the team's workflow asks for one. | [Tracker operations](../playbooks/tracker-operations.md#the-operations), and [its security review](../playbooks/tracker-operations.md#the-post-merge-security-review). |
| The branch | For a merge in a pinned repository, add `-C src/REPO` to each `git` command here. If the branch had a worktree, remove it first, after the check in review in a worktree's step 6. Then delete your local branch with `git branch -d BRANCH`. In this repository, `python3 ws.py merge` already deleted the branch on GitHub. After a merge made another way, `git ls-remote --heads origin BRANCH` prints nothing once the branch is gone. If it prints a line, the deletion is `git push origin --delete BRANCH`. Who runs it follows [the push](../procedure-endings.md#the-push)'s table: in a team's workspace, a person runs it and the agent gives the command. | [Changing the machinery](../changing-the-machinery.md#the-path-for-a-machinery-change) for the merge; [review in a worktree](../review-in-a-worktree.md#steps), step 6, for the check before removing a worktree. |
| Pins under `src/` | When the merge was in a pinned repository, move its pin forward and re-run the checks. This repository has no pins. The code map is planned for M5. | [Maintain the workspace](../maintain-the-workspace.md#duties-an-event-sets-off), the pin row; [decision 0001](../decisions/0001-pin-code-repositories.md). |
| The plan's Results | When the work has a hand-off plan, append the slice's report under "Results". | [Hand-off plan](hand-off-plan.md#how-to-use-it), rule 6. |
| Docs | Fix each page whose claim the merge made untrue. Add a page the change needs. | [Maintain the workspace](../maintain-the-workspace.md#duties-an-event-sets-off); [extend the workspace](../extend-the-workspace.md). |
| Stacked branches | When `python3 ws.py merge` exited 0, it already retargeted each open pull request based on the merged branch, before it deleted the branch, and named each; do not publish one until the person says whether its earlier review stands, as the retarget row says. When it exited 2, or the merge was made another way, such as from the web page, for each open pull request based on the merged branch, read its base with `gh pr view NUMBER --json baseRefName`. If it still names the deleted branch, it needs a retarget to the merged pull request's base. Ask first, unless the request names the retarget in its own words, as the retarget row says. | [Git-host operations](../playbooks/git-host-operations.md#the-operations), the retarget row. |

## Rules

| Rule | Enforced by |
|---|---|
| A description states what is true; it does not narrate how the work went. | `prose` |
| A description holds one bullet per change, and links or holds the review record for its tip, or says no review ran. | `prose` |
| A description lists each decision made without asking, or says "none". | `prose` |
| A description stays under 4,000 characters. | `prose` |
| A description keeps the skeleton's headings in their order, and its title and first line stay within 60 words. | `prose` |
| After a merge, work down the bookkeeping list; each item follows the page its row names. | `prose` |
