# impl-005 / int_google_ads__account_performance_metrics

## 结论

主要原因：**O**；把握：中；标记：无。

gold CS 上游额外 cost_per_conversion 被 SELECT * 带入，遮蔽后来正确舍入列；agent 当时上游没有此列。

参与因素：ctr_precision=A。

不确定性四档：**看到了但没提**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-005_int_google_ads__account_performance_metrics.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：10000/10000。本次固定控制下 baseline 行/格规模：9875/10008。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-005/docs/data_contract.yaml`；原文行段 522–623。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/intermediate/int_google_ads__account_performance_metrics.sql`，L1–52；SHA-256 `167481f6fb6d813ff79183f4da1074ee7f11e2cdbb3b3f109b67a7c52f8a4a46`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-005/sql/intermediate/int_google_ads__account_performance_metrics.sql`，L1–201；SHA-256 `7ba122db926d0d556c81288c452229c19c35b9e329c784395fa06f4dd3b9806c`。

ctr_precision：agent SQL L17，替换原片段如下。
```sql
clicks::DOUBLE / impressions
```
替换为：
```sql
clicks::FLOAT / impressions
```

cost_round：agent SQL L20，替换原片段如下。
```sql
round(CASE WHEN conversions > 0 THEN spend / conversions END, 4)
```
替换为：
```sql
CASE WHEN conversions > 0 THEN round(spend / conversions,4) END
```

cs_column_collision：agent SQL L2，替换原片段如下。
```sql
SELECT * FROM staging.stg_google_ads__account_stats
```
替换为：
```sql
SELECT * EXCLUDE(cost_per_conversion) FROM staging.stg_google_ads__account_stats
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-005_int_google_ads__account_performance_metrics.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 1 条（上限5）；代价档：一条查询。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

诊断：
```sql
DESCRIBE staging.stg_google_ads__account_stats
```
结果（仅统计/类型）：`[["source_relation", "VARCHAR", "YES", null, null, null], ["account_id", "VARCHAR", "YES", null, null, null], ["date_day", "DATE", "YES", null, null, null], ["ad_network_type", "VARCHAR", "YES", null, null, null], ["device", "VARCHAR", "YES", null, null, null], ["clicks", "BIGINT", "YES", null, null, null], ["spend", "DECIMAL(15,2)", "YES", null, null, null], ["impressions", "BIGINT", "YES", null, null, null], ["conversions", "DECIMAL(10,2)", "YES", null, null, null], ["conversions_value", "DECIMAL(15,2)", "YES", null, null, null], ["view_through_conversions", "BIGINT", "YES", null, null, null]]`

核实：
```sql
SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='staging' AND table_name='stg_google_ads__account_stats' AND column_name='cost_per_conversion'
```
结果（仅统计/类型）：`[]`

诊断：
```sql
DESCRIBE staging.stg_google_ads__account_stats
```
结果（仅统计/类型）：`[["platform", "VARCHAR", "YES", null, null, null], ["source_relation", "VARCHAR", "YES", null, null, null], ["account_id", "VARCHAR", "YES", null, null, null], ["date_day", "DATE", "YES", null, null, null], ["ad_network_type", "VARCHAR", "YES", null, null, null], ["device", "VARCHAR", "YES", null, null, null], ["active_view_impressions", "BIGINT", "YES", null, null, null], ["active_view_measurable_impressions", "BIGINT", "YES", null, null, null], ["clicks", "BIGINT", "YES", null, null, null], ["impressions", "BIGINT", "YES", null, null, null], ["interactions", "BIGINT", "YES", null, null, null], ["conversions", "DOUBLE", "YES", null, null, null], ["conversions_value", "DOUBLE", "YES", null, null, null], ["view_through_conversions", "BIGINT", "YES", null, null, null], ["cost_micros", "BIGINT", "YES", null, null, null], ["spend", "DOUBLE", "YES", null, null, null], ["active_view_measurable_cost_micros", "BIGINT", "YES", null, null, null], ["active_view_measurable_cost", "DOUBLE", "YES", null, null, null], ["active_view_viewability", "DOUBLE", "YES", null, null, null], ["active_view_measurability", "DOUBLE", "YES", null, null, null], ["click_through_rate", "DOUBLE", "YES", null, null, null], ["cost_per_click", "DOUBLE", "YES", null, null, null], ["cost_per_thousand_impressions", "DOUBLE", "YES", null, null, null], ["cost_per_conversion", "DOUBLE", "YES", null, null, null], ["interaction_event_types", "VARCHAR", "YES", null, null, null], ["_dbt_loaded_at", "TIMESTAMP WITH TIME ZONE", "YES", null, null, null]]`

诊断：
```sql
SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='staging' AND table_name='stg_google_ads__account_stats' AND column_name='cost_per_conversion'
```
结果（仅统计/类型）：`[["cost_per_conversion", "DOUBLE"]]`

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 9875 | 10008 | {"cost_per_conversion": 9875, "ctr": 6, "performance_tier": 127} | L0–L3均不匹配 |
| baseline | L1 | 9875 | 10008 | {"cost_per_conversion": 9875, "ctr": 6, "performance_tier": 127} | L0–L3均不匹配 |
| baseline | L2 | 192 | 307 | {"cost_per_conversion": 180, "performance_tier": 127} | L0–L3均不匹配 |
| baseline | L3 | 192 | 307 | {"cost_per_conversion": 180, "performance_tier": 127} | L0–L3均不匹配 |
| ctr_precision | L0 | 9875 | 10002 | {"cost_per_conversion": 9875, "performance_tier": 127} | L0–L3均不匹配 |
| ctr_precision | L1 | 9875 | 10002 | {"cost_per_conversion": 9875, "performance_tier": 127} | L0–L3均不匹配 |
| ctr_precision | L2 | 192 | 307 | {"cost_per_conversion": 180, "performance_tier": 127} | L0–L3均不匹配 |
| ctr_precision | L3 | 192 | 307 | {"cost_per_conversion": 180, "performance_tier": 127} | L0–L3均不匹配 |
| cost_round | L0 | 9875 | 10008 | {"cost_per_conversion": 9875, "ctr": 6, "performance_tier": 127} | L0–L3均不匹配 |
| cost_round | L1 | 9875 | 10008 | {"cost_per_conversion": 9875, "ctr": 6, "performance_tier": 127} | L0–L3均不匹配 |
| cost_round | L2 | 192 | 307 | {"cost_per_conversion": 180, "performance_tier": 127} | L0–L3均不匹配 |
| cost_round | L3 | 192 | 307 | {"cost_per_conversion": 180, "performance_tier": 127} | L0–L3均不匹配 |
| cs_column_collision | L0 | 19 | 19 | {"ctr": 6, "performance_tier": 13} | L0–L3均不匹配 |
| cs_column_collision | L1 | 19 | 19 | {"ctr": 6, "performance_tier": 13} | L0–L3均不匹配 |
| cs_column_collision | L2 | 13 | 13 | {"performance_tier": 13} | L0–L3均不匹配 |
| cs_column_collision | L3 | 13 | 13 | {"performance_tier": 13} | L0–L3均不匹配 |

- ctr_precision（A，单处 SQL 改动）：行减少 0，格减少 6。契约未指定中间运算用 FLOAT 还是 DOUBLE；两种浮点精度在最终舍入边界产生差异。

- cost_round（I，单处 SQL 改动）：行减少 0，格减少 0。ROUND(CASE...) 与 CASE(ROUND...) 引擎类型行为诊断。

- cs_column_collision（O，单处 SQL 改动）：行减少 9856，格减少 9989。gold CS 上游额外 cost_per_conversion 被 SELECT * 带入，遮蔽后来正确舍入列；agent 当时上游没有此列。

## agent 可见证据及不确定性

event 1 / message，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/1.json`，字段字符偏移 23682。

> int_google_ads__account_performance_metrics
>       description: Account-level daily KPIs with rolling averages, efficiency metrics, 30-day trend deltas, scoring, maturity, and data-quality flags joined to most-recent account info
>       grain: One row per account_id, source_relation, date_day
>       source_models:
>       - staging.stg_google_ads__account_stats
>       - staging.stg_google_ads__account_history (filtered to is_most_recent_record = true)
>       business_logic: '- Start from staging.stg_go

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

CS gold 上游额外包含 cost_per_conversion，agent 留存同名上游没有此列。SELECT * 与重算列重名后遮蔽，本次选 O（换成契约/agent 上游列集合即可消除主差异），不把 agent 当时不可见的 gold 扩展列当作 U 的数据反例。
