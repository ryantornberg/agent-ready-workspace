---
kind: record
last-reviewed: 2026-11-28
covers: docs/templates/pull-request.md
reviewed-at: 176642f, with the uncommitted change of the G1 builder
---

# Instruction review: docs/templates/pull-request.md

This records the instruction review of M4 slice G1's change to the pull request template's bookkeeping list, for its author and whoever works down it.

**In short:** 1 finding, none blocking: 1 step.

## Scope

In scope: the uncommitted diff against 176642f, which rewrites the "Stacked branches" row of "After the merge: the bookkeeping list": in this repository, `python3 ws.py merge` has already retargeted the stacked pull requests; after a merge made another way, the agent reads each base and asks before a retarget. Read with it: the rest of the bookkeeping list, in particular "The branch" row, which uses the same "In this repository ... After a merge made another way" form, and the rules table. Read beside it: `AGENTS.md`; `INDEX.md`; `docs/playbooks/git-host-operations.md` and `docs/changing-the-machinery.md`, with their changes; the earlier record [2026-11-22-b3-pull-request.md](2026-11-22-b3-pull-request.md); the plan `docs/plans/m4-fail-closed-guards-review-loop-and-evals.md`, row G1 and Q84. Code read: `git diff origin/main..HEAD -- wslib/merge.py`.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | After the merge: the bookkeeping list, the Stacked branches row | Not blocking. The row's first clause keys on the repository: "In this repository, `python3 ws.py merge` already retargeted each open pull request". Two cases in this repository fall outside it. When the helper merged and then failed a retarget, or could not list the stacked pull requests, it exited 2 and kept the branch, so some stacked pull requests were not moved. When a person merged from the web page, the helper did not run at all. An agent doing the bookkeeping takes the first clause and skips the check the second clause gives. The cost is a stacked pull request left on a kept branch, or, after a web merge, one GitHub may already have closed; nothing is written wrongly. Keying the clause on how the merge was made, "After `python3 ws.py merge` exited 0", closes both. The Branch row has the same form, from before this change. Verified: the row's text; `_kept` and `retarget` in `wslib/merge.py`, which raise before the deletion. What GitHub does to a stacked pull request after a web merge depends on the repository's settings, and is inferred. | fixed, fix round 1: the row now keys on how the merge ended: when `python3 ws.py merge` exited 0 the retargets are done; when it exited 2, or the merge was made another way such as from the web page, the agent reads each base and asks before a retarget. Verified, read. |

## Checked with no finding

- contradiction: the row's "do not publish one until the person says whether its earlier review stands" matches git-host operations' Retarget row and its rules row, and the helper's own message. The "After a merge made another way" clause keeps the ask-first rule that the 2026-11-22 record's finding 3 added. Verified, read.
- trigger: the page's purpose line, In short line and "When to use it" are unchanged; the list still runs "once a pull request merges". Verified.
- enforcement: the rules row "After a merge, work down the bookkeeping list" stays `prose`, which is true. Verified.
- placement: the row states what the helper already did in one clause and links git-host operations' Retarget row for the rule. Verified, read.
- eval-case: a template carries no proof mark, as decision 0006 says, and the behavior the row asks for is git-host operations' Retarget row, which is `proof: unproven` with `prove-by: M8`. Verified.
