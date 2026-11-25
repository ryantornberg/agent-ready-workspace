---
kind: record
last-reviewed: 2026-11-25
covers: plugin/skills/fix-a-bug/SKILL.md
reviewed-at: f326a7a, with the uncommitted change of the slice Z builder
---

# Instruction review: plugin/skills/fix-a-bug/SKILL.md

This records the instruction review of slice Z's change to the fix-a-bug wrapper's body, for its author and agents the wrapper starts.

**In short:** 1 finding, not blocking: 1 contradiction.

## Scope

In scope: the whole wrapper, its description and body, with most attention to the uncommitted diff on f326a7a: the body now says to follow the playbook through its last step, the report, and to end the reply with that report, in the definition of done's shape, every claim marked, even when a fix record keeps a copy. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/playbooks/fix-a-bug.md`, `docs/playbooks/README.md` ("The page is canonical", "Three ways to follow a playbook" and its rules), `docs/definition-of-done.md`, `docs/procedure-endings.md` and `docs/templates/fix-record.md` with their uncommitted changes, `parts/wrappers.py`, and `evals/one-time.json`. Ran `python3 ws.py check`: exit 0, with no `wrappers` finding. Ran the check's `PAGE_PATH` pattern on the body: it names one page, `docs/playbooks/fix-a-bug.md`.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | The body, its new second sentence | Not blocking. `docs/playbooks/README.md` says a wrapper "stays thin: it says when to use it and points at the page, and never restates or changes its steps", and its rules table repeats it ("never restates or changes the page's steps", tagged `prose`). The new sentence restates fix a bug's step 6 ("End with the report from the definition of done. Keep it in the fix's record too") and adds detail the step does not hold: the shape under "The report", every claim marked, and "even when a fix record keeps a copy", which is procedure endings' new rule. The wrapper also says the page "wins over anything said here", so the two texts must be kept in step by hand. Verified: the body, the README's section and rule, and step 6. Not blocking: today the restated text agrees with the page, so an agent following it does nothing the page forbids (inferred). This is also a procedure endings rule restated instead of linked; it is counted once, here. | fixed: the body now only names the page's last step, "the report in the definition of done's shape", as the maintainer's answer to Q83 asks, and no longer restates step 6 or procedure endings' rule |

## Checked with no finding

- step: the body names one backticked page, as the `wrappers` check requires (verified: `parts/wrappers.py` fails a body naming more or fewer, and the pattern finds one here). It names the definition of done without a path, which a second backticked path would fail; the agent reaches it through fix a bug's step 6, which links it. "Follow it through its last step" could be read as going past a stop the page orders, such as a brief with something blocked, but each of those stops also ends with the report, and the body says the page wins (inferred). Verified, for the paths.
- trigger: the description did not change, and still says when to fire and names the nearby wrappers; the `wrappers` check passes. Verified.
- enforcement: the body's new must, end the reply with the marked report, is the rule of definition of done and procedure endings, enforced there by `eval:fix-a-bug`, whose report grader reads the agent's final message. Verified: `evals/grade.py`.
- placement: the body loads only when the wrapper fires; only the description is in every session's loaded layer, and it did not change. The restated procedure endings rule is counted under finding 1. Verified.
- eval-case: the behavior is fix a bug's step 6 and definition of done's, which the fix-a-bug case grades in the final message. The guided arm does not load the plugin; the one-time arm `routed-after-fix` in `evals/one-time.json` loads it to measure this change. The selection cases test firing, which this change does not touch. Verified.
