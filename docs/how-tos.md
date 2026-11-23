---
kind: reference
last-reviewed: 2026-11-23
---

# How-to index

Every task a page under `docs/` helps with, where to go for it, and the one thing to remember. For any agent or person starting a task.

**In short:** find your task in the table for the stage you are at, and open the page it names. Playbooks are listed once, in the [playbook catalog](playbooks/README.md), not here.

## How to read the tables

The tables run in the order a piece of work meets them: start, plan, build, finish, then changing the workspace itself. A new page adds its row to the table of its stage, in the same commit as the page. A lane page is the exception: its row goes in [lane drafts](#lane-drafts).

The Proof column copies each page's front matter, or the proof line under a section's heading. "unproven, M4" means the page names M4 as the milestone that is to prove it; see [decision 0006](decisions/0006-what-proven-means.md). A reference page, a tutorial, a record and a template carry no proof state.

## Starting a task

| Task | Go to | Remember | Proof |
|---|---|---|---|
| New here: walk through the workspace with no agent, then run a first task with one | [Get oriented](tutorials/get-oriented.md), then [your first agent task](tutorials/first-agent-task.md) | Run them in a clone no other agent session works in. Every block marked as yours runs as written; CI runs those on three systems. | tutorial |
| Find code or a page, with a name or a topic in hand | [Research ladder](research-ladder.md) | Pick the one lookup that fits what you already know. Never stack lookups. | unproven, M4 |
| Learn what a word means in this workspace | [Glossary](glossary.md) | The team's everyday words for the code are in [INDEX.md's search aliases](../INDEX.md#search-aliases), not the glossary. | reference |
| Decide how much process a change needs | [Size the work](size-the-work.md#the-gate) | Small, easy to reverse, one repository and under a day: all four, or climb the ladder. When you cannot tell, climb. | unproven, M9 |
| Take a feature from request to a finished, reviewed change, once the gate sends it up the ladder | [The feature ladder](size-the-work.md#the-feature-ladder) | When what you find contradicts the spec, update the spec first, with the person's agreement, then the code. | unproven, M9 |
| Decide whether work needs a spec, then write it, gate it and keep it true | [The spec process](size-the-work.md#the-spec-process) | Every success criterion names the command that checks it. No plan is written before the person agrees to the spec. | unproven, M9 |
| Check that your machine runs the workspace's hooks, checks and tools: after setup, after a machine change, or when a guard seems not to run | [Machine self-check](machine-self-check.md) | Paste its prompt. Nothing changes until the report, then each fix only on your yes. | unproven, M5 |
| Find the pages to read first for your role: development, QA, product, automation or DevOps | [Reading paths by role](reading-paths.md) | Everyone reads the same six pages first; then each role has its own short path. | reference |
| Follow a procedure, such as fixing a bug, debugging or a review | [Playbook catalog](playbooks/README.md) | The playbook page is canonical; follow its steps, not a summary of them. | reference; each playbook's state is in its row there |

## Planning

| Task | Go to | Remember | Proof |
|---|---|---|---|
| Write a plan for work that climbs the ladder | [Hand-off plan template](templates/hand-off-plan.md) | Write the goal, non-goals and success criteria first, and get the person's agreement, as [the spec process](size-the-work.md#the-spec-process) says. Then a fresh session red-teams the plan, and a person approves it before any slice is built. | template |
| Choose the model and effort for a task | [Orchestration](orchestration.md) | Every handoff names its tier. Stakes, such as a change to a gate or the contract, raise it to driver. | unproven, M4 |
| Hand a piece of work to a helper session | [Delegating](orchestration.md#delegating) | Delegate when the reading is wide and the answer short. Checking your own work stays with you. | unproven, M4 |

## Building

| Task | Go to | Remember | Proof |
|---|---|---|---|
| Change the shape of code without changing what it does | [Safe refactor](safe-refactor.md) | The characterization test's assertions never change. If one would have to, behavior changed: stop and report. | unproven, M4 |
| Open a browser in an agent session | [Browsers](browsers.md) | Each session gets its own isolated browser, so logins do not survive the session. | unproven, M6 |
| Review a pull request without touching the main working copy | [Review in a worktree](review-in-a-worktree.md) | Start the session in the main working copy, never inside the worktree; remove it without `--force`. | unproven, M6 |

## Finishing

| Task | Go to | Remember | Proof |
|---|---|---|---|
| Know whether the work is done, and write the report | [Definition of done](definition-of-done.md) | A test failed before the fix, and every claim in the report is marked verified or inferred. | reference |
| End any procedure: outward writes, the commit, the question-log entry, the push and the report | [Procedure endings](procedure-endings.md) | Every step's refusal still ends in the report. A page links these rules; it does not restate them. | reference |
| Understand what an agent's code review checks and how to act on its findings | [Code review](code-review.md) | The reviewer sets obvious fix or decision; the author may raise it, never lower it. Nothing posts without your yes. | reference |
| Commit | [Commits](commits.md) | The subject's format and the trailer's form are here; how a procedure ends, staging included, is in [procedure endings](procedure-endings.md#the-commit). | reference |
| Record a question you had to ask a person | [Question log](question-log.md) | Fix the page where the next person will look. Adding and committing the row is in [procedure endings](procedure-endings.md#the-question-log-entry). | record |
| Find what a past review or run found | [Records](records/README.md) | One folder per record type. Instruction reviews have their own index there. | reference |
| Close a milestone | [Milestone record template](templates/milestone-record.md) | Numbers come from records and commands, never from memory. | template |

## Changing the workspace

| Task | Go to | Remember | Proof |
|---|---|---|---|
| Look up a page's kind, its front matter and the order it opens in; move or archive a page. To add a page, use extend the workspace below. | [Layout](layout.md) | Front matter names the kind. The page opens with its title, a purpose sentence of 25 words or fewer, then its **In short** line. | reference |
| Write or edit the words on a page: sentences, names, links and citations | [Style guide](authoring.md) | State each rule once, on the page that owns it, and link to it. Pages written before 2026-11-22 are not retrofitted. | reference |
| Write the bug report, pull request or project hub template, or a copy of one; credit a source under "References" | [Reader standard](reader-standard.md) | Name the reader, keep the top layer within its budget, use fixed headings and give one worked example. | reference |
| Add a check or a hook | [Parts](parts.md) | A part is a Python file and its cases. Run `python3 ws.py selftest`, then `python3 ws.py check`. | unproven, M4 |
| Change scripts, parts, hooks or CI | [Changing the machinery](changing-the-machinery.md) | It goes on its own branch and merges only after CI passes on Linux, macOS and Windows. | unproven, M4 |
| Change what an agent tool may read or fetch | [Agent settings](agent-settings.md) | The `agent_settings` check fails when a deny entry or a documentation domain goes missing. | reference |
| Add a playbook, how-to, reference page, decision record or rule page, with its routing rows; or make a small change to pages only, such as fixing a page a review or an audit found wrong | [Extend the workspace](extend-the-workspace.md) | One owner per topic: a procedure that overlaps a page already here goes into it as a section. A check or hook is on [parts](parts.md). | unproven, M5 |
| Set the workspace up for your own team | [Adopt the workspace](adopt-the-workspace.md) | Start here, not at the README: adopt runs the README's setup steps inside a plan a person approves, and says what transfers and when the adoption is done. | unproven, M5 |
| Find which upkeep duty an event or a closing milestone sets off, and who owns it | [Maintain the workspace](maintain-the-workspace.md) | The checks catch some drift on their own; the rest is a duty with an owner and a cadence. | unproven, M5 |

## Lane drafts

How-tos and reference pages that serve one lane of work, named in each page's `lane` key. A lane how-to is a draft that has not run on real work yet; the milestone in its Proof column runs it first. A lane reference page carries no proof state, and its Proof column says `reference`. [Reading paths by role](reading-paths.md) lists each lane's pages, playbooks and templates in reading order. By exception to the stage rule above, a new lane how-to or reference page adds its row here, and a line in its role's path on reading paths, in the same commit.

| Lane | Task | Go to | Remember | Proof |
|---|---|---|---|---|
| Automation | Write or run a script that dispatches helper sessions in a fixed shape | [Saved workflows](saved-workflows.md) | Each helper's prompt names its tier; the script names no model. The script is machinery wherever it lives. | unproven, M10 |
| Product | Label a bug so a triage meeting can sort it without reading it | [Bug triage labels](triage-labels.md) | One label from each of five categories, plus an area. Labels describe the fault; triage decides what to do. | reference |
| Product | Check a shelved predecessor for a major security bug's fault | [Checking a shelved predecessor](predecessor-check.md) | Only for a major security bug; the result is one origin line. Never edit the predecessor. | unproven, M9 |
| Product | Write a page whose reader is a product manager or another non-developer | [Pages for a product reader](product-reader-pages.md) | Colour says what it means in plain words. Never ask the reader to fill in a column on every row. | reference |
| DevOps | Check that the product's local container environment runs on your machine | [Environment self-check](environment-self-check.md) | Paste its prompt. It reports first, and fixes only on your yes. | unproven, M11 |
| DevOps | Give a new service, job or site its infrastructure and CI | [Ship a new deployable](ship-a-deployable.md) | Do the two steps no generator covers, and verify locally before you push. | unproven, M11 |

## Ways to follow a playbook

The [playbook catalog](playbooks/README.md#three-ways-to-follow-a-playbook) lists the three ways: read the page, ask the agent in one line, or a wrapper once they exist.

## Rules

| Rule | Enforced by |
|---|---|
| Every how-to and reference page a reader goes to for a task has a row here, added in the same commit as the page. No check catches a missing row. | `prose` |
| Playbooks are listed only in the playbook catalog, never repeated here. | `prose` |
