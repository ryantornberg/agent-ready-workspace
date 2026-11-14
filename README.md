# agent-ready-workspace

A small, working example of a workspace for coding agents: one contract file, docs that are checked, a symbol lookup, a definition of done and a sample eval. Python standard library only, no install step.

A model brings general skill. A repository says what the code is today. Neither knows which repository a change belongs in, what your team already tried, or what you mean by an everyday word. A workspace writes that down, and checks that it stays true.

The longer description of the pattern is at [ryantornberg.com/workspace](https://ryantornberg.com/workspace/). This repository is the smallest version that runs.

## What is here

| Path | What it is |
|---|---|
| [AGENTS.md](AGENTS.md) | The contract: the rules and facts every agent reads, in one file for every tool. |
| [INDEX.md](INDEX.md) | Topics, and a table that maps everyday words to the names the code uses. |
| [docs/definition-of-done.md](docs/definition-of-done.md) | What evidence a finished change needs, and the report shape. |
| [docs/playbooks/fix-a-bug.md](docs/playbooks/fix-a-bug.md) | One procedure an agent can run on request. |
| [docs/decisions/](docs/decisions/0001-pin-code-repositories.md) | One decision record, as a template. |
| [docs/question-log.md](docs/question-log.md) | The questions the workspace failed to answer. |
| `checks/check_docs.py` | Fails on a broken link or heading anchor, and on an edit to a page past its review date. |
| `tools/symbols.py` | Returns the file and line where a name is defined. Python, C#, TypeScript and JavaScript. |
| [evals/](evals/README.md) | One eval case for the playbook and a grader for recorded runs. |

The team and the order system in the examples are invented.

## Try it

```
python3 -m unittest discover -b tests         # the tests for all three scripts
python3 checks/check_docs.py                  # check this repository's own docs
python3 tools/symbols.py check checks         # where is "check" defined?
python3 evals/grade.py evals/cases/fix-a-bug.json evals/transcripts/fix-a-bug.fail.json
```

The last command exits 1 on purpose: it grades a run that skipped the playbook.

To run the doc check before every commit:

```
git config core.hooksPath .githooks
```

CI runs the same check and the tests on Linux, macOS and Windows, so a teammate who never installed the hook is still caught after the push.

## Use it for your own team

1. Replace the facts in `AGENTS.md` with the ones a model gets wrong about your code. Leave out anything it gets right from the code alone.
2. Add your code repositories under `src/` as submodules.
3. Fill the alias table from the words your team actually says.
4. Write a playbook for the task you repeat most, and one eval case for it.
5. Start the question log. Each entry is a gap; fix the page, then note the fix.

Add more machinery only when you hit the problem it solves.

## Limits

- `symbols.py` matches declarations line by line for C#, TypeScript and JavaScript. It can miss a declaration split across lines.
- `check_docs.py` proves that nothing is dangling. It cannot prove a page is true.
- `grade.py` grades a transcript you recorded. It does not run a model.

## License

MIT. See [LICENSE](LICENSE).
