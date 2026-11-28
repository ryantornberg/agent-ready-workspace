---
kind: record
last-reviewed: 2026-11-28
covers: docs/parts.md
reviewed-at: d1041d4
---

# Instruction review: docs/parts.md

This records the review of the parts page as the merge of origin/main into M4 slice G1 joined it, for that merge's author.

**In short:** no findings.

## Scope

In scope: `docs/parts.md` at d1041d4, the merge of 4cee990 (origin/main, holding slice G0) into 63c240a (slice G1), and only how the two sides' changes sit together. G1's change is the `python3 ws.py check --push REMOTE` row of the phases table under "A check". G0's change is the `building` row of "The manifest" and one sentence in the `proof` row of "The parts here". Each side's text was reviewed on its own branch, in `2026-11-28-g1-parts.md` and `2026-11-28-g0-parts.md`, and is not reviewed again here. Read: `git show d1041d4:docs/parts.md`; `git show --cc d1041d4 -- docs/parts.md`, which prints no hunk, so the merge resolved nothing by hand; each side's diff from the merge base f04fddf; "A check", "The manifest" and "The parts here" in full, with the `direct_push` and `review_trailer` rows. Read beside it: `AGENTS.md`; the README at d1041d4, its `proof` and machinery rows and its `direct_push` Limits bullet; `docs/changing-the-machinery.md` at d1041d4; `workspace.json` at d1041d4, its `building` list and `direct_push` entry; `parts/proof.py`, `parts/direct_push.py` and `parts/review_trailer.py` at d1041d4, for `PHASES`. Ran `git merge-file -p` on the three versions into the scratchpad: exit 0, and the output is byte for byte the page at d1041d4. Ran `python3 ws.py check` in the worktree at 534e4be, whose page is the same as d1041d4's: exit 0, one warning from `eval_record` on `docs/playbooks/fix-a-bug.md`, nothing on this page.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|

No findings.

## Checked with no finding

- contradiction: G0's `building` row says the sign-off commit changes `workspace.json`, which is machinery, so a sign-off merges through a pull request. G1's push row says the manifest and the push checks come from the remote's tip, and the `direct_push` row refuses a push to main that changes a machinery path. `workspace.json` is on the tip's `machinery` list at d1041d4, so the two rows agree on why a sign-off cannot go straight to main. G1's row says that on a push to main each other check loads from the tip only to read its `PHASES`; `proof`, which G0 extends, sets no `PHASES`, so it runs at the commit and in CI only, as the README's `proof` row says. The `building` row's example, `["M4"]`, is still the manifest's list at d1041d4. Verified: read at d1041d4; `grep PHASES` finds `("push",)` in `direct_push.py` and `review_trailer.py` and nothing in `proof.py`; the manifest printed.
- duplicate, dangling or lost text: the join is the plain three-way union. G1's hunk sits in "A check" and G0's two in "The manifest" and "The parts here", over 200 lines away; no conflict marker is left; neither side's sentence is repeated or cut. Verified: `git merge-file` output equals the page, `git show --cc` prints no hunk, and `grep` finds no conflict marker.
- step: the joined rows name `python3 ws.py check --push REMOTE` and link changing the machinery, decision 0006 and layout's tutorials, as the two sides did; the join adds no command. Verified, read.
- trigger: neither side changed the purpose line, the **In short** line, a heading or the front matter, which stays `proof: unproven`, `prove-by: M4`, `last-reviewed: 2026-11-18`. Verified: the front matter is the same in the base, both parents and the merge.
- enforcement: G0's `proof` sentence keeps its case, and G1's row states no new must or never; the joined page passes `rules`, `proof` and `page_kinds`. Verified: `python3 ws.py check`, exit 0.
- placement: each side's text stays in the table its own review placed it in, the phases table for G1 and the manifest and parts tables for G0; the join moved nothing. Verified, read.
- eval-case: the page is marked `proof: unproven` with `prove-by: M4`, and the join adds no behavior. Verified, front matter.
