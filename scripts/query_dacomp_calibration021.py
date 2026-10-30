from annotate_dacomp_batch021 import *
out=[]
for n,sqls in [(13,["SELECT count(*) n, count(*) FILTER(WHERE revenue_score IS NOT NULL) scored FROM intermediate.int_netsuite2__customer_profitability"]),(30,["SELECT count(*) n, count(*) FILTER(WHERE id IS NOT DISTINCT FROM account_id) id_eq_account, count(*) FILTER(WHERE account_id IN (SELECT id FROM raw.zuora_account_data)) account_fk_matches, count(*) FILTER(WHERE id IN (SELECT id FROM raw.zuora_account_data)) id_fk_matches, count(*) FILTER(WHERE try_cast(created_date AS TIMESTAMP) IS NULL) null_or_unparsable_created FROM raw.zuora_invoice_data"])]:
 case=json.loads((REC/'013_cases.json').read_text())[n-1]
 with duckdb.connect(case['agent_database'],read_only=True) as c:
  for sql in sqls:
   cur=c.execute(sql);out.append(dict(task=f'impl-{n:03}',kind='核实查询',source=case['agent_database'],sql=sql,columns=[x[0] for x in cur.description],rows=cur.fetchall()))
save(REC/'021_calibration_queries.json',out)
