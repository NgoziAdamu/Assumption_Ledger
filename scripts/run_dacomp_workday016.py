from annotate_dacomp_batch016 import *
s=Path(package(16)['agent_final_SQL'][0]['path']).read_text();P=[]
def patch(label,old,new):assert old in s,label;P.append((label,[(old,new)]))
for label,old in [('annual_zero',"round(coalesce(departures_last_year,0)*100.0/NULLIF(current_active_employees,0),2)::DOUBLE"),('management_zero',"round((coalesce(management_role_employees,0)+coalesce(director_role_employees,0))*100.0/NULLIF(current_active_employees,0),2)::DOUBLE"),('risk_zero',"round(coalesce(high_risk_employees,0)*100.0/NULLIF(current_active_employees,0),2)::DOUBLE"),('fill_zero',"round(coalesce(current_active_employees,0)*100.0/NULLIF(total_positions,0),2)::DOUBLE")]:patch(label,old,f'coalesce({old},0)')
patch('maturity_labels',"THEN 'New' WHEN date_diff('day',effective_start,current_date)<1095 THEN 'Young' WHEN date_diff('day',effective_start,current_date)<3650 THEN 'Mature' ELSE 'Legacy'", "THEN 'New Organization (<1 year)' WHEN date_diff('day',effective_start,current_date)<1095 THEN 'Young Organization (1-3 years)' WHEN date_diff('day',effective_start,current_date)<3650 THEN 'Mature Organization (3-10 years)' ELSE 'Legacy Organization (10+ years)'")
patch('size_labels',"THEN 'Empty' WHEN current_active_employees<=5 THEN 'Micro' WHEN current_active_employees<=15 THEN 'Small' WHEN current_active_employees<=50 THEN 'Medium' WHEN current_active_employees<=200 THEN 'Large' ELSE 'Enterprise'","THEN 'Empty Organization' WHEN current_active_employees<=5 THEN 'Micro Team' WHEN current_active_employees<=15 THEN 'Small Team' WHEN current_active_employees<=50 THEN 'Medium Team' WHEN current_active_employees<=200 THEN 'Large Team' ELSE 'Enterprise Unit'")
old=s[s.index(' SELECT ow.organization_id'):s.index('), perf AS')]
new=""" SELECT wpo.organization_id,wpo.source_relation,count(DISTINCT ow.role_id) unique_organization_roles,count(DISTINCT wpo.worker_id) FILTER(WHERE r.organization_role_code LIKE '%Manager%') management_role_employees,count(DISTINCT wpo.worker_id) FILTER(WHERE r.organization_role_code LIKE '%Director%') director_role_employees,count(DISTINCT wpo.worker_id) FILTER(WHERE r.organization_role_code LIKE '%Lead%') lead_role_employees FROM staging.stg_workday__worker_position_organization wpo LEFT JOIN staging.stg_workday__organization_role_worker ow ON wpo.worker_id=ow.organization_worker_code AND wpo.source_relation=ow.source_relation LEFT JOIN staging.stg_workday__organization_role r ON ow.role_id=r.organization_role_id AND ow.source_relation=r.source_relation AND wpo.organization_id=r.organization_id GROUP BY wpo.organization_id,wpo.source_relation
"""
patch('roles_relationship',old,new)
old=s[s.index(' SELECT worker_id'):s.index('), stats AS')]
new=old.replace(' SELECT worker_id,organization_id,source_relation,position_id,effective_start,effective_end,',' SELECT wpo.worker_id,wpo.organization_id,wpo.source_relation,wpo.position_id,wpo.effective_start,wpo.effective_end,').replace(' FROM staging.stg_workday__worker_position_organization',' FROM staging.stg_workday__worker_position_organization wpo LEFT JOIN staging.stg_workday__organization_role_worker ow ON wpo.worker_id=ow.organization_worker_code AND wpo.source_relation=ow.source_relation LEFT JOIN staging.stg_workday__organization_role r ON ow.role_id=r.organization_role_id AND ow.source_relation=r.source_relation AND wpo.organization_id=r.organization_id')
patch('tenure_join_weight',old,new)
patch('health_turnover_rule',"CASE WHEN departures_last_year=0 THEN 25 WHEN annual_turnover_rate<=10 THEN 25 WHEN annual_turnover_rate<=20 THEN 20 WHEN annual_turnover_rate<=30 THEN 15 WHEN annual_turnover_rate<=40 THEN 10 ELSE 5 END","CASE WHEN coalesce(departures_last_year,0)=0 AND coalesce(current_active_employees,0)>0 THEN 25 WHEN annual_turnover_rate<=10 THEN 20 WHEN annual_turnover_rate<=20 THEN 15 WHEN annual_turnover_rate<=30 THEN 10 ELSE 5 END")
patch('health_risk_rule',"CASE WHEN high_risk_employee_percentage<=10 THEN 10 WHEN high_risk_employee_percentage<=20 THEN 7 WHEN high_risk_employee_percentage<=30 THEN 4 ELSE 2 END","CASE WHEN high_risk_employee_percentage<=5 THEN 10 WHEN high_risk_employee_percentage<=15 THEN 7 WHEN high_risk_employee_percentage<=25 THEN 4 ELSE 2 END")
# All comparisons hold the clock at gold's stored timestamp so runtime-only differences do not dominate.
b=package(16)['differences'];q='SELECT cast(min(analysis_timestamp) as varchar),cast(max(analysis_timestamp) as varchar) FROM mart.workday__organization_overview'
with duckdb.connect(b['gold_database'],read_only=True) as c:
 c.execute("SET TimeZone='Asia/Singapore'");clock,maximum=c.execute(q).fetchone()
save(REC/'016_workday_clock.json',{'kind':'诊断查询','database':b['gold_database'],'sql':q,'clock':clock,'maximum':maximum,'reason':'use same clock in unchanged baseline and every single intervention; not an attributed fix'})
# Substitute old patches with the same controlled clock text that the harness will use.
controlled=[]
for name,edits in P:
 es=[]
 for old,new in edits:
  for pat,repl in [(r'\bcurrent_timestamp\b',f"TIMESTAMPTZ '{clock}'"),(r'\bcurrent_date\b',f"DATE '{clock[:10]}'")]:old=re.sub(pat,repl,old,flags=re.I);new=re.sub(pat,repl,new,flags=re.I)
  es.append((old,new))
 controlled.append((name,es))
rerun(16,controlled,clock=clock)
