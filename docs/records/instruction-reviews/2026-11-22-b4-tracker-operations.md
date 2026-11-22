---
kind: record
last-reviewed: 2026-11-22
covers: docs/playbooks/tracker-operations.md
reviewed-at: 31f9aaa, with the uncommitted change of the B2 builder
---

# Instruction review: docs/playbooks/tracker-operations.md

Review of the new tracker operations playbook from M3 slice B2, batch 4, for its author and the agents that act on work items.

**In short:** 4 findings: 1 contradiction, 2 step, 1 enforcement. The page routes well and marks its planned machinery honestly, but it never says whether a named write or an always-ask write wins, its draft mode has no way through step 2, and the security review's inputs have no defaults.

## Scope

The whole page, which is new. I read it in full, and beside it `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md` with its batch diff, `docs/changing-the-machinery.md`, `docs/size-the-work.md`, `docs/research-ladder.md`, `docs/review-in-a-worktree.md`, `docs/playbooks/fix-a-bug.md`, and the batch's pages it links or shares rules with: `docs/playbooks/git-host-operations.md`, `docs/playbooks/search-every-source.md`, `docs/playbooks/review-orchestrator.md`, `docs/playbooks/feedback-walkthrough.md` and `docs/extend-the-workspace.md`. I ran `python3 ws.py check` (no finding on this page), `python3 ws.py rules`, `gh pr view 36 --json state,mergeCommit` (returns `MERGED` and the merge commit's oid) and `git diff MERGE^1 MERGE --stat` on that merge commit (shows the merged change), all read-only.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Which writes need a yes; The post-merge security review, step 5 | The page says a write the request names needs no further yes, and also says to always ask first for another person's item, rejecting or closing a parent. It never says which wins when a named write is on the always-ask list, and step 3's default covers only "cannot tell whether named". Security review step 5 then closes the review sub-task without asking, though the same step assigns that sub-task to someone else, which makes it another person's item. Verified by reading the section, step 3 and security review step 5. Cause: sheet-silent-on-precedence — section 4 of the interface sheet states the named-write rule and the always-ask list side by side with no precedence, and the page copies both. | fixed: added a precedence paragraph and rules wording (a named write is its yes; none counts as housekeeping), and the security review now closes the sub-task before any reassignment, which comes last and only on a yes. |
| 2 | step | Steps, steps 1 and 2 | Step 1 sets draft mode when the session has no tracker tool or its read fails. Step 2 then reads each item's type, status, fields and sub-tasks with no way to do so in draft, and gives no default, such as asking the person for the item's state. Steps 3 to 5 and the security review's input all depend on that read. Verified by reading steps 1 to 5. Cause: pass-step-skipped — the brief's step pass asks every step to name where its input comes from, and step 2 has no input source in draft. | fixed: step 2 now takes step 1's mode and, in draft, asks the person to paste each item's state, going to step 7 with no answer. |
| 3 | step | The post-merge security review, steps 1 and 5 | Step 1's input is "the pull request the item names", but step 2 of the steps does not read linked pull requests. Neither step gives a default when the item names no pull request, names several, or names one in a repository that is neither this one nor pinned under `src/`, where `git fetch origin` cannot reach the merge commit. Step 5 posts on "the item's own security review sub-task" with no default when there is none. Verified by reading both sections. Cause: pass-step-skipped — the brief's step pass asks for a defined input and a default for every decision. | fixed: step 2 reads linked pull requests; security steps 1 and 5 give defaults for none, several, out-of-scope repositories, unmerged ones and a missing review sub-task. |
| 4 | enforcement | The post-merge security review, step 3; Rules | Two musts have no row in the rules table: "A new suppression is always a finding" and "A finding that needs a code change is reported, not fixed in this run". Verified by reading the page and its rules table. Cause: pass-self-review-skipped — the brief's self-review asks for every must, never, always and only to be listed against the rules table. | fixed: added rules rows for the always-a-finding suppression and for reporting, not fixing, a code finding. |

## Checked with no finding

- Trigger: the purpose and In short lines fire on a request that acts on a work item, and the routing table's rows agree with git-host operations, search every source, the review orchestrator and the feedback walk-through on who takes which request. The catalog row in `docs/playbooks/README.md` matches, and the review orchestrator's machinery table routes in on a tracker request.
- Placement: field ids and per-team traps are kept off the page and named as M8's trap table and schema file; the security review sits here as section 9 of the sheet assigns it. Nothing goes in the always-loaded layer.
- Eval-case: the page is marked unproven with `prove-by: M8`.

## Re-check

A fresh session re-read the page on 2026-11-22, after the fix round.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | "Which writes need a yes" now says a request naming an always-ask write in its own words is its yes and none counts as housekeeping, and security review step 5 closes the sub-task before any reassignment; verified by reading both. |
| 2 | fixed | Step 2 now takes step 1's mode and, in draft, asks the person to paste each item's state, going to step 7 with no answer; verified by reading steps 1, 2 and 6. |
| 3 | fixed | Step 2 reads linked pull requests, and security steps 1 and 5 give defaults for none, several, out-of-scope, unmerged and a missing sub-task; verified by reading both sections. |
| 4 | fixed | The rules table now has rows for the always-a-finding suppression and for reporting, not fixing, a code finding; verified by reading the table. |

Broke: none.
Missed:
- Steps, step 7 and the stop line: the page adds a question-log entry but "commits nothing", while docs audit, prompt retrospective and maintain commit that entry; verified by reading all four.
- The post-merge security review, step 5, and the operations row: a review sub-task already assigned to someone else is another person's item, yet its comment and close count as named; inferred.

## Batch 5's fix round

The builder's one fix round on the re-check's items, on 2026-11-22. A fix that touched a rule several pages share changed every page holding it: how a question-log entry is committed now lives on [the question log](../../question-log.md) and the other pages link it; who pushes follows [changing the machinery](../../changing-the-machinery.md#the-path-for-a-machinery-change).

| Item | Disposition |
|---|---|
| Missed: no commit path for the question-log entry | fixed: step 7 commits it as the log's page says, the stop line excepts it, and a rules row holds it. |
| Missed: a comment on another person's review sub-task counts as named | fixed: the operations row and the security review's step 5 make the comment and the close ask-first when the sub-task is assigned to another person. |

## Second re-check

A fresh session re-read the page on 2026-11-22, after batch 5's fix round.

| Item | Verdict | Evidence |
|---|---|---|
| Missed: no commit path for the question-log entry | fixed | Step 7 adds the entry before the report and commits it as the log's page says, the stop line excepts it, and a rules row holds it; verified by reading the page and the question log's "Adding an entry". |
| Missed: a comment on another person's review sub-task counts as named | fixed | The operations row makes the result comment and the close ask-first when the sub-task is assigned to another person, and the security review's step 5 posts and closes it only on step 4's yes; verified by reading both. |

Broke:
- The post-merge security review, step 5, with Steps, step 4: the result comment, now ask-first, is asked about in step 4 "with the new value", but the review that writes it runs inside step 5, so the person approves text they cannot see; verified by reading steps 4 and 5 and the section's "This section runs inside step 5".

Missed: none.
