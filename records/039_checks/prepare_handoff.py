"""Read-only preparation; no old labels are converted to v3.2 categories."""
from pathlib import Path
import json,re,hashlib,csv
R=Path('records');C=R/'039_checks'
def load(p):return json.loads(Path(p).read_text())
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
scope=load(R/'039_scope.json');catalog=[];delivery={}
for n in [8,9,10,11,13,30]:
 root=Path(f'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-{n:03}/agent')
 events=[(p,load(p)) for p in sorted(root.glob('.events/sessions/*/events/*.json'),key=lambda p:int(p.stem))]
 finish=[{'path':str(p),'event':e['id'],'field':'args.final_thought','text':e['args']['final_thought'],'sha256':sha(p)} for p,e in events if e.get('action')=='finish']
 files=[{'path':str(p),'sha256':sha(p),'matches_finish':any(p.read_text().strip()==f['text'].strip() for f in finish)} for p in root.rglob('result.md') if p.read_text().strip()]
 comments=[]
 for p in root.rglob('sql/**/*.sql'):
  for i,line in enumerate(p.read_text().splitlines(),1):
   if '--' in line or '/*' in line:comments.append({'path':str(p),'line':i,'text':line})
 delivery[f'impl-{n:03}']={'event_count':len(events),'finish':finish,'result_files':files,'sql_comment_candidates':comments,'note':'impl-011 官方 incomplete 不排除 finish 交付物' if n==11 else ''}
for i,o in enumerate(scope['formal']):
 key=o['task']+'_'+o['table'];p=R/'021_packages'/('021_'+key+'.md');s=p.read_text()
 contract=re.search(r'```yaml\n([\s\S]*?)\n```',s).group(1);sql=re.search(r'## agent 最终 SQL[\s\S]*?```sql\n([\s\S]*?)\n```',s).group(1)
 sources=dict(re.findall(r'- (S\d+): `([^`]+)`',s));ep=next(Path(sources['S13']).glob('*/events/1.json'));prompt=load(ep)['args']['content'];a,b=map(int,re.search(r'S3:(\d+)[–-](\d+)',s).groups());cp=Path(sources['S3']);orig='\n'.join(cp.read_text().splitlines()[a-1:b]);sp=Path(sources['S4'])
 qs=[]
 for f in ['021_queries.json','021_supplement_queries.json','021_earnings_diagnostic.json','021_final_diagnostics.json']:
  for j,q in enumerate(load(R/f)):
   if q.get('index')==i and q.get('kind') in ['核实','核实查询']:qs.append({'source':'records/'+f,'index_in_file':j,'sql':q['sql'],'failed':bool(q.get('error'))})
 rr=[]
 for rp in R.glob('021*reruns_'+key+'.json'):
  d=load(rp);rr.append({'source':str(rp),'sha256':sha(rp),'runs':[{'label':x['label'],'error':x.get('error'),'scales':[{k:v[k] for k in ['level','row_scale','cell_scale']} for v in x.get('comparison',{}).get('levels',[])]} for x in d.get('runs',[])]})
 cat={'object':key,'layer':o['layer'],'package':str(p),'package_sha256':sha(p),'contract_source':str(cp),'contract_lines':[a,b],'contract_matches_original':contract.strip()==orig.strip(),'event_path':str(ep),'complete_contract_present_in_initial_prompt':contract.strip() in prompt,'agent_sql':str(sp),'agent_sql_sha256':sha(sp),'package_sql_matches_delivered':sql.strip()==sp.read_text().strip(),'verification_queries':qs,'reused_verification_query_count':len(qs),'reruns':rr,'annotation_status':'pending'}
 assert all(cat[k] for k in ['contract_matches_original','complete_contract_present_in_initial_prompt','package_sql_matches_delivered']),key
 assert len(qs)<=5
 catalog.append(cat)
save(C/'evidence_catalog.json',catalog);save(C/'delivery_sources.json',delivery)
raw=load(R/'021_raw_diagnosis.json');rawreview=[]
for o in raw['tables']:
 if not o['table'].startswith('stg_') or not o['unevaluable']:continue
 checks=[]
 for q in o['checks']:
  name=q['raw'].split('.')[1];sides={side:{'rows':raw['sides'][side]['tables'][name]['row_count'],'content_hash':raw['sides'][side]['tables'][name]['content_hash'],'columns':raw['sides'][side]['tables'][name]['columns']} for side in ['initial','agent','gold']}
  checks.append({**q,'diagnostic':sides})
 rawreview.append({'object':o['task']+'_'+o['table'],'source':'records/021_raw_diagnosis.json','checks':checks,'status':'已核实原始数据不同；正式逐表说明待第二阶段生成'})
assert len(rawreview)==6;save(C/'raw_integrity_review.json',rawreview)
corrected=[]
for name in ['int_hubspot__owner_performance_metrics','hubspot__sales_performance_dashboard','hubspot__sales_rep_performance']:
 p=R/'021_annotations'/('021_impl-010_'+name+'.md');s=p.read_text();blocks=[]
 for block in re.findall(r'```json\n([\s\S]*?)\n```',s):
  try:d=json.loads(block)
  except json.JSONDecodeError:continue
  if isinstance(d,dict) and 'runs' in d and 'basis' in d:blocks.append(d)
 assert len(blocks)==1,(name,len(blocks));out=C/('025_evidence_impl-010_'+name+'.json');save(out,{'source':str(p),'source_sha256':sha(p),'record':blocks[0]})
 corrected.append({'object':'impl-010_'+name,'source':str(p),'evidence_copy':str(out),'old_label_after_025':'O','CS':'本表SQL仅直接读取gold上游；不得沿raw依赖链扩展不可评估'})
save(C/'fact_corrections.json',{'025':corrected,'026_021_3':{'object':'impl-008_int_asana__project_health_indicators','source':'records/026_Claude全量标注检查台账.md','fact':'关系数或有效任务数未由契约定死；悬空链接查询不能独自证明应该选哪侧计数；需按v3.2重新判断。'}})
print('catalog',len(catalog),'raw',len(rawreview),'025',len(corrected),'finishes',{k:[x['event'] for x in d['finish']] for k,d in delivery.items()})
