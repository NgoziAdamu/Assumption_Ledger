"""037 最终45表验证；只写037验证结果，不重建或覆盖封存/保护基线。"""
from pathlib import Path
import json,csv,hashlib,re,subprocess,collections
R=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads((R/p).read_text())
def write(p,v):(R/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def csvread(p):return list(csv.DictReader((R/p).open()))
scope=read('records/037_scope.json');formal={r['task']+'_'+r['table'] for r in scope['objects']};cal={'impl-008_int_asana__task_projects','impl-021_int_klaviyo__person_metrics'}
objects=csvread('records/037_objects.csv');pts=csvread('records/037_points.csv');done={x['对象编号'] for x in objects};audit=read('records/037_checks/disclosure_audit.json');fd=read('records/037_checks/formal_decisions.json')
levels=['交付物里针对本处说明了','交付物里只有通用说明','过程中意识到了，交付物里没提','看到了相关信息，但没有意识到的迹象','没有迹象'];allowed={'Data Misconception','Intent Misreading','Unstated Choice','Quiet Downgrade','Form Mismatch','已说出的选择','已说出的降级','代码写错','其他','不可评估','无法判定'}
headers={}
for name in ['objects','points']:
 with (R/f'records/036_{name}.csv').open() as f:expected=next(csv.reader(f))
 expected[-1]='019旧标签'
 with (R/f'records/037_{name}.csv').open() as f:headers[name]=next(csv.reader(f))==expected
keys=[(p['benchmark'],p['对象编号'],p['错误点名称']) for p in pts];pm={(p['对象编号'],p['错误点名称']):p for p in pts}
assert len(pm)==len(pts);assert {(a['对象编号'],a['错误点名称']) for a in audit}==set(pm)
for a in audit:assert a['grade'] in range(1,6) and a['是否说出']==levels[a['grade']-1]==pm[a['对象编号'],a['错误点名称']]['是否说出（五档）']
cache={};checked=[]
def check(ev,id,point,kind):
 path=R/ev['source'];k=str(path)
 if k not in cache:cache[k]=path.read_text()
 raw=cache[k];v=json.loads(raw) if ev.get('event') else raw
 if ev.get('event'):
  n,field=ev['event'].split('.',1)
  for key in field.split('.'):v=v[key]
 checked.append(dict(object=id,point=point,kind=kind,source=ev['source'],event=ev.get('event'),quote=ev['quote'],match=ev['quote'] in v,source_sha256=hashlib.sha256(raw.encode()).hexdigest()))
for a in audit:
 for ev in a['evidence']:check(ev,a['对象编号'],a['错误点名称'],'披露/相关信息')
for ev in read('records/037_checks/formal_quote_inventory.json'):check(ev,ev['object'],ev['point'],ev['kind'])
for o in read('records/037_calibration_blind_sealed.json')['objects']:
 for p in o['points']:
  for ev in p['evidence_presence_quotes']:check({'source':ev['path'],'event':str(ev['event'])+'.'+ev['field'],'quote':ev['quote']},o['对象编号'],p['错误点名称'],'校准在场')
write('records/037_checks/quote_checks.json',checked)
before=read('records/037_checks/input_hashes_before.json');changed=[p for p,h in before.items() if not (R/p).exists() or sha(R/p)!=h]
nb=read('records/037_checks/protected_notes_git_baseline.json');notes_changed=[p for p,h in nb['hashes'].items() if not (R/p).exists() or sha(R/p)!=h]
seal=read('records/037_checks/calibration_seal.json');manual=read('records/037_checks/manual_copy.json');cmp=subprocess.run(['cmp',manual['source'],str(R/manual['destination'])]).returncode
snap=read('records/037_checks/calibration_working_rows_before_phase2.json');cal_unchanged=snap=={'objects':[x for x in objects if x['对象编号'] in cal],'points':[x for x in pts if x['对象编号'] in cal],'audit':[x for x in audit if x['对象编号'] in cal]}
# Recompute range from prescribed source, and cross-check excluded pilots against036 objects.
raw=csvread('records/013_statuses.csv');selected={r['task']+'_'+r['table'] for r in raw if r['status']=='待标注' and r['task'] in [f'impl-{i:03}' for i in range(1,6)]};pilots={r['对象编号'] for r in csvread('records/036_objects.csv')};current=selected-pilots
old={r['题目']+'_'+r['表']:r['主要原因类别'] for r in csvread('records/019_annotations/019_summary.csv')}
# An intervention changes one specified location; reconstruct exact executed SQL from frozen baseline + recorded edit.
rerunchecks=[];superseded=0;newruns=0
for file in sorted((R/'records/037_checks').glob('rerun_impl-*.json')):
 j=json.loads(file.read_text());orig=(R/j['baseline_sql_path']).read_text();assert hashlib.sha256(orig.encode()).hexdigest()==j['baseline_sql_sha256'];superseded+=len(j.get('superseded_probes',[]))
 for run in j['runs']:
  if run['label']=='baseline':continue
  newruns+=1;ed=run['edits'];single=len(ed)==1 and orig.count(ed[0]['old'])==1 if ed else run['kind']=='呈现诊断'
  sql=orig.replace(ed[0]['old'],ed[0]['new'],1) if ed else run['sql'];frozen=not re.search(r'\bcurrent_timestamp\b|\bcurrent_date\b',sql,re.I)
  rerunchecks.append({'object':j['object'],'label':run['label'],'single_location_or_presentation_only':single,'clock_frozen':frozen,'levels':len(run['comparison']['levels'])==4,'sql_sha256_reconstructed':hashlib.sha256(sql.encode()).hexdigest(),'original_databases_read_only':j['original_databases_read_only'],'private_database':j['private_database']})
write('records/037_checks/rerun_validation.json',rerunchecks)
plan=read('records/037_checks/new_patch_plan.json');actual={(x['object'],x['label']) for x in rerunchecks};expected={(id,p['label']) for id,ps in plan.items() for p in ps}
cat=read('records/037_checks/evidence_catalog.json');contractchecks=[]
for id,o in cat.items():
 e=read(o['event_path']);v=e
 for k in o['field'].split('.'):v=v[k]
 contractchecks.append(dict(object=id,event_path=o['event_path'],event=o['event'],field=o['field'],complete_model_contract_in_observed_event=o['event_contract'] in v,contract_truncated=o['contract_truncated'],source='初始任务事件直接提供；不是被截断的cat输出'))
write('records/037_checks/contract_visibility.json',contractchecks)
allformalpoints=[p for o in fd for p in o['points']]
rank_ok=True
for o in fd:
 ps=o['points'];best=max(tuple(p['reduction']) for p in ps);w={p['name'] for p in ps if tuple(p['reduction'])==best and best>(0,0)}
 actualw={p['name'] for p in ps if p['role'] in ['主要','并列']};rank_ok &= w==actualw or (not w and all(p['category']=='其他' for p in ps))
formaldata=[p for p in allformalpoints if p['category']=='Data Misconception'];datagate=all(p.get('P') and p.get('data_refutation') and p.get('data_algorithm_gate') for p in formaldata)
reused=collections.Counter(q['task']+'_'+q['table'] for q in read('records/019_queries.json') if q.get('kind')=='核实' and q['task']+'_'+q['table'] in formal)
result={'status':'complete','task_complete':done==formal|cal,'expected_scope':{'formal':43,'calibration':2,'total':45},'scope_checked':len(formal)==43 and current==formal and len(selected & pilots)==5,'completed_scope':{'formal':len(done&formal),'calibration':len(done&cal),'total':len(done)},'missing_formal_objects':sorted(formal-done),'unexpected_objects':sorted(done-formal-cal),'object_count_unique':len(done)==len(objects),'point_count':len(pts),'formal_point_count':len(allformalpoints),'point_keys_unique':len(keys)==len(set(keys)),'all_objects_have_points':{p['对象编号'] for p in pts}==done,'annotation_files_exactly_45':{p.stem.removeprefix('037_') for p in (R/'records/037_annotations').glob('*.md')}==done,'csv_headers_match_036_with_last_column_renamed':headers,'old_019_labels_verbatim_in_all_rows':all(p['019旧标签']==old[p['对象编号']] for p in objects+pts),'five_grade_values_legal':all(p['是否说出（五档）'] in levels for p in pts),'point_categories_legal':all(p['类别'] in allowed for p in pts),'roles_legal':all(p['角色'] in ['主要','并列','参与','非原因'] for p in pts),'formal_roles_follow_row_then_cell_ranking':rank_ok,'disclosed_categories_and_grade_1_consistent':all((p['是否说出（五档）']==levels[0])==(p['类别'] in ['已说出的选择','已说出的降级']) for p in pts if p['类别'] in ['Unstated Choice','Quiet Downgrade','已说出的选择','已说出的降级']),'quote_count':len(checked),'quote_checks_all_pass':all(x['match'] for x in checked),'grade_1_2_have_deliverable_quotes':all(a['evidence'] and all('final_thought' in e['event'] or e['source'].endswith('.sql') for e in a['evidence']) for a in audit if a['grade'] in [1,2]),'grade_3_count':sum(a['grade']==3 for a in audit),'grade_3_have_mid_event_doubt_or_alternative_quotes':all(a['evidence'] and all('final_thought' not in e['event'] for e in a['evidence']) for a in audit if a['grade']==3),'formal_contract_visibility_all_checked':all(x['complete_model_contract_in_observed_event'] and not x['contract_truncated'] for x in contractchecks),'formal_data_algorithm_gate_and_P_verified':datagate,'protected_records_and_v31_count':len(before),'protected_records_and_v31_changed':changed,'protected_notes_count':len(nb['hashes']),'protected_notes_changed':notes_changed,'protected_notes_original_baseline_commit':nb['commit'],'protected_018_036_and_v31_unchanged':not changed and not notes_changed,'manual_cmp_exit':cmp,'manual_source_sha256_matches':sha(Path(manual['source']))==manual['sha256']==sha(R/manual['destination']),'blind_seal_unchanged':sha(R/seal['sealed_path'])==seal['sha256'],'calibration_working_rows_unchanged_in_phase2':cal_unchanged,'calibration_main_agreement':read('records/037_calibration_comparison.json')['main_agreement'],'new_verification_queries':{id:0 for id in sorted(done)},'reused_formal_verification_query_count':dict(reused),'verification_query_limit_le_5':all(n<=5 for n in reused.values()),'new_formal_reruns_and_presentation_probes':newruns,'superseded_probes_excluded':superseded,'new_patch_plan_all_executed':expected==actual,'new_reruns_single_location_private_readonly_frozen_L0_L3':all(x['single_location_or_presentation_only'] and x['clock_frozen'] and x['levels'] and x['original_databases_read_only'] and x['private_database']==':memory:' for x in rerunchecks),'note':'43正式表统计与2校准分开；工作CSV为解盲后结果，盲标一致率只取封存件。早期失败/修订探针保留审计，但不参与最终分类规模。验证完整性不表示每个单点恢复都能消除全部差异；负贡献和遮蔽已逐表列明。'}
flags=[v for k,v in result.items() if isinstance(v,bool)];assert all(flags),{k:v for k,v in result.items() if isinstance(v,bool) and not v};assert cmp==0 and all(headers.values())
write('records/037_checks/validation.json',result)
print(json.dumps({k:result[k] for k in ['status','task_complete','completed_scope','point_count','quote_count','quote_checks_all_pass','new_formal_reruns_and_presentation_probes','protected_018_036_and_v31_unchanged','blind_seal_unchanged']},ensure_ascii=False))
