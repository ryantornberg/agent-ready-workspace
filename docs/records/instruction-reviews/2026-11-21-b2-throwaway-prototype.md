---
kind: record
last-reviewed: 2026-11-21
covers: docs/playbooks/throwaway-prototype.md
reviewed-at: 8b33280, with the uncommitted change of the B2 builder
---

# Instruction review: docs/playbooks/throwaway-prototype.md

This records the instruction review of the new throwaway-prototype playbook, for its author and for agents or people who follow it.

**In short:** 3 findings: 1 contradiction, 1 step, 1 trigger. The logic branch runs as written, but the UI branch's worktree clashes with the contract and fails on submodules, and nothing routes a question here.

## Scope

The whole page was in scope, since it is new. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `README.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md`, and the page it links to: `docs/playbooks/test-first.md`. Also read `src/README.md`, decision 0001, decision 0005 and `parts/no_discard.py`, for the cleanup commands. Ran `python3 ws.py rules` and `python3 ws.py check`; the check passed. In a scratch repository with a submodule, ran step 7's commands on a linked worktree. Searched every Markdown page outside the records for links to the page.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Steps, step 2 | A UI prototype always goes in a worktree under `.claude/worktrees/`. The contract says to work in a worktree only when the lease hook refuses an edit in the main copy. The page does not label its use as an exception to that rule. Verified: read Facts a model cannot derive in `AGENTS.md` and decision 0005. | fixed: both branches now build in a scratch folder outside the repository, a UI prototype in a clone of it, so no worktree is used. |
| 2 | step | Steps, steps 2 and 7 | In a real workspace, `src/orders-web` is a pinned submodule. A new worktree leaves it empty, the `throwaway/<slug>` branch is on the workspace, not the code repository, and step 7's cleanup fails. Verified: in a scratch repository, the submodule folder was empty; `git restore .` and `git clean -fd` left the submodule's edit; `git worktree remove` refused, "working trees containing submodules cannot be moved or removed". Inferred: the steps work in this sample, whose `src/` holds plain files. | fixed: the clone checks out the pinned repositories with `python3 ws.py pins`, and step 7 deletes the folder, with no branch or worktree to remove. |
| 3 | trigger | Purpose line; the Topics table of `INDEX.md` | The page is for anyone planning work who must see something run, but nothing sends them there. `INDEX.md` has no row, and neither the size gate's ladder nor the hand-off plan template links it. Verified: searched `AGENTS.md`, `INDEX.md` and every page under `docs/`; only the README's proof table names the page. | queued for slice Z: a Topics row in INDEX.md, which the eval hashes. Until then the playbook catalog and how-to index, later in this slice, list the page. |

## Checked with no finding

- enforcement: each of the three musts and nevers has a `prose` rules row, and the five rules sit in the table those rows name.
- placement: the page loads only when needed, adds nothing to the always-loaded layer, and sends code meant to be kept to test first.
- eval-case: the page is marked `proof: unproven` with `prove-by: M4`, and the README's proof table lists it.
