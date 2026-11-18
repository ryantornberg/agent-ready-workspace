---
kind: how-to
proof: unproven
prove-by: M9
last-reviewed: 2026-11-15
---

# Size the work first

How much process a change gets. It is for the agent deciding how to start, and for the person who will read its plan.

**In short:** a change that is small, easy to reverse, in one repository and under a day of work goes straight to [fix a bug](playbooks/fix-a-bug.md). Everything else climbs a ladder, and stops climbing as soon as the work allows.

## The gate

A change skips the ladder only when all four hold:

1. **Small.** One screen of diff, give or take.
2. **Easy to reverse.** Reverting the commit undoes it. No data migration, no published release, no message sent.
3. **In one repository.**
4. **Under a day of work.**

If any one fails, or you cannot tell, climb the ladder. A change that turns out bigger than it looked stops and climbs from where it is.

## The ladder

| Rung | What it produces | Here |
|---|---|---|
| Bound | The goal and the non-goals, written before anything is touched. Non-goals stop an agent doing more than was asked. | A section of the hand-off plan |
| Grill | The agent asks the person about the design until the open questions are settled. | Not written yet |
| Spec | What will be true when the work is done. | Not written yet |
| Plan | Slices an agent can run, each with its own checks and tier. | [Hand-off plan template](templates/hand-off-plan.md) |
| Red team | A fresh session attacks the plan. Every finding is triaged. | A section of the hand-off plan |
| Execute | Run the slices, verify each one, record what happened. | [Definition of done](definition-of-done.md) |

Skip a rung only when the rung below it already holds its answer. A bug report with a clear cause needs no grill. A plan nobody has red-teamed does not get built.

A call that is hard to reverse also becomes a [decision record](decisions/0001-pin-code-repositories.md): the choice, the options and what it gave up.

Work that runs for weeks is one milestone. It gets a hand-off plan and, at the end, a [milestone record](templates/milestone-record.md).
