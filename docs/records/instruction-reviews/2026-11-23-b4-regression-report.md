---
kind: record
last-reviewed: 2026-11-23
covers: docs/templates/regression-report.md
reviewed-at: 1a18d68, with the uncommitted change of the B4 slice session
---

# Instruction review: docs/templates/regression-report.md

This records the instruction review of slice B4's new regression run report template, a QA lane draft, for the change's author.

**In short:** 7 findings, none blocking: 3 contradiction, 4 step. The summary's skipped count cannot match a results file that lists only selected cases. A `human` case, and a failure caught by a sink check, have no verdict or checkpoint the page can record. "New server errors" has no default for which run is previous, nor an order for normalizing messages.

## Scope

In scope: the whole page, which is new and untracked. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/extend-the-workspace.md`, and the pages it links to: `docs/playbooks/regression-run.md`, `docs/playbooks/regression-triage.md` and `docs/templates/bug-ticket.md`. Also read `docs/templates/regression-case.md`, whose worked example the results line reuses, and the new "Lane templates" rows in `docs/templates/README.md`. The page gives no command to run. Checked that both `.tsv` examples are tab-separated (`cat -A` shows tabs between fields), ran `grep` for inbound links to the page, and ran `python3 ws.py check`, which reports nothing on this page.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Filling the report, Verdicts; The results file; Rules, the last row | Not blocking. `skipped` covers a case "excluded at the case check or at selection". The results file holds "one line per selected case", so neither kind of skipped case is in it. Yet "The summary's counts match the results file", and the summary has a `skipped` row. With any skipped case, both cannot hold. Verified: the three texts, and regression run's steps 2 and 6, which exclude cases before and at selection. | fixed: the results file now holds one line per case the run considered, selected or skipped, so the summary's skipped count can match it. |
| 2 | step | The results file; Filling the report, Device checklist | Not blocking. A selected `human` case is not run by the agent (regression run's step 9), yet the results file needs a line for it with one of four verdicts, and none fits a case waiting for a person. The page does not say where the person's results go once the checklist is worked through. Nor does the checkpoint list say what to write for checkpoints after the one that failed: the example ends at the failed checkpoint 3. Verified: the page beside regression run's step 9. | fixed: `skipped` now covers a human case left for the device checklist; the person writes each result on its checklist line, where triage reads it; a checkpoint list ends at the first failed checkpoint. |
| 3 | step | Filling the report, Failures | Not blocking. The failure block's mapping assumes a failed checkpoint: "How to reproduce" runs "up to the failed checkpoint", and "Acceptance criteria is that checkpoint". A case can fail on a sink check, such as a missing database row or email, with every checkpoint passed, and then the mapping has no input. Verified: the case template has a separate "Sink checks" section, and regression run's step 8 gives a verdict on them. | fixed: Failures adds the sink-check case: "How to reproduce" gives every step and "Acceptance criteria" is the failed sink check. |
| 4 | step | Filling the report, New server errors; The error-signature file | Not blocking. The comparison has no default for which earlier run is "the previous run": the newest folder, or the newest on the same environment and selection. A previous run on another environment lists that environment's errors as new. Normalizing gives no order or definition: replacing numbers before timestamps or ids leaves `<n>-<n>-<n>T<n>:<n>` or a part-replaced id, so two runs can normalize one error two ways and report it as new. Verified: the page and regression run's step 10, which takes "the previous run's folder" with no default. Inferred: the false new signatures. | fixed: the previous run is the newest earlier folder with the same Environment; normalization runs in a fixed order: timestamps, then ids, then remaining digit runs (the example now shows `<n>`). |
| 5 | step | The report: report.md, the Failures skeleton; Rules, the third row | Not blocking. Each failure block sits under `### <CASE-ID>`, and the bug report template's headings are also `###`, so they land beside the case heading, not under it, with no level given. The page does not say whether the bug template's summary line and its "For developers" `<details>` block come along. "Keep every heading" and its Rules row are not qualified, while the block drops empty bug headings. Verified: the bug template's skeleton. | fixed: bug headings sit at level `####` under the case heading, without the summary line or `<details>` wrapper; "Keep every heading" and its Rules row now name the failure block's exception. |
| 6 | contradiction | Where copies go; Filling the report, Failures | Not blocking. The report, a page committed under `docs/records/`, names evidence "by name only", in a folder on the runner's machine, "so a reader asks the runner for them". Extend the workspace's step 4 says never to point a reader at "any file only one machine holds", and the bug template's evidence rule says never to link what "only you can open", yet the failure block is lifted into a draft ticket. Keeping evidence out of the repository is a reason for an exception, but the page does not label it as one. Verified: the three texts. | fixed: Where copies go labels the by-name rule as a deliberate exception for personal data, holding until triage deletes and marks the evidence; a filed ticket gets the evidence attached. |
| 7 | contradiction | The report: report.md, the field table | Not blocking. "Commit under test" holds one commit and "the repository". Regression run's step 3 records `git -C src/<repo> rev-parse HEAD` "for each repository the run covers", so a run over two repositories has two commits and one field. Verified: the two texts. | fixed: the field now holds one `repository@commit` per repository, comma-separated, matching regression run's step 3. |

## Checked with no finding

- trigger: the purpose line and **In short** name the three files and their readers; regression run's step 10 and regression triage's step 2 link the page at the point they write and read the set, and the templates README row says when to use it.
- enforcement: each must and never on the page has a Rules row tagged `prose`; the run's commit links procedure endings rather than restating it.
- placement: the commit rule links procedure endings, and the personal-data section is the one place regression run's step 11 links for it.
- eval-case: a lane template carries no proof keys; regression run and regression triage, which ask the behavior, are marked `proof: unproven` with `prove-by: M10`. Verified: their front matter.

## Re-check

A fresh session's reading after the fix round, on `1a18d68` with the uncommitted change of the B4 slice session. Read the whole page, the contract, procedure endings, and each page the changed text links to: regression run, regression triage, the bug report template's skeleton and layout's page kinds. Checked the two `.tsv` examples still hold tabs: `grep -P '\t' -c` counts four lines, the two header lines and the two example lines.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | Verified: "The results file" now holds one line per case the run considered, selected or skipped. The summary's skipped count has lines to match. |
| 2 | fixed in part | Verified: `skipped` now covers a human case left for the device checklist. The results file says a case's list ends at its first failed checkpoint, and a skipped case's list is empty. The person writes each result on its checklist line. But "where triage reads it" has no step behind it: regression triage's step 2 loads no checklist results. That gap is recorded under regression triage's re-check. |
| 3 | upheld | Verified: the Failures bullet maps a failed sink check with every checkpoint passed: every step, and the sink check as the acceptance criterion. |
| 4 | upheld | Verified: the previous run is the newest earlier folder with the same Environment, as regression run's step 10 says. Normalization runs timestamps, then ids, then digit runs, and the example shows `<n>`. |
| 5 | upheld | Verified: bug headings sit at level `####`, without the summary line or the `<details>` wrapper. The heading rule and its Rules row name the failure block's exception. |
| 6 | upheld | Verified: "Where copies go" labels the by-name rule as a deliberate exception that holds until triage deletes and marks the evidence. A filed ticket gets the evidence attached, as the bug template's evidence rules say. |
| 7 | upheld | Verified: the Commit under test field holds one `repository@commit` per repository, matching regression run's step 3. |

What a fix broke: none beyond finding 2's open part.

What the first reading missed: none.

## Known defects

What stays open after the one fix round the plan allows, each not blocking.

- Not blocking, finding 2's open part: "where triage reads it" has no step behind it in regression triage. Known defect, for the docs audit; regression triage's record carries the same gap for M10.
