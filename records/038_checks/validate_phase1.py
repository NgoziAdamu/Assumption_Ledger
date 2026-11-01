"""明确区分阶段验证通过与45表任务完成；只读受保护文件。"""
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
checked=[]
for q in quotes:
 path=R/q['source'];rawtext=path.read_text();v=rawtext
 if q['event']:
  v=json.loads(rawtext);n,field=q['event'].split('.',1);assert v['id']==int(n)
  for k in field.split('.'):v=v[k]
 checked.append({**q,'match':q['quote'] in v,'source_sha256':sha(path)})
write('records/038_checks/quote_checks.json',checked)
original=read('records/038_checks/input_hashes_before.json');changed=[p for p,h in original.items() if not (R/p).exists() or sha(R/p)!=h]
protected={str(p.relative_to(R)) for d in ['notes','records'] for p in (R/d).rglob('*') if p.is_file() and re.match(r'0(1[89]|2[0-9]|3[0-7])',p.relative_to(R/d).parts[0])}|{'docs/标注手册_v3.1.md','docs/标注手册_v3.2.md'}
seal=read('records/038_checks/calibration_seal.json');old={r['题目']+'_'+r['表']:r['主要原因类别'] for r in rows('records/020_annotations/020_summary.csv')}
pm={(p['对象编号'],p['错误点名称']):p for p in pts};delivery=read('records/038_checks/delivery_sources.json')['impl-007'];cats={'Data Misconception','Intent Misreading','Unstated Choice','Quiet Downgrade','Form Mismatch','已说出的选择','已说出的降级','代码写错','其他','不可评估','无法判定'}
checks={'scope_43_plus_2_exact':len(formal)==43 and len(cal)==2 and formal==expected and len(raw&pilots)==2,'by_task_32_11':dict(collections.Counter(r['task'] for r in scope['formal']))=={'impl-006':32,'impl-007':11},'catalog_exactly_43':{r['object'] for r in catalog}==formal,'catalog_all_contracts_and_sql_verified':all(r['contract_matches_original'] and r['complete_contract_present_in_initial_prompt'] and r['package_sql_matches_delivered'] for r in catalog),'completed_scope_exactly_two_calibration':done==cal and len(objs)==2,'point_keys_unique':len(pm)==len(pts),'all_completed_objects_have_points':{p['对象编号'] for p in pts}==done,'point_categories_legal':all(p['类别'] in cats for p in pts),'roles_legal':all(p['角色'] in ['主要','并列','参与','非原因'] for p in pts),'five_grade_values_legal':all(p['是否说出（五档）'] in levels for p in pts),'disclosed_categories_and_grade1_consistent':all((p['是否说出（五档）']==levels[0])==(p['类别'] in ['已说出的选择','已说出的降级']) for p in pts if p['类别'] in ['Unstated Choice','Quiet Downgrade','已说出的选择','已说出的降级']),'audit_keys_match_points':{(p['对象编号'],p['错误点名称']) for p in audit}==set(pm),'audit_grades_match_points':all(a['grade'] in range(1,6) and a['是否说出']==levels[a['grade']-1]==pm[a['对象编号'],a['错误点名称']]['是否说出（五档）'] for a in audit),'grade1_2_have_deliverable_quotes':all(a['evidence'] and all(e['source'].endswith('.sql') or 'args.final_thought' in e['event'] for e in a['evidence']) for a in audit if a['grade'] in [1,2]),'quotes_all_match_original':all(q['match'] for q in checked),'headers_match_037_except_last_column':all(headers.values()),'020_old_labels_verbatim':all(r['020旧标签']==old[r['对象编号']] for r in objs+pts),'annotations_exactly_completed_scope':{p.stem.removeprefix('038_') for p in (R/'records/038_annotations').glob('*.md')}==done,'protected_files_unchanged':not changed and protected==set(original),'blind_seal_unchanged':sha(R/seal['sealed_path'])==seal['sha256'],'query_budget_le5_including_failed':all(c['reused_verification_query_count']<=5 for c in catalog),'impl007_no_finish_or_report_or_sql_comments':not delivery['finish'] and not delivery['result_files'] and not delivery['sql_comment_candidates'],'impl007_report_failures_and_service_error_verified':all('No such file or directory' in a['response'] for a in delivery['failed_report_attempts']) and 'ServiceUnavailableError' in delivery['terminal_error']['extras']['reason'],'raw013_no_differences':not read('records/038_checks/raw_integrity_review.json')['matching_rows']}
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
result={'status':'phase1_complete_formal_pending','phase1_checks_pass':all(checks.values()),'task_complete':False,'expected_scope':{'formal':43,'calibration':2,'total':45},'completed_scope':{'formal':0,'calibration':2,'total':2},'pending_formal_objects':sorted(formal-done),'point_count':len(pts),'quote_count':len(checked),'protected_file_count':len(original),'protected_changed':changed,'checks':checks,'new_database_queries':0,'new_reruns':0,'database_opened_this_phase':False,'note':'通过仅表示准备与校准阶段符合检查；43张正式表未标注，45表最终完成检查尚未通过，不能把本文件作为完整批次PASS。'}
write('records/038_checks/validation.json',result)
assert all(checks.values()),[k for k,v in checks.items() if not v]
print(json.dumps({k:v for k,v in result.items() if k not in ['checks','pending_formal_objects']},ensure_ascii=False))
