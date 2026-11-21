---
kind: playbook
proof: unproven
prove-by: M4
last-reviewed: 2026-11-21
---

# Debugging

How an agent finds the cause of a failure before it changes any code. For an agent given a bug whose cause is not yet known.

**In short:** build a fast repro that fails the same way every run, before any theory. List several causes that a run could rule out, rank them, and test one change at a time. Keep the repro as the regression test, remove your instrumentation, and halt and report when the loop stalls.

## Steps

1. **Build the repro loop first.** Input: the bug report. Make one command that shows the failure, fails the same way every run, and takes seconds, not minutes. Prefer a test over a session in the running app; prefer a small input over a large one. Run it three times. Output: the command, and the failure it prints every time. Do not form a theory yet.
2. **List the causes.** Input: the repro and the code it runs, found with `python3 tools/symbols.py NAME src` or [INDEX.md](../../INDEX.md). Write at least three possible causes. For each, write the run that would rule it out and the result that would. Rank them, most likely first. Output: the ranked list.
3. **Test one cause per run.** Input: the top cause still standing. Change one thing only, such as one input, one line or one setting, and run the repro. Write down the change, the result, and which causes the result rules out. Output: an updated list. Repeat this step.
4. **Confirm the cause.** A cause is confirmed when one change makes the repro pass and undoing that change makes it fail again. Leave the change undone: it is evidence, not the fix. Output: the cause, and the two runs that show it.
5. **Keep the repro as the regression test.** Turn the repro into a test in the repository's suite, if it is not one already. It must fail on the code before the fix. Output: the test.
6. **Remove your instrumentation.** Delete every print, log line, breakpoint, temporary flag and scratch file you added. Check with `git status --short`, which also lists new files, and `git diff`, that none is left. Output: a working copy whose only change is the regression test.
7. **Fix or hand on.** If you were asked only for the cause, stop here and report. If you were asked to fix it, and the fix passes the gate in [size the work](../size-the-work.md#the-gate), continue with [fix a bug](fix-a-bug.md) from its second step. Otherwise report, with the cause, and let the work be sized.
8. **Report.** Say what the cause is, mark each claim verified or inferred, list the causes you ruled out and the run that ruled out each, and name the regression test.

## Halt and report

Stop and report, rather than guess, when:

| When | Report |
|---|---|
| You cannot make the failure happen on demand, or it does not happen every run. | What you tried, what each attempt showed, and what you would need, such as data, an environment or a log. |
| Every cause on the list is ruled out. | The list, the run that ruled out each, and what the runs suggest to look at next. |
| The cause is in a second repository, or in `src/orders-service-v1`, which is kept read-only. | The cause and the evidence. Do not edit there. |
| The fix would undo a recorded decision. | The cause, the decision, and the conflict. |

Never ship a fix for a cause you have not confirmed, and never change code on a hunch to see if the failure goes away.

## Rules

| Rule | Enforced by |
|---|---|
| Build a repro that fails every run before you form any theory. | `prose` |
| Change one thing per run. | `prose` |
| A cause is confirmed only when a change flips the repro both ways. | `prose` |
| Keep the repro as a regression test that fails on the code before the fix. | `prose` |
| Remove all instrumentation before you finish. | `prose` |
| Mark every claim in the report verified or inferred. | `eval:fix-a-bug` |
| Never edit `src/orders-service-v1` while debugging; report a cause found there. | `shelved#an edit inside the shelved folder` |
| Never edit a second repository while debugging; report a cause found there. | `prose` |
| When the loop stalls, halt and report; never guess at a fix. | `prose` |
