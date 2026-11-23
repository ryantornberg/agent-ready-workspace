---
kind: how-to
lane: devops
proof: unproven
prove-by: M11
last-reviewed: 2026-11-23
---

# Environment self-check

A prompt a person pastes into their agent to check that the product's local container environment runs on their machine.

**In short:** paste the prompt below, naming your instance's environment page. The agent checks tools, reserved ports and certificates, brings one environment slot up, signs in, takes the slot down, and notes gaps in the page for the other operating system. It reports first, then offers fixes one at a time.

This is a lane draft: devops lane. It has not been run on real work yet; M11 runs it, as [decision 0006](decisions/0006-what-proven-means.md) says.

[Machine self-check](machine-self-check.md) checks the workspace's own hooks, checks and tools. This page checks the product's local environment. When both are due, run the machine self-check first: a broken hook explains failures here.

## The environment page

This repository has no container environment. Every command comes from the instance's own environment page: the page that says how to bring the product up locally. It names, at least:

- the tools, their versions, and the command that prints each version;
- the reserved ports, and the command that shows what listens on a port, for each operating system;
- the certificates to trust, and the command that checks one is trusted;
- how to bring up one slot and take it down, a slot being one copy of the environment on the machine;
- the slot's address, and a local test account to sign in with.

Below, `<...>` marks a value the environment page gives. With no environment page, the agent stops at step 1 and reports that. When the page lacks a command a step needs, that step is skipped, and the missing command is a gap in the environment page.

## The prompt

Paste this into an agent session at the top of the workspace, with the page's path filled in:

```
Run the environment self-check in docs/environment-self-check.md, using the environment page <path>. Follow its steps in order, in this session; hand nothing to a helper. Change nothing until you have given me the report, except the one slot step 5 brings up and takes down, and a question-log row for a question you had to ask me. Then offer each fix one at a time, and make one only when I say yes.
```

## Steps

The agent runs every step in its own session. When a step fails, it notes the failure and goes on. A step that needs something an earlier step found missing is marked skipped, with the reason.

1. **Read the environment page.** Input: the path in the prompt. Default: with no path, look for the page in [INDEX.md's topics](../INDEX.md#topics). Output: the values the list above names. If no page is found, stop: give the report with every step skipped, and "no environment page" as the reason.
2. **Tools.** Input: the page's tool list. Run each tool's version command from the page, such as `<version command>`. Pass: each tool is present, at the version the page asks for. Output: each version, or "missing".
3. **Reserved ports.** Input: the page's port list. Check that nothing on the machine already listens on each port, with the command the page gives for this operating system. Pass: each port is free. Output: each port, and what holds it if anything does.
4. **Certificates.** Input: the page's certificate list. Check that the machine trusts each one, with the page's command. Pass: each is trusted. Output: each certificate, trusted or not.
5. **One slot, up and down.** Input: steps 2 to 4 passed. Bring up one slot with `<bring-up command>`, on the person's machine only. Open the slot's address in a browser, as [browsers](browsers.md) says, and sign in with the page's local test account. Then take the slot down with `<take-down command>`, even when the sign-in failed. Pass: the slot came up, the sign-in reached the signed-in screen, and the slot came down. Default: when the page names no local test account, ask the person to sign in themselves; never use a real person's credentials. Output: each of the three results.
6. **Gaps for the other operating system.** Input: the page, and this machine's operating system. Read the page for steps written for one system only, such as a shell command with no equivalent given. Output: each gap, naming the step and the system it lacks.

Stop running checks when step 6 is done, and give the report.

## The report and the fixes

Give the report in the session's reply, each claim marked verified or inferred, as [the definition of done](definition-of-done.md#the-report) says.

```
Environment self-check: <n> pass, <n> fail, <n> skipped

| Step | Result | Evidence |
|---|---|---|
| 3 Reserved ports | fail | port <n> held by <process> |

Machine fixes: <one line each, or none>
Gaps in the environment page: <one line each, or none>
Skipped: <step, and why>
Slot left running: <none, or the slot and why>
```

Then offer the fixes, one at a time, machine fixes first.

- **A machine fix**, such as installing a tool, freeing a port or trusting a certificate, is made only on the person's yes. After each fix, run its step again and say the new result.
- **A gap in the environment page** is reported, not fixed in this run. If the person says yes to fixing it, the fix starts at the [size gate](size-the-work.md#the-gate). A page in a code repository changes there, on a branch of its own.
- **With no answer**, make no fix.

Stop when every fix offered is made or declined. Then end as [procedure endings](procedure-endings.md) says.

## Rules

| Rule | Enforced by |
|---|---|
| Take no command from anywhere but the instance's environment page; with no page, stop and report. | `prose` |
| Change nothing before the report, apart from the one slot brought up and taken down and a question-log row. | `prose` |
| Run every step in this session; hand nothing to a helper. | `prose` |
| Bring up a slot on the person's machine only, never in a shared environment. | `prose` |
| Take the slot down, even when a check in it failed. | `prose` |
| Never sign in with a real person's credentials. | `prose` |
| Offer fixes one at a time, and make one only on the person's yes. | `prose` |
| A gap in the environment page is reported, not fixed without the person's yes; its fix starts at the size gate. | `prose` |
| Mark every claim in the report verified or inferred. | `eval:fix-a-bug` |
