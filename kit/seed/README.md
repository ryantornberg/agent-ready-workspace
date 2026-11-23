# Your team's workspace

The workspace your team's coding agents read before they work on your code, made from the agent-ready-workspace kit. Replace this line with what your workspace covers.

**In short:** run the setup below, then make the workspace your team's with the steps under "Use it for your own team". The kit owns its synced files: `python3 ws.py drift` names any you edited, and an upgrade from a newer kit replaces them, refusing while any is edited. Your facts, your index and your records are yours.

## Try it

Run these from the workspace's top folder. An HTML comment, `<!-- setup -->`, marks each block a fresh clone needs.

<!-- setup -->
```
python3 ws.py --version     # the engine's version, which the manifest must name
python3 ws.py pins          # check out the pinned code repositories under src/ (the sample pins none)
python3 ws.py list          # the parts this workspace uses, and the phases each check runs in
python3 ws.py selftest      # every part's own cases
python3 ws.py check         # run the checks on this workspace
python3 ws.py drift         # every file the kit owns, as the kit shipped it
```

To run the checks before every commit, and on every commit message, a person runs this from their own terminal; the guards refuse an agent's change to git config:

<!-- setup -->
```
git config core.hooksPath .githooks
```

Then a person commits what the kit wrote, before changing anything. That commit brings pages the kit's own instruction reviews read, so its message carries the line `Instructions-review: skipped: as the kit wrote it`; the commit check accepts it only while every page is as `kit.lock.json` holds it. The first push creates main, so push it once with `--no-verify`, as [changing the machinery](docs/changing-the-machinery.md#the-path-for-a-machinery-change) says.

## What is checked, and by what

The checks and guards are parts, and `workspace.json` names the parts this workspace runs. The table of [the parts here](docs/parts.md#the-parts-here) lists each one, with what it fails or refuses and whether it reads the commit message too. `python3 ws.py list` prints the parts in use, with the phases each check runs in, and `python3 ws.py rules` prints every rule in the pages' rules tables with what enforces it. The runner itself also refuses a hook event it cannot read, and a manifest written for another engine version; [decision 0004](docs/decisions/0004-the-hook-contract.md) and [decision 0003](docs/decisions/0003-the-engine-in-one-folder.md) say how.

## Use it for your own team

[Adopt the workspace](docs/adopt-the-workspace.md) runs these steps inside a plan a person approves, and says when the adoption is done.

1. Replace the facts in `AGENTS.md` with the ones a model gets wrong about your code. Leave out anything it gets right from the code alone.
2. Put your code repositories under `src/` as submodules, and remove the samples. Add `submodules: true` to the checkout step in `.github/workflows/ci.yml`. On a fresh clone, `python3 ws.py pins` checks out each one whose remote answers.
3. Fill the alias table in `INDEX.md` from the words your team actually says.
4. Write a playbook for the task you repeat most, and one eval case for it, as [evals](evals/README.md) says.
5. Start the [question log](docs/question-log.md). Each entry is a gap; fix the page, then note the fix.
6. Put your own repositories in `outward-repos.json`, each as its host and its whole path as the repository's URL gives it, such as `github.com/your-team/your-workspace`. The kit made the list empty, so agents write to no repository until a person adds one; add this workspace's own repository first. A person edits the file from their own terminal; the guards refuse an agent's edit. It is machinery, so the change reaches main through a pull request.
7. If your workspace lives on GitHub, set two things in the repository's Settings. Under Pull Requests, keep "Allow merge commits" on, and turn "Allow squash merging" and "Allow rebase merging" off. A squash or rebase merge drops a branch's own commits from main's history, and a proof anchor pinned to one of them with it; the setting also covers a merge from the web page. Under Branches, give main a rule that requires the CI jobs in `.github/workflows/ci.yml` to pass. `python3 ws.py merge NUMBER`, the way an agent merges, refuses every pull request while the rule requires no check. See [changing the machinery](docs/changing-the-machinery.md#the-path-for-a-machinery-change).

Add a part when the same mistake shows up twice.

## The kit

`kit.lock.json` lists every file of the kit, with its class and hash as of the kit version this workspace holds: the files this workspace got, and those that stayed in the kit. [Decision 0007](docs/decisions/0007-the-kit.md) says why the classes are drawn where they are.

| Class | What it is | Who changes it |
|---|---|---|
| Synced | The engine, the parts, the hooks and their wiring, the procedures, the templates and the kit's decision records | The kit. An upgrade replaces each one you have not edited, and refuses while any is edited. |
| Seeded | The contract, the index, the manifest, the sample code, the rule pages, the glossary, this page and the empty logs | You. The kit wrote each once, when the workspace was made, and never touches it again. |
| Never synced | The kit's own plans, records, eval cases and runs, tests and CI | Nobody here: they stay in the kit. |

The lock gives each file's class; the table names the main ones.

`python3 ws.py drift` fails, naming the file, when a synced file was edited or deleted. Put the kit's copy back with `git checkout`, or keep yours with `python3 ws.py drift --keep PATH`; a kept file is yours from then on, and upgrades leave it alone. A page the kit marks proven cannot be kept, since its proof rests on the kit's text: write your own steps on a page of your own instead. To take a newer kit, clone it, and from that clone run `python3 ws.py upgrade PATH`, where PATH is this workspace. It refuses while any synced file is edited, and changes nothing then. It changes the engine and the manifest's version together, so commit the result on a branch, as [changing the machinery](docs/changing-the-machinery.md#the-path-for-a-machinery-change) says, with the line `Instructions-review: skipped: as the kit wrote it` in the message. When the upgrade changes a page's proof state, correct its row in the table below in the same commit, have that change reviewed, and name the review's record in a second `Instructions-review:` line.

## Proven and unproven pages

A page marked proven was proven in the kit: a real run and an eval in which it beat both the bare model and two lines are on record there, not here. An unproven page names the milestone of the kit's plan that is to prove it. See [decision 0006](docs/decisions/0006-what-proven-means.md). The `proof` check holds this table to the pages' proof marks, and takes a synced page's marks from `kit.lock.json`. A page of this workspace's own gets a row here too, and its `prove-by` names a milestone of this workspace's own plans.

<!-- kit: proof table -->

## License

The kit's code is under the MIT licence. See [LICENSE](LICENSE).
