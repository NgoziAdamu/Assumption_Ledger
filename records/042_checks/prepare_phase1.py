from pathlib import Path
import json,re,hashlib,collections
R=Path('records');C=R/'042_checks';B=Path('data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01')
def load(p):return json.loads(Path(p).read_text())
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
sc=load(R/'042_scope.json');events={};delivery={}
for t in [f'impl-{i:03}' for i in [9,15,16,17,18,19,20,21,24]]:
 es=[(p,load(p)) for p in sorted((B/t/'agent/.events/sessions').glob('*/events/*.json'),key=lambda p:int(p.stem))];events[t]=es
 finish=[{'path':str(p),'event':e['id'],'text':e['args']['final_thought'],'sha256':sha(p)} for p,e in es if e.get('action')=='finish']
 results=list((B/t/'agent'/('dacomp-de-'+t)).rglob('result.md'))
 delivery[t]={'finish':finish,'event_count':len(es),'result_files':[{'path':str(p),'sha256':sha(p),'matches_finish':p.read_text().strip()==finish[0]['text'].strip()} for p in results], 'rule':'finish.final_thought及留存result.md、交付SQL注释；临时/测试脚本注释不算。'}
save(C/'delivery_sources.json',delivery)
raw=[]
for n in range(15,22):
 t=f'impl-{n:03}';d=load(R/f'013_raw_{t}.json');g=load(R/f'015_raw_{t}.json')
 raw.append({'task':t,'013_source':f'records/013_raw_{t}.json','015_source':f'records/015_raw_{t}.json','013_summary':d['summary'],'changed_tables':[{k:x[k] for k in ['table','different','columns_and_types_equal','row_counts_equal','row_delta_agent_minus_initial']}|{'initial_rows':x['initial']['row_count'] if x['initial'] else None,'agent_rows':x['agent']['row_count'] if x['agent'] else None} for x in d['tables'] if x['different']], '015_comparison_summary':{comp:dict(collections.Counter('different' if x['different'] else 'same' for x in g['comparisons'] if x['comparison']==comp)) for comp in ['gold_vs_initial','gold_vs_agent']}, 'policy': 'agent运行内改动，照常标注；staging用留存raw，CS用gold上游。' if n in [15,16] else '与gold也存在相同加载后变化，照常标注；staging用留存raw，CS用gold上游。' if n in [17,19,20,21] else '013/015未发现raw差异，照常标注。','causal_status':'impl-015 event45明确改加载器，类型改变因果细节仍须逐表核对。' if n==15 else 'impl-016 email行减少的具体步骤及原因未找到；不能从run.py中有CREATE/INSERT就推定删除步骤。' if n==16 else 'benchmark加载步骤造成属于用户背景/解释，015直接证明的是两侧比较，不把解释冒充执行溯源。','limitation':'复用013/015历史检查，本阶段未打开数据库。'})
save(C/'raw_integrity_review.json',raw)
cat=[];old={d['task']+'_'+d['table']:d['category'] for d in load(R/'023_decisions.json')}
queries=load(R/'023_queries.json')
for s in sc['formal']:
 oid=s['object_id'];t=s['task'];pkg=R/f'023_packages/023_{oid}.md';text=pkg.read_text();paths=dict(re.findall(r'^- (S\d+): `([^`]+)`',text,re.M));d=load(paths['S10']);con=d['contract_specification'];blocks=con['blocks'];sql=d['agent_final_SQL'][0];sqltext=Path(sql['path']).read_text();promptp,prompt=next((p,e) for p,e in events[t] if e['id']==1)
 rr=list(R.glob(f'023*reruns_{oid}.json'));runs=[]
 for f in rr:
  rd=load(f)
  runs.append({'path':str(f),'sha256':sha(f),'source':rd.get('source'),'clock_control':rd.get('clock_control'),'runs':[{'label':x['label'],'edits':x.get('edits'),'scales':[{k:a.get(k) for k in ['level','row_scale','cell_scale']} for a in x.get('comparison',{}).get('levels',[])]} for x in rd.get('runs',[])]})
 qs=[{'source':'records/023_queries.json','array_index':j,'label':q.get('label'),'sql':q.get('sql'),'error':q.get('error')} for j,q in enumerate(queries) if q.get('task')==t and q.get('table')==s['table']]
 rawsrc=sorted(set(re.findall(r'\braw\."?([A-Za-z_][A-Za-z_0-9]*)',sqltext,re.I)))
 rawby={x['table']:x for x in load(R/f'013_raw_{t}.json')['tables']}
 rawreview=[{'table':x,'found_in_013':x in rawby,'different':rawby.get(x,{}).get('different'),'columns_types_equal':rawby.get(x,{}).get('columns_and_types_equal'),'row_counts_equal':rawby.get(x,{}).get('row_counts_equal')} for x in rawsrc]
 entry={**s,'status':'pending_formal_annotation','package':str(pkg),'package_sha256':sha(pkg),'full_json':paths['S10'],'contract_path':con['source_path'],'contract_sha256':sha(con['source_path']),'contract_blocks':[{k:b[k] for k in ['start_line','end_line','original_text']} for b in blocks],'contract_matches_original':all(b['original_text'] in Path(con['source_path']).read_text() for b in blocks),'contract_present_in_initial_prompt':all(b['original_text'] in prompt.get('message','') for b in blocks) if blocks else None,'initial_prompt':str(promptp),'agent_sql':sql['path'],'agent_sql_sha256':sha(sql['path']),'sql_matches_package':sqltext.strip()==sql['text'].strip(),'sql_comment_lines':[x for x in sqltext.splitlines() if '--' in x or '/*' in x],'raw_direct_sources':rawreview,'raw_policy':'staging使用agent留存raw；CS上游使用gold。直读raw逐表核对013；间接raw变化不自动归不可评估。','rerun_sources':runs,'verification_queries':qs,'verification_query_count_including_failures':len(qs),'023_old_main':old[oid],'note':'只生成证据索引，不以旧类别/旧点粒度代替v3.2独立标注。'}
 cat.append(entry)
save(C/'evidence_catalog.json',cat)
print('catalog',len(cat),'max query count',max(x['verification_query_count_including_failures'] for x in cat))
print('contract/sql validation',all(x['contract_matches_original'] and x['sql_matches_package'] for x in cat),'prompt presence',collections.Counter(x['contract_present_in_initial_prompt'] for x in cat))
print('missing reruns',[x['object_id'] for x in cat if not x['rerun_sources']])
print('direct raw reviews',[(x['object_id'],x['raw_direct_sources']) for x in cat if any(v['different'] for v in x['raw_direct_sources'])])
print('results',[(t,d['event_count'],[x['matches_finish'] for x in d['result_files']]) for t,d in delivery.items()])
