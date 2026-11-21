---
kind: decision
status: accepted
last-reviewed: 2026-11-21
---

# 0006: What proven means

**In short:** every playbook and how-to says in its front matter whether it is proven. A proven page has a real run on record and an eval in which it beats the bare model and two lines, and the eval gate holds it there. An unproven page ships, labelled, and names the milestone that is to prove it. Neither mark moves without a record.

## Context

Until M3, every page in `docs/playbooks/` needed an eval case that beat the bare model, and there was one playbook. M3 ports about 60 pages. About 29 of them are procedures an agent follows. Proving those now is not honest: an eval case must come from a real task, this workspace has two milestones of them, and many procedures need machinery from M4 or M8 before they can run at all.

Two easy answers were wrong. Shipping the procedures with no mark tells a reader they carry the same weight as the one that was measured. Holding them back until each is proven keeps out pages people need now.

## Decision

**The mark.** A playbook or how-to carries `proof: proven` or `proof: unproven` in its front matter. A section merged into another page carries its own mark, in a line right under its heading: `Proof: unproven, prove-by M6.` or `Proof: proven, proven-by <list>.`. The label lives in those keys only, not in the purpose line. A tutorial, a reference page, a template or a record carries none.

**Proven.** A page is proven when both hold:

- a real run is on record: a milestone record or a fix record of the procedure used on real work, named in `proven-by` as a repository path;
- an eval passes for it: pooled across its cases, 40 or more runs per arm, the guided arm beats the two-line arm by a one-sided Fisher exact test at p < 0.05, and beats the bare arm in each case.

From then on the `eval_record` check holds it there. Each new recording's guided arm may pass no more than 3 runs fewer, pooled, than the previous record's, nor than the anchor's: the record that passed when the page was marked proven, named in `proven-by` as `<sha>:evals/runs/<case>/record.json`. The anchor is pinned to a commit because each recording overwrites a case's record file. Its commit must stay reachable from main, so this repository merges with merge commits only. An arm that misses its margin may be recorded once more, and the two are judged pooled, at a margin of 6.

**Unproven.** An unproven page names in `prove-by` the milestone whose program runs the procedure on real work. The `proof` check fails it once that milestone's record is signed off. A `prove-by` newly set to a milestone being built fails, since a page cannot be proven by the milestone that writes it. Moving `prove-by` later is refused unless a failed proof attempt is on record for the milestone it moves away from: a record under `evals/runs/` that names the page, that milestone and the verdict "not proven", added while that milestone was in the manifest's `building` list. An old attempt does not license a second move.

**The marks do not move quietly.**

- A page renamed with its proof keys changed is refused.
- Changing an existing anchor needs a line `Anchor: <page> <old> -> <new>` under an approved entry in "Changes after approval" of the plan whose `milestone` is being built. The entry is a `### YYYY-MM-DD` heading followed by an `Approved by: <name>, <date>` line. That approval is self-attested, like plan approval.
- Marking a proven page or section unproven again, or removing its mark, needs a line `Demote: <page>` under such an entry. Without it, one edit would take a page out of the eval gate. Added on 2026-11-18, after a side review of slice A0; see the M3 plan's changes after approval.
- A commit that adds or changes an anchor merges through a pull request, never a straight push to main. The `direct_push` check refuses it.

**The keys are bookkeeping, not guidance.** The eval runner takes them out, in their exact forms only, before a gated arm reads a page, and the eval hash ignores the same text through the same function (`evals/proofkeys.py`). So marking a page proven does not stale the record that proved it. Any other spelling is hashed and read, and `page_kinds` fails it, so a variant cannot hide text from the hash.

**Cutting.** A page whose proof attempt shows the bare model doing as well is cut. Cutting a page that holds facts or a rules table removes its procedure steps only. Its facts and rules stay, as a reference page.

**Plans name their milestone.** A plan carries `milestone: M<n>` in its front matter. Front matter is not a section that template rule 6 freezes, so an approved plan may gain it.

Amended 2026-11-21, M3 slice B1, after its instruction review; no rule changes, and each sentence states what the `proof` check already reads. The `milestone` key is optional, and M1's and M2's plans have none; the anchor and demotion lines count only in a plan whose `milestone` is being built. A failed proof attempt is the record that `python3 evals/run.py <case> --baseline --attempt M<n>` writes to `evals/runs/<case>/baseline/record.json`, holding `page`, `milestone` and the verdict `not proven`. For a marked section, the `<page>` in an `Anchor:` or `Demote:` line is the page's path, then `#`, then the heading in lower case, with every character but letters, digits, underscores, hyphens and spaces dropped and each space turned into a hyphen, such as `docs/playbooks/fix-a-bug.md#the-gates`.

## What it gave up

- **A reader must look at the mark.** An unproven page reads like any other. The README's table lists every page's state, and the check holds the table to the pages.
- **The gate on proven pages got stricter, and costlier.** Each proven playbook must now beat two lines on its own cases, not pooled with others, and keep near its past.
- **The approvals are self-attested.** The check reads an `Approved by` line; it cannot tell who wrote it.

## Rejected

- **Gating every procedure on an eval now.** Cases would come from guesses, not real work, and the gate would measure the guesses.
- **A label in the purpose line.** It would be guidance an agent reads, inside the hash, so marking a page proven would stale its own record.
- **Comparing with the previous record only.** Slips of 3 could add up: 45, 42, 39 would each pass. The anchor stops that.

## Rules

| Rule | Enforced by |
|---|---|
| Every playbook and how-to carries `proof`, and an unproven one names `prove-by`. | `page_kinds#a playbook without proof fails`, `proof#an unproven page with no prove-by fails` |
| An unproven page fails once its `prove-by` milestone is signed off. | `proof#an unproven page whose prove-by milestone is signed off fails` |
| `prove-by` moves later only with a failed attempt on record for the milestone it leaves. | `proof#prove-by moved later with no failed attempt fails` |
| A proven page names a real-run record and passes its eval, held to its previous record and its anchor. | `proof#a proven page whose evidence is only eval records fails`, `eval_record#4 runs below the anchor fails, though the previous record is matched` |
| An anchor changes, and a proven page is demoted, only with an approved change entry. | `proof#an anchor changed without an approved change fails`, `proof#a proven page marked unproven again fails without an approved change` |
| A commit that changes an anchor reaches main through a pull request. | `direct_push#a doc commit that changes a proof anchor fails` |
| The README's table matches the pages. | `proof#a README row that disagrees with the page fails` |
