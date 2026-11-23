---
kind: template
last-reviewed: 2026-11-22
---

# Bug report template

The shape of a bug ticket, in two layers, for anyone filing one on a team's tracker, person or agent.

**In short:** search for a duplicate first. Then write a plain top layer anyone can read: a title, a one- or two-sentence summary, and four headings in a fixed order. Put the technical detail in one collapsed section for developers. Every claim is one you checked. Describe the fault and point at it; never plan the fix.

## When to use it

Use it when a request asks you to file a bug, or to write one up for a person to file. Use it too to rewrite a stale bug ticket. Grooming a bug, and the labels triage adds, belong to the product lane.

Filing a ticket is an outward write. Before you file, follow [outward writes](../procedure-endings.md#outward-writes). Make the write itself as [tracker operations](../playbooks/tracker-operations.md) says, including what to do when the session has no tool for the tracker.

## Why two layers

A product manager, a tester and a triage meeting need to read a ticket without knowing the code. A developer needs every claim checked and pointed at. Writing for both in one layer either softens the claims or loses the plain reader. So the top layer is plain, and the detail sits below it, unsoftened.

The headings come in a fixed order so that two people filing the same bug write the same ticket.

## Where tickets live

On the team's tracker. This workspace's own repository is not a tracker, even when its host has issues turned on. File there only when the team's tracker is that repository. The tracker provider is planned for M8.

Where the tracker is GitHub's issues, the skeleton below works as it stands. File it on the tracker's repository with `gh issue create --repo OWNER/REPO --title "TITLE" --body-file FILE`. Always name the repository: without `--repo`, `gh` files on the repository of the current folder, which is often this workspace. The yes the write needs is as [tracker operations](../playbooks/tracker-operations.md#which-writes-need-a-yes) says.

## Before you write

1. **Search for a duplicate.** Search the tracker, open and closed tickets, for the same fault in the person's words and in the code's names. When one exists, file nothing new: offer to add what you found to it, which is a write on that ticket.
2. **Check every claim.** Reproduce the fault yourself, and record the commit you measured on. A claim you could not check stays out of the ticket, or goes under "Out of scope" as unknown.

## Skeleton

The tracker's rich format may offer a highlighted panel and a collapsible section. Use them there. In plain markdown, such as a GitHub issue, use a quote block for the summary and a `<details>` block for the developer layer, as below. Keep the blank line after the `<summary>` line, or the headings inside will not render.

```markdown
> <What goes wrong, and for whom. Two sentences at most.>

### Impact

<Who is affected, and how many. Whether it happens in live use. Whether there is a workaround.>

### Expected and actual

Expected: <what should happen>
Actual: <what happens>

### How to reproduce

1. <step>
2. <step>

### Acceptance criteria

- <What will be observably true once the bug is fixed.>

<details>
<summary>For developers</summary>

### Environment and version

<The environment, the build or version, and the commit the fault was measured on.>

### Evidence

<Links, attached files and numbers, as the evidence rules say.>

### Code pointer

<The file and the class, function or method, by name.>

### Suggested direction

<Where a fix might start. A direction, not a plan.>

### Out of scope

<What this ticket does not cover; dead ends already tried; claims an earlier version of this ticket made that re-checking disproved.>

</details>

Analysis: <optional, one line: a link to a longer analysis>
```

## Filling it

**Order.** Keep the headings in the skeleton's order. Drop a heading that has nothing under it; never reorder them.

**The top layer** is the title, the summary and the four headings above the collapsed section. Its readers are a product manager, a tester or a triage meeting. It stays under 200 words, and follows the [reader standard](../reader-standard.md). It holds no status code, route, method name or other term from the code. Those go below.

**Title.** What goes wrong for a person, then what sets it off. No mechanism, and no product or app name in front.

**Summary.** What goes wrong, and for whom, in one or two sentences.

**Impact.**

- Say who is affected and how many, whether it happens in live use, and whether a workaround exists.
- When the count is unknown, say so. Then say who is exposed, and under what condition.
- Do not state whether the product has launched. Every reader knows, and the sentence goes stale on every ticket at once. Describe the impact as it will be once people use the code.
- When nobody would be affected even then, say so. Then give what the bug costs the team now, and the event that would turn it into a fault people see. A bug with neither is not ready for grooming.

**A field restated in prose.** Repeat a tracker field in the text only when it changes the impact. Then write the condition it creates, not the field's value.

**Acceptance criteria.** Each one says what will be observably true, never the change to make. If you cannot write one that way, the fault is not understood well enough to file.

**Evidence.**

- Link to something that will still be there: a commit, a pinned version, a file attached to the ticket. Never a link that expires or that only you can open.
- Attach screenshots and recordings to the ticket itself.
- An attached text file, such as a log, opens with three labelled lines. `What:` says what it is, `Source:` the command or place it came from, and `Taken:` the date and time.
- Every number says how it was obtained: the command, the query or the count.
- Record the commit the measurement ran against, so a reader can repeat it.

**Code pointer.** Name the file and the class or function. Do not give a line number: lines move.

**Out of scope.** Besides what the ticket does not cover, list the dead ends already tried. When re-checking disproves a claim an earlier version of the ticket made, move the claim here with what disproved it. Do not delete it. A disproved claim deleted without trace gets worked out again, wrongly, by the next reader.

**Filing it.** File at the tracker's first status. Leave the fields triage sets, such as priority and severity, empty.

## A worked example

The ticket below is invented; the code it points at is real. It shows a top layer with no code terms, and a disproved claim kept under "Out of scope". The title goes in the tracker's title field; the fenced block is the body.

Title: Finance import skips the first order of the quarter when it loads the quarterly orders report

```markdown
> When the finance team loads the quarterly orders report into its accounting import, the first order of the quarter is missing. Quarter totals come out low by that order's amount.

### Impact

Everyone who loads the report into the accounting import, every quarter. How many quarters were affected so far is unknown. The workaround is to add the missing order by hand.

### Expected and actual

Expected: every order of the quarter is loaded.
Actual: the first order is skipped; all the others load.

### How to reproduce

1. Download the quarterly orders report for a quarter with at least two orders.
2. Load it into the accounting import.
3. Compare the number of orders loaded with the number of orders in the quarter.

### Acceptance criteria

- Loading the report brings in every order of the quarter.
- The import's quarter total equals the sum of every order in the quarter.

<details>
<summary>For developers</summary>

### Environment and version

orders-web at commit <sha>, on the test environment.

### Evidence

- `orders-2026-Q3.csv`, attached. Its first line is an order, not column names.
- The file holds 412 lines and the quarter has 412 orders: `wc -l orders-2026-Q3.csv`, and the count of orders for the quarter from the order store. The import loaded 411.

### Code pointer

`QuarterlyExport.toCsv` in `src/orders-web/quarterlyExport.ts`. It writes one line per order and no header line.

### Suggested direction

The import treats the first line as column names. A header line before the rows would match what it expects.

### Out of scope

- The import's settings: it has no option to read a file without column names.
- An earlier version of this ticket said the last order was missing too. Re-checking disproved it: the last order loads.

</details>
```

## Rules

| Rule | Enforced by |
|---|---|
| Search for a duplicate before filing a new ticket. | `prose` |
| Every claim in a ticket is one the filer checked. | `prose` |
| Headings keep the skeleton's order; an empty heading is dropped, never reordered. | `prose` |
| The top layer holds no status code, route, method name or other term from the code. | `prose` |
| An acceptance criterion says what will be observably true, never the change to make. | `prose` |
| A claim that re-checking disproved moves to "Out of scope"; it is never deleted. | `prose` |
| A ticket never restates whether the product has launched. | `prose` |
| A ticket is filed at the tracker's first status, with the fields triage sets left empty. | `prose` |
| A ticket describes the fault and points at it; it never plans the fix. | `prose` |
| A ticket is filed on the team's tracker, and `gh issue create` always names its repository with `--repo`. It is never filed on this workspace's repository unless that is the team's tracker. | `prose` |
| Evidence never links to something that expires or that only the filer can open. | `prose` |
| A code pointer never gives a line number. | `prose` |
