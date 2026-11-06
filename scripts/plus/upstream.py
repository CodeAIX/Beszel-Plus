#!/usr/bin/env python3
"""Prepare a reviewable three-way merge; conflicts stop before publication."""
import json, os, re, subprocess, sys
from pathlib import Path

def run(*args):
    return subprocess.check_output(args, text=True).strip()

def output(key, value):
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f: f.write(f"{key}={value}\n")
    print(f"{key}={value}")

current = json.loads(Path("supplemental/traffic/upstream.json").read_text())
latest = json.loads(run("gh", "api", "repos/henrygd/beszel/releases/latest"))
tag = latest["tag_name"]
if latest["draft"] or latest["prerelease"] or not re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+", tag):
    raise SystemExit("Latest release is not a supported stable tag")
version = lambda value: tuple(map(int, value.removeprefix("v").split(".")))
if version(tag) <= version(current["tag"]):
    output("build", "false"); output("checked_tag", tag); sys.exit(0)
branch = "plus/upstream-" + tag
if run("git", "ls-remote", "--heads", "origin", branch):
    output("build", "false"); output("existing_branch", branch); sys.exit(0)
run("git", "fetch", "https://github.com/henrygd/beszel.git", "refs/tags/" + tag)
sha = run("git", "rev-parse", "FETCH_HEAD^{commit}")
upstream = run("git", "show", sha + ":internal/entities/system/system.go")
body = upstream.split("type CombinedData struct {", 1)[1].split("\n}", 1)[0]
for key in (7, 8):
    if re.search(r'cbor:"' + str(key) + r'(?:,|")', body):
        raise SystemExit(f"Upstream allocated CombinedData key {key}; manual protocol migration required")
actions = run("git", "show", sha + ":internal/common/common-ws.go").split("const (", 1)[1].split("\n)", 1)[0]
names = re.findall(r'^\s*([A-Z]\w*)\b', actions, re.M)
if (names != ["GetData", "CheckFingerprint", "GetContainerLogs", "GetContainerInfo", "GetSmartData", "GetSystemdInfo", "GetZfsData", "SyncNetworkMonitors", "GetPackageUpdates", "GetSystemdLogs"]
    or not re.search(r'^\s*GetData\s+WebSocketAction\s*=\s*iota\s*(?://[^\n]*)?$', actions, re.M)
    or re.search(r'^\s*(?!GetData\b)[A-Z]\w*[^/\n]*=', actions, re.M)):
    raise SystemExit("Upstream action layout changed; verify reserved GetHistory action 10 before merging")
run("git", "config", "user.name", "beszel-plus[bot]")
run("git", "config", "user.email", "beszel-plus[bot]@users.noreply.github.com")
run("git", "checkout", "-b", branch)
previous = run("git", "rev-parse", "HEAD")
subprocess.run(["git", "merge", "--no-ff", "--no-commit", sha], check=True)
# Keep fork workflows unchanged: GITHUB_TOKEN cannot write upstream workflow
# changes, and inherited publishing must never activate in a candidate branch.
workflow_diff = run("git", "diff", previous, "--", ".github/workflows")
Path("supplemental/traffic/upstream-workflows.diff").write_text(workflow_diff + "\n")
run("git", "restore", "--source=" + previous, "--staged", "--worktree", "--", ".github/workflows")
current.update(tag=tag, commit=sha)
Path("supplemental/traffic/upstream.json").write_text(json.dumps(current, indent=2) + "\n")
run("git", "add", "supplemental/traffic/upstream.json", "supplemental/traffic/upstream-workflows.diff", ".github/workflows")
run("git", "commit", "-m", "chore(plus): record upstream " + tag)
run("git", "push", "origin", branch)
output("build", "true"); output("ref", run("git", "rev-parse", "HEAD")); output("branch", branch)
