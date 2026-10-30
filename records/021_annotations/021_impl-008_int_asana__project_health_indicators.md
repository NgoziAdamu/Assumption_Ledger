# impl-008 / int_asana__project_health_indicators（全量）

## 结论

主要原因：**C**；把握：中。分母为0时没有在验证前置0，丢掉23个项目；另把悬空关系键计入任务数。

参与因素：U：count_joined_tasks（减20行/132格）。标记：无。

## 差异与归因依据

契约明确百分比分母0时置0。agent先NULLIF生成NULL，再用BETWEEN验证过滤，最终SELECT的COALESCE太晚。独立修复减少23行；从pt.task_id改为t.task_id减少20行，作为U参与因素。P为project_task的task_id均能匹配有效task；agent可见留存数据核实20个悬空链接。轨迹无连接覆盖率核实。

层：intermediate；实际schema：intermediate；评测键：project_id。已核实数字来自下列查询/重跑；类别是按v2规则的判断，不将gold选择自动作为业务事实。

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-008/docs/data_contract.yaml:295–445`；逐字原文见精简材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/intermediate/int_asana__project_health_indicators.sql:1–57`，SHA-256 `ffa172c3308a69b841e9d68348fd4c6b1cdf5323bd3e738667dadb34f8ea2879`。
- gold（仅定位/诊断） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/sql/intermediate/int_asana__project_health_indicators.sql:1–280`，SHA-256 `83b07e678766aa2683c2f8f13c1c776dde2a08984a0d0a1c53d31922f1da0332`。

- count_joined_tasks：agent SQL第5行起：
```sql
pt.task_id,t.is_completed
```
替换为：
```sql
t.task_id,t.is_completed
```

- zero_denominator_policy：agent SQL第28行起：
```sql
SELECT *,ROUND(100.0*completed_tasks/NULLIF(total_tasks,0),2) completion_percentage,ROUND(100.0*assigned_tasks/NULLIF(total_tasks,0),2) assignment_percentage,
 ROUND(100.0*overdue_tasks/NULLIF(total_tasks,0),2) overdue_percentage,ROUND(100.0*quality_tasks/NULLIF(completed_tasks,0),2) quality_percentage,
 ROUND(100.0*(overdue_tasks+poor_performance_tasks+delayed_tasks)/NULLIF(total_tasks,0),2) risk_percentage,
 ROUND(100.0*(recent_task_creation+recent_task_completion)/NULLIF(total_tasks,0),2) activity_percentage,
 
```
替换为：
```sql
SELECT *,COALESCE(ROUND(100.0*completed_tasks/NULLIF(total_tasks,0),2),0) completion_percentage,COALESCE(ROUND(100.0*assigned_tasks/NULLIF(total_tasks,0),2),0) assignment_percentage,
 COALESCE(ROUND(100.0*overdue_tasks/NULLIF(total_tasks,0),2),0) overdue_percentage,COALESCE(ROUND(100.0*quality_tasks/NULLIF(completed_tasks,0),2),0) quality_percentage,
 COALESCE(ROUND(100.0*(overdue_tasks+poor_performance_tasks+delayed_tasks)/NULLIF(total_tasks,0),2),0) risk_percentage,
 COALESCE(ROUND(100.0*(recent_task_creation+recent_task_completion)/NULLIF(total_tasks,0),2),0) activity_percentage,
 
```

## agent可见证据与不确定性

**看到了但没提**。

event37→38已显示project=495而health=472行；event13→14显示任务/项目结构；event17生成相关计数和NULLIF，event53未说明零分母/悬空链接。

扫描55个原始事件及最终result.md；完整可见输出命中位置、显式截断标记见 `records/021_trace_audit.json` index=0。所有原始事件均按id检查；代码在message中重复出现不当作解释理由，执行日志行数不当作已核实连接基数/字段语义。

| event | cause | 显式截断 |
|---|---|---|
| 8 | 7 | False |
| 28 | 27 | False |
| 38 | 37 | False |

## 原始数据一致性与查询

015的逐题原始数据核对提供背景；本次全部原件均只读，前后字节指纹另核对。impl-008/009/011/013的raw三侧一致。校准impl-030按agent留存raw，不能因initial与gold不同而一概不可评估。

核实查询条数（含失败尝试）：1；核实代价档：一条查询。每张不超过5条。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/asana.duckdb`；记录：`records/021_queries.json`。

```sql
SELECT count(*) links, count(*) FILTER(WHERE t.task_id IS NULL) dangling_links FROM staging.stg_asana__project_task pt LEFT JOIN staging.stg_asana__task t ON pt.task_id::VARCHAR=t.task_id
```

结果（列顺序["links", "dangling_links"]）：`[[3995, 20]]`


## 固定时间与重跑

原始库只用read_only=True或READ_ONLY ATTACH；staging复制agent raw，其他层复制gold上游（CS）。所有写入在data/021_*私有副本。

留存结果同口径L0：43行/1190格；选定基线：43行/1190格。

共同固定时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 6}]`。每组基线与单修使用完全相同的时间；跨组时间不同明确分列，不跨基线计算减少量。

| 实验 | L0–L3规模（包含键） | 整表首次匹配 |
|---|---|---|
| baseline | L0 43行/1190格；L1 43行/1190格；L2 43行/1190格；L3 43行/1190格 | 均未整表匹配 |
| count_joined_tasks | L0 23行/1058格；L1 23行/1058格；L2 23行/1058格；L3 23行/1058格 | 均未整表匹配 |
| zero_denominator_policy | L0 20行/132格；L1 20行/132格；L2 20行/132格；L3 20行/132格 | 均未整表匹配 |

U仅作为参与因素：20个悬空链接的P被查询否定；只改计数键减少20行/132格，不满足独立主因半数门槛，但满足参与因素要求。

| 实验 | L0每列非零不一致数 |
|---|---|
| baseline | {"anomaly_flag": 3, "assignment_percentage": 20, "completion_percentage": 20, "focus_areas": 7, "health_grade": 5, "overall_health_score": 17, "progress_score": 8, "project_forecast": 2, "resource_score": 12, "risk_level": 1, "risk_percentage": 13, "risk_score": 4, "total_tasks": 20} |
| count_joined_tasks | {} |
| zero_denominator_policy | {"anomaly_flag": 3, "assignment_percentage": 20, "completion_percentage": 20, "focus_areas": 7, "health_grade": 5, "overall_health_score": 17, "progress_score": 8, "project_forecast": 2, "resource_score": 12, "risk_level": 1, "risk_percentage": 13, "risk_score": 4, "total_tasks": 20} |

L1–L3的每列不一致数、单侧行、共同键超额行及全部L0–L3字段已逐项保存在每个重跑JSON的`comparison.levels`，与本表同属交付证据；不是仅列总差异。

先按行数减少量，再按格子数；重复键先抵消相同行，剩余按整行字典序固定配对。大表使用权重区间配对，与展开重复行的原算法12组逐字段测试一致。整段gold实现及混合原因替换不冒充单点U证据；失败、无改善或行数变差的候选不计参与因素。


## 规则问题

task计数有“all linked tasks”的文字，但同段要求链接到有效task后计数。本次以悬空关联P归U参与因素；也可读为取哪侧键的A。查询只证明20个链接无法匹配，不把gold选t.task_id本身作为P证据。

## 证据路径与复现

- 精简材料包：`records/021_packages/021_impl-008_int_asana__project_health_indicators.md`。
- 完整机械材料（可由prepare脚本重建）：`data/021_packages_work/021_impl-008_int_asana__project_health_indicators/021_impl-008_int_asana__project_health_indicators.json`。
- 重跑：`records/021_reruns_impl-008_int_asana__project_health_indicators.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 原始轨迹：`traces/dacomp_deimpl_prev.tar.gz`，事件定位见 `records/021_trace_audit.json`。
- 输入前指纹：`records/021_input_before.json`；后指纹与验证另见021记录。
- 执行环境：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`；调用本表重跑记录对应的021脚本，具体命令汇总见 `records/021_commands.txt`。
