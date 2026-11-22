---
kind: record
last-reviewed: 2026-11-21
covers: docs/code-review.md
reviewed-at: 9f3de36, with the uncommitted change of the B2 builder
---

# Instruction review: docs/code-review.md

This records the instruction review of the new code review reference page, for its author and for a person whose change an agent reviews.

**In short:** 3 findings: 2 contradiction, 1 placement. The page agrees with the review orchestrator on the labels, the posting rule and the fix a bug exception. It restates two of the playbook's rules more broadly than they hold, and it carries numbered steps on a reference page.

## Scope

In scope: the whole page, a new file. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md` (with its diff), and the pages it links to: `docs/playbooks/review-orchestrator.md`, `docs/playbooks/fix-a-bug.md`, `docs/review-in-a-worktree.md` and `docs/playbooks/feedback-walkthrough.md`. Also read the other batch 3 pages: `docs/playbooks/architecture-review.md`, `docs/playbooks/reuse-checklist.md`, `docs/playbooks/impact-analysis.md`, `docs/playbooks/escape-analysis.md`, `docs/playbooks/handoff.md`, and `git diff` of the edited pages, including the how-to index row this page gets in `docs/how-tos.md`. Ran `python3 ws.py rules`, `python3 ws.py check` and `gh pr review --help`.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | What runs, against the definition of done | The page says "a new warning in a file the change touches" stops the review. The definition of done's list says to compare warnings with the base branch and count every new one, with no limit to changed files. A change that makes unchanged callers warn, such as a deprecation, passes this review's pre-pass but fails the definition of done. The page labels no exception. It copies the same narrowing from the review orchestrator's step 4. Verified: read "What runs" and the definition of done's second row. Cause: pass-contradiction-skipped — the brief requires reading the definition of done in the contradiction pass, and the narrowing survived it. | fixed: What runs now says any new error or warning stops the review, as the definition of done counts them. |
| 2 | contradiction | On your own branch, item 4, against the review orchestrator's steps 2 and 6 | Item 4 says the next round "reviews only what changed since the last one". The orchestrator's step 6 sends the code dimension over the whole branch again on a delta round before the pull request opens. Its step 2 runs a full round when no complete earlier review is found, and before a pull request opens with no plan, step 10 leaves the record only in a report. So a person told to expect a delta often gets a full review. Verified: read item 4 and the orchestrator's steps 2, 6 and 10. Cause: restated-not-linked — the brief says to prefer linking to restating, and the restatement dropped the playbook's conditions. | fixed: item 4 no longer restates the delta rule; it links to the review orchestrator's steps for what the next round reads. |
| 3 | placement | On your own branch, and On someone else's pull request | Both sections are numbered steps a person follows: ask, read, settle, ask again; ask, wait, read and answer. Layout defines a `reference` page as "Facts to look up, not steps", and a `how-to` as "Steps for one task, for a person or an agent", which carries a `proof` key. As a reference page, these steps sit outside the proof mark that every other page of steps carries. Verified: read the page's front matter and layout's page kinds table. Cause: brief-silent-on-kind-fit — the brief takes each page's kind as assigned and never asks the builder to check the content against its kind's row in layout. | declined: the M3 plan's B2 row assigns the explainer the reference kind with no proof field; its short lists point a person at the playbook, which holds the procedure and its proof mark. |

## Checked with no finding

- step: each numbered item names what the person does and what comes back. The reply table under "When you receive a review" matches the feedback walk-through's rule that a fix reply waits until its commit is pushed. "It posts under your own sign-in" matches `gh pr review`, which posts as the signed-in `gh` user.
- trigger: the purpose line and **In short** match the content. The how-to index row in "Finishing" exists. Routes in come from the review orchestrator's opening and architecture review's "When it runs", each naming its condition. The page sends a person to the feedback walk-through on a stated condition, and to the contract for opening and merging.
- enforcement: every must and never on the page has a row in its Rules table, each tagged `prose`, which is true: no part checks them.
- eval-case: a reference page needs no proof key. The agent behavior it describes is the review orchestrator's, which is `proof: unproven`, `prove-by: M6`.
- Also checked, with no defect: the five always-run dimensions and the two advisory ones match the orchestrator's dimensions table. The kind rule, the fix a bug exception and the "What is planned" milestones match the orchestrator. `python3 ws.py check` reports nothing for this page.
