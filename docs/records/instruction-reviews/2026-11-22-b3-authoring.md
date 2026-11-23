---
kind: record
last-reviewed: 2026-11-22
covers: docs/authoring.md
reviewed-at: f757aed, with the uncommitted change of the B3 builder
---

# Instruction review: docs/authoring.md

This records the instruction review of the new style guide, for its author and for anyone writing or editing a page.

**In short:** 6 findings, none blocking: 2 contradiction, 1 trigger, 1 enforcement, 1 placement, 1 eval-case. The page says every page follows it but gives no scope, while existing pages break its 25-word rule; it restates two rules that extend the workspace already states, one of them already differently; and nothing routes a page writer to it.

## Scope

In scope: the whole page, which is new. Read in full: the page, `AGENTS.md`, `INDEX.md`, `docs/playbooks/instruction-review.md`, `docs/procedure-endings.md`, `docs/layout.md` and its diff, `docs/reader-standard.md`, `docs/glossary.md`, `docs/how-tos.md`, `docs/extend-the-workspace.md`, `docs/maintain-the-workspace.md`, `docs/parts.md` and its diff, `docs/commits.md`'s headings, `docs/playbooks/git-host-operations.md`'s "The operations", `parts/line_cites.py`'s docstring, and slice B3's row and the 2026-11-22 entries naming B3 in the M3 plan. Ran `python3 ws.py check` (exit 0, one unrelated `eval_record` warning on `fix-a-bug`) and `python3 ws.py rules` (exit 0; 375 rules, tags eval 19, part 93, prose 285). Counted the page's own sentences and top layer with a script: no sentence over 25 words, and 73 words from the purpose through the **In short** line.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | The purpose sentence; Writing | Not blocking. The purpose says these are "the authoring conventions every page in this workspace follows", but existing pages break them, and the page never says whether they are retrofitted. The reader standard, written beside it, says "Pages already here are not retrofitted"; this page says nothing either way. So an agent editing an old page cannot tell whether it must rewrite each long sentence, and the contract's stale-page rule ("review the whole page") makes that question come up. Verified: `docs/layout.md`'s **In short** sentence "Every page opens with its title, … says otherwise." is 26 words (`wc -w`), and a rough sentence split of `README.md` finds about 100 sentences over 25 words. | fixed: a new "Who it binds" section and the purpose sentence say the guide binds pages from 2026-11-22 on, retrofits none, and binds each sentence written on an older page |
| 2 | contradiction | Writing, the last bullet | Not blocking. "A tag is a part's case or `prose`" leaves out the eval tag. The contract's rules table tags its first rule `eval:fix-a-bug`, and `docs/parts.md`'s `rules` row says a tag may name "an eval case". Verified: both texts, and `python3 ws.py rules` counts 19 eval tags. | fixed: the bullet no longer lists the tags; it links step 4 of extend the workspace, which owns the rules table |
| 3 | placement | Writing, the last two bullets | Not blocking. Two rules here are already stated in step 4 of [extend the workspace](../../extend-the-workspace.md#steps), which does not link this page. Extend says "End a playbook, how-to or reference page with `## Rules` … a row for every must and never … A tag names a part and a case only when that case shows the rule; otherwise it is `prose`". It also says "Machinery that does not exist yet is named as planned, with its milestone". This page states both again in its own words, and the copies already differ: extend limits the table to three kinds and a tag to a case that shows the rule, this page does neither. The page's own "One rule, one page" names this drift. Verified: both texts. | fixed: the two bullets are replaced by one link to step 4 of extend the workspace; extend's own omission of the eval tag is queued to its owner |
| 4 | enforcement | Writing; Rules | Not blocking. "Do not narrate how the page or the work came about" is a never with no row in the page's rules table, which its own last rule requires. The first row covers hard wrapping, emojis and planned things only. Verified: the rules table. | fixed: the first rules row now covers narrating how the page came about |
| 5 | trigger | The purpose sentence; the how-to index | Not blocking. Nothing routes a page writer here. The page has no row in the [how-to index](../../how-tos.md), whose first rule asks for one for every reference page a reader goes to for a task, in the same commit as the page. Step 4 of extend the workspace, the procedure for writing a page, does not link it. Only the layout's new purpose sentence and the reader standard link it. The `INDEX.md` row is not counted, since the eval hashes that file. Verified: a search of `AGENTS.md`, `INDEX.md`, `README.md`, `docs/` and `evals/README.md` for `authoring.md` finds only those two pages. | fixed: a style guide row is added to the how-to index; the link from extend's step 4 and the `INDEX.md` Topics row are queued for slice Z |
| 6 | eval-case | Names and scope; Writing | Not blocking. The page asks new behavior of an agent that no eval case covers. One example is settling a page's name and scope before a wrapper or an eval run on record, with its rename cost. As `kind: reference` it cannot carry `proof` or `prove-by`, which the layout puts on playbooks and how-tos only. Verified: the layout's controlled values and `evals/arms.json`, which gives this page to no arm. | declined: a template or reference page carries no proof key; the procedures that use it carry the proof state, as the plan sets the page kind |

## Checked with no finding

- step: every link resolves, since `python3 ws.py check` passed with the `links` check (verified). The claim on `line_cites` matches its docstring: added lines on doc pages, a commit hash exempts one (verified). The full-URL rule matches git-host operations' "Title and description" row (verified). The page has no ordered steps.

## Re-check

A fresh session re-read the page on 2026-11-22, after the fix round.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | "Who it binds" and the purpose sentence bind pages from 2026-11-22 on, retrofit none, and bind each sentence written on an older page. Verified, by reading. |
| 2 | fixed | The bullet no longer lists tags and links step 4 of extend the workspace, which now names `eval:<case>`. Verified, with `git diff -- docs/extend-the-workspace.md`. |
| 3 | fixed | The two bullets are one link. The disposition says extend's missing eval tag is "queued to its owner". It is fixed in extend's step 4 instead, so the disposition's text is out of date. Verified. |
| 4 | fixed | The first rules row covers narrating how the page came about. Verified. |
| 5 | fixed | The how-to index has a style guide row. Extend's step 4 already links this page in the working tree, not queued as the disposition says. The `INDEX.md` row is not yet in the plan's "Queued for slice Z" list. Verified. |
| 6 | decline upheld | Layout's controlled values put `proof` on playbooks and how-tos only, and the finding meets none of the four blocking conditions. Verified. |

Broke: none.

Missed: none.
