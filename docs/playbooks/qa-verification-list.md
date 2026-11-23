---
kind: playbook
lane: qa
proof: unproven
prove-by: M6
last-reviewed: 2026-11-23
---

# QA verification list

Rules for choosing what goes in a document QA reads, such as a QA test plan, for the agent or person writing or checking it.

**In short:** QA (quality assurance, the people who test a release) gets only what they can see and do. Each item is a checkbox: the place, the action, the observable result. Two sections are always present: what not to file, and what is not in this release. The writer runs a self-check before handing the document on.

This is a lane draft: QA lane. It has not been run on real work yet; M6 runs it, as [decision 0006](../decisions/0006-what-proven-means.md) says.

## What this page does and does not do

It selects. It says which items go in a document QA reads, and which stay out. It does not teach testing, and it does not lay the document out. The layout of a test plan is the [QA test plan template](../templates/qa-test-plan.md).

The output is a document for the person to hand on. Posting it on the tracker is an outward write.

## The rules

Each rule has a number, so the self-check in step 5 can name it.

1. **Only what QA can observe.** An item names something QA sees on a screen, in an email, in a file they download or in a report they open. A change QA cannot observe stays out, or appears only as its visible effect.
2. **Nothing on builds or CI.** No pipelines, jobs, branches, merges or deployment steps. The one exception: "Before you start" names the build to test, by the version QA sees. The test notes that tracker operations' "Ready for testing" row writes are a tracker field, not a document written from this page, and are outside this rule.
3. **No claims about QA's past work.** Never write what QA found, missed or tested before.
4. **No fix history.** Say what is true in this build. Never say what was tried, reverted or changed on the way.
5. **Each caveat once.** A warning appears in one place. Other items point to it, or leave it out.
6. **Each item is a checkbox with three parts.** The place (the screen or page, by the name QA sees), the action, and the observable result.
7. **Plain language.** No code names, routes, status codes or field ids. Explain any term QA would not use themselves.
8. **Links named as QA meets them.** A link's text is the label QA sees on screen, such as "Orders, then Holds". Never a raw address as the text.
9. **Every count matches its list.** If a sentence says "four scenarios", the list holds four.
10. **Two sections always present.** The do-not-file table and the not-in-this-release list. An empty one says "none".

## Steps

1. **Gather the scope.** Input: the request, naming a release or a change and its ticket keys. Read each ticket as [tracker operations](tracker-operations.md#steps) says in its steps 1 and 2; that page's draft mode applies when the session has no tracker tool. Note the key of the item's QA sub-task when it has one. Default: when the request is to check an existing document, take that document and go to step 5. Otherwise, when the request names no ticket, ask the person which; with no answer, stop at step 7 and report what is missing. Output: the changes in scope, the known issues QA may meet, and the QA sub-task's key.
2. **Select items.** Input: the changes from step 1. Keep each change QA can observe, under rule 1. Turn a change QA cannot observe into its visible effect, or drop it. Output: the list of observable changes. Default: when you cannot tell whether QA can see a change, leave it out and name it in the report.
3. **Write each item.** Input: the observable changes. Write each as a checkbox under rule 6: place, action, result. Group the items into scenarios, one per user journey. Output: the scenario checklists.
4. **Fill the two fixed sections.** Input: the known issues from step 1, and anything the request or the tickets exclude from this release. Each known issue becomes a do-not-file row: what QA sees, why it is expected, and its ticket. Each exclusion becomes a not-in-this-release line. Output: both sections, each holding "none" when empty.
5. **Run the self-check.** Input: the whole document. Go through the rules in order. For each, read the document and note pass, or the item that breaks it. Fix each break, then run the check again. Output: a line per rule, each pass. Default: stop after two rounds; report any rule still failing, with the item.
6. **Hand it on.** Input: the checked document, and the QA sub-task's key from step 1. Give it in your reply for the person to hand on. Posting it on the QA sub-task is a tracker write: make it only as [tracker operations](tracker-operations.md#steps) says in its steps 3 to 6, including its [yes rules](tracker-operations.md#which-writes-need-a-yes) and its read-back. A request that names the posting is its yes. Default: post nothing when the request does not name the posting, when step 1 found no QA sub-task or more than one, or when a rule still fails after step 5. The report then says the document is waiting for the person, and why. Output: the document, and any write made.
7. **Finish.** End as [procedure endings](../procedure-endings.md) says. The report includes the document and the self-check's result per rule. It names each change step 2 left out, and any tracker write made or waiting.

Stop when the report is given.

## Rules

| Rule | Enforced by |
|---|---|
| An item in a document QA reads names only what QA can observe. | `prose` |
| The document says nothing on builds or CI, apart from the build to test by its visible version. | `prose` |
| Never claim anything about QA's past work. | `prose` |
| Never give fix history; state what is true in this build. | `prose` |
| Each caveat appears once. | `prose` |
| Each item is a checkbox naming the place, the action and the observable result. | `prose` |
| Plain language: never a code name, route, status code or field id. | `prose` |
| Links are named as QA meets them on screen. | `prose` |
| Every count matches its list. | `prose` |
| The do-not-file table and the not-in-this-release list are always present; an empty one says "none". | `prose` |
| The writer runs the self-check over every rule before handing the document on. | `prose` |
| Posting the document on the tracker follows tracker operations; with no yes, nothing is posted. | `prose` |
