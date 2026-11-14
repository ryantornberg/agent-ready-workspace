"""Check: every local link points at a file that exists, and every #fragment at a real anchor.

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

    for page in snapshot.paths(suffixes=(".md",), skip=config.get("skip", ())):
        text = snapshot.read(page)
        if text is None:
            found.append(finding(page, 1, "not valid UTF-8, so its links were not checked"))
            continue
        for line, target, undefined_label in markdown.links(text):
            if undefined_label is not None:
                found.append(finding(page, line, f"reference [{undefined_label}] is never defined"))
                continue
            resolved = markdown.resolve(page, target)
            if resolved is None:
                continue  # an external link
            path, fragment = resolved
            if path is None:
                found.append(finding(page, line, f"link leaves the workspace: {target}"))
            elif not snapshot.exists(path):
                found.append(finding(page, line, f"link to missing file: {target}"))
            elif fragment and path.lower().endswith(".md") and snapshot.is_file(path) and fragment not in anchors(path):
                found.append(finding(page, line, f"no heading for #{fragment} in {path}"))
    return found
