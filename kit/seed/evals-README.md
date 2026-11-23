# Evals

A test of this workspace's guidance: does an agent that is given it do better than one that is not, and better than one given two lines instead? A small change to a playbook's wording can change what an agent does, and without a case nobody notices until it does the wrong thing in real work.

**In short:** this workspace has no eval cases yet. Add one for the task your team repeats most, from a real failure, and record it with `python3 evals/run.py NAME`, where NAME is the case's name. A page the kit marks proven was proven in the kit, on the kit's own cases; the `eval_record` check here gates only the pages this workspace proves itself.

## The cases

A case is a JSON file under `evals/cases/`, with the keys `name`, `playbook` (the page it tests), `scaffold_dir` (the folder the agent works in), `code_dir`, `acceptance` (a hidden acceptance test), `request` (the one-line request) and `graders`. Each grader has an `id` and a `type` from the list at the top of `grade.py`. The harness is `run.py`, `grade.py`, `pool.py` and `proofkeys.py`, which the kit owns; `python3 evals/run.py --help` lists the run's options, such as the model and the runs per arm. The kit's own cases test its invented order system and stay in the kit, so the first case here is your team's.

Each case runs three arms. [arms.json](arms.json) lists the files each arm is given: the guided arm gets the workspace's contract, index, playbook and definition of done; the two-line arm gets [two lines](two-line.md); the bare arm gets the scaffold only. Both files came from the kit and name its fix-a-bug playbook and that playbook's two habits. For a case on a playbook of your own, change both files to name yours, or have the case name its own arm files under `arms`.

## The gate

Only pages marked proven are gated, as [decision 0006](../docs/decisions/0006-what-proven-means.md) says. For each case of a proven page, the run's record stores one hash over what the run depends on: the case, its acceptance test, the scaffold, the arm files and the harness. The `eval_record` check compares the hash on every commit and in CI, so an edit to any of them fails the commit until the case is run again. A proven page needs, pooled across its cases, 40 or more runs per arm, with the guided arm beating the two-line arm by a one-sided Fisher exact test at p < 0.05.

A synced page the kit marks proven is the exception. Its records stay in the kit, so the check reads its state from `kit.lock.json` and does not gate it here. Treat it as proven in the kit, not yet in this workspace: once your contract and index replace the samples, the kit's runs no longer test what your agents read.

So the kit left one rule out of this workspace's contract: that a change to it, or to the index, needs a new eval run. With no case of your own, no run could be made. When this workspace proves a page of its own, add that rule back to the contract's rules table, tagged `eval_record#an edited playbook fails until its case is run again`, so a change to what its cases cover fails until they run again.

## The wrappers' selection cases

Each [wrapper](../docs/playbooks/README.md#three-ways-to-follow-a-playbook) has two or more selection cases: a request that should fire it, and a nearby request, one a wrapper next to it owns, that should leave it quiet. They test only whether the right wrapper loads. They sit with the plugin, one folder per case in `plugin/evals/`, in the format `claude plugin eval` reads. The kit gave you its own cases; rewrite each request in your team's words. To add a pair, copy an existing one and change the request and the wrapper's name. The `wrappers` check fails a wrapper that lacks either kind, and a case in any other form.

A run costs real agent time, so a person starts it, or an agent on that person's yes for that run. Run them from the top of the workspace, on the small model you hand work to, without the run that leaves the plugin out:

```
claude plugin eval plugin --model haiku --ablation none --no-publish --output-dir evals/selection/YYYY-MM-DD
```

Commit `evals/selection/YYYY-MM-DD/aggregate-result.json` and nothing else from the run, after searching it for your user name, home folder and git identity and replacing each with a placeholder. A wrapper that fails its case that fires in most of its runs is rewritten once, and the result is recorded either way.

## Rules that make this worth doing

These are advice; no check holds them.

- When an agent goes wrong in real work, turn the failure into a case before you fix the guidance.
- Run the cases on the smaller models you hand work to, not only the largest.
- Write a new playbook only after a run without it shows the model failing at the task.
- Never describe the graders in a page the agent reads.
