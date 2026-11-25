---
kind: reference
last-reviewed: 2026-11-24
---

# Definition of done

What evidence a finished change needs. It is for the agent doing the work and the person reading its report. An agent's "done" is a claim, and this page says what the claim has to show.

**In short:** done means a test failed before the fix, no new build warnings, a check in the running app where there is one, an impact check, and a report that marks each claim verified or inferred, kept where its record type says.

## The list

A change is done when all of these hold:

| Rule | Enforced by |
|---|---|
| **A test came first, and it failed before the fix**, where the change has behavior a test can show. A test written after the fix proves only that the code does what the code does. For a change that fixes nothing, such as a refactor, the test that came first is a characterization test: it passed before the change and still passes after it. | `eval:fix-a-bug` |
| **The build is clean against where it started**, where the work has a build. Compare warnings with the base branch and count only new ones, so old warnings cannot hide a new one. | `prose` |
| **The change was checked in the running app**, where there is one, on a local environment that no other session shares. | `prose` |
| **An impact check lists what else the changed paths touch.** Name each caller you looked at and each one you did not. | `prose` |
| **Every claim in the report is marked verified or inferred.** The eval grades one marked claim; in a fix record, the check reads every claim line. | `eval:fix-a-bug`, `claim_marks#a claim line not marked verified or inferred fails` |
| **The report is kept with the work's record.** A fix keeps it in the `## Report` of its [fix record](templates/fix-record.md); a slice of a plan, under the plan's "Results"; other work, such as a refactor or a page change, in the final reply alone. The check reads only fix records. | `claim_marks#a fix record with no report section fails`, `prose` |
| **A finding outside the change is written down, not fixed in it**, as a row of the [defect register](records/defects.md). | `prose` |
| **A changed guidance page names its review record** in the commit, as [procedure endings](procedure-endings.md#the-commit) says. | `review_trailer#a guidance page changed with no trailer fails` |

A row that says "where" applies only when the work has that thing: a test, a build, a running app. A done list once demanded checks a repository could not run, and a list that cannot be met teaches that it is optional.

## The report

Use this shape. Keep it short enough to read in a minute. End your reply with it, and keep the same text where the row above says.

```
Fixed: <what was wrong, in one sentence>

verified  <something you ran, and what you saw>
verified  <something you ran, and what you saw>
inferred  <something you reasoned out and did not check>

Not done: <anything you left, and why>
```

**Verified** means you ran something and saw the result. **Inferred** means you reasoned your way there. Both are useful. A report that mixes them up is how a confident wrong answer gets merged.

## What does not count

- "The tests pass" with no test that covers the change.
- A screenshot from before the fix.
- "Should work" about anything a command could have checked.
- A green run of `python3 ws.py check` taken as proof of what was committed. That command reads the working folder; the commit check reads the staged files, as `python3 ws.py check --staged` does. A green run on unstaged files once proved nothing.
- A passing check taken as proof of more than it checks. Green gates were once read as truth.
- A required check, one the commit, CI or the repository's suite runs, that errored or ran zero tests, read as a pass. It is a finding: write it in the defect register, even when the change did not cause it.
