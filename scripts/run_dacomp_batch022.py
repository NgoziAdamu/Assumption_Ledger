from annotate_dacomp_batch022 import *
from review_dacomp_batch022 import pkg
for r in json.loads((REC/'022_patch_plan.json').read_text()):
 i=r['index']
 if len(sys.argv)>1 and str(i) not in sys.argv[1:]:continue
 p=pkg(i); date=p['differences'].get('candidate_date') or ('2025-10-14' if r['task']=='impl-013' else '2025-10-12');clock=date+' 00:00:00+00'
 if i in [3,9]:
  b=p['differences'];col='health_check_timestamp' if i==3 else 'assessment_timestamp'
  with duckdb.connect(b['gold_database'],read_only=True) as c:clock=c.execute(f"SELECT min({col})::VARCHAR FROM {b['actual_schema']}.{b['table']}").fetchone()[0]
 print('INDEX',i,r['table'],'clock',clock,flush=True)
 try:rerun(int(r['task'][-3:]),[(x['label'],x['edits']) for x in r['patches']],clock=clock,pkg=p)
 except Exception as e:print('FAILED',i,repr(e),flush=True)
