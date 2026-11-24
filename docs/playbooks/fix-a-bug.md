---
kind: playbook
proof: proven
proven-by: docs/milestones/m1.md, b754e39bc8627f9cf180843b113d264ffb07b079:evals/runs/fix-a-bug/record.json, b754e39bc8627f9cf180843b113d264ffb07b079:evals/runs/nightly-job/record.json, b754e39bc8627f9cf180843b113d264ffb07b079:evals/runs/big-report/record.json
last-reviewed: 2026-11-24
---

# Fix a bug

The steps for a bug that is small, easy to reverse and in one repository. An agent runs this on a request such as "the Export button does nothing, fix it". If the bug turns out to be bigger than that, stop and say so.

## Steps

Before step 1, write the fix brief, as [the fix path's gates](#the-fix-paths-gates) say. A fix that comes from [debugging](debugging.md) with its cause found writes the brief first too, then starts at step 2.

1. **Reproduce it before you edit anything.** Write a test that fails for the reason in the report, as [test first](test-first.md) says for the red-green proof. If you cannot make it fail, you do not understand the bug yet: report that, and do not guess at a fix. When the cause is unknown, find it with [debugging](debugging.md) first.
2. **Make the smallest change that passes the test.** Before you write new logic, run [the reuse checklist](reuse-checklist.md). If you find a second bug on the way, write it down as a row of the [defect register](../records/defects.md) and leave it alone.
3. **Run the whole suite.** Where there is a running app, check the change in it too. Cover each axis of [the test matrix](#the-test-matrix) that the brief's test plan names.
4. **List what else calls the code you changed.** Say which callers you checked.
5. **Stage the files you changed, by name, and commit,** as [procedure endings](../procedure-endings.md#the-commit) says. Never stage everything: someone else's edits may be in the folder. Where the repository has a remote, open a draft pull request.
6. **End with the report** from the [definition of done](../definition-of-done.md#the-report). Keep it in the fix's record too, as [the fix record template](../templates/fix-record.md) says. When the fix is to code a review covered, run [defect escape analysis](escape-analysis.md) after the commit and before the report, as its page says.

## Stop and ask when

- The fix needs a change in a second repository.
- The failing test passes on the base branch, so the bug is not where the report says.
- The fix would undo a recorded decision.

## The fix path's gates

Proof: unproven, prove-by M6.

These gates run on every fix this page takes: the brief, the stop before a risky change and the test matrix. Gates that need the review machinery wait for M4, and gates on a tracker wait for M8; this page adds them then.

### The fix brief

Before step 1, open the fix's record in `docs/records/fixes/`, as [the fix record template](../templates/fix-record.md) says, and write a brief of one screen in its `## Brief` section, in ten parts, in this order:

1. The target, and the commit you measured at.
2. Each claim of the report, marked verified, corrected or could not verify.
3. The mechanism, and whether the report names the defect or one symptom of it.
4. The fix seam, and the seams you rejected. Always weigh the boundary that admits untrusted input. A fix was once placed at the visible layer again and again while the cause stayed reachable.
5. Reuse, in one line.
6. What else the change reaches: the callers step 4 will list, and each chain [the index](../../INDEX.md#cross-cutting-chains) names for the changed paths.
7. The test plan, naming the axes of [the test matrix](#the-test-matrix) in play.
8. What is blocked on the person. Keep a decision apart from a missing input. Each says what it blocks and gives a recommended answer.
9. What the report should have carried.
10. What is left out on purpose.

An empty part is one line saying so. Every fix this page takes is small, and each still gets a brief; for a plain fix most parts are one line. A brief that does not fit one screen is itself the finding: the work is not small, so stop and climb [the ladder](../size-the-work.md#the-ladder). A fix that is a slice of a hand-off plan writes its brief under the plan's "Results" instead, since it opens no fix record. With nothing blocked on the person, carry on with step 1. With something blocked, commit the record as [procedure endings](../procedure-endings.md#the-commit) says, stop and report as [the definition of done](../definition-of-done.md#the-report) says: each blocked item goes on the `Not done:` line, and the brief stays in its own section of the record.

### Before a risky change

Stop and ask before a migration, a data repair, a configuration change or a change to a shared environment, even when the brief has nothing blocked.

### The test matrix

The test plan covers each axis in play, and leaves out an axis that is not:

- every caller of the changed code;
- each kind of signed-in identity;
- each client platform;
- empty data and populated data, and a demonstration user against a real one;
- the routes a smoke suite covers;
- at least one error path.

A browser path with console errors is not verified.

| Rule | Enforced by |
|---|---|
| A browser path with console errors is not verified. | `prose` |
| Write the fix brief before step 1, and stop when something in it is blocked on the person. | `prose` |
| Stop and ask before a migration, a data repair, a configuration change or a change to a shared environment. | `prose` |
| The test plan covers each axis of the test matrix in play. | `prose` |

## Changing this page

A small wording change here can change what an agent does. This page has an eval case, and a check fails any commit that changes the page without a new passing run. This page does not say what the case looks for, because an agent reads this page.
