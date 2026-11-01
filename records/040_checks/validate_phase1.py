from pathlib import Path
import json,csv,hashlib,collections
R=Path('records');C=R/'040_checks'
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):return list(csv.DictReader(open(p)))
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
sc=load(R/'040_scope.json');formal={r['task']+'_'+r['table'] for r in sc['formal']};cal=set(sc['calibration'])
source={r['task']+'_'+r['table'] for r in rows(R/'013_statuses.csv') if r['status']=='待标注' and r['task'] in ['impl-012','impl-013','impl-014']};pilots={r['对象编号'] for r in rows(R/'036_objects.csv')}
o=rows(R/'040_objects.csv');p=rows(R/'040_points.csv');working=load(C/'calibration_working.json');catalog=load(C/'evidence_catalog.json');audit=load(C/'disclosure_audit.json');seal=load(C/'calibration_seal.json');comp=load(R/'040_calibration_comparison.json');handoff=load(C/'phase1_handoff.json')
levels=['交付物里针对本处说明了','交付物里只有通用说明','过程中意识到了，交付物里没提','看到了相关信息，但没有意识到的迹象','没有迹象'];old={d['task']+'_'+d['table']:d['main'] for d in load(R/'022_calibration_blind_decisions.json')['decisions']}
qs=[]
for q in load(C/'quote_inventory.json'):
 text=Path(q['path']).read_text()
 if q['field']!='text':
  v=json.loads(text)
  if 'event' in q:assert v['id']==q['event']
  for k in q['field'].split('.'):v=v[k]
  text=v
 qs.append({**q,'exact_match':q['quote'] in text,'source_sha256':sha(q['path'])})
save(C/'quote_checks.json',qs)
protected=load(C/'protected_hashes_before.json');changed=[s for s,h in protected.items() if not Path(s).is_file() or sha(s)!=h]
current={str(p) for d in ['notes','records'] for p in Path(d).rglob('*') if p.is_file() and p.relative_to(d).parts[0][:3].isdigit() and 18<=int(p.relative_to(d).parts[0][:3])<=39}|{'docs/标注手册_v3.1.md','docs/标注手册_v3.2.md'}
headers=[]
for k in ['objects','points']:
 h=next(csv.reader(open(R/f'039_{k}.csv')));h[-1]='022旧标签';headers.append(h==next(csv.reader(open(R/f'040_{k}.csv'))))
rank=[];scales=[]
for obj in working:
 best=max(tuple(x['reduction']) for x in obj['points']);winners={x['name'] for x in obj['points'] if tuple(x['reduction'])==best}
 rank.append(winners=={x['name'] for x in obj['points'] if x['role'] in ['主要','并列']})
 for x in obj['points']:
  d=load(x['rerun_source']);base=next(r['comparison']['levels'] for r in d['runs'] if r['label']=='baseline');run=next(r['comparison']['levels'] for r in d['runs'] if r['label']==x['rerun_label']);scales.append(base==x['baseline'] and run==x['single_change'])
  rank.append(x['reduction']==[base[0]['row_scale']-run[0]['row_scale'],base[0]['cell_scale']-run[0]['cell_scale']])
pm={(x['对象编号'],x['错误点名称']):x for x in p}
checks={'scope_38_plus_2':formal==source-pilots and len(formal)==38 and len(cal)==2 and len(source&pilots)==3,'counts_7_18_13':dict(collections.Counter(x['task'] for x in sc['formal']))=={'impl-012':7,'impl-013':18,'impl-014':13},'completed_only_2_calibration':len(o)==2 and {x['对象编号'] for x in o}==cal,'formal_not_claimed_complete':not formal&{x['对象编号'] for x in o},'point_keys_unique':len(pm)==len(p),'five_grades_legal':all(x['是否说出（五档）'] in levels for x in p),'point_scope_exact':{x['对象编号'] for x in p}==cal,'roles_legal':all(x['角色'] in ['主要','并列','参与','非原因'] for x in p),'headers_match_039_except_last':all(headers),'022_old_main_verbatim':all(x['022旧标签']==old[x['对象编号']] for x in o+p),'grade1_disclosed_consistency':all((x['是否说出（五档）']==levels[0])==(x['类别'] in ['已说出的选择','已说出的降级']) for x in p if x['类别'] in ['Unstated Choice','Quiet Downgrade','已说出的选择','已说出的降级']),'grade1_2_only_deliverables':all(all(q['field']=='args.final_thought' for q in x['evidence']) for x in audit if x['grade'] in [1,2]),'audit_matches_points':len(audit)==len(p) and all(x['是否说出']==pm[x['对象编号'],x['错误点名称']]['是否说出（五档）'] for x in audit),'quotes_exactly_match':all(x['exact_match'] for x in qs),'protected_files_unchanged':not changed and current==set(protected),'sealed_unchanged':sha(seal['path'])==seal['sha256']==comp['sealed_sha256'],'comparison_unchanged':sha(R/'040_calibration_comparison.json')==handoff['comparison_sha256'],'annotations_exactly_2':{x.stem.removeprefix('040_') for x in (R/'040_annotations').glob('*.md')}==cal,'row_then_cell_ranking':all(rank),'rerun_scales_exact':all(scales),'catalog_38_exact':len(catalog)==38 and {x['object'] for x in catalog}==formal,'catalog_contract_sql_originals_match':all(x['contract_matches_original'] and x['package_sql_matches_delivered'] and sha(x['agent_sql'])==x['agent_sql_sha256'] and sha(x['package'])==x['package_sha256'] for x in catalog),'query_budget_including_failures_le5':all(x['verification_query_count_including_failures']<=5 for x in catalog+working),'raw_difference_list_empty':all(not x['013_difference_entries'] and x['013_all_columns_types_and_row_counts_equal'] for x in load(C/'raw_integrity_review.json'))}
for t,d in load(C/'delivery_sources.json').items():checks['finish_verified_'+t]=len(d['finish'])==1 and d['result_matches_finish'] and all(load(x['path'])['args']['final_thought']==x['text'] and sha(x['path'])==x['sha256'] for x in d['finish'])
result={'status':'phase1_complete' if all(checks.values()) else 'validation_failed','task_complete':False,'phase1_complete':all(checks.values()),'expected_scope':{'formal':38,'calibration':2,'total':40},'completed_scope':{'formal':0,'calibration':2,'total':2},'pending_formal':sorted(formal),'point_count':len(p),'quote_count':len(qs),'protected_file_count':len(protected),'protected_changed':changed,'checks':checks,'limitations':['这是阶段一验证；38张正式表尚未标注，40张最终验证尚未完成。','38张证据索引的契约/SQL字节校验不等于已完成逐点分类。','引用原文匹配是机械核验，是否支持结论仍需语义审查。'],'database_execution':'没有新查询/重跑；没有打开数据库。','sealed_sha256':seal['sha256']}
save(C/'validation.json',result);print(json.dumps({k:result[k] for k in ['status','task_complete','completed_scope','point_count','quote_count','protected_file_count']},ensure_ascii=False));failed=[k for k,v in checks.items() if not v];print('failed',failed);assert not failed
