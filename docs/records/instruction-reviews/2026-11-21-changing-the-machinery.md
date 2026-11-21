---
kind: record
last-reviewed: 2026-11-21
covers: docs/changing-the-machinery.md
reviewed-at: 166bbc7
---

# Instruction review: docs/changing-the-machinery.md

Review of the rules table that M3 sub-batch A added to the machinery page, for its author and the next agent who follows it.

**In short:** 3 findings: 2 enforcement, 1 step. Two tags claim more than they show, and one required scan has no command to run it.

## Scope

In scope: the Rules table that sub-batch A added, its five rows, each row's tag, and how each row agrees with the rest of the page. I read the whole page and its sub-batch A diff. Beside it I read `AGENTS.md`, `INDEX.md`, `workspace.json`, the parts `direct_push`, `no_admin_merge`, `eval_record`, `deny_list` and `rules` with their cases, `wslib/runner.py`, `wslib/parts.py`, `tests/test_core.py`, `.githooks/`, the CI workflow, and the register from `python3 ws.py rules`. The review is of commit 166bbc7. Uncommitted edits by another session in the working copy were not reviewed.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | enforcement | Rules table, the row on retiring a part | The row is tagged `prose`, which the `rules` part defines as nothing checking it. The engine does check it: `dropped_parts` in `wslib/parts.py` fails a manifest that drops a used part, and the manifest parser refuses a `retired` entry with no `why`. A test in `tests/test_core.py` covers both, and the page's own trap says `check` fails. Verified by reading the code and the test. | fixed: the row says the runner enforces it, and why the tag stays `prose`. |
| 2 | enforcement | Rules table, the row on pushing an eval-covered change for review | The tag's case shows the commit check failing an edited playbook. It does not show a pull request held back. `eval_record` runs at the commit and in CI only, with no push phase, and no hook refuses `gh pr create`. So an early pull request opens freely and only its CI goes red. Verified by reading the case, the part and the manifest; the consequence is inferred. | fixed: the row now claims only the commit refusal; a second row, tagged `prose`, holds the pull request back. |
| 3 | step | Rules table, the row on pushing a branch committed with `--no-verify` | The row asks for a deny-list scan of each commit's diff, and neither the row nor the trap names a command. `ws.py check` has no per-commit scan of files. `--changed-from` scans the current files, so a term added then removed is missed. `--history` skips `deny_list`, which does not set `HISTORY`. Verified by reading `check --help` and `wslib/runner.py`. | queued for the maintainer: the message half now names `python3 ws.py check --commits`; no command scans each commit's diff against the deny list. |

## Checked with no finding

- Contradiction: compared each row with the path, the paragraph on the two parts and the traps. The row on direct pushes has one exception, creating main with `--no-verify`, and the page labels it.
- Trigger: the table adds no purpose, In short or index text, and the `INDEX.md` rows still route machinery changes and refused pushes here.
- Placement: each row concerns a machinery change and sits on the page that owns that path. Nothing was added to the always-loaded layer.
- Eval-case: the page is marked unproven with `prove-by: M4`, and the proof check passes on it.
