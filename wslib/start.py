# The one Python start behind wslib/launch.sh: check the version, then run the target in this same process.
# The launcher used to start Python twice, once to probe the version and once to run ws.py; now the probe is here.
# Every Python old enough to be on a path must be able to read this file and say it is too old, so it uses no
# syntax newer than Python 2.7, and nothing from the engine.
#
#   python wslib/start.py ROOT ws.py hook before-shell   a script, relative to the workspace ROOT or absolute
#   python wslib/start.py ROOT -m unittest discover      a module, as python -m runs it
#   python wslib/start.py ROOT hook before-shell         anything else is ws.py's arguments: older wiring sends these
#
# Exit 97 means "this Python is too old": the launcher then tries the next one on the path. No target exits 97.
import os
import sys

TOO_OLD = 97
MINIMUM = (3, 9)
HERE = os.path.dirname(os.path.abspath(__file__))


def first_path(folder):
    """Put folder where Python put this file's own folder, as if the target had been started directly."""
    if sys.path and os.path.abspath(sys.path[0] or os.curdir) == HERE:
        sys.path[0] = folder
    else:                                            # PYTHONSAFEPATH, or -I: Python added no folder of ours
        sys.path.insert(0, folder)


def main():
    if tuple(sys.version_info[:2]) < MINIMUM:
        sys.stderr.write("ws: %s is Python %d.%d, older than %d.%d.\n"
                         % (sys.executable, sys.version_info[0], sys.version_info[1], MINIMUM[0], MINIMUM[1]))
        sys.exit(TOO_OLD)
    import runpy
    if len(sys.argv) < 2:
        sys.stderr.write("ws: wslib/start.py needs the workspace folder as its first argument\n")
        sys.exit(2)
    root, args = sys.argv[1], sys.argv[2:]
    if args[:1] == ["-m"]:
        if len(args) < 2:
            sys.stderr.write("ws: -m needs a module name\n")
            sys.exit(2)
        sys.argv = [args[1]] + args[2:]
        first_path(os.getcwd())                      # as python -m sets it
        runpy.run_module(args[1], run_name="__main__", alter_sys=True)
        return
    if args and args[0].endswith(".py"):
        script, rest = args[0], args[1:]
    else:
        script, rest = "ws.py", args
    if not os.path.isabs(script):
        script = os.path.join(root, script)
    script = os.path.abspath(script)
    sys.argv = [script] + rest
    first_path(os.path.dirname(script))              # as python SCRIPT sets it
    runpy.run_path(script, run_name="__main__")


if __name__ == "__main__":
    main()
