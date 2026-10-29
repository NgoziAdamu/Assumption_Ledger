"""Snapshot inputs before task017 annotation/query/rerun; stdlib only."""
from pathlib import Path
import hashlib,json,datetime,sys
ROOT=Path(__file__).resolve().parents[1];REC=ROOT/'records'
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def fp(p):
 s=p.stat();h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 t=p.stat();assert (s.st_size,s.st_mtime_ns)==(t.st_size,t.st_mtime_ns),str(p)
 return {'size':s.st_size,'mtime_ns':s.st_mtime_ns,'sha256':h.hexdigest()}
def main():
 after='after' in sys.argv;started=stamp()
 if after:
  before=json.loads((REC/'017_input_before.json').read_text());paths=[Path(p) for p in before['files']]
 else:
  previous=json.loads((REC/'016_input_after.json').read_text());paths={Path(p) for p in previous['files']}
  for n in range(4,17):
   paths.update(p for p in REC.rglob(f'{n:03}_*') if p.is_file());paths.update((ROOT/'notes').glob(f'{n:03}_*'))
  paths.update(p for p in (ROOT/'docs').rglob('*') if p.is_file());paths.update(p for p in (ROOT/'scripts').glob('*.py') if '017' not in p.name);paths.add(ROOT/'AGENTS.md')
  for n in range(21,31):
   p=json.loads(next((REC/'012_packages').glob(f'012_impl-{n:03}_*.json')).read_text());paths.update(Path(p['differences'][k]) for k in ['prediction_database','gold_database'])
   for key in ['agent_final_SQL','gold_SQL_仅供定位差异']:paths.update(Path(x['path']) for x in p[key])
   paths.update((ROOT/f'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-{n:03}/agent/.events/sessions').glob('*/events/*.json'))
  paths=sorted(paths)
 missing=[str(p) for p in paths if not p.exists()];assert not [p for p in missing if not p.startswith('/mnt/c/')],missing
 files={str(p):fp(p) for p in paths if p.exists()};out={'started_utc':started,'completed_utc':stamp(),'files':files,'missing_external_prior_paths':missing}
 if after:
  out['changes']=[p for p,x in before['files'].items() if files.get(p)!=x];assert not out['changes'],out['changes']
 else:out['differences_from_016_after']=[p for p,x in previous['files'].items() if p in files and files[p]!=x]
 dest=REC/f'017_input_{"after" if after else "before"}.json';dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('completed',dest,len(files),'files',out['completed_utc'],flush=True)
if __name__=='__main__':main()
