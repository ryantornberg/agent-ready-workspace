---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/docs-audit/SKILL.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: plugin/skills/docs-audit/SKILL.md

This records the review of the docs-audit wrapper that slice B6 adds, for its author and its readers.

**In short:** 1 finding: 1 contradiction, not blocking. The audit's scope, "the whole docs tree" in the description and "the whole guidance set" on the page, leaves out the wrappers this change makes guidance pages, so no drift reading ever covers them.

## Scope

In scope: the whole wrapper, its front matter (`name`, `description`) and its body, which the staged change adds (`git diff --cached`). Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/README.md`, `docs/how-tos.md`, `docs/playbooks/docs-audit.md`, `docs/playbooks/instruction-review.md` ("When it runs") and its diff, `docs/maintain-the-workspace.md`, every other wrapper under `plugin/skills/`, the cases `plugin/evals/docs-audit-fires` and `plugin/evals/docs-audit-quiet`, `parts/wrappers.py`, and the `wrappers`, `loaded_size` and `review_trailer` entries in `workspace.json`.

Run, on macOS: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 17 of 17 cases` and `loaded_size: 4 of 4 cases`; `claude plugin validate plugin`, on Claude Code 2.1.330, passes with one warning, for a missing icon (verified). The 28 descriptions come to 6,542 bytes against the 9,000-byte ceiling; this one is 210 (verified). No selection case has run yet, as `evals/README.md` says (verified, reading), so every claim below about what a description fires on is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Front matter, `description`, "read the whole docs tree", against the page's step 1 and the `review_trailer` entry's guidance list | Not blocking. The page's step 1 sets the default scope as "the whole guidance set, which is every page under `docs/` plus `AGENTS.md`, `INDEX.md` and the README". The `review_trailer` entry's `guidance` list, which the instruction review calls the guidance pages, also holds `plugin/skills/`, `evals/README.md`, `CLAUDE.md`, the Copilot and opencode pointer files, and the kit's two seed pages (verified, reading `workspace.json`). So "the whole guidance set, which is ..." does not hold, and with this change the wrappers fall outside every drift reading: the instruction review reads each one at its own commit, and the audit never reads them. The wrappers are now where routing text repeats the catalog's rows and names its neighbors, so drift between them and the catalog is exactly the audit's kind of finding. The description's "the whole docs tree" carries the narrow scope into every session. The gap for `evals/README.md` and the pointer files is older than B6, which adds the wrappers to it (verified, reading the instruction review's diff). Widen step 1's default to the `review_trailer` guidance list, and say "the guidance pages" in the description. | deferred to M10: the description keeps the page's own scope. Whether the audit's step 1 reads every guidance page, the wrappers included, is a change to the audit page, which M10 proves. |

## Checked with no finding

- step: the body names one page, `docs/playbooks/docs-audit.md`, which exists, is a playbook with no `lane` key and has numbered steps (verified).
- trigger: the description's three occasions, once per milestone before sign-off, after a batch of page changes, and on request, match the page's "When it runs", the maintain page's event row for a batch of pages, and the catalog row (verified, reading). The fires case asks for the whole tree before sign-off; the quiet case asks for the review of two edited pages, which `workspace:instruction-review` owns, names this wrapper back for, and the page's own table sends there (verified).
- enforcement: the wrapper states no must or never. The rule that a wrapper stays thin is tagged `prose` in the catalog; the name, page, neighbor and case rules are enforced by the `wrappers` check, whose cases pass (verified).
- placement: the description says only when to fire and when not, and restates no step of the page (verified, reading).
- eval-case: both selection cases exist (verified). The page is marked unproven with `prove-by: M10`.

## Re-check

A fresh session re-read the wrapper on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6 (`git diff --cached`). It read the wrapper as staged, its canonical page, every other wrapper's description and the selection cases under `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; the 28 descriptions now come to 7,535 bytes against the 9,000-byte ceiling (verified). No selection case has run, so what a description fires on stays inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld: deferred to M10 | The finding is not blocking, and M10 is the audit page's `prove-by` (verified, front matter). The description still says "the whole docs tree", and step 1's scope still leaves out `plugin/skills/` and the other guidance paths the `review_trailer` entry lists (verified, reading). A deferral is one of the playbook's dispositions; the finding stays open until M10. |

What a fix broke: Nothing.

What the first reading missed: Nothing.
