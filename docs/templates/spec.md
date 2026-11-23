---
kind: template
last-reviewed: 2026-11-22
---

# Spec template

What a spec holds: the design spec inside a hand-off plan, and four standalone records for work that changes no code. For the agent writing one.

**In short:** a spec says what will be true, or what was found, not how to get there. A design spec is not a page of its own: it is the plan's Goal, Non-goals and Success criteria. Work that changes no code gets a standalone spec of one of four kinds. An investigation answers a question. An audit checks things against a standard. A retrospective, also called a postmortem, explains what happened. A baseline measures the current state before a change.

## Which spec

| The work | Spec | Where it lives |
|---|---|---|
| Passes [the gate](../size-the-work.md#the-gate) | None | Go to [fix a bug](../playbooks/fix-a-bug.md). |
| Anything else that climbs [the ladder](../size-the-work.md#the-ladder) | Design spec | The hand-off plan in `docs/plans/` |
| A question to answer | Investigation | `docs/records/specs/` |
| A set of things to check against a standard | Audit | `docs/records/specs/` |
| Something happened, and the team needs to know why | Retrospective | `docs/records/specs/` |
| A change is coming, and it needs a number to compare against | Baseline | `docs/records/specs/` |

A standalone spec changes no code. A change it leads to goes through [the gate](../size-the-work.md#the-gate) like any other.

Before you write a standalone spec, check whether a playbook covers the task. If one does, follow it: each says what it writes down, and none adds a standalone spec.

- A failure whose cause is not known: [debugging](../playbooks/debugging.md).
- Drift between the pages of `docs/`: [docs audit](../playbooks/docs-audit.md).
- Why a review missed a defect: [defect escape analysis](../playbooks/escape-analysis.md).
- How a prompt shaped a past session: [prompt retrospective](../playbooks/prompt-retrospective.md).
- A question for sources outside this workspace: [federated search](../playbooks/search-every-source.md).

Write a standalone spec only for a task no playbook covers. Even then, write one only when the person asks for a record to keep, or a plan will cite it. Otherwise, answer in the session's report.

## The design spec

The design spec is three sections of the hand-off plan: Goal, Non-goals and Success criteria. It has no template of its own; its skeleton is the [hand-off plan template](hand-off-plan.md#skeleton). [The spec process](../size-the-work.md#the-spec-process) says when to write it, how the person agrees to it, and how to word each requirement. It also says what to do when reality diverges. This page adds no rule to it.

A spec elsewhere often has sections this workspace keeps in other places:

| Part of a spec | Here |
|---|---|
| Context | The plan's Goal, with a link to any standalone spec the work started from |
| Requirements | The plan's Success criteria, each in [a requirement form](../size-the-work.md#writing-a-requirement) with its command |
| Decisions, with their reasons | The plan's "Settled decisions" for the person's; "Decisions made without asking" for the author's; a [decision record](../playbooks/decision-interview.md#when-a-decision-gets-a-record) for a hard-to-reverse call |
| Open questions | Settled by the [decision interview](../playbooks/decision-interview.md) before the person agrees to the spec |
| Doc changes | Slices of the plan, like any other change |
| Status | The plan's `status`, as [when reality diverges](../size-the-work.md#when-reality-diverges) says |

Whether a spec is kept up to date after the work ships, or frozen as written, is not settled yet. [The spec process](../size-the-work.md#when-reality-diverges) says a decision record will settle it.

## The standalone specs

Each one is a record. Copy the shared skeleton, then add the sections of its kind below.

- **Place and name:** `docs/records/specs/<YYYY-MM-DD>-<kind>-<topic>.md`, such as `2026-11-22-baseline-export-time.md`. The date is the day you start.
- **Front matter:** `kind: record` and `last-reviewed`. An optional `lane` names the team it serves.
- **Opening:** the title, a purpose sentence, then the **In short** line. A record may leave that line out; a spec keeps it, because it carries the answer.
- **Claims:** mark each claim **verified** or **inferred**, as [the report](../procedure-endings.md#the-report) does. Give the file, the command or the record that backs it.
- **The commit read:** name the commit you read, from `git rev-parse --short HEAD`, so a later reader can see the same state.

Every kind ends with its own closing section, then "Where the findings go". When the record is written, finish as [procedure endings](../procedure-endings.md) says.

### The shared skeleton

```markdown
---
kind: record
last-reviewed: YYYY-MM-DD
---

# <Kind>: <topic>

<One sentence: what this record answers, checks, explains or measures, and who reads it.>

**In short:** <the answer, verdict, cause or number, first.>

## Context

<Who asked, on what date, and why. Link the request or the plan. The commit read.>

## Scope

<What it covers, and what it leaves out.>

<The sections of its kind, below.>

## Where the findings go

| Finding | Goes to | State |
|---|---|---|
```

In "Where the findings go", each row names one finding, the page or record it went to, and its state: done in a named commit, offered, or waiting on the person's yes.

### Investigation

A question to answer. It ends with the answer.

```markdown
## Question

<The one question, as asked. What would count as an answer.>

## Method

<What you read and ran, in order. Exact commands.>

## Evidence

- verified: <what you ran or read, and what you saw>
- inferred: <what you reasoned from it>

## Answer

<The answer in one or two sentences. How sure you are, and what would change it. Questions left open.>
```

Where its findings go:

- A change the answer calls for goes to [the gate](../size-the-work.md#the-gate). A plan that follows links this record under its Goal.
- A design choice it raises goes to the [decision interview](../playbooks/decision-interview.md).
- A fact a guidance page should state goes through the [research ladder's offer](../research-ladder.md#offer-to-write-a-finding-down).

### Audit

A set of things checked against a standard. It ends with a verdict.

```markdown
## Standard

<What each item is checked against: a page, a rule or a checklist. Link it, at the commit read.>

## Items

<The set checked, and how it was chosen: all of them, or a sample and how it was drawn.>

## Results

| Item | Check | Result | Evidence |
|---|---|---|---|

## Verdict

<Counts of pass, fail and not checked. The failures, most severe first.>
```

Each result is `pass`, `fail` or `not checked`. A `not checked` row says why.

Where its findings go:

- A failure among the items checked stays in this record's Results and Verdict. Its fix goes through [the gate](../size-the-work.md#the-gate), like any other change.
- A defect found in passing, outside the items checked, goes to the [defect register](defect-register.md), as that template says.
- A gap in the standard itself goes to the person. A guidance page changes only on their yes.

### Retrospective

What happened and why, after the fact; many teams call it a postmortem. It ends with actions.

```markdown
## Timeline

| When | What happened | Source |
|---|---|---|

## Impact

<Who or what it affected, and for how long.>

## Causes

<Each cause with its evidence. Ask why until you reach something a change could prevent.>

## What went well

## Actions

| Action | Owner | Lands in |
|---|---|---|
```

A cause names a step, a page, a check or a tool, never a person. Every timeline row names its source: a commit, a record or a transcript.

Where its findings go:

- An action is a change, and goes to [the gate](../size-the-work.md#the-gate).
- A lesson goes to the [lessons log](lessons-log.md) in the same commit as the change that prevents it, as that template says. When that change is queued instead of made, the queue line carries the lesson in one line.
- A defect that a review missed goes to [defect escape analysis](../playbooks/escape-analysis.md).

### Baseline

A measurement of the current state before a change. It ends with how to measure again.

```markdown
## What is measured, and why

<The measure, and the change it will be compared against. Link the plan.>

## Method

<The exact commands, the commit measured, the machine, and how many runs.>

## Results

| Measure | Value | Runs | Spread |
|---|---|---|---|

## Noise

<What makes the number move between runs, and by how much.>

## How to measure again

<The command, unchanged, so the same measure can run after the change.>
```

Where its findings go:

- The plan for the change cites it in its Success criteria, such as "no new warnings against the baseline of <date>".
- A measure that already fails a standard goes to the [defect register](defect-register.md), as that template says.

## Rules

| Rule | Enforced by |
|---|---|
| A standalone spec changes no code; a change it leads to goes through the gate. | `prose` |
| Where a playbook covers the task, follow it instead of writing a standalone spec. | `prose` |
| A standalone spec is a page of kind `record`. | `page_kinds#a page in a kind's folder must be of that kind` |
| A standalone spec lives in `docs/records/specs/`. | `prose` |
| A standalone spec ends with its kind's closing section, then "Where the findings go". | `prose` |
| A standalone spec names the commit it read, and marks each claim verified or inferred. | `prose` |
| An audit's `not checked` row says why. | `prose` |
| A retrospective names a cause in a step, a page, a check or a tool, never in a person. | `prose` |
| Every row of a retrospective's timeline names its source. | `prose` |
