"""Check: no file or file name holds a term from a private deny list.

A public workspace is often built by someone who also works on private code.
Names of employers, products, hosts, ticket patterns and personal addresses
must never reach it. The list of those terms is itself private, so it lives
outside every repository.

Where the list is: the file the WS_DENY_LIST environment variable names, or,
when that is unset, ~/.config/agent-ready-workspace/deny-list.txt. When
neither exists, the check says so as a warning and checks nothing. CI has no
list, so CI cannot run this check: it guards commits made on a machine that
has one. A list committed by mistake fails on its own plain entries.

A finding never repeats a term. When a file's name matches, its path is shown
as its folder plus a short hash of the name, so the output is safe to paste.

List format: one entry per line, matched without regard to case. Words in an
entry also match when joined by spaces, a line break, "-" or "_", or nothing.
A line starting "re:" is a regular expression, used as written. Blank lines
and lines starting "#" are ignored.

Every file in the snapshot is read, whatever its encoding. Text is normalised
(NFKC, zero-width characters removed) before matching, and a copy with NUL
bytes removed is also scanned, which catches UTF-16 with no byte-order mark.

Limits: compressed or encrypted files are not opened. A list holding only
"re:" entries does not match itself if committed. The snapshot skips
node_modules, .venv and __pycache__ folders.

Config, for cases only, and refused anywhere else: "terms": the list's lines;
"list": a path to read instead, "" meaning no list. The manifest is public:
it must never carry terms, and it cannot redirect or switch off the list.
"""
import codecs
import hashlib
import os
import posixpath
import re
import unicodedata

from wslib.parts import finding
from wslib.snapshot import Memory

KIND = "check"
VARIABLE = "WS_DENY_LIST"
DEFAULT = "~/.config/agent-ready-workspace/deny-list.txt"
CASE_ONLY = ("terms", "list")
ZERO_WIDTH = dict.fromkeys(map(ord, "​‌‍⁠﻿­"))


def entries(lines):
    """[(line number, compiled pattern)] from the list's lines. Raises ValueError naming a bad line."""
    found = []
    for number, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("re:"):
            source = line[3:]
        else:
            source = r"[\s_-]*".join(re.escape(word) for word in line.split())
        try:
            found.append((number, re.compile(source, re.IGNORECASE)))
        except re.error:
            raise ValueError(f"line {number} of the deny list is not a valid regular expression")
    return found


def normalise(text):
    return unicodedata.normalize("NFKC", text).translate(ZERO_WIDTH)


def as_texts(data):
    """Every reading of a file worth scanning: decoded by its byte-order mark, UTF-8 or Latin-1, and without NULs."""
    texts = []
    for mark, encoding in ((codecs.BOM_UTF32_LE, "utf-32"), (codecs.BOM_UTF32_BE, "utf-32"),
                           (codecs.BOM_UTF16_LE, "utf-16"), (codecs.BOM_UTF16_BE, "utf-16")):
        if data.startswith(mark):
            texts.append(data.decode(encoding, "replace"))
            break
    else:
        try:
            texts.append(data.decode("utf-8-sig"))
        except UnicodeDecodeError:
            texts.append(data.decode("latin-1"))
    if b"\0" in data:
        texts.append(data.replace(b"\0", b"").decode("latin-1"))
    return [normalise(text) for text in texts]


def shown(path):
    """The path as printed when its name matches: the folder and a short hash of the name."""
    folder, name = posixpath.split(path)
    digest = hashlib.sha256(name.encode("utf-8")).hexdigest()[:8]
    return f"{folder}/<name {digest}>" if folder else f"<name {digest}>"


def read_list(config, in_case):
    """The list's lines, or a finding that explains why there are none."""
    if not in_case and any(key in config for key in CASE_ONLY):
        return None, finding("workspace.json", 1, 'the deny_list entry sets "terms" or "list"; only its cases may')
    if "terms" in config:
        return config["terms"], None
    location = config["list"] if "list" in config else (os.environ.get(VARIABLE, "").strip() or DEFAULT)
    path = os.path.expanduser(location) if location else ""
    if not path or (not os.environ.get(VARIABLE, "").strip() and not os.path.exists(path) and "list" not in config):
        return None, finding("workspace.json", 1, f"no private deny list: {VARIABLE} is not set and none is at {DEFAULT}, "
                                                  "so nothing was checked", level="warning")
    if not path:
        return None, finding("workspace.json", 1, "no private deny list, so nothing was checked", level="warning")
    try:
        with open(path, encoding="utf-8-sig") as stream:
            return stream.read().splitlines(), None
    except (OSError, UnicodeDecodeError):
        return None, finding("workspace.json", 1, "the private deny list cannot be read")


def run(snapshot, config):
    lines, problem = read_list(config, isinstance(snapshot, Memory))
    if problem:
        return [problem]
    try:
        patterns = entries(lines)
    except ValueError as error:
        return [finding("workspace.json", 1, str(error))]
    if not patterns:
        return [finding("workspace.json", 1, "the private deny list holds no entries")]

    found = []
    for path in snapshot.paths():
        name_hits = [number for number, pattern in patterns if pattern.search(normalise(path))]
        where = shown(path) if name_hits else path
        for number in name_hits:
            found.append(finding(where, 1, f"the file name matches line {number} of the private deny list"))
        data = snapshot.read_bytes(path)
        if data is None:
            found.append(finding(where, 1, "cannot be read, so it was not checked against the private deny list"))
            continue
        texts = as_texts(data)
        for number, pattern in patterns:
            for text in texts:
                match = pattern.search(text)
                if match:
                    line = text.count("\n", 0, match.start()) + 1
                    found.append(finding(where, line, f"matches line {number} of the private deny list"))
                    break
    return found
