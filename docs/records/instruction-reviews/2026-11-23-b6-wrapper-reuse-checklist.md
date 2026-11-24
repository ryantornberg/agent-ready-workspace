---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/reuse-checklist/SKILL.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: plugin/skills/reuse-checklist/SKILL.md

This records the review of slice B6's new `reuse-checklist` wrapper, for its author and whoever settles its findings.

**In short:** 1 finding: 1 trigger, none blocking. The description fires before any new logic, while the page and every search it runs cover only code under `src/`.

## Scope

In scope: the whole wrapper, new in this change: its `name`, its `description` and its body, read against the page its body names. The change was read with `git diff --cached`. Read beside it: `AGENTS.md`, `INDEX.md`, the playbook catalog `docs/playbooks/README.md`, `docs/how-tos.md`, `docs/playbooks/reuse-checklist.md` in full, `docs/playbooks/impact-analysis.md` ("When it runs"), `docs/playbooks/test-first.md`, the `impact-analysis` and `test-first` wrappers' descriptions, the description of every other wrapper under `plugin/skills/`, its selection cases `plugin/evals/reuse-checklist-fires` and `-quiet`, `parts/wrappers.py` and `parts/wrappers.cases.json`, and the `wrappers` and `loaded_size` entries in `workspace.json`.

Run, on macOS, in the worktree, before any record was written: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` exits 0 and lists `wrappers: 17 of 17 cases` (verified). With the records written, `check` fails only on `review_index`, for the index rows the author adds at step 5 (verified). The 28 wrappers' descriptions come to 6,542 bytes against the 9,000 the `loaded_size` entry allows (verified, summing each `description` value). The selection cases have not run: `evals/README.md` says the first run waits for the maintainer's yes to its budget. So every claim below about which wrapper a model would load is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | The description, "Use before writing new logic" | Not blocking. The description fires before any new logic. The page scopes the author's half to "new logic in code under `src/`", and every row of "Where to search" looks only there: `python3 tools/symbols.py --contains PART src`, `git grep -n "TEXT" -- src` and `git ls-files src/<repository>/<folder>` (verified, reading). New logic in the machinery, such as a part or a function in `wslib/`, fires the wrapper, and the searches it then runs cannot find a helper there, so "nothing fits" comes back for the wrong reason. Say "new logic in code under src/", as `workspace:safe-refactor`'s description scopes itself. Inferred: no case tests a machinery request. | fixed: "new logic in code under src/". |

## Checked with no finding

- contradiction: the description's two uses, the author's search before new logic and a review of a diff "when the request names reuse alone", match the page's "When it runs" and its catalog row. Its "Not for" matches impact analysis's own description, which names this wrapper back (verified, reading).
- step: the body names one path, `docs/playbooks/reuse-checklist.md`, which exists and is a playbook with no `lane` key and no place on the waiting list, as the `wrappers` check confirms on this tree (verified). Its one action, to read the page and follow it, needs no input it does not name.
- enforcement: the wrapper states no must or never of its own. The catalog's rules that bind it are tagged to `wrappers` cases that show them: a description that names no wrapper next to it fails `a wrong name or no description fails`, and a page that is missing fails `a wrapper whose page is missing fails` (verified, reading `parts/wrappers.cases.json`; selftest passes them). That a wrapper stays thin is tagged `prose`, and this one is: its body restates no step of the page.
- placement: the description, which loads into every session, holds only when to fire and the wrapper next to it that owns the nearby request; it restates no rule of the page. The body is one pointer.
- eval-case: the one behavior the wrapper asks is loading its page on a matching request, and its selection cases cover it: `reuse-checklist-fires` (`min: 1`) and `reuse-checklist-quiet` (`min: 0`, `max: 0`, `arm: both`), each `input_match` in the one form the check takes (verified, reading). What the page then asks is the page's own; `docs/playbooks/reuse-checklist.md` is marked unproven with `prove-by: M6` (verified, reading its front matter).

## Re-check

A fresh session re-read the wrapper on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6 (`git diff --cached`). It read the wrapper as staged, its canonical page, every other wrapper's description and the selection cases under `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; the 28 descriptions now come to 7,535 bytes against the 9,000-byte ceiling (verified). No selection case has run, so what a description fires on stays inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld: fixed | The description says "before writing new logic in code under src/", the page's own scope for the author's half (verified, reading). The fires case, a date-formatting helper for the sales report, stays inside it. |

What a fix broke: Nothing.

What the first reading missed: Nothing.
