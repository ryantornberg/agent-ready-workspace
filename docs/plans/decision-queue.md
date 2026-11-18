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

Seventh draft. It applies rounds 1 to 6 of the red team (26, 16, 20, 14, 17 and 16 findings; 6, 3, 1, 2, 1 and 0 blockers). Round 7 has not run yet.

- **The first version never messages a session.** The private version sends each answer to the asking session at once, which can start many idle sessions in one pass. Round 1 showed a guard against that could be bypassed and would block other messages. So version one is pull-only. A session sees its answers at each start until it marks them done. If the asking session is gone, the pass's report prints the line that hands the answer to another session, on the person's word.
- **The maintainer's private pass must stay out of this repository while this is built and measured.** It pushes answers to sessions, and its trigger overlaps this wrapper's. Builders must not call it, since it loads the original. The maintainer turns it off here before slice 1 (see "Preconditions").
- **A pass is a real thing the tool issues.** `queue pass start` returns an id tied to the session that started it, and `pass end` closes it. Only the person starts a pass, and a new pass ends any pass left open. Answers from a pass or from evidence must name that open pass. Only the session holding an item may mark it done. Every answer not given by the person in a pass is labelled at pickup: "from evidence", or "not from a pass".
- **The park rule is narrow.** An agent files a question only when the person tells it to park one, or when it runs with no person present. A question the person can answer now is asked in the session as usual. Round 2 showed a broad rule would file every clarifying question, including the pass's own.
- **Two tests, in order.** The trial of the private version is measured by use, with its one deadline at M3's sign-off (the maintainer's word, 2026-11-18); it gates the build. Then slice 6 tests this plan's own design over a window of use during M4, and decides keep or cut before M4's closing recording. The bars, C2 and C3, need the maintainer's yes.
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

Carried from the program, 2026-11-15 and 2026-11-16:

- The queue is experimental. It ships only if the maintainer's own trial of the private version shows real passes. If the trial fails, the queue is cut.
- Every port is rebuilt from scratch from a generic description. Nobody who builds it opens the original. Only a walled reader does, and a walled reader builds nothing.
- Public pages make no comparative claims.

## Choices for the maintainer

| # | Choice | Recommended | Why |
|---|---|---|---|
| C2 | The trial's bar, checked at M3's sign-off | At least 4 passes on at least 3 different days. At least 1 item closed from evidence without asking. At least 3 answers that reached the asking session and were acted on. | On 2026-11-18 the private queue had 2 passes on 2 days and 29 items done or answered (verified from its history), so an item count tests nothing. The private version pushes answers, so this bar tests use, not this plan's pull design; C3 tests that. |
| C3 | Slice 6's bar | Over one week of M4's build: at least 3 answers from a pass, or from evidence, picked up and acted on by the session holding them, where another session ran that pass; and no message sent to a session by a pass. If fewer than 8 items were filed that week, the verdict is "not tested": the window runs one more week, once, and then the maintainer decides. Otherwise a miss cuts the queue. | It is the only test of the design this plan changes. Answers given in the session (`direct`) do not count toward it. The floor stops a quiet week from cutting an untested design. |

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

Slice 0 starts only when the maintainer's private skill is turned off for this repository (the fourth item below). Slice 1 starts only when all of these hold:

- The maintainer has said the trial met the C2 bar, at or before M3's sign-off.
- M3's slice B6 has merged: the wrapper format, its check and its selection cases. (M3's slices C1, the launcher, and C2, the case runner, have merged; verified from `git log`.)
- The maintainer has turned their private decision skill off for sessions in this repository, in their own untracked settings, and their private pass skips sessions whose working folder is in this repository. Both hold until slice 6's verdict. Builders work in sessions where that skill cannot be called, worktree sessions included (fact (e)); its one-line description in a skill list is the only exposure, and the walled reader's section overrides it.
- After B6, the wrappers' descriptions leave at least 600 bytes under the ceiling then in force in `workspace.json`.
- The M4 plan exists, has a list of edits queued for its closing recording, and orders slice 6's verdict before that recording.
- Owned by the maintainer, not by any slice: the program's M10 done-when gains a line that the queue's playbook is proven, cut, or unproven with a failed attempt on record.

## Slices

| Order | Slice | Work | Tier | Done when |
|---|---|---|---|---|
| 0 | Facts | Record each as verified or not in "Results", with the command or transcript. Slice 0 runs no messaging tool and never invokes the private skill. (a) Which ways of going back to a session keep its session id, so its session-start event carries the id it filed under: `claude --resume`, `--continue`, `/resume`, `/clear`, compaction, `--fork-session`, a `--bg --resume` copy, and a Codex resume. (b) A tool call inside a session can read the same session id its hook event carries, for Claude Code and for Codex, recorded separately; whether a helper agent sees its parent's session id; and whether `CLAUDE_CODE_SESSION_ATTENDED` tells an attended session from an unattended one. (c) What `claude agents --json --cwd <this repository>` reports per session, for the pass's report, and whether it tells live sessions from ended ones; and whether an interactive session in this repository appears under `--cwd`, which the help text says lists background sessions only. Record field names and yes or no only, never the output, which can name private work. (d) In a plain session in this repository, a wrapper's description of the planned size is in context, in full; tested with a throwaway wrapper that is never committed, or one B6 shipped. (e) In a session under `.claude/worktrees/`, the maintainer's private decision skill is not in the session's skill listing or refuses there; and in a `claude plugin eval` run, whether user-level skills load at all. Both are checked by reading the skill listing, never by invoking the skill. Facts (a), (d) and (e) may need the person's hands; if so, the session asks once for all of them. A Codex model seeing session-start output is not checked; the README states it as an unverified limit. | Worker | Five lines in "Results" |
| 1 | Store and tool | `wslib/decisions.py` and `python3 ws.py queue` with `add`, `list`, `answer`, `done`, `close`, `take`, `count`, `pass start` and `pass end` (*o*, apart from `take` and `pass`). Items live in `ws-queue/` in the common git folder, so every worktree shares one queue and git never tracks it. The `WS_QUEUE_DIR` environment variable overrides the folder; tests always set it to a throwaway repository's folder, and the playbook tells anyone trying the tool by hand to do the same. Writes are atomic, under the queue's own lock file, with a retry on `add`. Every write appends one line to `ws-queue/events.jsonl`, which is never rewritten. Kinds: `decide`, `do`, `notice` (*o*). An item records the session id that filed it, the agent tool, its working copy and branch, and whether that session stopped on it (`blocking`, *o*). A `notice` is closed with the reason "read"; a `do` item is answered "done by the person". Statuses: `open`, `answered`, `done` (the session holding it acted), `closed` (dropped, with a reason). A pass belongs to the session that started it. `pass start` refuses while an open pass has had a write in the last 30 minutes, unless given `--replace`; otherwise it ends the open pass, logs it as abandoned and prints which pass it ended. The engine reads no liveness. The playbook says only the person starts a pass, and `--replace` is used only on the person's word. `answer` records its source: `pass` or `evidence`, each naming the caller's own open pass (any other id is refused), or `direct` (a filed item the person answered outside a pass). `close` takes `open` or `answered` items, only from the session holding the open pass. `done` takes an `answered` or `closed` item, and refuses a caller whose session id is not the item's. `list --mine` prints the caller's answered and closed items in the pickup hook's wording. `take ID` re-keys an answered or closed item to the caller's session id and logs an event; the playbook says a session runs it only on the person's instruction. The ownership commands, which need the caller's session id, are `add`, `answer`, `done`, `close`, `take`, `list --mine`, `pass start` and `pass end`. If fact (b) held for Claude Code but not Codex, they refuse under Codex, so Codex can neither file nor pick up items, and the README says so. `done` on a closed item sets `done` and its event records that the item was closed. | Driver | Criteria 1 to 5 |
| 2 | Pickup | Amend [decision 0004](../decisions/0004-the-hook-contract.md): `session-start` hooks may `NEED` a new fact, `answers`, the answered and closed items whose session id equals the event's. The amendment also lists the facts the runner already fills and 0004 omits (`fast_forward` for session events; `lease` and `rule_pages` for edit events). On any error reading the store, the runner sets `answers` to an empty list, so the other session-start notices still print. The runner reads them from the store; the part reads only the fact, so it stays a pure function. A session hook prints them at every start until the session runs `done`. Closed items are printed the same way, with their reason, so a session that stopped on one is told. An answer from evidence is labelled "from evidence: <source>"; a `direct` answer, "not from a pass". The wording lives in a small module, `wslib.queuetext`, which the 0004 amendment adds to the modules a part may import, so the hook and `list --mine` share it. It adds no tool event and no write. The case runner gains a store fixture, so cases can seed answers. The hook keeps the whole `session-start` event inside its budget, which it shares with the other session-start hooks. | Driver | Criteria 6 and 7 |
| 3 | The pass | `docs/playbooks/work-the-queue.md` (`kind: playbook`, `proof: unproven`, `prove-by: M10`; unproven pages are not eval-gated, per [decision 0006](../decisions/0006-what-proven-means.md)). It adds the page's row to the README's "Proven and unproven pages" table, updates its count line, and adds a row to `docs/layout.md`'s table of existing pages. The page has two separate sections. **Working the queue**, for the person's pass. Steps: `pass start`; gather open items; answer from evidence with read-only helpers at the worker tier, which never run a queue command, since they share the pass's session id; order (notices, then blocking, then oldest); ask one at a time with the recommendation first; follow-ups; confirm a thread's answers, evidence answers included; apply; `pass end`; report. If an answer is refused because the pass was ended, start a new pass with the person's word and re-ask from the last confirmed thread. The report lists each session holding answers, live or gone, and for a gone session the `take` line to run in another session. A Codex session is marked "liveness unknown" and gets no `take` line unless the person asks. **Parking a question**, for any session, holding no pass commands. It states the park rule: file a question only when the person says to park it, or when no person is present. "No person present" means the launch or the prompt says the run is unattended, or `CLAUDE_CODE_SESSION_ATTENDED` says so if fact (b) found it reliable. A question asked and answered in the session is never filed. A filed item the person answers outside a pass is recorded with `answer --source direct`, then `done`. A blocking parked question stops the session. A session the person returns to runs `queue list --mine` to see its answers. The page says no session is ever messaged, without naming any messaging tool. The report reads sessions with `claude agents --json --cwd` set to this repository, or, if fact (c) found interactive sessions missing from it, with `--json` alone, filtered by working folder in memory and never printed whole. If fact (c) failed, the report lists sessions by id without saying which are live. | Driver | Criterion 8 |
| 4 | Wrapper | A Claude Code wrapper in B6's format, with two triggers: the person asks to work the queue; and the person says to park a question, or a session with no person present reaches one. Should-not-fire cases: the pass's own questions, plan and approval questions, and a question asked of a person who is present. Trigger 2's should-fire cases are task prompts built to reach a question. A should-fire case runs with a stand-in of the same purpose loaded as a second local plugin in the case's scaffold, written for the case: the wrapper fires and the stand-in does not. The private skill is never loaded in a run (fact (e)). Both kinds of trigger-2 case state in the prompt whether the run is unattended. Bar: each should-fire case fires in at least 8 of 10 runs, and each should-not-fire case in at most 1 of 10. Runs use `--runs 10`, `--scaffold`, `--ablation none`, `--no-publish` and `--disallow-tools SendMessage`. A grader in the stand-in case checks the stand-in was listed in the run; a run without it is invalid, not passed. If fact (e) found user-level skills load in eval runs, the maintainer denies the private skill at user level only while slice 4's runs go, about a day, and allows it again after. At most 80 child runs per round, two rounds, 160 in all. Slices 3 and 4 commit the playbook and the wrapper together, so the wrapper check never sees one without the other. The slice report records the wrappers' total description bytes from `python3 -m unittest tests.test_queue.LoadedSize -v`. | Driver | Criteria 9 and 10 |
| 5 | Pages | Glossary rows (queue item, pass, pickup). A row in `docs/parts.md` for the pickup hook, and an `answers` row in its table of the facts each hook may need. A row in the README's "What is checked" table, and two Codex limits under "What stays prose": the pass's walk and the park trigger are Claude Code only, and a Codex model seeing the pickup notice is unverified. A decision record, numbered with the next free number: answers are pulled, and no pass messages a session. Two edits added to the M4 plan's queued list, each marked "only on slice 6's keep": the `AGENTS.md` park rule and the `INDEX.md` topic row. A changelog entry. Driver tier, because the README and the decision record are read outside the team. | Driver | Criterion 11 |
| 6 | Real use | Use the queue on this repository's own work for one week of M4's build. Record the counts in "Results", and note in M4's record that its questions-asked count includes parked questions. The maintainer records keep or cut before M4's closing slice starts. | Driver | Criteria 12 and 13 |

Slices 1 and 2 share one branch and one draft pull request. Slices 3 to 5 share a second branch, opened after the first merges.

## Success criteria

1. `python3 -m unittest tests.test_queue -b` passes.
2. Its cases show `add` refusing: no question; a `decide` item whose question does not end with `?`; a `decide` item with fewer than 2 or more than 4 options; an option with no consequence; a recommendation that names no option and does not start `none:`; an unknown kind.
3. Its cases show 20 processes adding at once get 20 distinct ids, on every system in CI. An item added in a linked worktree is listed from the main working copy.
4. Its cases show the store resolves under `git rev-parse --git-common-dir` unless `WS_QUEUE_DIR` is set, and `git status --porcelain` is the same before and after `add`, `answer` and `done`. A case writes a unique marker through the tool with `WS_QUEUE_DIR` set, and checks the marker never appears in the live store; a missing live store, as in CI, passes.
5. Its cases show: each write appends exactly one line to `events.jsonl` and changes no earlier line; `done` refuses an `open` or `done` item, and a caller whose session id is not the item's; `answer --source pass` and `--source evidence` refuse an id the tool did not issue, one already ended, and one held by another session; `close` refuses outside the caller's open pass and on a `done` item; `pass start` refuses while the open pass had a write in the last 30 minutes, and with `--replace` ends it, logs one abandoned event and prints its id; without `--replace` it ends a pass idle for more than 30 minutes; `pass end` refuses another session's pass; `take` re-keys an answered or closed item and logs it; `list --mine` prints only the caller's answered and closed items.
6. `python3 ws.py selftest` passes with the pickup hook's cases, for Claude Code and Codex events: it reminds when `answers` holds an item; it is silent when `answers` is empty; it labels an evidence answer and a `direct` answer; it prints a closed item with its reason.
7. `python3 -m unittest tests.test_core -b` passes, with cases showing the runner fills `answers` with the answered and closed items for the event's session id only; with the store missing or corrupt, `answers` is empty, the session start exits 0, and another session hook's reminder still prints. `python3 tests/hook_cases.py` passes, with a seeded store, inside the session-start budget.
8. `python3 ws.py check` passes, and `grep -n "prove-by: M10" docs/playbooks/work-the-queue.md` prints one line.
9. B6's wrapper check passes for the new wrapper, and B6's selection-case command meets slice 4's bar, counting only valid runs.
10. The `tests.test_queue.LoadedSize` case computes the wrappers' description bytes the way `loaded_size` does and fails when the total is over the ceiling it reads from `workspace.json`. Slice 4's report records the total it prints when run with `-v`.
11. `python3 ws.py check` passes after slice 5, and `grep -n "only on slice 6's keep" docs/plans/<the M4 plan>` prints two lines.
12. Slice 6's "Results" holds counts from `python3 ws.py queue count --since <date> --until <date>`, computed from `events.jsonl`: passes started, ended, and ended as abandoned; items filed; answered from evidence; answered in a pass; answered `direct`; closed items acknowledged with `done`, counted apart and never toward C3; picked up and acted on (`done` events by the item's session whose answer is not `direct` and came from a pass another session held); items re-keyed with `take`. It also states that the pass's playbook and wrapper hold no instruction to message a session: `grep -nE "SendMessage|send_message|claude (-p|--print)|(--resume|-r) [^ ]+ [\"']|codex (exec|resume) [^ ]+ [\"']" docs/playbooks/work-the-queue.md <the wrapper's SKILL.md>` prints nothing. The page states the prohibition without naming a tool, and a resume line never carries a prompt. The pattern catches the common forms only; the page's own prohibition covers the rest.
13. The maintainer reads slice 6's counts against the C3 bar and records "keep" or "cut" in "Results". This criterion is a person's reading, not a script's.
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
grep -n "only on slice 6's keep" docs/plans/<the M4 plan>  # criterion 11: two lines
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

**Cutting the queue.** In one pull request: mark the pickup hook's manifest entry `retired` (see [changing the machinery](../changing-the-machinery.md#traps)); remove `ws.py queue`, `wslib/decisions.py`, the runner's `answers` code, the pickup part's `.py` and `.cases.json`, `tests/test_queue.py`, the `test_core` cases and the store fixture in `tests/hook_cases.py`; amend decision 0004 with a dated entry that removes `answers`; mark the new decision record superseded; remove the wrapper and its selection cases; move the playbook out of `docs/playbooks/` to `archive/` in one commit, then, in a second commit, strip its proof keys, make it a reference page keeping its facts, as decision 0006 says a cut page does, fix links to it and point the `docs/layout.md` row at the new path; remove the glossary and `parts.md` rows, the `answers` row in `docs/parts.md`'s facts table, the README's "What is checked" row and its "Proven and unproven pages" row and count; withdraw the two edits from the M4 plan's queued list. The maintainer updates the program's M10 line. Leave the store's folder alone; it is the person's data.

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

Round 3, 2026-11-18. A fresh session read the third draft and the sources. It found 9 of round 2's actions applied as written, 4 applied in part and 3 that made new problems; 4 of its 20 findings finish earlier work.

| # | Finding | Verdict | Action |
|---|---|---|---|
| R3-1 | The maintainer's private decision skill is loaded in every session here, overlaps the wrapper's trigger and pushes answers by message, which would spoil slice 6 and bring back the flagged risk. | Accepted, verified | A precondition: the maintainer turns it off for this repository and makes the private pass skip its sessions until slice 6's verdict. A should-not-fire case runs with a same-purpose user skill loaded. |
| R3-2 | Builders can call that skill and load the original. | Accepted, verified | The same precondition. Its one-line description is the stated exposure. |
| R3-3 | A corrupt store would silence every session-start notice, because the runner wraps all session hooks together. | Accepted, verified | The runner sets `answers` to empty on a store error; criterion 7 checks another hook still prints. |
| R3-4 | An evidence answer needed no pass, and `done` was not tied to the item's session, so C3 could be met with no person and no pickup. | Accepted, verified | Evidence answers name the caller's open pass; `done` refuses another session; criterion 5 tests both. |
| R3-5 | A pass cut off before `pass end` stays open, and its id stays usable from any session. | Accepted, inferred | A pass belongs to its session. `pass start` ends one left by a gone session and refuses while a live one holds a pass. |
| R3-6 | R2-3's wording could be read as filing every in-session question. | Accepted, verified | Questions asked and answered in the session are never filed; `direct` is for a filed item answered outside a pass. |
| R3-7 | "No person present" has no signal an agent can read. | Accepted, inferred | The launch or the prompt says the run is unattended; the cases state it. |
| R3-8 | 80 runs could not cover the cases plus the rewrite the stop rule allows. | Accepted, verified | 80 runs per round, two rounds, 160 in all. |
| R3-9 | The plan wrote to the program's M10 line, which is outside this repository. | Accepted, verified, finishing | The M10 line is the maintainer's, listed under "Preconditions". |
| R3-10 | The cut path left tests, the part's files and the fixture behind, and misread decision 0006. | Accepted, verified, finishing | Every file is listed; the cut page becomes a reference page with no proof keys. |
| R3-11 | Criterion 12's `grep` did not search the folder and missed shell routes. | Accepted, verified, finishing | `grep -rnE` over both, with the shell routes, must print nothing. |
| R3-12 | `-b` hides the printed byte total. | Accepted, verified, finishing | The slice report records it from a `-v` run of the one test. |
| R3-13 | If fact (b) fails, `take`, `done` and `close` also need the caller's id. | Accepted, verified | Every such command takes `--session` on that branch. |
| R3-14 | With no gathering and a narrow park rule, a quiet week could cut an untested design. | Accepted, inferred | C3 has a floor of 8 filed items, below which the verdict is "not tested". The intake gap is a key point. |
| R3-15 | B6's check may refuse the playbook committed without its wrapper. | Accepted, inferred | Slices 3 and 4 commit them together. |
| R3-16 | Criterion 12 counted "closed from evidence", which this design does not have. | Accepted, verified | "Answered from evidence". |
| R3-17 | "C2" named both a plan choice and M3's slice. | Accepted, verified | The preconditions say "M3's slices C1 and C2". |
| R3-18 | The key point on the trial read as if a second, time-boxed trial changed the settled one. | Accepted, verified | The key point separates the trial (C2) from slice 6's window (C3). |
| R3-19 | Fact (c) had no branch for failure. | Accepted, verified | The report lists sessions by id without live or gone. |
| R3-20 | Decision 0004 omits facts the runner already fills. | Accepted, verified | Slice 2's amendment lists them. |

Round 4, 2026-11-18. A fresh session read the fourth draft and the sources. All 20 round-3 actions are in the body; four made new problems and three needed a follow-up.

| # | Finding | Verdict | Action |
|---|---|---|---|
| R4-1 | R3-5's action brought back engine liveness with no source; Codex on Windows has no process id. | Accepted, verified | No liveness: `pass start` ends any open pass and logs it abandoned. Only the person starts a pass. |
| R4-2 | Slice 4's selection runs could call the private skill, which messages sessions, and publish its text. | Accepted, verified | Runs use `--disallow-tools SendMessage` and `--no-publish`; fact (e) checks the private skill is absent; the same-purpose case uses a stand-in. |
| R4-3 | Turning the private skill off in the main copy may not reach worktree sessions. | Accepted, inferred | Fact (e) checks worktree sessions; on failure, a user-level deny or a stop. |
| R4-4 | Criterion 8 fails without the playbook's row in the README's proof table. | Accepted, verified, finishing | Slice 3 adds the row and count; the cut path removes them. |
| R4-5 | Criterion 12's `grep` forbade the pickup line and scanned eval results. | Accepted, verified, finishing | It greps the playbook and the wrapper only, and forbids only a resume line that carries a prompt. |
| R4-6 | The same-purpose case was called should-not-fire but must win. | Accepted, verified, finishing | It is a should-fire case with a stand-in. |
| R4-7 | The run budget did not count the baseline arm. | Accepted, verified | `--ablation none`; the budget is in child runs. |
| R4-8 | Some stops left merged machinery with no way out. | Accepted, verified | Facts (a), (b), (d) and (e) stop before slice 1; a slice 4 miss runs the cut path. |
| R4-9 | If fact (b) fails, the ownership guards are honor-system. | Accepted, verified | A failed fact (b) is a stop. |
| R4-10 | Fact (c)'s output would put private sessions in a public page. | Accepted, verified | `--cwd` this repository, and field names only. |
| R4-11 | Codex pickup is shown by wiring and cases, not a run. | Accepted, verified | Stated as an unverified limit. |
| R4-12 | A session answering its own item in its own pass counted as pickup. | Accepted, verified | Excluded from the count. |
| R4-13 | A closed item never reached the session that asked. | Accepted, verified | Pickup shows closed items with their reason; `done` acknowledges them. |
| R4-14 | `docs/layout.md`'s page table got no row. | Accepted, verified | Slice 3 adds it; the cut path removes it. |

Round 5, 2026-11-18. A fresh session read the fifth draft and the sources. All 14 round-4 actions are in the body; two were applied in part, two did not reach the criteria, and one made a new problem.

| # | Finding | Verdict | Action |
|---|---|---|---|
| R5-1 | Criterion 5 still required the liveness R4-1 removed. | Accepted, verified, finishing | Criterion 5 matches slice 1. |
| R5-2 | Any session running `pass start` would end the person's pass mid-way; the park steps and the pass steps shared a page. | Accepted, inferred | `pass start` refuses while the open pass had a write in the last 30 minutes, unless `--replace`, and prints what it ends. The playbook re-asks from the last confirmed thread, and parking is a separate section with no pass commands. |
| R5-3 | Criterion 12's greps matched text the plan requires. | Accepted, verified, finishing | One pattern for a command that carries a prompt; the page states the prohibition without naming a tool. |
| R5-4 | Closed items were only half wired: criterion 5 and `take` disagreed with slice 1. | Accepted, verified, finishing | `done` refuses `open` and `done`; criteria 6 and 7 cover closed items; `take` accepts them. |
| R5-5 | A stand-in "user skill" cannot load without loading the private one, and writes outside the repository. | Accepted, inferred | The stand-in is a second local plugin in the case's scaffold. Fact (e) checks whether user skills load in eval runs. |
| R5-6 | Nothing gives a still-open session its answers. | Accepted, verified | `queue list --mine`, named in the playbook, with a test. |
| R5-7 | Fact (b)'s stop rule had no branch for Claude Code passing and Codex failing. | Accepted, verified | A Codex-only failure makes the ownership commands refuse under Codex, stated in the README. Codex resume goes through `take`. |
| R5-8 | Fact (d) cannot test a wrapper that does not exist yet. | Accepted, verified | It tests a throwaway wrapper of the planned size, or one B6 shipped. |
| R5-9 | The report would call every Codex session gone and offer to take its answers. | Accepted, inferred | Items record the agent tool; Codex sessions are "liveness unknown" with no `take` line unless asked. |
| R5-10 | The fact (e) fallback silently turns off the maintainer's daily tool everywhere. | Accepted, inferred | A narrower guard first: the private skill refuses inside this repository. The user-level deny is the last resort, with its cost stated. |
| R5-11 | Tests and trials could write into the live store for good. | Accepted, inferred | `WS_QUEUE_DIR` overrides the folder; tests use a throwaway one; criterion 4 checks the live store is untouched. |
| R5-12 | The Verification block left out criteria 9, 11 and 12. | Accepted, verified | Added. |
| R5-13 | C3 lacked the own-pass exclusion criterion 12 counts. | Accepted, verified, finishing | C3 carries it. |
| R5-14 | Slice 5 named one Codex limit where there are two. | Accepted, verified, finishing | Both named. |
| R5-15 | The counting window had no end. | Accepted, verified | `--until`. |
| R5-16 | A cut after a slice 4 miss listed files on an unmerged branch. | Accepted, verified | Close that pull request and cut only what merged. |
| R5-17 | `do` and `notice` items had no path to `done`. | Accepted, inferred | One sentence each in slice 1. |

Round 6, 2026-11-18. A fresh session read the sixth draft and the sources. All 17 round-5 actions are in the body; four made new problems. It found no blocker.

| # | Finding | Verdict | Action |
|---|---|---|---|
| R6-1 | The cut path left a reference page in `docs/playbooks/`, and moved it and changed its proof keys in one commit; both are refused. | Accepted, verified | Move to `archive/` in one commit, strip the keys in a second. |
| R6-2 | `claude agents --cwd` may list background sessions only, so the report would call interactive ones gone. | Accepted, verified | Fact (c) checks it; on a miss the report filters `--json` in memory. |
| R6-3 | Without `--scaffold` the stand-in never loads, and the should-fire case passes by default. | Accepted, verified, finishing | `--scaffold` and `--runs 10`; a grader checks the stand-in loaded; a run without it is invalid. |
| R6-4 | The narrow guard never triggers in eval runs, which use temporary folders. | Accepted, verified | Fact (e) is split. Eval runs get a user-level deny held only during slice 4's runs, its cost stated. |
| R6-5 | Checking fact (e) by calling the skill would load the original, and slice 0 ran before the turn-off. | Accepted, verified | Fact (e) reads the skill listing only; slice 0 waits for the turn-off. |
| R6-6 | The Codex branch left "ownership commands" undefined and contradicted the non-goals. | Accepted, verified | The commands are listed; on that branch Codex neither files nor picks up, and the README says so. |
| R6-7 | Acknowledged closed items could inflate C3. | Accepted, verified | Counted apart, never toward C3; the status after `done` is stated. |
| R6-8 | A size check on the live store fails when another session files during the tests. | Accepted, inferred | A unique marker, checked absent; a missing live store passes. |
| R6-9 | Criterion 5 missed the idle-pass branch and `pass end` from another session. | Accepted, verified, finishing | Both added. |
| R6-10 | The hook and `list --mine` cannot share wording under 0004's import list. | Accepted, verified | `wslib.queuetext`, added to the allowed modules by the amendment. |
| R6-11 | Slice 5's `docs/parts.md` edit missed the facts table. | Accepted, verified, finishing | Named, in slice 5 and the cut path. |
| R6-12 | The 9,000-byte ceiling is hard-coded, and M3 resets it. | Accepted, verified | Read from `workspace.json`. |
| R6-13 | Verification omitted the `-v` run. | Accepted, verified, finishing | Added. |
| R6-14 | The grep missed common resume-with-prompt forms. | Accepted, inferred | Widened, and the page's prose covers the rest. |
| R6-15 | Building in a worktree contradicts the contract's "only then". | Rejected | The maintainer's standing rule since M2's slice 4 builds slices in worktrees; the M3 plan carries it. The Limits line now cites it. |
| R6-16 | `CLAUDE_CODE_SESSION_ATTENDED` may signal "no person present", and helpers share their parent's session id. | Accepted, verified | Fact (b) records both; helpers run no queue command; the park rule may use the variable. |

## Approval

Not yet approved.

## Changes after approval

## Results
