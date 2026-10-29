> **暂停检查点／待复核草稿**：用户于 2026-10-29 要求暂停。此文件尚未通过任务020最终复核，请勿作为正式定稿使用。

# impl-006 / stg_apple_search_ads__campaign_report（全量）

## 结论

主要原因：**D**；把握：高。campaign_id有原始id候选却直接填NULL，导致两侧键不重合。

参与因素：无。标记：已披露。

## 差异与归因依据

event19的别名候选未覆盖id就返回NULL；raw.apple_search_campaign_report_data有id。单改ID使3000行规模降至1500，其余计算指标等被键差异遮蔽。

层：staging；比较库schema：staging；评测键：campaign_id, date_day。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml:491–580`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_apple_search_ads__campaign_report.sql:1–33`；SHA-256 `3657ed59cf5f5f4b941aca807eeefd8ac11f05df46b8df381f0ced88249304d2`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/staging/stg_apple_search_ads__campaign_report.sql:1–198`；SHA-256 `9e0eab5d253412c2125aa37d9da93d9aef6a58a5c5a8fed68b9ea04d166cc678`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- campaign_id：
```sql
CAST(NULL::VARCHAR AS VARCHAR) AS campaign_id
```
→
```sql
CAST(TRIM(CAST(id AS TEXT)) AS TEXT) AS campaign_id
```

## agent可见证据与不确定性

不确定性四档：**只有通用策略说明**。

event 97（args.final_thought）：对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

完整事件扫描数：99；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | stg_apple_search_ads__campaign_report | False |
| 12 | 11 | apple_search_campaign_report_data | False |
| 16 | 15 | apple_search_campaign_report_data | False |
| 18 | 17 | apple_search_campaign_report_data | False |
| 38 | 37 | stg_apple_search_ads__campaign_report | False |
| 82 | 81 | stg_apple_search_ads__campaign_report | False |
| 86 | 85 | stg_apple_search_ads__campaign_report | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：2；核实代价档：多条查询。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='apple_search_campaign_report_data') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["raw", "apple_search_campaign_report_data", "date", "VARCHAR"], ["raw", "apple_search_campaign_report_data", "id", "VARCHAR"], ["raw", "apple_search_campaign_report_data", "avg_cpa_amount", "BIGINT"], ["raw", "apple_search_campaign_report_data", "avg_cpa_currency", "VARCHAR"], ["raw", "apple_search_campaign_report_data", "avg_cpt_amount", "BIGINT"], ["raw", "apple_search_campaign_report_data", "avg_cpt_currency", "VARCHAR"], ["raw", "apple_search_campaign_report_data", "conversion_rate", "BIGINT"], ["raw", "apple_search_campaign_report_data", "conversions", "BIGINT"], ["raw", "apple_search_campaign_report_data", "impressions", "BIGINT"], ["raw", "apple_search_campaign_report_data", "lat_off_installs", "BOOLEAN"], ["raw", "apple_search_campaign_report_data", "lat_on_installs", "BOOLEAN"], ["raw", "apple_search_campaign_report_data", "local_spend_amount", "DOUBLE"], ["raw", "apple_search_campaign_report_data", "local_spend_currency", "DOUBLE"], ["raw", "apple_search_campaign_report_data", "new_downloads", "BIGINT"], ["raw", "apple_search_campaign_report_data", "redownloads", "BOOLEAN"], ["raw", "apple_search_campaign_report_data", "tap_through_rate", "BOOLEAN"], ["raw", "apple_search_campaign_report_data", "taps", "BIGINT"], ["raw", "apple_search_campaign_report_data", "tap_installs", "BOOLEAN"], ["raw", "apple_search_campaign_report_data", "tap_new_downloads", "BOOLEAN"], ["raw", "apple_search_campaign_report_data", "tap_redownloads", "BOOLEAN"]]`

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT count(*) n FROM raw.apple_search_campaign_report_data
```

结果：`[[1500]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=20 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025的agent修改raw不适用“不可评估”，本次使用留存raw。

## 固定时间与重跑

私有目录：`data/020_work/impl-006_stg_apple_search_ads__campaign_report/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：3000行 / 63000格；重跑基线：3000行 / 63000格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:3000行/63000格 / L1:3000行/63000格 / L2:3000行/63000格 / L3:3000行/63000格 | 均未整表匹配 |
| campaign_id | L0:1500行/4500格 / L1:1500行/4500格 / L2:1500行/4500格 / L3:1500行/4500格 | 均未整表匹配 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {} |
| campaign_id | {"calculated_tap_through_rate": 1500, "cost_per_conversion": 1500, "cost_per_tap": 1500} |

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

无。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-006_stg_apple_search_ads__campaign_report.md`。
- 重跑：`records/020_reruns_impl-006_stg_apple_search_ads__campaign_report.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
