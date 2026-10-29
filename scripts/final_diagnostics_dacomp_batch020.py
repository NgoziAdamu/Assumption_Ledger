from annotate_dacomp_batch020 import *
from plan_dacomp_batch020 import pkg,rows
out=[]
# Additional fifth verification query for source-id choice; only agent-visible raw.
i=24;case=json.loads((REC/'013_cases.json').read_text())[5];q="SELECT count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.google_ads_ad_group_history_data h WHERE h.id=regexp_extract(s.base_ad_group,'[^/]+$',0))) base_suffix_matches, count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.google_ads_ad_group_history_data h WHERE h.id=s.id)) id_matches FROM raw.google_ads_ad_group_stats_data s"
with duckdb.connect(case['agent_database'],read_only=True) as c:out.append(dict(index=i,kind='核实',database=case['agent_database'],sql=q,result=c.execute(q).fetchall()))
# Exclude every window-derived value; confirm same base row multiset.
i=32;d=pkg(i);b=d['differences'];db=WORK/(rows[i]['task']+'_'+rows[i]['table'])/'work.duckdb';cols=['app_name','platform','crash_count','installs','uninstalls','total_activity','daily_average_rating','total_average_rating','crash_rate_per_thousand','uninstall_rate_percentage'];bb={**b,'comparison_columns':cols}
with duckdb.connect(str(db),read_only=True) as c:
 c.execute("ATTACH '"+b['gold_database']+"' AS gold (READ_ONLY)");c.create_function('tolerance_forms',udf_forms,['VARCHAR'],duckdb.struct_type({'l1':'VARCHAR','l2':'VARCHAR','l3':'VARCHAR'}));rel=b['actual_schema']+'.'+b['table'];out.append(dict(index=i,kind='诊断',comparison_columns=cols,comparison=compare_sql(c,rel,'gold.'+rel,bb)))
i=33;d=pkg(i);b=d['differences'];rel=b['actual_schema']+'.'+b['table'];q=f"WITH named AS (SELECT source_relation,date_day,app_platform,app_name,downloads,deletions,page_views,crashes FROM intermediate.int_google_play__overview UNION ALL SELECT source_relation,date_day,app_platform,app_name,deletions AS downloads,downloads AS deletions,page_views,crashes FROM intermediate.int_apple_store__overview) SELECT count(*) residual FROM ((SELECT * FROM named EXCEPT ALL SELECT source_relation,date_day,app_platform,app_name,downloads,deletions,page_views,crashes FROM {rel}) UNION ALL (SELECT source_relation,date_day,app_platform,app_name,downloads,deletions,page_views,crashes FROM {rel} EXCEPT ALL SELECT * FROM named))"
with duckdb.connect(b['gold_database'],read_only=True) as c:out.append(dict(index=i,kind='诊断',database=b['gold_database'],sql=q,result=c.execute(q).fetchall()))
save(REC/'020_final_diagnostics.json',out)
