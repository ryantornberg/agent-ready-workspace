---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/safe-refactor/SKILL.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: plugin/skills/safe-refactor/SKILL.md

This records the review of slice B6's new `safe-refactor` wrapper, for its author and whoever settles its findings.

**In short:** 1 finding: 1 trigger, none blocking. For a behavior change the description names only `workspace:test-first`, which takes work on a route already chosen, where the page names fix a bug or test first.

## Scope

In scope: the whole wrapper, new in this change: its `name`, its `description` and its body, read against the page its body names. The change was read with `git diff --cached`. Read beside it: `AGENTS.md`, `INDEX.md`, the playbook catalog `docs/playbooks/README.md`, `docs/how-tos.md`, `docs/safe-refactor.md` in full, `docs/playbooks/test-first.md`, `docs/playbooks/fix-a-bug.md`, the `test-first`, `debugging` and `fix-a-bug` wrappers' descriptions, the description of every other wrapper under `plugin/skills/`, its selection cases `plugin/evals/safe-refactor-fires` and `-quiet`, `parts/wrappers.py` and `parts/wrappers.cases.json`, and the `wrappers` and `loaded_size` entries in `workspace.json`.

Run, on macOS, in the worktree, before any record was written: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` exits 0 and lists `wrappers: 17 of 17 cases` (verified). With the records written, `check` fails only on `review_index`, for the index rows the author adds at step 5 (verified). The 28 wrappers' descriptions come to 6,542 bytes against the 9,000 the `loaded_size` entry allows (verified, summing each `description` value). The selection cases have not run: `evals/README.md` says the first run waits for the maintainer's yes to its budget. So every claim below about which wrapper a model would load is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | The description, "Not when behavior should change (workspace:test-first)" | Not blocking. The page's step 1 sends a behavior change to "fix a bug or test first". The description names only test first. `workspace:test-first`'s own description takes behavior changes "on a route already chosen, such as a plan's slice", and the contract's "How work flows" sends a change with no route yet through the size gate: a small one to fix a bug, the rest up the ladder (verified, reading). A request that mixes a reshape with a behavior change, which is when this clause matters, is sent to a wrapper that assumes the gate already ran. Name both, as the page does: "workspace:fix-a-bug, or workspace:test-first on a route already chosen". Not blocking: test-first's description and the contract, which every session loads, both still send an unsized change through the gate. | fixed: "workspace:fix-a-bug, or workspace:test-first on a route already chosen". |

## Checked with no finding

- step: the body names one path, `docs/safe-refactor.md`, which exists and is a how-to with no `lane` key and no place on the waiting list, as the `wrappers` check confirms on this tree (verified). Its one action, to read the page and follow it, needs no input it does not name.
- contradiction: the description agrees with the page's purpose line, "restructuring code under `src/`", and its how-to index row. Its second "Not for", an unknown cause, matches debugging's description. The page's step 2 labels its exception to the contract's routing (verified, reading).
- enforcement: the wrapper states no must or never of its own. The catalog's rules that bind it are tagged to `wrappers` cases that show them: a description that names no wrapper next to it fails `a wrong name or no description fails`, and a page that is missing fails `a wrapper whose page is missing fails` (verified, reading `parts/wrappers.cases.json`; selftest passes them). That a wrapper stays thin is tagged `prose`, and this one is: its body restates no step of the page.
- placement: the description, which loads into every session, holds only when to fire and the wrapper next to it that owns the nearby request; it restates no rule of the page. The body is one pointer.
- eval-case: the one behavior the wrapper asks is loading its page on a matching request, and its selection cases cover it: `safe-refactor-fires` (`min: 1`) and `safe-refactor-quiet` (`min: 0`, `max: 0`, `arm: both`), each `input_match` in the one form the check takes (verified, reading). What the page then asks is the page's own; `docs/safe-refactor.md` is marked unproven with `prove-by: M4` (verified, reading its front matter).

## Re-check

A fresh session re-read the wrapper on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6 (`git diff --cached`). It read the wrapper as staged, its canonical page, every other wrapper's description and the selection cases under `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; the 28 descriptions now come to 7,535 bytes against the 9,000-byte ceiling (verified). No selection case has run, so what a description fires on stays inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld: fixed | The description says "workspace:fix-a-bug, or workspace:test-first on a route already chosen", as the page's step 1 does with "fix a bug or test first" (verified, reading). The quiet case, a plan's slice built test first, stays outside it. |

What a fix broke: Nothing.

What the first reading missed: Nothing.
