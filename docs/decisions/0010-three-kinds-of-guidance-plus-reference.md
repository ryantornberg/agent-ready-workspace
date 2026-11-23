---
kind: decision
status: accepted
date: 2026-11-23
deciders: the maintainer, through M3's approved plan
last-reviewed: 2026-11-23
---

# 0010: Guidance comes in three kinds, plus reference, and each concept has one term

**In short:** a page that guides work is a playbook an agent runs, a how-to for one task, or a tutorial a newcomer walks through once. Facts to look up are reference. Each concept has one term across the workspace. The other page kinds hold records, plans and shapes to copy.

## Context

Guidance once sat in five overlapping kinds of page. A newcomer could not tell which kind to open, and the same procedure turned up in two of them, worded two ways. Two names for one thing made a reader wonder whether they were two things.

## Decision

- **Three kinds of guidance.** A *playbook* is steps an agent follows from request to report. A *how-to* is steps for one task, for a person or an agent. A *tutorial* is a walk-through a newcomer runs once.
- **Plus reference.** A *reference* page holds facts to look up, not steps.
- **The other kinds.** Templates, records, decision records, plans and milestone records each have their own kind and folder, as [layout](../layout.md#page-kinds) lists. They are shapes to copy or records of what happened, not one of the three kinds. This is a split of page kinds only: the [instruction review](../playbooks/instruction-review.md#when-it-runs) uses "guidance page" in a wider sense, and reviews templates and decision records too.
- **One term per concept.** A page calls a thing in the code by the name the code uses, which the [index's search aliases](../../INDEX.md#search-aliases) map from everyday words, and a workspace concept by its [glossary](../glossary.md) word. A title uses the industry's standard term where one exists, as the [reader standard](../reader-standard.md#names) says.

The `page_kinds` check holds every page under `docs/` to one of the kinds, with the front matter its kind needs.

## What it gave up

- **Some pages sit between kinds.** A page with both steps and facts must pick one kind; the facts move to a reference page or a section.
- **Renaming has a cost.** A settled term is kept even where a better one appears later, unless the change goes through every page that uses it.

## Options rejected

- **One merged tree of pages.** It drops the difference between steps an agent runs and facts it looks up, which decides how a page is written and checked.
- **All five kinds, with a legend.** The legend explains the overlap; it does not remove it.
