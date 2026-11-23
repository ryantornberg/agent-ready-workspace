---
kind: record
last-reviewed: 2026-11-22
covers: docs/reader-standard.md
reviewed-at: f757aed, with the uncommitted change of the B3 builder
---

# Instruction review: docs/reader-standard.md

This records the instruction review of the new reader standard, for its author and for anyone writing a page or template.

**In short:** 5 findings, 1 blocking: 1 contradiction, 1 step, 1 trigger, 1 placement, 1 eval-case. The blocking one: the page calls a coined term's `INDEX.md` row a "search alias", but the index's "Search aliases" table holds only code names, and its check fails such a row.

## Scope

In scope: the whole page, which is new. Read in full: the page, `AGENTS.md`, `INDEX.md`, `docs/playbooks/instruction-review.md`, `docs/procedure-endings.md`, `docs/layout.md` and its diff, `docs/authoring.md`, `docs/glossary.md`, `docs/how-tos.md`, `docs/extend-the-workspace.md`, `docs/maintain-the-workspace.md` ("What the checks catch for you", "When a duty falls due"), `docs/templates/bug-ticket.md`, `parts/aliases.py`'s docstring, and slice B3's row and the 2026-11-22 entries naming B3 in the M3 plan. Ran `python3 ws.py check` (exit 0, one unrelated `eval_record` warning on `fix-a-bug`). In a scratch copy of the worktree's files under a fresh `git init`, added the row `| adversarial review | [Red team review](docs/playbooks/adversarial-review.md) |` to `INDEX.md`'s "Search aliases" table and ran `python3 ws.py check`. Counted the top layer of every page under `docs/`, `docs/playbooks/` and `docs/templates/` with a script: none over 120 words, this page 81.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Names, the second bullet | Blocking. "A term coined here stays only as a search alias: a row in `INDEX.md` that maps the coined word to the page." In this workspace a search alias is a row of `INDEX.md`'s "Search aliases" table, which maps an everyday word to a name in the code, as the glossary's **In short** line and the research ladder say. The `aliases` check reads that table and fails a row whose second column is not one backticked code name. An agent that makes the row as this page defines it, such as the batch that makes slice Z's queued rows, gets a failing `ws.py check` and a refused commit. The plan's queued rows for coined terms go in Topics instead. Verified: in the scratch copy, `ws.py check` failed on the new row with "cannot read this alias row: it needs two columns, the second one name in backticks [aliases]". Marked blocking because the step runs a command that fails, and in doubt whether the batching default keeps this page's reader from making the row. | fixed: a coined term now stays only as a search word in its page's Topics row, never in "Search aliases", with an `aliases` rule row; the Topics rows are queued for slice Z |
| 2 | step | Who it binds; The shape | Not blocking. An agent writing a page cannot tell whether the four shape rules bind it. "Each page kind written mainly for a person" has no test. "Kind" is defined in the glossary and the layout as one of nine front-matter kinds, yet the examples given, a bug ticket, a pull request description and a project hub, are copies made from templates, not kinds. A new reference page or how-to is read by a person and an agent alike. Rules 3 and 4 then say "The template gives them" and "The template shows one filled-in copy", so a page with no template has no heading set or example to follow. Verified: the glossary's "Kind" row, the layout's page kinds table, and the page's text. | fixed: "Who it binds" now names the three templates it binds, the bug report, pull request and project hub, and their copies; rules 1 and 2 speak of the template |
| 3 | placement | References, the third bullet | Not blocking. "The instruction review opens each source and checks that it says what the page credits it for" sets a duty for the reviewer on a page the reviewer is not sent to. The instruction review's steps and six checks say nothing of sources or a "References" heading, so a reviewer following that page skips this. Verified: a search of `docs/playbooks/instruction-review.md` for "source" and "References" finds nothing. | fixed: the duty moved to step 3 of the instruction review; this page links it |
| 4 | trigger | The purpose sentence; the how-to index | Not blocking. Nothing routes a page or template writer here except the style guide's **In short** line and the bug report template. The page has no row in the [how-to index](../../how-tos.md), whose first rule asks for one in the same commit as the page. Neither [layout](../../layout.md), whose "The opening" this page adds a word budget to, nor step 4 of extend the workspace links it. The `INDEX.md` row is not counted, since the eval hashes that file. Verified: a search of `AGENTS.md`, `INDEX.md`, `README.md`, `docs/` and `evals/README.md` for `reader-standard` finds only `docs/authoring.md` and `docs/templates/bug-ticket.md`. | fixed: rows for this page and the style guide added to the how-to index, and layout's purpose paragraph links it; the `INDEX.md` Topics row is queued for slice Z |
| 5 | eval-case | The shape; References | Not blocking. The page asks new behavior of an agent that no eval case covers: a top layer within 120 words, fixed headings, one worked example, and only sources the builder opened and read. As `kind: reference` it cannot carry `proof` or `prove-by`, which the layout puts on playbooks and how-tos only. Verified: the layout's controlled values and `evals/arms.json`, which gives this page to no arm. | declined: a template or reference page carries no proof key; the procedures that use it carry the proof state, as the plan sets the page kind |

## Checked with no finding

- enforcement: every must and never on the page has a row in its rules table, each tagged `prose`, and no tag claims a check that does not exist; `python3 ws.py check` passed the `rules` check (verified). The unscoped second row, a 120-word top layer for "a page", breaks no page today: no top layer under `docs/`, `docs/playbooks/` or `docs/templates/` is over 120 words (verified, by the script).

## Re-check

A fresh session re-read the page on 2026-11-22, after the fix round.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | "Names" now keeps a coined term only as a search word in its page's Topics row, never in "Search aliases". Its rules row cites `aliases#a row it cannot read is an error, not a pass`, a case in `parts/aliases.cases.json`. The queued Topics rows are not yet in the plan's "Queued for slice Z" list. Verified. |
| 2 | fixed | "Who it binds" names the three templates and their copies. Verified, by reading. |
| 3 | fixed | Step 3 of the instruction review now holds the duty, and this page links its "Steps" and names step 3. Verified. |
| 4 | fixed | The how-to index has rows for this page and the style guide, and layout's purpose paragraph links this page. Verified. |
| 5 | decline upheld | Layout's controlled values put `proof` on playbooks and how-tos only, and the finding meets none of the four blocking conditions. Verified. |

Broke: none.

Missed:

- Not blocking. The rules table's first row binds the three templates "and each copy" to "give one worked example". "The shape" rule 4 asks that of the template only: "The template shows one filled-in copy". A writer reading the rules table adds an example to a bug report or pull request. The how-to index's new row repeats it. Verified, by reading.
