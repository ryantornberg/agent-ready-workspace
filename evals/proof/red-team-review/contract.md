# Agent contract

The rules every coding agent reads before it works here. This is a fixed copy of the workspace's contract, cut to what this folder needs.

## What lives where

- `src/` holds the code, and `tests/` its unit tests. Run them with `python3 -m unittest`.
- `docs/plans/` holds hand-off plans, `docs/records/` the records reviews leave, and `docs/playbooks/` the procedures an agent follows.
- `workspace.json` binds each tier of work to a model.

## Facts a model cannot derive

- Uncommitted changes you did not make belong to another session. Leave them as they are, and keep them out of your commit.
- This copy has no remote. Where a procedure says to push, commit and stop there.

## Rules

- Mark every claim in a report as **verified** (you ran something and saw the result) or **inferred** (you reasoned your way there).
- Stage files by name. Never `git add -A`, `git add .` or `git commit -a`: another session may have edits in the same folder.
- A delegated task's prompt starts with its tier, such as `Tier: driver`, and runs at the model `workspace.json` binds to that tier.
