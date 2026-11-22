---
kind: record
last-reviewed: 2026-11-22
covers: docs/extend-the-workspace.md
reviewed-at: 31f9aaa, with the uncommitted change of the B2 builder
---

# Instruction review: docs/extend-the-workspace.md

This records the instruction review of the new how-to "Extend the workspace", for its author and for anyone settling its findings.

**In short:** 6 findings: 2 step, 2 trigger, 2 enforcement. The page's kinds table, front matter rules and most tags hold. The in-place fix path the batch gives this page is under-specified, and two rows its rules table needs are missing.

## Scope

The whole page, which is new. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md`, and every page it links: `docs/parts.md`, `docs/changing-the-machinery.md`, `docs/research-ladder.md`, `docs/size-the-work.md`, `docs/playbooks/fix-a-bug.md`, `docs/playbooks/README.md`, `docs/how-tos.md`, `evals/README.md`, `docs/decisions/0006-what-proven-means.md`, `docs/playbooks/decision-interview.md`, `docs/rules/orders-api.md`, `opencode.json`, `workspace.json`, `README.md`, `docs/playbooks/instruction-review.md`, `docs/commits.md`, `docs/question-log.md` and `docs/maintain-the-workspace.md`. Also the other pages of batch 4 for the interface sweep. Commands and files checked: `python3 ws.py check` (passes, one unrelated warning), `python3 ws.py rules`, `parts/proof.py`, `parts/eval_record.py`, `evals/arms.json`, `evals/cases/*.json`, the front matter of `docs/decisions/*.md` and `docs/rules/*.md`, and `git diff` of `docs/parts.md` and `docs/how-tos.md` for the page's routes.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | Steps, step 5 "Route it" | Step 5 asks for a README proof-table row only "for a playbook or how-to". The page's own "One owner per topic" sends an overlapping procedure into an existing page as a section with a `Proof: unproven, prove-by M<n>.` line, and step 4's output may be that section. The `proof` check reads section proof lines as marks and fails when the README table has no `page#section` row for one, so the step as written leads to a refused commit with no instruction for the row. Verified: `parts/proof.py` compares every mark, sections included (`all_marks`), with the table, and the README already lists sections such as `docs/orchestration.md#delegating`. Cause: sheet-proof-row-names-pages-only — the sheet's bullet on the README's proof table speaks of adding "a playbook or how-to", and neither it nor the brief says a merged section needs its own row. | fixed: step 5 now asks for a README row for a procedure section too, named page#anchor, and the rules row says so. |
| 2 | step | What this page covers, its third paragraph; Steps, step 5; Rules, the INDEX.md and AGENTS.md row | The in-place path sends "a fix to a page a review or an audit found wrong" through these steps, but the page names only "a row in INDEX.md, and any line in AGENTS.md" as changing what the eval covers. The eval also hashes `CLAUDE.md`, `docs/playbooks/fix-a-bug.md`, `docs/definition-of-done.md` and `docs/rules/orders-api.md`. A fix in place to one of them fails `eval_record` at step 6, and the page gives no default for it; maintain's step 4 and the research ladder both say to list or batch such a change instead. Verified: `evals/arms.json` gives the guided arm those five files, and `evals/cases/nightly-job.json` and `big-report.json` add `docs/rules/orders-api.md`. Cause: sheet-silent-on-eval-covered-edits — the sheet's "small page change" bullet routes page fixes to extend without saying that some of those pages are ones the eval covers. | fixed: step 5 now names every eval-covered file, from evals/arms.json and the cases, and queues a fix in place to one of them; the in-place paragraph points there. |
| 3 | trigger | What this page covers, its second and third paragraphs | The second paragraph says a finding written into an existing page, "such as a missing alias", needs only the research ladder's offer, and to "use this page when the finding needs a new page or a new section". The third says a pages-only change, "such as a fix to a page a review or an audit found wrong", follows this page's steps. A docs audit's finding of a missing alias fits both, and the page names no tie-break, so the reader cannot tell whether to run the size gate, the checks and the instruction review here, or only the offer. Verified: read both paragraphs, and `docs/maintain-the-workspace.md` routes "a finding should have been written down" to the offer. Cause: sheet-no-tie-break-offer-vs-extend — section 2 of the sheet gives a kept finding to the offer and a found defect to extend, with no rule for a defect that is also a one-line finding. | fixed: "What this page covers" now says the offer decides whether a finding is written, and on a yes the write follows these steps; a rules row holds it. |
| 4 | trigger | The **In short** line; the how-to index row (docs/how-tos.md, "Changing the workspace") | The page now also owns small changes to existing pages, which maintain, the machine self-check and the sheet's defect route send here. Its **In short** line and its index row name only adding a page ("Add a playbook, how-to, reference page, decision record or rule page"), so neither fires for "fix a page that is wrong". The same index table keeps "Add, move or archive a page" pointing at [layout](../../layout.md), with no tie-break against this row. Verified: `docs/how-tos.md` "Changing the workspace" holds both rows; the page's purpose sentence names "or change one", its In short line does not. Cause: sheet-change-not-propagated — the sheet added the small-page-change route in a later version, after the page's route texts were set, and no pass re-checked them. | fixed: the In short line now names a small change to an existing page, and the page names layout and maintain for moving or archiving; the how-to index row's new text is in the builder's report for the orchestrator, who owns that file. |
| 5 | enforcement | Steps, step 8 "Report"; Rules | Step 8 requires every claim in the report to be marked verified or inferred, but the rules table has no row for it. Section 2 of the batch sheet gives that rule the tag `eval:fix-a-bug`, and the machine self-check, the docs audit and the four playbooks of the batch carry the row. Verified: `grep -l "eval:fix-a-bug"` lists those pages and not this one. Cause: sheet-tag-rule-not-a-row-rule — the sheet fixes which tag the report row carries, but does not say that every page of the batch must have the row. | fixed: added the rules row "Mark every claim in the report verified or inferred" tagged eval:fix-a-bug. |
| 6 | enforcement | Steps, step 4, the rule page bullet; Rules | "A rule page holds only facts that hold for every edit its pattern matches" is an only-rule with no row in the rules table. The neighbouring "A decision record is written only when..." has one. Verified: read the rules table. Cause: page-specific — the brief's self-review already asks for every must, never, always and only to have a row. | fixed: added a rules row for "A rule page holds only facts that hold for every edit its pattern matches", tagged prose. |

## Checked with no finding

- contradiction: the step 1 exception to the contract's "How work flows" is labelled, with its reason, as the sheet asks. The kinds table matches `docs/layout.md` (folders, `applies-to` on rule pages, `status: proposed` for a decision), the decision record rule matches the decision interview's three conditions, the evals rule matches `evals/README.md`, the approved-plan skip matches decision 0006, and `opencode.json` loads `docs/rules/*.md`. Statements about `parts.md`, `changing-the-machinery.md` and `maintain-the-workspace.md` hold against those pages as they are now. Verified.
- placement: the page restates neither parts nor changing the machinery, as the sheet's tie-break asks; the route in from `docs/parts.md` "The pieces" is in place. Verified.
- eval-case: the page is `proof: unproven`, `prove-by: M5`, and M5 is not in `building` (`["M3"]`). Verified.
- The other tags in the rules table exist in `python3 ws.py rules` and each case shows its rule. Verified.

## Re-check

A fresh session re-read the page on 2026-11-22, after the fix round.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | Verified: step 5 now asks a row for a procedure section named page#anchor, and the README holds `docs/orchestration.md#delegating` in that form, which `proof.marks` keys as `#slug`. |
| 2 | fixed | Verified: step 5 names the five guided-arm files of `evals/arms.json` and the rule page the `big-report` and `nightly-job` cases add, and defaults a fix in place to queued. |
| 3 | fixed | Verified: "What this page covers" now says the offer decides whether a finding is written and a yes routes the write through the steps; a rules row holds it. |
| 4 | fixed | Verified: the In short line names a small change to an existing page, and `docs/how-tos.md` now has extend's row naming page fixes and a layout row that sends adding a page to extend. |
| 5 | fixed | Verified: the rules table ends with the report row tagged `eval:fix-a-bug`. |
| 6 | fixed | Verified: the rules table holds the rule-page row, tagged `prose`. |

Broke:
- Steps, step 5: its new default queues every eval-covered change, with no case for an approved plan that must make one. Adopt's "Write the facts from evidence" sends contract and alias writes to this page's table, whose contract row points at step 5, while adopt's step 6 commits them on a branch. Inferred.

Missed: none.
