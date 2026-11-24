---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/reuse-checklist/SKILL.md
reviewed-at: 1a276e9, with the staged change of slice B6
---

# Instruction review: plugin/skills/reuse-checklist/SKILL.md

This records the review of the reuse-checklist wrapper's rewritten description, after the first selection run, for its author and its readers.

**In short:** 1 finding: 1 trigger, not blocking. A new clause repeats the fires case's last nine words, so the case tests wording rather than selection.

## Scope

In scope: the `description` line, the only line the staged change alters (`git diff --cached`); the body is unchanged. Read beside it: `AGENTS.md`, `docs/playbooks/README.md`, `docs/playbooks/reuse-checklist.md`, `docs/playbooks/test-first.md`'s step 1, every other wrapper's description under `plugin/skills/`, every case's `prompt.md` under `plugin/evals/`, `evals/selection/2026-11-23/aggregate-result.json`, "The wrappers' selection cases" in `evals/README.md`, criterion 22 of `docs/plans/m3-reading-layer-machinery-and-kit.md`, the B6 record `2026-11-23-b6-wrapper-reuse-checklist.md`, and the `wrappers` and `loaded_size` entries in `workspace.json`. Neighbours read against the rewrite: `workspace:impact-analysis`, whose fires case is this wrapper's quiet case and whose quiet case is this wrapper's fires case; `workspace:test-first`, `workspace:fix-a-bug` and `workspace:research-ladder`.

Run, on macOS: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; `claude plugin validate plugin`, on Claude Code 2.1.331, passes with warnings (verified). The 28 descriptions come to 8,613 bytes against the 9,000-byte ceiling, 924 more than at the base commit; this one is 384 bytes, up from 247 (verified). In the first selection run, on haiku, the fires case passed 0 of 3 runs and the quiet case 3 of 3 (verified, reading the result). No run has read the rewritten description, so every claim below about what it fires on is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | Front matter, `description`, "or asks whether the code already has something that does the job" | Not blocking. The fires case reads "Before I write a new date-formatting helper for the sales report, check whether the code already has something that does the job" (verified, reading). The rewrite's clause repeats its last nine words, and "about to add a helper" echoes "Before I write a new ... helper" (verified, reading the diff). The case now tests whether the description holds the request's words more than whether the model routes a reuse search here (inferred). A request of the same kind in other words, such as "is there already a function that parses order dates?", meets only "about to add a helper, a function or other new logic under src/" (inferred). Word the clause from the page instead, such as "or asks to search for existing code before new logic is written". | fixed: "whenever a request would add a helper, a function or other new logic under src/: it finds code that already does the job". |

## Checked with no finding

- contradiction: "under src/" and the reviewer's half "when the request names reuse alone" match the page's "When it runs" (verified, reading). "Use it first" agrees with test first's step 1, which runs the author's steps of this checklist before new logic (verified, reading). The neighbour it names, `workspace:impact-analysis`, exists and names this wrapper back for finding code to reuse (verified).
- step: the body is unchanged and names `docs/playbooks/reuse-checklist.md`, which exists; the `wrappers` check passes (verified).
- enforcement: the description states no must or never. The `wrappers` check holds its name, page, neighbours and cases, and its cases pass (verified).
- placement: the description says when to fire and when not, and restates no step of the page (verified, reading).
- eval-case: both selection cases exist (verified). The quiet case lists everything a change to how `order_total` is computed reaches; it adds no logic and asks for no existing code, so it stays outside the rewrite and with `workspace:impact-analysis` (inferred). The page is marked unproven with `prove-by: M6`.

## Re-check

A fresh session at the driver tier re-read the staged description on 2026-11-23, after the fix round, against its page, every other wrapper's description and the neighbours' selection cases in `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases` (verified). The 28 descriptions now come to 8,449 bytes against the 9,000-byte ceiling (verified). No selection run has read the final descriptions, so every claim about what they fire on is inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | The clause "asks whether the code already has something that does the job" is gone (verified, searching the description). "Finds code that already does the job" is the base description's and the catalog row's wording, "to find code that already does the job", not the case's alone (verified, reading both). This description is 349 bytes (verified). The new trigger has a cost; see R1. |

| # | Kind | Finding | Disposition |
|---|---|---|---|
| R1 | broke | trigger. Not blocking. The fix keyed the trigger to the request: "Use it first whenever a request would add a helper, a function or other new logic under src/". The first rewrite keyed it to the moment before writing, "about to add a helper, a function or other new logic under src/" (verified, reading this record's quote), as the base's "Use before writing new logic" and the page's "When it runs" do (verified, reading). Most requests to build or fix code would add logic, so this now claims "first" for test first's fires case, a plan's slice, and for a bug fix that adds a branch, where fix a bug's description also says "Use it first" (verified, reading; the match is inferred). Five of the 28 descriptions now say "Use it first" (verified, searching them). Test first's step 1 already sends an agent here, and this page's author's step 5 returns the agent "to the procedure that sent you" (verified, reading); an agent that loads only this wrapper for a slice has no such procedure to return to (inferred). Not blocking: the page's "When it runs" sets the same moment, so the checklist is right as a first step, and the owning wrapper's description matches the request too (inferred). Key the trigger to the moment again, such as "Use it before writing a helper, a function or other new logic under src/, inside the procedure that builds the change". | fixed (second round): "Use it before writing new logic under src/, such as a helper or a function", without "first", as the page's timing was before the rewrite. |

What the first reading missed: nothing found. R1 is the fix round's. Research ladder's restored trigger also matches this wrapper's fires case; that is recorded in `2026-11-23-b6-rewrite-research-ladder.md`, R1.

## Second re-check

A fresh session at the driver tier re-read the unstaged second-round change on 2026-11-23, on commit 1a276e9, against its page, every other wrapper's description and the selection cases in `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` exits 0, reporting `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases` (verified). The 28 descriptions now come to 8,542 bytes against the 9,000-byte ceiling (verified). No selection run has read these descriptions, so every claim about what they fire on is inferred.

| # | Verdict | Evidence |
|---|---|---|
| R1 | fixed | The trigger is keyed to the moment again: "Use it before writing new logic under src/, such as a helper or a function, to find code that already does the job", without "first" (verified, `git diff`). That is the base's "Use before writing new logic" and the page's "When it runs", "before you write new logic in code under `src/`" (verified, reading). It no longer claims a whole request, so it no longer competes with fix a bug's or test first's "first" for a request that only adds logic along the way (inferred). The suggested "inside the procedure that builds the change" was not added; the timing alone answers the finding (inferred). This description is 330 bytes (verified). |

Nothing this round broke was found. The fires case still matches by its own words, "Before I write a new date-formatting helper", and research ladder's new Not clause and impact analysis's description both send it here (verified, reading; the routing is inferred).
