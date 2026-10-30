# impl-008 | marts | asana__team_efficiency_metrics | 差异：S1；日期 原记录

## 契约完整原文

S3:1547–1717

```yaml
    - name: asana__team_efficiency_metrics
      description: Team-level efficiency, performance, schedule, quality metrics, classifications, and ranks computed from Asana teams, projects, tasks, and users
      grain: One validated row per (team_id, team_name)
      source_models:
      - staging.stg_asana__team
      - staging.stg_asana__project
      - intermediate.int_asana__project_health_indicators
      - staging.stg_asana__project_task
      - staging.stg_asana__task
      - staging.stg_asana__user
      business_logic: '- Inputs and filters: - team_base: teams with non-null team_name. - project_base: projects with non-null team_id. - project_health_summary: project health fields with project_size_category defaulted to ''medium_project'' and schedule_forecast sourced from project_forecast. - user_basic_metrics: users with defaults performance_grade=''developing_performer'', workload_category=''normal_workload'', anomaly_flag=''normal'', risk_level=''low_risk'', portfolio_task_count=0, portfolio_overdue_tasks=0. - team_project_summary (per team_id, team_name; projects linked to health by project_id): - Project counts: - total_projects: number of unique projects. - active_projects: unique projects where project_status=''active''; projects without health data are not counted. - completed_projects: unique projects with completion_percentage=100. - overdue_projects: unique projects forecasted ''overdue''. - Averages over health fields (NULLs are ignored; result is NULL when no non-NULL values exist): - avg_project_health and avg_project_performance from overall_health_score. - avg_completion_rate from completion_percentage. - avg_quality_rate from quality_percentage. - avg_risk_percentage from risk_percentage. - Project size distribution: counts of projects by project_size_category among those with health data. - Defaults: total_team_tasks=0, completed_team_tasks=0, active_team_tasks=0, overdue_team_tasks=0, total_project_assignments=0, avg_tasks_per_assignee_across_projects=0.0, avg_project_velocity=0.5, avg_estimated_completion_days=30.0. - Percent metrics: - on_schedule_rate_pct: for teams with at least one unique project, percentage of unique projects forecasted ''on_schedule'', rounded to 2 decimals; otherwise 0. - quality_completion_rate_pct: for teams with at least one unique completed project, percentage of unique completed projects with overall_health_score>=80, rounded to 2 decimals; otherwise 0. - team_member_performance (per team via projects → project_task → task; only tasks with non-null assignee; users linked by assignee_user_id=user_id): - unique_team_members: number of distinct assignees. - Defaults: avg_member_performance=50.0, avg_member_completion_rate=75.0, avg_member_quality_rate=70.0. - Distributions (counts across task rows; a member appearing on multiple tasks is counted multiple times): top/high/solid/developing/underperformers by performance_grade; high_workload_members by workload_category=''high_workload''; high_risk_members by risk_level=''high_risk''. - avg_tasks_per_member: average of portfolio_task_count over joined task rows; NULL when no rows. - team_efficiency_scoring (join by team_id): - project_management_score (0–25): from on_schedule_rate_pct thresholds (>=90→25, >=75→20, >=60→15, >=40→10, else 5), capped to [0,25]. - quality_management_score (0–25): from avg_quality_rate thresholds (>=85→25, >=70→20, >=55→15, >=40→10, else 5), capped to [0,25]. - collaboration_efficiency_score (0–25): if unique_team_members>0 then based on performer mix shares ((top+high), then (top+high+solid), then underperformers); else 0; capped to [0,25]. - resource_optimization_score (0–25): if unique_team_members>0 then based on shares of high_workload_members and high_risk_members; else 0; capped to [0,25]. - final_team_metrics: - overall_team_efficiency_score: sum of the four sub-scores (0–100). - efficiency_grade: thresholds on overall_team_efficiency_score (>=85 highly_efficient, >=70 efficient, >=55 moderately_efficient, >=40 needs_improvement, else inefficient). - team_size_category: by unique_team_members (<=3 small_team, <=8 medium_team, <=15 large_team, else enterprise_team). - workload_balance_status: by share of high_workload_members (<=10% well_balanced, <=25% mostly_balanced, <=50% unbalanced, else severely_unbalanced); ''no_data'' when no members. - team_maturity_level: by performer mix shares ((top+high) then (top+high+solid) then underperformers); ''undefined'' when no members. - improvement_recommendations: phrases appended in fixed order when conditions are met, then trailing comma/space removed; empty when none. - team_strengths: phrases appended in fixed order when conditions are met, then trailing comma/space removed; empty when none. - validated_team_metrics: - is_valid_record: true only when team_id and team_name are present; overall_team_efficiency_score, avg_completion_rate, avg_quality_rate are within [0,100]; total_projects, completed_projects are non-negative; completed_projects does not exceed total_projects; unique_team_members is non-negative. - Ranks: efficiency_rank by overall_team_efficiency_score descending; performance_rank by avg_project_performance descending; schedule_reliability_rank by on_schedule_rate_pct descending; quality_rank by avg_quality_rate descending; ranks computed before filtering invalid rows. - Output: only rows with is_valid_record=true; ordered by overall_team_efficiency_score descending, then team_id.'
      columns:
      - name: team_id
        data_type: VARCHAR
        description: Team identifier; exactly one output row per (team_id, team_name) after validation
      - name: team_name
        data_type: VARCHAR
        description: Team display name; non-null due to initial filter
      - name: total_projects
        data_type: BIGINT
        description: Number of unique projects for the team; unaffected by health join; 0 when none
      - name: active_projects
        data_type: BIGINT
        description: Unique projects with status 'active'; projects without health data are not counted; 0 when none
      - name: completed_projects
        data_type: BIGINT
        description: Unique projects with 100% completion; 0 when none
      - name: overdue_projects
        data_type: BIGINT
        description: Unique projects forecasted 'overdue'; 0 when none
      - name: avg_project_health
        data_type: DOUBLE
        description: Average overall health across projects with health data; NULL when none
      - name: avg_project_performance
        data_type: DOUBLE
        description: Same as avg_project_health; NULL when none
      - name: avg_completion_rate
        data_type: DOUBLE
        description: Average completion percentage (0–100) across projects with health data; NULL when none
      - name: avg_quality_rate
        data_type: DOUBLE
        description: Average quality percentage (0–100) across projects with health data; NULL when none
      - name: avg_risk_percentage
        data_type: DOUBLE
        description: Average risk percentage (0–100) across projects with health data; NULL when none
      - name: enterprise_projects
        data_type: BIGINT
        description: Projects with size 'enterprise_project' among those with health data
      - name: large_projects
        data_type: BIGINT
        description: Projects with size 'large_project' among those with health data
      - name: medium_projects
        data_type: BIGINT
        description: Projects with size 'medium_project' among those with health data
      - name: small_projects
        data_type: BIGINT
        description: Projects with size 'small_project' among those with health data
      - name: total_team_tasks
        data_type: INTEGER
        description: Constant 0
      - name: completed_team_tasks
        data_type: INTEGER
        description: Constant 0
      - name: active_team_tasks
        data_type: INTEGER
        description: Constant 0
      - name: overdue_team_tasks
        data_type: INTEGER
        description: Constant 0
      - name: total_project_assignments
        data_type: INTEGER
        description: Constant 0
      - name: avg_tasks_per_assignee_across_projects
        data_type: DECIMAL(2,1)
        description: Constant 0.0
      - name: avg_project_velocity
        data_type: DECIMAL(2,1)
        description: Constant 0.5
      - name: avg_estimated_completion_days
        data_type: DECIMAL(3,1)
        description: Constant 30.0
      - name: on_schedule_rate_pct
        data_type: DOUBLE
        description: Share of unique projects forecasted 'on_schedule', rounded to 2 decimals; 0 when no projects
      - name: quality_completion_rate_pct
        data_type: DOUBLE
        description: Share of unique completed projects with health>=80, rounded to 2 decimals; 0 when none completed
      - name: unique_team_members
        data_type: BIGINT
        description: Distinct assignees on tasks linked to the team's projects; NULL assignees excluded
      - name: avg_member_performance
        data_type: DECIMAL(3,1)
        description: Constant 50.0
      - name: avg_member_completion_rate
        data_type: DECIMAL(3,1)
        description: Constant 75.0
      - name: avg_member_quality_rate
        data_type: DECIMAL(3,1)
        description: Constant 70.0
      - name: top_performers
        data_type: BIGINT
        description: Task rows where user grade is 'top_performer'; duplicates by user across tasks are kept
      - name: high_performers
        data_type: BIGINT
        description: Task rows where user grade is 'high_performer'; duplicates by user across tasks are kept
      - name: solid_performers
        data_type: BIGINT
        description: Task rows where user grade is 'solid_performer'; duplicates by user across tasks are kept
      - name: developing_performers
        data_type: BIGINT
        description: Task rows where user grade is 'developing_performer'; duplicates by user across tasks are kept
      - name: underperformers
        data_type: BIGINT
        description: Task rows where user grade is 'needs_improvement' or 'requires_support'; duplicates kept
      - name: high_workload_members
        data_type: BIGINT
        description: Task rows with user workload 'high_workload'; duplicates kept
      - name: high_risk_members
        data_type: BIGINT
        description: Task rows with user risk 'high_risk'; duplicates kept
      - name: avg_tasks_per_member
        data_type: DOUBLE
        description: Average of user portfolio_task_count over joined task rows; typically 0 due to defaults; NULL when no rows
      - name: project_management_score
        data_type: INTEGER
        description: 0–25 score from on_schedule_rate_pct thresholds (>=90→25, >=75→20, >=60→15, >=40→10, else 5), capped to [0,25]
      - name: quality_management_score
        data_type: INTEGER
        description: 0–25 score from avg_quality_rate thresholds (>=85→25, >=70→20, >=55→15, >=40→10, else 5), capped to [0,25]
      - name: collaboration_efficiency_score
        data_type: INTEGER
        description: 0–25 score from performer mix among unique_team_members; 0 when no members; capped to [0,25]
      - name: resource_optimization_score
        data_type: INTEGER
        description: 0–25 score from high_workload and high_risk member shares; 0 when no members; capped to [0,25]
      - name: overall_team_efficiency_score
        data_type: INTEGER
        description: Sum of the four sub-scores in [0,100]
      - name: efficiency_grade
        data_type: VARCHAR
        description: 'Label from overall_team_efficiency_score: >=85 highly_efficient, >=70 efficient, >=55 moderately_efficient, >=40 needs_improvement, else inefficient'
      - name: team_size_category
        data_type: VARCHAR
        description: 'Size by unique_team_members: <=3 small_team, <=8 medium_team, <=15 large_team, else enterprise_team'
      - name: workload_balance_status
        data_type: VARCHAR
        description: 'Balance by share of high_workload members: <=10% well_balanced, <=25% mostly_balanced, <=50% unbalanced, else severely_unbalanced; ''no_data'' when no members'
      - name: team_maturity_level
        data_type: VARCHAR
        description: 'Maturity by performer mix: >=60% top+high mature_team; else >=70% top+high+solid developing_team; else underperformers<=30% mixed_maturity; else needs_development; ''undefined'' when no members'
      - name: improvement_recommendations
        data_type: VARCHAR
        description: Comma-separated suggestions built in fixed order and trimmed; empty when none
      - name: team_strengths
        data_type: VARCHAR
        description: Comma-separated strengths built in fixed order and trimmed; empty when none
      - name: is_valid_record
        data_type: BOOLEAN
        description: 'True only if IDs present and metrics within bounds: overall_team_efficiency_score, avg_completion_rate, avg_quality_rate in [0,100]; total_projects, completed_projects non-negative with completed_projects<=total_projects; unique_team_members non-negative; else false'
      - name: efficiency_rank
        data_type: BIGINT
        description: Rank over all teams by overall_team_efficiency_score descending (ties share rank); computed before filtering invalid rows
      - name: performance_rank
        data_type: BIGINT
        description: Rank over all teams by avg_project_performance descending (ties share rank); computed before filtering invalid rows
      - name: schedule_reliability_rank
        data_type: BIGINT
        description: Rank over all teams by on_schedule_rate_pct descending (ties share rank); computed before filtering invalid rows
      - name: quality_rank
        data_type: BIGINT
        description: Rank over all teams by avg_quality_rate descending (ties share rank); computed before filtering invalid rows
```

## agent 最终 SQL

S4

```sql
WITH teams AS (SELECT * FROM staging.stg_asana__team WHERE team_name IS NOT NULL),
project_stats AS (SELECT p.team_id,team.team_name,COUNT(DISTINCT p.project_id)::BIGINT total_projects,COUNT(DISTINCT p.project_id) FILTER(WHERE h.project_status='active')::BIGINT active_projects,COUNT(DISTINCT p.project_id) FILTER(WHERE h.completion_percentage=100)::BIGINT completed_projects,COUNT(DISTINCT p.project_id) FILTER(WHERE h.project_forecast='overdue')::BIGINT overdue_projects,AVG(h.overall_health_score) avg_project_health,AVG(h.overall_health_score) avg_project_performance,AVG(h.completion_percentage) avg_completion_rate,AVG(h.quality_percentage) avg_quality_rate,AVG(h.risk_percentage) avg_risk_percentage,COUNT(*) FILTER(WHERE h.total_tasks>100) enterprise_projects,COUNT(*) FILTER(WHERE h.total_tasks BETWEEN 51 AND 100) large_projects,COUNT(*) FILTER(WHERE h.total_tasks BETWEEN 21 AND 50) medium_projects,COUNT(*) FILTER(WHERE h.total_tasks BETWEEN 6 AND 20) small_projects,
 ROUND(100.0*COUNT(DISTINCT p.project_id) FILTER(WHERE h.project_forecast='on_schedule')/NULLIF(COUNT(DISTINCT p.project_id),0),2) on_schedule_rate_pct,ROUND(100.0*COUNT(DISTINCT p.project_id) FILTER(WHERE h.completion_percentage=100 AND h.overall_health_score>=80)/NULLIF(COUNT(DISTINCT p.project_id) FILTER(WHERE h.completion_percentage=100),0),2) quality_completion_rate_pct
FROM staging.stg_asana__project p LEFT JOIN staging.stg_asana__team team ON p.team_id::VARCHAR=team.team_id LEFT JOIN intermediate.int_asana__project_health_indicators h ON p.project_id=h.project_id GROUP BY p.team_id,team.team_name),
counts AS (SELECT team_id::VARCHAR team_id,COUNT(DISTINCT assignee_user_id)::BIGINT unique_team_members,COUNT(*) FILTER(WHERE FALSE)::BIGINT zero_rows FROM staging.stg_asana__project p JOIN staging.stg_asana__project_task pt ON p.project_id=pt.project_id::VARCHAR JOIN staging.stg_asana__task t ON pt.task_id::VARCHAR=t.task_id WHERE t.assignee_user_id IS NOT NULL GROUP BY team_id)
SELECT t.team_id,t.team_name,COALESCE(ps.total_projects,0)::BIGINT total_projects,COALESCE(ps.active_projects,0)::BIGINT active_projects,COALESCE(ps.completed_projects,0)::BIGINT completed_projects,COALESCE(ps.overdue_projects,0)::BIGINT overdue_projects,ps.avg_project_health,ps.avg_project_performance,ps.avg_completion_rate,ps.avg_quality_rate,ps.avg_risk_percentage,COALESCE(ps.enterprise_projects,0)::BIGINT enterprise_projects,COALESCE(ps.large_projects,0)::BIGINT large_projects,COALESCE(ps.medium_projects,0)::BIGINT medium_projects,COALESCE(ps.small_projects,0)::BIGINT small_projects,
0::INTEGER total_team_tasks,0::INTEGER completed_team_tasks,0::INTEGER active_team_tasks,0::INTEGER overdue_team_tasks,0::INTEGER total_project_assignments,0.0::DECIMAL(2,1) avg_tasks_per_assignee_across_projects,.5::DECIMAL(2,1) avg_project_velocity,30.0::DECIMAL(3,1) avg_estimated_completion_days,COALESCE(ps.on_schedule_rate_pct,0)::DOUBLE on_schedule_rate_pct,COALESCE(ps.quality_completion_rate_pct,0)::DOUBLE quality_completion_rate_pct,COALESCE(c.unique_team_members,0)::BIGINT unique_team_members,50.0::DECIMAL(3,1) avg_member_performance,75.0::DECIMAL(3,1) avg_member_completion_rate,70.0::DECIMAL(3,1) avg_member_quality_rate,
0::BIGINT top_performers,0::BIGINT high_performers,0::BIGINT solid_performers,0::BIGINT developing_performers,0::BIGINT underperformers,0::BIGINT high_workload_members,0::BIGINT high_risk_members,NULL::DOUBLE avg_tasks_per_member,
CASE WHEN COALESCE(ps.on_schedule_rate_pct,0)>=90 THEN 25 WHEN ps.on_schedule_rate_pct>=75 THEN 20 WHEN ps.on_schedule_rate_pct>=60 THEN 15 WHEN ps.on_schedule_rate_pct>=40 THEN 10 ELSE 5 END::INTEGER project_management_score,
CASE WHEN COALESCE(ps.avg_quality_rate,0)>=85 THEN 25 WHEN ps.avg_quality_rate>=70 THEN 20 WHEN ps.avg_quality_rate>=55 THEN 15 WHEN ps.avg_quality_rate>=40 THEN 10 ELSE 5 END::INTEGER quality_management_score,
0::INTEGER collaboration_efficiency_score,0::INTEGER resource_optimization_score,
(CASE WHEN COALESCE(ps.on_schedule_rate_pct,0)>=90 THEN 25 WHEN ps.on_schedule_rate_pct>=75 THEN 20 WHEN ps.on_schedule_rate_pct>=60 THEN 15 WHEN ps.on_schedule_rate_pct>=40 THEN 10 ELSE 5 END+CASE WHEN COALESCE(ps.avg_quality_rate,0)>=85 THEN 25 WHEN ps.avg_quality_rate>=70 THEN 20 WHEN ps.avg_quality_rate>=55 THEN 15 WHEN ps.avg_quality_rate>=40 THEN 10 ELSE 5 END)::INTEGER overall_team_efficiency_score,
'needs_improvement'::VARCHAR efficiency_grade,CASE WHEN COALESCE(c.unique_team_members,0)<=3 THEN 'small_team' WHEN c.unique_team_members<=8 THEN 'medium_team' WHEN c.unique_team_members<=15 THEN 'large_team' ELSE 'enterprise_team' END team_size_category,CASE WHEN COALESCE(c.unique_team_members,0)=0 THEN 'no_data' ELSE 'well_balanced' END workload_balance_status,CASE WHEN COALESCE(c.unique_team_members,0)=0 THEN 'undefined' ELSE 'mixed_maturity' END team_maturity_level,''::VARCHAR improvement_recommendations,''::VARCHAR team_strengths,
(t.team_id IS NOT NULL AND t.team_name IS NOT NULL AND COALESCE(ps.total_projects,0)>=0 AND COALESCE(ps.completed_projects,0)<=COALESCE(ps.total_projects,0) AND COALESCE(c.unique_team_members,0)>=0) is_valid_record,
RANK() OVER(ORDER BY COALESCE(ps.on_schedule_rate_pct,0) DESC) efficiency_rank,RANK() OVER(ORDER BY ps.avg_project_performance DESC) performance_rank,RANK() OVER(ORDER BY COALESCE(ps.on_schedule_rate_pct,0) DESC) schedule_reliability_rank,RANK() OVER(ORDER BY ps.avg_quality_rate DESC) quality_rank
FROM teams t LEFT JOIN project_stats ps ON t.team_id=ps.team_id::VARCHAR LEFT JOIN counts c ON t.team_id=c.team_id
WHERE t.team_id IS NOT NULL ORDER BY overall_team_efficiency_score DESC,t.team_id
```

## gold SQL（仅供定位差异）

S5

```sql
-- Team Efficiency Metrics
-- Team efficiency indicators - analyze team collaboration efficiency, work distribution, performance comparison, etc.

with team_base as (
    select *
    from staging.stg_asana__team
    where team_name is not null
),

user_base as (
    select *
    from staging.stg_asana__user
),

project_base as (
    select *
    from staging.stg_asana__project
    where team_id is not null
),

-- Simplify project analysis and avoid circular dependencies
project_health_summary as (
    select 
        project_id,
        project_name,
        project_status,
        team_id,
        overall_health_score,
        completion_percentage,
        quality_percentage,
        risk_percentage,
        'medium_project' as project_size_category,  -- Add default value
        project_forecast as schedule_forecast
    from intermediate.int_asana__project_health_indicators
),

-- Simplify user performance and avoid circular dependencies
user_basic_metrics as (
    select 
        user_id,
        user_name,
        'developing_performer' as performance_grade,  -- Default values ​​avoid dependencies
        'normal_workload' as workload_category,
        'normal' as anomaly_flag,
        'low_risk' as risk_level,
        0 as portfolio_task_count,
        0 as portfolio_overdue_tasks
    from staging.stg_asana__user
),

-- Team project summary statistics
team_project_summary as (
    select 
        t.team_id,
        t.team_name,
        
        -- Basic project statistics
        count(distinct p.project_id) as total_projects,
        count(distinct case when pa.project_status = 'active' then p.project_id end) as active_projects,
        count(distinct case when pa.completion_percentage = 100 then p.project_id end) as completed_projects,
        count(distinct case when pa.schedule_forecast = 'overdue' then p.project_id end) as overdue_projects,
        
        -- Project health statistics
        avg(pa.overall_health_score) as avg_project_health,
        avg(pa.overall_health_score) as avg_project_performance,
        avg(pa.completion_percentage) as avg_completion_rate,
        avg(pa.quality_percentage) as avg_quality_rate,
        avg(pa.risk_percentage) as avg_risk_percentage,
        
        -- Project size distribution
        count(case when pa.project_size_category = 'enterprise_project' then 1 end) as enterprise_projects,
        count(case when pa.project_size_category = 'large_project' then 1 end) as large_projects,
        count(case when pa.project_size_category = 'medium_project' then 1 end) as medium_projects,
        count(case when pa.project_size_category = 'small_project' then 1 end) as small_projects,
        
        -- Task summary (use default values ​​to avoid field non-existence errors)
        0 as total_team_tasks,
        0 as completed_team_tasks,
        0 as active_team_tasks,
        0 as overdue_team_tasks,
        
        -- Resource configuration (use default values)
        0 as total_project_assignments,
        0.0 as avg_tasks_per_assignee_across_projects,
        
        -- Time efficiency (use default value)
        0.5 as avg_project_velocity,
        30.0 as avg_estimated_completion_days,
        
        -- success rate indicator
        case 
            when count(distinct p.project_id) > 0 then
                round((count(distinct case when pa.schedule_forecast = 'on_schedule' then p.project_id end) * 100.0 / 
                       count(distinct p.project_id)), 2)
            else 0
        end as on_schedule_rate_pct,
        
        case 
            when count(distinct case when pa.completion_percentage = 100 then p.project_id end) > 0 then
                round((count(distinct case when pa.overall_health_score >= 80 then p.project_id end) * 100.0 / 
                       count(distinct case when pa.completion_percentage = 100 then p.project_id end)), 2)
            else 0
        end as quality_completion_rate_pct
        
    from team_base t
    left join project_base p on t.team_id = p.team_id
    left join project_health_summary pa on p.project_id = pa.project_id
    group by 1, 2
),

-- Team member performance summary (team members need to be found through project association)
team_member_performance as (
    select 
        p.team_id,
        
        -- Basic member statistics
        count(distinct t.assignee_user_id) as unique_team_members,
        
        -- Simplified team member data (avoiding complex dependencies)
        50.0 as avg_member_performance,  -- default value
        75.0 as avg_member_completion_rate,  -- default value
        70.0 as avg_member_quality_rate,  -- default value
        60.0 as avg_member_task_health,  -- default value
        
        -- Performance distribution (based on simplified logic)
        count(case when ub.performance_grade = 'top_performer' then 1 end) as top_performers,
        count(case when ub.performance_grade = 'high_performer' then 1 end) as high_performers,
        count(case when ub.performance_grade = 'solid_performer' then 1 end) as solid_performers,
        count(case when ub.performance_grade = 'developing_performer' then 1 end) as developing_performers,
        count(case when ub.performance_grade in ('needs_improvement', 'requires_support') then 1 end) as underperformers,
        
        -- Workload distribution
        count(case when ub.workload_category = 'high_workload' then 1 end) as high_workload_members,
        count(case when ub.workload_category = 'medium_workload' then 1 end) as medium_workload_members,
        count(case when ub.workload_category = 'normal_workload' then 1 end) as normal_workload_members,
        count(case when ub.workload_category = 'light_workload' then 1 end) as light_workload_members,
        
        -- risk assessment
        count(case when ub.risk_level = 'high_risk' then 1 end) as high_risk_members,
        count(case when ub.anomaly_flag != 'normal' then 1 end) as members_with_anomalies,
        
        -- Collaboration metrics
        avg(ub.portfolio_task_count) as avg_tasks_per_member,
        sum(ub.portfolio_task_count) as total_member_tasks,
        avg(ub.portfolio_overdue_tasks) as avg_overdue_per_member
        
    from project_base p
    inner join staging.stg_asana__project_task pt on p.project_id = pt.project_id
    inner join staging.stg_asana__task t on pt.task_id = t.task_id
    left join user_basic_metrics ub on cast(t.assignee_user_id as varchar) = ub.user_id
    where t.assignee_user_id is not null
    group by 1
),

-- Team efficiency score calculation
team_efficiency_scoring as (
    select 
        tps.*,
        tmp.unique_team_members,
        tmp.avg_member_performance,
        tmp.avg_member_completion_rate,
        tmp.avg_member_quality_rate,
        tmp.top_performers,
        tmp.high_performers,
        tmp.solid_performers,
        tmp.developing_performers,
        tmp.underperformers,
        tmp.high_workload_members,
        tmp.high_risk_members,
        tmp.avg_tasks_per_member,
        
        -- Project management efficiency score (0-25 points)
        least(25, greatest(0,
            case 
                when tps.on_schedule_rate_pct >= 90 then 25
                when tps.on_schedule_rate_pct >= 75 then 20
                when tps.on_schedule_rate_pct >= 60 then 15
                when tps.on_schedule_rate_pct >= 40 then 10
                else 5
            end
        )) as project_management_score,
        
        -- Quality management efficiency score (0-25 points)
        least(25, greatest(0,
            case 
                when tps.avg_quality_rate >= 85 then 25
                when tps.avg_quality_rate >= 70 then 20
                when tps.avg_quality_rate >= 55 then 15
                when tps.avg_quality_rate >= 40 then 10
                else 5
            end
        )) as quality_management_score,
        
        -- Team collaboration efficiency score (0-25 points)
        least(25, greatest(0,
            case 
                when tmp.unique_team_members > 0 then
                    case 
                        when (tmp.top_performers + tmp.high_performers) * 100.0 / tmp.unique_team_members >= 70 then 25
                        when (tmp.top_performers + tmp.high_performers) * 100.0 / tmp.unique_team_members >= 50 then 20
                        when (tmp.top_performers + tmp.high_performers + tmp.solid_performers) * 100.0 / tmp.unique_team_members >= 70 then 15
                        when tmp.underperformers * 100.0 / tmp.unique_team_members <= 20 then 10
                        else 5
                    end
                else 0
            end
        )) as collaboration_efficiency_score,
        
        -- Resource optimization efficiency score (0-25 points)
        least(25, greatest(0,
            case 
                when tmp.unique_team_members > 0 then
                    case 
                        when tmp.high_workload_members * 100.0 / tmp.unique_team_members <= 20 and 
                             tmp.high_risk_members = 0 then 25
                        when tmp.high_workload_members * 100.0 / tmp.unique_team_members <= 30 and 
                             tmp.high_risk_members <= tmp.unique_team_members * 0.1 then 20
                        when tmp.high_workload_members * 100.0 / tmp.unique_team_members <= 50 then 15
                        when tmp.high_workload_members * 100.0 / tmp.unique_team_members <= 70 then 10
                        else 5
                    end
                else 0
            end
        )) as resource_optimization_score
        
    from team_project_summary tps
    left join team_member_performance tmp on tps.team_id = tmp.team_id
),

-- Final team efficiency indicator calculation
final_team_metrics as (
    select 
        *,
        
        -- Overall team effectiveness score (0-100 points)
        (project_management_score + quality_management_score + 
         collaboration_efficiency_score + resource_optimization_score) as overall_team_efficiency_score,
        
        -- Team effectiveness level
        case 
            when (project_management_score + quality_management_score + 
                  collaboration_efficiency_score + resource_optimization_score) >= 85 then 'highly_efficient'
            when (project_management_score + quality_management_score + 
                  collaboration_efficiency_score + resource_optimization_score) >= 70 then 'efficient'
            when (project_management_score + quality_management_score + 
                  collaboration_efficiency_score + resource_optimization_score) >= 55 then 'moderately_efficient'
            when (project_management_score + quality_management_score + 
                  collaboration_efficiency_score + resource_optimization_score) >= 40 then 'needs_improvement'
            else 'inefficient'
        end as efficiency_grade,
        
        -- Team size assessment
        case 
            when unique_team_members <= 3 then 'small_team'
            when unique_team_members <= 8 then 'medium_team'
            when unique_team_members <= 15 then 'large_team'
            else 'enterprise_team'
        end as team_size_category,
        
        -- workload balance
        case 
            when unique_team_members > 0 then
                case 
                    when high_workload_members * 100.0 / unique_team_members <= 10 then 'well_balanced'
                    when high_workload_members * 100.0 / unique_team_members <= 25 then 'mostly_balanced'
                    when high_workload_members * 100.0 / unique_team_members <= 50 then 'unbalanced'
                    else 'severely_unbalanced'
                end
            else 'no_data'
        end as workload_balance_status,
        
        -- Team maturity assessment
        case 
            when unique_team_members > 0 then
                case 
                    when (top_performers + high_performers) * 100.0 / unique_team_members >= 60 then 'mature_team'
                    when (top_performers + high_performers + solid_performers) * 100.0 / unique_team_members >= 70 then 'developing_team'
                    when underperformers * 100.0 / unique_team_members <= 30 then 'mixed_maturity'
                    else 'needs_development'
                end
            else 'undefined'
        end as team_maturity_level,
        
        -- Improvement suggestions
        trim(
            case when project_management_score < 15 then 'improve_project_management, ' else '' end ||
            case when quality_management_score < 15 then 'enhance_quality_processes, ' else '' end ||
            case when collaboration_efficiency_score < 15 then 'strengthen_collaboration, ' else '' end ||
            case when resource_optimization_score < 15 then 'optimize_resource_allocation, ' else '' end ||
            case when unique_team_members > 0 and high_risk_members > 0 then 'address_at_risk_members, ' else '' end ||
            case when avg_risk_percentage > 25 then 'implement_risk_management, ' else '' end ||
            case when on_schedule_rate_pct < 60 then 'improve_schedule_adherence, ' else '' end,
            ', '
        ) as improvement_recommendations,
        
        -- Team advantage
        trim(
            case when project_management_score >= 20 then 'strong_project_management, ' else '' end ||
            case when quality_management_score >= 20 then 'high_quality_delivery, ' else '' end ||
            case when collaboration_efficiency_score >= 20 then 'excellent_collaboration, ' else '' end ||
            case when resource_optimization_score >= 20 then 'optimal_resource_use, ' else '' end ||
            case when unique_team_members > 0 and top_performers * 100.0 / unique_team_members >= 30 then 'strong_performers, ' else '' end ||
            case when on_schedule_rate_pct >= 80 then 'reliable_delivery, ' else '' end,
            ', '
        ) as team_strengths
        
    from team_efficiency_scoring
),

-- Data quality verification and ranking
validated_team_metrics as (
    select 
        *,
        
        -- Data quality verification
        case 
            when team_id is null or team_name is null then false
            when overall_team_efficiency_score < 0 or overall_team_efficiency_score > 100 then false
            when avg_completion_rate < 0 or avg_completion_rate > 100 then false
            when avg_quality_rate < 0 or avg_quality_rate > 100 then false
            when total_projects < 0 or completed_projects < 0 then false
            when completed_projects > total_projects then false
            when unique_team_members < 0 then false
            else true
        end as is_valid_record,
        
        -- Global ranking
        rank() over (order by overall_team_efficiency_score desc) as efficiency_rank,
        rank() over (order by avg_project_performance desc) as performance_rank,
        rank() over (order by on_schedule_rate_pct desc) as schedule_reliability_rank,
        rank() over (order by avg_quality_rate desc) as quality_rank
        
    from final_team_metrics
)

select *
from validated_team_metrics
where is_valid_record = true
order by overall_team_efficiency_score desc, team_id
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 44 | 44 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"team_id":"1158861054404"}</code> |
| K2 | <code>{"team_id":"1250724528183"}</code> |
| K3 | <code>{"team_id":"1257507046171"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| team_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| team_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| total_projects | 0 | 0 | 0 | BIGINT | BIGINT |
| active_projects | 0 | 0 | 0 | BIGINT | BIGINT |
| completed_projects | 0 | 0 | 0 | BIGINT | BIGINT |
| overdue_projects | 0 | 0 | 0 | BIGINT | BIGINT |
| avg_project_health | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_project_performance | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_completion_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_quality_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_risk_percentage | 0 | 0 | 0 | DOUBLE | DOUBLE |
| enterprise_projects | 0 | 0 | 0 | BIGINT | BIGINT |
| large_projects | 0 | 0 | 0 | BIGINT | BIGINT |
| medium_projects | 44 | 44 | 44 | BIGINT | BIGINT |
| small_projects | 44 | 44 | 44 | BIGINT | BIGINT |
| total_team_tasks | 0 | 0 | 0 | INTEGER | INTEGER |
| completed_team_tasks | 0 | 0 | 0 | INTEGER | INTEGER |
| active_team_tasks | 0 | 0 | 0 | INTEGER | INTEGER |
| overdue_team_tasks | 0 | 0 | 0 | INTEGER | INTEGER |
| total_project_assignments | 0 | 0 | 0 | INTEGER | INTEGER |
| avg_tasks_per_assignee_across_projects | 0 | 0 | 0 | DECIMAL(2,1) | DECIMAL(2,1) |
| avg_project_velocity | 0 | 0 | 0 | DECIMAL(2,1) | DECIMAL(2,1) |
| avg_estimated_completion_days | 0 | 0 | 0 | DECIMAL(3,1) | DECIMAL(3,1) |
| on_schedule_rate_pct | 0 | 0 | 0 | DOUBLE | DOUBLE |
| quality_completion_rate_pct | 0 | 0 | 0 | DOUBLE | DOUBLE |
| unique_team_members | 0 | 0 | 0 | BIGINT | BIGINT |
| avg_member_performance | 0 | 0 | 0 | DECIMAL(3,1) | DECIMAL(3,1) |
| avg_member_completion_rate | 0 | 0 | 0 | DECIMAL(3,1) | DECIMAL(3,1) |
| avg_member_quality_rate | 0 | 0 | 0 | DECIMAL(3,1) | DECIMAL(3,1) |
| top_performers | 0 | 0 | 0 | BIGINT | BIGINT |
| high_performers | 0 | 0 | 0 | BIGINT | BIGINT |
| solid_performers | 0 | 0 | 0 | BIGINT | BIGINT |
| developing_performers | 44 | 44 | 44 | BIGINT | BIGINT |
| underperformers | 0 | 0 | 0 | BIGINT | BIGINT |
| high_workload_members | 0 | 0 | 0 | BIGINT | BIGINT |
| high_risk_members | 0 | 0 | 0 | BIGINT | BIGINT |
| avg_tasks_per_member | 44 | 44 | 44 | DOUBLE | DOUBLE |
| project_management_score | 0 | 0 | 0 | INTEGER | INTEGER |
| quality_management_score | 0 | 0 | 0 | INTEGER | INTEGER |
| collaboration_efficiency_score | 44 | 44 | 44 | INTEGER | INTEGER |
| resource_optimization_score | 44 | 44 | 44 | INTEGER | INTEGER |
| overall_team_efficiency_score | 44 | 44 | 44 | INTEGER | INTEGER |
| efficiency_grade | 0 | 0 | 0 | VARCHAR | VARCHAR |
| team_size_category | 0 | 0 | 0 | VARCHAR | VARCHAR |
| workload_balance_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| team_maturity_level | 0 | 0 | 0 | VARCHAR | VARCHAR |
| improvement_recommendations | 44 | 44 | 44 | VARCHAR | VARCHAR |
| team_strengths | 44 | 44 | 44 | VARCHAR | VARCHAR |
| is_valid_record | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| efficiency_rank | 0 | 0 | 0 | BIGINT | BIGINT |
| performance_rank | 0 | 0 | 0 | BIGINT | BIGINT |
| schedule_reliability_rank | 0 | 0 | 0 | BIGINT | BIGINT |
| quality_rank | 0 | 0 | 0 | BIGINT | BIGINT |

medium_projects 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0 | 9 |
| K2 | 0 | 13 |
| K3 | 0 | 9 |

small_projects 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 7 | 0 |
| K2 | 10 | 0 |
| K3 | 6 | 0 |

developing_performers 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0 | 41 |
| K2 | 0 | 48 |
| K3 | 0 | 28 |

avg_tasks_per_member 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0.0 |
| K2 | null | 0.0 |
| K3 | null | 0.0 |

collaboration_efficiency_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0 | 10 |
| K2 | 0 | 10 |
| K3 | 0 | 10 |

resource_optimization_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0 | 25 |
| K2 | 0 | 25 |
| K3 | 0 | 25 |

overall_team_efficiency_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 10 | 45 |
| K2 | 10 | 45 |
| K3 | 10 | 45 |

improvement_recommendations 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code></code> | improve_project_management, enhance_quality_processes, strengthen_collaboration, improve_schedule_adherence |
| K2 | <code></code> | improve_project_management, enhance_quality_processes, strengthen_collaboration, improve_schedule_adherence |
| K3 | <code></code> | improve_project_management, enhance_quality_processes, strengthen_collaboration, improve_schedule_adherence |

team_strengths 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code></code> | optimal_resource_use |
| K2 | <code></code> | optimal_resource_use |
| K3 | <code></code> | optimal_resource_use |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>1列；[{"column":"avg_tasks_per_member","table_rows":44}]</code> |
| A3_constant_nonnull_column | <code>39列；[{"column":"active_projects","value":"0"},{"column":"avg_quality_rate","value":"0.0"},{"column":"enterprise_projects","value":"0"}]</code> |
| A4_equal_columns | <code>6组；[{"columns":["active_projects","enterprise_projects","large_projects","medium_projects","total_team_tasks","completed_team_tasks","active_team_tasks","overdue_team_tasks","total_project_assignments","top_performers","high_performers","solid_performers","developing_performers","underperformers","high_workload_members","high_risk_members","collaboration_efficiency_score","resource_optimization_score"],"nonnull_equal_rows":44,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["avg_project_health","avg_project_performance"],"nonnull_equal_rows":44,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["avg_quality_rate","avg_tasks_per_assignee_across_projects","on_schedule_rate_pct"],"nonnull_equal_rows":44,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>6组；[{"columns":["active_projects","enterprise_projects","large_projects","medium_projects","total_team_tasks","completed_team_tasks","active_team_tasks","overdue_team_tasks","total_project_assignments","top_performers","high_performers","solid_performers","developing_performers","underperformers","high_workload_members","high_risk_members","collaboration_efficiency_score","resource_optimization_score"],"nonnull_equal_rows":44,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["avg_project_health","avg_project_performance"],"nonnull_equal_rows":44,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["avg_quality_rate","avg_tasks_per_assignee_across_projects","on_schedule_rate_pct"],"nonnull_equal_rows":44,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| B5_null_literal_output | <code>1输出列；[{"column":"avg_tasks_per_member","expression":["CAST(NULL AS DOUBLE)"]}]</code> |
| B6_constant_literal_output | <code>23输出列；[{"column":"total_team_tasks","expression":["CAST(0 AS INT)"]},{"column":"completed_team_tasks","expression":["CAST(0 AS INT)"]},{"column":"active_team_tasks","expression":["CAST(0 AS INT)"]}]</code> |
| B7_specified_not_read | <code>["staging.stg_asana__user"]</code> |
| D10_keyword_in_any_result_field | <code>命中数=2；assistant_trajectory 'asana__team_efficiency_metrics':'''WITH teams AS (SELECT * FROM staging.stg_asana__team WHERE team_name IS NOT NULL),</code> |

## 轨迹索引（不放输出原文）

本题事件总数：55；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; sed -n '1,240p' run.py</code> | 12054 | true | false |
| 15 | run | <code>mkdir -p sql/{staging,intermediate,marts} &amp;&amp; cat &gt; /tmp/build.py &lt;&lt;'PY'<br>from pathlib import Path<br>S=Path('sql/staging')<br># source columns select expressions and row filters<br>models={<br>'stg_asana__user':("</code> | 0 | false | false |
| 17 | run | <code>cat &gt; /tmp/inter.py &lt;&lt;'PY'<br>from pathlib import Path<br>D=Path('sql/intermediate')<br>q={<br>'int_asana__task_story':'''SELECT s.story_id, s.created_at, s.created_by_user_id, s.story_type, s.story_text, s.targe</code> | 0 | false | false |
| 21 | run | <code>cat &gt;&gt; /tmp/inter.py &lt;&lt;'PY'<br>q2={<br>'int_asana__project_health_indicators':'''WITH project_base AS (<br> SELECT * FROM staging.stg_asana__project WHERE project_name IS NOT NULL AND created_at IS NOT NULL<br>),</code> | 0 | false | false |
| 23 | run | <code>cat &gt; /tmp/marts.py &lt;&lt;'PY'<br>from pathlib import Path<br>D=Path('sql/marts')<br>q={<br>'asana__user':'''SELECT u.user_id,u.user_name,u.email,COALESCE(m.number_of_open_tasks,0)::BIGINT number_of_open_tasks,COALES</code> | 0 | false | false |
| 25 | run | <code>cat &gt; /tmp/marts2.py &lt;&lt;'PY'<br>from pathlib import Path<br>D=Path('sql/marts')<br>q={<br>'asana__project_analytics':'''WITH base AS (<br> SELECT p.project_id,p.project_name,p.team_id,t.team_name,p.owner_user_id proj</code> | 0 | false | false |
| 27 | run | <code>python run.py &gt; /tmp/runlog 2&gt;&amp;1; tail -100 /tmp/runlog</code> | 7124 | true | false |
| 33 | run | <code>python - &lt;&lt;'PY'<br>p='sql/staging/stg_asana__project.sql';s=open(p).read();<br>for x in ['created_at','due_date','modified_at']:<br> s=s.replace(f'TRY_CAST({x} AS TIMESTAMP)',f'CAST(TRY_STRPTIME({x}, \'%Y-%m-%</code> | 551 | false | false |
| 35 | run | <code>cat &gt; sql/marts/asana__daily_metrics.sql &lt;&lt;'SQL'<br>WITH creations AS (<br>    SELECT CAST(CAST(created_at AS DATE) AS TIMESTAMP) AT TIME ZONE 'UTC' AS date_day,<br>           COUNT(*)::HUGEINT AS tasks_create</code> | 328 | false | false |
| 37 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('asana.duckdb',read_only=True)<br>for sch in ['staging','intermediate','mart']:<br> print('\n',sch)<br> for (t,) in c.execute(f"select table_name from information</code> | 1027 | true | false |
| 39 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('asana.duckdb',read_only=True)<br>print(c.execute('select min(created_at),max(created_at),count(*) filter(where assignee_user_id is not null),current_date f</code> | 872 | false | false |
| 41 | run | <code>grep -R -nE ';[[:space:]]*$&#124;ref\(' sql &#124;&#124; true; python - &lt;&lt;'PY'<br>from pathlib import Path<br>expected={<br>'staging':'stg_asana__user stg_asana__team stg_asana__project stg_asana__task stg_asana__section stg</code> | 105 | false | false |

### agent action 的 thought/message 命中原句

event 25 / message

```text
'asana__team_efficiency_metrics':'''WITH teams AS (SELECT * FROM staging.stg_asana__team WHERE team_name IS NOT NULL),
```
event 33 / message

```text
p='sql/marts/asana__team_efficiency_metrics.sql';s=open(p).read().replace("SELECT p.team_id,p.team_name,COUNT(DISTINCT p.project_id)","SELECT p.team_id,team.team_name,COUNT(DISTINCT p.project_id)").replace("FROM staging.stg_asana__project p LEFT JOIN intermediate.int_asana__project_health_indicators h ON p.project_id=h.project_id GROUP BY p.team_id,p.team_name)","FROM staging.stg_asana__project p LEFT JOIN staging.stg_asana__team team ON p.team_id::VARCHAR=team.team_id LEFT JOIN intermediate.int_asana__project_health_indicators h ON p.project_id=h.project_id GROUP BY p.team_id,team.team_name)")
```
event 41 / message

```text
'marts':'asana__user asana__team asana__tag asana__project asana__task asana__daily_metrics asana__user_performance_dashboard asana__project_analytics asana__team_efficiency_metrics asana__task_lifecycle_analysis'.split()}
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-008.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-008/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__team_efficiency_metrics.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/sql/marts/asana__team_efficiency_metrics.sql`
- S6: `records/006_contract_impl-008.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/result.md`
- S10: `data/021_packages_work/021_impl-008_asana__team_efficiency_metrics/021_impl-008_asana__team_efficiency_metrics.json`
- S11: `data/005_cs_work/impl-008/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/asana.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions`
