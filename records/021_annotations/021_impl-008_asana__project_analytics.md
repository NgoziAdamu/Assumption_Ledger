# impl-008 / asana__project_analytics（全量）

## 结论

主要原因：**C**；把握：高。时间管理评分没按schedule_forecast映射，472个综合得分不同。

参与因素：无经单修确认的其他参与因素。标记：无。

## 差异与归因依据

契约明确on_schedule/slight_delay/moderate_delay/significant_delay/overdue分别25/20/15/10/5，否则12。agent按完成率100和remaining_days判断。只替换这一CASE，472行/格→0，L0一致。

层：marts；实际schema：mart；评测键：project_id, team_id。已核实数字来自下列查询/重跑；类别是按v2规则的判断，不将gold选择自动作为业务事实。

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-008/docs/data_contract.yaml:1071–1214`；逐字原文见精简材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__project_analytics.sql:1–33`，SHA-256 `a2adacb9678a6ece4f6d52d650233bebfcddaaaa95eebf2442d3d76e98ec81cb`。
- gold（仅定位/诊断） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/sql/marts/asana__project_analytics.sql:1–282`，SHA-256 `6389f6a1fc05ef146020642871d47a62dc15d763b3e27731cbcbee8fc5b18fc7`。

- time_management：agent SQL第17行起：
```sql
CASE WHEN completion_percentage=100 THEN 25 WHEN remaining_days<0 THEN 5 ELSE 12 END time_management_score
```
替换为：
```sql
CASE schedule_forecast WHEN 'on_schedule' THEN 25 WHEN 'slight_delay' THEN 20 WHEN 'moderate_delay' THEN 15 WHEN 'significant_delay' THEN 10 WHEN 'overdue' THEN 5 ELSE 12 END time_management_score
```

## agent可见证据与不确定性

**没有迹象**。

检查全部55个事件与result.md；event25生成该CASE，event38只有建表行数。未找到针对schedule_forecast评分映射的可见数据查询、理由或不确定性说明；生成代码本身不算披露。

扫描55个原始事件及最终result.md；完整可见输出命中位置、显式截断标记见 `records/021_trace_audit.json` index=3。所有原始事件均按id检查；代码在message中重复出现不当作解释理由，执行日志行数不当作已核实连接基数/字段语义。

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
SELECT 'intermediate.int_asana__project_health_indicators' source,count(*) n FROM intermediate.int_asana__project_health_indicators UNION ALL SELECT 'staging.stg_asana__project' source,count(*) n FROM staging.stg_asana__project UNION ALL SELECT 'staging.stg_asana__team' source,count(*) n FROM staging.stg_asana__team
```

失败：Parser Error: syntax error at or near "source"

LINE 1: SELECT 'intermediate.int_asana__project_health_indicators' source,count(*) n FROM intermediate.int_asana__project_heal...
                                                                   ^

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/asana.duckdb`；记录：`records/021_supplement_queries.json`。

```sql
SELECT 'intermediate.int_asana__project_health_indicators' source_name,count(*) n FROM intermediate.int_asana__project_health_indicators UNION ALL SELECT 'staging.stg_asana__project' source_name,count(*) n FROM staging.stg_asana__project UNION ALL SELECT 'staging.stg_asana__team' source_name,count(*) n FROM staging.stg_asana__team
```

结果（列顺序["source_name", "n"]）：`[["intermediate.int_asana__project_health_indicators", 472], ["staging.stg_asana__project", 495], ["staging.stg_asana__team", 44]]`


## 固定时间与重跑

原始库只用read_only=True或READ_ONLY ATTACH；staging复制agent raw，其他层复制gold上游（CS）。所有写入在data/021_*私有副本。

留存结果同口径L0：472行/472格；选定基线：472行/472格。

共同固定时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 2}]`。每组基线与单修使用完全相同的时间；跨组时间不同明确分列，不跨基线计算减少量。

| 实验 | L0–L3规模（包含键） | 整表首次匹配 |
|---|---|---|
| baseline | L0 472行/472格；L1 472行/472格；L2 472行/472格；L3 472行/472格 | 均未整表匹配 |
| time_management | L0 0行/0格；L1 0行/0格；L2 0行/0格；L3 0行/0格 | L0 |

不适用：主因/并列项不是U；未将完整实现替换当作U局部修复。

| 实验 | L0每列非零不一致数 |
|---|---|
| baseline | {"comprehensive_project_score": 472} |
| time_management | {} |

L1–L3的每列不一致数、单侧行、共同键超额行及全部L0–L3字段已逐项保存在每个重跑JSON的`comparison.levels`，与本表同属交付证据；不是仅列总差异。

先按行数减少量，再按格子数；重复键先抵消相同行，剩余按整行字典序固定配对。大表使用权重区间配对，与展开重复行的原算法12组逐字段测试一致。整段gold实现及混合原因替换不冒充单点U证据；失败、无改善或行数变差的候选不计参与因素。


## 规则问题

无。

## 证据路径与复现

- 精简材料包：`records/021_packages/021_impl-008_asana__project_analytics.md`。
- 完整机械材料（可由prepare脚本重建）：`data/021_packages_work/021_impl-008_asana__project_analytics/021_impl-008_asana__project_analytics.json`。
- 重跑：`records/021_reruns_impl-008_asana__project_analytics.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 原始轨迹：`traces/dacomp_deimpl_prev.tar.gz`，事件定位见 `records/021_trace_audit.json`。
- 输入前指纹：`records/021_input_before.json`；后指纹与验证另见021记录。
- 执行环境：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`；调用本表重跑记录对应的021脚本，具体命令汇总见 `records/021_commands.txt`。
