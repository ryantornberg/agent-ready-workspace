---
kind: how-to
proof: unproven
prove-by: M5
last-reviewed: 2026-11-23
---

# Adopt the workspace

How a team takes this workspace for its own code: what transfers, what does not, and when the adoption is done. For the person setting up an instance.

**In short:** follow the steps below. They make the instance with the kit, run the README's setup steps, under [Use it for your own team](../README.md#use-it-for-your-own-team), inside a plan the person approves, then check the adoption is done. The engine, the parts and the procedures transfer; the sample facts and this workspace's history do not, and its proof transfers as the kit's.

## The kit

An instance is a copy of this workspace that a team adopts and runs on its own code.

The kit makes it. From the kit's repository, `python3 ws.py adopt PATH` writes an instance into PATH, an empty folder. The kit classes each file as synced, which the kit owns; seeded, which the instance owns from the start; or never synced, which stays in the kit. The instance's `kit.lock.json` records what it got, and `python3 ws.py drift` there names a synced file someone edited. [Decision 0007](decisions/0007-the-kit.md) says which file is in which class, and how an upgrade from a newer kit works. The tables below say what that means for each part of the workspace.

## What transfers

| What | Transfers | Note |
|---|---|---|
| The engine (`ws.py`, `wslib/`) and `tools/` | Yes, as they are | Change them only as [changing the machinery](changing-the-machinery.md) says. |
| The parts and their cases, and the shape of `workspace.json` | Yes | Set your own values where a part reads them, such as the commit subject formats in [commits](commits.md). A check that fails on old findings you cannot fix yet can tolerate them through a [baseline](parts.md#baselines). |
| The hook wiring: `.githooks/`, `.claude/settings.json`, `.codex/hooks.json` | Yes | The README's setup turns the git hooks on. |
| The page kinds, [layout](layout.md), the templates, the playbooks and how-tos | Yes, as procedures, synced, except the feature layer walk, which is seeded | Rewrite the feature layer walk's lists for your code; it is yours. To change any other, keep your own copy, as decision 0007 says. A page the kit marks proven cannot be kept: write your own steps on a page of your own. Their proof marks are the kit's; see the next table. |
| The decision records in `docs/decisions/` | Yes, as background | They say why the machinery works as it does. Your own decisions take the next free number, as [extend the workspace](extend-the-workspace.md) says. A later kit record may take the same number; the upgrade then refuses until you renumber yours. |

## What does not transfer

| What | Why | What to do |
|---|---|---|
| The facts in `AGENTS.md`, the aliases in `INDEX.md`, and the samples in `src/` | They describe the invented order system. | Replace them, as the README's steps say. See "Write the facts from evidence" below. |
| The rule page in `docs/rules/` | It describes the sample `src/orders-api`. The README's steps do not name it. | Rewrite it for one of your own repositories, or remove it and fix each link the `links` check then names. In a copy made by hand, an eval case covers it, so this joins the eval run that the contract and index changes need; an instance the kit makes has no case yet. |
| The eval cases in `evals/cases/` | They test the invented order system. | The kit does not copy them. Write cases from your own code, as the README says. |
| A proven page's proof | It rests on this workspace's runs and records. | The kit carries each synced page's proof state in `kit.lock.json`, and the proof checks read it there. Treat a page marked proven as proven in the kit, not yet in your instance. |
| This workspace's milestone state: `building` in `workspace.json`, which names M3 here and nothing in an instance the kit makes | M3 is this workspace's milestone, and its approved plan names this workspace's maintainer. | Once step 3's plan is approved, give it `milestone: M<n>` and set `building` to that milestone. Pick a number above every milestone a kept page or plan names in `prove-by`, a section's proof line or `milestone`, since the `proof` check fails an unproven page once its `prove-by` milestone's record is signed off. `git grep -h -o -E 'prove-by:? M[0-9]+|^milestone: M[0-9]+' -- docs | grep -o -E 'M[0-9]+' | sort -u -k1.2n` lists them in number order, the highest last. The plan's approver is then the maintainer that [maintain the workspace](maintain-the-workspace.md) names. |
| This workspace's plans, milestone records, eval records and other records | They are this workspace's history. | The kit never syncs them, and an instance's checks pass without them. In a copy made by hand instead, keep them: removing them fails the `proof`, `links`, `chains` and `review_index` checks, because fix a bug's proof, the index's chains and the pages' links name them. |
| The entries in the [question log](question-log.md) | They are this workspace's gaps. | Start your own log, as the README's steps say. |
| This workspace's tracker and git host | This repository has no tracker, and its git host is GitHub. | Name your own tracker and git host. Their providers and your team's trap tables are planned for M8; until then, see [tracker operations](playbooks/tracker-operations.md) and [git-host operations](playbooks/git-host-operations.md). |
| The repository's settings on GitHub | Settings are not files, so a copy does not carry them. | Set them by hand, as the README's last setup step says. |
| The maintainer's private deny list | It is kept outside the repository. | Without a list, the `deny_list` check warns and checks nothing. Keep your own list, if you want one, where [changing the machinery](changing-the-machinery.md#traps) says the check reads it. |
| Who publishes a pull request | In this repository, the maintainer lets agents publish and merge. | In your instance, a person publishes, as the contract's rules say. |

## Write the facts from evidence

Write a fact down only after a run shows the model getting it wrong, or a person had to answer it. The README's first step asks for the facts a model gets wrong about your code; this is how to find them.

1. Give an agent a few real tasks from your team's work, in the copy, with the sample facts removed.
2. Note each wrong turn: the wrong service, a word it could not map to a name, a step your team does differently.
3. Write each one in its one place: a trap in the contract, an everyday word in the index's aliases, a fact for one folder in a rule page. The table in [extend the workspace](extend-the-workspace.md#pick-the-kind-and-the-place) says which.

Leave out what the model gets right from the code alone. The README's fourth step asks for a playbook for the task you repeat most, and one eval case for it. Write it as [extend the workspace](extend-the-workspace.md) says: its step 3 runs the task without the playbook, and that run's failure is the source of the eval case. If the run does not fail, that task needs no playbook: take the next task you repeat, and say so in the report. Add a part when the same mistake shows up twice, as the README says.

## Open question: where per-repository reference docs live

A reference page about one code repository, such as its architecture or its conventions, could live in that repository or in the workspace. This is not settled.

| Where | Gains | Loses |
|---|---|---|
| In the code repository | The page travels with the code's branches, so one commit can change both. | The workspace's checks do not read pages inside a pinned repository, so its links, dates and kind go unchecked. |
| In the workspace | The checks hold the page. [Rule pages](rules/) already work this way, by path pattern. | The page does not travel with code branches: while a branch is open, it describes the default branch, not the branch. |

Neither has been chosen; a trial in a real instance is the recommended way to settle it. Until then, leave each repository's existing docs where they are, and write new workspace pages in the workspace. When your instance settles it, record the choice as a decision record.

## Steps

1. **Make it and run it unchanged.** Input: the team's decision to adopt. The person makes the instance with `python3 ws.py adopt PATH`, run from a clone of the kit, and makes its remote on the git host. In the instance, run the README's [Try it](../README.md#try-it) setup blocks before changing anything, and make the first commit as it says: the kit's pages, with the line `Instructions-review: skipped: as the kit wrote it`. Output: a copy whose setup passes. If a setup command fails, run step 2, then the setup again. If it still fails, stop and go to step 8 with the error; nothing has changed.
2. **Check each machine.** Input: the copy, set up. Each person who will run agents in the instance runs the [machine self-check](machine-self-check.md) on their own machine. Output: its report, and any fix the person said yes to. Default: go on to step 3 only when no step of the report still fails. If one still fails, such as a declined fix or a workspace bug, stop and go to step 8 with it, since the guards may not run on that machine; nothing has changed in the copy.
3. **Size it and plan it.** Input: the copy and the team's code repositories. Put the adoption through [the size gate](size-the-work.md#the-gate). Default: it climbs [the ladder](size-the-work.md#the-ladder), since it spans several repositories and more than a day. Write its goal, non-goals and [hand-off plan](templates/hand-off-plan.md) in the copy's `docs/plans/`, and have the person approve the plan before step 4. Output: the approved plan. If the person does not approve, stop and go to step 8.
4. **Make it the team's.** Input: the approved plan. Follow the README's "Use it for your own team" steps in order, with the two tables above beside you. For its steps on facts and aliases, work as "Write the facts from evidence" says. Default: keep every file the tables do not say to replace. Output: the copy, holding the team's facts, pins, aliases and eval cases.
5. **Settle the open question, or leave it open.** Input: the team's code repositories. Default: leave it open, as the section above says. Output: a decision record, or a line in the report saying it is still open.
6. **Commit.** Input: the changed files in the copy. Run `python3 ws.py check`, then commit through the copy's normal path: the [instruction review](playbooks/instruction-review.md) for each guidance page, files staged by name, as [procedure endings](procedure-endings.md#the-commit) says. A change to a machinery path, such as `workspace.json`, `.github/workflows/ci.yml` or `evals/cases/`, follows [changing the machinery](changing-the-machinery.md#the-path-for-a-machinery-change) instead: its own branch, and a merge only after CI passes on Linux, macOS and Windows, with a person publishing the pull request. Once a page you prove yourself has eval cases, a change to the contract or the index fails the commit check until the eval has run on them again; the eval trap in [changing the machinery](changing-the-machinery.md#traps) says how to save that work on a branch before the runs. Until then the eval gates nothing in the instance: a page the kit proved is not gated there, and the kit left the contract's rule on eval runs out, as decision 0007 says. When the instance proves a page of its own, add that rule back, as the `evals/README.md` an instance gets from the kit says. Output: the commits. If a check fails and will not clear, leave those files uncommitted and go to step 8 with the finding.
7. **Check it is done.** Input: the instance. Go through the table below, item by item. Output: each item checked, or the reason it is not.
8. **Finish.** Input: the outputs above. End as [procedure endings](procedure-endings.md) says: the question-log entry, the push, and the report. By exception to its push table's rows for pages, a branch the eval trap made is pushed as a branch, as that trap says, never to main; who pushes it follows that table's row for machinery. Name each done item not met, each file left uncommitted and why, and whether the open question was settled.

Stop when the report is given. Every stop in steps 1 to 7 ends in that report too, with the reason said.

## When an adoption is done

| Done when | Checked by |
|---|---|
| The checks pass in the instance, and every file the kit owns is as it shipped. | `python3 ws.py selftest`, `python3 ws.py check` and `python3 ws.py drift`, run in the instance |
| The git hooks are on. | `git config core.hooksPath` prints `.githooks` |
| Each pinned repository checks out. | `python3 ws.py pins` names each one, and skips none |
| The index's aliases and the contract's code names name your code, not the samples. | The `aliases` check in `python3 ws.py check` passes once the samples are gone from `src/` |
| The eval runs on cases from your own code, with records on file. | `evals/cases/` holds a case from your own code and `evals/runs/` its record; the `eval_record` check holds them once a page they test is marked proven |
| The question log is started. | The log has its first entry, or the person says no question has come up yet |
| The repository allows merge commits only, and its default branch requires CI. | The repository's settings page on the git host, read by the person |
| Each person who runs agents ran the machine self-check. | Each self-check's report |
| The open question on per-repository docs is settled or named as open. | A decision record, or the report |

## Rules

| Rule | Enforced by |
|---|---|
| The setup steps live in the README; this page links them and never restates them. | `prose` |
| In a copy made by hand, keep this workspace's plans, milestone records, eval records and other records; an instance the kit makes never gets them. | `proof#a proven-by path that does not exist fails`, `chains#a chain path that does not exist fails` |
| Write a fact down only after a run shows the model getting it wrong, or a person had to answer it. | `prose` |
| An adoption climbs the size gate's ladder: nothing is made the team's before the person approves its plan. | `prose` |
| The engine, the tools and the parts in a copy change only as changing the machinery says. | `direct_push#a commit that changes a part fails, naming the commit and the path` |
| A change to a machinery path in the copy, such as `workspace.json`, CI or the eval cases, reaches the default branch only through a pull request. | `direct_push#a commit that changes a part fails, naming the commit and the path` |
| Go past the machine self-check only when no step of its report still fails. | `prose` |
| Mark every claim in the report verified or inferred. | `eval:fix-a-bug` |
| Once the instance proves a page of its own, a change to the contract or the index fails the commit check until the eval runs again. | `eval_record#so does an edit to the contract the guided arm is given` |
| In an instance, a person publishes pull requests. | `prose` |
| An adoption is done only when each item of its done table is checked or reported as not met. | `prose` |
