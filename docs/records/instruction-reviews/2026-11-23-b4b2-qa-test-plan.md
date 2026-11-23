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
| 1 | contradiction | Filling it in, the first paragraph | Not blocking. The sentence binds each copy to pages for a product reader. That page's **In short** line says its rules add to the reader standard, "which still apply", and its first Rules row says such a page "follows the style guide and the reader standard as well as this page". The reader standard's "Who it binds" says its four shape rules bind exactly three templates, and another template "only when its own opening says so and links this page". This template's opening does neither. So a writer cannot tell whether a copy must meet the shape rules, such as naming its top layer's word budget. The copy is written either way, so nothing goes wrong on a write. Verified: the three texts. Inferred: that a writer reads "still apply" as binding the shape rules. The cleaner fix may sit on pages for a product reader, which is outside this review. | open |

## Checked with no finding

- contradiction: the sentence agrees with pages for a product reader, whose "Which pages these rules bind" names "a copy of the QA test plan" as an example, and binds a page whose template says so. The template's skeleton and worked example meet those rules. The sign-off and the scenario checkboxes are the tester's checklist that rule 4 allows. The Result line names its three choices, as rule 2 asks. The Do not file table gives each ticket key beside a plain description. The rules also agree with the QA verification list's rule 7, plain language. Verified: both pages read against the worked example.
- step: the change adds no step. The link resolves; the `links` check reported nothing on this page.
- trigger: the sentence fires on every copy, which is what pages for a product reader's binding section asks of a template that says so.
- enforcement: the sentence imports rules whose page states their enforcement, each `prose`; it adds no must of its own that needs a row here.
- placement: the sentence links the rules and restates none of them, so each stays on the page that owns it, as the style guide's "One rule, one page" asks.
- eval-case: a lane template carries no proof keys, and this one carries none. No eval case or arm in `evals/arms.json` reads it; its first use is named as M6.
