"""Fresh per-table dependency diagnosis, all three originals read-only."""
from review_dacomp_batch021 import *
from check_dacomp_gold_raw import inventory,hash_tables
from collections import defaultdict,deque
edges=[json.loads(x) for x in (REC/'015_lineage_edges.jsonl').read_text().splitlines()];back=defaultdict(list)
for e in edges:
 if e['task']=='impl-010':back[e['target']].append(e['source'])
paths={}
for i in range(18,29):
 r=rows[i];target=r['layer']+'.'+r['table'];q=deque([(target,[target])]);seen=set();found={}
 while q:
  node,path=q.popleft()
  if node in seen:continue
  seen.add(node)
  if node.startswith('raw.'):found[node]=list(reversed(path));continue
  q.extend((x,path+[x]) for x in back[node])
 paths[i]=found
names={n.split('.',1)[1] for v in paths.values() for n in v};case=json.loads((REC/'015_cases.json').read_text())[9];sides={}
for side in ['initial','agent','gold']:
 work=ROOT/'data/021_raw'/side
 d=inventory(case[side+'_database'],work);hash_tables(d,names,work);sides[side]={**d,'tables':{k:v for k,v in d['tables'].items() if k in names}}
out=[]
for i,refs in paths.items():
 checks=[]
 for ref,path in refs.items():
  t=ref.split('.',1)[1];values={side:(d['tables'][t]['columns'],d['tables'][t]['row_count'],d['tables'][t]['content_hash']['sha256']) for side,d in sides.items()}
  checks.append({'raw':ref,'path':path,'initial_eq_agent':values['initial']==values['agent'],'gold_eq_initial':values['gold']==values['initial'],'gold_eq_agent':values['gold']==values['agent']})
 out.append({'index':i,'task':rows[i]['task'],'table':rows[i]['table'],'checks':checks,'unevaluable':any(c['initial_eq_agent'] and not c['gold_eq_initial'] for c in checks)})
(REC/'021_raw_diagnosis.json').write_text(json.dumps({'sides':sides,'tables':out},ensure_ascii=False,indent=2)+'\n')
for x in out: print(x['index'],x['table'],x['unevaluable'],[c['raw'] for c in x['checks'] if not c['gold_eq_initial']])
