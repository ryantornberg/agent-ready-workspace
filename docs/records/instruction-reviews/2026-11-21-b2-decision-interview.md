---
kind: record
last-reviewed: 2026-11-21
covers: docs/playbooks/decision-interview.md
reviewed-at: e1d978a, with the uncommitted change of the B2 builder
---

# Instruction review: docs/playbooks/decision-interview.md

This records the instruction review of the new decision-interview playbook, for its author and for agents who run an interview.

**In short:** 4 findings: 1 contradiction, 2 step, 1 enforcement. The question loop runs as written. The defects sit at the edges: where the summary goes, and who finishes the doc changes the interview starts.

## Scope

The whole page was in scope, since it is new. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md`, and the other pages of the batch: `docs/playbooks/adversarial-review.md`, `docs/size-the-work.md`, `docs/playbooks/README.md`, `docs/how-tos.md`, with the diffs to `README.md` and the glossary. Also read every page it links to: `docs/playbooks/fix-a-bug.md`, `docs/research-ladder.md`, `docs/playbooks/throwaway-prototype.md`, `docs/playbooks/instruction-review.md`, `docs/question-log.md`, `docs/templates/hand-off-plan.md`, and the front matter of every record in `docs/decisions/`. Ran `python3 ws.py rules` and `python3 ws.py check`; the check passed with one unrelated warning. Read the `review_trailer` entry in `workspace.json` and the status values in `parts/page_kinds.py`. Searched `AGENTS.md`, `evals/README.md` and `docs/` for a defined batch or queue of eval-covered edits.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | The summary; the Settled decisions section of the hand-off plan template | The page writes the whole summary, with its open questions, doc changes and next step, under "Settled decisions". The template says that section holds the person's decisions, and its step 2 says "Do not reopen them". So an open question lands in a section a later agent is told to treat as settled. Verified: read "How to use it" step 2 and the skeleton in `docs/templates/hand-off-plan.md`. `docs/size-the-work.md`, under "Where it lives", repeats the page's placement, so the batch agrees with itself but not with the template. | fixed: the decisions alone go under Settled decisions; open questions, doc changes and next step go in a separate dated section after it. |
| 2 | step | Where a term goes, the INDEX.md row | An alias row is to be written "with the next batch of eval-covered edits". The workspace defines no such batch and no place that lists edits waiting for one. The row then lives only in this plan's summary, where nobody running an eval batch is told to look. Verified: searched `AGENTS.md`, `evals/README.md` and `docs/`; the contract and the research ladder say only "batch such edits". | fixed: the alias row is no longer written during the interview; it is listed as waits for an eval run and named in the report, so the person schedules the run. |
| 3 | step | Steps, steps 7 to 10; Where a term goes | Step 7 writes a glossary row at once, and step 8 may write a decision record. The page then says to "have the review run once, after the interview", but step 10 ends with "Stop", and no step runs or hands off that review, or commits the rows. Verified: read steps 7 to 10 and the paragraph under "Where a term goes"; the summary's Doc changes part only records whether the review ran. Inferred: the rows can sit as unreviewed, uncommitted edits, which the contract tells other sessions to leave alone. | fixed: step 10 now runs the instruction review on the glossary rows and decision records and commits them with the plan, staged by name, before it stops. |
| 4 | enforcement | When to use it | "It is never handed to a helper" is a never with no row in the page's Rules table. Verified: the Rules table holds seven rows, and none covers running the interview in the person's own session. | fixed: the Rules table gained a row for running the interview in the person's own session, never a helper. |

## Checked with no finding

- trigger: the purpose line, the **In short** line and "When to use it" match the Grill rung of the size gate's ladder, the feature ladder's step 1 and the playbook catalog's row. The skip case, a bug report with a clear cause, matches the ladder's own example. The page has a row in the playbook catalog, under "Before building".
- placement: the page sits in `docs/playbooks/` as a playbook, adds nothing to the always-loaded layer, and points at the research ladder, the throwaway prototype and the instruction review rather than restating them. Its three-condition test for a decision record lives here once, and `docs/size-the-work.md` links to it.
- eval-case: the page is marked `proof: unproven` with `prove-by: M9`, and the catalog's Proof column matches.
