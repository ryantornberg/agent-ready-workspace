---
kind: plan
last-reviewed: 2026-11-26
status: draft
milestone: M4
---

# M4, fail-closed shell guards, the review loop and the eval system: hand-off plan

The plan for the fourth milestone: close the shell guards' known gaps with one rule, then build the review loop and the eval system. Building sessions work from it; the maintainer approves it. It follows the [hand-off plan template](../templates/hand-off-plan.md).

**In short:** M3 left routes past the shell guards, a review that runs by hand, and ten pages that name M4 as the milestone to prove them. This plan closes the routes with one rule in the parser, builds the review's dispatch, mark and gate with teach-back and a merge policy, and builds the eval system those ten pages are tested with. It is a draft: not yet approved.

## Key points

- **The guards come first, under one rule.** A shell guard refuses any command whose deciding word the parser cannot resolve to a literal. Each known force-push route is a numbered row with a case.
- **The guard fixes wait for one small slice.** H0a moves grading files out of the recording's hash, so G2 to G4 merge on a re-grade.
- **The review loop:** dispatch, a completion record, a review mark, a gate at pull-request creation, teach-back and a merge policy.
- **The eval system:** suites, a gate at the push, and proof attempts for ten pages.
- **Eval runs:** about 1,285 planned, a stop at 1,400. After M4, an edit batch to a proven page costs about 132 runs.
- **Review sessions:** about 231 planned, stop at 250, 16 per pull request.
- **The stop rule splits findings.** A gap a slice caused can stop it. A gap open on main is recorded instead.
- **The decision queue is cut:** its trial closed no item from evidence.
- **Red team:** thirteen rounds held with fixes; 119 findings settled; round 14 next.
- **Not approved.** Every queue answer through Q106 is applied.

## Settled decisions

Spec not yet agreed. The maintainer agrees the spec and approves the plan together, after its red team; "Decisions made without asking" names the risk.

The maintainer, 2026-11-25, in the brief for this plan:

- Shell-parser work comes first. The guards fail closed on any word the parser cannot resolve to a literal. That is one rule, not a fix per route.
- The rule covers B3, B4, the zsh glob qualifier, the lines the red team's finding 6 names, and the commands git runs from its config or its environment. The pre-push fix rides with it.
- `python3 ws.py merge` retargets stacked pull requests before it deletes a branch.
- The stop rule separates a gap a slice caused from a gap already open on main. Eval-harness changes land in their own slice before any recording.
- Eval run budgets are stated per slice, because runs cost his usage quota.
- The plan says whether M4 builds the decision queue, and why.
- This plan stops before its red team, and is neither published nor merged.

The maintainer, 2026-11-26, in the brief for this revision:

- Apply every queue answer through Q103, and the upkeep cost of a proven page.
- Then run the red team round, triage every finding, and loop as the red team page says. The pull request stays a draft. Nobody approves or merges it but him.

Added to the brief the same day, through the coordinator:

- Pull request 59 moved the decision queue plan's red team tables into dated records, on the maintainer's answer to Q3. The plan template and the red team review page still say a plan keeps its triage table. M4 aligns them, and this plan says which form it takes.
- The run budget counted eval runs only. The review gate starts five or more driver-tier sessions for each pull request, and nothing capped that. The plan estimates review sessions per pull request and per slice, sets a cap or scales the dimensions to the diff, and says where the count is reported.

The maintainer, answering M3's queue, 2026-11-21 to 2026-11-25:

- **Q6.** The two gaps in the proof checks close in M4.
- **Q35.** Handoff's keep mode, a tracked copy of a note, waits for M4.
- **Q41.** Where a review commits its record on a branch is settled in M4.
- **Q45.** M4 decides whether a second agent tool loads the wrappers.
- **Q46.** An agent starts an eval or selection batch only on his yes for that batch, with a run count.
- **Q49.** M4 reruns the four fire cases that still miss at five turns, about 12 runs, before any second rewrite.
- **Q51.** Debugging's cases are fixed and recorded again in M4, with the fixes M3's slice B7 proposed.
- **Q53.** Reading the `with-secrets` wrapper in the parser waits for M4.
- **Q54, Q74, Q75, Q79, Q80.** The guards' own refusals of lines the parser misreads are stopgaps until the parser's fix, which comes early in M4. No list of programs is kept until then.
- **Q73.** M4 points the debugging fixture at `/home/user` when it records debugging again.
- **Q82.** The pre-push check is fixed in M4 with the parser work: it loads the library from the same commit as the cases, or skips cases for a ref no push check judges.
- **Q84.** The merge helper retargets every open pull request based on a merged branch before it deletes that branch, with a case.
- **Q85, and the sign-off.** B3, B4 and the zsh glob qualifier outside a push go to M4 with the parser work.

The maintainer, answering this plan's queue, 2026-11-26:

- **Q86.** The decision queue is cut. Its trial's bar C2 failed on one count: no item was closed from evidence before M3's sign-off. So, as that plan's own settled decision says, its plan is marked abandoned. The earlier count of answers acted on looks too low and is not the reason. His private decide pass stays private.
- **Q87.** The eval ceiling is 1,400 runs, staged. All ten baselines run first, about 200 runs. He then picks which pages get a recording. A page past the ceiling stays unproven and moves to M6.
- **Q88.** A re-grade holds grading files. A parser or grader change needs no new runs when re-grading every stored transcript changes no grade; a changed grade still needs a recording. The parser fix, G2, merges after R3. *Amended by Q102, 2026-11-26: G2 to G4 merge after H0a, not after R3.*
- **Q89.** Slice H0, now H0b, adds a usage check. `run.py` reads a usage file kept outside the repository before a batch, and refuses when over his limits. No file means the check is off. Only a stale file counts as unknown. Its rules sit outside the eval's hash.
- **Q90.** In G4 the outward-write guard also reads a list kept outside every repository, as `deny_list` reads its list. G4 updates the guard's cases and decision 0004.
- **Q92.** The leak rule accepts the placeholder `/home/user` inside quotes only after the path is normalized: `..` resolved and letter case matched. Cases cover a quoted placeholder and `/home/user/../bob/x`. Debugging's fixture moves to `/home/user`.
- **Q91.** A review scales to its diff. A pull request is capped at 16 review sessions, and M4 stops at 250. Reuse, docs drift and the re-check run at the worker tier, unless the change touches a gate.

The maintainer, 2026-11-26, on three recommendations of the session that drafted this plan:

- **Q91, narrowed.** Reuse and docs drift run at the worker tier always, since their findings never block. The gate exception is the re-check's alone.
- **One arm is re-recorded alone.** An edit that changes only what one arm is given needs that arm's runs again, and not the other arms'. A change of model, or of a file every arm shares, still needs every arm.
- **The decision queue plan is marked abandoned now,** and not by a slice of M4. It was, on 2026-11-26.

The maintainer, answering the workspace's queue, 2026-11-26:

- **Q101.** Every force-push route the private attack scripts' report lists is a numbered row in this plan, with a case. M3's record names them as known limits.
- **Q102.** Slice H0 splits. H0a is the grader stamp alone, landed on a re-grade. G2 to G4 depend on H0a only. The stop rule names the fallback: the parser fix gets its own 135-run recording. Q88's line above is amended.
- **Q103.** H0b changes the hand-off plan template's Red team section, red team review's step 5 and `evals/acceptance/red-team-lease.py`, so a plan's triage may live in each linked record. It lands in H0b, before R3. Q95's earlier answer put the same change in M4's first slice; Q103 is the later answer and governs.
- **Q104.** The selection and routing stop rises from 300 to 400.
- **Q105.** An agent may run a pull request's wrapper suites at its head itself, up to 12 runs per pull request. A larger run and the routing suite still need his yes with a count.
- **Q106.** The red team loop runs on until a round only finishes earlier work.
- **Upkeep.** The plan states what each proven page costs to edit after M4, and how edits to proven pages are batched. From his notes of 2026-11-25.

The maintainer, on the program, 2026-11-17 to 2026-11-24:

- M4 carries the proof attempts for the six procedures that may be model coaching, and for the four other pages M3 shipped with `prove-by: M4`.
- Teach-back is the human half of the review mark. A merge policy per repository is `agent` or `person`. A review reports at most five nits. A declined security or architecture finding needs a tracker key, or an acceptance with initials and a date.
- A procedure M3 left without a wrapper gets its wrapper in the milestone that proves it, after its name and scope are settled.
- A `lifecycle_map` check joins M4.
- One tag per milestone: M4's is `v0.5.0`.

Carried from the maintainer's notes of 2026-11-22 (inferred to be his decision; he corrects it on review):

- No pattern catalog and no saved agent roles. The dispatch script is the one place a delegation pattern is encoded, and each recurring brief becomes a template it reads.

Carried from M1 to M3:

- Agents write on no system other people can see, and nothing private goes into this repository.
- An eval result counts at 40 or more trials per arm. Eval runs are paid from the maintainer's subscription.
- In this repository agents push, open draft pull requests, and publish and merge them once CI passes on Linux, macOS and Windows.
- Builders never open the work workspace's files. A walled reader, which builds nothing, reads them and writes generic descriptions.
- Public pages make no comparative claims.

## Decisions made without asking

Each is the author's. A reviewer reads this section to challenge them.

- **Git settings pass by an allow list** (G3). Rejected: a list of the settings that run a command. Git has too many, and each one missed is a route to main.
- **A path inside a git folder passes only for a program that only reads** (G4). Rejected: the list of writers, which missed `tar`, `unzip` and `patch`.
- **No copy of the wrappers for Codex** (Q45). Rejected: a second skills folder. The selection cases run only on `claude plugin eval`, so a copy would ship untested, and the maintainer's own records retired prompt wrappers for a second tool. The README keeps the limit.
- **The eval gate moves from the commit to the push** (H2). A commit and a branch push warn; a push to main is refused; CI fails the pull request. Rejected: refusing the commit, which forces `--no-verify` commits while a recording is still to come.
- **The baselines run two arms, 400 runs, where Q87 said about 200.** Q87 set the baselines first and the pick after them; this keeps that order and adds the two-line arm, so the pick sees whether two lines already match a page. The maintainer's approval accepts the change; it is also in his queue. Rejected: the bare arm alone, which left 660 recording runs chosen blind to the comparison a recording most often fails.
- **Five of the ten pages are planned to reach a recording.** That five is a guess, and the baselines replace it. The ceiling of 1,400 is the maintainer's (Q87).
- **A stale usage reading stops a batch** (H0b, item 7). Q89 says a stale file counts as unknown, and leaves open what unknown does. Here `run.py` names the reading's age and refuses, unless the batch's yes allowed a run without a reading. Rejected: going on, which would spend quota on a reading nobody trusts.
- **The routed arm is measured once more at the close.** M4 adds contract lines, index rows and pages, and M3 showed that added text can cost passes.
- **Both red team cases' hidden tests change, not only the lease case's** (H0b, item 9). Q103 names `red-team-lease.py`. `red-team-fail-closed.py` makes the same assertion, so a run that puts its triage in the record, as the page will allow, would fail it. Rejected: changing one, which leaves two cases that disagree on what the page asks.
- **Size the work and the milestone record template change with the playbook** (H0b, item 9). Three places in size the work say the plan's table holds the triage. Rejected: leaving them, which would make them half true.
- **No check enforces either form.** Q103 says the triage *may* live in the record, so a plan that keeps its table is still right. Rejected: a check that fails a draft plan's table, which the first draft proposed.
- **Edits to a proven page are batched once per milestone** (Upkeep after M4). Rejected: a recording per edit, at about 44 runs each, and no rule at all, which leaves the count to whoever edits.
- **H0a migrates the stored records' hashes with no new run** (H0a). A test shows each record was current under the old hash at H0a's base, and that no file an agent is given changed. Rejected: re-stamping by hand, which the gate could not tell from a forged stamp.
- **A review scales to its diff, and a pull request is capped at 16 review sessions** (L1). Rejected: every dimension on every round, which makes about 22 sessions for a pull request with two fix rounds; and a cap alone, which stops a loop late without making it cheaper. Reuse runs when the range adds a file or a function, where the page runs it always today: the program counts four dimensions that always run. The maintainer settled the cap and the tiers on 2026-11-26 (Q91); the reuse trigger is still the author's.
- **A range of tests or eval cases alone gets two dimensions,** code and test adequacy. Rejected: the four. A test or a case holds no architecture to judge, and the code dimension reads what it could weaken.
- **New pages name M6 in `prove-by`.** A page cannot be proven by the milestone that writes it, and M6 uses the review loop on real fixes.
- **Machine-state records go to M5**, with the first instance. M3 left the choice between M4 and M5 open.
- **Names:** see [names this plan fixes](#names-this-plan-fixes).
- **The red team ran before the spec was agreed.** The maintainer's brief asked for the red team before his approval, and size the work puts the spec's agreement first. He agrees the spec and approves the plan in one step, after the loop. Its risk: a goal, non-goal or criterion he changes then sends the plan back for another round.
- **A plan of four sub-batches, approved once,** as M3 was. Rejected: a plan per sub-batch, which would need four red teams.

## Goal

Three things are true at the end. The work starts from M3's open ends: the "Known limits, for M4" in [M3's milestone record](../milestones/m3.md#known-limits-for-m4), and findings 7 and 10 of [its red team's record](../records/adversarial-reviews/2026-11-25-m3.md).

1. **The shell guards fail closed.** A shell guard refuses a command when a word it must judge cannot be resolved to a literal. Each route past the guards that M3's record lists for M4 is refused, with a case.
2. **No pull request opens without a review that is shown to have run.** A review mark, written only from the reviewers' own output, sits at the reviewed commit. A gate refuses a pull request without one. Teach-back and a merge policy per repository say who may publish and merge.
3. **No proven procedure and no wrapper changes without its cases running on the old and the new version.** Each of the ten pages that name M4 in `prove-by` is proven, cut, or unproven with a failed attempt on record.

## Non-goals

- **No decision queue.** It is cut (Q86): its trial closed no item from evidence before M3's sign-off. [Its plan](decision-queue.md) was marked abandoned on 2026-11-26, and M4 builds none of its slices.
- **No matching of findings to existing threads, and no posting of comments.** Both need a git-host provider, which is M8. The guard that refuses every `gh api graphql` call stays as it is.
- **No live agent run in CI.** CI re-grades stored transcripts and checks marks. Agent runs stay on the author's machine.
- **No new wrapper, and no rise in either always-loaded ceiling:** 6,000 bytes for the contract and pointer files, 9,000 for the wrappers' descriptions. No copy of the wrappers for a second agent tool.
- **No guard on what an interpreter or a script does.** A hook reads a command line. What `python3 -c`, a script file or `curl` then does stays out of reach, and the README keeps saying so.
- **No signature on a mark.** A mark shows that a process ran on this content. It does not stop a person who edits files by hand, and the pages say so.
- **No change, after the first recording, to a file that decides what an agent is given:** `run.py`, `proofkeys.py` and the hash itself. Grading files may change on a re-grade, as H0a sets out.
- **No edit outside the closing slice to a page a gated record hashes:** the contract, the index, `fix-a-bug.md`, the definition of done and the order service's rule page. A file hashed only into an unproven page's own cases may change before that page's attempt. One exception: H0b rewrites the contract's eval rule, since R3 records every arm right after it.
- **No edit to a page under a proof attempt once its M4 attempt has started,** except the commit that cuts it or replaces one of its cases.
- **No reading of an agent tool's transcripts outside one adapter per tool.** For evals the adapter is `run.py`'s own reader, frozen after R3. For the review loop it is L1's.
- **No machine-state records.** They go to M5, with the first instance.
- **No pattern catalog and no saved agent roles.** The dispatch script is the one place a delegation pattern is encoded.
- **No third-party package** in the engine, the parts or the tests CI runs.
- **No outward write beyond this repository,** no instance repository, and no page copied from the work workspace.

## Why this needs a plan

It fails two size-gate conditions: it is far more than one screen of diff, and far more than a day of work. Most slices change a gate, and a broken hook can lock a session out.

## Slices

Every slice is built in its own worktree under `.claude/worktrees/`, on a branch `m4/<slice>`, started from the remote's main. H0a has the branch `m4/h0a`. H0b and H1 share the branch `m4/h`. A slice that touches a machinery path merges through a pull request; a doc-only slice may push straight to main, as [changing the machinery](../changing-the-machinery.md) allows. Every slice here changes a gate, a hook, a grader or the contract, so each runs at the driver tier; a slice's page batches may go to worker-tier helpers, and every review is driver work.

Recordings are numbered on from M3's: R3 follows the harness slices, and R4 closes the milestone.

### Sub-batch G: the guards

| Order | Slice | Work | Tier | Done when |
|---|---|---|---|---|
| G0 | Open M4 | `building` becomes `["M4"]`. The test that pins it to M3, the parts page's row and the adoption page are corrected. A check fails a `building` entry whose milestone record is signed off. `.env` joins `.gitignore`. | driver | Criterion 1 |
| G1 | Push check and merge helper | The pre-push check loads a part's cases and the library they call from one commit (Q82). `ws.py merge` retargets pull requests stacked on a branch before it deletes that branch (Q84). | driver | Criteria 2–3 |
| G2 | The one rule, in the parser | The parser marks each word literal or not. A guard refuses a command whose deciding word is not literal. The stopgaps in the guards' own files go. See "G2" below. | driver | Criteria 4–8 |
| G3 | Commands git itself runs | A git setting passes only when it is on a list of settings known to run no command. A git option that takes a command is read as that command. See "G3" below. | driver | Criteria 9–10, 62 |
| G4 | Guard gaps outside the parser | The routes the private attack scripts marked non-blocking: discards, secret reads, the ledger's close, repository copies through `gh api`, and writers into a git folder. See "G4" below. | driver | Criteria 11–12 |

G0 and G1 touch no file the eval hashes. They branch from main and merge at once, so no later push needs `--no-verify`. G2 starts on the same day. G2 to G4 change the parser, which grades stored runs, so each merges only after H0a is on main, on a re-grade that shows no difference (Q102). If a re-grade changes a grade, the [stop rule](#stop-rule) names the fallback.

### Sub-batch H: the eval harness and the eval system

| Order | Slice | Work | Tier | Done when |
|---|---|---|---|---|
| H0a | The grader stamp | Grading files leave the recording's hash and get a stamp a re-grade writes. Stored records are migrated with no new run. Nothing an agent is given changes. See "H0a" below. | driver | Criteria 13, 61 |
| H0b | The other harness changes, before R3 | The model in a record, the leak rule, debugging's fixture and cases, batches, one-time arms' re-record, the proof checks' two gaps, a usage check, one arm's re-record, where a plan's red team triage lives, and a baseline of two arms. See "H0b" below. | driver | Criteria 14–19, 48, 60, 63 |
| H1 | Recording R3 | The three fix-a-bug cases, 15 runs per arm in each: 135 runs. A guided arm that misses its margin is recorded once more, 45 runs, in a new batch. H0b and H1 share one pull request. | driver | Criteria 20–21 |
| H2 | Suites, marks and the push gate | One suite per wrapped page, and a routing suite. A runner that picks suites from changed paths and runs the base and the head. A mark by content fingerprint. The gate at the push and in CI. See "H2" below. | driver | Criteria 22–27 |
| H3 | Proof attempts | The ten pages that name M4: a baseline of the bare model, then a recording where the baseline calls for one. Debugging goes first, with its fixed cases. See "H3" below. | driver | Criteria 28–30 |

H0a starts on the first day, beside G0, and merges first. H0b starts after H0a, in its own lane. H2 starts after H1 merges. Its gate merges after L4 and L7, which edit most of the wrapped pages M4 touches, so their edits run no suite. H3 starts after H1, and takes each page only after the last slice that edits that page.

### Sub-batch L: the review loop

| Order | Slice | Work | Tier | Done when |
|---|---|---|---|---|
| L0 | Facts and prior art | Record how each agent tool starts a headless session at a tier with its edit tools off, and where its transcript is. Test two existing review marks against this plan's criteria. A decision record says what is taken and what is built. See "L0" below. | driver | Criterion 31 |
| L1 | Dispatch | `ws.py dispatch` builds a prompt from a template file and its inputs, starts a fresh session at the tier's model and effort, and writes the reply to a record. Each recurring brief becomes one template file. It scales a review to its diff, and counts sessions against a cap. See "L1" below. | driver | Criteria 32–34, 57–59 |
| L2 | The completion record | For each reviewed commit, which dimensions completed, judged from each reviewer's own output. The findings table. A re-check of earlier "fixed" rows, and a whole-branch pass. See "L2" below. | driver | Criteria 35–36 |
| L3 | The review mark and the gate | `ws.py review mark` with its refusals, `ws.py review status`, and a `review_gate` part that refuses a pull request with no mark, or one that is not a draft. See "L3" below. | driver | Criteria 37–40 |
| L4 | The finding lifecycle | Verify before fixing. "Fixed" names the check that fails without the fix. A decline names where the defect now lives. A direction rule in place of a round count. A nit cap. The defect register's cross-check. See "L4" below. | driver | Criteria 41–42 |
| L5 | Teach-back | A playbook, a grader template and a teach-back mark at the commit. A trivial change gets one question or a recorded skip. See "L5" below. | driver | Criterion 43 |
| L6 | Merge policy | A `merge_policy` entry per repository in the manifest, `agent` or `person`; none means `person`. The review gate reads it. See "L6" below. | driver | Criteria 44–45 |
| L7 | Small pieces | The `lifecycle_map` check. Red team review's form for a milestone's outside check. Handoff's keep mode. One rule for where a review's record is committed. See "L7" below. | driver | Criteria 46–47 |

L0 starts beside G2. L1 and L2 run in order after G1 merges. L3 waits for L2 and for G2, whose rule its gate calls. L4 follows L3. L5 follows L3; L6 follows L3 and G4, whose list it reads. L7 may run beside them.

**First real use.** From L3's merge on, every pull request of this plan that changes a machinery path passes the gate: reviewed through the loop, marked, then opened. Before L3, a guard or harness slice ends with one fresh driver-tier re-check instead, as M3's did. A review comes before the runs it could spoil: H0b's re-check, or its review and mark after L3, runs on H0b's diff before R3's batch starts, and each H3 page's cases and two-line text are reviewed before its baseline. A commit of run records alone, files under `evals/runs/` or `evals/selection/` that CI's re-grade passes, is a record-only commit and keeps the mark. A defect found later in code a marked review covered goes to [escape analysis](../playbooks/escape-analysis.md) and becomes an outcome case, or a recorded reason why not.

### Closing

| Order | Slice | Work | Tier | Done when |
|---|---|---|---|---|
| Z | Contract, index and recordings | The queued edits to hashed pages, each with its instruction review. The version goes to 0.5.0. Then R4, the guided arm's 45 runs, and the routed arm, 45 runs, in separate batches. Then the records. See "Z" below. | driver | Criteria 49–56 |

After slice Z, the program's outside checks run before sign-off: CI, a fresh-session red team under L7's form, and private attack scripts written by a session that built nothing here, against the guards, the review gate and the mark. The tag `v0.5.0` follows sign-off.

### G0: Open M4

The [defect register](../records/defects.md) holds the row this slice closes: M3's sign-off left M3 in `building`, because a test pins the list to M3 and the adoption page says it names M3. The test stops pinning a number. The `proof` check gains one rule: a `building` entry whose record in `docs/milestones/` has `status: signed off` fails. M4 then removes itself in its own sign-off commit, and that rule holds every later milestone to the same step. The register's `.env` row closes here too: the secrets file joins `.gitignore`, in the repository and in the kit.

### G2: The one rule, in the parser

**The rule.** The parser reports, for each word it reads, whether the word is literal: bash and zsh would both hand the program exactly the text the parser reports. A word is not literal when it holds, outside quotes, a variable, a substitution, braces the shell expands (a comma or a range inside, so `HEAD@{1}` and `stash@{0}` stay literal), a glob, zsh's extended glob, `=name`, or a `(` that zsh reads as a glob group or a glob qualifier. It is not literal when it holds an ANSI-C escape other than the seven both shells read alike, or a quote the parser cannot close as the shells do, as inside `${...}` or `((`.

A command is unresolved, and every shell guard refuses it, when a word that decides what runs, or what it acts on, is not literal:

- the program word, and the words of a wrapper or a shell before its program;
- for a command a guard judges, its subcommand and each argument that guard reads: a refspec, a remote, a write's path, a `git config` key, a repository, a folder;
- any command nested deeper than the parser unwraps.

These follow from the same rule, and replace M3's rule about unread programs:

- **A judged program after an unread one is judged.** After a program the parser does not read, a literal word that names a program a guard judges, such as `git` or `gh`, is read as that program's command, and the line is refused when either reading would be. So `uv run git push -f origin main`, `direnv exec . git push -f origin main` and `parallel git push -f origin ::: main` are refused, and `which git` and `grep -n git notes.txt` pass, since neither reading of them is refused (row F28).
- **A word that may be a program is judged as one.** After a program the parser does not read, a word that is not literal may become `git` or `gh`. The words after it are judged as that program's, and the line is refused when either reading would be. So `arch $(command -v git) push -f origin main` is refused, and `ls *.md` passes.
- **Text that may be a command is judged as one.** A quoted argument of a program the parser does not read is parsed as a command line, as the text of `sh -c` is today. So `flock FILE -c 'git push -f origin main'` and `man -P '...' ls` are refused. A message body, such as `-m` or `--body`, is still never read so. In text read only because it may be a command, a program word that is not literal does not refuse the line by itself. The line is refused when a reading reaches a program a guard judges, or when that word could expand to such a program's name. So `curl -s 'https://example.com/v1/jobs?content=true'` and `tr '[:upper:]' '[:lower:]'` pass.
- **A shell's script operand is a deciding word.** `source` and `.` count as shells. A shell's or `source`'s script operand of `/dev/stdin`, `/dev/fd/N` or `-` reads the redirected text, judged as the next bullet says; a process substitution there, `<(...)` or zsh's `=(...)`, has its text read as a command line. So `bash /dev/stdin <<< '...'`, `bash <(echo '...')`, `source <(echo '...')` and `. =(echo '...')` are refused (row F33).
- **Known text on standard input is judged too.** Text the line itself holds, such as a `printf` or `echo` literal, a heredoc or a here-string (`<<<`), piped or redirected into a program the parser does not read, is parsed as a command line, as text piped into a shell is today. So `printf 'git push -f origin main' | script -q /dev/null` is refused, and `git log --oneline | head -5` passes. Text whose content the line does not hold, such as a download piped into such a program, is not judged; the README's Limits names that route.
- **A session's temporary folder is known.** A write path that starts from `TMPDIR`, which the hook reads at hook time, or from a `mktemp` result in the same line, resolves to a literal path under the temporary folder, which G4 then judges as any path, a git folder made there included. So the test-first idiom `D="$TMPDIR/old" && mkdir -p "$D" && git show HEAD:src/x.py > "$D/x.py"` passes.
- **A variable the line sets is read with its value.** When a word is a variable assigned earlier in the same line, the parser judges the word as that value, so `C='git push -f origin main'; flock /tmp/l -c "$C"` is judged as the text it runs. A variable counts as set only when every assignment to it before the word runs unconditionally in the same shell: not inside `if`, `case`, a loop, a function body, a background job, or after `&&` or `||`. Otherwise the word stays not literal, so `if [ -d / ]; then C=git; else C=echo; fi; $C push -f origin main` is refused, as it is today. A variable the line does not set stays not literal.
- **Programs that never run their arguments are listed.** A short list beside the parser, such as `echo`, `printf`, `grep`, `cat` and `ls`, names programs whose quoted arguments are never read as commands, so `grep -rn 'git push -f origin main' docs` passes. Every program not on the list is judged as above. Q79 kept no list until M4; this is the list M4 brings. G4 keeps a second list, of programs that only read, which is a subset of this one and holds no program that writes: `echo` and `printf` are on this list and not on G4's.
- **The lists live in the parser's own file,** `wslib/shell.py`, which the grader hash covers, so a change to a list changes the grader hash.
- **An interpreter's code is not a shell line.** A second short list names programs whose quoted argument is code in another language or a pattern: `python3`, `node`, `perl`, `ruby`, `awk`, `jq`, `sed`, and `find`'s `-name` and `-path` values. Their quoted arguments are not parsed as a shell line, so `python3 -c "import json; print(1)"`, `awk '{print $1}' notes.txt` and `find . -name '*.py'` pass. What that code then runs is the interpreter limit the README already states.

The parser also matches every program name it reads without regard to letter case, the shells, `env` and `printenv` included, since macOS and Windows find a program whatever its case.

**What it must refuse, each with a case.** The rows F11 to F18 under [force-push routes](#force-push-routes-numbered-q101). Text on standard input of an unread program, and a variable the line sets given as its text. B3 and B4, such as `echo x > .gi?/config`, `git config {alias.p,!sh}` and `rm outward-repos.jso?`. The zsh glob qualifier outside a push, such as `ls README.md(e:'git push -f origin main':)`, and the same word in an array assignment and a `for` list. Glob grouping in a program word, `g(i)t` and `g@(i)t`. The lines M3's last re-checks left: a quote inside `${...}` or `((`, runner text, a shell or `env` in another letter case, a shell the parser does not read when it is given text, and a word of only `\0` among the words of `sudo -s`. A brace in a discard, such as `git reset --{hard,}`.

**What goes.** The block of stopgap rules that M3 held twice, the guards' own refusals of a program word the shell expands, and the rule that refused any word naming a judged program after an unread one, which the first bullet above replaces with a reading that refuses only a refused command. `no_stage_all` does not take the rule: it only reminds, and it is the staging grader of the fix-a-bug cases, so a change to what it flags would change stored grades.

**A line that changes what a word means is unresolved.** A line that defines an alias, a global alias, a named folder (`hash -d`), a command-hash entry (`hash NAME=PATH`) or a trap changes what a literal word later runs or names, which no reading of the words shows. Every shell guard refuses such a line (rows F30 and F31). A trap's text is also read as a command, as `sh -c` text is.

**A runner's own options end at its first operand.** The parser reads `watch`'s options across the whole line today, so a `-f`, `--force` or `--delete` after `git` is taken as `watch`'s own and dropped from the push (row F19). Each runner's options end at its first operand, as the runner itself reads them, and G2's re-check also covers how the parser reads each known runner's options.

**The `with-secrets` wrapper (Q53).** The parser unwraps `python3 ws.py with-secrets NAME -- PROGRAM`, so each guard judges PROGRAM as it judges any command. `secrets_shell` stops refusing git, gh and writes under it outright. Each route M3's slice Z found has a case.

**The measure.** Before it merges, the slice runs the guards at main and at its tip over every command stored under `evals/runs/`, and reports each line whose answer changed. The maintainer's machine repeats that over its session logs, as M3's sign-off did. A newly refused line that does nothing a guard guards is fixed, or named in the README with its way round.

**The re-check.** One fresh driver-tier session gets the rule, the cases and the README's limits, and looks for a line that passes and should not. Its findings follow the [stop rule](#stop-rule)'s split. The README's Limits is rewritten around the rule: what the guards refuse, and what stays out of reach, which is an interpreter, a script, a program's own configuration, PowerShell, and a tracked hooks folder that a known repository's own config names, such as this repository's `.githooks/` or a pinned repository's `.husky/`, which their owners edit as ordinary work (row F27).

A new decision record states the rule, and decision 0004's amendments point to it.

### G3: Commands git itself runs

Git runs a program named by many settings: an editor, a pager, a credential helper, an ssh command, a filter, a diff or merge tool, a hooks folder, a file-system monitor. Ten of the private attack scripts' attacks got past the force-push guard through one of them.

- **Settings pass by an allow list.** A `-c KEY=VALUE`, a `GIT_CONFIG_*` pair, a variable git reads that is set on a git call, such as `GIT_EDITOR`, `EDITOR` or `GIT_SSH_COMMAND`, and a key `git config` writes, each passes only when it is on a list of settings known to run no command. `user.name`, `color.ui` and `GIT_AUTHOR_DATE` are on it. Anything else is refused, with a message that names the setting and the list. The list lives in one place, beside the parser.
- **A variable set earlier in the line counts as set on the call.** `export GIT_EDITOR=...; git commit --amend` is judged as `GIT_EDITOR=... git commit --amend`, since the parser already carries an export into the commands after it. An export made under a condition is judged on every value the line could leave, so a conditional `export GIT_EDITOR=true` does not hide an earlier unsafe one.
- **Every variable on a git call is judged, `HOME` and `XDG_CONFIG_HOME` included.** Each chooses a config file git reads, so setting either on a git call, or exporting it earlier in the line, is refused unless its value is the session's own (row F25).
- **A safe value passes.** A setting that names a command passes when its value is one literal word, `true`, `:` or a program on G2's never-run list, with no shell character, since git runs such a value through the shell, so `GIT_EDITOR=true git rebase --continue` passes.
- **Config written at clone or init counts as `-c`.** `git clone -c` and `--config` write the new repository's config, and each is judged as `-c` is (row F20). `--template=DIR` on `clone` or `init` copies in both a config and hooks, which the clone itself then runs, so it is refused unless DIR is a known folder (row F32). `GIT_TEMPLATE_DIR` and `init.templateDir` pass by the allow lists, which hold neither.
- **A git folder other than this repository's own is unresolved, unless the guard reads it.** `--git-dir`, `GIT_DIR`, `-C` and a `cd` before a git call that name a folder whose config the guards have not read make the call unresolved, since that folder's config may name a command. A folder the guard reads at hook time counts as known: this repository's worktrees and a pinned repository, one that `.gitmodules` or the manifest lists. Its existing config is a person's, as the next paragraph says, so `git -C src/REPO log` passes in a repository with husky's `core.hooksPath` or git-lfs filters. What an agent's command sets or writes is judged, a folder made or written in the same line included (F20, F24).
- **An option that takes a command is read as that command.** `rebase --exec` is read so today. The same reading covers `bisect run`, `submodule foreach`, `filter-branch`'s filters, `difftool --extcmd`, `grep --open-files-in-pager`, and `--upload-pack`, `--receive-pack` and `--exec` on the commands that reach a remote.
- **A remote's transport passes by an allow list too:** `https`, `ssh`, `git` and a local path. `ext::` runs a command and is refused.

A setting a person keeps in their own git config is theirs: the guards judge what an agent's command sets or writes. The slice's measure and re-check are G2's, and so are G4's: the measure runs over the stored eval commands and the maintainer's session logs, so a `gh` write the allow list would refuse, such as `gh run rerun` or `gh pr close`, shows up before the merge.

### Force-push routes, numbered (Q101)

Each route below but F28 force-pushes or deletes main past every shell guard on main today. F28 is refused today by a rule G2 removes, so its case shows it stays refused, at G2's base and at its tip. Each gets a case that fails before its slice and passes after it, named by its row. F1 to F10 are the routes the private attack scripts' report lists. F11 to F18 are the lines M3's last reviews left, as M3's record names them. F19 to F33 are routes this plan's red team rounds found. A route a slice's re-check finds later joins the table, under the stop rule's split. B1 and B2 of the same report closed in M3, with cases, and are not repeated.

| Row | Route | Example | Closed by |
|---|---|---|---|
| F1 | `core.editor` given with `-c` | `git -c core.editor='git push -f origin main; true' commit --amend` | G3 |
| F2 | `GIT_EDITOR` in the environment | `GIT_EDITOR='git push -f origin main; true' git commit --amend` | G3 |
| F3 | `GIT_SEQUENCE_EDITOR` in the environment | `GIT_SEQUENCE_EDITOR='...' git rebase -i HEAD~1` | G3 |
| F4 | `git bisect run` | `git bisect run sh -c 'git push -f origin main'` | G3 |
| F5 | `core.fsmonitor` given with `-c` | `git -c core.fsmonitor='...' status` | G3 |
| F6 | A difftool's `cmd` | `git -c difftool.x.cmd='...' difftool -y -t x HEAD~1` | G3 |
| F7 | A mergetool's `cmd` | `git -c mergetool.x.cmd='...' mergetool -y -t x` | G3 |
| F8 | The `ext::` transport | `git -c protocol.ext.allow=always ls-remote 'ext::sh -c ...'` | G3 |
| F9 | `credential.helper` given with `-c` | `git -c credential.helper='!git push -f origin main' credential fill` | G3 |
| F10 | `GIT_SSH_COMMAND` in the environment | `GIT_SSH_COMMAND='sh -c "..."' git ls-remote URL` | G3 |
| F11 | A zsh glob qualifier outside a push | `ls README.md(e:'git push -f origin main':)`, and the word in an array or a `for` list | G2 |
| F12 | A quote inside `${...}` or `((` | `: ${x:-$'\''} && git push --force origin main # '}` | G2 |
| F13 | Runner text | `flock /tmp/l -c 'git push -f origin main'`, `man -P '...' ls` | G2 |
| F14 | A runner whose program is a substitution | `arch $(command -v git) push -f origin main` | G2 |
| F15 | A shell, `env` or `printenv` in another letter case | `BASH -c 'git push -f origin main'` | G2 |
| F16 | A shell the parser does not read, given text | `arch -arm64 tcsh -c '...'` | G2 |
| F17 | A word of only `\0` among `sudo -s`'s words | `sudo -s $'\0' 'git push -f origin main'`, and under `sudo -i` | G2 |
| F18 | Glob grouping in a program word | `g(i)t push -f origin main`, `g@(i)t ...` | G2 |
| F19 | A runner's options read past its first operand | `watch git push -f origin main`, and its `--force`, `--delete` and `-x` forms | G2 |
| F20 | Config written by `clone` or `init`, then run after a `cd` | `git clone --config core.fsmonitor='...' . /tmp/c && cd /tmp/c && git status` | G3 |
| F21 | A `gh api` write that force-moves or deletes the default branch's ref | `gh api -X PATCH repos/O/R/git/refs/heads/main -F force=true` | G4 |
| F22 | A `gh api` merge of a pull request, past the checks an owner's sign-in skips | `gh api -X PUT repos/O/R/pulls/5/merge` | G4 |
| F23 | A `gh api` merge of a branch into the default branch, with no pull request | `gh api -X POST repos/O/R/merges -f base=main -f head=x` | G4 |
| F24 | A git folder made and written in the same line | `git init --bare /tmp/b && cp CFG /tmp/b/config` | G4 |
| F25 | `HOME` or `XDG_CONFIG_HOME` on a git call, pointing at a config the agent wrote | `HOME=/tmp/h git commit --amend` | G3 |
| F26 | Other `gh api` writes that move main or its checks | A ref `PATCH` without `force`, a `contents` write to main, a branch protection write, a `default_branch` change | G4 |
| F27 | A line added to a tracked git hook, which the next commit runs, in this repository or a known one whose config names a tracked hooks folder | `printf 'git push -f origin main\n' >> .githooks/pre-commit`; the same in `src/REPO/.husky/pre-commit` | Out of reach, named in the README |
| F28 | A literal judged program after a program the parser does not read | `uv run git push -f origin main`, `direnv exec . git push -f origin main` | G2 |
| F29 | `gh` subcommands that move main or its checks on a listed repository | `gh repo edit O/R --default-branch x`, `gh repo sync O/R --force`, `gh workflow disable ci.yml -R O/R` | G4 |
| F30 | An alias, a global alias, a named folder or a command-hash entry set earlier in the line | `alias g=git; eval g push -f origin main`, `hash -d G=.git; printf x >> ~G/config` | G2 |
| F31 | A trap whose text pushes | `trap 'git push -f origin main' EXIT` | G2 |
| F32 | A template folder's hooks, run by the clone that copies them | `git clone --template=/tmp/t . /tmp/c` | G3 |
| F33 | A shell or `source` given its own line's text as a script | `bash /dev/stdin <<< 'git push -f origin main'`, `source <(echo '...')` | G2 |

Examples shortened with `...` run the same push as F1. The cases hold each line in full.

### G4: Guard gaps outside the parser

Each is a route M3's private attack scripts found and marked non-blocking. None is a parser fault.

- **Discards, `no_discard`.** Git accepts any unique prefix of a long option, so the parser resolves `--har` to `--hard` as git does, and an ambiguous prefix is unresolved. While another live session holds the lease, the guard also refuses, in the main working copy: `checkout-index` with `-f` or `-a`, `update-ref` on a branch or the stash, a `restore`, `checkout --` or `rm` of paths, and a `clean` with `clean.requireForce` turned off.
- **Secret reads, `secrets_shell`.** `gh auth status --show-token`, `gh auth token`, `git credential fill`, the macOS keychain's password commands, a plain read after a `cd` into a secrets folder, `/proc/*/task/*/environ`, and `${!v}` over a list of every variable's name.
- **Person-only commands, under any spelling.** Each guard that refuses an agent's `ws.py` command refuses it under `wslib/launch.sh` and `wslib/start.py` too. The person-only commands, `ledger --close`, `review accept` and `teach-back`, also refuse in the command itself when the agent tool's marker variable is set or standard input is not a terminal, so a spelling no guard reads still stops there.
- **The ledger's close.** A before-shell part refuses `python3 ws.py ledger --close` from an agent session that holds entries of its own. It needs a new fact for the before-shell event, the session's own ledger entries, which the `stop` event alone has today, so decision 0004's fact table is amended. A person runs the close from a terminal.
- **Repository copies, `outward_write`.** A `gh api` write to a `forks` or `generate` path creates a repository, and is judged as `gh repo fork` is.
- **`gh` writes pass by an allow list.** On a listed repository, an agent's `gh` write, by a subcommand or by `gh api`, passes only when its method and endpoint are on a short list beside the guards, such as comments, labels, and a review that is not an approval. Everything else is refused, as G3 treats git settings: a ref update with or without `force` (row F21), a pull request or branch merge (F22, F23), a `contents` write, branch protection, rulesets, the repository's settings such as its default branch, and Actions settings (F26); and the same writes by subcommand, such as `gh repo edit --default-branch`, `gh repo sync --force`, `gh repo archive`, `gh repo rename`, `gh workflow disable`, `gh secret set` and `gh variable set` (F29). The list allows creating and editing a pull request, comments, labels, issues, and a review that is not an approval. An agent merges only through `ws.py merge`, in every repository.
- **A second list, outside every repository (Q90).** The tracked list is public, so it cannot name a repository whose name must stay private. `outward_write` also reads a list from the file a variable names, or from a default path beside the deny list, as `deny_list` reads its own. One file then serves every worktree, and nothing can commit it. `outward_list` refuses an agent's edit to that file as it refuses one to the tracked list. A missing file adds nothing. Decision 0004 is amended.
- **Paths inside a git folder, `git_folder_shell` and `outward_write`.** Today a named list of writers is refused, and `tar`, `unzip` and `patch` are not on it. The rule turns round: a command that names a path inside a git folder, or the outward-write list, passes only when its program is on G4's list of programs that only read, which never holds `cp`, `tee`, `sort` or any program that writes. A folder counts as a git folder when it is named `.git`, or when it holds `HEAD`, `objects` and `refs` at hook time, git's own test for a bare repository, so `printf ... >> /tmp/b/config` is refused when `/tmp/b` is one. Separately, a write of a file named `config` into a folder that holds `HEAD`, or of `HEAD` into a folder that holds `config`, is refused, so the order of writes does not matter. A folder that merely holds a `config/` folder, as a Rails application does, is not a git folder. A folder that `git init`, `git clone`, `--bare` or `--separate-git-dir` names earlier in the same line counts as a git folder too, since it does not exist at hook time (row F24).

### H0a: The grader stamp

M3's slice Z changed the harness inside the slice that recorded, and stopped three times on gaps in its own leak rule before its recording could start. Here every harness change lands before R3, and a test fails a later change (criterion 21). The grader stamp lands first, alone, because the guard fixes wait on it and on nothing else (Q102).

- **Two hashes.** Today one hash covers what the agent is given and the code that grades. A change to grading code, such as the parser the staging grader calls, then needs 135 new runs, though no agent would act differently. The record keeps its hash over what an agent is given, and gains a second hash over the grading files: `grade.py`, each hook a grader runs, and the parser.
- **The stamp.** When only grading files change, `python3 evals/grade.py --recorded --stamp` re-grades every stored transcript and, when no grade differs, writes the new grader hash. When a grade differs, the record fails until the case is recorded again: a grading rule is not changed after the runs it grades. CI's re-grade runs on every push, and fails a stamp nobody earned.
- **The migration, with no new run.** H0a's commit rewrites in the new form only the records current under the old hash at its base: today the three fix-a-bug records and the twelve one-time records that carry their cases' hash. A record already stale, as debugging's two records and baselines and red team review's baseline are, stays stale in the new form. A test reads the base commit, shows which records were current there, and shows that no file an agent is given differs between the base and H0a. So the records stand on the same runs. `run.py` and `proofkeys.py` do not change: the grader hash is computed and checked in `eval_record`, and written by the stamp. If the builder finds `run.py` must change, the migration is not sound, and the [stop rule](#stop-rule)'s fallback applies.
- **No `--no-verify`.** The records and the hash change land in one commit, which passes every hook.
- Decision 0006 is amended.

### H0b: The other harness changes, before R3

Each lands on the branch `m4/h` before R3 records, in the pull request R3's records join. H0b also rewrites the contract's eval rule to read: a change the eval covers reaches main only with its eval run, and a change to grading files alone only with a re-grade that changes no grade. Its tag stays `eval_record`. R3 records the contract as it then reads.

1. **The model in a record.** A record names the model and the agent tool's version of every run. The gate fails a record whose arms ran on different models, or on a model other than the one the manifest names for evals. A tool version that differs between arms is a warning, and the eval page reports it. The `eval_record` part's manifest entry names the eval model by its full id, and `run.py` reads it there in place of its own default, which closes the defect register's row on model names outside the tier binding. A record's model must equal that id.
2. **The leak rule (Q92).** M3's last re-check left two items: the placeholder's own path is refused when an agent writes it in quotes, and a `..` route passes. The rule normalizes a path first, resolving `..` and matching letter case, and only then accepts the placeholder `/home/user`, inside quotes too. Cases cover a quoted placeholder and `/home/user/../bob/x`, which is refused.
3. **Debugging's fixture and cases (Q51, Q73).** The fixture's owner becomes `/home/user`. The contract copy routes a failure to the playbook. The page's first step asks for the repro as a test. The fix case drops its ruled-out grader, or the page's fix path keeps that list. These files are hashed into debugging's own cases only.
4. **Batches.** A batch is every run started under one yes from the maintainer, across calls of `run.py`. `run.py` takes the batch's name and count, counts each started run in a batch file, probes and failed runs included, and refuses to start a run past the count. It also counts each session an agent dispatches inside its run, read from the transcript, so the count is built before the freeze on `run.py`. The eval page defines a batch, and no longer caps a "session": M3's slice Z ran 225 runs against a cap of 150 because that word was loose.
5. **One-time arms.** `--rerecord` takes a one-time arm and keeps its first batch, and `pool.py` prints one-time arms with their pooled counts. M3 moved folders and pooled by hand.
6. **The proof checks' two gaps (Q6).** `eval_record` gates a page marked proven wherever it sits under `docs/`, not only in `docs/playbooks/`. `proof` fails a proof key on a page whose kind carries none.
7. **A usage check before a batch (Q89).** Before a batch, `run.py` reads a usage reading from a file kept outside the repository, which the maintainer's own tooling writes, and refuses the batch when the reading is over limits he sets there. No file means the check is off. A stale file counts as unknown: `run.py` names the reading's age and refuses, unless the batch's yes allowed a run without a reading. The call sits in `run.py`; its rules sit in a file outside the eval's hash, so tuning them stales no record.
8. **One arm re-recorded alone.** The bare arm is given no files, and the two-line arm only its two lines. So an edit to a page changes nothing either of them reads, yet today it makes all three arms stale. The record's hash over what an agent is given splits per arm, beside one hash over what the arms share: the case, its hidden test, the scaffold and the harness. The case's playbook page, which the hash adds today outside every arm, moves into the guided arm's hash, since only the guided arm is given it. When only one arm's files change, `eval_record` asks for that arm alone, and `run.py` records it in place of the old runs. The other arms' runs stand, and the gate compares as before. When a shared file or the model changes, every arm is recorded. A one-time record holds its own arm's hash beside the shared one. A tool version that differs between the arms is the warning item 1 gives. `run.py` also writes each arm's milestone and the grader hash into each new record, so R3 and every later recording carry them. `eval_record` asks for every arm when the arms' milestones differ; `eval_record` fails a record with no grader hash once H0b has merged. An edit to a proven page then costs about 44 runs where it would cost 132, and a contract or index edit 45 where it costs 135. Decision 0006 is amended.
9. **Where a plan's red team triage lives (Q103).** A plan's triage may live in each linked record's Disposition column, as the decision queue plan's has since pull request 59. A plan that keeps its own table is still right. The hand-off plan template's Red team section and rule 4, red team review's step 5, the three places [size the work](../size-the-work.md) names the plan's table, and the milestone record template's row say so. Both red team cases' hidden tests, `red-team-lease.py` and `red-team-fail-closed.py`, accept a disposition in either place, and the harness test's stand-in run checks both. These are red team review's own case files, not R3's: the page is unproven, so no gate reads its record. Its one stored record, a 10-run baseline of one case, is stale already. The eval page still says no attempt run is on record, and H0b corrects that paragraph; M9, which is to prove the page, runs the baseline again. The change lands in H0b's pull request, before R3, under the same freeze as the rest of the harness.

10. **A baseline of two arms.** `run.py --baseline` runs the bare and the two-line arms, 10 runs each per case, into one baseline record that names the page, the milestone and the verdict `not proven`, with a test. It writes to a path named by its milestone, `evals/runs/<case>/baseline/M4/record.json`, so the `proof` check, which reads the milestone at the commit that added the record, sees M4; debugging's M3 baseline stays where it is. A test covers a page whose case holds an older baseline. Decision 0006's 2026-11-21 amendment, which names the old path, is amended too. `grade.py --recorded` widens its search to every `record.json` under `baseline/`, so CI re-grades M4's baselines, with a test; since `grade.py` is a grading file after H0a, the change lands with its stamp. It lands before the freeze on `run.py`, because H3's baselines come after R3. A case whose agent dispatches helpers counts them toward its batch, so the three dispatching pages' baselines may cost more than 40 runs each.

H0b's commits use `--no-verify` until R3's records are in, as the [machinery page's trap](../changing-the-machinery.md#traps) requires. H2 then moves that refusal to the push.

### H2: Suites, marks and the push gate

- **A suite belongs to one page that has a wrapper.** It holds that wrapper's selection cases, in the format M3's slice B6 set. A page's outcome cases stay where they are, under `evals/cases/`, gated by `eval_record` as today. One routing suite belongs to the contract and the index: a cold session gets a request and must name the right page.
- **Two runners, as today.** Selection and routing cases run on `claude plugin eval`. Outcome cases stay in `run.py`, because the plugin runner cannot run code graders.
- **Cases come from real work.** Each outcome and routing case names what it was drawn from: a commit, a pull request, a record or a question-log row. The names live in one file, `evals/sources.json`, outside every case's hash, so naming the fix-a-bug cases' sources stales no record. A check fails a case with no entry. Every grader is deterministic; none is judged by a model.
- **The suite runner.** `python3 evals/suites.py` picks suites from the changed paths: a wrapper, its cases, or any page a wrapper names. A change to the contract or the index picks routing. It runs each picked suite at the merge base and at the head, in temporary working copies, under the run cap it is given. A case that passed at the base and failed at the head runs at the head up to twice more, and counts as a regression at two failures of three: one run's difference is noise as often as signal. It exits 1 only for pass-to-fail, and 2 when the cap or the runner gave no verdict.
- **What passing means.** A selection case runs three times and passes when at least two of its runs pass. An outcome case passes as the eval page says. A suite passes when every case passes.
- **The routing suite is held to its base, not to every case.** It covers the contract and the index, which every session reads, so one routing case that misses at the small model must not block every contract edit. Its mark is written when no case passed at the base and failed at the head, at two failures of three, as the runner's regressions are counted. Its baseline in H2 shows which cases miss.
- **A suite with no mark.** For content a suite covers, the gate treats no mark as a failed suite. A wrapper whose suite cannot pass after Q49's rerun and one more rewrite is listed under a new key, `unpassing`, in the `wrappers` part's manifest entry, with its reason and the milestone that is to fix it; the part's code and cases learn the key. The gate warns on a listed suite and refuses nothing for it, and the milestone record names each one. The list starts with the four that miss today, and is empty when its milestone closes.
- **The base run is reused.** When the base's fingerprint matches a stored result, the runner reads that result and runs only the head.
- **The mark.** A suite's mark is a committed file, named by suite. It holds a fingerprint of the wrapper's folder, its selection cases and each page it names, taken through `eval_record`'s own hash, which drops the review date and the proof keys, with the model and the tool version. So moving a review date or marking a page proven leaves the mark current. The runner writes it only when every case passed at the head: passing, not merely no worse than the base. A check fails a mark that does not match the tree, in CI and at a push to main; a commit only warns.
- **The gate.** For content a suite's mark or a proven page's record covers, a commit and a push of a branch warn, the pre-push check refuses a push to main, and CI fails a pull request.
- **Machinery paths.** `evals/proof/` and `evals/sources.json` join `direct_push`'s machinery list, as `evals/cases/` and `evals/acceptance/` are on it.
- **Kit classes.** `evals/suites.py` is synced, as `run.py` is. `evals/sources.json`, the suites' stored results and the review's mark store are never synced. The dispatch templates are synced. In an instance, the suite gate does not bind a synced page, as `eval_record` already exempts one.
- **The routing baseline** is recorded once, with its table on the eval page.
- **Q49.** The four fire cases that still miss run again at five turns, about 12 runs. Only a wrapper that still misses is rewritten a second time.

### H3: Proof attempts

The ten: [test first](../playbooks/test-first.md), [debugging](../playbooks/debugging.md), the [throwaway prototype](../playbooks/throwaway-prototype.md), [safe refactor](../safe-refactor.md), the [research ladder](../research-ladder.md), [delegating](../orchestration.md#delegating), the [instruction review](../playbooks/instruction-review.md), [orchestration](../orchestration.md), [parts](../parts.md) and [changing the machinery](../changing-the-machinery.md).

Each attempt runs as M3's slice B7 did. Two cases are drawn from M1 to M3's real work. The page's two-line text is committed before its baseline runs. The baseline is the bare model and the two-line arm, 10 runs each per case, 40 runs a page, run with `run.py --baseline --attempt M4` so its record names the page, the milestone and its verdict. H0b's item 10 makes `--baseline` run both arms into one record. The bare model's cut row below is read first, so a page the bare model already does is cut, as decision 0006 says. Then the two-line screen: a page whose two-line arm passes 17 or more of its 20 baseline runs is not sent to a recording, since at 44 runs an arm a guided arm at 44 of 44 needs two-line at 39 or fewer, and at 40 of 44 at 33 or fewer. That page stays unproven with the baseline as its failed attempt, and its `prove-by` moves to M6, once. Otherwise the bare model's other rows decide, per case.

| The baseline shows | Then |
|---|---|
| The bare model passes 8 or more of 10 in both cases | The page is cut, with the baseline as the reason. A page that holds facts or a rules table loses its procedure steps only, as [decision 0006](../decisions/0006-what-proven-means.md) says. |
| It passes 5 or fewer in one case and 7 or fewer in the other | Three arms are recorded at 22 runs per case, 132 runs, on the maintainer's yes for that page. |
| It passes 5 or fewer in one case and 8 or more in the other | The guided arm cannot beat the bare arm in the second case. That case is replaced by one drawn from real work, its baseline run and counted, before any recording. |
| Anything between | The page stays unproven. The baseline is its failed attempt, and `prove-by` moves to M6, once. |

- **Order.** Debugging's baseline first: its cases exist, and H0b fixes them. Its recording waits with the rest for the maintainer's pick, as Q87 says. Then the pages no M4 slice edits. `orchestration.md`, its delegating section and the instruction review come after L1 and L4, which edit them. Their cases measure the agent tool's own subagent route, which the eval sandbox can run; L1 leaves those pages naming that route and `ws.py dispatch` as equal ways to start a fresh session. `parts.md` and `changing-the-machinery.md` come last, after every slice that adds a part.
- **A stop after the baselines.** Once the ten baselines are in, the slice stops for the maintainer's choice of which pages go to a recording. A page the budget does not reach stays unproven by his decision, with its baseline as the failed attempt, as red team review did in M3.
- **Proven needs a real run too.** A page's `proven-by` names a milestone or fix record of the page used on real work, as decision 0006 says, beside its record. A page no record shows in use stays unproven, whatever its recording.
- **A proven page is gated from then on, and each later edit costs a recording:** 132 a page after M4, or 44 inside the milestone of a full recording, under H0b's item 8. Up to M3's sign-off `parts.md` changed in 55 commits and `changing-the-machinery.md` in 22; the other pages in 1 to 6 (verified, `git log` on main). So the tables of those two move to a reference page before their two-line texts and baselines, in the slice that last edits each page, and the proven part is the procedure alone. Each old heading stays as a one-line pointer to its new page, after M4 too, since `INDEX.md` and four parts link to it; slice Z repoints those links and leaves the pointers, so Z changes no page under an attempt. The test that holds the machinery table equal to `direct_push`'s list changes with the move. The baselines then measure the page a recording would.
- **A case replacement.** The commit that adds the new case and removes the old one is exempt by name from criteria 21 and 30 and the non-goal on editing a page under an attempt. A replacement's baseline, about 20 runs, comes out of the reserve under the stop.
- **A section's cut waits for its page.** `orchestration.md#delegating` shares its page's hash, so its cut waits until `orchestration.md`'s own attempt has its recording or its failed attempt, and lands then.
- **A cut is queued for slice Z,** since it removes index rows: the page's steps, its wrapper and its rows leave in one commit. A cut ends the attempt, so that commit is exempt by name from criterion 30 and from the non-goal on editing a page under an attempt. Removing a cut page's wrapper means editing every other description that names it, up to four, so a cut costs those neighbours' suites, about 6 runs each, up to 24, from the selection reserve.
- A run that dispatches a helper session, as the instruction review's and delegating's cases do, counts each dispatched session toward its batch.

### L0: Facts and prior art

Record each as verified or not under "Results", with the command or the transcript. For Claude Code and for Codex CLI: the command that starts a headless session on a named model and effort; the setting that turns its edit tools off, and what can still write; where the session's transcript is, and what marks its end; how a time limit stops it; how a person's turn in its transcript differs from a tool result or a message the harness adds; how the author's session waits for a reviewer that runs up to 30 minutes; and whether the tool reports a session's token use.

Then test two existing review marks in a scratch repository, made before G3 merges or under a path the manifest names as known, since G3 leaves a git call elsewhere unresolved, against criteria 35 to 40: AI-DLC's `attest`, which ties commits to reviewed work by a content fingerprint and fails closed, and Anthropic's `agent-approval-check`, which requires human approvals on agent commits. Both are named by the program plan; that each exists and does this is inferred until the slice runs them. A decision record says, for each criterion, what each meets, what M4 takes with credit, and what it builds. It also settles where a mark is stored. If one of them meets every criterion of a slice, that slice takes its design, with credit, since no third-party package may join the engine or the parts, and the plan changes by an approved entry.

### L1: Dispatch

`python3 ws.py dispatch TEMPLATE --tier TIER --input NAME=VALUE`. Dispatch records go to one fixed folder under `docs/records/reviews/`, which the guards protect and `collect` reads.

- **The prompt is the template file with its placeholders filled, and nothing else.** The rule that a critic never gets the author's reasoning is then held by the tool, where today it is prose. The first line names the tier. The model and the effort come from the manifest's binding, and a dispatch never runs below the tier its template names.
- **One template file per recurring brief:** the review dimension at the driver tier, an advisory dimension at the worker tier, the review re-check at each tier, the red team, the instruction review and its re-check, and the teach-back grader. A playbook still shows its template; a check holds the page's copy equal to the file.
- **A review's pre-pass runs first:** the build, lint and format commands at the merge base and at the tip. On your own branch a new error or warning stops the review.
- **One session per dimension per tip.** `ws.py dispatch` refuses a second session of a dimension at a tip once its first reply was closed; only a reply with no closed report gets its one retry. `collect` reads every dispatch record for the branch since the last mark, and `review mark` refuses while any is not collected.
- **One retry** for a reply with no closed report, and a limit of 30 minutes per reviewer, the limit [decision 0020](../decisions/0020-where-the-sources-disagreed.md) chose and no page yet holds.
- **A dispatched session starts clean.** `ws.py dispatch` starts it with project settings only, as `run.py` does, so the person's user-level settings, hooks and memory do not load, and sets a variable the session-start runner reads to skip `handoff_loader`, so no author's note reaches it. A reviewer starts in a clean worktree at the tip; the red team writes its record there, and the dispatch copies it back. A case shows a dispatched session's transcript holds no handoff text.
- **A reviewer starts with its edit tools off,** as L0 found possible, so "edit nothing" is held by the launch. The red team is the one exception: it starts able to write, writes its own record as red team review says, and the dispatch writes no record for it. A check after it ends refuses any other file it changed.
- **One adapter per agent tool:** a function that builds the command, and one that reads recorded output. The tests need no agent.

**A review scales to its diff.** The dispatch picks a full round's dimensions from the paths the range changes, and prints why:

| The range changes | A full round starts |
|---|---|
| Guidance pages, plans or records only | Nothing. The instruction review's trailers hold guidance. |
| Tests or eval cases only | Code and test adequacy. |
| A pin bump under `src/` only | Code, over the pinned repository's range between the two pins. |
| Any other machinery path, or code under `src/`; or a range that mixes rows | Code, architecture, security and test adequacy. Reuse, when the range adds a file or a function. Docs drift and the other triggered dimensions, as their triggers say. |

- **A fix round runs less.** On a delta round the dispatch starts code over the delta; security, when the delta changes a hook, a guard, a check or CI; each dimension that has a finding from an earlier round; and the re-check of the rows marked fixed. The whole-branch pass runs once, at the tip that is to get the mark.
- **Advisory work runs a tier lower** (Q91). Reuse and docs drift run at the worker tier always: their findings never block, so a gate change does not raise them. The re-check runs at the worker tier too, and at the driver tier when the range changes a gate, which is a check, a hook, a grader, CI or the commit hook. The review orchestrator's page and [orchestration](../orchestration.md) say so, where both call every review driver work today.
- **It counts review sessions.** Every session a dispatch starts for a review is one: a dimension, a retry, a re-check, a whole-branch pass, an instruction review, a red team, a teach-back grader. Each dispatch record holds its tier, model, effort and duration, and its token use where the agent tool reports it.
- **A pull request has a cap.** The `review_gate` part's entry in the manifest sets the most review sessions one pull request's code review may start: 16 here, and the same in the kit. The cap counts dimensions, retries, re-checks and the whole-branch pass. An instruction review of the pull request's pages counts toward the milestone's total, not the cap. At the cap the dispatch refuses and names the count. The loop stops for the person, who raises the cap for that branch or ends the review. `python3 ws.py review status` prints the branch's count against the cap.

The estimates behind the cap are under [review session budgets](#review-session-budgets).

If a tool cannot be driven this way, dispatch ships for one tool behind its adapter, and the README marks the review gate "one tool". That is the program's rule, and not a stop.

### L2: The completion record

- **Only a dispatched session counts.** Each dispatch record holds the hash of the exact prompt it sent and the session's id. `collect` accepts a transcript only when its first message hashes to a dispatch record's prompt and its session id matches. A session the author starts or briefs by hand does not count. The dispatch record also holds the session's end and a hash of its transcript then; `collect` refuses a transcript with a person's turn after the prompt, as L0 records a person's turn for each tool, or one that changed after that hash. `review_gate` refuses an agent's resume or continue of a session a dispatch record names. The template's fixed lines are held by the tool. Each placeholder of each template has a type the dispatch checks: a commit range, a path, a list of paths, a date, a value from a fixed set such as a dimension's name or `fix` or `other`, a record row by its number, or text read from a file named by path. The request comes from such a file, such as the plan or an issue saved there, and so does the reuse line, from the file the reuse checklist writes; no placeholder takes free text the author types. The completion record keeps each placeholder's value, where the person and the re-check read it.
- **Judged from the reviewer's own words.** `python3 ws.py review collect` reads each reviewer's transcript through the adapter. A dimension is complete only when its reply holds a closed report for this tip, a count of findings equal to the table's rows, and the lines its dimension owes. For architecture those are `Invariants checked:` and `Big picture:`, and one alone does not count.
- **It writes two things for the tip:** the completion record, and the findings table in the form [the review orchestrator](../playbooks/review-orchestrator.md) gives. The completion record counts the round's sessions: started, retried and not complete.
- **A delta round re-checks every earlier row marked fixed,** in a fresh session.
- **Before a branch is called ready, one pass reads the whole branch,** not only the last delta.

The fix brief's mechanism and fix-seam fields point at architecture review's restate step and its look-past-the-repository step. That edit is to a hashed page, so it is queued for slice Z.

### L3: The review mark and the gate

- **`python3 ws.py review mark` refuses unless all of these hold.** The tree is clean but for the review's record paths. The reviewed commit is the remote's tip, or an ancestor of it whose later commits change only record paths. A findings record names the reviewed commit. The completion record is complete. A whole-branch pass exists. No row of a blocking severity, from any round, is still `open`, so a round that reports a new blocking finding cannot be the marked round. The findings record holds every row the completion record counts for each reviewer, so a row deleted before the mark is caught. Every declined security or architecture finding names a tracker key, or an acceptance with a developer's initials and an ISO date. A decline that names a key shows, by a quote or a comment id, that the ticket will remove the finding.
- **It has no mode that takes the caller's word.** The writer reads the completion record, and only the collector writes that, from transcripts.
- **The guards protect the evidence.** The edit guard and the shell guards refuse an agent's write to the dispatch records, the completion records, the findings records' rows the collector wrote, the mark's store, and each agent tool's session transcript files that the adapter reads, as they refuse a write into a git folder. They name the transcript files, such as Claude Code's `*.jsonl` session files, not their folder, so the tool's memory files beside them stay writable. Only `ws.py dispatch`, `ws.py review collect` and `ws.py review mark` write the first three, and the agent tool itself writes the transcripts. What an interpreter writes stays out of reach, as the README's limits say for every guard.
- **`python3 ws.py review status`** answers `reviewed`, `delta` when an ancestor holds the mark, `rebased` when another commit with the same patch id holds it, or `none`.
- **`review_gate`, before a shell command.** It refuses `gh pr create` without `--draft`. It refuses that command, and a `gh api` call that creates a pull request, when the range changes a machinery path or code under `src/` and the pushed tip has no mark. A range of guidance pages alone needs none: the instruction review's trailers hold it. A command it cannot resolve is refused, by G2's rule.
- **No new top-level manifest key.** The engine refuses any top-level key but `version`, `tiers`, `parts`, `retired` and `building`, so the cap, the merge policy and the eval model each live in a part's entry.
- **The fix path until slice Z.** `fix-a-bug.md` is frozen until Z, and its step 5 opens a draft pull request. From L3's merge, `review_gate`'s refusal of that draft names the review orchestrator and the command that marks the tip, so the refusal itself is the route until Z edits the page.
- **The gate holds at publish and merge too.** A hook cannot map a pull request's number to its head within its budget, so the checks live in two commands. An agent publishes with `python3 ws.py ready NUMBER` and merges with `python3 ws.py merge NUMBER`. Each reads the pull request's head with `gh`, as `ws.py merge` does today, and refuses when the range changes a machinery path or code under `src/` and the head's `review status` is not `reviewed`. `review_gate` refuses an agent's `gh pr ready` and `gh pr merge` in favor of them. When the range changes a machinery path or code under `src/`, CI fails a pull request whose head has no mark, or a mark whose fingerprint, which leaves out the record paths, does not match, computed at the pull request's head commit, not the merge with main. CI's mark and suite steps, `ws.py ready` and `ws.py merge` run the check's code from the base commit against the head's tree, as the pre-push hook takes its parts from the remote's tip, so a pull request that weakens a gate is judged by the gate it would replace. The README names what stays: a pull request that changes the engine those checks load. A pull request that changes the mark's format or how its fingerprint is taken is read by the base's reader as having no mark, so a person merges it after its own review, and the README names that too. CI's workflow runs from the pull request itself, so `ws.py ready` and `ws.py merge`, from base code, refuse an agent's publish or merge of a range that changes `.github/workflows/`; a person merges it after its own review, and the README names the workflow file beside the engine. CI cannot read the transcripts, which stay on the author's machine.
- **A forged mark reads `none`:** one edited by hand, copied from another commit, or with no completion record behind it.

The mark is keyed by the tip and by the branch's patch id. The gate reads it in the same clone, and a real change's mark and completion record are published with its pull request.

**Scope: this repository.** M4's mark, `review_gate`, `ws.py ready`, `ws.py merge` and the merge policy cover the workspace's own repository, whose `origin` `ws.py merge` acts on. A pull request in a pinned repository stays as the program has it: an agent opens a draft and a person does the rest, so the refusals of an agent's `gh pr ready` and `gh pr merge` there hold. A review loop for a pinned repository's pull requests waits for M6, which first runs the loop on upstream fixes. The README says so.

**A record-only commit keeps the mark.** L3 adds a CI trigger on every pushed branch, so the three systems pass before a review starts and a CI fix rarely follows a mark. The mark and suite steps run on `pull_request` events only, so a push before the review is not red for want of a mark. A branch's first push checks its commits against the merge base with main, since the push event names no earlier commit. H0b's branch is red on `eval_record` until R3 is in, as its `--no-verify` commits expect. A merge from main keeps the mark when the merge commit itself changes nothing beyond what main brings, with no conflict resolved, as `git diff` of the merge against main's side shows. A person accepts a `rebased` mark with `python3 ws.py review accept`, run from a terminal, where no hook runs; `review_gate` refuses an agent's run of it. The order is: collect writes the findings and completion records; they are committed and pushed; `review mark` writes the mark for the reviewed commit; the mark is committed and pushed. The mark's store and the completion records live under `docs/records/reviews/`, so every commit after the reviewed one is a record-only commit. A review's record is committed on the branch it reviewed (L7), which makes a new tip. `review status` reads that tip as `reviewed` when every commit after the marked one changes only the review's own record paths, the plan's file under `docs/plans/` and files under `docs/records/`, and run records under `evals/runs/` and `evals/selection/` that CI's re-grade passes, which `review status`, the fingerprint and CI all leave out, or is a merge from main that resolves no conflict. Any other change makes it `delta`. The mark's fingerprint is taken over the branch's patch against its merge base, so a clean merge from main leaves it matching. The gate reads `review status`, so the pull request opens at the record's commit. A test covers a record-only commit, and one that also changes a line of code.

### L4: The finding lifecycle

The rules go on [the review orchestrator's page](../playbooks/review-orchestrator.md), each tagged with what enforces it.

- **Verify before fixing.** The author checks a finding against the code before acting on it.
- **"Fixed" names the check that fails without the fix.** A row marked fixed with no check named stops the mark.
- **A decline names where the defect now lives,** and a decline rests on a search of the whole code, not a part of it. A deferred row names an open row of the [defect register](../records/defects.md).
- **A direction rule replaces a round count.** Rounds go on while each round's findings are fewer or narrower than the last. A round that widens the change stops for the person.
- **At most five nits are reported to the person,** and the rest are given as a count. Each reviewer's reply and the findings record keep every row, so L2's count and L3's row check hold. The template draws a written line between a finding that blocks and one that does not.
- **The cross-check.** `python3 ws.py defects check` fails a deferred finding whose register row is closed or missing. Until M8 it reads the register's file only.

### L5: Teach-back

`docs/playbooks/teach-back.md`, a playbook, `proof: unproven`, `prove-by: M6`. L5's pull request widens the `wrappers` part's code and cases so a waiting entry may name any later milestone, then adds teach-back's entry for M6 and moves the review orchestrator's to M6, so the check passes with no wrapper. This lands before H3 reaches `parts.md`.

- **What it is.** Before a person approves a plan, or publishes a pull request in a `person` repository, they explain it in their own words. A fresh session, sent the grader template through L1, grades the explanation against the plan or the diff, and against the plan's "Decisions made without asking". It asks follow-up questions only where the explanation had gaps.
- **The mark.** The person runs `python3 ws.py teach-back` in a terminal, where no hook runs: it takes their explanation, dispatches the grader, and takes their answers to its follow-ups there, so neither passes through an agent's session. The answers go to a second dispatched session, whose typed placeholders hold the first session's questions and the person's answers, read from a file the command writes; both sessions are bound as L2 binds a reviewer's. `review_gate` refuses an agent's run of it. The mark records `passed` or `skipped` at that commit, beside the review mark, read from the grader's transcript, bound to its dispatch as L2 binds a reviewer's. A skip is given the same way, with its reason. The guards protect its store as L3 protects the review's. Committing the mark is a record-only commit, so the teach-back mark, like the review mark, still counts at the new head.
- **It scales to size.** A change that passes [the size gate](../size-the-work.md#the-gate) gets one question, or a recorded skip with its reason.
- **It checks the owner of the change, never its reviewers.**
- **Fresh source.** Builders work from this description. Nobody building it opens the maintainer's private skill.

### L6: Merge policy

- **`merge_policy` in the `review_gate` part's manifest entry** maps a repository, named as the outward-write list names it, to `agent` or `person`.
- **`agent`:** agents publish and merge after CI passes, and teach-back runs at plan approval only.
- **`person`:** an agent opens drafts, and may publish one only with a passed teach-back mark at the head commit; `ws.py ready` refuses without it. `review_gate`, which sees an agent's command line, refuses an agent's `ws.py merge` there; a person's `ws.py merge` from a terminal passes, since no hook runs there. A person or human reviewers merge.
- **No entry means `person`.** This repository's entry is `agent`, as the maintainer has allowed since M1. The kit seeds none, so an adopted instance starts as `person`.
- **The policy never widens where agents may write.** `outward_write` still decides that.

### L7: Small pieces

- **`lifecycle_map`,** a check with cases. It fails a playbook or how-to with no row on the [lifecycle map](../lifecycle-map.md), and a row that links an archived page.
- **Red team review's second form** (the red team's finding 10): what a red team is sent for a milestone's outside check, that it may re-run the commands the record cites, and that it writes its record and commits nothing. The page stays thin, and gains no method.
- **Handoff's keep mode** (Q35): where a tracked copy of a note lives, and the rule that a path on the author's machine is flagged.
- **One rule for a review's record** (Q41): a record about a branch is committed on that branch and reaches main with its pull request. [Procedure endings](../procedure-endings.md) states it once, and the three known defects M3's review records list are fixed against it.

### Z: Contract, index and recordings

- **The queued edits,** from the list under "Results". `AGENTS.md` routes a branch to its review before its pull request, names the merge policy in its pull-request rule, and names the push in its eval rule. `INDEX.md` gains a row for each new page, part and chain, and the lifecycle map's row, which has waited since M3. `fix-a-bug.md` gains the review gates and the fix brief's two fields. Each new gate on a page the guided arm is given names when it applies, such as a remote and the review machinery being present, as step 5's pull request does today, and Z's instruction review checks that a run in the eval scaffold can still finish the page. The definition of done names the review mark. Each cut from H3 is made here.
- **Pages that still say "waits for M4".** Each slice that builds a piece edits the pages that name it as planned: L3 `docs/changing-the-machinery.md`'s step 6 and its rule on `gh pr merge`, which `ws.py ready` and `ws.py merge` replace, `docs/code-review.md`, `docs/playbooks/git-host-operations.md` and `docs/playbooks/README.md`; L1 `docs/playbooks/architecture-review.md` and `docs/playbooks/reuse-checklist.md`; L4 `docs/playbooks/escape-analysis.md` and `docs/playbooks/feedback-walkthrough.md`; H2 `docs/maintain-the-workspace.md` and `docs/extend-the-workspace.md`. Each edit takes its instruction review in that slice. Slice Z re-runs V8 and fixes any line left. Their suite runs sit inside the later pull requests the selection budget already counts.
- **The version** goes to 0.5.0, the engine's and the manifest's in one step.
- **R4,** the guided arm alone, 45 runs: slice Z changes only files the guided arm is given, so H0b's item 8 applies. Then, in a second batch, the routed arm: 45 runs to a new one-time arm, `routed-m4`, so M3's `routed` records stay as they are. An arm that misses its margin is recorded once more, 45 runs, and judged pooled.
- **The records:** `docs/milestones/m4.md`, the changelog and the evidence page at M4's numbers, written before the outside checks run. M3's red team found all three stale.

### Names this plan fixes

Settled before any page or part is written. A builder who finds a name wrong proposes the change in its report, and does not rename alone.

| Name | What it is | Rejected, and why |
|---|---|---|
| Review mark | A record that a review completed on one commit's content. | "Attestation": in common use that is a signed statement, and this mark is not signed. |
| Completion record | For one reviewed commit, which dimensions completed, read from the reviewers' output. | "Manifest", the word the review page uses today: the glossary gives it to `workspace.json`. |
| Review gate, `review_gate` | The guard that refuses a pull request with no mark. | "Pull request gate": it also judges the publish command. |
| Teach-back | A person explains a change back before approving or publishing it. | "Comprehension check": teach-back is the term already in use for this method. |
| Merge policy, `merge_policy` | Who may publish and merge in one repository: `agent` or `person`. | "Branch policy": a git host uses that for its own rules. |
| Suite | The cases that belong to one page. | None considered. |
| Outcome case | A case graded on what the agent left behind. | "Quality case": it grades an outcome, and says nothing else about quality. |
| Batch | Every eval run started under one yes from the maintainer. | "Session", which M3's cap used and a builder read three ways. |
| Review session | One fresh session a dispatch starts for a review, a re-check, an instruction review, a red team or a teach-back. | "Reviewer": one reviewer may take two sessions, a first and a retry. |
| Dispatch template | The fixed text a fresh session is sent. | "Prompt template": the pages already say dispatch. |

New pages: `docs/playbooks/teach-back.md`, as L5 gives it; one decision record each for the guards' rule, the review mark, the merge policy and teach-back; and the two reference pages H3 moves `parts.md`'s and `changing-the-machinery.md`'s tables to, with their how-to index rows in the same commit and their `INDEX.md` rows queued for slice Z. Everything else is an edit to a page that exists.

## Success criteria

Criteria are numbered in the order they were added, so a later one may sit beside the slice it belongs to.

Sub-batch G:

1. `building` in the manifest is `["M4"]`. When `building` names a milestone whose record has `status: signed off`, the `proof` check fails. `git check-ignore -q .env` exits 0. (V2)
2. When a push holds a guard change that turns a passing case into a refusal, the pre-push check judges it without `--no-verify`: the cases it runs and the library they call come from one commit. (V1)
3. When `ws.py merge` merges a pull request whose branch is the base of open pull requests, it retargets each to the merged one's base before it deletes the branch. When a retarget fails, it deletes nothing and says so. Its tests run on recorded `gh` output. (V1)
4. The shell guards never pass a command in which a word that decides what runs, or what it acts on, is not literal. Each line "G2" names is refused, with a case. (V2)
5. The rule lives in the parser. No part file and no second library file holds a copy of it, and the test that held two copies equal is gone. (V1)
6. When a command runs under `ws.py with-secrets`, each guard judges the wrapped program as it judges any command. (V2)
7. The lines that must keep passing each have a case: the heredoc commit and pull-request idioms, `cd "$D" && make`, `ls *.md`, `which git`, `grep -n git notes.txt`, `command -v git`, `grep -rn 'git push -f origin main' docs`, `echo 'git push --force origin main'`, `python3 -c "import json; print(1)"`, `awk '{print $1}' notes.txt`, `jq '.tiers' workspace.json`, `find . -name '*.py'`, `git log --oneline | head -5`, `curl -s 'https://example.com/v1/jobs?content=true'`, `tr '[:upper:]' '[:lower:]'`, `git reset --hard HEAD@{1}`, `GIT_EDITOR=true git rebase --continue`, `git -C src/REPO log` in a workspace with a pinned repository, and `D="$TMPDIR/old" && mkdir -p "$D" && git show HEAD:src/x.py > "$D/x.py"`. `cp`, `tee` and `sort -o` into a git folder are refused. Each line that round 1's record, `2026-11-26-m4-fail-closed-guards-review-loop-and-evals.md`, names in its finding 4 is refused, with a case. (V2)
8. After G2, G3 and G4 each, `python3 evals/grade.py --recorded` finds no difference, and the slice's report lists every stored eval command whose answer changed. (V3)
9. When a git call sets or writes a setting that is not on the allow list, the guards refuse it and name the setting. A case covers `-c`, `GIT_CONFIG_*`, an environment variable and `git config`. (V2)
10. When a git option takes a command, the guards judge its text as a command line, with a case for each option "G3" names. A remote whose transport is not on the allow list is refused. (V2)
11. Each route "G4" names is refused, with a case; each person-only command is refused under `ws.py`, `wslib/launch.sh` and `wslib/start.py`, and by the command itself under the agent tool's marker; writing `config` before `HEAD` and the reverse among them; a write in a repository whose root holds a `config/` folder passes. When a repository is named only in the list kept outside the repository, `outward_write` allows a write to it from the main copy and from a worktree, and `outward_list` refuses an agent's edit to that file. (V2)
12. A command that names a path inside a git folder, or the outward-write list, passes only for a program on the readers' list. `python3 tests/hook_cases.py` holds every hook row under its budget. (V2, V7)

Sub-batch H:

13. When only grading files change and a re-grade finds no difference, `eval_record` passes after the stamp. When a grade differs, it fails until the case is recorded again. CI recomputes the grader hash from the grading files and fails a record whose stored grader hash differs. (V1, V3)
14. `eval_record` fails a record whose arms ran on different models, or on a model other than the full id the manifest names for evals. `run.py` takes its model from the manifest. (V1)
15. `run.py` passes the placeholder's path written in quotes, and refuses `/home/user/../bob/x` and the placeholder in another letter case pointing at another folder. A case covers each. (V1)
16. Debugging's fixture names `/home/user`, and the transcript test lists no stored transcript as stale. (V1)
17. `run.py` never starts a run past its batch's count. A batch spans calls, and probes and failed runs count. When the usage file shows a reading over the limits, `run.py` refuses the batch; with no file it runs; with a stale file it refuses unless the batch allowed it. (V1)
18. `run.py --rerecord` takes a one-time arm and keeps its first batch, and `pool.py` prints one-time arms. (V1)
19. `eval_record` gates a proven page anywhere under `docs/`. `proof` fails a proof key on a page whose kind carries none. (V2)
20. R3 passes the gate. Its guided arm passes no more than 3 runs fewer, pooled, than R2's 42 of 45, or than the anchor's 40. After one re-record, the pooled 90 pass no fewer than 78. (V3)
21. After R3's commit, no commit before slice Z changes `evals/run.py` or `evals/proofkeys.py`, or the part of `parts/eval_record.py` that builds a hash, and no case file under `evals/cases/` moves, except in a case replacement's commit (H3). A test fails one that does. (V1)
22. Every page with a wrapper has a suite. Every outcome and routing case names the real work it was drawn from, and a check fails one that names none. (V2)
23. The suite runner picks a suite when its wrapper, its cases or any page its wrapper names changes. It runs the base and the head, reruns a pass-to-fail case twice, and exits 1 only at two failures of three. Its tests run on recorded output. (V1)
24. The runner writes a mark only when every case passed at the head, a selection case passing at two of its three runs. A check fails a mark whose fingerprint does not match the tree. Content whose suite has no mark fails the gate, unless its wrapper is on the manifest's list with a reason and a milestone. (V1, V2)
25. For content a mark or a proven page's record covers, a commit warns, the pre-push check refuses a push to main, and CI fails a pull request. (V1, V4)
26. The routing suite has a recorded baseline under `evals/`, and the eval page shows its table. (V6)
27. The four fire cases ran again at five turns, and the result is recorded either way. (V6)
28. The first command under V8 prints nothing. Each of the ten pages is proven, cut, or unproven with a failed-attempt record made while M4 was in `building`. (V2, V8)
29. Each attempt's two-line text was committed before its baseline, and its baseline and recording ran in separate batches. (V3)
30. No commit after a page's first attempt record changes a file that attempt's cases hash, except a cut's commit or a case replacement's commit, each named as one. A test lists each case's files and fails one that changed. (V1)
48. The plan template, red team review and size the work each say a plan's triage may live in each linked record. Both red team cases' hidden tests pass a run whose dispositions are in the record, and one whose dispositions are in the plan's table. (V1, V2)

Sub-batch L:

31. "Results" holds L0's facts, each marked verified or not. A decision record on the review mark passes the `decisions` check. (V2)
32. A dispatch's prompt differs from its template only inside the placeholders, and a test fails one that differs elsewhere. A placeholder whose value does not match its type is refused, and the completion record holds every value. Its first line names the tier, and its model and effort are the binding's. (V1)
33. A reviewer starts with its edit tools off. A reply with no closed report gets one retry. A reviewer past 30 minutes is stopped and counted not complete. (V1)
34. Each recurring brief is one template file, and a check fails a page whose printed template differs from its file. (V2)
35. A dimension counts as complete only on the reviewer's own output. A recorded architecture report with one of its two lines is counted incomplete. (V1)
36. A delta round re-checks every earlier row marked fixed. A branch with no whole-branch pass gets no mark. (V1)
37. `ws.py review mark` refuses in each case "L3" lists, with a test for each, an open blocking row, a deleted row and a second dispatch of one dimension at one tip among them. A decline with neither a tracker key nor initials and a date is refused. (V1)
38. A recorded run shows a forged mark read as `none`: one edited by hand, one copied from another commit, and one with no completion record. The guards refuse an agent's edit-tool and shell writes to the completion records, the mark's store and the transcript folder, with a case for each. (V1, V2)
39. `ws.py review status` gives each of its four answers, with a test for each. A tip whose commits after the marked one change only the review's record paths reads `reviewed`; one that also changes any other path reads `delta`; a clean merge from main reads `reviewed`, and one with a resolved conflict reads `delta`. (V1)
40. CI runs on a push to any branch, and its mark and suite steps run on pull requests only; CI passes at a head whose commits after the mark are record-only, and asks no mark of a range of pages alone. A recorded run shows `gh pr create` refused for lack of a mark, then allowed once the mark is there. Without `--draft` it is refused. After a code commit is pushed past the mark, `ws.py ready` and `ws.py merge` are refused, and CI fails the pull request. A transcript from a session no dispatch record names does not count, and neither does one resumed after its dispatch; a reviewer whose transcript holds tool calls counts. The hook's row stays under 200 milliseconds. (V1, V7)
41. The mark writer refuses a row marked fixed that names no check, and a declined row that names no home. `ws.py defects check` fails a deferred finding whose register row is closed or missing. (V1)
42. A recorded review with more than five nits reports five and a count to the person, while its findings record keeps every row. (V1)
43. Teach-back has a recorded run on one plan, the first awaiting approval after L5 merges, or a dated change entry to this plan if none comes first, and on one pull request, each with its mark at the commit, and one trivial change with a recorded skip. `ws.py teach-back` writes no mark with no dispatched grader's transcript behind it, and a grader with a follow-up passes through its second session. (V1)
44. In this repository, not in an instance, every repository the tracked list `outward-repos.json` names has a `merge_policy` entry, though only this repository's entry acts in M4, and no entry names a repository from the list kept outside the repository, and a repository with none reads as `person`. An instance the kit makes has no entry. (V2)
45. In a `person` repository, a recorded run shows an agent's `ws.py ready` refused without a passed teach-back mark at the head commit, and allowed with it. An agent's `ws.py merge` is refused there. In every repository, an agent's `gh pr ready`, `gh pr merge 5`, `gh pr merge 5 --merge` and `gh api -X PUT .../pulls/5/merge` are refused. (V1)
46. `lifecycle_map` fails a playbook or how-to with no row on the map, and a row that links an archived page. (V2)
47. Red team review states its form for a milestone's outside check. Handoff states keep mode. Procedure endings states where a review's record is committed. Each edit names its instruction review. (V2)

Closing:

49. `AGENTS.md` routes a branch to its review, and names the merge policy and the push gate. `loaded_size` passes at both ceilings. `INDEX.md` has a row for each new page, part and chain. (V2)
50. R4 passes the gate. Its guided arm passes no more than 3 runs fewer, pooled, than R3's or the anchor's. (V3)
51. The routed arm passes at least R4's guided count less 3; after one re-record, the pooled 90 pass at least twice that count less 6. The eval page reports every measurement. (V3)
52. No page still says something waits for M4. The command under V8 prints nothing. (V8)
53. From L3's merge on, every pull request of this plan that changed a machinery path or `src/` had a mark at its head when it was published. `docs/milestones/m4.md` lists each. (V4)
54. The private port ledger maps every catalog item it gives M4 to a page, a part, a later milestone or a reason. Its check prints 0 unmapped items. (V5)
55. Every pull request of this plan merged with every required check passing on Linux, macOS and Windows, except one that changes the mark's format or the CI workflow, which a person merges after its own review, as L3 says; the milestone record names each. (V4)
56. `docs/milestones/m4.md` marks each criterion with its evidence, and reports the eval runs used per slice against its budget, the review sessions used per slice against its estimate, the always-loaded size and the outside checks' outcomes. (V2, V9)

Sub-batch L, review sessions. They are numbered after the closing criteria because they joined the draft later:

57. When a range changes only guidance pages, plans or records, the dispatch starts no dimension. When it changes only tests or eval cases, it starts code and test adequacy. Otherwise it starts the four, and reuse and each triggered dimension only when its trigger holds. A test covers each row. (V1)
58. On a delta round the dispatch starts code, security when the delta changes a hook, a guard, a check or CI, each dimension with an earlier finding, and the re-check. A mark needs one whole-branch pass at its tip, and no more. Reuse and docs drift start at the worker tier. The re-check starts at the worker tier, and at the driver tier when the range changes a gate. (V1)
59. `ws.py dispatch` never starts a review session past the manifest's cap for a pull request, and its refusal names the count. Each dispatch record holds its tier, model, effort and duration. `ws.py review status` prints the branch's count against the cap. (V1)

Added on the maintainer's answers of 2026-11-26, numbered as they came:

60. When only the files one arm is given change, `eval_record` asks for that arm alone, and passes once that arm is recorded again on the same model. When a file every arm shares changes, the model, or the arms' milestones differ, it asks for every arm. A test covers each. (V1)
61. H0a's commit holds no new run. It migrates only the records current under the old hash at its base, and a record stale there stays stale. A test shows this, and that no file an agent is given changed. After H0a, a change to a grading file alone passes `eval_record` once `grade.py --recorded --stamp` finds no difference. (V1, V3)
62. Each row F1 to F33 under "Force-push routes, numbered", except F27, which is out of reach, has a case under its row's name. The case is refused by the slice that row names, and was allowed on that slice's base, except F28's, which is refused at both. (V2)
63. `run.py --baseline` runs the bare and the two-line arms into one baseline record at a path named by its milestone, naming the page, the milestone and the verdict `not proven`, with a test; a page whose case holds an M3 baseline can move its `prove-by` on its M4 one. H3 sends no page to a recording whose two-line arm passed 17 or more of its 20 baseline runs. (V1)


## Verification

- **V1:** `python3 -m unittest discover -b tests` passes, including the test each criterion names.
- **V2:** `python3 ws.py selftest`, `python3 ws.py check` and `python3 -m unittest discover -b tests` all exit 0.
- **V3:** `python3 evals/pool.py` prints each comparison. `python3 evals/grade.py --recorded` and `python3 ws.py check --phase ci` pass.
- **V4:** `gh pr checks NUMBER` shows every required check passing.
- **V5:** the private port ledger's own check, run on the maintainer's machine, prints 0 unmapped items.
- **V6:** the results `claude plugin eval` wrote are committed under `evals/`, and the suite runner prints its verdict from them.
- **V7:** `python3 tests/hook_cases.py` passes, with every row under its budget.
- **V8:** each of these prints nothing. `git grep -n -E 'prove-by:? M4' -- README.md docs ':(exclude)docs/plans' ':(exclude)docs/records' ':(exclude)docs/milestones'`. And `git grep -n -i -E '(until|waits? for|planned for|lands in) M4|M4 (plans|builds)' -- README.md AGENTS.md INDEX.md evals/README.md docs ':(exclude)docs/plans' ':(exclude)docs/records' ':(exclude)docs/milestones' ':(exclude)docs/decisions' ':(exclude)docs/question-log.md'`.
- **V9:** the private attack scripts, run on the maintainer's machine from outside the repository, against a fresh clone of main.

## Recovery

Halt and report. Do not work round a failing case, and do not loosen a check to pass. If a hook locks the session out, stop; the maintainer repairs it from a terminal, as [changing the machinery](../changing-the-machinery.md#traps) says. If a slice finds that a later slice's criterion is wrong, it proposes the revision in its report, as the template's rule 7 asks.

## Stop rule

**A finding stops a slice only when the slice caused it.** A re-check or a review sorts each finding first:

- **Caused by the slice:** a line that was refused at the slice's base and passes at its tip, a page the slice made false, or a defect in what the slice added. It is fixed inside the slice, and it counts toward the fix-round limit.
- **Already open on main:** the same line, read at the slice's base, behaves the same. It is not a stop. It gets a case that shows it, a row in the [defect register](../records/defects.md) and, for a guard, a line in the README's Limits. The slice goes on. It is fixed in the slice only when the fix fits the round in hand.

For a guard, blocking means what the private attack scripts' report means by it: a route that lets an agent write into a git folder, another person's repository or the outward-write list, or force-push or delete the default branch.

Stop the plan and report when any of these happens:

- A slice goes past two fix rounds on a failure it caused.
- R3 fails criterion 20, or R4 criterion 50, after the one re-record a margin miss allows. Publish the result and stop.
- The routed arm fails criterion 51 after its one re-record. Publish the result and stop; the new index rows stay out until a person decides.
- After R3, a slice needs a change to a file criterion 21 names. That costs a recording, so the maintainer decides.
- **The fallback (Q102).** H0a cannot migrate the stored records with no new run, or a re-grade after G2, G3 or G4 changes a stored grade. The guard slice stops before it merges. The maintainer then decides between giving the parser fix its own recording, the three fix-a-bug cases at 135 runs, so it merges first, and holding it until R3.
- The eval runs reach 1,400 agent runs, or the selection and routing runs 400. Re-records, probes, failed runs and dispatched sessions count.
- A slice's batch is used up before its "Done when" holds.
- The review sessions reach 250, counted as [review session budgets](#review-session-budgets) says.
- G2's measure shows it refuses a line agents need and no wording of the rule passes it.
- L0 finds that an existing review mark meets every criterion of a slice. The plan changes by an approved entry before that slice is built.
- The engine, a part or a CI test needs a third-party package.

A part that cannot be made safe on Windows within its slice ships for macOS and Linux, says so in the README, and does not weaken the guard. A review loop that cannot be made tool-neutral ships for one tool. Neither is a stop.

A pull request that reaches its cap of review sessions stops its own loop for the person. That does not stop the plan.

## Limits

- Each slice is built in its own worktree under `.claude/worktrees/`, on its own branch from the remote's main. No builder checks out a branch in the main working copy.
- A slice gets at most two fix rounds on a failure it caused. A fix that touches a shared rule re-reads every page that holds the rule, and its re-check covers them.
- An eval or selection batch starts only on the maintainer's yes for that batch, with a run count, except Q105's: an agent runs a pull request's wrapper suites itself, up to 12 runs. A batch holds at most 150 agent runs, dispatched sessions included, so a dispatching page's recording runs as two batches, each with its own yes. After a usage limit, a person or a session reruns with `--resume`; nothing restarts on its own.
- H0b's commits use `--no-verify` until R3's records are in; H0a's need none. Before each push of that branch, every commit passes `python3 ws.py check --commits origin/main..HEAD` and the deny-list scan. After G1 merges, no push uses `--no-verify`: a push the hook refuses is a stop.
- Agents push the branch, open a draft pull request, and publish and merge it once every required check passes.
- Unattended runs are limited to eval and selection batches, the sessions a dispatch starts, and L0's recorded tool runs. None of them may push to main, publish or merge.
- Builders read the private port catalog and ledger, and nothing of the work workspace. A builder that needs more asks for a walled reader.
- A file a shell or a script writes is recorded with `python3 ws.py ledger --add PATH` before it is staged. A new part's row in decision 0004's table lands in the same commit as the part.
- Maintainer setup before H1: `gh auth status` passes and the Claude Code command line tool is signed in. Before L0: Codex CLI is signed in.

## Eval run budgets

Runs cost the maintainer's usage quota. Each figure is a ceiling to plan by, never an approval: every batch still needs his yes with its count. M3 used 611 agent runs and 249 selection runs.

| Slice | What runs | Planned | With every re-record |
|---|---|---|---|
| H1 | R3: three cases, three arms, 15 runs each | 135 | 180 |
| H3 | Baselines for the ten pages, bare and two-line, 40 each | 400 | 400 |
| H3 | Recordings, 132 a page; five pages planned, picked after the baselines | 660 | 660 |
| Z | R4, the guided arm alone | 45 | 90 |
| Z | The routed arm | 45 | 90 |
| | **Agent runs on the small model** | **1,285, or about 1,405 if the three dispatching pages' baselines cost twice** | **1,420** |

- **The stop is 1,400 agent runs, staged (Q87).** If all ten pages went to a recording, the total would be about 1,945, or 2,080 with every re-record. With every re-record, the five planned recordings reach 1,420, past the stop, so a margin miss in R4 or the routed arm stops for the maintainer. If the three dispatching pages' baselines cost twice, the planned total is about 1,405 before any re-record; the maintainer's pick after the baselines then holds back slice Z's 90 runs, 180 with re-records, and a case replacement may find no reserve left. The maintainer chooses the pages after the baselines. A page past the stop stays unproven and moves to M6.
- **Dispatched sessions.** A case whose agent dispatches a helper, as delegating's, orchestration's and the instruction review's cases may, counts each helper toward its batch. Such a page's recording may cost about twice 132. The maintainer sees that price for each page after the baselines, before he picks.
- **Short runs on `claude plugin eval`:** Q49's rerun, about 12; the routing baseline, at most 120; the suite runner's first base-and-head run, about 24. Suite runs are counted per wrapper touched. H2's gate merges after L4 and L7, so their edits run no suite. After it, about six wrappers are touched by H3's cuts, L5, L6 and slice Z, each run at the base and the head the first time, about 12 runs each, 72. Q49's second rewrite, for any wrapper that still misses, reruns the rewritten wrappers' cases and their neighbours' fire cases, as M3's 75-run rerun did: at most 75. Slice Z runs the routing suite once per case at its head, about 40, and the runner reruns any case that fails twice more. That is about 343, against a stop of 400 (Q104), with about 57 held for reruns. Two more wrappers, debugging and the reuse checklist, passed their fire case at exactly two of three in M3's last run, so their suites may need a rerun on noise alone. A full selection rerun, 174, happens only if a wrapper's description changes.
- **Review sessions are not eval runs, and are budgeted apart,** in the next section.
- **The stop covers M4's build only.** Upkeep after M4 is in the next section.
- **Red team review's cases change in H0b and cost no run here.** Its stored 10-run baseline goes stale and is named so; M9 runs it again, 20 runs for both cases, with that page's recording.
- G0 to G4, H0a, H0b, H2's build, and L0 to L7 start no eval run. L0's recorded tool runs are a handful of headless sessions.

## Upkeep after M4

A proven page is gated from the day it is marked. Each edit to it makes its record stale, and the commit check fails until the page's cases run again. The 1,400-run stop does not count that.

| Edit | Runs it costs, after H0b's item 8 | Before H0b |
|---|---|---|
| A page M4 proves, two cases | 132 after M4, since the other arms are then older; 44 within the milestone of a full recording | 132 |
| `fix-a-bug.md`, the definition of done, the contract or the index | 135 after M4; 45 within the milestone of a full recording, as R4 is | 135 |
| A file every arm shares, or a change of model | Every arm: 132 a page, 135 for fix-a-bug | The same |
| A grading file alone | None, when a re-grade changes no grade (H0a) | 135 |
| A page a wrapper names, or a wrapper or its cases | Its suite at the head: about 6 selection runs | None |
| The contract or the index | The routing suite at the head: about 40 to 120 selection runs | None |

- **How many pages.** After M4, at most about six pages are proven: `fix-a-bug.md` and up to five pages H3 records and passes. 28 wrappers name 29 pages, and each of those pays the selection row above.
- **Who says yes to a suite run (Q105).** An agent may run a pull request's wrapper suites at its head itself, up to 12 runs per pull request; `suites.py` counts them in a file per branch and refuses the 13th without a batch yes. A larger run, and the routing suite, still need the maintainer's yes with a count, as Q46 says. The number of proven pages is his choice after the baselines.
- **How often.** Up to M3's sign-off the ten pages changed in 1 to 55 commits each. H3 weighs that before a page is recorded, and moves a high-churn page's tables to a reference page first.
- **Batching.** An edit to a proven page does not land on its own. It waits in a list under the current milestone's plan, "Results", as M3's "Queued for slice Z" did, and the queued edits land together in that milestone's closing slice, with one recording per page: the guided arm alone when the other arms were recorded that milestone, else every arm. A fix the maintainer will not wait for lands with its own recording, on his yes with its count.
- **For scale.** Re-recording one arm alone saves runs inside a milestone: R4's 90, and a rush fix's. A batch in a later milestone records every arm, so the batching rule, one recording per page per milestone, is what holds upkeep down after M4. With five pages proven and each edited once a milestone, that is about 795 runs a milestone.
- **Drift between arms.** A guided arm recorded alone is compared with two-line and bare runs that may be older. A record names each arm's agent tool version and milestone. A batch records the guided arm alone when the other arms were recorded in the same milestone. When they are older, or the model a run resolves to changed, it records every arm. So a page's first edit batch in a milestone after a full recording costs 44, and a batch in a later milestone costs 132. M4's own slice Z records R4's guided arm alone, since R3 recorded every arm in M4. A version that differs between arms is a warning, and the eval page reports it, as it did for M3's routed arm.
- **An instance pays none of this for the kit's pages.** A synced page the kit's lock marks proven is not gated in an instance. An instance pays only for pages it proves itself.
- **Each milestone record reports** the upkeep runs spent, beside its own eval runs.

## Review session budgets

A review session is a fresh session at the driver tier, or at the worker tier for advisory work (Q91). It costs more of the maintainer's quota than an eval run on the small model. How much more is not measured: L0 records whether each agent tool reports a session's token use, and the first three reviews through the loop put a figure in the milestone record. Every count in this section is an estimate, from the scale rule in "L1".

Per pull request, through the loop:

| Round | Sessions | Made of |
|---|---|---|
| A full round on machinery code | 6 | The four, docs drift, and reuse or one retry |
| A fix round after it | 5 | Code and security over the delta, one dimension with a finding, the re-check, the whole-branch pass |
| A full round on tests or cases alone | 2 | Code and test adequacy |
| A fix round after it | 3 | Code, the re-check, the whole-branch pass |

So a clean pull request costs about 6, one fix round makes 11, and two make 16, which is the cap. Without the scale rule, the review page's dimensions on every round would make 6, 14 and 22.

Per slice, for M4's own build:

| Slices | How each is reviewed | Sessions |
|---|---|---|
| G0 to G4 | By hand: a fresh re-check, one more per fix round, and the instruction review of its pages with its re-check. | 18 |
| H0a, H0b, H1 | The same. | 8 |
| L0 to L3 | The same: the loop does not exist yet. | 15 |
| L4 to L7 | Through the loop: one pull request each with one fix round, 11, and two for its pages' instruction review. | 52 |
| H2 | Through the loop, as two pull requests, the runner and mark, then the gate: one fix round each, 22, and two for their pages. | 24 |
| H3 | Through the loop: about five pull requests of cases and a page's proof keys, a mixed range, 11 each. | 55 |
| Z | Through the loop, 11, and four for the hashed pages' instruction reviews. | 15 |
| Two fix pull requests nobody planned | Through the loop, 11 each. | 22 |
| The plan and the close | The red team rounds as they run, priced at fifteen, the outside red team, and up to six teach-back grader sessions, three teach-backs with a follow-up each. | 22 |
| | **Review sessions** | **231** |

- **About a dozen of these run at the worker tier in M4:** docs drift and reuse, on each full round of machinery code through the loop. The re-check mostly stays at the driver tier, since nearly every range here changes a gate. The larger saving shows in an instance, where most changes are product code.
- **The stop is 250 review sessions.** A slice that passes twice its row says so in its report before it goes on.
- **A guard or harness slice still open when L3 merges goes through the loop,** as "First real use" says. Each adds about 11 to its row. H1, which waits on a 135-run yes, may be one.
- **Where the count is reported.** In each dispatch record. In the completion record, per round. By `python3 ws.py review status`, against the cap. In one line of the pull request's review record, such as `Sessions: 11 of 16`. In each slice's report under "Results", against its row here. And in `docs/milestones/m4.md`, in a "Review sessions used" table beside "Eval runs used".
- **Before L1 merges,** a builder counts by hand each fresh session it starts for a review, and reports the count the same way.
- **The cap is an instance's own.** It lives in the manifest, so a team sets its number where it sets its tiers.

## Execution profile

- Orchestrator: one driver-tier coordinator session hands each slice to a builder session in its own worktree. It does not commit for the builders.
- Order: lanes G, H and L run at once. G0, G1 and H0a merge first. G2 to G4 merge after H0a. L1 and L2 run in order after G1; L3 waits for L2 and G2; L4 and L5 follow L3; L6 follows L3 and G4; L7 may run beside them. H2's gate merges after L4 and L7. H3 takes each page after the last slice that edits it. Z waits for all.
- Shared interface: this plan's [names](#names-this-plan-fixes) and the "G2" rule. The coordinator owns both; a builder asks for a change in its report.
- Shared code: the literal rule, in the parser, written by G2; G3, G4 and L3 call it. The agent tools' adapters and `ws.py dispatch`, written by L1; L2 and L5 call them. The mark's store, written by L3; L5 and L6 call it.
- Nudges: 2.

## The maintainer's steps

About 6 hours, as the program estimates.

- Agree the spec, then approve the plan after its red team.
- Say yes, with a count, to each eval batch. After H3's baselines, choose which pages go to a recording.
- Read one full review record.
- Raise a pull request's cap of review sessions, or end its review, when a loop stops there.
- Sit two teach-backs: one on the first plan awaiting approval after L5 merges, or a change entry to this plan, and one on a pull request.
- Confirm this repository's merge policy, and set any other repository's.
- Merge, after its own review, each pull request that changes `.github/workflows/`: L3's push trigger and mark step, and H2's suite step.
- Read the ten proof results, and strike any page he disagrees with.
- Decide any declined security or architecture finding.
- Run the private checks: the ledger's, the attack scripts, and G2's measure over the session logs.
- Approve the tag.

## Records this plan must leave

- Decision records for the guards' fail-closed rule, the review mark, the merge policy and teach-back; amendments to 0004 and 0006. Each is offered as the [decision interview](../playbooks/decision-interview.md#when-a-decision-gets-a-record) says.
- R3 and R4, the routed arm's record, each baseline and proof recording, the routing baseline and the selection results.
- The recorded runs criteria 38, 40, 43 and 45 name, under `tests/records/`, each with a replay test.
- The mark and the completion record of one real change.
- An instruction-review record for each guidance page changed, and the trailers that name them.
- A report per slice under "Results", each claim marked verified or inferred, with the list of hashed-file edits queued for slice Z.
- `docs/milestones/m4.md`, with its eval runs, upkeep runs and review sessions used, and entries in `CHANGELOG.md` and `EVIDENCE.md`, all current before the outside checks run.
- A question-log row for each question the workspace should have answered, as the contract's rule says.

## Later

- **Matching findings to threads, and posting comments.** M8, with a git-host provider.
- **Machine-state records.** M5.
- **Wrappers for the review orchestrator and teach-back.** M6, the milestone that proves them.
- **A second agent tool loading the wrappers.** Not planned; the README states the limit.
- **A signed mark.** Nothing here needs one yet.

## Red team

Round 1: [record](../records/adversarial-reviews/2026-11-26-m4-fail-closed-guards-review-loop-and-evals.md), holds with fixes, 16 findings. Each was verified before it was accepted; findings 4, 5 and 6 by running the hook, the grep and the hash.

Round 2: [record](../records/adversarial-reviews/2026-11-26-m4-fail-closed-guards-review-loop-and-evals-round-2.md), holds with fixes, 14 findings, rows R2-1 to R2-14. Findings R2-1 and R2-6 were verified by running the hook.

Round 3: [record](../records/adversarial-reviews/2026-11-26-m4-fail-closed-guards-review-loop-and-evals-round-3.md), holds with fixes, 12 findings, rows R3-1 to R3-12. Findings R3-1, R3-4 and R3-6 were verified by running the hook.

Round 4: [record](../records/adversarial-reviews/2026-11-26-m4-fail-closed-guards-review-loop-and-evals-round-4.md), holds with fixes, 11 findings, rows R4-1 to R4-11. Findings R4-1 and R4-2 were verified by running the hook.

Round 5: [record](../records/adversarial-reviews/2026-11-26-m4-fail-closed-guards-review-loop-and-evals-round-5.md), holds with fixes, 11 findings, rows R5-1 to R5-11. Findings R5-2 and R5-4 were verified by running the hook.

**The loop goes on (Q106).** The rounds found 16, 14, 12, 11 and 11 findings, each "holds with fixes".

Round 6: [record](../records/adversarial-reviews/2026-11-26-m4-fail-closed-guards-review-loop-and-evals-round-6.md), holds with fixes, 8 findings, rows R6-1 to R6-8. Findings R6-1 and R6-2 were verified by running the hook. Round 6 changed the plan in substance, so round 7 runs.

Round 7: [record](../records/adversarial-reviews/2026-11-26-m4-fail-closed-guards-review-loop-and-evals-round-7.md), holds with fixes, 7 findings, rows R7-1 to R7-7. Round 7 changed the plan in substance, so round 8 runs.

Round 8: [record](../records/adversarial-reviews/2026-11-26-m4-fail-closed-guards-review-loop-and-evals-round-8.md), holds with fixes, 6 findings, rows R8-1 to R8-6. Round 8 changed the plan in substance, so round 9 runs.

Round 9: [record](../records/adversarial-reviews/2026-11-26-m4-fail-closed-guards-review-loop-and-evals-round-9.md), holds with fixes, 8 findings, rows R9-1 to R9-8. Round 9 changed the plan in substance, so round 10 runs.

Round 10: [record](../records/adversarial-reviews/2026-11-26-m4-fail-closed-guards-review-loop-and-evals-round-10.md), holds with fixes, 8 findings, rows R10-1 to R10-8. Round 10 changed the plan in substance, so round 11 runs.

Round 11: [record](../records/adversarial-reviews/2026-11-26-m4-fail-closed-guards-review-loop-and-evals-round-11.md), holds with fixes, 6 findings, rows R11-1 to R11-6. Round 11 changed the plan in substance, so round 12 runs.

Round 12: [record](../records/adversarial-reviews/2026-11-26-m4-fail-closed-guards-review-loop-and-evals-round-12.md), holds with fixes, 7 findings, rows R12-1 to R12-7. Round 12 changed the plan in substance, so round 13 runs.

Round 13: [record](../records/adversarial-reviews/2026-11-26-m4-fail-closed-guards-review-loop-and-evals-round-13.md), holds with fixes, 5 findings, rows R13-1 to R13-5. Round 13 changed the plan in substance, so round 14 runs.

| # | Finding | Disposition | Action |
|---|---|---|---|
| 1 | The review mark cannot sit at the tip it reviewed: committing the review's record makes a new tip with no mark. | Accepted | L3: a commit after the marked one that changes only the review's record paths keeps the mark; any other path makes it `delta`. Criterion 39 tests both. |
| 2 | The suite gate fails four wrappers today; "passed" is undefined for a three-run case; the selection budget leaves out later suite runs. | Accepted | H2: two of three runs pass a selection case; no mark fails the gate unless the wrapper is listed with a reason and a milestone; base results are reused. Criterion 24. Budget recounted at about 336; the stop is in the maintainer's queue. |
| 3 | The agent under review can write the completion record or a transcript and then mark its own change. | Accepted | L3: the guards refuse an agent's writes to the completion records, the mark's store and the transcript folder. Criterion 38 gains a case for each. An interpreter stays out of reach, as for every guard. |
| 4 | Four routes pass the guards and the rule as written does not reach them: stdin into an unread program, a variable as runner text, a bare repository's config with `--git-dir`, and an exported `GIT_EDITOR`. | Accepted | Verified, each exits 0 at the hook today. G2 judges stdin and a variable the line sets; G3 counts an earlier export and makes an unread git folder unresolved; G4 treats a folder with `HEAD` and `config` as a git folder. Criterion 7. |
| 5 | Criteria 28 and 52 cannot pass: V8's first grep matches dated records and plans. | Accepted | Verified, 64 instruction-review records match. V8's first command now excludes plans, records and milestone records. |
| 6 | H0a's migration claim is false: five of eight stored records are already stale. | Accepted | Verified, by recomputing each record's hash. H0a migrates only the records current at its base; a stale record stays stale. Criterion 61. |
| 7 | H3's budget leaves out dispatched sessions, and counting them needs a `run.py` change after the freeze. | Accepted | H0b item 4 counts dispatched sessions from the transcript, before the freeze. The budget says such a page may cost about twice 132. |
| 8 | The cap of 16 is below H2's own estimate of 18, and leaves no room for a retry. | Accepted | The cap counts the code review's sessions; an instruction review counts toward the milestone only. H2 runs as two pull requests. Review sessions rise to 186. |
| 9 | The upkeep example is wrong: R1 and R2 changed shared files. A guided arm recorded alone is compared with older arms. | Accepted | The example is replaced. Every arm is recorded again once a milestone, at its close, and whenever the resolved model changes. |
| 10 | Criterion 22 gives a case's source no home, and a field in a fix-a-bug case would stale R3. | Accepted | Sources live in `evals/sources.json`, outside every case's hash. |
| 11 | H3 records debugging before the stop, against Q87's order. | Accepted | Debugging's baseline runs first and its recording waits for the maintainer's pick. The budget prices ten baselines and five recordings; the total is unchanged. |
| 12 | Reading an unread program's quoted argument as a command refuses `grep -rn 'git push -f origin main' docs`. | Accepted | G2 names a short list of programs that never run their arguments, shared with G4's readers. Criterion 7 keeps the quoted search and `echo` lines passing. |
| 13 | This plan's Red team section used the record form, which red team review's step 5 does not yet allow. | Accepted | This table returns, as the page says today. H0b's item 9 changes the page. |
| 14 | L1 turns a red team's edit tools off and writes its record, but red team review says the red team writes its own record. | Accepted | L1 exempts the red team: it writes its own record, and a check after it ends refuses any other file it changed. |
| 15 | Criterion 44 could put the private list's repository names into the tracked manifest. | Accepted | Criterion 44 reads the tracked list only, and no entry may name a repository from the private list. |
| 16 | Editorial slips: a stale item number, a total on the wrong base, and criteria out of order. | Accepted | Fixed: the item number, 1,745 on the planned base and 1,880 with re-records, and a note that criteria are numbered in the order they were added. |
| R2-1 | G2 would read an interpreter's code as a shell line and refuse `python3 -c`, `awk`, `jq` and `find -name`; if `no_stage_all` took the rule, stored grades could flip. | Accepted | Verified: `python3 -c` lines exit 0 today, and 32 stored fix-a-bug transcripts hold one. G2 lists interpreters whose code is not a shell line. `no_stage_all` does not take the rule. Criterion 7 names the lines. |
| R2-2 | `review mark` cannot hold once the review's record is committed: round 1's fix reached `review status` only. | Accepted | L3: the mark names the reviewed commit, accepts later record-only commits, and its store sits under `docs/records/reviews/`. The order of collect, commit, mark, commit is written out. |
| R2-3 | The mark shows some session replied in shape, not that the dispatched review ran. | Accepted | L2: a transcript counts only when its first message hashes to a dispatch record's prompt and its session id matches. Dispatch records are guarded. Criterion 40 adds an undispatched transcript. |
| R2-4 | The gate holds only at `gh pr create`; nothing checks the mark at publish or merge. | Accepted | L3: `review_gate` also refuses `gh pr ready`, `gh pr merge` and `ws.py merge` without a mark at the head, and CI checks the mark's fingerprint. Criterion 40. |
| R2-5 | The upkeep rules contradict each other, so "about 44 runs" rarely holds. | Accepted | One rule: a batch records the guided arm alone when the other arms are from the same milestone, else every arm. Key point now says 44 to 132. Slice Z's guided-only R4 fits it. |
| R2-6 | In a `person` repository an agent can still run `gh pr merge`. | Accepted | Verified: `gh pr merge 5` exits 0 today. L6 refuses every merge form there. Criterion 45. |
| R2-7 | The plan budgets about 336 selection runs against its own stop of 300, an open question. | Accepted | The stop is now 400, by Q104; slice Z runs the routing suite three times per case. |
| R2-8 | L1's tier floor contradicts worker-tier dimensions, since the templates open `Tier: driver`. | Accepted | Advisory dimensions and the re-check get their own worker-tier templates; the floor holds per template. |
| R2-9 | The teach-back mark has no rule for its evidence, so an agent could write it. | Accepted | L5: the mark reads the grader's dispatched transcript, takes no caller's word, and its store is guarded. Criterion 43. |
| R2-10 | Guarding the transcript folder would also refuse the agent tool's memory writes. | Accepted | The guards name the session transcript files, not their folder. |
| R2-11 | The contract states the eval rule wrongly from H0a until slice Z. | Accepted | H0b rewrites the contract's eval rule before R3, which records it; the non-goal names that exception. |
| R2-12 | L3's mark refusals depend on L4's rules, which merge after it. | Accepted | The fixed-row and declined-row refusals leave L3; L4 adds them, as criterion 41 already tests. |
| R2-13 | A new recording carries no grader hash, and no step writes one. | Accepted | H0b's item 8: `run.py` writes the grader hash into each new record, and `eval_record` fails a record without one after H0b. |
| R2-14 | The cap still equals the clean two-fix-round count, and mixed ranges fit no scale row. | Accepted in part | A mixed range takes the full machinery row. The cap is rejected as a fault: the maintainer set 16 (Q91), and stopping a loop that needs a retry on top of two fix rounds, for a person, is its purpose. |
| R3-1 | `watch git push -f origin main` passes every guard: the parser reads `watch`'s options past `git` and drops the force flag. | Accepted | Row F19 with a case. G2: a runner's options end at its first operand, and the re-check covers each known runner's options. |
| R3-2 | G2's standard-input rule, as written, makes most piped lines unresolved; narrowing it is left to the builder. | Accepted | G2 judges text the line itself holds; a download piped into an unread program is not judged, and the README's Limits names it. Criterion 7 keeps `git log --oneline \| head -5` passing. |
| R3-3 | The routing suite can block slice Z: it needs every case to pass, and no list excuses it. | Accepted | H2: the routing suite's mark is written when no case regresses from the base, at two failures of three, not when every case passes. |
| R3-4 | `git clone --config` and `git init --template` write a command-running setting, and a `cd` into the clone runs it. | Accepted | G3 judges both as `-c`, and treats a folder named by a `cd` as it treats `-C`. Row F20 with a case. |
| R3-5 | Reading quoted data as a possible command refuses URLs with `?` and `tr '[:upper:]'`. | Accepted | G2: in such text a non-literal program word refuses only when a reading reaches a judged program or could expand to one's name. Criterion 7 names both lines. |
| R3-6 | G3's allow list refuses `GIT_EDITOR=true` and `git -C src/REPO`. | Accepted | G3: a setting whose value is `true`, `:` or a never-run program passes, and a folder the guard reads at hook time counts as known. Criterion 7 names both. |
| R3-7 | After M4 every batch records every arm, so 44 and 45 hold only inside a milestone. | Accepted | The upkeep table and key point now say about 132 a page after M4, with 44 only inside the milestone of a full recording. |
| R3-8 | The `wrappers` check refuses slice Z's M6 entry and L5's teach-back page. | Accepted | L5 adds teach-back's waiting entry for M8; slice Z widens the part's code and cases to any later milestone. |
| R3-9 | Nine pages still say something waits for M4, and no slice names their edits. | Accepted | Slice Z's detail names the slice that edits each page; Z re-runs V8. |
| R3-10 | L3 and L6 depend on G2 and G4, but the order does not wait for them. | Accepted | L3 waits for G2; L6 waits for G4. |
| R3-11 | H3's review sessions are priced on the wrong scale row. | Accepted | H3 at 11 a pull request, 55; review sessions rise to 216 of 250. |
| R3-12 | Braces with no comma marked non-literal; L6's `person` wording; nine baselines for ten. | Accepted | Braces count only with a comma or a range; L6 reworded; ten baselines. |
| R4-1 | `gh api` writes force-move main's ref, merge a pull request past checks, and merge a branch into main, and every guard passes them. | Accepted | Verified: the ref `PATCH` exits 0 at the hook. G4 judges each; rows F21 to F23 with cases. |
| R4-2 | A git folder made and written in the same line passes, and a known folder's config is not said to be judged. | Accepted | Verified: `git init --bare /tmp/b && cp CFG /tmp/b/config` exits 0. G4 counts such a folder; G3 judges a known folder's config by the allow list. Row F24. |
| R4-3 | The suite mark keyed by object id breaks decision 0006's proof-key design and pulls outcome runs into suites. | Accepted | A suite holds selection cases only; outcome cases stay with `eval_record`. The mark's fingerprint uses `eval_record`'s hash, which drops review dates and proof keys. |
| R4-4 | The upkeep section leaves out the suite gate's cost on the 29 pages wrappers name. | Accepted | Two rows added: about 6 selection runs for a wrapped page, 40 to 120 for the contract or the index. Whether suite runs get a standing yes is in the maintainer's queue. |
| R4-5 | The same-milestone drift rule has no enforcement, and no field records an arm's milestone before the freeze. | Accepted | H0b's item 8 writes each arm's milestone; `eval_record` asks for every arm when they differ. Criterion 60. |
| R4-6 | The one-adapter non-goal conflicts with `run.py`'s frozen reader. | Accepted | The non-goal names `run.py`'s reader as the eval adapter and L1's as the review loop's. |
| R4-7 | The author writes the placeholders, so a review can be steered and still earn a mark. | Accepted | Each placeholder has a type the dispatch checks; the request is read from a named file; the completion record keeps every value. Criterion 32. |
| R4-8 | The dispatching pages may become impossible to follow inside the eval sandbox once L1 lands. | Accepted | Their cases measure the agent tool's own subagent route; L1 names it beside `ws.py dispatch`. |
| R4-9 | Criterion 14 and the defect row need a rule from alias to id, and `run.py` does not read the manifest. | Accepted | The manifest names the full id; `run.py` reads it; a record's model must equal it. |
| R4-10 | H2 could stale R3 by moving the fix-a-bug case files. | Accepted | Outcome cases stay in place; criterion 21 forbids moving a case file. |
| R4-11 | Smaller slips: session totals, the six-page figure, the eval page's stale paragraph, `rg` on the never-run list, the 30-minute wait. | Accepted | Each fixed: 217 sessions, six pages, H0b corrects the paragraph, `rg` removed, L0 records how the author's session waits. |
| R5-1 | Other `gh api` writes still move main or narrow its checks: a ref update without `force`, a `contents` write, branch protection, the default branch. | Accepted | G4 turns round: an agent's `gh api` write to a listed repository passes only by an allow list of endpoints. Row F26. |
| R5-2 | A `gh api` merge stays open in this repository, since plain `gh pr merge` passes here. | Accepted | Verified: `gh api -X PUT .../pulls/5/merge` exits 0. An agent merges only through `ws.py merge`, in every repository; `gh pr merge` and the API merge are refused. Criterion 45. |
| R5-3 | G2's write-path clause would refuse the test-first idiom that writes to `$TMPDIR`. | Accepted | G2: a path from `TMPDIR` or a `mktemp` result in the same line resolves under the temporary folder. Criterion 7 keeps the idiom passing. |
| R5-4 | `HOME` and `XDG_CONFIG_HOME` on a git call point it at a config the agent wrote. | Accepted | Verified: `HOME=/tmp/h git commit --amend` exits 0. G3 judges every variable on a git call. Row F25. |
| R5-5 | H3 can record a page whose second case the bare model already passes, which no guided arm can beat. | Accepted | H3 records only at 5 or fewer in one case and 7 or fewer in the other; otherwise the passing case is replaced first. |
| R5-6 | A hook cannot map a pull request's number to its head within its budget. | Accepted | Publishing and merging go through `ws.py ready` and `ws.py merge`, which read the head with `gh`; the hook refuses an agent's `gh pr ready` and `gh pr merge`. |
| R5-7 | The kit ships the new gates without saying which new files it syncs. | Accepted | H2 names each new file's kit class, and the suite gate does not bind a synced page in an instance. |
| R5-8 | The suite gate's first runs need the base too, so selection runs reach about 316 to 396; two more wrappers sit at two of three. | Accepted | The budget says so and that the stop fires near slice Z unless Q104 raises it. Key points name both open questions. |
| R5-9 | One shared list cannot both never run its arguments and only read. | Accepted | Two lists; G4's readers are a subset that never writes. Criterion 7 refuses `cp`, `tee` and `sort -o` into a git folder. |
| R5-10 | The `wrappers` part is widened too late for both waiting entries. | Accepted | L5 widens the part and sets both entries to M6, before H3 reaches `parts.md`. |
| R5-11 | CI reads a merge tree for marks; baselines need `--attempt M4`; criterion 60 sat after 62. | Accepted | CI computes marks at the pull request's head; H3 names the flag; criterion 60 moved. |
| R6-1 | G2 deletes the only rule that refuses `uv run git push -f origin main` and similar lines, and puts nothing in its place. | Accepted | Verified: the line is refused today. G2 reads a literal judged program after an unread one as that program's command; `which git` still passes. Row F28. |
| R6-2 | G4's allow list covers `gh api` only; `gh repo edit --default-branch`, `gh repo sync --force` and `gh workflow disable` pass on the listed repository. | Accepted | Verified: `gh repo edit O/R --default-branch x` exits 0. The allow list covers every `gh` write. Row F29. |
| R6-3 | Every gate a pull request must pass runs that pull request's own code. | Accepted | CI's mark and suite steps, `ws.py ready` and `ws.py merge` run the base commit's check code against the head's tree. The README names the remaining limit, the engine. |
| R6-4 | H3 screens pages against the bare model only, though recordings usually fail on the two-line comparison. | Accepted | The baseline adds the two-line arm, 10 runs a case. Baselines cost 400; the plan totals 1,285, and 1,420 with every re-record, which stops for the maintainer. |
| R6-5 | L2's placeholder types do not fit the real templates, and the reuse line is free text again. | Accepted | Every template's placeholders get types; the reuse line is read from the reuse checklist's file. No placeholder takes typed free text. |
| R6-6 | Selection runs sit at 396 of 400, with reruns and multi-wrapper pages uncounted. | Accepted | Routing runs once per case with the runner's reruns; runs are counted per wrapper touched; about 50 are held in reserve. |
| R6-7 | The tracked `.githooks/` folder is a force-push route no guard can close. | Accepted | Row F27, out of reach, named in the README's rewritten Limits. |
| R6-8 | Small slips: rounds priced at five, a heading for seven bullets, the profile's order, the temporary folder's wording, criterion 44 in an instance. | Accepted | Each fixed; review sessions now 220. |
| R7-1 | H3's two-arm baseline cannot run: `--baseline` runs the bare arm alone and `run.py` is frozen before H3; the screen has no number; the 400 runs depart from Q87. | Accepted | H0b's item 10 builds the two-arm baseline before the freeze. A two-line arm at 17 or more of 20 stops a page. The change to Q87's figure is listed as the author's and queued. Criterion 63. |
| R7-2 | Criterion 30 and a non-goal forbid H3's own cuts and its late table moves. | Accepted | The two high-churn pages move their tables before their baselines; a cut's commit is exempt by name. |
| R7-3 | Judging a known folder's own config refuses husky, git-lfs and this repository's own `core.hooksPath`. | Accepted | G3 judges what an agent's command sets or writes; a known folder's existing config is a person's. Worktrees count as known. |
| R7-4 | The selection budget is still summed per pull request, and Q49's second rewrite is unpriced. | Accepted | H2's gate merges after L4 and L7; per-wrapper recount about 343 with Q49's rewrite at most 75, against 400. |
| R7-5 | The ledger refusal sits in a stop hook, new top-level manifest keys are refused, and `ws.py merge` cannot tell an agent. | Accepted | A before-shell part with a new fact and a 0004 amendment; each value lives in a part's entry; `review_gate` refuses an agent's `ws.py merge`. |
| R7-6 | Base-code gates have no rule for a pull request that changes the mark's format. | Accepted | A person merges such a pull request after its own review; the README names it. |
| R7-7 | Small slips: batching wording, the page's hash, criterion 13, criterion 62's wording, the unpassing list's key, here-strings, dispatching baselines. | Accepted | Each fixed. |
| R8-1 | The two-line screen pre-empts the cut, and a screened page keeps `prove-by: M4`. | Accepted | The bare model's cut row is read first; a screened page moves `prove-by` to M6 once. |
| R8-2 | Replacing a case breaks criterion 30, and the replacement's baseline is unbudgeted. | Accepted | A replacement's commit is exempt by name from criteria 21 and 30 and the non-goal; its baseline comes out of the reserve. |
| R8-3 | CI runs the pull request's own workflow, so a pull request can drop the mark step and stay green. | Accepted | `ws.py ready` and `ws.py merge` refuse an agent's publish or merge of a range that changes `.github/workflows/`; a person merges it; the README names the file. |
| R8-4 | Moving the two pages' tables breaks a test, `INDEX.md`'s links and four parts' messages, and adds unnamed pages. | Accepted | Old headings stay as pointers until slice Z; the test changes with the move; the reference pages join New pages. |
| R8-5 | Round 7's fix to G3 extends row F27 to every pinned repository with a tracked hooks folder. | Accepted | F27 and the README's limit name any tracked hooks folder a known repository's config names. |
| R8-6 | Small slips: item numbers, an ambiguous finding 4, criterion 55, dispatched baselines, the profile's order, criterion order, the round count. | Accepted | Each fixed; review sessions 222. |
| R9-1 | The gate, the mark and the merge policy are defined for this repository only, but the kit ships them to instances. | Accepted | L3 states the scope: this repository. A pinned repository keeps the program's rule, agent drafts and a person's merge; its review loop waits for M6. Criterion 44. |
| R9-2 | The mark comes before CI's first three-system run, and a CI fix or a sync drops it. | Accepted | CI runs on every pushed branch; a clean merge from main keeps the mark; a person accepts a `rebased` mark from a terminal. |
| R9-3 | Resuming the dispatched session defeats the binding. | Accepted | The dispatch record holds the session's end and its transcript's hash; `collect` refuses a later turn; the gate refuses an agent's resume. Criterion 40. |
| R9-4 | Nothing ties a teach-back explanation to the person. | Accepted | `ws.py teach-back` runs in the person's terminal and takes the explanation and answers there; the gate refuses an agent's run. |
| R9-5 | The machinery page and `fix-a-bug.md` tell agents to do what M4 refuses. | Accepted | L3 edits the machinery page; the gate's refusal names the review route until slice Z edits fix-a-bug. |
| R9-6 | G4's git-folder test can be evaded by the order of writes, and "pinned" is undefined. | Accepted | A folder with `HEAD` or `config` counts; a pinned repository is one `.gitmodules` or the manifest lists. Criterion 11. |
| R9-7 | The plan was red-teamed before its spec was agreed. | Accepted | Listed as a decision made without asking, with its risk. |
| R9-8 | Small slips: adopting outside code, where the lists live, the mark check's phases, the dispatch record's folder, G4's measure, an H slice after L3. | Accepted | Each fixed. |
| R10-1 | A review mark can be written with every blocking finding still open, and a row can be deleted first. | Accepted | `review mark` refuses an open blocking row from any round and a findings record missing a counted row; the collector's rows are guarded. Criterion 37. |
| R10-2 | Round 9's git-folder test refuses ordinary writes in any folder holding `config` or `HEAD`. | Accepted | A git folder is named `.git` or holds `HEAD`, `objects` and `refs`; a second-file write is refused separately. Criterion 11 keeps a Rails `config/` passing. |
| R10-3 | Teach-back cannot earn a mark when the grader asks a follow-up, and its committed mark leaves the head. | Accepted | Answers go to a second bound session; the teach-back mark uses the record-only rule. Criterion 43. |
| R10-4 | CI on every branch push is owned by no slice and would turn pre-review pushes red. | Accepted | L3 adds the trigger; mark and suite steps run on pull requests only; first pushes check against the merge base; the maintainer merges workflow changes. Criterion 40. |
| R10-5 | F28 is refused today, so its case cannot be allowed on its slice's base. | Accepted | Verified: `uv run git push -f origin main` exits 2. F28's case stays refused at both; F17's example uses the quoted form that passes today. Criterion 62. |
| R10-6 | L3's two rules for a merge from main disagree, and the fingerprint's scope is unstated. | Accepted | `review status` reads a clean merge from main as `reviewed`; the fingerprint covers the branch's patch. Criterion 39. |
| R10-7 | "A user turn after the prompt" does not match a transcript, where tool results are user entries. | Accepted | L0 records how a person's turn differs; `collect` refuses that only. Criterion 40 keeps a reviewer with tool calls counting. |
| R10-8 | Small slips: the round count, a pin bump's dimensions, where the 12-run allowance is counted. | Accepted | Rounds priced as they run, at twelve; a pin-only row; `suites.py` counts per branch. |
| R11-1 | A line can set shell state, an alias, a named folder, the command hash or a trap, that changes what a literal word runs. | Accepted | Such a line is unresolved; a trap's text is read as a command. Rows F30 and F31. |
| R11-2 | `git clone --template=DIR` runs the template's hooks during the clone. | Accepted | `--template` on `clone` and `init` is refused unless DIR is known. Row F32. |
| R11-3 | An M4 baseline overwrites debugging's M3 baseline file, so the proof check reads M3 and refuses the move. | Accepted | Baselines go to a path named by their milestone, with the verdict `not proven`. Criterion 63. |
| R11-4 | A dispatched critic gets the author's handoff note and user-level settings at start-up. | Accepted | `ws.py dispatch` starts project-settings-only, skips the handoff loader, and runs reviewers in a clean worktree. |
| R11-5 | The nit cap conflicts with the mark's row count. | Accepted | The cap applies to the report to the person; replies and the findings record keep every row. Criterion 42. |
| R11-6 | Small slips: Q105 against Limits, a dispatching recording past 150, teach-back sessions, which plan to teach back, `proven-by`'s real use, machinery paths. | Accepted | Each fixed; review sessions 228. |
| R12-1 | Reading a variable with its value takes the last assignment written, not the one that runs, so conditional assignments pass. | Accepted | Verified by its author: those lines are refused today. A variable counts as set only on unconditional assignments in the same shell; a conditional export is judged on every value. |
| R12-2 | A shell or `source` given its own line's text as a script passes every guard. | Accepted | A shell's or `source`'s script operand is a deciding word; `/dev/stdin` and process substitutions are read. Row F33. |
| R12-3 | Person-only commands are reachable through `wslib/launch.sh` and `wslib/start.py`. | Accepted | Verified: `wslib/launch.sh ledger --close` exits 0. Guards cover every spelling, and the commands refuse under the agent tool's marker. Criterion 11. |
| R12-4 | An author can dispatch a dimension again until a reply is clean, and collect only that one. | Accepted | One session per dimension per tip beyond the one retry; `collect` reads every dispatch record since the last mark. Criterion 37. |
| R12-5 | CI's fingerprint check cannot pass once the record and mark are committed, and asks a mark of page-only ranges. | Accepted | One set of record paths that status, fingerprint and CI leave out; CI asks only for machinery or `src/` ranges. Criterion 40. |
| R12-6 | Slice Z's new gates on guided-arm pages may stall R4's runs in the scaffold. | Accepted | Each new gate names when it applies; Z's instruction review checks a scaffold run can finish. |
| R12-7 | Small slips: a safe value with shell characters, decision 0006's old baseline path, the budget's reserve, L0's scratch repository after G3. | Accepted | Each fixed. |
| R13-1 | Reviews come after the eval runs a review fix would spoil, and committing run records drops the mark. | Accepted | H0b is reviewed before R3's batch, and each H3 page's cases before its baseline. Run records that CI's re-grade passes are record-only paths. |
| R13-2 | Slice Z must edit pages under a proof attempt: the pointer headings and a section's cut. | Accepted | Pointers stay after M4 and Z repoints the links; a section's cut waits for its page's attempt. |
| R13-3 | A cut forces edits to up to four other wrappers' descriptions, priced nowhere. | Accepted | A cut costs its neighbours' suites, up to 24 runs, from the selection reserve. |
| R13-4 | CI's re-grade misses `baseline/M4/record.json`. | Accepted | `grade.py --recorded` reads every `record.json` under `baseline/`, landed with its stamp. |
| R13-5 | Small slips: fifteen current records, the routed arm's folder, the round count, the decision record lists. | Accepted | Each fixed; review sessions 231. |
## Approval

Not yet approved.

## Changes after approval

## Results

### The draft, 2026-11-25

Written by a driver-tier session that built nothing, in a worktree on the branch `m4/plan`.

- **Verified, by reading:** the contract, the size gate, the plan template, the red team review page, M3's plan with its results, M3's milestone record, the red team's record, the defect register, the eval page, the review orchestrator's page and the manifest, all at `2d00f5b`.
- **Verified, by reading:** the program plan's section for M4, the private attack scripts' report, and the maintainer's answers to M3's queue.
- **Verified:** the eval's hash covers the shell parser, as the eval page's "The gate" says, so a parser change stales the three fix-a-bug records. The wrappers' descriptions hold 8,542 of 9,000 bytes, by M3's record. Ten pages or sections name M4 in `prove-by`, by the README's table.
- **Verified, for the red team triage item:** pull request 59 merged on 2026-11-25 as `cb07903`, and the decision queue plan's Red team section now links seven records. The plan template's rule 4, red team review's step 5 and three places in size the work still name the plan's table. Both red team cases give their guided arm the page, both hidden tests assert a Disposition in the plan's table, and one baseline record is stored, for `red-team-fail-closed`. Red team review is unproven, and `eval_record` gates proven pages only, by its own docstring.
- **Inferred, for the review session budgets:** every count in that section. It rests on the review orchestrator's page, read at `2d00f5b`: five dimensions that always run today, one retry each, and a re-check and a whole-branch pass on a delta round. No review has run through a dispatch yet, so no session's cost is measured.
- **Inferred:** every budget figure for H3 beyond the baselines, since the baselines decide which pages are recorded. That the two existing review marks do what the program plan says, until L0 runs them. That grading files can leave the recording's hash without loss, which the red team should attack.
- **Applied, 2026-11-26:** the maintainer's answers to Q86 to Q91, each under "Settled decisions". Three choices left "Decisions made without asking" because he settled them: the decision queue, the grader stamp and the parser's merge order.
- **Applied, 2026-11-26, on the maintainer's yes:** Q91's narrowing, the re-record of one arm alone as H0's item 9 (now H0b's item 8), and the decision queue plan marked abandoned on main as `f45ea0d`. R4's budget fell from 135 runs to 45.
- **Inferred:** that a newly recorded guided arm can be judged against older two-line and bare runs without loss, which the red team should attack. The arms file gives the bare arm no files and the two-line arm one (verified, `evals/arms.json`).
- **Applied, 2026-11-26, the revision:** Q92, Q101, Q102 and Q103, each under "Settled decisions", and the upkeep cost under "Upkeep after M4". H0 is now H0a and H0b. The red team triage item moved from L7 to H0b, and its check was dropped. Q95 was superseded by Q103.
- **Verified, for Q101:** the private attack scripts' stored results list ten force-push routes through a command git runs, F1 to F10, beside B1 and B2, which M3 closed. F11 to F18 are the lines M3's record lists under "Known limits, for M4".
- **Inferred, for H0a:** that the stored records can be re-hashed with no new run because no file an agent is given changes. The red team should attack this.
- **Red team round 1, 2026-11-26:** holds with fixes, 16 findings, each verified and accepted; the triage is in the Red team table. Verified: the four routes of finding 4 exit 0 at the before-shell hook; V8's first grep matches 64 instruction-review records; five of eight stored records are stale at `78e4dfd`.
- **Red team round 2, 2026-11-26:** holds with fixes, 14 findings; 13 accepted, one in part. Verified: `gh pr merge 5` and `python3 -c` lines exit 0 at the hook today; 32 stored fix-a-bug transcripts hold a `python3 -c` line.
- **Red team round 3, 2026-11-26:** holds with fixes, 12 findings, all accepted. Verified: `watch git push -f origin main` and `git clone --config core.fsmonitor=... . /tmp/c && cd /tmp/c && git status` exit 0 at the hook today.
- **Red team round 4, 2026-11-26:** holds with fixes, 11 findings, all accepted. Verified: the `gh api` ref `PATCH` and the same-line `git init --bare` write exit 0 at the hook today.
- **Red team round 5, 2026-11-26:** holds with fixes, 11 findings, all accepted. Verified: `HOME=/tmp/h git commit --amend` and `gh api -X PUT .../pulls/5/merge` exit 0 at the hook today.
- **Red team round 6, 2026-11-26:** holds with fixes, 8 findings, all accepted. Verified: `uv run git push -f origin main` is refused today by the rule G2 removes; `gh repo edit O/R --default-branch x` exits 0 at the hook.
- **Red team round 7, 2026-11-26:** holds with fixes, 7 findings, all accepted. Verified by its author: `--baseline` runs the bare arm only in `plan_runs`; the engine refuses unknown top-level manifest keys.
- **Red team round 8, 2026-11-26:** holds with fixes, 6 findings, all accepted. Verified by its author: `ci.yml` runs on `pull_request`; a test reads the machinery table in place.
- **Red team round 9, 2026-11-26:** holds with fixes, 8 findings, all accepted. Verified by its author: `ci.yml` runs on pushes to main and pull requests only; `claude --resume` keeps the session id.
- **Red team round 10, 2026-11-26:** holds with fixes, 8 findings, all accepted. Verified: `uv run git push -f origin main` exits 2 at the hook today.
- **Red team round 11, 2026-11-26:** holds with fixes, 6 findings, all accepted. Verified by its author: `alias g=git; eval g push -f origin main` exits 0 at the hook, and a `git clone --template` ran the template's hook in a scratch folder.
- **Red team round 12, 2026-11-26:** holds with fixes, 7 findings, all accepted. Verified: `wslib/launch.sh ledger --close` exits 0 at the hook today.
- **Red team round 13, 2026-11-26:** holds with fixes, 5 findings, all accepted. Verified by its author: `grade.py --recorded` reads three fixed globs; the one-time records carry their cases' hash.
- **Not run:** no eval or selection run, and no guard attack.
