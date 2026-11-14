# Agent contract

The rules every coding agent reads before it works here, whichever tool it runs in. This is a sample for an invented team that runs an order system; replace the facts with your own and keep the shape.

Keep this file to routing and traps. If a rule applies only to some files, or a fact needs more than three lines, it belongs in `docs/` with a link from here.

## What lives where

- `src/` holds the code repositories, each pinned at an exact commit. Change code in its own repository, not here.
- `docs/` holds what the code cannot tell you: decisions, procedures and how the parts fit together.
- [INDEX.md](INDEX.md) lists every topic and maps everyday words to the names the code uses. Look there before you search.

## Facts a model cannot derive

- `orders-api` is the live order service. `orders-service-v1` looks current and is not: it is read-only and kept for audits. Never change it.
- "The nightly job" means `ReconciliationWorker`. "A hold" means `AccountFreeze`. More in [INDEX.md](INDEX.md#search-aliases).
- The team tried event sourcing for orders in 2024 and rolled it back. Read [the decision record](docs/decisions/0001-pin-code-repositories.md) format before proposing a change that reopens an old choice, and look for a record of that choice first.

## Finding things

- You have an exact name: `python3 tools/symbols.py NAME src/` returns the file and line.
- You have a topic and no name: [INDEX.md](INDEX.md).
- Do not stack lookups. Pick the one that fits what you already know.

## How work flows

- A change that is small, easy to reverse, in one repository and under a day of work goes straight to [fix a bug](docs/playbooks/fix-a-bug.md).
- Anything else gets a written goal and non-goals first, then a plan a person has read.
- Work is done when it meets the [definition of done](docs/definition-of-done.md), not when the code compiles.

## Rules

- Mark every claim in a report as **verified** (you ran something and saw the result) or **inferred** (you reasoned your way there).
- Stage files by name. Never `git add -A` or `git add .`: another session may have edits in the same folder.
- Open a pull request only as a draft. A person publishes it.
- If you had to ask a person something this workspace should have answered, add it to the [question log](docs/question-log.md) before you finish.
- When a page you edit is past its review date, review the whole page and move the date. The commit check enforces this.
