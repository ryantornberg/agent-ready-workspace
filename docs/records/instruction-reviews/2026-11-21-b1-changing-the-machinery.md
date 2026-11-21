---
kind: record
last-reviewed: 2026-11-21
covers: docs/changing-the-machinery.md
reviewed-at: 166bbc7, with the uncommitted change of slice B1
---

# Instruction review: docs/changing-the-machinery.md

This records the instruction review of the B1 edits to the machinery page, for its author and for anyone changing scripts, hooks or CI.

**In short:** 2 findings: 1 contradiction, 1 step. The new `--commits` step runs as written, but the deny-list scan of each diff has no command, and docs no longer change freely.

## Scope

In scope: the four edited rules rows and the edited trap on changes the eval covers, read against the whole page. Read beside it: `AGENTS.md`, `INDEX.md`, `workspace.json`, `docs/playbooks/instruction-review.md`, `docs/parts.md`, `parts/deny_list.py`, `parts/review_trailer.py`, `wslib/runner.py` and `wslib/snapshot.py`. Ran `python3 ws.py check --commits origin/main..HEAD` and `python3 ws.py check --help`.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Purpose line | The page says docs change freely. A change to a guidance page now needs a review record or a listed skip reason, refused at the commit-msg hook, before a push to main and in CI. Verified: `docs/` is on the `review_trailer` guidance list, and `tests.test_instruction_review` shows the refusal. | fixed: the purpose line now says a guidance page goes to main after its review. |
| 2 | step | Rules table; Traps | Both ask that every commit's diff pass the deny-list scan, but name no command for it. `ws.py check --commits` runs `deny_list` on each message and identity only. Verified: `command_commits` builds a three-file message snapshot, and `ws.py check --help` offers no per-commit diff scan. | queued for the maintainer, with the same finding from sub-batch A's review of this page. |

## Checked with no finding

- trigger: the In short line and the index rows still fire for machinery work.
- enforcement: each edited rules row is tagged; `eval_record#an edited playbook fails until its case is run again` exists, and the `prose` rows say why.
- placement: the edits sit on the page that owns the trap.
- eval-case: the page is marked unproven with `prove-by: M4`.
