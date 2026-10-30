# impl-011 / jira__team_performance_dashboard（全量）

## 结论

主要原因：**C**；把握：高。以全部user为左表保留1626个无user_metrics用户，违背起始join。

参与因素：C：avg_daily_activity_score（减0行/3315格）；C：avg_weekly_activity_score（减0行/3315格）；D：projects_contributed_to（减0行/4374格）；D：issue_types_worked_on（减0行/4374格）；D：days_since_first_issue（减0行/4374格）；D：leadership_indicator（减0行/3207格）；D：overall_performance_score（减0行/4374格）。标记：已披露。

## 差异与归因依据

契约明确user_metrics与users join作为起始范围；agent以users LEFT JOIN。只改为JOIN减少1626行/52032格，主因C。两列额外COALESCE(avg_close_time_days,0)与多项增长/评分占位分别为C/D参与因素。

层：marts；实际schema：marts；评测键：user_id。已核实数字来自下列查询/重跑；类别是按v2规则的判断，不将gold选择自动作为业务事实。

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml:2475–2605`；逐字原文见精简材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__team_performance_dashboard.sql:1–1`，SHA-256 `98bb8b5cf3879fa0fe51948a50322ab06c8d8053c501669a93969bc0c2d5d9b4`。
- gold（仅定位/诊断） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/sql/marts/jira__team_performance_dashboard.sql:1–255`，SHA-256 `30e958d17295b7fe1189c5c16305f2720c5d0fe28c6bb683408646fd5986ce52`。

- whole_implementation_diagnostic：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_reruns_impl-011_jira__team_performance_dashboard.json`。

- user_metrics_driver：agent SQL第1行起：
```sql
from staging.stg_jira__user u left join intermediate.int_jira__user_metrics m using(user_id)
```
替换为：
```sql
from staging.stg_jira__user u join intermediate.int_jira__user_metrics m using(user_id)
```

- avg_daily_activity_score：agent SQL第1行起：
```sql
coalesce(m.avg_close_time_days,0)::decimal(18,0) avg_daily_activity_score
```
替换为：
```sql
m.avg_close_time_days::decimal(18,0) avg_daily_activity_score
```

- avg_weekly_activity_score：agent SQL第1行起：
```sql
coalesce(m.avg_close_time_days,0)::decimal(18,0) avg_weekly_activity_score
```
替换为：
```sql
m.avg_close_time_days::decimal(18,0) avg_weekly_activity_score
```

- projects_contributed_to：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_detailed_reruns_impl-011_jira__team_performance_dashboard.json`。

- issue_types_worked_on：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_detailed_reruns_impl-011_jira__team_performance_dashboard.json`。

- days_since_first_issue：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_detailed_reruns_impl-011_jira__team_performance_dashboard.json`。

- leadership_indicator：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_detailed_reruns_impl-011_jira__team_performance_dashboard.json`。

- overall_performance_score：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_detailed_reruns_impl-011_jira__team_performance_dashboard.json`。

- gold_sql_same_clock：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_extra_reruns_impl-011_jira__team_performance_dashboard.json`。

## agent可见证据与不确定性

**只有通用策略说明**。

event55点名team dashboard详细计算使用简化/默认；没有具体说明本表起始连接保留范围。

最终报告原句（其适用范围按上文判定）：

> 合同非常广泛，本实现优先保证所有配置模型可执行；少数复杂分析并未完整实现合同中的每个指标/分支。尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。

扫描57个原始事件及最终result.md；完整可见输出命中位置、显式截断标记见 `records/021_trace_audit.json` index=39。所有原始事件均按id检查；代码在message中重复出现不当作解释理由，执行日志行数不当作已核实连接基数/字段语义。

| event | cause | 显式截断 |
|---|---|---|
| 8 | 7 | False |
| 20 | 19 | False |
| 22 | 21 | False |
| 24 | 23 | False |
| 32 | 31 | False |
| 38 | 37 | False |
| 42 | 41 | False |
| 44 | 43 | False |
| 46 | 45 | False |

## 原始数据一致性与查询

015的逐题原始数据核对提供背景；本次全部原件均只读，前后字节指纹另核对。impl-008/009/011/013的raw三侧一致。校准impl-030按agent留存raw，不能因initial与gold不同而一概不可评估。

核实查询条数（含失败尝试）：2；核实代价档：多条查询。每张不超过5条。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/jira.duckdb`；记录：`records/021_queries.json`。

```sql
SELECT 'intermediate.int_jira__user_metrics' source,count(*) n FROM intermediate.int_jira__user_metrics UNION ALL SELECT 'staging.stg_jira__user' source,count(*) n FROM staging.stg_jira__user
```

失败：Parser Error: syntax error at or near "source"

LINE 1: SELECT 'intermediate.int_jira__user_metrics' source,count(*) n FROM intermediate.int_jira__user_metrics...
                                                     ^

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/jira.duckdb`；记录：`records/021_supplement_queries.json`。

```sql
SELECT 'intermediate.int_jira__user_metrics' source_name,count(*) n FROM intermediate.int_jira__user_metrics UNION ALL SELECT 'staging.stg_jira__user' source_name,count(*) n FROM staging.stg_jira__user
```

结果（列顺序["source_name", "n"]）：`[["intermediate.int_jira__user_metrics", 4374], ["staging.stg_jira__user", 6000]]`


## 固定时间与重跑

原始库只用read_only=True或READ_ONLY ATTACH；staging复制agent raw，其他层复制gold上游（CS）。所有写入在data/021_*私有副本。

留存结果同口径L0：6000行/79365格；选定基线：6000行/79365格。

共同固定时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-13 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-13'", "count": 0}]`。每组基线与单修使用完全相同的时间；跨组时间不同明确分列，不跨基线计算减少量。

| 实验 | L0–L3规模（包含键） | 整表首次匹配 |
|---|---|---|
| baseline | L0 6000行/79365格；L1 6000行/79365格；L2 6000行/79365格；L3 6000行/79365格 | 均未整表匹配 |
| whole_implementation_diagnostic | L0 4374行/4374格；L1 4374行/4374格；L2 4374行/4374格；L3 4374行/4374格 | 均未整表匹配 |
| user_metrics_driver | L0 4374行/27333格；L1 4374行/27333格；L2 4374行/27333格；L3 4374行/27333格 | 均未整表匹配 |
| avg_daily_activity_score | L0 6000行/76050格；L1 6000行/76050格；L2 6000行/76050格；L3 6000行/76050格 | 均未整表匹配 |
| avg_weekly_activity_score | L0 6000行/76050格；L1 6000行/76050格；L2 6000行/76050格；L3 6000行/76050格 | 均未整表匹配 |
| projects_contributed_to | L0 6000行/74991格；L1 6000行/74991格；L2 6000行/74991格；L3 6000行/74991格 | 均未整表匹配 |
| issue_types_worked_on | L0 6000行/74991格；L1 6000行/74991格；L2 6000行/74991格；L3 6000行/74991格 | 均未整表匹配 |
| days_since_first_issue | L0 6000行/74991格；L1 6000行/74991格；L2 6000行/74991格；L3 6000行/74991格 | 均未整表匹配 |
| leadership_indicator | L0 6000行/76158格；L1 6000行/76158格；L2 6000行/76158格；L3 6000行/76158格 | 均未整表匹配 |
| overall_performance_score | L0 6000行/74991格；L1 6000行/74991格；L2 6000行/74991格；L3 6000行/74991格 | 均未整表匹配 |
| gold_sql_same_clock | L0 0行/0格；L1 0行/0格；L2 0行/0格；L3 0行/0格 | L0 |

不适用：主因/并列项不是U；未将完整实现替换当作U局部修复。

| 实验 | L0每列非零不一致数 |
|---|---|
| baseline | {"avg_daily_activity_score": 3315, "avg_weekly_activity_score": 3315, "days_since_first_issue": 4374, "issue_types_worked_on": 4374, "leadership_indicator": 3207, "overall_performance_score": 4374, "projects_contributed_to": 4374} |
| whole_implementation_diagnostic | {"days_since_first_issue": 4374} |
| user_metrics_driver | {"avg_daily_activity_score": 3315, "avg_weekly_activity_score": 3315, "days_since_first_issue": 4374, "issue_types_worked_on": 4374, "leadership_indicator": 3207, "overall_performance_score": 4374, "projects_contributed_to": 4374} |
| avg_daily_activity_score | {"avg_weekly_activity_score": 3315, "days_since_first_issue": 4374, "issue_types_worked_on": 4374, "leadership_indicator": 3207, "overall_performance_score": 4374, "projects_contributed_to": 4374} |
| avg_weekly_activity_score | {"avg_daily_activity_score": 3315, "days_since_first_issue": 4374, "issue_types_worked_on": 4374, "leadership_indicator": 3207, "overall_performance_score": 4374, "projects_contributed_to": 4374} |
| projects_contributed_to | {"avg_daily_activity_score": 3315, "avg_weekly_activity_score": 3315, "days_since_first_issue": 4374, "issue_types_worked_on": 4374, "leadership_indicator": 3207, "overall_performance_score": 4374} |
| issue_types_worked_on | {"avg_daily_activity_score": 3315, "avg_weekly_activity_score": 3315, "days_since_first_issue": 4374, "leadership_indicator": 3207, "overall_performance_score": 4374, "projects_contributed_to": 4374} |
| days_since_first_issue | {"avg_daily_activity_score": 3315, "avg_weekly_activity_score": 3315, "issue_types_worked_on": 4374, "leadership_indicator": 3207, "overall_performance_score": 4374, "projects_contributed_to": 4374} |
| leadership_indicator | {"avg_daily_activity_score": 3315, "avg_weekly_activity_score": 3315, "days_since_first_issue": 4374, "issue_types_worked_on": 4374, "overall_performance_score": 4374, "projects_contributed_to": 4374} |
| overall_performance_score | {"avg_daily_activity_score": 3315, "avg_weekly_activity_score": 3315, "days_since_first_issue": 4374, "issue_types_worked_on": 4374, "leadership_indicator": 3207, "projects_contributed_to": 4374} |
| gold_sql_same_clock | {} |

L1–L3的每列不一致数、单侧行、共同键超额行及全部L0–L3字段已逐项保存在每个重跑JSON的`comparison.levels`，与本表同属交付证据；不是仅列总差异。

先按行数减少量，再按格子数；重复键先抵消相同行，剩余按整行字典序固定配对。大表使用权重区间配对，与展开重复行的原算法12组逐字段测试一致。整段gold实现及混合原因替换不冒充单点U证据；失败、无改善或行数变差的候选不计参与因素。


## 规则问题

无。

## 证据路径与复现

- 精简材料包：`records/021_packages/021_impl-011_jira__team_performance_dashboard.md`。
- 完整机械材料（可由prepare脚本重建）：`data/021_packages_work/021_impl-011_jira__team_performance_dashboard/021_impl-011_jira__team_performance_dashboard.json`。
- 重跑：`records/021_reruns_impl-011_jira__team_performance_dashboard.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 重跑：`records/021_detailed_reruns_impl-011_jira__team_performance_dashboard.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 重跑：`records/021_extra_reruns_impl-011_jira__team_performance_dashboard.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 原始轨迹：`traces/dacomp_deimpl_prev.tar.gz`，事件定位见 `records/021_trace_audit.json`。
- 输入前指纹：`records/021_input_before.json`；后指纹与验证另见021记录。
- 执行环境：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`；调用本表重跑记录对应的021脚本，具体命令汇总见 `records/021_commands.txt`。
