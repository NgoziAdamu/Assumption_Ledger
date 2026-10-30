# impl-006 / ad_reporting__monthly_campaign_country_report（全量）

## 结论

主要原因：**D**；把握：高。月度国家 mart 未映射 total_cost 和四个 total_attributed 字段，直接填 NULL。

参与因素：D：spend（减0行/1088格）；D：attributed_sales_14_day（减0行/1902格）；D：attributed_sales_30_day（减0行/1428格）。标记：已披露（D占位部分）。

## 差异与归因依据

契约已规定对应输出；上游有候选列，event27仅检查不完整别名映射后填NULL。逐列独立修复，所有有效错误点都是D。

层：marts；比较库schema：marts；评测键：country_code, account_id, campaign_id。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml:3798–3909`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__monthly_campaign_country_report.sql:1–37`；SHA-256 `8aeebe4c6e4c1329c07ab6aca0f4446266f99a3da10507a000f3d56ba4a3dfbb`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/marts/ad_reporting__monthly_campaign_country_report.sql:1–68`；SHA-256 `c3df66e3513d9278a49ed815ef1b0d263f39ede65516abbb74bfbead6f6cf190`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- spend（agent SQL 第13行起）：
```sql
NULL::DECIMAL(38,2) AS "spend"
```
→
```sql
total_cost AS spend
```

- attributed_sales_14_day（agent SQL 第17行起）：
```sql
NULL::DECIMAL(38,2) AS "attributed_sales_14_day"
```
→
```sql
total_attributed_sales_14_d AS attributed_sales_14_day
```

- attributed_sales_30_day（agent SQL 第18行起）：
```sql
NULL::DECIMAL(38,2) AS "attributed_sales_30_day"
```
→
```sql
total_attributed_sales_30_d AS attributed_sales_30_day
```

- attributed_conversions_14_day（agent SQL 第19行起）：
```sql
NULL::HUGEINT AS "attributed_conversions_14_day"
```
→
```sql
total_attributed_conversions_14_d AS attributed_conversions_14_day
```

- attributed_conversions_30_day（agent SQL 第20行起）：
```sql
NULL::HUGEINT AS "attributed_conversions_30_day"
```
→
```sql
total_attributed_conversions_30_d AS attributed_conversions_30_day
```

## agent可见证据与不确定性

不确定性四档：**只有通用策略说明**。

event 97（args.final_thought）：对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

完整事件扫描数：99；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | ad_reporting__monthly_campaign_country_report,int_ad_reporting__monthly_campaign_country_report | False |
| 26 | 25 | ad_reporting__monthly_campaign_country_report,int_ad_reporting__monthly_campaign_country_report | False |
| 38 | 37 | ad_reporting__monthly_campaign_country_report,int_ad_reporting__monthly_campaign_country_report | False |
| 84 | 83 | ad_reporting__monthly_campaign_country_report,int_ad_reporting__monthly_campaign_country_report | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：1；核实代价档：一条查询。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='intermediate' AND table_name='int_ad_reporting__monthly_campaign_country_report') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["intermediate", "int_ad_reporting__monthly_campaign_country_report", "platform", "VARCHAR"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "country_code", "VARCHAR"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "month_year", "DATE"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "year", "BIGINT"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "month", "BIGINT"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "account_id", "INTEGER"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "campaign_id", "VARCHAR"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "campaign_name", "INTEGER"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "total_impressions", "HUGEINT"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "total_clicks", "HUGEINT"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "total_interactions", "HUGEINT"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "total_cost", "DECIMAL(38,2)"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "total_conversions", "HUGEINT"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "total_conversions_value", "DECIMAL(38,2)"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "total_view_through_conversions", "HUGEINT"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "total_active_view_impressions", "HUGEINT"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "total_active_view_measurable_impressions", "HUGEINT"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "total_attributed_sales_14_d", "DECIMAL(38,2)"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "total_attributed_sales_30_d", "DECIMAL(38,2)"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "total_attributed_conversions_14_d", "HUGEINT"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "total_attributed_conversions_30_d", "HUGEINT"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "monthly_click_through_rate", "DOUBLE"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "monthly_cost_per_click", "DOUBLE"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "monthly_cost_per_thousand_impressions", "DOUBLE"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "monthly_cost_per_conversion", "DOUBLE"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "monthly_return_on_ad_spend", "DOUBLE"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "monthly_amazon_roas_30d", "DOUBLE"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "days_active_in_month", "BIGINT"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "avg_daily_spend", "DOUBLE"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "avg_daily_impressions", "DOUBLE"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "avg_daily_clicks", "DOUBLE"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "first_active_date", "DATE"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "last_active_date", "DATE"], ["intermediate", "int_ad_reporting__monthly_campaign_country_report", "_dbt_loaded_at", "TIMESTAMP WITH TIME ZONE"]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=10 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025本表实际使用的raw.call_data也三侧一致（2500行、同内容哈希），不把其他Snowflake兼容表的类型改动归给本表。

## 固定时间与重跑

私有目录：`data/020_work/impl-006_ad_reporting__monthly_campaign_country_report/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：4236行 / 79205格；重跑基线：4236行 / 79205格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:4236行/79205格 / L1:4236行/79172格 / L2:4236行/79134格 / L3:4236行/79134格 | 均未整表匹配 |
| spend | L0:4236行/78117格 / L1:4236行/78082格 / L2:4236行/78044格 / L3:4236行/78044格 | 均未整表匹配 |
| attributed_sales_14_day | L0:4236行/77303格 / L1:4236行/77824格 / L2:4236行/77770格 / L3:4236行/77770格 | 均未整表匹配 |
| attributed_sales_30_day | L0:4236行/77777格 / L1:4236行/77939格 / L2:4236行/77887格 / L3:4236行/77887格 | 均未整表匹配 |
| attributed_conversions_14_day | L0:4236行/43086格 / L1:4236行/43275格 / L2:4236行/43254格 / L3:4236行/43254格 | 均未整表匹配 |
| attributed_conversions_30_day | L0:4236行/43086格 / L1:4236行/43275格 / L2:4236行/43254格 / L3:4236行/43254格 | 均未整表匹配 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {"attributed_conversions_14_day": 4236, "attributed_conversions_30_day": 4236, "attributed_sales_14_day": 4236, "attributed_sales_30_day": 4236, "avg_cpa": 3147, "avg_cpc": 3144, "avg_cpm": 3148, "avg_ctr_percent": 3148, "avg_daily_clicks": 3130, "avg_daily_impressions": 3146, "avg_daily_spend": 3148, "avg_roas": 3148, "clicks": 3143, "conversions": 2958, "conversions_value": 3148, "days_active_in_month": 2527, "first_active_date": 3148, "impressions": 3147, "last_active_date": 3148, "month": 2958, "monthly_amazon_roas_30d": 3148, "report_month": 3148, "spend": 4236, "year": 2393} |
| spend | {"attributed_conversions_14_day": 4236, "attributed_conversions_30_day": 4236, "attributed_sales_14_day": 4236, "attributed_sales_30_day": 4236, "avg_cpa": 3147, "avg_cpc": 3144, "avg_cpm": 3148, "avg_ctr_percent": 3148, "avg_daily_clicks": 3130, "avg_daily_impressions": 3146, "avg_daily_spend": 3148, "avg_roas": 3148, "clicks": 3143, "conversions": 2958, "conversions_value": 3148, "days_active_in_month": 2527, "first_active_date": 3148, "impressions": 3147, "last_active_date": 3148, "month": 2958, "monthly_amazon_roas_30d": 3148, "report_month": 3148, "spend": 3148, "year": 2393} |
| attributed_sales_14_day | {"attributed_conversions_14_day": 4236, "attributed_conversions_30_day": 4236, "attributed_sales_14_day": 3108, "attributed_sales_30_day": 4236, "avg_cpa": 3109, "avg_cpc": 3094, "avg_cpm": 3109, "avg_ctr_percent": 3109, "avg_daily_clicks": 3085, "avg_daily_impressions": 3108, "avg_daily_spend": 3109, "avg_roas": 3109, "clicks": 3100, "conversions": 2937, "conversions_value": 3107, "days_active_in_month": 2445, "first_active_date": 3109, "impressions": 3109, "last_active_date": 3109, "month": 2914, "monthly_amazon_roas_30d": 3109, "report_month": 3109, "spend": 4236, "year": 2371} |
| attributed_sales_30_day | {"attributed_conversions_14_day": 4236, "attributed_conversions_30_day": 4236, "attributed_sales_14_day": 4236, "attributed_sales_30_day": 3131, "avg_cpa": 3132, "avg_cpc": 3126, "avg_cpm": 3132, "avg_ctr_percent": 3132, "avg_daily_clicks": 3116, "avg_daily_impressions": 3130, "avg_daily_spend": 3132, "avg_roas": 3131, "clicks": 3127, "conversions": 2934, "conversions_value": 3131, "days_active_in_month": 2491, "first_active_date": 3132, "impressions": 3132, "last_active_date": 3132, "month": 2916, "monthly_amazon_roas_30d": 3131, "report_month": 3132, "spend": 4236, "year": 2413} |
| attributed_conversions_14_day | {"attributed_conversions_30_day": 4236, "attributed_sales_14_day": 4236, "attributed_sales_30_day": 4236, "avg_cpa": 1499, "avg_cpc": 1494, "avg_cpm": 1499, "avg_ctr_percent": 1499, "avg_daily_clicks": 1475, "avg_daily_impressions": 1498, "avg_daily_spend": 1499, "avg_roas": 1498, "clicks": 1489, "conversions_value": 1499, "days_active_in_month": 1131, "first_active_date": 1499, "impressions": 1496, "last_active_date": 1499, "month": 1411, "monthly_amazon_roas_30d": 1498, "report_month": 1499, "spend": 4236, "year": 1160} |
| attributed_conversions_30_day | {"attributed_conversions_14_day": 4236, "attributed_sales_14_day": 4236, "attributed_sales_30_day": 4236, "avg_cpa": 1499, "avg_cpc": 1494, "avg_cpm": 1499, "avg_ctr_percent": 1499, "avg_daily_clicks": 1475, "avg_daily_impressions": 1498, "avg_daily_spend": 1499, "avg_roas": 1498, "clicks": 1489, "conversions_value": 1499, "days_active_in_month": 1131, "first_active_date": 1499, "impressions": 1496, "last_active_date": 1499, "month": 1411, "monthly_amazon_roas_30d": 1498, "report_month": 1499, "spend": 4236, "year": 1160} |

本表全部重跑证据文件：`records/020_reruns_impl-006_ad_reporting__monthly_campaign_country_report.json`。续做重跑私有副本在`data/020_resume_work/`。

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

 评测键并不唯一，v2未指定重复键残余行如何配对；沿用已验证脚本：先抵消相同行，再在同键内按整行字典序配对。格子数会包含配对变化，主因排序是此固定口径下的结果；没有把单列边际差异直接当整表格子规模。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-006_ad_reporting__monthly_campaign_country_report.md`。
- 重跑：`records/020_reruns_impl-006_ad_reporting__monthly_campaign_country_report.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
