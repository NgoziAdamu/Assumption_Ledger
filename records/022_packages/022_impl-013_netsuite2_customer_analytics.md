# impl-013 | marts | netsuite2_customer_analytics | 差异：S1；日期 2025-10-14

## 契约完整原文

S3:2533–2631

```yaml
    - name: netsuite2_customer_analytics
      description: Customer analytics derived from profitability (RFM-style), behavior patterns, retention scoring, and action recommendations
      grain: One row per customer_id (per build date = segmentation_date)
      source_models:
      - intermediate.int_netsuite2__customer_profitability
      - intermediate.int_netsuite2__transaction_details
      - staging.stg_netsuite2__transaction_lines
      business_logic: 'Build a customer analytics view by combining profitability (cp), behavioral patterns (cbp), and retention (cr), then deriving insights and recommendations: - customer_behavior_patterns (cbp): - Join intermediate.int_netsuite2__transaction_details t to staging.stg_netsuite2__transaction_lines tl on transaction_line_id. - Filter rows: tl.entity_id IS NOT NULL, t.account_type_name = ''Income'', t.converted_amount > 0. - Aggregate by tl.entity_id (as customer_id) and t.subsidiary_id: - Transaction frequency: total_transactions = distinct transaction_id count; active_months = distinct calendar months; active_quarters = distinct calendar quarters. - Amounts (Income only): total_revenue = sum of positive amounts; avg_transaction_value = mean of positive amounts (NULLs excluded); transaction_value_volatility = sample standard deviation of positive amounts (NULLs excluded); max/min as per positive Income amounts. - Timing: first_transaction_date = earliest accounting period end; last_transaction_date = latest accounting period end; customer_lifespan_days = days between first and last transaction. - Seasonal counts: q1/q2/q3/q4_transactions = distinct transaction counts by calendar quarter. - Recency: days_since_last_transaction = days between last transaction and today. - analysis_date = today. - customer_retention (cr) from cbp: - retention_category by customer_lifespan_days thresholds: ≥365 Long-term; ≥180 Medium-term; ≥90 Short-term; ≥30 New; else Very New. - activity_status by days_since_last_transaction: ≤30 Highly Active; ≤90 Active; ≤180 At Risk; ≤365 Dormant; else Lost. - avg_transactions_per_month = total_transactions divided by (customer_lifespan_days/30.0) when active_months > 0 and customer_lifespan_days > 0; otherwise 0; no rounding. - retention_probability: 0.95 if days≤30 and total_transactions≥5; 0.80 if days≤60 and total_transactions≥3; 0.60 if days≤90 and total_transactions≥2; 0.30 if days≤180; 0.10 if days≤365; else 0.05. - Carry through total_transactions, total_revenue, avg_transaction_value, days_since_last_transaction. - enhanced_customer_segmentation (ecs) by left joining cp to cr on customer_id: - Carry cp.customer_name, customer_email, subsidiary_id, profitability_segment (cp.customer_segment), total_revenue, net_profit, transaction_count, customer_age_days; avg_transactions_per_month and retention_probability from cr. - value_tier via overall revenue percentile thresholds across cp: ≥90th Platinum; ≥70th Gold; ≥50th Silver; ≥30th Bronze; else Basic (inclusive comparisons). - comprehensive_customer_score = weighted sum of cp revenue/frequency/margin scores plus activity and retention bonuses, capped at 100. - lifecycle_stage: Onboarding if customer_age_days≤90 and activity in (Highly Active, Active); Growth if customer_age_days≤365 and revenue above the overall cp average; Mature if retention in (Long-term, Medium-term) and activity in (Highly Active, Active); At Risk if activity = At Risk; Churned if activity in (Dormant, Lost); else Developing. - segmentation_date = today. - customer_insights by left joining ecs to cbp on customer_id: - Carry transaction_value_volatility and q1–q4_transactions from cbp. - seasonal_preference from the highest of q1..q4 counts: Q1/Q2/Q3/Q4 Peak based on which count is the maximum; ties break by first match in order Q1→Q2→Q3→Q4; else No Clear Pattern. - transaction_consistency: if volatility is NULL or 0 then Single Transaction; else compare volatility to avg_transaction_value: ≤0.3x Very Consistent; ≤0.6x Consistent; ≤1.0x Moderate Variance; else High Variance. - growth_potential: High Growth Potential if lifecycle_stage=Onboarding and comprehensive_customer_score≥70; Expansion Ready if lifecycle_stage=Growth and value_tier in (Gold, Platinum); Loyalty Program Candidate if lifecycle_stage=Mature and activity_status=Highly Active; Recovery Priority if lifecycle_stage=At Risk and value_tier in (Silver, Gold, Platinum); else Standard Growth. - recommended_action (evaluated in order): if lifecycle_stage=Churned and value_tier in (Gold, Platinum) then Win-Back Campaign; else if lifecycle_stage=At Risk then Retention Campaign; else if lifecycle_stage=Onboarding then Onboarding Support; else if growth_potential=Expansion Ready then Upsell Opportunity; else if value_tier=Platinum and activity_status=Highly Active then VIP Treatment; else Regular Engagement. - engagement_frequency (first-match wins): Platinum Weekly; else Gold Bi-weekly; else Silver Monthly; else if lifecycle_stage=At Risk then Immediate; else Quarterly. - Final projection and filters: - Select the columns listed below from customer_insights. - Filter out rows where customer_id IS NULL and where cp.total_revenue ≤ 0. - Create customer_analytics_id as a deterministic hash of customer_id and segmentation_date joined by an underscore. - Sort descending by comprehensive_customer_score, then by total_revenue. - Result grain is one row per customer_id for the build date (segmentation_date).'
      columns:
      - name: customer_id
        data_type: VARCHAR
        description: Customer identifier sourced from cp (and cbp), filtered to NOT NULL in final output
        tests:
        - not_null
      - name: customer_name
        data_type: VARCHAR
        description: Customer name from cp; propagated as-is without trimming or case normalization
      - name: customer_email
        data_type: VARCHAR
        description: Customer email from cp; propagated as-is without validation
      - name: subsidiary_id
        data_type: VARCHAR
        description: Subsidiary identifier from cp (behavioral CTE uses t.subsidiary_id but final value comes from cp)
      - name: profitability_segment
        data_type: VARCHAR
        description: Profitability classification from cp.customer_segment carried through unchanged
      - name: value_tier
        data_type: VARCHAR
        description: 'Revenue-based tier using overall percentile thresholds on cp.total_revenue: ≥P90 Platinum, ≥P70 Gold, ≥P50 Silver, ≥P30 Bronze, else Basic'
      - name: lifecycle_stage
        data_type: VARCHAR
        description: Lifecycle stage derived from customer_age_days, activity_status, retention_category, and cp.total_revenue vs cp average per defined precedence
      - name: activity_status
        data_type: VARCHAR
        description: 'Recency-based activity: ≤30 Highly Active; ≤90 Active; ≤180 At Risk; ≤365 Dormant; else Lost based on days_since_last_transaction'
      - name: retention_category
        data_type: VARCHAR
        description: 'Tenure-based retention: ≥365 Long-term; ≥180 Medium-term; ≥90 Short-term; ≥30 New; else Very New based on customer_lifespan_days'
      - name: total_revenue
        data_type: DOUBLE
        description: Total revenue from cp; final rows require total_revenue > 0; units as defined in cp (no conversion here)
      - name: net_profit
        data_type: DOUBLE
        description: Net profit from cp; no additional adjustments applied
      - name: transaction_count
        data_type: BIGINT
        description: Total transaction count from cp; may differ from cbp total_transactions; no distinct logic applied here
      - name: avg_transactions_per_month
        data_type: DOUBLE
        description: 'Average transactions per 30-day month from cbp: total_transactions/(customer_lifespan_days/30.0) when active_months>0 and lifespan>0 else 0 (no rounding)'
      - name: comprehensive_customer_score
        data_type: INTEGER
        description: Composite score capped at 100 from weighted cp scores plus activity and retention bonuses per defined mapping
      - name: retention_probability
        data_type: DECIMAL(3,2)
        description: 'Predicted retention probability from discrete thresholds: 0.95/0.80/0.60/0.30/0.10/0.05 per recency and total_transactions'
      - name: seasonal_preference
        data_type: VARCHAR
        description: 'Quarter with highest distinct transaction count: ''Qx Peak'' with tie-breaker order Q1>Q2>Q3>Q4; else ''No Clear Pattern'''
      - name: transaction_consistency
        data_type: VARCHAR
        description: 'Volatility classification: NULL or 0→Single Transaction; ≤0.3x avg Very Consistent; ≤0.6x Consistent; ≤1.0x Moderate Variance; else High Variance'
      - name: growth_potential
        data_type: VARCHAR
        description: 'Growth outlook from lifecycle_stage, value_tier, activity_status, and score: High Growth Potential, Expansion Ready, Loyalty Program Candidate, Recovery Priority, or Standard Growth'
      - name: recommended_action
        data_type: VARCHAR
        description: 'Action recommendation precedence: Win-Back Campaign, Retention Campaign, Onboarding Support, Upsell Opportunity, VIP Treatment, else Regular Engagement'
      - name: engagement_frequency
        data_type: VARCHAR
        description: 'Suggested touch cadence: Platinum Weekly; Gold Bi-weekly; Silver Monthly; if lifecycle_stage=At Risk then Immediate; else Quarterly'
      - name: customer_age_days
        data_type: INTEGER
        description: Days since customer creation from cp; integer day count
      - name: segmentation_date
        data_type: DATE
        description: Build date set to current_date for all rows in the run
        tests:
        - not_null
      - name: transaction_value_volatility
        data_type: DOUBLE
        description: Sample standard deviation of positive Income converted_amounts per customer from cbp; NULL if insufficient data
      - name: q1_transactions
        data_type: BIGINT
        description: Distinct Income transaction_id count in calendar Q1 from cbp; non-negative integer
      - name: q2_transactions
        data_type: BIGINT
        description: Distinct Income transaction_id count in calendar Q2 from cbp; non-negative integer
      - name: q3_transactions
        data_type: BIGINT
        description: Distinct Income transaction_id count in calendar Q3 from cbp; non-negative integer
      - name: q4_transactions
        data_type: BIGINT
        description: Distinct Income transaction_id count in calendar Q4 from cbp; non-negative integer
      - name: customer_analytics_id
        data_type: VARCHAR
        description: Deterministic hash of customer_id and segmentation_date joined by an underscore
        tests:
        - not_null
```

## agent 最终 SQL

S4

```sql
WITH behavior AS (SELECT l.entity_id customer_id,t.subsidiary_id,count(DISTINCT t.transaction_id) total_transactions,count(DISTINCT date_trunc('month',t.accounting_period_ending)) active_months,count(DISTINCT quarter(t.accounting_period_ending)) active_quarters,sum(t.converted_amount) total_revenue,avg(t.converted_amount) avg_transaction_value,stddev_samp(t.converted_amount) transaction_value_volatility,max(t.converted_amount) max_transaction_value,min(t.converted_amount) min_transaction_value,min(t.accounting_period_ending) first_transaction_date,max(t.accounting_period_ending) last_transaction_date,date_diff('day',min(t.accounting_period_ending),max(t.accounting_period_ending)) customer_lifespan_days,date_diff('day',max(t.accounting_period_ending),current_date) days_since_last_transaction,current_date analysis_date,count(DISTINCT t.transaction_id) FILTER(WHERE quarter(t.accounting_period_ending)=1) q1_transactions,count(DISTINCT t.transaction_id) FILTER(WHERE quarter(t.accounting_period_ending)=2) q2_transactions,count(DISTINCT t.transaction_id) FILTER(WHERE quarter(t.accounting_period_ending)=3) q3_transactions,count(DISTINCT t.transaction_id) FILTER(WHERE quarter(t.accounting_period_ending)=4) q4_transactions FROM intermediate.int_netsuite2__transaction_details t JOIN staging.stg_netsuite2__transaction_lines l USING(transaction_line_id) WHERE l.entity_id IS NOT NULL AND t.account_type_name='Income' AND t.converted_amount>0 GROUP BY l.entity_id,t.subsidiary_id), retention AS (SELECT *,CASE WHEN customer_lifespan_days>=365 THEN 'Long-term' WHEN customer_lifespan_days>=180 THEN 'Medium-term' WHEN customer_lifespan_days>=90 THEN 'Short-term' WHEN customer_lifespan_days>=30 THEN 'New' ELSE 'Very New' END retention_category,CASE WHEN days_since_last_transaction<=30 THEN 'Highly Active' WHEN days_since_last_transaction<=90 THEN 'Active' WHEN days_since_last_transaction<=180 THEN 'At Risk' WHEN days_since_last_transaction<=365 THEN 'Dormant' ELSE 'Lost' END activity_status,total_transactions/nullif(customer_lifespan_days/30.0,0) avg_transactions_per_month,CASE WHEN days_since_last_transaction<=30 AND total_transactions>=5 THEN .95 WHEN days_since_last_transaction<=60 AND total_transactions>=3 THEN .80 WHEN days_since_last_transaction<=90 AND total_transactions>=2 THEN .60 WHEN days_since_last_transaction<=180 THEN .30 WHEN days_since_last_transaction<=365 THEN .10 ELSE .05 END::DECIMAL(3,2) retention_probability FROM behavior), cp AS (SELECT *,percent_rank() OVER(ORDER BY total_revenue) rev_pct FROM intermediate.int_netsuite2__customer_profitability), enriched AS (SELECT cp.*,r.*,CASE WHEN cp.rev_pct>=.9 THEN 'Platinum' WHEN cp.rev_pct>=.7 THEN 'Gold' WHEN cp.rev_pct>=.5 THEN 'Silver' WHEN cp.rev_pct>=.3 THEN 'Bronze' ELSE 'Basic' END value_tier FROM cp LEFT JOIN retention r ON r.customer_id=cp.customer_id), scored AS (SELECT *,least(100,revenue_score*10+frequency_score*5+margin_score*5+CASE WHEN activity_status='Highly Active' THEN 15 WHEN activity_status='Active' THEN 10 ELSE 0 END+retention_probability*20)::INTEGER comprehensive_customer_score,CASE WHEN customer_age_days<=90 AND activity_status IN ('Highly Active','Active') THEN 'Onboarding' WHEN customer_age_days<=365 AND total_revenue>(SELECT avg(total_revenue) FROM cp) THEN 'Growth' WHEN retention_category IN ('Long-term','Medium-term') AND activity_status IN ('Highly Active','Active') THEN 'Mature' WHEN activity_status='At Risk' THEN 'At Risk' WHEN activity_status IN ('Dormant','Lost') THEN 'Churned' ELSE 'Developing' END lifecycle_stage FROM enriched), insights AS (SELECT *,CASE WHEN q1_transactions>=greatest(q2_transactions,q3_transactions,q4_transactions) THEN 'Q1 Peak' WHEN q2_transactions>=greatest(q1_transactions,q3_transactions,q4_transactions) THEN 'Q2 Peak' WHEN q3_transactions>=greatest(q1_transactions,q2_transactions,q4_transactions) THEN 'Q3 Peak' WHEN q4_transactions>=greatest(q1_transactions,q2_transactions,q3_transactions) THEN 'Q4 Peak' ELSE 'No Clear Pattern' END seasonal_preference,CASE WHEN transaction_value_volatility IS NULL OR transaction_value_volatility=0 THEN 'Single Transaction' WHEN transaction_value_volatility<=.3*avg_transaction_value THEN 'Very Consistent' WHEN transaction_value_volatility<=.6*avg_transaction_value THEN 'Consistent' WHEN transaction_value_volatility<=avg_transaction_value THEN 'Moderate Variance' ELSE 'High Variance' END transaction_consistency,CASE WHEN lifecycle_stage='Onboarding' AND comprehensive_customer_score>=70 THEN 'High Growth Potential' WHEN lifecycle_stage='Growth' AND value_tier IN ('Gold','Platinum') THEN 'Expansion Ready' WHEN lifecycle_stage='Mature' AND activity_status='Highly Active' THEN 'Loyalty Program Candidate' WHEN lifecycle_stage='At Risk' AND value_tier IN ('Silver','Gold','Platinum') THEN 'Recovery Priority' ELSE 'Standard Growth' END growth_potential FROM scored) SELECT customer_id,customer_name,customer_email,subsidiary_id,customer_segment profitability_segment,value_tier,lifecycle_stage,activity_status,retention_category,total_revenue,net_profit,transaction_count,avg_transactions_per_month,comprehensive_customer_score,retention_probability,seasonal_preference,transaction_consistency,growth_potential,CASE WHEN lifecycle_stage='Churned' AND value_tier IN ('Gold','Platinum') THEN 'Win-Back Campaign' WHEN lifecycle_stage='At Risk' THEN 'Retention Campaign' WHEN lifecycle_stage='Onboarding' THEN 'Onboarding Support' WHEN growth_potential='Expansion Ready' THEN 'Upsell Opportunity' WHEN value_tier='Platinum' AND activity_status='Highly Active' THEN 'VIP Treatment' ELSE 'Regular Engagement' END recommended_action,CASE WHEN value_tier='Platinum' THEN 'Weekly' WHEN value_tier='Gold' THEN 'Bi-weekly' WHEN value_tier='Silver' THEN 'Monthly' WHEN lifecycle_stage='At Risk' THEN 'Immediate' ELSE 'Quarterly' END engagement_frequency,customer_age_days,current_date segmentation_date,transaction_value_volatility,q1_transactions,q2_transactions,q3_transactions,q4_transactions,md5(customer_id||'_'||cast(current_date AS VARCHAR)) customer_analytics_id FROM insights WHERE customer_id IS NOT NULL AND total_revenue>0
```

## gold SQL（仅供定位差异）

S5

```sql
-- Customer Analytics and Insights
-- In-depth customer analysis, including behavior patterns, value stratification, and retention analysis
with customer_profitability as (
    select * from intermediate.int_netsuite2__customer_profitability
),

-- Customer transaction behavior analysis
customer_behavior_patterns as (
    select 
        t.subsidiary_id,
        tl.entity_id as customer_id,
        'Customer_' || substring(tl.entity_id, 1, 8) as customer_name,
        'customer_' || substring(tl.entity_id, 1, 8) || '@example.com' as customer_email,
        
        -- Transaction frequency pattern
        count(distinct t.transaction_id) as total_transactions,
        count(distinct date_trunc('month', t.accounting_period_ending)) as active_months,
        count(distinct date_trunc('quarter', t.accounting_period_ending)) as active_quarters,
        
        -- Amount mode
        sum(case when t.account_type_name = 'Income' then t.converted_amount else 0 end) as total_revenue,
        avg(case when t.account_type_name = 'Income' then t.converted_amount else null end) as avg_transaction_value,
        stddev(case when t.account_type_name = 'Income' then t.converted_amount else null end) as transaction_value_volatility,
        max(case when t.account_type_name = 'Income' then t.converted_amount else 0 end) as max_transaction_value,
        min(case when t.account_type_name = 'Income' and t.converted_amount > 0 then t.converted_amount else null end) as min_transaction_value,
        
        -- time pattern
        min(t.accounting_period_ending) as first_transaction_date,
        max(t.accounting_period_ending) as last_transaction_date,
        datediff('day', min(t.accounting_period_ending), max(t.accounting_period_ending)) as customer_lifespan_days,
        
        -- seasonal pattern
        count(distinct case when extract(quarter from t.accounting_period_ending) = 1 then t.transaction_id end) as q1_transactions,
        count(distinct case when extract(quarter from t.accounting_period_ending) = 2 then t.transaction_id end) as q2_transactions,
        count(distinct case when extract(quarter from t.accounting_period_ending) = 3 then t.transaction_id end) as q3_transactions,
        count(distinct case when extract(quarter from t.accounting_period_ending) = 4 then t.transaction_id end) as q4_transactions,
        
        -- Recent activity
        datediff('day', max(t.accounting_period_ending), current_date) as days_since_last_transaction,
        
        current_date as analysis_date
        
    from intermediate.int_netsuite2__transaction_details t
    join staging.stg_netsuite2__transaction_lines tl
        on t.transaction_line_id = tl.transaction_line_id
    where tl.entity_id is not null
        and t.account_type_name = 'Income'
        and t.converted_amount > 0
    group by t.subsidiary_id, tl.entity_id
),

-- Customer retention analysis (simplified version of Cohort analysis)
customer_retention as (
    select 
        cbp.customer_id,
        cbp.customer_name,
        cbp.subsidiary_id,
        cbp.first_transaction_date,
        
        -- Retention period calculation
        case 
            when cbp.customer_lifespan_days >= 365 then 'Long-term (1+ Years)'
            when cbp.customer_lifespan_days >= 180 then 'Medium-term (6-12 Months)'
            when cbp.customer_lifespan_days >= 90 then 'Short-term (3-6 Months)'
            when cbp.customer_lifespan_days >= 30 then 'New Customer (1-3 Months)'
            else 'Very New (<1 Month)'
        end as retention_category,
        
        -- activity score
        case 
            when cbp.days_since_last_transaction <= 30 then 'Highly Active'
            when cbp.days_since_last_transaction <= 90 then 'Active'
            when cbp.days_since_last_transaction <= 180 then 'At Risk'
            when cbp.days_since_last_transaction <= 365 then 'Dormant'
            else 'Lost'
        end as activity_status,
        
        -- Transaction frequency rating
        case 
            when cbp.active_months > 0 and cbp.customer_lifespan_days > 0 
            then (cbp.total_transactions::float / (cbp.customer_lifespan_days / 30.0))
            else 0 
        end as avg_transactions_per_month,
        
        -- Predicted probability of retention
        case 
            when cbp.days_since_last_transaction <= 30 and cbp.total_transactions >= 5 then 0.95
            when cbp.days_since_last_transaction <= 60 and cbp.total_transactions >= 3 then 0.80
            when cbp.days_since_last_transaction <= 90 and cbp.total_transactions >= 2 then 0.60
            when cbp.days_since_last_transaction <= 180 then 0.30
            when cbp.days_since_last_transaction <= 365 then 0.10
            else 0.05
        end as retention_probability,
        
        cbp.total_transactions,
        cbp.total_revenue,
        cbp.avg_transaction_value,
        cbp.days_since_last_transaction
        
    from customer_behavior_patterns cbp
),

-- Customer segmentation enhancement
enhanced_customer_segmentation as (
    select 
        cp.customer_id,
        cp.customer_name,
        cp.customer_email,
        cp.subsidiary_id,
        cp.customer_segment as profitability_segment,
        cr.retention_category,
        cr.activity_status,
        
        -- RFM-Enhanced Analysis
        cp.total_revenue,
        cp.net_profit,
        cp.transaction_count,
        cp.customer_age_days,
        cr.avg_transactions_per_month,
        cr.retention_probability,
        
        -- value stratification
        case 
            when cp.total_revenue >= (select percentile_cont(0.9) within group (order by total_revenue) from customer_profitability) then 'Platinum'
            when cp.total_revenue >= (select percentile_cont(0.7) within group (order by total_revenue) from customer_profitability) then 'Gold'
            when cp.total_revenue >= (select percentile_cont(0.5) within group (order by total_revenue) from customer_profitability) then 'Silver'
            when cp.total_revenue >= (select percentile_cont(0.3) within group (order by total_revenue) from customer_profitability) then 'Bronze'
            else 'Basic'
        end as value_tier,
        
        -- Overall customer rating (0-100)
        least(100, 
            (cp.revenue_score * 20) +
            (cp.frequency_score * 15) +
            (cp.margin_score * 20) +
            (case when cr.activity_status = 'Highly Active' then 25
                  when cr.activity_status = 'Active' then 20
                  when cr.activity_status = 'At Risk' then 10
                  when cr.activity_status = 'Dormant' then 5
                  else 0 end) +
            (case when cr.retention_category = 'Long-term (1+ Years)' then 20
                  when cr.retention_category = 'Medium-term (6-12 Months)' then 15
                  when cr.retention_category = 'Short-term (3-6 Months)' then 10
                  when cr.retention_category = 'New Customer (1-3 Months)' then 5
                  else 0 end)
        ) as comprehensive_customer_score,
        
        -- Customer life cycle stages
        case 
            when cp.customer_age_days <= 90 and cr.activity_status in ('Highly Active', 'Active') then 'Onboarding'
            when cp.customer_age_days <= 365 and cp.total_revenue > (select avg(total_revenue) from customer_profitability) then 'Growth'
            when cr.retention_category in ('Long-term (1+ Years)', 'Medium-term (6-12 Months)') and cr.activity_status in ('Highly Active', 'Active') then 'Mature'
            when cr.activity_status = 'At Risk' then 'At Risk'
            when cr.activity_status in ('Dormant', 'Lost') then 'Churned'
            else 'Developing'
        end as lifecycle_stage,
        
        current_date as segmentation_date
        
    from customer_profitability cp
    left join customer_retention cr on cp.customer_id = cr.customer_id
),

-- Customer Behavior Insights
customer_insights as (
    select 
        ecs.*,
        cbp.transaction_value_volatility,
        cbp.q1_transactions,
        cbp.q2_transactions,
        cbp.q3_transactions,
        cbp.q4_transactions,
        
        -- seasonal preference
        case 
            when greatest(cbp.q1_transactions, cbp.q2_transactions, cbp.q3_transactions, cbp.q4_transactions) = cbp.q1_transactions then 'Q1 Peak'
            when greatest(cbp.q1_transactions, cbp.q2_transactions, cbp.q3_transactions, cbp.q4_transactions) = cbp.q2_transactions then 'Q2 Peak'
            when greatest(cbp.q1_transactions, cbp.q2_transactions, cbp.q3_transactions, cbp.q4_transactions) = cbp.q3_transactions then 'Q3 Peak'
            when greatest(cbp.q1_transactions, cbp.q2_transactions, cbp.q3_transactions, cbp.q4_transactions) = cbp.q4_transactions then 'Q4 Peak'
            else 'No Clear Pattern'
        end as seasonal_preference,
        
        -- transaction consistency
        case 
            when cbp.transaction_value_volatility is null or cbp.transaction_value_volatility = 0 then 'Single Transaction'
            when cbp.transaction_value_volatility <= cbp.avg_transaction_value * 0.3 then 'Very Consistent'
            when cbp.transaction_value_volatility <= cbp.avg_transaction_value * 0.6 then 'Consistent'
            when cbp.transaction_value_volatility <= cbp.avg_transaction_value * 1.0 then 'Moderate Variance'
            else 'High Variance'
        end as transaction_consistency,
        
        -- Growth potential assessment
        case 
            when ecs.lifecycle_stage = 'Onboarding' and ecs.comprehensive_customer_score >= 70 then 'High Growth Potential'
            when ecs.lifecycle_stage = 'Growth' and ecs.value_tier in ('Gold', 'Platinum') then 'Expansion Ready'
            when ecs.lifecycle_stage = 'Mature' and ecs.activity_status = 'Highly Active' then 'Loyalty Program Candidate'
            when ecs.lifecycle_stage = 'At Risk' and ecs.value_tier in ('Silver', 'Gold', 'Platinum') then 'Recovery Priority'
            else 'Standard Growth'
        end as growth_potential,
        
        -- Recommended action
        case 
            when ecs.lifecycle_stage = 'Churned' and ecs.value_tier in ('Gold', 'Platinum') then 'Win-Back Campaign'
            when ecs.lifecycle_stage = 'At Risk' then 'Retention Campaign'
            when ecs.lifecycle_stage = 'Onboarding' then 'Onboarding Support'
            when growth_potential = 'Expansion Ready' then 'Upsell Opportunity'
            when ecs.value_tier = 'Platinum' and ecs.activity_status = 'Highly Active' then 'VIP Treatment'
            else 'Regular Engagement'
        end as recommended_action,
        
        -- Contact frequency recommendations
        case 
            when ecs.value_tier = 'Platinum' then 'Weekly'
            when ecs.value_tier = 'Gold' then 'Bi-weekly'
            when ecs.value_tier = 'Silver' then 'Monthly'
            when ecs.lifecycle_stage = 'At Risk' then 'Immediate'
            else 'Quarterly'
        end as engagement_frequency
        
    from enhanced_customer_segmentation ecs
    left join customer_behavior_patterns cbp on ecs.customer_id = cbp.customer_id
)

select 
    customer_id,
    customer_name,
    customer_email,
    subsidiary_id,
    
    -- Core categories
    profitability_segment,
    value_tier,
    lifecycle_stage,
    activity_status,
    retention_category,
    
    -- financial indicators
    total_revenue,
    net_profit,
    transaction_count,
    avg_transactions_per_month,
    
    -- score
    comprehensive_customer_score,
    retention_probability,
    
    -- behavioral insights
    seasonal_preference,
    transaction_consistency,
    growth_potential,
    
    -- suggestion
    recommended_action,
    engagement_frequency,
    
    -- time indicator
    customer_age_days,
    segmentation_date,
    
    -- Trading pattern statistics
    transaction_value_volatility,
    q1_transactions,
    q2_transactions, 
    q3_transactions,
    q4_transactions,
    
    md5(cast(customer_id as varchar) || '_' || cast(segmentation_date as varchar)) as customer_analytics_id
    
from customer_insights
where customer_id is not null
    and total_revenue > 0
order by comprehensive_customer_score desc, total_revenue desc
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 137 | 181 | 0 | 0 | 22 | 22 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"customer_id":"net03635978059","customer_analytics_id":"0dc25d9aca68b3793d9bb3f16055dd2a","subsidiary_id":"net08136744090"}</code> |
| K2 | <code>{"customer_id":"net02678306485","customer_analytics_id":"de6fe3017165ac52caf173e8706c722c","subsidiary_id":"net79315957917"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| customer_id | 0 | 0 | 44 | VARCHAR | VARCHAR |
| customer_analytics_id | 0 | 0 | 44 | VARCHAR | VARCHAR |
| subsidiary_id | 0 | 0 | 44 | VARCHAR | VARCHAR |
| customer_name | 0 | 0 | 44 | VARCHAR | VARCHAR |
| customer_email | 0 | 0 | 44 | VARCHAR | VARCHAR |
| profitability_segment | 0 | 0 | 44 | VARCHAR | VARCHAR |
| value_tier | 0 | 0 | 44 | VARCHAR | VARCHAR |
| lifecycle_stage | 0 | 0 | 44 | VARCHAR | VARCHAR |
| activity_status | 0 | 0 | 44 | VARCHAR | VARCHAR |
| retention_category | 137 | 137 | 181 | VARCHAR | VARCHAR |
| total_revenue | 0 | 0 | 44 | DOUBLE | DOUBLE |
| net_profit | 0 | 0 | 44 | DOUBLE | DOUBLE |
| transaction_count | 0 | 0 | 44 | BIGINT | BIGINT |
| avg_transactions_per_month | 137 | 137 | 181 | DOUBLE | DOUBLE |
| comprehensive_customer_score | 82 | 82 | 126 | INTEGER | INTEGER |
| retention_probability | 0 | 0 | 44 | DECIMAL(3,2) | DECIMAL(3,2) |
| seasonal_preference | 0 | 0 | 44 | VARCHAR | VARCHAR |
| transaction_consistency | 0 | 0 | 44 | VARCHAR | VARCHAR |
| growth_potential | 0 | 0 | 44 | VARCHAR | VARCHAR |
| recommended_action | 0 | 0 | 44 | VARCHAR | VARCHAR |
| engagement_frequency | 0 | 0 | 44 | VARCHAR | VARCHAR |
| customer_age_days | 0 | 0 | 44 | INTEGER | INTEGER |
| transaction_value_volatility | 0 | 0 | 44 | DOUBLE | DOUBLE |
| q1_transactions | 0 | 0 | 44 | BIGINT | BIGINT |
| q2_transactions | 0 | 0 | 44 | BIGINT | BIGINT |
| q3_transactions | 0 | 0 | 44 | BIGINT | BIGINT |
| q4_transactions | 0 | 0 | 44 | BIGINT | BIGINT |

customer_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"NET03635978059","rows":2}]</code> | <code>[{"value":"NET03635978059","rows":4}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

customer_analytics_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0dc25d9aca68b3793d9bb3f16055dd2a","rows":2}]</code> | <code>[{"value":"0dc25d9aca68b3793d9bb3f16055dd2a","rows":4}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

subsidiary_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"NET08136744090","rows":2}]</code> | <code>[{"value":"NET08136744090","rows":4}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

customer_name 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Customer_NET03635","rows":2}]</code> | <code>[{"value":"Customer_NET03635","rows":4}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

customer_email 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"customer_NET03635@example.com","rows":2}]</code> | <code>[{"value":"customer_NET03635@example.com","rows":4}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

profitability_segment 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Loyal","rows":2}]</code> | <code>[{"value":"Loyal","rows":4}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

value_tier 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Gold","rows":2}]</code> | <code>[{"value":"Gold","rows":4}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

lifecycle_stage 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Growth","rows":2}]</code> | <code>[{"value":"Growth","rows":4}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

activity_status 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Highly Active","rows":2}]</code> | <code>[{"value":"Highly Active","rows":4}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

retention_category 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | Very New | <code>Very New (&lt;1 Month)</code> |

total_revenue 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"853.99","rows":2}]</code> | <code>[{"value":"853.99","rows":4}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

net_profit 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"853.99","rows":2}]</code> | <code>[{"value":"853.99","rows":4}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

transaction_count 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"1","rows":2}]</code> | <code>[{"value":"1","rows":4}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

avg_transactions_per_month 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | null | 0.0 |

comprehensive_customer_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | 91 | 100 |

retention_probability 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0.30","rows":2}]</code> | <code>[{"value":"0.30","rows":4}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

seasonal_preference 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Q4 Peak","rows":2}]</code> | <code>[{"value":"Q4 Peak","rows":4}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

transaction_consistency 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Single Transaction","rows":2}]</code> | <code>[{"value":"Single Transaction","rows":4}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

growth_potential 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Expansion Ready","rows":2}]</code> | <code>[{"value":"Expansion Ready","rows":4}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

recommended_action 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Upsell Opportunity","rows":2}]</code> | <code>[{"value":"Upsell Opportunity","rows":4}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

engagement_frequency 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Bi-weekly","rows":2}]</code> | <code>[{"value":"Bi-weekly","rows":4}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

customer_age_days 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"365","rows":2}]</code> | <code>[{"value":"365","rows":4}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

transaction_value_volatility 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":2}]</code> | <code>[{"value":null,"rows":4}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

q1_transactions 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0","rows":2}]</code> | <code>[{"value":"0","rows":4}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

q2_transactions 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0","rows":2}]</code> | <code>[{"value":"0","rows":4}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

q3_transactions 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0","rows":2}]</code> | <code>[{"value":"0","rows":4}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

q4_transactions 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"1","rows":2}]</code> | <code>[{"value":"1","rows":4}]</code> |
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
| A2_all_null_column | <code>2列；[{"column":"avg_transactions_per_month","table_rows":137}]</code> |
| A3_constant_nonnull_column | <code>13列；[{"column":"profitability_segment","value":"Loyal"}]</code> |
| A4_equal_columns | <code>3组；[{"columns":["total_revenue","net_profit"],"nonnull_equal_rows":137,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>3组；[{"columns":["total_revenue","net_profit"],"nonnull_equal_rows":137,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| C9_agent_runtime_text | <code>S4:1 current_date；命中数=4</code> |
| C9_gold_runtime_text | <code>S5:39 current_date；命中数=3</code> |
| C9_contract_runtime_text | <code>S3:2540 today；命中数=4</code> |
| D10_keyword_in_any_result_field | <code>命中数=3；assistant_trajectory 2026-10-25 02:32:19,445 - WARNING - Skipping netsuite2_customer_analytics: SQL file does not exist (sql/marts/netsuite2_customer_analytics.sql)</code> |

## 轨迹索引（不放输出原文）

本题事件总数：67；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions/500adc0e-2b33-46-b20270d2bdbb488/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>find sql -type f &#124; sort &#124; wc -l; find sql -type f &#124; sort; cat config/layer_dependencies.yaml; sed -n '1,220p' run.py</code> | 16959 | true | false |
| 9 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>print(len(c['staging_contract']['tables']),len(c['modeling_spec']['intermediate_models']),len(c['modeling_spec']['marts_mo</code> | 5234 | false | false |
| 15 | run | <code>mkdir -p sql/{staging,intermediate,marts} &amp;&amp; cat &gt; /tmp/generate.py &lt;&lt;'PY'<br>import yaml, os<br>c=yaml.safe_load(open('docs/data_contract.yaml'))<br>raw=yaml.safe_load(open('netsuite_start.yaml'))<br># per-table</code> | 0 | false | false |
| 17 | run | <code>cat &gt; /tmp/inter.py &lt;&lt;'PY'<br>from pathlib import Path<br>base=Path('sql/intermediate')<br>models={<br>'int_netsuite2__accounts':'''SELECT account_id, parent_id, account_number, name, type_name, general_rate_type</code> | 0 | false | false |
| 19 | run | <code>cat &gt;&gt; /tmp/inter.py &lt;&lt;'PY'<br>models2={<br>'int_netsuite2__customer_profitability':'''WITH tx AS (SELECT t.*, l.entity_id AS customer_id, 'Customer_'&#124;&#124;left(l.entity_id,8) AS customer_name, 'customer_'&#124;&#124;lef</code> | 0 | false | false |
| 21 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -80 /tmp/runlog</code> | 8156 | true | false |
| 25 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/staging/stg_netsuite2__consolidated_exchange_rates.sql');s=p.read_text().replace('raw.netsuite2_exchange_rate_data','raw.netsuite2_consolidated_exc</code> | 0 | false | false |
| 27 | run | <code>cat &gt;&gt; /tmp/more.py &lt;&lt;'PY'<br>(p/'int_netsuite2__cash_flow_forecasting.sql').write_text("""WITH hist AS (SELECT * FROM intermediate.int_netsuite2__cash_flow_analysis WHERE analysis_month&gt;=date_trunc('mon</code> | 0 | false | false |
| 29 | run | <code>cat &gt; /tmp/marts.py &lt;&lt;'PY'<br>from pathlib import Path<br>m=Path('sql/marts')<br>passmodels={'netsuite2_balance_sheet':'intermediate.int_netsuite2__balance_sheet','netsuite2_income_statement':'intermediate.int</code> | 0 | false | false |
| 33 | run | <code>cat sql/intermediate/int_netsuite2__data_quality_metrics.sql; sed -n '1,60p' sql/intermediate/int_netsuite2__cash_flow_forecasting.sql</code> | 7098 | false | false |
| 35 | run | <code>find sql/intermediate -type f -printf '%f\n' &#124; sort; grep 'ERROR - ✗' /tmp/runlog2</code> | 1304 | false | false |
| 39 | run | <code>cat &gt; /tmp/marts_more.py &lt;&lt;'PY'<br>from pathlib import Path<br>m=Path('sql/marts')<br>for name,src in [('netsuite__transaction_details','staging.stg_netsuite__transaction_lines'),('netsuite__transaction_detail</code> | 817 | false | false |
| 41 | run | <code>grep -o 'count(DISTINCT[^)]*) total_transactions' sql/marts/netsuite2_vendor_risk_analysis.sql; head -c 1600 sql/marts/netsuite2_vendor_risk_analysis.sql; cat sql/intermediate/int_netsuite2__data_qual</code> | 3957 | false | false |
| 47 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/marts/netsuite2_vendor_risk_analysis.sql');s=p.read_text().replace('FROM intermediate.int_netsuite2__transaction_details t JOIN staging.stg_netsuit</code> | 488 | false | false |
| 51 | run | <code>cat sql/intermediate/int_netsuite2__transaction_lines.sql; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('netsuite.duckdb',read_only=True)<br>for t in ['stg_netsuite2__transaction_lines','int_netsuite2_</code> | 7032 | false | false |
| 57 | run | <code>cat &gt; sql/intermediate/int_netsuite2__data_quality_metrics.sql &lt;&lt;'SQL'<br>WITH transaction_stats AS (<br>    SELECT<br>        'Transactions' AS table_name,<br>        count(*)::BIGINT AS total_records,<br>        c</code> | 331 | false | false |

### agent action 的 thought/message 命中原句

event 29 / message

```text
(m/'netsuite2_customer_analytics.sql').write_text("""WITH behavior AS (SELECT l.entity_id customer_id,t.subsidiary_id,count(DISTINCT t.transaction_id) total_transactions,count(DISTINCT date_trunc('month',t.accounting_period_ending)) active_months,count(DISTINCT quarter(t.accounting_period_ending)) active_quarters,sum(t.converted_amount) total_revenue,avg(t.converted_amount) avg_transaction_value,stddev_samp(t.converted_amount) transaction_value_volatility,max(t.converted_amount) max_transaction_value,min(t.converted_amount) min_transaction_value,min(t.accounting_period_ending) first_transaction_date,max(t.accounting_period_ending) last_transaction_date,date_diff('day',min(t.accounting_period_ending),max(t.accounting_period_ending)) customer_lifespan_days,date_diff('day',max(t.accounting_period_ending),current_date) days_since_last_transaction,current_date analysis_date,count(DISTINCT t.transaction_id) FILTER(WHERE quarter(t.accounting_period_ending)=1) q1_transactions,count(DISTINCT t.transaction_id) FILTER(WHERE quarter(t.accounting_period_ending)=2) q2_transactions,count(DISTINCT t.transaction_id) FILTER(WHERE quarter(t.accounting_period_ending)=3) q3_transactions,count(DISTINCT t.transaction_id) FILTER(WHERE quarter(t.accounting_period_ending)=4) q4_transactions FROM intermediate.int_netsuite2__transaction_details t JOIN staging.stg_netsuite2__transaction_lines l USING(transaction_line_id) WHERE l.entity_id IS NOT NULL AND t.account_type_name='Income' AND t.converted_amount>0 GROUP BY l.entity_id,t.subsidiary_id), retention AS (SELECT *,CASE WHEN customer_lifespan_days>=365 THEN 'Long-term' WHEN customer_lifespan_days>=180 THEN 'Medium-term' WHEN customer_lifespan_days>=90 THEN 'Short-term' WHEN customer_lifespan_days>=30 THEN 'New' ELSE 'Very New' END retention_category,CASE WHEN days_since_last_transaction<=30 THEN 'Highly Active' WHEN days_since_last_transaction<=90 THEN 'Active' WHEN days_since_last_transaction<=180 THEN 'At Risk' WHEN days_since_last_transaction<=365 THEN 'Dormant' ELSE 'Lost' END activity_status,total_transactions/nullif(customer_lifespan_days/30.0,0) avg_transactions_per_month,CASE WHEN days_since_last_transaction<=30 AND total_transactions>=5 THEN .95 WHEN days_since_last_transaction<=60 AND total_transactions>=3 THEN .80 WHEN days_since_last_transaction<=90 AND total_transactions>=2 THEN .60 WHEN days_since_last_transaction<=180 THEN .30 WHEN days_since_last_transaction<=365 THEN .10 ELSE .05 END::DECIMAL(3,2) retention_probability FROM behavior), cp AS (SELECT *,percent_rank() OVER(ORDER BY total_revenue) rev_pct FROM intermediate.int_netsuite2__customer_profitability), enriched AS (SELECT cp.*,r.*,CASE WHEN cp.rev_pct>=.9 THEN 'Platinum' WHEN cp.rev_pct>=.7 THEN 'Gold' WHEN cp.rev_pct>=.5 THEN 'Silver' WHEN cp.rev_pct>=.3 THEN 'Bronze' ELSE 'Basic' END value_tier FROM cp LEFT JOIN retention r ON r.customer_id=cp.customer_id), scored AS (SELECT *,least(100,revenue_score*10+frequency_score*5+margin_score*5+CASE WHEN activity_status='Highly Active' THEN 15 WHEN activity_status='Active' THEN 10 ELSE 0 END+retention_probability*20)::INTEGER comprehensive_customer_score,CASE WHEN customer_age_days<=90 AND activity_status IN ('Highly Active','Active') THEN 'Onboarding' WHEN customer_age_days<=365 AND total_revenue>(SELECT avg(total_revenue) FROM cp) THEN 'Growth' WHEN retention_category IN ('Long-term','Medium-term') AND activity_status IN ('Highly Active','Active') THEN 'Mature' WHEN activity_status='At Risk' THEN 'At Risk' WHEN activity_status IN ('Dormant','Lost') THEN 'Churned' ELSE 'Developing' END lifecycle_stage FROM enriched), insights AS (SELECT *,CASE WHEN q1_transactions>=greatest(q2_transactions,q3_transactions,q4_transactions) THEN 'Q1 Peak' WHEN q2_transactions>=greatest(q1_transactions,q3_transactions,q4_transactions) THEN 'Q2 Peak' WHEN q3_transactions>=greatest(q1_transactions,q2_transactions,q4_transactions) THEN 'Q3 Peak' WHEN q4_transactions>=greatest(q1_transactions,q2_transactions,q3_transactions) THEN 'Q4 Peak' ELSE 'No Clear Pattern' END seasonal_preference,CASE WHEN transaction_value_volatility IS NULL OR transaction_value_volatility=0 THEN 'Single Transaction' WHEN transaction_value_volatility<=.3*avg_transaction_value THEN 'Very Consistent' WHEN transaction_value_volatility<=.6*avg_transaction_value THEN 'Consistent' WHEN transaction_value_volatility<=avg_transaction_value THEN 'Moderate Variance' ELSE 'High Variance' END transaction_consistency,CASE WHEN lifecycle_stage='Onboarding' AND comprehensive_customer_score>=70 THEN 'High Growth Potential' WHEN lifecycle_stage='Growth' AND value_tier IN ('Gold','Platinum') THEN 'Expansion Ready' WHEN lifecycle_stage='Mature' AND activity_status='Highly Active' THEN 'Loyalty Program Candidate' WHEN lifecycle_stage='At Risk' AND value_tier IN ('Silver','Gold','Platinum') THEN 'Recovery Priority' ELSE 'Standard Growth' END growth_potential FROM scored) SELECT customer_id,customer_name,customer_email,subsidiary_id,customer_segment profitability_segment,value_tier,lifecycle_stage,activity_status,retention_category,total_revenue,net_profit,transaction_count,avg_transactions_per_month,comprehensive_customer_score,retention_probability,seasonal_preference,transaction_consistency,growth_potential,CASE WHEN lifecycle_stage='Churned' AND value_tier IN ('Gold','Platinum') THEN 'Win-Back Campaign' WHEN lifecycle_stage='At Risk' THEN 'Retention Campaign' WHEN lifecycle_stage='Onboarding' THEN 'Onboarding Support' WHEN growth_potential='Expansion Ready' THEN 'Upsell Opportunity' WHEN value_tier='Platinum' AND activity_status='Highly Active' THEN 'VIP Treatment' ELSE 'Regular Engagement' END recommended_action,CASE WHEN value_tier='Platinum' THEN 'Weekly' WHEN value_tier='Gold' THEN 'Bi-weekly' WHEN value_tier='Silver' THEN 'Monthly' WHEN lifecycle_stage='At Risk' THEN 'Immediate' ELSE 'Quarterly' END engagement_frequency,customer_age_days,current_date segmentation_date,transaction_value_volatility,q1_transactions,q2_transactions,q3_transactions,q4_transactions,md5(customer_id||'_'||cast(current_date AS VARCHAR)) customer_analytics_id FROM insights WHERE customer_id IS NOT NULL AND total_revenue>0""")
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/011_table_alignment.jsonl`
- S2: `records/011_alignment_impl-013.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-013/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/sql/marts/netsuite2_customer_analytics.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/sql/marts/netsuite2_customer_analytics.sql`
- S6: `records/006_contract_impl-013.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/dacomp-de-impl-013/result.md`
- S10: `data/022_packages_work/022_impl-013_netsuite2_customer_analytics/022_impl-013_netsuite2_customer_analytics.json`
- S11: `data/011_agent_alignment/impl-013/netsuite2_customer_analytics_2025-10-14.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-013/netsuite.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-013/agent/.events/sessions`
