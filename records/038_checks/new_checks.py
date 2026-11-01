"""038: exact single-span patches; original databases READ_ONLY, private tables in memory."""
from pathlib import Path
import sys,json,re,hashlib,datetime
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'scripts'),str(R/'data/005_tools')]
from annotate_dacomp_batch016 import compare_sql,udf_forms
import duckdb
CAT=json.loads((R/'records/038_checks/evidence_catalog.json').read_text());PLAN={}
def record(i):return json.loads((R/f'records/020_reruns_{CAT[i]["object"]}.json').read_text())
def add(i,label,old,new,why,kind='单改重跑'):
 PLAN.setdefault(i,[]).append(dict(label=label,old=old,new=new,why=why,kind=kind))
# Previously masked metrics; each patch starts at original baseline.
for x in record(18)['runs'][1:]:
 if x['label'] in ['calculated_tap_through_rate','cost_per_tap','cost_per_conversion']:
  e=x['edits'][0];add(20,x['label'],e['old'],e['new'],'新识别：campaign_id错误掩盖的单列NULL，不沿用修键后的基线。')
for x in record(23)['runs'][1:]:
 e=x['edits'][0];add(24,x['label'],e['old'],e['new'],'新识别：键值选择掩盖的布尔文本清理策略差异。')
add(24,'conversions_decimal','CAST(TRY_CAST("conversions" AS BIGINT) AS DECIMAL(10,2)) AS conversions','TRY_CAST("conversions" AS DECIMAL(10,2)) AS conversions','移除中途BIGINT舍入，保留契约DECIMAL(10,2)。')
add(31,'app_installs_candidate','CAST(NULL::INTEGER AS INTEGER) AS app_installs','TRY_CAST(mobile_conversion_installs_order_quantity AS INTEGER) AS app_installs','原始库确有安装计数候选列；不能把020的补0当成恢复候选列。')
for col in ['follows','likes','comments','shares']:
 add(30,col+'_invalid_policy',f'TRY_CAST("{col.upper()}" AS INTEGER) AS {col}',f'coalesce(TRY_CAST("{col.upper()}" AS INTEGER),0) AS {col}','补齐被advertiser_id键选择掩盖的无效/缺失数值补0策略；并不将0宣称为唯一正确值。')
for col,typ,alias in [('CTR','DOUBLE','click_through_rate'),('COST_PER_CONVERSION','DECIMAL(18,2)','cost_per_conversion')]:
 add(30,alias+'_invalid_policy',f'TRY_CAST("{col}" AS {typ}) AS {alias}',f'coalesce(TRY_CAST("{col}" AS {typ}),0) AS {alias}','同上；非数值文本的NULL/0处理未被契约定下。')
for i in [10,11]:
 table=CAT[i]['object'].split('impl-006_',1)[1]
 src='intermediate.int_'+table
 add(i,'placeholder_filter','FROM '+src,'FROM '+src+" WHERE platform <> 'placeholder'",'新识别：契约排除placeholder平台；仅增加这一个过滤条件。')
# Isolate only floating representation in the output; compare both sides rounded.
add(34,'clv_presentation',None,'SELECT * REPLACE(round(global_avg_clv,10) AS global_avg_clv) FROM result_baseline','只改输出比较条件中global_avg_clv的浮点呈现；其他列仍L0–L3。','呈现诊断')
(R/'records/038_checks/new_patch_plan.json').write_text(json.dumps(PLAN,ensure_ascii=False,indent=2)+'\n')
def run(i):
 o=CAT[i];d=record(i);b=d['basis'];orig=(R/d['runs'][0]['sql_path']).read_text()
 out=dict(object=o['object'],source=d['source'],basis={k:b[k] for k in ['gold_database','actual_schema','table','comparison_columns','key_columns']},original_databases_read_only=True,private_database=':memory:',baseline_sql_path=d['runs'][0]['sql_path'],baseline_sql_sha256=hashlib.sha256(orig.encode()).hexdigest(),clock_control=d.get('clock_control',[]),runs=[])
 target=R/f'records/038_checks/rerun_{o["object"]}.json'
 if target.exists():out=json.loads(target.read_text())
 done={x['label'] for x in out['runs']}
 with duckdb.connect(':memory:') as c:
  c.execute("SET threads=2;SET memory_limit='2000MB'")
  c.create_function('tolerance_forms',udf_forms,['VARCHAR'],duckdb.struct_type({'l1':'VARCHAR','l2':'VARCHAR','l3':'VARCHAR'}))
  c.execute(f"ATTACH '{d['source']}' AS src (READ_ONLY)");gold='src'
  if d['source']!=b['gold_database']:c.execute(f"ATTACH '{b['gold_database']}' AS gold (READ_ONLY)");gold='gold'
  refs=set(re.findall(r'\b(?:FROM|JOIN)\s+((?:raw|staging|intermediate|marts|mart)\.\w+)',orig,re.I))
  for ref in refs:c.execute(f'CREATE SCHEMA IF NOT EXISTS {ref.split(".")[0]}');c.execute(f'CREATE TABLE {ref} AS SELECT * FROM src.{ref}')
  out['private_copy_tables']=sorted(refs)
  for p in [dict(label='baseline',old=None,new=orig,kind='基线')]+PLAN[i]:
   if p['old'] is not None:assert orig.count(p['old'])==1,(i,p['label'],p['old'])
   sql=p['new'] if p['old'] is None else orig.replace(p['old'],p['new'],1)
   c.execute('SELECT setseed(0.019)');c.execute('CREATE OR REPLACE TABLE result_current AS '+sql)
   if p['label']=='baseline':c.execute('CREATE TABLE result_baseline AS SELECT * FROM result_current')
   ref=gold+'.'+b['actual_schema']+'.'+b['table']
   if p['kind']=='呈现诊断':c.execute('CREATE TABLE gold_presented AS SELECT * REPLACE(round(global_avg_clv,10) AS global_avg_clv) FROM '+ref);ref='gold_presented'
   if p['label'] in done:continue
   r=dict(label=p['label'],kind=p['kind'],why=p.get('why'),edits=[] if p['old'] is None else [dict(old=p['old'],new=p['new'],offset=orig.index(p['old']))],sql=sql,sql_sha256=hashlib.sha256(sql.encode()).hexdigest(),comparison=compare_sql(c,'result_current',ref,b))
   out['runs'].append(r);target.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');x=r['comparison']['levels'][0];print(i,p['label'],x['row_scale'],x['cell_scale'],flush=True)
if __name__=='__main__':
 for i in map(int,sys.argv[1:]):run(i)
