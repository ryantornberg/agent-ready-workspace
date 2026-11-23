---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/architecture-review/SKILL.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: plugin/skills/architecture-review/SKILL.md

This records the review of the architecture-review wrapper that slice B6 adds, for its author and its readers.

**In short:** 2 findings: 1 trigger, 1 contradiction, none blocking. The description hands a plain review request to the review orchestrator by name alone, with no wrapper and no path to reach it. And the waiting list says the orchestrator cannot run before M4, while its own page says every step is done by hand today.

## Scope

In scope: the whole wrapper, its front matter (`name`, `description`) and its body, which the staged change adds (`git diff --cached`). Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/README.md`, `docs/how-tos.md`, `docs/playbooks/architecture-review.md`, `docs/playbooks/review-orchestrator.md` ("When it runs, and which page wins" and its table of what is done by hand), `docs/review-in-a-worktree.md`, every other wrapper under `plugin/skills/`, the cases `plugin/evals/architecture-review-fires` and `plugin/evals/architecture-review-quiet`, `parts/wrappers.py`, and the `wrappers` and `loaded_size` entries in `workspace.json`.

Run, on macOS: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 17 of 17 cases` and `loaded_size: 4 of 4 cases`; `claude plugin validate plugin`, on Claude Code 2.1.330, passes with one warning, for a missing icon (verified). The 28 descriptions come to 6,542 bytes against the 9,000-byte ceiling; this one is 295, the longest (verified). No selection case has run yet, as `evals/README.md` says (verified, reading), so every claim below about what a description fires on is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | Front matter, `description`, the sentence "A plain request for a review is the review orchestrator's." | Not blocking. The sentence sends a plain review request away from this wrapper to a page with no wrapper, and gives no path to it. The `wrappers` entry's waiting list holds the review orchestrator for M4 (verified), so no description fires on "review my branch", and an agent that obeys this sentence holds only a name. Every other neighbor the description names is a `workspace:<name>`. The wrapper most likely to fire instead, `workspace:review-in-a-worktree`, does reach the orchestrator in its step 5, but only for a pull request, not for the agent's own branch (verified, reading). Name the page's path in the sentence, `docs/playbooks/review-orchestrator.md`. The `wrappers` check allows it, since it reads page paths from the body only (verified: `PAGE_PATH` is applied to `body(text)` in `parts/wrappers.py`). | fixed: the sentence names `docs/playbooks/review-orchestrator.md`. |
| 2 | contradiction | Front matter, `description`, "the review orchestrator's", against the `wrappers` entry's waiting list and the catalog's "Three ways to follow a playbook", item 3 | Not blocking. The part's docstring says a waiting page is one that "cannot run before the milestone that builds what it needs". The catalog says the three pages "wait for the milestone that builds what they need", and the entry's `why` names the orchestrator's dispatch, completion reading, findings manifest and review mark as M4's machinery (verified, reading). The orchestrator's own **In short** line says "Its machinery is planned for M4, so today every step is done by hand", and its table lists each of those four as done by hand today. Architecture review's "When it runs" says the orchestrator runs it "by hand until its machinery lands in M4" (verified, reading). Both cannot hold. Either the orchestrator runs today and gets a wrapper, or the pages that send plain reviews to it today say it cannot run. This wrapper is where the two meet, since its description is the one that names the orchestrator. | fixed: the waiting entry's reason and the catalog now say the orchestrator runs by hand today and that its wrapper waits for M4's machinery, as the plan's red-team finding 14 and its "Later" list set. |

## Checked with no finding

- step: the body names one page, `docs/playbooks/architecture-review.md`, which exists, is a playbook with no `lane` key and has numbered steps (verified).
- enforcement: the wrapper states no must or never. The rule that a wrapper stays thin is tagged `prose` in the catalog; the name, page, neighbor and case rules are enforced by the `wrappers` check, whose cases pass (verified).
- placement: the description says only when to fire and when not, and restates no step of the page (verified, reading). It matches the catalog row, "when the request names that question alone".
- eval-case: the fires case asks for the diff on a branch to be checked against the system's decisions and the right problem; the quiet case asks for a fresh critic on a finished plan, which `workspace:red-team-review` owns and the description names (verified, reading). The page is marked unproven with `prove-by: M6`.

## Re-check

A fresh session re-read the wrapper on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6 (`git diff --cached`). It read the wrapper as staged, its canonical page, every other wrapper's description and the selection cases under `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; the 28 descriptions now come to 7,535 bytes against the 9,000-byte ceiling (verified). No selection case has run, so what a description fires on stays inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld: fixed | The description says "A plain request for a review is the review orchestrator's, docs/playbooks/review-orchestrator.md." The path exists, and the `wrappers` check reads page paths from the body only, so it still passes (verified, `python3 ws.py check`). |
| 2 | upheld: fixed | The waiting entry's `why` and the catalog's item 3 now say the orchestrator runs by hand today and its wrapper waits for M4's machinery, which matches the orchestrator's **In short** line; the part's docstring says a waiting page's wrapper waits for the milestone that builds its machinery (verified, reading). |

What a fix broke: Nothing.

What the first reading missed: Nothing.
