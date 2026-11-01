"""Collect already-retained inputs only. No model calls or network."""
from pathlib import Path
import json,re,hashlib
R=Path(__file__).resolve().parents[2]
def read(p):return json.loads((R/p).read_text())
def write(p,x):(R/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
scope=read('records/037_scope.json')['objects'];events={};deliveries={}
for task in sorted({x['task'] for x in scope}):
 root=R/f'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/{task}/agent'
 ev=[]
 for p in sorted(root.glob('.events/sessions/*/events/*.json'),key=lambda p:int(p.stem)):
  x=json.loads(p.read_text());ev.append({'path':str(p.relative_to(R)),**{k:x[k] for k in ['id','action','args','content','message','observation'] if k in x}})
 events[task]=ev
 finish=next(x for x in ev if x.get('action')=='finish')
 sql=[]
 for p in sorted(root.glob('dacomp-de-impl-*/sql/**/*.sql')):
  comments=[{'line':i,'text':l} for i,l in enumerate(p.read_text().splitlines(),1) if '--' in l or '/*' in l or '*/' in l]
  sql.append({'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'comments':comments})
 deliveries[task]={'event':finish['id'],'path':finish['path'],'report':finish['args']['final_thought'],'report_sha256':hashlib.sha256(finish['args']['final_thought'].encode()).hexdigest(),'sql_files':sql,'contract_read_commands':[{'event':e['id'],'command':e['args'].get('command','')} for e in ev if e.get('action')=='run' and 'data_contract' in e['args'].get('command','')]}
cat={}
for o in scope:
 task=o['task'];table=o['table'];id=task+'_'+table
 s=(R/f'records/019_packages/019_{id}.md').read_text()
 contract=s.split('```yaml\n',1)[1].split('```',1)[0].rstrip()
 sql=s.split('## agent 最终 SQL',1)[1].split('```sql\n',1)[1].split('```',1)[0].rstrip()
 ev=events[task][1];assert ev['id']==1
 observed=[]
 for e in events[task]:
  for field in (['message'] if e['id']==1 else ['content'] if e.get('observation')=='run' else []):
   text=e.get(field,'')
   if not isinstance(text,str): continue
   model_name=re.search(r'- name: (\S+)',contract).group(1)
   marker=re.search(r'(?m)^\s*- name: '+re.escape(model_name)+r'\s*$',text)
   if marker:
    start=marker.start();tail=text[start:];nxt=re.search(r'(?m)^    - name: ',tail[marker.end()-start:]);end=start+(marker.end()-start)+nxt.start() if nxt else len(text)
    observed.append({'path':e['path'],'event':e['id'],'field':field,'block':text[start:end].strip(),'whole_output_truncated':bool(re.search(r'output.*truncated|\[.*truncated',text,re.I))})
 block=observed[0]['block'] if observed else ''
 old=read(f'records/019_reruns_{id}.json')
 cat[id]={**o,'contract':contract,'event_contract':block,'observed_contracts':observed,'event_path':ev['path'],'event':1,'field':'message','contract_package_exact_in_event':contract.strip() in ev['message'],'contract_truncated':bool(re.search(r'output.*truncated|\[truncated',block,re.I)),'sql':sql,'sql_path':next(x['path'] for x in deliveries[task]['sql_files'] if x['path'].endswith('/'+re.search(r'- S4: `([^`]+)`',s).group(1).split('/')[-1])),'rerun_path':f'records/019_reruns_{id}.json','runs':old['runs'],'basis':old['basis'],'clock_control':old.get('clock_control',[]),'source':old['source'],'queries':[q for q in read('records/019_queries.json') if q['task']==task and q['table']==table]}
write('records/037_checks/evidence_catalog.json',cat);write('records/037_checks/delivery_sources.json',deliveries)
# Raw event extracts include only agent artifacts, no raw table rows.
write('records/037_checks/trace_index.json',{task:[{'id':e['id'],'path':e['path'],'action':e.get('action'),'command':e.get('args',{}).get('command',''),'thought':e.get('args',{}).get('thought','')} for e in ev if e.get('action') in ['run','finish']] for task,ev in events.items()})
print('43 contracts:',sum(x['contract_package_exact_in_event'] for x in cat.values()),'exact in event1; truncated:',sum(x['contract_truncated'] for x in cat.values()))
