---
kind: record
last-reviewed: 2026-11-23
covers: docs/machine-self-check.md
reviewed-at: 18eccc5, with the uncommitted change of the B2t builder
---

# Instruction review: docs/machine-self-check.md

This records the instruction review of slice B2t's change to the machine self-check, which reworks step 1's no-Python branch and its question-log ending. It is for the change's author.

**In short:** 4 findings: 2 contradiction, 2 step; 1 blocking. The prompt the person pastes still says "Change nothing until you have given me the report", while the page now commits, and in this repository pushes, a question-log row before the report. Step 1's no-Python branch disagrees with the Input lines of steps 5 and 11, and skips step 7, which needs no Python. A question asked while offering fixes has no commit or push.

## Scope

In scope: the changed text (step 1's last sentences, the closing paragraph of "The report and the fixes", and the first and sixth Rules rows), and anything on the page or a linked page that the change contradicts or leaves stale. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/procedure-endings.md`, `docs/definition-of-done.md`, `docs/playbooks/fix-a-bug.md`, `docs/question-log.md`, and procedure endings' "The question-log entry" section, which the changed text links. Also read `wslib/launch.sh`, the Claude Code shell hook in `.claude/settings.json`, and `.githooks/pre-commit` and `.githooks/commit-msg`. Ran step 1's commands (`python3 --version` gave 3.9.6, `git --version` 2.50.1, `gh --version` 2.96.0), `PATH=/nonexistent /bin/sh wslib/launch.sh ws.py --version` (printed "ws: no Python 3.9 or later on the path ...", exit 2), `command -v` for `gh`, `git` and `npx`, `git diff fad9f23` on the page and `python3 ws.py check`, which reports no error on it.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | The prompt; The report and the fixes, the closing paragraph; Rules, the first row | Blocking. The prompt the person pastes says "Change nothing until you have given me the report." The change makes a question-log entry "the one exception to changing nothing until the report is given", and links procedure endings, whose order commits that entry before the report and pushes it, and whose push table has the agent push to main in this repository. The prompt, which carries the person's own words, was not updated, and the report template still ends "Changed: nothing." An agent following the page commits, and here pushes, before the report, against what the person said. Verified by reading the prompt block, the closing paragraph, the Rules row, and procedure endings' "The order", question-log section ("A procedure that otherwise commits nothing still commits this entry") and push table. Marked blocking because the agent acts against an instruction the person gave in this session; when in doubt, the playbook says to mark it blocking. | fixed: the prompt excepts a question-log row, and the template reads "Changed on the machine" with a separate question-log line. |
| 2 | contradiction | Steps, step 1; Steps, steps 5 and 11 | Not blocking. Step 1 now says that with no Python 3.9 or later, "steps 2 to 4 and 11 need no Python, step 5 runs and fails with the launcher's error". Step 5's Input is still "Python from step 1", step 11's is "Python and git from step 1", and the paragraph above the steps says "A step that needs something an earlier step found missing is marked skipped". The page gives two answers for steps 5 and 11 and labels neither as an exception. Verified: the launcher with no Python on the path prints its error and exits 2, so step 5 does run and fail; step 11's three commands (`gh auth status`, `git submodule status`, `npx --version`) start no Python. | fixed: steps 5 and 11 name inputs the no-Python path meets. |
| 3 | step | Steps, step 1 | Not blocking. Step 1's no-Python branch marks steps 6 to 10 skipped, step 7 among them. Step 7 runs `: >> .git/HEAD`, which needs no Python. In Claude Code the shell hook is `wslib/launch.sh hook before-shell ... or exit 2`, and the launcher exits 2 with no Python, so every shell command would be refused. A session that reaches this branch can run shell commands only because its hooks are not firing, which is what step 7 exists to show. Skipping it drops the one result that explains the branch. Verified: the hook command in `.claude/settings.json` and the launcher's exit 2. Inferred: that a running shell with no Python means the hooks are off, as Codex CLI without trust also gives. | fixed: the no-Python path runs step 7. |
| 4 | step | The report and the fixes, the closing paragraph; Rules, the sixth row | Not blocking. A question asked while offering fixes "is logged before your last reply". Procedure endings' order ends with the report, so nothing after it commits or pushes that row, and the page does not say whether to. The page links only procedure endings' question-log section, which says the row "is committed in the next step" and never mentions a push. The question log's own page says "commit and push it". This also leaves the push of the entry made before the report unstated. Verified by reading the closing paragraph, the Rules row, procedure endings' "The order" and the question log's "Adding an entry" line. | fixed: the question is logged and committed before the last reply. |

## Checked with no finding

- trigger: the **In short** line, "When to run it" and the how-to index row are unchanged, and the change does not alter when the self-check runs.
- enforcement: both changed Rules rows keep `prose`, as before; the report row keeps `eval:fix-a-bug`.
- placement: the closing paragraph and the Rules row link procedure endings for the question-log entry instead of restating how it is committed.
- eval-case: the page is marked `proof: unproven` with `prove-by: M5`.

## Re-check

A fresh session re-read the page on 2026-11-23 after B2t's fix round. It read the page whole, `git diff fad9f23` of it, the contract, procedure endings, changing the machinery's "Traps", maintain the workspace, fix a bug and the question log's "Adding an entry" line, and ran `python3 ws.py check`, which exits 0 with only the known warning on fix a bug's eval record.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | The prompt now reads "Change nothing until you have given me the report, except a question-log row for a question you had to ask me", so the person's own words allow the row before the report. The template reads "Changed on the machine: nothing." with a separate "Question log:" line, and the first Rules row names the same exception. Verified: the text. The fix leaves two smaller gaps, under "Broke". |
| 2 | upheld | Step 5's Input says it still runs, and fails, with no Python; step 11's Input is git alone and says none of its commands needs Python. Both now match step 1's branch. Verified: the text. |
| 3 | upheld | Step 1's no-Python branch runs steps 2 to 4, 7 and 11, skips 6, 8, 9 and 10, and labels how it differs from the "every shell command is refused" branch. Verified: the text. |
| 4 | fixed in part | A question asked while offering fixes is now "logged and committed, as that page says, before your last reply". The push the finding also named is still unstated: the page links only procedure endings' question-log section, and the template's line reads "the row added and committed". The docs audit's fix to the same gap in this round says "log it, commit it and push it". Verified: both pages. Not blocking. |

Broke:

- Not blocking. The closing paragraph still says "the last line of the report says what was changed on the machine, or nothing". The template's last line is now "Question log:", not "Changed on the machine:". Verified: the template and the paragraph.
- Not blocking. The template's "Question log: <the row added and committed, or none>" has no form for a row left uncommitted, which procedure endings' question-log section requires when the log already holds rows the session did not add, or when the commit is refused. That section says to give the row's text in the report. Verified: both texts.

Missed: none.
