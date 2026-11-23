---
kind: template
lane: qa
last-reviewed: 2026-11-23
---

# QA test plan template

The shape of the QA test plan handed to testers for a release or a change, for whoever writes it, person or agent.

**In short:** five fixed headings, in order: Before you start, Scenario checklists, Do not file, Not in this release, Sign-off. Each copy's reader is the tester. What goes under each heading follows the [QA verification list](../playbooks/qa-verification-list.md). The copy goes on the tracker's QA sub-task.

This is a lane draft: QA lane. It has not been used on real work yet; M6 first uses it on real work.

## Where a copy goes

A copy is written in the session's reply, then copied into the QA sub-task on the team's tracker. That copy is an outward write: make it as [tracker operations](../playbooks/tracker-operations.md) says, or give the person the text. This repository keeps no copy.

## Skeleton

Keep the headings in this order. Every heading stays. [Rule 10](../playbooks/qa-verification-list.md#the-rules) of the QA verification list says what an empty section holds.

```markdown
## Before you start

- Environment: <where to test, by the name testers use>
- Accounts: <which accounts or roles, and where to get them>
- Build: <the version testers see on screen>

## Scenario checklists

### <Scenario: one user journey>

- [ ] <Place>, then <action>: <observable result>.
- [ ] <Place>, then <action>: <observable result>.

## Do not file

| What you see | Why it is expected | Ticket |
|---|---|---|
| <what the tester sees> | <why, in plain words> | <ticket key> |

## Not in this release

- <a change testers might expect, which ships later>

## Sign-off

- Tested by: <name>
- Date: <YYYY-MM-DD>
- Result: <pass, pass with findings, or fail>
- Findings: <one change-request sub-task per finding, or "none">
```

## Filling it in

A copy is a page for a product reader, so the [rules for such a page](../product-reader-pages.md) apply to it too.

- **Before you start:** only what a tester needs before the first scenario.
- **Scenario checklists:** one scenario per user journey, each item written as [the verification list's rules](../playbooks/qa-verification-list.md#the-rules) say.
- **Do not file:** each known issue a tester will meet in this build, with its ticket, so it is not reported twice.
- **Not in this release:** changes a tester might look for that ship later.
- **Sign-off:** the tester fills it in. Each finding goes on the tracker as one change-request sub-task, as the "A finding from testing" row of [tracker operations](../playbooks/tracker-operations.md#the-operations) says. The build is the one "Before you start" names.

## Worked example

Invented, and so are its tickets. ORD-431 shows staff on the order screen when an account has a hold. A held account's orders are accepted but not shipped, as `AccountFreeze` in `src/orders-api/AccountFreeze.cs` describes. ORD-437 is a known issue.

```markdown
## Before you start

- Environment: the staging site
- Accounts: a staff account, and a customer account with a hold on it; ask the release owner for both
- Build: 4.12.0, shown at the foot of every page

## Scenario checklists

### Staff see a hold on an order

- [ ] Orders, then open an order from the customer with a hold: a red "On hold" banner shows above the order lines.
- [ ] Same order, select "Why on hold": the reason staff entered shows, with the date it was set.
- [ ] Orders, then open an order from a customer with no hold: no banner shows.

### A hold stops shipping, not ordering

- [ ] Sign in as the customer with a hold, then New order, then Place order: the confirmation page shows the order as accepted, with the status "On hold".
- [ ] Sign in as staff, open that customer's account, then Lift hold: the order's status changes to "Ready to ship".

## Do not file

| What you see | Why it is expected | Ticket |
|---|---|---|
| The banner shows a moment after the order lines load. | The hold is looked up after the page loads; a later release speeds it up. | ORD-437 |

## Not in this release

- Customers cannot see why their account is on hold.
- Staff cannot place a hold from the order screen; they still place it from the account page.

## Sign-off

- Tested by:
- Date:
- Result:
- Findings:
```

## Rules

| Rule | Enforced by |
|---|---|
| A copy keeps the five headings in their order. | `prose` |
| What goes under each heading, an empty heading included, follows the QA verification list. | `prose` |
| Copying the plan into the tracker's QA sub-task follows tracker operations. | `prose` |
