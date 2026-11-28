---
kind: record
last-reviewed: 2026-11-28
covers: docs/maintain-the-workspace.md
reviewed-at: c37afc9, with the uncommitted change of the G0 session
---

# Instruction review: docs/maintain-the-workspace.md

This records the instruction review of M4 slice G0's change to the page on upkeep duties, for its author and its readers.

**In short:** 2 findings, not blocking: 1 step, 1 placement. The page names no maintainer while `building` is empty, which G0 makes a recurring state. It also omits the new sign-off step from the duties a closing milestone sets off.

## Scope

In scope: the opening paragraph of "Periodic duties", which the diff against c37afc9 changes to say the current plan is the approved one, and that an abandoned plan naming the same milestone does not count. Also read, as touched by it: the whole page, the "What the checks catch for you" table and the "Periodic duties" table above all, and the front matter (`proof: unproven`, `prove-by: M5`, `last-reviewed: 2026-11-22`). Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, decision 0006 and decision 0007, `docs/parts.md`'s `building` row, `kit/kit.json`'s `workspace.json` entry, the front matter of every plan in `docs/plans/`, the M4 plan's "Approval" section, `docs/size-the-work.md`'s plan statuses, and the machinery diff `origin/main..c37afc9`. Ran `python3 ws.py check` in the worktree with the change uncommitted: exit 0, no finding on this page.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | "Periodic duties", the opening paragraph | Not blocking. The owner of each periodic duty is the approver of "the approved one whose `milestone` is listed under `building`". When `building` is empty, no plan qualifies, and the page gives no default owner. G0 makes that state recur here: the `proof` check now fails the sign-off commit unless it drops the milestone, and the parts page says the next milestone adds itself only when its first slice merges. An instance the kit makes starts with `building` empty. Verified: `_signed_off_building` in `parts/proof.py`; the `building` row of `docs/parts.md`; `kit/kit.json` sets `building` to `[]`. Inferred: that between a sign-off and the next milestone's first slice, this definition names no maintainer. | fixed: the opening paragraph now names a default. With `building` empty, the current plan is the approved plan with the latest `Approved by:` date; in an instance with no approved plan yet, the person who adopted it owns the duties. |
| 2 | placement | "Periodic duties", the table; "What the checks catch for you", the `proof` row | Not blocking. The page lists every upkeep duty, and its wrapper fires for the duties a closing milestone sets off. Its "Pages due for proof" row names a step due at sign-off, with the `proof` check as its backstop. The new step at sign-off, removing the milestone from `building`, has the same shape, and the page names it nowhere: not in the duties, and not in the `proof` row of the checks table. It is stated on the parts page, the adoption page and decision 0006 only. Verified: the page, read in full; the `building` row of `docs/parts.md`; the description in `plugin/skills/maintain-the-workspace/SKILL.md` as the skill listing gives it. | fixed: a duty row, "Leaving `building`", says to remove the milestone in the sign-off commit, which merges through a pull request. The `proof` row of the checks table names a milestone left in `building`, and a Rules row tags `proof#a building entry whose milestone record is signed off fails`. |

## Checked with no finding

- contradiction: the new sentence matches the plans: `docs/plans/m4-fail-closed-guards-review-loop-and-evals.md` is `approved` with `milestone: M4` and an `Approved by:` line, and `docs/plans/decision-queue.md` is `abandoned` with `milestone: M4` (verified, read). It matches decision 0006's amendment on approved plans (verified, read).
- trigger: the change touches no purpose line, **In short** line or index row (verified, diff).
- enforcement: the changed paragraph states a definition, not a must; the page's Rules table is unchanged and its tags pass the `rules` check (verified, `python3 ws.py check`).
- eval-case: the page is marked `proof: unproven` with `prove-by: M5` (verified, front matter).
