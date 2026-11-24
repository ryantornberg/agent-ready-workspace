---
kind: plan
status: draft
---

# Hooks fail closed: hand-off plan

Make the before-edit hook refuse every payload it cannot read, so that no malformed call can edit the shelved folder. For the building session and the maintainer, who approves it.

**In short:** today the hook decides on the payloads it understands. This plan normalizes the paths it compares, so every payload is either decided on its path or refused.

## Key points

- `main()` in `src/hooks/runner.py` already refuses a payload it cannot parse, so this plan only adds path normalization.
- The agent tool treats exit code 2 from a hook as a refusal. Any other non-zero exit is an error it shows and then ignores.
- One slice, at the driver tier, because it changes a gate.

## Settled decisions

- The maintainer, 2026-11-14: a hook that cannot decide refuses.

## Decisions made without asking

- Paths are lower-cased before they are compared, since the shelved folder's name has no capitals. Rejected: resolving symbolic links, which needs the file to exist.

## Goal

Every payload the before-edit hook receives is either decided on its path or refused. No payload shape lets an edit reach the shelved folder, `src/orders-service-v1`.

## Non-goals

- No change to which folder is shelved.
- No new hook events, and no change to the lease.

## Why this needs a plan

It changes a gate, and a broken gate can lock every session out.

## Slices

| Order | Slice | Work | Tier | Done when |
|---|---|---|---|---|
| 1 | Normalize paths | `decide()` lower-cases the path and strips a leading `./` before it compares the path with the shelved folder. | driver | Criteria 1 to 3 |

## Success criteria

1. An edit whose path is `SRC/ORDERS-SERVICE-V1/x.py` or `./src/orders-service-v1/x.py` is refused.
2. A payload that is not JSON is refused.
3. A payload that names its path in a `filePath` field instead of `file_path` is refused.

## Verification

To write.

## Recovery

Halt and report. Do not loosen a test to make it pass.

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
