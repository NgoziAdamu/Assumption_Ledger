import json,sys,re
from pathlib import Path
import yaml
for r in json.loads(Path('records/024_package_inventory.json').read_text()):
 if r['task'] not in sys.argv[1:]:continue
 p=json.loads(Path(r['full_json']).read_text()); b=p['differences']; cs=[]
 print('\nTABLE',r['table'],'ROWS',b['prediction_rows'],b['gold_rows'],'KEYS',b['key_columns'])
 for c in b['column_details']:
  z=c['l0_counts_verbatim']
  if not(z['mismatch_rows_or_minimum_pairs'] or z['pred_unmatched_value_occurrences'] or z['gold_unmatched_value_occurrences']):continue
  cs.append(c['column']);print(c['column'],c['agent_actual_type'],c['gold_actual_type'],z['mismatch_rows_or_minimum_pairs'],[(s.get('agent_value'),s.get('gold_value')) for s in c['sample_key_groups'][:1]])
 text=''.join(x['original_text'] for x in p['contract_specification']['blocks']);v=yaml.safe_load(text)[0]
 for c in v.get('columns',[]):
  if c['name'] in cs:print('CONTRACT',c)
 for k in ['business_logic','notes','grain']:
  if k in v:print(k,v[k])
 for typ in ['agent_final_SQL','gold_SQL_仅供定位差异']:
  print(typ)
  for i,l in enumerate(p[typ][0]['text'].splitlines()):
   if any(re.search(r'\b'+re.escape(c)+r'\b',l) for c in cs):print(i+1,l)
