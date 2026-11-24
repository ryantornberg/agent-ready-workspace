---
kind: record
last-reviewed: 2026-11-24
covers: docs/playbooks/git-host-operations.md
reviewed-at: fca7d9b, with the uncommitted change of the slice Z builder
---

# Instruction review: docs/playbooks/git-host-operations.md

This records the instruction review of slice Z's change to the git-host operations playbook, for its author and its readers.

**In short:** 1 finding, none blocking: 1 placement.

## Scope

In scope: the diff from d2aa593, which changes "a person publishes" to "a person publishes and merges" for a team's workspace in three places: the paragraph after "Which writes need a yes", the operations table's "Publish and merge" row and the rules table's draft row. Read with it: the rest of "Which writes need a yes", the Steps' preamble on pinned repositories, the trap on merge commits and the rules table. Read beside it: `AGENTS.md` with its change (its rules table now says "a person publishes and merges" and adds "merging with `python3 ws.py merge NUMBER`"), `INDEX.md` with its change, `docs/changing-the-machinery.md` (steps 5 and 6 and the paragraph on `ws.py merge`), `docs/procedure-endings.md` (outward writes and the push table), `docs/adopt-the-workspace.md`'s row on who publishes, and `parts/outward_write.py`'s docstring. Every link in the changed text resolves: `../changing-the-machinery.md#the-path-for-a-machinery-change` is the heading "The path for a machinery change".

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | placement | Which writes need a yes, the paragraph on drafts; The operations, "Publish and merge"; Rules, the draft row | Not blocking. The page restates the contract's draft rule three times, and the edit kept the copies in step on who merges but not on how. The contract's row now reads "Publish and merge it only after CI passes on Linux, macOS and Windows, merging with `python3 ws.py merge NUMBER`"; none of the three copies names `ws.py merge`, and the rules table's copy reads as the whole rule. The command is one link away, in changing the machinery's step 6, so an agent that follows the "Publish and merge" row reaches it. One that reads the rules table alone may run `gh pr merge NUMBER --merge`, which no part refuses and which skips `ws.py merge`'s check that each required run passed on the head commit. Procedure endings' push table states who publishes and merges by link, not by copy. The paragraph says "as the contract's rules table says"; a link to that row, with the rules table's row pointing there too, leaves one copy to keep. Verified: `git diff d2aa593 -- AGENTS.md` shows the added clause; `grep` finds no `ws.py merge` on this page; `docs/changing-the-machinery.md`'s rules table says "no part refuses a plain `gh pr merge --merge`". | fixed: the rules table's copy now names `python3 ws.py merge NUMBER`; the two other copies link changing the machinery, which gives it |

## Checked with no finding

- contradiction: "in a team's workspace, a person publishes and merges" now matches the contract, changing the machinery's step 6 ("in a team's workspace, a person does") and procedure endings' push table. `docs/adopt-the-workspace.md` says "In your instance, a person publishes", which is narrower and does not contradict it. The page also covers repositories pinned under `src/`, and `ws.py merge` acts only on this repository's `origin`; in this repository `src/` holds sample files and no pinned repository, and in a team's workspace a person merges, so no agent reaches that case today.
- step: the changed text adds no command; the "Publish and merge" row's link gives `gh pr ready NUMBER` and `python3 ws.py merge NUMBER`, both of which exist.
- trigger: the purpose line, the In short line and the routing table are unchanged, and the change does not move when the page applies.
- enforcement: the rules table's draft row stays `prose`, which is true: no part refuses a non-draft `gh pr create` or an agent's merge in a team's workspace. The merge-commit row's `no_admin_merge` cases exist.
- eval-case: the page is `proof: unproven` with `prove-by: M8`, so its behavior needs no case yet.
