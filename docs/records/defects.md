---
kind: record
last-reviewed: 2026-11-22
---

# Defect register

Defects found in passing, kept until each is fixed or accepted, in the shape the [defect register template](../templates/defect-register.md) gives.

## Open

| Found | Where | What | Evidence | State |
|---|---|---|---|---|
| 2026-11-23 | `docs/orchestration.md`, "The binding" | It says the `tiers` entry is "the only place a model name appears", but the eval harness sets its own model with `--model`, and `evals/README.md` names models in its commands. | Read `evals/run.py`'s argument handling and `evals/README.md` at `dace91e`; found by slice B5's review of decision 0014, which now says the binding is the only place a tier's model is set. | open |
| 2026-11-23 | `.gitignore`, beside `secrets_shell`'s `"file": ".env"` in `workspace.json` | The secrets file `ws.py with-secrets` reads, `.env` at the top of the main working copy, is not ignored by git, so a person's `git add -A` there would stage their tokens; the secret scan at the commit is the only stop. | `git check-ignore -q .env` exits 1 in the m3-b5 worktree at `dace91e`; `.gitignore` lists no `.env` pattern. Found by slice B5's review of decision 0001. | open |

## Closed

| Found | Where | What | Evidence | Closed | How |
|---|---|---|---|---|---|
