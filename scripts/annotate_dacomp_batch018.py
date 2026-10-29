"""Task018 evidence harness: validated 016 comparator, isolated private work directory."""
from annotate_dacomp_batch016 import ROOT,REC,fp,save,package,compare_sql,udf_forms
from pathlib import Path
import duckdb,json,re,sys,datetime
WORK=ROOT/'data/018_work'
assert (REC/'018_input_before.json').exists(), 'Complete fingerprint snapshot before any execution'
WORK.mkdir(exist_ok=True)
def rerun(n,patches,clock=None):
 pkg=package(n);b=pkg['differences'];case=json.loads((REC/'013_cases.json').read_text())[n-1];source=case['agent_database'] if b['actual_schema']=='staging' else b['gold_database'];orig=Path(pkg['agent_final_SQL'][0]['path']).read_text();sql=orig
 clock_edits=[]
 if clock:
  for pat,new in [(r'\bcurrent_timestamp\b',f"TIMESTAMPTZ '{clock}'"),(r'\bcurrent_date\b',f"DATE '{clock[:10]}'")]:
   sql,k=re.subn(pat,new,sql,flags=re.I);clock_edits.append({'pattern':pat,'replacement':new,'count':k})
 work=WORK/f'impl-{n:03}';work.mkdir(exist_ok=True);out={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'task':f'impl-{n:03}','basis':b,'source':source,'clock_control':clock_edits,'runs':[]}
 with duckdb.connect(str(work/'work.duckdb')) as c:
  c.execute("SET threads=2; SET memory_limit='1500MB'");c.create_function('tolerance_forms',udf_forms,['VARCHAR'],duckdb.struct_type({'l1':'VARCHAR','l2':'VARCHAR','l3':'VARCHAR'}))
  for alias,path in [('src',source),('gold',b['gold_database']),('retained',b['prediction_database'])]:
   # same path aliases are allowed if already attached: use original alias in refs instead.
   existing=next((a for a,p in out.get('attached',[]) if p==path),None)
   if not existing:c.execute("ATTACH '"+path+f"' AS {alias} (READ_ONLY)");out.setdefault('attached',[]).append((alias,path))
   out[alias+'_alias']=existing or alias
  refs=set(re.findall(r'\b(?:FROM|JOIN)\s+((?:raw|staging|intermediate|marts|mart)\.[a-zA-Z_0-9]+)',sql,re.I));out['private_copy_tables']=sorted(refs)
  for ref in sorted(refs):
   sch=ref.split('.')[0];c.execute(f'CREATE SCHEMA IF NOT EXISTS {sch}');c.execute(f'CREATE OR REPLACE TABLE {ref} AS SELECT * FROM {out["src_alias"]}.{ref}')
  rel=b['actual_schema']+'.'+b['table'];c.execute(f'CREATE SCHEMA IF NOT EXISTS {b["actual_schema"]}')
  out['retained']=compare_sql(c,out['retained_alias']+'.'+rel,out['gold_alias']+'.'+rel,b)
  for name,edits in [('baseline',[])]+patches:
   modified=sql;detail=[]
   for old,new in edits:
    assert modified.count(old)==1,(n,name,old,modified.count(old));detail.append({'old':old,'new':new,'offset':modified.index(old)});modified=modified.replace(old,new,1)
   p=work/f'{name}.sql';p.write_text(modified);trial={'label':name,'edits':detail,'sql_path':str(p.relative_to(ROOT)),'sql_sha256':fp(p)['sha256']}
   try:
    c.execute(f'CREATE OR REPLACE TABLE {rel} AS '+modified.strip().rstrip(';'));trial['comparison']=compare_sql(c,rel,out['gold_alias']+'.'+rel,b)
   except Exception as e:trial['error']=str(e)
   out['runs'].append(trial);save(REC/f'018_reruns_impl-{n:03}.json',out);print(n,name,'done',trial.get('error',''),flush=True)
 save(REC/f'018_reruns_impl-{n:03}.json',out)
