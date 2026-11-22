---
kind: record
last-reviewed: 2026-11-21
covers: docs/playbooks/adversarial-review.md
reviewed-at: 9f3de36, with the uncommitted change of the B2 builder
---

# Instruction review: docs/playbooks/adversarial-review.md

This records the instruction review of batch 3's edit to the adversarial review playbook, for its author and for critics.

**In short:** 1 finding: 1 trigger. A diff sent away from this page goes only to architecture review, and the review orchestrator's tie-break for a general review of a diff is not named.

## Scope

In scope: the batch 3 edit to "When it runs", its second paragraph, which sends a diff of code whose design is in question to architecture review, and anything on the page it contradicts or leaves stale, including step 1's fit check and "Rules". Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md`, the linked pages architecture review, instruction review, decision interview and size the work, and the other batch 3 pages (review orchestrator, code review, reuse checklist, the playbook catalog diff). Ran `git diff docs/playbooks/adversarial-review.md` and `python3 ws.py check` (no finding on this page).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | "When it runs", second paragraph | The page says it does not fit a diff, then routes a diff only when "the question is whether its design is sound", to architecture review. A request to review or attack a branch or pull request in general gets no route here. The review orchestrator's "When it runs, and which page wins" says that when a request asks for "a review" of a branch or pull request, the orchestrator wins and runs architecture review as one dimension. An agent that lands here with such a request is either sent to architecture review alone or left with no page. Verified: read this paragraph, the orchestrator's tie-break table and architecture review's "When it runs". Cause: `route-in-names-one-of-several` — the brief asks a page to say which wins where two playbooks could fire, but the route-in sentence was written for one new page and names one target where three batch 3 pages share the diff case. | fixed: the route-in sentence now sends a review of a branch or pull request to the review orchestrator and a question about design alone to architecture review. |

## Checked with no finding

- contradiction: the edit agrees with architecture review's "When it runs" (a plan or requirements document goes to adversarial review; a diff of code goes there), and with the review orchestrator's tie-break row that sends a plan or requirements document here. Step 1's fit check still refuses a diff.
- step: the edit adds no step; step 1's "If it does not fit ... stop and report why" still ends the branch.
- enforcement: the edit adds no must or never; the Rules table is unchanged and still true.
- placement: the routing sentence sits in "When it runs", beside the existing instruction review route.
- eval-case: the page is `proof: unproven`, `prove-by: M9`, so the new behavior needs no case yet.
