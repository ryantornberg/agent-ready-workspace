---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/prompt-retrospective/SKILL.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: plugin/skills/prompt-retrospective/SKILL.md

This records the review of slice B6's new `prompt-retrospective` wrapper, for its author and whoever settles its findings.

**In short:** no findings. The description matches the page's first routing row and hands a review's miss to `workspace:escape-analysis`, as the page's second row does.

## Scope

In scope: the whole wrapper, new in this change: its `name`, its `description` and its body, read against the page its body names. The change was read with `git diff --cached`. Read beside it: `AGENTS.md`, `INDEX.md`, the playbook catalog `docs/playbooks/README.md`, `docs/how-tos.md`, `docs/playbooks/prompt-retrospective.md` in full, `docs/playbooks/escape-analysis.md` ("When it runs"), `docs/maintain-the-workspace.md`, the `escape-analysis` and `maintain-the-workspace` wrappers' descriptions, the description of every other wrapper under `plugin/skills/`, its selection cases `plugin/evals/prompt-retrospective-fires` and `-quiet`, `parts/wrappers.py` and `parts/wrappers.cases.json`, and the `wrappers` and `loaded_size` entries in `workspace.json`.

Run, on macOS, in the worktree, before any record was written: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` exits 0 and lists `wrappers: 17 of 17 cases` (verified). With the records written, `check` fails only on `review_index`, for the index rows the author adds at step 5 (verified). The 28 wrappers' descriptions come to 6,542 bytes against the 9,000 the `loaded_size` entry allows (verified, summing each `description` value). The selection cases have not run: `evals/README.md` says the first run waits for the maintainer's yes to its budget. So every claim below about which wrapper a model would load is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|

No findings.

## Checked with no finding

- contradiction: the description agrees with the page's purpose line and its catalog row, and its "Not for" matches the page's routing table, whose second row sends a review's miss to defect escape analysis; `escape-analysis`'s description names this wrapper back (verified, reading).
- step: the body names one path, `docs/playbooks/prompt-retrospective.md`, which exists and is a playbook with no `lane` key and no place on the waiting list, as the `wrappers` check confirms on this tree (verified). Its one action, to read the page and follow it, needs no input it does not name.
- trigger: the page also runs once per milestone and on the maintain page's event. Both are the maintainer's to start: the maintain page's step 2 says a session does not run it unless asked, so "Use when asked" fits (verified, reading). The fires case hands over a transcript and asks for a rewritten prompt; the quiet case asks why a review missed a defect, which is escape analysis's.
- enforcement: the wrapper states no must or never of its own. The catalog's rules that bind it are tagged to `wrappers` cases that show them: a description that names no wrapper next to it fails `a wrong name or no description fails`, and a page that is missing fails `a wrapper whose page is missing fails` (verified, reading `parts/wrappers.cases.json`; selftest passes them). That a wrapper stays thin is tagged `prose`, and this one is: its body restates no step of the page.
- placement: the description, which loads into every session, holds only when to fire and the wrapper next to it that owns the nearby request; it restates no rule of the page. The body is one pointer.
- eval-case: the one behavior the wrapper asks is loading its page on a matching request, and its selection cases cover it: `prompt-retrospective-fires` (`min: 1`) and `prompt-retrospective-quiet` (`min: 0`, `max: 0`, `arm: both`), each `input_match` in the one form the check takes (verified, reading). What the page then asks is the page's own; `docs/playbooks/prompt-retrospective.md` is marked unproven with `prove-by: M10` (verified, reading its front matter).

## Re-check

A fresh session re-read the wrapper on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6 (`git diff --cached`). It read the wrapper as staged, its canonical page, every other wrapper's description and the selection cases under `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; the 28 descriptions now come to 7,535 bytes against the 9,000-byte ceiling (verified). No selection case has run, so what a description fires on stays inferred.

The first reading recorded no findings, so there is no disposition to rule on. Escape analysis's description still names this wrapper for a past session's prompt, and the quiet case, why a review missed a defect, stays outside this description (verified, reading).

What a fix broke: Nothing.

What the first reading missed: Nothing.
