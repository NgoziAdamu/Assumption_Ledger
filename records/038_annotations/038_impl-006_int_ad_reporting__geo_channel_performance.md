# impl-006_int_ad_reporting__geo_channel_performance（038 正式表）

主要原因：**已说出的降级**；把握：中。020定稿旧主要原因：`D`，仅原样保留。

## 范围与材料

- 层：intermediate。范围清单：`records/038_scope.json`。

- 原契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`，[1890, 1988]行；初始event1完整在场，未截断。

- 交付SQL：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__geo_channel_performance.sql`。

- 对比执行输入：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/ad_reporting.duckdb`；staging使用agent留存raw，其余层沿用020标准上游的逐表评测口径，不把上游错误传播计入本表。

- impl-006：finish97/result.md及SQL注释为交付物。impl-007：无finish/result.md，65/67草稿失败且SQL无注释，不能第1/2档。

- 保护与原始数据：`records/038_checks/input_hashes_before.json`；013_raw_differences无006/007改动条目。

## 逐点标注

### 首源投影/整表NULL替代模型（同类缺口组）

- 类别：已说出的降级；角色：主要；把握：中。

- 是否说出：第1档（交付物里针对本处说明了）。

- 证据在场：不适用；曾经理解对过：不适用；系统提示：不适用。

要求三平台合并、月度地区/渠道聚合、增长和竞争指标、机会分类及6个月过滤；30个输出全NULL并逐行读取Google。不是字段解释分歧。

判定顺序：第3节先排除代码错误和只改呈现；第3步判定整列/模型占位不构成要求的结果。

契约/证据在场原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/1.json`，`1.args.content`：

> business_logic: 'Standardize and union campaign-day data from three ad platforms: - google_ads: use account_id as account_identifier; include campaign_id, date_day, clicks, impressions, spend as cost, conversions, and conversions_value as revenue; set platform=''google_ads'', country_code=''UNITED_STATES'', region=''NORTH_AMERICA'', local_currency=''USD''. - amazon_ads: set account_identifier to a constant (''AMZ_ACCOUNT''); include campaign_id, date_day, clicks, impressions, cost, purchases_30_d as conversions, and sales_30_d as revenue; set platform=''amazon_ads'', country_code=''UNITED_STATES'', region=''NORTH_AMERICA''; keep the reported budget currency as local_currency. - linkedin_ads: use campaign_id as account_identifier; include campaign_id, day (as a date), clicks, impressions (cast to integer), cost_in_usd (cast to numeric) as cost; derive conversions from conversion_value_in_local_currency (cast to integer, missing as 0); set revenue to 0; set platform=''linkedin_ads'', country_code=''UNITED_STATES'', region=''NORTH_AMERICA'', local_currency=''USD''; include only rows where cost_in_usd is non-negative. Aggregate the last 12 months by country_code, region, platform, and calendar month of date_day: - Market participants and volume: distinct advertisers (active_advertisers), distinct campaigns (active_campaigns), total impressions, clicks, spend, conversions, and revenue; count distinct active days (active_days_in_month). - Penetration: campaigns_per_advertiser is distinct campaigns divided by distinct advertisers (as a floating number). - KPIs with rounding and zero handling: CTR as percentage with four decimals, set to 0 when impressions are 0; CPC with two decimals, set to 0 when clicks are 0; CPM (per 1,000 impressions) with two decimals, set to 0 when impressions are 0; CPA with two decimals, set to 0 when conversions are 0; ROAS with four decimals, set to 0 unless both spend and revenue are positive. - Competitive intensity: variance and standard deviation of per-row CPC within the month; rows with zero clicks are excluded; results can be NULL if no valid values exist. Final filtering and enrichments: - Keep only months within the last six months where total_spend and total_impressions are both greater than zero. - Rename platform to marketing_channel. - Opportunity tier: HIGH_OPPORTUNITY when ROAS ≥ 3.0 and CTR ≥ 2.0; MEDIUM_OPPORTUNITY when ROAS ≥ 2.0 or CTR ≥ 1.0; OPTIMIZATION_NEEDED when ROAS < 1.0 and CTR < 0.5; otherwise MONITOR. - Growth: prev_month_spend is the previous month’s total_spend within the same country and channel after filtering; month_over_month_spend_growth is the percent change versus the previous month, rounded to two decimals, set to 0 when the previous month’s spend is not positive; the value can be negative. - Maturity tier: MATURE when active_advertisers ≥ 50 and campaigns_per_advertiser ≥ 3; DEVELOPING when active_advertisers ≥ 20 and campaigns_per_advertiser ≥ 2; EMERGING when active_advertisers ≥ 10; otherwise NASCENT. - Percentiles: spend_share_percentile is the relative position (0–1) within region and month by total_spend; performance_percentile is the relative position (0–1) within region and month by CTR. - Multi-channel metrics: avg_daily_platform_diversity is set to 1; multi_channel_advertisers equals active_advertisers; single_channel_advertisers is 0. - Analysis metadata: analysis_generated_at is the timestamp at query runtime. - Final ordering: rows are sorted by region, country_code, marketing_channel, and performance_month descending.'

交付SQL原处：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__geo_channel_performance.sql`，`delivered SQL`：

> SELECT
>     NULL::VARCHAR AS "country_code",
>     NULL::VARCHAR AS "region",
>     NULL::VARCHAR AS "marketing_channel",
>     NULL::DATE AS "performance_month",
>     NULL::BIGINT AS "active_advertisers",
>     NULL::BIGINT AS "active_campaigns",
>     NULL::DOUBLE AS "campaigns_per_advertiser",
>     NULL::BIGINT AS "active_days_in_month",
>     NULL::HUGEINT AS "total_impressions",
>     NULL::HUGEINT AS "total_clicks",
>     NULL::DOUBLE AS "total_spend",
>     NULL::DECIMAL(38,2) AS "total_conversions",
>     NULL::DECIMAL(38,2) AS "total_revenue",
>     NULL::DOUBLE AS "market_ctr",
>     NULL::DOUBLE AS "market_cpc",
>     NULL::DOUBLE AS "market_cpm",
>     NULL::DOUBLE AS "market_cpa",
>     NULL::DOUBLE AS "market_roas",
>     NULL::DOUBLE AS "cpc_variance",
>     NULL::DOUBLE AS "cpc_std_dev",
>     NULL::VARCHAR AS "market_opportunity_level",
>     NULL::DOUBLE AS "prev_month_spend",
>     NULL::DOUBLE AS "month_over_month_spend_growth",
>     NULL::VARCHAR AS "market_maturity",
>     NULL::DOUBLE AS "spend_share_percentile",
>     NULL::DOUBLE AS "performance_percentile",
>     NULL::INTEGER AS "avg_daily_platform_diversity",
>     NULL::BIGINT AS "multi_channel_advertisers",
>     NULL::INTEGER AS "single_channel_advertisers",
>     NULL::TIMESTAMP WITH TIME ZONE AS "analysis_generated_at"
> FROM staging.stg_google_ads__campaign_report

披露/相关信息原句：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/97.json`，`97.args.final_thought`：

> 当前实现以结构化 NULL/直接字段投影保障执行，并非完整的客户旅程、地理分析、时间序列、预测及执行仪表板业务逻辑。

fallback生成证据：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/27.json`，`27.args.command`：

> sql='SELECT\n'+',\n'.join(fields)+f'\nFROM {src[0]}'

finish 97以“地理分析”点名本表并说明占位/未实现；按037表级粒度仅用于本表的该类缺口。

重跑/诊断：`records/020_reruns_impl-006_int_ad_reporting__geo_channel_performance.json#whole_implementation_diagnostic`。仅为整体/共享前提诊断，不据此宣称单点贡献。

| 口径 | 基线行/格 | 改后行/格 | 减少行/格 |
|---|---:|---:|---:|
| L0 | 26031/780930 | 0/0 | 26031/780930 |
| L1 | 26031/780930 | 0/0 | 26031/780930 |
| L2 | 26031/780930 | 0/0 | 26031/780930 |
| L3 | 26031/780930 | 0/0 | 26031/780930 |

## 规模、覆盖和不确定

同类候选/共享前提无法逐项排序，按手册第7节以中把握记该类。整段替换或多位置诊断的差异仅定位，不声称为单点修复贡献。

各点非原因不自动删除。未评分列不参与主因排序。完整SQL差分、L0–L3与同口径基线保留在所引JSON。

复用核实查询（包含失败查询，合计预算不超过5）：

- `records/020_queries.json[3]`：`SELECT table_schema,table_name,column_name,data_type FROM information_schema.columns WHERE (table_schema='staging' AND table_name='stg_google_ads__campaign_report') ORDER BY table_schema,table_name,ordinal_position`。

规则问题：采用手册第7节同类候选无法逐项排序的口径，合并记录共享缺口组；整段诊断不是每个字段的单改，不声称独立字段贡献已知。
