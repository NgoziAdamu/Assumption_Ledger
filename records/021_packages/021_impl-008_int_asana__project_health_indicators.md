# impl-008 | intermediate | int_asana__project_health_indicators | 差异：S1；日期 2025-10-12

## 契约完整原文

S3:295–445

```yaml
    - name: int_asana__project_health_indicators
      description: Project-level health indicators derived from Asana projects and tasks with validated scores, percentages, and risk/forecast labels
      grain: One row per project_id (validated records only)
      source_models:
      - staging.stg_asana__project (project_id, project_name, created_at, due_date, owner_user_id, current_status, team_id)
      - staging.stg_asana__task (task_id, created_at, completed_at, is_completed, assignee_user_id)
      - staging.stg_asana__project_task (project_id, task_id)
      - intermediate.int_asana__task_performance_metrics (task_id, task_status_category, performance_grade, urgency_score, health_score, complexity_score, days_open, response_time_days, delay_days)
      business_logic: '1) Project and task filters: - project_base: projects where project_name and created_at are not null. - task_base: tasks where created_at is not null. - project_task_relation: all project-task links. - task_performance: all task performance metrics. 2) Project_task_stats (one row per project): - Left join p→ptr on project_id, then to t on task_id, then to tp on task_id. - Distinct task counts by project: • total_tasks: all linked tasks. • completed_tasks: tasks with is_completed = true. • active_tasks: tasks with is_completed = false. • assigned_tasks: tasks with non-null assignee_user_id. • unassigned_tasks: tasks with is_completed = false and null assignee_user_id. - Risk counts (distinct tasks): overdue (status_category=''overdue''), poor performance (grade=''poor''), high urgency (urgency_score ≥ 4), delayed (delay_days > 0). - Quality: • quality_tasks: performance_grade in {excellent, good}. • Averages: health_score, complexity_score (NULLs ignored). - Time metrics: • avg_completion_time_days: avg days_open over completed tasks; NULL if none. • avg_response_time_days: avg response_time_days; NULLs ignored. • max_task_age_days: max days_open; NULL if none. • avg_delay_days: avg delay_days; includes zeros; NULLs ignored. - Collaboration/recency: • unique_assignees: distinct assignee_user_id (non-null). • recent_task_creation: tasks created within the last 7 days (relative to current_date). • recent_task_completion: tasks completed within the last 7 days (relative to current_date). - Also select project attributes: id, name, created_at, due_date, owner_user_id, current_status, team_id. 3) project_health_metrics: - Percentages rounded to 2 decimals; when denominator is 0, set to 0: • completion_percentage = completed_tasks / total_tasks * 100. • assignment_percentage = assigned_tasks / total_tasks * 100. • overdue_percentage = overdue_tasks / total_tasks * 100. • quality_percentage = quality_tasks / completed_tasks * 100. • risk_percentage = (overdue + poor_performance + delayed) / total_tasks * 100 (may exceed 100 when categories overlap). • activity_percentage = (recent_task_creation + recent_task_completion) / total_tasks * 100 (may exceed 100 when both occur for the same task). - project_age_days = days from project_created_at to current_date. - deadline_status: no_deadline if due_date is null; on_time if due_date > today; due_today if equal; else overdue. - days_to_deadline: days from today to due_date; negative if past due; NULL if no due date. 4) project_health_scores (each clamped to [0,25]): - progress_score by completion_percentage: ≥90→25; ≥75→20; ≥50→15; ≥25→10; else 5. - quality_score by quality_percentage: ≥90→25; ≥75→20; ≥60→15; ≥40→10; else 5. - risk_score by risk_percentage (lower is better): ≤5→25; ≤10→20; ≤20→15; ≤35→10; else 5. - resource_score by assignment_percentage (and diversity): ≥95 and unique_assignees ≥ 2→25; else ≥85→20; ≥70→15; ≥50→10; else 5. 5) final_health_assessment: - overall_health_score = progress_score + quality_score + risk_score + resource_score (0–100). - health_grade: ≥90 excellent; ≥75 good; ≥60 fair; ≥40 poor; else critical. - risk_level (top-down): high_risk if risk_percentage ≥50 or overdue_percentage ≥30; else medium_risk if risk_percentage ≥25 or overdue_percentage ≥15; else low_risk if risk_percentage ≥10 or overdue_percentage ≥5; else minimal_risk. - project_forecast (top-down): overdue if deadline_status=''overdue''; else at_risk if risk_percentage ≥40 and days_to_deadline ≤ 7; else on_track if completion_percentage ≥75 and risk_percentage ≤15; else progressing if completion_percentage ≥50 and risk_percentage ≤25; else slow_progress if completion_percentage ≥25; else stalled. - focus_areas: concatenate applicable labels in fixed order [progress, quality, risk_management, resource_allocation, deadline_management, task_assignment] using ", "; include a label when its condition holds (score < 15; overdue_percentage > 20; unassigned_tasks > 30% of total); trim trailing delimiter; empty string if none. 6) validated_results and output: - is_valid_record = true only if project_id present; project_name non-empty; total_tasks ≥ 0; completed_tasks ≤ total_tasks; completion_percentage and quality_percentage in [0,100]; overall_health_score in [0,100]. - anomaly_flag: ''no_tasks'' if total_tasks=0; ''status_mismatch'' if completion_percentage=100 and project_status!=''completed''; ''excessive_overdue'' if overdue_percentage>50; ''poor_assignment'' if unassigned_tasks > 50% of total; ''stale_project'' if project_age_days>365 and completion_percentage<25; else ''normal''. - Final output filters to is_valid_record = true and orders by overall_health_score descending, then project_id.'
      columns:
      - name: project_id
        data_type: VARCHAR
        description: Asana project identifier; grouping key for one output row per project
        tests:
        - not_null
        - unique
      - name: project_name
        data_type: VARCHAR
        description: Project name as in Asana (non-null in input filter)
      - name: project_created_at
        data_type: TIMESTAMP
        description: Timestamp the project was created; used to compute project_age_days
      - name: project_due_date
        data_type: TIMESTAMP
        description: Project due date; drives deadline_status and days_to_deadline (can be NULL)
      - name: project_owner
        data_type: VARCHAR
        description: Owner user ID from project record
      - name: project_status
        data_type: VARCHAR
        description: Current project status from project record
      - name: team_id
        data_type: BIGINT
        description: Associated team identifier from project record
      - name: total_tasks
        data_type: BIGINT
        description: Distinct count of tasks linked to the project via project_task; includes all tasks
      - name: completed_tasks
        data_type: BIGINT
        description: Distinct count of project tasks where is_completed = true
      - name: active_tasks
        data_type: BIGINT
        description: Distinct count of project tasks where is_completed = false
      - name: assigned_tasks
        data_type: BIGINT
        description: Distinct count of project tasks with non-null assignee_user_id
      - name: unassigned_tasks
        data_type: BIGINT
        description: Distinct count of active project tasks (is_completed = false) with NULL assignee_user_id
      - name: overdue_tasks
        data_type: BIGINT
        description: Distinct count of project tasks where task_status_category = 'overdue'
      - name: poor_performance_tasks
        data_type: BIGINT
        description: Distinct count of project tasks where performance_grade = 'poor'
      - name: high_urgency_tasks
        data_type: BIGINT
        description: Distinct count of project tasks where urgency_score >= 4
      - name: delayed_tasks
        data_type: BIGINT
        description: Distinct count of project tasks where delay_days > 0
      - name: quality_tasks
        data_type: BIGINT
        description: Distinct count of project tasks where performance_grade in ('excellent','good')
      - name: avg_task_health_score
        data_type: DOUBLE
        description: Average of health_score across project tasks; simple mean; ignores NULLs
      - name: avg_task_complexity
        data_type: DOUBLE
        description: Average of complexity_score across project tasks; simple mean; ignores NULLs
      - name: avg_completion_time_days
        data_type: DOUBLE
        description: Average days_open for tasks with is_completed = true; NULL if none; ignores NULLs
      - name: avg_response_time_days
        data_type: DOUBLE
        description: Average response_time_days across project tasks; days; ignores NULLs
      - name: max_task_age_days
        data_type: BIGINT
        description: Maximum days_open across project tasks; days; NULL if no tasks
      - name: avg_delay_days
        data_type: DOUBLE
        description: Average delay_days across project tasks; days; includes zeros; ignores NULLs
      - name: unique_assignees
        data_type: BIGINT
        description: Distinct count of non-null assignee_user_id across project tasks
      - name: recent_task_creation
        data_type: BIGINT
        description: Distinct count of project tasks created in the last 7 days relative to current_date
      - name: recent_task_completion
        data_type: BIGINT
        description: Distinct count of project tasks completed in the last 7 days relative to current_date
      - name: completion_percentage
        data_type: DOUBLE
        description: Completed_tasks/Total_tasks*100 rounded to 2 decimals; 0 if total_tasks=0; bounded 0–100
      - name: assignment_percentage
        data_type: DOUBLE
        description: Assigned_tasks/Total_tasks*100 rounded to 2 decimals; 0 if total_tasks=0; bounded 0–100
      - name: overdue_percentage
        data_type: DOUBLE
        description: Overdue_tasks/Total_tasks*100 rounded to 2 decimals; 0 if total_tasks=0; bounded 0–100
      - name: quality_percentage
        data_type: DOUBLE
        description: Quality_tasks/Completed_tasks*100 rounded to 2 decimals; 0 if completed_tasks=0; bounded 0–100
      - name: risk_percentage
        data_type: DOUBLE
        description: (Overdue+Poor_performance+Delayed)/Total_tasks*100 rounded to 2 decimals; 0 if total_tasks=0; may exceed 100 when categories overlap
      - name: activity_percentage
        data_type: DOUBLE
        description: (Recent_creation+Recent_completion)/Total_tasks*100 rounded to 2 decimals; 0 if total_tasks=0; may exceed 100 when both occur for the same task
      - name: project_age_days
        data_type: BIGINT
        description: Days from project_created_at to current_date; non-negative integer
      - name: deadline_status
        data_type: VARCHAR
        description: One of 'no_deadline','on_time','due_today','overdue' based on project_due_date vs current_date
      - name: days_to_deadline
        data_type: BIGINT
        description: Days from current_date to project_due_date; negative if overdue; NULL if no due date
      - name: progress_score
        data_type: INTEGER
        description: 'Score 0–25 by completion_percentage: ≥90→25, ≥75→20, ≥50→15, ≥25→10, else 5'
      - name: quality_score
        data_type: INTEGER
        description: 'Score 0–25 by quality_percentage: ≥90→25, ≥75→20, ≥60→15, ≥40→10, else 5'
      - name: risk_score
        data_type: INTEGER
        description: 'Score 0–25 by risk_percentage (lower is better): ≤5→25, ≤10→20, ≤20→15, ≤35→10, else 5'
      - name: resource_score
        data_type: INTEGER
        description: 'Score 0–25 by assignment_percentage with bonus: ≥95 and unique_assignees≥2→25; else ≥85→20, ≥70→15, ≥50→10, else 5'
      - name: overall_health_score
        data_type: INTEGER
        description: Sum of progress_score + quality_score + risk_score + resource_score; range 0–100
      - name: health_grade
        data_type: VARCHAR
        description: 'Overall grade by overall_health_score: ≥90 excellent; ≥75 good; ≥60 fair; ≥40 poor; else critical'
      - name: risk_level
        data_type: VARCHAR
        description: Risk tier evaluated top-down using thresholds on risk_percentage and overdue_percentage
      - name: project_forecast
        data_type: VARCHAR
        description: 'Forecast label evaluated in order: overdue, at_risk, on_track, progressing, slow_progress, stalled based on status, risk, completion, and days_to_deadline'
      - name: focus_areas
        data_type: VARCHAR
        description: Comma+space separated labels from [progress, quality, risk_management, resource_allocation, deadline_management, task_assignment] included per rule; fixed order; no duplicates; empty string if none
      - name: is_valid_record
        data_type: BOOLEAN
        description: True if record passes validation rules (IDs present, counts consistent, percentages and overall score within bounds); final dataset filters to true
      - name: anomaly_flag
        data_type: VARCHAR
        description: One of 'normal','no_tasks','status_mismatch','excessive_overdue','poor_assignment','stale_project' based on anomaly rules
```

## agent 最终 SQL

S4

```sql
WITH project_base AS (
 SELECT * FROM staging.stg_asana__project WHERE project_name IS NOT NULL AND created_at IS NOT NULL
), joined AS (
 SELECT p.project_id,p.project_name,p.created_at AS project_created_at,p.due_date AS project_due_date,p.owner_user_id AS project_owner,p.current_status AS project_status,p.team_id,
        pt.task_id,t.is_completed,t.assignee_user_id,pm.task_status_category,pm.performance_grade,pm.urgency_score,pm.health_score,pm.complexity_score,pm.days_open,pm.response_time_days,pm.delay_days,t.created_at task_created_at,t.completed_at
 FROM project_base p LEFT JOIN staging.stg_asana__project_task rel ON p.project_id=rel.project_id::VARCHAR
 LEFT JOIN staging.stg_asana__task t ON rel.task_id::VARCHAR=t.task_id
 LEFT JOIN intermediate.int_asana__task_performance_metrics pm ON t.task_id=pm.task_id
 LEFT JOIN (SELECT project_id, task_id FROM staging.stg_asana__project_task) pt ON pt.project_id=rel.project_id AND pt.task_id=rel.task_id
), agg AS (
 SELECT project_id,project_name,project_created_at,project_due_date,project_owner,project_status,team_id,
 COUNT(DISTINCT task_id)::BIGINT total_tasks,COUNT(DISTINCT task_id) FILTER(WHERE is_completed)::BIGINT completed_tasks,
 COUNT(DISTINCT task_id) FILTER(WHERE is_completed=FALSE)::BIGINT active_tasks,
 COUNT(DISTINCT task_id) FILTER(WHERE assignee_user_id IS NOT NULL)::BIGINT assigned_tasks,
 COUNT(DISTINCT task_id) FILTER(WHERE is_completed=FALSE AND assignee_user_id IS NULL)::BIGINT unassigned_tasks,
 COUNT(DISTINCT task_id) FILTER(WHERE task_status_category='overdue')::BIGINT overdue_tasks,
 COUNT(DISTINCT task_id) FILTER(WHERE performance_grade='poor')::BIGINT poor_performance_tasks,
 COUNT(DISTINCT task_id) FILTER(WHERE urgency_score>=4)::BIGINT high_urgency_tasks,
 COUNT(DISTINCT task_id) FILTER(WHERE delay_days>0)::BIGINT delayed_tasks,
 COUNT(DISTINCT task_id) FILTER(WHERE performance_grade IN ('excellent','good'))::BIGINT quality_tasks,
 AVG(health_score) avg_task_health_score,AVG(complexity_score) avg_task_complexity,
 AVG(days_open) FILTER(WHERE is_completed) avg_completion_time_days,AVG(response_time_days) avg_response_time_days,
 MAX(days_open)::BIGINT max_task_age_days,AVG(delay_days) avg_delay_days,COUNT(DISTINCT assignee_user_id)::BIGINT unique_assignees,
 COUNT(DISTINCT task_id) FILTER(WHERE task_created_at>=CURRENT_DATE-INTERVAL '7 days')::BIGINT recent_task_creation,
 COUNT(DISTINCT task_id) FILTER(WHERE completed_at>=CURRENT_DATE-INTERVAL '7 days')::BIGINT recent_task_completion
 FROM joined GROUP BY ALL
), pct AS (
 SELECT *,ROUND(100.0*completed_tasks/NULLIF(total_tasks,0),2) completion_percentage,ROUND(100.0*assigned_tasks/NULLIF(total_tasks,0),2) assignment_percentage,
 ROUND(100.0*overdue_tasks/NULLIF(total_tasks,0),2) overdue_percentage,ROUND(100.0*quality_tasks/NULLIF(completed_tasks,0),2) quality_percentage,
 ROUND(100.0*(overdue_tasks+poor_performance_tasks+delayed_tasks)/NULLIF(total_tasks,0),2) risk_percentage,
 ROUND(100.0*(recent_task_creation+recent_task_completion)/NULLIF(total_tasks,0),2) activity_percentage,
 DATE_DIFF('day',project_created_at::DATE,CURRENT_DATE)::BIGINT project_age_days,
 CASE WHEN project_due_date IS NULL THEN 'no_deadline' WHEN project_due_date::DATE>CURRENT_DATE THEN 'on_time' WHEN project_due_date::DATE=CURRENT_DATE THEN 'due_today' ELSE 'overdue' END deadline_status,
 DATE_DIFF('day',CURRENT_DATE,project_due_date::DATE)::BIGINT days_to_deadline FROM agg
), scores AS (
 SELECT *,COALESCE(completion_percentage,0) cp,COALESCE(assignment_percentage,0) ap,COALESCE(overdue_percentage,0) op,COALESCE(quality_percentage,0) qp,COALESCE(risk_percentage,0) rp,
 CASE WHEN total_tasks=0 THEN 0 ELSE COALESCE(completion_percentage,0) END cpct,
 CASE WHEN COALESCE(completion_percentage,0)>=90 THEN 25 WHEN completion_percentage>=75 THEN 20 WHEN completion_percentage>=50 THEN 15 WHEN completion_percentage>=25 THEN 10 ELSE 5 END progress_score,
 CASE WHEN COALESCE(quality_percentage,0)>=90 THEN 25 WHEN quality_percentage>=75 THEN 20 WHEN quality_percentage>=60 THEN 15 WHEN quality_percentage>=40 THEN 10 ELSE 5 END quality_score,
 CASE WHEN COALESCE(risk_percentage,0)<=5 THEN 25 WHEN risk_percentage<=10 THEN 20 WHEN risk_percentage<=20 THEN 15 WHEN risk_percentage<=35 THEN 10 ELSE 5 END risk_score,
 CASE WHEN COALESCE(assignment_percentage,0)>=95 AND unique_assignees>=2 THEN 25 WHEN assignment_percentage>=85 THEN 20 WHEN assignment_percentage>=70 THEN 15 WHEN assignment_percentage>=50 THEN 10 ELSE 5 END resource_score
 FROM pct
), labels AS (
 SELECT *, progress_score+quality_score+risk_score+resource_score AS overall_health_score,
 CASE WHEN progress_score+quality_score+risk_score+resource_score>=90 THEN 'excellent' WHEN progress_score+quality_score+risk_score+resource_score>=75 THEN 'good' WHEN progress_score+quality_score+risk_score+resource_score>=60 THEN 'fair' WHEN progress_score+quality_score+risk_score+resource_score>=40 THEN 'poor' ELSE 'critical' END health_grade,
 CASE WHEN risk_percentage>=50 OR overdue_percentage>=30 THEN 'high_risk' WHEN risk_percentage>=25 OR overdue_percentage>=15 THEN 'medium_risk' WHEN risk_percentage>=10 OR overdue_percentage>=5 THEN 'low_risk' ELSE 'minimal_risk' END risk_level,
 CASE WHEN deadline_status='overdue' THEN 'overdue' WHEN risk_percentage>=40 AND days_to_deadline<=7 THEN 'at_risk' WHEN completion_percentage>=75 AND risk_percentage<=15 THEN 'on_track' WHEN completion_percentage>=50 AND risk_percentage<=25 THEN 'progressing' WHEN completion_percentage>=25 THEN 'slow_progress' ELSE 'stalled' END project_forecast,
 concat_ws(', ', CASE WHEN progress_score<15 THEN 'progress' END,CASE WHEN quality_score<15 THEN 'quality' END,CASE WHEN risk_score<15 THEN 'risk_management' END,CASE WHEN resource_score<15 THEN 'resource_allocation' END,CASE WHEN overdue_percentage>20 THEN 'deadline_management' END,CASE WHEN total_tasks>0 AND unassigned_tasks>0.3*total_tasks THEN 'task_assignment' END) focus_areas
 FROM scores
), final AS (
 SELECT *, total_tasks>=0 AND completed_tasks<=total_tasks AND completion_percentage BETWEEN 0 AND 100 AND quality_percentage BETWEEN 0 AND 100 AND overall_health_score BETWEEN 0 AND 100 AS is_valid_record,
 CASE WHEN total_tasks=0 THEN 'no_tasks' WHEN completion_percentage=100 AND project_status<>'completed' THEN 'status_mismatch' WHEN overdue_percentage>50 THEN 'excessive_overdue' WHEN total_tasks>0 AND unassigned_tasks>0.5*total_tasks THEN 'poor_assignment' WHEN project_age_days>365 AND completion_percentage<25 THEN 'stale_project' ELSE 'normal' END anomaly_flag
 FROM labels
)
SELECT project_id,project_name,project_created_at,project_due_date,project_owner,project_status,team_id,total_tasks,completed_tasks,active_tasks,assigned_tasks,unassigned_tasks,overdue_tasks,poor_performance_tasks,high_urgency_tasks,delayed_tasks,quality_tasks,avg_task_health_score,avg_task_complexity,avg_completion_time_days,avg_response_time_days,max_task_age_days,avg_delay_days,unique_assignees,recent_task_creation,recent_task_completion,
 COALESCE(completion_percentage,0)::DOUBLE completion_percentage,COALESCE(assignment_percentage,0)::DOUBLE assignment_percentage,COALESCE(overdue_percentage,0)::DOUBLE overdue_percentage,COALESCE(quality_percentage,0)::DOUBLE quality_percentage,COALESCE(risk_percentage,0)::DOUBLE risk_percentage,COALESCE(activity_percentage,0)::DOUBLE activity_percentage,project_age_days,deadline_status,days_to_deadline,progress_score,quality_score,risk_score,resource_score,overall_health_score,health_grade,risk_level,project_forecast,focus_areas,is_valid_record,anomaly_flag
FROM final WHERE is_valid_record ORDER BY overall_health_score DESC,project_id
```

## gold SQL（仅供定位差异）

S5

```sql
-- Project Health Indicators Analysis
-- Analysis of project health indicators, including core indicators such as progress, risk, resource allocation, etc.

with project_base as (
    select *
    from staging.stg_asana__project
    where project_name is not null  -- Constraint: project name cannot be empty
      and created_at is not null    -- Constraint: Creation time cannot be empty
),

task_base as (
    select *
    from staging.stg_asana__task
    where created_at is not null
),

project_task_relation as (
    select *
    from staging.stg_asana__project_task
),

task_performance as (
    select *
    from intermediate.int_asana__task_performance_metrics
),

user_productivity as (
    select *
    from intermediate.int_asana__user_productivity_trends
    where activity_month = date_trunc('month', current_date)  -- Current month data
),

-- Project task summary statistics
project_task_stats as (
    select 
        p.project_id,
        p.project_name,
        p.created_at as project_created_at,
        p.due_date as project_due_date,
        p.owner_user_id as project_owner,
        p.current_status as project_status,
        p.team_id,
        
        -- Basic task statistics
        count(distinct t.task_id) as total_tasks,
        count(distinct case when t.is_completed then t.task_id end) as completed_tasks,
        count(distinct case when not t.is_completed then t.task_id end) as active_tasks,
        count(distinct case when t.assignee_user_id is not null then t.task_id end) as assigned_tasks,
        count(distinct case when t.assignee_user_id is null and not t.is_completed then t.task_id end) as unassigned_tasks,
        
        -- Risk task statistics
        count(distinct case when tp.task_status_category = 'overdue' then t.task_id end) as overdue_tasks,
        count(distinct case when tp.performance_grade = 'poor' then t.task_id end) as poor_performance_tasks,
        count(distinct case when tp.urgency_score >= 4 then t.task_id end) as high_urgency_tasks,
        count(distinct case when tp.delay_days > 0 then t.task_id end) as delayed_tasks,
        
        -- quality index
        count(distinct case when tp.performance_grade in ('excellent', 'good') then t.task_id end) as quality_tasks,
        avg(tp.health_score) as avg_task_health_score,
        avg(tp.complexity_score) as avg_task_complexity,
        
        -- time indicator
        avg(case when t.is_completed then tp.days_open end) as avg_completion_time_days,
        avg(tp.response_time_days) as avg_response_time_days,
        max(tp.days_open) as max_task_age_days,
        avg(tp.delay_days) as avg_delay_days,
        
        -- Team collaboration metrics
        count(distinct t.assignee_user_id) as unique_assignees,
        count(distinct case when t.created_at >= current_date - interval '7 days' then t.task_id end) as recent_task_creation,
        count(distinct case when t.completed_at >= current_date - interval '7 days' then t.task_id end) as recent_task_completion
        
    from project_base p
    left join project_task_relation ptr on p.project_id = ptr.project_id
    left join task_base t on ptr.task_id = t.task_id
    left join task_performance tp on t.task_id = tp.task_id
    group by 1, 2, 3, 4, 5, 6, 7
),

-- Calculate project-level health metrics
project_health_metrics as (
    select 
        *,
        
        -- progress indicator
        case 
            when total_tasks > 0 then 
                round((completed_tasks * 100.0 / total_tasks), 2)
            else 0 
        end as completion_percentage,
        
        case 
            when total_tasks > 0 then 
                round((assigned_tasks * 100.0 / total_tasks), 2)
            else 0 
        end as assignment_percentage,
        
        case 
            when total_tasks > 0 then 
                round((overdue_tasks * 100.0 / total_tasks), 2)
            else 0 
        end as overdue_percentage,
        
        -- quality index
        case 
            when completed_tasks > 0 then 
                round((quality_tasks * 100.0 / completed_tasks), 2)
            else 0 
        end as quality_percentage,
        
        -- risk assessment
        case 
            when total_tasks > 0 then 
                round(((overdue_tasks + poor_performance_tasks + delayed_tasks) * 100.0 / total_tasks), 2)
            else 0 
        end as risk_percentage,
        
        -- activity indicator
        case 
            when total_tasks > 0 then 
                round(((recent_task_creation + recent_task_completion) * 100.0 / total_tasks), 2)
            else 0 
        end as activity_percentage,
        
        -- Project age (days)
        date_diff('day', project_created_at, current_date) as project_age_days,
        
        -- Project deadline status
        case 
            when project_due_date is null then 'no_deadline'
            when project_due_date > current_date then 'on_time'
            when project_due_date = current_date then 'due_today'
            else 'overdue'
        end as deadline_status,
        
        -- Days remaining
        case 
            when project_due_date is not null then 
                date_diff('day', current_date, project_due_date)
            else null 
        end as days_to_deadline
        
    from project_task_stats
),

-- Calculate overall health score and risk level
project_health_scores as (
    select 
        *,
        
        -- Progress health score (0-25 points)
        least(25, greatest(0, 
            case 
                when completion_percentage >= 90 then 25
                when completion_percentage >= 75 then 20
                when completion_percentage >= 50 then 15
                when completion_percentage >= 25 then 10
                else 5
            end
        )) as progress_score,
        
        -- Quality health score (0-25 points)
        least(25, greatest(0,
            case 
                when quality_percentage >= 90 then 25
                when quality_percentage >= 75 then 20
                when quality_percentage >= 60 then 15
                when quality_percentage >= 40 then 10
                else 5
            end
        )) as quality_score,
        
        -- Risk control score (0-25 points) - the lower the risk, the higher the score
        least(25, greatest(0,
            case 
                when risk_percentage <= 5 then 25
                when risk_percentage <= 10 then 20
                when risk_percentage <= 20 then 15
                when risk_percentage <= 35 then 10
                else 5
            end
        )) as risk_score,
        
        -- Resource allocation score (0-25 points)
        least(25, greatest(0,
            case 
                when assignment_percentage >= 95 and unique_assignees >= 2 then 25
                when assignment_percentage >= 85 then 20
                when assignment_percentage >= 70 then 15
                when assignment_percentage >= 50 then 10
                else 5
            end
        )) as resource_score
        
    from project_health_metrics
),

-- Final health calculation and rating
final_health_assessment as (
    select 
        *,
        
        -- Comprehensive health score (0-100 points)
        (progress_score + quality_score + risk_score + resource_score) as overall_health_score,
        
        -- health level
        case 
            when (progress_score + quality_score + risk_score + resource_score) >= 90 then 'excellent'
            when (progress_score + quality_score + risk_score + resource_score) >= 75 then 'good'
            when (progress_score + quality_score + risk_score + resource_score) >= 60 then 'fair'
            when (progress_score + quality_score + risk_score + resource_score) >= 40 then 'poor'
            else 'critical'
        end as health_grade,
        
        -- risk level
        case 
            when risk_percentage >= 50 or overdue_percentage >= 30 then 'high_risk'
            when risk_percentage >= 25 or overdue_percentage >= 15 then 'medium_risk'
            when risk_percentage >= 10 or overdue_percentage >= 5 then 'low_risk'
            else 'minimal_risk'
        end as risk_level,
        
        -- Project status forecast
        case 
            when deadline_status = 'overdue' then 'overdue'
            when risk_percentage >= 40 and days_to_deadline <= 7 then 'at_risk'
            when completion_percentage >= 75 and risk_percentage <= 15 then 'on_track'
            when completion_percentage >= 50 and risk_percentage <= 25 then 'progressing'
            when completion_percentage >= 25 then 'slow_progress'
            else 'stalled'
        end as project_forecast,
        
        -- Areas of concern (use concat instead of array_remove)
        trim(
            case when progress_score < 15 then 'progress, ' else '' end ||
            case when quality_score < 15 then 'quality, ' else '' end ||
            case when risk_score < 15 then 'risk_management, ' else '' end ||
            case when resource_score < 15 then 'resource_allocation, ' else '' end ||
            case when overdue_percentage > 20 then 'deadline_management, ' else '' end ||
            case when unassigned_tasks > total_tasks * 0.3 then 'task_assignment, ' else '' end,
            ', '
        ) as focus_areas
        
    from project_health_scores
),

-- Data quality verification and constraint checking
validated_results as (
    select 
        *,
        
        -- Data quality verification
        case 
            when project_id is null then false
            when project_name is null or trim(project_name) = '' then false
            when total_tasks < 0 then false  -- Constraint: The number of tasks cannot be negative
            when completed_tasks > total_tasks then false  -- Constraint: The number of completed tasks cannot exceed the total number of tasks
            when completion_percentage < 0 or completion_percentage > 100 then false  -- Constraint: Complete percentage must be between 0-100
            when quality_percentage < 0 or quality_percentage > 100 then false  -- Constraint: mass percentage must be between 0-100
            when overall_health_score < 0 or overall_health_score > 100 then false  -- Constraint: health score must be between 0-100
            else true
        end as is_valid_record,
        
        -- Exception flag
        case 
            when total_tasks = 0 then 'no_tasks'
            when completion_percentage = 100 and project_status != 'completed' then 'status_mismatch'
            when overdue_percentage > 50 then 'excessive_overdue'
            when unassigned_tasks > total_tasks * 0.5 then 'poor_assignment'
            when project_age_days > 365 and completion_percentage < 25 then 'stale_project'
            else 'normal'
        end as anomaly_flag
        
    from final_health_assessment
)

select *
from validated_results
where is_valid_record = true  -- Only output records that pass verification
order by overall_health_score desc, project_id
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 472 | 495 | 0 | 23 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"project_id":"2218666548720"}</code> |
| K2 | <code>{"project_id":"6277090307738"}</code> |
| K3 | <code>{"project_id":"9328927533820"}</code> |
| K4 | <code>{"project_id":"2355960258944"}</code> |
| K5 | <code>{"project_id":"3592044107714"}</code> |
| K6 | <code>{"project_id":"4736390227856"}</code> |
| K7 | <code>{"project_id":"4975782893340"}</code> |
| K8 | <code>{"project_id":"7869497570371"}</code> |
| K9 | <code>{"project_id":"3719349937021"}</code> |
| K10 | <code>{"project_id":"9978897153608"}</code> |
| K11 | <code>{"project_id":"8702221308883"}</code> |
| K12 | <code>{"project_id":"6348903063899"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| project_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| active_tasks | 0 | 0 | 0 | BIGINT | BIGINT |
| activity_percentage | 0 | 0 | 0 | DOUBLE | DOUBLE |
| anomaly_flag | 3 | 3 | 3 | VARCHAR | VARCHAR |
| assigned_tasks | 0 | 0 | 0 | BIGINT | BIGINT |
| assignment_percentage | 20 | 20 | 20 | DOUBLE | DOUBLE |
| avg_completion_time_days | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_delay_days | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_response_time_days | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_task_complexity | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_task_health_score | 0 | 0 | 0 | DOUBLE | DOUBLE |
| completed_tasks | 0 | 0 | 0 | BIGINT | BIGINT |
| completion_percentage | 20 | 20 | 20 | DOUBLE | DOUBLE |
| days_to_deadline | 0 | 0 | 0 | BIGINT | BIGINT |
| deadline_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| delayed_tasks | 0 | 0 | 0 | BIGINT | BIGINT |
| focus_areas | 7 | 7 | 7 | VARCHAR | VARCHAR |
| health_grade | 5 | 5 | 5 | VARCHAR | VARCHAR |
| high_urgency_tasks | 0 | 0 | 0 | BIGINT | BIGINT |
| is_valid_record | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| max_task_age_days | 0 | 0 | 0 | BIGINT | BIGINT |
| overall_health_score | 17 | 17 | 17 | INTEGER | INTEGER |
| overdue_percentage | 0 | 0 | 0 | DOUBLE | DOUBLE |
| overdue_tasks | 0 | 0 | 0 | BIGINT | BIGINT |
| poor_performance_tasks | 0 | 0 | 0 | BIGINT | BIGINT |
| progress_score | 8 | 8 | 8 | INTEGER | INTEGER |
| project_age_days | 0 | 0 | 0 | BIGINT | BIGINT |
| project_created_at | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| project_due_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| project_forecast | 2 | 2 | 2 | VARCHAR | VARCHAR |
| project_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| project_owner | 0 | 0 | 0 | VARCHAR | VARCHAR |
| project_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| quality_percentage | 0 | 0 | 0 | DOUBLE | DOUBLE |
| quality_score | 0 | 0 | 0 | INTEGER | INTEGER |
| quality_tasks | 0 | 0 | 0 | BIGINT | BIGINT |
| recent_task_completion | 0 | 0 | 0 | BIGINT | BIGINT |
| recent_task_creation | 0 | 0 | 0 | BIGINT | BIGINT |
| resource_score | 12 | 12 | 12 | INTEGER | INTEGER |
| risk_level | 1 | 1 | 1 | VARCHAR | VARCHAR |
| risk_percentage | 13 | 13 | 13 | DOUBLE | DOUBLE |
| risk_score | 4 | 4 | 4 | INTEGER | INTEGER |
| team_id | 0 | 0 | 0 | BIGINT | BIGINT |
| total_tasks | 20 | 20 | 20 | BIGINT | BIGINT |
| unassigned_tasks | 0 | 0 | 0 | BIGINT | BIGINT |
| unique_assignees | 0 | 0 | 0 | BIGINT | BIGINT |

anomaly_flag 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | stale_project | normal |
| K2 | normal | status_mismatch |
| K3 | stale_project | normal |

assignment_percentage 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 77.78 | 87.5 |
| K4 | 87.5 | 100.0 |
| K5 | 57.14 | 66.67 |

completion_percentage 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 22.22 | 25.0 |
| K4 | 62.5 | 71.43 |
| K5 | 28.57 | 33.33 |

focus_areas 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K6 | progress, quality, risk_management | quality, risk_management |
| K7 | quality, resource_allocation | quality |
| K8 | progress, quality, risk_management, resource_allocation | progress, quality, risk_management |

health_grade 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | critical | poor |
| K9 | poor | critical |
| K2 | fair | good |

overall_health_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 35 | 40 |
| K4 | 65 | 70 |
| K9 | 40 | 35 |

progress_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 5 | 10 |
| K6 | 10 | 15 |
| K7 | 15 | 20 |

project_forecast 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | stalled | slow_progress |
| K10 | slow_progress | progressing |

resource_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 15 | 20 |
| K4 | 20 | 25 |
| K7 | 10 | 15 |

risk_level 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K11 | low_risk | medium_risk |

risk_percentage 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 33.33 | 37.5 |
| K5 | 14.29 | 16.67 |
| K9 | 10.0 | 11.11 |

risk_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 10 | 5 |
| K9 | 20 | 15 |
| K12 | 20 | 15 |

total_tasks 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 9 | 8 |
| K4 | 8 | 7 |
| K5 | 7 | 6 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[{"project_id":"1381613423696"},{"project_id":"1772551392560"},{"project_id":"2040328813491"},{"project_id":"2675198004696"},{"project_id":"2925808505027"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>1列；[{"column":"avg_response_time_days","table_rows":472}]</code> |
| A3_constant_nonnull_column | <code>11列；[{"column":"overdue_tasks","value":"0"},{"column":"poor_performance_tasks","value":"0"},{"column":"quality_tasks","value":"0"}]</code> |
| A4_equal_columns | <code>3组；[{"columns":["overdue_tasks","poor_performance_tasks","quality_tasks","recent_task_creation","recent_task_completion"],"nonnull_equal_rows":472,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["high_urgency_tasks","delayed_tasks"],"nonnull_equal_rows":472,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["avg_completion_time_days","overdue_percentage","quality_percentage","activity_percentage"],"nonnull_equal_rows":472,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>3组；[{"columns":["overdue_tasks","poor_performance_tasks","quality_tasks","recent_task_creation","recent_task_completion"],"nonnull_equal_rows":472,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["high_urgency_tasks","delayed_tasks"],"nonnull_equal_rows":472,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["avg_completion_time_days","overdue_percentage","quality_percentage","activity_percentage"],"nonnull_equal_rows":472,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| B7_specified_not_read | <code>["intermediate.int_asana__task_performance_metrics (task_id, task_status_category, performance_grade, urgency_score, health_score, complexity_score, days_open, response_time_days, delay_days)","staging.stg_asana__project (project_id, project_name, created_at, due_date, owner_user_id, current_status, team_id)","staging.stg_asana__project_task (project_id, task_id)"]</code> |
| C9_agent_runtime_text | <code>S4:24 CURRENT_DATE；命中数=6</code> |
| C9_gold_runtime_text | <code>S5:30 current_date；命中数=7</code> |
| C9_contract_runtime_text | <code>S3:303 current_date；命中数=10</code> |
| D10_keyword_in_any_result_field | <code>命中数=1；task_instruction_not_agent_report  7) Project context: join staging.stg_asana__project_task on task_id, then staging.stg_asana__project left-joined to intermediate.int_asana__project_health_indicators to get project_name, team_id, and project_health_score (defaults to 50 when the project exists without indicators).</code> |

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

event 21 / message

```text
'int_asana__project_health_indicators':'''WITH project_base AS (
```
event 25 / message

```text
 FROM staging.stg_asana__project p LEFT JOIN staging.stg_asana__team t ON p.team_id::VARCHAR=t.team_id LEFT JOIN intermediate.int_asana__project_health_indicators h ON p.project_id=h.project_id
```
event 25 / message

```text
FROM staging.stg_asana__project p LEFT JOIN intermediate.int_asana__project_health_indicators h ON p.project_id=h.project_id GROUP BY p.team_id,p.team_name),
```
event 25 / message

```text
FROM calc c LEFT JOIN staging.stg_asana__project_task pt ON c.task_id=pt.task_id::VARCHAR LEFT JOIN staging.stg_asana__project p ON pt.project_id::VARCHAR=p.project_id LEFT JOIN intermediate.int_asana__project_health_indicators h ON p.project_id=h.project_id LEFT JOIN staging.stg_asana__user u ON c.assignee_user_id::VARCHAR=u.user_id),
```
event 33 / message

```text
p='sql/marts/asana__team_efficiency_metrics.sql';s=open(p).read().replace("SELECT p.team_id,p.team_name,COUNT(DISTINCT p.project_id)","SELECT p.team_id,team.team_name,COUNT(DISTINCT p.project_id)").replace("FROM staging.stg_asana__project p LEFT JOIN intermediate.int_asana__project_health_indicators h ON p.project_id=h.project_id GROUP BY p.team_id,p.team_name)","FROM staging.stg_asana__project p LEFT JOIN staging.stg_asana__team team ON p.team_id::VARCHAR=team.team_id LEFT JOIN intermediate.int_asana__project_health_indicators h ON p.project_id=h.project_id GROUP BY p.team_id,team.team_name)")
```
event 41 / message

```text
'intermediate':'int_asana__task_story int_asana__task_assignee int_asana__task_open_length int_asana__task_comments int_asana__task_followers int_asana__task_tags int_asana__task_first_modifier int_asana__subtask_parent int_asana__task_projects int_asana__project_task_metrics int_asana__project_user int_asana__user_task_metrics int_asana__task_performance_metrics int_asana__user_productivity_trends int_asana__project_health_indicators'.split(),
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/011_table_alignment.jsonl`
- S2: `records/011_alignment_impl-008.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-008/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/intermediate/int_asana__project_health_indicators.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/sql/intermediate/int_asana__project_health_indicators.sql`
- S6: `records/006_contract_impl-008.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/result.md`
- S10: `data/021_packages_work/021_impl-008_int_asana__project_health_indicators/021_impl-008_int_asana__project_health_indicators.json`
- S11: `data/011_agent_alignment/impl-008_attempt_01/int_asana__project_health_indicators_2025-10-12.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/asana.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions`
