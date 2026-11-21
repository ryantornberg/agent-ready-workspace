"""Print the setup steps a page marks, as one shell script: the blocks the cold-clone job runs.

A step is a fenced code block whose opening fence comes right after a line `<!-- setup -->` (blank lines
between are allowed). The script stops at the first command that fails. A page with no marked block, or a
marker with no block after it, is an error, so the job cannot pass by running nothing. The reading is
wslib/blocks.py's, which tutorials' runnable blocks share.

Usage: python3 tools/setup_steps.py README.md > setup.sh
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from wslib import blocks  # noqa: E402

# The pages whose marked steps set up a fresh clone. A change to one runs the cold-clone job.
SETUP_PAGES = ("README.md",)
MARKER = "setup"


def steps(text):
    """[(line number of the marker, [command lines])]. Raises ValueError for a marker with no block after it."""
    return blocks.marked(text, MARKER)


def script(page, text):
    return blocks.script(page, text, MARKER)


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
