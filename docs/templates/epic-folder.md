---
kind: template
last-reviewed: 2026-11-22
---

# Epic folder template

One folder for each large piece of work, with a hub page that says where the work stands. For the agent or person who plans an epic.

**In short:** work that needs three or more plans or specs, or is an epic in the tracker, keeps its plans in one folder, `docs/plans/<epic-slug>/`. Its `README.md` is the hub: the goal, where the work stands, every doc the epic has and its open questions. Below that size, the work keeps one plan file.

## When to use it

Make an epic folder when either holds:

- the work will have three or more plans or specs, counted together;
- the work is an epic in the team's tracker.

Otherwise the work stays one [hand-off plan](hand-off-plan.md) in `docs/plans/<name>.md`, however many slices it has. A milestone with one plan, such as [M3's](../plans/m3-reading-layer-machinery-and-kit.md), is one file, not a folder.

The folder exists so that one epic's docs are found in one place. Without it, an epic's plans, specs and questions end up spread across the folders for each page kind.

This hub is not the [project hub](hub.md). A project hub is the front page of one project's docs; an epic hub is the front page of one piece of work.

## Where it lives and how it is named

| Page | Path | Kind |
|---|---|---|
| The hub | `docs/plans/<epic-slug>/README.md` | `reference` |
| A plan for one story | `docs/plans/<epic-slug>/<ticket-key>-<story-slug>.md`, or `<story-slug>.md` when the story has no ticket | `plan`, a copy of the [hand-off plan template](hand-off-plan.md) |

`<epic-slug>` is the epic's name in two to four lowercase words, joined by hyphens. Put its ticket key in front when it has one, such as `ord-412-account-holds`.

Every page in the folder other than the hub is a plan; the page-kind check refuses anything else there. So the epic's other docs live where their kind lives, and the hub links them:

- the design spec for a story is the Goal, Non-goals and Success criteria of its plan, as [the spec process](../size-the-work.md#where-it-lives) says;
- an investigation, audit, retrospective or baseline is a record in `docs/records/specs/`, as the [spec template](spec.md) says;
- a decision record stays in [docs/decisions/](../decisions/);
- the open questions are a section of the hub, since a questions page would not be a plan.

When work crosses the threshold after its first plan is written, create the folder. Then:

- **A draft plan moves into it.** Move it with `git mv OLD NEW`. That stages both paths, so record both in the edit ledger: `python3 ws.py ledger --add OLD NEW`. Then fix each link the links check reports. If an approved plan or a signed-off record links the draft, leave the draft where it is, as for an approved plan.
- **An approved, done or abandoned plan stays where it is.** Its sections are frozen, as the [hand-off plan template](hand-off-plan.md#how-to-use-it) says in step 6, so its links cannot be fixed after a move. The hub lists it under "Docs elsewhere" with a link.

The commit section of [procedure endings](../procedure-endings.md#the-commit) says how the ledger and the commit work.

## Skeleton

The hub, `docs/plans/<epic-slug>/README.md`:

```markdown
---
kind: reference
last-reviewed: YYYY-MM-DD
---

# <Epic name>

<One sentence of 25 words or fewer: what this epic delivers, and who reads this hub.>

**In short:** <where the epic stands, and the next thing that happens.>

## Goal

<What is true when the epic is done, in two to four sentences. Link the tracker's epic item, if there is one.>

## State

<Where the work stands today: what has shipped, what is being built, what is blocked and on what. Date the paragraph.>

## Docs here

| Doc | What it covers | State |
|---|---|---|
| [<ticket-key>-<story-slug>.md](<ticket-key>-<story-slug>.md) | <the story, in one line> | <the plan's status: draft, approved, done or abandoned> |

## Docs elsewhere

| Doc | Where | What it holds |
|---|---|---|
| <name and link> | <a folder of this workspace, a code repository, or the tracker> | <one line> |

## Published pages

| Page | Where it is published | Its source here | Last published |
|---|---|---|---|
| <title> | <the wiki or other site, with a link> | <the page it is copied from> | <YYYY-MM-DD> |

## Open questions

| # | Question | Why it matters | Who can answer | Answer |
|---|---|---|---|---|
| 1 | <the question, in one sentence> | <what it blocks or changes> | <a person or a team> | <open, or the answer and where it is recorded> |
```

## Filling it in

1. **Copy the skeleton** into `docs/plans/<epic-slug>/README.md`. Write the goal first, since every other section is read against it.
2. **Keep "State" current.** Update it, and its date, whenever a plan in the folder changes status. The **In short** line changes with it.
3. **List every doc.** "Docs here" has one row for each plan in the folder, with the status from its front matter. "Docs elsewhere" has one row for each other page of the epic, wherever it lives, including a plan that stayed outside the folder.
4. **Name each published page.** A page copied to a wiki or another site gets a row, so a reader knows which copy is the source. Publishing is an outward write: [procedure endings](../procedure-endings.md#outward-writes) says when it needs a yes.
5. **Number open questions for good.** A question keeps its number after it is answered. Write the answer and link where it is recorded, such as a plan's "Settled decisions" or a decision record. Never renumber or delete a row.
6. **Write "none"** under a section that has nothing yet, rather than deleting it.

The hub's open questions are design questions the epic has not settled. A question the workspace should have answered goes in the [question log](../question-log.md) instead.

A product epic may also need questions for other teams, a tracker map or an unattended-run plan beside the hub. Their shapes are on the [epic satellites template](epic-satellites.md), a product lane draft.

## Rules

| Rule | Enforced by |
|---|---|
| Once work needs three or more plans or specs, or is a tracked epic, its plans go in one folder under `docs/plans/`. | `prose` |
| Every page in an epic folder other than its `README.md` is a plan. | `page_kinds#a page in a kind's folder must be of that kind` |
| Only a draft plan moves into an epic folder; an approved, done or abandoned plan stays where it is and the hub links it. | `prose` |
| A move records both its old and its new path in the edit ledger. | `edit_ledger#a staged deletion counts` |
| The hub lists every doc of the epic, here and elsewhere, with each plan's status. | `prose` |
| An open question keeps its number for good; an answered one keeps its row and gains its answer. | `prose` |
