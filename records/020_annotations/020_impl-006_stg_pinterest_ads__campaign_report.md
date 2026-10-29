> **暂停检查点／待复核草稿**：用户于 2026-10-29 要求暂停。此文件尚未通过任务020最终复核，请勿作为正式定稿使用。

# impl-006 / stg_pinterest_ads__campaign_report（全量）

## 结论

主要原因：**多因并列（A、D）**；把握：中。Pinterest可计算指标占位、impressions合并选择和无源字段默认值并列。

参与因素：无。标记：已披露。

## 差异与归因依据

impression_1与impression_2如何合并没有契约映射，数据未给唯一业务结论，A；无源outbound/pin/saves/close_ups/video默认0或NULL为A；clicks及金额/率指标有候选输入却NULL归D。

层：staging；比较库schema：staging；评测键：campaign_id。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml:1047–1091`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_pinterest_ads__campaign_report.sql:1–29`；SHA-256 `9a0f2407bc8eda2fd1e66225ce4bfa13d7395f1437ac1214f2ac84f78a4ce25e`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/staging/stg_pinterest_ads__campaign_report.sql:1–61`；SHA-256 `6cf302bac9cbd25aaa82643d49c8bdf45c045c51bc0fdff7f99a075846b6d4ca`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- click_through_rate：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS click_through_rate
```
→
```sql
CASE WHEN (CAST(COALESCE(impression_1, '0') AS INT) + CAST(COALESCE(impression_2, '0') AS INT)) > 0 THEN ROUND((CAST(CAST(COALESCE(clickthrough_1, '0') AS INT) + CAST(COALESCE(clickthrough_2, '0') AS INT) AS DECIMAL(18, 3)) / CAST(CAST(COALESCE(impression_1, '0') AS INT) + CAST(COALESCE(impression_2, '0') AS INT) AS DECIMAL(18, 3))) * 100, 4) ELSE 0 END AS click_through_rate
```

- clicks：
```sql
CAST(NULL::INTEGER AS INTEGER) AS clicks
```
→
```sql
CAST(CAST(COALESCE(clickthrough_1, '0') AS INT) + CAST(COALESCE(clickthrough_2, '0') AS INT) AS INT) AS clicks
```

- close_ups：
```sql
CAST(NULL::INTEGER AS INTEGER) AS close_ups
```
→
```sql
CAST(0 AS INT) AS close_ups
```

- cost_per_click：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_click
```
→
```sql
CASE WHEN (CAST(COALESCE(clickthrough_1, '0') AS INT) + CAST(COALESCE(clickthrough_2, '0') AS INT)) > 0 THEN ROUND((spend_in_micro_dollar / 1000000.0) / (CAST(COALESCE(clickthrough_1, '0') AS INT) + CAST(COALESCE(clickthrough_2, '0') AS INT)), 2) ELSE 0 END AS cost_per_click
```

- cost_per_conversion：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_conversion
```
→
```sql
CASE WHEN CAST(COALESCE(total_conversions, '0') AS INT) > 0 THEN ROUND((spend_in_micro_dollar / 1000000.0) / CAST(COALESCE(total_conversions, '0') AS INT), 2) ELSE 0 END AS cost_per_conversion
```

- cost_per_thousand_impressions：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_thousand_impressions
```
→
```sql
CASE WHEN (CAST(COALESCE(impression_1, '0') AS INT) + CAST(COALESCE(impression_2, '0') AS INT)) > 0 THEN ROUND(((spend_in_micro_dollar / 1000000.0) / (CAST(COALESCE(impression_1, '0') AS INT) + CAST(COALESCE(impression_2, '0') AS INT))) * 1000, 2) ELSE 0 END AS cost_per_thousand_impressions
```

- impressions：
```sql
CAST(TRY_CAST("impression_1" AS BIGINT) AS INTEGER) AS impressions
```
→
```sql
CAST(CAST(COALESCE(impression_1, '0') AS INT) + CAST(COALESCE(impression_2, '0') AS INT) AS INT) AS impressions
```

- outbound_clicks：
```sql
CAST(NULL::INTEGER AS INTEGER) AS outbound_clicks
```
→
```sql
CAST(0 AS INT) AS outbound_clicks
```

- pin_clicks：
```sql
CAST(NULL::INTEGER AS INTEGER) AS pin_clicks
```
→
```sql
CAST(0 AS INT) AS pin_clicks
```

- saves：
```sql
CAST(NULL::INTEGER AS INTEGER) AS saves
```
→
```sql
CAST(0 AS INT) AS saves
```

- spend：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS spend
```
→
```sql
ROUND(spend_in_micro_dollar / 1000000.0, 2) AS spend
```

- total_conversions_value：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS total_conversions_value
```
→
```sql
ROUND(total_conversions_value_in_micro_dollar / 1000000.0, 2) AS total_conversions_value
```

- video_views：
```sql
CAST(NULL::INTEGER AS INTEGER) AS video_views
```
→
```sql
CAST(0 AS INT) AS video_views
```

## agent可见证据与不确定性

不确定性四档：**click_through_rate=只有通用策略说明；clicks=只有通用策略说明；close_ups=只有通用策略说明；cost_per_click=只有通用策略说明；cost_per_conversion=只有通用策略说明；cost_per_thousand_impressions=只有通用策略说明；impressions=只有通用策略说明；outbound_clicks=只有通用策略说明；pin_clicks=只有通用策略说明；saves=只有通用策略说明；spend=只有通用策略说明；total_conversions_value=只有通用策略说明；video_views=只有通用策略说明**。

event 97（args.final_thought）：对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

完整事件扫描数：99；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | stg_pinterest_ads__campaign_report | False |
| 12 | 11 | pinterest_campaign_report_data | False |
| 16 | 15 | pinterest_campaign_report_data | False |
| 18 | 17 | pinterest_campaign_report_data | False |
| 38 | 37 | stg_pinterest_ads__campaign_report | False |
| 82 | 81 | stg_pinterest_ads__campaign_report | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：2；核实代价档：多条查询。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='pinterest_campaign_report_data') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["raw", "pinterest_campaign_report_data", "date", "VARCHAR"], ["raw", "pinterest_campaign_report_data", "campaign_id", "VARCHAR"], ["raw", "pinterest_campaign_report_data", "campaign_name", "VARCHAR"], ["raw", "pinterest_campaign_report_data", "campaign_status", "VARCHAR"], ["raw", "pinterest_campaign_report_data", "advertiser_id", "VARCHAR"], ["raw", "pinterest_campaign_report_data", "impression_1", "BIGINT"], ["raw", "pinterest_campaign_report_data", "impression_2", "BIGINT"], ["raw", "pinterest_campaign_report_data", "clickthrough_1", "BIGINT"], ["raw", "pinterest_campaign_report_data", "clickthrough_2", "BIGINT"], ["raw", "pinterest_campaign_report_data", "spend_in_micro_dollar", "BIGINT"], ["raw", "pinterest_campaign_report_data", "total_conversions", "BIGINT"], ["raw", "pinterest_campaign_report_data", "total_conversions_quantity", "BIGINT"], ["raw", "pinterest_campaign_report_data", "total_conversions_value_in_micro_dollar", "BIGINT"]]`

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT count(*) n,count(*) FILTER(WHERE "impression_1" IS NULL) AS c0_null,count(*) FILTER(WHERE "impression_1" IS NOT NULL AND TRY_CAST("impression_1" AS DOUBLE) IS NULL) AS c1_not_numeric,count(*) FILTER(WHERE "total_conversions" IS NULL) AS c2_null,count(*) FILTER(WHERE "total_conversions" IS NOT NULL AND TRY_CAST("total_conversions" AS DOUBLE) IS NULL) AS c3_not_numeric FROM raw.pinterest_campaign_report_data
```

结果：`[[900, 0, 0, 0, 0]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=28 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025的agent修改raw不适用“不可评估”，本次使用留存raw。

## 固定时间与重跑

私有目录：`data/020_work/impl-006_stg_pinterest_ads__campaign_report/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：900行 / 11700格；重跑基线：900行 / 11700格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:900行/11700格 / L1:900行/11700格 / L2:900行/11700格 / L3:900行/11700格 | 均未整表匹配 |
| click_through_rate | L0:900行/10800格 / L1:900行/10800格 / L2:900行/10800格 / L3:900行/10800格 | 均未整表匹配 |
| clicks | L0:900行/10800格 / L1:900行/10800格 / L2:900行/10800格 / L3:900行/10800格 | 均未整表匹配 |
| close_ups | L0:900行/10800格 / L1:900行/10800格 / L2:900行/10800格 / L3:900行/10800格 | 均未整表匹配 |
| cost_per_click | L0:900行/10800格 / L1:900行/10800格 / L2:900行/10800格 / L3:900行/10800格 | 均未整表匹配 |
| cost_per_conversion | L0:900行/10800格 / L1:900行/10800格 / L2:900行/10800格 / L3:900行/10800格 | 均未整表匹配 |
| cost_per_thousand_impressions | L0:900行/10800格 / L1:900行/10800格 / L2:900行/10800格 / L3:900行/10800格 | 均未整表匹配 |
| impressions | L0:900行/10800格 / L1:900行/10800格 / L2:900行/10800格 / L3:900行/10800格 | 均未整表匹配 |
| outbound_clicks | L0:900行/10800格 / L1:900行/10800格 / L2:900行/10800格 / L3:900行/10800格 | 均未整表匹配 |
| pin_clicks | L0:900行/10800格 / L1:900行/10800格 / L2:900行/10800格 / L3:900行/10800格 | 均未整表匹配 |
| saves | L0:900行/10800格 / L1:900行/10800格 / L2:900行/10800格 / L3:900行/10800格 | 均未整表匹配 |
| spend | L0:900行/10800格 / L1:900行/10800格 / L2:900行/10800格 / L3:900行/10800格 | 均未整表匹配 |
| total_conversions_value | L0:900行/10800格 / L1:900行/10800格 / L2:900行/10800格 / L3:900行/10800格 | 均未整表匹配 |
| video_views | L0:900行/10800格 / L1:900行/10800格 / L2:900行/10800格 / L3:900行/10800格 | 均未整表匹配 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {"click_through_rate": 900, "clicks": 900, "close_ups": 900, "cost_per_click": 900, "cost_per_conversion": 900, "cost_per_thousand_impressions": 900, "impressions": 900, "outbound_clicks": 900, "pin_clicks": 900, "saves": 900, "spend": 900, "total_conversions_value": 900, "video_views": 900} |
| click_through_rate | {"clicks": 900, "close_ups": 900, "cost_per_click": 900, "cost_per_conversion": 900, "cost_per_thousand_impressions": 900, "impressions": 900, "outbound_clicks": 900, "pin_clicks": 900, "saves": 900, "spend": 900, "total_conversions_value": 900, "video_views": 900} |
| clicks | {"click_through_rate": 900, "close_ups": 900, "cost_per_click": 900, "cost_per_conversion": 900, "cost_per_thousand_impressions": 900, "impressions": 900, "outbound_clicks": 900, "pin_clicks": 900, "saves": 900, "spend": 900, "total_conversions_value": 900, "video_views": 900} |
| close_ups | {"click_through_rate": 900, "clicks": 900, "cost_per_click": 900, "cost_per_conversion": 900, "cost_per_thousand_impressions": 900, "impressions": 900, "outbound_clicks": 900, "pin_clicks": 900, "saves": 900, "spend": 900, "total_conversions_value": 900, "video_views": 900} |
| cost_per_click | {"click_through_rate": 900, "clicks": 900, "close_ups": 900, "cost_per_conversion": 900, "cost_per_thousand_impressions": 900, "impressions": 900, "outbound_clicks": 900, "pin_clicks": 900, "saves": 900, "spend": 900, "total_conversions_value": 900, "video_views": 900} |
| cost_per_conversion | {"click_through_rate": 900, "clicks": 900, "close_ups": 900, "cost_per_click": 900, "cost_per_thousand_impressions": 900, "impressions": 900, "outbound_clicks": 900, "pin_clicks": 900, "saves": 900, "spend": 900, "total_conversions_value": 900, "video_views": 900} |
| cost_per_thousand_impressions | {"click_through_rate": 900, "clicks": 900, "close_ups": 900, "cost_per_click": 900, "cost_per_conversion": 900, "impressions": 900, "outbound_clicks": 900, "pin_clicks": 900, "saves": 900, "spend": 900, "total_conversions_value": 900, "video_views": 900} |
| impressions | {"click_through_rate": 900, "clicks": 900, "close_ups": 900, "cost_per_click": 900, "cost_per_conversion": 900, "cost_per_thousand_impressions": 900, "outbound_clicks": 900, "pin_clicks": 900, "saves": 900, "spend": 900, "total_conversions_value": 900, "video_views": 900} |
| outbound_clicks | {"click_through_rate": 900, "clicks": 900, "close_ups": 900, "cost_per_click": 900, "cost_per_conversion": 900, "cost_per_thousand_impressions": 900, "impressions": 900, "pin_clicks": 900, "saves": 900, "spend": 900, "total_conversions_value": 900, "video_views": 900} |
| pin_clicks | {"click_through_rate": 900, "clicks": 900, "close_ups": 900, "cost_per_click": 900, "cost_per_conversion": 900, "cost_per_thousand_impressions": 900, "impressions": 900, "outbound_clicks": 900, "saves": 900, "spend": 900, "total_conversions_value": 900, "video_views": 900} |
| saves | {"click_through_rate": 900, "clicks": 900, "close_ups": 900, "cost_per_click": 900, "cost_per_conversion": 900, "cost_per_thousand_impressions": 900, "impressions": 900, "outbound_clicks": 900, "pin_clicks": 900, "spend": 900, "total_conversions_value": 900, "video_views": 900} |
| spend | {"click_through_rate": 900, "clicks": 900, "close_ups": 900, "cost_per_click": 900, "cost_per_conversion": 900, "cost_per_thousand_impressions": 900, "impressions": 900, "outbound_clicks": 900, "pin_clicks": 900, "saves": 900, "total_conversions_value": 900, "video_views": 900} |
| total_conversions_value | {"click_through_rate": 900, "clicks": 900, "close_ups": 900, "cost_per_click": 900, "cost_per_conversion": 900, "cost_per_thousand_impressions": 900, "impressions": 900, "outbound_clicks": 900, "pin_clicks": 900, "saves": 900, "spend": 900, "video_views": 900} |
| video_views | {"click_through_rate": 900, "clicks": 900, "close_ups": 900, "cost_per_click": 900, "cost_per_conversion": 900, "cost_per_thousand_impressions": 900, "impressions": 900, "outbound_clicks": 900, "pin_clicks": 900, "saves": 900, "spend": 900, "total_conversions_value": 900} |

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

无。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-006_stg_pinterest_ads__campaign_report.md`。
- 重跑：`records/020_reruns_impl-006_stg_pinterest_ads__campaign_report.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
