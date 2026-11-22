---
kind: record
last-reviewed: 2026-11-22
covers: docs/playbooks/feedback-walkthrough.md
reviewed-at: 31f9aaa, with the uncommitted change of the B2 builder
---

# Instruction review: docs/playbooks/feedback-walkthrough.md

Review of the route-in sentence M3 slice B2, batch 4, added to the feedback walk-through's Posting section, for its author and its agents.

**In short:** 1 finding: 1 contradiction. The new sentence is sound, but the paragraph it extends lets an agent post on a repository outside the workspace's list on the author's yes, which git-host operations says is never done.

## Scope

In scope: the sentence added at the end of the Posting section, and anything on the page it contradicts or leaves stale. I read the whole page and its batch diff, and beside it `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md`, `docs/changing-the-machinery.md`, and the batch pages it shares rules with: `docs/playbooks/git-host-operations.md`, `docs/playbooks/review-orchestrator.md` and `docs/playbooks/tracker-operations.md`. I ran `python3 ws.py check`, with no finding on this page.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Posting, the paragraph under the table | The paragraph the edit extends says that on a repository not in the workspace's list, the planned guard will refuse a post, and "until then only the author's yes holds it": with a yes, the post goes out today. Git-host operations, which the new sentence now sends readers to, says a write to a repository other than this one and those pinned under `src/` is never made, and the review orchestrator's step 11 says never to post on one. Verified by reading all three pages. Cause: route-in-edit-scope-too-narrow — the brief lets a builder edit only the one route-in sentence on an existing page, so the paragraph beside it, which the sheet's outward-write rule now contradicts, was left as it was and not reported. | fixed: Posting now states section 4's rule, that a write to a repository other than this one and those pinned is never made, even with a yes; a rules row was added. |

## Checked with no finding

- Step: the new sentence names its condition (the round needs more than replies, such as a description update, a retarget or a CI read) and its page; the rest of the steps are unchanged.
- Trigger: the edit adds no purpose, In short or routing-table text; git-host operations' routing table sends answering comments back here, so the two do not compete.
- Enforcement: the sentence adds no must or never; the rules rows are unchanged.
- Placement: the sentence sits in the Posting section, which section 8 of the batch's interface sheet names as the route in for git-host operations.
- Eval-case: the page is marked unproven with `prove-by: M6`.

## Re-check

A fresh session re-read the page on 2026-11-22, after the fix round.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | Posting now says a write to a repository other than this one and those pinned under `src/` is never made, even with a yes, and a rules row says the same, matching git-host operations and the orchestrator's step 11; verified by reading all three. |

Broke:
- Posting, the paragraph under the table: "until it exists, only this rule and the author's yes hold it" names a yes as a hold on a write the sentence before forbids even with one; verified by reading it.

Missed:
- Steps, step 8 and Posting: step 8 has the agent run `git push` on the author's yes, while Posting and git-host operations say a person pushes in a team's workspace; verified by reading them.
