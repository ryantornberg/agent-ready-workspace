---
kind: record
last-reviewed: 2026-11-28
covers: docs/parts.md
reviewed-at: 4f75faf, with the uncommitted change of the H0a builder
---

# Instruction review: docs/parts.md

This records the review of the parts page as the merge of origin/main into M4 slice H0a joined it, for that merge's author.

**In short:** no findings.

## Scope

In scope: the page as staged on 4f75faf (slice H0a) in the merge of 0426275 (origin/main, holding slices G0 and G1), merge base f04fddf, and only how the sides' changes sit together. Main brings G1's rewrite of the `python3 ws.py check --push REMOTE` row of the phases table, and G0's `building` row of the manifest table and its sentence in the `proof` row of the parts table. H0a brings its rewrite of the `eval_record` row of the parts table. Each side's text was reviewed on its own branch, in `2026-11-28-g0-parts.md`, `2026-11-28-g1-parts.md`, `2026-11-28-g1-merge-parts.md` and `2026-11-28-h0a-parts.md`, and is not reviewed again here. Read: `git show :docs/parts.md`; `git diff --cached HEAD` and `git diff --cached 0426275` of the page; the phases paragraph on the commit-msg hook and `check --commits`, the manifest table and the parts table in full. Read beside it: `AGENTS.md`; the README and `docs/changing-the-machinery.md` as staged; `parts/eval_record.py` and `parts/direct_push.py`, their imports and `PHASES`. Ran `git merge-file -p` on the three versions into the scratchpad: exit 0, and the output is byte for byte the staged page, so git resolved nothing by hand. Ran `python3 ws.py check` in the worktree, whose copy of the page has no unstaged change: exit 0, nothing on this page.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|

No findings.

## Checked with no finding

- contradiction: G1's push row says the push checks, their cases and the engine library they import come from the remote's tip. H0a's `eval_record` row describes a check that runs at the commit and in CI, not at the push, so the push row does not govern it. Verified: `parts/eval_record.py` sets no `PHASES`, and `parts/direct_push.py` sets `("push",)`. G0's `building` row and `proof` sentence agree with H0a's naming of M4's slice H0b as later work. Verified, read. That no other sentence on the page reads differently because of the other side is inferred, from grepping the staged page for `tip`, `engine`, `grader`, `stamp`, `building`, `direct_push` and `H0b`.
- duplicate, dangling or lost text: G1's push row sits in the phases table, about 250 lines above the parts table; there, G0's `proof` row and H0a's `eval_record` row are separate rows with the `kit_drift` and `aliases` rows between them, so git merged them without a conflict. Neither side's sentence is repeated or cut, and no conflict marker is left. Verified: `git merge-file` output equals the staged page.
- step: the join adds no command; the page names `python3 ws.py check --push REMOTE` and `python3 evals/grade.py --recorded --stamp`, as the sides did. Verified, read.
- trigger: neither side changed a heading, the purpose line or the **In short** line. Verified, diff.
- enforcement: the rows are descriptions, not rules tables; the `rules` check passes on the page. Verified: `python3 ws.py check`, exit 0.
- placement: each side's text stays in the row of the phase, key or part it describes; the join moved nothing. Verified, read.
- eval-case: the page's procedure for adding a part is unchanged by the join, which adds no behavior. Verified, diff.
