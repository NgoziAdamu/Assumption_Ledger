from annotate_dacomp_batch022 import *
x=json.loads((REC/'022_queries.json').read_text());fix=[]
for r in x:
 if 'error' not in r:continue
 sql=r['sql'].replace('count(*) rows','count(*) source_rows').replace('count(*) groups','count(*) key_groups')
 with duckdb.connect(r['database'],read_only=True) as c:
  if 'impl-013' in r['database']:
   case=json.loads((REC/'013_cases.json').read_text())[12];c.execute("ATTACH '"+case['initial_database']+"' AS source (READ_ONLY)")
  cur=c.execute(sql);fix.append({**{k:v for k,v in r.items() if k not in ['error','sql']},'retry_of':r['sql'],'sql':sql,'columns':[v[0] for v in cur.description],'result':cur.fetchall()})
save(REC/'022_queries_retry.json',fix)
