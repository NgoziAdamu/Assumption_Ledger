"""Transparent corrective snapshot BEFORE repeating every use of previously unlisted derived inputs."""
from fingerprint_dacomp_batch019 import ROOT,REC,fp
import json,datetime,subprocess,sys,os
from pathlib import Path
inv=json.loads((REC/'019_package_inventory.json').read_text());before=json.loads((REC/'019_input_before.json').read_text());missing={};affected=[]
for r in inv:
 d=json.loads((ROOT/r['full_json']).read_text());paths=[p for p in d['original_files']['paths'] if str(Path(p)) not in before['files']]
 if paths:
  assert r['purpose']!='校准';affected.append(r)
  for p in paths:missing[p]=fp(Path(p))
path=REC/'019_input_supplement_before.json'
if not path.exists():path.write_text(json.dumps(dict(started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reason='原快照遗漏历史派生比较库；在本次所有受影响材料生成及重跑再次执行前补充，不回填或篡改原快照时间。',files=missing,affected_tables=[r['table'] for r in affected]),ensure_ascii=False,indent=2)+'\n')
else:
 old=json.loads(path.read_text());assert old['files']==missing
if 'snapshot-only' in sys.argv:print(len(missing),len(affected));sys.exit()
# Re-read original inputs to generate the evidence packages, not a cached pre-snapshot extraction.
for r in affected:
 p=ROOT/r['full_json'];p.unlink()
env=dict(os.environ);env['PYTHONPATH']=str(ROOT/'data/005_tools');python='/home/katherine/dac/.venv-openhands/bin/python'
with (REC/'019_supplement_packages.log').open('w') as f:subprocess.run([python,'-B','scripts/prepare_dacomp_batch019.py'],env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
# One worker per task; only derived-input-affected tables are repeated.
if '--worker' in sys.argv:raise RuntimeError('Use task drivers below')
from concurrent.futures import ThreadPoolExecutor
def task(n):
 for r in affected:
  if r['task']!=n:continue
  with (REC/('019_supplement_'+r['task']+'_'+r['table']+'.log')).open('w') as f:subprocess.run([python,'-B','scripts/run_dacomp_batch019.py','--table',r['table']],env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
  print(r['task'],r['table'],'repeated after snapshot',flush=True)
with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(task,sorted({r['task'] for r in affected})))
after={p:fp(Path(p)) for p in missing};delta=[p for p in missing if missing[p]!=after[p]];(REC/'019_input_supplement_after.json').write_text(json.dumps(dict(completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=after,changes=delta),ensure_ascii=False,indent=2)+'\n');assert not delta
