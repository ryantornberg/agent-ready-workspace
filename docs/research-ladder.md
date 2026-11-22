---
kind: how-to
proof: unproven
prove-by: M4
last-reviewed: 2026-11-21
---

# Research ladder

How to find something in this workspace with the cheapest lookup that can answer it. For any agent, or person, about to search.

**In short:** pick the one lookup that fits what you already know, and do not stack lookups. When a finding should have been written down, offer in one line to write it in one place, and write only on a yes.

## Pick one lookup

The rows run from cheapest to dearest. Start at the row that matches what you already know, not at the top.

| You already have | Use | You get |
|---|---|---|
| An exact name from the code | `python3 tools/symbols.py NAME src` | The file and line where it is defined. |
| An everyday word for something in the code, such as "the nightly job" | [INDEX.md's search aliases](../INDEX.md#search-aliases) | The name the code uses. |
| A topic and no name | [INDEX.md's topics](../INDEX.md#topics) | The page that owns the topic. |
| A kind of change, and you need every path it touches | [INDEX.md's cross-cutting chains](../INDEX.md#cross-cutting-chains) | The list of paths. |
| Part of a name | `python3 tools/symbols.py --contains PART src` | Every definition whose name holds it. |
| Text that is not a name, such as a message or a setting | `git grep -n "TEXT"` | Every line that holds it. |
| A question about how a library or tool behaves | Its current documentation, read live, not from memory. The domains a web read may reach without asking are in [agent settings](agent-settings.md#the-documentation-domains). | The behavior of the version in use. |
| A question that needs many files read | A sweep handed to a helper, as [delegating](orchestration.md#delegating) says. | Conclusions, not files. |

Do not stack lookups. Never run a second lookup to confirm what the first one found, and never run several at once on the same question.

Move to another row only in two cases. The lookup you picked gave you something new, such as a code name from an alias: then you know more, so pick again from the table. Or it came back empty: then take the next row down that still fits what you have. When the last row that fits comes back empty too, stop searching. The workspace does not hold the answer: say so in your report, with the lookups you ran, and ask the person what to do next. When the answer needs sources outside the workspace, such as a tracker, a wiki, mail or chat, and the person asks for them, follow [search every source](playbooks/search-every-source.md).

## Offer to write a finding down

Sometimes a search shows that the workspace should have told you the answer. An everyday word had no alias, or a fact took a long hunt. Then offer, in one line, to write it in one place. Name the place. Write only if the person says yes. With no answer, as in a run nobody is watching, write nothing and put the offer in your report.

| The finding | The one place |
|---|---|
| An everyday word the code calls by another name, or a topic with no row | A row in [INDEX.md](../INDEX.md) |
| A fact that holds for every edit in one folder | A [rule page](rules/) for that folder |
| A fact that needs explaining, about one topic | The page under `docs/` that owns the topic |
| A trap every session must know, in three lines or fewer | [AGENTS.md](../AGENTS.md#facts-a-model-cannot-derive) |

Each of these writes is a change to a guidance page, so it gets an [instruction review](playbooks/instruction-review.md). A change to a file the eval covers, such as INDEX.md, AGENTS.md or a rule page an eval case names, also needs a new eval run, as the contract's rules say, so batch those.

The question log is not an offer. If you had to ask a person something the workspace should have answered, the contract says to add it to the [question log](question-log.md) before you finish, with or without a yes.

## Rules

| Rule | Enforced by |
|---|---|
| Pick the one lookup that fits what you know; never stack lookups. | `prose` |
| Offer to write a finding in one place only, and write only on a yes. | `prose` |
