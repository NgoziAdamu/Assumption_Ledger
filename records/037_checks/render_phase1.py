"""037 第一阶段交付生成：CSV 当前仅校准2表，43正式表仍待完成。"""
from pathlib import Path
import json,csv,copy,hashlib
R=Path(__file__).resolve().parents[2]
def read(p):return json.loads((R/p).read_text())
def write(p,v): (R/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
blind=read('records/037_calibration_blind_sealed.json');comp=read('records/037_calibration_comparison.json')
comparisons={x['对象编号']:x for x in comp['comparisons']}
old={r['题目']+'_'+r['表']:r['主要原因类别'] for r in csv.DictReader((R/'records/019_annotations/019_summary.csv').open())}
objects=[];points=[];audit=[]
(R/'records/037_annotations').mkdir(exist_ok=True)
for o in copy.deepcopy(blind['objects']):
 id=o['对象编号'];decision=comparisons[id];post=decision['post_comparison'];o['主要原因']=post['main'];o['把握']=post['confidence']
 p=o['points'][0];p['类别']=post['main'];p['把握']=post['confidence'];p['disclosure_grade']=post['grade']
 if post['grade']==2:
  p['是否说出（五档）']='交付物里只有通用说明'
  ev=decision['036_disclosure_verbatim']['evidence'][0]
  path=o['delivery_review']['path'];e=json.loads((R/path).read_text());q=ev['quote'];assert q in e['args']['final_thought']
  p['disclosure_evidence']=[{'path':path,'event':41,'field':'args.final_thought','quote':q}]
 p['disclosure_reason']=post['reason']
 row={k:o.get(k,'') for k in ['对象编号','层','主要原因','并列项','是否只能组合修复','把握']}
 row.update({'benchmark':'DAComp','旧标签':old[id],'019旧标签':old[id]});objects.append(row)
 md=[f'# {id}（037 校准；解盲后工作结果）','',f'主要原因：**{o["主要原因"]}**；把握：{o["把握"]}。本表不属于43张正式批次。', '', '## 盲标与对比','',f'盲标原件：`records/037_calibration_blind_sealed.json`，SHA-256 `{comp["sealed_sha256_before_comparison"]}`。封存后不改。', '',f'盲标主因：{decision["blind_main"]}；主点第 {decision["blind_grade"]} 档。036：{decision["036_main"]}，第 {decision["036_grade"]} 档。','',post['reason'],'',f'019旧主要原因原样保留：`{old[id]}`；不以旧类别推导新类别。','', '## 逐点依据']
 for p in o['points']:
  row={'benchmark':'DAComp','对象编号':id,'错误点名称':p['错误点名称'],'角色':p['角色'],'类别':p['类别'],'是否说出（五档）':p['是否说出（五档）'],'证据在场':p['证据在场'],'曾经理解对过':p['曾经理解对过'],'系统提示是否适用':'不适用','证据是复用还是新做':'复用重跑/核实查询；037新核交付物/轨迹'+('；037新做只读呈现诊断' if p['类别']=='其他' else ''),'证据来源':';'.join(p['evidence']+['records/037_calibration_blind_sealed.json','records/037_calibration_comparison.json','records/037_checks/disclosure_audit.json']),'019旧标签':old[id]};points.append(row)
  ae={'benchmark':'DAComp','对象编号':id,'错误点名称':p['错误点名称'],'grade':p['disclosure_grade'],'是否说出':p['是否说出（五档）'],'019旧标签':old[id],'036类别':decision['036_main'] if p['角色']=='主要' else None,'037类别':p['类别'],'reason':p['disclosure_reason'],'evidence':[{'source':q['path'],'event':str(q['event'])+'.'+q['field'],'quote':q['quote']} for q in p['disclosure_evidence']],'final_answer_or_report_sha256':o['delivery_review']['final_report_sha256'],'final_answer':None,'校准状态':'解盲后工作结果；盲标见封存文件'};audit.append(ae)
  md += ['',f'### {p["错误点名称"]}','',f'- 类别：{p["类别"]}；角色：{p["角色"]}；把握：{p["把握"]}。',f'- SQL：`{o["delivery_review"]["sql_path"]}`，第 {p["SQL行"]} 行。',f'- 规模：{p["规模与角色"]}',f'- 是否说出：第 {p["disclosure_grade"]} 档（{p["是否说出（五档）"]}）。',f'- 证据在场：{p["证据在场"]}；曾经理解对过：{p["曾经理解对过"]}；系统提示：不适用。','',p['判据']]
  if p['类别']=='Intent Misreading':md += ['','解盲后分类说明：上述连接基数机制仍是事实，但主要分类按契约规定的 missing-day 计数定义归 Intent；原盲标 P 仅留在封存件，不作为最终 Data 条目。']
  if p['P'] and p['类别']=='Data Misconception':md += ['',f'P：{p["P"]}']
  md+=['','证据文件：']+['',*['- `'+x+'`' for x in p['evidence']]]
  md+=['','披露/相关信息原句：']
  for q in p['disclosure_evidence']:md += ['',f'`{q["path"]}`，event {q["event"]} / `{q["field"]}`：','', '> '+q['quote']]
  if p['证据在场']=='是':
   md+=['','证据在场：'+p['evidence_presence_explanation']]
   for q in p['evidence_presence_quotes']:md+=['',f'event {q["event"]} / `{q["field"]}`：','', '> '+q['quote']]
  md+=['',p['disclosure_reason']]
 md+=['','## 交付物核对','',f'最终报告取 finish event {o["delivery_review"]["finish_event"]} 的 `args.final_thought`。本表最终 SQL 无注释，临时脚本不作交付物；扫描相关其他交付 SQL 注释未发现本处说明。','', '## 不确定与规则问题','',decision['rule_question'],'',decision['point_coverage_difference'],'','Asana 的历史留存与单改重跑允许并列排序不同；不可把195行的留存基线与187行的重跑基线混算。校准表的最终类别与披露如经解盲修订，不能计入盲标一致率。','']
 (R/f'records/037_annotations/037_{id}.md').write_text('\n'.join(md))
for filename,rows,ref in [('objects',objects,'objects'),('points',points,'points')]:
 with (R/f'records/036_{ref}.csv').open() as f:fields=next(csv.reader(f))
 assert fields[-1]=='相对034';fields[-1]='019旧标签'
 with (R/f'records/037_{filename}.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fields,lineterminator="\n");w.writeheader();w.writerows(rows)
write('records/037_checks/disclosure_audit.json',audit)
print('rendered 2 calibration objects, 3 points; formal 43 pending')
