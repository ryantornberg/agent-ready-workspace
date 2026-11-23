---
kind: record
last-reviewed: 2026-11-23
covers: docs/triage-labels.md
reviewed-at: 1a18d68, with the uncommitted change of the B4 slice session
---

# Instruction review: docs/triage-labels.md

This records the instruction review of slice B4's new bug triage labels page, a product lane reference draft, for the change's author.

**In short:** 4 findings: 1 contradiction, 1 step, 1 trigger, 1 placement; none blocking. The bug report template gives labels to triage, while this page has the filer set them. Adding an area routes a guidance-page change through procedure endings alone. The bundling rule can drop `kind:security`. One grooming rule is restated instead of linked.

## Scope

In scope: the whole page, which is new and untracked. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/extend-the-workspace.md`, and the pages it links: `docs/predecessor-check.md`, `docs/playbooks/bug-grooming.md`, `docs/playbooks/bug-triage-meeting.md`, `docs/templates/bug-ticket.md` and `docs/playbooks/tracker-operations.md`. Also read the files under `src/` and the `review_trailer` entry in `workspace.json`. Ran `python3 tools/symbols.py` for `AccountFreeze` and `ReconciliationWorker` (both found under `src/orders-api/`), `grep` for links to this page (bug grooming, the triage meeting and the predecessor check link it), and `python3 ws.py check`, which reports nothing on this page.

The page has no `## References` heading. Missing catalog and index rows are out of scope for batch 2.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Who sets them | Not blocking. This page says "Whoever files the bug, person or agent, sets every label when filing". The bug report template, which a filer follows, says "Grooming a bug, and the labels triage adds, belong to the product lane". Its "Before you write" and "Filing it" set no label and never link this page. A filer following the template sets none, so every new bug reaches the triage meeting unlabelled, and the predecessor check's default, read from labels, never fires. Verified: the template's "When to use it", "Before you write" and "Filing it", and a grep showing the template does not link this page. | fixed: "Who sets them" and the In short line say the filer sets the labels, the template leaves them to triage, and the triage meeting's preparation proposes and sets labels for any bug that arrives without |
| 2 | step | Area | Not blocking. "To use a new area, add its row here first, in a change committed as procedure endings says". This page is a guidance page: `workspace.json`'s `review_trailer` entry lists `docs/` and does not except it. A change to it follows extend the workspace, with the size gate and a fresh session's instruction review, which procedure endings' commit only names. The page also gives no default for an agent filing a bug, or proposing labels at triage, when no area fits. Proposing the new area to the person, and leaving the area label as proposed, would settle it. Verified: the `review_trailer` entry and extend the workspace's "What this page covers". Inferred: that an agent mid-filing edits this page and has its commit refused for want of a record. | fixed: adding an area is now a change made as extend the workspace says, with a default to propose the new area and leave the label as proposed; the rules row matches |
| 3 | trigger | Boundary rules, the bundling rule | Not blocking. "A ticket bundling several faults takes its worst one's labels", where worst is "the widest `affects`, then the most common `trigger`". Severity of kind plays no part. A ticket bundling a security fault that affects staff with a functional fault that affects end users takes the functional one's labels and drops `kind:security`. The triage meeting's group 1, "Security and data", and the predecessor check's default for a major security bug then do not fire for it. Verified: the bundling rule, the triage meeting's agenda groups, and the predecessor check's "When it applies". Inferred: that such bundles occur. | fixed: the bundling rule ranks a `kind:security` or `kind:data` fault first, then the widest `affects`, then the most common `trigger` |
| 4 | placement | Boundary rules; Rules, the fourth row | Not blocking. "Grooming removes the `effort` label; a bug never shows two sizes" is a rules row here and on bug grooming, whose step 7 owns the action. The style guide's "One rule, one page" asks for one owner and a link. The boundary rule already links bug grooming, so the rules row restates it. Verified: both rules tables and the style guide. | fixed: the rules row restating grooming's removal of `effort` is gone; the boundary rule links bug grooming |

## Checked with no finding

- enforcement: every must and never on the page has a rules row, each tagged `prose`, which is true: no part checks a tracker's labels.
- eval-case: the page is a reference, which layout gives no `proof` key. The behavior it asks of an agent runs through bug grooming and the triage meeting, both marked `proof: unproven` with `prove-by: M9`, so no eval case is due yet.

## Re-check

A fresh session read the page at `4190d8d`, with the uncommitted change of the B4 slice session, beside the contract, procedure endings, extend the workspace, the bug report template, bug grooming, the triage meeting and the predecessor check.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed in part | Verified: "Who sets them" says the filer sets every label, that the template sets none, and that the triage meeting's preparation proposes labels for a bug that arrives without them; the triage meeting's step 2 does so. That closes the harm the finding named: unlabelled bugs at triage, and, with the predecessor check's finding 3, the predecessor default. Verified: the bug report template is unchanged (`git status` lists no change to it), still says "the labels triage adds" belong to the product lane, and does not link this page. So a filer reading both pages still gets two answers on who sets labels; this page now describes the conflict instead of settling it. Settling it takes a line in the template, which is outside this record's page. Not blocking. |
| 2 | upheld | Verified: "Area" gives the default to propose a new area and leave the label as proposed, and routes adding its row through extend the workspace; the second rules row matches. |
| 3 | upheld | Verified: the bundling rule ranks a `kind:security` or `kind:data` fault first, then the widest `affects`, then the most common `trigger`. |
| 4 | upheld | Verified: the rules row restating grooming's removal of `effort` is gone, and the boundary rule links bug grooming. |

What a fix broke: none.

What the first reading missed: none.

## Known defects

What stays open after the fix rounds the plan allows, each not blocking.

- Not blocking, finding 1 fixed in part: the bug report template still says triage adds the labels, while this page says the filer sets them. Settling it takes a line in the template. Known defect, for M9.
