#!/usr/bin/env python3
"""Export a patch and provenance for one exact, verified source commit."""
import json, os, re, subprocess
from pathlib import Path

def git(*args): return subprocess.check_output(["git", *args], text=True).strip()
u = json.loads(Path("supplemental/traffic/upstream.json").read_text())
assert u["repository"] == "henrygd/beszel"
assert re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+", u["tag"])
assert re.fullmatch(r"[0-9a-f]{40}", u["commit"])
subprocess.run(["git", "merge-base", "--is-ancestor", u["commit"], "HEAD"], check=True)
base = re.search(r'Version = "([^"]+)"', Path("beszel.go").read_text()).group(1)
assert base == u["tag"][1:], "upstream Version and manifest disagree"
version = base + "-plus.1-candidate." + os.environ.get("GITHUB_RUN_ID", "local") + "." + os.environ.get("GITHUB_RUN_ATTEMPT", "1")
sha = git("rev-parse", "HEAD")
out = Path(".plus-release"); out.mkdir(exist_ok=True)
(out / "traffic.patch").write_bytes(subprocess.check_output(["git", "diff", "--binary", u["commit"], sha]))
(out / "commits.txt").write_text(git("log", "--oneline", u["commit"] + ".." + sha) + "\n")
u.update(plus_commit=sha, plus_version=version, test_run=os.environ.get("GITHUB_SERVER_URL", "https://github.com") + "/" + os.environ.get("GITHUB_REPOSITORY", "CodeAIX/Beszel-Plus") + "/actions/runs/" + os.environ.get("GITHUB_RUN_ID", "local"), platforms=["linux/amd64", "linux/arm64"], migrations=sorted(p.name for p in Path("internal/migrations").glob("*.go") if "traffic" in p.name or "agent_history" in p.name), toolchain=Path("go.mod").read_text().splitlines()[2])
(out / "source-manifest.json").write_text(json.dumps(u, indent=2) + "\n")
if os.environ.get("GITHUB_OUTPUT"):
    with open(os.environ["GITHUB_OUTPUT"], "a") as f: f.write(f"version={version}\nsha={sha}\n")
print(version, sha)
