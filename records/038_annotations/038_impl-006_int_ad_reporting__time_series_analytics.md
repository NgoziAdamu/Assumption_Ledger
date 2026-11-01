# impl-006_int_ad_reporting__time_series_analytics（038 正式表）

主要原因：**已说出的降级**；把握：中。020定稿旧主要原因：`D`，仅原样保留。

## 范围与材料

- 层：intermediate。范围清单：`records/038_scope.json`。

- 原契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`，[2442, 2626]行；初始event1完整在场，未截断。

- 交付SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__time_series_analytics.sql`。

- 对比执行输入：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/ad_reporting.duckdb`；staging使用agent留存raw，其余层沿用020标准上游的逐表评测口径，不把上游错误传播计入本表。

- impl-006：finish97/result.md及SQL注释为交付物。impl-007：无finish/result.md，65/67草稿失败且SQL无注释，不能第1/2档。

- 保护与原始数据：`records/038_checks/input_hashes_before.json`；013_raw_differences无006/007改动条目。

## 逐点标注

### 首源投影/整表NULL替代模型（同类缺口组）

- 类别：已说出的降级；角色：主要；把握：中。

- 是否说出：第1档（交付物里针对本处说明了）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

要求四平台日粒度汇总、日历特征、移动窗口/趋势/异常/预测和12个月筛选；57个字段全NULL并逐行读取Google。整段gold诊断仍有149行875格残差，不据此把占位解释成唯一可精确修复的单点。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> business_logic: '- Ingest four ad sources, align fields, and union: - google_ads: cost comes from spend; conversions and conversion value as provided. - amazon_ads: conversions come from purchases_30_d; revenue uses sales_30_d; no conversion value. - facebook_ads: date is converted to date_day; ad_id is treated as the campaign identifier; conversions set to 0; clicks use inline_link_clicks; cost from spend. - linkedin_ads: day is converted to date_day; ensure impressions and cost are numeric; conversions use conversion_value_in_local_currency as an integer count; exclude rows with negative cost_in_usd. - Keep only records with date_day in the last 18 months, then aggregate by date_day and platform: - Sums: impressions, clicks, cost (spend), conversions, revenue (conversion value when present, else 30‑day revenue; missing treated as 0). - KPIs: CTR = 100×(clicks/impressions) rounded to 4 decimals when impressions>0, else 0; CPC = spend/clicks rounded to 2 decimals when clicks>0, else 0; CPA = spend/conversions rounded to 2 decimals when conversions>0, else 0; ROAS = revenue/spend rounded to 4 decimals when both >0, else 0. - Campaign indicators: active_campaigns = distinct campaigns; campaigns_with_clicks = distinct campaigns with clicks>0; market_active_day = 1 when total impressions>0, else 0. - Derive calendar features: day_of_week (0=Sun..6=Sat), week_of_year, month_of_year, quarter_of_year, day_type (WEEKEND when Sun/Sat else WEEKDAY), month_period (EARLY/MID/LATE/END by day of month), and seasonal_period using explicit US seasonal date rules. For trend math, compute days since 1970‑01‑01 as a whole‑day index. - Rolling metrics are computed per platform ordered by date_day and include the current day; if fewer than N days exist, use the available days: - Moving averages: last 7 days (spend, ctr, cpc), last 30 days (spend, ctr, cpc), and last 90 days (spend). - spend_ewma is approximated as the same 7‑day simple average of spend. - Volatility: sample standard deviation over the last 30 days for ctr and cpc. - Trend and seasonality: - 90‑day rolling linear trend slopes for spend and ctr using the day index (days since epoch). - Prior‑period references: values from 365, 30, and 7 days earlier for YoY, MoM, and WoW comparisons. - Baselines: average ctr and spend by day_of_week, and by month_of_year, over the available 18‑month input window. - Anomalies and momentum: - Percent change vs prior periods is computed when the prior value is >0; otherwise NULL. - z‑scores are absolute deviations from the 30‑day mean scaled by the 30‑day standard deviation; 0 when the standard deviation is not positive. - Day‑of‑week deviation is the absolute percent difference from the day‑of‑week average; NULL when the baseline is zero. - Momentum: spend is ACCELERATING when the 7‑day average exceeds 110% of the 30‑day average, DECELERATING when below 90%, else STABLE; ctr is IMPROVING when the 7‑day average exceeds 105% of the 30‑day average, DECLINING when below 95%, else STABLE. - Trend direction from the 90‑day spend slope: STRONG_UPTREND (>0.1), MILD_UPTREND (>0 to 0.1], STRONG_DOWNTREND (<-0.1), MILD_DOWNTREND (<0 to -0.1], else SIDEWAYS. - Forecasting and confidence: - 30‑day trend forecasts add 30 times the 90‑day slope to the 30‑day average (for spend and ctr). - Seasonal factors are ratios of the daily values to the corresponding monthly averages; NULL when the monthly average is zero. - Confidence bounds are the 30‑day average minus/plus two 30‑day standard deviations. - Market signals and actions: - market_state precedence: ANOMALOUS when ctr_z_score>2 or cpc_z_score>2; else VOLATILE when WoW spend change is >50% or <‑50%; else OPTIMIZING when ctr momentum is IMPROVING and spend momentum is STABLE; else SCALING when spend momentum is ACCELERATING and ctr momentum is STABLE; else NORMAL. - requires_investigation is true when ctr_z_score>3, or cpc_z_score>3, or absolute WoW spend change exceeds 200%; otherwise false. - optimization_recommendation: OPTIMIZE_TARGETING when ctr is DECLINING and spend is ACCELERATING; OPTIMIZE_BIDDING when cpc_z_score>2 and ctr momentum is STABLE; SEASONAL_ADJUSTMENT_NEEDED when spend seasonal factor>1.2 and ctr seasonal factor<0.8; SCALE_OPPORTUNITY when market_state is SCALING; otherwise MONITOR. - Finalize by keeping only the last 12 months, ordering by platform ascending and date_day descending, and stamping analysis_generated_at with the current timestamp.'

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__time_series_analytics.sql`，`delivered SQL`：

> SELECT
>     NULL::DATE AS "date_day",
>     NULL::VARCHAR AS "platform",
>     NULL::BIGINT AS "day_of_week",
>     NULL::VARCHAR AS "day_type",
>     NULL::BIGINT AS "week_of_year",
>     NULL::BIGINT AS "month_of_year",
>     NULL::BIGINT AS "quarter_of_year",
>     NULL::VARCHAR AS "seasonal_period",
>     NULL::VARCHAR AS "month_period",
>     NULL::HUGEINT AS "daily_impressions",
>     NULL::HUGEINT AS "daily_clicks",
>     NULL::DOUBLE AS "daily_spend",
>     NULL::DECIMAL(38,2) AS "daily_conversions",
>     NULL::DECIMAL(38,2) AS "daily_revenue",
>     NULL::DOUBLE AS "daily_ctr",
>     NULL::DOUBLE AS "daily_cpc",
>     NULL::DOUBLE AS "daily_cpa",
>     NULL::DOUBLE AS "daily_roas",
>     NULL::BIGINT AS "active_campaigns",
>     NULL::BIGINT AS "campaigns_with_clicks",
>     NULL::INTEGER AS "market_active_day",
>     NULL::DOUBLE AS "spend_7d_ma",
>     NULL::DOUBLE AS "spend_30d_ma",
>     NULL::DOUBLE AS "spend_90d_ma",
>     NULL::DOUBLE AS "spend_ewma",
>     NULL::DOUBLE AS "ctr_7d_ma",
>     NULL::DOUBLE AS "ctr_30d_ma",
>     NULL::DOUBLE AS "cpc_7d_ma",
>     NULL::DOUBLE AS "cpc_30d_ma",
>     NULL::DOUBLE AS "ctr_30d_volatility",
>     NULL::DOUBLE AS "cpc_30d_volatility",
>     NULL::DOUBLE AS "spend_trend_slope_90d",
>     NULL::DOUBLE AS "ctr_trend_slope_90d",
>     NULL::VARCHAR AS "spend_trend_direction",
>     NULL::VARCHAR AS "spend_momentum",
>     NULL::VARCHAR AS "ctr_momentum",
>     NULL::DOUBLE AS "spend_yoy_change_pct",
>     NULL::DOUBLE AS "spend_mom_change_pct",
>     NULL::DOUBLE AS "spend_wow_change_pct",
>     NULL::DOUBLE AS "ctr_z_score",
>     NULL::DOUBLE AS "cpc_z_score",
>     NULL::DOUBLE AS "ctr_dow_deviation_pct",
>     NULL::DOUBLE AS "spend_dow_deviation_pct",
>     NULL::DOUBLE AS "dow_avg_ctr",
>     NULL::DOUBLE AS "dow_avg_spend",
>     NULL::DOUBLE AS "monthly_avg_ctr",
>     NULL::DOUBLE AS "monthly_avg_spend",
>     NULL::DOUBLE AS "spend_seasonal_factor",
>     NULL::DOUBLE AS "ctr_seasonal_factor",
>     NULL::DOUBLE AS "spend_30d_trend_forecast",
>     NULL::DOUBLE AS "ctr_30d_trend_forecast",
>     NULL::DOUBLE AS "spend_lower_confidence",
>     NULL::DOUBLE AS "spend_upper_confidence",
>     NULL::VARCHAR AS "market_state",
>     NULL::BOOLEAN AS "requires_investigation",
>     NULL::VARCHAR AS "optimization_recommendation",
>     NULL::TIMESTAMP WITH TIME ZONE AS "analysis_generated_at"
> FROM staging.stg_google_ads__campaign_report

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 当前实现以结构化 NULL/直接字段投影保障执行，并非完整的客户旅程、地理分析、时间序列、预测及执行仪表板业务逻辑。

fallback生成证据：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/27.json`，`27.args.command`：

> sql='SELECT\n'+',\n'.join(fields)+f'\nFROM {src[0]}'

finish 97以“时间序列”点名本表并说明占位/未实现；按037表级粒度仅用于本表的该类缺口。

重跑/诊断：`records/020_reruns_impl-006_int_ad_reporting__time_series_analytics.json#whole_implementation_diagnostic`。仅为整体/共享前提诊断，不据此宣称单点贡献。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 26181/1466136 | 149/875 | 26032/1465261 |
| L1 | 26181/1466136 | 149/875 | 26032/1465261 |
| L2 | 26181/1466136 | 0/0 | 26181/1466136 |
| L3 | 26181/1466136 | 0/0 | 26181/1466136 |

## 规模、覆盖和不确定

同类候选/共享前提无法逐项排序，按手册第7节以中把握记该类。整段替换或多位置诊断的差异仅定位，不声称为单点修复贡献。

各点非原因不自动删除。未评分列不参与主因排序。完整SQL差分、L0–L3与同口径基线保留在所引JSON。

复用核实查询（包含失败查询，合计预算不超过5）：

- `records/020_queries.json[6]`：`SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='staging' AND table_name='stg_google_ads__campaign_report') ORDER BY table_schema,table_name,ordinal_position`。

规则问题：采用手册第7节同类候选无法逐项排序的口径，合并记录共享缺口组；整段诊断不是每个字段的单改，不声称独立字段贡献已知。
