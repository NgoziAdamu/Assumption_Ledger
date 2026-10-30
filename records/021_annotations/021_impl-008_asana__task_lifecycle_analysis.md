# impl-008 / asana__task_lifecycle_analysis（全量）

## 结论

主要原因：**A**；把握：中。无story时补0或保持NULL的选择影响活动率及派生标签。

参与因素：A：unique_action_types（减0行/722格）；A：days_with_activity（减0行/722格）；C：modification_source（减0行/338格）。标记：无。

## 差异与归因依据

先用gold诊断推回运行小时2025-10-12 09:00 UTC，基线及所有单修用同一时刻。缺失story的计数/活动率NULL政策未明确；agent补0，gold保留NULL。活动率NULL政策改动同步使验证接受NULL（同一缺失值政策），减少1148格，为主因A。unique_action_types、days_with_activity各减少722格；修改时间应取最新story而非task.modified_at为C参与因素，减少338格。

层：marts；实际schema：mart；评测键：task_id, assignee_user_id, parent_task_id, team_id。已核实数字来自下列查询/重跑；类别是按v2规则的判断，不将gold选择自动作为业务事实。

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-008/docs/data_contract.yaml:1382–1523`；逐字原文见精简材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__task_lifecycle_analysis.sql:1–20`，SHA-256 `115d619f2c2289942217104e31a419195aff722667530f48a205e51f7b569567`。
- gold（仅定位/诊断） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/sql/marts/asana__task_lifecycle_analysis.sql:1–335`，SHA-256 `402db1c810446a9f3ce61b3663d6aef5592a3d39b954befd8e1193e44e58befc`。

- unique_action_types：agent SQL第2行起：
```sql
COALESCE(s.unique_action_types,0)
```
替换为：
```sql
s.unique_action_types
```

- days_with_activity：agent SQL第2行起：
```sql
COALESCE(s.days_with_activity,0)
```
替换为：
```sql
s.days_with_activity
```

- missing_activity_null_policy：agent SQL第4行起：
```sql
ROUND(COALESCE(s.total_story_events,0)::DOUBLE/DATE_DIFF('day',t.created_at,COALESCE(t.completed_at,TIMESTAMPTZ '2025-10-12 09:00:00+00')),2) ELSE COALESCE(s.total_story_events,0)::DOUBLE
```
替换为：
```sql
ROUND(s.total_story_events::DOUBLE/DATE_DIFF('day',t.created_at,COALESCE(t.completed_at,TIMESTAMPTZ '2025-10-12 09:00:00+00')),2) ELSE s.total_story_events::DOUBLE
```

- missing_activity_null_policy：agent SQL第17行起：
```sql
AND avg_daily_activity_rate>=0 AND
```
替换为：
```sql
AND (avg_daily_activity_rate IS NULL OR avg_daily_activity_rate>=0) AND
```

- modification_source：agent SQL第9行起：
```sql
modified_at>=TIMESTAMPTZ '2025-10-12 09:00:00+00'-INTERVAL '7 day' THEN 'active_development' WHEN NOT is_completed AND assignee_user_id IS NOT NULL THEN 'stagnant'
```
替换为：
```sql
DATE_DIFF('day',last_modification_timestamp,TIMESTAMPTZ '2025-10-12 09:00:00+00')<=7 THEN 'active_development' WHEN NOT is_completed AND assignee_user_id IS NOT NULL AND DATE_DIFF('day',last_modification_timestamp,TIMESTAMPTZ '2025-10-12 09:00:00+00')>7 THEN 'stagnant'
```

- gold_sql_same_clock：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_supplement_reruns_impl-008_asana__task_lifecycle_analysis.json`。

## agent可见证据与不确定性

**只有通用策略说明**。

event53讨论系统story被枚举清洗及下游影响，并说明一般日期策略；没有针对本表无story的0/NULL取法。event28/38显示story及目标表行数。

最终报告原句（其适用范围按上文判定）：

> - 日期文本使用 `TRY_STRPTIME` 处理源数据中 `+0800` 时区格式，无法解析的可选日期会转为 NULL。

> - staging 中对必需键为空或严重无效的记录进行过滤；实体表对主键重复按键去重，关系表不额外去重。日期字段按可解析性进行清洗，任务 `modified_at` 的非日期污染行被排除。

> - 合同内部对 story 类型存在不一致：staging 允许的枚举不包含 `system`，但 task-story 逻辑要求 `story_type='system'` 才识别 assigned/completed 等系统动作。严格按 staging 合同清洗后，`system` 类型不能通过该枚举验证，故事动作因而归为 `other`，依赖系统动作的下游指标会受到影响；本实现未擅自扩充允许值。

扫描55个原始事件及最终result.md；完整可见输出命中位置、显式截断标记见 `records/021_trace_audit.json` index=4。所有原始事件均按id检查；代码在message中重复出现不当作解释理由，执行日志行数不当作已核实连接基数/字段语义。

| event | cause | 显式截断 |
|---|---|---|
| 8 | 7 | False |
| 28 | 27 | False |
| 38 | 37 | False |

## 原始数据一致性与查询

015的逐题原始数据核对提供背景；本次全部原件均只读，前后字节指纹另核对。impl-008/009/011/013的raw三侧一致。校准impl-030按agent留存raw，不能因initial与gold不同而一概不可评估。

核实查询条数（含失败尝试）：2；核实代价档：需要查业务说明。每张不超过5条。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/asana.duckdb`；记录：`records/021_queries.json`。

```sql
SELECT 'intermediate.int_asana__project_health_indicators' source,count(*) n FROM intermediate.int_asana__project_health_indicators UNION ALL SELECT 'intermediate.int_asana__task_performance_metrics' source,count(*) n FROM intermediate.int_asana__task_performance_metrics UNION ALL SELECT 'intermediate.int_asana__task_story' source,count(*) n FROM intermediate.int_asana__task_story UNION ALL SELECT 'staging.stg_asana__project' source,count(*) n FROM staging.stg_asana__project UNION ALL SELECT 'staging.stg_asana__project_task' source,count(*) n FROM staging.stg_asana__project_task UNION ALL SELECT 'staging.stg_asana__task' source,count(*) n FROM staging.stg_asana__task UNION ALL SELECT 'staging.stg_asana__user' source,count(*) n FROM staging.stg_asana__user
```

失败：Parser Error: syntax error at or near "source"

LINE 1: SELECT 'intermediate.int_asana__project_health_indicators' source,count(*) n FROM intermediate.int_asana__project_heal...
                                                                   ^

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/asana.duckdb`；记录：`records/021_supplement_queries.json`。

```sql
SELECT 'intermediate.int_asana__project_health_indicators' source_name,count(*) n FROM intermediate.int_asana__project_health_indicators UNION ALL SELECT 'intermediate.int_asana__task_performance_metrics' source_name,count(*) n FROM intermediate.int_asana__task_performance_metrics UNION ALL SELECT 'intermediate.int_asana__task_story' source_name,count(*) n FROM intermediate.int_asana__task_story UNION ALL SELECT 'staging.stg_asana__project' source_name,count(*) n FROM staging.stg_asana__project UNION ALL SELECT 'staging.stg_asana__project_task' source_name,count(*) n FROM staging.stg_asana__project_task UNION ALL SELECT 'staging.stg_asana__task' source_name,count(*) n FROM staging.stg_asana__task UNION ALL SELECT 'staging.stg_asana__user' source_name,count(*) n FROM staging.stg_asana__user
```

结果（列顺序["source_name", "n"]）：`[["intermediate.int_asana__project_health_indicators", 472], ["intermediate.int_asana__task_performance_metrics", 2986], ["intermediate.int_asana__task_story", 4974], ["staging.stg_asana__project", 495], ["staging.stg_asana__project_task", 3995], ["staging.stg_asana__task", 2986], ["staging.stg_asana__user", 990]]`

诊断来源：`records/021_supplement_queries.json`；SQL：
```sql
SELECT min(date_trunc('hour',t.created_at)+g.total_lifecycle_hours*interval '1 hour')::varchar inferred_hour_min,max(date_trunc('hour',t.created_at)+g.total_lifecycle_hours*interval '1 hour')::varchar inferred_hour_max FROM mart.asana__task_lifecycle_analysis g JOIN staging.stg_asana__task t ON g.task_id=t.task_id WHERE t.completed_at IS NULL
```
结果：`[["2025-10-12 09:00:00+00", "2025-10-12 09:00:00+00"]]`。


## 固定时间与重跑

原始库只用read_only=True或READ_ONLY ATTACH；staging复制agent raw，其他层复制gold上游（CS）。所有写入在data/021_*私有副本。

留存结果同口径L0：2727行/8240格；选定基线：722行/3356格。

共同固定时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 09:00:00+00'", "count": 5}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 2}]`。每组基线与单修使用完全相同的时间；跨组时间不同明确分列，不跨基线计算减少量。

| 实验 | L0–L3规模（包含键） | 整表首次匹配 |
|---|---|---|
| baseline | L0 722行/3356格；L1 722行/3356格；L2 722行/3356格；L3 722行/3356格 | 均未整表匹配 |
| unique_action_types | L0 722行/2634格；L1 722行/2634格；L2 722行/2634格；L3 722行/2634格 | 均未整表匹配 |
| days_with_activity | L0 722行/2634格；L1 722行/2634格；L2 722行/2634格；L3 722行/2634格 | 均未整表匹配 |
| missing_activity_null_policy | L0 722行/2208格；L1 722行/2208格；L2 722行/2208格；L3 722行/2208格 | 均未整表匹配 |
| modification_source | L0 722行/3018格；L1 722行/3018格；L2 722行/3018格；L3 722行/3018格 | 均未整表匹配 |
| gold_sql_same_clock | L0 0行/0格；L1 0行/0格；L2 0行/0格；L3 0行/0格 | L0 |

不适用：主因/并列项不是U；未将完整实现替换当作U局部修复。

| 实验 | L0每列非零不一致数 |
|---|---|
| baseline | {"anomaly_patterns": 426, "avg_daily_activity_rate": 722, "current_lifecycle_stage": 338, "days_with_activity": 722, "improvement_opportunities": 426, "unique_action_types": 722} |
| unique_action_types | {"anomaly_patterns": 426, "avg_daily_activity_rate": 722, "current_lifecycle_stage": 338, "days_with_activity": 722, "improvement_opportunities": 426} |
| days_with_activity | {"anomaly_patterns": 426, "avg_daily_activity_rate": 722, "current_lifecycle_stage": 338, "improvement_opportunities": 426, "unique_action_types": 722} |
| missing_activity_null_policy | {"current_lifecycle_stage": 338, "days_with_activity": 722, "improvement_opportunities": 426, "unique_action_types": 722} |
| modification_source | {"anomaly_patterns": 426, "avg_daily_activity_rate": 722, "days_with_activity": 722, "improvement_opportunities": 426, "unique_action_types": 722} |
| gold_sql_same_clock | {} |

L1–L3的每列不一致数、单侧行、共同键超额行及全部L0–L3字段已逐项保存在每个重跑JSON的`comparison.levels`，与本表同属交付证据；不是仅列总差异。

先按行数减少量，再按格子数；重复键先抵消相同行，剩余按整行字典序固定配对。大表使用权重区间配对，与展开重复行的原算法12组逐字段测试一致。整段gold实现及混合原因替换不冒充单点U证据；失败、无改善或行数变差的候选不计参与因素。


## 规则问题

无story的NULL与0政策未明示。活动率改为NULL必须同时让验证接受NULL，否则会人工删除722行；这两处作为同一个缺失值政策干预，其他字节不改。初始午夜基线与09时基线分开列出，主因只用后者。

## 证据路径与复现

- 精简材料包：`records/021_packages/021_impl-008_asana__task_lifecycle_analysis.md`。
- 完整机械材料（可由prepare脚本重建）：`data/021_packages_work/021_impl-008_asana__task_lifecycle_analysis/021_impl-008_asana__task_lifecycle_analysis.json`。
- 重跑：`records/021_reruns_impl-008_asana__task_lifecycle_analysis.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 重跑：`records/021_supplement_reruns_impl-008_asana__task_lifecycle_analysis.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 原始轨迹：`traces/dacomp_deimpl_prev.tar.gz`，事件定位见 `records/021_trace_audit.json`。
- 输入前指纹：`records/021_input_before.json`；后指纹与验证另见021记录。
- 执行环境：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`；调用本表重跑记录对应的021脚本，具体命令汇总见 `records/021_commands.txt`。
