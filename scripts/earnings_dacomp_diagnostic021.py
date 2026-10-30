from annotate_dacomp_batch021 import *
from review_dacomp_batch021 import pkg
p=pkg(16);case=json.loads((REC/'013_cases.json').read_text())[8];s=p['agent_final_SQL'][0]['text'];q='SELECT count(*) n,'+','.join(f'count(*) FILTER(WHERE {x} IS NULL) {x}_null' for x in ['package_name','sku_id','transaction_date','transaction_type'])+' FROM ('+s+') projected'
with duckdb.connect(case['agent_database'],read_only=True) as c:
 cur=c.execute(q);out=dict(index=16,kind='核实',database=case['agent_database'],sql=q,columns=[x[0] for x in cur.description],result=cur.fetchall());print(out['result']);save(REC/'021_earnings_diagnostic.json',[out])
