---
kind: plan
last-reviewed: 2026-11-25
status: draft
milestone: M4
---

# M4, fail-closed shell guards, the review loop and the eval system: hand-off plan

The plan for the fourth milestone: close the shell guards' known gaps with one rule, then build the review loop and the eval system. Building sessions work from it; the maintainer approves it. It follows the [hand-off plan template](../templates/hand-off-plan.md).

**In short:** this is the Bound rung only: the goal and the non-goals, written before anything else, as [the ladder](../size-the-work.md#the-ladder) asks. The rest of the plan follows in the next commit.

## Key points

- This page holds the goal and the non-goals only. The slices, criteria and budgets are not written yet.
- Nothing is approved, and nothing is built from this page.

## Goal

Three things are true at the end. The work starts from M3's open ends: the "Known limits, for M4" in [M3's milestone record](../milestones/m3.md#known-limits-for-m4), and findings 7 and 10 of [its red team's record](../records/adversarial-reviews/2026-11-25-m3.md).

1. **The shell guards fail closed.** A shell guard refuses a command when a word it must judge cannot be resolved to a literal. Each route past the guards that M3's record lists for M4 is refused, with a case.
2. **No pull request opens without a review that is shown to have run.** A review mark, written only from the reviewers' own output, sits at the reviewed commit. A gate refuses a pull request without one. Teach-back and a merge policy per repository say who may publish and merge.
3. **No proven procedure and no wrapper changes without its cases running on the old and the new version.** Each of the ten pages that name M4 in `prove-by` is proven, cut, or unproven with a failed attempt on record.

## Non-goals

- **No decision queue.** [Its plan](decision-queue.md) stays a draft, and M4 builds none of its slices.
- **No matching of findings to existing threads, and no posting of comments.** Both need a git-host provider, which is M8. The guard that refuses every `gh api graphql` call stays as it is.
- **No live agent run in CI.** CI re-grades stored transcripts and checks marks. Agent runs stay on the author's machine.
- **No new wrapper, and no rise in either always-loaded ceiling:** 6,000 bytes for the contract and pointer files, 9,000 for the wrappers' descriptions. No copy of the wrappers for a second agent tool.
- **No guard on what an interpreter or a script does.** A hook reads a command line. What `python3 -c`, a script file or `curl` then does stays out of reach, and the README keeps saying so.
- **No signature on a mark.** A mark shows that a process ran on this content. It does not stop a person who edits files by hand, and the pages say so.
- **No change to an eval harness file after the first recording, and no edit to a page the eval hashes outside the closing slice.** A proof attempt's own case files are the one exemption.
- **No edit to a page under a proof attempt once its attempt has started.**
- **No reading of an agent tool's transcripts outside one adapter per tool.**
- **No machine-state records.** They go to M5, with the first instance.
- **No pattern catalog and no saved agent roles.** The dispatch script is the one place a delegation pattern is encoded.
- **No third-party package** in the engine, the parts or the tests CI runs.
- **No outward write beyond this repository,** no instance repository, and no page copied from the work workspace.

## Why this needs a plan

It fails two size-gate conditions: it is far more than one screen of diff, and far more than a day of work. Most slices change a gate, and a broken hook can lock a session out.
