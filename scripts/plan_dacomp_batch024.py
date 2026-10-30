"""Explicit per-location counterfactuals; original bytes outside each edit are preserved."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1];REC=ROOT/'records'
inv=json.loads((REC/'024_package_inventory.json').read_text());plans=[]
def pkg(t):return json.loads((ROOT/next(r['full_json'] for r in inv if r['table']==t)).read_text())
def start(t):
 global p,a,g,d
 d=pkg(t);a=d['agent_final_SQL'][0]['text'];g=d['gold_SQL_仅供定位差异'][0]['text'];p={'task':d['basic_information']['task'],'table':t,'patches':[]};plans.append(p)
def add(label,old,new,cat,why,P=None):
 assert a.count(old)==1,(p['table'],label,a.count(old),old)
 p['patches'].append(dict(label=label,edits=[[old,new]],category=cat,reason=why,P=P))
def line(label,contains,new,cat,why):
 old=next(l.strip().rstrip(',') for l in a.splitlines() if contains in l);add(label,old,new,cat,why)
# impl030: entity identifiers are deliberately over-generalized in event45, not merged by generator.
for r in inv:
 if r['task']!='impl-030':continue
 start(r['table'])
 if r['layer']=='staging':
  for c in d['differences']['column_details']:
   col=c['column'];z=c['l0_counts_verbatim']
   # Include key columns too, even where all rows have exclusive keys.
   old=f'try_cast("id" AS VARCHAR) AS {col}'
   if old in a and col!=r['table'].replace('stg_zuora__','')+'_id':
    add('source_'+col,old,f'try_cast("{col}" AS VARCHAR) AS {col}','A','把本实体 id 当作 '+col+'；契约未给源列映射，按可见数据关系另核 U。','本实体 id 可以代表 '+col)
   elif z['mismatch_rows_or_minimum_pairs'] or z['pred_unmatched_value_occurrences'] or z['gold_unmatched_value_occurrences']:
    m=re.search(r'try_cast\("'+re.escape(col)+r'" AS [^\n]+?\) AS '+re.escape(col)+r'\b',a)
    if m:add('type_'+col,m.group(),f'"{col}" AS {col}','O','agent 按契约声明类型转换；gold 保留 raw 字符串或其他类型。仅诊断为匹配 gold 放宽该处类型，不建议修改契约。')
 elif r['table']=='zuora__account_overview':add('invoice_items_left','JOIN intermediate.int_zuora__invoice_item_base AS ii','LEFT JOIN intermediate.int_zuora__invoice_item_base AS ii','C','契约明确有invoice但无item时计数0；INNER JOIN删掉该账户分组。')
 else:
  add('spine_null_month','    WHERE service_start_day IS NOT NULL','    WHERE TRUE','C','契约要求输出spine的每个account/month；额外过滤NULL月份丢一行。')
  add('items_null_month','    WHERE ii.service_start_day IS NOT NULL','    WHERE TRUE','C','分类输入另有一个非空日期过滤，独立检验其贡献。')
# Twitter
for t in ['twitter_ads__promoted_tweet_report','twitter_ads__url_report']:
 start(t)
 if 'promoted' in t:add('currency_source','li.currency','c.currency','C','契约 currency 明确来自 campaigns。')
 else:add('campaign_projection','a.account_name, li.campaign_id','a.account_name, c.campaign_id','C','契约 campaign_id 明确来自匹配后的 campaigns。')
start('stg_twitter_ads__account_history')
line('timezone_trim','case when timezone in',"case when trim(timezone) in ('America/Los_Angeles','America/New_York','Europe/London','Asia/Tokyo','Australia/Sydney','UTC') then trim(timezone) else 'UTC' end as timezone",'A','无效timezone的correct未定义trim还是fallback UTC；合法原值带空白。')
start('stg_twitter_ads__tweet')
line('language_normalize','case when lang in',"case when lower(trim(lang)) in ('en','es','fr','de','ja','zh','ar','pt','ru','ko') then lower(trim(lang)) else null end as language",'O','契约规定不在枚举则null，gold先lower/trim接受本应不合枚举的原值。')
for suffix in ['campaign_regions_report','campaign_report','line_item_keywords_report','line_item_report','promoted_tweet_report']:
 start('stg_twitter_ads__'+suffix)
 add('date_type','try_cast(date as timestamp) as date_day','cast(date as date) as date_day','O','契约TIMESTAMP，留存gold为DATE；键列日期/午夜时间字符串也按评测键原样比较。')
 for col,typ in [('conversion_purchases_metric','bigint'),('conversion_custom_metric','bigint'),('conversion_purchases_sale_amount','double'),('conversion_custom_sale_amount','double')]:add(col,f'cast(null as {typ}) as {col}',f'cast(0 as {typ}) as {col}','A','原始源没有该指标，契约未规定0或NULL。')
 if suffix=='line_item_keywords_report':add('keyword_id','keyword as keyword_id',"md5(account_id || '-' || line_item_id || '-' || coalesce(keyword,'') || '-' || coalesce(placement,'')) as keyword_id",'A','契约未规定 keyword_id 推导规则，raw无该列；keyword文本与组合MD5是未定选择。')
start('stg_twitter_ads__line_item_history')
for col,new in [('bid_amount_local_micro','bid_amount_local_micro'),('bid_amount','round(bid_amount_local_micro / 1000000.0, 2)'),('total_budget_amount_local_micro','total_budget_amount_local_micro'),('total_budget_amount','round(total_budget_amount_local_micro / 1000000.0, 2)')]:line(col,' as '+col+',',new+' as '+col,'O','agent遵守契约类型，gold使用DOUBLE/两位小数。')
# Twilio
for suffix in ['incoming_phone_number','message']:
 start('stg_twilio__'+suffix)
 cols=[('phone_number','phone_number_normalized')] if suffix=='incoming_phone_number' else [('"from"','from_normalized'),('"to"','to_normalized')]
 for col,alias in cols:
  line(alias,' as '+alias+',',col+' as '+alias,'C','契约失败动作是nullify；agent预先去标点补+1，使不合法原值变成合法电话。')
 if suffix=='incoming_phone_number':add('friendly_trim','then friendly_name','then trim(friendly_name)','A','契约验证TRIM后的文本，但未明确输出是否trim；gold输出trim。')
# TikTok marts
for t in ['tiktok_ads__ad_report','tiktok_ads__url_report']:
 start(t)
 if 'ad.campaign_id,' in a:add('campaign_projection','ad.campaign_id,','c.campaign_id,','C','契约输出campaign_id来自匹配campaigns，非ads外键。')
 if 'ad.ad_group_id,' in a:add('ad_group_projection','ad.ad_group_id,','ag.ad_group_id,','C','契约输出ad_group_id来自匹配ad_groups。')
 if 'on ag.advertiser_id' in a:add('advertiser_join','on ag.advertiser_id = a.advertiser_id','on ad.advertiser_id = a.advertiser_id','C' if 'url' in t else 'A','URL契约规定ads.advertiser_id；ad_report契约只说匹配advertiser_id未明确来源。')
 if t=='tiktok_ads__url_report':
  add('adgroup_source_join',' and ad.source_relation = ag.source_relation','','C','契约url连接仅ad_group_id；额外source关系限制。')
  add('campaign_source_join',' and ad.source_relation = c.source_relation','','C','契约url连接仅campaign_id；额外source关系限制。')
 add('ads_source_join',' and h.source_relation = ad.source_relation','','C','契约首个ads连接仅ad_id；额外source_relation条件单独检验。')
# TikTok staging inspect actual scalar projections as independent locations, no bundle
for t in ['stg_tiktok_ads__ad_group_history','stg_tiktok_ads__ad_history']:
 start(t)
 add('source_relation',"'tiktok_ads' as source_relation",("'raw.tiktok_adgroup_history_data'" if 'ad_group' in t else "'raw.tiktok_ad_history_data'")+" as source_relation",'A','契约未规定source_relation常量字面量；gold使用raw表名。')
 if 'ad_group' in t:
  for col,pos in [('interest_category',56),('languages',67),('budget',38)]:
   old=next(l.strip().rstrip(',') for l in a.splitlines() if l.rstrip().endswith(' as '+col+','))
   new=f'split_part(record, \',\', {pos})'
   if col=='budget':new='try_cast('+new+' as DOUBLE)'
   add(col,old,new+' as '+col,'O','agent按原始header位置取对应字段；gold取其他位置。需数据与header诊断，不把gold位置当作业务真值。')
 else:
  for col in ['base_url','url_path']:
   old=next(l.strip().rstrip(',') for l in a.splitlines() if l.rstrip().endswith(' as '+col+','));new=next(l.strip().rstrip(',') for l in g.splitlines() if l.rstrip().endswith(' as '+col+','));new=new.replace("split_part(row_str, ',', 15)","trim(both '\"' from list_extract(regexp_extract_all(record, '(^|,)(\"(?:[^\"]|\"\")*\"|\\[[^\\]]*\\]|[^,]*)', 2), 15))")
   add(col,old,new,'A','契约未规定URL拆解算法与缺失值表示；gold的base_url保留query且path额外前缀/。')
# Xero
start('stg_xero__invoice_line_item')
for col in ['discount_rate','line_amount','quantity','tax_amount','unit_amount']:
 add(col,f'TRY_CAST({col} AS DECIMAL(18, 2)) AS {col}',f'{col} AS {col}','O','契约DECIMAL(18,2)；gold保留DOUBLE，字符串精度表示不同。')
start('stg_xero__journal')
add('processed_at','NULL::TIMESTAMP AS processed_at','current_timestamp AS processed_at','A','raw无processed_at，契约只声明TIMESTAMP；NULL或执行时间未规定。')
add('created_date_type','TRY_CAST(created_date_utc AS TIMESTAMP) AS created_date_utc','created_date_utc AS created_date_utc','O','契约TIMESTAMP，gold原样VARCHAR。')
add('journal_date_type','TRY_CAST(journal_date AS TIMESTAMP) AS journal_date','journal_date AS journal_date','O','契约TIMESTAMP，gold原样VARCHAR。')
start('xero__invoice_line_items')
for col,expr in [('gross','line_amount_nonneg'),('net','line_net_of_tax')]:
 add('sum_'+col,f'sum({expr}) OVER (PARTITION BY invoice_id)',f'(SELECT sum(s.{expr}) FROM standardized s WHERE s.invoice_id=standardized.invoice_id)','O','窗口SUM与分组SUM浮点累加顺序造成末位差异；诊断比较容差及改写。')
start('xero__profit_and_loss_report')
add('window_frame','ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW','RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW','O','契约允许并列项任意序，但gold默认RANGE同键整组累加；agent ROWS逐行累加。需诊断其余内容一致。')
# social media
start('social_media_reporting__twitter_posts_reporting');add('created_timestamp','min(tweet_created_at)','min(date)','C','契约明确组内earliest date；agent用了推文创建时间。')
start('social_media_reporting__youtube_videos_reporting');add('page_name','coalesce(channel_title,','coalesce(page_name,','A','契约channel title与上游两个名称列未明确对应；gold用page_name。');add('impressions','coalesce(impressions, 0)::bigint as impressions','coalesce(clicks, 0)::bigint as impressions','C','契约impressions与clicks均来自views/clicks。')
start('social_media_reporting__retention_kpis');add('cohort_date_type',"date_trunc('week', created_timestamp)::date as activity_week","date_trunc('week', created_timestamp) as activity_week",'O','契约cohort_week为DATE，gold为TIMESTAMP；此处首个UNION决定活动周类型，其他UNION转型检查。');add('null_page','    where page_id is not null','    where true','C','契约只过滤缺失created_timestamp；额外删除null page_id。')
start('social_media_reporting__rollup_report')
# tie-order diagnostic requires no logical edit
start('stg_social_media__account_history');add('id_type','try_cast(id as bigint) as id','id as id','O','契约BIGINT而gold保留VARCHAR的非数值键。');add('id_filter','where try_cast(id as bigint) is not null','where true','O','契约id非空与BIGINT，gold保留不能转为数值的ID。');add('timezone_filter',"  and regexp_matches(timezone, '^[A-Z][a-z]+/[A-Z][a-z_]+$')",'','O','契约要求无效timezone删行；gold对部分无效值置空或白名单保留。')
start('stg_social_media__linkedin_posts');add('created_source','h.created_time::timestamp','o._fivetran_synced::timestamp','A','契约未定created_timestamp源列；gold同步时间，agent历史created_time。');add('message_source','coalesce(pc.article_title, pc.media_title, h.commentary)::varchar',"concat('LinkedIn Post ',o.ugc_post_id)::varchar",'A','契约未规定post_message内容来源。');add('content_type','pc.type::varchar',"'text'::varchar",'A','契约未规定content_type常量或内容表来源。')
start('stg_social_media__twitter_organic_tweets')
add('tweet_join_account','t.tweet_id\n','t.tweet_id and o.account_id = (select any_value(account_id) from raw.tweet tx where try_cast(tx.id as bigint)=t.tweet_id)\n','C','契约tweet join按organic_tweet_id与account_id；单独补账户约束。')
add('user_join_source','u.id = o.account_id','u.id = (select any_value(user_id) from raw.tweet tx where try_cast(tx.id as bigint)=t.tweet_id)','C','契约需经tweet.user_id读取用户资料。')
add('user_latest',' and u.row_num = 1','','A','契约没有规定取最新还是保留history全部版本。')
add('screen_clean',"regexp_replace(u.screen_name, '[^A-Za-z0-9_]', '', 'g')",'u.screen_name','C','本表契约screen_name直接来自raw用户表；agent额外清洗。')
start('stg_social_media__twitter_user_history');add('screen_regex',"regexp_replace(screen_name, '[^A-Za-z0-9_]', '', 'g')","regexp_replace(screen_name, '[^A-Za-z0-9_]', '')",'C','契约可执行regexp_replace未指定g，agent改为全局。');add('harmful_filter','from raw.twitter_user_history',"from raw.twitter_user_history where NOT REGEXP_MATCHES(screen_name, '[!@#$%^&*()+=<>?}{|,]')",'C','契约要求含有害字符行删除；agent先清洗再保留。');add('empty_filter',"  and screen_name <> '' ",'','A','清洗后空串是否删行与规则先后未明确，gold保留。')
start('stg_social_media__youtube_videos')
add('channel_relation','select channel_id, max(channel_subscribers) as channel_subscribers\n    from raw.youtube_channel_basic\n    group by channel_id','select distinct channel_id, channel_display_name, channel_subscribers\n    from raw.youtube_channel_basic','A','契约未定同channel多个资料版本如何选；gold DISTINCT原三列。')
add('channel_title',"v.snippet_channel_title::varchar as channel_title","coalesce(v.snippet_channel_title, 'Unknown Channel')::varchar as channel_title",'A','契约未明确channel_title缺失时填Unknown。')
add('page_name',"coalesce(v.snippet_channel_title, 'Unknown Channel')::varchar as page_name","(select max(channel_display_name) from raw.youtube_channel_basic cb where cb.channel_id=v.snippet_channel_id)::varchar as page_name",'A','page_name没有明确源列映射，gold取channel_display_name。')
add('estimated_shares','floor(v.statistics_like_count / 10.0)::bigint','cast(v.statistics_like_count / 10.0 as bigint)','O','契约明确FLOOR，gold用CAST四舍五入。')
add('engagement_shares','floor(v.statistics_like_count / 10.0) else 0 end','v.statistics_like_count / 10.0 else 0 end','O','契约engagement使用estimated_shares，gold此处未FLOOR。')
start('int_youtube__video')
for kind in ['default','medium','high']:
 old=next(l.strip().rstrip(',') for l in a.splitlines() if 'regexp_extract(video_thumbnails' in l and ' as '+kind+'_thumbnail_url' in l)
 add(kind+'_regex',old,old.replace('\\\\','\\'),'I','regex显式意图匹配JSON的空白/花括号，但SQL原文双反斜杠匹配了字面反斜杠。')
 add(kind+'_missing',f"nullif({kind}_thumbnail_url, '') as {kind}_thumbnail_url",f'{kind}_thumbnail_url as {kind}_thumbnail_url','O','契约缺section/url返回NULL，gold split_part缺失返回空串。')
add('published_type','snippet_published_at::date as snippet_published_at','snippet_published_at as snippet_published_at','C','契约其余列原样透传，agent强制DATE。')
for p in plans:
 for x in p['patches']:assert len(x['edits'])==1
(REC/'024_patch_plan.json').write_text(json.dumps(plans,ensure_ascii=False,indent=2)+'\n')
print(len(plans),sum(len(p['patches']) for p in plans))
