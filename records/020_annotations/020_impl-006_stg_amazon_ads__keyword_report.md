> **暂停检查点／待复核草稿**：用户于 2026-10-29 要求暂停。此文件尚未通过任务020最终复核，请勿作为正式定稿使用。

# impl-006 / stg_amazon_ads__keyword_report（全量）

## 结论

主要原因：**多因并列（A、D）**；把握：高。缺失归因字段的NULL/0选择，与可计算CTR/CPC的NULL占位并列。

参与因素：无。标记：已披露。

## 差异与归因依据

raw schema无attributed_*及归因收入字段，契约没规定缺失值默认0还是NULL，此类及依赖缺失收入的ROAS归A；clicks/impressions/cost存在而CTR/CPC直接NULL归D。各单列修复减少710格、行数不变。

层：staging；比较库schema：staging；评测键：keyword_id, date_day, campaign_id, ad_group_id, currency_code。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml:169–236`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_amazon_ads__keyword_report.sql:1–32`；SHA-256 `a824d8a4a978235934b0810ed4506b9cc64a5edfbcb6e089a264bf2c03457364`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/staging/stg_amazon_ads__keyword_report.sql:1–130`；SHA-256 `4ead1697138d7c17a8bca920b3a1950f00c2d1ecea1e63216ff101275a6d3670`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- attributed_conversions_14_d：
```sql
CAST(NULL::INTEGER AS INTEGER) AS attributed_conversions_14_d
```
→
```sql
CAST(0 AS INT) AS attributed_conversions_14_d
```

- attributed_conversions_30_d：
```sql
CAST(NULL::INTEGER AS INTEGER) AS attributed_conversions_30_d
```
→
```sql
CAST(0 AS INT) AS attributed_conversions_30_d
```

- attributed_sales_14_d：
```sql
CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS attributed_sales_14_d
```
→
```sql
CAST(0.0 AS DECIMAL(18, 2)) AS attributed_sales_14_d
```

- attributed_sales_30_d：
```sql
CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS attributed_sales_30_d
```
→
```sql
CAST(0.0 AS DECIMAL(18, 2)) AS attributed_sales_30_d
```

- click_through_rate：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS click_through_rate
```
→
```sql
CAST(CASE WHEN CAST(impressions AS INT) IS NULL OR CAST(impressions AS INT) <= 0 THEN 0.0 WHEN CAST(CASE WHEN clicks < 0 THEN 0 ELSE clicks END AS INT) IS NULL OR CAST(CASE WHEN clicks < 0 THEN 0 ELSE clicks END AS INT) < 0 THEN 0.0 ELSE ROUND((CAST(CAST(CASE WHEN clicks < 0 THEN 0 ELSE clicks END AS INT) AS DECIMAL(18, 3)) / CAST(CAST(impressions AS INT) AS DECIMAL(18, 3))) * 100, 4) END AS DOUBLE) AS click_through_rate
```

- cost_per_click：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_click
```
→
```sql
CAST(CASE WHEN CAST(CASE WHEN clicks < 0 THEN 0 ELSE clicks END AS INT) IS NULL OR CAST(CASE WHEN clicks < 0 THEN 0 ELSE clicks END AS INT) <= 0 THEN 0.0 ELSE ROUND(ROUND(CASE WHEN CAST(ROUND(CASE WHEN cost IS NULL THEN 0.0 WHEN cost < 0 THEN 0.0 ELSE cost END, 2) AS DECIMAL(18, 2)) IS NULL THEN 0.0 WHEN CAST(ROUND(CASE WHEN cost IS NULL THEN 0.0 WHEN cost < 0 THEN 0.0 ELSE cost END, 2) AS DECIMAL(18, 2)) < 0 THEN 0.0 ELSE CAST(ROUND(CASE WHEN cost IS NULL THEN 0.0 WHEN cost < 0 THEN 0.0 ELSE cost END, 2) AS DECIMAL(18, 2)) END, 2) / CAST(CASE WHEN clicks < 0 THEN 0 ELSE clicks END AS INT), 2) END AS DOUBLE) AS cost_per_click
```

- return_on_ad_spend：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS return_on_ad_spend
```
→
```sql
CAST(0.0 AS DOUBLE) AS return_on_ad_spend
```

## agent可见证据与不确定性

不确定性四档：**attributed_conversions_14_d=只有通用策略说明；attributed_conversions_30_d=只有通用策略说明；attributed_sales_14_d=只有通用策略说明；attributed_sales_30_d=只有通用策略说明；click_through_rate=只有通用策略说明；cost_per_click=只有通用策略说明；return_on_ad_spend=只有通用策略说明**。

event 97（args.final_thought）：对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

完整事件扫描数：99；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | stg_amazon_ads__keyword_report | False |
| 12 | 11 | amazon_ads_targeting_keyword_report_data | False |
| 16 | 15 | amazon_ads_targeting_keyword_report_data | False |
| 18 | 17 | amazon_ads_targeting_keyword_report_data | False |
| 38 | 37 | stg_amazon_ads__keyword_report | False |
| 82 | 81 | stg_amazon_ads__keyword_report | False |
| 86 | 85 | stg_amazon_ads__keyword_report | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：2；核实代价档：多条查询。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='amazon_ads_targeting_keyword_report_data') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["raw", "amazon_ads_targeting_keyword_report_data", "ad_group_id", "VARCHAR"], ["raw", "amazon_ads_targeting_keyword_report_data", "campaign_id", "VARCHAR"], ["raw", "amazon_ads_targeting_keyword_report_data", "date", "VARCHAR"], ["raw", "amazon_ads_targeting_keyword_report_data", "keyword_id", "VARCHAR"], ["raw", "amazon_ads_targeting_keyword_report_data", "ad_keyword_status", "VARCHAR"], ["raw", "amazon_ads_targeting_keyword_report_data", "campaign_budget_amount", "DOUBLE"], ["raw", "amazon_ads_targeting_keyword_report_data", "campaign_budget_currency_code", "VARCHAR"], ["raw", "amazon_ads_targeting_keyword_report_data", "campaign_budget_type", "VARCHAR"], ["raw", "amazon_ads_targeting_keyword_report_data", "clicks", "BIGINT"], ["raw", "amazon_ads_targeting_keyword_report_data", "cost", "DOUBLE"], ["raw", "amazon_ads_targeting_keyword_report_data", "impressions", "BIGINT"], ["raw", "amazon_ads_targeting_keyword_report_data", "keyword_bid", "DOUBLE"], ["raw", "amazon_ads_targeting_keyword_report_data", "keyword_type", "VARCHAR"], ["raw", "amazon_ads_targeting_keyword_report_data", "match_type", "VARCHAR"], ["raw", "amazon_ads_targeting_keyword_report_data", "targeting", "VARCHAR"]]`

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT count(*) n,count(*) FILTER(WHERE "cost" IS NULL) AS c0_null,count(*) FILTER(WHERE "cost" IS NOT NULL AND TRY_CAST("cost" AS DOUBLE) IS NULL) AS c1_not_numeric FROM raw.amazon_ads_targeting_keyword_report_data
```

结果：`[[710, 0, 0]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=15 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025的agent修改raw不适用“不可评估”，本次使用留存raw。

## 固定时间与重跑

私有目录：`data/020_work/impl-006_stg_amazon_ads__keyword_report/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：710行 / 4970格；重跑基线：710行 / 4970格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:710行/4970格 / L1:710行/4970格 / L2:710行/4970格 / L3:710行/4970格 | 均未整表匹配 |
| attributed_conversions_14_d | L0:710行/4260格 / L1:710行/4260格 / L2:710行/4260格 / L3:710行/4260格 | 均未整表匹配 |
| attributed_conversions_30_d | L0:710行/4260格 / L1:710行/4260格 / L2:710行/4260格 / L3:710行/4260格 | 均未整表匹配 |
| attributed_sales_14_d | L0:710行/4260格 / L1:710行/4260格 / L2:710行/4260格 / L3:710行/4260格 | 均未整表匹配 |
| attributed_sales_30_d | L0:710行/4260格 / L1:710行/4260格 / L2:710行/4260格 / L3:710行/4260格 | 均未整表匹配 |
| click_through_rate | L0:710行/4260格 / L1:710行/4260格 / L2:710行/4260格 / L3:710行/4260格 | 均未整表匹配 |
| cost_per_click | L0:710行/4260格 / L1:710行/4260格 / L2:710行/4260格 / L3:710行/4260格 | 均未整表匹配 |
| return_on_ad_spend | L0:710行/4260格 / L1:710行/4260格 / L2:710行/4260格 / L3:710行/4260格 | 均未整表匹配 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {"attributed_conversions_14_d": 710, "attributed_conversions_30_d": 710, "attributed_sales_14_d": 710, "attributed_sales_30_d": 710, "click_through_rate": 710, "cost_per_click": 710, "return_on_ad_spend": 710} |
| attributed_conversions_14_d | {"attributed_conversions_30_d": 710, "attributed_sales_14_d": 710, "attributed_sales_30_d": 710, "click_through_rate": 710, "cost_per_click": 710, "return_on_ad_spend": 710} |
| attributed_conversions_30_d | {"attributed_conversions_14_d": 710, "attributed_sales_14_d": 710, "attributed_sales_30_d": 710, "click_through_rate": 710, "cost_per_click": 710, "return_on_ad_spend": 710} |
| attributed_sales_14_d | {"attributed_conversions_14_d": 710, "attributed_conversions_30_d": 710, "attributed_sales_30_d": 710, "click_through_rate": 710, "cost_per_click": 710, "return_on_ad_spend": 710} |
| attributed_sales_30_d | {"attributed_conversions_14_d": 710, "attributed_conversions_30_d": 710, "attributed_sales_14_d": 710, "click_through_rate": 710, "cost_per_click": 710, "return_on_ad_spend": 710} |
| click_through_rate | {"attributed_conversions_14_d": 710, "attributed_conversions_30_d": 710, "attributed_sales_14_d": 710, "attributed_sales_30_d": 710, "cost_per_click": 710, "return_on_ad_spend": 710} |
| cost_per_click | {"attributed_conversions_14_d": 710, "attributed_conversions_30_d": 710, "attributed_sales_14_d": 710, "attributed_sales_30_d": 710, "click_through_rate": 710, "return_on_ad_spend": 710} |
| return_on_ad_spend | {"attributed_conversions_14_d": 710, "attributed_conversions_30_d": 710, "attributed_sales_14_d": 710, "attributed_sales_30_d": 710, "click_through_rate": 710, "cost_per_click": 710} |

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

无。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-006_stg_amazon_ads__keyword_report.md`。
- 重跑：`records/020_reruns_impl-006_stg_amazon_ads__keyword_report.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
