---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/debugging/SKILL.md
reviewed-at: 1a276e9, with the staged change of slice B6
---

# Instruction review: plugin/skills/debugging/SKILL.md

This records the review of the debugging wrapper's rewritten description, after the first selection run, for its author and its readers.

**In short:** 1 finding: 1 trigger, not blocking. The rewritten list of failures takes its words from the wrapper's own fires case and drops the page's "bug report".

## Scope

In scope: the `description` line, the only line the staged change alters (`git diff --cached`); the body is unchanged. Read beside it: `AGENTS.md`, `docs/playbooks/README.md`, `docs/playbooks/debugging.md`, every other wrapper's description under `plugin/skills/`, every case's `prompt.md` under `plugin/evals/`, `evals/selection/2026-11-23/aggregate-result.json`, "The wrappers' selection cases" in `evals/README.md`, criterion 22 of `docs/plans/m3-reading-layer-machinery-and-kit.md`, the B6 record `2026-11-23-b6-wrapper-debugging.md`, and the `wrappers` and `loaded_size` entries in `workspace.json`. Neighbours read against the rewrite: `workspace:fix-a-bug`, whose quiet case is this wrapper's fires case, and `workspace:test-first`, whose fires case is this wrapper's quiet case.

Run, on macOS: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; `claude plugin validate plugin`, on Claude Code 2.1.331, passes with warnings (verified). The 28 descriptions come to 8,613 bytes against the 9,000-byte ceiling, 924 more than at the base commit; this one is 441 bytes, up from 273 (verified). In the first selection run, on haiku, the fires case passed 0 of 3 runs and the quiet case 3 of 3 (verified, reading the result). No run has read the rewritten description, so every claim below about what it fires on is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | Front matter, `description`, "a job, test, build or CI run that fails, fails now and then, or started failing" | Not blocking. The fires case reads "The nightly reconciliation job started failing about one run in five last week, and nobody knows why" (verified, reading). The rewritten list names a "job", "fails now and then" and "started failing", and "a failure nobody can explain yet" echoes "nobody knows why". The old list was the page's own, "a bug report, a failing test or CI run, or a flaky test", which the page's purpose line and the catalog's debugging row still use (verified, reading the diff, the page and the catalog). The case now tests whether the description repeats the request's words more than whether the model picks debugging for an unexplained failure (inferred). The list also drops "a bug report". A report of wrong behavior in the product, such as "customers sometimes get two confirmation emails and nobody knows why", is no job, test, build or CI run, and matches only the broader "reports a failure nobody can explain yet" (inferred). Put the page's kinds back in the list, such as "a bug report, or a test, job, build or CI run that fails every time or only sometimes", and keep the case's own phrasing out of it. | fixed: the kinds of failure are now the page's: "a bug report, a failing or flaky test, or a failing build or CI run has no known cause". |

## Checked with no finding

- contradiction: the description still says when to fire, an unknown cause, and when not, a known cause or a pull request's CI log that already says why, as the page's purpose line and the catalog row do (verified, reading). The neighbour it names, `workspace:fix-a-bug`, exists and names this wrapper back for an unknown cause (verified). That wrapper's side of the boundary moved in the same change; it is recorded in `2026-11-23-b6-rewrite-fix-a-bug.md`.
- step: the body is unchanged and names `docs/playbooks/debugging.md`, which exists; the `wrappers` check passes (verified).
- enforcement: the description states no must or never. "Use it first" says when to load the wrapper. The `wrappers` check holds its name, page, neighbours and cases, and its cases pass (verified).
- placement: "before reading or changing code" says when to load the wrapper, not how to work, and the description restates no step of the page (verified, reading).
- eval-case: both selection cases exist (verified). The quiet case, a plan's slice built one failing test at a time, has no failure to explain and stays outside the rewrite (inferred). The page is marked unproven with `prove-by: M4`.

## Re-check

A fresh session at the driver tier re-read the staged description on 2026-11-23, after the fix round, against its page, every other wrapper's description and the neighbours' selection cases in `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases` (verified). The 28 descriptions now come to 8,449 bytes against the 9,000-byte ceiling (verified). No selection run has read the final descriptions, so every claim about what they fire on is inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | The list is now "a bug report, a failing or flaky test, or a failing build or CI run", the kinds in the page's purpose line, "a bug report, a failing test or CI run, or a flaky test", with a build beside the CI run (verified, reading both). None of the fires case's words "job", "now and then", "started failing" or "nobody" is left in the description (verified, searching it). "Has no known cause" names the kind of request, not the case's "nobody knows why" (inferred). This description is 363 bytes (verified). |

What the first reading missed: nothing found. Fix a bug's quiet case, which is this wrapper's fires case, falls under "finding why something fails" and outside fix a bug's restored "Not when the cause is still unknown"; test first's fires case, this wrapper's quiet case, has no failure to explain (verified, reading the cases and descriptions; the routing is inferred).
