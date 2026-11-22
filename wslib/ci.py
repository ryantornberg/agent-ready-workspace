"""The CI fact at session start: whether the newest CI run on the default branch failed, read with `gh`.

The session-start notice (parts/ci_notice.py) says when main's CI is red. The engine works the fact out here, as
decision 0004 asks, and the part only words it. Each `gh` call comes from a build function and is read by a parse
function, so the tests run every step on recorded output (tests/records/ci-gh.json).

1. The repository is this workspace's `origin`, read from its own git config file, through wslib/gitcall.py and
   inside the deadline. An origin that is a local path, or names no owner and repository, gives no fact and no
   call. Any other host is asked; when gh cannot answer for it, the notice says nothing.
2. `gh run list` reads the newest runs of the workflow on the branch. Runs from pull requests, runs not yet
   finished, and runs that were cancelled or skipped say nothing about the branch and are passed over.
3. When the newest of the rest failed, `gh run view` reads its jobs, for the steps that failed.

The notice must never fail or hold up a session. No `gh` on the path, no sign-in, no network, a malformed answer or
the time limit all give None, and the notice then says nothing. The origin read and both calls share one deadline,
BUDGET seconds, and the runner works the fact out beside the session's other facts, not after them. gh's own GH_REPO and GH_HOST are
removed from its environment, and every call names the repository, so no variable chooses what it reads.
"""
import json
import shutil
import subprocess
import time

from . import gitcall
from . import merge as merges
from . import shellfacts

BUDGET = 3.0               # seconds for every gh call of one session start
LIMIT = 20                 # runs read; a streak this long is reported as "at least"
RUN_FIELDS = "databaseId,status,conclusion,createdAt,event,displayTitle,url"
PASSED = ("success",)
FAILED = ("failure", "timed_out", "startup_failure")


class Failed(Exception):
    """A gh call failed, ran out of time, or answered with something this module cannot read."""


def _slug(repo):
    return f"{repo['host']}/{repo['owner']}/{repo['name']}"


# -- build: every gh call, as a list of words -------------------------------------------------------------------

def build_runs(repo, workflow, branch, limit=LIMIT):
    return ["gh", "run", "list", "-R", _slug(repo), "--workflow", workflow, "--branch", branch,
            "--limit", str(limit), "--json", RUN_FIELDS]


def build_jobs(repo, run_id):
    return ["gh", "run", "view", str(run_id), "-R", _slug(repo), "--json", "jobs"]


# -- parse: each answer, read strictly --------------------------------------------------------------------------

def _json(text):
    try:
        return json.loads(text)
    except (TypeError, ValueError) as error:
        raise Failed(f"gh's answer is not JSON: {error}")


def parse_runs(text):
    """The finished runs that say something about the branch, newest first, as gh lists them:
    [{"id", "conclusion", "created", "title", "url"}]. "conclusion" is "passed" or "failed"."""
    found = _json(text)
    if not isinstance(found, list):
        raise Failed("gh run list did not answer with a list")
    runs = []
    for run in found:
        if not isinstance(run, dict):
            raise Failed("gh run list answered with an entry that is not an object")
        if run.get("event") == "pull_request" or run.get("status") != "completed":
            continue
        conclusion = run.get("conclusion")
        if conclusion not in PASSED + FAILED:
            continue                   # cancelled, skipped, neutral: the run says nothing about the code
        if not isinstance(run.get("databaseId"), int) or not isinstance(run.get("createdAt"), str):
            raise Failed("gh run list answered with a run that has no id or start time")
        runs.append({"id": run["databaseId"], "conclusion": "passed" if conclusion in PASSED else "failed",
                     "created": run["createdAt"], "title": str(run.get("displayTitle") or ""),
                     "url": str(run.get("url") or "")})
    return runs


def parse_jobs(text):
    """The steps that failed, as "job: step", in gh's order; a job that failed with no failed step is named alone."""
    found = _json(text)
    jobs = found.get("jobs") if isinstance(found, dict) else None
    if not isinstance(jobs, list):
        raise Failed("gh run view did not answer with a list of jobs")
    steps = []
    for job in jobs:
        if not isinstance(job, dict) or job.get("conclusion") not in FAILED:
            continue
        name = str(job.get("name") or "a job")
        failed = [str(step.get("name") or "a step") for step in job.get("steps") or []
                  if isinstance(step, dict) and step.get("conclusion") in FAILED]
        steps += [f"{name}: {step}" for step in failed] or [name]
    return steps


def summary(runs, steps=None, read=None, limit=LIMIT):
    """The fact the part words: {"failed": 0} when the newest run passed; otherwise {"failed": n, "at_least": bool,
    "since", "title", "url", "steps"}. None when there is no run to judge. read: how many runs gh listed, those
    passed over included; when the streak runs to the end of a full list, older runs may have failed too."""
    if not runs:
        return None
    streak = []
    for run in runs:
        if run["conclusion"] != "failed":
            break
        streak.append(run)
    if not streak:
        return {"failed": 0}
    newest = streak[0]
    listed = len(runs) if read is None else read
    return {"failed": len(streak), "at_least": len(streak) == len(runs) and listed >= limit,
            "since": streak[-1]["created"], "title": newest["title"], "url": newest["url"], "steps": list(steps or [])}


# -- run: the calls, under one deadline -------------------------------------------------------------------------

def call(words, deadline):
    """gh's standard output for one call, or Failed. The program is gh from the path; nothing waits on a prompt."""
    program = shutil.which(words[0])
    if program is None:
        raise Failed("gh is not on the path")
    left = deadline - time.monotonic()
    if left <= 0:
        raise Failed("the time limit ran out")
    try:
        child = subprocess.Popen([program, *words[1:]], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                 stdin=subprocess.DEVNULL, env=merges.gh_environment())
    except OSError as error:
        raise Failed(f"gh could not start: {error}")
    try:
        out, _ = child.communicate(timeout=left)
    except subprocess.TimeoutExpired:
        # Killed and left: waiting for its output to close would wait on any process it started, such as a
        # credential helper, or the interpreter a wrapper script runs.
        child.kill()
        child.stdout.close()
        try:
            child.wait(timeout=1)          # reaps gh itself, which the kill ends at once
        except subprocess.TimeoutExpired:
            pass
        raise Failed("the time limit ran out")
    if child.returncode != 0:
        raise Failed(f"gh exited {child.returncode}")
    return out.decode("utf-8", "replace")


def repository(root, deadline):
    """{"host", "owner", "name"} of origin, from the repository's own config file, or Failed."""
    left = deadline - time.monotonic()
    url = gitcall.run(root, "config", "--local", "--get", "remote.origin.url", timeout=left) if left > 0 else None
    found = shellfacts.parse_url(url) if url and url.strip() else {"local": True}
    if found.get("local") or not found.get("owner") or not found.get("name"):
        raise Failed("origin names no repository on a host gh could ask")
    return {"host": found["host"], "owner": found["owner"], "name": found["name"]}


def fact(root, workflow, branch, budget=None, run=call):
    """The "ci" fact for the session-start hooks, or None on any error. run(words, deadline): the gh caller."""
    try:
        deadline = time.monotonic() + (BUDGET if budget is None else budget)
        repo = repository(root, deadline)
        text = run(build_runs(repo, workflow, branch), deadline)
        runs = parse_runs(text)
        found = summary(runs, read=len(_json(text)))
        if found and found["failed"]:
            found["steps"] = parse_jobs(run(build_jobs(repo, runs[0]["id"]), deadline))
        return found
    except Exception:          # no gh, no sign-in, no network, a strange answer: the notice says nothing
        return None
