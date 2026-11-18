---
last-reviewed: 2026-11-18
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
| The milestones being built now, and their plans | `building` in [workspace.json](workspace.json); the plans are in [docs/plans/](docs/plans/) |
| What a finished milestone records | [Milestone record template](docs/templates/milestone-record.md), [milestone records](docs/milestones/) |
| Where a page goes; page kinds and their front matter; a commit refused by `page_kinds` | [Layout](docs/layout.md) |
| What a word means here | [Glossary](docs/glossary.md) |
| Proven and unproven pages; `proof`, `prove-by`, `proven-by` | [Decision 0006](docs/decisions/0006-what-proven-means.md) |
| Which rules a check enforces | `python3 ws.py rules` |
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

## Cross-cutting chains

For each kind of change, every path it touches. The `chains` check fails on a path that does not exist.

| Change | Paths it touches |
|---|---|
| Add or change a part | `parts/`, `workspace.json`, `docs/parts.md`, `README.md`, `tests/test_cases_bite.py` |
| Change a playbook marked proven, the contract or the index | `docs/playbooks/`, `AGENTS.md`, `INDEX.md`, `evals/cases/`, `evals/runs/`, `evals/README.md`, `README.md` |
| Change the eval harness or a grader | `evals/run.py`, `evals/grade.py`, `evals/proofkeys.py`, `evals/runs/`, `evals/README.md`, `docs/changing-the-machinery.md` |
| Mark a page proven or unproven | `docs/`, `README.md`, `docs/decisions/0006-what-proven-means.md`, `docs/plans/` |
| Add a page | `docs/layout.md`, `INDEX.md` |
| Add a rule page | `docs/rules/`, `INDEX.md` |
| Change the engine or its version | `wslib/`, `workspace.json`, `CHANGELOG.md`, `docs/decisions/0003-the-engine-in-one-folder.md` |
| Change what counts as machinery | `workspace.json`, `docs/changing-the-machinery.md`, `tests/test_core.py` |
| Start or sign off a milestone | `workspace.json`, `docs/plans/`, `docs/milestones/`, `CHANGELOG.md`, `EVIDENCE.md` |
