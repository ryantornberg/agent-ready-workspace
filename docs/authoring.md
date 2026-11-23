---
kind: reference
last-reviewed: 2026-11-22
---

# Style guide

The authoring conventions for every page written from 2026-11-22 on, for anyone writing or editing a page, person or agent.

**In short:** write plain prose in short sentences. Settle a page's name and scope before it is wrapped or recorded. State each rule once, on the page that owns it, and link to it from everywhere else. Cite a heading, never a line number. The page's shape is on [layout](layout.md) and the [reader standard](reader-standard.md).

## Who it binds

Every page added from 2026-11-22 on follows this page. Pages already here are not retrofitted. A sentence you write or change on an older page follows it.

## Where the other conventions live

| Topic | Page |
|---|---|
| Folders, page kinds, front matter, the opening, archiving | [Layout](layout.md) |
| The shape of a page a person reads; standard terms; the "References" heading | [Reader standard](reader-standard.md) |
| How a playbook or how-to ends | [Procedure endings](procedure-endings.md) |
| Commit subjects and trailers | [Commits](commits.md) |
| Adding a page, and keeping pages true | [Extend the workspace](extend-the-workspace.md), [maintain the workspace](maintain-the-workspace.md) |
| What the checks catch on a page | [Maintain the workspace](maintain-the-workspace.md#what-the-checks-catch-for-you) |
| The review a guidance page gets | [The instruction review](playbooks/instruction-review.md) |

## Writing

- Say what you mean, in plain words. Where a literal phrase exists, use it.
- Keep sentences to 25 words or fewer, one idea each, in the active voice.
- Explain each technical term or acronym where it first appears, or link the [glossary](glossary.md).
- Use US spelling. No emojis.
- Never hard-wrap a paragraph. Write one line per paragraph or list item.
- Use a list or a table when the content is a set of like items. Use prose when an argument needs defending.
- State what is true now. Do not narrate how the page or the work came about; that belongs in a record.
- Name machinery that is not built yet, and end the page with its `## Rules` table, as step 4 of [extend the workspace](extend-the-workspace.md#steps) says.

## Names and scope

A page's title and purpose sentence decide when a reader opens it, and when an agent's guidance fires. So settle them early.

- Name the page with the industry's standard term, as the [reader standard](reader-standard.md#names) says.
- Make the purpose sentence state the page's real scope: everything the page covers, and nothing it does not.
- Settle the name and the scope before the page gets a wrapper or an eval run on record. A rename after that means changing the wrapper, its cases and the record too.

## One rule, one page

State each rule once, on the page that owns it. Every other page links to it. A copy drifts from the original, and then a reader cannot tell which one holds.

For example, [procedure endings](procedure-endings.md) states how every procedure commits, pushes and reports. A playbook links it instead of repeating those steps. The [instruction review](playbooks/instruction-review.md#the-six-checks) counts a restated rule as a placement finding.

## Links and citations

- Link a page by its relative path, and a section by its heading's anchor. The `links` check fails a link to a page or heading that does not exist.
- Cite code by file and name, such as a class or function. Never cite a line number on a page: lines move. The `line_cites` check refuses one, unless a commit hash pins it.
- Link a file of this workspace from outside it, such as from a pull request, by its full URL, as [git-host operations](playbooks/git-host-operations.md#the-operations) says.

## Rules

| Rule | Enforced by |
|---|---|
| Sentences have 25 words or fewer, in plain words and the active voice. Prose is never hard-wrapped, holds no emojis, and never narrates how the page or the work came about. | `prose` |
| A page's name and scope are settled before it gets a wrapper or an eval run on record. | `prose` |
| A rule is stated once, on the page that owns it, and linked from everywhere else. | `prose` |
| A link names a page or heading that exists. | `links#a missing file fails`, `links#a missing heading fails` |
| A page never cites a file by line number, unless a commit hash pins it. | `line_cites#an added line that cites a file by line number fails` |
