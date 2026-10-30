# impl-011 / int_jira__sprint_performance_analytics（全量）

## 结论

主要原因：**D**；把握：中。story_points固定1而没有读取可用field history，是改善最多的局部点。

参与因素：D：velocity_trend（减0行/2格）；C：velocity_null_default（减1行/33格）；D：health_score（减0行/2格）；C：timestamp_window（减2行/236格）。标记：已披露。

## 差异与归因依据

契约要求读取最新active story point字段，无法解析才默认1；agent无读取判断直接1。单改该表达式减少19行/703格，比timestamp窗口减少2行和velocity NULL分支减少1行更多。窗口边界和NULL分类为C参与因素，health/velocity占位为D参与因素。LIMIT1000本身是契约规定，不能列为降级；错误放到snapshot之后是另一处实现差异，但单修未改善行规模，不列参与因素。

层：intermediate；实际schema：intermediate；评测键：sprint_id, performance_index。已核实数字来自下列查询/重跑；类别是按v2规则的判断，不将gold选择自动作为业务事实。

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml:1265–1414`；逐字原文见精简材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__sprint_performance_analytics.sql:1–1`，SHA-256 `221c358679c9d7256c3291fe27d0d6dcdbc63a8d8b8989afe4837dccde884525`。
- gold（仅定位/诊断） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/sql/intermediate/int_jira__sprint_performance_analytics.sql:1–233`，SHA-256 `b0f3b20d6a74ea127317086f5a1e415327f5df4ba8101aa19a87733a7994a31f`。

- whole_implementation_diagnostic：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_reruns_impl-011_int_jira__sprint_performance_analytics.json`。

- remove_limit：agent SQL第1行起：
```sql
 limit 1000
```
替换为：
```sql

```

- limit_before_snapshots：agent SQL第1行起：
```sql
from snapshots s join staging.stg_jira__issue i on cast(i.created_at as date) between s.start_date and coalesce(s.completed_at,s.ended_at,TIMESTAMPTZ '2025-10-13 00:00:00+00') limit 1000
```
替换为：
```sql
from snapshots s join (select sp.sprint_id,i.* from s sp cross join staging.stg_jira__issue i where cast(i.created_at as date) between sp.start_date and coalesce(sp.completed_at,sp.ended_at,TIMESTAMPTZ '2025-10-13 00:00:00+00') limit 1000) i on s.sprint_id=i.sprint_id
```

- velocity_trend：agent SQL第1行起：
```sql
null::double velocity_trend_3d
```
替换为：
```sql
avg(prev_remaining-remaining) over(partition by sprint_id order by day_number rows between 2 preceding and current row) velocity_trend_3d
```

- velocity_null_default：agent SQL第1行起：
```sql
case when coalesce(prev_remaining-remaining,0)>5 then 'High Velocity' when coalesce(prev_remaining-remaining,0)>2 then 'Good Velocity' when coalesce(prev_remaining-remaining,0)>0 then 'Low Velocity' when coalesce(prev_remaining-remaining,0)=0 then 'No Progress' else 'Negative Velocity' end
```
替换为：
```sql
case when prev_remaining-remaining>5 then 'High Velocity' when prev_remaining-remaining>2 then 'Good Velocity' when prev_remaining-remaining>0 then 'Low Velocity' when prev_remaining-remaining=0 then 'No Progress' else 'Negative Velocity' end
```

- health_score：agent SQL第1行起：
```sql
100::integer sprint_health_score
```
替换为：
```sql
least(100,greatest(0,100-case when completion_ratio<timeline_progress_ratio-0.2 then 30 else 0 end-case when not(completion_ratio<timeline_progress_ratio-0.2) and not(completion_ratio>timeline_progress_ratio+0.1) and abs(coalesce(committed_points-prev_committed_points,0))>committed_points*0.1 then 20 else 0 end-case when abs(remaining-ideal)>committed_points*0.3 then 25 else 0 end+case when completion_ratio>timeline_progress_ratio+0.1 then 10 else 0 end+case when completion_ratio/nullif(timeline_progress_ratio,0)>1.1 then 15 else 0 end))::integer sprint_health_score
```

- timestamp_window：agent SQL第1行起：
```sql
cast(i.created_at as date) between s.start_date
```
替换为：
```sql
i.created_at between s.started_at
```

- story_points_mapping：agent SQL第1行起：
```sql
1.0 points
```
替换为：
```sql
coalesce(
            (select
                case
                    when fh.field_value ~ '^[0-9]+\.?[0-9]*$' then fh.field_value::numeric
                    when fh.field_value ~ '^.*([0-9]+\.?[0-9]*).*$' then
                        regexp_extract(fh.field_value, '([0-9]+\.?[0-9]*)', 1)::numeric
                    else null
                end
             from staging.stg_jira__issue_field_history fh
             join staging.stg_jira__field f on fh.field_id = f.field_id
             where fh.issue_id = i.issue_id
               and f.field_name ilike '%story%point%'
               and fh.is_active = true
             order by fh.updated_at desc
             limit 1),
            1  -- Default story point value
        ) points
```

## agent可见证据与不确定性

**针对本表的具体说明**。

event55点名sprint performance analytics的趋势/评分简化默认；event15实现points=1，未出现对story字段不可用的判断。

最终报告原句（其适用范围按上文判定）：

> 合同非常广泛，本实现优先保证所有配置模型可执行；少数复杂分析并未完整实现合同中的每个指标/分支。尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。

扫描57个原始事件及最终result.md；完整可见输出命中位置、显式截断标记见 `records/021_trace_audit.json` index=34。所有原始事件均按id检查；代码在message中重复出现不当作解释理由，执行日志行数不当作已核实连接基数/字段语义。

| event | cause | 显式截断 |
|---|---|---|
| 8 | 7 | False |
| 22 | 21 | False |
| 24 | 23 | False |
| 26 | 25 | False |
| 32 | 31 | False |
| 36 | 35 | False |
| 42 | 41 | False |
| 44 | 43 | False |
| 46 | 45 | False |

## 原始数据一致性与查询

015的逐题原始数据核对提供背景；本次全部原件均只读，前后字节指纹另核对。impl-008/009/011/013的raw三侧一致。校准impl-030按agent留存raw，不能因initial与gold不同而一概不可评估。

核实查询条数（含失败尝试）：3；核实代价档：多条查询。每张不超过5条。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/jira.duckdb`；记录：`records/021_queries.json`。

```sql
SELECT 'staging.stg_jira__issue' source,count(*) n FROM staging.stg_jira__issue UNION ALL SELECT 'staging.stg_jira__sprint' source,count(*) n FROM staging.stg_jira__sprint
```

失败：Parser Error: syntax error at or near "source"

LINE 1: SELECT 'staging.stg_jira__issue' source,count(*) n FROM staging.stg_jira__issue UNION ALL...
                                         ^

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/jira.duckdb`；记录：`records/021_supplement_queries.json`。

```sql
SELECT 'staging.stg_jira__issue' source_name,count(*) n FROM staging.stg_jira__issue UNION ALL SELECT 'staging.stg_jira__sprint' source_name,count(*) n FROM staging.stg_jira__sprint
```

结果（列顺序["source_name", "n"]）：`[["staging.stg_jira__issue", 8000], ["staging.stg_jira__sprint", 298]]`

### 核实 3

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/jira.duckdb`；记录：`records/021_final_diagnostics.json`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE is_active) active_rows FROM staging.stg_jira__issue_field_history
```

结果（列顺序["n", "active_rows"]）：`[[12000, 9070]]`


## 固定时间与重跑

原始库只用read_only=True或READ_ONLY ATTACH；staging复制agent raw，其他层复制gold上游（CS）。所有写入在data/021_*私有副本。

留存结果同口径L0：169行/2986格；选定基线：168行/2947格。

共同固定时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-13 00:00:00+00'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-13'", "count": 1}]`。每组基线与单修使用完全相同的时间；跨组时间不同明确分列，不跨基线计算减少量。

| 实验 | L0–L3规模（包含键） | 整表首次匹配 |
|---|---|---|
| baseline | L0 168行/2947格；L1 168行/2947格；L2 168行/2947格；L3 168行/2947格 | 均未整表匹配 |
| whole_implementation_diagnostic | L0 16行/336格；L1 16行/336格；L2 16行/336格；L3 16行/336格 | 均未整表匹配 |
| remove_limit | L0 665行/12861格；L1 665行/12861格；L2 665行/12861格；L3 665行/12861格 | 均未整表匹配 |
| limit_before_snapshots | L0 197行/2903格；L1 197行/2903格；L2 197行/2903格；L3 197行/2903格 | 均未整表匹配 |
| velocity_trend | L0 168行/2945格；L1 168行/2945格；L2 168行/2945格；L3 168行/2945格 | 均未整表匹配 |
| velocity_null_default | L0 167行/2914格；L1 167行/2914格；L2 167行/2914格；L3 167行/2914格 | 均未整表匹配 |
| health_score | L0 168行/2945格；L1 168行/2945格；L2 168行/2945格；L3 168行/2945格 | 均未整表匹配 |
| timestamp_window | L0 166行/2711格；L1 166行/2711格；L2 166行/2711格；L3 166行/2711格 | 均未整表匹配 |
| story_points_mapping | L0 149行/2244格；L1 149行/2244格；L2 149行/2244格；L3 149行/2244格 | 均未整表匹配 |

不适用：主因/并列项不是U；未将完整实现替换当作U局部修复。

| 实验 | L0每列非零不一致数 |
|---|---|
| baseline | {"burndown_variance": 1, "issues_remaining": 25, "sprint_health_score": 2, "story_points_remaining": 33, "total_issues_committed": 25, "total_story_points_committed": 33, "velocity_category": 33, "velocity_trend_3d": 2} |
| whole_implementation_diagnostic | {} |
| remove_limit | {"issues_remaining": 69, "story_points_remaining": 69, "total_issues_committed": 69, "total_story_points_committed": 69, "velocity_category": 69} |
| limit_before_snapshots | {"burndown_variance": 11, "issues_remaining": 50, "sprint_health_score": 13, "story_points_remaining": 71, "total_issues_committed": 50, "total_story_points_committed": 71, "velocity_category": 62, "velocity_trend_3d": 13} |
| velocity_trend | {"burndown_variance": 1, "issues_remaining": 25, "sprint_health_score": 2, "story_points_remaining": 33, "total_issues_committed": 25, "total_story_points_committed": 33, "velocity_category": 33} |
| velocity_null_default | {"burndown_variance": 1, "issues_remaining": 25, "sprint_health_score": 2, "story_points_remaining": 33, "total_issues_committed": 25, "total_story_points_committed": 33, "velocity_trend_3d": 2} |
| health_score | {"burndown_variance": 1, "issues_remaining": 25, "story_points_remaining": 33, "total_issues_committed": 25, "total_story_points_committed": 33, "velocity_category": 33, "velocity_trend_3d": 2} |
| timestamp_window | {"burndown_variance": 5, "daily_velocity": 1, "sprint_health_score": 6, "story_points_remaining": 36, "total_story_points_committed": 36, "velocity_category": 37, "velocity_trend_3d": 7} |
| story_points_mapping | {"burndown_variance": 14, "daily_velocity": 2, "issues_completed": 2, "issues_remaining": 38, "sprint_health_score": 21, "story_points_completed": 2, "story_points_remaining": 38, "total_issues_committed": 39, "total_story_points_committed": 39, "velocity_category": 33, "velocity_trend_3d": 21} |

L1–L3的每列不一致数、单侧行、共同键超额行及全部L0–L3字段已逐项保存在每个重跑JSON的`comparison.levels`，与本表同属交付证据；不是仅列总差异。

先按行数减少量，再按格子数；重复键先抵消相同行，剩余按整行字典序固定配对。大表使用权重区间配对，与展开重复行的原算法12组逐字段测试一致。整段gold实现及混合原因替换不冒充单点U证据；失败、无改善或行数变差的候选不计参与因素。


## 规则问题

契约明确允许无序LIMIT1000，不能把LIMIT本身归D。移到snapshot前是C候选，但单修未改善行规模；gold完整SQL重跑仍有16行差异，说明任意子集/同序并列无法精确复现。按实际单修贡献选D，残余抽样差异记录为O性质诊断，不宣称占位解释全部差异。

## 证据路径与复现

- 精简材料包：`records/021_packages/021_impl-011_int_jira__sprint_performance_analytics.md`。
- 完整机械材料（可由prepare脚本重建）：`data/021_packages_work/021_impl-011_int_jira__sprint_performance_analytics/021_impl-011_int_jira__sprint_performance_analytics.json`。
- 重跑：`records/021_reruns_impl-011_int_jira__sprint_performance_analytics.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 重跑：`records/021_detailed_reruns_impl-011_int_jira__sprint_performance_analytics.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 重跑：`records/021_extra_reruns_impl-011_int_jira__sprint_performance_analytics.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 原始轨迹：`traces/dacomp_deimpl_prev.tar.gz`，事件定位见 `records/021_trace_audit.json`。
- 输入前指纹：`records/021_input_before.json`；后指纹与验证另见021记录。
- 执行环境：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`；调用本表重跑记录对应的021脚本，具体命令汇总见 `records/021_commands.txt`。
