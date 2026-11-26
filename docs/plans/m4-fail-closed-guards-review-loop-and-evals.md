---
kind: plan
last-reviewed: 2026-11-25
status: draft
milestone: M4
---

# M4, fail-closed shell guards, the review loop and the eval system: hand-off plan

The plan for the fourth milestone: close the shell guards' known gaps with one rule, then build the review loop and the eval system. Building sessions work from it; the maintainer approves it. It follows the [hand-off plan template](../templates/hand-off-plan.md).

**In short:** M3 left routes past the shell guards, a review that runs by hand, and ten pages that name M4 as the milestone to prove them. This plan closes the routes with one rule in the parser, builds the review's dispatch, mark and gate with teach-back and a merge policy, and builds the eval system those ten pages are tested with. It is a first draft: not red-teamed, not approved.

## Key points

- **The guards come first, under one rule.** A shell guard refuses any command whose deciding word the parser cannot resolve to a literal.
- **The parser fix merges after recording R3.** The eval hashes the parser. Slice H0 lets a re-grade hold grading files, so the fix then costs no runs.
- **The review loop:** dispatch, a completion record, a review mark, a gate at pull-request creation, teach-back and a merge policy.
- **The eval system:** suites, a gate at the push, and proof attempts for ten pages.
- **Eval runs:** about 1,175 planned, a stop at 1,400. Each batch needs the maintainer's yes with a count.
- **Review sessions:** about 180 planned, a stop at 250. A review scales to its diff, and a pull request is capped at 16.
- **Harness changes land in one slice, before any recording.**
- **The stop rule splits findings.** A gap a slice caused can stop it. A gap already open on main is recorded instead.
- **The decision queue is cut.** Its trial closed no item from evidence.
- **Not red-teamed and not approved.** The maintainer's review of M3 comes first. His six queue answers are applied.

## Settled decisions

Spec not yet agreed. The maintainer reads this draft after his hands-on review of M3, and his notes change it before any red team round.

The maintainer, 2026-11-25, in the brief for this plan:

- Shell-parser work comes first. The guards fail closed on any word the parser cannot resolve to a literal. That is one rule, not a fix per route.
- The rule covers B3, B4, the zsh glob qualifier, the lines the red team's finding 6 names, and the commands git runs from its config or its environment. The pre-push fix rides with it.
- `python3 ws.py merge` retargets stacked pull requests before it deletes a branch.
- The stop rule separates a gap a slice caused from a gap already open on main. Eval-harness changes land in their own slice before any recording.
- Eval run budgets are stated per slice, because runs cost his usage quota.
- The plan says whether M4 builds the decision queue, and why.
- This plan stops before its red team, and is neither published nor merged.

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
- **Q88.** A re-grade holds grading files. A parser or grader change needs no new runs when re-grading every stored transcript changes no grade; a changed grade still needs a recording. The parser fix, G2, merges after R3.
- **Q89.** Slice H0 adds a usage check. `run.py` reads a usage file kept outside the repository before a batch, and refuses when over his limits. No file means the check is off. Only a stale file counts as unknown. Its rules sit outside the eval's hash.
- **Q90.** In G4 the outward-write guard also reads a list kept outside every repository, as `deny_list` reads its list. G4 updates the guard's cases and decision 0004.
- **Q91.** A review scales to its diff. A pull request is capped at 16 review sessions, and M4 stops at 250. Reuse, docs drift and the re-check run at the worker tier, unless the change touches a gate.

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
- **Four of the nine other pages are planned to reach a recording.** That four is a guess, and the baselines replace it. The ceiling of 1,400 is the maintainer's (Q87).
- **A stale usage reading stops a batch** (H0, item 8). Q89 says a stale file counts as unknown, and leaves open what unknown does. Here `run.py` names the reading's age and refuses, unless the batch's yes allowed a run without a reading. Rejected: going on, which would spend quota on a reading nobody trusts.
- **The routed arm is measured once more at the close.** M4 adds contract lines, index rows and pages, and M3 showed that added text can cost passes.
- **A plan's red team triage lives in the record, and the plan links each record** (L7). Rejected: the table stays in the plan. The maintainer chose the record for the decision queue plan, the record already has a Disposition column that every other document uses, and M3's plan carried about 225 lines of triage tables. This plan's own Red team section takes that form now, ahead of the template.
- **A review scales to its diff, and a pull request is capped at 16 review sessions** (L1). Rejected: every dimension on every round, which makes about 22 sessions for a pull request with two fix rounds; and a cap alone, which stops a loop late without making it cheaper. Reuse runs when the range adds a file or a function, where the page runs it always today: the program counts four dimensions that always run. The maintainer settled the cap and the tiers on 2026-11-26 (Q91); the reuse trigger is still the author's.
- **A range of tests or eval cases alone gets two dimensions,** code and test adequacy. Rejected: the four. A test or a case holds no architecture to judge, and the code dimension reads what it could weaken.
- **New pages name M6 in `prove-by`.** A page cannot be proven by the milestone that writes it, and M6 uses the review loop on real fixes.
- **Machine-state records go to M5**, with the first instance. M3 left the choice between M4 and M5 open.
- **Names:** see [names this plan fixes](#names-this-plan-fixes).
- **A plan of four sub-batches, approved once,** as M3 was. Rejected: a plan per sub-batch, which would need four red teams.

## Goal

Three things are true at the end. The work starts from M3's open ends: the "Known limits, for M4" in [M3's milestone record](../milestones/m3.md#known-limits-for-m4), and findings 7 and 10 of [its red team's record](../records/adversarial-reviews/2026-11-25-m3.md).

1. **The shell guards fail closed.** A shell guard refuses a command when a word it must judge cannot be resolved to a literal. Each route past the guards that M3's record lists for M4 is refused, with a case.
2. **No pull request opens without a review that is shown to have run.** A review mark, written only from the reviewers' own output, sits at the reviewed commit. A gate refuses a pull request without one. Teach-back and a merge policy per repository say who may publish and merge.
3. **No proven procedure and no wrapper changes without its cases running on the old and the new version.** Each of the ten pages that name M4 in `prove-by` is proven, cut, or unproven with a failed attempt on record.

## Non-goals

- **No decision queue.** It is cut (Q86): its trial closed no item from evidence before M3's sign-off. Slice G0 marks [its plan](decision-queue.md) abandoned, and M4 builds none of its slices.
- **No matching of findings to existing threads, and no posting of comments.** Both need a git-host provider, which is M8. The guard that refuses every `gh api graphql` call stays as it is.
- **No live agent run in CI.** CI re-grades stored transcripts and checks marks. Agent runs stay on the author's machine.
- **No new wrapper, and no rise in either always-loaded ceiling:** 6,000 bytes for the contract and pointer files, 9,000 for the wrappers' descriptions. No copy of the wrappers for a second agent tool.
- **No guard on what an interpreter or a script does.** A hook reads a command line. What `python3 -c`, a script file or `curl` then does stays out of reach, and the README keeps saying so.
- **No signature on a mark.** A mark shows that a process ran on this content. It does not stop a person who edits files by hand, and the pages say so.
- **No change, after the first recording, to a file that decides what an agent is given:** `run.py`, `proofkeys.py` and the hash itself. Grading files may change on a re-grade, as H0 sets out.
- **No edit outside the closing slice to a page a gated record hashes:** the contract, the index, `fix-a-bug.md`, the definition of done and the order service's rule page. A file hashed only into an unproven page's own cases may change before that page's attempt.
- **No edit to a page under a proof attempt once its M4 attempt has started.**
- **No reading of an agent tool's transcripts outside one adapter per tool.**
- **No machine-state records.** They go to M5, with the first instance.
- **No pattern catalog and no saved agent roles.** The dispatch script is the one place a delegation pattern is encoded.
- **No third-party package** in the engine, the parts or the tests CI runs.
- **No outward write beyond this repository,** no instance repository, and no page copied from the work workspace.

## Why this needs a plan

It fails two size-gate conditions: it is far more than one screen of diff, and far more than a day of work. Most slices change a gate, and a broken hook can lock a session out.

## Slices

Every slice is built in its own worktree under `.claude/worktrees/`, on a branch `m4/<slice>`, started from the remote's main. H0 and H1 share the branch `m4/h`. A slice that touches a machinery path merges through a pull request; a doc-only slice may push straight to main, as [changing the machinery](../changing-the-machinery.md) allows. Every slice here changes a gate, a hook, a grader or the contract, so each runs at the driver tier; a slice's page batches may go to worker-tier helpers, and every review is driver work.

Recordings are numbered on from M3's: R3 follows the harness slice, and R4 closes the milestone.

### Sub-batch G: the guards

| Order | Slice | Work | Tier | Done when |
|---|---|---|---|---|
| G0 | Open M4 | `building` becomes `["M4"]`. The test that pins it to M3, the parts page's row and the adoption page are corrected. A check fails a `building` entry whose milestone record is signed off. `.env` joins `.gitignore`. The decision queue plan is marked abandoned. | driver | Criterion 1 |
| G1 | Push check and merge helper | The pre-push check loads a part's cases and the library they call from one commit (Q82). `ws.py merge` retargets pull requests stacked on a branch before it deletes that branch (Q84). | driver | Criteria 2–3 |
| G2 | The one rule, in the parser | The parser marks each word literal or not. A guard refuses a command whose deciding word is not literal. The stopgaps in the guards' own files go. See "G2" below. | driver | Criteria 4–8 |
| G3 | Commands git itself runs | A git setting passes only when it is on a list of settings known to run no command. A git option that takes a command is read as that command. See "G3" below. | driver | Criteria 9–10 |
| G4 | Guard gaps outside the parser | The routes the private attack scripts marked non-blocking: discards, secret reads, the ledger's close, repository copies through `gh api`, and writers into a git folder. See "G4" below. | driver | Criteria 11–12 |

G0 and G1 touch no file the eval hashes. They branch from main and merge at once, so no later push needs `--no-verify`. G2 starts on the same day. G2 to G4 change the parser, which the eval hashes, so each merges only after H1's records are on main, on a re-grade that shows no difference.

### Sub-batch H: the eval harness and the eval system

| Order | Slice | Work | Tier | Done when |
|---|---|---|---|---|
| H0 | Harness changes, before any recording | Every harness change M4 needs, in one slice: the grader stamp, the model in a record, the leak rule's open items, debugging's fixture and cases, batch budgets, one-time arms' re-record, and the proof checks' two gaps. See "H0" below. | driver | Criteria 13–19 |
| H1 | Recording R3 | The three fix-a-bug cases, 15 runs per arm in each: 135 runs. A guided arm that misses its margin is recorded once more, 45 runs, in a new batch. H0 and H1 share one pull request. | driver | Criteria 20–21 |
| H2 | Suites, marks and the push gate | One suite per wrapped page, and a routing suite. A runner that picks suites from changed paths and runs the base and the head. A mark by content fingerprint. The gate at the push and in CI. See "H2" below. | driver | Criteria 22–27 |
| H3 | Proof attempts | The ten pages that name M4: a baseline of the bare model, then a recording where the baseline calls for one. Debugging goes first, with its fixed cases. See "H3" below. | driver | Criteria 28–30 |

H0 starts beside G2, in its own lane. H2 starts after H1 merges. H3 starts after H1, and takes each page only after the last slice that edits that page.

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
| L7 | Small pieces | The `lifecycle_map` check. Red team review's form for a milestone's outside check. One home for a plan's red team triage. Handoff's keep mode. One rule for where a review's record is committed. See "L7" below. | driver | Criteria 46–48 |

L0 starts beside G2. L1 to L4 run in order after G1 merges. L5 and L6 follow L3, and L7 may run beside them.

**First real use.** From L3's merge on, every pull request of this plan that changes a machinery path passes the gate: reviewed through the loop, marked, then opened. Before L3, a guard or harness slice ends with one fresh driver-tier re-check instead, as M3's did. A defect found later in code a marked review covered goes to [escape analysis](../playbooks/escape-analysis.md) and becomes an outcome case, or a recorded reason why not.

### Closing

| Order | Slice | Work | Tier | Done when |
|---|---|---|---|---|
| Z | Contract, index and recordings | The queued edits to hashed pages, each with its instruction review. The version goes to 0.5.0. Then R4, 135 runs, and the routed arm, 45 runs, in separate batches. Then the records. See "Z" below. | driver | Criteria 49–56 |

After slice Z, the program's outside checks run before sign-off: CI, a fresh-session red team under L7's form, and private attack scripts written by a session that built nothing here, against the guards, the review gate and the mark. The tag `v0.5.0` follows sign-off.

### G0: Open M4

The [defect register](../records/defects.md) holds the row this slice closes: M3's sign-off left M3 in `building`, because a test pins the list to M3 and the adoption page says it names M3. The test stops pinning a number. The `proof` check gains one rule: a `building` entry whose record in `docs/milestones/` has `status: signed off` fails. M4 then removes itself in its own sign-off commit, and that rule holds every later milestone to the same step. The register's `.env` row closes here too: the secrets file joins `.gitignore`, in the repository and in the kit. The slice also sets the decision queue plan's `status` to `abandoned`, with a dated line that gives Q86's reason, and corrects each page that still calls the queue planned.

### G2: The one rule, in the parser

**The rule.** The parser reports, for each word it reads, whether the word is literal: bash and zsh would both hand the program exactly the text the parser reports. A word is not literal when it holds, outside quotes, a variable, a substitution, braces, a glob, zsh's extended glob, `=name`, or a `(` that zsh reads as a glob group or a glob qualifier. It is not literal when it holds an ANSI-C escape other than the seven both shells read alike, or a quote the parser cannot close as the shells do, as inside `${...}` or `((`.

A command is unresolved, and every shell guard refuses it, when a word that decides what runs, or what it acts on, is not literal:

- the program word, and the words of a wrapper or a shell before its program;
- for a command a guard judges, its subcommand and each argument that guard reads: a refspec, a remote, a write's path, a `git config` key, a repository, a folder;
- any command nested deeper than the parser unwraps.

Two cases follow from the same rule, and replace M3's rule about unread programs:

- **A word that may be a program is judged as one.** After a program the parser does not read, a word that is not literal may become `git` or `gh`. The words after it are judged as that program's, and the line is refused when either reading would be. So `arch $(command -v git) push -f origin main` is refused, and `ls *.md` passes.
- **Text that may be a command is judged as one.** A quoted argument of a program the parser does not read is parsed as a command line, as the text of `sh -c` is today. So `flock FILE -c 'git push -f origin main'` and `man -P '...' ls` are refused. A message body, such as `-m` or `--body`, is still never read so.

The parser also matches every program name it reads without regard to letter case, the shells, `env` and `printenv` included, since macOS and Windows find a program whatever its case.

**What it must refuse, each with a case.** B3 and B4, such as `echo x > .gi?/config`, `git config {alias.p,!sh}` and `rm outward-repos.jso?`. The zsh glob qualifier outside a push, such as `ls README.md(e:'git push -f origin main':)`, and the same word in an array assignment and a `for` list. Glob grouping in a program word, `g(i)t` and `g@(i)t`. The lines M3's last re-checks left: a quote inside `${...}` or `((`, runner text, a shell or `env` in another letter case, a shell the parser does not read when it is given text, and a word of only `\0` among the words of `sudo -s`. A brace in a discard, such as `git reset --{hard,}`.

**What goes.** The block of stopgap rules that M3 held twice, the guards' own refusals of a program word the shell expands, and the rule that refused any word naming a judged program after an unread one. So `which git` and `grep -n git notes.txt` pass again. `no_stage_all` takes the rule too; the eval's hash kept it out in M3.

**The `with-secrets` wrapper (Q53).** The parser unwraps `python3 ws.py with-secrets NAME -- PROGRAM`, so each guard judges PROGRAM as it judges any command. `secrets_shell` stops refusing git, gh and writes under it outright. Each route M3's slice Z found has a case.

**The measure.** Before it merges, the slice runs the guards at main and at its tip over every command stored under `evals/runs/`, and reports each line whose answer changed. The maintainer's machine repeats that over its session logs, as M3's sign-off did. A newly refused line that does nothing a guard guards is fixed, or named in the README with its way round.

**The re-check.** One fresh driver-tier session gets the rule, the cases and the README's limits, and looks for a line that passes and should not. Its findings follow the [stop rule](#stop-rule)'s split. The README's Limits is rewritten around the rule: what the guards refuse, and what stays out of reach, which is an interpreter, a script, a program's own configuration and PowerShell.

A new decision record states the rule, and decision 0004's amendments point to it.

### G3: Commands git itself runs

Git runs a program named by many settings: an editor, a pager, a credential helper, an ssh command, a filter, a diff or merge tool, a hooks folder, a file-system monitor. Ten of the private attack scripts' attacks got past the force-push guard through one of them.

- **Settings pass by an allow list.** A `-c KEY=VALUE`, a `GIT_CONFIG_*` pair, a variable git reads that is set on a git call, such as `GIT_EDITOR`, `EDITOR` or `GIT_SSH_COMMAND`, and a key `git config` writes, each passes only when it is on a list of settings known to run no command. `user.name`, `color.ui` and `GIT_AUTHOR_DATE` are on it. Anything else is refused, with a message that names the setting and the list. The list lives in one place, beside the parser.
- **An option that takes a command is read as that command.** `rebase --exec` is read so today. The same reading covers `bisect run`, `submodule foreach`, `filter-branch`'s filters, `difftool --extcmd`, `grep --open-files-in-pager`, and `--upload-pack`, `--receive-pack` and `--exec` on the commands that reach a remote.
- **A remote's transport passes by an allow list too:** `https`, `ssh`, `git` and a local path. `ext::` runs a command and is refused.

A setting a person keeps in their own git config is theirs: the guards judge what an agent's command sets or writes. The slice's measure and re-check are G2's.

### G4: Guard gaps outside the parser

Each is a route M3's private attack scripts found and marked non-blocking. None is a parser fault.

- **Discards, `no_discard`.** Git accepts any unique prefix of a long option, so the parser resolves `--har` to `--hard` as git does, and an ambiguous prefix is unresolved. While another live session holds the lease, the guard also refuses, in the main working copy: `checkout-index` with `-f` or `-a`, `update-ref` on a branch or the stash, a `restore`, `checkout --` or `rm` of paths, and a `clean` with `clean.requireForce` turned off.
- **Secret reads, `secrets_shell`.** `gh auth status --show-token`, `gh auth token`, `git credential fill`, the macOS keychain's password commands, a plain read after a `cd` into a secrets folder, `/proc/*/task/*/environ`, and `${!v}` over a list of every variable's name.
- **The ledger, `stop_gate`.** `python3 ws.py ledger --close`, run by an agent session that holds entries of its own, is refused. A person runs it from a terminal.
- **Repository copies, `outward_write`.** A `gh api` write to a `forks` or `generate` path creates a repository, and is judged as `gh repo fork` is.
- **A second list, outside every repository (Q90).** The tracked list is public, so it cannot name a repository whose name must stay private. `outward_write` also reads a list from the file a variable names, or from a default path beside the deny list, as `deny_list` reads its own. One file then serves every worktree, and nothing can commit it. `outward_list` refuses an agent's edit to that file as it refuses one to the tracked list. A missing file adds nothing. Decision 0004 is amended.
- **Paths inside a git folder, `git_folder_shell` and `outward_write`.** Today a named list of writers is refused, and `tar`, `unzip` and `patch` are not on it. The rule turns round: a command that names a path inside a git folder, or the outward-write list, passes only when its program is on a short list of programs that only read.

### H0: Harness changes, before any recording

M3's slice Z changed the harness inside the slice that recorded, and stopped three times on gaps in its own leak rule before its recording could start. Here every harness change lands first, and a test fails a later change (criterion 21).

1. **The grader stamp.** Today one hash covers what the agent is given and the code that grades. A change to grading code, such as the parser the staging grader calls, then needs 135 new runs, though no agent would act differently. The record gains a second hash, over the grading files: `grade.py`, each hook a grader runs, and the parser. When only those change, `python3 evals/grade.py --recorded --stamp` re-grades every stored transcript and, when no grade differs, writes the new grader hash. When a grade differs, the record fails until the case is recorded again: a grading rule is not changed after the runs it grades. CI's re-grade runs on every push, and fails a stamp nobody earned. Decision 0006 is amended.
2. **The model in a record.** A record names the model and the agent tool's version of every run. The gate fails a record whose arms ran on different models, or on a model other than the one the manifest names for evals. A tool version that differs between arms is a warning, and the eval page reports it. Naming the eval model in the manifest closes the defect register's row on model names outside the tier binding.
3. **The leak rule.** M3's last re-check left two items: the placeholder's own path is refused when an agent writes it in quotes, and a `..` route passes. Each gets a case.
4. **Debugging's fixture and cases (Q51, Q73).** The fixture's owner becomes `/home/user`. The contract copy routes a failure to the playbook. The page's first step asks for the repro as a test. The fix case drops its ruled-out grader, or the page's fix path keeps that list. These files are hashed into debugging's own cases only.
5. **Batches.** A batch is every run started under one yes from the maintainer, across calls of `run.py`. `run.py` takes the batch's name and count, counts each started run in a batch file, probes and failed runs included, and refuses to start a run past the count. The eval page defines a batch, and no longer caps a "session": M3's slice Z ran 225 runs against a cap of 150 because that word was loose.
6. **One-time arms.** `--rerecord` takes a one-time arm and keeps its first batch, and `pool.py` prints one-time arms with their pooled counts. M3 moved folders and pooled by hand.
7. **The proof checks' two gaps (Q6).** `eval_record` gates a page marked proven wherever it sits under `docs/`, not only in `docs/playbooks/`. `proof` fails a proof key on a page whose kind carries none.
8. **A usage check before a batch (Q89).** Before a batch, `run.py` reads a usage reading from a file kept outside the repository, which the maintainer's own tooling writes, and refuses the batch when the reading is over limits he sets there. No file means the check is off. A stale file counts as unknown: `run.py` names the reading's age and refuses, unless the batch's yes allowed a run without a reading. The call sits in `run.py`; its rules sit in a file outside the eval's hash, so tuning them stales no record.

H0's commits use `--no-verify` until R3's records are in, as the [machinery page's trap](../changing-the-machinery.md#traps) requires. H2 then moves that refusal to the push.

### H2: Suites, marks and the push gate

- **A suite belongs to one page that has a wrapper.** It holds that wrapper's selection cases, in the format M3's slice B6 set, and the page's outcome cases when it has them. One routing suite belongs to the contract and the index: a cold session gets a request and must name the right page.
- **Two runners, as today.** Selection and routing cases run on `claude plugin eval`. Outcome cases stay in `run.py`, because the plugin runner cannot run code graders.
- **Cases come from real work.** Each outcome and routing case names what it was drawn from: a commit, a pull request, a record or a question-log row. A check fails one that names none. Every grader is deterministic; none is judged by a model.
- **The suite runner.** `python3 evals/suites.py` picks suites from the changed paths: a wrapper, its cases, or any page a wrapper names. A change to the contract or the index picks routing. It runs each picked suite at the merge base and at the head, in temporary working copies, under the run cap it is given. A case that passed at the base and failed at the head runs at the head up to twice more, and counts as a regression at two failures of three: one run's difference is noise as often as signal. It exits 1 only for pass-to-fail, and 2 when the cap or the runner gave no verdict.
- **The mark.** A suite's mark is a committed file, named by suite. It holds the git object ids of the wrapper's folder, its cases and each page it names, with the model and the tool version. The runner writes it only when every case passed at the head: passing, not merely no worse than the base. A check fails a mark that does not match the tree.
- **The gate.** For content a suite's mark or a proven page's record covers, a commit and a push of a branch warn, the pre-push check refuses a push to main, and CI fails a pull request.
- **The routing baseline** is recorded once, with its table on the eval page.
- **Q49.** The four fire cases that still miss run again at five turns, about 12 runs. Only a wrapper that still misses is rewritten a second time.

### H3: Proof attempts

The ten: [test first](../playbooks/test-first.md), [debugging](../playbooks/debugging.md), the [throwaway prototype](../playbooks/throwaway-prototype.md), [safe refactor](../safe-refactor.md), the [research ladder](../research-ladder.md), [delegating](../orchestration.md#delegating), the [instruction review](../playbooks/instruction-review.md), [orchestration](../orchestration.md), [parts](../parts.md) and [changing the machinery](../changing-the-machinery.md).

Each attempt runs as M3's slice B7 did. Two cases are drawn from M1 to M3's real work. The page's two-line text is committed before its baseline runs. The baseline is the bare model alone, 10 runs per case.

| The baseline shows | Then |
|---|---|
| The bare model passes 8 or more of 10 in both cases | The page is cut, with the baseline as the reason. A page that holds facts or a rules table loses its procedure steps only, as [decision 0006](../decisions/0006-what-proven-means.md) says. |
| It passes 5 or fewer in either case | Three arms are recorded at 22 runs per case, 132 runs, on the maintainer's yes for that page. |
| Anything between | The page stays unproven. The baseline is its failed attempt, and `prove-by` moves to M6, once. |

- **Order.** Debugging first: its cases exist, and H0 fixes them. Then the pages no M4 slice edits. `orchestration.md`, its delegating section and the instruction review come after L1 and L4, which edit them. `parts.md` and `changing-the-machinery.md` come last, after every slice that adds a part.
- **A stop after the baselines.** Once the nine baselines are in, the slice stops for the maintainer's choice of which pages go to a recording. A page the budget does not reach stays unproven by his decision, with its baseline as the failed attempt, as red team review did in M3.
- **Proven needs a real run too.** A page's `proven-by` names the M4 slice report where the page was used, beside its record.
- **A proven page is gated from then on, and each later edit costs its recording again:** about 132 runs a page, as an edit to `fix-a-bug.md` costs 135 today. So the stop after the baselines also shows, for each page, how often it has changed. Up to M3's sign-off `parts.md` changed in 55 commits and `changing-the-machinery.md` in 22; the other pages in 1 to 6 (verified, `git log` on main). A page that changes that often is not sent to a recording whole: the slice first proposes which of its tables move to a reference page, so the proven part is the procedure alone.
- **A cut is queued for slice Z,** since it removes index rows: the page's steps, its wrapper and its rows leave in one commit.
- A run that dispatches a helper session, as the instruction review's and delegating's cases do, counts each dispatched session toward its batch.

### L0: Facts and prior art

Record each as verified or not under "Results", with the command or the transcript. For Claude Code and for Codex CLI: the command that starts a headless session on a named model and effort; the setting that turns its edit tools off, and what can still write; where the session's transcript is, and what marks its end; how a time limit stops it; and whether the tool reports a session's token use.

Then test two existing review marks in a scratch repository, against criteria 35 to 40: AI-DLC's `attest`, which ties commits to reviewed work by a content fingerprint and fails closed, and Anthropic's `agent-approval-check`, which requires human approvals on agent commits. Both are named by the program plan; that each exists and does this is inferred until the slice runs them. A decision record says, for each criterion, what each meets, what M4 takes with credit, and what it builds. It also settles where a mark is stored. If one of them meets every criterion of a slice, that slice adopts it, and the plan changes by an approved entry.

### L1: Dispatch

`python3 ws.py dispatch TEMPLATE --tier TIER --input NAME=VALUE --record PATH`.

- **The prompt is the template file with its placeholders filled, and nothing else.** The rule that a critic never gets the author's reasoning is then held by the tool, where today it is prose. The first line names the tier. The model and the effort come from the manifest's binding, and a dispatch never runs below the tier its template names.
- **One template file per recurring brief:** the review dimension, the review re-check, the red team, the instruction review and its re-check, and the teach-back grader. A playbook still shows its template; a check holds the page's copy equal to the file.
- **A review's pre-pass runs first:** the build, lint and format commands at the merge base and at the tip. On your own branch a new error or warning stops the review.
- **One retry** for a reply with no closed report, and a limit of 30 minutes per reviewer, the limit [decision 0020](../decisions/0020-where-the-sources-disagreed.md) chose and no page yet holds.
- **A reviewer starts with its edit tools off,** as L0 found possible, so "edit nothing" is held by the launch.
- **One adapter per agent tool:** a function that builds the command, and one that reads recorded output. The tests need no agent.

**A review scales to its diff.** The dispatch picks a full round's dimensions from the paths the range changes, and prints why:

| The range changes | A full round starts |
|---|---|
| Guidance pages, plans or records only | Nothing. The instruction review's trailers hold guidance. |
| Tests or eval cases only | Code and test adequacy. |
| Any other machinery path, or code under `src/` | Code, architecture, security and test adequacy. Reuse, when the range adds a file or a function. Docs drift and the other triggered dimensions, as their triggers say. |

- **A fix round runs less.** On a delta round the dispatch starts code over the delta; security, when the delta changes a hook, a guard, a check or CI; each dimension that has a finding from an earlier round; and the re-check of the rows marked fixed. The whole-branch pass runs once, at the tip that is to get the mark.
- **Advisory work runs a tier lower** (Q91). Reuse, docs drift and the re-check run at the worker tier. When the range changes a gate, which is a check, a hook, a grader, CI or the commit hook, they run at the driver tier like the rest. The review orchestrator's page and [orchestration](../orchestration.md) say so, where both call every review driver work today.
- **It counts review sessions.** Every session a dispatch starts for a review is one: a dimension, a retry, a re-check, a whole-branch pass, an instruction review, a red team, a teach-back grader. Each dispatch record holds its tier, model, effort and duration, and its token use where the agent tool reports it.
- **A pull request has a cap.** The manifest's `review` entry sets the most review sessions one pull request may start: 16 here, and the same in the kit. At the cap the dispatch refuses and names the count. The loop stops for the person, who raises the cap for that branch or ends the review. `python3 ws.py review status` prints the branch's count against the cap.

The estimates behind the cap are under [review session budgets](#review-session-budgets).

If a tool cannot be driven this way, dispatch ships for one tool behind its adapter, and the README marks the review gate "one tool". That is the program's rule, and not a stop.

### L2: The completion record

- **Judged from the reviewer's own words.** `python3 ws.py review collect` reads each reviewer's transcript through the adapter. A dimension is complete only when its reply holds a closed report for this tip, a count of findings equal to the table's rows, and the lines its dimension owes. For architecture those are `Invariants checked:` and `Big picture:`, and one alone does not count.
- **It writes two things for the tip:** the completion record, and the findings table in the form [the review orchestrator](../playbooks/review-orchestrator.md) gives. The completion record counts the round's sessions: started, retried and not complete.
- **A delta round re-checks every earlier row marked fixed,** in a fresh session.
- **Before a branch is called ready, one pass reads the whole branch,** not only the last delta.

The fix brief's mechanism and fix-seam fields point at architecture review's restate step and its look-past-the-repository step. That edit is to a hashed page, so it is queued for slice Z.

### L3: The review mark and the gate

- **`python3 ws.py review mark` refuses unless all of these hold.** The tree is clean. The tip equals the remote's tip. A findings record names the tip. The completion record is complete. A whole-branch pass exists. Every row marked fixed names its check, and every declined row its home (L4). Every declined security or architecture finding names a tracker key, or an acceptance with a developer's initials and an ISO date. A decline that names a key shows, by a quote or a comment id, that the ticket will remove the finding.
- **It has no mode that takes the caller's word.** The writer reads the completion record, and only the collector writes that, from transcripts.
- **`python3 ws.py review status`** answers `reviewed`, `delta` when an ancestor holds the mark, `rebased` when another commit with the same patch id holds it, or `none`.
- **`review_gate`, before a shell command.** It refuses `gh pr create` without `--draft`. It refuses that command, and a `gh api` call that creates a pull request, when the range changes a machinery path or code under `src/` and the pushed tip has no mark. A range of guidance pages alone needs none: the instruction review's trailers hold it. A command it cannot resolve is refused, by G2's rule.
- **A forged mark reads `none`:** one edited by hand, copied from another commit, or with no completion record behind it.

The mark is keyed by the tip and by the branch's patch id. The gate reads it in the same clone, and a real change's mark and completion record are published with its pull request.

### L4: The finding lifecycle

The rules go on [the review orchestrator's page](../playbooks/review-orchestrator.md), each tagged with what enforces it.

- **Verify before fixing.** The author checks a finding against the code before acting on it.
- **"Fixed" names the check that fails without the fix.** A row marked fixed with no check named stops the mark.
- **A decline names where the defect now lives,** and a decline rests on a search of the whole code, not a part of it. A deferred row names an open row of the [defect register](../records/defects.md).
- **A direction rule replaces a round count.** Rounds go on while each round's findings are fewer or narrower than the last. A round that widens the change stops for the person.
- **At most five nits are reported,** and the rest are given as a count. The template draws a written line between a finding that blocks and one that does not.
- **The cross-check.** `python3 ws.py defects check` fails a deferred finding whose register row is closed or missing. Until M8 it reads the register's file only.

### L5: Teach-back

`docs/playbooks/teach-back.md`, a playbook, `proof: unproven`, `prove-by: M6`.

- **What it is.** Before a person approves a plan, or publishes a pull request in a `person` repository, they explain it in their own words. A fresh session, sent the grader template through L1, grades the explanation against the plan or the diff, and against the plan's "Decisions made without asking". It asks follow-up questions only where the explanation had gaps.
- **The mark.** `python3 ws.py teach-back mark` records `passed` or `skipped` at that commit, beside the review mark.
- **It scales to size.** A change that passes [the size gate](../size-the-work.md#the-gate) gets one question, or a recorded skip with its reason.
- **It checks the owner of the change, never its reviewers.**
- **Fresh source.** Builders work from this description. Nobody building it opens the maintainer's private skill.

### L6: Merge policy

- **`merge_policy` in the manifest** maps a repository, named as the outward-write list names it, to `agent` or `person`.
- **`agent`:** agents publish and merge after CI passes, and teach-back runs at plan approval only.
- **`person`:** agents open drafts only. `review_gate` refuses an agent's `gh pr ready` unless a passed teach-back mark sits at the head commit. It refuses an agent's `ws.py merge` there: a person or human reviewers merge.
- **No entry means `person`.** This repository's entry is `agent`, as the maintainer has allowed since M1. The kit seeds none, so an adopted instance starts as `person`.
- **The policy never widens where agents may write.** `outward_write` still decides that.

### L7: Small pieces

- **`lifecycle_map`,** a check with cases. It fails a playbook or how-to with no row on the [lifecycle map](../lifecycle-map.md), and a row that links an archived page.
- **Red team review's second form** (the red team's finding 10): what a red team is sent for a milestone's outside check, that it may re-run the commands the record cites, and that it writes its record and commits nothing. The page stays thin, and gains no method.
- **One home for a plan's red team triage** (Q3, pull request 59). Each finding's disposition goes in the record's Disposition column, for a plan as for any other document, with the fix made or the place it is queued. The plan's Red team section holds one line per round: the record's link, its verdict, and the count of findings per disposition.
  - **The pages:** the plan template's rule 4 and skeleton, red team review's steps 1 and 5, the three places [size the work](../size-the-work.md) names the plan's table, and the milestone record template's row. An approved plan is frozen and keeps its tables.
  - **A check,** since nothing enforces either form today: a draft plan whose Red team section holds a findings table fails.
  - **The eval cases.** Red team review's two cases hash the page. Their hidden tests look for each disposition in the plan's table, and their two-line text names that table. All three change with the page, and so does the harness test's stand-in run.
  - **No recording is needed in M4.** The page is unproven, so no gate reads its record. Its one stored record, a 10-run baseline of one case, goes stale; the eval page says so. M9, which is to prove the page, runs the baseline again.
- **Handoff's keep mode** (Q35): where a tracked copy of a note lives, and the rule that a path on the author's machine is flagged.
- **One rule for a review's record** (Q41): a record about a branch is committed on that branch and reaches main with its pull request. [Procedure endings](../procedure-endings.md) states it once, and the three known defects M3's review records list are fixed against it.

### Z: Contract, index and recordings

- **The queued edits,** from the list under "Results". `AGENTS.md` routes a branch to its review before its pull request, names the merge policy in its pull-request rule, and names the push in its eval rule. `INDEX.md` gains a row for each new page, part and chain, and the lifecycle map's row, which has waited since M3. `fix-a-bug.md` gains the review gates and the fix brief's two fields. The definition of done names the review mark. Each cut from H3 is made here.
- **The waiting list.** The `wrappers` check's entry for the review orchestrator moves to M6, the milestone that proves it, and teach-back joins it.
- **The version** goes to 0.5.0, the engine's and the manifest's in one step.
- **R4,** 135 runs, as R3. Then, in a second batch, the routed arm: 45 runs to a one-time record. An arm that misses its margin is recorded once more, 45 runs, and judged pooled.
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

New pages: `docs/playbooks/teach-back.md`, as L5 gives it, and one decision record each for the guards' rule, the review mark and the merge policy. Everything else is an edit to a page that exists.

## Success criteria

Sub-batch G:

1. `building` in the manifest is `["M4"]`. When `building` names a milestone whose record has `status: signed off`, the `proof` check fails. `git check-ignore -q .env` exits 0. The decision queue plan's `status` is `abandoned`. (V2)
2. When a push holds a guard change that turns a passing case into a refusal, the pre-push check judges it without `--no-verify`: the cases it runs and the library they call come from one commit. (V1)
3. When `ws.py merge` merges a pull request whose branch is the base of open pull requests, it retargets each to the merged one's base before it deletes the branch. When a retarget fails, it deletes nothing and says so. Its tests run on recorded `gh` output. (V1)
4. The shell guards never pass a command in which a word that decides what runs, or what it acts on, is not literal. Each line "G2" names is refused, with a case. (V2)
5. The rule lives in the parser. No part file and no second library file holds a copy of it, and the test that held two copies equal is gone. (V1)
6. When a command runs under `ws.py with-secrets`, each guard judges the wrapped program as it judges any command. (V2)
7. The lines that must keep passing each have a case: the heredoc commit and pull-request idioms, `cd "$D" && make`, `ls *.md`, `which git`, `grep -n git notes.txt` and `command -v git`. (V2)
8. After G2, G3 and G4 each, `python3 evals/grade.py --recorded` finds no difference, and the slice's report lists every stored eval command whose answer changed. (V3)
9. When a git call sets or writes a setting that is not on the allow list, the guards refuse it and name the setting. A case covers `-c`, `GIT_CONFIG_*`, an environment variable and `git config`. (V2)
10. When a git option takes a command, the guards judge its text as a command line, with a case for each option "G3" names. A remote whose transport is not on the allow list is refused. (V2)
11. Each route "G4" names is refused, with a case. When a repository is named only in the list kept outside the repository, `outward_write` allows a write to it from the main copy and from a worktree, and `outward_list` refuses an agent's edit to that file. (V2)
12. A command that names a path inside a git folder, or the outward-write list, passes only for a program on the readers' list. `python3 tests/hook_cases.py` holds every hook row under its budget. (V2, V7)

Sub-batch H:

13. When only grading files change and a re-grade finds no difference, `eval_record` passes after the stamp. When a grade differs, it fails until the case is recorded again. A grader hash written by hand fails CI's re-grade. (V1, V3)
14. `eval_record` fails a record whose arms ran on different models, or on a model other than the manifest's eval model. (V1)
15. `run.py` passes the placeholder's path written in quotes, and refuses a `..` route to another account's folder. (V1)
16. Debugging's fixture names `/home/user`, and the transcript test lists no stored transcript as stale. (V1)
17. `run.py` never starts a run past its batch's count. A batch spans calls, and probes and failed runs count. When the usage file shows a reading over the limits, `run.py` refuses the batch; with no file it runs; with a stale file it refuses unless the batch allowed it. (V1)
18. `run.py --rerecord` takes a one-time arm and keeps its first batch, and `pool.py` prints one-time arms. (V1)
19. `eval_record` gates a proven page anywhere under `docs/`. `proof` fails a proof key on a page whose kind carries none. (V2)
20. R3 passes the gate. Its guided arm passes no more than 3 runs fewer, pooled, than R2's 42 of 45, or than the anchor's 40. After one re-record, the pooled 90 pass no fewer than 78. (V3)
21. After R3's commit, no commit before slice Z changes `evals/run.py` or `evals/proofkeys.py`, or the part of `parts/eval_record.py` that builds a hash. A test fails one that does. (V1)
22. Every page with a wrapper has a suite. Every outcome and routing case names the real work it was drawn from, and a check fails one that names none. (V2)
23. The suite runner picks a suite when its wrapper, its cases or any page its wrapper names changes. It runs the base and the head, reruns a pass-to-fail case twice, and exits 1 only at two failures of three. Its tests run on recorded output. (V1)
24. The runner writes a mark only when every case passed at the head. A check fails a mark whose fingerprint does not match the tree. (V1, V2)
25. For content a mark or a proven page's record covers, a commit warns, the pre-push check refuses a push to main, and CI fails a pull request. (V1, V4)
26. The routing suite has a recorded baseline under `evals/`, and the eval page shows its table. (V6)
27. The four fire cases ran again at five turns, and the result is recorded either way. (V6)
28. `git grep -n -E 'prove-by:? M4' -- docs README.md` prints nothing. Each of the ten pages is proven, cut, or unproven with a failed-attempt record made while M4 was in `building`. (V2, V8)
29. Each attempt's two-line text was committed before its baseline, and its baseline and recording ran in separate batches. (V3)
30. No commit after a page's first attempt record changes a file that attempt's cases hash. A test lists each case's files and fails one that changed. (V1)

Sub-batch L:

31. "Results" holds L0's facts, each marked verified or not. A decision record on the review mark passes the `decisions` check. (V2)
32. A dispatch's prompt differs from its template only inside the placeholders, and a test fails one that differs elsewhere. Its first line names the tier, and its model and effort are the binding's. (V1)
33. A reviewer starts with its edit tools off. A reply with no closed report gets one retry. A reviewer past 30 minutes is stopped and counted not complete. (V1)
34. Each recurring brief is one template file, and a check fails a page whose printed template differs from its file. (V2)
35. A dimension counts as complete only on the reviewer's own output. A recorded architecture report with one of its two lines is counted incomplete. (V1)
36. A delta round re-checks every earlier row marked fixed. A branch with no whole-branch pass gets no mark. (V1)
37. `ws.py review mark` refuses in each case "L3" lists, with a test for each. A decline with neither a tracker key nor initials and a date is refused. (V1)
38. A recorded run shows a forged mark read as `none`: one edited by hand, one copied from another commit, and one with no completion record. (V1)
39. `ws.py review status` gives each of its four answers, with a test for each. (V1)
40. A recorded run shows `gh pr create` refused for lack of a mark, then allowed once the mark is there. Without `--draft` it is refused. The hook's row stays under 200 milliseconds. (V1, V7)
41. The mark writer refuses a row marked fixed that names no check, and a declined row that names no home. `ws.py defects check` fails a deferred finding whose register row is closed or missing. (V1)
42. A recorded review with more than five nits reports five and a count. (V1)
43. Teach-back has a recorded run on one plan and on one pull request, each with its mark at the commit, and one trivial change with a recorded skip. (V1)
44. Every repository the outward-write list names has a `merge_policy` entry here, and a repository with none reads as `person`. An instance the kit makes has no entry. (V2)
45. In a `person` repository, a recorded run shows an agent's `gh pr ready` refused without a passed teach-back mark at the head commit, and allowed with it. An agent's `ws.py merge` is refused there. (V1)
46. `lifecycle_map` fails a playbook or how-to with no row on the map, and a row that links an archived page. (V2)
47. Red team review states its form for a milestone's outside check. Handoff states keep mode. Procedure endings states where a review's record is committed. Each edit names its instruction review. (V2)
48. The plan template, red team review and size the work each say a plan's red team triage lives in the record. A draft plan whose Red team section holds a findings table fails a check. The two red team cases' hidden tests read each disposition in the record. (V2)

Closing:

49. `AGENTS.md` routes a branch to its review, and names the merge policy and the push gate. `loaded_size` passes at both ceilings. `INDEX.md` has a row for each new page, part and chain. (V2)
50. R4 passes the gate. Its guided arm passes no more than 3 runs fewer, pooled, than R3's or the anchor's. (V3)
51. The routed arm passes at least R4's guided count less 3; after one re-record, the pooled 90 pass at least twice that count less 6. The eval page reports every measurement. (V3)
52. No page still says something waits for M4. The command under V8 prints nothing. (V8)
53. From L3's merge on, every pull request of this plan that changed a machinery path or `src/` had a mark at its head when it was published. `docs/milestones/m4.md` lists each. (V4)
54. The private port ledger maps every catalog item it gives M4 to a page, a part, a later milestone or a reason. Its check prints 0 unmapped items. (V5)
55. Every pull request of this plan merged with every required check passing on Linux, macOS and Windows. (V4)
56. `docs/milestones/m4.md` marks each criterion with its evidence, and reports the eval runs used per slice against its budget, the review sessions used per slice against its estimate, the always-loaded size and the outside checks' outcomes. (V2, V9)

Sub-batch L, review sessions. They are numbered after the closing criteria because they joined the draft later:

57. When a range changes only guidance pages, plans or records, the dispatch starts no dimension. When it changes only tests or eval cases, it starts code and test adequacy. Otherwise it starts the four, and reuse and each triggered dimension only when its trigger holds. A test covers each row. (V1)
58. On a delta round the dispatch starts code, security when the delta changes a hook, a guard, a check or CI, each dimension with an earlier finding, and the re-check. A mark needs one whole-branch pass at its tip, and no more. Reuse, docs drift and the re-check start at the worker tier, and at the driver tier when the range changes a gate. (V1)
59. `ws.py dispatch` never starts a review session past the manifest's cap for a pull request, and its refusal names the count. Each dispatch record holds its tier, model, effort and duration. `ws.py review status` prints the branch's count against the cap. (V1)

## Verification

- **V1:** `python3 -m unittest discover -b tests` passes, including the test each criterion names.
- **V2:** `python3 ws.py selftest`, `python3 ws.py check` and `python3 -m unittest discover -b tests` all exit 0.
- **V3:** `python3 evals/pool.py` prints each comparison. `python3 evals/grade.py --recorded` and `python3 ws.py check --phase ci` pass.
- **V4:** `gh pr checks NUMBER` shows every required check passing.
- **V5:** the private port ledger's own check, run on the maintainer's machine, prints 0 unmapped items.
- **V6:** the results `claude plugin eval` wrote are committed under `evals/`, and the suite runner prints its verdict from them.
- **V7:** `python3 tests/hook_cases.py` passes, with every row under its budget.
- **V8:** each of these prints nothing. `git grep -n -E 'prove-by:? M4' -- docs README.md`. And `git grep -n -i -E '(until|waits? for|planned for|lands in) M4|M4 (plans|builds)' -- README.md AGENTS.md INDEX.md evals/README.md docs ':(exclude)docs/plans' ':(exclude)docs/records' ':(exclude)docs/milestones' ':(exclude)docs/decisions' ':(exclude)docs/question-log.md'`.
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
- The eval runs reach 1,400 agent runs, or the selection and routing runs 300. Re-records, probes, failed runs and dispatched sessions count.
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
- An eval or selection batch starts only on the maintainer's yes for that batch, with a run count. A batch holds at most 150 agent runs. After a usage limit, a person or a session reruns with `--resume`; nothing restarts on its own.
- H0's commits use `--no-verify` until R3's records are in. Before each push of that branch, every commit passes `python3 ws.py check --commits origin/main..HEAD` and the deny-list scan. After G1 merges, no push uses `--no-verify`: a push the hook refuses is a stop.
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
| H3 | Debugging: a baseline of 20, then 132 | 152 | 152 |
| H3 | Baselines for the nine other pages, 20 each | 180 | 180 |
| H3 | Recordings, 132 a page; four pages planned | 528 | 528 |
| Z | R4 | 135 | 180 |
| Z | The routed arm | 45 | 90 |
| | **Agent runs on the small model** | **1,175** | **1,310** |

- **The stop is 1,400 agent runs, staged (Q87).** If all nine other pages went to a recording, the total would be about 1,970. The maintainer chooses the pages after the baselines. A page past the stop stays unproven and moves to M6.
- **Short runs on `claude plugin eval`:** Q49's rerun, about 12; the routing baseline, at most 120; the suite runner's first base-and-head run, about 24. A full selection rerun, 174, happens only if a wrapper's description changes. The stop is 300.
- **Review sessions are not eval runs, and are budgeted apart,** in the next section.
- **The stop covers M4's build only.** After M4, each edit to a page M4 proves costs that page's recording again, about 132 runs, and the stop does not count it. Edits to a proven page are batched, as the contract already asks.
- **Red team review's cases change in L7 and cost no run here.** Its stored 10-run baseline goes stale and is named so; M9 runs it again, 20 runs for both cases, with that page's recording.
- G0 to G4, H0, H2's build, and L0 to L7 start no eval run. L0's recorded tool runs are a handful of headless sessions.

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
| H0, H1 | The same. | 6 |
| L0 to L3 | The same: the loop does not exist yet. | 15 |
| L4 to L7 | Through the loop: one pull request each with one fix round, 11, and two for its pages' instruction review. | 52 |
| H2 | Through the loop, with two fix rounds, and two for its pages. | 18 |
| H3 | Through the loop: about five pull requests of cases, 5 each. | 25 |
| Z | Through the loop, 11, and four for the hashed pages' instruction reviews. | 15 |
| Two fix pull requests nobody planned | Through the loop, 11 each. | 22 |
| The plan and the close | Three red team rounds on this plan, the outside red team, and three teach-back graders. | 7 |
| | **Review sessions** | **178** |

- **Few of these drop a tier in M4.** Nearly every range here changes a gate, so reuse, docs drift and the re-check mostly stay at the driver tier. The saving shows in an instance, where most changes are product code.
- **The stop is 250 review sessions.** A slice that passes twice its row says so in its report before it goes on.
- **A guard slice still open when L3 merges goes through the loop,** as "First real use" says. Each adds about 11 to its row.
- **Where the count is reported.** In each dispatch record. In the completion record, per round. By `python3 ws.py review status`, against the cap. In one line of the pull request's review record, such as `Sessions: 11 of 16`. In each slice's report under "Results", against its row here. And in `docs/milestones/m4.md`, in a "Review sessions used" table beside "Eval runs used".
- **Before L1 merges,** a builder counts by hand each fresh session it starts for a review, and reports the count the same way.
- **The cap is an instance's own.** It lives in the manifest, so a team sets its number where it sets its tiers.

## Execution profile

- Orchestrator: one driver-tier coordinator session hands each slice to a builder session in its own worktree. It does not commit for the builders.
- Order: lanes G, H and L run at once. G0 and G1 merge first. G2 to G4 merge after H1. L1 to L4 run in order after G1; L5 to L7 after L3. H3 takes each page after the last slice that edits it. Z waits for all.
- Shared interface: this plan's [names](#names-this-plan-fixes) and the "G2" rule. The coordinator owns both; a builder asks for a change in its report.
- Shared code: the literal rule, in the parser, written by G2; G3, G4 and L3 call it. The agent tools' adapters and `ws.py dispatch`, written by L1; L2 and L5 call them. The mark's store, written by L3; L5 and L6 call it.
- Nudges: 2.

## The maintainer's steps

About 6 hours, as the program estimates.

- Agree the spec, then approve the plan after its red team.
- Say yes, with a count, to each eval batch. After H3's baselines, choose which pages go to a recording.
- Read one full review record.
- Raise a pull request's cap of review sessions, or end its review, when a loop stops there.
- Sit two teach-backs: one on a plan awaiting approval once L5 has merged, and one on a pull request.
- Confirm this repository's merge policy, and set any other repository's.
- Read the ten proof results, and strike any page he disagrees with.
- Decide any declined security or architecture finding.
- Run the private checks: the ledger's, the attack scripts, and G2's measure over the session logs.
- Approve the tag.

## Records this plan must leave

- Decision records for the guards' fail-closed rule, the review mark, and teach-back with the merge policy; amendments to 0004 and 0006. Each is offered as the [decision interview](../playbooks/decision-interview.md#when-a-decision-gets-a-record) says.
- R3 and R4, the routed arm's record, each baseline and proof recording, the routing baseline and the selection results.
- The recorded runs criteria 38, 40, 43 and 45 name, under `tests/records/`, each with a replay test.
- The mark and the completion record of one real change.
- An instruction-review record for each guidance page changed, and the trailers that name them.
- A report per slice under "Results", each claim marked verified or inferred, with the list of hashed-file edits queued for slice Z.
- `docs/milestones/m4.md`, with its eval runs and review sessions used, and entries in `CHANGELOG.md` and `EVIDENCE.md`, all current before the outside checks run.
- A question-log row for each question the workspace should have answered, as the contract's rule says.

## Later

- **Matching findings to threads, and posting comments.** M8, with a git-host provider.
- **Machine-state records.** M5.
- **Wrappers for the review orchestrator and teach-back.** M6, the milestone that proves them.
- **A second agent tool loading the wrappers.** Not planned; the README states the limit.
- **A signed mark.** Nothing here needs one yet.

## Red team

Records: none yet. No red team runs until the maintainer's hands-on review of M3 has fed this draft.

This section takes the form slice L7 sets, which the decision queue plan has had since pull request 59. Each round's triage is written in its record's Disposition column. This section then gains one line per round: the record's link, its verdict, and the count of findings per disposition.

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
- **Not run:** no eval or selection run, no guard attack, and no red team.
