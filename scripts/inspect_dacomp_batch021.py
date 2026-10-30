"""Print original excerpts; no annotation inference."""
import json,sys
from pathlib import Path
rows=json.loads(Path('records/021_package_inventory.json').read_text())
for i,r in enumerate(rows):
 if len(sys.argv)>1 and str(i) not in sys.argv[1:]:continue
 d=json.loads(Path(r['full_json']).read_text());b=d['differences'];print('\n###',i,r['task'],r['table']);print('rows',b['prediction_rows'],b['gold_rows'],'keys',b['key_columns']);print('DIFF',[(x['column'],x['l0_counts_verbatim']['mismatch_rows_or_minimum_pairs']) for x in b['column_details'] if x['l0_counts_verbatim']['mismatch_rows_or_minimum_pairs']]);
 if len(sys.argv)>1:
  print('CONTRACT', '\n'.join(x['original_text'] for x in d['contract_specification']['blocks']));print('AGENT',d['agent_final_SQL'][0]['text']);print('GOLD','\n'.join(x['text'] for x in d['gold_SQL_仅供定位差异']))
