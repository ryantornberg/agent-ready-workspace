---
kind: reference
last-reviewed: 2026-11-21
---

# Agent settings

What the agent tools' committed settings allow and deny here, and what they cannot. It is for anyone changing those settings or adopting them.

**In short:** Claude Code is denied reading the secrets files and may fetch eight documentation domains. Codex CLI gets a permissions profile with the same denies inside the workspace, defined but not the default, and the same domains for its web search. A new worktree gets a copy of the ignored local settings file. The `agent_settings` check fails when an entry goes missing.

## The secrets files

These are the files an agent should never read: `.env` and `.env.*` anywhere in the workspace, `*.pem` and `*.key` files, and any `secrets/` folder. Claude Code's deny list adds the home folder's credential files: `~/.ssh`, `~/.aws`, `~/.netrc`, `~/.git-credentials`, gh's sign-in file, and the folder that holds the private deny list.

| Tool | Where | What it does |
|---|---|---|
| Claude Code | `permissions.deny` in [.claude/settings.json](../.claude/settings.json), as `Read(<pattern>)` | Its read tools refuse the file. A shell command is not covered; slice C5 refuses reads of the secrets files there. |
| Codex CLI | The `agent-ready` profile in [.codex/config.toml](../.codex/config.toml), each pattern `"none"` under `":workspace_roots"` | The sandbox refuses the file to every process the agent starts. |

The Codex profile is defined but not made the default. Making it the default would replace a person's own sandbox setting for this project, and its base, `:workspace`, turns off network access and writes to the home folder. To use it, start Codex with `codex -c default_permissions="agent-ready"`, or set that line in your own config. Since it reaches every process, it denies nothing in the home folder: a home entry such as `~/.ssh` would also stop `git push`.

## The documentation domains

Claude Code's web fetch may read these without asking, through `WebFetch(domain:...)` entries in `permissions.allow`: `docs.python.org`, `git-scm.com`, `docs.github.com`, `cli.github.com`, `code.claude.com`, `docs.anthropic.com`, `developers.openai.com` and `learn.microsoft.com`. Codex CLI has no web fetch; its web search lists the same domains in `allowed_domains` under `[tools.web_search]`.

## The worktree's copy

`.claude/settings.local.json` holds a person's own permissions and is ignored by git, so `git worktree add` leaves it behind. The `post-checkout` git hook copies it from the main working copy into each new linked worktree, and never overwrites one already there. See [decision 0004](decisions/0004-the-hook-contract.md).

## Limits

- The check reads the committed files only. A person's own settings, or a local settings file, can loosen either tool.
- Whether Codex reads the project's profile was tested with the same settings given on the command line (`codex sandbox -c ...`), which refused each pattern. That it loads them from the project file in a trusted project is inferred.

## Rules

| Rule | Enforced by |
|---|---|
| Both agent tools' settings deny reading the secrets files, and name the documentation domains web reads may reach. | `agent_settings#a missing Claude Code deny entry fails` |
| A new linked worktree gets a copy of the ignored local settings file. | `prose` |
