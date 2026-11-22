---
kind: record
last-reviewed: 2026-11-22
covers: docs/research-ladder.md
reviewed-at: 31f9aaa, with the uncommitted change of the B2 builder
---

# Instruction review: docs/research-ladder.md

This records the instruction review of batch 4's edit to the research ladder, for its author and for agents about to search.

**In short:** 1 finding: 1 contradiction.

## Scope

In scope: the batch 4 edit, one sentence added to the paragraph under "Pick one lookup" that begins "Move to another row only in two cases", which sends the reader to search every source; and anything on the page it contradicts or leaves stale, including the lookup table, "Offer to write a finding down" and "Rules". Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md`, the new search every source playbook, and the other batch 4 pages and edits. Ran `git diff docs/research-ladder.md` and `python3 ws.py check` (no finding on this page; its review date is not stale).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | "Pick one lookup", the paragraph on moving to another row | The sentence before the edit says that when the last fitting row comes back empty, "ask the person or delegate a wider sweep". The table's last row is already a sweep handed to a helper, so a wider sweep after it can only reach outside the workspace. The new sentence and search every source allow outside sources only when the person asks for them. The stale sentence still lets an agent delegate a sweep beyond the workspace without that ask, and gives no default between asking and delegating. Verified by reading the table and the paragraph; that "wider" means outside the workspace is inferred. Cause: route-in-one-sentence-limit — the brief lets a builder edit only the one route-in sentence on the page that routes in, so the adjacent sentence it made stale was left as it was. | fixed: the stale "or delegate a wider sweep" is gone; an empty last row now means report and ask the person what to do next. |

## Checked with no finding

- step: the new sentence names its condition, matching the sheet's section 9 and the catalog row, and the link target exists.
- trigger: the condition "the answer needs sources outside the workspace ... and the person asks for them" matches search every source's "When to use it" and the playbook catalog's "Any stage" row.
- enforcement: the edit adds no must or never. The rule against stacking lookups still holds; search every source scopes it to its step 1 and says why each outside source gets its own search.
- placement: the edit links to the playbook rather than restating its steps.
- eval-case: the page is `proof: unproven`, `prove-by: M4`, so the new route needs no case yet.

## Re-check

A fresh session re-read the page on 2026-11-22, after the fix round.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | `git diff 31f9aaa -- docs/research-ladder.md` shows "or delegate a wider sweep" replaced by "ask the person what to do next", which matches search every source's trigger on a person asking to search further; verified by running the diff and reading both pages. |

Broke: none.
Missed: none.
