---
kind: decision
status: accepted
date: 2026-11-23
deciders: the maintainer, through M3's approved plan
last-reviewed: 2026-11-23
---

# 0014: Work runs at one of three tiers, bound to models in one place, with no hook that nudges

**In short:** every task is driver, worker or mechanical work, and one manifest entry binds each tier to a model and an effort level. A delegated task names its tier on its prompt's first line. No hook tells a session to change model. [Orchestration](../orchestration.md) holds the rules.

## Context

Most of the spend on agent work came from interactive sessions on the largest model. A report over 30 days showed about 91% of output tokens on the top tier. The main sessions were all on it, while the helpers they started already ran mostly on cheaper ones. The first reading of that report was wrong, because it scanned the main sessions' transcripts only.

A hook was then added that nudged a session toward a cheaper model or a lower effort when the task looked simple. It misfired, and the model was already making those moves on its own, so the hook was removed. Heavier tier machinery had also cost more than the evidence for it.

## Decision

- **Three tiers.** Driver for judgment, worker for bounded work against a plan, mechanical for reading and sweeping. Stakes raise the tier, as orchestration lists.
- **One binding.** The `tiers` entry in [workspace.json](../../workspace.json) maps each tier to a model and an effort. It is the only place a tier's model is set. The eval harness picks the model for its runs on its own, as [evals](../../evals/README.md) says.
- **Lower effort before lowering the model.**
- **Delegating saves context, not tokens.** A helper reads widely so the main session does not have to; the bill drops only when the helper runs on a cheaper tier.
- **Checked where it is cheap.** The `handoff_tier` hook refuses a delegated task whose prompt's first line does not name its tier. Where the agent tool lets a task set its model and effort, it also refuses one that sets them off the binding or leaves one unset, as [orchestration](../orchestration.md#what-enforces-this) says. Nothing else is enforced.
- **No nudge.** No hook suggests or forces a model change in the session a person talks to. The person picks that model.

## What it gave up

- **Nothing checks that a tier fits the work.** A slice that should run at the driver tier can be handed off at the worker tier; the person reading the plan is the check.
- **The person's own session is unmanaged.** Most spend sits there, and this decision leaves it to the person.

## Options rejected

- **A hard gate on model choice.** It would block work on a guess about how hard the task is.
- **A nudge hook.** It misfired, and the model already made the moves it suggested.
- **Hidden per-procedure downgrades.** A procedure that quietly ran a cheaper model would make its results hard to trust and hard to compare.
