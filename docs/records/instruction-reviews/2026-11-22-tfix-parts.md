---
kind: record
last-reviewed: 2026-11-22
covers: docs/parts.md
reviewed-at: b7351ba, with the uncommitted change of the TFIX builder
---

# Instruction review: docs/parts.md

This records the review of TFIX's edits to the page's **In short** line and to "Cases", for their author and their readers.

**In short:** 3 findings: 3 contradiction. The glossary's "Case" row still says a part runs its cases every time it loads. The **In short** line states the runner runs a part's cases when it loads the part, with no exception. The new paragraph gives "it runs on every tool call" as the reason, but the skip also covers the session and stop events, which are not tool calls.

## Scope

In scope: the **In short** line, and the new paragraph in "Cases" that follows the list of what the runner refuses to load, as `git diff docs/parts.md` shows them on b7351ba. The whole page was read. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/glossary.md`, the Traps section of `docs/changing-the-machinery.md`, decision 0004 ("What a part may read" and "Where the engine does the rest"), `.claude/settings.json`, `git show HEAD -- wslib/parts.py`, the hook-call and session-fact code in `wslib/runner.py`, `wslib/ledger.py` (`git_dir`), `tests/hook_cases.py` and the `CaseMemoryTests` in `tests/test_core.py`. `python3 -m unittest tests.test_core.CaseMemoryTests` runs 9 tests OK (verified). In a scratch repository made from `git archive HEAD`, two `python3 ws.py hook before-shell` calls exited 0, and the second took 0.04 seconds against the first's 0.10. `.git/ws-cases.json` then held the 6 `before-shell` hooks. Each entry listed the part, its cases file, `ws.py` and the `wslib` modules loaded (verified).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | "Cases", the new paragraph, against the glossary's "Case" row | The glossary defines a case as "Test data a part runs every time it loads". The new paragraph says a hook call loads a hook without running its cases when they passed before on the same files. Verified: `load` in `wslib/parts.py` returns the part before `failed_cases` when `memory.passed` holds, and `test_a_second_call_with_nothing_changed_runs_no_case` passes. The glossary row was not changed with the page (verified, `git status`). | fixed: the glossary's Case row now names the hook-call exception; that change has its own record, 2026-11-22-tfix-glossary.md. |
| 2 | contradiction | The **In short** line | "The runner runs a part's cases when it loads the part" states the rule with no exception. The exception in "Cases" covers most loads, since every hook call loads hooks this way. The edit only dropped "every time", so the line still reads as always. Verified, reading the same `load` code and the scratch run above, where a second hook call loaded six hooks and ran none of their cases. | fixed: the In short line now adds that a hook call skips the cases when they passed before on the same files. |
| 3 | contradiction | "Cases", the new paragraph, "because it runs on every tool call and has a time budget" | The skip covers every hook call, not only those on tool calls. Hook calls also run on `session-start`, `session-end` and `stop`, which are not tool calls. And not every tool call starts one: only the shell, edit and hand-off tools do, as the event table and `.claude/settings.json` show (verified, reading). `command_session`, `command_after_edit`, `command_stop` and `_command_hook` in `wslib/runner.py` all load through `load_hooks`, which uses the record (verified, reading). `session-end` has no budget in the page's own budget table under "The hook case runner" (verified, reading). Verified: in the scratch repository, a `python3 ws.py hook session-start` call exited 0 and added entries for `ci_notice`, `fast_forward`, `handoff_loader`, `stale_pages` and `stale_pins` to `ws-cases.json`. A reader may infer that session and stop hooks still run their cases every time (inferred). | fixed: the reason now reads that hooks run around every tool call and session event, and most have a time budget. |

## Checked with no finding

- step: the paragraph asks an agent to run nothing. The file it names, `ws-cases.json`, is written in the git folder that `ledger.git_dir` returns for the working copy, as the scratch run showed (verified).
- trigger: the page's purpose line is unchanged. The **In short** line still names parts, the manifest, the runner and cases. `INDEX.md` sends "Adding a check or a hook" and "Add or change a part" to this page (verified, reading). Finding 2 is about the line's accuracy, not where it routes.
- enforcement: the paragraph's absolute claims have tests. `test_a_failing_part_is_refused_on_every_call` shows a failure is never recorded. `test_a_check_command_runs_the_cases_every_time` shows a load without the record runs the cases. `load_all`, which every other command uses, passes no record, and the record is skipped whenever a snapshot is given (verified, reading `wslib/parts.py` and `wslib/runner.py`). The session-start `findings` fact loads its check with `load` and no record, so even inside a hook call a check's cases run every time (verified, reading). The Traps bullet "A part with a failing case is refused" still holds, since only a pass is recorded (verified, the test above).
- placement: the exception sits in "Cases", right after the rule it excepts, and labels itself as the one exception. The page is not in the always-loaded layer: `CLAUDE.md` imports only `AGENTS.md` (verified, reading).
- eval-case: the page is marked `proof: unproven` with `prove-by: M4` (verified, reading its front matter).
