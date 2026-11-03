from pathlib import Path
import json,csv,hashlib,collections,re
R=Path('records');C=R/'042_checks'
def load(p):return json.loads(Path(p).read_text())
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def rows(p):return list(csv.DictReader(open(p)))
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
sc=load(R/'042_scope.json');formal={x['object_id'] for x in sc['formal']};cal=set(sc['calibration']);allids=formal|cal
source={r['task']+'_'+r['table'] for r in rows(R/'013_statuses.csv') if r['status']=='待标注' and r['task'] in {f'impl-{n:03}' for n in range(15,22)}};pilots={r['对象编号'] for r in rows(R/'036_objects.csv')}
o=rows(R/'042_objects.csv');p=rows(R/'042_points.csv');cw=load(C/'calibration_working.json');fw=load(C/'formal_working.json');catalog=load(C/'evidence_catalog.json');audit=load(C/'disclosure_audit.json');receipt=load(C/'calibration_seal_receipt.json');comp=load(R/'042_calibration_comparison.json');handoff=load(C/'phase1_handoff.json');old={x['task']+'_'+x['table']:x['category'] for x in load(R/'023_decisions.json')}
levels=['交付物里针对本处说明了','交付物里只有通用说明','过程中意识到了，交付物里没提','看到了相关信息，但没有意识到的迹象','没有迹象']
pm={(x['对象编号'],x['错误点名称']):x for x in p};om={x['对象编号']:x for x in o};checks={};quotes=[]
for q in load(C/'quote_inventory.json')+load(C/'formal_quote_inventory.json'):
 text=Path(q['path']).read_text()
 if q['field']!='text':
  v=json.loads(text)
  if 'event' in q:assert v['id']==q['event']
  for key in q['field'].split('.'):v=v[key]
  text=v
 quotes.append({**q,'exact_match':bool(q['quote']) and q['quote'] in text,'source_sha256':sha(q['path'])})
save(C/'quote_checks.json',quotes)
protected=load(C/'protected_hashes_before.json');changed=[s for s,h in protected.items() if not Path(s).is_file() or sha(s)!=h]
current={str(p) for root in ['notes','records'] for p in Path(root).rglob('*') if p.is_file() and p.relative_to(root).parts[0][:3].isdigit() and 18<=int(p.relative_to(root).parts[0][:3])<=41}|{'docs/标注手册_v3.1.md','docs/标注手册_v3.2.md'}
checks.update(scope_39_plus_2=formal==source-pilots and len(formal)==39 and len(cal)==2 and len(source&pilots)==7 and not formal&cal,formal_counts=dict(collections.Counter(x['task'] for x in sc['formal']))==dict(zip([f'impl-{i:03}' for i in range(15,22)],[4,4,9,9,3,4,6])),completed_41_objects=len(o)==41 and set(om)==allids and len(om)==len(o),point_keys_unique=len(pm)==len(p),point_scope_exact={x['对象编号'] for x in p}==allids,five_grades_legal=all(x['是否说出（五档）'] in levels for x in p),roles_legal=all(x['角色'] in ['主要','并列','参与','非原因'] for x in p),old_023_main_verbatim=all(x['023旧标签']==old[x['对象编号']] for x in o+p),grade1_disclosed_consistency=all((x['是否说出（五档）']==levels[0])==(x['类别'] in ['已说出的选择','已说出的降级']) for x in p if x['类别'] in ['Unstated Choice','Quiet Downgrade','已说出的选择','已说出的降级']),grade1_2_only_deliverables=all(all(q['field']=='args.final_thought' for q in x['evidence']) for x in audit if x['grade'] in [1,2]),audit_matches_points=len(audit)==len(p) and {(x['对象编号'],x['错误点名称']) for x in audit}==set(pm) and all(x['是否说出']==pm[x['对象编号'],x['错误点名称']]['是否说出（五档）'] and x['category']==pm[x['对象编号'],x['错误点名称']]['类别'] for x in audit),quotes_exactly_match=all(x['exact_match'] for x in quotes),protected_files_unchanged=not changed and current==set(protected),sealed_unchanged=sha(receipt['path'])==receipt['sha256']==comp['sealed_sha256'],phase1_calibration_files_unchanged=all(sha(s)==h for s,h in handoff['protected_calibration_files'].items()),blind_accuracy_not_rewritten=comp['blind_main_matches']==1 and comp['final_main_matches']==2 and comp['final_is_not_blind_agreement'],annotations_exactly_41={x.stem.removeprefix('042_') for x in (R/'042_annotations').glob('*.md')}==allids,calibration_csv_prefix_unchanged=all((R/f'042_{k}.csv').read_bytes().startswith((C/f'phase1_{k}_prefix.csv').read_bytes()) for k in ['objects','points']),catalog_39_exact=len(catalog)==39 and {x['object_id'] for x in catalog}==formal,catalog_contract_sql_originals_match=all(x['contract_matches_original'] and x['sql_matches_package'] and sha(x['agent_sql'])==x['agent_sql_sha256'] and sha(x['package'])==x['package_sha256'] and sha(x['contract_path'])==x['contract_sha256'] for x in catalog),catalog_contract_present_39=all(x['contract_present_in_initial_prompt'] for x in catalog),query_budget_including_repeated_le5=all(x['verification_query_count']<=5 for x in fw) and all(x['verification_query_count_including_read_duplicate']<=5 for x in cw),raw_seven_tasks_reviewed=len(load(C/'raw_integrity_review.json'))==7,formal_working_39=len(fw)==39 and {x['id'] for x in fw}==formal)
for k in ['objects','points']:
 h=next(csv.reader(open(R/f'040_{k}.csv')));h[-1]='023旧标签';checks[f'header_{k}_same_040_except_last']=h==next(csv.reader(open(R/f'042_{k}.csv')))
rank=[];scales=[];pointmatch=[];source_policy=[];sql_checks=[];methods=[]
for obj in cw+fw:
 oid=obj.get('id',obj.get('object_id'))
 if oid is None:oid=obj['object']
 points=obj['points'];special=oid=='impl-017_greenhouse__application_history'
 if obj.get('combination_only'):
  d=load(obj['combination_source']);run=next(z for z in d['runs'] if z['label']==obj['combination_run']);rank.append(all(z['reduction']==[0,0] for z in points) and all(z['role']=='并列' for z in points) and run['comparison']['levels']==obj['combination_after'] and all(a['row_scale']==a['cell_scale']==0 for a in obj['combination_after']))
 elif special:rank.append(len(points)==1 and points[0]['category']=='其他' and points[0]['role']=='主要' and points[0]['after_levels'][2]['row_scale']==0)
 else:
  best=max(tuple(z['reduction']) for z in points);wins={z['name'] for z in points if tuple(z['reduction'])==best};rank.append(best>(0,0) and wins=={z['name'] for z in points if z['role'] in ['主要','并列']})
 for z in points:
  row=pm[oid,z['name']];pointmatch.append(row['类别']==z['category'] and row['角色']==z['role'] and row['是否说出（五档）']==levels[(z['grade'] if 'grade' in z else z['disclosure'])-1])
  d=load(z['run_source']);base=next(r['comparison']['levels'] for r in d['runs'] if r['label']=='baseline');run=next(r for r in d['runs'] if r['label']==z['run']);after=run['comparison']['levels'];scales.append(base==z['baseline_levels'] and after==z['after_levels'])
  if z['reduction'] is not None:scales.append(z['reduction']==[base[0]['row_scale']-after[0]['row_scale'],base[0]['cell_scale']-after[0]['cell_scale']])
  if oid not in formal:continue
  if z['category'] in ['Data Misconception','Intent Misreading']:pointmatch.append(row['证据在场']==z['presence'] and row['曾经理解对过']==z['ever_correct'])
  if z['category']=='Data Misconception':pointmatch.append(bool(z['premise']) and bool(obj['verification_queries']))
  if d.get('not_agent_sql_repair'):
   methods.append(z['category']=='其他' and '诊断' in z['scale_method']);continue
  methods.append(True)
  if obj['layer']=='staging':source_policy.append(Path(d['source']).resolve()==Path(load(R/'013_cases.json')[int(obj['task'][-3:])-1]['agent_database']).resolve())
  else:source_policy.append(d['source']==d['basis']['gold_database'])
# 审计所有使用的非诊断单改：固定时间基线、指定替换、SQL hash和完整L0-L3。
used_sources={z['run_source'] for o in fw for z in o['points']}|{o['combination_source'] for o in fw if o.get('combination_only')}
reruns=[]
for source in sorted(used_sources):
 d=load(source)
 if d.get('not_agent_sql_repair'):continue
 oid=next(o['id'] for o in fw if any(z['run_source']==source for z in o['points']) or o.get('combination_source')==source);obj=next(o for o in fw if o['id']==oid);base=Path(obj['sql_source']).read_text()
 for edit in d['clock_control']:base=re.sub(edit['pattern'],edit['replacement'],base,flags=re.I)
 for run in d['runs']:
  mod=base
  for e in run['edits']:
   assert mod[e['offset']:e['offset']+len(e['old'])]==e['old'],(source,run['label'],'offset')
   mod=mod[:e['offset']]+e['new']+mod[e['offset']+len(e['old']):]
  actual=run.get('sql') or Path(run['sql_path']).read_text();ok=actual==mod and hashlib.sha256(actual.encode()).hexdigest()==run['sql_sha256'];sql_checks.append(ok);reruns.append(dict(source=source,label=run['label'],sql_exact_patch=ok,sql_sha256=run['sql_sha256']))
checks.update(row_then_cell_ranking=all(rank),rerun_scales_exact=all(scales),working_matches_csv=all(pointmatch),staging_agent_raw_cs_gold_upstream=all(source_policy),rerun_sql_exact_edits_and_hash=all(sql_checks),diagnostics_not_claimed_sql_repairs=all(methods))
save(C/'rerun_audit.json',reruns)
# 本阶段真正打开的库：前后记录一致，并重新哈希确认收尾仍未变。
db_expected={};db_checks=[]
for f in sorted(C.glob('supplement_*.json'))+sorted(C.glob('diagnostic_*.json')):
 d=load(f);assert d['database_hashes_before']==d['database_hashes_after'];db_checks.append(d['original_databases_read_only'] and d['baseline_matches_023']);db_expected.update(d['database_hashes_after'])
for q in load(C/'new_verification_queries.json'):
 db_checks.append(q['database_hash_before']==q['database_hash_after'] and q['original_database_read_only']);db_expected[q['database']]=q['database_hash_after']
db_actual={path:sha(path) for path in db_expected};save(C/'database_hashes_final.json',{'expected':db_expected,'actual':db_actual,'unchanged':db_expected==db_actual});checks['new_queries_and_diagnostics_readonly_hash_unchanged']=all(db_checks) and db_expected==db_actual
checks['026_klaviyo_process_separately_audited']=all(z['process_awareness'] and z['grade']==2 and z['category']=='其他' for o in fw if o['table'] in ['stg_klaviyo__campaign','stg_klaviyo__flow','stg_klaviyo__metric'] for z in o['points'])
checks['report_full_scope']='39张正式表' in Path('notes/042_2026-11-01_DAComp重标第五批.md').read_text() and '任务已完成' in Path('notes/042_2026-11-01_DAComp重标第五批.md').read_text()
for task,d in load(C/'delivery_sources.json').items():checks['finish_verified_'+task]=len(d['finish'])==1 and all(load(x['path'])['args']['final_thought']==x['text'] and sha(x['path'])==x['sha256'] for x in d['finish'])
result={'status':'complete' if all(checks.values()) else 'validation_failed','task_complete':all(checks.values()),'expected_scope':{'formal':39,'calibration':2,'total':41},'completed_scope':{'formal':39,'calibration':2,'total':41},'point_count':len(p),'formal_point_count':sum(len(x['points']) for x in fw),'quote_count':len(quotes),'protected_file_count':len(protected),'protected_changed':changed,'new_opened_database_file_count':len(db_actual),'checks':checks,'sealed_sha256':receipt['sha256'],'limitations':['引句精确匹配不代替语义审查。','Workday raw email删行步骤和原因仍未找到。','允许并列的逐列屏蔽仅作Other诊断；不是SQL修复因果收益。','只改一处无收益或增差不代表组合后无影响；不将非原因计作参与。','023原有数据库快照沿用其时点证明，不能追溯补证早于快照的未变性。']}
save(C/'validation.json',result);print(json.dumps({k:result[k] for k in ['status','task_complete','completed_scope','point_count','quote_count','protected_file_count']},ensure_ascii=False));bad=[k for k,v in checks.items() if not v];print('failed',bad);assert not bad
