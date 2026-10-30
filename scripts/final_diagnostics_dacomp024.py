from annotate_dacomp_batch024 import *
inv=json.loads((REC/'024_package_inventory.json').read_text());cases=json.loads((REC/'013_cases.json').read_text());out=[]
def record(z):out.append(z);save(REC/'024_extra_diagnostics.json',out)
def q(t,label,sql,gold=True):
 r=next(x for x in inv if x['table']==t);d=json.loads((ROOT/r['full_json']).read_text());db=d['differences']['gold_database'] if gold else cases[int(r['task'][-3:])-1]['agent_database'];z=dict(task=r['task'],table=t,kind='诊断' if gold else '核实',label=label,sql=sql,database=db)
 try:
  with duckdb.connect(db,read_only=True) as c:v=c.execute(sql);z.update(columns=[x[0] for x in v.description],rows=v.fetchall())
 except Exception as e:z['error']=str(e)
 record(z)
q('stg_twitter_ads__account_history','timezone空白重试',"SELECT count(*) n,count(*) FILTER(WHERE timezone<>trim(timezone)) whitespace_n FROM raw.twitter_account_history_data",False)
for t in ['tiktok_ads__ad_report','tiktok_ads__url_report']:q(t,'gold连接字段非空',f'SELECT count(*) n,count(ad_name) ads_n,count(advertiser_name) advertisers_n,count(ad_group_id) groups_n,count(campaign_id) campaigns_n FROM marts.{t}')
for r in inv:
 if r['task']!='impl-030' or r['layer']!='staging':continue
 d=json.loads((ROOT/r['full_json']).read_text());a=d['agent_final_SQL'][0]['text'];ids=[x for x in re.findall(r'try_cast\("id" AS VARCHAR\) AS (\w+)',a) if x!=r['table'].replace('stg_zuora__','')+'_id'];qs=[]
 for col in ids:
  target='raw.zuora_'+col.removesuffix('_id')+'_data'
  qs.append(f"SELECT '{col}' col,count(*) n,count(s.{col}) nonnull,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM {target} t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM {target} t WHERE cast(t.id as varchar)=cast(s.{col} as varchar))) named_matches FROM source_rows s")
 if qs:q(r['table'],'实际纳入行的候选映射',a.split('\nSELECT\n')[0]+'\n'+' UNION ALL '.join(qs),False)
# Corresponding baseline/gold multi-set comparison without legitimately arbitrary tie columns.
for t,excluded in [('social_media_reporting__rollup_report',['daily_platform_rank','platform_lifetime_rank']),('xero__invoice_line_items',['line_seq_in_invoice','invoice_cum_gross_nonneg']),('xero__profit_and_loss_report',['cumulative_net'])]:
 r=next(x for x in inv if x['table']==t);d=json.loads((ROOT/r['full_json']).read_text());b=dict(d['differences']);rr=json.loads((REC/f"024_reruns_{r['task']}_{t}.json").read_text());a=(ROOT/rr['runs'][0]['sql_path']).read_text();z=dict(task=r['task'],table=t,kind='诊断',label='排除并列顺序派生列后的整表诊断',excluded=excluded,sql=a,database=b['gold_database'])
 with duckdb.connect(str(ROOT/'data/024_diagnostics'/('diagnostic_'+t+'.duckdb'))) as c:
  c.execute('SET threads=2');c.execute("ATTACH '"+b['gold_database']+"' AS src (READ_ONLY)");c.execute('USE src');c.create_function('tolerance_forms',udf_forms,['VARCHAR'],duckdb.struct_type({'l1':'VARCHAR','l2':'VARCHAR','l3':'VARCHAR'}));c.execute('CREATE TEMP TABLE pred AS '+a.strip().rstrip(';'));b['comparison_columns']=[x for x in b['comparison_columns'] if x not in excluded];z['comparison']=compare_sql(c,'pred',b['actual_schema']+'.'+t,b)
  if 'rollup' in t:
   # ranks are permutations confined to each impression tie block
   z['tie_permutations']=[]
   for rank,partition in [('daily_platform_rank',"platform,date_trunc('day',created_timestamp),impressions"),('platform_lifetime_rank','platform,impressions')]:
    sql=f"SELECT count(*) FROM ((SELECT {partition},list({rank} ORDER BY {rank}) ranks FROM pred GROUP BY ALL EXCEPT ALL SELECT {partition},list({rank} ORDER BY {rank}) ranks FROM src.marts.{t} GROUP BY ALL) UNION ALL (SELECT {partition},list({rank} ORDER BY {rank}) ranks FROM src.marts.{t} GROUP BY ALL EXCEPT ALL SELECT {partition},list({rank} ORDER BY {rank}) ranks FROM pred GROUP BY ALL))"
    z['tie_permutations'].append(dict(sql=sql,difference_groups=c.execute(sql).fetchone()[0]))
  else:
   group='invoice_id,line_item_id' if 'invoice_line' in t else 'report_month,pl_category,account_code'
   sql=f'SELECT count(*) FROM (SELECT {group} FROM pred GROUP BY ALL HAVING count(*)>1)';z['tie_groups']={'sql':sql,'count':c.execute(sql).fetchone()[0]}
 record(z)
# Gold key/contract mismatch: whole gold SQL executes correctly but compound changes can be masked.
for t in ['stg_social_media__account_history','tiktok_ads__ad_report','tiktok_ads__url_report','stg_zuora__invoice_payment']:
 r=next(x for x in inv if x['table']==t);d=json.loads((ROOT/r['full_json']).read_text());b=d['differences'];rr=json.loads((REC/f"024_reruns_{r['task']}_{t}.json").read_text());a=(ROOT/rr['runs'][0]['sql_path']).read_text();ps=next(p['patches'] for p in json.loads((REC/'024_patch_plan.json').read_text()) if p['table']==t)
 use=[p for p in ps if p['label'] in {'id_type','id_filter','timezone_filter','campaign_projection','ad_group_projection','advertiser_join','ads_source_join','adgroup_source_join','campaign_source_join'} or p['label'].startswith('source_')]
 if t=='stg_zuora__invoice_payment':
  # output primary key mapping in gold refers invoice_id rather than raw id; inspect independently, do not claim a valid repair.
  pass
 for p in use:
  for old,new in p['edits']:assert a.count(old)==1;(None);a=a.replace(old,new,1)
 z=dict(task=r['task'],table=t,kind='诊断',label='多处组合仅诊断（不用于单点原因排名）',labels=[p['label'] for p in use],sql=a,database=rr['source'])
 try:
  with duckdb.connect(str(ROOT/'data/024_diagnostics'/('diagnostic_'+t+'.duckdb'))) as c:
   c.execute('SET threads=2');c.execute("ATTACH '"+rr['source']+"' AS src (READ_ONLY)");c.execute('USE src');c.execute("ATTACH '"+b['gold_database']+"' AS gold (READ_ONLY)") if rr['source']!=b['gold_database'] else None;c.create_function('tolerance_forms',udf_forms,['VARCHAR'],duckdb.struct_type({'l1':'VARCHAR','l2':'VARCHAR','l3':'VARCHAR'}));c.execute('CREATE TEMP TABLE pred AS '+a.strip().rstrip(';'));z['comparison']=compare_sql(c,'pred',('gold.' if rr['source']!=b['gold_database'] else 'src.')+b['actual_schema']+'.'+t,b)
 except Exception as e:z['error']=str(e)
 record(z)
print(len(out))
