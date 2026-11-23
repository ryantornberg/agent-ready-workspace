---
kind: record
last-reviewed: 2026-11-23
covers: docs/playbooks/decision-interview.md
reviewed-at: dace91e, with the uncommitted change of the B5 slice session
---

# Instruction review: docs/playbooks/decision-interview.md

This records the review of B5's edit to decision interview, which points a new record at the template, for its author.

**In short:** 0 findings. A record written in an interview now follows the decision record template, which agrees with the playbook's conditions, its proposed status and its review step.

## Scope

In scope, from `git diff HEAD -- docs/playbooks/decision-interview.md`: in "When a decision gets a record", the sentence that now says a record "follows the decision record template". The whole page was read to judge it, step 8, step 10 and the rules table included. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/templates/decision-record.md`, `docs/playbooks/instruction-review.md` ("When it runs"), `parts/decisions.py` and its cases.

Run: `python3 ws.py check` passes with only an `eval_record` warning about `fix-a-bug.md`, so the new link resolves (verified).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|

No findings.

## Checked with no finding

- contradiction: the template's "When to write one" links this section's three conditions and requires the person's yes, as step 8 and the rules table do. Its extra case, a record an approved plan asks for, lies outside an interview. The template's "Front matter" says a proposed record's `date` is the day proposed and its `deciders` are who will decide, which fits step 8's output, a record with `status: proposed` (verified).
- step: the record's path, the next free number in `docs/decisions/`, and its skeleton are on the linked template. A record copied from the skeleton passes the `decisions` check once its placeholders are filled (verified, the case "a record in the template's shape passes" matches the skeleton's headings and keys).
- trigger: the section's three conditions, which decide when a record is offered, are unchanged.
- enforcement: the sentence states no new must or never. A record is a guidance page, so its commit needs a review trailer, as the page says (verified, `docs/` is guidance in instruction review's "When it runs").
- placement: the page now links the template for the shape, instead of "the shape of the newest record", so the shape is stated once.
- eval-case: the page is marked unproven with `prove-by: M9` (verified, its front matter).
