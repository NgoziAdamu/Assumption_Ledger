"""Mechanical original trace evidence; quotes are reviewed in final decisions."""
from plan_dacomp_batch020 import *
import hashlib
out=[]
for i,r in enumerate(rows):
 d=pkg(i);root=ROOT/'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01'/r['task']/'agent';events=[]
 for p in root.glob('.events/sessions/*/events/*.json'):
  e=json.loads(p.read_text());events.append((p,e))
 events.sort(key=lambda x:x[1]['id']);refs=sorted(set(re.findall(r'\b(?:FROM|JOIN)\s+((?:raw|staging|intermediate)\.[a-zA-Z_0-9]+)',d['agent_final_SQL'][0]['text'],re.I)))
 visible=[];actions=[]
 for p,e in events:
  content=e.get('content','');command=e.get('args',{}).get('command','');names=[r['table']]+[x.split('.')[-1] for x in refs]
  hits=[x for x in names if re.search(r'(?<![\w])'+re.escape(x)+r'(?![\w])',content)]
  if hits:
   visible.append(dict(event=e['id'],cause=e.get('cause'),names=hits,path=str(p.relative_to(ROOT)),characters=len(content),explicit_truncation=bool(re.search(r'Observation truncated|response clipped|output truncated',content,re.I))))
  if any(x in command for x in names):actions.append(dict(event=e['id'],path=str(p.relative_to(ROOT))))
 out.append(dict(index=i,task=r['task'],table=r['table'],events_scanned=len(events),visible=visible,actions=actions))
(REC/'020_trace_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
for x in out:print(x['index'],x['events_scanned'],[(y['event'],y['names'],y['explicit_truncation']) for y in x['visible']])
