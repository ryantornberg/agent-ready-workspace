---
last-reviewed: 2026-11-16
status: approved
---

# M2, port what the work workspace learned: hand-off plan

The plan for the second milestone: bring the features that proved themselves in the maintainer's private work workspace into this one, made generic. Building sessions work from it; the maintainer approves it. It follows the [hand-off plan template](../templates/hand-off-plan.md).

**In short:** the maintainer's work workspace has grown features this one lacks, most of them for running several agent sessions at once. This plan first clears the eval harness so engine changes stop invalidating the eval, then ports six groups of features in order of value. It lists what waits for later and what stays behind, with the reason for each. This is the third draft. The maintainer approved the second on 2026-11-16, with the changes listed under "Changes after approval"; the third applies the second red team's decided actions to the body.

## Key points

- **Slice 0 pays for one eval re-recording up front.** The eval hash covers the engine's part loader, so any engine change makes every eval record stale. Slice 0 takes the loader out of the hash, fixes the Windows path leak, and re-records the three cases at 15 runs per arm in each: 135 agent runs on the small model, the same design as M1. After it, slices 3–5 merge without new eval runs.
- **A second recording comes in slice 6**, the closing slice, for the queued edits to `AGENTS.md` and `INDEX.md`. Until then, M2's new rules live in `docs/` pages and stay out of the five files the guided arm reads, and each new hook's message links its page. New playbooks wait for M3, which generalizes the eval harness first.
- **GitHub now refuses a merge to main unless all five CI jobs pass.** The maintainer turned the branch rule on 2026-11-16. It does not bind the owner, so slice 1 covers what it cannot see: a machinery commit pushed straight to main, and `gh pr merge --admin`.
- **Slice 3 changes the hook contract.** Hooks today are pure functions of their event. The lease, the notices and the rule-page hook need read access to files, git and session identity. Decision record 0004 sets the new contract before any hook uses it. The event carries the working copy and the path within it, so a worktree edit is placed, ledgered and leased correctly.
- **The lease must work for both tools, on all three systems, and inside worktrees.** Today an edit inside a linked worktree slips past `shelved`. Slice 3 fixes that first.
- **Nothing private crosses over.** The source workspace's name, team, products and systems never appear here; the `deny_list` check refuses them. Each feature is rebuilt from its idea, never copied. Builders never open the work workspace's files. Before slice 2, a walled reader session, which builds nothing, opens them and writes a generic description of each feature: no code, no private names, nothing copied. Builders work only from those descriptions.
- **Every slice runs at the driver tier, in a separate working copy.** Each one changes a gate, the engine, the eval or the hook wiring. Until slice 3 fixes path placement, that copy sits outside the repository folder; see "Limits".
- **Round two's decided actions are part of the approved plan.** This third draft applies them. Their finding numbers are cited in the slices and criteria they changed.

## Settled decisions

The maintainer, 2026-11-16:

- "The workspace is supposed to have rules for using multiple playwright browsers. Check [the work workspace]. This is one of the many features I wanted moved to the workspace."
- "First write the porting plan."
- "You'll have to dig into the workspace for possible features. I'm constantly modifying it so I don't have a particular list."
- Turned on GitHub's branch rule for main: all five CI jobs required, direct pushes by the owner still allowed, force pushes and deletion blocked.
- Turned off "require branches to be up to date" the same day, so each doc push to main does not send every open pull request through a catch-up merge and a fresh CI run. CI on main catches a bad combination after the merge.
- Asked how to pay for the eval re-recording: "We're fine in my claude subscription right now."

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
- No third-party packages in the engine, the parts or the tests that CI runs. The browser server in slice 2 is a tool the agent runs, not part of the engine, and its test is opt-in.
- No edit to the five files the eval's guided arm reads (`AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/playbooks/fix-a-bug.md`, `docs/definition-of-done.md`) before slice 6. A slice that needs one records it under "Changes after approval" for slice 6's recording.
- No new playbook. Writing one needs per-case arms, a bare-only baseline and new graders, which M3 builds (round two, finding 1).
- No re-sync with the source workspace after this milestone. A later milestone takes a new survey.

## Why this needs a plan

It fails two size-gate conditions: it is more than one screen of diff, and it is more than a day of work. It is in one repository, and most of it reverts cleanly, but a broken hook can lock a session out.

## Slices

| Order | Slice | Work | Tier | Done when |
|---|---|---|---|---|
| 0 | Eval harness, re-recorded | `grade.py` loads the graded hook's file itself, so `wslib/parts.py` leaves the eval hash: only the hook's own file and the harness count. `run.py` and `grade.py` import nothing from `wslib/`. `leaks()` catches a Windows path written with backslashes. `eval_record` refuses a pooled comparison with fewer than 40 runs in an arm. Git ignores `.claude/worktrees/`. Re-record the three cases at 15 runs per arm in each, 135 runs on the small model, as M1 did. | driver | Criteria 1–2, 27–28 |
| 1 | Direct-push and admin-merge refusals | The machinery paths become one list in `workspace.json`, and a test holds the machinery page's table to it. A pre-push hook refuses a direct push to main whose new commits change a path on that list. A shell hook refuses `gh pr merge --admin`. Machinery reaches main only through a pull request, where GitHub's branch rule requires CI. `enforce_admins` stays off, so direct doc pushes still work. Needs no network. | driver | Criteria 3–4, 33–34 |
| — | Walled reader | A session that builds nothing opens the work workspace's files, using the private source map, which only it reads. It writes a generic description of each feature slices 2–5 port, with no code, no private names and nothing copied, to a private file beside the source map, outside every repository. It also names the five generic features round two found unplaced, and proposes Later or Staying behind for each. Builders work only from that file. | driver | Criterion 29 |
| 2 | One browser per session | Run the browser server from the workspace's own config, pinned to an exact version with `--isolated`, for Claude Code (`.mcp.json`) and for Codex CLI (its project config, read line by line, since Python 3.9 has no TOML parser). The project settings set the browser plugin to `false`. A `browser_isolation` check enforces both. The page names the Windows config and Chrome. Add the new config files to the machinery list. Document that an isolated browser forgets logins at session end. The risk it removes is two sessions sharing one folder's browser profile. | driver | Criteria 5–7, 35 |
| 3 | Hook contract, session start and session end | Decision record 0004: what a hook may read (files, git, session identity, tool name) and how cases supply it. The event carries the working copy and the path within it, and every hook places a path relative to its own working copy. No engine version bump unless a manifest key changes meaning. `session-start` and `session-end` events in both adapters, with a recorded Codex run of each and replay tests. Hooks on `session-start`: pages past their review date, and a pinned repository behind its upstream. A check that a staged pin is on its upstream default branch. | driver | Criteria 8–13, 30, 36 |
| 4 | Writing-session lease | Decision record 0005: concurrent sessions and the edit ledger. The first live session to edit the main working copy keeps it; any other live session is refused there and pointed at a worktree. Identity and liveness per tool and per system; on Windows, `os.kill(pid, 0)` is not a liveness probe. Release at session end. Takeover only of a dead or idle lease past a minimum age, and only when the main copy has no tracked change and no unpushed commit. At session start, a main working copy with no tracked change fast-forwards, unless another live session holds the lease. | driver | Criteria 14–18, 31 |
| 5 | Doc checks | The snapshot gains the lines a commit adds per file. `line_cites`: an added doc line may not cite a file by line number. `in_short`: a plan, decision or milestone page has an **In short** line within 15 lines of its title. A `before-edit` hook returns the text of every rule page whose `applies-to` front matter matches the edited path. Add the missing **In short** line to `docs/milestones/m1.md` and to the milestone record template, and one real rule page. | driver | Criteria 19–22 |
| 6 | Closing: contract, index and one recording | The edits queued under "Changes after approval": index entries for the new parts and the browser rule, and any contract line they need. Then one recording of the three cases, 135 runs, as slice 0 did. | driver | Criterion 37 |

Order rationale: slice 0 first, so engine changes after it don't stale the eval. Slice 1 next, so later machinery cannot reach main by a direct push. Slice 3 before 4 and 5, because both use its contract, its events and its worktree fix. Slice 6 last, so one recording covers every contract and index edit.

## Success criteria

1. `python3 ws.py check --phase ci` passes after the re-recording. Every record holds 15 runs per arm, and `eval_record` fails a pooled comparison with fewer than 40 runs in any arm. (V1, V4)
2. In a scratch copy, adding an entry to the engine's event list and editing `wslib/snapshot.py` leaves every eval record current, and neither `run.py` nor `grade.py` imports anything from `wslib/`. (V1)
3. A direct push to main whose new commits change a machinery path is refused, and the refusal names the commit and the path. (V1)
4. A direct push of doc-only commits, and a push of any branch other than main, is allowed. (V1)
5. `ws.py check` fails when the project settings do not set the browser plugin to `false`, when the workspace's browser server lacks `--isolated`, or when its version is not exact. It fails for the Claude Code config and for the Codex CLI config alike. (V2)
6. With the opt-in browser test on, two copies of the configured server each navigate to `about:blank` and both return the page. (V3)
7. With the opt-in browser test on, two copies without `--isolated` collide, and the second reports the profile lock. (V3)
8. Decision record 0004 exists. A test fails when a part reaches files, git, the environment or a process other than through the access 0004 defines. (V1)
9. For a path inside a linked worktree, `shelved` gives the same answer as for the same path in the main working copy. (V2)
10. A `session-start` event lists every page past its review date, and prints nothing when none is. (V2)
11. A `session-start` event warns when a pinned fixture repository is behind its upstream, and stays quiet when it is current or unreachable. (V2)
12. A commit that stages a pin not on its fixture upstream's default branch fails. When the upstream cannot be reached, the check warns and passes, locally and in CI; it fails only on a reachable upstream whose default branch lacks the pin. (V2)
13. Recorded Codex CLI runs deliver `session-start` and `session-end`, with the fields decision 0005 uses for identity and liveness, and replay tests of both pass in CI. (V1)
14. With a live lease held by another session, an edit to a tracked file in the main working copy is refused, and the message names the worktree command and links the lease's page. (V2)
15. A lease is taken over only when its holder is dead or idle past the limit decision 0005 sets, the lease is older than its minimum age, and the main copy has no tracked change and no unpushed commit. Each of those conditions has a case that refuses the takeover. Liveness is tested on all three systems. (V2, V5)
16. Each tool's identity is covered: a Claude Code payload and a Codex CLI payload each take, keep and release a lease in the cases. (V2)
17. At session start, a main working copy with no tracked change fast-forwards. One with tracked edits, or one whose lease another live session holds, is left alone, and the session is told why. (V2)
18. On `session-end`, from either tool, the holder's lease is released. (V2)
19. A commit adding a line-number citation to a doc fails; a citation already present does not. (V2)
20. A plan, decision or milestone page with no **In short** line within 15 lines of its title fails. `docs/milestones/m1.md` passes, and the milestone record template's skeleton has the line. (V2)
21. Editing a file matched by the real rule page's `applies-to` pattern returns that page's text, from the main working copy and from a linked worktree. Any other file returns nothing. (V2)
22. Every new part's cases fail against a stub part that does nothing. (V6)
23. Moved to M3 with the playbooks (round two, findings 1 and 2).
24. Moved to M3 with the playbooks (round two, findings 1 and 15).
25. No file in the repository holds a deny-listed term. (V2)
26. CI passes on all five jobs for every slice's pull request. (V5)
27. `leaks()` finds a Windows path written with backslashes, in a test that runs on all three systems. (V1, V5)
28. Git ignores `.claude/worktrees/`. (V1)
29. Before slice 2 starts, the private descriptions file holds one entry per feature slices 2–5 port, and holds no code block. It names the five features round two found unplaced, each with a proposed place, and "Later" or "Staying behind" here lists them. Each builder's report says it read no file of the work workspace. (V1)
30. An edit inside a linked worktree is recorded in that worktree's ledger, and placed relative to that worktree by every hook. (V2)
31. With a live lease held by another session, a non-holder's edit inside a linked worktree is allowed. (V2)
32. Every refusal or reminder a new hook gives names the docs page that explains it. (V1)
33. `gh pr merge --admin`, in any form `no_stage_all`'s parser follows, is refused, and `gh pr merge` without it is allowed. (V2)
34. A test fails when the machinery page's table and the machinery list in `workspace.json` differ. (V1)
35. A recorded Claude Code session in this repository lists the project's browser tools. (V3)
36. The `session-start` and `session-end` events each have a replay test from a recorded Claude Code run as well. (V1)
37. Slice 6's recording passes the gate and loses no comparison slice 0's recording won. (V4)

## Verification

- **V1:** `python3 -m unittest discover -b tests` passes, including the new tests named by each criterion: the scratch-copy event test, the push-hook tests against a temporary repository, and the Codex replay test.
- **V2:** `python3 ws.py selftest`, `python3 ws.py check` and `python3 -m unittest discover -b tests` all exit 0.
- **V3:** `WS_BROWSER_TEST=1 python3 -m unittest tests.test_browser -b` passes on the maintainer's machine, with Node installed. Its output, and criterion 35's recorded session, go into the slice's report. CI does not run it.
- **V4:** `evals/run.py` writes the records under `evals/runs/`; `python3 evals/pool.py` prints each comparison; `python3 ws.py check --phase ci` passes `eval_record`.
- **V5:** `gh pr checks <number>` shows all five jobs passing.
- **V6:** `python3 -m unittest tests.test_cases_bite -b` passes. It runs each new part's cases against a stub that allows everything and finds nothing, and expects at least one case to fail.

## Recovery

Halt and report. Do not work around a failing case or loosen a check to pass. If a hook locks the session out, stop; the maintainer repairs it from a terminal, per [changing the machinery](../changing-the-machinery.md#traps).

## Stop rule

Stop the plan and report when any of these happens:

- The engine, a part or a CI test needs a third-party package.
- A feature cannot be made generic without a private fact.
- A slice goes past two fix rounds on the same failure.
- Slice 0's or slice 6's recording does not show the guided arm beating the two-line arm across the three cases, by a one-sided Fisher exact test at p < 0.05. Or it loses a comparison M1's recording won: guided against bare in any case, or guided against two-line in nightly-job or big-report. Losing means the guided arm passes every grader in no more runs than the other arm. Publish that result and stop.

## Limits

- Each slice is built in its own separate working copy, on its own branch, `m2/slice-N`. No builder checks out a branch in the main working copy.
- Slices 0 to 3 put that copy outside the repository folder, because until slice 3 fixes path placement, an edit in a worktree nested inside the repository gets past `shelved`. From slice 4 on, it goes under `.claude/worktrees/`.
- Eval-harness work is committed with `--no-verify` before the paid runs, as the [machinery page's trap](../changing-the-machinery.md#traps) describes.
- Agents push the branch, open a draft pull request, and merge once GitHub shows all five CI jobs passing.
- No unattended runs, except the eval recordings. After a usage limit, a person or session reruns the case with `run.py --resume`, which runs only the missing runs; nothing restarts on its own.
- Maintainer setup before slice 0: `gh auth status` passes, and the Claude Code CLI is signed in. Before slice 2: Node with `npx`. Before slice 3: Codex CLI signed in, for the recorded run.

## Records this plan must leave

- Decision records 0004 (hook contract) and 0005 (concurrent sessions and the edit ledger).
- A report per slice under "Results", with each claim marked verified or inferred.
- `docs/milestones/m2.md`, written as the slices finish and closed at sign-off, plus entries in `CHANGELOG.md` and `EVIDENCE.md`.
- Question-log rows for anything a builder had to ask.

## Later

Worth porting, but not in this milestone:

- **Review mark before a pull request.** Refuse to open a pull request for a commit no recorded review covered. Needs a full-review playbook first, which is another eval recording.
- **Playbooks for red-team and diagnose tasks, and the eval harness they need** (per-case arms, a bare-only baseline, graders for their output, a per-playbook Fisher test). M3, by round two's findings 1 and 2.
- **Grill and spec playbooks.** The [size gate's ladder](../size-the-work.md#the-ladder) lists both as not written yet.
- **Other playbooks:** test-first development, impact analysis, reuse check, instructions check, docs audit, prompt review, review feedback, estimation. Each needs a baseline run showing the model failing first.
- **A per-session opt-in for shelved folders.** Lets one session edit a shelved folder on the person's say-so.
- **Lease check at push.** Refuse a push from the main working copy by a session that does not hold the lease.
- **Reverted-fix detector.** Flag a removed line whose history points at a fix commit.
- **Navigation eval.** Ask a cold session routing questions and score whether it names the right page.
- **Model-mix report.** How much work ran on each tier, from the agent's own logs.
- **Fresh-clone check.** Clone into an empty folder, follow only the README, and check the result works.
- **Backticked names resolve.** Extend `aliases` from the index to every doc.
- **Doc coverage and diagram checks.** Every documentable unit has a page; every diagram's image matches its source.
- **Linked-change reminder.** After an edit, name the other layers the index lists as changing with that path.
- **Warning delta.** Compare build warnings between two commits, for touched files only.

Placed by the walled reader on 2026-11-16 (criterion 29). Round two's five come first:

- **Partial-access checkout of pinned repositories.** This repository has no real pinned repositories yet.
- **Playbooks to import a pinned repository, review architecture, build a prototype, and review an escaped defect.** Playbooks wait for M3's eval harness.
- **Refuse commands that discard uncommitted work.** A reset or checkout that throws away another session's edits. Needs slice 4's lease.
- **Lease check at commit.** Pairs with the lease check at push, above.
- **Draft-only pull requests.** Refuse opening a pull request that is not a draft; same hook as the review mark.
- **Commit subject format.** A check on the first line of a commit message.
- **Instructions-check reminder.** Ask that a commit changing guidance record its instructions check; comes with that playbook.
- **Secret scan.** Needs a third-party scanner, which the engine may not use.
- **Worktrees read pinned repositories from the main copy.** Matters once pinned repositories exist.
- **Session hand-off note.** Needs its own eval case.
- **Remove a session's worktree after its work lands.** A `session-end` reminder can do it after slice 4.

## Staying behind

| Feature | Why it stays |
|---|---|
| No agent edits in the main working copy at all | Slice 4 takes the other rule the source settled on: the first writing session keeps the main copy. |
| Ask before the browser leaves the local test setup | Tied to the source team's local setup; on any public site it prompts every time. |
| Refuse bulk staging | `no_stage_all` and `edit_ledger` already cover it. |
| Require a tier on hand-offs | `handoff_tier` already covers it. |
| Refuse edits to personal notes folders | `shelved` covers it with a folder list. |
| Status line | A personal display preference, not a rule. |
| No-regression eval mark at push | `eval_record` already refuses a stale or losing record at the commit and in CI. |
| Per-clone switches that turn checks off | A check here binds every clone of the repository. |
| Publishing docs to a team wiki | Depends on the source team's wiki. |
| Twin-file drift, closed-ticket defects, migration audit, side-by-side test setups, commit-link rewriting, architecture lookup, code maps, local CI mirror, issue-tracker, regression, theme and scaffolding playbooks | Each depends on the source team's code, tracker or cloud. |

## Red team

Round 1, 2026-11-16: a fresh session given the first draft, both repositories, the private source map and the deny list.

| # | Finding | Verdict | Action |
|---|---|---|---|
| 1 | The pre-push gate never fires: pull requests merge on GitHub, and main had no branch rule. | Accepted | The maintainer turned on GitHub's branch rule. Slice 1 narrowed to direct pushes. |
| 2 | Slices 3–5 stale every eval record, because the hash covers the loader; only slice 6 paid for a recording. | Accepted | New slice 0 takes the loader out of the hash and re-records once. Contract files frozen until slice 6. |
| 3 | Hooks are pure functions; the lease, notices and rule-page hook need files, git and session identity. | Accepted | Slice 3 delivers the contract with decision record 0004. |
| 4 | The lease had no identity or liveness design for Codex, or for Windows. | Accepted | Criteria 15–16, and the recorded Codex run in criterion 13. |
| 5 | Edits inside a linked worktree escape `shelved`; rule-page patterns would miss them too. | Accepted | Slice 3 fixes path placement; criteria 9 and 21. |
| 6 | Decision 0002 covers staging only; the lease is no exception to it. | Accepted | Key point rewritten; decision record 0005 covers concurrent sessions and the ledger. |
| 7 | The fast-forward can move files under a live lease holder; session-end release, idle takeover and the push-side check were unplaced. | Accepted | Criteria 15, 17, 18. Push-side check moved to Later. |
| 8 | The plugin is enabled in user settings, so a project file that merely omits it passes the check. | Accepted | Criterion 5 requires an explicit `false`. |
| 9 | The browser test passed on a skip, had no negative control, and ran `npx` inside the normal tests. | Accepted | Opt-in test, criteria 6–7, outside CI. |
| 10 | The browser server is a third-party package, which the stop rule banned. | Accepted | Ban narrowed to the engine, parts and CI tests. |
| 11 | The pooled gate lets strong old records carry a losing playbook. | Accepted | Criterion 23 requires a per-playbook Fisher test. |
| 12 | No grader fits a red-team or diagnose task, the two-line arm is a bug-fix baseline, and the baseline run was skipped. | Accepted | Slice 6 split into 6a and 6b; criterion 24. |
| 13 | `line_cites` needs added lines the snapshot lacks; `in_short` would fail `m1.md`; "near its top" was not checkable; no rule page exists. | Accepted | Slice 5 names each; criteria 19–21. |
| 14 | This repository has no submodules; the offline behaviour of the pin checks was unspecified. | Accepted | Fixture repositories; criteria 11–12 state offline behaviour. |
| 15 | Builders and other sessions would share one working copy. | Accepted | Limits: one worktree per slice, and the maintainer's setup steps. |
| 16 | Several source features were unplaced; the legacy-app gate's per-session opt-in was missed. | Accepted | Later and Staying behind extended. |
| 17 | Size-gate claim wrong; milestone record timing wrong; "fail with its fix removed" had no command. | Accepted | Corrected; V6 added. |
| 18 | No deny-listed term in the plan. | Noted | None. |

Round 2, 2026-11-16: a fresh session given the second draft and the same sources. The verdicts below are decided, and the third draft applied each action to the body. Finding 23's five features are placed by the walled reader, which can read the source; this plan's builders cannot.

| # | Finding | Verdict | Action |
|---|---|---|---|
| 1 | Slice 6 cannot run on the current harness: arms are global, there is no bare-only mode, a case cannot exist before its playbook, and no grader fits red-team or diagnose output. Its real cost is far above the stated one. | Accepted | Slice 6 leaves M2. M3 generalizes the eval harness and ports playbooks. M2 ends instead with one closing slice: the queued contract edits and one re-recording. |
| 2 | No command computes a per-playbook Fisher test. | Accepted | Moves to M3 with the playbooks. |
| 3 | Slice 0 read "40 or more trials per arm" as per case (about 360 runs). M1 pooled it across cases and met it at 15 per case (135 runs). | Accepted | 135 runs per recording, pooled, as M1 did. Slice 0 makes `eval_record` check the pooled 40 per arm, so criterion 1 has a command. |
| 4 | Placing worktree paths relative to the worktree breaks the edit ledger and blinds the lease. | Accepted | Decision 0004: the event carries the working copy and the path within it. New criterion: an edit in a worktree is recorded in that worktree's ledger. |
| 5 | Criterion 14 passes for a lease that refuses everything. | Accepted | Negative control: a non-holder's edit inside a linked worktree is allowed. |
| 6 | `.claude/worktrees/` is not git-ignored, so the main copy always looks dirty. | Accepted | Slice 0 ignores it. "Clean" means no tracked change. |
| 7 | Session-end release has no event; the Codex escape clause lets a builder declare a gap. Codex appears to offer both events. | Accepted | Slice 3 adds `session-end` too, for both tools, with a recorded Codex run. Escape clause dropped. |
| 8 | The Codex lease is tested only on hand-written payloads. | Accepted | The recorded Codex run must show the fields decision 0005 uses for identity and liveness. |
| 9 | Time-based idle takeover can hand a live session's edits to another. | Accepted | Takeover only when the main copy has no tracked change and no unpushed commit, plus a minimum age, as the source does. |
| 10 | The owner's sign-in merges past red CI with `gh pr merge --admin`; the texts overclaimed. | Accepted | `changing-the-machinery.md` reworded now. Slice 1 adds a shell-hook refusal of `--admin` merges. `enforce_admins` stays off, so direct doc pushes keep working. |
| 11 | The Codex half of slice 2 was hedged to nothing, and Python 3.9 has no TOML parser. | Accepted | Hedge dropped. A line-based check of the Codex config, no parser. |
| 12 | The browser criteria test the package, not the wiring; Windows and Chrome are unaddressed; separate worktrees already get separate profiles. | Accepted | Criterion: a recorded Claude Code session lists the project's browser tools. Windows config and Chrome named. The risk restated as sessions sharing one folder. |
| 13 | `run.py` imports the snapshot, which slice 5 changes, so the eval can still go stale. | Accepted | Slice 0 removes that dependency as well; criterion 2 covers the snapshot. |
| 14 | The pin check fails closed in CI on an upstream it cannot reach. | Accepted | Warn when unreachable; fail only on a reachable upstream whose default branch lacks the pin. |
| 15 | Criteria 8, 13 and 24 need a person to judge. | Accepted | 8 becomes a test; 13 loses its escape clause; 24 leaves with slice 6. |
| 16 | The milestone template has no In short line, so `m2.md` would fail `in_short`. | Accepted | Slice 5 adds it to the template. |
| 17 | Freezing `INDEX.md` leaves it stale all milestone, with no page an agent finds for the browser rule. | Accepted | The closing slice updates the index and contract. Until then, each hook's refusal message links its doc page. |
| 18 | The engine version bump has no reason and needs a third working copy. | Accepted | No bump unless a manifest key changes meaning. |
| 19 | On Windows, `os.kill(pid, 0)` is not a liveness probe. | Accepted | Named in decision 0005. |
| 20 | The machinery path list is prose, and slice 1's hook needs one it can read. | Accepted | One list in `workspace.json`; a test holds the doc table to it. |
| 21 | The leak fix has no criterion. | Accepted | A test with a Windows path. |
| 22 | `deny_list` blocks names, not domain facts. | Accepted | Key point reworded. |
| 23 | Five generic source features were unplaced. | Accepted | Each placed in Later or Staying behind. |
| 24 | A proposal sat under settled decisions; `--resume` restarts nothing by itself; one stop-rule condition was undefined. | Accepted | Each corrected. |

## Approval

Approved by the maintainer on 2026-11-16, with the changes below. The approved plan is this second draft together with the round-two actions marked decided. Where the body and the round-two table disagree, the table governs until the third draft.

## Changes after approval

The maintainer, 2026-11-16, at approval:

1. **A walled reader before slice 2.** Builders never open the work workspace's files. A walled reader session, which builds nothing, opens them and writes a generic description of each feature: no code, no private names, nothing copied. Builders work only from those descriptions, and the private source map is for the walled reader only. Changed: the "Nothing private" key point, the slice table, criterion 29.
2. **Slice 0 records 15 runs per arm in each case, 135 runs, on the small model, the same design as M1.** Changed: the slice 0 key point, its row, criteria 1–2 and the stop rule. Criteria 27–28 place round two's findings 6 and 21; criteria 1–2 take its findings 3 and 13. If the guided arm does not beat the two-line arm across the three cases (one-sided Fisher exact, p < 0.05), or loses any comparison M1's recording won, the result is published and the plan stops.
3. **Where each slice is built.** Slices 0 to 3 in a separate working copy outside the repository folder, because nested worktrees get past `shelved` until slice 3. From slice 4 on, under `.claude/worktrees/`. Changed: the key point and "Limits".
4. **`--no-verify` before the paid runs is a standing rule** for eval-harness work, as the machinery page's trap describes. Changed: "Limits".
5. **Slice 0's session is capped at 150 agent runs**, probes and retries included.

The agent, 2026-11-16, at approval, on the same footing:

6. **Round two's decided actions are part of the approved plan.** Finding 1 takes the playbooks out of M2, so "slice 6" now names the closing slice: the queued edits to `AGENTS.md` and `INDEX.md`, and one re-recording. A third draft applies round two to slices 1–6 before slice 1 starts. Slice 0 applies only the actions that are its own, listed in item 2.
7. **Slice 0 edits neither `AGENTS.md` nor `INDEX.md`.** Nothing slice 0 changes is named there; what slices 1–5 add waits for slice 6's recording.
8. **The descriptions stay private.** The walled reader writes them beside the private source map, not in this repository. `deny_list` blocks names, not facts about how a team or its systems work, so a public page would need the maintainer to read it first. What the builders publish still passes `deny_list`, and is generic code and pages rather than a description of the source.

## Results

### Slice 0, 2026-11-16

Merged in [#12](https://github.com/ryantornberg/agent-ready-workspace/pull/12). The full report is in the [milestone record](../milestones/m2.md#slice-0-the-eval-harness-re-recorded).

- verified: criteria 1, 2, 27 and 28 hold. `EvalHarnessApartTests` passes; seven of its eight tests failed at `397e972`.
- verified: the recording passes the gate and loses no comparison M1's recording won. 45, 19 and 0 of 45 runs passed every grader; guided against two-line, one-sided Fisher exact p = 8.4e-11.
- verified: CI passed on all five jobs, on the pull request and on `main` after the merge (criterion 26 for this slice).
- verified: 139 agent runs used of the 150 allowed; the deny list and `leaks()` passed on every transcript.
- inferred: slices 3 to 5 can now change the engine without staling the eval, since the records hash only the hook's file and the harness. Slice 3 will be the first real test of that.
