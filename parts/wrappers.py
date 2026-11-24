"""Check: the wrappers route to procedures that can run now, and only to those.

A wrapper is a skill in the Agent Skills format, `<skills>/<name>/SKILL.md`: front matter with a `name` and a
`description` that says when to fire and when not, naming the wrappers next to it, and a body that points at
one canonical page, as a backticked path under docs/. Every description loads into every session, so a wrapper
that routes to a procedure that cannot run, or to a lane draft nobody has run on real work, costs every session
and sends agents to work they cannot finish. And a page struck or moved must not leave its wrapper behind.

A core procedure is a page under docs/ whose kind is playbook or how-to and that has no `lane` key; a lane page
counts too once it is marked proven, since a lane draft gets its wrapper in the milestone that proves it. Each
core procedure has exactly one wrapper, named after its page's file, unless "waiting" lists it: a core page whose
wrapper waits for the milestone that builds its machinery or providers, M4 or M8. A lane draft and a waiting page
have no wrapper.

Each wrapper has selection cases under "cases", in the format `claude plugin eval` reads: one folder per case
holding `prompt.md` and `graders/*.md`. At least one case must fire the wrapper (a `tool_used` grader on the
Skill tool with `min: 1`) and one must leave it quiet (`min: 0`, `max: 0`, `arm: both`), each with `input_match`
in the one form below, which names the plugin and the wrapper, so a case names exactly one wrapper and a skill of
the same name from another plugin does not count.

The plugin is declared for Claude Code: `<plugin>/.claude-plugin/plugin.json` names it, the marketplace file
lists it with the source `./<plugin>`, and the project settings enable `<plugin name>@<marketplace name>`.

Config: "skills" (folder), "cases" (folder), "plugin" (folder), "marketplace" (file), "settings" (file),
"waiting": [{"page", "for": "M4" or "M8", "why"}].
"""
import json
import re

from wslib import markdown
from wslib.parts import finding

KIND = "check"
PAGE = "docs/playbooks/README.md"
PROCEDURES = ("playbook", "how-to")
WAITS_FOR = ("M4", "M8")
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PAGE_PATH = re.compile(r"`(docs/[^`\s]+\.md)`")
MAX_DESCRIPTION = 1024           # the Agent Skills format's limit


def match_for(plugin, name):
    """The one `input_match` form a selection case uses: the Skill tool's JSON input naming this plugin's wrapper."""
    return '"skill"\\s*:\\s*"' + plugin + ':' + name + '"'


def fields(text):
    """{key: value} of the front matter's top-level `key: value` lines, quotes taken off."""
    out = {}
    for row in markdown.split_front_matter(text or "")[0]:
        match = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*?)\s*$", row)
        if match:
            value = match.group(2)
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                value = value[1:-1]
            out[match.group(1)] = value
    return out


def body(text):
    lines = (text or "").split("\n")
    return "\n".join(lines[markdown.split_front_matter(text or "")[1]:])


def _json(snapshot, path):
    try:
        return json.loads(snapshot.read(path) or "")
    except ValueError:
        return None


def _wiring(snapshot, config):
    """Findings on the plugin manifest, the marketplace file and the project settings; and the plugin's name."""
    found = []
    folder = config["plugin"].strip("/")
    manifest_path = f"{folder}/.claude-plugin/plugin.json"
    manifest = _json(snapshot, manifest_path) if snapshot.is_file(manifest_path) else None
    plugin = manifest.get("name") if isinstance(manifest, dict) else None
    if not isinstance(plugin, str) or not plugin:
        return [finding(manifest_path, 1, "the wrappers' plugin has no manifest naming it; write "
                                          f"{manifest_path} with a \"name\"")], None
    market_path = config["marketplace"]
    market = _json(snapshot, market_path) if snapshot.is_file(market_path) else None
    entries = market.get("plugins") if isinstance(market, dict) else None
    listed = [e for e in entries or [] if isinstance(e, dict) and e.get("name") == plugin]
    if not isinstance(market, dict) or not market.get("name") or not listed:
        found.append(finding(market_path, 1, f"no marketplace lists the plugin {plugin}; write {market_path} with a "
                                             f"\"name\" and a plugins entry for {plugin} with the source ./{folder}"))
        return found, plugin
    if listed[0].get("source") != f"./{folder}":
        found.append(finding(market_path, 1, f"the marketplace's entry for {plugin} has the source "
                                             f"{listed[0].get('source')!r}; set it to ./{folder}"))
    key = f"{plugin}@{market['name']}"
    settings = _json(snapshot, config["settings"]) if snapshot.is_file(config["settings"]) else None
    enabled = settings.get("enabledPlugins") if isinstance(settings, dict) else None
    if not isinstance(enabled, dict) or enabled.get(key) is not True:
        found.append(finding(config["settings"], 1, f"the project settings do not enable {key}, so Claude Code "
                                                    f"loads no wrapper; set \"enabledPlugins\": {{\"{key}\": true}}"))
    return found, plugin


def _draft(keys):
    """A lane draft: a lane page not yet marked proven."""
    return "lane" in keys and keys.get("proof") != "proven"


def _procedures(snapshot):
    """{path: front matter} of every playbook and how-to under docs/."""
    out = {}
    for path in snapshot.pages(skip=("archive",)):
        if path.startswith("docs/"):
            keys = fields(snapshot.read(path))
            if keys.get("kind") in PROCEDURES:
                out[path] = keys
    return out


def _cases(snapshot, folder, names, plugin):
    """({wrapper: {"fires", "quiet"}}, findings) from the selection cases under folder."""
    kinds, found = {}, []
    graders = [p for p in snapshot.paths(suffixes=(".md",), under=folder) if "/graders/" in p]
    for path in graders:
        keys = fields(snapshot.read(path))
        if keys.get("type") != "tool_used" or keys.get("tool") != "Skill":
            continue
        case = path.split("/graders/")[0]
        if not snapshot.is_file(f"{case}/prompt.md"):
            found.append(finding(path, 1, f"the selection case {case} has no prompt.md; write the request it tests "
                                          f"there"))
            continue
        given = keys.get("input_match", "")
        name = next((n for n in names if given == match_for(plugin, n)), None)
        if name is None:
            found.append(finding(path, 1, f"names no wrapper there is, or not in the one form "
                                          f"input_match: '{match_for(plugin, 'NAME')}'; point it at a wrapper, or "
                                          f"remove "
                                          f"the case"))
            continue
        if keys.get("min") == "1" and "max" not in keys:
            kinds.setdefault(name, set()).add("fires")
        elif keys.get("max") == "0" and keys.get("min") == "0" and keys.get("arm") == "both":
            kinds.setdefault(name, set()).add("quiet")
        else:
            found.append(finding(path, 1, f"is neither a case that fires {name} (min: 1, no max) nor one that "
                                          f"leaves it quiet (min: 0, max: 0, arm: both); set one of the two"))
    return kinds, found


def run(snapshot, config):
    missing = [key for key in ("skills", "cases", "plugin", "marketplace", "settings") if not config.get(key)]
    if missing:
        return [finding("workspace.json", 1, f"wrappers needs \"{missing[0]}\" in its manifest entry; see {PAGE}")]
    found, plugin = _wiring(snapshot, config)
    procedures = _procedures(snapshot)

    waiting = {}
    for entry in config.get("waiting", []):
        page = entry.get("page") if isinstance(entry, dict) else None
        if not page or entry.get("for") not in WAITS_FOR or not entry.get("why"):
            found.append(finding("workspace.json", 1, f"a waiting entry needs a \"page\", \"for\" (one of "
                                                      f"{', '.join(WAITS_FOR)}) and a \"why\": {entry!r}"))
        elif page not in procedures or _draft(procedures[page]):
            found.append(finding("workspace.json", 1, f"the waiting list names {page}, which is not a core "
                                                      f"procedure here; remove it from the list"))
        else:
            waiting[page] = entry["for"]

    skills = config["skills"].strip("/")
    wrapped, names = {}, {}
    for path in snapshot.paths(under=skills):
        if not path.endswith("/SKILL.md") or path.count("/") != skills.count("/") + 2:
            continue
        folder = path.split("/")[-2]
        text = snapshot.read(path) or ""
        keys = fields(text)
        if keys.get("name") != folder or not NAME.match(folder):
            found.append(finding(path, 1, f"its name is {keys.get('name')!r}; set it to its folder's name, {folder}, "
                                          f"in lowercase words joined by hyphens"))
        description = keys.get("description", "")
        if not description or len(description) > MAX_DESCRIPTION:
            found.append(finding(path, 1, f"its description has {len(description)} characters; write one of 1 to "
                                          f"{MAX_DESCRIPTION} that says when to fire and when not"))
        names[folder] = (path, description)
        pages = sorted(set(PAGE_PATH.findall(body(text))))
        if len(pages) != 1:
            found.append(finding(path, 1, f"its body names {len(pages)} pages; name exactly one, the procedure it "
                                          f"routes to, as a backticked path under docs/"))
            continue
        page = pages[0]
        if not snapshot.is_file(page):
            found.append(finding(path, 1, f"routes to {page}, which does not exist; point it at the page, or remove "
                                          f"the wrapper with its cases"))
        elif page not in procedures:
            found.append(finding(path, 1, f"routes to {page}, which is not a playbook or how-to; a wrapper starts a "
                                          f"procedure"))
        elif _draft(procedures[page]):
            found.append(finding(path, 1, f"routes to the lane draft {page}; a lane draft gets no wrapper until its "
                                          f"prove-by milestone proves it, so remove this one"))
        elif page.rsplit("/", 1)[-1][:-len(".md")] != folder:
            found.append(finding(path, 1, f"routes to {page} but is named {folder}; name a wrapper after its page's "
                                          f"file, without .md"))
        elif page in waiting:
            found.append(finding(path, 1, f"routes to {page}, which waits for {waiting[page]}; remove the wrapper, or "
                                          f"take the page off the waiting list once it can run"))
        else:
            wrapped[page] = path

    for page, keys in sorted(procedures.items()):
        if not _draft(keys) and page not in waiting and page not in wrapped:
            found.append(finding(page, 1, f"is a core procedure with no wrapper; add one under {skills}/ with its "
                                          f"selection cases, or list the page under waiting with the milestone it "
                                          f"waits for"))

    for name, (path, description) in sorted(names.items()):
        if plugin is None:
            break
        named = set(re.findall(rf"\b{re.escape(plugin)}:([a-z0-9]+(?:-[a-z0-9]+)*)", description))
        for other in sorted(named - set(names)):
            found.append(finding(path, 1, f"its description names {plugin}:{other}, which is no wrapper; name one "
                                          f"that exists"))
        if not named - {name}:
            found.append(finding(path, 1, f"its description names no wrapper next to it; say which one, as "
                                          f"{plugin}:<name>, owns the nearby request it must not take"))

    if plugin is None:
        return found
    kinds, case_findings = _cases(snapshot, config["cases"].strip("/"), set(names), plugin)
    found += case_findings
    for name, (path, _) in sorted(names.items()):
        for kind, what in (("fires", "fire it"), ("quiet", "leave it quiet")):
            if kind not in kinds.get(name, set()):
                found.append(finding(path, 1, f"has no selection case that should {what}; add one under "
                                              f"{config['cases'].strip('/')}/"))
    return found
