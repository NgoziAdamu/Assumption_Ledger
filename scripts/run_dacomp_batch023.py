"""Execute explicit task023 interventions in private data copies."""
from annotate_dacomp_batch023 import *
inv=json.loads((REC/'023_package_inventory.json').read_text());plans=json.loads((REC/'023_patch_plan.json').read_text())
for p in plans:
 if len(sys.argv)>1 and p['task'] not in sys.argv[1:]:continue
 path=REC/f"023_reruns_{p['task']}_{p['table']}.json"
 if path.exists():continue
 r=next(r for r in inv if r['table']==p['table']);pkg=json.loads((ROOT/r['full_json']).read_text())
 clock=p['clock']
 if p['table']=='greenhouse__application_history':
  b=pkg['differences']
  with duckdb.connect(b['gold_database'],read_only=True) as c:clock=str(c.execute('select max(valid_until) from mart.greenhouse__application_history').fetchone()[0])
  save(REC/'023_history_clock.json',dict(database=b['gold_database'],sql='select max(valid_until) from mart.greenhouse__application_history',clock=clock))
 rerun(int(p['task'][-3:]),[(x['label'],x['edits']) for x in p['patches']],clock=clock,pkg=pkg)
