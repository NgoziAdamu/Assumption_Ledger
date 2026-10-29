# impl-002 / pendo__executive_dashboard_metrics

## 结论

主要原因：**D**；把握：中；标记：已披露。

dashboard 账户汇总列 NULL 占位；恢复 account 上游的 feature adoption 平均。

参与因素：无经单修/诊断证实的额外因素。

不确定性四档：**针对本表的具体说明**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-002_pendo__executive_dashboard_metrics.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：1/1。本次固定控制下 baseline 行/格规模：1/7。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-002/docs/data_contract.yaml`；原文行段 2192–2281。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/marts/executive_dashboard_metrics.sql`，L1–1；SHA-256 `d9b8df10fcff156c42cb77d1a2a715a41df5ef562f88e6e5033080a61e8130c4`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/sql/marts/executive_dashboard_metrics.sql`，L1–206；SHA-256 `790e2be9a166b33af95c5225fd414083c86175e3e045e8fe5175880b56cb20c6`。

avg_platform_health_score：agent SQL L1，替换原片段如下。
```sql
NULL::DOUBLE avg_platform_health_score
```
替换为：
```sql
(SELECT avg(overall_health_score) FROM intermediate.int_pendo__product_health_metrics) AS avg_platform_health_score
```

avg_feature_adoption：agent SQL L1，替换原片段如下。
```sql
NULL::DOUBLE avg_feature_adoption
```
替换为：
```sql
(SELECT avg(v) FROM (SELECT ah.account_id,ah.first_visit_at,ah.last_visit_at,max(ph.feature_adoption_rate) v FROM staging.stg_pendo__account_history ah LEFT JOIN intermediate.int_pendo__product_health_metrics ph ON ah.account_id=ph.account_id GROUP BY 1,2,3)) AS avg_feature_adoption
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-002_pendo__executive_dashboard_metrics.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 0 条（上限5）；代价档：需要查业务说明。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 1 | 7 | {"avg_feature_adoption": 1, "avg_platform_health_score": 1, "avg_retention_rate": 1, "low_risk_accounts": 1, "medium_risk_accounts": 1, "overall_business_health_score": 1, "primary_alert_status": 1} | L0–L3均不匹配 |
| baseline | L1 | 1 | 7 | {"avg_feature_adoption": 1, "avg_platform_health_score": 1, "avg_retention_rate": 1, "low_risk_accounts": 1, "medium_risk_accounts": 1, "overall_business_health_score": 1, "primary_alert_status": 1} | L0–L3均不匹配 |
| baseline | L2 | 1 | 7 | {"avg_feature_adoption": 1, "avg_platform_health_score": 1, "avg_retention_rate": 1, "low_risk_accounts": 1, "medium_risk_accounts": 1, "overall_business_health_score": 1, "primary_alert_status": 1} | L0–L3均不匹配 |
| baseline | L3 | 1 | 7 | {"avg_feature_adoption": 1, "avg_platform_health_score": 1, "avg_retention_rate": 1, "low_risk_accounts": 1, "medium_risk_accounts": 1, "overall_business_health_score": 1, "primary_alert_status": 1} | L0–L3均不匹配 |
| avg_platform_health_score | L0 | 1 | 7 | {"avg_feature_adoption": 1, "avg_platform_health_score": 1, "avg_retention_rate": 1, "low_risk_accounts": 1, "medium_risk_accounts": 1, "overall_business_health_score": 1, "primary_alert_status": 1} | L0–L3均不匹配 |
| avg_platform_health_score | L1 | 1 | 7 | {"avg_feature_adoption": 1, "avg_platform_health_score": 1, "avg_retention_rate": 1, "low_risk_accounts": 1, "medium_risk_accounts": 1, "overall_business_health_score": 1, "primary_alert_status": 1} | L0–L3均不匹配 |
| avg_platform_health_score | L2 | 1 | 7 | {"avg_feature_adoption": 1, "avg_platform_health_score": 1, "avg_retention_rate": 1, "low_risk_accounts": 1, "medium_risk_accounts": 1, "overall_business_health_score": 1, "primary_alert_status": 1} | L0–L3均不匹配 |
| avg_platform_health_score | L3 | 1 | 7 | {"avg_feature_adoption": 1, "avg_platform_health_score": 1, "avg_retention_rate": 1, "low_risk_accounts": 1, "medium_risk_accounts": 1, "overall_business_health_score": 1, "primary_alert_status": 1} | L0–L3均不匹配 |
| avg_feature_adoption | L0 | 1 | 6 | {"avg_platform_health_score": 1, "avg_retention_rate": 1, "low_risk_accounts": 1, "medium_risk_accounts": 1, "overall_business_health_score": 1, "primary_alert_status": 1} | L0–L3均不匹配 |
| avg_feature_adoption | L1 | 1 | 6 | {"avg_platform_health_score": 1, "avg_retention_rate": 1, "low_risk_accounts": 1, "medium_risk_accounts": 1, "overall_business_health_score": 1, "primary_alert_status": 1} | L0–L3均不匹配 |
| avg_feature_adoption | L2 | 1 | 6 | {"avg_platform_health_score": 1, "avg_retention_rate": 1, "low_risk_accounts": 1, "medium_risk_accounts": 1, "overall_business_health_score": 1, "primary_alert_status": 1} | L0–L3均不匹配 |
| avg_feature_adoption | L3 | 1 | 6 | {"avg_platform_health_score": 1, "avg_retention_rate": 1, "low_risk_accounts": 1, "medium_risk_accounts": 1, "overall_business_health_score": 1, "primary_alert_status": 1} | L0–L3均不匹配 |

- avg_platform_health_score（D，单处 SQL 改动）：行减少 0，格减少 0。平台健康分直接 NULL 占位。

- avg_feature_adoption（D，单处 SQL 改动）：行减少 0，格减少 1。dashboard 账户汇总列 NULL 占位；恢复 account 上游的 feature adoption 平均。

## agent 可见证据及不确定性

event 59 / args.final_thought，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/59.json`，字段字符偏移 1215。

> Several complex outputs remain simplified relative to the detailed contract: product-health and conversion-funnel calculations omit prescribed breakdowns/full derivations; the data-quality report is summary-only; RFM account-level metrics are NULL placeholders; and advanced marts such as lifecycle insights and the executive dashboard use abbreviated/defaulted derivations.

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

错误点粒度存在两种读法：每个占位输出列分别算一处，或将同一遗漏聚合/规则模块视为一个降级错误点。本次以模块为错误点，列出全部可见占位及残余列统计，以局部恢复模块内表达式/来源证明贡献；没有用整份 gold SQL 替换来宣称因果成立。未逐一补齐全部占位列，不能据局部修法宣称已覆盖模块内所有修复。若后续决定按列拆分，需重新比较这些因素的贡献排序。
