# impl-003 | marts | customer360__customer_activity_metrics | 差异：S1；日期 原记录

## 契约完整原文

S3:1481–1662

```yaml
    - name: customer360__customer_activity_metrics
      description: Customer activity and engagement metrics across marketing, sales, and support with recency, velocity, depth, risk, and intervention signals
      grain: One row per primary_email
      source_models:
      - intermediate.int_customer360__customer_behavior_analysis
      - intermediate.int_customer360__customer_lifecycle_metrics
      - intermediate.int_customer360__marketo
      - intermediate.int_customer360__stripe
      - intermediate.int_customer360__zendesk
      business_logic: 'Overview - Start from behavior_analysis (intermediate.int_customer360__customer_behavior_analysis, one row per customer) and left join lifecycle_metrics (intermediate.int_customer360__customer_lifecycle_metrics) on primary_email. - Enrich with platform data via left joins on platform IDs: - Marketo: intermediate.int_customer360__marketo on lead_id - Stripe: intermediate.int_customer360__stripe on customer_id - Zendesk: intermediate.int_customer360__zendesk on user_id - Filter: exclude rows where primary_email is NULL; no de-duplication beyond joins. - Time anchors: current_date for recency calculations and current_timestamp for activity_analysis_timestamp; results vary by execution time. - Ordering: rows are sorted by activity_priority_score (desc), then weighted_engagement_score (desc), then active_channel_count (desc). Activity recency and counts - days/weeks/months_since_last_activity: difference between customer_last_activity and current_date by unit; returns NULL if customer_last_activity is NULL. - active_channel_count: integer sum (in_marketo + in_stripe + in_zendesk); if any flag is NULL the sum becomes NULL; expected domain is 0–3 from 0/1 flags. Estimated and adjusted activity (stochastic components) - estimated_monthly_activities: simulated with random() per run based on composite_engagement_score: - >=4.0 → 15 + floor(random()*10) ∈ [15,24] - >=3.0 → 8 + floor(random()*7) ∈ [8,14] - >=2.0 → 3 + floor(random()*5) ∈ [3,7] - >=1.0 → 1 + floor(random()*3) ∈ [1,3] - else → floor(random()*2) ∈ [0,1] - Note: random() yields different results each execution; this column is non-deterministic by design. - seasonally_adjusted_activity: estimated_monthly_activities multiplied by a month factor (Nov/Dec/Jan ×1.2; Jun/Jul/Aug ×0.8; else ×1.0); no rounding. - predicted_next_month_activity: estimated_monthly_activities multiplied by a factor from engagement_velocity category (Accelerating ×1.3; Steady High ×1.1; Steady Medium ×1.0; Declining ×0.7; Slow ×0.4; Stagnant ×0.2); no rounding. Engagement velocity, momentum, maturity (rule-based categories) - engagement_velocity (uses activity recency and composite_engagement_score): - <=7 days and score>=3.0 → Accelerating - <=14 days and score>=2.5 → Steady High - <=30 days and score>=2.0 → Steady Medium - <=60 days → Declining - <=90 days → Slow - else → Stagnant - activity_momentum (uses days_since_last_activity and composite_engagement_score): - <=7 days and score>=3.5 → High Momentum - <=14 days and score>=3.0 → Medium Momentum - <=30 days and score>=2.0 → Low Momentum - <=60 days → Losing Momentum - else → No Momentum - engagement_maturity (uses account_age_days and active_channel_count): - age>=365 and channels>=3 → Mature Multi-channel - age>=180 and channels>=2 → Developing Multi-channel - age>=90 and channels>=1 → Single Channel Engaged - age<90 → Early Stage - else → Minimal Engagement Channel scores and depths - marketing_engagement_score: if in_marketo=1 and is_unsubscribed=false and is_email_invalid=false then round(marketo_engagement × (1 − days since last Marketo update / 90), 2); else 0; may be negative; if the last update timestamp is NULL the result is NULL in the true branch. - sales_engagement_score: if in_stripe=1 and is_deleted=false and is_delinquent=false then round(stripe_engagement × (1 − days since last Stripe update / 60), 2); else 0; may be negative; NULL if the last update timestamp is NULL in the true branch. - support_engagement_score: if in_zendesk=1 and is_active=true and is_suspended=false and is_deleted=false then round(zendesk_engagement × (1 − days since last Zendesk update / 120), 2); else 0; may be negative; NULL if the last update timestamp is NULL in the true branch. - primary_engagement_channel: choose the channel with the highest raw engagement; ties break in order Marketing Driven > Sales Driven > Support Driven; if comparisons do not resolve (e.g., NULL inputs) fallback is Balanced. - marketing_depth/sales_depth/support_depth (per channel): if in_* = 1: engagement>=4 → Deep; engagement>=2 → Medium; else → Shallow; if in_*=0 → None. Cross-platform and composite scores - cross_platform_consistency: round( average of raw engagement across platforms where in_*=1, 2 decimals ); returns NULL if no active platforms or if any included operand (flags or raw engagements) is NULL. - activity_efficiency: round(composite_engagement_score divided by active_channel_count, 2); NULL if active_channel_count is 0 or NULL. - weighted_engagement_score: round(0.3×marketing_engagement_score (NULL→0) + 0.5×sales_engagement_score (NULL→0) + 0.2×support_engagement_score (NULL→0), 2); can be negative. - activity_grade: from weighted_engagement_score and active_channel_count: >=4.0 & channels>=3 → A+; >=3.5 & channels>=2 → A; >=3.0 → B+; >=2.5 → B; >=2.0 → C+; >=1.5 → C; >=1.0 → D; else → F. - activity_priority_score: round(0.4×weighted_engagement_score + 0.3×active_channel_count + 0.3×priority_component, 2) where priority_component is 5/4/3/2/1 by recency+composite rules (<=7 days & score>=3.5 → 5; <=14 & score>=3.0 → 4; <=30 & score>=2.0 → 3; <=60 → 2; else → 1). Risk and interventions - activity_risk_level: if days_since_last_activity>90 and customer_health_score<3.0 → High Activity Risk; else if days_since_last_activity>60 or active_channel_count=1 → Medium Activity Risk; else if days_since_last_activity>30 → Low Activity Risk; else → No Activity Risk. - recommended_activity_intervention (evaluated top-to-bottom): Declining/Slow/Stagnant with health>=3.0 → Re-engagement Campaign; else single channel (count=1) with composite>=2.5 → Channel Expansion; else Marketing Driven with in_stripe=0 → Sales Conversion Focus; else Sales Driven with in_zendesk=0 → Success Onboarding; else recent (<=7 days) with composite>=3.5 → Upsell Opportunity; else Standard Engagement.'
      columns:
      - name: marketo_lead_id
        data_type: BIGINT
        description: Marketo lead identifier sourced from behavior_analysis; may be NULL if not matched
      - name: stripe_customer_id
        data_type: VARCHAR
        description: Stripe customer identifier sourced from behavior_analysis; may be NULL if not matched
      - name: zendesk_user_id
        data_type: BIGINT
        description: Zendesk user identifier sourced from behavior_analysis; may be NULL if not matched
      - name: primary_email
        data_type: VARCHAR
        description: Customer email key; rows with NULL are excluded from output; grain is one row per primary_email
      - name: primary_organization
        data_type: VARCHAR
        description: Customer organization from behavior_analysis; passthrough value
      - name: customer_segment
        data_type: VARCHAR
        description: Customer segment from behavior_analysis; passthrough value
      - name: customer_journey_pattern
        data_type: VARCHAR
        description: Journey pattern label from behavior_analysis; passthrough value
      - name: lifecycle_stage
        data_type: VARCHAR
        description: Lifecycle stage from lifecycle_metrics joined on primary_email; may be NULL
      - name: composite_engagement_score
        data_type: DECIMAL(14,1)
        description: Base composite engagement score from behavior_analysis; used by multiple downstream rules without further rounding
      - name: weighted_engagement_score
        data_type: DOUBLE
        description: 0.3*marketing_engagement_score + 0.5*sales_engagement_score + 0.2*support_engagement_score rounded to 2 decimals; NULL channel scores treated as 0; may be negative
      - name: customer_health_score
        data_type: DECIMAL(15,2)
        description: Health score from lifecycle_metrics; passthrough value used in risk and intervention logic
      - name: activity_grade
        data_type: VARCHAR
        description: 'Letter grade from weighted_engagement_score and active_channel_count with thresholds: A+, A, B+, B, C+, C, D, F as defined in Business Logic'
      - name: activity_priority_score
        data_type: DOUBLE
        description: 'Priority score rounded to 2 decimals: 0.4*weighted_engagement_score + 0.3*active_channel_count + 0.3*recency_component (5–1) per rules'
      - name: days_since_last_activity
        data_type: BIGINT
        description: Number of days between customer_last_activity and current_date; NULL if customer_last_activity is NULL
      - name: weeks_since_last_activity
        data_type: BIGINT
        description: Number of weeks between customer_last_activity and current_date; NULL if customer_last_activity is NULL
      - name: months_since_last_activity
        data_type: BIGINT
        description: Number of months between customer_last_activity and current_date; NULL if customer_last_activity is NULL
      - name: account_age_days
        data_type: BIGINT
        description: Account age in days from behavior_analysis; passthrough value used in maturity logic
      - name: active_channel_count
        data_type: INTEGER
        description: Sum of in_marketo + in_stripe + in_zendesk (expected 0–3); NULL if any flag is NULL
      - name: primary_engagement_channel
        data_type: VARCHAR
        description: Channel with highest raw engagement; ties break Marketing Driven > Sales Driven > Support Driven; fallback Balanced when comparisons cannot be resolved (e.g., NULL inputs)
      - name: marketing_engagement_score
        data_type: DOUBLE
        description: If in_marketo=1 and not unsubscribed/invalid then mark_engagement×(1 − days since last update/90) rounded to 2 decimals; else 0; may be negative or NULL if updated_at is NULL in the true branch
      - name: sales_engagement_score
        data_type: DOUBLE
        description: If in_stripe=1 and not deleted and not delinquent then stripe_engagement×(1 − days since last update/60) rounded to 2 decimals; else 0; may be negative or NULL if updated_at is NULL in the true branch
      - name: support_engagement_score
        data_type: DOUBLE
        description: If in_zendesk=1 and active and not suspended/deleted then zendesk_engagement×(1 − days since last update/120) rounded to 2 decimals; else 0; may be negative or NULL if updated_at is NULL in the true branch
      - name: marketing_depth
        data_type: VARCHAR
        description: 'Depth within Marketo: if in_marketo=1 then engagement>=4 Deep, >=2 Medium, else Shallow; if in_marketo=0 then None'
      - name: sales_depth
        data_type: VARCHAR
        description: 'Depth within Stripe: if in_stripe=1 then engagement>=4 Deep, >=2 Medium, else Shallow; if in_stripe=0 then None'
      - name: support_depth
        data_type: VARCHAR
        description: 'Depth within Zendesk: if in_zendesk=1 then engagement>=4 Deep, >=2 Medium, else Shallow; if in_zendesk=0 then None'
      - name: engagement_velocity
        data_type: VARCHAR
        description: 'Velocity category from recency and composite_engagement_score: Accelerating, Steady High, Steady Medium, Declining, Slow, or Stagnant per thresholds'
      - name: activity_momentum
        data_type: VARCHAR
        description: 'Momentum category from days_since_last_activity and composite_engagement_score: High/Medium/Low Momentum, Losing Momentum, or No Momentum per thresholds'
      - name: engagement_maturity
        data_type: VARCHAR
        description: 'Maturity category from account_age_days and active_channel_count: Mature Multi-channel, Developing Multi-channel, Single Channel Engaged, Early Stage, or Minimal Engagement'
      - name: estimated_monthly_activities
        data_type: DOUBLE
        description: Simulated integer in defined ranges using random() and composite_engagement_score; stochastic and varies each run
      - name: predicted_next_month_activity
        data_type: DOUBLE
        description: Estimated future activity = estimated_monthly_activities × factor from engagement_velocity (1.3/1.1/1.0/0.7/0.4/0.2); not rounded
      - name: seasonally_adjusted_activity
        data_type: DOUBLE
        description: 'Estimated_monthly_activities adjusted by month: Nov–Jan ×1.2, Jun–Aug ×0.8, else ×1.0; not rounded'
      - name: active_30_days
        data_type: INTEGER
        description: Activity metric for last 30 days from lifecycle_metrics; passthrough
      - name: active_60_days
        data_type: INTEGER
        description: Activity metric for last 60 days from lifecycle_metrics; passthrough
      - name: active_90_days
        data_type: INTEGER
        description: Activity metric for last 90 days from lifecycle_metrics; passthrough
      - name: active_180_days
        data_type: INTEGER
        description: Activity metric for last 180 days from lifecycle_metrics; passthrough
      - name: active_365_days
        data_type: INTEGER
        description: Activity metric for last 365 days from lifecycle_metrics; passthrough
      - name: activity_risk_level
        data_type: VARCHAR
        description: 'Risk category from days_since_last_activity, customer_health_score, and active_channel_count: High/Medium/Low/No Activity Risk per rules'
      - name: cross_platform_consistency
        data_type: DOUBLE
        description: Average of raw engagement across active platforms (in_*=1) rounded to 2 decimals; NULL if no active platforms or any included operand is NULL
      - name: activity_efficiency
        data_type: DOUBLE
        description: Composite_engagement_score divided by active_channel_count rounded to 2 decimals; NULL if denominator is 0 or NULL
      - name: recommended_activity_intervention
        data_type: VARCHAR
        description: 'Intervention label evaluated in order: Re-engagement Campaign, Channel Expansion, Sales Conversion Focus, Success Onboarding, Upsell Opportunity, else Standard Engagement'
      - name: in_marketo
        data_type: INTEGER
        description: Channel presence flag from behavior_analysis (expected 0/1); used in counts and conditional logic; may be NULL
      - name: in_stripe
        data_type: INTEGER
        description: Channel presence flag from behavior_analysis (expected 0/1); used in counts and conditional logic; may be NULL
      - name: in_zendesk
        data_type: INTEGER
        description: Channel presence flag from behavior_analysis (expected 0/1); used in counts and conditional logic; may be NULL
      - name: is_unsubscribed
        data_type: BOOLEAN
        description: Marketo unsubscribe flag from platform data; influences marketing_engagement_score
      - name: is_email_invalid
        data_type: BOOLEAN
        description: Marketo invalid email flag from platform data; influences marketing_engagement_score
      - name: do_not_call
        data_type: BOOLEAN
        description: Marketo do-not-call flag from platform data; passthrough
      - name: is_delinquent
        data_type: BOOLEAN
        description: Stripe delinquency flag from platform data; influences sales_engagement_score
      - name: stripe_deleted
        data_type: BOOLEAN
        description: Stripe deletion flag from platform data; influences sales_engagement_score
      - name: zendesk_active
        data_type: BOOLEAN
        description: Zendesk active flag from platform data; required true for support_engagement_score to be computed
      - name: zendesk_suspended
        data_type: BOOLEAN
        description: Zendesk suspended flag from platform data; must be false for support_engagement_score to be computed
      - name: zendesk_deleted
        data_type: BOOLEAN
        description: Zendesk deletion flag from platform data; must be false for support_engagement_score to be computed
      - name: customer_first_touchpoint
        data_type: TIMESTAMP
        description: First touch timestamp from behavior_analysis; passthrough
      - name: customer_last_activity
        data_type: TIMESTAMP
        description: Most recent activity timestamp from behavior_analysis; drives recency metrics
      - name: marketo_registration_date
        data_type: TIMESTAMP
        description: Marketo created_at from platform data; passthrough
      - name: stripe_registration_date
        data_type: TIMESTAMP
        description: Stripe created_at from platform data; passthrough
      - name: zendesk_registration_date
        data_type: TIMESTAMP
        description: Zendesk created_at from platform data; passthrough
      - name: activity_analysis_timestamp
        data_type: TIMESTAMP WITH TIME ZONE
        description: Current timestamp at model execution time; changes each run and reflects generation time
```

## agent 最终 SQL

S4

```sql
with base as (
 select ba.*,lm.lifecycle_stage,lm.customer_health_score,lm.active_30_days,lm.active_60_days,lm.active_90_days,lm.active_180_days,lm.active_365_days,lm.account_age_days,
 m.is_unsubscribed,m.is_email_invalid,m.do_not_call,m.updated_at as m_updated,s.is_delinquent,s.is_deleted as stripe_deleted,s.updated_at as s_updated,
 z.is_active as zendesk_active,z.is_suspended as zendesk_suspended,z.is_deleted as zendesk_deleted,z.updated_at as z_updated,
 m.created_at as marketo_registration_date,s.created_at as stripe_registration_date,z.created_at as zendesk_registration_date,
 m.email as m_email,s.email as s_email,z.email as z_email
 from intermediate.int_customer360__customer_behavior_analysis ba
 left join intermediate.int_customer360__customer_lifecycle_metrics lm using(primary_email)
 left join intermediate.int_customer360__marketo m on ba.marketo_lead_id=m.lead_id
 left join intermediate.int_customer360__stripe s on ba.stripe_customer_id=s.customer_id
 left join intermediate.int_customer360__zendesk z on ba.zendesk_user_id=z.user_id
 where ba.primary_email is not null
), recency as (
 select *,date_diff('day',customer_last_activity,current_date)::bigint as days_since_last_activity,
 (in_marketo+in_stripe+in_zendesk)::integer as active_channel_count,
 case when customer_last_activity is null then null else date_diff('week',customer_last_activity,current_date)::bigint end as weeks_since_last_activity,
 case when customer_last_activity is null then null else date_diff('month',customer_last_activity,current_date)::bigint end as months_since_last_activity
 from base
), channels as (
 select *,case when in_marketo=1 and is_unsubscribed=false and is_email_invalid=false then round(marketo_engagement*(1-date_diff('day',m_updated,current_timestamp)/90.0),2) else 0 end as marketing_engagement_score,
 case when in_stripe=1 and stripe_deleted=false and is_delinquent=false then round(stripe_engagement*(1-date_diff('day',s_updated,current_timestamp)/60.0),2) else 0 end as sales_engagement_score,
 case when in_zendesk=1 and zendesk_active=true and zendesk_suspended=false and zendesk_deleted=false then round(zendesk_engagement*(1-date_diff('day',z_updated,current_timestamp)/120.0),2) else 0 end as support_engagement_score,
 case when days_since_last_activity<=7 and composite_engagement_score>=3 then 'Accelerating' when days_since_last_activity<=14 and composite_engagement_score>=2.5 then 'Steady High'
 when days_since_last_activity<=30 and composite_engagement_score>=2 then 'Steady Medium' when days_since_last_activity<=60 then 'Declining' when days_since_last_activity<=90 then 'Slow' else 'Stagnant' end as engagement_velocity,
 case when days_since_last_activity<=7 and composite_engagement_score>=3.5 then 'High Momentum' when days_since_last_activity<=14 and composite_engagement_score>=3 then 'Medium Momentum'
 when days_since_last_activity<=30 and composite_engagement_score>=2 then 'Low Momentum' when days_since_last_activity<=60 then 'Losing Momentum' else 'No Momentum' end as activity_momentum
 from recency
), scores as (
 select *,round(coalesce(marketing_engagement_score,0)*.3+coalesce(sales_engagement_score,0)*.5+coalesce(support_engagement_score,0)*.2,2) as weighted_engagement_score,
 case when marketing_engagement_score>=sales_engagement_score and marketing_engagement_score>=support_engagement_score then 'Marketing Driven'
 when sales_engagement_score>=support_engagement_score then 'Sales Driven' when support_engagement_score is not null then 'Support Driven' else 'Balanced' end as primary_engagement_channel,
 case when in_marketo=1 then case when marketo_engagement>=4 then 'Deep' when marketo_engagement>=2 then 'Medium' else 'Shallow' end else 'None' end as marketing_depth,
 case when in_stripe=1 then case when stripe_engagement>=4 then 'Deep' when stripe_engagement>=2 then 'Medium' else 'Shallow' end else 'None' end as sales_depth,
 case when in_zendesk=1 then case when zendesk_engagement>=4 then 'Deep' when zendesk_engagement>=2 then 'Medium' else 'Shallow' end else 'None' end as support_depth,
 case when account_age_days>=365 and active_channel_count>=3 then 'Mature Multi-channel' when account_age_days>=180 and active_channel_count>=2 then 'Developing Multi-channel'
 when account_age_days>=90 and active_channel_count>=1 then 'Single Channel Engaged' when account_age_days<90 then 'Early Stage' else 'Minimal Engagement' end as engagement_maturity,
 case when composite_engagement_score>=4 then 15+floor(random()*10) when composite_engagement_score>=3 then 8+floor(random()*7) when composite_engagement_score>=2 then 3+floor(random()*5) when composite_engagement_score>=1 then 1+floor(random()*3) else floor(random()*2) end as estimated_monthly_activities
 from channels
), final_scores as (
 select *,round(composite_engagement_score/nullif(active_channel_count,0),2) as activity_efficiency,
 round(case when in_marketo=1 then marketo_engagement else 0 end + case when in_stripe=1 then stripe_engagement else 0 end + case when in_zendesk=1 then zendesk_engagement else 0 end,2) as cross_platform_consistency,
 case when weighted_engagement_score>=4 and active_channel_count>=3 then 'A+' when weighted_engagement_score>=3.5 and active_channel_count>=2 then 'A' when weighted_engagement_score>=3 then 'B+' when weighted_engagement_score>=2.5 then 'B' when weighted_engagement_score>=2 then 'C+' when weighted_engagement_score>=1.5 then 'C' when weighted_engagement_score>=1 then 'D' else 'F' end as activity_grade,
 round(.4*weighted_engagement_score+.3*active_channel_count+.3*case when days_since_last_activity<=7 and composite_engagement_score>=3.5 then 5 when days_since_last_activity<=14 and composite_engagement_score>=3 then 4 when days_since_last_activity<=30 and composite_engagement_score>=2 then 3 when days_since_last_activity<=60 then 2 else 1 end,2) as activity_priority_score
 from scores
)
select marketo_lead_id,stripe_customer_id,zendesk_user_id,primary_email,primary_organization,customer_segment,customer_journey_pattern,lifecycle_stage,composite_engagement_score,
 weighted_engagement_score,customer_health_score,activity_grade,activity_priority_score,days_since_last_activity,weeks_since_last_activity,months_since_last_activity,account_age_days,active_channel_count,
 primary_engagement_channel,marketing_engagement_score,sales_engagement_score,support_engagement_score,marketing_depth,sales_depth,support_depth,engagement_velocity,activity_momentum,engagement_maturity,
 estimated_monthly_activities,
 estimated_monthly_activities*case engagement_velocity when 'Accelerating' then 1.3 when 'Steady High' then 1.1 when 'Steady Medium' then 1.0 when 'Declining' then .7 when 'Slow' then .4 else .2 end as predicted_next_month_activity,
 estimated_monthly_activities*case when month(current_date) in (11,12,1) then 1.2 when month(current_date) in (6,7,8) then .8 else 1 end as seasonally_adjusted_activity,
 active_30_days,active_60_days,active_90_days,active_180_days,active_365_days,
 case when days_since_last_activity>90 and customer_health_score<3 then 'High Activity Risk' when days_since_last_activity>60 or active_channel_count=1 then 'Medium Activity Risk' when days_since_last_activity>30 then 'Low Activity Risk' else 'No Activity Risk' end as activity_risk_level,
 cross_platform_consistency,activity_efficiency,
 case when engagement_velocity in ('Declining','Slow','Stagnant') and customer_health_score>=3 then 'Re-engagement Campaign' when active_channel_count=1 and composite_engagement_score>=2.5 then 'Channel Expansion'
 when primary_engagement_channel='Marketing Driven' and in_stripe=0 then 'Sales Conversion Focus' when primary_engagement_channel='Sales Driven' and in_zendesk=0 then 'Success Onboarding'
 when days_since_last_activity<=7 and composite_engagement_score>=3.5 then 'Upsell Opportunity' else 'Standard Engagement' end as recommended_activity_intervention,
 in_marketo,in_stripe,in_zendesk,is_unsubscribed,is_email_invalid,do_not_call,is_delinquent,stripe_deleted,zendesk_active,zendesk_suspended,zendesk_deleted,
 customer_first_touchpoint,customer_last_activity,marketo_registration_date,stripe_registration_date,zendesk_registration_date,current_timestamp as activity_analysis_timestamp
from final_scores
```

## gold SQL（仅供定位差异）

S5

```sql
-- Customer activity and engagement metrics across all touchpoints
-- Multi-dimensional activity analysis including daily, weekly, monthly engagement patterns

with behavior_analysis as (
    select * from intermediate.int_customer360__customer_behavior_analysis
),

lifecycle_metrics as (
    select * from intermediate.int_customer360__customer_lifecycle_metrics
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

-- Activity pattern analysis
activity_patterns as (
    select 
        ba.marketo_lead_id,
        ba.stripe_customer_id,
        ba.zendesk_user_id,
        ba.primary_email,
        ba.primary_organization,
        ba.customer_segment,
        ba.customer_journey_pattern,
        ba.customer_first_touchpoint,
        ba.customer_last_activity,
        ba.account_age_days,
        ba.composite_engagement_score,
        
        lm.lifecycle_stage,
        lm.customer_health_score,
        lm.active_30_days,
        lm.active_60_days,
        lm.active_90_days,
        lm.active_180_days,
        lm.active_365_days,
        
        -- Platform-specific activity indicators
        ba.in_marketo,
        ba.in_stripe,
        ba.in_zendesk,
        ba.marketo_engagement,
        ba.stripe_engagement,
        ba.zendesk_engagement,
        
        -- Activity recency metrics
        datediff('day', ba.customer_last_activity, current_date) as days_since_last_activity,
        datediff('week', ba.customer_last_activity, current_date) as weeks_since_last_activity,
        datediff('month', ba.customer_last_activity, current_date) as months_since_last_activity,
        
        -- Activity frequency estimation (simulated based on engagement patterns)
        case 
            when ba.composite_engagement_score >= 4.0 then 15 + floor(random() * 10)  -- 15-24 activities
            when ba.composite_engagement_score >= 3.0 then 8 + floor(random() * 7)   -- 8-14 activities
            when ba.composite_engagement_score >= 2.0 then 3 + floor(random() * 5)   -- 3-7 activities
            when ba.composite_engagement_score >= 1.0 then 1 + floor(random() * 3)   -- 1-3 activities
            else floor(random() * 2)  -- 0-1 activities
        end as estimated_monthly_activities,
        
        -- Engagement velocity (activity trend)
        case 
            when datediff('day', ba.customer_last_activity, current_date) <= 7 and ba.composite_engagement_score >= 3.0 then 'Accelerating'
            when datediff('day', ba.customer_last_activity, current_date) <= 14 and ba.composite_engagement_score >= 2.5 then 'Steady High'
            when datediff('day', ba.customer_last_activity, current_date) <= 30 and ba.composite_engagement_score >= 2.0 then 'Steady Medium'
            when datediff('day', ba.customer_last_activity, current_date) <= 60 then 'Declining'
            when datediff('day', ba.customer_last_activity, current_date) <= 90 then 'Slow'
            else 'Stagnant'
        end as engagement_velocity,
        
        -- Activity consistency score
        round(
            (case when ba.in_marketo = 1 then ba.marketo_engagement else 0 end +
             case when ba.in_stripe = 1 then ba.stripe_engagement else 0 end +
             case when ba.in_zendesk = 1 then ba.zendesk_engagement else 0 end) /
            nullif((ba.in_marketo + ba.in_stripe + ba.in_zendesk), 0), 2
        ) as cross_platform_consistency
        
    from behavior_analysis ba
    left join lifecycle_metrics lm 
        on ba.primary_email = lm.primary_email
),

-- Platform-specific engagement deep dive
platform_engagement_analysis as (
    select 
        ap.*,
        m.created_at as marketo_registration_date,
        m.updated_at as marketo_last_update,
        m.is_unsubscribed,
        m.is_email_invalid,
        m.do_not_call,
        
        s.created_at as stripe_registration_date,
        s.updated_at as stripe_last_update,
        s.is_delinquent,
        s.is_deleted as stripe_deleted,
        
        z.created_at as zendesk_registration_date,
        z.updated_at as zendesk_last_update,
        z.is_active as zendesk_active,
        z.is_suspended as zendesk_suspended,
        z.is_deleted as zendesk_deleted,
        
        -- Marketing engagement metrics
        case 
            when ap.in_marketo = 1 then
                case 
                    when m.is_unsubscribed = false and m.is_email_invalid = false then
                        round(ap.marketo_engagement * 
                              (1.0 - datediff('day', m.updated_at, current_date) / 90.0), 2)
                    else 0
                end
            else 0
        end as marketing_engagement_score,
        
        -- Sales engagement metrics (Stripe activity)
        case 
            when ap.in_stripe = 1 then
                case 
                    when s.is_deleted = false and s.is_delinquent = false then
                        round(ap.stripe_engagement * 
                              (1.0 - datediff('day', s.updated_at, current_date) / 60.0), 2)
                    else 0
                end
            else 0
        end as sales_engagement_score,
        
        -- Support engagement metrics (Zendesk activity)
        case 
            when ap.in_zendesk = 1 then
                case 
                    when z.is_active = true and z.is_suspended = false and z.is_deleted = false then
                        round(ap.zendesk_engagement * 
                              (1.0 - datediff('day', z.updated_at, current_date) / 120.0), 2)
                    else 0
                end
            else 0
        end as support_engagement_score,
        
        -- Channel preference analysis
        case 
            when ap.marketo_engagement >= ap.stripe_engagement and ap.marketo_engagement >= ap.zendesk_engagement then 'Marketing Driven'
            when ap.stripe_engagement >= ap.marketo_engagement and ap.stripe_engagement >= ap.zendesk_engagement then 'Sales Driven'
            when ap.zendesk_engagement >= ap.marketo_engagement and ap.zendesk_engagement >= ap.stripe_engagement then 'Support Driven'
            else 'Balanced'
        end as primary_engagement_channel,
        
        -- Activity breadth (number of active channels)
        (ap.in_marketo + ap.in_stripe + ap.in_zendesk) as active_channel_count,
        
        -- Engagement depth within each channel
        case 
            when ap.in_marketo = 1 and ap.marketo_engagement >= 4 then 'Deep'
            when ap.in_marketo = 1 and ap.marketo_engagement >= 2 then 'Medium'
            when ap.in_marketo = 1 then 'Shallow'
            else 'None'
        end as marketing_depth,
        
        case 
            when ap.in_stripe = 1 and ap.stripe_engagement >= 4 then 'Deep'
            when ap.in_stripe = 1 and ap.stripe_engagement >= 2 then 'Medium'
            when ap.in_stripe = 1 then 'Shallow'
            else 'None'
        end as sales_depth,
        
        case 
            when ap.in_zendesk = 1 and ap.zendesk_engagement >= 4 then 'Deep'
            when ap.in_zendesk = 1 and ap.zendesk_engagement >= 2 then 'Medium'
            when ap.in_zendesk = 1 then 'Shallow'
            else 'None'
        end as support_depth
        
    from activity_patterns ap
    left join marketo_data m on ap.marketo_lead_id = m.lead_id
    left join stripe_data s on ap.stripe_customer_id = s.customer_id
    left join zendesk_data z on ap.zendesk_user_id = z.user_id
),

-- Advanced activity metrics
advanced_activity_metrics as (
    select 
        pea.*,
        
        -- Comprehensive engagement score (weighted across all channels)
        round(
            (case when pea.marketing_engagement_score is not null then pea.marketing_engagement_score else 0 end * 0.3 +
             case when pea.sales_engagement_score is not null then pea.sales_engagement_score else 0 end * 0.5 +
             case when pea.support_engagement_score is not null then pea.support_engagement_score else 0 end * 0.2), 2
        ) as weighted_engagement_score,
        
        -- Activity momentum (trend analysis)
        case 
            when pea.days_since_last_activity <= 7 and pea.composite_engagement_score >= 3.5 then 'High Momentum'
            when pea.days_since_last_activity <= 14 and pea.composite_engagement_score >= 3.0 then 'Medium Momentum'
            when pea.days_since_last_activity <= 30 and pea.composite_engagement_score >= 2.0 then 'Low Momentum'
            when pea.days_since_last_activity <= 60 then 'Losing Momentum'
            else 'No Momentum'
        end as activity_momentum,
        
        -- Engagement maturity
        case 
            when pea.account_age_days >= 365 and pea.active_channel_count >= 3 then 'Mature Multi-channel'
            when pea.account_age_days >= 180 and pea.active_channel_count >= 2 then 'Developing Multi-channel'
            when pea.account_age_days >= 90 and pea.active_channel_count >= 1 then 'Single Channel Engaged'
            when pea.account_age_days < 90 then 'Early Stage'
            else 'Minimal Engagement'
        end as engagement_maturity,
        
        -- Seasonal activity patterns (simulated)
        case 
            when extract(month from current_date) in (11, 12, 1) then
                pea.estimated_monthly_activities * 1.2  -- Holiday boost
            when extract(month from current_date) in (6, 7, 8) then
                pea.estimated_monthly_activities * 0.8  -- Summer slowdown
            else 
                pea.estimated_monthly_activities
        end as seasonally_adjusted_activity,
        
        -- Activity efficiency score (engagement per channel)
        round(
            pea.composite_engagement_score / nullif(pea.active_channel_count, 0), 2
        ) as activity_efficiency,
        
        -- Predicted future activity level
        case 
            when pea.engagement_velocity = 'Accelerating' then 
                pea.estimated_monthly_activities * 1.3
            when pea.engagement_velocity = 'Steady High' then 
                pea.estimated_monthly_activities * 1.1
            when pea.engagement_velocity = 'Steady Medium' then 
                pea.estimated_monthly_activities * 1.0
            when pea.engagement_velocity = 'Declining' then 
                pea.estimated_monthly_activities * 0.7
            when pea.engagement_velocity = 'Slow' then 
                pea.estimated_monthly_activities * 0.4
            else 
                pea.estimated_monthly_activities * 0.2
        end as predicted_next_month_activity,
        
        -- Activity risk indicators
        case 
            when pea.days_since_last_activity > 90 and pea.customer_health_score < 3.0 then 'High Activity Risk'
            when pea.days_since_last_activity > 60 or pea.active_channel_count = 1 then 'Medium Activity Risk'
            when pea.days_since_last_activity > 30 then 'Low Activity Risk'
            else 'No Activity Risk'
        end as activity_risk_level,
        
        -- Recommended activity interventions
        case 
            when pea.engagement_velocity in ('Declining', 'Slow', 'Stagnant') and pea.customer_health_score >= 3.0 then 'Re-engagement Campaign'
            when pea.active_channel_count = 1 and pea.composite_engagement_score >= 2.5 then 'Channel Expansion'
            when pea.primary_engagement_channel = 'Marketing Driven' and pea.in_stripe = 0 then 'Sales Conversion Focus'
            when pea.primary_engagement_channel = 'Sales Driven' and pea.in_zendesk = 0 then 'Success Onboarding'
            when pea.days_since_last_activity <= 7 and pea.composite_engagement_score >= 3.5 then 'Upsell Opportunity'
            else 'Standard Engagement'
        end as recommended_activity_intervention
        
    from platform_engagement_analysis pea
),

-- Final activity insights
final_activity_metrics as (
    select 
        aam.*,
        
        -- Overall activity grade
        case 
            when aam.weighted_engagement_score >= 4.0 and aam.active_channel_count >= 3 then 'A+'
            when aam.weighted_engagement_score >= 3.5 and aam.active_channel_count >= 2 then 'A'
            when aam.weighted_engagement_score >= 3.0 then 'B+'
            when aam.weighted_engagement_score >= 2.5 then 'B'
            when aam.weighted_engagement_score >= 2.0 then 'C+'
            when aam.weighted_engagement_score >= 1.5 then 'C'
            when aam.weighted_engagement_score >= 1.0 then 'D'
            else 'F'
        end as activity_grade,
        
        -- Activity-based customer priority
        round(
            (aam.weighted_engagement_score * 0.4 +
             aam.active_channel_count * 0.3 +
             case 
                when aam.days_since_last_activity <= 7 and aam.composite_engagement_score >= 3.5 then 5
                when aam.days_since_last_activity <= 14 and aam.composite_engagement_score >= 3.0 then 4
                when aam.days_since_last_activity <= 30 and aam.composite_engagement_score >= 2.0 then 3
                when aam.days_since_last_activity <= 60 then 2
                else 1
             end * 0.3), 2
        ) as activity_priority_score,
        
        current_timestamp as activity_analysis_timestamp
        
    from advanced_activity_metrics aam
)

select 
    marketo_lead_id,
    stripe_customer_id,
    zendesk_user_id,
    primary_email,
    primary_organization,
    customer_segment,
    customer_journey_pattern,
    lifecycle_stage,
    
    -- Core activity metrics
    composite_engagement_score,
    weighted_engagement_score,
    customer_health_score,
    activity_grade,
    activity_priority_score,
    
    -- Temporal activity patterns
    days_since_last_activity,
    weeks_since_last_activity,
    months_since_last_activity,
    account_age_days,
    
    -- Platform engagement breakdown
    active_channel_count,
    primary_engagement_channel,
    marketing_engagement_score,
    sales_engagement_score,
    support_engagement_score,
    marketing_depth,
    sales_depth,
    support_depth,
    
    -- Activity patterns and trends
    engagement_velocity,
    activity_momentum,
    engagement_maturity,
    estimated_monthly_activities,
    predicted_next_month_activity,
    seasonally_adjusted_activity,
    
    -- Retention indicators
    active_30_days,
    active_60_days,
    active_90_days,
    active_180_days,
    active_365_days,
    
    -- Risk and opportunity indicators
    activity_risk_level,
    cross_platform_consistency,
    activity_efficiency,
    recommended_activity_intervention,
    
    -- Platform-specific flags
    in_marketo,
    in_stripe,
    in_zendesk,
    is_unsubscribed,
    is_email_invalid,
    do_not_call,
    is_delinquent,
    stripe_deleted,
    zendesk_active,
    zendesk_suspended,
    zendesk_deleted,
    
    -- Timestamps
    customer_first_touchpoint,
    customer_last_activity,
    marketo_registration_date,
    stripe_registration_date,
    zendesk_registration_date,
    activity_analysis_timestamp
    
from final_activity_metrics
where primary_email is not null
order by 
    activity_priority_score desc,
    weighted_engagement_score desc,
    active_channel_count desc
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 6947 | 6947 | 0 | 0 | 284 | 284 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"marketo_lead_id":"100","stripe_customer_id":"cus_005658","zendesk_user_id":"null"}</code> |
| K2 | <code>{"marketo_lead_id":"1003","stripe_customer_id":"cus_003355","zendesk_user_id":"null"}</code> |
| K3 | <code>{"marketo_lead_id":"1014","stripe_customer_id":"cus_004287","zendesk_user_id":"350"}</code> |
| K4 | <code>{"marketo_lead_id":"105","stripe_customer_id":"null","zendesk_user_id":"824"}</code> |
| K5 | <code>{"marketo_lead_id":"1239","stripe_customer_id":"null","zendesk_user_id":"3409"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| marketo_lead_id | 0 | 0 | 0 | BIGINT | BIGINT |
| stripe_customer_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| zendesk_user_id | 0 | 0 | 0 | BIGINT | BIGINT |
| primary_email | 0 | 0 | 0 | VARCHAR | VARCHAR |
| primary_organization | 0 | 0 | 0 | VARCHAR | VARCHAR |
| customer_segment | 0 | 0 | 0 | VARCHAR | VARCHAR |
| customer_journey_pattern | 0 | 0 | 0 | VARCHAR | VARCHAR |
| lifecycle_stage | 0 | 0 | 0 | VARCHAR | VARCHAR |
| composite_engagement_score | 0 | 0 | 0 | DECIMAL(14,1) | DECIMAL(14,1) |
| weighted_engagement_score | 3847 | 3847 | 3847 | DOUBLE | DOUBLE |
| customer_health_score | 0 | 0 | 0 | DECIMAL(15,2) | DECIMAL(15,2) |
| activity_grade | 0 | 0 | 0 | VARCHAR | VARCHAR |
| activity_priority_score | 3848 | 3848 | 3848 | DOUBLE | DOUBLE |
| days_since_last_activity | 6947 | 6947 | 6947 | BIGINT | BIGINT |
| weeks_since_last_activity | 6947 | 6947 | 6947 | BIGINT | BIGINT |
| months_since_last_activity | 6947 | 6947 | 6947 | BIGINT | BIGINT |
| account_age_days | 0 | 0 | 0 | BIGINT | BIGINT |
| active_channel_count | 0 | 0 | 0 | INTEGER | INTEGER |
| primary_engagement_channel | 6271 | 6271 | 6271 | VARCHAR | VARCHAR |
| marketing_engagement_score | 1553 | 1553 | 1553 | DOUBLE | DOUBLE |
| sales_engagement_score | 2353 | 2353 | 2353 | DOUBLE | DOUBLE |
| support_engagement_score | 793 | 793 | 793 | DOUBLE | DOUBLE |
| marketing_depth | 0 | 0 | 0 | VARCHAR | VARCHAR |
| sales_depth | 0 | 0 | 0 | VARCHAR | VARCHAR |
| support_depth | 0 | 0 | 0 | VARCHAR | VARCHAR |
| engagement_velocity | 321 | 321 | 321 | VARCHAR | VARCHAR |
| activity_momentum | 7 | 7 | 7 | VARCHAR | VARCHAR |
| engagement_maturity | 0 | 0 | 0 | VARCHAR | VARCHAR |
| estimated_monthly_activities | 3466 | 3466 | 3466 | DOUBLE | DOUBLE |
| predicted_next_month_activity | 3573 | 3573 | 3573 | DOUBLE | DOUBLE |
| seasonally_adjusted_activity | 3466 | 3466 | 3466 | DOUBLE | DOUBLE |
| active_30_days | 0 | 0 | 0 | INTEGER | INTEGER |
| active_60_days | 0 | 0 | 0 | INTEGER | INTEGER |
| active_90_days | 0 | 0 | 0 | INTEGER | INTEGER |
| active_180_days | 0 | 0 | 0 | INTEGER | INTEGER |
| active_365_days | 0 | 0 | 0 | INTEGER | INTEGER |
| activity_risk_level | 321 | 321 | 321 | VARCHAR | VARCHAR |
| cross_platform_consistency | 6947 | 6947 | 6947 | INTEGER | DOUBLE |
| activity_efficiency | 0 | 0 | 0 | DOUBLE | DOUBLE |
| recommended_activity_intervention | 3347 | 3347 | 3347 | VARCHAR | VARCHAR |
| in_marketo | 0 | 0 | 0 | INTEGER | INTEGER |
| in_stripe | 0 | 0 | 0 | INTEGER | INTEGER |
| in_zendesk | 0 | 0 | 0 | INTEGER | INTEGER |
| is_unsubscribed | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| is_email_invalid | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| do_not_call | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| is_delinquent | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| stripe_deleted | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| zendesk_active | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| zendesk_suspended | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| zendesk_deleted | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| customer_first_touchpoint | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| customer_last_activity | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| marketo_registration_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| stripe_registration_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| zendesk_registration_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| activity_analysis_timestamp | 6947 | 6947 | 6947 | TIMESTAMP WITH TIME ZONE | TIMESTAMP WITH TIME ZONE |

weighted_engagement_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | -10.96 | -7.31 |

activity_priority_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | -3.48 | -2.02 |

days_since_last_activity 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 1186 | 821 |

weeks_since_last_activity 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 169 | 117 |

months_since_last_activity 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 39 | 27 |

primary_engagement_channel 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | Sales Driven | Marketing Driven |

marketing_engagement_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | -36.53 | -24.37 |

sales_engagement_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | <code>[{"value":"-47.6","rows":2}]</code> | <code>[{"value":"-23.27","rows":2}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

support_engagement_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K3 | -16.73 | -4.57 |

engagement_velocity 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K4 | Stagnant | Slow |

activity_momentum 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K5 | No Momentum | Losing Momentum |

estimated_monthly_activities 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 1.0 | 3.0 |

predicted_next_month_activity 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0.2 | 0.6000000000000001 |

seasonally_adjusted_activity 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 1.0 | 3.0 |

activity_risk_level 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K4 | High Activity Risk | Medium Activity Risk |

cross_platform_consistency 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 4 | 2.0 |

recommended_activity_intervention 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | Success Onboarding | Standard Engagement |

activity_analysis_timestamp 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 2026-10-27 16:49:17.763138+08 | 2025-10-27 12:41:52.695115+08 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

| 约束 | 列 | 违反计数 |
|---|---|---|
| grain | primary_email | <code>{"distinct_key_groups":4734,"duplicate_key_groups":111,"rows_in_duplicate_groups":2324,"excess_duplicate_rows":2213,"null_key_rows":0,"nonnull_duplicate_key_groups":111,"nonnull_rows_in_duplicate_groups":2324,"nonnull_excess_duplicate_rows":2213,"null_containing_duplicate_key_groups":0,"rows_in_null_containing_duplicate_groups":0}</code> |

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>9列；[{"column":"activity_grade","value":"F"}]</code> |
| A4_equal_columns | <code>2组；[{"columns":["estimated_monthly_activities","seasonally_adjusted_activity"],"nonnull_equal_rows":6947,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>2组；[{"columns":["estimated_monthly_activities","seasonally_adjusted_activity"],"nonnull_equal_rows":6947,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| C9_agent_runtime_text | <code>S4:14 current_date；命中数=9</code> |
| C9_gold_runtime_text | <code>S5:60 current_date；命中数=14</code> |
| C9_contract_runtime_text | <code>S3:1490 current_date；命中数=7</code> |
| D10_keyword_in_any_result_field | <code>命中数=1；assistant_trajectory  left join marts.customer360__customer_activity_metrics am using(primary_email) where ba.primary_email is not null</code> |

## 轨迹索引（不放输出原文）

本题事件总数：53；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -printf '%p %s bytes\n' &#124; sort; cat config/layer_dependencies.yaml</code> | 3128 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 11047 | false | false |
| 17 | run | <code>mkdir -p sql/{staging,intermediate,marts} &amp;&amp; cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>from pathlib import Path<br>P=Path('sql')<br>def put(layer,name,sql):<br>    (P/layer/f'{name}.sql').write_text(sql.strip()+"\n")<br># STAGING</code> | 0 | false | false |
| 19 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br><br>put('intermediate','int_customer360__customer_behavior_analysis', '''<br>with matches as (<br>    select * from intermediate.int_customer360__source_matches<br>), joined as (<br>    sel</code> | 0 | false | false |
| 21 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br><br>put('intermediate','int_customer360__risk_assessment', '''<br>with behavior as (<br> select ba.*, lm.customer_health_score, lm.lifecycle_stage, lm.active_30_days, lm.active_90_day</code> | 0 | false | false |
| 23 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br><br># Generic distinct/index profile marts<br>put('marts','customer360__email', '''<br>with email_rows as (<br> select m.customer360_id, s.email from marts.customer360__mapping m inner j</code> | 0 | false | false |
| 25 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br><br>put('marts','customer360__customer_value_analysis', '''<br>with base as (<br> select *,case when estimated_customer_value&gt;=5000 then 5 when estimated_customer_value&gt;=3000 then 4 w</code> | 0 | false | false |
| 27 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br><br>put('marts','customer360__organization_network', '''<br>with entities as (<br> select ba.primary_email,ba.marketo_lead_id,ba.stripe_customer_id,ba.zendesk_user_id,ba.primary_organ</code> | 48 | false | false |
| 29 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -100 /tmp/runlog</code> | 7140 | true | false |
| 31 | run | <code>sed -i 's/m\.phone is not null or m\.mobile_phone is not null/phone is not null or mobile_phone is not null/' sql/intermediate/int_customer360__customer_behavior_analysis.sql &amp;&amp; python run.py &gt; /tmp/r</code> | 1493 | true | false |
| 33 | run | <code>grep -n ' m\.' sql/intermediate/int_customer360__customer_behavior_analysis.sql; grep -n -A6 -B4 'ERROR - ✗ intermediate.int_customer360__customer_behavior_analysis' /tmp/runlog</code> | 1764 | false | false |
| 35 | run | <code>sed -i -e 's/m\.country_code/country_code/g' -e 's/m\.state_code/state_code/g' -e 's/m\.city/city/g' sql/intermediate/int_customer360__customer_behavior_analysis.sql; python run.py &gt; /tmp/runlog 2&gt;&amp;1;</code> | 1493 | true | false |
| 37 | run | <code>grep -nE 's\.&#124;z\.' sql/intermediate/int_customer360__customer_behavior_analysis.sql</code> | 1249 | false | false |
| 39 | run | <code>sed -i -e 's/s\.customer_address_line_1/customer_address_line_1/g' -e 's/s\.customer_country_code/customer_country_code/g' -e 's/z\.organization_id/organization_id/g' sql/intermediate/int_customer360_</code> | 394 | false | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('customer360.duckdb',read_only=True)<br>checks={<br>'status_key_dups':"select count(*) from (select customer360_id from marts.customer360__status group by 1 ha</code> | 616 | false | false |

### agent action 的 thought/message 命中原句

event 25 / message

```text
put('marts','customer360__customer_activity_metrics', '''
```
event 27 / message

```text
 left join marts.customer360__customer_activity_metrics am using(primary_email) where ba.primary_email is not null
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-003.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-003/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/marts/customer360__customer_activity_metrics.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/sql/marts/customer360__customer_activity_metrics.sql`
- S6: `records/006_contract_impl-003.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/result.md`
- S10: `data/019_packages_work/019_impl-003_customer360__customer_activity_metrics/019_impl-003_customer360__customer_activity_metrics.json`
- S11: `data/005_cs_work/impl-003/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/customer360.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions`
