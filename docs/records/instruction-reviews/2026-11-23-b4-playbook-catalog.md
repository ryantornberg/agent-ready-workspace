---
kind: record
last-reviewed: 2026-11-23
covers: docs/playbooks/README.md
reviewed-at: 1a18d68, with the uncommitted change of the B4 slice session
---

# Instruction review: docs/playbooks/README.md

This records the instruction review of slice B4's edit to the playbook catalog, for its author and for critics.

**In short:** 4 findings: 1 contradiction, 1 enforcement, 2 trigger, none blocking. The new section's rule on where a lane playbook's row goes is not labelled as an exception to "in its stage". Its no-wrapper rule has no Rules row. Two rows fire where the pages they lead to do not settle the request.

## Scope

In scope: the uncommitted edit, which adds the section "Lane drafts" with its intro and four rows: regression run, regression triage, QA verification list and feature layer walk. Also in scope: anything on the page, or on a page it links to, that the change contradicts or leaves stale.

Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/extend-the-workspace.md`, `docs/reading-paths.md`, the four new playbooks in full, `docs/saved-workflows.md`, and the opening of `docs/playbooks/impact-analysis.md`. Ran `git diff -- docs/playbooks/README.md`. Ran a loop that checks every playbook in `docs/playbooks/` has a row. Ran `python3 ws.py check` at the start: it passed, with the known `eval_record` warning on `fix-a-bug.md`.

Not judged: while this review ran, the builder session added `docs/playbooks/standup-report.md` and `docs/playbooks/effort-estimate.md`, which have no row here yet. They were not part of the change handed to this review.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | "The catalog" intro and "Lane drafts" intro | Not blocking. "The catalog" says "A new playbook adds its row in its stage". "Lane drafts" says "A new lane playbook adds its row here, under its lane." A lane playbook is a playbook, so both apply, and neither labels the second as an exception to the first. Extend the workspace's routing table, which an author adding a page follows, also says "A row in the playbook catalog, in its stage" and knows no lane section. An author following it puts a lane playbook in a stage table. Either way a row is written in the catalog, so no write goes wrong. Verified: read both intros and extend the workspace's "Pick the kind and the place". | fixed: the stage rule in "The catalog" now names lane playbooks as its exception, and "Lane drafts" labels its rule as that exception. Extend the workspace's routing table still says "in its stage"; an author following it reaches this page, whose intro redirects. |
| 2 | enforcement | "Lane drafts" intro, and "Rules" | Not blocking. "None gets a wrapper until that milestone proves it" is a never. The page's Rules table has no row for it. Extend the workspace's step 4 asks for a row for every must and never on the page. `docs/reading-paths.md` states the same rule with a `prose` row, and `docs/saved-workflows.md` states it a third time, so no page is plainly its owner. Verified: read the Rules table and both other pages. | fixed: this page owns the rule; its Rules table gains "A lane draft gets no wrapper until the milestone its `prove-by` names proves it". Reading paths now links this table instead of stating the rule. |
| 3 | trigger | "Lane drafts", the QA verification list row | Not blocking. The row fires on "You write or check a document QA reads". The page's purpose line is for "the agent or person writing it", and its steps start by reading tickets and writing items. A request to check a document someone else wrote has no entry step and no default; only step 5, the self-check, fits it. Verified: read the row and the page's purpose and steps. Inferred: that an agent given a check-only request will either run the whole write procedure or improvise. | fixed: the row now fires on writing a document QA reads, not checking one. |
| 4 | trigger | "Lane drafts", the Feature layer walk row, against the Impact analysis row | Not blocking. The new row fires when "You start a feature of a known type and need every layer it touches"; its page says it fills a plan's slices. The Impact analysis row already fires on "planning slices", and impact analysis's own "When it runs" lists writing a plan's slices, with "Anything else: This page." The feature layer walk says impact analysis "runs once the change exists", which impact analysis does not say. The catalog row carries no tie-break, so a request to plan a new feature's slices matches both. Both pages only read, so no write goes wrong. Verified: read both rows, the feature layer walk's "When to use it, and which page wins" and impact analysis's "When it runs". | fixed: the row now says it lists the layers before a feature's slices are planned, and sends what a change to an existing path or name reaches to impact analysis. |

## Checked with no finding

- step: the change adds no step. Every new link resolves; the `links` check reported nothing on this page. The loop found a row for every playbook that was part of the change.
- placement: the section routes and links reading paths; it restates no procedure's steps and no rule of procedure endings.
- eval-case: the page is a reference. No eval case or arm in `evals/arms.json` reads it, and each new row routes to a page marked unproven with a `prove-by`. Each row's Proof cell matches its page's front matter: M10, M10, M6 and M9. Each row's title matches its page's heading, and the regression run and triage rows match their pages' purpose lines, including the local default and the fresh session.

## Re-check

A fresh session's reading after the fix round, on `1a18d68` with the uncommitted fix of the B4 slice session. It read `git diff -- docs/playbooks/README.md`, the QA verification list and the feature layer walk in full, impact analysis's "When it runs", and ran `python3 ws.py check`, which reports nothing on this page.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | Verified: "The catalog" names a lane playbook as the exception to the stage rule, and "Lane drafts" labels its own rule as that exception. |
| 2 | upheld | Verified: the Rules table gains "A lane draft gets no wrapper until the milestone its `prove-by` names proves it", and reading paths links this table. |
| 3 | upheld | Verified: the row now fires on "You write a document QA reads". See "What a fix broke". |
| 4 | upheld | Verified: the row says it lists the layers before a feature's slices are planned, and sends what a change to an existing path or name reaches to impact analysis. The walk's page says to run both when filling slices, so the rows compose. |

What a fix broke:

- Not blocking. Finding 3's fix narrowed the row to writing, while the QA verification list's own finding 4 fix widened that page to checking: its purpose line names checking, and its step 1 sends a check request to step 5. A request to check a QA document now matches no row here, though the page serves it. Verified: the row, and the page's purpose line and step 1.

What the first reading missed:

- None.

## Known defects

What stays open after the one fix round the plan allows, each not blocking.

- Not blocking, what a fix broke: the QA verification list row fires only on writing a QA document, while the page now also serves checking one. Known defect, for the docs audit.
