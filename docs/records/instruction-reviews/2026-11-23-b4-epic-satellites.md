---
kind: record
last-reviewed: 2026-11-23
covers: docs/templates/epic-satellites.md
reviewed-at: 1a18d68, with the uncommitted change of the B4 slice session
---

# Instruction review: docs/templates/epic-satellites.md

This records the instruction review of slice B4's new epic satellites template, a product lane draft, for the change's author.

**In short:** 4 findings, none blocking: 1 contradiction, 1 step, 1 trigger, 1 placement. The page forbids an agent to send a question even when the owner asks, with no label as an exception to procedure endings. Nothing routes a hub writer here. "Links this row" has no anchor to link. The page restates orchestration's limits.

## Scope

In scope: the whole page, which is new and untracked. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/extend-the-workspace.md`, and the pages it links to: `docs/templates/epic-folder.md`, `docs/templates/hand-off-plan.md`, `docs/playbooks/tracker-operations.md` and `docs/orchestration.md`'s "Limits". Also read `parts/page_kinds.py`'s folder rule and the case `page_kinds#a page in a kind's folder must be of that kind` in `parts/page_kinds.cases.json`. The page gives no command to run. Ran `grep` for inbound links to the page, and `python3 ws.py check`, which reports nothing on this page.

The page has no `## References` heading.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Questions for other teams; Rules, the second row | Not blocking. The page says "Only the epic's owner sends a question. An agent drafts it and never sends it, on any channel." Procedure endings' "Outward writes" lets an agent make a write on another system when the request names it in its own words. So when the owner asks "send question 1 to the payments team", the two pages disagree, and this page does not label its rule as an exception to that one. Verified: the two texts. | fixed: an agent drafts a question and sends it only when the epic's owner asks in their own words, linking procedure endings' outward writes; the Rules row matches |
| 2 | trigger | The whole page; the epic folder template | Not blocking. Nothing sends a hub writer here. The [epic folder template](../../templates/epic-folder.md), which a person or agent follows to write a hub, neither links this page nor shows the two new sections in its skeleton. So a hub written from it never gains them. This is a route in, not an index row, so the batch 2 note does not cover it. Verified: `grep` finds `epic-satellites` only in this page and the M3 plan. | fixed: the slice session added a paragraph to the epic folder template, after its open questions, that names the three satellites and links this page. That edit has its own review record. |
| 3 | step | Questions for other teams | Not blocking. "When an answer here settles an open question, that row's answer links this row." A Markdown table row has no anchor, so there is no target for the link. The page does not say what to write instead, such as the section's anchor and the row's number. Inferred: from Markdown's heading-only anchors and the style guide's "a section by its heading's anchor". | fixed: the settled question's answer now links this section's anchor and names the row's number, with an example |
| 4 | placement | Unattended-run plan, the Non-goals and Limits row | Not blocking. The row links orchestration's limits and also restates them: "three rounds, then freeze and report, with nothing published or merged". [Orchestration](../../orchestration.md#limits) owns that rule, and the style guide's "One rule, one page" counts a restated rule as a finding. Verified: the row and orchestration's "Limits". | fixed: the row now links orchestration's limits without restating them |

## Checked with no finding

- enforcement: the first Rules row's tag, `page_kinds#a page in a kind's folder must be of that kind`, exists. `parts/page_kinds.py` matches a page by `startswith(folder + "/")`, so it covers a page nested in `docs/plans/<epic-slug>/`. The other rows are `prose`, and each must and never on the page has a row.
- eval-case: the page is a template, which carries no proof keys under decision 0006. Its lane-draft line names M9 as its first use on real work.

## Re-check

A fresh session read the page as it stands on `4190d8d`, uncommitted, beside procedure endings, the epic folder template's uncommitted change, the hand-off plan template and orchestration's "Limits".

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | "Questions for other teams" says an agent sends a question only when the epic's owner asks in their own words, linking procedure endings' outward writes, and the second Rules row matches. Procedure endings lets a request that names the write in its own words be its yes, so the two now agree. Verified: both texts. |
| 2 | upheld | `git diff -- docs/templates/epic-folder.md` shows one added paragraph after the open questions note, naming the three satellites and linking `epic-satellites.md`. Verified. |
| 3 | upheld | The settled question's answer now links the section's anchor and names the row's number, such as `[question 1](#questions-for-other-teams)`. The hub holds both sections, so the anchor resolves on the same page. Verified: the text. Inferred: that the hub keeps the heading as the skeleton writes it. |
| 4 | upheld | The Non-goals and Limits row links orchestration's limits without restating them. `## Limits` exists in `docs/orchestration.md`. Verified. |

What a fix broke:

- none.

What the first reading missed:

- none.
