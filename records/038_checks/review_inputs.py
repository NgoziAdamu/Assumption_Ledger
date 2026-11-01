"""Read-only compact review of original material and retained interventions."""
from pathlib import Path
import json,re,sys
R=Path(__file__).resolve().parents[2]
cat=json.loads((R/'records/038_checks/evidence_catalog.json').read_text())
for index in map(int,sys.argv[1:]):
 o=cat[index];id=o['object'];s=(R/o['package']).read_text();contract=s.split('```yaml\n',1)[1].split('```',1)[0];sql=(R/o['agent_sql']).read_text()
 print('\n###',index,id,'\nCONTRACT\n',contract,'\nSQL\n',sql)
 for file in [f'records/020_reruns_{id}.json',f'records/020_resume_reruns_{id}.json']:
  if not (R/file).exists():continue
  d=json.loads((R/file).read_text());print('RUNS',file)
  for run in d['runs']:
   c=run.get('comparison',{}).get('levels',[{}])[0];print(run['label'],c.get('row_scale'),c.get('cell_scale'),'edits',str(run.get('edits'))[:2500] if 'whole_implementation' not in run['label'] else '[whole diagnostic]')
 for q in o['reused_verification_queries_including_failed']:
  row=json.loads((R/q['source']).read_text())[q['json_index']];print('QUERY',q['source'],q['json_index'],row.get('sql'),'RESULT',str(row.get('result',row.get('error')))[:6500])
