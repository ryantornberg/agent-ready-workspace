---
kind: record
last-reviewed: 2026-11-22
covers: docs/playbooks/docs-audit.md
reviewed-at: 31f9aaa, with the uncommitted change of the B2 builder
---

# Instruction review: docs/playbooks/docs-audit.md

This records the instruction review of the new docs audit playbook, for its author and for the maintainer who runs the audit.

**In short:** 3 findings: 1 contradiction, 2 step. The read-only rule says the audit writes no record while the page requires a question-log entry, step 1's claim about what the audit reads is false on a dirty tree, and the deferred-findings item has no default for a finding queued to a person.

## Scope

In scope: the whole page, which is new. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md`, and every page it links: `docs/maintain-the-workspace.md`, `docs/playbooks/instruction-review.md`, `docs/size-the-work.md`, `docs/question-log.md`, `docs/extend-the-workspace.md`, `docs/changing-the-machinery.md`, `docs/research-ladder.md`, `docs/playbooks/README.md`, `docs/how-tos.md`. Also read the other pages of batch 4 and the diffs of the edited pages. Ran `python3 ws.py check`, `python3 ws.py check --phase ci`, `python3 ws.py rules` (ends with a count per kind of tag), `git rev-parse --short HEAD`, and every command of "The judgment pass": the heading count, both routing loops (no output), and the deferred-findings grep (24 rows). Read the `page_kinds` and `stale_pages` docstrings for the stale-page warning, the plans' "Results" headings and the milestone records' `status:` lines.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | When it runs, the paragraph under the table; Steps, step 5; Rules table, the first and last rows | The page says the audit "edits no page and writes no record", and step 5 says "The audit wrote nothing, so nothing is left uncommitted". The same paragraph and the last rule require adding a question-log entry before finishing. The question log is a record, as layout says, and the research ladder says it is written "with or without a yes". So an audit that had to ask a person writes a record the page says it never writes, and that entry has no commit or uncommitted ending. Verified: layout's "Folders" section ("One record sits outside `docs/records/`: the question log"), the question log's `kind: record`, and the research ladder's offer section. Cause: sheet-forbids-labelling-exception — the sheet's section 3 tells the read-only pages to state the question-log rule in the contract's words and not label it an exception, beside a "writes no record" rule it breaks. | fixed: the page now says it changes no line of what it reads, and step 5 commits any question-log entry staged by name, or reports it uncommitted with the refusal. |
| 2 | step | Steps, step 1 | Step 1 says "The audit reads that commit's pages, since `git grep` reads only tracked files", and puts uncommitted changes outside the audit. `git grep` without `--cached` reads the working-tree text of tracked files, so a modified tracked page is read as modified. The checks of step 2 and the playbook loop of item 3, a shell glob, read the disk too, untracked pages included, while item 3's second loop skips untracked pages. On a dirty tree the audit reads a mix and reports it as the commit. Verified: `git grep -n "Machine self-check" -- docs/how-tos.md` matched a line that `git show HEAD:docs/how-tos.md` lacks; `git grep -c maintain -- docs/maintain-the-workspace.md` on the untracked page found nothing. Cause: step-pass-skipped — the brief's step pass asks each command to be run and confirmed to do what the page says, and this claim about what the commands read does not hold. | fixed: step 1 now says the checks, git grep and loops read pages on disk, git grep skips untracked files, and any changed or untracked page is named in the report. |
| 3 | step | The judgment pass, item 4 | Item 4 asks, for each deferred finding, whether "the slice or milestone it names" is done. Five of the rows its grep lists today name neither: they read "queued for the maintainer" or "queued for the maintainer, with finding 4". The item gives no default for such a row, so an agent cannot tell whether it is a finding. Verified: `git grep -n -E '[|] *(deferred to|queued for) (the maintainer|later)' -- docs/records docs/plans` lists five rows. Cause: step-pass-skipped — the brief's step pass requires a default for every decision in a step. | fixed: item 4 now gives a default: a row naming no slice or milestone is listed for the maintainer unless a later record, plan entry or commit shows it settled. |

## Checked with no finding

- trigger: the purpose line, the "When it runs" table and the catalog's Upkeep row fire on the milestone cadence, on a batch of page changes and on request, and send one commit's pages to the instruction review and a known fix to the size gate; the maintain page routes in from its event list and periodic duties.
- enforcement: every must and never on the page has a row; the report row carries `eval:fix-a-bug` as the sheet asks; the rest are `prose`, and `python3 ws.py rules` lists all six.
- placement: the cadence and owner are stated in the sheet's words, as maintain states them; the steps and categories sit on this page only, and maintain links them rather than restating them.
- eval-case: the page is marked `proof: unproven` with `prove-by: M10`. The scheduled audit is named as M10's, with the by-hand cadence until then.

## Re-check

A fresh session re-read the page on 2026-11-22, after the fix round.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | Verified: "When it runs" now forbids writing a record of its own, which the question log is not, and step 5 commits any question-log entry staged by name or reports it uncommitted with the refusal. |
| 2 | fixed | Verified: step 1 now says the checks, `git grep` and the loops read pages on disk, `git grep` skips untracked files, and each changed page is named; `git status --short` over the scope lists them. |
| 3 | fixed | Verified: item 4 now lists a row naming no slice or milestone for the maintainer unless something later shows it settled; the grep still returns such rows, two from batch 1. |

Broke:
- The In short line: "The audit changes nothing it reads", yet judgment item 5 reads the question log and step 5 may add an entry to it. Verified by reading; that the fix round wrote the line is inferred.

Missed: none.
