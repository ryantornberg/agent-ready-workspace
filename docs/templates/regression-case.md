---
kind: template
lane: qa
last-reviewed: 2026-11-23
---

# Regression case template

The shape of one regression case: a user journey with checkpoints a run can judge. For whoever writes or fixes a case, person or agent.

**In short:** one case per file. A heading names the case and its journey. Fixed fields follow, then numbered steps, each with a checkpoint. Sink checks say where data must land; residue says what the case leaves behind. Expectations come from what the product is meant to do, never from the code.

This is a lane draft: QA lane. It has not been run on real work yet; M10 first uses it on real work.

## When to use it

Use it to add a case to a suite, or to fix one that [regression triage](../playbooks/regression-triage.md) found to be a test defect or intended behavior. A [regression run](../playbooks/regression-run.md) reads each case file in this shape. A row in the [regression candidates ledger](regression-candidates.md) is often where a new case starts.

## Where copies go

In the instance, one file per case at `regression/cases/<area>/<case-id>.md`. The folder is the instance's choice; this path is the default. This repository holds no suite and no cases.

A case checker that validates each file against this shape is planned for M10. Until it exists, a run checks the files by reading them.

## Skeleton

```markdown
# <CASE-ID>: <the user journey, in one line>

- **Priority:** <P1, P2 or P3>
- **Tier:** <smoke or full>
- **Mode:** <automated, agent or human>
- **Fixture:** <the accounts and data the case needs before step 1>
- **Source:** <the ticket or requirement the expectations come from>

## Steps

1. <action>
   Checkpoint: <what is observably true now>
2. <action>
   Checkpoint: <what is observably true now>

## Sink checks

- <where data must land, and what it must hold: a database row, an email, a log line>

## Residue

- <what the case leaves behind, and how to clean it up>
```

Keep every heading. Write "none" under one with nothing in it, so a reader can tell it was considered.

## Filling it in

- **Case id:** the area's short name and a number, such as `HOLD-001`. It never changes once a run has used it, even when the journey's wording does.
- **Priority:** `P1` means a failure blocks a release. `P2` means it needs a ticket before the release. `P3` means it can wait.
- **Tier:** the suite tier that selects the case. A `smoke` case runs on every run that selects by tier; a `full` case runs when the run selects the full suite. A run narrowed to an area or a case id runs only what it names. This is not an agent tier from [orchestration](../orchestration.md).
- **Mode:** `automated` when the instance's test runner drives it. `agent` when a helper session drives a browser. `human` when it needs a real device, so a person runs it from a checklist.
- **Fixture:** name test accounts and data by their role, never a real person's details.
- **Source:** the ticket key or the requirement's link. Every expectation in the case traces back to it.
- **Steps and checkpoints:** one action per step. A checkpoint states what a person could see or check, such as a message, a status or a total. What a run records at each checkpoint is on [regression run](../playbooks/regression-run.md#steps).
- **Sink checks:** where the journey must leave a trace outside the screen. Name the store and what it must hold. An instance's case file holds the instance's real query command. This page shows one as a placeholder in angle brackets, since this repository has no store to query.
- **Residue:** the rows, mails or files the case creates, and how to remove them. Write "none" only when the case creates nothing.

### Where expectations come from

Take every checkpoint from product intent: the source ticket, the spec, or the product owner's answer. Never derive one from reading the code. A case written from the code passes on the bug it should catch.

When intent and the product disagree, the case keeps the intent and fails. [Regression triage](../playbooks/regression-triage.md) decides whether that is a regression or intended behavior.

## A worked example

The case below is invented, and so is its ticket. Its expectations come from that invented ticket, ORD-412: a held account's orders are accepted but not shipped until the hold is lifted.

```markdown
# HOLD-001: A customer orders while their account is on hold, and the order ships once staff lift the hold

- **Priority:** P1
- **Tier:** smoke
- **Mode:** agent
- **Fixture:** a test customer account with one saved address; a staff account allowed to place and lift holds
- **Source:** ORD-412 (invented)

## Steps

1. As staff, place a hold on the test customer's account with the reason "address check".
   Checkpoint: the account page shows the hold and its reason.
2. As the customer, place an order for one item.
   Checkpoint: the confirmation page shows the order as accepted, with the status "On hold".
3. As staff, lift the hold.
   Checkpoint: the order's status changes to "Ready to ship".

## Sink checks

- The order store holds one order for the test account, accepted at step 2: `<the instance's query for orders by account>`.
- The customer's test mailbox holds one confirmation email for the order, and no shipping email before step 3.
- The server log holds one line recording the hold's lift, with the staff account's id.

## Residue

- One order and one lifted hold on the test account. Cancel the order as staff; the lifted hold may stay.
```

## Rules

| Rule | Enforced by |
|---|---|
| One case per file, in the skeleton's shape, with every heading kept. | `prose` |
| Every checkpoint comes from product intent, never from reading the code. | `prose` |
| A fixture never holds a real person's details. | `prose` |
| A case id never changes once a run has used it. | `prose` |
