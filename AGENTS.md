# Agent contract

The rules every coding agent reads before it works here, whichever tool it runs in. The team and its order system are invented; replace the facts with your own and keep the shape.

Keep this file to routing and traps. If a rule applies only to some files, or a fact needs more than three lines, it belongs in `docs/` with a link from here.

## What lives where

- [src/](src/README.md) holds the code. In a real workspace each folder is a repository pinned at an exact commit; here it is a few sample files.
- `docs/` holds what the code cannot tell you: decisions, procedures and how the parts fit together.
- [INDEX.md](INDEX.md) lists every topic and maps everyday words to the names the code uses. Look there before you search.
- [workspace.json](workspace.json) lists the checks and hooks this workspace runs. [docs/parts.md](docs/parts.md) says how to add one.

## Facts a model cannot derive

- `src/orders-api` is the live order service. `src/orders-service-v1` looks current and is not: it is kept read-only for audits. A hook refuses edits to it.
- "The nightly job" means `ReconciliationWorker`. "A hold" means `AccountFreeze`. More in [INDEX.md](INDEX.md#search-aliases). A check fails when one of those names leaves the code.

## Finding things

- You have an exact name: `python3 tools/symbols.py NAME src` returns the file and line.
- You have a topic and no name: [INDEX.md](INDEX.md).
- Do not stack lookups. Pick the one that fits what you already know.

## How work flows

- A change that is small, easy to reverse, in one repository and under a day of work goes straight to [fix a bug](docs/playbooks/fix-a-bug.md).
- Anything else gets a written goal and non-goals first, then a plan a person has read.
- Work is done when it meets the [definition of done](docs/definition-of-done.md), not when the code compiles.

## Rules

- Mark every claim in a report as **verified** (you ran something and saw the result) or **inferred** (you reasoned your way there).
- Stage files by name. Never `git add -A`, `git add .` or `git commit -a`: another session may have edits in the same folder. A hook refuses these.
- Open a pull request only as a draft. A person publishes it.
- If you had to ask a person something this workspace should have answered, add it to the [question log](docs/question-log.md) before you finish.
- When a page you edit is past its review date, review the whole page and move the date. The commit check and CI both enforce this.
- A change to a playbook needs a new passing eval run on record. See [evals](evals/README.md).
