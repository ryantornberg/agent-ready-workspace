---
last-reviewed: 2026-11-15
---

# Changing the machinery

Docs change freely. The scripts, hooks and CI that check them take a stricter path. It is for anyone, person or agent, about to change one of them.

**In short:** a doc change goes straight to the main branch. A machinery change goes to its own branch and merges only after CI passes on Linux, macOS and Windows. Machinery work runs at the driver tier.

## What counts as machinery

| Path | What it is |
|---|---|
| `ws.py`, `wslib/` | The runner and its core |
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
5. **The person pushes the branch.** CI runs on three systems.
6. **Merge once CI is green.** A red run on any one system blocks the merge.

A hook that refuses a direct push of machinery to the main branch is planned. Until then this path is kept by hand.

## Traps

- **The hooks guard the session that edits them.** A part with a failing case is refused, and today every command loads every part. A broken case can then refuse every shell and edit call, including the one that repairs it. This happened while building M1's first slice. The [M1 hand-off plan](plans/m1-make-the-core-hold-weight.md) fixes it in slice 2. Until then:
  - change a part's code and its cases in one step, and run the cases before the next tool call;
  - if the session is locked out, the person repairs the file from their own terminal, where the agent's hooks do not run.
- **The staged manifest decides what the commit check runs.** A manifest that drops a part, staged with the change, switches that part off for the commit. Stage the manifest only when the change means it.
- **A check you cannot run in CI.** The `deny_list` check reads a private list from the file `WS_DENY_LIST` names, or from `~/.config/agent-ready-workspace/deny-list.txt`. CI has no list, so it warns and checks nothing. Commit on a machine that has the list.
