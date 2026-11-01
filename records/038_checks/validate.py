"""45表最终验证；逐条回查引句、范围、单点补充实验与保护hash。"""
from pathlib import Path
import json,csv,hashlib,re,collections
R=Path(__file__).resolve().parents[2]
def read(p):return json.loads((R/p).read_text())
def write(p,v):(R/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def rows(p):return list(csv.DictReader((R/p).open()))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
scope=read('records/038_scope.json');formal={r['task']+'_'+r['table'] for r in scope['formal']};cal=set(scope['calibration']);objs=rows('records/038_objects.csv');pts=rows('records/038_points.csv');done={r['对象编号'] for r in objs};audit=read('records/038_checks/disclosure_audit.json');catalog=read('records/038_checks/evidence_catalog.json')
raw={r['task']+'_'+r['table'] for r in rows('records/013_statuses.csv') if r['status']=='待标注' and r['task'] in ['impl-006','impl-007']};pilots={r['对象编号'] for r in rows('records/036_objects.csv')};expected=raw-pilots
levels=['交付物里针对本处说明了','交付物里只有通用说明','过程中意识到了，交付物里没提','看到了相关信息，但没有意识到的迹象','没有迹象']
headers={}
for kind in ['objects','points']:
 with (R/f'records/037_{kind}.csv').open() as f:h=next(csv.reader(f))
 h[-1]='020旧标签'
 with (R/f'records/038_{kind}.csv').open() as f:headers[kind]=next(csv.reader(f))==h
quotes=read('records/038_checks/quote_inventory.json');blind=read('records/038_calibration_blind_sealed.json')
for o in blind['objects']:
 for p in o['points']:
  for q in p['disclosure_evidence']+p['evidence_presence_quotes']:quotes.append({'object':o['对象编号'],'point':p['错误点名称'],'kind':'封存件','source':q['path'],'event':str(q['event'])+'.'+q['field'],'quote':q['quote']})
for r in read('records/038_calibration_comparison.json')['points']:
 if 'delivered_quote' in r:
  q=r['delivered_quote'];quotes.append({'object':r['对象编号'],'point':r['blind_point'],'kind':'解盲对比','source':q['path'],'event':str(q['event'])+'.'+q['field'],'quote':q['quote']})
quotes += read('records/038_checks/formal_quote_inventory.json')
checked=[]
for q in quotes:
 path=R/q['source'];rawtext=path.read_text();v=rawtext
 if q.get('field','') and q['field']!='text':
  v=json.loads(rawtext)
  for k in q['field'].split('.'):v=v[k]
 elif q.get('event') and q['event']!='delivered SQL':
  v=json.loads(rawtext);n,field=q['event'].split('.',1);assert v['id']==int(n)
  for k in field.split('.'):v=v[k]
 checked.append({**q,'match':q['quote'] in v,'source_sha256':sha(path)})
write('records/038_checks/quote_checks.json',checked)
original=read('records/038_checks/input_hashes_before.json');changed=[p for p,h in original.items() if not (R/p).exists() or sha(R/p)!=h]
protected={str(p.relative_to(R)) for d in ['notes','records'] for p in (R/d).rglob('*') if p.is_file() and re.match(r'0(1[89]|2[0-9]|3[0-7])',p.relative_to(R/d).parts[0])}|{'docs/标注手册_v3.1.md','docs/标注手册_v3.2.md'}
seal=read('records/038_checks/calibration_seal.json');old={r['题目']+'_'+r['表']:r['主要原因类别'] for r in rows('records/020_annotations/020_summary.csv')}
pm={(p['对象编号'],p['错误点名称']):p for p in pts};delivery=read('records/038_checks/delivery_sources.json')['impl-007'];cats={'Data Misconception','Intent Misreading','Unstated Choice','Quiet Downgrade','Form Mismatch','已说出的选择','已说出的降级','代码写错','其他','不可评估','无法判定'}
checks={'scope_43_plus_2_exact':len(formal)==43 and len(cal)==2 and formal==expected and len(raw&pilots)==2,'by_task_32_11':dict(collections.Counter(r['task'] for r in scope['formal']))=={'impl-006':32,'impl-007':11},'catalog_exactly_43':{r['object'] for r in catalog}==formal,'catalog_all_contracts_and_sql_verified':all(r['contract_matches_original'] and r['complete_contract_present_in_initial_prompt'] and r['package_sql_matches_delivered'] for r in catalog),'completed_scope_exactly_45':done==formal|cal and len(objs)==45,'point_keys_unique':len(pm)==len(pts),'all_completed_objects_have_points':{p['对象编号'] for p in pts}==done,'point_categories_legal':all(p['类别'] in cats for p in pts),'roles_legal':all(p['角色'] in ['主要','并列','参与','非原因'] for p in pts),'five_grade_values_legal':all(p['是否说出（五档）'] in levels for p in pts),'disclosed_categories_and_grade1_consistent':all((p['是否说出（五档）']==levels[0])==(p['类别'] in ['已说出的选择','已说出的降级']) for p in pts if p['类别'] in ['Unstated Choice','Quiet Downgrade','已说出的选择','已说出的降级']),'audit_keys_match_points':{(p['对象编号'],p['错误点名称']) for p in audit}==set(pm),'audit_grades_match_points':all(a['grade'] in range(1,6) and a['是否说出']==levels[a['grade']-1]==pm[a['对象编号'],a['错误点名称']]['是否说出（五档）'] for a in audit),'grade1_2_have_deliverable_quotes':all(a['evidence'] and all(e['source'].endswith('.sql') or 'args.final_thought' in e['event'] for e in a['evidence']) for a in audit if a['grade'] in [1,2]),'quotes_all_match_original':all(q['match'] for q in checked),'headers_match_037_except_last_column':all(headers.values()),'020_old_labels_verbatim':all(r['020旧标签']==old[r['对象编号']] for r in objs+pts),'annotations_exactly_completed_scope':{p.stem.removeprefix('038_') for p in (R/'records/038_annotations').glob('*.md')}==done,'protected_files_unchanged':not changed and protected==set(original),'blind_seal_unchanged':sha(R/seal['sealed_path'])==seal['sha256'],'query_budget_le5_including_failed':all(c['reused_verification_query_count']<=5 for c in catalog),'impl007_no_finish_or_report_or_sql_comments':not delivery['finish'] and not delivery['result_files'] and not delivery['sql_comment_candidates'],'impl007_report_failures_and_service_error_verified':all('No such file or directory' in a['response'] for a in delivery['failed_report_attempts']) and 'ServiceUnavailableError' in delivery['terminal_error']['extras']['reason'],'raw013_no_differences':not read('records/038_checks/raw_integrity_review.json')['matching_rows']}
working=read('records/038_checks/calibration_working.json');rank=[]
for o in working:
 best=max(tuple(p['reduction']) for p in o['points']);win={p['错误点名称'] for p in o['points'] if tuple(p['reduction'])==best};actual={p['错误点名称'] for p in o['points'] if p['角色'] in ['主要','并列']};rank.append(win==actual)
checks['calibration_roles_follow_row_then_cell_ranking']=all(rank)
source_checks=[]
for c in catalog:
 package=R/c['package'];text=package.read_text();contract=re.search(r'```yaml\n([\s\S]*?)\n```',text).group(1)
 prompt=read(c['event_path'])['args']['content'];a,b=c['contract_lines'];actual='\n'.join(Path(c['contract_source']).read_text().splitlines()[a-1:b])
 source_checks.append(sha(package)==c['package_sha256'] and sha(R/c['agent_sql'])==c['agent_sql_sha256'] and contract.strip() in prompt and actual.strip()==contract.strip())
for t,d in read('records/038_checks/delivery_sources.json').items():
 for f in d['finish']:source_checks.append(read(f['path'])['args']['final_thought']==f['text'])
 for f in d.get('failed_report_attempts',[]):source_checks.append(read(f['path'])['args']['command']==f['command'] and read(f['response_path'])['content']==f['response'])
fallback=read('records/038_checks/fact_corrections.json')['verified_fallback']
source_checks.append(read(fallback['path'])['args']['command']==fallback['command'])
checks['preparation_sources_independently_rechecked']=all(source_checks)
# Recheck preserved working calibration records, not the unblinded labels in the seal.
cal_before=read('records/038_checks/calibration_working_rows_before_phase2.json')
checks['calibration_working_rows_unchanged']=objs[:2]==cal_before['objects'] and pts[:5]==cal_before['points'] and audit[:5]==cal_before['audit']
checks['impl007_all_grades_ge3']=all(a['grade']>=3 for a in audit if a['对象编号'].startswith('impl-007_'))
checks['grade1_tables_explicitly_named']=all(a.get('named_table') for a in audit if a['grade']==1 and a['对象编号'] in formal)
checks['grade3_has_doubt_quote']=all('语义不完全一致' in ''.join(e['quote'] for e in a['evidence']) and '进一步确认' in ''.join(e['quote'] for e in a['evidence']) for a in audit if a['grade']==3)
newq=read('records/038_checks/new_verification.json');qcounts={c['object']:c['reused_verification_query_count'] for c in catalog}
for q in newq:qcounts[q['object']]+=1
checks['query_budget_le5_including_failed']=all(n<=5 for n in qcounts.values())
checks['new_verification_only_agent_raw']=all(q['read_only'] and '/agent/' in q['source'] and 'FROM raw.' in q['sql'] for q in newq)
patches=[];nruns=0
for f in sorted((R/'records/038_checks').glob('rerun_impl-*.json')):
 d=json.loads(f.read_text());original_sql=(R/d['baseline_sql_path']).read_text();oldrun=read('records/020_reruns_'+d['object']+'.json')['runs'][0]
 ok=d['original_databases_read_only'] and d['private_database']==':memory:' and hashlib.sha256(original_sql.encode()).hexdigest()==d['baseline_sql_sha256']
 newbase=next(x for x in d['runs'] if x['label']=='baseline')
 ok=ok and [(x['row_scale'],x['cell_scale']) for x in newbase['comparison']['levels']]==[(x['row_scale'],x['cell_scale']) for x in oldrun['comparison']['levels']]
 for run in d['runs']:
  nruns+=run['label']!='baseline'
  r_ok=hashlib.sha256(run['sql'].encode()).hexdigest()==run['sql_sha256']
  if run['kind']=='单改重跑':
   es=run['edits'];r_ok=r_ok and len(es)==1 and original_sql.count(es[0]['old'])==1 and original_sql.replace(es[0]['old'],es[0]['new'],1)==run['sql']
  elif run['kind']=='呈现诊断':r_ok=r_ok and run['label']=='clv_presentation' and run['sql']=='SELECT * REPLACE(round(global_avg_clv,10) AS global_avg_clv) FROM result_baseline'
  patches.append(dict(source=str(f.relative_to(R)),label=run['label'],valid=r_ok))
 ok=ok and all(x['valid'] for x in patches if x['source']==str(f.relative_to(R)))
 checks['new_run_'+d['object']]=ok
write('records/038_checks/rerun_validation.json',patches)
dec=read('records/038_checks/formal_decisions.json');formalrank=[]
for o in dec:
 ps=o['points'];w=[p for p in ps if p['role'] in ['主要','并列']]
 if len(ps)==1 and ps[0].get('diagnostic'):formalrank.append(o['confidence']=='中' and len(w)==1)
 else:
  key=lambda p:(p['scales'][0]['delta_rows'],p['scales'][0]['delta_cells'])
  best=max(map(key,ps));formalrank.append({p['name'] for p in ps if key(p)==best}=={p['name'] for p in w})
 actual=next(x for x in objs if x['对象编号']==o['object']);cc=sorted(set(p['category'] for p in w))
 formalrank.append(actual['主要原因']==(cc[0] if len(cc)==1 else '多因并列') and actual['并列项']==('；'.join(cc) if len(cc)>1 else ''))
 checks['exploration_presence_'+o['object']]=all(p['contract_evidence']['source'] and p['evidence_presence']=='是' for p in ps if p['base_category']=='Intent Misreading')
checks['formal_roles_follow_row_then_cell_or_explicit_same_category_exception']=all(formalrank)
checks['formal_decisions_match_csv']=len(dec)==43 and sum(len(o['points']) for o in dec)==len(pts)-5 and all(pm[o['object'],p['name']]['类别']==p['category'] and pm[o['object'],p['name']]['角色']==p['role'] for o in dec for p in o['points'])
checks['primary_categories_consistent']=all(x['主要原因'] in cats|{'多因并列'} for x in objs)
# Guard immutable phase1 files against their committed snapshot too.
import subprocess
immutable=['records/038_calibration_blind_sealed.json','records/038_checks/calibration_seal.json','records/038_checks/input_hashes_before.json','records/038_calibration_comparison.json','records/038_checks/calibration_working_rows_before_phase2.json']
checks['csv_appended_original_byte_prefix']=all((R/('records/038_'+k+'.csv')).read_bytes().startswith(subprocess.check_output(['git','show','967056d:records/038_'+k+'.csv'],cwd=R)) for k in ['objects','points'])
checks['phase1_immutable_matches_commit']=all((R/p).read_bytes()==subprocess.check_output(['git','show','967056d:'+p],cwd=R) for p in immutable)
result={'status':'complete' if all(checks.values()) else 'validation_failed','task_complete':all(checks.values()),'expected_scope':{'formal':43,'calibration':2,'total':45},'completed_scope':{'formal':len(done&formal),'calibration':len(done&cal),'total':len(done)},'point_count':len(pts),'formal_point_count':len(pts)-5,'quote_count':len(checked),'protected_file_count':len(original),'protected_changed':changed,'checks':checks,'new_verification_queries':len(newq),'query_counts_including_reused_and_failed':qcounts,'new_interventions_including_presentation_diagnostic':nruns,'new_rerun_objects':7,'database_originals_read_only':True,'private_execution_in_memory':True,'sealed_sha256':sha(R/seal['sealed_path'])}
write('records/038_checks/validation.json',result)
failed=[k for k,v in checks.items() if not v]
print(json.dumps(dict(status=result['status'],objects=len(objs),points=len(pts),quotes=len(checked),protected=len(original),new_interventions=nruns,failed=failed),ensure_ascii=False))
assert not failed,failed
