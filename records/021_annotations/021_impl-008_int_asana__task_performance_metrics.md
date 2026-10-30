# impl-008 / int_asana__task_performance_metrics（全量）

## 结论

主要原因：**C**；把握：高。完成状态比较把完整时间戳截为日期，91行分类不同。

参与因素：无经单修确认的其他参与因素。标记：无。

## 差异与归因依据

契约completed_on_time/late使用completed_at与due_date的先后关系，仅overdue说明按日比较；agent两项都::DATE。独立恢复时间戳比较，91行/91格→0，L0整表一致。

层：intermediate；实际schema：intermediate；评测键：task_id。已核实数字来自下列查询/重跑；类别是按v2规则的判断，不将gold选择自动作为业务事实。

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-008/docs/data_contract.yaml:688–774`；逐字原文见精简材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/intermediate/int_asana__task_performance_metrics.sql:1–32`，SHA-256 `91df3c8e5530cf06cd6a1a3934963ff5911ea1b506bfeb58d8ce4a2659021c6a`。
- gold（仅定位/诊断） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/sql/intermediate/int_asana__task_performance_metrics.sql:1–157`，SHA-256 `dbe6604557ca9ec7dfaea10a2961d756fdb0ed6ca3ce1fa3ddee9f9b410aa4c2`。

- timestamp_status：agent SQL第11行起：
```sql
WHEN is_completed AND completed_at::DATE <= due_date::DATE THEN 'completed_on_time'
 WHEN is_completed AND completed_at::DATE > due_date::DATE THEN 'completed_late'
```
替换为：
```sql
WHEN is_completed AND completed_at <= due_date THEN 'completed_on_time'
 WHEN is_completed AND completed_at > due_date THEN 'completed_late'
```

## agent可见证据与不确定性

**看到了但没提**。

event11→12及13→14显示completed_at、due_on、due_at等日期列；event29→30显示源日期样例；event53只说明一般解析策略，没有说明本表状态比较截日。

扫描55个原始事件及最终result.md；完整可见输出命中位置、显式截断标记见 `records/021_trace_audit.json` index=1。所有原始事件均按id检查；代码在message中重复出现不当作解释理由，执行日志行数不当作已核实连接基数/字段语义。

| event | cause | 显式截断 |
|---|---|---|
| 8 | 7 | False |
| 28 | 27 | False |
| 38 | 37 | False |

## 原始数据一致性与查询

015的逐题原始数据核对提供背景；本次全部原件均只读，前后字节指纹另核对。impl-008/009/011/013的raw三侧一致。校准impl-030按agent留存raw，不能因initial与gold不同而一概不可评估。

核实查询条数（含失败尝试）：2；核实代价档：多条查询。每张不超过5条。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/asana.duckdb`；记录：`records/021_queries.json`。

```sql
SELECT 'intermediate.int_asana__task_open_length' source,count(*) n FROM intermediate.int_asana__task_open_length UNION ALL SELECT 'intermediate.int_asana__task_story' source,count(*) n FROM intermediate.int_asana__task_story UNION ALL SELECT 'staging.stg_asana__task' source,count(*) n FROM staging.stg_asana__task
```

失败：Parser Error: syntax error at or near "source"

LINE 1: SELECT 'intermediate.int_asana__task_open_length' source,count(*) n FROM intermediate.int_asana__task_open_le...
                                                          ^

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/asana.duckdb`；记录：`records/021_supplement_queries.json`。

```sql
SELECT 'intermediate.int_asana__task_open_length' source_name,count(*) n FROM intermediate.int_asana__task_open_length UNION ALL SELECT 'intermediate.int_asana__task_story' source_name,count(*) n FROM intermediate.int_asana__task_story UNION ALL SELECT 'staging.stg_asana__task' source_name,count(*) n FROM staging.stg_asana__task
```

结果（列顺序["source_name", "n"]）：`[["intermediate.int_asana__task_open_length", 2986], ["intermediate.int_asana__task_story", 4974], ["staging.stg_asana__task", 2986]]`


## 固定时间与重跑

原始库只用read_only=True或READ_ONLY ATTACH；staging复制agent raw，其他层复制gold上游（CS）。所有写入在data/021_*私有副本。

留存结果同口径L0：91行/91格；选定基线：91行/91格。

共同固定时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 4}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 7}]`。每组基线与单修使用完全相同的时间；跨组时间不同明确分列，不跨基线计算减少量。

| 实验 | L0–L3规模（包含键） | 整表首次匹配 |
|---|---|---|
| baseline | L0 91行/91格；L1 91行/91格；L2 91行/91格；L3 91行/91格 | 均未整表匹配 |
| timestamp_status | L0 0行/0格；L1 0行/0格；L2 0行/0格；L3 0行/0格 | L0 |

不适用：主因/并列项不是U；未将完整实现替换当作U局部修复。

| 实验 | L0每列非零不一致数 |
|---|---|
| baseline | {"task_status_category": 91} |
| timestamp_status | {} |

L1–L3的每列不一致数、单侧行、共同键超额行及全部L0–L3字段已逐项保存在每个重跑JSON的`comparison.levels`，与本表同属交付证据；不是仅列总差异。

先按行数减少量，再按格子数；重复键先抵消相同行，剩余按整行字典序固定配对。大表使用权重区间配对，与展开重复行的原算法12组逐字段测试一致。整段gold实现及混合原因替换不冒充单点U证据；失败、无改善或行数变差的候选不计参与因素。


## 规则问题

无。

## 证据路径与复现

- 精简材料包：`records/021_packages/021_impl-008_int_asana__task_performance_metrics.md`。
- 完整机械材料（可由prepare脚本重建）：`data/021_packages_work/021_impl-008_int_asana__task_performance_metrics/021_impl-008_int_asana__task_performance_metrics.json`。
- 重跑：`records/021_reruns_impl-008_int_asana__task_performance_metrics.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 原始轨迹：`traces/dacomp_deimpl_prev.tar.gz`，事件定位见 `records/021_trace_audit.json`。
- 输入前指纹：`records/021_input_before.json`；后指纹与验证另见021记录。
- 执行环境：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`；调用本表重跑记录对应的021脚本，具体命令汇总见 `records/021_commands.txt`。
