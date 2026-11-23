---
kind: decision
status: accepted
date: 2026-11-23
deciders: the maintainer, through M3's approved plan
last-reviewed: 2026-11-23
---

# 0017: A large piece of work keeps its plans in one folder, with a hub page

**In short:** work that needs three or more plans or specs, or is an epic in the tracker, gets one folder under `docs/plans/`. Its README is the hub: the goal, where the work stands, every doc it has and its open questions. Smaller work keeps one plan file. The [epic folder template](../templates/epic-folder.md) holds the shape.

## Context

One large piece of work once had its documents spread across the folders for each page type: plans in one, specs in another, open questions somewhere else. Nobody could see in one place what the work was or where it stood.

## Decision

- **The threshold:** three or more plans or specs, or an epic in the tracker. Below it, one plan file.
- **One folder,** `docs/plans/<epic-slug>/`, holding the work's plans. Every page in it but the hub is a plan; the work's other documents live where their kind lives, and the hub links them, as the [template](../templates/epic-folder.md#where-it-lives-and-how-it-is-named) says.
- **One hub,** the folder's `README.md`: the goal, where the work stands, every doc the work has, and its open questions.
- **Questions stay with the work.** The hub holds the work's open questions, not one page shared by every piece of work.

## What it gave up

- **Two places for plans.** A reader looks in `docs/plans/` and in each epic folder in it.
- **The threshold is a count.** Work just under it keeps separate plan files, even when it will grow.

## Options rejected

- **A subfolder per page type inside the work's folder.** It brings back the scatter one level down.
- **One questions page for every piece of work.** It mixes questions from unrelated work, and nobody owns it.
