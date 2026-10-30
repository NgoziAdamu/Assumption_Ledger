# impl-006 / stg_snapchat_ads__campaign_report（全量）

## 结论

主要原因：**多因并列（A、D、I）**；把握：高。spend映射覆盖（I）、率指标占位（D）及无源/异常字段默认值（A）并列。

参与因素：A：shares（减0行/673格）；A：video_views（减0行/685格）。标记：已披露（D占位部分）。

## 差异与归因依据

event19 的 special 字典先有 `'campaign_id':['campaign_id','id']` 和 `'spend':['spend','local_spend_amount']`，后被同名键 `'campaign_id':['campaign_id','CAMPAIGN_ID']`、`'spend':['local_spend_amount']` 覆盖。代码自身给出正确映射意图，符合手册I的明确例子。 ad_account_id缺失，异常文本清理为0或NULL未规定，A；可计算的率指标直接NULL为D。最大单项改善均900格。

层：staging；比较库schema：staging；评测键：campaign_id。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml:1149–1203`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_snapchat_ads__campaign_report.sql:1–34`；SHA-256 `ad7bbb7698080f86eedaf6b92bca5535574ffde5d8116d48c85a93d977323ba0`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/staging/stg_snapchat_ads__campaign_report.sql:1–70`；SHA-256 `9529c20b0c1df836eb14b03f95842e42d7c8458ab1d4caf6250105758ffb1624`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- ad_account_id（agent SQL 第9行起）：
```sql
CAST(NULL::VARCHAR AS VARCHAR) AS ad_account_id
```
→
```sql
CAST('unknown' AS TEXT) AS ad_account_id
```

- conversion_purchases（agent SQL 第23行起）：
```sql
TRY_CAST("conversion_purchases" AS INTEGER) AS conversion_purchases
```
→
```sql
CASE WHEN conversion_purchases IS NULL OR TRIM(CAST(conversion_purchases AS TEXT)) IN ('', 'true', 'false') OR TRIM(CAST(conversion_purchases AS TEXT)) LIKE 'mock_%' THEN 0 ELSE CAST(conversion_purchases AS INT) END AS conversion_purchases
```

- cost_per_install（agent SQL 第30行起）：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_install
```
→
```sql
CASE WHEN (CASE WHEN total_installs IS NULL OR TRIM(CAST(total_installs AS TEXT)) IN ('', 'true', 'false') THEN 0 ELSE CAST(total_installs AS INT) END) > 0 THEN ROUND(spend / (CASE WHEN total_installs IS NULL OR TRIM(CAST(total_installs AS TEXT)) IN ('', 'true', 'false') THEN 0 ELSE CAST(total_installs AS INT) END), 2) ELSE 0 END AS cost_per_install
```

- cost_per_swipe（agent SQL 第27行起）：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_swipe
```
→
```sql
CASE WHEN swipes > 0 THEN ROUND(spend / swipes, 2) ELSE 0 END AS cost_per_swipe
```

- cost_per_thousand_impressions（agent SQL 第28行起）：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_thousand_impressions
```
→
```sql
CASE WHEN impressions > 0 THEN ROUND((spend / impressions) * 1000, 2) ELSE 0 END AS cost_per_thousand_impressions
```

- cost_per_video_view（agent SQL 第29行起）：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_video_view
```
→
```sql
CASE WHEN (CASE WHEN video_views = '' OR video_views = 'true' OR video_views = 'false' OR video_views IS NULL THEN 0 ELSE CAST(video_views AS INT) END) > 0 THEN ROUND(spend / (CASE WHEN video_views = '' OR video_views = 'true' OR video_views = 'false' OR video_views IS NULL THEN 0 ELSE CAST(video_views AS INT) END), 2) ELSE 0 END AS cost_per_video_view
```

- quartile_1（agent SQL 第15行起）：
```sql
TRY_CAST("quartile_1" AS INTEGER) AS quartile_1
```
→
```sql
CASE WHEN quartile_1 IS NULL OR TRIM(CAST(quartile_1 AS TEXT)) IN ('', 'true', 'false') OR TRIM(CAST(quartile_1 AS TEXT)) LIKE 'mock_%' THEN 0 ELSE CAST(quartile_1 AS INT) END AS quartile_1
```

- quartile_2（agent SQL 第16行起）：
```sql
TRY_CAST("quartile_2" AS INTEGER) AS quartile_2
```
→
```sql
CASE WHEN quartile_2 IS NULL OR TRIM(CAST(quartile_2 AS TEXT)) IN ('', 'true', 'false') OR TRIM(CAST(quartile_2 AS TEXT)) LIKE 'mock_%' THEN 0 ELSE CAST(quartile_2 AS INT) END AS quartile_2
```

- quartile_3（agent SQL 第17行起）：
```sql
TRY_CAST("quartile_3" AS INTEGER) AS quartile_3
```
→
```sql
CASE WHEN quartile_3 IS NULL OR TRIM(CAST(quartile_3 AS TEXT)) IN ('', 'true', 'false') OR TRIM(CAST(quartile_3 AS TEXT)) LIKE 'mock_%' THEN 0 ELSE CAST(quartile_3 AS INT) END AS quartile_3
```

- screen_time_millis（agent SQL 第14行起）：
```sql
TRY_CAST("screen_time_millis" AS BIGINT) AS screen_time_millis
```
→
```sql
CASE WHEN screen_time_millis IS NULL OR TRIM(CAST(screen_time_millis AS TEXT)) LIKE '%-%-%' OR TRIM(CAST(screen_time_millis AS TEXT)) LIKE 'mock_%' THEN 0 ELSE CAST(COALESCE(screen_time_millis, '0') AS BIGINT) END AS screen_time_millis
```

- shares（agent SQL 第21行起）：
```sql
TRY_CAST("shares" AS INTEGER) AS shares
```
→
```sql
CASE WHEN shares IS NULL OR TRIM(CAST(shares AS TEXT)) IN ('', 'true', 'false') OR TRIM(CAST(shares AS TEXT)) LIKE 'mock_%' THEN 0 ELSE CAST(shares AS INT) END AS shares
```

- spend（agent SQL 第12行起）：
```sql
CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS spend
```
→
```sql
CAST(spend AS DECIMAL(18, 2)) AS spend
```

- story_completes（agent SQL 第20行起）：
```sql
TRY_CAST("story_completes" AS INTEGER) AS story_completes
```
→
```sql
CASE WHEN story_completes IS NULL OR TRIM(CAST(story_completes AS TEXT)) IN ('', 'true', 'false') OR TRIM(CAST(story_completes AS TEXT)) LIKE 'mock_%' THEN 0 ELSE CAST(story_completes AS INT) END AS story_completes
```

- swipe_up_rate（agent SQL 第26行起）：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS swipe_up_rate
```
→
```sql
CASE WHEN impressions > 0 THEN ROUND((CAST(swipes AS DECIMAL(18, 3)) / CAST(impressions AS DECIMAL(18, 3))) * 100, 4) ELSE 0 END AS swipe_up_rate
```

- video_views（agent SQL 第13行起）：
```sql
CAST(TRY_CAST("video_views" AS BIGINT) AS INTEGER) AS video_views
```
→
```sql
CASE WHEN video_views IS NULL OR TRIM(CAST(video_views AS TEXT)) IN ('', 'true', 'false') OR TRIM(CAST(video_views AS TEXT)) LIKE 'mock_%' THEN 0 ELSE CAST(video_views AS INT) END AS video_views
```

- view_completion（agent SQL 第18行起）：
```sql
TRY_CAST("view_completion" AS INTEGER) AS view_completion
```
→
```sql
CASE WHEN view_completion IS NULL OR TRIM(CAST(view_completion AS TEXT)) IN ('', 'true', 'false') OR TRIM(CAST(view_completion AS TEXT)) LIKE 'mock_%' THEN 0 ELSE CAST(view_completion AS INT) END AS view_completion
```

- spend_restore_overwritten_mapping（agent SQL 第12行起）：
```sql
CAST(NULL::DECIMAL(18,2) AS DECIMAL(18,2)) AS spend
```
→
```sql
CAST(ROUND(TRY_CAST("spend" AS DOUBLE), 2) AS DECIMAL(18,2)) AS spend
```

## agent可见证据与不确定性

不确定性四档：**ad_account_id=只有通用策略说明；conversion_purchases=只有通用策略说明；cost_per_install=只有通用策略说明；cost_per_swipe=只有通用策略说明；cost_per_thousand_impressions=只有通用策略说明；cost_per_video_view=只有通用策略说明；quartile_1=只有通用策略说明；quartile_2=只有通用策略说明；quartile_3=只有通用策略说明；screen_time_millis=只有通用策略说明；story_completes=只有通用策略说明；swipe_up_rate=只有通用策略说明；view_completion=只有通用策略说明；spend_restore_overwritten_mapping=看到了但没提**。

event 97（args.final_thought）：对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。 event 97（args.final_thought）：脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。 各并列项单独分档：占位/缺省选择沿用适用的NULL通用披露；I覆盖错误只见event18列清单与event19代码，没有说明。

完整事件扫描数：99；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | stg_snapchat_ads__campaign_report | False |
| 16 | 15 | snapchat_campaign_hourly_report_data | False |
| 18 | 17 | snapchat_campaign_hourly_report_data | False |
| 30 | 29 | stg_snapchat_ads__campaign_report | False |
| 38 | 37 | stg_snapchat_ads__campaign_report | False |
| 82 | 81 | stg_snapchat_ads__campaign_report | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：2；核实代价档：多条查询。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='snapchat_campaign_hourly_report_data') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["raw", "snapchat_campaign_hourly_report_data", "campaign_id", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "date", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "android_installs", "BIGINT"], ["raw", "snapchat_campaign_hourly_report_data", "attachment_avg_view_time_millis", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "attachment_quartile_1", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "attachment_quartile_2", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "attachment_quartile_3", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "attachment_total_view_time_millis", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "attachment_view_completion", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "avg_screen_time_millis", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "avg_view_time_millis", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "conversion_add_billing", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "conversion_add_cart", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "conversion_app_opens", "BIGINT"], ["raw", "snapchat_campaign_hourly_report_data", "conversion_level_completes", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "conversion_page_views", "BIGINT"], ["raw", "snapchat_campaign_hourly_report_data", "conversion_purchases", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "conversion_purchases_value", "DOUBLE"], ["raw", "snapchat_campaign_hourly_report_data", "conversion_save", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "conversion_searches", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "conversion_sign_ups", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "conversion_start_checkout", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "conversion_view_content", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "impressions", "BIGINT"], ["raw", "snapchat_campaign_hourly_report_data", "ios_installs", "BIGINT"], ["raw", "snapchat_campaign_hourly_report_data", "quartile_1", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "quartile_2", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "quartile_3", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "saves", "BIGINT"], ["raw", "snapchat_campaign_hourly_report_data", "screen_time_millis", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "shares", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "spend", "DOUBLE"], ["raw", "snapchat_campaign_hourly_report_data", "story_completes", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "story_opens", "BIGINT"], ["raw", "snapchat_campaign_hourly_report_data", "swipe_up_percent", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "swipes", "BIGINT"], ["raw", "snapchat_campaign_hourly_report_data", "total_installs", "BIGINT"], ["raw", "snapchat_campaign_hourly_report_data", "video_views", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "view_completion", "VARCHAR"], ["raw", "snapchat_campaign_hourly_report_data", "view_time_millis", "VARCHAR"]]`

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT count(*) n,count(*) FILTER(WHERE "conversion_purchases" IS NULL) AS c0_null,count(*) FILTER(WHERE "conversion_purchases" IS NOT NULL AND TRY_CAST("conversion_purchases" AS DOUBLE) IS NULL) AS c1_not_numeric,count(*) FILTER(WHERE "impressions" IS NULL) AS c2_null,count(*) FILTER(WHERE "impressions" IS NOT NULL AND TRY_CAST("impressions" AS DOUBLE) IS NULL) AS c3_not_numeric,count(*) FILTER(WHERE "quartile_1" IS NULL) AS c4_null,count(*) FILTER(WHERE "quartile_1" IS NOT NULL AND TRY_CAST("quartile_1" AS DOUBLE) IS NULL) AS c5_not_numeric,count(*) FILTER(WHERE "quartile_2" IS NULL) AS c6_null,count(*) FILTER(WHERE "quartile_2" IS NOT NULL AND TRY_CAST("quartile_2" AS DOUBLE) IS NULL) AS c7_not_numeric,count(*) FILTER(WHERE "quartile_3" IS NULL) AS c8_null,count(*) FILTER(WHERE "quartile_3" IS NOT NULL AND TRY_CAST("quartile_3" AS DOUBLE) IS NULL) AS c9_not_numeric,count(*) FILTER(WHERE "screen_time_millis" IS NULL) AS c10_null,count(*) FILTER(WHERE "screen_time_millis" IS NOT NULL AND TRY_CAST("screen_time_millis" AS DOUBLE) IS NULL) AS c11_not_numeric,count(*) FILTER(WHERE "shares" IS NULL) AS c12_null,count(*) FILTER(WHERE "shares" IS NOT NULL AND TRY_CAST("shares" AS DOUBLE) IS NULL) AS c13_not_numeric,count(*) FILTER(WHERE "spend" IS NULL) AS c14_null,count(*) FILTER(WHERE "spend" IS NOT NULL AND TRY_CAST("spend" AS DOUBLE) IS NULL) AS c15_not_numeric,count(*) FILTER(WHERE "story_completes" IS NULL) AS c16_null,count(*) FILTER(WHERE "story_completes" IS NOT NULL AND TRY_CAST("story_completes" AS DOUBLE) IS NULL) AS c17_not_numeric,count(*) FILTER(WHERE "video_views" IS NULL) AS c18_null,count(*) FILTER(WHERE "video_views" IS NOT NULL AND TRY_CAST("video_views" AS DOUBLE) IS NULL) AS c19_not_numeric,count(*) FILTER(WHERE "view_completion" IS NULL) AS c20_null,count(*) FILTER(WHERE "view_completion" IS NOT NULL AND TRY_CAST("view_completion" AS DOUBLE) IS NULL) AS c21_not_numeric FROM raw.snapchat_campaign_hourly_report_data
```

结果：`[[900, 0, 900, 0, 0, 0, 900, 0, 900, 0, 900, 0, 900, 223, 450, 0, 0, 0, 900, 219, 466, 0, 900]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=29 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025本表实际使用的raw.call_data也三侧一致（2500行、同内容哈希），不把其他Snowflake兼容表的类型改动归给本表。

## 固定时间与重跑

私有目录：`data/020_work/impl-006_stg_snapchat_ads__campaign_report/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：900行 / 13958格；重跑基线：900行 / 13958格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:900行/13958格 / L1:900行/13958格 / L2:900行/13958格 / L3:900行/13958格 | 均未整表匹配 |
| ad_account_id | L0:900行/13058格 / L1:900行/13058格 / L2:900行/13058格 / L3:900行/13058格 | 均未整表匹配 |
| conversion_purchases | L0:900行/13058格 / L1:900行/13058格 / L2:900行/13058格 / L3:900行/13058格 | 均未整表匹配 |
| cost_per_install | L0:900行/13058格 / L1:900行/13058格 / L2:900行/13058格 / L3:900行/13058格 | 均未整表匹配 |
| cost_per_swipe | L0:900行/13058格 / L1:900行/13058格 / L2:900行/13058格 / L3:900行/13058格 | 均未整表匹配 |
| cost_per_thousand_impressions | L0:900行/13058格 / L1:900行/13058格 / L2:900行/13058格 / L3:900行/13058格 | 均未整表匹配 |
| cost_per_video_view | L0:900行/13058格 / L1:900行/13058格 / L2:900行/13058格 / L3:900行/13058格 | 均未整表匹配 |
| quartile_1 | L0:900行/13058格 / L1:900行/13058格 / L2:900行/13058格 / L3:900行/13058格 | 均未整表匹配 |
| quartile_2 | L0:900行/13058格 / L1:900行/13058格 / L2:900行/13058格 / L3:900行/13058格 | 均未整表匹配 |
| quartile_3 | L0:900行/13058格 / L1:900行/13058格 / L2:900行/13058格 / L3:900行/13058格 | 均未整表匹配 |
| screen_time_millis | L0:900行/13058格 / L1:900行/13058格 / L2:900行/13058格 / L3:900行/13058格 | 均未整表匹配 |
| shares | L0:900行/13285格 / L1:900行/13285格 / L2:900行/13285格 / L3:900行/13285格 | 均未整表匹配 |
| spend | L0:900行/13058格 / L1:900行/13058格 / L2:900行/13058格 / L3:900行/13058格 | 均未整表匹配 |
| story_completes | L0:900行/13058格 / L1:900行/13058格 / L2:900行/13058格 / L3:900行/13058格 | 均未整表匹配 |
| swipe_up_rate | L0:900行/13058格 / L1:900行/13058格 / L2:900行/13058格 / L3:900行/13058格 | 均未整表匹配 |
| video_views | L0:900行/13273格 / L1:900行/13273格 / L2:900行/13273格 / L3:900行/13273格 | 均未整表匹配 |
| view_completion | L0:900行/13058格 / L1:900行/13058格 / L2:900行/13058格 / L3:900行/13058格 | 均未整表匹配 |
| spend_restore_overwritten_mapping | L0:900行/13058格 / L1:900行/13058格 / L2:900行/13058格 / L3:900行/13058格 | 均未整表匹配 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {"ad_account_id": 900, "conversion_purchases": 900, "cost_per_install": 900, "cost_per_swipe": 900, "cost_per_thousand_impressions": 900, "cost_per_video_view": 900, "quartile_1": 900, "quartile_2": 900, "quartile_3": 900, "screen_time_millis": 900, "shares": 673, "spend": 900, "story_completes": 900, "swipe_up_rate": 900, "video_views": 685, "view_completion": 900} |
| ad_account_id | {"conversion_purchases": 900, "cost_per_install": 900, "cost_per_swipe": 900, "cost_per_thousand_impressions": 900, "cost_per_video_view": 900, "quartile_1": 900, "quartile_2": 900, "quartile_3": 900, "screen_time_millis": 900, "shares": 673, "spend": 900, "story_completes": 900, "swipe_up_rate": 900, "video_views": 685, "view_completion": 900} |
| conversion_purchases | {"ad_account_id": 900, "cost_per_install": 900, "cost_per_swipe": 900, "cost_per_thousand_impressions": 900, "cost_per_video_view": 900, "quartile_1": 900, "quartile_2": 900, "quartile_3": 900, "screen_time_millis": 900, "shares": 673, "spend": 900, "story_completes": 900, "swipe_up_rate": 900, "video_views": 685, "view_completion": 900} |
| cost_per_install | {"ad_account_id": 900, "conversion_purchases": 900, "cost_per_swipe": 900, "cost_per_thousand_impressions": 900, "cost_per_video_view": 900, "quartile_1": 900, "quartile_2": 900, "quartile_3": 900, "screen_time_millis": 900, "shares": 673, "spend": 900, "story_completes": 900, "swipe_up_rate": 900, "video_views": 685, "view_completion": 900} |
| cost_per_swipe | {"ad_account_id": 900, "conversion_purchases": 900, "cost_per_install": 900, "cost_per_thousand_impressions": 900, "cost_per_video_view": 900, "quartile_1": 900, "quartile_2": 900, "quartile_3": 900, "screen_time_millis": 900, "shares": 673, "spend": 900, "story_completes": 900, "swipe_up_rate": 900, "video_views": 685, "view_completion": 900} |
| cost_per_thousand_impressions | {"ad_account_id": 900, "conversion_purchases": 900, "cost_per_install": 900, "cost_per_swipe": 900, "cost_per_video_view": 900, "quartile_1": 900, "quartile_2": 900, "quartile_3": 900, "screen_time_millis": 900, "shares": 673, "spend": 900, "story_completes": 900, "swipe_up_rate": 900, "video_views": 685, "view_completion": 900} |
| cost_per_video_view | {"ad_account_id": 900, "conversion_purchases": 900, "cost_per_install": 900, "cost_per_swipe": 900, "cost_per_thousand_impressions": 900, "quartile_1": 900, "quartile_2": 900, "quartile_3": 900, "screen_time_millis": 900, "shares": 673, "spend": 900, "story_completes": 900, "swipe_up_rate": 900, "video_views": 685, "view_completion": 900} |
| quartile_1 | {"ad_account_id": 900, "conversion_purchases": 900, "cost_per_install": 900, "cost_per_swipe": 900, "cost_per_thousand_impressions": 900, "cost_per_video_view": 900, "quartile_2": 900, "quartile_3": 900, "screen_time_millis": 900, "shares": 673, "spend": 900, "story_completes": 900, "swipe_up_rate": 900, "video_views": 685, "view_completion": 900} |
| quartile_2 | {"ad_account_id": 900, "conversion_purchases": 900, "cost_per_install": 900, "cost_per_swipe": 900, "cost_per_thousand_impressions": 900, "cost_per_video_view": 900, "quartile_1": 900, "quartile_3": 900, "screen_time_millis": 900, "shares": 673, "spend": 900, "story_completes": 900, "swipe_up_rate": 900, "video_views": 685, "view_completion": 900} |
| quartile_3 | {"ad_account_id": 900, "conversion_purchases": 900, "cost_per_install": 900, "cost_per_swipe": 900, "cost_per_thousand_impressions": 900, "cost_per_video_view": 900, "quartile_1": 900, "quartile_2": 900, "screen_time_millis": 900, "shares": 673, "spend": 900, "story_completes": 900, "swipe_up_rate": 900, "video_views": 685, "view_completion": 900} |
| screen_time_millis | {"ad_account_id": 900, "conversion_purchases": 900, "cost_per_install": 900, "cost_per_swipe": 900, "cost_per_thousand_impressions": 900, "cost_per_video_view": 900, "quartile_1": 900, "quartile_2": 900, "quartile_3": 900, "shares": 673, "spend": 900, "story_completes": 900, "swipe_up_rate": 900, "video_views": 685, "view_completion": 900} |
| shares | {"ad_account_id": 900, "conversion_purchases": 900, "cost_per_install": 900, "cost_per_swipe": 900, "cost_per_thousand_impressions": 900, "cost_per_video_view": 900, "quartile_1": 900, "quartile_2": 900, "quartile_3": 900, "screen_time_millis": 900, "spend": 900, "story_completes": 900, "swipe_up_rate": 900, "video_views": 685, "view_completion": 900} |
| spend | {"ad_account_id": 900, "conversion_purchases": 900, "cost_per_install": 900, "cost_per_swipe": 900, "cost_per_thousand_impressions": 900, "cost_per_video_view": 900, "quartile_1": 900, "quartile_2": 900, "quartile_3": 900, "screen_time_millis": 900, "shares": 673, "story_completes": 900, "swipe_up_rate": 900, "video_views": 685, "view_completion": 900} |
| story_completes | {"ad_account_id": 900, "conversion_purchases": 900, "cost_per_install": 900, "cost_per_swipe": 900, "cost_per_thousand_impressions": 900, "cost_per_video_view": 900, "quartile_1": 900, "quartile_2": 900, "quartile_3": 900, "screen_time_millis": 900, "shares": 673, "spend": 900, "swipe_up_rate": 900, "video_views": 685, "view_completion": 900} |
| swipe_up_rate | {"ad_account_id": 900, "conversion_purchases": 900, "cost_per_install": 900, "cost_per_swipe": 900, "cost_per_thousand_impressions": 900, "cost_per_video_view": 900, "quartile_1": 900, "quartile_2": 900, "quartile_3": 900, "screen_time_millis": 900, "shares": 673, "spend": 900, "story_completes": 900, "video_views": 685, "view_completion": 900} |
| video_views | {"ad_account_id": 900, "conversion_purchases": 900, "cost_per_install": 900, "cost_per_swipe": 900, "cost_per_thousand_impressions": 900, "cost_per_video_view": 900, "quartile_1": 900, "quartile_2": 900, "quartile_3": 900, "screen_time_millis": 900, "shares": 673, "spend": 900, "story_completes": 900, "swipe_up_rate": 900, "view_completion": 900} |
| view_completion | {"ad_account_id": 900, "conversion_purchases": 900, "cost_per_install": 900, "cost_per_swipe": 900, "cost_per_thousand_impressions": 900, "cost_per_video_view": 900, "quartile_1": 900, "quartile_2": 900, "quartile_3": 900, "screen_time_millis": 900, "shares": 673, "spend": 900, "story_completes": 900, "swipe_up_rate": 900, "video_views": 685} |
| spend_restore_overwritten_mapping | {"ad_account_id": 900, "conversion_purchases": 900, "cost_per_install": 900, "cost_per_swipe": 900, "cost_per_thousand_impressions": 900, "cost_per_video_view": 900, "quartile_1": 900, "quartile_2": 900, "quartile_3": 900, "screen_time_millis": 900, "shares": 673, "story_completes": 900, "swipe_up_rate": 900, "video_views": 685, "view_completion": 900} |

本表全部重跑证据文件：`records/020_reruns_impl-006_stg_snapchat_ads__campaign_report.json`；`records/020_resume_reruns_impl-006_stg_snapchat_ads__campaign_report.json`。续做重跑私有副本在`data/020_resume_work/`。

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

 映射覆盖有代码自身的明确意图证据，直接适用v2的I定义，不修改规则；复核重跑恢复原先候选列，未套用gold额外清洗。旧gold表达式试验仅作诊断，避免重复计为两个错误点。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-006_stg_snapchat_ads__campaign_report.md`。
- 重跑：`records/020_reruns_impl-006_stg_snapchat_ads__campaign_report.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
