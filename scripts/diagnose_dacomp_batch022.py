from annotate_dacomp_batch022 import *
from review_dacomp_batch022 import pkg,inventory
out=[]
for i in [0,2,3,7,9,16,25]:
 p=pkg(i);b=p['differences'];r=inventory()[i];rel=b['actual_schema']+'.'+b['table'];work=WORK/(r['task']+'_'+b['table'])
 with duckdb.connect(str(work/'work.duckdb')) as c:
  c.execute("SET threads=2; SET memory_limit='1500MB'");c.create_function('tolerance_forms',udf_forms,['VARCHAR'],duckdb.struct_type({'l1':'VARCHAR','l2':'VARCHAR','l3':'VARCHAR'}))
  c.execute("ATTACH '"+b['gold_database']+"' AS gold (READ_ONLY)")
  c.execute("ATTACH '"+b['prediction_database']+"' AS retained (READ_ONLY)")
  d=dict(index=i,kind='诊断查询',queries=[])
  def q(label,sql):
   cur=c.execute(sql);d['queries'].append(dict(label=label,sql=sql,columns=[x[0] for x in cur.description],result=cur.fetchall()))
  if i in [0,2]:
   for alias in ['retained','gold']:
    c.execute(f"CREATE OR REPLACE TEMP TABLE {alias}_canonical AS SELECT * REPLACE(array_to_string(list_sort(string_split(merged_into_lead_id, ', ')), ', ') AS merged_into_lead_id) FROM {alias}.{rel}")
   d['order_canonicalization']=compare_sql(c,'retained_canonical','gold_canonical',b)
   d['transformation']="仅对merged_into_lead_id以逗号空格分组、排序；其他列和重复次数原样，键保留。"
  if i==3:q('实际分歧',f'SELECT overall_health_score,primary_recommendation FROM gold.{rel}')
  if i==7:
   q('主支与CTA行数',f"SELECT account_name,count(*) FROM gold.{rel} GROUP BY 1 ORDER BY 2 DESC")
  if i==9:q('三类报告键和payload',f'SELECT report_type,quality_grade,primary_concern,recommended_action,accuracy_score,overall_quality_score,quality_assessment_id FROM gold.{rel}')
  if i==16:q('评分日期和窗口边界',f'SELECT min(analysis_date),max(analysis_date),min(performance_month),max(performance_month),count(*) FROM gold.{rel}')
  if i==25:
   gold=p['gold_SQL_仅供定位差异'][0]['text'];old='try_cast(sr.recorded_date as timestamp)';new="try_strptime(sr.recorded_date, '%Y-%m-%d %H:%M:%S.%f %z')::TIMESTAMP"
   d['gold_parser_diagnostic']={'old':old,'new':new,'occurrences':gold.count(old)}
   # unused CTE source still needs copying from read-only gold
   for ref in set(re.findall(r'\b(?:from|join)\s+((?:staging|intermediate)\.[\w]+)',gold,re.I)):
    c.execute('CREATE SCHEMA IF NOT EXISTS '+ref.split('.')[0]);c.execute(f'CREATE OR REPLACE TABLE {ref} AS SELECT * FROM gold.{ref}')
   c.execute('CREATE OR REPLACE TEMP TABLE repaired_gold AS '+gold.replace(old,new))
   c.execute('CREATE OR REPLACE TEMP TABLE baseline AS '+(work/'baseline.sql').read_text())
   d['gold_parser_diagnostic']['comparison']=compare_sql(c,'baseline','repaired_gold',b)
   c.execute('CREATE OR REPLACE TEMP TABLE repaired_gold_date AS SELECT * REPLACE(CAST(cohort_month AS DATE) AS cohort_month) FROM repaired_gold')
   d['gold_parser_and_contract_date_diagnostic']={'sql':'SELECT * REPLACE(CAST(cohort_month AS DATE) AS cohort_month) FROM repaired_gold','comparison':compare_sql(c,'baseline','repaired_gold_date',b),'purpose':'同时纠正gold解析和契约DATE键类型，只作O诊断，不作为agent单改干预'}
  out.append(d);save(REC/'022_diagnostics.json',out)
