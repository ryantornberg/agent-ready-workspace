---
kind: record
last-reviewed: 2026-11-22
covers: docs/playbooks/search-every-source.md
reviewed-at: 31f9aaa, with the uncommitted change of the B2 builder
---

# Instruction review: docs/playbooks/search-every-source.md

This records the instruction review of the new search every source playbook, for its author and for agents asked to search beyond the workspace.

**In short:** 3 findings: 2 contradiction, 1 step.

## Scope

The whole page, which is new in batch 4. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md`, the linked pages research ladder, size the work, changing the machinery, extend the workspace, tracker operations, git-host operations and the question log, and the other batch 4 pages and edits, with the playbook catalog's new "Any stage" rows. Ran `gh auth status` (signed in), `gh issue list --help` and `gh pr list --help` (both take `--search` and `--state all`), `python3 ws.py rules` (the page's rows are listed; `handoff_tier#no tier named` and `eval:fix-a-bug` are tags in use), and read `wslib/events.py` (`CODEX_REFUSED` refuses Codex's `spawn_agent` at before-handoff, so step 3's Codex note holds).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | "In short", step 5 and "Rules" | The In short line says "Nothing is written; the report is the output", and the first rules row says nothing is written on the pages the procedure reads, "no page, record, comment or message". Step 5 then sends a finding through the research ladder's offer, which writes a page on a yes, and a later rules row says "A page is updated only on the person's yes". The page-write path is not labelled as an exception to the read-only rule, so an agent must pick one. Verified by reading the page and the research ladder's "Offer to write a finding down". Cause: sheet-read-only-vs-offer — the sheet's section 3 makes this page read-only with no exception, while its section 2 routes every page's keepable finding through an offer that writes on a yes. | fixed: In short, step 5 and the first rules row now say the search writes nothing and a page changes only afterward, through the offer, on a yes. |
| 2 | contradiction | "When to use it", the paragraph on tracker operations | This page sends "a request to read or change a named work item, such as 'what is the status of this ticket'" to tracker operations. Tracker operations' "When to use it, and which page wins" sends a question whose answer may sit on the tracker and other sources back here, and says it wins only "once the person names an item to change". A question about a named item's state that also needs other sources, such as chat, is sent by each page to the other. Verified by reading both tables. Cause: sheet-silent-on-tie-break — the sheet's section 9 sets no tie-break between search every source and tracker operations, so each builder drew its own boundary. | fixed: "When to use it" now uses tracker operations' boundary: a named item goes there first, then this page searches the other sources. |
| 3 | step | "When to use it" and step 2 | The page fires on a request to "search further" after the ladder came back empty, and on a request for "every source" (the mail and chat paragraph). Neither names a source. Step 2's default lists "only the sources the request names", so such a request gives an empty list, and step 2's only exit, "If none is reachable, go to step 5", does not cover a list that was never filled. The agent cannot tell whether "every source" means every row of the search notes. Verified by reading; that an agent would stall or guess is inferred. Cause: branch-end-pass-skipped — the brief's step pass asks every decision for a default that covers each branch, and this default does not cover the triggers the page itself admits. | fixed: a request naming no source now means every search-notes source except mail and chat, and step 2 exits on an empty list. |

## Checked with no finding

- enforcement: every must and never on the page has a rules row; the tier row carries `handoff_tier#no tier named`, which `python3 ws.py rules` lists, and the report row carries `eval:fix-a-bug` as the sheet and the contract give it.
- trigger: the purpose line, In short and the catalog's "Any stage" row agree with the sheet's ladder tie-break; git-host operations' row for searching pull requests points here with the same "writes nothing" sense; the research ladder routes in with the condition named.
- placement: the per-source facts sit in the search notes table, not in the steps; the helper brief is a table each prompt carries.
- eval-case: the page is `proof: unproven`, `prove-by: M8`, so its new behavior needs no case yet. The tracker provider is named as planned for M8, with a by-hand path until then.

## Re-check

A fresh session re-read the page on 2026-11-22, after the fix round.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | In short, step 5 and the first rules row now all say the search writes nothing and a page changes only afterward, through the offer, on a yes; verified by reading. |
| 2 | fixed | "When to use it" sends a named item to tracker operations first, then this page, which agrees with tracker operations' last routing row; verified by reading both tables. |
| 3 | fixed | "When to use it" and step 2 now default a request naming no source to every search-notes source except mail and chat, and step 2 exits on an empty list; verified by reading. |

Broke:
- "When to use it", the new item-then-search sentence: running tracker operations to read the item lets its housekeeping writes fire without asking (a missing development sub-task, "an item they asked about counts as named"), so a search this page says writes nothing can write on the tracker. Inferred, from reading tracker operations' "Which writes need a yes" and "The operations".

Missed:
- Step 5 and the closing paragraph: "Nothing was written, so nothing is committed" sits beside the contract's question-log write; the page never says how that entry is committed, while the docs audit says to commit it staged by name. Verified by reading both pages.

## Batch 5's fix round

The builder's one fix round on the re-check's items, on 2026-11-22. A fix that touched a rule several pages share changed every page holding it: how a question-log entry is committed now lives on [the question log](../../question-log.md) and the other pages link it; who pushes follows [changing the machinery](../../changing-the-machinery.md#the-path-for-a-machinery-change).

| Item | Disposition |
|---|---|
| Broke: reading an item through tracker operations lets its writes fire | fixed: "When to use it" reads the item as tracker operations' steps 1 and 2 say, and makes none of its writes. |
| Missed: no commit path for the question-log entry | fixed: step 5 and the closing paragraph commit it as the log's page says; the In short line and the first rules row now carve it out; a rules row holds it. |

## Second re-check

A fresh session re-read the page on 2026-11-22, after batch 5's fix round.

| Item | Verdict | Evidence |
|---|---|---|
| Broke: reading an item through tracker operations lets its writes fire | fixed | "When to use it" now reads the item only as tracker operations' steps 1 and 2 say and makes none of its writes, and those two steps hold no write; verified by reading both pages. |
| Missed: no commit path for the question-log entry | fixed | Step 5, the closing paragraph and a new rules row commit the entry as the log's page says, and the In short line and the first rules row now carve it out; verified by reading the page and the question log's "Adding an entry". |

Broke:
- "When to use it", the steps-1-and-2 sentence: tracker operations' step 2 sends a missing answer to its step 7, which stops, so an unread item ends the run before this page searches, and this page gives no default; inferred, from reading both pages.

Missed:
- The purpose line ("without writing anything") and the report shape's "Written: nothing" line leave no place for the question-log entry step 5 now commits; verified by reading the page.
