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

## Re-check

A fresh session re-read the page and the code on 2026-11-25, after fix round 1, at 0c447d4: the diff `09e832c..0c447d4` of this page, `parts/no_force_push.py`, its cases and `wslib/gitrules.py`. It ran `python3 ws.py selftest` (every part ok, `no_force_push` 185 of 185), `no_force_push.decide`, `python3 ws.py hook before-shell --tool claude-code` on Bash events with `cwd` set to this worktree, and `zsh -f` and `bash` on `print` and `echo` lines in a temporary folder of its own.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed, holds | The row names a word directly followed by `(`. The hook refuses `git push -f origin ma(i)n`, `git push -f origin ma(\|)in` and `git push origin feature README.md(e:'git push -f origin main':)`, exit 2 each. Verified. The same refusal is skipped when the program word is quoted: Missed, item 1. |
| 2 | fixed, holds | The row names the remote helpers. The hook refuses `git remote-https`, fed a forced refspec, and `git -c alias.h=remote-https h origin URL`, exit 2 each. Verified. A helper git starts from an `ext::` URL still passes: Missed, item 2. |
| 3 | fixed, holds | The row says the rule covers "a git call that is not built in and so may be one", and the docstring now says such a call passes "unless one of its words is one the shell would expand". The hook refuses `git lfs track *.psd` and passes `git lfs track "*.psd"`, `git log -- *.py` and `git add docs/*.md`. Verified. |

Broke: none.

Missed:

1. Blocking. A quoted or escaped program word turns off the refusal the row lists. `push_expands` returns early when the text `git` is not in the line, but the parser and both shells read `g\it`, `gi''t`, `"g"it` and `$'g'it` as `git`. The hook passes `g\it push origin {+,}main`, `gi''t push -f origin mai[n]`, `"g"it push -f origin ma(i)n` and `$'g'it push origin {+,}main`, exit 0 each, and bash and zsh print `git git git git +main main` for `g\it gi""t "g"it $'g'it {+,}main`. Verified. Inferred, not run: that git then force-pushes main. The full evidence is in the README's record, `2026-11-25-signoff-readme.md`, under "Re-check".
2. Not blocking, as finding 2 was here, since the row does not claim its list of routes is complete. `git -c protocol.ext.allow=always ls-remote 'ext::sh -c git% push% -f% origin% main'` passes every before-shell hook, and git's `ext::` transport runs the command a remote helper is given. Verified: the hook, exit 0, and `man git-remote-ext`. Inferred, not run: that the push runs. The README's and decision 0004's records mark it blocking.

The author's settlement of the re-check, 2026-11-25. No further re-check ran; fix round 2 was the last the plan allows.

- Missed 1: fixed, fix round 2: `push_expands` no longer tests the line for the text `git`, so the walk reads the program as the parser does; four cases, `g\it`, `"g"it`, `gi''t` and `$'g'it`, each failed first.
- Missed 2: the row now says a remote helper is refused when called by name. The `ext::` route itself is the README's interpreter limit, taken to the maintainer for M4, as the README record says.
