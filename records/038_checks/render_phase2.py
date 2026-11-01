"""Render explicit reviewed rules, append formal rows after preserved calibration rows."""
from pathlib import Path
import csv,json,re,hashlib
from formal_rules import RULES
R=Path(__file__).resolve().parents[2];D=R/'records/038_checks'
C=json.loads((D/'evidence_catalog.json').read_text());CAL=json.loads((D/'calibration_working_rows_before_phase2.json').read_text());DEL=json.loads((D/'delivery_sources.json').read_text())
G={1:'交付物里针对本处说明了',2:'交付物里只有通用说明',3:'过程中意识到了，交付物里没提',4:'看到了相关信息，但没有意识到的迹象',5:'没有迹象'}
objs=CAL['objects'].copy();pts=CAL['points'].copy();aud=CAL['audit'].copy();dec=[];quotes=[]
def ev(source,field,quote,event=None):
 z=dict(source=source,field=field,quote=quote,event=event or field);quotes.append(z);return z
final=DEL['impl-006']['finish'][0]
null_quote='对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。'
parse_quote='脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。'
named_quote='当前实现以结构化 NULL/直接字段投影保障执行，并非完整的客户旅程、地理分析、时间序列、预测及执行仪表板业务逻辑。'
country_quote='`int_ad_reporting__country_mapping` 由于契约没有给出完整静态列举值，目前为单行静态占位映射，不能代表全量国家覆盖。'
group_quote='Apple 订阅 summary/event 字段有若干原始字段与 staging 字段语义不完全一致，使用可用列映射且转换兼容字段类型。若这类字段用于正式订阅财务决策，应以源端字段定义进一步确认。'
mapnamed={2:'int_ad_reporting__country_mapping',3:'客户旅程',4:'地理分析',7:'时间序列',9:'执行仪表板',12:'预测'}
for i,o in enumerate(C):
 id=o['object'];oldpath=f'records/020_reruns_{id}.json';base=json.loads((R/oldpath).read_text());sql=(R/o['agent_sql']).read_text();pack=(R/o['package']).read_text();contract=pack.split('```yaml\n',1)[1].split('```',1)[0];lines=contract.splitlines()
 od=dict(object=id,index=i,layer=o['layer'],old_main=o['020_final_old_main'],contract_source=o['contract_source'],contract_lines=o['contract_lines'],agent_sql=o['agent_sql'],source=base['source'],clock_control=base.get('clock_control'),points=[],comparison_columns=base['basis']['comparison_columns'],excluded_sql_columns_note='未纳入官方比较的列不据此制造判错原因；marts country的mart_created_at、Google account/ad_group的spend等不评分。')
 for spec0 in RULES[i]:
  s=spec0.copy();label=s['label'];actual=label.replace('campaign_id_mapping_restore','campaign_id_restore_overwritten_mapping').replace('spend_mapping_restore','spend_restore_overwritten_mapping')
  path=oldpath if s['source']=='old' else (f'records/020_resume_reruns_{id}.json' if s['source']=='resume' else f'records/038_checks/rerun_{id}.json')
  data=json.loads((R/path).read_text());run=next(x for x in data['runs'] if x['label']==actual);br=next(x for x in data['runs'] if x['label']=='baseline')
  s.update(name=s.get('name',label),reference=path+'#'+actual,experiment_label=actual,confidence=s.get('confidence','高'),evidence_presence='是' if s['base_category'] in ['Intent Misreading','Data Misconception'] else '不适用',understood_before='否' if s['base_category'] in ['Intent Misreading','Data Misconception'] else '不适用')
  s['category']={'Unstated Choice':'已说出的选择','Quiet Downgrade':'已说出的降级'}.get(s['base_category'],s['base_category']) if s['grade']==1 else s['base_category']
  s['scales']=[dict(level=a['level'],baseline_rows=a['row_scale'],baseline_cells=a['cell_scale'],after_rows=b['row_scale'],after_cells=b['cell_scale'],delta_rows=a['row_scale']-b['row_scale'],delta_cells=a['cell_scale']-b['cell_scale']) for a,b in zip(br['comparison']['levels'],run['comparison']['levels'])]
  # Exact contract column block when available, otherwise the model business logic.
  col=re.sub(r'_invalid_policy$','',label)
  col={'conversions_decimal':'conversions','invalid_id_contract_delete':'ad_group_id','spend_masked_diagnostic':'spend','campaign_id_mapping_restore':'campaign_id','spend_mapping_restore':'spend','app_installs_candidate':'app_installs','google_roas_rounding':'return_on_ad_spend','ctr_platform_fallthrough':'ctr_performance_tier','gold_roi_labels_diagnostic':'roi_expectation','clv_presentation':'global_avg_clv','valid_rate_formula_choice':'conversion_rate','invalid_rate_policy_diagnostic':'conversion_rate','gold_rating_policy_diagnostic':'average_rating'}.get(col,col)
  m=re.search(r'''(?m)^\s+- name: ["']?'''+re.escape(col)+r'[\"\']?\s*\n',contract)
  if m:
   tail=contract[m.start():];n=re.search(r'\n\s+- name: ',tail[len(m.group()):]); cq=tail[:len(m.group())+n.start() if n else len(tail)].strip()
  else:cq=next((l.strip() for l in lines if 'business_logic:' in l),lines[0].strip())
  if i==8 or label=='placeholder_filter':cq=next(l.strip() for l in lines if 'business_logic:' in l)
  s['contract_evidence']=ev(o['event_path'],'args.content',cq,'1.args.content')
  # Exact original SQL snippet; rerun clock-normalized timestamps may differ.
  edits=run.get('edits',[]);sq='\n'.join(e['old'] for e in edits if e['old'] in sql)
  if not sq:
   sq=next((l for l in sql.splitlines() if col.lower() in l.lower() and len(col)>2),sql.splitlines()[0])
  # Non-contiguous edits are individual evidence entries, never a fabricated quote.
  sqlquotes=[ev(o['agent_sql'],'text',e['old'],'delivered SQL') for e in edits if e['old'] in sql]
  if not sqlquotes:sqlquotes=[ev(o['agent_sql'],'text',sq,'delivered SQL')]
  s['sql_evidence']=sqlquotes
  grade=s['grade'];named=None
  if grade==1:
   q=country_quote if i==2 else named_quote;named=mapnamed[i];de=ev(final['path'],'args.final_thought',q,'97.args.final_thought');why=f'finish 97以“{named}”点名本表并说明占位/未实现；按037表级粒度仅用于本表的该类缺口。'
  elif grade==2:
   q=parse_quote if ('TRY_CAST' in s['reason'] or '文本' in s['reason']) else null_quote
   de=ev(final['path'],'args.final_thought',q,'97.args.final_thought');why='交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。'
  elif grade==3:
   attempt=DEL['impl-007']['failed_report_attempts'][0];de=ev(attempt['path'],'args.command',group_quote,'65.args.command');why='同组意识：明确说订阅summary/event语义不一致且需进一步确认。event65写result.md失败，不是交付物，只有第3档。'
  else:
   de=s['contract_evidence'];why='完整契约在初始event1可见；交付物无本处说明。未发现比较备选或点出本处冲突/疑问的迹象；仅写所选做法不算第3档。'
  s['disclosure']=dict(grade=grade,text=G[grade],reason=why,named_table=named,evidence=[de])
  if s['base_category']=='代码写错':
   ep=str(Path(C[0]['event_path']).with_name('19.json'));cmd=json.loads((R/ep).read_text())['args']['command'];key='campaign_id' if 'campaign_id' in label else 'spend';ss=[]
   for line in cmd.splitlines():
    if "'"+key+"':" in line:ss.append(ev(ep,'args.command',line,'19.args.command'))
   assert len(ss)>=2,(label,ss);s['code_intent_evidence']=ss
  if i in [0,3,4,5,6,7,9,12]:
   ep=str(Path(C[0]['event_path']).with_name('27.json'));q="sql='SELECT\\n'+',\\n'.join(fields)+f'\\nFROM {src[0]}'";s['fallback_evidence']=ev(ep,'args.command',q,'27.args.command')
  od['points'].append(s)
 # Rank independently relative to each intervention's own baseline.
 if len(od['points'])==1 and od['points'][0].get('diagnostic'):
  winners=od['points'];od['ranking_note']='同类候选/共享前提无法逐项排序，按手册第7节以中把握记该类。整段替换或多位置诊断的差异仅定位，不声称为单点修复贡献。'
 else:
  key=lambda p:(p['scales'][0]['delta_rows'],p['scales'][0]['delta_cells'])
  best=max(map(key,od['points']));assert best>(0,0),id;winners=[p for p in od['points'] if key(p)==best];od['ranking_note']='按L0减少行优先、格次之；各次干预仅与其自身固定时间/同口径基线比。L1–L3保留，不能相加独立贡献。'
 for p in od['points']:
  z=p['scales'][0];p['role']=('并列' if len(winners)>1 else '主要') if p in winners else ('参与' if (z['delta_rows'],z['delta_cells'])>(0,0) else '非原因')
  if p['role']=='非原因':p['noncause_note']='存在未确立的前提，但不是判错原因；本处单改没有正向减少规模（负值亦不算参与）。'
 cats=sorted(set(p['category'] for p in winners));main=cats[0] if len(cats)==1 else '多因并列';confidence='中' if any(p['confidence']=='中' for p in winners) else '高'
 if len(od['points'])==1 and od['points'][0].get('diagnostic'):confidence='中'
 od.update(main=main,tied_categories=cats if len(cats)>1 else [],confidence=confidence)
 objs.append(dict(benchmark='DAComp',对象编号=id,层=o['layer'],主要原因=main,并列项='；'.join(cats) if len(cats)>1 else '',是否只能组合修复='否',把握=confidence,旧标签=o['020_final_old_main'],**{'020旧标签':o['020_final_old_main']}))
 for p in od['points']:
  pts.append(dict(benchmark='DAComp',对象编号=id,错误点名称=p['name'],角色=p['role'],类别=p['category'],**{'是否说出（五档）':G[p['grade']]},证据在场=p['evidence_presence'],曾经理解对过=p['understood_before'],系统提示是否适用='不适用',证据是复用还是新做=('038新单点重跑/诊断；' if p['source']=='new' else '复用020重跑/查询；')+'038新核原契约/SQL/轨迹',证据来源=p['reference']+';records/038_checks/formal_decisions.json#'+id+';'+o['package'],**{'020旧标签':o['020_final_old_main']}))
  aud.append(dict(benchmark='DAComp',对象编号=id,错误点名称=p['name'],grade=p['grade'],是否说出=G[p['grade']],category=p['category'],reason=p['disclosure']['reason'],named_table=p['disclosure']['named_table'],evidence=p['disclosure']['evidence']))
 dec.append(od)
 # One independent, reviewable document per object.
 md=[f'# {id}（038 正式表）',f'主要原因：**{main}**；把握：{confidence}。020定稿旧主要原因：`{o["020_final_old_main"]}`，仅原样保留。','## 范围与材料',f'- 层：{o["layer"]}。范围清单：`records/038_scope.json`。',f'- 原契约：`{o["contract_source"]}`，{o["contract_lines"]}行；初始event1完整在场，未截断。',f'- 交付SQL：`{o["agent_sql"]}`。',f'- 对比执行输入：`{base["source"]}`；staging使用agent留存raw，其余层沿用020标准上游的逐表评测口径，不把上游错误传播计入本表。', '- impl-006：finish97/result.md及SQL注释为交付物。impl-007：无finish/result.md，65/67草稿失败且SQL无注释，不能第1/2档。',f'- 保护与原始数据：`records/038_checks/input_hashes_before.json`；013_raw_differences无006/007改动条目。', '## 逐点标注']
 for p in od['points']:
  md += [f'### {p["name"]}',f'- 类别：{p["category"]}；角色：{p["role"]}；把握：{p["confidence"]}。',f'- 是否说出：第{p["grade"]}档（{G[p["grade"]]}）。',f'- 证据在场：{p["evidence_presence"]}；曾经理解对过：{p["understood_before"]}；系统提示：不适用。',p['reason'], '判定顺序：'+({'代码写错':'第3节第1步由正确映射被覆盖的代码证据排除前提类。','其他':'第3节第1步及第6节；以契约/呈现条件定位差异。','Quiet Downgrade':'第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。','Unstated Choice':'第3步仍有合理读法；第4步材料不能唯一决定，不能以gold选择代替证据。','Intent Misreading':'不是仅呈现差异；契约明确规定算法/清理，依第5节归Intent而不是Data。'}[p['base_category']]),p.get('noncause_note','')]
  for label0,evid in [('契约/证据在场原句',[p['contract_evidence']]),('交付SQL原处',p['sql_evidence']),('披露/相关信息原句',p['disclosure']['evidence']),('代码正确意图证据',p.get('code_intent_evidence',[])),('fallback生成证据',[p['fallback_evidence']] if 'fallback_evidence' in p else [])]:
   for e in evid:md += [f'{label0}：`{e["source"]}`，`{e["event"]}`：','> '+e['quote'].replace('\n','\n> ')]
  md += [p['disclosure']['reason'],f'重跑/诊断：`{p["reference"]}`。'+('仅为整体/共享前提诊断，不据此宣称单点贡献。' if p.get('diagnostic') else '指定点干预，其余不动；呈现诊断仅改变该输出列比较条件。'),'| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |','|---|---:|---:|---:|']
  for z in p['scales']:md.append(f'| {z["level"]} | {z["baseline_rows"]}/{z["baseline_cells"]} | {z["after_rows"]}/{z["after_cells"]} | {z["delta_rows"]}/{z["delta_cells"]} |')
 md+=['## 规模、覆盖和不确定',od['ranking_note'],'各点非原因不自动删除。未评分列不参与主因排序。完整SQL差分、L0–L3与同口径基线保留在所引JSON。', '复用核实查询（包含失败查询，合计预算不超过5）：']
 for q in o['reused_verification_queries_including_failed']:md.append(f'- `{q["source"]}[{q["json_index"]}]`：`{q["sql"]}`。')
 nv=json.loads((D/'new_verification.json').read_text());extra=[x for x in nv if x['object']==id]
 for x in extra:md.append(f'- 新核实 `records/038_checks/new_verification.json`：`{x["sql"]}`；结果 `{x["result"]}`。累计{x["total_count"]}/5。')
 if i in [23,24,26,29,30,31]:md+=['规则问题：Boolean文本/脏文本补0与Data边界见完整038报告。当前Choice不否认存在大量NULL；缺的是证明这些值可唯一恢复为某个数值的证据，不用gold反证。']
 if i in [0,2,3,4,5,6,7,9,12,32]:md+=['规则问题：采用手册第7节同类候选无法逐项排序的口径，合并记录共享缺口组；整段诊断不是每个字段的单改，不声称独立字段贡献已知。']
 md=['\n'.join(line.rstrip() for line in x.split('\n')) for x in md]
 (R/f'records/038_annotations/038_{id}.md').write_text(re.sub(r'\|\n\n(?=\|)', '|\n', '\n\n'.join(x for x in md if x))+'\n')
for kind,rows in [('objects',objs),('points',pts)]:
 path=R/f'records/038_{kind}.csv';headers=next(csv.reader(path.open()))
 with path.open('w',newline='') as f:w=csv.DictWriter(f,headers,lineterminator="\n");w.writeheader();w.writerows(rows)
for path,data in [('formal_decisions.json',dec),('formal_quote_inventory.json',quotes),('disclosure_audit.json',aud)]:
 (D/path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(objects=len(objs),points=len(pts),formal_points=len(pts)-5,quotes=len(quotes)),ensure_ascii=False))
