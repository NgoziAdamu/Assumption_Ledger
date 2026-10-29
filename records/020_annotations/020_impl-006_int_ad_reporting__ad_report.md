> **暂停检查点／待复核草稿**：用户于 2026-10-29 要求暂停。此文件尚未通过任务020最终复核，请勿作为正式定稿使用。

# impl-006 / int_ad_reporting__ad_report（全量）

## 结论

主要原因：**D**；把握：高。仅取 Facebook 分支且将可映射指标填 NULL，遗漏 Apple 的 1500 行。

参与因素：D：clicks（减0行/1000格）；D：cost（减0行/1000格）；D：interactions（减0行/1000格）；D：conversions（减0行/1000格）；D：conversions_value（减0行/1000格）；D：view_through_conversions（减0行/1000格）；D：cost_per_conversion（减0行/1000格）；D：return_on_ad_spend（减0行/1000格）。标记：已披露。

## 差异与归因依据

event23 写明 primary source only / fanin unsupported；event27 fallback 用 source_models[0]。存在 Apple 来源但未作数据判断而裁成单源，按 D；缺失分支单修减少1500行，逐列NULL单修各减少1000格。

层：intermediate；比较库schema：intermediate；评测键：ad_id。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml:1517–1623`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__ad_report.sql:1–35`；SHA-256 `80e02d328d08fa1a418c9c33d45c61134ba5ddc5bcc77d1363cdc76fcc4377fe`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__ad_report.sql:1–131`；SHA-256 `f89bd269895ddccabd00a47da7eb8e0b3ad971a4d9039ae2e4828f0f1376a723`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- missing_apple_branch：
```sql
FROM staging.stg_facebook_ads__ad_report
```
→
```sql
FROM staging.stg_facebook_ads__ad_report
UNION ALL


-- Apple Search Ads Ad Report
SELECT 
    -- Platform identifier
    platform,
    
    -- Primary Keys
    ad_id,
    date_day,
    
    -- Hierarchy References
    NULL AS account_id,
    campaign_id,
    ad_group_id,
    
    -- Segmentation attributes
    NULL AS ad_network_type,
    NULL AS device,
    
    -- Performance Metrics
    CAST(impressions AS INTEGER) AS impressions,
    CAST(taps AS INTEGER) AS clicks,
    0 AS interactions,
    
    -- Cost Metrics
    spend AS cost,
    
    -- Conversion Metrics
    conversions,
    0.0 AS conversions_value,
    0 AS view_through_conversions,
    
    -- Viewability Metrics
    NULL AS active_view_impressions,
    NULL AS active_view_measurable_impressions,
    NULL AS active_view_measurable_cost,
    NULL AS active_view_measurability,
    NULL AS active_view_viewability,
    
    -- Amazon Ads specific metrics
    NULL AS attributed_sales_14_d,
    NULL AS attributed_sales_30_d,
    NULL AS attributed_conversions_14_d,
    NULL AS attributed_conversions_30_d,
    
    -- Apple Search Ads specific metrics
    CAST(new_downloads AS INTEGER) AS installs,
    CAST(taps AS INTEGER) AS taps,
    
    -- Calculated Metrics
    tap_through_rate AS click_through_rate,
    cost_per_tap AS cost_per_click,
    0.0 AS cost_per_thousand_impressions,
    cost_per_conversion,
    0.0 AS return_on_ad_spend,
    
    -- Additional metadata
    NULL AS interaction_event_types,
    
    -- Data Quality
    _dbt_loaded_at

FROM staging.stg_apple_search_ads__ad_report
```

- clicks：
```sql
NULL::INTEGER AS "clicks"
```
→
```sql
inline_link_clicks AS clicks
```

- cost：
```sql
NULL::DECIMAL(18,2) AS "cost"
```
→
```sql
spend AS cost
```

- interactions：
```sql
NULL::INTEGER AS "interactions"
```
→
```sql
0 AS interactions
```

- conversions：
```sql
NULL::INTEGER AS "conversions"
```
→
```sql
0 AS conversions
```

- conversions_value：
```sql
NULL::DECIMAL(2,1) AS "conversions_value"
```
→
```sql
0.0 AS conversions_value
```

- view_through_conversions：
```sql
NULL::INTEGER AS "view_through_conversions"
```
→
```sql
0 AS view_through_conversions
```

- cost_per_conversion：
```sql
NULL::DOUBLE AS "cost_per_conversion"
```
→
```sql
0.0 AS cost_per_conversion
```

- return_on_ad_spend：
```sql
NULL::DECIMAL(2,1) AS "return_on_ad_spend"
```
→
```sql
0.0 AS return_on_ad_spend
```

## agent可见证据与不确定性

不确定性四档：**只有通用策略说明**。

event 97（args.final_thought）：对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

完整事件扫描数：99；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | int_ad_reporting__ad_report,stg_facebook_ads__ad_report | False |
| 26 | 25 | int_ad_reporting__ad_report | False |
| 38 | 37 | int_ad_reporting__ad_report,stg_facebook_ads__ad_report | False |
| 82 | 81 | stg_facebook_ads__ad_report | False |
| 84 | 83 | int_ad_reporting__ad_report | False |
| 86 | 85 | stg_facebook_ads__ad_report | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：1；核实代价档：一条查询。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='staging' AND table_name='stg_facebook_ads__ad_report') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["staging", "stg_facebook_ads__ad_report", "platform", "VARCHAR"], ["staging", "stg_facebook_ads__ad_report", "ad_id", "VARCHAR"], ["staging", "stg_facebook_ads__ad_report", "date_day", "DATE"], ["staging", "stg_facebook_ads__ad_report", "account_id", "VARCHAR"], ["staging", "stg_facebook_ads__ad_report", "impressions", "INTEGER"], ["staging", "stg_facebook_ads__ad_report", "inline_link_clicks", "INTEGER"], ["staging", "stg_facebook_ads__ad_report", "spend", "DECIMAL(18,2)"], ["staging", "stg_facebook_ads__ad_report", "click_through_rate", "INTEGER"], ["staging", "stg_facebook_ads__ad_report", "cost_per_click", "INTEGER"], ["staging", "stg_facebook_ads__ad_report", "cost_per_thousand_impressions", "DOUBLE"], ["staging", "stg_facebook_ads__ad_report", "_dbt_loaded_at", "TIMESTAMP WITH TIME ZONE"]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=1 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025的agent修改raw不适用“不可评估”，本次使用留存raw。

## 固定时间与重跑

私有目录：`data/020_work/impl-006_int_ad_reporting__ad_report/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 0}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：2500行 / 56000格；重跑基线：2500行 / 56000格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:2500行/56000格 / L1:2500行/56000格 / L2:2500行/56000格 / L3:2500行/56000格 | 均未整表匹配 |
| missing_apple_branch | L0:1000行/8000格 / L1:1000行/8000格 / L2:1000行/8000格 / L3:1000行/8000格 | 均未整表匹配 |
| clicks | L0:2500行/55000格 / L1:2500行/55000格 / L2:2500行/55000格 / L3:2500行/55000格 | 均未整表匹配 |
| cost | L0:2500行/55000格 / L1:2500行/55000格 / L2:2500行/55000格 / L3:2500行/55000格 | 均未整表匹配 |
| interactions | L0:2500行/55000格 / L1:2500行/55000格 / L2:2500行/55000格 / L3:2500行/55000格 | 均未整表匹配 |
| conversions | L0:2500行/55000格 / L1:2500行/55000格 / L2:2500行/55000格 / L3:2500行/55000格 | 均未整表匹配 |
| conversions_value | L0:2500行/55000格 / L1:2500行/55000格 / L2:2500行/55000格 / L3:2500行/55000格 | 均未整表匹配 |
| view_through_conversions | L0:2500行/55000格 / L1:2500行/55000格 / L2:2500行/55000格 / L3:2500行/55000格 | 均未整表匹配 |
| cost_per_conversion | L0:2500行/55000格 / L1:2500行/55000格 / L2:2500行/55000格 / L3:2500行/55000格 | 均未整表匹配 |
| return_on_ad_spend | L0:2500行/55000格 / L1:2500行/55000格 / L2:2500行/55000格 / L3:2500行/55000格 | 均未整表匹配 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {"clicks": 1000, "conversions": 1000, "conversions_value": 1000, "cost": 1000, "cost_per_conversion": 1000, "interactions": 1000, "return_on_ad_spend": 1000, "view_through_conversions": 1000} |
| missing_apple_branch | {"clicks": 1000, "conversions": 1000, "conversions_value": 1000, "cost": 1000, "cost_per_conversion": 1000, "interactions": 1000, "return_on_ad_spend": 1000, "view_through_conversions": 1000} |
| clicks | {"conversions": 1000, "conversions_value": 1000, "cost": 1000, "cost_per_conversion": 1000, "interactions": 1000, "return_on_ad_spend": 1000, "view_through_conversions": 1000} |
| cost | {"clicks": 1000, "conversions": 1000, "conversions_value": 1000, "cost_per_conversion": 1000, "interactions": 1000, "return_on_ad_spend": 1000, "view_through_conversions": 1000} |
| interactions | {"clicks": 1000, "conversions": 1000, "conversions_value": 1000, "cost": 1000, "cost_per_conversion": 1000, "return_on_ad_spend": 1000, "view_through_conversions": 1000} |
| conversions | {"clicks": 1000, "conversions_value": 1000, "cost": 1000, "cost_per_conversion": 1000, "interactions": 1000, "return_on_ad_spend": 1000, "view_through_conversions": 1000} |
| conversions_value | {"clicks": 1000, "conversions": 1000, "cost": 1000, "cost_per_conversion": 1000, "interactions": 1000, "return_on_ad_spend": 1000, "view_through_conversions": 1000} |
| view_through_conversions | {"clicks": 1000, "conversions": 1000, "conversions_value": 1000, "cost": 1000, "cost_per_conversion": 1000, "interactions": 1000, "return_on_ad_spend": 1000} |
| cost_per_conversion | {"clicks": 1000, "conversions": 1000, "conversions_value": 1000, "cost": 1000, "interactions": 1000, "return_on_ad_spend": 1000, "view_through_conversions": 1000} |
| return_on_ad_spend | {"clicks": 1000, "conversions": 1000, "conversions_value": 1000, "cost": 1000, "cost_per_conversion": 1000, "interactions": 1000, "view_through_conversions": 1000} |

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

无。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-006_int_ad_reporting__ad_report.md`。
- 重跑：`records/020_reruns_impl-006_int_ad_reporting__ad_report.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
