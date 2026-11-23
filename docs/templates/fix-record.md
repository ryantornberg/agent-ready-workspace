---
kind: template
last-reviewed: 2026-11-22
---

# Fix record template

The dated record that one bug fix leaves behind, for the agent making the fix and anyone later checking what it proved.

**In short:** one file per fix in `docs/records/fixes/`, opened when the fix starts and filled as it goes. It holds the fix brief when there is one, where the work stands, and a `## Report` whose every claim line is marked verified or inferred. The `claim_marks` check reads that report.

## When to write one

Open a fix record when you start a fix on the [fix a bug](../playbooks/fix-a-bug.md) path, and fill it in at each step, not from memory at the end. Its report is the report that page ends with.

A fix that is a slice of a hand-off plan needs no fix record. Its report goes under the plan's "Results", as step 6 of the [hand-off plan template](hand-off-plan.md#how-to-use-it) says for every slice.

## Where copies live

In `docs/records/fixes/`, one file per fix, named `<YYYY-MM-DD>-<topic>.md`. The date is the day the fix started. The topic is the tracker item's key when there is one, otherwise a few words for the bug in lowercase with hyphens, such as `2026-11-22-export-button.md`. The first fix record creates the folder.

A fix record is a record page: front matter `kind: record` and `last-reviewed`, then the opening [layout](../layout.md#the-opening) gives a record.

## Skeleton

```markdown
---
kind: record
last-reviewed: YYYY-MM-DD
---

# Fix: <the bug, in a few words>

<One sentence: which bug this record covers, and who reads it.>

**In short:** <what was wrong, what the fix changed, and where it stands now.>

## Brief

<The fix brief and any dated change to it after approval. Delete this section when the fix had no brief.>

## Where it stands

- Commits: <short hash and subject, one per line, in the repository that holds the fix>
- Red-green proof: <the test's name>; fails at <commit> with <what it printed>; passes at <commit>. Layer: <the layer the test exercised, such as the API handler, the database query or the screen>
- Running app: <what you checked, at which commit, and what you saw>, or "no running app"
- Pull request: <link, and draft or published>, or "none: the repository has no remote"
- Tracker item: <key and link>, or "none"

## Escape analysis

<The analysis, when escape analysis runs on this fix. Delete this section when it did not.>

## Report

Fixed: <what was wrong, in one sentence>

- verified: <something you ran, and what you saw>
- inferred: <something you reasoned out and did not check>

Not done: <anything left, and why, or "nothing">
```

## Filling it in

- **The brief.** When the fix had a brief, put it here, with any change to it after approval under a dated line. [Fix a bug](../playbooks/fix-a-bug.md) will define the brief and when a fix needs one; that section is planned for slice Z of M3. Until then, a fix with no brief deletes the section.
- **Where it stands.** Write a line only once you have run what it claims. A line you have not reached yet says "not yet". A claim written down because it looked plausible, and never checked, is how a wrong fix gets merged.
- **The layer.** The red-green line names the layer the failing test exercised. A check that passes at one layer proves nothing about another: a screen that now looks right says nothing about the server behind it. When the bug lives at a layer your test did not reach, say so under "Not done".
- **The running app.** Name the commit each check ran on. A check on an earlier commit does not count for a later one.
- **An escape analysis**, when one runs on this fix, goes in its section, before the report. Step 9 of [escape analysis](../playbooks/escape-analysis.md#steps) says what it holds.
- **The report.** Always write it, even when the work stopped early. Keep it the last section. The session's report repeats its lines. "Not done" names the same things a report in the session names, as [procedure endings](../procedure-endings.md#the-report) says.
- **Committing it.** Commit the record with the fix, on the fix's branch, with "Where it stands" filled so far. After the push, fill in the commits, the pull request and the report, then commit and push the record once more on that branch. This follows the order of [procedure endings](../procedure-endings.md#the-order): commit, push, then report. Staging and messages follow [its commit section](../procedure-endings.md#the-commit). When the fix is code in a pinned repository, its branch is not in this repository: the record is then a change of pages only here, committed and pushed as procedure endings' rows for pages say. A review is not needed again for that commit: the [review orchestrator](../playbooks/review-orchestrator.md#steps)'s step 2 counts a tip whose only change since the reviewed commit is this record as reviewed. A review round's record goes in the pull request's description, as that page's step 10 says, not here.

## What the check reads

The `claim_marks` check reads every file in `docs/records/fixes/` except a README. In each, it reads the lines from `## Report` to the next heading of level one or two, and sorts them:

- A blank line is skipped. So is a line starting with three backticks; the lines between two such lines are still read.
- A line starting `Fixed:` or `Not done:` is a header line. Keep everything it says on that line.
- Every other line is a claim line. It may start with `- ` or `* `, then `**`. Then it must start with `verified` or `inferred` in lowercase, followed by a space, a colon or `**`.

Both shapes pass: the skeleton's list, and the block of `verified  <...>` lines that the [definition of done](../definition-of-done.md#the-report) gives. Each of these fails:

- `Verified` or `Inferred` with a capital letter.
- A numbered list, such as `1. verified: ...`.
- A claim wrapped onto a second line.
- A `###` subheading inside the report.
- A bulleted list under `Not done:`. Write those items on the header line, separated by semicolons.

The check also fails a fix record with no `## Report` section. It does not check that the report comes last.

## Rules

| Rule | Enforced by |
|---|---|
| A fix record has a `## Report` section, and every claim line in it starts with verified or inferred. | `claim_marks#a fix record with no report section fails`, `claim_marks#a claim line not marked verified or inferred fails` |
| The report is the record's last section. | `prose` |
| The record is committed with the fix on the fix's branch, and again after the push with the report filled. | `prose` |
| One fix record per fix, in `docs/records/fixes/`, unless the fix is a slice of a hand-off plan. | `prose` |
| A line under "Where it stands" is written only after you ran what it claims. | `prose` |
| The red-green line names the layer the test exercised. | `prose` |
| A running-app check names the commit it ran on. | `prose` |
