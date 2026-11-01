"""040 isolated single-change diagnostics; original DBs READ_ONLY, results in memory."""
from pathlib import Path
import sys,json,re,hashlib,datetime,os
sys.dont_write_bytecode=True
ROOT=Path.cwd();sys.path.insert(0,str(ROOT/'scripts'))
from annotate_dacomp_batch016 import compare_sql,udf_forms
import duckdb
C=ROOT/'records/040_checks'
def load(p):return json.loads(Path(p).read_text())
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for buf in iter(lambda:f.read(8*1024*1024),b''):h.update(buf)
 return h.hexdigest()
rs=load(ROOT/'records/022_decisions.json');plans=load(ROOT/'records/022_patch_plan.json');cases=load(ROOT/'records/013_cases.json')
for i in [21,22,24,25]:
 if len(sys.argv)>1 and str(i) not in sys.argv[1:]:continue
 r=rs[i];oid=r['task']+'_'+r['table'];pkg=load(r['full_json']);b=pkg['differences'];source=cases[int(r['task'][-3:])-1]['agent_database'] if r['layer']=='staging' else b['gold_database'];oldrun=load(ROOT/f'records/022_reruns_{oid}.json');orig=Path(pkg['agent_final_SQL'][0]['path']).read_text();sql=orig
 for e in oldrun.get('clock_control',[]):sql=re.sub(e['pattern'],e['replacement'],sql,flags=re.I)
 if i in [21,22,24]:
  patches=[('restore_'+re.search(r'AS (\w+)$',a[0]).group(1),[a]) for a in plans[i]['patches'][0]['edits']]
 else:patches=[('cohort_month_gold_type',[["date_trunc('month', min(recorded_at))::DATE AS cohort_month","date_trunc('month', min(recorded_at))::TIMESTAMP AS cohort_month"]])]
 if i==24:
  patches=[(label,[[a,b.replace('entitytitle AS entity_name','entityid AS entity_name')] for a,b in edits]) for label,edits in patches]
 initial=cases[int(r['task'][-3:])-1]['initial_database'] if r['task']=='impl-013' else None
 paths=sorted(set([source,b['gold_database']]+([initial] if initial else [])));before={p:sha(p) for p in paths};out={'object':oid,'index':i,'source':source,'gold':b['gold_database'],'original_databases_read_only':True,'private_execution':'DuckDB :memory:','database_hashes_before':before,'clock_control':oldrun.get('clock_control',[]),'runs':[]}
 with duckdb.connect(':memory:') as c:
  c.execute("SET threads=2; SET memory_limit='1500MB'");c.create_function('tolerance_forms',udf_forms,['VARCHAR'],duckdb.struct_type({'l1':'VARCHAR','l2':'VARCHAR','l3':'VARCHAR'}))
  c.execute("ATTACH '"+source.replace("'","''")+"' AS src (READ_ONLY)")
  if initial:c.execute("ATTACH '"+initial.replace("'","''")+"' AS source (READ_ONLY)")
  gold='src'
  if source!=b['gold_database']:c.execute("ATTACH '"+b['gold_database'].replace("'","''")+"' AS gold (READ_ONLY)");gold='gold'
  refs=sorted(set(re.findall(r'\b(?:FROM|JOIN)\s+((?:raw|staging|intermediate|marts|utils)\.[a-zA-Z_0-9]+)',sql,re.I)));out['private_copy_tables']=refs
  for ref in refs:c.execute('CREATE SCHEMA IF NOT EXISTS '+ref.split('.')[0]);c.execute(f'CREATE TABLE {ref} AS SELECT * FROM src.{ref}')
  rel=b['actual_schema']+'.'+b['table'];c.execute('CREATE SCHEMA IF NOT EXISTS '+b['actual_schema'])
  for label,edits in [('baseline',[])]+patches:
   mod=sql;details=[]
   for old,new in edits:
    assert mod.count(old)==1;(details.append({'old':old,'new':new,'offset':mod.index(old)}));mod=mod.replace(old,new,1)
   c.execute('CREATE OR REPLACE TABLE '+rel+' AS '+mod.strip().rstrip(';'))
   result=compare_sql(c,rel,gold+'.'+rel,b)
   out['runs'].append({'label':label,'edits':details,'sql':mod,'sql_sha256':hashlib.sha256(mod.encode()).hexdigest(),'comparison':result})
   print(i,label,[(x['row_scale'],x['cell_scale']) for x in result['levels']],flush=True)
 out['database_hashes_after']={p:sha(p) for p in paths};assert before==out['database_hashes_after']
 out['baseline_matches_022']=out['runs'][0]['comparison']==oldrun['runs'][0]['comparison'];assert out['baseline_matches_022']
 save(C/f'supplement_{oid}.json',out)
