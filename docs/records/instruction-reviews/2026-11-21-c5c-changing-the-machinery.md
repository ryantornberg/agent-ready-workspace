---
kind: record
last-reviewed: 2026-11-21
covers: docs/changing-the-machinery.md
reviewed-at: 35e641c, with the uncommitted change of slice C5c
---

# Instruction review: docs/changing-the-machinery.md

This records the instruction review of slice C5c's machinery page change, for its author and for agents a merge guard's refusal sends here.

**In short:** 1 finding: 1 trigger. The merge guard now refuses any shell command it cannot judge, such as `$EDITOR README.md`, and sends the agent to this page, whose purpose line, **In short** line and index row speak only of changing machinery and merging.

## Scope

In scope: the changed text of `docs/changing-the-machinery.md` against `35e641c`: the new sentence on commands the guard cannot judge, in the `no_admin_merge` bullet of "The path for a machinery change". It was read against the whole page, its Rules table and its Traps. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/instruction-review.md`, the README's `direct_push` and `no_admin_merge` Limits bullet, the uncommitted changes to `docs/decisions/0004-the-hook-contract.md`, `docs/decisions/0005-concurrent-sessions-and-the-edit-ledger.md` and `docs/parts.md`, `parts/no_admin_merge.py` and its 65 cases, and `wslib/shell.py`. Commands run: `python3 ws.py check` (passes), `python3 ws.py selftest` (every part's cases pass), and 19 commands through `python3 ws.py hook before-shell`.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | The page's purpose and **In short** lines; the `no_admin_merge` bullet of "The path for a machinery change" | The guard runs on every shell command and now refuses any it cannot judge, whatever it does: `$EDITOR README.md` and `cat x \| bash` are refused with "it may merge past CI", ending "See docs/changing-the-machinery.md". The page's purpose line is for "anyone about to change" machinery, its **In short** line is about branches and CI, and the index row that points here names only a refused push to main and `gh pr merge --admin`. The one sentence that explains the refusal sits mid-bullet, so an agent that was only opening an editor cannot tell it is on the right page. Verified: ran both commands through `hook before-shell` and read the refusal; read the purpose line, the **In short** line and the `INDEX.md` row. | fixed in the page: the refusal of a command `no_admin_merge` cannot judge has its own paragraph after the bullet, with what to do. The `INDEX.md` row is queued for slice Z, since the eval hashes the index; the purpose and In short lines still describe the page's job and are unchanged. |

## Checked with no finding

- contradiction: the new list of commands the guard cannot judge matches `_unresolved` and the parser's reasons: a program word or `gh` subcommand that is a variable, text piped into a shell, `xargs` or `find -exec` giving `gh pr merge` or `gh api` its arguments, and a variable argument of `gh pr merge` are each refused, and `xargs` giving a `gh` read its arguments passes. It agrees with the README's Limits bullet and with the `no_admin_merge` row in `docs/parts.md`. "It cannot see a merge made through another program" still holds: a `curl` call to the merge endpoint and `echo ... | python3` pass.
- step: the refusal's way through, writing the command with literal words or running `python3 ws.py merge NUMBER`, exists and is the page's own step 6.
- enforcement: the change states what a hook refuses, not a must for an agent. Each named form has a case in `parts/no_admin_merge.cases.json`, such as "a gh subcommand that is a variable is refused" and "an argument of gh pr merge that is a variable is refused", and the Rules table's existing tags still name real cases.
- placement: the sentence describes one part's behavior on the page that the part's refusal names, beside the rest of that part's description. The page is not in the always-loaded layer.
- eval-case: the page is marked unproven with `prove-by: M4`.
