---
kind: decision
status: accepted
date: 2026-11-23
deciders: the maintainer, through M3's approved plan
last-reviewed: 2026-11-23
lane: automation
---

# 0018: An unattended run writes only to a branch, runs an approved task list, and its pin moves once, after the merge

**In short:** a run with nobody at the keyboard writes only to its own branch of the code repository, starts only once a person approves its task list, and stops after the fix rounds its plan allows. The workspace's pin moves once, only when every task passed, after a person merges the branch. These rules bind any harness an instance builds. This workspace ships no harness.

## Context

An unattended run can make many changes before anyone looks. If it can write anywhere, one wrong step reaches what other people use. If it moves the pin as it goes, the workspace points at half-done work for as long as the run lasts, and at broken work when it stops partway.

A loop harness that ran such tasks was built once, then removed as unused. The rules it followed were sound, and they are what this record keeps.

## Decision

- **A branch only.** The run writes to a branch of its own in the code repository. It never pushes to the default branch, publishes, merges or writes to another repository.
- **An approved task list.** A person approves the list of tasks before the run starts. The run does not add tasks.
- **One pin move, after the merge.** When every task passed, a person merges the run's branch into the code repository's default branch. Then the workspace's pin moves once, to that merge, as [decision 0001](0001-pin-code-repositories.md) moves any pin, and the `pin_on_default` check holds it to the default branch. The run itself writes nothing to the workspace. A run that stops early leaves the pin where it was.
- **It stops after its fix rounds.** A run stops after the fix rounds its plan allows, as [orchestration's limits](../orchestration.md#limits) say, then freezes and reports.

The automation lane's harness, if an instance builds one, follows these rules; its proof is M10's.

## What it gave up

- **Slower results.** Nothing a run produces is in use until a person merges the branch and the pin moves.
- **A partial success is not kept.** A run where most tasks passed still leaves the pin unmoved.

## Options rejected

- **Moving the pin after each task.** The workspace would point at work in progress.
- **The run moving the pin itself, at its end.** The ported rule did this. Here a pin must point at a commit on the code repository's default branch, which only a person's merge puts there, and a run writes to no repository but its own branch.
