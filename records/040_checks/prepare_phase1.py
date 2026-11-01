from pathlib import Path
import json,csv,hashlib,re
R=Path('records');C=R/'040_checks';B=Path('data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01')
def load(p):return json.loads(Path(p).read_text())
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
sc=load(R/'040_scope.json');dec=load(R/'022_decisions.json');plans=load(R/'022_patch_plan.json')
delivery={};events={}
for t in ['impl-005','impl-027','impl-012','impl-013','impl-014']:
 es=[(p,load(p)) for p in sorted((B/t/'agent/.events/sessions').glob('*/events/*.json'),key=lambda x:int(x.stem))];events[t]=es
 finish=[{'path':str(p),'event':e['id'],'text':e['args']['final_thought'],'sha256':sha(p)} for p,e in es if e.get('action')=='finish']
 result=B/t/'agent'/('dacomp-de-'+t)/'result.md'
 delivery[t]={'finish':finish,'result_path':str(result),'result_sha256':sha(result),'result_matches_finish':result.read_text().strip()==finish[0]['text'].strip(),'event_count':len(es),'rule':'交付物仅finish.final_thought、留存result.md及交付SQL注释；附带测试脚本排除。'}
save(C/'delivery_sources.json',delivery)
cat=[]
for r in dec:
 oid=r['task']+'_'+r['table'];d=load(r['full_json']);con=d['contract_specification'];blocks=con['blocks'];sql=d['agent_final_SQL'][0];sqltext=Path(sql['path']).read_text();es=events[r['task']];promptp,prompt=next((p,e) for p,e in es if e['id']==1)
 rr=R/f'022_reruns_{oid}.json';rd=load(rr)
 qs=[]
 for f in [R/'022_queries.json',R/'022_queries_retry.json']:
  qs += [{'source':str(f),'array_index':j,'label':q.get('label'),'error':q.get('error'),'sql':q.get('sql')} for j,q in enumerate(load(f)) if q['index']==r['index']]
 entry={'object':oid,'index_022':r['index'],'layer':r['layer'],'status':'pending_formal_annotation','package':r['path'],'package_sha256':sha(r['path']),'full_json':r['full_json'],'contract_path':con['source_path'],'contract_blocks':[{k:b[k] for k in ['start_line','end_line','original_text']} for b in blocks],'contract_matches_original':all(b['original_text'] in Path(con['source_path']).read_text() for b in blocks),'contract_absent':not blocks,'complete_contract_present_in_initial_prompt':all(b['original_text'] in prompt['message'] for b in blocks) if blocks else None,'initial_prompt':str(promptp),'agent_sql':sql['path'],'agent_sql_sha256':sha(sql['path']),'package_sql_matches_delivered':sqltext.strip()==sql['text'].strip(),'sql_comment_lines':[x for x in sqltext.splitlines() if '--' in x or '/*' in x],'rerun_source':str(rr),'rerun_sha256':sha(rr),'rerun_summaries':[{'label':x['label'],'edits':x.get('edits'),'scales':[{k:a[k] for k in ['level','row_scale','cell_scale']} for a in x['comparison']['levels']]} for x in rd['runs']],'verification_queries':qs,'verification_query_count_including_failures':len(qs),'clock_control':rd.get('clock_control',[]),'source':rd.get('source'),'022_old_main':r['main'],'note':'旧主要原因只供最后一列存档；patch label与数值只用作待核证据，不自动赋新类别。'}
 cat.append(entry)
save(C/'evidence_catalog.json',cat)
rawdiff=list(csv.DictReader(open(R/'013_raw_differences.csv')));reuse=load(R/'022_raw_reuse_audit.json');raw=[]
for t in ['impl-012','impl-013','impl-014']:
 d=load(R/f'013_raw_{t}.json');raw.append({'task':t,'013_source':f'records/013_raw_{t}.json','013_raw_table_count':len(d['tables']),'013_difference_entries':[x for x in rawdiff if x['task']==t],'013_all_columns_types_and_row_counts_equal':all(x['columns_and_types_equal'] and x['row_counts_equal'] for x in d['tables']),'022_reused_three_side_audit':next(x for x in reuse if x['task']==t),'limitation':'本阶段复用013/015/022历史检查，未重新打开数据库或重新做内容hash；013差异清单的结构/行数检查本身不证明所有值相同。'})
save(C/'raw_integrity_review.json',raw)
corrections=[{'id':'022-1','object':'impl-014_qualtrics__user_cohort_analysis','fact':'026指出gold TRY_CAST解析失败，不能把其失败当数据事实。','stage1_status':'已登记；正式点与主因未定','next':'分别核对解析选择、cohort_month DATE/TIMESTAMP类型、解析成功过滤的贡献；解析选择按v3.2判断，不从022的O沿用。'}, {'id':'022-2','object':'impl-012_marketo__calendar_spine','fact':'finish中“日历延伸至当前日期，并按 lead created date 起算。”仅说明做法；附带测试脚本不算交付物。','stage1_status':'已核读finish原句；正式五档未定','next':'核实此句是否一一对应utils表而非逐lead日历；第1档/第2档按具体覆盖范围判断，过程中写实现不够第3档。'}, {'id':'020-5','object':'impl-013_int_netsuite__transaction_and_reporting_periods','fact':'契约写 multiplier starting_at须截到秒再解释timestamp；022仅改parse_period后可全对齐。','stage1_status':'已核读契约及单改计划；探索证据在场仍待逐段确认','next':'优先按规定算法判断Intent，不直接从解析失败判Data；完成原始事件/重跑引用后才定稿。'}]
save(C/'fact_corrections.json',{'source':'records/026_Claude全量标注检查台账.md','items':corrections})
save(C/'phase1_handoff.json',{'task':'040','phase':'preparation_and_calibration','formal_completed':0,'formal_pending':38,'calibration_completed':2,'calibration_points':5,'sealed':'records/040_calibration_blind_sealed.json','sealed_sha256':sha(R/'040_calibration_blind_sealed.json'),'comparison':'records/040_calibration_comparison.json','comparison_sha256':sha(R/'040_calibration_comparison.json'),'continue_in_same_session':True,'protect':['018–039全部records/notes','docs/标注手册_v3.1.md','docs/标注手册_v3.2.md','040盲标封存件及解盲对比'],'formal_evidence_catalog':'records/040_checks/evidence_catalog.json','pending_work':['逐表读完38张契约、SQL、诊断与原始事件；022旧理由不能替代契约。','customer_credit_risk列说明有always populated；financial_ratios需确认是否有无类别时0的明文，不能把gold的SUM CASE ELSE 0直接称契约。','三个placeholder_mapping组需核实代码意图、点粒度；不能因旧I整体恢复就跳过逐列检查。','核实所有独立点，包括单改只减少格子和被键差遮住的非原因点；必要时补单改。','处理fact_corrections三项，特别cohort解析与类型分开及calendar交付句覆盖。','逐条复用查询保守含失败≤5；新查询如需打开原库必须只读，staging用agent raw。','生成38正式对象及逐点说明，追加校准后最终验证40表；本阶段validation不能当最终通过。','完成报告、commit并push main。'],'execution_boundary':'本阶段没有打开数据库、运行agent、下载数据或改动旧记录。'})
print('catalog',len(cat),'sql/contract matches',all(x['package_sql_matches_delivered'] and x['contract_matches_original'] for x in cat),'max query count',max(x['verification_query_count_including_failures'] for x in cat))
print('contract_in_prompt',[(x['index_022'],x['complete_contract_present_in_initial_prompt']) for x in cat])
print('raw',[(x['task'],x['013_raw_table_count'],len(x['013_difference_entries'])) for x in raw])
