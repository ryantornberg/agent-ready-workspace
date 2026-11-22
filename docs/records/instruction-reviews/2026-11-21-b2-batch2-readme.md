---
kind: record
last-reviewed: 2026-11-21
covers: README.md
reviewed-at: e1d978a, with the uncommitted change of the B2 builder
---

# Instruction review: README.md

This records the instruction review of the four batch 2 rows in the README's proof table, for their author and for readers of proof state.

**In short:** 0 findings. The four rows and the new count match the pages' proof marks and the M3 plan's prove-by table, and the check passes.

## Scope

In scope: the section Proven and unproven pages, its four new rows (`docs/playbooks/decision-interview.md`, `docs/playbooks/adversarial-review.md`, `docs/size-the-work.md#the-feature-ladder`, `docs/size-the-work.md#the-spec-process`) and its count line, read against the rest of the section and the page for anything they must agree with. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md`, `docs/decisions/0006-what-proven-means.md`, `parts/proof.py`, the batch 2 pages (`docs/playbooks/decision-interview.md` front matter, `docs/playbooks/adversarial-review.md`, `docs/size-the-work.md`, `docs/playbooks/README.md`, `docs/how-tos.md`), the B2 row and its prove-by table in `docs/plans/m3-reading-layer-machinery-and-kit.md`, and `workspace.json`'s `building` list. Commands run: `git diff README.md`, `python3 ws.py check` and `python3 ws.py check --changed-from HEAD`, both exit 0.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|

No findings.

## Checked with no finding

- contradiction: each new row's state and milestone match its page's front matter or section line: both playbooks carry `proof: unproven`, `prove-by: M9`, and both `size-the-work.md` sections open with `Proof: unproven, prove-by M9.` The milestone matches the M3 plan's prove-by table, which gives M9 to adversarial review, the decision interview, the feature ladder and the spec process. The playbook catalog's Proof column says `unproven, M9` for both playbooks. The count, 1 proven and 16 unproven, matches the 17 rows. The sentence over the table already covers section rows: "the proof line under a merged section's heading". The plan's B2 row calls both sections merged into `size-the-work.md`. Verified.
- step: each of the four links resolves, including the `#the-feature-ladder` and `#the-spec-process` anchors; `python3 ws.py check` reports no `links` finding. Verified.
- trigger: the section's heading and purpose are unchanged, and each new page or section sits in the table a reader scans for proof state. The two section rows are needed beside the existing `docs/size-the-work.md` row, since `parts/proof.py` `marks()` keys a page's front matter and each marked section separately. Verified by reading `marks()`.
- enforcement: the `proof` check holds the table to the marks, as the sentence over it says (`parts/proof.py` `_readme_table()` and its docstring), and `python3 ws.py check --changed-from HEAD` passes. M9 is not in the manifest's `building` list (`["M3"]`), so no new prove-by is refused. The count line itself is not read by the check, but the page states no rule about it. Verified.
- placement: the rows are the table the `proof` check requires in the README; the detail stays on the pages they link. Verified against `parts/proof.py` `_readme_table()`.
- eval-case: the change asks no new behavior of an agent, and every page or section it adds is marked unproven with prove-by M9. Verified.
