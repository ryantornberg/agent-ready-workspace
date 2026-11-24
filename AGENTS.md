---
last-reviewed: 2026-11-18
---

# Agent contract

The rules every coding agent reads before it works here, whichever tool it runs in. The team and its order system are invented; replace the facts with your own and keep the shape.

Keep this file to routing and traps. If a rule applies only to some files, or a fact needs more than three lines, it belongs in `docs/` with a link from here.

## What lives where

- [src/](src/README.md) holds the code. In a real workspace each folder there is a pinned code repository; this sample checks in a few files instead.
- `docs/` holds what the code cannot tell you: decisions, procedures and how the parts fit together.
- [INDEX.md](INDEX.md) lists every topic and maps everyday words to the names the code uses. Look there before you search.
- [workspace.json](workspace.json) lists the checks and hooks this workspace runs. [docs/parts.md](docs/parts.md) says how to add one.

## Facts a model cannot derive

- `src/orders-api` is the live order service. `src/orders-service-v1` looks current and is not: it is kept read-only for audits. A hook refuses edits to it.
- "The nightly job" means `ReconciliationWorker`. "A hold" means `AccountFreeze`. More in [INDEX.md](INDEX.md#search-aliases). A check fails when one of those names leaves the code.
- A hook refuses an edit in the main working copy while another live agent session holds it. Only then work in a worktree of your own under `.claude/worktrees/`, as the refusal says. Uncommitted changes you did not make are not that refusal: leave them and work where you are. See [decision 0005](docs/decisions/0005-concurrent-sessions-and-the-edit-ledger.md). A review may also read a pull request or a commit in a worktree, as [review in a worktree](docs/review-in-a-worktree.md) says.

## Finding things

- You have an exact name: `python3 tools/symbols.py NAME src` returns the file and line.
- You have a topic and no name: [INDEX.md](INDEX.md).
- Do not stack lookups. Pick the one that fits what you already know; the [research ladder](docs/research-ladder.md) says which.

## How work flows

- A one-line request maps to its page in the [request map](docs/request-map.md). Each role's first pages are in [reading paths by role](docs/reading-paths.md).
- A change that is small, easy to reverse, in one repository and under a day of work goes straight to [fix a bug](docs/playbooks/fix-a-bug.md). A small refactor passes the same gate and follows [safe refactor](docs/safe-refactor.md). A small change to pages only follows [extend the workspace](docs/extend-the-workspace.md), since a page has no failing test to start from.
- Anything else climbs the [size gate's ladder](docs/size-the-work.md): goal and non-goals first, then a [hand-off plan](docs/templates/hand-off-plan.md) a person has approved.
- Every task you hand off names its tier. See [orchestration](docs/orchestration.md).
- A change to scripts, parts, hooks or CI is machinery: [changing the machinery](docs/changing-the-machinery.md).
- Work is done when it meets the [definition of done](docs/definition-of-done.md), not when the code compiles.

## Rules

| Rule | Enforced by |
|---|---|
| Mark every claim in a report as **verified** (you ran something and saw the result) or **inferred** (you reasoned your way there). | `eval:fix-a-bug`, `claim_marks#a claim line not marked verified or inferred fails` |
| Stage files by name. Never `git add -A`, `git add .` or `git commit -a`: another session may have edits in the same folder. The commit check refuses a staged file your edit tools did not write; record one you wrote another way with `python3 ws.py ledger --add PATH`. | `edit_ledger#a path the ledger does not hold fails, whatever staged it` |
| Open a pull request as a draft. Publish and merge it only after CI passes on Linux, macOS and Windows, merging with `python3 ws.py merge NUMBER`. In this repository the maintainer lets agents do both; in a team's workspace, a person publishes and merges. | `prose` |
| If you had to ask a person something this workspace should have answered, add it to the [question log](docs/question-log.md) before you finish. | `prose` |
| When a page you edit is past its review date, review the whole page and move the date. The commit check and CI both enforce this. | `page_kinds#review date: a stale page the commit edits must be reviewed` |
| A change to a playbook marked proven, to this file, to `INDEX.md`, or to anything else the eval covers, needs a new eval run on record in which the guidance beats both the bare model and a two-line instruction. The run costs real agent time, so batch such edits. See [evals](evals/README.md). | `eval_record#an edited playbook fails until its case is run again` |
