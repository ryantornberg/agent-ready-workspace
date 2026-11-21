---
kind: reference
last-reviewed: 2026-11-21
---

# Instruction reviews

The index of instruction-review records: each record, the pages it covers and the classes of defect it found. For reviewers, and for whoever counts a stop rule.

**In short:** one row per record. The instruction review playbook, `docs/playbooks/instruction-review.md`, says how a record is written and when a commit must name one. The `review_index` check holds each row to its record, and requires a record for each page M3's sub-batch A wrote before the review existed.

A class is counted from a record's findings, leaving out a finding the author declined. "none" means the review found nothing, or declined all it found.

| Record | Covers | Classes found |
|---|---|---|
| [2026-11-21-agents-md.md](2026-11-21-agents-md.md) | `AGENTS.md` | enforcement |
| [2026-11-21-index-md.md](2026-11-21-index-md.md) | `INDEX.md` | contradiction |
| [2026-11-21-layout.md](2026-11-21-layout.md) | `docs/layout.md` | contradiction, enforcement, placement, eval-case |
| [2026-11-21-glossary.md](2026-11-21-glossary.md) | `docs/glossary.md` | contradiction |
| [2026-11-21-decision-0006.md](2026-11-21-decision-0006.md) | `docs/decisions/0006-what-proven-means.md` | contradiction, step, enforcement |
| [2026-11-21-changing-the-machinery.md](2026-11-21-changing-the-machinery.md) | `docs/changing-the-machinery.md` | enforcement, step |
| [2026-11-21-definition-of-done.md](2026-11-21-definition-of-done.md) | `docs/definition-of-done.md` | enforcement, trigger, step |
| [2026-11-21-orchestration.md](2026-11-21-orchestration.md) | `docs/orchestration.md` | contradiction |
