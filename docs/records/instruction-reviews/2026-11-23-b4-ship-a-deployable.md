---
kind: record
last-reviewed: 2026-11-23
covers: docs/ship-a-deployable.md
reviewed-at: 1a18d68, with the uncommitted change of the B4 slice session
---

# Instruction review: docs/ship-a-deployable.md

This records the instruction review of slice B4's new devops lane how-to for giving a new deployable its infrastructure and CI. It is for the page's author.

**In short:** 3 findings: 1 contradiction, 2 step; none blocking. Step 6 pushes to a code repository without naming the outward-write list that decides whether an agent may. Step 1 gives no route for a change that passes the size gate. Step 4 credits procedure endings with a stricter rule than it states.

## Scope

In scope: the whole page, which is new and untracked. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/extend-the-workspace.md`, and the pages it links: decision 0006, `docs/size-the-work.md` ("The gate", "The ladder"), procedure endings' "Outward writes" and "The commit", `docs/playbooks/git-host-operations.md`, and `docs/changing-the-machinery.md`. Also read `outward-repos.json` and the header of `parts/outward_write.py`. The page's commands are instance values in angle brackets, so none could be run. Ran `python3 ws.py check`: no finding on the page beyond the expected `proof` error for its missing README row.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | Steps, step 6 | Not blocking. Step 6 pushes the branch to the code repository and opens its pull request. The `outward_write` hook refuses a push or a `gh` write to any repository not in `outward-repos.json`, and an adopted instance starts with that list empty. The page never names the list, says to check it, or says to give the person the line to add, as the import playbook's sweep does. Where an agent pushes, step 6 is refused for every repository not listed. Verified: `outward-repos.json` and the header of `parts/outward_write.py`. Not blocking because the refusal is safe, step 6's output allows "the commits left unpushed", and in a team's workspace a person pushes, as git-host operations says. | fixed: step 6 says an agent pushes only to a repository listed in `outward-repos.json`; if the code repository is not listed, it pushes nothing and gives the person the line to add. A Rules row states it, tagged `outward_write#a push to a repository outside the list is refused`. |
| 2 | step | Steps, step 1 | Not blocking. Step 1 says what to do when the change fails the size gate, but not when it passes. The contract sends a change that passes to fix a bug, which starts from a failing test and has no generator or manual steps. The page neither sends a passing change on to step 2 as a labelled exception, as extend the workspace's step 1 does, nor says it goes to fix a bug. Verified: step 1, the contract's "How work flows" and extend the workspace's step 1. | fixed: step 1 now says a change that passes the gate runs steps 2 to 7 directly, labelled as an exception to the contract's "How work flows", with the reason: no failing test to start from, so step 5's local verification takes its place. |
| 3 | contradiction | Steps, step 4; Rules, the third row | Not blocking. Step 4 says a manual step that writes to a shared system needs the person's yes first, "as procedure endings says", and the third Rules row makes that unconditional. Procedure endings' "Outward writes" says to ask first "unless the request names the write in its own words". The page is stricter than the rule it credits and does not label the difference. Verified: both texts. | fixed: step 4 and the third Rules row now say "unless the request names the write in its own words", matching procedure endings. |

## Checked with no finding

- trigger: the purpose sentence names a new service, job or site, and the page's last paragraph sends a change to this workspace's own CI to changing the machinery.
- enforcement: each must and never on the page has a Rules row tagged `prose`, and no row claims a part or case.
- placement: commit, outward-write and report rules link procedure endings instead of restating them; the pull request links git-host operations.
- eval-case: the page is marked `proof: unproven` with `prove-by: M11`, a milestone after the `building` list's M3.

## Re-check

A fresh session read the page as it stands on `4190d8d`, uncommitted, beside the contract, procedure endings, extend the workspace's step 1, `outward-repos.json` and `parts/outward_write.cases.json`. The page's commands are instance values in angle brackets, so none could be run. Ran `python3 ws.py check`.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | Step 6 says an agent pushes only to a repository in `outward-repos.json`; otherwise it pushes nothing and gives the person the line to add. A Rules row carries the tag `outward_write#a push to a repository outside the list is refused`, a case that exists. Verified: step 6, the Rules table and the cases file. |
| 2 | upheld | Step 1 sends a passing change through steps 2 to 7, labelled as an exception to the contract's "How work flows" with its reason. It has the same shape as extend the workspace's step 1. Verified: both steps. |
| 3 | upheld | Step 4 and the third Rules row now say "unless the request names the write", matching procedure endings' "Outward writes" for any other system. Verified: the three texts. |

What a fix broke:

- None.

What the first reading missed:

- Not blocking. Steps, step 6, and the last Rules row: "Deploying to a shared environment needs the person's yes first, even when CI passes" has no "unless the request names the write". A deploy that people outside the workspace can see is an outward write as procedure endings defines one. So this is stricter than the rule step 4 now follows, and the page does not label the difference. Stricter is safe. Verified: step 6, the Rules row and procedure endings' "Outward writes".

## Known defects

What stays open after the fix rounds the plan allows, each not blocking.

- Not blocking: step 6 asks for a yes before every deploy to a shared environment, stricter than procedure endings' outward-write rule, and does not label the difference. Known defect, for M11.
