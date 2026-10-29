"""Agent-visible verification queries, at most 5 per target, plus separately marked diagnostics."""
from annotate_dacomp_batch020 import *
from plan_dacomp_batch020 import pkg,rows
out=[]
for i,r in enumerate(rows[:43]):
 d=pkg(i);n=int(r['task'][-3:]);case=json.loads((REC/'013_cases.json').read_text())[n-1];sql=d['agent_final_SQL'][0]['text'];refs=sorted(set(re.findall(r'\b(?:FROM|JOIN)\s+((?:raw|staging|intermediate)\.[a-zA-Z_0-9]+)',sql,re.I)))
 qs=[]
 if refs:
  predicates=' OR '.join("(table_schema='"+x.split('.')[0]+"' AND table_name='"+x.split('.')[1]+"')" for x in refs)
  qs.append("SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE "+predicates+' ORDER BY table_schema,table_name,ordinal_position')
 if i in range(13,32):
  ref=refs[0];cols=[x['edits'][0][0] for z in json.loads((REC/'020_patch_plan.json').read_text()) if z['index']==i for x in z['patches']];names=[]
  with duckdb.connect(case['agent_database'],read_only=True) as c:
   actual=[x[0] for x in c.execute('DESCRIBE '+ref).fetchall()]
   for name in actual:
    if any(name.lower() in x.lower() for x in cols) and name.lower() not in ['date','day','id']:
     name='"'+name+'"';names +=[f'count(*) FILTER(WHERE {name} IS NULL) AS c{len(names)}_null',f'count(*) FILTER(WHERE {name} IS NOT NULL AND TRY_CAST({name} AS DOUBLE) IS NULL) AS c{len(names)+1}_not_numeric']
  qs.append('SELECT count(*) n'+(','+','.join(names) if names else '')+' FROM '+ref)
 if i in [37,38,39,40]:qs.append('SELECT count(*) n, count(*) FILTER(WHERE active_device_installs<>current_device_installs) unequal, min(active_device_installs) min_active, min(current_device_installs) min_current, max(active_device_installs) max_active, max(current_device_installs) max_current FROM '+refs[0])
 if i==35:qs.append("SELECT count(*) n,count(*) FILTER(WHERE revenue<0) negative_revenue,count(*) FILTER(WHERE revenue<>round(revenue)) fractional_revenue,count(*) FILTER(WHERE trim(subscription_name)='') blank_name FROM "+refs[0])
 if i==36:qs.append('SELECT count(*) n,count(*) FILTER(WHERE subscribers<0) negative_subscribers,count(*) FILTER(WHERE subscribers<>cast(active_standard_price_subscriptions AS BIGINT)) different_active,count(*) FILTER(WHERE active_free_trial_introductory_offer_subscriptions AND subscribers<>1) different_free FROM '+refs[0])
 if i==41:qs.append('SELECT count(*) n,count(*) FILTER(WHERE daily_average_rating IS NULL) null_daily,count(*) FILTER(WHERE daily_average_rating NOT BETWEEN 1 AND 5) invalid_daily,count(*) FILTER(WHERE total_average_rating NOT BETWEEN 1 AND 5) invalid_total FROM '+refs[0])
 if i==42:qs.append('SELECT count(*) n,count(*) FILTER(WHERE store_listing_conversion_rate NOT BETWEEN 0 AND 1) invalid_raw_rate,count(*) FILTER(WHERE store_listing_visitors>0 AND store_listing_acquisitions*1.0/store_listing_visitors>1) invalid_ratio,count(*) FILTER(WHERE store_listing_conversion_rate IS DISTINCT FROM round(store_listing_acquisitions*1.0/nullif(store_listing_visitors,0),4)) different_ratio FROM '+refs[0])
 if i==32:qs.append(' UNION ALL '.join("SELECT '"+ref+"' source,count(*) duplicate_groups,sum(n-1) extra_rows FROM (SELECT date_day,"+('app_name' if 'apple' in ref else 'package_name')+',count(*) n FROM '+ref+' GROUP BY ALL HAVING count(*)>1)' for ref in refs))
 with duckdb.connect(case['agent_database'],read_only=True) as c:
  for j,q in enumerate(qs):
   item=dict(index=i,task=r['task'],table=r['table'],kind='核实',id=f'Q{i:02}-{j+1}',database=case['agent_database'],sql=q)
   try:cur=c.execute(q);item.update(columns=[x[0] for x in cur.description],result=cur.fetchall())
   except Exception as e:item['error']=str(e)
   out.append(item)
 save(REC/'020_queries.json',out)
print(len(out))
