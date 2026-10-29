# impl-003 / int_customer360__customer_behavior_analysis

## 结论

主要原因：**O**；把握：高；标记：无。

契约明确任一输入 NULL 则输出 NULL，agent 照做；gold least/greatest 忽略 NULL。

参与因素：last_activity=O。

不确定性四档：**看到了但没提**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-003_int_customer360__customer_behavior_analysis.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：5001/5001。本次固定控制下 baseline 行/格规模：4027/17590。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-003/docs/data_contract.yaml`；原文行段 821–913。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/intermediate/int_customer360__customer_behavior_analysis.sql`，L1–91；SHA-256 `1085d091326800df600d023637d63d6c56ea1d78fec0fa7357d574cf4146bad5`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/sql/intermediate/int_customer360__customer_behavior_analysis.sql`，L1–260；SHA-256 `f6a6528a1175438712646987758bb955f802a56f35a3d03076b681d4665abf09`。

first_touch：agent SQL L44，替换原片段如下。
```sql
case when m_created is null or s_created is null or z_created is null then null else least(m_created,s_created,z_created) end
```
替换为：
```sql
least(m_created,s_created,z_created)
```

last_activity：agent SQL L45，替换原片段如下。
```sql
case when m_updated is null or s_updated is null or z_updated is null then null else greatest(m_updated,s_updated,z_updated) end
```
替换为：
```sql
greatest(m_updated,s_updated,z_updated)
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-003_int_customer360__customer_behavior_analysis.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 0 条（上限5）；代价档：需要查业务说明。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 4027 | 17590 | {"account_age_days": 4027, "churn_risk_level": 1468, "customer_first_touchpoint": 4027, "customer_last_activity": 4027, "customer_maturity": 4027, "customer_segment": 7, "recommended_action": 7} | L0–L3均不匹配 |
| baseline | L1 | 4027 | 17590 | {"account_age_days": 4027, "churn_risk_level": 1468, "customer_first_touchpoint": 4027, "customer_last_activity": 4027, "customer_maturity": 4027, "customer_segment": 7, "recommended_action": 7} | L0–L3均不匹配 |
| baseline | L2 | 4027 | 17590 | {"account_age_days": 4027, "churn_risk_level": 1468, "customer_first_touchpoint": 4027, "customer_last_activity": 4027, "customer_maturity": 4027, "customer_segment": 7, "recommended_action": 7} | L0–L3均不匹配 |
| baseline | L3 | 4027 | 17590 | {"account_age_days": 4027, "churn_risk_level": 1468, "customer_first_touchpoint": 4027, "customer_last_activity": 4027, "customer_maturity": 4027, "customer_segment": 7, "recommended_action": 7} | L0–L3均不匹配 |
| first_touch | L0 | 4027 | 5252 | {"churn_risk_level": 1225, "customer_last_activity": 4027} | L0–L3均不匹配 |
| first_touch | L1 | 4027 | 5252 | {"churn_risk_level": 1225, "customer_last_activity": 4027} | L0–L3均不匹配 |
| first_touch | L2 | 4027 | 5252 | {"churn_risk_level": 1225, "customer_last_activity": 4027} | L0–L3均不匹配 |
| first_touch | L3 | 4027 | 5252 | {"churn_risk_level": 1225, "customer_last_activity": 4027} | L0–L3均不匹配 |
| last_activity | L0 | 4027 | 12095 | {"account_age_days": 4027, "customer_first_touchpoint": 4027, "customer_maturity": 4027, "customer_segment": 7, "recommended_action": 7} | L0–L3均不匹配 |
| last_activity | L1 | 4027 | 12095 | {"account_age_days": 4027, "customer_first_touchpoint": 4027, "customer_maturity": 4027, "customer_segment": 7, "recommended_action": 7} | L0–L3均不匹配 |
| last_activity | L2 | 4027 | 12095 | {"account_age_days": 4027, "customer_first_touchpoint": 4027, "customer_maturity": 4027, "customer_segment": 7, "recommended_action": 7} | L0–L3均不匹配 |
| last_activity | L3 | 4027 | 12095 | {"account_age_days": 4027, "customer_first_touchpoint": 4027, "customer_maturity": 4027, "customer_segment": 7, "recommended_action": 7} | L0–L3均不匹配 |

- first_touch（O，单处 SQL 改动）：行减少 0，格减少 12338。契约明确任一输入 NULL 则输出 NULL，agent 照做；gold least/greatest 忽略 NULL。

- last_activity（O，单处 SQL 改动）：行减少 0，格减少 5495。契约明确任一输入 NULL 则输出 NULL，agent 照做；gold least/greatest 忽略 NULL。

## agent 可见证据及不确定性

event 1 / message，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/1.json`，字段字符偏移 46248。

> int_customer360__customer_behavior_analysis
>       description: Customer behavior profile per resolved customer with cross-platform engagement, lifecycle metrics, and segmentation
>       grain: One row per source match key (marketo_lead_id, stripe_customer_id, zendesk_user_id) with non-null primary_email
>       source_models:
>       - intermediate.int_customer360__source_matches
>       - intermediate.int_customer360__marketo
>       - intermediate.int_customer360__stripe
>       - intermediate.int_custom

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

未遇到需要改变手册定义的问题。
