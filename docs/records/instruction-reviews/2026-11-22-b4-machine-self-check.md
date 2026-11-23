---
kind: record
last-reviewed: 2026-11-22
covers: docs/machine-self-check.md
reviewed-at: 31f9aaa, with the uncommitted change of the B2 builder
---

# Instruction review: docs/machine-self-check.md

This records the instruction review of the new machine self-check how-to, for its author and for people checking that their machine runs the workspace.

**In short:** 2 findings: 2 step.

## Scope

The whole page, which is new in batch 4. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md`, the linked pages README ("Try it", "Use it for your own team", "Limits"), agent settings, browsers, size the work, extend the workspace, changing the machinery and the question log, the other batch 4 pages (adopt's step 2 routes in), the how-to index row, `.claude/settings.json`, `.codex/hooks.json`, `wslib/launch.sh` and `.githooks/pre-commit`. Ran in this worktree: `wslib/launch.sh ws.py --version` (0.3.0), `git config core.hooksPath` (`.githooks`), `ls -l .githooks wslib/launch.sh` (all executable), `git ls-files --eol | grep "w/crlf"` (no output), `grep -ns disableAllHooks .claude/settings.local.json ~/.claude/settings.json` (no line), `python3 tests/hook_cases.py` (`70 of 70 cases pass`), `python3 ws.py selftest` (every part `ok`), `python3 -m unittest discover -b tests` (604 tests, 6 failures, all from this batch's uncommitted edits), `python3 ws.py check` and `sh .githooks/pre-commit` (both exit 0 before other reviewers' records appeared), `python3 tools/symbols.py ReconciliationWorker src` (the class's file and line in `src/orders-api/ReconciliationWorker.cs`), `git submodule status` (no output), `npx --version`, `gh auth status`, and step 7's `: >> .git/HEAD` through this session's shell tool (refused by `git_folder_shell`).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | "Steps", steps 1 to 5 | Every step runs through the session's shell tool. That tool's before-shell hook calls `wslib/launch.sh ... \|\| exit 2` (`.claude/settings.json`, `.codex/hooks.json`). The launcher exits 2 when it finds no Python 3.9 or later, and a launcher with CRLF endings or no execute bit fails into `\|\| exit 2`. The README's "Limits" confirms every call before a tool runs is then refused. So on exactly the faults steps 1, 2, 3 and 5 look for, the agent cannot run `python3 --version`, the eol check or `ls -l`: every command is refused. The page has no branch for that, such as reading the refusal as step 5's result, or giving the person the commands to run in their own terminal. Verified by reading the wiring, the launcher and the README; the refusal on a broken machine is inferred, not run. Cause: sample-cannot-exercise-path — the builder's step pass ran on a machine with a working launcher, so the all-refused path never showed. | fixed: a "When every shell command is refused" branch records the refusal as step 5's result and gives the person steps 1, 2, 3 and 5 to run in their terminal. |
| 2 | step | "Steps", step 8 (and step 6) | Step 8 classes every failure as "a workspace bug, unless a failure names a tool step 1 found missing". Run on this worktree, `python3 -m unittest discover -b tests` failed 6 tests, all link errors from uncommitted edits that point at untracked new pages: work in progress, not a bug. Step 9 has the work-in-progress class; steps 8 and 6 do not, though the self-check may run in any working copy, a worktree included. Verified: ran the tests and read the failures. Cause: step-pass-skipped — the brief's step pass asks that each command be run and confirmed to do what the page says, and a run on the batch's own tree shows a result the class rule misnames. | fixed: a "Work in progress" rule covers steps 6, 8 and 9, and steps 6 and 8 now class failures from uncommitted edits as work in progress. |

## Checked with no finding

- contradiction: the read-only-until-report rule, the one-fix-at-a-time offer, the machine fix never committed and the workspace-bug route agree with the sheet's sections 2 and 3, with extend the workspace and with adopt's step 2; the Codex trust and `/hooks` note matches the README's "Limits"; the selftest tie-break matches the sheet's section 9. Step 7's refusal reaches the agent behind a tool prefix ("PreToolUse:Bash hook error: ... Refused by git_folder_shell: ..."), but the hook's own message starts as the page says.
- trigger: the purpose line, In short, "When to run it" and the how-to index row agree; adopt's step 2 routes in with its condition.
- enforcement: every must and never on the page has a rules row; the report row carries `eval:fix-a-bug`.
- placement: the page is a how-to under `docs/`, its commands are in its steps and its prompt is a code block a person pastes.
- eval-case: the page is `proof: unproven`, `prove-by: M5`, so its new behavior needs no case yet.

## Re-check

A fresh session re-read the page on 2026-11-22, after the fix round.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | "When every shell command is refused" records the refusal as step 5's result and gives the person steps 1, 2, 3 and 5 for their own terminal; the launcher's message does start "ws: no Python 3.9 or later", not "Refused by", as the branch says. Verified by reading the page and `wslib/launch.sh`. |
| 2 | fixed | "Work in progress" covers steps 6, 8 and 9, and steps 6 and 8 now class failures from uncommitted edits as work in progress before the bug class; verified by reading. |

Broke:
- "When every shell command is refused": it marks steps 1 to 10 "not run", yet reads results for steps 1, 2, 3 and 5 and records step 5's; "not run" is not a state In short or the report header (pass, fail, skipped) allows, and step 11 is left unnamed. Verified by reading.
- "Work in progress" and "The report and the fixes": the new class is to be "reported as such", but the report template has lines only for machine setup fixes, workspace bugs and skipped, and In short names only those two classes. Verified by reading.

Missed:
- "The report and the fixes", last paragraph: "Nothing this how-to does is committed" sits beside the contract's question-log write, with no word on committing that entry, while the docs audit says to commit it staged by name. Verified by reading both pages.

## Batch 5's fix round

The builder's one fix round on the re-check's items, on 2026-11-22. A fix that touched a rule several pages share changed every page holding it: how a question-log entry is committed now lives on [the question log](../../question-log.md) and the other pages link it; who pushes follows [changing the machinery](../../changing-the-machinery.md#the-path-for-a-machinery-change).

| Item | Disposition |
|---|---|
| Broke: the refused-shell branch marks steps "not run" | fixed: the branch gives the person steps 1 to 5 for their own terminal, records each result from the pasted output, and marks steps 6 to 11 skipped with the reason. |
| Broke: work in progress has no place in the report | fixed: the report template has a "Work in progress" line, the In short line names the class, the step still reads fail, and it is not offered as a fix. |
| Missed: no commit path for the question-log entry | fixed: the closing paragraph excepts the entry from "nothing is committed" and commits it as the log's page says; a rules row holds it. |

## Second re-check

A fresh session re-read the page on 2026-11-22, after batch 5's fix round.

| Item | Verdict | Evidence |
|---|---|---|
| Broke: the refused-shell branch marks steps "not run" | fixed | The branch now has the person run steps 1 to 5, records each from the pasted output, and marks steps 6 to 11 skipped with a reason, so every step has a state the report header allows; verified by reading the page and its diff. |
| Broke: work in progress has no place in the report | fixed | The template has a "Work in progress" line, In short names the class, the step stays fail for the header's count, and a closing line says it is not a fix to offer; verified by reading. |
| Missed: no commit path for the question-log entry | fixed | The closing paragraph excepts the entry from "nothing is committed" and links the question log's "Adding an entry" rule, which exists and says how to stage, commit and push it; verified by reading both pages, and `python3 ws.py check` exits 0 with the link. |

Broke:
- "Rules" table: the new question-log row says to add the entry "before you report", but the closing paragraph says "before you finish", after the report and fixes, and the first rule says change nothing until the report is given. Verified by reading.

Missed:
- "When every shell command is refused" against step 1: with no Python 3.9, step 1 marks steps 5 to 10 skipped, while the branch makes step 5 a fail and skips 6 to 11; the exception is not labelled. The round restated this, it did not start it. Verified by reading.
