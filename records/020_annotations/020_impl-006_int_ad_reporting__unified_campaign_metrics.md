# impl-006 / int_ad_reporting__unified_campaign_metrics（全量）

## 结论

主要原因：**C**；把握：高。Google ROAS额外四舍五入是主要差异；CTR平台分支还发生回落串用。

参与因素：I：ctr_platform_fallthrough（减6行/6格）。标记：无。

## 差异与归因依据

契约只对CTR/CPC/CPM/CPA规定舍入，Google ROAS明确是正值相除；agent ROUND(...,4)造成433行差异。CTR前6个分支正确写了平台阈值，后2个通用阈值又作用于同一平台，作为I参与因素，有代码自身的意图证据。

层：intermediate；比较库schema：intermediate；评测键：campaign_id, date_day。staging使用agent留存raw，后续层采用gold上游的CS口径，不把上游传导错误归给本表。

已核实的契约原文位置：

- `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml:2627–2717`；完整逐字原文见材料包。
- agent SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql:1–137`；SHA-256 `0a12c1a768ebda76ccadd723c15cd1918e15b7156fe7dcfa44eaa447d0673698`。
- gold（只作差异定位） SQL：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql:1–259`；SHA-256 `da35995d63fc4ee734196a7121e688ebc03cedfe1121ef38288718970258bb1c`。

具体差异表达式和替换（未列出的字节保持不变；共同固定时间除外）：

- google_roas_rounding（agent SQL 第43行起）：
```sql
ROUND(conversions_value / spend, 4)
```
→
```sql
conversions_value / spend
```

- ctr_platform_fallthrough（agent SQL 第108行起）：
```sql
WHEN base.click_through_rate >= 1.0 THEN 'HIGH'
```
→
```sql
WHEN base.platform NOT IN ('amazon_ads','google_ads','facebook_ads') AND base.click_through_rate >= 1.0 THEN 'HIGH'
```

- ctr_platform_fallthrough（agent SQL 第110行起）：
```sql
WHEN base.click_through_rate >= 0.5 THEN 'MEDIUM'
```
→
```sql
WHEN base.platform NOT IN ('amazon_ads','google_ads','facebook_ads') AND base.click_through_rate >= 0.5 THEN 'MEDIUM'
```

## agent可见证据与不确定性

不确定性四档：**看到了但没提**。

event43写统一指标SQL，event67修改base平台字段限定；event84/86只核对输出列。完整99事件未找到ROAS舍入选择的说明；相关字段/表达式已出现，不将执行成功等同于披露。

完整事件扫描数：99；可见输出的机械命中及原始截断标记：

| event | cause | 命中名 | 显式截断 |
|---|---|---|---|
| 8 | 7 | int_ad_reporting__unified_campaign_metrics,stg_amazon_ads__campaign_report,stg_facebook_ads__ad_report,stg_google_ads__campaign_report | False |
| 12 | 11 | linkedin_ad_analytics_by_campaign_data | False |
| 16 | 15 | linkedin_ad_analytics_by_campaign_data | False |
| 18 | 17 | linkedin_ad_analytics_by_campaign_data | False |
| 26 | 25 | int_ad_reporting__unified_campaign_metrics | False |
| 30 | 29 | int_ad_reporting__unified_campaign_metrics,stg_google_ads__campaign_report | False |
| 32 | 31 | int_ad_reporting__unified_campaign_metrics | False |
| 34 | 33 | int_ad_reporting__unified_campaign_metrics,stg_google_ads__campaign_report | False |
| 38 | 37 | int_ad_reporting__unified_campaign_metrics,stg_amazon_ads__campaign_report,stg_facebook_ads__ad_report,stg_google_ads__campaign_report | False |
| 46 | 45 | int_ad_reporting__unified_campaign_metrics | False |
| 48 | 47 | int_ad_reporting__unified_campaign_metrics | False |
| 54 | 53 | int_ad_reporting__unified_campaign_metrics | False |
| 68 | 67 | int_ad_reporting__unified_campaign_metrics | False |
| 82 | 81 | stg_amazon_ads__campaign_report,stg_facebook_ads__ad_report,stg_google_ads__campaign_report | False |
| 84 | 83 | int_ad_reporting__unified_campaign_metrics | False |
| 86 | 85 | stg_amazon_ads__campaign_report,stg_facebook_ads__ad_report,stg_google_ads__campaign_report | False |

此表的可见性判定以原始输出和上面引句为准；命中表名的执行日志或只返回列数，不证明已核实值或业务性质。event中的args.command/message重复代码不当作选择理由，最终报告中的策略按其实际覆盖范围引用。

## 核实查询与诊断

核实查询条数（含失败尝试）：1；核实代价档：一条查询。全部连接原件read_only=True，查询只用agent当时可见库。

### 核实 1

数据库：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/ad_reporting.duckdb`

```sql
SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='raw' AND table_name='linkedin_ad_analytics_by_campaign_data') OR (table_schema='staging' AND table_name='stg_amazon_ads__campaign_report') OR (table_schema='staging' AND table_name='stg_facebook_ads__ad_report') OR (table_schema='staging' AND table_name='stg_google_ads__campaign_report') ORDER BY table_schema,table_name,ordinal_position
```

结果：`[["raw", "linkedin_ad_analytics_by_campaign_data", "campaign_id", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "day", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "action_clicks", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "ad_unit_clicks", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "approximate_unique_impressions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "card_clicks", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "card_impressions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "clicks", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "comment_likes", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "comments", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "company_page_clicks", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "conversion_value_in_local_currency", "DOUBLE"], ["raw", "linkedin_ad_analytics_by_campaign_data", "cost_in_local_currency", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "cost_in_usd", "DOUBLE"], ["raw", "linkedin_ad_analytics_by_campaign_data", "external_website_conversions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "external_website_post_click_conversions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "external_website_post_view_conversions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "follows", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "full_screen_plays", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "impressions", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "landing_page_clicks", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "lead_generation_mail_contact_info_shares", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "lead_generation_mail_interested_clicks", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "likes", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "one_click_lead_form_opens", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "one_click_leads", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "opens", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "other_engagements", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "shares", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "text_url_clicks", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "total_engagements", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "video_completions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "video_first_quartile_completions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "video_midpoint_completions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "video_starts", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "video_third_quartile_completions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "video_views", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_card_clicks", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_card_impressions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_clicks", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_comment_likes", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_comments", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_company_page_clicks", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_external_website_conversions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_external_website_post_click_conversions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_external_website_post_view_conversions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_follows", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_full_screen_plays", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_impressions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_landing_page_clicks", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_likes", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_one_click_lead_form_opens", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_one_click_leads", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_other_engagements", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_shares", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_total_engagements", "BIGINT"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_video_completions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_video_first_quartile_completions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_video_midpoint_completions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_video_starts", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_video_third_quartile_completions", "VARCHAR"], ["raw", "linkedin_ad_analytics_by_campaign_data", "viral_video_views", "BIGINT"], ["staging", "stg_amazon_ads__campaign_report", "platform", "VARCHAR"], ["staging", "stg_amazon_ads__campaign_report", "campaign_id", "VARCHAR"], ["staging", "stg_amazon_ads__campaign_report", "date_day", "DATE"], ["staging", "stg_amazon_ads__campaign_report", "campaign_applicable_budget_rule_id", "VARCHAR"], ["staging", "stg_amazon_ads__campaign_report", "campaign_applicable_budget_rule_name", "VARCHAR"], ["staging", "stg_amazon_ads__campaign_report", "campaign_bidding_strategy", "VARCHAR"], ["staging", "stg_amazon_ads__campaign_report", "campaign_budget_amount", "DECIMAL(18,2)"], ["staging", "stg_amazon_ads__campaign_report", "campaign_budget_currency_code", "VARCHAR"], ["staging", "stg_amazon_ads__campaign_report", "campaign_budget_type", "VARCHAR"], ["staging", "stg_amazon_ads__campaign_report", "campaign_rule_based_budget_amount", "DECIMAL(18,2)"], ["staging", "stg_amazon_ads__campaign_report", "clicks", "INTEGER"], ["staging", "stg_amazon_ads__campaign_report", "cost", "DECIMAL(18,2)"], ["staging", "stg_amazon_ads__campaign_report", "impressions", "INTEGER"], ["staging", "stg_amazon_ads__campaign_report", "sales_7_d", "DECIMAL(18,2)"], ["staging", "stg_amazon_ads__campaign_report", "purchases_30_d", "INTEGER"], ["staging", "stg_amazon_ads__campaign_report", "sales_30_d", "DECIMAL(18,2)"], ["staging", "stg_amazon_ads__campaign_report", "click_through_rate", "DOUBLE"], ["staging", "stg_amazon_ads__campaign_report", "cost_per_click", "DOUBLE"], ["staging", "stg_amazon_ads__campaign_report", "return_on_ad_spend", "DOUBLE"], ["staging", "stg_amazon_ads__campaign_report", "_dbt_loaded_at", "TIMESTAMP WITH TIME ZONE"], ["staging", "stg_facebook_ads__ad_report", "platform", "VARCHAR"], ["staging", "stg_facebook_ads__ad_report", "ad_id", "VARCHAR"], ["staging", "stg_facebook_ads__ad_report", "date_day", "DATE"], ["staging", "stg_facebook_ads__ad_report", "account_id", "VARCHAR"], ["staging", "stg_facebook_ads__ad_report", "impressions", "INTEGER"], ["staging", "stg_facebook_ads__ad_report", "inline_link_clicks", "INTEGER"], ["staging", "stg_facebook_ads__ad_report", "spend", "DECIMAL(18,2)"], ["staging", "stg_facebook_ads__ad_report", "click_through_rate", "INTEGER"], ["staging", "stg_facebook_ads__ad_report", "cost_per_click", "INTEGER"], ["staging", "stg_facebook_ads__ad_report", "cost_per_thousand_impressions", "DOUBLE"], ["staging", "stg_facebook_ads__ad_report", "_dbt_loaded_at", "TIMESTAMP WITH TIME ZONE"], ["staging", "stg_google_ads__campaign_report", "source_relation", "VARCHAR"], ["staging", "stg_google_ads__campaign_report", "account_id", "VARCHAR"], ["staging", "stg_google_ads__campaign_report", "date_day", "DATE"], ["staging", "stg_google_ads__campaign_report", "campaign_id", "VARCHAR"], ["staging", "stg_google_ads__campaign_report", "ad_network_type", "VARCHAR"], ["staging", "stg_google_ads__campaign_report", "device", "VARCHAR"], ["staging", "stg_google_ads__campaign_report", "clicks", "BIGINT"], ["staging", "stg_google_ads__campaign_report", "spend", "DECIMAL(18,2)"], ["staging", "stg_google_ads__campaign_report", "impressions", "BIGINT"], ["staging", "stg_google_ads__campaign_report", "conversions", "DECIMAL(10,2)"], ["staging", "stg_google_ads__campaign_report", "conversions_value", "DECIMAL(15,2)"], ["staging", "stg_google_ads__campaign_report", "view_through_conversions", "BIGINT"]]`

诊断允许读gold，不计入上面的五条限额。详见 `records/020_diagnostics.json`、`records/020_final_diagnostics.json` 中 index=8 的条目；仅在本表有条目时适用。015已核实impl-006/007所有raw三侧一致，校准002一致；025本表实际使用的raw.call_data也三侧一致（2500行、同内容哈希），不把其他Snowflake兼容表的类型改动归给本表。

## 固定时间与重跑

私有目录：`data/020_work/impl-006_int_ad_reporting__unified_campaign_metrics/`。原始数据库仅READ_ONLY attach；只复制所需上游表。共同时间替换：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-12 12:00:00+00'", "count": 4}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-12'", "count": 1}]`。

留存结果同口径规模：439行 / 439格；重跑基线：439行 / 439格。

| 实验 | L0–L3 行数/格子规模 | 整表首次匹配 |
|---|---|---|
| baseline | L0:439行/439格 / L1:439行/439格 / L2:8行/8格 / L3:8行/8格 | 均未整表匹配 |
| google_roas_rounding | L0:6行/6格 / L1:6行/6格 / L2:6行/6格 / L3:6行/6格 | 均未整表匹配 |
| ctr_platform_fallthrough | L0:433行/433格 / L1:433行/433格 / L2:2行/2格 / L3:2行/2格 | 均未整表匹配 |

不适用：主要原因不是U；完整实现诊断不当作U局部修复。

完整每列不一致数（含键，L0–L3）和单侧/重复键额外行数见本表配套重跑JSON的每个comparison.levels；这里另展开L0非零列计数：

| 实验 | L0每列不一致数 |
|---|---|
| baseline | {"ctr_performance_tier": 6, "return_on_ad_spend": 433} |
| google_roas_rounding | {"ctr_performance_tier": 6} |
| ctr_platform_fallthrough | {"return_on_ad_spend": 433} |

本表全部重跑证据文件：`records/020_reruns_impl-006_int_ad_reporting__unified_campaign_metrics.json`。续做重跑私有副本在`data/020_resume_work/`。

规模先行数、相同再按格子数。重复键先抵消整行相等项，剩余按既有脚本固定字典序配对，因此单列patch也可能改变其他列的配对；不是逐列计数简单相加来选择主因。类别相同的并列项合并类别；完全无改善不列参与因素。

## 规则问题

无。

## 证据路径

- 精简材料包：`records/020_packages/020_impl-006_int_ad_reporting__unified_campaign_metrics.md`。
- 重跑：`records/020_reruns_impl-006_int_ad_reporting__unified_campaign_metrics.json`（含old/new、偏移、SHA-256、全部层级逐列计数）。
- 核实：`records/020_queries.json`；校准另见 `records/020_calibration_queries.json`。
- 轨迹：`records/020_trace_audit.json` 中逐event路径；归档 `traces/dacomp_deimpl_prev.tar.gz`。
- 输入快照：`records/020_input_before.json`。
