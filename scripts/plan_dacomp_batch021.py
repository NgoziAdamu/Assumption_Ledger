"""Reviewed byte-local interventions; full implementations explicitly diagnostic only."""
from review_dacomp_batch021 import *
import sqlglot
from sqlglot import exp
plan={}
def add(i,label,old,new,cat,reason='',diagnostic=False):
 assert pkg(i)['agent_final_SQL'][0]['text'].count(old)==1,(i,label,old)
 plan.setdefault(i,[]).append(dict(label=label,edits=[(old,new)],category=cat,reason=reason,diagnostic_only=diagnostic))
def whole(i,cat):
 d=pkg(i);add(i,'whole_implementation_diagnostic',d['agent_final_SQL'][0]['text'],d['gold_SQL_仅供定位差异'][0]['text'],cat,'整段实现只作诊断，不算U局部修复。',True)
add(0,'count_joined_tasks','pt.task_id,t.is_completed','t.task_id,t.is_completed','U','P：project_task中的task_id均能匹配可用task；查询核实悬空引用。')
s=pkg(0)['agent_final_SQL'][0]['text'];old=s[s.index('SELECT *,ROUND(100.0'):s.index('DATE_DIFF(\'day\',project_created_at')]
new=old
import re
new=re.sub(r'ROUND\((100\.0\*.*?/NULLIF\([^)]*\)),2\)',r'COALESCE(ROUND(\1,2),0)',new)
add(0,'zero_denominator_policy',old,new,'C','契约明确分母0时百分比为0，必须在有效性过滤前赋0。')
add(1,'timestamp_status',"WHEN is_completed AND completed_at::DATE <= due_date::DATE THEN 'completed_on_time'\n WHEN is_completed AND completed_at::DATE > due_date::DATE THEN 'completed_late'","WHEN is_completed AND completed_at <= due_date THEN 'completed_on_time'\n WHEN is_completed AND completed_at > due_date THEN 'completed_late'",'C')
add(2,'calendar_day_type',"CAST(CAST(created_at AS DATE) AS TIMESTAMP) AT TIME ZONE 'UTC'","date_trunc('day',created_at)",'O')
# Treat both arms as one output type policy; second arm must change consistently.
plan[2][0]['edits'].append(("CAST(CAST(completed_at AS DATE) AS TIMESTAMP) AT TIME ZONE 'UTC'","date_trunc('day',completed_at)"))
add(3,'time_management',"CASE WHEN completion_percentage=100 THEN 25 WHEN remaining_days<0 THEN 5 ELSE 12 END time_management_score","CASE schedule_forecast WHEN 'on_schedule' THEN 25 WHEN 'slight_delay' THEN 20 WHEN 'moderate_delay' THEN 15 WHEN 'significant_delay' THEN 10 WHEN 'overdue' THEN 5 ELSE 12 END time_management_score",'C')
for col in ['unique_action_types','days_with_activity']:
 add(4,col,f'COALESCE(s.{col},0)',f's.{col}','A','无story时补0或保留NULL未明确。')
add(4,'activity_null_policy',"ROUND(COALESCE(s.total_story_events,0)::DOUBLE/DATE_DIFF('day',t.created_at,COALESCE(t.completed_at,CURRENT_TIMESTAMP)),2) ELSE COALESCE(s.total_story_events,0)::DOUBLE","ROUND(s.total_story_events::DOUBLE/DATE_DIFF('day',t.created_at,COALESCE(t.completed_at,CURRENT_TIMESTAMP)),2) ELSE s.total_story_events::DOUBLE",'A')
add(4,'modification_source',"modified_at>=CURRENT_TIMESTAMP-INTERVAL '7 day' THEN 'active_development' WHEN NOT is_completed AND assignee_user_id IS NOT NULL THEN 'stagnant'","DATE_DIFF('day',last_modification_timestamp,CURRENT_TIMESTAMP)<=7 THEN 'active_development' WHEN NOT is_completed AND assignee_user_id IS NOT NULL AND DATE_DIFF('day',last_modification_timestamp,CURRENT_TIMESTAMP)>7 THEN 'stagnant'",'C')
whole(5,'C')
add(6,'required_project_id','WHERE _rn = 1','WHERE _rn = 1 AND project_id IS NOT NULL','C')
for col,raw in [('due_date','due_on'),('start_date','start_on')]:
 old=f"CAST(TRY_STRPTIME({raw}, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP)"
 add(7,col,old,f'COALESCE({old},TRY_CAST({raw} AS TIMESTAMP))','U','P：所有可解析的该源日期都符合同一带时区格式。')
for i in range(8,16):whole(i,'D')
# NULL placeholders projected from actual source fields: independent local repairs.
for i in [9,12,14]:
 for col in ['device_installs','device_uninstalls','device_upgrades','user_installs','user_uninstalls','install_events','uninstall_events','update_events','active_devices_last_30_days']:
  s=pkg(i)['agent_final_SQL'][0]['text'];m=re.search(r'cast\((?:0|NULL) as BIGINT\) AS '+col+r'\b',s)
  add(i,col,m[0],f'cast(src.{col} as BIGINT) AS {col}','D')
add(8,'avg_7d_crashes','CAST(NULL AS DOUBLE) AS avg_7d_crashes','CAST(AVG(crashes) OVER(PARTITION BY package_name ORDER BY date_day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS DOUBLE) AS avg_7d_crashes','D')
add(8,'avg_7d_anrs','CAST(NULL AS DOUBLE) AS avg_7d_anrs','CAST(AVG(anrs) OVER(PARTITION BY package_name ORDER BY date_day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS DOUBLE) AS avg_7d_anrs','D')
add(16,'required_fields','FROM raw.earnings','FROM raw.earnings WHERE package_name IS NOT NULL AND sku_id IS NOT NULL AND transaction_date IS NOT NULL AND transaction_type IS NOT NULL','C')
add(16,'package_source','CAST(base_plan_id AS VARCHAR) AS package_name','CAST(product_id AS VARCHAR) AS package_name','A')
add(17,'required_fields','FROM raw.stats_ratings_overview','FROM raw.stats_ratings_overview WHERE date_day IS NOT NULL AND package_name IS NOT NULL','C')
add(24,'unique_engagement','where engagement_id is not null',"where engagement_id is not null QUALIFY row_number() over(partition by cast(engagement_id as varchar) order by property_hs_lastmodifieddate desc nulls last, property_hs_createdate desc nulls last)=1",'C')
for col,raw in [('created_timestamp','created_at'),('updated_timestamp','updated_at')]:
 old=f"try_strptime(substr({raw}, 1, 19), '%Y-%m-%d %H:%M:%S')"
 new=f"CASE WHEN {raw} IS NOT NULL AND CAST({raw} AS VARCHAR) ~ '^\\d{{4}}-\\d{{2}}-\\d{{2}}' THEN CAST({raw} AS TIMESTAMP) ELSE NULL END"
 add(25,col,old,new,'O','gold正则全串匹配使规范时间戳为空；created违反not_null。',True)
add(29,'unresolved_open_until','coalesce(cast(valid_starting_on as date),current_date)','case when i.resolved_at is null then current_date else cast(valid_starting_on as date) end','C')
add(29,'history_driver','from staging.stg_jira__issue i left join intermediate.int_jira__field_history_scd f using(issue_id)','from intermediate.int_jira__field_history_scd f left join staging.stg_jira__issue i using(issue_id)','A')
add(30,'remove_many_to_many','select h.issue_id,h.change_time,a.days_between_changes from h join a using(issue_id) where h.previous_change_time is not null',"select issue_id,change_time,epoch(change_time-previous_change_time)/86400.0 days_between_changes from h where previous_change_time is not null",'C','契约要求直接聚合时间间隔，agent额外按issue_id自连接。')
add(31,'derived_parent_name','i.*,coalesce(i.revised_parent_issue_id,i.parent_issue_id) parent_issue_id_derived','i.issue_id,coalesce(cast(i.revised_parent_issue_id as varchar),cast(i.parent_issue_id as varchar)) parent_issue_id,i.*','C')
for col in ['status','sprint','story_points','story_point_estimate']:
 # A single per-field NULL placement policy is altered; both constituent expressions belong to that output.
 s=pkg(32)['agent_final_SQL'][0]['text'];pred="lower(field_id)='status'" if col=='status' else "lower(field_name)='"+col.replace('_',' ')+"'"
 old=f'max(field_value) filter(where {pred}) {col}'
 add(32,col,old,f"max(coalesce(field_value,'is_null')) filter(where {pred}) {col}",'C')
 plan[32][-1]['edits'].append((f"coalesce({col},'is_null') {col}",col))
whole(33,'D');whole(34,'D')
add(34,'remove_limit',' limit 1000','','D','无数据判断直接裁剪至1000行。')
for i in [35,36,37,38,39]:whole(i,'D')
(REC/'021_patch_plan.json').write_text(json.dumps([dict(index=i,task=rows[i]['task'],table=rows[i]['table'],patches=p) for i,p in sorted(plan.items())],ensure_ascii=False,indent=2)+'\n')
print('planned',len(plan),sum(map(len,plan.values())))
