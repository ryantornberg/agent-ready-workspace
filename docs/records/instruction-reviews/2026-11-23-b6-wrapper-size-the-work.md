---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/size-the-work/SKILL.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: plugin/skills/size-the-work/SKILL.md

This records the review of slice B6's new `size-the-work` wrapper, for its author and whoever settles its findings.

**In short:** 2 findings: 1 contradiction, 1 trigger, none blocking. The description sends every change that passes the gate to fix a bug, with neither labelled exception. And "before starting a change" fires on the bug-fix request its quiet case expects it to leave alone.

## Scope

In scope: the whole wrapper, new in this change: its `name`, its `description` and its body, read against the page its body names. The change was read with `git diff --cached`. Read beside it: `AGENTS.md`, `INDEX.md`, the playbook catalog `docs/playbooks/README.md`, `docs/how-tos.md`, `docs/size-the-work.md` in full, `docs/playbooks/fix-a-bug.md`, `docs/safe-refactor.md` (step 2), `docs/extend-the-workspace.md`, the `fix-a-bug`, `safe-refactor` and `extend-the-workspace` wrappers' descriptions, the description of every other wrapper under `plugin/skills/`, its selection cases `plugin/evals/size-the-work-fires` and `-quiet`, `parts/wrappers.py` and `parts/wrappers.cases.json`, and the `wrappers` and `loaded_size` entries in `workspace.json`.

Run, on macOS, in the worktree, before any record was written: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` exits 0 and lists `wrappers: 17 of 17 cases` (verified). With the records written, `check` fails only on `review_index`, for the index rows the author adds at step 5 (verified). The 28 wrappers' descriptions come to 6,542 bytes against the 9,000 the `loaded_size` entry allows (verified, summing each `description` value). The selection cases have not run: `evals/README.md` says the first run waits for the maintainer's yes to its budget. So every claim below about which wrapper a model would load is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | The description, "A change that passes the gate goes to workspace:fix-a-bug" | Not blocking. Two pages state an exception to that, and the catalog's "Before you pick one" labels both: a small refactor follows safe refactor, and a small change to pages only follows extend the workspace (verified, reading the catalog and safe refactor's step 2). The description gives the rule with no exception, in the layer every session loads. It copies the page's own **In short** line and the contract, which say the same; only the catalog and the two pages label the exception. Say "goes to workspace:fix-a-bug, or workspace:safe-refactor for a refactor, or workspace:extend-the-workspace for pages only". Not blocking: both exception wrappers fire on their own requests. | fixed: the description names workspace:safe-refactor and workspace:extend-the-workspace for a refactor or pages only. |
| 2 | trigger | The description, "Use before starting a change" | Not blocking. Every change starts, so the clause fires on every change request, including the quiet case's: "The CSV export on the orders page puts each order's date in the wrong column. Please fix it." (verified, reading the case). The contract and the page do ask that a change pass the gate first, so loading this wrapper there could be right, and then the quiet case fails. Or the case is right, and the description is too broad. The two disagree. Decide which: narrow the description to work that may not pass the gate, such as a feature or a change whose size is unclear, or make the quiet case a request with no change in it. Inferred: the case has not run. | fixed: the description fires on a change that may not pass the gate, or whose size is unclear; the quiet case, a small bug, stays. |

## Checked with no finding

- step: the body names one path, `docs/size-the-work.md`, which exists and is a how-to with no `lane` key and no place on the waiting list, as the `wrappers` check confirms on this tree (verified). Its one action, to read the page and follow it, needs no input it does not name.
- enforcement: the wrapper states no must or never of its own. The catalog's rules that bind it are tagged to `wrappers` cases that show them: a description that names no wrapper next to it fails `a wrong name or no description fails`, and a page that is missing fails `a wrapper whose page is missing fails` (verified, reading `parts/wrappers.cases.json`; selftest passes them). That a wrapper stays thin is tagged `prose`, and this one is: its body restates no step of the page.
- placement: the description, which loads into every session, holds only when to fire and the wrapper next to it that owns the nearby request; it restates no rule of the page. The body is one pointer.
- eval-case: the one behavior the wrapper asks is loading its page on a matching request, and its selection cases cover it: `size-the-work-fires` (`min: 1`) and `size-the-work-quiet` (`min: 0`, `max: 0`, `arm: both`), each `input_match` in the one form the check takes (verified, reading). What the page then asks is the page's own; `docs/size-the-work.md` is marked unproven with `prove-by: M9` (verified, reading its front matter).

## Re-check

A fresh session re-read the wrapper on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6 (`git diff --cached`). It read the wrapper as staged, its canonical page, every other wrapper's description and the selection cases under `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; the 28 descriptions now come to 7,535 bytes against the 9,000-byte ceiling (verified). No selection case has run, so what a description fires on stays inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld: fixed | The description says a change that passes the gate goes to `workspace:fix-a-bug`, or to `workspace:safe-refactor` or `workspace:extend-the-workspace` for a refactor or pages only, the two exceptions the catalog labels (verified, reading). |
| 2 | upheld: fixed | The description now fires on a change that may not pass the gate, such as a feature, or whose size is unclear. The quiet case, a wrong CSV column with "Please fix it", reads as a small bug and stays outside it, and the fires case, a new refunds feature, stays inside (verified, reading; inferred: no case has run). |

What a fix broke: Nothing.

What the first reading missed: Nothing.
