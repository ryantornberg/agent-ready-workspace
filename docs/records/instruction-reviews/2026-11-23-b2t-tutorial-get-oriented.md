---
kind: record
last-reviewed: 2026-11-23
covers: docs/tutorials/get-oriented.md
reviewed-at: 18eccc5, with the uncommitted change of the B2t builder
---

# Instruction review: docs/tutorials/get-oriented.md

This records the instruction review of slice B2t's new get-oriented tutorial, for its author and for the newcomer who runs it.

**In short:** 5 findings: 2 contradiction, 1 step, 2 trigger. 2 are blocking: `python3` as written fails on a common Windows setup, and step 5 discards any uncommitted change to the glossary.

## Scope

The page is new and uncommitted, so the whole page was in scope.

Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `README.md` ("Try it", "What is checked, and by what", "Limits"), `docs/layout.md` ("Page kinds", "The opening", "Tutorials"), `wslib/blocks.py`, `wslib/launch.sh`, `tests/test_tutorials.py`, `.github/workflows/ci.yml`, `docs/procedure-endings.md`, `docs/question-log.md`, `docs/commits.md`, `docs/machine-self-check.md`, `docs/research-ladder.md`, `docs/how-tos.md` (with the builder's uncommitted row), `docs/playbooks/README.md`, `docs/glossary.md`, `docs/tutorials/first-agent-task.md`, and `src/orders-api/ReconciliationWorker.cs`.

Ran, on macOS only: cloned the worktree's HEAD (18eccc5) into a scratch folder, copied both tutorials in, committed them there with `--no-verify` and a throwaway identity, and called `wslib.blocks.run_tutorial` on the page. It passed: every block ran, the `[links]` line printed, the guard refused, and `ws.py check` gave only the expected `eval_record` warning. Linux and Windows were not run. Also ran, in a second scratch clone: the two hook calls of step 4 by hand (exit 0 and exit 2, and no state left but the git folder's case cache), a commit holding step 5's broken link with the hooks given by `-c core.hooksPath=.githooks` (refused by `links`), and step 5 over a file with an earlier uncommitted edit (finding 2).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | "Before you start", and every block that calls `python3` (steps 1 to 5) | Blocking. The page says every block runs as written on Windows, in Git for Windows' bash, and that CI proves it there. But the Python installer for Windows gives no `python3`, as `wslib/blocks.py` says beside `LAUNCHER` and machine self-check step 1 says ("Where `python3` is missing, as on some Windows machines, try `python` and `py`"); what is left is often the Windows Store stand-in, which the launcher itself skips. CI cannot catch this: `run_tutorial` puts `python3() { bash "$WS_CLONE/wslib/launch.sh" "$@"; }` before the blocks, so in CI `python3` is the launcher, not the command the reader types. A Windows reader following the page then runs a command that fails at step 1. Fix: tell the Windows reader what to type, such as `bash wslib/launch.sh` in place of `python3`, or have them define the same function first, and say that CI runs `python3` through the launcher. Verified by reading `blocks.py`, `launch.sh` and machine self-check step 1; the failure on a Windows machine is inferred, not run. | fixed: step 1 sends python3 through the launcher, in a runnable block CI runs. |
| 2 | contradiction | "In short" ("Nothing you run changes the workspace for anyone else"), with "5. Break a link on purpose" and "Before you start" | Blocking. Step 5 ends with `git checkout -- docs/glossary.md`, which puts back the whole file, not only the line it added. The page never asks for a clean clone, or one no agent session works in; its sibling tutorial and the how-to index row do. So in a clone where someone else has an uncommitted change to the glossary, the step discards it. That breaks the page's own promise and procedure endings' rule that an uncommitted change you did not make is not reverted. This worktree is such a clone: `git status` shows ` M docs/glossary.md`. Fix: before step 1, have the reader confirm `git status --short` prints nothing and that no agent session works in the clone, or break a link in a new untracked page and delete it instead. Verified: in a scratch clone, an earlier uncommitted line in the glossary was gone after the step's commands ran. | fixed: step 5 writes a practice page of its own and deletes it; no tracked page is edited. |
| 3 | contradiction | "2. Find the nightly job three ways", the third lookup | Not blocking. The block's third case is "You have only a fragment of text", and it runs `git grep -n "class ReconciliationWorker"`, which searches for a code name. The [research ladder](../../research-ladder.md#pick-one-lookup) sends part of a name to `python3 tools/symbols.py --contains PART src`, and keeps `git grep` for "text that is not a name, such as a message or a setting". So the example teaches the newcomer the row the ladder says not to use for that input. Fix: search for text that is not a name, such as the worker's summary comment, `git grep -n "once a night" -- src`. Verified by reading the ladder's table and `ReconciliationWorker.cs`. | fixed: the third lookup searches a phrase from a comment. |
| 4 | trigger | The page as a whole: what routes a newcomer to it | Not blocking. The only page that links the tutorial is the how-to index, in the builder's uncommitted row. `README.md`, `AGENTS.md` and `INDEX.md` link neither the tutorial nor the how-to index, so a newcomer who starts at the README's "Try it", as most will, never reaches it. Fix: a line in "Try it" or a row in INDEX.md's topics; both are eval-covered files, so batch the change. Verified by `grep` over the worktree for the page's name and for `how-tos.md`. | queued for slice Z: an `INDEX.md` row for the tutorials; the how-to index routes to them now. |
| 5 | trigger | The purpose sentence | Not blocking. Layout's "The opening" asks the purpose sentence to say what the page is for and who reads it. This one says what the walk covers but names no reader, and neither does the **In short** line; nothing on the page says it is for someone new. Verified by reading the opening against `docs/layout.md`. | fixed: the purpose line names the newcomer. |

## Checked with no finding

- step, beyond finding 1: every block ran green on macOS in a fresh clone of the commit; the README anchors `#try-it` and `#what-is-checked-and-by-what` resolve (the `links` check passed); each block uses only `python3`, `git`, `grep`, `printf` and `echo`, which Git for Windows ships; step 4's `&& exit 1 || echo` stops the run if the guard ever lets the edit through; the page's stated outputs match the run, among them the `[links]` line naming the file, the rule's page and the re-run command, and `git status --short` printing nothing in a clean clone.
- enforcement: the page states one enforcement, that CI runs every block on Linux, macOS and Windows. `tests/test_tutorials.py` runs every tutorial at HEAD, `.github/workflows/ci.yml` runs the tests on all three systems, and the pre-push hook runs a tutorial a push to main changes (`wslib/runner.py`, `push_tutorials`). It holds, except for how `python3` runs on Windows, which is finding 1. The claim that a commit holding the broken link would be refused was verified with the hooks wired.
- placement: the page links the research ladder for which lookup to use rather than restating its rules, and links the README for setup and the guards; it restates no procedure-endings rule.
- eval-case: the page asks nothing of an agent; it is run by a person with no agent, and a tutorial carries no proof state.

## Re-check

A fresh session re-read the page on 2026-11-23, after B2t's fix round. It cloned the worktree's HEAD (18eccc5) into a scratch folder outside the worktree, copied both tutorials in, committed them with `--no-verify` and a throwaway identity, and called `wslib.blocks.run_tutorial` on this page: it passed. Every block ran, `ws.py --version` printed 0.3.0, every part's selftest passed, the hooks path printed `.githooks`, the three lookups printed `INDEX.md:47`, `ReconciliationWorker.cs:4` and line 3's "once a night" comment, the guard refused, step 5 printed the `[links]` line for `docs/practice-broken-link.md`, and `ws.py check` gave only the expected `eval_record` warning. macOS only; Windows judged by reading.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed, holds | Step 1's runnable block now defines `python3() { bash wslib/launch.sh "$@"; }`, so the reader's `python3` is the launcher on every system. `blocks.script` puts its own `LAUNCHER` line first and the page's block after it, so the page's definition replaces it and CI runs the reader's own function, not a stand-in. In Git for Windows' bash, `bash` is Git's, and `launch.sh` finds `python3`, `python` or `py` and tries the Windows Store stand-in last. No recursion: the function is not exported, so the launcher's `command -v python3` sees only real programs. Verified: the run, `blocks.py` (`script`, `LAUNCHER`) and `launch.sh`; the Windows behavior is inferred from reading. |
| 2 | fixed, holds | Step 5 writes `docs/practice-broken-link.md`, a new untracked page, then `rm`s it. No tracked file is edited, so no one's uncommitted change can be lost. Verified: in the scratch clone, `git status --short` was empty before and after the step's three commands, and the check also reported the page's missing `kind` and `last-reviewed`, as the page's text says. |
| 3 | fixed, holds | The third lookup is `git grep -n "once a night" -- src`, text that is not a name, which is the research ladder's row for `git grep`. Verified: the run printed the class's summary comment from `ReconciliationWorker.cs`, and the ladder's lookup table. |
| 4 | queue accepted, entry missing | Queuing is right: the eval hashes `INDEX.md`, and the plan keeps a missing `INDEX.md` row for slice Z. But the plan's list of edits queued for slice Z holds no tutorials row. Its only tutorial line is B1's row for layout's "Tutorials". Until that entry is written, the queue is a claim only. Verified: grep over the plan for "tutorial" and "get-oriented". |
| 5 | fixed, holds | The purpose line reads "A thirty-minute walk for a newcomer with no agent". Verified: the page, and `page_kinds` passed on it in the run. |

Broke:

- Not blocking. The step 1 function stays in the reader's terminal after the walk. It calls `wslib/launch.sh` by a relative path, so from any other folder `python3` fails with "No such file or directory" (exit 127). The page says to keep the terminal open but never says how to undo the function, such as `unset -f python3`. Verified: in zsh, the function worked at the clone's top folder and failed from `docs/`.

Missed:

- none.
