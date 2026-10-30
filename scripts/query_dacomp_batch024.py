"""Agent-visible aggregate verification (<=5 statements/table), separate gold diagnostics."""
from annotate_dacomp_batch024 import *
inv=json.loads((REC/'024_package_inventory.json').read_text());cases=json.loads((REC/'013_cases.json').read_text());out=[]
def q(r,label,sql,gold=False,db=None):
 d=json.loads((ROOT/r['full_json']).read_text());path=db or (d['differences']['gold_database'] if gold else cases[int(r['task'][-3:])-1]['agent_database'])
 item=dict(task=r['task'],table=r['table'],kind='诊断' if gold else '核实',label=label,sql=sql,database=path)
 try:
  with duckdb.connect(path,read_only=True) as c:
   v=c.execute(sql);item.update(columns=[x[0] for x in v.description],rows=v.fetchall())
 except Exception as e:item['error']=str(e)
 out.append(item);save(REC/'024_queries.json',out)
for r in inv:
 if r['purpose']=='校准':continue
 d=json.loads((ROOT/r['full_json']).read_text());a=d['agent_final_SQL'][0]['text'];refs=sorted(set(re.findall(r'\b(?:FROM|JOIN)\s+(raw\.\w+)',a,re.I)))
 if r['layer']=='staging':
  names=','.join("'"+x.split('.')[1]+"'" for x in refs)
  q(r,'直接raw列名类型',f"SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name IN ({names}) ORDER BY table_name,ordinal_position")
 if r['task']=='impl-030' and r['layer']=='staging':
  ref=refs[0];sqls=[]
  for col in re.findall(r'try_cast\("id" AS VARCHAR\) AS (\w+)',a):
   if col==r['table'].replace('stg_zuora__','')+'_id':continue
   target='raw.zuora_'+col.removesuffix('_id')+'_data'
   # Schema lookup uses prior same statement result; do not silently execute exploratory reads.
   cols=next(x['rows'] for x in out if x['table']==r['table'] and x['label']=='直接raw列名类型')
   if col not in [x[1] for x in cols]:continue
   sqls.append(f"SELECT '{col}' col,count(*) n,count({col}) nonnull,count(*) FILTER(WHERE cast(id as varchar)=cast({col} as varchar)) same_as_id FROM {ref}")
  if sqls:q(r,'本实体id与各外键是否相同',' UNION ALL '.join(sqls))
  # One union statement compares all candidate source columns to the related raw entity ID.
  sqls=[]
  for col in re.findall(r'try_cast\("id" AS VARCHAR\) AS (\w+)',a):
   if col==r['table'].replace('stg_zuora__','')+'_id':continue
   target='raw.zuora_'+col.removesuffix('_id')+'_data'
   sqls.append(f"SELECT '{col}' col,count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM {target} t WHERE cast(t.id as varchar)=cast(s.id as varchar))) chosen_id_matches,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM {target} t WHERE cast(t.id as varchar)=cast(s.{col} as varchar))) named_col_matches FROM {ref} s")
  if sqls:q(r,'候选外键匹配对照',' UNION ALL '.join(sqls))
 if r['table']=='stg_social_media__linkedin_posts':q(r,'UGC历史关联覆盖',"SELECT count(*) n,count(h.id) history_match,count(h.created_time) creation_available,count(o._fivetran_synced) sync_available FROM raw.linkedin_pages_organization_ugc_post o LEFT JOIN raw.linkedin_pages_ugc_post_history h ON o.ugc_post_id=h.id")
 if r['table']=='stg_social_media__twitter_organic_tweets':q(r,'tweet关联/账户与用户ID差异',"SELECT count(*) n,count(t.id) tweet_match,count(*) FILTER(WHERE t.account_id=o.account_id) same_account,count(*) FILTER(WHERE t.user_id=o.account_id) user_equals_account FROM raw.organic_tweet_report o LEFT JOIN raw.tweet t ON try_cast(o.organic_tweet_id AS BIGINT)=try_cast(t.id AS BIGINT)")
 if r['table']=='stg_social_media__youtube_videos':q(r,'频道多版本与两个标题',"SELECT (SELECT count(*) FROM (SELECT channel_id FROM raw.youtube_channel_basic GROUP BY 1 HAVING count(DISTINCT (channel_display_name,channel_subscribers))>1)) duplicate_channels,(SELECT count(*) FROM raw.youtube_video WHERE snippet_channel_title IS NULL) null_title,(SELECT count(*) FROM raw.youtube_video WHERE statistics_like_count>10 AND statistics_like_count%10<>0) fractional_share")
 if r['table']=='stg_social_media__account_history':q(r,'契约键及timezone过滤计数',"SELECT count(*) n,count(try_cast(id AS BIGINT)) numeric_id,count(*) FILTER(WHERE timezone IS NOT NULL AND NOT regexp_matches(timezone,'^[A-Z][a-z]+/[A-Z][a-z_]+$')) invalid_timezone FROM raw.account_history")
 if r['table']=='stg_social_media__twitter_user_history':q(r,'有害字符与全局替换差异',"SELECT count(*) n,count(*) FILTER(WHERE regexp_matches(screen_name,'[!@#$%^&*()+=<>?}{|,]')) harmful,count(*) FILTER(WHERE regexp_replace(screen_name,'[^A-Za-z0-9_]','')<>regexp_replace(screen_name,'[^A-Za-z0-9_]','','g')) multi_invalid FROM raw.twitter_user_history")
 if r['table']=='stg_twitter_ads__account_history':q(r,'timezone空白',"SELECT count(*) n,count(*) FILTER(WHERE timezone<>trim(timezone)) whitespace FROM raw.twitter_account_history_data")
 if r['table']=='stg_twitter_ads__tweet':q(r,'language原值与规范值',"SELECT lang,count(*) n FROM raw.twitter_tweet_data WHERE lang<>lower(trim(lang)) GROUP BY lang")
 if r['table']=='stg_twilio__message':q(r,'两处原始电话格式',"SELECT count(*) n,count(*) FILTER(WHERE regexp_matches(\"from\",'^\\+1[0-9]{10}$')) valid_from,count(*) FILTER(WHERE regexp_matches(\"to\",'^\\+1[0-9]{10}$')) valid_to FROM raw.message_data")
 if r['table']=='stg_twilio__incoming_phone_number':q(r,'原始电话格式与name空白',"SELECT count(*) n,count(*) FILTER(WHERE regexp_matches(phone_number,'^\\+1[0-9]{10}$')) valid_phone,count(*) FILTER(WHERE friendly_name<>trim(friendly_name)) whitespace_name FROM raw.incoming_phone_number_data")
 if r['table']=='zuora__account_overview':q(r,'agent可见有invoice无item的账户',"SELECT count(DISTINCT inv.account_id) accounts FROM intermediate.int_zuora__invoice_base inv LEFT JOIN intermediate.int_zuora__invoice_item_base ii ON inv.invoice_id=ii.invoice_id WHERE ii.invoice_item_id IS NULL")
 if r['table']=='zuora__monthly_recurring_revenue':q(r,'agent可见NULL服务日期',"SELECT count(*) n,count(*) FILTER(WHERE service_start_day IS NULL) missing FROM intermediate.int_zuora__invoice_item_base")
 if r['table']=='int_youtube__video':q(r,'agent可见thumbnail非空',"SELECT count(*) n,count(video_thumbnails) nonnull FROM staging.stg_youtube__video")
 if r['table']=='int_youtube__video':q(r,'CS gold thumbnail解析输入',"SELECT video_id,video_thumbnails FROM staging.stg_youtube__video",True)
 if r['table'].startswith('stg_youtube__'):
  for side in ['initial_database','agent_database']:
   q(r,side+'直接原始表规模', ' UNION ALL '.join(f"SELECT '{ref}' relation,count(*) n FROM {ref}" for ref in refs),True,db=cases[27][side])
  q(r,'gold实际raw表清单',"SELECT table_name FROM information_schema.tables WHERE table_schema='raw' ORDER BY table_name",True)
  # exact rows match initial-agent verified independently, no raw records exported
  cse=cases[27]
  with duckdb.connect(cse['initial_database'],read_only=True) as c:
   c.execute("ATTACH '"+cse['agent_database']+"' AS retained (READ_ONLY)")
   for ref in refs:
    sql=f"SELECT count(*) FROM ((SELECT * FROM {ref} EXCEPT ALL SELECT * FROM retained.{ref}) UNION ALL (SELECT * FROM retained.{ref} EXCEPT ALL SELECT * FROM {ref}))"
    out.append(dict(task=r['task'],table=r['table'],kind='诊断',label='initial-agent逐值差集',sql=sql,rows=c.execute(sql).fetchall(),database=cse['initial_database'],attached_read_only=cse['agent_database']))
   save(REC/'024_queries.json',out)
print(len(out))
