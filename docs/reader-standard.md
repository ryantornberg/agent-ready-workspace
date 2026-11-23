---
kind: reference
last-reviewed: 2026-11-22
---

# Reader standard

The shape of three templates a person reads, and the naming and credit rules for every page, for anyone writing a page or template.

**In short:** three templates, and every copy of them, name their reader and open with a short top layer. They use fixed headings in a fixed order, and give one worked example. Every page uses the industry's standard term in its title, and may credit its sources under "References".

## Who it binds

The four shape rules bind exactly three templates and every copy made from them: the [bug report](templates/bug-ticket.md), the [pull request description](templates/pull-request.md) and the [project hub](templates/hub.md). Another template comes under them only when its own opening says so and links this page. Pages already here are not retrofitted. The rules on names and on references bind every page added from 2026-11-22 on.

How to write the words on any page is on [the style guide](authoring.md). The kinds, front matter and opening every page carries are on [layout](layout.md).

## The shape

1. **It names its reader.** The template's purpose sentence says who reads it, as [the opening](layout.md#the-opening) already asks. It also names the reader of each copy, such as "a product manager, a tester or a triage meeting".
2. **It opens with a top layer under a word budget.** The top layer is what a reader who stops early still gets. On the template page, it is the opening through the **In short** line, at most 120 words. The template names its copies' top layer and budget, such as a ticket's summary of two sentences at most.
3. **Its headings are fixed, in a fixed order.** The template gives them. Two writers filling it for the same thing then produce the same page. The template also says whether an empty heading is dropped or kept with "none".
4. **It gives one worked example.** The template shows one filled-in copy, invented where this repository has no real one, and says what is invented.

Detail the top layer's reader does not need goes below it. Put it under later headings, or in a collapsed section where the format has one.

## Names

- A title uses the industry's standard term where one exists, such as "bug report" or "red team review".
- A term coined here stays only as a search word in the page's row of `INDEX.md`'s Topics table. It never goes in the "Search aliases" table, which maps words to names in the code; the `aliases` check fails any other row there.
- `INDEX.md` is covered by the eval, so its rows are added in a batch, as [maintain the workspace](maintain-the-workspace.md#when-a-duty-falls-due) says in step 4.
- Names are settled before the page is wrapped or recorded: see [the style guide](authoring.md#names-and-scope).

## References

A page may end with a `## References` heading, after its rules table. It lists the sources for a named technique the page adopts.

- It is credit only. The page's rules stand on their own text, never on a source.
- List only a source you opened and read while building the page. Give its title, its author or publisher, a link, and the technique it is credited for.
- The [instruction review](playbooks/instruction-review.md#steps) checks each source against the credit, as its step 3 says.
- Do not compare the workspace with the source, or claim it does something the source does not.

## Rules

| Rule | Enforced by |
|---|---|
| The bug report, pull request description and project hub templates, and each copy, name their reader, open with a top layer under its budget, keep fixed headings in a fixed order, and give one worked example. | `prose` |
| A bound template's own top layer, through its **In short** line, holds at most 120 words. | `prose` |
| A title uses the industry's standard term where one exists; a coined term stays only as a search word in its page's `INDEX.md` Topics row. | `prose` |
| A coined term never goes in `INDEX.md`'s "Search aliases" table. | `aliases#a row it cannot read is an error, not a pass` |
| A source under "References" is one the builder opened and read, cited as credit only and with no comparison. | `prose` |
