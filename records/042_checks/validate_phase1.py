from pathlib import Path
import json,csv,hashlib,collections
R=Path('records');C=R/'042_checks'
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):return list(csv.DictReader(open(p)))
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
sc=load(R/'042_scope.json');formal={x['object_id'] for x in sc['formal']};cal=set(sc['calibration']);source={r['task']+'_'+r['table'] for r in rows(R/'013_statuses.csv') if r['status']=='待标注' and r['task'] in {f'impl-{n:03}' for n in range(15,22)}};pilots={r['对象编号'] for r in rows(R/'036_objects.csv')}
o=rows(R/'042_objects.csv');p=rows(R/'042_points.csv');w=load(C/'calibration_working.json');cat=load(C/'evidence_catalog.json');audit=load(C/'disclosure_audit.json');receipt=load(C/'calibration_seal_receipt.json');comp=load(R/'042_calibration_comparison.json');handoff=load(C/'phase1_handoff.json');old={x['task']+'_'+x['table']:x['category'] for x in load(R/'023_decisions.json')}
levels=['交付物里针对本处说明了','交付物里只有通用说明','过程中意识到了，交付物里没提','看到了相关信息，但没有意识到的迹象','没有迹象']
quotes=[]
for q in load(C/'quote_inventory.json'):
 text=Path(q['path']).read_text()
 if q['field']!='text':
  value=json.loads(text)
  if 'event' in q:assert value['id']==q['event']
  for key in q['field'].split('.'):value=value[key]
  text=value
 quotes.append({**q,'exact_match':q['quote'] in text,'source_sha256':sha(q['path'])})
save(C/'quote_checks.json',quotes)
protected=load(C/'protected_hashes_before.json');changed=[s for s,h in protected.items() if not Path(s).is_file() or sha(s)!=h]
current={str(p) for root in ['notes','records'] for p in Path(root).rglob('*') if p.is_file() and p.relative_to(root).parts[0][:3].isdigit() and 18<=int(p.relative_to(root).parts[0][:3])<=41}|{'docs/标注手册_v3.1.md','docs/标注手册_v3.2.md'}
headers=[]
for k in ['objects','points']:
 h=next(csv.reader(open(R/f'040_{k}.csv')));h[-1]='023旧标签';headers.append(h==next(csv.reader(open(R/f'042_{k}.csv'))))
rank=[];scales=[]
for obj in w:
 best=max(tuple(x['reduction']) for x in obj['points']);winners={x['name'] for x in obj['points'] if tuple(x['reduction'])==best};rank.append(winners=={x['name'] for x in obj['points'] if x['role'] in ['主要','并列']})
 for x in obj['points']:
  d=load(x['run_source']);base=next(r['comparison']['levels'] for r in d['runs'] if r['label']=='baseline');run=next(r['comparison']['levels'] for r in d['runs'] if r['label']==x['run']);scales.append(base==x['baseline_levels'] and run==x['after_levels']);rank.append(x['reduction']==[base[0]['row_scale']-run[0]['row_scale'],base[0]['cell_scale']-run[0]['cell_scale']])
pm={(x['对象编号'],x['错误点名称']):x for x in p}
checks={'scope_39_plus_2':formal==source-pilots and len(formal)==39 and len(cal)==2 and len(source&pilots)==7 and not formal&cal,'formal_counts':dict(collections.Counter(x['task'] for x in sc['formal']))==dict(zip([f'impl-{i:03}' for i in range(15,22)],[4,4,9,9,3,4,6])),'completed_only_2_calibration':len(o)==2 and {x['对象编号'] for x in o}==cal,'formal_not_claimed_complete':not formal&{x['对象编号'] for x in o},'point_keys_unique':len(pm)==len(p),'five_grades_legal':all(x['是否说出（五档）'] in levels for x in p),'point_scope_exact':{x['对象编号'] for x in p}==cal,'roles_legal':all(x['角色'] in ['主要','并列','参与','非原因'] for x in p),'headers_match_040_except_last':all(headers),'023_old_main_verbatim':all(x['023旧标签']==old[x['对象编号']] for x in o+p),'grade1_disclosed_consistency':all((x['是否说出（五档）']==levels[0])==(x['类别'] in ['已说出的选择','已说出的降级']) for x in p if x['类别'] in ['Unstated Choice','Quiet Downgrade','已说出的选择','已说出的降级']),'grade1_2_only_deliverables':all(all(q['field']=='args.final_thought' for q in x['evidence']) for x in audit if x['grade'] in [1,2]),'audit_matches_points':len(audit)==len(p) and all(x['是否说出']==pm[x['对象编号'],x['错误点名称']]['是否说出（五档）'] for x in audit),'quotes_exactly_match':all(x['exact_match'] for x in quotes),'protected_files_unchanged':not changed and current==set(protected),'sealed_unchanged':sha(receipt['path'])==receipt['sha256']==comp['sealed_sha256'],'post_unblind_change_visible':comp['blind_main_matches']==1 and comp['final_main_matches']==2 and comp['final_is_not_blind_agreement'] and load(receipt['path'])['objects'][0]['main']=='其他' and w[0]['main']=='Unstated Choice','phase1_calibration_files_unchanged':all(sha(s)==h for s,h in handoff['protected_calibration_files'].items()),'annotations_exactly_2':{x.stem.removeprefix('042_') for x in (R/'042_annotations').glob('*.md')}==cal,'row_then_cell_ranking':all(rank),'rerun_scales_exact':all(scales),'catalog_39_exact':len(cat)==39 and {x['object_id'] for x in cat}==formal,'catalog_contract_sql_originals_match':all(x['contract_matches_original'] and x['sql_matches_package'] and sha(x['agent_sql'])==x['agent_sql_sha256'] and sha(x['package'])==x['package_sha256'] and sha(x['contract_path'])==x['contract_sha256'] for x in cat),'catalog_contract_present_39':all(x['contract_present_in_initial_prompt'] for x in cat),'query_budget_including_failures_le5':all(x['verification_query_count_including_failures']<=5 for x in cat) and all(x['verification_query_count_including_read_duplicate']<=5 for x in w),'raw_seven_tasks_catalogued':len(load(C/'raw_integrity_review.json'))==7,'026_fact_preparation_documented':len(load(C/'fact_corrections.json')['items'])==2,'prefix_files_match':all((C/f'phase1_{k}_prefix.csv').read_bytes()==(R/f'042_{k}.csv').read_bytes() for k in ['objects','points'])}
for task,d in load(C/'delivery_sources.json').items():
 checks['finish_verified_'+task]=len(d['finish'])==1 and all(load(x['path'])['args']['final_thought']==x['text'] and sha(x['path'])==x['sha256'] for x in d['finish'])
result={'status':'phase1_complete' if all(checks.values()) else 'validation_failed','task_complete':False,'phase1_complete':all(checks.values()),'expected_scope':{'formal':39,'calibration':2,'total':41},'completed_scope':{'formal':0,'calibration':2,'total':2},'pending_formal':sorted(formal),'point_count':len(p),'quote_count':len(quotes),'protected_file_count':len(protected),'protected_changed':changed,'checks':checks,'limitations':['这是阶段一验证；39张正式表尚未逐点标注，最终41张覆盖检查待第二阶段完成。','契约/SQL字节核对不等于逐点分类；026事实准备中的暂定判断未纳入正式CSV。','impl-024留存result.md与finish最后一句环境说明文字不同；披露引用句两者一致，采用finish原句。','原文匹配为机械校验，不代替语义审查。'],'database_execution':'未打开数据库；没有新查询/重跑。','sealed_sha256':receipt['sha256']}
save(C/'validation.json',result)
print(json.dumps({k:result[k] for k in ['status','task_complete','completed_scope','point_count','quote_count','protected_file_count']},ensure_ascii=False));bad=[k for k,v in checks.items() if not v];print('failed:',bad);assert not bad
