---
kind: record
last-reviewed: 2026-11-24
covers: docs/size-the-work.md
reviewed-at: fca7d9b, with the uncommitted change of the slice Z builder
---

# Instruction review: docs/size-the-work.md

This records the instruction review of slice Z's change to the size gate's page, for its author and its readers.

**In short:** 1 finding, 1 of them blocking: 1 contradiction. The blocking one: the "Failure modes" table still sends all work that passes the gate to fix a bug, against the page's new routing and the contract.

## Scope

In scope: the whole page, with most attention to the diff from d2aa593: the In short line and the "Passes the gate" row of "When to write a spec", which now send a small refactor to safe refactor and a small change to pages only to extend the workspace, as the contract routes them. Read beside it: `AGENTS.md` and `CLAUDE.md` with their uncommitted change, `INDEX.md`, `docs/playbooks/fix-a-bug.md`, `docs/definition-of-done.md`, `docs/safe-refactor.md`, `docs/extend-the-workspace.md`, `docs/procedure-endings.md`, `docs/changing-the-machinery.md` ("The path for a machinery change"), the playbook catalog's routing paragraph, the new request map's rows for a bug, a refactor and a page, and this batch's record for safe refactor. `python3 ws.py check` reports no finding on this page; its only errors are the three `eval_record` errors on fix a bug that slice Z expects until its eval run is on record.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | The spec process, "Failure modes" table, the "Ceremony" row | Blocking. The row's remedy for "a spec for work that passes the gate" is "Go to fix a bug." The changed In short line and the changed "Passes the gate" row now say such work goes to fix a bug, or to safe refactor or extend the workspace as the contract routes it. The contract's "How work flows", with its uncommitted change, sends a small refactor to safe refactor and a small change to pages only to extend the workspace. An agent that started a spec for a small refactor or a page fix, and follows this row, goes to fix a bug, which is a step that contradicts the contract. The fix that updated the In short line and the spec table, after this batch's safe refactor review, left this third copy of the old routing. Verified: the three places on the page, and `AGENTS.md`, "How work flows". Inferred: that an agent reaches this row with such work. | fixed: the Ceremony row now routes as the contract does, like the In short line and the spec table |

## Checked with no finding

- step: every link and anchor on the page resolves (`python3 ws.py check` reports none on it). The changed spec-table row names safe refactor and extend the workspace without links, but the In short line links both, and "the contract" is the always-loaded `AGENTS.md`. Verified.
- trigger: the In short line now matches the contract, the playbook catalog's paragraph, safe refactor's step 2, extend the workspace's step 1 and the request map's "Refactor this" and "fix this page" rows. A small machinery change is not listed among its routes, but changing the machinery sets a commit path (a branch and a failing case first), which fix a bug's step 5 reaches through procedure endings; it does not replace fix a bug. Verified for the texts; inferred for how an agent combines them.
- enforcement: the changed text adds no must or never. The gate's rule keeps its `prose` row. Verified.
- placement: the routing is stated in the contract and repeated here as the gate's outcome, where a reader sizing work needs it; no rule procedure endings states is restated in the changed text. Verified.
- eval-case: the page is `proof: unproven` with `prove-by: M9`, so its behavior needs no case yet. Verified: front matter.

## Re-check

A fresh session re-read the page on 2026-11-24, after the fix round, at 9a28eda. It read the page, `git diff d2aa593` of it and the contract's "How work flows", and ran `python3 ws.py check`, whose only errors are fix a bug's three pending eval runs.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | The Ceremony row now says "Go to fix a bug, or to safe refactor or extend the workspace as the contract routes it", in the same words as the spec table's "Passes the gate" row, and the In short line links all three pages. The contract sends a small refactor to safe refactor and a small change to pages only to extend the workspace. No other place on the page sends work that passes the gate to fix a bug alone. Verified: the page and `AGENTS.md`. |

Broke: none.

Missed: none.
