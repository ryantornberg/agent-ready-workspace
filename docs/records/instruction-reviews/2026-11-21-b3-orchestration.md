---
kind: record
last-reviewed: 2026-11-21
covers: docs/orchestration.md
reviewed-at: 9f3de36, with the uncommitted change of the B2 builder
---

# Instruction review: docs/orchestration.md

This records the review of batch 3's one-bullet edit to the orchestration page, which routes a stopping session to the handoff playbook.

**In short:** 0 findings. The bullet separates a session stopping mid-task from delegation, names its condition, and contradicts nothing on the page or the handoff playbook.

## Scope

In scope: the new bullet under "Handing work off" ("A whole session stopping mid-task is not a handoff to a helper"), read with `git diff docs/orchestration.md`, and anything on the page it contradicts or leaves stale. Read beside it: the whole page, `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/layout.md`, `docs/glossary.md` with its batch 3 diff, `docs/playbooks/handoff.md`, `docs/templates/hand-off-plan.md`, and `docs/playbooks/instruction-review.md`. Commands run: `python3 ws.py rules` and `python3 ws.py check` (exit 0, one unrelated `eval_record` warning).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|

No findings.

## Checked with no finding

- contradiction: the bullet says a stopping session is "not a handoff to a helper", so the list's first bullet, "Every handoff names its tier", and the **In short** line's tier rule still mean delegation only; the handoff playbook asks for no tier, and nothing here says it should. The "Write down what must outlive the session" bullet under "Delegating" and the handoff page agree that findings go to the record the task names, such as the plan's "Results". Verified: read both pages.
- step: the link `playbooks/handoff.md` resolves, and `python3 ws.py check` reports no `links` finding. Verified.
- trigger: the sentence that links the playbook names its condition, "when a later session will carry on the task, such as when your context runs low", which matches the playbook's "When to use it" table and its catalog row. The page's title, purpose and **In short** lines are unchanged and still scope it to delegation. Verified.
- enforcement: the bullet holds no must or never, so it needs no row in "What enforces this"; the existing rows are unchanged and `python3 ws.py rules` lists their tags. Verified.
- placement: the bullet sits in "Handing work off", where a reader deciding whether to hand work to a helper would meet it, and it routes out rather than restating the handoff procedure. Verified.
- eval-case: the page is `proof: unproven` with `prove-by: M4`, and the bullet asks for no new behavior beyond the linked playbook, which is unproven with `prove-by: M6`. Verified.
