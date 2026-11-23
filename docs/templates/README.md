---
kind: reference
last-reviewed: 2026-11-22
---

# Templates

Every shape this workspace asks you to copy: the templates in this folder, and the record shapes another page defines. For anyone about to write a plan, a record or a standard text.

**In short:** find the row for what you are writing, open its page and copy its skeleton. The page holds the shape and its rules; the row says when to use it and where your copy goes.

## Templates in this folder

| Template | Use it when | Your copy goes |
|---|---|---|
| [Hand-off plan](hand-off-plan.md) | Work fails the [size gate](../size-the-work.md#the-gate) and needs a plan a person approves. | `docs/plans/<name>.md`, or inside an epic folder |
| [Spec](spec.md) | The design spec of a plan, or a standalone investigation, audit, retrospective or baseline. | The design spec: inside the plan. The other four: `docs/records/specs/<YYYY-MM-DD>-<variant>-<topic>.md` |
| [Epic folder](epic-folder.md) | Work needs three or more plans or specs, or is an epic in the tracker. | `docs/plans/<epic-slug>/`, with `README.md` as its hub |
| [Milestone record](milestone-record.md) | A milestone's slices are finishing and it needs its sign-off record. | `docs/milestones/m<n>.md` |
| [Project hub](hub.md) | A project, one or more repositories that ship together, has more than one documentable unit, or a unit easy to mistake for another. | `docs/projects/<project>/README.md`, with its unit pages beside it, until an instance settles the [open question on where per-repository docs live](../adopt-the-workspace.md#open-question-where-per-repository-reference-docs-live) |
| [Unit doc](unit-doc.md) | A service, library, client or piece of infrastructure needs its reference page. | Not settled: the same open question |
| [Bug ticket](bug-ticket.md) | You file or rewrite a bug in the tracker. | The tracker, as an outward write |
| [Pull request](pull-request.md) | You open a pull request, or do the bookkeeping after one merges. | The pull request's description, as an outward write |
| [Fix record](fix-record.md) | You start a fix on the [fix a bug](../playbooks/fix-a-bug.md) path. A slice of a hand-off plan reports in the plan instead. | `docs/records/fixes/<YYYY-MM-DD>-<topic>.md`, one per fix |
| [Defect register](defect-register.md) | You find a defect in passing that you are not fixing now, or defer a review finding on your own change. | One file, [docs/records/defects.md](../records/defects.md) |
| [Lessons log](lessons-log.md) | A mistake led you to change what prevents it, such as a rule, a check or a template. | One file, [docs/records/lessons.md](../records/lessons.md) |
| [Fresh-session prompt](fresh-session-prompt.md) | A person asks for a prompt to start a new session on a task, or a task needs a context of its own, such as one slice of a plan. | Not saved: your reply, in one fenced block |

An outward write, such as a ticket or a pull request description, follows [procedure endings](../procedure-endings.md#outward-writes).

## Record shapes another page defines

These have no page here. The page that holds or writes them defines the shape, so open it there.

| Record | Use it when | Shape | Your copy goes |
|---|---|---|---|
| Interview summary | A decision interview ends. | [Decision interview, "The summary"](../playbooks/decision-interview.md#the-summary) | Inside the draft hand-off plan, as that section says |
| Red team review record | A fresh session attacks a finished plan or spec. | [Adversarial review, "The record"](../playbooks/adversarial-review.md#the-record) | `docs/records/adversarial-reviews/`, named as that playbook says |
| Handoff note | A session stops mid-task and a later one carries on. | [Handoff, "The note"](../playbooks/handoff.md#the-note) | Outside every repository. Keep mode, a tracked copy, waits for M4: see [two modes](../playbooks/handoff.md#two-modes). |
| Review record | A change is reviewed by the review orchestrator. | [Review orchestrator](../playbooks/review-orchestrator.md#steps), step 10 | As step 10 says: the hand-off plan's Results, or the pull request's description |
| Instruction review record | A guidance page is added or changed. | [Instruction review, "The record"](../playbooks/instruction-review.md#the-record) | `docs/records/instruction-reviews/`, with a row in [its index](../records/instruction-reviews/README.md) |
| Question-log row | You had to ask a person something the workspace should have answered. | [Question log](../question-log.md): its table, and its kinds of gap | A row in [docs/question-log.md](../question-log.md), as [procedure endings](../procedure-endings.md#the-question-log-entry) says |
| Kickoff prompt | A newcomer starts a first real task. | [Question log, "The kickoff prompt"](../question-log.md#the-kickoff-prompt) | Not saved: pasted into a new session, with the task filled in |
| Decision record | A decision meets the three conditions in [when a decision gets a record](../playbooks/decision-interview.md#when-a-decision-gets-a-record), and the person says yes. | The newest record in [docs/decisions/](../decisions/), as [extend the workspace](../extend-the-workspace.md#steps) says | `docs/decisions/<NNNN>-<topic>.md`, with the next free number |

Every records folder is listed in [records](../records/README.md).
