---
kind: record
last-reviewed: 2026-11-24
covers: docs/safe-refactor.md
reviewed-at: d2aa593, with the uncommitted change of the slice Z builder
---

# Instruction review: docs/safe-refactor.md

This records the instruction review of slice Z's change to safe refactor, for its author and its readers.

**In short:** 2 findings, none blocking: 1 contradiction, 1 placement.

## Scope

In scope: the whole page, with most attention to the diff from d2aa593, which rewrites step 2's routing sentence: the contract now routes a small refactor here, where the page used to call this an exception to the contract. Read beside it: `AGENTS.md` and `CLAUDE.md` with their uncommitted change, `INDEX.md`, `docs/size-the-work.md`, `docs/definition-of-done.md` with its change, `docs/playbooks/fix-a-bug.md`, `docs/playbooks/test-first.md`, `docs/parts.md`, `docs/procedure-endings.md`, `docs/templates/fix-record.md`, `docs/records/defects.md`, the playbook catalog's routing paragraph, the how-to index's row and the new request map. Every link and anchor on the page resolves, `tools/symbols.py` exists, and the `shelved` case the rules table names exists in `parts/shelved.cases.json`.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Steps, step 2 | Not blocking. Step 2 no longer labels its route as an exception, and the contract, with its uncommitted change, does route a small refactor here. Two loaded pages still say otherwise. The size gate's page says a change that passes the gate goes to fix a bug, in its In short line and in "When to write a spec" ("Passes the gate: No. Go to fix a bug."). The playbook catalog says "Two pages state an exception: safe refactor for a small refactor, and extend the workspace", but this page no longer states one. An agent reading the size gate alone still sends a small refactor to fix a bug. Verified: `docs/size-the-work.md`, In short and "When to write a spec"; `docs/playbooks/README.md`, its routing paragraph; `AGENTS.md`, "How work flows". | fixed: the size gate's In short line and its spec table, and the playbook catalog's routing paragraph, now route a small refactor and a small page change as the contract does |
| 2 | placement | Steps, step 7 | Not blocking. Step 7 states its own reading of the definition of done: "a refactor fixes nothing, so the test that came first is the characterization test, which passed before the change and still passes after it". The definition of done's first row now states the same, nearly word for word. Two copies can drift; step 7 can link the row. Verified: `docs/definition-of-done.md`, the first row of "The list". | fixed: step 7 now points to the definition of done's first row instead of restating it |

## Checked with no finding

- step: each step names its input, action, output and a default; the stop condition and the early stop are stated. Step 3's pointer to test first's step 2 matches that step (the test command, and stop when there is no harness). Step 7's "Report as that page says" meets the definition of done's new row on where a report is kept, which names no place for a refactor; that gap is recorded in the definition of done's own record, 2026-11-24-z-definition-of-done.md, finding 1.
- trigger: the purpose sentence, the In short line, the contract's new routing line, the how-to index's row, INDEX.md's topic row and the request map's "Refactor this" row all send a refactor here, and step 1 sends a behavior change away.
- enforcement: each must and never on the page has a row; the `shelved` tag's case shows an edit in `src/orders-service-v1` refused. The other rows are `prose`, as tagged.
- eval-case: the page is `proof: unproven` with `prove-by: M4`, so its behavior needs no case yet.

## Re-check

A fresh session at the driver tier read safe refactor on 2026-11-24 as it stands on fca7d9b with the slice Z builder's uncommitted change, with `git diff d2aa593 --` this page, the size gate's page and the playbook catalog, and the contract, the definition of done and the two wrappers.

| # | Verdict | Evidence |
|---|---|---|
| 1 | The fix holds. | Verified: the size gate's In short line and its "Passes the gate" row route a small refactor and a small change to pages only as the contract does. The catalog's routing paragraph says "The contract routes two kinds elsewhere", and no page under `docs/` still calls either route an exception to the contract (search). The fix-a-bug wrapper sends a refactor to safe refactor. |
| 2 | The fix holds. | Verified: step 7 points to the definition of done's first row, which says the test that came first for a refactor is a characterization test. The definition of done's report row now gives a refactor's report a place, the final reply, which closes the gap this record's "Checked with no finding" named. |

What the fixes broke: fix 1 left the size gate's "Failure modes" table with a "Ceremony" row that still said "Go to fix a bug" for work that passes the gate. The size gate's own review (2026-11-24-z-size-the-work.md, finding 1) marked it blocking. A later fix changed the row before this re-check read it: it now says "or to safe refactor or extend the workspace as the contract routes it" (verified, `git diff d2aa593 -- docs/size-the-work.md`). Not blocking now. The catalog's "Fix a bug" row, which still fired on a small refactor, was also changed and now names both other routes (verified); its record is 2026-11-24-z-playbooks-readme.md.

What the first reading missed: nothing found, blocking or not.
