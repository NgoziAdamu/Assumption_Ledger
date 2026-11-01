# impl-006_ad_reporting__executive_dashboard（038 正式表）

主要原因：**已说出的降级**；把握：中。020定稿旧主要原因：`D`，仅原样保留。

## 范围与材料

- 层：marts。范围清单：`records/038_scope.json`。

- 原契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`，[3406, 3540]行；初始event1完整在场，未截断。

- 交付SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__executive_dashboard.sql`。

- 对比执行输入：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/ad_reporting.duckdb`；staging使用agent留存raw，其余层沿用020标准上游的逐表评测口径，不把上游错误传播计入本表。

- impl-006：finish97/result.md及SQL注释为交付物。impl-007：无finish/result.md，65/67草稿失败且SQL无注释，不能第1/2档。

- 保护与原始数据：`records/038_checks/input_hashes_before.json`；013_raw_differences无006/007改动条目。

## 逐点标注

### 首源投影/整表NULL替代模型（同类缺口组）

- 类别：已说出的降级；角色：主要；把握：中。

- 是否说出：第1档（交付物里针对本处说明了）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

要求月度战略指标连接客户/地理/平台KPI并汇总、分类与建议；42个字段全NULL逐行读取统一指标源，不是执行仪表板。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> business_logic: '- Executive KPIs (last 12 months): For each platform and month, compute monthly investment (sum of spend), average daily spend, active days, totals for impressions/clicks/conversions/revenue, average CTR/CPC/CPA/ROAS (CTR and ROAS rounded to 4 decimals; CPC and CPA to 2), and volatility as the standard deviation of daily CTR (rounded to 4) and CPC (rounded to 2). Growth and anomaly placeholders are set to zero. - Customer insights (last 12 months): For each acquisition cohort month, compute new customers (distinct count), cohort revenue (sum), average customer value and lifespan, counts of high-value, highly engaged, and frequent converters, average retention for months 1–3, average customer ROAS and order value, average platforms used per customer, and count of multi-platform customers (used more than one platform). - Geographic performance (last 6 months): For each month and region, compute active countries (distinct count), regional investment (sum), average market CTR and CPC, spend in high-opportunity markets (sum) and count of such markets, mature market ratio (share of markets classified as mature), average market share and performance percentiles, and average multi-channel adoption. - Unified performance (last 12 months): For each month, compute active platforms (distinct count), monthly totals for impressions/clicks/spend/conversions/revenue, blended averages for CTR/CPC/ROAS (rounded as above), variance across platforms for CTR (rounded to 4) and CPC (rounded to 2), designate platform leaders (CTR leader is google_ads; efficiency and ROAS leaders are amazon_ads), and campaign metrics (distinct active campaigns, average campaign age, counts of new vs established campaigns). - Strategic insights by month: - Investment efficiency grade from overall ROAS thresholds (≥3.0, ≥2.0, ≥1.0, else). - Month-over-month growth rate as percent change in monthly spend versus the prior month, rounded to 2, and set to NULL if no prior month exists. - Portfolio diversification based on active platforms and CTR variance. - Expansion mode based on the ratio of new to established campaigns. - Performance consistency based on CTR and CPC variance thresholds. - Carry forward monthly totals, blended metrics, counts, and platform leaders. - Final output: Start from strategic insights; left join platform-level KPIs by month; left join cohort-level customer insights by cohort month; left join regional geographic performance by month; filter to the last 6 reporting months; group by month and the exposed categorical fields. - Aggregate per reporting_month: customer and geographic metrics are averaged or summed across joined rows; leader platform KPIs are taken from the platform that matches the designated leader; anomaly days use the maximum; performance volatility uses the average; platform growth uses the average; scaling and optimizing days use sums. - Recommendations and strategies: - Executive recommendation based on efficiency grade, consistency, expansion status, growth rate, and overall ROAS (with a default fallback). - Allocation strategy prioritizes when efficiency and ROAS leaders align; else considers low overall ROAS; else considers high average spend in high-opportunity markets; else defaults. Comparisons against aggregated values treat NULLs as not satisfying thresholds. - Customer strategy insight evaluates retention, high-value customer mix (with zero-division protection), and cross-platform engagement, with a default fallback. - Data quality and metadata: platforms_with_data is the count of platforms present in the platform KPI join for the month (0 when none); analysis_period_start and analysis_period_end both equal the reporting_month; dashboard_generated_at is the current timestamp; results are ordered by reporting_month descending.'

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__executive_dashboard.sql`，`delivered SQL`：

> SELECT
>     NULL::DATE AS "reporting_month",
>     NULL::BIGINT AS "reporting_year",
>     NULL::BIGINT AS "reporting_quarter",
>     NULL::DOUBLE AS "monthly_ad_spend",
>     NULL::DECIMAL(38,2) AS "monthly_revenue",
>     NULL::DOUBLE AS "overall_roas",
>     NULL::DOUBLE AS "overall_ctr",
>     NULL::DOUBLE AS "overall_cpc",
>     NULL::VARCHAR AS "investment_efficiency_grade",
>     NULL::DOUBLE AS "month_over_month_growth_rate",
>     NULL::VARCHAR AS "portfolio_diversification",
>     NULL::VARCHAR AS "expansion_mode",
>     NULL::VARCHAR AS "performance_consistency",
>     NULL::BIGINT AS "platforms_in_use",
>     NULL::BIGINT AS "total_active_campaigns",
>     NULL::VARCHAR AS "performance_leader_ctr",
>     NULL::VARCHAR AS "efficiency_leader",
>     NULL::VARCHAR AS "revenue_leader",
>     NULL::DOUBLE AS "monthly_avg_customer_value",
>     NULL::HUGEINT AS "monthly_new_customers",
>     NULL::DOUBLE AS "avg_customer_retention_rate",
>     NULL::HUGEINT AS "high_value_customers_acquired",
>     NULL::DOUBLE AS "avg_platforms_per_customer",
>     NULL::DOUBLE AS "avg_countries_active",
>     NULL::DOUBLE AS "high_opportunity_spend_ratio",
>     NULL::DOUBLE AS "mature_markets_percentage",
>     NULL::DOUBLE AS "avg_market_position_percentile",
>     NULL::DOUBLE AS "top_platform_roas",
>     NULL::DOUBLE AS "top_platform_ctr",
>     NULL::DOUBLE AS "top_platform_cpc",
>     NULL::INTEGER AS "max_platform_anomaly_days",
>     NULL::DOUBLE AS "avg_performance_volatility",
>     NULL::DOUBLE AS "avg_platform_growth_rate",
>     NULL::HUGEINT AS "total_scaling_days",
>     NULL::HUGEINT AS "total_optimizing_days",
>     NULL::VARCHAR AS "executive_recommendation",
>     NULL::VARCHAR AS "allocation_strategy",
>     NULL::VARCHAR AS "customer_strategy_insight",
>     NULL::BIGINT AS "platforms_with_data",
>     NULL::DATE AS "analysis_period_start",
>     NULL::DATE AS "analysis_period_end",
>     NULL::TIMESTAMP WITH TIME ZONE AS "dashboard_generated_at"
> FROM intermediate.int_ad_reporting__unified_campaign_metrics

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 当前实现以结构化 NULL/直接字段投影保障执行，并非完整的客户旅程、地理分析、时间序列、预测及执行仪表板业务逻辑。

fallback生成证据：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/27.json`，`27.args.command`：

> sql='SELECT\n'+',\n'.join(fields)+f'\nFROM {src[0]}'

finish 97以“执行仪表板”点名本表并说明占位/未实现；按037表级粒度仅用于本表的该类缺口。

重跑/诊断：`records/020_reruns_impl-006_ad_reporting__executive_dashboard.json#whole_implementation_diagnostic`。仅为整体/共享前提诊断，不据此宣称单点贡献。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 1474/61908 | 0/0 | 1474/61908 |
| L1 | 1474/61908 | 0/0 | 1474/61908 |
| L2 | 1474/61908 | 0/0 | 1474/61908 |
| L3 | 1474/61908 | 0/0 | 1474/61908 |

## 规模、覆盖和不确定

同类候选/共享前提无法逐项排序，按手册第7节以中把握记该类。整段替换或多位置诊断的差异仅定位，不声称为单点修复贡献。

各点非原因不自动删除。未评分列不参与主因排序。完整SQL差分、L0–L3与同口径基线保留在所引JSON。

复用核实查询（包含失败查询，合计预算不超过5）：

- `records/020_queries.json[8]`：`SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='intermediate' AND table_name='int_ad_reporting__unified_campaign_metrics') ORDER BY table_schema,table_name,ordinal_position`。

规则问题：采用手册第7节同类候选无法逐项排序的口径，合并记录共享缺口组；整段诊断不是每个字段的单改，不声称独立字段贡献已知。
