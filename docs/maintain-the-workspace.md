---
kind: how-to
proof: unproven
prove-by: M5
last-reviewed: 2026-11-22
---

# Maintain the workspace

Every upkeep duty this workspace has, when each falls due and who does it. For the maintainer, and for any agent whose change sets a duty off.

**In short:** the checks catch most drift at the commit and in CI. The rest is duties: some fall due when an event happens, the others once per milestone. The maintainer owns the periodic ones.

## What the checks catch for you

These need no duty: a check finds them on its own. `python3 ws.py list` shows every part and when it runs; [parts](parts.md#the-parts-here) says what each one does.

| Drift | Caught by | When |
|---|---|---|
| A link to a page or heading that moved or went away | `links` | At the commit and in CI |
| A page with no kind, a wrong opening, or past its review date when a commit edits it | `page_kinds` | At the commit and in CI |
| Pages past their review date that nobody is editing | `stale_pages` | A notice when a session starts |
| A search alias, or a code name in the contract, that left the code | `aliases` | At the commit and in CI |
| A path in the index's cross-cutting chains that does not exist | `chains` | At the commit and in CI |
| A rules-table tag naming a part or case that does not exist | `rules` | At the commit and in CI |
| A proof mark out of step: the README's table, or an unproven page whose `prove-by` milestone is signed off | `proof` | At the commit and in CI |
| A guidance change that names no instruction review | `review_trailer` | At the commit, the push to main, and in CI |
| A change to what the eval covers, with no new run on record | `eval_record` | At the commit and in CI |
| A pinned repository behind its upstream, or pinned to a commit the upstream never merged | `stale_pins`, `pin_on_default` | A notice when a session starts; at the commit and in CI |
| The always-loaded layer past its size limit | `loaded_size` | At the commit and in CI |

The checks prove that nothing is dangling. They cannot prove a page is true: a page that contradicts last week's decision passes every one. That is what the duties below are for.

## Duties an event sets off

The session whose change sets off the event does the duty, in the same piece of work. The last two rows are the exception: the maintainer runs those, as the procedure pages say. A session that sets one off names it in its report as due, with the event, as step 2 says.

| When this happens | Do this |
|---|---|
| A page is added | Adding it is on [extend the workspace](extend-the-workspace.md). Once it lands, its upkeep is the rest of this page. |
| A page is moved, renamed or archived | Move it as [layout](layout.md#archiving-a-page) says, and fix every link to it; the `links` check names each one left. Change its row in the [playbook catalog](playbooks/README.md) or the [how-to index](how-tos.md). When it carries a proof mark, change its row in the README's proof table too; the `proof` check fails a row that disagrees. A link to it from `INDEX.md` or `AGENTS.md` is a change to a file the eval covers: step 4 says how it is committed. |
| A name in the code changes | Change its row in [INDEX.md's search aliases](../INDEX.md#search-aliases); the `aliases` check fails until you do. `INDEX.md` is a file the eval covers, so step 4 says how the change is committed. Then `git grep -n "OLD_NAME"` and fix every page that still uses the old name. |
| A word in the [glossary](glossary.md) changes meaning | `git grep -n -i "WORD" -- docs AGENTS.md INDEX.md README.md`, and fix each page that uses the old meaning. |
| A claim stops being true, such as a superseded decision, a retired part or a renamed command | `git grep -n "PHRASE"` for every restatement of it, and fix each in the same change. The checks cannot find a restatement that is merely false. |
| You edit a page past its review date | Review the whole page and move its `last-reviewed` date, as the contract's rules say; the commit check refuses the edit otherwise. |
| A pinned repository's pin moves | Run `git submodule update` before you commit the pin change, since the commit check reads the checkout on disk. Then reread the [rule pages](rules/) for that repository. This repository has no pins; an instance's first ones come in M5. |
| You had to ask a person something the workspace should have answered | Log it in the [question log](question-log.md), as the contract's rules say. Then fix the page where the next person will look. |
| The same mistake shows up twice | Turn it into a rule on the page that owns the topic, or a check or hook as [parts](parts.md) says. A part is machinery and follows [changing the machinery](changing-the-machinery.md). The lessons log for such mistakes is planned in slice B3 of M3; until then, write the lesson into the rule's text or the part's `why`. |
| You find a page that points a reader at an agent's private memory, a session's scratch folder, or any file only one machine holds | Another reader cannot open it. Write the fact on the page instead, and remove the pointer. |
| A finding should have been written down | Offer it as the research ladder's [offer to write a finding down](research-ladder.md#offer-to-write-a-finding-down) says. |
| Many pages change at once, such as a batch of new pages or a rename across folders | Run the [docs audit](playbooks/docs-audit.md) once the batch lands, since a batch is where drift between pages starts. |
| A session went sideways: it wasted context, needed the person's corrections, or asserted a claim that had to be walked back | Run a [prompt retrospective](playbooks/prompt-retrospective.md) on its transcript, to find what in its prompt shaped that. |

## Periodic duties

The owner of each periodic duty is the workspace's maintainer: the person named as approver in the current plan. The current plan is the one whose `milestone` is listed under `building` in [workspace.json](../workspace.json); its `Approved by:` line names the person.

| Duty | When | How |
|---|---|---|
| The docs audit | Until M10 schedules the docs audit, a person runs it by hand once per milestone, before the milestone's record is signed off, and whenever this page's event list says so. | Run the [docs audit](playbooks/docs-audit.md) when its cadence or an event above calls for it. It reads the whole `docs/` tree for drift between pages, and reports a ranked cleanup list. |
| A prompt retrospective | Once per milestone, before the milestone's record is signed off, and whenever this page's event list says so. | Run a [prompt retrospective](playbooks/prompt-retrospective.md) when its cadence or an event above calls for it. Its first step says which transcript it reads. |
| Pages due for proof | Before the milestone's record is signed off. | List the pages it is to prove with `git grep -l "^prove-by: M<n>" -- docs`, and the merged sections with `git grep -n "prove-by M<n>\." -- docs`. Each one is proven by then, or its `prove-by` is moved later on a failed attempt on record, as [decision 0006](decisions/0006-what-proven-means.md) says. Otherwise the `proof` check fails once the record is signed off. |
| Pruning unused wrappers | Waits for slice B6 of M3, which adds the wrappers. | Nothing to prune until then. |
| The routing eval | Waits for M4, which builds the eval system for procedures and routing evals. | Nothing to run until then. |

## When a duty falls due

1. **Find the duty.** Input: the event that happened, or the milestone that is closing. Find its row in the tables above. Default: when no row fits, there is no duty; say so in your report. Output: the duty and the page it names.
2. **Hand a procedure to its page.** Input: the duty. When the row names the docs audit or a prompt retrospective, the maintainer runs it. Unless the maintainer or a person asked you to run it, do not run it. Name it in your report as due, with the event that set it off, and go to step 5. Otherwise, and for any other procedure a row names, follow that page; it ends in its own report, and this procedure ends with it. When the row names no procedure, go on. Output: the change the duty needs, or the due duty for the report.
3. **Size the change.** Input: the change. Put it through the [size gate](size-the-work.md#the-gate). A change to pages only follows [extend the workspace](extend-the-workspace.md)'s steps, which say how a small one is routed. A small change to code goes to [fix a bug](playbooks/fix-a-bug.md). A change to a part, hook, check or CI follows [changing the machinery](changing-the-machinery.md). Anything else that fails the gate climbs the ladder. Default: when you cannot tell, climb. Output: the route.
4. **Make the change on its route.** Input: the route. A change to a file the eval covers, such as `INDEX.md` or `AGENTS.md`, needs a new eval run, and the contract says to batch such edits. Default: when the rest of the change commits without it, such as a new topic row, do not make it. List it in your report for the maintainer to batch. Sometimes a check refuses the commit without it, such as the alias row a code rename needs. Then make it with the rest of the change on a branch, as the [trap on eval-covered commits](changing-the-machinery.md#traps) says. Ask the maintainer before starting the eval run, since it costs real agent time. Until the run is on record, the branch is not merged, and your report says so. Commit everything else as [commits](commits.md) says: staged by name, with the instruction review's trailer. Output: the commit, or the branch waiting for its eval run. If a check refuses the commit for any other reason, leave the change uncommitted, and name the finding and the files in your report.
5. **Report.** Input: what steps 1 to 4 produced. Report to the person in the session's reply, with each claim marked verified or inferred, as [the definition of done](definition-of-done.md#the-report) says. Name any duty left undone, and why. If you had to ask a person something this workspace should have answered, add it to the [question log](question-log.md) before you finish, and commit it as step 4 says. Stop here.

## Rules

| Rule | Enforced by |
|---|---|
| The session whose change sets off an event duty does that duty in the same piece of work, except the docs audit and the prompt retrospective, which the maintainer runs. | `prose` |
| A name in the code that changes gets its search alias changed too. | `aliases#a renamed class leaves a dangling alias` |
| A page found pointing at an agent's private memory, a session's scratch folder, or a file only one machine holds gets the fact written on it instead. | `prose` |
| The docs audit and the prompt retrospective run once per milestone, before its record is signed off, and on the events listed here. The maintainer owns them. | `prose` |
| Each page due for proof is proven before its milestone's record is signed off, or its `prove-by` is moved later on a failed attempt on record. | `proof#an unproven page whose prove-by milestone is signed off fails` |
| A change to a file the eval covers is listed for the maintainer to batch. When a check needs it now, its branch is not merged until the eval run is on record. | `prose` |
| A session that sets off the docs audit or a prompt retrospective, and is not running it, names it as due in its report. | `prose` |
| Mark every claim in the report verified or inferred. | `eval:fix-a-bug` |
| If you had to ask a person something this workspace should have answered, add it to the question log before you finish. | `prose` |
