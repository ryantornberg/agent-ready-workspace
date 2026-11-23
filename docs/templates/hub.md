---
kind: template
last-reviewed: 2026-11-22
---

# Project hub template

The front page of one project's docs, for the author writing it and the agent keeping it true. It sits between the index and the project's unit pages, and follows the [reader standard](../reader-standard.md).

**In short:** one hub per project. Five headings, in a fixed order: the units, where the project fits, a reading order, which page to open when, and shared topics. The units table is the project's coverage record: every unit has its own page or a pointer row with a reason.

## When to use it

Write a hub when a project has more than one documentable unit, or when one of its units is easy to mistake for another. A unit is one part of the code a reader works on as a whole: a service, library, client or infrastructure folder. Each unit with a page follows the [unit doc template](unit-doc.md).

A copy is read by a newcomer to the project, a reviewer, or an agent about to change its code.

A project is one or more pinned code repositories under `src/` that ship together, as [src](../../src/README.md) describes them. In this sample, the order system is one project: `orders-api`, `orders-web` and the shelved `orders-service-v1`.

This is not the [epic folder](epic-folder.md)'s hub, which is the front page of one piece of work, not of a project's code.

## Where copies live

Whether per-repository reference docs live in the code repository or in the workspace is the [open question on adopting the workspace](../adopt-the-workspace.md#open-question-where-per-repository-reference-docs-live). Do not settle it from this page. Until an instance records a decision, that section says to write new pages in the workspace.

So the default is `docs/projects/<project>/README.md`, with the unit pages beside it in the same folder. `<project>` is the project's name in one to three lowercase words, joined by hyphens, such as `orders`. Wherever a hub lives, its unit pages sit beside it, so its links stay short. Readers reach the hub from a row in [INDEX.md](../../INDEX.md). An index change needs a new eval run, as the contract's rules table says, so batch it with other index edits.

## Skeleton

```markdown
---
kind: reference
last-reviewed: YYYY-MM-DD
---

# <Project>: project hub

<One sentence, 25 words or fewer: what the project does, and who reads this hub.> Checked against <repository> at <pinned commit>, <repository> at <pinned commit>.

**In short:** <the project in two sentences: what it is made of, and the one trap a newcomer falls into>.

## Units

| Unit | What it is | Where it lives | Page |
|---|---|---|---|
| <unit> | <kind, and what it does in one line> | `src/<repository>/<folder>` | [<unit>](<unit>.md) |
| <unit> | <kind, and what it does in one line> | `src/<repository>/<folder>` | No page: <reason> |

## Where it fits

<A small diagram: who calls this project, what it calls, and where its data sits.>

- <A trap: something that looks true here and is not.>

## Reading order

| # | Page | What you get |
|---|---|---|
| 1 | [<page>](<page>.md) | <what the reader knows after it> |

About <n> minutes in all.

## When to open which page

| Page | Open it when |
|---|---|
| [<page>](<page>.md) | <the reader's situation, such as "a payment shows as unmatched the next morning"> |

<!-- Optional. Keep only when readers arrive with distinct tasks; otherwise delete the block. -->
## Start here by task

- <task, in the reader's words>: <page>, then <page>.
<!-- End of the optional block. -->

## Shared topics

<One paragraph linking the workspace-wide pages this project's readers need, such as fixing a bug or sizing the work.>
```

## Filling it in

1. **The opening.** This is the copy's top layer: the title, the purpose line, the checked-against sentence and the **In short** line, at most 120 words in all. The purpose line names the project and the reader in 25 words or fewer. The next sentence names each repository and the commit the hub was checked against. In an instance with pins, `git submodule status` prints each pinned commit. The **In short** line holds two sentences.
2. **Units.** One row per unit, in three states only: it has a page, it has a pointer row with a reason, or it is missing. A missing unit is a gap to fix before the commit, with a page or a pointer row. The reason on a pointer row says why the unit gets no page, such as "shelved, read-only for audits" or "another team's unit". [The unit doc template](unit-doc.md#units-that-get-no-page) lists the units that get a pointer row.
3. **Where it fits.** Keep the diagram to the boxes a reader needs: callers, this project, what it calls, the data. Under it, list the traps: names that mislead, a copy that looks live and is not. Leave out anything a search of the code would show.
4. **Reading order.** At most five rows. Each row says what the reader gets from the page, not what the page covers. Give one time estimate for the whole list.
5. **When to open which page.** Write the right-hand column as the reader's situation, not the page's subject. "A hold will not lift" sends a reader to the right page; "account freezes" does not.
6. **Start here by task.** Optional. Keep it inside its comment markers, so a reader can tell it apart from the five required headings.
7. **Shared topics.** Link the pages rather than copying from them. A rule with a home elsewhere stays there.

The headings' wording stays as the skeleton gives it, so every hub reads the same. Add headings freely; never drop or rename one of the five. The order is the one readers expect; keep it. A required heading with nothing under it yet keeps the heading and the word "none". The optional "Start here by task" block is the one part you delete when it does not apply.

## Worked example

A hub for this sample's order system. The order system is invented, as the contract says. The unit pages, the commits, the diagram's database and payment provider, and the timings are invented too: this sample has no pins and no unit pages yet. The code names are real files under `src/`.

```markdown
---
kind: reference
last-reviewed: 2026-11-22
---

# Orders: project hub

The order system's front page, for an engineer or agent about to change how orders are taken, matched or exported. Checked against orders-api at 3f9c2a1, orders-web at 8b41d07, orders-service-v1 at 52e0c9a.

**In short:** two live units, the order service and its front end, plus a shelved copy of the old service. The trap: `orders-service-v1` has the same names as `orders-api` and is not the code that runs.

## Units

| Unit | What it is | Where it lives | Page |
|---|---|---|---|
| orders-api | Service: the live order service, with the nightly payment match (`ReconciliationWorker`) and holds (`AccountFreeze`) | `src/orders-api` | [orders-api](orders-api.md) |
| orders-web | Client: the front end of `orders-api`, with the quarterly export | `src/orders-web` | [orders-web](orders-web.md) |
| orders-service-v1 | Service, shelved: the one `orders-api` replaced | `src/orders-service-v1` | No page: shelved, read-only for audits. A hook refuses edits to it. |

## Where it fits

    browser --> orders-web --> orders-api --> orders database
                                  |
                                  +--> payment provider (nightly match)

- `orders-service-v1` has the same names as `orders-api` and is not the code that runs.
- "The nightly job" is `ReconciliationWorker`; "a hold" is `AccountFreeze`.

## Reading order

| # | Page | What you get |
|---|---|---|
| 1 | [orders-api](orders-api.md) | How an order moves from placed to paid, and where a hold stops it |
| 2 | [orders-web](orders-web.md) | Which screens call which endpoints, and how the export is built |

About 20 minutes in all.

## When to open which page

| Page | Open it when |
|---|---|
| [orders-api](orders-api.md) | A payment shows as unmatched the next morning, or a hold will not lift |
| [orders-web](orders-web.md) | The quarterly export is late or missing rows |

## Shared topics

To change any unit, start from [fix a bug](../../playbooks/fix-a-bug.md), or [size the work](../../size-the-work.md) when the change is larger.
```

## Rules

| Rule | Enforced by |
|---|---|
| A hub carries the five required headings, worded as the skeleton gives them; an empty one keeps "none". No check reads headings. The author holds this, and a copy under `docs/` gets an [instruction review](../playbooks/instruction-review.md) like any guidance page. | `prose` |
| A hub's top layer, through its **In short** line, holds at most 120 words. | `prose` |
| Every unit of the project has a page or a pointer row with a reason in the units table. The doc-coverage check that the M3 plan lists for M5 is to hold this. | `prose` |
| The reading order has at most five rows and one time estimate. | `prose` |
