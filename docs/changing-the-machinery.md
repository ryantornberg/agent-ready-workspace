---
last-reviewed: 2026-11-15
---

# Changing the machinery

Docs change freely. The scripts, hooks and CI that check them take a stricter path. It is for anyone, person or agent, about to change one of them.

**In short:** a doc change goes straight to the main branch. A machinery change goes to its own branch and merges only after CI passes on Linux, macOS and Windows. Machinery work runs at the driver tier.

## What counts as machinery

| Path | What it is |
|---|---|
| `ws.py`, `wslib/` | The engine: `wslib/` holds its code, and `ws.py` starts it. See [decision 0003](decisions/0003-the-engine-in-one-folder.md). |
| `parts/` | Every check and hook, and their cases |
| `tools/` | Lookups such as `symbols.py` |
| `evals/*.py`, `evals/cases/` | The eval harness, the graders and the cases |
| `workspace.json` | The manifest: which parts run, and the tier binding |
| `.githooks/`, `.github/`, `.claude/settings.json` | The commit hook, CI and the agent tool's wiring |
| `tests/` | The tests of all of the above |

Everything else is a doc.

## The path for a machinery change

1. **Branch.** Name it after the work, such as `m1/slice-2`.
2. **Write the failing case first.** A part's case, or a test in `tests/`, that fails without the change.
3. **Run the three commands** and keep their output for the report:

   ```
   python3 ws.py selftest
   python3 ws.py check
   python3 -m unittest discover -b tests
   ```

4. **Commit on the branch**, staging files by name.
5. **Push the branch and open a draft pull request.** CI runs on three systems. In this repository an agent may push; in a team's workspace, a person does.
6. **Merge once CI is green.** A red run on any one system blocks the merge.

A hook that refuses a direct push of machinery to the main branch is planned. Until then this path is kept by hand.

## Traps

- **The hooks guard the session that edits them.** A part with a failing case is refused. A hook call loads only the hooks for its event, so a broken check no longer refuses anything, and a broken hook refuses only its own event: with a broken shell hook, the edit tools still work. Four things still refuse every hook call, because the runner cannot tell whether a hook would refuse: a manifest it cannot read, a manifest whose `version` differs from the engine's, a part file that is missing, and a part whose `KIND` line it cannot read. A manifest entry with no `why`, or an unknown key, fails every other command but does not refuse a hook call. [Parts](parts.md#a-hook) says how a part declares its kind.
  - Change a part's code and its cases in one step, and run `python3 ws.py selftest` before the next tool call.
  - If the session is locked out, the person repairs the file from their own terminal, where the agent's hooks do not run.
  - Change the engine's `VERSION` and the manifest's `version` in one step: on a branch in its own working copy, then a merge or a checkout. Edited one at a time in the working copy the session runs in, they lock the session out.
- **A part leaves the manifest only by being retired.** A manifest that drops a part the last commit used fails `check`, and in CI the base branch's manifest decides. List the part under `retired` with a reason. See [removing a part](parts.md#removing-a-part).
- **A check you cannot run in CI.** The `deny_list` check reads a private list from the file `WS_DENY_LIST` names, or from `~/.config/agent-ready-workspace/deny-list.txt`. CI has no list, so it warns and checks nothing. Commit on a machine that has the list.
