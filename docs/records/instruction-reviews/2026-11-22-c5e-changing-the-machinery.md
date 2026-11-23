---
kind: record
last-reviewed: 2026-11-22
covers: docs/changing-the-machinery.md
reviewed-at: 2b60e09, with the uncommitted change of slice C5e
---

# Instruction review: docs/changing-the-machinery.md

This records the review of C5e's new `outward-repos.json` row in the machinery table, for its author and its readers.

**In short:** 1 finding: 1 step. The page's one path for a machinery change asks for a failing case first and is written for an agent's change, but the new row's file is one only a person edits and holds no code to test, so its path has no default for that step.

## Scope

In scope: the new `outward-repos.json` row in "What counts as machinery". The whole page was read. Read beside it: `AGENTS.md`, `INDEX.md`, `README.md` with its uncommitted change (the `outward_write` row and Limits bullet, and step 6 under "Use it for your own team"), decision 0004 with its uncommitted change ("The outward-write guard"), `docs/parts.md`, `docs/adopt-the-workspace.md`, `workspace.json`, `outward-repos.json`, `parts/outward_write.py`, `parts/outward_list.py` and their cases, and the M3 plan's C5 row, criteria 39, 55 and 65 and the C5e row of the split. `tests.test_core` runs 220 tests OK, among them `test_the_machinery_page_and_the_manifest_hold_one_list`, which compares this table with the `direct_push` entry's `machinery` list; `python3 ws.py check` exits 0; `python3 ws.py selftest` passes `outward_list` 7 of 7 (verified). `outward_list.decide` refuses an edit to `outward-repos.json`, `sub/Outward-Repos.JSON` and a worktree's copy, and passes `outward-repos.json.bak` (verified).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | "What counts as machinery", the `outward-repos.json` row, read with "The path for a machinery change" | The row makes the list machinery and says only a person edits it, so a change to it takes the page's one path. That path's step 2, "Write the failing case first. A part's case, or a test in `tests/`, that fails without the change", has nothing to apply to when a person adds a repository to a data file, and the page gives no default for skipping it. The path is also written for an agent's change: step 5 says "In this repository an agent may push", and the In short line says "Machinery work runs at the driver tier", while an agent's edit of this file is refused (verified, `outward_list.decide`). The README's step 6 sends the person here through "It is machinery, so the change reaches main through a pull request" (verified, reading). That a person stops at step 2, or writes a pointless test, is inferred. | fixed: the row says a person edits the list on a branch and opens the pull request, since the guards refuse an agent's edit, and that step 2's failing case does not apply, since the file holds data, not code. |

## Checked with no finding

- contradiction: the row agrees with the README's `outward_write` row and step 6, with decision 0004's "The list." bullet, and with the `outward_list` and `outward_write` entries in `workspace.json`, which name `outward-repos.json` in `"list"` (verified, reading); the table and the `direct_push` list hold the same paths (verified, the test above).
- trigger: the purpose line and the In short line still fire for the row's file, since it is in the table a change is checked against; the row links decision 0004, where the guard's refusals point (verified, reading `PAGE` in both parts).
- enforcement: "Only a person edits it" is enforced as stated by `outward_list` for an edit tool and by `outward_write` for a shell write the parser reports (verified, `outward_list.decide` and the hook fixture "a redirect onto the list is refused"); the README's Limits bullet names what still gets past, a git command that rewrites the file (verified, reading). A direct push of a change to it to main is refused by `direct_push`, since the file is on its list (verified, reading `workspace.json`).
- placement: a one-line row in the machinery table, with the detail in decision 0004; the page is not in the always-loaded layer, since `CLAUDE.md` imports only `AGENTS.md` (verified, reading).
- eval-case: the page is marked `proof: unproven` with `prove-by: M4`, so no eval case is required (verified, reading its front matter).
