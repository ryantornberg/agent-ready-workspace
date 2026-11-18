---
kind: decision
status: accepted
last-reviewed: 2026-11-14
---

# 0001: The workspace pins code repositories; it does not copy them

**In short:** The workspace is its own repository. It includes each code repository as a git submodule fixed at an exact commit, so every doc describes a known version of the code.

## Context

An agent needs the team's context next to the code it is changing. There are three places that context could live: inside each code repository, in a copy of the code, or in a separate repository that points at the code.

## Decision

Keep the workspace separate and pin each code repository under `src/` as a submodule. When a change merges upstream, move the pin forward and re-run the checks.

## What it gave up

- A newcomer runs one more command after cloning.
- A doc can describe a commit that is a few days behind the code's main branch. The pin makes that visible; it does not prevent it.

## Options rejected

- **Docs inside each code repository.** Reviewers of code changes would see every doc edit, and nothing could describe how several repositories fit together.
- **A copy of the code.** A copy drifts, and nobody can say which version a doc describes.
