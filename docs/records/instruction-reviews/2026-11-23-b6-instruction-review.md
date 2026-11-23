---
kind: record
last-reviewed: 2026-11-23
covers: docs/playbooks/instruction-review.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: docs/playbooks/instruction-review.md

This records the review of B6's edit to the instruction review's list of guidance pages, now naming the wrappers, for its readers.

**In short:** 1 finding: 1 step, not blocking. Every wrapper is a file named `SKILL.md`, so the record's naming rule, "the date and the page", gives no name for a wrapper's record.

## Scope

In scope: in "When it runs", the changed sentences on `plugin/skills/` and `plugin/evals/`, read against "The record" and the steps. The whole page was read, with `git diff --cached -- docs/playbooks/instruction-review.md` for the change. Read beside it: `AGENTS.md`, `INDEX.md`, `workspace.json` (the `review_trailer` and `review_index` entries), `parts/review_trailer.py`'s `_pattern` through the new test, the staged diff of `tests/test_instruction_review.py`, the wrappers under `plugin/skills/`, the selection cases under `plugin/evals/`, `plugin/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `docs/playbooks/README.md` and the record `docs/records/instruction-reviews/2026-11-23-c8-readme.md`.

Run, on macOS: `python3 -m unittest tests.test_instruction_review tests.test_m3_a -b` passes, 43 tests, among them `test_the_wrappers_are_guidance_and_their_selection_cases_are_not` (verified). `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` reports `review_trailer: 24 of 24 cases` (verified).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | "The record", "Name it for the date and the page", read against "When it runs" | Not blocking. The changed sentence makes every wrapper a guidance page, and all 28 are files named `SKILL.md` (verified, listing `plugin/skills/`). "The date and the page, such as `2026-11-21-layout.md`" gives no rule for which word names a wrapper's record: its file name, its folder or its page. Nothing fails, since the `covers:` line ties a record to its page and the `review_index` check reads that line, not the name (verified, the page says so and the check passes). Add: a wrapper's record is named for its folder, such as `2026-11-23-wrapper-debugging.md`. | fixed: a wrapper's record is named for its folder. |

## Checked with no finding

- contradiction: the sentence agrees with `workspace.json`. The `review_trailer` entry's `guidance` list names `plugin/skills/` and no other path under `plugin/` (verified). The new test holds every tracked file under `plugin/` to it: the wrappers are guidance, and the selection cases and the plugin's manifest are not (verified, passing). The catalog's "At the commit" row lists fewer guidance pages than this section; that is recorded once, against the catalog (2026-11-23-b6-playbook-catalog.md).
- trigger: the page's purpose and **In short** lines are unchanged. "When it runs" is the text that decides when the review applies, and it now covers every path the check covers.
- enforcement: the rules table is unchanged, and each tag still names a case of `review_trailer` or `review_index` that `python3 ws.py selftest` runs (verified). The new sentence adds no must or never.
- placement: the sentence says which paths are guidance on the page that owns that list, and gives the reason the selection cases are not.
- eval-case: the page is marked unproven, with `prove-by: M4` (verified, reading its front matter).

## Re-check

A fresh session re-read the page on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6, using `git diff --cached`. On macOS, `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` exits 0, with `wrappers: 18 of 18 cases`; and `python3 -m unittest tests.test_kit tests.test_instruction_review -b` runs 48 tests, OK (verified).

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | "The record" now says: "A wrapper's record is named for its folder, such as `2026-11-23-wrapper-debugging.md`." The `covers:` line still ties a record to its page, and `review_index` reads that line (verified, reading the page and `parts/review_index.py`). |

What a fix broke: nothing.

What the first reading missed: nothing.
