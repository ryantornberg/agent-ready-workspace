---
kind: decision
status: accepted
date: 2026-11-23
deciders: the maintainer, through M3's approved plan
last-reviewed: 2026-11-23
---

# 0016: A spec lives in its plan, changes only by dated entries while the work is built, and is kept as written once its plan is done

**In short:** work that climbs the ladder gets one defined spec process, sized to the work, with a person's yes between phases and no command of its own. The spec is three sections of the hand-off plan. While the work is built, a change to it is a dated entry, made before the code changes. Once the plan is `done`, the spec is kept as the record of what was agreed, and the tests its criteria name carry what stays true.

## Context

Without one defined process, each piece of work invented its own, and a newcomer had to work out the process from old examples.

The source pages disagreed on what happens to a spec over time. One said specs persist and change with the code. Another said a spec is frozen once written. Each has a cost. A spec edited after the fact no longer says what was agreed, so nobody can check the work against it. A spec frozen and forgotten goes stale beside the code, and the next reader trusts it.

## Decision

- **One process, sized to the work.** Work that passes [the size gate](../size-the-work.md#the-gate) has no spec. Work that climbs the ladder follows [the spec process](../size-the-work.md#the-spec-process): specify, plan, slice, build.
- **A person between phases.** The person agrees to the spec before the plan is written, and approves the plan before any slice runs.
- **The spec is part of the plan.** Its goal, non-goals and success criteria are sections of the [hand-off plan](../templates/hand-off-plan.md). It has no file, no status and no command of its own; the plan's `status` carries it.
- **While the work is built, the spec changes with the code.** The spec is updated first, then the code. Before approval, its sections are edited and agreed again. After approval, a change is a dated entry under "Changes after approval", as the template's rule 6 says.
- **Once the plan is `done`, the spec is kept as written.** It is the record of what was agreed and why. It is not edited to match later code. Each success criterion names the command that checks it, so the tests carry what stays true. A later change to the same behavior passes the size gate as any change does: a small one goes to fix a bug, and a larger one gets its own plan, which links the old one.

## What it gave up

- **No single page says what a feature does today.** A reader finds it in the tests, the reference pages and the newest plan that touched it.
- **Small changes still need an entry.** After approval, even a one-line change to a criterion is a dated, approved entry.

## Options rejected

- **Throwaway specs.** Nothing would record what was agreed, or why.
- **Specs kept in step with the code forever.** Each edit erases what was agreed at the time, and keeping every spec current is work nobody owns once the plan is done.
- **Code generated from specs.** It moves the design into the spec, which the process keeps out: a spec says what will be true, not how.
- **A command of its own for the process.** The ladder and the plan template already hold it; a command would be one more thing to keep in step.
