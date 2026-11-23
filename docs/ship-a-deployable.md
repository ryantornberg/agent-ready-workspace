---
kind: how-to
lane: devops
proof: unproven
prove-by: M11
last-reviewed: 2026-11-23
---

# Ship a new deployable

Steps for giving a new service, job or site its infrastructure and CI, for the agent or developer adding it to a code repository.

**In short:** a generator usually writes most of a new deployable's infrastructure and CI. Run it, do the two manual steps it does not cover for your instance, and verify the result locally before you push. The instance fills in the generator, the two steps and the verify command below.

This is a lane draft: devops lane. It has not been run on real work yet; M11 runs it, as [decision 0006](decisions/0006-what-proven-means.md) says.

A deployable is a unit that is built and deployed on its own, such as a service, a scheduled job or a site. CI (continuous integration) is the pipeline that builds and tests each change.

## What the instance fills in

This repository deploys nothing, so it has no generator. An instance replaces each value below with its own. Until it does, the agent stops at step 2.

| Value | What it is | This instance's value |
|---|---|---|
| The generator | The command that writes the deployable's infrastructure and CI files | `<generator command>` |
| Manual step 1 | A step the generator does not cover, such as registering the deployable with a secrets store | `<step>` |
| Manual step 2 | A second such step, such as adding its route to a shared gateway's settings | `<step>` |
| Verify locally | The command that builds the deployable and checks its infrastructure files without deploying | `<verify command>` |

## Steps

1. **Size it.** Input: the request, naming the deployable and its code repository. Put it through [the size gate](size-the-work.md#the-gate). Default: when you cannot tell, it fails; a new deployable usually does. If it fails, climb [the ladder](size-the-work.md#the-ladder), and run steps 2 to 7 as slices of the approved plan. If it passes, run steps 2 to 7 yourself. This is a labelled exception to the contract's "How work flows", which sends a change that passes the gate to [fix a bug](playbooks/fix-a-bug.md): a new deployable has no failing test to start from, so step 5's local verification takes its place. Output: the route.
2. **Read the instance's values.** Input: the table above. Output: the four values. If any is still in angle brackets, stop at step 7 and report which.
3. **Run the generator.** Input: the code repository, on a branch of its own, never its main. Run the generator there. Output: the files it wrote, listed with `git status --short` in that repository.
4. **Do the two manual steps.** Input: the table's two steps. Do each one in the code repository. A step that writes to a shared system, such as a secrets store or a gateway, is an outward write: ask the person first, unless the request names the write in its own words, as [procedure endings](procedure-endings.md#outward-writes) says. Default: with no yes, do not make it; give the person the exact change, and the report names it as waiting. Output: each step done, or waiting.
5. **Verify locally.** Input: the branch. Run the verify command on the person's machine. Pass: it exits 0. Default: a failure is fixed and the command run again, twice at most; then stop at step 7 with the output. Output: the command's result.
6. **Hand on the change.** Input: the verified branch. Commit and push it as [procedure endings](procedure-endings.md#the-commit) says for code in a code repository, and as that repository's own rules say. An agent may push only to a repository listed in `outward-repos.json`; the `outward_write` hook refuses any other. If the code repository is not listed, push nothing: give the person the line to add, since only a person edits that list. Open the pull request as [git-host operations](playbooks/git-host-operations.md) says. Deploying to a shared environment needs the person's yes first, even when CI passes. Output: the pull request's link, or the commits left unpushed.
7. **Finish.** End as [procedure endings](procedure-endings.md) says. The report names each file the generator wrote, each manual step done or waiting, and the verify command's result.

Stop when the report is given.

A change to this workspace's own CI, under `.github/`, is not this page's work. It is machinery: follow [changing the machinery](changing-the-machinery.md).

## Rules

| Rule | Enforced by |
|---|---|
| With any instance value unfilled, stop and report; never guess a generator or a manual step. | `prose` |
| Run the generator on a branch of its own in the code repository, never on its main. | `prose` |
| A manual step that writes to a shared system needs the person's yes first, unless the request names that write. | `prose` |
| An agent pushes only to a repository listed in `outward-repos.json`. | `outward_write#a push to a repository outside the list is refused` |
| Verify locally before the change is pushed. | `prose` |
| Never deploy to a shared environment without the person's yes. | `prose` |
| A change to this workspace's CI follows changing the machinery. | `prose` |
