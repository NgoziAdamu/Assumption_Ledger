"""Render reviewed 019 evidence, causal scales and frozen calibration into delivery artifacts."""
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo
import csv,json,hashlib
ROOT=Path(__file__).resolve().parents[1];REC=ROOT/'records';OUT=REC/'019_annotations';OUT.mkdir(exist_ok=True)
inv=json.loads((REC/'019_package_inventory.json').read_text());plans=json.loads((REC/'019_patch_plan.json').read_text());unc={x['table']:x for x in json.loads((REC/'019_uncertainty.json').read_text())};queries=json.loads((REC/'019_queries.json').read_text());stoch={x['table']:x for x in json.loads((REC/'019_stochastic_diagnostics.json').read_text())};sealed=json.loads((REC/'019_calibration_blind_sealed.json').read_text());blind={x['table']:x for x in sealed['annotations']};previous=list(csv.DictReader((REC/'018_annotations/018_summary.csv').open()));fields=[x for x in previous[0] if x!='与上一版相比是否变化及原因'];results=[];decisions=[]
rules={
'lever__candidate_experience_insights':'gold 将同一 journey 派生的四个非唯一键子结果再次连接，产生 n^5 重数；契约声明每 opportunity 一行，且未规定最终四次连接。两种读法：按 SQL 缺少连接判 C/U，或按契约粒度与 gold 重数不一致判 O。本次选 O；乘数试验是复现评测条件的诊断，不是推荐实现。其他 C/I/D 差异仍按单修量记录。',
'customer360__customer':'两种读法：契约“combine by customer360_id”直接要求自连接（C），或 agent 内联 sample metrics 依赖 dimensions 唯一性（U）。本次选 U：P 可写为 dimensions 每 customer_id 唯一，agent 可见数据反例78组；同键结合单修后 L0 完全一致。契约的一行粒度不能抹去现有上游重复证据。',
'int_customer360__customer_lifecycle_metrics':'手册明确固定时间，但未规定随机模拟量的共同控制。保留官方判错，以固定 setseed 的私有执行减小试验噪声；gold 原 seed 未知。共同将契约允许随机的输出替换为0，仅作 O 诊断，不能当作普通代码修复或 U 第4条件。',
'customer360__customer_activity_metrics':'random() 派生的三列同样采用共同屏蔽诊断；不修改官方评分。主因比较使用完整列数，随机差异作为评测条件因素。',
'google_ads__customer_acquisition_analysis':'契约的“lower CAC ranked higher / higher ratio ranked higher”可解释成较大的 percentile 或较前的排序名次；未给 ORDER BY 表达式。本次按 A 处理，不用 gold 排序替契约补定义。sophistication/segment/recommendation 也没有完整斜率和阈值表。',
'int_google_ads__account_performance_metrics':'CS gold 上游额外包含 cost_per_conversion，agent 留存同名上游没有此列。SELECT * 与重算列重名后遮蔽，本次选 O（换成契约/agent 上游列集合即可消除主差异），不把 agent 当时不可见的 gold 扩展列当作 U 的数据反例。',
'customer360__phone':'契约明确相同 phone 的 extension 并列次序未规定；只改变排序不能保证复现 gold。O 依据去除 index 后两侧 EXCEPT ALL 为0，而非任一碰巧匹配的重跑。',
'customer360__status':'当前私有 baseline 可能偶然 L0 一致；保留 013 的官方待标注状态。无序 STRING_AGG 的顺序诊断仍基于内容多重集，不能用一次重跑通过改写原始判错。',
'customer360__updates':'两列无序 STRING_AGG 属同一顺序条件；诊断逐列排序后整表多重集相同，不要求单次执行复现 gold 的偶然顺序。',
'lever__candidate_quality_insights':'契约规定消息的含义但没给完整英文常量。四个文本选择单修的行/格改善并列，类别均为 A，按 v2 第5节直接记 A。',
'stg_customer360__state_territory_codes':'契约没有整行 DISTINCT 要求。两种读法：把 gold 去重作为隐含粒度要求，或认为重复保留策略未定。本次选 A，不自行补 unique 规则。',
'stg_google_ads__account_history':'契约只有 TIMESTAMP 类型及 updated_at <= CURRENT_TIMESTAMP，没有指定 TRY_CAST 或 STRPTIME，也未规定格式解析失败处理。日期值可读不等于契约规定了解析器；本次按解析策略未定记 A，不能将 gold 的 TRY_CAST 写法冒充契约字面要求。',
'stg_google_ads__ad_history':'时间文本解析策略未规定；agent 修复可读的时区文本，gold TRY_CAST 后因 NULL 删除。按 A 记录，不声称 agent 日期值错误。',
'stg_google_ads__campaign_history':'时间文本解析策略未规定，gold TRY_CAST 产生 NULL 并过滤，而 agent STRPTIME 成功。按 A 记录；未把没有写在契约中的 parser 补成 C。',
'int_customer360__risk_assessment':'probability 的 .30 与 0.30 数值相同，但契约显式要求 DECIMAL(3,2)，agent 字面量推断 DECIMAL(2,2)，L0 表示不同；按 C。其他风险分类只给优先级、未完整给阈值，按 A。两种概率修法同源，不重复计为参与因素。',
}
for t,b in blind.items():rules[t]=b['rule_issue']
for t in ['int_lever__posting_analytics','int_lever__posting_performance','lever__departmental_hiring_trends','lever__hiring_manager_scorecard','int_pendo__conversion_funnel_analysis','int_pendo__data_quality_checks','int_pendo__product_health_metrics','pendo__customer_lifecycle_insights','pendo__executive_dashboard_metrics']:
 rules[t]='错误点粒度存在两种读法：每个占位输出列分别算一处，或将同一遗漏聚合/规则模块视为一个降级错误点。本次以模块为错误点，列出全部可见占位及残余列统计，以局部恢复模块内表达式/来源证明贡献；没有用整份 gold SQL 替换来宣称因果成立。未逐一补齐全部占位列，不能据局部修法宣称已覆盖模块内所有修复。若后续决定按列拆分，需重新比较这些因素的贡献排序。'

for r in inv:
 t=r['table'];d=json.loads((ROOT/r['full_json']).read_text());runpath=REC/('019_reruns_'+r['task']+'_'+t+'.json');runs=json.loads(runpath.read_text());base=runs['runs'][0]['comparison'];b0=base['levels'][0];ps={p['label']:p for p in plans.get(t,[])};trials=[]
 for trial in runs['runs'][1:]:
  if trial.get('error'):raise RuntimeError((t,trial['label'],trial['error']))
  p=ps.get(trial['label']);
  if not p:continue
  c=trial['comparison']['levels'][0];trials.append(dict(label=trial['label'],category=p['category'],reason=p['reason'],row_reduction=b0['row_scale']-c['row_scale'],cell_reduction=b0['cell_scale']-c['cell_scale'],comparison=trial['comparison'],kind='单处 SQL 改动'))
 if t in stoch:
  a=stoch[t]['baseline']['levels'][0];c=stoch[t]['comparison']['levels'][0];trials.append(dict(label='stochastic_evaluation',category='O',reason='契约允许每次变化的模拟量；共同屏蔽随机输出的诊断。',row_reduction=a['row_scale']-c['row_scale'],cell_reduction=a['cell_scale']-c['cell_scale'],comparison=stoch[t]['comparison'],kind='评测条件诊断，非代码修复'))
 # Alternative repairs of one cause must not be counted as distinct causes.
 if any(x['label']=='probability_type' for x in trials):trials=[x for x in trials if x['label']!='intervention_success_probability']
 effective=[x for x in trials if (x['row_reduction'],x['cell_reduction'])>(0,0)]
 if r['purpose']=='校准':
  main=blind[t]['category'];selected=[];factors=[];reason=blind[t]['reason'];confidence=blind[t]['confidence'];flags='；'.join(blind[t]['flags'])
 else:
  if t in ['customer360__status','customer360__updates','customer360__phone','salesforce__account_daily_history','salesforce__contact_daily_history','int_lever__posting_applications']:
   main='O';selected=[x for x in effective if x['category']=='O'];factors=[];reason='契约允许的并列选择或聚合顺序不同；诊断确认其余内容/候选最大时间记录一致。'
  else:
   assert effective,(t,'没有可支持的贡献试验');best=max((x['row_reduction'],x['cell_reduction']) for x in effective);selected=[x for x in effective if (x['row_reduction'],x['cell_reduction'])==best];cats=set(x['category'] for x in selected);main=next(iter(cats)) if len(cats)==1 else '多因并列';factors=[x for x in effective if x not in selected];reason='；'.join(dict.fromkeys(x['reason'] for x in selected))
  confidence='中' if main in ['A','U','多因并列'] or t in rules else '高';flags=''
  if main=='D' and (r['task']=='impl-002' or t in ['int_lever__posting_analytics','int_lever__posting_performance','lever__departmental_hiring_trends','lever__hiring_manager_scorecard']):flags='已披露'
  if main=='U' and t=='customer360__customer':flags='证据曾出现但被忽略'
 qs=[q for q in queries if q['table']==t];verify=[q for q in qs if q['kind']=='核实'];uq=unc[t];level=uq['level'];factorstr='；'.join(x['label']+'='+x['category'] for x in factors) or '无经单修/诊断证实的额外因素'
 if r['purpose']=='校准':
  qcal=[q for q in json.loads((REC/'019_calibration_queries.json').read_text()) if q['task']==int(r['task'][-3:])];verify=[q for q in qcal if q['kind']=='核实'];qs=qcal
  good=runs['runs'][1]['comparison']['levels'][0];usatisfied='是' if main=='U' and (good['row_scale']<=b0['row_scale']/2 or runs['runs'][1]['comparison']['first_match'] in ['L0','L1','L2']) else '不适用'
 else:usatisfied='是' if main=='U' and any(x['comparison']['first_match'] in ['L0','L1','L2'] or x['row_reduction']>=b0['row_scale']/2 for x in selected) else '不适用'
 assert main!='U' or usatisfied=='是',t
 scale='；'.join(x['label']+':'+str(b0['cell_scale'])+'→'+str(x['comparison']['levels'][0]['cell_scale']) for x in trials)
 if r['purpose']=='校准':scale='；'.join(x['label']+':'+str(b0['cell_scale'])+'→'+str(x['comparison']['levels'][0]['cell_scale']) for x in runs['runs'][1:])
 row=dict(zip(fields,['']*len(fields)));row.update({'题目':r['task'],'表':t,'一句话描述':('【校准】' if r['purpose']=='校准' else '')+reason,'主要原因类别':main,'参与因素':factorstr,'标记':flags,'把握':confidence,'核实查询条数':str(len(verify)),'核实代价档':'一条查询' if len(verify)==1 else '多条查询' if verify else '需要查业务说明','重跑是否满足 U 的第 4 个条件':usatisfied,'格子数口径规模变化':scale,'与 014 相比是否变化':'不适用：019独立标注','agent 是否意识到或提到了与本表差异相关的不确定性':f'{level}；event {uq["event_id"]}；'+uq['quote'],'并列项类别':'；'.join(x['label']+'='+x['category'] for x in selected) if len(selected)>1 else '不适用','不确定性四档':('；'.join(x['label']+'='+level for x in selected) if main=='多因并列' else level)})
 results.append(row);decisions.append(dict(task=r['task'],table=t,layer=r['layer'],purpose=r['purpose'],category=main,confidence=confidence,selected=[{k:v for k,v in x.items() if k!='comparison'} for x in selected],factors=[{k:v for k,v in x.items() if k!='comparison'} for x in factors],uncertainty=level,verification_queries=len(verify)))
 lines=[f'# {r["task"]} / {t}'+('（校准，盲标封存）' if r['purpose']=='校准' else ''),'','## 结论','',f'主要原因：**{main}**；把握：{confidence}；标记：{flags or "无"}。', '',reason,'',f'参与因素：{factorstr}。','',f'不确定性四档：**{level}**。','', '## 差异与依据','',f'精简材料包：`{r["path"]}`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。',f'历史选定结果 agent/gold 行数：{d["differences"]["prediction_rows"]}/{d["differences"]["gold_rows"]}。本次固定控制下 baseline 行/格规模：{b0["row_scale"]}/{b0["cell_scale"]}。',f'契约：`{d["contract_specification"]["source_path"]}`；原文行段 '+', '.join(str(x['start_line'])+'–'+str(x['end_line']) for x in d['contract_specification']['blocks'])+'。']
 for label,key in [('agent SQL','agent_final_SQL'),('gold SQL（仅定位）','gold_SQL_仅供定位差异')]:
  for v in d[key]:lines.append(f'{label}：`{v["path"]}`，L1–{v["end_line"]}；SHA-256 `{v["sha256"]}`。')
 for item in trials:
  pp=ps.get(item['label'])
  if pp:
   for oldsql,newsql in pp['edits']:
    original=d['agent_final_SQL'][0]['text'];off=original.index(oldsql);line=original.count('\n',0,off)+1
    lines+=['',f"{item['label']}：agent SQL L{line}，替换原片段如下。",'```sql',oldsql,'```','替换为：','```sql',newsql,'```']
 if r['purpose']=='校准':
  for trial in runs['runs'][1:]:
   for edit in trial['edits']:
    original=d['agent_final_SQL'][0]['text'];line=original.count('\n',0,original.index(edit['old']))+1
    lines+=['',f"{trial['label']}：agent SQL L{line}，盲标单处改动。",'```sql',edit['old'],'```','替换为：','```sql',edit['new'],'```']
 lines+=['','每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。','',f'`{runpath.relative_to(ROOT)}`；修改理由与类别：`records/019_patch_plan.json`。','', '## 查询和重跑','',f'核实查询 {len(verify)} 条（上限5）；代价档：{row["核实代价档"]}。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。']
 if main=='多因并列':lines+=['','并列项不确定性：'+'；'.join(x['label']+'='+level+'（event '+str(uq['event_id'])+'，同一下节可见证据）' for x in selected)+'。']
 for q in qs:lines+=['',q['kind']+'：','```sql',q['sql'],'```','结果（仅统计/类型）：`'+json.dumps(q.get('result'),ensure_ascii=False)+'`']
 lines+=['','| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |','|---|---|---:|---:|---|---|']
 for v in runs['runs']:
  for x in v['comparison']['levels']:
   mm={k:z for k,z in x['column_mismatches'].items() if z};lines.append('| '+v['label']+' | '+x['level']+' | '+str(x['row_scale'])+' | '+str(x['cell_scale'])+' | '+json.dumps(mm,ensure_ascii=False)+' | '+str(v['comparison']['first_match'] or 'L0–L3均不匹配')+' |')
 for x in trials:
  lines+=['',f'- {x["label"]}（{x["category"]}，{x["kind"]}）：行减少 {x["row_reduction"]}，格减少 {x["cell_reduction"]}。{x["reason"]}']
 if t in stoch:lines+=['','随机诊断：`records/019_stochastic_diagnostics.json`，保留全部比较列与官方键，只共同屏蔽指定随机量。没有复原 gold seed，不把它记为 U 单修。']
 if t=='customer360__conversion_funnel_analysis':lines+=['','补充键诊断：`records/019_funnel_key_diagnostic.json`。将 journey_efficiency_index 临时移出键仅用于定位，未改变本表官方判错或主试验比较键。']
 if main=='U':lines+=['','U 条件：P 及反例见结论和核实查询；实际可见材料见下一节；仅指定取列/解析/同键结合的改动达到第4条件。'+('原始轨迹未出现检验该格式可解析性的查询；schema 中 VARCHAR 本身不足以判定 P。' if t=='stg_pendo__user' else '对重复/缺失的已有提示不等于验证了代码依赖的等价性，按手册保留“证据曾出现但被忽略”（适用时）。')]
 lines+=['','## agent 可见证据及不确定性','',f'event {uq["event_id"]} / {uq["field"]}，`{uq["path"]}`，字段字符偏移 {uq["start_offset"]}。','', '> '+uq['quote'].replace('\n','\n> '),'', '原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。', '', '## 不确定与限制','', '单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。', '', '## 规则问题','',rules.get(t,'未遇到需要改变手册定义的问题。')]
 if r['purpose']=='校准':lines+=['',f'盲标封存：`records/019_calibration_blind_sealed.json`，时间 {sealed["sealed_utc"]}。封存前未读取014–018标注；封存后比较只报告分歧，不回写本表盲标结论。']
 (OUT/(r['stem']+'.md')).write_text('\n'.join(lines)+'\n')
with (OUT/'019_summary.csv').open('w',newline='') as f:w=csv.DictWriter(f,fields);w.writeheader();w.writerows(results)
(REC/'019_decisions.json').write_text(json.dumps(decisions,ensure_ascii=False,indent=2)+'\n')
comparisons=[]
for t,b in blind.items():
 old=next(x for x in previous if x['表']==t);new=next(x for x in results if x['表']==t);comparisons.append(dict(table=t,blind_category=b['category'],previous_018_category=old['主要原因类别'],category_agrees=b['category']==old['主要原因类别'],blind_uncertainty=b['uncertainty'],previous_018_uncertainty=old['不确定性四档'],uncertainty_agrees=b['uncertainty'] in old['不确定性四档'],reason=b['rule_issue']))
(REC/'019_calibration_comparison.json').write_text(json.dumps(dict(seal_sha256=hashlib.sha256((REC/'019_calibration_blind_sealed.json').read_bytes()).hexdigest(),comparisons=comparisons),ensure_ascii=False,indent=2)+'\n')
full=[x for x in decisions if x['purpose']=='全量'];dist=Counter(x['category'] for x in full);udist=Counter(x['uncertainty'] for x in full);layers=Counter(x['layer'] for x in full);summary=dict(full_count=len(full),calibration_count=2,categories=dict(dist),uncertainty={k:udist[k] for k in ['针对本表的具体说明','只有通用策略说明','看到了但没提','没有迹象']},layers=dict(layers),layer_categories={l:dict(Counter(x['category'] for x in full if x['layer']==l)) for l in layers},layer_uncertainty={l:dict(Counter(x['uncertainty'] for x in full if x['layer']==l)) for l in layers},rule_questions=rules)
(REC/'019_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary,ensure_ascii=False,indent=2)[:3000])
date=datetime.now(ZoneInfo('Asia/Singapore')).strftime('%Y-%m-%d');report=ROOT/'notes'/f'019_{date}_全量标注_impl-001至005.md'
text=f'''# 任务 019：全量标注 impl-001 至 impl-005

## 任务

按冻结的 `docs/标注手册_v2.md`，标注 013 状态为待标注、排除试标30张后的 impl-001～005 表；另盲标 impl-008 int_asana__task_projects 与 impl-021 int_klaviyo__person_metrics。原记录与原库不修改。

## 结论

已核实范围为 **43张全量 + 2张校准**，与预期一致。全量类别分布：{dict(dist)}。四档分布：{summary['uncertainty']}。按层：{dict(layers)}；逐层类别与四档见下表。

校准 Asana 的主要类别 U、四档“看到了但没提”与018一致。Klaviyo 本次盲标 C / 看到了但没提，018 为 U / 只有通用策略说明，两项不一致。已保留封存判断，将“同日多事件不改变计数”是规定做法还是描述数据性质的 C/U 边界，以及共享重复计数说明的适用范围记为规则问题；没有为匹配018而改标签。

## 详细发现

### 范围与交付

- 43份新增精简包：`records/019_packages/`；校准复用013包。内容只摘原文与机械统计。
- 45份逐表 Markdown 和 `records/019_annotations/019_summary.csv`。汇总字段沿用018，仅删除“与上一版相比是否变化及原因”；最后两行的描述以【校准】标记。
- 每张表保留原始/基线/单处改动的 L0–L3、整表首次匹配、行/格规模和每列不一致；结构化结果为 `records/019_reruns_*.json`。
- 主因按行改善、再按格改善选择；同类并列直接归该类。同源替代修法不重复计因素；未改善不计参与因素。

| 层 | 表数 | 类别分布 | 四档分布 |
|---|---:|---|---|
'''
for l in layers:text+=f'| {l} | {layers[l]} | {summary["layer_categories"][l]} | {summary["layer_uncertainty"][l]} |\n'
text+='''
### 关键判据

1. 多张 Lever/Pendo 复杂输出存在常量/NULL占位，原最终报告明确披露的保留 D + 已披露；披露不改变类别。
2. Customer360 customer 的维度键不唯一；恢复按键结合后 L0 完全匹配。Pendo user 的日期文本直接转换失败，格式修正的单处影响达到 U 门槛。
3. Salesforce 两张快照及 Customer360 phone/status/updates 的 O 依据最大时间候选或多重集诊断，不根据一次偶然重跑通过改写官方状态。
4. gold 上游额外列可在 CS 中遮蔽 `SELECT *` 后的重算列；gold 与契约的 NULL 传播、粒度、类型及两平台规则不一致时，分别保留 O 证据。
5. 运行时间在每张表的 baseline 与所有修改中固定。随机模型另设固定 seed，并以共同屏蔽契约允许随机列作 O 诊断；gold seed未知，未伪称普通修复完全一致。

### 执行纠错与验证

材料生成曾因 impl-004 两份 result.md 中断，随后明确采用项目根目录最终报告。局部重跑曾有别名绑定错误，修正后重跑；初始失败日志保留，不计作成功证据。最终逐项验证报告在 `records/019_validation.json`，包含范围、字段、精确补丁重建、原句偏移、核实上限及规模算术。补充快照后的22张重跑开始时间也逐一检查。

最终完整性校验通过：136次成功试验，补丁重建、SQL字节哈希、行/格规模算术及轨迹引用均通过；主快照6713项及补充快照19项在对应执行前后均无变化。已有记录未修改，原库未写入。

### 规则问题

完整逐表问题在 `records/019_summary.json` 和对应 Markdown；重点包括校准C/U分歧、未规定解析器、CS额外列、随机模拟、未指定完整分类阈值、隐含自连接与声明粒度冲突。未修改冻结手册。

## 证据来源

- `records/019_scope.json`、`records/019_package_inventory.json`：精确范围与材料出处。
- `records/019_input_before.json`、`records/019_input_after.json`、`records/019_input_supplement_before.json`、`records/019_input_supplement_after.json`：执行前与完成后的 size/mtime_ns/SHA-256。主快照在首次执行前完成。最终检查发现漏列19个历史派生比较库，保留原快照另作补充快照，然后重新生成受影响22张表的材料统计及全套baseline/单修；补充快照在这次重复执行前完成。014–018标注在盲标封存前仅作字节哈希。不能把补充快照称为首次执行前已存在。
- `records/019_queries.json`、`records/019_calibration_queries.json`、`records/019_stochastic_diagnostics.json`、`records/019_funnel_key_diagnostic.json`：核实与诊断SQL及结果。
- `records/019_uncertainty.json`：事件号、字段、路径、原句和偏移。
- `records/019_patch_plan.json`、`records/019_decisions.json`：逐处修法、原因、贡献排序。
- `records/019_calibration_blind_sealed.json`、`records/019_calibration_comparison.json`：先封存，后对照018。
- raw一致性参照已打开的 `notes/015_2026-10-29_gold原始表一致性检查.md`（实际文件名以notes/015为准）及 `records/015_raw_impl-001.json`～005：本批五题原始三侧一致，不适用“不可评估”。

执行入口（均在仓库根目录，Python为 `/home/katherine/dac/.venv-openhands/bin/python`，`PYTHONPATH=data/005_tools`）：

```bash
python3 scripts/fingerprint_dacomp_batch019.py
python -B scripts/prepare_dacomp_batch019.py
python -B scripts/calibrate_dacomp_batch019.py
python -B scripts/query_dacomp_calibration019.py
python -B scripts/plan_dacomp_batch019.py
python -B scripts/run_dacomp_batch019.py --task impl-001
# 同样执行 impl-002、003、004、005；局部补跑见019_trials日志
python3 scripts/supplement_dacomp_batch019.py
python -B scripts/query_dacomp_batch019.py
python -B scripts/diagnose_dacomp_batch019.py
python -B scripts/diagnose_dacomp_keys019.py
python3 scripts/uncertainty_dacomp_batch019.py
python3 scripts/write_dacomp_batch019.py
python3 scripts/validate_dacomp_batch019.py
python3 scripts/fingerprint_dacomp_batch019.py after
```

新增材料完整中间JSON可由prepare脚本重建于 `data/019_packages_work/`；私有库/SQL位于 `data/019_work/`，不纳入git。记录中的补丁和SQL哈希允许复核单处改动；日志及统计纳入git，不含原始数据或凭据。

## 不确定或没查到的

- 首次输入快照漏列19个历史派生库；已补快照并重做其全部22张关联表的材料/重跑，不掩盖这一执行偏差。
- 两张校准不是全量一致性证明，Klaviyo明确存在分歧。
- golden随机种子及所有并列项的原始物理行序未找到，不能保证复现其逐字节偶然值。
- 单处改动不等于整表完整修复；未匹配的试验明确保留残余规模。D的局部补齐仅证明相应占位/降级的贡献，不声称所有复杂指标已实现。
- 本次规则问题是按v2第9节作出的具体选择，须由用户与Claude复核，不能把其中涉及的解释自动推广为手册修订。

## 建议的下一步

先复核校准Klaviyo的C/U边界及不确定性范围，再复核本批规则问题。若仅确认操作解释，后续仍用v2；如决定改变类别定义，按手册要求重标受影响的全部已有表。
'''
prior=list((ROOT/'notes').glob('015_*.md'));text=text.replace('notes/015_2026-10-29_gold原始表一致性检查.md',str(prior[0].relative_to(ROOT)) if prior else 'notes/015')
report.write_text(text);print(report)
