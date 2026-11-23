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
| Investigation, audit, retrospective or baseline | `specs/` | `<YYYY-MM-DD>-<variant>-<topic>.md` | [Spec template](../templates/spec.md) |
| Defect register | [defects.md](defects.md) | one file | [Defect register template](../templates/defect-register.md) |
| Lessons log | [lessons.md](lessons.md) | one file | [Lessons log template](../templates/lessons-log.md) |
| Red team review record | `adversarial-reviews/` | as its playbook says | [Red team review, "The record"](../playbooks/red-team-review.md#the-record) |
| Instruction review record | [instruction-reviews/](instruction-reviews/README.md), with its index | as its playbook says | [Instruction review, "The record"](../playbooks/instruction-review.md#the-record) |
| Regression run report set | `regression-runs/` | `<YYYY-MM-DD>-<run-id>/`, one folder per run | [Regression run report template](../templates/regression-report.md) |
| Regression candidates ledger | `regression-candidates.md` | one file | [Regression candidates ledger template](../templates/regression-candidates.md) |

Four records live elsewhere. The [question log](../question-log.md) sits at the top of `docs/`, where the contract links it. A design spec and an interview summary sit inside their hand-off plan in `docs/plans/`. A code review's record sits in its hand-off plan's "Results" or its pull request's description, as step 10 of the [review orchestrator](../playbooks/review-orchestrator.md#steps) says. Every template and record shape is indexed in [templates](../templates/README.md).
