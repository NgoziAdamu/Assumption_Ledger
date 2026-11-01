from pathlib import Path
import json,csv,hashlib,copy
R=Path('records');C=R/'040_checks';A=R/'040_annotations';A.mkdir(exist_ok=True)
def load(p):return json.loads(Path(p).read_text())
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
levels=['交付物里针对本处说明了','交付物里只有通用说明','过程中意识到了，交付物里没提','看到了相关信息，但没有意识到的迹象','没有迹象']
sealed=load(R/'040_calibration_blind_sealed.json');working=copy.deepcopy(sealed['objects']);old={d['task']+'_'+d['table']:d['main'] for d in load(R/'022_calibration_blind_decisions.json')['decisions']}
audit=[];quotes=[];objs=[];pts=[]
for o in working:
 oid=o['id'];task=oid[:8];table=oid[9:];pack=R/f'012_packages/012_{task}_{o["layer"]}_{table}.json';d=load(pack);con=d['contract_specification'];sql=d['agent_final_SQL'][0]
 assert sql['text'].strip()==Path(sql['path']).read_text().strip()
 assert all(b['original_text'] in Path(con['source_path']).read_text() for b in con['blocks'])
 o['contract_source']=con['source_path'];o['contract_sha256']=sha(con['source_path']);o['sql_source']=sql['path'];o['sql_sha256']=sha(sql['path']);o['old_label']=old[oid]
 o['verification_query_count_including_failures']=3 if task=='impl-005' else 2
 o['query_budget_note']='Google Ads复用014 V1及016 V1/V2共3条；Xero实际证据用017 V2，保守把已读V1失败也算入为2条。封存件verification_query_count记录成功采用数，原件不改。'
 o['contract_quotes']=[{'path':con['source_path'],'field':'text','quote':b['original_text']} for b in con['blocks']]
 objs.append({'benchmark':'DAComp','对象编号':oid,'层':o['layer'],'主要原因':o['main'],'并列项':'','是否只能组合修复':'否','把握':o['confidence'],'旧标签':old[oid],'022旧标签':old[oid]})
 body=[f'# 040 校准：{oid}','## 任务',f'按冻结v3.2第3～8节盲标；层：{o["layer"]}。本说明来自封存结果，没有用036改写结论。','## 结论',f'主要原因：**{o["main"]}**；把握{o["confidence"]}；共{len(o["points"])}点；不是只能组合修复。','## 详细发现','### 判断顺序与范围','先检查契约、交付SQL及单改结果，排除代码意图错误、raw版本差异及gold与契约不一致。未采用领域惯例补出未写明的规则。主因按L0含评测键全表行规模优先、格子规模次之；L1～L3仅辅助定位，不跨口径排序。']
 for p in o['points']:
  p['role']={'主要原因':'主要','参与因素':'参与'}[p['role']]
  base=p['baseline'][0];run=p['single_change'][0];p['reduction']=[base['row_scale']-run['row_scale'],base['cell_scale']-run['cell_scale']]
  evidence=list(p['quotes']);quotes += [{'object':oid,'point':p['name'],**q} for q in evidence]
  # 引用交付SQL中对应原表达式，作为机制依据；非注释不算披露。
  expressions={'campaign_id源列选择':'CAST(campaign_base_campaign AS VARCHAR(20)) campaign_id','spend两位小数':'CAST(cost_micros / 1000000.0 AS DECIMAL(15,2)) spend','conversions类型表示':'CAST(conversions AS DECIMAL(10,2)) conversions','conversions_value类型表示':'CAST(conversions_value AS DECIMAL(15,2)) conversions_value','account_code去重满足line_item_id唯一性':'QUALIFY row_number() OVER (PARTITION BY account_code ORDER BY account_id) = 1'}
  sq={'path':sql['path'],'field':'text','quote':expressions[p['name']]};assert sq['quote'] in Path(sq['path']).read_text();quotes.append({'object':oid,'point':p['name'],**sq})
  refs=[p['rerun_source'],*p.get('verification_sources',[]),'records/040_checks/disclosure_audit.json']
  pts.append({'benchmark':'DAComp','对象编号':oid,'错误点名称':p['name'],'角色':p['role'],'类别':p['category'],'是否说出（五档）':levels[p['disclosure']-1],'证据在场':p['evidence_present'],'曾经理解对过':p['previously_correct'],'系统提示是否适用':p['system_prompt'],'证据是复用还是新做':'复用014–022证据；040新核交付物/原始轨迹','证据来源':';'.join(refs),'022旧标签':old[oid]})
  audit.append({'对象编号':oid,'错误点名称':p['name'],'grade':p['disclosure'],'是否说出':levels[p['disclosure']-1],'reason':p['disclosure_reason'],'evidence':evidence,'delivery_source':'records/040_checks/delivery_sources.json','sql_path':sql['path'],'sql_comment_count':sum('--' in line or '/*' in line for line in sql['text'].splitlines()),'not_delivery':'交付SQL的普通表达式和中间脚本不算披露；第4档引句是看到了相关信息的证据。'})
  body += [f'### {p["name"]}',f'{p["role"]}；**{p["category"]}**；把握{p["confidence"]}。',p['reason'],f'是否说出：第{p["disclosure"]}档——{levels[p["disclosure"]-1]}。{p["disclosure_reason"]}',f'证据在场：{p["evidence_present"]}；曾经理解对过：{p["previously_correct"]}；系统提示是否适用：{p["system_prompt"]}。','| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |','|---|---:|---:|---:|---:|']
  for b,a in zip(p['baseline'],p['single_change']):body.append(f'| {b["level"]} | {b["row_scale"]} | {a["row_scale"]} | {b["cell_scale"]} | {a["cell_scale"]} |')
  body += ['',f'单改来源：`{p["rerun_source"]}` / `{p["rerun_label"]}`。L0减少{p["reduction"][0]}行、{p["reduction"][1]}格；不同单改收益不相加。']
  for q in evidence+[sq]:body += [f'原句：`{q["path"]}` / `{q["field"]}`'+(f' / event {q["event"]}' if 'event' in q else ''),'```text',q['quote'],'```']
  if p.get('verification_sources'):body += ['核实证据：'+ '；'.join('`'+x+'`' for x in p['verification_sources'])+'。']
 for q in o['contract_quotes']:quotes.append({'object':oid,'point':'契约依据',**q})
 body += ['### 契约依据',f'完整契约原文已在`{pack}`核对到`{con["source_path"]}`；SHA-256 `{o["contract_sha256"]}`。']
 if task=='impl-027':body += ['契约原句：`Unique identifier for the invoice line item; exactly one output row per value`。gold直接JOIN的多重性不符合这里的唯一粒度；移除去重用于定位差异，不表示agent应当复制gold的行数。']
 else:body += ['契约campaign_id只有VARCHAR(20)和not_null，没有源列映射；spend/conversions/conversions_value分别规定DECIMAL(15,2)、DECIMAL(10,2)、DECIMAL(15,2)。']
 body += ['## 证据来源',f'- 材料包：`{pack}`。',f'- 交付SQL：`{sql["path"]}`；SHA-256 `{o["sql_sha256"]}`。','- `records/040_calibration_blind_sealed.json`、`records/040_calibration_comparison.json`、`records/040_checks/quote_checks.json`。',f'- {o["query_budget_note"]}','- 本阶段没有新执行数据库查询或重跑；Google Ads复用022的agent留存raw，Xero复用CS gold上游；执行路径与clock_control见各重跑JSON。','## 不确定或没查到的（含规则问题）','- 未发现需要修改手册的规则问题；没有因为gold结果不同而补出唯一业务规则。','- 036只列Google Ads的campaign主因点，未列三项类型参与；本次保留独立单改减少格子的三项，校准一致率只按两个对应点计算。' if task=='impl-005' else '- 去重可能舍弃其他账户属性；交付报告已针对invoice enrichment说明。当前判错差异仅由209条重复行解释。','## 建议的下一步','保留该校准结果和封存hash，在同一会话继续38张正式表；不把本阶段2张校准误作40张完成。']
 (A/f'040_{oid}.md').write_text('\n\n'.join(body).replace('|\n\n|', '|\n|')+'\n')
for kind,rows in [('objects',objs),('points',pts)]:
 headers=next(csv.reader(open(R/f'039_{kind}.csv')));headers[-1]='022旧标签'
 with open(R/f'040_{kind}.csv','w',newline='') as f:
  w=csv.DictWriter(f,headers,lineterminator="\n");w.writeheader();w.writerows(rows)
save(C/'calibration_working.json',working);save(C/'disclosure_audit.json',audit);save(C/'quote_inventory.json',quotes)
save(C/'calibration_rows_before_phase2.json',{'objects':objs,'points':pts,'audit':audit,'csv_sha256':{k:sha(R/f'040_{k}.csv') for k in ['objects','points']}})
print('calibration objects',len(objs),'points',len(pts),'quotes',len(quotes))
