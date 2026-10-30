# impl-010 | sales | hubspot__sales_performance_dashboard | 差异：S1；日期 原记录

## 契约完整原文

S3:1932–2014

```yaml
    - name: hubspot__sales_performance_dashboard
      schema: sales
      description: Quarterly sales performance metrics and forecasts derived from deal-level activity
      grain: One row per created_year and created_quarter
      source_models:
      - intermediate.int_hubspot__deal_performance_metrics
      business_logic: '- Build quarterly_sales_metrics (qsm) from intermediate.int_hubspot__deal_performance_metrics (dpb): - Keep records where created_year and created_quarter are present; aggregate by created_year, created_quarter. - Distinct counts of deal_id: total created, Won, Lost, Open; null deal_id never counted. - Revenue: - revenue_won_in_quarter: sum of deal_amount for Won deals; non-Won contribute zero; null amounts do not affect the sum. - pipeline_value_in_quarter: sum of deal_amount for Open deals; others contribute zero; null amounts ignored. - Averages and distribution for Won deals only: - avg_won_deal_size: average deal_amount; null amounts ignored; returns null if no values. - avg_sales_cycle_days: average deal_cycle_time_days; null values ignored; returns null if none. - median_sales_cycle_days: continuous 50th percentile of deal_cycle_time_days; null if none. - p25_deal_size: continuous 25th percentile of deal_amount; null if none. - p75_deal_size: continuous 75th percentile of deal_amount; null if none. - quarterly_win_rate (%): 100 times distinct Won divided by distinct Won+Lost; returns 0 if no Won+Lost. - active_sales_reps_in_quarter: distinct owner_id across all deals; null owner_id excluded. - Build forecast_metrics (fm), grouped by created_year, created_quarter: - total_open_pipeline: sum of deal_amount for Open deals; null amounts ignored. - weighted_pipeline_forecast: for Open deals, sum of deal_amount multiplied by the deal_size_category’s historical win rate (average of 1 for Won, 0 otherwise across all data); use 0.15 if no category history; null amounts ignored. - time_weighted_forecast: for Open deals with unknown cycle time, sum of deal_amount multiplied by a recency factor based on created_date relative to quarter boundaries at execution time (0.3 for current quarter, 0.5 for last quarter, 0.7 if older); null amounts ignored. - Left join qsm to fm on created_year and created_quarter. - Previous-quarter benchmarks: - Sort by created_year, created_quarter ascending; prev_quarter_revenue and prev_quarter_win_rate take the prior row’s values; first applicable row returns null. - Growth and indicators: - revenue_growth_rate (%): 100 times (current revenue_won_in_quarter minus previous) divided by previous; null if previous is null or not positive. - quarterly_performance_rating: Excellent if win_rate ≥ 30 and avg cycle ≤ 60; Good if win_rate ≥ 20 and avg cycle ≤ 90; Average if win_rate ≥ 15 and avg cycle ≤ 120; otherwise Below Average. - revenue_per_sales_rep: revenue_won_in_quarter divided by active_sales_reps_in_quarter; returns 0 if rep count is 0. - revenue_per_deal_created: revenue_won_in_quarter divided by deals_created_in_quarter; returns 0 if deal count is 0. - quarterly_goal_status: Exceeded Target if revenue_won_in_quarter ≥ 1,000,000; Met Target if ≥ 750,000; Close to Target if ≥ 500,000; otherwise Below Target. - Final output is sorted by created_year and created_quarter descending; the grain is one row per year-quarter.'
      columns:
      - name: created_year
        data_type: BIGINT
        description: Calendar year of deal creation; grouping key; never NULL in output
      - name: created_quarter
        data_type: BIGINT
        description: Calendar quarter (1–4) of deal creation; grouping key; never NULL in output
      - name: deals_created_in_quarter
        data_type: BIGINT
        description: Distinct count of deal_id in the quarter; NULL deal_id excluded
      - name: deals_won_in_quarter
        data_type: BIGINT
        description: Distinct count of deal_id with status Won in the quarter; NULL deal_id excluded
      - name: deals_lost_in_quarter
        data_type: BIGINT
        description: Distinct count of deal_id with status Lost in the quarter; NULL deal_id excluded
      - name: deals_still_open
        data_type: BIGINT
        description: Distinct count of deal_id with status Open in the quarter; NULL deal_id excluded
      - name: revenue_won_in_quarter
        data_type: DECIMAL(38,2)
        description: Sum of deal_amount for Won deals in the quarter; others contribute zero; NULL amounts ignored
      - name: pipeline_value_in_quarter
        data_type: DECIMAL(38,2)
        description: Sum of deal_amount for Open deals in the quarter; others contribute zero; NULL amounts ignored
      - name: total_open_pipeline
        data_type: DECIMAL(38,2)
        description: Sum of deal_amount for Open deals in the quarter from forecast metrics; NULL amounts ignored
      - name: quarterly_win_rate
        data_type: DOUBLE
        description: 'Percentage: 100 × distinct Won divided by distinct Won+Lost for the quarter; returns 0 when none Closed'
      - name: prev_quarter_win_rate
        data_type: DOUBLE
        description: Win rate from the previous quarter based on ascending year-quarter order; NULL for the first applicable row
      - name: prev_quarter_revenue
        data_type: DECIMAL(38,2)
        description: Revenue_won_in_quarter from the previous quarter based on ascending year-quarter order; NULL for the first applicable row
      - name: revenue_growth_rate
        data_type: DOUBLE
        description: Percent change vs previous quarter revenue; NULL if previous is NULL or not positive
      - name: avg_won_deal_size
        data_type: DOUBLE
        description: Average deal_amount for Won deals in the quarter; NULL amounts ignored; NULL if no values
      - name: p25_deal_size
        data_type: DECIMAL(18,2)
        description: Continuous 25th percentile of deal_amount for Won deals in the quarter; NULL if no values
      - name: p75_deal_size
        data_type: DECIMAL(18,2)
        description: Continuous 75th percentile of deal_amount for Won deals in the quarter; NULL if no values
      - name: avg_sales_cycle_days
        data_type: DOUBLE
        description: Average deal_cycle_time_days for Won deals in the quarter; NULL values ignored; NULL if none
      - name: median_sales_cycle_days
        data_type: DOUBLE
        description: Continuous 50th percentile of deal_cycle_time_days for Won deals in the quarter; NULL if none
      - name: active_sales_reps_in_quarter
        data_type: BIGINT
        description: Distinct count of owner_id across all deals in the quarter; NULL owner_id excluded
      - name: revenue_per_sales_rep
        data_type: DOUBLE
        description: Revenue_won_in_quarter divided by active_sales_reps_in_quarter; returns 0 when rep count is 0
      - name: revenue_per_deal_created
        data_type: DOUBLE
        description: Revenue_won_in_quarter divided by deals_created_in_quarter; returns 0 when deal count is 0
      - name: weighted_pipeline_forecast
        data_type: DOUBLE
        description: Sum for Open deals of deal_amount × category win rate (average of 1 for Won, 0 otherwise by deal_size_category); uses 0.15 if no history; NULL amounts ignored
      - name: time_weighted_forecast
        data_type: DECIMAL(38,3)
        description: Sum for Open deals with unknown cycle time of deal_amount × recency factor (0.3 current quarter, 0.5 last quarter, 0.7 older) using quarter boundaries at execution; NULL amounts ignored
      - name: quarterly_performance_rating
        data_type: VARCHAR
        description: Rating determined by win rate and average cycle time using ordered thresholds
      - name: quarterly_goal_status
        data_type: VARCHAR
        description: 'Target attainment from revenue_won_in_quarter: ≥1,000,000 Exceeded, ≥750,000 Met, ≥500,000 Close, otherwise Below'
```

## agent 最终 SQL

S4

```sql
with base as (select created_year,created_quarter,count(distinct deal_id)::bigint deals_created_in_quarter,count(distinct deal_id) filter(where deal_status='Won')::bigint deals_won_in_quarter,count(distinct deal_id) filter(where deal_status='Lost')::bigint deals_lost_in_quarter,count(distinct deal_id) filter(where deal_status='Open')::bigint deals_still_open,coalesce(sum(deal_amount) filter(where deal_status='Won'),0) revenue_won_in_quarter,coalesce(sum(deal_amount) filter(where deal_status='Open'),0) pipeline_value_in_quarter,avg(deal_amount) filter(where deal_status='Won') avg_won_deal_size,quantile_cont(deal_amount,0.25) filter(where deal_status='Won') p25_deal_size,quantile_cont(deal_amount,0.75) filter(where deal_status='Won') p75_deal_size,avg(deal_cycle_time_days) filter(where deal_status='Won') avg_sales_cycle_days,quantile_cont(deal_cycle_time_days,0.5) filter(where deal_status='Won') median_sales_cycle_days,count(distinct owner_id)::bigint active_sales_reps_in_quarter from intermediate.int_hubspot__deal_performance_metrics where created_year is not null and created_quarter is not null group by 1,2), hist as (select deal_size_category,avg(case when deal_status='Won' then 1.0 else 0.0 end) win_rate from intermediate.int_hubspot__deal_performance_metrics group by 1), fm as (select d.created_year,d.created_quarter,coalesce(sum(deal_amount) filter(where deal_status='Open'),0) total_open_pipeline,coalesce(sum(deal_amount*coalesce(h.win_rate,0.15)) filter(where deal_status='Open'),0) weighted_pipeline_forecast,sum(case when deal_status='Open' and deal_cycle_time_days is null then deal_amount*case when date_trunc('quarter',created_date)=date_trunc('quarter',current_date) then 0.3 when date_trunc('quarter',created_date)=date_trunc('quarter',current_date)-interval 3 month then 0.5 else 0.7 end end) time_weighted_forecast from intermediate.int_hubspot__deal_performance_metrics d left join hist h using(deal_size_category) where created_year is not null and created_quarter is not null group by 1,2), joined as (select b.*,f.total_open_pipeline,f.weighted_pipeline_forecast,f.time_weighted_forecast,lag(revenue_won_in_quarter) over(order by b.created_year,b.created_quarter) prev_quarter_revenue,lag(100.0*deals_won_in_quarter/nullif(deals_won_in_quarter+deals_lost_in_quarter,0)) over(order by b.created_year,b.created_quarter) prev_quarter_win_rate from base b left join fm f using(created_year,created_quarter)), final as (select *,case when prev_quarter_revenue>0 then (revenue_won_in_quarter-prev_quarter_revenue)*100.0/prev_quarter_revenue end revenue_growth_rate,case when deals_won_in_quarter+deals_lost_in_quarter>0 then 100.0*deals_won_in_quarter/(deals_won_in_quarter+deals_lost_in_quarter) else 0 end quarterly_win_rate,case when active_sales_reps_in_quarter>0 then revenue_won_in_quarter::double/active_sales_reps_in_quarter else 0 end revenue_per_sales_rep,case when deals_created_in_quarter>0 then revenue_won_in_quarter::double/deals_created_in_quarter else 0 end revenue_per_deal_created from joined) select created_year,created_quarter,deals_created_in_quarter,deals_won_in_quarter,deals_lost_in_quarter,deals_still_open,revenue_won_in_quarter,pipeline_value_in_quarter,total_open_pipeline,quarterly_win_rate,prev_quarter_win_rate,prev_quarter_revenue,revenue_growth_rate,avg_won_deal_size,p25_deal_size,p75_deal_size,avg_sales_cycle_days,median_sales_cycle_days,active_sales_reps_in_quarter,revenue_per_sales_rep,revenue_per_deal_created,weighted_pipeline_forecast,time_weighted_forecast,case when quarterly_win_rate>=30 and avg_sales_cycle_days<=60 then 'Excellent' when quarterly_win_rate>=20 and avg_sales_cycle_days<=90 then 'Good' when quarterly_win_rate>=15 and avg_sales_cycle_days<=120 then 'Average' else 'Below Average' end quarterly_performance_rating,case when revenue_won_in_quarter>=1000000 then 'Exceeded Target' when revenue_won_in_quarter>=750000 then 'Met Target' when revenue_won_in_quarter>=500000 then 'Close to Target' else 'Below Target' end quarterly_goal_status from final order by created_year desc,created_quarter desc
```

## gold SQL（仅供定位差异）

S5

```sql
-- Sales performance dashboard mart table
-- Comprehensive sales analytics with territory, quota, and forecasting metrics
with deal_performance_base as (
    select *
    from intermediate.int_hubspot__deal_performance_metrics
),

owner_performance_base as (
    select *
    from intermediate.int_hubspot__owner_performance_metrics
),

quarterly_sales_metrics as (
    select 
        dpb.created_year,
        dpb.created_quarter,
        
        -- Quarterly aggregations
        count(distinct dpb.deal_id) as deals_created_in_quarter,
        count(distinct case when dpb.deal_status = 'Won' then dpb.deal_id end) as deals_won_in_quarter,
        count(distinct case when dpb.deal_status = 'Lost' then dpb.deal_id end) as deals_lost_in_quarter,
        count(distinct case when dpb.deal_status = 'Open' then dpb.deal_id end) as deals_still_open,
        
        -- Revenue metrics
        sum(case when dpb.deal_status = 'Won' then dpb.deal_amount else 0 end) as revenue_won_in_quarter,
        sum(case when dpb.deal_status = 'Open' then dpb.deal_amount else 0 end) as pipeline_value_in_quarter,
        avg(case when dpb.deal_status = 'Won' then dpb.deal_amount end) as avg_won_deal_size,
        
        -- Performance rates  
        case 
            when count(distinct case when dpb.deal_status in ('Won', 'Lost') then dpb.deal_id end) > 0
            then cast(count(distinct case when dpb.deal_status = 'Won' then dpb.deal_id end) as decimal) / 
                 cast(count(distinct case when dpb.deal_status in ('Won', 'Lost') then dpb.deal_id end) as decimal) * 100
            else 0 
        end as quarterly_win_rate,
        
        -- Sales velocity
        avg(case when dpb.deal_status = 'Won' then dpb.deal_cycle_time_days end) as avg_sales_cycle_days,
        percentile_cont(0.5) within group (order by case when dpb.deal_status = 'Won' then dpb.deal_cycle_time_days end) as median_sales_cycle_days,
        
        -- Deal size distribution
        percentile_cont(0.25) within group (order by case when dpb.deal_status = 'Won' then dpb.deal_amount end) as p25_deal_size,
        percentile_cont(0.75) within group (order by case when dpb.deal_status = 'Won' then dpb.deal_amount end) as p75_deal_size,
        
        -- Activity metrics
        count(distinct dpb.owner_id) as active_sales_reps_in_quarter
        
    from deal_performance_base dpb
    where dpb.created_year is not null and dpb.created_quarter is not null
    group by 1, 2
),

territory_performance as (
    select 
        -- Simplified territory analysis based on deal size
        dpb.deal_size_category as territory_segment,
        
        -- Territory metrics
        count(distinct dpb.deal_id) as territory_total_deals,
        count(distinct case when dpb.deal_status = 'Won' then dpb.deal_id end) as territory_won_deals,
        sum(case when dpb.deal_status = 'Won' then dpb.deal_amount else 0 end) as territory_revenue,
        sum(case when dpb.deal_status = 'Open' then dpb.deal_amount else 0 end) as territory_pipeline,
        
        -- Territory performance rates
        case 
            when count(distinct case when dpb.deal_status in ('Won', 'Lost') then dpb.deal_id end) > 0
            then cast(count(distinct case when dpb.deal_status = 'Won' then dpb.deal_id end) as decimal) / 
                 cast(count(distinct case when dpb.deal_status in ('Won', 'Lost') then dpb.deal_id end) as decimal) * 100
            else 0 
        end as territory_win_rate,
        
        avg(case when dpb.deal_status = 'Won' then dpb.deal_cycle_time_days end) as territory_avg_cycle_time,
        count(distinct dpb.owner_id) as territory_sales_rep_count
        
    from deal_performance_base dpb
    group by 1
),

rep_ranking_metrics as (
    select 
        opb.entity_id as owner_id,
        opb.owner_name,
        opb.owner_email,
        opb.total_deals,
        opb.won_deals,
        opb.total_won_revenue,
        opb.win_rate_percentage,
        opb.avg_won_cycle_time,
        
        -- Performance rankings
        row_number() over (order by opb.total_won_revenue desc) as revenue_rank,
        row_number() over (order by opb.win_rate_percentage desc) as win_rate_rank,
        row_number() over (order by opb.won_deals desc) as deals_won_rank,
        row_number() over (order by opb.avg_won_cycle_time asc) as cycle_time_rank,
        
        -- Performance percentiles
        percent_rank() over (order by opb.total_won_revenue) as revenue_percentile,
        percent_rank() over (order by opb.win_rate_percentage) as win_rate_percentile,
        percent_rank() over (order by opb.won_deals) as deals_won_percentile,
        percent_rank() over (order by opb.avg_won_cycle_time desc) as cycle_time_percentile,
        
        -- Composite performance score
        (
            percent_rank() over (order by opb.total_won_revenue) * 30 +
            percent_rank() over (order by opb.win_rate_percentage) * 25 +
            percent_rank() over (order by opb.won_deals) * 25 +
            percent_rank() over (order by opb.avg_won_cycle_time desc) * 20
        ) * 100 as composite_performance_score
        
    from owner_performance_base opb
    where opb.total_deals > 0
),

forecast_metrics as (
    select 
        dpb.created_year,
        dpb.created_quarter,
        
        -- Pipeline forecast (based on historical win rates)
        sum(case when dpb.deal_status = 'Open' then dpb.deal_amount else 0 end) as total_open_pipeline,
        
        -- Weighted pipeline forecast
        sum(
            case 
                when dpb.deal_status = 'Open' then 
                    dpb.deal_amount * 
                    coalesce(
                        (select avg(case when dpb2.deal_status = 'Won' then 1.0 else 0.0 end) 
                         from deal_performance_base dpb2 
                         where dpb2.deal_size_category = dpb.deal_size_category), 
                        0.15
                    )
                else 0 
            end
        ) as weighted_pipeline_forecast,
        
        -- Time-based forecast (deals likely to close this quarter)
        sum(
            case 
                when dpb.deal_status = 'Open' 
                     and dpb.deal_cycle_time_days is null 
                     and dpb.created_date >= date_trunc('quarter', current_date)
                then dpb.deal_amount * 0.3  -- New deals this quarter
                when dpb.deal_status = 'Open' 
                     and dpb.deal_cycle_time_days is null 
                     and dpb.created_date >= date_trunc('quarter', current_date) - interval '1 quarter'
                then dpb.deal_amount * 0.5  -- Deals from last quarter
                when dpb.deal_status = 'Open' 
                     and dpb.deal_cycle_time_days is null 
                     and dpb.created_date < date_trunc('quarter', current_date) - interval '1 quarter'
                then dpb.deal_amount * 0.7  -- Older deals
                else 0 
            end
        ) as time_weighted_forecast
        
    from deal_performance_base dpb
    group by 1, 2
)

select 
    -- Quarter identification
    qsm.created_year,
    qsm.created_quarter,
    
    -- Quarterly performance metrics
    qsm.deals_created_in_quarter,
    qsm.deals_won_in_quarter,
    qsm.deals_lost_in_quarter,
    qsm.deals_still_open,
    qsm.revenue_won_in_quarter,
    qsm.pipeline_value_in_quarter,
    qsm.avg_won_deal_size,
    qsm.quarterly_win_rate,
    qsm.avg_sales_cycle_days,
    qsm.median_sales_cycle_days,
    qsm.p25_deal_size,
    qsm.p75_deal_size,
    qsm.active_sales_reps_in_quarter,
    
    -- Forecast metrics
    fm.total_open_pipeline,
    fm.weighted_pipeline_forecast,
    fm.time_weighted_forecast,
    
    -- Performance benchmarks
    lag(qsm.revenue_won_in_quarter, 1) over (order by qsm.created_year, qsm.created_quarter) as prev_quarter_revenue,
    lag(qsm.quarterly_win_rate, 1) over (order by qsm.created_year, qsm.created_quarter) as prev_quarter_win_rate,
    
    -- Growth calculations
    case 
        when lag(qsm.revenue_won_in_quarter, 1) over (order by qsm.created_year, qsm.created_quarter) > 0
        then (qsm.revenue_won_in_quarter - lag(qsm.revenue_won_in_quarter, 1) over (order by qsm.created_year, qsm.created_quarter)) / 
             lag(qsm.revenue_won_in_quarter, 1) over (order by qsm.created_year, qsm.created_quarter) * 100
        else null 
    end as revenue_growth_rate,
    
    -- Performance indicators
    case 
        when qsm.quarterly_win_rate >= 30 and qsm.avg_sales_cycle_days <= 60 then 'Excellent Performance'
        when qsm.quarterly_win_rate >= 20 and qsm.avg_sales_cycle_days <= 90 then 'Good Performance'
        when qsm.quarterly_win_rate >= 15 and qsm.avg_sales_cycle_days <= 120 then 'Average Performance'
        else 'Below Average Performance'
    end as quarterly_performance_rating,
    
    -- Sales efficiency metrics
    case 
        when qsm.active_sales_reps_in_quarter > 0 
        then qsm.revenue_won_in_quarter / qsm.active_sales_reps_in_quarter
        else 0 
    end as revenue_per_sales_rep,
    
    case 
        when qsm.deals_created_in_quarter > 0 
        then qsm.revenue_won_in_quarter / qsm.deals_created_in_quarter
        else 0 
    end as revenue_per_deal_created,
    
    -- Goal achievement indicators (assuming quarterly targets)
    case 
        when qsm.revenue_won_in_quarter >= 1000000 then 'Exceeded Target'
        when qsm.revenue_won_in_quarter >= 750000 then 'Met Target'
        when qsm.revenue_won_in_quarter >= 500000 then 'Close to Target'
        else 'Below Target'
    end as quarterly_goal_status
    
from quarterly_sales_metrics qsm
left join forecast_metrics fm on qsm.created_year = fm.created_year and qsm.created_quarter = fm.created_quarter
order by qsm.created_year desc, qsm.created_quarter desc
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 7 | 7 | 0 | 0 | 2 | 2 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"created_year":"2023"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| created_year | 0 | 0 | 0 | BIGINT | BIGINT |
| created_quarter | 0 | 0 | 0 | BIGINT | BIGINT |
| deals_created_in_quarter | 0 | 0 | 0 | BIGINT | BIGINT |
| deals_won_in_quarter | 0 | 0 | 0 | BIGINT | BIGINT |
| deals_lost_in_quarter | 0 | 0 | 0 | BIGINT | BIGINT |
| deals_still_open | 0 | 0 | 0 | BIGINT | BIGINT |
| revenue_won_in_quarter | 0 | 0 | 0 | DECIMAL(38,2) | DECIMAL(38,2) |
| pipeline_value_in_quarter | 0 | 0 | 0 | DECIMAL(38,2) | DECIMAL(38,2) |
| avg_won_deal_size | 0 | 0 | 0 | DOUBLE | DOUBLE |
| quarterly_win_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| p25_deal_size | 0 | 0 | 0 | DECIMAL(18,2) | DECIMAL(18,2) |
| p75_deal_size | 0 | 0 | 0 | DECIMAL(18,2) | DECIMAL(18,2) |
| active_sales_reps_in_quarter | 0 | 0 | 0 | BIGINT | BIGINT |
| total_open_pipeline | 0 | 0 | 0 | DECIMAL(38,2) | DECIMAL(38,2) |
| weighted_pipeline_forecast | 0 | 0 | 0 | DOUBLE | DOUBLE |
| time_weighted_forecast | 0 | 0 | 0 | DECIMAL(38,3) | DECIMAL(38,3) |
| prev_quarter_revenue | 0 | 0 | 0 | DECIMAL(38,2) | DECIMAL(38,2) |
| prev_quarter_win_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| revenue_growth_rate | 3 | 3 | 3 | DOUBLE | DOUBLE |
| quarterly_performance_rating | 7 | 7 | 7 | VARCHAR | VARCHAR |
| revenue_per_sales_rep | 0 | 0 | 0 | DOUBLE | DOUBLE |
| quarterly_goal_status | 0 | 0 | 0 | VARCHAR | VARCHAR |

revenue_growth_rate 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1},{"value":"-7.263725032671558","rows":1},{"value":"-7.679052309149123","rows":1},{"value":"4.5169932653626175","rows":1}]</code> | <code>[{"value":null,"rows":1},{"value":"-7.263725032671557","rows":1},{"value":"-7.679052309149122","rows":1},{"value":"4.5169932653626175","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

quarterly_performance_rating 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Below Average","rows":4}]</code> | <code>[{"value":"Below Average Performance","rows":4}]</code> |
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
| A3_constant_nonnull_column | <code>3列；[{"column":"deals_lost_in_quarter","value":"0"}]</code> |
| A4_equal_columns | <code>1组；[{"columns":["pipeline_value_in_quarter","total_open_pipeline"],"nonnull_equal_rows":7,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>1组；[{"columns":["pipeline_value_in_quarter","total_open_pipeline"],"nonnull_equal_rows":7,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| C9_agent_runtime_text | <code>S4:1 current_date；命中数=2</code> |
| C9_gold_runtime_text | <code>S5:142 current_date；命中数=3</code> |
| D10_keyword_in_any_result_field | <code>命中数=2；assistant_trajectory put('sales','hubspot__sales_performance_dashboard',"""with base as (select created_year,created_quarter,count(distinct deal_id)::bigint deals_created_in_quarter,count(distinct deal_id) filter(where deal_status='Won')::bigint deals_won_in_quarter,count(distinct deal_id) filter(where deal_status='Lost')::bigint deals_lost_in_quarter,count(distinct deal_id) filter(where deal_status='Open')::bigint deals_still_open,coalesce(sum(deal_amount) filter(where deal_status='Won'),0) revenue_won_in_quarter,coalesce(sum(deal_amount) filter(where deal_status='Open'),0) pipeline_value_in_quarter,avg(deal_amount) filter(where deal_status='Won') avg_won_deal_size,quantile_cont(deal_amount,0.25) filter(where deal_status='Won') p25_deal_size,quantile_cont(deal_amount,0.75) filter(where deal_status='Won') p75_deal_size,avg(deal_cycle_time_days) filter(where deal_status='Won') avg_sales_cycle_days,quantile_cont(deal_cycle_time_days,0.5) filter(where deal_status='Won') median_sales_cycle_days,count(distinct owner_id)::bigint active_sales_reps_in_quarter from intermediate.int_hubspot__deal_performance_metrics where created_year is not null and created_quarter is not null group by 1,2), hist as (select deal_size_category,avg(case when deal_status='Won' then 1.0 else 0.0 end) win_rate from intermediate.int_hubspot__deal_performance_metrics group by 1), fm as (select d.created_year,d.created_quarter,coalesce(sum(deal_amount) filter(where deal_status='Open'),0) total_open_pipeline,coalesce(sum(deal_amount*coalesce(h.win_rate,0.15)) filter(where deal_status='Open'),0) weighted_pipeline_forecast,sum(case when deal_status='Open' and deal_cycle_time_days is null then deal_amount*case when date_trunc('quarter',created_date)=date_trunc('quarter',current_date) then 0.3 when date_trunc('quarter',created_date)=date_trunc('quarter',current_date)-interval 3 month then 0.5 else 0.7 end end) time_weighted_forecast from intermediate.int_hubspot__deal_performance_metrics d left join hist h using(deal_size_category) where created_year is not null and created_quarter is not null group by 1,2), joined as (select b.*,f.total_open_pipeline,f.weighted_pipeline_forecast,f.time_weighted_forecast,lag(revenue_won_in_quarter) over(order by b.created_year,b.created_quarter) prev_quarter_revenue,lag(100.0*deals_won_in_quarter/nullif(deals_won_in_quarter+deals_lost_in_quarter,0)) over(order by b.created_year,b.created_quarter) prev_quarter_win_rate from base b left join fm f using(created_year,created_quarter)), final as (select *,case when prev_quarter_revenue&gt;0 then (revenue_won_in_quarter-prev_quarter_revenue)*100.0/prev_quarter_revenue end revenue_growth_rate,case when deals_won_in_quarter+deals_lost_in_quarter&gt;0 then 100.0*deals_won_in_quarter/(deals_won_in_quarter+deals_lost_in_quarter) else 0 end quarterly_win_rate,case when active_sales_reps_in_quarter&gt;0 then revenue_won_in_quarter::double/active_sales_reps_in_quarter else 0 end revenue_per_sales_rep,case when deals_created_in_quarter&gt;0 then revenue_won_in_quarter::double/deals_created_in_quarter else 0 end revenue_per_deal_created from joined) select created_year,created_quarter,deals_created_in_quarter,deals_won_in_quarter,deals_lost_in_quarter,deals_still_open,revenue_won_in_quarter,pipeline_value_in_quarter,total_open_pipeline,quarterly_win_rate,prev_quarter_win_rate,prev_quarter_revenue,revenue_growth_rate,avg_won_deal_size,p25_deal_size,p75_deal_size,avg_sales_cycle_days,median_sales_cycle_days,active_sales_reps_in_quarter,revenue_per_sales_rep,revenue_per_deal_created,weighted_pipeline_forecast,time_weighted_forecast,case when quarterly_win_rate&gt;=30 and avg_sales_cycle_days&lt;=60 then 'Excellent' when quarterly_win_rate&gt;=20 and avg_sales_cycle_days&lt;=90 then 'Good' when quarterly_win_rate&gt;=15 and avg_sales_cycle_days&lt;=120 then 'Average' else 'Below Average' end quarterly_performance_rating,case when revenue_won_in_quarter&gt;=1000000 then 'Exceeded Target' when revenue_won_in_quarter&gt;=750000 then 'Met Target' when revenue_won_in_quarter&gt;=500000 then 'Close to Target' else 'Below Target' end quarterly_goal_status from final order by created_year desc,created_quarter desc""")</code> |

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
| 49 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,yaml<br>c=duckdb.connect('hubspot.duckdb',read_only=True)<br>contract=yaml.safe_load(open('docs/data_contract.yaml'))<br>for key,layer in [('tables','staging_contract'),('intermed</code> | 2557 | true | false |
| 63 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('hubspot.duckdb',read_only=True)<br>for schema in ['staging','intermediate','marketing','sales','service']:<br> print(schema,c.execute(f"select table_name from</code> | 1569 | true | false |
| 65 | run | <code>grep -R ';' -n sql &#124;&#124; true; find sql -type f &#124; sort</code> | 1842 | true | false |

### agent action 的 thought/message 命中原句

event 27 / message

```text
put('sales','hubspot__sales_performance_dashboard',"""with base as (select created_year,created_quarter,count(distinct deal_id)::bigint deals_created_in_quarter,count(distinct deal_id) filter(where deal_status='Won')::bigint deals_won_in_quarter,count(distinct deal_id) filter(where deal_status='Lost')::bigint deals_lost_in_quarter,count(distinct deal_id) filter(where deal_status='Open')::bigint deals_still_open,coalesce(sum(deal_amount) filter(where deal_status='Won'),0) revenue_won_in_quarter,coalesce(sum(deal_amount) filter(where deal_status='Open'),0) pipeline_value_in_quarter,avg(deal_amount) filter(where deal_status='Won') avg_won_deal_size,quantile_cont(deal_amount,0.25) filter(where deal_status='Won') p25_deal_size,quantile_cont(deal_amount,0.75) filter(where deal_status='Won') p75_deal_size,avg(deal_cycle_time_days) filter(where deal_status='Won') avg_sales_cycle_days,quantile_cont(deal_cycle_time_days,0.5) filter(where deal_status='Won') median_sales_cycle_days,count(distinct owner_id)::bigint active_sales_reps_in_quarter from intermediate.int_hubspot__deal_performance_metrics where created_year is not null and created_quarter is not null group by 1,2), hist as (select deal_size_category,avg(case when deal_status='Won' then 1.0 else 0.0 end) win_rate from intermediate.int_hubspot__deal_performance_metrics group by 1), fm as (select d.created_year,d.created_quarter,coalesce(sum(deal_amount) filter(where deal_status='Open'),0) total_open_pipeline,coalesce(sum(deal_amount*coalesce(h.win_rate,0.15)) filter(where deal_status='Open'),0) weighted_pipeline_forecast,sum(case when deal_status='Open' and deal_cycle_time_days is null then deal_amount*case when date_trunc('quarter',created_date)=date_trunc('quarter',current_date) then 0.3 when date_trunc('quarter',created_date)=date_trunc('quarter',current_date)-interval 3 month then 0.5 else 0.7 end end) time_weighted_forecast from intermediate.int_hubspot__deal_performance_metrics d left join hist h using(deal_size_category) where created_year is not null and created_quarter is not null group by 1,2), joined as (select b.*,f.total_open_pipeline,f.weighted_pipeline_forecast,f.time_weighted_forecast,lag(revenue_won_in_quarter) over(order by b.created_year,b.created_quarter) prev_quarter_revenue,lag(100.0*deals_won_in_quarter/nullif(deals_won_in_quarter+deals_lost_in_quarter,0)) over(order by b.created_year,b.created_quarter) prev_quarter_win_rate from base b left join fm f using(created_year,created_quarter)), final as (select *,case when prev_quarter_revenue>0 then (revenue_won_in_quarter-prev_quarter_revenue)*100.0/prev_quarter_revenue end revenue_growth_rate,case when deals_won_in_quarter+deals_lost_in_quarter>0 then 100.0*deals_won_in_quarter/(deals_won_in_quarter+deals_lost_in_quarter) else 0 end quarterly_win_rate,case when active_sales_reps_in_quarter>0 then revenue_won_in_quarter::double/active_sales_reps_in_quarter else 0 end revenue_per_sales_rep,case when deals_created_in_quarter>0 then revenue_won_in_quarter::double/deals_created_in_quarter else 0 end revenue_per_deal_created from joined) select created_year,created_quarter,deals_created_in_quarter,deals_won_in_quarter,deals_lost_in_quarter,deals_still_open,revenue_won_in_quarter,pipeline_value_in_quarter,total_open_pipeline,quarterly_win_rate,prev_quarter_win_rate,prev_quarter_revenue,revenue_growth_rate,avg_won_deal_size,p25_deal_size,p75_deal_size,avg_sales_cycle_days,median_sales_cycle_days,active_sales_reps_in_quarter,revenue_per_sales_rep,revenue_per_deal_created,weighted_pipeline_forecast,time_weighted_forecast,case when quarterly_win_rate>=30 and avg_sales_cycle_days<=60 then 'Excellent' when quarterly_win_rate>=20 and avg_sales_cycle_days<=90 then 'Good' when quarterly_win_rate>=15 and avg_sales_cycle_days<=120 then 'Average' else 'Below Average' end quarterly_performance_rating,case when revenue_won_in_quarter>=1000000 then 'Exceeded Target' when revenue_won_in_quarter>=750000 then 'Met Target' when revenue_won_in_quarter>=500000 then 'Close to Target' else 'Below Target' end quarterly_goal_status from final order by created_year desc,created_quarter desc""")
```
event 63 / message

```text
for name in ['stg_hubspot__company','stg_hubspot__ticket','hubspot__tickets','hubspot__sales_performance_dashboard']:
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/009_tolerance_tables.jsonl`
- S2: `records/009_cs_impl-010.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-010/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/sql/sales/hubspot__sales_performance_dashboard.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/sql/sales/hubspot__sales_performance_dashboard.sql`
- S6: `records/006_contract_impl-010.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/dacomp-de-impl-010/result.md`
- S10: `data/021_packages_work/021_impl-010_hubspot__sales_performance_dashboard/021_impl-010_hubspot__sales_performance_dashboard.json`
- S11: `data/009_cs_work/impl-010/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-010/hubspot.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-010/agent/.events/sessions`
