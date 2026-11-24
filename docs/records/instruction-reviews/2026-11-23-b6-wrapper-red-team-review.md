---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/red-team-review/SKILL.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: plugin/skills/red-team-review/SKILL.md

This records the review of slice B6's new `red-team-review` wrapper, for its author and whoever settles its findings.

**In short:** 2 findings: 1 contradiction, 1 trigger, none blocking. The description offers a spec as something to attack on its own, which the page forbids, and it sends every code diff to architecture review, which owns only a diff's design question.

## Scope

In scope: the whole wrapper, new in this change: its `name`, its `description` and its body, read against the page its body names. The change was read with `git diff --cached`. Read beside it: `AGENTS.md`, `INDEX.md`, the playbook catalog `docs/playbooks/README.md`, `docs/how-tos.md`, `docs/playbooks/red-team-review.md` in full, `docs/playbooks/architecture-review.md` and `docs/playbooks/review-orchestrator.md` (their opening and "When it runs"), `docs/size-the-work.md`, the `architecture-review` and `decision-interview` wrappers' descriptions, the description of every other wrapper under `plugin/skills/`, its selection cases `plugin/evals/red-team-review-fires` and `-quiet`, `parts/wrappers.py` and `parts/wrappers.cases.json`, and the `wrappers` and `loaded_size` entries in `workspace.json`.

Run, on macOS, in the worktree, before any record was written: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` exits 0 and lists `wrappers: 17 of 17 cases` (verified). With the records written, `check` fails only on `review_index`, for the index rows the author adds at step 5 (verified). The 28 wrappers' descriptions come to 6,542 bytes against the 9,000 the `loaded_size` entry allows (verified, summing each `description` value). The selection cases have not run: `evals/README.md` says the first run waits for the maintainer's yes to its budget. So every claim below about which wrapper a model would load is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | The description, "a finished hand-off plan, spec or requirements document" | Not blocking. The description lists a spec beside a plan and a requirements document, as a document to attack on its own. The page says a spec "lives in three sections of a hand-off plan ... so it is reviewed with the plan that holds it, never alone", and that a feature's red team runs on the plan after the spec is agreed (verified, reading "When it runs"). Say "a finished hand-off plan, with its spec, or a requirements document", as the page's purpose line does. Not blocking: step 1 checks that the document is a plan or a requirements document, and stops if not. | fixed: "a finished hand-off plan, with its spec, or a requirements document". |
| 2 | trigger | The description, "Not for a code diff (workspace:architecture-review)" | Not blocking. The description sends every code diff to architecture review. The page sends "a review of the branch or pull request" to the review orchestrator, and only "a question about its design alone" to architecture review (verified, reading "When it runs"). Architecture review's own description says "A plain request for a review is the review orchestrator's", so an agent sent there for a plain review is sent on again. The orchestrator has no wrapper to name, since the `wrappers` entry keeps it waiting for M4 (verified, reading `workspace.json`). Say "a code diff, which goes to the review orchestrator, or to workspace:architecture-review for its design alone". Inferred: the quiet case, a diff checked against the system's decisions, tests only the design question. | fixed: a plain review goes to the review orchestrator's page, by path, and a diff's design alone to workspace:architecture-review. |

## Checked with no finding

- step: the body names one path, `docs/playbooks/red-team-review.md`, which exists and is a playbook with no `lane` key and no place on the waiting list, as the `wrappers` check confirms on this tree (verified). Its one action, to read the page and follow it, needs no input it does not name.
- enforcement: the wrapper states no must or never of its own. The catalog's rules that bind it are tagged to `wrappers` cases that show them: a description that names no wrapper next to it fails `a wrong name or no description fails`, and a page that is missing fails `a wrapper whose page is missing fails` (verified, reading `parts/wrappers.cases.json`; selftest passes them). That a wrapper stays thin is tagged `prose`, and this one is: its body restates no step of the page.
- placement: the description, which loads into every session, holds only when to fire and the wrapper next to it that owns the nearby request; it restates no rule of the page. The body is one pointer.
- eval-case: the one behavior the wrapper asks is loading its page on a matching request, and its selection cases cover it: `red-team-review-fires` (`min: 1`) and `red-team-review-quiet` (`min: 0`, `max: 0`, `arm: both`), each `input_match` in the one form the check takes (verified, reading). What the page then asks is the page's own; `docs/playbooks/red-team-review.md` is marked unproven with `prove-by: M9` (verified, reading its front matter).

## Re-check

A fresh session re-read the wrapper on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6 (`git diff --cached`). It read the wrapper as staged, its canonical page, every other wrapper's description and the selection cases under `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; the 28 descriptions now come to 7,535 bytes against the 9,000-byte ceiling (verified). No selection case has run, so what a description fires on stays inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld: fixed | The description says "a finished hand-off plan, with its spec, or a requirements document", the page's own purpose line (verified, reading). |
| 2 | upheld: fixed | The description says a plain review is the review orchestrator's, `docs/playbooks/review-orchestrator.md`, and a diff's design alone is architecture review's, as the page's "When it runs" does (verified, reading). The quiet case, a diff checked against the system's decisions, stays outside it. |

What a fix broke: Nothing.

What the first reading missed: Nothing.
