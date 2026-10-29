from annotate_dacomp_batch017 import *
from diagnose_dacomp_batch017 import runq

def main():
 out=json.loads((REC/'017_diagnostics.json').read_text())
 b=package(26)['differences'];q="SELECT (SELECT data_type FROM information_schema.columns WHERE table_schema='staging' AND table_name='stg_twitter_ads__campaign_locations_report' AND column_name='date_day') AS retained_date_type,typeof(try_cast(date AS TIMESTAMP)) AS cast_type,typeof(date_trunc('day',try_cast(date AS TIMESTAMP))) AS gold_sql_type,count(*) AS row_count FROM raw.twitter_campaign_locations_report_data GROUP BY ALL"
 with duckdb.connect(b['gold_database'],read_only=True) as c:x=runq(c,q)
 out.append(dict(task='impl-026',kind='诊断查询',database=b['gold_database'],**x))
 # Inspect source null dates excluded by the agent but retained by explicit contract OR branch.
 b=package(30)['differences'];cases=json.loads((REC/'013_cases.json').read_text());path=cases[29]['agent_database']
 q="SELECT count(*) AS nondeleted_invalid_created FROM raw.zuora_invoice_data WHERE coalesce(lower(cast(_fivetran_deleted AS VARCHAR)),'false') NOT IN ('true','1','t') AND try_cast(created_date AS TIMESTAMP) IS NULL"
 with duckdb.connect(path,read_only=True) as c:x=runq(c,q)
 p=REC/'017_queries_impl-030.json';qs=json.loads(p.read_text());qs.append(dict(id='V2',kind='核实查询',database=path,executed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),**x));save(p,qs)
 save(REC/'017_diagnostics.json',out);print('final diagnostics',out[-1],x,flush=True)
if __name__=='__main__':main()
