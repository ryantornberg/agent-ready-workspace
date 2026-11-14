---
last-reviewed: 2026-11-14
---

# Fix a bug

The steps for a bug that is small, easy to reverse and in one repository. An agent runs this on a request such as "the Export button does nothing, fix it". If the bug turns out to be bigger than that, stop and say so.

## Steps

1. **Reproduce it before you edit anything.** Write a test that fails for the reason in the report. If you cannot make it fail, you do not understand the bug yet: report that, and do not guess at a fix.
2. **Make the smallest change that passes the test.** If you find a second bug on the way, write it down and leave it alone.
3. **Run the whole suite.** Where there is a running app, check the change in it too.
4. **List what else calls the code you changed.** Say which callers you checked.
5. **Stage the files you changed, by name, and commit.** Never stage everything: someone else's edits may be in the folder. Where the repository has a remote, open a draft pull request.
6. **End with the report** from the [definition of done](../definition-of-done.md#the-report).

## Stop and ask when

- The fix needs a change in a second repository.
- The failing test passes on the base branch, so the bug is not where the report says.
- The fix would undo a recorded decision.

## Why it is tested

A small wording change here can change what an agent does. [The eval case](../../evals/README.md) for this playbook runs a real model on a small broken repository, once with this page and once without it. It checks that the agent saw a test fail before it edited the code, that its new test fails on the original code, that the report marks a claim as verified, and that someone else's uncommitted edits stayed out of the commit. The `eval_record` check fails any commit that changes this page without a new passing run.
