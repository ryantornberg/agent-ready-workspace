---
kind: record
last-reviewed: 2026-11-28
covers: docs/playbooks/git-host-operations.md
reviewed-at: 176642f, with the uncommitted change of the G1 builder
---

# Instruction review: docs/playbooks/git-host-operations.md

This records the instruction review of M4 slice G1's change to git-host operations, for its author and any agent acting on a pull request.

**In short:** 1 finding, 1 blocking: 1 contradiction. The page now says the merge helper retargets stacked pull requests itself, while its own rules say a write on a pull request nobody asked about always needs a yes, and it labels no exception.

## Scope

In scope: the uncommitted diff against 176642f, which adds one sentence to the operations table's Retarget row: "A merge with `python3 ws.py merge` retargets each open pull request based on the merged branch itself, and names each; the rest of this row still holds for each one." Read with it: the whole page, in particular "Which writes need a yes", step 3, the "Publish and merge" row and the rules table. Read beside it: `AGENTS.md`; `INDEX.md`; `docs/changing-the-machinery.md` and `docs/templates/pull-request.md`, with their changes; `docs/procedure-endings.md`'s outward writes; the earlier record [2026-11-22-b3-pull-request.md](2026-11-22-b3-pull-request.md), whose finding 3 added "Ask first" to the template's stacked-branches row; the plan `docs/plans/m4-fail-closed-guards-review-loop-and-evals.md`, row G1, Q84 and success criterion 3. Code read: `git diff origin/main..HEAD -- wslib/merge.py`.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | The operations, the Retarget row; Which writes need a yes; Rules, the ask-first row | Blocking. "Which writes need a yes" says "Always ask first for: a pull request nobody asked about; another person's pull request", and that none of these follows from a request that names something wider. The rules table repeats it. The new sentence says `python3 ws.py merge` retargets each open pull request based on the merged branch, which the merge request did not name and which may be another person's. The page does not label this as an exception, and "the rest of this row still holds for each one" can be read to include the row's own "Ask first", which a write already made cannot follow. An agent asked to merge pull request N either merges and so retargets others without the yes the page requires, or stops to ask about a write the helper makes unasked. Q84 settled that the helper retargets. What the page lacks is a labelled exception in "Which writes need a yes", saying whether a merge request is the yes for the helper's retarget, another person's pull request included, or a step that lists the stacked pull requests and asks before the merge. Verified: the quoted text; `retarget` and `parse_dependents` in `wslib/merge.py`, which move every open pull request based on the branch whatever its author. | fixed, fix round 1: "Which writes need a yes" gains a labelled exception, in this repository only: the retarget `python3 ws.py merge` makes of the pull requests stacked on the branch it merges, on the maintainer's answer to Q84; the request to merge is its yes, another person's pull request included, and every other retarget, a manual one after the helper failed included, follows the rules. The Retarget row names the exception and says the review question holds for every retarget; the rules table's ask-first row names it too. No ask step was added, by the coordinator's ruling. Verified, read. |

## Checked with no finding

- step: the Retarget row's command, `gh pr edit NUMBER --base BRANCH`, is unchanged and exists. "Names each" matches the helper, which prints "Retargeted #N (HEAD) from BRANCH to BASE" for each, with the instruction not to publish it until the person says whether its review stands. Verified: `retarget` in `wslib/merge.py`.
- trigger: the purpose line, the In short line and the routing table are unchanged; `INDEX.md` still routes "retargeting" here. Verified.
- enforcement: the new sentence adds no must or never; the rules table's row that a retargeted pull request is not published until the person says whether its review stands stays `prose`, which is true, since no part checks it. Verified.
- placement: the sentence states the helper's behavior in one clause and leaves the detail to changing the machinery, which the "Publish and merge" row links. Verified, read.
- eval-case: the page is `proof: unproven` with `prove-by: M8`. Verified.
