---
kind: plan
last-reviewed: 2026-11-26
status: abandoned
milestone: M4
---

# The decision queue: hand-off plan

The plan for one queue of the questions agents leave for a person, answered one at a time in a single pass. Building sessions work from it.

**In short:** sessions file each question as a queue item, with its options and the consequence of each. A pass answers what the evidence already answers, then asks the person the rest, one at a time. The first version sends nothing to any session: the session that asked picks its answer up when it next starts, or the person hands it to another session.

**Abandoned on 2026-11-26.** The maintainer cut the queue. The trial's bar, C2 under "The two bars", was checked at M3's sign-off and failed on one count: no item had been closed from evidence without asking. This plan's settled decisions say a failed trial cuts the queue. No slice was built. The maintainer's private pass stays private.

## Key points

Eighth draft, after seven red-team rounds. Each point in full is under "Key points in detail".

- **The first version never messages a session.** Answers wait for the asking session's next start, or the person hands them on.
- **The maintainer's private pass stays out of this repository** while this is built and measured. The maintainer turns it off here before slice 0.
- **A pass is a real thing the tool issues.** Only the person starts one. Answers from evidence or outside a pass are labelled at pickup.
- **The park rule is narrow.** An agent files a question only on the person's word or with no person present.
- **Two tests, in order.** The trial of the private version (C2) gates the build at M3's sign-off. Slice 6 then tests this design (C3) during M4: keep or cut.
- **Fewer items will come in than in the private version.** With too few items filed, C3's verdict is "not tested", not "cut".
- **Smaller than the private version.** Out-of-scope features wait under "Later".
- **Fresh source.** Builders never open the private version's files.
- **Two edits to eval-hashed files wait** for M4's closing recording, and only on a "keep".

## Key points in detail

Eighth draft. It applies rounds 1 to 7 of the red team (26, 16, 20, 14, 17, 16 and 17 findings; 6, 3, 1, 2, 1, 0 and 0 blockers).

- **The first version never messages a session.** The private version sends each answer to the asking session at once, which can start many idle sessions in one pass. Round 1 showed a guard against that could be bypassed and would block other messages. So version one is pull-only. A session sees its answers at each start until it marks them done. If the asking session is gone, the pass's report prints the line that hands the answer to another session, on the person's word.
- **The maintainer's private pass must stay out of this repository while this is built and measured.** It pushes answers to sessions, and its trigger overlaps this wrapper's. Builders must not call it, since it loads the original. The maintainer turns it off here before slice 0 (see "Preconditions").
- **A pass is a real thing the tool issues.** `queue pass start` returns an id tied to the session that started it, and `pass end` closes it. Only the person starts a pass, and a new pass ends any pass left open. Answers from a pass or from evidence must name that open pass. Only the session holding an item may mark it done. Every answer not given by the person in a pass is labelled at pickup: "from evidence", or "not from a pass".
- **The park rule is narrow.** An agent files a question only when the person tells it to park one, or when it runs with no person present. A question the person can answer now is asked in the session as usual. Round 2 showed a broad rule would file every clarifying question, including the pass's own.
- **Two tests, in order.** The trial of the private version is measured by use, with its one deadline at M3's sign-off (the maintainer's word, 2026-11-18); it gates the build. Then slice 6 tests this plan's own design over a window of use during M4, and decides keep or cut before M4's closing recording. The maintainer set both bars, C2 and C3, as recommended on 2026-11-18.
- **Fewer items will come in than in the private version.** It gathers unanswered questions from live sessions; this version does not, and parks questions only on the person's word or when no person is present. So C3 has a floor: with too few items filed, the verdict is "not tested", not "cut".
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
- The two bars, C2 and C3, are set as recommended (see "The two bars").
- The plan is approved if round 8 of the red team only finishes earlier work. Round 7 raised new findings, so the program's stop rule calls for round 8. If round 8 raises anything new, the plan goes back to the maintainer.
- The private decision skill stays on in this repository until right before slice 0, so passes run here still count toward the trial.

Carried from the program, 2026-11-15 and 2026-11-16:

- The queue is experimental. It ships only if the maintainer's own trial of the private version shows real passes. If the trial fails, the queue is cut.
- Every port is rebuilt from scratch from a generic description. Nobody who builds it opens the original. Only a walled reader does, and a walled reader builds nothing.
- Public pages make no comparative claims.

## The two bars

Both set by the maintainer on 2026-11-18, as recommended.

| # | Choice | Bar | Why |
|---|---|---|---|
| C2 | The trial's bar, checked at M3's sign-off | At least 4 passes on at least 3 different days. At least 1 item closed from evidence without asking. At least 3 answers that reached the asking session and were acted on. | On 2026-11-18 the private queue had 2 passes on 2 days and 29 items done or answered (verified from its history), so an item count tests nothing. The private version pushes answers, so this bar tests use, not this plan's pull design; C3 tests that. |
| C3 | Slice 6's bar | Over one week of M4's build: at least 3 answers from a pass, or from evidence, picked up and acted on by the session holding them, where another session ran that pass; and no message sent to a session by a pass. A floor applies; see "C3's floor" below. | It is the only test of the design this plan changes. Answers given in the session (`direct`) do not count toward it. The floor stops a quiet week from cutting an untested design. |

**C3's floor.** If fewer than 8 items were filed that week, the verdict is "not tested": the window runs one more week, once, and then the maintainer decides. Otherwise a miss cuts the queue.

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

Slice 0 starts only when the maintainer's private skill is turned off for this repository (the third item below). Slice 1 starts only when all of these hold:

- The maintainer has said the trial met the C2 bar, at or before M3's sign-off.
- M3's slice B6 has merged: the wrapper format, its check and its selection cases. (M3's slices C1, the launcher, and C2, the case runner, have merged; verified from `git log`.)
- The maintainer has turned their private decision skill off for sessions in this repository, in their own untracked settings, and their private pass skips sessions whose working folder is in this repository. Both hold until slice 6's verdict. Builders work in sessions where that skill cannot be called, worktree sessions included (fact (e)); its one-line description in a skill list is the only exposure, and the walled reader's section overrides it. The maintainer also confirms nothing else files this repository's questions into the private queue until then.
- After B6, the wrappers' descriptions leave at least 600 bytes under the ceiling then in force in `workspace.json`.
- The M4 plan exists, keeps a list of edits queued for its closing recording under its "Results", and orders slice 6's verdict before that recording.
- Owned by the maintainer, not by any slice: the program's M10 done-when gains a line that the queue's playbook is proven, cut, or unproven with a failed attempt on record.

## Slices

| Order | Slice | Work | Tier | Done when |
|---|---|---|---|---|
| 0 | Facts | Record facts (a) to (e) as verified or not in "Results", with the command or transcript. They cover session ids across resumes, the session id a tool call can read, `claude agents --json`, a wrapper description's size, and the private skill's absence. See "Slice 0: Facts" below. | Driver | Five lines in "Results" |
| 1 | Store and tool | `wslib/decisions.py` and `python3 ws.py queue`, with the store in `ws-queue/` in the common git folder, an append-only event log, passes the tool issues, and ownership guards. See "Slice 1: Store and tool" below. | Driver | Criteria 1 to 5 |
| 2 | Pickup | Amend [decision 0004](../decisions/0004-the-hook-contract.md) so `session-start` hooks may `NEED` a new `answers` fact. A session hook prints the session's answered and closed items at every start until `done`. See "Slice 2: Pickup" below. | Driver | Criteria 6 and 7 |
| 3 | The pass | `docs/playbooks/work-the-queue.md`, unproven, with two sections: **Working the queue**, for the person's pass, and **Parking a question**, for any session. See "Slice 3: The pass" below. | Driver | Criterion 8 |
| 4 | Wrapper | A Claude Code wrapper in B6's format with two triggers. Selection cases must fire in at least 8 of 10 runs, and should-not-fire cases in at most 1 of 10. See "Slice 4: Wrapper" below. | Driver | Criteria 9 and 10 |
| 5 | Pages | Glossary, `docs/parts.md` and README rows, two Codex limits, a decision record, two queued edits in the M4 plan, and a changelog entry. See "Slice 5: Pages" below. | Driver | Criterion 11 |
| 6 | Real use | Use the queue on this repository's own work for one week of M4's build. Record the counts in "Results", and note in M4's record that its questions-asked count includes parked questions. The maintainer records keep or cut before M4's closing slice starts. | Driver | Criteria 12 and 13 |

Slices 1 and 2 share one branch and one draft pull request. Slices 3 to 5 share a second branch, opened after the first merges.

### Slice 0: Facts

Record each as verified or not in "Results", with the command or transcript. Slice 0 runs no messaging tool and never invokes the private skill. (a) Which ways of going back to a session keep its session id, so its session-start event carries the id it filed under: `claude --resume`, `--continue`, `/resume`, `/clear`, compaction, `--fork-session`, a `--bg --resume` copy, and a Codex resume. (b) A tool call inside a session can read the same session id its hook event carries, for Claude Code and for Codex, recorded separately; whether a helper agent sees its parent's session id; and whether `CLAUDE_CODE_SESSION_ATTENDED` tells an attended session from an unattended one; and whether a tool call in a worktree session, and in a Codex session, can write a file under `git rev-parse --git-common-dir`. (c) What `claude agents --json --cwd <this repository>` reports per session, for the pass's report, and whether it tells live sessions from ended ones; and whether an interactive session in this repository appears under `--cwd`, which the help text says lists background sessions only. Record field names and yes or no only, never the output, which can name private work. (d) In a plain session in this repository, a wrapper's description of 600 bytes is in context, in full; tested with a throwaway wrapper that is never committed, or one B6 shipped. (e) In a session under `.claude/worktrees/`, the maintainer's private decision skill is not in the session's skill listing or refuses there; and in a `claude plugin eval` run, whether user-level skills load at all. Both are checked by reading the skill listing, never by invoking the skill. Facts (a), (d) and (e) may need the person's hands; if so, the session asks once for all of them. A Codex model seeing session-start output is not checked; the README states it as an unverified limit. Driver tier, because its report goes into this public plan under a privacy rule.

### Slice 1: Store and tool

`wslib/decisions.py` and `python3 ws.py queue` with `add`, `list`, `answer`, `done`, `close`, `take`, `count`, `pass start` and `pass end` (*o*, apart from `take` and `pass`). Items live in `ws-queue/` in the common git folder, so every worktree shares one queue and git never tracks it. The `WS_QUEUE_DIR` environment variable overrides the folder, set per command and never exported; tests set it to a throwaway repository's folder, and the playbook tells anyone trying the tool by hand to do the same. When it is set, `queue list` and the pickup notice name the store they read. Writes are atomic, under the queue's own lock file, with a retry on `add`. Every write appends one line to `ws-queue/events.jsonl`, which is never rewritten. Kinds: `decide`, `do`, `notice` (*o*). An item records the session id that filed it, the agent tool, its working copy and branch, and whether that session stopped on it (`blocking`, *o*). A `notice` is closed with the reason "read"; a `do` item is answered "done by the person". Statuses: `open`, `answered`, `done` (the session holding it acted), `closed` (dropped, with a reason). A pass belongs to the session that started it. `pass start` refuses while an open pass has had a write in the last 30 minutes, unless given `--replace`; otherwise it ends the open pass, logs it as abandoned and prints which pass it ended. The engine reads no liveness. The playbook says only the person starts a pass, and `--replace` is used only on the person's word. `answer` records its source: `pass` or `evidence`, each naming the caller's own open pass (any other id is refused), or `direct` (a filed item the person answered outside a pass). `close` takes `open` or `answered` items, only from the session holding the open pass. `answer` takes an `open` item, or an `answered` one as a logged amendment, and refuses `done` and `closed` items. `done` takes an `answered` or `closed` item, requires a `--did` note saying what the session did (a commit, a file, or a decision applied), records it in its event, and refuses a caller whose session id is not the item's. `list --mine` prints the caller's answered and closed items in the pickup hook's wording. `take ID` re-keys an answered or closed item to the caller's session id and logs an event; the playbook says a session runs it only on the person's instruction. The ownership commands, which need the caller's session id, are `add`, `answer`, `done`, `close`, `take`, `list --mine`, `pass start` and `pass end`. If fact (b) held for Claude Code but not Codex, they refuse under Codex, so Codex can neither file nor pick up items, and the README says so. `done` on a closed item sets `done` and its event records that the item was closed.

### Slice 2: Pickup

Amend [decision 0004](../decisions/0004-the-hook-contract.md): `session-start` hooks may `NEED` a new fact, `answers`, the answered and closed items whose session id equals the event's. The amendment also lists the facts the runner already fills and 0004 omits (`fast_forward` for session events; `lease` and `rule_pages` for edit events). On any error reading the store, the runner sets `answers` to an empty list, so the other session-start notices still print. The runner reads them from the store; the part reads only the fact, so it stays a pure function. A session hook prints them at every start until the session runs `done`. Closed items are printed the same way, with their reason, so a session that stopped on one is told. An answer from evidence is labelled "from evidence: <source>"; a `direct` answer, "not from a pass". The wording lives in a small module, `wslib.queuetext`, which the 0004 amendment adds to the modules a part may import, by editing the "Parts may import only" bullet inline with a dated note, as 0004's 2026-11-17 amendment did, so the allowed-modules test reads it. `queuetext` itself imports only allowed modules, and a test checks both. If M3's B5 decisions check refuses the inline edit, stop and report. It adds no tool event and no write. The case runner gains a store fixture, so cases can seed answers. The hook keeps the whole `session-start` event inside its budget, which it shares with the other session-start hooks.

### Slice 3: The pass

`docs/playbooks/work-the-queue.md` (`kind: playbook`, `proof: unproven`, `prove-by: M10`; unproven pages are not eval-gated, per [decision 0006](../decisions/0006-what-proven-means.md)). It adds the page's row to the README's "Proven and unproven pages" table, updates its count line, and adds a row to `docs/layout.md`'s table of existing pages. The page has two separate sections. **Working the queue**, for the person's pass. Steps: `pass start`; gather open items; answer from evidence with read-only helpers at the worker tier, which never run a queue command, since they share the pass's session id; order (notices, then blocking, then oldest); ask one at a time with the recommendation first; follow-ups; confirm a thread's answers, evidence answers included; apply; `pass end`; report. If an answer is refused because the pass was ended, start a new pass with the person's word and re-ask from the last confirmed thread. The report lists each session holding answers, live or gone. For a live session it prints the line the person types there ("run `python3 ws.py queue list --mine` and act on your answers"); for a gone session, the `take` line to run in another session. A Codex session is marked "liveness unknown" and gets no `take` line unless the person asks. **Parking a question**, for any session, holding no pass commands. It states the park rule: file a question only when the person says to park it, or when no person is present. "No person present" means the launch or the prompt says the run is unattended, or `CLAUDE_CODE_SESSION_ATTENDED` says so if fact (b) found it reliable. A question asked and answered in the session is never filed. A filed item the person answers outside a pass is recorded with `answer --source direct`, then `done`. A blocking parked question stops the session. A session the person returns to runs `queue list --mine` to see its answers. The page says no session is ever messaged, without naming any messaging tool. The report reads sessions with `claude agents --json --cwd` set to this repository, or, if fact (c) found interactive sessions missing from it, with `--json` alone piped through a filter the playbook gives, which keeps only sessions whose working folder is in this repository and prints only their id and state. If fact (c) failed, the report lists sessions by id without saying which are live.

### Slice 4: Wrapper

A Claude Code wrapper in B6's format, with two triggers: the person asks to work the queue; and the person says to park a question, or a session with no person present reaches one. Should-not-fire cases: the pass's own questions, plan and approval questions, and a question asked of a person who is present. Trigger 2's should-fire cases are task prompts built to reach a question. Three more cases run the three fix-a-bug eval requests unattended, with the bar that the wrapper never stops the run, because M4's routed arm will run them with the wrappers on. A should-fire case runs with a stand-in of the same purpose loaded as a second local plugin in the case's scaffold, written for the case: the wrapper fires and the stand-in does not. The private skill is never loaded in a run (fact (e)). Both kinds of trigger-2 case state in the prompt whether the run is unattended. Bar: each should-fire case fires in at least 8 of 10 runs, and each should-not-fire case in at most 1 of 10. Runs use `--runs 10`, `--scaffold`, `--ablation none`, `--no-publish` and `--disallow-tools SendMessage`. A grader in the stand-in case checks the stand-in was listed in the run; a run without it is invalid, not passed. Invalid runs are re-run to reach 10 valid ones within the cap; more than 2 invalid runs in one case is a stop. If fact (e) found user-level skills load in eval runs, the maintainer denies the private skill at user level only while slice 4's runs go, about a day, and allows it again after. At most 80 child runs per round, two rounds, 160 in all. The slice report shows the real description is no larger than the 600 bytes fact (d) tested, or fact (d) is run again. Slices 3 and 4 commit the playbook and the wrapper together, so the wrapper check never sees one without the other. The slice report records the wrappers' total description bytes from `python3 -m unittest tests.test_queue.LoadedSize -v`.

### Slice 5: Pages

Glossary rows (queue item, pass, pickup). A row in `docs/parts.md` for the pickup hook, and an `answers` row in its table of the facts each hook may need. A row in the README's "What is checked" table, and two Codex limits under "What stays prose": the pass's walk and the park trigger are Claude Code only, and a Codex model seeing the pickup notice is unverified. A decision record, numbered with the next free number: answers are pulled, and no pass messages a session. Two edits added to the M4 plan's queued list, each marked "only on slice 6's keep": the `AGENTS.md` park rule and the `INDEX.md` topic row. A note in that list that the routed arm carries the park trigger. A changelog entry. Driver tier, because the README and the decision record are read outside the team.

## Success criteria

1. `python3 -m unittest tests.test_queue -b` passes.
2. Its cases show `add` refusing: no question; a `decide` item whose question does not end with `?`; a `decide` item with fewer than 2 or more than 4 options; an option with no consequence; a recommendation that names no option and does not start `none:`; an unknown kind.
3. Its cases show 20 processes adding at once get 20 distinct ids, on every system in CI. An item added in a linked worktree is listed from the main working copy.
4. Its cases show the store resolves under `git rev-parse --git-common-dir` unless `WS_QUEUE_DIR` is set, and `git status --porcelain` is the same before and after `add`, `answer` and `done`. A case writes a unique marker through the tool with `WS_QUEUE_DIR` set, and checks the marker never appears in the live store; a missing live store, as in CI, passes.
5. Its cases show: each write appends exactly one line to `events.jsonl` and changes no earlier line; `done` refuses an `open` or `done` item, a caller whose session id is not the item's, and a call without `--did`; `done` on a `closed` item sets `done` and its event records that the item was closed; `answer` refuses a `done` or `closed` item and logs an amendment on an `answered` one; `answer --source pass` and `--source evidence` refuse an id the tool did not issue, one already ended, and one held by another session; `close` refuses outside the caller's open pass and on a `done` item; `pass start` refuses while the open pass had a write in the last 30 minutes, and with `--replace` ends it, logs one abandoned event and prints its id; without `--replace` it ends a pass idle for more than 30 minutes; `pass end` refuses another session's pass; `take` re-keys an answered or closed item and logs it; `list --mine` prints only the caller's answered and closed items.
6. `python3 ws.py selftest` passes with the pickup hook's cases, for Claude Code and Codex events: it reminds when `answers` holds an item; it is silent when `answers` is empty; it labels an evidence answer and a `direct` answer; it prints a closed item with its reason.
7. `python3 -m unittest tests.test_core -b` passes, with cases showing the runner fills `answers` with the answered and closed items for the event's session id only; with the store missing or corrupt, `answers` is empty, the session start exits 0, and another session hook's reminder still prints. `python3 tests/hook_cases.py` passes, with a seeded store, inside the session-start budget.
8. `python3 ws.py check` passes, and `grep -n "prove-by: M10" docs/playbooks/work-the-queue.md` prints one line.
9. B6's wrapper check passes for the new wrapper, and B6's selection-case command meets slice 4's bar, counting only valid runs.
10. The `tests.test_queue.LoadedSize` case computes the wrappers' description bytes the way `loaded_size` does and fails when the total is over the ceiling it reads from `workspace.json`. Slice 4's report records the total it prints when run with `-v`.
11. `python3 ws.py check` passes after slice 5, and `sed -n '/^## Results/,$p' docs/plans/<the M4 plan> | grep -c "only on slice 6's keep"` prints 2.
12. Slice 6's "Results" holds counts from `python3 ws.py queue count --since <date> --until <date>`, computed from `events.jsonl`: passes started, ended, and ended as abandoned; items filed; answered from evidence; answered in a pass; answered `direct`; closed items acknowledged with `done`, counted apart and never toward C3; picked up and acted on (`done` events by the item's session whose answer is not `direct` and came from a pass another session held); items re-keyed with `take`. It also states that the pass's playbook and wrapper hold no instruction to message a session: `grep -nE "SendMessage|send_message|claude (-p|--print)|(--resume|-r) [^ ]+ [\"']|codex (exec|resume) [^ ]+ [\"']" docs/playbooks/work-the-queue.md <the wrapper's SKILL.md>` prints nothing. The page states the prohibition without naming a tool, and a resume line never carries a prompt. The pattern catches the common forms only; the page's own prohibition covers the rest.
13. The maintainer reads slice 6's counts, and the `--did` notes of the items counted toward C3, against the C3 bar, and records "keep" or "cut" in "Results". This criterion is a person's reading, not a script's.
14. CI passes on Linux, macOS and Windows for both pull requests: `gh pr checks <number>` shows every job "pass".

## Verification

```
python3 -m unittest tests.test_queue -b          # criteria 1 to 5 and 10: "OK"
python3 -m unittest tests.test_queue.LoadedSize -v   # criterion 10: the byte total, for slice 4's report
python3 ws.py selftest                           # criterion 6: exit 0
python3 -m unittest tests.test_core -b           # criterion 7: "OK"
python3 tests/hook_cases.py                      # criterion 7, the budget: exit 0
python3 -m unittest discover -b tests            # every test: "OK"
python3 ws.py check                              # criteria 8 and 11: exit 0
grep -n "prove-by: M10" docs/playbooks/work-the-queue.md    # criterion 8: one line
<B6's selection-case command>                    # criterion 9: slice 4's bar met
sed -n '/^## Results/,$p' docs/plans/<the M4 plan> | grep -c "only on slice 6's keep"   # criterion 11: 2
python3 ws.py queue count --since <date> --until <date>     # criterion 12: the counts
grep -nE "SendMessage|send_message|claude (-p|--print)|(--resume|-r) [^ ]+ [\"']|codex (exec|resume) [^ ]+ [\"']" docs/playbooks/work-the-queue.md <the wrapper's SKILL.md>   # criterion 12: nothing
gh pr checks <number>                            # criterion 14: every job "pass"
```

B6 writes the selection-case command into `evals/README.md`.

## Recovery

Halt and report. Do not work around a failure. A test that fails on one operating system only is a finding to report, not a test to skip.

## Stop rule

- If a precondition does not hold, do not start.
- If fact (a) finds that `claude --resume` gives a new id, pickup cannot match it. Stop and report before slice 1. Any other path that gives a new id, a Codex resume included, is handled by `take`, and the playbook names each one.
- If fact (b) fails for Claude Code, the ownership guards cannot hold and C3 means nothing. Stop and report before slice 1. If it fails for Codex only, the ownership commands refuse under Codex, the README says so, and the plan goes on.
- If fact (e) fails for worktree sessions, the maintainer makes the private skill refuse to run when its working folder is in this repository, and fact (e) is checked again; if it still fails, the plan stops. For eval runs, see slice 4: a user-level deny held only while its runs go, which turns the skill off in every repository, work included, for about a day.
- If fact (c) fails, the pass's report lists sessions by id without saying which are live. Report and go on. If interactive sessions are missing under `--cwd`, the report uses `--json` alone and filters in memory, as slice 3 says.
- If fact (d) fails, the park rule cannot ride in the wrapper. Stop and report before slice 1.
- If slice 4's bar is missed after one rewrite of the description, stop and report. Close the second branch's pull request unmerged, and run the cut path on what slices 1 and 2 merged.
- If C3's bar is missed with the item floor met, cut the queue by the path below.

**Cutting the queue.** In one pull request: mark the pickup hook's manifest entry `retired` (see [changing the machinery](../changing-the-machinery.md#traps)); remove `ws.py queue`, `wslib/decisions.py`, `wslib/queuetext.py`, the runner's `answers` code, the pickup part's `.py` and `.cases.json`, `tests/test_queue.py`, the `test_core` cases, the store fixture in `tests/hook_cases.py` and the pickup rows in `tests/hooks/session-start.json`; amend decision 0004 with a dated entry that removes `answers` and `wslib.queuetext` from its allowed modules; mark the new decision record superseded; remove the wrapper and its selection cases; in one commit, move the playbook to `archive/docs/playbooks/`, remove the README's "Proven and unproven pages" row and count, fix every link to it and repoint the `docs/layout.md` row; in a second commit, strip its proof keys. No tombstone stays in `docs/playbooks/`, which admits only playbooks. Remove the glossary and `parts.md` rows, the `answers` row in `docs/parts.md`'s facts table, and the README's "What is checked" row; withdraw the two edits from the M4 plan's queued list. The maintainer updates the program's M10 line. Leave the store's folder alone; it is the person's data.

## Limits

- Machinery goes to its own branch, from a worktree under `.claude/worktrees/` (the maintainer's standing rule since M2's slice 4, carried in the M3 plan), in a draft pull request. Agents here may publish and merge it after CI passes on all three systems.
- Docs-only commits go straight to main.
- Any unattended fix loop stops after three rounds.
- Stage files by name.

## Records this plan must leave

- The new decision record, and the amendment to decision 0004.
- Slice 0's facts, slice 4's selection results, and slice 6's counts and verdict, in "Results".
- The two queued edits, in the M4 plan.
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

Records: [round 1](../records/adversarial-reviews/2026-11-18-decision-queue.md), [2](../records/adversarial-reviews/2026-11-18-decision-queue-round-2.md), [3](../records/adversarial-reviews/2026-11-18-decision-queue-round-3.md), [4](../records/adversarial-reviews/2026-11-18-decision-queue-round-4.md), [5](../records/adversarial-reviews/2026-11-18-decision-queue-round-5.md), [6](../records/adversarial-reviews/2026-11-18-decision-queue-round-6.md) and [7](../records/adversarial-reviews/2026-11-18-decision-queue-round-7.md).

Seven rounds ran on 2026-11-18, each by a fresh session on the latest draft. They raised 126 findings, every one triaged: 125 accepted in whole or in part and one rejected (round 6, finding 15). The approval below depends on an eighth round. Each record holds its round's findings, with the author's disposition and action for each.

## Approval

Approved by the maintainer on 2026-11-18, on one condition: round 8 of the red team only finishes earlier work. If round 8 raises anything new, the plan goes back to the maintainer before any slice starts. The status stays `draft` until round 8 is on record.

## Changes after approval

## Results

### Abandoned, 2026-11-26

The maintainer cut the queue on 2026-11-26, answering Q86 of the workspace's queue. C2 failed on its evidence bar: no item was closed from evidence before M3's sign-off. The count of answers acted on was not the reason. No slice ran, and nothing in this repository was built from this plan. The seven red team records stay as the record of the design. M4's hand-off plan names the cut among its non-goals.
