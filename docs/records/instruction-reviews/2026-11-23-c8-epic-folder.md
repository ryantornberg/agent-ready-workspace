---
kind: record
last-reviewed: 2026-11-23
covers: docs/templates/epic-folder.md
reviewed-at: 157570e, with the uncommitted change of slice C8
---

# Instruction review: docs/templates/epic-folder.md

This records the review of C8's edit to the epic folder template, the sentence naming M3's plan, for its author and its readers.

**In short:** 0 findings. The example now names "the kit's M3" without a link into `docs/plans/`, which an instance never gets, and it is still true.

## Scope

In scope: in "When to use it", the sentence that starts "Otherwise the work stays one hand-off plan", whose example changed from a link to M3's plan to the words "the kit's M3". The whole page was read, with `git diff docs/templates/epic-folder.md` for the change. Read beside it: `AGENTS.md`, `INDEX.md`, `kit/kit.json`, `docs/decisions/0007-the-kit.md`, `docs/templates/hand-off-plan.md` (by its link), the list of `docs/plans/`, and the front matter and title of `docs/plans/m3-reading-layer-machinery-and-kit.md`.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|

No findings.

## Checked with no finding

- contradiction: M3 has one plan, `docs/plans/m3-reading-layer-machinery-and-kit.md`, with `milestone: M3`. There is no M3 folder under `docs/plans/` (verified, by listing it). The sentence holds in the kit and in an instance, where "the kit's" says whose milestone it is.
- step: the sentence gives no step. The removed link pointed into `docs/plans/`, which `kit/kit.json` never syncs. An instance adopted with this page synced passes `python3 ws.py check` (verified, running).
- trigger: the section's two conditions for an epic folder are unchanged; only the example changed.
- enforcement: the changed sentence states no must or never.
- placement: the page is synced, as a template under `docs/` (verified, reading `kit/kit.json`), so an example both the kit and an instance can read fits it. In the kit's own repository the plan is no longer one click away, but the sentence still names it.
- eval-case: the page is a template with no proof mark, and the change asks no new behavior of an agent.
