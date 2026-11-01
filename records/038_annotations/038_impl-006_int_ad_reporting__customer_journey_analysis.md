# impl-006_int_ad_reporting__customer_journey_analysis（038 正式表）

主要原因：**已说出的降级**；把握：中。020定稿旧主要原因：`D`，仅原样保留。

## 范围与材料

- 层：intermediate。范围清单：`records/038_scope.json`。

- 原契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`，[1776, 1889]行；初始event1完整在场，未截断。

- 交付SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__customer_journey_analysis.sql`。

- 对比执行输入：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/ad_reporting.duckdb`；staging使用agent留存raw，其余层沿用020标准上游的逐表评测口径，不把上游错误传播计入本表。

- impl-006：finish97/result.md及SQL注释为交付物。impl-007：无finish/result.md，65/67草稿失败且SQL无注释，不能第1/2档。

- 保护与原始数据：`records/038_checks/input_hashes_before.json`；013_raw_differences无006/007改动条目。

## 逐点标注

### 首源投影/整表NULL替代模型（同类缺口组）

- 类别：已说出的降级；角色：主要；把握：中。

- 是否说出：第1档（交付物里针对本处说明了）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

要求合并Google/Amazon/Facebook触点，建立customer_identifier，按客户汇总、分类、归因、留存占位及12个月筛选；34个输出全NULL并逐行读取Google，未建立客户模型。缺口属于同一个结构占位替代行为。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> business_logic: '- Build customer_touchpoints by unifying: - Google Ads: platform=''google_ads''; use account_id as both customer_id and account_id; include campaign_id, date_day, impressions, clicks, spend as cost, conversions, conversions_value; keep only rows with account_id present. - Amazon Ads: platform=''amazon_ads''; no customer_id or account_id; include campaign_id, date_day, impressions, clicks, cost, purchases_30_d as conversions, sales_30_d as revenue_30d. - Facebook Ads: platform=''facebook_ads''; no customer_id; use account_id; set campaign_id from ad_id (as text), date_day from date; include impressions, inline_link_clicks as clicks, spend as cost; set conversions to 0. - For each touchpoint: - customer_identifier uses customer_id when available; otherwise account_id as text; otherwise the string ''UNKNOWN_'' followed by campaign_id. - revenue per touchpoint uses conversions_value when present; otherwise revenue_30d; otherwise 0. - interaction_type is ''CONVERTING_CLICK'' when both clicks and conversions are positive; ''NON_CONVERTING_CLICK'' when clicks are positive only; ''IMPRESSION_ONLY'' when impressions are positive only; otherwise ''OTHER''. - Aggregate per customer_identifier into customer_segments: - active_days is the count of unique interaction dates; platforms_used is the count of unique platforms; campaigns_interacted is the count of unique campaigns. - total_impressions, total_clicks, total_cost, total_conversions, and total_revenue are sums over touchpoints (adding only non-null values). - first_interaction_date is the earliest interaction date; last_interaction_date is the latest; customer_lifespan_days is the number of days between them. - click_to_conversion_rate is conversions divided by clicks, scaled by 100 and rounded to 2 decimals; returns 0 when clicks are missing or not positive. - impression_to_click_rate is clicks divided by impressions, scaled by 100 and rounded to 4 decimals; returns 0 when impressions are missing or not positive. - average_order_value is revenue divided by conversions, rounded to 2 decimals; returns 0 when conversions are missing or not positive. - customer_roas is revenue divided by cost, rounded to 4 decimals; returns 0 when cost is missing or not positive. - Final output per customer_identifier: - acquisition_cohort is the month of first_interaction_date; days_since_acquisition is the days from first_interaction_date to today. - customer_value_tier by total_revenue: >=1000 HIGH_VALUE; >=500 MEDIUM_VALUE; >=100 LOW_VALUE; >0 MINIMAL_VALUE; else NO_VALUE. - engagement_level: if active_days>=10 and platforms_used>=2 then HIGHLY_ENGAGED; else if active_days>=5 or platforms_used>=2 then MODERATELY_ENGAGED; else if active_days>=2 then LIGHTLY_ENGAGED; else SINGLE_INTERACTION. - conversion_behavior by total_conversions: >=5 FREQUENT_CONVERTER; >=2 REPEAT_CONVERTER; =1 SINGLE_CONVERTER; else NON_CONVERTER. - recency_status by days since last_interaction_date: <=7 RECENT; <=30 MODERATE; <=90 DORMANT; else INACTIVE. - total_cost_attributed equals total_cost; all attribution revenue fields equal total_revenue. - Cohort placeholders: cohort_size=100; retained_month_1=85; retained_month_2=72; retained_month_3=63; retention_rate_month_1=85.0; retention_rate_month_2=72.0; retention_rate_month_3=63.0. - analysis_generated_at is the run timestamp with timezone. - Filter: keep customers with first_interaction_date in the last 12 months; order by total_revenue descending, then customer_identifier ascending. - Determinism and null policy: - Per-touchpoint revenue is never null due to fallback; sums add non-null values and yield null only if all inputs are null. - Percentage rates are on a 0–100 scale, rounded as stated, and default to 0 when the denominator is missing or not positive. - Distinct counts exclude nulls and do not count duplicates.'

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__customer_journey_analysis.sql`，`delivered SQL`：

> SELECT
>     NULL::VARCHAR AS "customer_identifier",
>     NULL::DATE AS "acquisition_cohort",
>     NULL::DATE AS "first_interaction_date",
>     NULL::DATE AS "last_interaction_date",
>     NULL::BIGINT AS "customer_lifespan_days",
>     NULL::BIGINT AS "days_since_acquisition",
>     NULL::VARCHAR AS "customer_value_tier",
>     NULL::VARCHAR AS "engagement_level",
>     NULL::VARCHAR AS "conversion_behavior",
>     NULL::VARCHAR AS "recency_status",
>     NULL::BIGINT AS "active_days",
>     NULL::BIGINT AS "platforms_used",
>     NULL::BIGINT AS "campaigns_interacted",
>     NULL::HUGEINT AS "total_impressions",
>     NULL::HUGEINT AS "total_clicks",
>     NULL::DECIMAL(38,2) AS "total_conversions",
>     NULL::DECIMAL(38,2) AS "total_revenue",
>     NULL::DOUBLE AS "total_cost_attributed",
>     NULL::DOUBLE AS "click_to_conversion_rate",
>     NULL::DOUBLE AS "impression_to_click_rate",
>     NULL::DOUBLE AS "average_order_value",
>     NULL::DOUBLE AS "customer_roas",
>     NULL::DECIMAL(38,2) AS "total_first_touch_revenue",
>     NULL::DECIMAL(38,2) AS "total_last_touch_revenue",
>     NULL::DECIMAL(38,2) AS "total_linear_attributed_revenue",
>     NULL::DECIMAL(38,2) AS "total_time_decay_attributed_revenue",
>     NULL::INTEGER AS "cohort_size",
>     NULL::INTEGER AS "retained_month_1",
>     NULL::INTEGER AS "retained_month_2",
>     NULL::INTEGER AS "retained_month_3",
>     NULL::DECIMAL(3,1) AS "retention_rate_month_1",
>     NULL::DECIMAL(3,1) AS "retention_rate_month_2",
>     NULL::DECIMAL(3,1) AS "retention_rate_month_3",
>     NULL::TIMESTAMP WITH TIME ZONE AS "analysis_generated_at"
> FROM staging.stg_google_ads__campaign_report

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 当前实现以结构化 NULL/直接字段投影保障执行，并非完整的客户旅程、地理分析、时间序列、预测及执行仪表板业务逻辑。

fallback生成证据：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/27.json`，`27.args.command`：

> sql='SELECT\n'+',\n'.join(fields)+f'\nFROM {src[0]}'

finish 97以“客户旅程”点名本表并说明占位/未实现；按037表级粒度仅用于本表的该类缺口。

重跑/诊断：`records/020_reruns_impl-006_int_ad_reporting__customer_journey_analysis.json#whole_implementation_diagnostic`。仅为整体/共享前提诊断，不据此宣称单点贡献。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 26031/885054 | 0/0 | 26031/885054 |
| L1 | 26031/885054 | 0/0 | 26031/885054 |
| L2 | 26031/885054 | 0/0 | 26031/885054 |
| L3 | 26031/885054 | 0/0 | 26031/885054 |

## 规模、覆盖和不确定

同类候选/共享前提无法逐项排序，按手册第7节以中把握记该类。整段替换或多位置诊断的差异仅定位，不声称为单点修复贡献。

各点非原因不自动删除。未评分列不参与主因排序。完整SQL差分、L0–L3与同口径基线保留在所引JSON。

复用核实查询（包含失败查询，合计预算不超过5）：

- `records/020_queries.json[2]`：`SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='staging' AND table_name='stg_google_ads__campaign_report') ORDER BY table_schema,table_name,ordinal_position`。

规则问题：采用手册第7节同类候选无法逐项排序的口径，合并记录共享缺口组；整段诊断不是每个字段的单改，不声称独立字段贡献已知。
