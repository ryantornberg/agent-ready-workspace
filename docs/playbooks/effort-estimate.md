---
kind: playbook
lane: product
proof: unproven
prove-by: M9
last-reviewed: 2026-11-23
---

# Effort estimate

How an agent sizes a feature as a range of changed lines and story points, layer by layer. For product owners and agents asked how big a feature is.

**In short:** take the feature's layers from the [feature layer walk](feature-layer-walk.md), score each layer small, medium or large with a one-line reason, and sum to a range, never one number. Map the range to story points with the team's table, and list the risks. The estimate goes in the report; it sets nothing on a ticket by itself.

This is a lane draft: product lane. It has not been run on real work yet; M9 runs it, as [decision 0006](../decisions/0006-what-proven-means.md) says.

## When to use it, and which page wins

Use it when someone asks how big a feature is, such as "how many points is ORD-412?", from a request, a ticket or a draft plan.

- A bug is sized by [bug grooming](bug-grooming.md), which borrows this page's rubric and points table. These steps size features.
- An estimate never decides how much process the work gets. That is [the size gate](../size-the-work.md#the-gate), whatever the estimate says.
- The scores are a guess made before the code exists. They never replace a plan's slices.

## The rubric

Score each layer by the lines it will change, tests counted in their own layer. Never in hours.

| Score | Lines changed | Typical sign |
|---|---|---|
| none | 0 | The layer is not touched. |
| small | 10 to 50 | An existing pattern to copy, such as one more method on an interface like `IOrderStore`. |
| medium | 50 to 200 | A pattern to copy, adapted in more than one place. |
| large | 200 to 600 | New logic, a data migration, or a layer with no pattern to copy. |

A layer that looks bigger than 600 lines is scored large and listed as a risk: it likely needs a slice of its own.

## Story points

The team sets this table. The rows below are a default an instance replaces on its own copy of this page. Each end of the line range is mapped on its own.

| Total lines changed, up to | Points |
|---|---|
| 100 | 1 |
| 250 | 2 |
| 500 | 3 |
| 1,000 | 5 |
| 2,000 | 8 |
| More than 2,000 | 13, and the report says to split the feature |

## Steps

1. **Get the layers.** Input: the request, and the ticket or plan it names. Read a ticket as [tracker operations](tracker-operations.md#steps) says in its steps 1 and 2; its draft mode applies when the session has no tracker tool. When the ticket is a bug, stop: [bug grooming](bug-grooming.md) sizes it. Then run steps 1 to 4 of the [feature layer walk](feature-layer-walk.md#steps), keeping their output for this page instead of reporting it. Default: when the walk takes more than one type, as its step 1 does, keep each type's layers. Score a layer two types share once. When no type fits, stop and report that no layer list fits, with the walk's nearest type. Output: the type or types and the layer list.
2. **Read where each layer lands.** Input: the layer list. For each path hint, read the code it points at, read-only, to see whether a pattern exists to copy. With an exact name, find it with `python3 tools/symbols.py NAME src`. Default: when a hint names no place in the code, or no code is found there, note "no pattern found". No layer lands in `src/orders-service-v1`: it is shelved and read-only. Output: one note per layer on what exists there.
3. **Score each layer.** Input: the notes. Give each layer one score from [the rubric](#the-rubric) and one line of reason. Default: when a layer sits between two scores, take the larger. A layer the feature touches with "no pattern found" scores large, as the rubric says. Output: a table of layer, score and reason.
4. **Sum to a range.** Input: the scores. Add the low bounds of every score for the low end, and the high bounds for the high end. Output: the range, such as "170 to 700 lines". Never collapse it to one number.
5. **Map to points.** Input: the range. Look up each end in [the story points table](#story-points). Output: a points range, such as "2 to 5 points". When both ends map to the same points, still write it as a range, such as "2 to 2 points".
6. **List the risks.** Input: the notes and scores. Name each thing that could push the work past the high end, one line each: a layer scored large with no pattern, a data migration, a call to an outside system, a question the request leaves open. Default: when there are none, write "none found". Output: the risk list.
7. **Report.** Input: steps 1 to 6. Setting a points field on a ticket is a tracker write: make it only as [tracker operations](tracker-operations.md) says, including its "Which writes need a yes" and its draft mode. Default: with no such request or yes, the points stay in the report. End as [procedure endings](../procedure-endings.md) says. The report gives the type, the layer table, the line range, the points range and the risks. Output: the report.

Stop when the report is given.

## Example

Invented, on the sample's order system: "add a note to an order", a new field end to end.

| Layer | Score | Reason |
|---|---|---|
| Storage and its migration | medium | A new column and its migration; no migration exists to copy. |
| Domain type | small | One property on the order record. |
| Contracts | small | Two responses return the order. |
| Client and screen | medium | A text box and its display in `src/orders-web`. |
| Search aliases | none | People call it a note, as the code will. |
| Tests | medium | One test per layer above. |

Range: 170 to 700 lines. Points: 2 to 5. Risk: the migration is hard to reverse.

## Rules

| Rule | Enforced by |
|---|---|
| An estimate is a range of lines and points, never a single number, and never in hours. | `prose` |
| A bug is sized by bug grooming, not by these steps. | `prose` |
| Each layer gets one score and a one-line reason; between two scores, the larger. | `prose` |
| The estimate never decides the work's process; the size gate does. | `prose` |
| A points field on a ticket is set only through tracker operations, with its yes. | `prose` |
| A layer never lands in `src/orders-service-v1`. | `prose` |
