---
kind: record
last-reviewed: 2026-11-25
covers: docs/parts.md
reviewed-at: 09e832c, with the uncommitted change of the sign-off session
---

# Instruction review: docs/parts.md

This records the instruction review of the M3 sign-off's change to the parts page, for its author and its readers.

**In short:** 3 findings, 1 blocking: 2 enforcement (1 blocking), 1 contradiction. The blocking one: the `no_force_push` row says the hook refuses a word of the push the shell would expand, and zsh's glob grouping and glob qualifiers pass it.

## Scope

In scope: the `no_force_push` row of "The parts here", which the diff against 09e832c changes to add `git send-pack` and `git http-push`, refused outright, and "a word of the push the shell would expand, unquoted braces or a glob" among the pushes it cannot judge. Also read, as touched by it: the `outward_write`, `push_lease` and `git_folder_shell` rows, and the page's front matter (`proof: unproven`, `prove-by: M4`). Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/changing-the-machinery.md`, the README's `no_force_push` rules row and Limits bullet, decision 0004 with its sign-off amendment, and the code diff of `parts/no_force_push.py`, its cases and `wslib/gitrules.py`. Ran `python3 ws.py selftest` (every part ok, `no_force_push` 180 of 180), `python3 ws.py check` (exit 0, no finding on this page), `no_force_push.decide` on hand-made events, and `python3 ws.py hook before-shell` on version-1 events with `cwd` set to this worktree. Decision 0004's record, `2026-11-25-signoff-0004.md`, holds the full evidence for findings 1 and 2.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | enforcement | "The parts here", the `no_force_push` row | Blocking. The row lists "a word of the push the shell would expand, unquoted braces or a glob" among what the hook refuses. zsh also expands glob grouping and glob qualifiers, and both pass every before-shell hook: `git push -f origin ma(i)n`, which becomes `main` when a file or folder of that name is in the folder, and `git push origin feature README.md(e:'git push -f origin main':)`, which runs the force push during expansion. Verified: the hook, exit 0; `zsh -c` in `/` expands `b(i)n` to `bin` and runs the code in `bin(e:'print -u2 RAN2':)`. Inferred: that the agent's shell is zsh here, and that git then force-pushes main. | fixed, fix round 1: the hook refuses a word directly followed by `(` in a push, or in a git call that may be one, with cases; the row says so. The same form in another command waits for M4, as the README's Limits say. |
| 2 | enforcement | "The parts here", the `no_force_push` row | Not blocking. The row adds `send-pack` and `http-push` as the commands "which push without `git push`". A git remote helper is a third: `printf 'push +refs/heads/main:refs/heads/main\n\n' \| git remote-https origin <url>` passes every before-shell hook, since the parser counts `remote-https` as one of git's own commands that is not a push. The row makes no claim that its list is complete, so this is marked not blocking here; the README's and decision 0004's records mark it blocking, since those pages state the route as closed. Verified: the hook, exit 0; the helper lists `push` among its capabilities; `man gitremote-helpers` documents a leading `+` as a forced update. Inferred, not run: that the line force-pushes main. | fixed, fix round 1: the hook refuses the remote helpers outright, with cases, and the row names them. |
| 3 | contradiction | "The parts here", the `no_force_push` row | Not blocking. The row scopes the new refusal to "a word of the push". The hook refuses an unquoted glob or braces in any git call that is not built in: `git lfs track *.psd`, and `git co feature-*` when `co` is read from config as `checkout`. The part's docstring still says such a subcommand "is a program named git-NAME, not a push, and passes". Decision 0004's amendment states the wider rule, "or of a git call that is not built in and so may be an alias for one"; this row, the list of what the hook refuses, does not. Verified: the hook and `decide`, with `git lfs track "*.psd"` and `git co feature-x` passing. | fixed: the row now says the rule covers a git call that is not built in and so may be a push, and the part's docstring no longer says such a call always passes. |

## Checked with no finding

- step: the row names no command for an agent to run; the refusal it describes gives `git push -u origin HEAD`, which passes the hook (verified).
- trigger: `INDEX.md` routes "Adding a check or a hook" and a finding named by its part here, and a refused force push to decision 0004, which the row links (verified).
- placement: the row is the page's one-line statement of what the hook refuses, beside the `outward_write` row that already names `send-pack` and `http-push` for its own rule; the two do not disagree, since `outward_write` refuses them by destination and `no_force_push` outright (verified, read).
- eval-case: the page is marked `proof: unproven` with `prove-by: M4` (verified, front matter).
