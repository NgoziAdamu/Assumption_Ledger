from rerun_dacomp_supplement021 import *
from review_dacomp_batch021 import pkg,rows
plans={}
def add(i,label,edits,cat,diagnostic=False):plans.setdefault(i,[]).append(dict(label=label,edits=edits,category=cat,diagnostic_only=diagnostic))
add(2,'source_timezone_midnight',[("AT TIME ZONE 'UTC' AS date_day","AT TIME ZONE 'Asia/Singapore' AS date_day")],'A')
# two identical occurrences: use complete select expression for exact byte changes
plans[2][0]['edits']=[(f"CAST(CAST({col} AS DATE) AS TIMESTAMP) AT TIME ZONE 'UTC'",f"CAST(CAST({col} AS DATE) AS TIMESTAMP) AT TIME ZONE 'Asia/Singapore'") for col in ['created_at','completed_at']]
for col in ['unique_action_types','days_with_activity']:add(4,col,[(f'COALESCE(s.{col},0)',f's.{col}')],'A')
s=pkg(4)['agent_final_SQL'][0]['text'];old="ROUND(COALESCE(s.total_story_events,0)::DOUBLE/DATE_DIFF('day',t.created_at,COALESCE(t.completed_at,CURRENT_TIMESTAMP)),2) ELSE COALESCE(s.total_story_events,0)::DOUBLE";new=old.replace('COALESCE(s.total_story_events,0)','s.total_story_events')
add(4,'missing_activity_null_policy',[(old,new),('AND avg_daily_activity_rate>=0 AND','AND (avg_daily_activity_rate IS NULL OR avg_daily_activity_rate>=0) AND')],'A')
add(4,'modification_source',[("modified_at>=CURRENT_TIMESTAMP-INTERVAL '7 day' THEN 'active_development' WHEN NOT is_completed AND assignee_user_id IS NOT NULL THEN 'stagnant'","DATE_DIFF('day',last_modification_timestamp,CURRENT_TIMESTAMP)<=7 THEN 'active_development' WHEN NOT is_completed AND assignee_user_id IS NOT NULL AND DATE_DIFF('day',last_modification_timestamp,CURRENT_TIMESTAMP)>7 THEN 'stagnant'")],'C')
add(4,'gold_sql_same_clock',[(s,pkg(4)['gold_SQL_仅供定位差异'][0]['text'])],'O',True)
# due date source mapping; retain output type
old="COALESCE(CAST(TRY_STRPTIME(due_at, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP), CAST(TRY_STRPTIME(due_on, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP))"
add(7,'due_source_choice',[(old,"CAST(TRY_STRPTIME(due_on, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP)")],'A')
add(7,'due_gold_type',[(old,"COALESCE(TRY_STRPTIME(due_at, '%Y-%m-%d %H:%M:%S.%f %z'), TRY_STRPTIME(due_on, '%Y-%m-%d %H:%M:%S.%f %z'))")],'O',True)
old="CAST(TRY_STRPTIME(start_on, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP)"
add(7,'start_gold_type',[(old,"TRY_STRPTIME(start_on, '%Y-%m-%d %H:%M:%S.%f %z')")],'O',True)
# Only copy fields declared by the contracts under their actual upstream names.
for i in [9,12,14]:
 for col in ['device_installs','device_uninstalls','device_upgrades','user_installs','user_uninstalls','active_devices_last_30_days']:
  raw='active_device_installs' if col=='active_devices_last_30_days' else 'daily_'+col
  s=pkg(i)['agent_final_SQL'][0]['text'];m=re.search(r'cast\((?:0|NULL) as BIGINT\) AS '+col+r'\b',s)
  add(i,col,[(m[0],f'cast(coalesce(src.{raw},0) as BIGINT) AS {col}')],'D')
# mandatory output constraint without shadowing raw columns
s=pkg(16)['agent_final_SQL'][0]['text']
add(16,'output_not_null_policy',[(s,'SELECT * FROM ('+s+') checked WHERE package_name IS NOT NULL AND sku_id IS NOT NULL AND transaction_date IS NOT NULL AND transaction_type IS NOT NULL')],'C')
add(16,'missing_required_source_policy',[(s,pkg(16)['gold_SQL_仅供定位差异'][0]['text'])],'A',True)
# independent null placeholders in sprint enhanced: explicit aggregate formulas from contract/gold
s=pkg(37)['gold_SQL_仅供定位差异'][0]['text']
# remaining detailed patches added separately after source review
save(REC/'021_supplement_patch_plan.json',[dict(index=i,patches=p) for i,p in plans.items()])
if __name__=='__main__':
 for i,patches in plans.items():
  if len(sys.argv)>1 and str(i) not in sys.argv[1:]:continue
  d=pkg(i);date=d['differences'].get('candidate_date') or '2025-10-12';clock=date+' 00:00:00+00'
  if i==4:clock='2025-10-12 09:00:00+00'
  rerun(int(rows[i]['task'][-3:]),[(x['label'],x['edits']) for x in patches],clock=clock,pkg=d)
