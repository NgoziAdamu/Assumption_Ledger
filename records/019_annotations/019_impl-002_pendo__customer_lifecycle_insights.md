# impl-002 / pendo__customer_lifecycle_insights

## 结论

主要原因：**D**；把握：中；标记：已披露。

高级派生字段用固定值代替规则。

参与因素：无经单修/诊断证实的额外因素。

不确定性四档：**针对本表的具体说明**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-002_pendo__customer_lifecycle_insights.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：898267/898267。本次固定控制下 baseline 行/格规模：895934/6356401。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-002/docs/data_contract.yaml`；原文行段 2038–2191。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/marts/customer_lifecycle_insights.sql`，L1–1；SHA-256 `8a4f3bb40d3789fc20328bf0452c4a45a59258ce2c1a8164efcba13e0c120841`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/sql/marts/customer_lifecycle_insights.sql`，L1–221；SHA-256 `0abe3468084ce0b932218151b4cac789661421987249e7124a72e11914bf51c5`。

customer_journey_stage：agent SQL L1，替换原片段如下。
```sql
'Maintenance' customer_journey_stage
```
替换为：
```sql
CASE WHEN DATE_DIFF('DAY', CAST(SUBSTRING(CAST(v.first_event_on AS TEXT), 1, 10) AS DATE), CURRENT_DATE) <= 30 THEN 'Onboarding' WHEN l.lifecycle_stage IN ('Growing User', 'Mature User') AND r.customer_value_tier IN ('High Value', 'Medium Value') THEN 'Growth' WHEN l.lifecycle_stage IN ('Power User', 'Mature User') AND r.rfm_segment IN ('Champions', 'Loyal Customers') THEN 'Maturity' WHEN l.churn_risk_level IN ('High Risk', 'Medium Risk') OR l.lifecycle_stage = 'At Risk' THEN 'Retention' WHEN l.lifecycle_stage = 'Churned' THEN 'Win-back' ELSE 'Maintenance' END AS customer_journey_stage
```

predicted_ltv_tier：agent SQL L1，替换原片段如下。
```sql
'Standard LTV' predicted_ltv_tier
```
替换为：
```sql
CASE WHEN l.lifecycle_stage IN ('Power User', 'Mature User') AND r.customer_value_tier = 'High Value' AND COALESCE(h.overall_health_score, 60) >= 70 THEN 'Very High LTV' WHEN (l.user_value_score >= 70 OR r.rfm_composite_score >= 4) AND l.churn_risk_level = 'Low Risk' THEN 'High LTV' WHEN l.lifecycle_stage IN ('Growing User', 'New User') AND r.predicted_clv_tier IN ('High CLV', 'Medium CLV') THEN 'Moderate LTV' WHEN l.churn_risk_level = 'High Risk' OR l.lifecycle_stage = 'Churned' THEN 'Low LTV' ELSE 'Standard LTV' END AS predicted_ltv_tier
```

engagement_velocity：agent SQL L1，替换原片段如下。
```sql
0::FLOAT engagement_velocity
```
替换为：
```sql
CASE WHEN v.count_active_days > 0 AND DATE_DIFF('DAY', CAST(SUBSTRING(CAST(v.first_event_on AS TEXT), 1, 10) AS DATE), CURRENT_DATE) > 0 THEN CAST(v.count_active_days AS REAL) / DATE_DIFF('DAY', CAST(SUBSTRING(CAST(v.first_event_on AS TEXT), 1, 10) AS DATE), CURRENT_DATE) ELSE 0 END AS engagement_velocity
```

usage_trend：agent SQL L1，替换原片段如下。
```sql
'Declining' usage_trend
```
替换为：
```sql
CASE WHEN v.average_daily_events > CAST(v.sum_events AS REAL) / NULLIF(v.count_active_days, 0) * 1.2 THEN 'Accelerating' WHEN v.average_daily_events > CAST(v.sum_events AS REAL) / NULLIF(v.count_active_days, 0) * 0.8 THEN 'Stable' ELSE 'Declining' END AS usage_trend
```

customer_importance_level：agent SQL L1，替换原片段如下。
```sql
'Standard' customer_importance_level
```
替换为：
```sql
CASE WHEN customer_segment_label IN ('Star Customer', 'Key Account') AND predicted_ltv_tier = 'Very High LTV' THEN 'Critical' WHEN comprehensive_customer_value >= 80 AND customer_journey_stage IN ('Growth', 'Maturity') THEN 'High' WHEN comprehensive_customer_value >= 60 OR customer_segment_label IN ('Rising Star', 'Fresh Prospect') THEN 'Medium' WHEN l.needs_attention OR customer_journey_stage = 'Retention' THEN 'At Risk' ELSE 'Standard' END AS customer_importance_level
```

investment_expectation：agent SQL L1，替换原片段如下。
```sql
'Standard ROI - Maintenance' investment_expectation
```
替换为：
```sql
CASE WHEN customer_segment_label = 'Star Customer' THEN 'High ROI - Advocacy & Expansion' WHEN customer_segment_label = 'Key Account' THEN 'High ROI - Retention & Upsell' WHEN customer_segment_label = 'Rising Star' THEN 'Medium ROI - Growth Investment' WHEN customer_segment_label = 'Fresh Prospect' THEN 'Medium ROI - Onboarding Investment' WHEN customer_segment_label = 'Save Immediately' THEN 'Low ROI - Retention Cost' WHEN customer_segment_label = 'Lost Customer' THEN 'Negative ROI - Win-back Cost' ELSE 'Standard ROI - Maintenance' END AS investment_expectation
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-002_pendo__customer_lifecycle_insights.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 0 条（上限5）；代价档：需要查业务说明。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 895934 | 6356401 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "customer_journey_stage": 895934, "predicted_ltv_tier": 895934, "engagement_velocity": 895934, "usage_trend": 895934, "customer_importance_level": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |
| baseline | L1 | 895934 | 6356401 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "customer_journey_stage": 895934, "predicted_ltv_tier": 895934, "engagement_velocity": 895934, "usage_trend": 895934, "customer_importance_level": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |
| baseline | L2 | 895934 | 5703915 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "customer_journey_stage": 895934, "predicted_ltv_tier": 895934, "engagement_velocity": 243448, "usage_trend": 895934, "customer_importance_level": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |
| baseline | L3 | 895934 | 5703915 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "customer_journey_stage": 895934, "predicted_ltv_tier": 895934, "engagement_velocity": 243448, "usage_trend": 895934, "customer_importance_level": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |
| customer_journey_stage | L0 | 895934 | 5460467 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "predicted_ltv_tier": 895934, "engagement_velocity": 895934, "usage_trend": 895934, "customer_importance_level": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |
| customer_journey_stage | L1 | 895934 | 5460467 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "predicted_ltv_tier": 895934, "engagement_velocity": 895934, "usage_trend": 895934, "customer_importance_level": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |
| customer_journey_stage | L2 | 895934 | 4807981 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "predicted_ltv_tier": 895934, "engagement_velocity": 243448, "usage_trend": 895934, "customer_importance_level": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |
| customer_journey_stage | L3 | 895934 | 4807981 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "predicted_ltv_tier": 895934, "engagement_velocity": 243448, "usage_trend": 895934, "customer_importance_level": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |
| predicted_ltv_tier | L0 | 895934 | 5460467 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "customer_journey_stage": 895934, "engagement_velocity": 895934, "usage_trend": 895934, "customer_importance_level": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |
| predicted_ltv_tier | L1 | 895934 | 5460467 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "customer_journey_stage": 895934, "engagement_velocity": 895934, "usage_trend": 895934, "customer_importance_level": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |
| predicted_ltv_tier | L2 | 895934 | 4807981 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "customer_journey_stage": 895934, "engagement_velocity": 243448, "usage_trend": 895934, "customer_importance_level": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |
| predicted_ltv_tier | L3 | 895934 | 4807981 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "customer_journey_stage": 895934, "engagement_velocity": 243448, "usage_trend": 895934, "customer_importance_level": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |
| engagement_velocity | L0 | 895934 | 5460467 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "customer_journey_stage": 895934, "predicted_ltv_tier": 895934, "usage_trend": 895934, "customer_importance_level": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |
| engagement_velocity | L1 | 895934 | 5460467 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "customer_journey_stage": 895934, "predicted_ltv_tier": 895934, "usage_trend": 895934, "customer_importance_level": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |
| engagement_velocity | L2 | 895934 | 5460467 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "customer_journey_stage": 895934, "predicted_ltv_tier": 895934, "usage_trend": 895934, "customer_importance_level": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |
| engagement_velocity | L3 | 895934 | 5460467 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "customer_journey_stage": 895934, "predicted_ltv_tier": 895934, "usage_trend": 895934, "customer_importance_level": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |
| usage_trend | L0 | 895934 | 5460467 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "customer_journey_stage": 895934, "predicted_ltv_tier": 895934, "engagement_velocity": 895934, "customer_importance_level": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |
| usage_trend | L1 | 895934 | 5460467 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "customer_journey_stage": 895934, "predicted_ltv_tier": 895934, "engagement_velocity": 895934, "customer_importance_level": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |
| usage_trend | L2 | 895934 | 4807981 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "customer_journey_stage": 895934, "predicted_ltv_tier": 895934, "engagement_velocity": 243448, "customer_importance_level": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |
| usage_trend | L3 | 895934 | 4807981 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "customer_journey_stage": 895934, "predicted_ltv_tier": 895934, "engagement_velocity": 243448, "customer_importance_level": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |
| customer_importance_level | L0 | 895934 | 5460467 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "customer_journey_stage": 895934, "predicted_ltv_tier": 895934, "engagement_velocity": 895934, "usage_trend": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |
| customer_importance_level | L1 | 895934 | 5460467 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "customer_journey_stage": 895934, "predicted_ltv_tier": 895934, "engagement_velocity": 895934, "usage_trend": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |
| customer_importance_level | L2 | 895934 | 4807981 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "customer_journey_stage": 895934, "predicted_ltv_tier": 895934, "engagement_velocity": 243448, "usage_trend": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |
| customer_importance_level | L3 | 895934 | 4807981 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "customer_journey_stage": 895934, "predicted_ltv_tier": 895934, "engagement_velocity": 243448, "usage_trend": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |
| investment_expectation | L0 | 895934 | 6356401 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "customer_journey_stage": 895934, "predicted_ltv_tier": 895934, "engagement_velocity": 895934, "usage_trend": 895934, "customer_importance_level": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |
| investment_expectation | L1 | 895934 | 6356401 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "customer_journey_stage": 895934, "predicted_ltv_tier": 895934, "engagement_velocity": 895934, "usage_trend": 895934, "customer_importance_level": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |
| investment_expectation | L2 | 895934 | 5703915 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "customer_journey_stage": 895934, "predicted_ltv_tier": 895934, "engagement_velocity": 243448, "usage_trend": 895934, "customer_importance_level": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |
| investment_expectation | L3 | 895934 | 5703915 | {"customer_segment_label": 895934, "recommended_next_action": 84863, "customer_journey_stage": 895934, "predicted_ltv_tier": 895934, "engagement_velocity": 243448, "usage_trend": 895934, "customer_importance_level": 895934, "investment_expectation": 895934} | L0–L3均不匹配 |

- customer_journey_stage（D，单处 SQL 改动）：行减少 0，格减少 895934。高级派生字段用固定值代替规则。

- predicted_ltv_tier（D，单处 SQL 改动）：行减少 0，格减少 895934。高级派生字段用固定值代替规则。

- engagement_velocity（D，单处 SQL 改动）：行减少 0，格减少 895934。高级派生字段用固定值代替规则。

- usage_trend（D，单处 SQL 改动）：行减少 0，格减少 895934。高级派生字段用固定值代替规则。

- customer_importance_level（D，单处 SQL 改动）：行减少 0，格减少 895934。高级派生字段用固定值代替规则。

- investment_expectation（D，单处 SQL 改动）：行减少 0，格减少 0。高级派生字段用固定值代替规则。

## agent 可见证据及不确定性

event 59 / args.final_thought，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，字段字符偏移 1215。

> Several complex outputs remain simplified relative to the detailed contract: product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations; the data-quality report is summary-only; RFM account-level metrics are NULL placeholders; and advanced marts such as lifecycle insights and the executive dashboard use abbreviated/defaulted derivations.

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

错误点粒度存在两种读法：每个占位输出列分别算一处，或将同一遗漏聚合/规则模块视为一个降级错误点。本次以模块为错误点，列出全部可见占位及残余列统计，以局部恢复模块内表达式/来源证明贡献；没有用整份 gold SQL 替换来宣称因果成立。未逐一补齐全部占位列，不能据局部修法宣称已覆盖模块内所有修复。若后续决定按列拆分，需重新比较这些因素的贡献排序。
