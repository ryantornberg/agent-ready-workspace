#!/usr/bin/env python3
"""Run a workspace's parts. The manifest, workspace.json, says which parts this workspace uses.

    python3 ws.py list                       # the parts, their kind and how many cases each has
    python3 ws.py selftest                   # run every part's own cases and report each failure
    python3 ws.py check                      # run the checks on the working folder
    python3 ws.py check --staged             # run them on exactly what is staged (the commit hook)
    python3 ws.py check --changed-from REF   # treat files edited since REF as changed (CI)
    python3 ws.py hook before-shell          # decide one event in the workspace's shape, read as JSON on standard input
    python3 ws.py hook before-edit --tool claude-code   # the same, from one agent tool's own payload
    python3 ws.py baseline                   # record the checks' current errors as tolerated, in baselines/
    python3 ws.py check --message FILE       # check a commit message and the commit's identities (commit-msg hook)
    python3 ws.py ledger                     # this working copy's edit ledger: open or closed, and its paths
    python3 ws.py ledger --add PATH ...      # record files this session wrote another way, by name
    python3 ws.py ledger --close             # close it, for a person's own commit
    python3 ws.py ledger --committed         # drop the last commit's paths (the post-commit hook)
    python3 ws.py merge NUMBER               # merge a pull request with a merge commit, once CI passed on its head
    python3 ws.py handoff NOTE               # mark NOTE as this branch's handoff note, shown at the next session start
    python3 ws.py handoff --done             # clear this branch's handoff marker (--done BRANCH: another branch's)
    python3 ws.py handoff                    # list this working copy's handoff markers, pending or merged
    python3 ws.py with-secrets NAME -- PROGRAM ...   # run PROGRAM with NAME from the secrets file, in its environment only

The engine is the folder wslib/; this file only starts it. wslib/runner.py says how the commands work.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from wslib.runner import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
