#!/usr/bin/env python3
"""Run an eval case against a real agent, twice: with the workspace's guidance and without it.

    python3 evals/run.py fix-a-bug --model haiku --runs 5

For each arm this:

  1. copies evals/scaffold into a fresh temporary git repository;
  2. for the "with" arm, adds the guidance the case lists: a short contract
     (evals/arm) and the real playbook and definition of done from docs/, so the
     eval tests the files the workspace ships. The "without" arm gets none of it;
  3. leaves another session's uncommitted edits in the folder;
  4. gives the agent the case's request and records what it does;
  5. inspects the folder the agent left and appends "state" lines the agent cannot fake;
  6. grades the transcript.

It runs each arm several times, because one run says little: models vary from
run to run. It writes evals/runs/<case>/with-N.json, without-N.json and record.json. The record
holds one hash over the case and its guidance files, which the eval_record check
compares on every commit.

The agent here is Claude Code, run headless with only project settings and an
empty global git config, so the operator's personal instructions and identity
do not reach either arm. A run whose transcript still holds the operator's
user name, home folder or git identity is refused, and nothing is written. To use another
tool, replace agent_command and to_transcript; nothing else knows which agent ran.

Exit 0 when every with-guidance run passes every grader.
"""
import argparse
import concurrent.futures
import datetime
import getpass
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "evals"))

import grade as grading  # noqa: E402
from parts import eval_record  # noqa: E402
from wslib import snapshot as snapshots  # noqa: E402

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


def prepare(folder, case, with_guidance):
    """Build the repository the agent starts in. Returns the starting commit."""
    shutil.copytree(ROOT / case["scaffold_dir"], folder, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))
    if with_guidance:
        shutil.copytree(ROOT / "evals/arm", folder, dirs_exist_ok=True)
        for doc in case["guidance"]:
            if not doc.startswith("evals/arm/"):
                (folder / doc).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(ROOT / doc, folder / doc)
    git(folder, "init", "-q", "-b", "main")
    git(folder, "config", "user.name", "eval")              # the agent commits as this, not as the operator
    git(folder, "config", "user.email", "eval@example.invalid")
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
        """Remove what would identify the machine: the temporary folder, the home folder and the user name."""
        for prefix in prefixes:
            text = text.replace(prefix + "/", "").replace(prefix, ".")
        text = text.replace(str(pathlib.Path.home()), "~")
        return re.sub(rf"\b{re.escape(getpass.getuser())}\b", "user", text)

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


def operator_identity():
    """Strings that must never reach a transcript: the user name, the home folder and the git identity."""
    found = {getpass.getuser(), str(pathlib.Path.home())}
    for key in ("user.name", "user.email"):
        value = subprocess.run(["git", "config", "--global", key], capture_output=True, text=True).stdout.strip()
        if value:
            found.add(value)
    return [value for value in found if len(value) > 2]


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


def run_arm(case, model, with_guidance, timeout):
    with tempfile.TemporaryDirectory() as scratch:
        folder = pathlib.Path(scratch) / "orders"
        folder.mkdir()
        start = prepare(folder, case, with_guidance)
        # The agent must not see the operator's git identity or settings: point git at an empty global config.
        empty = pathlib.Path(scratch) / "gitconfig"
        empty.write_text("", encoding="utf-8")
        env = {**os.environ, "GIT_CONFIG_GLOBAL": str(empty), "GIT_CONFIG_NOSYSTEM": "1"}
        done = subprocess.run(agent_command(case["request"], model), cwd=folder, env=env, capture_output=True, text=True, timeout=timeout)
        if done.returncode != 0 and not done.stdout.strip():
            raise RuntimeError(f"the agent did not run: {done.stderr.strip()[:300]}")
        actions, used_model, version = to_transcript(done.stdout, folder)
        actions.extend(inspect(folder, start))
    leaked = [secret for secret in operator_identity() if secret.lower() in json.dumps(actions).lower()]
    if leaked:
        raise RuntimeError("a transcript holds the operator's identity; nothing was written")
    results = grading.grade(case, actions)
    return actions, {"passed": all(ok for _, ok in results), "graders": dict(results)}, used_model, version


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run an eval case with and without the workspace's guidance.")
    parser.add_argument("case")
    parser.add_argument("--model", default="haiku")
    parser.add_argument("--runs", type=int, default=5, help="runs per arm; one run says little, because models vary")
    parser.add_argument("--timeout", type=int, default=900, help="seconds allowed per run")
    args = parser.parse_args(argv)

    case_path = f"evals/cases/{args.case}.json"
    case = json.loads((ROOT / case_path).read_text(encoding="utf-8"))
    tree = snapshots.Tree(ROOT)
    covered = eval_record.covered_files(case_path, case, list(tree.paths()))
    record = {
        "case": case["name"],
        "date": datetime.date.today().isoformat(),
        "playbook": case["playbook"],
        "covers": covered,
        "guidance_sha256": eval_record.guidance_hash({f: tree.read(f) or "" for f in covered}),
        "runs_per_arm": args.runs,
    }

    jobs = [(arm, with_guidance, number) for arm, with_guidance in (("with", True), ("without", False))
            for number in range(1, args.runs + 1)]
    print(f"running {case['name']}: {args.runs} runs per arm on {args.model} ...", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        finished = list(pool.map(lambda job: run_arm(case, args.model, job[1], args.timeout), jobs))

    out = ROOT / "evals/runs" / case["name"]
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("with*.json"):   # matches without*.json too
        old.unlink()
    for arm in ("with", "without"):
        results = []
        for (job_arm, _, number), (actions, result, model, version) in zip(jobs, finished):
            if job_arm == arm:
                (out / f"{arm}-{number}.json").write_text(json.dumps(actions, indent=2) + "\n", encoding="utf-8")
                results.append(result)
                record.update({"agent": f"Claude Code {version}", "model": model})
        record[f"{arm}_guidance"] = {
            "passed": all(result["passed"] for result in results),
            "runs_passing_every_grader": sum(result["passed"] for result in results),
            "runs_passing_each_grader": {grader["id"]: sum(result["graders"][grader["id"]] for result in results)
                                         for grader in case["graders"]},
        }
    (out / "record.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    print(f"\n{'runs passing, of ' + str(args.runs):<44}{'with':>6}{'without':>9}")
    for grader in case["graders"]:
        counts = [record[f"{arm}_guidance"]["runs_passing_each_grader"][grader["id"]] for arm in ("with", "without")]
        print(f"{grader['id']:<44}{counts[0]:>6}{counts[1]:>9}")
    return 0 if record["with_guidance"]["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
