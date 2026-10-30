# impl-018 · salesforce__team_performance

用途：**全量**；层：`marts`；状态：待标注；手册：v2 冻结版。

## 结论

主要原因：**C**；把握：中；主要错误点：health_growth_null。

增长率 NULL 经 COALESCE 成0后多给5分，是行数口径最大主因；收入来源另有差异。

参与因素：A：revenue_sum（行减少0，格减少272）；A：revenue_avg（行减少0，格减少292）；C：revenue_top（行减少0，格减少270）。

标记：无。

top_win_rate_performer 的2个名称差异是契约允许的并列任意选择，023_team_ties 已确认4个候选均为组内最大0；作为剩余O诊断记录，未有单独减少规模干预，不计参与因素。

## 材料与比较口径

精简材料包：[023_impl-018_salesforce__team_performance.md](../023_packages/023_impl-018_salesforce__team_performance.md)。原始 SQL、契约摘录见下文。

判错沿用官方状态；比较列为原评测列与评测键的并集，不能把输出列数减少当作匹配。重跑 staging 读取 agent 留存 raw；intermediate/marts 读取 gold 上游（CS）。原件 READ_ONLY，只在 data/023_work 或 data/023_supplement_work 写私有副本。每个干预从自己的未修改基线独立出发，一处代码算一个错误点；时刻替换是共同控制。

重复键先消去相同整行，再在同一键内按行序列配对剩余行；格子计数包含仅一侧行乘以比较列数。使用与前批相同的 L0–L3 归一化和比较器；各档重新比较整表。

## 契约与两边 SQL 原文

契约来源：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-018/docs/data_contract.yaml`；SHA-256 `d25131b0d954e07cbd82bb6c2ee8c425958f33748c62432c60ed5c2f890f2cd2`。
契约行 3278–3391：

```
3278:     - name: salesforce__team_performance
3279:       description: Aggregated Salesforce team metrics by manager and team type for active users, including tiers, health score, and recent performance
3280:       grain: One row per team_manager_id + team_manager_name + team_type
3281:       source_models:
3282:       - intermediate.int_salesforce__user_performance
3283:       - marts.dim_salesforce__user
3284:       - marts.salesforce__revenue_analytics
3285:       business_logic: '- Create user_performance from intermediate.int_salesforce__user_performance and user_dimension from marts.dim_salesforce__user. - From marts.salesforce__revenue_analytics, aggregate per owner_id: total revenue won (sum of won_revenue), deals won (count of rows where won), average sales cycle (average days on won deals), current-quarter won revenue (sum where in current quarter), previous-quarter won revenue (sum where in previous quarter), and current-quarter deals won (count of won deals in current quarter). - Join user_dimension to user_performance on user_id (left join), and to revenue_data on user_id = owner_id (left join). Keep only rows where the user is active, then group by: • team_manager_id = manager_id with nulls replaced by "No Manager" • team_manager_name = manager_name with nulls replaced by "No Manager" • team_type = user_type (can be null) - For each group, compute: • team_size = distinct count of users • active_team_members = distinct count of users where active (equals team_size under the active-user filter) • high_performers, good_performers, developing_performers, new_users = distinct user counts by performance_tier exact match • team_total_opportunities and team_won_opportunities = sums across users • team_total_revenue and team_total_pipeline = sums of revenue and pipeline amounts • team_win_rate_percentage = 100 × (total won opportunities ÷ total opportunities), rounded to two decimals; return 0 if total opportunities is zero or null • avg_opportunities_per_member and avg_wins_per_member = per-user averages, rounded to one decimal; nulls excluded • avg_revenue_per_member = per-user average revenue won, rounded to the nearest whole unit; nulls excluded • avg_win_rate_per_member = per-user average win rate percentage, rounded to two decimals; nulls excluded • team_total_leads and team_converted_leads = sums across users • team_lead_conversion_rate = 100 × (converted leads ÷ total leads), rounded to two decimals; return 0 if total leads is zero or null • team_total_activities = sum across users; avg_activity_completion_rate = per-user average completion rate percentage, rounded to two decimals; nulls excluded • team_revenue_current_quarter and team_deals_current_quarter = sums of current-quarter revenue and deals from revenue_data • revenue_growth_qoq_percentage = 100 × (current-quarter revenue minus previous-quarter revenue) ÷ previous-quarter revenue, rounded to two decimals; null if previous-quarter revenue is zero or null • team_activities_per_win_ratio = total activities ÷ total won opportunities, rounded to two decimals; null unless both totals are greater than zero • top_revenue_performer = the full_name of the member with the highest total won amount; members without a value are ranked last; ties are arbitrary • top_win_rate_performer = the full_name of the member with the highest win rate percentage; members without a value are ranked last; ties are arbitrary • avg_team_tenure_days = average user tenure in days, rounded to the nearest whole day; nulls excluded • new_team_members and veteran_team_members = distinct user counts where user_tenure_category is "New User" or "Veteran" - Enhance with: • team_performance_tier: - High Performing Team: win rate ≥ 30, average revenue per member ≥ 100,000, and at least 2 high performers - Good Performing Team: win rate ≥ 20, average revenue per member ≥ 50,000, and high + good performers cover at least half of the team - Developing Team: win rate ≥ 10 and average revenue per member ≥ 25,000 - Otherwise: Needs Improvement • team_health_score = sum of five components, clipped to the 0–100 range: - Win rate contribution: the win rate capped at 25 - High-performer share: 25 if high performers ÷ team_size ≥ 0.3, else 15 if ≥ 0.1, else 5 (when team_size is 0, this defaults to 5) - Activity completion: 20 if ≥ 80%, else 15 if ≥ 60%, else 10 - Revenue growth: 20 if > 10%, else 15 if > 0%, else 10 if ≥ -10%, else 5 - Lead conversion: 10 if ≥ 20%, else 7 if ≥ 10%, else 3 • team_diversity_level: - High Diversity: team_size ≥ 5 and at least one high, one good, and one developing performer - Medium Diversity: team_size ≥ 3 and at least one high or good performer and at least one developing performer - Low Diversity: team_size ≥ 2 - Otherwise: Single Member - Output all fields from the enhanced dataset; final ordering is by team_health_score descending, then team_total_revenue descending.'
3286:       columns:
3287:       - name: team_manager_id
3288:         data_type: VARCHAR
3289:         description: Manager identifier for the team with nulls replaced by 'No Manager'.
3290:       - name: team_manager_name
3291:         data_type: VARCHAR
3292:         description: Manager full name with nulls replaced by 'No Manager'.
3293:       - name: team_type
3294:         data_type: VARCHAR
3295:         description: Team type from user_type; can be null and is part of the grouping.
3296:       - name: team_size
3297:         data_type: BIGINT
3298:         description: Distinct count of active users in the team after filtering to active users.
3299:       - name: active_team_members
3300:         data_type: BIGINT
3301:         description: Distinct count of active users; equals team_size under the active-user filter.
3302:       - name: high_performers
3303:         data_type: BIGINT
3304:         description: Distinct user count with performance_tier equal to 'High Performer'.
3305:       - name: good_performers
3306:         data_type: BIGINT
3307:         description: Distinct user count with performance_tier equal to 'Good Performer'.
3308:       - name: developing_performers
3309:         data_type: BIGINT
3310:         description: Distinct user count with performance_tier equal to 'Developing'.
3311:       - name: new_users
3312:         data_type: BIGINT
3313:         description: Distinct user count with performance_tier equal to 'New User'.
3314:       - name: team_performance_tier
3315:         data_type: VARCHAR
3316:         description: Team tier based on win rate, average revenue per member, and performer mix thresholds.
3317:       - name: team_health_score
3318:         data_type: DOUBLE
3319:         description: Composite score from five components capped between 0 and 100.
3320:       - name: team_diversity_level
3321:         data_type: VARCHAR
3322:         description: Diversity category based on team size and presence across performance tiers.
3323:       - name: team_total_opportunities
3324:         data_type: HUGEINT
3325:         description: Total opportunities summed across team; nulls ignored and result is null if all inputs are null.
3326:       - name: team_won_opportunities
3327:         data_type: HUGEINT
3328:         description: Total won opportunities summed across team; nulls ignored and result is null if all inputs are null.
3329:       - name: team_win_rate_percentage
3330:         data_type: DOUBLE
3331:         description: Win rate as 100 × won opportunities ÷ total opportunities, rounded to two decimals; returns 0 if total opportunities is zero or null.
3332:       - name: team_total_revenue
3333:         data_type: DECIMAL(38,2)
3334:         description: Total revenue won summed across team; currency formatted to two decimals; nulls ignored and result is null if all inputs are null.
3335:       - name: team_total_pipeline
3336:         data_type: DECIMAL(38,2)
3337:         description: Total pipeline amount summed across team; currency formatted to two decimals; nulls ignored and result is null if all inputs are null.
3338:       - name: avg_opportunities_per_member
3339:         data_type: DOUBLE
3340:         description: Average opportunities per user rounded to one decimal; excludes nulls and is null if no values.
3341:       - name: avg_wins_per_member
3342:         data_type: DOUBLE
3343:         description: Average won opportunities per user rounded to one decimal; excludes nulls and is null if no values.
3344:       - name: avg_revenue_per_member
3345:         data_type: DOUBLE
3346:         description: Average revenue won per user rounded to the nearest whole unit; excludes nulls and is null if no values.
3347:       - name: avg_win_rate_per_member
3348:         data_type: DOUBLE
3349:         description: Average user win rate percentage rounded to two decimals; excludes nulls and is null if no values.
3350:       - name: team_total_leads
3351:         data_type: HUGEINT
3352:         description: Total leads summed across team; nulls ignored and result is null if all inputs are null.
3353:       - name: team_converted_leads
3354:         data_type: HUGEINT
3355:         description: Total converted leads summed across team; nulls ignored and result is null if all inputs are null.
3356:       - name: team_lead_conversion_rate
3357:         data_type: DOUBLE
3358:         description: Lead conversion as 100 × converted ÷ total leads, rounded to two decimals; returns 0 if total leads is zero or null.
3359:       - name: team_total_activities
3360:         data_type: HUGEINT
3361:         description: Total activities summed across team; nulls ignored and result is null if all inputs are null.
3362:       - name: avg_activity_completion_rate
3363:         data_type: DOUBLE
3364:         description: Average activity completion rate percentage rounded to two decimals; excludes nulls and is null if no values.
3365:       - name: team_revenue_current_quarter
3366:         data_type: DECIMAL(38,2)
3367:         description: Total current-quarter revenue won summed across team; currency with two decimals; nulls ignored and result is null if all inputs are null.
3368:       - name: team_deals_current_quarter
3369:         data_type: HUGEINT
3370:         description: Total current-quarter deals won summed across team; nulls ignored and result is null if all inputs are null.
3371:       - name: revenue_growth_qoq_percentage
3372:         data_type: DOUBLE
3373:         description: Quarter-over-quarter revenue growth percentage rounded to two decimals; null when previous-quarter revenue is zero or null.
3374:       - name: team_activities_per_win_ratio
3375:         data_type: DOUBLE
3376:         description: Total activities divided by total won opportunities, rounded to two decimals; null unless both totals are greater than zero.
3377:       - name: top_revenue_performer
3378:         data_type: VARCHAR
3379:         description: Full name of the member with the highest total won amount; nulls ranked last and ties are arbitrary.
3380:       - name: top_win_rate_performer
3381:         data_type: VARCHAR
3382:         description: Full name of the member with the highest win rate percentage; nulls ranked last and ties are arbitrary.
3383:       - name: avg_team_tenure_days
3384:         data_type: DOUBLE
3385:         description: Average user tenure in days rounded to the nearest whole day; excludes nulls and is null if no values.
3386:       - name: new_team_members
3387:         data_type: BIGINT
3388:         description: Distinct user count where user_tenure_category is 'New User'.
3389:       - name: veteran_team_members
3390:         data_type: BIGINT
3391:         description: Distinct user count where user_tenure_category is 'Veteran'.
```

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-018/agent/dacomp-de-impl-018/sql/marts/salesforce__team_performance.sql`，SHA-256 `f0fcb6526b209972c74c557815cdae25a35354208eae21ea4c0cf1b09a1336e9`，行 1–75。

```
1: with revenue_by_owner as (
2:  select owner_id,sum(won_revenue) as total_revenue_won,
3:  count(*) filter(where is_won is true) as deals_won,
4:  avg(sales_cycle_days) filter(where is_won is true) as avg_sales_cycle_days,
5:  sum(won_revenue) filter(where is_current_quarter) as revenue_current_quarter,
6:  sum(won_revenue) filter(where is_previous_quarter) as revenue_previous_quarter,
7:  count(*) filter(where is_won is true and is_current_quarter) as deals_current_quarter
8:  from marts.salesforce__revenue_analytics group by owner_id
9: ),
10: member_metrics as (
11:  select d.user_id,d.full_name,d.manager_id,d.manager_name,d.user_type,d.is_active,d.performance_tier,d.user_tenure_days,d.user_tenure_category,
12:  p.total_opportunities,p.won_opportunities,p.total_won_amount,p.total_pipeline_amount,p.win_rate_percentage,p.total_leads,p.converted_leads,
13:  p.total_activities,p.activity_completion_rate_percentage,r.total_revenue_won,r.deals_won,r.avg_sales_cycle_days,r.revenue_current_quarter,r.revenue_previous_quarter,r.deals_current_quarter
14:  from marts.dim_salesforce__user d
15:  left join intermediate.int_salesforce__user_performance p on d.user_id=p.user_id
16:  left join revenue_by_owner r on d.user_id=r.owner_id
17:  where d.is_active=true
18: ),
19: team_rollup as (
20:  select coalesce(manager_id,'No Manager') as team_manager_id,coalesce(manager_name,'No Manager') as team_manager_name,user_type as team_type,
21:  count(distinct user_id) as team_size,count(distinct user_id) filter(where is_active) as active_team_members,
22:  count(distinct user_id) filter(where performance_tier='High Performer') as high_performers,
23:  count(distinct user_id) filter(where performance_tier='Good Performer') as good_performers,
24:  count(distinct user_id) filter(where performance_tier='Developing') as developing_performers,
25:  count(distinct user_id) filter(where performance_tier='New User') as new_users,
26:  sum(total_opportunities) as team_total_opportunities,sum(won_opportunities) as team_won_opportunities,
27:  sum(total_revenue_won) as team_total_revenue,sum(total_pipeline_amount) as team_total_pipeline,
28:  avg(total_opportunities) as avg_opportunities_per_member,avg(won_opportunities) as avg_wins_per_member,
29:  round(avg(total_revenue_won)) as avg_revenue_per_member,round(avg(win_rate_percentage),2) as avg_win_rate_per_member,
30:  sum(total_leads) as team_total_leads,sum(converted_leads) as team_converted_leads,sum(total_activities) as team_total_activities,
31:  round(avg(activity_completion_rate_percentage),2) as avg_activity_completion_rate,
32:  sum(revenue_current_quarter) as team_revenue_current_quarter,sum(deals_current_quarter) as team_deals_current_quarter,
33:  sum(revenue_previous_quarter) as team_revenue_previous_quarter,
34:  case when sum(team_total_opportunities) over(partition by coalesce(manager_id,'No Manager'),coalesce(manager_name,'No Manager'),user_type)>0 then 0 end as unused_placeholder,
35:  round(avg(user_tenure_days)) as avg_team_tenure_days,
36:  count(distinct user_id) filter(where user_tenure_category='New User') as new_team_members,
37:  count(distinct user_id) filter(where user_tenure_category='Veteran') as veteran_team_members
38:  from member_metrics group by manager_id,manager_name,user_type
39: ),
40: performer_names as (
41:  select coalesce(manager_id,'No Manager') as team_manager_id,coalesce(manager_name,'No Manager') as team_manager_name,user_type as team_type,
42:  arg_max(full_name,total_revenue_won) filter(where total_revenue_won is not null) as top_revenue_performer,
43:  arg_max(full_name,win_rate_percentage) filter(where win_rate_percentage is not null) as top_win_rate_performer
44:  from member_metrics group by manager_id,manager_name,user_type
45: ),
46: scored as (
47:  select t.*,pn.top_revenue_performer,pn.top_win_rate_performer,
48:  case when team_total_opportunities>0 then round(team_won_opportunities::double/team_total_opportunities*100,2) else 0.0 end as team_win_rate_percentage,
49:  case when team_total_leads>0 then round(team_converted_leads::double/team_total_leads*100,2) else 0.0 end as team_lead_conversion_rate,
50:  case when team_revenue_previous_quarter>0 then round((team_revenue_current_quarter-team_revenue_previous_quarter)::double/team_revenue_previous_quarter*100,2) end as revenue_growth_qoq_percentage,
51:  case when team_total_activities>0 and team_won_opportunities>0 then round(team_total_activities::double/team_won_opportunities,2) end as team_activities_per_win_ratio
52:  from team_rollup t left join performer_names pn using(team_manager_id,team_manager_name,team_type)
53: ),
54: final_scores as (
55:  select *,least(100.0,greatest(0.0,
56:  least(team_win_rate_percentage,25)
57:  + case when team_size>0 and high_performers::double/team_size>=0.3 then 25 when team_size>0 and high_performers::double/team_size>=0.1 then 15 else 5 end
58:  + case when coalesce(avg_activity_completion_rate,0)>=80 then 20 when coalesce(avg_activity_completion_rate,0)>=60 then 15 else 10 end
59:  + case when coalesce(revenue_growth_qoq_percentage,0)>10 then 20 when coalesce(revenue_growth_qoq_percentage,0)>0 then 15 when coalesce(revenue_growth_qoq_percentage,0)>=-10 then 10 else 5 end
60:  + case when coalesce(team_lead_conversion_rate,0)>=20 then 10 when coalesce(team_lead_conversion_rate,0)>=10 then 7 else 3 end))::double as team_health_score
61:  from scored
62: )
63: select team_manager_id,team_manager_name,team_type,team_size,active_team_members,high_performers,good_performers,developing_performers,new_users,
64:  case when team_win_rate_percentage>=30 and avg_revenue_per_member>=100000 and high_performers>=2 then 'High Performing Team'
65:  when team_win_rate_percentage>=20 and avg_revenue_per_member>=50000 and high_performers+good_performers>=team_size/2.0 then 'Good Performing Team'
66:  when team_win_rate_percentage>=10 and avg_revenue_per_member>=25000 then 'Developing Team' else 'Needs Improvement' end as team_performance_tier,
67:  team_health_score,
68:  case when team_size>=5 and high_performers>=1 and good_performers>=1 and developing_performers>=1 then 'High Diversity'
69:  when team_size>=3 and (high_performers>=1 or good_performers>=1) and developing_performers>=1 then 'Medium Diversity'
70:  when team_size>=2 then 'Low Diversity' else 'Single Member' end as team_diversity_level,
71:  team_total_opportunities,team_won_opportunities,team_win_rate_percentage,team_total_revenue,team_total_pipeline,round(avg_opportunities_per_member,1) as avg_opportunities_per_member,
72:  round(avg_wins_per_member,1) as avg_wins_per_member,avg_revenue_per_member,avg_win_rate_per_member,team_total_leads,team_converted_leads,team_lead_conversion_rate,
73:  team_total_activities,avg_activity_completion_rate,team_revenue_current_quarter,team_deals_current_quarter,revenue_growth_qoq_percentage,team_activities_per_win_ratio,
74:  top_revenue_performer,top_win_rate_performer,avg_team_tenure_days,new_team_members,veteran_team_members
75: from final_scores order by team_health_score desc,team_total_revenue desc
```

gold（只用于诊断，不作为未写明业务规则的规范）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/sql/marts/salesforce__team_performance.sql`，SHA-256 `2a9d366fbde29ab612a45e58594c3bf1d8a839d43af5cf27e481ceb23bec3b16`，行 1–193。

```
1: with user_performance as (
2:     select *
3:     from intermediate.int_salesforce__user_performance
4: ),
5: 
6: user_dimension as (
7:     select *
8:     from marts.dim_salesforce__user
9: ),
10: 
11: revenue_data as (
12:     select 
13:         owner_id,
14:         sum(won_revenue) as total_revenue_won,
15:         count(*) filter (where is_won = true) as total_deals_won,
16:         avg(sales_cycle_days) filter (where is_won = true) as avg_sales_cycle,
17:         sum(won_revenue) filter (where is_current_quarter = true) as revenue_current_quarter,
18:         sum(won_revenue) filter (where is_previous_quarter = true) as revenue_previous_quarter,
19:         count(*) filter (where is_won = true and is_current_quarter = true) as deals_won_current_quarter
20:     from marts.salesforce__revenue_analytics
21:     group by owner_id
22: ),
23: 
24: team_aggregation as (
25:     select 
26:         coalesce(ud.manager_id, 'No Manager') as team_manager_id,
27:         coalesce(ud.manager_name, 'No Manager') as team_manager_name,
28:         ud.user_type as team_type,
29:         
30:         -- Team size and composition
31:         count(distinct ud.user_id) as team_size,
32:         count(distinct ud.user_id) filter (where ud.is_active = true) as active_team_members,
33:         
34:         -- Performance distribution
35:         count(distinct ud.user_id) filter (where up.performance_tier = 'High Performer') as high_performers,
36:         count(distinct ud.user_id) filter (where up.performance_tier = 'Good Performer') as good_performers,
37:         count(distinct ud.user_id) filter (where up.performance_tier = 'Developing') as developing_performers,
38:         count(distinct ud.user_id) filter (where up.performance_tier = 'New User') as new_users,
39:         
40:         -- Team productivity metrics
41:         sum(up.total_opportunities) as team_total_opportunities,
42:         sum(up.won_opportunities) as team_won_opportunities,
43:         sum(up.total_won_amount) as team_total_revenue,
44:         sum(up.total_pipeline_amount) as team_total_pipeline,
45:         
46:         -- Team win rate
47:         case 
48:             when sum(up.total_opportunities) > 0 
49:             then round(sum(up.won_opportunities) * 100.0 / sum(up.total_opportunities), 2)
50:             else 0
51:         end as team_win_rate_percentage,
52:         
53:         -- Average metrics per team member
54:         round(avg(up.total_opportunities), 1) as avg_opportunities_per_member,
55:         round(avg(up.won_opportunities), 1) as avg_wins_per_member,
56:         round(avg(up.total_won_amount), 0) as avg_revenue_per_member,
57:         round(avg(up.win_rate_percentage), 2) as avg_win_rate_per_member,
58:         
59:         -- Lead metrics
60:         sum(up.total_leads) as team_total_leads,
61:         sum(up.converted_leads) as team_converted_leads,
62:         case 
63:             when sum(up.total_leads) > 0 
64:             then round(sum(up.converted_leads) * 100.0 / sum(up.total_leads), 2)
65:             else 0
66:         end as team_lead_conversion_rate,
67:         
68:         -- Activity metrics
69:         sum(up.total_activities) as team_total_activities,
70:         round(avg(up.activity_completion_rate_percentage), 2) as avg_activity_completion_rate,
71:         
72:         -- Recent performance (current quarter)
73:         sum(rd.revenue_current_quarter) as team_revenue_current_quarter,
74:         sum(rd.deals_won_current_quarter) as team_deals_current_quarter,
75:         
76:         -- Quarter-over-quarter growth
77:         case 
78:             when sum(rd.revenue_previous_quarter) > 0 
79:             then round((sum(rd.revenue_current_quarter) - sum(rd.revenue_previous_quarter)) * 100.0 / sum(rd.revenue_previous_quarter), 2)
80:             else null
81:         end as revenue_growth_qoq_percentage,
82:         
83:         -- Team efficiency metrics
84:         case 
85:             when sum(up.total_activities) > 0 and sum(up.won_opportunities) > 0 
86:             then round(sum(up.total_activities)::decimal / sum(up.won_opportunities), 2)
87:             else null
88:         end as team_activities_per_win_ratio,
89:         
90:         -- Top performer identification
91:         (array_agg(ud.full_name order by up.total_won_amount desc nulls last))[1] as top_revenue_performer,
92:         (array_agg(ud.full_name order by up.win_rate_percentage desc nulls last))[1] as top_win_rate_performer,
93:         
94:         -- Team tenure analysis
95:         round(avg(ud.user_tenure_days), 0) as avg_team_tenure_days,
96:         count(distinct ud.user_id) filter (where ud.user_tenure_category = 'New User') as new_team_members,
97:         count(distinct ud.user_id) filter (where ud.user_tenure_category = 'Veteran') as veteran_team_members
98:         
99:     from user_dimension ud
100:     left join user_performance up on ud.user_id = up.user_id
101:     left join revenue_data rd on ud.user_id = rd.owner_id
102:     where ud.is_active = true
103:     group by 
104:         coalesce(ud.manager_id, 'No Manager'),
105:         coalesce(ud.manager_name, 'No Manager'),
106:         ud.user_type
107: ),
108: 
109: team_enhanced as (
110:     select 
111:         *,
112:         
113:         -- Team performance tier
114:         case 
115:             when team_win_rate_percentage >= 30 and avg_revenue_per_member >= 100000 and high_performers >= 2 
116:             then 'High Performing Team'
117:             when team_win_rate_percentage >= 20 and avg_revenue_per_member >= 50000 and (high_performers + good_performers) >= team_size * 0.5 
118:             then 'Good Performing Team'
119:             when team_win_rate_percentage >= 10 and avg_revenue_per_member >= 25000 
120:             then 'Developing Team'
121:             else 'Needs Improvement'
122:         end as team_performance_tier,
123:         
124:         -- Team health score (0-100)
125:         least(100, greatest(0, 
126:             (case when team_win_rate_percentage >= 25 then 25 else team_win_rate_percentage end) +
127:             (case when high_performers::decimal / nullif(team_size, 0) >= 0.3 then 25 
128:                   when high_performers::decimal / nullif(team_size, 0) >= 0.1 then 15 
129:                   else 5 end) +
130:             (case when avg_activity_completion_rate >= 80 then 20 
131:                   when avg_activity_completion_rate >= 60 then 15 
132:                   else 10 end) +
133:             (case when revenue_growth_qoq_percentage > 10 then 20 
134:                   when revenue_growth_qoq_percentage > 0 then 15 
135:                   when revenue_growth_qoq_percentage >= -10 then 10 
136:                   else 5 end) +
137:             (case when team_lead_conversion_rate >= 20 then 10 
138:                   when team_lead_conversion_rate >= 10 then 7 
139:                   else 3 end)
140:         )) as team_health_score,
141:         
142:         -- Team diversity index (based on performance distribution)
143:         case 
144:             when team_size >= 5 and high_performers > 0 and good_performers > 0 and developing_performers > 0 
145:             then 'High Diversity'
146:             when team_size >= 3 and (high_performers > 0 or good_performers > 0) and developing_performers > 0 
147:             then 'Medium Diversity'
148:             when team_size >= 2 
149:             then 'Low Diversity'
150:             else 'Single Member'
151:         end as team_diversity_level
152:         
153:     from team_aggregation
154: )
155: 
156: select 
157:     team_manager_id,
158:     team_manager_name,
159:     team_type,
160:     team_size,
161:     active_team_members,
162:     high_performers,
163:     good_performers,
164:     developing_performers,
165:     new_users,
166:     team_performance_tier,
167:     team_health_score,
168:     team_diversity_level,
169:     team_total_opportunities,
170:     team_won_opportunities,
171:     team_win_rate_percentage,
172:     team_total_revenue,
173:     team_total_pipeline,
174:     avg_opportunities_per_member,
175:     avg_wins_per_member,
176:     avg_revenue_per_member,
177:     avg_win_rate_per_member,
178:     team_total_leads,
179:     team_converted_leads,
180:     team_lead_conversion_rate,
181:     team_total_activities,
182:     avg_activity_completion_rate,
183:     team_revenue_current_quarter,
184:     team_deals_current_quarter,
185:     revenue_growth_qoq_percentage,
186:     team_activities_per_win_ratio,
187:     top_revenue_performer,
188:     top_win_rate_performer,
189:     avg_team_tenure_days,
190:     new_team_members,
191:     veteran_team_members
192: from team_enhanced
193: order by team_health_score desc, team_total_revenue desc
```

## 轨迹可见性与不确定性

**四档：看到了但没提**。

event 1 已给增长率分支；event 33 生成模型；event 99 未讨论 NULL 增长率评分。

工作清单、已实现功能列表和验证通过列表本身不算通用策略。上述证据只针对本表主要差异。事件索引及 action 原文：[023_trace_audit.json](../023_trace_audit.json)。

- event 1：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/1.json`。
- event 33：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/33.json`。
- event 99：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-018/agent/.events/sessions/0f843e69-f2eb-45-6b806c23080a1dd/events/99.json`。
## 查询

核实查询 **0** 条；核实代价档：**需要查业务说明**。诊断查询不计入 5 条上限。

未追加 agent 可见数据核实；判断依据为契约、SQL 和明确标为诊断的查询，不用 gold 结果证明 U。

### 诊断：增长率 NULL

只读数据库：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/salesforce.duckdb`。

```sql
SELECT count(*) n,count(*) FILTER(WHERE revenue_growth_qoq_percentage IS NULL) null_growth FROM marts.salesforce__team_performance
```


```json
{"columns":["n","null_growth"],"rows":[[496,496]]}
```


### 诊断：补充差异定位


```sql
SELECT a.team_manager_id,a.team_manager_name,a.team_type,a.top_win_rate_performer agent_name,b.top_win_rate_performer gold_name FROM p.marts.salesforce__team_performance a JOIN g.marts.salesforce__team_performance b ON a.team_manager_id IS NOT DISTINCT FROM b.team_manager_id AND a.team_manager_name IS NOT DISTINCT FROM b.team_manager_name AND a.team_type IS NOT DISTINCT FROM b.team_type WHERE a.top_win_rate_performer IS DISTINCT FROM b.top_win_rate_performer
```


```json
{"columns":["team_manager_id","team_manager_name","team_type","agent_name","gold_name"],"rows":[["005u8TBNEtRI3Mw","Stacey Powell","Other","Christine Morrison","Heidi Turner"],["005I5SrJH3yvVjc","Jason Moreno","Other","Dawn Bailey","Tony Lewis"]]}
```


并列赢家诊断：[023_team_ties.json](../023_team_ties.json)，两组共四个候选 win rate 均为所在组最大值 0。

## 独立单点重跑

### 首轮：[023_reruns_impl-018_salesforce__team_performance.json](../023_reruns_impl-018_salesforce__team_performance.json)

上游副本来源：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-018/salesforce.duckdb`。

共同时间控制：`[]`。

留存结果与 gold（可能含上游或时刻影响；归因使用下面的同口径基线）：

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|496|496|496|1334|否|
|L1|496|496|496|1334|否|
|L2|496|496|496|1334|否|
|L3|496|496|496|1334|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"team_health_score":496,"team_total_revenue":272,"avg_revenue_per_member":292,"top_revenue_performer":272,"top_win_rate_performer":2}`
- L1：`{"team_health_score":496,"team_total_revenue":272,"avg_revenue_per_member":292,"top_revenue_performer":272,"top_win_rate_performer":2}`
- L2：`{"team_health_score":496,"team_total_revenue":272,"avg_revenue_per_member":292,"top_revenue_performer":272,"top_win_rate_performer":2}`
- L3：`{"team_health_score":496,"team_total_revenue":272,"avg_revenue_per_member":292,"top_revenue_performer":272,"top_win_rate_performer":2}`

#### baseline

只应用共同时间控制，未改错误点。
私有 SQL：`data/023_work/impl-018_salesforce__team_performance/baseline.sql`；SHA-256 `f0fcb6526b209972c74c557815cdae25a35354208eae21ea4c0cf1b09a1336e9`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|496|496|496|1334|否|
|L1|496|496|496|1334|否|
|L2|496|496|496|1334|否|
|L3|496|496|496|1334|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"team_health_score":496,"team_total_revenue":272,"avg_revenue_per_member":292,"top_revenue_performer":272,"top_win_rate_performer":2}`
- L1：`{"team_health_score":496,"team_total_revenue":272,"avg_revenue_per_member":292,"top_revenue_performer":272,"top_win_rate_performer":2}`
- L2：`{"team_health_score":496,"team_total_revenue":272,"avg_revenue_per_member":292,"top_revenue_performer":272,"top_win_rate_performer":2}`
- L3：`{"team_health_score":496,"team_total_revenue":272,"avg_revenue_per_member":292,"top_revenue_performer":272,"top_win_rate_performer":2}`

#### health_growth_null

判定：主因；类别候选 C。契约增长率 NULL 落 else=5，agent COALESCE 成0给10分。

相对本轮基线减少行 204、格 496；按行优先、格次之排序。
共同控制后 SQL 第 59 行起、字符 offset 4826 的唯一连续替换；其余字节不动。
替换前：
```sql
case when coalesce(revenue_growth_qoq_percentage,0)>10 then 20 when coalesce(revenue_growth_qoq_percentage,0)>0 then 15 when coalesce(revenue_growth_qoq_percentage,0)>=-10 then 10 else 5 end
```

替换后：
```sql
case when revenue_growth_qoq_percentage>10 then 20 when revenue_growth_qoq_percentage>0 then 15 when revenue_growth_qoq_percentage>=-10 then 10 else 5 end
```

私有 SQL：`data/023_work/impl-018_salesforce__team_performance/health_growth_null.sql`；SHA-256 `30c6de7b76e739a7349a3a7543f995a44a9ffe42f4214936a59b9a727fe539ed`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|496|496|292|838|否|
|L1|496|496|292|838|否|
|L2|496|496|292|838|否|
|L3|496|496|292|838|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"team_total_revenue":272,"avg_revenue_per_member":292,"top_revenue_performer":272,"top_win_rate_performer":2}`
- L1：`{"team_total_revenue":272,"avg_revenue_per_member":292,"top_revenue_performer":272,"top_win_rate_performer":2}`
- L2：`{"team_total_revenue":272,"avg_revenue_per_member":292,"top_revenue_performer":272,"top_win_rate_performer":2}`
- L3：`{"team_total_revenue":272,"avg_revenue_per_member":292,"top_revenue_performer":272,"top_win_rate_performer":2}`

#### revenue_sum

判定：参与因素；类别候选 A。total revenue 的来源两种聚合未明确列映射。

相对本轮基线减少行 0、格 272；按行优先、格次之排序。
共同控制后 SQL 第 27 行起、字符 offset 1952 的唯一连续替换；其余字节不动。
替换前：
```sql
sum(total_revenue_won) as team_total_revenue
```

替换后：
```sql
sum(total_won_amount) as team_total_revenue
```

私有 SQL：`data/023_work/impl-018_salesforce__team_performance/revenue_sum.sql`；SHA-256 `0be5ae0d826bd7354e34d6a4d391a1fa5fdb9a63717e3d9bafea8e6d652a8498`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|496|496|496|1062|否|
|L1|496|496|496|1062|否|
|L2|496|496|496|1062|否|
|L3|496|496|496|1062|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"team_health_score":496,"avg_revenue_per_member":292,"top_revenue_performer":272,"top_win_rate_performer":2}`
- L1：`{"team_health_score":496,"avg_revenue_per_member":292,"top_revenue_performer":272,"top_win_rate_performer":2}`
- L2：`{"team_health_score":496,"avg_revenue_per_member":292,"top_revenue_performer":272,"top_win_rate_performer":2}`
- L3：`{"team_health_score":496,"avg_revenue_per_member":292,"top_revenue_performer":272,"top_win_rate_performer":2}`

#### revenue_avg

判定：参与因素；类别候选 A。平均 revenue 来源不同。

相对本轮基线减少行 0、格 292；按行优先、格次之排序。
共同控制后 SQL 第 29 行起、字符 offset 2154 的唯一连续替换；其余字节不动。
替换前：
```sql
round(avg(total_revenue_won)) as avg_revenue_per_member
```

替换后：
```sql
round(avg(total_won_amount)) as avg_revenue_per_member
```

私有 SQL：`data/023_work/impl-018_salesforce__team_performance/revenue_avg.sql`；SHA-256 `5cfb31e8013d8b49e0d4dc4c0d658dbbb33aa1df60420a7d2dccc846b4101674`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|496|496|496|1042|否|
|L1|496|496|496|1042|否|
|L2|496|496|496|1042|否|
|L3|496|496|496|1042|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"team_health_score":496,"team_total_revenue":272,"top_revenue_performer":272,"top_win_rate_performer":2}`
- L1：`{"team_health_score":496,"team_total_revenue":272,"top_revenue_performer":272,"top_win_rate_performer":2}`
- L2：`{"team_health_score":496,"team_total_revenue":272,"top_revenue_performer":272,"top_win_rate_performer":2}`
- L3：`{"team_health_score":496,"team_total_revenue":272,"top_revenue_performer":272,"top_win_rate_performer":2}`

#### revenue_top

判定：参与因素；类别候选 C。契约明确 highest total won amount。

相对本轮基线减少行 0、格 270；按行优先、格次之排序。
共同控制后 SQL 第 42 行起、字符 offset 3320 的唯一连续替换；其余字节不动。
替换前：
```sql
arg_max(full_name,total_revenue_won) filter(where total_revenue_won is not null)
```

替换后：
```sql
arg_max(full_name,total_won_amount) filter(where total_won_amount is not null)
```

私有 SQL：`data/023_work/impl-018_salesforce__team_performance/revenue_top.sql`；SHA-256 `c040cc37cc76e70b11149c0b264cc609c9f0298fc00ba3a4e38e6ee1f717762d`。

|档位|agent 行|gold 行|不一致行|不一致格|整表匹配|
|---|---:|---:|---:|---:|---|
|L0|496|496|496|1064|否|
|L1|496|496|496|1064|否|
|L2|496|496|496|1064|否|
|L3|496|496|496|1064|否|

整表首次匹配档位：仍不匹配。

每列不一致格数（共同键残余配对的不同值，加仅一侧行/重复余量对每列各贡献 1；包含评测键，未列列为 0）：
- L0：`{"team_health_score":496,"team_total_revenue":272,"avg_revenue_per_member":292,"top_revenue_performer":2,"top_win_rate_performer":2}`
- L1：`{"team_health_score":496,"team_total_revenue":272,"avg_revenue_per_member":292,"top_revenue_performer":2,"top_win_rate_performer":2}`
- L2：`{"team_health_score":496,"team_total_revenue":272,"avg_revenue_per_member":292,"top_revenue_performer":2,"top_win_rate_performer":2}`
- L3：`{"team_health_score":496,"team_total_revenue":272,"avg_revenue_per_member":292,"top_revenue_performer":2,"top_win_rate_performer":2}`

## 规则问题

team_total_revenue 与 avg_revenue_per_member 的收入源未明确列名，可读作 user_performance.total_won_amount 或 revenue_data.total_revenue_won，本次两处列为 A 因素；top_revenue_performer 明确 total won amount，按 C。
