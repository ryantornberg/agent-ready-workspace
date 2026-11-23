---
kind: how-to
lane: product
proof: unproven
prove-by: M9
last-reviewed: 2026-11-23
---

# Checking a shelved predecessor

When and how to check a shelved predecessor for a bug's fault, for the agent or developer handling a major security bug.

**In short:** check the predecessor only for a major security bug. The result is one origin line on the ticket: introduced here, carried over, or unknown, marked verified or inferred, naming the commit checked. Read the predecessor; never edit it.

This is a lane draft: product lane. It has not been run on real work yet; M9 runs it, as [decision 0006](decisions/0006-what-proven-means.md) says.

## When it applies

A shelved predecessor is an older version of the product, kept read-only for audits. Here it is `src/orders-service-v1`, which `src/orders-api` replaced. The contract keeps it read-only, and the `shelved` hook refuses any edit there.

| The bug | What to do |
|---|---|
| A major security bug | Run the steps below. |
| Any other bug | No check. The ticket names the predecessor only when the filer already knows it has the fault. |

Default: a bug is a major security bug when it carries `kind:security` and `affects:end-user` or `affects:staff`, as [the triage labels](triage-labels.md) define them. When the bug has no labels yet, judge from its text as the triage labels define them, and say so in the report. When the person or the ticket says otherwise, that wins.

## Steps

1. **Confirm it applies.** Input: the ticket key the request names. Read the ticket as [tracker operations](playbooks/tracker-operations.md#steps) says in its steps 1 and 2; its draft mode applies when the session has no tracker tool. Output: the ticket's labels and its code pointer. If the bug is not a major security bug, stop: write nothing, and report why.
2. **Find the fault in the live code.** Input: the ticket's code pointer, by file and name. Look the name up with `python3 tools/symbols.py NAME src`. Read the code until you can say what makes the fault: a missing check, a wrong value, an unsafe call. Output: the fault in one sentence, and the names involved. Default: when the ticket has no code pointer, ask the person for one; with no answer, go to step 6 with origin unknown.
3. **Name the commit you check.** Input: the repository that holds the predecessor. Run `git fetch origin`, then `git rev-parse origin/main`. For a predecessor pinned under `src/REPO`, add `-C src/REPO` to both. Output: the commit checked.
4. **Read the predecessor at that commit.** Input: the names from step 2 and the commit. Search it read-only, at that commit: `git grep -n "NAME" origin/main -- src/orders-service-v1`, and `git show origin/main:PATH` to read a file. For a predecessor pinned under `src/REPO`, add `-C src/REPO` and drop the path after `--`. Look for the same fault, which may sit under a different name. Never open the predecessor's files with an edit tool. Output: the code that matches, or none.
5. **Decide the origin.** Input: steps 2 and 4. Pick one:
   - **carried over:** the predecessor has the same fault;
   - **introduced here:** the predecessor does the thing correctly, or does not do it at all;
   - **unknown:** you cannot tell from what you read.

   Mark it **verified** only when you ran the fault's input against the predecessor and saw the result: the fault reproduced, for carried over, or the input refused, for introduced here. Run it only in a temporary copy of the commit checked, outside the workspace, made as [bug grooming](playbooks/bug-grooming.md#steps)'s step 3 makes one. Mark it **inferred** when you concluded it from reading the code. Default: when torn between two, choose unknown. Output: the origin and its mark.
6. **Write the origin line.** Input: the origin, its mark and the commit. Write one line for the ticket's "For developers" layer, as the [bug report template](templates/bug-ticket.md) lays it out. Its shape: `Origin: carried over from orders-service-v1 (inferred), checked at <commit>.` For carried over or introduced here, also set the matching predecessor label from [the triage labels](triage-labels.md#the-optional-label); for unknown, set none. Both are tracker writes: make them as [tracker operations](playbooks/tracker-operations.md#which-writes-need-a-yes) says. A request that asks for the origin to be recorded on the ticket is their yes. Default: with no yes, write nothing and put the line in the report. Output: the line, written or waiting.
7. **Record a fix decision, if one is made.** Input: a developer's decision on whether the predecessor also gets a fix. Any developer may make it; the agent never does. When one gives it, record it on the ticket as `Predecessor fix: yes, <initials>, <YYYY-MM-DD>.` or `Predecessor fix: no, <initials>, <YYYY-MM-DD>.`, through tracker operations. Default: with no decision, write nothing. Output: the decision line, or none.
8. **Finish.** End as [procedure endings](procedure-endings.md) says. The report gives the origin line, its mark, the commit checked, and each tracker write made or waiting. Apart from a question-log entry, this page writes no file in this repository.

Stop when the report is given.

## A fix in the predecessor

This procedure never edits the predecessor. A fix there is a separate change, never part of this procedure. In this sample, the contract keeps `src/orders-service-v1` read-only and the `shelved` hook refuses edits there. So a decision to fix it goes in the report for the person; no step here acts on it.

## Example

Invented: `ORD-426` says any signed-in person can lift another account's hold. The live code is `AccountFreeze.Lift` in `src/orders-api/AccountFreeze.cs`. The predecessor's `OrderService` has no holds at all. So the origin is introduced here, inferred from reading, and the line reads `Origin: introduced here (inferred), checked at <commit>.` The bug gets `predecessor:introduced-here`.

## Rules

| Rule | Enforced by |
|---|---|
| Check the predecessor only for a major security bug; for any other, the ticket names it only when the filer already knows. | `prose` |
| The origin line names the origin, its verified or inferred mark, and the commit checked. | `prose` |
| The predecessor label is set only after a check, and never for an unknown origin. | `prose` |
| Never edit the predecessor from this procedure. | `shelved#an edit inside the shelved folder` |
| Only a developer decides whether the predecessor gets a fix; the ticket records it with initials and date. | `prose` |
| Every write on the ticket follows tracker operations; with no yes, nothing is written. | `prose` |
