---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/maintain-the-workspace/SKILL.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: plugin/skills/maintain-the-workspace/SKILL.md

This records the review of slice B6's new `maintain-the-workspace` wrapper, for its author and whoever settles its findings.

**In short:** 1 finding: 1 trigger, none blocking. The description fires only when someone asks which duty falls due, while the page's event duties belong to the session whose own change sets them off, and that session is asked nothing.

## Scope

In scope: the whole wrapper, new in this change: its `name`, its `description` and its body, read against the page its body names. The change was read with `git diff --cached`. Read beside it: `AGENTS.md`, `INDEX.md`, the playbook catalog `docs/playbooks/README.md`, `docs/how-tos.md`, `docs/maintain-the-workspace.md` in full, the `docs-audit`, `extend-the-workspace` and `prompt-retrospective` wrappers' descriptions, the change to the page's "Pruning unused wrappers" row, the description of every other wrapper under `plugin/skills/`, its selection cases `plugin/evals/maintain-the-workspace-fires` and `-quiet`, `parts/wrappers.py` and `parts/wrappers.cases.json`, and the `wrappers` and `loaded_size` entries in `workspace.json`.

Run, on macOS, in the worktree, before any record was written: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` exits 0 and lists `wrappers: 17 of 17 cases` (verified). With the records written, `check` fails only on `review_index`, for the index rows the author adds at step 5 (verified). The 28 wrappers' descriptions come to 6,542 bytes against the 9,000 the `loaded_size` entry allows (verified, summing each `description` value). The selection cases have not run: `evals/README.md` says the first run waits for the maintainer's yes to its budget. So every claim below about which wrapper a model would load is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | The description, "Use when asked which upkeep duty an event or a closing milestone sets off" | Not blocking. The description fires only on a question. The page is also for "any agent whose change sets a duty off", and its "Duties an event sets off" says the session whose change sets off the event does the duty "in the same piece of work": a moved page's catalog and proof rows, a renamed code name's other uses, a glossary word's old meaning (verified, reading). An agent that moves a page or renames a class is asking nothing, so the description gives it no reason to load the page. The checks catch some of these on their own, such as the alias row and a broken link; the catalog row and the sweeps for a renamed word rest on the agent finding this page. The how-to index row is worded the same, so it does not catch this either. Name the events too, such as "or after a change that moves a page, renames a code name or changes what a glossary word means". Inferred: no selection case has run, and none tests an event-led request. | fixed: the description adds the change that moves a page, renames a code name or changes a glossary word's meaning. |

## Checked with no finding

- step: the body names one path, `docs/maintain-the-workspace.md`, which exists and is a how-to with no `lane` key and no place on the waiting list, as the `wrappers` check confirms on this tree (verified). Its one action, to read the page and follow it, needs no input it does not name. The page's "When a duty falls due" steps each name an input, a default and an output, and step 5 stops.
- contradiction: the description agrees with the page's purpose line and its how-to index row, and its two "Not for" pointers match the page: the docs audit is the maintainer's to run, as step 2 says, and adding a page is on extend the workspace, as the first event row says (verified, reading). The changed "Pruning unused wrappers" row holds: `parts/wrappers.py` fails a wrapper whose page does not exist (verified, reading and its case `a wrapper whose page is missing fails`).
- enforcement: the wrapper states no must or never of its own. The catalog's rules that bind it are tagged to `wrappers` cases that show them: a description that names no wrapper next to it fails `a wrong name or no description fails`, and a page that is missing fails `a wrapper whose page is missing fails` (verified, reading `parts/wrappers.cases.json`; selftest passes them). That a wrapper stays thin is tagged `prose`, and this one is: its body restates no step of the page.
- placement: the description, which loads into every session, holds only when to fire and the wrapper next to it that owns the nearby request; it restates no rule of the page. The body is one pointer.
- eval-case: the one behavior the wrapper asks is loading its page on a matching request, and its selection cases cover it: `maintain-the-workspace-fires` (`min: 1`) and `maintain-the-workspace-quiet` (`min: 0`, `max: 0`, `arm: both`), each `input_match` in the one form the check takes (verified, reading). What the page then asks is the page's own; `docs/maintain-the-workspace.md` is marked unproven with `prove-by: M5` (verified, reading its front matter).

## Re-check

A fresh session re-read the wrapper on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6 (`git diff --cached`). It read the wrapper as staged, its canonical page, every other wrapper's description and the selection cases under `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; the 28 descriptions now come to 7,535 bytes against the 9,000-byte ceiling (verified). No selection case has run, so what a description fires on stays inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld: fixed | The description adds "or after a change that moves a page, renames a code name or changes what a glossary word means", which are three rows of the page's "Duties an event sets off" (verified, reading). The quiet case, a drift reading of the whole tree, stays outside it and inside docs audit's. |

What a fix broke: Nothing.

What the first reading missed: Nothing.
