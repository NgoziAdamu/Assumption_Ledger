> **暂停检查点／待复核草稿**：用户于 2026-10-29 要求暂停。此文件尚未通过任务020最终复核，请勿作为正式定稿使用。

# impl-006 / stg_facebook_ads__ad_report（全量）

## 结论

主要原因：**D**；把握：高。spend及CTR/CPC/CPM直接置空。

参与因素：无。标记：已披露。

## 差异与归因依据

原始spend和inline_link_clicks/impressions均存在；占位不是源数据缺失导致。逐列单改均减少1000格。

层：staging；比较库schema：staging；评测键：ad_id。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml:648–698`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_facebook_ads__ad_report.sql:1–19`；SHA-256 `8a74e1e95f24afb2f94758911306ba00681f8dd8d4767976c20db229d98be6be`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/staging/stg_facebook_ads__ad_report.sql:1–103`；SHA-256 `5bb255e7e1a8c9d1de41ddccf3437f075e218b268721e3cf5a942cda41b85e1a`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- click_through_rate：
```sql
CAST(NULL::INTEGER AS INTEGER) AS click_through_rate
```
→
```sql
CAST(CASE WHEN impressions IS NULL OR impressions <= 0 THEN 0 WHEN inline_link_clicks IS NULL OR inline_link_clicks < 0 THEN 0 ELSE ROUND((CAST(inline_link_clicks AS DECIMAL(18, 3)) / CAST(impressions AS DECIMAL(18, 3))) * 100, 4) END AS INT) AS click_through_rate
```

- cost_per_click：
```sql
CAST(NULL::INTEGER AS INTEGER) AS cost_per_click
```
→
```sql
CAST(CASE WHEN inline_link_clicks IS NULL OR inline_link_clicks <= 0 THEN 0 WHEN spend IS NULL OR spend < 0 THEN 0 ELSE ROUND(ROUND(CASE WHEN spend IS NULL THEN 0.0 WHEN spend > 999999999999.99 THEN 999999999999.99 ELSE spend END, 2) / inline_link_clicks, 2) END AS INT) AS cost_per_click
```

- cost_per_thousand_impressions：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_thousand_impressions
```
→
```sql
CAST(CASE WHEN impressions IS NULL OR impressions <= 0 THEN 0.0 WHEN spend IS NULL OR spend < 0 THEN 0.0 ELSE ROUND(ROUND(CASE WHEN spend IS NULL THEN 0.0 WHEN spend > 999999999999.99 THEN 999999999999.99 ELSE spend END, 2) / CAST(impressions AS DECIMAL(18, 3)) * 1000.0, 2) END AS DOUBLE) AS cost_per_thousand_impressions
```

- spend：
```sql
CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS spend
```
→
```sql
CAST(ROUND(CASE WHEN spend IS NULL THEN 0.0 WHEN spend < 0 THEN 0.0 WHEN spend > 999999999999.99 THEN 999999999999.99 ELSE spend END, 2) AS DECIMAL(18, 2)) AS spend
```

## agent可见证据与不确定性

不确定性四档：**只有通用策略说明**。

event 97（args.final_thought）：对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

完整事件扫描数：99；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | stg_facebook_ads__ad_report | False |
| 12 | 11 | facebook_ads_basic_ad_data | False |
| 16 | 15 | facebook_ads_basic_ad_data | False |
| 18 | 17 | facebook_ads_basic_ad_data | False |
| 38 | 37 | stg_facebook_ads__ad_report | False |
| 82 | 81 | stg_facebook_ads__ad_report | False |
| 86 | 85 | stg_facebook_ads__ad_report | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：2；核实代价档：多条查询。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='facebook_ads_basic_ad_data') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["raw", "facebook_ads_basic_ad_data", "ad_id", "BIGINT"], ["raw", "facebook_ads_basic_ad_data", "date", "VARCHAR"], ["raw", "facebook_ads_basic_ad_data", "account_id", "BIGINT"], ["raw", "facebook_ads_basic_ad_data", "impressions", "BIGINT"], ["raw", "facebook_ads_basic_ad_data", "inline_link_clicks", "BIGINT"], ["raw", "facebook_ads_basic_ad_data", "spend", "DOUBLE"]]`

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT count(*) n,count(*) FILTER(WHERE "impressions" IS NULL) AS c0_null,count(*) FILTER(WHERE "impressions" IS NOT NULL AND TRY_CAST("impressions" AS DOUBLE) IS NULL) AS c1_not_numeric,count(*) FILTER(WHERE "spend" IS NULL) AS c2_null,count(*) FILTER(WHERE "spend" IS NOT NULL AND TRY_CAST("spend" AS DOUBLE) IS NULL) AS c3_not_numeric FROM raw.facebook_ads_basic_ad_data
```

结果：`[[1000, 0, 0, 0, 0]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=22 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025的agent修改raw不适用“不可评估”，本次使用留存raw。

## 固定时间与重跑

私有目录：`data/020_work/impl-006_stg_facebook_ads__ad_report/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：1000行 / 4000格；重跑基线：1000行 / 4000格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:1000行/4000格 / L1:1000行/4000格 / L2:1000行/4000格 / L3:1000行/4000格 | 均未整表匹配 |
| click_through_rate | L0:1000行/3000格 / L1:1000行/3000格 / L2:1000行/3000格 / L3:1000行/3000格 | 均未整表匹配 |
| cost_per_click | L0:1000行/3000格 / L1:1000行/3000格 / L2:1000行/3000格 / L3:1000行/3000格 | 均未整表匹配 |
| cost_per_thousand_impressions | L0:1000行/3000格 / L1:1000行/3000格 / L2:1000行/3000格 / L3:1000行/3000格 | 均未整表匹配 |
| spend | L0:1000行/3000格 / L1:1000行/3000格 / L2:1000行/3000格 / L3:1000行/3000格 | 均未整表匹配 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {"click_through_rate": 1000, "cost_per_click": 1000, "cost_per_thousand_impressions": 1000, "spend": 1000} |
| click_through_rate | {"cost_per_click": 1000, "cost_per_thousand_impressions": 1000, "spend": 1000} |
| cost_per_click | {"click_through_rate": 1000, "cost_per_thousand_impressions": 1000, "spend": 1000} |
| cost_per_thousand_impressions | {"click_through_rate": 1000, "cost_per_click": 1000, "spend": 1000} |
| spend | {"click_through_rate": 1000, "cost_per_click": 1000, "cost_per_thousand_impressions": 1000} |

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

无。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-006_stg_facebook_ads__ad_report.md`。
- 重跑：`records/020_reruns_impl-006_stg_facebook_ads__ad_report.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
