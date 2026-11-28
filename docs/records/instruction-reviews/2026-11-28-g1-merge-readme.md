---
kind: record
last-reviewed: 2026-11-28
covers: README.md
reviewed-at: d1041d4
---

# Instruction review: README.md

This records the review of the README as the merge of origin/main into M4 slice G1 joined it, for that merge's author.

**In short:** no findings.

## Scope

In scope: the README at d1041d4, the merge of 4cee990 (origin/main, holding slice G0) into 63c240a (slice G1), and only how the two sides' changes sit together. G0's change is the sentence "A milestone leaves the manifest's `building` list when its record is signed off." at the end of the `proof` row of "What is checked, and by what". G1's change is two Limits bullets: the `direct_push` and `no_admin_merge` bullet, and the `python3 ws.py merge` bullet. Each side's text was reviewed on its own branch, in `2026-11-28-g0-readme.md` and `2026-11-28-g1-readme.md`, and is not reviewed again here. Read: `git show d1041d4:README.md`; `git show --cc d1041d4 -- README.md`, which prints no hunk, so the merge resolved nothing by hand; each side's diff from the merge base f04fddf; the "What is checked, and by what" table and Limits in full. Read beside it: `AGENTS.md`; `docs/parts.md` at d1041d4, its `building`, `proof` and `direct_push` rows; `docs/changing-the-machinery.md` at d1041d4; the `direct_push` entry of `workspace.json` at d1041d4. Ran `git merge-file -p` on the three versions into the scratchpad: exit 0, and the output is byte for byte the README at d1041d4. Ran `python3 ws.py check` in the worktree at 534e4be, whose README is the same as d1041d4's (`git diff d1041d4 HEAD` touches only `docs/records/defects.md`): exit 0, one warning from `eval_record` on `docs/playbooks/fix-a-bug.md`, nothing on this page.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|

No findings.

## Checked with no finding

- contradiction: G0's `proof` row says a milestone leaves `building` at sign-off, and G1's `direct_push` bullet says the pre-push hook takes the machinery list from the remote's tip. `workspace.json` is on that list at d1041d4, so a sign-off pushed straight to main is refused, which agrees with the "Machinery ... reaches main only through a pull request" row and with the parts page's `building` row. G1's `python3 ws.py merge` bullet, on check runs, workflow runs and the retarget, says nothing about proof marks or `building`. Verified: read at d1041d4, and the manifest's `direct_push` entry printed. That no other README sentence outside the two changed regions now reads differently because of the other side's change is inferred, from reading both regions and grepping the page for `building`, `signed off`, `direct_push`, `machinery`, `pre-push` and `retarget`.
- duplicate, dangling or lost text: the join is the plain three-way union. G0's hunk sits in "What is checked, and by what" and G1's two in Limits, about 170 lines apart; no conflict marker is left; neither side's sentence is repeated or cut. Verified: `git merge-file` output equals the page, `git show --cc` prints no hunk, and `grep` finds no line starting with `<<<<<<<`, `=======` or `>>>>>>>`.
- step: the joined text names `python3 ws.py rules`, `git push --no-verify` and `python3 ws.py merge`, as the two sides did; the join adds no command. Verified, read.
- trigger: neither side changed a heading, a purpose line or a table header, so the join changes no routing. Verified: the page's headings at d1041d4 match both parents'.
- enforcement: G0's row keeps its tags, the `proof` check and `direct_push`, with "Commit, CI; before a push"; G1's bullets state limits and add no tag. The `rules` and `proof` checks pass on the joined text. Verified: `python3 ws.py check`, exit 0.
- placement: each side's text stays in the section its own review placed it in, the rules table for G0 and Limits for G1; the join moved nothing. Verified, read.
- eval-case: the README is not a procedure and carries no proof mark, and the join adds no behavior. Verified, read; `eval_record` reports nothing on it.
