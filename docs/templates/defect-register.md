---
kind: template
last-reviewed: 2026-11-22
---

# Defect register template

The shape of the defect register, which keeps each defect found in passing until it is fixed or accepted. For whoever finds or settles one.

**In short:** one file, [docs/records/defects.md](../records/defects.md), with an open table and a closed table. A row is a defect you checked, with its evidence cited. It has one of four states: open, filed, accepted or fixed. A row may stay open as long as it needs to; it leaves only for the closed table, never by deletion.

## When to add a row

Add a row when you find a defect that is not the one you are working on:

- [Fix a bug](../playbooks/fix-a-bug.md) says to write down a second bug found on the way and leave it alone. Write it here.
- A finding the [review orchestrator](../playbooks/review-orchestrator.md) records, which the author defers instead of fixing, goes here. When a tracker item already holds it, its row starts in the `filed` state, with the item's key.

Before you add a row, reproduce the defect or read it in the code at the current commit. A suspicion you have not checked is not a row: put it in your report, marked inferred.

## Where it lives

One file, `docs/records/defects.md`, a record page. Add and move rows with your edit tools, and commit as [procedure endings](../procedure-endings.md#the-commit) says.

## Skeleton

```markdown
## Open

| Found | Where | What | Evidence | State |
|---|---|---|---|---|
| YYYY-MM-DD | <repository, file, and method or class> | <what goes wrong, for whom, in one sentence> | <what you ran and what you saw, or a link to it> | open, or filed: <tracker key> |

## Closed

| Found | Where | What | Evidence | Closed | How |
|---|---|---|---|---|---|
| YYYY-MM-DD | <as above> | <as above> | <as above> | YYYY-MM-DD | fixed: <commit or pull request>, or accepted: <who>, <the reason> |
```

## The four states

| State | Means | Table |
|---|---|---|
| `open` | Found and checked; no tracker item, and nobody has decided. Staying open is legitimate: a row needs no owner or date to stay. | Open |
| `filed` | A tracker item holds it. The row names the key, and stays open until the fix lands, so a review can still find it here. | Open |
| `accepted` | A person decided to leave it as it is. The row names who, and a reason a stranger could judge. | Closed |
| `fixed` | The fix is merged. The row names the commit or pull request. | Closed |

## Filling it in

- **Where:** name the file and the method, class or heading. Never a line number: it goes stale with the next edit.
- **Evidence:** a row is verified, never inferred. Cite the command you ran and what it printed, or the code you read at which commit.
- **Moving a row:** to close it, cut it from the open table and add it to the closed table with the date and how it closed. Never delete a row.
- **Reconciling:** step 5 of the review orchestrator is where a review checks the change against the open rows. No script does this yet, so the review does it by hand.

## Rules

| Rule | Enforced by |
|---|---|
| A row is a defect you reproduced or read in the code, with its evidence cited. | `prose` |
| A row's state is one of open, filed, accepted or fixed. | `prose` |
| A row is never deleted; it moves to the closed table when it is fixed or accepted. | `prose` |
| An accepted row names who accepted it and a reason a stranger could judge. | `prose` |
| A row's Where names a file and a method, class or heading, never a line number. The `line_cites` check skips a line that holds a commit hash, so it misses a row whose Evidence or How names a commit. | `prose` |
