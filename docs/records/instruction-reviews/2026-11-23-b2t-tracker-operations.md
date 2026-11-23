---
kind: record
last-reviewed: 2026-11-23
covers: docs/playbooks/tracker-operations.md
reviewed-at: 18eccc5, with the uncommitted change of the B2t builder
---

# Instruction review: docs/playbooks/tracker-operations.md

This records the instruction review of slice B2t's change to tracker operations, for its author and for agents asked to act on a ticket.

**In short:** 3 findings: 2 step, 1 placement. None is blocking.

## Scope

The change is `git diff fad9f23 -- docs/playbooks/tracker-operations.md`: the outward-write guard row of "What exists today and what is planned", steps 4, 5 and 7 of "Steps", the opening of "The post-merge security review", and the question-log row of "Rules". In scope: that changed text, and anything on the page, or on a page it links to, that the change contradicts or leaves stale.

Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/procedure-endings.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/changing-the-machinery.md`, `docs/parts.md` (the `outward_write` row and "The parts here"), the case names in `parts/outward_write.cases.json`, `outward-repos.json`, decision 0004's "The outward-write guard", `docs/research-ladder.md`, `docs/question-log.md`, `docs/templates/bug-ticket.md`, and the pages the changed text links to. Ran `python3 ws.py check` (no error; one unrelated eval_record warning).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | "Steps", step 4, with "The post-merge security review", step 1 | Not blocking. Step 4 now runs the review section's steps 1 to 4 before it asks. Those steps end in "go to step 7 of the steps" when the item links no pull request and the person gives no number, or when none is merged. Run from step 4, that exit skips the rest of step 4 and all of step 5. So the other ask-first writes are never asked, and named writes that do not depend on the review, such as a status change the request also names, are never made. Step 5's own rule stops only "a write that depends on it". Before the change the exit fired inside step 5. Verified by reading steps 4 and 5 and the section's step 1; that an agent would drop the unrelated writes is inferred. | fixed: step 4 drops the review's writes and asks about the rest when the review ends early. |
| 2 | step | "What exists today and what is planned", the outward-write guard row | Not blocking. The new row says the guard refuses a gh write to a repository outside `outward-repos.json`, "so it covers a tracker reached through `gh`". Decision 0004 and the parts table also refuse, on every repository, a gh write that acts on an account's projects, and every `gh api graphql` call. The cases show it: `gh project item-add is refused: projects belong to an account`, while `gh project item-list` is a read that goes ahead. So on a GitHub Projects tracker, step 1 finds live mode and every write in step 5 is refused, which the page does not predict; draft mode would fit. Verified by the case names and decision 0004's text; the Projects scenario is inferred. | fixed: the row says every `gh api graphql` call is refused. |
| 3 | placement | "Steps", step 7 | Not blocking. The changed step 7 still restates the report rule ("with each claim marked verified or inferred, as the definition of done says") rather than linking [procedure endings' report](../../procedure-endings.md#the-report), which the page now links only for the question-log entry. Procedure endings' report also names refusals and anything left uncommitted or unpushed; step 7's list does not. Verified by reading both pages. | fixed: step 7 links procedure endings' "The report". |

## Checked with no finding

- contradiction: the review section's new opening and steps 4 and 5 agree on where its steps 1 to 4 run; the section's step 5 still takes "the yeses from step 4"; the new question-log wording matches procedure endings' "The question-log entry" and the question log's own "Adding an entry"; the stop line's "apart from a question-log entry" still holds.
- trigger: the purpose line, the In short line and the routing table were not changed; the change adds no text that decides when the page applies.
- enforcement: no new must or never; the changed rules row stays `prose`, and the guard row claims no tag.
- eval-case: the page is `proof: unproven`, `prove-by: M8`, so the new order of the review needs no eval case yet.

## Re-check

A fresh session re-read the page on 2026-11-23 after B2t's fix round, with `git diff fad9f23`, procedure endings, changing the machinery, the contract, the parts table's `outward_write` row, the `outward_write` case names, and the other five pages of this batch that share the off-`main` rule: architecture review, the review orchestrator, defect escape analysis, git-host operations and federated search. `python3 ws.py check` passes, with only the known warning on fix a bug's eval record. In a scratch repository with a local bare remote, `git push origin HEAD:main` from a worktree on a branch holding a code commit and then a question-log commit exited 0 and moved the remote's main to include the code commit.

| # | Verdict | Evidence |
|---|---|---|
| 1 | holds | Step 4 now says that if one of the review section's steps 1 to 4 ends the review early, the review's writes are dropped from the list and the rest are asked about. So the other ask-first writes and the unrelated named writes go on to step 5. Verified: the text. A wording gap remains; see "Broke". |
| 2 | holds | The guard row now says the guard refuses every `gh api graphql` call on any repository, "which rules out GitHub Projects writes through `gh`". So the page now predicts that a Projects write is refused. Verified: the row and the parts table. The reason it gives is partly wrong; see "Broke". |
| 3 | holds | Step 7 links procedure endings' "The report" and names any refusal. Verified: the text. |

Broke:

- Not blocking. The review section's step 1 still says, twice, "go to step 7 of the steps" when no pull request is given or none is merged. Run from step 4, that jump conflicts with step 4's new "drop the review's writes from the list and ask about the rest". The section's new opening says where its steps run but does not override the jump. An agent can reconcile the two only by reading step 4's "ends the review early" as meaning that jump. Verified: the texts of step 4 and the section's opening and step 1.
- Not blocking. The guard row says `gh api graphql` refusals rule out GitHub Projects writes through `gh`. The ordinary route, `gh project item-add` and its siblings, is not a `gh api graphql` call. The guard refuses it for another reason: projects belong to an account, so the write names no listed repository. The conclusion holds and the reason does not. Verified: the case names `gh project item-add is refused: projects belong to an account` and `a plain GraphQL query is refused`.

Missed:

- Blocking. Step 7 logs a question and commits it "as procedure endings says", with no exception for a branch other than `main`. Procedure endings puts a pages-only commit "on the worktree's branch in a worktree", then pushes it with `git push origin HEAD:main`. This page is often run from a fix's or a feature's worktree, such as to move a ticket to review once its pull request opens. There HEAD is an unmerged code branch, so the push carries its code to main with no pull request and no CI. That goes against procedure endings' "never on its main" for code and the contract's draft pull request rule. `direct_push` refuses only machinery paths. Git-host operations' finding 1 was this same chain, marked blocking, and was fixed there by leaving the row uncommitted off `main`; this page got no such exception. Verified: the texts of step 7 and procedure endings' "The commit" and "The push"; the scratch push above. Inferred: that the page runs with a code branch checked out, and that an agent follows procedure endings through to the push. The fix is the same exception git-host operations has, or one rule on procedure endings for every procedure.
