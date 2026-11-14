# agent-ready-workspace

A small, working workspace for coding agents. It holds what neither the model nor the code knows, and it checks that what it holds stays true. Python standard library only, no install step.

A model brings general skill. A repository says what the code is today. Neither knows which service is the live one, what your team calls things, or how you have agreed to finish work. A workspace writes that down. This one is built so that every rule in it is either checked by a part or tested by an eval, and so that adding a rule means adding one file.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/parts-dark.svg">
  <img src="assets/parts-light.svg" alt="The commit hook, CI and the agent's tool all call one runner. The manifest names the parts in use. The runner loads each part, refuses one with no cases, and gives each check a snapshot of the files and each hook one event.">
</picture>

The longer description of the pattern is at [ryantornberg.com/workspace](https://ryantornberg.com/workspace/). This repository is the smallest version that runs. The team and the order system in its examples are invented.

## Try it

```
python3 ws.py list          # the parts this workspace uses
python3 ws.py selftest      # every part's own cases
python3 ws.py check         # run the checks on this repository
python3 -m unittest discover -b tests
```

Then watch it refuse something:

```
echo '{"command": "git add -A"}' | python3 ws.py hook before-shell     # refused, exit 2
echo '{"path": "src/orders-service-v1/OrderService.cs"}' | python3 ws.py hook before-edit
python3 tools/symbols.py ReconciliationWorker src                      # file and line
```

Rename the class in `src/orders-api/ReconciliationWorker.cs` and `python3 ws.py check` fails, because the index still sends agents to the old name. Edit `docs/playbooks/fix-a-bug.md` and it fails again, because the playbook no longer matches its last passing eval run.

To run the checks before every commit:

```
git config core.hooksPath .githooks
```

## What is here

| Path | What it is |
|---|---|
| [AGENTS.md](AGENTS.md) | The contract: the rules and facts every agent reads, in one file for every tool. |
| [INDEX.md](INDEX.md) | Topics, and a table that maps everyday words to the names the code uses. |
| [workspace.json](workspace.json) | The manifest: which parts this workspace runs, and their settings. |
| `ws.py`, `wslib/` | The runner and the small core the parts plug into. |
| [parts/](docs/parts.md) | Four checks and two hooks, each one file plus its cases. |
| [docs/](docs/definition-of-done.md) | The definition of done, one playbook, one decision record, the question log. |
| [evals/](evals/README.md) | One eval case, a broken sample repository, and recorded runs of a real model with and without the playbook. |
| `tools/symbols.py` | Returns the file and line where a name is defined. |
| [src/](src/README.md) | A few sample code files for the checks and hooks to act on. |

## What is checked, and by what

| Rule | Enforced by | When |
|---|---|---|
| A link points at a real file and heading. | `links` check | Commit, CI |
| Whoever edits a page past its review date reviews it. | `freshness` check | Commit, CI |
| An alias in the index names something the code still defines. | `aliases` check | Commit, CI |
| A playbook changes only with a new passing eval run. | `eval_record` check | Commit, CI |
| Files are staged by name, never all at once. | `no_stage_all` hook | Before a shell command |
| A shelved folder is not edited. | `shelved` hook | Before an edit |
| A part has cases that show it working. | The runner | Every run |

The commit check reads the staged snapshot, not the folder, so another session's unsaved edits cannot make a commit pass or fail. CI runs the same checks on Linux, macOS and Windows and treats every file in the push as changed, so a teammate who never installed the hook is still caught.

## Add a part

A part is one Python file and one file of cases. [docs/parts.md](docs/parts.md) has the two interfaces and a worked example of each. In short:

```python
# parts/no_empty_pages.py
from wslib.parts import finding

KIND = "check"


def run(snapshot, config):
    return [finding(path, 1, "this page is empty")
            for path in snapshot.paths(suffixes=(".md",))
            if not (snapshot.read(path) or "").strip()]
```

```json
[{"name": "an empty page fails", "files": {"a.md": "", "b.md": "# B"}, "expect": ["this page is empty"]}]
```

Save the cases as `parts/no_empty_pages.cases.json`, add `{"use": "no_empty_pages"}` to `workspace.json`, and it runs at commit and in CI. Without the cases file the runner refuses to load it.

## The eval

The playbook says: reproduce the bug before you edit, and mark each claim in your report as verified or inferred. [evals/](evals/README.md) tests whether saying so changes anything. It gives a real model a small broken repository and the request "The Export button on the orders page does nothing. Fix it and commit the fix", once with the playbook and once without.

In the recorded run, on a small model, the run with the playbook passed all six graders. The run without it passed four: it edited the code before it had seen a test fail, and its report did not mark a claim as verified. Both runs staged by name and left another session's edits out of the commit, so those two graders show a habit the model already has. It is one run per arm, which shows the mechanism and is not a measurement. The transcripts are in [evals/runs/](evals/runs/fix-a-bug/record.json).

## Use it for your own team

1. Replace the facts in `AGENTS.md` with the ones a model gets wrong about your code. Leave out anything it gets right from the code alone.
2. Put your code repositories under `src/` as submodules, and remove the samples.
3. Fill the alias table from the words your team actually says.
4. Write a playbook for the task you repeat most, and one eval case for it.
5. Start the question log. Each entry is a gap; fix the page, then note the fix.

Add a part when the same mistake shows up twice.

## Limits

- **`symbols.py` reads C#, TypeScript and JavaScript one line at a time.** It finds types, methods, constructors, properties, functions and constants declared on one line in the usual style. It misses a declaration split across lines, a C# field or event, a TypeScript arrow function assigned inside a class, and anything generated at build time. It can report a declaration that sits inside a multi-line string.
- **`links` reads the common ways to link**: inline links and images, reference definitions, and HTML `href`, `src`, `id` and `name`. It does not read autolinks or headings produced by HTML tags. Its anchors follow GitHub's rules as I understand them; another renderer may differ.
- **The checks prove that nothing is dangling. They cannot prove a page is true.** A page that contradicts last week's decision passes every one.
- **The hooks are wired for one agent tool** ([.claude/settings.json](.claude/settings.json)). The parts do not depend on it; another tool needs a few lines to call `ws.py hook`.
- **`no_stage_all` reads a command line; it does not run a shell.** A command built by a script, or hidden in an alias, gets past it. The eval's check on what was actually committed does not depend on it.
- **The eval is one case, one model, one run per arm.** `evals/run.py` drives one agent tool.

## License

MIT. See [LICENSE](LICENSE).
