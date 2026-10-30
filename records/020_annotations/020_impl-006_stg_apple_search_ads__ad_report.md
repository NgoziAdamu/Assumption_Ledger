# impl-006 / stg_apple_search_ads__ad_report（全量）

## 结论

主要原因：**D**；把握：高。四个tap和cost衍生指标均为NULL占位。

参与因素：无。标记：已披露（D占位部分）。

## 差异与归因依据

taps、impressions、local_spend_amount、conversions和new_downloads均在源schema中；代码未对可计算性作判断，直接四列NULL。各单修1500格。

层：staging；比较库schema：staging；评测键：ad_id。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml:448–490`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_apple_search_ads__ad_report.sql:1–28`；SHA-256 `3aa03041cbf6a4df1f82f0a5837543257bd5971008b1819ce18f25d39b2d331c`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/staging/stg_apple_search_ads__ad_report.sql:1–183`；SHA-256 `e577a921e5ef20c50034983b0d5466df392e407f69630498f83bcda9b098b512`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- cost_per_conversion（agent SQL 第23行起）：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_conversion
```
→
```sql
CAST(CASE WHEN (CASE WHEN conversions = TRUE THEN 1 WHEN conversions = FALSE THEN 0 WHEN CAST(COALESCE(conversions, 0) AS INT) < 0 THEN 0 ELSE CAST(conversions AS INT) END) <= 0 THEN 0.0 WHEN local_spend_amount IS NULL OR local_spend_amount < 0 THEN 0.0 ELSE ROUND(ROUND(CASE WHEN local_spend_amount IS NULL THEN 0.0 WHEN local_spend_amount > 999999999999.99 THEN 999999999999.99 ELSE local_spend_amount END, 2) / (CASE WHEN conversions = TRUE THEN 1 WHEN conversions = FALSE THEN 0 WHEN CAST(COALESCE(conversions, 0) AS INT) < 0 THEN 0 ELSE CAST(conversions AS INT) END), 2) END AS DOUBLE) AS cost_per_conversion
```

- cost_per_download（agent SQL 第24行起）：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_download
```
→
```sql
CAST(CASE WHEN new_downloads IS NULL OR new_downloads <= 0 THEN 0.0 WHEN local_spend_amount IS NULL OR local_spend_amount < 0 THEN 0.0 ELSE ROUND(ROUND(CASE WHEN local_spend_amount IS NULL THEN 0.0 WHEN local_spend_amount > 999999999999.99 THEN 999999999999.99 ELSE local_spend_amount END, 2) / new_downloads, 2) END AS DOUBLE) AS cost_per_download
```

- cost_per_tap（agent SQL 第22行起）：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_tap
```
→
```sql
CAST(CASE WHEN taps IS NULL OR taps <= 0 THEN 0.0 WHEN local_spend_amount IS NULL OR local_spend_amount < 0 THEN 0.0 ELSE ROUND(ROUND(CASE WHEN local_spend_amount IS NULL THEN 0.0 WHEN local_spend_amount > 999999999999.99 THEN 999999999999.99 ELSE local_spend_amount END, 2) / taps, 2) END AS DOUBLE) AS cost_per_tap
```

- tap_through_rate（agent SQL 第21行起）：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS tap_through_rate
```
→
```sql
CAST(CASE WHEN impressions IS NULL OR impressions <= 0 THEN 0.0 WHEN taps IS NULL OR taps < 0 THEN 0.0 ELSE ROUND((CAST(taps AS DECIMAL(18, 3)) / CAST(impressions AS DECIMAL(18, 3))) * 100, 4) END AS DOUBLE) AS tap_through_rate
```

## agent可见证据与不确定性

不确定性四档：**只有通用策略说明**。

event 97（args.final_thought）：对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

完整事件扫描数：99；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | stg_apple_search_ads__ad_report | False |
| 12 | 11 | apple_search_ad_report_data | False |
| 16 | 15 | apple_search_ad_report_data | False |
| 18 | 17 | apple_search_ad_report_data | False |
| 38 | 37 | stg_apple_search_ads__ad_report | False |
| 82 | 81 | stg_apple_search_ads__ad_report | False |
| 86 | 85 | stg_apple_search_ads__ad_report | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：2；核实代价档：多条查询。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='apple_search_ad_report_data') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["raw", "apple_search_ad_report_data", "date", "VARCHAR"], ["raw", "apple_search_ad_report_data", "campaign_id", "VARCHAR"], ["raw", "apple_search_ad_report_data", "ad_group_id", "VARCHAR"], ["raw", "apple_search_ad_report_data", "ad_id", "VARCHAR"], ["raw", "apple_search_ad_report_data", "impressions", "BIGINT"], ["raw", "apple_search_ad_report_data", "local_spend_amount", "DOUBLE"], ["raw", "apple_search_ad_report_data", "local_spend_currency", "DOUBLE"], ["raw", "apple_search_ad_report_data", "new_downloads", "BIGINT"], ["raw", "apple_search_ad_report_data", "redownloads", "BOOLEAN"], ["raw", "apple_search_ad_report_data", "tap_installs", "BOOLEAN"], ["raw", "apple_search_ad_report_data", "tap_new_downloads", "BOOLEAN"], ["raw", "apple_search_ad_report_data", "tap_redownloads", "BOOLEAN"], ["raw", "apple_search_ad_report_data", "taps", "BIGINT"], ["raw", "apple_search_ad_report_data", "conversions", "BIGINT"]]`

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT count(*) n FROM raw.apple_search_ad_report_data
```

结果：`[[1500]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=19 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025本表实际使用的raw.call_data也三侧一致（2500行、同内容哈希），不把其他Snowflake兼容表的类型改动归给本表。

## 固定时间与重跑

私有目录：`data/020_work/impl-006_stg_apple_search_ads__ad_report/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：1500行 / 6000格；重跑基线：1500行 / 6000格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:1500行/6000格 / L1:1500行/6000格 / L2:1500行/6000格 / L3:1500行/6000格 | 均未整表匹配 |
| cost_per_conversion | L0:1500行/4500格 / L1:1500行/4500格 / L2:1500行/4500格 / L3:1500行/4500格 | 均未整表匹配 |
| cost_per_download | L0:1500行/4500格 / L1:1500行/4500格 / L2:1500行/4500格 / L3:1500行/4500格 | 均未整表匹配 |
| cost_per_tap | L0:1500行/4500格 / L1:1500行/4500格 / L2:1500行/4500格 / L3:1500行/4500格 | 均未整表匹配 |
| tap_through_rate | L0:1500行/4500格 / L1:1500行/4500格 / L2:1500行/4500格 / L3:1500行/4500格 | 均未整表匹配 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {"cost_per_conversion": 1500, "cost_per_download": 1500, "cost_per_tap": 1500, "tap_through_rate": 1500} |
| cost_per_conversion | {"cost_per_download": 1500, "cost_per_tap": 1500, "tap_through_rate": 1500} |
| cost_per_download | {"cost_per_conversion": 1500, "cost_per_tap": 1500, "tap_through_rate": 1500} |
| cost_per_tap | {"cost_per_conversion": 1500, "cost_per_download": 1500, "tap_through_rate": 1500} |
| tap_through_rate | {"cost_per_conversion": 1500, "cost_per_download": 1500, "cost_per_tap": 1500} |

本表全部重跑证据文件：`records/020_reruns_impl-006_stg_apple_search_ads__ad_report.json`。续做重跑私有副本在`data/020_resume_work/`。

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

无。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-006_stg_apple_search_ads__ad_report.md`。
- 重跑：`records/020_reruns_impl-006_stg_apple_search_ads__ad_report.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
