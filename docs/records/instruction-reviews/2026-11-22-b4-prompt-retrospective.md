---
kind: record
last-reviewed: 2026-11-22
covers: docs/playbooks/prompt-retrospective.md
reviewed-at: 31f9aaa, with the uncommitted change of the B2 builder
---

# Instruction review: docs/playbooks/prompt-retrospective.md

This records the instruction review of the new prompt retrospective playbook, for its author and for the maintainer who runs it.

**In short:** 3 findings: 1 contradiction, 2 enforcement. The read-only rule says the retrospective writes no record while step 6 requires a question-log entry, the tier rule's tag shows only that some tier is named, and the question-log must has no rules row.

## Scope

In scope: the whole page, which is new. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md`, and every page it links: `docs/maintain-the-workspace.md`, `docs/playbooks/escape-analysis.md`, `docs/playbooks/debugging.md`, `docs/research-ladder.md`, `docs/question-log.md`. Also read the other pages of batch 4 and the diffs of the edited pages. Listed `~/.claude/projects/` and `~/.codex/sessions/` to confirm the transcript table's paths, ran `git log -1 --before="2026-11-20T10:00:00Z" --format=%H` and `git cat-file -e` on a present and an absent path (exit 0 and 128), read `parts/handoff_tier.cases.json`, and ran `python3 ws.py rules` and `python3 ws.py check`.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | When it runs, the paragraph under the table; Steps, step 6; Rules table, the third row | The page says the retrospective "edits no page and writes no record, helpers included". Step 6 says "The retrospective wrote nothing, so nothing is left uncommitted", then, in the next sentence, requires a question-log entry when a person had to be asked. The question log is a record, as layout says, written with or without a yes, as the research ladder says. So the step writes a record the page says it never writes, and that entry has no commit or uncommitted ending. Verified: layout's "Folders" section, the question log's `kind: record`, and the research ladder's offer section. Cause: sheet-forbids-labelling-exception — the sheet's section 3 tells the read-only pages to state the question-log rule in the contract's words and not label it an exception, beside a "writes no record" rule it breaks. | fixed: the page now says it writes nothing on what it reads, and step 6 commits any question-log entry staged by name, or reports it uncommitted with the refusal. |
| 2 | enforcement | Rules table, the first row | The rule says the helper's prompt starts with `Tier: driver`, and is tagged `handoff_tier#no tier named`. That case shows a prompt with no tier refused; the hook allows any tier the binding holds, as its case "a tier, with the bound model and effort" allows `Tier: mechanical`. So the driver half of the rule, which step 2 and the sheet's tiers section rely on, is unenforced while the tag claims it. Verified: read `parts/handoff_tier.cases.json`. Cause: page-specific — the brief already requires a tag only where the case shows the rule. | fixed: the tier-line row now claims only that the prompt starts with a tier; a separate `prose` row holds the driver tier. |
| 3 | enforcement | Steps, step 6; Rules table | Step 6 requires a question-log entry before the session finishes. The rules table has no row for it, though the docs audit, the sibling page with the same read-only shape, carries one. Verified: `python3 ws.py rules` lists nine rules for this page, none on the question log. Cause: self-review-must-list-skipped — the brief's self-review asks for every must on the page to be listed against the rules table, and this one was missed. | fixed: a rules row now holds the question-log entry and its commit, staged by name. |

## Checked with no finding

- trigger: the purpose line, the "When it runs" table and the catalog's Upkeep row separate this page from escape analysis and debugging as the sheet's tie-break says; the maintain page routes in from its event list and periodic duties.
- step: each step names its input, default and output; a missing transcript, a helper that returns no report, an agent tool that cannot start a helper, and a session in another repository each end in step 6's report; the transcript paths, `git log --before` and `git cat-file -e` behave as the page says.
- placement: the transcript table is a short reference section the steps need; the four checks sit on this page only, and maintain links them.
- eval-case: the page is marked `proof: unproven` with `prove-by: M10`.

## Re-check

A fresh session re-read the page on 2026-11-22, after the fix round.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | Verified: "When it runs" now says the retrospective writes nothing on what it reads and no record of its own, and step 6 commits any question-log entry staged by name or reports the refusal. |
| 2 | fixed | Verified: the tier row now claims only that the prompt starts with a tier, which `handoff_tier#no tier named` shows, and a separate `prose` row holds the driver tier. |
| 3 | fixed | Verified: the rules table holds a question-log row with its commit, staged by name. |

Broke: none.
Missed: none.
