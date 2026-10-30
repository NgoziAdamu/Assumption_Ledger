"""Read relevant original material excerpts, never execute trace commands."""
import json,sys,re
from pathlib import Path
R=Path(__file__).resolve().parents[1]
for r in json.loads((R/'records/023_package_inventory.json').read_text()):
 if int(r['task'][-3:]) not in list(map(int,sys.argv[1:])):continue
 d=json.loads((R/r['full_json']).read_text());t=r['table'];print('\nTABLE',t)
 for b in d['contract_specification']['blocks']:
  s=b['original_text']; i=s.find('      business_logic:');j=s.find('\n      columns:',i)
  print('CONTRACT',s[i:j] if i>=0 else s)
 print('AGENT',d['agent_final_SQL'][0]['text'])
