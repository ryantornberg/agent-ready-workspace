---
kind: reference
last-reviewed: 2026-11-21
---

# Glossary

The words this workspace uses in its own sense. For anyone reading its pages for the first time.

**In short:** the team's words for the code are in the [index's search aliases](../INDEX.md#search-aliases). This page holds the workspace's own words.

| Word | Means |
|---|---|
| Anchor | The commit-pinned eval record, `<sha>:evals/runs/<case>/record.json`, that a proven playbook's guided arm is compared with from then on. |
| Arm | One way an eval case is run: guided (the workspace's pages), two-line (two lines of instruction) or bare (the code alone). A one-time arm, such as `routed` in `evals/one-time.json`, is recorded once in a record the gate never reads. |
| Building | The milestones being built now, listed under `building` in `workspace.json`. |
| Case | Test data a part runs every time it loads; or an eval case, a request an agent is given in each arm. |
| Check | A part that reads a snapshot of files and reports findings. By default it runs at the commit and in CI; a check may name other phases, such as the push or the nightly run. |
| Contract | `AGENTS.md`: the rules every agent reads first. |
| Critic | A fresh session that reviews an artifact, such as a plan, without the author's reasoning. See [fresh context for critics](orchestration.md#fresh-context-for-critics) and [adversarial review](playbooks/adversarial-review.md). |
| Dimension | One side of a change that one fresh reviewer judges, such as security or architecture. The [review orchestrator](playbooks/review-orchestrator.md) dispatches one session per dimension, except the agent-instructions dimension, which the instruction review at each commit already covers. |
| Escape | A defect that passed a review which covered its code. [Escape analysis](playbooks/escape-analysis.md) finds why. |
| Handoff note | The note a session writes when it must stop mid-task, so a later session can carry on. See [handoff](playbooks/handoff.md). Not a delegated task, and not a hand-off plan. |
| Hook | A part that runs on one agent tool event. Before a tool call it refuses or reminds; when a session starts or ends it only reminds. A git hook, such as the commit-msg or pre-push hook, is a different thing: a script in `.githooks/` that runs the checks. |
| Instance | A copy of this workspace that a team adopts and runs on its own code. See [adopt the workspace](adopt-the-workspace.md). |
| Invariant | A numbered decision the system already rests on, which every [architecture review](playbooks/architecture-review.md) checks a diff against. |
| Kind | What a page is: playbook, how-to, tutorial, reference, template, record, decision, plan or milestone. See [layout](layout.md). |
| Kit | The packaged workspace an instance is made from. Its manifest classes each file as synced, seeded once or never synced. Planned in slice C8 of M3; see [adopt the workspace](adopt-the-workspace.md). |
| Lease | The claim a live agent session holds on the main working copy while it edits there. See [decision 0005](decisions/0005-concurrent-sessions-and-the-edit-ledger.md). |
| Ledger | The list of files an agent's edit tools wrote, which the commit check compares with what is staged. |
| Machinery | Scripts, parts, hooks and CI. They change on a branch that passes CI on three systems. See [changing the machinery](changing-the-machinery.md). |
| Manifest | `workspace.json`: the parts in use, the tier binding and the milestones being built. |
| Outside source | Anywhere an answer may sit that is not this repository: a tracker, a wiki, mail, chat or a code host's discussions. See [search every source](playbooks/search-every-source.md). |
| Part | One check or hook: a Python file and its cases. See [parts](parts.md). |
| Proven | A playbook or how-to with a real run on record and an eval that beats both the bare model and two lines. See [decision 0006](decisions/0006-what-proven-means.md). |
| Rule page | A page under `docs/rules/` shown to the agent when it edits a file its `applies-to` matches. |
| Spec | What a piece of work will make true: the goal, non-goals and success criteria of its hand-off plan, which a person agrees to before the rest of the plan is written. See [the spec process](size-the-work.md#the-spec-process). |
| Spine | The steps of a tracker or git-host procedure that hold on any tracker or host. Each team writes its own trap table beside it, planned for M8. See [tracker operations](playbooks/tracker-operations.md) and [git-host operations](playbooks/git-host-operations.md). |
| Tier | Driver, worker or mechanical: the model and effort a task runs at. See [orchestration](orchestration.md). |
| Unproven | A playbook or how-to shipped without that proof yet. It names the milestone that is to prove it in `prove-by`. |
| Work item | A ticket on a tracker, or one of its sub-tasks. See [tracker operations](playbooks/tracker-operations.md). |
| Wrapper | A skill an agent tool loads: its description says when it fires, and its body points at a procedure page, a playbook or a how-to, which stays canonical. Slice B6 of M3 adds them; see the [playbook catalog](playbooks/README.md). |
| Worktree | A second working copy of the repository, under `.claude/worktrees/`, where a session works apart from others. |
