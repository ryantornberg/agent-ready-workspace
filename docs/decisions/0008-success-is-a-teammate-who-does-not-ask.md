---
kind: decision
status: accepted
date: 2026-11-23
deciders: the maintainer, through M3's approved plan
last-reviewed: 2026-11-23
---

# 0008: The workspace makes agent work a team practice, and success is a teammate who does not have to ask

**In short:** the workspace exists so that a team, not one person, can hand real work to coding agents. It succeeds when a teammate ships a real change with an agent without asking the person who wrote the workspace. Its size and polish are not measures.

## Context

A workspace like this one grows. Each new page, check and hook feels like progress, and each can be counted. None of those counts says whether anyone other than its author can use it.

The question that matters is narrower. Can a teammate who did not build the workspace take a real task, work it with an agent, and finish it the way the team agreed, without stopping to ask the author what something means or where it lives?

## Decision

- **The purpose** is to make agent-assisted work a practice the whole team shares: the same contract, the same procedures and the same checks, whoever runs the session.
- **The measure** is a teammate shipping a real change without asking the author. Each question they had to ask is a gap in the workspace. The [question log](../question-log.md) records each one, and the contract's rule says to add it before finishing.
- **Not measures:** the number of pages, checks or lines, a smaller always-loaded layer for its own sake, or how finished the workspace looks. A size ceiling, such as the one on the always-loaded layer, is a cost control, not a goal.

## What it gave up

- **The measure is slow.** It needs a teammate and a real task. A milestone can add many pages before anyone outside tests one.
- **Questions not asked are invisible.** A teammate who gives up, or guesses, leaves no row in the log.

## Options rejected

- **"Smaller is success."** Cutting text is easy to count and says nothing about whether a teammate can finish a task. Each cut still has to pass the same test as an addition.
- **Size and polish as progress.** More pages, checks and hooks can make the workspace harder to use, not easier.
