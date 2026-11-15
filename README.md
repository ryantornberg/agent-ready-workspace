# agent-ready-workspace

A small, working workspace for coding agents. It holds what neither the model nor the code knows, and it checks that what it holds stays true. Python standard library only, no install step.

A model brings general skill. A repository says what the code is today. Neither knows which service is the live one, what your team calls things, or how you have agreed to finish work. A workspace writes that down. Where a machine can check one of its rules, a part checks it, and the table below says which rules those are and which stay prose. Adding a check means adding one part: a file, its cases and a line in the manifest.

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

Rename the class in `src/orders-api/ReconciliationWorker.cs` and `python3 ws.py check` fails, because the index still sends agents to the old name. Edit `docs/playbooks/fix-a-bug.md` and it fails again, because the playbook no longer matches its last passing eval run. Both changes are easy to undo with `git checkout`.

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
| [parts/](docs/parts.md) | Five checks and two hooks, each one file plus its cases. |
| [docs/](docs/definition-of-done.md) | The definition of done, one playbook, one decision record, the question log, the orchestration rules, and the templates and plan for the current milestone. |
| [evals/](evals/README.md) | One eval case, a broken sample repository, and five recorded runs each of a real model with and without the workspace's guidance. |
| `tools/symbols.py` | Returns the file and line where a name is defined. |
| [src/](src/README.md) | A few sample code files for the checks and hooks to act on. |

## What is checked, and by what

| Rule | Enforced by | When |
|---|---|---|
| A link points at a real file and heading. | `links` check | Commit, CI |
| Whoever edits a page past its review date reviews it. | `freshness` check | Commit, CI |
| An alias in the index names something the code still defines. | `aliases` check | Commit, CI |
| A playbook, and the guidance tested with it, changes only with a new passing eval run. | `eval_record` check | Commit, CI |
| No file holds a term from the maintainer's private deny list. | `deny_list` check | Commit, on a machine that has the list |
| Files are staged by name, never all at once. | `no_stage_all` hook | Before a shell command |
| A shelved folder is not edited. | `shelved` hook | Before an edit |
| A part's own cases pass. | The runner | Every command: a part with a failing case is refused |

The commit check reads the staged pages and the staged manifest, not the folder, so another session's unsaved edits to them cannot make a commit pass or fail. The parts' own code runs from disk. CI runs the same checks on Linux, macOS and Windows and compares with the commit before the push, so a teammate who never installed the hook is still caught. The one exception is `deny_list`, which needs a private list that CI does not have. When CI has nothing to compare with, such as a first push or a force push, it treats every file as changed.

These rules in [AGENTS.md](AGENTS.md) and the [definition of done](docs/definition-of-done.md) stay prose, because nothing here can check them: open pull requests only as drafts, write a goal and non-goals for larger work, log the questions you had to ask, compare build warnings with the base branch, and list the callers you checked. The eval tests two more: see a test fail before editing, and mark claims as verified.

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

Save the cases as `parts/no_empty_pages.cases.json`, add `{"use": "no_empty_pages"}` to `workspace.json`, and it runs at commit and in CI. Without the cases file, or with a case that fails, the runner refuses to load it.

## The eval

The playbook says: reproduce the bug with a failing test before you edit, and mark each claim in your report as verified or inferred. [evals/](evals/README.md) tests whether saying so changes anything. It gives a real model a small broken repository and the request "The Export button on the orders page does nothing. Fix it and commit the fix", once with the workspace's guidance and once without.

In the recorded runs, five of each on a small model, every run with the guidance passed all six graders. Every run without it failed the same two: it edited the code before it had seen a test fail, and its report did not mark a claim as verified. All ten runs fixed the bug, staged by name and left another session's edits out of the commit, so those graders show habits this model already has. Ten runs on one small bug is a demonstration, not a benchmark. The transcripts are in [evals/runs/](evals/runs/fix-a-bug/record.json).

## Use it for your own team

1. Replace the facts in `AGENTS.md` with the ones a model gets wrong about your code. Leave out anything it gets right from the code alone.
2. Put your code repositories under `src/` as submodules, and remove the samples. Add `submodules: true` to the checkout step in `.github/workflows/ci.yml`.
3. Fill the alias table from the words your team actually says.
4. Write a playbook for the task you repeat most, and one eval case for it.
5. Start the question log. Each entry is a gap; fix the page, then note the fix.

Add a part when the same mistake shows up twice.

## Limits

- **`symbols.py` reads C#, TypeScript and JavaScript one line at a time.** It finds types, methods, constructors, properties, functions and constants declared on one line in the usual style. It is a lookup for names you already know, not a parser. It misses a declaration split across lines or behind an attribute; C# fields, events, delegates, indexers and operators; TypeScript class fields, getters, one-line method bodies and CommonJS exports; Python module-level constants; and anything generated at build time. It can report a declaration that sits inside a multi-line string.
- **`links` reads the common ways to link**: inline links and images, reference definitions, and HTML `href`, `src`, `srcset`, `id` and `name`. It does not read autolinks, headings inside list items, headings produced by HTML tags, or the second candidate in a `srcset`. It checks links inside HTML comments and indented code blocks, and it reads `a[0][1]` in prose as a reference link; put such text in backticks. Its anchors follow GitHub's rules as I understand them; another renderer may differ.
- **The checks prove that nothing is dangling. They cannot prove a page is true.** A page that contradicts last week's decision passes every one.
- **The hooks are wired for one agent tool** ([.claude/settings.json](.claude/settings.json)), and that wiring calls `python3`, which a stock Windows machine may not have. The parts do not depend on it; another tool needs a few lines to call `ws.py hook`.
- **`no_stage_all` reads a command line; it does not run a shell.** It follows separators, new lines, subshells, `sh -c`, `eval` and common wrappers, and it skips heredoc bodies and quoted text. A command built by a script, held in a variable, hidden in an alias or piped into a shell gets past it, and it cannot tell that `git add src` names a whole folder. The eval's check on what was actually committed does not depend on it.
- **`shelved` guards the edit tools only.** A shell command that writes into the folder, such as `sed -i` or `git mv`, does not pass through it, and neither does an edit through a symbolic link that points into it.
- **`aliases` is strict about its table and loose about what counts.** Each row needs exactly two columns, the second one plain name in backticks; a linked name or a second table under the heading is an error. Any definition of that name under `src/` satisfies it, including a method that happens to share the name.
- **The commit check reads a submodule from its checkout on disk**, not from the commit the index pins. Run `git submodule update` before committing a pin change, and initialise submodules before the first check.
- **`eval_record` trusts the record file.** It shows that someone ran the case on the current wording. It cannot stop a person from editing the record by hand. Changing a playbook's wording means running the eval again, which needs the agent tool and costs a few cents; moving its review date does not.
- **Review dates run out.** Every dated page here was reviewed on the same day. About six months later a first push or a force push, where CI treats every file as changed, fails until the pages are reviewed and their dates moved.
- **The eval is one case and one model, five runs per arm.** `evals/run.py` drives one agent tool.

## License

MIT. See [LICENSE](LICENSE).
