---
last-reviewed: 2026-11-16
status: draft
---

# M2, port what the work workspace learned: hand-off plan

The plan for the second milestone: bring the features that proved themselves in the maintainer's private work workspace into this one, made generic. Building sessions work from it; the maintainer approves it. It follows the [hand-off plan template](../templates/hand-off-plan.md).

**In short:** the maintainer's work workspace has grown features this one lacks, most of them for running several agent sessions at once. This plan ports six groups of them, in order of value. It also lists what waits for later and what stays behind, with the reason for each.

## Key points

- **Nothing private crosses over.** The source workspace's name, team, products and systems never appear here; the `deny_list` check refuses them. Each feature is rebuilt from its idea against this repository's invented example, never copied. A builder finds each feature's source files in a private map at `~/.config/agent-ready-workspace/port-sources.md`, next to the deny list.
- **Slice 1 closes a gap this repository already admits.** [Changing the machinery](../changing-the-machinery.md) says a hook refusing a direct push of machinery to main "is planned". The work workspace has one.
- **Slice 2 fixes a failure seen on 2026-11-16.** A second session's browser call failed with "Browser is already in use". The work workspace solved it by giving each session its own browser profile.
- **Slice 4 needs a new decision record.** The writing-session lease refuses an edit before it happens. [Decision 0002](../decisions/0002-hooks-remind-the-commit-enforces.md) holds that hooks remind and the commit enforces. The record says why the lease is an exception, or the slice drops the refusal.
- **Every slice runs at the driver tier.** Each one changes a gate, the engine or the hook wiring.
- **Slice 6 is the costly one.** Two new playbooks each need a recorded eval run, at 40 or more trials per arm. It comes last so that one batched run covers both.
- **Agents push branches and open draft pull requests here, and merge once CI passes on all three systems.** That is this repository's standing rule.

## Settled decisions

The maintainer, 2026-11-16:

- "The workspace is supposed to have rules for using multiple playwright browsers. Check [the work workspace]. This is one of the many features I wanted moved to the workspace."
- "First write the porting plan."
- "You'll have to dig into the workspace for possible features. I'm constantly modifying it so I don't have a particular list."

Carried from M1, 2026-11-15:

- "Do not write on any system other people can see, and put nothing private in the public repository."
- "Make sure the plan is written such that I can use the workspace itself to implement the plan."
- The second agent tool is Codex CLI.
- An eval result counts at 40 or more trials per arm.

## Goal

Each ported feature works on its own in this repository. It has cases that fail without it, it runs under both Claude Code and Codex CLI wherever the tool offers the event, and it passes CI on Linux, macOS and Windows.

## Non-goals

- No feature that only makes sense for the source team's products, issue tracker, cloud or local test setup. See "Staying behind".
- No change to the meaning of an existing part, except where a slice names it.
- No third-party packages. The engine stays Python standard library only. A feature that cannot be built that way moves to "Later".
- No re-sync with the source workspace after this milestone. It keeps changing; a later milestone takes a new survey.

## Why this needs a plan

It fails all four size-gate conditions: it spans more than a day, it changes several gates, it touches the engine and both tools' wiring, and a mistake in a hook can lock a session out.

## Slices

| Order | Slice | Work | Tier | Done when |
|---|---|---|---|---|
| 1 | Machinery push gate | A pre-push check that refuses a push to main carrying a machinery commit whose CI run did not pass on all three systems. It reads CI status through `gh` when installed, and otherwise refuses with a message. | driver | Criteria 1–2 |
| 2 | One browser per session | Run the browser tool from the workspace's own config, pinned to an exact version with `--isolated`, for Claude Code and Codex CLI. Turn off the plugin that starts it without the flag. A check fails when the plugin is on or the flag is missing. Document that an isolated browser forgets logins when the session ends. | driver | Criteria 3–4 |
| 3 | Session-start notices | A new `session-start` event in the engine and both adapters. Two hooks on it: list pages past their review date, and warn when a pinned code repository is behind its upstream. Add a check that a staged pin is on its upstream default branch ([decision 0001](../decisions/0001-pin-code-repositories.md)). | driver | Criteria 5–7 |
| 4 | Writing-session lease | The first live session to edit the main working copy keeps it; any other live session is refused there and works in a worktree. At session start the main working copy fast-forwards to its upstream if it has no edits. Decision record 0004 first. | driver | Criteria 8–9 |
| 5 | Doc checks | `line_cites`: a line a commit adds to a doc may not cite a file by line number. `in_short`: a plan, decision or milestone page opens with an **In short** line. A `before-edit` hook that shows the agent the path-scoped rule pages whose `applies-to` patterns match the file it is editing. | driver | Criteria 10–12 |
| 6 | Playbooks | Port a red-team playbook and a diagnose playbook, with eval cases. One batched eval run. | driver | Criterion 13 |

Order rationale: slice 1 first, because every later slice is machinery and should reach main through the gate. Slice 3 comes before slice 4, because the catch-up at session start uses the new event. Slice 6 is last for cost.

## Success criteria

1. A push to main with a machinery commit and no passing three-system CI run for it is refused. The refusal names the commit and the missing systems. (V1)
2. The same push is allowed once the run has passed. Docs-only pushes are never checked. (V1)
3. `ws.py check` fails when `.claude/settings.json` enables the browser plugin, or when the workspace's browser server lacks `--isolated` or an exact version, for either tool. (V2)
4. Two copies of the configured browser server run at once, each navigates to `about:blank`, and both return the page. (V3)
5. A `session-start` event lists every page past its review date, and prints nothing when none is. (V2)
6. A `session-start` event warns when a pinned repository is behind its upstream, and stays quiet when it is current or offline. (V2)
7. A commit that stages a pin not on its upstream default branch fails. (V2)
8. With a live lease held by another session, an edit to a tracked file in the main working copy is refused, and the message names the worktree command. A stale lease, whose process has exited, is taken over. (V2)
9. At session start, a main working copy with no edits fast-forwards; one with edits is left alone and the session is told. (V2)
10. A commit adding a line-number citation to a doc fails; existing citations do not. (V2)
11. A plan, decision or milestone page without an **In short** line near its top fails. (V2)
12. Editing a file matched by a rule page's `applies-to` pattern returns that page's text to the agent; any other file returns nothing. (V2)
13. Each new playbook's recorded eval run shows its guided arm beating the two-line arm, pooled, at 40 or more trials per arm. A losing playbook is cut, not tuned. (V4)
14. No file in the repository holds a deny-listed term. (V2)
15. CI passes on Linux, macOS and Windows for every slice's pull request. (V5)

## Verification

- **V1:** `python3 -m unittest tests.test_push_gate -b` passes, with a fake CI status source covering pass, fail, missing and `gh` absent.
- **V2:** `python3 ws.py selftest`, `python3 ws.py check` and `python3 -m unittest discover -b tests` all exit 0, and each new part has cases that fail with its fix removed.
- **V3:** a test that starts two copies of the configured server command and drives both through an MCP `initialize` and `browser_navigate`. It skips with a printed reason when no browser is installed, which CI records.
- **V4:** `evals/run.py` records under `evals/runs/`, and `python3 ws.py check` passes `eval_record`.
- **V5:** `gh pr checks` on each pull request shows the three systems green.

## Recovery

Halt and report. Do not work around a failing case or loosen a check to pass. If a hook locks the session out, stop; the maintainer repairs it from a terminal, per [changing the machinery](../changing-the-machinery.md#traps).

## Stop rule

Stop the plan and report when any of these happens:

- A slice needs a third-party package.
- A feature cannot be made generic without a private fact.
- A slice goes past two fix rounds on the same failure.

## Limits

- Each slice runs on its own branch, `m2/slice-N`.
- Agents push the branch, open a draft pull request, and merge once CI is green on all three systems.
- No unattended runs.

## Records this plan must leave

- Decision record 0004, the writing-session lease (slice 4). Another one if slice 3's new event changes how a hook may answer.
- A report per slice under "Results", with each claim marked verified or inferred.
- `docs/milestones/m2.md` at the close, and entries in `CHANGELOG.md` and `EVIDENCE.md`.
- Question-log rows for anything a builder had to ask.

## Later

Worth porting, but not in this milestone:

- **Review mark before a pull request.** Refuse to open a pull request for a commit no recorded review covered. It needs a full-review playbook first, which is a third eval run.
- **Reverted-fix detector.** Flag a removed line whose history points at a fix commit.
- **Navigation eval.** Ask a cold session routing questions and score whether it names the right page.
- **Model-mix report.** How much work ran on each tier, from the agent's own logs.
- **Fresh-clone check.** Clone into an empty folder, follow only the README, and check the result works.
- **Backticked names resolve.** Extend `aliases` from the index to every doc.
- **Linked-change reminder.** After an edit, name the other layers the index lists as changing with that path.
- **Warning delta.** Compare build warnings between two commits, for touched files only.

## Staying behind

| Feature | Why it stays |
|---|---|
| Ask before the browser leaves the local test setup | Tied to the source team's local setup; on any public site it prompts every time. |
| Gate on the legacy app | `shelved` already covers it. |
| Refuse bulk staging | `no_stage_all` and `edit_ledger` already cover it. |
| Require a tier on hand-offs | `handoff_tier` already covers it. |
| Refuse edits to personal notes folders | `shelved` covers it with a folder list. |
| Twin-file drift, closed-ticket defects, migration audit, side-by-side test setups, commit-link rewriting, architecture lookup, code maps, local CI mirror, issue-tracker and theme playbooks | Each depends on the source team's code, tracker or cloud. |

## Red team

Not yet run. A fresh session gets this plan and the private source map, never the author's reasoning.

| # | Finding | Verdict | Action |
|---|---|---|---|

## Approval

Not yet approved.

## Changes after approval

## Results
