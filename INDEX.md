---
last-reviewed: 2026-11-15
---

# Index

Where each topic lives, and what the code calls the things people talk about. Agents read this before they search.

## Topics

| Topic | Page |
|---|---|
| The rules every agent follows | [AGENTS.md](AGENTS.md) |
| When work counts as done | [Definition of done](docs/definition-of-done.md) |
| Fixing a small bug | [Fix a bug](docs/playbooks/fix-a-bug.md) |
| How much process a change needs | [Size the work](docs/size-the-work.md) |
| Which model and effort a task gets; delegating | [Orchestration](docs/orchestration.md) |
| Writing a plan for larger work | [Hand-off plan template](docs/templates/hand-off-plan.md) |
| The plan being built now | [M1 hand-off plan](docs/plans/m1-make-the-core-hold-weight.md) |
| What a finished milestone records | [Milestone record template](docs/templates/milestone-record.md), [M1 record](docs/milestones/m1.md) |
| Changing scripts, parts, hooks or CI | [Changing the machinery](docs/changing-the-machinery.md) |
| Why code repositories are pinned, not copied | [Decision 0001](docs/decisions/0001-pin-code-repositories.md) |
| A commit refused because no edit tool wrote a file; why staging is checked at the commit | [Decision 0002](docs/decisions/0002-hooks-remind-the-commit-enforces.md), [the edit ledger](docs/parts.md#the-edit-ledger) |
| Questions someone had to ask a person | [Question log](docs/question-log.md) |
| Testing a playbook | [Evals](evals/README.md) |
| Adding a check or a hook | [Parts](docs/parts.md) |
| The sample code | [src](src/README.md) |

## Search aliases

People and code use different words for the same thing. A search for the everyday word finds nothing, so map it here. The `aliases` check fails when a name in the right-hand column is no longer defined under `src/`.

| You say | The code says |
|---|---|
| the nightly job | `ReconciliationWorker` |
| a hold | `AccountFreeze` |
| the big report | `QuarterlyExport` |
