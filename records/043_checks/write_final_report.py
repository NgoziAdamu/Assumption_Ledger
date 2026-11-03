"""以已验证的043正式结果更新唯一043报告；保留第一阶段校准说明。"""
from pathlib import Path
import json
K=Path('records/043_checks');N=Path('notes/043_2026-11-03_DAComp重标第六批.md')
def load(p):return json.loads(Path(p).read_text())
formal=load(K/'formal_working.json');stats=load(K/'formal_statistics.json');roots=load(K/'shared_root_decisions.json');validation=load(K/'validation.json')
assert validation['status']=='passed'
prior=N.read_text();cal=prior.split('### 2. 盲标封存、解盲与校准定稿\n',1)[1].split('### 3.',1)[0].strip()
lines=['# 043：DAComp 按 v3.2 重标第六批（完整报告）','', '## 任务','',
'完成impl-022～030的50张正式表，并保留2张盲标校准。使用冻结的 `docs/标注手册_v3.2.md`；逐点按第3～8节重判，旧024类别只作原样回填。正式结果追加到第一阶段CSV之后，校准封存、解盲比较和定稿均未改。', '',
'第一阶段开始时确认notes/、records/没有043，之后按用户明确要求在本会话继续第二阶段；未另开编号。封存前只从036取完整对象编号排除试点，未看禁止的校准标注和037～042报告；仅读042表头。第二阶段没有调用agent/子agent、下载数据、新连数据库或执行轨迹命令；未读取041正文，未改018～042及手册。', '',
'## 结论','',
'**任务043已完成：正式50张（其中48张可评估、2张不可评估），另有校准2张；最终52份逐表说明、52行对象CSV、217行点CSV。** 正式部分182点，校准35点分开统计。52张最终验证全部通过，校准前缀逐字节不变，封存hash不变。', '',
'正式表主因：其他15、多因并列10、Intent Misreading 9、Data Misconception 7、Unstated Choice 4、已说出的选择2、代码写错1、不可评估2。排序严格先比行、再比格；4张为只能组合修复，另2张全部候选属于其他，依手册第7节记同类主因、中把握，不虚构逐列收益。', '',
'Zuora最终执行使用正常多列raw；早期曾看见单列坏结构。已追溯到benchmark原版run.py的导入展开逻辑，而非agent新增修复代码。event45同一外键映射决定涉及14张、43点，其中22点Data、21点Choice；22个Data均记录event19曾经理解对过。共同生成动作目录覆盖本批所有50张，包含12个脚本/批量写入动作，不限于event45。', '',
'## 详细发现','', '### 1. 范围与交付','',
'按013的待标注状态和完整task号筛选，再按完整对象编号排除036的9张试点，无子串匹配。正式范围为023：9、024：4、025：2、026：10、027：4、028：3、030：18；022、029各0，合计50。初始逐张清单保存在 [043_scope.json](../records/043_scope.json)，最终逐张主因如下。', '',
'| 正式对象编号 | 主要原因 | 点数 | 只能组合修复 |','|---|---|---:|---|']
for o in formal:lines.append(f"| {o['object_id']} | {o['main']} | {len(o['points'])} | {'是' if o['combination_only'] else '否'} |")
lines+=['', '所有表的完整契约块、交付SQL路径与hash见 `formal_material_audit.json`；182点的L0～L3基线、单改后规模、精确替换及来源见 `formal_working.json` 和逐表说明。staging复用单改使用agent留存raw，中间层及之后用gold上游的CS口径。最后一列“024旧标签”逐行与024旧主要原因完全一致。', '',
'### 2. 盲标封存、解盲与校准定稿','',cal,'',
'### 3. 正式批逐点统计与主要原因排序','',
'下表仅182个正式点；不把35个校准点混入第六批分布。统计保留非原因点、组合项及同类候选，不能把全部点都解读为对评测差异有独立贡献。','',
'| 类别 | 点数 | 第1档 | 第2档 | 第3档 | 第4档 | 第5档 |','|---|---:|---:|---:|---:|---:|---:|']
for c,n in stats['points'].items():
    ps=[p for o in formal for p in o['points'] if p['category']==c]
    lines.append('| '+c+' | '+str(n)+' | '+' | '.join(str(sum(p['disclosure']==i for p in ps)) for i in range(1,6))+' |')
lines+=['',
'角色：主要30、并列51、参与35、组合项14、同类候选6、非原因46。五档合计为7／92／3／80／0。主口径仅第1档算具体说出；另报第1+2档时，共99点有具体或通用披露。Unstated Choice 59点中42点只有通用说明；若第1+2档都算说出，Choice家族62点中45点被说明（3个已说出的选择+42个通用说明），这只是另报口径，不改CSV类别。正式批无Quiet Downgrade和Form Mismatch，不预设分布。', '',
'全部正式交付SQL均无注释。披露依据只用finish final_thought（完整报告另存 `formal_delivery_sources.json`），第3档只在TikTok共享CSV解析问题上有event19比较两种解析方法、event39改写分支的组级意识证据。一般“完成”“采用安全转换”不能推广到无关的取列或预先改值决定：TikTok budget和Twilio三处电话标准化均记第4档。', '',
'主因用L0的行减量优先，行减量相同才比格减量；L1～L3同时列出作诊断。行数增加时不靠格子减少把它升为主要或参与。只有所有单改都不减少行或格、组合减少时才记“只能组合修复”。', '',
'| 表 | 基线L0 行/格 | 所有单改是否改善 | 组合L0 行/格 | 组合L1～L3 | 类别与处理 |','|---|---:|---|---:|---|---|',
'| 023 account_history | 2500/22500 | 否，id_filter反而增差 | 11/11 | 均11/11 | 全为其他；组合项id_type/id_filter/timezone_filter |',
'| 024 ad_report | 2499/7484 | 否，ads_source_join格数反而增差 | 0/0 | 均0 | Intent + Choice；4个组合项 |',
'| 024 url_report | 2499/109956 | 否，ads_source_join行数反而增差 | 0/0 | 均0 | Intent；3个组合项 |',
'| 030 invoice_payment | 12/324 | 否，4个外键单改均12/324 | 6/6 | 均0 | Data + Choice；4个外键组合项；refund_type单改零改善，非原因 |', '',
'invoice_payment不能写成L0完全修复：剩余refund布尔/数值表示在L1以后消失。Social media rollup的两列并列排名、Xero invoice_line_items的两列顺序派生值只做过成组诊断；结合Xero两处浮点求和点，两个对象的全部候选都属其他，故用手册允许的同类候选例外。没有把成组清零的收益分摊到单列。', '',
'### 4. 不可评估表及依据','',
'- `impl-028_stg_youtube__channel_basic`：直接读取agent的`raw.youtube_channel_basic_data`（3500行）；024诊断确认agent与initial逐值差集0。gold读取另一套`channel_basic_a_2`原始表，结构与行数不同。按第6节不可评估，0错误点，不填五档。',
'- `impl-028_stg_youtube__video`：直接读取agent的`raw.youtube_video_data`（2501行）；agent与initial逐值差集0。gold读取另一套`video`，同样不可评估。',
'- `impl-028_int_youtube__video`：以gold staging为输入正常按CS评估。三处thumbnail正则在quoted heredoc内多转义一层，三个单改各减少0行、5格，均为代码写错并列；缺失URL应NULL和DATE声明冲突点另列其他、非原因。不能由同题raw不同或agent全流程的缩略图空值将此表也判不可评估。', '',
'013、015及024的逐值差集诊断都已回查；不是仅凭raw表名不同推断内容不同。两张不可评估仍有说明文件和对象行，排除在182点及根源错误点统计外。', '',
'### 5. 原始数据有变化的各题怎么处理','',
'| task | 013变化 | 015 gold–agent关系 | 本批处理 |','|---|---|---|---|',
'| 022/023/024/026/027 | 无 | raw一致 | 正常标注；022无正式表 |',
'| 025 | call_data_snowflake、message_data_snowflake，列数和行数不变但schema不同 | 变化gold也有 | 两张正式表照常标；实际直接源incoming_phone_number_data/message_data仍用agent留存，不能把Snowflake源的变化泛化到每张raw |',
'| 028 | agent与initial无变化 | gold与agent各3张、名称集合不同 | 两张staging不可评估，int按CS |',
'| 029 | brand_data_postgres、user_data_snowflake有变化 | 变化gold也有 | 本批0正式表，仅记录013/015背景，不扩展标注范围 |',
'| 030 | account/amendment/contact/invoice/taxation_item从1列展开 | gold与agent留存raw一致 | 正常标注；逐表写版本，解释如下 |', '',
'Zuora初始五张坏结构表只有一个列名，多个header挤在一起；展开后account 56列、amendment 33列、contact 28列、invoice 54列、taxation_item 56列，行数不变。逐张对照及原句见 `raw_integrity_review.json`。', '',
'已经核实的过程：event10展示原版`run.py`的`if len(sinfo) == 1`分支，按逗号拆header与每行内容再导入raw；event18检查初始源时仍见缺列；event31执行`python3 run.py`触发已有导入逻辑；event40打印正常54列invoice；event45再生成错误外键映射。initial与agent留存`run.py`的SHA-256同为`28dc6705cef9f39f8262598fde54403e48bffd9d91c5224b7b842b1a9c07d687`。这是运行已有benchmark导入程序的结果，不把留存一致性推断成agent自行写了修复程序。', '',
'本批Zuora staging最终读取正常结构。直接源曾坏的account/amendment/contact/taxation_item，说明里同时记录早期坏结构和最终正常列数；其余直接raw源初始就是正常多列。invoice本身不在这50张待标范围，但它的54列恢复影响整题执行环境，两个marts说明中均注明最终执行时正常、本次CS输入仍是gold上游。正常列结构不等于字段值语义全部正确，invoice_item/taxation_item部分候选列内容错位，所以仍逐列核实关系。', '',
'### 6. 026相关条目的最终处理','',
'- **024-1**：按新排序重新检查TikTok两张最终层与Zuora invoice_payment，均确属只能组合修复，详见上表。没有将“行数不变但格子减少”的点误记成只能组合修复。',
'- **021-2**：亲自回查event19的`srcname=n`和event45的`if n in pk_alias: srcname=\'id\'`。22个Data点的曾经理解对过均为是；证据在场均否，因为原轨迹看过列名和自己的投影，但没见能单凭它否定P的目标匹配对照。该全局规则有43个点、14张表，台账“12张”是旧U涉及范围，不能当作全局规则全部范围。',
'- **account_history**：2500个原始id均不可转数字；契约明确BIGINT/not_null。agent照做输出0行，归其他。event53报告及finish55均明确点名，id_type/id_filter记第1档，timezone仅通用过滤说明第2档。不能按旧类别或空输出本身判误解。',
'- **impl-028**：两张staging按不可评估，中间层照常；直接内容差集诊断已用于第4节。',
'- **024-2，同源决定**：补齐共同生成脚本、批量SQL写入动作及各表各点，不只event45；按下面两种去重口径另报统计，原主因排名不动。',
'- **024-3，快照限制**：最初hash扫描漏了编号目录下720个无编号子文件；补齐前用Git差异检查确认未改。最终2199项hash相同，但不声称这720项在首次读取前已快照。唯一阶段一只读查询未做数据库读前hash，也不声称已完成该项验证。', '',
'完整处理记录：[026_review_final.json](../records/043_checks/026_review_final.json)。准备件保留阶段一事实和pending状态供追溯，最终以final件为准。', '',
'### 7. 同源决定及按根源计的口径','',
'共同生成动作覆盖完整50张；包含一次写多个文件的shell heredoc，不局限于Python脚本。目录记录每个动作的event、原句、所有本批表及点。对同一文件内不同逻辑，不假设它们是同一个语义前提，因此另提供较细的规则归并结果。两种都是敏感性统计，不能用来改分类或重排主因。', '',
'| 共同生成脚本／动作 | event | 本批表数 | 点数 |','|---|---|---:|---:|']
for f in roots['generation_families']:lines.append(f"| {f['task']} {f['script']} | {','.join(map(str,f['events']))} | {f['table_count']} | {f['point_count']} |")
lines+=['',
'按上表共同生成动作合并，12个动作中11个有可评估错误点，另1个只涵盖两张不可评估staging。11个单元按类别集合互斥统计如下；一个单元含多类时保留整个集合，不随意指定一个“主类”。', '',
'| 类别集合 | 共同生成单元数 |','|---|---:|']
for c,n in roots['generation_counts']['category_sets_mutually_exclusive'].items():lines.append(f'| {c} | {n} |')
lines+=['','进一步仅归并能确认同一实现规则的点，以下11条共享规则覆盖118点，其余64点各保留为独立单元，得到**75个根源决定单元**。同一脚本中的多个独立表达式不强行认作一个认识。','',
'| 同一规则 | event | 表数 | 点数 |','|---|---|---:|---:|']
for r in roots['decisions']:
    if r['point_count']>1:lines.append(f"| {r['id']}：{r['description']} | {r['event']} | {r['table_count']} | {r['point_count']} |")
lines+=['','| 类别集合 | 较细根源单元数 |','|---|---:|']
for c,n in roots['root_decision_counts']['category_sets_mutually_exclusive'].items():lines.append(f'| {c} | {n} |')
lines+=['',
'这两种根源口径都包括非原因点及其他类差异，不是“已证实导致判错的独立决定数”。若按类别分别计出现，混合单元会重叠；JSON同时提供互斥集合和非互斥出现次数，不能相加后解释为独立样本。逐表均有“同源决定：event编号+描述”，完整成员见 [shared_root_decisions.json](../records/043_checks/shared_root_decisions.json)。', '',
'### 8. 最终检查','',
f"[validation.json](../records/043_checks/validation.json) 中 {len(validation['checks'])}/{len(validation['checks'])} 项通过。覆盖52张精确范围、217个唯一点键、五档与改名一致、024旧标签、校准字节前缀、5个校准文件hash、单改数值与排序、查询预算、原始契约/SQL/引句、所有共同生成成员和Zuora版本说明。", '',
'引句逐条回查原始事件字段，1340次引用核验、219条去重原句全部成功。正式50张的契约相关块逐张确认完整出现在event1；所有正式交付SQL与材料包一致且无注释。核实预算每表最多5条，正式50张共106条复用引用（14张Zuora各5条），无新核实查询、诊断查询或重跑；校准Reddit复用2+新做1=3，Workday复用1。', '',
'018～040、042及v3.1/v3.2手册共2199项hash未变；041未读取正文，用Git索引对象编号和工作区差异确认未改。最终只提交043的报告与记录，不包含数据库、原始数据、第三方代码或凭据。', '',
'## 证据来源','',
'- [对象CSV](../records/043_objects.csv)、[点CSV](../records/043_points.csv)、[52份逐表说明](../records/043_annotations/)。',
'- [逐点工作件](../records/043_checks/formal_working.json)、[完整契约块及交付SQL审计](../records/043_checks/formal_material_audit.json)、[核实查询目录](../records/043_checks/formal_query_inventory.json)、[披露审计](../records/043_checks/disclosure_audit.json)、[原句回查](../records/043_checks/quote_checks.json)。',
'- [封存](../records/043_calibration_blind_sealed.json)、[解盲比较](../records/043_calibration_comparison.json)、[校准定稿](../records/043_checks/calibration_working.json)、[阶段一交接历史](../records/043_checks/phase1_handoff.json)。',
'- `records/013_raw_impl-022.json`～`013_raw_impl-030.json`、对应015；`records/024_packages/`、`024_decisions.json`（仅定位旧点、数值及原样旧标签）、逐表`024_reruns_*.json`和补充重跑、`024_queries.json`、`024_mapping_queries.json`、`024_diagnostics.json`、`024_extra_diagnostics.json`。',
'- `records/026_Claude全量标注检查台账.md`；轨迹原文 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-NNN/agent/output.jsonl`；契约及最终SQL具体路径逐表列出。历史轨迹归档保留于既有traces，不另下载。', '',
'本阶段执行的构建、验证命令：', '', '```bash',
'python3 -B records/043_checks/build_formal.py',
'python3 -B records/043_checks/finalize_formal.py',
'python3 -B records/043_checks/validate_final.py',
'python3 -B records/043_checks/write_final_report.py',
'git diff HEAD --check','```','',
'`build_formal.py`将逐点人工规则与已有证据结合；`finalize_formal.py`汇编同源、CSV、说明及统计；二者不会连接数据库。按上述顺序复现正式部分，不能重跑封存脚本来替换校准。报告生成后再做一次最终验证和提交前检查。', '',
'## 不确定或没查到的（含规则问题）','',
'1. 校准Reddit四个派生/访问指标有“原始分项足以构成候选”与“目标含义仍未定”两种读法，解盲定稿取后者；三处TRY_CAST披露保留第2档，与036不同。封存和一致率不改。Workday拆组新增点不能用35点作为一致率分母。',
'2. Social media twitter_user_history的清洗与删除先后：有害字符规则可读成原值发现即删除，也可读成先按给定表达式清洗；本次harmful_filter按前者Intent、中把握。空值规则允许清洗后空串删除，empty_filter按其他、中把握。原样表达式无g这一点则按契约字面Intent。',
'3. TikTok age_groups解析：gold的截断不能当数据事实，契约未规定解析/序列化边界，取Choice。另三处header位置明确的budget/interest/languages按其他；不能用旧gold位置反向定义源含义。',
'4. Xero P&L允许并列顺序不确定，本次将逐行ROWS累计与gold RANGE整组累计的差异按其他；若把允许不确定仅限展示顺序，可能有另一读法。两张同类候选表仅有成组诊断，按手册例外标其他、中把握，未补造独立单改。',
'5. YouTube int的snippet_published_at既声明DATE又要求透传，按明确列类型给其他、中把握；该点单改无改善，不影响三处代码写错主因。',
'6. Zuora外键：命名候选全为一致ID格式、确有目标匹配而本表id完全无匹配时判Data；错位时间文本、无匹配或反向匹配时保留Choice，不用gold选列替代事实。product_rate_plan.product_id支持样本仅2/505，把握中；没有另设类别最低匹配率门槛。',
'7. 所有第1档功能名称均须与单表一一对应。Twitter Ads keyword report与account timezone在本题可一一对应；“raw Twitter report tables”等多表描述只算第2档。共同CSV解析问题的第3档采用手册允许的组级意识，未推广到预算取列或来源常量。',
'8. 同一脚本不必等于一个语义决定，因此同时给出11个有点的生成动作和75个细规则单元两种统计；不将任一去重数当作已建立的独立因果样本量。初始hash补快照与阶段一数据库读前hash限制如第6节，未隐去。', '',
'上述按第11节记录，未修改手册或扩大任务范围。', '',
'## 建议的下一步','',
'由用户与Claude复核列出的规则边界及同源计数口径，再合并037～040、042、043六批统计。合并时区分正式表与校准、不可评估表、组合项、同类候选、非原因点，以及逐点计数与根源决定计数。后续统计不属于本次043执行范围。']
N.write_text('\n'.join(lines)+'\n')
print(N)
