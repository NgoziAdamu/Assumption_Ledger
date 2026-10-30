import json,sys,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REC=ROOT/'records';rows=json.loads((REC/'021_scope.json').read_text())
def pkg(i):
 r=rows[i]
 p=ROOT/'data/021_packages_work'/r['stem']/(r['stem']+'.json') if i<40 else next((REC/'012_packages').glob('*'+r['task']+'*.json'))
 return json.loads(p.read_text())
if __name__=='__main__':
 for i in map(int,sys.argv[2:]):
  d=pkg(i);print('\n###',i,rows[i]['table'])
  if sys.argv[1]=='agent':print(d['agent_final_SQL'][0]['text'])
  elif sys.argv[1]=='gold':print(d['gold_SQL_仅供定位差异'][0]['text'])
  elif sys.argv[1]=='contract':print('\n'.join(b['original_text'] for b in d['contract_specification']['blocks']))
