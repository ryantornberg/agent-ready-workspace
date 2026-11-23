---
kind: template
lane: product
last-reviewed: 2026-11-23
---

# Epic satellites template

Three shapes that sit beside an epic's hub: questions for other teams, a tracker map, and an unattended-run plan. For whoever keeps an epic folder.

**In short:** questions for other teams and the tracker map are two more sections of the hub, `docs/plans/<epic-slug>/README.md`. The unattended-run plan is a hand-off plan in the epic folder. None is a separate page of another kind, since every page in the folder but the hub must be a plan.

This is a lane draft: product lane. It has not been used on real work yet; M9 first uses it on real work.

## Where each one lives

The [epic folder template](epic-folder.md) owns the folder and the hub. Its rule is that every page in the folder other than the hub is a plan. So:

| Satellite | Where it lives | Kind |
|---|---|---|
| Questions for other teams | A section of the hub, after "Open questions" | Part of the hub, `reference` |
| Tracker map | A section of the hub, after "Docs elsewhere" | Part of the hub, `reference` |
| Unattended-run plan | `docs/plans/<epic-slug>/unattended-run-<YYYY-MM-DD>.md` | `plan`, a copy of the [hand-off plan template](hand-off-plan.md) |

The run plan is listed under the hub's "Docs here", like any other plan in the folder. Each file is committed as [procedure endings](../procedure-endings.md#the-commit) says.

## Questions for other teams

The hub's "Open questions" holds what the epic itself must decide. This section holds what the epic must ask another team, by a date. A question goes in one of the two, never both. When an answer here settles an open question, that question's answer links this section and names the row's number, such as `[question 1](#questions-for-other-teams)`.

```markdown
## Questions for other teams

| # | Question | For | Needed by | Status |
|---|---|---|---|---|
| 1 | <the question, in one sentence> | <the team, and a person there if known> | <YYYY-MM-DD> | <not sent, sent YYYY-MM-DD, or answered: the answer in one line> |
```

- An agent drafts a question. It sends one only when the epic's owner asks it to in their own words, as [procedure endings](../procedure-endings.md#outward-writes) says for any other system.
- Number rows for good, as the epic folder template says for open questions. An answered row keeps its number and gains its answer.
- Write "none" when the epic has no question for another team.

## Tracker map

The plan's items in the order they are built, each with its tracker key. It lets a reader go from a plan to the tracker and back.

```markdown
## Tracker map

| Order | Plan item | Tracker key | Needed by |
|---|---|---|---|
| 1 | <link to the plan, or the plan and its slice> | <key, or "none yet"> | <YYYY-MM-DD> |
```

- Keys are read from the tracker as [tracker operations](../playbooks/tracker-operations.md) says. Creating a missing item is a tracker write and follows that page, its "Which writes need a yes" included.
- Update the map whenever a plan in the folder gains or loses a slice.

## Unattended-run plan

A plan for slices that run with no person present, such as overnight. It is a copy of the [hand-off plan template](hand-off-plan.md), approved by a person before the run, like any other plan. Fill these sections as follows; fill the rest as that template says.

| Section of the plan | What it holds for an unattended run |
|---|---|
| Slices | The run order: which slice runs first, and which waits for another. |
| Execution profile | The orchestrator, its tier, and the order, as [the execution profile](hand-off-plan.md#the-execution-profile) says. |
| Non-goals and Limits | The guardrails: what the run must not touch, its fix-round limit, where commits go and who pushes. With no limit set, [orchestration's limits](../orchestration.md#limits) apply. |
| Stop rule | When the whole run stops instead of going on to the next slice. |
| Records this plan must leave | The morning report's shape: each slice done, stopped or not started; each stop with its reason; what waits on a person; each claim marked verified or inferred. |
| Results | The run report, appended after the run in the morning report's shape, as the template's rule 6 says. |

## Worked example

Invented, for an epic `ord-412-account-holds` on the sample's order system. Two rows of its hub:

| # | Question | For | Needed by | Status |
|---|---|---|---|---|
| 1 | Does the payments team need an event when a hold is placed? | Payments team | 2026-12-04 | sent 2026-11-20 |

| Order | Plan item | Tracker key | Needed by |
|---|---|---|---|
| 1 | `ORD-413-hold-api.md`, slice 1 | ORD-413 | 2026-12-08 |

## Rules

| Rule | Enforced by |
|---|---|
| No satellite is a page of another kind in the epic folder: the unattended-run plan is a plan, and the other two are sections of the hub. | `page_kinds#a page in a kind's folder must be of that kind` |
| An agent sends a question to another team only when the epic's owner asks it to in their own words. | `prose` |
| A question sits under "Open questions" or "Questions for other teams", never both. | `prose` |
| An unattended-run plan is approved by a person before the run, and its run report is appended under "Results". | `prose` |
