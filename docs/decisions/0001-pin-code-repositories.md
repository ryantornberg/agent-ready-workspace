---
kind: decision
status: accepted
date: 2026-11-14
deciders: the maintainer
last-reviewed: 2026-11-14
---

# 0001: The workspace pins code repositories; it does not copy them

**In short:** The workspace is its own repository. It includes each code repository as a git submodule fixed at an exact commit, so every doc describes a known version of the code. A person's own agent memory and notes stay outside it, and the only personal files inside it are the few an agent tool reads from a fixed place there, kept out of git.

## Context

An agent needs the team's context next to the code it is changing. There are three places that context could live: inside each code repository, in a copy of the code, or in a separate repository that points at the code.

## Decision

Keep the workspace separate and pin each code repository under `src/` as a submodule. When a change merges upstream, move the pin forward and re-run the checks.

Amended 2026-11-23, M3 slice B5: personal content stays out of the workspace. A person's agent memory and notes live outside this repository, so it holds only what the team shares. A page never points into one person's agent memory or scratch folder, since no other reader can open it; [maintain the workspace](../maintain-the-workspace.md) makes finding such a pointer a duty. By exception, a personal file stays inside the working copy when a tool reads it only from a fixed place there, and it is never committed: Claude Code's `.claude/settings.local.json`, which git ignores, and the secrets file that `ws.py with-secrets` reads, `.env` at the top of the main working copy, which agents are denied reading, as [agent settings](../agent-settings.md) says. Session output, such as `.claude/worktrees/` and `.playwright-mcp/`, stays in folders git ignores.

## What it gave up

- A newcomer runs one more command after cloning.
- A doc can describe a commit that is a few days behind the code's main branch. The pin makes that visible; it does not prevent it.

## Options rejected

- **Docs inside each code repository.** Reviewers of code changes would see every doc edit, and nothing could describe how several repositories fit together.
- **A copy of the code.** A copy drifts, and nobody can say which version a doc describes.

