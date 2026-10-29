# impl-003 / int_customer360__risk_assessment

## 结论

主要原因：**C**；把握：中；标记：无。

只显式转换类型，验证前导0表示差异；与展开S修法为同一错误点。

参与因素：primary_risk_factor=A；recommended_intervention=A。

不确定性四档：**看到了但没提**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-003_int_customer360__risk_assessment.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：6947/6947。本次固定控制下 baseline 行/格规模：6947/9180。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-003/docs/data_contract.yaml`；原文行段 1038–1202。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/intermediate/int_customer360__risk_assessment.sql`，L1–58；SHA-256 `ad085dc59b443e907eb1530d7267c93aa420c9872a6791580a24b61f8df6f516`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/sql/intermediate/int_customer360__risk_assessment.sql`，L1–340；SHA-256 `bd40ddcf0a483136036f53e3ddc29adc291efbebd46b1f3bf04c68d12e5186cf`。

primary_risk_factor：agent SQL L34，替换原片段如下。
```sql
case when payment_behavior_risk>0 then 'Payment Issues' when activity_decline_risk>0 then 'Engagement Decline' when lifecycle_transition_risk>0 then 'Lifecycle Transition' when revenue_at_risk_score>0 then 'High Value at Risk' when support_engagement_risk>0 then 'Support Issues' when email_engagement_risk>0 then 'Communication Breakdown' else 'Standard Monitoring' end as primary_risk_factor
```
替换为：
```sql
CASE WHEN payment_behavior_risk >= 3 THEN 'Payment Issues' WHEN activity_decline_risk >= 2 AND platform_abandonment_risk >= 1 THEN 'Engagement Decline' WHEN lifecycle_transition_risk >= 2 THEN 'Lifecycle Transition' WHEN revenue_at_risk_score >= 3 THEN 'High Value at Risk' WHEN support_engagement_risk >= 2 THEN 'Support Issues' WHEN email_engagement_risk >= 1 AND activity_decline_risk >= 1 THEN 'Communication Breakdown' ELSE 'Standard Monitoring' END AS primary_risk_factor
```

recommended_intervention：agent SQL L38，替换原片段如下。
```sql
case when payment_behavior_risk>0 then 'Account Management Call' when activity_decline_risk>=2 and estimated_customer_ltv>=5000 then 'Executive Outreach' when support_engagement_risk>0 then 'Customer Success Check-in' when email_engagement_risk>0 then 'Personalized Email Campaign' when platform_abandonment_risk>0 then 'Product Adoption Workshop' when lifecycle_stage is not null then 'Lifecycle-specific Campaign' else 'Automated Monitoring' end as recommended_intervention
```
替换为：
```sql
CASE WHEN payment_behavior_risk >= 3 THEN 'Account Management Call' WHEN activity_decline_risk >= 2 AND estimated_customer_ltv >= 5000 THEN 'Executive Outreach' WHEN support_engagement_risk >= 2 THEN 'Customer Success Check-in' WHEN email_engagement_risk >= 2 THEN 'Personalized Email Campaign' WHEN platform_abandonment_risk >= 2 THEN 'Product Adoption Workshop' WHEN lifecycle_transition_risk >= 2 THEN 'Lifecycle-specific Campaign' ELSE 'Automated Monitoring' END AS recommended_intervention
```

probability_type：agent SQL L39，替换原片段如下。
```sql
case when S>=8 then .30 when S>=5 then .60 when S>=3 then .80 when S>=1 then .90 else .95 end as intervention_success_probability
```
替换为：
```sql
case when S>=8 then .30 when S>=5 then .60 when S>=3 then .80 when S>=1 then .90 else .95 end::DECIMAL(3,2) AS intervention_success_probability
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-003_int_customer360__risk_assessment.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 0 条（上限5）；代价档：需要查业务说明。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

诊断：
```sql
SELECT typeof(intervention_success_probability) AS type,count(*) n FROM intermediate.int_customer360__risk_assessment GROUP BY ALL
```
结果（仅统计/类型）：`[["DECIMAL(2,2)", 6947]]`

诊断：
```sql
SELECT typeof(intervention_success_probability) AS type,count(*) n FROM intermediate.int_customer360__risk_assessment GROUP BY ALL
```
结果（仅统计/类型）：`[["DECIMAL(3,2)", 6947]]`

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 6947 | 9180 | {"intervention_roi": 561, "intervention_success_probability": 6947, "primary_risk_factor": 1111, "recommended_intervention": 561} | L0–L3均不匹配 |
| baseline | L1 | 1570 | 2233 | {"intervention_roi": 561, "primary_risk_factor": 1111, "recommended_intervention": 561} | L0–L3均不匹配 |
| baseline | L2 | 1570 | 2233 | {"intervention_roi": 561, "primary_risk_factor": 1111, "recommended_intervention": 561} | L0–L3均不匹配 |
| baseline | L3 | 1570 | 2233 | {"intervention_roi": 561, "primary_risk_factor": 1111, "recommended_intervention": 561} | L0–L3均不匹配 |
| primary_risk_factor | L0 | 6947 | 8069 | {"intervention_roi": 561, "intervention_success_probability": 6947, "recommended_intervention": 561} | L0–L3均不匹配 |
| primary_risk_factor | L1 | 561 | 1122 | {"intervention_roi": 561, "recommended_intervention": 561} | L0–L3均不匹配 |
| primary_risk_factor | L2 | 561 | 1122 | {"intervention_roi": 561, "recommended_intervention": 561} | L0–L3均不匹配 |
| primary_risk_factor | L3 | 561 | 1122 | {"intervention_roi": 561, "recommended_intervention": 561} | L0–L3均不匹配 |
| recommended_intervention | L0 | 6947 | 8058 | {"intervention_success_probability": 6947, "primary_risk_factor": 1111} | L0–L3均不匹配 |
| recommended_intervention | L1 | 1111 | 1111 | {"primary_risk_factor": 1111} | L0–L3均不匹配 |
| recommended_intervention | L2 | 1111 | 1111 | {"primary_risk_factor": 1111} | L0–L3均不匹配 |
| recommended_intervention | L3 | 1111 | 1111 | {"primary_risk_factor": 1111} | L0–L3均不匹配 |
| intervention_success_probability | L0 | 1570 | 2233 | {"intervention_roi": 561, "primary_risk_factor": 1111, "recommended_intervention": 561} | L0–L3均不匹配 |
| intervention_success_probability | L1 | 1570 | 2233 | {"intervention_roi": 561, "primary_risk_factor": 1111, "recommended_intervention": 561} | L0–L3均不匹配 |
| intervention_success_probability | L2 | 1570 | 2233 | {"intervention_roi": 561, "primary_risk_factor": 1111, "recommended_intervention": 561} | L0–L3均不匹配 |
| intervention_success_probability | L3 | 1570 | 2233 | {"intervention_roi": 561, "primary_risk_factor": 1111, "recommended_intervention": 561} | L0–L3均不匹配 |
| probability_type | L0 | 1570 | 2233 | {"intervention_roi": 561, "primary_risk_factor": 1111, "recommended_intervention": 561} | L0–L3均不匹配 |
| probability_type | L1 | 1570 | 2233 | {"intervention_roi": 561, "primary_risk_factor": 1111, "recommended_intervention": 561} | L0–L3均不匹配 |
| probability_type | L2 | 1570 | 2233 | {"intervention_roi": 561, "primary_risk_factor": 1111, "recommended_intervention": 561} | L0–L3均不匹配 |
| probability_type | L3 | 1570 | 2233 | {"intervention_roi": 561, "primary_risk_factor": 1111, "recommended_intervention": 561} | L0–L3均不匹配 |

- primary_risk_factor（A，单处 SQL 改动）：行减少 0，格减少 1111。契约给出类别优先级，但未完整规定触发阈值；agent 与 gold 采用不同阈值。

- recommended_intervention（A，单处 SQL 改动）：行减少 0，格减少 1122。契约给出类别优先级，但未完整规定触发阈值；agent 与 gold 采用不同阈值。

- probability_type（C，单处 SQL 改动）：行减少 5377，格减少 6947。只显式转换类型，验证前导0表示差异；与展开S修法为同一错误点。

## agent 可见证据及不确定性

event 1 / message，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/1.json`，字段字符偏移 70338。

> int_customer360__risk_assessment
>       description: Multi-dimensional customer risk assessment derived from behavior, lifecycle, payment, and support signals with computed scores, classifications, flags, interventions, ROI, and timestamp
>       grain: One row per intermediate.int_customer360__customer_behavior_analysis record with non-null primary_email
>       source_models:
>       - intermediate.int_customer360__customer_behavior_analysis
>       - intermediate.int_customer360__customer_lifecycle_me

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

probability 的 .30 与 0.30 数值相同，但契约显式要求 DECIMAL(3,2)，agent 字面量推断 DECIMAL(2,2)，L0 表示不同；按 C。其他风险分类只给优先级、未完整给阈值，按 A。两种概率修法同源，不重复计为参与因素。
