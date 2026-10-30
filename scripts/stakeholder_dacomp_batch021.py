"""Isolate additional local errors; scalar subqueries read CS upstream, never gold result rows."""
from rerun_dacomp_extra021 import *
from review_dacomp_batch021 import pkg,rows
import sqlglot
from sqlglot import exp
plans={}
def add(i,label,old,new,cat,diag=False):
 assert pkg(i)['agent_final_SQL'][0]['text'].count(old)==1,(i,label,old)
 plans.setdefault(i,[]).append(dict(label=label,edits=[(old,new)],category=cat,diagnostic_only=diag))
def scalar_patch(i,col,outerkey,cat='D',diag=False):
 d=pkg(i);s=d['agent_final_SQL'][0]['text'];g=d['gold_SQL_仅供定位差异'][0]['text'].strip().rstrip(';');tree=sqlglot.parse_one(s,read='duckdb');vals=[x for x in tree.expressions if isinstance(x,exp.Alias) and x.alias_or_name.lower()==col.lower()];assert len(vals)==1,(i,col)
 v=vals[0];# identify original expression from parser offsets (aliases may lack positions)
 # Find full alias via SQL lexer boundaries, then expand left to enclosing expression with token span.
 # tokenizer uses module imported above
 tokens=sqlglot.Tokenizer(dialect='duckdb').tokenize(s)
 # delimiter-based original select-list item boundaries, respecting parentheses
 depth=0;boundaries=[0]
 for t in tokens:
  if t.text=='(':depth+=1
  elif t.text==')':depth-=1
  if t.text==',' and depth==0:boundaries.append(t.end+1)
 # use literal span from rendered parsed expression and search manual list with balanced depth per SELECT tree
 # SQLGlot source locations give col alias exact location; use outer select expression list split for these one-line statements.
 aliasmatch=list(re.finditer(r'\b'+re.escape(col)+r'\b',s,re.I))
 candidates=[]
 for m in aliasmatch:
  j=m.start()-1;bal=0
  while j>=0:
   ch=s[j]
   if ch==')':bal+=1
   elif ch=='(':bal-=1
   if ch==',' and bal==0:break
   j-=1
  old=s[j+1:m.end()].strip()
  if old.lower().startswith('select '):old=old[7:]
  try:
   parsed=sqlglot.parse_one('SELECT '+old,read='duckdb').expressions[0]
   if isinstance(parsed,exp.Alias) and parsed.alias_or_name.lower()==col and parsed.this==v.this:candidates.append(old)
  except Exception:pass
 assert len(candidates)==1,(i,col,candidates)
 key=d['differences']['key_columns'][0]
 expr=f'(SELECT expected."{col}" FROM ({g}) expected WHERE expected."{key}" IS NOT DISTINCT FROM {outerkey}) AS {col}'
 add(i,col,candidates[0],expr,cat,diag)
# Each scalar computes one field from the gold SQL logic on the same CS input (not held output).
for col in ['medium_projects','small_projects','developing_performers','avg_tasks_per_member','collaboration_efficiency_score','resource_optimization_score','overall_team_efficiency_score','improvement_recommendations','team_strengths']:
 scalar_patch(5,col,'t.team_id','C' if col in ['medium_projects','small_projects'] else 'D')
# Move cap from snapshot pairs to qualifying sprint/issue pairs. Keep agent's date predicate for this isolated patch.
old='from snapshots s join staging.stg_jira__issue i on cast(i.created_at as date) between s.start_date and coalesce(s.completed_at,s.ended_at,current_timestamp) limit 1000'
new='from snapshots s join (select sp.sprint_id,i.* from s sp cross join staging.stg_jira__issue i where cast(i.created_at as date) between sp.start_date and coalesce(sp.completed_at,sp.ended_at,current_timestamp) limit 1000) i on s.sprint_id=i.sprint_id'
add(34,'limit_before_snapshots',old,new,'C')
add(34,'velocity_trend','null::double velocity_trend_3d','avg(prev_remaining-remaining) over(partition by sprint_id order by day_number rows between 2 preceding and current row) velocity_trend_3d','D')
add(34,'velocity_null_default',"case when coalesce(prev_remaining-remaining,0)>5 then 'High Velocity' when coalesce(prev_remaining-remaining,0)>2 then 'Good Velocity' when coalesce(prev_remaining-remaining,0)>0 then 'Low Velocity' when coalesce(prev_remaining-remaining,0)=0 then 'No Progress' else 'Negative Velocity' end","case when prev_remaining-remaining>5 then 'High Velocity' when prev_remaining-remaining>2 then 'Good Velocity' when prev_remaining-remaining>0 then 'Low Velocity' when prev_remaining-remaining=0 then 'No Progress' else 'Negative Velocity' end",'C')
add(35,'comparative_join_multiplicity','from marts.jira__issue_enhanced','from (select base.* from marts.jira__issue_enhanced base join marts.jira__issue_enhanced peer on base.project_id=peer.project_id) comparative','C')
for col in ['estimated_project_value_points','delivered_value_points']:
 # These two aggregate aliases are exposed under different short aliases in iv; handle same type-selection expression separately below.
 pass
s=pkg(36)['agent_final_SQL'][0]['text'];old="case lower(t.issue_type_name) when 'epic' then 8.0 when 'story' then 3.0 when 'bug' then 1.5 else 2.0 end";new="case when i.issue_type_id ilike '%epic%' then 8.0 when i.issue_type_id ilike '%story%' then 3.0 when i.issue_type_id ilike '%bug%' then 1.5 else 2.0 end"
# one source-choice policy occurs in estimated and delivered weights
plans.setdefault(36,[]).append(dict(label='type_id_instead_name',edits=[('sum('+old+') estimated','sum('+new+') estimated'),('then '+old+' else 0 end) delivered','then '+new+' else 0 end) delivered')],category='A',diagnostic_only=False))
for col in ['unique_issue_types','unique_components','total_external_links','sprint_adoption_rate','complexity_risk_score','scope_risk_score','recommended_intervention','strategic_priority_recommendation']:
 # Outer aliases are in multiple CTEs; unqualified key would self-correlate, so skip generic routine here.
 pass
# Sprint fields from contract, one aggregate per output.
start="date_day=cast(sprint_started_at as date) or (date_day<cast(sprint_started_at as date) and date_day=cast(current_timestamp as date))"
end='date_day=cast(sprint_ended_at as date)'
for col in ['story_points_committed','story_point_estimate_committed','story_points_end','story_point_estimate_end','story_points_completed','story_point_estimate_completed']:
 raw='story_point_estimate' if col.startswith('story_point_estimate') else 'story_points';value=f'coalesce({raw},0)' if not col.endswith('completed') else f'case when is_issue_resolved_in_sprint then {raw} else 0 end';pred=start if col.endswith('committed') else end
 add(37,col,f'null::hugeint {col}',f'sum({value}) filter(where {pred}) {col}','D')
add(37,'issues_committed','null::bigint issues_committed',f'count(distinct issue_id) filter(where {start}) issues_committed','D')
for col in ['response_pattern_type','engagement_depth_score','total_engagement_score','stakeholder_archetype','influence_level','development_opportunity','total_comments_authored','total_projects_involved','cross_functional_projects','engagement_breadth_score','engagement_quality_score','engagement_impact_score','engagement_risk_status','strategic_value_score','recommended_engagement_strategy']:
 scalar_patch(38,col,'u.user_id','O' if col in ['engagement_depth_score','total_engagement_score','influence_level'] else 'D',col in ['engagement_depth_score','total_engagement_score','influence_level'])
add(39,'user_metrics_driver','from staging.stg_jira__user u left join intermediate.int_jira__user_metrics m using(user_id)','from staging.stg_jira__user u join intermediate.int_jira__user_metrics m using(user_id)','C')
for col in ['avg_daily_activity_score','avg_weekly_activity_score']:
 add(39,col,f'coalesce(m.avg_close_time_days,0)::decimal(18,0) {col}',f'm.avg_close_time_days::decimal(18,0) {col}','C')
for col in ['projects_contributed_to','issue_types_worked_on','days_since_first_issue','leadership_indicator','overall_performance_score']:
 scalar_patch(39,col,'u.user_id','D')
save(REC/'021_stakeholder_patch_plan.json',[dict(index=i,patches=p) for i,p in plans.items()])
if __name__=='__main__':
 for i,patches in plans.items():
  if i==38:patches=[x for x in patches if x['label'] not in ['response_pattern_type','engagement_depth_score','total_engagement_score','stakeholder_archetype','influence_level','development_opportunity']]
  if len(sys.argv)>1 and str(i) not in sys.argv[1:]:continue
  d=pkg(i);clock=(d['differences'].get('candidate_date') or '2025-10-13')+' 00:00:00+00'
  rerun(int(rows[i]['task'][-3:]),[(x['label'],x['edits']) for x in patches],clock=clock,pkg=d)
