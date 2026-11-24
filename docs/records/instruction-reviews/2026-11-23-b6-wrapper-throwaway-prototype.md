---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/throwaway-prototype/SKILL.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: plugin/skills/throwaway-prototype/SKILL.md

This records the review of slice B6's new `throwaway-prototype` wrapper, for its author and whoever settles its findings.

**In short:** no findings. The description matches the page's two kinds of question and its deletion, and hands the real change to `workspace:test-first`, as the page does.

## Scope

In scope: the whole wrapper, new in this change: its `name`, its `description` and its body, read against the page its body names. The change was read with `git diff --cached`. Read beside it: `AGENTS.md`, `INDEX.md`, the playbook catalog `docs/playbooks/README.md`, `docs/how-tos.md`, `docs/playbooks/throwaway-prototype.md` in full, `docs/playbooks/test-first.md`, the feature ladder and the spec process in `docs/size-the-work.md`, `docs/playbooks/decision-interview.md` (its opening), the `test-first` and `decision-interview` wrappers' descriptions, the description of every other wrapper under `plugin/skills/`, its selection cases `plugin/evals/throwaway-prototype-fires` and `-quiet`, `parts/wrappers.py` and `parts/wrappers.cases.json`, and the `wrappers` and `loaded_size` entries in `workspace.json`.

Run, on macOS, in the worktree, before any record was written: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` exits 0 and lists `wrappers: 17 of 17 cases` (verified). With the records written, `check` fails only on `review_index`, for the index rows the author adds at step 5 (verified). The 28 wrappers' descriptions come to 6,542 bytes against the 9,000 the `loaded_size` entry allows (verified, summing each `description` value). The selection cases have not run: `evals/README.md` says the first run waits for the maintainer's yes to its budget. So every claim below about which wrapper a model would load is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|

No findings.

## Checked with no finding

- contradiction: the description matches the page's "When to use it", a question about state step by step or about how a screen should look, and its catalog row. "Not for building the real change" matches the page's "If you are building code to keep, this is not the page: see test first". A prototype runs at the feature ladder's step 1, before the plan, so the real change is built at step 4, test first, and the pointer names the right wrapper (verified, reading).
- step: the body names one path, `docs/playbooks/throwaway-prototype.md`, which exists and is a playbook with no `lane` key and no place on the waiting list, as the `wrappers` check confirms on this tree (verified). Its one action, to read the page and follow it, needs no input it does not name.
- trigger: the fires case asks for three rough screens side by side, with nothing kept; the quiet case is a plan slice built test first, which is test first's (verified, reading).
- enforcement: the wrapper states no must or never of its own. The catalog's rules that bind it are tagged to `wrappers` cases that show them: a description that names no wrapper next to it fails `a wrong name or no description fails`, and a page that is missing fails `a wrapper whose page is missing fails` (verified, reading `parts/wrappers.cases.json`; selftest passes them). That a wrapper stays thin is tagged `prose`, and this one is: its body restates no step of the page.
- placement: the description, which loads into every session, holds only when to fire and the wrapper next to it that owns the nearby request; it restates no rule of the page. The body is one pointer.
- eval-case: the one behavior the wrapper asks is loading its page on a matching request, and its selection cases cover it: `throwaway-prototype-fires` (`min: 1`) and `throwaway-prototype-quiet` (`min: 0`, `max: 0`, `arm: both`), each `input_match` in the one form the check takes (verified, reading). What the page then asks is the page's own; `docs/playbooks/throwaway-prototype.md` is marked unproven with `prove-by: M4` (verified, reading its front matter).

## Re-check

A fresh session re-read the wrapper on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6 (`git diff --cached`). It read the wrapper as staged, its canonical page, every other wrapper's description and the selection cases under `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; the 28 descriptions now come to 7,535 bytes against the 9,000-byte ceiling (verified). No selection case has run, so what a description fires on stays inferred.

The first reading recorded no findings, so there is no disposition to rule on. No neighbor's fix changed the boundary with test first, and the quiet case, a plan's slice built test first, stays outside this description (verified, reading).

What a fix broke: Nothing.

What the first reading missed: Nothing.
