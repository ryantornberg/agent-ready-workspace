---
kind: record
last-reviewed: 2026-11-23
covers: docs/product-reader-pages.md
reviewed-at: 1a18d68, with the uncommitted change of the B4 slice session
---

# Instruction review: docs/product-reader-pages.md

This records the instruction review of slice B4's new reference page on pages for a product reader, a product lane draft, for the change's author.

**In short:** 3 findings: 2 trigger, 1 contradiction; none blocking. The page's own test for which pages it binds does not fire on the triage sheet, its first example, and the QA test plan template never routes a writer here. The QA plan's checkbox on every item meets rule 4's ban on a column filled on every row. The title is not the industry's term for this practice.

## Scope

In scope: the whole page, which is new and untracked. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/extend-the-workspace.md`, the instruction review playbook, and every page the page links to: the style guide, the reader standard, the bug triage meeting playbook, the QA test plan template and procedure endings. Also read the bug report template's opening, which names a product manager among a ticket's readers.

Ran: `python3 ws.py check`, which reports nothing on this page, so its links and anchors resolve and its opening passes `page_kinds`; and `grep -n -i "product reader" INDEX.md`, which finds nothing.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | Which pages these rules bind | Not blocking. The test is "A page is for a product reader when its purpose sentence names a non-developer as its reader." The triage sheet, the first example, has no purpose sentence: the bug triage meeting's step 3 lists its rows and groups and gives it none. So the test does not fire on it; the sheet is bound only because the triage page says so. The second example, a QA test plan copy, is bound, but the QA test plan template neither links this page nor says its copies follow it. A writer following the template never reaches these rules. Verified by reading the triage page's step 3 and the whole QA test plan template. | fixed: the test now also binds a page whose procedure or template says so, which covers the triage sheet; the QA test plan template's link to this page is a batch 1 edit this round may not make, reported to the slice session |
| 2 | contradiction | The rules, rule 4 | Not blocking. Rule 4 says the page "never asks the reader to fill in a column on every row", with one exception for a column a meeting fills in together. The QA test plan template, named here as a bound page, gives every scenario item a `- [ ]` checkbox the tester ticks, and its Sign-off asks the tester to fill each field. Neither page labels that as an exception. Verified by reading the QA template's skeleton. Inferred: that a checkbox on every item counts as a column on every row. | fixed: rule 4 and its Rules row now say a tester's checklist, such as the QA test plan's scenarios and sign-off, is not a column to fill in |
| 3 | trigger | Title | Not blocking. The reader standard asks for the industry's standard term in a title where one exists. Writing for a non-specialist reader, with plain words, explained terms and color never carrying meaning alone, is usually called plain language. A writer looking for that guidance under its usual name does not find "Pages for a product reader". Inferred: that "plain language" is the standard term; no source was opened. | declined: the title and path are already named in committed batch 1 index rows (`docs/how-tos.md`, `docs/reading-paths.md`), which this round may not edit; and "plain language" is the style guide's subject for every page, while these four rules add to it for one reader, so that title would overclaim |

## Checked with no finding

- step: the page is a reference page and gives no steps to run. Its "Where a page goes" links procedure endings' commit and outward writes, and both anchors resolve.
- enforcement: each of the five rules in the body has a row in the Rules table, tagged `prose`; no tag claims a part.
- placement: the page states its own four rules and links the style guide, the reader standard and procedure endings for theirs. Rule 3 is stricter than the style guide's "explain each term", and the **In short** line labels the page as adding to it.
- eval-case: the page is a lane reference page, which carries no proof keys; it states that M9 first uses it on real work.

## Re-check

A fresh session read the page as it stands on `4190d8d`, uncommitted, beside the QA test plan template's uncommitted change, the bug triage meeting playbook and the reader standard.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | The test now also binds a page whose procedure or template says so. The bug triage meeting's step 3 says the sheet is a page for a product reader, and `git diff -- docs/templates/qa-test-plan.md` shows the added link under "Filling it in": "A copy is a page for a product reader". Verified. |
| 2 | upheld | Rule 4 and its Rules row say a tester's checklist, such as the QA test plan's scenarios and sign-off, is not a column to fill in. Verified: the texts. |
| 3 | upheld | The decline's second reason holds: the style guide asks for plain words on every page, and this page adds four rules for one reader, so "plain language" would name the whole style guide's subject. Its first reason is wrong: `git show HEAD:docs/how-tos.md` and `git show HEAD:docs/reading-paths.md` hold no link to this page; the rows naming it are uncommitted edits under their own review. Verified: both commands. Inferred: that no narrower industry term fits these four rules. |

What a fix broke:

- none.

What the first reading missed:

- none.
