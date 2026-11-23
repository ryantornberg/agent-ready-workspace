---
kind: how-to
lane: automation
proof: unproven
prove-by: M10
last-reviewed: 2026-11-23
---

# Saved workflows

How to write and run a saved workflow, a script that dispatches helper sessions in a fixed shape. For whoever automates a repeated dispatch.

**In short:** a saved workflow runs one of two shapes: reviewers in parallel, or area runners one after another. It checks its arguments before it dispatches anything and pins each helper's tier from the binding. It retries a failed helper once, then reports, and returns conclusions, not files. Its script is machinery wherever it lives.

This is a lane draft: automation lane. It has not been run on real work yet; M10 runs it, as [decision 0006](decisions/0006-what-proven-means.md) says.

## When to use it, and which page wins

Use it when the same dispatch repeats in the same shape. Examples are the [review orchestrator](playbooks/review-orchestrator.md)'s reviews and a [regression run](playbooks/regression-run.md)'s per-area runs. A one-off dispatch needs no script: hand it off as [orchestration](orchestration.md#handing-work-off) says.

## What exists today and what is planned

| Piece | State |
|---|---|
| A saved workflow | None in this repository. An instance writes its own. |
| The agent tool that runs one | Differs between tools, and some cannot run one at all. The instance names its tool and that tool's run command in its own docs. This repository names neither. |
| A wrapper that starts a playbook | Planned for slice B6 of M3. Lane drafts get none. |

## The two shapes

| Shape | Helpers run | On a failed helper | For example |
|---|---|---|---|
| Reviewers | In parallel, each on its own question | One retry for that helper | One reviewer per review dimension |
| Area runners | Strictly one after another, each from its own written brief | One rerun for that area, then the next area | One runner per area of a regression suite |

A helper never takes another helper's output as its input. That is chaining tightly coupled work, which [orchestration](orchestration.md#delegating) rules out.

## What every saved workflow does

- **It checks its arguments first.** Each required argument is present and well formed before any helper starts. On a bad argument it stops, names the argument, and dispatches nothing.
- **It pins each helper's tier.** Each helper's prompt starts with `Tier: <tier>`. The script reads that tier's model and effort from the `tiers` entry of [workspace.json](../workspace.json) at run time. It never names a model itself.
- **It retries once, then reports.** A helper that fails gets one retry, or one rerun for an area. A second failure goes in the result as failed, with its error. The workflow never loops.
- **It returns conclusions.** Each helper returns findings in the shape its brief names, as [orchestration](orchestration.md#handing-work-off) says. The workflow returns those, never whole files.

To see the binding the script will read, run `python3 -c "import json; print(json.load(open('workspace.json'))['tiers'])"` at the top of the workspace.

## Steps to write one

1. **Pick the shape.** Input: the dispatch that repeats, and the agent tool and run command the instance names. If the instance names no tool that can run a saved workflow, stop: write no script, and report that. Choose a shape from [the two shapes](#the-two-shapes). Default: area runners when the helpers share an environment or data; reviewers otherwise. If one helper needs another's output, stop: write no script, and report why. Output: the shape.
2. **Place the script.** Input: the shape. Default: a file under `tools/`, which is machinery. If the instance's agent tool needs the script in another folder, stop and ask the person first. On a yes, use that folder. On a no or no answer, write no script, and report that the tool cannot run a script from `tools/`. Wherever it lives, the script is machinery, as the contract says, and takes the machinery path in step 4. A folder outside the `machinery` list of the `direct_push` part in [workspace.json](../workspace.json) escapes that part's check, not the path. Output: the path.
3. **Write it.** Input: the path and the shape. Write the script so it does each item in [what every saved workflow does](#what-every-saved-workflow-does). Each helper's brief carries one tight question, the shape of the answer and what is ruled out. Output: the script.
4. **Take the machinery path.** Input: the script. Follow [changing the machinery](changing-the-machinery.md#the-path-for-a-machinery-change), its failing case first, at the driver tier as [stakes raise the tier](orchestration.md#stakes-raise-the-tier) says. Output: the branch with the script and its case.
5. **Finish.** Input: the branch. End as [procedure endings](procedure-endings.md) says, on its row for machinery. The report names the script's path and the branch.

Stop when the report is given.

## Steps to run one

1. **Gather the arguments.** Input: the request and the procedure that calls the workflow. If no saved workflow exists for that procedure, or the instance names no run command, stop and report that. The calling procedure then dispatches its helpers by hand, as [orchestration](orchestration.md#handing-work-off) says. Name each argument the script needs. Default: a target environment is the person's local one. A shared environment needs the person's yes first, and naming it in the request is that yes. Output: the arguments.
2. **Run it.** Input: the arguments. Run `<the run command the instance names>`, with the instance's agent tool. An unattended run stops as [orchestration's limits](orchestration.md#limits) say. Output: the workflow's result.
3. **Read the result.** Input: the result. List each helper's conclusions, and each helper reported failed after its retry. Default: do not run the workflow again by hand; a failure goes in the report. Output: the conclusions and the failures.
4. **Finish.** Input: steps 1 to 3. Hand the conclusions back to the procedure that called the workflow, if one did. Otherwise end as [procedure endings](procedure-endings.md) says. The report names each failed helper and its error.

Stop when the report is given.

## Rules

| Rule | Enforced by |
|---|---|
| A workflow checks its arguments before it dispatches anything. | `prose` |
| Each helper's prompt starts with `Tier: <tier>`. Whether the agent tool's handoff hook sees a workflow's dispatches depends on the tool. | `prose` |
| A script never names a model; it reads model and effort from the `tiers` binding. | `prose` |
| A failed helper gets one retry, then is reported; a workflow never loops. | `prose` |
| A workflow returns conclusions, never whole files. | `prose` |
| A helper never takes another helper's output as its input. | `prose` |
| A saved workflow's script is machinery wherever it lives, and takes the machinery path. | `prose` |
| Place a script outside `tools/` only on the person's yes. | `prose` |
| A shared environment is a target only on the person's yes. | `prose` |
