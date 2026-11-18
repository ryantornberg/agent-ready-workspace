---
kind: reference
last-reviewed: 2026-11-18
---

# Glossary

The words this workspace uses in its own sense. For anyone reading its pages for the first time.

**In short:** the team's words for the code are in the [index's search aliases](../INDEX.md#search-aliases). This page holds the workspace's own words.

| Word | Means |
|---|---|
| Anchor | The commit-pinned eval record, `<sha>:evals/runs/<case>/record.json`, that a proven playbook's guided arm is compared with from then on. |
| Arm | One way an eval case is run: guided (the workspace's pages), two-line (two lines of instruction) or bare (the code alone). |
| Building | The milestones being built now, listed under `building` in `workspace.json`. |
| Case | Test data a part runs every time it loads; or an eval case, a request an agent is given in each arm. |
| Check | A part that reads a snapshot of files and reports findings, at the commit and in CI. |
| Contract | `AGENTS.md`: the rules every agent reads first. |
| Hook | A part that decides on one agent tool call before it runs. It refuses, or reminds. |
| Kind | What a page is: playbook, how-to, tutorial, reference, template, record, decision, plan or milestone. See [layout](layout.md). |
| Lease | The claim a live agent session holds on the main working copy while it edits there. See [decision 0005](decisions/0005-concurrent-sessions-and-the-edit-ledger.md). |
| Ledger | The list of files an agent's edit tools wrote, which the commit check compares with what is staged. |
| Machinery | Scripts, parts, hooks and CI. They change on a branch that passes CI on three systems. See [changing the machinery](changing-the-machinery.md). |
| Manifest | `workspace.json`: the parts in use, the tier binding and the milestones being built. |
| Part | One check or hook: a Python file and its cases. See [parts](parts.md). |
| Proven | A playbook or how-to with a real run on record and an eval that beats both the bare model and two lines. See [decision 0006](decisions/0006-what-proven-means.md). |
| Rule page | A page under `docs/rules/` shown to the agent when it edits a file its `applies-to` matches. |
| Tier | Driver, worker or mechanical: the model and effort a task runs at. See [orchestration](orchestration.md). |
| Unproven | A playbook or how-to shipped without that proof yet. It names the milestone that is to prove it in `prove-by`. |
| Worktree | A second working copy of the repository, under `.claude/worktrees/`, where a session works apart from others. |
