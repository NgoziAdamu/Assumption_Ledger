"""解盲后对比036；封存件只读。输出工作结果与逐项差异。"""
from pathlib import Path
import json,csv,hashlib,copy,datetime
R=Path(__file__).resolve().parents[2]
def read(p):return json.loads((R/p).read_text())
def write(p,v):(R/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
seal=read('records/038_checks/calibration_seal.json');assert hashlib.sha256((R/seal['sealed_path']).read_bytes()).hexdigest()==seal['sha256']
blind=read(seal['sealed_path']);working=copy.deepcopy(blind['objects'])
oldobjs={r['对象编号']:r for r in csv.DictReader((R/'records/036_objects.csv').open())}
oldpts={(r['对象编号'],r['错误点名称']):r for r in csv.DictReader((R/'records/036_points.csv').open())}
names={'latitude':'latitude_range','url':'url_rule','key':'key_formula','phone_user':'user_phone_no_repair','phone_contact':'contact_phone_no_repair'}
generic={'impl-002':(59,'Contract-directed deletion removes unusable rows and nullification retains records while setting invalid optional values to NULL.'),'impl-025':(41,'依契约的清理策略处理非法日期、枚举、电话和字段值；需要丢弃的记录按整行过滤，非关键字段则置为 NULL。')}
rows=[];ors=[]
for o in working:
 id=o['对象编号'];ref=oldobjs[id];ors.append({'对象编号':id,'blind_main':o['主要原因'],'036_main':ref['主要原因'],'main_agrees':o['主要原因']==ref['主要原因'],'blind_tied_categories':o['并列项'],'036_tied_items':ref['并列项'],'blind_confidence':o['把握'],'036_confidence':ref['把握'],'confidence_agrees':o['把握']==ref['把握'],'resolution':'主因一致；仍保持本次高把握，020逐列单改和契约/交付原文均能定下，不为与036一致回改把握。'})
 for p in o['points']:
  ref=oldpts[(id,names[p['run_label']])];r={'对象编号':id,'blind_point':p['错误点名称'],'036_point':ref['错误点名称'],'blind_category':p['类别'],'036_category':ref['类别'],'category_agrees':p['类别']==ref['类别'],'blind_role':p['角色'],'036_role':ref['角色'],'role_agrees':p['角色']==ref['角色'],'blind_disclosure':p['是否说出（五档）'],'036_disclosure':ref['是否说出（五档）'],'disclosure_agrees':p['是否说出（五档）']==ref['是否说出（五档）'],'presence_agrees':p['证据在场']==ref['证据在场'],'previous_correct_agrees':p['曾经理解对过']==ref['曾经理解对过']}
  p['blind_disclosure_grade']=p['disclosure_grade']
  if p['run_label'] in ['url','phone_user','phone_contact']:
   task=id[:8];n,text=generic[task];path=next((R/f'data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/{task}/agent/.events').glob(f'sessions/*/events/{n}.json'));e=json.loads(path.read_text());assert text in e['args']['final_thought']
   p['是否说出（五档）']='交付物里只有通用说明';p['disclosure_grade']=2;p['disclosure_evidence']=[dict(path=str(path.relative_to(R)),event=n,field='args.final_thought',quote=text)]
   p['disclosure_reason']='解盲后修订：交付报告中的清理/置空策略虽未点名本字段，但明确涉及本类处理，按036及037第2档口径接受；不是第1档。盲标把这类策略全部视作一般完成声明，判得过窄。'
   r['resolution']=p['disclosure_reason'];r['delivered_quote']=p['disclosure_evidence'][0]
  else:r['resolution']='维持盲标第4档。键生成只是工作清单；latitude不是契约定下的清理规则，不能把其他字段的通用策略扩张为本处披露。'
  r['working_disclosure']=p['是否说出（五档）'];rows.append(r)
 o['delivery_review']['working_resolution']='盲标delivery_review原文保留于封存件。工作行以每点disclosure_reason为准；URL和两项电话改第2档，latitude与key仍第4档。'
write('records/038_checks/calibration_working.json',working)
result={'task':'038','compared_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'blind_seal_sha256':seal['sha256'],'036_sources':['records/036_objects.csv','records/036_points.csv','records/036_checks/disclosure_audit.json'],'main_agreement':{'agree':sum(r['main_agrees'] for r in ors),'total':2},'point_category_agreement':{'agree':sum(r['category_agrees'] for r in rows),'total':5},'point_role_agreement':{'agree':sum(r['role_agrees'] for r in rows),'total':5},'point_disclosure_agreement':{'agree':sum(r['disclosure_agrees'] for r in rows),'total':5},'object_all_point_disclosure_agreement':{'agree':sum(all(r['disclosure_agrees'] for r in rows if r['对象编号']==o['对象编号']) for o in ors),'total':2},'object_confidence_agreement':{'agree':sum(r['confidence_agrees'] for r in ors),'total':2},'objects':ors,'points':rows,'rule_resolution':'037报告明确对行规模相同时按格子比较。guide_event 两主点各减15000格，latitude减13655格；沿用037读法，不记只能组合修复。此结论与036一致。','sealed_file_modified':False,'warning':'所有盲标一致率均按封存件计算，不能用修订后的工作结果提高一致率。'}
write('records/038_calibration_comparison.json',result)
assert hashlib.sha256((R/seal['sealed_path']).read_bytes()).hexdigest()==seal['sha256']
print(json.dumps({k:v for k,v in result.items() if 'agreement' in k},ensure_ascii=False))
