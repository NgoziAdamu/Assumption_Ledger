"""042 limited supplements; READ_ONLY originals, private in-memory execution."""
from pathlib import Path
import sys,json,re,hashlib,copy
sys.dont_write_bytecode=True
ROOT=Path.cwd();sys.path.insert(0,str(ROOT/'scripts'))
from annotate_dacomp_batch016 import compare_sql,udf_forms
import duckdb
C=ROOT/'records/042_checks'
def load(p):return json.loads(Path(p).read_text())
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
cat={x['object_id']:x for x in load(C/'evidence_catalog.json')};cases=load('records/013_cases.json')
position_old=load('records/023_supplement_reruns_impl-016_workday__position_overview.json')['runs'][1]['edits'][0]
plans={
 'impl-016_workday__position_overview':[
 ('similar_count_only',[('count(DISTINCT b.position_id) similar_positions_in_department','count(*) similar_positions_in_department')]),
 ('similar_organization_only',[(position_old['old'],position_old['new'].replace('count(*) similar_positions_in_department','count(DISTINCT b.position_id) similar_positions_in_department'))])],
 'impl-018_stg_salesforce__lead':[
 ('revenue_precision', [('try_cast(annual_revenue as DECIMAL(18,3))','try_cast(annual_revenue as DECIMAL(18,2))')]),
 ('revenue_range_only',[('try_cast(annual_revenue as DECIMAL(18,3))','case when annual_revenue<0 or annual_revenue>999999999999.99 then null else try_cast(annual_revenue as DECIMAL(18,3)) end')])],
 'impl-020_stg_intercom__conversation_contact_history':[
 ('mapping_combination',[('try_cast(conversation_id as varchar) as contact_id','contact_id as contact_id'),('try_cast(contact_id as bigint) as conversation_id','conversation_id as conversation_id')])]
}
for oid,patches in plans.items():
 dest=C/f'supplement_{oid}.json'
 if dest.exists():continue
 x=cat[oid];pkg=load(x['full_json']);b=pkg['differences'];oldrun=load(f'records/023_reruns_{oid}.json');source=oldrun['source'];orig=Path(x['agent_sql']).read_text();sql=orig
 for e in oldrun['clock_control']:sql=re.sub(e['pattern'],e['replacement'],sql,flags=re.I)
 paths=sorted(set([source,b['gold_database']]));before={p:sha(p) for p in paths};out={'object':oid,'basis':b,'source':source,'gold':b['gold_database'],'original_databases_read_only':True,'private_execution':'DuckDB :memory:','database_hashes_before':before,'clock_control':oldrun['clock_control'],'runs':[]}
 with duckdb.connect(':memory:') as c:
  c.execute("SET threads=2; SET memory_limit='1500MB'");c.create_function('tolerance_forms',udf_forms,['VARCHAR'],duckdb.struct_type({'l1':'VARCHAR','l2':'VARCHAR','l3':'VARCHAR'}))
  c.execute("ATTACH '"+source+"' AS src (READ_ONLY)");c.execute("ATTACH '"+b['gold_database']+"' AS gold (READ_ONLY)")
  refs=sorted(set(re.findall(r'\b(?:FROM|JOIN)\s+((?:raw|staging|intermediate|marts|mart)\.[a-zA-Z_0-9]+)',sql+'\n'+'\n'.join(new for _,edits in patches for _,new in edits),re.I)));out['private_copy_tables']=refs
  for ref in refs:c.execute('CREATE SCHEMA IF NOT EXISTS '+ref.split('.')[0]);c.execute(f'CREATE TABLE {ref} AS SELECT * FROM src.{ref}')
  rel=b['actual_schema']+'.'+b['table'];c.execute('CREATE SCHEMA IF NOT EXISTS '+b['actual_schema'])
  for label,edits in [('baseline',[])]+patches:
   mod=sql;details=[]
   for old,new in edits:
    assert mod.count(old)==1;details.append({'old':old,'new':new,'offset':mod.index(old)});mod=mod.replace(old,new,1)
   c.execute('CREATE OR REPLACE TABLE '+rel+' AS '+mod.strip().rstrip(';'));result=compare_sql(c,rel,'gold.'+rel,b)
   out['runs'].append({'label':label,'edits':details,'sql':mod,'sql_sha256':hashlib.sha256(mod.encode()).hexdigest(),'comparison':result});print(oid,label,[(a['row_scale'],a['cell_scale']) for a in result['levels']],flush=True)
 out['database_hashes_after']={p:sha(p) for p in paths};assert before==out['database_hashes_after'];out['baseline_matches_023']=out['runs'][0]['comparison']==oldrun['runs'][0]['comparison'];assert out['baseline_matches_023'];save(dest,out)
# One verification query only, on agent raw, for the newly identified history dedup premise.
oid='impl-018_stg_salesforce__contact_history';db=cases[17]['agent_database'];before=sha(db)
sql="""WITH versions AS (SELECT id, count(*) n, count(DISTINCT md5(concat_ws('|',coalesce(cast(id AS VARCHAR),''),coalesce(cast(_fivetran_start AS VARCHAR),''),coalesce(cast(_fivetran_end AS VARCHAR),'')))) versions FROM raw.contact_history GROUP BY id) SELECT sum(n) total_rows,count(*) distinct_ids,count(*) FILTER(WHERE n>1) repeated_ids,sum(n-1) removed_by_id,count(*) FILTER(WHERE versions>1) multiversion_ids,max(versions) max_versions FROM versions"""
with duckdb.connect(db,read_only=True) as c:
 cur=c.execute(sql);q={'object':oid,'kind':'核实查询','database':db,'sql':sql,'columns':[a[0] for a in cur.description],'rows':cur.fetchall(),'original_database_read_only':True,'database_hash_before':before}
q['database_hash_after']=sha(db);assert q['database_hash_after']==before;save(C/'new_verification_queries.json',[q]);print('history query',q['rows'],flush=True)
# Diagnostic: mask exactly one non-key column on BOTH sides, keeping the same comparison width.
# This attributes permitted tie / gold-spec discrepancies; it is not an agent SQL repair.
plans=[('impl-015_quickbooks__general_ledger',['running_balance','running_converted_balance'],True),('impl-018_salesforce__team_performance',['top_win_rate_performer'],False),('impl-021_int_klaviyo__events',['inter_event_minutes','session_seq'],True)]
for oid,columns,private in plans:
 dest=C/f'diagnostic_{oid}.json'
 if dest.exists():continue
 d=load(f'records/023_reruns_{oid}.json');b=d['basis'];pred=str(ROOT/'data/023_work'/oid/'work.duckdb') if private else b['prediction_database'];gold=b['gold_database'];rel=b['actual_schema']+'.'+b['table'];paths=[pred,gold];before={p:sha(p) for p in paths};out={'object':oid,'mode':'diagnostic_mask_one_output_column_both_sides','not_agent_sql_repair':True,'source':pred,'gold':gold,'original_databases_read_only':True,'database_hashes_before':before,'runs':[]}
 with duckdb.connect(':memory:') as c:
  c.execute("SET threads=2; SET memory_limit='1500MB'");c.create_function('tolerance_forms',udf_forms,['VARCHAR'],duckdb.struct_type({'l1':'VARCHAR','l2':'VARCHAR','l3':'VARCHAR'}));c.execute("ATTACH '"+pred+"' AS pred (READ_ONLY)");c.execute("ATTACH '"+gold+"' AS gold (READ_ONLY)")
  for col in [None]+columns:
   psql='SELECT *'+(' REPLACE (NULL AS "'+col+'")' if col else '')+' FROM pred.'+rel;gsql='SELECT *'+(' REPLACE (NULL AS "'+col+'")' if col else '')+' FROM gold.'+rel
   c.execute('CREATE OR REPLACE TABLE pdiag AS '+psql);c.execute('CREATE OR REPLACE TABLE gdiag AS '+gsql);res=compare_sql(c,'pdiag','gdiag',b)
   out['runs'].append({'label':'baseline' if col is None else 'mask_'+col,'column':col,'prediction_sql':psql,'gold_sql':gsql,'comparison':res});print(oid,col,[(a['row_scale'],a['cell_scale']) for a in res['levels']],flush=True)
 out['database_hashes_after']={p:sha(p) for p in paths};assert before==out['database_hashes_after'];out['baseline_matches_023']=out['runs'][0]['comparison']==d['runs'][0]['comparison'];assert out['baseline_matches_023'];save(dest,out)
