---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/test-first/SKILL.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: plugin/skills/test-first/SKILL.md

This records the review of slice B6's new `test-first` wrapper, for its author and whoever settles its findings.

**In short:** no findings. The description matches the page's catalog row, and its two "Not for" pointers name the wrappers that own a failure with an unknown cause and a change of shape only.

## Scope

In scope: the whole wrapper, new in this change: its `name`, its `description` and its body, read against the page its body names. The change was read with `git diff --cached`. Read beside it: `AGENTS.md`, `INDEX.md`, the playbook catalog `docs/playbooks/README.md`, `docs/how-tos.md`, `docs/playbooks/test-first.md` in full, `docs/playbooks/fix-a-bug.md`, `docs/safe-refactor.md`, `docs/playbooks/reuse-checklist.md`, the `debugging`, `safe-refactor`, `fix-a-bug` and `throwaway-prototype` wrappers' descriptions, the description of every other wrapper under `plugin/skills/`, its selection cases `plugin/evals/test-first-fires` and `-quiet`, `parts/wrappers.py` and `parts/wrappers.cases.json`, and the `wrappers` and `loaded_size` entries in `workspace.json`.

Run, on macOS, in the worktree, before any record was written: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` exits 0 and lists `wrappers: 17 of 17 cases` (verified). With the records written, `check` fails only on `review_index`, for the index rows the author adds at step 5 (verified). The 28 wrappers' descriptions come to 6,542 bytes against the 9,000 the `loaded_size` entry allows (verified, summing each `description` value). The selection cases have not run: `evals/README.md` says the first run waits for the maintainer's yes to its budget. So every claim below about which wrapper a model would load is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|

No findings.

## Checked with no finding

- contradiction: the description agrees with the page's catalog row, "on a route already chosen, such as a slice of a hand-off plan, one failing test at a time". Its pointers match the page: step 5 sends a restructuring larger than the loop to safe refactor, and debugging's description owns an unknown cause (verified, reading).
- step: the body names one path, `docs/playbooks/test-first.md`, which exists and is a playbook with no `lane` key and no place on the waiting list, as the `wrappers` check confirms on this tree (verified). Its one action, to read the page and follow it, needs no input it does not name.
- trigger: the fires case is a slice of an approved plan built one failing test at a time; the quiet case, a rename that changes nothing, is safe refactor's (verified, reading). The page's bug-fix section is reached from fix a bug's route, not through this description, and the page says so: "A bug fix follows fix a bug".
- enforcement: the wrapper states no must or never of its own. The catalog's rules that bind it are tagged to `wrappers` cases that show them: a description that names no wrapper next to it fails `a wrong name or no description fails`, and a page that is missing fails `a wrapper whose page is missing fails` (verified, reading `parts/wrappers.cases.json`; selftest passes them). That a wrapper stays thin is tagged `prose`, and this one is: its body restates no step of the page.
- placement: the description, which loads into every session, holds only when to fire and the wrapper next to it that owns the nearby request; it restates no rule of the page. The body is one pointer.
- eval-case: the one behavior the wrapper asks is loading its page on a matching request, and its selection cases cover it: `test-first-fires` (`min: 1`) and `test-first-quiet` (`min: 0`, `max: 0`, `arm: both`), each `input_match` in the one form the check takes (verified, reading). What the page then asks is the page's own; `docs/playbooks/test-first.md` is marked unproven with `prove-by: M4` (verified, reading its front matter).

## Re-check

A fresh session re-read the wrapper on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6 (`git diff --cached`). It read the wrapper as staged, its canonical page, every other wrapper's description and the selection cases under `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; the 28 descriptions now come to 7,535 bytes against the 9,000-byte ceiling (verified). No selection case has run, so what a description fires on stays inferred.

The first reading recorded no findings, so there is no disposition to rule on. Safe refactor's fixed description now names this wrapper only for a route already chosen, which matches this description. The quiet case, a rename that changes nothing, stays outside it (verified, reading).

What a fix broke: Nothing.

What the first reading missed: Nothing.
