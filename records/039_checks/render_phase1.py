from pathlib import Path
import json,csv,hashlib,collections
R=Path('records');C=R/'039_checks';A=R/'039_annotations';A.mkdir(exist_ok=True)
def load(p):return json.loads(Path(p).read_text())
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
levels=['交付物里针对本处说明了','交付物里只有通用说明','过程中意识到了，交付物里没提','看到了相关信息，但没有意识到的迹象','没有迹象']
working=load(C/'calibration_working.json');old={x['题目']+'_'+x['表']:x['主要原因类别'] for x in csv.DictReader(open(R/'021_annotations/021_summary.csv'))};orows=[];prows=[];audit=[];quotes=[]
for o in working:
 orows.append({'benchmark':'DAComp','对象编号':o['id'],'层':o['layer'],'主要原因':o['main'],'并列项':'；'.join(p['name']+':'+p['category'] for p in o['points'] if p['role']=='并列'),'是否只能组合修复':'是' if o['combination_only'] else '否','把握':o['confidence'],'旧标签':old[o['id']],'021旧标签':old[o['id']]})
 text=[f"# {o['id']}（039，v3.2校准工作结果）",'', '## 任务', '', '先独立盲标封存，后与036对照；本文件为解盲后的工作结果，不能替代封存件计算一致率。', '', '## 结论', '', f"主要原因：**{o['main']}**；把握：{o['confidence']}。",f"021旧主要原因原样保留：`{old[o['id']]}`，不作为新类别依据。",'', '## 详细发现', '', '### 判定和规模口径', '', '按038做法，以L0整表行规模优先，行规模并列时比较格子数；评测键计入。单改须从同一基线独立进行，不能相加贡献。L1–L3仅作宽松诊断。', '', f"基线：`{json.dumps(o['baseline'],ensure_ascii=False)}`。", '',f"重跑来源：`{o['rerun_source']}`。原记录中clock_control、source、private_copy_tables和edits提供共同日期、CS/agent-raw来源与准确替换。",'']
 for p in o['points']:
  source=p.get('rerun_source',o['rerun_source'])
  prows.append({'benchmark':'DAComp','对象编号':o['id'],'错误点名称':p['name'],'角色':p['role'],'类别':p['category'],'是否说出（五档）':levels[p['disclosure']-1],'证据在场':p['evidence_present'],'曾经理解对过':p['understood_before'],'系统提示是否适用':'不适用','证据是复用还是新做':'复用重跑/核实；039新核原文'+('；解盲后补录' if p.get('added_after_unblinding') else ''),'证据来源':';'.join([source,o['package'],'records/039_checks/disclosure_audit.json',f'records/039_annotations/039_{o["id"]}.md']+o['verification_sources']),'021旧标签':old[o['id']]})
  dq=[q for q in p['quotes'] if q['kind']=='delivery'];pq=[q for q in p['quotes'] if q['kind']=='process'];ev=dq if p['disclosure']<=2 else pq
  audit.append({'对象编号':o['id'],'错误点名称':p['name'],'category':p['category'],'grade':p['disclosure'],'是否说出':levels[p['disclosure']-1],'evidence':ev,'reason':p['delivery_review'],'evidence_present':p['evidence_present'],'understood_before':p['understood_before'],'note':p['reason']})
  text += [f"### {p['name']}",'',f"角色：{p['role']}；类别：**{p['category']}**；把握：{p['confidence']}。",'',p['reason'],'',f"前提P/处理选择：{p.get('premise','不适用：其他类是契约与gold不一致，并非agent未确立的前提。')}",f"是否说出：第{p['disclosure']}档——{levels[p['disclosure']-1]}。{p['delivery_review']}",f"证据在场：{p['evidence_present']}；曾经理解对过：{p['understood_before']}；系统提示是否适用：不适用。",'', '| 口径 | 基线行 | 单改后行 | 基线格 | 单改后格 |','|---|---:|---:|---:|---:|']
  for level,v in p['scales'].items():
   b=o['baseline'][level];text.append(f"| {level} | {b['row_scale']} | {v['row_scale']} | {b['cell_scale']} | {v['cell_scale']} |")
  text += ['',f"单改：`{source}` / `{p['rerun']}`；减少量（L0行、格）：`{p['reduction']}`。",'']
  if p.get('verification'):text += [p['verification'],'']
  if p.get('marker'):text += [f"标记：{p['marker']}。",'']
  text += ['准确old/new：','', '```json',json.dumps(p['edits'],ensure_ascii=False,indent=2),'```','', '引句与用途（执行SQL只是定位代码；只有finish或交付SQL注释算披露）：','']
  for q in p['quotes']:
   quotes.append({'object':o['id'],'point':p['name'],**q});text += [f"- `{q['source']}` / `{q.get('event','SQL')}.{q['field']}` / {q['kind']}：",'','```text',q['quote'],'```','']
 text += ['## 证据来源','',f"- 契约/SQL材料包：`{o['package']}`。",f"- 原始契约：`{o['contract_source']}`。",f"- 交付SQL：`{o['agent_sql']}`。",f"- 原始交付报告及SQL注释清单：`records/039_checks/delivery_sources.json`。",f"- 核实查询复用（保守计入失败共{o['verification_query_count']}条，不超过5）：`{'`、`'.join(o['verification_sources'])}`。",'- 盲标封存、解盲差异：`records/039_calibration_blind_sealed.json`、`records/039_calibration_comparison.json`。','', '## 不确定或没查到的（含规则问题）','']+['- '+s for s in o['rules']]
 if o['id'].startswith('impl-030'):text += ['- 补充组合诊断为L0–L3全表0行/0格，见`records/039_checks/calibration_combo.json`。它不是单点排序证据，也不表示agent违反了类型契约。','- 曾经理解对过保留“是”，与036不同，依据已在account_source列明。盲标event34引句回查能匹配文本，但不属于本张invoice；工作结果已撤回其证明作用。']
 text += ['', '## 建议的下一步','', '由用户与Claude复核校准中的规则读法和轨迹证据差异；第二阶段继续同一会话的40张正式表，不重新盲标、不改封存件。','']
 (A/f'039_{o["id"]}.md').write_text('\n'.join(text))
for kind,rows in [('objects',orows),('points',prows)]:
 with open(R/f'038_{kind}.csv') as f:fields=next(csv.reader(f))
 fields[-1]='021旧标签'
 with open(R/f'039_{kind}.csv','w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(rows)
save(C/'disclosure_audit.json',audit);save(C/'quote_inventory.json',quotes);save(C/'calibration_working_rows_before_phase2.json',{'objects':orows,'points':prows,'audit':audit})
print('rendered',len(orows),len(prows),'quotes',len(quotes))
