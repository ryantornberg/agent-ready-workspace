---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/research-ladder/SKILL.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: plugin/skills/research-ladder/SKILL.md

This records the review of slice B6's new `research-ladder` wrapper, for its author and whoever settles its findings.

**In short:** 1 finding: 1 trigger, none blocking. The description fires only to find code or a page in the workspace, while the page also answers how a library or tool behaves, from its live documentation, and no wrapper fires on that question.

## Scope

In scope: the whole wrapper, new in this change: its `name`, its `description` and its body, read against the page its body names. The change was read with `git diff --cached`. Read beside it: `AGENTS.md`, `INDEX.md`, the playbook catalog `docs/playbooks/README.md`, `docs/how-tos.md`, `docs/research-ladder.md` in full, `docs/playbooks/search-every-source.md`, the feature ladder in `docs/size-the-work.md`, the `search-every-source` wrapper's description, the description of every other wrapper under `plugin/skills/`, its selection cases `plugin/evals/research-ladder-fires` and `-quiet`, `parts/wrappers.py` and `parts/wrappers.cases.json`, and the `wrappers` and `loaded_size` entries in `workspace.json`.

Run, on macOS, in the worktree, before any record was written: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` exits 0 and lists `wrappers: 17 of 17 cases` (verified). With the records written, `check` fails only on `review_index`, for the index rows the author adds at step 5 (verified). The 28 wrappers' descriptions come to 6,542 bytes against the 9,000 the `loaded_size` entry allows (verified, summing each `description` value). The selection cases have not run: `evals/README.md` says the first run waits for the maintainer's yes to its budget. So every claim below about which wrapper a model would load is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | The description, "find code or a page in this workspace" | Not blocking. The description fires only to find code or a page in this workspace. The page's "Pick one lookup" has two rows that reach past that: "A question about how a library or tool behaves", answered from "its current documentation, read live, not from memory", and "A question that needs many files read", handed to a helper (verified, reading). The feature ladder's step 3 sends UI work to read a library's documentation "as the research ladder says". A question about how a library's API behaves fires neither this wrapper nor `workspace:search-every-source`, whose description is for a tracker, a wiki, mail or chat that the person asks for. Add the library question, such as "or how a library or tool behaves, from its live documentation". Inferred: no case tests it. | fixed: the description adds how a library or tool behaves, from its live documentation. |

## Checked with no finding

- contradiction: the description agrees with the page's purpose line and its how-to index row, "Find code or a page, with a name or a topic in hand". Its "Not for" matches the page's hand-off to federated search when the person asks for outside sources, and `search-every-source`'s description names this wrapper back (verified, reading).
- step: the body names one path, `docs/research-ladder.md`, which exists and is a how-to with no `lane` key and no place on the waiting list, as the `wrappers` check confirms on this tree (verified). Its one action, to read the page and follow it, needs no input it does not name. The page has no numbered steps; "follow its steps" reads as "pick one lookup and follow the page".
- enforcement: the wrapper states no must or never of its own. The catalog's rules that bind it are tagged to `wrappers` cases that show them: a description that names no wrapper next to it fails `a wrong name or no description fails`, and a page that is missing fails `a wrapper whose page is missing fails` (verified, reading `parts/wrappers.cases.json`; selftest passes them). That a wrapper stays thin is tagged `prose`, and this one is: its body restates no step of the page.
- placement: the description, which loads into every session, holds only when to fire and the wrapper next to it that owns the nearby request; it restates no rule of the page. The body is one pointer.
- eval-case: the one behavior the wrapper asks is loading its page on a matching request, and its selection cases cover it: `research-ladder-fires` (`min: 1`) and `research-ladder-quiet` (`min: 0`, `max: 0`, `arm: both`), each `input_match` in the one form the check takes (verified, reading). What the page then asks is the page's own; `docs/research-ladder.md` is marked unproven with `prove-by: M4` (verified, reading its front matter).

## Re-check

A fresh session re-read the wrapper on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6 (`git diff --cached`). It read the wrapper as staged, its canonical page, every other wrapper's description and the selection cases under `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; the 28 descriptions now come to 7,535 bytes against the 9,000-byte ceiling (verified). No selection case has run, so what a description fires on stays inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld: fixed | The description adds "or how a library or tool behaves, from its live documentation", matching the page's "Pick one lookup" row (verified, reading). The quiet case, a tracker and wiki report, stays outside it and inside search every source's. |

What a fix broke: Nothing.

What the first reading missed: Nothing.
