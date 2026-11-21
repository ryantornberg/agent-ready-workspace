"""Print the setup steps a page marks, as one shell script: the blocks the cold-clone job runs.

A step is a fenced code block whose opening fence comes right after a line `<!-- setup -->` (blank lines
between are allowed). The script stops at the first command that fails. A page with no marked block, or a
marker with no block after it, is an error, so the job cannot pass by running nothing.

Usage: python3 tools/setup_steps.py README.md > setup.sh
"""
import re
import sys

# The pages whose marked steps set up a fresh clone. A change to one runs the cold-clone job.
SETUP_PAGES = ("README.md",)

MARKER = re.compile(r"^ {0,3}<!--\s*setup\s*-->\s*$")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def steps(text):
    """[(line number of the marker, [command lines])]. Raises ValueError for a marker with no block after it."""
    lines, found, index = text.splitlines(), [], 0
    while index < len(lines):
        if FENCE.match(lines[index]):   # a block no marker opens: an example, whose text is never a marker
            index = close(lines, index) + 1
            continue
        if not MARKER.match(lines[index]):
            index += 1
            continue
        marker = index + 1
        index += 1
        while index < len(lines) and not lines[index].strip():
            index += 1
        opening = FENCE.match(lines[index]) if index < len(lines) else None
        if not opening:
            raise ValueError(f"line {marker}: a setup marker must be followed by a fenced code block")
        end = close(lines, index)
        if end == len(lines):
            raise ValueError(f"line {marker}: the setup block's fence is never closed")
        found.append((marker, lines[index + 1:end]))
        index = end + 1
    return found


def close(lines, index):
    """The index of the line that closes the fence opened at lines[index], or len(lines) when none does."""
    fence = FENCE.match(lines[index]).group(1)
    for end in range(index + 1, len(lines)):
        closing = FENCE.match(lines[end])
        if closing and closing.group(1)[0] == fence[0] and len(closing.group(1)) >= len(fence) \
                and not lines[end].strip().strip(fence[0]):
            return end
    return len(lines)


def script(page, text):
    blocks = steps(text)
    if not blocks:
        raise ValueError("no block is marked <!-- setup -->")
    out = ["set -eu"]
    for marker, body in blocks:
        out.append(f"# {page}, the block marked at line {marker}")
        out.extend(body)
    return "\n".join(out) + "\n"


def main(argv):
    if len(argv) != 1:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 2
    try:
        with open(argv[0], encoding="utf-8") as handle:
            sys.stdout.write(script(argv[0], handle.read()))
    except (OSError, ValueError) as error:
        print(f"setup_steps: {argv[0]}: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
