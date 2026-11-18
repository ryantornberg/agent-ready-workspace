---
kind: plan
last-reviewed: 2026-11-18
status: draft
milestone: M4
---

# The decision queue: hand-off plan

The plan for one queue of the questions agents leave for a person, answered one at a time in a single pass. Building sessions work from it.

**In short:** sessions file each question as a queue item, with its options and the consequence of each. A pass answers what the evidence already answers, then asks the person the rest, one at a time. The first version sends nothing to any session: the session that asked picks its answer up when it next starts, or the person hands it to another session.

## Key points

Third draft. It applies rounds 1 and 2 of the red team (26 and 16 findings; 6 and 3 blockers). Round 3 has not run yet.

- **The first version never messages a session.** The private version sends each answer to the asking session at once, which can start many idle sessions in one pass. Round 1 showed a guard against that could be bypassed and would block other messages. So version one is pull-only. A session sees its answers at each start until it marks them done. If the asking session is gone, the pass's report prints the line that hands the answer to another session, on the person's word.
- **A pass is a real thing the tool issues.** `queue pass start` returns an id, and `pass end` closes it. An answer that claims to come from a pass must name an open id the tool issued. Every answer not given by the person in a pass is labelled at pickup: "from evidence", or "not from a pass".
- **The park rule is narrow.** An agent files a question only when the person tells it to park one, or when it runs with no person present. A question the person can answer now is asked in the session as usual. Round 2 showed a broad rule would file every clarifying question, including the pass's own.
- **The trial is measured by use, with one deadline.** The maintainer's word on 2026-11-18. The numbers in C2 and C3 need their yes. The trial of the private version gates the build. A week of real use in slice 6 decides keep or cut, and comes before M4's closing recording.
- **Smaller than the private version.** Out of scope now: waking sessions, a prompt-time notice, gathering unfiled questions from transcripts, question-log rows, archive and restore, messages for people, tracker lookups, and sync across machines. Each is under "Later".
- **Fresh source.** Builders never open the private version's files. This planning session read them and acts as the walled reader. The section "What the private version does" is the only description builders get. Details the slices take from the original are marked (*o*), and a builder may change any of them.
- **Two edits to eval-hashed files wait for M4's closing recording, and only on a "keep".** The park rule in `AGENTS.md` and a topic row in `INDEX.md`. Until then, the wrapper's description carries the park rule.

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
| C2 | The trial's bar, checked at M3's sign-off | At least 4 passes on at least 3 different days. At least 1 item closed from evidence without asking. At least 3 answers that reached the asking session and were acted on. | On 2026-11-18 the private queue had 2 passes on 2 days and 29 items done or answered (verified from its history), so an item count tests nothing. The private version pushes answers, so this bar tests use, not this plan's pull design; C3 tests that. |
| C3 | Slice 6's bar | Over one week of M4's build: at least 3 answers from a pass, or from evidence, picked up and acted on by a session; and no message sent to a session by a pass. Otherwise the queue is cut. | It is the only test of the design this plan changes. Answers given in the session (`direct`) do not count toward it. |

## What the private version does

A generic description, written by the walled reader for the builders.

- **Item.** One JSON file per item, named by a running number. Kinds: a choice, a message to a person, hands-on work only the person can do, and a heads-up. A choice has 2 to 4 options. Each option has a label, a consequence and, optionally, the follow-up question it leads to. It has a recommendation (a label and a reason, or "none" and a reason), a thread, the work it unblocks, its source and references. A command-line tool is the only writer. It refuses an item without a full question and full options. Each write is committed to a private notes repository.
- **Pass.** It gathers open items, plus live sessions whose last reply ends on a question nobody answered. Read-only helper agents at a cheaper tier try to answer each item from evidence. An answer they can prove closes the item; a leaning becomes the recommendation. The rest are asked one at a time, grouped by thread, with the recommended option first. A follow-up comes next in the same thread. At the thread's end, the person confirms the list of answers before they apply. Then it drafts messages for other people, runs a weekly archive pass, prints a report and commits.
- **Delivery.** If the asking session is still listed as live, the pass messages it the answer at once. Otherwise the answer waits, and a session-start hook hands it to the next session that works on the same item.

## Goal

A person answers every question agents left for them in one pass, one question at a time. Each question carries its options and what each one leads to. Every answer, from the person or from evidence, reaches the session that asked, or the session the person hands it to. No pass sends a message to a session.

## Non-goals

- No port of the private version's code or wording. Builders work from the section above and this plan only.
- No message to any agent session from a pass, and no message to a person. A pass may start its own read-only helpers; that is not a message to a session.
- No prompt-time hook. Pickup is at session start, or when the person asks a session for its answers.
- No gathering of unfiled questions from transcripts, no question-log rows, no archive or restore, no tracker, pull-request or monitoring lookups.
- No sync across machines and no queue shared between people. One clone has one queue.
- No edit to `AGENTS.md`, `CLAUDE.md`, `INDEX.md` or any other file the eval hashes.
- The store, the tool and the pickup hook work for Claude Code and Codex: both wire `session-start` to the same runner. The pass's walk and the park-rule trigger are a Claude Code wrapper only; for Codex that is a stated limit.
- No write outside this repository and its common git folder.

## Why this needs a plan

It fails three of the size gate's four conditions. It is several screens of diff. It adds an engine module, a session hook and a skill, which is machinery. And it is more than a day of work.

## Preconditions

Slice 1 starts only when all of these hold:

- The maintainer has said the trial met the C2 bar, at or before M3's sign-off.
- M3's B6 has merged: the wrapper format, its check and its selection cases. (C1's launcher and C2's case runner have merged; verified from `git log`.)
- After B6, the wrappers' descriptions leave at least 600 bytes under their 9,000-byte ceiling.
- The M4 plan exists, has a list of edits queued for its closing recording, and orders slice 6's verdict before that recording.

## Slices

| Order | Slice | Work | Tier | Done when |
|---|---|---|---|---|
| 0 | Facts | Record each as verified or not in "Results", with the command or transcript. (a) Which ways of going back to a session keep its session id, so its session-start event carries the id it filed under: `claude --resume`, `--continue`, `/resume`, `/clear`, compaction, `--fork-session`, a `--bg --resume` copy, and a Codex resume. (b) A tool call inside a session can read the same session id its hook event carries, for Claude Code and Codex. (c) What `claude agents --json` reports per session, for the pass's report. (d) In a plain session in this repository, the wrapper's description is in context, in full. Facts (a) and (d) may need the person's hands; if so, the session asks once for all of them. | Worker | Four lines in "Results" |
| 1 | Store and tool | `wslib/decisions.py` and `python3 ws.py queue` with `add`, `list`, `answer`, `done`, `close`, `take`, `count`, `pass start` and `pass end` (*o*, apart from `take` and `pass`). Items live in `ws-queue/` in the common git folder, so every worktree shares one queue and git never tracks it. Writes are atomic, under the queue's own lock file, with a retry on `add`. Every write appends one line to `ws-queue/events.jsonl`, which is never rewritten. Kinds: `decide`, `do`, `notice` (*o*). An item records the session id that filed it, its working copy and branch, and whether that session stopped on it (`blocking`, *o*). Statuses: `open`, `answered`, `done` (the session holding it acted), `closed` (dropped, with a reason). `answer` records its source: `pass` (naming an open pass id the tool issued; any other id is refused), `evidence` (with the evidence) or `direct` (given in the session). `close` takes `open` or `answered` items and runs only inside an open pass. `take ID` re-keys an answered item to the caller's session id and logs an event; the playbook says a session runs it only on the person's instruction. | Driver | Criteria 1 to 5 |
| 2 | Pickup | Amend [decision 0004](../decisions/0004-the-hook-contract.md): `session-start` hooks may `NEED` a new fact, `answers`, the answered items whose session id equals the event's. The runner reads them from the store; the part reads only the fact, so it stays a pure function. A session hook prints them at every start until the session runs `done`. An answer from evidence is labelled "from evidence: <source>"; a `direct` answer, "not from a pass". It adds no tool event and no write. The case runner gains a store fixture, so cases can seed answers. The hook keeps the whole `session-start` event inside its budget, which it shares with the other session-start hooks. If fact (b) failed, the hook also prints the session id at every start. | Driver | Criteria 6 and 7 |
| 3 | The pass | `docs/playbooks/work-the-queue.md` (`kind: playbook`, `proof: unproven`, `prove-by: M10`; unproven pages are not eval-gated, per [decision 0006](../decisions/0006-what-proven-means.md)). Steps: `pass start`; gather open items; answer from evidence with read-only helpers at the worker tier; order (notices, then blocking, then oldest); ask one at a time with the recommendation first; follow-ups; confirm a thread's answers, evidence answers included; apply; `pass end`; report. The report lists each session holding answers, live or gone, and for a gone session the `take` line to run in another session. The page states the park rule: file a question only when the person says to park it, or when no person is present; a question the person answers in the session is recorded with `answer --source direct` and then `done`. A blocking parked question stops the session. | Driver | Criterion 8 |
| 4 | Wrapper | A Claude Code wrapper in B6's format, with two triggers: the person asks to work the queue; and the person says to park a question, or a session with no person present reaches one. Should-not-fire cases: the pass's own questions, plan and approval questions, and a question asked of a person who is present. Trigger 2's should-fire cases are task prompts built to reach a question. Bar: each should-fire case fires in at least 8 of 10 runs, and each should-not-fire case in at most 1 of 10. At most 80 runs in all. | Driver | Criteria 9 and 10 |
| 5 | Pages | Glossary rows (queue item, pass, pickup). A row in `docs/parts.md` for the pickup hook. A row in the README's "What is checked" table, and the Codex limit under "What stays prose". A decision record, numbered with the next free number: answers are pulled, and no pass messages a session. Two edits added to the M4 plan's queued list, each marked "only on slice 6's keep": the `AGENTS.md` park rule and the `INDEX.md` topic row. A line for the program's M10 done-when: the queue's playbook is proven, cut or unproven with a failed attempt on record. A changelog entry. Driver tier, because the README and the decision record are read outside the team. | Driver | Criterion 11 |
| 6 | Real use | Use the queue on this repository's own work for one week of M4's build. Record the counts in "Results", and note in M4's record that its questions-asked count includes parked questions. The maintainer records keep or cut before M4's closing slice starts. | Driver | Criteria 12 and 13 |

Slices 1 and 2 share one branch and one draft pull request. Slices 3 to 5 share a second branch, opened after the first merges.

## Success criteria

1. `python3 -m unittest tests.test_queue -b` passes.
2. Its cases show `add` refusing: no question; a `decide` item whose question does not end with `?`; a `decide` item with fewer than 2 or more than 4 options; an option with no consequence; a recommendation that names no option and does not start `none:`; an unknown kind.
3. Its cases show 20 processes adding at once get 20 distinct ids, on every system in CI. An item added in a linked worktree is listed from the main working copy.
4. Its cases show the store resolves under `git rev-parse --git-common-dir`, and `git status --porcelain` is the same before and after `add`, `answer` and `done`.
5. Its cases show: each write appends exactly one line to `events.jsonl` and changes no earlier line; `done` refuses an item that is not answered; `answer --source pass` refuses an id the tool did not issue and one already ended; `close` refuses outside an open pass and on a `done` item; `take` re-keys the item and logs it.
6. `python3 ws.py selftest` passes with the pickup hook's cases, for Claude Code and Codex events: it reminds when `answers` holds an item; it is silent when `answers` is empty; it labels an evidence answer and a `direct` answer.
7. `python3 -m unittest tests.test_core -b` passes, with cases showing the runner fills `answers` for the event's session id only, and the hook prints nothing and exits 0 when the store is missing or corrupt. `python3 tests/hook_cases.py` passes, with a seeded store, inside the session-start budget.
8. `python3 ws.py check` passes, and `grep -n "prove-by: M10" docs/playbooks/work-the-queue.md` prints one line.
9. B6's wrapper check passes for the new wrapper, and B6's selection-case command meets slice 4's bar.
10. A `tests.test_queue` case computes the wrappers' description bytes the way `loaded_size` does, prints the total, and fails when it is over 9,000.
11. `python3 ws.py check` passes after slice 5, and `grep -n "only on slice 6's keep" docs/plans/<the M4 plan>` prints two lines.
12. Slice 6's "Results" holds counts from `python3 ws.py queue count --since <date>`, computed from `events.jsonl`: passes started and ended; items filed; closed from evidence; answered in a pass; answered `direct`; picked up and acted on (`done` events whose answer is not `direct`); items re-keyed with `take`. It also states that the pass's wrapper and playbook hold no instruction to message a session, checked with `grep -n "SendMessage" docs/playbooks/work-the-queue.md plugin/`.
13. The maintainer reads slice 6's counts against the C3 bar and records "keep" or "cut" in "Results". This criterion is a person's reading, not a script's.
14. CI passes on Linux, macOS and Windows for both pull requests: `gh pr checks <number>` shows every job "pass".

## Verification

```
python3 -m unittest tests.test_queue -b          # criteria 1 to 5 and 10: "OK"
python3 ws.py selftest                           # criterion 6: exit 0
python3 -m unittest tests.test_core -b           # criterion 7: "OK"
python3 tests/hook_cases.py                      # criterion 7, the budget: exit 0
python3 -m unittest discover -b tests            # every test: "OK"
python3 ws.py check                              # criteria 8 and 11: exit 0
grep -n "prove-by: M10" docs/playbooks/work-the-queue.md    # criterion 8: one line
python3 ws.py queue count --since <date>         # criterion 12: the counts
gh pr checks <number>                            # criterion 14: every job "pass"
```

Criterion 9's command is the one B6 writes into `evals/README.md`.

## Recovery

Halt and report. Do not work around a failure. A test that fails on one operating system only is a finding to report, not a test to skip.

## Stop rule

- If a precondition does not hold, do not start.
- If fact (a) finds that `claude --resume` gives a new id, pickup cannot match it. Stop and report before slice 2. Any other path that gives a new id is handled by `take`, and the playbook names each one.
- If fact (b) fails, `add` takes the session id as an argument, and the pickup hook prints the id at every start. Report and go on.
- If fact (d) fails, the park rule cannot ride in the wrapper. Stop and report before slice 4.
- If slice 4's bar is missed after one rewrite of the description, stop and report.
- If C3's bar is missed, cut the queue by the path below.

**Cutting the queue.** In one pull request: mark the pickup hook's manifest entry `retired` (see [changing the machinery](../changing-the-machinery.md#traps)); remove `ws.py queue`, `wslib/decisions.py` and the runner's `answers` code; amend decision 0004 with a dated entry that removes `answers`; mark the new decision record superseded; remove the wrapper; remove the playbook's procedure steps, leaving a page that says the queue was cut and why, as decision 0006 says a cut page does; remove the glossary, `parts.md` and README rows; withdraw the two edits from the M4 plan's queued list; tell the program's M10 line it was cut. Leave the store's folder alone; it is the person's data.

## Limits

- Machinery goes to its own branch, from a worktree under `.claude/worktrees/`, in a draft pull request. Agents here may publish and merge it after CI passes on all three systems.
- Docs-only commits go straight to main.
- Any unattended fix loop stops after three rounds.
- Stage files by name.

## Records this plan must leave

- The new decision record, and the amendment to decision 0004.
- Slice 0's facts, slice 4's selection results, and slice 6's counts and verdict, in "Results".
- The two queued edits, in the M4 plan.
- The line for the program's M10 done-when.
- A changelog entry.

## Later

| Item | Could come in | Needs first |
|---|---|---|
| Waking a session the person picks | After slice 6, if pickup is too slow in use | A grant tied to the person's answer in an issued pass, and a guard that fails open |
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
| 1 | Items closed from evidence never reach the session that asked. | Accepted, verified | An evidence answer is `answered` with source `evidence` and goes through pickup. Only the session holding it closes it with `done`. |
| 2 | "Wake only by the person's pick" is not enforced: any agent can run the grant command. | Accepted, inferred | Waking is out of version one. "Later" names a guard an agent cannot grant itself as its precondition. |
| 3 | "Live", "idle a day" and "gone" have no data source a hook may use. | Accepted, verified | With no wake, the engine needs no liveness. The pass's report uses `claude agents --json`, fact (c). |
| 4 | Matching a gone session's answers by branch sends them to every main-copy session. | Accepted, verified | Matching is by session id only. Fact (a) checks which paths keep the id; `take` covers the rest. |
| 5 | The 0004 amendment names no facts, so pickup cannot be a pure part. | Accepted, verified | Slice 2 names the `answers` fact the runner fills. The printed-once mark is dropped: the hook prints at every start until `done`. |
| 6 | Criterion 4's `git ls-files` command is empty in the main copy and fails in a worktree. | Accepted, verified | Replaced by a `test_queue` case on the store path and `git status --porcelain`. |
| 7 | Criteria 5 and 6 named commands that cannot check them; 10 and 13 named none. | Accepted, verified | Every criterion names a command, and criterion 13 says it is a person's reading. |
| 8 | The `before-message` hook fails closed and blocks other messages. | Accepted, verified | The hook is dropped with waking. |
| 9 | Slice 0 missed facts the design depends on. | Accepted, verified | Slice 0 checks the facts the pull-only design needs, and says when it needs the person. |
| 10 | C2's item count was already met, and the private version tests push, not pull. | Accepted, verified | C2 drops the item count. C3 gives slice 6 a keep-or-cut bar. |
| 11 | The trial gate and a cut were not sequenced or defined. | Accepted, verified | "Preconditions" gates slice 1 on the trial. The stop rule holds a cut path. |
| 12 | The queued contract and index edits had no owner or list. | Accepted, verified | They go to the M4 plan's queued list. |
| 13 | Decision number 0007 will be taken by M3's B5. | Accepted, verified | "The next free number". |
| 14 | Question-log rows change the log's meaning and need a ledger step. | Accepted, verified | Deferred to "Later", after B3's gap kinds. |
| 15 | A wrapper added after M3 is never measured in the routed arm. | Accepted, verified | Slice 4 adds selection cases with a bar, and a byte count. The routed-arm harm stays unmeasured until M4's recording, a known limit. |
| 16 | A prompt-time hook resembles the retired prompt-nudge hook and has no budget. | Accepted, inferred | Dropped from version one; "Later" needs the maintainer's word first. |
| 17 | The pickup notice was called tool-neutral but wired for Claude Code only. | Accepted, verified | Corrected in round 2: pickup works for both; the wrapper is the Claude Code-only part. |
| 18 | Nothing records who answered. | Accepted, inferred | `answer` records its source, a pass id must be one the tool issued, and pickup labels every answer not from a pass. |
| 19 | An untracked store keeps no history for slice 6's counts. | Accepted, verified | An append-only `events.jsonl`; criterion 12 counts from it. |
| 20 | C1 claimed it needs only machinery that exists now. | Partly accepted | B6 has not merged and is a precondition. C1 and C2 have merged (verified, `git log`), against the finding. |
| 21 | Slice details written by the walled reader may carry the original's design. | Accepted, inferred | Details taken from the original are marked (*o*), and builders may change them. |
| 22 | The `?` rule made `do` and `notice` items impossible. | Accepted, verified | It applies to `decide` items only. |
| 23 | `close` had no status; a grant allowed many messages. | Accepted, verified | `closed` is a status. Grants are gone. |
| 24 | Criterion 3 may be flaky on Windows on a shared, briefly polled lock. | Accepted, inferred | The queue has its own lock file and `add` retries. |
| 25 | `AGENTS.md` says any playbook change needs an eval run; decision 0006 exempts unproven pages. | Accepted, verified | Slice 3 cites 0006. The contract's wording is not this plan's to fix (round 2, finding 15). |
| 26 | Slice 6 changes what M4's questions-asked count measures. | Accepted, inferred | Slice 6 notes it in M4's record. |

Round 2, 2026-11-18. A fresh session read the second draft and the sources. It found every round-1 action in the body; 7 of its 16 findings finish round-1 actions.

| # | Finding | Verdict | Action |
|---|---|---|---|
| R2-1 | C3 cannot be computed: nothing writes a pass or a session start, so "must be 0" held by construction. A `direct` answer would count as pickup. | Accepted, verified | `pass start` and `pass end` write events and issue ids. C3 counts only answers not `direct`. "No message sent" is checked against the playbook and wrapper text, and stated as prose. |
| R2-2 | Answers to a session that is gone are stranded; several paths give a new session id; `close` had no rule. | Accepted, verified | `take` re-keys an answer on the person's word, and the report prints its line. Fact (a) covers every path. `close` runs only in a pass, on `open` or `answered`. |
| R2-3 | A broad park rule files every clarifying question, the pass's own included, and re-asks settled ones. | Accepted, inferred | The rule is narrowed: park only on the person's word or with no person present. An in-session answer is recorded `direct` and `done`. Should-not-fire cases named. |
| R2-4 | Trigger 2 is not measurable by what criterion 9 named, and nothing checks the wrapper loads. | Accepted, verified | Fact (d); a bar of 8 of 10 and 1 of 10; scenario prompts; at most 80 runs. |
| R2-5 | Criterion 7 named the wrong command for the session-start budget, which is shared. | Accepted, verified | `python3 tests/hook_cases.py` with a store fixture. |
| R2-6 | Evidence answers read like the person's decision. | Accepted, inferred | They join the thread's confirmation list and are labelled at pickup. |
| R2-7 | A pass id can be forged. | Accepted, verified | The tool refuses an id it did not issue or that has ended. |
| R2-8 | The cut path leaves the queue half alive. | Accepted, verified | The cut path lists every artifact and withdraws the queued edits. |
| R2-9 | Slice 6 is not ordered against M4's closing recording. | Accepted, inferred | The queued edits are marked "only on slice 6's keep", and the M4 plan must order the verdict first. |
| R2-10 | `milestone: M10` contradicts the decision to build after M3; `prove-by: M10` is not tied to M10. | Accepted, verified | `milestone: M4`. Slice 5 writes a line for the program's M10 done-when. |
| R2-11 | Codex already has pickup through its `SessionStart` wiring. | Accepted, verified | Non-goals corrected; Codex cases in criterion 6; Codex resume in fact (a). |
| R2-12 | If fact (b) fails, nothing tells the agent its session id. | Accepted, verified | On that branch the hook prints the id at every start. |
| R2-13 | The wrapper may have no room, and `loaded_size` prints nothing under the ceiling. | Accepted, verified | A precondition of 600 bytes of headroom, a test that prints the total, a stop rule. |
| R2-14 | `ws.py check` does not verify `prove-by` or the M4 queued list. | Accepted, verified | Each has a `grep`. |
| R2-15 | The contract's eval-rule wording is not this plan's business. | Accepted, verified | Removed from slice 5. |
| R2-16 | Slice 5 writes public text at the worker tier. | Accepted, verified | Slice 5 runs at the driver tier. |

## Approval

Not yet approved.

## Changes after approval

## Results
