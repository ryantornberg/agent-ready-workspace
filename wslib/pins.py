"""The pinned-repository initializer: `ws.py pins` checks out each pinned code repository whose remote answers.

A workspace pins its code repositories as git submodules (decision 0001). A fresh clone holds the pins but
not the code. This probes every pinned repository's remote at once, each with prompts off and a time limit,
so a remote the person cannot reach costs one time limit in all and asks nothing. It then initializes and
checks out each one that answered, one at a time. A folder that already holds a checkout, or any files, is
never touched: no fetch, no reset, no switch. An unreachable remote is skipped with a note.
"""
import concurrent.futures
import os
import subprocess

from . import gitcall

PROBE_SECONDS = 10      # each remote's time limit; they run at once, so this is about the whole wait
CHECKOUT_SECONDS = 900  # one clone; prompts are off, so this only stops a stalled transfer


def resolve(url, base):
    """A .gitmodules URL as git would read it: one that starts with ./ or ../ is relative to base, the
    workspace's own remote. Anything else is returned unchanged."""
    if not url.startswith(("./", "../")) or not base:
        return url
    base = base.rstrip("/")
    while True:
        if url.startswith("./"):
            url = url[2:]
        elif url.startswith("../"):
            url = url[3:]
            cut = max(base.rfind("/"), base.rfind(":"))
            base = base[:cut] if cut > 0 else base
        else:
            break
    joiner = "" if base.endswith(":") else "/"
    return base + joiner + url


def pinned(root):
    """[(path, url or None)] for every pin: each gitlink in the index, with its URL from .gitmodules."""
    listing = gitcall.run(root, "ls-files", "-s") or ""
    paths = [line.split("\t", 1)[1] for line in listing.splitlines() if line.startswith("160000 ") and "\t" in line]
    urls = {}
    config = gitcall.run(root, "config", "-f", ".gitmodules", "--get-regexp", r"^submodule\..*\.(path|url)$") or ""
    entries = {}
    for line in config.splitlines():
        key, _, value = line.partition(" ")
        name, _, field = key[len("submodule."):].rpartition(".")
        entries.setdefault(name, {})[field] = value
    for entry in entries.values():
        if "path" in entry:
            urls[entry["path"].strip("/")] = entry.get("url")
    base = (gitcall.run(root, "config", "--get", "remote.origin.url") or "").strip() or str(root)
    return [(path, resolve(urls[path], base) if urls.get(path) else None) for path in sorted(paths)]


def state(root, path):
    """"checkout" when the folder holds a git checkout, "files" when it holds anything else, "empty" otherwise."""
    folder = os.path.join(str(root), path)
    if os.path.lexists(os.path.join(folder, ".git")):
        return "checkout"
    if os.path.isdir(folder) and os.listdir(folder):
        return "files"
    return "empty"


def probe(root, url, timeout=PROBE_SECONDS):
    """True when the remote answers within timeout seconds, with no prompt; False or None otherwise."""
    return gitcall.ok(root, "ls-remote", "-q", url, "HEAD", timeout=timeout)


def check_out(root, path, timeout=CHECKOUT_SECONDS):
    """Initialize and check out one pin. (True, "") or (False, why)."""
    try:
        done = subprocess.run(["git", "-C", str(root), "submodule", "update", "--init", "--", path],
                              capture_output=True, env=gitcall.environment(), timeout=timeout,
                              stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return False, f"the checkout ran past {timeout} seconds"
    except OSError as error:
        return False, str(error)
    if done.returncode != 0:
        lines = done.stderr.decode("utf-8", "replace").strip().splitlines()
        return False, lines[-1] if lines else f"git exited {done.returncode}"
    return True, ""


def initialize(root, timeout=PROBE_SECONDS, checkout_timeout=CHECKOUT_SECONDS):
    """Initialize every pin whose remote answers. [(path, outcome, note)], outcome one of
    "initialized", "untouched", "unreachable", "no-url" or "failed"."""
    results, to_probe = {}, []
    for path, url in pinned(root):
        current = state(root, path)
        if current == "checkout":
            results[path] = ("untouched", "already checked out; left as it is")
        elif current == "files":
            results[path] = ("untouched", "the folder holds files but no checkout; left as it is")
        elif url is None:
            results[path] = ("no-url", "no URL for it in .gitmodules; add one, then run this again")
        else:
            to_probe.append((path, url))
    if to_probe:
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(16, len(to_probe))) as pool:
            answers = dict(zip(to_probe, pool.map(lambda pin: probe(root, pin[1], timeout), to_probe)))
        for (path, url), answered in answers.items():
            if not answered:
                results[path] = ("unreachable", f"{url} did not answer within {timeout} seconds, with prompts off; "
                                                "check your access to it, then run this again")
                continue
            done, why = check_out(root, path, checkout_timeout)
            head = (gitcall.run(os.path.join(str(root), path), "rev-parse", "--short", "HEAD") or "").strip()
            results[path] = ("initialized", f"checked out at {head}") if done else ("failed", why)
    return [(path,) + results[path] for path in sorted(results)]
