# impl-006 / stg_tiktok_ads__campaign_report（全量）

## 结论

主要原因：**A**；把握：高。不存在advertiser_id时，NULL与unknown默认值选择改变了评测键。

参与因素：无。标记：无。

## 差异与归因依据

schema无advertiser_id，契约未给默认值；单改unknown使1800→900行，为主因A。spend、conversions和计算指标确有占位遗漏，但各自在原始键差异下单修规模完全不变，不列参与因素。 spend另有event19同名映射覆盖的I证据；独立恢复仍为1800行/48600格，不列参与因素。

层：staging；比较库schema：staging；评测键：campaign_id, date_day, advertiser_id。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml:1204–1262`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_tiktok_ads__campaign_report.sql:1–36`；SHA-256 `d1f0680a0f006fbb3531b177e7126ab558fd12bd9854b875ebc5bed858fcad7e`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/staging/stg_tiktok_ads__campaign_report.sql:1–68`；SHA-256 `88551b513c8fea7fb771fda85536172e679c80ab2bbcafe31097208405d2a092`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- date_day（agent SQL 第8行起）：
```sql
CAST(TRY_CAST(STAT_TIME_HOUR AS DATE) AS DATE) AS date_day
```
→
```sql
CAST(STAT_TIME_HOUR AS DATE) AS date_day
```

- advertiser_id（agent SQL 第9行起）：
```sql
CAST(NULL::VARCHAR AS VARCHAR) AS advertiser_id
```
→
```sql
CAST('unknown' AS TEXT) AS advertiser_id
```

- spend（agent SQL 第12行起）：
```sql
CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS spend
```
→
```sql
CAST(SPEND AS DECIMAL(18, 2)) AS spend
```

- conversions（agent SQL 第26行起）：
```sql
CAST(NULL::INTEGER AS INTEGER) AS conversions
```
→
```sql
CASE WHEN CONVERSION IS NULL OR TRIM(CAST(CONVERSION AS TEXT)) IN ('', 'true', 'false') OR CONVERSION LIKE 'mock_%' THEN 0 ELSE CAST(CONVERSION AS INT) END AS conversions
```

- calculated_cost_per_click（agent SQL 第30行起）：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS calculated_cost_per_click
```
→
```sql
CASE WHEN clicks > 0 THEN ROUND(spend / clicks, 2) ELSE 0 END AS calculated_cost_per_click
```

- cost_per_thousand_impressions（agent SQL 第31行起）：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_thousand_impressions
```
→
```sql
CASE WHEN impressions > 0 THEN ROUND((spend / impressions) * 1000, 2) ELSE 0 END AS cost_per_thousand_impressions
```

- cost_per_thousand_reached（agent SQL 第32行起）：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_thousand_reached
```
→
```sql
CASE WHEN CAST(REACH AS INT) > 0 THEN ROUND((spend / CAST(REACH AS DECIMAL(18, 3))) * 1000, 2) ELSE 0 END AS cost_per_thousand_reached
```

- spend_restore_overwritten_mapping（agent SQL 第12行起）：
```sql
CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS spend
```
→
```sql
CAST(ROUND(TRY_CAST("SPEND" AS DOUBLE), 2) AS DECIMAL(18,2)) AS spend
```

## agent可见证据与不确定性

不确定性四档：**只有通用策略说明**。

event 97（args.final_thought）：对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

完整事件扫描数：99；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | stg_tiktok_ads__campaign_report | False |
| 16 | 15 | tiktok_campaign_report_hourly_data | False |
| 18 | 17 | tiktok_campaign_report_hourly_data | False |
| 30 | 29 | stg_tiktok_ads__campaign_report | False |
| 38 | 37 | stg_tiktok_ads__campaign_report | False |
| 82 | 81 | stg_tiktok_ads__campaign_report | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：2；核实代价档：多条查询。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='tiktok_campaign_report_hourly_data') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["raw", "tiktok_campaign_report_hourly_data", "CAMPAIGN_ID", "VARCHAR"], ["raw", "tiktok_campaign_report_hourly_data", "STAT_TIME_HOUR", "VARCHAR"], ["raw", "tiktok_campaign_report_hourly_data", "COST_PER_CONVERSION", "VARCHAR"], ["raw", "tiktok_campaign_report_hourly_data", "CPC", "VARCHAR"], ["raw", "tiktok_campaign_report_hourly_data", "VIDEO_PLAY_ACTIONS", "BIGINT"], ["raw", "tiktok_campaign_report_hourly_data", "CONVERSION_RATE", "BIGINT"], ["raw", "tiktok_campaign_report_hourly_data", "VIDEO_VIEWS_P_75", "BIGINT"], ["raw", "tiktok_campaign_report_hourly_data", "RESULT", "VARCHAR"], ["raw", "tiktok_campaign_report_hourly_data", "VIDEO_VIEWS_P_50", "BIGINT"], ["raw", "tiktok_campaign_report_hourly_data", "IMPRESSIONS", "BIGINT"], ["raw", "tiktok_campaign_report_hourly_data", "COMMENTS", "VARCHAR"], ["raw", "tiktok_campaign_report_hourly_data", "REAL_TIME_COST_PER_RESULT", "VARCHAR"], ["raw", "tiktok_campaign_report_hourly_data", "CONVERSION", "VARCHAR"], ["raw", "tiktok_campaign_report_hourly_data", "REAL_TIME_RESULT", "VARCHAR"], ["raw", "tiktok_campaign_report_hourly_data", "VIDEO_VIEWS_P_100", "BIGINT"], ["raw", "tiktok_campaign_report_hourly_data", "SHARES", "VARCHAR"], ["raw", "tiktok_campaign_report_hourly_data", "REAL_TIME_CONVERSION_RATE", "VARCHAR"], ["raw", "tiktok_campaign_report_hourly_data", "COST_PER_SECONDARY_GOAL_RESULT", "VARCHAR"], ["raw", "tiktok_campaign_report_hourly_data", "SECONDARY_GOAL_RESULT_RATE", "BIGINT"], ["raw", "tiktok_campaign_report_hourly_data", "CLICKS", "BIGINT"], ["raw", "tiktok_campaign_report_hourly_data", "COST_PER_1000_REACHED", "DOUBLE"], ["raw", "tiktok_campaign_report_hourly_data", "VIDEO_VIEWS_P_25", "BIGINT"], ["raw", "tiktok_campaign_report_hourly_data", "REACH", "BIGINT"], ["raw", "tiktok_campaign_report_hourly_data", "REAL_TIME_COST_PER_CONVERSION", "VARCHAR"], ["raw", "tiktok_campaign_report_hourly_data", "PROFILE_VISITS_RATE", "BIGINT"], ["raw", "tiktok_campaign_report_hourly_data", "AVERAGE_VIDEO_PLAY", "VARCHAR"], ["raw", "tiktok_campaign_report_hourly_data", "PROFILE_VISITS", "BIGINT"], ["raw", "tiktok_campaign_report_hourly_data", "CPM", "VARCHAR"], ["raw", "tiktok_campaign_report_hourly_data", "CTR", "VARCHAR"], ["raw", "tiktok_campaign_report_hourly_data", "VIDEO_WATCHED_2_S", "BIGINT"], ["raw", "tiktok_campaign_report_hourly_data", "FOLLOWS", "VARCHAR"], ["raw", "tiktok_campaign_report_hourly_data", "RESULT_RATE", "BIGINT"], ["raw", "tiktok_campaign_report_hourly_data", "VIDEO_WATCHED_6_S", "BIGINT"], ["raw", "tiktok_campaign_report_hourly_data", "SECONDARY_GOAL_RESULT", "VARCHAR"], ["raw", "tiktok_campaign_report_hourly_data", "COST_PER_RESULT", "VARCHAR"], ["raw", "tiktok_campaign_report_hourly_data", "AVERAGE_VIDEO_PLAY_PER_USER", "VARCHAR"], ["raw", "tiktok_campaign_report_hourly_data", "REAL_TIME_RESULT_RATE", "VARCHAR"], ["raw", "tiktok_campaign_report_hourly_data", "SPEND", "DOUBLE"], ["raw", "tiktok_campaign_report_hourly_data", "LIKES", "VARCHAR"], ["raw", "tiktok_campaign_report_hourly_data", "REAL_TIME_CONVERSION", "VARCHAR"], ["raw", "tiktok_campaign_report_hourly_data", "TOTAL_PURCHASE_VALUE", "BIGINT"], ["raw", "tiktok_campaign_report_hourly_data", "TOTAL_SALES_LEAD_VALUE", "BIGINT"]]`

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT count(*) n,count(*) FILTER(WHERE "STAT_TIME_HOUR" IS NULL) AS c0_null,count(*) FILTER(WHERE "STAT_TIME_HOUR" IS NOT NULL AND TRY_CAST("STAT_TIME_HOUR" AS DOUBLE) IS NULL) AS c1_not_numeric FROM raw.tiktok_campaign_report_hourly_data
```

结果：`[[900, 0, 900]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=30 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025本表实际使用的raw.call_data也三侧一致（2500行、同内容哈希），不把其他Snowflake兼容表的类型改动归给本表。

## 固定时间与重跑

私有目录：`data/020_work/impl-006_stg_tiktok_ads__campaign_report/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：1800行 / 48600格；重跑基线：1800行 / 48600格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:1800行/48600格 / L1:1800行/48600格 / L2:1800行/48600格 / L3:1800行/48600格 | 均未整表匹配 |
| date_day | L0:1800行/48600格 / L1:1800行/48600格 / L2:1800行/48600格 / L3:1800行/48600格 | 均未整表匹配 |
| advertiser_id | L0:900行/9009格 / L1:900行/9009格 / L2:900行/9009格 / L3:900行/9009格 | 均未整表匹配 |
| spend | L0:1800行/48600格 / L1:1800行/48600格 / L2:1800行/48600格 / L3:1800行/48600格 | 均未整表匹配 |
| conversions | L0:1800行/48600格 / L1:1800行/48600格 / L2:1800行/48600格 / L3:1800行/48600格 | 均未整表匹配 |
| calculated_cost_per_click | L0:1800行/48600格 / L1:1800行/48600格 / L2:1800行/48600格 / L3:1800行/48600格 | 均未整表匹配 |
| cost_per_thousand_impressions | L0:1800行/48600格 / L1:1800行/48600格 / L2:1800行/48600格 / L3:1800行/48600格 | 均未整表匹配 |
| cost_per_thousand_reached | L0:1800行/48600格 / L1:1800行/48600格 / L2:1800行/48600格 / L3:1800行/48600格 | 均未整表匹配 |
| spend_restore_overwritten_mapping | L0:1800行/48600格 / L1:1800行/48600格 / L2:1800行/48600格 / L3:1800行/48600格 | 均未整表匹配 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {} |
| date_day | {} |
| advertiser_id | {"calculated_cost_per_click": 900, "click_through_rate": 900, "comments": 686, "conversions": 900, "cost_per_conversion": 900, "cost_per_thousand_impressions": 900, "cost_per_thousand_reached": 900, "follows": 663, "likes": 681, "shares": 679, "spend": 900} |
| spend | {} |
| conversions | {} |
| calculated_cost_per_click | {} |
| cost_per_thousand_impressions | {} |
| cost_per_thousand_reached | {} |
| spend_restore_overwritten_mapping | {} |

本表全部重跑证据文件：`records/020_reruns_impl-006_stg_tiktok_ads__campaign_report.json`；`records/020_resume_reruns_impl-006_stg_tiktok_ads__campaign_report.json`。续做重跑私有副本在`data/020_resume_work/`。

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

 映射覆盖有代码自身的明确意图证据，直接适用v2的I定义，不修改规则；复核重跑恢复原先候选列，未套用gold额外清洗。旧gold表达式试验仅作诊断，避免重复计为两个错误点。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-006_stg_tiktok_ads__campaign_report.md`。
- 重跑：`records/020_reruns_impl-006_stg_tiktok_ads__campaign_report.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
