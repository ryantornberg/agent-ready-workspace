---
kind: record
last-reviewed: 2026-11-28
covers: kit/seed/evals-README.md
reviewed-at: ba17f28, with the uncommitted change of the H0a builder
---

# Instruction review: kit/seed/evals-README.md

This records the instruction review of slice H0a's change to the kit's seed eval page, for its author and readers of the result.

**In short:** 2 findings, 2 blocking: 1 step, 1 contradiction.

## Scope

In scope: the uncommitted diff on ba17f28, the paragraph under "The gate" that now names two hashes and the stamp. The rest of the page was read for statements the change makes false. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `evals/README.md` as changed, `kit/kit.json` (`evals/grade.py` is synced), the plan's H0a section, Q88, Q102 and criterion 61, and the committed code from the merge base f04fddf to ba17f28: `evals/grade.py`, `parts/eval_record.py`, `evals/run.py`'s `build_record`.

Run in a clone of the branch with the uncommitted pages applied, in a scratch folder: `python3 ws.py check`, with two simulations: a record with its grader fields removed, and a `grade.py` edit that changes a grade followed by a re-grade of the fix-a-bug records as a new recording would grade them.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | "The gate", "an edit to any of them fails the commit until the case is run again" and "a grade that differs means the case is run again" | Blocking. The synced `run.py` writes no grader hash at H0a (verified: `grep grader evals/run.py`), and `eval_record` fails a record with none (verified: `python3 ws.py check` on a record with the fields removed reported "holds no grader hash"). So in an instance, the run the page names leaves the commit failing until `python3 evals/grade.py --recorded --stamp` runs. The page gives the run as the whole remedy. | fixed: the page names the stamp after every run, before the commit |
| 2 | contradiction | "The gate", "a grade that differs means the case is run again" | Blocking. When the grading file that changed is `grade.py` itself, as in a kit upgrade that changes a grading rule, running the case again does not pass: the stamp and CI re-grade the new runs with the base commit's `grade.py` too, which applies the old rule. Verified by simulation in this repository: after such an edit and a re-grade of the fix-a-bug records by the new copy, the base commit's copy found 194 differences in them and `--stamp` wrote nothing. That it reaches an instance the same way is inferred: the instance gets the same synced `grade.py`. | fixed in code: the base commit's `grade.py` now judges only the runs the base holds, and a run recorded since the base is judged by this `grade.py` alone (`evals/grade.py` `judged_by_base`; test `test_a_grade_py_change_that_alters_a_stored_grade_fails_and_passes_once_the_case_is_recorded_again`); the page says a case run again is then stamped |

## Checked with no finding

- trigger: the page has no In short line, and the change does not alter when it applies. Verified.
- enforcement: the new sentences state what `eval_record` and the stamp do, and both are synced with the kit; the cases `eval_record#an edit to grade.py alone fails until the stamp writes the new grader hash` and `eval_record#after the stamp, an edit to grade.py alone passes` show it (verified: `parts/eval_record.cases.json`). "The cases" still calls the harness `run.py`, `grade.py`, `pool.py` and `proofkeys.py`; "The gate" now qualifies its hash as over "the harness that runs the agent", so the two do not conflict.
- placement: the paragraph stays short and leaves the base copy and the migration to the kit's own eval page, which an instance does not need. Verified.
- eval-case: the seed page is not a playbook or how-to; it asks no behavior an eval case would cover. Verified.
