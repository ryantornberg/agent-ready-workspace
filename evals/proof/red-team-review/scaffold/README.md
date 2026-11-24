# Workspace hooks

Two hooks a workspace runs for its agents: the before-edit hook, which refuses an edit inside the shelved folder, and the writing-session lease, which lets one session at a time write in the main working copy. Their hand-off plans are in `docs/plans/`.

Run the tests with `python3 -m unittest`.
