---
kind: reference
last-reviewed: 2026-11-16
applies-to: "src/orders-api/**"
---

# Rule: the live order service

You are editing `src/orders-api`, the live order service. These hold for every change here.

**In short:** this is the live service, not the shelved copy; the team's words map to the names below; and a change follows its page.

- **This is the code that runs.** `src/orders-service-v1` has the same names and is shelved, kept read-only for audits. A fix made there fixes nothing.
- **The team's words map to these names.** "The nightly job" is `ReconciliationWorker`. "A hold" is `AccountFreeze`. The [index](../../INDEX.md#search-aliases) lists the rest.
- **A change here is a bug fix or a feature, and follows its page.** Small fixes follow [fix a bug](../playbooks/fix-a-bug.md): a test that fails first, then the fix.
