import sys,json,re,hashlib
from pathlib import Path
sys.path[:0]=['scripts','data/005_tools']
import duckdb
from annotate_dacomp_batch016 import compare_sql,udf_forms
C=Path('records/039_checks');cat=json.loads((C/'evidence_catalog.json').read_text())
for i in [16,38]:
 o=cat[i];srcfile=('records/021_reruns_' if i==16 else 'records/021_extra_reruns_')+o['object']+'.json';d=json.load(open(srcfile));b=d['basis'];orig=Path(o['agent_sql']).read_text().strip().rstrip(';')
 for e in d['clock_control']:orig=re.sub(e['pattern'],e['replacement'],orig,flags=re.I)
 if i==16:
  specs=[('transaction_date_source_policy','try_cast(substr(transaction_time, 1, 10) AS DATE) AS transaction_date','try_cast(substr(cast(transaction_date as varchar),1,10) AS DATE) AS transaction_date','transaction_date'),('sku_source_policy','CAST(coalesce(sku_id, product_id, base_plan_id) AS VARCHAR) AS sku_id','CAST(sku_id AS VARCHAR) AS sku_id','sku_id'),('package_source_policy','CAST(base_plan_id AS VARCHAR) AS package_name','CAST(product_id AS VARCHAR) AS package_name','package_name')]
  variants=[('baseline',orig,[])]
  for label,old,new,col in specs:
   assert orig.count(old)==1
   sql='SELECT * FROM ('+orig.replace(old,new)+') projected WHERE '+col+' IS NOT NULL'
   variants.append((label,sql,[{'old':old,'new':new},{'scope':'single column source policy','new':'filter projected '+col+' IS NOT NULL'}]))
  rationale='逐列对比“使用替代候选列保留”与“使用同名/候选主列，不能提供必填值时排除”的来源政策。一个逻辑选择同时对应映射及该列not_null执行；不触碰其他列校验。三者是互相重叠的反事实，不可累加；旧整表替换不用于排序。'
 else:
  expression="(SELECT CASE WHEN avg(epoch(coalesce(si.resolved_at,TIMESTAMPTZ '2025-10-13 00:00:00+00')-si.created_at)/86400.0)<=7 THEN 'Rapid' WHEN avg(epoch(coalesce(si.resolved_at,TIMESTAMPTZ '2025-10-13 00:00:00+00')-si.created_at)/86400.0)<=14 THEN 'Timely' WHEN avg(epoch(coalesce(si.resolved_at,TIMESTAMPTZ '2025-10-13 00:00:00+00')-si.created_at)/86400.0)<=30 THEN 'Standard' ELSE 'Slow' END FROM staging.stg_jira__issue si WHERE si.assignee_user_id=u.user_id) response_pattern_type"
  old="'Slow' response_pattern_type";assert orig.count(old)==1
  variants=[('baseline',orig,[])]+[(label,orig.replace(old,new),[{'old':old,'new':new}]) for label,new in [('response_label_only',"'Slow Responder' response_pattern_type"),('response_calculation_only',expression),('response_calculation_and_label',expression.replace("'Rapid'","'Rapid Responder'").replace("'Timely'","'Timely Responder'").replace("'Standard'","'Standard Responder'").replace("'Slow'","'Slow Responder'"))]]
  rationale='拆开同一输出的计算缺口（固定Slow）与gold额外Responder标签。仅组合用于诊断，不作为单点排序。'
 out={'object':o['object'],'source_record':srcfile,'source':d['source'],'original_databases_read_only':True,'private_database':':memory:','clock_control':d['clock_control'],'rationale':rationale,'runs':[]}
 with duckdb.connect(':memory:') as c:
  c.execute("SET threads=1; SET memory_limit='1500MB'");c.create_function('tolerance_forms',udf_forms,['VARCHAR'],duckdb.struct_type({'l1':'VARCHAR','l2':'VARCHAR','l3':'VARCHAR'}));c.execute("ATTACH '"+d['source']+"' AS src (READ_ONLY)");ga='src'
  if d['source']!=b['gold_database']:c.execute("ATTACH '"+b['gold_database']+"' AS gold (READ_ONLY)");ga='gold'
  refs=set(re.findall(r'\b(?:FROM|JOIN)\s+((?:raw|staging|intermediate|marts)\.[\w]+)',' '.join(x[1] for x in variants),re.I))
  for ref in refs:c.execute('CREATE SCHEMA IF NOT EXISTS '+ref.split('.')[0]);c.execute('CREATE TABLE '+ref+' AS SELECT * FROM src.'+ref)
  for label,sql,edits in variants:
   c.execute('CREATE OR REPLACE TABLE candidate AS '+sql);comparison=compare_sql(c,'candidate',ga+'.'+b['actual_schema']+'.'+b['table'],b)
   if label=='baseline':assert comparison==d['runs'][0]['comparison']
   out['runs'].append({'label':label,'sql':sql,'edits':edits,'sql_sha256':hashlib.sha256(sql.encode()).hexdigest(),'comparison':comparison});z=comparison['levels'][0];print(o['object'],label,z['row_scale'],z['cell_scale'],flush=True)
 (C/('supplement_'+o['object']+'.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
