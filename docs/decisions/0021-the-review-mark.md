---
kind: decision
status: accepted
date: 2026-11-28
deciders: the maintainer, through M4's approved plan
last-reviewed: 2026-11-28
---

# 0021: M4 builds its own review mark, takes six ideas from two published checks with credit, and stores the mark in the branch it reviews

**In short:** two published checks were tested against the review mark's criteria: AI-DLC's `attest` and Anthropic's `agent-approval-check`. Neither meets every criterion of slice L2 or L3, so the stop rule of M4's plan does not fire, and M4 builds the mark. It takes six ideas from them, credited below. The mark, its completion record and its dispatch records are files under `docs/records/reviews/`, committed on the branch they review.

## Context

M4's plan, `docs/plans/m4-fail-closed-guards-review-loop-and-evals.md`, builds a review mark: a record that a review completed on one commit's content. Before building it, slice L0 tests two existing checks against criteria 35 to 40. If one meets every criterion of a slice, that slice takes its design. No third-party package may join the engine, the parts or the tests CI runs.

Both checks exist. They were found and read on 2026-11-28:

- **`attest`** is the `aidlc attest` command of AWS's AI-Driven Development Life Cycle workflows. A reviewer's approval writes a receipt and an evidence file into the repository: the evidence lists each reviewed path's content hash, and the receipt holds the evidence's hash. `aidlc attest resolve` then reads a commit or a range and classes each changed path. A path is `verified` when its content matches what a receipt approved, and `drifted`, `unattested`, `unverifiable` or `indeterminate` otherwise. The last two fail closed. Each report states its trust level: whether the receipts it relied on came from the change itself, from a ref the verifier named, or from signed commits.
- **`agent-approval-check`** is a GitHub Action in Anthropic's Claude Code Action. On a pull request with agent commits, it counts approvals from people with write access: approving reviews, and `/approve <sha>` comments that name the current head. It posts a commit status, `success` at the required count and `pending` below it, which branch protection can require. Its workflow runs from the base branch, so a pull request cannot edit the check that judges it.

How each was tested:

- **`agent-approval-check` was run.** Its decision function was run offline against eight cases built from the commits of a scratch git repository. Its three libraries were replaced by stand-ins, and a stand-in client took the place of every GitHub call, so nothing reached the network. The results are what the table below cites as "the run".
- **`attest` was read, not run. This departs from the plan,** which asks L0 to test both checks in a scratch repository. `attest` imports 50 of its project's files, and 134 with the logging command that writes its receipts. Two of them import a module only the Bun runtime has, and the machine L0 ran on does not have Bun. Installing a runtime to run code too large to read first was ruled out. What the table says of `attest` comes from its source, its reference chapter and its test suite, so each such line is inferred.

The run, its cases and the facts about each agent tool's sessions are in that plan's "Results", under the entry for L0.

## Decision

### The stop rule does not fire

L2 answers to criteria 35 and 36, and L3 to criteria 37 to 40. Neither check meets criterion 35 or 36, so neither holds L2. Neither meets all of criteria 37 to 40, so neither holds L3. M4 builds both slices, as the plan says.

### What each meets, what M4 takes and what it builds

Each cell says whether the check meets the criterion, and the behavior that decides it.

| Criterion | `attest` | `agent-approval-check` | M4 takes, with credit | M4 builds |
|---|---|---|---|---|
| 35. A dimension counts as complete only on the reviewer's own output. | Does not meet. A receipt records the verdict passed to its logging command, after a review section is appended to the reviewed file. The criterion asks for the reviewer session's own output. | Does not meet. It counts approvals and reads no review content: the run counted only approving reviews and `/approve` comments. | Nothing. | `review collect`, reading each reviewer's transcript through one adapter per agent tool. |
| 36. A delta round re-checks rows marked fixed; no whole-branch pass, no mark. | Does not meet. It classes a path changed since its review as `drifted`; it keeps no review rounds or finding rows. | Does not meet. It keeps no review rounds or finding rows. | Nothing. | The re-check of fixed rows, and the whole-branch pass. |
| 37. `review mark` refuses in each case L3 lists. | Meets in part. It fails closed on a path it cannot bind (`unverifiable`) or cannot order (`indeterminate`), and its gate exits non-zero. It keeps no finding rows or declines. | Meets in part. It fails closed on any unhandled error, and on a pull request whose commits it cannot list in full. It keeps no finding rows. | **Fail closed on whatever cannot be bound**, from `attest`. | Every refusal L3 lists. |
| 38. A forged mark reads `none`; the guards refuse writes to the stores. | Meets in part. A changed evidence byte can only fail a path, never verify one. A receipt the change wrote itself is reported as self-attested, and a verifier can read receipts from a ref the change cannot move. Its threat model states that whoever can write the repository can write a receipt that verifies. | Meets in part. In the run, an `/approve` that named an earlier head did not count, nor did one from an agent's login or from a user without write access. Two approving reviews counted at the head of a code commit pushed after them: a review names no head, and staleness is left to a GitHub branch setting. | **A vouch names the head it vouches for, and counts at no other**, from `agent-approval-check`. **A report states the basis it rests on**, from `attest`: slice L3's pages are to say that the mark is not signed, and what it does not stop. | The reader that gives a forged mark `none`, and the guards on the stores. |
| 39. `review status` gives four answers; a record-only commit keeps the mark. | Meets in part. It binds to content, not to ancestry, so a squashed or rebased change still verifies. A change cannot declare its own exclusions: which harness folders are excluded is read from the range's base. | Does not meet. In the run, a commit that changed only a record file, after two `/approve` comments at the earlier head, took the count to zero, since each comment names a head. | **Bind the mark to content, not to a commit**, from `attest`: the fingerprint is over the branch's patch, and `rebased` reads the patch id. **A change cannot widen what is left out of judgment**, from `attest`: the record paths are fixed by the base's code. | `review status` and its four answers. |
| 40. The gate at pull-request creation, publish and merge, and in CI. | Meets in part. Its gate flags make it a step a pipeline can run. It does not act on a pull request. | Meets in part. In the run, a code commit pushed after two `/approve` comments sent the status back to `pending`, which blocks a merge where the status is required. It does not judge a pull request's creation or draft state, and reads no transcripts. | **The check is run from the base, not from the change**, from `agent-approval-check`: L3's CI step, `ws.py ready` and `ws.py merge` run the check's code from the base commit. | `review_gate`, `ws.py ready`, and the CI step. |

### Where the mark is stored

- **In the repository, under `docs/records/reviews/`.** The dispatch records, the completion records, the findings rows the collector writes and the mark's store all live there, as L1 and L3 say.
- **On the branch it reviews.** A review's records are committed on that branch and reach main with its pull request. CI reads them at the pull request's head, and `review status` reads them in the same clone.
- **Keyed by the reviewed tip and the branch's patch id.** The fingerprint is taken over the branch's patch against its merge base, leaving out the record paths. A commit after the mark that changes only record paths keeps it.
- **Not on the git host.** The mark is not a commit status, a check run or a review. Reading or writing those needs a git-host provider, which is M8.
- **Not on a separate ref, and not in git notes.** See "Options rejected".

## What it gave up

- **M4 writes and tests the whole mark itself.** No outside test suite stands behind it.
- **A mark in the branch can be written by anyone who can write the branch.** The guards refuse an agent's writes to the stores, and a mark with no completion record behind it reads `none`. A person editing files by hand can still forge one, and CI cannot read the transcripts. Slice L3 adds both to the README's limits.
- **No trust root outside the change.** Neither a protected ref nor a signature backs the mark in M4, so it shows that a review ran, not who ran it.

## Options rejected

- **Take `agent-approval-check` as the gate.** It does not meet criteria 35 and 36, since it counts approvals rather than reading review output. It would also need a workflow under `.github/workflows/`, three third-party libraries in CI and statuses on the git host, which the plan's non-goals and limits exclude.
- **Take `attest` as the mark.** It does not meet criteria 35 and 36. Running it needs the Bun runtime and its own record model of intents, units and stages, and no third-party package may join the engine.
- **Port `attest`'s code.** Its licence allows it, but the code reads its own record model, which M4 does not keep. The ideas carry over; the files would not.
- **Gate by the committer's email.** Criterion 40 gates by the paths a range changes, whoever commits. An email names no path, and in the run a commit made under a person's email was read as "No agent activity".
- **Store the mark as a commit status on the git host.** It needs a git-host provider, which is M8. In M4, agents use the maintainer's own sign-in, so a status would not show that a review ran rather than that an agent posted it.
- **Keep the records on a separate protected ref.** A protected ref binds only someone who cannot move it. In M4, agents use the maintainer's sign-in, so it binds nobody. It is worth reopening once agents have an identity of their own, which the plan defers to M10.
- **Store the mark in git notes.** Notes do not travel with an ordinary push, and a pull request does not show them, so CI and the gate could not read the mark at the pull request's head.
- **Sign the mark.** The plan's non-goals rule out a signature in M4.

## Credit

The review mark takes six ideas from two published sources. No code was copied from either.

- **AI-Driven Development Life Cycle workflows**, by AWS Labs, MIT No Attribution licence: [`awslabs/aidlc-workflows` at commit `c903d59`](https://github.com/awslabs/aidlc-workflows/tree/c903d599fa49a2d747048d051351b1630fd4389e), its `aidlc attest` command and the reference chapter "Commit Provenance". Credited for: fail closed on whatever cannot be bound; bind to content rather than to a commit; let the base, not the change, decide what is left out of judgment; and make every report state the basis it rests on.
- **Claude Code Action**, by Anthropic, MIT licence: [`anthropics/claude-code-action` at commit `4411a9e`](https://github.com/anthropics/claude-code-action/tree/4411a9e9b0283becf4b924f7bce360fd7756c78c/agent-approval-check), its `agent-approval-check` action. Credited for: a vouch names the head it vouches for and counts at no other; and the check that judges a change runs from the base, so the change cannot edit it.
