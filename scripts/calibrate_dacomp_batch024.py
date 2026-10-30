"""Blind calibration uses only 012/013 packages, original SQL/data and trace."""
from annotate_dacomp_batch024 import *
import sqlglot
from sqlglot import exp
queries=[]
def q(n,label,sql,gold=False):
 p=package(n);case=json.loads((REC/'013_cases.json').read_text())[n-1];db=p['differences']['gold_database'] if gold else case['agent_database']
 with duckdb.connect(db,read_only=True) as c:
  r=c.execute(sql);queries.append(dict(task=case['task'],kind='诊断' if gold else '核实',label=label,sql=sql,columns=[x[0] for x in r.description],rows=r.fetchall(),database=db))
q(6,'Reddit 原始列',"SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name='reddit_ads_campaign_report_data' ORDER BY ordinal_position")
q(6,'候选指标可用性',"SELECT count(*) n,count(spend) spend_n,count(video_started) video_n,count(comment_upvotes) up_n,count(comment_downvotes) down_n,count(viewer_comments) comments_n,count(try_cast(ctr AS DOUBLE)) ctr_numeric,count(try_cast(cpc AS DOUBLE)) cpc_numeric,count(try_cast(ecpm AS DOUBLE)) ecpm_numeric,count(*) FILTER(WHERE date IS NULL OR campaign_id IS NULL) missing_keys FROM raw.reddit_ads_campaign_report_data")
p=package(6);a=p['agent_final_SQL'][0]['text'];g=p['gold_SQL_仅供定位差异'][0]['text'];gt=sqlglot.parse_one(g,read='duckdb');gm={e.alias_or_name:e.this.sql(dialect='duckdb') for e in gt.expressions if isinstance(e,exp.Alias)}
patches=[]
for line in a.splitlines():
 if ' AS ' not in line:continue
 col=line.rsplit(' AS ',1)[-1].strip().strip(',');old=line.strip().rstrip(',')
 if col not in gm or col in ['platform','campaign_id','date_day','account_id','impressions','clicks','_dbt_loaded_at']:continue
 patches.append((col,[(old,gm[col]+' AS '+col)]))
rerun(6,patches,clock='2025-10-12 00:00:00+00')
p=package(16);a=p['agent_final_SQL'][0]['text'];g=p['gold_SQL_仅供定位差异'][0]['text'];patches=[]
q(16,'agent 可见零活动分母',"SELECT count(*) n,count(*) FILTER(WHERE effective_end IS NULL) active FROM staging.stg_workday__worker_position_organization")
q(16,'gold 固定时钟',"SELECT min(analysis_timestamp),max(analysis_timestamp) FROM mart.workday__organization_overview",True)
clock=str(queries[-1]['rows'][0][0])
for col in ['position_fill_rate','annual_turnover_rate','management_ratio','high_risk_employee_percentage']:
 old=next(l.strip().split(','+col)[0] for l in []) if False else None
 # explicit full expressions, never broad repeated textual replacement
 expr={'position_fill_rate':'round(coalesce(current_active_employees,0)*100.0/NULLIF(total_positions,0),2)', 'annual_turnover_rate':'round(coalesce(departures_last_year,0)*100.0/NULLIF(current_active_employees,0),2)', 'management_ratio':'round((coalesce(management_role_employees,0)+coalesce(director_role_employees,0))*100.0/NULLIF(current_active_employees,0),2)', 'high_risk_employee_percentage':'round(coalesce(high_risk_employees,0)*100.0/NULLIF(current_active_employees,0),2)'}[col]
 patches.append((col,[(expr,'coalesce('+expr+',0)')]))
for col,mp in [('organization_maturity_level',{'New':'New Organization (<1 year)','Young':'Young Organization (1-3 years)','Mature':'Mature Organization (3-10 years)','Legacy':'Legacy Organization (10+ years)'}),('organization_size_category',{'Empty':'Empty Organization','Micro':'Micro Team','Small':'Small Team','Medium':'Medium Team','Large':'Large Team','Enterprise':'Enterprise Unit'})]:
 old=next(l for l in a.splitlines() if l.endswith(col+','));new=old
 for x,y in mp.items():new=new.replace("'"+x+"'","'"+y+"'")
 patches.append((col,[(old,new)]))
# One join block controls assignment multiplicity and role counting; test them separately.
old='FROM rel GROUP BY organization_id,source_relation'
new='FROM (SELECT w.* FROM rel w LEFT JOIN staging.stg_workday__organization_role_worker ow ON w.worker_id=ow.organization_worker_code AND w.source_relation=ow.source_relation LEFT JOIN staging.stg_workday__organization_role r ON ow.role_id=r.organization_role_id AND ow.source_relation=r.source_relation AND w.organization_id=r.organization_id) rel GROUP BY organization_id,source_relation'
patches.append(('assignment_join',[(old,new)]))
old=a.split('), roles AS (\n')[1].split('\n), perf AS')[0]
new=" SELECT w.organization_id,w.source_relation,count(DISTINCT ow.role_id) unique_organization_roles,count(DISTINCT w.worker_id) FILTER(WHERE r.organization_role_code LIKE '%Manager%') management_role_employees,count(DISTINCT w.worker_id) FILTER(WHERE r.organization_role_code LIKE '%Director%') director_role_employees,count(DISTINCT w.worker_id) FILTER(WHERE r.organization_role_code LIKE '%Lead%') lead_role_employees FROM staging.stg_workday__worker_position_organization w LEFT JOIN staging.stg_workday__organization_role_worker ow ON w.worker_id=ow.organization_worker_code AND w.source_relation=ow.source_relation LEFT JOIN staging.stg_workday__organization_role r ON ow.role_id=r.organization_role_id AND ow.source_relation=r.source_relation AND w.organization_id=r.organization_id GROUP BY w.organization_id,w.source_relation"
patches.append(('roles_join',[(old,new)]))
# Distinct score CASE locations, each independently intervened.
for label,old,new in [
('score_turnover',"CASE WHEN departures_last_year=0 THEN 25 WHEN annual_turnover_rate<=10 THEN 25 WHEN annual_turnover_rate<=20 THEN 20 WHEN annual_turnover_rate<=30 THEN 15 WHEN annual_turnover_rate<=40 THEN 10 ELSE 5 END","CASE WHEN coalesce(departures_last_year,0)=0 AND coalesce(current_active_employees,0)>0 THEN 25 WHEN annual_turnover_rate<=10 THEN 20 WHEN annual_turnover_rate<=20 THEN 15 WHEN annual_turnover_rate<=30 THEN 10 ELSE 5 END"),
('score_efficiency','CASE WHEN position_fill_rate>=90 THEN 15 WHEN position_fill_rate>=75 THEN 12 WHEN position_fill_rate>=60 THEN 9 ELSE 6 END','CASE WHEN position_fill_rate>=90 THEN 15 WHEN position_fill_rate>=80 THEN 12 WHEN position_fill_rate>=70 THEN 9 ELSE 6 END'),
('score_risk','CASE WHEN high_risk_employee_percentage<=10 THEN 10 WHEN high_risk_employee_percentage<=20 THEN 7 WHEN high_risk_employee_percentage<=30 THEN 4 ELSE 2 END','CASE WHEN high_risk_employee_percentage<=5 THEN 10 WHEN high_risk_employee_percentage<=15 THEN 7 WHEN high_risk_employee_percentage<=25 THEN 4 ELSE 2 END')]:patches.append((label,[(old,new)]))
rerun(16,patches,clock=clock)
save(REC/'024_calibration_queries.json',queries)
