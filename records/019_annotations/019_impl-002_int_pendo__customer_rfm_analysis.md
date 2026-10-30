# impl-002 / int_pendo__customer_rfm_analysis

## 结论

主要原因：**A**；把握：中；标记：已披露（参与因素 D：account 级 5 列占位，event 59）。

契约未给出完整 segment→文本/CLV 档位映射；不把 gold 的具体文本当要求。

参与因素：predicted_clv_tier=A；action_priority=A；account_total_visitors=D；account_high_value_ratio=D；account_top_segment_ratio=D；account_at_risk_ratio=D；account_avg_rfm_score=D。

不确定性四档：**看到了但没提**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-002_int_pendo__customer_rfm_analysis.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：7977/7977。本次固定控制下 baseline 行/格规模：7977/60241。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-002/docs/data_contract.yaml`；原文行段 772–854。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-002/agent/dacomp-de-impl-002/sql/intermediate/int_pendo__customer_rfm_analysis.sql`，L1–1；SHA-256 `3bccd611de1fbb0d27214469fe32a9afceccfcdf5e4e05e653c1df95cc69e48b`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-002/sql/intermediate/int_pendo__customer_rfm_analysis.sql`，L1–250；SHA-256 `e5f99cf0e42879c06596c0eb20df27fc7d24a49a0dfd174c945d14a4a3a05eca`。

recommended_strategy：agent SQL L1，替换原片段如下。
```sql
CASE WHEN rfm_segment IN ('Champions','Loyal Customers') THEN 'Reward loyalty and advocate' WHEN rfm_segment IN ('At Risk','Cannot Be Retrieved','Hibernating') THEN 'Re-engage customer' ELSE 'Standard engagement tactics' END recommended_strategy
```
替换为：
```sql
CASE rfm_segment WHEN 'Champions' THEN 'Reward them. They can become early adopters for new features and advocates.' WHEN 'Loyal Customers' THEN 'Upsell higher value products. Ask for reviews and referrals.' WHEN 'Potential Loyalists' THEN 'Offer membership/loyalty programs. Recommend complementary features.' WHEN 'New Customers' THEN 'Provide onboarding support. Start building relationships.' WHEN 'Promising' THEN 'Offer free trials of premium features. Engage them with content.' WHEN 'Customers Needing Attention' THEN 'Send personalized emails. Offer limited time offers.' WHEN 'About to Sleep' THEN 'Provide helpful resources. Send re-engagement campaigns.' WHEN 'At Risk' THEN 'Send win-back campaigns. Conduct exit interviews.' WHEN 'Cannot Be Retrieved' THEN 'Conduct customer research. Focus retention efforts elsewhere.' WHEN 'Hibernating' THEN 'Offer other relevant products. Send special offers to re-activate.' ELSE 'Standard engagement tactics.' END AS recommended_strategy
```

predicted_clv_tier：agent SQL L1，替换原片段如下。
```sql
CASE WHEN rfm_segment IN ('Champions','Loyal Customers') AND customer_lifetime_days>180 THEN 'Very High CLV' WHEN rfm_segment IN ('Champions','Loyal Customers') THEN 'High CLV' WHEN rfm_segment IN ('Potential Loyalists','Promising') THEN 'Medium CLV' ELSE 'Low CLV' END predicted_clv_tier
```
替换为：
```sql
CASE WHEN rfm_segment IN ('Champions', 'Loyal Customers') AND customer_lifetime_days > 180 THEN 'Very High CLV' WHEN rfm_segment IN ('Champions', 'Loyal Customers', 'Potential Loyalists') THEN 'High CLV' WHEN rfm_segment IN ('Promising', 'New Customers') THEN 'Medium CLV' WHEN rfm_segment IN ('Customers Needing Attention', 'About to Sleep', 'Hibernating') THEN 'Low CLV' ELSE 'Minimal CLV' END AS predicted_clv_tier
```

action_priority：agent SQL L1，替换原片段如下。
```sql
CASE WHEN rfm_segment IN ('Champions','Loyal Customers') THEN 'Retention & Advocacy' WHEN rfm_segment IN ('Potential Loyalists','Promising') THEN 'Growth & Upsell' WHEN rfm_segment='New Customers' THEN 'Onboarding & Education' WHEN rfm_segment IN ('At Risk','Cannot Be Retrieved','Hibernating') THEN 'Re-engagement' ELSE 'Monitor' END action_priority
```
替换为：
```sql
CASE WHEN rfm_segment IN ('Champions', 'Loyal Customers') THEN 'Retention & Advocacy' WHEN rfm_segment IN ('Potential Loyalists', 'Promising') THEN 'Growth & Upsell' WHEN rfm_segment = 'New Customers' THEN 'Onboarding & Education' WHEN rfm_segment IN ('Customers Needing Attention', 'About to Sleep') THEN 'Re-engagement' WHEN rfm_segment IN ('At Risk', 'Cannot Be Retrieved') THEN 'Win-back or Deprioritize' WHEN rfm_segment = 'Hibernating' THEN 'Reactivation' ELSE 'Monitor' END AS action_priority
```

account_total_visitors：agent SQL L1，替换原片段如下。
```sql
CAST(NULL AS BIGINT) account_total_visitors
```
替换为：
```sql
(SELECT count(*) FROM z az WHERE az.account_id=z.account_id) AS account_total_visitors
```

account_high_value_ratio：agent SQL L1，替换原片段如下。
```sql
CAST(NULL AS FLOAT) account_high_value_ratio
```
替换为：
```sql
(SELECT count(*) FILTER(WHERE az.customer_value_tier='High Value')::FLOAT/count(*) FROM z az WHERE az.account_id=z.account_id) AS account_high_value_ratio
```

account_top_segment_ratio：agent SQL L1，替换原片段如下。
```sql
CAST(NULL AS FLOAT) account_top_segment_ratio
```
替换为：
```sql
(SELECT count(*) FILTER(WHERE az.rfm_segment IN ('Champions','Loyal Customers'))::FLOAT/count(*) FROM z az WHERE az.account_id=z.account_id) AS account_top_segment_ratio
```

account_at_risk_ratio：agent SQL L1，替换原片段如下。
```sql
CAST(NULL AS FLOAT) account_at_risk_ratio
```
替换为：
```sql
(SELECT count(*) FILTER(WHERE az.rfm_segment IN ('At Risk','Cannot Be Retrieved'))::FLOAT/count(*) FROM z az WHERE az.account_id=z.account_id) AS account_at_risk_ratio
```

account_avg_rfm_score：agent SQL L1，替换原片段如下。
```sql
CAST(NULL AS DOUBLE) account_avg_rfm_score
```
替换为：
```sql
(SELECT avg(az.rfm_composite_score) FROM z az WHERE az.account_id=z.account_id) AS account_avg_rfm_score
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-002_int_pendo__customer_rfm_analysis.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 0 条（上限5）；代价档：需要查业务说明。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 7977 | 60241 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "action_priority": 7915, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |
| baseline | L1 | 7977 | 60241 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "action_priority": 7915, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |
| baseline | L2 | 7977 | 60241 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "action_priority": 7915, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |
| baseline | L3 | 7977 | 60241 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "action_priority": 7915, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |
| recommended_strategy | L0 | 7976 | 52264 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "action_priority": 7915, "predicted_clv_tier": 7239} | L0–L3均不匹配 |
| recommended_strategy | L1 | 7976 | 52264 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "action_priority": 7915, "predicted_clv_tier": 7239} | L0–L3均不匹配 |
| recommended_strategy | L2 | 7976 | 52264 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "action_priority": 7915, "predicted_clv_tier": 7239} | L0–L3均不匹配 |
| recommended_strategy | L3 | 7976 | 52264 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "action_priority": 7915, "predicted_clv_tier": 7239} | L0–L3均不匹配 |
| predicted_clv_tier | L0 | 7977 | 53002 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "action_priority": 7915, "recommended_strategy": 7977} | L0–L3均不匹配 |
| predicted_clv_tier | L1 | 7977 | 53002 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "action_priority": 7915, "recommended_strategy": 7977} | L0–L3均不匹配 |
| predicted_clv_tier | L2 | 7977 | 53002 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "action_priority": 7915, "recommended_strategy": 7977} | L0–L3均不匹配 |
| predicted_clv_tier | L3 | 7977 | 53002 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "action_priority": 7915, "recommended_strategy": 7977} | L0–L3均不匹配 |
| action_priority | L0 | 7977 | 52326 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |
| action_priority | L1 | 7977 | 52326 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |
| action_priority | L2 | 7977 | 52326 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |
| action_priority | L3 | 7977 | 52326 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |
| account_total_visitors | L0 | 7977 | 53374 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 555, "action_priority": 7915, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |
| account_total_visitors | L1 | 7977 | 53374 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 555, "action_priority": 7915, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |
| account_total_visitors | L2 | 7977 | 53374 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 555, "action_priority": 7915, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |
| account_total_visitors | L3 | 7977 | 53374 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 555, "action_priority": 7915, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |
| account_high_value_ratio | L0 | 7977 | 53374 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 555, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "action_priority": 7915, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |
| account_high_value_ratio | L1 | 7977 | 53374 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 555, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "action_priority": 7915, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |
| account_high_value_ratio | L2 | 7977 | 53374 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 555, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "action_priority": 7915, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |
| account_high_value_ratio | L3 | 7977 | 53374 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 555, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "action_priority": 7915, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |
| account_top_segment_ratio | L0 | 7977 | 53374 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 555, "account_total_visitors": 7422, "action_priority": 7915, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |
| account_top_segment_ratio | L1 | 7977 | 53374 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 555, "account_total_visitors": 7422, "action_priority": 7915, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |
| account_top_segment_ratio | L2 | 7977 | 53374 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 555, "account_total_visitors": 7422, "action_priority": 7915, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |
| account_top_segment_ratio | L3 | 7977 | 53374 | {"account_at_risk_ratio": 7422, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 555, "account_total_visitors": 7422, "action_priority": 7915, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |
| account_at_risk_ratio | L0 | 7977 | 53374 | {"account_at_risk_ratio": 555, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "action_priority": 7915, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |
| account_at_risk_ratio | L1 | 7977 | 53374 | {"account_at_risk_ratio": 555, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "action_priority": 7915, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |
| account_at_risk_ratio | L2 | 7977 | 53374 | {"account_at_risk_ratio": 555, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "action_priority": 7915, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |
| account_at_risk_ratio | L3 | 7977 | 53374 | {"account_at_risk_ratio": 555, "account_avg_rfm_score": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "action_priority": 7915, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |
| account_avg_rfm_score | L0 | 7977 | 52819 | {"account_at_risk_ratio": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "action_priority": 7915, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |
| account_avg_rfm_score | L1 | 7977 | 52819 | {"account_at_risk_ratio": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "action_priority": 7915, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |
| account_avg_rfm_score | L2 | 7977 | 52819 | {"account_at_risk_ratio": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "action_priority": 7915, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |
| account_avg_rfm_score | L3 | 7977 | 52819 | {"account_at_risk_ratio": 7422, "account_high_value_ratio": 7422, "account_top_segment_ratio": 7422, "account_total_visitors": 7422, "action_priority": 7915, "predicted_clv_tier": 7239, "recommended_strategy": 7977} | L0–L3均不匹配 |

- recommended_strategy（A，单处 SQL 改动）：行减少 1，格减少 7977。契约未给出完整 segment→文本/CLV 档位映射；不把 gold 的具体文本当要求。

- predicted_clv_tier（A，单处 SQL 改动）：行减少 0，格减少 7239。契约未给出完整 segment→文本/CLV 档位映射；不把 gold 的具体文本当要求。

- action_priority（A，单处 SQL 改动）：行减少 0，格减少 7915。契约未给出完整 segment→文本/CLV 档位映射；不把 gold 的具体文本当要求。

- account_total_visitors（D，单处 SQL 改动）：行减少 0，格减少 6867。account 聚合列 NULL 占位。

- account_high_value_ratio（D，单处 SQL 改动）：行减少 0，格减少 6867。account 聚合列 NULL 占位。

- account_top_segment_ratio（D，单处 SQL 改动）：行减少 0，格减少 6867。account 聚合列 NULL 占位。

- account_at_risk_ratio（D，单处 SQL 改动）：行减少 0，格减少 6867。account 聚合列 NULL 占位。

- account_avg_rfm_score（D，单处 SQL 改动）：行减少 0，格减少 7422。account 聚合列 NULL 占位。

## agent 可见证据及不确定性

event 1 / message，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-002/agent/.events/sessions/b6712d34-dc73-43-f385087dcc904ff/events/1.json`，字段字符偏移 39448。

> int_pendo__customer_rfm_analysis
>       description: Visitor–account level RFM segmentation with strategies and account-level health metrics
>       grain: One row per visitor_id + account_id
>       source_models:
>       - staging.stg_pendo__event
>       - intermediate.int_pendo__latest_visitor_account
>       business_logic: '1) Aggregate events by visitor_id + account_id: - Active days: number of distinct calendar days with any event (based on occurred_at). - Active months: number of distinct calendar

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

未遇到需要改变手册定义的问题。
