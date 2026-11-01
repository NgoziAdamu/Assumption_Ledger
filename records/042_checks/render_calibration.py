from pathlib import Path
import json,csv,hashlib,copy
from datetime import datetime,timezone
R=Path('records');C=R/'042_checks';A=R/'042_annotations';A.mkdir(exist_ok=True)
def load(p):return json.loads(Path(p).read_text())
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
levels=['交付物里针对本处说明了','交付物里只有通用说明','过程中意识到了，交付物里没提','看到了相关信息，但没有意识到的迹象','没有迹象']
sealed=load(R/'042_calibration_blind_sealed.json');work=copy.deepcopy(sealed['objects'])
# 解盲后的修订与盲标结果分开保存，封存件不写。
change='盲标将country编码看作形式未规定；解盲复核后改为Unstated Choice。该投影通过lookup选择输出键值，014查询V2显示同一numeric码有多个alpha-2候选，不能证明所有输出仅是同一内容的另一种呈现；不满足第3节只改呈现的前提。契约没有指定country编码及映射策略，故按材料没定的映射选择处理。扩行的唯一性前提仍独立归Data Misconception。不以036标签本身作证据；两种读法保留为规则问题。'
work[0]['main']='Unstated Choice';work[0]['points'][0].update(category='Unstated Choice',reason=change)
names=[['country_value_only','lookup_dedup'],['email_pattern']]
quote_inventory=[];audit=[];old={d['task']+'_'+d['table']:d['category'] for d in load(R/'023_decisions.json')}
for i,obj in enumerate(work):
 oid=obj['object_id'];task=oid.split('_')[0];table=oid[len(task)+1:];prefix='014' if i==0 else '017'
 traces=load(R/f'{prefix}_trace_{task}.json');by={e['id']:e for e in traces}
 obj['023_old_main']=old[oid];obj['verification_query_count_including_read_duplicate']=3 if i==0 else 1
 obj['seal_main']=sealed['objects'][i]['main'];obj['post_unblind_change']=change if i==0 else '无'
 sql=Path('data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01')/task/'agent'/('dacomp-de-'+task)/'sql/staging'/f'{table}.sql'
 obj['agent_sql']=str(sql);obj['agent_sql_sha256']=sha(sql);obj['sql_comments']= [x for x in sql.read_text().splitlines() if '--' in x or '/*' in x]
 pkg=R/f'013_packages/013_{task}_staging_{table}.md';pt=pkg.read_text();import re
 paths=dict(re.findall(r'^- (S\d+): `([^`]+)`',pt,re.M));con=load(paths['S10'])['contract_specification'];obj['contract_path']=con['source_path'];obj['contract_sha256']=sha(con['source_path']);obj['contract_blocks']=con['blocks']
 for block in con['blocks']:
  quote_inventory.append({'object_id':oid,'name':'contract','path':con['source_path'],'field':'text','quote':block['original_text'],'kind':'contract'})
  quote_inventory.append({'object_id':oid,'name':'contract_prompt','path':by[1]['path'],'field':'message','event':1,'quote':block['original_text'],'kind':'contract_presence'})
 for j,p in enumerate(obj['points']):
  p['display_name']=p['name'];p['name']=names[i][j];p['role']={'主要原因':'主要','参与因素':'参与'}[p['role']]
  rr=load(p['run_source']);base=next(x['comparison']['levels'] for x in rr['runs'] if x['label']=='baseline');run=next(x['comparison']['levels'] for x in rr['runs'] if x['label']==p['run'])
  p['baseline_levels']=base;p['after_levels']=run;p['reduction']=[base[0]['row_scale']-run[0]['row_scale'],base[0]['cell_scale']-run[0]['cell_scale']]
  pe=[]
  for q in p['quotes']:
   raw=by[q['event']]['path'];nq={'object_id':oid,'name':p['name'],'path':raw,'field':q['field'],'event':q['event'],'quote':q['text'],'kind':'delivery' if q['field']=='args.final_thought' else 'process'}
   pe.append(nq);quote_inventory.append(nq)
  p['verified_quote_references']=pe
  audit.append({'对象编号':oid,'错误点名称':p['name'],'grade':p['disclosure'],'是否说出':levels[p['disclosure']-1],'category':p['category'],'decision':p['disclosure_reason'],'evidence':pe,'sql_path':str(sql),'sql_comments':obj['sql_comments'],'final_event':67 if i==0 else 63,'final_checked':True,'temporary_script_comments_count_as_delivery':False})
 # 引用最终报告以说明未泛化无关的完成陈述。
 if i==0:
  q={'object_id':oid,'name':'final_exclusion','path':by[67]['path'],'field':'args.final_thought','event':67,'quote':'staging 做了基础字段投影及类型转换，并处理日期、币种、国家码和合同中明确的部分校验。','kind':'delivery_not_sufficient'};quote_inventory.append(q)
  obj['final_exclusion_quote']=q
 save(C/'calibration_working.json',work)
save(C/'quote_inventory.json',quote_inventory);save(C/'disclosure_audit.json',audit)
refobj={r['对象编号']:r for r in csv.DictReader(open(R/'036_objects.csv'))}
refp=list(csv.DictReader(open(R/'036_points.csv')))
comparison=[]
for i,obj in enumerate(work):
 oid=obj['object_id'];b=sealed['objects'][i];pr=[]
 for j,p in enumerate(obj['points']):
  ref=next(r for r in refp if r['对象编号']==oid and r['错误点名称']==p['name']);blind=b['points'][j]
  pr.append({'point':p['name'],'blind_category':blind['category'],'036_category':ref['类别'],'blind_category_match':blind['category']==ref['类别'],'blind_grade':blind['disclosure'],'036_grade':ref['是否说出（五档）'],'blind_grade_match':levels[blind['disclosure']-1]==ref['是否说出（五档）'],'final_category':p['category'],'final_grade':p['disclosure']})
 comparison.append({'object_id':oid,'blind_main':b['main'],'036_main':refobj[oid]['主要原因'],'blind_main_match':b['main']==refobj[oid]['主要原因'],'final_main':obj['main'],'post_unblind_change':obj['post_unblind_change'],'points':pr})
comp={'unblinded_at_utc':datetime.now(timezone.utc).isoformat(),'sealed_path':'records/042_calibration_blind_sealed.json','sealed_sha256':sha(R/'042_calibration_blind_sealed.json'),'reference_sources':['records/036_objects.csv','records/036_points.csv','records/034_annotations/dacomp_impl-009_stg_google_play__store_performance_country.md'],'blind_main_matches':1,'blind_main_denominator':2,'blind_point_category_matches':2,'blind_point_denominator':3,'blind_disclosure_matches':3,'blind_disclosure_denominator':3,'final_main_matches':2,'final_is_not_blind_agreement':True,'objects':comparison}
assert not (R/'042_calibration_comparison.json').exists(), '解盲对比已存在，禁止自动覆盖'
save(R/'042_calibration_comparison.json',comp)
headers={k:next(csv.reader(open(R/f'040_{k}.csv'))) for k in ['objects','points']}
for h in headers.values():h[-1]='023旧标签'
with open(R/'042_objects.csv','w') as f:
 w=csv.writer(f,lineterminator="\n");w.writerow(headers['objects'])
 for obj in work:w.writerow(['DAComp',obj['object_id'],'staging',obj['main'],'','否',obj['confidence'],obj['023_old_main'],obj['023_old_main']])
with open(R/'042_points.csv','w') as f:
 w=csv.writer(f,lineterminator="\n");w.writerow(headers['points'])
 for obj in work:
  for p in obj['points']:w.writerow(['DAComp',obj['object_id'],p['name'],p['role'],p['category'],levels[p['disclosure']-1],p['evidence_present'],p['ever_correct'],'不适用','复用；042核对原始交付物/轨迹',';'.join([p['run_source'],*obj['sources'],'records/042_checks/disclosure_audit.json']),obj['023_old_main']])
for obj in work:
 oid=obj['object_id'];parts=[f'# 042 校准标注：{oid}','## 任务','按冻结v3.2第3～8节盲标、封存后解盲。此说明为解盲后校准定稿；盲标原件不改。','## 结论',f"主要原因：**{obj['main']}**；把握{obj['confidence']}；{len(obj['points'])}个点。不是只能组合修复。023旧主要原因 `{obj['023_old_main']}` 只存档，不作分类依据。",'## 详细发现',f"盲标主因：{obj['seal_main']}。解盲后变动：{obj['post_unblind_change']}", '先排除代码写错、非agent处理原因与raw版本不同；本表复用staging agent留存raw的重跑。逐点区分纯形式、占位替代、契约明定算法和未定选择；不把gold实现当契约。按行减量优先，行数相同再比格子；不同单改减量不相加。']
 for p in obj['points']:
  parts += [f"### {p['name']}：{p['display_name']}",f"{p['role']}；**{p['category']}**；把握{p['confidence']}。",p['reason']]
  if p.get('P'):parts += ['P：'+p['P']]
  parts += [f"是否说出：第{p['disclosure']}档——{levels[p['disclosure']-1]}。{p['disclosure_reason']}",f"证据在场：{p['evidence_present']}。{p.get('evidence_reason','非探索类别不填。')}",f"曾经理解对过：{p['ever_correct']}。系统提示是否适用：不适用。",'| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |','|---|---:|---:|---:|---:|']
  for b,r in zip(p['baseline_levels'],p['after_levels']):parts += [f"| {b['level']} | {b['row_scale']} | {r['row_scale']} | {b['cell_scale']} | {r['cell_scale']} |"]
  parts += [f"来源 `{p['run_source']}` / `{p['run']}`；L0减少{p['reduction'][0]}行/{p['reduction'][1]}格。"]
  for q in p['verified_quote_references']:parts += [f"原句：`{q['path']}` / event {q['event']} / `{q['field']}`。",'```text\n'+q['quote']+'\n```']
  if p.get('verification_queries'):parts += ['核实查询：'+'；'.join(p['verification_queries'])+'。']
 if obj.get('final_exclusion_quote'):
  q=obj['final_exclusion_quote'];parts += ['最终报告的相关完成陈述：','```text\n'+q['quote']+'\n```','这句话没有说明此表选择哪种country码，也未说明lookup的非唯一性；不作第1或第2档依据。交付SQL无注释。']
 parts += ['## 证据来源',*[f'- `{x}`' for x in obj['sources']],f"- 契约：`{obj['contract_path']}`，SHA-256 `{obj['contract_sha256']}`。",f"- 交付SQL：`{obj['agent_sql']}`，SHA-256 `{obj['agent_sql_sha256']}`。",'- 原文引用核验：`records/042_checks/quote_checks.json`；盲标/解盲：`records/042_calibration_blind_sealed.json`、`records/042_calibration_comparison.json`。',f"- 未新开数据库/新查询/重跑。保守计已读重复核实查询为{obj['verification_query_count_including_read_duplicate']}条（Google Play封存件采用V1/V2两条，另已读相同SQL的V3计入预算）。" if oid.startswith('impl-009') else '- 未新开数据库/新查询/重跑。复用核实查询1条。','## 不确定或没查到的（含规则问题）',obj['rule_issue'] if not oid.startswith('impl-009') else '国家码映射可读作表示格式，也可读作生成键值的选择。盲标采用前者，解盲复核后采用后者：未证明lookup映射的语义等价，不满足只改呈现条件。正式口径保留Choice，供用户与Claude复核，不改手册。','## 建议的下一步','校准定稿保留；在同一会话继续39张正式表。阶段二保护封存件、解盲对比和本校准定稿，不重新盲标。']
 (A/f'042_{oid}.md').write_text('\n\n'.join(parts)+'\n')
print('calibration rendered:',len(work),'objects',sum(len(x['points']) for x in work),'points')
