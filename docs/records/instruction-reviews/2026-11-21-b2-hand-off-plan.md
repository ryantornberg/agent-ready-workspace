---
kind: record
last-reviewed: 2026-11-21
covers: docs/templates/hand-off-plan.md
reviewed-at: e1d978a, with the uncommitted change of the B2 builder
---

# Instruction review: docs/templates/hand-off-plan.md

This records the instruction review of the B2 edit to the hand-off plan template's step 4, for its author and for agents writing a plan.

**In short:** 2 findings: 2 contradiction. The new link resolves and routes to the right playbook, but step 4 and the skeleton's Red team table disagree with what the adversarial review says happens there.

## Scope

In scope: step 4 of "How to use it", which the uncommitted change rewrites to link the adversarial review, and the parts of the page it must agree with: the purpose line, steps 5 and 6, and the skeleton's "Red team" section. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md`, `docs/playbooks/instruction-review.md`, and chiefly `docs/playbooks/adversarial-review.md`. Also read the other batch 2 pages where they name the red team table: `docs/size-the-work.md` and `docs/how-tos.md`. Ran `git diff docs/templates/hand-off-plan.md`, `python3 ws.py check --changed` (passes; links and anchors resolve), and listed each eval case's covered files with `evals/run.py`'s `covered()`. Read the Red team sections of the four plans in `docs/plans/` to see the table in use.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | "How to use it", step 4; the skeleton's "Red team" section | The adversarial review's step 5 says to write the triage "in its own Red team table, as the hand-off plan template asks, and link the record above the table". The template asks for no record link: step 4 says only "Record every finding in the triage table", and the skeleton's Red team section is a bare table with no line for the record. The table's "Verdict" column also holds what the playbook calls a disposition (`accepted`, `rejected`, `deferred to <where>`), while the playbook uses "verdict" for the record's `holds` / `holds with fixes` / `does not hold`. Verified: read both pages and the four plans' Red team tables. | fixed: the skeleton's Red team section now opens with a record link line, and its column reads Disposition, the playbook's word. |
| 2 | contradiction | "How to use it", steps 4 and 5 | Step 4 says, with no condition, "Record every finding in the triage table", and step 5 goes on to ask the person to approve. The adversarial review's step 4 says that on a `does not hold` verdict the author fixes nothing, commits the record alone and reports to the person: "That ends the procedure", with no triage. On that verdict an agent cannot follow both pages. Verified: read both steps. | fixed: step 4 now stops on a does-not-hold verdict, commits the record and reports, before step 5's approval. |

## Checked with no finding

- step: the new link `../playbooks/adversarial-review.md` resolves (`ws.py check --changed` passes); "a fresh session" agrees with the playbook's step 2, which lets a session that never wrote or edited the plan act as critic; "It gets the plan and the sources, never your reasoning" matches the playbook's template and its first rule.
- trigger: the purpose line ("a fresh session red-teams it") and the how-to index row still route a plan writer here and on to the playbook; the playbook's "When it runs" names a finished hand-off plan, so the link fires on the right documents.
- enforcement: step 4's "never your reasoning" now points at the playbook, whose Rules table tags that rule `prose`, which is true. The page's review date, 2026-11-18, is inside the 180-day limit in `workspace.json`, so no review-date move is due.
- placement: the protocol stays on the playbook and step 4 carries one link and one sentence of it, which is right for a template.
- eval-case: no eval case covers this page; `covered()` lists no template file for `big-report`, `fix-a-bug` or `nightly-job`. The behavior it now points to is on the adversarial review, marked unproven with `prove-by: M9`.
