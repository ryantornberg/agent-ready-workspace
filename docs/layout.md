---
kind: reference
last-reviewed: 2026-11-18
---

# Layout: folders and page kinds

Where each kind of page lives, the front matter it carries, and the order it opens in. For anyone adding or moving a page.

**In short:** every page under `docs/` names its kind in its front matter. Nine kinds, each with its own folder or place. Every page opens with its title, a purpose sentence of 25 words or fewer, then its **In short** line. The `page_kinds` check enforces all of it, at the commit and in CI.

## Folders

| Folder | Holds |
|---|---|
| `src/` | The code. In a real workspace, each folder is a pinned code repository; this sample checks in a few invented files instead. See [src](../src/README.md). |
| `docs/` | Pages for top-level how-tos and references, such as this one. |
| `docs/playbooks/` | Playbooks. |
| `docs/tutorials/` | Tutorials. |
| `docs/templates/` | Templates. |
| `docs/rules/` | Rule pages: reference pages with an `applies-to` key, shown when a matching file is edited. |
| `docs/records/` | Records, such as the instruction reviews in `docs/records/instruction-reviews/`. |
| `docs/decisions/` | Decision records. |
| `docs/plans/` | Hand-off plans. |
| `docs/milestones/` | Milestone records. |
| `archive/` | Retired pages. An ignore file hides it from search, and the link and page checks skip it. |
| `evals/` | The eval harness, its cases and its recorded runs. See [evals](../evals/README.md). |
| `parts/`, `wslib/`, `tools/`, `tests/` | The machinery. See [changing the machinery](changing-the-machinery.md). |

## Page kinds

| Kind | What it is | Required front matter | Opens with |
|---|---|---|---|
| `playbook` | Steps an agent follows from request to report. | `kind`, `last-reviewed`, `proof` | Title, purpose. **In short** optional. |
| `how-to` | Steps for one task, for a person or an agent. | `kind`, `last-reviewed`, `proof` | Title, purpose, **In short**. |
| `tutorial` | A walk-through a newcomer runs once. | `kind`, `last-reviewed` | Title, purpose, **In short**. |
| `reference` | Facts to look up, not steps. | `kind`, `last-reviewed` | Title, purpose, **In short**. |
| `template` | A shape to copy. | `kind`, `last-reviewed` | Title, purpose, **In short**. |
| `record` | A log or a record of something that happened. | `kind`, `last-reviewed` | Title, purpose. **In short** optional. |
| `decision` | A decision record. | `kind`, `last-reviewed`, `status` | Title, then **In short**; a purpose sentence is optional. |
| `plan` | A hand-off plan. | `kind`, `last-reviewed`, `status`; `milestone` optional | Title, purpose, **In short**, then `## Key points`. |
| `milestone` | A milestone record. | `kind`, `last-reviewed`, `status` | Title, purpose, **In short**. |

Controlled values:

| Key | Values |
|---|---|
| `kind` | The nine kinds above. |
| `status` | Decision: `proposed`, `accepted`, `superseded`, `rejected`. Plan: `draft`, `approved`, `done`, `abandoned`. Milestone: `open`, `signed off`. |
| `proof` | `proven` or `unproven`, on every playbook and how-to. See [decision 0006](decisions/0006-what-proven-means.md). |
| `prove-by` | `M<n>`, on an unproven page: the milestone that is to prove it. |
| `proven-by` | On a proven page: bare repository paths, or `<40-hex sha>:<path>`, separated by a comma and a space. No link text. |
| `milestone` | `M<n>`, on a plan. |
| `lane` | Optional: `development`, `qa`, `product`, `automation` or `devops`. |
| `last-reviewed` | `YYYY-MM-DD`. A page edited after 180 days must be reviewed and its date moved. |

A page in a kind's own folder must be of that kind. A README in one of those folders is a reference page.

## The opening

1. The title: the first line after the front matter, `# <title>`.
2. The purpose: one sentence of 25 words or fewer, saying what the page is for and who reads it. More sentences may follow in the same paragraph.
3. The **In short** line: the verdict or the gist, before any background.
4. On a plan, `## Key points` as the first section.

The 25-word limit does not apply to an approved plan, an accepted decision record or a signed-off milestone record. Those are frozen; they change only by a dated "Amended" paragraph.

## Where the existing pages sit

| Page | Kind | Proof |
|---|---|---|
| [Fix a bug](playbooks/fix-a-bug.md) | playbook | proven |
| [Size the work](size-the-work.md) | how-to | unproven, prove-by M9 |
| [Orchestration](orchestration.md) | how-to | unproven, prove-by M4 |
| [Parts](parts.md) | how-to | unproven, prove-by M4 |
| [Changing the machinery](changing-the-machinery.md) | how-to | unproven, prove-by M4 |
| [Browsers](browsers.md) | how-to | unproven, prove-by M6 |
| [Definition of done](definition-of-done.md), [Glossary](glossary.md), this page, [rule pages](rules/) | reference | |
| [Question log](question-log.md) | record | |
| [Templates](templates/) | template | |

## Rules

| Rule | Enforced by |
|---|---|
| Every page under `docs/` names its kind, from the nine, and carries the front matter its kind needs. | `page_kinds#a page with no kind fails`, `page_kinds#a playbook without proof fails` |
| A page opens with its title, a purpose sentence, then its **In short** line. | `page_kinds#an In short line before the purpose is out of order`, `page_kinds#a missing In short fails where the kind needs one` |
| A purpose sentence has 25 words or fewer, except on a frozen page. | `page_kinds#a purpose sentence over 25 words fails`, `page_kinds#an approved plan is exempt from the word limit` |
| A proof key or section proof line is written in its exact form only. | `page_kinds#a variant proof key fails, so it cannot hide from the hash` |
| Every path in the index's cross-cutting chains exists. | `chains#a chain path that does not exist fails` |
| Each agent tool's pointer file names the contract and the rule pages. | `pointers#a pointer file that stops naming the rule pages fails` |
| The contract and the pointer files stay under 6,000 bytes, and the wrappers' descriptions under 9,000. | `loaded_size#over the ceiling fails` |
| Every rule in a rules table carries a tag that is true. | `rules#a part not in the manifest fails` |

## Archiving a page

Move it under `archive/`, keeping its path below the folder. At the old path, leave a tombstone: a short reference page that names where the page went and why. Then fix every link to it.
