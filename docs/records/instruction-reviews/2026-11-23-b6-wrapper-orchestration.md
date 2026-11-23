---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/orchestration/SKILL.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: plugin/skills/orchestration/SKILL.md

This records the review of slice B6's new `orchestration` wrapper, for its author and whoever settles its findings.

**In short:** no findings. The description names the page's three uses, a task's model and effort, a slice's tier and delegation, and hands a session that stops mid-task to `workspace:handoff`, as the page itself does.

## Scope

In scope: the whole wrapper, new in this change: its `name`, its `description` and its body, read against the page its body names. The change was read with `git diff --cached`. Read beside it: `AGENTS.md`, `INDEX.md`, the playbook catalog `docs/playbooks/README.md`, `docs/how-tos.md`, `docs/orchestration.md` in full, `docs/playbooks/handoff.md` ("When to use it" and "Writing the note") and the `handoff` wrapper's description, the description of every other wrapper under `plugin/skills/`, its selection cases `plugin/evals/orchestration-fires` and `-quiet`, `parts/wrappers.py` and `parts/wrappers.cases.json`, and the `wrappers` and `loaded_size` entries in `workspace.json`.

Run, on macOS, in the worktree, before any record was written: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` exits 0 and lists `wrappers: 17 of 17 cases` (verified). With the records written, `check` fails only on `review_index`, for the index rows the author adds at step 5 (verified). The 28 wrappers' descriptions come to 6,542 bytes against the 9,000 the `loaded_size` entry allows (verified, summing each `description` value). The selection cases have not run: `evals/README.md` says the first run waits for the maintainer's yes to its budget. So every claim below about which wrapper a model would load is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|

No findings.

## Checked with no finding

- contradiction: the description agrees with the page's purpose line and its two how-to index rows, "Choose the model and effort for a task" and "Hand a piece of work to a helper session" (verified, reading). Its "Not for" matches the page's own line under "Handing work off", that a whole session stopping mid-task is not a handoff to a helper, and `handoff`'s description names this wrapper back.
- step: the body names one path, `docs/orchestration.md`, which exists and is a how-to with no `lane` key and no place on the waiting list, as the `wrappers` check confirms on this tree (verified). Its one action, to read the page and follow it, needs no input it does not name. The page has no numbered steps; "follow its steps" reads as "follow the page", which the body's next sentence says outright.
- trigger: the fires case asks which model and effort a helper gets and how to hand it a sweep, which the page's "The binding" and "Delegating" answer; the quiet case is a session stopping with its context nearly full, which is handoff's (verified, reading). Every delegation fires the description, which fits: the `handoff_tier` hook refuses a delegated task with no tier line.
- enforcement: the wrapper states no must or never of its own. The catalog's rules that bind it are tagged to `wrappers` cases that show them: a description that names no wrapper next to it fails `a wrong name or no description fails`, and a page that is missing fails `a wrapper whose page is missing fails` (verified, reading `parts/wrappers.cases.json`; selftest passes them). That a wrapper stays thin is tagged `prose`, and this one is: its body restates no step of the page.
- placement: the description, which loads into every session, holds only when to fire and the wrapper next to it that owns the nearby request; it restates no rule of the page. The body is one pointer.
- eval-case: the one behavior the wrapper asks is loading its page on a matching request, and its selection cases cover it: `orchestration-fires` (`min: 1`) and `orchestration-quiet` (`min: 0`, `max: 0`, `arm: both`), each `input_match` in the one form the check takes (verified, reading). What the page then asks is the page's own; `docs/orchestration.md` is marked unproven with `prove-by: M4` (verified, reading its front matter).

## Re-check

A fresh session re-read the wrapper on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6 (`git diff --cached`). It read the wrapper as staged, its canonical page, every other wrapper's description and the selection cases under `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; the 28 descriptions now come to 7,535 bytes against the 9,000-byte ceiling (verified). No selection case has run, so what a description fires on stays inferred.

The first reading recorded no findings, so there is no disposition to rule on. Handoff's description still names this wrapper for handing work to a helper, and the quiet case, a session stopping with its context nearly full, stays outside this description (verified, reading).

What a fix broke: Nothing.

What the first reading missed: Nothing.
