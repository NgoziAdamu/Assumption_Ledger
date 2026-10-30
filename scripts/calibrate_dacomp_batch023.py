"""Blind calibration, only original data and 012/013 material packages."""
from annotate_dacomp_batch023 import *
queries=[]
def q(n,label,sql):
 case=json.loads((REC/'013_cases.json').read_text())[n-1]
 with duckdb.connect(case['agent_database'],read_only=True) as c:
  r=c.execute(sql);queries.append(dict(task=case['task'],label=label,sql=sql,columns=[x[0] for x in r.description],rows=r.fetchall(),database=case['agent_database']))
q(9,'country 编码连接基数',"SELECT (SELECT count(*) FROM raw.stats_store_performance_country) source_rows,(SELECT count(*) FROM raw.stats_store_performance_country p LEFT JOIN raw.google_play__country_codes c ON c.country_code_numeric=p.country_region) joined_rows,(SELECT count(*) FROM (SELECT country_code_numeric FROM raw.google_play__country_codes GROUP BY 1 HAVING count(*)>1)) duplicate_numeric_codes")
q(9,'源键空值',"SELECT count(*) n,count(*) FILTER(WHERE date IS NULL) null_date,count(*) FILTER(WHERE package_name IS NULL) null_package,count(*) FILTER(WHERE country_region IS NULL) null_country FROM raw.stats_store_performance_country")
q(24,'email 边界样例',"SELECT count(*) n,count(*) FILTER(WHERE EMAIL LIKE '%..%') consecutive_dot_emails FROM raw.tiktok_advertiser_data")
save(REC/'023_calibration_queries.json',queries)
rerun(9,[('country_projection',[('cc.country_code_alpha_2','country_region')]),('join_cardinality',[('raw.google_play__country_codes AS cc','(SELECT * FROM raw.google_play__country_codes QUALIFY row_number() OVER(PARTITION BY country_code_numeric ORDER BY country_code_alpha_2)=1) AS cc')])])
p=package(24);s=p['agent_final_SQL'][0]['text'];old=next(x.strip().split(' as email')[0] for x in s.splitlines() if ' as email' in x)
new="case when regexp_full_match(lower(trim(\"EMAIL\")), '^[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}$') then lower(trim(\"EMAIL\")) else null end"
rerun(24,[('email_pattern',[(old,new)])])
