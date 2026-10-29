# impl-003 | intermediate | int_customer360__customer_lifecycle_metrics | 差异：S1；日期 原记录

## 契约完整原文

S3:914–1037

```yaml
    - name: int_customer360__customer_lifecycle_metrics
      description: Customer lifecycle metrics, health scoring, retention/churn risk, and cohort/tier enrichments derived from customer behavior analysis
      grain: One row per customer from intermediate.int_customer360__customer_behavior_analysis
      source_models:
      - intermediate.int_customer360__customer_behavior_analysis
      business_logic: 'Starting from intermediate.int_customer360__customer_behavior_analysis (one row per resolved customer), compute lifecycle metrics and enrichments: - Activity windows and recency: - days_since_last_activity = number of days between customer_last_activity and today; NULL if customer_last_activity is missing. - active_X_days flags (X ∈ {30,60,90,180,365}) = 1 if customer_last_activity occurred within X days of today, else 0; missing customer_last_activity yields 0. - Lifecycle stage (first match wins): - ''Acquisition'' if account_age_days ≤ 30 - ''Activation'' if account_age_days ≤ 90 and last_activity within 30 days - ''Growth'' if account_age_days ≤ 365 and last_activity within 60 days - ''Maturity'' if account_age_days > 365 and last_activity within 90 days - ''Dormant'' if last_activity older than 180 days - Else ''Retention'' - Note: NULL account_age_days or last_activity causes earlier conditions to fail and typically falls through to ''Retention''. - Cohort and platform consistency: - acquisition_cohort_month = month of the first touchpoint (truncated to month); NULL if first_touchpoint is missing. - platform_consistency_score ∈ {1,2,3}: sum of presence flags (in_marketo + in_stripe + in_zendesk); 3 if sum ≥ 3, 2 if sum = 2, else 1. NULL in any flag leads to the else path → 1. - Value and engagement scores: - estimated_customer_value (DECIMAL(6,2)) by customer_segment: - ''Champion'' 5000.00; ''Loyal Customer'' 3500.00; ''Potential Loyalist'' 2000.00; ''New Customer'' 800.00; ''At Risk'' 1200.00; ''Hibernating'' 500.00; else 200.00. - frequency_score (1–5): 5 if platform_consistency_score = 3 and active_30_days = 1; 4 if platform_consistency_score ≥ 2 and active_60_days = 1; 3 if platform_consistency_score ≥ 2 and active_90_days = 1; 2 if active_180_days = 1; else 1. - recency_score (1–5) by days_since_last_activity: 5 (≤7), 4 (≤30), 3 (≤60), 2 (≤180), else 1; NULL days_since_last_activity maps to 1. - estimated_transaction_count (DOUBLE): simulated per run: - If segment in (''Champion'',''Loyal Customer'') → integer 2–9 - If ''Potential Loyalist'' → integer 1–4 - Else → integer 0–1 - Stored as DOUBLE; values vary each execution. - customer_health_score (DECIMAL(15,2)) = rounded to 2 decimals from: recency_component*0.3 + platform_consistency_score*0.3 + segment_component*0.4, where: - recency_component: 5/4/3/2/1 as in recency_score logic - segment_component: ''Champion'' 5.0; ''Loyal Customer'' 4.5; ''Potential Loyalist'' 3.5; ''New Customer'' 3.0; ''At Risk'' 2.0; ''Hibernating'' 1.5; else 1.0 - Advanced lifecycle metrics: - estimated_customer_ltv (DECIMAL(18,2)) = estimated_customer_value × (1 + 0.2 × frequency_score) × (1 + 0.1 × platform_consistency_score) × stage_factor; rounded to 2 decimals, where stage_factor: Growth 1.5; Maturity 2.0; Retention 1.8; Activation 1.2; else 1.0. - retention_probability (DECIMAL(3,2)) by customer_health_score: ≥4.5→0.95; ≥4.0→0.85; ≥3.5→0.75; ≥3.0→0.65; ≥2.5→0.50; ≥2.0→0.35; else 0.20. - churn_probability (DECIMAL(3,2)) inverse mapping: ≥4.5→0.05; ≥4.0→0.15; ≥3.5→0.25; ≥3.0→0.35; ≥2.5→0.50; ≥2.0→0.65; else 0.80. - revenue_at_risk (DECIMAL(9,2)) = estimated_customer_value × churn-probability mapping above; rounded to 2 decimals. - growth_potential (first match wins): - ''High Growth Potential'' if lifecycle_stage in (''Acquisition'',''Activation'') and customer_health_score ≥ 3.5 - ''Expansion Ready'' if lifecycle_stage = ''Growth'' and platform_consistency_score ≥ 2 - ''Upsell Candidate'' if lifecycle_stage = ''Maturity'' and customer_health_score ≥ 4.0 - ''Stable Account'' if lifecycle_stage = ''Retention'' and customer_health_score ≥ 3.0 - ''Reactivation Needed'' if lifecycle_stage = ''Dormant'' - Else ''Monitor'' - action_priority (INT, first match wins): - 5 if churn-probability mapping ≥ 0.65 - 4 if lifecycle_stage = ''Acquisition'' and customer_health_score ≥ 3.5 - 4 if lifecycle_stage = ''Growth'' and platform_consistency_score ≥ 2 - 3 if customer_health_score ≥ 4.0 and estimated_customer_value ≥ 3000 - 3 if churn-probability mapping ≥ 0.35 - Else 2 - acquisition_year = year of acquisition_cohort_month; acquisition_month = month number; months_since_acquisition = whole months between acquisition_cohort_month and today; NULL if acquisition_cohort_month is NULL. - acquisition_season: ''Holiday Season'' if month in (11,12,1); ''Summer Season'' if in (6,7,8); ''Spring Season'' if in (3,4,5); else ''Fall Season'' (default for NULL or not matched). - Final enrichments: - customer_tier by estimated_customer_ltv: Platinum (≥8000), Gold (≥5000), Silver (≥2500), Bronze (≥1000), else Basic. - is_strategic_account = TRUE if estimated_customer_ltv ≥ 10000 OR (customer_segment in (''Champion'',''Loyal Customer'') AND platform_consistency_score = 3); else FALSE. - intervention_urgency by action_priority: 5→''Immediate''; 4→''This Week''; 3→''This Month''; else ''Routine''. - expected_retention_rate by LTV and lifecycle: 0.90 if LTV ≥ 8000; 0.85 if LTV ≥ 5000; 0.75 if LTV ≥ 2500 and lifecycle_stage ≠ ''Dormant''; 0.60 if LTV ≥ 1000 and lifecycle_stage in (''Growth'',''Maturity''); else 0.45. - performance_vs_expectation: ''Above Expectation'' if retention_probability > expected_retention_rate; ''Meeting Expectation'' if retention_probability ≥ 80% of expected_retention_rate; else ''Below Expectation''. - Output ordering: sorted by is_strategic_account (true first), then action_priority descending, then estimated_customer_ltv descending, then customer_health_score descending.'
      columns:
      - name: marketo_lead_id
        data_type: BIGINT
        description: Marketo lead identifier; may be NULL
      - name: stripe_customer_id
        data_type: VARCHAR
        description: Stripe customer identifier
      - name: zendesk_user_id
        data_type: BIGINT
        description: Zendesk user identifier; may be NULL
      - name: primary_email
        data_type: VARCHAR
        description: Primary resolved customer email
      - name: primary_organization
        data_type: VARCHAR
        description: Resolved customer organization or account label
      - name: customer_first_touchpoint
        data_type: TIMESTAMP
        description: Earliest known customer interaction; used to derive acquisition_cohort_month
      - name: customer_last_activity
        data_type: TIMESTAMP
        description: Most recent activity timestamp; used for recency and active window flags
      - name: account_age_days
        data_type: BIGINT
        description: Account age in days; used in lifecycle_stage rules
      - name: customer_segment
        data_type: VARCHAR
        description: Behavioral segment driving value and scoring rules
      - name: customer_journey_pattern
        data_type: VARCHAR
        description: Descriptive journey pattern label
      - name: days_since_last_activity
        data_type: BIGINT
        description: Days between customer_last_activity and today; NULL if customer_last_activity is NULL
      - name: active_30_days
        data_type: INTEGER
        description: 1 if last_activity within 30 days of today, else 0; NULL last_activity yields 0
      - name: active_60_days
        data_type: INTEGER
        description: 1 if last_activity within 60 days of today, else 0; NULL last_activity yields 0
      - name: active_90_days
        data_type: INTEGER
        description: 1 if last_activity within 90 days of today, else 0; NULL last_activity yields 0
      - name: active_180_days
        data_type: INTEGER
        description: 1 if last_activity within 180 days of today, else 0; NULL last_activity yields 0
      - name: active_365_days
        data_type: INTEGER
        description: 1 if last_activity within 365 days of today, else 0; NULL last_activity yields 0
      - name: lifecycle_stage
        data_type: VARCHAR
        description: 'Stage from ordered rules using account_age_days and recency: Acquisition, Activation, Growth, Maturity, Dormant, else Retention'
      - name: acquisition_cohort_month
        data_type: DATE
        description: Month of first touchpoint; NULL if customer_first_touchpoint is NULL
      - name: platform_consistency_score
        data_type: INTEGER
        description: 'Cross-platform presence score: 3 if all three sources, 2 if two, else 1; NULL flags fall through to 1'
      - name: estimated_customer_value
        data_type: DECIMAL(6,2)
        description: Segment-based monetary value estimate with fixed mapping; never NULL
      - name: frequency_score
        data_type: INTEGER
        description: Engagement frequency score (1–5) from platform consistency and recent activity per ordered rules
      - name: recency_score
        data_type: INTEGER
        description: Recency score (1–5) from days_since_last_activity thresholds; NULL recency maps to 1
      - name: estimated_transaction_count
        data_type: DOUBLE
        description: 'Simulated integer count: 2–9 for top segments, 1–4 for Potential Loyalist, else 0–1; varies each run'
      - name: customer_health_score
        data_type: DECIMAL(15,2)
        description: 'Weighted composite: 0.3×recency_component + 0.3×platform_consistency + 0.4×segment_component; rounded to 2 decimals'
      - name: estimated_customer_ltv
        data_type: DECIMAL(18,2)
        description: LTV estimate from value × frequency × platform × stage_factor; rounded to 2 decimals
      - name: retention_probability
        data_type: DECIMAL(3,2)
        description: Probability mapped from customer_health_score thresholds (≥4.5→0.95 down to else 0.20)
      - name: churn_probability
        data_type: DECIMAL(3,2)
        description: Inverse of retention mapping from customer_health_score (≥4.5→0.05 up to else 0.80)
      - name: revenue_at_risk
        data_type: DECIMAL(9,2)
        description: Estimated_customer_value multiplied by churn mapping; rounded to 2 decimals
      - name: growth_potential
        data_type: VARCHAR
        description: Categorical potential per ordered rules using lifecycle_stage, platform consistency, and health score
      - name: action_priority
        data_type: INTEGER
        description: Next-action priority (2–5) from ordered rules using churn mapping, lifecycle, platform consistency, health, and value
      - name: acquisition_year
        data_type: BIGINT
        description: Year extracted from acquisition_cohort_month; NULL if acquisition_cohort_month is NULL
      - name: acquisition_month
        data_type: BIGINT
        description: Month number (1–12) extracted from acquisition_cohort_month; NULL if acquisition_cohort_month is NULL
      - name: months_since_acquisition
        data_type: BIGINT
        description: Whole months between acquisition_cohort_month and today; NULL if acquisition_cohort_month is NULL
      - name: acquisition_season
        data_type: VARCHAR
        description: 'Season by acquisition month: Holiday (11,12,1), Summer (6,7,8), Spring (3,4,5), else Fall (default for NULL/not matched)'
      - name: customer_tier
        data_type: VARCHAR
        description: 'Tier by estimated_customer_ltv: Platinum (≥8000), Gold (≥5000), Silver (≥2500), Bronze (≥1000), else Basic'
      - name: is_strategic_account
        data_type: BOOLEAN
        description: TRUE if estimated_customer_ltv ≥ 10000 or (segment in ('Champion','Loyal Customer') and platform_consistency_score = 3), else FALSE
      - name: intervention_urgency
        data_type: VARCHAR
        description: 'Urgency label by action_priority: 5→Immediate; 4→This Week; 3→This Month; else Routine'
      - name: expected_retention_rate
        data_type: DECIMAL(3,2)
        description: 'Expected rate by LTV and lifecycle: 0.90, 0.85, 0.75 (non-Dormant), 0.60 (Growth/Maturity), else 0.45'
      - name: performance_vs_expectation
        data_type: VARCHAR
        description: 'Comparison of retention_probability vs expected_retention_rate: Above (>), Meeting (≥80%), or Below'
```

## agent 最终 SQL

S4

```sql
with base as (
    select *, date_diff('day', customer_last_activity, current_date)::bigint as days_since_last_activity,
           date_trunc('month', customer_first_touchpoint)::date as acquisition_cohort_month,
           case when customer_last_activity >= current_timestamp - interval '30 days' then 1 else 0 end as active_30_days,
           case when customer_last_activity >= current_timestamp - interval '60 days' then 1 else 0 end as active_60_days,
           case when customer_last_activity >= current_timestamp - interval '90 days' then 1 else 0 end as active_90_days,
           case when customer_last_activity >= current_timestamp - interval '180 days' then 1 else 0 end as active_180_days,
           case when customer_last_activity >= current_timestamp - interval '365 days' then 1 else 0 end as active_365_days,
           coalesce(in_marketo,0)+coalesce(in_stripe,0)+coalesce(in_zendesk,0) as platform_sum
    from intermediate.int_customer360__customer_behavior_analysis
), stages as (
    select *, case when account_age_days <= 30 then 'Acquisition'
        when account_age_days <= 90 and active_30_days=1 then 'Activation'
        when account_age_days <= 365 and active_60_days=1 then 'Growth'
        when account_age_days > 365 and active_90_days=1 then 'Maturity'
        when days_since_last_activity > 180 then 'Dormant' else 'Retention' end as lifecycle_stage,
        case when platform_sum>=3 then 3 when platform_sum=2 then 2 else 1 end as platform_consistency_score,
        case customer_segment when 'Champion' then 5000.00 when 'Loyal Customer' then 3500.00
          when 'Potential Loyalist' then 2000.00 when 'New Customer' then 800.00 when 'At Risk' then 1200.00
          when 'Hibernating' then 500.00 else 200.00 end::decimal(6,2) as estimated_customer_value,
        case when days_since_last_activity<=7 then 5 when days_since_last_activity<=30 then 4
          when days_since_last_activity<=60 then 3 when days_since_last_activity<=180 then 2 else 1 end as recency_score,
        case when platform_sum>=2 and active_90_days=1 then 3 when active_180_days=1 then 2 else 1 end as frequency_score
    from base
), health as (
    select *, round(recency_score*0.3 + platform_consistency_score*0.3 +
       (case customer_segment when 'Champion' then 5.0 when 'Loyal Customer' then 4.5 when 'Potential Loyalist' then 3.5
        when 'New Customer' then 3.0 when 'At Risk' then 2.0 when 'Hibernating' then 1.5 else 1.0 end)*0.4,2)::decimal(15,2) as customer_health_score,
       case when customer_segment in ('Champion','Loyal Customer') then 2+floor(random()*8)
            when customer_segment='Potential Loyalist' then 1+floor(random()*4) else floor(random()*2) end::double as estimated_transaction_count
    from stages
), measures as (
    select *, round(estimated_customer_value*(1+0.2*frequency_score)*(1+0.1*platform_consistency_score)*
       (case lifecycle_stage when 'Growth' then 1.5 when 'Maturity' then 2.0 when 'Retention' then 1.8 when 'Activation' then 1.2 else 1.0 end),2)::decimal(18,2) as estimated_customer_ltv,
       case when customer_health_score>=4.5 then 0.95 when customer_health_score>=4 then 0.85 when customer_health_score>=3.5 then 0.75 when customer_health_score>=3 then 0.65 when customer_health_score>=2.5 then 0.50 when customer_health_score>=2 then 0.35 else 0.20 end::decimal(3,2) as retention_probability,
       case when customer_health_score>=4.5 then 0.05 when customer_health_score>=4 then 0.15 when customer_health_score>=3.5 then 0.25 when customer_health_score>=3 then 0.35 when customer_health_score>=2.5 then 0.50 when customer_health_score>=2 then 0.65 else 0.80 end::decimal(3,2) as churn_probability
    from health
), outputs as (
    select *, round(estimated_customer_value*churn_probability,2)::decimal(9,2) as revenue_at_risk,
       case when lifecycle_stage in ('Acquisition','Activation') and customer_health_score>=3.5 then 'High Growth Potential'
            when lifecycle_stage='Growth' and platform_consistency_score>=2 then 'Expansion Ready'
            when lifecycle_stage='Maturity' and customer_health_score>=4 then 'Upsell Candidate'
            when lifecycle_stage='Retention' and customer_health_score>=3 then 'Stable Account'
            when lifecycle_stage='Dormant' then 'Reactivation Needed' else 'Monitor' end as growth_potential,
       case when churn_probability>=0.65 then 5 when lifecycle_stage='Acquisition' and customer_health_score>=3.5 then 4
            when lifecycle_stage='Growth' and platform_consistency_score>=2 then 4
            when customer_health_score>=4 and estimated_customer_value>=3000 then 3
            when churn_probability>=0.35 then 3 else 2 end as action_priority
    from measures
), completed as (
    select *, case when month(acquisition_cohort_month) in (11,12,1) then 'Holiday Season'
       when month(acquisition_cohort_month) in (6,7,8) then 'Summer Season'
       when month(acquisition_cohort_month) in (3,4,5) then 'Spring Season' else 'Fall Season' end as acquisition_season,
       case when estimated_customer_ltv>=8000 then 'Platinum' when estimated_customer_ltv>=5000 then 'Gold'
            when estimated_customer_ltv>=2500 then 'Silver' when estimated_customer_ltv>=1000 then 'Bronze' else 'Basic' end as customer_tier,
       case when estimated_customer_ltv>=10000 or (customer_segment in ('Champion','Loyal Customer') and platform_consistency_score=3) then true else false end as is_strategic_account,
       case when estimated_customer_ltv>=8000 then 0.90 when estimated_customer_ltv>=5000 then 0.85
            when estimated_customer_ltv>=2500 and lifecycle_stage<>'Dormant' then 0.75
            when estimated_customer_ltv>=1000 and lifecycle_stage in ('Growth','Maturity') then 0.60 else 0.45 end::decimal(3,2) as expected_retention_rate
    from outputs
)
select marketo_lead_id, stripe_customer_id, zendesk_user_id, primary_email, primary_organization,
 customer_first_touchpoint, customer_last_activity, account_age_days, customer_segment, customer_journey_pattern,
 days_since_last_activity, active_30_days, active_60_days, active_90_days, active_180_days, active_365_days,
 lifecycle_stage, acquisition_cohort_month, platform_consistency_score, estimated_customer_value,
 frequency_score, recency_score, estimated_transaction_count, customer_health_score, estimated_customer_ltv,
 retention_probability, churn_probability, revenue_at_risk,
 case when acquisition_cohort_month is not null then year(acquisition_cohort_month)::bigint end as acquisition_year,
 case when acquisition_cohort_month is not null then month(acquisition_cohort_month)::bigint end as acquisition_month,
 case when acquisition_cohort_month is not null then date_diff('month',acquisition_cohort_month::date,current_date)::bigint end as months_since_acquisition,
 acquisition_season, customer_tier, is_strategic_account,
 case action_priority when 5 then 'Immediate' when 4 then 'This Week' when 3 then 'This Month' else 'Routine' end as intervention_urgency,
 expected_retention_rate,
 case when retention_probability>expected_retention_rate then 'Above Expectation'
      when retention_probability>=expected_retention_rate*0.8 then 'Meeting Expectation' else 'Below Expectation' end as performance_vs_expectation,
 growth_potential, action_priority
from completed
```

## gold SQL（仅供定位差异）

S5

```sql
-- Customer lifecycle metrics and value calculation
-- Comprehensive customer lifetime value, retention analysis, and cohort metrics

with behavior_analysis as (
    select * from intermediate.int_customer360__customer_behavior_analysis
),

source_matches as (
    select * from intermediate.int_customer360__source_matches
),

marketo_data as (
    select * from intermediate.int_customer360__marketo
),

stripe_data as (
    select * from intermediate.int_customer360__stripe
),

zendesk_data as (
    select * from intermediate.int_customer360__zendesk
),

-- Calculate retention periods and activity windows
customer_activity_windows as (
    select 
        ba.marketo_lead_id,
        ba.stripe_customer_id,
        ba.zendesk_user_id,
        ba.primary_email,
        ba.primary_organization,
        ba.customer_first_touchpoint,
        ba.customer_last_activity,
        ba.account_age_days,
        ba.customer_segment,
        ba.customer_journey_pattern,
        
        -- Activity recency analysis  
        datediff('day', ba.customer_last_activity, current_date) as days_since_last_activity,
        
        -- Retention windows
        case 
            when ba.customer_last_activity >= current_date - interval '30 days' then 1
            else 0
        end as active_30_days,
        
        case 
            when ba.customer_last_activity >= current_date - interval '60 days' then 1
            else 0
        end as active_60_days,
        
        case 
            when ba.customer_last_activity >= current_date - interval '90 days' then 1
            else 0
        end as active_90_days,
        
        case 
            when ba.customer_last_activity >= current_date - interval '180 days' then 1
            else 0
        end as active_180_days,
        
        case 
            when ba.customer_last_activity >= current_date - interval '365 days' then 1
            else 0
        end as active_365_days,
        
        -- Lifecycle stage based on activity pattern
        case 
            when ba.account_age_days <= 30 then 'Acquisition'
            when ba.account_age_days <= 90 and ba.customer_last_activity >= current_date - interval '30 days' then 'Activation'
            when ba.account_age_days <= 365 and ba.customer_last_activity >= current_date - interval '60 days' then 'Growth'
            when ba.account_age_days > 365 and ba.customer_last_activity >= current_date - interval '90 days' then 'Maturity'
            when ba.customer_last_activity < current_date - interval '180 days' then 'Dormant'
            else 'Retention'
        end as lifecycle_stage,
        
        -- Cohort assignment (based on first touchpoint month)
        date_trunc('month', ba.customer_first_touchpoint) as acquisition_cohort_month,
        
        -- Cross-platform consistency score
        case 
            when ba.in_marketo + ba.in_stripe + ba.in_zendesk >= 3 then 3
            when ba.in_marketo + ba.in_stripe + ba.in_zendesk = 2 then 2
            else 1
        end as platform_consistency_score
        
    from behavior_analysis ba
),

-- Calculate customer value metrics (simulated with business rules)
customer_value_metrics as (
    select 
        caw.*,
        
        -- Simulated monetary value based on customer characteristics
        case 
            when caw.customer_segment = 'Champion' then 5000.00
            when caw.customer_segment = 'Loyal Customer' then 3500.00
            when caw.customer_segment = 'Potential Loyalist' then 2000.00
            when caw.customer_segment = 'New Customer' then 800.00
            when caw.customer_segment = 'At Risk' then 1200.00
            when caw.customer_segment = 'Hibernating' then 500.00
            else 200.00
        end as estimated_customer_value,
        
        -- Frequency score based on platform engagement
        case 
            when caw.platform_consistency_score = 3 and caw.active_30_days = 1 then 5
            when caw.platform_consistency_score >= 2 and caw.active_60_days = 1 then 4
            when caw.platform_consistency_score >= 2 and caw.active_90_days = 1 then 3
            when caw.active_180_days = 1 then 2
            else 1
        end as frequency_score,
        
        -- Recency score (inverse of days since last activity)
        case 
            when caw.days_since_last_activity <= 7 then 5
            when caw.days_since_last_activity <= 30 then 4
            when caw.days_since_last_activity <= 60 then 3
            when caw.days_since_last_activity <= 180 then 2
            else 1
        end as recency_score,
        
        -- Simulated transaction frequency
        case 
            when caw.customer_segment in ('Champion', 'Loyal Customer') then
                2 + floor(random() * 8)  -- 2-9 transactions
            when caw.customer_segment = 'Potential Loyalist' then
                1 + floor(random() * 4)  -- 1-4 transactions  
            when caw.customer_segment = 'New Customer' then
                floor(random() * 2)      -- 0-1 transactions
            else
                floor(random() * 2)      -- 0-1 transactions
        end as estimated_transaction_count,
        
        -- Customer health score
        round(
            (case 
                when caw.days_since_last_activity <= 7 then 5
                when caw.days_since_last_activity <= 30 then 4
                when caw.days_since_last_activity <= 60 then 3
                when caw.days_since_last_activity <= 180 then 2
                else 1
            end * 0.3 +
            caw.platform_consistency_score * 0.3 +
            case 
                when caw.customer_segment = 'Champion' then 5
                when caw.customer_segment = 'Loyal Customer' then 4.5
                when caw.customer_segment = 'Potential Loyalist' then 3.5
                when caw.customer_segment = 'New Customer' then 3.0
                when caw.customer_segment = 'At Risk' then 2.0
                when caw.customer_segment = 'Hibernating' then 1.5
                else 1.0
            end * 0.4), 2
        ) as customer_health_score
        
    from customer_activity_windows caw
),

-- Advanced lifecycle calculations
lifecycle_advanced_metrics as (
    select 
        cvm.*,
        
        -- Customer Lifetime Value calculation
        round(
            cvm.estimated_customer_value * 
            (1.0 + cvm.frequency_score * 0.2) * 
            (1.0 + cvm.platform_consistency_score * 0.1) *
            case 
                when cvm.lifecycle_stage = 'Growth' then 1.5
                when cvm.lifecycle_stage = 'Maturity' then 2.0
                when cvm.lifecycle_stage = 'Retention' then 1.8
                when cvm.lifecycle_stage = 'Activation' then 1.2
                else 1.0
            end, 2
        ) as estimated_customer_ltv,
        
        -- Retention probability based on historical patterns
        case 
            when cvm.customer_health_score >= 4.5 then 0.95
            when cvm.customer_health_score >= 4.0 then 0.85
            when cvm.customer_health_score >= 3.5 then 0.75
            when cvm.customer_health_score >= 3.0 then 0.65
            when cvm.customer_health_score >= 2.5 then 0.50
            when cvm.customer_health_score >= 2.0 then 0.35
            else 0.20
        end as retention_probability,
        
        -- Churn probability (inverse of retention)
        case 
            when cvm.customer_health_score >= 4.5 then 0.05
            when cvm.customer_health_score >= 4.0 then 0.15
            when cvm.customer_health_score >= 3.5 then 0.25
            when cvm.customer_health_score >= 3.0 then 0.35
            when cvm.customer_health_score >= 2.5 then 0.50
            when cvm.customer_health_score >= 2.0 then 0.65
            else 0.80
        end as churn_probability,
        
        -- Revenue at risk calculation
        round(
            cvm.estimated_customer_value *
            case 
                when cvm.customer_health_score >= 4.5 then 0.05
                when cvm.customer_health_score >= 4.0 then 0.15
                when cvm.customer_health_score >= 3.5 then 0.25
                when cvm.customer_health_score >= 3.0 then 0.35
                when cvm.customer_health_score >= 2.5 then 0.50
                when cvm.customer_health_score >= 2.0 then 0.65
                else 0.80
            end, 2
        ) as revenue_at_risk,
        
        -- Account growth potential
        case 
            when cvm.lifecycle_stage in ('Acquisition', 'Activation') and cvm.customer_health_score >= 3.5 then 'High Growth Potential'
            when cvm.lifecycle_stage = 'Growth' and cvm.platform_consistency_score >= 2 then 'Expansion Ready'
            when cvm.lifecycle_stage = 'Maturity' and cvm.customer_health_score >= 4.0 then 'Upsell Candidate'
            when cvm.lifecycle_stage = 'Retention' and cvm.customer_health_score >= 3.0 then 'Stable Account'
            when cvm.lifecycle_stage = 'Dormant' then 'Reactivation Needed'
            else 'Monitor'
        end as growth_potential,
        
        -- Next action priority (1-5 scale)
        case 
            when (case 
                when cvm.customer_health_score >= 4.5 then 0.05
                when cvm.customer_health_score >= 4.0 then 0.15
                when cvm.customer_health_score >= 3.5 then 0.25
                when cvm.customer_health_score >= 3.0 then 0.35
                when cvm.customer_health_score >= 2.5 then 0.50
                when cvm.customer_health_score >= 2.0 then 0.65
                else 0.80
            end) >= 0.65 then 5  -- Urgent retention
            when cvm.lifecycle_stage = 'Acquisition' and cvm.customer_health_score >= 3.5 then 4  -- High-value onboarding
            when cvm.lifecycle_stage = 'Growth' and cvm.platform_consistency_score >= 2 then 4  -- Expansion focus
            when cvm.customer_health_score >= 4.0 and cvm.estimated_customer_value >= 3000 then 3  -- Loyalty programs
            when (case 
                when cvm.customer_health_score >= 4.5 then 0.05
                when cvm.customer_health_score >= 4.0 then 0.15
                when cvm.customer_health_score >= 3.5 then 0.25
                when cvm.customer_health_score >= 3.0 then 0.35
                when cvm.customer_health_score >= 2.5 then 0.50
                when cvm.customer_health_score >= 2.0 then 0.65
                else 0.80
            end) >= 0.35 then 3  -- Preventive measures
            else 2  -- Standard engagement
        end as action_priority,
        
        -- Cohort performance indicators
        extract(year from cvm.acquisition_cohort_month) as acquisition_year,
        extract(month from cvm.acquisition_cohort_month) as acquisition_month,
        
        -- Months since acquisition
        datediff('month', cvm.acquisition_cohort_month, current_date) as months_since_acquisition,
        
        -- Seasonal acquisition flag
        case 
            when extract(month from cvm.acquisition_cohort_month) in (11, 12, 1) then 'Holiday Season'
            when extract(month from cvm.acquisition_cohort_month) in (6, 7, 8) then 'Summer Season'
            when extract(month from cvm.acquisition_cohort_month) in (3, 4, 5) then 'Spring Season'
            else 'Fall Season'
        end as acquisition_season
        
    from customer_value_metrics cvm
),

-- Final enrichment with business intelligence
final_lifecycle_metrics as (
    select 
        lam.*,
        
        -- Customer tier classification
        case 
            when lam.estimated_customer_ltv >= 8000 then 'Platinum'
            when lam.estimated_customer_ltv >= 5000 then 'Gold'
            when lam.estimated_customer_ltv >= 2500 then 'Silver'
            when lam.estimated_customer_ltv >= 1000 then 'Bronze'
            else 'Basic'
        end as customer_tier,
        
        -- Strategic account flag
        case 
            when lam.estimated_customer_ltv >= 10000 or
                 (lam.customer_segment in ('Champion', 'Loyal Customer') and lam.platform_consistency_score = 3)
            then true
            else false
        end as is_strategic_account,
        
        -- Intervention urgency
        case 
            when lam.action_priority = 5 then 'Immediate'
            when lam.action_priority = 4 then 'This Week'
            when lam.action_priority = 3 then 'This Month'
            else 'Routine'
        end as intervention_urgency,
        
        -- Expected retention rate by tier and lifecycle
        case 
            when lam.estimated_customer_ltv >= 8000 then 0.90  -- Platinum tier equivalent
            when lam.estimated_customer_ltv >= 5000 then 0.85  -- Gold tier equivalent
            when lam.estimated_customer_ltv >= 2500 and lam.lifecycle_stage not in ('Dormant') then 0.75  -- Silver tier equivalent
            when lam.estimated_customer_ltv >= 1000 and lam.lifecycle_stage in ('Growth', 'Maturity') then 0.60  -- Bronze tier equivalent
            else 0.45
        end as expected_retention_rate,
        
        -- Performance vs expectation
        case 
            when lam.retention_probability > 
                (case 
                    when lam.estimated_customer_ltv >= 8000 then 0.90
                    when lam.estimated_customer_ltv >= 5000 then 0.85
                    when lam.estimated_customer_ltv >= 2500 and lam.lifecycle_stage not in ('Dormant') then 0.75
                    when lam.estimated_customer_ltv >= 1000 and lam.lifecycle_stage in ('Growth', 'Maturity') then 0.60
                    else 0.45
                end) then 'Above Expectation'
            when lam.retention_probability >= 
                (case 
                    when lam.estimated_customer_ltv >= 8000 then 0.90
                    when lam.estimated_customer_ltv >= 5000 then 0.85
                    when lam.estimated_customer_ltv >= 2500 and lam.lifecycle_stage not in ('Dormant') then 0.75
                    when lam.estimated_customer_ltv >= 1000 and lam.lifecycle_stage in ('Growth', 'Maturity') then 0.60
                    else 0.45
                end * 0.8) then 'Meeting Expectation'
            else 'Below Expectation'
        end as performance_vs_expectation
        
    from lifecycle_advanced_metrics lam
)

select * from final_lifecycle_metrics
order by 
    is_strategic_account desc,
    action_priority desc,
    estimated_customer_ltv desc,
    customer_health_score desc
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 5001 | 5001 | 0 | 0 | 78 | 78 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"marketo_lead_id":"100","stripe_customer_id":"cus_005658","zendesk_user_id":"null"}</code> |
| K2 | <code>{"marketo_lead_id":"1239","stripe_customer_id":"null","zendesk_user_id":"3409"}</code> |
| K3 | <code>{"marketo_lead_id":"105","stripe_customer_id":"null","zendesk_user_id":"824"}</code> |
| K4 | <code>{"marketo_lead_id":"1018","stripe_customer_id":"cus_006759","zendesk_user_id":"3232"}</code> |
| K5 | <code>{"marketo_lead_id":"1003","stripe_customer_id":"cus_003355","zendesk_user_id":"null"}</code> |
| K6 | <code>{"marketo_lead_id":"1204","stripe_customer_id":"cus_003218","zendesk_user_id":"null"}</code> |
| K7 | <code>{"marketo_lead_id":"1124","stripe_customer_id":"cus_001676","zendesk_user_id":"null"}</code> |
| K8 | <code>{"marketo_lead_id":"1278","stripe_customer_id":"cus_006999","zendesk_user_id":"2526"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| marketo_lead_id | 0 | 0 | 0 | BIGINT | BIGINT |
| stripe_customer_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| zendesk_user_id | 0 | 0 | 0 | BIGINT | BIGINT |
| primary_email | 0 | 0 | 0 | VARCHAR | VARCHAR |
| primary_organization | 0 | 0 | 0 | VARCHAR | VARCHAR |
| customer_first_touchpoint | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| customer_last_activity | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| account_age_days | 0 | 0 | 0 | BIGINT | BIGINT |
| customer_segment | 0 | 0 | 0 | VARCHAR | VARCHAR |
| customer_journey_pattern | 0 | 0 | 0 | VARCHAR | VARCHAR |
| days_since_last_activity | 5001 | 5001 | 5001 | BIGINT | BIGINT |
| active_30_days | 0 | 0 | 0 | INTEGER | INTEGER |
| active_60_days | 7 | 7 | 7 | INTEGER | INTEGER |
| active_90_days | 127 | 127 | 127 | INTEGER | INTEGER |
| active_180_days | 622 | 622 | 622 | INTEGER | INTEGER |
| active_365_days | 1567 | 1567 | 1567 | INTEGER | INTEGER |
| lifecycle_stage | 622 | 622 | 622 | VARCHAR | VARCHAR |
| acquisition_cohort_month | 0 | 0 | 0 | DATE | DATE |
| platform_consistency_score | 0 | 0 | 0 | INTEGER | INTEGER |
| estimated_customer_value | 0 | 0 | 0 | DECIMAL(6,2) | DECIMAL(6,2) |
| frequency_score | 622 | 622 | 622 | INTEGER | INTEGER |
| recency_score | 622 | 622 | 622 | INTEGER | INTEGER |
| estimated_transaction_count | 2532 | 2532 | 2532 | DOUBLE | DOUBLE |
| customer_health_score | 622 | 622 | 622 | DECIMAL(15,2) | DECIMAL(15,2) |
| estimated_customer_ltv | 622 | 622 | 622 | DECIMAL(18,2) | DECIMAL(18,2) |
| churn_probability | 209 | 209 | 209 | DECIMAL(3,2) | DECIMAL(3,2) |
| revenue_at_risk | 209 | 209 | 209 | DECIMAL(9,2) | DECIMAL(9,2) |
| growth_potential | 622 | 622 | 622 | VARCHAR | VARCHAR |
| action_priority | 29 | 29 | 29 | INTEGER | INTEGER |
| acquisition_year | 0 | 0 | 0 | BIGINT | BIGINT |
| acquisition_month | 0 | 0 | 0 | BIGINT | BIGINT |
| months_since_acquisition | 5001 | 5001 | 5001 | BIGINT | BIGINT |
| acquisition_season | 0 | 0 | 0 | VARCHAR | VARCHAR |
| customer_tier | 534 | 534 | 534 | VARCHAR | VARCHAR |
| is_strategic_account | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| intervention_urgency | 29 | 29 | 29 | VARCHAR | VARCHAR |
| expected_retention_rate | 224 | 224 | 224 | DECIMAL(3,2) | DECIMAL(3,2) |
| performance_vs_expectation | 20 | 20 | 20 | VARCHAR | VARCHAR |

days_since_last_activity 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 1186 | 821 |

active_60_days 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | 0 | 1 |

active_90_days 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K3 | 0 | 1 |

active_180_days 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K4 | <code>[{"value":"0","rows":2}]</code> | <code>[{"value":"1","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

active_365_days 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K5 | 0 | 1 |

lifecycle_stage 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K4 | <code>[{"value":"Dormant","rows":2}]</code> | <code>[{"value":"Retention","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

frequency_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K4 | <code>[{"value":"1","rows":2}]</code> | <code>[{"value":"2","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

recency_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K4 | <code>[{"value":"1","rows":2}]</code> | <code>[{"value":"2","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

estimated_transaction_count 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K5 | 1.0 | 0.0 |

customer_health_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K4 | <code>[{"value":"1.80","rows":2}]</code> | <code>[{"value":"2.10","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

estimated_customer_ltv 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K4 | <code>[{"value":"780.00","rows":2}]</code> | <code>[{"value":"1638.00","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

churn_probability 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K4 | <code>[{"value":"0.80","rows":2}]</code> | <code>[{"value":"0.65","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

revenue_at_risk 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K4 | <code>[{"value":"400.00","rows":2}]</code> | <code>[{"value":"325.00","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

growth_potential 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K4 | <code>[{"value":"Reactivation Needed","rows":2}]</code> | <code>[{"value":"Monitor","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

action_priority 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K6 | 5 | 3 |

months_since_acquisition 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 39 | 27 |

customer_tier 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K4 | <code>[{"value":"Basic","rows":2}]</code> | <code>[{"value":"Bronze","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

intervention_urgency 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K6 | Immediate | This Month |

expected_retention_rate 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K7 | 0.45 | 0.75 |

performance_vs_expectation 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K8 | Above Expectation | Below Expectation |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>7列；[{"column":"active_30_days","value":"0"}]</code> |
| A4_equal_columns | <code>2组；[{"columns":["active_30_days","active_60_days","active_90_days","active_180_days","active_365_days"],"nonnull_equal_rows":5001,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>2组；[{"columns":["active_30_days","active_60_days","active_90_days","active_180_days","active_365_days"],"nonnull_equal_rows":5001,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| C9_agent_runtime_text | <code>S4:2 current_date；命中数=7</code> |
| C9_gold_runtime_text | <code>S5:39 current_date；命中数=11</code> |
| C9_contract_runtime_text | <code>S3:919 today；命中数=10</code> |
| D10_keyword_in_any_result_field | <code>命中数=2；task_instruction_not_agent_report       grain: One row per customer (from int_customer360__customer_lifecycle_metrics) with non-null primary_email</code> |

## 轨迹索引（不放输出原文）

本题事件总数：53；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -printf '%p %s bytes\n' &#124; sort; cat config/layer_dependencies.yaml</code> | 3128 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 11047 | true | false |
| 19 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br><br>put('intermediate','int_customer360__customer_behavior_analysis', '''<br>with matches as (<br>    select * from intermediate.int_customer360__source_matches<br>), joined as (<br>    sel</code> | 0 | false | false |
| 21 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br><br>put('intermediate','int_customer360__risk_assessment', '''<br>with behavior as (<br> select ba.*, lm.customer_health_score, lm.lifecycle_stage, lm.active_30_days, lm.active_90_day</code> | 0 | false | false |
| 25 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br><br>put('marts','customer360__customer_value_analysis', '''<br>with base as (<br> select *,case when estimated_customer_value&gt;=5000 then 5 when estimated_customer_value&gt;=3000 then 4 w</code> | 0 | false | false |
| 27 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br><br>put('marts','customer360__organization_network', '''<br>with entities as (<br> select ba.primary_email,ba.marketo_lead_id,ba.stripe_customer_id,ba.zendesk_user_id,ba.primary_organ</code> | 48 | false | false |
| 29 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -100 /tmp/runlog</code> | 7140 | true | false |
| 31 | run | <code>sed -i 's/m\.phone is not null or m\.mobile_phone is not null/phone is not null or mobile_phone is not null/' sql/intermediate/int_customer360__customer_behavior_analysis.sql &amp;&amp; python run.py &gt; /tmp/r</code> | 1493 | true | false |
| 33 | run | <code>grep -n ' m\.' sql/intermediate/int_customer360__customer_behavior_analysis.sql; grep -n -A6 -B4 'ERROR - ✗ intermediate.int_customer360__customer_behavior_analysis' /tmp/runlog</code> | 1764 | true | false |
| 35 | run | <code>sed -i -e 's/m\.country_code/country_code/g' -e 's/m\.state_code/state_code/g' -e 's/m\.city/city/g' sql/intermediate/int_customer360__customer_behavior_analysis.sql; python run.py &gt; /tmp/runlog 2&gt;&amp;1;</code> | 1493 | true | false |
| 37 | run | <code>grep -nE 's\.&#124;z\.' sql/intermediate/int_customer360__customer_behavior_analysis.sql</code> | 1249 | false | false |
| 39 | run | <code>sed -i -e 's/s\.customer_address_line_1/customer_address_line_1/g' -e 's/s\.customer_country_code/customer_country_code/g' -e 's/z\.organization_id/organization_id/g' sql/intermediate/int_customer360_</code> | 394 | false | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('customer360.duckdb',read_only=True)<br>checks={<br>'status_key_dups':"select count(*) from (select customer360_id from marts.customer360__status group by 1 ha</code> | 616 | true | false |

### agent action 的 thought/message 命中原句

event 19 / message

```text
put('intermediate','int_customer360__customer_lifecycle_metrics', '''
```
event 21 / message

```text
 left join intermediate.int_customer360__customer_lifecycle_metrics lm using (primary_email)
```
event 25 / message

```text
 from intermediate.int_customer360__customer_lifecycle_metrics
```
event 25 / message

```text
 left join intermediate.int_customer360__customer_lifecycle_metrics lm using(primary_email)
```
event 27 / message

```text
 left join intermediate.int_customer360__customer_lifecycle_metrics lm using(primary_email)
```
event 27 / message

```text
 from intermediate.int_customer360__customer_behavior_analysis ba left join intermediate.int_customer360__customer_lifecycle_metrics lm using(primary_email)
```
event 45 / message

```text
for s,t in [('intermediate','int_customer360__marketo'),('intermediate','int_customer360__stripe'),('intermediate','int_customer360__zendesk'),('intermediate','int_customer360__source_matches'),('intermediate','int_customer360__customer_behavior_analysis'),('intermediate','int_customer360__customer_lifecycle_metrics'),('intermediate','int_customer360__risk_assessment'),('marts','customer360__mapping'),('marts','customer360__status'),('marts','customer360__updates')]: print(s+'.'+t,c.execute(f'select count(*) from {s}.{t}').fetchone()[0])
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-003.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-003/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/intermediate/int_customer360__customer_lifecycle_metrics.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/sql/intermediate/int_customer360__customer_lifecycle_metrics.sql`
- S6: `records/006_contract_impl-003.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/result.md`
- S10: `data/019_packages_work/019_impl-003_int_customer360__customer_lifecycle_metrics/019_impl-003_int_customer360__customer_lifecycle_metrics.json`
- S11: `data/005_cs_work/impl-003/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/customer360.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions`
