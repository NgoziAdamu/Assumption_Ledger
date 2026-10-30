# impl-006 / stg_apple_search_ads__ad_group_report（全量）

## 结论

主要原因：**多因并列（C、D）**；把握：高。货币代码验证遗漏与三个计算指标占位并列；转化率校验为次因。

参与因素：C：conversion_rate（减0行/1469格）。标记：已披露（D占位部分）。

## 差异与归因依据

契约直接规定avg_cpt/avg_cpa货币白名单/大写，遗漏归C；三个计算指标填NULL归D。五项各减少1500格并列；conversion_rate未按0–1置NULL为C，减少1469格。

层：staging；比较库schema：staging；评测键：ad_group_id。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml:351–447`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_apple_search_ads__ad_group_report.sql:1–33`；SHA-256 `7400b18f89a8dd63c5d987e407b9aa93822c8cce876642bdd85e1078d73c2821`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/staging/stg_apple_search_ads__ad_group_report.sql:1–206`；SHA-256 `64678775b7c88fcd614050963462f4d757ac8cfe2a3f15a9a8906e87e69ae7f3`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- avg_cpa_currency（agent SQL 第22行起）：
```sql
TRY_CAST("avg_cpa_currency" AS VARCHAR) AS avg_cpa_currency
```
→
```sql
CAST(CASE WHEN TRIM(avg_cpa_currency) IS NULL OR avg_cpa_currency = '' THEN NULL WHEN NOT UPPER(TRIM(avg_cpa_currency)) IN ('USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD') THEN NULL WHEN LENGTH(TRIM(avg_cpa_currency)) > 3 THEN NULL ELSE UPPER(TRIM(avg_cpa_currency)) END AS TEXT) AS avg_cpa_currency
```

- avg_cpt_currency（agent SQL 第20行起）：
```sql
TRY_CAST("avg_cpt_currency" AS VARCHAR) AS avg_cpt_currency
```
→
```sql
CAST(CASE WHEN TRIM(avg_cpt_currency) IS NULL OR avg_cpt_currency = '' THEN NULL WHEN NOT UPPER(TRIM(avg_cpt_currency)) IN ('USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD') THEN NULL WHEN LENGTH(TRIM(avg_cpt_currency)) > 3 THEN NULL ELSE UPPER(TRIM(avg_cpt_currency)) END AS TEXT) AS avg_cpt_currency
```

- calculated_tap_through_rate（agent SQL 第27行起）：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS calculated_tap_through_rate
```
→
```sql
CAST(CASE WHEN impressions IS NULL OR impressions <= 0 THEN 0.0 WHEN taps IS NULL OR taps < 0 THEN 0.0 ELSE ROUND((CAST(taps AS DECIMAL(18, 3)) / CAST(impressions AS DECIMAL(18, 3))) * 100, 4) END AS DOUBLE) AS calculated_tap_through_rate
```

- conversion_rate（agent SQL 第24行起）：
```sql
TRY_CAST("conversion_rate" AS DECIMAL(10,6)) AS conversion_rate
```
→
```sql
CAST(CASE WHEN conversion_rate IS NULL OR conversion_rate < 0 OR conversion_rate > 1.0 THEN NULL ELSE ROUND(conversion_rate, 6) END AS DECIMAL(10, 6)) AS conversion_rate
```

- cost_per_conversion（agent SQL 第29行起）：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_conversion
```
→
```sql
CAST(CASE WHEN conversions IS NULL OR conversions <= 0 THEN 0.0 WHEN local_spend_amount IS NULL OR local_spend_amount < 0 THEN 0.0 ELSE ROUND(ROUND(CASE WHEN local_spend_amount IS NULL THEN 0.0 WHEN local_spend_amount > 999999999999.99 THEN 999999999999.99 ELSE local_spend_amount END, 2) / conversions, 2) END AS DOUBLE) AS cost_per_conversion
```

- cost_per_tap（agent SQL 第28行起）：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_tap
```
→
```sql
CAST(CASE WHEN taps IS NULL OR taps <= 0 THEN 0.0 WHEN local_spend_amount IS NULL OR local_spend_amount < 0 THEN 0.0 ELSE ROUND(ROUND(CASE WHEN local_spend_amount IS NULL THEN 0.0 WHEN local_spend_amount > 999999999999.99 THEN 999999999999.99 ELSE local_spend_amount END, 2) / taps, 2) END AS DOUBLE) AS cost_per_tap
```

## agent可见证据与不确定性

不确定性四档：**avg_cpa_currency=看到了但没提；avg_cpt_currency=看到了但没提；calculated_tap_through_rate=只有通用策略说明；cost_per_conversion=只有通用策略说明；cost_per_tap=只有通用策略说明**。

event 97（args.final_thought）：对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。 event 97（args.final_thought）：脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。 各并列项单独分档：占位/缺省选择沿用适用的NULL通用披露；货币枚举校验遗漏只见event18相关列及实现，没有白名单处理说明，不能由数值TRY_CAST泛述推定已披露。

完整事件扫描数：99；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | stg_apple_search_ads__ad_group_report | False |
| 12 | 11 | apple_search_ad_group_report_data | False |
| 16 | 15 | apple_search_ad_group_report_data | False |
| 18 | 17 | apple_search_ad_group_report_data | False |
| 38 | 37 | stg_apple_search_ads__ad_group_report | False |
| 82 | 81 | stg_apple_search_ads__ad_group_report | False |
| 86 | 85 | stg_apple_search_ads__ad_group_report | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：2；核实代价档：多条查询。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='apple_search_ad_group_report_data') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["raw", "apple_search_ad_group_report_data", "ad_group_id", "VARCHAR"], ["raw", "apple_search_ad_group_report_data", "date", "VARCHAR"], ["raw", "apple_search_ad_group_report_data", "avg_cpa_amount", "BIGINT"], ["raw", "apple_search_ad_group_report_data", "avg_cpa_currency", "VARCHAR"], ["raw", "apple_search_ad_group_report_data", "avg_cpt_amount", "BIGINT"], ["raw", "apple_search_ad_group_report_data", "avg_cpt_currency", "VARCHAR"], ["raw", "apple_search_ad_group_report_data", "conversion_rate", "BIGINT"], ["raw", "apple_search_ad_group_report_data", "conversions", "BIGINT"], ["raw", "apple_search_ad_group_report_data", "impressions", "BIGINT"], ["raw", "apple_search_ad_group_report_data", "lat_off_installs", "BOOLEAN"], ["raw", "apple_search_ad_group_report_data", "lat_on_installs", "BOOLEAN"], ["raw", "apple_search_ad_group_report_data", "local_spend_amount", "DOUBLE"], ["raw", "apple_search_ad_group_report_data", "local_spend_currency", "DOUBLE"], ["raw", "apple_search_ad_group_report_data", "new_downloads", "BIGINT"], ["raw", "apple_search_ad_group_report_data", "redownloads", "BOOLEAN"], ["raw", "apple_search_ad_group_report_data", "tap_through_rate", "BOOLEAN"], ["raw", "apple_search_ad_group_report_data", "taps", "BIGINT"], ["raw", "apple_search_ad_group_report_data", "tap_installs", "BOOLEAN"], ["raw", "apple_search_ad_group_report_data", "tap_new_downloads", "BOOLEAN"], ["raw", "apple_search_ad_group_report_data", "tap_redownloads", "BOOLEAN"]]`

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT count(*) n,count(*) FILTER(WHERE "avg_cpa_currency" IS NULL) AS c0_null,count(*) FILTER(WHERE "avg_cpa_currency" IS NOT NULL AND TRY_CAST("avg_cpa_currency" AS DOUBLE) IS NULL) AS c1_not_numeric,count(*) FILTER(WHERE "avg_cpt_currency" IS NULL) AS c2_null,count(*) FILTER(WHERE "avg_cpt_currency" IS NOT NULL AND TRY_CAST("avg_cpt_currency" AS DOUBLE) IS NULL) AS c3_not_numeric,count(*) FILTER(WHERE "conversion_rate" IS NULL) AS c4_null,count(*) FILTER(WHERE "conversion_rate" IS NOT NULL AND TRY_CAST("conversion_rate" AS DOUBLE) IS NULL) AS c5_not_numeric,count(*) FILTER(WHERE "tap_through_rate" IS NULL) AS c6_null,count(*) FILTER(WHERE "tap_through_rate" IS NOT NULL AND TRY_CAST("tap_through_rate" AS DOUBLE) IS NULL) AS c7_not_numeric FROM raw.apple_search_ad_group_report_data
```

结果：`[[1500, 0, 1500, 0, 1500, 0, 0, 0, 0]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=18 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025本表实际使用的raw.call_data也三侧一致（2500行、同内容哈希），不把其他Snowflake兼容表的类型改动归给本表。

## 固定时间与重跑

私有目录：`data/020_work/impl-006_stg_apple_search_ads__ad_group_report/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：1500行 / 8969格；重跑基线：1500行 / 8969格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:1500行/8969格 / L1:1500行/8969格 / L2:1500行/8969格 / L3:1500行/8969格 | 均未整表匹配 |
| avg_cpa_currency | L0:1500行/7469格 / L1:1500行/7469格 / L2:1500行/7469格 / L3:1500行/7469格 | 均未整表匹配 |
| avg_cpt_currency | L0:1500行/7469格 / L1:1500行/7469格 / L2:1500行/7469格 / L3:1500行/7469格 | 均未整表匹配 |
| calculated_tap_through_rate | L0:1500行/7469格 / L1:1500行/7469格 / L2:1500行/7469格 / L3:1500行/7469格 | 均未整表匹配 |
| conversion_rate | L0:1500行/7500格 / L1:1500行/7500格 / L2:1500行/7500格 / L3:1500行/7500格 | 均未整表匹配 |
| cost_per_conversion | L0:1500行/7469格 / L1:1500行/7469格 / L2:1500行/7469格 / L3:1500行/7469格 | 均未整表匹配 |
| cost_per_tap | L0:1500行/7469格 / L1:1500行/7469格 / L2:1500行/7469格 / L3:1500行/7469格 | 均未整表匹配 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {"avg_cpa_currency": 1500, "avg_cpt_currency": 1500, "calculated_tap_through_rate": 1500, "conversion_rate": 1469, "cost_per_conversion": 1500, "cost_per_tap": 1500} |
| avg_cpa_currency | {"avg_cpt_currency": 1500, "calculated_tap_through_rate": 1500, "conversion_rate": 1469, "cost_per_conversion": 1500, "cost_per_tap": 1500} |
| avg_cpt_currency | {"avg_cpa_currency": 1500, "calculated_tap_through_rate": 1500, "conversion_rate": 1469, "cost_per_conversion": 1500, "cost_per_tap": 1500} |
| calculated_tap_through_rate | {"avg_cpa_currency": 1500, "avg_cpt_currency": 1500, "conversion_rate": 1469, "cost_per_conversion": 1500, "cost_per_tap": 1500} |
| conversion_rate | {"avg_cpa_currency": 1500, "avg_cpt_currency": 1500, "calculated_tap_through_rate": 1500, "cost_per_conversion": 1500, "cost_per_tap": 1500} |
| cost_per_conversion | {"avg_cpa_currency": 1500, "avg_cpt_currency": 1500, "calculated_tap_through_rate": 1500, "conversion_rate": 1469, "cost_per_tap": 1500} |
| cost_per_tap | {"avg_cpa_currency": 1500, "avg_cpt_currency": 1500, "calculated_tap_through_rate": 1500, "conversion_rate": 1469, "cost_per_conversion": 1500} |

本表全部重跑证据文件：`records/020_reruns_impl-006_stg_apple_search_ads__ad_group_report.json`。续做重跑私有副本在`data/020_resume_work/`。

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

无。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-006_stg_apple_search_ads__ad_group_report.md`。
- 重跑：`records/020_reruns_impl-006_stg_apple_search_ads__ad_group_report.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
