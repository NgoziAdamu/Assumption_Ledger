from annotate_dacomp_batch017 import *
from run_dacomp_batch017 import P
from diagnose_dacomp_batch017 import runq

def main():
 cases=json.loads((REC/'013_cases.json').read_text());n=21;p=REC/'017_queries_impl-021.json';qs=json.loads(p.read_text())
 q="SELECT person_id,source_relation,cast(occurred_at AS DATE) AS event_day,count(*) AS event_count FROM staging.stg_klaviyo__event WHERE person_id IS NOT NULL GROUP BY ALL HAVING count(*)>1 ORDER BY person_id,event_day"
 with duckdb.connect(cases[n-1]['agent_database'],read_only=True) as c:x=runq(c,q)
 x.update(id='V3',kind='核实查询',database=cases[n-1]['agent_database'],executed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());qs.append(x);save(p,qs);print('V3',x,flush=True)
 d=json.loads((REC/'017_diagnostics.json').read_text());q=d[0]['sql'].replace(')) days,',')) AS day_count,');path=package(21)['differences']['gold_database']
 with duckdb.connect(path,read_only=True) as c:x=runq(c,q)
 d.append(dict(task='impl-021',kind='诊断查询',database=path,**x));save(REC/'017_diagnostics.json',d);print('D2',x,flush=True)
 patches=P[26]+[('date_cast',[('try_cast(date as timestamp) as date_day','try_cast(date as date) as date_day')])]
 rerun(26,patches)
if __name__=='__main__':main()
