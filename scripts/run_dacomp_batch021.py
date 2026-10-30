from annotate_dacomp_batch021 import *
from review_dacomp_batch021 import pkg
for r in json.loads((REC/'021_patch_plan.json').read_text()):
 i=r['index']
 if len(sys.argv)>1 and str(i) not in sys.argv[1:]:continue
 p=pkg(i);date=p['differences'].get('candidate_date') or '2025-10-12'
 rerun(int(r['task'][-3:]),[(x['label'],x['edits']) for x in r['patches']],clock=date+' 00:00:00+00',pkg=p)
