---
kind: record
last-reviewed: 2026-11-23
covers: docs/saved-workflows.md
reviewed-at: 1a18d68, with the uncommitted change of the B4 slice session
---

# Instruction review: docs/saved-workflows.md

This records the instruction review of slice B4's new automation lane how-to on saved workflows, for the change's author.

**In short:** 4 findings: 2 step, 1 contradiction, 1 enforcement; 1 blocking. Step 2 of writing a workflow says a script outside the machinery list "skips the machinery path", while step 4 and the contract send every script down it. Step 2's stop to ask the person has no path after the answer and no rules row. Neither the writing steps nor the running steps say where the agent tool and its run command come from, or what to do when there is none.

## Scope

In scope: the whole page, which is new and untracked. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/extend-the-workspace.md`, and the pages it links to: `docs/decisions/0006-what-proven-means.md`, `docs/playbooks/review-orchestrator.md`, `docs/playbooks/regression-run.md`, `docs/orchestration.md`, `docs/changing-the-machinery.md` and `workspace.json`. Also read the page's routing rows in `git diff` of `README.md` and `docs/how-tos.md`, the regression run report template, and the M3 plan's B4 row. Ran the page's one command, `python3 -c "import json; print(json.load(open('workspace.json'))['tiers'])"`, at the top of the workspace: it printed the three tiers and exited 0. Ran `python3 ws.py check`: no finding on this page; only the known `eval_record` warning on fix a bug.

The page has no `## References` heading.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Steps to write one, steps 2 and 4; Rules, the last-but-one row | Blocking. Step 2 says "A script outside the machinery list skips the machinery path." Step 4 says "Take the machinery path" with no exception, and the contract's "How work flows" says "A change to scripts, parts, hooks or CI is machinery". The Rules row covers only "A script under `tools/`", so it leaves the case open. An agent whose tool needs the script elsewhere, such as under `.claude/`, can read step 2 as leave to skip step 4. It would then commit a script as a page change, straight to main with no failing case and no CI on three systems. Verified: the `direct_push` machinery list in `workspace.json` holds `tools/` and only `.claude/settings.json` under `.claude/`; changing the machinery's table ends "Everything else is a doc"; the three texts above. Inferred: that an agent reads "skips" as an instruction, not a warning. Saying that a script outside the list escapes the `direct_push` check but still takes the machinery path settles it. | fixed: step 2 now says the script is machinery wherever it lives and takes the machinery path in step 4; a folder outside the `direct_push` part's machinery list escapes that check, not the path. The In short line and the rules row say the same. |
| 2 | step | Steps to write one, step 2 | Not blocking. "Stop and ask the person first" has no path after the answer. It does not say where the script goes on a yes, whether step 4 still applies, or what to do on a no when the agent tool cannot run a script from `tools/`. Verified by reading step 2 and the steps after it. | fixed: step 2 says what follows the answer: on a yes, use that folder, with step 4 still applying; on a no or no answer, write no script and report. |
| 3 | step | What exists today, the agent tool's row; Steps to write one, step 3; Steps to run one, steps 1 and 2 | Not blocking. The page says "The instance names its tool and that tool's run command", but no page says where an instance names them, and this repository names neither. Writing step 3 gives no default for how the script dispatches a helper. Running step 2 runs `<the run command the instance names>`. Neither has a stop for a tool that "cannot run one at all", or, when running, for no saved workflow existing, which is the case here. Verified: the table's rows say "None in this repository" and "some cannot run one at all"; `grep -rn -i "run command" docs` finds only this page's two lines and unrelated plan rows, so no page names one. Inferred: an agent does not run the placeholder as written; it is more likely to stop at step 1 with no script to read, with no stop condition telling it to. | fixed: the tool's table row says the instance names its tool and run command in its own docs and this repository names neither; writing step 1 stops when no tool can run a saved workflow; running step 1 stops when no workflow or run command exists, and the caller dispatches by hand as orchestration says. |
| 4 | enforcement | Steps to write one, step 2; Rules | Not blocking. Step 2's "stop and ask the person first" before placing a script outside `tools/` is a must with no row in the Rules table. [Extend the workspace](../../extend-the-workspace.md#steps) step 4 asks for a row for every must and never on the page. Verified: the table's eight rows, none of which names the placement or the person's yes for it. | fixed: added a rules row: a script goes outside `tools/` only on the person's yes. |

## Checked with no finding

- trigger: the purpose line, the **In short** line and the how-to index's new "Lane drafts" row agree on the scope: writing or running a script that dispatches helpers in a fixed shape. "When to use it, and which page wins" sends a one-off dispatch to orchestration. The regression run playbook routes to this page for its stage 2.
- placement: step 5 of writing and step 4 of running link procedure endings instead of restating them; the tier and model rules link orchestration's binding; the shared-environment yes matches regression run's default of the person's local environment.
- eval-case: the page is marked `proof: unproven` with `prove-by: M10`, the automation lane's milestone in the M3 plan's B4 row, and M10 is not in `building`, so its new behavior needs no eval case yet. Its `lane: automation` key is one of the five values.

## Re-check

A fresh session's reading after the fix round, on `1a18d68` with the uncommitted fix of the B4 slice session. It read the page in full, the contract, procedure endings, `docs/changing-the-machinery.md`, `docs/orchestration.md`, `workspace.json` and the how-to index's row, and ran `python3 ws.py check`, which reports nothing on this page.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | Verified: step 2 now says "Wherever it lives, the script is machinery, as the contract says, and takes the machinery path in step 4", and that a folder outside the `direct_push` part's machinery list "escapes that part's check, not the path". The **In short** line and the rules row say the same. Procedure endings' "Where the commit goes" sends a change to scripts to a branch of its own, which agrees. No sentence left reads as leave to skip step 4. |
| 2 | upheld | Verified: step 2 gives both paths after the question: on a yes, that folder, with step 4 still applying; on a no or no answer, no script and a report. |
| 3 | upheld | Verified: the tool row says the instance names its tool and run command in its own docs and this repository names neither. Writing step 1 stops when no tool can run a saved workflow. Running step 1 stops when no workflow or run command exists, and sends the caller to dispatch by hand as orchestration says. Inferred: in this repository both procedures stop at their step 1, which is the intended outcome. |
| 4 | upheld | Verified: the rules row "Place a script outside `tools/` only on the person's yes." |

What a fix broke:

- Not blocking. Finding 1's fix makes a script outside the `direct_push` list machinery. Changing the machinery's "What counts as machinery", the page step 4 links, ends "Everything else is a doc". This page labels its rule as an exception to the check, not to that sentence. Following this page takes the stricter path, which the contract's "How work flows" and procedure endings' "Where the commit goes" both support, so no write goes where it may not. Verified: the three texts.
- Not blocking. The how-to index's Remember cell for this page still says only "A script under `tools/` is machinery". Recorded on the how-to index's record.

What the first reading missed:

- None.

## Known defects

What stays open after the one fix round the plan allows, each not blocking.

- Not blocking, what a fix broke: the page makes a script outside the `direct_push` list machinery, while changing the machinery ends "Everything else is a doc". The page takes the stricter path. Known defect, for M10.
