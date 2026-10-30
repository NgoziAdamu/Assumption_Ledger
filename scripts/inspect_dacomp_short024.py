import json,sys,re
from pathlib import Path
for r in json.loads(Path('records/024_package_inventory.json').read_text()):
 if r['task'] not in sys.argv[1:]:continue
 p=json.loads(Path(r['full_json']).read_text());print('\nTABLE',r['table'])
 print('DIFF',p['differences']['prediction_rows'],p['differences']['gold_rows'],[(c['column'],c['l0_counts_verbatim']['mismatch_rows_or_minimum_pairs'],[(s.get('agent_value'),s.get('gold_value')) for s in c['sample_key_groups'][:1]]) for c in p['differences']['column_details'] if c['l0_counts_verbatim']['mismatch_rows_or_minimum_pairs']])
 if '--contract' in sys.argv:print('CONTRACT', ''.join(b['original_text'] for b in p['contract_specification']['blocks']))
 else:
  print('AGENT',p['agent_final_SQL'][0]['text']);print('GOLD',p['gold_SQL_仅供定位差异'][0]['text'])
