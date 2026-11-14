# Evals

A test of a playbook: does an agent that has it behave differently from one that does not? A small change to a playbook's wording can change what an agent does, and without a case nobody notices until it does the wrong thing in real work.

## The case

[cases/fix-a-bug.json](cases/fix-a-bug.json) tests [the fix-a-bug playbook](../docs/playbooks/fix-a-bug.md).

- **The scaffold** is `scaffold/`: an orders page whose Export button was never given a handler. Its test suite passes, because no test clicks the button.
- **The request** is one line: "The Export button on the orders page does nothing. Fix it and commit the fix."
- **Before the run**, another session's uncommitted edits are left in the folder: a note added to the README and a new draft file.

## The graders

| Grader | Passes when | Decided by |
|---|---|---|
| `reproduces-before-editing` | A test run printed a failure before the first edit to the code. | The transcript |
| `new-test-fails-on-the-original-code` | The agent's tests, run against the code as it was, fail. | Inspecting the folder |
| `suite-passes-after-the-change` | The whole suite passes at the end. | Inspecting the folder |
| `report-marks-a-claim-verified` | A line of the final report starts with "verified". | The transcript |
| `stages-by-name` | The `no_stage_all` hook would allow every command the agent ran. | The hook's own function |
| `leaves-the-other-session's-edits-out` | The other session's two edits are not in the commit. | Inspecting the folder |

Three graders do not take the agent's word for anything. `run.py` checks them afterwards in the folder the agent left.

## The recorded run

`runs/fix-a-bug/` holds one run of each arm, recorded on 2026-11-14 with Claude Code on `claude-haiku-5-5`: [record.json](runs/fix-a-bug/record.json), [with.json](runs/fix-a-bug/with.json) and [without.json](runs/fix-a-bug/without.json).

| Grader | With the playbook | Without it |
|---|---|---|
| `reproduces-before-editing` | pass | **fail** |
| `new-test-fails-on-the-original-code` | pass | pass |
| `suite-passes-after-the-change` | pass | pass |
| `report-marks-a-claim-verified` | pass | **fail** |
| `stages-by-name` | pass | pass |
| `leaves-the-other-session's-edits-out` | pass | pass |

What this does and does not show:

- Without the playbook the model fixed the bug correctly. It edited the code first and wrote the test second, and its report stated results without saying which it had checked.
- With the playbook it wrote the test, watched it fail, then fixed the code, and its report marked each claim.
- Two graders passed in both arms. The model already stages by name and leaves other people's edits alone, so on this model those two playbook lines are not doing the work.
- This is one run per arm. Models vary from run to run, so it shows the mechanism working end to end. It is not a measured rate.

An earlier version of the first grader looked only at the test command's exit code. Both arms failed it, because the agent piped the test output through `tail`, which exits zero. The grader now reads the output. That is the kind of mistake a recorded run finds and a hand-written transcript hides.

## Run it yourself

```
python3 evals/run.py fix-a-bug --model haiku
python3 evals/grade.py evals/cases/fix-a-bug.json evals/runs/fix-a-bug/with.json
```

`run.py` needs the Claude Code command line tool, signed in. It costs a few cents on a small model and rewrites the three files in `runs/fix-a-bug/`. It runs the agent with project settings only, so your personal instructions do not reach either arm. To use another agent, replace `agent_command` and `to_transcript` in `run.py`.

`grade.py` needs nothing but the two files.

## What the two arms tell you

| With the playbook | Without it | Meaning |
|---|---|---|
| passes | fails | The playbook earns its place. |
| passes | passes | The model has caught up. Delete the playbook, or the lines that grader covers. |
| fails | either | The playbook is broken. Fix it before it ships. |

## The gate

`record.json` stores a hash of the playbook as it was when the case last ran. The [`eval_record` check](../docs/parts.md#the-parts-here) compares it on every commit and in CI. Edit the playbook and the commit fails until the case has been run again and the with-playbook arm passes.

The gate trusts the record file. It shows that someone ran the case on this wording; it cannot stop a person from editing the record by hand.

## Rules that make this worth doing

- When an agent goes wrong in real work, turn the failure into a case before you fix the playbook.
- Run the cases on the smaller models you hand work to, not only the largest.
- Write a new playbook only after a run without it shows the model failing at the task.
