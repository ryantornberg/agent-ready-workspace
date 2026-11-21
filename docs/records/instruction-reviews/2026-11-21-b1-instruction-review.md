---
kind: record
last-reviewed: 2026-11-21
covers: docs/playbooks/instruction-review.md
reviewed-at: 166bbc7, with the uncommitted change of slice B1
---

# Instruction review: docs/playbooks/instruction-review.md

This records the instruction review of the new instruction-review playbook, for its author and for reviewers who follow it.

**In short:** 9 findings: 2 contradiction, 4 step, 2 trigger, 1 enforcement. The procedure runs, but its record rules cannot name or date a repeat review, and its guidance list names a missing folder.

## Scope

The whole page was in scope, since it is new. Read beside it: `AGENTS.md`, `INDEX.md`, `README.md`, `workspace.json`, `docs/orchestration.md`, `docs/commits.md`, `docs/layout.md`, `docs/records/instruction-reviews/README.md` and the folder's existing records. Also read the machinery the page describes: `parts/review_trailer.py`, `parts/review_index.py`, their cases files, `wslib/runner.py`, `wslib/snapshot.py`, `.github/workflows/ci.yml`, `.githooks/` and `tests/test_instruction_review.py`. Ran `python3 ws.py check`, `python3 ws.py selftest`, `python3 ws.py rules` and both test modules; all passed.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | When it runs | The page says guidance today includes the wrappers under `plugin/`. No `plugin/` folder exists in the working copy or in any commit, though the manifest's `guidance` list names it too. Verified: listing the folder fails, and `git log --all -- plugin` prints nothing. | fixed: the page says `plugin/` is listed for the wrappers B6 adds. |
| 2 | contradiction | The record | The section says one file per page, then says a record may cover more than one page. The second is an exception the page does not label as one. Verified: read both sentences. | fixed: a record covers one page, and `review_index` now fails one that covers more. |
| 3 | step | The record | The name `YYYY-MM-DD-<page>.md` does not say how a path becomes `<page>`. A second review of a page on the same day also reuses the first record's name. Verified: today's records already use `agents-md`, `index-md` and `decision-0006`, and this review of five of the same pages needed other names. | fixed: the page says how to name a record and what to do when the name is taken. |
| 4 | step | The record | The `reviewed-at:` key holds the commit the reviewer read. Step 1 has the reviewer read the change before it is committed, so that commit does not exist yet. The page gives no form for this, the usual case. Verified: read the Steps and The record sections. | fixed: the page gives the form for a change not yet committed. |
| 5 | step | Steps | Step 3 has the reviewer write the findings table, which has a Disposition column. The page lists only the author's dispositions, so what the reviewer writes in that cell is undefined. Verified: read the Steps and The record sections. | fixed: the reviewer writes `open`; the author replaces it. |
| 6 | step | Counting for a stop rule | The count is the rows that list a class over the pages reviewed. The index lists classes per record, and a record may cover several pages, so a class cannot be traced to one page. Verified: `review_index` reads classes per row. Inferred: a multi-page record makes the count undefined. | fixed: with one page per record, a class traces to one page. |
| 7 | trigger | Purpose line; the Topics table of `INDEX.md` | No index row leads to this page, either for running the review or for a commit refused for a missing trailer. The contract says the index lists every topic, and the index's Add a page chain names `INDEX.md`. Verified: searched `INDEX.md` for the page and the trailer. | queued for slice Z: `INDEX.md` is hashed; add rows for running the review and for a commit refused for a missing trailer. |
| 8 | trigger | When it runs | The guidance list names the Copilot pointer file but not `opencode.json`, which the `pointers` and `loaded_size` entries treat as the other pointer file. A change to what opencode loads needs no review. Verified: read both lists in `workspace.json`. Inferred: the omission is not deliberate, since no reason is given. | fixed: `opencode.json` is now on the guidance list. |
| 9 | enforcement | When it runs, the skip reasons table | The page allows a skip only when its reason applies, but the check accepts any listed reason without reading the change. No rules row tags that condition `prose`. Verified: `judge` in `parts/review_trailer.py` compares only the reason's text, and the case `a listed skip reason passes` changes a page to `x`. | fixed: the page says the check reads the reason only, and a `prose` row states it. |

## Checked with no finding

- placement: the page loads only when needed, and the change adds nothing to the always-loaded layer.
- eval-case: the page is marked `proof: unproven` with `prove-by: M4`, and the README's proof table lists it.
