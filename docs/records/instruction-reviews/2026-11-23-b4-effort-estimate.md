---
kind: record
last-reviewed: 2026-11-23
covers: docs/playbooks/effort-estimate.md
reviewed-at: 1a18d68, with the uncommitted change of the B4 slice session
---

# Instruction review: docs/playbooks/effort-estimate.md

This records the instruction review of slice B4's new effort estimate playbook, a product lane draft, for the change's author.

**In short:** 5 findings: 2 contradiction, 2 step, 1 enforcement; none blocking. Step 1 says the feature layer walk keeps the type with more layers, where the walk takes every type that fits. Step 5 gives a single points value, which the rules forbid. The shelved-folder tag cannot see an estimate. Step 1 reads a ticket with no route through tracker operations and no check that it is a feature, not a bug.

## Scope

In scope: the whole page, which is new and untracked. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/extend-the-workspace.md`, the instruction review playbook, and every page the page links to: decision 0006, the feature layer walk, bug grooming, the size gate in size the work, and tracker operations.

Ran: step 2's `python3 tools/symbols.py NAME src` with `IOrderStore`, which printed the file `src/orders-api/AccountFreeze.cs` and the type `IOrderStore`; `ls src/*`, which shows `src/orders-web` exists; `python3 ws.py rules`, which lists `shelved#an edit inside the shelved folder`; `parts/shelved.cases.json`, whose case is an edit event on `src/orders-service-v1/OrderService.cs`; and `python3 ws.py check`, which reports nothing on this page but the expected `proof` error for its missing README row. Checked the example's sums by hand: the low bounds give 170 and the high bounds 700, which map to 2 and 5 points, as the page says.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Steps, step 1 | Not blocking. Step 1's default says "when the walk names two types, use the one with more layers, as it does". The feature layer walk's step 1 says the opposite: "when more than one type fits, such as a new field served by a new endpoint, take each one that fits", and its step 2 prints each type's table. An agent following this page drops the smaller type's layers and sizes the feature low. Verified by reading both steps. | fixed: step 1 now keeps each type's layers when the walk takes more than one, as the walk's step 1 does, scoring a shared layer once |
| 2 | contradiction | Steps, step 5; Rules; In short | Not blocking. The In short line says "sum to a range, never one number", and the first rules row says an estimate is "a range of lines and points, never a single number". Step 5 says "When both ends give the same points, give that one value." Neither labels this as an exception to the other. Verified by reading all three. | fixed: step 5 always writes a range, such as "2 to 2 points", when both ends map alike |
| 3 | enforcement | Rules, the row on `src/orders-service-v1` | Not blocking. The row "A layer never lands in `src/orders-service-v1`" is tagged `shelved#an edit inside the shelved folder`. That case is an edit event on a file in the folder. This page edits nothing: a layer "lands" there only in the estimate's text, which no hook sees. So the case does not show this rule, and the tag should be `prose`. Verified: `parts/shelved.cases.json`'s case. | fixed: the row is now tagged `prose` |
| 4 | step | When to use it; Steps, step 1 | Not blocking. The trigger's example is a ticket, "how many points is ORD-412?". Step 1 takes "the ticket or plan it names" but never says how to read a ticket: no link to tracker operations' read steps or its draft mode, as bug grooming and the triage meeting give. Nor does any step check whether the ticket is a bug, which "which page wins" sends to bug grooming. An agent sizes a bug with the feature steps. Verified by reading step 1 beside bug grooming's step 1. | fixed: step 1 reads a ticket through tracker operations' steps 1 and 2, its draft mode included, and stops on a bug, which bug grooming sizes; a Rules row added |
| 5 | step | Steps, steps 2 and 3 | Not blocking. Step 2 says "For each path hint, read the code it points at". The feature layer walk says a path hint names "a repository and the kind of file, not a file that exists", and some hints name no place in the code, such as "Where the instance logs a failed run". No default says what to note when the hint leads to no code, and so which score step 3 gives a layer with nothing found. Verified by reading the walk's "Seeded, not synced" and its background job table. Inferred: that "no pattern found" is meant to score large, from the rubric's "a layer with no pattern to copy". | fixed: step 2 notes "no pattern found" when a hint names no code place or none is found, and step 3 scores such a touched layer large |

## Checked with no finding

- trigger: the purpose line, the **In short** line and "When to use it" all name sizing a feature. "Which page wins" routes a bug to bug grooming and the process decision to the size gate. `INDEX.md` has no row for the page; extend the workspace's step 5 queues an eval-covered row by default.
- placement: the rubric and points table are owned here and borrowed by bug grooming by link; the page links procedure endings and tracker operations instead of restating them.
- eval-case: the page is marked `proof: unproven` with `prove-by: M9`, and `workspace.json`'s `building` list holds only `M3`.

## Re-check

A fresh session read the page as it stands on `4190d8d`, uncommitted, beside the feature layer walk, bug grooming and tracker operations.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | Step 1 keeps each type's layers when the walk takes more than one, as the walk's step 1 does, and scores a shared layer once. Verified: both steps. |
| 2 | upheld | Step 5 always writes a range, such as "2 to 2 points", matching the **In short** line and the first Rules row. Verified: the texts. |
| 3 | upheld | The `src/orders-service-v1` row is tagged `prose`. Verified: the Rules table. |
| 4 | upheld | Step 1 reads a ticket through tracker operations' steps 1 and 2, draft mode included, and stops on a bug; the second Rules row states it. Verified: the texts. |
| 5 | upheld | Step 2 notes "no pattern found" when a hint names no code place or none is found, and step 3 scores such a touched layer large. Step 2's command, run with `IOrderStore`, printed the file `src/orders-api/AccountFreeze.cs` and the type `IOrderStore`, exit 0. Verified. |

What a fix broke:

- Not blocking. Finding 2's fix makes step 5 always write a range, such as "2 to 2 points", while bug grooming's step 5, which borrows this page's points table, still says "When both ends give the same points, give that one value". The two pages now write the same table's result two ways. Verified: both steps.

What the first reading missed:

- Not blocking. The example scores "Storage and its migration" medium, with the reason "no migration exists to copy". The rubric scores a data migration, or a layer with no pattern to copy, large, and step 3 now says a touched layer with "no pattern found" scores large. The example contradicts both; scored large, its range becomes 320 to 1,100 lines and 3 to 8 points. Verified: the rubric, step 3 and the example's sums.
