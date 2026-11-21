"""Check: every local link points at a file that exists, and every #fragment at a real anchor.

It reads the pages the workspace owns. A page inside a code repository under the
workspace, such as a submodule in src/, links by that repository's own layout and
is not read; a link into one still resolves. A symbolic link is not read as a page.
A page that is not UTF-8 is an error, not skipped. So is a line over 10,000
characters, which the reader does not parse.

Config:
  "skip": folders whose pages are not checked (finished work, fixtures).
  "backticked": pages, or folders of pages, whose backticked paths are checked too. Opt-in, since most
      backticked text is code, not a path. A backticked path is text with a slash and no spaces, read from
      the top of the workspace, whose first folder exists there: `src/orders-api` is checked; `origin/main`,
      `~/.config/x`, `<repo>/x` and `docs/*.md` are not.
  "exempt": [{"source": page, "target": link or backticked text, "reason": why}]. A link that cannot
      resolve on purpose, such as one into a folder git ignores. Each pair tolerates the finding for that
      exact target on that page. An exemption with no source, target or reason fails, and so does one
      that tolerates nothing, so a fixed link does not leave its exemption behind.
"""
import re

from wslib import markdown
from wslib.parts import finding

KIND = "check"

MANIFEST = "workspace.json"
CODE_SPAN = re.compile(r"(`+)(?!`)(.*?)(?<!`)\1(?!`)")
PATH = re.compile(r"^\.?[A-Za-z0-9_][A-Za-z0-9_.@+-]*(?:/[A-Za-z0-9_.@+-]+)*/?$")


def exemptions(config):
    """(the well-formed exemptions as {(source, target): reason}, findings for the rest)."""
    given = config.get("exempt", [])
    if not isinstance(given, list):
        return {}, [finding(MANIFEST, 1, 'links: "exempt" must be a list of {"source", "target", "reason"}')]
    good, found = {}, []
    for entry in given:
        if not isinstance(entry, dict):
            found.append(finding(MANIFEST, 1, f"links: an exemption must be an object, not {entry!r}"))
            continue
        missing = [key for key in ("source", "target", "reason")
                   if not isinstance(entry.get(key), str) or not entry[key].strip()]
        if missing:
            found.append(finding(MANIFEST, 1, f"links: an exemption has no {' and no '.join(missing)}: {entry!r}; "
                                              "each names the page, the exact target and why it cannot resolve"))
            continue
        good[(entry["source"], entry["target"])] = entry["reason"]
    return good, found


def backticked_paths(text):
    """Yield (line number, text) for each code span outside fenced blocks that reads as a relative path."""
    for number, line in markdown.prose_lines(text):
        for match in CODE_SPAN.finditer(line):
            span = match.group(2).strip()
            if "/" in span and "*" not in span and PATH.match(span):
                yield number, span


def opted_in(page, config):
    return any(page == place or page.startswith(place.rstrip("/") + "/") for place in config.get("backticked", ()))


def run(snapshot, config):
    found, anchor_cache = [], {}
    exempt, found_exempt = exemptions(config)
    used = set()

    def anchors(path):
        if path not in anchor_cache:
            anchor_cache[path] = markdown.anchors(snapshot.read(path) or "")
        return anchor_cache[path]

    def report(page, line, target, message):
        if (page, target) in exempt:
            used.add((page, target))
        else:
            found.append(finding(page, line, message))

    pages = set()
    for page in snapshot.pages(skip=config.get("skip", ())):
        pages.add(page)
        text = snapshot.read(page)
        if text is None:
            found.append(finding(page, 1, f"{snapshot.not_utf8(page)}, so its links were not checked; save it as UTF-8"))
            continue
        for line, target, problem in markdown.links(text):
            if problem is not None:
                found.append(finding(page, line, problem))
                continue
            resolved = markdown.resolve(page, target)
            if resolved is None:
                continue  # an external link
            path, fragment = resolved
            if path is None:
                report(page, line, target, f"link leaves the workspace: {target}")
            elif not snapshot.exists(path):
                report(page, line, target, f"link to missing file: {target}")
            elif fragment and path.lower().endswith(".md") and snapshot.is_file(path) and not snapshot.is_link(path) \
                    and fragment not in anchors(path):
                report(page, line, target, f"no heading for #{fragment} in {path}")
        if opted_in(page, config):
            for line, span in backticked_paths(text):
                first = span.split("/", 1)[0]
                if snapshot.exists(first) and not snapshot.exists(span.rstrip("/")):
                    report(page, line, span, f"backticked path does not exist: {span}")

    for (source, target), reason in sorted(exempt.items()):
        if (source, target) in used:
            continue
        where = "is not a page this check reads" if source not in pages else f"has no failing link or path {target!r}"
        found.append(finding(MANIFEST, 1, f"links: the exemption for {target!r} on {source} tolerates nothing: "
                                          f"{source} {where}; remove the exemption"))
    return found_exempt + found
