---
kind: record
last-reviewed: 2026-11-23
covers: docs/environment-self-check.md
reviewed-at: 1a18d68, with the uncommitted change of the B4 slice session
---

# Instruction review: docs/environment-self-check.md

This records the instruction review of slice B4's new devops lane how-to for checking the product's local container environment. It is for the page's author.

**In short:** 5 findings: 2 contradiction, 2 step, 1 enforcement; 1 blocking. The prompt and the page's last paragraph forbid any write before or during the report, with no exception for the question-log row the contract requires. Steps 3 to 5 depend on values the environment page is not required to give.

## Scope

In scope: the whole page, which is new and untracked. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/extend-the-workspace.md`, and the pages it links: decision 0006, `docs/machine-self-check.md`, `INDEX.md`'s "Topics", `docs/definition-of-done.md` ("The report"), `docs/size-the-work.md` ("The gate"). Also checked that `docs/browsers.md` exists and that `INDEX.md` names no environment page. The page's commands all come from an instance's environment page, which this repository does not have, so none could be run. Ran `python3 ws.py check`: no finding on the page beyond the expected `proof` error for its missing README row.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | The prompt; The report and the fixes, the last paragraph | Blocking. The prompt the person pastes says "Change nothing on my machine until you have given me the report, apart from the one slot step 5 brings up and takes down". The page ends "This how-to writes no file in this repository." The contract's rules table requires a question-log row when the agent had to ask something the workspace should have answered. Procedure endings, which the page ends with, commits that row before the report. Step 5's default asks the person to sign in themselves when the environment page names no test account. Neither the prompt nor the page leaves room for that row, so an agent either breaks the contract's rule or acts against the person's own words. The machine self-check's prompt carries the exception: "except a question-log row for a question you had to ask me". Verified: the texts of the prompt, the paragraph, the contract's rule, procedure endings' "The order" and the machine self-check's prompt. Inferred: that step 5's ask counts as such a question. Marked blocking because following the page contradicts the contract. | fixed: the prompt now says "Change nothing until you have given me the report, except the one slot step 5 brings up and takes down, and a question-log row for a question you had to ask me", as the machine self-check's prompt does; the closing "writes no file" sentence is cut, so the page ends as procedure endings says; the Rules row names the question-log row. |
| 2 | contradiction | Rules, the first row; Steps, step 2 | Not blocking. The first Rules row says "Take no command from anywhere but the instance's environment page". Step 2 supplies its own command, "such as `<tool> --version`", and the list under "The environment page" does not require a version command. Verified: the texts. | fixed: the environment page's list now includes each tool's version command, and step 2 runs it from the page as `<version command>`. |
| 3 | step | The environment page; Steps, steps 3 and 4 | Not blocking. Steps 3 and 4 check ports and certificates "with the command the page gives for this operating system" and "with the page's command". The list of what the environment page names holds the ports and the certificates but no command to check either. Neither step has a default when the page gives none, and the first Rules row forbids any other command. Verified: the list, the steps and the Rules row. | fixed: the list now includes the port and certificate commands, and the page says a step whose command the page lacks is skipped and reported as a gap in the environment page. |
| 4 | step | Steps, step 5 | Not blocking. Step 5 signs in with the local test account and passes when "the sign-in reached the signed-in screen". The page does not say where to sign in, such as the slot's address, which the environment page's list does not name, or how the agent drives a browser there. The page does not link [browsers](../../browsers.md), which says how a session gets a browser. Verified: the list, step 5, and that `docs/browsers.md` exists. | fixed: the list now includes the slot's address, and step 5 opens it in a browser as [browsers](../../browsers.md) says. |
| 5 | enforcement | Steps, the opening paragraph; The prompt; Rules | Not blocking. "The agent runs every step in its own session", and the prompt says "hand nothing to a helper". The Rules table has no row for it, while extend the workspace's step 4 asks for a row for every must and never on a page. Verified: the texts. | fixed: a Rules row "Run every step in this session; hand nothing to a helper", tagged `prose`. |

## Checked with no finding

- trigger: the purpose sentence names the product's local container environment, and the paragraph after the lane-draft line separates this page from the machine self-check and says which runs first.
- placement: the report's verified and inferred marks link the definition of done, and the ending links procedure endings instead of restating it.
- eval-case: the page is marked `proof: unproven` with `prove-by: M11`, a milestone after the `building` list's M3.

## Re-check

A fresh session read the page as it stands on `4190d8d`, uncommitted, beside the contract, procedure endings, the machine self-check, `docs/browsers.md`, `INDEX.md`'s "Topics" and the definition of done. None of the page's commands can be run here, since they come from an instance's environment page. Ran `python3 ws.py check`.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | The prompt now excepts the slot and "a question-log row for a question you had to ask me", in the machine self-check's own words. The "writes no file" sentence is gone, and the page ends with procedure endings, which commits the row before its report. The second Rules row names the row. Verified: the prompt, the last section, the Rules table and the machine self-check's prompt. |
| 2 | upheld | The environment page's list includes each tool's version command, and step 2 runs it from the page as `<version command>`. Verified: the list and step 2. |
| 3 | upheld | The list includes the port command for each operating system and the certificate command. The paragraph under the list says a step whose command the page lacks is skipped and reported as a gap. Verified: the list and that paragraph. |
| 4 | upheld | The list includes the slot's address, and step 5 opens it in a browser as `docs/browsers.md` says. That page exists and says how a session gets its own browser. Verified: the list, step 5 and the linked page. |
| 5 | upheld | The Rules table has "Run every step in this session; hand nothing to a helper.", tagged `prose`. Verified: the Rules table. |

What a fix broke:

- None.

What the first reading missed:

- None.
