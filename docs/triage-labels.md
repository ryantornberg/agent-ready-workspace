---
kind: reference
lane: product
last-reviewed: 2026-11-23
---

# Bug triage labels

The labels every bug carries so a triage meeting can sort it without reading it, for whoever files, grooms or triages a bug.

**In short:** a new bug carries exactly one label from each of five categories (`affects`, `trigger`, `seen`, `kind`, `effort`), one `area` label, and optionally one predecessor label. Whoever files the bug sets them, and triage's preparation labels any bug that arrives without. Labels describe the fault; triage decides its priority. Grooming replaces the `effort` label with its own size.

This is a lane draft: product lane. It is not used on real work yet; M9 first uses it on real work.

## Why labels

A triage meeting's cost is reading time, not ticket quality. The answers to "who does it hurt" and "when does it happen" were in every ticket, but no list could show them. One label per question lets a list group and sort bugs before anyone reads one.

They are labels, not custom fields, because adding a label needs no tracker administrator.

## The five categories

Pick exactly one label from each.

| Category | Label | Means |
|---|---|---|
| `affects`: who loses something | `affects:end-user` | A customer or other person outside the company. |
| | `affects:staff` | People inside the company who use the product, such as support or finance. |
| | `affects:team-only` | Only the team that builds the product, such as a broken script or a noisy log. |
| | `affects:nobody-yet` | Nobody until something else changes, such as a feature turned on or a limit reached. |
| `trigger`: when it happens | `trigger:normal-path` | On the ordinary path a person takes. |
| | `trigger:specific-input` | Only with specific data or specific steps. |
| | `trigger:other-system-fails` | Only when another system fails, such as a payment service timing out. |
| `seen`: how we know | `seen:observed` | Someone watched it happen: in use, in a test, or in a log. |
| | `seen:code-reading` | Found by reading code; nobody has watched it happen. |
| `kind`: what breaks | `kind:functional` | The product does the wrong thing. |
| | `kind:security` | Someone can see or do what they should not. |
| | `kind:accessibility` | Someone using assistive technology, or a keyboard alone, cannot use it. |
| | `kind:data` | Stored data is lost, wrong or duplicated. |
| | `kind:tooling` | The team's own tools, builds or tests. |
| | `kind:wording` | Text on screen or in a message is wrong or unclear. |
| `effort`: the filer's guess | `effort:small`, `effort:medium`, `effort:large` | How big the fix looks to whoever filed it. |

## Area

Every bug carries one `area:<name>` label, naming the part of the product it is in. Use a name from this list. Default: when no area fits, propose a new one to the person and leave the area label as proposed. Adding its row here is a change to this page, made as [extend the workspace](extend-the-workspace.md) says, before the label is used.

The list below is invented for this sample's order system. An instance replaces it with its own.

| Label | Part of the product |
|---|---|
| `area:checkout` | Placing an order. |
| `area:holds` | Holds on accounts (`AccountFreeze` in the code). |
| `area:reconciliation` | The nightly job that matches payments to orders (`ReconciliationWorker`). |
| `area:reports` | Downloads and reports, such as the quarterly orders report. |

## The optional label

One more label says whether the shelved predecessor has the same fault. Set it only when someone checked, as [checking a shelved predecessor](predecessor-check.md) says. With no check, set none.

| Label | Means |
|---|---|
| `predecessor:carried-over` | The predecessor has the same fault. |
| `predecessor:introduced-here` | The predecessor does not have it. |

## Boundary rules

- **`affects` is about loss, not visibility.** A silent loss counts: wrong data nobody has noticed yet still affects the person whose data it is.
- **The trigger says when; the kind says what breaks.** A security fault reached only with crafted input is `trigger:specific-input` and `kind:security`.
- **A dependency that always fails is the normal path.** `trigger:other-system-fails` is for a failure that comes and goes.
- **A ticket bundling several faults takes its worst one's labels.** Worst means a `kind:security` or `kind:data` fault first, then the widest `affects`, then the most common `trigger`.
- **`effort` is a guess, not an estimate.** [Bug grooming](playbooks/bug-grooming.md) sizes the bug and replaces the `effort` label with that size, on the person's yes. A bug that has grooming's size needs no `effort` label.
- **Priority is not a category.** Labels describe the fault. The [triage meeting](playbooks/bug-triage-meeting.md) decides what happens to it.

## Who sets them

Whoever files the bug, person or agent, sets every label when filing. The [bug report template](templates/bug-ticket.md) leaves labels to triage and sets none, so a bug may arrive without them. The [triage meeting](playbooks/bug-triage-meeting.md#steps)'s preparation proposes labels for any bug that arrives without them, and sets them on the person's yes. The template still leaves the fields triage sets, such as priority, empty. Every label write on a tracker follows [tracker operations](playbooks/tracker-operations.md#which-writes-need-a-yes).

## Example

An invented bug, `ORD-421`: a hold placed on an account is lifted when the nightly job runs, so held orders ship. Support saw it happen on two accounts.

`affects:end-user`, `trigger:normal-path`, `seen:observed`, `kind:functional`, `effort:medium`, `area:holds`.

## Rules

| Rule | Enforced by |
|---|---|
| A new bug carries exactly one label from each of the five categories and one area label. | `prose` |
| A new area is added to this page's list, as extend the workspace says, before it is used. | `prose` |
| The predecessor label is set only when someone checked. | `prose` |
| Labels never set priority; triage decides. | `prose` |
| Every label write on a tracker follows tracker operations. | `prose` |
