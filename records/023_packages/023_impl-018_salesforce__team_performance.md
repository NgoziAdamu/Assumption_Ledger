# impl-018 | marts | salesforce__team_performance | 差异：S1；日期 原记录

## 契约完整原文

S3:3278–3391

```yaml
    - name: salesforce__team_performance
      description: Aggregated Salesforce team metrics by manager and team type for active users, including tiers, health score, and recent performance
      grain: One row per team_manager_id + team_manager_name + team_type
      source_models:
      - intermediate.int_salesforce__user_performance
      - marts.dim_salesforce__user
      - marts.salesforce__revenue_analytics
      business_logic: '- Create user_performance from intermediate.int_salesforce__user_performance and user_dimension from marts.dim_salesforce__user. - From marts.salesforce__revenue_analytics, aggregate per owner_id: total revenue won (sum of won_revenue), deals won (count of rows where won), average sales cycle (average days on won deals), current-quarter won revenue (sum where in current quarter), previous-quarter won revenue (sum where in previous quarter), and current-quarter deals won (count of won deals in current quarter). - Join user_dimension to user_performance on user_id (left join), and to revenue_data on user_id = owner_id (left join). Keep only rows where the user is active, then group by: • team_manager_id = manager_id with nulls replaced by "No Manager" • team_manager_name = manager_name with nulls replaced by "No Manager" • team_type = user_type (can be null) - For each group, compute: • team_size = distinct count of users • active_team_members = distinct count of users where active (equals team_size under the active-user filter) • high_performers, good_performers, developing_performers, new_users = distinct user counts by performance_tier exact match • team_total_opportunities and team_won_opportunities = sums across users • team_total_revenue and team_total_pipeline = sums of revenue and pipeline amounts • team_win_rate_percentage = 100 × (total won opportunities ÷ total opportunities), rounded to two decimals; return 0 if total opportunities is zero or null • avg_opportunities_per_member and avg_wins_per_member = per-user averages, rounded to one decimal; nulls excluded • avg_revenue_per_member = per-user average revenue won, rounded to the nearest whole unit; nulls excluded • avg_win_rate_per_member = per-user average win rate percentage, rounded to two decimals; nulls excluded • team_total_leads and team_converted_leads = sums across users • team_lead_conversion_rate = 100 × (converted leads ÷ total leads), rounded to two decimals; return 0 if total leads is zero or null • team_total_activities = sum across users; avg_activity_completion_rate = per-user average completion rate percentage, rounded to two decimals; nulls excluded • team_revenue_current_quarter and team_deals_current_quarter = sums of current-quarter revenue and deals from revenue_data • revenue_growth_qoq_percentage = 100 × (current-quarter revenue minus previous-quarter revenue) ÷ previous-quarter revenue, rounded to two decimals; null if previous-quarter revenue is zero or null • team_activities_per_win_ratio = total activities ÷ total won opportunities, rounded to two decimals; null unless both totals are greater than zero • top_revenue_performer = the full_name of the member with the highest total won amount; members without a value are ranked last; ties are arbitrary • top_win_rate_performer = the full_name of the member with the highest win rate percentage; members without a value are ranked last; ties are arbitrary • avg_team_tenure_days = average user tenure in days, rounded to the nearest whole day; nulls excluded • new_team_members and veteran_team_members = distinct user counts where user_tenure_category is "New User" or "Veteran" - Enhance with: • team_performance_tier: - High Performing Team: win rate ≥ 30, average revenue per member ≥ 100,000, and at least 2 high performers - Good Performing Team: win rate ≥ 20, average revenue per member ≥ 50,000, and high + good performers cover at least half of the team - Developing Team: win rate ≥ 10 and average revenue per member ≥ 25,000 - Otherwise: Needs Improvement • team_health_score = sum of five components, clipped to the 0–100 range: - Win rate contribution: the win rate capped at 25 - High-performer share: 25 if high performers ÷ team_size ≥ 0.3, else 15 if ≥ 0.1, else 5 (when team_size is 0, this defaults to 5) - Activity completion: 20 if ≥ 80%, else 15 if ≥ 60%, else 10 - Revenue growth: 20 if > 10%, else 15 if > 0%, else 10 if ≥ -10%, else 5 - Lead conversion: 10 if ≥ 20%, else 7 if ≥ 10%, else 3 • team_diversity_level: - High Diversity: team_size ≥ 5 and at least one high, one good, and one developing performer - Medium Diversity: team_size ≥ 3 and at least one high or good performer and at least one developing performer - Low Diversity: team_size ≥ 2 - Otherwise: Single Member - Output all fields from the enhanced dataset; final ordering is by team_health_score descending, then team_total_revenue descending.'
      columns:
      - name: team_manager_id
        data_type: VARCHAR
        description: Manager identifier for the team with nulls replaced by 'No Manager'.
      - name: team_manager_name
        data_type: VARCHAR
        description: Manager full name with nulls replaced by 'No Manager'.
      - name: team_type
        data_type: VARCHAR
        description: Team type from user_type; can be null and is part of the grouping.
      - name: team_size
        data_type: BIGINT
        description: Distinct count of active users in the team after filtering to active users.
      - name: active_team_members
        data_type: BIGINT
        description: Distinct count of active users; equals team_size under the active-user filter.
      - name: high_performers
        data_type: BIGINT
        description: Distinct user count with performance_tier equal to 'High Performer'.
      - name: good_performers
        data_type: BIGINT
        description: Distinct user count with performance_tier equal to 'Good Performer'.
      - name: developing_performers
        data_type: BIGINT
        description: Distinct user count with performance_tier equal to 'Developing'.
      - name: new_users
        data_type: BIGINT
        description: Distinct user count with performance_tier equal to 'New User'.
      - name: team_performance_tier
        data_type: VARCHAR
        description: Team tier based on win rate, average revenue per member, and performer mix thresholds.
      - name: team_health_score
        data_type: DOUBLE
        description: Composite score from five components capped between 0 and 100.
      - name: team_diversity_level
        data_type: VARCHAR
        description: Diversity category based on team size and presence across performance tiers.
      - name: team_total_opportunities
        data_type: HUGEINT
        description: Total opportunities summed across team; nulls ignored and result is null if all inputs are null.
      - name: team_won_opportunities
        data_type: HUGEINT
        description: Total won opportunities summed across team; nulls ignored and result is null if all inputs are null.
      - name: team_win_rate_percentage
        data_type: DOUBLE
        description: Win rate as 100 × won opportunities ÷ total opportunities, rounded to two decimals; returns 0 if total opportunities is zero or null.
      - name: team_total_revenue
        data_type: DECIMAL(38,2)
        description: Total revenue won summed across team; currency formatted to two decimals; nulls ignored and result is null if all inputs are null.
      - name: team_total_pipeline
        data_type: DECIMAL(38,2)
        description: Total pipeline amount summed across team; currency formatted to two decimals; nulls ignored and result is null if all inputs are null.
      - name: avg_opportunities_per_member
        data_type: DOUBLE
        description: Average opportunities per user rounded to one decimal; excludes nulls and is null if no values.
      - name: avg_wins_per_member
        data_type: DOUBLE
        description: Average won opportunities per user rounded to one decimal; excludes nulls and is null if no values.
      - name: avg_revenue_per_member
        data_type: DOUBLE
        description: Average revenue won per user rounded to the nearest whole unit; excludes nulls and is null if no values.
      - name: avg_win_rate_per_member
        data_type: DOUBLE
        description: Average user win rate percentage rounded to two decimals; excludes nulls and is null if no values.
      - name: team_total_leads
        data_type: HUGEINT
        description: Total leads summed across team; nulls ignored and result is null if all inputs are null.
      - name: team_converted_leads
        data_type: HUGEINT
        description: Total converted leads summed across team; nulls ignored and result is null if all inputs are null.
      - name: team_lead_conversion_rate
        data_type: DOUBLE
        description: Lead conversion as 100 × converted ÷ total leads, rounded to two decimals; returns 0 if total leads is zero or null.
      - name: team_total_activities
        data_type: HUGEINT
        description: Total activities summed across team; nulls ignored and result is null if all inputs are null.
      - name: avg_activity_completion_rate
        data_type: DOUBLE
        description: Average activity completion rate percentage rounded to two decimals; excludes nulls and is null if no values.
      - name: team_revenue_current_quarter
        data_type: DECIMAL(38,2)
        description: Total current-quarter revenue won summed across team; currency with two decimals; nulls ignored and result is null if all inputs are null.
      - name: team_deals_current_quarter
        data_type: HUGEINT
        description: Total current-quarter deals won summed across team; nulls ignored and result is null if all inputs are null.
      - name: revenue_growth_qoq_percentage
        data_type: DOUBLE
        description: Quarter-over-quarter revenue growth percentage rounded to two decimals; null when previous-quarter revenue is zero or null.
      - name: team_activities_per_win_ratio
        data_type: DOUBLE
        description: Total activities divided by total won opportunities, rounded to two decimals; null unless both totals are greater than zero.
      - name: top_revenue_performer
        data_type: VARCHAR
        description: Full name of the member with the highest total won amount; nulls ranked last and ties are arbitrary.
      - name: top_win_rate_performer
        data_type: VARCHAR
        description: Full name of the member with the highest win rate percentage; nulls ranked last and ties are arbitrary.
      - name: avg_team_tenure_days
        data_type: DOUBLE
        description: Average user tenure in days rounded to the nearest whole day; excludes nulls and is null if no values.
      - name: new_team_members
        data_type: BIGINT
        description: Distinct user count where user_tenure_category is 'New User'.
      - name: veteran_team_members
        data_type: BIGINT
        description: Distinct user count where user_tenure_category is 'Veteran'.
```

## agent 最终 SQL

S4

```sql
with revenue_by_owner as (
 select owner_id,sum(won_revenue) as total_revenue_won,
 count(*) filter(where is_won is true) as deals_won,
 avg(sales_cycle_days) filter(where is_won is true) as avg_sales_cycle_days,
 sum(won_revenue) filter(where is_current_quarter) as revenue_current_quarter,
 sum(won_revenue) filter(where is_previous_quarter) as revenue_previous_quarter,
 count(*) filter(where is_won is true and is_current_quarter) as deals_current_quarter
 from marts.salesforce__revenue_analytics group by owner_id
),
member_metrics as (
 select d.user_id,d.full_name,d.manager_id,d.manager_name,d.user_type,d.is_active,d.performance_tier,d.user_tenure_days,d.user_tenure_category,
 p.total_opportunities,p.won_opportunities,p.total_won_amount,p.total_pipeline_amount,p.win_rate_percentage,p.total_leads,p.converted_leads,
 p.total_activities,p.activity_completion_rate_percentage,r.total_revenue_won,r.deals_won,r.avg_sales_cycle_days,r.revenue_current_quarter,r.revenue_previous_quarter,r.deals_current_quarter
 from marts.dim_salesforce__user d
 left join intermediate.int_salesforce__user_performance p on d.user_id=p.user_id
 left join revenue_by_owner r on d.user_id=r.owner_id
 where d.is_active=true
),
team_rollup as (
 select coalesce(manager_id,'No Manager') as team_manager_id,coalesce(manager_name,'No Manager') as team_manager_name,user_type as team_type,
 count(distinct user_id) as team_size,count(distinct user_id) filter(where is_active) as active_team_members,
 count(distinct user_id) filter(where performance_tier='High Performer') as high_performers,
 count(distinct user_id) filter(where performance_tier='Good Performer') as good_performers,
 count(distinct user_id) filter(where performance_tier='Developing') as developing_performers,
 count(distinct user_id) filter(where performance_tier='New User') as new_users,
 sum(total_opportunities) as team_total_opportunities,sum(won_opportunities) as team_won_opportunities,
 sum(total_revenue_won) as team_total_revenue,sum(total_pipeline_amount) as team_total_pipeline,
 avg(total_opportunities) as avg_opportunities_per_member,avg(won_opportunities) as avg_wins_per_member,
 round(avg(total_revenue_won)) as avg_revenue_per_member,round(avg(win_rate_percentage),2) as avg_win_rate_per_member,
 sum(total_leads) as team_total_leads,sum(converted_leads) as team_converted_leads,sum(total_activities) as team_total_activities,
 round(avg(activity_completion_rate_percentage),2) as avg_activity_completion_rate,
 sum(revenue_current_quarter) as team_revenue_current_quarter,sum(deals_current_quarter) as team_deals_current_quarter,
 sum(revenue_previous_quarter) as team_revenue_previous_quarter,
 case when sum(team_total_opportunities) over(partition by coalesce(manager_id,'No Manager'),coalesce(manager_name,'No Manager'),user_type)>0 then 0 end as unused_placeholder,
 round(avg(user_tenure_days)) as avg_team_tenure_days,
 count(distinct user_id) filter(where user_tenure_category='New User') as new_team_members,
 count(distinct user_id) filter(where user_tenure_category='Veteran') as veteran_team_members
 from member_metrics group by manager_id,manager_name,user_type
),
performer_names as (
 select coalesce(manager_id,'No Manager') as team_manager_id,coalesce(manager_name,'No Manager') as team_manager_name,user_type as team_type,
 arg_max(full_name,total_revenue_won) filter(where total_revenue_won is not null) as top_revenue_performer,
 arg_max(full_name,win_rate_percentage) filter(where win_rate_percentage is not null) as top_win_rate_performer
 from member_metrics group by manager_id,manager_name,user_type
),
scored as (
 select t.*,pn.top_revenue_performer,pn.top_win_rate_performer,
 case when team_total_opportunities>0 then round(team_won_opportunities::double/team_total_opportunities*100,2) else 0.0 end as team_win_rate_percentage,
 case when team_total_leads>0 then round(team_converted_leads::double/team_total_leads*100,2) else 0.0 end as team_lead_conversion_rate,
 case when team_revenue_previous_quarter>0 then round((team_revenue_current_quarter-team_revenue_previous_quarter)::double/team_revenue_previous_quarter*100,2) end as revenue_growth_qoq_percentage,
 case when team_total_activities>0 and team_won_opportunities>0 then round(team_total_activities::double/team_won_opportunities,2) end as team_activities_per_win_ratio
 from team_rollup t left join performer_names pn using(team_manager_id,team_manager_name,team_type)
),
final_scores as (
 select *,least(100.0,greatest(0.0,
 least(team_win_rate_percentage,25)
 + case when team_size>0 and high_performers::double/team_size>=0.3 then 25 when team_size>0 and high_performers::double/team_size>=0.1 then 15 else 5 end
 + case when coalesce(avg_activity_completion_rate,0)>=80 then 20 when coalesce(avg_activity_completion_rate,0)>=60 then 15 else 10 end
 + case when coalesce(revenue_growth_qoq_percentage,0)>10 then 20 when coalesce(revenue_growth_qoq_percentage,0)>0 then 15 when coalesce(revenue_growth_qoq_percentage,0)>=-10 then 10 else 5 end
 + case when coalesce(team_lead_conversion_rate,0)>=20 then 10 when coalesce(team_lead_conversion_rate,0)>=10 then 7 else 3 end))::double as team_health_score
 from scored
)
select team_manager_id,team_manager_name,team_type,team_size,active_team_members,high_performers,good_performers,developing_performers,new_users,
 case when team_win_rate_percentage>=30 and avg_revenue_per_member>=100000 and high_performers>=2 then 'High Performing Team'
 when team_win_rate_percentage>=20 and avg_revenue_per_member>=50000 and high_performers+good_performers>=team_size/2.0 then 'Good Performing Team'
 when team_win_rate_percentage>=10 and avg_revenue_per_member>=25000 then 'Developing Team' else 'Needs Improvement' end as team_performance_tier,
 team_health_score,
 case when team_size>=5 and high_performers>=1 and good_performers>=1 and developing_performers>=1 then 'High Diversity'
 when team_size>=3 and (high_performers>=1 or good_performers>=1) and developing_performers>=1 then 'Medium Diversity'
 when team_size>=2 then 'Low Diversity' else 'Single Member' end as team_diversity_level,
 team_total_opportunities,team_won_opportunities,team_win_rate_percentage,team_total_revenue,team_total_pipeline,round(avg_opportunities_per_member,1) as avg_opportunities_per_member,
 round(avg_wins_per_member,1) as avg_wins_per_member,avg_revenue_per_member,avg_win_rate_per_member,team_total_leads,team_converted_leads,team_lead_conversion_rate,
 team_total_activities,avg_activity_completion_rate,team_revenue_current_quarter,team_deals_current_quarter,revenue_growth_qoq_percentage,team_activities_per_win_ratio,
 top_revenue_performer,top_win_rate_performer,avg_team_tenure_days,new_team_members,veteran_team_members
from final_scores order by team_health_score desc,team_total_revenue desc
```

## gold SQL（仅供定位差异）

S5

```sql
with user_performance as (
    select *
    from intermediate.int_salesforce__user_performance
),

user_dimension as (
    select *
    from marts.dim_salesforce__user
),

revenue_data as (
    select 
        owner_id,
        sum(won_revenue) as total_revenue_won,
        count(*) filter (where is_won = true) as total_deals_won,
        avg(sales_cycle_days) filter (where is_won = true) as avg_sales_cycle,
        sum(won_revenue) filter (where is_current_quarter = true) as revenue_current_quarter,
        sum(won_revenue) filter (where is_previous_quarter = true) as revenue_previous_quarter,
        count(*) filter (where is_won = true and is_current_quarter = true) as deals_won_current_quarter
    from marts.salesforce__revenue_analytics
    group by owner_id
),

team_aggregation as (
    select 
        coalesce(ud.manager_id, 'No Manager') as team_manager_id,
        coalesce(ud.manager_name, 'No Manager') as team_manager_name,
        ud.user_type as team_type,
        
        -- Team size and composition
        count(distinct ud.user_id) as team_size,
        count(distinct ud.user_id) filter (where ud.is_active = true) as active_team_members,
        
        -- Performance distribution
        count(distinct ud.user_id) filter (where up.performance_tier = 'High Performer') as high_performers,
        count(distinct ud.user_id) filter (where up.performance_tier = 'Good Performer') as good_performers,
        count(distinct ud.user_id) filter (where up.performance_tier = 'Developing') as developing_performers,
        count(distinct ud.user_id) filter (where up.performance_tier = 'New User') as new_users,
        
        -- Team productivity metrics
        sum(up.total_opportunities) as team_total_opportunities,
        sum(up.won_opportunities) as team_won_opportunities,
        sum(up.total_won_amount) as team_total_revenue,
        sum(up.total_pipeline_amount) as team_total_pipeline,
        
        -- Team win rate
        case 
            when sum(up.total_opportunities) > 0 
            then round(sum(up.won_opportunities) * 100.0 / sum(up.total_opportunities), 2)
            else 0
        end as team_win_rate_percentage,
        
        -- Average metrics per team member
        round(avg(up.total_opportunities), 1) as avg_opportunities_per_member,
        round(avg(up.won_opportunities), 1) as avg_wins_per_member,
        round(avg(up.total_won_amount), 0) as avg_revenue_per_member,
        round(avg(up.win_rate_percentage), 2) as avg_win_rate_per_member,
        
        -- Lead metrics
        sum(up.total_leads) as team_total_leads,
        sum(up.converted_leads) as team_converted_leads,
        case 
            when sum(up.total_leads) > 0 
            then round(sum(up.converted_leads) * 100.0 / sum(up.total_leads), 2)
            else 0
        end as team_lead_conversion_rate,
        
        -- Activity metrics
        sum(up.total_activities) as team_total_activities,
        round(avg(up.activity_completion_rate_percentage), 2) as avg_activity_completion_rate,
        
        -- Recent performance (current quarter)
        sum(rd.revenue_current_quarter) as team_revenue_current_quarter,
        sum(rd.deals_won_current_quarter) as team_deals_current_quarter,
        
        -- Quarter-over-quarter growth
        case 
            when sum(rd.revenue_previous_quarter) > 0 
            then round((sum(rd.revenue_current_quarter) - sum(rd.revenue_previous_quarter)) * 100.0 / sum(rd.revenue_previous_quarter), 2)
            else null
        end as revenue_growth_qoq_percentage,
        
        -- Team efficiency metrics
        case 
            when sum(up.total_activities) > 0 and sum(up.won_opportunities) > 0 
            then round(sum(up.total_activities)::decimal / sum(up.won_opportunities), 2)
            else null
        end as team_activities_per_win_ratio,
        
        -- Top performer identification
        (array_agg(ud.full_name order by up.total_won_amount desc nulls last))[1] as top_revenue_performer,
        (array_agg(ud.full_name order by up.win_rate_percentage desc nulls last))[1] as top_win_rate_performer,
        
        -- Team tenure analysis
        round(avg(ud.user_tenure_days), 0) as avg_team_tenure_days,
        count(distinct ud.user_id) filter (where ud.user_tenure_category = 'New User') as new_team_members,
        count(distinct ud.user_id) filter (where ud.user_tenure_category = 'Veteran') as veteran_team_members
        
    from user_dimension ud
    left join user_performance up on ud.user_id = up.user_id
    left join revenue_data rd on ud.user_id = rd.owner_id
    where ud.is_active = true
    group by 
        coalesce(ud.manager_id, 'No Manager'),
        coalesce(ud.manager_name, 'No Manager'),
        ud.user_type
),

team_enhanced as (
    select 
        *,
        
        -- Team performance tier
        case 
            when team_win_rate_percentage >= 30 and avg_revenue_per_member >= 100000 and high_performers >= 2 
            then 'High Performing Team'
            when team_win_rate_percentage >= 20 and avg_revenue_per_member >= 50000 and (high_performers + good_performers) >= team_size * 0.5 
            then 'Good Performing Team'
            when team_win_rate_percentage >= 10 and avg_revenue_per_member >= 25000 
            then 'Developing Team'
            else 'Needs Improvement'
        end as team_performance_tier,
        
        -- Team health score (0-100)
        least(100, greatest(0, 
            (case when team_win_rate_percentage >= 25 then 25 else team_win_rate_percentage end) +
            (case when high_performers::decimal / nullif(team_size, 0) >= 0.3 then 25 
                  when high_performers::decimal / nullif(team_size, 0) >= 0.1 then 15 
                  else 5 end) +
            (case when avg_activity_completion_rate >= 80 then 20 
                  when avg_activity_completion_rate >= 60 then 15 
                  else 10 end) +
            (case when revenue_growth_qoq_percentage > 10 then 20 
                  when revenue_growth_qoq_percentage > 0 then 15 
                  when revenue_growth_qoq_percentage >= -10 then 10 
                  else 5 end) +
            (case when team_lead_conversion_rate >= 20 then 10 
                  when team_lead_conversion_rate >= 10 then 7 
                  else 3 end)
        )) as team_health_score,
        
        -- Team diversity index (based on performance distribution)
        case 
            when team_size >= 5 and high_performers > 0 and good_performers > 0 and developing_performers > 0 
            then 'High Diversity'
            when team_size >= 3 and (high_performers > 0 or good_performers > 0) and developing_performers > 0 
            then 'Medium Diversity'
            when team_size >= 2 
            then 'Low Diversity'
            else 'Single Member'
        end as team_diversity_level
        
    from team_aggregation
)

select 
    team_manager_id,
    team_manager_name,
    team_type,
    team_size,
    active_team_members,
    high_performers,
    good_performers,
    developing_performers,
    new_users,
    team_performance_tier,
    team_health_score,
    team_diversity_level,
    team_total_opportunities,
    team_won_opportunities,
    team_win_rate_percentage,
    team_total_revenue,
    team_total_pipeline,
    avg_opportunities_per_member,
    avg_wins_per_member,
    avg_revenue_per_member,
    avg_win_rate_per_member,
    team_total_leads,
    team_converted_leads,
    team_lead_conversion_rate,
    team_total_activities,
    avg_activity_completion_rate,
    team_revenue_current_quarter,
    team_deals_current_quarter,
    revenue_growth_qoq_percentage,
    team_activities_per_win_ratio,
    top_revenue_performer,
    top_win_rate_performer,
    avg_team_tenure_days,
    new_team_members,
    veteran_team_members
from team_enhanced
order by team_health_score desc, team_total_revenue desc
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 496 | 496 | 0 | 0 | 117 | 117 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"team_manager_id":"0050bcasg70kkv4"}</code> |
| K2 | <code>{"team_manager_id":"0050pkwbm2fyly7"}</code> |
| K3 | <code>{"team_manager_id":"00512egkubuvnxv"}</code> |
| K4 | <code>{"team_manager_id":"0051awrquzwdwip"}</code> |
| K5 | <code>{"team_manager_id":"005i5srjh3yvvjc"}</code> |
| K6 | <code>{"team_manager_id":"005u8tbnetri3mw"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| team_manager_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| team_manager_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| team_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| team_size | 0 | 0 | 0 | BIGINT | BIGINT |
| active_team_members | 0 | 0 | 0 | BIGINT | BIGINT |
| high_performers | 0 | 0 | 0 | BIGINT | BIGINT |
| good_performers | 0 | 0 | 0 | BIGINT | BIGINT |
| developing_performers | 0 | 0 | 0 | BIGINT | BIGINT |
| new_users | 0 | 0 | 0 | BIGINT | BIGINT |
| team_performance_tier | 0 | 0 | 0 | VARCHAR | VARCHAR |
| team_health_score | 496 | 496 | 496 | DOUBLE | DOUBLE |
| team_diversity_level | 0 | 0 | 0 | VARCHAR | VARCHAR |
| team_total_opportunities | 0 | 0 | 0 | HUGEINT | HUGEINT |
| team_won_opportunities | 0 | 0 | 0 | HUGEINT | HUGEINT |
| team_win_rate_percentage | 0 | 0 | 0 | DOUBLE | DOUBLE |
| team_total_revenue | 272 | 272 | 272 | DECIMAL(38,2) | DECIMAL(38,2) |
| team_total_pipeline | 0 | 0 | 0 | DECIMAL(38,2) | DECIMAL(38,2) |
| avg_opportunities_per_member | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_wins_per_member | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_revenue_per_member | 292 | 292 | 292 | DOUBLE | DOUBLE |
| avg_win_rate_per_member | 0 | 0 | 0 | DOUBLE | DOUBLE |
| team_total_leads | 0 | 0 | 0 | HUGEINT | HUGEINT |
| team_converted_leads | 0 | 0 | 0 | HUGEINT | HUGEINT |
| team_lead_conversion_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| team_total_activities | 0 | 0 | 0 | HUGEINT | HUGEINT |
| avg_activity_completion_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| team_revenue_current_quarter | 0 | 0 | 0 | DECIMAL(38,2) | DECIMAL(38,2) |
| team_deals_current_quarter | 0 | 0 | 0 | HUGEINT | HUGEINT |
| revenue_growth_qoq_percentage | 0 | 0 | 0 | DOUBLE | DOUBLE |
| team_activities_per_win_ratio | 0 | 0 | 0 | DOUBLE | DOUBLE |
| top_revenue_performer | 272 | 272 | 272 | VARCHAR | VARCHAR |
| top_win_rate_performer | 2 | 2 | 2 | VARCHAR | VARCHAR |
| new_team_members | 0 | 0 | 0 | BIGINT | BIGINT |
| veteran_team_members | 0 | 0 | 0 | BIGINT | BIGINT |

team_health_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"28.0","rows":2}]</code> | <code>[{"value":"23.0","rows":2}]</code> |
| K2 | <code>[{"value":"28.0","rows":1},{"value":"35.0","rows":1},{"value":"53.0","rows":1}]</code> | <code>[{"value":"23.0","rows":1},{"value":"30.0","rows":1},{"value":"48.0","rows":1}]</code> |
| K3 | 35.0 | 30.0 |
重复键为同键值/次数，列表位置不是唯一配对。

team_total_revenue 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1},{"value":"0.00","rows":1}]</code> | <code>[{"value":"0.00","rows":2}]</code> |
| K2 | <code>[{"value":null,"rows":1},{"value":"0.00","rows":1},{"value":"1327105.00","rows":1}]</code> | <code>[{"value":"0.00","rows":2},{"value":"1327105.00","rows":1}]</code> |
| K4 | <code>[{"value":null,"rows":1},{"value":"1984792.00","rows":1}]</code> | <code>[{"value":"0.00","rows":1},{"value":"1984792.00","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

avg_revenue_per_member 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1},{"value":"0.0","rows":1}]</code> | <code>[{"value":"0.0","rows":2}]</code> |
| K2 | <code>[{"value":null,"rows":1},{"value":"0.0","rows":1},{"value":"1327105.0","rows":1}]</code> | <code>[{"value":"0.0","rows":2},{"value":"1327105.0","rows":1}]</code> |
| K4 | <code>[{"value":null,"rows":1},{"value":"1984792.0","rows":1}]</code> | <code>[{"value":"0.0","rows":1},{"value":"1984792.0","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

top_revenue_performer 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":1},{"value":"Justin Rojas","rows":1}]</code> | <code>[{"value":"Justin Rojas","rows":1},{"value":"Vincent Davies","rows":1}]</code> |
| K2 | <code>[{"value":null,"rows":1},{"value":"Dwayne Chambers","rows":1},{"value":"Whitney Yoder","rows":1}]</code> | <code>[{"value":"Dwayne Chambers","rows":1},{"value":"Timothy Peterson","rows":1},{"value":"Whitney Yoder","rows":1}]</code> |
| K4 | <code>[{"value":null,"rows":1},{"value":"Jacob Haynes","rows":1}]</code> | <code>[{"value":"Brandon Munoz","rows":1},{"value":"Jacob Haynes","rows":1}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

top_win_rate_performer 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K5 | <code>[{"value":"Austin Deleon","rows":1},{"value":"Dawn Bailey","rows":1},{"value":"Katie Castillo","rows":1}]</code> | <code>[{"value":"Austin Deleon","rows":1},{"value":"Katie Castillo","rows":1},{"value":"Tony Lewis","rows":1}]</code> |
| K6 | <code>[{"value":"Amy Long","rows":1},{"value":"Christine Morrison","rows":1},{"value":"Robert Rodgers","rows":1}]</code> | <code>[{"value":"Amy Long","rows":1},{"value":"Heidi Turner","rows":1},{"value":"Robert Rodgers","rows":1}]</code> |
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
| A2_all_null_column | <code>3列；[{"column":"team_revenue_current_quarter","table_rows":479},{"column":"revenue_growth_qoq_percentage","table_rows":479},{"column":"team_activities_per_win_ratio","table_rows":479}]</code> |
| A3_constant_nonnull_column | <code>6列；[{"column":"high_performers","value":"0"},{"column":"good_performers","value":"0"},{"column":"team_total_activities","value":"0"}]</code> |
| A4_equal_columns | <code>2组；[{"columns":["team_size","active_team_members"],"nonnull_equal_rows":479,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["high_performers","good_performers","team_total_activities","new_team_members","veteran_team_members"],"nonnull_equal_rows":479,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>2组；[{"columns":["team_size","active_team_members"],"nonnull_equal_rows":479,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["high_performers","good_performers","team_total_activities","new_team_members","veteran_team_members"],"nonnull_equal_rows":479,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |

## 轨迹索引（不放输出原文）

本题事件总数：101；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; sed -n '1,220p' run.py</code> | 11932 | true | false |
| 23 | run | <code>cat &gt; sql/intermediate/int_salesforce__lead_conversion_funnel.sql &lt;&lt;'SQL'<br>with lead_base as (<br>    select * from staging.stg_salesforce__lead where not coalesce(is_deleted, false)<br>),<br>scored as (<br>    se</code> | 0 | false | false |
| 29 | run | <code>cat &gt; sql/marts/dim_salesforce__user.sql &lt;&lt;'SQL'<br>with user_base as (<br> select u.*,ur.user_role_name,ur.developer_name,ur.parent_role_id,ur.rollup_description,<br> m.user_id as matched_manager_id,m.first_n</code> | 0 | false | false |
| 33 | run | <code>cat &gt; sql/marts/salesforce__revenue_analytics.sql &lt;&lt;'SQL'<br>with closed_opportunities as (<br> select * from intermediate.int_salesforce__opportunity_pipeline where is_closed is true<br>),<br>enriched as (<br> sele</code> | 0 | false | false |
| 43 | run | <code>tail -180 /tmp/run2.log; grep -E '✗&#124;ERROR&#124;layer complete' /tmp/run2.log</code> | 15611 | true | false |
| 49 | run | <code>for f in sql/staging/*.sql; do echo ==== $f; grep -E 'md5&#124;history_unique_key&#124;created_date as&#124;last_modified_date' $f; done; python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('salesforce.duckdb',read_only=</code> | 14873 | true | false |
| 51 | run | <code>python - &lt;&lt;'PY'<br>import yaml,duckdb<br>x=yaml.safe_load(open('docs/data_contract.yaml'))['modeling_spec']; c=duckdb.connect('salesforce.duckdb',read_only=True)<br>for layer,sch in [('intermediate_models','in</code> | 1355 | true | false |
| 57 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br># Correct field source mapping; canonical foreign keys should remain FK columns, not the row's own id.<br>fixes={<br>'stg_salesforce__contact':'id as account_id','st</code> | 3263 | true | false |

### agent action 的 thought/message 命中原句

event 33 / message

```text
cat > sql/marts/salesforce__team_performance.sql <<'SQL'
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-018.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/marts/salesforce__team_performance.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/sql/marts/salesforce__team_performance.sql`
- S6: `records/006_contract_impl-018.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/.tmp/result.md`
- S10: `data/023_packages_work/023_impl-018_salesforce__team_performance/023_impl-018_salesforce__team_performance.json`
- S11: `data/005_cs_work/impl-018_parallel/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/salesforce.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions`
