# impl-011 / jira__sprint_enhanced（全量）

## 结论

主要原因：**D**；把握：高。七个sprint承诺/完成指标全部NULL，源字段和窗口都可用。

参与因素：无经单修确认的其他参与因素。标记：已披露。

## 差异与归因依据

契约明确开始/结束日的story points聚合和issues_committed；agent七列NULL。逐列按契约聚合单修均减少298格，同类D并列合并为D；完整实现L0一致。

层：marts；实际schema：marts；评测键：sprint_id。已核实数字来自下列查询/重跑；类别是按v2规则的判断，不将gold选择自动作为业务事实。

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml:2177–2245`；逐字原文见精简材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__sprint_enhanced.sql:1–1`，SHA-256 `230eda3392cc2b380fb230cc02d031f9f39454c06d97226ef0571bca075884dd`。
- gold（仅定位/诊断） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/sql/marts/jira__sprint_enhanced.sql:1–95`，SHA-256 `4e261441b297e1a3bb29e812e4d2730b2e029447ca5b3b63343965ef5a2b5b73`。

- whole_implementation_diagnostic：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_reruns_impl-011_jira__sprint_enhanced.json`。

- story_points_committed：agent SQL第1行起：
```sql
null::hugeint story_points_committed
```
替换为：
```sql
sum(coalesce(story_points,0)) filter(where date_day=cast(sprint_started_at as date) or (date_day<cast(sprint_started_at as date) and date_day=cast(TIMESTAMPTZ '2025-10-13 00:00:00+00' as date))) story_points_committed
```

- story_point_estimate_committed：agent SQL第1行起：
```sql
null::hugeint story_point_estimate_committed
```
替换为：
```sql
sum(coalesce(story_point_estimate,0)) filter(where date_day=cast(sprint_started_at as date) or (date_day<cast(sprint_started_at as date) and date_day=cast(TIMESTAMPTZ '2025-10-13 00:00:00+00' as date))) story_point_estimate_committed
```

- story_points_end：agent SQL第1行起：
```sql
null::hugeint story_points_end
```
替换为：
```sql
sum(coalesce(story_points,0)) filter(where date_day=cast(sprint_ended_at as date)) story_points_end
```

- story_point_estimate_end：agent SQL第1行起：
```sql
null::hugeint story_point_estimate_end
```
替换为：
```sql
sum(coalesce(story_point_estimate,0)) filter(where date_day=cast(sprint_ended_at as date)) story_point_estimate_end
```

- story_points_completed：agent SQL第1行起：
```sql
null::hugeint story_points_completed
```
替换为：
```sql
sum(case when is_issue_resolved_in_sprint then story_points else 0 end) filter(where date_day=cast(sprint_ended_at as date)) story_points_completed
```

- story_point_estimate_completed：agent SQL第1行起：
```sql
null::hugeint story_point_estimate_completed
```
替换为：
```sql
sum(case when is_issue_resolved_in_sprint then story_point_estimate else 0 end) filter(where date_day=cast(sprint_ended_at as date)) story_point_estimate_completed
```

- issues_committed：agent SQL第1行起：
```sql
null::bigint issues_committed
```
替换为：
```sql
count(distinct issue_id) filter(where date_day=cast(sprint_started_at as date) or (date_day<cast(sprint_started_at as date) and date_day=cast(TIMESTAMPTZ '2025-10-13 00:00:00+00' as date))) issues_committed
```

## agent可见证据与不确定性

**只有通用策略说明**。

event17写NULL占位；event55仅泛称复杂分析未完整实现，未点名sprint_enhanced这七项。

最终报告原句（其适用范围按上文判定）：

> 合同非常广泛，本实现优先保证所有配置模型可执行；少数复杂分析并未完整实现合同中的每个指标/分支。尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。

扫描57个原始事件及最终result.md；完整可见输出命中位置、显式截断标记见 `records/021_trace_audit.json` index=37。所有原始事件均按id检查；代码在message中重复出现不当作解释理由，执行日志行数不当作已核实连接基数/字段语义。

| event | cause | 显式截断 |
|---|---|---|
| 8 | 7 | False |
| 22 | 21 | False |
| 24 | 23 | False |
| 32 | 31 | False |
| 38 | 37 | False |

## 原始数据一致性与查询

015的逐题原始数据核对提供背景；本次全部原件均只读，前后字节指纹另核对。impl-008/009/011/013的raw三侧一致。校准impl-030按agent留存raw，不能因initial与gold不同而一概不可评估。

核实查询条数（含失败尝试）：2；核实代价档：多条查询。每张不超过5条。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/jira.duckdb`；记录：`records/021_queries.json`。

```sql
SELECT 'marts.jira__daily_sprint_issue_history' source,count(*) n FROM marts.jira__daily_sprint_issue_history
```

失败：Parser Error: syntax error at or near "source"

LINE 1: SELECT 'marts.jira__daily_sprint_issue_history' source,count(*) n FROM marts.jira__daily_sprint_issue_histo...
                                                        ^

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/jira.duckdb`；记录：`records/021_supplement_queries.json`。

```sql
SELECT 'marts.jira__daily_sprint_issue_history' source_name,count(*) n FROM marts.jira__daily_sprint_issue_history
```

结果（列顺序["source_name", "n"]）：`[["marts.jira__daily_sprint_issue_history", 58102]]`


## 固定时间与重跑

原始库只用read_only=True或READ_ONLY ATTACH；staging复制agent raw，其他层复制gold上游（CS）。所有写入在data/021_*私有副本。

留存结果同口径L0：298行/2086格；选定基线：298行/2086格。

共同固定时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-13 00:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-13'", "count": 0}]`。每组基线与单修使用完全相同的时间；跨组时间不同明确分列，不跨基线计算减少量。

| 实验 | L0–L3规模（包含键） | 整表首次匹配 |
|---|---|---|
| baseline | L0 298行/2086格；L1 298行/2086格；L2 298行/2086格；L3 298行/2086格 | 均未整表匹配 |
| whole_implementation_diagnostic | L0 0行/0格；L1 0行/0格；L2 0行/0格；L3 0行/0格 | L0 |
| story_points_committed | L0 298行/1788格；L1 298行/1788格；L2 298行/1788格；L3 298行/1788格 | 均未整表匹配 |
| story_point_estimate_committed | L0 298行/1788格；L1 298行/1788格；L2 298行/1788格；L3 298行/1788格 | 均未整表匹配 |
| story_points_end | L0 298行/1788格；L1 298行/1788格；L2 298行/1788格；L3 298行/1788格 | 均未整表匹配 |
| story_point_estimate_end | L0 298行/1788格；L1 298行/1788格；L2 298行/1788格；L3 298行/1788格 | 均未整表匹配 |
| story_points_completed | L0 298行/1788格；L1 298行/1788格；L2 298行/1788格；L3 298行/1788格 | 均未整表匹配 |
| story_point_estimate_completed | L0 298行/1788格；L1 298行/1788格；L2 298行/1788格；L3 298行/1788格 | 均未整表匹配 |
| issues_committed | L0 298行/1788格；L1 298行/1788格；L2 298行/1788格；L3 298行/1788格 | 均未整表匹配 |

不适用：主因/并列项不是U；未将完整实现替换当作U局部修复。

| 实验 | L0每列非零不一致数 |
|---|---|
| baseline | {"issues_committed": 298, "story_point_estimate_committed": 298, "story_point_estimate_completed": 298, "story_point_estimate_end": 298, "story_points_committed": 298, "story_points_completed": 298, "story_points_end": 298} |
| whole_implementation_diagnostic | {} |
| story_points_committed | {"issues_committed": 298, "story_point_estimate_committed": 298, "story_point_estimate_completed": 298, "story_point_estimate_end": 298, "story_points_completed": 298, "story_points_end": 298} |
| story_point_estimate_committed | {"issues_committed": 298, "story_point_estimate_completed": 298, "story_point_estimate_end": 298, "story_points_committed": 298, "story_points_completed": 298, "story_points_end": 298} |
| story_points_end | {"issues_committed": 298, "story_point_estimate_committed": 298, "story_point_estimate_completed": 298, "story_point_estimate_end": 298, "story_points_committed": 298, "story_points_completed": 298} |
| story_point_estimate_end | {"issues_committed": 298, "story_point_estimate_committed": 298, "story_point_estimate_completed": 298, "story_points_committed": 298, "story_points_completed": 298, "story_points_end": 298} |
| story_points_completed | {"issues_committed": 298, "story_point_estimate_committed": 298, "story_point_estimate_completed": 298, "story_point_estimate_end": 298, "story_points_committed": 298, "story_points_end": 298} |
| story_point_estimate_completed | {"issues_committed": 298, "story_point_estimate_committed": 298, "story_point_estimate_end": 298, "story_points_committed": 298, "story_points_completed": 298, "story_points_end": 298} |
| issues_committed | {"story_point_estimate_committed": 298, "story_point_estimate_completed": 298, "story_point_estimate_end": 298, "story_points_committed": 298, "story_points_completed": 298, "story_points_end": 298} |

L1–L3的每列不一致数、单侧行、共同键超额行及全部L0–L3字段已逐项保存在每个重跑JSON的`comparison.levels`，与本表同属交付证据；不是仅列总差异。

先按行数减少量，再按格子数；重复键先抵消相同行，剩余按整行字典序固定配对。大表使用权重区间配对，与展开重复行的原算法12组逐字段测试一致。整段gold实现及混合原因替换不冒充单点U证据；失败、无改善或行数变差的候选不计参与因素。


## 规则问题

无。

## 证据路径与复现

- 精简材料包：`records/021_packages/021_impl-011_jira__sprint_enhanced.md`。
- 完整机械材料（可由prepare脚本重建）：`data/021_packages_work/021_impl-011_jira__sprint_enhanced/021_impl-011_jira__sprint_enhanced.json`。
- 重跑：`records/021_reruns_impl-011_jira__sprint_enhanced.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 重跑：`records/021_detailed_reruns_impl-011_jira__sprint_enhanced.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 原始轨迹：`traces/dacomp_deimpl_prev.tar.gz`，事件定位见 `records/021_trace_audit.json`。
- 输入前指纹：`records/021_input_before.json`；后指纹与验证另见021记录。
- 执行环境：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`；调用本表重跑记录对应的021脚本，具体命令汇总见 `records/021_commands.txt`。
