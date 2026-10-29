# impl-005 | marts | google_ads__executive_dashboard | 差异：S1；日期 原记录

## 契约完整原文

S3:1795–1953

```yaml
    - name: google_ads__executive_dashboard
      description: Executive summary of Google Ads performance with daily account KPIs, trends, portfolio composition, and prescriptive flags
      grain: One row per account_id per date_day (only days with total_spend > 0; account_id and date_day not null)
      source_models:
      - intermediate.int_google_ads__account_performance_metrics (source_relation, account_id, account_name, currency_code, date_day, account_maturity_stage, performance_score, performance_tier, spend_mom_change_pct, conversions_mom_change_pct, spend, clicks, impressions, conversions, conversions_value, ctr, cpc, cost_per_conversion, roas)
      - intermediate.int_google_ads__campaign_cohort_analysis (date_day, campaign_id, lifecycle_stage, momentum_indicator, performance_tier_in_cohort, investment_tier, underperforming_flag, spend)
      - intermediate.int_google_ads__keyword_performance_segmentation (date_day, campaign_id, keyword_id, performance_tier, bid_recommendation, efficiency_score, pause_candidate_flag)
      business_logic: '1) Start from intermediate.int_google_ads__account_performance_metrics and rename core metrics to account-level totals: total_spend=spend; total_clicks=clicks; total_impressions=impressions; total_conversions=conversions; total_conversions_value=conversions_value; overall_ctr=ctr; overall_cpc=cpc; overall_cost_per_conversion=cost_per_conversion; overall_roas=roas. Also carry: source_relation, account_id, account_name, currency_code, date_day, account_maturity_stage, performance_score, performance_tier, spend_mom_change_pct, conversions_mom_change_pct. 2) Build campaign_aggregates by date_day (global scope) from intermediate.int_google_ads__campaign_cohort_analysis: active_campaigns=count of distinct campaigns; campaigns_in_launch/growth/maturity=count of distinct campaigns in each lifecycle stage; high_momentum_campaigns=count with momentum_indicator=''High Momentum''; underperforming_campaigns=count with underperforming_flag=true; premium_investment_campaigns=count with investment_tier=''Premium Investment''; premium_investment_spend=sum of spend for ''Premium Investment''. Null campaign/category values are not counted; missing dates yield no records. 3) Build keyword_aggregates by date_day (global scope) from intermediate.int_google_ads__keyword_performance_segmentation: active_keywords=count of distinct keywords; star_performer_keywords=count with performance_tier=''Star Performer''; bid_increase_opportunities=count where bid_recommendation starts with ''Increase''; pause_candidate_keywords=count with pause_candidate_flag=true; avg_keyword_efficiency_score=average efficiency_score. Missing dates yield no records. 4) Join account-level metrics to campaign_aggregates and keyword_aggregates on date_day; replace missing aggregate counts and premium_investment_spend with 0; set avg_keyword_efficiency_score to 0 when missing. 5) Compute trends per account_id ordered by date_day: - spend_wow_growth_pct: percent change in total_spend vs the value 7 days prior; round to 2 decimals; set to null if the prior value is missing or <= 0. - conversions_wow_growth_pct: percent change in total_conversions vs the value 7 days prior; round to 2 decimals; set to null if the prior value is missing or <= 0. - spend_30d_avg: rolling average of total_spend over the current day and the 29 preceding rows for the same account; rounded in final to 2 decimals. - roas_30d_avg: rolling average of overall_roas over the current day and the 29 preceding rows for the same account; rounded in final to 4 decimals. - performance_score_30d_avg: rolling average of performance_score over the current day and the 29 preceding rows for the same account; rounded in final to 1 decimal. Window partition: by account_id; order: date_day ascending. 6) Derive classifications and flags: - premium_investment_pct: premium_investment_spend/total_spend*100; round to 2 decimals; if total_spend=0 then null (rows with 0 spend are excluded by filter). - performance_alert (first match wins): spend_wow_growth_pct > 50 → ''High Spend Growth Alert''; spend_wow_growth_pct < -30 → ''Spend Decline Alert''; conversions_wow_growth_pct > 50 → ''Conversion Growth Opportunity''; conversions_wow_growth_pct < -30 → ''Conversion Decline Alert''; overall_roas < 1.0 and total_spend > 1000 → ''ROI Optimization Needed''; underperforming_campaigns/active_campaigns > 0.3 using safe divide → ''Portfolio Health Issue''; else ''Normal Performance''. - strategic_recommendation (first match wins): star_performer_keywords/active_keywords > 0.2 and bid_increase_opportunities > 10 using safe divide → ''Scale High Performers''; pause_candidate_keywords/active_keywords > 0.2 using safe divide → ''Portfolio Optimization Needed''; high_momentum_campaigns/active_campaigns > 0.3 using safe divide → ''Invest in Growth''; avg_keyword_efficiency_score < 40 → ''Keyword Strategy Review''; premium_investment_spend/total_spend < 0.1 using safe divide → ''Consider Premium Investments''; else ''Maintain Current Strategy''. - budget_efficiency_tier: ''Highly Efficient'' if overall_roas >= 4.0; ''Efficient'' if >= 2.0; ''Break-even'' if >= 1.0; ''Underperforming'' if >= 0.5; else ''Poor Performance''. - overall_account_health_score: cap to [0,100] after combining performance_score*0.6 and avg_keyword_efficiency_score*0.4; treat missing inputs as 0. - immediate_attention_required: true if overall_roas < 1.0 and total_spend > 1000; else false. - trending_alert: true if spend_wow_growth_pct > 50 or conversions_wow_growth_pct < -30; else false. - scale_opportunity: true if star_performer_keywords/active_keywords > 0.15 using safe divide; else false. - top_performer_account: true if performance_score*0.6 + avg_keyword_efficiency_score*0.4 >= 80; else false. 7) Filter to executive-relevant rows: total_spend > 0, account_id present, date_day present. Order by account_id ascending and date_day descending.'
      columns:
      - name: source_relation
        data_type: VARCHAR
        description: Upstream relation identifier for the account metrics row
      - name: account_id
        data_type: VARCHAR
        description: Account identifier; join and window partition key for trends
        tests:
        - not_null
      - name: account_name
        data_type: VARCHAR
        description: Human-readable account name from source
      - name: currency_code
        data_type: VARCHAR
        description: Three-letter currency code associated with the account
      - name: date_day
        data_type: DATE
        description: Metric date; window order key; exactly one row per account_id per date_day post-filter
        tests:
        - not_null
      - name: total_spend
        data_type: DOUBLE
        description: Account daily spend (from source); rows with total_spend <= 0 are excluded; used as denominator for premium_investment_pct
      - name: total_clicks
        data_type: BIGINT
        description: Account daily clicks (from source) without rounding or imputation
      - name: total_impressions
        data_type: BIGINT
        description: Account daily impressions (from source) without rounding or imputation
      - name: total_conversions
        data_type: DOUBLE
        description: Account daily conversions (from source) used in WoW trend calculations
      - name: total_conversions_value
        data_type: DOUBLE
        description: Account daily conversion value/revenue (from source)
      - name: overall_ctr
        data_type: FLOAT
        description: Account click-through rate ratio (0–1) as provided by source (no re-scaling)
      - name: overall_cpc
        data_type: DOUBLE
        description: Account average cost-per-click as provided by source
      - name: overall_cost_per_conversion
        data_type: DOUBLE
        description: Account cost per conversion as provided by source
      - name: overall_roas
        data_type: DOUBLE
        description: Account return on ad spend (revenue/spend) as provided by source
      - name: spend_wow_growth_pct
        data_type: DOUBLE
        description: Percent change in total_spend vs value 7 days prior for same account; rounded to 2 decimals; NULL if prior <= 0 or missing
      - name: conversions_wow_growth_pct
        data_type: DOUBLE
        description: Percent change in total_conversions vs value 7 days prior for same account; rounded to 2 decimals; NULL if prior <= 0 or missing
      - name: spend_mom_change_pct
        data_type: DOUBLE
        description: Month-over-month spend change percentage as provided by source (no recomputation or rounding here)
      - name: conversions_mom_change_pct
        data_type: DOUBLE
        description: Month-over-month conversions change percentage as provided by source (no recomputation or rounding here)
      - name: active_campaigns
        data_type: BIGINT
        description: Global count of distinct campaigns active on date_day; COALESCE to 0 when missing
      - name: campaigns_in_launch
        data_type: BIGINT
        description: Global count of distinct campaigns with lifecycle_stage='Launch Phase' on date_day; COALESCE to 0
      - name: campaigns_in_growth
        data_type: BIGINT
        description: Global count of distinct campaigns with lifecycle_stage='Growth Phase' on date_day; COALESCE to 0
      - name: campaigns_in_maturity
        data_type: BIGINT
        description: Global count of distinct campaigns with lifecycle_stage='Maturity Phase' on date_day; COALESCE to 0
      - name: high_momentum_campaigns
        data_type: BIGINT
        description: Global count of distinct campaigns with momentum_indicator='High Momentum' on date_day; COALESCE to 0
      - name: underperforming_campaigns
        data_type: BIGINT
        description: Global count of distinct campaigns with underperforming_flag=true on date_day; COALESCE to 0
      - name: premium_investment_campaigns
        data_type: BIGINT
        description: Global count of distinct campaigns with investment_tier='Premium Investment' on date_day; COALESCE to 0
      - name: premium_investment_spend
        data_type: DOUBLE
        description: Global spend sum for campaigns with investment_tier='Premium Investment' on date_day; COALESCE to 0
      - name: premium_investment_pct
        data_type: DOUBLE
        description: Premium investment share of total_spend as a percentage (0–100), computed as premium_investment_spend/total_spend*100 and rounded to 2 decimals; NULL if total_spend=0 (rows with 0 spend are filtered out)
      - name: active_keywords
        data_type: BIGINT
        description: Global count of distinct keywords on date_day; COALESCE to 0
      - name: star_performer_keywords
        data_type: BIGINT
        description: Global count of distinct keywords with performance_tier='Star Performer' on date_day; COALESCE to 0
      - name: bid_increase_opportunities
        data_type: BIGINT
        description: Global count of distinct keywords with bid_recommendation starting with 'Increase' on date_day; COALESCE to 0
      - name: pause_candidate_keywords
        data_type: BIGINT
        description: Global count of distinct keywords with pause_candidate_flag=true on date_day; COALESCE to 0
      - name: avg_keyword_efficiency_score
        data_type: DOUBLE
        description: Global average of efficiency_score on date_day rounded to 1 decimal in final; COALESCE to 0 before rounding when missing
      - name: performance_score
        data_type: DOUBLE
        description: Account performance score from source used in health score and top_performer_account logic
      - name: performance_tier
        data_type: VARCHAR
        description: Account performance tier label from source (passed through unchanged)
      - name: account_maturity_stage
        data_type: VARCHAR
        description: Account maturity stage label from source (passed through unchanged)
      - name: spend_30d_avg
        data_type: DOUBLE
        description: Rolling average of total_spend over the last 30 rows per account_id (max 30 days), rounded to 2 decimals
      - name: roas_30d_avg
        data_type: DOUBLE
        description: Rolling average of overall_roas over the last 30 rows per account_id (max 30 days), rounded to 4 decimals
      - name: performance_score_30d_avg
        data_type: DOUBLE
        description: Rolling average of performance_score over the last 30 rows per account_id (max 30 days), rounded to 1 decimal
      - name: performance_alert
        data_type: VARCHAR
        description: 'Categorical alert derived by ordered CASE (see business logic); emits one of: High Spend Growth Alert, Spend Decline Alert, Conversion Growth Opportunity, Conversion Decline Alert, ROI Optimization Needed, Portfolio Health Issue, Normal Performance'
      - name: strategic_recommendation
        data_type: VARCHAR
        description: 'Categorical recommendation derived by ordered CASE (see business logic); emits one of: Scale High Performers, Portfolio Optimization Needed, Invest in Growth, Keyword Strategy Review, Consider Premium Investments, Maintain Current Strategy'
      - name: budget_efficiency_tier
        data_type: VARCHAR
        description: 'Budget efficiency classification: Highly Efficient, Efficient, Break-even, Underperforming, or Poor Performance'
      - name: overall_account_health_score
        data_type: DOUBLE
        description: Composite health score capped to [0,100] = performance_score*0.6 + avg_keyword_efficiency_score*0.4 with bounding via least/greatest
      - name: immediate_attention_required
        data_type: BOOLEAN
        description: True if overall_roas < 1.0 and total_spend > 1000, else false
        tests:
        - not_null
      - name: trending_alert
        data_type: BOOLEAN
        description: True if spend_wow_growth_pct > 50 or conversions_wow_growth_pct < -30, else false
        tests:
        - not_null
      - name: scale_opportunity
        data_type: BOOLEAN
        description: True if star_performer_keywords/active_keywords > 0.15 (safe-divide), else false
        tests:
        - not_null
      - name: top_performer_account
        data_type: BOOLEAN
        description: True if performance_score*0.6 + avg_keyword_efficiency_score*0.4 >= 80, else false
        tests:
        - not_null
```

## agent 最终 SQL

S4

```sql
WITH ap AS (SELECT * FROM intermediate.int_google_ads__account_performance_metrics), ca AS (
 SELECT date_day,count(distinct campaign_id) active_campaigns,count(distinct campaign_id) FILTER(WHERE lifecycle_stage='Launch Phase') campaigns_in_launch,count(distinct campaign_id) FILTER(WHERE lifecycle_stage='Growth Phase') campaigns_in_growth,count(distinct campaign_id) FILTER(WHERE lifecycle_stage='Maturity Phase') campaigns_in_maturity,count(distinct campaign_id) FILTER(WHERE momentum_indicator='High Momentum') high_momentum_campaigns,count(distinct campaign_id) FILTER(WHERE underperforming_flag) underperforming_campaigns,count(distinct campaign_id) FILTER(WHERE investment_tier='Premium Investment') premium_investment_campaigns,sum(spend) FILTER(WHERE investment_tier='Premium Investment') premium_investment_spend FROM intermediate.int_google_ads__campaign_cohort_analysis GROUP BY date_day), ka AS (
 SELECT date_day,count(distinct keyword_id) active_keywords,count(distinct keyword_id) FILTER(WHERE performance_tier='Star Performer') star_performer_keywords,count(distinct keyword_id) FILTER(WHERE starts_with(bid_recommendation,'Increase')) bid_increase_opportunities,count(distinct keyword_id) FILTER(WHERE pause_candidate_flag) pause_candidate_keywords,avg(efficiency_score) avg_keyword_efficiency_score FROM intermediate.int_google_ads__keyword_performance_segmentation GROUP BY date_day), enriched AS (
 SELECT ap.source_relation,ap.account_id,ap.account_name,ap.currency_code,ap.date_day,ap.spend total_spend,ap.clicks total_clicks,ap.impressions total_impressions,ap.conversions total_conversions,ap.conversions_value total_conversions_value,ap.ctr overall_ctr,ap.cpc overall_cpc,ap.cost_per_conversion overall_cost_per_conversion,ap.roas overall_roas,ap.spend_mom_change_pct,ap.conversions_mom_change_pct,ap.performance_score,ap.performance_tier,ap.account_maturity_stage,
 coalesce(ca.active_campaigns,0) active_campaigns,coalesce(ca.campaigns_in_launch,0) campaigns_in_launch,coalesce(ca.campaigns_in_growth,0) campaigns_in_growth,coalesce(ca.campaigns_in_maturity,0) campaigns_in_maturity,coalesce(ca.high_momentum_campaigns,0) high_momentum_campaigns,coalesce(ca.underperforming_campaigns,0) underperforming_campaigns,coalesce(ca.premium_investment_campaigns,0) premium_investment_campaigns,coalesce(ca.premium_investment_spend,0) premium_investment_spend,
 coalesce(ka.active_keywords,0) active_keywords,coalesce(ka.star_performer_keywords,0) star_performer_keywords,coalesce(ka.bid_increase_opportunities,0) bid_increase_opportunities,coalesce(ka.pause_candidate_keywords,0) pause_candidate_keywords,coalesce(ka.avg_keyword_efficiency_score,0) avg_keyword_efficiency_score
 FROM ap LEFT JOIN ca USING(date_day) LEFT JOIN ka USING(date_day)), trends AS (
 SELECT *,lag(total_spend,7) over(partition by account_id order by date_day) prior_spend,lag(total_conversions,7) over(partition by account_id order by date_day) prior_conversions,
 avg(total_spend) over(partition by account_id order by date_day rows between 29 preceding and current row) spend_30d_avg,avg(overall_roas) over(partition by account_id order by date_day rows between 29 preceding and current row) roas_30d_avg,avg(performance_score) over(partition by account_id order by date_day rows between 29 preceding and current row) performance_score_30d_avg
 FROM enriched), deltas AS (
 SELECT *,round(CASE WHEN prior_spend>0 THEN (total_spend-prior_spend)/prior_spend*100 END,2) spend_wow_growth_pct,round(CASE WHEN prior_conversions>0 THEN (total_conversions-prior_conversions)/prior_conversions*100 END,2) conversions_wow_growth_pct,
 round(100*premium_investment_spend/nullif(total_spend,0),2) premium_investment_pct,
 round(100.0*star_performer_keywords/nullif(active_keywords,0),2) star_pct,round(100.0*pause_candidate_keywords/nullif(active_keywords,0),2) pause_pct,round(100.0*high_momentum_campaigns/nullif(active_campaigns,0),2) momentum_pct,round(100.0*underperforming_campaigns/nullif(active_campaigns,0),2) under_pct
 FROM trends), scored AS (
 SELECT *,round(spend_30d_avg,2) spend_30d_avg,round(roas_30d_avg,4) roas_30d_avg,round(performance_score_30d_avg,1) performance_score_30d_avg,
 least(100.0,greatest(0.0,coalesce(performance_score,0)*.6+coalesce(avg_keyword_efficiency_score,0)*.4)) overall_account_health_score,
 CASE WHEN overall_roas>=4 THEN 'Highly Efficient' WHEN overall_roas>=2 THEN 'Efficient' WHEN overall_roas>=1 THEN 'Break-even' WHEN overall_roas>=.5 THEN 'Underperforming' ELSE 'Poor Performance' END budget_efficiency_tier
 FROM deltas), final AS (
 SELECT *,CASE WHEN spend_wow_growth_pct>50 THEN 'High Spend Growth Alert' WHEN spend_wow_growth_pct< -30 THEN 'Spend Decline Alert' WHEN conversions_wow_growth_pct>50 THEN 'Conversion Growth Opportunity' WHEN conversions_wow_growth_pct< -30 THEN 'Conversion Decline Alert' WHEN overall_roas<1 AND total_spend>1000 THEN 'ROI Optimization Needed' WHEN under_pct>30 THEN 'Portfolio Health Issue' ELSE 'Normal Performance' END performance_alert,
 CASE WHEN star_pct>20 AND bid_increase_opportunities>10 THEN 'Scale High Performers' WHEN pause_pct>20 THEN 'Portfolio Optimization Needed' WHEN momentum_pct>30 THEN 'Invest in Growth' WHEN avg_keyword_efficiency_score<40 THEN 'Keyword Strategy Review' WHEN premium_investment_pct<10 THEN 'Consider Premium Investments' ELSE 'Maintain Current Strategy' END strategic_recommendation
 FROM scored)
SELECT source_relation,account_id,account_name,currency_code,date_day,total_spend,total_clicks,total_impressions,total_conversions,total_conversions_value,overall_ctr,overall_cpc,overall_cost_per_conversion,overall_roas,spend_wow_growth_pct,conversions_wow_growth_pct,spend_mom_change_pct,conversions_mom_change_pct,
 active_campaigns,campaigns_in_launch,campaigns_in_growth,campaigns_in_maturity,high_momentum_campaigns,underperforming_campaigns,premium_investment_campaigns,premium_investment_spend,premium_investment_pct,active_keywords,star_performer_keywords,bid_increase_opportunities,pause_candidate_keywords,round(avg_keyword_efficiency_score,1) avg_keyword_efficiency_score,performance_score,performance_tier,account_maturity_stage,spend_30d_avg,roas_30d_avg,performance_score_30d_avg,performance_alert,strategic_recommendation,budget_efficiency_tier,overall_account_health_score,
 (overall_roas<1 AND total_spend>1000) immediate_attention_required,(spend_wow_growth_pct>50 OR conversions_wow_growth_pct< -30) trending_alert,(star_pct>15) scale_opportunity,(coalesce(performance_score,0)*.6+avg_keyword_efficiency_score*.4>=80) top_performer_account
FROM final WHERE total_spend>0 AND account_id IS NOT NULL AND date_day IS NOT NULL ORDER BY account_id,date_day DESC
```

## gold SQL（仅供定位差异）

S5

```sql
-- Google Ads Executive Dashboard - Simplified High-level KPIs
-- Comprehensive executive summary with performance metrics and business intelligence

with account_performance as (
    select 
        source_relation,
        account_id,
        account_name,
        currency_code,
        date_day,
        account_maturity_stage,
        performance_score,
        performance_tier,
        spend_mom_change_pct,
        conversions_mom_change_pct,
        
        -- Core metrics
        spend as total_spend,
        clicks as total_clicks,
        impressions as total_impressions,
        conversions as total_conversions,
        conversions_value as total_conversions_value,
        ctr as overall_ctr,
        cpc as overall_cpc,
        cost_per_conversion as overall_cost_per_conversion,
        roas as overall_roas
    from intermediate.int_google_ads__account_performance_metrics
),

campaign_summary as (
    select
        date_day,
        campaign_id,
        lifecycle_stage,
        momentum_indicator,
        performance_tier_in_cohort,
        investment_tier,
        underperforming_flag,
        spend
    from intermediate.int_google_ads__campaign_cohort_analysis
),

keyword_summary as (
    select 
        date_day,
        campaign_id,
        keyword_id,
        performance_tier,
        bid_recommendation,
        efficiency_score,
        pause_candidate_flag
    from intermediate.int_google_ads__keyword_performance_segmentation
),

-- Aggregate campaign metrics by date
campaign_aggregates as (
    select
        date_day,
        count(distinct campaign_id) as active_campaigns,
        count(distinct case when lifecycle_stage = 'Launch Phase' then campaign_id end) as campaigns_in_launch,
        count(distinct case when lifecycle_stage = 'Growth Phase' then campaign_id end) as campaigns_in_growth,
        count(distinct case when lifecycle_stage = 'Maturity Phase' then campaign_id end) as campaigns_in_maturity,
        count(distinct case when momentum_indicator = 'High Momentum' then campaign_id end) as high_momentum_campaigns,
        count(distinct case when underperforming_flag = true then campaign_id end) as underperforming_campaigns,
        count(distinct case when investment_tier = 'Premium Investment' then campaign_id end) as premium_investment_campaigns,
        sum(case when investment_tier = 'Premium Investment' then spend else 0 end) as premium_investment_spend,
        count(distinct case when performance_tier_in_cohort = 'Top 20%' then campaign_id end) as top_tier_campaigns
    from campaign_summary
    group by date_day
),

-- Aggregate keyword metrics by date
keyword_aggregates as (
    select
        date_day,
        count(distinct keyword_id) as active_keywords,
        count(distinct case when performance_tier = 'Star Performer' then keyword_id end) as star_performer_keywords,
        count(distinct case when bid_recommendation like 'Increase%' then keyword_id end) as bid_increase_opportunities,
        count(distinct case when pause_candidate_flag = true then keyword_id end) as pause_candidate_keywords,
        avg(efficiency_score) as avg_keyword_efficiency_score
    from keyword_summary
    group by date_day
),

-- Calculate week-over-week trends
trending_metrics as (
    select
        ap.source_relation,
        ap.account_id,
        ap.account_name,
        ap.currency_code,
        ap.date_day,
        ap.account_maturity_stage,
        ap.performance_score,
        ap.performance_tier,
        ap.spend_mom_change_pct,
        ap.conversions_mom_change_pct,
        ap.total_spend,
        ap.total_clicks,
        ap.total_impressions,
        ap.total_conversions,
        ap.total_conversions_value,
        ap.overall_ctr,
        ap.overall_cpc,
        ap.overall_cost_per_conversion,
        ap.overall_roas,

        coalesce(ca.active_campaigns, 0) as active_campaigns,
        coalesce(ca.campaigns_in_launch, 0) as campaigns_in_launch,
        coalesce(ca.campaigns_in_growth, 0) as campaigns_in_growth,
        coalesce(ca.campaigns_in_maturity, 0) as campaigns_in_maturity,
        coalesce(ca.high_momentum_campaigns, 0) as high_momentum_campaigns,
        coalesce(ca.underperforming_campaigns, 0) as underperforming_campaigns,
        coalesce(ca.premium_investment_campaigns, 0) as premium_investment_campaigns,
        coalesce(ca.premium_investment_spend, 0) as premium_investment_spend,
        coalesce(ca.top_tier_campaigns, 0) as top_tier_campaigns,

        coalesce(ka.active_keywords, 0) as active_keywords,
        coalesce(ka.star_performer_keywords, 0) as star_performer_keywords,
        coalesce(ka.bid_increase_opportunities, 0) as bid_increase_opportunities,
        coalesce(ka.pause_candidate_keywords, 0) as pause_candidate_keywords,
        coalesce(ka.avg_keyword_efficiency_score, 0) as avg_keyword_efficiency_score,

        -- Week-over-week comparisons
        lag(ap.total_spend, 7) over (partition by ap.account_id order by ap.date_day) as spend_7d_ago,
        lag(ap.total_conversions, 7) over (partition by ap.account_id order by ap.date_day) as conversions_7d_ago,

        -- Calculate WoW growth rates
        case
            when lag(ap.total_spend, 7) over (partition by ap.account_id order by ap.date_day) > 0
            then round((ap.total_spend - lag(ap.total_spend, 7) over (partition by ap.account_id order by ap.date_day)) /
                      lag(ap.total_spend, 7) over (partition by ap.account_id order by ap.date_day) * 100, 2)
            else null
        end as spend_wow_growth_pct,

        case
            when lag(ap.total_conversions, 7) over (partition by ap.account_id order by ap.date_day) > 0
            then round((ap.total_conversions - lag(ap.total_conversions, 7) over (partition by ap.account_id order by ap.date_day)) /
                      lag(ap.total_conversions, 7) over (partition by ap.account_id order by ap.date_day) * 100, 2)
            else null
        end as conversions_wow_growth_pct,

        -- Rolling 30-day averages
        avg(ap.total_spend) over (
            partition by ap.account_id
            order by ap.date_day
            rows between 29 preceding and current row
        ) as spend_30d_avg,

        avg(ap.overall_roas) over (
            partition by ap.account_id
            order by ap.date_day
            rows between 29 preceding and current row
        ) as roas_30d_avg,

        avg(ap.performance_score) over (
            partition by ap.account_id
            order by ap.date_day
            rows between 29 preceding and current row
        ) as performance_score_30d_avg

    from account_performance ap
    left join campaign_aggregates ca on ap.date_day = ca.date_day
    left join keyword_aggregates ka on ap.date_day = ka.date_day
),

-- Business intelligence insights
final as (
    select
        source_relation,
        account_id,
        account_name,
        currency_code,
        date_day,
        
        -- Core business metrics
        total_spend,
        total_clicks,
        total_impressions,
        total_conversions,
        total_conversions_value,
        
        -- Efficiency KPIs
        overall_ctr,
        overall_cpc,
        overall_cost_per_conversion,
        overall_roas,
        
        -- Growth metrics
        spend_wow_growth_pct,
        conversions_wow_growth_pct,
        spend_mom_change_pct,
        conversions_mom_change_pct,
        
        -- Portfolio composition
        active_campaigns,
        campaigns_in_launch,
        campaigns_in_growth,
        campaigns_in_maturity,
        high_momentum_campaigns,
        underperforming_campaigns,
        
        -- Investment allocation
        premium_investment_campaigns,
        premium_investment_spend,
        round(premium_investment_spend::float / nullif(total_spend, 0) * 100, 2) as premium_investment_pct,
        
        -- Keyword intelligence
        active_keywords,
        star_performer_keywords,
        bid_increase_opportunities,
        pause_candidate_keywords,
        round(avg_keyword_efficiency_score, 1) as avg_keyword_efficiency_score,
        
        -- Performance benchmarks
        performance_score,
        performance_tier,
        account_maturity_stage,
        round(spend_30d_avg, 2) as spend_30d_avg,
        round(roas_30d_avg, 4) as roas_30d_avg,
        round(performance_score_30d_avg, 1) as performance_score_30d_avg,
        
        -- Business intelligence alerts
        case 
            when spend_wow_growth_pct > 50 then 'High Spend Growth Alert'
            when spend_wow_growth_pct < -30 then 'Spend Decline Alert'
            when conversions_wow_growth_pct > 50 then 'Conversion Growth Opportunity'
            when conversions_wow_growth_pct < -30 then 'Conversion Decline Alert'
            when overall_roas < 1.0 and total_spend > 1000 then 'ROI Optimization Needed'
            when underperforming_campaigns::float / nullif(active_campaigns, 0) > 0.3 then 'Portfolio Health Issue'
            else 'Normal Performance'
        end as performance_alert,
        
        -- Strategic recommendations
        case 
            when star_performer_keywords::float / nullif(active_keywords, 0) > 0.2 
                 and bid_increase_opportunities > 10 then 'Scale High Performers'
            when pause_candidate_keywords::float / nullif(active_keywords, 0) > 0.2 then 'Portfolio Optimization Needed'
            when high_momentum_campaigns::float / nullif(active_campaigns, 0) > 0.3 then 'Invest in Growth'
            when avg_keyword_efficiency_score < 40 then 'Keyword Strategy Review'
            when premium_investment_spend::float / nullif(total_spend, 0) < 0.1 then 'Consider Premium Investments'
            else 'Maintain Current Strategy'
        end as strategic_recommendation,
        
        -- Budget efficiency classification
        case 
            when overall_roas >= 4.0 then 'Highly Efficient'
            when overall_roas >= 2.0 then 'Efficient'
            when overall_roas >= 1.0 then 'Break-even'
            when overall_roas >= 0.5 then 'Underperforming'
            else 'Poor Performance'
        end as budget_efficiency_tier,
        
        -- Overall account health score (0-100)
        least(100, greatest(0,
            coalesce(performance_score * 0.6, 0) +
            coalesce(avg_keyword_efficiency_score * 0.4, 0)
        )) as overall_account_health_score,
        
        -- Executive summary flags
        case when overall_roas < 1.0 and total_spend > 1000 then true else false end as immediate_attention_required,
        case when spend_wow_growth_pct > 50 or conversions_wow_growth_pct < -30 then true else false end as trending_alert,
        case when star_performer_keywords::float / nullif(active_keywords, 0) > 0.15 then true else false end as scale_opportunity,
        case when (performance_score * 0.6 + avg_keyword_efficiency_score * 0.4) >= 80 then true else false end as top_performer_account
        
    from trending_metrics
)

select *
from final
where 
    -- Executive focus constraints
    total_spend > 0  -- Only include days with activity
    and date_day is not null
    and account_id is not null
order by account_id, date_day desc
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 10000 | 10000 | 0 | 0 | 317 | 317 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"account_id":"acc12253649392","currency_code":"null","date_day":"2023-02-12"}</code> |
| K2 | <code>{"account_id":"acc12253649392","currency_code":"null","date_day":"2023-05-04"}</code> |
| K3 | <code>{"account_id":"acc12253649392","currency_code":"null","date_day":"2023-05-16"}</code> |
| K4 | <code>{"account_id":"acc02369342072","currency_code":"null","date_day":"2021-01-31"}</code> |
| K5 | <code>{"account_id":"acc02369342072","currency_code":"null","date_day":"2021-03-03"}</code> |
| K6 | <code>{"account_id":"acc02369342072","currency_code":"null","date_day":"2021-03-18"}</code> |
| K7 | <code>{"account_id":"acc02369342072","currency_code":"null","date_day":"2021-05-10"}</code> |
| K8 | <code>{"account_id":"acc03152339046","currency_code":"null","date_day":"2022-03-29"}</code> |
| K9 | <code>{"account_id":"acc09426864345","currency_code":"null","date_day":"2021-05-04"}</code> |
| K10 | <code>{"account_id":"acc33518709772","currency_code":"null","date_day":"2021-11-30"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| currency_code | 0 | 0 | 0 | VARCHAR | VARCHAR |
| date_day | 0 | 0 | 0 | DATE | DATE |
| total_spend | 0 | 0 | 0 | DOUBLE | DOUBLE |
| total_clicks | 0 | 0 | 0 | BIGINT | BIGINT |
| total_impressions | 0 | 0 | 0 | BIGINT | BIGINT |
| total_conversions | 0 | 0 | 0 | DOUBLE | DOUBLE |
| total_conversions_value | 0 | 0 | 0 | DOUBLE | DOUBLE |
| overall_ctr | 0 | 0 | 0 | FLOAT | FLOAT |
| overall_cpc | 0 | 0 | 0 | DOUBLE | DOUBLE |
| overall_cost_per_conversion | 0 | 0 | 0 | DOUBLE | DOUBLE |
| overall_roas | 0 | 0 | 0 | DOUBLE | DOUBLE |
| spend_wow_growth_pct | 70 | 70 | 70 | DOUBLE | DOUBLE |
| conversions_wow_growth_pct | 66 | 66 | 66 | DOUBLE | DOUBLE |
| spend_mom_change_pct | 0 | 0 | 0 | DOUBLE | DOUBLE |
| conversions_mom_change_pct | 0 | 0 | 0 | DOUBLE | DOUBLE |
| active_campaigns | 0 | 0 | 0 | BIGINT | BIGINT |
| campaigns_in_launch | 0 | 0 | 0 | BIGINT | BIGINT |
| campaigns_in_growth | 0 | 0 | 0 | BIGINT | BIGINT |
| campaigns_in_maturity | 0 | 0 | 0 | BIGINT | BIGINT |
| high_momentum_campaigns | 0 | 0 | 0 | BIGINT | BIGINT |
| underperforming_campaigns | 0 | 0 | 0 | BIGINT | BIGINT |
| premium_investment_campaigns | 0 | 0 | 0 | BIGINT | BIGINT |
| premium_investment_spend | 0 | 0 | 0 | DOUBLE | DOUBLE |
| premium_investment_pct | 0 | 0 | 0 | DOUBLE | DOUBLE |
| active_keywords | 0 | 0 | 0 | BIGINT | BIGINT |
| star_performer_keywords | 0 | 0 | 0 | BIGINT | BIGINT |
| bid_increase_opportunities | 0 | 0 | 0 | BIGINT | BIGINT |
| pause_candidate_keywords | 0 | 0 | 0 | BIGINT | BIGINT |
| performance_score | 0 | 0 | 0 | DOUBLE | DOUBLE |
| performance_tier | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_maturity_stage | 0 | 0 | 0 | VARCHAR | VARCHAR |
| spend_30d_avg | 10000 | 10000 | 10000 | DOUBLE | DOUBLE |
| roas_30d_avg | 9612 | 9612 | 9612 | DOUBLE | DOUBLE |
| performance_score_30d_avg | 9980 | 9980 | 9980 | DOUBLE | DOUBLE |
| strategic_recommendation | 0 | 0 | 0 | VARCHAR | VARCHAR |
| budget_efficiency_tier | 0 | 0 | 0 | VARCHAR | VARCHAR |
| overall_account_health_score | 0 | 0 | 0 | DOUBLE | DOUBLE |
| immediate_attention_required | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| trending_alert | 726 | 726 | 726 | BOOLEAN | BOOLEAN |
| scale_opportunity | 16 | 16 | 16 | BOOLEAN | BOOLEAN |
| top_performer_account | 0 | 0 | 0 | BOOLEAN | BOOLEAN |

spend_wow_growth_pct 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"-49.49","rows":1},{"value":"1650.13","rows":1}]</code> | <code>[{"value":"483.37","rows":1},{"value":"51.53","rows":1}]</code> |
| K2 | <code>[{"value":"-97.09","rows":1},{"value":"135.48","rows":1}]</code> | <code>[{"value":"-66.4","rows":1},{"value":"135.48","rows":1}]</code> |
| K3 | 211.14 | -73.06 |
重复键为同键值/次数，列表位置不是唯一配对。

conversions_wow_growth_pct 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"-40.0","rows":1},{"value":"700.0","rows":1}]</code> | <code>[{"value":"0.0","rows":1},{"value":"380.0","rows":1}]</code> |
| K2 | <code>[{"value":"-95.83","rows":1},{"value":"188.89","rows":1}]</code> | <code>[{"value":"-66.67","rows":1},{"value":"188.89","rows":1}]</code> |
| K3 | 366.67 | -41.67 |
重复键为同键值/次数，列表位置不是唯一配对。

spend_30d_avg 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K4 | 24.166845 | 24.17 |
| K5 | 75.5915595 | 75.59 |
| K6 | 61.471875000000004 | 61.47 |

roas_30d_avg 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K5 | 3.4662500000000005 | 3.4663 |
| K6 | 4.2306333333333335 | 4.2306 |
| K7 | 5.002825 | 5.0028 |

performance_score_30d_avg 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K4 | 44.012998413085946 | 44.0 |
| K5 | 67.52749900817872 | 67.5 |
| K6 | 78.35166600545249 | 78.4 |

trending_alert 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K4 | null | false |
| K5 | null | false |
| K6 | null | false |

scale_opportunity 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K8 | null | false |
| K9 | null | false |
| K10 | null | false |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

| 约束 | 列 | 违反计数 |
|---|---|---|
| not_null | trending_alert | <code>{"sql_null_rows":707}</code> |
| not_null | scale_opportunity | <code>{"sql_null_rows":16}</code> |

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>6列；[{"column":"source_relation","value":"google_ads"},{"column":"premium_investment_campaigns","value":"0"},{"column":"premium_investment_spend","value":"0.0"}]</code> |
| A4_equal_columns | <code>2组；[{"columns":["premium_investment_campaigns","pause_candidate_keywords"],"nonnull_equal_rows":10000,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["premium_investment_spend","premium_investment_pct"],"nonnull_equal_rows":10000,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>2组；[{"columns":["premium_investment_campaigns","pause_candidate_keywords"],"nonnull_equal_rows":10000,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["premium_investment_spend","premium_investment_pct"],"nonnull_equal_rows":10000,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| B7_specified_not_read | <code>["intermediate.int_google_ads__account_performance_metrics (source_relation, account_id, account_name, currency_code, date_day, account_maturity_stage, performance_score, performance_tier, spend_mom_change_pct, conversions_mom_change_pct, spend, clicks, impressions, conversions, conversions_value, ctr, cpc, cost_per_conversion, roas)","intermediate.int_google_ads__campaign_cohort_analysis (date_day, campaign_id, lifecycle_stage, momentum_indicator, performance_tier_in_cohort, investment_tier, underperforming_flag, spend)","intermediate.int_google_ads__keyword_performance_segmentation (date_day, campaign_id, keyword_id, performance_tier, bid_recommendation, efficiency_score, pause_candidate_flag)"]</code> |

## 轨迹索引（不放输出原文）

本题事件总数：49；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions/6bb241f2-c289-42-6f7dba956740748/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; find sql -type f -maxdepth 3 -print -exec wc -l {} \;</code> | 2838 | true | false |
| 17 | run | <code>cat &gt; sql/intermediate/int_google_ads__account_performance_metrics.sql &lt;&lt;'SQL'<br>WITH daily_stats AS (<br>    SELECT * FROM staging.stg_google_ads__account_stats<br>),<br>rolling_metrics AS (<br>    SELECT<br>        </code> | 0 | false | false |
| 19 | run | <code>cat &gt; sql/intermediate/int_google_ads__campaign_cohort_analysis.sql &lt;&lt;'SQL'<br>WITH history AS (<br>    SELECT * FROM staging.stg_google_ads__campaign_history WHERE is_most_recent_record<br>),<br>stats AS (<br>    S</code> | 0 | false | false |
| 23 | run | <code>cat &gt;&gt; /tmp/marts.py &lt;&lt;'PY'<br>write('google_ads__channel_performance_analysis',"""WITH cp AS (SELECT * FROM intermediate.int_google_ads__campaign_cohort_analysis), ast AS (SELECT * FROM staging.stg_goog</code> | 0 | false | false |
| 25 | run | <code>sed -i "s/and ad_network_type in ('SEARCH','DISPLAY','MIXED','YOUTUBE') or ad_network_type is null/and (ad_network_type in ('SEARCH','DISPLAY','MIXED','YOUTUBE') or ad_network_type is null)/" sql/stag</code> | 8152 | true | false |
| 31 | run | <code>python run.py &gt; /tmp/run2.log 2&gt;&amp;1; grep -E 'ERROR&#124;Layer complete&#124;rows$' /tmp/run2.log &#124; tail -60</code> | 2499 | true | false |
| 37 | run | <code>python - &lt;&lt;'PY'<br>import duckdb, pathlib<br>c=duckdb.connect('google_ads.duckdb',read_only=True)<br>for schema in ('staging','intermediate','marts'):<br> for (t,) in c.execute(f"select table_name from informatio</code> | 2322 | true | false |

### agent action 的 thought/message 命中原句

event 23 / message

```text
write('google_ads__executive_dashboard',"""WITH ap AS (SELECT * FROM intermediate.int_google_ads__account_performance_metrics), ca AS (
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-005.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-005/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/marts/google_ads__executive_dashboard.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-005/sql/marts/google_ads__executive_dashboard.sql`
- S6: `records/006_contract_impl-005.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/result.md`
- S10: `data/019_packages_work/019_impl-005_google_ads__executive_dashboard/019_impl-005_google_ads__executive_dashboard.json`
- S11: `data/005_cs_work/impl-005/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-005/google_ads.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions`
