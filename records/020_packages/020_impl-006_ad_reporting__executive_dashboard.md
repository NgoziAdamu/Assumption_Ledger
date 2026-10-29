# impl-006 | marts | ad_reporting__executive_dashboard | 差异：S1；日期 原记录

## 契约完整原文

S3:3406–3540

```yaml
    - name: ad_reporting__executive_dashboard
      description: Executive monthly ad performance, customer, and geographic KPIs with strategic insights (one row per month)
      grain: One row per reporting_month
      source_models:
      - intermediate.int_ad_reporting__unified_campaign_metrics
      - intermediate.int_ad_reporting__customer_journey_analysis
      - intermediate.int_ad_reporting__geo_channel_performance
      business_logic: '- Executive KPIs (last 12 months): For each platform and month, compute monthly investment (sum of spend), average daily spend, active days, totals for impressions/clicks/conversions/revenue, average CTR/CPC/CPA/ROAS (CTR and ROAS rounded to 4 decimals; CPC and CPA to 2), and volatility as the standard deviation of daily CTR (rounded to 4) and CPC (rounded to 2). Growth and anomaly placeholders are set to zero. - Customer insights (last 12 months): For each acquisition cohort month, compute new customers (distinct count), cohort revenue (sum), average customer value and lifespan, counts of high-value, highly engaged, and frequent converters, average retention for months 1–3, average customer ROAS and order value, average platforms used per customer, and count of multi-platform customers (used more than one platform). - Geographic performance (last 6 months): For each month and region, compute active countries (distinct count), regional investment (sum), average market CTR and CPC, spend in high-opportunity markets (sum) and count of such markets, mature market ratio (share of markets classified as mature), average market share and performance percentiles, and average multi-channel adoption. - Unified performance (last 12 months): For each month, compute active platforms (distinct count), monthly totals for impressions/clicks/spend/conversions/revenue, blended averages for CTR/CPC/ROAS (rounded as above), variance across platforms for CTR (rounded to 4) and CPC (rounded to 2), designate platform leaders (CTR leader is google_ads; efficiency and ROAS leaders are amazon_ads), and campaign metrics (distinct active campaigns, average campaign age, counts of new vs established campaigns). - Strategic insights by month: - Investment efficiency grade from overall ROAS thresholds (≥3.0, ≥2.0, ≥1.0, else). - Month-over-month growth rate as percent change in monthly spend versus the prior month, rounded to 2, and set to NULL if no prior month exists. - Portfolio diversification based on active platforms and CTR variance. - Expansion mode based on the ratio of new to established campaigns. - Performance consistency based on CTR and CPC variance thresholds. - Carry forward monthly totals, blended metrics, counts, and platform leaders. - Final output: Start from strategic insights; left join platform-level KPIs by month; left join cohort-level customer insights by cohort month; left join regional geographic performance by month; filter to the last 6 reporting months; group by month and the exposed categorical fields. - Aggregate per reporting_month: customer and geographic metrics are averaged or summed across joined rows; leader platform KPIs are taken from the platform that matches the designated leader; anomaly days use the maximum; performance volatility uses the average; platform growth uses the average; scaling and optimizing days use sums. - Recommendations and strategies: - Executive recommendation based on efficiency grade, consistency, expansion status, growth rate, and overall ROAS (with a default fallback). - Allocation strategy prioritizes when efficiency and ROAS leaders align; else considers low overall ROAS; else considers high average spend in high-opportunity markets; else defaults. Comparisons against aggregated values treat NULLs as not satisfying thresholds. - Customer strategy insight evaluates retention, high-value customer mix (with zero-division protection), and cross-platform engagement, with a default fallback. - Data quality and metadata: platforms_with_data is the count of platforms present in the platform KPI join for the month (0 when none); analysis_period_start and analysis_period_end both equal the reporting_month; dashboard_generated_at is the current timestamp; results are ordered by reporting_month descending.'
      columns:
      - name: reporting_month
        data_type: DATE
        description: Month bucket for all metrics; one output row per month; not null
      - name: reporting_year
        data_type: BIGINT
        description: Calendar year derived from reporting_month; not null
      - name: reporting_quarter
        data_type: BIGINT
        description: Calendar quarter (1–4) derived from reporting_month; not null
      - name: monthly_ad_spend
        data_type: DOUBLE
        description: Total monthly spend across platforms; may be NULL if upstream spend is absent
      - name: monthly_revenue
        data_type: DECIMAL(38,2)
        description: Total monthly 30-day revenue across platforms with two-decimal scale; may be NULL
      - name: overall_roas
        data_type: DOUBLE
        description: Blended ROAS across platforms rounded to 4 decimals; may be NULL
      - name: overall_ctr
        data_type: DOUBLE
        description: Blended CTR across platforms rounded to 4 decimals on a 0–1 scale; may be NULL
      - name: overall_cpc
        data_type: DOUBLE
        description: Blended CPC across platforms rounded to 2 decimals; may be NULL
      - name: investment_efficiency_grade
        data_type: VARCHAR
        description: Efficiency grade derived from overall ROAS thresholds; not null
      - name: month_over_month_growth_rate
        data_type: DOUBLE
        description: Percent change in monthly_ad_spend versus prior month rounded to 2 decimals; NULL when no prior month
      - name: portfolio_diversification
        data_type: VARCHAR
        description: Diversification score based on active platforms and CTR variance; not null
      - name: expansion_mode
        data_type: VARCHAR
        description: Expansion status based on the share of new versus established campaigns; not null
      - name: performance_consistency
        data_type: VARCHAR
        description: Consistency score based on CTR and CPC variance thresholds; not null
      - name: platforms_in_use
        data_type: BIGINT
        description: Number of active platforms in the month; not null
      - name: total_active_campaigns
        data_type: BIGINT
        description: Distinct active campaigns in the month; not null
      - name: performance_leader_ctr
        data_type: VARCHAR
        description: Platform designated as CTR leader (constant google_ads); not null
      - name: efficiency_leader
        data_type: VARCHAR
        description: Platform designated as CPC efficiency leader (constant amazon_ads); not null
      - name: revenue_leader
        data_type: VARCHAR
        description: Platform designated as ROAS leader (constant amazon_ads); not null
      - name: monthly_avg_customer_value
        data_type: DOUBLE
        description: Average customer value for cohorts in the month rounded to 2 decimals; NULL if no cohort data
      - name: monthly_new_customers
        data_type: HUGEINT
        description: New customers acquired in the cohort month; NULL if no cohort data
      - name: avg_customer_retention_rate
        data_type: DOUBLE
        description: Average month-1 retention rate rounded to 2 decimals; NULL if no cohort data
      - name: high_value_customers_acquired
        data_type: HUGEINT
        description: High-value customers acquired in the cohort month; NULL if no cohort data
      - name: avg_platforms_per_customer
        data_type: DOUBLE
        description: Average platforms used per customer rounded to 1 decimal; NULL if no cohort data
      - name: avg_countries_active
        data_type: DOUBLE
        description: Average active countries across regions rounded to a whole number; NULL if no geo data
      - name: high_opportunity_spend_ratio
        data_type: DOUBLE
        description: Percent of spend in high-opportunity markets rounded to 1 decimal; NULL when regional investment is zero or absent
      - name: mature_markets_percentage
        data_type: DOUBLE
        description: Percent of markets classified as mature rounded to 1 decimal; NULL if no geo data
      - name: avg_market_position_percentile
        data_type: DOUBLE
        description: Average market share position percentile (0–100) rounded to 1 decimal; NULL if no geo data
      - name: top_platform_roas
        data_type: DOUBLE
        description: Average ROAS for the revenue leader platform in the month; NULL if no matching platform data
      - name: top_platform_ctr
        data_type: DOUBLE
        description: Average CTR for the CTR leader platform in the month; NULL if no matching platform data
      - name: top_platform_cpc
        data_type: DOUBLE
        description: Average CPC for the efficiency leader platform in the month; NULL if no matching platform data
      - name: max_platform_anomaly_days
        data_type: INTEGER
        description: Maximum anomaly days across platforms for the month; NULL if no platform data
      - name: avg_performance_volatility
        data_type: DOUBLE
        description: Average CTR volatility across platforms rounded to 4 decimals; NULL if no platform data
      - name: avg_platform_growth_rate
        data_type: DOUBLE
        description: Average platform-level month-over-month growth rate rounded to 2 decimals; NULL if no platform data
      - name: total_scaling_days
        data_type: HUGEINT
        description: Total platform-level scaling days in the month; NULL if no platform data
      - name: total_optimizing_days
        data_type: HUGEINT
        description: Total platform-level optimizing days in the month; NULL if no platform data
      - name: executive_recommendation
        data_type: VARCHAR
        description: Recommendation based on efficiency grade, consistency, expansion, growth rate, and ROAS; not null
      - name: allocation_strategy
        data_type: VARCHAR
        description: Allocation guidance based on leader alignment, overall ROAS, and average high-opportunity spend; not null
      - name: customer_strategy_insight
        data_type: VARCHAR
        description: Customer strategy guidance based on retention, high-value mix, and cross-platform engagement; not null
      - name: platforms_with_data
        data_type: BIGINT
        description: Number of platforms present in the platform KPI join for the month; returns 0 when none; not null
      - name: analysis_period_start
        data_type: DATE
        description: Earliest reporting_month in the group (equals reporting_month); not null
      - name: analysis_period_end
        data_type: DATE
        description: Latest reporting_month in the group (equals reporting_month); not null
      - name: dashboard_generated_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Timestamp when the dashboard was generated; not null
```

## agent 最终 SQL

S4

```sql
SELECT
    NULL::DATE AS "reporting_month",
    NULL::BIGINT AS "reporting_year",
    NULL::BIGINT AS "reporting_quarter",
    NULL::DOUBLE AS "monthly_ad_spend",
    NULL::DECIMAL(38,2) AS "monthly_revenue",
    NULL::DOUBLE AS "overall_roas",
    NULL::DOUBLE AS "overall_ctr",
    NULL::DOUBLE AS "overall_cpc",
    NULL::VARCHAR AS "investment_efficiency_grade",
    NULL::DOUBLE AS "month_over_month_growth_rate",
    NULL::VARCHAR AS "portfolio_diversification",
    NULL::VARCHAR AS "expansion_mode",
    NULL::VARCHAR AS "performance_consistency",
    NULL::BIGINT AS "platforms_in_use",
    NULL::BIGINT AS "total_active_campaigns",
    NULL::VARCHAR AS "performance_leader_ctr",
    NULL::VARCHAR AS "efficiency_leader",
    NULL::VARCHAR AS "revenue_leader",
    NULL::DOUBLE AS "monthly_avg_customer_value",
    NULL::HUGEINT AS "monthly_new_customers",
    NULL::DOUBLE AS "avg_customer_retention_rate",
    NULL::HUGEINT AS "high_value_customers_acquired",
    NULL::DOUBLE AS "avg_platforms_per_customer",
    NULL::DOUBLE AS "avg_countries_active",
    NULL::DOUBLE AS "high_opportunity_spend_ratio",
    NULL::DOUBLE AS "mature_markets_percentage",
    NULL::DOUBLE AS "avg_market_position_percentile",
    NULL::DOUBLE AS "top_platform_roas",
    NULL::DOUBLE AS "top_platform_ctr",
    NULL::DOUBLE AS "top_platform_cpc",
    NULL::INTEGER AS "max_platform_anomaly_days",
    NULL::DOUBLE AS "avg_performance_volatility",
    NULL::DOUBLE AS "avg_platform_growth_rate",
    NULL::HUGEINT AS "total_scaling_days",
    NULL::HUGEINT AS "total_optimizing_days",
    NULL::VARCHAR AS "executive_recommendation",
    NULL::VARCHAR AS "allocation_strategy",
    NULL::VARCHAR AS "customer_strategy_insight",
    NULL::BIGINT AS "platforms_with_data",
    NULL::DATE AS "analysis_period_start",
    NULL::DATE AS "analysis_period_end",
    NULL::TIMESTAMP WITH TIME ZONE AS "dashboard_generated_at"
FROM intermediate.int_ad_reporting__unified_campaign_metrics
```

## gold SQL（仅供定位差异）

S5

```sql
-- Executive Dashboard Model
-- High-level KPIs and strategic insights for executive decision making
-- Combines performance, customer behavior, geographic, and temporal analytics
-- Provides actionable insights for budget allocation and strategic planning

WITH executive_kpis AS (
    -- Core performance metrics for executive summary
    SELECT 
        DATE_TRUNC('month', date_day) AS reporting_month,
        platform AS marketing_channel,
        
        -- Investment metrics
        SUM(cost) AS monthly_investment,
        AVG(cost) AS avg_daily_spend,
        COUNT(DISTINCT date_day) AS active_days,
        
        -- Reach and engagement metrics
        SUM(impressions) AS total_impressions,
        SUM(clicks) AS total_clicks,
        SUM(conversions) AS total_conversions,
        SUM(revenue_30d) AS total_revenue,
        
        -- Efficiency metrics
        ROUND(AVG(click_through_rate), 4) AS avg_ctr,
        ROUND(AVG(cost_per_click), 2) AS avg_cpc,
        ROUND(AVG(cost_per_conversion), 2) AS avg_cpa,
        ROUND(AVG(return_on_ad_spend), 4) AS avg_roas,
        
        -- Performance stability
        ROUND(STDDEV(click_through_rate), 4) AS ctr_volatility,
        ROUND(STDDEV(cost_per_click), 2) AS cpc_volatility,
        
        -- Growth indicators (simplified)
        0 AS avg_mom_growth_rate,
        0 AS scaling_days,
        0 AS optimizing_days,
        
        -- Market position (simplified)
        0 AS avg_ctr_performance_score,
        0 AS anomaly_days
        
    FROM intermediate.int_ad_reporting__unified_campaign_metrics
    WHERE date_day >= CURRENT_DATE - INTERVAL '12 months'
    GROUP BY DATE_TRUNC('month', date_day), platform
),

customer_insights AS (
    -- Customer behavior insights for strategic planning
    SELECT 
        acquisition_cohort AS cohort_month,
        
        -- Customer acquisition metrics
        COUNT(DISTINCT customer_identifier) AS new_customers_acquired,
        SUM(total_revenue) AS cohort_total_revenue,
        AVG(total_revenue) AS avg_customer_value,
        AVG(customer_lifespan_days) AS avg_customer_lifespan,
        
        -- Customer quality metrics
        COUNT(CASE WHEN customer_value_tier = 'HIGH_VALUE' THEN 1 END) AS high_value_customers,
        COUNT(CASE WHEN engagement_level = 'HIGHLY_ENGAGED' THEN 1 END) AS highly_engaged_customers,
        COUNT(CASE WHEN conversion_behavior = 'FREQUENT_CONVERTER' THEN 1 END) AS frequent_converters,
        
        -- Retention performance
        AVG(retention_rate_month_1) AS avg_month_1_retention,
        AVG(retention_rate_month_2) AS avg_month_2_retention,
        AVG(retention_rate_month_3) AS avg_month_3_retention,
        
        -- Customer economics
        AVG(customer_roas) AS avg_customer_roas,
        AVG(average_order_value) AS avg_order_value,
        
        -- Platform diversity
        AVG(platforms_used) AS avg_platforms_per_customer,
        COUNT(CASE WHEN platforms_used > 1 THEN 1 END) AS multi_platform_customers
        
    FROM intermediate.int_ad_reporting__customer_journey_analysis
    WHERE acquisition_cohort >= CURRENT_DATE - INTERVAL '12 months'
    GROUP BY acquisition_cohort
),

geographic_performance AS (
    -- Geographic expansion and performance insights
    SELECT 
        performance_month,
        region,
        
        -- Market penetration
        COUNT(DISTINCT country_code) AS countries_active,
        SUM(total_spend) AS regional_investment,
        AVG(market_ctr) AS regional_avg_ctr,
        AVG(market_cpc) AS regional_avg_cpc,
        
        -- Growth opportunity metrics
        SUM(CASE WHEN market_opportunity_level = 'HIGH_OPPORTUNITY' THEN total_spend END) AS high_opportunity_spend,
        COUNT(CASE WHEN market_opportunity_level = 'HIGH_OPPORTUNITY' THEN 1 END) AS high_opportunity_markets,
        
        -- Market maturity
        AVG(CASE WHEN market_maturity = 'MATURE' THEN 1 ELSE 0 END) AS mature_market_ratio,
        
        -- Competitive positioning
        AVG(spend_share_percentile) AS avg_market_share_position,
        AVG(performance_percentile) AS avg_performance_position,
        
        -- Multi-channel effectiveness
        AVG(multi_channel_advertisers) AS avg_multi_channel_adoption
        
    FROM intermediate.int_ad_reporting__geo_channel_performance
    WHERE performance_month >= CURRENT_DATE - INTERVAL '6 months'
    GROUP BY performance_month, region
),

unified_performance AS (
    -- Platform comparison and cross-platform insights
    SELECT 
        DATE_TRUNC('month', date_day) AS reporting_month,
        
        -- Overall business metrics
        COUNT(DISTINCT platform) AS active_platforms,
        SUM(impressions) AS total_monthly_impressions,
        SUM(clicks) AS total_monthly_clicks,
        SUM(cost) AS total_monthly_spend,
        SUM(conversions) AS total_monthly_conversions,
        SUM(revenue_30d) AS total_monthly_revenue,
        
        -- Cross-platform efficiency
        ROUND(AVG(click_through_rate), 4) AS blended_ctr,
        ROUND(AVG(cost_per_click), 2) AS blended_cpc,
        ROUND(AVG(return_on_ad_spend), 4) AS blended_roas,
        
        -- Performance distribution
        ROUND(STDDEV(click_through_rate), 4) AS ctr_variance_across_platforms,
        ROUND(STDDEV(cost_per_click), 2) AS cpc_variance_across_platforms,
        
        -- Platform leadership (simplified)
        'google_ads' AS best_ctr_platform,
        'amazon_ads' AS most_efficient_platform, 
        'amazon_ads' AS best_roas_platform,
        
        -- Campaign scale and diversity
        COUNT(DISTINCT campaign_id) AS total_active_campaigns,
        AVG(campaign_age_days) AS avg_campaign_maturity,
        COUNT(CASE WHEN lifecycle_stage = 'LAUNCH' THEN 1 END) AS new_campaigns,
        COUNT(CASE WHEN lifecycle_stage = 'ESTABLISHED' THEN 1 END) AS established_campaigns
        
    FROM intermediate.int_ad_reporting__unified_campaign_metrics
    WHERE date_day >= CURRENT_DATE - INTERVAL '12 months'
    GROUP BY DATE_TRUNC('month', date_day)
),

strategic_insights AS (
    -- Generate strategic insights and recommendations
    SELECT 
        reporting_month,
        
        -- Investment efficiency assessment
        CASE 
            WHEN blended_roas >= 3.0 THEN 'HIGHLY_EFFICIENT'
            WHEN blended_roas >= 2.0 THEN 'EFFICIENT' 
            WHEN blended_roas >= 1.0 THEN 'BREAK_EVEN'
            ELSE 'INEFFICIENT'
        END AS investment_efficiency_grade,
        
        -- Growth trajectory assessment
        CASE 
            WHEN LAG(total_monthly_spend) OVER (ORDER BY reporting_month) IS NOT NULL THEN
                ROUND(((total_monthly_spend - LAG(total_monthly_spend) OVER (ORDER BY reporting_month)) 
                / LAG(total_monthly_spend) OVER (ORDER BY reporting_month)) * 100, 2)
            ELSE NULL
        END AS month_over_month_growth_rate,
        
        -- Portfolio diversification score
        CASE 
            WHEN active_platforms >= 4 AND ctr_variance_across_platforms < 0.5 THEN 'WELL_DIVERSIFIED'
            WHEN active_platforms >= 3 THEN 'MODERATELY_DIVERSIFIED'
            WHEN active_platforms >= 2 THEN 'LIMITED_DIVERSIFICATION'
            ELSE 'CONCENTRATED'
        END AS portfolio_diversification,
        
        -- Market opportunity assessment
        CASE 
            WHEN new_campaigns > established_campaigns * 0.2 THEN 'EXPANDING'
            WHEN new_campaigns > 0 THEN 'STEADY_GROWTH'
            ELSE 'MAINTENANCE_MODE'
        END AS expansion_mode,
        
        -- Performance consistency
        CASE 
            WHEN ctr_variance_across_platforms < 0.3 AND cpc_variance_across_platforms < 0.5 THEN 'HIGHLY_CONSISTENT'
            WHEN ctr_variance_across_platforms < 0.5 AND cpc_variance_across_platforms < 1.0 THEN 'CONSISTENT'
            ELSE 'INCONSISTENT'
        END AS performance_consistency,
        
        total_monthly_spend,
        total_monthly_revenue,
        blended_roas,
        blended_ctr,
        blended_cpc,
        active_platforms,
        total_active_campaigns,
        best_ctr_platform,
        most_efficient_platform,
        best_roas_platform
        
    FROM unified_performance
)

-- Final executive dashboard output
SELECT 
    -- Reporting period
    si.reporting_month,
    EXTRACT(year FROM si.reporting_month) AS reporting_year,
    EXTRACT(quarter FROM si.reporting_month) AS reporting_quarter,
    
    -- High-level performance metrics
    si.total_monthly_spend AS monthly_ad_spend,
    si.total_monthly_revenue AS monthly_revenue,
    si.blended_roas AS overall_roas,
    si.blended_ctr AS overall_ctr,
    si.blended_cpc AS overall_cpc,
    
    -- Strategic assessments
    si.investment_efficiency_grade,
    si.month_over_month_growth_rate,
    si.portfolio_diversification,
    si.expansion_mode,
    si.performance_consistency,
    
    -- Platform insights
    si.active_platforms AS platforms_in_use,
    si.total_active_campaigns,
    si.best_ctr_platform AS performance_leader_ctr,
    si.most_efficient_platform AS efficiency_leader,
    si.best_roas_platform AS revenue_leader,
    
    -- Customer insights (aggregated monthly)
    ROUND(AVG(ci.avg_customer_value), 2) AS monthly_avg_customer_value,
    SUM(ci.new_customers_acquired) AS monthly_new_customers,
    ROUND(AVG(ci.avg_month_1_retention), 2) AS avg_customer_retention_rate,
    SUM(ci.high_value_customers) AS high_value_customers_acquired,
    ROUND(AVG(ci.avg_platforms_per_customer), 1) AS avg_platforms_per_customer,
    
    -- Geographic insights (aggregated monthly)
    ROUND(AVG(gp.countries_active), 0) AS avg_countries_active,
    ROUND(AVG(gp.high_opportunity_spend) / NULLIF(AVG(gp.regional_investment), 0) * 100, 1) AS high_opportunity_spend_ratio,
    ROUND(AVG(gp.mature_market_ratio) * 100, 1) AS mature_markets_percentage,
    ROUND(AVG(gp.avg_market_share_position) * 100, 1) AS avg_market_position_percentile,
    
    -- Executive KPIs by top platforms
    MAX(CASE WHEN ek.marketing_channel = si.best_roas_platform THEN ek.avg_roas END) AS top_platform_roas,
    MAX(CASE WHEN ek.marketing_channel = si.best_ctr_platform THEN ek.avg_ctr END) AS top_platform_ctr,
    MAX(CASE WHEN ek.marketing_channel = si.most_efficient_platform THEN ek.avg_cpc END) AS top_platform_cpc,
    
    -- Risk indicators
    MAX(ek.anomaly_days) AS max_platform_anomaly_days,
    ROUND(AVG(ek.ctr_volatility), 4) AS avg_performance_volatility,
    
    -- Growth trajectory indicators
    ROUND(AVG(ek.avg_mom_growth_rate), 2) AS avg_platform_growth_rate,
    SUM(ek.scaling_days) AS total_scaling_days,
    SUM(ek.optimizing_days) AS total_optimizing_days,
    
    -- Strategic recommendations
    CASE 
        WHEN si.investment_efficiency_grade = 'INEFFICIENT' AND si.performance_consistency = 'INCONSISTENT' 
        THEN 'URGENT: Platform optimization and budget reallocation required'
        WHEN si.investment_efficiency_grade = 'EFFICIENT' AND si.expansion_mode = 'MAINTENANCE_MODE'
        THEN 'OPPORTUNITY: Consider expansion into new markets or platforms'
        WHEN si.portfolio_diversification = 'CONCENTRATED' AND si.investment_efficiency_grade = 'EFFICIENT'
        THEN 'RECOMMENDATION: Diversify platform portfolio to reduce risk'
        WHEN si.month_over_month_growth_rate > 20 AND si.blended_roas > 2.0
        THEN 'SCALE: Increase investment in top-performing channels'
        ELSE 'MONITOR: Continue current strategy with minor optimizations'
    END AS executive_recommendation,
    
    -- Investment allocation insights
    CASE 
        WHEN si.best_roas_platform = si.most_efficient_platform 
        THEN CONCAT('Increase allocation to ', si.best_roas_platform, ' (leading both efficiency and returns)')
        WHEN si.blended_roas < 1.5 
        THEN 'Focus on cost optimization across all platforms'
        WHEN AVG(gp.high_opportunity_spend) > 10000
        THEN 'Prioritize geographic expansion in high-opportunity markets'
        ELSE 'Maintain current allocation with minor adjustments'
    END AS allocation_strategy,
    
    -- Customer strategy insights
    CASE 
        WHEN AVG(ci.avg_month_1_retention) < 50 
        THEN 'FOCUS: Improve customer retention programs'
        WHEN SUM(ci.high_value_customers) / NULLIF(SUM(ci.new_customers_acquired), 0) < 0.1
        THEN 'FOCUS: Optimize targeting for higher-value customers'
        WHEN AVG(ci.avg_platforms_per_customer) < 1.5
        THEN 'OPPORTUNITY: Increase cross-platform customer engagement'
        ELSE 'STRENGTH: Customer acquisition and retention performing well'
    END AS customer_strategy_insight,
    
    -- Data freshness and quality
    COUNT(DISTINCT ek.marketing_channel) AS platforms_with_data,
    MIN(si.reporting_month) AS analysis_period_start,
    MAX(si.reporting_month) AS analysis_period_end,
    CURRENT_TIMESTAMP AS dashboard_generated_at

FROM strategic_insights si
LEFT JOIN executive_kpis ek ON si.reporting_month = ek.reporting_month
LEFT JOIN customer_insights ci ON si.reporting_month = ci.cohort_month
LEFT JOIN geographic_performance gp ON si.reporting_month = gp.performance_month

WHERE si.reporting_month >= CURRENT_DATE - INTERVAL '6 months'

GROUP BY 
    si.reporting_month, si.investment_efficiency_grade, si.month_over_month_growth_rate,
    si.portfolio_diversification, si.expansion_mode, si.performance_consistency,
    si.total_monthly_spend, si.total_monthly_revenue, si.blended_roas, si.blended_ctr, si.blended_cpc,
    si.active_platforms, si.total_active_campaigns, si.best_ctr_platform, si.most_efficient_platform, si.best_roas_platform

ORDER BY si.reporting_month DESC
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 1474 | 0 | 1 | 0 | 1 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| reporting_month | 0 | 0 | 0 | DATE | DATE |
| reporting_year | 0 | 0 | 0 | BIGINT | BIGINT |
| reporting_quarter | 0 | 0 | 0 | BIGINT | BIGINT |
| monthly_ad_spend | 0 | 0 | 0 | DOUBLE | DOUBLE |
| monthly_revenue | 0 | 0 | 0 | DECIMAL(38,2) | DECIMAL(38,2) |
| overall_roas | 0 | 0 | 0 | DOUBLE | DOUBLE |
| overall_ctr | 0 | 0 | 0 | DOUBLE | DOUBLE |
| overall_cpc | 0 | 0 | 0 | DOUBLE | DOUBLE |
| investment_efficiency_grade | 0 | 0 | 0 | VARCHAR | VARCHAR |
| month_over_month_growth_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| portfolio_diversification | 0 | 0 | 0 | VARCHAR | VARCHAR |
| expansion_mode | 0 | 0 | 0 | VARCHAR | VARCHAR |
| performance_consistency | 0 | 0 | 0 | VARCHAR | VARCHAR |
| platforms_in_use | 0 | 0 | 0 | BIGINT | BIGINT |
| total_active_campaigns | 0 | 0 | 0 | BIGINT | BIGINT |
| performance_leader_ctr | 0 | 0 | 0 | VARCHAR | VARCHAR |
| efficiency_leader | 0 | 0 | 0 | VARCHAR | VARCHAR |
| revenue_leader | 0 | 0 | 0 | VARCHAR | VARCHAR |
| monthly_avg_customer_value | 0 | 0 | 0 | DOUBLE | DOUBLE |
| monthly_new_customers | 0 | 0 | 0 | HUGEINT | HUGEINT |
| avg_customer_retention_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| high_value_customers_acquired | 0 | 0 | 0 | HUGEINT | HUGEINT |
| avg_platforms_per_customer | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_countries_active | 0 | 0 | 0 | DOUBLE | DOUBLE |
| high_opportunity_spend_ratio | 0 | 0 | 0 | DOUBLE | DOUBLE |
| mature_markets_percentage | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_market_position_percentile | 0 | 0 | 0 | DOUBLE | DOUBLE |
| top_platform_roas | 0 | 0 | 0 | DOUBLE | DOUBLE |
| top_platform_ctr | 0 | 0 | 0 | DOUBLE | DOUBLE |
| top_platform_cpc | 0 | 0 | 0 | DOUBLE | DOUBLE |
| max_platform_anomaly_days | 0 | 0 | 0 | INTEGER | INTEGER |
| avg_performance_volatility | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_platform_growth_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| total_scaling_days | 0 | 0 | 0 | HUGEINT | HUGEINT |
| total_optimizing_days | 0 | 0 | 0 | HUGEINT | HUGEINT |
| executive_recommendation | 0 | 0 | 0 | VARCHAR | VARCHAR |
| allocation_strategy | 0 | 0 | 0 | VARCHAR | VARCHAR |
| customer_strategy_insight | 0 | 0 | 0 | VARCHAR | VARCHAR |
| platforms_with_data | 0 | 0 | 0 | BIGINT | BIGINT |
| analysis_period_start | 0 | 0 | 0 | DATE | DATE |
| analysis_period_end | 0 | 0 | 0 | DATE | DATE |
| dashboard_generated_at | 0 | 0 | 0 | TIMESTAMP WITH TIME ZONE | TIMESTAMP WITH TIME ZONE |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[{"reporting_month":null}]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A1_zero_rows | 行数=0 |
| B5_null_literal_output | <code>42输出列；[{"column":"reporting_month","expression":["CAST(NULL AS DATE)"]},{"column":"reporting_year","expression":["CAST(NULL AS BIGINT)"]},{"column":"reporting_quarter","expression":["CAST(NULL AS BIGINT)"]}]</code> |
| B7_specified_not_read | <code>["intermediate.int_ad_reporting__customer_journey_analysis","intermediate.int_ad_reporting__geo_channel_performance"]</code> |
| B8_shared_single_source | <code>唯一源=intermediate.int_ad_reporting__unified_campaign_metrics；目标数=2；例=["marts.ad_reporting__executive_dashboard","marts.ad_reporting__predictive_analytics"]</code> |
| C9_gold_runtime_text | <code>S5:43 CURRENT_DATE；命中数=6</code> |
| C9_contract_runtime_text | <code>S3:3413 current timestamp；命中数=1</code> |

## 轨迹索引（不放输出原文）

本题事件总数：99；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -printf '%p %s bytes\n' &#124; sort &amp;&amp; cat config/layer_dependencies.yaml</code> | 7365 | true | false |
| 23 | run | <code>cat &gt; /tmp/models.py &lt;&lt;'PY'<br>import yaml,re,os<br>c=yaml.safe_load(open('docs/data_contract.yaml'))['modeling_spec']<br># output schema<br><br>def parse_src(s):<br> x=s.split('.')[-1]<br> if x.startswith('int_'): return</code> | 0 | false | false |
| 25 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -100 /tmp/runlog</code> | 8424 | true | false |
| 29 | run | <code>python run.py &gt; /tmp/runlog2 2&gt;&amp;1; grep -E 'ERROR - ✗&#124;layer complete&#124;ERROR - Failed&#124;Binder Error&#124;Catalog Error' /tmp/runlog2</code> | 1956 | false | false |
| 31 | run | <code>cat sql/intermediate/int_ad_reporting__time_series_analytics.sql &#124; head -20; head -35 sql/marts/ad_reporting__predictive_analytics.sql; head -20 sql/staging/stg_google_ads__account_report.sql</code> | 3170 | false | false |
| 33 | run | <code>grep -n 'FROM\&#124;JOIN' sql/intermediate/int_ad_reporting__time_series_analytics.sql sql/marts/ad_reporting__predictive_analytics.sql</code> | 466 | false | false |
| 35 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>import re<br>for p in Path('sql/staging').glob('*.sql'):<br> s=p.read_text()<br> # only raw source casts rather than casts of computed values; make raw conversions tole</code> | 0 | false | false |
| 37 | run | <code>python run.py &gt; /tmp/runlog3 2&gt;&amp;1; grep -E 'ERROR - ✗&#124;layer complete' /tmp/runlog3;</code> | 6937 | true | false |
| 43 | run | <code>cat &gt; sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql &lt;&lt;'SQL'<br>WITH execution_clock AS (<br>    SELECT CURRENT_TIMESTAMP AS processed_at<br>),<br>amazon_rows AS (<br>    SELECT<br>        'amazon_ads'</code> | 0 | false | false |
| 45 | run | <code>python run.py &gt; /tmp/runlog5 2&gt;&amp;1; grep -E 'ERROR - ✗&#124;layer complete' /tmp/runlog5</code> | 843 | true | false |
| 47 | run | <code>grep -A12 -B2 'unified_campaign_metrics' /tmp/runlog5 &#124; head -25;</code> | 2253 | true | false |
| 49 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('ad_reporting.duckdb')<br>s=open('sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql').read()<br>try:c.execute('create or replace table intermedia</code> | 139 | false | false |
| 51 | run | <code>python - &lt;&lt;'PY'<br>p='sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql';s=open(p).read();s=s.replace('CASE WHEN conversions &gt; 0 THEN ROUND(cost / conversions, 2) ELSE 0 END AS cost_per_con</code> | 506 | false | false |
| 53 | run | <code>sed -n '115,145p' sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql; python run.py &gt;/tmp/runlog6 2&gt;&amp;1; grep -E 'ERROR - ✗&#124;layer complete' /tmp/runlog6</code> | 2241 | true | false |
| 55 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('ad_reporting.duckdb')<br>s=open('sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql').read()<br>for needle in ['CASE WHEN metrics.conversions &gt; 0</code> | 290 | false | false |
| 57 | run | <code>sed -n '97,118p' sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql</code> | 1596 | false | false |
| 59 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('ad_reporting.duckdb')<br>s=open('sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql').read()<br>for ix in [s.index('base AS ('),s.index('metrics </code> | 454 | false | false |
| 61 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>s=open('sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql').read(); c=duckdb.connect('ad_reporting.duckdb')<br># Build each section by CTE text manually staged</code> | 828 | false | false |
| 63 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>s=open('sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql').read();c=duckdb.connect('ad_reporting.duckdb')<br>for end in ['amazon_rows AS (','google_rows AS ('</code> | 139 | false | false |
| 65 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('ad_reporting.duckdb')<br>s=open('sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql').read()<br># replace select list final output<br>p=s.index('SEL</code> | 512 | false | false |
| 67 | run | <code>python - &lt;&lt;'PY'<br>p='sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql';s=open(p).read()<br>for old,new in [('WHEN platform = \'amazon_ads\' AND click_through_rate','WHEN base.platform = \'am</code> | 843 | true | false |
| 69 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('ad_reporting.duckdb');s=open('sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql').read();p=s.index('metrics AS (')<br>q=s[:p]+'SELECT * FROM </code> | 87 | false | false |
| 71 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,re<br>c=duckdb.connect('ad_reporting.duckdb');s=open('sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql').read()<br>for marker,final in [('metrics AS (','SELECT *</code> | 384 | false | false |
| 73 | run | <code>sed -n '96,130p' sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql;</code> | 2534 | false | false |
| 75 | run | grep -n conversions sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql | 743 | false | false |
| 77 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>s=open('sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql').read();c=duckdb.connect('ad_reporting.duckdb')<br>for key in ['amazon_rows','google_rows','facebook</code> | 1078 | false | false |
| 79 | run | <code>python - &lt;&lt;'PY'<br>p='sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql';s=open(p).read();s=s.replace("CAST(COALESCE(impressions, 0) AS BIGINT) AS impressions,\n        CAST(COALESCE(clicks</code> | 276 | false | false |
| 83 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for layer in ('intermediate_models','marts_models'):<br> for m in c['modeling_spec'][layer]: print(m['name'],len(m['columns']</code> | 1029 | true | false |

### agent action 的 thought/message 命中原句

未找到命中原句。

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-006.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/marts/ad_reporting__executive_dashboard.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/marts/ad_reporting__executive_dashboard.sql`
- S6: `records/006_contract_impl-006.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/result.md`
- S10: `data/020_packages_work/020_impl-006_ad_reporting__executive_dashboard/020_impl-006_ad_reporting__executive_dashboard.json`
- S11: `data/005_cs_work/impl-006/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/ad_reporting.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions`
