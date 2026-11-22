---
kind: record
last-reviewed: 2026-11-22
---

# Question log

Every question someone had to ask a person because the workspace did not answer it. Each one marks context the workspace failed to carry. Log it, fix the page where the next person will look, and note the fix.

The measure of a workspace is this list getting shorter per piece of work, not the workspace getting bigger.

**Adding an entry.** Add one dated row before the session finishes. Stage this file by name and commit it, with the session's other work or on its own, with a subject as [commits](commits.md) says. It needs no `Instructions-review:` trailer, since the log is not a guidance page. A procedure that otherwise commits nothing still commits this entry. Push it with the session's other work. With none, an agent may push it in this repository, and in a team's workspace a person does, as [changing the machinery](changing-the-machinery.md#the-path-for-a-machinery-change) says of a branch. If the edit, the commit or the push is refused, leave the entry where it stopped, and give its text and the refusal in your report.

| Date | The question | Where the answer lives now |
|---|---|---|
| 2026-11-14 | Which order service is the live one? (invented example) | [AGENTS.md](../AGENTS.md#facts-a-model-cannot-derive) |
| 2026-11-15 | Which model and effort should each slice of a plan run at? The maintainer had to ask; the workspace had no rule. | [Orchestration](orchestration.md) |
| 2026-11-15 | M1's criterion 25 asks for `git add -A` to be refused, but decision 0002 made the hook remind and the commit refuse. Which one holds? The session had to ask the maintainer to approve a revised criterion. | The revised criterion, under "Changes after approval" in the [M1 plan](plans/m1-make-the-core-hold-weight.md); the reasons in [decision 0002](decisions/0002-hooks-remind-the-commit-enforces.md) |
| 2026-11-15 | How does a session commit eval-harness work before the costly runs, when `eval_record` refuses every commit that changes what the eval covers until the runs are on record? The maintainer asked for the work to be committed and pushed first; the workspace did not say how. | [Changing the machinery](changing-the-machinery.md#traps), the trap on eval-harness commits |
| 2026-11-21 | May an amendment to a decision record edit its **In short** line? The layout rule said a record changes only by a dated "Amended" paragraph, yet slices C4 and C5a had edited the line to keep it true. M3's builders queued it for the maintainer as Q15. | [Layout](layout.md#the-opening): an amendment may also edit the record's **In short** line |
