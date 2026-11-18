---
kind: reference
last-reviewed: 2026-11-18
---

# Definition of done

What evidence a finished change needs. It is for the agent doing the work and the person reading its report. An agent's "done" is a claim, and this page says what the claim has to show.

**In short:** done means a test failed before the fix, no new build warnings, a check in the running app where there is one, an impact check, and a report that marks each claim verified or inferred.

## The list

A change is done when all of these hold:

| Rule | Enforced by |
|---|---|
| **A test came first, and it failed before the fix.** A test written after the fix proves only that the code does what the code does. | `eval:fix-a-bug` |
| **The build is clean against where it started.** Compare warnings with the base branch and count only new ones, so old warnings cannot hide a new one. | `prose` |
| **The change was checked in the running app**, where there is one, on a local environment that no other session shares. | `prose` |
| **An impact check lists what else the changed paths touch.** Name each caller you looked at and each one you did not. | `prose` |
| **Every claim in the report is marked verified or inferred.** | `eval:fix-a-bug` |

## The report

Use this shape. Keep it short enough to read in a minute.

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
