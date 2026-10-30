# impl-006 / stg_amazon_ads__campaign_report（全量）

## 结论

主要原因：**A**；把握：中。竞价策略保留原值与gold白名单/大小写清洗的未规定选择为主因。

参与因素：D：click_through_rate（减0行/12643格）；D：cost_per_click（减0行/12645格）；D：return_on_ad_spend（减0行/12753格）。标记：已披露（D占位部分）。

## 差异与归因依据

契约campaign_bidding_strategy只有VARCHAR，没有gold所用枚举白名单。逐列修复行数均不变，残余重复键按固定配对算格子，策略改动减少最多；CTR/CPC/ROAS占位为D参与因素。

层：staging；比较库schema：staging；评测键：campaign_id, date_day, campaign_applicable_budget_rule_id, campaign_budget_currency_code。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml:112–168`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_amazon_ads__campaign_report.sql:1–28`；SHA-256 `4da8bc2e681795f5931553facd7e956e6c690cbc9aeda8c24b8dcd0e1b02c5ae`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/staging/stg_amazon_ads__campaign_report.sql:1–143`；SHA-256 `699e2d6e393a5d4b90e7c7008f6c881c78d767ef5482261ce1dc924b88677c6f`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- campaign_bidding_strategy（agent SQL 第11行起）：
```sql
TRY_CAST("campaign_bidding_strategy" AS VARCHAR) AS campaign_bidding_strategy
```
→
```sql
CAST(CASE WHEN LOWER(TRIM(campaign_bidding_strategy)) IN ('advanced cpc', 'enhanced cpc', 'manual cpc', 'manual cpm', 'target impression share bids', 'maximize conversions', 'maximize conversion value', 'target cpa', 'target roas', 'viewable cpm', 'target cpm', 'commission', 'percent cpc') THEN UPPER(TRIM(campaign_bidding_strategy)) ELSE NULL END AS TEXT) AS campaign_bidding_strategy
```

- click_through_rate（agent SQL 第22行起）：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS click_through_rate
```
→
```sql
CAST(CASE WHEN impressions IS NULL OR impressions <= 0 THEN 0.0 WHEN clicks IS NULL OR clicks < 0 THEN 0.0 ELSE ROUND((CAST(clicks AS DECIMAL(18, 3)) / CAST(impressions AS DECIMAL(18, 3))) * 100, 4) END AS DOUBLE) AS click_through_rate
```

- cost_per_click（agent SQL 第23行起）：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_click
```
→
```sql
CAST(CASE WHEN clicks IS NULL OR clicks <= 0 THEN 0.0 ELSE ROUND(ROUND(CASE WHEN cost IS NULL THEN 0.0 WHEN cost < 0 THEN 0.0 ELSE cost END, 2) / clicks, 2) END AS DOUBLE) AS cost_per_click
```

- return_on_ad_spend（agent SQL 第24行起）：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS return_on_ad_spend
```
→
```sql
CAST(CASE WHEN cost IS NULL OR cost <= 0 THEN 0.0 WHEN sales_30_d IS NULL OR sales_30_d < 0 THEN 0.0 WHEN sales_30_d > 0 AND cost > 0 THEN ROUND(sales_30_d / cost, 4) ELSE 0.0 END AS DOUBLE) AS return_on_ad_spend
```

## agent可见证据与不确定性

不确定性四档：**看到了但没提**。

event18输出campaign_bidding_strategy列，event40有相关类型修复输出；未说明策略字符串是否采用白名单/大小写清洗。event97通用数值TRY_CAST/缺列NULL不涉及这项选择。

完整事件扫描数：99；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | stg_amazon_ads__campaign_report | False |
| 12 | 11 | amazon_ads_campaign_level_report_data | False |
| 16 | 15 | amazon_ads_campaign_level_report_data | False |
| 18 | 17 | amazon_ads_campaign_level_report_data | False |
| 38 | 37 | stg_amazon_ads__campaign_report | False |
| 40 | 39 | amazon_ads_campaign_level_report_data | False |
| 82 | 81 | stg_amazon_ads__campaign_report | False |
| 86 | 85 | stg_amazon_ads__campaign_report | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：2；核实代价档：多条查询。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='amazon_ads_campaign_level_report_data') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["raw", "amazon_ads_campaign_level_report_data", "campaign_id", "VARCHAR"], ["raw", "amazon_ads_campaign_level_report_data", "date", "VARCHAR"], ["raw", "amazon_ads_campaign_level_report_data", "campaign_applicable_budget_rule_id", "VARCHAR"], ["raw", "amazon_ads_campaign_level_report_data", "campaign_applicable_budget_rule_name", "VARCHAR"], ["raw", "amazon_ads_campaign_level_report_data", "campaign_bidding_strategy", "VARCHAR"], ["raw", "amazon_ads_campaign_level_report_data", "campaign_budget_amount", "DOUBLE"], ["raw", "amazon_ads_campaign_level_report_data", "campaign_budget_currency_code", "VARCHAR"], ["raw", "amazon_ads_campaign_level_report_data", "campaign_budget_type", "VARCHAR"], ["raw", "amazon_ads_campaign_level_report_data", "clicks", "BIGINT"], ["raw", "amazon_ads_campaign_level_report_data", "cost", "DOUBLE"], ["raw", "amazon_ads_campaign_level_report_data", "impressions", "BIGINT"], ["raw", "amazon_ads_campaign_level_report_data", "campaign_rule_based_budget_amount", "DOUBLE"], ["raw", "amazon_ads_campaign_level_report_data", "sales_7_d", "DOUBLE"], ["raw", "amazon_ads_campaign_level_report_data", "purchases_30_d", "BIGINT"], ["raw", "amazon_ads_campaign_level_report_data", "sales_30_d", "DOUBLE"]]`

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT count(*) n,count(*) FILTER(WHERE "campaign_bidding_strategy" IS NULL) AS c0_null,count(*) FILTER(WHERE "campaign_bidding_strategy" IS NOT NULL AND TRY_CAST("campaign_bidding_strategy" AS DOUBLE) IS NULL) AS c1_not_numeric,count(*) FILTER(WHERE "cost" IS NULL) AS c2_null,count(*) FILTER(WHERE "cost" IS NOT NULL AND TRY_CAST("cost" AS DOUBLE) IS NULL) AS c3_not_numeric FROM raw.amazon_ads_campaign_level_report_data
```

结果：`[[12990, 0, 12990, 0, 0]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=14 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025本表实际使用的raw.call_data也三侧一致（2500行、同内容哈希），不把其他Snowflake兼容表的类型改动归给本表。

## 固定时间与重跑

私有目录：`data/020_work/impl-006_stg_amazon_ads__campaign_report/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：12990行 / 54566格；重跑基线：12990行 / 54566格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:12990行/54566格 / L1:12990行/54566格 / L2:12990行/54566格 / L3:12990行/54566格 | 均未整表匹配 |
| campaign_bidding_strategy | L0:12990行/38970格 / L1:12990行/38970格 / L2:12990行/38970格 / L3:12990行/38970格 | 均未整表匹配 |
| click_through_rate | L0:12990行/41923格 / L1:12990行/41923格 / L2:12990行/41923格 / L3:12990行/41923格 | 均未整表匹配 |
| cost_per_click | L0:12990行/41921格 / L1:12990行/41921格 / L2:12990行/41921格 / L3:12990行/41921格 | 均未整表匹配 |
| return_on_ad_spend | L0:12990行/41813格 / L1:12990行/41813格 / L2:12990行/41813格 / L3:12990行/41813格 | 均未整表匹配 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {"campaign_bidding_strategy": 12990, "campaign_budget_amount": 347, "campaign_budget_type": 176, "campaign_rule_based_budget_amount": 347, "click_through_rate": 12990, "clicks": 339, "cost": 347, "cost_per_click": 12990, "impressions": 347, "purchases_30_d": 229, "return_on_ad_spend": 12990, "sales_30_d": 237, "sales_7_d": 237} |
| campaign_bidding_strategy | {"click_through_rate": 12990, "cost_per_click": 12990, "return_on_ad_spend": 12990} |
| click_through_rate | {"campaign_bidding_strategy": 12990, "campaign_budget_amount": 347, "campaign_budget_type": 176, "campaign_rule_based_budget_amount": 347, "click_through_rate": 347, "clicks": 339, "cost": 347, "cost_per_click": 12990, "impressions": 347, "purchases_30_d": 229, "return_on_ad_spend": 12990, "sales_30_d": 237, "sales_7_d": 237} |
| cost_per_click | {"campaign_bidding_strategy": 12990, "campaign_budget_amount": 347, "campaign_budget_type": 176, "campaign_rule_based_budget_amount": 347, "click_through_rate": 12990, "clicks": 339, "cost": 347, "cost_per_click": 345, "impressions": 347, "purchases_30_d": 229, "return_on_ad_spend": 12990, "sales_30_d": 237, "sales_7_d": 237} |
| return_on_ad_spend | {"campaign_bidding_strategy": 12990, "campaign_budget_amount": 347, "campaign_budget_type": 176, "campaign_rule_based_budget_amount": 347, "click_through_rate": 12990, "clicks": 339, "cost": 347, "cost_per_click": 12990, "impressions": 347, "purchases_30_d": 229, "return_on_ad_spend": 237, "sales_30_d": 237, "sales_7_d": 237} |

本表全部重跑证据文件：`records/020_reruns_impl-006_stg_amazon_ads__campaign_report.json`。续做重跑私有副本在`data/020_resume_work/`。

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

 评测键并不唯一，v2未指定重复键残余行如何配对；沿用已验证脚本：先抵消相同行，再在同键内按整行字典序配对。格子数会包含配对变化，主因排序是此固定口径下的结果；没有把单列边际差异直接当整表格子规模。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-006_stg_amazon_ads__campaign_report.md`。
- 重跑：`records/020_reruns_impl-006_stg_amazon_ads__campaign_report.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
