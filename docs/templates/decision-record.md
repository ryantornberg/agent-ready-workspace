---
kind: template
last-reviewed: 2026-11-23
---

# Decision record template

The shape of a decision record, also called an architecture decision record, and how one changes once decided. For anyone writing or amending a record in `docs/decisions/`.

**In short:** a record is numbered, and names its status, its date and who decided. It opens with an **In short** line, then four sections in order: Context, Decision, What it gave up, Options rejected. An accepted record changes only by a dated "Amended" paragraph. The `decisions` check holds every record to this shape.

## When to write one

Only when the three conditions in [when a decision gets a record](../playbooks/decision-interview.md#when-a-decision-gets-a-record) hold and the person says yes. An approved plan that asks for a record is that yes; such a record may start at `status: accepted`, naming the plan in `deciders`. One record states one decision. Its rule goes on the page that owns the rule, as [the style guide](../authoring.md) says; the record says why, and that page links it.

## The file

`docs/decisions/<NNNN>-<topic>.md`: the next free four-digit number, a hyphen, then the topic in lower-case words joined by hyphens. Two records never share a number. A number is never reused, not even for a rejected record.

## Front matter

| Key | Holds |
|---|---|
| `kind` | `decision`. |
| `status` | `proposed`, `accepted`, `superseded` or `rejected`. |
| `date` | `YYYY-MM-DD`: the day the record was accepted or rejected. On a proposed record, the day it was proposed. A superseded record keeps its accepted date. |
| `deciders` | Who decided, such as `the maintainer`. On a proposed record, who will decide. |
| `last-reviewed` | `YYYY-MM-DD`, as [layout](../layout.md#page-kinds) says. |
| `supersedes` | Optional: the number of the record this one replaces, such as `0003`. |
| `superseded-by` | On a superseded record only, and required there: the number of the record that replaces it. |
| `lane` | Optional: the one lane the decision binds, from the values [layout](../layout.md#page-kinds) lists. |

## The opening

1. The title: `# <NNNN>: <the decision, as a statement>`, with the file's number. Write what was decided, such as "Pages go straight to main", not the topic alone.
2. The **In short** line: the decision in one or two sentences. A proposed record also says who decides and what stage the idea is at. A purpose sentence between the title and this line is optional, as [layout](../layout.md#page-kinds) says.

A superseded record adds a line under its **In short** line that starts `Superseded by`, links its successor, and names each clause that still binds, or says that none does.

## The sections

These four, in this order:

| Section | Holds |
|---|---|
| `## Context` | What forced a choice: the problem, the facts and the limits. Not the decision. |
| `## Decision` | What was decided, as rules a reader can follow. |
| `## What it gave up` | Each cost the decision accepts. |
| `## Options rejected` | Each workable option not taken, and why. Several records written before this template call it `## Rejected`, which the check accepts. |

A record may add other sections after Context, each only when it has something to say: `## Rules`, a rules table as on other pages; `## Out of scope`; `## Open questions`, each with who owns it; `## Revisiting`, what evidence would reopen the decision; `## Credit`; `## Related`.

## How a record changes

- **Proposed.** Edit it freely until it is decided. A deferral is a dated sentence in the record, and the status stays `proposed`.
- **Accepted.** It is frozen, as [layout](../layout.md#the-opening) says, and changes only by an amendment. An amendment is a paragraph that starts `Amended YYYY-MM-DD, <who or which slice>:`, then says what changed. When it extends a section, it may instead open that section's new paragraph after a bold heading, or sit in the list item it adds, as `amended YYYY-MM-DD by <who>`. An amendment that changes what the **In short** line sums up edits that line too.
- **Superseded.** A new record replaces it. The new one carries `supersedes`; the old one takes `status: superseded`, `superseded-by` and its `Superseded by` line. Nothing else in it changes.
- **Rejected.** Keep it, with `status: rejected` and the day of the rejection as its `date`, so the question is not reopened without its history.

The front matter of a frozen record may change, as layout says: its review date, its status and a new key.

## What the check holds

The `decisions` check reads every page directly in `docs/decisions/` but its README. It fails a record whose file name, number, `date`, `deciders`, title or supersession break the rules above, or that lacks one of the four sections or holds them out of order. Where an added section sits is the author's; the check does not place it. It also fails the word "Amended" or "amended" with no date after it, or a date before the record's own, unless the word sits in code or in double quotes. It fails when the folder holds no record. It does not judge whether an edit to an accepted record is an amendment; nothing does, as layout says.

## Skeleton

```markdown
---
kind: decision
status: proposed
date: YYYY-MM-DD
deciders: <who decides>
last-reviewed: YYYY-MM-DD
---

# <NNNN>: <the decision, as a statement>

**In short:** <the decision in one or two sentences; while proposed, who decides and at what stage the idea is>.

## Context

<What forced a choice.>

## Decision

<What was decided, as rules a reader can follow.>

## What it gave up

- <A cost the decision accepts.>

## Options rejected

- **<An option.>** <Why it was not taken.>
```

## Rules

| Rule | Enforced by |
|---|---|
| A record's file name is a four-digit number and a topic, and no two records share a number. | `decisions#a file name without a four-digit number fails`, `decisions#two records with one number fail` |
| A record names its date and who decided. | `decisions#a record with no date fails`, `decisions#a record with no deciders fails` |
| Its title starts with its own number. | `decisions#a title whose number differs from the file name fails` |
| It holds Context, Decision, What it gave up and Options rejected, in that order. | `decisions#a missing section fails`, `decisions#sections out of order fail` |
| An amendment carries its date, on or after the record's own. | `decisions#an amendment without a date fails`, `decisions#an amendment dated before the record fails` |
| A superseded record names its successor in its front matter and in a `Superseded by` line. | `decisions#a superseded record without superseded-by fails`, `decisions#a superseded record without its banner fails` |
| An accepted record changes only by an amendment. | `prose` |
| A record is written only when the three conditions hold and the person says yes; an approved plan that asks for one is that yes. | `prose` |
