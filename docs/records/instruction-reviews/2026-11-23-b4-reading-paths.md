---
kind: record
last-reviewed: 2026-11-23
covers: docs/reading-paths.md
reviewed-at: 1a18d68, with the uncommitted change of the B4 slice session
---

# Instruction review: docs/reading-paths.md

This records the instruction review of slice B4's new reference page of reading paths by role, for the change's author.

**In short:** 5 findings: 2 contradiction, 2 placement, 1 trigger; none blocking. The **In short** line miscounts the planned pages and misstates the paths' order, and the lane definition calls development both outside and among the lanes. No route reaches the page from where a newcomer starts. Its rule that a new lane page adds itself here lives only here, and its wrapper rule is stated on three pages.

## Scope

In scope: the whole page, which is new and untracked. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `README.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md` and `docs/extend-the-workspace.md`. Opened every page it links to, and read each one's opening against the page's line for it: the tutorial get oriented, the research ladder, size the work, decision 0006, decision 0001, parts, the playbook catalog, the how-to index, the templates index, fix a bug, debugging, test first, the reuse checklist, impact analysis, the review orchestrator, the definition of done, the decision interview, red team review, tracker operations, orchestration, saved workflows, changing the machinery, machine self-check, agent settings, commits, `evals/README.md`, and the B4 lane pages and templates. Also read the routing rows in `git diff` of `README.md`, `docs/how-tos.md`, `docs/playbooks/README.md` and `docs/templates/README.md`, and the M3 plan's B4 row, red-team finding 18 and finding R2-21. Ran `python3 ws.py check`: every link and anchor on the page resolves, with only the known `eval_record` warning on fix a bug. Ran `python3 ws.py rules`: the page's four rows are listed with their tags.

The page has no `## References` heading.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | The **In short** line; Development; DevOps | Not blocking. The **In short** line says "Two pages a role needs are not written yet". The product path names the request door, and the DevOps path names "release and rollback", which "M11 builds them": three pages, or two if release and rollback is one. The line also says each path runs "the core pages it uses most, then its lane's pages". The development path puts its lane draft, the feature layer walk, fourth of seven, between core pages. Verified by reading the line beside the two paths. The M3 plan's B4 row and finding R2-21 name "release and rollback" without saying whether it is one page or two. | fixed: the In short line now says each path runs in the order its work meets the pages, core and lane pages together, and that two topics are not written yet, one on the product path and one on the DevOps path. |
| 2 | contradiction | Lanes, the first paragraph | Not blocking. "A lane is one kind of work the workspace guides beyond development: QA, product, automation or DevOps, with development as the fifth." Development cannot be both beyond the lanes and one of them. Layout's `lane` key and the playbook catalog's "Lane drafts" paragraph list development as one of the five values, and the feature layer walk carries `lane: development`. Verified: the three texts and the page's front matter. | fixed: a lane is now one of five kinds of work, development among them. |
| 3 | trigger | The purpose line's reader, "a person or agent new to one role here" | Not blocking. No page a newcomer starts from links this one. The README has no link to it. The tutorial get oriented, which this page names as everyone's first read, ends in "Learn the map" with its own reading order: the contract, the index, the playbook catalog, the how-to index, the glossary and the question log. It never sends the reader here. The only routes in are the "Lane drafts" paragraphs of the playbook catalog and the how-to index, and the templates index's "Lane templates". A development or DevOps newcomer has no reason to open those. Verified: `grep -n -i -E "role|reading path|new to"` on the README and the tutorial, and the tutorial's "Learn the map" section. The `INDEX.md` row is left out here: the index is eval-covered, so its row is queued by default. | fixed: the README's "What is here" row for docs/ and the how-to index's "Starting a task" now link this page. The get-oriented tutorial is left as it is, since a tutorial edit reruns its blocks on three systems and the two routes reach the same reader. |
| 4 | placement | Rules, the last row | Not blocking. "A new lane page adds itself to its role's path here, in the same commit as the page" binds the author of every future lane page, but it is stated only on this page. That author follows [extend the workspace](../../extend-the-workspace.md#steps), whose step 5 lists the rows a new page adds and does not name this page. The catalog's and the how-to index's lane paragraphs ask only for a row there, and the templates index's lane paragraph asks for nothing. Verified: `grep -n -i reading` on extend the workspace and maintain the workspace finds nothing; the three index paragraphs in `git diff`. | fixed: the lane paragraphs of the playbook catalog, the how-to index and the templates index, which extend the workspace's step 5 sends an author to, now say a new lane page also adds its line here. |
| 5 | placement | Lanes, the second paragraph; Rules, the third row | Not blocking. "Lane pages get no wrapper until their milestone proves them" is stated here twice, in the playbook catalog's "Lane drafts" paragraph, and in saved workflows' "What exists today" table. Wrappers belong to the catalog, whose "Three ways to follow a playbook" says which procedures B6 wraps. A reading-order page restates the rule as its own, so the copies can drift. Verified: `grep -rn -i wrapper docs` outside records, plans and milestones. | fixed: the rule is stated once, in the playbook catalog's Rules table. This page links it, and its own Rules row is removed. Saved workflows' "What exists today" table states the current state, not the rule. |

## Checked with no finding

- step: the page is a reference page with no steps. Every link and anchor resolves (`python3 ws.py check`), and each line describing a linked page matches that page's opening. Each lane draft's milestone matches its front matter: the feature layer walk M9, the QA verification list M6, regression run and triage M10, saved workflows M10. "Fix a bug ... the only proven playbook" matches the README's proven table. The product path names the request door as planned for M9 and the DevOps path names release and rollback as planned for M11, as B4's row asks, neither as a step to run. "The suite that M10 runs as a scheduled job" has no source in this repository; the program plan's M10 section, outside it, runs the regression suite as one of that milestone's jobs.
- enforcement: the links row's tags are true, since the `links` check covers the page. The lane-vocabulary tag names a case in `parts/page_kinds.cases.json` that fails a value outside the five. The wrapper row and the new-lane-page row are tagged `prose`, which is true today; B6's planned check is not claimed.
- eval-case: a reference page carries no proof key, and the page asks no new behavior of an agent beyond the authoring rule in finding 4.

## Re-check

A fresh session's reading after the fix round, on `1a18d68` with the uncommitted fix of the B4 slice session. It read the page in full, the diffs of the README, the playbook catalog, the how-to index and the templates index, layout's `lane` key, and ran `python3 ws.py check`, which reports nothing on this page.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | Verified: the **In short** line says each path runs "in the order its work meets the pages, core and lane pages together", and that two topics are not written yet, one each on the product and DevOps paths. Both paths name their planned topic and milestone. |
| 2 | upheld | Verified: "A lane is one kind of work the workspace guides: development, QA, product, automation or DevOps", the five values of layout's `lane` key. |
| 3 | upheld | Verified: the README's "What is here" row for `docs/` and the how-to index's "Starting a task" link this page. Inferred: the reason for leaving the tutorial holds, since both routes reach a newcomer. |
| 4 | upheld | Verified: the lane paragraphs of the playbook catalog, the how-to index and the templates index each say a new lane page adds its line here, in the same commit. |
| 5 | upheld | Verified: the rule is a row in the playbook catalog's Rules table; this page links it and has no wrapper row of its own. Saved workflows' table says "Lane drafts get none", a state, not the rule. |

What a fix broke:

- None.

What the first reading missed:

- None.
