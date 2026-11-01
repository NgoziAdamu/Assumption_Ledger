# impl-006_int_ad_reporting__monthly_campaign_region_report（038 正式表）

主要原因：**Quiet Downgrade**；把握：中。020定稿旧主要原因：`D`，仅原样保留。

## 范围与材料

- 层：intermediate。范围清单：`records/038_scope.json`。

- 原契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`，[2206, 2332]行；初始event1完整在场，未截断。

- 交付SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__monthly_campaign_region_report.sql`。

- 对比执行输入：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/ad_reporting.duckdb`；staging使用agent留存raw，其余层沿用020标准上游的逐表评测口径，不把上游错误传播计入本表。

- impl-006：finish97/result.md及SQL注释为交付物。impl-007：无finish/result.md，65/67草稿失败且SQL无注释，不能第1/2档。

- 保护与原始数据：`records/038_checks/input_hashes_before.json`；013_raw_differences无006/007改动条目。

## 逐点标注

### 首源投影/整表NULL替代模型（同类缺口组）

- 类别：Quiet Downgrade；角色：主要；把握：中。

- 是否说出：第2档（交付物里只有通用说明）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

要求region/campaign/月粒度聚合、country_list、月度KPI、区域份额及筛选；仅投影首源，其他NULL，无区域月度计算。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> business_logic: '- Source: intermediate.int_ad_reporting__campaign_report; include only rows where date_day is not null. - Derive geography per row: - region by platform: google_ads/facebook_ads/amazon_ads/linkedin_ads/microsoft_ads/pinterest_ads/snapchat_ads/reddit_ads/apple_search_ads → North America; tiktok_ads/twitter_ads → Global; else Unknown. - country_code by platform: google_ads/facebook_ads/amazon_ads → US; else Unknown. - Group by keys: platform, region, account_id, campaign_id, campaign_name, and time fields where: - month_year is the first day of the month for date_day; year is the calendar year; month is the calendar month number (1–12). - Geographic aggregates: - countries_in_region counts distinct country_code values. - country_list concatenates distinct country_code values separated by ", ", ordered ascending, excluding nulls, preserving original casing. - Aggregate metrics: - Sum impressions, clicks, interactions, cost, conversions, conversions_value, and view_through_conversions (nulls ignored). - For active_view_impressions, active_view_measurable_impressions, attributed_sales_14_d, attributed_sales_30_d, attributed_conversions_14_d, attributed_conversions_30_d: treat nulls as 0 before summing. - Derived monthly regional KPIs (division-by-zero handling and rounding): - Click-through rate: 100 times clicks divided by impressions over the group, rounded to 4 decimals; 0 when impressions are 0. - Cost per click: cost divided by clicks, rounded to 2 decimals; 0 when clicks are 0. - Cost per thousand impressions: cost per 1,000 impressions, rounded to 2 decimals; 0 when impressions are 0. - Cost per conversion: cost divided by conversions, rounded to 2 decimals; 0 when conversions are 0. - Return on ad spend: conversions_value divided by cost, rounded to 4 decimals; 0 when cost or conversions_value is 0. - Amazon ROAS 30d: attributed_sales_30_d divided by cost, rounded to 4 decimals; 0 when cost or attributed_sales_30_d is 0. - Activity and daily averages: - days_active_in_month counts distinct active dates. - avg_daily_regional_spend: total cost divided by days_active_in_month, rounded to 2 decimals. - avg_daily_regional_impressions: total impressions divided by days_active_in_month, rounded to 0 decimals. - avg_daily_regional_clicks: total clicks divided by days_active_in_month, rounded to 0 decimals. - Platform-month share and concentration (computed across all regions within each platform and month): - regional_cost_share_pct: percent of platform-month total cost contributed by the group, rounded to 2 decimals; 0 when the platform-month total is 0. - regional_impression_share_pct: percent of platform-month total impressions contributed by the group, rounded to 2 decimals; 0 when the platform-month total is 0. - regional_cost_concentration: fraction of platform-month total cost contributed by the group; null when the platform-month total is 0. - regional_conversion_concentration: fraction of platform-month total conversions contributed by the group; null when the platform-month total is 0. - Data quality dates: first_active_date is the minimum date_day; last_active_date is the maximum date_day. - Exclusions: retain only groups where at least one of impressions, clicks, or cost is greater than 0 for the month. - Load timestamp: _dbt_loaded_at is set to the current timestamp at model run time. - Final ordering: platform ascending, region ascending, month_year descending, then total_cost descending.'

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__monthly_campaign_region_report.sql`，`delivered SQL`：

> SELECT
>     CAST("platform" AS VARCHAR) AS "platform",
>     NULL::VARCHAR AS "region",
>     NULL::DATE AS "month_year",
>     NULL::BIGINT AS "year",
>     NULL::BIGINT AS "month",
>     CAST("account_id" AS INTEGER) AS "account_id",
>     CAST("campaign_id" AS VARCHAR) AS "campaign_id",
>     CAST("campaign_name" AS INTEGER) AS "campaign_name",
>     NULL::BIGINT AS "countries_in_region",
>     NULL::VARCHAR AS "country_list",
>     NULL::HUGEINT AS "total_impressions",
>     NULL::HUGEINT AS "total_clicks",
>     NULL::HUGEINT AS "total_interactions",
>     NULL::DECIMAL(38,2) AS "total_cost",
>     NULL::HUGEINT AS "total_conversions",
>     NULL::DECIMAL(38,2) AS "total_conversions_value",
>     NULL::HUGEINT AS "total_view_through_conversions",
>     NULL::HUGEINT AS "total_active_view_impressions",
>     NULL::HUGEINT AS "total_active_view_measurable_impressions",
>     NULL::DECIMAL(38,2) AS "total_attributed_sales_14_d",
>     NULL::DECIMAL(38,2) AS "total_attributed_sales_30_d",
>     NULL::HUGEINT AS "total_attributed_conversions_14_d",
>     NULL::HUGEINT AS "total_attributed_conversions_30_d",
>     NULL::DOUBLE AS "monthly_regional_click_through_rate",
>     NULL::DOUBLE AS "monthly_regional_cost_per_click",
>     NULL::DOUBLE AS "monthly_regional_cost_per_thousand_impressions",
>     NULL::DOUBLE AS "monthly_regional_cost_per_conversion",
>     NULL::DOUBLE AS "monthly_regional_return_on_ad_spend",
>     NULL::DOUBLE AS "monthly_regional_amazon_roas_30d",
>     NULL::BIGINT AS "days_active_in_month",
>     NULL::DOUBLE AS "avg_daily_regional_spend",
>     NULL::DOUBLE AS "avg_daily_regional_impressions",
>     NULL::DOUBLE AS "avg_daily_regional_clicks",
>     NULL::DOUBLE AS "regional_cost_share_pct",
>     NULL::DOUBLE AS "regional_impression_share_pct",
>     NULL::DOUBLE AS "regional_cost_concentration",
>     NULL::DOUBLE AS "regional_conversion_concentration",
>     NULL::DATE AS "first_active_date",
>     NULL::DATE AS "last_active_date",
>     CAST("_dbt_loaded_at" AS TIMESTAMP WITH TIME ZONE) AS "_dbt_loaded_at"
> FROM intermediate.int_ad_reporting__campaign_report

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 对缺失源字段采用类型明确的 NULL，占用可用字段进行投影，并在缺失加载时间时采用运行时 `CURRENT_TIMESTAMP`。

fallback生成证据：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/27.json`，`27.args.command`：

> sql='SELECT\n'+',\n'.join(fields)+f'\nFROM {src[0]}'

交付报告有适用于多表的转换/NULL策略说明，未点名本表本处，不能升第1档。

重跑/诊断：`records/020_reruns_impl-006_int_ad_reporting__monthly_campaign_region_report.json#whole_implementation_diagnostic`。仅为整体/共享前提诊断，不据此宣称单点贡献。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 17226/671814 | 4236/4236 | 12990/667578 |
| L1 | 17226/671814 | 4236/4236 | 12990/667578 |
| L2 | 17226/671814 | 4236/4236 | 12990/667578 |
| L3 | 17226/671814 | 0/0 | 17226/671814 |

## 规模、覆盖和不确定

同类候选/共享前提无法逐项排序，按手册第7节以中把握记该类。整段替换或多位置诊断的差异仅定位，不声称为单点修复贡献。

各点非原因不自动删除。未评分列不参与主因排序。完整SQL差分、L0–L3与同口径基线保留在所引JSON。

复用核实查询（包含失败查询，合计预算不超过5）：

- `records/020_queries.json[5]`：`SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='intermediate' AND table_name='int_ad_reporting__campaign_report') ORDER BY table_schema,table_name,ordinal_position`。

规则问题：采用手册第7节同类候选无法逐项排序的口径，合并记录共享缺口组；整段诊断不是每个字段的单改，不声称独立字段贡献已知。
