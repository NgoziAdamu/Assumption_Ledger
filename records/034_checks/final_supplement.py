from replay import *
run('legal-hard-17',[2,3,4,5],(5,'estimate=round(total_2007*auto_2024/total_2024)','estimate=round(total_2007*.0304)'),label='printed_share_success',prelude="import os,pandas as pd\nbase="+repr(str(ROOT/'data/kramabench/data/legal/input/csn-data-book-2024-csv/CSVs')))
# Counterfactual output calculations using the original rate estimates, separately for estimator and sign.
baseline=[-.006853,-.054269];gold=[.0193,-.002]
r=[]
for name,v in [('baseline',baseline),('sign_only',[-x for x in baseline]),('estimator_only',[-x for x in gold]),('combination',gold)]:
 r.append({'variant':name,'answer':v,'different_elements':sum(a!=b for a,b in zip(v,gold))})
(OUT/'astronomy-easy-6_factorial.json').write_text(json.dumps({'kind':'output calculation diagnostic; rates from original step3 and endpoint_diagnostic','variants':r},indent=2))
(OUT/'final_supplement_summary.json').write_text(json.dumps(results,ensure_ascii=False,indent=2,default=str))
