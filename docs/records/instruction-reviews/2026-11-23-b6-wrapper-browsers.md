---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/browsers/SKILL.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: plugin/skills/browsers/SKILL.md

This records the review of the browsers wrapper that slice B6 adds, for its author and its readers.

**In short:** 1 finding: 1 step, not blocking. The body says to follow the page's steps, and the browsers page has none.

## Scope

In scope: the whole wrapper, its front matter (`name`, `description`) and its body, which the staged change adds (`git diff --cached`). Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/README.md`, `docs/how-tos.md`, `docs/browsers.md`, every other wrapper under `plugin/skills/`, the cases `plugin/evals/browsers-fires` and `plugin/evals/browsers-quiet`, `parts/wrappers.py`, the `wrappers` and `loaded_size` entries in `workspace.json`, and `.claude/settings.json`.

Run, on macOS: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 17 of 17 cases` and `loaded_size: 4 of 4 cases`; `claude plugin validate plugin`, on Claude Code 2.1.330, passes with one warning, for a missing icon (verified). The 28 descriptions come to 6,542 bytes against the 9,000-byte ceiling; this one is 203 (verified). No selection case has run yet, as `evals/README.md` says (verified, reading), so every claim below about what a description fires on is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | Body, "read the whole page and follow its steps" | Not blocking. `docs/browsers.md` has no steps. Its sections are "Why", "What is set, and where", "On Windows" and "Things to know", with no numbered list (verified, reading). An agent told to follow its steps finds none. What the page asks of an agent that needs a browser is to use the project's server and to expect an isolated browser to forget its logins; for the setup case the description names, the "On Windows" block is the only action. Not blocking: nothing fails and nothing is written. Say "read the whole page and act on it" in this body, or give the page steps for the setup case. | fixed: every wrapper's body now says to read the page and follow it, not its steps. |

## Checked with no finding

- contradiction: the description matches the how-to index row "Open a browser in an agent session" and the page's purpose line, which names anyone running more than one session or setting up a machine (verified, reading). The neighbor it names, `workspace:machine-self-check`, exists. The staged change adds the wrappers' plugin to `enabledPlugins` beside the browser plugin, which stays `false`, so the page's "What is set" table still holds (verified, reading the diff).
- trigger: the fires case is two sessions' browsers colliding; the quiet case is a laptop check, which `workspace:machine-self-check` owns and the description names (verified, reading). "An agent session needs a browser" fires on any browser task, which loads a 49-line page each time; the how-to index row routes that same task to this page, so the two agree.
- enforcement: the wrapper states no must or never. The rule that a wrapper stays thin is tagged `prose` in the catalog; the name, page, neighbor and case rules are enforced by the `wrappers` check, whose cases pass (verified).
- placement: the description says only when to fire and when not, and restates nothing from the page (verified, reading).
- eval-case: both selection cases exist (verified). The page is marked unproven with `prove-by: M6`.

## Re-check

A fresh session re-read the wrapper on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6 (`git diff --cached`). It read the wrapper as staged, its canonical page, every other wrapper's description and the selection cases under `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; the 28 descriptions now come to 7,535 bytes against the 9,000-byte ceiling (verified). No selection case has run, so what a description fires on stays inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld: fixed | All 28 bodies now say "read the whole page and follow it", and none says "its steps" (verified, reading every `SKILL.md`). Each body still names exactly one page, as the `wrappers` check requires (verified). |

What a fix broke: Nothing.

What the first reading missed: Nothing.
