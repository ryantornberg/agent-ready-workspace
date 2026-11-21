"""Hook: refuse a delegated task that names no tier, or that runs off its tier's binding.

The orchestration rules (docs/orchestration.md) put every task in a tier:
driver, worker or mechanical. The manifest's "tiers" binds each one to a
model and an effort level. A task handed to a helper session names its tier
on the first line of its prompt, such as "Tier: worker", so that the person
reading the work, and this hook, can tell what it should run at.

Where the agent tool lets a task set its model or effort, the task must set
the binding's value for its tier. Leaving one unset is refused too: the helper
would then inherit the caller's model and effort, so a driver session would run
mechanical work at the driver's cost. A tool that exposes neither setting needs
only the tier line.

Config: "tiers", which the runner fills from the manifest. A case gives its own.
"""
import re

KIND = "hook"
PAGE = "docs/orchestration.md"   # the rule's page, which every finding names (criterion 34)
EVENT = "before-handoff"

TIERS = ("driver", "worker", "mechanical")
TIER_LINE = re.compile(r"^\s*tier\s*:\s*([A-Za-z]+)\b", re.IGNORECASE)
HOW = 'Start the prompt with "Tier: driver", "Tier: worker" or "Tier: mechanical"; see docs/orchestration.md.'


def decide(event, config):
    prompt = event.get("prompt")
    if not isinstance(prompt, str):
        return "the task has no prompt to read its tier from."
    first = next((line for line in prompt.splitlines() if line.strip()), "")
    match = TIER_LINE.match(first)
    if not match:
        return f"the task names no tier on its first line. {HOW}"
    tier = match.group(1).lower()
    if tier not in TIERS:
        return f'"{match.group(1)}" is not a tier. {HOW}'
    binding = (config.get("tiers") or {}).get(tier)
    if not isinstance(binding, dict):
        return f'the manifest\'s "tiers" binds nothing to the {tier} tier, so the task cannot be checked. Set a model and effort for it in workspace.json.'
    for setting in ("model", "effort"):
        if setting not in event:
            continue   # this agent tool does not let a task set it
        want = binding.get(setting)
        if not isinstance(want, str) or not want.strip():
            return f'the manifest\'s "tiers" gives the {tier} tier no {setting}, so the task cannot be checked. Set it in workspace.json.'
        got = event[setting]
        if got is None:
            return (f"the {tier} tier runs with {setting} {want}. Set it on the task: left unset, "
                    f"the helper inherits this session's {setting}.")
        if got.strip().lower() != want.strip().lower():
            return f"the {tier} tier runs with {setting} {want}, not {got}. Set it from the manifest's \"tiers\"."
    return None
