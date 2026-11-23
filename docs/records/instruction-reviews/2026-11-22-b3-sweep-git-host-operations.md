---
kind: record
last-reviewed: 2026-11-22
covers: docs/playbooks/git-host-operations.md
reviewed-at: f757aed, with the uncommitted change of the B3 builder
---

# Instruction review: docs/playbooks/git-host-operations.md

This records the review of the fix-round link to the pull request template, for its author and any agent opening a pull request.

**In short:** 1 finding, not blocking: 1 trigger. The page now sends a description to the pull request template, but its merge row does not send a merged pull request to that template's bookkeeping list.

## Scope

In scope: the fix round's change to the "Title and description" row of "The operations", shown by `git diff -- docs/playbooks/git-host-operations.md`, read in the context of the whole page. It replaces the row's own shape for a description with a link to the template. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/instruction-review.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/authoring.md`, `docs/templates/pull-request.md` and its review record, `docs/templates/README.md`, `docs/commits.md`, `docs/changing-the-machinery.md`, `docs/playbooks/review-orchestrator.md`, and B3's row and the 2026-11-22 entries naming B3 in the M3 plan. Ran `python3 ws.py check` in the worktree: its only errors are review records of the B3 fix round not yet in the index, none about this page. Searched `docs/`, `README.md`, `AGENTS.md` and `INDEX.md` for "bookkeeping".

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | The operations, the "Publish and merge" row | Not blocking. The pull request template says to work down its bookkeeping list once a pull request merges, "when you merged it". This page's merge row sends the agent to changing the machinery, which merges and does not name the list either. Outside the template, only the templates index mentions the bookkeeping. So an agent merging through this page never reaches the list: the branch, the tracker item, the plan's "Results" and stacked pull requests are left as they were. Verified: the two rows, and a search for "bookkeeping" that finds only the template, the templates index, the M3 plan and an unrelated line of decision 0006. | open |

## Checked with no finding

- contradiction: the template's title rule, a commit subject with a ticket's key first when the team's format puts it there, fits this row's rule that the key goes in the title or the description. The template's "Review" section matches the "Create a pull request" row: link the record for the tip, or say on the fix a bug path that no review ran. The template's scope, this repository and those pinned under `src/`, is this page's. Verified.
- step: the template says to write the description to a scratch file and pass it with `--body-file`, which the "Create a pull request" and "Update the description" rows do. Step 6 compares the body with that file. Verified.
- enforcement: the new sentence is an instruction, not a must or a never, so it needs no Rules row. Verified.
- placement: the row now links the template instead of giving its own shape, and keeps only the two rules this page owns: where a ticket's key goes, and how to link a file of this workspace. Verified.
- eval-case: the page is `proof: unproven` with `prove-by: M8`. Verified from the front matter.
