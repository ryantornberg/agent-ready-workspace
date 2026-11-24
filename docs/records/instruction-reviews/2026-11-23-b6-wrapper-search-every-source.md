---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/search-every-source/SKILL.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: plugin/skills/search-every-source/SKILL.md

This records the review of slice B6's new `search-every-source` wrapper, for its author and whoever settles its findings.

**In short:** 2 findings: 2 trigger, none blocking. The description sends an edit to a known page to the research ladder, which owns no such edit. And it fires on a request to act on one work item or pull request, which its page passes to two pages the waiting list says cannot run yet.

## Scope

In scope: the whole wrapper, new in this change: its `name`, its `description` and its body, read against the page its body names. The change was read with `git diff --cached`. Read beside it: `AGENTS.md`, `INDEX.md`, the playbook catalog `docs/playbooks/README.md`, `docs/how-tos.md`, `docs/playbooks/search-every-source.md` in full, `docs/research-ladder.md`, `docs/extend-the-workspace.md` and its change, the `research-ladder` and `extend-the-workspace` wrappers' descriptions, the description of every other wrapper under `plugin/skills/`, its selection cases `plugin/evals/search-every-source-fires-1`, `-fires-2`, `-quiet-1` and `-quiet-2`, `parts/wrappers.py` and `parts/wrappers.cases.json`, and the `wrappers` and `loaded_size` entries in `workspace.json`.

Run, on macOS, in the worktree, before any record was written: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` exits 0 and lists `wrappers: 17 of 17 cases` (verified). With the records written, `check` fails only on `review_index`, for the index rows the author adds at step 5 (verified). The 28 wrappers' descriptions come to 6,542 bytes against the 9,000 the `loaded_size` entry allows (verified, summing each `description` value). The selection cases have not run: `evals/README.md` says the first run waits for the maintainer's yes to its budget. So every claim below about which wrapper a model would load is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | The description, "or an edit to a known page: use workspace:research-ladder" | Not blocking. The description sends "an edit to a known page" to the research ladder. The ladder finds code or pages; the only write it describes is its offer to write a finding down, made on a yes (verified, reading `docs/research-ladder.md`). A small change to pages is `workspace:extend-the-workspace`'s, whose description says "making a small change to pages only", as its how-to index row does. The quiet case `search-every-source-quiet-2`, "Update the glossary's row for 'hold' so it names AccountFreeze", is such an edit. It tests only that this wrapper stays quiet, so it passes whichever wrapper loads. Name `workspace:extend-the-workspace` for the edit, or drop the clause. | fixed: an edit to a page goes to workspace:extend-the-workspace. |
| 2 | trigger | The description, "Use when the answer needs sources outside the workspace, such as a tracker" | Not blocking. A request to read or change one work item, or to read why a pull request's CI failed, names an outside source and fires the description as written. The page passes it on: "A request that names a work item to read or change is on tracker operations", and "A request about a pull request or its CI is on git-host operations" (verified, reading "When to use it"). Both pages are on the `wrappers` entry's waiting list for M8, kept without a wrapper because the providers they need do not exist yet (verified, reading `workspace.json`). So this wrapper is the route by which such a request reaches pages the list keeps from agents. Add "not for acting on one work item or pull request", though no wrapper can be named for it yet. Inferred: no case tests such a request. | fixed: the description leaves out acting on one work item or pull request; it names no wrapper for it, since both pages wait for M8. |

## Checked with no finding

- contradiction: the description agrees with the page's purpose line and its catalog row, outside sources "and the person asks for them". Its first pointer, a question the workspace alone answers, matches the page's rule that the ladder wins unless the person names an outside source, and `research-ladder`'s description names this wrapper back (verified, reading).
- step: the body names one path, `docs/playbooks/search-every-source.md`, which exists and is a playbook with no `lane` key and no place on the waiting list, as the `wrappers` check confirms on this tree (verified). Its one action, to read the page and follow it, needs no input it does not name.
- enforcement: the wrapper states no must or never of its own. The catalog's rules that bind it are tagged to `wrappers` cases that show them: a description that names no wrapper next to it fails `a wrong name or no description fails`, and a page that is missing fails `a wrapper whose page is missing fails` (verified, reading `parts/wrappers.cases.json`; selftest passes them). That a wrapper stays thin is tagged `prose`, and this one is: its body restates no step of the page.
- placement: the description, which loads into every session, holds only when to fire and the wrapper next to it that owns the nearby request; it restates no rule of the page. The body is one pointer. Its clause "it writes nothing" is the page's read-only rule in four words, which also tells a reader the search is safe to start; it is within the ceiling and was not raised.
- eval-case: the one behavior the wrapper asks is loading its page on a matching request, and its selection cases cover it: `search-every-source-fires-1` and `-fires-2` (`min: 1`) and `-quiet-1` and `-quiet-2` (`min: 0`, `max: 0`, `arm: both`), each `input_match` in the one form the check takes (verified, reading). What the page then asks is the page's own; `docs/playbooks/search-every-source.md` is marked unproven with `prove-by: M8` (verified, reading its front matter).

## Re-check

A fresh session re-read the wrapper on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6 (`git diff --cached`). It read the wrapper as staged, its canonical page, every other wrapper's description and the selection cases under `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; the 28 descriptions now come to 7,535 bytes against the 9,000-byte ceiling (verified). No selection case has run, so what a description fires on stays inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld: fixed | The description names `workspace:extend-the-workspace` for an edit to a page, and that wrapper's description takes a small change to pages only (verified, reading both). `search-every-source-quiet-2`, the glossary edit, now sits inside the wrapper this description names. |
| 2 | upheld: fixed | The description leaves out "acting on one work item or pull request" and names no wrapper for it, since tracker operations and git-host operations wait for M8 (verified, reading the `wrappers` entry). "Act on" is the page's own word for the contrast in "When to use it". |

What a fix broke: Nothing.

What the first reading missed: Nothing.
