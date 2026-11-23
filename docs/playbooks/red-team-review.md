---
kind: playbook
proof: unproven
prove-by: M9
last-reviewed: 2026-11-23
---

# Red team review

How a fresh red team attacks a finished hand-off plan, with its spec, or a requirements document, and how its author settles the findings. For the author and the red team.

**In short:** the author sends a fresh driver-tier session, the red team, one fixed template, with nothing added. The red team checks the claims the document rests on, writes ranked findings, a verdict and what survives to a dated record, and replies briefly. The document is not done until every finding is triaged.

## When it runs

It serves the Red team rung of [the ladder](../size-the-work.md#the-ladder), once the document is finished. For a feature, it runs on the hand-off plan after the [spec](../size-the-work.md#the-spec-process) is agreed, as [the feature ladder](../size-the-work.md#the-feature-ladder) orders it. While a design question that blocks it is still open, the document is not finished: settle it first, in a [decision interview](decision-interview.md).

It fits a finished hand-off plan or requirements document. A spec lives in three sections of a hand-off plan, as [the spec process](../size-the-work.md#the-spec-process) says, so it is reviewed with the plan that holds it, never alone. It does not fit a diff or a diagnosis. When the work in hand is a diff of code, a review of the branch or pull request goes to the [review orchestrator](review-orchestrator.md), and a question about its design alone to [architecture review](architecture-review.md). A change to a guidance page has its own review: when the work in hand is one, use the [instruction review](instruction-review.md) instead.

## Thin by design

This page stays thin on purpose. The protocol below is the whole procedure: it fixes what the red team is sent and what it must produce, never how it looks for faults. Judgment stays with the red team. Guidance on how to attack tends to anchor a red team on what the guidance names, so the template carries none. Do not add a checklist, a list of known risks or hints, here or in a dispatch.

The red team is a critic: the rule that a critic never shares the author's session, and gets the artifact and sources but not the author's conclusions, is in [fresh context for critics](../orchestration.md#fresh-context-for-critics). It is driver-tier work, as the [tiers](../orchestration.md#the-three-tiers) say.

## Steps

1. **Check that it fits.** Input: the document to review and the request. Confirm it is a hand-off plan or a requirements document, and that it is finished: every section it needs before approval is filled, and no open question it lists, such as one a decision interview left open, blocks a decision, requirement or slice in it. Sections filled later, such as a hand-off plan's red team table, approval and results, do not count. Default: if you cannot tell that it is finished, it is not. Output: the document's path, and its sources, which are the paths it names or links. If it does not fit, or is not finished, stop and report why.
2. **Decide who the red team is.** Input: what this session has done. If this session wrote or edited the document, or holds the author's reasoning about it, the red team is a fresh agent: go to step 3. If it has done neither, as when a person starts a session only to review, and it runs at the driver tier's model and effort in the `tiers` entry of [workspace.json](../../workspace.json), this session is the red team: fill the template's placeholders as step 3 says, carry out its lines yourself, commit nothing, and stop there. The author takes it from step 4. Otherwise, dispatch. Default, when unsure: dispatch.
3. **Dispatch the red team.** Input: [the template](#the-template), the document's path, its sources, today's date, and a record path, `docs/records/adversarial-reviews/<YYYY-MM-DD>-<document's file name>.md`, with that date. The folder keeps the page's older name. If that name is taken, add a word before `.md`, such as `-round-2`. Replace the four placeholders and change nothing else. Send it to one fresh agent, at the driver tier's model and effort in the `tiers` entry of [workspace.json](../../workspace.json). Output: the dispatch, its prompt the template word for word but for the placeholders.
4. **Read the reply and the record.** Input: the red team's reply. Open the record at the path you gave. Output: a record with a verdict, ranked findings and what survives. If the verdict is `does not hold`, fix nothing: commit the record alone, end as [procedure endings](../procedure-endings.md) says, and give the record's path in the report. That ends the procedure. If the record is missing or has no verdict, dispatch one more fresh red team with the same template and a new record path. If the second one also fails, stop and report.
5. **Triage every finding.** Input: the record. Verify each finding yourself before you accept it, by reading or running what its evidence cites. Then give it one disposition: `accepted`, with the fix made or the place it is queued; `rejected`, with a reason a stranger could judge; or `deferred to <where>`, with the reason. For a finding that needs a decision only a person can make, write your recommendation and ask; with nobody to ask, defer it to that person. For a hand-off plan, write the triage in its own Red team table, as the [hand-off plan template](../templates/hand-off-plan.md) asks, and link the record above the table. For any other document, write it in the record's Disposition column. Output: a disposition for every finding.
6. **Decide on another round.** Input: the triage. If the accepted fixes changed the document in substance, such as a decision, a requirement, a slice or a step, go back to step 3 with a new record path; a fixed wording, link or typo is not substance. The loop stops as [the limits](../orchestration.md#limits) say. Output: a document whose last review needs no change in substance, or a report.
7. **Finish.** Input: the record or records, and the document. End as [procedure endings](../procedure-endings.md) says: commit them together, push, and report the record's path, the verdict, and the count of findings per disposition.

Stop when every finding of the last review has a disposition and nothing in step 6 sends you back. The document is not done before then.

## The template

Send this, with only the four angle-bracket placeholders replaced. For `<sources>`, list the paths from step 1, or write `the repository` when the document names none.

```text
Tier: driver

Review this document as an adversary: <document path>
It rests on: <sources>
Check against the repository each claim the document's decisions rest on.
Write ranked findings, an explicit verdict and what survives to <record path>, in the shape under "The record" in docs/playbooks/red-team-review.md. Use <date> as the record's date.
Edit nothing else.
Reply with the record's path, the verdict, and at most five lines on the top findings.
```

## The record

The red team writes one file in `docs/records/adversarial-reviews/`. Its front matter is `kind: record`, `last-reviewed:` with the date, `covers:` with the document's path, and `reviewed-at:` with the commit the red team read. For a document not yet committed, that is the commit it sits on, followed by `, with the uncommitted change of the author`.

It opens with `# Red team review: <document path>`, a purpose sentence of 25 words or fewer, and an **In short** line giving the verdict and the number of findings. Then three sections:

- `## Verdict`: one of `holds`, `holds with fixes` or `does not hold`, and a sentence or two on why. `holds` means the document can be used as written. `holds with fixes` means it can once its top findings are fixed. `does not hold` means its core fails and it needs rethinking.
- `## Findings`: a table with the header `| # | Finding | Evidence | Disposition |`, most serious first. Evidence names what the red team read or ran, marked verified or inferred. The red team writes `open` in every Disposition cell. With no findings, the table keeps its header and the line `No findings.` follows it.
- `## What survives`: what the red team attacked that held.

## Rules

| Rule | Enforced by |
|---|---|
| A red team that is dispatched gets the template word for word but for its placeholders: never the author's reasoning, a summary of the session, or hints on what to look for. | `prose` |
| The dispatch's first line names its tier. | `handoff_tier#no tier named` |
| The red team runs at the driver tier, in a session that did not write or edit the document. A session at another model or effort dispatches. | `prose` |
| The red team writes only its record. | `prose` |
| On a `does not hold` verdict, commit the record and report to the person; never patch the document around it. | `prose` |
| Verify each finding before you accept it. | `prose` |
| A rejected or deferred finding carries a reason a stranger could judge. | `prose` |
| The document is not done until every finding of its last review has a disposition. | `prose` |
| Never add method guidance, such as a checklist or hints, to this page or to a dispatch. | `prose` |
| The author's procedure ends as [procedure endings](../procedure-endings.md) says. The red team, dispatched or not, writes its record and commits nothing; the author commits it. | `prose` |

## References

- UK Ministry of Defence, [Red Teaming Handbook](https://www.gov.uk/government/publications/a-guide-to-red-teaming), third edition, June 2021. Credited for the term and its core idea: a team formed to subject a plan's ideas and assumptions to rigorous analysis and challenge, best kept separate from the plan's authors (its "Terminology", paragraphs 1.9 and 1.10).
