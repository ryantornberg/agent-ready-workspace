---
kind: record
last-reviewed: 2026-11-21
covers: docs/orchestration.md
reviewed-at: 8b33280, with the uncommitted change of the B2 builder
---

# Instruction review: docs/orchestration.md

This records the instruction review of the orchestration page with its new "Delegating" section, for its author and for agents who delegate work.

**In short:** 1 finding: 1 contradiction. The moved text lands without loss, but the new write-it-down bullet tells you to write unconditionally, while the page it cites says to write only on a yes.

## Scope

In scope: the whole page, with the new "Delegating" section, the shortened "Handing work off" list and the two new rules rows in focus. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/layout.md`, `docs/glossary.md`, `docs/research-ladder.md`, `docs/changing-the-machinery.md`, `docs/parts.md`, `docs/templates/hand-off-plan.md`, `docs/playbooks/instruction-review.md` and `workspace.json`. Read `git diff docs/orchestration.md` to compare the moved text with the old list. Ran `python3 ws.py rules` and `python3 ws.py check`.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Delegating, the "Write down what must outlive the session" bullet | The bullet says, unconditionally, "Before you finish, put each finding that matters in the one place it belongs", citing the research ladder. That section of the research ladder says to offer in one line, write only if the person says yes, and with no answer, as in an unattended run, write nothing. Its table of places also holds only findings the workspace should have recorded, so most findings a helper returns have no place in it. Verified: read both sections. | fixed: findings go to the record the task names; one for a guidance page goes through the research ladder's offer, written only on a yes. |

## Checked with no finding

- step: `python3 ws.py check` passes, and its link check resolves `#delegating`, `#fresh-context-for-critics` and `research-ladder.md#offer-to-write-a-finding-down`. The instruction-review playbook's link to `#handing-work-off` still resolves. Each row of the delegating table gives a yes or no, and each yes a tier or a fresh session.
- trigger: the title, purpose and **In short** lines are unchanged and still name delegation and handoff. The index row "Which model and effort a task gets; delegating" points here.
- enforcement: `python3 ws.py rules` lists the two new rows, both `prose`. The `handoff_tier` tags pass the `rules` check. The one remaining "never" without a row, a helper never returning whole files, falls under the closing line "The rest is prose".
- placement: delegation is merged into this page, as the M3 plan's slice B2 says. Every line removed from "Handing work off" now sits in "Delegating", and "Handing work off" links there for the shape of the answer, so nothing is duplicated.
- eval-case: the page is marked `proof: unproven` with `prove-by: M4`, and the new section carries its own line, "Proof: unproven, prove-by M4."
