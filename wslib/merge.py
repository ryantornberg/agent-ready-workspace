"""`ws.py merge NUMBER`: merge a pull request on GitHub, only once CI passed on its exact head commit.

The steps, each a `gh` call made from a build function and read by a parse function, so the tests can run every
step on recorded output (tests/records/merge-gh.json):

1. The repository is this workspace's `origin`, read from the repository's own git config file. The pull
   request is read: it must be open, published (not a draft), and from a branch of this repository.
2. The checks required are read from the branch rule of the pull request's base: the classic branch protection
   and any ruleset. A base that requires none is refused, since nothing would show that CI passed.
3. Each required check must have passed on exactly the pull request's head commit: its newest run of that name,
   from the app the rule names, completed with success. A run from GitHub Actions counts only when its check suite
   is a workflow run of the pull_request event, read from the commit's workflow runs, so a push or a scheduled run
   of the same name on the same commit is not read (M4 plan, criterion 3). A run from another app, and a legacy
   commit status of that name, count as before.
4. It merges on GitHub with a merge commit, never a squash or a rebase, and only if the head is still that
   commit: `gh pr merge NUMBER --merge --match-head-commit SHA`. A squash would leave the branch's own commits
   unreachable once the branch is gone, and a proof anchor pinned to one of them with it (decision 0006). It then
   reads the pull request back and checks that its merge commit has two parents.
5. It retargets each open pull request based on the merged branch to the merged one's base, and reads the answer
   back (Q84). GitHub closes a pull request whose base branch is deleted, so when a retarget fails, or the list of
   such pull requests cannot be read, nothing is deleted: the merge went through, and the message says which pull
   requests moved and which did not.
6. It deletes the branch on GitHub. A branch that is already gone is noted, not an error.
7. It brings the main working copy up to date, under the conditions of the session-start fast-forward
   (wslib/lease.py): only a clean main, never while another live session holds the lease. Otherwise it says why.

No working copy takes part in the merge, so the lease and the caller's own files play no part in it. No variable
the helper reads and no argument but the number changes what it calls: the program is `gh`, every call names the
repository as host/owner/name with -R or --hostname and the path, and gh's own GH_REPO and GH_HOST are removed from
its environment. What chooses a program or a configuration for every command alike, PATH, HOME or gh's config
folder, is outside it: an agent that can set those can run gh itself. See docs/changing-the-machinery.md.
"""
import json
import os
import subprocess
import urllib.parse

from . import gitcall
from . import lease as leases
from . import shellfacts

PAGE = "docs/changing-the-machinery.md"
PR_FIELDS = "number,state,isDraft,baseRefName,headRefName,headRefOid,isCrossRepository,url"
TIMEOUT = 120              # seconds for one gh call
REMOVED = ("GH_REPO", "GH_HOST")
# Variables that change the config git reads; the repository's own file decides, not the caller's environment.
GIT_CONFIG_VARIABLES = ("GIT_CONFIG_PARAMETERS", "GIT_CONFIG_COUNT", "GIT_CONFIG_GLOBAL", "GIT_CONFIG_SYSTEM",
                        "GIT_CONFIG_NOSYSTEM", "GIT_CONFIG")
ANY_APP = (None, -1)
ACTIONS = "github-actions"   # the app slug of GitHub Actions' check runs
PAGE_SIZE = 100


class MergeError(RuntimeError):
    """The merge cannot go ahead, or a step failed: the runner prints it and exits 2."""


class Refused(Exception):
    """The pull request is not ready to merge: the reasons, one per line."""

    def __init__(self, reasons):
        super().__init__("\n".join(reasons))
        self.reasons = list(reasons)


# -- the repository ---------------------------------------------------------------------------------------------

def git_environment(environ=None):
    """The caller's environment without the variables git sets for a hook or reads as extra config."""
    environ = os.environ if environ is None else environ
    env = {key: value for key, value in environ.items()
           if key not in gitcall.HOOK_VARIABLES and key not in GIT_CONFIG_VARIABLES
           and not key.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_"))}
    env["GIT_TERMINAL_PROMPT"] = "0"
    return env


def repository(root, environ=None):
    """{"host", "owner", "name"} of origin, from the repository's own config file only."""
    try:
        done = subprocess.run(["git", "-C", str(root), "config", "--local", "--get", "remote.origin.url"],
                              capture_output=True, env=git_environment(environ), timeout=10, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise MergeError(f"git could not read this repository's origin: {error}")
    url = done.stdout.decode("utf-8", "replace").strip()
    if done.returncode != 0 or not url:
        raise MergeError("this repository has no origin remote in its own config, so there is no GitHub "
                         f"repository to merge in; see {PAGE}")
    found = shellfacts.parse_url(url)
    if found.get("local") or not found.get("owner") or not found.get("name"):
        raise MergeError(f"origin is {url}, which names no GitHub repository; see {PAGE}")
    return {"host": found["host"], "owner": found["owner"], "name": found["name"]}


def gh_environment(environ=None):
    """The caller's environment without the variables gh reads to choose a repository or host, and with no prompt."""
    environ = os.environ if environ is None else environ
    env = {key: value for key, value in environ.items() if key not in REMOVED}
    env.update({"GH_PROMPT_DISABLED": "1", "GH_NO_UPDATE_NOTIFIER": "1", "NO_COLOR": "1", "GH_PAGER": "cat"})
    return env


# -- build: every gh call, as a list of words -------------------------------------------------------------------

def _slug(repo):
    return f"{repo['host']}/{repo['owner']}/{repo['name']}"


def _path(repo, *rest):
    return "/".join(["repos", repo["owner"], repo["name"], *rest])


def _quote(name):
    return urllib.parse.quote(name, safe="/")


def build_view(repo, number):
    return ["gh", "pr", "view", str(number), "-R", _slug(repo), "--json", PR_FIELDS]


def build_branch_rule(repo, branch):
    return ["gh", "api", "--hostname", repo["host"], _path(repo, "branches", _quote(branch))]


def build_rulesets(repo, branch):
    return ["gh", "api", "--hostname", repo["host"], _path(repo, "rules", "branches", _quote(branch))]


def build_check_runs(repo, sha):
    return ["gh", "api", "--hostname", repo["host"], _path(repo, "commits", sha, "check-runs") + "?per_page=100"]


def build_workflow_runs(repo, sha):
    return ["gh", "api", "--hostname", repo["host"], _path(repo, "actions", "runs") + f"?head_sha={sha}&per_page={PAGE_SIZE}"]


def build_statuses(repo, sha):
    return ["gh", "api", "--hostname", repo["host"], _path(repo, "commits", sha, "status") + "?per_page=100"]


def build_merge(repo, number, sha):
    return ["gh", "pr", "merge", str(number), "-R", _slug(repo), "--merge", "--match-head-commit", sha]


def build_merged(repo, number):
    return ["gh", "pr", "view", str(number), "-R", _slug(repo), "--json", "state,mergeCommit"]


def build_commit(repo, sha):
    return ["gh", "api", "--hostname", repo["host"], _path(repo, "commits", sha)]


def build_dependents(repo, branch):
    """The open pull requests whose base is branch."""
    value = urllib.parse.quote(branch, safe="")
    return ["gh", "api", "--hostname", repo["host"], _path(repo, "pulls") + f"?state=open&base={value}&per_page={PAGE_SIZE}"]


def build_retarget(repo, number, base):
    return ["gh", "api", "--hostname", repo["host"], "-X", "PATCH", _path(repo, "pulls", str(number)), "-f", f"base={base}"]


def build_delete(repo, branch):
    return ["gh", "api", "--hostname", repo["host"], "-X", "DELETE", _path(repo, "git", "refs", "heads", _quote(branch))]


# -- parse: each answer, as (exit code, standard output, standard error) ----------------------------------------

def _json(answer, what):
    code, out, err = answer
    if code != 0:
        raise MergeError(f"gh could not read {what}: {(err or out).strip() or f'exit {code}'}")
    try:
        return json.loads(out)
    except ValueError:
        raise MergeError(f"gh's answer about {what} is not JSON")


def parse_pull_request(answer, number):
    data = _json(answer, f"pull request {number}")
    if not isinstance(data, dict) or not isinstance(data.get("headRefOid"), str) or len(data["headRefOid"]) != 40:
        raise MergeError(f"gh's answer about pull request {number} has no head commit")
    reasons = []
    if data.get("state") != "OPEN":
        reasons.append(f"pull request {number} is {str(data.get('state')).lower()}, not open")
    if data.get("isDraft"):
        reasons.append(f"pull request {number} is a draft. Once CI passes, publish it with gh pr ready {number}, "
                       f"then merge")
    if data.get("isCrossRepository"):
        reasons.append(f"pull request {number} comes from another repository's branch, which this helper cannot "
                       f"delete; a person merges it")
    if not data.get("baseRefName") or not data.get("headRefName"):
        reasons.append(f"gh's answer about pull request {number} names no base or head branch")
    if reasons:
        raise Refused(reasons)
    return data


def parse_required(branch_answer, rules_answer, branch):
    """[{"context", "app_id"}] the base branch's rule requires: classic protection and rulesets together."""
    rule = _json(branch_answer, f"the branch rule of {branch}")
    rules = _json(rules_answer, f"the rulesets of {branch}")
    required = []
    checks = ((rule.get("protection") or {}).get("required_status_checks") or {}) if isinstance(rule, dict) else {}
    if checks.get("checks"):
        required += [{"context": c.get("context"), "app_id": c.get("app_id")} for c in checks["checks"]]
    else:
        required += [{"context": c, "app_id": None} for c in checks.get("contexts") or ()]
    for item in rules if isinstance(rules, list) else ():
        if isinstance(item, dict) and item.get("type") == "required_status_checks":
            for c in (item.get("parameters") or {}).get("required_status_checks") or ():
                required.append({"context": c.get("context"), "app_id": c.get("integration_id")})
    unique = []
    for item in required:
        if item["context"] and item not in unique:
            unique.append(item)
    if not unique:
        raise Refused([f"the branch rule of {branch} requires no check, so nothing shows that CI passed. Set the "
                       f"required checks in the repository's branch rule first; see {PAGE}"])
    return unique


def parse_check_runs(answer, sha):
    data = _json(answer, f"the check runs of {sha[:7]}")
    runs = data.get("check_runs") if isinstance(data, dict) else None
    if not isinstance(runs, list):
        raise MergeError(f"gh's answer about the check runs of {sha[:7]} holds no list")
    if isinstance(data.get("total_count"), int) and data["total_count"] > len(runs):
        raise Refused([f"{sha[:7]} has {data['total_count']} check runs, more than one page; this helper reads one "
                       f"page of 100, so a person merges it"])
    return runs


def parse_workflow_runs(answer, sha):
    """The check suites of the commit's workflow runs, as {check suite id: event}."""
    data = _json(answer, f"the workflow runs of {sha[:7]}")
    runs = data.get("workflow_runs") if isinstance(data, dict) else None
    if not isinstance(runs, list):
        raise MergeError(f"gh's answer about the workflow runs of {sha[:7]} holds no list")
    if isinstance(data.get("total_count"), int) and data["total_count"] > len(runs):
        raise Refused([f"{sha[:7]} has {data['total_count']} workflow runs, more than one page; this helper reads one "
                       f"page of {PAGE_SIZE}, so a person merges it"])
    return {run["check_suite_id"]: run.get("event") for run in runs
            if isinstance(run, dict) and run.get("head_sha") == sha and isinstance(run.get("check_suite_id"), int)}


def pull_request_run(run, suites):
    """Whether a check run may count: one from GitHub Actions only when its workflow run is the pull request's."""
    if (run.get("app") or {}).get("slug") != ACTIONS:
        return True
    suite = (run.get("check_suite") or {}).get("id")
    return suite in suites and suites[suite] == "pull_request"


def parse_statuses(answer, sha):
    data = _json(answer, f"the commit statuses of {sha[:7]}")
    statuses = data.get("statuses") if isinstance(data, dict) else None
    return statuses if isinstance(statuses, list) else []


def judge(required, runs, statuses, sha, suites):
    """Why the head commit has not passed every required check, one reason per check; empty when it has.
    suites: {check suite id: event} of the commit's workflow runs (parse_workflow_runs)."""
    reasons = []
    for need in required:
        name, app = need["context"], need.get("app_id")
        mine = [run for run in runs if isinstance(run, dict) and run.get("name") == name
                and run.get("head_sha") == sha
                and (app in ANY_APP or (run.get("app") or {}).get("id") == app)
                and pull_request_run(run, suites)]
        if mine:
            newest = max(mine, key=lambda run: run.get("id") or 0)
            if newest.get("status") != "completed":
                reasons.append(f"{name}: still {newest.get('status') or 'running'} on {sha[:7]}")
            elif newest.get("conclusion") != "success":
                reasons.append(f"{name}: {newest.get('conclusion')} on {sha[:7]}")
            continue
        status = next((s for s in statuses if isinstance(s, dict) and s.get("context") == name), None)
        if status is not None and app in ANY_APP:
            if status.get("state") != "success":
                reasons.append(f"{name}: {status.get('state')} on {sha[:7]}")
            continue
        reasons.append(f"{name}: has not run on {sha[:7]} for the pull request; a push or a scheduled run does not count")
    return reasons


def parse_merge(answer, number):
    code, out, err = answer
    if code != 0:
        raise MergeError(f"GitHub did not merge pull request {number}: {(err or out).strip() or f'exit {code}'}. "
                         f"If its head moved, wait for CI on the new head and run python3 ws.py merge {number} again")


def parse_merged(answer, number):
    data = _json(answer, f"pull request {number} after the merge")
    data = data if isinstance(data, dict) else {}
    oid = (data.get("mergeCommit") or {}).get("oid")
    if data.get("state") != "MERGED" or not isinstance(oid, str):
        raise MergeError(f"pull request {number} is {data.get('state')} after the merge, not merged")
    return oid


def parse_commit(answer, sha):
    data = _json(answer, f"commit {sha[:7]}")
    parents = data.get("parents") if isinstance(data, dict) else None
    if not isinstance(parents, list):
        raise MergeError(f"gh's answer about commit {sha[:7]} lists no parents")
    return len(parents)


def _kept(branch, done, why):
    moved = "".join(f" Retargeted already: #{number}." for number in done)
    return MergeError(f"the merge went through, but the branch {branch} was not deleted: {why}.{moved} GitHub closes "
                      f"an open pull request whose base branch is deleted, so each one still based on {branch} needs a "
                      f"retarget first. A retarget by hand is a write on a pull request the merge did not name: report "
                      f"this to the person and ask before you make it (docs/playbooks/git-host-operations.md, which "
                      f"writes need a yes). Then: gh pr edit NUMBER --base BASE for each, and git push origin --delete "
                      f"{branch} once nothing is based on it")


def parse_dependents(answer, branch):
    """[{"number", "head"}] of the open pull requests based on branch."""
    code, out, err = answer
    if code != 0:
        raise _kept(branch, [], f"the open pull requests based on it could not be listed: "
                                f"{(err or out).strip() or f'exit {code}'}")
    try:
        data = json.loads(out)
    except ValueError:
        data = None
    if not isinstance(data, list):
        raise _kept(branch, [], "gh's list of the open pull requests based on it is not a list")
    if len(data) >= PAGE_SIZE:
        raise _kept(branch, [], f"{PAGE_SIZE} or more open pull requests are based on it, more than one page")
    found = []
    for item in data:
        if not isinstance(item, dict) or not isinstance(item.get("number"), int):
            raise _kept(branch, [], "gh's list of the open pull requests based on it holds an entry with no number")
        if item.get("state") == "open" and (item.get("base") or {}).get("ref") == branch:
            found.append({"number": item["number"], "head": (item.get("head") or {}).get("ref")})
    return found


def parse_retarget(answer, number, base):
    """None when GitHub's answer shows the pull request on base; else what went wrong."""
    code, out, err = answer
    if code != 0:
        return (err or out).strip() or f"exit {code}"
    try:
        data = json.loads(out)
    except ValueError:
        return "gh's answer is not JSON"
    if not isinstance(data, dict):
        return "gh's answer is not a pull request"
    got = (data.get("base") or {}).get("ref")
    if data.get("number") != number or got != base:
        return f"GitHub's answer names its base as {got}, not {base}"
    return None


def parse_delete(answer, branch):
    """"deleted" or "gone"; raises when GitHub refused for another reason."""
    code, out, err = answer
    if code == 0:
        return "deleted"
    if "Reference does not exist" in (out or "") + (err or ""):
        return "gone"
    raise MergeError(f"the merge went through, but the branch {branch} could not be deleted: "
                     f"{(err or out).strip() or f'exit {code}'}. Delete it with git push origin --delete {branch}")


# -- run --------------------------------------------------------------------------------------------------------

def call_gh(words, environ=None):
    """(exit code, standard output, standard error) of one gh call."""
    try:
        done = subprocess.run(words, capture_output=True, env=gh_environment(environ), timeout=TIMEOUT,
                              stdin=subprocess.DEVNULL)
    except FileNotFoundError:
        raise MergeError("gh is not installed, or not on the PATH; see https://cli.github.com")
    except (OSError, subprocess.TimeoutExpired) as error:
        raise MergeError(f"gh did not answer: {error}")
    return (done.returncode, done.stdout.decode("utf-8", "replace").replace("\r\n", "\n"),
            done.stderr.decode("utf-8", "replace").replace("\r\n", "\n"))


def merge(root, number, call=call_gh, say=print, update=None, environ=None):
    """Merge pull request NUMBER. Returns 0 when merged, 1 when refused; raises MergeError when a step fails."""
    repo = repository(root, environ)
    slug = f"{repo['owner']}/{repo['name']}"
    try:
        pr = parse_pull_request(call(build_view(repo, number)), number)
        sha, base, branch = pr["headRefOid"], pr["baseRefName"], pr["headRefName"]
        required = parse_required(call(build_branch_rule(repo, base)), call(build_rulesets(repo, base)), base)
        runs = parse_check_runs(call(build_check_runs(repo, sha)), sha)
        suites = parse_workflow_runs(call(build_workflow_runs(repo, sha)), sha)
        statuses = parse_statuses(call(build_statuses(repo, sha)), sha)
        reasons = judge(required, runs, statuses, sha, suites)
        if reasons:
            raise Refused(reasons)
    except Refused as refused:
        say(f"Not merged: {slug}#{number}.")
        for reason in refused.reasons:
            say(f"  {reason}")
        say(f"Every check the branch rule requires must pass on the head commit first; see {PAGE}")
        return 1
    say(f"{len(required)} required check(s) passed on {sha[:7]}, the head of {slug}#{number}.")
    parse_merge(call(build_merge(repo, number, sha)), number)
    oid = parse_merged(call(build_merged(repo, number)), number)
    parents = parse_commit(call(build_commit(repo, oid)), oid)
    if parents != 2:
        raise MergeError(f"pull request {number} merged as {oid[:7]}, which has {parents} parent(s), not a merge "
                         f"commit. Allow merge commits only in the repository's settings; see {PAGE}")
    say(f"Merged {slug}#{number} into {base} as {oid[:7]}, a merge commit.")
    retarget(repo, branch, base, call, say)
    deleted = parse_delete(call(build_delete(repo, branch)), branch)
    say(f"Deleted the branch {branch} on GitHub." if deleted == "deleted" else f"The branch {branch} was already gone.")
    outcome, note = (update or _update)(root)
    if outcome == "moved":
        say("Brought the main working copy up to date with origin/main.")
    elif outcome == "current":
        say("The main working copy was already up to date.")
    else:
        say(f"Did not bring the main working copy up to date. {note or ''}".rstrip())
    return 0


def retarget(repo, branch, base, call, say):
    """Move each open pull request based on branch to base. Raises MergeError, so nothing is deleted, when one fails."""
    done = []
    for item in parse_dependents(call(build_dependents(repo, branch)), branch):
        number = item["number"]
        problem = parse_retarget(call(build_retarget(repo, number, base)), number, base)
        if problem is not None:
            raise _kept(branch, done, f"#{number} could not be retargeted to {base}: {problem}")
        done.append(number)
        say(f"Retargeted #{number} ({item['head']}) from {branch} to {base}. Its earlier review covered the old range: "
            f"do not publish it until the person says whether that review stands.")


def _update(root):
    return leases.update_main(root, leases.tool_pid("claude-code"))
