# impl-005 | marts | google_ads__customer_acquisition_analysis | 差异：S1；日期 原记录

## 契约完整原文

S3:1643–1794

```yaml
    - name: google_ads__customer_acquisition_analysis
      description: Customer acquisition analysis by account and date with matched campaign context, cohort-based CAC/LTV, running totals, cohort benchmarks, segmentation, recommendations, and alert flags
      grain: One row per source_relation, account_id, date_day, and matched campaign cohort row (joined on source_relation, account_id=campaign_id, and date_day); if no match, one row with NULL campaign fields
      source_models:
      - intermediate.int_google_ads__account_performance_metrics (source_relation, account_id, account_name, date_day, account_maturity_stage, spend, clicks, impressions, conversions, conversions_value, ctr, cpc, cost_per_conversion, roas)
      - intermediate.int_google_ads__campaign_cohort_analysis (source_relation, campaign_id, date_day, advertising_channel_type, advertising_channel_subtype, lifecycle_stage)
      business_logic: '- Begin with account_performance (ap); left join campaign_cohorts (cc) on source_relation, account_id=campaign_id, and date_day. - Keep only ap rows where conversions > 0 or spend > 0. - Acquisition cohort: for each account_id, find the earliest date_day with conversions > 0 and use the first day of that month; set to NULL if the account has no conversions. - Days since first conversion: calendar days between the account’s first conversion date and the current date_day; NULL if no first conversion date. - Channel and lifecycle: take advertising_channel_type, advertising_channel_subtype, and lifecycle_stage (as campaign_lifecycle_stage) from cc; these may be NULL. - Running totals within each account_id ordered by date_day from earliest to current: - cumulative_acquisition_cost: running sum of spend. - cumulative_conversions: running sum of conversions. - cumulative_ltv: running sum of conversions_value. - If multiple rows share the same date_day, accumulation follows the row order. - Daily portfolio counts per account_id and date_day (based on joined cc rows; NULLs ignored): - active_campaigns_count: distinct campaign_id count. - channel_diversity_count: distinct advertising_channel_type count. - Derived economics per row: - customer_acquisition_cost (CAC): cumulative_acquisition_cost divided by cumulative_conversions, rounded to 2 decimals when cumulative_conversions > 0; otherwise NULL. - average_customer_ltv: cumulative_ltv divided by cumulative_conversions, rounded to 2 decimals when cumulative_conversions > 0; otherwise 0. - ltv_cac_ratio: average_customer_ltv divided by customer_acquisition_cost, rounded to 2 decimals when cumulative_acquisition_cost > 0 and cumulative_conversions > 0; otherwise 0. - estimated_payback_days: cost_per_conversion divided by average conversion value on the row (conversions_value divided by conversions), scaled to 30 days and rounded to a whole number when cost_per_conversion > 0 and conversions_value > 0; otherwise NULL. - Cohort benchmarks: - cohort_avg_cac: average of (cumulative_acquisition_cost / cumulative_conversions) across rows sharing acquisition_cohort and advertising_channel_type; rows with cumulative_conversions <= 0 are excluded; not rounded. - cohort_avg_ltv: average of (cumulative_ltv / cumulative_conversions) across the same cohort/channel; rows with cumulative_conversions <= 0 are excluded; not rounded. - Percentile ranks within acquisition_cohort: - cac_efficiency_percentile: percentile (0–1) based on customer_acquisition_cost with lower values ranked higher. - ltv_cac_performance_percentile: percentile (0–1) based on ltv_cac_ratio with higher values ranked higher. - Segmentation and insights: - acquisition_efficiency_tier by ltv_cac_ratio: ≥3.0 Excellent; ≥2.0 Good; ≥1.0 Break-even; ≥0.5 Negative; else Poor. - cac_performance_tier by cac_efficiency_percentile: ≥0.8 Top CAC Efficiency; ≥0.6 Above Average CAC; ≥0.4 Average CAC; ≥0.2 Below Average CAC; else High CAC. - customer_maturity_stage from days_since_first_conversion: Not Acquired (NULL), ≤30 New Customer, ≤90 Early Stage, ≤365 Developing Customer, ≤1095 Mature Customer, else Long-term Customer. - acquisition_sophistication_score: clamp to [0,100] of (channel_diversity_count*15 + active_campaigns_count*5 + up to 30 from average_customer_ltv, and up to 25 from ltv_cac_ratio); rounded to 1 decimal in the final output. - cac_vs_cohort_pct: ((customer_acquisition_cost − cohort_avg_cac) / cohort_avg_cac) * 100 rounded to 2 decimals when cohort_avg_cac > 0; otherwise NULL. - ltv_vs_cohort_pct: ((average_customer_ltv − cohort_avg_ltv) / cohort_avg_ltv) * 100 rounded to 2 decimals when cohort_avg_ltv > 0; otherwise NULL. - strategic_customer_segment selected by ordered rules using ltv_cac_ratio, average_customer_ltv, days_since_first_conversion, and CAC vs cohort comparisons. - acquisition_recommendation selected by ordered rules using ltv_cac_ratio, cac_efficiency_percentile, channel_diversity_count, days_since_first_conversion, CAC vs cohort, and active_campaigns_count. - Alerts in the final projection: - negative_roi_alert: true when ltv_cac_ratio < 0.5 and cumulative_acquisition_cost > 1000; else false. - high_cac_alert: true when customer_acquisition_cost > 2× cohort_avg_cac; else false. - scale_opportunity: true when ltv_cac_ratio ≥ 4.0 and cac_efficiency_percentile ≥ 0.9; else false. - retention_risk: true when days_since_first_conversion > 365 and ltv_cac_ratio < 1.5; else false. - Final filter: keep rows where cumulative_conversions > 0 or spend > 0, and date_day and account_id are not NULL; ordered by account_id ascending and date_day descending.'
      columns:
      - name: source_relation
        data_type: VARCHAR
        description: Upstream source identifier from account performance and join key to campaign cohorts
      - name: account_id
        data_type: VARCHAR
        description: Ads account identifier from account performance; non-null in the final result
        tests:
        - not_null
      - name: account_name
        data_type: VARCHAR
        description: Ads account name from account performance
      - name: date_day
        data_type: DATE
        description: Metric date used for joining and for ordering running totals; non-null in the final result
        tests:
        - not_null
      - name: acquisition_cohort
        data_type: DATE
        description: Month start of the account’s first conversion date; NULL if the account has never converted
      - name: days_since_first_conversion
        data_type: BIGINT
        description: Calendar days from the account’s first conversion date to the current date_day; NULL if no first conversion date
      - name: advertising_channel_type
        data_type: VARCHAR
        description: Channel type from the matched campaign cohort row; may be NULL
      - name: advertising_channel_subtype
        data_type: VARCHAR
        description: Channel subtype from the matched campaign cohort row; may be NULL
      - name: account_maturity_stage
        data_type: VARCHAR
        description: Account maturity stage from account performance
      - name: customer_maturity_stage
        data_type: VARCHAR
        description: Customer stage derived from days_since_first_conversion
      - name: campaign_lifecycle_stage
        data_type: VARCHAR
        description: Lifecycle stage from the matched campaign cohort row; may be NULL
      - name: spend
        data_type: DOUBLE
        description: Daily spend from account performance; rows exist only when spend > 0 or conversions > 0
      - name: clicks
        data_type: BIGINT
        description: Daily clicks from account performance
      - name: impressions
        data_type: BIGINT
        description: Daily impressions from account performance
      - name: conversions
        data_type: DOUBLE
        description: Daily conversions from account performance; used in running totals and payback calculation
      - name: conversions_value
        data_type: DOUBLE
        description: Daily conversion value from account performance; used in running LTV and payback calculation
      - name: ctr
        data_type: FLOAT
        description: Click-through rate from account performance
      - name: cpc
        data_type: DOUBLE
        description: Cost per click from account performance
      - name: cost_per_conversion
        data_type: DOUBLE
        description: Cost per conversion from account performance; used in payback calculation
      - name: roas
        data_type: DOUBLE
        description: Return on ad spend from account performance
      - name: customer_acquisition_cost
        data_type: DOUBLE
        description: 'Running CAC: cumulative_acquisition_cost divided by cumulative_conversions, rounded to 2 decimals when cumulative_conversions > 0; otherwise NULL'
      - name: average_customer_ltv
        data_type: DOUBLE
        description: 'Running average conversion value: cumulative_ltv divided by cumulative_conversions, rounded to 2 decimals when cumulative_conversions > 0; otherwise 0'
      - name: ltv_cac_ratio
        data_type: DOUBLE
        description: Ratio of average_customer_ltv to customer_acquisition_cost, rounded to 2 decimals when both are defined; otherwise 0
      - name: estimated_payback_days
        data_type: DOUBLE
        description: 'Estimated days to recover CAC: cost_per_conversion divided by average conversion value, scaled to 30 days and rounded when applicable; otherwise NULL'
      - name: cumulative_acquisition_cost
        data_type: DOUBLE
        description: Running total of spend within each account ordered by date_day; same-day ties accumulate in row order
      - name: cumulative_conversions
        data_type: DOUBLE
        description: Running total of conversions within each account ordered by date_day; same-day ties accumulate in row order
      - name: cumulative_ltv
        data_type: DOUBLE
        description: Running total of conversion value within each account ordered by date_day; same-day ties accumulate in row order
      - name: cohort_avg_cac
        data_type: DOUBLE
        description: Average running CAC within the same acquisition_cohort and advertising_channel_type; rows with zero cumulative_conversions are excluded; not rounded
      - name: cohort_avg_ltv
        data_type: DOUBLE
        description: Average running LTV per conversion within the same acquisition_cohort and advertising_channel_type; rows with zero cumulative_conversions are excluded; not rounded
      - name: cac_vs_cohort_pct
        data_type: DOUBLE
        description: Percent difference vs cohort CAC, rounded to 2 decimals; NULL when cohort_avg_cac is missing or not positive
      - name: ltv_vs_cohort_pct
        data_type: DOUBLE
        description: Percent difference vs cohort LTV, rounded to 2 decimals; NULL when cohort_avg_ltv is missing or not positive
      - name: cac_efficiency_percentile
        data_type: DOUBLE
        description: Percentile rank (0–1) of CAC within the acquisition_cohort, with lower CAC ranked higher; ties share rank
      - name: ltv_cac_performance_percentile
        data_type: DOUBLE
        description: Percentile rank (0–1) of LTV:CAC within the acquisition_cohort, with higher ratios ranked higher; ties share rank
      - name: acquisition_efficiency_tier
        data_type: VARCHAR
        description: 'Tier by ltv_cac_ratio thresholds: Excellent (≥3.0), Good (≥2.0), Break-even (≥1.0), Negative (≥0.5), else Poor'
      - name: cac_performance_tier
        data_type: VARCHAR
        description: 'Tier by cac_efficiency_percentile: Top CAC Efficiency (≥0.8), Above Average CAC (≥0.6), Average CAC (≥0.4), Below Average CAC (≥0.2), else High CAC'
      - name: strategic_customer_segment
        data_type: VARCHAR
        description: Strategic segment chosen by ordered rules using ltv_cac_ratio, average_customer_ltv, days_since_first_conversion, and CAC vs cohort
      - name: acquisition_sophistication_score
        data_type: DOUBLE
        description: Score clamped to [0,100] using channel diversity, active campaigns, LTV, and LTV:CAC; rounded to 1 decimal in the final output
      - name: active_campaigns_count
        data_type: BIGINT
        description: Distinct campaign count per account_id and date_day from matched cohort rows; NULLs ignored
      - name: channel_diversity_count
        data_type: BIGINT
        description: Distinct advertising_channel_type count per account_id and date_day from matched cohort rows; NULLs ignored
      - name: acquisition_recommendation
        data_type: VARCHAR
        description: Recommendation selected by ordered rules using LTV:CAC, CAC percentile, channel diversity, days since first conversion, CAC vs cohort, and active campaigns
      - name: negative_roi_alert
        data_type: BOOLEAN
        description: True when ltv_cac_ratio < 0.5 and cumulative_acquisition_cost > 1000; else false
        tests:
        - not_null
      - name: high_cac_alert
        data_type: BOOLEAN
        description: True when customer_acquisition_cost > cohort_avg_cac × 2; else false
        tests:
        - not_null
      - name: scale_opportunity
        data_type: BOOLEAN
        description: True when ltv_cac_ratio ≥ 4.0 and cac_efficiency_percentile ≥ 0.9; else false
        tests:
        - not_null
      - name: retention_risk
        data_type: BOOLEAN
        description: True when days_since_first_conversion > 365 and ltv_cac_ratio < 1.5; else false
        tests:
        - not_null
```

## agent 最终 SQL

S4

```sql
WITH ap AS (SELECT * FROM intermediate.int_google_ads__account_performance_metrics), cc AS (SELECT * FROM intermediate.int_google_ads__campaign_cohort_analysis), base AS (
 SELECT ap.*,cc.campaign_id,cc.advertising_channel_type,cc.advertising_channel_subtype,cc.lifecycle_stage campaign_lifecycle_stage FROM ap LEFT JOIN cc ON ap.source_relation=cc.source_relation AND ap.account_id=cc.campaign_id AND ap.date_day=cc.date_day WHERE ap.conversions>0 OR ap.spend>0),
 activity AS (SELECT *,min(date_day) FILTER(WHERE conversions>0) OVER(PARTITION BY account_id) first_conversion_date,
 sum(spend) over(partition by account_id order by date_day rows unbounded preceding) cumulative_acquisition_cost,
 sum(conversions) over(partition by account_id order by date_day rows unbounded preceding) cumulative_conversions,
 sum(conversions_value) over(partition by account_id order by date_day rows unbounded preceding) cumulative_ltv,
 count(distinct campaign_id) over(partition by account_id,date_day) active_campaigns_count,
 count(distinct advertising_channel_type) over(partition by account_id,date_day) channel_diversity_count
 FROM base), economics AS (
 SELECT *,date_trunc('month',first_conversion_date)::DATE acquisition_cohort,date_diff('day',first_conversion_date,date_day) days_since_first_conversion,
 round(cumulative_acquisition_cost/nullif(cumulative_conversions,0),2) customer_acquisition_cost,
 CASE WHEN cumulative_conversions>0 THEN round(cumulative_ltv/cumulative_conversions,2) ELSE 0 END average_customer_ltv,
 CASE WHEN cumulative_acquisition_cost>0 AND cumulative_conversions>0 THEN round((cumulative_ltv/cumulative_conversions)/(cumulative_acquisition_cost/cumulative_conversions),2) ELSE 0 END ltv_cac_ratio,
 round(CASE WHEN cost_per_conversion>0 AND conversions_value>0 AND conversions>0 THEN cost_per_conversion/(conversions_value/conversions)*30 END,0) estimated_payback_days
 FROM activity), benchmarks AS (
 SELECT *,avg(customer_acquisition_cost) FILTER(WHERE cumulative_conversions>0) over(partition by acquisition_cohort,advertising_channel_type) cohort_avg_cac,
 avg(average_customer_ltv) FILTER(WHERE cumulative_conversions>0) over(partition by acquisition_cohort,advertising_channel_type) cohort_avg_ltv,
 percent_rank() over(partition by acquisition_cohort order by customer_acquisition_cost desc) cac_efficiency_percentile,
 percent_rank() over(partition by acquisition_cohort order by ltv_cac_ratio) ltv_cac_performance_percentile
 FROM economics), classifications AS (
 SELECT *,round(CASE WHEN cohort_avg_cac>0 THEN (customer_acquisition_cost-cohort_avg_cac)/cohort_avg_cac*100 END,2) cac_vs_cohort_pct,
 round(CASE WHEN cohort_avg_ltv>0 THEN (average_customer_ltv-cohort_avg_ltv)/cohort_avg_ltv*100 END,2) ltv_vs_cohort_pct,
 CASE WHEN ltv_cac_ratio>=3 THEN 'Excellent' WHEN ltv_cac_ratio>=2 THEN 'Good' WHEN ltv_cac_ratio>=1 THEN 'Break-even' WHEN ltv_cac_ratio>=.5 THEN 'Negative' ELSE 'Poor' END acquisition_efficiency_tier,
 CASE WHEN cac_efficiency_percentile>=.8 THEN 'Top CAC Efficiency' WHEN cac_efficiency_percentile>=.6 THEN 'Above Average CAC' WHEN cac_efficiency_percentile>=.4 THEN 'Average CAC' WHEN cac_efficiency_percentile>=.2 THEN 'Below Average CAC' ELSE 'High CAC' END cac_performance_tier,
 CASE WHEN days_since_first_conversion IS NULL THEN 'Not Acquired' WHEN days_since_first_conversion<=30 THEN 'New Customer' WHEN days_since_first_conversion<=90 THEN 'Early Stage' WHEN days_since_first_conversion<=365 THEN 'Developing Customer' WHEN days_since_first_conversion<=1095 THEN 'Mature Customer' ELSE 'Long-term Customer' END customer_maturity_stage,
 least(100.0,greatest(0.0,channel_diversity_count*15+active_campaigns_count*5+least(average_customer_ltv/100,30)+least(ltv_cac_ratio*5,25))) acquisition_sophistication_score
 FROM benchmarks)
SELECT source_relation,account_id,account_name,date_day,acquisition_cohort,days_since_first_conversion,advertising_channel_type,advertising_channel_subtype,account_maturity_stage,customer_maturity_stage,campaign_lifecycle_stage,spend,clicks,impressions,conversions,conversions_value,ctr,cpc,cost_per_conversion,roas,
 customer_acquisition_cost,average_customer_ltv,ltv_cac_ratio,estimated_payback_days,cumulative_acquisition_cost,cumulative_conversions,cumulative_ltv,cohort_avg_cac,cohort_avg_ltv,cac_vs_cohort_pct,ltv_vs_cohort_pct,cac_efficiency_percentile,ltv_cac_performance_percentile,acquisition_efficiency_tier,cac_performance_tier,
 CASE WHEN ltv_cac_ratio>=4 AND average_customer_ltv>1000 THEN 'High-value scale customer' WHEN ltv_cac_ratio<.5 THEN 'Unprofitable customer' WHEN days_since_first_conversion<=30 THEN 'New customer development' WHEN cac_vs_cohort_pct>50 THEN 'High CAC customer' ELSE 'Core customer' END strategic_customer_segment,
 round(acquisition_sophistication_score,1) acquisition_sophistication_score,active_campaigns_count,channel_diversity_count,
 CASE WHEN ltv_cac_ratio>=3 AND cac_efficiency_percentile>=.8 THEN 'Scale acquisition investment' WHEN ltv_cac_ratio<.5 THEN 'Reduce acquisition cost' WHEN channel_diversity_count<2 THEN 'Diversify acquisition channels' WHEN cac_vs_cohort_pct>30 THEN 'Optimize CAC versus cohort' ELSE 'Maintain acquisition strategy' END acquisition_recommendation,
 (ltv_cac_ratio<.5 AND cumulative_acquisition_cost>1000) negative_roi_alert,(customer_acquisition_cost>cohort_avg_cac*2) high_cac_alert,(ltv_cac_ratio>=4 AND cac_efficiency_percentile>=.9) scale_opportunity,(days_since_first_conversion>365 AND ltv_cac_ratio<1.5) retention_risk
FROM classifications WHERE (cumulative_conversions>0 OR spend>0) AND date_day IS NOT NULL AND account_id IS NOT NULL ORDER BY account_id,date_day DESC
```

## gold SQL（仅供定位差异）

S5

```sql
-- Google Ads Customer Acquisition Analysis
-- Advanced customer acquisition cost analysis with cohort-based LTV modeling

with account_performance as (
    select *
    from intermediate.int_google_ads__account_performance_metrics
),

campaign_cohorts as (
    select *
    from intermediate.int_google_ads__campaign_cohort_analysis
),

-- Calculate customer acquisition metrics by cohort and channel
acquisition_metrics as (
    select
        ap.source_relation,
        ap.account_id,
        ap.account_name,
        ap.date_day,
        ap.account_maturity_stage,
        
        -- Acquisition cohort based on first conversion date
        date_trunc('month', 
            min(case when ap.conversions > 0 then try_cast(ap.date_day as date) end) over (partition by ap.account_id)
        ) as acquisition_cohort,
        
        -- Days since first conversion for lifetime analysis
        datediff('day',
            min(case when ap.conversions > 0 then try_cast(ap.date_day as date) end) over (partition by ap.account_id),
            try_cast(ap.date_day as date)
        ) as days_since_first_conversion,
        
        -- Campaign channel information
        cc.advertising_channel_type,
        cc.advertising_channel_subtype,
        cc.lifecycle_stage as campaign_lifecycle_stage,
        
        -- Performance metrics
        ap.spend,
        ap.clicks,
        ap.impressions,
        ap.conversions,
        ap.conversions_value,
        ap.ctr,
        ap.cpc,
        ap.cost_per_conversion,
        ap.roas,
        
        -- Cumulative metrics for LTV calculation
        sum(ap.spend) over (
            partition by ap.account_id 
            order by ap.date_day 
            rows unbounded preceding
        ) as cumulative_acquisition_cost,
        
        sum(ap.conversions) over (
            partition by ap.account_id 
            order by ap.date_day 
            rows unbounded preceding
        ) as cumulative_conversions,
        
        sum(ap.conversions_value) over (
            partition by ap.account_id 
            order by ap.date_day 
            rows unbounded preceding
        ) as cumulative_ltv,
        
        -- Campaign portfolio diversity
        count(distinct cc.campaign_id) over (
            partition by ap.account_id, ap.date_day
        ) as active_campaigns_count,
        
        count(distinct cc.advertising_channel_type) over (
            partition by ap.account_id, ap.date_day
        ) as channel_diversity_count
        
    from account_performance ap
    left join campaign_cohorts cc
        on ap.account_id = cc.campaign_id  -- Join logic based on available relationships
        and ap.source_relation = cc.source_relation
        and ap.date_day = cc.date_day
    where ap.conversions > 0 or ap.spend > 0  -- Only include accounts with activity
),

-- Calculate cohort-based acquisition economics
cohort_economics as (
    select
        am.*,
        
        -- Customer acquisition cost (CAC) calculations
        case 
            when cumulative_conversions > 0 then round(cumulative_acquisition_cost / cumulative_conversions, 2)
            else null 
        end as customer_acquisition_cost,
        
        -- Lifetime value metrics
        case 
            when cumulative_conversions > 0 then round(cumulative_ltv / cumulative_conversions, 2)
            else 0 
        end as average_customer_ltv,
        
        -- LTV:CAC ratio
        case 
            when cumulative_acquisition_cost > 0 and cumulative_conversions > 0 
            then round((cumulative_ltv / cumulative_conversions) / (cumulative_acquisition_cost / cumulative_conversions), 2)
            else 0 
        end as ltv_cac_ratio,
        
        -- Payback period estimation (in days)
        case 
            when cost_per_conversion > 0 and conversions_value > 0
            then round(cost_per_conversion / (conversions_value / nullif(conversions, 0)) * 30, 0)  -- Assuming monthly recurring value
            else null 
        end as estimated_payback_days,
        
        -- Cohort benchmarks
        avg(case when cumulative_conversions > 0 then cumulative_acquisition_cost / cumulative_conversions end) over (
            partition by acquisition_cohort, advertising_channel_type
        ) as cohort_avg_cac,
        
        avg(case when cumulative_conversions > 0 then cumulative_ltv / cumulative_conversions end) over (
            partition by acquisition_cohort, advertising_channel_type
        ) as cohort_avg_ltv,
        
        -- Acquisition efficiency percentiles
        percent_rank() over (
            partition by acquisition_cohort 
            order by customer_acquisition_cost asc
        ) as cac_efficiency_percentile,
        
        percent_rank() over (
            partition by acquisition_cohort 
            order by ltv_cac_ratio desc
        ) as ltv_cac_performance_percentile
        
    from acquisition_metrics am
),

-- Advanced segmentation and insights
customer_segmentation as (
    select
        ce.*,
        
        -- Customer acquisition efficiency tier
        case 
            when ltv_cac_ratio >= 3.0 then 'Excellent'
            when ltv_cac_ratio >= 2.0 then 'Good'  
            when ltv_cac_ratio >= 1.0 then 'Break-even'
            when ltv_cac_ratio >= 0.5 then 'Negative'
            else 'Poor'
        end as acquisition_efficiency_tier,
        
        -- Channel acquisition performance
        case 
            when cac_efficiency_percentile >= 0.8 then 'Top CAC Efficiency'
            when cac_efficiency_percentile >= 0.6 then 'Above Average CAC'
            when cac_efficiency_percentile >= 0.4 then 'Average CAC'
            when cac_efficiency_percentile >= 0.2 then 'Below Average CAC'
            else 'High CAC'
        end as cac_performance_tier,
        
        -- Customer maturity stage based on days since acquisition
        case 
            when days_since_first_conversion is null then 'Not Acquired'
            when days_since_first_conversion <= 30 then 'New Customer'
            when days_since_first_conversion <= 90 then 'Early Stage'
            when days_since_first_conversion <= 365 then 'Developing Customer'
            when days_since_first_conversion <= 1095 then 'Mature Customer'
            else 'Long-term Customer'
        end as customer_maturity_stage,
        
        -- Investment sophistication score
        least(100, greatest(0,
            coalesce(channel_diversity_count * 15, 0) +
            coalesce(active_campaigns_count * 5, 0) +
            case when average_customer_ltv > 500 then 30 else average_customer_ltv / 500 * 30 end +
            case when ltv_cac_ratio >= 2.0 then 25 else ltv_cac_ratio / 2.0 * 25 end
        )) as acquisition_sophistication_score,
        
        -- Performance vs cohort benchmarks
        case 
            when cohort_avg_cac > 0 then round((customer_acquisition_cost - cohort_avg_cac) / cohort_avg_cac * 100, 2)
            else null 
        end as cac_vs_cohort_pct,
        
        case 
            when cohort_avg_ltv > 0 then round((average_customer_ltv - cohort_avg_ltv) / cohort_avg_ltv * 100, 2)
            else null 
        end as ltv_vs_cohort_pct,
        
        -- Strategic customer classification
        case 
            when ltv_cac_ratio >= 3.0 and average_customer_ltv >= 1000 then 'Premium Customer'
            when ltv_cac_ratio >= 2.0 and customer_acquisition_cost <= cohort_avg_cac then 'High Value Customer'
            when ltv_cac_ratio >= 1.5 and days_since_first_conversion <= 90 then 'Growth Opportunity'
            when ltv_cac_ratio < 1.0 and days_since_first_conversion > 180 then 'At Risk Customer'
            when customer_acquisition_cost > cohort_avg_cac * 1.5 then 'High Cost Customer'
            else 'Standard Customer'
        end as strategic_customer_segment,
        
        -- Acquisition optimization recommendations
        case 
            when ltv_cac_ratio >= 3.0 and cac_efficiency_percentile >= 0.8 then 'Scale Aggressively'
            when ltv_cac_ratio >= 2.0 and channel_diversity_count < 3 then 'Expand Channels'
            when ltv_cac_ratio < 1.0 and days_since_first_conversion > 90 then 'Optimize or Pause'
            when customer_acquisition_cost > cohort_avg_cac * 1.3 then 'Reduce Acquisition Spend'
            when ltv_cac_ratio >= 1.5 and active_campaigns_count < 5 then 'Increase Investment'
            else 'Maintain Current Strategy'
        end as acquisition_recommendation
        
    from cohort_economics ce
),

final as (
    select
        source_relation,
        account_id,
        account_name,
        date_day,
        acquisition_cohort,
        days_since_first_conversion,
        
        -- Channel and campaign context
        advertising_channel_type,
        advertising_channel_subtype,
        account_maturity_stage,
        customer_maturity_stage,
        campaign_lifecycle_stage,
        
        -- Core performance metrics
        spend,
        clicks,
        impressions,
        conversions,
        conversions_value,
        ctr,
        cpc,
        cost_per_conversion,
        roas,
        
        -- Customer acquisition economics
        customer_acquisition_cost,
        average_customer_ltv,
        ltv_cac_ratio,
        estimated_payback_days,
        cumulative_acquisition_cost,
        cumulative_conversions,
        cumulative_ltv,
        
        -- Benchmarking and performance
        cohort_avg_cac,
        cohort_avg_ltv,
        cac_vs_cohort_pct,
        ltv_vs_cohort_pct,
        cac_efficiency_percentile,
        ltv_cac_performance_percentile,
        
        -- Segmentation and insights
        acquisition_efficiency_tier,
        cac_performance_tier,
        strategic_customer_segment,
        round(acquisition_sophistication_score, 1) as acquisition_sophistication_score,
        
        -- Portfolio metrics
        active_campaigns_count,
        channel_diversity_count,
        
        -- Strategic guidance
        acquisition_recommendation,
        
        -- Alert flags
        case when ltv_cac_ratio < 0.5 and cumulative_acquisition_cost > 1000 then true else false end as negative_roi_alert,
        case when customer_acquisition_cost > cohort_avg_cac * 2 then true else false end as high_cac_alert,
        case when ltv_cac_ratio >= 4.0 and cac_efficiency_percentile >= 0.9 then true else false end as scale_opportunity,
        case when days_since_first_conversion > 365 and ltv_cac_ratio < 1.5 then true else false end as retention_risk
        
    from customer_segmentation
)

select *
from final
where 
    -- Focus on accounts with acquisition activity
    (cumulative_conversions > 0 or spend > 0)
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
| K1 | <code>{"account_id":"acc02369342072","date_day":"2021-01-31"}</code> |
| K2 | <code>{"account_id":"acc02369342072","date_day":"2021-03-03"}</code> |
| K3 | <code>{"account_id":"acc02369342072","date_day":"2021-03-18"}</code> |
| K4 | <code>{"account_id":"acc02369342072","date_day":"2021-05-10"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| account_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| date_day | 0 | 0 | 0 | DATE | DATE |
| advertising_channel_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| advertising_channel_subtype | 0 | 0 | 0 | VARCHAR | VARCHAR |
| account_maturity_stage | 0 | 0 | 0 | VARCHAR | VARCHAR |
| customer_maturity_stage | 0 | 0 | 0 | VARCHAR | VARCHAR |
| campaign_lifecycle_stage | 0 | 0 | 0 | VARCHAR | VARCHAR |
| spend | 0 | 0 | 0 | DOUBLE | DOUBLE |
| clicks | 0 | 0 | 0 | BIGINT | BIGINT |
| impressions | 0 | 0 | 0 | BIGINT | BIGINT |
| conversions | 0 | 0 | 0 | DOUBLE | DOUBLE |
| conversions_value | 0 | 0 | 0 | DOUBLE | DOUBLE |
| ctr | 0 | 0 | 0 | FLOAT | FLOAT |
| cpc | 0 | 0 | 0 | DOUBLE | DOUBLE |
| cost_per_conversion | 0 | 0 | 0 | DOUBLE | DOUBLE |
| roas | 0 | 0 | 0 | DOUBLE | DOUBLE |
| customer_acquisition_cost | 0 | 0 | 0 | DOUBLE | DOUBLE |
| average_customer_ltv | 0 | 0 | 0 | DOUBLE | DOUBLE |
| ltv_cac_ratio | 0 | 0 | 0 | DOUBLE | DOUBLE |
| estimated_payback_days | 0 | 0 | 0 | DOUBLE | DOUBLE |
| cumulative_acquisition_cost | 0 | 0 | 0 | DOUBLE | DOUBLE |
| cumulative_conversions | 0 | 0 | 0 | DOUBLE | DOUBLE |
| cumulative_ltv | 0 | 0 | 0 | DOUBLE | DOUBLE |
| cohort_avg_cac | 10000 | 10000 | 10000 | DOUBLE | DOUBLE |
| cohort_avg_ltv | 10000 | 10000 | 10000 | DOUBLE | DOUBLE |
| cac_efficiency_percentile | 9990 | 9990 | 9990 | DOUBLE | DOUBLE |
| ltv_cac_performance_percentile | 9991 | 9991 | 9991 | DOUBLE | DOUBLE |
| acquisition_efficiency_tier | 0 | 0 | 0 | VARCHAR | VARCHAR |
| cac_performance_tier | 7998 | 7998 | 7998 | VARCHAR | VARCHAR |
| strategic_customer_segment | 10000 | 10000 | 10000 | VARCHAR | VARCHAR |
| acquisition_sophistication_score | 10000 | 10000 | 10000 | DOUBLE | DOUBLE |
| active_campaigns_count | 0 | 0 | 0 | BIGINT | BIGINT |
| channel_diversity_count | 0 | 0 | 0 | BIGINT | BIGINT |
| acquisition_recommendation | 10000 | 10000 | 10000 | VARCHAR | VARCHAR |
| negative_roi_alert | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| high_cac_alert | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| scale_opportunity | 145 | 145 | 145 | BOOLEAN | BOOLEAN |
| retention_risk | 0 | 0 | 0 | BOOLEAN | BOOLEAN |

cohort_avg_cac 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 51.474879340064014 | 51.47488524517977 |
| K2 | 51.474879340064014 | 51.47488524517977 |
| K3 | 51.474879340064014 | 51.47488524517977 |

cohort_avg_ltv 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 109.73041245998529 | 109.73040771801129 |
| K2 | 109.73041245998529 | 109.73040771801129 |
| K3 | 109.73041245998529 | 109.73040771801129 |

cac_efficiency_percentile 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0.01797808151705455 | 0.9820219184829454 |
| K2 | 0.9881787957148135 | 0.011821204285186553 |
| K3 | 0.9917497845092969 | 0.008250215490703115 |

ltv_cac_performance_percentile 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0.5062184460041866 | 0.48639330131757175 |
| K2 | 0.9895333087058245 | 0.010466691294175594 |
| K3 | 0.9915035094200222 | 0.008496490579977835 |

cac_performance_tier 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | High CAC | Top CAC Efficiency |
| K2 | Top CAC Efficiency | High CAC |
| K3 | Top CAC Efficiency | High CAC |

strategic_customer_segment 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | New customer development | Growth Opportunity |
| K2 | Core customer | High Value Customer |
| K3 | Core customer | High Value Customer |

acquisition_sophistication_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 12.6 | 35.5 |
| K2 | 22.9 | 32.2 |
| K3 | 24.2 | 32.0 |

acquisition_recommendation 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | Diversify acquisition channels | Expand Channels |
| K2 | Scale acquisition investment | Expand Channels |
| K3 | Scale acquisition investment | Expand Channels |

scale_opportunity 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | true | false |
| K3 | true | false |
| K4 | true | false |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>3列；[{"column":"advertising_channel_type","table_rows":10000},{"column":"advertising_channel_subtype","table_rows":10000},{"column":"campaign_lifecycle_stage","table_rows":10000}]</code> |
| A3_constant_nonnull_column | <code>4列；[{"column":"source_relation","value":"google_ads"},{"column":"active_campaigns_count","value":"0"},{"column":"channel_diversity_count","value":"0"}]</code> |
| A4_equal_columns | <code>1组；[{"columns":["active_campaigns_count","channel_diversity_count"],"nonnull_equal_rows":10000,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>1组；[{"columns":["active_campaigns_count","channel_diversity_count"],"nonnull_equal_rows":10000,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| B7_specified_not_read | <code>["intermediate.int_google_ads__account_performance_metrics (source_relation, account_id, account_name, date_day, account_maturity_stage, spend, clicks, impressions, conversions, conversions_value, ctr, cpc, cost_per_conversion, roas)","intermediate.int_google_ads__campaign_cohort_analysis (source_relation, campaign_id, date_day, advertising_channel_type, advertising_channel_subtype, lifecycle_stage)"]</code> |

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
write('google_ads__customer_acquisition_analysis',"""WITH ap AS (SELECT * FROM intermediate.int_google_ads__account_performance_metrics), cc AS (SELECT * FROM intermediate.int_google_ads__campaign_cohort_analysis), base AS (
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-005.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-005/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/sql/marts/google_ads__customer_acquisition_analysis.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-005/sql/marts/google_ads__customer_acquisition_analysis.sql`
- S6: `records/006_contract_impl-005.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/dacomp-de-impl-005/result.md`
- S10: `data/019_packages_work/019_impl-005_google_ads__customer_acquisition_analysis/019_impl-005_google_ads__customer_acquisition_analysis.json`
- S11: `data/005_cs_work/impl-005/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-005/google_ads.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-005/agent/.events/sessions`
