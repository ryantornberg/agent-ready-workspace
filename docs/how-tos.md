---
kind: reference
last-reviewed: 2026-11-21
---

# How-to index

Every task a page under `docs/` helps with, where to go for it, and the one thing to remember. For any agent or person starting a task.

**In short:** find your task in the table for the stage you are at, and open the page it names. Playbooks are listed once, in the [playbook catalog](playbooks/README.md), not here.

## How to read the tables

The tables run in the order a piece of work meets them: start, plan, build, finish, then changing the workspace itself. A new page adds its row to the table of its stage, in the same commit as the page.

The Proof column copies each page's front matter, or the proof line under a section's heading. "unproven, M4" means the page names M4 as the milestone that is to prove it; see [decision 0006](decisions/0006-what-proven-means.md). A reference page, a record and a template carry no proof state.

## Starting a task

| Task | Go to | Remember | Proof |
|---|---|---|---|
| Find code or a page, with a name or a topic in hand | [Research ladder](research-ladder.md) | Pick the one lookup that fits what you already know. Never stack lookups. | unproven, M4 |
| Learn what a word means in this workspace | [Glossary](glossary.md) | The team's everyday words for the code are in [INDEX.md's search aliases](../INDEX.md#search-aliases), not the glossary. | reference |
| Decide how much process a change needs | [Size the work](size-the-work.md#the-gate) | Small, easy to reverse, one repository and under a day: all four, or climb the ladder. When you cannot tell, climb. | unproven, M9 |
| Take a feature from request to a finished, reviewed change, once the gate sends it up the ladder | [The feature ladder](size-the-work.md#the-feature-ladder) | When what you find contradicts the spec, update the spec first, with the person's agreement, then the code. | unproven, M9 |
| Decide whether work needs a spec, then write it, gate it and keep it true | [The spec process](size-the-work.md#the-spec-process) | Every success criterion names the command that checks it. No plan is written before the person agrees to the spec. | unproven, M9 |
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

## Finishing

| Task | Go to | Remember | Proof |
|---|---|---|---|
| Know whether the work is done, and write the report | [Definition of done](definition-of-done.md) | A test failed before the fix, and every claim in the report is marked verified or inferred. | reference |
| Commit | [Commits](commits.md) | Stage files by name. A commit that changes a guidance page names its instruction review in a trailer. | reference |
| Record a question you had to ask a person | [Question log](question-log.md) | Log it before you finish, then fix the page where the next person will look. | record |
| Find what a past review or run found | [Records](records/README.md) | One folder per record type. Instruction reviews have their own index there. | reference |
| Close a milestone | [Milestone record template](templates/milestone-record.md) | Numbers come from records and commands, never from memory. | template |

## Changing the workspace

| Task | Go to | Remember | Proof |
|---|---|---|---|
| Add, move or archive a page | [Layout](layout.md) | Front matter names the kind. The page opens with its title, a purpose sentence of 25 words or fewer, then its **In short** line. | reference |
| Add a check or a hook | [Parts](parts.md) | A part is a Python file and its cases. Run `python3 ws.py selftest`, then `python3 ws.py check`. | unproven, M4 |
| Change scripts, parts, hooks or CI | [Changing the machinery](changing-the-machinery.md) | It goes on its own branch and merges only after CI passes on Linux, macOS and Windows. | unproven, M4 |
| Change what an agent tool may read or fetch | [Agent settings](agent-settings.md) | The `agent_settings` check fails when a deny entry or a documentation domain goes missing. | reference |

## Ways to follow a playbook

The [playbook catalog](playbooks/README.md#three-ways-to-follow-a-playbook) lists the three ways: read the page, ask the agent in one line, or a wrapper once they exist.

## Rules

| Rule | Enforced by |
|---|---|
| Every how-to and reference page a reader goes to for a task has a row here, added in the same commit as the page. No check catches a missing row. | `prose` |
| Playbooks are listed only in the playbook catalog, never repeated here. | `prose` |
