# impl-006 / stg_google_ads__ad_group_report（全量）

## 结论

主要原因：**A**；把握：中。ad_group_id取base_ad_group资源路径还是原始id，契约未定。

参与因素：无。标记：无。

## 差异与归因依据

原始id与history直接匹配15/715，base_ad_group直接匹配0；但去掉资源路径前缀后base_ad_group与history匹配715/715。因此不能据第一次全串连接结果声称原列错误，也不能用gold的id选择判U。字段映射/表示有歧义，单改id使1430→705行。

层：staging；比较库schema：staging；评测键：account_id, ad_group_id, date_day, ad_network_type, device。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml:733–769`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_google_ads__ad_group_report.sql:1–20`；SHA-256 `d8295f7141fa275d3ff714fb82fc97b9c48ec819ca446df9a67646a160165cb8`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/staging/stg_google_ads__ad_group_report.sql:1–48`；SHA-256 `b240591bdfd03cc8d3f778c798d0e10da8278b2162fdeaa5653c7aaf6d810b27`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- ad_group_id（agent SQL 第9行起）：
```sql
CAST(TRY_CAST("base_ad_group" AS VARCHAR) AS VARCHAR(20)) AS ad_group_id
```
→
```sql
CAST(id AS TEXT) AS ad_group_id
```

## agent可见证据与不确定性

不确定性四档：**看到了但没提**。

event18输出base_ad_group和id列，event29生成Google staging映射；未解释为何选base_ad_group。event97的缺列NULL策略不涉及两个已有源列之间的选择。

完整事件扫描数：99；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | stg_google_ads__ad_group_report | False |
| 12 | 11 | google_ads_ad_group_stats_data | False |
| 16 | 15 | google_ads_ad_group_stats_data | False |
| 18 | 17 | google_ads_ad_group_stats_data | False |
| 30 | 29 | stg_google_ads__ad_group_report | False |
| 38 | 37 | stg_google_ads__ad_group_report | False |
| 82 | 81 | stg_google_ads__ad_group_report | False |
| 86 | 85 | stg_google_ads__ad_group_report | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：5；核实代价档：需要查业务说明。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='google_ads_ad_group_stats_data') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["raw", "google_ads_ad_group_stats_data", "customer_id", "VARCHAR"], ["raw", "google_ads_ad_group_stats_data", "date", "VARCHAR"], ["raw", "google_ads_ad_group_stats_data", "active_view_impressions", "VARCHAR"], ["raw", "google_ads_ad_group_stats_data", "active_view_measurability", "VARCHAR"], ["raw", "google_ads_ad_group_stats_data", "active_view_measurable_cost_micros", "VARCHAR"], ["raw", "google_ads_ad_group_stats_data", "active_view_measurable_impressions", "VARCHAR"], ["raw", "google_ads_ad_group_stats_data", "active_view_viewability", "VARCHAR"], ["raw", "google_ads_ad_group_stats_data", "ad_network_type", "VARCHAR"], ["raw", "google_ads_ad_group_stats_data", "base_ad_group", "VARCHAR"], ["raw", "google_ads_ad_group_stats_data", "campaign_base_campaign", "VARCHAR"], ["raw", "google_ads_ad_group_stats_data", "campaign_id", "VARCHAR"], ["raw", "google_ads_ad_group_stats_data", "clicks", "BIGINT"], ["raw", "google_ads_ad_group_stats_data", "conversions", "DOUBLE"], ["raw", "google_ads_ad_group_stats_data", "conversions_value", "VARCHAR"], ["raw", "google_ads_ad_group_stats_data", "cost_micros", "BIGINT"], ["raw", "google_ads_ad_group_stats_data", "device", "VARCHAR"], ["raw", "google_ads_ad_group_stats_data", "id", "VARCHAR"], ["raw", "google_ads_ad_group_stats_data", "impressions", "BIGINT"], ["raw", "google_ads_ad_group_stats_data", "interaction_event_types", "VARCHAR"], ["raw", "google_ads_ad_group_stats_data", "interactions", "BIGINT"], ["raw", "google_ads_ad_group_stats_data", "view_through_conversions", "VARCHAR"]]`

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT count(*) n,count(*) FILTER(WHERE "base_ad_group" IS NULL) AS c0_null,count(*) FILTER(WHERE "base_ad_group" IS NOT NULL AND TRY_CAST("base_ad_group" AS DOUBLE) IS NULL) AS c1_not_numeric FROM raw.google_ads_ad_group_stats_data
```

结果：`[[715, 0, 715]]`

### 核实 3

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT count(*) n, count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.google_ads_ad_group_history_data h WHERE h.id=s.id)) id_matches_history, count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.google_ads_ad_group_history_data h WHERE h.id=s.base_ad_group)) base_matches_history,count(DISTINCT id) ids,count(DISTINCT base_ad_group) bases FROM raw.google_ads_ad_group_stats_data s
```

结果：`[[715, 15, 0, 701, 1]]`

### 核实 4

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='raw' AND table_name='google_ads_ad_group_history_data' ORDER BY ordinal_position
```

结果：`[["google_ads_ad_group_history_data", "id", "VARCHAR"], ["google_ads_ad_group_history_data", "updated_at", "VARCHAR"], ["google_ads_ad_group_history_data", "type", "VARCHAR"], ["google_ads_ad_group_history_data", "campaign_id", "VARCHAR"], ["google_ads_ad_group_history_data", "campaign_name", "VARCHAR"], ["google_ads_ad_group_history_data", "name", "VARCHAR"], ["google_ads_ad_group_history_data", "status", "VARCHAR"]]`

### 核实 5

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT count(*) n,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.google_ads_ad_group_history_data h WHERE h.id=regexp_extract(s.base_ad_group,'[^/]+$',0))) base_suffix_matches, count(*) FILTER(WHERE EXISTS(SELECT 1 FROM raw.google_ads_ad_group_history_data h WHERE h.id=s.id)) id_matches FROM raw.google_ads_ad_group_stats_data s
```

结果：`[[715, 715, 15]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=24 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025本表实际使用的raw.call_data也三侧一致（2500行、同内容哈希），不把其他Snowflake兼容表的类型改动归给本表。

## 固定时间与重跑

私有目录：`data/020_work/impl-006_stg_google_ads__ad_group_report/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：1430行 / 14300格；重跑基线：1430行 / 14300格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:1430行/14300格 / L1:1430行/14300格 / L2:1430行/14300格 / L3:1430行/14300格 | 均未整表匹配 |
| ad_group_id | L0:705行/2099格 / L1:705行/2099格 / L2:705行/2099格 / L3:705行/2099格 | 均未整表匹配 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {} |
| ad_group_id | {"conversions": 699, "conversions_value": 700, "view_through_conversions": 700} |

本表全部重跑证据文件：`records/020_reruns_impl-006_stg_google_ads__ad_group_report.json`。续做重跑私有副本在`data/020_resume_work/`。

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

全串连接base_ad_group为0匹配，若忽略资源路径格式会误读为U；去前缀后715/715匹配。最终按未规定的ID表示/映射标A，不从gold推定raw.id必然更正确。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-006_stg_google_ads__ad_group_report.md`。
- 重跑：`records/020_reruns_impl-006_stg_google_ads__ad_group_report.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
