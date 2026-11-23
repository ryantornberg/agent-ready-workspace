---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/review-in-a-worktree/SKILL.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: plugin/skills/review-in-a-worktree/SKILL.md

This records the review of slice B6's new `review-in-a-worktree` wrapper, for its author and whoever settles its findings.

**In short:** 1 finding: 1 contradiction, none blocking. The wrapper fires on a plain pull-request review and sends it, at the page's step 5, to the review orchestrator, which the `wrappers` entry says cannot run before M4, with no default between that and reading the code yourself.

## Scope

In scope: the whole wrapper, new in this change: its `name`, its `description` and its body, read against the page its body names. The change was read with `git diff --cached`. Read beside it: `AGENTS.md`, `INDEX.md`, the playbook catalog `docs/playbooks/README.md`, `docs/how-tos.md`, `docs/review-in-a-worktree.md` in full, `docs/playbooks/feedback-walkthrough.md` ("When to use it"), `docs/playbooks/review-orchestrator.md` (its opening and "What exists today and what is planned"), the `feedback-walkthrough` and `architecture-review` wrappers' descriptions, the description of every other wrapper under `plugin/skills/`, its selection cases `plugin/evals/review-in-a-worktree-fires` and `-quiet`, `parts/wrappers.py` and `parts/wrappers.cases.json`, and the `wrappers` and `loaded_size` entries in `workspace.json`.

Run, on macOS, in the worktree, before any record was written: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` exits 0 and lists `wrappers: 17 of 17 cases` (verified). With the records written, `check` fails only on `review_index`, for the index rows the author adds at step 5 (verified). The 28 wrappers' descriptions come to 6,542 bytes against the 9,000 the `loaded_size` entry allows (verified, summing each `description` value). The selection cases have not run: `evals/README.md` says the first run waits for the maintainer's yes to its budget. So every claim below about which wrapper a model would load is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | The description and its fires case, against step 5 of `docs/review-in-a-worktree.md` and the waiting list in the `wrappers` entry | Not blocking. The fires case is a plain review request: "Review pull request #42 for me, without touching my main working copy". The page's step 5 then says "Follow the review orchestrator with that path as the folder at the tip, or read the code yourself", with no default between the two (verified, reading). The `wrappers` entry keeps the review orchestrator without a wrapper, as waiting for M4, because "its dispatch, its completion reading, its findings manifest and its review mark are M4's review machinery". The orchestrator's own page says "today every step is done by hand" (verified, reading both). So two loaded files disagree on whether the orchestrator runs today, and this wrapper is where a plain pull-request review meets that disagreement. Give step 5 a default, such as the orchestrator by hand or reading the code yourself until M4, and make the waiting entry's reason agree with the orchestrator page. Not blocking: either branch runs, and neither writes. | deferred to M6: step 5's missing default is the page's own, from B2, and M6 proves the page. The other half is fixed: the waiting entry's reason now agrees with the orchestrator page, which runs by hand today. |

## Checked with no finding

- step: the body names one path, `docs/review-in-a-worktree.md`, which exists and is a how-to with no `lane` key and no place on the waiting list, as the `wrappers` check confirms on this tree (verified). Its one action, to read the page and follow it, needs no input it does not name. Steps 1 to 4 and 6 each name their command, and each stop ends in the step 7 report.
- trigger: the description says when to fire, a pull request's files reviewed apart from the main working copy, and its "Not for" matches feedback walk-through's own table, which sends reviewing someone else's pull request to the review orchestrator or here; `feedback-walkthrough`'s description names this wrapper back. The quiet case, an author walking through comments, is that request (verified, reading).
- enforcement: the wrapper states no must or never of its own. The catalog's rules that bind it are tagged to `wrappers` cases that show them: a description that names no wrapper next to it fails `a wrong name or no description fails`, and a page that is missing fails `a wrapper whose page is missing fails` (verified, reading `parts/wrappers.cases.json`; selftest passes them). That a wrapper stays thin is tagged `prose`, and this one is: its body restates no step of the page.
- placement: the description, which loads into every session, holds only when to fire and the wrapper next to it that owns the nearby request; it restates no rule of the page. The body is one pointer.
- eval-case: the one behavior the wrapper asks is loading its page on a matching request, and its selection cases cover it: `review-in-a-worktree-fires` (`min: 1`) and `review-in-a-worktree-quiet` (`min: 0`, `max: 0`, `arm: both`), each `input_match` in the one form the check takes (verified, reading). What the page then asks is the page's own; `docs/review-in-a-worktree.md` is marked unproven with `prove-by: M6` (verified, reading its front matter).

## Re-check

A fresh session re-read the wrapper on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6 (`git diff --cached`). It read the wrapper as staged, its canonical page, every other wrapper's description and the selection cases under `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; the 28 descriptions now come to 7,535 bytes against the 9,000-byte ceiling (verified). No selection case has run, so what a description fires on stays inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld: the waiting half fixed, step 5's default deferred to M6 | The `wrappers` entry's `why` for the orchestrator now says it runs by hand today, as its page does (verified, reading). Step 5 still reads "Follow the review orchestrator ... or read the code yourself" with no default (verified, reading). M6 is the page's `prove-by` (verified), and the finding is not blocking, so the deferral stands. |

What a fix broke: Nothing.

What the first reading missed: Nothing.
