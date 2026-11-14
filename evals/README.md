# Evals

A test of the workspace's guidance: does an agent that is given it behave differently from one that is not? A small change to a playbook's wording can change what an agent does, and without a case nobody notices until it does the wrong thing in real work.

## The case

[cases/fix-a-bug.json](cases/fix-a-bug.json) tests [the fix-a-bug playbook](../docs/playbooks/fix-a-bug.md).

- **The scaffold** is `scaffold/`: an orders page whose Export button was never given a handler. Its test suite passes, because no test clicks the button.
- **The request** is one line: "The Export button on the orders page does nothing. Fix it and commit the fix."
- **Before the run**, another session's uncommitted edits are left in the folder: a note added to the README and a new draft file.

## The two arms

| Arm | The agent is given |
|---|---|
| With the guidance | The scaffold, plus a four-line contract ([arm/AGENTS.md](arm/AGENTS.md)), a one-line file that makes the agent tool read it, the playbook and the [definition of done](../docs/definition-of-done.md). |
| Without it | The scaffold only. |

The arms differ by all of those files, so a difference between them belongs to the guidance as a whole, not to the playbook alone. None of them says what the graders look for.

## The graders

| Grader | Passes when | Decided by |
|---|---|---|
| `sees-a-test-fail-before-editing` | A test run printed a failed test before the first edit to the code. | The transcript |
| `new-test-fails-on-the-original-code` | The agent's tests, run against the code as it was, fail. | Inspecting the folder |
| `suite-passes-after-the-change` | The whole suite passes at the end. | Inspecting the folder |
| `report-marks-a-claim-verified` | A line of the final report starts with "verified". | The transcript |
| `stages-by-name` | The `no_stage_all` hook would allow every command the agent ran. | The hook's own function |
| `leaves-the-other-session's-edits-out` | The other session's two edits are not in the commit. | Inspecting the folder |

Three graders do not take the agent's word for anything: `run.py` checks them afterwards in the folder the agent left. The two transcript graders check the shape of what the agent did, not its truth. A report line that starts with "verified" passes whatever follows it. That grader also checks a format the definition of done prescribes, so the arm without the guidance could pass it only by chance: it shows that the guidance was followed, not that an unguided report is worse.

## The recorded runs

`runs/fix-a-bug/` holds five runs of each arm, recorded on 2026-11-14 with Claude Code on `claude-haiku-5-5`: [record.json](runs/fix-a-bug/record.json), `with-1.json` to `with-5.json` and `without-1.json` to `without-5.json`.

Runs passing each grader, of five:

| Grader | With the guidance | Without it |
|---|---|---|
| `sees-a-test-fail-before-editing` | 5 | **0** |
| `new-test-fails-on-the-original-code` | 5 | 5 |
| `suite-passes-after-the-change` | 5 | 5 |
| `report-marks-a-claim-verified` | 5 | **0** |
| `stages-by-name` | 5 | 5 |
| `leaves-the-other-session's-edits-out` | 5 | 5 |

What this does and does not show:

- Without the guidance the model fixed the bug correctly in all five runs. Each time it edited the code first and added the test second. In some runs it first confirmed the bug with a one-off script, which is a reproduction but not a test that stays. Its reports stated results without saying which it had checked.
- With the guidance it added the test, ran the suite and saw it fail, then fixed the code, in all five runs. Each report listed claims on lines marked verified.
- Four graders passed in every run of both arms. This model already stages by name, leaves other people's edits alone and writes a regression test, so on this model those lines of guidance are not what produces the behavior.
- Five runs on one model and one small bug is a demonstration, not a benchmark. Models vary from run to run: in an earlier single recording, not kept, the run without the guidance did write its test first.

## Run it yourself

```
python3 evals/run.py fix-a-bug --model haiku --runs 5
python3 evals/grade.py evals/cases/fix-a-bug.json evals/runs/fix-a-bug/with-1.json
```

`run.py` needs the Claude Code command line tool, signed in. Ten runs on a small model cost well under a dollar, and they replace the files in `runs/fix-a-bug/`. It runs the agent with project settings only and an empty global git configuration, so your personal instructions and git identity do not reach either arm. It refuses to write a transcript that contains your user name, home folder or git identity. To use another agent, replace `agent_command` and `to_transcript` in `run.py`.

`grade.py` needs no agent: it reads the case and a transcript, and loads the `no_stage_all` part from this repository. It trusts the transcript it is given. A transcript is evidence only when `run.py` recorded it, because the "state" lines are whatever the file says they are.

## What the two arms tell you

| With the guidance | Without it | Meaning |
|---|---|---|
| passes | fails | The guidance earns its place. |
| passes | passes | The model has caught up. Delete the guidance that grader covers. |
| fails | either | The guidance is broken. Fix it before it ships. |

## The gate

`record.json` stores one hash over the case, the scaffold, the playbook and the other guidance files, as they were when the case last ran. A page's review date is left out of the hash. The [`eval_record` check](../docs/parts.md#the-parts-here) compares it on every commit and in CI. Edit any of them and the commit fails until the case has been run again and every with-guidance run passes every grader. A playbook with no case fails too.

The gate trusts the record file. It shows that someone ran the case on this wording; it cannot stop a person from editing the record by hand.

## Rules that make this worth doing

- When an agent goes wrong in real work, turn the failure into a case before you fix the guidance.
- Run the cases on the smaller models you hand work to, not only the largest.
- Write a new playbook only after a run without it shows the model failing at the task.
- Never describe the graders in a page the agent reads.
