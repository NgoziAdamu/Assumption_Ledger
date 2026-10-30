# impl-008 / asana__daily_metrics（全量）

## 结论

主要原因：**A**；把握：中。午夜键使用UTC或源数据+08时区，产生两侧各1个独有键。

参与因素：无经单修确认的其他参与因素。标记：无。

## 差异与归因依据

契约要求TIMESTAMP WITH TIME ZONE且是其时区午夜，未指定目标时区。agent将无时区日转为UTC午夜，gold保存+08午夜；两者都在各自时区为午夜。两条聚合分支统一改Asia/Singapore，2行/8格→0。三个计数值一致；不能把gold时区直接作为契约唯一选择。

层：marts；实际schema：mart；评测键：date_day。已核实数字来自下列查询/重跑；类别是按v2规则的判断，不将gold选择自动作为业务事实。

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-008/docs/data_contract.yaml:974–992`；逐字原文见精简材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__daily_metrics.sql:1–26`，SHA-256 `50c63fceadae16678066be2db07b734b1a976521f618de20908581930dfab83b`。
- gold（仅定位/诊断） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/sql/marts/asana__daily_metrics.sql:1–37`，SHA-256 `f64aa86ce8e7caba459e35afb30f2d1ef30b6face49cb2c6f81e89928b796bf9`。

- source_timezone_midnight：agent SQL第2行起：
```sql
CAST(CAST(created_at AS DATE) AS TIMESTAMP) AT TIME ZONE 'UTC'
```
替换为：
```sql
CAST(CAST(created_at AS DATE) AS TIMESTAMP) AT TIME ZONE 'Asia/Singapore'
```

- source_timezone_midnight：agent SQL第8行起：
```sql
CAST(CAST(completed_at AS DATE) AS TIMESTAMP) AT TIME ZONE 'UTC'
```
替换为：
```sql
CAST(CAST(completed_at AS DATE) AS TIMESTAMP) AT TIME ZONE 'Asia/Singapore'
```

## agent可见证据与不确定性

**只有通用策略说明**。

event35写UTC转换；event53：日期文本使用 `TRY_STRPTIME` 处理源数据中 `+0800` 时区格式，无法解析的可选日期会转为 NULL。该说明未指明日指标聚合时区。

最终报告原句（其适用范围按上文判定）：

> - 日期文本使用 `TRY_STRPTIME` 处理源数据中 `+0800` 时区格式，无法解析的可选日期会转为 NULL。

> - staging 中对必需键为空或严重无效的记录进行过滤；实体表对主键重复按键去重，关系表不额外去重。日期字段按可解析性进行清洗，任务 `modified_at` 的非日期污染行被排除。

> - 合同内部对 story 类型存在不一致：staging 允许的枚举不包含 `system`，但 task-story 逻辑要求 `story_type='system'` 才识别 assigned/completed 等系统动作。严格按 staging 合同清洗后，`system` 类型不能通过该枚举验证，故事动作因而归为 `other`，依赖系统动作的下游指标会受到影响；本实现未擅自扩充允许值。

扫描55个原始事件及最终result.md；完整可见输出命中位置、显式截断标记见 `records/021_trace_audit.json` index=2。所有原始事件均按id检查；代码在message中重复出现不当作解释理由，执行日志行数不当作已核实连接基数/字段语义。

| event | cause | 显式截断 |
|---|---|---|
| 8 | 7 | False |
| 14 | 13 | False |
| 28 | 27 | False |
| 34 | 33 | False |
| 38 | 37 | False |

## 原始数据一致性与查询

015的逐题原始数据核对提供背景；本次全部原件均只读，前后字节指纹另核对。impl-008/009/011/013的raw三侧一致。校准impl-030按agent留存raw，不能因initial与gold不同而一概不可评估。

核实查询条数（含失败尝试）：1；核实代价档：需要查业务说明。每张不超过5条。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/asana.duckdb`；记录：`records/021_queries.json`。

```sql
SELECT typeof(min(created_at)) created_type,typeof(min(completed_at)) completed_type,min(created_at)::varchar first_created,max(created_at)::varchar last_created FROM staging.stg_asana__task
```

结果（列顺序["created_type", "completed_type", "first_created", "last_created"]）：`[["TIMESTAMP", "TIMESTAMP", "2025-09-05 18:26:45.051", "2025-09-05 18:32:44.945"]]`

诊断来源：`records/021_supplement_queries.json`；SQL：
```sql
SELECT typeof(date_day),min(date_day)::varchar,max(date_day)::varchar FROM mart.asana__daily_metrics GROUP BY ALL
```
结果：`[["TIMESTAMP WITH TIME ZONE", "2025-09-04 16:00:00+00", "2025-09-04 16:00:00+00"]]`。


## 固定时间与重跑

原始库只用read_only=True或READ_ONLY ATTACH；staging复制agent raw，其他层复制gold上游（CS）。所有写入在data/021_*私有副本。

留存结果同口径L0：2行/8格；选定基线：2行/8格。

共同固定时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。每组基线与单修使用完全相同的时间；跨组时间不同明确分列，不跨基线计算减少量。

| 实验 | L0–L3规模（包含键） | 整表首次匹配 |
|---|---|---|
| baseline | L0 2行/8格；L1 2行/8格；L2 2行/8格；L3 2行/8格 | 均未整表匹配 |
| calendar_day_type | 执行失败 | Binder Error: column "created_at" must appear in the GROUP BY clause or must be part of an aggregate function.<br>Either add it to the GROUP BY list, or use "ANY_VALUE(created_at)" if the exact value of "created_at" is not important.<br><br>LINE 2:     SELECT date_trunc('day',created_at) AS date_day,<br>                                    ^ |
| source_timezone_midnight | L0 0行/0格；L1 0行/0格；L2 0行/0格；L3 0行/0格 | L0 |

不适用：主因/并列项不是U；未将完整实现替换当作U局部修复。

| 实验 | L0每列非零不一致数 |
|---|---|
| baseline | {} |
| source_timezone_midnight | {} |

L1–L3的每列不一致数、单侧行、共同键超额行及全部L0–L3字段已逐项保存在每个重跑JSON的`comparison.levels`，与本表同属交付证据；不是仅列总差异。

先按行数减少量，再按格子数；重复键先抵消相同行，剩余按整行字典序固定配对。大表使用权重区间配对，与展开重复行的原算法12组逐字段测试一致。整段gold实现及混合原因替换不冒充单点U证据；失败、无改善或行数变差的候选不计参与因素。


## 规则问题

契约说“其时区午夜”但未指定时区。按A记录UTC/+08选择；不能因gold键不同便定义UTC午夜违法。

## 证据路径与复现

- 精简材料包：`records/021_packages/021_impl-008_asana__daily_metrics.md`。
- 完整机械材料（可由prepare脚本重建）：`data/021_packages_work/021_impl-008_asana__daily_metrics/021_impl-008_asana__daily_metrics.json`。
- 重跑：`records/021_reruns_impl-008_asana__daily_metrics.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 重跑：`records/021_supplement_reruns_impl-008_asana__daily_metrics.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 原始轨迹：`traces/dacomp_deimpl_prev.tar.gz`，事件定位见 `records/021_trace_audit.json`。
- 输入前指纹：`records/021_input_before.json`；后指纹与验证另见021记录。
- 执行环境：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`；调用本表重跑记录对应的021脚本，具体命令汇总见 `records/021_commands.txt`。
