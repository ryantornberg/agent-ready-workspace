---
kind: record
last-reviewed: 2026-11-22
covers: docs/templates/fresh-session-prompt.md
reviewed-at: f757aed, with the uncommitted change of the B3 builder
---

# Instruction review: docs/templates/fresh-session-prompt.md

This records the instruction review of the new fresh-session prompt template, for its author and for anyone writing a prompt from it.

**In short:** 2 findings, 1 of them blocking: 1 step, 1 trigger. The blocking one: the fixed start step, `git pull --ff-only origin main`, fails on any branch with commits of its own, and in the main working copy it moves past the conditions decision 0005 sets for bringing main up to date.

## Scope

In scope: the whole page, as a new template. Read in full: the page; `AGENTS.md`, `INDEX.md`, `docs/playbooks/instruction-review.md`, `docs/procedure-endings.md`, `docs/layout.md`, `docs/reader-standard.md`, `docs/authoring.md`; B3's row and the 2026-11-22 entries naming B3 in the M3 plan; `docs/templates/README.md`, `docs/playbooks/handoff.md`, `docs/orchestration.md` (the three tiers, delegating, handing work off, fresh context for critics), the template section of `docs/playbooks/adversarial-review.md`, decisions 0005 and 0006, and git-host operations, tracker operations and fix a bug as loaded beside it. Ran `python3 ws.py check` in the worktree: it passed, with one warning about fix a bug's eval record, unrelated to this page. In a scratch repository, ran the skeleton's pull on a worktree branch with a commit of its own after main moved.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | Skeleton, Start from a known commit | Blocking. The skeleton fixes the step as "Run `git pull --ff-only origin main` in <the working copy's path>", and stops the session if the pull is refused. On a branch with commits of its own, such as a slice's branch in its worktree, the pull always fails, so a prompt that continues such work stops before it starts. The page names "one slice of a plan" as a use. In the main working copy, the pull fast-forwards main with no check for another live session. Decision 0005 brings main up to date at session start only with no tracked change and no other live holder, and its guards refuse a rebasing pull there but not a fast-forward one. A pull on a worktree branch with no commits of its own also moves the tip a reviewer was sent to read. Verified: in a scratch repository, the pull on a worktree branch with its own commit printed "Not possible to fast-forward, aborting." and exited 128; decision 0005's text. Inferred: that no guard refuses the fast-forward pull in the main copy while another session holds it. | fixed: the skeleton now names the working copy, its branch, the starting commit and `git status -sb`. The session runs `git fetch origin`, never pulls, and stops only when the working copy or branch differs. A branch behind main is reported, not rebased, unless the prompt says to. Step 4 and a rules row hold it. |
| 2 | trigger | When to use it; Where copies go | Not blocking. The page fires also "when a task needs a context of its own, such as one slice of a plan". Orchestration's delegating table already routes "A slice of an approved plan" to delegation at the plan's tier, and this page's own table sends only "a helper ... answers one question" there. So an agent dispatching a slice itself has two pages that claim it. "Where copies go" then fits only a person pasting the prompt: "Give it to the person in your reply, inside one fenced block". The templates index row fires only when "A person asks for a prompt", narrower than the page. Verified: the three texts. | fixed: the page now fires only for a prompt a person pastes into a new session. A slice or question this session hands to a helper goes to orchestration's handing work off, matching its delegating table and the templates index row. |

## Checked with no finding

- contradiction: the tier line matches orchestration's handing work off (`Tier: driver`, `worker` or `mechanical`); the handoff row matches handoff's resume line, `Read <path> and resume from its next step.`; the critic row matches orchestration's fresh context for critics and adversarial review's thin template. Verified.
- enforcement: each must and never has a rules row tagged `prose`: the six parts in order, claims never under "Settled", links instead of copies, and the critic's own template. Verified.
- placement: the report part points at procedure endings' report instead of restating it, and the prompt links the plan instead of copying it. The page is in the templates folder, which layout gives templates. Verified.
- eval-case: decision 0006 gives a template no proof mark, and the page's steps are steps for filling its shape. No eval case covers it, verified with `covered()` over the three cases.
- The reader standard does not bind the page's copies, since a prompt is read mainly by a session, not a person. Inferred. The page's own top layer is 73 words, under 120. Verified.

## Re-check

A fresh session re-read the page on 2026-11-22, after the fix round.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | The skeleton names the working copy, branch, starting commit and `git status -sb` line. The session runs `git fetch origin`, never pulls, and stops only when the working copy or branch differs. Step 4 and a rules row hold it. No step now moves a branch or the main copy. Verified: the page's text. |
| 2 | fixed | The page fires only for a prompt a person pastes into a new session. Its table sends a slice or question this session hands a helper to orchestration's "Handing work off", matching orchestration's delegating table. Verified: both texts. The templates index now disagrees, under "Broke". |

Broke:

- Not blocking. The templates index row for this page now reads "A person asks for a prompt to start a new session on a task, or a task needs a context of its own, such as one slice of a plan". The fix to the templates index's own finding 2 widened the row to the old trigger, while this page's fix narrowed the page. An agent dispatching a plan slice itself is sent here by the index and away from here by the page. Verified: `docs/templates/README.md` and this page's "When to use it".

Missed:

- Not blocking. "Start from a known commit" asks the session to report when "the branch is behind `origin/main`", but gives no command that shows it. `git status -sb` counts ahead and behind against the branch's upstream, which for a pushed task branch is its own remote branch, not `origin/main`. A command such as `git rev-list --count HEAD..origin/main` would. Inferred, from git's documented status output.
