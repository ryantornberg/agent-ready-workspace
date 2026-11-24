---
kind: record
last-reviewed: 2026-11-24
covers: docs/playbooks/README.md
reviewed-at: fca7d9b, with the uncommitted change of the slice Z builder
---

# Instruction review: docs/playbooks/README.md

This records the instruction review of slice Z's change to the playbook catalog, for its author and its readers.

**In short:** 1 finding, none blocking: 1 trigger.

## Scope

In scope: the whole page, with most attention to the diff from d2aa593 in "Before you pick one", which now says the contract routes a small refactor to safe refactor and a small change to pages only to extend the workspace, where it used to say two pages state an exception. Read beside it: `AGENTS.md` and `CLAUDE.md` with their uncommitted change, `INDEX.md`, `docs/size-the-work.md`, `docs/playbooks/fix-a-bug.md`, `docs/definition-of-done.md`, `docs/safe-refactor.md`, `docs/extend-the-workspace.md`, `docs/procedure-endings.md`, `docs/changing-the-machinery.md`, the how-to index and the new request map. `python3 ws.py check` reports no finding on this page.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | The catalog, the "Fix a bug" row | Not blocking. The row fires on "A change that passes the size gate: small, easy to reverse, in one repository and under a day of work". That also matches a small refactor and a small change to pages only, which the changed paragraph above it, and the contract, route elsewhere. Neither safe refactor nor extend the workspace has a row in this catalog, since both are how-tos, so the page's In short line ("find the row that matches your situation") lands such work on fix a bug. The row's second sentence, "written for a bug whose cause you can pin in a failing test", hints at the limit but does not name where else to go. Verified: the row, the paragraph, the catalog's rows, and `AGENTS.md`, "How work flows". Inferred: that a reader picks from the table without the paragraph. | fixed: the fix a bug row now sends a small refactor to safe refactor and a small change to pages only to extend the workspace |

## Checked with no finding

- contradiction: the changed sentence matches the contract with its uncommitted change, safe refactor's step 2, extend the workspace's step 1 and the size gate's changed In short line. "Two kinds" holds: the contract's machinery line sets a commit path, which a small machinery fix reaches through fix a bug's step 5 and procedure endings, rather than a replacement for fix a bug. Verified for the texts; inferred for how an agent combines them.
- step: every link and anchor in the paragraph resolves. Verified: `python3 ws.py check`.
- enforcement: the changed text adds no must or never, and the rules table is unchanged. Verified.
- placement: the paragraph repeats the contract's routing on the page that picks a procedure, where it belongs, and links procedure endings rather than restating it. Verified.
- eval-case: the change rewords who states the two routes; the routes themselves are the same as before the change, so it asks no new behavior. The page is a reference page with no proof key. Verified: `git diff d2aa593 -- docs/playbooks/README.md`.
