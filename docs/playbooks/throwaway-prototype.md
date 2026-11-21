---
kind: playbook
proof: unproven
prove-by: M4
last-reviewed: 2026-11-21
---

# Throwaway prototype

How an agent answers a question that has to be seen to be answered, with code it then deletes. For an agent or a person planning work.

**In short:** build the fastest thing that shows the answer: a harness that prints its state after every step, or several very different screens behind a switcher. Follow the five rules, keep only the answer, then delete the code.

## When to use it

Use it when reading the code or the docs cannot settle a question, and seeing it run can. Two kinds:

- **Logic**: how state changes through a sequence, such as what an order looks like after each step of the nightly job.
- **UI**: how a screen should look or behave, such as where the Export button goes.

If the question can be answered by reading, read instead. If you are building code to keep, this is not the page: see [test first](test-first.md).

## Steps

1. **Write the question.** Input: the open question. Write it in one sentence, and say what an answer looks like. Output: the question, and its branch: UI if it is about how a screen looks or feels, logic otherwise.
2. **Make a place for it, outside the repository.** Logic: an empty scratch folder. UI: a scratch folder holding a clone of this repository, since the variants need the front end to run: `git clone <path of this repository> <scratch folder>`, then `python3 ws.py pins` inside the clone to check out the code repositories. Output: the folder. Nothing in the repository or its working copies changes, so no other session is affected.
3. **Build it, by branch.**
   - **Logic:** the fastest runnable harness. A short script that calls the real code, or a stand-in for it, and prints the full state after each step. Output: one command that runs it.
   - **UI:** several very different variants, three by default, on one route of the front end, `src/orders-web`. Add a switcher, such as a query parameter or a key, that flips between them. Output: one command that starts it, and how to switch.
4. **Hold to the five rules** below while you build. If a rule starts to slip, the prototype is growing into real code: stop and go back to step 1.
5. **Get the answer.** Run it, or show it to the person who asked. Output: the answer, in one or two sentences, with what you ran.
6. **Keep the answer.** Write the question and the answer where the work needs it: the hand-off plan, a decision record, or your report. Keep no code.
7. **Delete it.** Delete the scratch folder, clone and all. Output: nothing of the prototype is left.

Stop when the answer is written down and the prototype is deleted. If no answer came after one round, report what the prototype showed and what question it raised instead.

## The five rules

| Rule | Means |
|---|---|
| Marked throwaway | The first line of each file says it is a throwaway prototype. |
| One command to run | Anyone can run it with one command, written down in step 3. |
| No persistence | It writes to no database, file or shared service. State lives in memory and dies with the run. |
| No polish | No error handling, no styling past what the question needs, no tests. |
| Surface state | It shows its state: the logic harness prints after every step; each UI variant shows the data behind it. |

## Rules

| Rule | Enforced by |
|---|---|
| A prototype follows the five rules. | `prose` |
| A prototype lives in a scratch folder outside the repository, and nothing of it is committed or pushed. | `prose` |
| Keep only the answer; delete the scratch folder. | `prose` |
