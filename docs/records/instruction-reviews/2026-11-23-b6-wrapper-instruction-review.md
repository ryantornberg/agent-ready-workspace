---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/instruction-review/SKILL.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: plugin/skills/instruction-review/SKILL.md

This records the review of the instruction-review wrapper that slice B6 adds, for its author and its readers.

**In short:** 1 finding: 1 trigger, not blocking. The description's list of guidance pages leaves out the eval page, the Copilot and opencode pointer files and the kit's seed pages, which the `review_trailer` entry and the playbook's "When it runs" both name.

## Scope

In scope: the whole wrapper, its front matter (`name`, `description`) and its body, which the staged change adds (`git diff --cached`). Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/README.md`, `docs/how-tos.md`, `docs/playbooks/instruction-review.md` and its diff, `docs/playbooks/docs-audit.md`, every other wrapper under `plugin/skills/`, the cases `plugin/evals/instruction-review-fires` and `plugin/evals/instruction-review-quiet`, `parts/wrappers.py`, and the `wrappers`, `loaded_size` and `review_trailer` entries in `workspace.json`.

Run, on macOS: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 17 of 17 cases` and `loaded_size: 4 of 4 cases`; `claude plugin validate plugin`, on Claude Code 2.1.330, passes with one warning, for a missing icon (verified). The 28 descriptions come to 6,542 bytes against the 9,000-byte ceiling; this one is 260 (verified). No selection case has run yet, as `evals/README.md` says (verified, reading), so every claim below about what a description fires on is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | Front matter, `description`, its list "the contract, INDEX.md, the README, a wrapper, or a page under docs/ other than ..." | Not blocking. The `review_trailer` entry's `guidance` list also holds `evals/README.md`, the Copilot and opencode pointer files, `.github/copilot-instructions.md` and `opencode.json`, and the kit's two seed pages, `kit/seed/README.md` and `kit/seed/evals-README.md` (verified, reading `workspace.json`). The playbook's "When it runs" names them all (verified, reading). "The contract" may be read to take in `CLAUDE.md` and the pointer files, but not the eval page or the seed pages. A commit that changes only one of those may not fire this wrapper (inferred); the commit check then refuses it for a missing trailer, so a miss costs a refused commit. Add "the eval page, the pointer files or the kit's seed pages", or say "any path the `review_trailer` entry lists as guidance". The catalog row has the same gap; this record covers the wrapper only. | fixed: the description says any path the `review_trailer` entry lists as guidance, and names the pointer files and the eval page among them. |

## Checked with no finding

- contradiction: the description's exceptions under `docs/`, a plan, a milestone record, a record and the question log, match the entry's `except` list, `docs/plans/`, `docs/milestones/`, `docs/records/` and `docs/question-log.md` (verified, reading). "A wrapper" matches the staged `plugin/skills/` entry, and the selection cases are left out, as the staged "When it runs" says. The neighbor it names, `workspace:docs-audit`, exists and names this wrapper back for the pages one commit changes (verified).
- step: the body names one page, `docs/playbooks/instruction-review.md`, which exists, is a playbook with no `lane` key and has seven numbered steps (verified).
- enforcement: the wrapper states no must or never. The rule that a wrapper stays thin is tagged `prose` in the catalog; the name, page, neighbor and case rules are enforced by the `wrappers` check, whose cases pass (verified). The review itself is enforced at the commit by `review_trailer`, which this wrapper does not restate.
- placement: the description says only when to fire and when not, and restates no step of the page (verified, reading).
- eval-case: the fires case asks for the review of two edited `docs/` pages before the commit; the quiet case asks for a drift reading of the whole tree, which `workspace:docs-audit` owns and the description names (verified, reading). The page is marked unproven with `prove-by: M4`.

## Re-check

A fresh session re-read the wrapper on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6 (`git diff --cached`). It read the wrapper as staged, its canonical page, every other wrapper's description and the selection cases under `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; the 28 descriptions now come to 7,535 bytes against the 9,000-byte ceiling (verified). No selection case has run, so what a description fires on stays inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld: fixed | The description says "any path the review_trailer entry in workspace.json lists as guidance", and names the pointer files and the eval page among them (verified, reading the entry's `guidance` list). |

What a fix broke: the rows marked broke below.

What the first reading missed: Nothing.

| # | Kind | Finding | Disposition |
|---|---|---|---|
| R1 | broke | Not blocking. A trigger finding. Before the fix the description excluded, under `docs/`, a plan, a milestone record, a record and the question log, matching the entry's `except` list; the first reading checked that (verified, its "Checked with no finding"). The fixed list says only "a page under docs/ other than a plan or a record", so the question log, `docs/question-log.md`, and the milestone records under `docs/milestones/` now read as guidance (verified, reading the `except` list). The contract asks any session that had to ask a person something to add to the question log, so such a commit can fire this wrapper and a review no check requires (inferred). Put back "a milestone record" and "the question log", as the catalog's row has them. | fixed (second round): "other than a plan, a milestone record, a record or the question log". |

## Second re-check

A fresh session re-read the wrapper's description on 2026-11-23, after the second fix round, at commit c44cbee, using `git diff ec6562b c44cbee` and, for the pages main also changed, `git diff origin/main c44cbee`. On macOS, `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` exits 0, with `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; `python3 -m unittest tests.test_kit tests.test_instruction_review -b` runs 48 tests, OK; and `python3 ws.py check --commits origin/main..c44cbee` exits 0 (verified).

| # | Verdict | Evidence |
|---|---|---|
| R1 | fixed | The description says "a page under docs/ other than a plan, a milestone record, a record or the question log", the four paths of the `review_trailer` entry's `except` list in `workspace.json` (verified, reading). |

What the first readings missed: nothing.
