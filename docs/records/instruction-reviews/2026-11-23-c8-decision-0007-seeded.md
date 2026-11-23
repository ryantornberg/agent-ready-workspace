---
kind: record
last-reviewed: 2026-11-23
covers: docs/decisions/0007-the-kit.md
reviewed-at: 215bd27, with the uncommitted change of slice C8
---

# Instruction review: docs/decisions/0007-the-kit.md

This records the review of slice C8's change that seeds the feature layer walk, for the change's author and the decision's readers.

**In short:** 2 findings: 2 contradiction; 0 blocking. The adoption how-to still says every playbook is synced and kept with `drift --keep`, which refuses the now-seeded walk. The walk's proof mark becomes the instance's own, but it still names M9 of the kit's plan, and the instance's README row calls that milestone the instance's own.

## Scope

In scope: only the uncommitted change, read with `git diff -- docs/decisions/0007-the-kit.md`. That is the Seeded row of the classes table, which now names the feature layer walk, and the last sentence of the paragraph "Proof in an instance", which says how the seed README's proof table is filled. The rest of the page was read for statements the change made false.

Read beside it: the code behind the change, `git diff -- kit/kit.json wslib/kit.py tests/test_kit.py`; `docs/playbooks/feature-layer-walk.md`; `kit/seed/README.md`; `parts/proof.py`; `docs/decisions/0006-what-proven-means.md`; `docs/adopt-the-workspace.md`; and `docs/playbooks/instruction-review.md` for the checks.

Run, from the worktree: `python3 -m unittest tests.test_kit -b` ran 28 tests, OK (verified). `python3 ws.py kit` classes the walk `seeded` and leaves it out of the manifest's `proof` map (verified). `python3 ws.py adopt` into a new scratch folder outside the worktree made an instance: 206 synced, 26 seeded, 396 never synced (verified). In the instance, `python3 ws.py check` and `python3 ws.py drift` both exit 0 (verified). Its README's table holds a row for each synced page and one more: `| [docs/playbooks/feature-layer-walk.md](...) | unproven | M9; this workspace's own page, seeded by the kit |` (verified).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | "Decision", the classes table, the Seeded row | Not blocking. The row makes the walk, a playbook, seeded. `docs/adopt-the-workspace.md`, "What transfers", still says "the playbooks and how-tos" transfer "Yes, as procedures, synced", and "To change one, keep your own copy, as decision 0007 says". The walk is an exception that page does not label (verified, reading). An agent in an instance that follows that row to rewrite the walk's layer lists runs `python3 ws.py drift --keep docs/playbooks/feature-layer-walk.md`, which exits 2: "is not a synced file in kit.lock.json, so there is nothing to keep" (verified, in the scratch instance). The refusal changes nothing and says why, and the walk's own section "Seeded, not synced" says to rewrite the lists in place. The seed README's kit table also puts "the procedures" in its Synced row and leaves the walk out of its Seeded row, though it says the table "names the main ones" (verified, reading `kit/seed/README.md`). Not blocking because following decision 0007 as written runs no failing command; the failing command comes from the how-to's row. | fixed: adopt the workspace's row says the feature layer walk is seeded and the instance rewrites its lists, and that any other page is changed by keeping it; the adopt record notes the change. |
| 2 | contradiction | "Decision", "Proof in an instance", its last sentence | Not blocking. The sentence says a seeded page's proof mark "is the instance's own from the start". The walk is seeded as a plain copy, so the instance's walk keeps `prove-by: M9` and the lines "M9 runs it, as decision 0006 says" and "The kit, planned in slice C8 of M3, is to copy them once" (verified, `grep` in the scratch instance). M9 is a milestone of the kit's plan. The instance's README row then reads "M9; this workspace's own page, seeded by the kit", while the seed README's text above the table says such a row's `prove-by` "names a milestone of this workspace's own plans" (verified). The instance has no `docs/plans/` and no `docs/milestones/` (verified, `ls`). Once its mark is the instance's own, the `proof` check holds the walk to the instance's own M9 and fails it when the instance signs off a `docs/milestones/m9.md` that never meant to run the walk (inferred, from `parts/proof.py`: the walk is not in the lock's synced pages, so every rule of decision 0006 applies). The adoption how-to's `git grep` lists M9 among the numbers to pick above, so a first milestone chosen as it says does not collide (verified, the command prints M8, M9, M10 in the instance). The decision does not say what a seeded page's kit milestone means in the instance, nor whether the kit rewrites it. | fixed: the paragraph says a seeded page's `prove-by` names the kit's milestone until the instance sets its own, and that the check reads it against the instance's own milestone records. |

## Checked with no finding

- step: the changed text names no command. The rule it describes exists in `kit/kit.json` at the path `docs/playbooks/feature-layer-walk.md`, and `ws.py kit`, `adopt`, `check` and `drift` all run and exit 0 on it (verified).
- trigger: the page's **In short** line is unchanged and still true of the change: seeded files are written once and then belong to the instance (verified, reading). The walk's own section "Seeded, not synced" agrees with the new Seeded row.
- enforcement: the changed text states no must or never. The README row it describes is held in an instance by `proof#a README row that disagrees with the page fails`: in a copy of the scratch instance with the walk's row removed, `check` fails with "its table says nothing for docs/playbooks/feature-layer-walk.md, which is marked unproven" (verified). `tests/test_kit.py` asserts the walk is a seeded page with a proof mark, and passes (verified). The code fills rows only for seeded pages under `docs/`, which matches the `proof` check's default folder; the sentence does not say so, and no seeded page outside `docs/` carries a mark today (inferred, from the `proof` check's `folders` default and the seeded rules in `kit/kit.json`).
- placement: the reason in the Seeded row is one clause, and the walk's page carries the rest. No rule that procedure endings states is restated (verified, reading).
- eval-case: a decision record carries no proof mark, and the change asks no new behavior of an agent; it describes what `adopt` writes (verified, reading).
