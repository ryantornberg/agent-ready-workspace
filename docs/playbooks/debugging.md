---
kind: playbook
proof: unproven
prove-by: M4
last-reviewed: 2026-11-23
---

# Debugging

How an agent finds the unknown cause of a failure before it changes code. For a bug report, a failing test or CI run, or a flaky test.

**In short:** build a fast repro that shows the failure on demand, before any theory: every run, or at a measured rate for a flaky failure. List several causes that a run could rule out, rank them, and test one change at a time. Keep the repro as the regression test, remove your instrumentation, and halt and report when the loop stalls.

## Steps

1. **Build the repro loop first.** Input: the failure, as a bug report, a failing test, or a failed CI run, whose failing step's log `gh run view RUN --log-failed` prints. RUN is the run's number: the number right after `/runs/` in its link, which `gh run list --limit 5` also lists. A job's link goes on past it, `/runs/<run>/job/<job>`; the job's number is not RUN. Make one command that shows the failure, fails the same way every run, and takes seconds, not minutes. Prefer a test over a session in the running app; prefer a small input over a large one. Run it three times. A flaky failure, one that fails only on some runs, gets a loop instead: run the command 20 times and count the failures. With none, run it 100 times. Output: the command, and the failure it prints every time, or for a flaky failure its count out of the runs. Do not form a theory yet.
2. **List the causes.** Input: the repro and the code it runs, found with `python3 tools/symbols.py NAME src` or [INDEX.md](../../INDEX.md). Write at least three possible causes. For each, write the run that would rule it out and the result that would. Rank them, most likely first. Output: the ranked list.
3. **Test one cause per run.** Input: the top cause still standing. Change one thing only, such as one input, one line or one setting, and run the repro. Write down the change, the result, and which causes the result rules out. Output: an updated list. Repeat this step.
4. **Confirm the cause.** A cause is confirmed when one change makes the repro pass and undoing that change makes it fail again. For a flaky failure, pass means no failure in 100 runs of the loop, and fail means failures return at about step 1's rate. Leave the change undone: it is evidence, not the fix. Output: the cause, and the two runs that show it.
5. **Keep the repro as the regression test.** Turn the repro into a test in the repository's suite, if it is not one already. It must fail on the code before the fix. For a flaky failure, it fails at least once in step 1's loop on the code before the fix. Output: the test.
6. **Remove your instrumentation.** Delete every print, log line, breakpoint, temporary flag and scratch file you added. Check with `git status --short`, which also lists new files, and `git diff`, that none is left. Output: a working copy whose only change is the regression test.
7. **Fix or hand on.** If you were asked only for the cause, go to step 8. If you were asked to fix it, and the fix passes the gate in [size the work](../size-the-work.md#the-gate), continue with [fix a bug](fix-a-bug.md) from its second step; once that fix is committed, run [defect escape analysis](escape-analysis.md), which checks whether a review covered the faulty code and, if one did, why it missed it. Otherwise go to step 8, and let the work be sized.
8. **Report.** Say what the cause is, list the causes you ruled out and the run that ruled out each, and name the regression test. Mark each claim verified or inferred, and log a question you had to ask a person, as [procedure endings](../procedure-endings.md) says. By exception to that page's commit step, a regression test from a run that asked only for the cause stays uncommitted: name it in the report, for whoever fixes the bug. On the fix path, [fix a bug](fix-a-bug.md) commits it with the fix.

## Halt and report

Stop and report, rather than guess, when:

| When | Report |
|---|---|
| You cannot make the failure happen on demand, or a flaky failure does not fail once in 100 runs of the loop. | What you tried, what each attempt showed, and what you would need, such as data, an environment or a log. |
| Every cause on the list is ruled out. | The list, the run that ruled out each, and what the runs suggest to look at next. |
| The cause is in a second repository, or in `src/orders-service-v1`, which is kept read-only. | The cause and the evidence. Do not edit there. |
| The fix would undo a recorded decision. | The cause, the decision, and the conflict. |

Never ship a fix for a cause you have not confirmed, and never change code on a hunch to see if the failure goes away.

## Rules

| Rule | Enforced by |
|---|---|
| Build a repro that shows the failure on demand, every run or at a measured rate, before you form any theory. | `prose` |
| Change one thing per run. | `prose` |
| A cause is confirmed only when a change flips the repro both ways. | `prose` |
| The report and the question-log entry follow [procedure endings](../procedure-endings.md); a regression test from a cause-only run stays uncommitted, named in the report. | `prose` |
| Keep the repro as a regression test that fails on the code before the fix. | `prose` |
| Remove all instrumentation before you finish. | `prose` |
| Mark every claim in the report verified or inferred. | `eval:fix-a-bug` |
| Never edit `src/orders-service-v1` while debugging; report a cause found there. | `shelved#an edit inside the shelved folder` |
| Never edit a second repository while debugging; report a cause found there. | `prose` |
| When the loop stalls, halt and report; never guess at a fix. | `prose` |

## References

- Andreas Zeller, [Introduction to Debugging](https://www.debuggingbook.org/html/Intro_Debugging.html), in *The Debugging Book*. Credited for steps 2 to 4: debugging as the scientific method, which invents a hypothesis, derives a prediction from it, tests the prediction and repeats until one hypothesis stands.
