---
kind: record
last-reviewed: 2026-11-21
covers: docs/changing-the-machinery.md
reviewed-at: de8b4b3, with the uncommitted change of slice C4
---

# Instruction review: docs/changing-the-machinery.md

This records the instruction review of the C4 edits to the machinery page, for its author and for anyone merging a pull request here.

**In short:** 3 findings: 2 contradiction, 1 enforcement. The merge helper does what the page says before the merge, but step 6 drops the team caveat on publishing, exit 2 can follow a merge that went through, and the merge hook passes more than the page admits.

## Scope

In scope: the edited step 6, the new paragraphs on `python3 ws.py merge` and on merge commits, the edited lead-in and `no_admin_merge` bullet, and the two new rules rows, read against the whole page. Read beside it: `AGENTS.md`, `INDEX.md`, `workspace.json`, `docs/decisions/0005-concurrent-sessions-and-the-edit-ledger.md`, `docs/decisions/0006-what-proven-means.md`, `wslib/merge.py`, `wslib/runner.py` (`command_merge`), `parts/no_admin_merge.py` and its cases, and `tests/test_merge.py`. Ran `python3 ws.py merge --help`, `python3 ws.py selftest`, `python3 ws.py rules`, `python3 -m unittest tests.test_merge`, the hook's `decide` on sample commands, and read-only `gh api` calls for the repository's merge settings and main's branch rule.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | The path for a machinery change, step 6 | Step 6 tells the reader to publish with `gh pr ready NUMBER`, and says nothing about who may. The contract's rules table says that in a team's workspace a person publishes, and step 5 on this page keeps that caveat for the push. An agent in a team's workspace that follows step 6 publishes its own pull request. Verified: the drafts row of the Rules table in `AGENTS.md`, and the last sentence of step 5. | fixed: step 6 now says that in a team's workspace a person publishes and merges. |
| 2 | contradiction | The path for a machinery change, the paragraph on `python3 ws.py merge` | The page says the helper exits 0 when it merged and 2 when a step failed. A merge that went through and then fails a later step exits 2: when the result is not a merge commit, or when GitHub will not delete the branch. An agent that reads 2 as "not merged" reports the wrong outcome or runs it again. Verified: `merge` in `wslib/merge.py` raises `MergeError` after the `gh pr merge` call in both cases, `test_a_merge_that_is_not_a_merge_commit_is_an_error` shows the first, and `command_merge` turns `MergeError` into exit 2. | fixed: the page says a step can fail after the merge, and that its message then says the merge went through. Both such messages already say so. |
| 3 | enforcement | The path for a machinery change, the lead-in to the two parts and the `no_admin_merge` bullet | The lead-in says the second part keeps every merge a merge commit. The bullet says it refuses a `gh api` merge whose `merge_method` is not `merge`, and misses only a `gh` alias or a script. A variable anywhere in the API path makes the hook pass it: `gh api -X PUT repos/o/r/pulls/$N/merge -f merge_method=squash` is allowed. So are `curl` and an interpreter, which the old text covered as "a raw API call" and the new text drops. What keeps every merge a merge commit is the repository's settings. Verified: `decide` refused none of those three commands, `_api_merge` returns early when the path is dynamic, and the repository's settings, read with `gh api`, allow merge commits only. | fixed: the lead-in credits the repository's settings with keeping every merge a merge commit; the bullet names `curl` and an interpreter; an API write whose path is a variable is now refused, with cases. |

## Checked with no finding

- step: `python3 ws.py merge --help` takes only the number, as the page says; `gh pr ready` is gh's own command; `tests.test_merge` ran 35 tests and passed, including the refusals of a draft, a closed pull request, a branch from another repository and a head that moved.
- trigger: the In short line and the index row for this page, which names a refused merge, still route merge work here, and each `no_admin_merge` refusal names the page.
- placement: the helper's description sits on the page whose step 6 uses it.
- eval-case: the page is marked unproven with `prove-by: M4`.
