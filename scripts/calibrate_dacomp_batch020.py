"""Blind calibration: only 012 packages, original data and original events."""
from annotate_dacomp_batch020 import *
p=package(2);s=p['agent_final_SQL'][0]['text']
key=s[s.index("md5(concat_ws"):s.index(' AS guide_event_key')]
g=p['gold_SQL_仅供定位差异'][0]['text'];gkey=g[g.index('CASE\n        WHEN account_id'):g.index(' as guide_event_key')]
rerun(2,[('latitude', [('TRY_CAST(latitude AS DOUBLE) AS latitude','CASE WHEN TRY_CAST(latitude AS DOUBLE) BETWEEN -90 AND 90 THEN TRY_CAST(latitude AS DOUBLE) ELSE NULL END AS latitude')]),('url',[("CASE WHEN url IS NULL THEN NULL ELSE NULLIF(TRIM(CAST(url AS VARCHAR)), '') END AS url","CASE WHEN url ~ '^https?://' THEN NULLIF(TRIM(CAST(url AS VARCHAR)), '') ELSE NULL END AS url")]),('key',[(key,gkey)])])
p=package(25);s=p['agent_final_SQL'][0]['text'];ed=[]
for raw,target in [('from','user'),('to','contact')]:
 old=next(l.strip().rstrip(',') for l in s.splitlines() if 'as '+target+'_phone_number_raw' in l)
 ed.append((old,f'try_cast("{raw}" as varchar) as {target}_phone_number_raw'))
rerun(25,[('phone_user',[ed[0]]),('phone_contact',[ed[1]]),('phone_policy',ed)],clock='2025-10-12 12:00:00+00')
queries=[]
for n,q in [(2,'SELECT count(*) n, count(*) FILTER (WHERE latitude NOT BETWEEN -90 AND 90) invalid_latitude FROM raw.guide_event'),(25,"SELECT count(*) n, count(*) FILTER(WHERE regexp_matches(\"from\", '^\\+1[0-9]{10}$')) valid_from, count(*) FILTER(WHERE regexp_matches(\"to\", '^\\+1[0-9]{10}$')) valid_to FROM raw.call_data")]:
 case=json.loads((REC/'013_cases.json').read_text())[n-1]
 with duckdb.connect(case['agent_database'],read_only=True) as c:
  cur=c.execute(q);queries.append(dict(task=f'impl-{n:03}',kind='核实',sql=q,columns=[d[0] for d in cur.description],result=cur.fetchall(),database=case['agent_database']))
save(REC/'020_calibration_queries.json',queries)
