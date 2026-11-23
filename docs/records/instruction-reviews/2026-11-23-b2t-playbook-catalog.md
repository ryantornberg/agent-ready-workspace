---
kind: record
last-reviewed: 2026-11-23
covers: docs/playbooks/README.md
reviewed-at: 18eccc5, with the uncommitted change of the B2t builder
---

# Instruction review: docs/playbooks/README.md

This records the instruction review of slice B2t's edit to the playbook catalog, for its author and for critics.

**In short:** 2 findings: 2 trigger, none blocking. The widened Debugging row now fires on a failed CI run, as git-host operations does, and nothing says which wins. The prompt retrospective row still names escape analysis by its old title.

## Scope

In scope: the link change in the adversarial review row, from commit 18eccc5, and the uncommitted edit. That edit moves the review date and, in "Before you pick one", renames the red team rung's page and adds a sentence linking procedure endings. It also renames three rows, red team review, defect escape analysis and federated search, and widens the Debugging row. Also in scope: anything on the page, or on a page it links to, that the change contradicts or leaves stale.

Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/procedure-endings.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/size-the-work.md`, `docs/templates/hand-off-plan.md`, `docs/records/README.md`, and `docs/reader-standard.md`. Also the pages the changed text links or renames: red team review, debugging, escape analysis, search every source, and git-host operations' "When to use it, and which page wins". Ran `git diff -M fad9f23` and `git diff` on the page and on those four playbooks. Ran `python3 ws.py check`: it passes, with one warning on `fix-a-bug.md` that has nothing to do with this page. Checked each changed row's title and Proof cell against its page's heading and front matter. Ran a loop that checks every playbook in `docs/playbooks/` has a row.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | "The catalog", the Debugging and Git-host operations rows | Not blocking. The Debugging row now fires when "something fails and you cannot yet say why, such as a bug report, a failing test or CI run". The Git-host operations row fires on "read why its CI failed". Git-host operations gives "why is CI red on pull request 42" as a typical request. Its "which page wins" table has no row for debugging, and debugging has no section on when it runs. A request such as "why is CI red" now matches both rows, and neither the catalog nor either page says which wins. Debugging's step 1 even reads the failed log with `gh run view RUN --log-failed`, the same read. Verified: read both rows, git-host operations' "When to use it, and which page wins", and debugging's opening and step 1. Inferred: that agents will split between the two routes. Both read before they write, and debugging changes code only when asked to fix, so no write goes wrong. | fixed: the Debugging row says reading CI with no cause to find is git-host operations. |
| 2 | trigger | "The catalog", the Prompt retrospective row | Not blocking. The row's tie-break reads "Not why a review missed a defect, which is escape analysis." Three rows above, the same change retitles that row "Defect escape analysis", and the page's heading changed to match. The tie-break now names the page by a title it no longer carries, without a link. The reader standard keeps old names only as search words in `INDEX.md`. The old words are still part of the new title, so a reader still finds the row. Verified: read both rows and the heading of `escape-analysis.md`. | fixed: the tie-break uses the new title. |

## Checked with no finding

- contradiction: "Before you pick one" now names red team review for the red team rung, which matches size the work's ladder table. The Debugging row matches `debugging.md`'s new purpose line. Each renamed row's title matches its page's heading: "Red team review", "Defect escape analysis", "Federated search". Each Proof cell matches its page's front matter: M9, M4, M6 and M8.
- step: the page has no steps. Every link resolves, and `python3 ws.py check` passes its links check.
- enforcement: both Rules rows still hold. The loop found a row for every playbook in `docs/playbooks/`.
- placement: the new sentence in "Before you pick one" links procedure endings and restates none of its rules.
- eval-case: the page is a reference. No eval case or arm in `evals/arms.json` reads it, and each row it changes routes to a page marked unproven with a `prove-by`.

## Re-check

A fresh session re-read the page on 2026-11-23, after B2t's fix round.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed in part | The catalog's Debugging row now adds "Reading a pull request's CI state or log, with no cause to find, is git-host operations." So the catalog now says which page wins. The git-host operations page still does not. Its "which page wins" table has no row for debugging, and it still gives "why is CI red on pull request 42" as a typical request. That request also matches the new Debugging row: a failing CI run whose cause is not yet known. The tie-break turns on "no cause to find", which an agent cannot know before it reads the log, and no default is given. Both routes read before they write. Verified: the catalog row and git-host operations' "When to use it, and which page wins". |
| 2 | fixed, holds | The Prompt retrospective row's tie-break reads "which is defect escape analysis", matching the row title and the page's heading. Verified: the page and `escape-analysis.md`'s heading. |

Broke:

- none.

Missed:

- none.
