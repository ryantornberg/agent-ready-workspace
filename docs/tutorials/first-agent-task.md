---
kind: tutorial
last-reviewed: 2026-11-23
---

# Your first agent task

A newcomer's forty-five-minute first task with an agent, on a practice branch: a research question, a one-row change, the diff, the checks, a commit.

**In short:** put the practice on a branch of its own, start an agent, and ask it where the nightly job lives. Check its answer yourself. Have it add one row to the question log and commit it on the branch, then review the diff and run the checks yourself. Reflect on how it worked, then delete the branch, so nothing reaches main.

## Before you start

Run [get oriented](get-oriented.md) first. You need an agent tool this workspace supports: Claude Code, or Codex CLI on Linux or macOS. On Windows, use Claude Code: Codex CLI there cannot take the lease an agent's edit needs, as [decision 0005](../decisions/0005-concurrent-sessions-and-the-edit-ledger.md) says, so its edit in step 4 is refused. Run the blocks in the bash that comes with Git for Windows.

Run this tutorial in a clone no other agent session is working in, such as a fresh clone in a scratch folder, set up as get oriented's [step 1](get-oriented.md#1-set-it-up) says, in the same terminal. Everything stays on a practice branch that you delete at the end, and the agent is told not to push.

The blocks marked as yours run as written; CI runs each one, in order, in a fresh clone on Linux, macOS and Windows. The prompts you paste into the agent are shown as plain text.

## 1. Make a practice branch

<!-- runnable -->
```sh
git switch -c practice-first-task
git branch --show-current
```

The second line prints `practice-first-task`. Your commit in step 4 lands here, never on main.

## 2. Start the agent

Open the agent tool in the clone's top folder: `claude` for Claude Code, or `codex` for Codex CLI. It reads [AGENTS.md](../../AGENTS.md) at the start, through `CLAUDE.md` for Claude Code, and natively for Codex CLI. Codex CLI runs the project's hooks only once you trust the project and review its hooks with `/hooks`; do both first, as the [machine self-check](../machine-self-check.md) says.

## 3. Ask a research question

Paste this:

```text
Where does the nightly job live? Give the file and the line, and the page that told you where to look. Change nothing.
```

Watch how it gets there. A good answer goes from the everyday words to the index's search aliases, finds the name `ReconciliationWorker`, then asks for that name's file and line. A weak one searches every file for "nightly". The contract's "Finding things" section tells it which lookup fits.

Check its answer yourself:

<!-- runnable -->
```sh
python3 tools/symbols.py ReconciliationWorker src
```

Its file and line should match what the agent said. Each claim in its reply should be marked verified, when it ran something and saw the result, or inferred, when it reasoned its way there.

## 4. Make a one-row change

Paste this, with today's date:

```text
Add one row to the table in docs/question-log.md: date <today>, the question "Practice: where does the nightly job live?", kind "could not find", and where the answer lives now, INDEX.md's search aliases. Commit it on the current branch with a conventional commit subject, staging the file by name. Do not push.
```

Watch whether it ends the way [procedure endings](../procedure-endings.md#the-commit) says a commit ends: the file staged by name, a subject in the form [commits](../commits.md) gives, and no `Instructions-review:` trailer, since the question log is a record, not a guidance page. If its commit is refused, that page says what it should do; it should never work around the refusal.

## 5. Review the diff

<!-- runnable -->
```sh
git status --short
git log --oneline -3
git show --stat HEAD
```

`git status --short` should print nothing: the agent committed its change and left nothing behind. The log's top line is its commit. `git show --stat HEAD` should name one file, `docs/question-log.md`, with one line added. Run `git show HEAD` to read the row itself. If the agent changed anything else, ask it why before you go on.

## 6. Run the checks yourself

<!-- runnable -->
```sh
python3 ws.py check
```

The commit hook already ran these, but run them once yourself: an agent's "the checks pass" is a claim until you see it. The warning about fix a bug's eval record is expected, as in [get oriented](get-oriented.md#3-run-the-checks).

## 7. Reflect

Answer these for yourself, in a sentence each:

- **Steer:** where did your prompt leave the agent to guess? What one line would have saved it a step?
- **Review:** did the diff hold only what you asked for? Did you read it before you trusted the reply?
- **Verify:** which of its claims did you check yourself, and which did you take on its word?

If you had to ask a person something this workspace should have answered, that is a real row for the [question log](../question-log.md), on main, not on this branch.

## 8. Clean up

<!-- runnable -->
```sh
git checkout -q -
git branch -D practice-first-task
git status --short
```

The first line goes back to where you were before step 1. The second deletes the practice branch, with its commit. `git status --short` prints nothing.

For your first real task, start from [the kickoff prompt](../question-log.md#the-kickoff-prompt), and follow [procedure endings](../procedure-endings.md) for how it ends.
