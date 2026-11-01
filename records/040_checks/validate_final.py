"""Final task040 validation: 38 formal + 2 unchanged calibration objects."""
from pathlib import Path
import json,csv,hashlib,collections,subprocess,io,re
ROOT=Path.cwd();R=ROOT/'records';C=R/'040_checks'
def load(p):return json.loads(Path(p).read_text())
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def rows(p):return list(csv.DictReader(open(p)))
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
formal=load(C/'formal_working.json');cal=load(C/'calibration_working.json');scope=load(R/'040_scope.json');objects=rows(R/'040_objects.csv');points=rows(R/'040_points.csv');audit=load(C/'disclosure_audit.json');q=load(C/'quote_checks.json');seal=load(C/'calibration_seal.json');handoff=load(C/'phase1_handoff.json');snap=load(C/'calibration_rows_before_phase2.json')
expected_formal={r['task']+'_'+r['table'] for r in scope['formal']};expected_cal=set(scope['calibration']);expected=expected_formal|expected_cal
src={r['task']+'_'+r['table'] for r in rows(R/'013_statuses.csv') if r['task'] in ['impl-012','impl-013','impl-014'] and r['status']=='待标注'};pilots={r['对象编号'] for r in rows(R/'036_objects.csv')};old={r['题目']+'_'+r['表']:r['主要原因类别'] for r in rows(R/'022_annotations/022_summary.csv')}
for r in load(R/'022_calibration_blind_decisions.json')['decisions']:old[r['task']+'_'+r['table']]=r['main']
levels=['交付物里针对本处说明了','交付物里只有通用说明','过程中意识到了，交付物里没提','看到了相关信息，但没有意识到的迹象','没有迹象'];allowed={'Data Misconception','Intent Misreading','Unstated Choice','Quiet Downgrade','Form Mismatch','已说出的选择','已说出的降级','代码写错','其他','不可评估','无法判定'}
pm={(p['对象编号'],p['错误点名称']):p for p in points};om={o['对象编号']:o for o in objects};checks={}
checks['exact_38_plus_2_scope']=expected_formal==src-pilots and len(src&pilots)==3 and len(expected_formal)==38 and len(expected_cal)==2 and len(objects)==40 and set(om)==expected
checks['counts_7_18_13']=dict(collections.Counter(r['task'] for r in scope['formal']))=={'impl-012':7,'impl-013':18,'impl-014':13}
checks['all_40_annotations']=len(list((R/'040_annotations').glob('*.md')))==40 and {p.stem.removeprefix('040_') for p in (R/'040_annotations').glob('*.md')}==expected
checks['point_keys_unique']=len(pm)==len(points)
checks['points_cover_exact_scope']={x['对象编号'] for x in points}==expected
checks['five_grades_legal']=all(p['是否说出（五档）'] in levels for p in points)
checks['categories_legal']=all(p['类别'] in allowed for p in points)
checks['roles_legal']=all(p['角色'] in ['主要','并列','参与','非原因'] for p in points)
checks['disclosed_category_iff_grade1']=all((p['是否说出（五档）']==levels[0])==(p['类别'] in ['已说出的选择','已说出的降级']) for p in points if p['类别'] in ['Unstated Choice','Quiet Downgrade','已说出的选择','已说出的降级'])
checks['022_old_labels_verbatim']=all(x['022旧标签']==old[x['对象编号']] for x in objects+points)
checks['schema_matches_039']=True
for kind in ['objects','points']:
 h=next(csv.reader(open(R/f'039_{kind}.csv')));h[-1]='022旧标签';checks['schema_matches_039'] &= h==next(csv.reader(open(R/f'040_{kind}.csv')))
 prefix=(C/f'phase1_{kind}_prefix.csv').read_bytes();checks['calibration_'+kind+'_bytes_unchanged']=(R/f'040_{kind}.csv').read_bytes().startswith(prefix) and hashlib.sha256(prefix).hexdigest()==snap['csv_sha256'][kind]
checks['calibration_rows_unchanged']=objects[:2]==snap['objects'] and points[:5]==snap['points'] and audit[:5]==snap['audit']
checks['seal_unchanged']=sha(seal['path'])==seal['sha256']==handoff['sealed_sha256']
checks['comparison_unchanged']=sha(handoff['comparison'])==handoff['comparison_sha256']
for oid in expected_cal:
 f=f'records/040_annotations/040_{oid}.md';oldbytes=subprocess.check_output(['git','show','5a96290:'+f]);checks['calibration_annotation_'+oid+'_unchanged']=Path(f).read_bytes()==oldbytes
checks['audit_one_per_point']=len(audit)==len(points) and {(a['对象编号'],a['错误点名称']) for a in audit}==set(pm) and all(a['是否说出']==pm[a['对象编号'],a['错误点名称']]['是否说出（五档）'] for a in audit)
checks['grade1_2_deliverable_only']=all(a['evidence'] and all(e['field']=='args.final_thought' for e in a['evidence']) for a in audit if a['grade'] in [1,2])
checks['all_quotes_rechecked']=True
for x in q:
 v=Path(x['path']).read_text()
 if x['field']!='text':
  v=json.loads(v)
  if 'event' in x:checks['all_quotes_rechecked'] &= v['id']==x['event']
  for k in x['field'].split('.'):v=v[k]
 checks['all_quotes_rechecked'] &= x['exact_match'] and x['quote'] in v and sha(x['path'])==x['source_sha256']
protected=load(C/'protected_hashes_before.json');changed=[p for p,h in protected.items() if not Path(p).is_file() or sha(p)!=h]
current={str(p) for d in ['notes','records'] for p in Path(d).rglob('*') if p.is_file() and p.relative_to(d).parts[0][:3].isdigit() and 18<=int(p.relative_to(d).parts[0][:3])<=39}|{'docs/标注手册_v3.1.md','docs/标注手册_v3.2.md'}
checks['protected_018_039_and_manual_hashes_unchanged']=not changed and current==set(protected)
checks['working_matches_csv']=True;checks['row_then_cell_ranking']=True;checks['metrics_trace_to_sources']=True;checks['exploration_evidence_and_previous_correct']=True
for o in formal+cal:
 pts=o['points'];deltas=[tuple(p['reduction']) for p in pts];best=max(deltas);w=[p for p in pts if tuple(p['reduction'])==best];expected_main=next(iter({p['category'] for p in w})) if len({p['category'] for p in w})==1 else '多因并列'
 checks['row_then_cell_ranking'] &= best>(0,0) and o['main']==expected_main and om[o['id']]['主要原因']==expected_main and not o['combination_only']
 for p in pts:
  row=pm[o['id'],p['name']];checks['working_matches_csv'] &= row['类别']==p['category'] and row['角色']==p['role'] and row['是否说出（五档）']==levels[p['disclosure']-1]
  expectrole=('主要' if len(w)==1 else '并列') if p in w else ('参与' if tuple(p['reduction'])>(0,0) else '非原因');checks['row_then_cell_ranking'] &= p['role']==expectrole and p['reduction']==[p['baseline'][0]['row_scale']-p['single_change'][0]['row_scale'],p['baseline'][0]['cell_scale']-p['single_change'][0]['cell_scale']]
  s=load(p['rerun_source'])
  if p.get('diagnostic_index') is not None:cmp=s[p['diagnostic_index']]['order_canonicalization']['levels']
  else:
   run=next(r for r in s['runs'] if r['label']==p['rerun_label']);cmp=run['comparison']['levels'];checks['metrics_trace_to_sources'] &= p['baseline']==s['runs'][0]['comparison']['levels']
  checks['metrics_trace_to_sources'] &= p['single_change']==cmp
  if p['category'] in ['Data Misconception','Intent Misreading']:
   checks['exploration_evidence_and_previous_correct'] &= p['evidence_present']=='是' and any(x.get('kind')=='presence' and x.get('event')==1 for x in p['quotes']) and row['证据在场']==p['evidence_present'] and row['曾经理解对过']==p['previously_correct']
   if p['previously_correct']=='是':checks['exploration_evidence_and_previous_correct'] &= any(x.get('kind')=='previous_correct' for x in p['quotes'])
checks['verification_queries_including_failures_le5']=all(o['verification_query_count']<=5 for o in formal) and all(o['verification_query_count_including_failures']<=5 for o in cal)
checks['source_contract_sql_still_match']=all(sha(o['contract_path'])==o['contract_sha256'] and sha(o['sql_source'])==o['sql_sha256'] for o in formal)
checks['all_contract_presence_per_table']=all(o['contract_present'] is True for o in formal if o['index_022']!=6)
search=load(C/'calendar_contract_search.json');checks['calendar_full_document_no_definition']=not search['exact_definition_matches'] and sha(search['path'])==search['sha256'] and len(Path(search['path']).read_text().splitlines())==search['line_count'] and len(search['references'])==2
newfiles=list(C.glob('supplement_*.json'));new_runs=0;dbpaths=set();checks['supplement_readonly_and_unchanged']=True;checks['supplement_baselines_equal022']=True;checks['single_change_exact_reconstruction']=True
for f in newfiles:
 d=load(f);new_runs+=len(d['runs'])-1;dbpaths.update(d['database_hashes_before']);checks['supplement_readonly_and_unchanged'] &= d['original_databases_read_only'] and d['private_execution']=='DuckDB :memory:' and d['database_hashes_before']==d['database_hashes_after']
 oldd=load(R/f'022_reruns_{d["object"]}.json');checks['supplement_baselines_equal022'] &= d['baseline_matches_022'] and d['runs'][0]['comparison']==oldd['runs'][0]['comparison']
 for run in d['runs']:
  text=d['runs'][0]['sql']
  for e in run['edits']:
   checks['single_change_exact_reconstruction'] &= text.count(e['old'])==1 and text.index(e['old'])==e['offset'];text=text.replace(e['old'],e['new'],1)
  checks['single_change_exact_reconstruction'] &= text==run['sql'] and hashlib.sha256(text.encode()).hexdigest()==run['sql_sha256']
 for path,h in d['database_hashes_after'].items():checks['supplement_readonly_and_unchanged'] &= sha(path)==h
checks['three_026_corrections_completed']=all(x.get('phase2_status')=='已完成' for x in load(C/'fact_corrections.json')['items'])
checks['raw_three_tasks_013_no_changes']=all(not x['013_difference_entries'] and x['013_all_columns_types_and_row_counts_equal'] and not x['022_reused_three_side_audit']['different_tables'] for x in load(C/'raw_integrity_review.json'))
res={'status':'complete' if all(checks.values()) else 'validation_failed','task_complete':all(checks.values()),'expected_scope':{'formal':38,'calibration':2,'total':40},'completed_scope':{'formal':len(formal),'calibration':len(cal),'total':len(objects)},'point_count':len(points),'formal_point_count':sum(len(o['points']) for o in formal),'quote_count':len(q),'protected_file_count':len(protected),'protected_changed':changed,'supplement_single_changes':new_runs,'supplement_baselines':len(newfiles),'new_database_files_read':len(dbpaths),'checks':checks,'limits':['引句逐字回查是机械验证，类别和语义依据见逐表说明。','官方comparison_columns之外的契约列不扩充评分口径；如customer_credit_risk缺少的风险输出不凭空填入差异规模。','阶段一handoff/evidence_catalog保留为历史准备文件，其pending状态不代表最终结果。'],'sealed_sha256':seal['sha256'],'formal_main_counts':dict(collections.Counter(o['main'] for o in formal))}
save(C/'validation.json',res);print(json.dumps({k:res[k] for k in ['status','task_complete','completed_scope','point_count','quote_count','protected_file_count','supplement_single_changes','supplement_baselines']},ensure_ascii=False));fail=[k for k,v in checks.items() if not v];print('failed',fail);assert not fail
