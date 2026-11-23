---
kind: decision
status: accepted
date: 2026-11-23
deciders: the maintainer, through M3's approved plan
last-reviewed: 2026-11-23
---

# 0020: Each disagreement in the ported pages is settled on one side, and each departure from them is deliberate

**In short:** the pages M3 ported from a longer-running workspace disagreed with each other in eleven places. This record picks one side of each and names the page here that holds the choice. It also lists each place where this workspace deliberately does something other than the ported pages did, and why.

## Context

M3 rewrote this workspace's pages from a catalog that describes a workspace a team had run for longer. The catalog found ten places where two of its pages stated one rule two ways, and an eleventh sat elsewhere in it. A rewrite that copied both sides would carry the contradiction here; one that picked a side silently would leave the next reader to rediscover it.

Some of M3's own choices also differ from the catalog on purpose. A reader who knows the other workspace, or who reads the catalog's descriptions, needs to know those differences are deliberate.

## Decision

### The eleven disagreements

| # | The two sides | The choice here | Where it lives |
|---|---|---|---|
| 1 | One table hands a review loop to a person after five rounds; three other pages say a loop has no round count. | No round count. An attended loop runs while it converges and ends on a round that only finishes earlier work. An unattended run stops after the fix rounds its plan allows, or three. | [Orchestration, "Limits"](../orchestration.md#limits) |
| 2 | One page says playbooks carry no front matter; another requires it, and every playbook has it. | Required, on every page under `docs/`. | [Layout, "Page kinds"](../layout.md#page-kinds), held by `page_kinds` |
| 3 | The contract counts five path rule files; another tool's instruction page lists four. | No page states a count. The pointer files name the rule pages' folder, and the `pointers` check holds them to it. | [Layout's rules](../layout.md#rules) |
| 4 | The audience list is singular; two pages use a plural value. | No `audience` key. A page's purpose sentence names its reader. | [Layout, "The opening"](../layout.md#the-opening) |
| 5 | Specs name four status values; pages also use done, complete and active. | A spec has no status of its own. The plan's `status` carries it: `draft`, `approved`, `done` or `abandoned`. | [Size the work, "When reality diverges"](../size-the-work.md#when-reality-diverges) |
| 6 | The review record template says status draft; later records say active. | A red team record has no status. Its verdict, one of three, carries what the status tried to. | [Red team review, "The record"](../playbooks/red-team-review.md#the-record) |
| 7 | One path treats any reviewer as stalled after 15 minutes; another gives the code reviewer 30. | One limit for every reviewer, 30 minutes, since a reviewer reading a whole diff is the slowest and a false stall pays for the review twice. No page here names a limit yet; M4's review machinery holds it. | M4 |
| 8 | Tracker pages mention logging hours; their own rule says nobody logs time. | No time is logged against a ticket. Tracker pages carry no hours, and an estimate is in points, never hours. | [Effort estimate](../playbooks/effort-estimate.md); no page yet says that nobody logs time, since no page here writes time to a tracker |
| 9 | Pages name a prototype command that does not exist. | A page names a wrapper or command only once it exists. | [The throwaway prototype](../playbooks/throwaway-prototype.md) names none |
| 10 | The playbook catalog names two playbooks with no wrapper; at least five have none. | No page states a count of unwrapped playbooks. A wrapper check, planned in slice B6 of M3, is to list the waiting pages by name. | [Playbook catalog](../playbooks/README.md) |
| 11 | Specs persist and change with the code; a spec is frozen once written. | Both, in turn. A spec changes by dated entries while its work is built, and is kept as written once the work ships. | [Decision 0016](0016-a-spec-lives-in-its-plan.md) |

### Deliberate departures from the ported pages

| What the ported pages did | What this workspace does | Why |
|---|---|---|
| A worker-tier session reviews a changed instruction page, and a hook only warns when the commit names no review. | A driver-tier session reviews it and writes a record, and the commit is refused without a trailer naming that record or a listed reason. | A trailer that is only checked for presence lets anything pass, and a review is judgment, which the [orchestration](../orchestration.md#stakes-raise-the-tier) rules put at the driver tier. See [the instruction review](../playbooks/instruction-review.md). |
| A merge proceeds while a slow third CI system is still running. | A pull request merges only after CI passes on Linux, macOS and Windows. | The contract requires all three. The rule is revisited only if this repository's CI shows the same wait. |
| The merge script merges from a throwaway local worktree. | `ws.py merge` merges on GitHub, after checking CI on the exact head commit. | The pre-push check refuses a local merge that brings machinery in, as [changing the machinery](../changing-the-machinery.md#the-path-for-a-machinery-change) says. |
| The kit never syncs the contract or the index. | The kit seeds them once into an instance. | An instance's checks read both from the start; see [decision 0007](0007-the-kit.md). |
| Spec-driven work, and one folder per large piece of work, belong to the product lane. | Every change that climbs the size gate's ladder follows the spec process, and any work past the threshold gets its folder, whatever its lane. | The gate and the size of the work, not the lane, decide; see decisions [0016](0016-a-spec-lives-in-its-plan.md) and [0017](0017-one-folder-per-large-piece-of-work.md). |
| An unattended run moves the pin itself, at its end. | The pin moves after a person merges the run's branch. | A pin must point at the code repository's default branch; see [decision 0018](0018-unattended-runs-write-only-to-a-branch.md). |
| A decision record carries `status`, `date` and `deciders`, three statuses, and consequences split into positive, accepted negative and neutral. Amendments link separate records. | A record also carries `kind` and `last-reviewed`, keeps a fourth status, `rejected`, and states its costs under "What it gave up". An amendment is a dated paragraph in the record itself. | Every page here names its kind and review date. A rejected proposal stays on record so it is not reopened blindly. The costs are what a later reader weighs; the gains restate the decision. One file per decision keeps its history in one place. See the [decision record template](../templates/decision-record.md). |

## What it gave up

- **One side of each pair is dropped.** A team used to the dropped side must relearn it here.
- **Some choices wait.** The reviewer limit has no page until M4, so nothing here enforces it yet.

## Options rejected

- **Keep both sides where they are.** Each disagreement would stay for a reader or an agent to trip on.
- **Pick silently, page by page.** The choice would be scattered, and a later port could undo it without knowing.
