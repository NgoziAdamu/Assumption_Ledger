import json,sys
from pathlib import Path
for r in json.loads(Path('records/024_package_inventory.json').read_text()):
 if r['task'] not in sys.argv[1:]:continue
 p=json.loads(Path(r['full_json']).read_text());print('\nTABLE',r['table'])
 print('CONTRACT');print(''.join(b['original_text'] for b in p['contract_specification']['blocks']))
 print('AGENT');print(p['agent_final_SQL'][0]['text']);print('GOLD');print(p['gold_SQL_仅供定位差异'][0]['text'])
