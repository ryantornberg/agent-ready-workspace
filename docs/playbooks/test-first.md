---
kind: playbook
proof: unproven
prove-by: M4
last-reviewed: 2026-11-21
---

# Test first

How an agent adds or changes behavior one failing test at a time, and how it proves a bug fix with a test. For any agent changing code.

**In short:** look for code to reuse, then loop: one failing test through a public interface, the least code that passes it, a tidy-up, repeat. For a bug fix, the test fails on the code before the fix and passes on the fix, and the report records both runs.

## Steps

1. **Look for reuse first.** Input: the behavior you were asked for. Search with `python3 tools/symbols.py NAME src` when you have a name, or [INDEX.md](../../INDEX.md) when you have a topic. Output: the code and the test helpers you will build on, or a note that none fit.
2. **Find the repository's test command.** Input: the repository you are changing. Read its own build and test files; commands differ per repository, so do not carry one over from another. Output: the command that runs one test and the command that runs the whole suite. If it has no test harness at any level, stop and report.
3. **Write one failing test.** Input: the next small piece of behavior. Write a single test that calls the code through its public interface, as a caller would. Run it. Output: a test that fails, and fails for the reason you expect. A test that fails for another reason, such as a typo or a missing import, does not count: fix the test and run it again.
4. **Write the least code that passes it.** Input: the failing test. Change only what that test needs. Run the test. Output: the test passes.
5. **Tidy up.** Input: passing tests. Remove duplication and rename what reads badly, running the tests after each change. Output: cleaner code, every test still passing. A restructuring larger than this loop goes to [safe refactor](../safe-refactor.md).
6. **Repeat from step 3** until the behavior you were asked for is covered. Never write several tests and then the code for all of them; one test at a time.
7. **Run the whole suite.** Output: the suite passes. Then finish as the [definition of done](../definition-of-done.md) says, with the report it gives.

Stop when the requested behavior is covered and the suite passes. If a test shows the request needs a change in a second repository, stop and report, as [fix a bug](fix-a-bug.md#stop-and-ask-when) says.

## A bug fix: the red-green proof

A bug fix follows [fix a bug](fix-a-bug.md). Its test is the regression test, and it carries the proof that the fix works:

1. Write the test before you change the code, as fix-a-bug's first step says.
2. Run it on the code before the fix. It fails, for the reason in the report. That is red.
3. Make the fix. Run the test again. It passes. That is green.
4. Record both runs in the report as verified lines: the command, and what each run showed.

Skip the tidy-up step for a bug fix. Fix-a-bug asks for the smallest change that passes, and a second bug found on the way is written down and left alone.

If you cannot make the test fail on the code before the fix, you do not understand the bug yet. Report that and do not guess at a fix. A test that passes on both versions proves nothing.

## Writing a good test

| Do | Why |
|---|---|
| Put the test at the seam the cause points to: the narrowest layer where the wrong behavior shows. | A test at the right layer fails for the right reason and runs fast. |
| Test the class of input, not the one case in the report. If one empty order broke it, test empty orders. | The report names one instance; the bug is usually a class. |
| Assert the behavior the caller sees, not the shape of the fix. | A test that checks the fix's own lines passes for any code that has those lines, right or wrong. |
| When a test level has no harness, such as no end-to-end runner, move down one level: integration, then unit. | A test that runs beats a better test that cannot. Say in the report which level you used and why. |
| For a UI handler, call the handler directly instead of mounting the whole screen, where the framework allows it. | It is faster, and it fails for the handler's own reason. |
| Never pin a wall-clock time or date in a test. Pass in a clock, or compare against one the test controls. | A pinned time passes today and fails tomorrow. |

## Rules

| Rule | Enforced by |
|---|---|
| A bug fix's test fails on the code before the fix and passes on the fix. | `eval:fix-a-bug` |
| The report records both runs of that test, before and after the fix. | `prose` |
| Write one failing test at a time; never batch tests ahead of the code. | `prose` |
| A test that fails for a reason other than the one expected does not count as red. | `prose` |
| Never pin a wall-clock time or date in a test. | `prose` |
