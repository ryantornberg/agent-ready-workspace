---
kind: record
last-reviewed: 2026-11-23
covers: docs/templates/epic-folder.md
reviewed-at: 4190d8d, with the uncommitted change of the B4 slice session
---

# Instruction review: docs/templates/epic-folder.md

This records the instruction review of slice B4's edit to the epic folder template, for its author and for critics.

**In short:** 3 findings: 2 contradiction, 1 trigger; none blocking. The new line puts all three satellites "beside the hub", where two are sections of it. The page's naming table does not allow the unattended-run plan's file name. "A product epic" narrows a template meant for any epic folder.

## Scope

In scope: the uncommitted edit, one paragraph at the end of "Filling it in" that points to the epic satellites template. Also in scope: how that paragraph fits the rest of the page, its "Where it lives and how it is named" table, the hub skeleton and its Rules.

Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/extend-the-workspace.md`, and the epic satellites template in full, with the hand-off plan template it names. Ran `git diff -- docs/templates/epic-folder.md`, `grep -rn "product epic" docs` outside records, and `python3 ws.py check`, which reports nothing on this page.

The page has no `## References` heading.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Filling it in, the last paragraph | Not blocking. "A product epic may also need questions for other teams, a tracker map or an unattended-run plan beside the hub." The satellites template's "Where each one lives" puts the first two in the hub, as sections of `README.md`; only the run plan is a file beside it. This page's own rule says every page in the folder but the hub is a plan, so a questions page beside the hub would be refused by the `page_kinds` check. The next sentence sends the reader to the satellites page, where the place is right. Verified: the paragraph, the satellites table, and this page's Rules. | fixed: the line now puts questions for other teams and the tracker map in the hub, as sections, and the unattended-run plan beside it, as a plan. |
| 2 | contradiction | "Where it lives and how it is named", the first table; Filling it in, the last paragraph | Not blocking. The table lists two kinds of page in the folder: the hub, and "A plan for one story", named `<ticket-key>-<story-slug>.md` or `<story-slug>.md`. The new paragraph brings in the unattended-run plan, which the satellites template names `unattended-run-<YYYY-MM-DD>.md` and which serves no one story. The table does not list it, and nothing labels it as an exception. A reader who names files from this table cannot place the run plan. Verified: the table and the satellites template's "Where each one lives". | fixed: the naming table gains a row for the unattended-run plan, labelled as serving the epic rather than one story, with the satellites template's file name and kind `plan`. |
| 3 | trigger | Filling it in, the last paragraph | Not blocking. The paragraph opens "A product epic". The epic satellites template serves "whoever keeps an epic folder", and this template covers every epic, with no lane. "Product epic" is used nowhere else in `docs/`. A development team's epic that must ask another team a question reads the line as not its own. Verified: `grep -rn "product epic" docs` finds only this line; the satellites template's purpose line. Inferred: that such a reader skips the link. | fixed: the line opens "An epic", so it reads as every epic folder's. |

## Checked with no finding

- step: the change adds no step. The link resolves; the `links` check reported nothing on this page.
- enforcement: the paragraph adds no must or never. The Rules row that every page but the hub is a plan stays true of the satellites, as the run plan is a plan. Verified: the satellites template's `page_kinds` row.
- placement: the paragraph points to the satellites page and restates none of its shapes. It sits after the line that sends workspace questions to the question log, which is where a reader choosing where a question goes looks next.
- eval-case: a template carries no proof keys. No eval case or arm in `evals/arms.json` reads this page, and the paragraph asks no new behavior beyond opening the linked page.

## Re-check

A fresh session read the fix round's `git diff -- docs/templates/epic-folder.md`, the whole page as it now stands, and the epic satellites template in full, with its "Where each one lives" table, **In short** line and Rules. It also ran `grep -rn "beside.*hub" docs` outside records and `python3 ws.py check`, which exited 0 with only the known `eval_record` warning on `fix-a-bug.md`. Verified: the check passed, so the new link resolves and the page's review date is not stale. Verified: the naming table keeps three columns on every row. Side note, not created by this round: the satellites template's own purpose line still says all three shapes "sit beside an epic's hub", against its own table; reading paths' product item 6 repeats it. Both sit outside this record.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | Verified: "Filling it in", the last paragraph, now puts questions for other teams and the tracker map in the hub as sections and the unattended-run plan beside it as a plan. That matches the satellites template's "Where each one lives" table and its first Rules row, and this page's rule that every page but the hub is a plan. |
| 2 | upheld | Verified: "Where it lives and how it is named" gains a row, "An unattended-run plan, which serves the epic rather than one story", with `docs/plans/<epic-slug>/unattended-run-<YYYY-MM-DD>.md` and kind `plan`, a copy of the hand-off plan template. That is the satellites table's path and kind word for word. The row labels the exception, and it stays true to "Filling it in" step 3, since "Docs here" lists every plan in the folder, as the satellites template says the run plan is listed. |
| 3 | upheld | Verified: the paragraph opens "An epic". The trailing "a product lane draft" describes the linked page, not which epics it serves. Inferred: a development team's reader now takes the line as its own. |

What a fix broke:

- None.
