---
kind: record
last-reviewed: 2026-11-24
covers: README.md
reviewed-at: 2d83108, with the uncommitted page edits of the slice GFIX builder
---

# Instruction review: README.md (slice GFIX)

This records a fresh session's review of slice GFIX's edit to the README's Limits list, for the slice's builder and the maintainer.

**In short:** 4 findings: 3 contradiction, 1 eval-case; none is blocking. Every example on the bullet behaves as it says. The bullet says every shell guard but `no_stage_all` refuses a NUL escape and a judged name under a program the parser does not read, but two forms of those pass all seven guards; the code findings are in [the 0004 record](2026-11-24-gfix-0004.md).

## Scope

In scope: the Limits bullet that begins "The shell guards refuse six more lines the parser misreads", uncommitted on 2d83108. Read beside it: AGENTS.md, the instruction review playbook, the rest of the Limits list, decision 0004's GFIX paragraph, the plan's last "### 2026-11-24" entry on origin/main, and the block from "# -- A command no guard can read (Q54, Q74, Q75)" in `wslib/gitrules.py`. Each example was run through the seven guards' `decide`, and the route lines through bash 3.2.57 and zsh 5.9 with a fake `git` and `gh`, as [the 0004 record](2026-11-24-gfix-0004.md#scope) describes.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | The bullet, "a NUL escape after other text in its word, such as `git$'\0' push --force origin main`, since a NUL ends the word a program gets" | Not blocking. The bullet says every shell guard but `no_stage_all` refuses such a line, and gives a reason that holds for zsh only. Bash ends only the `$'...'` text at the NUL and keeps the rest of the word, so `$'\0'git push --force origin main` passes all seven guards and bash runs git (verified; 0004 record, finding 1). The bullet's list of what still gets past does not name it. | fixed: with finding 1 of the 0004 record; the bullet names `$'\0'git` and the form that passes |
| 2 | contradiction | The bullet, "A program the parser does not know ... is refused when one of its words is ... the name of a program the guards judge"; "So does a shell named in another letter case" | Not blocking. A wrapper named in another letter case is a program the parser does not know, yet `NICE -n 5 git push -f origin main` and `NOHUP gh pr merge 5 --admin` pass all seven guards, and both shells run the call on macOS (verified; 0004 record, finding 2). The bullet names only a shell in another case among what gets past, and says nothing of `ENV` or `PRINTENV`, which print the environment past `secrets_shell` (verified; 0004 record, finding 3). | fixed: with finding 2 of the 0004 record; the bullet names a wrapper in another case among the refused, and `env` and `printenv` in another case among what gets past |
| 3 | contradiction | The bullet, "`git`, `gh`, `env`, `printenv`, `pwsh`, `powershell` or a shell, by name or by path" | Not blocking. Only the eight shells the parser reads count: `arch -arm64 csh` and `arch -arm64 tcsh` pass all seven guards, while `arch -arm64 bash` and `arch -arm64 /bin/zsh` are refused (verified). "A shell" should say which. | fixed: the bullet names the eight shells the parser reads, and `tcsh` among what gets past |
| 4 | eval-case | The bullet, "Look a program up with `command -v git`, and put a pattern inside a longer quoted string" | Not blocking. The bullet asks a new habit of agents, and no eval case covers it; the README carries no `prove-by` mark (verified, read). The stored runs show the old habit: 9 of the 65 `debug-staging-reminder` run files hold `type git` or `which -a git`, which are now refused (verified). The refusal message gives the same advice at the moment it applies (verified), which lowers the cost of the gap. | deferred to M4: the parser's fix there removes the refusals this advice works around, and the refusal message gives the advice where it applies |

## Checked with no finding

- enforcement: each example the bullet says is refused is refused by all seven guards (verified): `$'\x67it' push --force origin main`, `git$'\0' push --force origin main`, `((git push -f origin main) )`, `$(( $(git push) ))`, `nice -n {5,git} push`, a `nice` inside 8 nested `sh -c`, `GIT push --force origin main`, `arch`, `script` and `flock` with a literal `git`, and the harmless `which git`, `echo gh pr merge 5 --admin`, `grep -n git notes.txt`, `echo $(( $(date +%s) - START ))` and `bash $SCRIPT`. Each example it says gets past passes all seven (verified): `arch $(command -v git) push -f origin main`, `flock /tmp/l -c 'git push -f origin main'`, `man -P 'git push -f origin main' ls` and `BASH -c 'git push -f origin main'`.
- step: `command -v git` passes all seven guards, and so do `grep -n "git push" notes.txt` and `echo "gh pr merge 5 --admin"`, the longer quoted strings the bullet asks for (verified). `grep -n 'git' notes.txt` is refused, as "a longer quoted string" implies (verified).
- trigger: the bold lead says what follows: six refused lines and runner forms that still get past.
- placement: the bullet sits in the Limits list beside the Q54 bullet it extends, and links decision 0004 for the detail; it restates no rule from procedure endings.
