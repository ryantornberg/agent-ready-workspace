---
kind: record
last-reviewed: 2026-11-23
covers: docs/templates/spec.md
reviewed-at: dace91e, with the uncommitted change of the B5 slice session
---

# Instruction review: docs/templates/spec.md

This records the review of B5's changed sentence in the spec template's "The design spec", for its author and its readers.

**In short:** 1 finding, none blocking: 1 placement. The new sentence restates the spec process's rule for a done plan, right after the section says it adds no rule, where a link alone would do.

## Scope

In scope: the sentence that replaces "not settled yet" under "The design spec", "Once the plan is `done`, the spec is kept as written and not edited to match later code, as the spec process says and decision 0016 explains", from `git diff HEAD -- docs/templates/spec.md`. The whole page was read to judge contradictions. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md` ("Page kinds", "The opening"), `docs/authoring.md`, `docs/procedure-endings.md`, `docs/size-the-work.md` with its diff ("The spec process", "Rules"), `docs/templates/hand-off-plan.md` ("How to use it"), decision 0016 and decision 0020 (row 11).

Runs (verified): `python3 ws.py check` in the worktree exits 0 with one `eval_record` warning, so the sentence's links resolve.

Outside the six checks: the new sentence is 27 words, over the style guide's 25 (verified, counted).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | placement | "The design spec", the sentence after the table | Not blocking. The section says of the spec process, "This page adds no rule to it". The new sentence then states that process's rule in full, kept as written and not edited to match later code, beside a link to it (verified, reading). Size the work's "When reality diverges" owns the rule and its rules row (verified). The style guide's "One rule, one page" asks every other page to link the rule, not state it, and the instruction review counts a restated rule as a placement finding (verified, reading). A pointer such as "what happens to the spec once its plan is done is in the spec process" would not drift if the rule changes (inferred). | fixed: the sentence is now a short pointer to "When reality diverges", with no rule of its own |

## Checked with no finding

- contradiction: the sentence agrees with size the work's "When reality diverges", its new rules row and decision 0016, which all switch at the plan's `done` status (verified, reading). It does not add a rule, so "This page adds no rule to it" still holds (inferred). Decision 0020's row 11 still says "once the work ships", but this page does not link it.
- step: the sentence asks no action of a writer; the table row "Status" still points at the plan's `status` (verified).
- trigger: the purpose and **In short** lines are unchanged, and the sentence sits in the section a writer of a design spec reads (verified).
- enforcement: the never in the sentence is owned and tagged `prose` on size the work's rules table; this template's own rules table covers its standalone specs and needs no row for a rule it points to (verified, reading both tables).
- eval-case: a template carries no proof key, and the behavior lives in size the work's spec process, marked `Proof: unproven, prove-by M9` (verified).
