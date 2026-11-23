---
kind: record
last-reviewed: 2026-11-23
covers: docs/templates/regression-case.md
reviewed-at: 1a18d68, with the uncommitted change of the B4 slice session
---

# Instruction review: docs/templates/regression-case.md

This records the instruction review of slice B4's new regression case template, a QA lane draft, for the change's author.

**In short:** 6 findings, none blocking: 3 contradiction, 1 step, 1 trigger, 1 placement. The worked example takes its expectation from the code the page forbids reading for one. "A smoke case runs on every run" does not hold when a run selects by area or case id. A sink check's command written as the page asks is a placeholder the run cannot run.

## Scope

In scope: the whole page, which is new and untracked. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/extend-the-workspace.md`, and the pages it links to: `docs/playbooks/regression-triage.md`, `docs/playbooks/regression-run.md`, `docs/templates/regression-candidates.md` and `docs/orchestration.md`. Also read `src/orders-api/AccountFreeze.cs`, which the worked example names, the new "Lane templates" rows in `docs/templates/README.md` (`git diff -- docs/templates/README.md`), and `docs/reading-paths.md`'s QA list. The page gives no command to run. Ran `grep` for inbound links to the page, and `python3 ws.py check`, which reports nothing on this page.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | A worked example; Where expectations come from | Not blocking. "Where expectations come from" says to take every checkpoint from product intent and "Never derive one from reading the code". The worked example's lead-in says the case "follows the live order service's rule ... as `AccountFreeze` in `src/orders-api/AccountFreeze.cs` describes": its expectation is taken from the code's doc comment. An agent that copies the example cites code as a case's basis. Verified: the page's two passages, and the doc comment in `AccountFreeze.cs`, "orders are accepted and not shipped until it is lifted". | fixed: the worked example's lead-in now takes its expectations from the invented ticket ORD-412, not from `AccountFreeze`'s code. |
| 2 | contradiction | Filling it in, Tier | Not blocking. The page says "A `smoke` case runs on every run". Regression run's step 6 selects "by tier, area, priority or case id, as the request says", so a run asked for one area or one case id leaves out the other areas' smoke cases. Its stage 1 also runs only the automated smoke cases; an agent-mode smoke case, such as the worked example's, runs in stage 2. Verified: the page's Tier bullet beside regression run's steps 6 to 8. | fixed: the Tier bullet says a smoke case runs on every run that selects by tier, a narrowed run runs only what it names; regression run's step 6 now runs each mode in its own stage, smoke-tier first. |
| 3 | contradiction | Filling it in, Case id; Rules, the fourth row | Not blocking. The Case id bullet says an id "never changes, even when the journey's wording does". The Rules row says it "never changes once a run has used it", which lets an id change before the first run. The two cannot both be the rule. Verified: the two texts. | fixed: the Case id bullet now says the id never changes once a run has used it, matching the Rules row. |
| 4 | step | Filling it in, Sink checks | Not blocking. The bullet says a sink check's query command "is the instance's own, written as a placeholder in angle brackets". In an instance's own case file, that leaves the command unfilled: a helper in regression run's stage 2 "runs the case's sink checks" and has nothing it can run, and regression run treats "a placeholder with no filling in the instance" as a stop. The page does not say that the placeholder is only for this template, and that a copy holds the real command. Verified: the two texts. Inferred: that an agent writing a case follows the bullet literally. | fixed: the bullet says an instance's case file holds the real query command, and only this page shows it as a placeholder. |
| 5 | trigger | When to use it | Not blocking. The page names one reason to fix a case: one "regression triage found to be a test defect". Regression triage's step 8 also fixes the case file for the "Intended behavior" class, naming the ticket or spec. That fix does not fire this page's trigger, though it rewrites a case's expectation and its Source. Verified: regression triage's class table and step 8. The templates README row, "You write or fix one case", does cover it. | fixed: When to use it now names fixing a case triage found to be a test defect or intended behavior. |
| 6 | placement | Filling it in, Steps and checkpoints | Not blocking. "A run takes a screenshot at each checkpoint" states a run's duty on the case template, restating regression run's step 8, and states it wider: step 8 asks it only of the agent-mode helpers. An `automated` case run by the instance's test runner, or a `human` case on a device, gets no such rule there. The run's rule belongs on the run's page, linked from here. Verified: regression run's step 7, 8 and 9. | fixed: the screenshot sentence is replaced by a link to regression run's steps for what a run records at each checkpoint. |

## Checked with no finding

- enforcement: each must and never on the page has a Rules row, all tagged `prose`, which `rules` accepts; the planned case checker is named as planned for M10 and is never a step to run.
- eval-case: a lane template carries no proof keys, by layout's page kinds table; the procedures that use the template, regression run and regression triage, are marked `proof: unproven` with `prove-by: M10`. Verified: their front matter.

## Re-check

A fresh session's reading after the fix round, on `1a18d68` with the uncommitted change of the B4 slice session. Read the whole page, the contract, procedure endings, and each page the changed text links to: regression run's steps, regression triage's classes and step 8, and the regression candidates template. The page gives no command to run.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | Verified: the lead-in names the invented ticket ORD-412 as the source, and the example's Source field says the same. No code is cited. |
| 2 | upheld | Verified: the Tier bullet limits "every run" to a run that selects by tier, and a narrowed run runs only what it names. Regression run's step 6 runs each mode in its own stage, smoke-tier first. |
| 3 | upheld | Verified: the Case id bullet and the Rules row both say the id never changes once a run has used it. |
| 4 | upheld | Verified: the Sink checks bullet says an instance's case file holds the real query command, and only this page shows a placeholder. The worked example's placeholder is covered by that line. |
| 5 | upheld | Verified: "When to use it" names both triage classes that fix a case, test defect and intended behavior, matching triage's step 8. |
| 6 | upheld | Verified: the Steps and checkpoints bullet links regression run's steps, and the anchor exists. The screenshot duty is no longer stated here. |

What a fix broke: none.

What the first reading missed: none.
