---
kind: reference
last-reviewed: 2026-11-24
---

# Request map

Short requests a person types, what each one sets off, and the page that defines it. For the person asking and the agent answering.

**In short:** common kinds of work once had no entry point, so a person had to explain each one again. Each row below maps a one-line request to its page. The defaults apply to every request without being said. When one line is not enough, write a fresh-session prompt.

## One-line requests

The page in each row owns the steps. This table only routes.

| A person says | The agent | Page |
|---|---|---|
| "Fix this bug", "pick up this ticket and fix it" | Sizes it, then fixes it test first, or climbs the ladder when it is not small. Moves the ticket only as tracker operations allows. | [Size the work](size-the-work.md), [fix a bug](playbooks/fix-a-bug.md), [tracker operations](playbooks/tracker-operations.md) |
| "Build this feature" | Climbs the feature ladder: goal and non-goals, a spec, a plan. | [The feature ladder](size-the-work.md#the-feature-ladder) |
| "Why does this fail?", "debug this" | Finds the cause before any fix, and leaves its repro test uncommitted for the person. | [Debugging](playbooks/debugging.md) |
| "Refactor this" | Changes structure, not behavior, behind a characterization test. | [Safe refactor](safe-refactor.md) |
| "Try a few versions of this screen" | Builds a throwaway prototype to answer a question of feel. | [Throwaway prototype](playbooks/throwaway-prototype.md) |
| "What does this change touch?" | Lists callers, chains and pages likely stale. | [Impact analysis](playbooks/impact-analysis.md) |
| "Where is X?", "how does Y work?" | Picks one lookup by what it already knows. | [Research ladder](research-ladder.md) |
| "Search the tracker, the wiki or chat for X" | Searches outside the workspace, each source in turn. | [Federated search](playbooks/search-every-source.md) |
| "Create a bug for this" | Writes the ticket, checking every claim first, and files it as tracker operations allows. | [Bug report template](templates/bug-ticket.md), [tracker operations](playbooks/tracker-operations.md) |
| "Is this ticket accurate?" | Checks each claim and answers. It rewrites the ticket only on the person's yes. | [Bug report template](templates/bug-ticket.md), [tracker operations](playbooks/tracker-operations.md#which-writes-need-a-yes) |
| "Review this pull request" | Reviews it as the review orchestrator says, reading its files from a worktree where the review needs them. | [The review orchestrator](playbooks/review-orchestrator.md), [review in a worktree](review-in-a-worktree.md), [code review](code-review.md) |
| "Walk me through the comments on this pull request" | Goes through each comment with the person. | [Feedback walk-through](playbooks/feedback-walkthrough.md) |
| "That pull request merged, do the bookkeeping" | Works down the list for after a merge. | [Pull request template](templates/pull-request.md#after-the-merge-the-bookkeeping-list) |
| "Red-team this plan" | Hands the plan to a fresh critic and triages what it finds. | [Red team review](playbooks/red-team-review.md) |
| "Interview me on this" | Asks about the design until the open questions are settled. | [Decision interview](playbooks/decision-interview.md) |
| "Review this page", "check these instructions" | Has a fresh session review a guidance page. | [The instruction review](playbooks/instruction-review.md) |
| "Give me a prompt for a new session" | Writes one prompt to paste whole. | [Fresh-session prompt template](templates/fresh-session-prompt.md) |
| "Hand off", "I am low on context" | Writes a note a later session resumes from. | [Handoff](playbooks/handoff.md) |
| "Add a page", "fix this page" | Sizes it, then writes or edits the page and has it reviewed. | [Extend the workspace](extend-the-workspace.md) |

Requests for a role's lane, such as a regression run or a standup report, start from [reading paths by role](reading-paths.md).

## Defaults nobody has to say

These hold for every request unless the person says otherwise.

| Default | Where it is stated |
|---|---|
| A question gets an answer, not a change. Debugging's repro test, left uncommitted, is the one exception. | Here. |
| The live service, not the shelved one. | [The contract](../AGENTS.md#facts-a-model-cannot-derive) |
| Measure at the tip you will ship against, and name the commit. | Here, and the [fix brief](playbooks/fix-a-bug.md#the-fix-brief)'s first part. |
| Check in a local environment that no other session shares, never on shared data. | The [definition of done](definition-of-done.md)'s running-app row |
| A review runs in a fresh session, and its findings are verified before they are acted on. | [Orchestration](orchestration.md#fresh-context-for-critics), [the instruction review](playbooks/instruction-review.md#steps) |
| Every claim is marked verified or inferred. | [The contract](../AGENTS.md#rules) |
| One example stands for a category: one screenshot with one symptom means find every instance and the shared cause. | Here. |
| A fault the change caused is fixed in it. A fault it did not cause is written down, not fixed. | Here for the first half; the [definition of done](definition-of-done.md#the-list) for the second. |
| When a step needs a person to sign in, the agent waits for them. It never signs in for them. | Here. |
| Plain language. | [The style guide](authoring.md) |

## When one line is not enough

A request needs more than one line when it carries a decision the agent cannot make, such as a scope, a deadline or a risk the person accepts. It also needs more when it hands work to a fresh session that knows nothing of this one. Write it with the [fresh-session prompt template](templates/fresh-session-prompt.md).

## Rules

| Rule | Enforced by |
|---|---|
| A question gets an answer, not a change. | `prose` |
| A fault the change caused is fixed in it. | `prose` |
| Measure at the tip you will ship against, and name the commit. | `prose` |
| One example stands for a category. | `prose` |
| When a step needs a person to sign in, the agent waits; it never signs in for them. | `prose` |
