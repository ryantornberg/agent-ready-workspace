---
kind: record
last-reviewed: 2026-11-22
---

# Question log

Every question someone had to ask a person because the workspace did not answer it. Each one marks context the workspace failed to carry. Log it, fix the page where the next person will look, and note the fix.

The measure of a workspace is this list getting shorter per piece of work, not the workspace getting bigger.

**Adding an entry.** Add one dated row before the session reports, and commit and push it as [procedure endings](procedure-endings.md#the-question-log-entry) says.

**Kinds of gap.** Each row names the kind of gap it marks, so the log shows where the workspace fails:

- **could not find**: the answer was in the workspace, but the asker did not reach it. Fix the route: an index row, an alias or a link.
- **did not understand**: the asker reached the answer, but it was unclear, or two pages disagreed. Fix the page.
- **not there**: the workspace did not hold the answer. Write it where the next person will look.

| Date | The question | Kind | Where the answer lives now |
|---|---|---|---|
| 2026-11-14 | Which order service is the live one? (invented example) | not there | [AGENTS.md](../AGENTS.md#facts-a-model-cannot-derive) |
| 2026-11-15 | Which model and effort should each slice of a plan run at? The maintainer had to ask; the workspace had no rule. | not there | [Orchestration](orchestration.md) |
| 2026-11-15 | M1's criterion 25 asks for `git add -A` to be refused, but decision 0002 made the hook remind and the commit refuse. Which one holds? The session had to ask the maintainer to approve a revised criterion. | did not understand | The revised criterion, under "Changes after approval" in the [M1 plan](plans/m1-make-the-core-hold-weight.md); the reasons in [decision 0002](decisions/0002-hooks-remind-the-commit-enforces.md) |
| 2026-11-15 | How does a session commit eval-harness work before the costly runs, when `eval_record` refuses every commit that changes what the eval covers until the runs are on record? The maintainer asked for the work to be committed and pushed first; the workspace did not say how. | not there | [Changing the machinery](changing-the-machinery.md#traps), the trap on eval-harness commits |
| 2026-11-21 | May an amendment to a decision record edit its **In short** line? The layout rule said a record changes only by a dated "Amended" paragraph, yet slices C4 and C5a had edited the line to keep it true. M3's builders queued it for the maintainer as Q15. | did not understand | [Layout](layout.md#the-opening): an amendment may also edit the record's **In short** line |
| 2026-11-22 | When a slice builds what another lane's pages call planned, who updates those pages? Slice C5e built the outward-write guard, and three B2 pages still call it planned in C5e; the plan's rule against changing anything outside a slice's row left it open. M3's builder queued it for the maintainer as Q31. | not there | Not answered yet: Q31 in the workspace queue |

## The kickoff prompt

A newcomer's first real task starts from this prompt, pasted into a new session with the task filled in. The newcomer then logs here every question they still had to ask a person.

```text
I am new to this workspace. My task: <one or two sentences, with the ticket or page it comes from>.

Before you change anything:
1. Read AGENTS.md, then route through INDEX.md to the playbook or how-to that fits the task.
2. Tell me which page you will follow, how big the change is by docs/size-the-work.md, and what you will not touch.
3. Ask me only what the workspace does not answer. For each question you ask, say where you looked first.

When you finish, end as docs/procedure-endings.md says, and add a row to docs/question-log.md for each question I had to answer, with its kind of gap.
```
