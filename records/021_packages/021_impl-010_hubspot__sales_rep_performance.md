# impl-010 | sales | hubspot__sales_rep_performance | 差异：S1；日期 原记录

## 契约完整原文

S3:1797–1931

```yaml
    - name: hubspot__sales_rep_performance
      schema: sales
      description: Sales representative performance analytics with rankings, segment metrics, trends, and derived classifications
      grain: One row per owner_id (only reps with total_deals > 0)
      source_models:
      - intermediate.int_hubspot__owner_performance_metrics
      - intermediate.int_hubspot__deal_performance_metrics
      business_logic: '- Start from intermediate.int_hubspot__owner_performance_metrics and retain only owners where total_deals > 0. - Build monthly deal performance per owner from intermediate.int_hubspot__deal_performance_metrics: - Group by owner_id and the year/month of created_date; exclude rows where created_date is NULL. - monthly_deals_created: count distinct deal_id per month. - monthly_deals_won: count distinct deal_id where deal_status = ''Won''. - monthly_revenue: sum deal_amount where deal_status = ''Won'' (0 otherwise). - monthly_pipeline_added: sum deal_amount where deal_status = ''Open'' (0 otherwise). - monthly_win_rate: if decided deals (Won or Lost) exist, compute 100 × (won / decided); otherwise 0. - monthly_avg_cycle_time: average deal_cycle_time_days for won deals; NULL if none. - Aggregate per-owner trends over monthly data: - Use month_index = performance_year*12 + performance_month and current_month_index from current_date. - recent_6m_avg_revenue: average monthly_revenue where month_index >= current_month_index - 6 (inclusive). - prior_6m_avg_revenue: average monthly_revenue where month_index between current_month_index - 12 and current_month_index - 7 (inclusive). - recent_6m_avg_win_rate / prior_6m_avg_win_rate: analogous averages over monthly_win_rate (percent values). - revenue_volatility: standard deviation of monthly_revenue; activity_consistency: standard deviation of monthly_deals_created. - recent_active_months: count of monthly rows in the last 3 calendar months (relative to current_date), inclusive. - Territory and segment analysis per owner from all deals: - primary_deal_segment: most frequent deal_size_category; ties break by ascending category label. - segments_covered: count distinct deal_size_category. - enterprise/large/medium/small_revenue: sum won deal_amount within each named deal_size_category. - enterprise_win_rate / large_deal_win_rate: if decided deals in the segment exist, compute 100 × (won / decided); otherwise 0. - Rankings and percentiles from owner metrics: - revenue_rank: best-to-worst by total_won_revenue; win_rate_rank: best-to-worst by win_rate_percentage; volume_rank: best-to-worst by won_deals. - efficiency_rank: best-to-worst by avg_won_cycle_time, treating NULL as 999. - revenue_percentile / win_rate_percentile / volume_percentile: percentile position (0–100) across all reps using ascending order of each metric; peers share the same percentile. - efficiency_percentile: percentile position (0–100) using descending order of avg_won_cycle_time, treating NULL as 999 (longer cycles → higher percentile). - overall_performance_score: weighted sum of these percentiles (revenue 40%, win rate 25%, volume 20%, efficiency 15%), then scaled by ×100 to a 0–10,000 range. - Ties in ranks are resolved by the database’s implicit peer order. - Join rankings to trends and territory by owner_id (cast trend/territory owner_id to VARCHAR); unmatched trend/territory values remain NULL. - Derivations: - revenue_trend_percentage: if prior_6m_avg_revenue > 0 and recent_6m_avg_revenue is not NULL, compute 100 × (recent - prior) / prior; else NULL. - win_rate_trend_points: if prior_6m_avg_win_rate > 0 and recent_6m_avg_win_rate is not NULL, compute recent - prior; else NULL. - performance_tier: >=80 Top Performer; >=60 High Performer; >=40 Core Performer; >=20 Developing Performer; else Needs Improvement. - performance_trend: >=20 Strong Growth; >=5 Steady Growth; >=-5 Stable; >=-20 Declining; else Significant Decline (NULLs map to the else). - sales_specialization: Enterprise Specialist if enterprise_revenue strictly exceeds (large + medium + small); Large Deal Specialist if large_revenue strictly exceeds (enterprise + medium + small); else if segments_covered >= 3 then Generalist; otherwise Focused Seller. - development_focus (first-match order): low win rate + long cycle → Focus on Qualification and Process; low win rate → Improve Win Rate; very long cycle → Accelerate Sales Cycle; few wins → Increase Activity Volume; declining revenue trend → Address Performance Decline; else Maintain Current Performance. - activity_level (first-match): Highly Active (recent_active_months >= 3 and total_deals >= 10); Active (recent_active_months >= 2 and total_deals >= 5); Moderately Active (recent_active_months >= 1); else Low Activity. - pipeline_health_status: compare current_pipeline_value to total_won_revenue thresholds: >=2× Strong Pipeline; >=1× Healthy Pipeline; >=0.5× Adequate Pipeline; else Weak Pipeline. - Output rows are ordered by overall_performance_score descending.'
      columns:
      - name: owner_id
        data_type: VARCHAR
        description: Sales rep identifier; grouping key; exactly one output row per owner_id with total_deals > 0
        tests:
        - not_null
        - unique
      - name: owner_name
        data_type: VARCHAR
        description: Sales rep name from owner metrics; passed through from source (may be NULL)
      - name: owner_email
        data_type: VARCHAR
        description: Sales rep email from owner metrics; passed through from source (may be NULL)
      - name: total_deals
        data_type: BIGINT
        description: Total number of deals attributed to the rep from owner metrics; used for filters and activity_level thresholds
      - name: won_deals
        data_type: BIGINT
        description: Count of won deals from owner metrics; used for volume_rank and development_focus
      - name: total_won_revenue
        data_type: DECIMAL(38,2)
        description: Sum of deal_amount for won deals from owner metrics; basis for revenue_rank, revenue_percentile, and pipeline health thresholds
      - name: win_rate_percentage
        data_type: DOUBLE
        description: Overall win rate percentage (0–100) from owner metrics; used for win_rate_rank and percentiles
      - name: avg_won_cycle_time
        data_type: DOUBLE
        description: Average days to close for won deals from owner metrics; NULL permitted; for ranking, NULL treated as 999
      - name: current_pipeline_value
        data_type: DECIMAL(38,2)
        description: Current open pipeline value from owner metrics (alias of pipeline_value); used for pipeline_health_status thresholds
      - name: enterprise_win_rate
        data_type: DOUBLE
        description: Enterprise (100K+) segment win rate in percent; if no decided enterprise deals then 0; computed as 100×won/decided
      - name: large_deal_win_rate
        data_type: DOUBLE
        description: Large (50K-100K) segment win rate in percent; if no decided large deals then 0; computed as 100×won/decided
      - name: enterprise_revenue
        data_type: DECIMAL(38,2)
        description: Sum of won deal_amount in Enterprise (100K+) segment; NULL if no territory data joined
      - name: large_revenue
        data_type: DECIMAL(38,2)
        description: Sum of won deal_amount in Large (50K-100K) segment; NULL if no territory data joined
      - name: medium_revenue
        data_type: DECIMAL(38,2)
        description: Sum of won deal_amount in Medium (10K-50K) segment; NULL if no territory data joined
      - name: small_revenue
        data_type: DECIMAL(38,2)
        description: Sum of won deal_amount in Small (<10K) segment; NULL if no territory data joined
      - name: revenue_rank
        data_type: BIGINT
        description: Integer rank by total_won_revenue descending across all reps; 1 is highest revenue; ties resolved by peer order
      - name: win_rate_rank
        data_type: BIGINT
        description: Integer rank by win_rate_percentage descending across all reps; 1 is highest win rate; ties resolved by peer order
      - name: volume_rank
        data_type: BIGINT
        description: Integer rank by won_deals descending across all reps; 1 is most wins; ties resolved by peer order
      - name: efficiency_rank
        data_type: BIGINT
        description: Integer rank by avg_won_cycle_time ascending, treating NULL as 999; 1 is shortest cycle; ties resolved by peer order
      - name: revenue_percentile
        data_type: DOUBLE
        description: Percentile (0–100) using ascending order of total_won_revenue; peers share the same percentile
      - name: win_rate_percentile
        data_type: DOUBLE
        description: Percentile (0–100) using ascending order of win_rate_percentage; peers share the same percentile
      - name: volume_percentile
        data_type: DOUBLE
        description: Percentile (0–100) using ascending order of won_deals; peers share the same percentile
      - name: efficiency_percentile
        data_type: DOUBLE
        description: Percentile (0–100) using descending order of avg_won_cycle_time with NULL treated as 999; higher values indicate longer cycles
      - name: overall_performance_score
        data_type: DOUBLE
        description: Weighted sum of percentiles (revenue 40%, win rate 25%, volume 20%, efficiency 15%) scaled by ×100; range 0–10,000
      - name: performance_tier
        data_type: VARCHAR
        description: 'Tier by overall_performance_score: >=80 Top, >=60 High, >=40 Core, >=20 Developing, else Needs Improvement'
      - name: sales_specialization
        data_type: VARCHAR
        description: Enterprise Specialist if enterprise_revenue > (large + medium + small), Large Deal Specialist if large_revenue > (enterprise + medium + small), else Generalist if segments_covered >= 3, otherwise Focused Seller
      - name: development_focus
        data_type: VARCHAR
        description: 'First-match guidance: low win rate + long cycle → process; low win rate → improve; very long cycle → accelerate; few wins → increase volume; declining trend → address; else maintain'
      - name: pipeline_health_status
        data_type: VARCHAR
        description: 'Pipeline health by current_pipeline_value versus total_won_revenue: >=2x Strong, >=1x Healthy, >=0.5x Adequate, else Weak'
      - name: primary_deal_segment
        data_type: VARCHAR
        description: Most frequent deal_size_category with tie-break by ascending label; NULL if no deal data
      - name: segments_covered
        data_type: BIGINT
        description: Count of distinct deal_size_category values across the rep’s deals; NULL if no deal data
      - name: activity_level
        data_type: VARCHAR
        description: 'Activity classification by recent_active_months and total_deals with ordered thresholds: Highly Active, Active, Moderately Active, or Low Activity'
      - name: activity_consistency
        data_type: DOUBLE
        description: Standard deviation of monthly_deals_created; higher implies more variability; may be NULL with limited data
      - name: recent_active_months
        data_type: BIGINT
        description: Count of months in the last 3-month window with any monthly activity row (based on created_date); integer >= 0
      - name: performance_trend
        data_type: VARCHAR
        description: 'Trend label from revenue_trend_percentage: >=20 Strong Growth, >=5 Steady Growth, >=-5 Stable, >=-20 Declining, else Significant Decline (NULLs map to else)'
      - name: revenue_trend_percentage
        data_type: DOUBLE
        description: Percent change between recent_6m_avg_revenue and prior_6m_avg_revenue; NULL if prior <= 0 or recent is NULL
      - name: win_rate_trend_points
        data_type: DOUBLE
        description: Difference in percentage points between recent_6m_avg_win_rate and prior_6m_avg_win_rate; NULL if prior <= 0 or recent is NULL
      - name: revenue_volatility
        data_type: DOUBLE
        description: Standard deviation of monthly_revenue; may be NULL with limited data
      - name: recent_6m_avg_revenue
        data_type: DOUBLE
        description: Average monthly_revenue where month_index >= current_month_index - 6; includes months with zero revenue if present; NULL if no months
      - name: prior_6m_avg_revenue
        data_type: DOUBLE
        description: Average monthly_revenue where month_index is between current_month_index - 12 and current_month_index - 7; NULL if no months
      - name: recent_6m_avg_win_rate
        data_type: DOUBLE
        description: Average monthly_win_rate (percent) where month_index >= current_month_index - 6; NULL if no months
      - name: prior_6m_avg_win_rate
        data_type: DOUBLE
        description: Average monthly_win_rate (percent) where month_index is between current_month_index - 12 and current_month_index - 7; NULL if no months
```

## agent 最终 SQL

S4

```sql
with om as (select * from intermediate.int_hubspot__owner_performance_metrics where total_deals>0), d as (select *,year(created_date) y,month(created_date) m from intermediate.int_hubspot__deal_performance_metrics), monthly as (select owner_id,y performance_year,m performance_month,y*12+m month_index,count(distinct deal_id) monthly_deals_created,sum(case when deal_status='Won' then 1 else 0 end) monthly_deals_won,sum(case when deal_status='Won' then deal_amount else 0 end) monthly_revenue,sum(case when deal_status='Open' then deal_amount else 0 end) monthly_pipeline_added,100.0*count(*) filter(where deal_status='Won')/nullif(count(*) filter(where deal_status in('Won','Lost')),0) monthly_win_rate,avg(deal_cycle_time_days) filter(where deal_status='Won') monthly_avg_cycle_time from d where created_date is not null group by 1,2,3), trends as (select owner_id,avg(monthly_revenue) filter(where month_index>=year(current_date)*12+month(current_date)-6) recent_6m_avg_revenue,avg(monthly_revenue) filter(where month_index between year(current_date)*12+month(current_date)-12 and year(current_date)*12+month(current_date)-7) prior_6m_avg_revenue,avg(monthly_win_rate) filter(where month_index>=year(current_date)*12+month(current_date)-6) recent_6m_avg_win_rate,avg(monthly_win_rate) filter(where month_index between year(current_date)*12+month(current_date)-12 and year(current_date)*12+month(current_date)-7) prior_6m_avg_win_rate,stddev_samp(monthly_revenue) revenue_volatility,stddev_samp(monthly_deals_created) activity_consistency,count(*) filter(where month_index>=year(current_date)*12+month(current_date)-2) recent_active_months from monthly group by 1), seg as (select owner_id,mode() within group(order by deal_size_category) primary_deal_segment,count(distinct deal_size_category)::bigint segments_covered,sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Enterprise (100K+)') enterprise_revenue,sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Large (50K-100K)') large_revenue,sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Medium (10K-50K)') medium_revenue,sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Small (<10K)') small_revenue from d group by 1), ranks as (select *,row_number() over(order by total_won_revenue desc) revenue_rank,row_number() over(order by win_rate_percentage desc) win_rate_rank,row_number() over(order by won_deals desc) volume_rank,row_number() over(order by coalesce(avg_won_cycle_time,999)) efficiency_rank,100*percent_rank() over(order by total_won_revenue) revenue_percentile,100*percent_rank() over(order by win_rate_percentage) win_rate_percentile,100*percent_rank() over(order by won_deals) volume_percentile,100*percent_rank() over(order by coalesce(avg_won_cycle_time,999) desc) efficiency_percentile from om), joined as (select r.*,s.primary_deal_segment,s.segments_covered,s.enterprise_revenue,s.large_revenue,s.medium_revenue,s.small_revenue,t.activity_consistency,t.recent_active_months,t.revenue_volatility,t.recent_6m_avg_revenue,t.prior_6m_avg_revenue,t.recent_6m_avg_win_rate,t.prior_6m_avg_win_rate,case when t.prior_6m_avg_revenue>0 then 100*(t.recent_6m_avg_revenue-t.prior_6m_avg_revenue)/t.prior_6m_avg_revenue end revenue_trend_percentage,case when t.prior_6m_avg_win_rate>0 then t.recent_6m_avg_win_rate-t.prior_6m_avg_win_rate end win_rate_trend_points from ranks r left join seg s on cast(r.owner_id as varchar)=cast(s.owner_id as varchar) left join trends t on cast(r.owner_id as varchar)=cast(t.owner_id as varchar)), scored as (select *,revenue_percentile*40+win_rate_percentile*25+volume_percentile*20+efficiency_percentile*15 overall_performance_score from joined) select owner_id,owner_name,owner_email,total_deals,won_deals,total_won_revenue,win_rate_percentage,avg_won_cycle_time,pipeline_value current_pipeline_value,enterprise_win_rate,large_deal_win_rate,enterprise_revenue,large_revenue,medium_revenue,small_revenue,revenue_rank,win_rate_rank,volume_rank,efficiency_rank,revenue_percentile,win_rate_percentile,volume_percentile,efficiency_percentile,overall_performance_score,case when overall_performance_score>=80 then 'Top Performer' when overall_performance_score>=60 then 'High Performer' when overall_performance_score>=40 then 'Core Performer' when overall_performance_score>=20 then 'Developing Performer' else 'Needs Improvement' end performance_tier,case when enterprise_revenue>coalesce(large_revenue,0)+coalesce(medium_revenue,0)+coalesce(small_revenue,0) then 'Enterprise Specialist' when large_revenue>coalesce(enterprise_revenue,0)+coalesce(medium_revenue,0)+coalesce(small_revenue,0) then 'Large Deal Specialist' when segments_covered>=3 then 'Generalist' else 'Focused Seller' end sales_specialization,case when win_rate_percentage<15 and avg_won_cycle_time>90 then 'Focus on Qualification and Process' when win_rate_percentage<15 then 'Improve Win Rate' when avg_won_cycle_time>120 then 'Accelerate Sales Cycle' when won_deals<5 then 'Increase Activity Volume' when revenue_trend_percentage< -5 then 'Address Performance Decline' else 'Maintain Current Performance' end development_focus,case when pipeline_value>=2*total_won_revenue then 'Strong Pipeline' when pipeline_value>=total_won_revenue then 'Healthy Pipeline' when pipeline_value>=0.5*total_won_revenue then 'Adequate Pipeline' else 'Weak Pipeline' end pipeline_health_status,primary_deal_segment,segments_covered,case when recent_active_months>=3 and total_deals>=10 then 'Highly Active' when recent_active_months>=2 and total_deals>=5 then 'Active' when recent_active_months>=1 then 'Moderately Active' else 'Low Activity' end activity_level,activity_consistency,recent_active_months,case when revenue_trend_percentage>=20 then 'Strong Growth' when revenue_trend_percentage>=5 then 'Steady Growth' when revenue_trend_percentage>=-5 then 'Stable' when revenue_trend_percentage>=-20 then 'Declining' else 'Significant Decline' end performance_trend,revenue_trend_percentage,win_rate_trend_points,revenue_volatility,recent_6m_avg_revenue,prior_6m_avg_revenue,recent_6m_avg_win_rate,prior_6m_avg_win_rate from scored order by overall_performance_score desc
```

## gold SQL（仅供定位差异）

S5

```sql
-- Sales representative performance mart table
-- Individual sales rep analytics with rankings, targets, and performance trends
with sales_rep_base as (
    select *
    from intermediate.int_hubspot__owner_performance_metrics
),

deal_details as (
    select *
    from intermediate.int_hubspot__deal_performance_metrics
),

rep_monthly_performance as (
    select 
        dd.owner_id,
        date_part('year', dd.created_date) as performance_year,
        date_part('month', dd.created_date) as performance_month,
        
        -- Monthly deal metrics
        count(distinct dd.deal_id) as monthly_deals_created,
        count(distinct case when dd.deal_status = 'Won' then dd.deal_id end) as monthly_deals_won,
        sum(case when dd.deal_status = 'Won' then dd.deal_amount else 0 end) as monthly_revenue,
        sum(case when dd.deal_status = 'Open' then dd.deal_amount else 0 end) as monthly_pipeline_added,
        
        -- Monthly performance rates
        case 
            when count(distinct case when dd.deal_status in ('Won', 'Lost') then dd.deal_id end) > 0
            then cast(count(distinct case when dd.deal_status = 'Won' then dd.deal_id end) as decimal) / 
                 cast(count(distinct case when dd.deal_status in ('Won', 'Lost') then dd.deal_id end) as decimal) * 100
            else 0 
        end as monthly_win_rate,
        
        avg(case when dd.deal_status = 'Won' then dd.deal_cycle_time_days end) as monthly_avg_cycle_time
        
    from deal_details dd
    where dd.created_date is not null 
    group by 1, 2, 3
),

rep_performance_trends as (
    select 
        rmp.owner_id,
        
        -- Trend calculations (last 6 months vs previous 6 months)
        avg(case when rmp.performance_year * 12 + rmp.performance_month >= 
                      (date_part('year', current_date) * 12 + date_part('month', current_date)) - 6
             then rmp.monthly_revenue else null end) as recent_6m_avg_revenue,
        avg(case when rmp.performance_year * 12 + rmp.performance_month between 
                      (date_part('year', current_date) * 12 + date_part('month', current_date)) - 12 and
                      (date_part('year', current_date) * 12 + date_part('month', current_date)) - 7
             then rmp.monthly_revenue else null end) as prior_6m_avg_revenue,
             
        avg(case when rmp.performance_year * 12 + rmp.performance_month >= 
                      (date_part('year', current_date) * 12 + date_part('month', current_date)) - 6
             then rmp.monthly_win_rate else null end) as recent_6m_avg_win_rate,
        avg(case when rmp.performance_year * 12 + rmp.performance_month between 
                      (date_part('year', current_date) * 12 + date_part('month', current_date)) - 12 and
                      (date_part('year', current_date) * 12 + date_part('month', current_date)) - 7
             then rmp.monthly_win_rate else null end) as prior_6m_avg_win_rate,
        
        -- Activity consistency metrics
        stddev(rmp.monthly_revenue) as revenue_volatility,
        stddev(rmp.monthly_deals_created) as activity_consistency,
        
        -- Performance momentum
        count(case when rmp.performance_year * 12 + rmp.performance_month >= 
                       (date_part('year', current_date) * 12 + date_part('month', current_date)) - 3
              then 1 end) as recent_active_months
        
    from rep_monthly_performance rmp
    group by 1
),

rep_territory_analysis as (
    select 
        dd.owner_id,
        
        -- Territory/segment focus analysis
        mode() within group (order by dd.deal_size_category) as primary_deal_segment,
        count(distinct dd.deal_size_category) as segments_covered,
        
        -- Segment performance
        sum(case when dd.deal_size_category = 'Enterprise (100K+)' and dd.deal_status = 'Won' then dd.deal_amount else 0 end) as enterprise_revenue,
        sum(case when dd.deal_size_category = 'Large (50K-100K)' and dd.deal_status = 'Won' then dd.deal_amount else 0 end) as large_revenue,
        sum(case when dd.deal_size_category = 'Medium (10K-50K)' and dd.deal_status = 'Won' then dd.deal_amount else 0 end) as medium_revenue,
        sum(case when dd.deal_size_category = 'Small (<10K)' and dd.deal_status = 'Won' then dd.deal_amount else 0 end) as small_revenue,
        
        -- Win rates by segment
        case 
            when count(case when dd.deal_size_category = 'Enterprise (100K+)' and dd.deal_status in ('Won', 'Lost') then 1 end) > 0
            then cast(count(case when dd.deal_size_category = 'Enterprise (100K+)' and dd.deal_status = 'Won' then 1 end) as decimal) / 
                 cast(count(case when dd.deal_size_category = 'Enterprise (100K+)' and dd.deal_status in ('Won', 'Lost') then 1 end) as decimal) * 100
            else 0 
        end as enterprise_win_rate,
        
        case 
            when count(case when dd.deal_size_category = 'Large (50K-100K)' and dd.deal_status in ('Won', 'Lost') then 1 end) > 0
            then cast(count(case when dd.deal_size_category = 'Large (50K-100K)' and dd.deal_status = 'Won' then 1 end) as decimal) / 
                 cast(count(case when dd.deal_size_category = 'Large (50K-100K)' and dd.deal_status in ('Won', 'Lost') then 1 end) as decimal) * 100
            else 0 
        end as large_deal_win_rate
        
    from deal_details dd
    group by 1
),

rep_ranking_analysis as (
    select 
        srb.owner_id as owner_id,
        srb.owner_name,
        srb.owner_email,
        srb.total_deals,
        srb.won_deals,
        srb.total_won_revenue,
        srb.win_rate_percentage,
        srb.avg_won_cycle_time,
        srb.pipeline_value as current_pipeline_value,
        
        -- Company rankings
        row_number() over (order by srb.total_won_revenue desc) as revenue_rank,
        row_number() over (order by srb.win_rate_percentage desc) as win_rate_rank,
        row_number() over (order by srb.won_deals desc) as volume_rank,
        row_number() over (order by coalesce(srb.avg_won_cycle_time, 999) asc) as efficiency_rank,
        
        -- Percentile rankings
        percent_rank() over (order by srb.total_won_revenue) * 100 as revenue_percentile,
        percent_rank() over (order by srb.win_rate_percentage) * 100 as win_rate_percentile,
        percent_rank() over (order by srb.won_deals) * 100 as volume_percentile,
        percent_rank() over (order by coalesce(srb.avg_won_cycle_time, 999) desc) * 100 as efficiency_percentile,
        
        -- Overall performance score
        (
            percent_rank() over (order by srb.total_won_revenue) * 40 +
            percent_rank() over (order by srb.win_rate_percentage) * 25 +
            percent_rank() over (order by srb.won_deals) * 20 +
            percent_rank() over (order by coalesce(srb.avg_won_cycle_time, 999) desc) * 15
        ) * 100 as overall_performance_score
        
    from sales_rep_base srb
    where srb.total_deals > 0
),

final_rep_analysis as (
    select 
        rra.*,
        
        -- Trend data
        rpt.recent_6m_avg_revenue,
        rpt.prior_6m_avg_revenue,
        rpt.recent_6m_avg_win_rate,
        rpt.prior_6m_avg_win_rate,
        rpt.revenue_volatility,
        rpt.activity_consistency,
        rpt.recent_active_months,
        
        -- Territory analysis
        rta.primary_deal_segment,
        rta.segments_covered,
        rta.enterprise_revenue,
        rta.large_revenue,
        rta.medium_revenue,
        rta.small_revenue,
        rta.enterprise_win_rate,
        rta.large_deal_win_rate,
        
        -- Trend calculations
        case 
            when rpt.prior_6m_avg_revenue > 0 and rpt.recent_6m_avg_revenue is not null
            then (rpt.recent_6m_avg_revenue - rpt.prior_6m_avg_revenue) / rpt.prior_6m_avg_revenue * 100
            else null 
        end as revenue_trend_percentage,
        
        case 
            when rpt.prior_6m_avg_win_rate > 0 and rpt.recent_6m_avg_win_rate is not null
            then rpt.recent_6m_avg_win_rate - rpt.prior_6m_avg_win_rate
            else null 
        end as win_rate_trend_points
        
    from rep_ranking_analysis rra
    left join rep_performance_trends rpt on rra.owner_id = cast(rpt.owner_id as varchar)
    left join rep_territory_analysis rta on rra.owner_id = cast(rta.owner_id as varchar)
)

select 
    *,
    
    -- Performance tier classification
    case 
        when overall_performance_score >= 80 then 'Top Performer'
        when overall_performance_score >= 60 then 'High Performer'
        when overall_performance_score >= 40 then 'Core Performer'
        when overall_performance_score >= 20 then 'Developing Performer'
        else 'Needs Improvement'
    end as performance_tier,
    
    -- Trend classification
    case 
        when revenue_trend_percentage >= 20 then 'Strong Growth'
        when revenue_trend_percentage >= 5 then 'Steady Growth'
        when revenue_trend_percentage >= -5 then 'Stable'
        when revenue_trend_percentage >= -20 then 'Declining'
        else 'Significant Decline'
    end as performance_trend,
    
    -- Specialization analysis
    case 
        when enterprise_revenue > large_revenue + medium_revenue + small_revenue then 'Enterprise Specialist'
        when large_revenue > enterprise_revenue + medium_revenue + small_revenue then 'Large Deal Specialist'
        when segments_covered >= 3 then 'Generalist'
        else 'Focused Seller'
    end as sales_specialization,
    
    -- Development recommendations
    case 
        when win_rate_percentage < 15 and avg_won_cycle_time > 90 then 'Focus on Qualification and Process'
        when win_rate_percentage < 15 then 'Improve Win Rate'
        when avg_won_cycle_time > 120 then 'Accelerate Sales Cycle'
        when won_deals < 5 then 'Increase Activity Volume'
        when revenue_trend_percentage < -10 then 'Address Performance Decline'
        else 'Maintain Current Performance'
    end as development_focus,
    
    -- Activity level assessment
    case 
        when recent_active_months >= 3 and total_deals >= 10 then 'Highly Active'
        when recent_active_months >= 2 and total_deals >= 5 then 'Active'
        when recent_active_months >= 1 then 'Moderately Active'
        else 'Low Activity'
    end as activity_level,
    
    -- Pipeline health
    case 
        when current_pipeline_value >= total_won_revenue * 2 then 'Strong Pipeline'
        when current_pipeline_value >= total_won_revenue then 'Healthy Pipeline'
        when current_pipeline_value >= total_won_revenue * 0.5 then 'Adequate Pipeline'
        else 'Weak Pipeline'
    end as pipeline_health_status
    
from final_rep_analysis
order by overall_performance_score desc
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 200 | 200 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"owner_id":"1000"}</code> |
| K2 | <code>{"owner_id":"1001"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| owner_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| owner_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| owner_email | 0 | 0 | 0 | VARCHAR | VARCHAR |
| total_deals | 0 | 0 | 0 | BIGINT | BIGINT |
| won_deals | 0 | 0 | 0 | BIGINT | BIGINT |
| total_won_revenue | 0 | 0 | 0 | DECIMAL(38,2) | DECIMAL(38,2) |
| win_rate_percentage | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_won_cycle_time | 0 | 0 | 0 | DOUBLE | DOUBLE |
| current_pipeline_value | 0 | 0 | 0 | DECIMAL(38,2) | DECIMAL(38,2) |
| revenue_rank | 0 | 0 | 0 | BIGINT | BIGINT |
| win_rate_rank | 164 | 164 | 164 | BIGINT | BIGINT |
| volume_rank | 180 | 180 | 180 | BIGINT | BIGINT |
| efficiency_rank | 4 | 4 | 4 | BIGINT | BIGINT |
| revenue_percentile | 0 | 0 | 0 | DOUBLE | DOUBLE |
| win_rate_percentile | 0 | 0 | 0 | DOUBLE | DOUBLE |
| volume_percentile | 0 | 0 | 0 | DOUBLE | DOUBLE |
| efficiency_percentile | 0 | 0 | 0 | DOUBLE | DOUBLE |
| overall_performance_score | 0 | 0 | 0 | DOUBLE | DOUBLE |
| revenue_volatility | 75 | 75 | 75 | DOUBLE | DOUBLE |
| activity_consistency | 74 | 74 | 74 | DOUBLE | DOUBLE |
| recent_active_months | 0 | 0 | 0 | BIGINT | BIGINT |
| primary_deal_segment | 0 | 0 | 0 | VARCHAR | VARCHAR |
| segments_covered | 0 | 0 | 0 | BIGINT | BIGINT |
| enterprise_revenue | 0 | 0 | 0 | DECIMAL(38,2) | DECIMAL(38,2) |
| large_revenue | 74 | 74 | 74 | DECIMAL(38,2) | DECIMAL(38,2) |
| medium_revenue | 108 | 108 | 108 | DECIMAL(38,2) | DECIMAL(38,2) |
| small_revenue | 171 | 171 | 171 | DECIMAL(38,2) | DECIMAL(38,2) |
| enterprise_win_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| large_deal_win_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| revenue_trend_percentage | 0 | 0 | 0 | DOUBLE | DOUBLE |
| win_rate_trend_points | 0 | 0 | 0 | DOUBLE | DOUBLE |
| performance_tier | 0 | 0 | 0 | VARCHAR | VARCHAR |
| performance_trend | 0 | 0 | 0 | VARCHAR | VARCHAR |
| sales_specialization | 0 | 0 | 0 | VARCHAR | VARCHAR |
| development_focus | 0 | 0 | 0 | VARCHAR | VARCHAR |
| activity_level | 0 | 0 | 0 | VARCHAR | VARCHAR |
| pipeline_health_status | 0 | 0 | 0 | VARCHAR | VARCHAR |

win_rate_rank 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 168 | 86 |

volume_rank 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 119 | 108 |

efficiency_rank 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | 48 | 49 |

revenue_volatility 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | 172510.35865790994 | 172510.3586579099 |

activity_consistency 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | 0.8819171036881969 | 0.8819171036881968 |

large_revenue 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0.00 |

medium_revenue 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | null | 0.00 |

small_revenue 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0.00 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>6列；[{"column":"revenue_trend_percentage","table_rows":200}]</code> |
| A3_constant_nonnull_column | <code>9列；[{"column":"win_rate_percentage","value":"100.0"}]</code> |
| A4_equal_columns | <code>2组；[{"columns":["win_rate_percentage","enterprise_win_rate"],"nonnull_equal_rows":200,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>2组；[{"columns":["win_rate_percentage","enterprise_win_rate"],"nonnull_equal_rows":200,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| C9_agent_runtime_text | <code>S4:1 current_date；命中数=14</code> |
| C9_gold_runtime_text | <code>S5:46 current_date；命中数=14</code> |
| C9_contract_runtime_text | <code>S3:1804 current_date；命中数=2</code> |
| D10_keyword_in_any_result_field | <code>命中数=2；assistant_trajectory put('sales','hubspot__sales_rep_performance',"""with om as (select * from intermediate.int_hubspot__owner_performance_metrics where total_deals&gt;0), d as (select *,year(created_date) y,month(created_date) m from intermediate.int_hubspot__deal_performance_metrics), monthly as (select owner_id,y performance_year,m performance_month,y*12+m month_index,count(distinct deal_id) monthly_deals_created,sum(case when deal_status='Won' then 1 else 0 end) monthly_deals_won,sum(case when deal_status='Won' then deal_amount else 0 end) monthly_revenue,sum(case when deal_status='Open' then deal_amount else 0 end) monthly_pipeline_added,100.0*count(*) filter(where deal_status='Won')/nullif(count(*) filter(where deal_status in('Won','Lost')),0) monthly_win_rate,avg(deal_cycle_time_days) filter(where deal_status='Won') monthly_avg_cycle_time from d where created_date is not null group by 1,2,3), trends as (select owner_id,avg(monthly_revenue) filter(where month_index&gt;=year(current_date)*12+month(current_date)-6) recent_6m_avg_revenue,avg(monthly_revenue) filter(where month_index between year(current_date)*12+month(current_date)-12 and year(current_date)*12+month(current_date)-7) prior_6m_avg_revenue,avg(monthly_win_rate) filter(where month_index&gt;=year(current_date)*12+month(current_date)-6) recent_6m_avg_win_rate,avg(monthly_win_rate) filter(where month_index between year(current_date)*12+month(current_date)-12 and year(current_date)*12+month(current_date)-7) prior_6m_avg_win_rate,stddev_samp(monthly_revenue) revenue_volatility,stddev_samp(monthly_deals_created) activity_consistency,count(*) filter(where month_index&gt;=year(current_date)*12+month(current_date)-2) recent_active_months from monthly group by 1), seg as (select owner_id,mode() within group(order by deal_size_category) primary_deal_segment,count(distinct deal_size_category)::bigint segments_covered,sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Enterprise (100K+)') enterprise_revenue,sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Large (50K-100K)') large_revenue,sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Medium (10K-50K)') medium_revenue,sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Small (&lt;10K)') small_revenue from d group by 1), ranks as (select *,row_number() over(order by total_won_revenue desc) revenue_rank,row_number() over(order by win_rate_percentage desc) win_rate_rank,row_number() over(order by won_deals desc) volume_rank,row_number() over(order by coalesce(avg_won_cycle_time,999)) efficiency_rank,100*percent_rank() over(order by total_won_revenue) revenue_percentile,100*percent_rank() over(order by win_rate_percentage) win_rate_percentile,100*percent_rank() over(order by won_deals) volume_percentile,100*percent_rank() over(order by coalesce(avg_won_cycle_time,999) desc) efficiency_percentile from om), joined as (select r.*,s.primary_deal_segment,s.segments_covered,s.enterprise_revenue,s.large_revenue,s.medium_revenue,s.small_revenue,t.activity_consistency,t.recent_active_months,t.revenue_volatility,t.recent_6m_avg_revenue,t.prior_6m_avg_revenue,t.recent_6m_avg_win_rate,t.prior_6m_avg_win_rate,case when t.prior_6m_avg_revenue&gt;0 then 100*(t.recent_6m_avg_revenue-t.prior_6m_avg_revenue)/t.prior_6m_avg_revenue end revenue_trend_percentage,case when t.prior_6m_avg_win_rate&gt;0 then t.recent_6m_avg_win_rate-t.prior_6m_avg_win_rate end win_rate_trend_points from ranks r left join seg s on cast(r.owner_id as varchar)=cast(s.owner_id as varchar) left join trends t on cast(r.owner_id as varchar)=cast(t.owner_id as varchar)), scored as (select *,revenue_percentile*40+win_rate_percentile*25+volume_percentile*20+efficiency_percentile*15 overall_performance_score from joined) select owner_id,owner_name,owner_email,total_deals,won_deals,total_won_revenue,win_rate_percentage,avg_won_cycle_time,pipeline_value current_pipeline_value,enterprise_win_rate,large_deal_win_rate,enterprise_revenue,large_revenue,medium_revenue,small_revenue,revenue_rank,win_rate_rank,volume_rank,efficiency_rank,revenue_percentile,win_rate_percentile,volume_percentile,efficiency_percentile,overall_performance_score,case when overall_performance_score&gt;=80 then 'Top Performer' when overall_performance_score&gt;=60 then 'High Performer' when overall_performance_score&gt;=40 then 'Core Performer' when overall_performance_score&gt;=20 then 'Developing Performer' else 'Needs Improvement' end performance_tier,case when enterprise_revenue&gt;coalesce(large_revenue,0)+coalesce(medium_revenue,0)+coalesce(small_revenue,0) then 'Enterprise Specialist' when large_revenue&gt;coalesce(enterprise_revenue,0)+coalesce(medium_revenue,0)+coalesce(small_revenue,0) then 'Large Deal Specialist' when segments_covered&gt;=3 then 'Generalist' else 'Focused Seller' end sales_specialization,case when win_rate_percentage&lt;15 and avg_won_cycle_time&gt;90 then 'Focus on Qualification and Process' when win_rate_percentage&lt;15 then 'Improve Win Rate' when avg_won_cycle_time&gt;120 then 'Accelerate Sales Cycle' when won_deals&lt;5 then 'Increase Activity Volume' when revenue_trend_percentage&lt; -5 then 'Address Performance Decline' else 'Maintain Current Performance' end development_focus,case when pipeline_value&gt;=2*total_won_revenue then 'Strong Pipeline' when pipeline_value&gt;=total_won_revenue then 'Healthy Pipeline' when pipeline_value&gt;=0.5*total_won_revenue then 'Adequate Pipeline' else 'Weak Pipeline' end pipeline_health_status,primary_deal_segment,segments_covered,case when recent_active_months&gt;=3 and total_deals&gt;=10 then 'Highly Active' when recent_active_months&gt;=2 and total_deals&gt;=5 then 'Active' when recent_active_months&gt;=1 then 'Moderately Active' else 'Low Activity' end activity_level,activity_consistency,recent_active_months,case when revenue_trend_percentage&gt;=20 then 'Strong Growth' when revenue_trend_percentage&gt;=5 then 'Steady Growth' when revenue_trend_percentage&gt;=-5 then 'Stable' when revenue_trend_percentage&gt;=-20 then 'Declining' else 'Significant Decline' end performance_trend,revenue_trend_percentage,win_rate_trend_points,revenue_volatility,recent_6m_avg_revenue,prior_6m_avg_revenue,recent_6m_avg_win_rate,prior_6m_avg_win_rate from scored order by overall_performance_score desc""")</code> |

## 轨迹索引（不放输出原文）

本题事件总数：75；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/.events/sessions/49d1fc2e-5da1-4b-71664cc3fd873b2/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 9 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; sed -n '1,260p' run.py</code> | 13570 | true | false |
| 15 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>x=yaml.safe_load(open('docs/data_contract.yaml'))<br>print(len(x['staging_contract']['tables']))<br>for grp in ['intermediate_models','marketing_models','sales_models','service_m</code> | 755 | true | false |
| 21 | run | <code>cat &gt;&gt; /tmp/build.py &lt;&lt;'PY'<br>put('intermediate','int_hubspot__deal_performance_metrics',"""with b as (select deal_id,deal_name,amount as deal_amount,pipeline_stage_label as deal_stage,pipeline_label as</code> | 0 | false | false |
| 27 | run | <code>cat &gt;&gt; /tmp/build.py &lt;&lt;'PY'<br># Sales models<br>put('sales','hubspot__deals',"select * from intermediate.int_hubspot__deals_enhanced")<br>put('sales','hubspot__companies',"select * from staging.stg_hubspot__c</code> | 0 | false | false |
| 31 | run | <code>python run.py &gt; /tmp/run.log 2&gt;&amp;1; rc=$?; tail -100 /tmp/run.log; exit $rc</code> | 7656 | true | false |
| 35 | run | <code>sed -i 's/) cycle from intermediate/) as cycle_days from intermediate/' sql/intermediate/int_hubspot__owner_performance_metrics.sql; rm -f hubspot.duckdb &amp;&amp; python run.py &gt; /tmp/run2.log 2&gt;&amp;1; grep -E</code> | 6768 | true | false |
| 39 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,os<br>os.remove('hubspot.duckdb') if os.path.exists('hubspot.duckdb') else None<br>s=duckdb.connect('hubspot_start.duckdb',read_only=True); t=duckdb.connect('hubspot.duckdb')<br>t</code> | 6600 | true | false |
| 41 | run | <code>python - &lt;&lt;'PY'<br>p='run.py'<br>s=open(p).read();s=s.replace("            self.conn.execute(f\"ATTACH '{self.source_db_path}' AS source_db\")", "            source_conn.close()\n            self.conn.execu</code> | 1178 | true | false |
| 43 | run | <code>grep -n 'cycle\&#124;close_date' sql/intermediate/int_hubspot__owner_performance_metrics.sql &#124; head</code> | 3948 | false | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>p='sql/intermediate/int_hubspot__contact_lifecycle_metrics.sql';s=open(p).read().replace('left join deal_metrics d using(contact_id)','left join deal_metrics d on cast(c.contact_id as </code> | 976 | true | false |
| 47 | run | <code>python - &lt;&lt;'PY'<br>p='sql/intermediate/int_hubspot__owner_performance_metrics.sql';s=open(p).read().replace('deal_amount','amount');open(p,'w').write(s)<br>p='sql/marketing/hubspot__contact_engagement_analy</code> | 452 | false | false |
| 49 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,yaml<br>c=duckdb.connect('hubspot.duckdb',read_only=True)<br>contract=yaml.safe_load(open('docs/data_contract.yaml'))<br>for key,layer in [('tables','staging_contract'),('intermed</code> | 2557 | true | false |
| 63 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('hubspot.duckdb',read_only=True)<br>for schema in ['staging','intermediate','marketing','sales','service']:<br> print(schema,c.execute(f"select table_name from</code> | 1569 | true | false |
| 65 | run | <code>grep -R ';' -n sql &#124;&#124; true; find sql -type f &#124; sort</code> | 1842 | true | false |

### agent action 的 thought/message 命中原句

event 27 / message

```text
put('sales','hubspot__sales_rep_performance',"""with om as (select * from intermediate.int_hubspot__owner_performance_metrics where total_deals>0), d as (select *,year(created_date) y,month(created_date) m from intermediate.int_hubspot__deal_performance_metrics), monthly as (select owner_id,y performance_year,m performance_month,y*12+m month_index,count(distinct deal_id) monthly_deals_created,sum(case when deal_status='Won' then 1 else 0 end) monthly_deals_won,sum(case when deal_status='Won' then deal_amount else 0 end) monthly_revenue,sum(case when deal_status='Open' then deal_amount else 0 end) monthly_pipeline_added,100.0*count(*) filter(where deal_status='Won')/nullif(count(*) filter(where deal_status in('Won','Lost')),0) monthly_win_rate,avg(deal_cycle_time_days) filter(where deal_status='Won') monthly_avg_cycle_time from d where created_date is not null group by 1,2,3), trends as (select owner_id,avg(monthly_revenue) filter(where month_index>=year(current_date)*12+month(current_date)-6) recent_6m_avg_revenue,avg(monthly_revenue) filter(where month_index between year(current_date)*12+month(current_date)-12 and year(current_date)*12+month(current_date)-7) prior_6m_avg_revenue,avg(monthly_win_rate) filter(where month_index>=year(current_date)*12+month(current_date)-6) recent_6m_avg_win_rate,avg(monthly_win_rate) filter(where month_index between year(current_date)*12+month(current_date)-12 and year(current_date)*12+month(current_date)-7) prior_6m_avg_win_rate,stddev_samp(monthly_revenue) revenue_volatility,stddev_samp(monthly_deals_created) activity_consistency,count(*) filter(where month_index>=year(current_date)*12+month(current_date)-2) recent_active_months from monthly group by 1), seg as (select owner_id,mode() within group(order by deal_size_category) primary_deal_segment,count(distinct deal_size_category)::bigint segments_covered,sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Enterprise (100K+)') enterprise_revenue,sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Large (50K-100K)') large_revenue,sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Medium (10K-50K)') medium_revenue,sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Small (<10K)') small_revenue from d group by 1), ranks as (select *,row_number() over(order by total_won_revenue desc) revenue_rank,row_number() over(order by win_rate_percentage desc) win_rate_rank,row_number() over(order by won_deals desc) volume_rank,row_number() over(order by coalesce(avg_won_cycle_time,999)) efficiency_rank,100*percent_rank() over(order by total_won_revenue) revenue_percentile,100*percent_rank() over(order by win_rate_percentage) win_rate_percentile,100*percent_rank() over(order by won_deals) volume_percentile,100*percent_rank() over(order by coalesce(avg_won_cycle_time,999) desc) efficiency_percentile from om), joined as (select r.*,s.primary_deal_segment,s.segments_covered,s.enterprise_revenue,s.large_revenue,s.medium_revenue,s.small_revenue,t.activity_consistency,t.recent_active_months,t.revenue_volatility,t.recent_6m_avg_revenue,t.prior_6m_avg_revenue,t.recent_6m_avg_win_rate,t.prior_6m_avg_win_rate,case when t.prior_6m_avg_revenue>0 then 100*(t.recent_6m_avg_revenue-t.prior_6m_avg_revenue)/t.prior_6m_avg_revenue end revenue_trend_percentage,case when t.prior_6m_avg_win_rate>0 then t.recent_6m_avg_win_rate-t.prior_6m_avg_win_rate end win_rate_trend_points from ranks r left join seg s on cast(r.owner_id as varchar)=cast(s.owner_id as varchar) left join trends t on cast(r.owner_id as varchar)=cast(t.owner_id as varchar)), scored as (select *,revenue_percentile*40+win_rate_percentile*25+volume_percentile*20+efficiency_percentile*15 overall_performance_score from joined) select owner_id,owner_name,owner_email,total_deals,won_deals,total_won_revenue,win_rate_percentage,avg_won_cycle_time,pipeline_value current_pipeline_value,enterprise_win_rate,large_deal_win_rate,enterprise_revenue,large_revenue,medium_revenue,small_revenue,revenue_rank,win_rate_rank,volume_rank,efficiency_rank,revenue_percentile,win_rate_percentile,volume_percentile,efficiency_percentile,overall_performance_score,case when overall_performance_score>=80 then 'Top Performer' when overall_performance_score>=60 then 'High Performer' when overall_performance_score>=40 then 'Core Performer' when overall_performance_score>=20 then 'Developing Performer' else 'Needs Improvement' end performance_tier,case when enterprise_revenue>coalesce(large_revenue,0)+coalesce(medium_revenue,0)+coalesce(small_revenue,0) then 'Enterprise Specialist' when large_revenue>coalesce(enterprise_revenue,0)+coalesce(medium_revenue,0)+coalesce(small_revenue,0) then 'Large Deal Specialist' when segments_covered>=3 then 'Generalist' else 'Focused Seller' end sales_specialization,case when win_rate_percentage<15 and avg_won_cycle_time>90 then 'Focus on Qualification and Process' when win_rate_percentage<15 then 'Improve Win Rate' when avg_won_cycle_time>120 then 'Accelerate Sales Cycle' when won_deals<5 then 'Increase Activity Volume' when revenue_trend_percentage< -5 then 'Address Performance Decline' else 'Maintain Current Performance' end development_focus,case when pipeline_value>=2*total_won_revenue then 'Strong Pipeline' when pipeline_value>=total_won_revenue then 'Healthy Pipeline' when pipeline_value>=0.5*total_won_revenue then 'Adequate Pipeline' else 'Weak Pipeline' end pipeline_health_status,primary_deal_segment,segments_covered,case when recent_active_months>=3 and total_deals>=10 then 'Highly Active' when recent_active_months>=2 and total_deals>=5 then 'Active' when recent_active_months>=1 then 'Moderately Active' else 'Low Activity' end activity_level,activity_consistency,recent_active_months,case when revenue_trend_percentage>=20 then 'Strong Growth' when revenue_trend_percentage>=5 then 'Steady Growth' when revenue_trend_percentage>=-5 then 'Stable' when revenue_trend_percentage>=-20 then 'Declining' else 'Significant Decline' end performance_trend,revenue_trend_percentage,win_rate_trend_points,revenue_volatility,recent_6m_avg_revenue,prior_6m_avg_revenue,recent_6m_avg_win_rate,prior_6m_avg_win_rate from scored order by overall_performance_score desc""")
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/009_tolerance_tables.jsonl`
- S2: `records/009_cs_impl-010.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-010/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/sales/hubspot__sales_rep_performance.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/sql/sales/hubspot__sales_rep_performance.sql`
- S6: `records/006_contract_impl-010.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/result.md`
- S10: `data/021_packages_work/021_impl-010_hubspot__sales_rep_performance/021_impl-010_hubspot__sales_rep_performance.json`
- S11: `data/009_cs_work/impl-010/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/hubspot.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/.events/sessions`
