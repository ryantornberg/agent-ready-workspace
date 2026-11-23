---
kind: playbook
lane: development
proof: unproven
prove-by: M9
last-reviewed: 2026-11-23
---

# Feature layer walk

How an agent lists every layer a feature of a known type touches, before planning or estimating it. For developers and agents starting a feature.

**In short:** name the feature's type, then print its layer list from the tables below, then the verification reminder. Each layer has a path hint and a delegation hint. It is a checklist, never a generator: it writes no code.

This is a lane draft: development lane. It has not been run on real work yet; M9 runs it, as [decision 0006](../decisions/0006-what-proven-means.md) says.

## When to use it, and which page wins

Use it when a feature's type is known and someone needs its layers: to fill a plan's slices, or to feed an effort estimate.

- It does not size or start the work. The change itself goes through [the size gate](../size-the-work.md#the-gate), and a feature that fails it climbs [the feature ladder](../size-the-work.md#the-feature-ladder).
- It does not list callers of existing code. That is [impact analysis](impact-analysis.md). When you fill a plan's slices, run both: this walk lists the layers the feature adds, and impact analysis lists the existing code its goal reaches.

## Seeded, not synced

The layer lists below are seeded for this sample's stack: `src/orders-api`, the live order service in C#, and `src/orders-web`, its TypeScript front end. An instance rewrites them for its own stack. The kit, planned in slice C8 of M3, is to copy them once and never update them, so an instance's lists are its own to keep true.

Path hints name a repository and the kind of file, not a file that exists. Folder layout inside a repository is the instance's choice. Never put a layer in `src/orders-service-v1`: it is shelved and read-only, and a hook refuses edits to it.

## The feature types

| Type | Use it when the feature |
|---|---|
| A new API endpoint | Adds a route to `src/orders-api` that a client calls. |
| A new screen | Adds a page or view to `src/orders-web`, using endpoints that exist. |
| A new field end to end | Adds one piece of data that is stored, served and shown, such as a note on an order. |
| A background job | Adds work that runs on a schedule or a queue, like `ReconciliationWorker`, "the nightly job". |
| A call to an outside system | Adds a call from `src/orders-api` to a service this workspace does not hold, such as a payment provider. |

## The layer lists

Each row is one layer: what it is, a path hint, and a delegation hint. The tiers come from [orchestration](../orchestration.md#the-three-tiers).

**A new API endpoint**

| Layer | Path hint | Delegation hint |
|---|---|---|
| Request and response contracts | `src/orders-api`, beside the endpoint | Keep in session: the shapes bind every later layer. |
| The endpoint and its routing | `src/orders-api`, where routes are registered | Worker tier, against the plan's slice. |
| Domain logic | `src/orders-api`, such as a type next to `AccountFreeze` | Keep in session when it is new logic; it starts with the reuse checklist. |
| Data access | `src/orders-api`, an interface like `IOrderStore` | Mechanical tier first: list the store's existing methods. |
| Authorization | `src/orders-api`, where the service checks callers | Keep in session: a mistake here is a security fault. |
| Tests | Beside the code, in the test project the instance names | Written first, as [test first](test-first.md) says; never delegated apart from the code. |

**A new screen**

| Layer | Path hint | Delegation hint |
|---|---|---|
| The client call | `src/orders-web`, where calls to `src/orders-api` live | Mechanical tier: list the endpoints the screen needs and confirm each exists. |
| The screen and its components | `src/orders-web` | Worker tier, after the outside-world check in the feature ladder's step 3. |
| State and validation | `src/orders-web`, beside the screen | Keep in session with the screen. |
| Accessibility | The screen's own files | Driver tier, as the "Accessibility and visual" dimension of the [review orchestrator](review-orchestrator.md#the-dimensions). |
| Tests | Beside the screen, in the runner the instance names | Written first, with the screen. |

**A new field end to end**

| Layer | Path hint | Delegation hint |
|---|---|---|
| Storage and its migration | `src/orders-api`, the store and its schema change | Keep in session: a migration is hard to reverse. |
| Domain type | `src/orders-api`, the record that carries the data | Keep in session. |
| Contracts | `src/orders-api`, every response that returns the type | Mechanical tier: list each contract that holds the type. |
| Client and screen | `src/orders-web`, such as `QuarterlyExport` when an export shows it | Worker tier, once the contracts are settled. |
| Search aliases | [INDEX.md](../../INDEX.md#search-aliases), if people call it by another word | Keep in session. INDEX.md is covered by the eval, so the change is queued as [extend the workspace](../extend-the-workspace.md#steps) step 5 says. |
| Tests | Each repository's own tests | Written first, layer by layer. |

**A background job**

| Layer | Path hint | Delegation hint |
|---|---|---|
| The worker | `src/orders-api`, a class like `ReconciliationWorker` | Keep in session. |
| Its schedule or trigger | `src/orders-api`, where workers are registered | Mechanical tier: find how existing workers are registered. |
| Data access | `src/orders-api`, an interface like `IOrderStore` | Mechanical tier first: list the store's existing methods. |
| Rerun safety | The worker | Keep in session: decide what a second run on the same day does. |
| Logging and alerts | Where the instance logs a failed run | Worker tier. |
| Tests | Beside the worker | Written first. |

**A call to an outside system**

| Layer | Path hint | Delegation hint |
|---|---|---|
| The client wrapper | `src/orders-api`, one type that owns the call | Keep in session. |
| Configuration and secrets | Where the instance keeps settings; never a secret in the repository | Keep in session. |
| Timeouts, retries and failure handling | The client wrapper | Keep in session: this decides what users see when the system is down. |
| A fake for tests | Beside the tests | Worker tier. |
| Tests | Beside the wrapper | Written first, against the fake. |

## Steps

1. **Name the type.** Input: the request or the plan's goal. Match it against [the feature types](#the-feature-types). Default: when more than one type fits, such as a new field served by a new endpoint, take each one that fits. When none fits, stop and report that no list fits, with the nearest type. Output: the type or types.
2. **Print the layers.** Input: the type or types. Print each type's table from [the layer lists](#the-layer-lists), unchanged, one after the other. For each path hint, name the real folder when the request or the code shows it; otherwise leave the hint as it stands. Output: the layer list.
3. **Start the delegation hints with reuse.** Input: the layer list. Above it, print one line: before any layer gets new logic, the author runs the [reuse checklist](reuse-checklist.md). Each hint is advice for the plan's slices, not a dispatch. This walk hands nothing off. Output: the line.
4. **Print the verification reminder.** Input: the list. Below it, print one line: the feature is done only when it meets the [definition of done](../definition-of-done.md). Output: the line.
5. **Report.** Input: steps 1 to 4. End as [procedure endings](../procedure-endings.md) says. The report gives each type from step 1 and the list with both lines. Output: the report.

Stop when the report is given.

## Rules

| Rule | Enforced by |
|---|---|
| The walk writes no code; it prints a checklist. | `prose` |
| The walk hands nothing off; its delegation hints are advice for a plan. | `prose` |
| Never put a layer in `src/orders-service-v1`. | `shelved#an edit inside the shelved folder` |
| An instance rewrites the seeded lists for its own stack; the kit, planned in slice C8 of M3, is never to update them. | `prose` |
| Tests are written first and never delegated apart from the code they test. | `prose` |
| Never put a secret in the repository. | `prose` |
