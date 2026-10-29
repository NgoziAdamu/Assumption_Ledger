from annotate_dacomp_batch017 import *
Q={
21:["SELECT person_id,source_relation,cast(occurred_at AS DATE) day,count(*) n FROM staging.stg_klaviyo__event GROUP BY ALL HAVING count(*)>1 ORDER BY n DESC LIMIT 10"],
22:["SELECT count(*) n,count(distinct id) distinct_id,count(distinct subscription_id) distinct_subscription_id,count(*) FILTER(WHERE id IS DISTINCT FROM subscription_id) different_id,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.subscription s WHERE s.id=h.id)) id_matches_subscription,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.subscription s WHERE s.id=h.subscription_id)) fk_matches_subscription,count(*) FILTER(WHERE _fivetran_deleted) deleted FROM raw.subscription_history h"],
23:["SELECT count(*) n,count(*) FILTER(WHERE fan_count IS DISTINCT FROM try_cast(fan_count AS BIGINT)) fractional_fan_count,count(*) FILTER(WHERE _fivetran_deleted) deleted FROM raw.facebook_pages_page_data"],
24:[r"SELECT \"ID\",\"EMAIL\",regexp_matches(lower(trim(\"EMAIL\")), '^[a-z0-9.!#$%&''*+/=?^_`{|}~-]+@[a-z0-9-]+(\.[a-z0-9-]+)*\.[a-z]{2,}$') agent_accept,regexp_full_match(lower(trim(\"EMAIL\")), '^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$') alternative_accept FROM raw.tiktok_advertiser_data WHERE agent_accept IS DISTINCT FROM alternative_accept".replace('\\"','"')],
25:[r"SELECT count(*) n,count(*) FILTER(WHERE regexp_full_match(cast(\"from\" AS VARCHAR),'^\+1[0-9]{10}$')) from_valid_before,count(*) FILTER(WHERE regexp_full_match(cast(\"to\" AS VARCHAR),'^\+1[0-9]{10}$')) to_valid_before,count(*) FILTER(WHERE regexp_full_match(regexp_replace(regexp_replace(cast(\"from\" AS VARCHAR),'[^0-9]','','g'),'^1?([0-9]{10})$','+1\1'),'^\+1[0-9]{10}$')) from_valid_after,count(*) FILTER(WHERE regexp_full_match(regexp_replace(regexp_replace(cast(\"to\" AS VARCHAR),'[^0-9]','','g'),'^1?([0-9]{10})$','+1\1'),'^\+1[0-9]{10}$')) to_valid_after FROM raw.call_data".replace('\\"','"')],
26:["SELECT count(*) n,count(*) FILTER(WHERE try_cast(date AS TIMESTAMP) IS NULL) parse_null,count(*) FILTER(WHERE try_cast(date AS TIMESTAMP) IS DISTINCT FROM cast(try_cast(date AS DATE) AS TIMESTAMP)) not_midnight,min(cast(date AS VARCHAR)),max(cast(date AS VARCHAR)) FROM raw.twitter_campaign_locations_report_data"],
27:["SELECT account_code,count(*) n,count(distinct account_name) names FROM staging.stg_xero__account GROUP BY account_code HAVING count(*)>1 ORDER BY account_code"],
28:[],
29:["SELECT id,start_date,end_date,try_cast(start_date AS DATE) direct_date,try_cast(substr(start_date,1,10) AS DATE) prefix_date FROM raw.schedule_holiday_data WHERE try_cast(start_date AS DATE) IS DISTINCT FROM try_cast(substr(start_date,1,10) AS DATE)"],
30:["SELECT count(*) n,count(*) FILTER(WHERE i.id=i.account_id) id_equal_fk,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data a WHERE a.id=i.account_id)) fk_matches_account,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.zuora_account_data a WHERE a.id=i.id)) invoice_id_matches_account,count(*) FILTER(WHERE try_cast(created_date AS TIMESTAMP) IS NULL) invalid_created FROM raw.zuora_invoice_data i"]}
def main():
 cases=json.loads((REC/'013_cases.json').read_text())
 for n,qs in Q.items():
  path=cases[n-1]['agent_database'];out=[]
  with duckdb.connect(path,read_only=True) as c:
   for i,q in enumerate(qs,1):
    x={'id':f'V{i}','kind':'核实查询','database':path,'sql':q,'executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:r=c.execute(q);x.update(columns=[d[0] for d in r.description],rows=r.fetchall())
    except Exception as e:x['error']=str(e)
    out.append(x)
  save(REC/f'017_queries_impl-{n:03}.json',out);print(n,out,flush=True)
if __name__=='__main__':main()
