---
kind: plan
status: draft
---

# The writing-session lease: hand-off plan

Let one agent session at a time write in the main working copy, and send every other session to a worktree of its own. For the building session and the maintainer, who approves it.

**In short:** a session takes a lease before its first edit, and an edit from any other session is refused while the lease is held. A lease whose holder has gone is taken over, so a crashed session never blocks the next one.

## Key points

- `acquire()` in `src/hooks/lease.py` already stores the holder's process id and takes over a lease whose process has exited, so a crashed session frees the main copy at once.
- The lease file lives in the git folder that every worktree shares, so a session in a worktree sees the same lease.
- One slice, at the driver tier, because it adds a gate.

## Settled decisions

- The maintainer, 2026-11-16: a person working with one session must never be refused.

## Decisions made without asking

- A lease lasts 30 minutes without a refresh. Rejected: no time limit, which leaves a hung session holding the copy until someone deletes the file.

## Goal

While one live session writes in the main working copy, an edit there from another session is refused, with a message that names a worktree. A lease whose holder has exited or gone quiet for 30 minutes is taken over.

## Non-goals

- No lease on a worktree: each worktree belongs to the session that made it.
- No change to the before-edit hook's shelved-folder rule.

## Why this needs a plan

It adds a gate that refuses edits, and a wrong refusal locks a person out of their own working copy.

## Slices

| Order | Slice | Work | Tier | Done when |
|---|---|---|---|---|
| 1 | Refuse on the lease | The before-edit hook calls `acquire()` with the session and its process id, and refuses the edit when it returns "refused". | driver | Criteria 1 to 3 |

## Success criteria

1. A second session's edit in the main copy is refused while the first session's lease is fresh, and the refusal names a worktree.
2. A lease whose process has exited is taken over at the next edit.
3. A lease 30 minutes old is taken over.

## Verification

- `python3 -m unittest` passes, including a test for each criterion in `tests/test_hooks.py`.

## Recovery

To write.

## Stop rule

Stop when the same criterion fails after two fix rounds.

## Limits

One branch and one pull request. At most two fix rounds.

## Execution profile

none

## Records this plan must leave

- A test for each criterion in `tests/test_hooks.py`.

## Red team

Record: none yet.

| # | Finding | Disposition | Action |
|---|---|---|---|

## Approval

Not yet approved.
