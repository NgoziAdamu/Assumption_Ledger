from annotate_dacomp_batch014 import *
P={
1:[('allow_null_created', [('opportunity_id IS NOT NULL AND\n              created_at IS NOT NULL','opportunity_id IS NOT NULL')]),('archive_check',[('WHERE _row_num = 1','WHERE _row_num = 1 AND (archived_at IS NULL OR created_at IS NULL OR archived_at >= created_at)')])],
2:[('key_formula',[("md5(concat_ws('|', coalesce(CAST(visitor_id AS VARCHAR), ''), coalesce(CAST(timestamp AS VARCHAR), ''), coalesce(CAST(guide_id AS VARCHAR), ''), coalesce(CAST(account_id AS VARCHAR), '')))","CASE WHEN account_id IS NOT NULL AND guide_id IS NOT NULL AND timestamp IS NOT NULL AND visitor_id IS NOT NULL THEN md5(concat(coalesce(CAST(visitor_id AS VARCHAR), ''), coalesce(CAST(timestamp AS VARCHAR), ''), coalesce(CAST(account_id AS VARCHAR), ''), coalesce(server_name, ''), coalesce(CAST(guide_id AS VARCHAR), ''), coalesce(user_agent, ''), coalesce(remote_ip, ''))) ELSE NULL END")]),('url_rule',[("CASE WHEN url IS NULL THEN NULL ELSE NULLIF(TRIM(CAST(url AS VARCHAR)), '') END","CASE WHEN TRIM(url) = '' THEN NULL WHEN url IS NOT NULL AND url ~ '^https?://' THEN TRIM(url) ELSE NULL END")]),('latitude_range',[("TRY_CAST(latitude AS DOUBLE)","CASE WHEN latitude BETWEEN -90 AND 90 THEN CAST(latitude AS DOUBLE) ELSE NULL END")])],
3:[('rank_neutral',[('row_number() over(partition by customer360_id order by priority) as rank','NULL::BIGINT as rank')])],
4:[('history_key', [('CAST(hash("_fivetran_start", "_fivetran_end") AS VARCHAR)', "concat(id, '_', current_timestamp::varchar)")]),('activity_rule',[('CAST("last_activity_date" AS DATE) AS last_activity_date',"CASE WHEN last_activity_date > CURRENT_DATE OR last_activity_date < DATE '2020-01-01' THEN NULL ELSE CAST(last_activity_date AS DATE) END AS last_activity_date")])],
5:[('campaign_source',[('CAST(campaign_base_campaign AS VARCHAR(20))','CAST(campaign_id AS VARCHAR(20))')]),('spend_type',[('CAST(cost_micros / 1000000.0 AS DECIMAL(15,2))','cost_micros / 1000000.0')]),('conversions_type',[('CAST(conversions AS DECIMAL(10,2))','CAST(conversions AS DOUBLE)')]),('value_type',[('CAST(conversions_value AS DECIMAL(15,2))','CAST(conversions_value AS DOUBLE)')])],
7:[('subscriber_source',[('CAST(subscriber_id_vendor AS VARCHAR)','CAST(promotional_offer_id AS VARCHAR)')]),('marketing_source',[('CAST(subscription_offer_duration AS VARCHAR)','CAST(marketing_opt_in_duration AS VARCHAR)')]),('source_relation', [('CAST(app_apple_id AS VARCHAR) AS source_relation',"'apple_store' AS source_relation")])],
8:[('project_source',[('SELECT pt.task_id, p.project_id,','SELECT pt.task_id, pt.project_id,')]),('id_numeric_order',[("STRING_AGG(project_id, ', ' ORDER BY project_id)","STRING_AGG(project_id, ', ' ORDER BY TRY_CAST(project_id AS BIGINT))")])],
9:[('remove_country_translation', [('CAST(cc.country_code_alpha_2 AS VARCHAR)','CAST(country_region AS VARCHAR)'),('\nLEFT JOIN raw.google_play__country_codes AS cc ON cc.country_code_numeric = country_region','')])],
10:[('deduplicate',[('where guid is not null','where guid is not null\nQUALIFY row_number() over(partition by guid order by updated_at desc nulls last,created_at desc nulls last)=1')]),('created_rule',[("try_strptime(substr(created_at, 1, 19), '%Y-%m-%d %H:%M:%S')", "CASE WHEN created_at IS NOT NULL AND CAST(created_at AS VARCHAR) ~ '^\\d{4}-\\d{2}-\\d{2}' THEN CAST(created_at AS TIMESTAMP) ELSE NULL END")])]
}
# Each Reddit output expression is an independent intervention, with no combined fixes.
expr={
'spend':('DECIMAL(18,2)','CAST(spend AS DECIMAL(18,2))'),
'video_views':('INTEGER',"CAST(COALESCE(video_started, '0') AS INTEGER)"),
'video_view_rate':('DECIMAL(8,4)','CAST(0 AS DECIMAL(8,4))'),
'upvotes':('INTEGER',"CAST(COALESCE(comment_upvotes, '0') AS INTEGER)"),
'downvotes':('INTEGER',"CAST(COALESCE(comment_downvotes, '0') AS INTEGER)"),
'comments':('INTEGER',"CAST(COALESCE(viewer_comments, '0') AS INTEGER)")}
for col in ['shares','saves','post_visits','profile_visits','community_joins','conversions']:expr[col]=('INTEGER','CAST(0 AS INTEGER)')
expr['conversion_value']=('DECIMAL(18,2)','CAST(0 AS DECIMAL(18,2))')
expr['cost_per_video_view']=('DOUBLE',"CASE WHEN CAST(COALESCE(video_started, '0') AS INTEGER)>0 THEN ROUND(spend/CAST(COALESCE(video_started, '0') AS INTEGER),2) ELSE 0 END")
expr['cost_per_conversion']=('DOUBLE','0::DOUBLE')
total="(CAST(COALESCE(comment_upvotes, '0') AS INTEGER)+CAST(COALESCE(comment_downvotes, '0') AS INTEGER)+CAST(COALESCE(viewer_comments, '0') AS INTEGER))"
expr['total_engagements']=('INTEGER',total)
expr['engagement_rate']=('DOUBLE',f'CASE WHEN impressions>0 THEN ROUND(CAST({total} AS DECIMAL)/CAST(impressions AS DECIMAL)*100,4) ELSE 0 END')
P[6]=[(col,[(f'CAST(NULL::{typ} AS {typ}) AS {col}',f'{new} AS {col}')]) for col,(typ,new) in expr.items()]
for col,raw,new in [('click_through_rate','ctr','CASE WHEN impressions>0 THEN ROUND(CAST(clicks AS DECIMAL)/CAST(impressions AS DECIMAL)*100,4) ELSE 0 END'),('cost_per_click','cpc','CASE WHEN clicks>0 THEN ROUND(spend/clicks,2) ELSE 0 END'),('cost_per_thousand_impressions','ecpm','CASE WHEN impressions>0 THEN ROUND(spend/impressions*1000,2) ELSE 0 END')]:P[6].append((col,[(f'TRY_CAST("{raw}" AS DOUBLE)',new)]))
if __name__=='__main__':
 for n in (list(map(int,sys.argv[1:])) or range(1,11)):reruns(n,P[n])
