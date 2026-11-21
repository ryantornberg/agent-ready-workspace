---
kind: reference
last-reviewed: 2026-11-21
---

# Commits

What every commit to this workspace must hold, and which checks hold it. It is for anyone, person or agent, about to commit.

**In short:** a commit's subject follows one of the formats the manifest accepts, conventional commits by default, and a commit adds no line that looks like a credential. The commit-msg and pre-commit hooks check both; CI scans the whole history for credentials too.

## The subject line

The subject is the message's first line that is neither blank nor a comment. It matches one of the regular expressions in the `commit_subject` entry's `formats` in [workspace.json](../workspace.json). With no `formats`, it is a conventional commit: a type (`feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf`, `ci`, `build`, `style` or `revert`), an optional scope in brackets, an optional `!`, a colon and a space, then the summary. For example: `fix(lease): keep the holder's start time`.

git's own subjects always pass: a merge, a revert, and an autosquash subject starting `fixup!`, `squash!` or `amend!`. A subject over 72 characters warns; put the detail in the body.

A team sets its own formats in the manifest, such as `"formats": ["^[A-Z]+-[0-9]+ \\S"]` for a ticket key first.

## Credentials

The secret scan reads every line a commit adds, at the commit against the last commit and in CI against the base branch. It matches the formats of common tokens and private keys: GitHub, AWS access key ids, private key blocks, Slack, Anthropic, OpenAI, Google API keys, Stripe live keys and npm tokens. In CI, `python3 ws.py check --history` reads every line every commit in the history added.

A finding names the format and the first four characters only, so the output is safe to paste. If it fires:

1. Take the value out of the file.
2. Revoke the token with its issuer. A token that reached a pushed commit is exposed, and deleting it later leaves it in the history.
3. Run `python3 ws.py check --staged` again.

A test value is built from pieces at run time, or written with JSON escapes in a cases file, so the file's text never holds a whole token.

The scan is a seatbelt, not a vault. A format it does not know, a token split across lines and a secret in a binary file pass.

## Rules

| Rule | Enforced by |
|---|---|
| A commit's subject follows one of the manifest's formats; git's own merge and revert subjects pass. | `commit_subject#a subject with no type fails` |
| A commit adds no line that looks like a token or a private key. | `secret_scan#an added line with a GitHub token fails` |
| Every finding a check prints names the file, the rule's page and a command to run it again. | `prose` |
