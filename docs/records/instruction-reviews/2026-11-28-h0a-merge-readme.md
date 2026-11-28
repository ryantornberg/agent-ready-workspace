---
kind: record
last-reviewed: 2026-11-28
covers: README.md
reviewed-at: 4f75faf, with the uncommitted change of the H0a builder
---

# Instruction review: README.md

This records the review of the README as the merge of origin/main into M4 slice H0a joined it, for that merge's author.

**In short:** 1 finding, none blocking: 1 contradiction.

## Scope

In scope: the README as staged on 4f75faf (slice H0a) in the merge of 0426275 (origin/main, holding slices G0 and G1), merge base f04fddf, and only how the sides' changes sit together. Main brings G0's sentence at the end of the `proof` row of "What is checked, and by what", and G1's rewrites of two Limits bullets, the `direct_push` and `no_admin_merge` bullet and the `python3 ws.py merge` bullet. H0a brings its rewrite of the row on proven playbooks in the same table and the new Limits bullet "A change to `evals/grade.py` itself needs its cases recorded again." Each side's text was reviewed on its own branch, in `2026-11-28-g0-readme.md`, `2026-11-28-g1-readme.md`, `2026-11-28-g1-merge-readme.md` and `2026-11-28-h0a-readme.md`, and is not reviewed again here. Read: `git show :README.md`; `git diff --cached HEAD -- README.md`; `git diff --cached 0426275 -- README.md`; the table and Limits in full. Read beside it: `AGENTS.md`; `docs/parts.md` and `docs/changing-the-machinery.md` as staged, their push rows and `direct_push` bullet; `.github/workflows/ci.yml`; `parts/eval_record.py` and `parts/direct_push.py`, their imports and `PHASES`; the head of `wslib/runner.py`. Ran `git merge-file -p` on the three versions into the scratchpad: exit 1, one conflict, at the two adjacent rows, and the staged page differs from that output only in the resolution, which keeps H0a's row on proven playbooks and then G0's `proof` row. Ran `python3 ws.py check` in the worktree, whose README has no unstaged change: exit 0, one warning from `eval_record` on `docs/playbooks/fix-a-bug.md`, nothing on this page.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Limits, the bullet "A change to `evals/grade.py` itself needs its cases recorded again", against the bullet "`direct_push` and `no_admin_merge` close two routes past CI, not every one" | Not blocking. H0a's bullet names a third route past the rule: "an edit to a part or the engine is judged by that changed code, as `direct_push`'s limit above says." In the joined page, that limit, as G1 rewrote it, says the pre-push hook "takes the part, its cases, the library the part imports and the machinery list from the remote's tip, but the engine code that runs them is the working copy's own". So the cited text says a part, and now the library it imports, are not judged by changed code; only the engine code that runs them is. Verified: both bullets as staged. The route itself holds where it lies, in CI and the commit check: `eval_record` sets no `PHASES`, so it runs at the commit and in CI and not at the push, and CI runs `ws.py check --phase ci` from the pull request's own checkout. Verified: `parts/eval_record.py` and `.github/workflows/ci.yml`. The part half of the mismatch was already there on H0a's side, whose `direct_push` bullet said the part came from the tip; G1's move of the imported library to the tip widens it to half of what H0a calls the engine. Verified: `git show HEAD:README.md`. Fix in one line: say that CI and the commit check run the pull request's own parts and engine, so an edit to `eval_record` or the engine is judged by that changed code, and drop the citation, or cite it only for the push. | fixed: the bullet now says CI and the commit check run the pull request's own parts and engine, so an edit to `eval_record` or the engine is judged by that changed code; the citation of `direct_push`'s limit is dropped |

## Checked with no finding

- contradiction, apart from finding 1: G0's `proof` row says a milestone leaves `building` at sign-off; H0a's row and bullet name M4's slice H0b as later work, which agrees with M4 being in `building`. H0a's statement that CI's re-grade with the base's `grade.py` is the check that holds a `grade.py` change agrees with G1's merge bullet, under which only a run that a `pull_request` event started counts, since that is the run whose `--changed-from` is the pull request's base. Verified: both texts and `ci.yml`'s `check --phase ci --changed-from` step. That no other sentence outside the changed regions reads differently because of the other side is inferred, from grepping the page for `building`, `tip`, `engine`, `judged by`, `grade.py`, `stamp` and `H0b`.
- duplicate, dangling or lost text: the resolved conflict keeps both rows, each once, H0a's above G0's in the order the base had them; neither side's sentence is repeated or cut, and no conflict marker is left. G1's two Limits bullets and H0a's new bullet merged with no conflict. Verified: each side's diff against the staged page shows only the other side's changes, and `grep` finds no line starting with `<<<<<<<`, `=======` or `>>>>>>>`.
- step: the joined text names `evals/grade.py --recorded`, `python3 ws.py merge`, `git push --no-verify` and `python3 ws.py rules`, as the sides did; the join adds no command. Verified, read.
- trigger: neither side changed a heading, a purpose line or a table header, so the join changes no routing. Verified: the headings match both parents'.
- enforcement: each row keeps its own side's tags, the `eval_record` check with `evals/grade.py --recorded`, and the `proof` check with `direct_push`. The `rules` and `proof` checks pass on the joined text. Verified: `python3 ws.py check`, exit 0.
- placement: each side's text stays where its own review placed it, the rules table and Limits; the join moved nothing. Verified, read.
- eval-case: the README is not a procedure and carries no proof mark, and the join adds no behavior. Verified, read; `eval_record` reports nothing on it.
