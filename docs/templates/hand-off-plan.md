---
kind: template
last-reviewed: 2026-11-22
---

# Hand-off plan template

The plan an agent works from when the work is too big for [fix a bug](../playbooks/fix-a-bug.md). A driver-tier session writes it, a fresh session red-teams it, and a person approves it. That approval is the only one the building sessions need.

**In short:** a hand-off plan says what is true when the work is done, in terms a script could check, and the exact commands that check it. It also says what not to touch, what to do when something goes wrong, and which tier runs each slice. A plan whose slices an orchestrating session hands to helpers also says how they work together.

## The five things it must hold

| Section | Holds | Fails when |
|---|---|---|
| Success criteria | What is true at the end, stated so a script could check it | A criterion says "works", "clean" or "better" with no command behind it |
| Verification | The exact commands the agent runs itself, and what each must print or return | A command needs a person to judge its output |
| Non-goals | What the work must not touch, and how far a change may reach | It is empty: every plan has a boundary |
| Recovery | What to do when a step fails. By default: halt and report. Do not improvise. | It invites the agent to "work around" a failure |
| Tier per slice | One tier from the [orchestration rules](../orchestration.md) for each slice | A slice that changes a gate is not at the driver tier |

The plan's Goal, Non-goals and Success criteria are its design spec. They are written and agreed first, as [the spec process](../size-the-work.md#the-spec-process) says. The [spec template](spec.md) maps them to the parts a standalone spec has.

An orchestrated plan holds a sixth thing: its [execution profile](#the-execution-profile).

## How to use it

1. Copy the skeleton below into `docs/plans/<name>.md`. Keep `status: draft`. If the work is large enough for an [epic folder](epic-folder.md#when-to-use-it), the plan goes in that folder instead.
2. Put the person's settled decisions at the top, in their words. Do not reopen them.
3. Fill every section. Write "none" rather than deleting one.
4. Have a fresh session red-team the plan, as the [red team review](../playbooks/red-team-review.md) says. It gets the plan and the sources, never your reasoning. Link its record above the Red team table, and give every finding a disposition there. If its verdict is `does not hold`, stop instead: commit the record and report to the person, as that page says.
5. Ask the person to approve. On approval, set `status: approved` and fill the approval line.
6. As slices finish, append each slice's report under "Results". Never edit the approved sections. A change of plan is a new dated entry under "Changes after approval": a `### YYYY-MM-DD` heading, then a line `Approved by: <name>, <date>`, then the change. The front matter is not a section this rule freezes: an approved plan may gain a key, such as `milestone`. See [decision 0006](../decisions/0006-what-proven-means.md) for the anchor and demotion lines an entry may carry.
7. When a slice's work contradicts a criterion of a slice not yet built, such as a decision record that changes what a hook does, propose the revised criterion in that slice's report. Do not leave it for the later slice to find.
8. Keep a draft within its budgets. The Key points block holds at most 200 words. A table cell anywhere in the plan, outside fenced blocks, holds at most 60 words. A word is a run of characters between spaces. Slice detail that does not fit a cell goes under a `### <slice>` heading below the slices table. An approved, done or abandoned plan is frozen as rule 6 says, so the budgets bind only a draft.
9. List each choice you made without asking the person under "Decisions made without asking": the choice, what you rejected, and why. A reviewer reads that section to challenge your choices. Add to it as you write the rest of the plan; the spec still comes first, as [where it lives](../size-the-work.md#where-it-lives) says. A choice the person made goes under "Settled decisions" instead.
10. If the work started from an investigation, audit, retrospective or baseline, link that record under "Goal". Those records are the [standalone specs](spec.md#the-standalone-specs).
11. If an orchestrating session will hand the slices to helper sessions, fill the execution profile as [the section below](#the-execution-profile) says. Otherwise write "none" there.

## The execution profile

For a plan whose slices one session, the orchestrator, hands to helper sessions. It says how the helpers work together. Each line holds one fact; write "none" for a line that does not apply.

| Line | Says |
|---|---|
| Orchestrator | Which session hands out the slices, at which tier, and whether it commits for the helpers. |
| Order | Which slices run at the same time, and which wait for another to finish. |
| Shared interface | Where the sheet lives that every helper conforms to: fixed paths, names and shared rules. Who owns it, and how a helper asks for a change. |
| Shared code | When two or more slices need the same code: the file and the function that will hold it, and the slice that writes it. The other slices call it and write no copy of their own. |
| Nudges | How many times the orchestrator nudges a helper whose turn ends unfinished. Default: two. |

A helper's turn can end with text while its slice's "Done when" does not hold. That text is a report, not a finish. Send the helper its open items and ask it to go on, up to the profile's number of nudges. If your agent tool cannot message a helper whose turn has ended, start a new helper instead. Give it the slice, the open items and what the first helper returned, so it does not redo that work. Each new helper counts as one nudge. If the slice is still not done, halt it and record it as not done under "Results". Then do what Recovery says.

Every task the orchestrator hands off still names its tier, as [handing work off](../orchestration.md#handing-work-off) says.

## Skeleton

```markdown
---
kind: plan
last-reviewed: YYYY-MM-DD
status: draft
milestone: M<n>
---

# <Name>: hand-off plan

<One sentence: what this plan delivers, and who reads it.>

**In short:** <two or three sentences.>

## Key points

- <What the person must know before approving, most important first. At most 200 words.>

## Settled decisions

<The person's decisions, in their words, with dates. Not reopened here.>

## Decisions made without asking

<Each choice the author made alone: the choice, what was rejected, and why. Or "none".>

## Goal

<What is true at the end. Link the investigation, audit, retrospective or baseline the work started from, if any.>

## Non-goals

## Why this needs a plan

<Which of the four size-gate conditions it fails.>

## Slices

| Order | Slice | Work | Tier | Done when |
|---|---|---|---|---|

<Detail that does not fit a 60-word cell goes under a ### heading per slice, here.>

## Success criteria

<Numbered. Each one names the command in "Verification" that checks it.>

## Verification

<The exact commands, and what each must print or return.>

## Recovery

## Stop rule

<When to stop the whole plan and report, rather than push on.>

## Limits

<Fix-round limit for any unattended run. Where commits go. Who pushes.>

## Execution profile

<Only for an orchestrated run; otherwise "none".>

- Orchestrator: <session and tier; whether it commits for the helpers>
- Order: <which slices run together, which wait>
- Shared interface: <where the sheet lives, who owns it>
- Shared code: <file and function, and the slice that writes it; or "none">
- Nudges: <number; default 2>

## Records this plan must leave

## Red team

Record: <link to the adversarial review record>.

| # | Finding | Disposition | Action |
|---|---|---|---|

## Approval

Approved by: <name>, <date>. Or: not yet approved.

## Changes after approval

## Results
```

## Rules

| Rule | Enforced by |
|---|---|
| A plan holds success criteria, verification, non-goals, recovery and a tier per slice. | `prose` |
| A plan's first section is Key points. | `page_kinds#a plan whose first section is not Key points fails` |
| An approved plan changes only by a dated entry under "Changes after approval" and by reports under "Results". | `prose` |
| A draft plan's Key points block holds at most 200 words, and any table cell outside a fenced block at most 60. | `plan_budgets#a draft whose Key points block is over 200 words fails`, `plan_budgets#a draft with a table cell over 60 words fails` |
| Each choice the author made without asking the person is listed under "Decisions made without asking". | `prose` |
| An orchestrated plan names where code that two or more slices share will live, and which slice writes it. | `prose` |
| A helper whose turn ends before its slice is done gets at most the profile's number of nudges. Then the slice halts as not done. | `prose` |
