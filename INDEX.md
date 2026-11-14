# Index

Where each topic lives, and what the code calls the things people talk about. Agents read this before they search.

## Topics

| Topic | Page |
|---|---|
| The rules every agent follows | [AGENTS.md](AGENTS.md) |
| When work counts as done | [Definition of done](docs/definition-of-done.md) |
| Fixing a small bug | [Fix a bug](docs/playbooks/fix-a-bug.md) |
| Why code repositories are pinned, not copied | [Decision 0001](docs/decisions/0001-pin-code-repositories.md) |
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
