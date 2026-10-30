# impl-011 / jira__project_risk_assessment（全量）

## 结论

主要原因：**O**；把握：中。gold用issue_type_id匹配类型单词，agent按类型名计算价值。

参与因素：D：unique_issue_types（减0行/193格）；D：unique_components（减0行/186格）；D：total_external_links（减0行/193格）；D：sprint_adoption_rate（减0行/193格）；D：complexity_risk_score（减0行/189格）；D：scope_risk_score（减0行/193格）；D：recommended_intervention（减0行/193格）；D：strategic_priority_recommendation（减0行/61格）。标记：已披露。

## 差异与归因依据

契约按epic/story/task/bug类型分别赋8/3/2/1.5分。agent通过issue_type表匹配类型名；agent可见8000行均成功关联，其中4180行名称是epic/story/bug，但ID字符串匹配这些单词为0。gold对ID做ILIKE使全部回落2。只改这一权重来源政策减少578格，为最大单项。其他复杂度、scope和建议占位为D参与因素。

层：marts；实际schema：marts；评测键：project_id。已核实数字来自下列查询/重跑；类别是按v2规则的判断，不将gold选择自动作为业务事实。

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml:2718–2868`；逐字原文见精简材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__project_risk_assessment.sql:1–1`，SHA-256 `8c35c82677fdafd686cddcf429cb022be23ca2100ded9f071acd9f872fd92500`。
- gold（仅定位/诊断） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-011/sql/marts/jira__project_risk_assessment.sql:1–292`，SHA-256 `206a0ca45af5d4cb902db7b39ef83c7b8ff54bf0b14cc06fc3348eb48b2a6d70`。

- whole_implementation_diagnostic：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_reruns_impl-011_jira__project_risk_assessment.json`。

- type_id_instead_name：agent SQL第1行起：
```sql
sum(case lower(t.issue_type_name) when 'epic' then 8.0 when 'story' then 3.0 when 'bug' then 1.5 else 2.0 end) estimated
```
替换为：
```sql
sum(case when i.issue_type_id ilike '%epic%' then 8.0 when i.issue_type_id ilike '%story%' then 3.0 when i.issue_type_id ilike '%bug%' then 1.5 else 2.0 end) estimated
```

- type_id_instead_name：agent SQL第1行起：
```sql
then case lower(t.issue_type_name) when 'epic' then 8.0 when 'story' then 3.0 when 'bug' then 1.5 else 2.0 end else 0 end) delivered
```
替换为：
```sql
then case when i.issue_type_id ilike '%epic%' then 8.0 when i.issue_type_id ilike '%story%' then 3.0 when i.issue_type_id ilike '%bug%' then 1.5 else 2.0 end else 0 end) delivered
```

- unique_issue_types：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_extra_reruns_impl-011_jira__project_risk_assessment.json`。

- unique_components：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_extra_reruns_impl-011_jira__project_risk_assessment.json`。

- total_external_links：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_extra_reruns_impl-011_jira__project_risk_assessment.json`。

- sprint_adoption_rate：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_extra_reruns_impl-011_jira__project_risk_assessment.json`。

- complexity_risk_score：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_extra_reruns_impl-011_jira__project_risk_assessment.json`。

- scope_risk_score：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_extra_reruns_impl-011_jira__project_risk_assessment.json`。

- recommended_intervention：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_extra_reruns_impl-011_jira__project_risk_assessment.json`。

- strategic_priority_recommendation：agent SQL第1行起的指定表达式/实现块；old/new、偏移、SQL SHA-256完整记录于`records/021_extra_reruns_impl-011_jira__project_risk_assessment.json`。

## agent可见证据与不确定性

**只有通用策略说明**。

event55点名project risk assessment详细业务计算简化/默认，但未说明按type name还是type ID给价值权重；通用说明不能算本表该主因的具体披露。

最终报告原句（其适用范围按上文判定）：

> 合同非常广泛，本实现优先保证所有配置模型可执行；少数复杂分析并未完整实现合同中的每个指标/分支。尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。

扫描57个原始事件及最终result.md；完整可见输出命中位置、显式截断标记见 `records/021_trace_audit.json` index=36。所有原始事件均按id检查；代码在message中重复出现不当作解释理由，执行日志行数不当作已核实连接基数/字段语义。

| event | cause | 显式截断 |
|---|---|---|
| 8 | 7 | False |
| 20 | 19 | False |
| 22 | 21 | False |
| 24 | 23 | False |
| 32 | 31 | False |
| 36 | 35 | False |
| 38 | 37 | False |
| 42 | 41 | False |
| 44 | 43 | False |
| 46 | 45 | False |

## 原始数据一致性与查询

015的逐题原始数据核对提供背景；本次全部原件均只读，前后字节指纹另核对。impl-008/009/011/013的raw三侧一致。校准impl-030按agent留存raw，不能因initial与gold不同而一概不可评估。

核实查询条数（含失败尝试）：3；核实代价档：需要查业务说明。每张不超过5条。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/jira.duckdb`；记录：`records/021_queries.json`。

```sql
SELECT 'intermediate.int_jira__project_metrics' source,count(*) n FROM intermediate.int_jira__project_metrics UNION ALL SELECT 'staging.stg_jira__issue' source,count(*) n FROM staging.stg_jira__issue UNION ALL SELECT 'staging.stg_jira__issue_type' source,count(*) n FROM staging.stg_jira__issue_type UNION ALL SELECT 'staging.stg_jira__project' source,count(*) n FROM staging.stg_jira__project
```

失败：Parser Error: syntax error at or near "source"

LINE 1: SELECT 'intermediate.int_jira__project_metrics' source,count(*) n FROM intermediate.int_jira__project_metrics...
                                                        ^

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/jira.duckdb`；记录：`records/021_supplement_queries.json`。

```sql
SELECT 'intermediate.int_jira__project_metrics' source_name,count(*) n FROM intermediate.int_jira__project_metrics UNION ALL SELECT 'staging.stg_jira__issue' source_name,count(*) n FROM staging.stg_jira__issue UNION ALL SELECT 'staging.stg_jira__issue_type' source_name,count(*) n FROM staging.stg_jira__issue_type UNION ALL SELECT 'staging.stg_jira__project' source_name,count(*) n FROM staging.stg_jira__project
```

结果（列顺序["source_name", "n"]）：`[["intermediate.int_jira__project_metrics", 200], ["staging.stg_jira__issue", 8000], ["staging.stg_jira__issue_type", 700], ["staging.stg_jira__project", 193]]`

### 核实 3

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/jira.duckdb`；记录：`records/021_final_diagnostics.json`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE lower(t.issue_type_name) IN ('epic','story','bug')) weighted_names,count(*) FILTER(WHERE i.issue_type_id ILIKE '%epic%' OR i.issue_type_id ILIKE '%story%' OR i.issue_type_id ILIKE '%bug%') weighted_ids,count(*) FILTER(WHERE t.issue_type_id IS NULL) unmatched FROM staging.stg_jira__issue i LEFT JOIN staging.stg_jira__issue_type t USING(issue_type_id)
```

结果（列顺序["n", "weighted_names", "weighted_ids", "unmatched"]）：`[[8000, 4180, 0, 0]]`


## 固定时间与重跑

原始库只用read_only=True或READ_ONLY ATTACH；staging复制agent raw，其他层复制gold上游（CS）。所有写入在data/021_*私有副本。

留存结果同口径L0：193行/2525格；选定基线：193行/2525格。

共同固定时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-13 00:00:00+00'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-13'", "count": 0}]`。每组基线与单修使用完全相同的时间；跨组时间不同明确分列，不跨基线计算减少量。

| 实验 | L0–L3规模（包含键） | 整表首次匹配 |
|---|---|---|
| baseline | L0 193行/2525格；L1 193行/2525格；L2 193行/2525格；L3 193行/2525格 | 均未整表匹配 |
| whole_implementation_diagnostic | L0 0行/0格；L1 0行/0格；L2 0行/0格；L3 0行/0格 | L0 |
| type_id_instead_name | L0 193行/1947格；L1 193行/1947格；L2 193行/1947格；L3 193行/1947格 | 均未整表匹配 |
| unique_issue_types | L0 193行/2332格；L1 193行/2332格；L2 193行/2332格；L3 193行/2332格 | 均未整表匹配 |
| unique_components | L0 193行/2339格；L1 193行/2339格；L2 193行/2339格；L3 193行/2339格 | 均未整表匹配 |
| total_external_links | L0 193行/2332格；L1 193行/2332格；L2 193行/2332格；L3 193行/2332格 | 均未整表匹配 |
| sprint_adoption_rate | L0 193行/2332格；L1 193行/2332格；L2 193行/2332格；L3 193行/2332格 | 均未整表匹配 |
| complexity_risk_score | L0 193行/2336格；L1 193行/2336格；L2 193行/2336格；L3 193行/2336格 | 均未整表匹配 |
| scope_risk_score | L0 193行/2332格；L1 193行/2332格；L2 193行/2332格；L3 193行/2332格 | 均未整表匹配 |
| recommended_intervention | L0 193行/2332格；L1 193行/2332格；L2 193行/2332格；L3 193行/2332格 | 均未整表匹配 |
| strategic_priority_recommendation | L0 193行/2464格；L1 193行/2464格；L2 193行/2464格；L3 193行/2464格 | 均未整表匹配 |

不适用：主因/并列项不是U；未将完整实现替换当作U局部修复。

| 实验 | L0每列非零不一致数 |
|---|---|
| baseline | {"budget_impact_prediction": 180, "complexity_risk_score": 189, "delivered_value_points": 192, "estimated_project_value_points": 193, "primary_risk_driver": 176, "recommended_intervention": 193, "risk_category": 193, "scope_risk_score": 193, "sprint_adoption_rate": 193, "strategic_priority_recommendation": 61, "total_external_links": 193, "unique_components": 186, "unique_issue_types": 193, "value_delivery_percentage": 190} |
| whole_implementation_diagnostic | {} |
| type_id_instead_name | {"budget_impact_prediction": 177, "complexity_risk_score": 189, "primary_risk_driver": 176, "recommended_intervention": 193, "risk_category": 193, "scope_risk_score": 193, "sprint_adoption_rate": 193, "strategic_priority_recommendation": 61, "total_external_links": 193, "unique_components": 186, "unique_issue_types": 193} |
| unique_issue_types | {"budget_impact_prediction": 180, "complexity_risk_score": 189, "delivered_value_points": 192, "estimated_project_value_points": 193, "primary_risk_driver": 176, "recommended_intervention": 193, "risk_category": 193, "scope_risk_score": 193, "sprint_adoption_rate": 193, "strategic_priority_recommendation": 61, "total_external_links": 193, "unique_components": 186, "value_delivery_percentage": 190} |
| unique_components | {"budget_impact_prediction": 180, "complexity_risk_score": 189, "delivered_value_points": 192, "estimated_project_value_points": 193, "primary_risk_driver": 176, "recommended_intervention": 193, "risk_category": 193, "scope_risk_score": 193, "sprint_adoption_rate": 193, "strategic_priority_recommendation": 61, "total_external_links": 193, "unique_issue_types": 193, "value_delivery_percentage": 190} |
| total_external_links | {"budget_impact_prediction": 180, "complexity_risk_score": 189, "delivered_value_points": 192, "estimated_project_value_points": 193, "primary_risk_driver": 176, "recommended_intervention": 193, "risk_category": 193, "scope_risk_score": 193, "sprint_adoption_rate": 193, "strategic_priority_recommendation": 61, "unique_components": 186, "unique_issue_types": 193, "value_delivery_percentage": 190} |
| sprint_adoption_rate | {"budget_impact_prediction": 180, "complexity_risk_score": 189, "delivered_value_points": 192, "estimated_project_value_points": 193, "primary_risk_driver": 176, "recommended_intervention": 193, "risk_category": 193, "scope_risk_score": 193, "strategic_priority_recommendation": 61, "total_external_links": 193, "unique_components": 186, "unique_issue_types": 193, "value_delivery_percentage": 190} |
| complexity_risk_score | {"budget_impact_prediction": 180, "delivered_value_points": 192, "estimated_project_value_points": 193, "primary_risk_driver": 176, "recommended_intervention": 193, "risk_category": 193, "scope_risk_score": 193, "sprint_adoption_rate": 193, "strategic_priority_recommendation": 61, "total_external_links": 193, "unique_components": 186, "unique_issue_types": 193, "value_delivery_percentage": 190} |
| scope_risk_score | {"budget_impact_prediction": 180, "complexity_risk_score": 189, "delivered_value_points": 192, "estimated_project_value_points": 193, "primary_risk_driver": 176, "recommended_intervention": 193, "risk_category": 193, "sprint_adoption_rate": 193, "strategic_priority_recommendation": 61, "total_external_links": 193, "unique_components": 186, "unique_issue_types": 193, "value_delivery_percentage": 190} |
| recommended_intervention | {"budget_impact_prediction": 180, "complexity_risk_score": 189, "delivered_value_points": 192, "estimated_project_value_points": 193, "primary_risk_driver": 176, "risk_category": 193, "scope_risk_score": 193, "sprint_adoption_rate": 193, "strategic_priority_recommendation": 61, "total_external_links": 193, "unique_components": 186, "unique_issue_types": 193, "value_delivery_percentage": 190} |
| strategic_priority_recommendation | {"budget_impact_prediction": 180, "complexity_risk_score": 189, "delivered_value_points": 192, "estimated_project_value_points": 193, "primary_risk_driver": 176, "recommended_intervention": 193, "risk_category": 193, "scope_risk_score": 193, "sprint_adoption_rate": 193, "total_external_links": 193, "unique_components": 186, "unique_issue_types": 193, "value_delivery_percentage": 190} |

L1–L3的每列不一致数、单侧行、共同键超额行及全部L0–L3字段已逐项保存在每个重跑JSON的`comparison.levels`，与本表同属交付证据；不是仅列总差异。

先按行数减少量，再按格子数；重复键先抵消相同行，剩余按整行字典序固定配对。大表使用权重区间配对，与展开重复行的原算法12组逐字段测试一致。整段gold实现及混合原因替换不冒充单点U证据；失败、无改善或行数变差的候选不计参与因素。


## 规则问题

契约“按type”没有逐列source_expression。两种读法是A源映射未定，或O标准未实现类型权重。原始可见ID完全不含类别词，且类型表全部匹配、4180个类型名明确落入非默认权重，本次采用O，置信中。

## 证据路径与复现

- 精简材料包：`records/021_packages/021_impl-011_jira__project_risk_assessment.md`。
- 完整机械材料（可由prepare脚本重建）：`data/021_packages_work/021_impl-011_jira__project_risk_assessment/021_impl-011_jira__project_risk_assessment.json`。
- 重跑：`records/021_reruns_impl-011_jira__project_risk_assessment.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 重跑：`records/021_detailed_reruns_impl-011_jira__project_risk_assessment.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 重跑：`records/021_extra_reruns_impl-011_jira__project_risk_assessment.json`；上游来源、private_copy_tables、每项old/new/offset/SQL路径/SHA-256、原基线完整保留。
- 原始轨迹：`traces/dacomp_deimpl_prev.tar.gz`，事件定位见 `records/021_trace_audit.json`。
- 输入前指纹：`records/021_input_before.json`；后指纹与验证另见021记录。
- 执行环境：`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=data/005_tools:scripts /home/katherine/dac/.venv-openhands/bin/python -B`；调用本表重跑记录对应的021脚本，具体命令汇总见 `records/021_commands.txt`。
