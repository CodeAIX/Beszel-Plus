#!/usr/bin/env python3
"""Start under 2 GB, cleanly stop, copy complete data, restore to a new container."""
import json, os, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path
image = sys.argv[1]
docker = ["docker"]
if os.environ.get("PLUS_DOCKER_CONTEXT"): docker += ["--context", os.environ["PLUS_DOCKER_CONTEXT"]]

def run(*args): return subprocess.check_output([*docker,*args], text=True).strip()
def healthy(name):
    port=json.loads(run("inspect",name))[0]["NetworkSettings"]["Ports"]["8090/tcp"][0]["HostPort"]
    for _ in range(100):
        try:
            with urllib.request.urlopen("http://127.0.0.1:"+port+"/api/health",timeout=1) as r:
                if r.status==200: return
        except Exception: time.sleep(.2)
    raise RuntimeError("Hub did not become healthy")

names=[]
with tempfile.TemporaryDirectory(prefix="plus-restore-") as temp:
    try:
        first=run("run","-d","--memory=2g","--name","plus-smoke-"+str(os.getpid()),"-p","127.0.0.1::8090","-e","CHECK_UPDATES=false",image);names.append(first);healthy(first)
        run("stop",first);run("cp",first+":/beszel_data",temp+"/backup")
        assert (Path(temp)/"backup/data.db").is_file()
        second=run("create","--memory=2g","--name","plus-restore-"+str(os.getpid()),"-p","127.0.0.1::8090","-e","CHECK_UPDATES=false",image);names.append(second)
        run("cp",temp+"/backup/.",second+":/beszel_data");run("start",second);healthy(second)
        print("2GB Hub startup, clean full-directory backup and independent restore passed")
    finally:
        for name in names: subprocess.run([*docker,"rm","-f","-v",name],stdout=subprocess.DEVNULL,check=False)
