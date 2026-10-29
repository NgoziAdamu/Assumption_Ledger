"""Hash inputs without interpreting annotation contents; before/after immutable-input audit."""
from pathlib import Path
import hashlib,json,datetime,sys,subprocess
ROOT=Path(__file__).resolve().parents[1]; REC=ROOT/'records'
def fp(p):
 s=p.stat(); h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
 assert (s.st_size,s.st_mtime_ns)==(p.stat().st_size,p.stat().st_mtime_ns)
 return dict(size=s.st_size,mtime_ns=s.st_mtime_ns,sha256=h.hexdigest())
def main():
 after='after' in sys.argv; start=datetime.datetime.now(datetime.timezone.utc).isoformat()
 if after: before=json.loads((REC/'020_input_before.json').read_text()); paths=[Path(p) for p in before['files']]
 else:
  paths={ROOT/p for p in subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines()}
  # Fingerprint manifests contain paths and hashes only, never annotation labels.
  for p in REC.glob('*_input_before.json'):
   d=json.loads(p.read_text()); paths.update(Path(x) for x in d.get('files',{}) if Path(x).exists())
  for case in json.loads((REC/'013_cases.json').read_text()):
   if case['task'] not in [f'impl-{i:03}' for i in [2,6,7,25]]: continue
   for k in ['initial_database','agent_database']:paths.add(Path(case[k]))
   paths.update(Path(case['trace_directory']).rglob('*.json'));paths.update(Path(case['agent_directory']).rglob('*.sql'))
 files={str(p):fp(p) for p in sorted(paths) if p.is_file()}
 out=dict(started_utc=start,completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=files)
 if after:out['changes']=[p for p,x in before['files'].items() if files.get(p)!=x]
 (REC/f'020_input_{"after" if after else "before"}.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 print(len(files),out.get('changes',[]),flush=True)
if __name__=='__main__':main()
