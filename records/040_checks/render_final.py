from pathlib import Path
import json,csv,io,hashlib,collections
ROOT=Path.cwd();R=ROOT/'records';C=R/'040_checks';A=R/'040_annotations'
def load(p):return json.loads(Path(p).read_text())
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
levels=['交付物里针对本处说明了','交付物里只有通用说明','过程中意识到了，交付物里没提','看到了相关信息，但没有意识到的迹象','没有迹象'];working=load(C/'formal_working.json');objs=[];pts=[]
for o in working:
 oid=o['id'];pfile='records/040_checks/formal_working.json';ties='；'.join(x['name']+'（'+x['category']+'）' for x in o['ties'])
 objs.append({'benchmark':'DAComp','对象编号':oid,'层':o['layer'],'主要原因':o['main'],'并列项':ties,'是否只能组合修复':'否','把握':o['confidence'],'旧标签':o['old_label'],'022旧标签':o['old_label']})
 lines=[f'# 040 正式标注：{oid}','## 任务',f'按冻结v3.2第3～8节逐点重标；层：{o["layer"]}。022旧主要原因仅原样存档为 `{o["old_label"]}`，不作为新类别依据。','## 结论',f'主要原因：**{o["main"]}**；把握{o["confidence"]}；共{len(o["points"])}个点。不是只能组合修复。',('并列项：'+ties) if ties else '主因由独立单改的L0行规模减少量、再格子减少量决定。','## 详细发现','### 第3～7节判断顺序','本题013原始数据改动清单无条目，022三侧复用检查未发现依赖raw版本差异。CS层使用gold上游，staging使用agent留存raw。先排除代码意图未落实及gold/规格差异，再区分形式、占位替代、明确业务算法和未定选择；不借gold实现补契约，不添加拿不准的领域惯例。','各点的基线/单改均为整表含评测键口径；先行数、再格子数。L1～L3辅助定位，主因不跨口径比较。各单改减量不相加。角色“非原因”不计参与因素，具体说明见各点。']
 if o['index_022']==6:lines += ['完整 `data_contract.yaml` 已搜索：没有 `name: marketo__calendar_spine` 定义，只有下游引用；依赖配置也未给出该表定义。下游写“The upper bound of dates is defined only by the calendar spine; no additional end-date filter is applied.”，没有决定工具表终点。证据：`records/040_checks/calendar_contract_search.json`。']
 for p in o['points']:
  refs=list(dict.fromkeys([p['rerun_source'],o['package'],pfile,'records/040_checks/disclosure_audit.json']))
  pts.append({'benchmark':'DAComp','对象编号':oid,'错误点名称':p['name'],'角色':p['role'],'类别':p['category'],'是否说出（五档）':levels[p['disclosure']-1],'证据在场':p['evidence_present'],'曾经理解对过':p['previously_correct'],'系统提示是否适用':'不适用','证据是复用还是新做':('040新做单改；复用022材料；040新核原始轨迹' if p['new_evidence'] else '复用022单改/诊断；040新核契约/交付物/轨迹'),'证据来源':';'.join(refs),'022旧标签':o['old_label']})
  lines += [f'### {p["name"]}',f'{p["role"]}；**{p["category"]}**；把握{p["confidence"]}。',p['reason'],f'是否说出：第{p["disclosure"]}档——{levels[p["disclosure"]-1]}。{p["disclosure_reason"]}',f'证据在场：{p["evidence_present"]}。{p["presence_reason"]}',f'曾经理解对过：{p["previously_correct"]}。{p["previously_correct_reason"]}','系统提示是否适用：不适用。','| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |','|---|---:|---:|---:|---:|']
  for b,a in zip(p['baseline'],p['single_change']):lines.append(f'| {b["level"]} | {b["row_scale"]} | {a["row_scale"]} | {b["cell_scale"]} | {a["cell_scale"]} |')
  lines += ['',f'来源：`{p["rerun_source"]}` / `{p["rerun_label"]}`'+(f' / diagnostic index {p["diagnostic_index"]}' if p['diagnostic_index'] is not None else '')+f'。L0减少{p["reduction"][0]}行、{p["reduction"][1]}格。']
  if p.get('noncause_note'):lines.append('非原因说明：'+p['noncause_note'])
  for q in p['quotes']:
   lines += [f'原句：`{q["path"]}` / `{q["field"]}`'+(f' / event {q["event"]}' if 'event' in q else '')+f'（{q["kind"]}；普通SQL表达式不是披露）','```text',q['quote'],'```']
 if o['excluded_diagnostics']:
  lines += ['### 排除的旧候选/无差异诊断']
  for x in o['excluded_diagnostics']:lines.append(f'- `{x["label"]}`：{x["reason"]}')
 lines += ['## 证据来源',f'- 完整契约：`{o["contract_path"]}`；行段{o["contract_lines"]}；SHA-256 `{o["contract_sha256"]}`。',f'- 交付SQL：`{o["sql_source"]}`；SHA-256 `{o["sql_sha256"]}`。',f'- 原始完整提示：`{o["initial_prompt"]}`；材料包：`{o["package"]}`。',f'- 基线源：`{o["source"]}`；时钟控制：`{json.dumps(o["clock_control"],ensure_ascii=False)}`。','- `records/040_checks/process_review.json`、`formal_working.json`、`disclosure_audit.json`、`quote_checks.json`。',f'- 复用核实查询连失败共{o["verification_query_count"]}条，新核实0条，总数≤5；以下逐条列出，诊断/单改不计入：']
 for q in o['verification_queries']:lines.append(f'  - `{q["source"]}` / index {q["array_index"]}；{q["label"]}；失败={bool(q["error"])}。')
 lines += ['## 不确定或没查到的（含规则问题）']
 lines += ['- '+x for x in o['rule_questions']]
 if not o['rule_questions']:lines.append('无新增规则问题；按冻结v3.2执行。')
 if o['index_022']==8:lines.append('官方comparison_columns仅覆盖已列的14列及键；其他契约评分/风险列未进入本次比较。这里只对官方判错范围及已诊断点归因，不将未比较的契约缺口虚填成差异规模。')
 if o['index_022'] in [21,22,24]:lines.append('多个NULL投影共享生成器源名问题，但按列给单改。主键单改只减格也足以定主因；其余列被空主键过滤遮住。022整组恢复保留作定位，不替代独立点收益。')
 lines += ['## 建议的下一步','纳入任务040正式批次汇总；本任务不处理其他批次。规则边界或非原因标记可供用户与Claude复核，不修改手册。']
 (A/f'040_{oid}.md').write_text('\n\n'.join(lines).replace('|\n\n|','|\n|')+'\n')
# Preserve original phase-one bytes, append only new rows.
for kind,rows in [('objects',objs),('points',pts)]:
 path=R/f'040_{kind}.csv';prefix=(C/f'phase1_{kind}_prefix.csv').read_bytes();current=path.read_bytes();assert current.startswith(prefix)
 headers=next(csv.reader(io.StringIO(prefix.decode())));buf=io.StringIO(newline='');writer=csv.DictWriter(buf,fieldnames=headers,lineterminator='\n');writer.writerows(rows);tail=buf.getvalue().encode()
 if current==prefix:
  with path.open('ab') as f:f.write(tail)
 elif current!=prefix+tail:path.write_bytes(prefix+tail)
base=load(C/'calibration_rows_before_phase2.json')['audit'];formal=load(C/'formal_disclosure_audit.json')
for a in formal:a['是否说出']=levels[a['grade']-1]
save(C/'disclosure_audit.json',base+formal)
q=load(C/'quote_inventory.json')+load(C/'formal_quote_inventory.json');checks=[]
for x in q:
 v=Path(x['path']).read_text()
 if x['field']!='text':
  v=json.loads(v)
  if 'event' in x:assert v['id']==x['event']
  for k in x['field'].split('.'):v=v[k]
 checks.append({**x,'exact_match':x['quote'] in v,'source_sha256':hashlib.sha256(Path(x['path']).read_bytes()).hexdigest()})
assert all(x['exact_match'] for x in checks);save(C/'quote_checks.json',checks)
print('appended objects',len(objs),'points',len(pts),'quotes',len(checks),'total annotations',len(list(A.glob('*.md'))))
