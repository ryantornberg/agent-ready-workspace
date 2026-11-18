"""Check: each agent tool's pointer file still sends that tool to the contract and the rule pages.

Claude Code reads CLAUDE.md, and Codex CLI reads AGENTS.md itself. GitHub Copilot and opencode each read a
file of their own. If that file stops naming AGENTS.md and the rule pages, a session in that tool works
without the workspace's rules and nobody notices. So each file named in "files" must exist and contain
every text in "names".

Config: "files" (the pointer files), "names" (default ["AGENTS.md", "docs/rules"]).
"""
from wslib.parts import finding

KIND = "check"
PAGE = "docs/layout.md"


def run(snapshot, config):
    names = config.get("names", ["AGENTS.md", "docs/rules"])
    files = config.get("files", [])
    if not files:
        return [finding("workspace.json", 1, "pointers names no pointer file to check; list each agent tool's file")]
    found = []
    for path in files:
        if not snapshot.is_file(path):
            found.append(finding(path, 1, f"the pointer file is missing; that tool would start without {names[0]}"))
            continue
        text = snapshot.read(path) or ""
        for name in names:
            if name not in text:
                found.append(finding(path, 1, f"no longer names {name}; a session in that tool would miss it. Name it "
                                              f"again; see {PAGE}"))
    return found
