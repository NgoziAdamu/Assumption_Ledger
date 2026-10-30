# impl-011 / jira__issue_intelligence_analytics（全量）

## 结论

主要原因：**C**；把握：中。省略契约明确保留重复的comparative关联，使千万行结果缩成8000行。

参与因素：无经单修确认的其他参与因素；保留其他评分/分类占位事实，未逐项单修，不列为参与因素。。标记：已披露。

## 差异与归因依据

契约明确project内self-join及后续两次按issue_id关联，重复保留。agent仅原始issue逐行投影并填默认评分。独立恢复该关联基数（其余投影字节不动）测量行数改善；未实现的评分/分类另有D，但不把完整gold替换当单点因果证据。

层：marts；实际schema：marts；评测键：issue_id, issue_key。已核实数字来自下列查询/重跑；类别是按v2规则的判断，不将gold选择自动作为业务事实。

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml:2606–2717`；逐字原文见精简材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__issue_intelligence_analytics.sql:1–1`，SHA-256 `cf2a179aecbc5966ec5d1164e833a937927dad0488bb88d4bb26ce97f7b203d6`。
- gold（仅定位/诊断） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/sql/marts/jira__issue_intelligence_analytics.sql:1–250`，SHA-256 `9b19f0418f4abfa2d5784224cc50c494d163a26dbf3c1710bdf362cfaeebe460`。

- comparative_join_multiplicity：agent SQL第1行起：
```sql
from marts.jira__issue_enhanced
```
替换为：
```sql
from (select base.* from marts.jira__issue_enhanced base join marts.jira__issue_enhanced peer on base.project_id=peer.project_id join marts.jira__issue_enhanced peer2 on base.project_id=peer2.project_id) comparative
```

- whole_implementation_diagnostic：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_fast_reruns_impl-011_jira__issue_intelligence_analytics.json`。

## agent可见证据与不确定性

**只有通用策略说明**。

event21生成单源简化SQL；event55笼统说明少数复杂分析未完整实现，但列举中没有点名issue intelligence或其重复关联。

最终报告原句（其适用范围按上文判定）：

> 合同非常广泛，本实现优先保证所有配置模型可执行；少数复杂分析并未完整实现合同中的每个指标/分支。尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。

扫描57个原始事件及最终result.md；完整可见输出命中位置、显式截断标记见 `records/021_trace_audit.json` index=35。所有原始事件均按id检查；代码在message中重复出现不当作解释理由，执行日志行数不当作已核实连接基数/字段语义。

| event | cause | 显式截断 |
|---|---|---|
| 8 | 7 | False |
| 20 | 19 | False |
| 22 | 21 | False |
| 24 | 23 | False |
| 32 | 31 | False |
| 38 | 37 | False |
| 46 | 45 | False |

## 原始数据一致性与查询

015的逐题原始数据核对提供背景；本次全部原件均只读，前后字节指纹另核对。impl-008/009/011/013的raw三侧一致。校准impl-030按agent留存raw，不能因initial与gold不同而一概不可评估。

核实查询条数（含失败尝试）：2；核实代价档：多条查询。每张不超过5条。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/jira.duckdb`；记录：`records/021_queries.json`。

```sql
SELECT 'marts.jira__issue_enhanced' source,count(*) n FROM marts.jira__issue_enhanced
```

失败：Parser Error: syntax error at or near "source"

LINE 1: SELECT 'marts.jira__issue_enhanced' source,count(*) n FROM marts.jira__issue_enhanced
                                            ^

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/jira.duckdb`；记录：`records/021_supplement_queries.json`。

```sql
SELECT 'marts.jira__issue_enhanced' source_name,count(*) n FROM marts.jira__issue_enhanced
```

结果（列顺序["source_name", "n"]）：`[["marts.jira__issue_enhanced", 8000]]`

诊断来源：`records/021_final_diagnostics.json`；SQL：
```sql
SELECT sum(n*n) expected_project_selfjoin_rows FROM (SELECT project_id,count(*) n FROM marts.jira__issue_enhanced WHERE project_id IS NOT NULL GROUP BY project_id)
```
结果：`[[328274]]`。

诊断来源：`records/021_runtime_diagnostics.json`；SQL：
```sql
WITH a AS(SELECT "issue_id","issue_key","age_risk_score","assignee_name","assignment_risk_score","collaboration_opportunity_score","completion_probability","complexity_risk_score","current_priority","current_status","deviation_risk_score","efficiency_opportunity_score","health_status","high_complexity_risk","intelligence_score","intervention_urgency","is_active_sprint","issue_type","lifecycle_outlier_status","lifecycle_pattern","lifecycle_quality_score","predicted_completion_timeframe","process_opportunity_score","project_name","recommended_action","regression_ratio","strategic_importance","total_opportunity_score","total_risk_score",count(*) n FROM replay.marts.jira__issue_intelligence_analytics GROUP BY ALL),g AS(SELECT "issue_id","issue_key","age_risk_score","assignee_name","assignment_risk_score","collaboration_opportunity_score","completion_probability","complexity_risk_score","current_priority","current_status","deviation_risk_score","efficiency_opportunity_score","health_status","high_complexity_risk","intelligence_score","intervention_urgency","is_active_sprint","issue_type","lifecycle_outlier_status","lifecycle_pattern","lifecycle_quality_score","predicted_completion_timeframe","process_opportunity_score","project_name","recommended_action","regression_ratio","strategic_importance","total_opportunity_score","total_risk_score",count(*) n FROM gold.marts.jira__issue_intelligence_analytics GROUP BY ALL) SELECT (SELECT count(*) FROM (SELECT * FROM a EXCEPT ALL SELECT * FROM g)),(SELECT count(*) FROM (SELECT * FROM g EXCEPT ALL SELECT * FROM a))
```
结果：`[[0, 0]]`。

诊断来源：`records/021_runtime_diagnostics.json`；SQL：
```sql
SELECT min(i.created_at+g.total_lifecycle_days*interval '1 day')::VARCHAR,max(i.created_at+g.total_lifecycle_days*interval '1 day')::VARCHAR FROM gold.marts.jira__issue_intelligence_analytics g JOIN gold.marts.jira__issue_enhanced i USING(issue_id) WHERE i.resolved_at IS NULL
```
结果：`[["2025-10-13 11:15:18.991", "2025-10-13 11:15:18.991"]]`。


## 固定时间与重跑

原始库只用read_only=True或READ_ONLY ATTACH；staging复制agent raw，其他层复制gold上游（CS）。所有写入在data/021_*私有副本。

留存结果同口径L0：13799108行/427586968格；选定基线：13799108行/427586968格。

共同固定时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-13 00:00:00+00'", "count": 8}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-13'", "count": 0}]`。每组基线与单修使用完全相同的时间；跨组时间不同明确分列，不跨基线计算减少量。

| 实验 | L0–L3规模（包含键） | 整表首次匹配 |
|---|---|---|
| baseline | L0 13799108行/427586968格；L1 13799108行/427586968格；L2 13799108行/427586968格；L3 13799108行/427586968格 | 均未整表匹配 |
| comparative_join_multiplicity | L0 13799108行/107821945格；L1 13799108行/107821945格；L2 13799108行/107821945格；L3 13799108行/107821945格 | 均未整表匹配 |
| whole_implementation_diagnostic | L0 5981646行/11472799格；L1 5981646行/11472799格；L2 5517274行/7995018格；L3 5517274行/7995018格 | 均未整表匹配 |

不适用：主因/并列项不是U；未将完整实现替换当作U局部修复。

| 实验 | L0每列非零不一致数 |
|---|---|
| baseline | {"collaboration_opportunity_score": 2606, "deviation_risk_score": 3052, "efficiency_opportunity_score": 2617, "health_status": 5761, "intelligence_score": 7986, "intervention_urgency": 4053, "lifecycle_deviation_ratio": 8000, "lifecycle_outlier_status": 8000, "recommended_action": 6609, "strategic_importance": 3304, "total_lifecycle_days": 3205, "total_opportunity_score": 4375, "total_risk_score": 3052} |
| comparative_join_multiplicity | {"collaboration_opportunity_score": 4443545, "deviation_risk_score": 5296949, "efficiency_opportunity_score": 4502719, "health_status": 9897148, "intelligence_score": 13777360, "intervention_urgency": 6976642, "lifecycle_deviation_ratio": 13799108, "lifecycle_outlier_status": 13799108, "recommended_action": 11356516, "strategic_importance": 5671731, "total_lifecycle_days": 5517274, "total_opportunity_score": 7486896, "total_risk_score": 5296949} |
| whole_implementation_diagnostic | {"lifecycle_deviation_ratio": 5955525, "total_lifecycle_days": 5517274} |

L1–L3的每列不一致数、单侧行、共同键超额行及全部L0–L3字段已逐项保存在每个重跑JSON的`comparison.levels`，与本表同属交付证据；不是仅列总差异。

先按行数减少量，再按格子数；重复键先抵消相同行，剩余按整行字典序固定配对。大表使用权重区间配对，与展开重复行的原算法12组逐字段测试一致。整段gold实现及混合原因替换不冒充单点U证据；失败、无改善或行数变差的候选不计参与因素。

恢复关联后行规模可能保持不变：原先的gold单侧重复行变成共同键差异行；格子规模才体现改善。完整gold同固定时刻重跑仍因历史运行时刻不同在两个时间派生列残留差异，去除这两列的含重复次数诊断见021_runtime_diagnostics.json。


## 规则问题

省略的是comparative关联块；局部替换仅增加两次project内关联以恢复重复基数，保持所有原投影不动。完整gold替换单列为诊断，不能用于U门槛，也不能用它区分各占位输出的相对贡献。

## 证据路径与复现

- 精简材料包：`records/021_packages/021_impl-011_jira__issue_intelligence_analytics.md`。
- 完整机械材料（可由prepare脚本重建）：`data/021_packages_work/021_impl-011_jira__issue_intelligence_analytics/021_impl-011_jira__issue_intelligence_analytics.json`。
- 重跑：`records/021_fast_reruns_impl-011_jira__issue_intelligence_analytics.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 原始轨迹：`traces/dacomp_deimpl_prev.tar.gz`，事件定位见 `records/021_trace_audit.json`。
- 输入前指纹：`records/021_input_before.json`；后指纹与验证另见021记录。
- 执行环境：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`；调用本表重跑记录对应的021脚本，具体命令汇总见 `records/021_commands.txt`。
