---
kind: record
last-reviewed: 2026-11-22
covers: docs/glossary.md
reviewed-at: b7351ba, with the uncommitted change of the TFIX builder
---

# Instruction review: docs/glossary.md

This records the review of TFIX's edit to the glossary's "Case" row, for its author and its readers.

**In short:** 1 finding: 1 contradiction. The row's exception covers any part loaded in a hook call, but only hooks skip their cases. A check loaded inside a session-start hook call runs its cases every time.

## Scope

In scope: the "Case" row of the glossary table, as `git diff docs/glossary.md` shows it on b7351ba, and its consistency with the rest of the glossary, `AGENTS.md`, `INDEX.md` and `docs/parts.md` (with its uncommitted change). The whole glossary was read. Also read: `load`, `load_all`, `load_hooks`, `_load_hooks` and `CaseMemory` in `wslib/parts.py`; `session_facts`, `command_session` and every call of `load`, `load_all` and `load_hooks` in `wslib/runner.py`; the `.githooks/` scripts; `parts/stale_pages.py`; `workspace.json`; `evals/arms.json`. `python3 -m unittest tests.test_core.CaseMemoryTests` runs 9 tests OK (verified). In a scratch repository made from `git archive HEAD`, three `session-start` hook calls ran through `runner.main` with the Claude Code adapter, counting each part whose cases ran. The first ran the cases of `ci_notice`, `fast_forward`, `handoff_loader`, `page_kinds`, `stale_pages` and `stale_pins`; the second and third ran only `page_kinds` (verified).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | The "Case" row, "Test data a part runs when it loads, except in a hook call when they passed before on the same files", against `docs/parts.md` "Cases" | The row's subject is "a part", so the exception reads as covering every part loaded during a hook call. Only hooks skip their cases: `load` skips them only when given a `CaseMemory`, and only `load_hooks` gives one (verified, reading `wslib/parts.py`). `docs/parts.md` says the same narrower thing: "It skips a hook's cases" (verified, reading). Inside a `session-start` hook call, `session_facts` in `wslib/runner.py` loads the check a hook names in its `part` config with `load` and no record. In the manifest, `stale_pages` names `page_kinds` and needs `findings` (verified, reading). In the scratch run above, the second and third `session-start` calls ran `page_kinds`'s cases although they had passed on the same files, while the hooks' cases were skipped (verified). | fixed: the row now says a hook's cases are skipped in a hook call, so a check that a hook call loads still runs its cases. |

## Checked with no finding

- step: the row asks an agent to run nothing and names no path or command (verified, reading).
- trigger: the glossary's purpose and **In short** lines are unchanged. `INDEX.md` still routes "What a word means here" to the glossary (verified, reading). The row keeps its alphabetical place and its second sense, the eval case, unchanged.
- enforcement: the row states no must or never. The behavior it describes is tested: `CaseMemoryTests` pass, including the second call that runs no case and the check command that runs every case (verified, the run above). The glossary is in `review_index`'s `required` list, so its review record is checked (verified, reading `workspace.json`). A reader taking "hook call" to include a git hook, such as the pre-commit hook, would be wrong: those run `ws.py check`, which loads through `load_all` with no record (verified, reading `.githooks/` and `wslib/runner.py`). The glossary's own "Hook" row separates the two senses, so this is not recorded (inferred).
- placement: the glossary is not in the always-loaded layer: `CLAUDE.md` imports only `AGENTS.md`, and `AGENTS.md` does not link the glossary (verified, reading). The mechanism's detail, the `ws-cases.json` record and what its digest holds, stays in `docs/parts.md` "Cases", and the row carries only the exception.
- eval-case: the glossary is a reference page and asks no new behavior of an agent. It is in no eval arm: `evals/arms.json` gives the guided arm `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `fix-a-bug.md` and the definition of done (verified, reading).
