---
kind: record
last-reviewed: 2026-11-14
---

# Question log

Every question someone had to ask a person because the workspace did not answer it. Each one marks context the workspace failed to carry. Log it, fix the page where the next person will look, and note the fix.

The measure of a workspace is this list getting shorter per piece of work, not the workspace getting bigger.

| Date | The question | Where the answer lives now |
|---|---|---|
| 2026-11-14 | Which order service is the live one? (invented example) | [AGENTS.md](../AGENTS.md#facts-a-model-cannot-derive) |
| 2026-11-15 | Which model and effort should each slice of a plan run at? The maintainer had to ask; the workspace had no rule. | [Orchestration](orchestration.md) |
| 2026-11-15 | M1's criterion 25 asks for `git add -A` to be refused, but decision 0002 made the hook remind and the commit refuse. Which one holds? The session had to ask the maintainer to approve a revised criterion. | The revised criterion, under "Changes after approval" in the [M1 plan](plans/m1-make-the-core-hold-weight.md); the reasons in [decision 0002](decisions/0002-hooks-remind-the-commit-enforces.md) |
| 2026-11-15 | How does a session commit eval-harness work before the costly runs, when `eval_record` refuses every commit that changes what the eval covers until the runs are on record? The maintainer asked for the work to be committed and pushed first; the workspace did not say how. | [Changing the machinery](changing-the-machinery.md#traps), the trap on eval-harness commits |
