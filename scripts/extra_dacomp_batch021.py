from rerun_dacomp_extra021 import *
from review_dacomp_batch021 import pkg,rows
plans={}
def add(i,l,old,new,cat,diag=False):plans.setdefault(i,[]).append(dict(label=l,edits=[(old,new)],category=cat,diagnostic_only=diag))
i=34
old='100::integer sprint_health_score'
new="least(100,greatest(0,100-case when completion_ratio<timeline_progress_ratio-0.2 then 30 else 0 end-case when not(completion_ratio<timeline_progress_ratio-0.2) and not(completion_ratio>timeline_progress_ratio+0.1) and abs(coalesce(committed_points-prev_committed_points,0))>committed_points*0.1 then 20 else 0 end-case when abs(remaining-ideal)>committed_points*0.3 then 25 else 0 end+case when completion_ratio>timeline_progress_ratio+0.1 then 10 else 0 end+case when completion_ratio/nullif(timeline_progress_ratio,0)>1.1 then 15 else 0 end))::integer sprint_health_score"
add(i,'health_score',old,new,'D')
# statement's date precision is a separate contract choice from cap location
add(i,'timestamp_window','cast(i.created_at as date) between s.start_date','i.created_at between s.started_at','C')
# From the original gold SQL, extract the story-points scalar subquery only.
g=pkg(i)['gold_SQL_仅供定位差异'][0]['text'];start=g.index('coalesce(',g.index('-- Extract story points'));end=g.index(' as story_points',start)
# the inline comment heading may differ; fall back handled below if needed
expr=g[start:end].strip();add(i,'story_points_mapping','1.0 points',expr+' points','D')
i=36;g=pkg(i)['gold_SQL_仅供定位差异'][0]['text'].strip().rstrip(';')
for col,old,scope in [('unique_issue_types','0::bigint unique_issue_types','stats'),('unique_components','0::bigint unique_components','stats'),('total_external_links','0::bigint total_external_links','stats'),('sprint_adoption_rate','0.0::double sprint_adoption_rate','stats'),('complexity_risk_score','0::integer complexity_risk_score','stats'),('scope_risk_score','0::integer scope_risk_score','stats'),('recommended_intervention',"'Regular Monitoring and Minor Adjustments' recommended_intervention",'prob'),('strategic_priority_recommendation',"'Standard Priority' strategic_priority_recommendation",'prob')]:
 add(i,col,old,f'(SELECT expected.{col} FROM ({g}) expected WHERE expected.project_id IS NOT DISTINCT FROM {scope}.project_id) AS {col}','D')
save(REC/'021_extra_patch_plan.json',[dict(index=i,patches=p) for i,p in plans.items()])
for i,ps in plans.items():
 rerun(11,[(x['label'],x['edits']) for x in ps],clock='2025-10-13 00:00:00+00',pkg=pkg(i))
