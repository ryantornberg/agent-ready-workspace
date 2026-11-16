"""Check: every local link points at a file that exists, and every #fragment at a real anchor.

It reads the pages the workspace owns. A page inside a code repository under the
workspace, such as a submodule in src/, links by that repository's own layout and
is not read; a link into one still resolves. A symbolic link is not read as a page.
A page that is not UTF-8 is an error, not skipped. So is a line over 10,000
characters, which the reader does not parse.

Config: "skip": folders whose pages are not checked (finished work, fixtures).
"""
from wslib import markdown
from wslib.parts import finding

KIND = "check"


def run(snapshot, config):
    found, anchor_cache = [], {}

    def anchors(path):
        if path not in anchor_cache:
            anchor_cache[path] = markdown.anchors(snapshot.read(path) or "")
        return anchor_cache[path]

    for page in snapshot.pages(skip=config.get("skip", ())):
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
                found.append(finding(page, line, f"link leaves the workspace: {target}"))
            elif not snapshot.exists(path):
                found.append(finding(page, line, f"link to missing file: {target}"))
            elif fragment and path.lower().endswith(".md") and snapshot.is_file(path) and not snapshot.is_link(path) \
                    and fragment not in anchors(path):
                found.append(finding(page, line, f"no heading for #{fragment} in {path}"))
    return found
