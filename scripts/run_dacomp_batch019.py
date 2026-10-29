"""Execute explicit per-table, single-cause trials on private copies."""
from annotate_dacomp_batch019 import *
import argparse

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--task');ap.add_argument('--table');ap.add_argument('--baseline',action='store_true');ap.add_argument('--labels');args=ap.parse_args()
 inv=json.loads((REC/'019_package_inventory.json').read_text())
 plans=json.loads((REC/'019_patch_plan.json').read_text()) if (REC/'019_patch_plan.json').exists() else {}
 for r in inv:
  if r['purpose']=='校准' or (args.task and r['task']!=args.task) or (args.table and r['table']!=args.table):continue
  dest=REC/('019_reruns_'+r['task']+'_'+r['table']+'.json')
  if args.baseline and dest.exists():continue
  pkg=json.loads((ROOT/r['full_json']).read_text());patches=[(p['label'],p['edits']) for p in plans.get(r['table'],[])];b=pkg['differences']
  # Date is the historical comparison selection; timestamp read from gold when an output clock is scored.
  clock=(b.get('candidate_date') or ('2025-10-27' if r['task']=='impl-003' else '2025-10-25'))+' 12:00:00+08'
  with duckdb.connect(b['gold_database'],read_only=True) as c:
   cols=[x[0] for x in c.execute('DESCRIBE '+b['actual_schema']+'.'+b['table']).fetchall()]
   for col in ['generated_at','calculated_at']+[x for x in cols if x.endswith('_timestamp')]+['analysis_date','report_date','calculation_date']:
    if col in cols:
     v=c.execute('SELECT "'+col+'" FROM '+b['actual_schema']+'.'+b['table']+' WHERE "'+col+'" IS NOT NULL LIMIT 1').fetchone()
     if v:clock=str(v[0]);break
  try:
   previous=json.loads(dest.read_text()) if args.labels and dest.exists() else None
   if args.labels:patches=[x for x in patches if x[0] in args.labels.split(',')]
   rerun(int(r['task'][-3:]),patches,clock=clock,pkg=pkg)
   if previous:
    current=json.loads(dest.read_text());done={x['label']:x for x in current['runs']}
    current['runs']=[done.pop(x['label'],x) for x in previous['runs']]+list(done.values());save(dest,current)

  except Exception as e:print(r['table'],'FATAL',str(e),flush=True)
if __name__=='__main__':main()
