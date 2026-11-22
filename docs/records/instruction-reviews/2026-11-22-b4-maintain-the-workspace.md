---
kind: record
last-reviewed: 2026-11-22
covers: docs/maintain-the-workspace.md
reviewed-at: 31f9aaa, with the uncommitted change of the B2 builder
---

# Instruction review: docs/maintain-the-workspace.md

This records the instruction review of the new maintain-the-workspace how-to, for its author and for agents whose change sets off an upkeep duty.

**In short:** 5 findings: 2 contradiction, 1 step, 1 enforcement, 1 placement. Two event rows require edits to `INDEX.md` that step 4 forbids, the maintainer-only duties give the triggering session no action, the retrospective's transcript default differs from its own page, the rules table lacks two rows, and a page-writing rule sits here rather than on extend.

## Scope

In scope: the whole page, which is new. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md`, and every page it links: `docs/parts.md`, `docs/extend-the-workspace.md`, `docs/playbooks/README.md`, `docs/how-tos.md`, `docs/research-ladder.md`, `docs/question-log.md`, `docs/changing-the-machinery.md`, `docs/size-the-work.md`, `docs/commits.md`, `docs/decisions/0006-what-proven-means.md`, `docs/playbooks/docs-audit.md`, `docs/playbooks/prompt-retrospective.md`, `docs/playbooks/fix-a-bug.md`, `workspace.json`. Also read the other pages of batch 4 and the README's diff. Ran `python3 ws.py list`, `python3 ws.py check`, `python3 ws.py rules`, both `git grep` commands of "Pages due for proof" for M4, and read the docstrings of `links`, `aliases`, `rules`, `stale_pins`, `pin_on_default`, `proof` and `eval_record`, `evals/arms.json`, `.githooks/commit-msg`, the CI workflow and the plans' `milestone:` keys and `Approved by:` lines. Every row of "What the checks catch for you" matches `python3 ws.py list` and the parts' docstrings, including `review_trailer` at the commit, the push and CI. The pin row matches the README's limit on `git submodule update`, and there is no `.gitmodules`, which bears out "This repository has no pins".

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Duties an event sets off, the rows "A name in the code changes" and "A page is moved, renamed or archived"; When a duty falls due, step 4; Rules table | The rename row says to change the alias row in `INDEX.md`, and that `aliases` fails until you do; the page's first rule repeats it. Step 4 and the last rule say a change to `INDEX.md` is never made alone but listed for the maintainer. Both cannot hold: without the edit `aliases` refuses the commit, and with it `eval_record` refuses it until the eval runs again, so the rename cannot be committed and the page gives no way through. A moved page linked from `INDEX.md` or `AGENTS.md` hits the same bind through `links`. The way through exists elsewhere: changing the machinery's trap on eval-covered commits. Verified: `aliases` docstring (fails on a name gone from `src/`), `evals/arms.json` gives the guided arm `INDEX.md`, `eval_record` docstring (any change the hash covers fails until rerun). Inferred: that `links` reads `INDEX.md` and `AGENTS.md`, from its docstring ("the pages the workspace owns"). Cause: brief-silent-on-hashed-file-edits — the brief treats eval-covered files only as files a builder must not touch, and says nothing about a procedure whose own steps must edit one, so the page forbade the edit its rows require. | fixed: step 4 now lists a deferrable eval-covered edit for batching, and commits a check-required one on a branch per the eval-covered trap, unmerged until its run; both rows and the rules row point there. |
| 2 | step | Duties an event sets off, the opening paragraph and its last two rows; When a duty falls due, step 2 | The opening says the session whose change sets off an event does the duty, except the last two rows, which "the maintainer runs". No step says what that session does instead, such as naming the due audit or retrospective in its report. Step 2 tells it to follow the procedure page the row names, which is the very run the exception reserves for the maintainer. So an agent that lands a batch of pages either runs the audit against the exception or drops it with no report. Verified by reading the opening paragraph, the two rows and step 2. Cause: sheet-owner-without-handoff — the sheet names the maintainer as owner of these duties and makes the event list a trigger, but sets no step for a session that is not the owner and sets one off. | fixed: the opening and step 2 now tell a session that sets off the audit or retrospective, and is not running it, to name it as due in its report and go to step 5; a rules row says so. |
| 3 | contradiction | Periodic duties, the "A prompt retrospective" row | The row sets a default transcript: the session the maintainer names, or else "the newest transcript of a session that worked on the milestone". The retrospective's own step 1 sets a different default: the newest transcript of any session in this workspace other than the current one. Step 2 here sends the reader to follow that page, so the two defaults pick different transcripts whenever the newest session did not work on the milestone. Verified by reading both pages. Cause: shared-rule-restated-not-linked — the sheet says maintain links each procedure and restates none of its steps; this row restates a step's default and changes it. | fixed: the retrospective row no longer sets a default; it says the retrospective's first step picks the transcript. |
| 4 | enforcement | Rules table; When a duty falls due, step 5; Duties an event sets off, the question-log row | Step 5 requires every claim in the report marked verified or inferred, and the question-log row requires the log entry. Neither has a rules row. The sheet asks every page of the batch for the report row tagged `eval:fix-a-bug`; the other two pages of this builder carry it. Verified: `python3 ws.py rules` lists six rules for this page, none on the report or the question log. Cause: self-review-must-list-skipped — the brief's self-review asks for every must on the page to be listed against the rules table, and these two were missed. | fixed: rules rows added for the report's verified-or-inferred marks (`eval:fix-a-bug`) and the question-log entry, which step 5 now names. |
| 5 | placement | Duties an event sets off, the paragraph under the table; Rules table, the third row | "Whenever you write a page, never point a reader at an agent's private memory, a session's scratch folder, or any file only one machine holds" is a rule for writing any page. It sits on the upkeep page, not on extend the workspace, which the sheet makes the page for writing pages and which a writer follows. A writer following extend never meets it. Verified: `grep -rn -i "private memory"` over `docs/` and `AGENTS.md` finds it only on this page. Cause: page-specific — the sheet's extend/maintain tie-break already gives page writing to extend. | fixed: the writing rule left this page; an upkeep row now says to replace such a pointer with the fact, and the writing rule is reported to extend's builder. |

## Checked with no finding

- trigger: the purpose line and the how-to index row both name finding a duty from an event or a closing milestone; extend's "After the page lands" routes in with its condition; the docs audit and prompt retrospective are reached from this page's tables with their conditions.
- eval-case: the page is marked `proof: unproven` with `prove-by: M5`. The wrappers (B6), the routing eval (M4) and the lessons log (B3) are named as planned, with nothing to run until then.

## Re-check

A fresh session re-read the page on 2026-11-22, after the fix round.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | Verified: step 4 lists a deferrable eval-covered edit for the maintainer and commits a check-required one on a branch, per the trap in `changing-the-machinery.md#traps`, which exists and says the same; both rows point to step 4. |
| 2 | fixed | Verified: the opening and step 2 now tell a session that sets off the audit or retrospective, and was not asked to run it, to name it as due and go to step 5; a rules row holds it. |
| 3 | fixed | Verified: the retrospective row sets no default and defers to that page's step 1, which picks the newest transcript of another session in this workspace. |
| 4 | fixed | Verified: the rules table holds the report row tagged `eval:fix-a-bug` and a question-log row, and step 5 names the log. |
| 5 | fixed | Verified: the page-writing rule now sits in extend's step 4 and rules table; this page keeps only an upkeep row for a pointer found later. |

Broke:
- When a duty falls due, step 5: it commits a question-log entry "as step 4 says", and step 4 names the instruction review's trailer, though `review_trailer` excepts `docs/question-log.md` and commits asks a trailer only for guidance pages. Verified.

Missed: none.
