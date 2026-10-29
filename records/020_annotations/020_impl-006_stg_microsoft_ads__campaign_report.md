> **暂停检查点／待复核草稿**：用户于 2026-10-29 要求暂停。此文件尚未通过任务020最终复核，请勿作为正式定稿使用。

# impl-006 / stg_microsoft_ads__campaign_report（全量）

## 结论

主要原因：**多因并列（A、D）**；把握：高。可用spend及指标占位，与不存在字段的默认值选择并列。

参与因素：无。标记：已披露。

## 差异与归因依据

raw.spend及各计算分子分母存在，D；assists/bounce_rate/average_position没有源列，gold常数0与agent NULL归A。单列影响均1500格。

层：staging；比较库schema：staging；评测键：campaign_id。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml:1002–1046`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_microsoft_ads__campaign_report.sql:1–29`；SHA-256 `c3a577f0d919bfcf14f9b5c6eea541deaa0a1f1ff731c2dd50faf803d56cf643`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/staging/stg_microsoft_ads__campaign_report.sql:1–65`；SHA-256 `d3a7e61be64095517d6271677d5b04b95ca3d1cec9771eaf23aa32fc4f900ef3`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- assists：
```sql
CAST(NULL::INTEGER AS INTEGER) AS assists
```
→
```sql
CAST(0 AS INT) AS assists
```

- average_position：
```sql
CAST(NULL::DECIMAL(8,2) AS DECIMAL(8,2)) AS average_position
```
→
```sql
CAST(0 AS DECIMAL(8, 2)) AS average_position
```

- bounce_rate：
```sql
CAST(NULL::DECIMAL(8,4) AS DECIMAL(8,4)) AS bounce_rate
```
→
```sql
CAST(0 AS DECIMAL(8, 4)) AS bounce_rate
```

- click_through_rate：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS click_through_rate
```
→
```sql
CASE WHEN impressions > 0 THEN ROUND((CAST(clicks AS DECIMAL(18, 3)) / CAST(impressions AS DECIMAL(18, 3))) * 100, 4) ELSE 0 END AS click_through_rate
```

- cost_per_click：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_click
```
→
```sql
CASE WHEN clicks > 0 THEN ROUND(spend / clicks, 2) ELSE 0 END AS cost_per_click
```

- cost_per_conversion：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_conversion
```
→
```sql
CASE WHEN conversions > 0 THEN ROUND(spend / conversions, 2) ELSE 0 END AS cost_per_conversion
```

- cost_per_thousand_impressions：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_thousand_impressions
```
→
```sql
CASE WHEN impressions > 0 THEN ROUND((spend / impressions) * 1000, 2) ELSE 0 END AS cost_per_thousand_impressions
```

- return_on_ad_spend：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS return_on_ad_spend
```
→
```sql
CASE WHEN spend > 0 THEN ROUND(CAST(COALESCE(revenue, '0') AS DECIMAL(18, 2)) / spend, 4) ELSE 0 END AS return_on_ad_spend
```

- spend：
```sql
CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS spend
```
→
```sql
CAST(spend AS DECIMAL(18, 2)) AS spend
```

## agent可见证据与不确定性

不确定性四档：**assists=只有通用策略说明；average_position=只有通用策略说明；bounce_rate=只有通用策略说明；click_through_rate=只有通用策略说明；cost_per_click=只有通用策略说明；cost_per_conversion=只有通用策略说明；cost_per_thousand_impressions=只有通用策略说明；return_on_ad_spend=只有通用策略说明；spend=只有通用策略说明**。

event 97（args.final_thought）：对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

完整事件扫描数：99；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | stg_microsoft_ads__campaign_report | False |
| 12 | 11 | microsoft_ads_campaign_performance_daily_report_data | False |
| 16 | 15 | microsoft_ads_campaign_performance_daily_report_data | False |
| 18 | 17 | microsoft_ads_campaign_performance_daily_report_data | False |
| 38 | 37 | stg_microsoft_ads__campaign_report | False |
| 82 | 81 | stg_microsoft_ads__campaign_report | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：2；核实代价档：多条查询。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='microsoft_ads_campaign_performance_daily_report_data') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["raw", "microsoft_ads_campaign_performance_daily_report_data", "date", "VARCHAR"], ["raw", "microsoft_ads_campaign_performance_daily_report_data", "account_id", "VARCHAR"], ["raw", "microsoft_ads_campaign_performance_daily_report_data", "campaign_id", "VARCHAR"], ["raw", "microsoft_ads_campaign_performance_daily_report_data", "currency_code", "VARCHAR"], ["raw", "microsoft_ads_campaign_performance_daily_report_data", "device_os", "VARCHAR"], ["raw", "microsoft_ads_campaign_performance_daily_report_data", "device_type", "VARCHAR"], ["raw", "microsoft_ads_campaign_performance_daily_report_data", "network", "VARCHAR"], ["raw", "microsoft_ads_campaign_performance_daily_report_data", "ad_distribution", "VARCHAR"], ["raw", "microsoft_ads_campaign_performance_daily_report_data", "bid_match_type", "VARCHAR"], ["raw", "microsoft_ads_campaign_performance_daily_report_data", "delivered_match_type", "VARCHAR"], ["raw", "microsoft_ads_campaign_performance_daily_report_data", "top_vs_other", "VARCHAR"], ["raw", "microsoft_ads_campaign_performance_daily_report_data", "budget_association_status", "VARCHAR"], ["raw", "microsoft_ads_campaign_performance_daily_report_data", "budget_name", "VARCHAR"], ["raw", "microsoft_ads_campaign_performance_daily_report_data", "clicks", "BIGINT"], ["raw", "microsoft_ads_campaign_performance_daily_report_data", "impressions", "BIGINT"], ["raw", "microsoft_ads_campaign_performance_daily_report_data", "spend", "DOUBLE"], ["raw", "microsoft_ads_campaign_performance_daily_report_data", "conversions_qualified", "VARCHAR"], ["raw", "microsoft_ads_campaign_performance_daily_report_data", "conversions", "BIGINT"], ["raw", "microsoft_ads_campaign_performance_daily_report_data", "revenue", "DOUBLE"], ["raw", "microsoft_ads_campaign_performance_daily_report_data", "all_conversions_qualified", "VARCHAR"], ["raw", "microsoft_ads_campaign_performance_daily_report_data", "all_conversions", "VARCHAR"], ["raw", "microsoft_ads_campaign_performance_daily_report_data", "all_revenue", "BIGINT"]]`

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT count(*) n,count(*) FILTER(WHERE "impressions" IS NULL) AS c0_null,count(*) FILTER(WHERE "impressions" IS NOT NULL AND TRY_CAST("impressions" AS DOUBLE) IS NULL) AS c1_not_numeric,count(*) FILTER(WHERE "spend" IS NULL) AS c2_null,count(*) FILTER(WHERE "spend" IS NOT NULL AND TRY_CAST("spend" AS DOUBLE) IS NULL) AS c3_not_numeric FROM raw.microsoft_ads_campaign_performance_daily_report_data
```

结果：`[[1500, 0, 0, 0, 0]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=27 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025的agent修改raw不适用“不可评估”，本次使用留存raw。

## 固定时间与重跑

私有目录：`data/020_work/impl-006_stg_microsoft_ads__campaign_report/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：1500行 / 13500格；重跑基线：1500行 / 13500格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:1500行/13500格 / L1:1500行/13500格 / L2:1500行/13500格 / L3:1500行/13500格 | 均未整表匹配 |
| assists | L0:1500行/12000格 / L1:1500行/12000格 / L2:1500行/12000格 / L3:1500行/12000格 | 均未整表匹配 |
| average_position | L0:1500行/12000格 / L1:1500行/12000格 / L2:1500行/12000格 / L3:1500行/12000格 | 均未整表匹配 |
| bounce_rate | L0:1500行/12000格 / L1:1500行/12000格 / L2:1500行/12000格 / L3:1500行/12000格 | 均未整表匹配 |
| click_through_rate | L0:1500行/12000格 / L1:1500行/12000格 / L2:1500行/12000格 / L3:1500行/12000格 | 均未整表匹配 |
| cost_per_click | L0:1500行/12000格 / L1:1500行/12000格 / L2:1500行/12000格 / L3:1500行/12000格 | 均未整表匹配 |
| cost_per_conversion | L0:1500行/12000格 / L1:1500行/12000格 / L2:1500行/12000格 / L3:1500行/12000格 | 均未整表匹配 |
| cost_per_thousand_impressions | L0:1500行/12000格 / L1:1500行/12000格 / L2:1500行/12000格 / L3:1500行/12000格 | 均未整表匹配 |
| return_on_ad_spend | L0:1500行/12000格 / L1:1500行/12000格 / L2:1500行/12000格 / L3:1500行/12000格 | 均未整表匹配 |
| spend | L0:1500行/12000格 / L1:1500行/12000格 / L2:1500行/12000格 / L3:1500行/12000格 | 均未整表匹配 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {"assists": 1500, "average_position": 1500, "bounce_rate": 1500, "click_through_rate": 1500, "cost_per_click": 1500, "cost_per_conversion": 1500, "cost_per_thousand_impressions": 1500, "return_on_ad_spend": 1500, "spend": 1500} |
| assists | {"average_position": 1500, "bounce_rate": 1500, "click_through_rate": 1500, "cost_per_click": 1500, "cost_per_conversion": 1500, "cost_per_thousand_impressions": 1500, "return_on_ad_spend": 1500, "spend": 1500} |
| average_position | {"assists": 1500, "bounce_rate": 1500, "click_through_rate": 1500, "cost_per_click": 1500, "cost_per_conversion": 1500, "cost_per_thousand_impressions": 1500, "return_on_ad_spend": 1500, "spend": 1500} |
| bounce_rate | {"assists": 1500, "average_position": 1500, "click_through_rate": 1500, "cost_per_click": 1500, "cost_per_conversion": 1500, "cost_per_thousand_impressions": 1500, "return_on_ad_spend": 1500, "spend": 1500} |
| click_through_rate | {"assists": 1500, "average_position": 1500, "bounce_rate": 1500, "cost_per_click": 1500, "cost_per_conversion": 1500, "cost_per_thousand_impressions": 1500, "return_on_ad_spend": 1500, "spend": 1500} |
| cost_per_click | {"assists": 1500, "average_position": 1500, "bounce_rate": 1500, "click_through_rate": 1500, "cost_per_conversion": 1500, "cost_per_thousand_impressions": 1500, "return_on_ad_spend": 1500, "spend": 1500} |
| cost_per_conversion | {"assists": 1500, "average_position": 1500, "bounce_rate": 1500, "click_through_rate": 1500, "cost_per_click": 1500, "cost_per_thousand_impressions": 1500, "return_on_ad_spend": 1500, "spend": 1500} |
| cost_per_thousand_impressions | {"assists": 1500, "average_position": 1500, "bounce_rate": 1500, "click_through_rate": 1500, "cost_per_click": 1500, "cost_per_conversion": 1500, "return_on_ad_spend": 1500, "spend": 1500} |
| return_on_ad_spend | {"assists": 1500, "average_position": 1500, "bounce_rate": 1500, "click_through_rate": 1500, "cost_per_click": 1500, "cost_per_conversion": 1500, "cost_per_thousand_impressions": 1500, "spend": 1500} |
| spend | {"assists": 1500, "average_position": 1500, "bounce_rate": 1500, "click_through_rate": 1500, "cost_per_click": 1500, "cost_per_conversion": 1500, "cost_per_thousand_impressions": 1500, "return_on_ad_spend": 1500} |

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

无。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-006_stg_microsoft_ads__campaign_report.md`。
- 重跑：`records/020_reruns_impl-006_stg_microsoft_ads__campaign_report.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
