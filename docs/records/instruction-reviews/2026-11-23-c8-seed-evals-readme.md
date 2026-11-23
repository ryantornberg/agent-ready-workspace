---
kind: record
last-reviewed: 2026-11-23
covers: kit/seed/evals-README.md
reviewed-at: 157570e, with the uncommitted change of slice C8
---

# Instruction review: kit/seed/evals-README.md

This records the review of the seed eval page that `ws.py adopt` writes as a new instance's `evals/README.md`, for its author and its readers.

**In short:** 6 findings: 3 contradiction, 2 step, 1 enforcement; 2 blocking. The page says the eval gates nothing the instance has not proven, while the instance's contract still demands an eval run for any contract change. Its one command fails as written. It does not say what a case holds, and the shared arms it describes still give every case the fix-a-bug playbook.

## Scope

In scope: the whole page, read as an instance's `evals/README.md`, with links read from `evals/`.

Read beside it: the instance's `AGENTS.md`, `README.md`, `evals/arms.json`, `evals/two-line.md` and `kit.lock.json`; in the worktree, `evals/README.md` (the kit's, to compare), `evals/run.py`, `evals/cases/fix-a-bug.json`, `docs/decisions/0006-what-proven-means.md`, `docs/decisions/0007-the-kit.md`, `kit/kit.json`, `wslib/kitlock.py`, `parts/eval_record.py`, `parts/proof.py` and `tests/test_kit.py`.

Run: a temporary clone outside the worktree, at 157570e with C8's uncommitted change applied and committed there, then `python3 ws.py adopt` into a scratch folder. In the instance, `python3 ws.py check` passes, so the page's three links resolve (verified). `evals/` holds `run.py`, `grade.py`, `pool.py`, `proofkeys.py`, `arms.json`, `two-line.md` and this page, and no cases, scaffold or acceptance tests (verified, `ls`).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | **In short**, "the `eval_record` check here gates only the pages this workspace proves itself"; "The gate", its last paragraph | Blocking. The instance's `AGENTS.md`, the kit's byte for byte (verified, `diff`), links this page for its rule: "A change to a playbook marked proven, to this file, to `INDEX.md` ... needs a new eval run on record in which the guidance beats both the bare model and a two-line instruction". This page says the check gates only the instance's own proven pages. That matches the code: in the scratch instance an edit to `AGENTS.md` and `INDEX.md` raises no `eval_record` finding (verified). The contract's rule cannot be met in a new instance, which has no case to run. An agent that follows this page edits the contract against the contract's own row. | fixed: the kit drops the contract's eval-run row from an instance, and the page says so and when to add it back. |
| 2 | step | **In short**, "record it with `python3 evals/run.py`" | Blocking. As written, the command fails. In the scratch instance it exits 2: "run.py: error: name a case, or pass --probe" (verified). The page gives no case-name argument and no other run option, such as `--model` or `--runs`. The kit's run uses `python3 evals/run.py fix-a-bug --model haiku --runs 15` (verified, `evals/run.py`'s docstring). | fixed: the command is `python3 evals/run.py NAME`, and the page points to `--help` for the options. |
| 3 | step | "The cases", "A case is a JSON file under `evals/cases/`: a one-line request, the playbook it tests, a scaffold folder ... a hidden acceptance test and its graders" | Not blocking. The page names the parts of a case but not its keys, and the instance holds no case to copy: cases, scaffold and acceptance tests are never synced (verified, `kit/kit.json` and `ls evals`). A case needs `name`, `playbook`, `scaffold_dir`, `code_dir`, `acceptance`, `request` and `graders`, each grader with an `id` and a `type` from `grade.py`'s list (verified, reading `evals/cases/fix-a-bug.json` and `evals/grade.py`). The README's step 4 sends the reader here to write one. | fixed: the page lists a case's keys and where the grader types are. |
| 4 | contradiction | "The cases", "the guided arm gets the workspace's contract, index, playbook and definition of done; the two-line arm gets two lines" | Not blocking. The seeded `arms.json` names `docs/playbooks/fix-a-bug.md` as the guided arm's playbook, and `two-line.md` holds fix-a-bug's two habits (verified, reading the instance's files). `run.py` does not add a case's own playbook to the shared arms (verified, reading `arms_for`). So a first case for the team's own playbook, on the shared arms, gives the guided arm the kit's playbook and the two-line arm the kit's two lines. The page should say to change both files, or have the case name its own arms. | fixed: the page says both arm files name the kit's playbook, and to change them or have the case name its own arms. |
| 5 | contradiction | "The gate", "an edit to any of them fails the commit until the case is run again" and "Only pages marked proven are gated" | Not blocking. The first sentence says every edit fails; the second limits that to proven pages. In the scratch instance, a case for an unproven playbook, with no record at all, raises no `eval_record` finding (verified). Put the limit in the first sentence. | fixed: the gate's paragraph opens with the limit to proven pages. |
| 6 | enforcement | "Rules that make this worth doing" | Not blocking. Four rules, among them "Never describe the graders in a page the agent reads", with no enforcement stated and no rules table. The kit's own eval page has the same list (verified, reading). Tag them `prose` in a rules table, or say they are advice. | fixed: the section says the rules are advice and no check holds them. |

## Checked with no finding

- trigger: the title and **In short** line fit a new instance's eval page: no cases yet, and the kit's proof is the kit's. `INDEX.md`'s row "Testing a playbook" points here (verified, reading the instance's index).
- placement: the page links decision 0006 for the proof rule and decision 0007's lock behavior is stated in two sentences where the reader needs it. It restates no rule of procedure endings (verified, reading).
- eval-case: the page asks for no new agent behavior that an eval would test; it describes the harness. It carries no proof mark and is not a playbook or how-to (verified, reading).

## Re-check

A fresh session re-read the whole page on 2026-11-23, after the fix round, at 8162e8e with the uncommitted change of slice C8, as an instance's `evals/README.md`. It ran on a scratch clone with that change committed and an instance adopted from it.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | The instance's `AGENTS.md` no longer holds the eval-run row (verified, `diff`). "The gate" says the kit left it out and when to add it back, with the tag `eval_record#an edited playbook fails until its case is run again`, a case the synced `parts/eval_record.cases.json` holds (verified, `selftest` passes `eval_record` 49 of 49). |
| 2 | fixed | The command is `python3 evals/run.py NAME`. In the instance, `python3 evals/run.py --help` exits 0 and lists `--model` and `--runs` (verified). |
| 3 | fixed | The keys listed match the kit's cases and what `run.py` reads (verified, reading `evals/cases/*.json` and `run.py`). |
| 4 | fixed | The page says both arm files name the kit's playbook. A case's own `arms` replaces the shared file, as `arms_for` in `run.py` shows (verified, reading). |
| 5 | fixed | "The gate" opens with "Only pages marked proven are gated" (verified, reading). |
| 6 | fixed | The section says the rules are advice and no check holds them (verified, reading). |

Broke: none. The pooled threshold the page states, 40 or more runs per arm, matches `POOLED_MIN_RUNS` in `parts/eval_record.py` and decision 0006 (verified).

Missed: none.
