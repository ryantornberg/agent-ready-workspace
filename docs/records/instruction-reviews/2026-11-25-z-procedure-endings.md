---
kind: record
last-reviewed: 2026-11-25
covers: docs/procedure-endings.md
reviewed-at: f326a7a, with the uncommitted change of the slice Z builder
---

# Instruction review: docs/procedure-endings.md

This records the instruction review of slice Z's change to procedure endings' report section, for its author and agents ending a procedure.

**In short:** 2 findings, none blocking: 1 enforcement, 1 contradiction.

## Scope

In scope: the whole page, with most attention to the uncommitted diff on f326a7a: the last paragraph of "The report", which now says a procedure that keeps its report in a record puts the same lines there as a copy, and that the reply still ends with the report, every claim marked. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md` (its procedure endings row), `docs/definition-of-done.md`, `docs/templates/fix-record.md` with its own uncommitted change, `docs/playbooks/fix-a-bug.md`, `docs/playbooks/escape-analysis.md` (step 9), `docs/playbooks/instruction-review.md`, `docs/layout.md`, `evals/arms.json`, `evals/cases/fix-a-bug.json`, `evals/grade.py`, `evals/run.py`, and the earlier record `2026-11-23-b2t-procedure-endings.md`. Ran `python3 ws.py check`: exit 0, with no finding on this page.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | enforcement | "The report", last paragraph; Rules table | Not blocking. The new sentence is a must: "The copy does not replace the reply: the reply still ends with the report, every claim marked." The rules table has a row for marking claims (`eval:fix-a-bug`) and one for a refused step not skipping the report (`prose`), but no row says the report goes in the reply, last, when a record holds a copy. That is the case this change exists for. Verified: the rules table. The nearest real enforcement is the fix-a-bug case's `report-marks-a-claim-verified` grader, which reads only the agent's final message (verified: `evals/grade.py`, "report" is the agent's final message; `evals/run.py` records it), so a row could cite `eval:fix-a-bug` truthfully for the marked claim in the reply. It would not hold "ends with" or "every claim" (inferred from the grader's `any` type and its one pattern). | fixed: the rules row tagged `eval:fix-a-bug` now also says the reply ends with the report, even when a record keeps a copy |
| 2 | contradiction | "The push", the sentence above the table | Not blocking. Outside the diff. "Then check whether you are off main: if you are, the table's first row applies and no other." A code change under `src/` and a machinery change always sit on a branch other than main, so read literally the code and machinery rows can never apply: the fix's branch is not pushed and no draft pull request opens, against fix a bug's step 5 ("open a draft pull request") and the table's own code row. "Off main" itself scopes its rule to pages ("push nothing for pages"). Verified: the page and fix a bug's step 5. Not blocking: no command fails, nothing reaches main, and what is left unpushed is named in the report (inferred). The record `2026-11-23-b2t-procedure-endings.md` holds this as a known defect for the docs audit; it is still present. | declined: outside this change, and already held as a known defect for the docs audit in `2026-11-23-b2t-procedure-endings.md` |

## Checked with no finding

- contradiction (the changed text): the new sentence agrees with definition of done's "The report" ("End your reply with it, and keep the same text where the row above says") and its row that a fix keeps the report in its fix record and other work in the final reply alone. Escape analysis's step 9, "the report is the only copy", is about a run with no plan and no record, and does not conflict. The fix record template's second push of the record on the fix's branch, against "Off main", is recorded in `2026-11-25-z-fix-record.md`, finding 3. Verified.
- step: the changed text names no command or path; "such as a fix record" points at a record the template defines. The order is unchanged: the report is step 5, always and last. Verified.
- trigger: the In short line ("Then report, each claim marked verified or inferred") and `INDEX.md`'s row ("How a procedure ends; commit, push, the question-log entry and the report") still describe the page; the change does not alter when it applies. Verified.
- placement: this page is where the report rule is stated once, and the new sentence belongs here; the shape stays on definition of done, linked from the section's first sentence. Verified.
- eval-case: the behavior, a marked report in the final reply even with a record, was already asked by this section's first sentence ("Report to the person in the session's reply") and by definition of done, and the fix-a-bug case grades a marked claim in the final message. This page is a reference page and carries no proof key (verified: `docs/layout.md`, page kinds). The guided arm in `evals/arms.json` does not hold this page; the one-time arm `routed-after-fix` reads it. Verified.
