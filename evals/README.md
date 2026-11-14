# Evals

Test cases for the playbooks. A small change to a playbook's wording can change what an agent does, and nobody notices until it does the wrong thing in real work.

## A case

[cases/fix-a-bug.json](cases/fix-a-bug.json) holds one case: a request, a description of the scaffold repository the agent works in, and graders. Each grader checks one behavior in the run, such as "it ran a test before it edited the code".

## Running one

`grade.py` grades a recorded run. It does not start an agent, so it works with any tool.

1. Give the agent the case's request in the scaffold repository, **with** the playbook available.
2. Save what it did as a transcript: an ordered JSON list of `{"kind": "read|run|edit|report", "target": "..."}`.
3. Do the same again **without** the playbook.
4. Grade both:

```
python3 evals/grade.py evals/cases/fix-a-bug.json evals/transcripts/fix-a-bug.pass.json
python3 evals/grade.py evals/cases/fix-a-bug.json evals/transcripts/fix-a-bug.fail.json
```

The two transcripts here are written by hand to show the format. They are not recordings of a model.

## What the two runs tell you

| With the playbook | Without it | Meaning |
|---|---|---|
| passes | fails | The playbook earns its place. |
| passes | passes | The model has caught up. Delete the playbook. |
| fails | either | The playbook is broken. Fix it before it ships. |

## Rules that make this worth doing

- Change a playbook only with a passing run on record for the new wording.
- When an agent goes wrong in real work, turn the failure into a case before you fix the playbook.
- Run the cases on the smaller models you hand work to, not only the largest.
