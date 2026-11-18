---
kind: template
last-reviewed: 2026-11-18
---

# Hand-off plan template

The plan an agent works from when the work is too big for [fix a bug](../playbooks/fix-a-bug.md). A driver-tier session writes it, a fresh session red-teams it, and a person approves it. That approval is the only one the building sessions need.

**In short:** a hand-off plan says what is true when the work is done, in terms a script could check, and the exact commands that check it. It also says what not to touch, what to do when something goes wrong, and which tier runs each slice.

## The five things it must hold

| Section | Holds | Fails when |
|---|---|---|
| Success criteria | What is true at the end, stated so a script could check it | A criterion says "works", "clean" or "better" with no command behind it |
| Verification | The exact commands the agent runs itself, and what each must print or return | A command needs a person to judge its output |
| Non-goals | What the work must not touch, and how far a change may reach | It is empty: every plan has a boundary |
| Recovery | What to do when a step fails. By default: halt and report. Do not improvise. | It invites the agent to "work around" a failure |
| Tier per slice | One tier from the [orchestration rules](../orchestration.md) for each slice | A slice that changes a gate is not at the driver tier |

## How to use it

1. Copy the skeleton below into `docs/plans/<name>.md`. Keep `status: draft`.
2. Put the person's settled decisions at the top, in their words. Do not reopen them.
3. Fill every section. Write "none" rather than deleting one.
4. Have a fresh session red-team the plan. It gets the plan and the sources, never your reasoning. Record every finding in the triage table.
5. Ask the person to approve. On approval, set `status: approved` and fill the approval line.
6. As slices finish, append each slice's report under "Results". Never edit the approved sections. A change of plan is a new dated entry under "Changes after approval": a `### YYYY-MM-DD` heading, then a line `Approved by: <name>, <date>`, then the change. The front matter is not a section this rule freezes: an approved plan may gain a key, such as `milestone`. See [decision 0006](../decisions/0006-what-proven-means.md) for the anchor and demotion lines an entry may carry.
7. When a slice's work contradicts a criterion of a slice not yet built, such as a decision record that changes what a hook does, propose the revised criterion in that slice's report. Do not leave it for the later slice to find.

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

- <What the person must know before approving, most important first.>

## Settled decisions

<The person's decisions, in their words, with dates. Not reopened here.>

## Goal

## Non-goals

## Why this needs a plan

<Which of the four size-gate conditions it fails.>

## Slices

| Order | Slice | Work | Tier | Done when |
|---|---|---|---|---|

## Success criteria

<Numbered. Each one names the command in "Verification" that checks it.>

## Verification

<The exact commands, and what each must print or return.>

## Recovery

## Stop rule

<When to stop the whole plan and report, rather than push on.>

## Limits

<Fix-round limit for any unattended run. Where commits go. Who pushes.>

## Records this plan must leave

## Red team

| # | Finding | Verdict | Action |
|---|---|---|---|

## Approval

Approved by: <name>, <date>. Or: not yet approved.

## Changes after approval

## Results
```
