---
kind: reference
last-reviewed: 2026-11-21
---

# Layout: folders and page kinds

Where each kind of page lives, the front matter it carries, and the order it opens in. For anyone adding, moving or amending a page. How to write a page's words is on the [style guide](authoring.md). The shape of a template a person reads, its top layer's budget included, is on the [reader standard](reader-standard.md).

**In short:** every page under `docs/` names its kind in its front matter. Nine kinds, each with its own folder or place. Every page opens with its title, a purpose sentence of 25 words or fewer, then its **In short** line. Its kind's row may say otherwise. The `page_kinds` check enforces the kinds, their front matter and the opening, at the commit and in CI.

## Folders

| Folder | Holds |
|---|---|
| `src/` | The code. In a real workspace, each folder is a pinned code repository; this sample checks in a few invented files instead. See [src](../src/README.md). |
| `docs/` | Pages for top-level how-tos and references, such as this one. |
| `docs/playbooks/` | Playbooks. |
| `docs/tutorials/` | Tutorials. |
| `docs/templates/` | Templates. |
| `docs/projects/` | One folder per project: its [hub](templates/hub.md) as `README.md` and its unit pages beside it, all reference pages. The default until an instance settles where per-repository docs live. |
| `docs/rules/` | Rule pages: reference pages with an `applies-to` key, shown when a matching file is edited. |
| `docs/records/` | Records, such as the instruction reviews in `docs/records/instruction-reviews/`. |
| `docs/decisions/` | Decision records. |
| `docs/plans/` | Hand-off plans. |
| `docs/milestones/` | Milestone records. |
| `archive/` | Retired pages. An ignore file hides it from search, and the link and page checks skip it. |
| `evals/` | The eval harness, its cases and its recorded runs. See [evals](../evals/README.md). |
| `parts/`, `wslib/`, `tools/`, `tests/` | The machinery. See [changing the machinery](changing-the-machinery.md). |
| `kit/` | The kit's classes, and the seed files a new instance gets in place of this workspace's own; also machinery. In an instance, `kit.lock.json` takes its place. See [decision 0007](decisions/0007-the-kit.md). |

One record sits outside `docs/records/`: the [question log](question-log.md), at the top of `docs/`, where the contract links it.

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
2. The purpose: one sentence of 25 words or fewer, saying what the page is for and who reads it. More sentences may follow in the same paragraph. A decision record may open with its **In short** line instead.
3. The **In short** line: the verdict or the gist, before any background. A playbook and a record may leave it out.
4. On a plan, `## Key points` as the first section.

The 25-word limit does not apply to an approved or done plan, an accepted or superseded decision record, or a signed-off milestone record. Those are frozen. An approved plan changes only as rule 6 of the [hand-off plan template](templates/hand-off-plan.md) says: by a dated entry under "Changes after approval", and by each slice's report appended under "Results". A decision or milestone record changes only by a dated "Amended" paragraph. An amendment to a decision record may also edit its **In short** line, and does so when it changes what that line sums up, so the line stays true for a reader who reads only it. The front matter of a frozen page is not frozen: its review date, its status and a new key may change. No check holds the frozen pages to this.

## Where the existing pages sit

Whether each playbook and how-to is proven is in its front matter, and in the [README's table](../README.md#proven-and-unproven-pages), which the `proof` check holds to the pages.

| Page | Kind |
|---|---|
| [Fix a bug](playbooks/fix-a-bug.md), [The instruction review](playbooks/instruction-review.md) | playbook |
| [Size the work](size-the-work.md), [Orchestration](orchestration.md), [Parts](parts.md), [Changing the machinery](changing-the-machinery.md), [Browsers](browsers.md) | how-to |
| [Definition of done](definition-of-done.md), [Glossary](glossary.md), [Commits](commits.md), [Agent settings](agent-settings.md), this page, [rule pages](rules/) | reference |
| [Question log](question-log.md) | record |
| [Templates](templates/) | template |

## Rules

| Rule | Enforced by |
|---|---|
| Every page under `docs/` names its kind, from the nine, and carries the front matter its kind needs. | `page_kinds#a page with no kind fails`, `page_kinds#a playbook without proof fails` |
| A page opens with its title, a purpose sentence, then its **In short** line, as its kind's row allows. | `page_kinds#an In short line before the purpose is out of order`, `page_kinds#a missing In short fails where the kind needs one` |
| A purpose sentence has 25 words or fewer, except on a frozen page. | `page_kinds#a purpose sentence over 25 words fails`, `page_kinds#an approved plan is exempt from the word limit` |
| A proof key or section proof line is written in its exact form only. | `page_kinds#a variant proof key fails, so it cannot hide from the hash` |
| Every path in the index's cross-cutting chains exists. | `chains#a chain path that does not exist fails` |
| Each agent tool's pointer file names the contract and the rule pages. | `pointers#a pointer file that stops naming the rule pages fails` |
| The contract and the pointer files stay under 6,000 bytes, and the wrappers' descriptions under 9,000. | `loaded_size#over the ceiling fails` |
| Every rule in a rules table carries a tag that is true. | `rules#a part not in the manifest fails` |
| A tutorial marks at least one block runnable, and its marked blocks pass in a fresh clone. `tests/test_tutorials.py` holds it in CI, and the pre-push hook for a push to main; neither is a part. | `prose` |

## Tutorials

A tutorial marks each command block a reader runs with a line `<!-- runnable -->` right before the block's opening fence. CI runs every tutorial's marked blocks, in order, in a fresh clone on Linux, macOS and Windows; the pre-push hook runs them for each tutorial a push to main changes. A block runs in bash from the top of the clone, and the run stops at the first command that fails. `python3` in a block starts the clone's launcher, so give it a script or `-m` and a module. A block that is not marked is an example and never runs. A tutorial with no marked block fails, so a run cannot pass by running nothing.

## Archiving a page

Move it under `archive/`, keeping its path below the folder. At the old path, leave a tombstone: a short reference page that names where the page went and why. A kind's own folder, such as `docs/playbooks/`, takes no reference page but its README, so a page archived from one leaves no tombstone. Then fix every link to it.
