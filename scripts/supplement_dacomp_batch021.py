from annotate_dacomp_batch021 import *
from review_dacomp_batch021 import pkg,rows
out=[]
def q(i,sql,kind='诊断',side='gold'):
 d=pkg(i);case=json.loads((REC/'015_cases.json').read_text())[int(rows[i]['task'][-3:])-1];path=case[side+'_database']
 with duckdb.connect(path,read_only=True) as c:
  c.execute("SET TimeZone='UTC'");r=dict(index=i,kind=kind,database=path,sql=sql)
  try:
   cur=c.execute(sql);r.update(columns=[x[0] for x in cur.description],result=cur.fetchall())
  except Exception as e:r['error']=str(e)
  out.append(r);print(i,r.get('result',r.get('error')))
q(2,"SELECT typeof(date_day),min(date_day)::varchar,max(date_day)::varchar FROM mart.asana__daily_metrics GROUP BY ALL")
q(7,"SELECT count(*) n,count(*) FILTER(WHERE due_on IS DISTINCT FROM due_at) due_choices_differ,count(*) FILTER(WHERE due_on IS NOT NULL) due_on_present,count(*) FILTER(WHERE due_at IS NOT NULL) due_at_present FROM raw.task_data",'核实','agent')
q(7,"SELECT typeof(min(due_date)),typeof(min(start_date)) FROM staging.stg_asana__task")
q(4,"SELECT min(date_trunc('hour',t.created_at)+g.total_lifecycle_hours*interval '1 hour')::varchar inferred_hour_min,max(date_trunc('hour',t.created_at)+g.total_lifecycle_hours*interval '1 hour')::varchar inferred_hour_max FROM mart.asana__task_lifecycle_analysis g JOIN staging.stg_asana__task t ON g.task_id=t.task_id WHERE t.completed_at IS NULL")
q(25,"SELECT count(*) n,count(*) FILTER(WHERE try_strptime(substr(created_at,1,19),'%Y-%m-%d %H:%M:%S') IS NOT NULL) created_prefix_parseable,count(*) FILTER(WHERE try_strptime(substr(updated_at,1,19),'%Y-%m-%d %H:%M:%S') IS NOT NULL) updated_prefix_parseable FROM raw.owner_data",'核实','agent')
# preserve failed and successful verification attempts, only retry parser alias failures
for r in json.loads((REC/'021_queries.json').read_text()):
 if r.get('error'):
  sql=r['sql'].replace("' source,count", "' source_name,count")
  q(r['index'],sql,'核实','agent')
save(REC/'021_supplement_queries.json',out)
