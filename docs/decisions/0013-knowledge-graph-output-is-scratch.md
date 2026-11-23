---
kind: decision
status: accepted
date: 2026-11-23
deciders: the maintainer, through M3's approved plan
last-reviewed: 2026-11-23
---

# 0013: A knowledge graph of the code is a scratch tool, and its output is never stored

**In short:** a tool that builds a knowledge graph of the code may be run when a question needs it. Its output stays outside the repository and is deleted after use. No page, check or index reads a stored graph.

## Context

Graph tools read a codebase and output its parts and the links between them. Their output looks like a free code map. In use, two problems showed. Nobody kept the stored output current, so it described code that had moved. And some of the links it inferred did not exist in the code.

An unmaintained generated artifact is worse than none. A reader trusts it because it looks generated, and it is wrong in ways nobody wrote down.

## Decision

- **Run it on demand,** for one question, such as "what calls this across the repositories".
- **Its output is scratch.** It goes in a session's scratch folder, outside every repository, and is deleted when the question is answered. A finding worth keeping is checked against the code and written down as the [research ladder](../research-ladder.md#offer-to-write-a-finding-down) says.
- **Nothing stored.** No graph output is committed, and no page, check or index row links one.

## What it gave up

- **Each use pays the build again.** A question that needs the graph waits for it.
- **No shared graph.** Two sessions asking related questions each build their own.

## Options rejected

- **Refreshing it on a schedule.** It would stay current, but the invented links would still be there, now on a timer.
- **Replacing code maps with it.** Code maps, due in M5, are written and checked against the pinned code; a graph's inferred links are not.
