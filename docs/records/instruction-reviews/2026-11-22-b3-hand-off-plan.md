---
kind: record
last-reviewed: 2026-11-22
covers: docs/templates/hand-off-plan.md
reviewed-at: f757aed, with the uncommitted change of the B3 builder
---

# Instruction review: docs/templates/hand-off-plan.md

This records the instruction review of B3's change to the hand-off plan template, for its author and for agents writing or orchestrating a plan.

**In short:** 3 findings, none blocking: 1 enforcement, 1 placement, 1 step. The budget rule is tagged `prose` and called planned, though the `plan_budgets` check that enforces it is built and running; the nudge procedure for helpers sits on a template instead of the delegation page, and has no path when a helper cannot be resumed.

## Scope

In scope: the uncommitted change shown by `git diff -- docs/templates/hand-off-plan.md`, read in the context of the whole page. The change adds a sentence to the **In short** line, the paragraph tying the plan to the spec, steps 8 to 11 of "How to use it", the section "The execution profile", the skeleton's "Decisions made without asking", Goal placeholder, slice-detail note and "Execution profile" sections, and a new "Rules" table.

Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/instruction-review.md`, `docs/procedure-endings.md`, `docs/layout.md`, `docs/reader-standard.md`, `docs/authoring.md`, `docs/orchestration.md`, `docs/size-the-work.md`, `docs/templates/spec.md`, `docs/templates/epic-folder.md`, `docs/templates/README.md`, `docs/records/README.md`, `parts/plan_budgets.py`, `parts/plan_budgets.cases.json`, the `plan_budgets` entry in `workspace.json`, `parts/page_kinds.cases.json`, and B3's row and the 2026-11-22 "Changes after approval" entries of the M3 plan. Ran `python3 ws.py check` in the worktree (exit 0, one unrelated `eval_record` warning; links and anchors resolve), `python3 ws.py rules`, and `evals/run.py`'s `covered()` for the three eval cases.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | enforcement | "Rules", the budgets row | Not blocking. The row says "A check for both is planned for M3" and is tagged `prose`. The check exists: `parts/plan_budgets.py` is committed on this branch as `8c08faf`, `workspace.json` lists it, and `python3 ws.py check` runs it. Its cases "a draft whose Key points block is over 200 words fails" and "a draft with a table cell over 60 words fails" show the rule. So the stated enforcement is false, and the row describes a built thing as planned, the reverse of the style guide's rule. The tag should name those two cases. Verified: read the part, its cases and the manifest entry, and `ws.py rules` lists the row as `prose`. | fixed: the budgets row now names `plan_budgets`'s two failing cases, and step 8 says the cell budget covers every table cell outside fenced blocks. |
| 2 | placement | "The execution profile", the paragraph on a helper's turn ending | Not blocking. The paragraph is a procedure for the orchestrating session: treat a helper's text as a report, send its open items, nudge up to N times, then halt the slice. That is delegation behavior, which [orchestration](../../orchestration.md) owns ("how work is handed to a helper session"), and whose "Delegating" section is marked unproven with `prove-by: M4`. On a template, which carries no proof key, the new behavior has no eval case and no milestone to prove it. The profile line "Nudges" can stay here, with the procedure on orchestration and a link. Verified: orchestration's purpose line and proof line; `covered()` lists no template for any eval case. | deferred to M4: orchestration's "Delegating" section, which M4 proves, takes the nudge procedure; the template keeps the paragraph until then, so the behavior is not lost |
| 3 | step | "The execution profile", the paragraph on a helper's turn ending | Not blocking. "Send the helper its open items and ask it to go on" assumes the orchestrator can resume a helper whose turn ended. The page gives no default for an agent tool that cannot, where the only move is a new helper, which orchestration's "do not redo work a helper returned" bears on. Pages beside it give such fallbacks, such as search every source's "Where the agent tool cannot start a helper". Inferred: that some agent tools this workspace supports cannot message a finished helper. | fixed: the paragraph now says to start a new helper with the slice, the open items and the first helper's return when the tool cannot message an ended helper, counted as one nudge. |

## Checked with no finding

- contradiction: steps 8 to 10 agree with `docs/size-the-work.md`'s "Where it lives" (the spec's three sections come first, "Settled decisions" aside) and with the spec template's "The standalone specs". Rule 8's budgets, its word definition, the per-slice `###` headings and its draft-only scope match `plan_budgets.py`: a word is a whitespace-split token, so bullet markers count, which the definition allows; the Key points block ends at the next level-one or level-two heading; approved, done and abandoned plans are skipped. The new section order in the skeleton keeps Key points first, as `page_kinds#a plan whose first section is not Key points fails` requires. Verified.
- trigger: the added **In short** sentence fires for an orchestrated plan only, and step 11 tells a plan with no orchestrator to write "none". The page's top layer is 108 words. Verified.
- eval-case: no eval case covers the template (`covered()` lists none for `big-report`, `fix-a-bug` or `nightly-job`). The plan-writing steps run under the feature ladder of `docs/size-the-work.md`, which is unproven with `prove-by: M9`. The one new behavior outside it is finding 2's. Verified.

## Re-check

A fresh session re-read the page on 2026-11-22, after the fix round.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | The budgets row now cites `plan_budgets#a draft whose Key points block is over 200 words fails` and `plan_budgets#a draft with a table cell over 60 words fails`. Both names are in `parts/plan_budgets.cases.json`, and the part's docstring matches step 8: a cell "anywhere in the plan outside a fenced block". Verified. |
| 2 | deferral upheld | The finding is not blocking: a misplaced paragraph meets none of the four conditions in "Severity". "Deferred to" a milestone is a listed form, and M4 proves orchestration's "Delegating", the page that owns delegation. Verified, by reading. Inferred: only this record carries the deferral to M4. |
| 3 | fixed | The paragraph now says to start a new helper with the slice, the open items and the first helper's return when the tool cannot message an ended helper, and counts it as one nudge. Verified, by reading. |

Broke: none.

Missed: none.
