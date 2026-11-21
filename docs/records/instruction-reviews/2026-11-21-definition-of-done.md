---
kind: record
last-reviewed: 2026-11-21
covers: docs/definition-of-done.md
reviewed-at: 166bbc7
---

# Instruction review: docs/definition-of-done.md

Review of the rules table that M3 sub-batch A made of the definition of done, for its author and the agents who report against it.

**In short:** 3 findings: 1 enforcement, 1 step, 1 trigger. One tag claims more than its eval grades, and two rows assume a code fix with a build.

## Scope

In scope: the rules table under The list, which sub-batch A made from a numbered list, its five rows, each row's tag, and how each row agrees with the rest of the page. I read the whole page and its sub-batch A diff. Beside it I read `AGENTS.md`, `INDEX.md`, `workspace.json`, the `rules` part, the eval case `evals/cases/fix-a-bug.json`, `docs/playbooks/fix-a-bug.md`, `src/README.md`, and the register from `python3 ws.py rules`. The review is of commit 166bbc7.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | enforcement | The list, the row on marking every claim | The row is tagged `eval:fix-a-bug`, but that case's only report grader, `report-marks-a-claim-verified`, passes when one claim is marked verified. No grader checks that every claim is marked, or that any claim is marked inferred. The contract's rule on the same point carries the same tag. Verified by reading `evals/cases/fix-a-bug.json`. | queued for slice Z: the page is hashed. Retag as for the contract's rule. |
| 2 | trigger | Purpose line, and the list's row on a test that came first | The purpose line covers every finished change, and the contract says work is done when it meets this page. The first row then requires a test that failed before the fix, with no exception for a doc-only change, which has no fix to test. Such a change can never be done. Verified by reading the page and `AGENTS.md`; the consequence is inferred. | queued for slice Z: the row applies where the change has behavior a test can show. |
| 3 | step | The list, the row on a clean build | The row asks for a comparison of build warnings with the base branch but names no build. Unlike the running-app row, it has no exception for work that has none. The page, the fix-a-bug playbook and `src/README.md` name no build command, so an agent has no default. Verified by searching those three files. | queued for slice Z: the row applies where the work has a build, as the running-app row does. |

## Checked with no finding

- Contradiction: compared each row with the sections The report and What does not count, and with the contract's verified-or-inferred rule. They agree.
- Placement: the rules sit on the page that `AGENTS.md` and the fix-a-bug playbook route to. Nothing moved into the always-loaded layer.
- Eval-case: sub-batch A turned an existing list into a table and added an In short line, so it asks no new behavior. The test-first row is graded by two fix-a-bug graders.
