from annotate_dacomp_batch014 import *
n=10;p=REC/'014_queries_impl-010.json';out=json.loads(p.read_text());case=json.loads((REC/'013_cases.json').read_text())[9]
paths=[case['initial_database'],case['agent_database'],package(n)['differences']['gold_database']];rows=[]
for path in paths:
 with duckdb.connect(path,read_only=True) as c:
  cols=sorted(r[0] for r in c.execute('DESCRIBE raw.form_data').fetchall());q='SELECT '+','.join('"'+x+'"' for x in cols)+' FROM raw.form_data';rows.append(Counter(c.execute(q).fetchall()))
out.append({'id':'D_input_alignment','kind':'诊断查询','databases':paths,'schema_query':'DESCRIBE raw.form_data','sql':q,'operation':'sort column names, compare full typed row Counters; data not saved','result':{'initial_agent_equal':rows[0]==rows[1],'agent_gold_equal':rows[1]==rows[2],'agent_only':sum((rows[1]-rows[2]).values()),'gold_only':sum((rows[2]-rows[1]).values())}})
save(p,out)
print(out[-1])
