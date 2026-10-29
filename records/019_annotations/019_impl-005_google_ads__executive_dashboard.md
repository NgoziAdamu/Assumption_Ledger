# impl-005 / google_ads__executive_dashboard

## 结论

主要原因：**I**；把握：高；标记：无。

SELECT * 已含同名列，新增舍入列自动改名，最终仍选旧列。

参与因素：scale_null=C。

不确定性四档：**看到了但没提**。

## 差异与依据

精简材料包：`records/019_packages/019_impl-005_google_ads__executive_dashboard.md`。原始判错不变；staging 从 agent raw 复制，intermediate/marts 使用 gold 上游；原库只读。
历史选定结果 agent/gold 行数：10000/10000。本次固定控制下 baseline 行/格规模：10000/30474。
契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-005/docs/data_contract.yaml`；原文行段 1795–1953。
agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/marts/google_ads__executive_dashboard.sql`，L1–25；SHA-256 `dabab0e6c6c48d8455a45e426aafc9d930a93d334ce0a820404758a1fa9ade91`。
gold SQL（仅定位）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-005/sql/marts/google_ads__executive_dashboard.sql`，L1–276；SHA-256 `a8f72507b0573e9c01d1c92baff75ef1dc951a9b31c4701ab92a47ca9fc126b5`。

rounded_alias：agent SQL L15，替换原片段如下。
```sql
SELECT *,round(spend_30d_avg,2)
```
替换为：
```sql
SELECT * EXCLUDE(spend_30d_avg,roas_30d_avg,performance_score_30d_avg),round(spend_30d_avg,2)
```

scale_null：agent SQL L24，替换原片段如下。
```sql
(star_pct>15) scale_opportunity
```
替换为：
```sql
coalesce(star_pct>15,false) scale_opportunity
```

每个单处改动的准确 old/new、字节位置和私有 SQL SHA-256 见下列重跑记录；未改变其余 SQL 字节（固定时间为共同控制）。

`records/019_reruns_impl-005_google_ads__executive_dashboard.json`；修改理由与类别：`records/019_patch_plan.json`。

## 查询和重跑

核实查询 0 条（上限5）；代价档：需要查业务说明。0条表示契约或代码已提供直接判据，不虚构数据核实。诊断查询不计入5条。

| 改动 | 档位 | 行规模 | 格子规模 | 每列不一致（共同键） | 整表首次匹配 |
|---|---|---:|---:|---|---|
| baseline | L0 | 10000 | 30474 | {"conversions_wow_growth_pct": 68, "performance_score_30d_avg": 9980, "roas_30d_avg": 9612, "scale_opportunity": 16, "spend_30d_avg": 10000, "spend_wow_growth_pct": 70, "trending_alert": 728} | L0–L3均不匹配 |
| baseline | L1 | 10000 | 30474 | {"conversions_wow_growth_pct": 68, "performance_score_30d_avg": 9980, "roas_30d_avg": 9612, "scale_opportunity": 16, "spend_30d_avg": 10000, "spend_wow_growth_pct": 70, "trending_alert": 728} | L0–L3均不匹配 |
| baseline | L2 | 9090 | 10024 | {"conversions_wow_growth_pct": 68, "performance_score_30d_avg": 8995, "roas_30d_avg": 98, "scale_opportunity": 16, "spend_30d_avg": 49, "spend_wow_growth_pct": 70, "trending_alert": 728} | L0–L3均不匹配 |
| baseline | L3 | 9090 | 10024 | {"conversions_wow_growth_pct": 68, "performance_score_30d_avg": 8995, "roas_30d_avg": 98, "scale_opportunity": 16, "spend_30d_avg": 49, "spend_wow_growth_pct": 70, "trending_alert": 728} | L0–L3均不匹配 |
| rounded_alias | L0 | 805 | 1029 | {"conversions_wow_growth_pct": 68, "performance_score_30d_avg": 48, "roas_30d_avg": 50, "scale_opportunity": 16, "spend_30d_avg": 49, "spend_wow_growth_pct": 70, "trending_alert": 728} | L0–L3均不匹配 |
| rounded_alias | L1 | 805 | 1029 | {"conversions_wow_growth_pct": 68, "performance_score_30d_avg": 48, "roas_30d_avg": 50, "scale_opportunity": 16, "spend_30d_avg": 49, "spend_wow_growth_pct": 70, "trending_alert": 728} | L0–L3均不匹配 |
| rounded_alias | L2 | 805 | 1028 | {"conversions_wow_growth_pct": 68, "performance_score_30d_avg": 48, "roas_30d_avg": 49, "scale_opportunity": 16, "spend_30d_avg": 49, "spend_wow_growth_pct": 70, "trending_alert": 728} | L0–L3均不匹配 |
| rounded_alias | L3 | 805 | 1028 | {"conversions_wow_growth_pct": 68, "performance_score_30d_avg": 48, "roas_30d_avg": 49, "scale_opportunity": 16, "spend_30d_avg": 49, "spend_wow_growth_pct": 70, "trending_alert": 728} | L0–L3均不匹配 |
| scale_null | L0 | 10000 | 30458 | {"conversions_wow_growth_pct": 68, "performance_score_30d_avg": 9980, "roas_30d_avg": 9612, "spend_30d_avg": 10000, "spend_wow_growth_pct": 70, "trending_alert": 728} | L0–L3均不匹配 |
| scale_null | L1 | 10000 | 30458 | {"conversions_wow_growth_pct": 68, "performance_score_30d_avg": 9980, "roas_30d_avg": 9612, "spend_30d_avg": 10000, "spend_wow_growth_pct": 70, "trending_alert": 728} | L0–L3均不匹配 |
| scale_null | L2 | 9087 | 10008 | {"conversions_wow_growth_pct": 68, "performance_score_30d_avg": 8995, "roas_30d_avg": 98, "spend_30d_avg": 49, "spend_wow_growth_pct": 70, "trending_alert": 728} | L0–L3均不匹配 |
| scale_null | L3 | 9087 | 10008 | {"conversions_wow_growth_pct": 68, "performance_score_30d_avg": 8995, "roas_30d_avg": 98, "spend_30d_avg": 49, "spend_wow_growth_pct": 70, "trending_alert": 728} | L0–L3均不匹配 |

- rounded_alias（I，单处 SQL 改动）：行减少 9195，格减少 29445。SELECT * 已含同名列，新增舍入列自动改名，最终仍选旧列。

- scale_null（C，单处 SQL 改动）：行减少 0，格减少 16。契约规定布尔 false 默认，agent 保留 NULL。

## agent 可见证据及不确定性

event 1 / message，`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/1.json`，字段字符偏移 116896。

> google_ads__executive_dashboard
>       description: Executive summary of Google Ads performance with daily account KPIs, trends, portfolio composition, and prescriptive flags
>       grain: One row per account_id per date_day (only days with total_spend > 0; account_id and date_day not null)
>       source_models:
>       - intermediate.int_google_ads__account_performance_metrics (source_relation, account_id, account_name, currency_code, date_day, account_maturity_stage, performance_score, performance_

原轨迹检索覆盖本题事件的 thought/message、命令输出与最终报告；索引、截断标记见材料包。这里引用原事件中实际存在的字段，不将工具请求读取但未返回的内容当作看过。

## 不确定与限制

单修未改善的点不列参与因素；同源替代修法不重复计数。未整表匹配意味着该单修不是完整修复，不声称其余错误均已消除。重跑与历史保留结果可能因允许的并列顺序或随机值变化，基线和每次试验均保留。

## 规则问题

未遇到需要改变手册定义的问题。
