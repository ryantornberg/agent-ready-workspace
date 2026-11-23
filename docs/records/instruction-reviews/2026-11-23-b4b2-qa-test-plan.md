---
kind: record
last-reviewed: 2026-11-23
covers: docs/templates/qa-test-plan.md
reviewed-at: 4190d8d, with the uncommitted change of the B4 slice session
---

# Instruction review: docs/templates/qa-test-plan.md

This records the instruction review of slice B4's second-batch edit to the QA test plan template, for its author and for critics.

**In short:** 1 finding: 1 contradiction, not blocking. The new line makes the rules for a product reader's page bind every copy, and those rules say the reader standard applies too, where the reader standard binds no template whose opening does not say so.

## Scope

In scope: the uncommitted edit, one sentence at the top of "Filling it in": a copy is a page for a product reader, so that page's rules apply. Also in scope: how the sentence fits the rest of the page, its skeleton, worked example and Rules.

Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/extend-the-workspace.md`, pages for a product reader in full, and the QA verification list's rules. Ran `git diff -- docs/templates/qa-test-plan.md` and `python3 ws.py check`, which reports nothing on this page.

The page has no `## References` heading.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Filling it in, the first paragraph | Not blocking. The sentence binds each copy to pages for a product reader. That page's **In short** line says its rules add to the reader standard, "which still apply", and its first Rules row says such a page "follows the style guide and the reader standard as well as this page". The reader standard's "Who it binds" says its four shape rules bind exactly three templates, and another template "only when its own opening says so and links this page". This template's opening does neither. So a writer cannot tell whether a copy must meet the shape rules, such as naming its top layer's word budget. The copy is written either way, so nothing goes wrong on a write. Verified: the three texts. Inferred: that a writer reads "still apply" as binding the shape rules. The cleaner fix may sit on pages for a product reader, which is outside this review. | fixed: the sentence now adds that the reader standard's shape rules do not bind a copy, since this template's opening does not say so. The names and references rules, which bind every new page, are untouched. Pages for a product reader was left as it is. |

## Checked with no finding

- contradiction: the sentence agrees with pages for a product reader, whose "Which pages these rules bind" names "a copy of the QA test plan" as an example, and binds a page whose template says so. The template's skeleton and worked example meet those rules. The sign-off and the scenario checkboxes are the tester's checklist that rule 4 allows. The Result line names its three choices, as rule 2 asks. The Do not file table gives each ticket key beside a plain description. The rules also agree with the QA verification list's rule 7, plain language. Verified: both pages read against the worked example.
- step: the change adds no step. The link resolves; the `links` check reported nothing on this page.
- trigger: the sentence fires on every copy, which is what pages for a product reader's binding section asks of a template that says so.
- enforcement: the sentence imports rules whose page states their enforcement, each `prose`; it adds no must of its own that needs a row here.
- placement: the sentence links the rules and restates none of them, so each stays on the page that owns it, as the style guide's "One rule, one page" asks.
- eval-case: a lane template carries no proof keys, and this one carries none. No eval case or arm in `evals/arms.json` reads it; its first use is named as M6.

## Re-check

A fresh session read the fix round's `git diff -- docs/templates/qa-test-plan.md`, the whole template as it now stands, the reader standard's "Who it binds" and Rules, and pages for a product reader in full. It ran `python3 ws.py check`, which exited 0 with only the known `eval_record` warning on `fix-a-bug.md`.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | Verified: "Filling it in", the first paragraph, now adds that the reader standard's shape rules do not bind a copy, since this template does not say so in its opening. That is true to "Who it binds": another template comes under the shape rules only when its own opening says so and links that page, and this template's opening, through its **In short** line, does neither. The new link sits in "Filling it in", not the opening, and says the opposite, so it does not bring the template under them. A writer of a copy can now tell. Left as it was, as the disposition says: pages for a product reader's first Rules row still says such a page follows "the reader standard" with no qualifier. Inferred: that reads consistently, since following the reader standard includes its own binding section, but another product-reader page, such as the triage sheet, still carries the first reading's ambiguity. |

What a fix broke:

- None.
