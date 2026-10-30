# impl-010 | intermediate | int_hubspot__owner_performance_metrics | 差异：S1；日期 原记录

## 契约完整原文

S3:1024–1140

```yaml
    - name: int_hubspot__owner_performance_metrics
      schema: intermediate
      description: Sales owner performance metrics with counts, revenue, cycle times, rankings, percentiles, and rule-based classifications
      grain: One row per owner_id with at least one deal
      source_models:
      - intermediate.int_hubspot__deals_enhanced (owner_id, amount, pipeline_stage_label, pipeline_label, deal_pipeline_stage_id, created_date, closed_date)
      - intermediate.int_hubspot__owners_enhanced (owner_id, owner_full_name, owner_email_address)
      business_logic: '- Start from intermediate.int_hubspot__deals_enhanced, keeping only deals with a non-NULL owner_id. - For each deal, derive: - deal_status: Won if closed_date is present and amount > 0; Lost if closed_date is present and amount = 0; Open if closed_date is missing; otherwise Unknown. - deal_size_category: Enterprise (100K+) if amount >= 100000; Large (50K-100K) if amount >= 50000; Medium (10K-50K) if amount >= 10000; Small (<10K) if amount > 0; else No Value. - deal_cycle_time_days: number of days between created_date and closed_date when both exist; otherwise NULL. - Left join to intermediate.int_hubspot__owners_enhanced on owner_id to bring owner_full_name and owner_email_address. - Aggregate by owner_id, owner_name, owner_email: - Counts: total_deals (all deals); won_deals (status Won); lost_deals (status Lost); open_deals (status Open). - Win rate: wins divided by (wins + losses) times 100; if there are no closed (Won/Lost) deals then 0. - Revenue: total_won_revenue = sum of amounts from Won deals (non-won contribute 0; NULL amounts are ignored); avg_won_deal_size = average amount for Won deals (NULL if none); pipeline_value = sum of amounts from Open deals (non-open contribute 0; NULL amounts are ignored). - Velocity: avg_won_cycle_time = average cycle days for Won; avg_lost_cycle_time = average cycle days for Lost (both NULL if none). - Dates: first_deal_date = earliest created_date; latest_deal_date = latest created_date; last_won_date = latest close_date among Won. - Size distribution: counts of Enterprise, Large, Medium, and Small as defined above. - Size-specific win rates: within Enterprise and Large respectively, wins divided by (wins + losses) times 100; if no closed deals in that size then 0. - Keep only owners with total_deals > 0. - Compute window metrics across all remaining owners (no partitions): - revenue_rank: position when ordering by total_won_revenue descending (1 = highest; ties break arbitrarily). - win_rate_rank: position when ordering by win_rate_percentage descending (1 = highest; ties break arbitrarily). - deals_won_rank: position when ordering by won_deals descending (1 = highest; ties break arbitrarily). - cycle_time_rank: position when ordering by average won cycle time ascending; missing averages are treated as 999 days (1 = shortest). - revenue_percentile: percentile rank scaled 0–100 by total_won_revenue (lowest = 0, highest = 100). - win_rate_percentile: percentile rank scaled 0–100 by win_rate_percentage (lowest = 0, highest = 100). - volume_percentile: percentile rank scaled 0–100 by won_deals (lowest = 0, highest = 100). - efficiency_percentile: percentile rank scaled 0–100 by average won cycle time in descending order with missing treated as 999 (0 = slowest or NULL, 100 = fastest). - overall_performance_score: take the percentile ranks (0–1) for revenue, win rate, won deals, and cycle time (faster = higher), weight them 40/25/20/15 respectively, sum them, then multiply by 100; the score ranges from 0 to 10000. - Classifications: - performance_tier: Top Performer if score >= 80; High Performer if >= 60; Core Performer if >= 40; Developing Performer if >= 20; else Needs Improvement. - sales_specialization: Enterprise Specialist if enterprise_deals > (large_deals + medium_deals + small_deals); Large Deal Specialist if large_deals > (enterprise_deals + medium_deals + small_deals); Generalist if the total across size categories >= 3; else Focused Seller. - development_focus (first match applies): if win_rate_percentage < 15 and avg_won_cycle_time > 90 then Focus on Qualification and Process; else if win_rate_percentage < 15 then Improve Win Rate; else if avg_won_cycle_time > 120 then Accelerate Sales Cycle; else if won_deals < 5 then Increase Activity Volume; else Maintain Current Performance. - pipeline_health_status (evaluated in order): Strong Pipeline if pipeline_value >= 2 × total_won_revenue; Healthy Pipeline if >= total_won_revenue; Adequate Pipeline if >= 0.5 × total_won_revenue; else Weak Pipeline.'
      columns:
      - name: owner_id
        data_type: VARCHAR
        description: Sales owner identifier and grouping key; one row per owner with at least one deal
        tests:
        - not_null
        - unique
      - name: owner_name
        data_type: VARCHAR
        description: Owner full name from owners_enhanced; may be NULL if no match
      - name: owner_email
        data_type: VARCHAR
        description: Owner email from owners_enhanced; may be NULL if no match
      - name: total_deals
        data_type: BIGINT
        description: Total number of the owner's deals across all statuses
      - name: won_deals
        data_type: BIGINT
        description: Number of closed deals with amount > 0
      - name: lost_deals
        data_type: BIGINT
        description: Number of closed deals with amount = 0
      - name: open_deals
        data_type: BIGINT
        description: Number of deals with no closed_date
      - name: win_rate_percentage
        data_type: DOUBLE
        description: Wins divided by (wins + losses) times 100; returns 0 if there are no closed deals; no rounding
      - name: total_won_revenue
        data_type: DECIMAL(38,2)
        description: Total amount from won deals; non-won contribute 0 and NULL amounts are ignored; 2-decimal scale
      - name: avg_won_deal_size
        data_type: DOUBLE
        description: Average amount for won deals; excludes NULLs; NULL if no won deals
      - name: pipeline_value
        data_type: DECIMAL(38,2)
        description: Total amount from open deals; non-open contribute 0 and NULL amounts are ignored; 2-decimal scale
      - name: avg_won_cycle_time
        data_type: DOUBLE
        description: Average days from created to closed for won deals; NULL if none
      - name: avg_lost_cycle_time
        data_type: DOUBLE
        description: Average days from created to closed for lost deals; NULL if none
      - name: first_deal_date
        data_type: TIMESTAMP
        description: Earliest created_date across the owner's deals; NULL if all created_date values are NULL
      - name: latest_deal_date
        data_type: TIMESTAMP
        description: Latest created_date across the owner's deals; NULL if all created_date values are NULL
      - name: last_won_date
        data_type: TIMESTAMP
        description: Most recent close_date among won deals; NULL if no won deals
      - name: enterprise_deals
        data_type: BIGINT
        description: Number of deals with amount >= 100000
      - name: large_deals
        data_type: BIGINT
        description: Number of deals with 50000 <= amount < 100000
      - name: medium_deals
        data_type: BIGINT
        description: Number of deals with 10000 <= amount < 50000
      - name: small_deals
        data_type: BIGINT
        description: Number of deals with 0 < amount < 10000
      - name: enterprise_win_rate
        data_type: DOUBLE
        description: Within Enterprise size, wins divided by (wins + losses) times 100; returns 0 if no closed Enterprise deals
      - name: large_deal_win_rate
        data_type: DOUBLE
        description: Within Large size, wins divided by (wins + losses) times 100; returns 0 if no closed Large deals
      - name: revenue_rank
        data_type: BIGINT
        description: Position when ordering all owners by total won revenue descending; 1 is highest; ties break arbitrarily
      - name: win_rate_rank
        data_type: BIGINT
        description: Position when ordering all owners by win rate percentage descending; 1 is highest; ties break arbitrarily
      - name: deals_won_rank
        data_type: BIGINT
        description: Position when ordering all owners by number of won deals descending; 1 is highest; ties break arbitrarily
      - name: cycle_time_rank
        data_type: BIGINT
        description: Position when ordering by average won cycle time ascending; 1 is shortest; missing averages treated as 999 days; ties break arbitrarily
      - name: revenue_percentile
        data_type: DOUBLE
        description: Percentile rank scaled 0–100 by total won revenue; 0 = lowest, 100 = highest
      - name: win_rate_percentile
        data_type: DOUBLE
        description: Percentile rank scaled 0–100 by win rate percentage; 0 = lowest, 100 = highest
      - name: volume_percentile
        data_type: DOUBLE
        description: Percentile rank scaled 0–100 by number of won deals; 0 = lowest, 100 = highest
      - name: efficiency_percentile
        data_type: DOUBLE
        description: Percentile rank scaled 0–100 by average won cycle time in descending order with missing treated as 999; 0 = slowest/NULL, 100 = fastest
      - name: overall_performance_score
        data_type: DOUBLE
        description: Weighted sum of percentile ranks (0–1) for revenue, win rate, won deals, and cycle time (faster is higher) with weights 40/25/20/15, multiplied by 100; range 0–10000
      - name: performance_tier
        data_type: VARCHAR
        description: 'Tier from overall_performance_score: >=80 Top Performer; >=60 High Performer; >=40 Core Performer; >=20 Developing Performer; else Needs Improvement'
      - name: sales_specialization
        data_type: VARCHAR
        description: Enterprise Specialist if enterprise_deals > (large+medium+small); Large Deal Specialist if large_deals > (enterprise+medium+small); Generalist if total size-deal count >= 3; else Focused Seller
      - name: development_focus
        data_type: VARCHAR
        description: 'Priority rules: if win_rate_percentage < 15 and avg_won_cycle_time > 90 then Focus on Qualification and Process; else if win_rate_percentage < 15 then Improve Win Rate; else if avg_won_cycle_time > 120 then Accelerate Sales Cycle; else if won_deals < 5 then Increase Activity Volume; else Maintain Current Performance'
      - name: pipeline_health_status
        data_type: VARCHAR
        description: 'Pipeline status by comparing pipeline_value to total_won_revenue: >=2x Strong; >=1x Healthy; >=0.5x Adequate; else Weak'
```

## agent 最终 SQL

S4

```sql
with d as (select *,case when closed_date is null then 'Open' when amount>0 then 'Won' when amount=0 then 'Lost' else 'Unknown' end status,case when amount>=100000 then 'Enterprise' when amount>=50000 then 'Large' when amount>=10000 then 'Medium' when amount>0 then 'Small' else 'No Value' end size,date_diff('day',cast(created_date as date),cast(closed_date as date)) as cycle_days from intermediate.int_hubspot__deals_enhanced where owner_id is not null), a as (select d.owner_id,o.owner_full_name owner_name,o.owner_email_address owner_email,count(*)::bigint total_deals,count(*) filter(where status='Won')::bigint won_deals,count(*) filter(where status='Lost')::bigint lost_deals,count(*) filter(where status='Open')::bigint open_deals,100.0*count(*) filter(where status='Won')/nullif(count(*) filter(where status in ('Won','Lost')),0) win_rate_percentage,coalesce(sum(amount) filter(where status='Won'),0) total_won_revenue,avg(amount) filter(where status='Won') avg_won_deal_size,coalesce(sum(amount) filter(where status='Open'),0) pipeline_value,avg(cycle_days) filter(where status='Won') avg_won_cycle_time,avg(cycle_days) filter(where status='Lost') avg_lost_cycle_time,min(created_date) first_deal_date,max(created_date) latest_deal_date,max(closed_date) filter(where status='Won') last_won_date,count(*) filter(where size='Enterprise')::bigint enterprise_deals,count(*) filter(where size='Large')::bigint large_deals,count(*) filter(where size='Medium')::bigint medium_deals,count(*) filter(where size='Small')::bigint small_deals,100.0*count(*) filter(where size='Enterprise' and status='Won')/nullif(count(*) filter(where size='Enterprise' and status in('Won','Lost')),0) enterprise_win_rate,100.0*count(*) filter(where size='Large' and status='Won')/nullif(count(*) filter(where size='Large' and status in('Won','Lost')),0) large_deal_win_rate from d left join intermediate.int_hubspot__owners_enhanced o using(owner_id) group by d.owner_id,o.owner_full_name,o.owner_email_address), p as (select *,row_number() over(order by total_won_revenue desc) revenue_rank,row_number() over(order by win_rate_percentage desc nulls last) win_rate_rank,row_number() over(order by won_deals desc) deals_won_rank,row_number() over(order by coalesce(avg_won_cycle_time,999)) cycle_time_rank,100*percent_rank() over(order by total_won_revenue) revenue_percentile,100*percent_rank() over(order by win_rate_percentage) win_rate_percentile,100*percent_rank() over(order by won_deals) volume_percentile,100*percent_rank() over(order by coalesce(avg_won_cycle_time,999) desc) efficiency_percentile from a), s as (select *, revenue_percentile*40+win_rate_percentile*25+volume_percentile*20+efficiency_percentile*15 overall_performance_score from p) select *,case when overall_performance_score>=80 then 'Top Performer' when overall_performance_score>=60 then 'High Performer' when overall_performance_score>=40 then 'Core Performer' when overall_performance_score>=20 then 'Developing Performer' else 'Needs Improvement' end performance_tier,case when enterprise_deals>large_deals+medium_deals+small_deals then 'Enterprise Specialist' when large_deals>enterprise_deals+medium_deals+small_deals then 'Large Deal Specialist' when enterprise_deals+large_deals+medium_deals+small_deals>=3 then 'Generalist' else 'Focused Seller' end sales_specialization,case when win_rate_percentage<15 and avg_won_cycle_time>90 then 'Focus on Qualification and Process' when win_rate_percentage<15 then 'Improve Win Rate' when avg_won_cycle_time>120 then 'Accelerate Sales Cycle' when won_deals<5 then 'Increase Activity Volume' else 'Maintain Current Performance' end development_focus,case when pipeline_value>=2*total_won_revenue then 'Strong Pipeline' when pipeline_value>=total_won_revenue then 'Healthy Pipeline' when pipeline_value>=0.5*total_won_revenue then 'Adequate Pipeline' else 'Weak Pipeline' end pipeline_health_status from s
```

## gold SQL（仅供定位差异）

S5

```sql
-- Owner performance metrics intermediate table
-- Calculates sales rep performance, rankings, and efficiency metrics
with deals_enhanced as (
    select *
    from intermediate.int_hubspot__deals_enhanced
),

owners_enhanced as (
    select *
    from intermediate.int_hubspot__owners_enhanced  
),

deal_summary_by_owner as (
    select 
        d.owner_id,
        d.amount as deal_amount,
        d.pipeline_stage_label as deal_stage,
        d.pipeline_label as deal_pipeline,
        d.deal_pipeline_stage_id as deal_pipeline_stage,
        d.created_date,
        d.closed_date as close_date,
        
        -- Deal status classification
        case 
            when d.closed_date is not null and d.amount > 0 then 'Won'
            when d.closed_date is not null and d.amount = 0 then 'Lost'
            when d.closed_date is null then 'Open'
            else 'Unknown'
        end as deal_status,
        
        -- Deal size categorization
        case 
            when d.amount >= 100000 then 'Enterprise (100K+)'
            when d.amount >= 50000 then 'Large (50K-100K)'
            when d.amount >= 10000 then 'Medium (10K-50K)'
            when d.amount > 0 then 'Small (<10K)'
            else 'No Value'
        end as deal_size_category,
        
        -- Deal velocity calculations
        case 
            when d.closed_date is not null and d.created_date is not null
            then datediff('day', d.created_date, d.closed_date)
            else null
        end as deal_cycle_time_days
        
    from deals_enhanced d
    where d.owner_id is not null
),

owner_performance_metrics as (
    select 
        dsbo.owner_id,
        o.owner_full_name as owner_name,
        o.owner_email_address as owner_email,
        
        -- Deal count metrics
        count(*) as total_deals,
        count(case when dsbo.deal_status = 'Won' then 1 end) as won_deals,
        count(case when dsbo.deal_status = 'Lost' then 1 end) as lost_deals,
        count(case when dsbo.deal_status = 'Open' then 1 end) as open_deals,
        
        -- Win rate calculation
        case 
            when count(case when dsbo.deal_status in ('Won', 'Lost') then 1 end) > 0
            then cast(count(case when dsbo.deal_status = 'Won' then 1 end) as decimal) / 
                 cast(count(case when dsbo.deal_status in ('Won', 'Lost') then 1 end) as decimal) * 100
            else 0 
        end as win_rate_percentage,
        
        -- Revenue metrics
        sum(case when dsbo.deal_status = 'Won' then dsbo.deal_amount else 0 end) as total_won_revenue,
        avg(case when dsbo.deal_status = 'Won' then dsbo.deal_amount end) as avg_won_deal_size,
        sum(case when dsbo.deal_status = 'Open' then dsbo.deal_amount else 0 end) as pipeline_value,
        
        -- Velocity metrics
        avg(case when dsbo.deal_status = 'Won' then dsbo.deal_cycle_time_days end) as avg_won_cycle_time,
        avg(case when dsbo.deal_status = 'Lost' then dsbo.deal_cycle_time_days end) as avg_lost_cycle_time,
        
        -- Activity timing
        min(dsbo.created_date) as first_deal_date,
        max(dsbo.created_date) as latest_deal_date,
        max(case when dsbo.deal_status = 'Won' then dsbo.close_date end) as last_won_date,
        
        -- Deal size distribution
        count(case when dsbo.deal_size_category = 'Enterprise (100K+)' then 1 end) as enterprise_deals,
        count(case when dsbo.deal_size_category = 'Large (50K-100K)' then 1 end) as large_deals,
        count(case when dsbo.deal_size_category = 'Medium (10K-50K)' then 1 end) as medium_deals,
        count(case when dsbo.deal_size_category = 'Small (<10K)' then 1 end) as small_deals,
        
        -- Enterprise win rates
        case 
            when count(case when dsbo.deal_size_category = 'Enterprise (100K+)' and dsbo.deal_status in ('Won', 'Lost') then 1 end) > 0
            then cast(count(case when dsbo.deal_size_category = 'Enterprise (100K+)' and dsbo.deal_status = 'Won' then 1 end) as decimal) / 
                 cast(count(case when dsbo.deal_size_category = 'Enterprise (100K+)' and dsbo.deal_status in ('Won', 'Lost') then 1 end) as decimal) * 100
            else 0 
        end as enterprise_win_rate,
        
        case 
            when count(case when dsbo.deal_size_category = 'Large (50K-100K)' and dsbo.deal_status in ('Won', 'Lost') then 1 end) > 0
            then cast(count(case when dsbo.deal_size_category = 'Large (50K-100K)' and dsbo.deal_status = 'Won' then 1 end) as decimal) / 
                 cast(count(case when dsbo.deal_size_category = 'Large (50K-100K)' and dsbo.deal_status in ('Won', 'Lost') then 1 end) as decimal) * 100
            else 0 
        end as large_deal_win_rate
        
    from deal_summary_by_owner dsbo
    left join owners_enhanced o on dsbo.owner_id = o.owner_id
    group by 1, 2, 3
),

owner_rankings as (
    select 
        opm.*,
        
        -- Performance rankings
        row_number() over (order by opm.total_won_revenue desc) as revenue_rank,
        row_number() over (order by opm.win_rate_percentage desc) as win_rate_rank,
        row_number() over (order by opm.won_deals desc) as deals_won_rank,
        row_number() over (order by coalesce(opm.avg_won_cycle_time, 999) asc) as cycle_time_rank,
        
        -- Percentile rankings
        percent_rank() over (order by opm.total_won_revenue) * 100 as revenue_percentile,
        percent_rank() over (order by opm.win_rate_percentage) * 100 as win_rate_percentile,
        percent_rank() over (order by opm.won_deals) * 100 as volume_percentile,
        percent_rank() over (order by coalesce(opm.avg_won_cycle_time, 999) desc) * 100 as efficiency_percentile,
        
        -- Overall performance score
        (
            percent_rank() over (order by opm.total_won_revenue) * 40 +
            percent_rank() over (order by opm.win_rate_percentage) * 25 +
            percent_rank() over (order by opm.won_deals) * 20 +
            percent_rank() over (order by coalesce(opm.avg_won_cycle_time, 999) desc) * 15
        ) * 100 as overall_performance_score
        
    from owner_performance_metrics opm
    where opm.total_deals > 0
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
    
    -- Specialization analysis
    case 
        when enterprise_deals > large_deals + medium_deals + small_deals then 'Enterprise Specialist'
        when large_deals > enterprise_deals + medium_deals + small_deals then 'Large Deal Specialist'
        when enterprise_deals + large_deals + medium_deals + small_deals >= 3 then 'Generalist'
        else 'Focused Seller'
    end as sales_specialization,
    
    -- Development recommendations
    case 
        when win_rate_percentage < 15 and avg_won_cycle_time > 90 then 'Focus on Qualification and Process'
        when win_rate_percentage < 15 then 'Improve Win Rate'
        when avg_won_cycle_time > 120 then 'Accelerate Sales Cycle'
        when won_deals < 5 then 'Increase Activity Volume'
        else 'Maintain Current Performance'
    end as development_focus,
    
    -- Pipeline health
    case 
        when pipeline_value >= total_won_revenue * 2 then 'Strong Pipeline'
        when pipeline_value >= total_won_revenue then 'Healthy Pipeline'
        when pipeline_value >= total_won_revenue * 0.5 then 'Adequate Pipeline'
        else 'Weak Pipeline'
    end as pipeline_health_status
    
from owner_rankings
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
| K3 | <code>{"owner_id":"1002"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| owner_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| owner_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| owner_email | 0 | 0 | 0 | VARCHAR | VARCHAR |
| total_deals | 0 | 0 | 0 | BIGINT | BIGINT |
| won_deals | 0 | 0 | 0 | BIGINT | BIGINT |
| lost_deals | 0 | 0 | 0 | BIGINT | BIGINT |
| open_deals | 0 | 0 | 0 | BIGINT | BIGINT |
| win_rate_percentage | 0 | 0 | 0 | DOUBLE | DOUBLE |
| total_won_revenue | 0 | 0 | 0 | DECIMAL(38,2) | DECIMAL(38,2) |
| avg_won_deal_size | 0 | 0 | 0 | DOUBLE | DOUBLE |
| pipeline_value | 0 | 0 | 0 | DECIMAL(38,2) | DECIMAL(38,2) |
| avg_won_cycle_time | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_lost_cycle_time | 0 | 0 | 0 | DOUBLE | DOUBLE |
| enterprise_deals | 0 | 0 | 0 | BIGINT | BIGINT |
| large_deals | 0 | 0 | 0 | BIGINT | BIGINT |
| medium_deals | 0 | 0 | 0 | BIGINT | BIGINT |
| small_deals | 0 | 0 | 0 | BIGINT | BIGINT |
| enterprise_win_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| large_deal_win_rate | 74 | 74 | 74 | DOUBLE | DOUBLE |
| revenue_rank | 0 | 0 | 0 | BIGINT | BIGINT |
| win_rate_rank | 164 | 164 | 164 | BIGINT | BIGINT |
| deals_won_rank | 183 | 183 | 183 | BIGINT | BIGINT |
| cycle_time_rank | 2 | 2 | 2 | BIGINT | BIGINT |
| revenue_percentile | 0 | 0 | 0 | DOUBLE | DOUBLE |
| win_rate_percentile | 0 | 0 | 0 | DOUBLE | DOUBLE |
| volume_percentile | 0 | 0 | 0 | DOUBLE | DOUBLE |
| efficiency_percentile | 0 | 0 | 0 | DOUBLE | DOUBLE |
| overall_performance_score | 88 | 88 | 88 | DOUBLE | DOUBLE |
| performance_tier | 0 | 0 | 0 | VARCHAR | VARCHAR |
| sales_specialization | 0 | 0 | 0 | VARCHAR | VARCHAR |
| development_focus | 0 | 0 | 0 | VARCHAR | VARCHAR |
| pipeline_health_status | 0 | 0 | 0 | VARCHAR | VARCHAR |

large_deal_win_rate 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0.0 |

win_rate_rank 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 86 | 168 |

deals_won_rank 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 119 | 117 |

cycle_time_rank 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | 48 | 49 |

overall_performance_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K3 | 3934.6733668341712 | 3934.673366834171 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>1列；[{"column":"avg_lost_cycle_time","table_rows":200}]</code> |
| A3_constant_nonnull_column | <code>6列；[{"column":"lost_deals","value":"0"}]</code> |
| A4_equal_columns | <code>2组；[{"columns":["win_rate_percentage","enterprise_win_rate"],"nonnull_equal_rows":200,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>2组；[{"columns":["win_rate_percentage","enterprise_win_rate"],"nonnull_equal_rows":200,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| B7_specified_not_read | <code>["intermediate.int_hubspot__deals_enhanced (owner_id, amount, pipeline_stage_label, pipeline_label, deal_pipeline_stage_id, created_date, closed_date)"]</code> |
| D10_keyword_in_any_result_field | <code>命中数=5；assistant_trajectory p='sql/intermediate/int_hubspot__owner_performance_metrics.sql';s=open(p).read().replace('select *,case when close_date is null', 'select *,case when closed_date is null').replace('cast(close_date as date)', 'cast(closed_date as date)').replace('max(close_date)', 'max(closed_date)').replace('avg(cycle)', 'avg(cycle_days)');open(p,'w').write(s)</code> |

## 轨迹索引（不放输出原文）

本题事件总数：75；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/.events/sessions/49d1fc2e-5da1-4b-71664cc3fd873b2/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 9 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; sed -n '1,260p' run.py</code> | 13570 | true | false |
| 15 | run | <code>python - &lt;&lt;'PY'<br>import yaml<br>x=yaml.safe_load(open('docs/data_contract.yaml'))<br>print(len(x['staging_contract']['tables']))<br>for grp in ['intermediate_models','marketing_models','sales_models','service_m</code> | 755 | true | false |
| 19 | run | <code>cat &gt;&gt; /tmp/build.py &lt;&lt;'PY'<br># Intermediate models<br>put('intermediate','int_hubspot__owners_enhanced',"""select owner_id, active_user_id as owner_active_user_id, email_address as owner_email_address, fu</code> | 0 | false | false |
| 21 | run | <code>cat &gt;&gt; /tmp/build.py &lt;&lt;'PY'<br>put('intermediate','int_hubspot__deal_performance_metrics',"""with b as (select deal_id,deal_name,amount as deal_amount,pipeline_stage_label as deal_stage,pipeline_label as</code> | 0 | false | false |
| 27 | run | <code>cat &gt;&gt; /tmp/build.py &lt;&lt;'PY'<br># Sales models<br>put('sales','hubspot__deals',"select * from intermediate.int_hubspot__deals_enhanced")<br>put('sales','hubspot__companies',"select * from staging.stg_hubspot__c</code> | 0 | false | false |
| 29 | run | <code>cat &gt;&gt; /tmp/build.py &lt;&lt;'PY'<br>put('service','hubspot__tickets',"""with ca as (select tc.ticket_id,string_agg(coalesce(tc.company_id,''),',') company_ids,string_agg(coalesce(c.company_name,''),',') compa</code> | 3 | false | false |
| 31 | run | <code>python run.py &gt; /tmp/run.log 2&gt;&amp;1; rc=$?; tail -100 /tmp/run.log; exit $rc</code> | 7656 | true | false |
| 33 | run | <code>grep -E 'ERROR&#124;Executing: staging' /tmp/run.log &#124; head -45</code> | 5229 | false | false |
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

event 21 / message

```text
put('intermediate','int_hubspot__owner_performance_metrics',"""with d as (select *,case when close_date is null then 'Open' when deal_amount>0 then 'Won' when deal_amount=0 then 'Lost' else 'Unknown' end status,case when deal_amount>=100000 then 'Enterprise' when deal_amount>=50000 then 'Large' when deal_amount>=10000 then 'Medium' when deal_amount>0 then 'Small' else 'No Value' end size,date_diff('day',cast(created_date as date),cast(close_date as date)) cycle from intermediate.int_hubspot__deals_enhanced where owner_id is not null), a as (select d.owner_id,o.owner_full_name owner_name,o.owner_email_address owner_email,count(*)::bigint total_deals,count(*) filter(where status='Won')::bigint won_deals,count(*) filter(where status='Lost')::bigint lost_deals,count(*) filter(where status='Open')::bigint open_deals,100.0*count(*) filter(where status='Won')/nullif(count(*) filter(where status in ('Won','Lost')),0) win_rate_percentage,coalesce(sum(deal_amount) filter(where status='Won'),0) total_won_revenue,avg(deal_amount) filter(where status='Won') avg_won_deal_size,coalesce(sum(deal_amount) filter(where status='Open'),0) pipeline_value,avg(cycle) filter(where status='Won') avg_won_cycle_time,avg(cycle) filter(where status='Lost') avg_lost_cycle_time,min(created_date) first_deal_date,max(created_date) latest_deal_date,max(close_date) filter(where status='Won') last_won_date,count(*) filter(where size='Enterprise')::bigint enterprise_deals,count(*) filter(where size='Large')::bigint large_deals,count(*) filter(where size='Medium')::bigint medium_deals,count(*) filter(where size='Small')::bigint small_deals,100.0*count(*) filter(where size='Enterprise' and status='Won')/nullif(count(*) filter(where size='Enterprise' and status in('Won','Lost')),0) enterprise_win_rate,100.0*count(*) filter(where size='Large' and status='Won')/nullif(count(*) filter(where size='Large' and status in('Won','Lost')),0) large_deal_win_rate from d left join intermediate.int_hubspot__owners_enhanced o using(owner_id) group by d.owner_id,o.owner_full_name,o.owner_email_address), p as (select *,row_number() over(order by total_won_revenue desc) revenue_rank,row_number() over(order by win_rate_percentage desc nulls last) win_rate_rank,row_number() over(order by won_deals desc) deals_won_rank,row_number() over(order by coalesce(avg_won_cycle_time,999)) cycle_time_rank,100*percent_rank() over(order by total_won_revenue) revenue_percentile,100*percent_rank() over(order by win_rate_percentage) win_rate_percentile,100*percent_rank() over(order by won_deals) volume_percentile,100*percent_rank() over(order by coalesce(avg_won_cycle_time,999) desc) efficiency_percentile from a), s as (select *, revenue_percentile*40+win_rate_percentile*25+volume_percentile*20+efficiency_percentile*15 overall_performance_score from p) select *,case when overall_performance_score>=80 then 'Top Performer' when overall_performance_score>=60 then 'High Performer' when overall_performance_score>=40 then 'Core Performer' when overall_performance_score>=20 then 'Developing Performer' else 'Needs Improvement' end performance_tier,case when enterprise_deals>large_deals+medium_deals+small_deals then 'Enterprise Specialist' when large_deals>enterprise_deals+medium_deals+small_deals then 'Large Deal Specialist' when enterprise_deals+large_deals+medium_deals+small_deals>=3 then 'Generalist' else 'Focused Seller' end sales_specialization,case when win_rate_percentage<15 and avg_won_cycle_time>90 then 'Focus on Qualification and Process' when win_rate_percentage<15 then 'Improve Win Rate' when avg_won_cycle_time>120 then 'Accelerate Sales Cycle' when won_deals<5 then 'Increase Activity Volume' else 'Maintain Current Performance' end development_focus,case when pipeline_value>=2*total_won_revenue then 'Strong Pipeline' when pipeline_value>=total_won_revenue then 'Healthy Pipeline' when pipeline_value>=0.5*total_won_revenue then 'Adequate Pipeline' else 'Weak Pipeline' end pipeline_health_status from s""")
```
event 27 / message

```text
put('sales','hubspot__sales_rep_performance',"""with om as (select * from intermediate.int_hubspot__owner_performance_metrics where total_deals>0), d as (select *,year(created_date) y,month(created_date) m from intermediate.int_hubspot__deal_performance_metrics), monthly as (select owner_id,y performance_year,m performance_month,y*12+m month_index,count(distinct deal_id) monthly_deals_created,sum(case when deal_status='Won' then 1 else 0 end) monthly_deals_won,sum(case when deal_status='Won' then deal_amount else 0 end) monthly_revenue,sum(case when deal_status='Open' then deal_amount else 0 end) monthly_pipeline_added,100.0*count(*) filter(where deal_status='Won')/nullif(count(*) filter(where deal_status in('Won','Lost')),0) monthly_win_rate,avg(deal_cycle_time_days) filter(where deal_status='Won') monthly_avg_cycle_time from d where created_date is not null group by 1,2,3), trends as (select owner_id,avg(monthly_revenue) filter(where month_index>=year(current_date)*12+month(current_date)-6) recent_6m_avg_revenue,avg(monthly_revenue) filter(where month_index between year(current_date)*12+month(current_date)-12 and year(current_date)*12+month(current_date)-7) prior_6m_avg_revenue,avg(monthly_win_rate) filter(where month_index>=year(current_date)*12+month(current_date)-6) recent_6m_avg_win_rate,avg(monthly_win_rate) filter(where month_index between year(current_date)*12+month(current_date)-12 and year(current_date)*12+month(current_date)-7) prior_6m_avg_win_rate,stddev_samp(monthly_revenue) revenue_volatility,stddev_samp(monthly_deals_created) activity_consistency,count(*) filter(where month_index>=year(current_date)*12+month(current_date)-2) recent_active_months from monthly group by 1), seg as (select owner_id,mode() within group(order by deal_size_category) primary_deal_segment,count(distinct deal_size_category)::bigint segments_covered,sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Enterprise (100K+)') enterprise_revenue,sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Large (50K-100K)') large_revenue,sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Medium (10K-50K)') medium_revenue,sum(deal_amount) filter(where deal_status='Won' and deal_size_category='Small (<10K)') small_revenue from d group by 1), ranks as (select *,row_number() over(order by total_won_revenue desc) revenue_rank,row_number() over(order by win_rate_percentage desc) win_rate_rank,row_number() over(order by won_deals desc) volume_rank,row_number() over(order by coalesce(avg_won_cycle_time,999)) efficiency_rank,100*percent_rank() over(order by total_won_revenue) revenue_percentile,100*percent_rank() over(order by win_rate_percentage) win_rate_percentile,100*percent_rank() over(order by won_deals) volume_percentile,100*percent_rank() over(order by coalesce(avg_won_cycle_time,999) desc) efficiency_percentile from om), joined as (select r.*,s.primary_deal_segment,s.segments_covered,s.enterprise_revenue,s.large_revenue,s.medium_revenue,s.small_revenue,t.activity_consistency,t.recent_active_months,t.revenue_volatility,t.recent_6m_avg_revenue,t.prior_6m_avg_revenue,t.recent_6m_avg_win_rate,t.prior_6m_avg_win_rate,case when t.prior_6m_avg_revenue>0 then 100*(t.recent_6m_avg_revenue-t.prior_6m_avg_revenue)/t.prior_6m_avg_revenue end revenue_trend_percentage,case when t.prior_6m_avg_win_rate>0 then t.recent_6m_avg_win_rate-t.prior_6m_avg_win_rate end win_rate_trend_points from ranks r left join seg s on cast(r.owner_id as varchar)=cast(s.owner_id as varchar) left join trends t on cast(r.owner_id as varchar)=cast(t.owner_id as varchar)), scored as (select *,revenue_percentile*40+win_rate_percentile*25+volume_percentile*20+efficiency_percentile*15 overall_performance_score from joined) select owner_id,owner_name,owner_email,total_deals,won_deals,total_won_revenue,win_rate_percentage,avg_won_cycle_time,pipeline_value current_pipeline_value,enterprise_win_rate,large_deal_win_rate,enterprise_revenue,large_revenue,medium_revenue,small_revenue,revenue_rank,win_rate_rank,volume_rank,efficiency_rank,revenue_percentile,win_rate_percentile,volume_percentile,efficiency_percentile,overall_performance_score,case when overall_performance_score>=80 then 'Top Performer' when overall_performance_score>=60 then 'High Performer' when overall_performance_score>=40 then 'Core Performer' when overall_performance_score>=20 then 'Developing Performer' else 'Needs Improvement' end performance_tier,case when enterprise_revenue>coalesce(large_revenue,0)+coalesce(medium_revenue,0)+coalesce(small_revenue,0) then 'Enterprise Specialist' when large_revenue>coalesce(enterprise_revenue,0)+coalesce(medium_revenue,0)+coalesce(small_revenue,0) then 'Large Deal Specialist' when segments_covered>=3 then 'Generalist' else 'Focused Seller' end sales_specialization,case when win_rate_percentage<15 and avg_won_cycle_time>90 then 'Focus on Qualification and Process' when win_rate_percentage<15 then 'Improve Win Rate' when avg_won_cycle_time>120 then 'Accelerate Sales Cycle' when won_deals<5 then 'Increase Activity Volume' when revenue_trend_percentage< -5 then 'Address Performance Decline' else 'Maintain Current Performance' end development_focus,case when pipeline_value>=2*total_won_revenue then 'Strong Pipeline' when pipeline_value>=total_won_revenue then 'Healthy Pipeline' when pipeline_value>=0.5*total_won_revenue then 'Adequate Pipeline' else 'Weak Pipeline' end pipeline_health_status,primary_deal_segment,segments_covered,case when recent_active_months>=3 and total_deals>=10 then 'Highly Active' when recent_active_months>=2 and total_deals>=5 then 'Active' when recent_active_months>=1 then 'Moderately Active' else 'Low Activity' end activity_level,activity_consistency,recent_active_months,case when revenue_trend_percentage>=20 then 'Strong Growth' when revenue_trend_percentage>=5 then 'Steady Growth' when revenue_trend_percentage>=-5 then 'Stable' when revenue_trend_percentage>=-20 then 'Declining' else 'Significant Decline' end performance_trend,revenue_trend_percentage,win_rate_trend_points,revenue_volatility,recent_6m_avg_revenue,prior_6m_avg_revenue,recent_6m_avg_win_rate,prior_6m_avg_win_rate from scored order by overall_performance_score desc""")
```
event 35 / message

```text
Running command: sed -i 's/) cycle from intermediate/) as cycle_days from intermediate/' sql/intermediate/int_hubspot__owner_performance_metrics.sql; rm -f hubspot.duckdb && python run.py > /tmp/run2.log 2>&1; grep -E 'ERROR|layer complete|Executing:' /tmp/run2.log | tail -60
```
event 43 / message

```text
Running command: grep -n 'cycle\|close_date' sql/intermediate/int_hubspot__owner_performance_metrics.sql | head
```
event 45 / message

```text
p='sql/intermediate/int_hubspot__owner_performance_metrics.sql';s=open(p).read().replace('select *,case when close_date is null', 'select *,case when closed_date is null').replace('cast(close_date as date)', 'cast(closed_date as date)').replace('max(close_date)', 'max(closed_date)').replace('avg(cycle)', 'avg(cycle_days)');open(p,'w').write(s)
```
event 47 / message

```text
p='sql/intermediate/int_hubspot__owner_performance_metrics.sql';s=open(p).read().replace('deal_amount','amount');open(p,'w').write(s)
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-010.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-010/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/intermediate/int_hubspot__owner_performance_metrics.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/sql/intermediate/int_hubspot__owner_performance_metrics.sql`
- S6: `records/006_contract_impl-010.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/result.md`
- S10: `data/021_packages_work/021_impl-010_int_hubspot__owner_performance_metrics/021_impl-010_int_hubspot__owner_performance_metrics.json`
- S11: `data/005_cs_work/impl-010/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/hubspot.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/.events/sessions`
