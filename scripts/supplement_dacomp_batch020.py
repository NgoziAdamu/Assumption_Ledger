from annotate_dacomp_batch020 import *
from plan_dacomp_batch020 import pkg,rows,oldexpr,goldexpr
import sqlglot
from sqlglot import exp
for i in [0,1,2,3,4,5,6,7,8,9,10,11,12,32,33,34,41,42]:
 if len(sys.argv)>1 and str(i) not in sys.argv[1:]:continue
 d=pkg(i);s=d['agent_final_SQL'][0]['text'];g=d['gold_SQL_仅供定位差异'][0]['text'];patches=[]
 if i in [0,2,3,4,5,6,7,9,12]:
  # whole fallback implementation diagnostics; never a U isolated-edit claim.
  patches=[('whole_implementation_diagnostic',[(s,g)])]
 elif i==1:
  branch=g.split('UNION ALL')[1]
  end='FROM staging.stg_facebook_ads__ad_report'
  patches=[('missing_apple_branch',[(end,end+'\nUNION ALL\n'+branch)])]
  mapping={'clicks':'inline_link_clicks','cost':'spend','interactions':'0','conversions':'0','conversions_value':'0.0','view_through_conversions':'0','cost_per_conversion':'0.0','return_on_ad_spend':'0.0'}
  patches +=[(c,[(oldexpr(d,c),v+' AS '+c)]) for c,v in mapping.items()]
 elif i==8:
  patches=[('google_roas_rounding',[('ROUND(conversions_value / spend, 4)','conversions_value / spend')]),('ctr_platform_fallthrough',[("WHEN base.click_through_rate >= 1.0 THEN 'HIGH'","WHEN base.platform NOT IN ('amazon_ads','google_ads','facebook_ads') AND base.click_through_rate >= 1.0 THEN 'HIGH'"),("WHEN base.click_through_rate >= 0.5 THEN 'MEDIUM'","WHEN base.platform NOT IN ('amazon_ads','google_ads','facebook_ads') AND base.click_through_rate >= 0.5 THEN 'MEDIUM'")])]
 elif i in [10,11]:
  cols=[x['column'] for x in d['differences']['column_details'] if x['l0_counts_verbatim']['mismatch_rows_or_minimum_pairs']]
  patches=[(c,[(oldexpr(d,c),goldexpr(d,c)+' AS '+c)]) for c in cols]
 elif i==32:
  # Explicitly diagnostic: same date peer ordering, not an inferred unique golden tie key.
  patches=[('peer_order_diagnostic',[("ORDER BY date_day ROWS BETWEEN 6", "ORDER BY date_day,installs,uninstalls,crash_count ROWS BETWEEN 6"),("ORDER BY date_day ROWS BETWEEN 29", "ORDER BY date_day,installs,uninstalls,crash_count ROWS BETWEEN 29")]),('gold_sql_diagnostic',[(s,g)])]
 elif i==33:
  patches=[('gold_positional_union_diagnostic',[(s,g)])]
 elif i==34:
  old="CASE WHEN global_avg_clv>500 THEN 'High' WHEN global_avg_clv>200 THEN 'Medium' WHEN global_avg_clv>50 THEN 'Low' ELSE 'Uncertain' END roi_expectation"
  new="CASE WHEN global_avg_clv>500 THEN 'High ROI Expected' WHEN global_avg_clv>200 THEN 'Medium ROI Expected' WHEN global_avg_clv>50 THEN 'Low ROI Expected' ELSE 'ROI Uncertain' END roi_expectation"
  patches=[('gold_roi_labels_diagnostic',[(old,new)])]
 elif i==41:patches=[('gold_rating_policy_diagnostic',[(s,g)])]
 elif i==42:
  old='CASE WHEN store_listing_conversion_rate BETWEEN 0 AND 1 THEN store_listing_conversion_rate ELSE NULL END AS store_listing_conversion_rate'
  patches=[('gold_ratio_diagnostic',[(old,goldexpr(d,'store_listing_conversion_rate')+' AS store_listing_conversion_rate')])]
 date=d['differences'].get('candidate_date') or '2025-10-12';clock=date+' 12:00:00+00'
 if i==11:
  with duckdb.connect(d['differences']['gold_database'],read_only=True) as c:
   clock=str(c.execute('SELECT min(mart_created_at) FROM marts.ad_reporting__monthly_campaign_region_report').fetchone()[0])
 rerun(int(rows[i]['task'][-3:]),patches,clock=clock,pkg=d)
