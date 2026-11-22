---
kind: record
last-reviewed: 2026-11-21
covers: docs/playbooks/test-first.md
reviewed-at: 9f3de36, with the uncommitted change of the B2 builder
---

# Instruction review: docs/playbooks/test-first.md

This records the instruction review of batch 3's edit to the test-first playbook, for its author and for agents changing code.

**In short:** 0 findings. The new route from step 1 to the reuse checklist names its condition and returns to step 2.

## Scope

In scope: the batch 3 edit to "Steps", step 1, which sends the author to the reuse checklist's author's steps when the behavior needs new logic, and anything on the page it contradicts or leaves stale, including the stop line, "A bug fix: the red-green proof" and "Rules". Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md`, the linked pages reuse checklist, fix a bug and safe refactor, and the other batch 3 pages (review orchestrator, architecture review, the playbook catalog diff). Ran `git diff docs/playbooks/test-first.md`, `python3 tools/symbols.py --help` and `python3 tools/symbols.py --contains Freeze src` (the reuse checklist's first search row works and returns the file and line of `AccountFreeze` in `src/orders-api/AccountFreeze.cs`), and `python3 ws.py check` (no finding on this page).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|

No findings.

## Checked with no finding

- contradiction: step 1's condition, "new logic, not only a call to code that exists", matches the reuse checklist's "When it runs" (new logic under `src/`; a change that adds no logic skips it). The checklist's stop on a reuse needing a second repository agrees with this page's stop line and fix a bug's "Stop and ask when".
- step: the checklist's author's step 5 returns the reader to the procedure that sent it, at its next step, so step 1 ends and step 2 follows; its one failure path (a second repository) ends in a report with nothing committed.
- trigger: the link names its condition in the same sentence; the reuse checklist names this step as its route in, and its catalog row ("Before writing new logic") agrees.
- enforcement: the edit adds no must or never; the checklist's own rules table carries the "never copy and change the copy" rule.
- placement: the edit links to the checklist rather than restating its searches.
- eval-case: the page is `proof: unproven`, `prove-by: M4`, so the new behavior needs no case yet.
