#!/usr/bin/env python3
"""Find where a name is defined, as file:line, in one call.

    python3 tools/symbols.py ReconciliationWorker src     # exact name
    python3 tools/symbols.py --contains export src        # any name containing "export"

An agent that knows a name should not have to search for it. Python is read
with its own parser; C#, TypeScript and JavaScript by line patterns, which the
README's Limits section describes.

Prints "path:line  kind  name". Exit 0 when found, 1 when not, 2 when the folder does not exist.
The code is wslib/symbols.py; this file only starts it.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from wslib.symbols import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
