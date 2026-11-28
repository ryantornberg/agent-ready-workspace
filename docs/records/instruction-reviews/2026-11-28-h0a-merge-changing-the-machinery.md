---
kind: record
last-reviewed: 2026-11-28
covers: docs/changing-the-machinery.md
reviewed-at: 4f75faf, with the uncommitted change of the H0a builder
---

# Instruction review: docs/changing-the-machinery.md

This records the review of changing the machinery as the merge of origin/main into M4 slice H0a joined it, for that merge's author.

**In short:** no findings.

## Scope

In scope: the page as staged on 4f75faf (slice H0a) in the merge of 0426275 (origin/main, holding slices G0 and G1), merge base f04fddf, and only how the sides' changes sit together. Main brings G1's changes: step 6's sentence on retargeting stacked pull requests, the paragraph on `python3 ws.py merge NUMBER`, the `direct_push` bullet, and the rules row on the merge helper. H0a brings its rules row on the grader hash and the stamp, and its rewrite of the trap "A change the eval covers cannot pass the commit check until the eval has run". Each side's text was reviewed on its own branch, in `2026-11-28-g1-changing-the-machinery.md` and `2026-11-28-h0a-changing-the-machinery.md`, and is not reviewed again here. Read: `git show :docs/changing-the-machinery.md`; `git diff --cached HEAD` and `git diff --cached 0426275` of the page; the page in full. Read beside it: `AGENTS.md`; the README and `docs/parts.md` as staged; `.github/workflows/ci.yml`. Ran `git merge-file -p` on the three versions into the scratchpad: exit 0, and the output is byte for byte the staged page, so git resolved nothing by hand. Ran `python3 ws.py check` in the worktree, whose copy of the page has no unstaged change: exit 0, nothing on this page.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|

No findings.

## Checked with no finding

- contradiction: H0a's trap says to commit a change that needs the runs with `git commit --no-verify` and push its branch; G1's `direct_push` bullet says a push to any other branch than main loads nothing, so that push goes ahead, and says a guard change is pushed without `--no-verify`. The two name different commands, the commit and the push, and agree. H0a's rules row says CI's check against the pull request's base holds a `grade.py` change; G1's merge paragraph counts only the pull request's own CI run, which is the run whose `--changed-from` is the pull request's base, so G1 makes H0a's statement hold at the merge. Verified: both texts and `ci.yml`'s `check --phase ci --changed-from` step, whose base is `github.event.pull_request.base.sha` on a pull request. H0a's "open no pull request until the commit with the records passes every hook" and G1's step 6 and merge paragraph read in sequence. Verified, read.
- duplicate, dangling or lost text: G1's hunks sit in the steps, the merge paragraph, the `direct_push` bullet and one rules row; H0a's in one new rules row and one trap. H0a's row sits after the row "A change the eval covers fails the commit check", below G1's rewritten merge row, and each appears once. No conflict marker is left. Verified: `git merge-file` output equals the staged page, and each side's diff shows only the other side's changes.
- step: the join adds no command; the commands the sides named, `python3 ws.py merge NUMBER`, `gh pr ready NUMBER`, `python3 evals/grade.py --recorded --stamp` and `python3 ws.py check --commits origin/main..HEAD`, are unchanged. Verified, read.
- trigger: neither side changed the purpose line, the **In short** line, a heading or the machinery table. Verified, diff.
- enforcement: each rules row keeps its own side's tags, and the `rules` check passes on the page. Verified: `python3 ws.py check`, exit 0.
- placement: each side's text stays in the section its own review placed it in; the join moved nothing. Verified, read.
- eval-case: the page is marked unproven with `prove-by: M4`, and the join adds no behavior beyond the two sides'. Verified, front matter read.
