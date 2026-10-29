from annotate_dacomp_batch014 import *
QUERIES={
1:["SELECT count(*) n,count(created_at) raw_created_nonnull,count(try_cast(created_at AS TIMESTAMP)) parsed_created_nonnull,count(*) FILTER(WHERE try_cast(archived_at AS TIMESTAMP)<try_cast(created_at AS TIMESTAMP)) inverted,count(distinct id) ids FROM raw.application"],
2:["SELECT count(*) n,count(*) FILTER(WHERE url IS NOT NULL) urls,count(*) FILTER(WHERE url ~ '^https?://') full_regex,count(*) FILTER(WHERE regexp_matches(url,'^https?://')) prefix_regex,count(*) FILTER(WHERE latitude NOT BETWEEN -90 AND 90) invalid_lat,count(*) FILTER(WHERE account_id IS NULL OR guide_id IS NULL OR timestamp IS NULL OR visitor_id IS NULL OR app_id IS NULL) missing_required FROM raw.guide_event"],
3:[],
4:["SELECT count(*) n,count(distinct id) ids,count(*) FILTER(WHERE last_activity_date < DATE '2020-01-01') old_activity,count(*) FILTER(WHERE last_activity_date > DATE '2026-10-25') future_activity,count(*) FILTER(WHERE mobile_phone <> '' AND length(regexp_replace(mobile_phone,'[^0-9]',''))<10) short_mobile,count(*) FILTER(WHERE mailing_postal_code <> '' AND length(trim(mailing_postal_code))<3) short_postal FROM raw.contact_history"],
5:["SELECT count(*) n,count(*) FILTER(WHERE cast(campaign_base_campaign AS VARCHAR) IS DISTINCT FROM cast(campaign_id AS VARCHAR)) different_campaign,count(*) FILTER(WHERE ad_network_type IS NOT NULL AND ad_network_type NOT IN ('SEARCH','DISPLAY','MIXED','YOUTUBE')) invalid_network,count(*) FILTER(WHERE try_cast(date AS DATE)<DATE '2020-01-01' OR try_cast(date AS DATE)>DATE '2026-10-25') outside_date FROM raw.ad_group_stats_data"],
6:["SELECT count(*) n,count(spend) spend_present,count(video_started) video_present,count(comment_upvotes) upvotes_present,count(*) FILTER(WHERE try_cast(ctr AS DOUBLE) IS DISTINCT FROM round(100.0*clicks/nullif(impressions,0),4)) ctr_different FROM raw.reddit_ads_campaign_report_data"],
7:["SELECT count(*) n,count(*) FILTER(WHERE marketing_opt_in_duration IS DISTINCT FROM subscription_offer_duration) durations_differ,count(*) FILTER(WHERE cast(promotional_offer_id AS VARCHAR) IS DISTINCT FROM subscriber_id_vendor) ids_differ,count(marketing_opt_in_duration) marketing_present FROM raw.sales_subscription_event_summary"],
8:["SELECT count(*) n,count(*) FILTER(WHERE p.project_id IS NULL) missing_projects,count(distinct pt.task_id) FILTER(WHERE p.project_id IS NULL) affected_tasks FROM staging.stg_asana__project_task pt LEFT JOIN staging.stg_asana__project p ON pt.project_id::VARCHAR=p.project_id"],
9:["SELECT count(*) n,count(country_region) nonnull_country,count(distinct country_region) countries,(SELECT count(*) FROM raw.google_play__country_codes) code_rows,(SELECT count(distinct country_code_numeric) FROM raw.google_play__country_codes) distinct_codes FROM raw.stats_store_performance_country"],
10:["SELECT count(*) n,count(distinct guid) guids,count(*) FILTER(WHERE guid LIKE 'FORM_%') synthetic_style_ids,min(guid) min_guid,max(guid) max_guid,count(distinct portal_id) portals FROM raw.form_data"]}
def main():
 cases=json.loads((REC/'013_cases.json').read_text());allout=[]
 for n,queries in QUERIES.items():
  pkg=package(n); case=cases[n-1];path=case['agent_database'];out=[]
  with duckdb.connect(path,read_only=True) as c:
   for i,q in enumerate(queries,1):
    row={'id':f'V{i}','kind':'核实查询','database':path,'sql':q}
    try:
     r=c.execute(q);row.update(columns=[x[0] for x in r.description],rows=r.fetchall())
    except Exception as e:row['error']=str(e)
    out.append(row)
  # diagnostic on gold raw; no data availability inference from these queries
  with duckdb.connect(pkg['differences']['gold_database'],read_only=True) as g:
   for i,q in enumerate(queries,1):
    row={'id':f'D{i}','kind':'诊断查询','database':pkg['differences']['gold_database'],'sql':q}
    try:
     r=g.execute(q);row.update(columns=[x[0] for x in r.description],rows=r.fetchall())
    except Exception as e:row['error']=str(e)
    out.append(row)
  save(REC/f'014_queries_impl-{n:03}.json',out);allout.append({'n':n,'queries':out})
 print(json.dumps(allout,ensure_ascii=False,indent=2,default=str))
if __name__=='__main__':main()
