from annotate_dacomp_batch020 import *
from plan_dacomp_batch020 import pkg
plan=json.loads((REC/'020_patch_plan.json').read_text())
for r in plan:
 if len(sys.argv)>1 and str(r['index']) not in sys.argv[1:]:continue
 p=pkg(r['index']);date=p['differences'].get('candidate_date') or '2025-10-12'
 rerun(int(r['task'][-3:]),[(x['label'],x['edits']) for x in r['patches']],clock=date+' 12:00:00+00',pkg=p)
