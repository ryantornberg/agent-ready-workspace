---
kind: reference
last-reviewed: 2026-11-24
---

# Lifecycle map

Each stage of software delivery, the pages that guide it here, and the stages with no page yet. For anyone judging what the workspace covers.

**In short:** the workspace is deepest from sizing to review, and one playbook there is proven. Requests, release, deployment and learning are drafts or planned. Monitoring and on-call are not covered, and the row says why. Find your stage in the first table, or your topic in the second.

## How to read it

The first table runs in the order a change meets each stage. The second lists topics that cut across every stage.

Each row's State cell uses these four words. A row whose pages differ names the state of each.

| State | Meaning |
|---|---|
| Proven | A page has a real run on record and an eval it wins, as [decision 0006](decisions/0006-what-proven-means.md) says. |
| Draft | Pages exist. Each playbook and how-to among them is marked unproven, and the milestones named are the ones that run them on real work. Reference pages and templates carry no proof state. |
| Planned | No page exists yet. The row names what is to be built, and the milestone that builds it. |
| Not covered | No page exists and none is planned. The row says why. |

This page does not own any page's proof state. Each page's front matter does, and the [README's table](../README.md#proven-and-unproven-pages) lists them all. To pick a procedure, use the [playbook catalog](playbooks/README.md) or the [how-to index](how-tos.md). For the pages one role reads first, use [reading paths by role](reading-paths.md).

## By stage

| Stage | Pages here today | State | Planned |
|---|---|---|---|
| Request and readiness | [Bug report template](templates/bug-ticket.md), [bug grooming](playbooks/bug-grooming.md), [bug triage meeting](playbooks/bug-triage-meeting.md), [triage labels](triage-labels.md) | Draft, M9. Bugs only. | A door for a new request from outside development, and a check that a work item is ready to build, in M9. |
| Sizing | [The size gate](size-the-work.md#the-gate) | Draft, M9 | Nothing more. |
| Design and plan | [Decision interview](playbooks/decision-interview.md), [throwaway prototype](playbooks/throwaway-prototype.md), [the spec process](size-the-work.md#the-spec-process), [hand-off plan template](templates/hand-off-plan.md), [red team review](playbooks/red-team-review.md), [effort estimate](playbooks/effort-estimate.md), [feature layer walk](playbooks/feature-layer-walk.md) | Draft, M4 and M9 | A question in the spec on the data a change touches and who can reach it, in M9. |
| Build | [Fix a bug](playbooks/fix-a-bug.md), [debugging](playbooks/debugging.md), [test first](playbooks/test-first.md), [safe refactor](safe-refactor.md), [reuse checklist](playbooks/reuse-checklist.md), [impact analysis](playbooks/impact-analysis.md), [handoff](playbooks/handoff.md) | Proven: fix a bug. Draft, M4 and M6: the rest. | Nothing more. |
| Local environment | [Environment self-check](environment-self-check.md), [browsers](browsers.md) | Draft, M6 and M11. The first checks an environment and the second isolates a browser. Nothing here builds an environment. | One command that gives each working copy its own environment, in M5. |
| Test | [Test first](playbooks/test-first.md), [QA verification list](playbooks/qa-verification-list.md), [QA test plan template](templates/qa-test-plan.md), [regression run](playbooks/regression-run.md), [regression triage](playbooks/regression-triage.md) | Draft, M4, M6 and M10 | A check that a new test fails on the code before the fix, in M6. |
| Review | [Review orchestrator](playbooks/review-orchestrator.md), [code review](code-review.md), [architecture review](playbooks/architecture-review.md), [review in a worktree](review-in-a-worktree.md), [feedback walk-through](playbooks/feedback-walkthrough.md) | Draft, M6 | A review mark, and a gate that needs one before a pull request opens, in M4. |
| Pull request and merge | [Git-host operations](playbooks/git-host-operations.md), [pull request template](templates/pull-request.md), [commits](commits.md), [procedure endings](procedure-endings.md), [tracker operations](playbooks/tracker-operations.md) | Draft, M8 | Scripts that do the bookkeeping after a merge, in M6 and M8. |
| Release | None | Planned | Release notes drafted from the records, in M9. A release playbook with a person's approval, in M11. |
| Deploy and rollback | [Ship a new deployable](ship-a-deployable.md) | Draft, M11. It covers a new deployable, not a release of an existing one. | An environment map, a pipeline, a smoke check and one rehearsed rollback, in M11. The rollback rule covers a release that changed a database schema. |
| Incident response | None | Planned | One incident drill on a sandbox, with a runbook, in M11. |
| Monitoring and on-call | None | Not covered | Nothing. The workspace runs no live product to prove a procedure on. |
| Learn | [Defect escape analysis](playbooks/escape-analysis.md), [question log](question-log.md), [records](records/README.md), [prompt retrospective](playbooks/prompt-retrospective.md) | Draft, M6 and M10 | A miss found by escape analysis becomes an eval case, once the eval system for procedures exists, in M4. |

## Across every stage

| Topic | Pages here today | State | Planned |
|---|---|---|---|
| Security | Security is one side of every [code review](code-review.md), which the [review orchestrator](playbooks/review-orchestrator.md) runs. [Agent settings](agent-settings.md) keeps secrets from an agent. [Tracker operations](playbooks/tracker-operations.md#the-post-merge-security-review) holds the review after a merge. [Checking a shelved predecessor](predecessor-check.md) is for a major security bug. | Draft, M6, M8 and M9 | The design-time question named under "Design and plan". No threat-modeling procedure is planned. |
| Dependency updates | None | Planned | Update pull requests from the git host's own bot, sorted by what an agent may take unasked, in M10. |
| Schema and data changes | [The size gate](size-the-work.md#the-gate) sends any change with a data migration up the ladder. | Draft, M9 | The rollback rule named under "Deploy and rollback", in M11. |
| Unattended work | [Orchestration](orchestration.md), [saved workflows](saved-workflows.md), [decision 0018](decisions/0018-unattended-runs-write-only-to-a-branch.md) | Draft, M4 and M10 | A register of every job that runs unattended, with its limits, in M10. |
| Finding code and pages | [Research ladder](research-ladder.md), [federated search](playbooks/search-every-source.md) | Draft, M4 and M8 | Nothing more. |
| Status reporting | [Standup report](playbooks/standup-report.md) | Draft, M9 | Nothing more. |
| Setting up and extending the workspace | [Adopt the workspace](adopt-the-workspace.md), [machine self-check](machine-self-check.md), [extend the workspace](extend-the-workspace.md), [changing the machinery](changing-the-machinery.md), [import a repository](playbooks/import-a-repository.md) | Draft, M4, M5 and M11 | A setup interview that asks only what it cannot detect, in M7. |
| Keeping the guidance true | [Docs audit](playbooks/docs-audit.md), [maintain the workspace](maintain-the-workspace.md), [the instruction review](playbooks/instruction-review.md), [evals](../evals/README.md), [the parts](parts.md#the-parts-here) | Draft, M4, M5 and M10. The checks run today. | A check that every playbook and how-to has a row on this page, in M4. |

## Rules

| Rule | Enforced by |
|---|---|
| A commit that adds, archives or proves a playbook or how-to, or moves its `prove-by`, updates its row here. | `prose`. The check named under "Keeping the guidance true" is planned for M4. |
| A stage or topic with no page says so, as Planned with a milestone or as Not covered with the reason. | `prose` |
