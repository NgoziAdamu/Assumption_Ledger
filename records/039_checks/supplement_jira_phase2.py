import sys,json,re,hashlib,inspect
from pathlib import Path
sys.path[:0]=['scripts','data/005_tools']
import duckdb
import annotate_dacomp_batch016 as base
from compare_dacomp_fast021 import src as fast_src
C=Path('records/039_checks');cat=json.loads((C/'evidence_catalog.json').read_text())
# Identical weighted comparator; keep immutable normalized gold across candidates.
src=fast_src.replace("  select=','.join(normalized(col)","  if side=='g' and globals().get('gold_cached',False):continue\n  select=','.join(normalized(col)")
ns=dict(vars(base));exec(src,ns);compare=ns['compare_sql']
o=cat[35];d=json.load(open('records/021_fast_reruns_'+o['object']+'.json'));b=d['basis'];orig=Path(o['agent_sql']).read_text().strip().rstrip(';')
for e in d['clock_control']:orig=re.sub(e['pattern'],e['replacement'],orig,flags=re.I)
recovery="""WITH ib AS (SELECT *,epoch(coalesce(resolved_at,TIMESTAMPTZ '2025-10-13 00:00:00+00')-created_at)/86400.0 life FROM marts.jira__issue_enhanced),
p AS (SELECT project_id,median(life) med,quantile_cont(life,.75) p75,avg(count_comments) avg_comments FROM ib GROUP BY project_id),
a AS (SELECT ib.*,abs(life-med)/nullif(med,0) deviation,CASE WHEN life>2*p75 THEN 'Statistical Outlier' WHEN life>1.5*p75 THEN 'Above Normal Range' WHEN life<.5*med THEN 'Unusually Fast' ELSE 'Normal Range' END outlier,CASE WHEN count_comments>p.avg_comments*1.5 THEN 5 ELSE 0 END collaboration,CASE WHEN life<med*.7 THEN 5 ELSE 0 END efficiency FROM ib LEFT JOIN p USING(project_id)),
r AS (SELECT *,CASE WHEN deviation>1 THEN 7 ELSE 0 END devrisk,CASE WHEN resolved_at IS NULL AND life>90 THEN 10 ELSE 0 END age,CASE WHEN count_comments=0 THEN 5 ELSE 0 END engagement,CASE WHEN assignee_user_id IS NULL THEN 8 ELSE 0 END assignment_pts FROM a),
s AS (SELECT *,devrisk+age+engagement+assignment_pts risk,collaboration+efficiency+5 opportunity FROM r)
SELECT issue_id,issue_key,deviation AS lifecycle_deviation_ratio,outlier AS lifecycle_outlier_status,devrisk AS deviation_risk_score,collaboration AS collaboration_opportunity_score,efficiency AS efficiency_opportunity_score,risk AS total_risk_score,opportunity AS total_opportunity_score,
CASE WHEN age>0 AND assignment_pts>0 THEN 'Urgent: Assign and Expedite' WHEN engagement>0 THEN 'Encourage Collaboration' WHEN opportunity>10 THEN 'Leverage Best Practices' WHEN resolved_at IS NULL AND life>30 THEN 'Management Review Required' ELSE 'Monitor Progress' END AS recommended_action,
least(100,greatest(0,50+2*opportunity-risk+CASE WHEN resolved_at IS NOT NULL OR life<=14 THEN 10 ELSE 0 END))::INTEGER AS intelligence_score,
CASE WHEN risk>=25 THEN 'Critical' WHEN risk>=15 THEN 'High Risk' WHEN risk>=8 THEN 'Medium Risk' WHEN risk>0 THEN 'Low Risk' ELSE 'Healthy' END AS health_status,
CASE WHEN lower(current_priority) LIKE '%critical%' OR lower(current_priority) LIKE '%high%' OR lower(issue_type) LIKE '%epic%' THEN 'Strategic' WHEN opportunity>10 THEN 'High Value' ELSE 'Standard' END AS strategic_importance,
CASE WHEN resolved_at IS NULL AND risk>=25 THEN 'Immediate' WHEN resolved_at IS NULL AND risk>=15 THEN 'Within 24 Hours' WHEN resolved_at IS NULL AND risk>=8 THEN 'Within Week' WHEN opportunity>10 THEN 'Study for Replication' ELSE 'Regular Monitoring' END AS intervention_urgency FROM s"""
cols=['lifecycle_deviation_ratio','lifecycle_outlier_status','deviation_risk_score','collaboration_opportunity_score','efficiency_opportunity_score','total_risk_score','total_opportunity_score','recommended_action','intelligence_score','health_status','strategic_importance','intervention_urgency']
out={'object':o['object'],'kind':'单输出恢复诊断','source_record':'records/021_fast_reruns_'+o['object']+'.json','source':d['source'],'original_databases_read_only':True,'private_database':':memory:','baseline_sql':orig,'recovery_sql':recovery,'clock_control':d['clock_control'],'recovery_basis':'按契约从CS上游重算项目中位数/p75、异常及评分。项目内self-join等权重复的统计量可在8千行项目聚合求出；每次只替换agent的一个最终占位输出，不改变原始行数及其他列。gold仅用于比较。','runs':[]}
with duckdb.connect(':memory:') as c:
 c.execute("SET threads=1; SET memory_limit='1500MB'");c.create_function('tolerance_forms',base.udf_forms,['VARCHAR'],duckdb.struct_type({'l1':'VARCHAR','l2':'VARCHAR','l3':'VARCHAR'}))
 c.execute("ATTACH '"+d['source']+"' AS src (READ_ONLY)");c.execute('CREATE SCHEMA marts');c.execute('CREATE TABLE marts.jira__issue_enhanced AS SELECT * FROM src.marts.jira__issue_enhanced')
 c.execute('CREATE TABLE original_result AS '+orig);c.execute('CREATE TABLE recovered_result AS '+recovery)
 out['recovery_duplicate_groups']=c.execute('SELECT count(*) FROM (SELECT issue_id,issue_key,count(*) n FROM recovered_result GROUP BY ALL HAVING n>1)').fetchone()[0];assert out['recovery_duplicate_groups']==0
 for col in ['baseline']+cols:
  sql='SELECT * FROM original_result' if col=='baseline' else f'SELECT original_result.* REPLACE((SELECT recovered_result."{col}" FROM recovered_result WHERE recovered_result.issue_id=original_result.issue_id AND recovered_result.issue_key=original_result.issue_key) AS "{col}") FROM original_result'
  c.execute('CREATE OR REPLACE TABLE candidate AS '+sql);comparison=compare(c,'candidate','src.marts.jira__issue_intelligence_analytics',b);ns['gold_cached']=True
  if col=='baseline':assert comparison==d['runs'][0]['comparison']
  out['runs'].append({'label':col,'sql':sql,'sql_sha256':hashlib.sha256(sql.encode()).hexdigest(),'comparison':comparison});(C/('supplement_'+o['object']+'.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');z=comparison['levels'][0];print(col,z['row_scale'],z['cell_scale'],flush=True)
