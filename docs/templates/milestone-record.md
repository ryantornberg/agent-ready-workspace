---
kind: template
last-reviewed: 2026-11-15
---

# Milestone record template

What a finished milestone leaves behind: the numbers that using the workspace produced, and what the outside checks found. It is for the person signing the milestone off, and for anyone later asking whether the workspace helped.

**In short:** one page per milestone in `docs/milestones/`. It is written as the slices finish, and closed when the person signs off. Numbers come from records and commands, never from memory.

## What it records, and why

| Section | Records | Why |
|---|---|---|
| Slices | Tier, questions asked, fix rounds and what the checks caught, per slice | Shows where the workspace carried context and where it failed to |
| Outside checks | The attack scripts, CI on three systems, and the fresh-session red team with its triage | A gate cannot certify its own repair |
| Always-loaded size | The contract's size before and after, and what was deleted | Every line in the always-loaded layer costs every session |
| Records left | Links to the plan, decision records, question-log rows and evidence | Proof of use is the records, not the claim |
| Sign-off | Who signed, when, and anything they struck | Done is a person's decision |

## Skeleton

```markdown
---
last-reviewed: YYYY-MM-DD
status: in progress
---

# <Milestone>: milestone record

<One sentence: what the milestone delivered.> The plan is <link to the hand-off plan>.

**In short:** <the verdict: what holds now, the key number, and what is left>.

## Slices

| Slice | Tier | Questions asked | Fix rounds | What the checks caught | Commits |
|---|---|---|---|---|---|

## Outside checks

| Check | Result | Evidence |
|---|---|---|
| Attack scripts against a scratch copy | <n> of <n> handled | <where the output is kept> |
| CI on Linux, macOS and Windows | green or red | <run link> |
| Fresh-session red team | <n> findings, all triaged | <triage table> |

## Always-loaded size

| | Bytes | Words |
|---|---|---|
| Before | | |
| After | | |

Deleted: <what left the always-loaded layer, or "nothing">.

## Records left

## Sign-off

Signed off by: <name>, <date>. Or: not yet signed off.
```
