---
kind: decision
status: accepted
date: 2026-11-23
deciders: the maintainer, through M3's approved plan
last-reviewed: 2026-11-23
---

# 0009: The workspace holds what nobody can derive, and each new mechanism carries the burden of proof

**In short:** the workspace holds four things: facts a fresh session cannot work out, cheap insurance against a costly misreading, what a person needs to understand the work, and the team's agreed process. It refuses content a model or the code already gives, and coaching on how to think. Whoever adds a playbook, check or hook must show it is needed.

## Context

Fresh sessions with no workspace were asked the questions a contract usually answers. They found most of the answers on their own, from the code and the repository. Where a page restates what a session can derive, it costs reading time and adds nothing.

One kind of fact was different. A trap fact, such as a service that looks current and is kept read-only, took a fresh session its whole budget and it still got it wrong. Writing that fact down costs one line. That is the case for cheap insurance.

## Decision

The workspace holds:

- **Facts nobody can derive** from the model or the code: which service is live, what the team calls things, what was decided and why. The contract's "Facts a model cannot derive" section is the first example.
- **Cheap insurance:** a short note on an ambiguity that is costly to get wrong, even when a careful session might work it out.
- **Human understanding:** what a person needs to follow and judge the work, such as tutorials, decision records and the reasons behind rules.
- **Team process:** how this team agrees to finish work, such as the [definition of done](../definition-of-done.md) and [procedure endings](../procedure-endings.md).

It refuses:

- **Pre-digested derivable content:** summaries of code a session can read, and lists a command can print.
- **Model coaching:** advice on how to think that the model already follows unaided.

**The burden of proof** sits with each new mechanism. A playbook is written only after a run without it fails, as the [evals rules](../../evals/README.md#rules-that-make-this-worth-doing) say. By exception, a procedure an approved plan ports skips that run: it ships unproven and names the milestone that will prove it, as [decision 0006](0006-what-proven-means.md) and step 3 of [extend the workspace](../extend-the-workspace.md#steps) say. A check or hook states in its manifest `why` what it guards against.

## What it gave up

- **Some useful-looking pages are refused.** A newcomer may want a summary that a session could derive; the workspace sends them to the code instead.
- **Other pages have no such test.** A reference page, how-to or decision record shows its need only in the judgment of whoever adds it, and of its instruction review.
- **The line is a judgment.** Whether a fact is derivable depends on the model and the code at the time. The test is applied when a page is added, and again when its milestone tries to prove it.

## Options rejected

- **Hold everything a newcomer might want.** It grows without limit, and much of it goes stale against the code it summarizes.
- **Hold only what a check can enforce.** Decisions, reasons and process cannot be checked, and they are much of what a teammate lacks.
