---
kind: record
last-reviewed: 2026-11-23
covers: docs/size-the-work.md
reviewed-at: dace91e, with the uncommitted change of the B5 slice session
---

# Instruction review: docs/size-the-work.md

This records the instruction review of B5's two edits to size the work, for their author and readers.

**In short:** 5 findings, 1 blocking: 3 contradiction, 1 trigger, 1 enforcement. The "Silent drift" failure mode still tells an agent to update the spec whenever the code moves, which after shipping edits a frozen plan the new paragraph keeps as written.

## Scope

In scope: the diff from `git diff HEAD -- docs/size-the-work.md`. That is the sentence added to step 3 of "The feature ladder", and the paragraph under "When reality diverges" that replaces "not settled yet" with the rule for a shipped spec. The whole page was read to judge contradictions. Read beside it: `AGENTS.md`, `INDEX.md`, decision 0016 and decision 0020 (row 11), `docs/templates/hand-off-plan.md` ("How to use it", rule 6), `docs/templates/spec.md`, `docs/templates/epic-folder.md`, `docs/layout.md` ("Page kinds", "The opening"), `docs/authoring.md`, `docs/procedure-endings.md`, and the B2 and B5 rows of `docs/plans/m3-reading-layer-machinery-and-kit.md` with its non-goal on hashed files.

Runs (verified): `python3 ws.py check` in the worktree prints one `eval_record` warning and no failure. `grep` finds no mention of `size-the-work` under `evals/`, so the page is not one the eval hashes, and editing it in B5 stales no record.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | "Failure modes" table, the "Silent drift" row; "When reality diverges", the new last paragraph | Blocking. The row reads "The code moved and the spec did not. Update the spec first, as above." The new paragraph makes that exact state correct once the work ships: the spec "is not edited to match later code". The row carries no "while the work is built" label (verified, reading). An agent that finds a shipped feature's code moved past its spec follows the row and edits the Goal or Success criteria of a done plan. Layout's "The opening" freezes a done plan except by rule 6's dated entries, and the new paragraph forbids the edit (verified, reading). | fixed: the Silent drift row is scoped to while the work is built, and says to leave the spec as written once the plan is `done` |
| 2 | contradiction | "When reality diverges", the new last paragraph, "a later change gets its own plan" | Not blocking. The sentence has no exception. "The gate", at the top of the same page, sends a later change that is small, easy to reverse, in one repository and under a day to fix a bug, with no plan (verified, reading). Read as written, a small fix to a shipped feature gets a hand-off plan and a person's approval (inferred). | fixed: a later change passes the gate as any change does |
| 3 | contradiction | "When reality diverges", the replaced sentence; the spec template's "The design spec" | Not blocking. The diff removes "a decision record will settle it". `docs/templates/spec.md` still says whether a spec is kept up to date after shipping "is not settled yet", and that "The spec process says a decision record will settle it", linking this section (verified, reading). After this change that link points at text that no longer exists, and an agent writing a spec reads the question as open. | fixed: the spec template's sentence now states the settled rule and links decision 0016 |
| 4 | trigger | "When reality diverges", the new last paragraph, "Once the work ships" | Not blocking. The paragraph switches the rule when the work "ships". The paragraph just above says the plan's `status` carries the spec through its life, `draft`, `approved`, `done` or `abandoned`, and none of those is "shipped" (verified, reading). A plan can be `done` before its release, or ship slice by slice, so the moment the dated-entry rule gives way to "kept as written" cannot be read from the plan (inferred). | fixed: the switch is the plan's `done` status |
| 5 | enforcement | "Rules" table; "When reality diverges", the new last paragraph | Not blocking. "It is not edited to match later code" is a never, and the rules table has no row for it, not even `prose` (verified, reading the table's seven rows). The row "When reality diverges from the spec, the spec is updated first, then the code" now has a scope the paragraph narrows, and the table does not say so. | fixed: a `prose` row says a spec is not edited to match later code once its plan is `done` |

## Checked with no finding

- step: the step 3 sentence adds a reason, not an action; the step's input, default, output and failure branch are unchanged. The new paragraph's link to `decisions/0016-a-spec-lives-in-its-plan.md` resolves (`ws.py check` passes). The added sentence is 24 words, within the style guide's 25 (verified, counted).
- placement: the after-ship rule sits on the page that owns the spec process, and decision 0016 gives its why, as the decision record template's "When to write one" asks (verified). The step 3 reason states a lesson behind the rule, as B5's row asks, and narrates no history of the page itself.
- eval-case: the page is `proof: unproven`, `prove-by: M9`, and both "The feature ladder" and "The spec process" carry `Proof: unproven, prove-by M9.` (verified, reading).

## Re-check

A fresh driver-tier session read the changed passages as they stand, with `git diff HEAD -- docs/size-the-work.md`, beside decision 0016, `docs/templates/spec.md` with its diff, layout's "Page kinds" and "The opening", and the hand-off plan template's "How to use it", and ran `python3 ws.py check` (exit 0, only the `eval_record` warning).

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | The "Silent drift" row now reads "While the work is built, the code moved and the spec did not" and adds "Once the plan is `done`, leave the spec as written" (verified, reading). An agent no longer edits a done plan's spec by following the row. |
| 2 | upheld | The paragraph now says "A later change passes the gate as any change does, and one that climbs the ladder gets its own plan" (verified, reading). |
| 3 | upheld | The spec template's sentence now states the rule for a done plan and links "When reality diverges" and decision 0016; "not settled yet" is gone from both pages (verified, `git diff HEAD -- docs/templates/spec.md`). |
| 4 | upheld | The paragraph opens "Once the plan is `done`", a status the paragraph above lists (verified, reading). |
| 5 | upheld | The rules table has a new row, "Once its plan is `done`, a spec is not edited to match later code", tagged `prose` (verified). The older row, "When reality diverges from the spec, the spec is updated first, then the code", still carries no scope, so the second half of the finding is met by the pair of rows rather than by a label (verified, reading). |

What a fix broke:

- None.

What the first reading missed:

- None.
