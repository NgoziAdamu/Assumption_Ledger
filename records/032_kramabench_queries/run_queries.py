"""Run the nine local queries, capturing complete stdout/stderr without truncation."""
from pathlib import Path
import contextlib,hashlib,importlib.metadata,json,os,platform,runpy,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(OUT))
os.environ['PROJ_NETWORK']='OFF'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write_new(p,obj):
    with p.open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')

sources=sorted(set([p for p in (ROOT/'data/kramabench').rglob('*') if p.is_file()]+[
 ROOT/p for p in subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0') if p]))
before={str(p.relative_to(ROOT)):digest(p) for p in sources}
write_new(OUT/'source_hashes_before.json',before)
manifest=[];results={}
for p in sorted(OUT.glob('[0-9][0-9]_*.py')):
    start=time.time();stdout=p.with_suffix('.stdout.txt');stderr=p.with_suffix('.stderr.txt')
    with stdout.open('x') as o,stderr.open('x') as e,contextlib.redirect_stdout(o),contextlib.redirect_stderr(e):
        scope=runpy.run_path(str(p),run_name='__main__')
    results[p.stem]=scope['RESULT']
    manifest.append({'script':p.name,'stdout':stdout.name,'stderr':stderr.name,'elapsed_seconds':time.time()-start,
       'stdout_bytes':stdout.stat().st_size,'stderr_bytes':stderr.stat().st_size,'script_sha256':digest(p),'stdout_sha256':digest(stdout)})
    print(p.name,'OK',flush=True)
changed=[str(p.relative_to(ROOT)) for p in sources if digest(p)!=before[str(p.relative_to(ROOT))]]
assert not changed,changed
write_new(OUT/'results.json',results)
write_new(OUT/'run_manifest.json',{'python':sys.executable,'python_version':platform.python_version(),
 'dependencies':{n:importlib.metadata.version(n) for n in ['pandas','numpy','openpyxl','pyproj']},
 'command':'PYTHONDONTWRITEBYTECODE=1 /home/katherine/dac/.venv/bin/python records/032_kramabench_queries/run_queries.py',
 'queries':manifest,'source_files_checked':len(sources),'sources_changed':changed,
 'query_network_blocked_by_audit_hook':True,'PROJ_NETWORK':'OFF'})
