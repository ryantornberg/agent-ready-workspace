---
last-reviewed: 2026-11-17
status: draft
---

# M3, the reading layer, the rest of the safety machinery and the kit: hand-off plan

The plan for the third milestone: write fresh, in this repository, everything a person or agent reads in order to work, finish the safety machinery, and package the workspace as a kit an instance can adopt. Building sessions work from it; the maintainer approves it. It follows the [hand-off plan template](../templates/hand-off-plan.md).

**In short:** the work workspace holds about 60 core procedures, templates and record types, and machinery this repository lacks. This plan ports them in three sub-batches: the eval harness and the page structure first, with one recording; then the procedures, as pages marked proven or unproven; then the machinery and the kit. A closing slice makes the queued contract and index edits and records the eval once more.

## Key points

- **A playbook can now ship unproven, but says so.** Today every page in `docs/playbooks/` must have an eval case that beats the bare model. Of the about 60 pages this plan ports, about half are templates, record formats and tutorials, which checks and CI hold instead. About 20 are procedures an agent follows. Proving those now is not honest: cases must come from real tasks, this workspace has two milestones of them, and many procedures need machinery from M4 or M8 before they can run. Instead every procedure carries a `proof` field. A `proven` page needs a real-run record and a passing eval record; an `unproven` page is labelled as such where agents and people read it. The gate for proven pages gets stricter, not looser: each must beat the two-line arm on its own. Decision record 0006 sets this.
- **Unproven is temporary.** Each unproven page names the milestone that is to prove it, in a `prove-by` field. A check fails an unproven page whose milestone record is closed. "One that cannot be proven is cut" becomes enforced, not prose.
- **Shipping unproven pages must not hurt what is proven.** M2 showed that added text can: a longer index dropped the guided arm from 45 to 40 of 45. The closing slice adds a fourth arm to R2 that gets every page the index routes to, unproven ones included. If it does worse than R2's guided arm, the plan stops. This is measured once, not gated on every edit, because a gate would make every doc edit cost a recording; the README says so.
- **The public sentence "a playbook stays only while it beats the bare model" stops being true as written.** It becomes "a playbook marked proven stays only while it beats the bare model", beside the README's count of proven and unproven pages. The README and any other page that says the old sentence change with slice A3.
- **Three eval recordings of the fix-a-bug cases, a no-harm arm, and two proof attempts.** R1 after the harness and structure changes; R2 at close, for the queued contract and index edits, with the no-harm arm beside it. Proof attempts for the adversarial-review and debugging playbooks, each starting with a bare-only baseline. Expected total: 595 agent runs on the small model, or 730 if R1 needs its one retry, plus about 200 short selection runs, at most 150 per session. M2 made two recordings of 135.
- **R1 also tests M2's open question.** The guided arm slipped from 45 to 40 of 45 after M2's index grew, and 17 runs went looking for `docs/rules/`, which the scaffold lacks. R1 gives each case's guided arm the rule pages its code paths match.
- **Lane procedures are drafts with no wrapper.** QA, product, DevOps and automation pages are written and marked unproven. They get no skill wrapper until their lane's milestone proves them, because a wrapper's description loads into every session and would route agents to a procedure that cannot run yet. This narrows the program's "every procedure gets a wrapper" to the core procedures.
- **The always-loaded layer gets a measured budget.** The contract and tool pointers stay under 6,000 bytes (3,646 today). The wrappers' descriptions, which every session also loads, stay under 9,000 bytes in all. A check enforces both.
- **One plan, approved once, in three sub-batches.** The program asked for one plan per sub-batch; one plan with three sub-batches keeps a single red team and a single approval, which the program's step 2 calls the only approval the builders need. Any slice whose design a finished slice changes is revised under "Changes after approval" first.
- **The publish-and-approve guard allows this repository's own flow.** Agents here may publish and merge their own pull requests after CI passes. The new guard refuses approval everywhere, and publishing or merging on any repository not listed in the manifest. Only this repository is listed.
- **Builders read the private port catalog, never the work workspace.** The catalog was written behind the wall and holds generic descriptions only. A builder who finds an entry too thin asks for a walled reader; it does not open the source.

## Settled decisions

The maintainer, 2026-11-15:

- "Make sure the plan is written such that I can use the workspace itself to implement the plan. Testing the workspace could be an exercise of the workspace itself."
- "I think there might be many areas to expand in the workspace before we begin the testing." And: "the import from [the work workspace] is more narrow than I had intended."
- "Expand the scope of the workspace to officially include and guide for automations, devops, product, etc."
- "I do not have a goal to compete with anybody or even consider myself a competition." Other setups are cited only as credit for an idea taken from them.

The maintainer, 2026-11-16, approving M2's plan, carried here:

- Builders never open the work workspace's files. A walled reader session, which builds nothing, reads them and writes generic descriptions.
- Eval-harness work is committed with `--no-verify` before the paid runs; this is a standing rule.
- From M2's slice 4 on, slices are built in worktrees under `.claude/worktrees/`.
- On paying for eval runs: "We're fine in my claude subscription right now."

The maintainer, 2026-11-17:

- The port catalog's batch table is built as written.
- Six procedures that may be model coaching stay in: test-first, debugging, the throwaway prototype, delegation, safe refactoring and the research ladder. The proof rule decides them.
- One tag per milestone: M3's is `v0.4.0`.

Carried from M1 and M2:

- "Do not write on any system other people can see, and put nothing private in the public repository."
- An eval result counts at 40 or more trials per arm.
- In this repository agents push, open draft pull requests, and publish and merge them once CI passes on Linux, macOS and Windows.

## Goal

Everything a person or agent reads in order to work here exists, written fresh, and each procedure says whether it is proven. The safety machinery M2 did not build is in place, with cases and CI on three systems. A new instance can adopt the kit, and a drift check catches a hand edit to a file the kit owns.

## Non-goals

- No trap tables for one tracker or one git host, and no provider adapters. Those are M8.
- None of the six procedures and five pieces of machinery the catalog leaves out, and nothing the maintainer's own records retired: the prompt-nudge hook, the unattended loop harness, stored knowledge-graph output, the kit health check, prompt wrappers for a second tool, and code-map freshness as a blocking gate.
- No environment slots, code maps, architecture model or review machinery. Slots and code maps come with the Umbraco instance in M5; review machinery is M4.
- No edit to a file the eval hashes, except in sub-batch A and the closing slice. Today those are `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/playbooks/fix-a-bug.md`, `docs/definition-of-done.md`, `parts/no_stage_all.py`, the harness and the cases; slice A0 adds the rule pages. A slice that needs such an edit queues it for the closing slice, under "Changes after approval".
- No third-party packages in the engine, the parts or the tests CI runs.
- No outward writes beyond this repository: no upstream repository, no issue, no comment.
- No page copied or paraphrased line by line from the work workspace, and no re-sync with it after this milestone.
- No instance repository. The kit is proven on a scratch instance; the first real one is M5.
- No wrapper for a lane draft.

## Why this needs a plan

It fails two size-gate conditions: it is far more than one screen of diff, and far more than a day of work. Several slices change gates, and a broken hook can lock a session out.

## Slices

Every slice is built in its own worktree under `.claude/worktrees/`, on a branch `m3/<slice>`. A slice that touches a machinery path merges through a pull request; a doc-only slice may push straight to main from its worktree, as [changing the machinery](../changing-the-machinery.md) allows. The tier comes from the [orchestration rules](../orchestration.md): every slice that changes a gate, a hook, a grader, CI or the contract runs at the driver tier.

### Sub-batch A: the harness and the structure, with one recording

| Order | Slice | Work | Tier | Done when |
|---|---|---|---|---|
| A0 | The harness, generalized | A case may name its own arm files. The three fix-a-bug cases' guided arm also gets every rule page in `docs/rules/` whose `applies-to` matches the case's code paths. A bare-only baseline mode writes a record the gate never counts as passing. A per-playbook test pools a playbook's cases and requires guided to beat two-line, one-sided Fisher exact, p < 0.05, with 40 or more runs per arm. A new record that loses a comparison the case's previous record won fails the gate. Graders for a written review (does it name the planted flaw, does it give a verdict) and for a diagnosis (does a regression test fail on the original code, is the debug output gone). Re-grading the stored transcripts gives no difference. | driver | Criteria 1–6 |
| A1 | Structure | A layout page naming each folder and page kind: playbook, how-to, tutorial, reference, template, record, decision, plan, milestone. Each kind's required front matter, with controlled values, and the opening order: title, a purpose sentence of 25 words or fewer, an **In short** line, key points on plans. `freshness` grows into a `page_kinds` check that enforces them and refuses to pass with no pages checked. An `archive/` folder hidden from search by an ignore file, skipped by the link and page checks, with a tombstone at each old path. A glossary. The index gains cross-cutting chains: for each kind of change, every path it touches; a check fails on a chain path that does not exist. Pointer files for GitHub Copilot and opencode; Claude Code's `CLAUDE.md` and Codex's native reading of `AGENTS.md` stay. Existing pages gain the front matter their kind needs. `AGENTS.md`'s "one repository per folder" and the index's "plan being built now" row are corrected. | driver | Criteria 7–11 |
| A2 | The rules register | Every rule lives on the page it belongs to, in a rules table with an enforcement tag: `part#case`, `eval:case`, or `prose`. A `rules` check fails a tag that names a part not in the manifest or a case that does not exist. `python3 ws.py rules` prints the register with a count per tag. The contract stays at routing and traps. A `loaded_size` check enforces the budget in the key points. | driver | Criteria 12–13 |
| A3 | The proof field | Decision record 0006, what proven means. Every playbook and how-to carries `proof: proven` or `proof: unproven`; an unproven page says so in its purpose line and names, in `prove-by`, the milestone that is to prove it. A check fails an unproven page whose `prove-by` milestone has a closed record in `docs/milestones/`. `eval_record` checks proven pages only: each needs a `proven-by` link to a real-run record and passes the per-playbook test. A check holds the README's table of proven and unproven pages to the front matter. `fix-a-bug.md` is marked proven, by M1's runs and the recorded evals. | driver | Criterion 14 |
| A4 | Recording R1 | The three fix-a-bug cases, 15 runs per arm in each, 135 runs on the small model, as M2 did. | driver | Criterion 15 |

A0 goes first, so the recording covers the new harness. A1 to A3 go before R1 because each edits a hashed file. Nothing in sub-batch B or C starts before R1 passes, except C1 and C2, which touch no hashed file.

### Sub-batch B: the reading layer

Built from the private port catalog's descriptions. Every page lands with the front matter A1 requires and the `proof` field A3 requires. Pages are written in batches of about ten. The maintainer reads each batch after it lands, and a page they strike is removed in its own commit; building does not wait for the read.

| Order | Slice | Work | Tier | Done when |
|---|---|---|---|---|
| B1 | The instruction-file review, first | The review that treats guidance as a program: contradictions, executable steps, triggering text, enforcement of every must and never, placement and load cost, an eval case for new behaviour. A fresh worker-tier session runs it; the commit records it in an `Instructions-review:` trailer, as done or skipped with a reason. A commit-message check refuses a commit that adds or changes a guidance page without the trailer, and CI runs the message checks over every commit of a pull request. Every later page in this milestone goes through it. | driver | Criterion 17 |
| B2 | Core procedures | The fix path with its five human gates, the feature ladder, the spec process, the decision interview, adversarial document review, test-first, debugging, the throwaway prototype, safe refactoring, the research ladder, delegation, impact analysis, the reuse checklist, the review orchestrator's page and its explainer (its machinery is M4), architecture-invariant review, escape analysis, the feedback walk-through, the tracker and git-host spines, the docs audit, the prompt retrospective, handoff, extending, maintaining and adopting the workspace, the machine self-check prompt, two tutorials, and the one-line request map. All `proof: unproven`. | worker | Criteria 16, 20 |
| B3 | Templates and records | Plan, spec, hub and unit-doc templates; the bug ticket and pull request standards; authoring conventions. The definition of done is queued for the closing slice, because the eval hashes it. Record types: fix record, review record, interview summary, adversarial review record, epic folder, handoff note, fresh-session prompt, defect register, lessons log. The question log gains its gap kinds. A `claim_marks` check fails a fix record whose report holds a claim line not marked verified or inferred. | worker; driver for the check | Criterion 18 |
| B4 | Lane drafts | QA: the regression case and report formats, run and triage, the QA steps document, the candidates ledger. Product: grooming, the request door, epic satellites, the standup report, the effort estimate. DevOps: importing a repository, the environment self-check, release and rollback, shipping a new deployable. Automation: saved workflows. Development: the feature layer walk. Each carries `lane:` and `proof: unproven`. A guide gives each of the five roles a reading path. | worker | Criterion 19 |
| B5 | Decisions and lessons | Each workspace decision the catalog marks core or lane becomes a public decision record, or amends one already here, in the catalog's record format. One record settles the ten places where two source pages disagreed, with the choice for each. Each of the 40 lessons becomes the stated reason behind a rule or a part's `why`, or is recorded as retired. A `decisions` check holds every record to the format. | worker; driver for the disagreements record and the check | Criteria 23–24 |
| B6 | Wrappers | Each core procedure gets a thin wrapper in the Agent Skills format: a description that says when to fire and when not, naming the wrappers next to it, and a body that points at the canonical page. Declared for Claude Code as a local plugin; Codex CLI's reading of skills is checked at the slice and stated. A check fails a wrapper whose page is missing, a core procedure with no wrapper, and a lane draft with one. Selection cases on `claude plugin eval`: at least one should-fire and one should-not-fire prompt per wrapper, results recorded. | worker | Criteria 21–22 |
| B7 | Proof attempts | For adversarial document review and for debugging: two cases each, drawn from M1 and M2's real work. First a bare-only baseline, 10 runs per case. If the bare model passes 8 or more of 10 in both cases, the page is cut and the baseline kept as the reason. If it passes 5 or fewer in either case, record three arms at 20 runs per case, 120 runs per playbook, against a two-line arm written for that playbook. In between, the page stays unproven. | driver | Criterion 25 |

### Sub-batch C: the machinery and the kit

Every slice here is machinery: its own branch, the failing case first, a pull request, CI on three systems.

| Order | Slice | Work | Tier | Done when |
|---|---|---|---|---|
| C1 | Launcher and baselines | Every hook wiring entry, git hook and CI step starts Python through `wslib/launch.sh`, in UTF-8 mode, with one interpreter start per call; the Windows store stub is skipped. One baseline file of tolerated finding counts per check, all zero here, read the same way at the commit and in CI, so an adopting team can start with known findings and fail only on new ones. | driver | Criteria 26–27, 30 |
| C2 | The case runner | Cases build scratch repositories and seed leases with live and dead process ids. The runner prints each hook's median time and fails above 200 milliseconds on Linux and macOS; on Windows it reports. | driver | Criterion 28 |
| C3 | Settings, guards and the commit | Allow and deny lists for both agent tools, the deny list covering the secrets files. A discard guard, as a new part: hard reset, whole-tree checkout or restore, forced clean and stash writes are refused in the main working copy; rebase, cherry-pick and a rebasing pull are refused unless the session holds the lease; linked worktrees pass. A secret scan as a part, on the lines a commit adds and in CI over the whole history. The commit-subject format. Every check's finding names the file, the rule's page and the fix or re-run command. | driver | Criteria 29, 31–34 |
| C4 | Push and merge | A push from the main working copy by a session that does not hold the lease is refused. A merge helper: `ws.py merge` refuses unless all five CI jobs passed on exactly the pull request's head commit, then merges, deletes the branch and fast-forwards main. Its `gh` calls are a build function and a parse function, tested on recorded output. | driver | Criteria 35–36 |
| C5 | Reminders and guards | An `after-edit` event in both adapters, with recorded runs, and the chain reminder on it. A force-push guard for the default branch. The publish-and-approve guard. Secrets kept out of the agent's shell: environment dumps and reads of the secrets files are refused, and `ws.py with-secrets` passes named values to one child process only. A stop gate on a new `stop` event: when a session with edits in its ledger tries to finish, the runner runs `check` and the tests, refuses once while either fails, then reports. Decision record 0004 is amended for the two new events. | driver | Criteria 37–41 |
| C6 | Not inherited | No guard turns off when any single environment variable is unset. A killed commit check leaves no temporary file, worktree or lock behind. | driver | Criterion 46 |
| C7 | Clones and checkouts | A nightly cold-clone job: clone fresh, follow the README's marked setup steps and nothing else, run `selftest`, `check` and the tests. A pinned-repository initializer that probes every remote in parallel with prompts off and a timeout, initializes those that answer, and never touches an existing checkout. The link check gains exemptions as source-and-target pairs with a reason, and opt-in backticked paths. | driver | Criteria 43–45 |
| C8 | The kit | Before building, read AI-DLC's packager, which projects one core of hooks and agent tiers into several agent tools. Take its projection where it fits the tier binding and the hook wiring, and credit what was taken in the decision record. A kit manifest lists each kit file with its class (synced, seeded once, never synced) and its hash. `ws.py adopt PATH` creates an instance; `ws.py drift` fails on a hand edit to a synced file; an upgrade replaces synced files whose hash matches the instance's lock, and refuses on drift. A decision record holds the classes and the kill rules: three divergent copies of a synced procedure in a quarter demote it to seeded; no outside adopter in two quarters demotes the kit to a plain template. | driver | Criterion 47 |
| C9 | The two-session demonstration | Two headless agent sessions start at once on the same main working copy. The second is refused there and works in a worktree. Both commits reach main, and neither holds the other's files. The transcripts are kept as records, with a replay test. | driver | Criterion 48 |

C1 and C2 may start once A0 has merged; they touch no hashed file. C3 to C9 start after R1. Sub-batches B and C run in parallel sessions, each in its own worktree; the lease from M2 keeps them apart.

### Closing

| Order | Slice | Work | Tier | Done when |
|---|---|---|---|---|
| Z | Contract, index and recording R2 | The queued edits: index rows for every new page, chain and part; the request map and the guide linked from the contract; the definition of done brought in line with the new record types. The instruction-file review runs on each. Then R2, 135 runs, as R1, with a fourth arm, "routed": the guided arm's files plus every page under `docs/` that the index links to, unproven pages included, 15 runs in each case, 45 in all. The routed arm is recorded once and kept out of the gate's hash. | driver | Criteria 53–54 |

## Success criteria

Sub-batch A:

1. A case can name its own arm files, and the three fix-a-bug cases' guided arm holds the rule pages matching their code paths. (V1)
2. `run.py --baseline` writes a record that `eval_record` never counts as passing. (V1)
3. `eval_record` fails a proven playbook whose cases, pooled, have fewer than 40 runs in an arm, or whose guided arm does not beat its two-line arm at p < 0.05. (V1)
4. `eval_record` fails a new record that loses a comparison its case's previous record won: guided against bare in the case, or guided against two-line pooled. Losing means the guided arm passes in no more runs than the other. (V1)
5. The review and diagnosis graders each have a test with a passing and a failing run. (V1)
6. `python3 evals/grade.py --recorded` passes after the harness changes. (V3)
7. `page_kinds` fails a page missing a front-matter key its kind requires, a value outside its vocabulary, or an opening out of order. It fails when it checks no pages. (V2)
8. A page under `archive/` is not found by `rg` run with its default settings from the repository root, and the link and page checks skip it. (V1)
9. Every path listed in the index's cross-cutting chains exists; the check fails on one that does not. (V2)
10. The Copilot and opencode pointer files each name `AGENTS.md`; a check fails when one stops doing so. (V2)
11. `AGENTS.md` no longer says `src/` holds one repository per folder, and the index has no "plan being built now" row pointing at a finished plan. (V2)
12. `rules` fails a rule tagged with a part that is not in the manifest, or with a case that does not exist. `python3 ws.py rules` prints every rule with its tag and a count per tag. (V2)
13. `loaded_size` fails when `AGENTS.md`, `CLAUDE.md` and the pointer files exceed 6,000 bytes together, or the wrappers' descriptions exceed 9,000 bytes together. (V2)
14. Every playbook and how-to has a `proof` field, and every unproven one a `prove-by` milestone. A check fails an unproven page whose `prove-by` milestone record is closed. A page marked proven without a `proven-by` link, or without a passing per-playbook record, fails. The README's proven and unproven table matches the pages. Decision record 0006 exists. (V2)
15. R1 passes the gate and loses no comparison M2's closing recording won. (V3)

Sub-batch B:

16. The private port ledger maps every core procedure, template and record type in the catalog to a public page or a recorded reason. Its check prints 0 unmapped items. (V5)
17. Every commit in M3 that adds or changes a guidance page carries an `Instructions-review:` trailer. A commit without one is refused, and CI refuses a pull request holding one. (V1, V4)
18. `claim_marks` fails a fix record whose report holds a claim line not marked verified or inferred, and passes one whose lines are all marked. (V2)
19. Every lane page has `lane:` and `proof: unproven`. The guide has a reading path for development, QA, product, automation and DevOps, and every link in it resolves. (V2)
20. Every command block the two tutorials mark as runnable runs green in a fresh clone, in CI on three systems. (V4)
21. Every core procedure has a wrapper and every wrapper's page exists; no lane draft has one. (V2)
22. Every wrapper has a should-fire and a should-not-fire selection case, and the results are recorded in `evals/`. A wrapper that fails its should-fire case in most runs is rewritten once; the result is recorded either way. (V6)
23. Every decision record passes the `decisions` check; one record settles the ten disagreements. (V2)
24. The private port ledger maps each of the 40 lessons to a public rule or `why`, or to "retired". (V5)
25. Adversarial document review and debugging each have a baseline record. Each is then proven, unproven or cut by the rule in slice B7, and its page says which. (V3)

Sub-batch C:

26. No hook wiring entry, git hook or CI step starts Python except through `wslib/launch.sh`; a test fails on one that does. (V1)
27. A hook call starts exactly one Python process, measured by a test that counts starts. (V1)
28. The case runner fails a hook whose median time exceeds 200 milliseconds, on Linux and macOS, and prints every hook's time on all three systems. (V4)
29. Both agent tools' settings deny reading the secrets files, and a check fails when a deny entry is missing. (V2)
30. With a baseline of N findings for a check, N findings pass and N+1 fail, at the commit and in CI alike. (V1)
31. The discard guard refuses each form named in slice C3, allows each in a linked worktree, and allows the rebase family to the lease holder only. (V2)
32. A commit adding a line that matches a token format fails, and CI's history scan fails on a seeded token in a scratch repository. (V1, V2)
33. A commit whose subject is not conventional is refused; git's own merge and revert subjects pass; a subject over 72 characters warns. (V2)
34. Every finding any check prints names the file, the rule's page, and a fix or a re-run command; a test runs every part's cases and checks each message. (V1)
35. `ws.py merge`, on recorded `gh` output, refuses when any of the five jobs did not pass on the exact head commit, or when another session holds the lease, and otherwise merges, deletes the branch and fast-forwards main. (V1)
36. A push from the main working copy by a session that does not hold the lease is refused. (V1)
37. An edit to a path in an index chain returns that chain's paths and pages after the edit, from both agent tools; any other path returns nothing. Replay tests from recorded runs of both tools pass. (V1)
38. A force push to the default branch is refused in every form the shell parser follows; `--force-with-lease` to another branch is allowed. (V2)
39. An approval is refused on any repository. Publishing or merging a pull request is refused on a repository not listed in the manifest, and allowed on this one. (V2)
40. Environment dumps and reads of the secrets files are refused. Under `ws.py with-secrets`, the child sees the named values and the calling shell does not. (V1, V2)
41. With edits in the ledger and a failing check, the first stop is refused with the failure, and the second is allowed with a report. With no edits, stopping runs nothing. A recorded Claude Code run shows one refusal. Codex CLI is covered if it offers the event, and the README says which. (V1)
42. Every part's cases fail against a stub that allows everything and finds nothing. (V7)
43. The cold-clone job passed on three consecutive nights. (V8)
44. On fixture repositories, the initializer initializes the reachable ones, skips an unreachable one with a note and no prompt, and leaves an existing checkout untouched. (V1)
45. The link check fails an exemption that has no reason or names no target. (V2)
46. Unsetting any one environment variable leaves the lease and ledger guards working. Killing the commit check mid-run leaves no temporary file, worktree or lock. (V1)
47. `ws.py adopt` into a scratch folder makes an instance whose `selftest` and `check` pass. A hand edit to a synced file makes `ws.py drift` fail and name the file; an edit to a seeded file does not. An upgrade replaces unedited synced files and refuses on drift. The kit decision record holds the kill rules and the credit. (V1)
48. The two-session demonstration's transcripts are recorded and its replay test passes. (V1)

Whole plan:

49. Every test file under `tests/` runs in CI on three systems, except opt-in tests listed by name in the README. (V4)
50. No file in the repository holds a deny-listed term. (V2)
51. CI passes on all five jobs for every pull request in this plan. (V4)
52. `python3 ws.py check` passes on main at the end. (V2)
53. R2 passes the gate and loses no comparison R1 won. (V3)
54. The routed arm is not worse than R2's guided arm: a one-sided Fisher exact test that it passes fewer runs gives p ≥ 0.05, pooled across the three cases. `evals/README.md` reports both arms and says the comparison was made once. (V3)

## Verification

- **V1:** `python3 -m unittest discover -b tests` passes, including the test each criterion names.
- **V2:** `python3 ws.py selftest`, `python3 ws.py check` and `python3 -m unittest discover -b tests` all exit 0.
- **V3:** `evals/run.py` writes the records under `evals/runs/`; `python3 evals/pool.py` prints each comparison; `python3 evals/grade.py --recorded` and `python3 ws.py check --phase ci` pass.
- **V4:** `gh pr checks <number>` shows all five jobs passing.
- **V5:** the private port ledger's own check, run on the maintainer's machine, prints 0 unmapped items. The ledger and its check live beside the private catalog, outside every repository.
- **V6:** `claude plugin eval` runs each wrapper's selection cases. The exact command is confirmed at slice B6 and written into `evals/README.md`.
- **V7:** `python3 -m unittest tests.test_cases_bite -b` passes.
- **V8:** `gh run list --workflow cold-clone --limit 3` shows three scheduled runs on consecutive days, all successful.

## Recovery

Halt and report. Do not work around a failing case or loosen a check to pass. If a hook locks the session out, stop; the maintainer repairs it from a terminal, per [changing the machinery](../changing-the-machinery.md#traps). If a slice finds that a later slice's criterion is wrong, it proposes the revision in its report, as the template's rule 7 asks.

## Stop rule

Stop the plan and report when any of these happens:

- R1 fails the gate or loses a comparison M2's closing recording won. One recovery is allowed: revert A1's and A2's edits to `AGENTS.md` and `INDEX.md`, keep the harness, and record again. If that recording also fails, publish both results and stop.
- R2 fails the gate or loses a comparison R1 won. Publish the result and stop.
- The routed arm does worse than R2's guided arm (criterion 54). Publish the result and stop; the unproven pages stay out of the index until a person decides.
- The instruction-file review finds the same class of defect in more than a third of the pages ported so far, counted after each batch. Stop and fix the rewrite brief before the next batch.
- The engine, a part or a CI test needs a third-party package.
- More than five catalog items cannot be made generic without a private fact. Fewer are left out, each with its reason in the private ledger.
- A slice goes past two fix rounds on the same failure.
- The eval runs reach 750 agent runs, or the selection runs 300, before the plan ends.

A part that cannot be made safe on Windows within its slice ships for macOS and Linux, says so in the README, and does not weaken the guard. That is not a stop.

## Limits

- Each slice is built in its own worktree under `.claude/worktrees/`, on its own branch. No builder checks out a branch in the main working copy.
- Eval-harness work is committed with `--no-verify` before the paid runs, as the [machinery page's trap](../changing-the-machinery.md#traps) describes.
- Each recording or proof session is capped at 150 agent runs, probes and retries included. After a usage limit, a person or session reruns with `run.py --resume`; nothing restarts on its own.
- Agents push the branch, open a draft pull request, and publish and merge it once all five CI jobs pass.
- No unattended runs except the eval and selection recordings.
- Builders read the private port catalog and nothing of the work workspace. A builder that needs more asks for a walled reader, which writes to the private catalog.
- Maintainer setup before A4: `gh auth status` passes and the Claude Code command line tool is signed in. Before C5: Codex CLI signed in, for its recorded runs.

## Records this plan must leave

- Decision records 0006 (what proven means), the kit's, the disagreements', each ported workspace decision, and the amendment to 0004.
- The proven and unproven table in the README.
- The R1 and R2 recordings, the routed arm's runs, the baselines, any proof recordings, and the selection results.
- The instruction-review trailers on every guidance commit.
- The two-session demonstration's records.
- A report per slice under "Results", with each claim marked verified or inferred.
- `docs/milestones/m3.md`, with the always-loaded size before and after, plus entries in `CHANGELOG.md` and `EVIDENCE.md`.
- Question-log rows for anything a builder had to ask.

## Later

- **The review orchestrator's machinery, the review mark and draft-only pull requests.** M4.
- **Eval marks at push and the eval stage in CI.** M4.
- **Environment slots, code maps and the doc-coverage and doc-symbol checks.** M5, against real code.
- **Removing a session's worktree after its work lands.** A `session-end` reminder; it waits for real worktree use in M5.
- **Worktrees reading pinned repositories from the main copy.** Matters once pinned repositories exist, in M5.
- **Trap tables for a tracker and a git host, and the schema-drift check.** M8.

## Red team

Not yet run.

| # | Finding | Verdict | Action |
|---|---|---|---|

## Approval

Not yet approved.

## Changes after approval

None yet.

## Results

None yet.
