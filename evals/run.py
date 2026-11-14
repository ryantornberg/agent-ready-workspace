#!/usr/bin/env python3
"""Run an eval case against a real agent, twice: with the playbook and without it.

    python3 evals/run.py fix-a-bug --model haiku

For each arm this:

  1. copies evals/scaffold into a fresh temporary git repository;
  2. for the "with" arm, adds the contract (evals/arm) and the real playbook and
     definition of done from docs/, so the eval tests the files the workspace ships;
  3. leaves another session's uncommitted edits in the folder;
  4. gives the agent the case's request and records what it does;
  5. inspects the folder the agent left and appends "state" lines the agent cannot fake;
  6. grades the transcript.

It writes evals/runs/<case>/with.json, without.json and record.json. The record
holds a hash of the playbook, which the eval_record check compares on every commit.

The agent here is Claude Code, run headless with only project settings, so the
operator's personal instructions do not leak into either arm. To use another
tool, replace agent_command and to_transcript; nothing else knows which agent ran.

Exit 0 when the with-playbook arm passes every grader.
"""
import argparse
import datetime
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "evals"))

import grade as grading  # noqa: E402
from parts import eval_record  # noqa: E402

SHIPPED_DOCS = ("docs/playbooks/fix-a-bug.md", "docs/definition-of-done.md")
OTHER_SESSION = {
    "README.md": "\nNote to self: ask whether Export should include cancelled orders.\n",   # appended to a tracked file
    "notes/todo.txt": "Draft, not ready to commit.\n",                                       # a new untracked file
}
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
READ_TOOLS = {"Read", "Grep", "Glob"}
OUTPUT_TAIL = 600   # characters of each command's output kept in the transcript


def sh(folder, *command, check=True):
    done = subprocess.run(command, cwd=folder, capture_output=True, text=True)
    if check and done.returncode != 0:
        raise RuntimeError(f"{' '.join(command)}: {done.stderr.strip() or done.stdout.strip()}")
    return done


def git(folder, *args, check=True):
    return sh(folder, "git", "-c", "user.name=eval", "-c", "user.email=eval@example.invalid",
              "-c", "commit.gpgsign=false", *args, check=check)


def prepare(folder, with_playbook):
    """Build the repository the agent starts in. Returns the starting commit."""
    shutil.copytree(ROOT / "evals/scaffold", folder, dirs_exist_ok=True)
    if with_playbook:
        shutil.copytree(ROOT / "evals/arm", folder, dirs_exist_ok=True)
        for doc in SHIPPED_DOCS:
            (folder / doc).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / doc, folder / doc)
    git(folder, "init", "-q", "-b", "main")
    git(folder, "add", "--all")
    git(folder, "commit", "-q", "-m", "Orders page")
    for name, text in OTHER_SESSION.items():
        path = folder / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(text)
    return git(folder, "rev-parse", "HEAD").stdout.strip()


def agent_command(request, model):
    return ["claude", "-p", request, "--model", model, "--output-format", "stream-json", "--verbose",
            "--setting-sources", "project", "--strict-mcp-config", "--no-session-persistence",
            "--permission-mode", "bypassPermissions"]


def result_text(content):
    if isinstance(content, list):
        return "\n".join(part.get("text", "") for part in content if isinstance(part, dict))
    return content or ""


def to_transcript(log, folder):
    """Convert a Claude Code stream-json log into transcript actions. Returns (actions, model, version)."""
    prefixes = sorted({str(folder), str(folder.resolve())}, key=len, reverse=True)

    def local(text):
        for prefix in prefixes:
            text = text.replace(prefix + "/", "").replace(prefix, ".")
        return text

    actions, pending, model, version, report = [], {}, None, None, ""
    for line in log.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "system" and event.get("subtype") == "init":
            model, version = event.get("model"), event.get("claude_code_version")
        elif event.get("type") == "assistant":
            for block in event.get("message", {}).get("content", []):
                if block.get("type") != "tool_use":
                    continue
                name, given = block.get("name"), block.get("input", {})
                if name == "Bash":
                    action = {"kind": "run", "target": local(given.get("command", "")), "ok": True}
                elif name in EDIT_TOOLS:
                    action = {"kind": "edit", "target": local(given.get("file_path") or given.get("notebook_path", "")), "ok": True}
                elif name in READ_TOOLS:
                    action = {"kind": "read", "target": local(given.get("file_path") or given.get("pattern", "")), "ok": True}
                else:
                    continue
                pending[block.get("id")] = action
                actions.append(action)
        elif event.get("type") == "user":
            content = event.get("message", {}).get("content", [])
            for block in content if isinstance(content, list) else []:
                if block.get("type") == "tool_result" and block.get("tool_use_id") in pending:
                    action = pending[block["tool_use_id"]]
                    action["ok"] = not block.get("is_error", False)
                    if action["kind"] == "run":
                        action["output"] = local(result_text(block.get("content")))[-OUTPUT_TAIL:]
        elif event.get("type") == "result":
            report = event.get("result") or ""
    actions.append({"kind": "report", "target": local(report), "ok": True})
    return actions, model, version


def suite_passes(folder):
    return sh(folder, sys.executable, "-m", "unittest", check=False).returncode == 0


def inspect(folder, start):
    """Facts about the folder the agent left. These are checked, not reported by the agent."""
    passes_after = suite_passes(folder)

    # The agent's tests, run against the code as it was before the fix, must fail.
    with tempfile.TemporaryDirectory() as scratch:
        before = pathlib.Path(scratch) / "before"
        shutil.copytree(folder, before, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        shutil.rmtree(before / "shop")
        for name in git(folder, "ls-tree", "-r", "--name-only", start, "shop").stdout.split():
            (before / name).parent.mkdir(parents=True, exist_ok=True)
            (before / name).write_text(git(folder, "show", f"{start}:{name}").stdout, encoding="utf-8")
        fails_on_original = not suite_passes(before)

    committed = git(folder, "diff", "--name-only", start, "HEAD").stdout.split()
    readme_committed = OTHER_SESSION["README.md"].strip() in git(folder, "show", "HEAD:README.md").stdout
    others_out = bool(committed) and "notes/todo.txt" not in committed and not readme_committed
    return [
        {"kind": "state", "target": "suite passes after the change", "ok": passes_after},
        {"kind": "state", "target": "tests fail on the original code", "ok": fails_on_original},
        {"kind": "state", "target": "a commit was made", "ok": bool(committed)},
        {"kind": "state", "target": "other edits stayed out of the commit", "ok": others_out},
    ]


def run_arm(case, model, with_playbook, timeout):
    with tempfile.TemporaryDirectory() as scratch:
        folder = pathlib.Path(scratch) / "orders"
        folder.mkdir()
        start = prepare(folder, with_playbook)
        done = subprocess.run(agent_command(case["request"], model), cwd=folder, capture_output=True, text=True, timeout=timeout)
        if done.returncode != 0 and not done.stdout.strip():
            raise RuntimeError(f"the agent did not run: {done.stderr.strip()[:300]}")
        actions, used_model, version = to_transcript(done.stdout, folder)
        actions.extend(inspect(folder, start))
    results = grading.grade(case, actions)
    return actions, {"passed": all(ok for _, ok in results), "graders": dict(results)}, used_model, version


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run an eval case with and without its playbook.")
    parser.add_argument("case")
    parser.add_argument("--model", default="haiku")
    parser.add_argument("--timeout", type=int, default=900, help="seconds allowed per arm")
    args = parser.parse_args(argv)

    case = json.loads((ROOT / "evals/cases" / f"{args.case}.json").read_text(encoding="utf-8"))
    out = ROOT / "evals/runs" / case["name"]
    out.mkdir(parents=True, exist_ok=True)
    record = {
        "case": case["name"],
        "date": datetime.date.today().isoformat(),
        "playbook": case["playbook"],
        "playbook_sha256": eval_record.playbook_hash((ROOT / case["playbook"]).read_text(encoding="utf-8")),
    }
    for arm, with_playbook in (("with", True), ("without", False)):
        print(f"running {case['name']} {arm} the playbook on {args.model} ...", flush=True)
        actions, result, model, version = run_arm(case, args.model, with_playbook, args.timeout)
        (out / f"{arm}.json").write_text(json.dumps(actions, indent=2) + "\n", encoding="utf-8")
        record.update({"agent": f"Claude Code {version}", "model": model, f"{arm}_playbook": result})
        for grader_id, ok in result["graders"].items():
            print(f"  {'pass' if ok else 'FAIL'}  {grader_id}")
    (out / "record.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return 0 if record["with_playbook"]["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
