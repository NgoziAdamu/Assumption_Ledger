from annotate_dacomp_batch021 import *
from review_dacomp_batch021 import pkg,rows
out=[]
def q(i,sql,side='gold',kind='诊断'):
 case=json.loads((REC/'015_cases.json').read_text())[int(rows[i]['task'][-3:])-1];path=case[side+'_database'];r=dict(index=i,kind=kind,database=path,sql=sql)
 with duckdb.connect(path,read_only=True) as c:
  c.execute("SET TimeZone='UTC'")
  try:
   cur=c.execute(sql);r.update(columns=[x[0] for x in cur.description],result=cur.fetchall())
  except Exception as e:r['error']=str(e)
 out.append(r);print(i,r.get('result',r.get('error')))
q(36,"SELECT count(*) n,count(*) FILTER(WHERE lower(t.issue_type_name) IN ('epic','story','bug')) weighted_names,count(*) FILTER(WHERE i.issue_type_id ILIKE '%epic%' OR i.issue_type_id ILIKE '%story%' OR i.issue_type_id ILIKE '%bug%') weighted_ids,count(*) FILTER(WHERE t.issue_type_id IS NULL) unmatched FROM staging.stg_jira__issue i LEFT JOIN staging.stg_jira__issue_type t USING(issue_type_id)",'agent','核实')
q(38,"SELECT count(*) n,count(*) FILTER(WHERE avg_outbound_influence_strength IS NULL) missing_strength,count(*) FILTER(WHERE avg_outbound_influence_strength IS NULL AND engagement_depth_score IS NOT NULL) null_policy_conflict,count(*) FILTER(WHERE total_engagement_score IS NOT NULL) scored,string_agg(DISTINCT response_pattern_type,',') response_labels,string_agg(DISTINCT influence_level,',') influence_labels FROM marts.jira__stakeholder_engagement_insights")
q(38,"SELECT count(*) mismatched_users,sum(g.total_comments_authored-coalesce(c.n,0)) excess_comments FROM marts.jira__stakeholder_engagement_insights g LEFT JOIN (SELECT author_user_id,count(*) n FROM staging.stg_jira__comment GROUP BY author_user_id) c ON g.stakeholder_id=c.author_user_id WHERE g.total_comments_authored IS DISTINCT FROM coalesce(c.n,0)")
q(8,"SELECT count(*) n,count(*) FILTER(WHERE daily_average_rating BETWEEN 1 AND 5) valid_ratings FROM staging.stg_google_play__stats_ratings_overview",'agent','核实')
q(35,"SELECT sum(n*n) expected_project_selfjoin_rows FROM (SELECT project_id,count(*) n FROM marts.jira__issue_enhanced WHERE project_id IS NOT NULL GROUP BY project_id)")
q(34,"SELECT count(*) n,count(*) FILTER(WHERE is_active) active_rows FROM staging.stg_jira__issue_field_history",'agent','核实')
save(REC/'021_final_diagnostics.json',out)
