# impl-003 | intermediate | int_customer360__customer_behavior_analysis | 差异：S1；日期 2025-10-27

## 契约完整原文

S3:821–913

```yaml
    - name: int_customer360__customer_behavior_analysis
      description: Customer behavior profile per resolved customer with cross-platform engagement, lifecycle metrics, and segmentation
      grain: One row per source match key (marketo_lead_id, stripe_customer_id, zendesk_user_id) with non-null primary_email
      source_models:
      - intermediate.int_customer360__source_matches
      - intermediate.int_customer360__marketo
      - intermediate.int_customer360__stripe
      - intermediate.int_customer360__zendesk
      business_logic: 'Build per-customer behavior and segmentation by: - Source inputs: - Marketo (intermediate.int_customer360__marketo) per lead_id - Stripe (intermediate.int_customer360__stripe) per customer_id - Zendesk (intermediate.int_customer360__zendesk) per user_id - Identity map (intermediate.int_customer360__source_matches) providing the cross-platform ID linkage - Per-platform metrics: - Marketo: - marketo_first_touch = created_at; marketo_last_activity = updated_at - marketo_engagement_score: - 0 if is_unsubscribed = true or is_email_invalid = true - else 3 if days between created_at and updated_at < 30 - else 2 if < 90 - else 1 - has_organization_data = 1 if organization_name_no_suffix not null and length > 3 else 0 - has_phone_contact = 1 if phone or mobile_phone present else 0 - address_completeness_score: - 3 if country_code, state_code, and city all present - 2 if country_code present and at least one of state_code or city present - 1 if only country_code present - 0 otherwise - Stripe: - stripe_first_transaction = created_at; stripe_last_activity = updated_at - stripe_engagement_score: - 0 if is_deleted = true - 1 if is_delinquent = true (and not deleted) - else 4 if days between created_at and updated_at < 30 - else 3 if < 90 - else 2 - payment_reliability_score: - 3 if is_delinquent = false and is_deleted = false - 1 if is_delinquent = true and is_deleted = false - 0 otherwise - billing_completeness_score: - 2 if customer_address_line_1 and customer_country_code present - 1 if only customer_country_code present - 0 otherwise - Zendesk: - zendesk_first_contact = created_at; zendesk_last_activity = updated_at - zendesk_engagement_score: - 0 if is_suspended = true or is_deleted = true - 1 if is_active = false - else 4 if days between created_at and updated_at < 30 - else 3 if < 90 - else 2 - org_relationship_strength: - 2 if organization_id and organization_name_no_suffix present - 1 if only organization_id present - 0 otherwise - Join and aggregate: - Left join per-platform metrics to source_matches on respective IDs - primary_email = coalesce(Marketo.email, Stripe.email, Zendesk.email); rows with NULL primary_email are excluded - email_domain and primary_organization use the same COALESCE order (Marketo, then Stripe, then Zendesk) - customer_first_touchpoint = the earliest of the three per-platform first-touch timestamps - customer_last_activity = the latest of the three per-platform last-activity timestamps - If any of the three timestamps is NULL, the earliest/latest result is NULL - marketo_engagement/stripe_engagement/zendesk_engagement = respective per-platform scores with NULL → 0 - composite_engagement_score = weighted average (weights: Marketo 0.3, Stripe 0.5, Zendesk 0.2), rounded to two decimals and stored with one decimal precision - in_marketo/in_stripe/in_zendesk = 1 if respective joined record exists, else 0 - organization_data_quality = coalesce(has_organization_data,0) + coalesce(billing_completeness_score,0) + coalesce(org_relationship_strength,0) - has_contact_phone = coalesce(has_phone_contact, 0) - address_data_quality = coalesce(address_completeness_score,0) + coalesce(billing_completeness_score,0) - marketing_to_sales_days = days between Marketo first touch and Stripe first transaction only if both present; else NULL - sales_to_support_days = days between Stripe first transaction and Zendesk first contact only if both present; else NULL - account_age_days = days between the earliest available first-touch and current_date; NULL if the earliest is NULL - customer_maturity (derived from the same earliest timestamp vs current_date): - ''New Customer'' if < 90 days - ''Growing Relationship'' if < 365 days - ''Established Customer'' if < 1095 days - ''Long-term Customer'' otherwise (including when the start date is NULL) - customer_journey_pattern based on platform presence, evaluated in this order: - ''Full Journey'' if all three present - ''Marketing to Sales'' if Marketo and Stripe - ''Sales to Support'' if Stripe and Zendesk - ''Marketing to Support'' if Marketo and Zendesk - ''Marketing Only'' if only Marketo - ''Sales Only'' if only Stripe - ''Support Only'' if only Zendesk - ''Unknown'' otherwise - payment_reliability = coalesce(Stripe.payment_reliability_score, 0) - Classification: - customer_segment (first match wins): - ''Champion'' if composite_engagement_score >= 3.5 and payment_reliability >= 2 - ''Loyal Customer'' if composite_engagement_score >= 3.0 and customer_journey_pattern = ''Full Journey'' - ''Potential Loyalist'' if composite_engagement_score >= 2.5 and payment_reliability >= 2 - ''New Customer'' if composite_engagement_score >= 2.0 and account_age_days < 90 - ''At Risk'' if composite_engagement_score >= 1.5 - ''Hibernating'' if composite_engagement_score > 0 - ''Lost'' otherwise - churn_risk_level: - ''High Risk'' if payment_reliability = 0 or composite_engagement_score < 1 - ''Medium Risk'' if composite_engagement_score < 2 and account_age_days > 365 - ''Medium Risk'' if customer_last_activity is more than 90 days ago - ''Low Risk'' otherwise (including when comparisons evaluate to NULL) - recommended_action based on customer_segment: - ''Upsell/Cross-sell'' for ''Champion'' or ''Loyal Customer'' - ''Engagement Campaign'' for ''Potential Loyalist'' - ''Onboarding Focus'' for ''New Customer'' - ''Win-back Campaign'' for ''At Risk'' - ''Reactivation Campaign'' for ''Hibernating'' - ''Recovery Campaign'' otherwise - Output filter and ordering: - Keep only rows where primary_email is not NULL - Order rows by composite_engagement_score descending, then account_age_days descending'
      columns:
      - name: marketo_lead_id
        data_type: BIGINT
        description: Marketo lead identifier from source_matches; nullable when no Marketo mapping exists
      - name: stripe_customer_id
        data_type: VARCHAR
        description: Stripe customer identifier from source_matches; nullable when no Stripe mapping exists
      - name: zendesk_user_id
        data_type: BIGINT
        description: Zendesk user identifier from source_matches; nullable when no Zendesk mapping exists
      - name: primary_email
        data_type: VARCHAR
        description: Primary email chosen by Marketo then Stripe then Zendesk; not null due to final filter; casing and spacing preserved
        tests:
        - not_null
      - name: email_domain
        data_type: VARCHAR
        description: Email domain chosen by the same precedence as primary_email; NULL if all source domains are NULL; formatting preserved
      - name: primary_organization
        data_type: VARCHAR
        description: Organization chosen by precedence Marketo, then Stripe, then Zendesk; NULL if all are NULL
      - name: customer_first_touchpoint
        data_type: TIMESTAMP
        description: Earliest timestamp across the three platform first-touch timestamps; NULL if any input is NULL
      - name: customer_last_activity
        data_type: TIMESTAMP
        description: Latest timestamp across the three platform last-activity timestamps; NULL if any input is NULL
      - name: marketo_engagement
        data_type: INTEGER
        description: Marketo engagement score per rules in business_logic (0/1/2/3); NULL Marketo row yields 0
      - name: stripe_engagement
        data_type: INTEGER
        description: Stripe engagement score per rules in business_logic (0/1/2/3/4); NULL Stripe row yields 0
      - name: zendesk_engagement
        data_type: INTEGER
        description: Zendesk engagement score per rules in business_logic (0/1/2/3/4); NULL Zendesk row yields 0
      - name: composite_engagement_score
        data_type: DECIMAL(14,1)
        description: Weighted average of platform scores (weights 0.3, 0.5, 0.2), rounded to two decimals then stored with one decimal; missing scores treated as 0; range 0.0–3.7
      - name: in_marketo
        data_type: INTEGER
        description: Platform presence flag derived from join on Marketo (1 if joined row exists, else 0); values strictly 0 or 1
      - name: in_stripe
        data_type: INTEGER
        description: Platform presence flag derived from join on Stripe (1 if joined row exists, else 0); values strictly 0 or 1
      - name: in_zendesk
        data_type: INTEGER
        description: Platform presence flag derived from join on Zendesk (1 if joined row exists, else 0); values strictly 0 or 1
      - name: organization_data_quality
        data_type: INTEGER
        description: Aggregate org data score = has_organization_data(0/1) + billing_completeness_score(0/1/2) + org_relationship_strength(0/1/2); NULL components treated as 0; range 0–5
      - name: has_contact_phone
        data_type: INTEGER
        description: 1 if Marketo has phone or mobile_phone, else 0; NULL treated as 0; values strictly 0 or 1
      - name: address_data_quality
        data_type: INTEGER
        description: Address/billing completeness = Marketo.address_completeness_score(0–3) + Stripe.billing_completeness_score(0–2); NULL components treated as 0; range 0–5
      - name: marketing_to_sales_days
        data_type: BIGINT
        description: Days from Marketo first touch to Stripe first transaction; NULL unless both timestamps are non-null; may be negative or positive
      - name: sales_to_support_days
        data_type: BIGINT
        description: Days from Stripe first transaction to Zendesk first contact; NULL unless both timestamps are non-null; may be negative or positive
      - name: account_age_days
        data_type: BIGINT
        description: Days from the earliest first-touch timestamp to current_date; NULL if the earliest is NULL; computed at execution time
      - name: customer_maturity
        data_type: VARCHAR
        description: 'Lifecycle label based on days since earliest touch: New Customer (<90), Growing Relationship (<365), Established Customer (<1095), else Long-term Customer; NULL start yields Long-term Customer'
      - name: customer_journey_pattern
        data_type: VARCHAR
        description: 'Journey coverage across platforms with precedence: Full Journey; Marketing to Sales; Sales to Support; Marketing to Support; Marketing Only; Sales Only; Support Only; else Unknown'
      - name: payment_reliability
        data_type: INTEGER
        description: 'Stripe-derived reliability score: 3 (not delinquent and not deleted), 1 (delinquent and not deleted), 0 otherwise; NULL Stripe row yields 0'
      - name: customer_segment
        data_type: VARCHAR
        description: 'Segment assigned by ordered rules: Champion; Loyal Customer; Potential Loyalist; New Customer; At Risk; Hibernating; else Lost'
      - name: churn_risk_level
        data_type: VARCHAR
        description: 'Risk level by ordered rules: High if payment_reliability=0 or composite<1; Medium if composite<2 and age>365; Medium if last activity >90 days ago; else Low'
      - name: recommended_action
        data_type: VARCHAR
        description: 'Next best action mapped from customer_segment: Upsell/Cross-sell; Engagement Campaign; Onboarding Focus; Win-back Campaign; Reactivation Campaign; else Recovery Campaign'
```

## agent 最终 SQL

S4

```sql
with matches as (
    select * from intermediate.int_customer360__source_matches
), joined as (
    select sm.marketo_lead_id, sm.stripe_customer_id, sm.zendesk_user_id,
           m.email as m_email, s.email as s_email, z.email as z_email,
           m.email_domain as m_domain, s.email_domain as s_domain, z.email_domain as z_domain,
           coalesce(m.organization_name_no_suffix, s.customer_organization_name_no_suffix, z.organization_name_no_suffix) as primary_organization,
           m.created_at as m_created, m.updated_at as m_updated, m.is_unsubscribed, m.is_email_invalid,
           m.organization_name_no_suffix as m_org, m.phone, m.mobile_phone, country_code, state_code, city,
           s.created_at as s_created, s.updated_at as s_updated, s.is_deleted as s_deleted, s.is_delinquent,
           customer_address_line_1, customer_country_code,
           z.created_at as z_created, z.updated_at as z_updated, z.is_deleted as z_deleted, z.is_suspended, z.is_active,
           organization_id, z.organization_name_no_suffix as z_org
    from matches sm
    left join intermediate.int_customer360__marketo m on sm.marketo_lead_id = m.lead_id
    left join intermediate.int_customer360__stripe s on sm.stripe_customer_id = s.customer_id
    left join intermediate.int_customer360__zendesk z on sm.zendesk_user_id = z.user_id
), scored as (
    select *,
        case when m_email is null then null when is_unsubscribed or is_email_invalid then 0
             when date_diff('day', m_created, m_updated) < 30 then 3
             when date_diff('day', m_created, m_updated) < 90 then 2 else 1 end as m_score,
        case when s_email is null then null when s_deleted then 0 when is_delinquent then 1
             when date_diff('day', s_created, s_updated) < 30 then 4
             when date_diff('day', s_created, s_updated) < 90 then 3 else 2 end as s_score,
        case when z_email is null then null when is_suspended or z_deleted then 0 when is_active = false then 1
             when date_diff('day', z_created, z_updated) < 30 then 4
             when date_diff('day', z_created, z_updated) < 90 then 3 else 2 end as z_score,
        case when m_org is not null and length(m_org)>3 then 1 else 0 end as org_score,
        case when phone is not null or mobile_phone is not null then 1 else 0 end as phone_score,
        case when country_code is not null and state_code is not null and city is not null then 3
             when country_code is not null and (state_code is not null or city is not null) then 2
             when country_code is not null then 1 else 0 end as address_score,
        case when s_email is not null and s_deleted = false and is_delinquent = false then 3
             when s_email is not null and is_delinquent = true and s_deleted = false then 1 else 0 end as reliability,
        case when customer_address_line_1 is not null and customer_country_code is not null then 2
             when customer_country_code is not null then 1 else 0 end as billing_score,
        case when organization_id is not null and z_org is not null then 2
             when organization_id is not null then 1 else 0 end as org_relationship
    from joined
), derived as (
    select *, coalesce(m_email,s_email,z_email) as primary_email,
        coalesce(m_domain,s_domain,z_domain) as email_domain,
        case when m_created is null or s_created is null or z_created is null then null else least(m_created,s_created,z_created) end as first_touch,
        case when m_updated is null or s_updated is null or z_updated is null then null else greatest(m_updated,s_updated,z_updated) end as last_activity,
        coalesce(m_score,0) as me, coalesce(s_score,0) as se, coalesce(z_score,0) as ze,
        (coalesce(m_score,0)*0.3 + coalesce(s_score,0)*0.5 + coalesce(z_score,0)*0.2)::decimal(14,1) as composite
    from scored
), segments as (
    select *, date_diff('day', first_touch, current_date)::bigint as age_days,
        case when m_email is not null then 1 else 0 end as im,
        case when s_email is not null then 1 else 0 end as is_,
        case when z_email is not null then 1 else 0 end as iz,
        case when m_email is not null and s_email is not null and z_email is not null then 'Full Journey'
             when m_email is not null and s_email is not null then 'Marketing to Sales'
             when s_email is not null and z_email is not null then 'Sales to Support'
             when m_email is not null and z_email is not null then 'Marketing to Support'
             when m_email is not null then 'Marketing Only' when s_email is not null then 'Sales Only'
             when z_email is not null then 'Support Only' else 'Unknown' end as journey,
        case when composite >= 3.5 and reliability >= 2 then 'Champion'
             when composite >= 3.0 and m_email is not null and s_email is not null and z_email is not null then 'Loyal Customer'
             when composite >= 2.5 and reliability >= 2 then 'Potential Loyalist'
             when composite >= 2.0 and date_diff('day', first_touch, current_date) < 90 then 'New Customer'
             when composite >= 1.5 then 'At Risk' when composite > 0 then 'Hibernating' else 'Lost' end as segment
    from derived
), labels as (
    select *, case when age_days < 90 then 'New Customer' when age_days < 365 then 'Growing Relationship'
                   when age_days < 1095 then 'Established Customer' else 'Long-term Customer' end as maturity,
        case when reliability=0 or composite<1 then 'High Risk'
             when composite<2 and age_days>365 then 'Medium Risk'
             when last_activity < current_timestamp - interval '90 days' then 'Medium Risk' else 'Low Risk' end as churn_risk
    from segments
)
select marketo_lead_id, stripe_customer_id, zendesk_user_id, primary_email, email_domain, primary_organization,
       first_touch as customer_first_touchpoint, last_activity as customer_last_activity,
       me as marketo_engagement, se as stripe_engagement, ze as zendesk_engagement,
       composite as composite_engagement_score, im as in_marketo, is_ as in_stripe, iz as in_zendesk,
       (coalesce(org_score,0)+coalesce(billing_score,0)+coalesce(org_relationship,0))::integer as organization_data_quality,
       coalesce(phone_score,0)::integer as has_contact_phone,
       (coalesce(address_score,0)+coalesce(billing_score,0))::integer as address_data_quality,
       case when m_created is not null and s_created is not null then date_diff('day',m_created,s_created) end::bigint as marketing_to_sales_days,
       case when s_created is not null and z_created is not null then date_diff('day',s_created,z_created) end::bigint as sales_to_support_days,
       age_days::bigint as account_age_days, maturity as customer_maturity, journey as customer_journey_pattern,
       reliability::integer as payment_reliability, segment as customer_segment,
       churn_risk as churn_risk_level,
       case segment when 'Champion' then 'Upsell/Cross-sell' when 'Loyal Customer' then 'Upsell/Cross-sell'
            when 'Potential Loyalist' then 'Engagement Campaign' when 'New Customer' then 'Onboarding Focus'
            when 'At Risk' then 'Win-back Campaign' when 'Hibernating' then 'Reactivation Campaign'
            else 'Recovery Campaign' end as recommended_action
from labels
where primary_email is not null
```

## gold SQL（仅供定位差异）

S5

```sql
-- Customer behavior analysis across all platforms
-- This table analyzes customer engagement patterns across Marketo, Stripe, and Zendesk
-- to create comprehensive behavior profiles for customer segmentation

with marketo_data as (
    select * from intermediate.int_customer360__marketo
),

stripe_data as (
    select * from intermediate.int_customer360__stripe  
),

zendesk_data as (
    select * from intermediate.int_customer360__zendesk
),

source_matches as (
    select * from intermediate.int_customer360__source_matches
),

-- Calculate customer engagement metrics from each platform
marketo_engagement as (
    select 
        m.lead_id,
        m.email,
        m.email_domain,
        m.organization_name_no_suffix as organization,
        m.created_at as marketo_first_touch,
        m.updated_at as marketo_last_activity,
        -- Email engagement scoring
        case 
            when m.is_unsubscribed = true then 0
            when m.is_email_invalid = true then 0
            when datediff('day', m.created_at, m.updated_at) < 30 then 3
            when datediff('day', m.created_at, m.updated_at) < 90 then 2
            else 1
        end as marketo_engagement_score,
        -- Lead quality indicators
        case 
            when m.organization_name_no_suffix is not null and length(m.organization_name_no_suffix) > 3 then 1
            else 0
        end as has_organization_data,
        case 
            when m.phone is not null or m.mobile_phone is not null then 1
            else 0
        end as has_phone_contact,
        -- Geographic completeness
        case 
            when m.country_code is not null and m.state_code is not null and m.city is not null then 3
            when m.country_code is not null and (m.state_code is not null or m.city is not null) then 2
            when m.country_code is not null then 1
            else 0
        end as address_completeness_score
    from marketo_data m
),

stripe_engagement as (
    select 
        s.customer_id,
        s.email,
        s.email_domain,
        s.customer_organization_name_no_suffix as organization,
        s.created_at as stripe_first_transaction,
        s.updated_at as stripe_last_activity,
        -- Customer value indicators
        case 
            when s.is_deleted = true then 0
            when s.is_delinquent = true then 1
            when datediff('day', s.created_at, s.updated_at) < 30 then 4
            when datediff('day', s.created_at, s.updated_at) < 90 then 3
            else 2
        end as stripe_engagement_score,
        -- Payment reliability
        case 
            when s.is_delinquent = false and s.is_deleted = false then 3
            when s.is_delinquent = true and s.is_deleted = false then 1
            else 0
        end as payment_reliability_score,
        -- Data completeness for billing
        case 
            when s.customer_address_line_1 is not null and s.customer_country_code is not null then 2
            when s.customer_country_code is not null then 1
            else 0
        end as billing_completeness_score
    from stripe_data s
),

zendesk_engagement as (
    select 
        z.user_id,
        z.email,
        z.email_domain,
        z.organization_name_no_suffix as organization,
        z.organization_id,
        z.created_at as zendesk_first_contact,
        z.updated_at as zendesk_last_activity,
        z.organization_created_at,
        z.organization_updated_at,
        -- Support engagement scoring
        case 
            when z.is_suspended = true then 0
            when z.is_deleted = true then 0
            when z.is_active = false then 1
            when datediff('day', z.created_at, z.updated_at) < 30 then 4
            when datediff('day', z.created_at, z.updated_at) < 90 then 3
            else 2
        end as zendesk_engagement_score,
        -- Organization relationship strength
        case 
            when z.organization_id is not null and z.organization_name_no_suffix is not null then 2
            when z.organization_id is not null then 1
            else 0
        end as org_relationship_strength
    from zendesk_data z
),

-- Combine engagement data using source matches
comprehensive_behavior as (
    select 
        -- Identity mapping
        sm.marketo_lead_id,
        sm.stripe_customer_id, 
        sm.zendesk_user_id,
        
        -- Primary identification
        coalesce(me.email, se.email, ze.email) as primary_email,
        coalesce(me.email_domain, se.email_domain, ze.email_domain) as email_domain,
        coalesce(me.organization, se.organization, ze.organization) as primary_organization,
        
        -- Temporal analysis
        least(
            me.marketo_first_touch,
            se.stripe_first_transaction, 
            ze.zendesk_first_contact
        ) as customer_first_touchpoint,
        
        greatest(
            me.marketo_last_activity,
            se.stripe_last_activity,
            ze.zendesk_last_activity
        ) as customer_last_activity,
        
        -- Cross-platform engagement scoring
        coalesce(me.marketo_engagement_score, 0) as marketo_engagement,
        coalesce(se.stripe_engagement_score, 0) as stripe_engagement,
        coalesce(ze.zendesk_engagement_score, 0) as zendesk_engagement,
        
        -- Composite engagement score (weighted average)
        round(
            (coalesce(me.marketo_engagement_score, 0) * 0.3 +
             coalesce(se.stripe_engagement_score, 0) * 0.5 +
             coalesce(ze.zendesk_engagement_score, 0) * 0.2), 2
        ) as composite_engagement_score,
        
        -- Platform presence indicators
        case when me.lead_id is not null then 1 else 0 end as in_marketo,
        case when se.customer_id is not null then 1 else 0 end as in_stripe,
        case when ze.user_id is not null then 1 else 0 end as in_zendesk,
        
        -- Data quality scores
        coalesce(me.has_organization_data, 0) + 
        coalesce(se.billing_completeness_score, 0) + 
        coalesce(ze.org_relationship_strength, 0) as organization_data_quality,
        
        coalesce(me.has_phone_contact, 0) as has_contact_phone,
        coalesce(me.address_completeness_score, 0) + 
        coalesce(se.billing_completeness_score, 0) as address_data_quality,
        
        -- Customer lifecycle indicators  
        case 
            when me.marketo_first_touch is not null and se.stripe_first_transaction is not null then
                datediff('day', me.marketo_first_touch, se.stripe_first_transaction)
            else null
        end as marketing_to_sales_days,
        
        case 
            when se.stripe_first_transaction is not null and ze.zendesk_first_contact is not null then
                datediff('day', se.stripe_first_transaction, ze.zendesk_first_contact)
            else null
        end as sales_to_support_days,
        
        -- Account age and maturity
        datediff('day', 
            least(me.marketo_first_touch, se.stripe_first_transaction, ze.zendesk_first_contact), 
            current_date
        ) as account_age_days,
        
        case 
            when datediff('day', 
                least(me.marketo_first_touch, se.stripe_first_transaction, ze.zendesk_first_contact), 
                current_date) < 90 then 'New Customer'
            when datediff('day', 
                least(me.marketo_first_touch, se.stripe_first_transaction, ze.zendesk_first_contact), 
                current_date) < 365 then 'Growing Relationship'
            when datediff('day', 
                least(me.marketo_first_touch, se.stripe_first_transaction, ze.zendesk_first_contact), 
                current_date) < 1095 then 'Established Customer'
            else 'Long-term Customer'
        end as customer_maturity,
        
        -- Multi-platform engagement patterns
        case 
            when me.lead_id is not null and se.customer_id is not null and ze.user_id is not null then 'Full Journey'
            when me.lead_id is not null and se.customer_id is not null then 'Marketing to Sales'
            when se.customer_id is not null and ze.user_id is not null then 'Sales to Support'
            when me.lead_id is not null and ze.user_id is not null then 'Marketing to Support'
            when me.lead_id is not null then 'Marketing Only'
            when se.customer_id is not null then 'Sales Only'
            when ze.user_id is not null then 'Support Only'
            else 'Unknown'
        end as customer_journey_pattern,
        
        -- Business value indicators
        coalesce(se.payment_reliability_score, 0) as payment_reliability
        
    from source_matches sm
    left join marketo_engagement me on sm.marketo_lead_id = me.lead_id
    left join stripe_engagement se on sm.stripe_customer_id = se.customer_id
    left join zendesk_engagement ze on sm.zendesk_user_id = ze.user_id
),

-- Final behavior classification
final_analysis as (
    select 
        *,
        -- Customer segment classification
        case 
            when composite_engagement_score >= 3.5 and payment_reliability >= 2 then 'Champion'
            when composite_engagement_score >= 3.0 and customer_journey_pattern = 'Full Journey' then 'Loyal Customer'
            when composite_engagement_score >= 2.5 and payment_reliability >= 2 then 'Potential Loyalist'
            when composite_engagement_score >= 2.0 and account_age_days < 90 then 'New Customer'
            when composite_engagement_score >= 1.5 then 'At Risk'
            when composite_engagement_score > 0 then 'Hibernating'
            else 'Lost'
        end as customer_segment,
        
        -- Risk assessment
        case 
            when payment_reliability = 0 or composite_engagement_score < 1 then 'High Risk'
            when composite_engagement_score < 2 and account_age_days > 365 then 'Medium Risk'
            when customer_last_activity < current_date - interval '90 days' then 'Medium Risk'
            else 'Low Risk'
        end as churn_risk_level,
        
        -- Next best action recommendation
        case 
            when customer_segment in ('Champion', 'Loyal Customer') then 'Upsell/Cross-sell'
            when customer_segment = 'Potential Loyalist' then 'Engagement Campaign'
            when customer_segment = 'New Customer' then 'Onboarding Focus'
            when customer_segment = 'At Risk' then 'Win-back Campaign'
            when customer_segment = 'Hibernating' then 'Reactivation Campaign'
            else 'Recovery Campaign'
        end as recommended_action
        
    from comprehensive_behavior
)

select * from final_analysis
where primary_email is not null
order by composite_engagement_score desc, account_age_days desc
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
| K2 | <code>{"marketo_lead_id":"1003","stripe_customer_id":"cus_003355","zendesk_user_id":"null"}</code> |
| K3 | <code>{"marketo_lead_id":"101","stripe_customer_id":"null","zendesk_user_id":"654"}</code> |
| K4 | <code>{"marketo_lead_id":"1017","stripe_customer_id":"cus_006450","zendesk_user_id":"null"}</code> |
| K5 | <code>{"marketo_lead_id":"2421","stripe_customer_id":"cus_006806","zendesk_user_id":"null"}</code> |
| K6 | <code>{"marketo_lead_id":"340","stripe_customer_id":"cus_004842","zendesk_user_id":"null"}</code> |
| K7 | <code>{"marketo_lead_id":"3740","stripe_customer_id":"cus_004349","zendesk_user_id":"null"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| marketo_lead_id | 0 | 0 | 0 | BIGINT | BIGINT |
| stripe_customer_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| zendesk_user_id | 0 | 0 | 0 | BIGINT | BIGINT |
| account_age_days | 4027 | 4027 | 4027 | BIGINT | BIGINT |
| address_data_quality | 0 | 0 | 0 | INTEGER | INTEGER |
| churn_risk_level | 1468 | 1468 | 1468 | VARCHAR | VARCHAR |
| composite_engagement_score | 0 | 0 | 0 | DECIMAL(14,1) | DECIMAL(14,1) |
| customer_first_touchpoint | 4027 | 4027 | 4027 | TIMESTAMP | TIMESTAMP |
| customer_journey_pattern | 0 | 0 | 0 | VARCHAR | VARCHAR |
| customer_last_activity | 4027 | 4027 | 4027 | TIMESTAMP | TIMESTAMP |
| customer_maturity | 4027 | 4027 | 4027 | VARCHAR | VARCHAR |
| customer_segment | 7 | 7 | 7 | VARCHAR | VARCHAR |
| email_domain | 0 | 0 | 0 | VARCHAR | VARCHAR |
| has_contact_phone | 0 | 0 | 0 | INTEGER | INTEGER |
| in_marketo | 0 | 0 | 0 | INTEGER | INTEGER |
| in_stripe | 0 | 0 | 0 | INTEGER | INTEGER |
| in_zendesk | 0 | 0 | 0 | INTEGER | INTEGER |
| marketo_engagement | 0 | 0 | 0 | INTEGER | INTEGER |
| organization_data_quality | 0 | 0 | 0 | INTEGER | INTEGER |
| payment_reliability | 0 | 0 | 0 | INTEGER | INTEGER |
| primary_email | 0 | 0 | 0 | VARCHAR | VARCHAR |
| primary_organization | 0 | 0 | 0 | VARCHAR | VARCHAR |
| recommended_action | 7 | 7 | 7 | VARCHAR | VARCHAR |
| stripe_engagement | 0 | 0 | 0 | INTEGER | INTEGER |
| zendesk_engagement | 0 | 0 | 0 | INTEGER | INTEGER |

account_age_days 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 831 |
| K2 | null | 438 |
| K3 | null | 987 |

churn_risk_level 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | Low Risk | Medium Risk |
| K2 | Low Risk | Medium Risk |
| K4 | Low Risk | Medium Risk |

customer_first_touchpoint 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 2023-07-19 19:15:58.290113 |
| K2 | null | 2024-08-15 19:15:58.367276 |
| K3 | null | 2023-02-13 19:15:59.489086 |

customer_last_activity 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 2023-07-29 19:15:58.290113 |
| K2 | null | 2024-12-22 19:15:57.162401 |
| K3 | null | 2023-02-23 19:15:59.489086 |

customer_maturity 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | Long-term Customer | Established Customer |
| K2 | Long-term Customer | Established Customer |
| K3 | Long-term Customer | Established Customer |

customer_segment 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K5 | At Risk | New Customer |
| K6 | At Risk | New Customer |
| K7 | At Risk | New Customer |

recommended_action 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K5 | Win-back Campaign | Onboarding Focus |
| K6 | Win-back Campaign | Onboarding Focus |
| K7 | Win-back Campaign | Onboarding Focus |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A4_equal_columns | <code>1组；[{"columns":["in_marketo","has_contact_phone"],"nonnull_equal_rows":5001,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>1组；[{"columns":["in_marketo","has_contact_phone"],"nonnull_equal_rows":5001,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| C9_agent_runtime_text | <code>S4:50 current_date；命中数=3</code> |
| C9_gold_runtime_text | <code>S5:185 current_date；命中数=5</code> |
| C9_contract_runtime_text | <code>S3:829 current_date；命中数=3</code> |
| D10_keyword_in_any_result_field | <code>命中数=4；task_instruction_not_agent_report       grain: One row per intermediate.int_customer360__customer_behavior_analysis record with non-null primary_email</code> |

## 轨迹索引（不放输出原文）

本题事件总数：53；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions/6b2b0a3f-8315-48-8f57baf0001c6f1/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f -maxdepth 3 -printf '%p %s bytes\n' &#124; sort; cat config/layer_dependencies.yaml</code> | 3128 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 11047 | true | false |
| 17 | run | <code>mkdir -p sql/{staging,intermediate,marts} &amp;&amp; cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>from pathlib import Path<br>P=Path('sql')<br>def put(layer,name,sql):<br>    (P/layer/f'{name}.sql').write_text(sql.strip()+"\n")<br># STAGING</code> | 0 | false | false |
| 19 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br><br>put('intermediate','int_customer360__customer_behavior_analysis', '''<br>with matches as (<br>    select * from intermediate.int_customer360__source_matches<br>), joined as (<br>    sel</code> | 0 | false | false |
| 21 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br><br>put('intermediate','int_customer360__risk_assessment', '''<br>with behavior as (<br> select ba.*, lm.customer_health_score, lm.lifecycle_stage, lm.active_30_days, lm.active_90_day</code> | 0 | false | false |
| 23 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br><br># Generic distinct/index profile marts<br>put('marts','customer360__email', '''<br>with email_rows as (<br> select m.customer360_id, s.email from marts.customer360__mapping m inner j</code> | 0 | false | false |
| 25 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br><br>put('marts','customer360__customer_value_analysis', '''<br>with base as (<br> select *,case when estimated_customer_value&gt;=5000 then 5 when estimated_customer_value&gt;=3000 then 4 w</code> | 0 | false | false |
| 27 | run | <code>cat &gt;&gt; /tmp/gen.py &lt;&lt;'PY'<br><br>put('marts','customer360__organization_network', '''<br>with entities as (<br> select ba.primary_email,ba.marketo_lead_id,ba.stripe_customer_id,ba.zendesk_user_id,ba.primary_organ</code> | 48 | false | false |
| 29 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -100 /tmp/runlog</code> | 7140 | true | false |
| 31 | run | <code>sed -i 's/m\.phone is not null or m\.mobile_phone is not null/phone is not null or mobile_phone is not null/' sql/intermediate/int_customer360__customer_behavior_analysis.sql &amp;&amp; python run.py &gt; /tmp/r</code> | 1493 | true | false |
| 33 | run | <code>grep -n ' m\.' sql/intermediate/int_customer360__customer_behavior_analysis.sql; grep -n -A6 -B4 'ERROR - ✗ intermediate.int_customer360__customer_behavior_analysis' /tmp/runlog</code> | 1764 | true | false |
| 35 | run | <code>sed -i -e 's/m\.country_code/country_code/g' -e 's/m\.state_code/state_code/g' -e 's/m\.city/city/g' sql/intermediate/int_customer360__customer_behavior_analysis.sql; python run.py &gt; /tmp/runlog 2&gt;&amp;1;</code> | 1493 | true | false |
| 37 | run | <code>grep -nE 's\.&#124;z\.' sql/intermediate/int_customer360__customer_behavior_analysis.sql</code> | 1249 | false | false |
| 39 | run | <code>sed -i -e 's/s\.customer_address_line_1/customer_address_line_1/g' -e 's/s\.customer_country_code/customer_country_code/g' -e 's/z\.organization_id/organization_id/g' sql/intermediate/int_customer360_</code> | 394 | false | false |
| 43 | run | <code>cat &gt; sql/intermediate/int_customer360__source_matches.sql &lt;&lt;'SQL'<br>with marketo_stripe as (<br>    select<br>        m.lead_id as marketo_id,<br>        s.customer_id as stripe_id,<br>        m.updated_at as mark</code> | 394 | false | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('customer360.duckdb',read_only=True)<br>checks={<br>'status_key_dups':"select count(*) from (select customer360_id from marts.customer360__status group by 1 ha</code> | 616 | true | false |

### agent action 的 thought/message 命中原句

event 19 / message

```text
put('intermediate','int_customer360__customer_behavior_analysis', '''
```
event 19 / message

```text
    from intermediate.int_customer360__customer_behavior_analysis
```
event 21 / message

```text
 from intermediate.int_customer360__customer_behavior_analysis ba
```
event 25 / message

```text
 from intermediate.int_customer360__customer_behavior_analysis ba
```
event 27 / message

```text
 from intermediate.int_customer360__customer_behavior_analysis ba
```
event 27 / message

```text
 from intermediate.int_customer360__customer_behavior_analysis ba left join intermediate.int_customer360__customer_lifecycle_metrics lm using(primary_email)
```
event 31 / message

```text
Running command: sed -i 's/m\.phone is not null or m\.mobile_phone is not null/phone is not null or mobile_phone is not null/' sql/intermediate/int_customer360__customer_behavior_analysis.sql && python run.py > /tmp/runlog 2>&1; grep -E 'ERROR|Binder Error|Catalog Error|layer complete|completed successfully' /tmp/runlog
```
event 33 / message

```text
Running command: grep -n ' m\.' sql/intermediate/int_customer360__customer_behavior_analysis.sql; grep -n -A6 -B4 'ERROR - ✗ intermediate.int_customer360__customer_behavior_analysis' /tmp/runlog
```
event 35 / message

```text
Running command: sed -i -e 's/m\.country_code/country_code/g' -e 's/m\.state_code/state_code/g' -e 's/m\.city/city/g' sql/intermediate/int_customer360__customer_behavior_analysis.sql; python run.py > /tmp/runlog 2>&1; grep -E 'ERROR|Binder Error|Catalog Error|layer complete|completed successfully' /tmp/runlog
```
event 37 / message

```text
Running command: grep -nE 's\.|z\.' sql/intermediate/int_customer360__customer_behavior_analysis.sql
```
event 39 / message

```text
Running command: sed -i -e 's/s\.customer_address_line_1/customer_address_line_1/g' -e 's/s\.customer_country_code/customer_country_code/g' -e 's/z\.organization_id/organization_id/g' sql/intermediate/int_customer360__customer_behavior_analysis.sql; python run.py > /tmp/runlog 2>&1; grep -E 'ERROR|Binder Error|Catalog Error|layer complete|completed successfully' /tmp/runlog
```
event 45 / message

```text
'behavior_null_email':"select count(*) from intermediate.int_customer360__customer_behavior_analysis where primary_email is null",
```
event 45 / message

```text
for s,t in [('intermediate','int_customer360__marketo'),('intermediate','int_customer360__stripe'),('intermediate','int_customer360__zendesk'),('intermediate','int_customer360__source_matches'),('intermediate','int_customer360__customer_behavior_analysis'),('intermediate','int_customer360__customer_lifecycle_metrics'),('intermediate','int_customer360__risk_assessment'),('marts','customer360__mapping'),('marts','customer360__status'),('marts','customer360__updates')]: print(s+'.'+t,c.execute(f'select count(*) from {s}.{t}').fetchone()[0])
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/011_table_alignment.jsonl`
- S2: `records/011_alignment_impl-003.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-003/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/sql/intermediate/int_customer360__customer_behavior_analysis.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/sql/intermediate/int_customer360__customer_behavior_analysis.sql`
- S6: `records/006_contract_impl-003.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/dacomp-de-impl-003/result.md`
- S10: `data/019_packages_work/019_impl-003_int_customer360__customer_behavior_analysis/019_impl-003_int_customer360__customer_behavior_analysis.json`
- S11: `data/011_agent_alignment/impl-003_attempt_01/int_customer360__customer_behavior_analysis_2025-10-27.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-003/customer360.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-003/agent/.events/sessions`
