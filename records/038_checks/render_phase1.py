"""输出038第一阶段交付；CSV只有两张已完成校准，不伪造43张正式结果。"""
from pathlib import Path
import json,csv
R=Path(__file__).resolve().parents[2]
def read(p):return json.loads((R/p).read_text())
def write(p,v):(R/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
working=read('records/038_checks/calibration_working.json');old={r['题目']+'_'+r['表']:r['主要原因类别'] for r in csv.DictReader((R/'records/020_annotations/020_summary.csv').open())};old36={r['对象编号']:r['旧标签'] for r in csv.DictReader((R/'records/036_objects.csv').open())}
objects=[];points=[];audit=[];quotes=[]
ann=R/'records/038_annotations';ann.mkdir(exist_ok=True)
for o in working:
 id=o['对象编号'];label=old[id];objects.append({'benchmark':'DAComp',**{k:o[k] for k in ['对象编号','层','主要原因','并列项','是否只能组合修复','把握']},'旧标签':old36[id],'020旧标签':label})
 lines=[f'# 038 校准：{id}','', '## 结论','',f"主要原因：**{o['主要原因']}**；并列类别：{o['并列项'] or '无'}；把握：{o['把握']}。这是解盲后的工作结果；盲标原件不变。",'', '两表校准已完成；43张正式表尚未标注。本文件不计入正式批次分布。','', '## 手册第3～7节判断与规模','',o['ranking_basis'],'', '先排除：未发现本表原始数据版本差异导致不可评估的证据；类别不从020旧标签映射。契约明确算法优先Intent，只有输出形式变化才考虑Form，原代码是否显露正确意图须单独核实。','', '| 实验 | L0 行/格 | L1 行/格 | L2 行/格 | L3 行/格 |','|---|---|---|---|---|', '| baseline | '+' | '.join(f"{l['row_scale']}/{l['cell_scale']}" for l in o['baseline'])+' |']
 for p in o['points']: lines.append('| '+p['run_label']+' | '+' | '.join(f"{l['row_scale']}/{l['cell_scale']}" for l in p['rerun'])+' |')
 lines+=['','重跑复用 `records/020_reruns_'+id+'.json`，完整SQL替换与逐列L0–L3结果保留于该文件；没有新执行SQL或打开数据库。Twilio重跑基线及单改均固定为2025-10-12，guide_event不依赖运行时钟。','', '## 逐点标注']
 sqlpath=o['delivery_review']['sql_path'];sql=(R/sqlpath).read_text()
 tokens={'latitude':'TRY_CAST(latitude AS DOUBLE) AS latitude','url':'END AS url','key':'AS guide_event_key','phone_user':'as user_phone_number_raw','phone_contact':'as contact_phone_number_raw'}
 for p in o['points']:
  src=['records/038_checks/calibration_working.json','records/038_calibration_comparison.json']+p['evidence']
  points.append({'benchmark':'DAComp','对象编号':id,**{k:p[k] for k in ['错误点名称','角色','类别','是否说出（五档）','证据在场','曾经理解对过','系统提示是否适用']},'证据是复用还是新做':'复用020查询/重跑；038新核原始契约/轨迹/交付物','证据来源':';'.join(src),'020旧标签':label})
  ev=[{'source':q['path'],'event':str(q['event'])+'.'+q['field'],'quote':q['quote']} for q in p['disclosure_evidence']]
  audit.append({'benchmark':'DAComp','对象编号':id,'错误点名称':p['错误点名称'],'grade':p['disclosure_grade'],'是否说出':p['是否说出（五档）'],'category':p['类别'],'blind_grade':p['blind_disclosure_grade'],'reason':p['disclosure_reason'],'evidence':ev})
  for kind,qs in [('是否说出',p['disclosure_evidence']),('证据在场',p['evidence_presence_quotes'])]:
   for q in qs:quotes.append({'object':id,'point':p['错误点名称'],'kind':kind,'source':q['path'],'event':str(q['event'])+'.'+q['field'],'quote':q['quote']})
  sl=next(s for s in sql.splitlines() if tokens[p['run_label']] in s);quotes.append({'object':id,'point':p['错误点名称'],'kind':'最终SQL','source':sqlpath,'event':None,'quote':sl})
  lines+=['',f"### {p['错误点名称']}",'',f"- 类别：{p['类别']}；角色：{p['角色']}；把握：{p['把握']}。",f"- 判据：{p['判据']}",f"- P：{p['P'] or '不适用（不是Data Misconception）'}",f"- 单改减少：{p['reduction'][0]}行／{p['reduction'][1]}格。",f"- 是否说出：第{p['disclosure_grade']}档，{p['是否说出（五档）']}；盲标第{p['blind_disclosure_grade']}档。{p['disclosure_reason']}",f"- 证据在场：{p['证据在场']}。{p['evidence_presence_explanation']}",f"- 曾经理解对过：{p['曾经理解对过']}；系统提示是否适用：不适用。",'- 最终SQL证据：`'+sqlpath+'`','', '```sql',sl,'```','', '披露/相关信息原句：']
  for q in p['disclosure_evidence']:lines+=['',f"`{q['path']}`，event {q['event']}.{q['field']}",'','> '+q['quote'].replace('\n','\n> ')]
  if p['evidence_presence_quotes']!=p['disclosure_evidence']:
   for q in p['evidence_presence_quotes']:lines+=['',f"证据在场原句：event {q['event']}.{q['field']}，`{q['path']}`",'', '> '+q['quote'].replace('\n','\n> ')]
  lines+=['','证据：'+'；'.join('`'+s+'`' for s in p['evidence'])+'。']
 lines+=['','## 交付物核查','',f"finish：event {o['delivery_review']['finish_event']}，`{o['delivery_review']['path']}` 的 `args.final_thought`。本表最终SQL没有注释。",'',o['delivery_review']['working_resolution'],'','## 规则问题','', 'guide_event各单改的整表行数都不下降，采用037的“行规模相同则按格子”读法，URL与key各减15000格并列，latitude减13655格为参与因素。解盲确认036相同；不改手册。' if id.startswith('impl-002') else '两列电话可分别单改，保留两点而不把整组修复冒充单点；contact减10行，user减9行。报告中的通用清理策略属于第2档，不证明已说明预修复选择。','','## 证据来源与限制','',f"020定稿旧主要原因原样为 `{label}`；只作追溯，不作v3.2判类依据。",'', '来源：`records/020_calibration_queries.json`、`records/020_reruns_'+id+'.json`、`records/013_packages/013_'+id[:8]+'_staging_'+id[9:]+'.md`；封存及解盲详情见038对应JSON。','', '已核实来自实际打开的契约/SQL/事件和复用查询记录；没有新查数据库，因此不声称重新验证了整个数据集。','']
 (ann/f'038_{id}.md').write_text('\n'.join(lines))
for kind,rows in [('objects',objects),('points',points)]:
 with (R/f'records/037_{kind}.csv').open() as f:fields=next(csv.reader(f))
 fields[-1]='020旧标签'
 with (R/f'records/038_{kind}.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(rows)
write('records/038_checks/disclosure_audit.json',audit);write('records/038_checks/quote_inventory.json',quotes)
write('records/038_checks/calibration_working_rows_before_phase2.json',{'objects':objects,'points':points,'audit':audit})
print('Rendered calibration objects=2 points=5; formal=0 (pending).')
