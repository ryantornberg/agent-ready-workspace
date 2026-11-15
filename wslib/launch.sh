#!/bin/sh
# Run ws.py with the first Python 3.9 or later on the path, and refuse when there is none.
# An agent tool blocks a call only on exit 2. Without this launcher, a missing python3 exits 127,
# which the tool reads as "the hook failed" and lets the call through: the hook would fail open.
# It uses only shell built-ins, so it works on an empty PATH. The wiring adds "|| exit 2", so even
# a missing launcher refuses.
#   wslib/launch.sh hook before-shell --tool claude-code
here=${0%/*}
for candidate in python3 python py; do
  if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c "import sys; sys.exit(sys.version_info < (3, 9))" 2>/dev/null; then
    exec "$candidate" "$here/../ws.py" "$@"
  fi
done
echo "ws: no Python 3.9 or later on the path, so the workspace's hooks cannot run; refused. Install Python 3, or put it on the PATH." >&2
exit 2
