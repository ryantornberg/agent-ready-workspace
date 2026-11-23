---
kind: record
last-reviewed: 2026-11-23
covers: docs/playbooks/feature-layer-walk.md
reviewed-at: 1a18d68, with the uncommitted change of the B4 slice session
---

# Instruction review: docs/playbooks/feature-layer-walk.md

This records the instruction review of slice B4's new feature layer walk playbook, a development lane draft, for the change's author.

**In short:** 8 findings: 5 contradiction, 1 step, 1 enforcement, 1 trigger; 1 blocking. "Writes no file, so it commits and pushes nothing" drops the contract's question-log entry. Step 1's tie rule has no tie-break and drops a second type's layers. Accessibility is sent to the worker tier, impact analysis is misdated, and the kit is written as built.

## Scope

In scope: the whole page, which is new and untracked, and its rows in the playbook catalog, the README's proof table and the development reading path. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/extend-the-workspace.md`, and the pages it links: `docs/size-the-work.md`, `docs/playbooks/impact-analysis.md`, `docs/orchestration.md`, `docs/playbooks/test-first.md`, `docs/playbooks/reuse-checklist.md`, `docs/definition-of-done.md` and `docs/decisions/0006-what-proven-means.md`. Also read `docs/playbooks/review-orchestrator.md`'s dimensions, `docs/playbooks/tracker-operations.md`'s stop line, `docs/glossary.md`'s Kit row, `docs/adopt-the-workspace.md`, the M3 plan's C8 row, `docs/reading-paths.md`, and the files under `src/`. Ran `python3 tools/symbols.py` for `AccountFreeze`, `IOrderStore`, `QuarterlyExport` and `ReconciliationWorker` (each found under `src/`), `python3 ws.py rules` (the `shelved#an edit inside the shelved folder` tag is in use), `grep` for links to this page, `ls wslib` (no adopt module), and `python3 ws.py check`, which reports no finding on this page.

The page has no `## References` heading.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Steps, step 5; Rules, first row | Blocking. Step 5 says "End as procedure endings says", then "This walk writes no file, so it commits and pushes nothing", and the first rules row says "The walk writes no code and no file". The contract says a session that had to ask a person something the workspace should have answered adds it to the question log before it finishes. Procedure endings says such a procedure "still commits this entry". An agent that asked, such as which of two types was meant, gets two instructions that cannot both hold, and the page does not label the exception. Tracker operations, by contrast, says "Apart from a question-log entry, nothing on this page commits a file". Verified: the contract's rules table, procedure endings' "The question-log entry", tracker operations' stop line and this page's step 5 and rules. Marked blocking because following the page as written skips a step the contract requires; when in doubt, blocking. | fixed: step 5 now says only "End as procedure endings says" with the report's contents; the In short line and the first rules row say the walk writes no code, without "no file". |
| 2 | step | Steps, step 1 | Not blocking. When two types fit, step 1 takes "the one with more layers". Three of the five types have six layers each (a new API endpoint, a new field end to end, a background job), and the other two have five each. The likeliest pair, a new field served by a new endpoint, is a tie, and no tie-break is given. Verified: the rows of each layer table, counted. The uncommitted effort estimate page, outside this review, runs steps 1 to 4 and copies the same default, so the gap reaches it too. | fixed: step 1's default takes every type that fits, with no tie to break; step 2 prints each type's table in turn. The effort estimate's step 1 still copies the old default; reported to the slice session, which owns that page. |
| 3 | contradiction | The purpose line and the **In short** line; Steps, step 1 | Not blocking. The purpose line says the walk lists "every layer a feature of a known type touches". Step 1 prints one type's table and only names a second type that also fits. A screen that needs a new endpoint fits neither type whole: "A new screen" assumes "endpoints that exist". Taking the screen drops the endpoint's Authorization layer, which the page calls a security fault, and taking the endpoint drops Accessibility. Verified: the purpose line, the types table and step 1. Inferred: that features spanning two types are common. | fixed: by the same change as finding 2, a feature spanning two types gets both tables, so no layer is dropped. |
| 4 | contradiction | The layer lists, A new screen, the Accessibility row | Not blocking. The row's hint is "Worker tier, as its own review pass". Orchestration's tier table puts review at the driver tier, and the review orchestrator says "Every dimension runs at the driver tier, since review is driver work", with "Accessibility and visual" as one of its dimensions. A plan built from this hint runs an accessibility review at the wrong tier. Verified: the three texts. | fixed: the Accessibility row's hint is now driver tier, as the review orchestrator's "Accessibility and visual" dimension. |
| 5 | contradiction | When to use it, and which page wins, the impact analysis bullet | Not blocking. The page says impact analysis "runs once the change exists". Impact analysis's "When it runs" includes "You are writing the slices of a hand-off plan", and its step 1 takes "a change not made yet" from the request or plan. So both pages fire when a plan's slices are being filled, which is this page's own first use, and neither says which wins or how they combine. Verified: both pages' text. | fixed: the impact analysis bullet now says to run both when filling a plan's slices: this walk for the layers added, impact analysis for the existing code the goal reaches. |
| 6 | contradiction | Seeded, not synced; Rules, last row | Not blocking. The page says "The kit copies them once and never updates them", and its last rules row says "the kit never updates them", both as present fact. The glossary's Kit row and adopt the workspace both say the kit is planned in slice C8 of M3, and adopt says "None of these runs yet". The style guide and extend the workspace's step 4 ask that machinery not yet built be named as planned, with its milestone. The sentence is not a step to run. Verified: the glossary row, adopt's text, the M3 plan's C8 row, and `ls wslib`, which holds no adopt module. | fixed: the seeded-lists paragraph and the last rules row name the kit as planned in slice C8 of M3. |
| 7 | enforcement | The layer lists, the Tests row of A new API endpoint, and the Configuration and secrets row of A call to an outside system; Rules | Not blocking. Two nevers sit in the tables: tests are "never delegated apart from the code", and secrets go "never ... in the repository". Neither has a rules row, so neither shows in the rules table or `python3 ws.py rules`. Extend the workspace's step 4 asks for a row for every must and never on a page. Verified: the tables beside the rules table. | fixed: added rules rows for tests never delegated apart from their code, and for never putting a secret in the repository. |
| 8 | trigger | When to use it, and which page wins; the feature ladder | Not blocking. The page's own use is "to fill a plan's slices", which is step 2 of the feature ladder, but nothing on the feature ladder or the hand-off plan template names this page. Its only links in are the catalog row, the README's proof table, the development reading path and the uncommitted effort estimate page. Extend the workspace's step 5 asks for one sentence on the page a reader is on when they need this one. An agent climbing the feature ladder does not meet it. Verified: `grep -rn feature-layer-walk` across the repository. | known defect, for M9: the feature ladder's step 2 in `docs/size-the-work.md` gains one sentence naming the feature layer walk for filling a plan's slices. That page is outside this slice; the re-check rejected the first disposition, a decline. |

## Checked with no finding

- step (beyond finding 2): every link resolves (`python3 ws.py check` reports none on this page); the feature ladder's step 3 is the outside-world check the screen table names; `IOrderStore`, `AccountFreeze`, `QuarterlyExport` and `ReconciliationWorker` exist under `src/`; extend the workspace's step 5 queues an `INDEX.md` change as the Search aliases row says; steps 1 to 5 each name an input and an output, and the page has a stop line.
- placement: step 5 links procedure endings and the definition of done instead of restating them; step 3 links the reuse checklist instead of restating its steps; the shelved-folder line restates the contract's fact in one sentence where the path hints need it.
- eval-case: the page is marked `proof: unproven` with `prove-by: M9`, which is not in `building` (`['M3']`), so its new behavior needs no eval case yet; its README row says the same.

## Re-check

A fresh session's reading after the fix round, on `1a18d68` with the uncommitted fix of the B4 slice session. It read the page in full, the contract, procedure endings, every page the changed text links to, and ran `python3 ws.py check`, which reports nothing on this page.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | Verified: step 5 now reads "End as procedure endings says" and gives the report's contents, with no "commits and pushes nothing". The **In short** line says "it writes no code", and the first rules row "The walk writes no code; it prints a checklist." Procedure endings' "The commit" and "The question-log entry" then govern a log row, so nothing on the page contradicts the contract. |
| 2 | upheld | Verified: step 1's default takes "each one that fits", and step 2 prints "each type's table ... one after the other", so there is no tie to break. The effort estimate's copy of the old default is outside this re-check. |
| 3 | upheld | Verified: by the same text, a screen with a new endpoint prints both tables, keeping Authorization and Accessibility. |
| 4 | upheld | Verified: the Accessibility hint reads "Driver tier, as the 'Accessibility and visual' dimension". The review orchestrator's "The dimensions" says every dimension runs at the driver tier and lists that dimension; the link resolves. |
| 5 | upheld | Verified: the bullet says to run both when filling a plan's slices. Impact analysis's "When it runs" lists writing a plan's slices, so the two compose. |
| 6 | upheld | Verified: "The kit, planned in slice C8 of M3, is to copy them once", and the last rules row names it as planned. The glossary's Kit row and adopt the workspace say the same. |
| 7 | upheld | Verified: two rules rows added, for tests never delegated apart from their code and for no secret in the repository, each tagged `prose`. |
| 8 | rejected | Not blocking. The decline's reason agrees with the finding and moves its fix to another page. That is a queue, not a decline: the fitting form is `queued for docs/size-the-work.md, the feature ladder's step 2`. Verified: outside records, only `README.md`, `docs/reading-paths.md`, the playbook catalog and the effort estimate link this page; `git status` shows `docs/size-the-work.md` and the hand-off plan template unchanged. As declined, the finding leaves the index, whose row for this page lists no `trigger`. |

What a fix broke:

- None. Verified: the page read in full after the fixes.

What the first reading missed:

- None.

## Known defects

What stays open after the one fix round the plan allows, each not blocking.

- Not blocking, finding 8: the feature ladder does not name this page. Known defect, for M9, as its Disposition says.
