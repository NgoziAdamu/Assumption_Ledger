"""038 准备清单：提取已有证据与原始轨迹；不执行SQL、不打开数据库、不定正式表类别。"""
from pathlib import Path
import json,csv,re,hashlib,collections
R=Path(__file__).resolve().parents[2]
def read(p):return json.loads((R/p).read_text())
def write(p,v):(R/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return str(p.relative_to(R))
scope=read('records/038_scope.json');events={};trace_index={};delivery={}
for task in ['impl-006','impl-007']:
 fs=sorted((R/f'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/{task}/agent/.events').glob('sessions/*/events/*.json'),key=lambda p:int(p.stem))
 events[task]={int(p.stem):(p,json.loads(p.read_text())) for p in fs}
 trace_index[task]=[dict(event=n,path=rel(p),sha256=sha(p),action=d.get('action'),observation=d.get('observation')) for n,(p,d) in events[task].items()]
 finishes=[{'path':rel(p),'event':n,'field':'args.final_thought','text':d['args']['final_thought'],'sha256':sha(p)} for n,(p,d) in events[task].items() if d.get('action')=='finish']
 results=list((R/f'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/{task}/agent').glob('**/result.md'))
 sqls=list((R/f'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/{task}/agent').glob('dacomp-de-impl-*/sql/**/*.sql'))
 comments=[]
 for p in sqls:
  t=p.read_text(); snippets=re.findall(r'--[^\n]*|/\*[\s\S]*?\*/',t)
  if snippets:comments.append(dict(path=rel(p),sha256=sha(p),comments=snippets))
 delivery[task]={'finish':finishes,'result_files':[dict(path=rel(p),sha256=sha(p)) for p in results],'delivered_sql_file_count':len(sqls),'sql_comment_candidates':comments,'note':'SQL注释候选为机械提取，正式逐点判断需再核查语境；不能因有注释就认定披露。'}
 if task=='impl-007':
  delivery[task]['failed_report_attempts']=[{'event':n,'path':rel(events[task][n][0]),'field':'args.command','command':events[task][n][1]['args']['command'],'response_event':n+1,'response_path':rel(events[task][n+1][0]),'response':events[task][n+1][1]['content']} for n in [65,67]]
  delivery[task]['terminal_error']={'path':rel(events[task][69][0]),'event':69,'extras':events[task][69][1]['extras']}
  delivery[task]['disclosure_rule']='无finish、无result.md；两次草稿均未交付，不能作为第1/2档依据。中间意识只有点明疑问/备选/缺失/冲突才可第3档；SQL注释需逐点检查。'
old={r['题目']+'_'+r['表']:r for r in csv.DictReader((R/'records/020_annotations/020_summary.csv').open())}
indexmap={r['index']:r['task']+'_'+r['table'] for r in read('records/020_decisions.json')}
queries=collections.defaultdict(list)
for file in ['records/020_queries.json','records/020_diagnostics.json','records/020_final_diagnostics.json']:
 for i,q in enumerate(read(file)):
  if q.get('kind')!='核实':continue
  id=q.get('task','')+'_'+q.get('table','') if 'table' in q else indexmap[q['index']]
  queries[id].append({'source':file,'json_index':i,'id':q.get('id'),'sql':q['sql'],'error':q.get('error'),'database':q.get('database')})
catalog=[]
for row in scope['formal']:
 task,table,layer=row['task'],row['table'],row['layer'];id=task+'_'+table;file=R/f'records/020_packages/020_{id}.md';t=file.read_text()
 contract=re.search(r'```yaml\n([\s\S]*?)\n```',t).group(1)
 sql=re.search(r'## agent 最终 SQL[\s\S]*?```sql\n([\s\S]*?)\n```',t).group(1)
 p=next((R/f'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/{task}/agent').glob('dacomp-de-impl-*/sql/'+layer+'/'+table+'.sql'))
 ep,ed=events[task][1];full=ed['args']['content'];present=contract.strip() in full
 cs=re.search(r'- S3: `([^`]+)`',t).group(1);csfile=Path(cs);cm=re.search(r'S3:(\d+)[–-](\d+)',t);a,b=map(int,cm.groups());actual='\n'.join(csfile.read_text().splitlines()[a-1:b])
 matches=actual.strip()==contract.strip()
 runs=[]
 for rf in [R/f'records/020_reruns_{id}.json',R/f'records/020_resume_reruns_{id}.json']:
  if not rf.exists():continue
  d=json.loads(rf.read_text())
  for run in d['runs']:
   comp=run.get('comparison',{});runs.append({'source':rel(rf),'label':run['label'],'diagnostic_only':'diagnostic' in run['label'],'edit_count':len(run.get('edits',[])),'scales':[{k:l[k] for k in ['level','agent_rows','gold_rows','row_scale','cell_scale']} for l in comp.get('levels',[])],'sql_sha256':run.get('sql_sha256'),'error':run.get('error')})
 cat={'object':id,'layer':layer,'package':rel(file),'package_sha256':sha(file),'contract_source':cs,'contract_lines':[a,b],'contract_matches_original':matches,'event_path':rel(ep),'event':1,'field':'args.content','complete_contract_present_in_initial_prompt':present,'contract_sha256':hashlib.sha256(contract.encode()).hexdigest(),'agent_sql':rel(p),'agent_sql_sha256':sha(p),'package_sql_matches_delivered':sql.strip()==p.read_text().strip(),'sql_comments':re.findall(r'--[^\n]*|/\*[\s\S]*?\*/',p.read_text()),'020_final_old_main':old[id]['主要原因类别'],'old_label_source':'records/020_annotations/020_summary.csv','reused_verification_queries_including_failed':queries[id],'reused_verification_query_count':len(queries[id]),'remaining_verification_query_budget':5-len(queries[id]),'reruns':runs,'status':'prepared_not_annotated'}
 catalog.append(cat)
assert all(c['contract_matches_original'] and c['complete_contract_present_in_initial_prompt'] and c['package_sql_matches_delivered'] for c in catalog)
assert all(c['remaining_verification_query_budget']>=0 for c in catalog)
write('records/038_checks/evidence_catalog.json',catalog);write('records/038_checks/trace_index.json',trace_index);write('records/038_checks/delivery_sources.json',delivery)
rawdiff=[r for r in csv.DictReader((R/'records/013_raw_differences.csv').open()) if r.get('task') in ['impl-006','impl-007']]
raw={'source':'records/013_raw_differences.csv','matching_rows':rawdiff,'task_summaries':{task:read(f'records/013_raw_{task}.json')['summary'] for task in events},'new_database_queries':0,'interpretation':'复核013已有记录：两题未记录原始表差异；此次没有新查库，不能把这次文件复核说成重新计算全部raw内容hash。'}
assert not rawdiff;write('records/038_checks/raw_integrity_review.json',raw)
p,d=events['impl-006'][27];command=d['args']['command'];assert 'int_ad_reporting__account_report' not in command.split('preserve=')[1].split('\n')[0]
facts={'source':'records/026_Claude全量标注检查台账.md','relevant_lines':[{'line':i,'text':s} for i,s in enumerate((R/'records/026_Claude全量标注检查台账.md').read_text().splitlines(),1) if any(term in s for term in ['impl-006','impl-007','020-','020：'])],'verified_fallback':{'event':27,'path':rel(p),'field':'args.command','command':command,'account_not_in_preserve':True,'status':'事实已核；正式类别尚未判定。不得直接照抄026建议的旧D。'},'next_checks':['staging按候选列逐列区分NULL占位与无对应源列。','Data候选先查契约规定算法，存在明确算法则Intent。','whole_implementation_diagnostic整段替换仅为诊断，不能当作多个独立点的单改。','event19映射字典被覆盖事实须与020_resume单改逐表对应。','impl-007草稿仅可在满足v3.2疑问门槛时用于第3档。']}
write('records/038_checks/fact_corrections.json',facts)
write('records/038_checks/phase1_handoff.json',{'task':'038','phase':'phase1_preparation_and_calibration','task_complete':False,'formal_prepared':43,'formal_annotated':0,'calibration_annotated':2,'remaining_formal_objects':[c['object'] for c in catalog],'continue_number':'038，不另占039，也不因本阶段生成038文件而误判为新任务冲突','immutable_files':['records/038_calibration_blind_sealed.json','records/038_checks/calibration_seal.json','records/038_checks/input_hashes_before.json'],'scripts_not_to_rerun':['records/038_checks/seal_calibration.py'],'next_steps':['读取phase1校准工作行与对比，保留封存件。','以020的10-30定稿及resume实验为来源，逐表逐点判类，旧标签仅原样附列。','复用evidence_catalog中的查询预算；Google ad_group已5条，不能再新增核实查询。','需要时补单点重跑，原库只读，内存/私有副本执行，共同固定时间；用户禁止写数据库，默认使用内存。','向现有CSV追加43正式表；逐表说明写入038_annotations。','将阶段报告改为完整报告；validation task_complete只有45表真正完成后才为true。','检查保护hash、封存hash、引句、范围与各字段一致后commit并push main。']})
print(json.dumps({'catalog_count':len(catalog),'contracts_visible':sum(c['complete_contract_present_in_initial_prompt'] for c in catalog),'verification_query_count_distribution':dict(collections.Counter(c['reused_verification_query_count'] for c in catalog)),'impl007_sql_comment_candidates':len(delivery['impl-007']['sql_comment_candidates']),'impl007_formal_sql_comments':{c['object']:c['sql_comments'] for c in catalog if c['object'].startswith('impl-007') and c['sql_comments']}},ensure_ascii=False))
