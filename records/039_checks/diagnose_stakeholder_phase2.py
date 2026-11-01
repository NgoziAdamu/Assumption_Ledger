import json
from pathlib import Path
import duckdb
C=Path('records/039_checks');o=json.load(open(C/'evidence_catalog.json'))[38];d=json.load(open('records/021_extra_reruns_'+o['object']+'.json'))
sql="""WITH counts AS (SELECT u.user_id,count(distinct i.project_id) raw_projects,count(distinct p.project_id) valid_projects FROM staging.stg_jira__user u LEFT JOIN staging.stg_jira__issue i ON u.user_id IN (i.assignee_user_id,i.reporter_user_id) LEFT JOIN staging.stg_jira__project p ON i.project_id=p.project_id WHERE u.is_active GROUP BY u.user_id)
SELECT count(*) users,count(*) FILTER(WHERE g.cross_functional_projects<>c.raw_projects) raw_count_diff,count(*) FILTER(WHERE g.cross_functional_projects<>c.valid_projects) valid_count_diff,count(*) FILTER(WHERE g.total_projects_involved<>c.raw_projects) union_count_diff,count(*) FILTER(WHERE g.engagement_breadth_score<>least(25,c.raw_projects*8)) breadth_diff,count(*) FILTER(WHERE g.direct_network_connections<>0 OR g.avg_outbound_influence_strength IS NOT NULL) nonzero_network FROM counts c JOIN marts.jira__stakeholder_engagement_insights g ON c.user_id=g.stakeholder_id"""
with duckdb.connect(d['source'],read_only=True) as c:
 cur=c.execute(sql);rows=[dict(zip([x[0] for x in cur.description],r)) for r in cur.fetchall()]
out={'object':o['object'],'purpose':'其他类：gold是否额外要求项目实体匹配；网络零值是否真实。只诊断CS/gold差异，不证明agent可见数据事实。','source':d['source'],'read_only':True,'sql':sql,'rows':rows}
(C/'stakeholder_diagnostic.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(rows)
