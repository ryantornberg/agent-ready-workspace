---
kind: record
last-reviewed: 2026-11-22
covers: docs/playbooks/git-host-operations.md
reviewed-at: 31f9aaa, with the uncommitted change of the B2 builder
---

# Instruction review: docs/playbooks/git-host-operations.md

Review of the new git-host operations playbook from M3 slice B2, batch 4, for its author and the agents that act on pull requests.

**In short:** 5 findings: 3 contradiction, 1 step, 1 enforcement. Its commands run as written, but it disagrees with two pages on who pushes in a team's workspace, sends a retargeted pull request to a review that stops at once, and leaves the named-versus-always-ask precedence open.

## Scope

The whole page, which is new. I read it in full, and beside it `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md` with its batch diff, `docs/changing-the-machinery.md`, `docs/size-the-work.md`, `docs/research-ladder.md`, `docs/review-in-a-worktree.md`, `docs/playbooks/fix-a-bug.md`, and the batch's pages it links or shares rules with: `docs/playbooks/tracker-operations.md`, `docs/playbooks/search-every-source.md`, `docs/playbooks/review-orchestrator.md`, `docs/playbooks/feedback-walkthrough.md` and `docs/extend-the-workspace.md`. Read-only, I ran `python3 ws.py check` (no finding on this page), `python3 ws.py rules` (the `no_admin_merge` and `eval:fix-a-bug` tags exist), `gh auth status` (exit 0), `gh pr list --head m3/c5c --state all --json number,state,isDraft,baseRefName`, `gh pr view 36 --json number,state,isDraft,baseRefName,headRefName,title,url` and `gh pr checks 36` (links hold `/runs/<id>`). I read the help of `gh pr checks` (exit 8 means pending), `gh run view` (`--log-failed` exists) and `gh pr create` (`--draft`, `--base`, `--body-file` exist) instead of running the writes.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Which writes need a yes; Steps, step 3 | The page says a write the request names needs no further yes, and also says to always ask first for another person's pull request and for any post on one. It never says which wins when a request names such a write, such as "reply to the reviewer on pull request 42". Step 3's default covers only "cannot tell whether named". The retarget row's "unless the request names it" suggests named wins, but the always-ask list says otherwise. Verified by reading the section, step 3 and the operations table. Cause: sheet-silent-on-precedence — section 4 of the interface sheet states the named-write rule and the always-ask list side by side with no precedence, and the page copies both. | fixed: added the same precedence paragraph as tracker operations, and the rules row now says a named write is its yes and none counts as housekeeping. |
| 2 | contradiction | The operations, Create a pull request | The row has the agent push the branch whenever the request names it, in any workspace. Changing the machinery, step 5, says "in a team's workspace, a person does" push, and the feedback walk-through's Posting section says "In a team's workspace, a person pushes." In an instance, an agent following this page pushes where the other two pages say a person does. Verified by reading all three pages. Cause: sheet-silent-on-push — section 4 of the interface sheet settles who publishes in a team's workspace but not who pushes, which two existing pages already settle. | fixed: the Create row now says a person pushes in a team's workspace, as changing the machinery says, and the agent gives the command; a rules row was added. |
| 3 | contradiction | The operations, Retarget | The row says a review recorded for the old range no longer counts after a retarget, so run the review orchestrator again. A retarget keeps the same tip, and the orchestrator's step 2 stops at once when "this tip has a complete review", judging by the tip alone. The rerun the row asks for never reviews the new range. Verified by reading the row and the orchestrator's step 2. Cause: handoff-not-traced-through-target-steps — the brief's contradiction pass compares statements, and does not ask the builder to follow a hand-off through the target page's steps to see that it does what the sender expects. | fixed: the Retarget row no longer reruns the orchestrator; it holds publishing until the person says whether the earlier review stands, as orchestrator step 2 does for a moved branch. |
| 4 | step | Steps, step 6 | Step 6 reads back `state,isDraft,baseRefName,title,url` only. A description update and a push, both writes on the operations table, cannot be compared with what was meant, though the rules table says to read the pull request again after each write to confirm it. Verified by reading step 6, the operations table and the rules table; `gh pr view --json` also offers `body` and `headRefOid`. Cause: pass-step-skipped — the brief's step pass asks each step's output to show it did what it says, and step 6 cannot confirm two of the writes. | fixed: step 6 now reads body and headRefOid too, comparing the body with the file sent and headRefOid with git rev-parse HEAD after a push. |
| 5 | enforcement | The operations, Create a pull request; Rules | "If it does not, stop and run the review orchestrator first", the page's only hold on a review before a pull request until M4's gate, has no row in the rules table. Verified by reading the row and the table. Cause: pass-self-review-skipped — the brief's self-review asks for every must, never, always and only to be listed against the rules table. | fixed: added a rules row: a pull request opens only once the review its sending page or plan asks for is on record for its tip. |

## Checked with no finding

- Trigger: the purpose and In short lines fire on creating, updating or reading a pull request or its CI. The routing table agrees with tracker operations, search every source, the review orchestrator and the feedback walk-through, and the catalog row matches. The feedback walk-through's Posting section routes in, and the review orchestrator does not link here, as the sheet's tie-break says.
- Placement: GitHub traps sit in their own table, the merge command stays on changing the machinery, and per-host trap tables are named as M8's. Nothing goes in the always-loaded layer.
- Eval-case: the page is marked unproven with `prove-by: M8`.

## Re-check

A fresh session re-read the page on 2026-11-22, after the fix round.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | "Which writes need a yes" now says a request naming an always-ask write in its own words is its yes and none counts as housekeeping, and the rules row says the same; verified by reading both. |
| 2 | fixed | The Create row and a new rules row say a person pushes in a team's workspace and the agent gives the command, matching changing the machinery step 5; verified by reading both pages. |
| 3 | fixed | The Retarget row no longer reruns the orchestrator; it holds publishing until the person says whether the earlier review stands, as orchestrator step 2 does for a moved branch; verified by reading both. |
| 4 | fixed | Step 6 now reads `body` and `headRefOid` and says what to compare each with; verified by reading the step and running `gh pr view 36 --json body,headRefOid,baseRefName`, which returned both fields. |
| 5 | fixed | Rules row "Open a pull request only once the review its sending page or plan asks for is on record for its tip" now exists; verified by reading the table. |

Broke:
- The operations, Create a pull request: "push it as the page that sent you says", but fix a bug's step 5, a named sending page, says nothing about pushing; verified by reading it.

Missed:
- Steps, step 7 and the stop line: the page adds a question-log entry but "commits nothing", while docs audit, prompt retrospective and maintain commit that entry; verified by reading all four.

## Batch 5's fix round

The builder's one fix round on the re-check's items, on 2026-11-22. A fix that touched a rule several pages share changed every page holding it: how a question-log entry is committed now lives on [the question log](../../question-log.md) and the other pages link it; who pushes follows [changing the machinery](../../changing-the-machinery.md#the-path-for-a-machinery-change).

| Item | Disposition |
|---|---|
| Broke: Create pushes "as the sending page says" | fixed: the Create row says pushing is part of a request to open the pull request: an agent may push in this repository, and a person pushes in a team's workspace. |
| Missed: no commit path for the question-log entry | fixed: step 7 commits it as the log's page says, the stop line excepts it, and a rules row holds it. |

## Second re-check

A fresh session re-read the page on 2026-11-22, after batch 5's fix round.

| Item | Verdict | Evidence |
|---|---|---|
| Broke: Create pushes "as the sending page says" | fixed | The Create row no longer defers to the sending page: pushing is part of the request, an agent may push here with `git push -u origin HEAD`, and a person pushes in a team's workspace, matching changing the machinery's step 5; verified by reading both. |
| Missed: no commit path for the question-log entry | fixed | Step 7 adds the entry before the report and commits it "as that page says", the stop line excepts it, and a rules row holds it, matching the question log's "Adding an entry"; verified by reading both. |

Broke:
- The operations, Create a pull request: removing "the page that sent you" left "When that page or the plan asked for a review" with changing the machinery as its only antecedent; verified by reading the row and its diff.

Missed:
- The operations, Create a pull request: `git push -u origin HEAD` and `gh pr create` without `--head` both act on the checked-out branch, while step 2 accepts a branch the request names, and no step checks they match; verified by reading and `gh pr create --help` (head defaults to the current branch).
