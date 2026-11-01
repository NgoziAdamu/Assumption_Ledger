"""Complete 038 report from reviewed decisions and final validation."""
from pathlib import Path
from collections import Counter
import json,subprocess,re
R=Path(__file__).resolve().parents[2];D=R/'records/038_checks'
dec=json.loads((D/'formal_decisions.json').read_text());v=json.loads((D/'validation.json').read_text());ps=[p for o in dec for p in o['points']]
assert v['task_complete']
phase1=subprocess.check_output(['git','show','967056d:notes/038_2026-11-01_DAComp重标第二批.md'],cwd=R,text=True)
cal=phase1.split('### 2. 盲标封存和解盲',1)[1].split('### 4. 正式表准备',1)[0].strip()
md=['# 038：DAComp 按 v3.2 重标第二批（完整批次）','## 任务',
'承接 `records/038_checks/phase1_handoff.json`，完成 impl-006～007 的43张正式表，另有2张已完成盲标校准表。初始任务检查确认038未占用；第二阶段沿用038，替换本报告为完整报告。现有CSV中的2张校准/5个点保持原行，后面追加43张正式表；封存件和解盲对比不修改。',
'## 结论',
f'已完成 **43＋2＝45张表、193个标注点/同类缺口组**：正式188，校准5。45份逐表说明齐备；最终验证通过，{v["quote_count"]}条契约、SQL和披露引句逐一回查成功，{v["protected_file_count"]}个018～037记录/报告及v3.1、v3.2手册保护项的hash未变。盲标封存hash未变。',
'正式表主因：Unstated Choice 10、多因并列10、Quiet Downgrade 8、已说出的降级6、其他5、Intent Misreading 2、代码写错2。只按逐点证据判断，没有预期类别分布。复杂模型的整体占位按手册第7节记录同类缺口组、把握中；没有把whole_implementation_diagnostic当成每个缺失字段的独立修复。',
'校准主因一致率2/2，逐点类别和角色各5/5，五档2/5。解盲后仅工作结果中URL和两项电话由第4档改第2档；所有一致率仍按盲标封存件计算。',
'## 详细发现','### 范围与逐表结果',
'从013的status=待标注、task=impl-006/007的45行，减去036已有的 `impl-006_stg_reddit_ads__campaign_report`、`impl-007_stg_apple_store__sales_subscription_event_summary`；精确得到32＋11＝43张。校准为 `impl-002_stg_pendo__guide_event`、`impl-025_stg_twilio__call`。起始清单和最终复算均为43，见 [038_scope.json](../records/038_scope.json)。',
'| 对象 | 层 | 主要原因 | 点/组数 |','|---|---|---|---:|']
for o in dec:md.append(f'| `{o["object"]}` | {o["layer"]} | {o["main"]} | {len(o["points"])} |')
md+=['### 主要原因分布（43张正式表）','| 主要原因 | staging | intermediate | marts | 合计 |','|---|---:|---:|---:|---:|']
for cat in sorted(set(o['main'] for o in dec)):
 c=Counter(o['layer'] for o in dec if o['main']==cat);md.append(f'| {cat} | {c["staging"]} | {c["intermediate"]} | {c["marts"]} | {sum(c.values())} |')
md+=['多因并列按表单列，未分摊进单类：']
for o in dec:
 if o['main']=='多因并列':md.append(f'- `{o["object"]}`：'+ '；'.join(o['tied_categories'])+'。具体并列点、行/格减少量见逐表说明。')
md+=['### 是否说出五档（188个正式点/组，含非原因）','第1档只认交付物针对本处；第2档为通用说明；第3档要求中途明确疑问/备选/缺失/冲突。第4档为已看相关信息但无意识迹象，第5档为没有迹象。','| 类别 | 第1档 | 第2档 | 第3档 | 第4档 | 第5档 | 合计 |','|---|---:|---:|---:|---:|---:|---:|']
for cat in sorted(set(p['category'] for p in ps)):
 c=Counter(p['grade'] for p in ps if p['category']==cat);md.append('| '+cat+' | '+' | '.join(str(c[i]) for i in range(1,6))+' | '+str(sum(c.values()))+' |')
c=Counter(p['grade'] for p in ps);md.append('| 合计 | '+' | '.join(str(c[i]) for i in range(1,6))+' | 188 |')
md+=['角色分布：主要27、并列97、参与43、非原因21。角色是点/组口径，与43张表的主因数不同。没有“只能组合修复”的对象。',
'主口径只有第1档将Choice/Downgrade改记“已说出”；另报第1、2档都算说出的口径时，五档原值不变，仅改变类别汇总：','| 另报类别（第1＋2档算说出） | 正式点/组数 |','|---|---:|']
alt=Counter(('已说出的选择' if p['base_category']=='Unstated Choice' else '已说出的降级') if p['grade']<=2 and p['base_category'] in ['Unstated Choice','Quiet Downgrade'] else p['category'] for p in ps)
for cat,n in sorted(alt.items()):md.append(f'| {cat} | {n} |')
md+=['### 关键事实与分类',
'**fallback与代码覆盖分开。** 026指出account_report由event27的fallback生成，已回查脚本：取第一个source_model、按候选投影、否则整列NULL；没有account聚合。该表归Quiet Downgrade第2档，保留020旧C仅供追溯。另有6个staging的spend/campaign_id点，在event19字典中能看到正确候选先写、同键后写覆盖，归代码写错；这些点使用020_resume的恢复候选实验。',
'**NULL逐列区分。** Amazon keyword/product/search的归因字段无对应raw列，填0/NULL未定，归Choice；同表CTR/CPC有clicks/impressions/cost，整列NULL归降级。Facebook action字段、Pinterest微单位成本/转换价值和点击候选均存在，不能归“无源”。Twitter app_installs有mobile_conversion_installs_order_quantity等候选，038恢复候选只改善21格；020补0改善900格仅定位gold默认策略，不用它给恢复候选的降级点排序。app_opens则未找到对应候选。',
'**先契约、后数据事实。** Amazon ad_group非法ID的regex/delete_row、Apple ad_group货币允许集及0–1转换率均有明确算法，归Intent。Amazon ID使用契约删除实验，未拿gold置空实验当作正确修复。Apple货币新核实1500行均不在允许集，改变的是值清理，不只是大小写呈现。unified_campaign_metrics的ROAS额外ROUND和CTR平台兜底也由契约定下，归Intent。',
'**键掩盖的缺口仍列出。** 新补Apple campaign三个NULL指标、Google ad_group两个转换策略和一个中途BIGINT、TikTok六个脏值策略的单点实验。全部从原始基线独立改动，键差异仍在，规模无减少；保留“存在未确立的前提，但不是判错原因”，不记参与。两张月度mart的placeholder过滤亦单改无改善。区域mart的avg_cpm单改反增411格，也不记参与。',
'**impl-007的Other逐点定位。** overview的gold按位置UNION导致Apple downloads/deletions互换，而agent按字段含义正确；user_value_segmentation的ROI短标签符合契约，另有浮点末位呈现差异；Apple financial revenue的BIGINT符合契约而gold保留小数；ratings_overview依约删9条越界而gold填3；traffic_source的3条非法rate依约nullify而gold重算，另1条合法rate保留/重算未定，后者单列Choice。',
'### impl-007交付物情况（单列）',
'原始0～69共70个事件，无finish。event65写/workspace/result.md失败，66返回路径不存在；event67重试，68返回Read-only file system及路径不存在；event69因ServiceUnavailableError终止。留存树无result.md。已扫描全部51个交付SQL，无注释。两次报告草稿均不构成交付物，因此11张正式表中没有第1、2档。证据见 [delivery_sources.json](../records/038_checks/delivery_sources.json)。',
'仅sales_subscription_summary两个点采用第3档，依据event65草稿的组级疑问：“Apple 订阅 summary/event 字段有若干原始字段与 staging 字段语义不完全一致，使用可用列映射且转换兼容字段类型。若这类字段用于正式订阅财务决策，应以源端字段定义进一步确认。”没有将这句扩展到financial表或Google Play。其余点第4档；单纯说明自己按哪列映射、按什么规则删行，不当作已经意识到别的做法。',
'impl-006的第1档只用于finish97明确点名的country_mapping，以及“客户旅程、地理分析、时间序列、预测及执行仪表板”对应五表。逐表文件均写明原句和点名对应关系。该句不推广到account、ad或月度报表；后者只适用通用NULL策略的第2档。',
'### 盲标封存及校准',cal,
'### 证据复用、新做与保护',
'020以2026-10-30定稿和020_summary.csv为准，10-29暂停报告不作为定稿标签来源。43张的020旧主要原因逐字填入两个CSV最后一列；旧类别没有用来生成v3.2类别。43张契约均与原始文件对应行一致且初始event1完整可见；材料包SQL与交付SQL一致。',
'新增4条核实查询，分别用于Apple ad_group货币、Google account布尔文本、TikTok脏值分布、Twitter安装候选。连同020复用及失败查询，各表均≤5条；Google ad_group保持5/5，未新增核实。新增7张表的16项干预，其中15项指定单处SQL修改、1项只改CLV输出呈现比较条件；每项均记录L0–L3及自身基线。',
'数据库原件均READ_ONLY打开；新重跑仅在内存创建私有表，未写原数据库。staging使用agent留存raw，其他层沿用020逐表标准上游口径。未调用agent，未下载数据，未做其他批次。records没有数据库或原始数据副本，仅保存查询语句、汇总统计、SQL差分和比较结果。',
'013已记录impl-006初始/留存raw各125张、impl-007各25张，different_tables均0；013_raw_differences无两题条目。本次复核记录，未新做全库内容相等性检查，也未发现相反证据。',
'最终验证：45表范围、43正式表分题32/11、点键唯一、五档合法、类别与第1档一致、CSV列名、020旧标签、校准工作行、主要原因排序、原文引句、单点差分及历史hash全部通过。第一阶段handoff保留为历史起点，当前完成状态以 [validation.json](../records/038_checks/validation.json) 的 `task_complete=true` 为准。',
'## 证据来源',
'- [对象CSV](../records/038_objects.csv)、[点CSV](../records/038_points.csv)、[45份逐表说明](../records/038_annotations/)。',
'- [正式逐点决定](../records/038_checks/formal_decisions.json)、[披露审计](../records/038_checks/disclosure_audit.json)、[全部引句回查](../records/038_checks/quote_checks.json)、[最终验证](../records/038_checks/validation.json)。',
'- [新核实查询](../records/038_checks/new_verification.json)、[新单改计划](../records/038_checks/new_patch_plan.json)、[差分验证](../records/038_checks/rerun_validation.json)；7份rerun_impl-*.json列明每个SQL及L0–L3。',
'- [证据索引](../records/038_checks/evidence_catalog.json)、[026事实核对](../records/038_checks/fact_corrections.json)、[013原始数据复核](../records/038_checks/raw_integrity_review.json)、[020定稿](020_2026-10-30_全量标注_impl-006至007.md)、[037做法](037_2026-11-01_DAComp重标第一批.md)。',
'第二阶段实际命令（在仓库根目录；封存脚本不重跑）：',
'''```bash
/home/katherine/dac/.venv-openhands/bin/python records/038_checks/new_verification.py
/home/katherine/dac/.venv-openhands/bin/python records/038_checks/new_checks.py 20 24 30 31 34
/home/katherine/dac/.venv-openhands/bin/python records/038_checks/new_checks.py 10 11
python3 records/038_checks/render_phase2.py
python3 records/038_checks/validate.py
python3 records/038_checks/report_phase2.py
```''',
'## 不确定或没查到的（含规则问题）',
'1. **布尔/脏文本的数值恢复边界。** Google account、Google ad_group、Twitter follows/likes及LinkedIn、Snapchat、TikTok部分指标可读成“TRY_CAST大面积失败”的Data，也可读成未规定的类型修复政策。本次选择后者、中把握：例如Google account有700条true/false，但把true解释为金额1或次数1、把缺失/任意脏文本补0，并非数据本身能唯一确定；未证成“原本有唯一可恢复数值”的P。与037可恢复时间文本变NULL区别在于数值语义本身未定。该选择没有依照gold定义正误；将此边界显式提交复核，不改手册。',
'2. **整体占位的细分粒度。** 8张fallback模型和country_mapping按共享替代行为记录同类缺口组；各缺失功能在逐表文字列明。若逐列算点会大幅增加点数，但现有整段重写不能提供独立字段贡献。依第7节同类候选规则给中把握，报告统计明确含“组”，不声称所有字段贡献已分别排序。account不是依据026的旧D直接贴类，而是原始脚本、契约和交付物重新判断。',
'3. **窗口并列顺序。** int_app_health_metrics上游确有重复日期键；非窗口基础列一致。契约只规定按date排序，未明确允许任意并列顺序，故Choice而非第6节Other。两处窗口ORDER与LAG共享前提，现有诊断不能唯一复现gold；中把握，不声称全量修复。',
'4. **country_mapping缺少枚举输入。** 选择“自造替代品”的降级读法，已经具体披露；不把gold的完整清单强加给agent。不把缺少输入和可任意选一国等同。',
'5. **单改规模受重复键配对影响。** 月度mart出现同一列改动带来大幅格子配对变化或负改善，仍使用既定L0整表行优先/格次之，不相加贡献。旧整段诊断后的残余差异不拿来反向证明原始占位SQL的另一个独立原因。',
'6. 没有查到impl-007成功交付报告；已查finish事件、两次写报告命令及返回、留存result.md和全部SQL注释。不存在的交付物不补全、不推测。',
'## 建议的下一步',
'由用户与Claude复核本批已单列的规则边界和同类缺口组粒度；其余批次仍按原计划串行推进。本次任务038的范围、校准、正式标注、完整报告及最终验证已完成，不扩展到第三批。']
(R/'notes/038_2026-11-01_DAComp重标第二批.md').write_text(re.sub(r'\|\n\n(?=\|)', '|\n', '\n\n'.join(md))+'\n')
print('complete report written')
