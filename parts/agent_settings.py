"""Check: both agent tools' settings deny reading the secrets files, and allow web reads of the documentation domains.

Claude Code reads its permissions from .claude/settings.json: a "deny" entry Read(<pattern>) for each secrets
pattern, and an "allow" entry WebFetch(domain:<domain>) for each documentation domain. Codex CLI reads
.codex/config.toml: a permissions profile whose filesystem table gives "none" to each secrets pattern under
":workspace_roots", and `[tools.web_search]` whose `allowed_domains` names each domain. With "codex_default"
set, the config's `default_permissions` must name that profile, so the denies apply without the person
choosing it. Codex's profile reaches every process the agent starts, so it denies only the patterns inside
the workspace: a home folder entry such as ~/.ssh would also stop git from pushing.

It reads the committed files only; a machine-local settings file can loosen either. Python 3.9 has no TOML
parser, so the Codex config is read line by line: tables, and `key = "value"` or `key = [strings]` lines.

Config: "claude" and "codex": the files; "secrets": the patterns inside the workspace, such as "**/.env";
"home": patterns under the home folder, for Claude Code only, such as "~/.ssh/**"; "domains"; "profile": the
Codex profile's name; "codex_default": whether it must be the default.
"""
import json
import re

from wslib.parts import finding

KIND = "check"
PAGE = "docs/agent-settings.md"
TABLE = re.compile(r"^\s*\[\s*([^\]]+?)\s*\]\s*(?:#.*)?$")
PAIR = re.compile(r"^\s*(\"(?:[^\"\\]|\\.)*\"|'[^']*'|[A-Za-z0-9_.-]+)\s*=\s*(.+?)\s*(?:#.*)?$")
STRING = re.compile(r"\"((?:[^\"\\]|\\.)*)\"|'([^']*)'")


def _unquote(text):
    match = STRING.fullmatch(text.strip())
    return (match.group(1) if match.group(1) is not None else match.group(2)) if match else text.strip()


def _table_name(text):
    """A TOML table header as a list of keys: permissions.ar.filesystem.":workspace_roots"."""
    keys, rest = [], text.strip()
    while rest:
        match = STRING.match(rest) or re.match(r"[A-Za-z0-9_-]+", rest)
        if not match:
            return None
        keys.append(_unquote(match.group(0)))
        rest = rest[match.end():].lstrip()
        if rest.startswith("."):
            rest = rest[1:].lstrip()
        elif rest:
            return None
    return keys


def toml_tables(text):
    """{tuple of table keys: {key: value text}} for the top level and each [table]."""
    tables, current = {(): {}}, ()
    for line in text.splitlines():
        header = TABLE.match(line)
        if header and not line.strip().startswith("[["):
            keys = _table_name(header.group(1))
            current = tuple(keys) if keys is not None else ("?",)
            tables.setdefault(current, {})
            continue
        pair = PAIR.match(line)
        if pair:
            tables.setdefault(current, {})[_unquote(pair.group(1))] = pair.group(2)
    return tables


def _strings(value):
    return [a if a is not None else b for a, b in STRING.findall(value or "")]


def _claude(snapshot, path, secrets, home, domains):
    text = snapshot.read(path)
    try:
        data = json.loads(text or "")
        permissions = data.get("permissions") or {}
        deny, allow = set(permissions.get("deny") or []), set(permissions.get("allow") or [])
    except (ValueError, AttributeError, TypeError):
        return [finding(path, 1, f"{path} is not readable JSON with a permissions object. Repair it, then run: "
                                 f"python3 ws.py check. See {PAGE}")]
    found = []
    for pattern in secrets:
        if f"Read(./{pattern})" not in deny and f"Read({pattern})" not in deny:
            found.append(finding(path, 1, f"Claude Code may read {pattern}: add \"Read(./{pattern})\" to "
                                          f"permissions.deny. See {PAGE}"))
    for pattern in home:
        if f"Read({pattern})" not in deny:
            found.append(finding(path, 1, f"Claude Code may read {pattern}: add \"Read({pattern})\" to "
                                          f"permissions.deny. See {PAGE}"))
    for domain in domains:
        if f"WebFetch(domain:{domain})" not in allow:
            found.append(finding(path, 1, f"Claude Code's web fetch is not allowed {domain}: add "
                                          f"\"WebFetch(domain:{domain})\" to permissions.allow. See {PAGE}"))
    return found


def _codex(snapshot, path, secrets, domains, profile, default):
    text = snapshot.read(path)
    if text is None:
        return [finding(path, 1, f"{path} is missing, so Codex CLI denies no secrets file. Add the profile "
                                 f"{profile!r}. See {PAGE}")]
    tables = toml_tables(text)
    found = []
    if default and _unquote(tables[()].get("default_permissions", "")) != profile:
        found.append(finding(path, 1, f"default_permissions does not name the profile {profile!r}, so Codex CLI "
                                      f"runs without its denies: add default_permissions = \"{profile}\". See {PAGE}"))
    roots = tables.get(("permissions", profile, "filesystem", ":workspace_roots"), {})
    if ("permissions", profile) not in tables:
        found.append(finding(path, 1, f"Codex CLI has no permissions profile {profile!r}: add "
                                      f"[permissions.{profile}] with extends = \":workspace\". See {PAGE}"))
    for pattern in secrets:
        if _unquote(roots.get(pattern, "")) != "none":
            found.append(finding(path, 1, f"Codex CLI may read {pattern}: add \"{pattern}\" = \"none\" under "
                                          f"[permissions.{profile}.filesystem.\":workspace_roots\"]. See {PAGE}"))
    allowed = set(_strings(tables.get(("tools", "web_search"), {}).get("allowed_domains")))
    for domain in domains:
        if domain not in allowed:
            found.append(finding(path, 1, f"Codex CLI's web search is not allowed {domain}: add it to "
                                          f"allowed_domains under [tools.web_search]. See {PAGE}"))
    return found


def run(snapshot, config):
    secrets, domains = config.get("secrets", []), config.get("domains", [])
    found = _claude(snapshot, config.get("claude", ".claude/settings.json"), secrets, config.get("home", []), domains)
    found += _codex(snapshot, config.get("codex", ".codex/config.toml"), secrets, domains,
                    config.get("profile", "agent-ready"), config.get("codex_default", True))
    if not secrets:
        found.append(finding("workspace.json", 1, f"agent_settings lists no secrets patterns, so it checks nothing. "
                                                  f"Add them to its \"secrets\" setting. See {PAGE}"))
    return found
