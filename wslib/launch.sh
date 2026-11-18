#!/bin/sh
# Start the workspace's Python, once, for every hook, git hook, check and CI step.
#   wslib/launch.sh ws.py hook before-shell --tool claude-code    a script, relative to the workspace or absolute
#   wslib/launch.sh -m unittest discover -b tests                 a module
#   wslib/launch.sh hook before-shell --tool claude-code          ws.py's arguments: the wiring a running session holds
#
# It starts Python one time, in UTF-8 mode. wslib/start.py, run by that one start, checks the version and then runs
# the target in the same process. A Python older than 3.9 exits 97 there, and the next one on the path is tried.
# The Windows Store's stand-in for python3, under a WindowsApps folder, is tried only after every other.
#
# An agent tool blocks a call only on exit 2. With no Python that will do, this exits 2. A guard's wiring adds
# "|| exit 2", so a missing launcher or a Python that crashes refuses as well; a reminder's adds "|| exit 0".
# It uses only shell built-ins, so it works on an empty PATH.
here=${0%/*}
[ "$here" = "$0" ] && here=.
PYTHONUTF8=1
export PYTHONUTF8
for pass in first last; do
  for candidate in python3 python py; do
    found=$(command -v "$candidate" 2>/dev/null) || continue
    case "$found" in
      */WindowsApps/*) [ "$pass" = first ] && continue ;;
      *) [ "$pass" = last ] && continue ;;
    esac
    "$found" "$here/start.py" "$here/.." "$@"
    code=$?
    [ "$code" -ne 97 ] && exit "$code"
  done
done
echo "ws: no Python 3.9 or later on the path, so the workspace's hooks and checks cannot run; refused. Install Python 3.9 or later, or put it on the PATH." >&2
exit 2
