from rerun_dacomp_fast021 import *
from review_dacomp_batch021 import pkg
for i in map(int,sys.argv[1:]):
 p=pkg(i);plans=next(x['patches'] for x in json.loads((REC/'021_patch_plan.json').read_text()) if x['index']==i)
 if i==35:
  s=p['agent_final_SQL'][0]['text'];plans=[{'label':'comparative_join_multiplicity','edits':[('from marts.jira__issue_enhanced','from (select base.* from marts.jira__issue_enhanced base join marts.jira__issue_enhanced peer on base.project_id=peer.project_id join marts.jira__issue_enhanced peer2 on base.project_id=peer2.project_id) comparative')]}]+plans
 rerun(11,[(x['label'],x['edits']) for x in plans],clock=(p['differences'].get('candidate_date') or '2025-10-13')+' 00:00:00+00',pkg=p)
