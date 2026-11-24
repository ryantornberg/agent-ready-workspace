---
kind: reference
last-reviewed: 2026-11-22
---

# Agent settings

What the agent tools' settings and the secrets guard allow and deny here, and what they cannot. It is for anyone changing them, adopting them or needing a token.

**In short:** Claude Code is denied reading the secrets files and may fetch eight documentation domains. Codex CLI gets a permissions profile with the same denies inside the workspace, defined but not the default, and the same domains for its web search. In the shell, a hook refuses environment dumps and reads of the secrets files, and `python3 ws.py with-secrets` hands a value to one program. A new worktree gets a copy of the ignored local settings file. The `agent_settings` check fails when an entry goes missing.

## The secrets files

These are the files an agent should never read: `.env` and `.env.*` anywhere in the workspace, `*.pem` and `*.key` files, and any `secrets/` folder. Claude Code's deny list adds the home folder's credential files: `~/.ssh`, `~/.aws`, `~/.netrc`, `~/.git-credentials`, gh's sign-in file, and the folder that holds the private deny list.

| Tool | Where | What it does |
|---|---|---|
| Claude Code | `permissions.deny` in [.claude/settings.json](../.claude/settings.json), as `Read(<pattern>)` | Its read tools refuse the file. A shell command is not covered by the setting; the `secrets_shell` hook refuses it, as [secrets in the shell](#secrets-in-the-shell) says. |
| Codex CLI | The `agent-ready` profile in [.codex/config.toml](../.codex/config.toml), each pattern `"none"` under `":workspace_roots"` | The sandbox refuses the file to every process the agent starts. |

The Codex profile is defined but not made the default. Making it the default would replace a person's own sandbox setting for this project, and its base, `:workspace`, turns off network access and writes to the home folder. To use it, start Codex with `codex -c default_permissions="agent-ready"`, or set that line in your own config. Since it reaches every process, it denies nothing in the home folder: a home entry such as `~/.ssh` would also stop `git push`.

## Secrets in the shell

The tools' settings do not reach a shell command, so the `secrets_shell` hook judges each one before it runs, in both agent tools. It refuses two things.

- **An environment dump:** `env` with no program to run, `printenv` in any form, `export`, `declare` or `typeset` with no name, `set` with no argument, `ps` with `e` or `E` in a letter group or with `-E`, a read of `/proc/<pid>/environ`, and PowerShell's `env:` drive and its `GetEnvironmentVariables` method. The method's name passes as text in a message body, or in a heredoc fed to a program that is not a shell. To see a variable that holds no secret, such as `PATH`, echo it by name; ask the person for a secret.
- **A read of a secrets file:** any command that names one, in an argument or after `<`. The patterns are the ones above, and the file `with-secrets` reads, matched at the end of any path. A glob that may match one, such as `cat *`, counts as naming it. A program that only looks at a file's name passes, such as `ls`, `test`, `rm`, `git status` and `git check-ignore`. The first word after `grep`, `rg`, `sed` or `awk` is a pattern, so `grep -n '.env' .gitignore` passes.

When a program needs a value from the secrets file, such as a token, run it through `with-secrets`:

```
python3 ws.py with-secrets NPM_TOKEN -- npm publish
```

It reads the named values from the secrets file and starts the program with them in its environment. The shell that called it never holds them. The agent sees them only if the program prints them, or if another command reads the program's environment while it runs; the hook refuses `ps eww`, the usual one. The program must read the variable itself, as `npm`, `gh` and most command-line tools do. Do not write `$NPM_TOKEN` on the command line: the calling shell fills it in before `with-secrets` runs, with what that shell holds, which is not the file's value.

- **The file** is `.env` at the top of the main working copy, so every worktree reads the same one. The `"file"` setting of `secrets_shell` in [workspace.json](../workspace.json) names another, and the hook refuses shell reads of that one too. A person writes it, one `NAME=value` per line; `#` starts a comment, and quotes around a value are dropped.
- **Under Codex's `agent-ready` profile,** the sandbox denies `.env` to every process the agent starts, `with-secrets` included, so in the main working copy it exits 2 and says so. A person who uses that profile keeps the file outside the workspace, such as `~/.config/agent-ready-workspace/secrets.env`, which Claude Code's deny list and the hook already cover. They set `WS_SECRETS_FILE` to its path in their own shell profile, so the shared `workspace.json` stays as it is. The hook refuses an agent's command that sets `WS_SECRETS_FILE`.
- **It refuses some programs.** A shell, `env`, `printenv` and a program that runs another, such as `sudo`, `xargs`, `find` or `nohup`, would show every value to whatever they run. It also refuses a program whose file is a link to a shell. On Windows, a batch file such as `npm.cmd` runs under cmd.exe, which reads its arguments, so it refuses one whose arguments hold `&`, `|`, `%`, `!`, `^`, a quote, a bracket or `<` and `>`.
- **Every shell guard judges the program it starts.** The shared parser reads `with-secrets NAME -- PROGRAM` as a wrapper, so a push meets the push guards, a gh write the outward-write guard and a file write the git folder guard, as if run by its own name. Each NAME it hands in is read as a value the line does not show, so a `GH_REPO` or `GIT_CONFIG_*` handed in this way leaves the target unknown, and the guard refuses. The hook refuses a second `with-secrets` under it. git and gh sign in on their own, so neither needs it.
- **It exits** with the program's own code, and with 2 when it refuses or a name or the file is missing. No message shows a value.

## The documentation domains

Claude Code's web fetch may read these without asking, through `WebFetch(domain:...)` entries in `permissions.allow`: `docs.python.org`, `git-scm.com`, `docs.github.com`, `cli.github.com`, `code.claude.com`, `docs.anthropic.com`, `developers.openai.com` and `learn.microsoft.com`. Codex CLI has no web fetch; its web search lists the same domains in `allowed_domains` under `[tools.web_search]`.

## The worktree's copy

`.claude/settings.local.json` holds a person's own permissions and is ignored by git, so `git worktree add` leaves it behind. The `post-checkout` git hook copies it from the main working copy into each new linked worktree, and never overwrites one already there. See [decision 0004](decisions/0004-the-hook-contract.md).

## Limits

- The check reads the committed files only. A person's own settings, or a local settings file, can loosen either tool.
- The shell hook reads command lines, so much gets past it. An interpreter or a script that opens a secrets file is not seen; `python3 -c "open('.env')"` is, since the file's name is on the line. Neither is a recursive read of a folder that holds one, such as `grep -r TOKEN .` or `tar`. Nor are files that `xargs` or `find -exec` supply, a variable the line does not set, brace expansion such as `.{env,x}`, an unquoted Windows path, and PowerShell beyond its `env:` drive and its `GetEnvironmentVariables` method, the drive inside `pwsh -c` text included. An environment dump by an interpreter or `awk`, such as `python3 -c "import os; print(os.environ)"`, `node -p process.env` or `awk` reading `ENVIRON`, passes. `echo "$TOKEN"` prints a variable the shell already holds; `with-secrets` keeps a value out of the shell so there is nothing there to print.
- The hook refuses some commands that read nothing secret, such as `cat *` and `head docs/*`, whose globs may match a `.pem` or `.key` file, and `find . -name .env`. Name the files, or use `ls`. A search for the PowerShell method's full name, such as with `grep` or `git log -S`, is refused too; search for part of it.
- A write to a secrets file by a redirection passes, such as `echo A=1 > .env`; a program that also reads, such as `cp` or `tee`, is refused.
- `with-secrets` narrows where a value goes; it does not seal it. A child that prints its environment, an interpreter told to, or a program that starts a shell itself, such as `make`, `npm run` or `npx`, can still show the value. A copy of a shell under another name, not a link, passes. Its output is shown as it is, never masked.
- Whether Codex reads the project's profile was tested with the same settings given on the command line (`codex sandbox -c ...`), which refused each pattern. That it loads them from the project file in a trusted project is inferred.

## Rules

| Rule | Enforced by |
|---|---|
| Both agent tools' settings deny reading the secrets files, and name the documentation domains web reads may reach. | `agent_settings#a missing Claude Code deny entry fails` |
| An agent's shell command runs none of the environment dumps listed above and reads no secrets file, with the misses under "Limits". | `secrets_shell#printenv prints the environment`, `secrets_shell#cat of .env is refused` |
| A program that needs a value from the secrets file runs through `python3 ws.py with-secrets`, which refuses a shell, `env`, `printenv` or a program that runs another as its child. | `secrets_shell#with-secrets with a shell is refused` |
| A new linked worktree gets a copy of the ignored local settings file. | `prose` |
