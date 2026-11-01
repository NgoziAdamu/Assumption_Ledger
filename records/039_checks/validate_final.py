"""039 final structural, provenance, ranking and immutable-input validation."""
from pathlib import Path
import csv,json,hashlib,collections,io
R=Path('records');C=R/'039_checks'
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def rows(p):return list(csv.DictReader(open(p)))
scope=load(R/'039_scope.json');formal={x['task']+'_'+x['table'] for x in scope['formal']};cal=set(scope['calibration']);objects=rows(R/'039_objects.csv');points=rows(R/'039_points.csv');audit=load(C/'disclosure_audit.json');working=load(C/'formal_working.json');calwork=load(C/'calibration_working.json');catalog=load(C/'evidence_catalog.json');snapshot=load(C/'calibration_working_rows_before_phase2.json');handoff=load(C/'phase1_handoff.json')
raw={x['task']+'_'+x['table'] for x in rows(R/'013_statuses.csv') if x['status']=='待标注' and x['task'] in ['impl-008','impl-009','impl-010','impl-011']};pilots={x['对象编号'] for x in rows(R/'036_objects.csv')};uneval={x['object'] for x in load(C/'raw_integrity_review.json')}
levels=['交付物里针对本处说明了','交付物里只有通用说明','过程中意识到了，交付物里没提','看到了相关信息，但没有意识到的迹象','没有迹象'];categories={'Data Misconception','Intent Misreading','Unstated Choice','Quiet Downgrade','Form Mismatch','其他','代码写错','已说出的选择','已说出的降级'}
old={x['题目']+'_'+x['表']:x['主要原因类别'] for x in rows(R/'021_annotations/021_summary.csv')}
for x in load(C/'fact_corrections.json')['025']:old[x['object']]=x['old_label_after_025']
q=load(C/'quote_inventory.json')
for o in load(R/'039_calibration_blind_sealed.json')['objects']:
 for p in o['points']:
  for x in p['quotes']:q.append({'object':o['id'],'point':p['name'],'sealed':True,**x})
checks_q=[];text_cache={}
for x in q:
 path=x['source'];v=text_cache.setdefault(path,Path(path).read_text())
 if x['field']!='text':
  v=json.loads(v);assert v['id']==x['event']
  for k in x['field'].split('.'):v=v[k]
 checks_q.append({**x,'exact_match':x['quote'] in v,'source_sha256':sha(path),'semantic_caveat':'封存event34不是invoice；工作结果已撤回其证明作用' if x.get('sealed') and x.get('event')==34 else ''})
save(C/'quote_checks.json',checks_q)
original=load(C/'input_hashes_before.json');changed=[p for p,h in original.items() if not Path(p).exists() or sha(p)!=h]
current={str(p) for d in ['notes','records'] for p in Path(d).rglob('*') if p.is_file() and '__pycache__' not in str(p) and p.parts[1][:3].isdigit() and 18<=int(p.parts[1][:3])<=38}|{'docs/标注手册_v3.1.md','docs/标注手册_v3.2.md'}
headers={};prefix={}
for k in ['objects','points']:
 with open(R/f'038_{k}.csv') as f:h=next(csv.reader(f))
 h[-1]='021旧标签'
 with open(R/f'039_{k}.csv') as f:headers[k]=next(csv.reader(f))==h
 s=io.StringIO(newline='');w=csv.DictWriter(s,fieldnames=h,lineterminator='\n');w.writeheader();w.writerows(snapshot[k]);b=s.getvalue().encode();prefix[k]=hashlib.sha256(b).hexdigest()==handoff['calibration_csv_prefix_sha256'][str(R/f'039_{k}.csv')] and (R/f'039_{k}.csv').read_bytes().startswith(b)
pm={(p['对象编号'],p['错误点名称']):p for p in points};om={o['对象编号']:o for o in objects}
checks={
 'expected_scope_40_plus_2':formal==raw-pilots and len(formal)==40 and len(cal)==2 and len(raw&pilots)==4,
 'task_counts_8_10_11_11':dict(collections.Counter(x['task'] for x in scope['formal']))=={'impl-008':8,'impl-009':10,'impl-010':11,'impl-011':11},
 'completed_scope_exactly_42':len(objects)==len(om)==42 and set(om)==formal|cal,
 'formal_working_exactly_40':len(working)==40 and {x['object'] for x in working}==formal,
 'point_keys_unique':len(pm)==len(points),
 'point_scope_exact_except_6_unevaluable':{p['对象编号'] for p in points}==(formal|cal)-uneval,
 'unevaluable_6_no_point_grade':len(uneval)==6 and all(om[k]['主要原因']=='不可评估' for k in uneval) and not any(p['对象编号'] in uneval for p in points),
 'five_grades_legal':all(p['是否说出（五档）'] in levels for p in points),
 'point_categories_legal':all(p['类别'] in categories for p in points),
 'role_values_legal':all(p['角色'] in ['主要','并列','参与','非原因'] for p in points),
 'headers_match_038_except_last_column':all(headers.values()),
 '021_old_labels_verbatim_including_025':all(o['021旧标签']==old[o['对象编号']] for o in objects+points),
 'grade1_disclosed_category_consistency':all((p['是否说出（五档）']==levels[0])==(p['类别'] in ['已说出的选择','已说出的降级']) for p in points if p['类别'] in ['Unstated Choice','Quiet Downgrade','已说出的选择','已说出的降级']),
 'all_quote_text_matches':all(x['exact_match'] for x in checks_q),
 'grade1_2_only_delivery':all(a['evidence'] and all(q['kind']=='delivery' and q['field']=='args.final_thought' for q in a['evidence']) for a in audit if a['grade'] in [1,2]),
 'audit_matches_points':len(audit)==len(points) and all(a['是否说出']==pm[a['对象编号'],a['错误点名称']]['是否说出（五档）'] and a['category']==pm[a['对象编号'],a['错误点名称']]['类别'] for a in audit),
 'protected_files_unchanged':not changed and current==set(original),
 'phase1_immutable_hashes_unchanged':all(sha(p)==h for p,h in handoff['immutable_sha256'].items()),
 'calibration_csv_prefixes_unchanged':all(prefix.values()),
 'calibration_rows_audit_unchanged':objects[:2]==snapshot['objects'] and points[:13]==snapshot['points'] and audit[:13]==snapshot['audit'],
 'annotations_exactly_42':{p.stem.removeprefix('039_') for p in (R/'039_annotations').glob('*.md')}==formal|cal,
 'formal_contract_and_sql_verified':all(x['contract_matches_original'] and x['complete_contract_present_in_initial_prompt'] and x['package_sql_matches_delivered'] for x in catalog),
 'formal_original_sources_hash_unchanged':all(sha(x['package'])==x['package_sha256'] and sha(x['agent_sql'])==x['agent_sql_sha256'] for x in catalog),
 'verification_budget_including_reused_le5':all(x['reused_verification_query_count']<=5 for x in catalog) and all(x['verification_query_count']<=5 for x in calwork),
 '025_three_CS_not_unevaluable':all(om[x['object']]['主要原因']!='不可评估' and om[x['object']]['021旧标签']=='O' for x in load(C/'fact_corrections.json')['025']),
 'raw_mismatch_content_hash_confirmed':all(q['initial_eq_agent'] and not q['gold_eq_agent'] and q['diagnostic']['initial']['content_hash']['sha256']==q['diagnostic']['agent']['content_hash']['sha256']!=q['diagnostic']['gold']['content_hash']['sha256'] for o in load(C/'raw_integrity_review.json') for q in o['checks'])}
for k,d in load(C/'delivery_sources.json').items():checks['finish_verified_'+k]=len(d['finish'])==1 and all(load(x['path'])['args']['final_thought']==x['text'] and sha(x['path'])==x['sha256'] for x in d['finish'])
checks['all_process_event_hashes_verified']=all(sha(e['path'])==e['sha256'] for t in load(C/'process_review.json') for e in t['events'])
qkeys={(x['object'],x['point'],x['kind']) for x in q};checks['contract_quote_refs_resolve']=all((ref['object'],ref['point'],ref['kind']) in qkeys for a in audit for ref in ([a['contract_quote_ref']] if 'contract_quote_ref' in a else []))
rank=[];rerun=[];pointtext=[]
for o in working+calwork:
 key=o.get('object',o.get('id'));ps=o['points']
 if not ps:continue
 best=max(tuple(p['reduction']) for p in ps);w={p['name'] for p in ps if tuple(p['reduction'])==best};actual={p['name'] for p in ps if p['role'] in ['主要','并列']};rank.extend([w==actual,best>(0,0),not o['combination_only']])
 cats={p['category'] for p in ps if p['name'] in w};rank.append(o['main']==(next(iter(cats)) if len(cats)==1 else '多因并列'))
 for p in ps:
  rank.append(p['reduction']==[o['baseline']['L0'][k]-p['scales']['L0'][k] for k in ['row_scale','cell_scale']])
  if p['role']=='参与':rank.append(tuple(p['reduction'])>(0,0))
  if p['role']=='非原因':rank.append(tuple(p['reduction'])<=(0,0))
  source=p.get('rerun_source',o.get('rerun_source'));d=load(source);d=d.get('record',d);r=next(x for x in d['runs'] if x['label']==p['rerun']);b=d['runs'][0]['comparison'];f=lambda cp:{z['level']:{k:z[k] for k in ['row_scale','cell_scale']} for z in cp['levels']}
  rerun.extend([f(r['comparison'])==p['scales'],f(b)==o['baseline']]);pointtext.append(p['name'] in (R/'039_annotations'/f'039_{key}.md').read_text())
checks['row_then_cell_ranking_all_42']=all(rank);checks['all_rerun_scales_baselines_trace_to_records']=all(rerun);checks['all_points_documented']=all(pointtext)
new=[]
for f in C.glob('supplement_impl-*.json'):
 d=load(f);source=load(d['source_record']);source=source.get('record',source)
 new.append(d['original_databases_read_only'] and d['private_database']==':memory:' and d['runs'][0]['comparison']==source['runs'][0]['comparison'])
 for run in d['runs']:
  new.append(hashlib.sha256(run['sql'].encode()).hexdigest()==run['sql_sha256'])
 if 'recovery_duplicate_groups' in d:new.append(d['recovery_duplicate_groups']==0)
checks['new_diagnostics_source_baselines_and_sql_hashes_valid']=len(new)>0 and all(new)
checks['stakeholder_diagnostic_confirms_gold_difference']=load(C/'stakeholder_diagnostic.json')['rows']==[{'users':4524,'raw_count_diff':356,'valid_count_diff':0,'union_count_diff':2418,'breadth_diff':1579,'nonzero_network':0}]
combo=load(C/'calibration_combo.json');checks['calibration_combo_full_match_L0_L3']=all(x['row_scale']==x['cell_scale']==0 for x in combo['runs'][-1]['comparison']['levels'])
checks['formal_working_status_complete']=all(o['annotation_status']=='complete' for o in working)
checks['new_staging_uses_agent_retained_raw']=all('/agent/' in load(f)['source'] or 'agent' in load(f)['source'] for f in C.glob('supplement_impl-009_stg_*.json'))
report=Path('notes/039_2026-11-01_DAComp重标第三批.md').read_text()
checks['complete_report_covers_scope_corrections_and_rules']=all(x in report for x in ['完整批次','40＋2＝42','189','425','1932','025更正的三张CS表','不可评估的六张表','不确定或没查到的（含规则问题）'])
result={'status':'complete' if all(checks.values()) else 'validation_failed','task_complete':all(checks.values()),'expected_scope':{'formal':40,'calibration':2,'total':42},'completed_scope':{'formal':40,'calibration':2,'total':42},'unevaluable_count':6,'point_count':len(points),'formal_point_count':len(points)-13,'quote_count':len(checks_q),'protected_file_count':len(original),'protected_changed':changed,'checks':checks,'new_verification_queries':0,'max_reused_formal_verification_queries':max(x['reused_verification_query_count'] for x in catalog),'sealed_sha256':sha(R/'039_calibration_blind_sealed.json'),'limitations':['引句逐字匹配不自动证明语义；封存event34错配仅保留原件，工作结果已撤回。','四个同类缺口组为整表机械生成诊断，不能推导各字段独立贡献；Earnings来源政策颗粒度及Stakeholder项目范围读法在规则问题列明。','高重复键/不同运行时钟/任意LIMIT残差按逐表说明处理，不将gold所有差异都解释成agent错误。']}
save(C/'validation.json',result);print(json.dumps({k:result[k] for k in ['status','task_complete','completed_scope','point_count','quote_count','protected_file_count']},ensure_ascii=False));failed=[k for k,v in checks.items() if not v];print('failed',failed);assert not failed
