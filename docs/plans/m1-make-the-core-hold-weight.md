---
last-reviewed: 2026-11-15
status: approved
---

# M1, make the core hold weight: hand-off plan

The plan for the first milestone of the workspace's expansion. Building sessions work from it; the maintainer approves it. It follows the [hand-off plan template](../templates/hand-off-plan.md).

**In short:** a red team ran attacks against this repository, and several README claims did not survive them. This plan repairs each failure, with the attack as the failing test. It then re-records the eval so that the eval can show the guidance losing.

## Key points

- **Slice 0 is built, on the local branch `m1/slice-0`, and waits on this approval.** It holds the [orchestration rules](../orchestration.md), the [size gate](../size-the-work.md), [changing the machinery](../changing-the-machinery.md), the two templates, the `deny_list` check and the first real question-log row.
- **The order is 0, 2, 1, 5, 4, 6, 7, then 3.** Slice 2 comes first so that no session is locked out by the hooks it edits. That lockout happened while building slice 0. The eval comes last because it is the costly step, and slices 5 and 6 change what its hash covers.
- **Every slice runs at the driver tier.** Each one changes a gate or the hook wiring.
- **Agents never push.** Each slice is committed on a local branch. The maintainer pushes it, waits for CI on three systems, and merges.
- **Every attack becomes a test that fails before its fix and passes after it.** Attacks this milestone does not fix are listed, each with the milestone that will.
- **The eval may lose.** If the guided arm does no better than a two-line instruction, that result is published and the playbook is cut. The graders are not tuned until it passes.
- **A contract edit will cost an eval run.** Once the eval feeds the real contract to the agent, any edit to `AGENTS.md` or `INDEX.md` needs a passing re-run of the affected cases, at five runs per arm.

## Settled decisions

The maintainer, 2026-11-15:

- "make sure the plan is written such that I can use the workspace itself to implement the plan. Testing the workspace could be an exercise of the workspace itself."
- "The workspace should already contain orchestration rules."
- "Do not write on any system other people can see, and put nothing private in the public repository."
- An eval result counts at 40 or more trials per arm, with graders that read the folder and the commit.
- The second agent tool is Codex CLI.
- Slice 2 comes before any hook is made stricter.

## Goal

Every claim in the README survives the red team's attacks, and the eval can lose.

## Non-goals

- No playbooks beyond slice 0's templates. The fix-a-bug playbook's wording changes only with a new passing eval run.
- No tracker or code-host adapters. No hook moments beyond the new before-handoff one.
- No edits under `src/orders-service-v1`.
- No push, pull request, issue, comment or release by an agent, on any host.
- No grader changes made to turn a failing eval into a passing one.
- No README claim without a command or a record behind it.

## Why this needs a plan

It fails three of the four size-gate conditions. It spans weeks, it touches every gate, and the eval re-recording is not cheap to reverse.

## Slices

| Order | Slice | Work | Tier | Done when |
|---|---|---|---|---|
| 1 | 0. Bootstrap | Orchestration rules and the tier binding; size gate; changing the machinery; the two templates; the `deny_list` check; the first real question-log row; this plan | Driver | This plan is approved, and CI is green on the pushed branch |
| 2 | 2. No self-lock | A case runs with its own settings only. A hook call loads only the hooks for its event. A part outside the workspace is refused. Cases assert a finding's level. Required parts come from the last commit locally and from the base branch in CI. | Driver | Criteria 1 to 6 |
| 3 | 1. Hooks fail closed | A versioned event shape, with one adapter per agent tool. Unknown shapes are refused. A launcher that refuses when Python is missing. A before-handoff moment, with a hook that refuses a delegated task naming no tier. | Driver | Criteria 7 to 11 |
| 4 | 5. Staging rule at the commit | The commit check compares staged paths with the paths the session edited. The shell hook stays as an early reminder. The commit message and identity are checked against the deny list. | Driver | Criteria 12 to 14 |
| 5 | 4. Adoption path | Page checks cover workspace-owned folders by default. Undecodable files are reported. Both snapshots come from one file listing and one batch read. `AGENTS.md` and `INDEX.md` carry review dates. Names in the contract are checked. | Driver | Criteria 15 to 19 |
| 6 | 6. Shape for growth | Engine in one folder. A version in the manifest. Parts selectable by phase. A `why` on every manifest entry. The manifest's keys are validated. CI gets a permissions block and a weekly run. Two small parser fixes. | Driver | Criteria 20 to 24 |
| 7 | 7. Second tool | The hooks run under Codex CLI, through their own adapter, with one recorded run. | Driver | Criterion 25 |
| 8 | 3. An eval that can lose | A case where workspace knowledge changes the outcome. A third arm with a two-line instruction. Three cases pooled to 40 or more trials per arm. Graders read the folder and the commit. Graders, harness and contract inside the hash. CI re-grades stored transcripts. The agent runs in a container. | Driver | Criteria 26 to 31 |

Each slice runs the way fix-a-bug runs, one attack at a time: write the test, see it fail, fix, see it pass. A slice ends with the report from the [definition of done](../definition-of-done.md#the-report). The tag `v0.2.0` follows the last slice.

**Why the eval is last, though it is the most serious finding:** recording 120 or more runs is the costly step. Its hash will cover the harness and the graders, which slices 5 and 6 change. Recording it earlier means recording it twice. The README already calls the current eval a demonstration, not a benchmark.

## Success criteria

Criteria 1 to 31 are each a named test in `tests/` or a case in `parts/*.cases.json`. The first three commands under "Verification" run them all. Each slice report shows its tests failing at the slice's base commit and passing at its tip. Criteria 32 to 35 are checked by the maintainer.

**No self-lock (slice 2)**

1. Changing any documented setting of a part leaves that part's own cases passing. The red team's examples: freshness `max_age_days` and `require`, aliases `code` and `heading`, links `skip`.
2. With one check's case broken, a `before-shell` hook call for `ls` exits 0, while `selftest` and `check` still fail. With one `before-shell` hook's case broken, the hook call exits 2.
3. With the manifest half-written, every hook call exits 2 and names the manifest. The repair is the person's step, from their own terminal.
4. A manifest `use` that points outside the workspace is refused when it loads.
5. A case can state a finding's level, and does. A part demoted to warnings fails its own cases.
6. The required parts are the names in the last commit's manifest locally, and in the base branch's manifest in CI. A manifest that drops one fails, unless it lists the part as retired with a reason. Only part names are read from the older manifest, so keys added later do not break the comparison. An unstaged edit to a part's cases does not change the result of `check --staged`.

**Hooks fail closed (slice 1)**

7. Every event that is neither the versioned shape nor a known tool's payload exits 2. The red team's examples: an empty event; a `filePath` field; a `cmd` field; a command given as a list; a top-level `file_path`; a `toolArgs` string.
8. These edits to the shelved folder are refused: through an upper-cased absolute path on a case-insensitive file system; through a symbolic link that points into it; through the notebook edit tool.
9. A path inside a code repository under `src/` is decided like any other path, with a test for each answer.
10. With no Python on the path, the wiring exits 2, not 0 or 1.
11. A delegated task whose prompt names no tier is refused. One whose model or effort differs from the binding for its tier is refused, where the tool exposes that setting. One that names its tier and matches is allowed.

**Staging at the commit (slice 5)**

12. The hooks record each path the session edits in a ledger per working copy, inside `.git/`. While a ledger is open, a commit that stages a path not in it fails `check --staged`, whatever command staged it. With no ledger, as for a person's own commit, the check passes, and the README says so.
13. These are allowed: `git commit -m"add export handler"`, `git add -u docs/parts.md`, and `git add .` inside a temporary fixture repository.
14. A commit whose message, author email or committer email matches the deny list is refused by a commit-message hook.

**Adoption path (slice 4)**

15. With a stand-in code repository under `src/` holding its own broken links, `check` passes.
16. A Windows-1252 or UTF-16 file is reported by the checks, not skipped. `symbols.py` finds a type declared in a Windows-1252 file.
17. `check` and `check --staged` agree on each of these: a stray `.DS_Store` in the eval scaffold; a `.pytest_cache` folder there; a symlinked page; a staged file under `node_modules/`.
18. On a repository of 3,000 tracked files, `check --staged` starts at most three git processes. A test counts them.
19. `AGENTS.md` and `INDEX.md` fail without a review date. A backticked name in the contract that the code no longer defines fails. A page dated one day ahead of UTC passes.

**Shape for growth (slice 6)**

20. `python3 ws.py --version` prints the engine version, and the manifest's `version` must match it.
21. `python3 ws.py check --phase nightly` runs only nightly parts.
22. The runner refuses a manifest entry with no `why`, an unknown top-level key, and a `tiers` entry that lacks a model or an effort for any of the three tiers.
23. The CI file has a `permissions` block and a weekly `schedule` trigger.
24. The link reader reports a line over 10,000 characters instead of parsing it. `symbols.py` does not report `new Order(1),` as a constructor.

**Second tool (slice 7)**

25. A recorded Codex CLI run, in a scratch clone of the workspace, shows the reminder on `git add -A` next to the command's result, the sweep refused at the commit, and an edit to the shelved folder refused. The files Codex wrote with its patch tool reach the slice-5 ledger, and their commit passes. A test replays every hook payload the run recorded and gets the same answers. A patch that touches several files is refused when any one of them is in the shelved folder, a move into it included, and then records none of them.

**An eval that can lose (slice 3)**

26. A new case asks for a fix to "the nightly job", with a tempting fix in the shelved folder. A grader reads the commit and fails any run that changed the shelved folder.
27. Three arms run: the guidance, no guidance, and a two-line instruction.
28. Three cases are pooled: fix-a-bug, the nightly job, and a request about "the big report". Each arm has 40 or more trials. The table in `evals/README.md` gives each arm's pass rate with its 95% interval.
29. A `last-reviewed:` line outside the front matter changes the hash. Editing `grade.py`, `run.py`, `AGENTS.md` or `INDEX.md` changes the hash. The gate accepts a record only with five or more passing runs per arm for each affected case. The gate also refuses a record in which, for any affected case, the guided arm passes no grader more often than the bare arm.
30. CI re-grades every stored transcript, and fails when a grade differs from the record.
31. The agent runs inside the agent tool's own operating-system sandbox where the tool has one, and inside a container where it does not. Its permissions are bypassed only inside one of the two. A recorded transcript holds none of the operator's environment: no home folder, user name, shell alias or git identity.

**For the whole milestone, checked by the maintainer**

32. The private attack scripts, run against a scratch copy, find every attack either handled or listed under "Attacks left for later".
33. The first three commands under "Verification" pass in CI on Linux, macOS and Windows.
34. Every README claim has been re-read against the results, and fixed or removed.
35. A fresh session has red-teamed the result, and every finding is triaged in the milestone record.

## Attacks left for later

| Attack | Why not here | Where it goes |
|---|---|---|
| Discards: `git stash -u`, `git checkout -- .`, `git reset --hard`, `git clean -fd` | A guard on discards belongs with session safety | M3, session safety |
| A commit made inside a code repository under `src/` runs no workspace check | Needs hooks installed in each pinned repository | M3, submodule setup |
| `git commit --no-verify` skips the commit hook | CI re-runs the checks, but the staging rule needs the session's ledger, which CI lacks | Stated in the README |
| A compressed file holding a private term | The deny list does not open archives | Not planned; stated in the part |

## Verification

Run by the building session, in this order, before each slice's report:

```
python3 ws.py selftest                       # every part "ok"; exit 0
python3 ws.py check                          # exit 0, with no deny-list warning on the maintainer's machine
python3 -m unittest discover -b tests        # "OK"
```

Run by the maintainer:

- CI on three systems, after pushing the slice's branch. Every job green.
- At the end, the private attack scripts against a scratch copy.

## Recovery

- **By default, halt and report.** Do not work around a failing check, case or test.
- **A hook refuses every call.** Stop. Say which part and which case, and give the person the command that repairs it.
- **A criterion cannot be met as written.** Stop and say why. Propose a revised criterion under "Changes after approval". Do not build it until the maintainer approves.
- **A fix makes an existing case fail.** Revert the fix, not the case.

## Stop rule

- If the eval shows no difference between the guided arm and the two-line arm, publish that result and cut the playbook to what does differ. A difference means a one-sided Fisher exact test at p < 0.05 on the pooled pass rate.
- If slice 2 cannot remove the self-lock without letting a hook fail open, stop and report. Failing closed wins.

## Limits

- Sessions are attended. A review loop runs while it converges.
- Each slice is committed on its own branch, named `m1/slice-<n>`, with files staged by name. Agents push the branch to this repository; see "Changes after approval".
- Where fix-a-bug says to open a draft pull request, stop at the local commit instead.
- Each question the session had to ask the maintainer becomes a [question-log](../question-log.md) row before the slice ends.
- Before slice 3, the maintainer starts Docker, if the agent tool has no sandbox of its own. Before slice 7, the maintainer confirms the `codex` command runs.

## Records this plan must leave

- This plan, approved, with its red-team triage.
- A test or case per attack.
- The re-recorded eval runs and the new results table.
- A CI run on three systems.
- Question-log rows from real sessions.
- Two decision records: the engine in its own folder; hooks remind and the commit enforces.
- A changelog entry and the first `EVIDENCE.md`.
- The [milestone record](../milestones/m1.md).

## Red team

A fresh session, at the driver tier, attacked this plan and slice 0 on 2026-11-15. It ran its attacks on a scratch copy. It found ten problems, three of them blocking.

| # | Finding | Verdict | Action |
|---|---|---|---|
| 1 | The deny list did not run in agent sessions, because the environment variable was unset there. | Accepted | The check falls back to a fixed path under `~/.config` when the variable is unset. |
| 2 | "Every attack exists as a case" could not fail, and about a dozen attacks had no criterion. | Accepted | Each attack is now a criterion or is listed under "Attacks left for later". Each test must fail before its fix. |
| 3 | One manifest edit switched the deny list off, and its cases still passed. | Accepted | The part refuses `terms` and `list` outside its cases. It no longer reads `skip` or a variable name from the manifest. |
| 4 | A file-name finding printed the private term. | Accepted | A matching name prints as its folder and a hash. |
| 5 | The deny list failed open on several inputs. | Accepted in part | Fixed: a list file with a byte-order mark; words split by spaces, hyphens or underscores; zero-width and full-width characters; UTF-16 with no byte-order mark. Moved to criterion 17: staged files under `node_modules/`. Declined, and stated in the part: compressed files, and a committed list holding only regular expressions. |
| 6 | Slice 7 at the worker tier broke the orchestration rules. | Accepted | Slice 7 runs at the driver tier. |
| 7 | Several criteria were vague or could be met by a wrong build. | Accepted | Every criterion is now a named test. The timing criterion counts git processes. The third eval case is named. The stop rule names its test. The ledger rule says what happens with no ledger. Criterion 2 also requires the checks to still fail. |
| 8 | Some dependencies between slices were missed. | Accepted in part | Codex feeds the ledger. Only part names are read from an older manifest. The cost of putting the contract in the eval hash is in the key points. Declined: moving the eval earlier, for the reason under "Slices". |
| 9 | The new pages contradicted older ones. | Accepted | Corrected: slice 0's status, CI in its done-when, two README sentences, and the orchestration page's model table. A misspelt `tiers` key is refused under criterion 22. |
| 10 | Private details reached public pages, and commit identity was not scanned. | Accepted | Removed a private finding number and a description of the build machine. Commit identity is checked under criterion 14. |

## Approval

Approved by: Ryan Tornberg, 2026-11-15.

## Changes after approval

- 2026-11-15, the maintainer: agents may push slice branches to this repository. Merging into main still waits for CI to pass on all three systems. Agents push nothing to any other host.
- 2026-11-15, the maintainer: agents open a draft pull request for each slice, which runs CI.
- 2026-11-15, the maintainer: agents publish and merge a slice's pull request once CI passes on all three systems. The contract says so.
- 2026-11-15, the maintainer approved two revisions to slice 3. Criteria 29 and 31 and the Docker line under "Limits" now carry them.
  - **Criterion 29 gains a sentence:** "The gate also refuses a record in which, for any affected case, the guided arm passes no grader more often than the bare arm." Why: today `eval_record` checks only that the guided arm passed. A playbook the bare model follows just as well still ships, which contradicts the eval page's rule that guidance stays only while it beats the bare model. The stop rule's Fisher test still decides the milestone's pooled result; this sentence is the cheap check on every change.
  - **Criterion 31 becomes:** "The agent runs inside the agent tool's own operating-system sandbox where the tool has one, and inside a container where it does not. Its permissions are bypassed only inside one of the two. A recorded transcript holds none of the operator's environment: no home folder, user name, shell alias or git identity." Why: Claude Code's sandbox already confines writes to the run's folder, hides the home folder and limits the network. A container is then needed only for a tool without one. The Limits line "Before slice 3, the maintainer starts Docker" applies only if a container turns out to be needed.
- 2026-11-15, the maintainer approved a revision to criterion 25, which now carries it.
  - **Criterion 25 becomes:** "A recorded Codex CLI run, in a scratch clone of the workspace, shows the reminder on `git add -A` next to the command's result, the sweep refused at the commit, and an edit to the shelved folder refused. The files Codex wrote with its patch tool reach the slice-5 ledger, and their commit passes. A test replays every hook payload the run recorded and gets the same answers. A patch that touches several files is refused when any one of them is in the shelved folder, a move into it included, and then records none of them."
  - **Why the reminder, not a refusal:** since slice 5 the shell hook never refuses `git add -A`; the commit check does. [Decision 0002](../decisions/0002-hooks-remind-the-commit-enforces.md) gives the reasons. The criterion as approved predates it.
  - **Why a replay test:** every other criterion is a named test that can fail later. A recording alone cannot. The replay runs in CI on three systems, so a change to the adapter that would misread Codex fails there.
  - **Why the several-file patch:** Codex edits through one patch tool, and one patch can add, change, delete or move several files. Deciding only the first path would let a shelved edit through as the second.
  - **Why a scratch clone:** the sweep needs a file the session did not write, and a refused commit leaves the index staged. In a scratch clone neither touches the main checkout or its ledger. The live run of the session's own hooks still happens in the main checkout before the push.

## Results

Slice 0: see the [milestone record](../milestones/m1.md#slices).
