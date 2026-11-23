---
kind: decision
status: accepted
date: 2026-11-15
deciders: the maintainer
last-reviewed: 2026-11-15
---

# 0003: The engine in one folder

**In short:** the engine's code lives in `wslib/`, and only there. The few files outside it that start the engine, such as `ws.py`, hold no code of their own. The engine has a version, and the manifest must name the same one.

## Context

Later work copies the engine into other workspaces and keeps those copies in step. A copy is easy to compare when the engine is one folder and a short list of files. It is hard when the runner's commands sit in a file at the top of the workspace, next to the workspace's own pages and manifest.

Before this change, `ws.py` held every command of the runner, and `tools/symbols.py` held the lookup's command line. Both sat outside `wslib/`.

A copied engine also needs a way to say which manifest it can read. A manifest written for one engine may mean something different to the next one: a setting renamed, or a key added. Nothing recorded which engine a manifest was written for.

## Decision

- **`wslib/` holds the engine.** That is the runner (`wslib/runner.py`), the part loader, the snapshots, the markdown and symbol readers, the event adapters, the edit ledger and the launcher. A workspace's own files never sit in it.
- **Entry points stay where people and tools look for them, and only start the engine.** `ws.py` is the command every page names. `tools/symbols.py` is the lookup the contract names. `.githooks/` is where git finds its hooks, and `.claude/settings.json` is where the agent tool finds its wiring. A test fails if `ws.py` or `tools/symbols.py` defines a function or a class, or imports anything but `wslib`, `pathlib` and `sys`.
- **The engine has a version.** `VERSION` in `wslib/__init__.py`, printed by `python3 ws.py --version`. The manifest's `version` must equal it, or every command refuses, hook calls included.

## What it gave up

- **An upgrade cannot be made one file at a time inside an agent session.** Once the engine's version and the manifest's differ, every hook call is refused, including the edit that would make them match. So an upgrade lands as one step: a merge, a checkout, or a copy from the person's own terminal. A hook that read a manifest written for another engine could misread a setting and allow what it should refuse. Failing closed is the plan's rule.
- **Every engine release changes the manifest.** Each workspace edits one line when it takes a new engine.

## Options rejected

- **Rename `wslib/` to `engine/`.** Every part, and every part a team has written, starts with `from wslib.parts import finding`. A rename breaks all of them for a clearer folder name.
- **Move `ws.py` into the folder.** Every page, hook and CI step runs `python3 ws.py`. Keeping it at the top, with no code of its own, costs nothing.
- **Move `parts/` into the engine.** A workspace adds its own parts next to the ones it takes. The parts are copied by name, not as a folder.
- **Let a hook call go ahead on a version mismatch.** It would avoid the lockout above, but it would run hooks on settings this engine may read differently. That is failing open.
