"""Hook: refuse an edit to a shelved folder.

Some code looks current and is not: a service kept read-only for audits, a
branch of the product the team abandoned. A model cannot tell from the code.
The contract says so in prose, and this hook says so at the moment of the edit.

It guards the edit tools. A shell command that writes into the folder (sed -i,
rm, git mv) does not pass through it; the README's Limits say so.

Config: "paths": the shelved folders.
"""
import posixpath
import unicodedata

KIND = "hook"
PAGE = "AGENTS.md#facts-a-model-cannot-derive"   # the rule's page, which every finding names (criterion 34)
EVENT = "before-edit"


def _folded(path):
    """A path as a case-insensitive file system sees it. On macOS and Windows a differently-cased name,
    or one Unicode folds to the same letters (a long s for an s), is the same folder; Windows also
    drops a trailing dot or space from each name."""
    path = posixpath.normpath(path.replace("\\", "/"))
    parts = [part.rstrip(". ") or part for part in path.split("/")]
    return unicodedata.normalize("NFC", "/".join(parts)).casefold()


def decide(event, config):
    path = _folded(event.get("path") or ".")
    for folder in config.get("paths", ()):
        folder = folder.strip("/")
        shelved = _folded(folder)
        if path == shelved or path.startswith(shelved + "/"):
            return f"{folder} is shelved and read-only. If the change really belongs there, ask the person first."
    return None
