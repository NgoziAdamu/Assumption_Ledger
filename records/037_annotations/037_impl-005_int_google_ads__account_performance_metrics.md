# impl-005_int_google_ads__account_performance_metrics（037 正式批次）

主要原因：**其他**；把握：中。019旧主要原因原样保留：`O`，不作为新类别依据。

## 范围与材料

- 层：intermediate；属于已核对的43张正式表。
- 契约：初始 event 1 的 `message` 直接提供本模型完整契约；全文匹配已核实，没有读取截断。
- 最终SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/intermediate/int_google_ads__account_performance_metrics.sql`。
- 最终报告：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/47.json`，finish 47 / `args.final_thought`。交付SQL注释扫描未找到额外说明；临时脚本不算交付物。
- CS及数据来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-005/google_ads.duckdb`；staging使用agent留存raw，其他层复用标准上游。原数据库只读；新重跑在内存私有副本。
- 019基线/干预：`records/019_reruns_impl-005_int_google_ads__account_performance_metrics.json`；037补充：`records/037_checks/`。

## 逐点标注

### cs_column_collision

- 类别：其他；角色：主要；把握：中。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

CS使用gold上游，其额外cost_per_conversion列被SELECT *带入并遮蔽正确舍入列；agent当时的上游没有该额外列。019诊断排除该列后主要差异消失，属于评测上游条件不同。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> - name: cost_per_conversion
>         data_type: DOUBLE
>         description: Spend per conversion in account currency, rounded to 4 decimals; NULL when conversions <= 0

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/intermediate/int_google_ads__account_performance_metrics.sql`，第 2–2 行：

```sql
SELECT * FROM staging.stg_google_ads__account_stats
```

单改/诊断：`records/019_reruns_impl-005_int_google_ads__account_performance_metrics.json#cs_column_collision`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 9875/10008 | 19/19 | 9856/9989 |
| L1 | 9875/10008 | 19/19 | 9856/9989 |
| L2 | 192/307 | 13/13 | 179/294 |
| L3 | 192/307 | 13/13 | 179/294 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/1.json`，event `1.message`：

> - name: cost_per_conversion
>         data_type: DOUBLE
>         description: Spend per conversion in account currency, rounded to 4 decimals; NULL when conversions <= 0

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

### ctr_precision

- 类别：Unstated Choice；角色：参与；把握：中。
- 是否说出：第4档（看到了相关信息，但没有意识到的迹象）。
- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

契约未规定中间CTR运算使用FLOAT还是DOUBLE；边界舍入数值不同，不能只视为呈现差异。

契约原句（初始 event 1，完整在场；摘录不代表完整业务规则只有这一句）：

> business_logic: '- Start from staging.stg_google_ads__account_stats as daily_stats (no filtering). - From staging.stg_google_ads__account_history, keep only rows where is_most_recent_record = true (account_info). - Compute rolling_metrics per (account_id, source_relation), ordered by date_day: - 7-day rolling averages: for each day, average spend, clicks, and impressions across the current day and up to six prior days; averages ignore NULLs and use smaller windows at the start. - 30-day lags: prior 30th-day values for spend and conversions for month-over-month comparisons. - Efficiency metrics (rounded to 4 decimals): - CTR: percentage of impressions that resulted in clicks; 0 when impressions <= 0. - CPC: spend per click; 0 when clicks <= 0. - CPM: spend per 1,000 impressions; 0 when impressions <= 0. - Cost per conversion: spend per conversion; NULL when conversions <= 0. - ROAS: conversion value divided by spend; 0 when spend <= 0 or conversions_value <= 0. - Compute account_scoring: - days_since_first_activity: days since the earliest date_day for the account_id (partitioned by account_id only); non-negative. - performance_score: clamp to 0–100 for the sum of: CTR*10; ROAS*10 capped at 50; +20 if cost_per_conversion < 50; and either +10 if clicks_7d_avg > 100 else + (clicks_7d_avg / 10); may be NULL if clicks_7d_avg is NULL. - spend_mom_change_pct: percent change vs the 30-day lag of spend when the lag > 0; rounded to 2 decimals; else NULL. - conversions_mom_change_pct: percent change vs the 30-day lag of conversions when the lag > 0; rounded to 2 decimals; else NULL. - account_maturity_stage by days_since_first_activity: <30 → "New Account"; <90 → "Growing Account"; <365 → "Established Account"; else "Mature Account". - performance_tier by performance_score: ≥80 → "Excellent"; ≥60 → "Good"; ≥40 → "Average"; ≥20 → "Below Average"; else "Poor". - Final select joins account_scoring to account_info on (account_id, source_relation) with a left join; account_name, currency_code, and time_zone may be NULL if no match. - Apply final filters: keep rows where spend >= 0, clicks >= 0, impressions >= 0, conversions >= 0, date_day IS NOT NULL, and account_id IS NOT NULL. - Output is ordered by account_id, date_day (ordering does not affect computed values).'

SQL原处：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/intermediate/int_google_ads__account_performance_metrics.sql`，第 17–17 行：

```sql
clicks::DOUBLE / impressions
```

单改/诊断：`records/019_reruns_impl-005_int_google_ads__account_performance_metrics.json#ctr_precision`。单处SQL干预；其他类的gold复现只作诊断；与其自身固定时间基线比较。

| 口径 | 基线行/格 | 单改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 9875/10008 | 9875/10002 | 0/6 |
| L1 | 9875/10008 | 9875/10002 | 0/6 |
| L2 | 192/307 | 192/307 | 0/0 |
| L3 | 192/307 | 192/307 | 0/0 |

披露/相关信息原句：

`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/1.json`，event `1.message`：

> business_logic: '- Start from staging.stg_google_ads__account_stats as daily_stats (no filtering). - From staging.stg_google_ads__account_history, keep only rows where is_most_recent_record = true (account_info). - Compute rolling_metrics per (account_id, source_relation), ordered by date_day: - 7-day rolling averages: for each day, average spend, clicks, and impressions across the current day and up to six prior days; averages ignore NULLs and use smaller windows at the start. - 30-day lags: prior 30th-day values for spend and conversions for month-over-month comparisons. - Efficiency metrics (rounded to 4 decimals): - CTR: percentage of impressions that resulted in clicks; 0 when impressions <= 0. - CPC: spend per click; 0 when clicks <= 0. - CPM: spend per 1,000 impressions; 0 when impressions <= 0. - Cost per conversion: spend per conversion; NULL when conversions <= 0. - ROAS: conversion value divided by spend; 0 when spend <= 0 or conversions_value <= 0. - Compute account_scoring: - days_since_first_activity: days since the earliest date_day for the account_id (partitioned by account_id only); non-negative. - performance_score: clamp to 0–100 for the sum of: CTR*10; ROAS*10 capped at 50; +20 if cost_per_conversion < 50; and either +10 if clicks_7d_avg > 100 else + (clicks_7d_avg / 10); may be NULL if clicks_7d_avg is NULL. - spend_mom_change_pct: percent change vs the 30-day lag of spend when the lag > 0; rounded to 2 decimals; else NULL. - conversions_mom_change_pct: percent change vs the 30-day lag of conversions when the lag > 0; rounded to 2 decimals; else NULL. - account_maturity_stage by days_since_first_activity: <30 → "New Account"; <90 → "Growing Account"; <365 → "Established Account"; else "Mature Account". - performance_tier by performance_score: ≥80 → "Excellent"; ≥60 → "Good"; ≥40 → "Average"; ≥20 → "Below Average"; else "Poor". - Final select joins account_scoring to account_info on (account_id, source_relation) with a left join; account_name, currency_code, and time_zone may be NULL if no match. - Apply final filters: keep rows where spend >= 0, clicks >= 0, impressions >= 0, conversions >= 0, date_day IS NOT NULL, and account_id IS NOT NULL. - Output is ordered by account_id, date_day (ordering does not affect computed values).'

契约相关信息在初始事件完整出现；复核中间run/finish与最终SQL，没有找到本处比较备选、指出疑问或冲突的原句。仅写做法不按v3.2计第3档。

## 规模、覆盖与不确定

主因按L0整表规模先行后格排序，L1–L3一并保留；不能相加各点贡献。新旧干预只和各自基线比较。不同类别候选均有单改/诊断，不根据旧标签决定角色。

未评分列、单改不改善的缺口也保留非原因；派生列由上游错误传播时不按每个差异格重复制造错误点。恢复某个常量公式时，其他占位继续保留；未声称单点修复了整个模型。原始单改SQL与L0–L3完整结果可逐项复查。

如本表有主因同类多点并列，仍逐点列出；只在不同类别同规模并列时把对象主因写为多因并列。

复用核实/诊断查询：

`records/019_queries.json` / 诊断：
```sql
DESCRIBE staging.stg_google_ads__account_stats
```
结果：`[["source_relation", "VARCHAR", "YES", null, null, null], ["account_id", "VARCHAR", "YES", null, null, null], ["date_day", "DATE", "YES", null, null, null], ["ad_network_type", "VARCHAR", "YES", null, null, null], ["device", "VARCHAR", "YES", null, null, null], ["clicks", "BIGINT", "YES", null, null, null], ["spend", "DECIMAL(15,2)", "YES", null, null, null], ["impressions", "BIGINT", "YES", null, null, null], ["conversions", "DECIMAL(10,2)", "YES", null, null, null], ["conversions_value", "DECIMAL(15,2)", "YES", null, null, null], ["view_through_conversions", "BIGINT", "YES", null, null, null]]`

`records/019_queries.json` / 核实：
```sql
SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='staging' AND table_name='stg_google_ads__account_stats' AND column_name='cost_per_conversion'
```
结果：`[]`

`records/019_queries.json` / 诊断：
```sql
DESCRIBE staging.stg_google_ads__account_stats
```
结果：`[["platform", "VARCHAR", "YES", null, null, null], ["source_relation", "VARCHAR", "YES", null, null, null], ["account_id", "VARCHAR", "YES", null, null, null], ["date_day", "DATE", "YES", null, null, null], ["ad_network_type", "VARCHAR", "YES", null, null, null], ["device", "VARCHAR", "YES", null, null, null], ["active_view_impressions", "BIGINT", "YES", null, null, null], ["active_view_measurable_impressions", "BIGINT", "YES", null, null, null], ["clicks", "BIGINT", "YES", null, null, null], ["impressions", "BIGINT", "YES", null, null, null], ["interactions", "BIGINT", "YES", null, null, null], ["conversions", "DOUBLE", "YES", null, null, null], ["conversions_value", "DOUBLE", "YES", null, null, null], ["view_through_conversions", "BIGINT", "YES", null, null, null], ["cost_micros", "BIGINT", "YES", null, null, null], ["spend", "DOUBLE", "YES", null, null, null], ["active_view_measurable_cost_micros", "BIGINT", "YES", null, null, null], ["active_view_measurable_cost", "DOUBLE", "YES", null, null, null], ["active_view_viewability", "DOUBLE", "YES", null, null, null], ["active_view_measurability", "DOUBLE", "YES", null, null, null], ["click_through_rate", "DOUBLE", "YES", null, null, null], ["cost_per_click", "DOUBLE", "YES", null, null, null], ["cost_per_thousand_impressions", "DOUBLE", "YES", null, null, null], ["cost_per_conversion", "DOUBLE", "YES", null, null, null], ["interaction_event_types", "VARCHAR", "YES", null, null, null], ["_dbt_loaded_at", "TIMESTAMP WITH TIME ZONE", "YES", null, null, null]]`

`records/019_queries.json` / 诊断：
```sql
SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='staging' AND table_name='stg_google_ads__account_stats' AND column_name='cost_per_conversion'
```
结果：`[["cost_per_conversion", "DOUBLE"]]`
