---
last-reviewed: 2026-11-14
---

# Fix a bug

The steps for a bug that is small, easy to reverse and in one repository. An agent runs this on a request such as "the Export button does nothing, fix it". If the bug turns out to be bigger than that, stop and say so.

## Steps

1. **Reproduce it before you edit anything.** Write a test that fails for the reason in the report. If you cannot make it fail, you do not understand the bug yet: report that, and do not guess at a fix.
2. **Make the smallest change that passes the test.** If you find a second bug on the way, write it down and leave it alone.
3. **Run the whole suite**, then check the change in the running app.
4. **List what else calls the code you changed.** Say which callers you checked.
5. **Stage the files you changed, by name.** Open a draft pull request with the report from the [definition of done](../definition-of-done.md#the-report).

## Stop and ask when

- The fix needs a change in a second repository.
- The failing test passes on the base branch, so the bug is not where the report says.
- The fix would undo a recorded decision.

## Why it is tested

A small wording change here can change what an agent does. [The eval case](../../evals/README.md) for this playbook checks four things: the agent reproduces before it edits, adds a regression test, marks its claims, and never stages everything at once.
