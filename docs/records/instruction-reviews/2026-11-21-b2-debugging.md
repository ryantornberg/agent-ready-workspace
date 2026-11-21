---
kind: record
last-reviewed: 2026-11-21
covers: docs/playbooks/debugging.md
reviewed-at: 8b33280, with the uncommitted change of the B2 builder
---

# Instruction review: docs/playbooks/debugging.md

This records the instruction review of the new debugging playbook, for its author and for agents who follow it.

**In short:** 4 findings: 2 step, 1 trigger, 1 enforcement. The repro-first loop is sound, but the cleanup check misses new files, the fix's place in the steps is unclear, and nothing routes a bug here.

## Scope

The whole page was in scope, since it is new. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `README.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md`, and the pages it links to: `docs/playbooks/fix-a-bug.md` and `docs/size-the-work.md`. Also read `src/README.md`, decision 0005 and `evals/cases/fix-a-bug.json`. Ran `python3 tools/symbols.py ReconciliationWorker src`, `python3 ws.py rules` and `python3 ws.py check`; the check passed. Ran `git diff` in a scratch repository holding a new untracked file. Searched every Markdown page outside the records for links to the page.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | Steps, step 6 | Step 6 checks with `git diff` that no instrumentation is left, and expects a diff holding the test. `git diff` does not show untracked files, so a new test file or a new debug script never appears, and leftover instrumentation in a new file passes the check. Verified: in a scratch repository, `git diff --stat` printed nothing with a new untracked file present. | fixed: step 6 checks with `git status --short` as well as `git diff`, and names scratch files. |
| 2 | step | Steps, steps 4, 6 and 7 | Step 4 confirms the cause by making a change and undoing it, but does not say whether the change stays. Step 6's output is a diff with the fix in it, yet step 7 makes the fix later, through fix a bug's second step. An agent cannot tell when the fix goes in. Verified: read the three steps and fix a bug's Steps. | fixed: step 4 leaves the confirming change undone, as evidence, and step 6's output is the regression test alone; the fix comes in step 7. |
| 3 | trigger | Purpose line; the Topics table of `INDEX.md` | The page is for a bug whose cause is not known, but nothing sends a bug there. The contract sends a small bug straight to fix a bug, whose first step says to report and stop when the bug will not reproduce; it does not link this page. `INDEX.md` has no row. Verified: searched `AGENTS.md`, `INDEX.md`, `fix-a-bug.md` and every page under `docs/`; only the README's proof table names the page. | queued for slice Z: a Topics row in INDEX.md, which the eval hashes. Until then the playbook catalog and how-to index, later in this slice, list the page. |
| 4 | enforcement | Halt and report, the row for a second repository | The row says not to edit a second repository or `src/orders-service-v1`. No rules row states this, and nothing enforces it for a second repository; the `shelved` hook covers only the read-only folder. Verified: the page's rules table and `python3 ws.py rules` list no such row. | fixed: two rows, one tagged with the `shelved` case for the read-only folder, one `prose` for a second repository. |

## Checked with no finding

- contradiction: the halt cases match fix a bug's Stop and ask when; step 7's hand-on to fix a bug's second step fits step 5 having written the test; changing one thing per listed cause is not the hunch the page forbids.
- placement: the page loads only when needed and adds nothing to the always-loaded layer; the report shape defers to the definition of done.
- eval-case: the page is marked `proof: unproven` with `prove-by: M4`, and the README's proof table lists it.
