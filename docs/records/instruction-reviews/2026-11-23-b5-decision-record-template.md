---
kind: record
last-reviewed: 2026-11-23
covers: docs/templates/decision-record.md
reviewed-at: dace91e, with the uncommitted change of the B5 slice session
---

# Instruction review: docs/templates/decision-record.md

This records the review of B5's new decision record template, for its author.

**In short:** 4 findings: 1 contradiction, 1 step, 1 trigger, 1 enforcement, none blocking. The template puts the **In short** line right under the title where layout allows a purpose sentence; it gives no numbering rule for an instance whose kit later ships a record with the same number; the index has no route to it; and the check does not hold "sections anywhere after Context", though the page says it holds the rules above.

## Scope

In scope: the whole page, which is new and untracked. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, the playbook's section "When a decision gets a record" in `docs/playbooks/decision-interview.md`, the openings and front matter of every record in `docs/decisions/`, decision 0007's classes and its "Upgrade" paragraph, `kit/kit.json`, `parts/decisions.py`, `parts/decisions.cases.json` and the `decisions` entry in `workspace.json`.

Run: `python3 ws.py selftest` reports `decisions: 25 of 25 cases` (verified). `python3 ws.py check` passes on the worktree with only an `eval_record` warning about `fix-a-bug.md` (verified). `python3 ws.py rules` lists each tag in the page's rules table with no complaint (verified). `parts/decisions.py`'s `run` was called on three hand-made records, as the findings below say.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | "The opening", item 2 | Not blocking. The template says the **In short** line goes "right under the title". Layout's page-kinds row for `decision` says "Title, then **In short**; a purpose sentence is optional", and "The opening" says a decision record "may open with its **In short** line instead" of a purpose sentence (verified, reading `docs/layout.md`). So layout lets a record carry a purpose sentence between title and **In short**, and this page forbids it. Neither `page_kinds` nor `decisions` refuses one: a record with a purpose sentence there passes `decisions` (verified, calling `run`). All twenty records today open with **In short** right under the title (verified), so nothing is broken yet. Say which page holds: either drop "a purpose sentence is optional" from layout's row, or say here that an optional purpose sentence may sit between the two. | fixed: a purpose sentence between the title and the In short line is optional, as layout says |
| 2 | step | "The file" | Not blocking. "The next free four-digit number" has no rule for an instance. `docs/` is synced by the kit, so the kit's records ship into every instance (verified, `kit/kit.json`). An upgrade refuses a new synced file only when its path is taken (verified, decision 0007, "Upgrade"); a kit record `0021-a.md` and an instance's own `0021-b.md` have different paths. The `decisions` check then fails both, "two records with one number" (verified, its case). The instance cannot renumber the synced one without drift, and renumbering its own breaks its links (inferred). Give a default, such as a number range or prefix an instance uses for its own records, or say the kit's numbers are reserved. | deferred to M5: the first instance settles how an instance numbers its own records beside the kit's |
| 3 | trigger | `INDEX.md`, "Topics" | Not blocking. The contract sends an agent with a topic and no name to `INDEX.md`. No Topics row covers writing, amending or superseding a decision record, or a commit refused by `decisions` (verified, reading `INDEX.md`; its decision rows cover 0001 to 0006 by subject only). Routes do exist: the templates index row, decision interview's section, extend the workspace's step 4, and every `decisions` finding names this page (verified, `PAGE` in `parts/decisions.py`). An agent told only "record this decision" is not routed. Add a Topics row; `INDEX.md` is covered by the eval, so batch it with the next eval run. | queued for slice Z: an `INDEX.md` Topics row for writing, amending or superseding a record |
| 4 | enforcement | "The sections", the paragraph on added sections; "What the check holds" | Not blocking. The page says added sections go "anywhere after Context", and that the check "fails a record whose ... sections ... break the rules above". The check places only the four named sections; a `## Rules` before `## Context` passes (verified, calling `run` on such a record: no finding). The module's docstring makes the same claim. Either say the check holds only the four sections' presence and order, or add the test and a case. | fixed: the page says the check holds the four sections' presence and order, and that where an added section sits is the author's; the check's docstring says the same |

## Checked with no finding

- placement: the page owns the record's shape. It links the three conditions in decision interview instead of restating them, and points to layout for freezing and front matter, as the style guide's "One rule, one page" asks. Its "What the check holds" describes the part that names this page as its `PAGE`.
- eval-case: the page is a template, which carries no proof mark (verified, layout's page-kinds table). The shape it asks for is held by the `decisions` check, whose rules-table tags all name real cases: each of the twelve case names in the table matches a case in `parts/decisions.cases.json` (verified, `python3 ws.py rules` and reading the cases).

## Re-check

A fresh driver-tier session read the whole page as it stands, beside `docs/layout.md` (the `decision` row, "The opening"), decision interview's "When a decision gets a record", `parts/decisions.py` with `git diff HEAD`, its cases, and M3's plan (non-goals, "Queued for slice Z"), and ran `python3 ws.py check` (exit 0, only the `eval_record` warning) and `python3 ws.py selftest` (`decisions: 25 of 25 cases`).

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | "The opening" item 2 now says a purpose sentence between the title and the **In short** line is optional, as layout's `decision` row says (verified). |
| 2 | upheld | M3's plan says the first real instance is M5, and the kit is proven only on a scratch instance before then (verified, non-goals), so the deferral fits. |
| 3 | upheld | A missing `INDEX.md` row goes to slice Z under M3's change of 2026-11-21 (verified). It is not yet in "Queued for slice Z"; B5's report must add it there (verified). |
| 4 | upheld | "What the check holds" says the check holds the four sections' presence and order, and that where an added section sits is the author's; the docstring of `parts/decisions.py` now says "it does not place any other section" (verified, `git diff HEAD`). |

What a fix broke:

- Not blocking. "The sections" says a record adds other sections "after Context", and "What the check holds" now says "Where an added section sits is the author's". A reader may take the second as leave to put one before Context (inferred). Saying "the check does not hold that rule" would keep both.

What the first reading missed:

- Not blocking. "When to write one" lets a record an approved plan asks for start at `status: accepted`. Decision interview's "When a decision gets a record" says a record "starts at `status: proposed` until the person accepts it", with no exception (verified, reading both). No check fails either status, so nothing is refused (inferred).

## Known defects

From the re-check, left for later since the plan allows one fix round:

- "Where an added section sits is the author's" can be read as leave to put one before Context, which "The sections" does not allow. For the docs audit.
- Decision interview's "When a decision gets a record" says a record starts at `status: proposed`, with no exception for a record an approved plan asks for. For the docs audit.
