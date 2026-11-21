---
kind: record
last-reviewed: 2026-11-21
covers: docs/playbooks/test-first.md
reviewed-at: 8b33280, with the uncommitted change of the B2 builder
---

# Instruction review: docs/playbooks/test-first.md

This records the instruction review of the new test-first playbook, for its author and for agents who follow it.

**In short:** 2 findings: 1 trigger, 1 placement. The loop and the red-green proof run as written, but nothing routes a behavior change to the page, and its console rule sits where running-app checks never load it.

## Scope

The whole page was in scope, since it is new. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `README.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md`, and the pages it links to: `docs/playbooks/fix-a-bug.md` and `docs/safe-refactor.md`. Also read `docs/browsers.md`, `evals/cases/fix-a-bug.json` and `evals/grade.py`, for the tag `eval:fix-a-bug`. Ran `python3 tools/symbols.py ReconciliationWorker src`, `python3 ws.py rules` and `python3 ws.py check`; the check passed. Searched every Markdown page outside the records for links to the page.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | Purpose line; the Topics table of `INDEX.md` | The page is for any agent changing behavior, but nothing sends one there. `INDEX.md` has no row for it, the contract's How work flows names only fix a bug and the size gate, and fix a bug does not link it. Only `docs/safe-refactor.md` and the throwaway prototype page link it. Verified: searched `INDEX.md`, `AGENTS.md`, `fix-a-bug.md` and every page under `docs/` for the path. | queued for slice Z: a Topics row in INDEX.md, which the eval hashes. Until then the playbook catalog and how-to index, later in this slice, list the page; fix-a-bug's link to it is queued with the row. |
| 2 | placement | Writing a good test, the line after the table | The rule that a running-app check with console errors is not verified is about checking in the running app, not about writing a test. The definition of done owns that check, and fix a bug runs it, but neither mentions the console or links this page, so an agent doing the check never loads the rule. Verified: no "console" in `docs/definition-of-done.md` or `docs/browsers.md`; `fix-a-bug.md` has no link here. | fixed: the console sentence and its rule row are gone; the definition of done owns the running-app check. |

## Checked with no finding

- contradiction: the red-green proof matches fix a bug's first two steps; skipping the tidy-up for a bug fix is labelled with its reason; stopping when no harness exists at any level fits moving down one level when one level has none.
- step: `tools/symbols.py` runs as given, every link resolves, each step names its input and output, and the page states when to stop and when to stop and report.
- enforcement: each must or never has a rules row; `eval:fix-a-bug` holds the red-green rule through the graders `new-test-fails-on-the-original-code` and `suite-passes-after-the-change`.
- eval-case: the page is marked `proof: unproven` with `prove-by: M4`, and the README's proof table lists it.
