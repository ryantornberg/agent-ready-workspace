---
kind: reference
last-reviewed: 2026-11-22
---

# Records

What this folder holds: records of work that happened, kept as evidence. For anyone checking what a review, a fix or a run found.

**In short:** one folder or file per record type, each with its shape on a template or a playbook. Every page here other than a README is `kind: record`. A folder is created by the first record written into it.

| Record | Place | Named | Shape |
|---|---|---|---|
| Fix record | `fixes/` | `<YYYY-MM-DD>-<topic>.md`, one per fix | [Fix record template](../templates/fix-record.md) |
| Review record, for a review with no plan and no fix record | `reviews/` | `<YYYY-MM-DD>-<branch or pull request>.md` | [Review orchestrator](../playbooks/review-orchestrator.md#steps), step 10 |
| Investigation, audit, retrospective or baseline | `specs/` | `<YYYY-MM-DD>-<variant>-<topic>.md` | [Spec template](../templates/spec.md) |
| Handoff note in keep mode | `handoffs/` | `<YYYY-MM-DD>-<topic>.md` | [Handoff, "Two modes"](../playbooks/handoff.md#two-modes) |
| Defect register | [defects.md](defects.md) | one file | [Defect register template](../templates/defect-register.md) |
| Lessons log | [lessons.md](lessons.md) | one file | [Lessons log template](../templates/lessons-log.md) |
| Red team review record | `adversarial-reviews/` | as its playbook says | [Adversarial review, "The record"](../playbooks/adversarial-review.md#the-record) |
| Instruction review record | [instruction-reviews/](instruction-reviews/README.md), with its index | as its playbook says | [Instruction review, "The record"](../playbooks/instruction-review.md#the-record) |

Three records live elsewhere. The [question log](../question-log.md) sits at the top of `docs/`, where the contract links it. A design spec and an interview summary sit inside their hand-off plan in `docs/plans/`. Every template and record shape is indexed in [templates](../templates/README.md).
