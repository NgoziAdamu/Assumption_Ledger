"""Validate the completed calibration and prepared scope, explicitly not task completion."""
from pathlib import Path
import json,csv,hashlib,collections,re
R=Path('records');C=R/'039_checks'
def load(p):return json.loads(Path(p).read_text())
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def rows(p):return list(csv.DictReader(open(p)))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
scope=load(R/'039_scope.json');formal={x['task']+'_'+x['table'] for x in scope['formal']};cal=set(scope['calibration']);objects=rows(R/'039_objects.csv');points=rows(R/'039_points.csv');audit=load(C/'disclosure_audit.json');working=load(C/'calibration_working.json');catalog=load(C/'evidence_catalog.json');seal=load(C/'calibration_seal.json');comp=load(R/'039_calibration_comparison.json')
raw={x['task']+'_'+x['table'] for x in rows(R/'013_statuses.csv') if x['status']=='待标注' and x['task'] in ['impl-008','impl-009','impl-010','impl-011']};pilots={x['对象编号'] for x in rows(R/'036_objects.csv')}
levels=['交付物里针对本处说明了','交付物里只有通用说明','过程中意识到了，交付物里没提','看到了相关信息，但没有意识到的迹象','没有迹象']
old={x['题目']+'_'+x['表']:x['主要原因类别'] for x in rows(R/'021_annotations/021_summary.csv')}
q=load(C/'quote_inventory.json')
for o in load(R/'039_calibration_blind_sealed.json')['objects']:
 for p in o['points']:
  for x in p['quotes']:q.append({'object':o['id'],'point':p['name'],'sealed':True,**x})
checks_q=[]
for x in q:
 v=Path(x['source']).read_text()
 if x['field']!='text':
  v=json.loads(v)
  assert v['id']==x['event']
  for k in x['field'].split('.'):v=v[k]
 checks_q.append({**x,'exact_match':x['quote'] in v,'source_sha256':sha(x['source']),'semantic_caveat':'封存event34不是invoice；工作结果已撤回其证明作用' if x.get('sealed') and x.get('event')==34 else ''})
save(C/'quote_checks.json',checks_q)
original=load(C/'input_hashes_before.json');changed=[p for p,h in original.items() if not Path(p).exists() or sha(p)!=h]
current={str(p) for d in ['notes','records'] for p in Path(d).rglob('*') if p.is_file() and '__pycache__' not in str(p) and p.parts[1][:3].isdigit() and 18<=int(p.parts[1][:3])<=38}|{'docs/标注手册_v3.1.md','docs/标注手册_v3.2.md'}
headers={}
for k in ['objects','points']:
 with open(R/f'038_{k}.csv') as f:h=next(csv.reader(f))
 h[-1]='021旧标签'
 with open(R/f'039_{k}.csv') as f:headers[k]=next(csv.reader(f))==h
pm={(p['对象编号'],p['错误点名称']):p for p in points}
checks={'expected_scope_40_plus_2':formal==raw-pilots and len(formal)==40 and len(cal)==2 and len(raw&pilots)==4,'task_counts_8_10_11_11':dict(collections.Counter(x['task'] for x in scope['formal']))=={'impl-008':8,'impl-009':10,'impl-010':11,'impl-011':11},'completed_scope_exactly_2_calibration':len(objects)==2 and {o['对象编号'] for o in objects}==cal,'formal_not_claimed_complete':not(formal&{o['对象编号'] for o in objects}),'point_keys_unique':len(pm)==len(points),'point_scope_exact':{p['对象编号'] for p in points}==cal,'five_grades_legal':all(p['是否说出（五档）'] in levels for p in points),'role_values_legal':all(p['角色'] in ['主要','并列','参与','非原因'] for p in points),'headers_match_038_except_last_column':all(headers.values()),'021_old_labels_verbatim':all(o['021旧标签']==old[o['对象编号']] for o in objects+points),'grade1_disclosed_category_consistency':all((p['是否说出（五档）']==levels[0])==(p['类别'] in ['已说出的选择','已说出的降级']) for p in points if p['类别'] in ['Unstated Choice','Quiet Downgrade','已说出的选择','已说出的降级']),'all_quote_text_matches':all(x['exact_match'] for x in checks_q),'grade1_2_only_delivery':all(a['evidence'] and all(q['kind']=='delivery' and q['field']=='args.final_thought' for q in a['evidence']) for a in audit if a['grade'] in [1,2]),'audit_matches_points':len(audit)==len(points) and all(a['是否说出']==pm[a['对象编号'],a['错误点名称']]['是否说出（五档）'] for a in audit),'protected_files_unchanged':not changed and current==set(original),'blind_seal_unchanged':sha(seal['path'])==seal['sha256']==comp['sealed_sha256'],'annotations_exactly_2':{p.stem.removeprefix('039_') for p in (R/'039_annotations').glob('*.md')}==cal,'formal_evidence_catalog_40':len(catalog)==40 and {x['object'] for x in catalog}==formal,'formal_contract_and_sql_verified':all(x['contract_matches_original'] and x['complete_contract_present_in_initial_prompt'] and x['package_sql_matches_delivered'] for x in catalog),'verification_budget_including_reused_le5':all(x['reused_verification_query_count']<=5 for x in catalog) and all(x['verification_query_count']<=5 for x in working),'six_direct_raw_mismatches':len(load(C/'raw_integrity_review.json'))==6 and all(q['initial_eq_agent'] and not q['gold_eq_agent'] and q['diagnostic']['initial']['content_hash']['sha256']==q['diagnostic']['agent']['content_hash']['sha256']!=q['diagnostic']['gold']['content_hash']['sha256'] for o in load(C/'raw_integrity_review.json') for q in o['checks']),'025_three_CS_evidence_preserved':len(load(C/'fact_corrections.json')['025'])==3}
checks['formal_original_sources_rechecked']=all(sha(x['package'])==x['package_sha256'] and sha(x['agent_sql'])==x['agent_sql_sha256'] for x in catalog)
for k,d in load(C/'delivery_sources.json').items():
 checks['finish_verified_'+k]=len(d['finish'])==1 and all(load(x['path'])['args']['final_thought']==x['text'] and sha(x['path'])==x['sha256'] for x in d['finish'])
rank=[]
for o in working:
 best=max(tuple(p['reduction']) for p in o['points']);w={p['name'] for p in o['points'] if tuple(p['reduction'])==best};actual={p['name'] for p in o['points'] if p['role'] in ['主要','并列']};rank.append(w==actual)
 for p in o['points']:
  rank.append(p['reduction']==[o['baseline']['L0'][k]-p['scales']['L0'][k] for k in ['row_scale','cell_scale']])
checks['working_row_then_cell_ranking']=all(rank)
combo=load(C/'calibration_combo.json');base=load(R/'021_reruns_impl-030_stg_zuora__invoice.json')['runs'][0]['comparison'];checks['combo_baseline_equals_reused']=combo['runs'][0]['comparison']==base;checks['combo_full_match_L0_L3']=all(x['row_scale']==x['cell_scale']==0 for x in combo['runs'][-1]['comparison']['levels'])
checks['calibration_csv_snapshot']=load(C/'calibration_working_rows_before_phase2.json')=={'objects':objects,'points':points,'audit':audit}
result={'status':'phase1_complete' if all(checks.values()) else 'validation_failed','task_complete':False,'phase1_complete':all(checks.values()),'expected_scope':{'formal':40,'calibration':2,'total':42},'completed_scope':{'formal':0,'calibration':2,'total':2},'pending_formal':sorted(formal),'point_count':len(points),'quote_count':len(checks_q),'protected_file_count':len(original),'protected_changed':changed,'checks':checks,'limitations':['阶段一验证仅证明准备和2张校准完成，尚未完成40张正式表标注或42张最终验证。','引句逐字匹配不是语义证明；盲标event34错配已单列并在工作结果撤回。'],'new_database_execution':'仅039校准组合诊断，in-memory私有副本，src/gold READ_ONLY；无新增核实查询','sealed_sha256':seal['sha256']}
save(C/'validation.json',result)
print(json.dumps({k:result[k] for k in ['status','task_complete','completed_scope','point_count','quote_count','protected_file_count']},ensure_ascii=False));failed=[k for k,v in checks.items() if not v];print('failed',failed);assert not failed
