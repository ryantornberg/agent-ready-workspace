---
last-reviewed: 2026-11-16
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
| The plan being built now | [M2 hand-off plan](docs/plans/m2-port-from-the-work-workspace.md), [its record so far](docs/milestones/m2.md) |
| What a finished milestone records | [Milestone record template](docs/templates/milestone-record.md), [M1 record](docs/milestones/m1.md) |
| Changing scripts, parts, hooks or CI | [Changing the machinery](docs/changing-the-machinery.md) |
| A push to main refused; a merge with `gh pr merge --admin` refused | [Changing the machinery](docs/changing-the-machinery.md#the-path-for-a-machinery-change) |
| Two agent sessions at once; an edit refused because another session holds the main copy; the lease; when to use a worktree | [Decision 0005](docs/decisions/0005-concurrent-sessions-and-the-edit-ledger.md) |
| What a hook may read; a path inside a worktree; writing a session hook | [Decision 0004](docs/decisions/0004-the-hook-contract.md) |
| Notices when a session starts: stale pages, a pin behind its upstream, the main copy not brought up to date | [The parts here](docs/parts.md#the-parts-here) |
| Rules shown when you edit a file in one folder; adding such a rule | [Rule pages](docs/rules/), such as [the live order service's](docs/rules/orders-api.md) |
| A commit refused for a line-number citation or a missing **In short** line | [The parts here](docs/parts.md#the-parts-here) |
| Opening a browser; "browser is already in use"; logins gone after a session | [Browsers](docs/browsers.md) |
| Why code repositories are pinned, not copied | [Decision 0001](docs/decisions/0001-pin-code-repositories.md) |
| A commit refused because no edit tool wrote a file; why staging is checked at the commit | [Decision 0002](docs/decisions/0002-hooks-remind-the-commit-enforces.md), [the edit ledger](docs/parts.md#the-edit-ledger) |
| A manifest refused for its version; where the engine's code lives | [Decision 0003](docs/decisions/0003-the-engine-in-one-folder.md), [the manifest](docs/parts.md#the-manifest) |
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
