# impl-006 | intermediate | int_ad_reporting__unified_campaign_metrics | 差异：S1；日期 2025-10-12

## 契约完整原文

S3:2627–2717

```yaml
    - name: int_ad_reporting__unified_campaign_metrics
      description: Unified daily campaign metrics across platforms with standardized KPIs, performance tiers, rolling 365‑day filter, and data quality screening
      grain: One row per platform, campaign_id, date_day
      source_models:
      - staging.stg_amazon_ads__campaign_report
      - staging.stg_google_ads__campaign_report
      - staging.stg_facebook_ads__ad_report
      - raw.linkedin_ad_analytics_by_campaign_data
      business_logic: 'Combine four platform feeds into a standardized base and apply filters per source: - Amazon Ads (staging.stg_amazon_ads__campaign_report): - Map fields: platform=''amazon_ads''; campaign_type from campaign_bidding_strategy; daily_budget from campaign_budget_amount; currency from campaign_budget_currency_code; cost from source; revenue_7d from sales_7_d; revenue_30d from sales_30_d; conversions from purchases_30_d; conversion_type=''PRODUCT_SALES''; CTR, CPC, ROAS from source; source_updated_at from _dbt_loaded_at. - Keep rows where clicks, impressions, and cost are all non‑negative. - Google Ads (staging.stg_google_ads__campaign_report): - Map fields: platform=''google_ads''; campaign_type from ad_network_type with default ''SEARCH''; daily_budget NULL; currency=''USD''; cost from spend; revenue_7d and revenue_30d both from conversions_value; conversions from conversions; conversion_type=''ONLINE_CONVERSION''. - KPIs: CTR as percentage (clicks ÷ impressions), rounded to 4 decimals and set to 0 when impressions=0; CPC as cost ÷ clicks, rounded to 2 decimals and set to 0 when clicks=0; ROAS as revenue_7d ÷ cost when both are positive, else 0. - Set source_updated_at to the execution timestamp; keep rows where clicks, impressions, and spend are all non‑negative. - Facebook Ads (staging.stg_facebook_ads__ad_report): - Map fields: platform=''facebook_ads''; campaign_id from ad_id; campaign_type=''FACEBOOK_FEED''; daily_budget NULL; currency=''USD''; clicks from inline_link_clicks defaulting to 0; impressions defaulting to 0; cost from spend defaulting to 0; revenue_7d=0; revenue_30d=0; conversions=0; conversion_type=''ENGAGEMENT''. - KPIs: CTR as percentage (clicks ÷ impressions), rounded to 4 decimals and set to 0 when impressions=0; CPC as cost ÷ clicks, rounded to 2 decimals and set to 0 when clicks=0; ROAS=0. - Set source_updated_at to the execution timestamp; keep rows where spend and impressions are non‑negative. - LinkedIn Ads (raw.linkedin_ad_analytics_by_campaign_data): - Map fields: platform=''linkedin_ads''; date_day from day; campaign_type=''LINKEDIN_SPONSORED''; daily_budget NULL; currency=''USD''; clicks defaulting to 0; impressions cast to integer and defaulting to 0; cost cast to decimal and defaulting to 0; revenue_7d=0; revenue_30d=0; conversions from conversion_value_in_local_currency cast to integer and defaulting to 0; conversion_type=''LEAD_GENERATION''. - KPIs: CTR as percentage (clicks ÷ impressions), rounded to 4 decimals and set to 0 when impressions=0; CPC as cost ÷ clicks, rounded to 2 decimals and set to 0 unless both clicks and cost are positive; ROAS=0. - Set source_updated_at to the execution timestamp; keep rows where cost_in_usd is non‑negative. Enhance with performance metrics (computed on the full base before final filters): - ctr_performance_tier: platform‑specific thresholds on CTR (percent): - amazon_ads: HIGH when ≥0.5; MEDIUM when ≥0.2; else LOW. - google_ads: HIGH when ≥2.0; MEDIUM when ≥0.8; else LOW. - facebook_ads: HIGH when ≥1.5; MEDIUM when ≥0.9; else LOW. - others: HIGH when ≥1.0; MEDIUM when ≥0.5; else LOW. - cost_efficiency_tier: VERY_EFFICIENT when CPC≤0.5; EFFICIENT when ≤1.5; MODERATE when ≤3.0; EXPENSIVE when ≤5.0; else VERY_EXPENSIVE. - roas_performance_tier: for amazon_ads and google_ads, classify ROAS as EXCELLENT when ≥4.0; GOOD when ≥2.0; BREAK_EVEN when ≥1.0; LOSS_MAKING when >0; else NO_REVENUE; other platforms NOT_APPLICABLE. - campaign_age_days: days since the earliest observed date_day for the platform and campaign_id in the full base (not limited to the 365‑day window). - volume_tier: HIGH_VOLUME when impressions≥10,000; MEDIUM_VOLUME when ≥1,000; LOW_VOLUME when ≥100; else MINIMAL_VOLUME. Final selection and additional computations: - cost_per_mille (CPM): cost per 1,000 impressions, rounded to 2 decimals; set to 0 when impressions=0. - cost_per_conversion: cost ÷ conversions, rounded to 2 decimals; set to 0 when conversions=0. - lifecycle_stage from campaign_age_days: LAUNCH when ≤7; OPTIMIZATION when ≤30; MATURE when ≤90; else ESTABLISHED. - has_data_quality_issues: TRUE when clicks>impressions or cost<0 or CTR>100 or CPC>50; otherwise FALSE. - processed_at set to the execution timestamp. Apply final filters: - Keep rows where date_day is within the last 365 days relative to execution. - Keep rows where impressions>0. - Exclude rows flagged with has_data_quality_issues (output rows have has_data_quality_issues=FALSE). Notes: - Inputs are combined without deduplication; no ordering is enforced. - Rounding: CTR to 4 decimals (for computed platforms), CPC to 2 decimals, CPM to 2 decimals, cost_per_conversion to 2 decimals. - Units: CTR is a percentage; CPC/CPM/cost_per_conversion and cost are in the stated currency (USD for Google/Facebook/LinkedIn; Amazon uses its source currency); ROAS is a ratio. - CURRENT_DATE and CURRENT_TIMESTAMP are evaluated at query execution time.'
      columns:
      - name: platform
        data_type: VARCHAR
        description: 'Ad platform identifier: ''amazon_ads'', ''google_ads'', ''facebook_ads'', or ''linkedin_ads'''
      - name: campaign_id
        data_type: VARCHAR
        description: Source campaign identifier (Facebook uses ad_id as campaign_id)
      - name: date_day
        data_type: DATE
        description: Metric date; only rows within the rolling last 365 days relative to execution are kept
      - name: campaign_type
        data_type: VARCHAR
        description: Platform-specific campaign type (Amazon=bidding strategy, Google=ad_network_type default 'SEARCH', Facebook='FACEBOOK_FEED', LinkedIn='LINKEDIN_SPONSORED')
      - name: daily_budget
        data_type: DECIMAL(18,2)
        description: Daily budget amount (Amazon only from campaign_budget_amount; NULL for other platforms; currency given by currency column)
      - name: currency
        data_type: VARCHAR
        description: ISO currency code for monetary fields (USD for Google/Facebook/LinkedIn; Amazon from campaign_budget_currency_code)
      - name: conversion_type
        data_type: VARCHAR
        description: 'Conversion attribution type by platform: ''PRODUCT_SALES'', ''ONLINE_CONVERSION'', ''ENGAGEMENT'', or ''LEAD_GENERATION'''
      - name: impressions
        data_type: BIGINT
        description: Number of impressions (non-negative in base; cast to integer on LinkedIn); final output enforces impressions>0
      - name: clicks
        data_type: BIGINT
        description: Number of clicks (defaults to 0 where applicable); must be ≤ impressions in final output due to data quality filtering
      - name: cost
        data_type: DOUBLE
        description: Spend amount (Amazon in source currency; Google/Facebook/LinkedIn in USD); non-negative in base and non-negative in final output
      - name: revenue_7d
        data_type: DECIMAL(18,2)
        description: 7-day revenue proxy (Amazon=sales_7_d, Google=conversions_value, others=0)
      - name: revenue_30d
        data_type: DECIMAL(18,2)
        description: 30-day revenue proxy (Amazon=sales_30_d, Google=conversions_value, others=0)
      - name: conversions
        data_type: DECIMAL(12,2)
        description: Conversion count/value (Amazon=purchases_30_d, Google=conversions, Facebook=0, LinkedIn from conversion_value_in_local_currency as integer)
      - name: click_through_rate
        data_type: DOUBLE
        description: CTR as a percentage in [0,100] (Amazon from source; others as clicks ÷ impressions expressed as percent, rounded to 4 decimals; rows with CTR>100 are excluded)
      - name: cost_per_click
        data_type: DOUBLE
        description: CPC (Amazon from source; others as cost ÷ clicks rounded to 2 decimals with 0 when clicks≤0); rows with CPC>50 are excluded
      - name: return_on_ad_spend
        data_type: DOUBLE
        description: ROAS ratio (Amazon from source; Google as revenue_7d ÷ cost with 0 when inputs are not positive; others=0)
      - name: cost_per_mille
        data_type: DOUBLE
        description: CPM as cost per 1,000 impressions rounded to 2 decimals; denominator is always >0 due to final filter
      - name: cost_per_conversion
        data_type: DOUBLE
        description: Cost per conversion as cost ÷ conversions rounded to 2 decimals when conversions>0 else 0
      - name: ctr_performance_tier
        data_type: VARCHAR
        description: CTR performance classification by platform (HIGH, MEDIUM, LOW) using platform-specific percent thresholds
      - name: cost_efficiency_tier
        data_type: VARCHAR
        description: 'CPC-based cost efficiency classification: VERY_EFFICIENT, EFFICIENT, MODERATE, EXPENSIVE, VERY_EXPENSIVE'
      - name: roas_performance_tier
        data_type: VARCHAR
        description: ROAS-based classification for Amazon/Google (EXCELLENT, GOOD, BREAK_EVEN, LOSS_MAKING, NO_REVENUE) else NOT_APPLICABLE
      - name: volume_tier
        data_type: VARCHAR
        description: 'Impression volume classification: HIGH_VOLUME (≥10,000), MEDIUM_VOLUME (≥1,000), LOW_VOLUME (≥100), else MINIMAL_VOLUME'
      - name: campaign_age_days
        data_type: BIGINT
        description: Days since the earliest observed date_day for the platform+campaign_id in the base (pre 365‑day filter)
      - name: lifecycle_stage
        data_type: VARCHAR
        description: 'Stage by campaign_age_days: LAUNCH (≤7), OPTIMIZATION (≤30), MATURE (≤90), else ESTABLISHED'
      - name: has_data_quality_issues
        data_type: BOOLEAN
        description: TRUE if clicks>impressions or cost<0 or CTR>100 or CPC>50; final output only contains FALSE due to filtering
      - name: source_updated_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Source freshness timestamp (Amazon=_dbt_loaded_at; Google/Facebook/LinkedIn set to the execution timestamp)
      - name: processed_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Model processing timestamp set to the execution timestamp
```

## agent 最终 SQL

S4

```sql
WITH execution_clock AS (
    SELECT CURRENT_TIMESTAMP AS processed_at
),
amazon_rows AS (
    SELECT
        'amazon_ads'::VARCHAR AS platform,
        CAST(campaign_id AS VARCHAR) AS campaign_id,
        date_day,
        CAST(campaign_bidding_strategy AS VARCHAR) AS campaign_type,
        CAST(campaign_budget_amount AS DECIMAL(18,2)) AS daily_budget,
        campaign_budget_currency_code AS currency,
        'PRODUCT_SALES'::VARCHAR AS conversion_type,
        CAST(impressions AS BIGINT) AS impressions,
        CAST(clicks AS BIGINT) AS clicks,
        CAST(cost AS DOUBLE) AS cost,
        CAST(sales_7_d AS DECIMAL(18,2)) AS revenue_7d,
        CAST(sales_30_d AS DECIMAL(18,2)) AS revenue_30d,
        CAST(purchases_30_d AS DECIMAL(12,2)) AS conversions,
        CAST(click_through_rate AS DOUBLE) AS click_through_rate,
        CAST(cost_per_click AS DOUBLE) AS cost_per_click,
        CAST(return_on_ad_spend AS DOUBLE) AS return_on_ad_spend,
        _dbt_loaded_at AS source_updated_at
    FROM staging.stg_amazon_ads__campaign_report
    WHERE COALESCE(clicks, 0) >= 0 AND COALESCE(impressions, 0) >= 0 AND COALESCE(cost, 0) >= 0
),
google_rows AS (
    SELECT
        'google_ads'::VARCHAR AS platform,
        CAST(campaign_id AS VARCHAR) AS campaign_id,
        date_day,
        COALESCE(CAST(ad_network_type AS VARCHAR), 'SEARCH') AS campaign_type,
        NULL::DECIMAL(18,2) AS daily_budget,
        'USD'::VARCHAR AS currency,
        'ONLINE_CONVERSION'::VARCHAR AS conversion_type,
        CAST(COALESCE(impressions, 0) AS BIGINT) AS impressions,
        CAST(COALESCE(clicks, 0) AS BIGINT) AS clicks,
        CAST(COALESCE(spend, 0) AS DOUBLE) AS cost,
        CAST(conversions_value AS DECIMAL(18,2)) AS revenue_7d,
        CAST(conversions_value AS DECIMAL(18,2)) AS revenue_30d,
        CAST(conversions AS DECIMAL(12,2)) AS conversions,
        CASE WHEN COALESCE(impressions, 0) > 0 THEN ROUND(COALESCE(clicks, 0)::DOUBLE / impressions * 100, 4) ELSE 0 END AS click_through_rate,
        CASE WHEN COALESCE(clicks, 0) > 0 THEN ROUND(COALESCE(spend, 0) / clicks, 2) ELSE 0 END AS cost_per_click,
        CASE WHEN COALESCE(spend, 0) > 0 AND COALESCE(conversions_value, 0) > 0 THEN ROUND(conversions_value / spend, 4) ELSE 0 END AS return_on_ad_spend,
        CURRENT_TIMESTAMP AS source_updated_at
    FROM staging.stg_google_ads__campaign_report
    WHERE COALESCE(clicks, 0) >= 0 AND COALESCE(impressions, 0) >= 0 AND COALESCE(spend, 0) >= 0
),
facebook_rows AS (
    SELECT
        'facebook_ads'::VARCHAR AS platform,
        CAST(ad_id AS VARCHAR) AS campaign_id,
        date_day,
        'FACEBOOK_FEED'::VARCHAR AS campaign_type,
        NULL::DECIMAL(18,2) AS daily_budget,
        'USD'::VARCHAR AS currency,
        'ENGAGEMENT'::VARCHAR AS conversion_type,
        CAST(COALESCE(impressions, 0) AS BIGINT) AS impressions,
        CAST(COALESCE(inline_link_clicks, 0) AS BIGINT) AS clicks,
        CAST(COALESCE(spend, 0) AS DOUBLE) AS cost,
        0::DECIMAL(18,2) AS revenue_7d,
        0::DECIMAL(18,2) AS revenue_30d,
        0::DECIMAL(12,2) AS conversions,
        CASE WHEN COALESCE(impressions, 0) > 0 THEN ROUND(COALESCE(inline_link_clicks, 0)::DOUBLE / impressions * 100, 4) ELSE 0 END AS click_through_rate,
        CASE WHEN COALESCE(inline_link_clicks, 0) > 0 THEN ROUND(COALESCE(spend, 0) / inline_link_clicks, 2) ELSE 0 END AS cost_per_click,
        0::DOUBLE AS return_on_ad_spend,
        CURRENT_TIMESTAMP AS source_updated_at
    FROM staging.stg_facebook_ads__ad_report
    WHERE COALESCE(spend, 0) >= 0 AND COALESCE(impressions, 0) >= 0
),
linkedin_rows AS (
    SELECT
        'linkedin_ads'::VARCHAR AS platform,
        CAST(campaign_id AS VARCHAR) AS campaign_id,
        TRY_CAST(day AS DATE) AS date_day,
        'LINKEDIN_SPONSORED'::VARCHAR AS campaign_type,
        NULL::DECIMAL(18,2) AS daily_budget,
        'USD'::VARCHAR AS currency,
        'LEAD_GENERATION'::VARCHAR AS conversion_type,
        CAST(COALESCE(TRY_CAST(impressions AS BIGINT), 0) AS BIGINT) AS impressions,
        CAST(COALESCE(TRY_CAST(clicks AS BIGINT), 0) AS BIGINT) AS clicks,
        CAST(COALESCE(TRY_CAST(cost_in_usd AS DOUBLE), 0) AS DOUBLE) AS cost,
        0::DECIMAL(18,2) AS revenue_7d,
        0::DECIMAL(18,2) AS revenue_30d,
        CAST(COALESCE(TRY_CAST(conversion_value_in_local_currency AS INTEGER), 0) AS DECIMAL(12,2)) AS conversions,
        CASE WHEN COALESCE(TRY_CAST(impressions AS BIGINT), 0) > 0 THEN ROUND(COALESCE(TRY_CAST(clicks AS BIGINT), 0)::DOUBLE / TRY_CAST(impressions AS BIGINT) * 100, 4) ELSE 0 END AS click_through_rate,
        CASE WHEN COALESCE(TRY_CAST(clicks AS BIGINT), 0) > 0 AND COALESCE(TRY_CAST(cost_in_usd AS DOUBLE), 0) > 0 THEN ROUND(TRY_CAST(cost_in_usd AS DOUBLE) / TRY_CAST(clicks AS BIGINT), 2) ELSE 0 END AS cost_per_click,
        0::DOUBLE AS return_on_ad_spend,
        CURRENT_TIMESTAMP AS source_updated_at
    FROM raw.linkedin_ad_analytics_by_campaign_data
    WHERE COALESCE(TRY_CAST(cost_in_usd AS DOUBLE), 0) >= 0
),
base AS (
    SELECT * FROM amazon_rows
    UNION ALL SELECT * FROM google_rows
    UNION ALL SELECT * FROM facebook_rows
    UNION ALL SELECT * FROM linkedin_rows
),
metrics AS (
    SELECT
        base.*,
        CASE
            WHEN base.platform = 'amazon_ads' AND base.click_through_rate >= 0.5 THEN 'HIGH'
            WHEN base.platform = 'amazon_ads' AND base.click_through_rate >= 0.2 THEN 'MEDIUM'
            WHEN base.platform = 'google_ads' AND base.click_through_rate >= 2.0 THEN 'HIGH'
            WHEN base.platform = 'google_ads' AND base.click_through_rate >= 0.8 THEN 'MEDIUM'
            WHEN base.platform = 'facebook_ads' AND base.click_through_rate >= 1.5 THEN 'HIGH'
            WHEN base.platform = 'facebook_ads' AND base.click_through_rate >= 0.9 THEN 'MEDIUM'
            WHEN base.click_through_rate >= 1.0 THEN 'HIGH'
            WHEN base.click_through_rate >= 0.5 THEN 'MEDIUM'
            ELSE 'LOW'
        END AS ctr_performance_tier,
        CASE WHEN base.cost_per_click <= 0.5 THEN 'VERY_EFFICIENT' WHEN cost_per_click <= 1.5 THEN 'EFFICIENT' WHEN cost_per_click <= 3.0 THEN 'MODERATE' WHEN cost_per_click <= 5.0 THEN 'EXPENSIVE' ELSE 'VERY_EXPENSIVE' END AS cost_efficiency_tier,
        CASE WHEN base.platform NOT IN ('amazon_ads','google_ads') THEN 'NOT_APPLICABLE' WHEN base.return_on_ad_spend >= 4 THEN 'EXCELLENT' WHEN base.return_on_ad_spend >= 2 THEN 'GOOD' WHEN base.return_on_ad_spend >= 1 THEN 'BREAK_EVEN' WHEN base.return_on_ad_spend > 0 THEN 'LOSS_MAKING' ELSE 'NO_REVENUE' END AS roas_performance_tier,
        CASE WHEN base.impressions >= 10000 THEN 'HIGH_VOLUME' WHEN impressions >= 1000 THEN 'MEDIUM_VOLUME' WHEN impressions >= 100 THEN 'LOW_VOLUME' ELSE 'MINIMAL_VOLUME' END AS volume_tier,
        MIN(date_day) OVER (PARTITION BY base.platform, base.campaign_id) AS first_campaign_date
    FROM base
),
classified AS (
    SELECT
        metrics.*,
        DATE_DIFF('day', first_campaign_date, date_day)::BIGINT AS campaign_age_days,
        CASE WHEN metrics.impressions > 0 THEN ROUND(metrics.cost / metrics.impressions * 1000, 2) ELSE 0 END AS cost_per_mille,
        CASE WHEN metrics.conversions > 0 THEN ROUND(metrics.cost / metrics.conversions, 2) ELSE 0 END AS cost_per_conversion,
        clicks > impressions OR cost < 0 OR click_through_rate > 100 OR cost_per_click > 50 AS has_data_quality_issues
    FROM metrics
)
SELECT
    platform, campaign_id, date_day, campaign_type, daily_budget, currency, conversion_type,
    impressions, clicks, cost, revenue_7d, revenue_30d, conversions,
    click_through_rate, cost_per_click, return_on_ad_spend, cost_per_mille, cost_per_conversion,
    ctr_performance_tier, cost_efficiency_tier, roas_performance_tier, volume_tier, campaign_age_days,
    CASE WHEN campaign_age_days <= 7 THEN 'LAUNCH' WHEN campaign_age_days <= 30 THEN 'OPTIMIZATION' WHEN campaign_age_days <= 90 THEN 'MATURE' ELSE 'ESTABLISHED' END AS lifecycle_stage,
    has_data_quality_issues, source_updated_at, processed_at
FROM classified CROSS JOIN execution_clock
WHERE date_day >= CURRENT_DATE - INTERVAL '365 days'
  AND impressions > 0
  AND NOT has_data_quality_issues
```

## gold SQL（仅供定位差异）

S5

```sql
-- Unified Campaign Metrics Model (Simplified)
-- Combines all advertising platforms into a single comprehensive view
-- Implements business logic, data quality rules, and advanced calculations

WITH base_campaigns AS (
    -- Amazon Ads Campaigns
    SELECT 
        'amazon_ads' AS platform,
        campaign_id,
        date_day,
        campaign_bidding_strategy AS campaign_type,
        campaign_budget_amount AS daily_budget,
        campaign_budget_currency_code AS currency,
        clicks,
        impressions,
        cost,
        sales_7_d AS revenue_7d,
        sales_30_d AS revenue_30d,
        purchases_30_d AS conversions,
        'PRODUCT_SALES' AS conversion_type,
        click_through_rate,
        cost_per_click,
        return_on_ad_spend,
        _dbt_loaded_at AS source_updated_at
    FROM staging.stg_amazon_ads__campaign_report
    WHERE clicks >= 0 AND impressions >= 0 AND cost >= 0
    
    UNION ALL
    
    -- Google Ads Campaigns
    SELECT
        'google_ads' AS platform,
        campaign_id,
        date_day,
        COALESCE(ad_network_type, 'SEARCH') AS campaign_type,
        NULL AS daily_budget,
        'USD' AS currency,
        clicks,
        impressions,
        spend AS cost,
        conversions_value AS revenue_7d,
        conversions_value AS revenue_30d,
        conversions,
        'ONLINE_CONVERSION' AS conversion_type,
        CASE
            WHEN impressions > 0 THEN ROUND((clicks::DECIMAL / impressions::DECIMAL) * 100, 4)
            ELSE 0
        END AS click_through_rate,
        CASE
            WHEN clicks > 0 THEN ROUND(spend / clicks, 2)
            ELSE 0
        END AS cost_per_click,
        CASE
            WHEN spend > 0 AND conversions_value > 0
            THEN conversions_value / spend
            ELSE 0
        END AS return_on_ad_spend,
        CURRENT_TIMESTAMP AS source_updated_at
    FROM staging.stg_google_ads__campaign_report
    WHERE clicks >= 0 AND impressions >= 0 AND spend >= 0
    
    UNION ALL
    
    -- Facebook Ads Campaigns (Basic Ad Data)
    SELECT
        'facebook_ads' AS platform,
        ad_id AS campaign_id,
        date_day,
        'FACEBOOK_FEED' AS campaign_type,
        NULL AS daily_budget,
        'USD' AS currency,
        COALESCE(inline_link_clicks, 0) AS clicks,
        COALESCE(impressions, 0) AS impressions,
        COALESCE(spend, 0) AS cost,
        0 AS revenue_7d,
        0 AS revenue_30d,
        0 AS conversions,
        'ENGAGEMENT' AS conversion_type,
        CASE
            WHEN impressions > 0 THEN ROUND((inline_link_clicks::DECIMAL / impressions::DECIMAL) * 100, 4)
            ELSE 0
        END AS click_through_rate,
        CASE
            WHEN inline_link_clicks > 0 THEN ROUND(spend / inline_link_clicks, 2)
            ELSE 0
        END AS cost_per_click,
        0 AS return_on_ad_spend,
        CURRENT_TIMESTAMP AS source_updated_at
    FROM staging.stg_facebook_ads__ad_report
    WHERE spend >= 0 AND impressions >= 0
    
    UNION ALL
    
    -- LinkedIn Campaigns
    SELECT 
        'linkedin_ads' AS platform,
        campaign_id,
        CAST(day AS DATE) AS date_day,
        'LINKEDIN_SPONSORED' AS campaign_type,
        NULL AS daily_budget,
        'USD' AS currency,
        COALESCE(clicks, 0) AS clicks,
        COALESCE(TRY_CAST(impressions AS INTEGER), 0) AS impressions,
        COALESCE(TRY_CAST(cost_in_usd AS DECIMAL), 0) AS cost,
        0 AS revenue_7d,
        0 AS revenue_30d,
        COALESCE(TRY_CAST(conversion_value_in_local_currency AS INTEGER), 0) AS conversions,
        'LEAD_GENERATION' AS conversion_type,
        CASE 
            WHEN TRY_CAST(impressions AS INTEGER) > 0 
            THEN ROUND((clicks::DECIMAL / TRY_CAST(impressions AS INTEGER)::DECIMAL) * 100, 4)
            ELSE 0 
        END AS click_through_rate,
        CASE 
            WHEN clicks > 0 AND TRY_CAST(cost_in_usd AS DECIMAL) > 0
            THEN ROUND(TRY_CAST(cost_in_usd AS DECIMAL) / clicks, 2)
            ELSE 0 
        END AS cost_per_click,
        0 AS return_on_ad_spend,
        CURRENT_TIMESTAMP AS source_updated_at
    FROM raw.linkedin_ad_analytics_by_campaign_data
    WHERE TRY_CAST(cost_in_usd AS DECIMAL) >= 0
),

-- Performance Metrics with Advanced Calculations
performance_metrics AS (
    SELECT 
        *,
        -- Platform-specific performance thresholds
        CASE platform
            WHEN 'amazon_ads' THEN
                CASE 
                    WHEN click_through_rate >= 0.5 THEN 'HIGH'
                    WHEN click_through_rate >= 0.2 THEN 'MEDIUM' 
                    ELSE 'LOW'
                END
            WHEN 'google_ads' THEN
                CASE 
                    WHEN click_through_rate >= 2.0 THEN 'HIGH'
                    WHEN click_through_rate >= 0.8 THEN 'MEDIUM'
                    ELSE 'LOW'
                END
            WHEN 'facebook_ads' THEN
                CASE 
                    WHEN click_through_rate >= 1.5 THEN 'HIGH'
                    WHEN click_through_rate >= 0.9 THEN 'MEDIUM'
                    ELSE 'LOW'
                END
            ELSE
                CASE 
                    WHEN click_through_rate >= 1.0 THEN 'HIGH'
                    WHEN click_through_rate >= 0.5 THEN 'MEDIUM'
                    ELSE 'LOW'
                END
        END AS ctr_performance_tier,
        
        -- Cost efficiency classification
        CASE 
            WHEN cost_per_click <= 0.5 THEN 'VERY_EFFICIENT'
            WHEN cost_per_click <= 1.5 THEN 'EFFICIENT'
            WHEN cost_per_click <= 3.0 THEN 'MODERATE'
            WHEN cost_per_click <= 5.0 THEN 'EXPENSIVE'
            ELSE 'VERY_EXPENSIVE'
        END AS cost_efficiency_tier,
        
        -- Revenue performance (for platforms with revenue data)
        CASE 
            WHEN platform IN ('amazon_ads', 'google_ads') THEN
                CASE 
                    WHEN return_on_ad_spend >= 4.0 THEN 'EXCELLENT'
                    WHEN return_on_ad_spend >= 2.0 THEN 'GOOD'
                    WHEN return_on_ad_spend >= 1.0 THEN 'BREAK_EVEN'
                    WHEN return_on_ad_spend > 0 THEN 'LOSS_MAKING'
                    ELSE 'NO_REVENUE'
                END
            ELSE 'NOT_APPLICABLE'
        END AS roas_performance_tier,
        
        -- Campaign maturity (days since first activity)
        DATEDIFF('day', MIN(date_day) OVER (PARTITION BY platform, campaign_id), date_day) AS campaign_age_days,
        
        -- Volume classification
        CASE 
            WHEN impressions >= 10000 THEN 'HIGH_VOLUME'
            WHEN impressions >= 1000 THEN 'MEDIUM_VOLUME'
            WHEN impressions >= 100 THEN 'LOW_VOLUME'
            ELSE 'MINIMAL_VOLUME'
        END AS volume_tier
        
    FROM base_campaigns
)

SELECT 
    -- Primary identifiers
    platform,
    campaign_id,
    date_day,
    
    -- Campaign attributes
    campaign_type,
    daily_budget,
    currency,
    conversion_type,
    
    -- Core metrics
    impressions,
    clicks,
    cost,
    revenue_7d,
    revenue_30d,
    conversions,
    
    -- Calculated KPIs
    click_through_rate,
    cost_per_click,
    return_on_ad_spend,
    
    CASE 
        WHEN impressions > 0 THEN ROUND((cost / impressions) * 1000, 2)
        ELSE 0 
    END AS cost_per_mille,
    
    CASE 
        WHEN conversions > 0 THEN ROUND(cost / conversions, 2)
        ELSE 0 
    END AS cost_per_conversion,
    
    -- Performance classifications
    ctr_performance_tier,
    cost_efficiency_tier,
    roas_performance_tier,
    volume_tier,
    
    -- Time-based metrics
    campaign_age_days,
    CASE 
        WHEN campaign_age_days <= 7 THEN 'LAUNCH'
        WHEN campaign_age_days <= 30 THEN 'OPTIMIZATION'
        WHEN campaign_age_days <= 90 THEN 'MATURE'
        ELSE 'ESTABLISHED'
    END AS lifecycle_stage,
    
    -- Data quality flags
    CASE 
        WHEN clicks > impressions THEN TRUE
        WHEN cost < 0 THEN TRUE
        WHEN click_through_rate > 100 THEN TRUE
        WHEN cost_per_click > 50 THEN TRUE
        ELSE FALSE
    END AS has_data_quality_issues,
    
    -- Attribution and metadata
    source_updated_at,
    CURRENT_TIMESTAMP AS processed_at

FROM performance_metrics
WHERE date_day >= CURRENT_DATE - INTERVAL '365 days'
  AND impressions > 0
  AND NOT has_data_quality_issues
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 1474 | 1474 | 0 | 0 | 94 | 94 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"campaign_id":"goo18622995762","date_day":"2024-10-20"}</code> |
| K2 | <code>{"campaign_id":"goo10172822045","date_day":"2024-10-22"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| campaign_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| date_day | 0 | 0 | 0 | DATE | DATE |
| campaign_age_days | 0 | 0 | 0 | BIGINT | BIGINT |
| campaign_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| click_through_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| clicks | 0 | 0 | 0 | BIGINT | BIGINT |
| conversion_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| conversions | 0 | 0 | 0 | DECIMAL(12,2) | DECIMAL(12,2) |
| cost | 0 | 0 | 0 | DOUBLE | DOUBLE |
| cost_efficiency_tier | 0 | 0 | 0 | VARCHAR | VARCHAR |
| cost_per_click | 0 | 0 | 0 | DOUBLE | DOUBLE |
| cost_per_conversion | 0 | 0 | 0 | DOUBLE | DOUBLE |
| cost_per_mille | 0 | 0 | 0 | DOUBLE | DOUBLE |
| ctr_performance_tier | 6 | 6 | 6 | VARCHAR | VARCHAR |
| currency | 0 | 0 | 0 | VARCHAR | VARCHAR |
| daily_budget | 0 | 0 | 0 | DECIMAL(18,2) | DECIMAL(18,2) |
| has_data_quality_issues | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| impressions | 0 | 0 | 0 | BIGINT | BIGINT |
| lifecycle_stage | 0 | 0 | 0 | VARCHAR | VARCHAR |
| platform | 0 | 0 | 0 | VARCHAR | VARCHAR |
| return_on_ad_spend | 433 | 433 | 433 | DOUBLE | DOUBLE |
| revenue_30d | 0 | 0 | 0 | DECIMAL(18,2) | DECIMAL(18,2) |
| revenue_7d | 0 | 0 | 0 | DECIMAL(18,2) | DECIMAL(18,2) |
| roas_performance_tier | 0 | 0 | 0 | VARCHAR | VARCHAR |
| volume_tier | 0 | 0 | 0 | VARCHAR | VARCHAR |

ctr_performance_tier 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | MEDIUM | LOW |

return_on_ad_spend 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | <code>[{"value":"0.0125","rows":1},{"value":"0.7513","rows":1}]</code> | <code>[{"value":"0.012508767827916763","rows":1},{"value":"0.7512938872569591","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A1_zero_rows | 行数=0 |
| B5_null_literal_output | <code>1输出列；[{"column":"daily_budget","expression":["CAST(campaign_budget_amount AS DECIMAL(18, 2))"]}]</code> |
| B6_constant_literal_output | <code>8输出列；[{"column":"platform","expression":["CAST('amazon_ads' AS TEXT)"]}]</code> |
| C9_agent_runtime_text | <code>S4:2 CURRENT_TIMESTAMP；命中数=5</code> |
| C9_gold_runtime_text | <code>S5:58 CURRENT_TIMESTAMP；命中数=5</code> |
| C9_contract_runtime_text | <code>S3:2635 CURRENT_DATE；命中数=2</code> |
| D10_keyword_in_any_result_field | <code>命中数=3；assistant_trajectory  NULL::INTEGER AS interaction_event_types, _dbt_loaded_at FROM intermediate.int_ad_reporting__unified_campaign_metrics...</code> |

## 轨迹索引（不放输出原文）

本题事件总数：99；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions/acf22d09-caa1-49-dbca994e29b4624/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -printf '%p %s bytes\n' &#124; sort &amp;&amp; cat config/layer_dependencies.yaml</code> | 7365 | true | false |
| 11 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('ad_reporting_start.duckdb',read_only=True)<br>print(c.execute('show all tables').fetchall()[:100])<br>PY</code> | 52227 | false | false |
| 15 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>x=yaml.safe_load(open('ad_reporting_start.yaml'))<br>print(type(x), x.keys())<br>print(str(x)[:2500])<br>PY</code> | 7232 | false | false |
| 17 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('ad_reporting_start.duckdb',read_only=True)<br>for r in c.execute("select table_name from information_schema.tables where table_schema='raw' order by 1").fe</code> | 26086 | false | false |
| 19 | run | <code>mkdir -p sql/{staging,intermediate,marts} &amp;&amp; cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>import yaml,duckdb,os,re<br>contract=yaml.safe_load(open('docs/data_contract.yaml'))<br>con=duckdb.connect('ad_reporting_start.duckdb',r</code> | 528 | false | false |
| 21 | run | <code>python - &lt;&lt;'PY'<br>p='/tmp/gen.py'<br>s=open(p).read();s=s.replace("if suffix.startswith('amazon_ads__'): return source['amazon_ads'+suffix[len('amazon_ads'):]]", "if suffix.startswith('amazon_ads__'): retu</code> | 0 | false | false |
| 23 | run | <code>cat &gt; /tmp/models.py &lt;&lt;'PY'<br>import yaml,re,os<br>c=yaml.safe_load(open('docs/data_contract.yaml'))['modeling_spec']<br># output schema<br><br>def parse_src(s):<br> x=s.split('.')[-1]<br> if x.startswith('int_'): return</code> | 0 | false | false |
| 25 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -100 /tmp/runlog</code> | 8424 | true | false |
| 29 | run | <code>python run.py &gt; /tmp/runlog2 2&gt;&amp;1; grep -E 'ERROR - ✗&#124;layer complete&#124;ERROR - Failed&#124;Binder Error&#124;Catalog Error' /tmp/runlog2</code> | 1956 | true | false |
| 31 | run | <code>cat sql/intermediate/int_ad_reporting__time_series_analytics.sql &#124; head -20; head -35 sql/marts/ad_reporting__predictive_analytics.sql; head -20 sql/staging/stg_google_ads__account_report.sql</code> | 3170 | true | false |
| 33 | run | <code>grep -n 'FROM\&#124;JOIN' sql/intermediate/int_ad_reporting__time_series_analytics.sql sql/marts/ad_reporting__predictive_analytics.sql</code> | 466 | true | false |
| 35 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>import re<br>for p in Path('sql/staging').glob('*.sql'):<br> s=p.read_text()<br> # only raw source casts rather than casts of computed values; make raw conversions tole</code> | 0 | false | false |
| 37 | run | <code>python run.py &gt; /tmp/runlog3 2&gt;&amp;1; grep -E 'ERROR - ✗&#124;layer complete' /tmp/runlog3;</code> | 6937 | true | false |
| 39 | run | head -20 sql/staging/stg_amazon_ads__campaign_report.sql | 1415 | false | false |
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
| 81 | run | <code>find sql -type f &#124; wc -l; grep -R ';' sql --include='*.sql' &#124; head; git status --short 2&gt;/dev/null &#124;&#124; true; python - &lt;&lt;'PY'<br>import yaml,os<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for t in c[</code> | 999 | false | false |
| 83 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>for layer in ('intermediate_models','marts_models'):<br> for m in c['modeling_spec'][layer]: print(m['name'],len(m['columns']</code> | 1029 | true | false |
| 85 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb<br>c=yaml.safe_load(open('docs/data_contract.yaml')); d=duckdb.connect('ad_reporting.duckdb',read_only=True)<br>for layer,key in [('staging','staging_contract'),('intermed</code> | 776 | false | false |

### agent action 的 thought/message 命中原句

event 23 / message

```text
  return """SELECT platform, ad_id, date_day, account_id, campaign_id, ad_group_id, NULL::INTEGER AS ad_network_type, NULL::INTEGER AS device, impressions, clicks, 0::INTEGER AS interactions, cost::DECIMAL(18,2) AS cost, conversions, 0.0::DECIMAL(2,1) AS conversions_value, 0::INTEGER AS view_through_conversions, NULL::INTEGER AS active_view_impressions, NULL::INTEGER AS active_view_measurable_impressions, NULL::INTEGER AS active_view_measurable_cost, NULL::INTEGER AS active_view_measurability, NULL::INTEGER AS active_view_viewability, NULL::INTEGER AS attributed_sales_14_d, NULL::INTEGER AS attributed_sales_30_d, NULL::INTEGER AS attributed_conversions_14_d, NULL::INTEGER AS attributed_conversions_30_d, installs, taps, click_through_rate, cost_per_click, cost_per_thousand_impressions, cost_per_conversion, 0.0::DECIMAL(2,1) AS return_on_ad_spend, NULL::INTEGER AS interaction_event_types, _dbt_loaded_at FROM intermediate.int_ad_reporting__unified_campaign_metrics WHERE FALSE"""
```
event 35 / message

```text
 s=re.sub(r'FROM (intermediate\.int_ad_reporting__unified_campaign_metrics) \([^\)]*\)',r'FROM \1',s)
```
event 43 / message

```text
Running command: cat > sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql <<'SQL'
```
event 49 / message

```text
s=open('sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql').read()
```
event 51 / message

```text
p='sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql';s=open(p).read();s=s.replace('CASE WHEN conversions > 0 THEN ROUND(cost / conversions, 2) ELSE 0 END AS cost_per_conversion','CASE WHEN metrics.conversions > 0 THEN ROUND(metrics.cost / metrics.conversions, 2) ELSE 0 END AS cost_per_conversion').replace('SELECT\n        *,\n        DATE_DIFF', 'SELECT\n        metrics.*,\n        DATE_DIFF').replace('FROM metrics\n),\nSELECT','FROM metrics\n),\nSELECT')
```
event 51 / message

```text
grep -n 'classified\|SELECT\|conversions >' sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql | tail -20
```
event 53 / message

```text
Running command: sed -n '115,145p' sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql; python run.py >/tmp/runlog6 2>&1; grep -E 'ERROR - ✗|layer complete' /tmp/runlog6
```
event 55 / message

```text
s=open('sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql').read()
```
event 57 / message

```text
Running command: sed -n '97,118p' sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql
```
event 59 / message

```text
s=open('sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql').read()
```
event 61 / message

```text
s=open('sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql').read(); c=duckdb.connect('ad_reporting.duckdb')
```
event 63 / message

```text
s=open('sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql').read();c=duckdb.connect('ad_reporting.duckdb')
```
event 65 / message

```text
s=open('sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql').read()
```
event 67 / message

```text
p='sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql';s=open(p).read()
```
event 69 / message

```text
c=duckdb.connect('ad_reporting.duckdb');s=open('sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql').read();p=s.index('metrics AS (')
```
event 71 / message

```text
c=duckdb.connect('ad_reporting.duckdb');s=open('sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql').read()
```
event 73 / message

```text
Running command: sed -n '96,130p' sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql;
```
event 75 / message

```text
Running command: grep -n conversions sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql
```
event 77 / message

```text
s=open('sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql').read();c=duckdb.connect('ad_reporting.duckdb')
```
event 79 / message

```text
p='sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql';s=open(p).read();s=s.replace("CAST(COALESCE(impressions, 0) AS BIGINT) AS impressions,\n        CAST(COALESCE(clicks, 0) AS BIGINT) AS clicks,\n        CAST(COALESCE(cost, 0) AS DOUBLE) AS cost,\n        0::DECIMAL(18,2) AS revenue_7d,\n        0::DECIMAL(18,2) AS revenue_30d,\n        CAST(COALESCE(conversions, 0) AS DECIMAL(12,2)) AS conversions,", "CAST(COALESCE(TRY_CAST(impressions AS BIGINT), 0) AS BIGINT) AS impressions,\n        CAST(COALESCE(TRY_CAST(clicks AS BIGINT), 0) AS BIGINT) AS clicks,\n        CAST(COALESCE(TRY_CAST(cost_in_usd AS DOUBLE), 0) AS DOUBLE) AS cost,\n        0::DECIMAL(18,2) AS revenue_7d,\n        0::DECIMAL(18,2) AS revenue_30d,\n        CAST(COALESCE(TRY_CAST(conversion_value_in_local_currency AS INTEGER), 0) AS DECIMAL(12,2)) AS conversions,")
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/011_table_alignment.jsonl`
- S2: `records/011_alignment_impl-006.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-006/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/sql/intermediate/int_ad_reporting__unified_campaign_metrics.sql`
- S6: `records/006_contract_impl-006.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/dacomp-de-impl-006/result.md`
- S10: `data/020_packages_work/020_impl-006_int_ad_reporting__unified_campaign_metrics/020_impl-006_int_ad_reporting__unified_campaign_metrics.json`
- S11: `data/011_agent_alignment/impl-006_attempt_01/int_ad_reporting__unified_campaign_metrics_2025-10-12.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-006/ad_reporting.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-006/agent/.events/sessions`
