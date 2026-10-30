from annotate_dacomp_batch024 import *
ps=json.loads((REC/'024_patch_plan.json').read_text());inv=json.loads((REC/'024_package_inventory.json').read_text());out=[]
for p in ps:
 d=json.loads((ROOT/next(x['full_json'] for x in inv if x['table']==p['table'])).read_text());g=d['gold_SQL_仅供定位差异'][0]['text'];b=d['differences'];cols=re.findall(r'current_timestamp\s+(?:as\s+)?([\w]+)',g,re.I)
 for col in cols:
  q=f'SELECT min({col}),max({col}) FROM {b["actual_schema"]}.{b["table"]}'
  try:
   with duckdb.connect(b['gold_database'],read_only=True) as c:row=c.execute(q).fetchone()
   if row[0] and row[0]==row[1]:p['clock']=str(row[0]);out.append(dict(table=p['table'],kind='诊断',sql=q,rows=[row],database=b['gold_database']));break
  except Exception:pass
save(REC/'024_history_clock.json',out);save(REC/'024_patch_plan.json',ps)
