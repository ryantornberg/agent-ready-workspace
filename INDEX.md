---
last-reviewed: 2026-11-24
---

# Index

Where each topic lives, and what the code calls the things people talk about. Agents read this before they search.

## Topics

### Rules, sizing and how work flows

| Topic | Page |
|---|---|
| The rules every agent follows | [AGENTS.md](AGENTS.md) |
| A one-line request and what it expands to; the defaults nobody has to say; a prompt for a new session | [Request map](docs/request-map.md), [the fresh-session prompt template](docs/templates/fresh-session-prompt.md) |
| Where to start for a role: development, QA, product, automation or DevOps; lane drafts | [Reading paths by role](docs/reading-paths.md) |
| A walk-through of the workspace with no agent; your first agent task | [Get oriented](docs/tutorials/get-oriented.md), [your first agent task](docs/tutorials/first-agent-task.md) |
| When work counts as done | [Definition of done](docs/definition-of-done.md) |
| How a procedure ends; commit, push, the question-log entry and the report | [Procedure endings](docs/procedure-endings.md) |
| How much process a change needs | [Size the work](docs/size-the-work.md) |
| Building a feature; writing a spec; spec approval; when a spec changes | [The feature ladder](docs/size-the-work.md#the-feature-ladder), [decision 0016](docs/decisions/0016-a-spec-lives-in-its-plan.md) |
| Which model and effort a task gets; delegating; tiers | [Orchestration](docs/orchestration.md), [decision 0014](docs/decisions/0014-three-tiers-bound-in-one-place.md) |
| Writing a plan for larger work; a plan's word budgets | [Hand-off plan template](docs/templates/hand-off-plan.md) |
| A large piece of work with several plans; a project hub; an epic folder | [Decision 0017](docs/decisions/0017-one-folder-per-large-piece-of-work.md), [the epic folder template](docs/templates/epic-folder.md), [the project hub template](docs/templates/hub.md) |
| The milestones being built now, and their plans | `building` in [workspace.json](workspace.json); the plans are in [docs/plans/](docs/plans/) |
| What a finished milestone records | [Milestone record template](docs/templates/milestone-record.md), [milestone records](docs/milestones/) |
| Questions someone had to ask a person | [Question log](docs/question-log.md) |

### Playbooks and procedures

| Topic | Page |
|---|---|
| Which playbook to follow; every playbook and its proof state | [The playbook catalog](docs/playbooks/README.md) |
| Where to go for a task; how-tos and reference pages by task | [The how-to index](docs/how-tos.md) |
| Fixing a small bug | [Fix a bug](docs/playbooks/fix-a-bug.md) |
| Test first; a regression test; red-green proof | [Test first](docs/playbooks/test-first.md) |
| Debugging; finding a cause; a repro; a flaky failure | [Debugging](docs/playbooks/debugging.md) |
| A prototype; a spike; trying screen variants | [The throwaway prototype](docs/playbooks/throwaway-prototype.md) |
| Restructuring code without changing behavior; replacing a repeated value everywhere | [Safe refactor](docs/safe-refactor.md) |
| Where to look first; which lookup to use; writing down a finding | [The research ladder](docs/research-ladder.md), [decision 0012](docs/decisions/0012-one-lookup-by-what-you-know.md) |
| Interview me on this; settling design questions before a plan | [The decision interview](docs/playbooks/decision-interview.md) |
| Red team; adversarial review; a critic attacks a plan | [Red team review](docs/playbooks/red-team-review.md) |
| Reviewing a branch or pull request; review dimensions | [The review orchestrator](docs/playbooks/review-orchestrator.md) |
| What the code review checks; answering a review comment | [Code review](docs/code-review.md) |
| Checking out a pull request to review it | [Review in a worktree](docs/review-in-a-worktree.md) |
| Does a change keep what the system decided; a symptom fix; a simpler alternative | [Architecture review](docs/playbooks/architecture-review.md) |
| Is there a helper for this already; duplicated logic; design debt | [The reuse checklist](docs/playbooks/reuse-checklist.md) |
| What a change touches; callers; docs likely stale | [Impact analysis](docs/playbooks/impact-analysis.md) |
| Why a review missed a defect; defect escape analysis | [Defect escape analysis](docs/playbooks/escape-analysis.md) |
| Walk me through the review comments | [The feedback walk-through](docs/playbooks/feedback-walkthrough.md) |
| Hand off; low on context; resume a session | [Handoff](docs/playbooks/handoff.md) |
| Resume another session's work; a handoff note shown at session start; mark or clear a note with `ws.py handoff` | [Handoff](docs/playbooks/handoff.md#the-marker-and-the-loader) |
| A ticket; a work item; a sub-task; the security review after a merge | [Tracker operations](docs/playbooks/tracker-operations.md) |
| A pull request; a draft; a CI failure; retargeting | [Git-host operations](docs/playbooks/git-host-operations.md) |
| Federated search; searching outside the workspace; a tracker, a wiki, mail or chat | [Federated search](docs/playbooks/search-every-source.md) |
| A docs audit; drift between pages | [The docs audit](docs/playbooks/docs-audit.md) |
| A prompt retrospective; what a session's prompt cost | [The prompt retrospective](docs/playbooks/prompt-retrospective.md) |
| Review a guidance page; a commit refused for a missing Instructions-review trailer | [The instruction review](docs/playbooks/instruction-review.md) |
| QA: a regression run; triaging its failures; a verification list; a test plan; regression candidates | [Regression run](docs/playbooks/regression-run.md), [regression triage](docs/playbooks/regression-triage.md), [QA verification list](docs/playbooks/qa-verification-list.md), [the templates index](docs/templates/README.md#lane-templates) |
| Product: grooming bugs; a bug triage meeting; triage labels; an effort estimate; a standup report | [Bug grooming](docs/playbooks/bug-grooming.md), [bug triage meeting](docs/playbooks/bug-triage-meeting.md), [triage labels](docs/triage-labels.md), [effort estimate](docs/playbooks/effort-estimate.md), [standup report](docs/playbooks/standup-report.md) |
| Development: walking a feature through its layers; a fix that may belong in a shelved predecessor; pages for a product reader | [Feature layer walk](docs/playbooks/feature-layer-walk.md), [checking a shelved predecessor](docs/predecessor-check.md), [pages for a product reader](docs/product-reader-pages.md) |
| DevOps: importing a repository; the environment self-check; shipping a new deployable | [Import a repository](docs/playbooks/import-a-repository.md), [environment self-check](docs/environment-self-check.md), [ship a new deployable](docs/ship-a-deployable.md) |
| Automation: a saved workflow | [Saved workflows](docs/saved-workflows.md) |

### Pages, templates and records

| Topic | Page |
|---|---|
| Where a page goes; page kinds and their front matter; a commit refused by `page_kinds` | [Layout](docs/layout.md) |
| Guidance kinds: playbook, how-to, tutorial, reference; one term per concept | [Decision 0010](docs/decisions/0010-three-kinds-of-guidance-plus-reference.md) |
| A tutorial's runnable blocks; a push refused because a tutorial fails | [Layout](docs/layout.md#tutorials) |
| Amend an accepted decision record; what a frozen page may change | [Layout](docs/layout.md#the-opening) |
| Adding a page, a playbook, a decision record or a rule page; a small fix to a page | [Extend the workspace](docs/extend-the-workspace.md) |
| Why pages go straight to main | [Decision 0011](docs/decisions/0011-pages-go-straight-to-main.md) |
| How to write a page; authoring conventions; who a page is for, its word budget and its fixed headings | [The style guide](docs/authoring.md), [the reader standard](docs/reader-standard.md) |
| What a word means here | [Glossary](docs/glossary.md) |
| Proven and unproven pages; `proof`, `prove-by`, `proven-by` | [Decision 0006](docs/decisions/0006-what-proven-means.md) |
| Templates; which template for a plan, spec, bug report, pull request or record; the defect register; the lessons log | [The templates index](docs/templates/README.md) |
| Write a bug report; rewrite a stale bug ticket; the bug ticket standard | [The bug report template](docs/templates/bug-ticket.md) |
| Write a pull request description; what a pull request must say; the bookkeeping after a merge | [The pull request template](docs/templates/pull-request.md) |
| A fix record; where a fix's report goes | [The fix record template](docs/templates/fix-record.md) |
| An investigation, an audit report, a postmortem or a baseline; a standalone spec | [The spec template](docs/templates/spec.md) |
| Decision records; write, amend or supersede a decision; why a rule exists | [The decision record template](docs/templates/decision-record.md) |
| Where the ported pages disagreed; departures from the ported pages | [Decision 0020](docs/decisions/0020-where-the-sources-disagreed.md) |
| What the workspace holds and refuses; what success means | Decisions [0008](docs/decisions/0008-success-is-a-teammate-who-does-not-ask.md) and [0009](docs/decisions/0009-hold-what-nobody-can-derive.md) |
| Retired pages; the archive; what search still finds | [Decision 0015](docs/decisions/0015-retired-pages-move-to-an-archive.md) |

### The workspace and its machinery

| Topic | Page |
|---|---|
| Adopting the workspace for a team; what transfers; where per-repository docs live | [Adopt the workspace](docs/adopt-the-workspace.md) |
| Make an instance of the workspace; a file refused by `kit_drift`; keep a synced file; upgrade an instance; `kit.lock.json` | [Decision 0007](docs/decisions/0007-the-kit.md), [the kit](docs/parts.md#the-kit) |
| Upkeep; maintenance duties; who owns them | [Maintain the workspace](docs/maintain-the-workspace.md) |
| Machine check; setup check; hooks not firing | [The machine self-check](docs/machine-self-check.md) |
| Which rules a check enforces | `python3 ws.py rules` |
| A finding or refusal named by its part, such as `[review_trailer]`; what each check and hook does | [The parts here](docs/parts.md#the-parts-here) |
| Adding a check or a hook | [Parts](docs/parts.md) |
| Changing scripts, parts, hooks or CI | [Changing the machinery](docs/changing-the-machinery.md) |
| Merge a pull request; a squash, rebase or `gh pr merge --admin` merge refused | [Changing the machinery](docs/changing-the-machinery.md#the-path-for-a-machinery-change), [decision 0005](docs/decisions/0005-concurrent-sessions-and-the-edit-ledger.md) |
| A push to main refused; a force push or deletion of main refused; a push refused because its branch is a variable; a worktree's push of the main copy's branch refused | [Changing the machinery](docs/changing-the-machinery.md#the-path-for-a-machinery-change), [decision 0004](docs/decisions/0004-the-hook-contract.md), [decision 0005](docs/decisions/0005-concurrent-sessions-and-the-edit-ledger.md) |
| A command refused because it cannot be judged, such as a program word that is a variable | [Changing the machinery](docs/changing-the-machinery.md#the-path-for-a-machinery-change) |
| Two agent sessions at once; an edit or a push refused because another session holds the main copy; a stop refused; the lease; when to use a worktree | [Decision 0005](docs/decisions/0005-concurrent-sessions-and-the-edit-ledger.md) |
| A hard reset, stash drop or rebase refused while another session works here; which working copy a git command acts on | [Decision 0005](docs/decisions/0005-concurrent-sessions-and-the-edit-ledger.md), [decision 0004](docs/decisions/0004-the-hook-contract.md#decision) |
| What a hook may read; a path inside a worktree; writing a session hook; a write to a git folder or a git config file refused; a git config key an agent may not set; a git alias judged as what it runs | [Decision 0004](docs/decisions/0004-the-hook-contract.md) |
| A write to another repository refused; an approval or `gh api graphql` refused; add a repository to the list agents may write to | [Decision 0004](docs/decisions/0004-the-hook-contract.md), [changing the machinery](docs/changing-the-machinery.md#what-counts-as-machinery) |
| Notices when a session starts: stale pages, a pin behind its upstream, the main copy not brought up to date, main's CI failing, a pending handoff note | [The parts here](docs/parts.md#the-parts-here) |
| A reminder after an edit of the other paths the same change touches; a stop refused because the check or the fast tests fail | [The parts here](docs/parts.md#the-parts-here), [decision 0005](docs/decisions/0005-concurrent-sessions-and-the-edit-ledger.md) |
| Rules shown when you edit a file in one folder; adding such a rule | [Rule pages](docs/rules/), such as [the live order service's](docs/rules/orders-api.md) |
| A commit refused for a line-number citation or a missing **In short** line | [The parts here](docs/parts.md#the-parts-here) |
| Commit subject format; a token or key in a commit; the history scan | [Commits](docs/commits.md) |
| A commit refused because no edit tool wrote a file; why staging is checked at the commit | [Decision 0002](docs/decisions/0002-hooks-remind-the-commit-enforces.md), [the edit ledger](docs/parts.md#the-edit-ledger) |
| What an agent may read or fetch; secrets files; a worktree missing local settings; Codex's permissions profile | [Agent settings](docs/agent-settings.md) |
| A token a program needs; `ws.py with-secrets`; a shell read of `.env` or a key refused; an environment dump refused | [Agent settings](docs/agent-settings.md#secrets-in-the-shell) |
| A guard that may turn off when an environment variable is unset; the deny list's intended opt-out; what a killed commit check leaves | [The README's checks table](README.md#what-is-checked-and-by-what) |
| Which Python the hooks and CI run; a hook refused because Python is missing or too old | [The launcher](docs/parts.md#the-launcher) |
| A check that fails on old findings an adopting team cannot fix yet; tolerated findings | [Baselines](docs/parts.md#baselines) |
| How long a hook takes; a hook called for real, through the launcher, in a scratch repository | [The hook case runner](docs/parts.md#the-hook-case-runner) |
| A manifest refused for its version; where the engine's code lives | [Decision 0003](docs/decisions/0003-the-engine-in-one-folder.md), [the manifest](docs/parts.md#the-manifest) |
| Check out the code repositories after a fresh clone; a pinned repository is missing or unreachable | [Pinned repositories](docs/parts.md#pinned-repositories) |
| Why code repositories are pinned, not copied; where a person's agent memory, notes and settings belong | [Decision 0001](docs/decisions/0001-pin-code-repositories.md) |
| Whether the README's setup still works; a nightly fresh clone; a link that cannot resolve on purpose | [The cold-clone job](docs/parts.md#the-cold-clone-job) |
| Unattended runs; moving a pin after a run | [Decision 0018](docs/decisions/0018-unattended-runs-write-only-to-a-branch.md) |
| Branching for product repositories; hotfixes; release branches | [Decision 0019](docs/decisions/0019-every-fix-lands-on-trunk-first.md) |
| A knowledge graph of the code | [Decision 0013](docs/decisions/0013-knowledge-graph-output-is-scratch.md) |
| Opening a browser; "browser is already in use"; logins gone after a session | [Browsers](docs/browsers.md) |
| Testing a playbook | [Evals](evals/README.md) |
| Wrappers; skills; the plugin; why a wrapper fires or stays quiet; selection cases | [The playbook catalog's three ways](docs/playbooks/README.md#three-ways-to-follow-a-playbook), [the wrappers' selection cases](evals/README.md) |
| The sample code | [src](src/README.md) |

## Search aliases

People and code use different words for the same thing. A search for the everyday word finds nothing, so map it here. The `aliases` check fails when a name in the right-hand column is no longer defined under `src/`.

| You say | The code says |
|---|---|
| the nightly job | `ReconciliationWorker` |
| a hold | `AccountFreeze` |
| the big report | `QuarterlyExport` |

## Cross-cutting chains

For each kind of change, every path it touches. The `chains` check fails on a path that does not exist.

| Change | Paths it touches |
|---|---|
| Add or change a part | `parts/`, `workspace.json`, `docs/parts.md`, `README.md`, `tests/test_cases_bite.py` |
| Change a playbook marked proven, the contract or the index | `docs/playbooks/`, `AGENTS.md`, `INDEX.md`, `evals/cases/`, `evals/runs/`, `evals/README.md`, `README.md` |
| Change the eval harness or a grader | `evals/run.py`, `evals/grade.py`, `evals/proofkeys.py`, `evals/pool.py`, `evals/arms.json`, `evals/one-time.json`, `evals/cases/`, `evals/acceptance/`, `evals/runs/`, `evals/README.md`, `docs/changing-the-machinery.md` |
| Mark a page proven or unproven | `docs/playbooks/`, `docs/adopt-the-workspace.md`, `docs/browsers.md`, `docs/changing-the-machinery.md`, `docs/environment-self-check.md`, `docs/extend-the-workspace.md`, `docs/machine-self-check.md`, `docs/maintain-the-workspace.md`, `docs/orchestration.md`, `docs/parts.md`, `docs/predecessor-check.md`, `docs/research-ladder.md`, `docs/review-in-a-worktree.md`, `docs/safe-refactor.md`, `docs/saved-workflows.md`, `docs/ship-a-deployable.md`, `docs/size-the-work.md`, `evals/cases/`, `evals/runs/`, `README.md`, `docs/decisions/0006-what-proven-means.md`, `docs/plans/` |
| Add a page | `docs/layout.md`, `INDEX.md`, `README.md` |
| Add a rule page | `docs/rules/`, `INDEX.md` |
| Change the engine or its version | `wslib/`, `workspace.json`, `CHANGELOG.md`, `docs/decisions/0003-the-engine-in-one-folder.md` |
| Change what counts as machinery | `workspace.json`, `docs/changing-the-machinery.md`, `tests/test_core.py` |
| Change what the kit ships | `kit/`, `wslib/kit.py`, `tests/test_kit.py`, `docs/decisions/0007-the-kit.md`, `README.md` |
| Start or sign off a milestone | `workspace.json`, `docs/plans/`, `docs/milestones/`, `CHANGELOG.md`, `EVIDENCE.md` |
