"""Check: every agent session gets its own browser.

Without isolation, the browser server keeps one profile folder per user on disk.
A second session that opens a browser while the first has one open fails with
"browser already in use". So the workspace runs the browser server from its own
committed config, pinned to an exact version, with --isolated, which gives each
server its own profile in memory. And the project settings turn the agent tool's
own browser plugin off, explicitly: a key left out lets user settings turn it
back on, and then two servers run.

It reads the committed files only. A machine-local settings file can still turn
the plugin back on; docs/browsers.md says where to look.

Config: "settings": the project settings file, "plugin": the plugin to turn off,
"package": the browser server's package, "configs": {tool: config file}. A ".json"
config holds "mcpServers"; a ".toml" config is read line by line, for Python 3.9,
which has no TOML parser: tables [mcp_servers.NAME] with an "args" array of strings.
"""
import json
import re

from wslib.parts import finding

KIND = "check"
PAGE = "docs/browsers.md"
EXACT = re.compile(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?")
TABLE = re.compile(r"^\s*\[\s*mcp_servers\.(?:\"([^\"]+)\"|'([^']+)'|([A-Za-z0-9_-]+))\s*\]\s*(?:#.*)?$")
STRING = re.compile(r"\"((?:[^\"\\]|\\.)*)\"|'([^']*)'")


def _json_servers(text):
    data = json.loads(text)
    servers = data.get("mcpServers") if isinstance(data, dict) else None
    if not isinstance(servers, dict):
        raise ValueError("no mcpServers")
    return {name: [a for a in (spec.get("args") or []) if isinstance(a, str)] + [spec.get("command") or ""]
            for name, spec in servers.items() if isinstance(spec, dict)}


def _uncomment(line):
    """The line up to a # that sits outside a quoted string, so a comment cannot supply --isolated."""
    quote, index = None, 0
    while index < len(line):
        char = line[index]
        if quote == '"' and char == "\\":
            index += 2
            continue
        if quote and char == quote:
            quote = None
        elif not quote and char in "\"'":
            quote = char
        elif not quote and char == "#":
            return line[:index]
        index += 1
    return line


def _toml_servers(text):
    """{server: its args} from [mcp_servers.NAME] tables, read line by line. An args array may span lines."""
    servers, current, collecting, gathered = {}, None, False, ""
    for line in map(_uncomment, text.splitlines()):
        if collecting:
            gathered += " " + line
            if "]" in line.split("#")[0]:
                servers[current] = [a or b for a, b in STRING.findall(gathered)]
                collecting = False
            continue
        table = TABLE.match(line)
        if table:
            current = next(name for name in table.groups() if name)
            servers.setdefault(current, [])
            continue
        if line.strip().startswith("["):
            current = None
            continue
        if current and re.match(r"^\s*(args|command)\s*=", line):
            values = [a or b for a, b in STRING.findall(line.split("=", 1)[1])]
            if line.split("=", 1)[0].strip() == "command":
                servers[current] = servers[current] + values
            elif "]" in line.split("=", 1)[1]:
                servers[current] = values + servers[current]
            else:
                collecting, gathered = True, line.split("=", 1)[1]
    return servers


def _settings(snapshot, path, plugin):
    if not snapshot.is_file(path):
        return [finding(path, 1, f"{path} is missing, so the browser plugin {plugin} is not turned off; see {PAGE}")]
    try:
        data = json.loads(snapshot.read(path) or "")
    except ValueError:
        return [finding(path, 1, f"{path} is not readable JSON; see {PAGE}")]
    plugins = data.get("enabledPlugins") if isinstance(data, dict) else None
    if not isinstance(plugins, dict) or plugins.get(plugin) is not False:
        return [finding(path, 1, f"{path} must set enabledPlugins.\"{plugin}\" to false: a key left out lets user "
                                 f"settings turn the plugin on, and then two browser servers run; see {PAGE}")]
    return []


def _config(snapshot, tool, path, package):
    if not snapshot.is_file(path):
        return [finding(path, 1, f"{path} is missing, so {tool} has no isolated browser server; see {PAGE}")]
    text = snapshot.read(path) or ""
    try:
        servers = _json_servers(text) if path.endswith(".json") else _toml_servers(text)
    except (ValueError, AttributeError):
        return [finding(path, 1, f"{path} is not readable JSON with mcpServers; see {PAGE}")]
    found, runs = [], False
    for name, args in sorted(servers.items()):
        pinned = [a for a in args if a == package or a.startswith(package + "@")]
        if not pinned:
            continue
        runs = True
        version = pinned[0][len(package) + 1:] if "@" in pinned[0][len(package):] else ""
        if not EXACT.fullmatch(version):
            shown = f'"{version}"' if version else "no version"
            found.append(finding(path, 1, f"{path}: the server {name} pins {package} to {shown}; pin an exact version, "
                                          f"such as {package}@1.2.3; see {PAGE}"))
        if "--isolated" not in args:
            found.append(finding(path, 1, f"{path}: the server {name} runs {package} without --isolated, so two "
                                          f"sessions share one browser profile; see {PAGE}"))
    if not runs:
        found.append(finding(path, 1, f"{path} runs no {package} server, so {tool} has no isolated browser; see {PAGE}"))
    return found


def run(snapshot, config):
    package, plugin = config.get("package", "@playwright/mcp"), config.get("plugin")
    configs = config.get("configs")
    if not isinstance(plugin, str) or not isinstance(configs, dict) or not configs:
        return [finding("workspace.json", 1, f"browser_isolation needs \"plugin\" and \"configs\"; see {PAGE}")]
    found = _settings(snapshot, config.get("settings", ".claude/settings.json"), plugin)
    for tool, path in sorted(configs.items()):
        found += _config(snapshot, tool, path, package)
    return found
