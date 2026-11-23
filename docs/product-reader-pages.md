---
kind: reference
lane: product
last-reviewed: 2026-11-23
---

# Pages for a product reader

Rules for a page whose reader is a product manager or another non-developer, such as a triage sheet. For anyone writing one, person or agent.

**In short:** these rules add to the [style guide](authoring.md) and the [reader standard](reader-standard.md), which still apply. Color is welcome when the colored text says its meaning in plain words. A status that asks for a decision sits under text naming the choices. Never use a code the reader must learn first. The page asks for edits or a reply, never a column filled on every row.

This is a lane draft: product lane. It has not been used on real work yet; M9 first uses it on real work.

## Which pages these rules bind

A page is for a product reader when its purpose sentence names a non-developer as its reader, or when the procedure or template that makes it says so. Examples: the sheet a [bug triage meeting](playbooks/bug-triage-meeting.md) runs from, and a copy of the [QA test plan](templates/qa-test-plan.md). A page with mixed readers follows these rules in the part the product reader reads.

## The rules

1. **Color carries words, not meaning alone.** Color a cell or a word when it helps the eye. The colored text itself says what it means, such as "Blocks launch", never a bare red dot. A reader who cannot see the color still gets the meaning.
2. **A decision names its choices.** A status that asks the reader to decide sits under text that names each choice and what follows from it. For example: "Decide one: fix before launch, fix after launch, or reject."
3. **No code to learn first.** Write what a label, key or field means in plain words. A tracker label such as `affects:end-user` appears as "Affects end users". A ticket key may appear as a link, beside a plain title.
4. **Ask for edits or a reply.** The page asks the reader to edit it or to answer. It never asks the reader to fill in a column on every row. A column the team fills in together during a meeting is fine, such as a triage meeting's outcome. So is a tester's checklist, such as a QA test plan's scenarios and sign-off. Ticking it is the testing itself, not a form to fill in.

## Where a page goes

Writing such a page in this repository commits as [procedure endings](procedure-endings.md#the-commit) says. Posting it anywhere else, such as on a tracker, a wiki or a chat, is an outward write: [procedure endings](procedure-endings.md#outward-writes) says when it needs a yes.

## Rules

| Rule | Enforced by |
|---|---|
| A page for a product reader follows the style guide and the reader standard as well as this page. | `prose` |
| Color never carries meaning alone; the colored text says it in plain words. | `prose` |
| A status that asks for a decision sits under text that names the choices. | `prose` |
| Never use a code the reader must learn first; write its meaning in plain words. | `prose` |
| The page asks for edits or a reply, never for a column filled in on every row; a column the team fills during a meeting, or a tester's checklist, is fine. | `prose` |
