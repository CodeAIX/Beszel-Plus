#!/usr/bin/env python3
"""Disposable maintenance test; no published releases or application changes."""
import json,os,subprocess
from pathlib import Path
repo=os.environ['GITHUB_REPOSITORY'];suffix=os.environ['GITHUB_RUN_ID']+'-'+os.environ['GITHUB_RUN_ATTEMPT']
branch='plus/permission-check-'+suffix;tag='plus-permission-check-'+suffix
release_id=None
created=[]
def run(*args):return subprocess.check_output(args,text=True).strip()
def gh(*args):return run('gh',*args)
try:
 run('git','config','user.name','beszel-plus[bot]');run('git','config','user.email','beszel-plus[bot]@users.noreply.github.com')
 base=run('git','rev-parse','HEAD')
 run('git','checkout','-b',branch+'-input')
 p=Path('.github/workflows/plus-ci.yml');p.write_text(p.read_text()+'\n# Disposable simulated upstream workflow change\n')
 run('git','add',str(p));run('git','commit','-m','test: simulated upstream workflow change')
 upstream=run('git','rev-parse','HEAD');run('git','checkout','-b',branch,base)
 run('git','merge','--no-ff','--no-commit',upstream)
 run('git','restore','--source='+base,'--staged','--worktree','--','.github/workflows')
 run('git','commit','-m','test: preserve reviewed fork workflows during merge')
 sha=run('git','rev-parse','HEAD')
 run('git','merge-base','--is-ancestor',upstream,sha)
 run('git','diff','--exit-code',base,sha,'--','.github/workflows')
 run('git','push','origin','HEAD:refs/heads/'+branch);created.append('heads/'+branch)
 gh('api','--method','POST',f'repos/{repo}/git/refs','-f','ref=refs/tags/'+tag,'-f','sha='+sha);created.append('tags/'+tag)
 response=json.loads(gh('api','--method','POST',f'repos/{repo}/releases','-f','tag_name='+tag,'-f','name=Disposable maintenance permission check','-F','draft=true','-F','prerelease=true'))
 release_id=response['id']
 print('GITHUB_TOKEN quarantined merge push, immutable tag reservation and draft release all passed')
finally:
 if release_id:gh('api','--method','DELETE',f'repos/{repo}/releases/{release_id}')
 for ref in reversed(created):gh('api','--method','DELETE',f'repos/{repo}/git/refs/{ref}')
