#!/usr/bin/env python3
import json, os, subprocess
from pathlib import Path
subprocess.run(["python3", "scripts/plus/export.py"],check=True)
m=json.loads(Path(".plus-release/source-manifest.json").read_text())
assert m['plus_commit']==os.environ['PLUS_SHA']
# Ref creation requires workflow-write if these differ from the default branch.
# Halt before publishing images; upstream.py preserves our reviewed workflows.
subprocess.run(["git","fetch","origin","plus/main"],check=True)
subprocess.run(["git","diff","--exit-code","origin/plus/main","HEAD","--",".github/workflows"],check=True)
subprocess.run(["gh","api","--method","POST","repos/"+os.environ['GITHUB_REPOSITORY']+"/git/refs","-f","ref=refs/tags/v"+m['plus_version'],"-f","sha="+m['plus_commit']],check=True)
with open(os.environ['GITHUB_ENV'],'a') as f:f.write('PLUS_VERSION='+m['plus_version']+'\n')
