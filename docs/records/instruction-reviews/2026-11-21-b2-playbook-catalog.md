---
kind: record
last-reviewed: 2026-11-21
covers: docs/playbooks/README.md
reviewed-at: e1d978a, with the uncommitted change of the B2 builder
---

# Instruction review: docs/playbooks/README.md

This records the instruction review of the new playbook catalog, for its author and for agents who choose a procedure from it.

**In short:** 3 findings: 3 trigger. The proof column is right on every row; the routing is not. A small bug of unknown cause, and a small change that is not a bug, each match two routes with no tie-break, and the instruction review row fires on pages that need no review.

## Scope

The whole page was in scope, since it is new. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `README.md` (its proof table and the diff to it), `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md`, `docs/decisions/0006-what-proven-means.md`, and every page the catalog links to: the seven playbooks, `docs/size-the-work.md` and `docs/how-tos.md`. Also read `workspace.json`, `parts/proof.py`, `evals/cases/fix-a-bug.json` and slice B6's row in `docs/plans/m3-reading-layer-machinery-and-kit.md`. Ran `python3 ws.py check`, which passed with one warning unrelated to this page, and searched `parts/` for any reference to the catalog. Each row's trigger was compared with its playbook's purpose line, **In short** line and "When to use it" or "When it runs" section; the rows for decision interview, throwaway prototype, adversarial review and test first match their pages.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | The catalog, rows Debugging and Fix a bug; Before you pick one | A small bug whose cause is not known fires both rows, and the page gives no tie-break. "Before you pick one" says every request goes through the gate first and a small change goes straight to fix a bug. But `docs/size-the-work.md`, "When to write a spec", sends a bug whose cause is not known to debugging first, and only then puts the fix through the gate. Verified: fix a bug's eval request, "The Export button on the orders page does nothing. Fix it and commit the fix.", states no cause and matches the Debugging row ("Something fails and you do not yet know why") as well as the Fix a bug row. That an agent would pick either route is inferred. | fixed: Before you pick one now gives the tie-break (fix a bug when you can write a test that fails for the report's reason, debugging when you cannot yet say what it is), and the Debugging row says the same. |
| 2 | trigger | The catalog, rows Fix a bug and Test first; Before you pick one | "Before you pick one" sends any small, easy-to-reverse change to fix a bug, as the contract does. The Fix a bug row fires only on "A bug whose fix is small", so a small change that is not a bug matches no row of its target. It matches the Test first row ("code that adds or changes behavior") instead. Verified: read the paragraph, both rows, `AGENTS.md`'s "How work flows" and fix a bug's purpose line ("The steps for a bug"). | fixed: the Fix a bug row now fires on any change that passes the size gate, as the contract routes it, with safe refactor named as the one exception, and Test first fires only on a route already chosen. |
| 3 | trigger | The catalog, row The instruction review | The row gives "a page under `docs/`" as an example of a guidance page. The `review_trailer` entry excepts `docs/plans/`, `docs/milestones/`, `docs/records/` and `docs/question-log.md`, so the row fires on commits that need no review, such as one adding a plan or an adversarial review record. Verified: read the `review_trailer` entry's `guidance` and `except` lists in `workspace.json`, and the instruction review's "When it runs". | fixed: the row now names the guidance pages as the review_trailer entry lists them, excepting plans, milestone records, records and the question log. |

## Checked with no finding

- contradiction: each row's proof state matches its page's front matter and `README.md`'s proof table, all seven (fix a bug proven; decision interview and adversarial review unproven, M9; the other four unproven, M4), and `python3 ws.py check` passed with the `proof` check in it; the meaning given to "unproven, M4" matches decision 0006; the grill and red team mapping and the stage order match `docs/size-the-work.md`'s ladder and feature ladder; the wrapper statements match the glossary's Wrapper row, the how-to index, the instruction review's guidance list and slice B6 in the M3 plan.
- step: the page's one procedure, find a row and open its page, can be followed; all seven playbook files in `docs/playbooks/` have a row and every row's link resolves (the `links` check passed); the anchors `#the-gate`, `#the-ladder`, `#three-ways-to-follow-a-playbook` and `#proven-and-unproven-pages` exist.
- enforcement: both rules are tagged `prose` and the first says no check catches a missing row, which holds (no part in `parts/` names the catalog); the claim that the `proof` check holds the README's table to the pages holds (`parts/proof.py`'s docstring and its config key `readme`).
- placement: a reference page loaded only when a reader picks a procedure; it adds nothing to the always-loaded layer, restates no playbook's steps, and sends the ways to follow a playbook to the how-to index rather than repeating them.
- eval-case: a reference page with no proof mark that asks no behavior of an agent beyond choosing a row; the `eval_record` check passed with the page in place.
