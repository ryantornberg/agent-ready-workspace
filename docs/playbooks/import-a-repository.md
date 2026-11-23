---
kind: playbook
lane: devops
proof: unproven
prove-by: M11
last-reviewed: 2026-11-23
---

# Import a repository

Steps for pinning a new code repository under `src/` and bringing every page that names repositories up to date, for the agent doing the import.

**In short:** an import is never small, so it runs as slices of an approved plan. Check who can reach the repository, pin it over HTTPS at its default branch's tip on a branch of its own, and register the pin, `src/README.md` and the project hub in one commit. Then draft unit docs, sweep every surface that names repositories, run a cold clone, and merge through a pull request.

This is a lane draft: devops lane. It has not been run on real work yet; M11 runs it, as [decision 0006](../decisions/0006-what-proven-means.md) says.

Why pins and not copies is [decision 0001](../decisions/0001-pin-code-repositories.md). How a fresh clone checks pins out is [pinned repositories](../parts.md#pinned-repositories).

## Which path the change takes

| Path | Machinery? | How it lands |
|---|---|---|
| The pin under `src/<repo>` and `.gitmodules` | No: neither is in [changing the machinery](../changing-the-machinery.md#what-counts-as-machinery)'s table. | With the pages, on the import's own branch. It changes `src/`, so it is not a change of pages only: it takes [procedure endings](../procedure-endings.md#the-push)' row for code under `src/`, a draft pull request. |
| `src/README.md`, the hub, unit docs | No. | In the same pull request. |
| `outward-repos.json` | Yes. | Only a person edits it, on a branch of their own, with its own pull request. The `outward_list` hook refuses an agent's edit. |
| `workspace.json`, such as the `shelved` part's `paths` | Yes. | Its own branch and pull request, at the driver tier, as changing the machinery says. |

The import's pull request merges only after CI passes on Linux, macOS and Windows, as the contract's rule on draft pull requests says.

## Steps

1. **Climb the ladder.** Input: the request, naming the repository's URL. An import touches several surfaces and is hard to undo once others pull it, so it never passes [the size gate](../size-the-work.md#the-gate). Climb [the ladder](../size-the-work.md#the-ladder): goal and non-goals, then a [hand-off plan](../templates/hand-off-plan.md) a person approves. Steps 2 to 11 are its slices, the instruction reviews of steps 7 to 9 included. Output: the approved plan. With no approval, stop at step 12.
2. **Check reach and readers.** Input: the URL, as `https://github.com/OWNER/REPO.git`. Run `GIT_TERMINAL_PROMPT=0 git ls-remote --symref URL HEAD`. It prints the default branch and its tip, or fails at once without a password. On GitHub, also run `gh repo view OWNER/REPO --json visibility,defaultBranchRef`. Output: the default branch, its tip commit, and the visibility. Default: when this workspace is public and the repository is private, say so in the plan: other readers and the cold-clone job will skip it, as [pinned repositories](../parts.md#pinned-repositories) says. If `ls-remote` fails, stop at step 12 and report it.
3. **Make the branch.** Input: the repository's name. Where you are, run `git fetch origin`, then `git switch --no-track -c import/REPO origin/main`. Starting from the remote's main keeps commits that are not the import's off the branch and its pull request. Uncommitted changes you did not make come along: leave them, and stage only by name. If the lease hook refuses an edit, the contract sends you to a worktree: run `git worktree add --no-track -b import/REPO .claude/worktrees/import-REPO origin/main`, as the refusal says, and work there. Output: the branch, and the folder that has it checked out.
4. **Pin it.** Input: the URL and the tip from step 2. Run `git submodule add URL src/REPO`. Then check that `git -C src/REPO rev-parse HEAD` prints step 2's tip. Default: always the HTTPS URL, never SSH, so a reader without a key can clone. The `pin_on_default` check refuses a pin the upstream's default branch does not hold. Output: the pin and its `.gitmodules` entry.
5. **Survey the units.** Input: the checkout. List its files with `git -C src/REPO ls-files`. Find each unit: a service, library, client or infrastructure folder, as the [unit doc template](../templates/unit-doc.md) defines them. For each unit, find its consumers with `git grep -l NAME -- src`. Output: a table of units, each with its kind and consumers.
6. **Ask for scope once.** Input: the units table. Ask the repository's owner, in one message, which units get a unit doc and which get a pointer row only. Default: with no answer, every unit gets a pointer row with the reason "scope not set yet"; the report names it. Output: the scope per unit.
7. **Register it in one commit.** Input: the pin and the scope. In one commit: the pin and `.gitmodules`, a line in [src/README.md](../../src/README.md), and the project hub. The project is the one the request names; by default, a new project named after the repository. If that project has a hub, add one units row per unit from step 5 to it. If not, write one to the [hub template](../templates/hub.md) at `docs/projects/<project>/README.md` when its "When to use it" holds; otherwise write no hub, and the `src/README.md` line names the unit. The hub is a guidance page, so run [the instruction review](instruction-review.md) on it and settle its findings. Stage each file and the review record by name, then run `python3 ws.py check --staged`, and fix each finding on these files. Commit them as [procedure endings](../procedure-endings.md#the-commit) says, on the import's branch, with the record in the `Instructions-review:` trailer. Output: the registration commit.
8. **Draft the unit docs.** Input: the units in scope. Hand each unit to one fresh helper at the worker tier, as [orchestration](../orchestration.md#handing-work-off) says. Each writes one page to the [unit doc template](../templates/unit-doc.md), checked against the pin. Then one more fresh helper at the driver tier reviews every page against the pinned code, as [fresh context for critics](../orchestration.md#fresh-context-for-critics) says. Settle each finding. Unit docs are guidance pages: run [the instruction review](instruction-review.md) on each, one record per page, and settle its findings. Output: the unit docs and their records, committed on the import's branch as procedure endings says, each record named in the `Instructions-review:` trailer.
9. **Sweep the integration surfaces.** Input: the new repository's name. Answer every row of [the sweep](#the-sweep) with the change made, or "no change" and why. Commit the changes on the import's branch as procedure endings says, before step 10, so the clone and the pull request hold them. A changed guidance page, such as a rule page or the glossary, gets [the instruction review](instruction-review.md) first, its record named in the trailer. Output: the answered sweep, for the report.
10. **Run a cold clone.** Input: the branch. In a temporary folder outside the workspace, run `git clone --quiet --branch import/REPO <working copy path> <tmp>/fresh`, where the path is the folder from step 3. In that clone, run `bash wslib/launch.sh tools/setup_steps.py README.md > <tmp>/setup.sh`, then `bash <tmp>/setup.sh`. It follows the README's marked setup steps, as [the cold-clone job](../parts.md#the-cold-clone-job) does. Pass: it exits 0, and `python3 ws.py pins` in its output checked the new repository out. When step 2 found the repository private and `pins` reports it unreachable, it passes on exit 0 alone, and the report says the check-out went untested. Output: pass, or the failing step. If it fails, fix the cause and run it again, once; if it still fails, stop at step 12.
11. **Open the pull request.** Input: the branch. Open it as a draft, as [git-host operations](git-host-operations.md) says. It merges after CI passes on three systems, as [changing the machinery](../changing-the-machinery.md#the-path-for-a-machinery-change)'s steps 5 and 6 say. Output: the pull request's link.
12. **Finish.** End as [procedure endings](../procedure-endings.md) says. The report names the pin's commit, the scope per unit, the answered sweep, each row queued for a person or the next eval run, and the cold clone's result.

Stop when the report is given.

## The sweep

An import once left other surfaces naming the old set of repositories. Every row gets an answer.

| Surface | What to check |
|---|---|
| `src/README.md` | A line for the repository, saying what it is. Done in step 7. |
| The project hub | A units row per unit, when step 7 wrote one or the project had one. Done in step 7. |
| `outward-repos.json` | Must agents write to this repository? If so, give the person the exact line; they add it, as the path table says. |
| The contract's facts in `AGENTS.md` | Does the repository add a trap a model cannot derive, such as a look-alike? The file is eval-covered: queue the change for the next eval batch. |
| `INDEX.md` | Topic rows and search aliases for the new names. Eval-covered: queue it, never edit it in this branch. |
| Rule pages in [docs/rules/](../rules/) | Does a fact hold for every edit under `src/REPO/`? Then a rule page with an `applies-to` pattern, as [the live order service's](../rules/orders-api.md). |
| The [glossary](../glossary.md) | A term the repository brings that a reader would not know. |
| The `shelved` part in `workspace.json` | Is the repository read-only, like `src/orders-service-v1`? Then its path joins `paths`, as machinery. |
| The cold-clone job | Step 10 ran it. A private repository is skipped there; say so. |
| `python3 ws.py pins` | It checks the repository out on a fresh clone. Step 10's output shows it. |

## Decisions and open points

| Decided | Why |
|---|---|
| HTTPS, at the default branch's tip | Any reader can clone it, and `pin_on_default` holds the pin to the default branch. |
| Pin, `src/README.md` and hub in one commit | No commit on the branch has a pin with no page naming it. |
| No answer on scope means pointer rows | A pointer row is cheap to replace with a page later. |

Not settled:

- Where unit docs live: the [open question on adopting the workspace](../adopt-the-workspace.md#open-question-where-per-repository-reference-docs-live). Until an instance settles it, they go beside the hub.
- How to remove a pin. No page covers it yet.

## Rules

| Rule | Enforced by |
|---|---|
| An import climbs the ladder; it never goes straight to a fix. | `prose` |
| Pin at a commit on the default branch. | `pin_on_default#a pin off the default branch fails, naming the pin and the branch` |
| Pin over HTTPS, never SSH. | `prose` |
| Work on a branch of its own, made from `origin/main` with `--no-track`; use a worktree only when the lease hook refuses an edit. | `prose` |
| Register the pin, `src/README.md` and the hub in one commit, after `python3 ws.py check --staged`. | `prose` |
| A hub, unit doc or other guidance page is committed with its instruction review record named in the trailer. | `review_trailer#a guidance page changed with no trailer fails` |
| Ask the owner for scope once; with no answer, use pointer rows. | `prose` |
| A fresh helper reviews the unit docs, never the one that wrote them. | `prose` |
| Answer every row of the sweep. | `prose` |
| Never edit `outward-repos.json`; give the person the line. | `outward_list#an edit to the list is refused` |
| Never edit `INDEX.md` or `AGENTS.md` in the import; queue the change. | `prose` |
| The pull request merges only after CI passes on three systems. | `prose` |
