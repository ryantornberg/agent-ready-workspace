---
kind: record
last-reviewed: 2026-11-22
covers: docs/playbooks/instruction-review.md
reviewed-at: 0d7c926, with the uncommitted change of the B3 builder
---

# Instruction review: docs/playbooks/instruction-review.md

This records the instruction review of B3's severity change to the instruction review, for its author and for reviewers who follow it.

**In short:** 4 findings: 1 contradiction, 2 step, 1 placement. None is blocking.

## Scope

In scope: the B3 builder's uncommitted change, shown by `git diff docs/playbooks/instruction-review.md`. It adds the severity mark to the In short line and to steps 3 and 4, a "Severity" section, the placement sentence on restated rules, the `Blocking.` or `Not blocking.` opening of the Finding cell, the "Re-check" and "Known defects" sections, the `known defect, for <...>` disposition, the second paragraph under "Counting for a stop rule", and the last rules row. Also in scope: anything else on the page that the change contradicts or leaves stale.

Read beside it: `AGENTS.md`, `INDEX.md`, `docs/procedure-endings.md` (new, uncommitted), `docs/records/instruction-reviews/README.md`, `parts/review_index.py`, `parts/review_trailer.py`, the `review_trailer` and `review_index` entries in `workspace.json`, and the plan `docs/plans/m3-reading-layer-machinery-and-kit.md`, "Changes after approval", the 2026-11-22 entry that sets the severity mark and lane B's stop rule. Also read the "Re-check" sections of `2026-11-22-b4-adopt-the-workspace.md` and the other B4 records, to see how a re-check is recorded today.

Ran: `git diff` on the page; a script that looks up each `part#case` tag in the rules table in `parts/<part>.cases.json` (all 10 found); `grep` for `procedure-endings`, `staged by name` and `fix round` on the page; `grep` for review terms in `INDEX.md` and `AGENTS.md`; `python3 ws.py check` (exit 0, one unrelated `eval_record` warning on `fix-a-bug.md`).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | "Steps", step 4, against "Severity" and the "Rules" table | Not blocking. Step 4 says "Never change a finding's severity mark". "Severity" says the author "never lowers its mark", and the new rules row says "the author never lowers the mark". The plan says only that "the builder cannot lower it". So the page both forbids and leaves room for an author who wants to raise a mark. Verified: the three sentences and the plan's line, by reading them. Inferred: that "never lowers" reads as letting the author raise a mark. | fixed: step 4 now says never lower the mark, as the Severity section and the rules row do. |
| 2 | step | "The record", "Re-check" and "Known defects"; "Counting for a stop rule" | Not blocking. The re-check lists "what the first reading missed, each marked blocking or not". A missed blocking item has no outcome. It is not one of the three stop triggers ("one that survives the fix round, a declined one a re-check rejects, or one a fix creates"). "Known defects" takes only non-blocking findings. The plan allows no second fix round. So the author cannot tell whether to stop, fix, or file it. The page matches the plan here, so the gap is in both. Verified: by reading the page's three passages and the plan's lane B stop rule. | fixed: step 4 now says a blocking finding still open when no fix round is left is never a known defect, and goes to the plan's owner in the report. The plan's own gap is proposed as a revision in B3's results. |
| 3 | step | "Steps", step 7, against "The record", "Re-check" | Not blocking. Step 7 says "If a fix changes a page again in substance, run the review again on that change", which by step 3 writes a new record. The new "Re-check" section records "a fresh session's reading after a fix round" in the same record, as the B4 records do. Nothing says which one follows a fix round, so the author cannot choose between a new record and a re-check. Verified: step 7, step 3 and the "Re-check" bullet, by reading them; the B4 records' practice, by `grep` for `## Re-check`. | fixed: step 7 now says a plan's re-check goes in the same record's Re-check section, and any other later change in substance gets a record of its own. |
| 4 | placement | "Steps", steps 6 and 7 | Not blocking. The new placement sentence makes a rule that procedure endings states, restated instead of linked, a finding, and says an older page switches to the link "when it is next edited". This page is being edited now. Step 6 still restates "staged by name", which is procedure endings' "Stage each file by name". Step 7 stops at the commit check and never links procedure endings for the push, the question-log entry and the report. The only link to `procedure-endings.md` is in the six-checks table. Verified: by `grep` on the page and by reading procedure endings' "The commit". | fixed: step 6 links procedure endings for the commit, and step 7 for the push and the report. |

## Checked with no finding

- trigger: the In short line now says each finding is "marked blocking or not", which matches step 3 and "Severity". The purpose line still fits. `INDEX.md` has no row for the instruction review, procedure endings or severity. That was so before this change, and the plan leaves missing `INDEX.md` rows to slice Z, so it is not counted here.
- enforcement: all 10 `part#case` tags in the rules table name cases that exist in `parts/review_trailer.cases.json` and `parts/review_index.cases.json`. The new row is tagged `prose`, which is true: neither part reads the `Blocking.` or `Not blocking.` opening, and the page says "the index does not hold severity". `review_index.py` reads only the first table under the header `| # | Class | Where | Finding | Disposition |`, so the "Re-check" table `| # | Verdict | Evidence |` and a "Known defects" section do not change its count. It leaves out only dispositions starting with "declined", so a `known defect, for ...` finding still counts, as the index's README says.
- eval-case: the page is `proof: unproven` with `prove-by: M4`, so the new behavior needs no case yet.
- Agreement with the plan: the four blocking conditions, the rule that the builder cannot lower a mark, the three stop triggers, and "Known defects" for the `prove-by` milestone or the docs audit all match the 2026-11-22 entry; the page adds "a command that does not exist" and "when in doubt, blocking", which widen and do not conflict. `docs/playbooks/docs-audit.md` exists, and the `#severity` anchor resolves to the new heading.
