from annotate_dacomp_batch024 import *
inv=json.loads((REC/'024_package_inventory.json').read_text());out=[]
def q(t,label,sql,db=None):
 r=next(r for r in inv if r['table']==t);d=json.loads((ROOT/r['full_json']).read_text());db=db or d['differences']['gold_database'];z=dict(task=r['task'],table=t,kind='诊断',label=label,sql=sql,database=db)
 try:
  with duckdb.connect(db,read_only=True) as c:
   res=c.execute(sql);z.update(columns=[x[0] for x in res.description],rows=res.fetchall())
 except Exception as e:z['error']=str(e)
 out.append(z);save(REC/'024_diagnostics.json',out)
for t in ['tiktok_ads__ad_report','tiktok_ads__url_report']:
 q(t,'gold各上游source_relation',"SELECT 'hourly' relation,source_relation,count(*) n FROM intermediate.int_tiktok_ads__ad_report_hourly GROUP BY 2 UNION ALL SELECT 'ads',source_relation,count(*) FROM intermediate.int_tiktok_ads__ad_history_latest GROUP BY 2 UNION ALL SELECT 'ad_groups',source_relation,count(*) FROM intermediate.int_tiktok_ads__ad_group_history_latest GROUP BY 2 UNION ALL SELECT 'campaigns',source_relation,count(*) FROM intermediate.int_tiktok_ads__campaign_history_latest GROUP BY 2")
 q(t,'gold输出连接字段非空',f'SELECT count(*) n,count(ad_name) ads,count(advertiser_name) advertisers,count(ad_group_id) groups,count(campaign_id) campaigns FROM marts.{t}')
for t in ['stg_social_media__twitter_organic_tweets','stg_social_media__twitter_user_history','stg_social_media__account_history','stg_xero__journal','stg_tiktok_ads__ad_group_history','stg_zuora__invoice_payment']:
 r=next(r for r in inv if r['table']==t);d=json.loads((ROOT/r['full_json']).read_text());b=d['differences'];case=json.loads((REC/'013_cases.json').read_text())[int(r['task'][-3:])-1]
 for side,db,rel in [('agent',case['agent_database'],'staging.'+t),('gold',b['gold_database'],b['actual_schema']+'.'+t)]:
  cols=['id','followers_count','following_count'] if 'twitter_user' in t else ['date','account_id'] if 'organic_tweets' in t else ['id','timezone'] if 'account_history' in t else ['created_date_utc','journal_date','journal_number'] if 'journal' in t else ['age_groups','budget','source_relation'] if 'ad_group_history' in t else ['invoice_payment_id','account_id','invoice_id','payment_id','payment_method_id']
  q(t,side+'实际类型',f"SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='{rel.split('.')[0]}' AND table_name='{t}'",db)
  q(t,side+'有限差异样例','SELECT '+','.join(cols)+' FROM '+rel+' LIMIT 3',db)
# exact gold SQL replay on its own gold upstreams (diagnostic, not a single-error repair)
for t in ['tiktok_ads__ad_report','tiktok_ads__url_report','stg_tiktok_ads__ad_group_history','stg_social_media__account_history','stg_social_media__twitter_user_history','stg_xero__journal','xero__invoice_line_items','xero__profit_and_loss_report']:
 r=next(r for r in inv if r['table']==t);d=json.loads((ROOT/r['full_json']).read_text());b=d['differences'];rr=json.loads((REC/f"024_reruns_{r['task']}_{t}.json").read_text());g=d['gold_SQL_仅供定位差异'][0]['text']
 for e in rr['clock_control']:g=re.sub(e['pattern'],e['replacement'],g,flags=re.I)
 z=dict(task=r['task'],table=t,kind='诊断',label='gold SQL同gold输入重跑',database=b['gold_database'],sql=g)
 try:
  with duckdb.connect(str(ROOT/'data/024_diagnostics'/('diagnostic_'+t+'.duckdb'))) as c:
   c.execute("SET threads=2; SET memory_limit='1500MB'");c.execute("ATTACH '"+b['gold_database']+"' AS src (READ_ONLY)");c.execute('USE src')
   c.create_function('tolerance_forms',udf_forms,['VARCHAR'],duckdb.struct_type({'l1':'VARCHAR','l2':'VARCHAR','l3':'VARCHAR'}))
   c.execute('CREATE TEMP TABLE replay AS '+g.strip().rstrip(';'));z['comparison']=compare_sql(c,'replay',b['actual_schema']+'.'+t,b)
 except Exception as e:z['error']=str(e)
 out.append(z);save(REC/'024_diagnostics.json',out)
print(len(out))
