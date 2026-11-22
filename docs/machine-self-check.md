---
kind: how-to
proof: unproven
prove-by: M5
last-reviewed: 2026-11-22
---

# Machine self-check

A prompt a person pastes into their agent to check that their machine runs this workspace's hooks, checks and tools.

**In short:** paste the prompt below into an agent session at the top of the workspace. The agent runs ten checks and a few optional extras, all of which change nothing, reports each as pass, fail or skipped, then offers fixes one at a time. A machine fix stays on your machine; a fault in the workspace is reported as a bug, and a failure from uncommitted edits as work in progress.

## When to run it

- After setup: once the marked setup steps in the README's [Try it](../README.md#try-it) have run, or a team's own setup in [Use it for your own team](../README.md#use-it-for-your-own-team).
- After the machine changes: a new Python, git, operating system or agent tool version.
- When a guard seems not to run: a commit went through that a check should have refused, or a session saw no refusal where one was due.

`python3 ws.py selftest` is one step inside the self-check, step 8. The self-check also checks the machine and the wiring around the workspace. Run selftest alone when you changed a part and want only its cases.

## The prompt

Paste this into an agent session whose working folder is the top of the workspace, the main working copy or a worktree:

```
Run the machine self-check in docs/machine-self-check.md. Follow its steps in order, in this session; hand nothing to a helper. Change nothing until you have given me the report. Then offer each fix one at a time, and make one only when I say yes.
```

## Steps

The agent runs every step in its own session and hands nothing off. Every command below reads only, or writes only to a temporary folder outside the workspace. When a step fails, the default is to note it and go on to the next step. A step that needs something an earlier step found missing is marked skipped, with the reason.

**When every shell command is refused.** The shell tool's own hook starts Python through the launcher. With no Python 3.9 or later, or a launcher with CRLF endings or no execute bit, that hook refuses every command, with an error from the launcher or the shell rather than a message that starts `Refused by`. Then give the person the commands of steps 1 to 5 to run in their own terminal, and record each step's result from the output they paste back, as that step says. Step 5's result is the launcher's error, a fail. Mark steps 6 to 11 skipped, with the reason "every shell command is refused", and mark skipped any of steps 1 to 4 whose output the person does not give. Then go on to the report.

**Work in progress.** The self-check may run in a working copy with uncommitted edits, a worktree included. In steps 6, 8 and 9, a failure that comes from those edits, such as a link to a page that is not committed yet, is work in progress, not a bug. It goes on the report's "Work in progress" line, and its step's result is still fail. `git status --short` lists the edits.

1. **Tools.** Input: the session's shell, at the top of the workspace. Run `python3 --version`, `git --version` and `gh --version`. Where `python3` is missing, as on some Windows machines, try `python --version` and `py --version`, which the launcher also tries, and use the name that works in the later steps. On Windows, confirm that the bash that comes with Git is installed: the hook wiring needs a POSIX shell. Pass: Python 3.9 or later, and git. Output: each tool's version, or "missing". A missing `gh` is a note, not a fail: it is needed only for work on GitHub: opening, reading and merging pull requests, including `python3 ws.py merge`, and reading their CI. If no Python 3.9 or later is found, mark steps 5 to 10 skipped and go on to step 2.
2. **Line endings.** Input: the checkout. Run `git ls-files --eol | grep "w/crlf"`. Pass: no output, so every file is checked out with the LF endings `.gitattributes` asks for. Fail: the files it lists. A shell script with CRLF endings, such as `wslib/launch.sh`, does not run, so every guard refuses. Output: pass, or the list. Class: machine setup. Something on the machine rewrote the endings, often an editor setting.
3. **Git hooks.** Input: the checkout. Run `git config core.hooksPath`. Pass: it prints `.githooks`. Fail: no output, so the commit, commit message and push checks never run on this machine, and only CI catches a bad commit, after the push. On Linux and macOS, also run `ls -l .githooks wslib/launch.sh`. Pass: each file shows `x` in its mode; git skips a hook file that is not executable. Output: pass, or what is missing. Class: machine setup.
4. **Agent tool wiring and local overrides.** Input: the agent tool this session runs in. Claude Code reads its hooks from `.claude/settings.json`, and Codex CLI from `.codex/hooks.json`. For Claude Code, run `grep -ns disableAllHooks .claude/settings.local.json ~/.claude/settings.json`. Pass: no line that sets it to `true`. Also list any `hooks` or `permissions` entries in `.claude/settings.local.json`: a local file can loosen the committed settings, as [agent settings](agent-settings.md#limits) says. For Codex CLI, ask the person whether they have trusted the project and reviewed its hooks with `/hooks`; until they have, no hook runs. Default: with no answer, mark it unknown; step 7 shows the result either way. Output: each override found, or none. Class: machine setup.
5. **The launcher.** Input: Python from step 1. Run `wslib/launch.sh ws.py --version`. It starts Python the way every hook, git hook and CI step does. Pass: it prints the engine's version. Fail: "no Python 3.9 or later on the path", with exit code 2, means every guard refuses every call; "permission denied" means the launcher is not executable, as in step 3. Output: the version, or the error. Class: machine setup for those two errors; any other error is a workspace bug.
6. **Hook replay.** Input: a working launcher. Run `python3 tests/hook_cases.py`. It builds scratch repositories in a temporary folder and calls every hook event through each agent tool's real wiring, with that tool's own payload, and times each call. It takes about a minute. Pass: the last line reads `<n> of <n> cases pass`. Fail: each failing case is named. Output: the count, and each failing case. Class: work in progress when the failure comes from uncommitted edits; otherwise a workspace bug when steps 1 to 5 passed, or the earlier step's cause when one failed.
7. **Proof that a hook fires in this session.** Input: this session's own shell tool. Steps 5 and 6 call the wiring by hand; this step shows that the agent tool itself calls it. Run `: >> .git/HEAD` through the session's shell tool. Pass: the call is refused, with a message that starts `Refused by git_folder_shell`. Fail: the command runs with no refusal, so this session's hooks are off. The command writes no content either way: `:` writes nothing, so the file keeps its content, and in a worktree, where `.git` is a file, the command only fails. Output: the refusal, or what ran. Class: machine setup when step 4 found an override or an untrusted project; otherwise a workspace bug.
8. **Script tests.** Input: Python from step 1. Run `python3 ws.py selftest`, then `python3 -m unittest discover -b tests`. Selftest runs every part's own cases, in about a second. The tests take a minute or two. Pass: every part is listed `ok`, and the tests end with `OK`; skipped tests are allowed. Output: both results, and each failure. Class: work in progress when the failure comes from uncommitted edits; machine setup when it names a tool step 1 found missing; otherwise a workspace bug.
9. **Commit gates.** Input: Python from step 1. Run `python3 ws.py check`, then `sh .githooks/pre-commit`. The first runs every check on the working folder. The second runs the git hook's own command on what is staged, as a commit would. Pass: both exit 0; a warning does not fail. Output: both results, and each finding. Class: a finding on a file with uncommitted edits is work in progress, reported as such, not a bug; a finding on a committed file is a workspace bug.
10. **Lookup.** Input: Python from step 1. Run `python3 tools/symbols.py ReconciliationWorker src`. Pass: it prints `src/orders-api/ReconciliationWorker.cs` and a line number. In an instance, use a name from your own code, such as one from [INDEX.md's search aliases](../INDEX.md#search-aliases). Fail: no output. Output: the file and line, or nothing. Class: in an instance, first run step 11's pin check, since a pinned repository that is not checked out holds no names; otherwise a workspace bug.
11. **Extras.** Input: Python and git from step 1. Default: run all three; each reads only.
    - GitHub: `gh auth status`. Pass: signed in. Needed for every `gh` call on GitHub, such as opening, reading or merging a pull request and reading its CI.
    - Pinned code repositories: `git submodule status`. Pass: no line starts with `-`; such a line is a repository that is not checked out. This sample pins none, so no output passes.
    - A browser for agent sessions: `npx --version`, since the browser server starts through it, as [browsers](browsers.md) says. Pass: a version.

    Output: each result. Class: machine setup.

Stop running checks when step 11 is done, and give the report.

## The report and the fixes

Give the report in the session's reply, with each claim marked verified or inferred, as [the definition of done](definition-of-done.md#the-report) says. A step's result is verified when you ran its command and saw the output. A cause you name for a failure is inferred unless a command showed it.

```
Machine self-check: <n> pass, <n> fail, <n> skipped

| Step | Result | Evidence |
|---|---|---|
| 1 Tools | pass | Python 3.12.1, git 2.45.0, gh not found (a note) |
| 3 Git hooks | fail | core.hooksPath is not set |

Machine setup fixes: <one line each, or none>
Workspace bugs: <one line each, or none>
Work in progress: <step and finding, one line each, or none>
Skipped: <step, and why>
Changed: nothing.
```

Then offer the fixes, one at a time, machine setup first, since one may explain a later failure.

- **A machine setup fix**, such as `git config core.hooksPath .githooks` from the README's setup, an install or a setting, is made on the person's machine, and only on their yes. It is never committed. After each fix, run its step again and say the new result.
- **A workspace bug** is reported, not fixed in this run. If the person says yes to fixing it, the fix starts at the [size gate](size-the-work.md#the-gate): a small change goes to fix a bug, or to [extend the workspace](extend-the-workspace.md) when it changes pages only, and the rest climbs the ladder; a change to scripts, parts, hooks or CI follows [changing the machinery](changing-the-machinery.md).
- **With no answer**, make no fix. The report stands as given.

Work in progress is not a fix to offer: it clears when those edits are finished or committed.

Stop when every fix offered is made or declined and each step run again has its result reported. Nothing this how-to does is committed, except a question-log entry; the last line of the report says what was changed on the machine, or nothing. If you had to ask a person something this workspace should have answered, add it to the [question log](question-log.md) before you finish, and commit it as that page says.

## Rules

| Rule | Enforced by |
|---|---|
| Change nothing until the report is given. | `prose` |
| Run every step in the person's own session; hand nothing off. | `prose` |
| Offer fixes one at a time, and make one only on the person's yes. | `prose` |
| A fix to the person's machine is never committed. | `prose` |
| A workspace bug is reported, not fixed in this run without the person's yes; its fix starts at the size gate. | `prose` |
| If you had to ask a person something this workspace should have answered, add it to the question log before you report, and commit it as that page says. | `prose` |
| Mark every claim in the report verified or inferred. | `eval:fix-a-bug` |
