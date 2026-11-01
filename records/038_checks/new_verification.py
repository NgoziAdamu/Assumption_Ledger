"""New agent-visible checks only; no raw values persisted, originals read_only."""
from pathlib import Path
import json,hashlib
import duckdb
R=Path(__file__).resolve().parents[2];C=json.loads((R/'records/038_checks/evidence_catalog.json').read_text())
PLAN=[(18,"SELECT count(*) n, count(*) FILTER(WHERE upper(trim(avg_cpa_currency)) IN ('USD','EUR','GBP','JPY','AUD','CAD')) valid_cpa, count(*) FILTER(WHERE upper(trim(avg_cpt_currency)) IN ('USD','EUR','GBP','JPY','AUD','CAD')) valid_cpt FROM raw.apple_search_ad_group_report_data"),
(23,"SELECT count(*) n,count(*) FILTER(WHERE conversions_value IN ('true','false')) bool_value,count(*) FILTER(WHERE view_through_conversions IN ('true','false')) bool_view FROM raw.google_ads_account_stats_data"),
(30,"SELECT count(*) n,"+','.join(f'''count(*) FILTER(WHERE "{col}" IS NULL) "{col}_null", count(*) FILTER(WHERE "{col}" IS NOT NULL AND try_cast("{col}" AS DOUBLE) IS NULL) "{col}_invalid_numeric", count(*) FILTER(WHERE "{col}" IN ('true','false')) "{col}_bool"''' for col in ['FOLLOWS','LIKES','COMMENTS','SHARES','CTR','COST_PER_CONVERSION'])+" FROM raw.tiktok_campaign_report_hourly_data"),
(31,"SELECT count(*) n, count(*) FILTER(WHERE mobile_conversion_installs_order_quantity IS NOT NULL) candidate_present, count(*) FILTER(WHERE try_cast(mobile_conversion_installs_order_quantity AS BIGINT)=0) candidate_zero FROM raw.twitter_campaign_report_data")]
out=[]
for i,sql in PLAN:
 o=C[i];d=json.loads((R/f'records/020_reruns_{o["object"]}.json').read_text());assert o['remaining_verification_query_budget']>=1
 with duckdb.connect(d['source'],read_only=True) as c:
  z=c.execute(sql);cols=[x[0] for x in z.description];rows=z.fetchall()
 out.append(dict(object=o['object'],kind='核实查询',source=d['source'],read_only=True,sql=sql,columns=cols,result=rows,reused_count=o['reused_verification_query_count'],total_count=o['reused_verification_query_count']+1))
(R/'records/038_checks/new_verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False,indent=2))
