---
kind: record
last-reviewed: 2026-11-23
covers: docs/playbooks/git-host-operations.md
reviewed-at: dace91e, with the uncommitted change of the B5 slice session
---

# Instruction review: docs/playbooks/git-host-operations.md

This records the review of B5's added sentence in step 6 of git-host operations, for its author and its readers.

**In short:** 1 finding, none blocking: 1 step. Step 6 now says to read `isDraft` back after every write, but it runs once, after step 5 has made all of them.

## Scope

In scope: the sentence added to step 6 under "Steps", "An update call once published a draft without being asked to, so read `isDraft` back after every write, not only after the one that sets it." The whole page was read, with `git diff HEAD`. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/changing-the-machinery.md` ("The path for a machinery change"), and the pages the steps link.

Runs (verified): `python3 ws.py check` exits 0 in the worktree, with only the `eval_record` warning about a missing base commit.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | "Steps", steps 5 and 6, and the rules-table row "Read the pull request again after each write" | Not blocking. Step 5 runs every write "in the list's order", with no read between them. Step 6 then reads the pull request once, with input "the writes from step 5" (verified, reading both steps). The new sentence, inside step 6, says to read `isDraft` "after every write". An agent cannot tell whether to add a read inside step 5 after each write or to read once in step 6 (inferred). Read once, a draft published by the first write stays published while the later writes run, the case the sentence's own reason describes (inferred). The rules table already says "after each write", so the table and the steps disagreed before this change; the sentence makes it visible without settling it (verified). | fixed in part: the sentence now says this one read covers `isDraft` whatever the writes meant to change. The older mismatch between step 5's writes and the rules row's "after each write" predates this change: a known defect, for M8 |

## Checked with no finding

- contradiction: the step's default, "when a value differs, do not write again; report the difference", fits an unexpected publish. It leaves the contract's rule, publish only after CI passes on three systems, to the person (verified, reading the contract and step 6).
- trigger: the purpose and **In short** lines are unchanged and still cover the step: "read it back from the host" (verified).
- enforcement: the rule the sentence sharpens has a rules-table row, tagged `prose`, which is true (verified). Which update call published a draft is not named, and no record in this workspace holds the incident (inferred; `git grep -n -i "draft" docs/records/lessons.md` finds nothing).
- placement: the sentence sits in the step it changes, not restated from procedure endings (verified).
- eval-case: the page is `proof: unproven` with `prove-by: M8` (verified, reading its front matter).

## Known defects

- Steps 5 and 6 against the rules row "Read the pull request again after each write": step 6 reads once, after all of step 5's writes. This predates slice B5. For M8, the page's `prove-by` milestone.

## Re-check

A fresh driver-tier session read the changed passage as it stands, with `git diff HEAD -- docs/playbooks/git-host-operations.md`, beside steps 5 to 7, "Which writes need a yes" and "Rules", and ran `python3 ws.py check` (exit 0, only the `eval_record` warning).

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | Step 6's sentence now reads "An update call can publish a draft without being asked to, so this read covers `isDraft` whatever the writes meant to change": it places the check in step 6's one read and no longer says "after every write" (verified, reading). It states a present fact, not the page's history. The older mismatch with the rules row is in "Known defects", for M8, and the finding was not blocking (verified). |

What a fix broke:

- None.

What the first reading missed:

- None.
