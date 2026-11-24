---
kind: record
last-reviewed: 2026-11-24
covers: docs/how-tos.md
reviewed-at: fc9b9d4, with the uncommitted change of the lifecycle map session
---

# Instruction review: docs/how-tos.md

This records the instruction review of the how-to index row that routes to the new lifecycle map, for its author and for critics.

**In short:** 1 finding: 1 trigger, not blocking. The row's Task cell names stages only, so a question about a topic the map's second table covers, such as dependency updates, does not match it.

## Scope

In scope: the one added row in "Starting a task", for the lifecycle map, read against the rest of the page, its "How to read the tables" and its Rules. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/extend-the-workspace.md`, and `docs/lifecycle-map.md` in full, which its own record covers. Ran `git diff --cached -- docs/how-tos.md` and `python3 ws.py check`, which reported nothing on this page.

The page has no `## References` heading.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | Starting a task, the lifecycle map row | Not blocking. The Task cell reads "See which stages of delivery the workspace guides, from a request to operations, and which have no page yet". The map has a second table, "Across every stage", for security, dependency updates, schema and data changes, unattended work and keeping the guidance true, and its **In short** line sends a reader to "your topic in the second". A reader asking whether the workspace covers dependency updates or threat modeling finds no stage word to match. "From a request to operations" also stops one stage short of the map's last, Learn. Verified: the Task cell against the map's tables and **In short** line. Inferred: that a topic question misses the row. | fixed: the Task cell names the topics across stages and no longer stops at operations. |

## Checked with no finding

- contradiction: the Proof cell, `reference`, matches the map's `kind: reference`, and the section's intro says a reference page carries no proof state. The Remember cell restates the map's second rule, and each stage with no page, Release and Operate, names a milestone or a reason (verified, reading). The map's own record covers how its Operate row marks that state.
- step: the row adds no step. Its link resolves; the `links` check reported nothing.
- enforcement: the page's first rule holds for this change: a reference page a reader goes to for a task gets its row in the same commit as the page (verified, `git diff --cached`). The second holds: the row is not a playbook.
- placement: the row routes only, in the table beside reading paths by role, the other page for a reader finding their way in. It restates none of the map's tables.
- eval-case: the page is a reference. No eval case or arm in `evals/arms.json` reads it, and the row routes to a reference page, which carries no proof state.
