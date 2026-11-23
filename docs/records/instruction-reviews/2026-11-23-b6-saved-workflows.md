---
kind: record
last-reviewed: 2026-11-23
covers: docs/saved-workflows.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: docs/saved-workflows.md

This records the review of B6's edit to the saved workflows page's row on wrappers, for its author and the automation lane's readers.

**In short:** no findings. The row now says that core procedures have wrappers and lane drafts, this page included, have none, which the check holds.

## Scope

In scope: in "What exists today and what is planned", the row "A wrapper that starts a playbook". The whole page was read, with `git diff --cached -- docs/saved-workflows.md` for the change. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/README.md` ("Three ways to follow a playbook" and its rules), `workspace.json` (the `wrappers` entry), `parts/wrappers.py` and its cases, and the wrappers under `plugin/skills/`.

Run, on macOS: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` reports `wrappers: 17 of 17 cases` (verified).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|

No findings.

## Checked with no finding

- contradiction: the page carries `lane: automation` (verified), and no wrapper names `docs/saved-workflows.md` (verified, by listing every wrapper's body path). "This page included" is true. The row's label still says "starts a playbook" while its cell covers how-tos too. The cell is the claim, and it is right.
- step: the row asks for no action, and the page's steps name no wrapper. Its link to the catalog section resolves (verified, the `links` check passes).
- trigger: the page's purpose and **In short** lines are unchanged. The page has no wrapper, as a lane draft, and its how-to index row stays its route in.
- enforcement: the row states facts the `wrappers` check holds (`wrappers#a lane draft with a wrapper fails`; verified, by name in `parts/wrappers.cases.json`). It adds no must or never.
- placement: the row links the catalog, which owns the wrappers, instead of restating its rules.
- eval-case: the page is marked unproven, with `prove-by: M10` (verified, reading its front matter).
