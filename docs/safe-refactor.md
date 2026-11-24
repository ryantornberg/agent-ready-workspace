---
kind: how-to
proof: unproven
prove-by: M4
last-reviewed: 2026-11-21
---

# Safe refactor

How to change the shape of code without changing what it does. For any agent or person restructuring code under `src/`.

**In short:** first make sure it is a refactor at all. Pin today's behavior in a test whose assertions do not change, map everything the change reaches, add the new shape beside the old, switch callers over, and delete the old only once nothing uses it.

## Steps

1. **Decide whether it is a refactor.** Input: the request. A refactor changes structure and leaves behavior alone: same inputs, same outputs, same side effects. If any behavior is meant to change, it is a fix or a feature: use [fix a bug](playbooks/fix-a-bug.md) or [test first](playbooks/test-first.md). When you cannot tell, treat it as a behavior change. Output: one line saying which it is.
2. **Size it.** Input: the refactor. Run it through the [size gate](size-the-work.md#the-gate). The contract routes a small refactor here, not to fix a bug: that page assumes a defect, so a small refactor passes the same gate and follows these steps instead. A rename across the live service and its front end is two repositories, so it climbs the ladder. Output: straight to the next step, or a plan.
3. **Pin the behavior.** Input: the code you will restructure. Find the repository's test command, and what to do when it has no harness, as step 2 of [test first](playbooks/test-first.md) says. Write a characterization test: it records what the code does now, through its public interface, and passes before you change anything. Run it and keep the output. Output: a passing test. Its assertions must not change while the refactor runs.
4. **Map the blast radius.** Input: every name you will move, rename or delete. Find each definition with `python3 tools/symbols.py NAME src`, then search for its callers with `git grep -n NAME`. Check [INDEX.md](../INDEX.md#cross-cutting-chains) for a chain that names the paths. Look for copies of the same code elsewhere: `src/orders-service-v1` has the same names as `src/orders-api`, and is read-only, so it stays as it is. Look for code that more than one repository uses, such as an interface `src/orders-web` calls. Output: a list of what the change reaches, and what you chose to leave alone.
5. **Add, then switch.** Input: the map. Add the new shape beside the old one. Move callers to it one at a time, and run the characterization test and the suite after each move. Output: every caller on the new shape, every test passing, the old shape still present.
6. **Verify, then delete.** Input: the old shape. Search for it again: no caller may remain. Run the whole suite. Only then delete the old shape, and run the suite once more. Output: the old shape gone, the suite passing.
7. **Finish.** The [definition of done](definition-of-done.md) holds; its first row says what the test that came first is for a refactor. Report as that page says.

Stop when the old shape is gone, the characterization test is unchanged and passing, and the report is written. Stop early and report if the characterization test fails, or one of its assertions would have to change, at any step after step 3: behavior changed.

## The done checklist

| Check | How you know |
|---|---|
| It was a refactor | No behavior was meant to change, and no assertion changed. |
| Behavior was pinned first | The characterization test passed before the first edit. |
| The blast radius was mapped | The report names each caller and copy you checked, and each you did not. |
| The old shape is gone | A search for it finds nothing under `src/`, outside read-only code. |
| The suite passes | You ran it after the delete. |

## A worked pattern: tokenize, then swap

Use this when one value is written out by hand in many places, and you need to change it everywhere. Examples are a color or spacing value repeated across `src/orders-web`, or a status string repeated across `src/orders-api`. It is two refactor passes, then one deliberate change.

1. **Tokenize, with no visible change.** Give the value one named home, such as a token or a constant. Replace each raw literal with that name, keeping the value the same. Compare before and after: nothing may differ.
2. **Gate the raw literals.** Search for the literal outside its home. The count must be zero, and it must stay zero. No check here does this yet, so run the search by hand on every pass. A part that holds it is added as [parts](parts.md) says.
3. **Swap the value.** Change it once, in its home. Compare before and after again: the only differences are the ones you intended.

Compare on every pass, not only at the end. For a screen in `src/orders-web`, compare screenshots of the same pages. For a service, compare the characterization test's output. A pass that shows an unplanned difference stops the work until you know why.

Steps 1 and 2 are a refactor and follow the steps above. Step 3 changes behavior, so it is a change of its own, with its own test and report.

## Rules

| Rule | Enforced by |
|---|---|
| A characterization test pins the behavior before the first edit, and its assertions do not change during the refactor. | `prose` |
| The old shape is deleted only when no caller remains and the suite passes. | `prose` |
| Never edit `src/orders-service-v1` as part of a refactor. | `shelved#an edit inside the shelved folder` |
| In tokenize-then-swap, compare before and after on every pass, and keep the raw-literal count at zero. | `prose` |
