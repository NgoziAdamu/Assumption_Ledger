from annotate_dacomp_batch021 import *
from review_dacomp_batch021 import pkg
p=pkg(35);b=p['differences'];work=ROOT/'data/021_runtime';work.mkdir(exist_ok=True)
with duckdb.connect(str(work/'diagnostic.duckdb')) as c:
 c.execute("SET threads=2; SET memory_limit='1500MB'")
 c.execute("ATTACH '"+b['gold_database']+"' AS gold (READ_ONLY)")
 c.execute("ATTACH '"+str(ROOT/'data/021_fast_work/impl-011_jira__issue_intelligence_analytics/work.duckdb')+"' AS replay (READ_ONLY)")
 cols=list(dict.fromkeys(b['key_columns']+b['comparison_columns']));cols=[x for x in cols if x not in ['total_lifecycle_days','lifecycle_deviation_ratio']];projection=','.join('"'+x+'"' for x in cols)
 q=f'''WITH a AS(SELECT {projection},count(*) n FROM replay.marts.jira__issue_intelligence_analytics GROUP BY ALL),g AS(SELECT {projection},count(*) n FROM gold.marts.jira__issue_intelligence_analytics GROUP BY ALL) SELECT (SELECT count(*) FROM (SELECT * FROM a EXCEPT ALL SELECT * FROM g)),(SELECT count(*) FROM (SELECT * FROM g EXCEPT ALL SELECT * FROM a))'''
 r={'index':35,'kind':'诊断','sql':q,'result':c.execute(q).fetchall(),'meaning':'排除两个运行时派生列后，带重复次数的整行分组多重集差异；0/0才证明其余列与多重性完全一致。'}
 q2="SELECT min(i.created_at+g.total_lifecycle_days*interval '1 day')::VARCHAR,max(i.created_at+g.total_lifecycle_days*interval '1 day')::VARCHAR FROM gold.marts.jira__issue_intelligence_analytics g JOIN gold.marts.jira__issue_enhanced i USING(issue_id) WHERE i.resolved_at IS NULL"
 try:r2={'index':35,'kind':'诊断','sql':q2,'result':c.execute(q2).fetchall()}
 except Exception as e:r2={'index':35,'kind':'诊断','sql':q2,'error':str(e)}
 save(REC/'021_runtime_diagnostics.json',[r,r2]);print(r['result'],r2)
