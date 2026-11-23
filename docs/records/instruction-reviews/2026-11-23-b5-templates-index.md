---
kind: record
last-reviewed: 2026-11-23
covers: docs/templates/README.md
reviewed-at: dace91e, with the uncommitted change of the B5 slice session
---

# Instruction review: docs/templates/README.md

This records the review of B5's edit to the templates index, which moves the decision record's row into this folder's table, for its author.

**In short:** 0 findings. The row now points at the new template, and its condition and destination match that page.

## Scope

In scope, from `git diff HEAD -- docs/templates/README.md`: the row added to "Templates in this folder" for the decision record, and the row removed from "Record shapes another page defines". The whole page was read to judge them. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/templates/decision-record.md`, and decision interview's section "When a decision gets a record".

Run: `python3 ws.py check` passes with only an `eval_record` warning about `fix-a-bug.md`, so both links in the row resolve (verified).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|

No findings.

## Checked with no finding

- contradiction: the row's "Use it when" matches the template's "When to write one", the approved-plan case included, and its destination matches the template's "The file" (verified). Extend the workspace states the condition without the approved-plan case; that is recorded against that page, in `2026-11-23-b5-extend-the-workspace.md`.
- step: the row's destination, `docs/decisions/<NNNN>-<topic>.md` with the next free number, is a path the reader can write; the template gives the skeleton to copy, as this page's **In short** line promises (verified).
- trigger: the row sits in the table of templates in this folder, where the page's **In short** line sends a reader, and no longer in the table for shapes with no page here.
- enforcement: the changed rows state no must or never.
- placement: the old row is removed, so the shape is indexed once.
- eval-case: the page is a reference page with no proof mark, and the change asks no new behavior.
