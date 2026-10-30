# impl-008 | marts | asana__project_analytics | 差异：S1；日期 2025-10-12

## 契约完整原文

S3:1071–1214

```yaml
    - name: asana__project_analytics
      description: Executive-level Asana project analytics with health, workload, schedule, scoring, ROI, maturity, priorities, and ranks; only valid projects are output
      grain: One row per project_id (valid records only)
      source_models:
      - staging.stg_asana__project
      - staging.stg_asana__team
      - intermediate.int_asana__project_health_indicators
      business_logic: 'Build analytics in stages: - Filter projects to those with a non-null project_name. - Join team details by team_id and health indicators by project_id. - Derive schedule metrics: - planned_duration_days: whole days from start (created_at) to deadline if a deadline exists; otherwise null. - elapsed_days: whole days from start to today. - remaining_days: whole days from today to deadline if a deadline exists; otherwise null. - completion_rate_per_day: completion_percentage divided by elapsed_days, rounded to 4 decimals; null if elapsed_days is not positive. - Resource/workload metrics: - avg_tasks_per_assignee: if total_tasks > 0, divide total_tasks by max(1, unique_assignees) and round to 2 decimals; if unique_assignees is null in this case, the result is null; otherwise 0. - team_size_category by unique_assignees: 0 → no_team; 1 → solo_project; 2–3 → small_team; 4–7 → medium_team; 8–15 → large_team; else enterprise_team (null maps to enterprise_team). - project_size_category by total_tasks: 0–5 → micro_project; 6–20 → small_project; 21–50 → medium_project; 51–100 → large_project; else enterprise_project (null maps to enterprise_project). - estimated_days_to_completion: when completion_rate_per_day > 0 and completion_percentage < 100, (100 − completion_percentage) divided by completion_rate_per_day, rounded up to whole days; otherwise null. - schedule_forecast: if completion_rate_per_day > 0 and completion_percentage < 100, compare estimated_days_to_completion to remaining_days: ≤ remaining_days → on_schedule; ≤ remaining_days × 1.2 → slight_delay; ≤ remaining_days × 1.5 → moderate_delay; else significant_delay. Otherwise, if completion_percentage = 100 → completed; else if remaining_days < 0 → overdue; else uncertain. - Performance scoring: - efficiency_score (0–25): by completion_rate_per_day thresholds, inclusive bands: ≥2.0 → 25; ≥1.0 → 20; ≥0.5 → 15; ≥0.2 → 10; else 5; then constrained to 0–25. - time_management_score (0–25): by schedule_forecast mapping: on_schedule 25; slight_delay 20; moderate_delay 15; significant_delay 10; overdue 5; else 12; constrained to 0–25. - collaboration_score (0–25): by avg_tasks_per_assignee and team size: if avg between 3 and 8 (inclusive) and unique_assignees ≥ 2 → 25; if avg between 2 and 12 → 20; if avg between 1 and 15 → 15; if unique_assignees ≥ 1 → 10; else 5; constrained to 0–25. - complexity_factor: enterprise_project 1.2; large_project 1.1; medium_project 1.0; small_project 0.9; micro_project 0.8. - Final analytics: - comprehensive_project_score: weighted sum of health (40%), efficiency (25%), time (20%), and collaboration (15%), multiplied by complexity_factor and rounded to 2 decimals. - roi_efficiency_ratio: if unique_assignees > 0 and elapsed_days > 0, compute (completion_percentage × quality_percentage ÷ 100) divided by (unique_assignees × elapsed_days ÷ 30), rounded to 3 decimals; otherwise 0. - project_maturity_phase by elapsed_days: ≤7 → startup_phase; ≤30 → early_development; ≤90 → active_development; ≤180 → mature_development; ≤365 → long_term_project; else legacy_project (null maps to legacy_project). - success_factors: concatenate, in this order, any applicable tokens separated by ", ": high_health (overall_health_score ≥ 80), strong_progress (completion_percentage ≥ 75), quality_delivery (quality_percentage ≥ 70), low_risk (risk_percentage ≤ 15), good_collaboration (unique_assignees ≥ 3), on_time (schedule_forecast is on_schedule or completed); remove any trailing comma and space; empty string if none. - improvement_opportunities: concatenate, in this order, any applicable tokens separated by ", ": improve_health (overall_health_score < 60), accelerate_progress (completion_percentage < 50 and elapsed_days > 30), enhance_quality (quality_percentage < 60), reduce_risks (risk_percentage > 25), balance_workload (avg_tasks_per_assignee > 10), address_delays (schedule_forecast is moderate_delay or significant_delay), expand_team (unique_assignees < 2 and total_tasks > 10); remove any trailing comma and space; empty string if none. - management_priority: immediate_attention if risk_level is high_risk or schedule_forecast is overdue; else high_priority if overall_health_score < 50 or schedule_forecast is significant_delay; else monitor if overall_health_score ≥ 80 and schedule_forecast is on_schedule; otherwise regular_review. - Validation and ranking: - is_valid_record is true only when: project_id and project_name are present; comprehensive_project_score is between 0 and 120 inclusive; completion_percentage, quality_percentage, and risk_percentage are each between 0 and 100 inclusive; total_tasks and completed_tasks are not negative; and completed_tasks does not exceed total_tasks. - Ranks are computed across all rows before filtering: overall_performance_rank by comprehensive_project_score descending; health_rank by overall_health_score descending; progress_rank by completion_percentage descending; efficiency_rank by roi_efficiency_ratio descending. Ties share the same rank with gaps. - Output: return only rows where is_valid_record is true, ordered by comprehensive_project_score descending, then overall_health_score descending, then project_id ascending.'
      columns:
      - name: project_id
        data_type: VARCHAR
        description: Project identifier from Asana; grouping key with at most one output row per project_id
      - name: project_name
        data_type: VARCHAR
        description: Project name from source; rows with null project_name are excluded
      - name: team_id
        data_type: BIGINT
        description: Team identifier associated with the project; null if no matching team
      - name: team_name
        data_type: VARCHAR
        description: Team name joined by team_id; null if no match
      - name: project_owner
        data_type: VARCHAR
        description: Owner user identifier from the project record (no user lookup applied)
      - name: project_status
        data_type: VARCHAR
        description: Current project status from the source (passthrough)
      - name: project_start_date
        data_type: TIMESTAMP
        description: Project start timestamp from created_at
      - name: project_deadline
        data_type: TIMESTAMP
        description: Project due date timestamp; may be null
      - name: total_tasks
        data_type: BIGINT
        description: Total task count from health indicators; must be nonnegative for validity
      - name: completed_tasks
        data_type: BIGINT
        description: Completed task count from health indicators; must be between 0 and total_tasks
      - name: active_tasks
        data_type: BIGINT
        description: Active or in-progress task count from health indicators; may be null
      - name: overdue_tasks
        data_type: BIGINT
        description: Past-due, incomplete task count from health indicators; may be null
      - name: unique_assignees
        data_type: BIGINT
        description: Distinct assignee count from health indicators; 0 means no assignees; may be null
      - name: completion_percentage
        data_type: DOUBLE
        description: Percent of tasks completed from health indicators; expected 0–100 for validity
      - name: quality_percentage
        data_type: DOUBLE
        description: Percent meeting quality criteria from health indicators; expected 0–100 for validity
      - name: risk_percentage
        data_type: DOUBLE
        description: Percent flagged as risky from health indicators; expected 0–100 for validity
      - name: overall_health_score
        data_type: INTEGER
        description: Overall health score from health indicators used in composite scoring
      - name: health_grade
        data_type: VARCHAR
        description: Health grade label from health indicators
      - name: risk_level
        data_type: VARCHAR
        description: Risk level label from health indicators (e.g., high_risk)
      - name: project_forecast
        data_type: VARCHAR
        description: Forecast label from health indicators, distinct from schedule_forecast
      - name: focus_areas
        data_type: VARCHAR
        description: Focus areas text from health indicators
      - name: planned_duration_days
        data_type: BIGINT
        description: Whole days from start to deadline; null if no deadline
      - name: elapsed_days
        data_type: BIGINT
        description: Whole days since start; null if start date is null
      - name: remaining_days
        data_type: BIGINT
        description: Whole days until deadline; negative if overdue; null if no deadline
      - name: completion_rate_per_day
        data_type: DOUBLE
        description: Completion percentage per day since start, rounded to 4 decimals; null if elapsed_days is not positive
      - name: avg_tasks_per_assignee
        data_type: DOUBLE
        description: If total_tasks > 0, total_tasks divided by max(1, unique_assignees) rounded to 2 decimals (null if unique_assignees is null); otherwise 0
      - name: team_size_category
        data_type: VARCHAR
        description: 'Team size bucket by unique_assignees: no_team, solo_project, small_team, medium_team, large_team, or enterprise_team (null maps to enterprise_team)'
      - name: project_size_category
        data_type: VARCHAR
        description: 'Project size bucket by total_tasks: micro_project, small_project, medium_project, large_project, or enterprise_project (null maps to enterprise_project)'
      - name: estimated_days_to_completion
        data_type: DOUBLE
        description: Remaining percent divided by daily completion rate and rounded up when rate > 0 and completion < 100; otherwise null
      - name: schedule_forecast
        data_type: VARCHAR
        description: 'Outlook: on_schedule, slight_delay, moderate_delay, significant_delay, completed, overdue, or uncertain based on thresholds and gating rules'
      - name: efficiency_score
        data_type: INTEGER
        description: 0–25 score from completion_rate_per_day thresholds, constrained to 0–25
      - name: time_management_score
        data_type: INTEGER
        description: 0–25 score from schedule_forecast mapping, constrained to 0–25
      - name: collaboration_score
        data_type: INTEGER
        description: 0–25 score from avg_tasks_per_assignee and team size, constrained to 0–25
      - name: complexity_factor
        data_type: DECIMAL(2,1)
        description: 'Multiplier by project_size_category: micro 0.8, small 0.9, medium 1.0, large 1.1, enterprise 1.2'
      - name: comprehensive_project_score
        data_type: DECIMAL(18,2)
        description: Weighted health (40%), efficiency (25%), time (20%), and collaboration (15%) scaled by complexity and rounded to 2 decimals
      - name: roi_efficiency_ratio
        data_type: DOUBLE
        description: Efficiency of progress and quality relative to team size and time, rounded to 3 decimals; 0 when team size or elapsed_days is not positive
      - name: project_maturity_phase
        data_type: VARCHAR
        description: 'Lifecycle phase by elapsed_days: startup_phase, early_development, active_development, mature_development, long_term_project, or legacy_project'
      - name: success_factors
        data_type: VARCHAR
        description: Comma-separated tokens for strong signals in a fixed order; trailing comma and space removed; empty string if none
      - name: improvement_opportunities
        data_type: VARCHAR
        description: Comma-separated tokens for weak signals in a fixed order; trailing comma and space removed; empty string if none
      - name: management_priority
        data_type: VARCHAR
        description: 'Priority recommendation: immediate_attention, high_priority, monitor, or regular_review based on risk, health, and schedule'
      - name: is_valid_record
        data_type: BOOLEAN
        description: True only when all validation checks pass; output includes only true rows
      - name: overall_performance_rank
        data_type: BIGINT
        description: Rank by comprehensive_project_score descending across all rows before filtering; ties share rank with gaps
      - name: health_rank
        data_type: BIGINT
        description: Rank by overall_health_score descending across all rows before filtering; ties share rank with gaps
      - name: progress_rank
        data_type: BIGINT
        description: Rank by completion_percentage descending across all rows before filtering; ties share rank with gaps
      - name: efficiency_rank
        data_type: BIGINT
        description: Rank by roi_efficiency_ratio descending across all rows before filtering; ties share rank with gaps
```

## agent 最终 SQL

S4

```sql
WITH base AS (
 SELECT p.project_id,p.project_name,p.team_id,t.team_name,p.owner_user_id project_owner,p.current_status project_status,p.created_at project_start_date,p.due_date project_deadline,
 h.total_tasks,h.completed_tasks,h.active_tasks,h.overdue_tasks,h.unique_assignees,h.completion_percentage,h.quality_percentage,h.risk_percentage,h.overall_health_score,h.health_grade,h.risk_level,h.project_forecast,h.focus_areas,
 DATE_DIFF('day',p.created_at::DATE,p.due_date::DATE)::BIGINT planned_duration_days,DATE_DIFF('day',p.created_at::DATE,CURRENT_DATE)::BIGINT elapsed_days,DATE_DIFF('day',CURRENT_DATE,p.due_date::DATE)::BIGINT remaining_days
 FROM staging.stg_asana__project p LEFT JOIN staging.stg_asana__team t ON p.team_id::VARCHAR=t.team_id LEFT JOIN intermediate.int_asana__project_health_indicators h ON p.project_id=h.project_id
 WHERE p.project_name IS NOT NULL
), derived AS (
 SELECT *,ROUND(completion_percentage/NULLIF(elapsed_days,0),4) completion_rate_per_day,
 CASE WHEN total_tasks>0 AND unique_assignees IS NOT NULL THEN ROUND(total_tasks::DOUBLE/GREATEST(1,unique_assignees),2) WHEN total_tasks>0 THEN NULL ELSE 0 END avg_tasks_per_assignee,
 CASE WHEN unique_assignees=0 THEN 'no_team' WHEN unique_assignees=1 THEN 'solo_project' WHEN unique_assignees<=3 THEN 'small_team' WHEN unique_assignees<=7 THEN 'medium_team' WHEN unique_assignees<=15 THEN 'large_team' ELSE 'enterprise_team' END team_size_category,
 CASE WHEN total_tasks<=5 THEN 'micro_project' WHEN total_tasks<=20 THEN 'small_project' WHEN total_tasks<=50 THEN 'medium_project' WHEN total_tasks<=100 THEN 'large_project' ELSE 'enterprise_project' END project_size_category
 FROM base
), scored AS (
 SELECT *,CASE WHEN completion_rate_per_day>0 AND completion_percentage<100 THEN CEIL((100-completion_percentage)/completion_rate_per_day) END estimated_days_to_completion,
 CASE WHEN completion_rate_per_day>0 AND completion_percentage<100 THEN CASE WHEN CEIL((100-completion_percentage)/completion_rate_per_day)<=remaining_days THEN 'on_schedule' WHEN CEIL((100-completion_percentage)/completion_rate_per_day)<=remaining_days*1.2 THEN 'slight_delay' WHEN CEIL((100-completion_percentage)/completion_rate_per_day)<=remaining_days*1.5 THEN 'moderate_delay' ELSE 'significant_delay' END WHEN completion_percentage=100 THEN 'completed' WHEN remaining_days<0 THEN 'overdue' ELSE 'uncertain' END schedule_forecast,
 CASE WHEN completion_rate_per_day>=2 THEN 25 WHEN completion_rate_per_day>=1 THEN 20 WHEN completion_rate_per_day>=.5 THEN 15 WHEN completion_rate_per_day>=.2 THEN 10 ELSE 5 END efficiency_score,
 CASE WHEN completion_percentage=100 THEN 25 WHEN remaining_days<0 THEN 5 ELSE 12 END time_management_score,
 CASE WHEN avg_tasks_per_assignee BETWEEN 3 AND 8 AND unique_assignees>=2 THEN 25 WHEN avg_tasks_per_assignee BETWEEN 2 AND 12 THEN 20 WHEN avg_tasks_per_assignee BETWEEN 1 AND 15 THEN 15 WHEN unique_assignees>=1 THEN 10 ELSE 5 END collaboration_score,
 CASE project_size_category WHEN 'enterprise_project' THEN 1.2 WHEN 'large_project' THEN 1.1 WHEN 'medium_project' THEN 1.0 WHEN 'small_project' THEN .9 ELSE .8 END::DECIMAL(2,1) complexity_factor
 FROM derived
), totals AS (
 SELECT *,ROUND((overall_health_score*.4+efficiency_score*.25+time_management_score*.2+collaboration_score*.15)*complexity_factor,2)::DECIMAL(18,2) comprehensive_project_score,
 CASE WHEN unique_assignees>0 AND elapsed_days>0 THEN ROUND((completion_percentage*quality_percentage/100.0)/(unique_assignees*elapsed_days/30.0),3) ELSE 0 END roi_efficiency_ratio,
 CASE WHEN elapsed_days<=7 THEN 'startup_phase' WHEN elapsed_days<=30 THEN 'early_development' WHEN elapsed_days<=90 THEN 'active_development' WHEN elapsed_days<=180 THEN 'mature_development' WHEN elapsed_days<=365 THEN 'long_term_project' ELSE 'legacy_project' END project_maturity_phase
 FROM scored
), ranked AS (
 SELECT *,concat_ws(', ',CASE WHEN overall_health_score>=80 THEN 'high_health' END,CASE WHEN completion_percentage>=75 THEN 'strong_progress' END,CASE WHEN quality_percentage>=70 THEN 'quality_delivery' END,CASE WHEN risk_percentage<=15 THEN 'low_risk' END,CASE WHEN unique_assignees>=3 THEN 'good_collaboration' END,CASE WHEN schedule_forecast IN ('on_schedule','completed') THEN 'on_time' END) success_factors,
 concat_ws(', ',CASE WHEN overall_health_score<60 THEN 'improve_health' END,CASE WHEN completion_percentage<50 AND elapsed_days>30 THEN 'accelerate_progress' END,CASE WHEN quality_percentage<60 THEN 'enhance_quality' END,CASE WHEN risk_percentage>25 THEN 'reduce_risks' END,CASE WHEN avg_tasks_per_assignee>10 THEN 'balance_workload' END,CASE WHEN schedule_forecast IN ('moderate_delay','significant_delay') THEN 'address_delays' END,CASE WHEN unique_assignees<2 AND total_tasks>10 THEN 'expand_team' END) improvement_opportunities,
 CASE WHEN risk_level='high_risk' OR schedule_forecast='overdue' THEN 'immediate_attention' WHEN overall_health_score<50 OR schedule_forecast='significant_delay' THEN 'high_priority' WHEN overall_health_score>=80 AND schedule_forecast='on_schedule' THEN 'monitor' ELSE 'regular_review' END management_priority
 FROM totals
), final AS (SELECT *,RANK() OVER(ORDER BY comprehensive_project_score DESC) overall_performance_rank,RANK() OVER(ORDER BY overall_health_score DESC) health_rank,RANK() OVER(ORDER BY completion_percentage DESC) progress_rank,RANK() OVER(ORDER BY roi_efficiency_ratio DESC) efficiency_rank,
 (project_id IS NOT NULL AND project_name IS NOT NULL AND comprehensive_project_score BETWEEN 0 AND 120 AND completion_percentage BETWEEN 0 AND 100 AND quality_percentage BETWEEN 0 AND 100 AND risk_percentage BETWEEN 0 AND 100 AND total_tasks>=0 AND completed_tasks>=0 AND completed_tasks<=total_tasks) is_valid_record FROM ranked)
SELECT * FROM final WHERE is_valid_record ORDER BY comprehensive_project_score DESC,overall_health_score DESC,project_id
```

## gold SQL（仅供定位差异）

S5

```sql
-- Project Analytics Dashboard
-- Project Analysis Summary - Comprehensive project health, resource allocation, risk assessment and performance forecasting

with project_base as (
    select *
    from staging.stg_asana__project
    where project_name is not null
),

team_base as (
    select *
    from staging.stg_asana__team
),

project_health as (
    select *
    from intermediate.int_asana__project_health_indicators
),

user_performance as (
    select *
    from staging.stg_asana__user
),

-- Project team configuration analysis
project_team_analysis as (
    select 
        p.project_id,
        p.project_name,
        p.team_id,
        t.team_name,
        p.owner_user_id as project_owner,
        p.current_status as project_status,
        p.created_at as project_start_date,
        p.due_date as project_deadline,
        
        -- Get details from health metrics
        ph.total_tasks,
        ph.completed_tasks,
        ph.active_tasks,
        ph.overdue_tasks,
        ph.unique_assignees,
        ph.completion_percentage,
        ph.quality_percentage,
        ph.risk_percentage,
        ph.overall_health_score,
        ph.health_grade,
        ph.risk_level,
        ph.project_forecast,
        ph.focus_areas,
        
        -- Project duration analysis
        case 
            when p.due_date is not null then 
                date_diff('day', p.created_at, p.due_date)
            else null
        end as planned_duration_days,
        
        date_diff('day', p.created_at, current_date) as elapsed_days,
        
        case 
            when p.due_date is not null then 
                date_diff('day', current_date, p.due_date)
            else null
        end as remaining_days,
        
        -- Progress rate calculation
        case 
            when date_diff('day', p.created_at, current_date) > 0 then
                round((ph.completion_percentage / date_diff('day', p.created_at, current_date)), 4)
            else null
        end as completion_rate_per_day
        
    from project_base p
    left join team_base t on p.team_id = t.team_id
    left join project_health ph on p.project_id = ph.project_id
),

-- Project resource and workload analysis
project_resource_metrics as (
    select 
        pta.*,
        
        -- Resource allocation indicators
        case 
            when pta.total_tasks > 0 then
                round((pta.total_tasks * 1.0 / greatest(1, pta.unique_assignees)), 2)
            else 0
        end as avg_tasks_per_assignee,
        
        -- Team size fit
        case 
            when pta.unique_assignees = 0 then 'no_team'
            when pta.unique_assignees = 1 then 'solo_project'
            when pta.unique_assignees <= 3 then 'small_team'
            when pta.unique_assignees <= 7 then 'medium_team'
            when pta.unique_assignees <= 15 then 'large_team'
            else 'enterprise_team'
        end as team_size_category,
        
        -- Project size classification
        case 
            when pta.total_tasks <= 5 then 'micro_project'
            when pta.total_tasks <= 20 then 'small_project'
            when pta.total_tasks <= 50 then 'medium_project'
            when pta.total_tasks <= 100 then 'large_project'
            else 'enterprise_project'
        end as project_size_category,
        
        -- Estimated completion time
        case 
            when pta.completion_rate_per_day > 0 and pta.completion_percentage < 100 then
                ceil((100 - pta.completion_percentage) / pta.completion_rate_per_day)
            else null
        end as estimated_days_to_completion,
        
        -- deadline forecast
        case 
            when pta.completion_rate_per_day > 0 and pta.completion_percentage < 100 then
                case 
                    when ceil((100 - pta.completion_percentage) / pta.completion_rate_per_day) <= pta.remaining_days then 'on_schedule'
                    when ceil((100 - pta.completion_percentage) / pta.completion_rate_per_day) <= pta.remaining_days * 1.2 then 'slight_delay'
                    when ceil((100 - pta.completion_percentage) / pta.completion_rate_per_day) <= pta.remaining_days * 1.5 then 'moderate_delay'
                    else 'significant_delay'
                end
            when pta.completion_percentage = 100 then 'completed'
            when pta.remaining_days < 0 then 'overdue'
            else 'uncertain'
        end as schedule_forecast
        
    from project_team_analysis pta
),

-- Project performance scoring and benchmarking
project_performance_scoring as (
    select 
        prm.*,
        
        -- Efficiency score (based on completion speed and resource utilization)
        least(25, greatest(0,
            case 
                when prm.completion_rate_per_day >= 2.0 then 25  -- Complete more than 2% every day
                when prm.completion_rate_per_day >= 1.0 then 20  -- Complete 1-2% every day
                when prm.completion_rate_per_day >= 0.5 then 15  -- Complete 0.5-1% every day
                when prm.completion_rate_per_day >= 0.2 then 10  -- Complete 0.2-0.5% every day
                else 5
            end
        )) as efficiency_score,
        
        -- Time management score (based on whether or not you stayed on schedule)
        least(25, greatest(0,
            case 
                when prm.schedule_forecast = 'on_schedule' then 25
                when prm.schedule_forecast = 'slight_delay' then 20
                when prm.schedule_forecast = 'moderate_delay' then 15
                when prm.schedule_forecast = 'significant_delay' then 10
                when prm.schedule_forecast = 'overdue' then 5
                else 12
            end
        )) as time_management_score,
        
        -- Team collaboration score (based on task assignment and team size)
        least(25, greatest(0,
            case 
                when prm.avg_tasks_per_assignee between 3 and 8 and prm.unique_assignees >= 2 then 25  -- ideal distribution
                when prm.avg_tasks_per_assignee between 2 and 12 then 20  -- good distribution
                when prm.avg_tasks_per_assignee between 1 and 15 then 15  -- Acceptable allocation
                when prm.unique_assignees >= 1 then 10  -- basic allocation
                else 5  -- No allocation
            end
        )) as collaboration_score,
        
        -- Project complexity factor (adjustment factor that affects scoring)
        case 
            when prm.project_size_category = 'enterprise_project' then 1.2
            when prm.project_size_category = 'large_project' then 1.1
            when prm.project_size_category = 'medium_project' then 1.0
            when prm.project_size_category = 'small_project' then 0.9
            else 0.8
        end as complexity_factor
        
    from project_resource_metrics prm
),

-- Final ratings and rankings
final_project_analytics as (
    select 
        pps.*,
        
        -- Comprehensive project rating (taking into account complexity adjustments)
        round(
            ((pps.overall_health_score * 0.4) +  -- Health weight 40%
             (pps.efficiency_score * 0.25) +    -- Efficiency weight 25%
             (pps.time_management_score * 0.2) + -- Time management weights 20%
             (pps.collaboration_score * 0.15))   -- Collaboration weight 15%
            * pps.complexity_factor, 2
        ) as comprehensive_project_score,
        
        -- ROI assessment (based on quality of completion and resource investment)
        case 
            when pps.unique_assignees > 0 and pps.elapsed_days > 0 then
                round(
                    (pps.completion_percentage * pps.quality_percentage / 100.0) /
                    (pps.unique_assignees * pps.elapsed_days / 30.0), 3
                )
            else 0
        end as roi_efficiency_ratio,
        
        -- Project maturity assessment
        case 
            when pps.elapsed_days <= 7 then 'startup_phase'
            when pps.elapsed_days <= 30 then 'early_development'
            when pps.elapsed_days <= 90 then 'active_development'
            when pps.elapsed_days <= 180 then 'mature_development'
            when pps.elapsed_days <= 365 then 'long_term_project'
            else 'legacy_project'
        end as project_maturity_phase,
        
        -- critical success factors
        trim(
            case when pps.overall_health_score >= 80 then 'high_health, ' else '' end ||
            case when pps.completion_percentage >= 75 then 'strong_progress, ' else '' end ||
            case when pps.quality_percentage >= 70 then 'quality_delivery, ' else '' end ||
            case when pps.risk_percentage <= 15 then 'low_risk, ' else '' end ||
            case when pps.unique_assignees >= 3 then 'good_collaboration, ' else '' end ||
            case when pps.schedule_forecast in ('on_schedule', 'completed') then 'on_time, ' else '' end,
            ', '
        ) as success_factors,
        
        -- Improve opportunity identification
        trim(
            case when pps.overall_health_score < 60 then 'improve_health, ' else '' end ||
            case when pps.completion_percentage < 50 and pps.elapsed_days > 30 then 'accelerate_progress, ' else '' end ||
            case when pps.quality_percentage < 60 then 'enhance_quality, ' else '' end ||
            case when pps.risk_percentage > 25 then 'reduce_risks, ' else '' end ||
            case when pps.avg_tasks_per_assignee > 10 then 'balance_workload, ' else '' end ||
            case when pps.schedule_forecast in ('moderate_delay', 'significant_delay') then 'address_delays, ' else '' end ||
            case when pps.unique_assignees < 2 and pps.total_tasks > 10 then 'expand_team, ' else '' end,
            ', '
        ) as improvement_opportunities,
        
        -- Project priority recommendations
        case 
            when pps.risk_level = 'high_risk' or pps.schedule_forecast = 'overdue' then 'immediate_attention'
            when pps.overall_health_score < 50 or pps.schedule_forecast = 'significant_delay' then 'high_priority'
            when pps.overall_health_score >= 80 and pps.schedule_forecast = 'on_schedule' then 'monitor'
            else 'regular_review'
        end as management_priority
        
    from project_performance_scoring pps
),

-- Data quality verification and final output
validated_analytics as (
    select 
        *,
        
        -- Data quality verification
        case 
            when project_id is null or project_name is null then false
            when comprehensive_project_score < 0 or comprehensive_project_score > 120 then false  -- Allows complexity adjustment over 100
            when completion_percentage < 0 or completion_percentage > 100 then false
            when quality_percentage < 0 or quality_percentage > 100 then false
            when risk_percentage < 0 or risk_percentage > 100 then false
            when total_tasks < 0 or completed_tasks < 0 then false
            when completed_tasks > total_tasks then false
            else true
        end as is_valid_record,
        
        -- Global ranking
        rank() over (order by comprehensive_project_score desc) as overall_performance_rank,
        rank() over (order by overall_health_score desc) as health_rank,
        rank() over (order by completion_percentage desc) as progress_rank,
        rank() over (order by roi_efficiency_ratio desc) as efficiency_rank
        
    from final_project_analytics
)

select *
from validated_analytics
where is_valid_record = true
order by comprehensive_project_score desc, overall_health_score desc, project_id
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 495 | 495 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"project_id":"1026191027708","team_id":"6345774049957"}</code> |
| K2 | <code>{"project_id":"1037512360527","team_id":"9998174459982"}</code> |
| K3 | <code>{"project_id":"1086088130693","team_id":"8508131138262"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| project_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| team_id | 0 | 0 | 0 | BIGINT | BIGINT |
| comprehensive_project_score | 472 | 472 | 472 | DECIMAL(18,2) | DECIMAL(18,2) |
| efficiency_rank | 0 | 0 | 0 | BIGINT | BIGINT |
| focus_areas | 0 | 0 | 0 | VARCHAR | VARCHAR |
| health_grade | 0 | 0 | 0 | VARCHAR | VARCHAR |
| improvement_opportunities | 0 | 0 | 0 | VARCHAR | VARCHAR |
| is_valid_record | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| management_priority | 0 | 0 | 0 | VARCHAR | VARCHAR |
| overall_health_score | 0 | 0 | 0 | INTEGER | INTEGER |
| overdue_tasks | 0 | 0 | 0 | BIGINT | BIGINT |
| planned_duration_days | 0 | 0 | 0 | BIGINT | BIGINT |
| project_deadline | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| project_forecast | 0 | 0 | 0 | VARCHAR | VARCHAR |
| project_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| project_owner | 0 | 0 | 0 | VARCHAR | VARCHAR |
| project_start_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| project_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| risk_level | 0 | 0 | 0 | VARCHAR | VARCHAR |
| schedule_forecast | 0 | 0 | 0 | VARCHAR | VARCHAR |
| success_factors | 0 | 0 | 0 | VARCHAR | VARCHAR |
| team_name | 0 | 0 | 0 | VARCHAR | VARCHAR |

comprehensive_project_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 20.60 | 21.40 |
| K2 | 26.78 | 27.68 |
| K3 | 22.20 | 23.00 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>7列；[{"column":"overdue_tasks","value":"0"},{"column":"quality_percentage","value":"0.0"},{"column":"efficiency_score","value":"5"}]</code> |
| A4_equal_columns | <code>1组；[{"columns":["quality_percentage","roi_efficiency_ratio"],"nonnull_equal_rows":472,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>1组；[{"columns":["quality_percentage","roi_efficiency_ratio"],"nonnull_equal_rows":472,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| C9_agent_runtime_text | <code>S4:4 CURRENT_DATE；命中数=2</code> |
| C9_gold_runtime_text | <code>S5:59 current_date；命中数=4</code> |
| C9_contract_runtime_text | <code>S3:1078 today；命中数=2</code> |

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
| 37 | run | <code>python - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('asana.duckdb',read_only=True)<br>for sch in ['staging','intermediate','mart']:<br> print('\n',sch)<br> for (t,) in c.execute(f"select table_name from information</code> | 1027 | true | false |
| 41 | run | <code>grep -R -nE ';[[:space:]]*$&#124;ref\(' sql &#124;&#124; true; python - &lt;&lt;'PY'<br>from pathlib import Path<br>expected={<br>'staging':'stg_asana__user stg_asana__team stg_asana__project stg_asana__task stg_asana__section stg</code> | 105 | false | false |

### agent action 的 thought/message 命中原句

event 25 / message

```text
'asana__project_analytics':'''WITH base AS (
```
event 41 / message

```text
'marts':'asana__user asana__team asana__tag asana__project asana__task asana__daily_metrics asana__user_performance_dashboard asana__project_analytics asana__team_efficiency_metrics asana__task_lifecycle_analysis'.split()}
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/011_table_alignment.jsonl`
- S2: `records/011_alignment_impl-008.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-008/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__project_analytics.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/sql/marts/asana__project_analytics.sql`
- S6: `records/006_contract_impl-008.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/result.md`
- S10: `data/021_packages_work/021_impl-008_asana__project_analytics/021_impl-008_asana__project_analytics.json`
- S11: `data/011_agent_alignment/impl-008_attempt_01/asana__project_analytics_2025-10-12.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/asana.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions`
