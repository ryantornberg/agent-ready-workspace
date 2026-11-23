---
kind: template
lane: qa
last-reviewed: 2026-11-23
---

# Regression candidates ledger template

The shape of the ledger that lists bugs proposed as new regression cases, and the bar a bug meets to earn a row. For QA and triage.

**In short:** one file, `docs/records/regression-candidates.md`, one row per candidate. A bug earns a row only when it meets all four conditions of the bar. A row's status says whether a case was written, declined or is still proposed. Three gaps in the process are open.

This is a lane draft: QA lane. It has not been run on real work yet; M10 first uses it on real work.

## When to add a row

Add a row only when a bug meets the bar below, which is often once its fix merges. A person adds most rows then; no procedure prompts it yet. [Regression triage](../playbooks/regression-triage.md) may add one for a bug its run noted off a checkpoint, which no case guards yet. A failing case never earns a row, since its case exists. A row that becomes a case follows the [regression case template](regression-case.md).

## The bar

A bug earns a row only when all four hold:

1. **It reached people, or would have.** Someone outside the team met it, or would have once the code shipped.
2. **It is on a path the suite covers, or should.** The journey is one a regression run walks, or one worth adding.
3. **It can be checked by what is seen.** A case can judge it from the screen or a data sink, without reading the code.
4. **A fix exists to hold.** The fix is merged, so the case guards it against a return.

A bug that fails one condition gets no row. Say which condition failed in the report of the session that judged it.

## Where it lives

One file, `docs/records/regression-candidates.md`, a record page. It carries `kind: record` and `last-reviewed`, as [layout](../layout.md#page-kinds) gives a record. Add rows at the bottom with your edit tools, and commit as [procedure endings](../procedure-endings.md#the-commit) says.

## Skeleton

```markdown
---
kind: record
last-reviewed: <YYYY-MM-DD>
---

# Regression candidates

The bugs proposed as new regression cases, each meeting the bar in the [regression candidates ledger template](../templates/regression-candidates.md#the-bar), for QA and triage.

| Date | Case and priority | Ticket | What to test | Tier | Why | Status |
|---|---|---|---|---|---|---|
| YYYY-MM-DD | <proposed case id>, <P1, P2 or P3> | <ticket key> | <the journey and the checkpoint that would catch it> | <smoke or full> | <which harm it guards against, in one line> | proposed |
```

## Filling it in

- **Date:** the day the row is added.
- **Case and priority:** a case id that is free in its area, and the priority, as the [case template](regression-case.md#filling-it-in) defines them.
- **Ticket:** the bug's key. One row per ticket.
- **What to test:** the journey, and the checkpoint a person could see fail if the bug came back.
- **Tier:** the suite tier, as the case template defines it.
- **Why:** the harm the case guards against, such as lost orders or a wrong total.
- **Status:** `proposed`; `written: <case id>` once the case file exists; or `declined: <reason>`. Change the status in place.

## A worked example

The row below is invented, and so is its ticket.

| Date | Case and priority | Ticket | What to test | Tier | Why | Status |
|---|---|---|---|---|---|---|
| 2026-12-04 | HOLD-002, P2 | ORD-418 | Lift a hold on an account with two held orders; both orders move to "Ready to ship". | full | Customers' second order stayed held after the lift, so it never shipped. | proposed |

## Open gaps

These are open, not settled. Each needs a person's decision before M10 runs the ledger on real work.

- **No agreed process with QA.** Who reviews a proposed row, and how a row becomes a case, is not agreed with QA.
- **No owner for pruning.** Nobody owns removing rows that are stale or declined. Until someone does, rows stay.
- **Which candidates get automated.** Whether a written case runs as `automated`, `agent` or `human` is an open question.

## Rules

| Rule | Enforced by |
|---|---|
| A bug gets a row only when it meets all four conditions of the bar. | `prose` |
| One row per ticket; its status changes in place. | `prose` |
| The three open gaps stay named as open until a person settles each one. | `prose` |
