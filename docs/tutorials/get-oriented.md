---
kind: tutorial
last-reviewed: 2026-11-23
---

# Get oriented

A thirty-minute walk for a newcomer with no agent: set up the workspace, find code three ways, run the checks, watch a guard refuse.

**In short:** run each block below, in order, from the top folder of a clone. You wire the git hooks, answer one where-is question with three lookups, run the checks, watch a guard remind and refuse, break a link on purpose and see the check catch it, then read the map. Nothing you run changes the workspace for anyone else.

## Before you start

You need a clone of this repository, git, and Python 3.9 or later. On Windows, run the blocks in the bash that comes with Git for Windows. Open a terminal at the clone's top folder; every block runs from there.

Every block below runs as written. CI runs each one, in order, in a fresh clone on Linux, macOS and Windows, so a block that stops working fails the build. A line starting with `#` is a comment for you.

## 1. Set it up

<!-- runnable -->
```sh
# Send python3 through the workspace's launcher, which finds a good Python even where none is named python3, as on Windows.
python3() { bash wslib/launch.sh "$@"; }
python3 ws.py --version
python3 ws.py selftest
git config core.hooksPath .githooks
git config core.hooksPath
```

The first two lines make `python3` in this terminal start the workspace's launcher, as every hook does; keep the terminal open for the steps below. The next prints the engine's version. `selftest` runs every part's own cases: each check and hook is a small Python file with cases that show it refusing and allowing. The last two lines point git at the workspace's own hooks, and print the setting back: from now on, every commit and push in this clone runs the checks first. The README's [Try it](../../README.md#try-it) section holds the same setup.

## 2. Find the nightly job three ways

People here say "the nightly job". Where is it? Each lookup below answers from a different starting point.

<!-- runnable -->
```sh
# 1. You have an everyday word: look it up in the index's search aliases.
grep -n -i "nightly" INDEX.md
# 2. You have the exact name the code uses: ask for its file and line.
python3 tools/symbols.py ReconciliationWorker src
# 3. You have only a fragment of text that is not a name: search the tracked files.
git grep -n "once a night" -- src
```

The first lookup turns the everyday word into the name the code uses, `ReconciliationWorker`. The second goes straight to the file and line. The third finds any text, here a phrase from the class's comment, and is the slowest to read on a large codebase. Pick the one that fits what you already know, and do not stack them: the [research ladder](../research-ladder.md) says which to use when.

## 3. Run the checks

<!-- runnable -->
```sh
python3 ws.py check
```

`check` runs every check on the clone: links resolve, pages carry their front matter, the index's aliases name code that exists, and more. It may print a warning that fix a bug's eval record was not compared with an earlier one. A plain check has no earlier commit to compare with, so that is expected; a warning does not fail the run. Each finding names the file, the page that holds its rule, and how to re-run it.

## 4. Watch a guard remind, then refuse

An agent's tool calls pass through hooks before they run. You can call a hook by hand with a made-up event, as an agent tool would. Nothing runs and nothing changes.

<!-- runnable -->
```sh
# A reminder: staging everything at once lets through other people's edits.
echo '{"version": 1, "command": "git add -A"}' | python3 ws.py hook before-shell
# A refusal: the old order service is kept read-only, so an edit to it is refused.
echo '{"version": 1, "path": "src/orders-service-v1/OrderService.cs"}' | python3 ws.py hook before-edit && exit 1 || echo "Refused, as expected."
```

The first hook prints a reminder and lets the command through. The second refuses with exit code 2 and names its reason. The `&& exit 1` stops this walk-through if the guard ever lets that edit through. The [README's checks table](../../README.md#what-is-checked-and-by-what) lists every guard.

## 5. Break a link on purpose

Make a mistake, see the check catch it, then undo it. The mistake goes in a new page of its own, so no page you or anyone else is editing changes.

<!-- runnable -->
```sh
printf '# Practice\n\nSee [a page that is not there](not-there.md).\n' > docs/practice-broken-link.md
python3 ws.py check 2>&1 | grep "\[links\]"
rm docs/practice-broken-link.md
```

The first line writes a small page with a broken link. The check's output names it, with the `links` check in brackets; the `grep` keeps only that line. The check also says the page has no front matter, which every page here needs. `rm` deletes the practice page, so the clone is as it was. With the hooks from step 1, a commit holding that page would have been refused the same way.

## 6. Learn the map

You have now used most of the workspace's entry points. Read these next, in this order:

| Page | What it is for |
|---|---|
| [AGENTS.md](../../AGENTS.md) | The contract every agent reads first: where things live, the facts a model cannot work out, and the rules. |
| [INDEX.md](../../INDEX.md) | Every topic, and the everyday words mapped to the code's names, as in step 2. |
| [The playbook catalog](../playbooks/README.md) | Which procedure to follow for a task, and whether it is proven. |
| [The how-to index](../how-tos.md) | Tasks that are not playbooks, such as committing or adding a check. |
| [The glossary](../glossary.md) | The words this workspace uses in one sense only. |
| [The question log](../question-log.md) | Questions the workspace failed to answer. Add yours. |

Next, run your first task with an agent: [your first agent task](first-agent-task.md).
