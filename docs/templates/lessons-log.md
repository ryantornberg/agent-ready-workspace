---
kind: template
last-reviewed: 2026-11-22
---

# Lessons log template

The shape of the lessons log, which records each mistake that led to a change that stops it happening again. For whoever makes that change.

**In short:** one file, [docs/records/lessons.md](../records/lessons.md), one row per lesson: the date, the lesson, and the page, check or other artifact that changed. A row goes in only in the same commit as that change. A lesson with no change behind it is not logged.

## When to add a row

Add a row when a mistake led you to change what prevents it: a rule on a page, a check, a hook, a template or an eval case. The commit that makes the change adds the row. Two procedures end with such a change:

- [Maintain the workspace](../maintain-the-workspace.md), when the same mistake shows up twice.
- [Defect escape analysis](../playbooks/escape-analysis.md), once it has changed what let a defect through.

A lesson you learned but did not act on is not a row. Raise it in your report, or offer it as the [research ladder](../research-ladder.md#offer-to-write-a-finding-down) says.

Sometimes the change is queued instead of made: listed for slice Z, or for the maintainer's batch of edits the eval covers. Then the queue line carries the lesson in one line. The commit that later makes the change adds the row.

## Where it lives

One file, `docs/records/lessons.md`, a record page. Add rows at the bottom with your edit tools, and commit as [procedure endings](../procedure-endings.md#the-commit) says.

## Skeleton

```markdown
| Date | Lesson | Artifact updated |
|---|---|---|
| YYYY-MM-DD | <what went wrong, and what now prevents it, in one or two sentences> | <link to the page and section, or the part and its case, that changed> |
```

## Filling it in

- **Date:** the day of the commit that changed the artifact.
- **Lesson:** what went wrong, then what now stops it. Write it so a reader who was not there can tell when it applies.
- **Artifact updated:** link the page and its section, or name the part and the case that shows the rule. Several artifacts may share one row.
- Rows only add. A lesson that a later change retires keeps its row; add a new row for the change.

## Rules

| Rule | Enforced by |
|---|---|
| A row is added only in the same commit as the change to the artifact that prevents a repeat. | `prose` |
| A queued change's queue line carries its lesson in one line, and the commit that makes the change adds the row. | `prose` |
| Rows only add; none is edited or deleted. | `prose` |
