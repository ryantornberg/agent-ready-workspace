---
kind: record
last-reviewed: 2026-11-23
covers: docs/templates/regression-candidates.md
reviewed-at: 1a18d68, with the uncommitted change of the B4 slice session
---

# Instruction review: docs/templates/regression-candidates.md

This records the instruction review of slice B4's new regression candidates ledger template, a QA lane draft, for the change's author.

**In short:** 3 findings, none blocking: 1 contradiction, 1 step, 1 trigger. The page's one example of a triage row, a failure fixed upstream, is a bug a case already covers. The skeleton gives no title or purpose for creating the ledger file. Nothing on the fix path, where the page says rows often start, sends an agent here.

## Scope

In scope: the whole page, which is new and untracked. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/extend-the-workspace.md`, and the pages it links to: `docs/playbooks/regression-triage.md` and `docs/templates/regression-case.md`. Also read `docs/playbooks/fix-a-bug.md`, `docs/definition-of-done.md`, and the new "Lane templates" rows in `docs/templates/README.md`. The page gives no command to run. Ran `grep` for inbound links to the page and for "regression" or "candidate" in fix a bug and the definition of done, and `python3 ws.py check`, which reports nothing on this page.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | When to add a row | Not blocking. The ledger lists "bugs proposed as new regression cases". Its one example of a row triage adds is "a failure fixed upstream". In regression triage's classes, that is a case of the suite that failed in the run and passes at a newer commit: a case already exists for the bug, so the row proposes a case the suite holds. Verified: triage's "Fixed upstream" row and step 8. Inferred: that no second case is meant; the page does not say. | fixed: the example is gone; the page says a failing case never earns a row, since its case exists, and triage may add one only for a bug noted off a checkpoint that no case guards; triage's step 8 says the same. |
| 2 | step | Where it lives; Skeleton | Not blocking. Regression triage's step 8 creates `docs/records/regression-candidates.md` "from that template if it is missing". The page names its front matter, but the skeleton holds only the table: no title and no purpose sentence, which layout's page kinds table requires of a record, so `page_kinds` refuses a file made from the skeleton alone. The regression report template gives both in its skeleton. Verified: layout's page kinds table and the two skeletons. | fixed: the skeleton now holds the record front matter, the title and a purpose sentence before the table. |
| 3 | trigger | When to add a row | Not blocking. The page says a bug often meets the bar "once its fix merges", and "Anyone may add one for a fixed bug". The agent at that point is on fix a bug or the definition of done, and neither names the ledger. The only routes in are regression triage, the case template, the templates README and the reading paths, so the common trigger never fires. Verified: `grep` finds no "regression" or "candidate" in either page. Fix a bug is eval-covered, so a route from it waits for an eval run. | fixed: the page no longer promises a trigger: it says a person adds most rows after a fix merges and no procedure prompts it yet. A route from fix a bug would need an eval run, so it is not added. |

## Checked with no finding

- enforcement: each must and never has a Rules row tagged `prose`, which `rules` accepts.
- placement: the commit links procedure endings; the three open gaps are named as open, as the Rules table requires, and not as settled.
- eval-case: a lane template carries no proof keys; regression triage, which adds rows, is marked `proof: unproven` with `prove-by: M10`. Verified: its front matter.

## Re-check

A fresh session's reading after the fix round, on `1a18d68` with the uncommitted change of the B4 slice session. Read the whole page, the contract, procedure endings, and each page the changed text links to: regression triage's step 8, the regression case template, layout's page kinds and the records README's row for the ledger. The page gives no command to run.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | Verified: the fixed-upstream example is gone. "When to add a row" says a failing case never earns a row, and triage adds one only for a bug noted off a checkpoint. Triage's step 8 says the same. |
| 2 | upheld | Verified: the skeleton holds the record front matter, a title and a purpose sentence, which layout's page kinds table asks of a record. The purpose link resolves from `docs/records/` to this page's "The bar". |
| 3 | upheld | Verified: the page says a person adds most rows after a fix merges and no procedure prompts it yet. Fix a bug is not touched. |

What a fix broke:

- Not blocking. "When to add a row", beside "The bar". Triage's one route is now a bug noted off a checkpoint. The bar's fourth condition needs a merged fix. A bug triage has just drafted has no fix yet, so in a triage session the bar almost never holds, and triage's default adds no row. The route rarely fires. Inferred: from the two texts; not run.

What the first reading missed: none.

## Known defects

What stays open after the one fix round the plan allows, each not blocking.

- Not blocking, what a fix broke: triage's one route to a row, a bug noted off a checkpoint, rarely meets the bar's merged-fix condition, so the route seldom fires. Known defect, for the docs audit.
