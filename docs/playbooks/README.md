---
kind: reference
last-reviewed: 2026-11-21
---

# Playbooks

Every playbook in this folder, when to use it, and whether it is proven. For an agent or person choosing which procedure to follow.

**In short:** find the row that matches your situation and open its page. The page is the procedure; nothing else replaces it.

## Before you pick one

A request to change something first goes through the [size gate](../size-the-work.md#the-gate). A request that changes nothing by itself, such as reviewing a pull request, walking through review comments, writing a handoff note or tracing why a review missed a defect, skips the gate and goes straight to its row below. A small, easy-to-reverse change in one repository, under a day of work, goes straight to [fix a bug](fix-a-bug.md), whether or not it is a bug; [safe refactor](../safe-refactor.md) states the one exception, a small refactor. A bug starts at fix a bug when you can write a test that fails for the reason in the report. When you cannot yet say what that reason is, start at debugging, which hands back to fix a bug once it finds the cause. Anything else climbs [the ladder](../size-the-work.md#the-ladder), where the decision interview serves the grill rung and adversarial review the red team. For tasks that are not playbooks, such as committing or adding a check, see the [how-to index](../how-tos.md).

## The catalog

Rows run roughly in the order a piece of work meets them: before building, while building, at the commit, review, then after the fix. A review reads committed work, so it comes after the commit that made it. A new playbook adds its row in its stage, in the same commit as the page.

| Stage | Playbook | Use it when | Proof |
|---|---|---|---|
| Before building | [Decision interview](decision-interview.md) | Design questions are still open on work that failed the size gate, after its goal and non-goals are written; or a person asks to be interviewed on a topic. | unproven, M9 |
| Before building | [Throwaway prototype](throwaway-prototype.md) | A question has to be seen running to be answered, such as how state changes step by step or how a screen should look. | unproven, M4 |
| Before building | [Adversarial review](adversarial-review.md) | A finished hand-off plan or requirements document needs a fresh critic to attack it before anyone builds from it; not for diffs or diagnoses. | unproven, M9 |
| While building | [Debugging](debugging.md) | Something fails and you cannot yet say why, so you cannot write a test that fails for the reason in the report. It finds the cause, then hands a small fix on to fix a bug. | unproven, M4 |
| While building | [Fix a bug](fix-a-bug.md) | A change that passes the size gate: small, easy to reverse, in one repository and under a day of work. It is written for a bug whose cause you can pin in a failing test. | proven |
| While building | [Test first](test-first.md) | You are writing code that adds or changes behavior on a route already chosen, such as a slice of a hand-off plan, one failing test at a time. | unproven, M4 |
| While building | [Reuse checklist](reuse-checklist.md) | Before writing new logic, to find code that already does the job; or reviewing a diff for missed helpers and design debt when the request names reuse alone. | unproven, M6 |
| While building | [Impact analysis](impact-analysis.md) | You need everything a change to a path or name reaches: closing the feature ladder, planning slices, or a person asks; not inside fix a bug or safe refactor, which map their own. | unproven, M6 |
| While building | [Handoff](handoff.md) | A session must stop mid-task, such as when its context runs low, and a later session will carry on from a written note. | unproven, M6 |
| At the commit | [The instruction review](instruction-review.md) | Your commit adds, changes or deletes a guidance page: the contract, INDEX.md, the README, or a page under `docs/` other than a plan, a milestone record, a record or the question log. | unproven, M4 |
| Review | [The review orchestrator](review-orchestrator.md) | You are asked for a review of a branch, before its pull request or a later push, or of someone else's pull request. A plain request for "a review" lands here, not on one dimension's page. | unproven, M6 |
| Review | [Architecture review](architecture-review.md) | A diff of code needs checking against what the system has already decided, and whether it solves the right problem; when the request names that question alone, or as a dimension of the review orchestrator. | unproven, M6 |
| Review | [Feedback walk-through](feedback-walkthrough.md) | The author of a pull request wants to go through its review comments one at a time and understand each before anything changes. | unproven, M6 |
| After the fix | [Escape analysis](escape-analysis.md) | A defect is fixed and committed, and a review had covered the code that held it; find why the review missed it. | unproven, M6 |

"unproven, M4" means the page has no proof yet and names M4 as the milestone that is to prove it. See [decision 0006](../decisions/0006-what-proven-means.md). The [README's table](../../README.md#proven-and-unproven-pages) is the one the `proof` check holds to the pages. If this column ever disagrees with a page's front matter, the front matter is right.

## The page is canonical

Each playbook page is the one place its procedure lives. Anything else that starts a playbook stays thin: it says when to use it and points at the page, and never restates or changes its steps.

## Three ways to follow a playbook

The playbook page is the procedure in each case. Only the way you reach it differs.

1. **Read the page and follow it.** Open the page from the table above and work its steps in order. A person running a procedure by hand does this.
2. **Ask the agent in one line.** Name the task and the playbook, such as "find why the export test fails, following the debugging playbook". The agent opens the page and follows it.
3. **Use a wrapper.** A wrapper is a skill an agent tool loads, whose description fires on a matching request and whose body points the agent at the page. None exist yet: slice B6 of M3 adds them, only for procedures that can run today. Until then, use the first two ways.

## Rules

| Rule | Enforced by |
|---|---|
| Every playbook in `docs/playbooks/` has a row here, added in the same commit as the page. No check catches a missing row. | `prose` |
| A wrapper or any other pointer to a playbook stays thin: it never restates or changes the page's steps. Where the two differ, the page wins. | `prose` |
