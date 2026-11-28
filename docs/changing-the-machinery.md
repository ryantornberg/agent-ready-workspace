---
kind: how-to
proof: unproven
prove-by: M4
last-reviewed: 2026-11-21
---

# Changing the machinery

Docs go straight to main, a guidance page after its instruction review. The scripts, hooks and CI that check them take a stricter path. It is for anyone, person or agent, about to change one of them.

**In short:** a doc change goes straight to the main branch. A machinery change goes to its own branch and merges only after CI passes on Linux, macOS and Windows. Machinery work runs at the driver tier.

## What counts as machinery

| Path | What it is |
|---|---|
| `ws.py`, `wslib/` | The engine: `wslib/` holds its code, and `ws.py` starts it. See [decision 0003](decisions/0003-the-engine-in-one-folder.md). |
| `parts/` | Every check and hook, and their cases |
| `tools/` | Lookups such as `symbols.py` |
| `evals/*.py`, `evals/cases/`, `evals/acceptance/`, `evals/arms.json`, `evals/one-time.json` | The eval harness, the graders, the cases with their hidden acceptance tests, and what each arm is given. A change to most of these needs the eval run again; see [evals](../evals/README.md#the-gate). |
| `workspace.json` | The manifest: which parts run, and the tier binding |
| `.githooks/`, `.github/`, `.claude/settings.json`, `.codex/hooks.json` | The commit hook, CI and the agent tools' wiring |
| `.mcp.json`, `.codex/config.toml` | The browser server each agent tool runs; see [browsers](browsers.md) |
| `opencode.json` | The instructions opencode loads: the contract and the rule pages |
| `outward-repos.json` | The repositories agents may write to; see [decision 0004](decisions/0004-the-hook-contract.md). The guards refuse an agent's edit in the cases decision 0004 names, and the README's limits name what gets past them; a person edits it on a branch and opens the pull request. It holds data, not code, so step 2's failing case does not apply to it. |
| `tests/` | The tests of all of the above |
| `baselines/` | The findings each check tolerates; see [baselines](parts.md#baselines) |
| `kit/`, `kit.lock.json` | What the kit gives an instance, and an instance's record of it; see [decision 0007](decisions/0007-the-kit.md). The lock holds data that `ws.py upgrade` and `ws.py drift --keep` write, so step 2's failing case does not apply to it; an upgrade changes the engine and the lock together. A change to a seed page, `kit/seed/README.md` or `kit/seed/evals-README.md`, is also a guidance change and takes the instruction review too. |

Everything else is a doc. The table is the `machinery` list of the `direct_push` part in [workspace.json](../workspace.json), and a test fails when the two differ.

## The path for a machinery change

1. **Branch.** Name it after the work, such as `m1/slice-2`.
2. **Write the failing case first.** A part's case, or a test in `tests/`, that fails without the change.
3. **Run the three commands** and keep their output for the report:

   ```
   python3 ws.py selftest
   python3 ws.py check
   python3 -m unittest discover -b tests
   ```

   An instance made from the kit has no `tests/`, since the kit's tests stay in the kit. There, run `python3 ws.py drift` as the third command instead.

4. **Commit on the branch**, staging files by name.
5. **Push the branch and open a draft pull request.** CI runs on three systems. In this repository an agent may push; in a team's workspace, a person does. When a reviewer leaves comments on it and the author is present to go through them, follow the [feedback walk-through](playbooks/feedback-walkthrough.md). With no author present, list the comments in your report and do not merge in step 6 until the author has answered them.
6. **Publish and merge once CI is green**, with `gh pr ready NUMBER` and then `python3 ws.py merge NUMBER`. A red run on any one system blocks the merge. In this repository an agent may publish and merge; in a team's workspace, a person does.

`python3 ws.py merge NUMBER` merges on GitHub and uses no working copy, so it works from a worktree while another session holds the main copy. It takes the pull request's number and nothing else: the repository is always this one's `origin`. It refuses a draft, a closed pull request and a branch from another repository. It reads the checks the base branch's rule requires, and refuses unless each one's newest run passed on the pull request's exact head commit. Then it runs `gh pr merge NUMBER --merge --match-head-commit SHA`, so a push after the check stops the merge. It checks that the result is a merge commit, deletes the branch on GitHub, and brings the main working copy up to date when that is safe. When it is not safe, it says why: see [decision 0005](decisions/0005-concurrent-sessions-and-the-edit-ledger.md). It exits 0 when it merged, 1 when it refused, and 2 when a step failed. A step can fail after the merge, such as the branch's deletion; its message then says that the merge went through.

A merge is always a merge commit. A squash or a rebase rewrites the branch's commits, so once the branch is deleted, main no longer holds them. A proof anchor pinned to one of them then names a commit main does not have: see [decision 0006](decisions/0006-what-proven-means.md). The repository's settings on GitHub allow merge commits only, which also covers a merge from the web page.

A branch rule on GitHub requires all five CI jobs to pass before a pull request merges to main. It does not bind the repository's owner: an owner's direct push, and `gh pr merge --admin`, both go past it, and an agent using the owner's sign-in has the same power. Two parts close those routes for an agent's shell, and the second also refuses a squash or a rebase merge. The repository's settings, which allow merge commits only, keep every merge a merge commit, whatever made it:

- **`direct_push`, at the push.** The pre-push hook refuses a push to main that adds a commit changing a machinery path, and names each such commit with its path. A merge is judged by the commits it brings in, and by any change the merge commit makes itself. A machinery file renamed or moved away counts as a change to its old path. A doc-only push, and a push to any other branch, goes ahead. The hook reads the part and the machinery list from the remote's current tip, so a push that edits the list is judged by the list it would replace. The engine that runs it is the working copy's own, so a commit that changes the engine is judged by the engine it brings. It refuses when it cannot list the commits being pushed, so fetch first; and it refuses a push to main when the remote's tip holds no readable manifest.
- **`no_admin_merge`, before a shell command.** It refuses `gh pr merge` with `--admin`, `--squash` or `--rebase`, in their short forms too, in any form the shared command-line parser follows. It refuses a `gh api` call to a pull request's merge endpoint whose `merge_method` is not `merge`, or whose body it cannot read. It refuses any API write whose path is a variable, and a GraphQL merge or auto-merge with another method, or whose query it cannot read. It cannot see a merge made through another program such as `curl`, an interpreter, a `gh` alias or a script.

**A command `no_admin_merge` cannot judge is refused too**, wherever it runs, since it might merge past CI: a program word or a gh subcommand that is a variable, such as `"$EDITOR" README.md`; text piped into a shell, such as `cat x | bash`; arguments that `xargs` or `find -exec` give `gh pr merge` or `gh api`; and a `gh pr merge` argument that is a variable. Write the command with literal words, such as the program's own name; to merge, run `python3 ws.py merge NUMBER`.

A first push that creates main checks the whole history being pushed. To create main in a new repository, push once with `--no-verify`.

## Rules

| Rule | Enforced by |
|---|---|
| A commit that changes a machinery path reaches main only through a pull request. | `direct_push#a commit that changes a part fails, naming the commit and the path` |
| No merge with `gh pr merge --admin`, which goes past red CI. | `no_admin_merge#a merge with the flag after the number` |
| A pull request merges with a merge commit, never a squash or a rebase. | `no_admin_merge#a squash merge`, `no_admin_merge#a rebase merge`, `no_admin_merge#an api merge whose method is squash` |
| An agent merges with `python3 ws.py merge NUMBER`, which merges only once every check the branch rule requires passed on the pull request's head commit. Its tests run it on recorded `gh` answers; no part refuses a plain `gh pr merge --merge`. | `prose` |
| A part leaves the manifest only by being listed under `retired`, with a reason. The runner refuses any other removal; it is not a part, so the tag is `prose`. | `prose` |
| A change the eval covers fails the commit check until the eval has run again and its new records are committed. | `eval_record#an edited playbook fails until its case is run again` |
| A change to grading files alone fails the commit check until `python3 evals/grade.py --recorded --stamp` re-grades every stored transcript with no difference and writes the new grader hash; a record with no grader hash fails. | `eval_record#an edit to grade.py alone fails until the stamp writes the new grader hash`, `eval_record#after the stamp, an edit to grade.py alone passes`, `eval_record#a record with no grader hash fails` |
| Open no pull request for such a change until the commit with its new records passes every hook. | `prose` |
| A pull request with review comments nobody has gone through with the author is not merged; the comments go in the report. | `prose` |
| Before each push of a branch committed with `--no-verify`, every commit message passes the message checks, which `python3 ws.py check --commits origin/main..HEAD` runs on each commit, and every commit's diff passes the deny-list scan. | `prose` |

## Traps

- **The hooks guard the session that edits them.** A part with a failing case is refused. A hook call loads only the hooks for its event, so a broken check no longer refuses anything, and a broken hook refuses only its own event: with a broken shell hook, the edit tools still work. Four things still refuse every hook call, because the runner cannot tell whether a hook would refuse: a manifest it cannot read, a manifest whose `version` differs from the engine's, a part file that is missing, and a part whose `KIND` line it cannot read. A manifest entry with no `why`, or an unknown key, fails every other command but does not refuse a hook call. [Parts](parts.md#a-hook) says how a part declares its kind.
  - Change a part's code and its cases in one step, and run `python3 ws.py selftest` before the next tool call.
  - If the session is locked out, the person repairs the file from their own terminal, where the agent's hooks do not run.
  - Change the engine's `VERSION` and the manifest's `version` in one step: on a branch in its own working copy, then a merge or a checkout. Edited one at a time in the working copy the session runs in, they lock the session out.
- **A part leaves the manifest only by being retired.** A manifest that drops a part the last commit used fails `check`, and in CI the base branch's manifest decides. List the part under `retired` with a reason. See [removing a part](parts.md#removing-a-part).
- **A change the eval covers cannot pass the commit check until the eval has run, or, for grading files alone, the stamp.** `eval_record` refuses it by design. After a recording, run `python3 evals/grade.py --recorded --stamp` too, before the commit: `run.py` writes no grader hash until M4's slice H0b adds it. A change to grading files alone, `evals/grade.py` or a hook a grader runs with the modules it imports, needs no run: run the stamp and commit the records it rewrites with the change, with no `--no-verify`. When the stamp finds a grade that differs, it writes nothing; record the case again, then stamp. Until M4's slice H0b rewrites the contract's eval rule, read that rule in `AGENTS.md` as covering what an agent is given: the grading-files exception is [the eval page's](../evals/README.md#the-gate). To save a change that needs the runs before the costly runs, commit it on its branch with `git commit --no-verify`, after `python3 ws.py check --staged` shows only the `eval_record` findings, and run `python3 ws.py check --message FILE` on the message by hand, since `--no-verify` skips that hook too. Before every push of that branch, run the checks `--no-verify` skipped on every commit it holds: `python3 ws.py check --commits origin/main..HEAD`, which runs the message checks on each commit's message, and the `deny_list` check on each commit's diff, since a pushed branch on a public repository is visible at once. Push the branch, but open no pull request until the commit with the records passes every hook.
- **A check you cannot run in CI.** The `deny_list` check reads a private list from the file `WS_DENY_LIST` names, or from `~/.config/agent-ready-workspace/deny-list.txt`. CI has no list, so it warns and checks nothing. Commit on a machine that has the list.
