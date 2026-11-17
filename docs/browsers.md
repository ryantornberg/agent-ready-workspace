---
last-reviewed: 2026-11-16
---

# Browsers: one per session

How an agent session in this workspace gets a browser, and why each session gets its own. It is for anyone who runs more than one agent session at a time, or who sets up a new machine.

**In short:** the browser server runs from the workspace's own config, pinned to an exact version, with `--isolated`. Each session then gets its own browser profile in memory, so two sessions never fight over one. The agent tool's own browser plugin stays off. The `browser_isolation` check fails a commit that breaks any of this.

## Why

Without `--isolated`, the browser server keeps one profile folder per user on disk. When a second session opens a browser while the first has one open, the second fails with "Browser is already in use for ..., use --isolated to run multiple instances of the same browser". The opt-in test in `tests/test_browser.py` shows both sides: two isolated servers both open a page, and two that share a profile folder collide.

## What is set, and where

| File | What it holds | For |
|---|---|---|
| [.mcp.json](../.mcp.json) | The browser server, `@playwright/mcp` at an exact version, with `--isolated` | Claude Code |
| [.codex/config.toml](../.codex/config.toml) | The same server, in Codex's own project config | Codex CLI |
| [.claude/settings.json](../.claude/settings.json) | `enabledPlugins` sets the browser plugin to `false` | Claude Code |

The plugin is turned off by name, not left out. A key left out lets user settings turn the plugin on, and then the session runs two browser servers, one of them without isolation.

The version is exact, never `latest` or a range, so every session runs the same server. Move it on a branch, like any machinery change, and pick a release at least two weeks old.

## On Windows

Starting `npx` straight from the config often fails on Windows. Run it through the command shell instead:

```json
{"mcpServers": {"playwright": {"command": "cmd", "args": ["/c", "npx", "@playwright/mcp@0.0.84", "--isolated"]}}}
```

The check accepts this form: it looks for the pinned package and `--isolated` among the arguments.

## Things to know

- **An isolated browser forgets everything when the session ends:** logins, cookies and local storage. Sign in again in each session.
- **The server uses the installed Chrome by default.** On a machine without Chrome, install it, or name another browser with the server's `--browser` option.
- **Local settings can undo this.** The check reads only committed files. A machine-local settings file, such as `.claude/settings.local.json` or your user settings, can turn the plugin back on, and the project's `false` loses to the local file. If a session lists two browser servers, look there.
- **Tool names differ.** The project's server names its tools `mcp__playwright__...`; the plugin's are `mcp__plugin_playwright_playwright__...`. A permission or hook that matches browser tools by name must name the prefix in use.
- **A running session keeps its old server.** Restart the session after the config changes.
- **Claude Code asks once.** An interactive session asks you to approve the project's server the first time it appears.
- **Codex is not shown loading it yet.** The check holds Codex's config to the same rule, but no recorded Codex run here shows the server starting. A recorded Claude Code session does: [tests/records/claude-code-browser-session.json](../tests/records/claude-code-browser-session.json).
