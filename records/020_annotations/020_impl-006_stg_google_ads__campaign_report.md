# impl-006 / stg_google_ads__campaign_report（全量）

## 结论

主要原因：**I**；把握：高。campaign_id 的正确 id 映射被后写的字典条目覆盖，最终生成 NULL。

参与因素：无。标记：无。

## 差异与归因依据

event19 的 special 字典先有 `'campaign_id':['campaign_id','id']` 和 `'spend':['spend','local_spend_amount']`，后被同名键 `'campaign_id':['campaign_id','CAMPAIGN_ID']`、`'spend':['local_spend_amount']` 覆盖。代码自身给出正确映射意图，符合手册I的明确例子。 恢复生成器原先的id映射，只改campaign_id投影，行数规模减半；其他遗漏仍被键差异遮蔽。

层：staging；比较库schema：staging；评测键：account_id, date_day, campaign_id, ad_network_type, device。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml:770–796`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_google_ads__campaign_report.sql:1–20`；SHA-256 `f85c461f055ed1ac92f8a76dfd066d252f8fb7d27ca380fb0a4dbcfe11c25f12`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/staging/stg_google_ads__campaign_report.sql:1–53`；SHA-256 `8942a52307c27ba4c5fe4353bc85174cd54fe30a8dc64aa74ab117742cc1aa82`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- campaign_id（agent SQL 第9行起）：
```sql
CAST(NULL::VARCHAR(20) AS VARCHAR(20)) AS campaign_id
```
→
```sql
CAST(id AS TEXT) AS campaign_id
```

- campaign_id_restore_overwritten_mapping（agent SQL 第9行起）：
```sql
CAST(NULL::VARCHAR(20) AS VARCHAR(20)) AS campaign_id
```
→
```sql
CAST(CAST("id" AS VARCHAR) AS VARCHAR(20)) AS campaign_id
```

- spend_masked_diagnostic（agent SQL 第13行起）：
```sql
CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS spend
```
→
```sql
ROUND(cost_micros / 1000000.0, 2) AS spend
```

## agent可见证据与不确定性

不确定性四档：**看到了但没提**。

event18输出原始id列清单；event19先写正确映射又覆盖。event97只披露缺失源字段填NULL，未说明本表已有id却因覆盖失效，不能把该缺省策略当作对此处代码错误的说明。

完整事件扫描数：99；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | stg_google_ads__campaign_report | False |
| 12 | 11 | google_ads_campaign_stats_data | False |
| 16 | 15 | google_ads_campaign_stats_data | False |
| 18 | 17 | google_ads_campaign_stats_data | False |
| 30 | 29 | stg_google_ads__campaign_report | False |
| 34 | 33 | stg_google_ads__campaign_report | False |
| 38 | 37 | stg_google_ads__campaign_report | False |
| 82 | 81 | stg_google_ads__campaign_report | False |
| 86 | 85 | stg_google_ads__campaign_report | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：2；核实代价档：多条查询。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='google_ads_campaign_stats_data') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["raw", "google_ads_campaign_stats_data", "customer_id", "VARCHAR"], ["raw", "google_ads_campaign_stats_data", "date", "VARCHAR"], ["raw", "google_ads_campaign_stats_data", "active_view_impressions", "BIGINT"], ["raw", "google_ads_campaign_stats_data", "active_view_measurability", "DOUBLE"], ["raw", "google_ads_campaign_stats_data", "active_view_measurable_cost_micros", "BIGINT"], ["raw", "google_ads_campaign_stats_data", "active_view_measurable_impressions", "BIGINT"], ["raw", "google_ads_campaign_stats_data", "active_view_viewability", "DOUBLE"], ["raw", "google_ads_campaign_stats_data", "ad_network_type", "VARCHAR"], ["raw", "google_ads_campaign_stats_data", "base_campaign", "VARCHAR"], ["raw", "google_ads_campaign_stats_data", "clicks", "BIGINT"], ["raw", "google_ads_campaign_stats_data", "conversions", "BIGINT"], ["raw", "google_ads_campaign_stats_data", "conversions_value", "DOUBLE"], ["raw", "google_ads_campaign_stats_data", "cost_micros", "BIGINT"], ["raw", "google_ads_campaign_stats_data", "device", "VARCHAR"], ["raw", "google_ads_campaign_stats_data", "id", "VARCHAR"], ["raw", "google_ads_campaign_stats_data", "impressions", "BIGINT"], ["raw", "google_ads_campaign_stats_data", "interaction_event_types", "VARCHAR"], ["raw", "google_ads_campaign_stats_data", "interactions", "BIGINT"], ["raw", "google_ads_campaign_stats_data", "view_through_conversions", "BIGINT"]]`

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT count(*) n FROM raw.google_ads_campaign_stats_data
```

结果：`[[26031]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=25 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025本表实际使用的raw.call_data也三侧一致（2500行、同内容哈希），不把其他Snowflake兼容表的类型改动归给本表。

## 固定时间与重跑

私有目录：`data/020_work/impl-006_stg_google_ads__campaign_report/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：52062行 / 572682格；重跑基线：52062行 / 572682格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:52062行/572682格 / L1:52062行/572682格 / L2:52062行/572682格 / L3:52062行/572682格 | 均未整表匹配 |
| campaign_id | L0:26031行/26031格 / L1:26031行/26031格 / L2:26031行/26031格 / L3:26031行/26031格 | 均未整表匹配 |
| campaign_id_restore_overwritten_mapping | L0:26031行/26031格 / L1:26031行/26031格 / L2:26031行/26031格 / L3:26031行/26031格 | 均未整表匹配 |
| spend_masked_diagnostic | L0:52062行/572682格 / L1:52062行/572682格 / L2:52062行/572682格 / L3:52062行/572682格 | 均未整表匹配 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {} |
| campaign_id | {"spend": 26031} |
| campaign_id_restore_overwritten_mapping | {"spend": 26031} |
| spend_masked_diagnostic | {} |

本表全部重跑证据文件：`records/020_reruns_impl-006_stg_google_ads__campaign_report.json`；`records/020_resume_reruns_impl-006_stg_google_ads__campaign_report.json`。续做重跑私有副本在`data/020_resume_work/`。

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

 映射覆盖有代码自身的明确意图证据，直接适用v2的I定义，不修改规则；复核重跑恢复原先候选列，未套用gold额外清洗。旧gold表达式试验仅作诊断，避免重复计为两个错误点。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-006_stg_google_ads__campaign_report.md`。
- 重跑：`records/020_reruns_impl-006_stg_google_ads__campaign_report.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
