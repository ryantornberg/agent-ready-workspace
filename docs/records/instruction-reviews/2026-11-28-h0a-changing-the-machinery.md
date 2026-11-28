---
kind: record
last-reviewed: 2026-11-28
covers: docs/changing-the-machinery.md
reviewed-at: ba17f28, with the uncommitted change of the H0a builder
---

# Instruction review: docs/changing-the-machinery.md

This records the instruction review of slice H0a's change to changing the machinery, the grader stamp, for its author and readers of the result.

**In short:** 5 findings, 3 blocking: 3 contradiction, 2 step.

## Scope

In scope: the uncommitted diff on ba17f28, two sentences added to the trap "A change the eval covers cannot pass the commit check until the eval has run", and the page's "Rules" table, which states the same rule. The rest of the page was read for statements the change makes false. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md` (the row "Change the eval harness or a grader"), `evals/README.md` as changed, `parts/edit_ledger.py`'s docstring and message, the plan `docs/plans/m4-fail-closed-guards-review-loop-and-evals.md` (the H0a row and section, Q88, Q102, criteria 13 and 61, the stop rule's fallback, triage item R2-11, and "No `--no-verify`" under H0a), and the committed code from the merge base f04fddf to ba17f28: `evals/grade.py`, `parts/eval_record.py`, `evals/run.py`'s `build_record`.

Run in a clone of the branch with the uncommitted pages applied, in a scratch folder: `python3 evals/grade.py --recorded`, `python3 -m unittest tests.test_m4_h0a` (11 tests, OK) and `python3 ws.py check`, with two simulations: a record with its grader fields removed, and a `grade.py` edit that changes a grade followed by a re-grade of the fix-a-bug records as a new recording would grade them.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | "Traps", the bullet "A change the eval covers cannot pass the commit check until the eval has run", against `AGENTS.md`'s rules table | Blocking. The bullet now says a change to grading files alone "needs no run: run `python3 evals/grade.py --recorded --stamp` and commit the records it rewrites". The contract says a change "to anything else the eval covers, needs a new eval run on record". The grading files are in the record's grader hash, so on a plain reading the eval covers them, and an agent following the bullet acts against the contract (verified: both texts). The plan accepts the contract being wrong until H0b rewrites its eval rule (triage item R2-11; verified), but the page does not label it as an exception. | fixed: the page labels the exception until M4's slice H0b rewrites the contract's eval rule; the contract edit is queued for H0b |
| 2 | step | "Traps", the same bullet, the sentence "When the stamp finds a grade that differs, it writes nothing, and the case is recorded again", and the last sentence, "open no pull request until the commit with the records passes every hook" | Blocking. At H0a, `run.py` writes a record with no grader hash (verified: `grep grader evals/run.py` finds no `grader_sha256`), and `eval_record` fails such a record: with those fields removed from the fix-a-bug record, `python3 ws.py check` reported "holds no grader hash; run python3 evals/grade.py --recorded --stamp" (verified). So after the recording the bullet sends the agent to, the commit with the records fails until the stamp runs again. The page names no stamp after a recording. | fixed: the trap names the stamp after every recording, before the commit |
| 3 | contradiction | "Traps", the same bullet, "the case is recorded again" | Blocking. For a change to `evals/grade.py` that changes a grade, recording again does not pass. The stamp and CI re-grade the new runs with the base commit's `grade.py` too, which applies the old rule. Verified by simulation: after such an edit and a re-grade of the five fix-a-bug records by the new copy, the base commit's copy found 194 differences in them, this copy none, and `--stamp` printed "nothing stamped". The bullet offers recording again as the remedy for every grading file. | fixed in code: the base commit's `grade.py` now judges only the runs the base holds, and a run recorded since the base is judged by this `grade.py` alone (`evals/grade.py` `judged_by_base`; test `test_a_grade_py_change_that_alters_a_stored_grade_fails_and_passes_once_the_case_is_recorded_again`); the trap says record again, then stamp |
| 4 | contradiction | "Traps", the bullet's bold lead; "Rules", the row "A change the eval covers fails the commit check until the eval has run again and its new records are committed" | Not blocking. The bold lead and the rules row both still say a change the eval covers passes only after the eval has run again. The bullet's body now says a change to grading files alone needs no run. The exception is not labelled in the lead or the row, and the rules table has no row for the stamp path, though cases for it exist (`eval_record#after the stamp, an edit to grade.py alone passes`). An agent reading the table runs a recording the stamp would have saved. Verified: the page's text and `parts/eval_record.cases.json`. | fixed: the bold lead names the stamp, and a Rules row holds the stamp path with its three cases |
| 5 | step | "Traps", the same bullet, the sentence after the inserted ones | Not blocking. "To save the work before the costly runs, commit it on its branch with `git commit --no-verify`" now follows the grading sentences, so "it" can be read as the grading change. The plan says H0a's kind of change lands with no `--no-verify` and passes every hook. Inferred: a reader may skip the hooks on a change that needs none. | fixed: the sentence reads "To save a change that needs the runs", and the stamp path says no `--no-verify` |

## Checked with no finding

- trigger: the page's purpose and In short lines are unchanged and still cover a change to `evals/grade.py` or a hook, which are machinery; `INDEX.md`'s row "Change the eval harness or a grader" routes here. Verified.
- enforcement: the new sentences add no must or never of their own; the stamp's refusal on a differing grade is held by `test_a_grade_that_differs_stamps_nothing_and_the_record_keeps_failing`, which passes (verified). The records the stamp rewrites are written by a script, so a commit while the edit ledger is open needs `python3 ws.py ledger --add PATH` for each; the contract states that rule and `edit_ledger`'s refusal names it, so the page need not restate it (verified: `parts/edit_ledger.py`).
- placement: the stamp's procedure sits in the trap about the eval, beside the costly-run path, and the gate's details are left to the eval page. Verified.
- eval-case: the page is marked unproven, `prove-by: M4`. Verified.
