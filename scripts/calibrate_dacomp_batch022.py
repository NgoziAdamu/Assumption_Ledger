"""Blind calibration: only 012/013 materials, original databases and event originals."""
from annotate_dacomp_batch022 import *
queries=[]
def q(n,label,sql):
 case=json.loads((REC/'013_cases.json').read_text())[n-1]
 with duckdb.connect(case['agent_database'],read_only=True) as c:
  r=c.execute(sql);queries.append(dict(task=case['task'],label=label,sql=sql,columns=[x[0] for x in r.description],rows=r.fetchall(),database=case['agent_database']))
q(5,'候选列关系核实',"""SELECT count(*) n,count(*) FILTER(WHERE campaign_id=campaign_base_campaign) equal_candidates,
 count(*) FILTER(WHERE campaign_id IN(SELECT id FROM raw.campaign_history_data)) direct_in_history,
 count(*) FILTER(WHERE campaign_base_campaign IN(SELECT id FROM raw.campaign_history_data)) base_in_history FROM raw.ad_group_stats_data""")
q(27,'账号重复和行粒度核实',"""SELECT (SELECT count(*) FROM staging.stg_xero__account) accounts,(SELECT count(distinct account_code) FROM staging.stg_xero__account) codes,(SELECT count(*) FROM staging.stg_xero__invoice_line_item) lines,(SELECT count(distinct line_item_id) FROM staging.stg_xero__invoice_line_item) line_ids""")
save(REC/'022_calibration_queries.json',queries)
rerun(5,[('campaign_column',[('CAST(campaign_base_campaign AS VARCHAR(20))','CAST(base.campaign_id AS VARCHAR(20))')]),('numeric_types',[('CAST(cost_micros / 1000000.0 AS DECIMAL(15,2))','cost_micros / 1000000.0'),('CAST(conversions AS DECIMAL(10,2))','CAST(conversions AS DOUBLE)'),('CAST(conversions_value AS DECIMAL(15,2))','CAST(conversions_value AS DOUBLE)')])],clock='2025-10-12 00:00:00+00')
rerun(27,[('account_duplicates',[('    QUALIFY row_number() OVER (PARTITION BY account_code ORDER BY account_id) = 1','')])])
