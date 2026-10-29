from annotate_dacomp_batch020 import *
from plan_dacomp_batch020 import pkg,rows
out=[]
def query(i,q,kind='诊断',db=None):
 d=pkg(i);case=json.loads((REC/'013_cases.json').read_text())[int(rows[i]['task'][-3:])-1];path=db or (case['agent_database'] if kind=='核实' else d['differences']['gold_database'])
 with duckdb.connect(path,read_only=True) as c:
  c.execute('SET threads=2')
  x=dict(index=i,task=rows[i]['task'],table=rows[i]['table'],kind=kind,database=path,sql=q)
  try:r=c.execute(q);x.update(columns=[v[0] for v in r.description],result=r.fetchall())
  except Exception as e:x['error']=str(e)
  out.append(x);save(REC/'020_diagnostics.json',out)
query(24,"SELECT count(*) n, count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.google_ads_ad_group_history_data h WHERE h.id=s.id)) id_matches_history, count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.google_ads_ad_group_history_data h WHERE h.id=s.base_ad_group)) base_matches_history,count(DISTINCT id) ids,count(DISTINCT base_ad_group) bases FROM raw.google_ads_ad_group_stats_data s",'核实')
query(24,"SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name='google_ads_ad_group_history_data' ORDER BY ordinal_position",'核实')
refs=['staging.stg_google_play__stats_crashes_overview','staging.stg_google_play__stats_installs_overview','staging.stg_google_play__stats_ratings_overview','staging.stg_apple_store__app_crash_daily','staging.stg_apple_store__app_store_download_standard_daily']
q=' UNION ALL '.join("SELECT '"+ref+"' AS source_table,count(*) duplicate_groups,sum(n-1) extra_rows FROM (SELECT date_day,"+('app_name' if 'apple' in ref else 'package_name')+',count(*) n FROM '+ref+' GROUP BY ALL HAVING count(*)>1)' for ref in refs)
query(32,q,'核实');query(32,q)
query(32,"SELECT count(*) duplicate_groups,sum(n-1) extra_rows FROM (SELECT date_day,app_name,platform,count(*) n FROM intermediate.int_app_health_metrics GROUP BY ALL HAVING count(*)>1)")
query(33,"SELECT table_name,column_name,ordinal_position FROM information_schema.columns WHERE table_schema='intermediate' AND table_name IN ('int_google_play__overview','int_apple_store__overview') ORDER BY table_name,ordinal_position")
query(33,"WITH named AS (SELECT source_relation,date_day,app_platform,app_name,downloads,deletions,page_views,crashes FROM intermediate.int_google_play__overview UNION ALL SELECT source_relation,date_day,app_platform,app_name,deletions AS downloads,downloads AS deletions,page_views,crashes FROM intermediate.int_apple_store__overview) SELECT count(*) residual FROM ((SELECT * FROM named EXCEPT ALL SELECT source_relation,date_day,app_platform,app_name,downloads,deletions,page_views,crashes FROM marts.app_reporting__overview_report) UNION ALL (SELECT source_relation,date_day,app_platform,app_name,downloads,deletions,page_views,crashes FROM marts.app_reporting__overview_report EXCEPT ALL SELECT * FROM named))")
query(35,"SELECT count(*) n,count(*) FILTER(WHERE revenue <> round(revenue)) fractional_gold, min(typeof(revenue)) revenue_type FROM staging.stg_apple_store__financial_stats_subscriptions_country")
query(42,"SELECT count(*) n,count(*) FILTER(WHERE store_listing_conversion_rate IS NULL) null_rates,count(*) FILTER(WHERE store_listing_conversion_rate NOT BETWEEN 0 AND 1) invalid_rates FROM staging.stg_google_play__stats_store_performance_traffic_source")
# Read-only diagnostic comparisons on existing private outputs, excluding only specified columns.
for i,exclude in [(32,['uninstall_rate_7d_avg','installs_30d_sum','crashes_30d_sum','volume_tier']),(34,['roi_expectation'])]:
 d=pkg(i);b=d['differences'];db=WORK/(rows[i]['task']+'_'+rows[i]['table'])/'work.duckdb';bb={**b,'comparison_columns':[x for x in b['comparison_columns'] if x not in exclude]}
 with duckdb.connect(str(db),read_only=True) as c:
  c.execute("ATTACH '"+b['gold_database']+"' AS gold (READ_ONLY)");c.create_function('tolerance_forms',udf_forms,['VARCHAR'],duckdb.struct_type({'l1':'VARCHAR','l2':'VARCHAR','l3':'VARCHAR'}));rel=b['actual_schema']+'.'+b['table'];out.append(dict(index=i,kind='诊断',excluded_columns=exclude,meaning='已有私有重跑与gold在排除列后的比较',comparison=compare_sql(c,rel,'gold.'+rel,bb)))
save(REC/'020_diagnostics.json',out)
