---
kind: playbook
lane: product
proof: unproven
prove-by: M9
last-reviewed: 2026-11-23
---

# Bug grooming

How an agent checks a filed bug, fills its gaps and sizes it, for the agent asked to groom a bug.

**In short:** bugs only. Read the ticket and stop if it is groomed or closed. Search for duplicates. Re-check every claim in a fresh session at the tip of main. Hold the ticket against the bug report template, list each gap with proposed text, and size it. Change the ticket only when the person asks.

This is a lane draft: product lane. It has not been run on real work yet; M9 runs it, as [decision 0006](../decisions/0006-what-proven-means.md) says.

A groomed bug is ready for a developer. It goes to [fix a bug](fix-a-bug.md) when it passes [the size gate](../size-the-work.md#the-gate), and climbs [the ladder](../size-the-work.md#the-ladder) when it does not, as the contract's "How work flows" says.

## Steps

1. **Read the ticket.** Input: the ticket key the request names. Read it as [tracker operations](tracker-operations.md#steps) says in its steps 1 and 2; its draft mode applies when the session has no tracker tool. Output: the ticket's text, type, status, labels, fields and attachments. Stop, with no write, when it is not a bug, or when its status is groomed or later, or closed. The groomed status is the team's name for it; default: `Groomed`. Default: when you cannot tell whether a status comes after groomed, ask the person; with no answer, stop with no write.
2. **Search for duplicates.** Input: the ticket's fault, in its own words and in the code's names. Search the tracker, open and closed tickets, as the [bug report template](../templates/bug-ticket.md#before-you-write) says. In draft mode, ask the person to run the search; with no answer, carry on and say in the report that no search was made. Output: each likely duplicate, or none. Default: when one is found, stop grooming and go to step 8. Report the duplicate; linking or closing either ticket is a write for the person to ask for, through tracker operations.
3. **Re-check every claim in a fresh session.** Input: the ticket's text. Hand it to a fresh session as [orchestration](../orchestration.md#handing-work-off) says, with a prompt that starts `Tier: worker`. Give it the ticket, not your reading of it. It runs `git fetch origin` and `git rev-parse origin/main` in the repository that holds the code (add `-C src/REPO` for one pinned under `src/`, to every `git` command here). It never checks out that commit in the main working copy or in a pin: another session may be working there. It makes a copy of that commit in a new temporary folder outside the workspace, `git worktree add --detach TEMP origin/main`, reproduces each claim there, then runs `git worktree remove TEMP`. It returns one verdict per claim: holds, disproved, or could not check, each marked verified or inferred. Default: the person's local environment; a shared environment needs the person's yes first. When the ticket has no screenshot and the bug is visible, it captures one with a browser, as [browsers](../browsers.md) says, and keeps the file outside the repository. Output: the verdicts, the commit measured, and any screenshot.
4. **Hold the ticket against the template.** Input: the ticket and the verdicts. Check each item below, in order, against the [bug report template](../templates/bug-ticket.md). For each gap, write the text you propose. Output: the list of gaps, each with its proposed text.
   - A plain title: what goes wrong for a person, then what sets it off.
   - Labels as [the triage labels](../triage-labels.md) say: one from each category, one area. When the ticket has an `effort` label, propose removing it together with step 5's size, so a bug never shows two sizes.
   - The summary: what goes wrong, and for whom, in two sentences at most.
   - The headings in the template's order, with the technical part collapsed under "For developers".
   - An impact that can be groomed: who is affected and how many, or, when nobody yet, what it costs the team and what would make it visible.
   - The commit from step 3 under "Environment and version", as the commit measured, so the fixer need not re-verify.
   - Evidence, measured at that commit.
   - A code pointer by file and name, never by line number. Find it with `python3 tools/symbols.py NAME src`.
   - Out of scope, holding each claim step 3 disproved, with what disproved it, and each claim it could not check, as unknown.
   - For a major security bug, as [checking a shelved predecessor](../predecessor-check.md#when-it-applies) defines it, the origin line: run that page's steps 2 to 5 and propose its line and label here.
   - Acceptance criteria, each one observable.
   - Every field the groomed status requires, read from the ticket in step 1.
5. **Size it.** Input: the ticket and the code pointer. Give the whole fix, tests included, one score from the [effort estimate's rubric](effort-estimate.md#the-rubric), and map each end of its range with [its story points table](effort-estimate.md#story-points). That page's steps size features; a bug borrows only these two tables. Default: a fix under 10 lines scores small; between two scores, take the larger. Output: a range of lines, never one number, its points, and a one-line reason. When both ends give the same points, give that one value. Leave alone every field the product owner owns. Default: priority, the release, the assignee and any due date are the product owner's.
6. **Ask once.** Input: the gaps and the size. Show every proposed change in one message: each new text, the commit measured, each label added or removed, the size, any screenshot to attach, and the move to groomed. The `effort` label goes only with the size: when the person declines the size, keep the label. Ask which to make. Changes the request names in its own words are already its yes, as [tracker operations](tracker-operations.md#which-writes-need-a-yes) says. Default: with no answer, make none; they go in the report as proposed. Output: the changes to make.
7. **Apply the changes.** Input: the changes to make. Make only those, as [tracker operations](tracker-operations.md#steps) says in its steps 5 and 6. Make them in this order:
   1. The text, the commit measured, the fields, the size, the labels and any screenshot.
   2. Move the ticket to groomed, last, once every field that status needs is set.

   In draft mode, write each change as text for the person instead. Output: each change made and confirmed, or its text. If a write is refused, make no write that depends on it, and go to step 8.
8. **Finish.** End as [procedure endings](../procedure-endings.md) says. The report gives each claim's verdict with its mark, the commit measured, every change made, and every change proposed and not made. A helper's verdict is a claim, not a result you saw: report it as inferred unless you saw the result yourself, as [orchestration](../orchestration.md#delegating) says. Apart from a question-log entry, this page writes no file in this repository.

Stop when the report is given.

## Example

Invented: `ORD-421` says a hold placed on an account is lifted when the nightly job runs. Step 3 reproduces it at the tip of main: the hold is lifted, verified. The ticket also claims held orders ship that night; the helper could not check shipping locally, so that claim is marked could not check, and step 4 proposes moving it to "Out of scope" as unknown. The code pointer is `ReconciliationWorker` in `src/orders-api/ReconciliationWorker.cs`. The person approves every change but the size, which stays proposed, so the filer's `effort` label stays too.

## Rules

| Rule | Enforced by |
|---|---|
| Groom bugs only; stop with no write on a ticket that is groomed or closed. | `prose` |
| Re-check every claim in a fresh session at the tip of main, and name the commit measured. | `prose` |
| Give the helper the ticket, not your reading of it. | `prose` |
| Measure in a temporary copy outside the workspace; never check out another commit in the main working copy or a pin. | `prose` |
| Keep a screenshot outside the repository. | `prose` |
| Give the size as a range of lines, never one number. | `prose` |
| A disproved claim moves to "Out of scope" with what disproved it; it is never deleted. | `prose` |
| Never change a field the product owner owns. | `prose` |
| Change the ticket only as the person asks, through tracker operations; with no answer, change nothing. | `prose` |
| Remove the `effort` label only with the person's yes and only when the size is set too, so a bug never shows two sizes. | `prose` |
| Move the ticket to groomed last, after every field it needs is set. | `prose` |
| A shared environment is used only on the person's yes. | `prose` |
| Mark every claim in the report verified or inferred. | `eval:fix-a-bug` |
