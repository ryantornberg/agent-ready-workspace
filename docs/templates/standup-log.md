---
kind: template
lane: product
last-reviewed: 2026-11-23
---

# Standup log template

The shape of the standup log, where each saved standup report is one entry, for the agent writing the report and the person reading it.

**In short:** one file in the person's home folder, never inside a repository; by default `~/standup-log.md`. Newest entry at the top, one per standup day. Each entry holds a title line, a rollup of at most six lines, the detail in fixed sections, and three closing lines. Every line but the title carries a verified or inferred mark.

This is a lane draft: product lane. It has not been used on real work yet; M9 first uses it on real work.

## Where it lives

A file in the person's own home folder, outside every repository. Default: `~/standup-log.md`. It is never written inside a repository, so it is never committed. The [standup report](../playbooks/standup-report.md) writes it; nothing else does.

- Newest entry at the top.
- One entry per standup day.

The [standup report](../playbooks/standup-report.md#steps)'s steps 1 and 6 own the report's window and what a same-day rerun does.

## Skeleton

One entry, in this order. The rollup sits directly under the title line, with no heading.

```markdown
## <report date, YYYY-MM-DD> (since <window start, YYYY-MM-DD>)

- <track, in plain words>: <where it stands, in one clause> (<link>; <mark>)
- <up to six lines, one per epic or track>
- Blockers: <what is blocked, on whom> (<link>; <mark>)

### Done

- <outcome, one short spoken-style line> (<link>; <mark>)
  - <sub-task outcome> (<link>; <mark>)

### Doing

- <outcome> (<link>; <mark>)

### Waiting on

- <what, on whom> (<link>; <mark>)

### Other

- <outcome> (<link>; <mark>)

No movement: <the person's open items that did not move, or "none"> (<mark>)
Left out: <each item left out, named only by kind, such as "one personal item", or "none"> (<mark>)
Unavailable: <each evidence source that could not be read, with the reason, or "none"> (<mark>)
```

## Filling it in

- **Title line:** the report's date, then the window's start date.
- **Rollup:** at most six lines, one per epic or track. Name the track in plain words, say where it stands in one clause, and give one link. Then one blockers line; omit it when nothing is blocked. Everything in the rollup comes from the detail below it.
- **Sections:** Done, Doing, Waiting on and Other, in that order. Omit Waiting on when it is empty; keep the other three, writing "none" in an empty one.
- **An item** is an outcome: a pull request opened or merged, a work item filed or moved, a review result, a shipped page or tool. A commit is never an item.
- **A parent item** is one line, with its sub-tasks nested under it.
- **Each item** is one short line, the way the person would say it aloud, with at least one link.
- **Mark:** every line but the title ends with `verified` or `inferred`, as [procedure endings](../procedure-endings.md#the-report) asks of every claim in a report. Verified: a source shows the outcome itself, such as a pull request's state or an item's status. Inferred: you reasoned it, such as an outcome read from commits or a judgment that an item waits on someone. A rollup line takes the weaker mark of the items it sums.
- **An item in two sections:** an open item blocked on someone goes under Waiting on only, never also under Doing.
- **Closing lines:** no movement, left out, and any evidence source that was unavailable. Personal items are left out of every section and named only on the left-out line.

## Worked example

Invented, and so are its tickets and pull requests. The links point nowhere real.

```markdown
## 2026-11-23 (since 2026-11-20)

- Account holds: the hold banner is merged; the hold notice email is under way (https://tracker.example/ORD-431; verified)
- Nightly reconciliation: the retry fix is in review (https://git.example/orders-api/pull/88; inferred)
- Blockers: the retry fix waits on a review from the payments team (https://git.example/orders-api/pull/88; inferred)

### Done

- Merged the hold banner on the order screen (https://git.example/orders-web/pull/212; verified)
- Account holds story moved to testing (https://tracker.example/ORD-431; verified)
  - Development sub-task closed (https://tracker.example/ORD-432; verified)

### Doing

- Opened the hold notice email (https://git.example/orders-api/pull/90; verified)

### Waiting on

- Opened the retry fix for the nightly job; it waits on a payments team review (https://git.example/orders-api/pull/88; inferred)

### Other

- Reviewed the order export change; asked for one test (https://git.example/orders-api/pull/85; verified)

No movement: ORD-419, the order history filter (https://tracker.example/ORD-419; verified)
Left out: one personal item (verified)
Unavailable: none (verified)
```

## Rules

| Rule | Enforced by |
|---|---|
| The log lives in the person's home folder, never inside a repository. | `prose` |
| Newest entry at the top; one entry per standup day. | `prose` |
| Only the standup report writes the log. | `prose` |
| An item is an outcome, never a commit; a parent item is one line with its sub-tasks nested. | `prose` |
| Each item has at least one link, and sits in one section only. | `prose` |
| Every line but the title is marked verified or inferred. | `prose` |
| The rollup has at most six lines, and everything in it comes from the detail. | `prose` |
| Personal items are left out, and named only on the left-out line. | `prose` |
