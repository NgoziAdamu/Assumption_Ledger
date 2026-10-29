> **暂停检查点／待复核草稿**：用户于 2026-10-29 要求暂停。此文件尚未通过任务020最终复核，请勿作为正式定稿使用。

# impl-006 / stg_linkedin_ads__campaign_report（全量）

## 结论

主要原因：**多因并列（A、D）**；把握：高。三列可计算指标的占位，与缺失sends的NULL/0选择并列。

参与因素：A：comments（减0行/1144格）；A：follows（减0行/1107格）；A：likes（减0行/1112格）；A：shares（减0行/1115格）；A：video_completions（减0行/1166格）；A：video_views（减0行/1121格）。标记：已披露。

## 差异与归因依据

raw有计算指标输入而三列NULL，D；raw没有sends，契约没指定默认0，A。其他互动字段非法文本清理为0还是NULL也未规定，A参与因素。

层：staging；比较库schema：staging；评测键：campaign_id。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml:963–1001`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/staging/stg_linkedin_ads__campaign_report.sql:1–26`；SHA-256 `99d16a1fa35ec4409bf24ab0900f9dc9c5bff7deead00cd72c4a1bef0266effa`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/staging/stg_linkedin_ads__campaign_report.sql:1–50`；SHA-256 `cfd67328ac8f2379672f7161956b3601599d6616af9bc2dcc90233fc34c00a58`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- click_through_rate：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS click_through_rate
```
→
```sql
CASE WHEN impressions > 0 THEN ROUND((CAST(clicks AS DECIMAL(18, 3)) / CAST(impressions AS DECIMAL(18, 3))) * 100, 4) ELSE 0 END AS click_through_rate
```

- comments：
```sql
TRY_CAST("comments" AS INTEGER) AS comments
```
→
```sql
CASE WHEN comments = '' OR comments IS NULL OR comments = 'true' OR comments = 'false' THEN 0 ELSE CAST(comments AS INT) END AS comments
```

- cost_per_click：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_click
```
→
```sql
CASE WHEN clicks > 0 THEN ROUND(cost_in_usd / clicks, 2) ELSE 0 END AS cost_per_click
```

- cost_per_thousand_impressions：
```sql
CAST(NULL::DOUBLE AS DOUBLE) AS cost_per_thousand_impressions
```
→
```sql
CASE WHEN impressions > 0 THEN ROUND((cost_in_usd / impressions) * 1000, 2) ELSE 0 END AS cost_per_thousand_impressions
```

- follows：
```sql
TRY_CAST("follows" AS INTEGER) AS follows
```
→
```sql
CASE WHEN follows = '' OR follows IS NULL OR follows = 'true' OR follows = 'false' THEN 0 ELSE CAST(follows AS INT) END AS follows
```

- likes：
```sql
TRY_CAST("likes" AS INTEGER) AS likes
```
→
```sql
CASE WHEN likes = '' OR likes IS NULL OR likes = 'true' OR likes = 'false' THEN 0 ELSE CAST(likes AS INT) END AS likes
```

- sends：
```sql
CAST(NULL::INTEGER AS INTEGER) AS sends
```
→
```sql
CAST(0 AS INT) AS sends
```

- shares：
```sql
TRY_CAST("shares" AS INTEGER) AS shares
```
→
```sql
CASE WHEN shares = '' OR shares IS NULL OR shares = 'true' OR shares = 'false' THEN 0 ELSE CAST(shares AS INT) END AS shares
```

- video_completions：
```sql
TRY_CAST("video_completions" AS INTEGER) AS video_completions
```
→
```sql
CASE WHEN video_completions = '' OR video_completions IS NULL OR video_completions = 'true' OR video_completions = 'false' THEN 0 ELSE CAST(video_completions AS INT) END AS video_completions
```

- video_views：
```sql
CAST(TRY_CAST("video_views" AS BIGINT) AS INTEGER) AS video_views
```
→
```sql
CASE WHEN video_views = '' OR video_views IS NULL OR video_views = 'true' OR video_views = 'false' THEN 0 ELSE CAST(video_views AS INT) END AS video_views
```

## agent可见证据与不确定性

不确定性四档：**click_through_rate=只有通用策略说明；cost_per_click=只有通用策略说明；cost_per_thousand_impressions=只有通用策略说明；sends=只有通用策略说明**。

event 97（args.final_thought）：对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。 event 97（args.final_thought）：脏值转换采用 DuckDB `TRY_CAST`；不可解析值转为 NULL，避免全批失败，但该字段数据会缺失并可能降低后续统计有效性。

完整事件扫描数：99；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | stg_linkedin_ads__campaign_report | False |
| 12 | 11 | linkedin_ad_analytics_by_campaign_data | False |
| 16 | 15 | linkedin_ad_analytics_by_campaign_data | False |
| 18 | 17 | linkedin_ad_analytics_by_campaign_data | False |
| 30 | 29 | stg_linkedin_ads__campaign_report | False |
| 38 | 37 | stg_linkedin_ads__campaign_report | False |
| 82 | 81 | stg_linkedin_ads__campaign_report | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：2；核实代价档：多条查询。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='linkedin_ad_analytics_by_campaign_data') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["raw", "linkedin_ad_analytics_by_campaign_data", "campaign_id", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "day", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "action_clicks", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "ad_unit_clicks", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "approximate_unique_impressions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "card_clicks", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "card_impressions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "clicks", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "comment_likes", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "comments", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "company_page_clicks", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "conversion_value_in_local_currency", "DOUBLE"], ["raw", "linkedin_ad_analytics_by_campaign_data", "cost_in_local_currency", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "cost_in_usd", "DOUBLE"], ["raw", "linkedin_ad_analytics_by_campaign_data", "external_website_conversions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "external_website_post_click_conversions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "external_website_post_view_conversions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "follows", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "full_screen_plays", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "impressions", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "landing_page_clicks", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "lead_generation_mail_contact_info_shares", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "lead_generation_mail_interested_clicks", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "likes", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "one_click_lead_form_opens", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "one_click_leads", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "opens", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "other_engagements", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "shares", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "text_url_clicks", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "total_engagements", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "video_completions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "video_first_quartile_completions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "video_midpoint_completions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "video_starts", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "video_third_quartile_completions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "video_views", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_card_clicks", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_card_impressions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_clicks", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_comment_likes", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_comments", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_company_page_clicks", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_external_website_conversions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_external_website_post_click_conversions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_external_website_post_view_conversions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_follows", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_full_screen_plays", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_impressions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_landing_page_clicks", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_likes", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_one_click_lead_form_opens", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_one_click_leads", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_other_engagements", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_shares", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_total_engagements", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_video_completions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_video_first_quartile_completions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_video_midpoint_completions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_video_starts", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_video_third_quartile_completions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_video_views", "BIGINT"]]`

### 核实 2

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT count(*) n,count(*) FILTER(WHERE "comments" IS NULL) AS c0_null,count(*) FILTER(WHERE "comments" IS NOT NULL AND TRY_CAST("comments" AS DOUBLE) IS NULL) AS c1_not_numeric,count(*) FILTER(WHERE "follows" IS NULL) AS c2_null,count(*) FILTER(WHERE "follows" IS NOT NULL AND TRY_CAST("follows" AS DOUBLE) IS NULL) AS c3_not_numeric,count(*) FILTER(WHERE "impressions" IS NULL) AS c4_null,count(*) FILTER(WHERE "impressions" IS NOT NULL AND TRY_CAST("impressions" AS DOUBLE) IS NULL) AS c5_not_numeric,count(*) FILTER(WHERE "likes" IS NULL) AS c6_null,count(*) FILTER(WHERE "likes" IS NOT NULL AND TRY_CAST("likes" AS DOUBLE) IS NULL) AS c7_not_numeric,count(*) FILTER(WHERE "shares" IS NULL) AS c8_null,count(*) FILTER(WHERE "shares" IS NOT NULL AND TRY_CAST("shares" AS DOUBLE) IS NULL) AS c9_not_numeric,count(*) FILTER(WHERE "video_completions" IS NULL) AS c10_null,count(*) FILTER(WHERE "video_completions" IS NOT NULL AND TRY_CAST("video_completions" AS DOUBLE) IS NULL) AS c11_not_numeric,count(*) FILTER(WHERE "video_views" IS NULL) AS c12_null,count(*) FILTER(WHERE "video_views" IS NOT NULL AND TRY_CAST("video_views" AS DOUBLE) IS NULL) AS c13_not_numeric FROM raw.linkedin_ad_analytics_by_campaign_data
```

结果：`[[1500, 368, 776, 396, 711, 0, 0, 387, 725, 369, 746, 395, 771, 360, 761]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=26 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025的agent修改raw不适用“不可评估”，本次使用留存raw。

## 固定时间与重跑

私有目录：`data/020_work/impl-006_stg_linkedin_ads__campaign_report/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 0}]`。

留存结果同口径规模：1500行 / 12765格；重跑基线：1500行 / 12765格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:1500行/12765格 / L1:1500行/12765格 / L2:1500行/12765格 / L3:1500行/12765格 | 均未整表匹配 |
| click_through_rate | L0:1500行/11265格 / L1:1500行/11265格 / L2:1500行/11265格 / L3:1500行/11265格 | 均未整表匹配 |
| comments | L0:1500行/11621格 / L1:1500行/11621格 / L2:1500行/11621格 / L3:1500行/11621格 | 均未整表匹配 |
| cost_per_click | L0:1500行/11265格 / L1:1500行/11265格 / L2:1500行/11265格 / L3:1500行/11265格 | 均未整表匹配 |
| cost_per_thousand_impressions | L0:1500行/11265格 / L1:1500行/11265格 / L2:1500行/11265格 / L3:1500行/11265格 | 均未整表匹配 |
| follows | L0:1500行/11658格 / L1:1500行/11658格 / L2:1500行/11658格 / L3:1500行/11658格 | 均未整表匹配 |
| likes | L0:1500行/11653格 / L1:1500行/11653格 / L2:1500行/11653格 / L3:1500行/11653格 | 均未整表匹配 |
| sends | L0:1500行/11265格 / L1:1500行/11265格 / L2:1500行/11265格 / L3:1500行/11265格 | 均未整表匹配 |
| shares | L0:1500行/11650格 / L1:1500行/11650格 / L2:1500行/11650格 / L3:1500行/11650格 | 均未整表匹配 |
| video_completions | L0:1500行/11599格 / L1:1500行/11599格 / L2:1500行/11599格 / L3:1500行/11599格 | 均未整表匹配 |
| video_views | L0:1500行/11644格 / L1:1500行/11644格 / L2:1500行/11644格 / L3:1500行/11644格 | 均未整表匹配 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {"click_through_rate": 1500, "comments": 1144, "cost_per_click": 1500, "cost_per_thousand_impressions": 1500, "follows": 1107, "likes": 1112, "sends": 1500, "shares": 1115, "video_completions": 1166, "video_views": 1121} |
| click_through_rate | {"comments": 1144, "cost_per_click": 1500, "cost_per_thousand_impressions": 1500, "follows": 1107, "likes": 1112, "sends": 1500, "shares": 1115, "video_completions": 1166, "video_views": 1121} |
| comments | {"click_through_rate": 1500, "cost_per_click": 1500, "cost_per_thousand_impressions": 1500, "follows": 1107, "likes": 1112, "sends": 1500, "shares": 1115, "video_completions": 1166, "video_views": 1121} |
| cost_per_click | {"click_through_rate": 1500, "comments": 1144, "cost_per_thousand_impressions": 1500, "follows": 1107, "likes": 1112, "sends": 1500, "shares": 1115, "video_completions": 1166, "video_views": 1121} |
| cost_per_thousand_impressions | {"click_through_rate": 1500, "comments": 1144, "cost_per_click": 1500, "follows": 1107, "likes": 1112, "sends": 1500, "shares": 1115, "video_completions": 1166, "video_views": 1121} |
| follows | {"click_through_rate": 1500, "comments": 1144, "cost_per_click": 1500, "cost_per_thousand_impressions": 1500, "likes": 1112, "sends": 1500, "shares": 1115, "video_completions": 1166, "video_views": 1121} |
| likes | {"click_through_rate": 1500, "comments": 1144, "cost_per_click": 1500, "cost_per_thousand_impressions": 1500, "follows": 1107, "sends": 1500, "shares": 1115, "video_completions": 1166, "video_views": 1121} |
| sends | {"click_through_rate": 1500, "comments": 1144, "cost_per_click": 1500, "cost_per_thousand_impressions": 1500, "follows": 1107, "likes": 1112, "shares": 1115, "video_completions": 1166, "video_views": 1121} |
| shares | {"click_through_rate": 1500, "comments": 1144, "cost_per_click": 1500, "cost_per_thousand_impressions": 1500, "follows": 1107, "likes": 1112, "sends": 1500, "video_completions": 1166, "video_views": 1121} |
| video_completions | {"click_through_rate": 1500, "comments": 1144, "cost_per_click": 1500, "cost_per_thousand_impressions": 1500, "follows": 1107, "likes": 1112, "sends": 1500, "shares": 1115, "video_views": 1121} |
| video_views | {"click_through_rate": 1500, "comments": 1144, "cost_per_click": 1500, "cost_per_thousand_impressions": 1500, "follows": 1107, "likes": 1112, "sends": 1500, "shares": 1115, "video_completions": 1166} |

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

无。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-006_stg_linkedin_ads__campaign_report.md`。
- 重跑：`records/020_reruns_impl-006_stg_linkedin_ads__campaign_report.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
