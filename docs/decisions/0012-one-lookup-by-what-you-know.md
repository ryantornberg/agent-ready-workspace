---
kind: decision
status: accepted
date: 2026-11-23
deciders: the maintainer, through M3's approved plan
last-reviewed: 2026-11-23
---

# 0012: An agent picks one lookup by what it already knows, and code maps never block a commit

**In short:** a symbol lookup finds a name in the code, the index finds a topic, and an agent picks the one lookup that fits what it already knows. It never stacks a second to confirm the first. Code maps per repository come in M5, and their freshness will warn, never block.

## Context

Agents spent most of their context finding things. Two fixes were tried: a generated table of every symbol, with a command to look one up, and code maps, a short page per repository on how it is laid out.

Then the lookups were measured, in paired fresh sessions, one of each pair kept from the index. Stacking lookups, one to find and another to confirm, cost about 14% more tokens, and still 5% more after the guidance was reworded. Finding a bug's place across several repositories cost about 30% less with the lookups. A topic lookup made no difference. Each cell was one run, so these numbers point the way; they do not settle it.

Later, the code maps' freshness was made a gate that refused a commit while a map was stale. It blocked work for drift the work had not caused, and it was turned back into a warning.

## Decision

- **One lookup, picked by what you know.** An exact name goes to `python3 tools/symbols.py NAME src`. A topic goes to [INDEX.md](../../INDEX.md). The [research ladder](../research-ladder.md) lists every row. The contract says the same in "Finding things".
- **Do not stack lookups.** A second lookup to confirm the first, or several at once on one question, is not used.
- **Code maps wait for M5,** with the first instance. When they come, their freshness is judged against the pinned commits, not the checkouts. A stale map warns, and a check that needs its symbols reports, as a warning, that it did not run. No commit is refused for a stale map.
- **The routing sentences change only with a new measurement.** A rewording of "pick one lookup" is tested, not assumed better. Nothing enforces this beyond the eval's hash of the contract, which covers "Finding things" and not the research ladder.

## What it gave up

- **One run per cell.** The measurement behind the rule is thin. A later milestone that measures again may change it.
- **Until M5, no code maps.** An agent new to a repository reads its code, its README and the index.

## Options rejected

- **Stackable lookups,** each confirming the last. They measured worse.
- **Code-map freshness as a gate.** It refused commits for drift they did not cause, and was routed around.
- **A mandate to use the lookups.** The ladder offers the cheapest lookup that fits; it does not require one before every read.
