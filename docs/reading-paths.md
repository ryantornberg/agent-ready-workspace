---
kind: reference
last-reviewed: 2026-11-23
---

# Reading paths by role

The pages to read first, in order, for each of five roles: development, QA, product, automation and DevOps. For a person or agent new to one role here.

**In short:** everyone reads the same six pages first. Then each role has its own short path, in the order its work meets the pages, core and lane pages together. A lane page is a draft until the milestone it names runs it on real work. Two topics a role needs are not written yet: the product path and the DevOps path each name the milestone that builds theirs.

## Lanes

A lane is one kind of work the workspace guides: development, QA, product, automation or DevOps. A page that serves one lane names it in its `lane` front-matter key, as [layout](layout.md#page-kinds) says. Most lane pages are drafts: a lane playbook or how-to is marked unproven, and names the milestone that is to prove it, as [decision 0006](decisions/0006-what-proven-means.md) says. A lane template is first used in the milestone its row names in [the templates index](templates/README.md#lane-templates).

A lane draft gets no wrapper yet, as the [playbook catalog's rules](playbooks/README.md#rules) say. Reach it through this page, the [playbook catalog](playbooks/README.md#lane-drafts), the [how-to index](how-tos.md#lane-drafts) and the [templates index](templates/README.md#lane-templates).

## Everyone first

1. [Get oriented](tutorials/get-oriented.md): a walk-through of the workspace with no agent.
2. [The contract](../AGENTS.md): the rules every agent reads before it works here.
3. [INDEX.md](../INDEX.md): every topic, and the everyday words for the names the code uses.
4. [The research ladder](research-ladder.md): which one lookup to use for what you already know.
5. [Size the work](size-the-work.md): how much process a change needs.
6. [Procedure endings](procedure-endings.md): how every procedure commits, pushes, logs a question and reports.

## Development

1. [Fix a bug](playbooks/fix-a-bug.md): the path for a small change, and the only proven playbook.
2. [Debugging](playbooks/debugging.md), when you cannot yet say why something fails.
3. [Test first](playbooks/test-first.md), for behavior on a route already chosen.
4. [Feature layer walk](playbooks/feature-layer-walk.md): every layer a feature of a known type touches. A development lane draft, for M9.
5. [The reuse checklist](playbooks/reuse-checklist.md) and [impact analysis](playbooks/impact-analysis.md), before new logic is written.
6. [The review orchestrator](playbooks/review-orchestrator.md), for a review of a branch or pull request.
7. [The definition of done](definition-of-done.md): when the work is done, and the report's shape.

## QA

1. [Bug report template](templates/bug-ticket.md): the shape of a bug ticket, for any bug QA files outside a QA sub-task.
2. [QA verification list](playbooks/qa-verification-list.md): what goes in a document QA reads. A QA lane draft, for M6.
3. [QA test plan template](templates/qa-test-plan.md): the document handed to QA for a release or a change.
4. [Regression case template](templates/regression-case.md): one case of a regression suite.
5. [Regression run](playbooks/regression-run.md): run the suite and write its report set. A QA lane draft, for M10.
6. [Regression run report template](templates/regression-report.md): the files a run writes.
7. [Regression triage](playbooks/regression-triage.md): sort a run's failures and file the ones the person picks. A QA lane draft, for M10.
8. [Regression candidates ledger template](templates/regression-candidates.md): which fixed bugs earn a regression case.

## Product

1. [The feature ladder](size-the-work.md#the-feature-ladder) and [the spec process](size-the-work.md#the-spec-process): how a feature goes from request to a reviewed change.
2. [The decision interview](playbooks/decision-interview.md), to settle design questions before a plan.
3. [Red team review](playbooks/red-team-review.md), to have a finished plan or spec attacked before anyone builds from it.
4. [Bug report template](templates/bug-ticket.md): the plain top layer a product reader gets on every bug.
5. [Tracker operations](playbooks/tracker-operations.md): reads and writes on work items, and which writes need your yes.
6. [Epic folder template](templates/epic-folder.md): one place for a large piece of work, and the [epic satellites template](templates/epic-satellites.md) beside its hub.
7. [Bug triage labels](triage-labels.md): the labels a triage meeting sorts bugs by.
8. [Bug triage meeting](playbooks/bug-triage-meeting.md): prepare the sheet and apply the outcomes. A product lane draft, for M9.
9. [Bug grooming](playbooks/bug-grooming.md): check a bug and fill its gaps before a fixer picks it up. A product lane draft, for M9.
10. [Checking a shelved predecessor](predecessor-check.md), for a major security bug. A product lane draft, for M9.
11. [Effort estimate](playbooks/effort-estimate.md): how big a feature is, as a range. A product lane draft, for M9.
12. [Standup report](playbooks/standup-report.md) and the [standup log template](templates/standup-log.md): what you moved since the last standup. A product lane draft, for M9.
13. [Pages for a product reader](product-reader-pages.md): the rules for a page a non-developer reads.

Planned for M9: the request door, where a new request from outside development enters the workspace and is sized. M9 builds it from real requests.

## Automation

1. [Orchestration](orchestration.md): tiers, the model binding, and how work is handed to a helper.
2. [Saved workflows](saved-workflows.md): scripts that dispatch helpers in a fixed shape. An automation lane draft, for M10.
3. [Regression run](playbooks/regression-run.md): the suite that M10 runs as a scheduled job, shared with QA.
4. [Changing the machinery](changing-the-machinery.md): the path every script, part, hook and CI change takes.
5. [Parts](parts.md): how a check or a hook is built.
6. [Evals](../evals/README.md): how a playbook is proven.

## DevOps

1. [Pinned repositories](parts.md#pinned-repositories) and [decision 0001](decisions/0001-pin-code-repositories.md): how code repositories sit under `src/`.
2. [Changing the machinery](changing-the-machinery.md): CI and hooks change on a branch, and merge after CI passes on three systems.
3. [Machine self-check](machine-self-check.md): check that a machine runs the workspace's hooks, checks and tools.
4. [Agent settings](agent-settings.md): what an agent tool may read or fetch, and how secrets reach a program.
5. [Commits](commits.md): the subject format and the trailer.
6. [Import a repository](playbooks/import-a-repository.md): pin a new code repository and update every page that names one. A DevOps lane draft, for M11.
7. [Environment self-check](environment-self-check.md): check the product's local container environment on your machine. A DevOps lane draft, for M11.
8. [Ship a new deployable](ship-a-deployable.md): infrastructure and CI for a new service, job or site. A DevOps lane draft, for M11.

Planned for M11: release and rollback, how a change ships and how it is undone. M11 builds them from real work.

## Rules

| Rule | Enforced by |
|---|---|
| Every link on this page resolves. | `links#a missing file fails`, `links#a missing heading fails` |
| A lane page names its lane in its `lane` key, from the five values. | `page_kinds#a lane outside the vocabulary fails` |
| A new lane page adds itself to its role's path here, in the same commit as the page, beside its row in the playbook catalog, the how-to index or the templates index. | `prose` |
