import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; REC=ROOT/'records'
def inventory():
 if (REC/'022_package_inventory.json').exists():return json.loads((REC/'022_package_inventory.json').read_text())
 return [{**r,'full_json':f"data/022_packages_work/{r['stem']}/{r['stem']}.json"} for r in json.loads((REC/'022_scope.json').read_text())]
def pkg(i):return json.loads((ROOT/inventory()[i]['full_json']).read_text())
if __name__=='__main__':
 for i in map(int,sys.argv[1:]):
  d=pkg(i);b=d['differences'];print('\nINDEX',i,d['basic_information']['task'],b['table'],b.get('candidate_date'))
  print('CONTRACT\n'+'\n'.join(x['original_text'] for x in d['contract_specification']['blocks']))
  for k in ('agent_final_SQL','gold_SQL_仅供定位差异'):
   print(k)
   for x in d[k]:print('\n'.join(f'{n+1}: {l}' for n,l in enumerate(x['text'].splitlines())))
  print('DIFF',b['prediction_rows'],b['gold_rows'],[(x['column'],x['l0_counts_verbatim']['mismatch_rows_or_minimum_pairs']) for x in b['column_details']])
