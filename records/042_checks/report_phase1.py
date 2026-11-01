from pathlib import Path
import json
R=Path('records');C=R/'042_checks'
def load(p):return json.loads(Path(p).read_text())
sc=load(R/'042_scope.json');v=load(C/'validation.json');raw=load(C/'raw_integrity_review.json')
s='''# 042：DAComp 按 v3.2 重标第五批（阶段一：准备与校准）

## 任务

按用户允许的两阶段交付，完成范围核对、文件保护基线、2张盲标校准与39张正式表的证据准备。**本报告不是完整批次报告：正式表完成0/39，校准完成2/2（3个点）。** 第二阶段在本会话继续，沿用042，不顺延、不重做盲标。

开工检查确认 notes/、records/ 没有042编号；当时Git工作区干净。本轮未调用agent或子agent。会话由用户端发起，没有用工具另建会话。冻结的v3.2手册未修改；041仅按最终保护要求计算hash，未查看正文。

## 结论

正式范围核对为 **4＋4＋9＋9＋3＋4＋6＝39张**，加2张校准共41张。按013“待标注”和完整对象编号精确排除036试点，排除7张；未用子串匹配。

盲标主因与036一致 **1/2**，点类别一致 **2/3**，五档一致 **3/3**。Google Play国家码点盲标判“其他”，解盲复核后改为Unstated Choice；因此解盲后主因一致2/2不能写成盲标一致。封存件保持原样。

阶段一验证通过：2份校准说明、2行对象CSV、3行点CSV齐备；19条引用回查原文成功，2119个018～041记录/报告及两版手册保护项hash未变。validation明确记 `task_complete=false`，39张正式表仍待逐点标注，未冒充最终41张通过。

## 详细发现

### 1. 正式范围与准备状态

| 对象编号 | 层 | 本阶段状态 |
|---|---|---|
'''
for x in sc['formal']:s+=f"| `{x['object_id']}` | {x['layer']} | 待正式标注；证据入口已齐 |\n"
s+='''
39张材料包、单改/补充单改JSON、查询入口已收集至 `records/042_checks/evidence_catalog.json`。程序逐张核对：契约块与完整契约原文件匹配、SQL与交付文件匹配，39张契约块都完整出现在event1初始提示中。这里只验证证据可用与未截断，尚未完成每个错误点的“证据在场/曾经理解对过”语义判断。

023_queries.json本批每表最多2条核实查询，含错误尝试字段一并登记。后续复用其他文件或新查时，仍需累计每表不超过5条。目录中的旧023主要原因只用于CSV最后一列原样存档，不作为新分类依据。

### 2. 盲标、封存与解盲

封存前只阅读手册、013材料、014/016/017查询和重跑、轨迹及交付物。036只投影读取对象编号筛范围，040只读取CSV表头；未看两张表的034/036标签、018逐表说明及037～040报告。封存后才打开036对象/点表、034的Google Play说明，以及040报告和检查脚本。

封存文件：`records/042_calibration_blind_sealed.json`。SHA-256：

```text
eaee3ade3d733b09e4b74667718af5e768e544c6e38a6097ed87d405498e7b33
```

封存时间与hash另存 `records/042_checks/calibration_seal_receipt.json`。解盲对比保存为 `records/042_calibration_comparison.json`；解盲后校准定稿单独在CSV、逐表说明、`calibration_working.json`，没有回写封存件。

| 校准表/点 | 盲标类别 | 036类别 | 解盲后定稿 | 五档 | L0行/格规模 |
|---|---|---|---|---:|---|
| Google Play country_value_only | 其他 | Unstated Choice | Unstated Choice | 4 | 15200/91200 → 2400/14400 |
| Google Play lookup_dedup | Data Misconception | Data Misconception | Data Misconception，参与 | 4 | 15200/91200 → 12800/76800 |
| TikTok email_pattern | Unstated Choice | Unstated Choice | Unstated Choice | 2 | 1/1 → 0/0 |

Google Play修订理由：盲标把numeric/alpha-2当作未规定的表示形式；复核发现输出来自lookup选值，同一numeric码有多个alpha-2候选，不能证明所有输出只是同一内容的另一种呈现。契约未定编码/映射策略，定稿按未定选择处理；扩行的唯一性前提另归Data。两种读法在规则问题保留，不能仅以036标签覆盖独立证据。

Google Play的Data点P是“lookup的country_code_numeric对源行最多匹配一条”。014 V2显示4个numeric码各有2行，V1显示250行/246个码；独立去重减少2400行。agent只看到了schema和一行样例，没有看到反证唯一性的统计，故“证据在场=否、曾经理解对过=否”。写出join并不等于意识到有别的做法，记第4档。

TikTok契约没有给出可执行email正则；本次差异是对连续点domain的接受边界，不把gold接受结果当作合法性证明。finish event63“可选邮箱/名称/手机号字段验证失败时置 NULL，记录仍保留。”只解释这一类处理，未交代该边界，记第2档。两张交付SQL均无注释。TikTok留存result.md与finish最后一句环境说明措辞不同，所引用的披露原句一致，采用finish原文。

排序严格先行数、再格子数；两张校准均非“只能组合修复”。复用核实查询Google Play采用V1/V2两条；把已读、与V2同SQL的V3也保守计入预算为3条。TikTok1条。没有新增数据库查询或重跑。

### 3. 原始数据有变化的各题怎么处理

以下直接事实来自逐题013与015 JSON；本阶段未重开数据库。013只查结构与行数；015包含排序内容hash，两者证据强度不混用。

| 题 | 013初始/agent不同raw表数 | 015 gold–initial不同 | 015 gold–agent不同 | 后续处理 |
|---|---:|---:|---:|---|
'''
for x in raw:
 s+=f"| {x['task']} | {x['013_summary']['different_tables']} | {x['015_comparison_summary']['gold_vs_initial'].get('different',0)} | {x['015_comparison_summary']['gold_vs_agent'].get('different',0)} | {'agent运行内改动，照常标注' if x['task'] in ['impl-015','impl-016'] else '无raw差异' if x['task']=='impl-018' else 'gold与agent一致，照常标注'} |\n"
s+='''
- **impl-015（已核实）**：event45改写run.py，理由为同一DuckDB文件重复ATTACH引发Unique file handle conflict。新路径通过已打开源连接的fetchdf/register复制raw。013发现30张类型/结构变化、行数未变；本批invoice_line_data、vendor_data直接涉及变化，payment_line_data未列为变化。类型变化与复制路线有关是解释，未逐列重演推断，不把每列因果称为已核实。CS general_ledger仍使用gold上游，不直接归因raw变化。
- **impl-016（已核实但步骤未找到）**：raw.person_contact_email_address从7284减到2448，少4836行（约66.4%）。复核013/015并搜索完整85事件的email、DELETE、TRUNCATE、DROP及run.py命令，未找到造成该减少的具体步骤与原因。run.py中存在建表/插入代码不是定位删除动作的证据。完整搜索索引见 `workday_raw_change_search.json`；正式说明继续如实写“未找到”。CS上游使用gold，不将4836直接当本张表的错误规模。
- **impl-017/019/020/021（已核实比较、因果解释分开）**：015显示这些题gold与agent raw一致，而gold与initial不同。按照用户指定，照常标注，staging使用agent留存raw。来自benchmark加载步骤的解释属于任务背景/推断，015本身没有gold生成执行轨迹，不能把比较结果冒充已溯源加载原因。
- **impl-018**：013/015未见raw差异。

每张表直接读取的raw已经从交付SQL提取并逐个对照013记录；结果在evidence_catalog的raw_direct_sources中。后续仍须逐张写入说明，特别区分staging直接raw与CS使用gold上游，不把“题目有raw变化”泛化成所有表不可评估。

### 4. 026相关条目的准备核对结果

**023-1 / Workday**：确认7284→2448，具体步骤仍未找到，未推测补全。已生成完整检索证据，正式4张表仍待逐点标注。

**Klaviyo campaign、flow、metric**：event19查询、event20输出分别为200/2、79/1、29/1（总行/非空ID），即ID空值198、78、28行；比例分别99.0%、98.7%、96.6%，不能把三张都精确称为99%。已读相应契约：各ID列明写not_null；agent过滤，gold没有该ID过滤。准备性判断为此过滤点“其他”，正式表其他点、主因排序尚待第二阶段。

“是否说出”需保留以下区别：

1. finish event41明确有“无效关键 ID 和非法邮件记录被排除”的**通用说明**，是第2档候选；列出了最终构建行数，但没有逐表说明丢失比例或大部分ID为空。没有把构建行数本身当第1档。
2. event21/22区分ID过滤和email正则，event23/24比较初始库的ID/大小写写法；event27/29修复email正则。它不只是数了一次行数，但不能把对邮件正则的意识自动推广到ID稀疏问题。正式阶段应单列对ID问题的过程意识判定；如果已符合第2档，最终五档不降为第3档。
3. 以上事实与待判边界存于 `fact_corrections.json`，未将准备性判断计作正式表标注完成。

### 5. 阶段一验证与第二阶段交接

`records/042_checks/validation.json`：`status=phase1_complete`、`task_complete=false`。校验39+2预期范围、7张精确排除、4/4/9/9/3/4/6分布、校准点键唯一、五档及已说出类别规则、040表头（仅最后列换为023旧标签）、023旧主因原样、引用回查、行/格排序与重跑原数值、query预算、保护hash和校准封存不变。

没有打开或写入数据库，没有运行agent，没有执行轨迹里的命令，没有下载数据。所有新增文件是042；notes仅放本Markdown报告。第二阶段交接见 `records/042_checks/phase1_handoff.json`，校准定稿文件hash和CSV前缀已保存。阶段二追加39正式表，并更新本报告为完整批次，最终再验证41张覆盖。

## 证据来源

- 范围：`records/013_statuses.csv`、`records/036_objects.csv`（开工仅投影对象编号）、`records/042_scope.json`。
- 冻结规则：`docs/标注手册_v3.2.md`；交付参考：`notes/040_2026-11-01_DAComp重标第四批.md`、`records/040_checks/`（封存后读取）。
- 校准：`records/014_queries_impl-009.json`、`records/016_reruns_impl-009.json`、`records/014_trace_impl-009.json`；`records/017_queries_impl-024.json`、`records/017_reruns_impl-024.json`、`records/017_trace_impl-024.json`。原始事件/SQL/契约路径与hash在逐表说明和quote_checks中。
- 正式材料：`records/023_packages/`、`records/023_*reruns*.json`、`records/023_queries.json`、`records/023_diagnostics.json`、`records/023_extra_diagnostics.json`。阶段一只是建立索引，不声称已逐项读完并定稿。
- raw：`records/013_raw_impl-015.json`～`013_raw_impl-021.json`、对应015逐题JSON；必读事实：`records/026_Claude全量标注检查台账.md`。
- 新增交付：`records/042_objects.csv`、`records/042_points.csv`、`records/042_annotations/`、两份校准JSON、`records/042_checks/`。

本阶段实际执行的主要可复核命令：

```text
python3 records/042_checks/seal_calibration.py
python3 records/042_checks/prepare_phase1.py
python3 records/042_checks/render_calibration.py
python3 records/042_checks/record_facts.py
python3 records/042_checks/validate_phase1.py
python3 records/042_checks/report_phase1.py
```

封存与解盲脚本带防覆盖断言，不能在第二阶段重复运行。最初尝试`python`发现命令不存在，随即改用python3；未导致源记录变化。

## 不确定或没查到的

- 39张正式表未逐点标注；阶段一完整性检查不等于最终全批验证。
- Google Play country的形式/选择边界有盲标分歧；本次解盲后定稿为Choice，保留理由与原判，不修改手册或036。
- email “standard pattern”未给可执行正则，若采用额外领域规则可能有“其他”的读法；未使用未经核实的领域约定。
- impl-016 raw email减少的步骤和原因仍未找到。
- 015证明数据比较结果，不直接证明gold加载历史；不得把加载因果推断写成已核实。

## 建议的下一步

在**同一会话**继续第二阶段的39张正式表。使用本次证据索引和交接清单，从v3.2重新判点；完成后追加CSV及逐表说明，更新同一042报告，验证39+2全范围，再commit并push main。不要重新占号、解盲或修改018～041和冻结手册。
'''
Path('notes/042_2026-11-01_DAComp重标第五批.md').write_text(s)
print('report written')
