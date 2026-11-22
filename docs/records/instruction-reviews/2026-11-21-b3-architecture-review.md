---
kind: record
last-reviewed: 2026-11-21
covers: docs/playbooks/architecture-review.md
reviewed-at: 9f3de36, with the uncommitted change of the B2 builder
---

# Instruction review: docs/playbooks/architecture-review.md

This records the instruction review of the new architecture review playbook, for its author and for agents who follow it.

**In short:** 3 findings: 2 contradiction, 1 step. The steps, the invariants and the big-picture pass run as written, but the reply's ending and the posting rule disagree with the review orchestrator, and step 1 gives no source for the request outside a plan.

## Scope

The whole page was in scope, since it is new. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md`, and the pages it links to: `docs/changing-the-machinery.md`, `docs/playbooks/review-orchestrator.md`, `docs/playbooks/adversarial-review.md`, `docs/playbooks/instruction-review.md`, `docs/code-review.md`, `docs/playbooks/reuse-checklist.md`, `docs/playbooks/test-first.md`, `docs/playbooks/escape-analysis.md`, `workspace.json` and `docs/decisions/`. Read the other pages of batch 3 for statements about this page: `docs/review-in-a-worktree.md`, `docs/playbooks/impact-analysis.md`, `docs/playbooks/feedback-walkthrough.md`, `docs/playbooks/handoff.md`, and the edits to `docs/playbooks/README.md`, `docs/glossary.md` and `README.md`. Ran `python3 ws.py rules`, `python3 ws.py check`, `grep -l "status: accepted" docs/decisions/*.md`, `python3 tools/symbols.py AccountFreeze src` and `git grep -n AccountFreeze`, and opened `parts/shelved.cases.json` and `parts/handoff_tier.cases.json`.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | The reply; When it runs, first bullet | The page says the reviewer replies with the table, then the two closing lines, "and nothing else". When the review orchestrator dispatches it, that page's template ends the reply with `Dimension complete: <dimension>`, and its step 7 counts a reply complete only when it ends with that line. A reviewer that obeys this page fails the orchestrator's completion test and is dispatched again. The page says only the orchestrator's table replaces this one, not that the extra line follows. Verified: read "The reply" here and the dispatch template and step 7 of `docs/playbooks/review-orchestrator.md`. Cause: contradiction-pass-skipped — the brief required reading every page of the batch and checking each statement against them, and this clash is between two batch pages. | fixed: when it runs and the reply now say the orchestrator's Dimension complete line follows the two closing lines when it dispatched the review. |
| 2 | contradiction | Steps, step 6; Rules | Step 6 lets the session post findings on a pull request on the person's yes, with no limit on where. The review orchestrator, for the same outward write, never posts on a pull request outside this repository and the repositories it pins, even with a yes, and hands the person the draft instead. A standalone architecture review of an outside pull request would post where the orchestrator forbids it. Verified: read step 6 and the Rules table here, and step 11 and the Rules table of `docs/playbooks/review-orchestrator.md`. Cause: shared-rule-restated-not-linked — the brief says a rule on two pages must say the same thing and to prefer linking, and this page restated the posting rule without the orchestrator's repository limit. | fixed: step 6 and the rules row now post only where the review orchestrator's step 11 allows, this repository or one pinned under src/, and otherwise hand the findings to the person. |
| 3 | step | Steps, step 1; The template | Step 1 outputs "the request, word for word, from the person or the plan", and the template needs it. For someone else's pull request, or a branch with no plan, the request the change answers is in neither place, and the step names no other source and no default. The big-picture pass depends on this text. The review orchestrator's step 5 gives the fallbacks this step lacks: the issue, the pull request's description, then the commit messages. Verified: read step 1 and the template here and step 5 of `docs/playbooks/review-orchestrator.md`. Cause: step-pass-skipped — the brief's step pass requires each input to say where it comes from and each decision a default, and step 1 borrows the tip and base from the orchestrator but not its request sources. | fixed: step 1 now takes the request from the sources and default of the review orchestrator's step 5, ending with the commit messages. |

## Checked with no finding

- trigger: the purpose and In short lines match the steps; "When it runs" names which page wins against the orchestrator, adversarial review, the instruction review, code review and the reuse checklist, each with its condition; the playbook catalog lists the page, and the review orchestrator, adversarial review, escape analysis and the glossary route in.
- enforcement: every must and never on the page has a Rules row; `handoff_tier#no tier named` and `shelved#an edit inside the shelved folder` exist in `parts/handoff_tier.cases.json` and `parts/shelved.cases.json` and show their rules; the rest are `prose`.
- placement: the invariants and misframing tables belong on this page, which escape analysis and the glossary point to; nothing here belongs in the always-loaded layer.
- eval-case: the page is marked `proof: unproven` with `prove-by: M6`, its big-picture pass carries the section mark in the form decision 0006 sets, and the README's proof table lists both.
