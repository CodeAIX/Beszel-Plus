#!/usr/bin/env python3
"""Resume only release metadata; never rebuild or retag verified images."""
import hashlib,json,os,re,subprocess,tempfile
from pathlib import Path
run_id=os.environ['VERIFIED_RUN'];assert re.fullmatch(r'[0-9]+',run_id)
def gh(*args):return subprocess.check_output(['gh',*args],text=True).strip()
repo=os.environ['GITHUB_REPOSITORY']
r=json.loads(gh('api',f'repos/{repo}/actions/runs/{run_id}'))
assert r['path']=='.github/workflows/plus-release.yml' and r['event']=='workflow_dispatch'
jobs=json.loads(gh('api',f'repos/{repo}/actions/runs/{run_id}/jobs'))['jobs']
assert any(j['name']=='verify' and j['conclusion']=='success' for j in jobs)
image=next(j for j in jobs if j['name']=='images')
for name in ['Start, back up and restore isolated Hub','Publish Hub','Publish Docker Agent with vnStat CLI']:
 assert any(s['name']==name and s['conclusion']=='success' for s in image['steps']),name
with tempfile.TemporaryDirectory() as directory:
 gh('run','download',run_id,'-n','plus-publication','-D',directory)
 p=Path(directory)
 for name in ['traffic.patch','commits.txt','source-manifest.json']:
  lines=(p/'SHA256SUMS').read_text().splitlines()
  digest=next(l.split()[0] for l in lines if l.split()[1]==name)
  assert hashlib.sha256((p/name).read_bytes()).hexdigest()==digest
 m=json.loads((p/'source-manifest.json').read_text());version=m['plus_version']
 assert re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+-plus\.1-candidate\.'+run_id+r'\.[0-9]+',version)
 assert re.fullmatch('[a-f0-9]{40}',m['plus_commit'])
 tag='v'+version
 ref=json.loads(gh('api',f'repos/{repo}/git/ref/tags/{tag}'))
 assert ref['object']['type']=='commit' and ref['object']['sha']==m['plus_commit']
 for name,path in [('hub','beszel'),('agent','beszel-agent')]:
  assert re.fullmatch('ghcr.io/codeaix/beszel-plus/'+path+'@sha256:[a-f0-9]{64}',m['images'][name])
 # The exact tag already exists and is verified above; omit unused target_commitish.
 gh('release','create',tag,'--verify-tag','--prerelease','--title','Beszel+ '+version,'--notes-file',str(p/'notes.md'),*(str(p/n) for n in ['traffic.patch','commits.txt','source-manifest.json','SHA256SUMS']))
 print('Published existing verified images and source without rebuilding:',tag)
