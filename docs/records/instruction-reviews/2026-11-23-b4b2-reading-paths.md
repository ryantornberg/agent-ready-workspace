---
kind: record
last-reviewed: 2026-11-23
covers: docs/reading-paths.md
reviewed-at: 4190d8d, with the uncommitted change of the B4 slice session
---

# Instruction review: docs/reading-paths.md

This records the instruction review of slice B4's second-batch edit to reading paths by role, for its author and for critics.

**In short:** no findings. Each new line in the product and DevOps paths is true to the page it links, and every batch-2 lane page has a line in its role's path.

## Scope

In scope: the uncommitted edit, which extends the product path's item 6 with the epic satellites template, adds product items 7 to 13, and adds DevOps items 6 to 8. Also in scope: how the edit fits the rest of the page, its **In short** line, "Lanes" and its Rules.

Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/extend-the-workspace.md`, and each page the new lines link, in full: bug grooming, bug triage labels, bug triage meeting, checking a shelved predecessor, standup report, standup log template, effort estimate, epic satellites template, pages for a product reader, import a repository, environment self-check and ship a new deployable. Also the playbook catalog, the how-to index and the templates index as they stand. Ran `git diff -- docs/reading-paths.md` and `python3 ws.py check`, which reports nothing on this page.

The page has no `## References` heading.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|

No findings.

## Checked with no finding

- contradiction: each new line's gloss matches its page's purpose line. Each line marked "A product lane draft, for M9" or "A DevOps lane draft, for M11" names a playbook or how-to whose `prove-by` is that milestone. The lines for triage labels, pages for a product reader, the standup log and epic satellites carry no such mark, as the existing QA path leaves its templates unmarked; those pages carry no proof keys. Item 6 calls the satellites "beside its hub", which is that template's own purpose line; the path gives no place to write, so it does not mislead on where a copy goes. The **In short** line's two planned topics, the request door for M9 and release and rollback for M11, are still the only planned lines. Verified: front matter and purpose lines read.
- step: the change adds no step. Every new link resolves; the `links` check reported nothing on this page.
- trigger: each of the twelve batch-2 lane pages has a line in its lane's path, as this page's Rules row asks, and each also has its row in the playbook catalog, the how-to index or the templates index. Verified: read the three index sections against the twelve pages' `kind` and `lane` keys. The product path's order follows the work: labels before the meeting that sorts by them, grooming and the predecessor check after.
- enforcement: the change adds no must or never. The Rules rows still hold: links resolve, and each new page's `lane` value is one of the five, `product` or `devops`. Verified: front matter and `python3 ws.py check`.
- placement: the lines route only; none restates a page's steps or rules.
- eval-case: a reference page carries no proof key, and no eval case or arm in `evals/arms.json` reads this page. Every playbook or how-to the new lines name is marked unproven with a `prove-by`.
