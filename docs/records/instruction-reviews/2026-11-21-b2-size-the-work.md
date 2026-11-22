---
kind: record
last-reviewed: 2026-11-21
covers: docs/size-the-work.md
reviewed-at: e1d978a, with the uncommitted change of the B2 builder
---

# Instruction review: docs/size-the-work.md

This records the instruction review of the B2 edits to the size-the-work page, for its author and for agents sizing or building a feature.

**In short:** 3 findings: 2 contradiction, 1 placement. The feature ladder's steps run as written; the phases table orders the red team before slicing, and two skip rules for the grill disagree.

## Scope

In scope: the new sections "The feature ladder" and "The spec process", every other line the uncommitted change touches (purpose, **In short**, the ladder table's Grill, Spec and Red team rows, the decision-record paragraph, the new Rules table), and the whole page for consistency with them. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md`, and every page it links: fix a bug, decision interview, adversarial review, debugging, test first, throwaway prototype, safe refactor, research ladder, browsers, the hand-off plan and milestone record templates. Also read the other batch 2 pages: the playbook catalog, the how-to index, and the README and glossary diffs. Ran `git diff docs/size-the-work.md`, `python3 ws.py check --changed` on the batch's pages (no finding on this page; links and anchors resolve, proof lines and the README table agree), and read `src/orders-api/AccountFreeze.cs` and `ls src/*`.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | "The four phases" table | The table puts the adversarial review in the Plan phase and the slices table in the later Slice phase, so the red team runs before slicing. "The feature ladder" step 2 and "The ladder" table both write the slices first, then red-team. Adversarial review's step 1 also stops on a plan whose pre-approval sections, slices included, are not filled. The table's Specify row likewise reads "the decision interview, then the plan's goal, non-goals", while step 1 and "Where it lives" write goal and non-goals before the interview. Verified: read all four places. | fixed: the phases table now writes goal and non-goals before the interview, and puts the adversarial review in the Slice phase after the slices table, matching step 2, the ladder and the adversarial review's step 1. |
| 2 | contradiction | "The ladder", the paragraph after the table; "The feature ladder", step 1 | The ladder says skip a rung "only when the rung below it already holds its answer". Step 1, and the decision interview's "When to use it", skip the grill only when "the code, the docs or the request" settle every question. A request that settles every question while no other rung holds the answer passes one rule and fails the other. The paragraph's own example, a bug report with a clear cause, is a request, not a rung. Verified: read both pages. | fixed: the ladder's skip rule now reads: skip a rung only when its answer is already in hand, from an earlier rung, the code, the docs or the request, which matches step 1 and the decision interview. |
| 3 | placement | "The feature ladder" | The section is a request-to-report procedure: "Input: the request" through "Stop when the definition of done's report is written". The layout's Page kinds table defines that as a playbook, and a how-to as steps for one task. On a how-to page it has no row in the playbook catalog, where an agent choosing a procedure looks. Verified: read `docs/layout.md` and `docs/playbooks/README.md`. Inferred: it cannot get a B6 wrapper, since the glossary says a wrapper points at a playbook page. | declined: the M3 plan's B2 row merges the feature ladder into size-the-work.md by name, so moving it to a playbook is outside this slice; the how-to index routes to the section, and wrappers are being widened to procedure pages, so the wrapper inference no longer holds. |

## Checked with no finding

- step: every linked page and anchor exists (`ws.py check` passes the page); each of the seven steps names its input, output and default; the stop rule covers a declined spec, a declined plan and a halting recovery. Step 5's review and step 6's impact check name the M4 orchestrator and the later impact page as planned and give a manual way to proceed today.
- trigger: the purpose and **In short** lines now name the feature ladder and the spec; the how-to index routes to both sections with their conditions, and the playbook catalog's "Before you pick one" routes through the gate and the ladder.
- enforcement: the new Rules table tags each rule `prose`, which is true; no check claims to enforce them. The new sections' "never", "do not" and "no plan" lines each map to a row.
- eval-case: the page and both new sections are marked unproven with `prove-by: M9`, so their new behavior needs no case yet.
