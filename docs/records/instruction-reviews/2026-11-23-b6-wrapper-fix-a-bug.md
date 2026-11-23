---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/fix-a-bug/SKILL.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: plugin/skills/fix-a-bug/SKILL.md

This records the review of the fix-a-bug wrapper that slice B6 adds, for its author and its readers.

**In short:** 1 finding: 1 trigger, not blocking. The description takes every small change in one repository, and names neither exception the catalog gives: safe refactor for a small refactor, and extend the workspace for a small change to pages only.

## Scope

In scope: the whole wrapper, its front matter (`name`, `description`) and its body, which the staged change adds (`git diff --cached`). Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/README.md` ("Before you pick one" and the catalog), `docs/how-tos.md`, `docs/playbooks/fix-a-bug.md`, `docs/safe-refactor.md`, `docs/extend-the-workspace.md`, every other wrapper under `plugin/skills/`, the cases `plugin/evals/fix-a-bug-fires` and `plugin/evals/fix-a-bug-quiet`, `parts/wrappers.py`, the `wrappers` and `loaded_size` entries in `workspace.json`, and `evals/arms.json`.

Run, on macOS: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 17 of 17 cases` and `loaded_size: 4 of 4 cases`; `claude plugin validate plugin`, on Claude Code 2.1.330, passes with one warning, for a missing icon (verified). The 28 descriptions come to 6,542 bytes against the 9,000-byte ceiling; this one is 249 (verified). No selection case has run yet, as `evals/README.md` says (verified, reading), so every claim below about what a description fires on is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | Front matter, `description`, "Use for a small change in one repository that is easy to reverse and under a day of work" | Not blocking. The catalog's "Before you pick one" gives two exceptions to that route: "safe refactor for a small refactor, and extend the workspace for a small change to pages only" (verified, reading). The description names neither. A small page fix matches both this description and extend-the-workspace's "making a small change to pages only"; a small rename under `src/` matches both this and safe-refactor's "changing the shape of code" (inferred). Fix a bug's step 1 asks for a failing test, which a page fix cannot give, and its steps keep no characterization test, which safe refactor's do. Add the two exceptions to the "Not" clause, naming `workspace:safe-refactor` and `workspace:extend-the-workspace`. | fixed: the description names workspace:safe-refactor for a refactor and workspace:extend-the-workspace for pages only. |

## Checked with no finding

- contradiction: the description matches the contract's "How work flows" line and the catalog row, including "written for a bug whose cause you can pin in a failing test" (verified, reading). Both neighbors it names exist, and `workspace:debugging` names this wrapper back for a known cause (verified).
- step: the body names one page, `docs/playbooks/fix-a-bug.md`, which exists, is a playbook with no `lane` key and has numbered steps (verified).
- enforcement: the wrapper states no must or never. The rule that a wrapper stays thin is tagged `prose` in the catalog; the name, page, neighbor and case rules are enforced by the `wrappers` check, whose cases pass (verified).
- placement: the description says only when to fire and when not, and restates no step of the page (verified, reading).
- eval-case: the fires case is a CSV export with its date in the wrong column; the quiet case is a flaky nightly failure with no known cause, which `workspace:debugging` owns and the description names (verified, reading). The page is proven, but the wrapper is outside what the eval covers: `evals/arms.json` gives the guided arm the contract, the index, this page and the definition of done, and no plugin (verified, reading). So the wrapper needs no eval run of its own.

## Re-check

A fresh session re-read the wrapper on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6 (`git diff --cached`). It read the wrapper as staged, its canonical page, every other wrapper's description and the selection cases under `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; the 28 descriptions now come to 7,535 bytes against the 9,000-byte ceiling (verified). No selection case has run, so what a description fires on stays inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld: fixed | The description's "Not" clause names `workspace:safe-refactor` for a refactor and `workspace:extend-the-workspace` for pages only, as the catalog's "Before you pick one" does, and both wrappers exist (verified, reading and `python3 ws.py check`). The fires case, a CSV column bug, stays inside it; the quiet case, an unknown cause, stays outside. |

What a fix broke: Nothing.

What the first reading missed: the rows marked missed below.

| # | Kind | Finding | Disposition |
|---|---|---|---|
| R1 | missed | Not blocking. A trigger finding. The feedback walk-through's page takes "The author names one comment and asks only for its fix", and says it wins over fix a bug there because it asks before committing (verified, reading its "When to use it"). Its fixed description now claims that request, but this description still takes "a small change in one repository" with no exception for it, so a request like "fix the comment Dana left on pull request 42" matches both (inferred: no case tests it). Add "or the fix of one named review comment (workspace:feedback-walkthrough)" to the "Not" clause. | open |
