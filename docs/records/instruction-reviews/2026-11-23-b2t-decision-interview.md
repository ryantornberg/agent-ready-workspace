---
kind: record
last-reviewed: 2026-11-23
covers: docs/playbooks/decision-interview.md
reviewed-at: 18eccc5, with the uncommitted change of the B2t builder
---

# Instruction review: docs/playbooks/decision-interview.md

This records the instruction review of slice B2t's change to the decision interview playbook, for the change's author. The change ends step 10 as procedure endings says.

**In short:** 2 findings: 1 step, 1 contradiction; none blocking. Step 10 commits before it logs a question, then lists only "push" and "report", so its own order has no commit for the log row. Its Output says the commits are pushed, where procedure endings has a person push in a team's workspace.

## Scope

In scope: the changed text (step 10, the "The question log" section and the last Rules row), and anything on the page or a linked page that the change contradicts or leaves stale. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/procedure-endings.md`, `docs/definition-of-done.md`, `docs/playbooks/fix-a-bug.md`, `docs/question-log.md`, `docs/playbooks/instruction-review.md` (step 10 runs it), and the hand-off plan template's "Changes after approval" section. The changed text names no command that only reads; `git push` was not run. Ran `git diff fad9f23` on the page and `python3 ws.py check`, which reports no error on it.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | Steps, step 10 | Not blocking. Procedure endings runs its steps in the order log, commit, push, report. Step 10 commits the plan and any reviewed rows first, then says "log any question ..., push the commits, and report". Its own sequence has no commit for a question-log row written after that commit, so an agent that follows the step's words pushes without it. The last Rules row ("committed and pushed as procedure endings says") and procedure endings' section ("committed in the next step, with the rest or on its own") cover it, so a careful reader gets it right. Verified by reading step 10, the Rules row and procedure endings' "The order". | fixed: step 10 logs the question and commits the row before the push. |
| 2 | contradiction | Steps, step 10, its Output | Not blocking. Step 10's Output is "the commits, pushed". Procedure endings' push table says that in a team's workspace a person pushes, and the agent leaves the commits unpushed and says so. The sentence before the Output defers to procedure endings, so the Output line alone states something that does not hold for a team's workspace. Verified by reading step 10 and the "Who pushes" column of procedure endings' push table. | fixed: step 10 leaves the push to the person where procedure endings says a person pushes. |

## Checked with no finding

- trigger: the purpose line, **In short** line and "When to use it" are unchanged, and the change does not alter when the interview runs.
- enforcement: the changed Rules row keeps `prose`; the row tying glossary rows and decision records to `review_trailer` is unchanged and still true.
- placement: step 10 and "The question log" now link procedure endings for the question-log entry, the push and the report instead of restating them; the removed "marked verified or inferred, as the contract says" is carried by procedure endings' report.
- eval-case: the page is marked `proof: unproven` with `prove-by: M9`.

## Re-check

A fresh session re-read the page on 2026-11-23 after B2t's fix round. It read the page whole, `git diff fad9f23` of it, the contract, procedure endings, changing the machinery's "Traps", maintain the workspace, fix a bug and the instruction review, and ran `python3 ws.py check`, which exits 0 with only the known warning on fix a bug's eval record.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | Step 10 now runs log, commit the row, push, report, in procedure endings' order. Verified: the text. The new "commit the row" leaves a smaller gap, under "Broke". |
| 2 | upheld | Step 10 says to push "or leave them for the person where that page says a person pushes", and its Output reads "the commits, pushed as that page says". That matches the "Who pushes" column of procedure endings' push table. Verified: both texts. |

Broke:

- Not blocking. Step 10 now says to log the question "and commit the row" with no condition. Procedure endings' question-log section, which "The question log" below links, says not to stage the log when it already holds uncommitted rows the session did not add. The step does not label that case as an exception to its own words. A reader who follows the link gets it right. Verified: both texts.

Missed: none.
