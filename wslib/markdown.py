"""Just enough markdown to check links: prose lines, link targets, heading anchors, front matter.

This is not a markdown parser. It reads the constructs people use to link
between pages, and the README lists the ones it does not read.
"""
import re
import urllib.parse

FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
ATX = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.*?)(?:[ \t]+#+)?[ \t]*$")
SETEXT = re.compile(r"^ {0,3}(=+|-+)[ \t]*$")
DEFINITION = re.compile(r"^ {0,3}\[([^\]]+)\]:[ \t]*(?:<([^>]*)>|(\S+))")
REFERENCE = re.compile(r"\]\[([^\]]+)\]")
HTML_TARGET = re.compile(r"""<(?:a|img|source)\b[^>]*?\b(?:href|src|srcset)\s*=\s*["']\s*([^"'\s,]*)""", re.I)
QUOTE = re.compile(r"^(?: {0,3}> ?)+")
HTML_ID = re.compile(r"""<[a-z][^>]*?\b(?:id|name)\s*=\s*["']([^"']+)["']""", re.I)
EXTERNAL = re.compile(r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*:|//)")


def split_front_matter(text):
    """Return (front matter lines, number of lines it occupies). ([], 0) when there is none."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return [], 0
    for index, line in enumerate(lines[1:], 1):
        if line.strip() in ("---", "..."):
            return lines[1:index], index + 1
    return [], 0


def prose_lines(text):
    """Yield (line number, line) outside front matter and fenced code blocks.

    A fence closes only on the same character, at least as long as the one that
    opened it, so a three-backtick line inside a four-backtick block stays code.
    """
    _, skip = split_front_matter(text)
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        if number <= skip:
            continue
        match = FENCE.match(line)
        if fence:
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence) \
                    and not line.strip().strip(fence[0]):
                fence = None
            continue
        if match:
            fence = match.group(1)
            continue
        yield number, line


def strip_code_spans(line):
    """Blank out inline code, so a link written as an example is not checked."""
    return re.sub(r"(`+)(?!`).*?(?<!`)\1(?!`)", lambda m: " " * len(m.group(0)), line)


def inline_targets(line):
    """Destinations of every [text](destination) and ![alt](destination) on a line.

    Scans from each "](" so brackets in the link text do not matter. Reads a
    <bracketed destination>, or a bare one with balanced parentheses, and
    ignores a trailing "title", 'title' or (title).
    """
    found, position = [], 0
    while True:
        position = line.find("](", position)
        if position < 0:
            return found
        index = position + 2
        while index < len(line) and line[index] in " \t":
            index += 1
        if index < len(line) and line[index] == "<":
            end = line.find(">", index)
            if end > 0:
                found.append(line[index + 1:end])
        else:
            depth, start = 0, index
            while index < len(line):
                char = line[index]
                if char in " \t" or (char == ")" and depth == 0):
                    break
                depth += (char == "(") - (char == ")")
                index += 1
            if index > start:
                found.append(line[start:index])
        position += 2


def links(text):
    """Yield (line number, target) for every link, image, reference definition and HTML href or src.

    Also yields (line number, None, label) for a [text][label] whose label is never defined.
    """
    defined, used = set(), []
    for number, raw in prose_lines(text):
        definition = DEFINITION.match(raw)
        if definition and definition.group(1).startswith("^"):
            continue  # a footnote, not a link
        if definition:
            defined.add(definition.group(1).strip().lower())
            yield number, definition.group(2) if definition.group(2) is not None else definition.group(3), None
            continue
        line = strip_code_spans(raw)
        for target in inline_targets(line):
            yield number, target, None
        for target in HTML_TARGET.findall(line):
            yield number, target, None
        used.extend((number, label.strip().lower()) for label in REFERENCE.findall(line) if not label.startswith("^"))
    for number, label in used:
        if label not in defined:
            yield number, None, label


def slug(heading):
    """The anchor GitHub gives a heading.

    Lower case; drop everything but letters, digits, spaces, hyphens and
    underscores; each space becomes a hyphen. Emphasis markers go, but an
    underscore inside a word stays, so "foo_bar" keeps its anchor.
    """
    heading = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", heading)   # a link keeps its text
    heading = re.sub(r"<[^>]+>", "", heading)                       # inline HTML goes
    heading = re.sub(r"[`*]", "", heading)
    heading = re.sub(r"(?<!\w)_+(.+?)_+(?!\w)", r"\1", heading)     # _emphasis_, not snake_case
    heading = re.sub(r"[^\w\- ]", "", heading.strip().lower())
    return heading.replace(" ", "-")


def anchors(text):
    """Every anchor a link into this page may use: headings, and HTML id or name attributes."""
    seen, found = {}, set()

    def add(title):
        base = slug(title)
        count = seen.get(base, 0)
        seen[base] = count + 1
        found.add(base if count == 0 else f"{base}-{count}")

    previous = ""
    for _, line in prose_lines(text):
        line = QUOTE.sub("", line)  # a heading inside a blockquote still gets an anchor
        atx = ATX.match(line)
        if atx:
            add(atx.group(2))
        elif SETEXT.match(line) and previous.strip() and not ATX.match(previous):
            add(previous.strip())
        found.update(name.lower() for name in HTML_ID.findall(line))
        previous = line
    return found


def resolve(page, target):
    """Turn a link target into (path, fragment) relative to the workspace root.

    Returns None for a link that leaves the web of local files (https:, mailto:, //host).
    path is None when the link climbs out of the workspace.
    """
    if EXTERNAL.match(target):
        return None
    target, _, fragment = target.partition("#")
    target = urllib.parse.unquote(target.partition("?")[0])
    fragment = urllib.parse.unquote(fragment).lower()
    if not target:
        return page, fragment
    parts = [] if target.startswith("/") else page.split("/")[:-1]
    for part in target.strip("/").split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if not parts:
                return None, fragment
            parts.pop()
        else:
            parts.append(part)
    return "/".join(parts), fragment
