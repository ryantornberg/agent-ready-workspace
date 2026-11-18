---
kind: plan
last-reviewed: 2026-11-18
status: draft
milestone: M10
---

# The decision queue: hand-off plan

The plan for one queue of the questions agents leave for a person, answered one at a time in a single pass. Building sessions work from it.

**In short:** sessions file each question as a queue item, with its options and the consequence of each. A pass answers what the evidence already answers, then asks the person the rest, one at a time. The first version sends nothing to any session: the session that asked picks its answer up when it next starts, or when the person tells it to.

## Key points

Second draft. It applies round 1 of the red team: 26 findings, 6 of them blockers. Round 2 has not run yet.

- **The first version never messages a session.** The private version sends each answer to the asking session at once, which can start many idle sessions in one pass. The first draft guarded against that with a grant command and a refusal hook. Round 1 showed an agent could grant itself, that the hook failed closed on every message, and that it needed liveness data nothing supplies. So version one is pull-only. A session sees its answers at its next start. The pass's report lists each live session holding answers, with the line to type into it. Waking a session is the person typing into it.
- **The trial is measured by use, with one deadline.** The maintainer's word on 2026-11-18. The numbers in C2 need their yes. Round 1 showed the first proposal's item count was already met, and that the private version pushes answers, so its trial cannot test pull. So the trial gates the build, and slice 6, a week of real use, is where pull passes or is cut.
- **Evidence answers travel like any other answer.** An item the pass answers from code, docs or git history is marked answered, with its source, and the asking session picks it up. Only that session closes it.
- **Answers carry who gave them.** An answer recorded outside a pass is labelled so at pickup, because any agent can run the command.
- **Smaller than the private version and the first draft.** Out of scope now: waking sessions, a prompt-time notice, gathering unfiled questions from transcripts, question-log rows, archive and restore, messages for people, tracker lookups, and sync across machines. Each is under "Later".
- **Fresh source.** Builders never open the private version's files. This planning session read them and acts as the walled reader. The section "What the private version does" is the only description builders get. Details the slices take from the original are marked (*o*), and a builder may change any of them.
- **The contract and index edits wait for M4.** The park rule belongs in `AGENTS.md`, and the queue needs an `INDEX.md` row. The eval hashes both, so they go in the M4 plan's list of edits for its closing recording. Until then, the wrapper's description carries the park rule, as an always-loaded line whose size is measured.

## Settled decisions

The maintainer, 2026-11-18:

- They work through their open questions and decisions often with a private decision pass. One interface that takes them through one thing at a time is what makes it work.
- They want that kind of pass in this workspace, and in their own setup wherever it ends up. They asked for it to be planned and red-teamed.
- They flagged a risk: sending each answer to an idle session could start many sessions at once.
- Build it right after M3 closes, not in M10.
- The trial is measured by use rather than by time. It keeps one deadline: the sign-off of M3's milestone record.

Carried from the program, 2026-11-15 and 2026-11-16:

- The queue is experimental. It ships only if the maintainer's own trial of the private version shows real passes. If the trial fails, the queue is cut.
- Every port is rebuilt from scratch from a generic description. Nobody who builds it opens the original. Only a walled reader does, and a walled reader builds nothing.
- Public pages make no comparative claims.

## Choices for the maintainer

| # | Choice | Recommended | Why |
|---|---|---|---|
| C2 | The trial's bar, checked at M3's sign-off | At least 4 passes on at least 3 different days. At least 1 item closed from evidence without asking. At least 3 answers that reached the asking session and were acted on. | On 2026-11-18 the private queue had 2 passes on 2 days and 29 items done or answered (verified from its history), so an item count tests nothing. The private version pushes answers, so this bar tests use, not this plan's pull design; slice 6 tests that. |
| C3 | Slice 6's bar | Over one week of M4's build: at least 3 answers picked up by pull and acted on, and no session started by a pass. Otherwise the queue is cut. | It is the only test of the design this plan changes. |

## What the private version does

A generic description, written by the walled reader for the builders.

- **Item.** One JSON file per item, named by a running number. Kinds: a choice, a message to a person, hands-on work only the person can do, and a heads-up. A choice has 2 to 4 options. Each option has a label, a consequence and, optionally, the follow-up question it leads to. It has a recommendation (a label and a reason, or "none" and a reason), a thread, the work it unblocks, its source and references. A command-line tool is the only writer. It refuses an item without a full question and full options. Each write is committed to a private notes repository.
- **Pass.** It gathers open items, plus live sessions whose last reply ends on a question nobody answered. Read-only helper agents at a cheaper tier try to answer each item from evidence. An answer they can prove closes the item; a leaning becomes the recommendation. The rest are asked one at a time, grouped by thread, with the recommended option first. A follow-up comes next in the same thread. At the thread's end, the person confirms the list of answers before they apply. Then it drafts messages for other people, runs a weekly archive pass, prints a report and commits.
- **Delivery.** If the asking session is still listed as live, the pass messages it the answer at once. Otherwise the answer waits, and a session-start hook hands it to the next session that works on the same item.

## Goal

A person answers every question agents left for them in one pass, one question at a time. Each question carries its options and what each one leads to. Every answer, from the person or from evidence, reaches the session that asked. No pass starts a session.

## Non-goals

- No port of the private version's code or wording. Builders work from the section above and this plan only.
- No message to any agent session, and no message to a person.
- No prompt-time hook. Pickup is at session start, or when the person asks the session for its answers.
- No gathering of unfiled questions from transcripts, no question-log rows, no archive or restore, no tracker, pull-request or monitoring lookups.
- No sync across machines and no queue shared between people. One clone has one queue.
- No edit to `AGENTS.md`, `CLAUDE.md`, `INDEX.md` or any other file the eval hashes.
- No front end for an agent tool other than Claude Code. The store and command-line tool are tool-neutral. The pickup notice is wired for Claude Code; Codex is a stated limit unless slice 0 records a run.
- No write outside this repository and its common git folder.

## Why this needs a plan

It fails three of the size gate's four conditions. It is several screens of diff. It adds an engine module, a session hook and a skill, which is machinery. And it is more than a day of work.

## Preconditions

Slice 1 starts only when all of these hold:

- The maintainer has said the trial met the C2 bar, at or before M3's sign-off.
- M3's B6 has merged: the wrapper format, its check and its selection cases. (C1's launcher and C2's case runner have merged; verified from `git log`.)
- The M4 plan exists and has a list of edits queued for its closing recording.

## Slices

| Order | Slice | Work | Tier | Done when |
|---|---|---|---|---|
| 0 | Facts | Record each as verified or not in "Results", with the command or transcript. (a) `claude --resume` keeps the session id, so the session-start event of a resumed session carries the id it filed under. (b) A tool call inside a session can read the same session id the hook event carries, for Claude Code and for Codex. (c) What `claude agents --json` reports per session, for the pass's report. Fact (a) may need the person's hands; if so, the session asks once. | Worker | Three lines in "Results" |
| 1 | Store and tool | `wslib/decisions.py` and `python3 ws.py queue` with `add`, `list`, `answer`, `done`, `close` and `count` (*o*). Items live in `ws-queue/` in the common git folder, so every worktree shares one queue and git never tracks it. Writes are atomic, under the queue's own lock file, with a retry on `add`. Every write also appends one line to `ws-queue/events.jsonl`, which is never rewritten. Kinds: `decide`, `do`, `notice` (*o*). An item records the session id that filed it, its working copy and branch, and whether that session stopped on it (`blocking`, *o*). Statuses: `open`, `answered`, `done` (the asking session acted), `closed` (dropped, with a reason). `answer` records its source: `pass` (with the pass's id, after the person confirmed), `evidence` (with the evidence) or `direct`. | Driver | Criteria 1 to 5 |
| 2 | Pickup | Amend [decision 0004](../decisions/0004-the-hook-contract.md): `session-start` hooks may `NEED` a new fact, `answers`, the answered items whose session id equals the event's. The runner reads them from the store; the part reads only the fact, so it stays a pure function. A session hook prints them at every start until the session runs `done`. An answer whose source is `direct` is labelled "not from a pass". It adds no tool event and no write. The hook stays under the session-start time budget. | Driver | Criteria 6 and 7 |
| 3 | The pass | `docs/playbooks/work-the-queue.md` (`kind: playbook`, `proof: unproven`, `prove-by: M10`; unproven pages are not eval-gated, per [decision 0006](../decisions/0006-what-proven-means.md)). Steps: gather open items; answer from evidence with read-only helpers at the worker tier; order (notices, then blocking, then oldest); ask one at a time with the recommendation first; follow-ups; confirm a thread's answers; apply; report. The report lists each session holding answers, live or gone, with what to type to pick them up, and answers waiting more than three days for a session that is gone (*o*). The page states the park rule: a question that does not block the rest of the work is filed and the work goes on; one that blocks is filed and the session stops. | Worker | Criterion 8 |
| 4 | Wrapper | A Claude Code wrapper in B6's format, with two triggers: the person asks to work the queue, and a session is about to end its turn on a question for the person. Should-fire and should-not-fire selection cases for both. Its description's bytes are counted against the wrappers' 9,000-byte ceiling. | Driver | Criteria 9 and 10 |
| 5 | Pages | Glossary rows (queue item, pass, pickup). A row in `docs/parts.md` for the pickup hook. A row in the README's "What is checked" table, and the Codex limit under "What stays prose". A decision record, numbered with the next free number: answers are pulled, and no pass starts a session. Three edits added to the M4 plan's queued list: the `AGENTS.md` park rule, the `INDEX.md` topic row, and `AGENTS.md`'s eval rule worded to match decision 0006 (a playbook marked proven). A changelog entry. | Worker | Criterion 11 |
| 6 | Real use | Use the queue on this repository's own work for one week of M4's build. Record the counts from `events.jsonl` in "Results", and note in M4's record that its questions-asked count includes parked questions. | Driver | Criteria 12 and 13 |

Slices 1 and 2 share one branch and one draft pull request. Slices 3 to 5 share a second branch, opened after the first merges. Slice 4 is at the driver tier because the wrapper's description is always loaded, which changes what every session reads.

## Success criteria

1. `python3 -m unittest tests.test_queue -b` passes.
2. Its cases show `add` refusing: no question; a `decide` item whose question does not end with `?`; a `decide` item with fewer than 2 or more than 4 options; an option with no consequence; a recommendation that names no option and does not start `none:`; an unknown kind.
3. Its cases show 20 processes adding at once get 20 distinct ids, on every system in CI. An item added in a linked worktree is listed from the main working copy.
4. Its cases show the store resolves under `git rev-parse --git-common-dir`, and `git status --porcelain` is the same before and after `add`, `answer` and `done`.
5. Its cases show each write appends exactly one line to `events.jsonl` and changes no earlier line, and that `done` refuses an item that is not answered.
6. `python3 ws.py selftest` passes with the pickup hook's cases: it reminds when `answers` holds an item; it is silent when `answers` is empty; it labels a `direct` answer.
7. `python3 -m unittest tests.test_core -b` passes, with cases showing the runner fills `answers` for the event's session id only, the hook prints nothing and exits 0 when the store is missing or corrupt, and the hook is under the session-start budget.
8. `python3 ws.py check` passes. The new playbook carries `proof: unproven` and `prove-by: M10`.
9. B6's wrapper check passes for the new wrapper, and B6's selection-case command passes its cases.
10. `python3 ws.py check` reports the wrappers' description bytes under 9,000 (the `loaded_size` part).
11. `python3 ws.py check` passes after slice 5, and the M4 plan's queued list holds the three edits.
12. Slice 6's "Results" holds counts computed by `python3 ws.py queue count --since <date>` from `events.jsonl`: passes; items filed; closed from evidence; answered by the person; picked up and acted on; sessions started by a pass (must be 0).
13. The maintainer reads slice 6's counts against the C3 bar and records "keep" or "cut" in "Results". This criterion is a person's reading, not a script's.
14. CI passes on Linux, macOS and Windows for both pull requests: `gh pr checks <number>` shows every job "pass".

## Verification

```
python3 -m unittest tests.test_queue -b          # criteria 1 to 5: "OK"
python3 ws.py selftest                           # criterion 6: exit 0
python3 -m unittest tests.test_core -b           # criterion 7: "OK"
python3 -m unittest discover -b tests            # every test: "OK"
python3 ws.py check                              # criteria 8, 10 and 11: exit 0
python3 ws.py queue count --since <date>         # criterion 12: the six counts
gh pr checks <number>                            # criterion 14: every job "pass"
```

Criterion 9's command is the one B6 writes into `evals/README.md`.

## Recovery

Halt and report. Do not work around a failure. A test that fails on one operating system only is a finding to report, not a test to skip.

## Stop rule

- If a precondition does not hold, do not start.
- If slice 0 finds a resumed session gets a new id, pickup cannot match it. Stop and report before slice 2.
- If slice 0 finds a tool call cannot read the session id, `add` takes it as an argument and the playbook says how to find it. Report and go on.
- If C3's bar is missed, cut the queue by the path below.

**Cutting the queue.** Mark the pickup hook's manifest entry `retired` (see [changing the machinery](../changing-the-machinery.md#traps)). Revert the 0004 amendment with a dated entry. Remove the wrapper. Keep the playbook as `proof: unproven`, with a line saying the queue was cut and why. Leave the store's folder alone; it is the person's data.

## Limits

- Machinery goes to its own branch, from a worktree under `.claude/worktrees/`, in a draft pull request. Agents here may publish and merge it after CI passes on all three systems.
- Docs-only commits go straight to main.
- Any unattended fix loop stops after three rounds.
- Stage files by name.

## Records this plan must leave

- The new decision record, and the amendment to decision 0004.
- Slice 0's facts and slice 6's counts and verdict, in "Results".
- The three queued edits, in the M4 plan.
- A changelog entry.

## Later

| Item | Could come in | Needs first |
|---|---|---|
| Waking a session the person picks, with a guard an agent cannot grant itself | After slice 6, if pickup is too slow in use | A grant tied to the person's answer, and a guard that fails open |
| A notice when the person next types into a live session | After slice 6 | The maintainer's word that it is not the prompt-nudge hook they retired; a time budget |
| Gathering unfiled questions from session transcripts | M4 or later | A tool-neutral transcript reader |
| Question-log rows from items closed by evidence | After M3's B3 | B3's gap kinds, to log a search miss as one |
| Archive and restore | When a real queue holds items worth revisiting | |
| Messages drafted for other people | M8 | |
| Answering from trackers, pull requests and monitoring | M8 | |
| A queue shared by a team, with an owner per item | M9 | |
| A front end for a second agent tool | M12 | |

## Red team

Round 1, 2026-11-18. A fresh session read the first draft and the sources, and not the private version.

| # | Finding | Verdict | Action |
|---|---|---|---|
| 1 | Items closed from evidence never reach the session that asked. | Accepted, verified | An evidence answer is `answered` with source `evidence` and goes through pickup. Only the asking session's `done` closes it. |
| 2 | "Wake only by the person's pick" is not enforced: any agent can run the grant command. | Accepted, inferred | Waking is out of version one. "Later" names a guard an agent cannot grant itself as its precondition. |
| 3 | "Live", "idle a day" and "gone" have no data source a hook may use. | Accepted, verified | With no wake, the engine needs no liveness. The pass's report uses `claude agents --json`, fact (c). |
| 4 | Matching a gone session's answers by branch sends them to every main-copy session. | Accepted, verified | Matching is by session id only. Fact (a) checks a resumed session keeps its id. |
| 5 | The 0004 amendment names no facts, so pickup cannot be a pure part. | Accepted, verified | Slice 2 names the `answers` fact the runner fills. The printed-once mark is dropped: the hook prints at every start until `done`. |
| 6 | Criterion 4's `git ls-files` command is empty in the main copy and fails in a worktree. | Accepted, verified | Replaced by a `test_queue` case on the store path and `git status --porcelain`. |
| 7 | Criteria 5 and 6 named commands that cannot check them; 10 and 13 named none. | Accepted, verified | State and error cases moved to `test_core`; every criterion names a command, and criterion 13 says it is a person's reading. |
| 8 | The `before-message` hook fails closed and blocks other messages. | Accepted, verified | The hook is dropped with waking. |
| 9 | Slice 0 missed facts the design depends on. | Accepted, verified | Slice 0 now checks the facts the pull-only design needs, and says when it needs the person. |
| 10 | C2's item count was already met, and the private version tests push, not pull. | Accepted, verified | C2 drops the item count and says what it cannot test. C3 gives slice 6 a keep-or-cut bar. |
| 11 | The trial gate and a cut were not sequenced or defined. | Accepted, verified | "Preconditions" gates slice 1 on the trial. The stop rule holds a cut path. |
| 12 | The queued contract and index edits had no owner or list. | Accepted, verified | They go to the M4 plan's queued list, and M4's existence is a precondition. |
| 13 | Decision number 0007 will be taken by M3's B5. | Accepted, verified | "The next free number". |
| 14 | Question-log rows change the log's meaning and need a ledger step. | Accepted, verified | Deferred to "Later", after B3's gap kinds. |
| 15 | A wrapper added after M3 is never measured in the routed arm. | Accepted, verified | Slice 4 adds selection cases and a byte count. The routed-arm harm stays unmeasured until M4's recording, a known limit. |
| 16 | A prompt-time hook resembles the retired prompt-nudge hook and has no budget. | Accepted, inferred | Dropped from version one; "Later" needs the maintainer's word first. |
| 17 | The pickup notice was called tool-neutral but wired for Claude Code only. | Accepted, verified | Non-goals now say so, with the Codex limit in the README. |
| 18 | Nothing records who answered. | Accepted, inferred | `answer` records its source; pickup labels a `direct` answer. |
| 19 | An untracked store keeps no history for slice 6's counts. | Accepted, verified | An append-only `events.jsonl`; criterion 12 counts from it. |
| 20 | C1 claimed it needs only machinery that exists now. | Partly accepted | B6 has not merged and is a precondition. C1 and C2 have merged (verified, `git log`), against the finding. |
| 21 | Slice details written by the walled reader may carry the original's design. | Accepted, inferred | Details taken from the original are marked (*o*), and builders may change them. |
| 22 | The `?` rule made `do` and `notice` items impossible. | Accepted, verified | It applies to `decide` items only. |
| 23 | `close` had no status; a grant allowed many messages. | Accepted, verified | `closed` is a status. Grants are gone. |
| 24 | Criterion 3 may be flaky on Windows on a shared, briefly polled lock. | Accepted, inferred | The queue has its own lock file and `add` retries. |
| 25 | `AGENTS.md` says any playbook change needs an eval run; decision 0006 exempts unproven pages. | Accepted, verified | Slice 3 cites 0006. Slice 5 queues the contract's wording for M4. |
| 26 | Slice 6 changes what M4's questions-asked count measures. | Accepted, inferred | Slice 6 notes it in M4's record. |

## Approval

Not yet approved.

## Changes after approval

## Results
