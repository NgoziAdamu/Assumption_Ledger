# impl-008 / stg_asana__task（全量）

## 结论

主要原因：**O**；把握：高。agent按契约TIMESTAMP输出，gold两列为TIMESTAMPTZ；due源列取法另有歧义。

参与因素：A：due_source_choice（减584行/829格）；O：start_gold_type（减366行/887格）。标记：无。

## 差异与归因依据

契约due_date/start_date都明确TIMESTAMP，agent遵守，gold保留带时区解析值。due类型单项对照减少631行/907格，start类型减少366行/887格。due取due_at优先还是仅due_on未指定；单改源列减少584行/829格，L3整表一致，作为A参与因素。最初另一种格式解析假设被核实查询否定（0行），不能归U。

层：staging；实际schema：staging；评测键：task_id。已核实数字来自下列查询/重跑；类别是按v2规则的判断，不将gold选择自动作为业务事实。

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-008/docs/data_contract.yaml:117–151`；逐字原文见精简材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/staging/stg_asana__task.sql:1–8`，SHA-256 `ea60d0bb38b23b4c5e7043d46e7e3d8a9e3ac5aac702ea3ba578de4a08248bb9`。
- gold（仅定位/诊断） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/sql/staging/stg_asana__task.sql:1–33`，SHA-256 `082f8cffae199d4f2ac424851626a196789cc8158e37326844c0d2e0a9509e74`。

- due_date：agent SQL第2行起：
```sql
CAST(TRY_STRPTIME(due_on, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP)
```
替换为：
```sql
COALESCE(CAST(TRY_STRPTIME(due_on, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP),TRY_CAST(due_on AS TIMESTAMP))
```

- start_date：agent SQL第2行起：
```sql
CAST(TRY_STRPTIME(start_on, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP)
```
替换为：
```sql
COALESCE(CAST(TRY_STRPTIME(start_on, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP),TRY_CAST(start_on AS TIMESTAMP))
```

- due_source_choice：agent SQL第2行起：
```sql
COALESCE(CAST(TRY_STRPTIME(due_at, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP), CAST(TRY_STRPTIME(due_on, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP))
```
替换为：
```sql
CAST(TRY_STRPTIME(due_on, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP)
```

- due_gold_type：agent SQL第2行起：
```sql
COALESCE(CAST(TRY_STRPTIME(due_at, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP), CAST(TRY_STRPTIME(due_on, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP))
```
替换为：
```sql
COALESCE(TRY_STRPTIME(due_at, '%Y-%m-%d %H:%M:%S.%f %z'), TRY_STRPTIME(due_on, '%Y-%m-%d %H:%M:%S.%f %z'))
```

- start_gold_type：agent SQL第2行起：
```sql
CAST(TRY_STRPTIME(start_on, '%Y-%m-%d %H:%M:%S.%f %z') AS TIMESTAMP)
```
替换为：
```sql
TRY_STRPTIME(start_on, '%Y-%m-%d %H:%M:%S.%f %z')
```

## agent可见证据与不确定性

**只有通用策略说明**。

event53：原始数据 timestamp 格式不能直接 `TRY_CAST`，已依据观测到的 `YYYY-MM-DD HH:MM:SS.fff +0800` 格式采用 DuckDB `TRY_STRPTIME` 修复。未逐列说明due_at/due_on或目标类型差别。

最终报告原句（其适用范围按上文判定）：

> - 日期文本使用 `TRY_STRPTIME` 处理源数据中 `+0800` 时区格式，无法解析的可选日期会转为 NULL。

> - staging 中对必需键为空或严重无效的记录进行过滤；实体表对主键重复按键去重，关系表不额外去重。日期字段按可解析性进行清洗，任务 `modified_at` 的非日期污染行被排除。

> - 合同内部对 story 类型存在不一致：staging 允许的枚举不包含 `system`，但 task-story 逻辑要求 `story_type='system'` 才识别 assigned/completed 等系统动作。严格按 staging 合同清洗后，`system` 类型不能通过该枚举验证，故事动作因而归为 `other`，依赖系统动作的下游指标会受到影响；本实现未擅自扩充允许值。

扫描55个原始事件及最终result.md；完整可见输出命中位置、显式截断标记见 `records/021_trace_audit.json` index=7。所有原始事件均按id检查；代码在message中重复出现不当作解释理由，执行日志行数不当作已核实连接基数/字段语义。

| event | cause | 显式截断 |
|---|---|---|
| 8 | 7 | False |
| 12 | 11 | False |
| 14 | 13 | False |
| 28 | 27 | False |
| 30 | 29 | False |
| 38 | 37 | False |

## 原始数据一致性与查询

015的逐题原始数据核对提供背景；本次全部原件均只读，前后字节指纹另核对。impl-008/009/011/013的raw三侧一致。校准impl-030按agent留存raw，不能因initial与gold不同而一概不可评估。

核实查询条数（含失败尝试）：2；核实代价档：多条查询。每张不超过5条。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/asana.duckdb`；记录：`records/021_queries.json`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE due_on IS NOT NULL AND TRY_STRPTIME(due_on, '%Y-%m-%d %H:%M:%S.%f %z') IS NULL AND TRY_CAST(due_on AS TIMESTAMP) IS NOT NULL) due_on_parseable_other_format,count(*) FILTER(WHERE start_on IS NOT NULL AND TRY_STRPTIME(start_on, '%Y-%m-%d %H:%M:%S.%f %z') IS NULL AND TRY_CAST(start_on AS TIMESTAMP) IS NOT NULL) start_on_parseable_other_format FROM raw.task_data
```

结果（列顺序["n", "due_on_parseable_other_format", "start_on_parseable_other_format"]）：`[[3000, 0, 0]]`

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/asana.duckdb`；记录：`records/021_supplement_queries.json`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE due_on IS DISTINCT FROM due_at) due_choices_differ,count(*) FILTER(WHERE due_on IS NOT NULL) due_on_present,count(*) FILTER(WHERE due_at IS NOT NULL) due_at_present FROM raw.task_data
```

结果（列顺序["n", "due_choices_differ", "due_on_present", "due_at_present"]）：`[[3000, 1742, 910, 832]]`

诊断来源：`records/021_supplement_queries.json`；SQL：
```sql
SELECT typeof(min(due_date)),typeof(min(start_date)) FROM staging.stg_asana__task
```
结果：`[["TIMESTAMP WITH TIME ZONE", "TIMESTAMP WITH TIME ZONE"]]`。


## 固定时间与重跑

原始库只用read_only=True或READ_ONLY ATTACH；staging复制agent raw，其他层复制gold上游（CS）。所有写入在data/021_*私有副本。

留存结果同口径L0：2102行/2623格；选定基线：2102行/2623格。

共同固定时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。每组基线与单修使用完全相同的时间；跨组时间不同明确分列，不跨基线计算减少量。

| 实验 | L0–L3规模（包含键） | 整表首次匹配 |
|---|---|---|
| baseline | L0 2102行/2623格；L1 2102行/2623格；L2 2102行/2623格；L3 829行/829格 | 均未整表匹配 |
| due_date | L0 2102行/2623格；L1 2102行/2623格；L2 2102行/2623格；L3 829行/829格 | 均未整表匹配 |
| start_date | L0 2102行/2623格；L1 2102行/2623格；L2 2102行/2623格；L3 829行/829格 | 均未整表匹配 |
| due_source_choice | L0 1518行/1794格；L1 1518行/1794格；L2 1518行/1794格；L3 0行/0格 | L3 |
| due_gold_type | L0 1471行/1716格；L1 1471行/1716格；L2 1471行/1716格；L3 829行/829格 | 均未整表匹配 |
| start_gold_type | L0 1736行/1736格；L1 1736行/1736格；L2 1736行/1736格；L3 829行/829格 | 均未整表匹配 |

不适用：主因/并列项不是U；未将完整实现替换当作U局部修复。

| 实验 | L0每列非零不一致数 |
|---|---|
| baseline | {"due_date": 1736, "start_date": 887} |
| due_date | {"due_date": 1736, "start_date": 887} |
| start_date | {"due_date": 1736, "start_date": 887} |
| due_source_choice | {"due_date": 907, "start_date": 887} |
| due_gold_type | {"due_date": 829, "start_date": 887} |
| start_gold_type | {"due_date": 1736} |

L1–L3的每列不一致数、单侧行、共同键超额行及全部L0–L3字段已逐项保存在每个重跑JSON的`comparison.levels`，与本表同属交付证据；不是仅列总差异。

先按行数减少量，再按格子数；重复键先抵消相同行，剩余按整行字典序固定配对。大表使用权重区间配对，与展开重复行的原算法12组逐字段测试一致。整段gold实现及混合原因替换不冒充单点U证据；失败、无改善或行数变差的候选不计参与因素。


## 规则问题

无。

## 证据路径与复现

- 精简材料包：`records/021_packages/021_impl-008_stg_asana__task.md`。
- 完整机械材料（可由prepare脚本重建）：`data/021_packages_work/021_impl-008_stg_asana__task/021_impl-008_stg_asana__task.json`。
- 重跑：`records/021_reruns_impl-008_stg_asana__task.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 重跑：`records/021_supplement_reruns_impl-008_stg_asana__task.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 原始轨迹：`traces/dacomp_deimpl_prev.tar.gz`，事件定位见 `records/021_trace_audit.json`。
- 输入前指纹：`records/021_input_before.json`；后指纹与验证另见021记录。
- 执行环境：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`；调用本表重跑记录对应的021脚本，具体命令汇总见 `records/021_commands.txt`。
