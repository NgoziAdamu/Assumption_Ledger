# impl-008 | marts | asana__task_lifecycle_analysis | 差异：S1；日期 原记录

## 契约完整原文

S3:1382–1523

```yaml
    - name: asana__task_lifecycle_analysis
      description: Deterministic lifecycle analytics per task with computed timings, classifications, pattern lists, and project/user context; outputs only records passing validation
      grain: One row per task_id per associated project (or one row if no project), after validation
      source_models:
      - staging.stg_asana__task
      - intermediate.int_asana__task_performance_metrics
      - intermediate.int_asana__task_story
      - staging.stg_asana__project
      - intermediate.int_asana__project_health_indicators
      - staging.stg_asana__project_task
      - staging.stg_asana__user
      business_logic: '1) Base rows: include tasks from staging.stg_asana__task where created_at is not null. 2) Join per-task metrics from intermediate.int_asana__task_performance_metrics (task_status_category, performance_grade, health_score, response_time_days, delay_days, complexity_score, urgency_score, activity_score). 3) Build task stories from intermediate.int_asana__task_story where action_taken is not null and derive per task: - creation_timestamp: earliest ''created'' story, - first_assignment_timestamp: earliest ''assigned'' story, - last_assignment_timestamp: latest ''assigned'' story, - last_modification_timestamp: latest story across all actions, - completion_timestamp: earliest ''completed'' story, - Activity aggregates: total_story_events (count), unique_action_types (distinct action_taken), days_with_activity (distinct calendar dates of stories). 4) Compute lifecycle durations: - hours_to_assignment: hours from task.created_at to first_assignment_timestamp when first_assignment_timestamp exists; otherwise null, - hours_assigned_to_completion: hours from first_assignment_timestamp to task.completed_at when both exist; otherwise null, - total_lifecycle_hours: hours from task.created_at to task.completed_at if completed, else to the current time, - avg_daily_activity_rate: if lifecycle days from task.created_at to task.completed_at or current time > 0, then total_story_events divided by that day count rounded to two decimals; otherwise equals total_story_events. 5) Classifications and scores: - lifecycle_efficiency_category: • If completed: ''highly_efficient'' when hours_to_assignment<=24 and hours_assigned_to_completion<=168; ''efficient'' when <=72 and <=336; ''moderate'' when <=168 and <=720; ''slow_start'' when hours_to_assignment<=336; ''slow_completion'' when hours_assigned_to_completion>720; else ''inefficient''. • If not completed: ''stalled_unassigned'' when hours_to_assignment is null and total_lifecycle_hours>168; ''stalled_assigned'' when hours_to_assignment is not null and total_lifecycle_hours>720; ''urgent_delayed'' when urgency_score>=4 and total_lifecycle_hours>72; else ''in_progress''. - activity_level by avg_daily_activity_rate: >=2.0 ''very_active''; >=1.0 ''active''; >=0.5 ''moderate_activity''; >=0.1 ''low_activity''; else ''dormant''. - lifecycle_health_score: clamp to [0,100] the sum of: • Timeliness: completed on time=40; completed with delay_days<=2=30; <=7=20; completed late>7=10; if not completed and due_date>today=35; due today=25; overdue=5. • Response speed: response_time_days<=1=30; <=3=25; <=7=20; <=14=15; non-null else=10; null=5. • Activity: activity_score*4. • Complexity fit: complexity=1 and total_lifecycle_hours<=168=10; complexity=2 and <=336=10; complexity=3 and <=720=10; any task <=72 hours=8; else=5. - current_lifecycle_stage: ''backlog'' (not completed and no assignee); ''newly_assigned'' (not completed, assignee exists, and within 1 day of first assignment or creation if assignment missing); ''active_development'' (not completed, assignee exists, and modified within 7 days); ''stagnant'' (not completed, assignee exists, and last modification >7 days); ''completed_on_time'' (completed with delay_days=0); ''completed_delayed'' (completed with delay_days>0); else ''unknown_state''. 6) Pattern lists (tokens evaluated in fixed order, joined by ", ", and trimmed; empty string if none): - anomaly_patterns: ''delayed_assignment'' if hours_to_assignment>336; ''prolonged_execution'' if hours_assigned_to_completion>1440; ''dormant_task'' if avg_daily_activity_rate<0.1 and not completed; ''overengineered_simple'' if complexity_score=1 and total_lifecycle_hours>336; ''urgent_ignored'' if urgency_score>=4 and response_time_days>3; ''blocked_subtask'' if parent_task_id not null and total_lifecycle_hours>720; ''severely_delayed'' if delay_days>14; ''high_churn'' if total_story_events>50. - success_patterns: ''fast_track'' if lifecycle_efficiency_category=''highly_efficient''; ''exemplary_execution'' if completed, on time, and performance_grade=''excellent''; ''consistent_progress'' if avg_daily_activity_rate>=1.0 and completed; ''rapid_delivery'' if response_time_days<=1 and hours_assigned_to_completion<=168; ''complex_mastery'' if complexity_score=3 and lifecycle_health_score>=80; ''urgent_success'' if urgency_score>=4 and delay_days=0. - improvement_opportunities: ''faster_assignment'' if hours_to_assignment>72; ''increase_engagement'' if activity_level in (''low_activity'',''dormant''); ''improve_time_management'' if delay_days>0; ''enhance_responsiveness'' if response_time_days>3; ''overall_process_improvement'' if lifecycle_health_score<60; ''add_progress_updates'' if total_story_events<3 and not completed. - complexity_execution_match (first match wins): ''appropriate_simple'' if complexity_score=1 and total_lifecycle_hours<=72; ''appropriate_medium'' if complexity_score=2 and total_lifecycle_hours in 73–336; ''appropriate_complex'' if complexity_score=3 and total_lifecycle_hours in 337–720; ''faster_than_expected'' if total_lifecycle_hours < complexity_score*72; ''slower_than_expected'' if total_lifecycle_hours > complexity_score*240; else ''within_range''. 7) Project context: join staging.stg_asana__project_task on task_id, then staging.stg_asana__project left-joined to intermediate.int_asana__project_health_indicators to get project_name, team_id, and project_health_score (defaults to 50 when the project exists without indicators). Tasks with multiple projects yield one row per membership; tasks without a project retain a single row with null project fields. 8) User context: join staging.stg_asana__user by casting assignee_user_id to the user_id type to get assignee_name; assignee_performance_grade is always ''unknown'' for matched users. 9) Relative performance vs project: compare lifecycle_health_score to project_health_score and assign: >+20 ''above_project_average''; >+10 ''slightly_above_average''; >= -10 ''project_average''; >= -20 ''slightly_below_average''; else ''below_project_average'' (null project score falls into ''below_project_average''). 10) Data quality validation (is_valid_record): mark false when task_id or task_name is null; lifecycle_health_score outside [0,100]; any of total_lifecycle_hours, hours_to_assignment, hours_assigned_to_completion, or avg_daily_activity_rate is negative; or is_completed=true while both completion_timestamp and completed_at are null. Only rows with is_valid_record=true are kept, and results are sorted by lifecycle_health_score descending, then total_lifecycle_hours ascending, then task_id.'
      columns:
      - name: task_id
        data_type: VARCHAR
        description: Asana task identifier; may repeat across rows if the task belongs to multiple projects
      - name: task_name
        data_type: VARCHAR
        description: Task display name from stg_asana__task
      - name: created_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Task creation timestamp from stg_asana__task; non-null by model filter
      - name: completed_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Task completion timestamp from stg_asana__task; null if not completed
      - name: due_date
        data_type: TIMESTAMP WITH TIME ZONE
        description: Due date from stg_asana__task; may be null and is compared to current date in scoring
      - name: is_completed
        data_type: BOOLEAN
        description: True if the task is marked completed in stg_asana__task
      - name: assignee_user_id
        data_type: BIGINT
        description: Current assignee user_id from stg_asana__task; may be null
      - name: parent_task_id
        data_type: BIGINT
        description: Parent task_id when this is a subtask; null otherwise
      - name: task_status_category
        data_type: VARCHAR
        description: Status category from int_asana__task_performance_metrics; passed through as-is
      - name: performance_grade
        data_type: VARCHAR
        description: Performance grade from int_asana__task_performance_metrics; used in success_patterns
      - name: health_score
        data_type: BIGINT
        description: Health score from int_asana__task_performance_metrics; not recomputed here
      - name: response_time_days
        data_type: BIGINT
        description: Days from creation to first response from metrics; used in scoring and patterns; null treated as worst in scoring
      - name: delay_days
        data_type: BIGINT
        description: Days completed past due date from metrics; used in scoring and patterns
      - name: complexity_score
        data_type: INTEGER
        description: Complexity score from metrics (integer); used in complexity matching and scoring
      - name: urgency_score
        data_type: INTEGER
        description: Urgency score from metrics (integer); used in efficiency and patterns
      - name: activity_score
        data_type: INTEGER
        description: Activity score from metrics (integer); contributes to lifecycle_health_score as activity_score*4
      - name: creation_timestamp
        data_type: TIMESTAMP
        description: Earliest 'created' story timestamp; may be null
      - name: first_assignment_timestamp
        data_type: TIMESTAMP
        description: Earliest 'assigned' story timestamp; null if never assigned
      - name: last_assignment_timestamp
        data_type: TIMESTAMP
        description: Latest 'assigned' story timestamp; null if never assigned
      - name: last_modification_timestamp
        data_type: TIMESTAMP
        description: Latest story timestamp across all actions; null if no stories
      - name: completion_timestamp
        data_type: TIMESTAMP
        description: Earliest 'completed' story timestamp; required when is_completed and completed_at is null
      - name: hours_to_assignment
        data_type: BIGINT
        description: Hours from task.created_at to first_assignment_timestamp; null if never assigned
      - name: hours_assigned_to_completion
        data_type: BIGINT
        description: Hours from first_assignment_timestamp to task.completed_at; null if either timestamp is missing
      - name: total_lifecycle_hours
        data_type: BIGINT
        description: Hours from task.created_at to task.completed_at, or to the current time if not completed
      - name: total_story_events
        data_type: BIGINT
        description: Count of all stories with non-null action_taken for the task
      - name: unique_action_types
        data_type: BIGINT
        description: Distinct count of action_taken values across stories for the task
      - name: days_with_activity
        data_type: BIGINT
        description: Distinct count of calendar dates with any story activity
      - name: avg_daily_activity_rate
        data_type: DOUBLE
        description: Average stories per day across the lifecycle; rounded to 2 decimals when lifecycle days > 0, else equals total_story_events
      - name: lifecycle_efficiency_category
        data_type: VARCHAR
        description: Efficiency class based on completion status, hours_to_assignment, hours_assigned_to_completion, total_lifecycle_hours, and urgency_score using ordered rules
      - name: activity_level
        data_type: VARCHAR
        description: 'Activity class from avg_daily_activity_rate thresholds: very_active, active, moderate_activity, low_activity, dormant'
      - name: lifecycle_health_score
        data_type: INTEGER
        description: Overall lifecycle score clamped to [0,100] from timeliness, response speed, activity_score*4, and complexity adaptation
      - name: current_lifecycle_stage
        data_type: VARCHAR
        description: 'Stage label from ordered rules: backlog, newly_assigned, active_development, stagnant, completed_on_time, completed_delayed, or unknown_state'
      - name: anomaly_patterns
        data_type: VARCHAR
        description: Comma+space separated anomaly tokens in fixed order with trimming; empty string if none
      - name: success_patterns
        data_type: VARCHAR
        description: Comma+space separated success tokens in fixed order with trimming; empty string if none
      - name: improvement_opportunities
        data_type: VARCHAR
        description: Comma+space separated improvement tokens in fixed order with trimming; empty string if none
      - name: complexity_execution_match
        data_type: VARCHAR
        description: 'Execution speed vs complexity classification with first-match priority: appropriate_simple/medium/complex, faster_than_expected, slower_than_expected, within_range'
      - name: project_name
        data_type: VARCHAR
        description: Project name from stg_asana__project via project membership; null when no project
      - name: team_id
        data_type: BIGINT
        description: Team ID from the associated project; null when no project
      - name: project_health_score
        data_type: INTEGER
        description: Project overall health score (default 50 when project exists but no indicator); null when no project membership
      - name: assignee_name
        data_type: VARCHAR
        description: Assignee user_name from stg_asana__user using the casted assignee_user_id join; null if no match
      - name: assignee_performance_grade
        data_type: VARCHAR
        description: Assignee performance grade from user context; set to 'unknown' for any matched user by design
      - name: relative_performance_vs_project
        data_type: VARCHAR
        description: 'Relative class vs project_health_score: above_project_average, slightly_above_average, project_average, slightly_below_average, below_project_average (null project treated as below_project_average)'
      - name: is_valid_record
        data_type: BOOLEAN
        description: True if all data quality checks pass; the final result set filters to is_valid_record=true
```

## agent 最终 SQL

S4

```sql
WITH story_agg AS (SELECT target_task_id,MIN(created_at) FILTER(WHERE action_taken='created') creation_timestamp,MIN(created_at) FILTER(WHERE action_taken='assigned') first_assignment_timestamp,MAX(created_at) FILTER(WHERE action_taken='assigned') last_assignment_timestamp,MAX(created_at) last_modification_timestamp,MIN(created_at) FILTER(WHERE action_taken='completed') completion_timestamp,COUNT(*)::BIGINT total_story_events,COUNT(DISTINCT action_taken)::BIGINT unique_action_types,COUNT(DISTINCT created_at::DATE)::BIGINT days_with_activity FROM intermediate.int_asana__task_story WHERE action_taken IS NOT NULL GROUP BY target_task_id),
base AS (SELECT t.*,m.task_status_category,m.performance_grade,m.health_score,m.response_time_days,m.delay_days,m.complexity_score,m.urgency_score,m.activity_score,s.creation_timestamp,s.first_assignment_timestamp,s.last_assignment_timestamp,s.last_modification_timestamp,s.completion_timestamp,COALESCE(s.total_story_events,0)::BIGINT total_story_events,COALESCE(s.unique_action_types,0)::BIGINT unique_action_types,COALESCE(s.days_with_activity,0)::BIGINT days_with_activity,
 DATE_DIFF('hour',t.created_at,s.first_assignment_timestamp)::BIGINT hours_to_assignment,DATE_DIFF('hour',s.first_assignment_timestamp,t.completed_at)::BIGINT hours_assigned_to_completion,DATE_DIFF('hour',t.created_at,COALESCE(t.completed_at,CURRENT_TIMESTAMP))::BIGINT total_lifecycle_hours,
 CASE WHEN DATE_DIFF('day',t.created_at,COALESCE(t.completed_at,CURRENT_TIMESTAMP))>0 THEN ROUND(COALESCE(s.total_story_events,0)::DOUBLE/DATE_DIFF('day',t.created_at,COALESCE(t.completed_at,CURRENT_TIMESTAMP)),2) ELSE COALESCE(s.total_story_events,0)::DOUBLE END avg_daily_activity_rate
FROM staging.stg_asana__task t LEFT JOIN intermediate.int_asana__task_performance_metrics m ON t.task_id=m.task_id LEFT JOIN story_agg s ON t.task_id=s.target_task_id WHERE t.created_at IS NOT NULL),
calc AS (SELECT *,CASE WHEN is_completed THEN CASE WHEN hours_to_assignment<=24 AND hours_assigned_to_completion<=168 THEN 'highly_efficient' WHEN hours_to_assignment<=72 AND hours_assigned_to_completion<=336 THEN 'efficient' WHEN hours_to_assignment<=168 AND hours_assigned_to_completion<=720 THEN 'moderate' WHEN hours_to_assignment<=336 THEN 'slow_start' WHEN hours_assigned_to_completion>720 THEN 'slow_completion' ELSE 'inefficient' END WHEN hours_to_assignment IS NULL AND total_lifecycle_hours>168 THEN 'stalled_unassigned' WHEN hours_to_assignment IS NOT NULL AND total_lifecycle_hours>720 THEN 'stalled_assigned' WHEN urgency_score>=4 AND total_lifecycle_hours>72 THEN 'urgent_delayed' ELSE 'in_progress' END lifecycle_efficiency_category,
CASE WHEN avg_daily_activity_rate>=2 THEN 'very_active' WHEN avg_daily_activity_rate>=1 THEN 'active' WHEN avg_daily_activity_rate>=.5 THEN 'moderate_activity' WHEN avg_daily_activity_rate>=.1 THEN 'low_activity' ELSE 'dormant' END activity_level,
LEAST(100,GREATEST(0,(CASE WHEN is_completed AND delay_days=0 THEN 40 WHEN is_completed AND delay_days<=2 THEN 30 WHEN is_completed AND delay_days<=7 THEN 20 WHEN is_completed THEN 10 WHEN due_date::DATE>CURRENT_DATE THEN 35 WHEN due_date::DATE=CURRENT_DATE THEN 25 ELSE 5 END)+(CASE WHEN response_time_days<=1 THEN 30 WHEN response_time_days<=3 THEN 25 WHEN response_time_days<=7 THEN 20 WHEN response_time_days<=14 THEN 15 WHEN response_time_days IS NOT NULL THEN 10 ELSE 5 END)+COALESCE(activity_score,1)*4+(CASE WHEN complexity_score=1 AND total_lifecycle_hours<=168 THEN 10 WHEN complexity_score=2 AND total_lifecycle_hours<=336 THEN 10 WHEN complexity_score=3 AND total_lifecycle_hours<=720 THEN 10 WHEN total_lifecycle_hours<=72 THEN 8 ELSE 5 END)))::INTEGER lifecycle_health_score,
CASE WHEN NOT is_completed AND assignee_user_id IS NULL THEN 'backlog' WHEN NOT is_completed AND assignee_user_id IS NOT NULL AND COALESCE(first_assignment_timestamp,created_at)>=CURRENT_TIMESTAMP-INTERVAL '1 day' THEN 'newly_assigned' WHEN NOT is_completed AND assignee_user_id IS NOT NULL AND modified_at>=CURRENT_TIMESTAMP-INTERVAL '7 day' THEN 'active_development' WHEN NOT is_completed AND assignee_user_id IS NOT NULL THEN 'stagnant' WHEN is_completed AND delay_days=0 THEN 'completed_on_time' WHEN is_completed AND delay_days>0 THEN 'completed_delayed' ELSE 'unknown_state' END current_lifecycle_stage
FROM base), context AS (SELECT c.*,p.project_name,p.team_id,CASE WHEN p.project_id IS NULL THEN NULL ELSE COALESCE(h.overall_health_score,50) END::INTEGER project_health_score,u.user_name assignee_name,CASE WHEN u.user_id IS NOT NULL THEN 'unknown' END assignee_performance_grade
FROM calc c LEFT JOIN staging.stg_asana__project_task pt ON c.task_id=pt.task_id::VARCHAR LEFT JOIN staging.stg_asana__project p ON pt.project_id::VARCHAR=p.project_id LEFT JOIN intermediate.int_asana__project_health_indicators h ON p.project_id=h.project_id LEFT JOIN staging.stg_asana__user u ON c.assignee_user_id::VARCHAR=u.user_id),
final AS (SELECT *,CASE WHEN project_health_score IS NULL THEN 'below_project_average' WHEN lifecycle_health_score-project_health_score>20 THEN 'above_project_average' WHEN lifecycle_health_score-project_health_score>10 THEN 'slightly_above_average' WHEN lifecycle_health_score-project_health_score>=-10 THEN 'project_average' WHEN lifecycle_health_score-project_health_score>=-20 THEN 'slightly_below_average' ELSE 'below_project_average' END relative_performance_vs_project,
concat_ws(', ',CASE WHEN hours_to_assignment>336 THEN 'delayed_assignment' END,CASE WHEN hours_assigned_to_completion>1440 THEN 'prolonged_execution' END,CASE WHEN avg_daily_activity_rate<.1 AND NOT is_completed THEN 'dormant_task' END,CASE WHEN complexity_score=1 AND total_lifecycle_hours>336 THEN 'overengineered_simple' END,CASE WHEN urgency_score>=4 AND response_time_days>3 THEN 'urgent_ignored' END,CASE WHEN parent_task_id IS NOT NULL AND total_lifecycle_hours>720 THEN 'blocked_subtask' END,CASE WHEN delay_days>14 THEN 'severely_delayed' END,CASE WHEN total_story_events>50 THEN 'high_churn' END) anomaly_patterns,
concat_ws(', ',CASE WHEN lifecycle_efficiency_category='highly_efficient' THEN 'fast_track' END,CASE WHEN is_completed AND delay_days=0 AND performance_grade='excellent' THEN 'exemplary_execution' END,CASE WHEN avg_daily_activity_rate>=1 AND is_completed THEN 'consistent_progress' END,CASE WHEN response_time_days<=1 AND hours_assigned_to_completion<=168 THEN 'rapid_delivery' END,CASE WHEN complexity_score=3 AND lifecycle_health_score>=80 THEN 'complex_mastery' END,CASE WHEN urgency_score>=4 AND delay_days=0 THEN 'urgent_success' END) success_patterns,
concat_ws(', ',CASE WHEN hours_to_assignment>72 THEN 'faster_assignment' END,CASE WHEN activity_level IN ('low_activity','dormant') THEN 'increase_engagement' END,CASE WHEN delay_days>0 THEN 'improve_time_management' END,CASE WHEN response_time_days>3 THEN 'enhance_responsiveness' END,CASE WHEN lifecycle_health_score<60 THEN 'overall_process_improvement' END,CASE WHEN total_story_events<3 AND NOT is_completed THEN 'add_progress_updates' END) improvement_opportunities,
CASE WHEN complexity_score=1 AND total_lifecycle_hours<=72 THEN 'appropriate_simple' WHEN complexity_score=2 AND total_lifecycle_hours BETWEEN 73 AND 336 THEN 'appropriate_medium' WHEN complexity_score=3 AND total_lifecycle_hours BETWEEN 337 AND 720 THEN 'appropriate_complex' WHEN total_lifecycle_hours<complexity_score*72 THEN 'faster_than_expected' WHEN total_lifecycle_hours>complexity_score*240 THEN 'slower_than_expected' ELSE 'within_range' END complexity_execution_match,
(task_id IS NOT NULL AND task_name IS NOT NULL AND lifecycle_health_score BETWEEN 0 AND 100 AND total_lifecycle_hours>=0 AND (hours_to_assignment IS NULL OR hours_to_assignment>=0) AND (hours_assigned_to_completion IS NULL OR hours_assigned_to_completion>=0) AND avg_daily_activity_rate>=0 AND NOT(is_completed AND completion_timestamp IS NULL AND completed_at IS NULL)) is_valid_record
FROM context)
SELECT task_id,task_name,created_at,completed_at,due_date,is_completed,assignee_user_id,parent_task_id,task_status_category,performance_grade,health_score,response_time_days,delay_days,complexity_score,urgency_score,activity_score,creation_timestamp,first_assignment_timestamp,last_assignment_timestamp,last_modification_timestamp,completion_timestamp,hours_to_assignment,hours_assigned_to_completion,total_lifecycle_hours,total_story_events,unique_action_types,days_with_activity,avg_daily_activity_rate,lifecycle_efficiency_category,activity_level,lifecycle_health_score,current_lifecycle_stage,anomaly_patterns,success_patterns,improvement_opportunities,complexity_execution_match,project_name,team_id,project_health_score,assignee_name,assignee_performance_grade,relative_performance_vs_project,is_valid_record
FROM final WHERE is_valid_record ORDER BY lifecycle_health_score DESC,total_lifecycle_hours,task_id
```

## gold SQL（仅供定位差异）

S5

```sql
-- Task Lifecycle Analysis
-- Task life cycle analysis - in-depth analysis of the entire process of tasks from creation to completion

with task_base as (
    select *
    from staging.stg_asana__task
    where created_at is not null
),

task_performance as (
    select *
    from intermediate.int_asana__task_performance_metrics
),

task_stories as (
    select *
    from intermediate.int_asana__task_story
    where action_taken is not null
),

-- Simplify access to project information
project_info as (
    select 
        p.project_id,
        p.project_name,
        p.team_id,
        coalesce(phi.overall_health_score, 50) as overall_health_score
    from staging.stg_asana__project p
    left join intermediate.int_asana__project_health_indicators phi on p.project_id = phi.project_id
),

-- Simplify user information acquisition
user_info as (
    select 
        u.user_id,
        u.user_name,
        'unknown' as performance_grade  -- Simplify and avoid circular dependencies
    from staging.stg_asana__user u
),

-- Task life cycle phase definition
task_lifecycle_stages as (
    select 
        tb.task_id,
        tb.task_name,
        tb.created_at,
        tb.completed_at,
        tb.due_date,
        tb.is_completed,
        tb.assignee_user_id,
        tb.parent_task_id,
        
        -- Get detailed metrics from the performance table
        tp.task_status_category,
        tp.performance_grade,
        tp.health_score,
        tp.response_time_days,
        tp.delay_days,
        tp.complexity_score,
        tp.urgency_score,
        tp.activity_score,
        
        -- key points in life cycle
        ts_created.created_at as creation_timestamp,
        ts_assigned.min_assigned_at as first_assignment_timestamp,
        ts_assigned.max_assigned_at as last_assignment_timestamp,
        ts_modified.max_modified_at as last_modification_timestamp,
        ts_completed.completed_at as completion_timestamp,
        
        -- Life cycle duration calculation
        case 
            when ts_assigned.min_assigned_at is not null then
                date_diff('hour', tb.created_at, ts_assigned.min_assigned_at)
            else null
        end as hours_to_assignment,
        
        case 
            when tb.completed_at is not null and ts_assigned.min_assigned_at is not null then
                date_diff('hour', ts_assigned.min_assigned_at, tb.completed_at)
            else null
        end as hours_assigned_to_completion,
        
        case 
            when tb.completed_at is not null then
                date_diff('hour', tb.created_at, tb.completed_at)
            else 
                date_diff('hour', tb.created_at, current_timestamp)
        end as total_lifecycle_hours,
        
        -- Activity frequency analysis
        ts_activity.total_story_events,
        ts_activity.unique_action_types,
        ts_activity.days_with_activity,
        
        case 
            when date_diff('day', tb.created_at, coalesce(tb.completed_at, current_timestamp)) > 0 then
                round(ts_activity.total_story_events * 1.0 / 
                      date_diff('day', tb.created_at, coalesce(tb.completed_at, current_timestamp)), 2)
            else ts_activity.total_story_events
        end as avg_daily_activity_rate
        
    from task_base tb
    left join task_performance tp on tb.task_id = tp.task_id
    
    -- Creation time (should be equal to created_at of task table, but verified from story table)
    left join (
        select target_task_id, min(created_at) as created_at
        from task_stories 
        where action_taken = 'created'
        group by 1
    ) ts_created on tb.task_id = ts_created.target_task_id
    
    -- Allocate time points
    left join (
        select 
            target_task_id,
            min(created_at) as min_assigned_at,
            max(created_at) as max_assigned_at,
            count(*) as assignment_count
        from task_stories 
        where action_taken = 'assigned'
        group by 1
    ) ts_assigned on tb.task_id = ts_assigned.target_task_id
    
    -- last modified time
    left join (
        select 
            target_task_id,
            max(created_at) as max_modified_at
        from task_stories 
        group by 1
    ) ts_modified on tb.task_id = ts_modified.target_task_id
    
    -- Completion time (obtained from story table)
    left join (
        select 
            target_task_id,
            min(created_at) as completed_at
        from task_stories 
        where action_taken = 'completed'
        group by 1
    ) ts_completed on tb.task_id = ts_completed.target_task_id
    
    -- activity statistics
    left join (
        select 
            target_task_id,
            count(*) as total_story_events,
            count(distinct action_taken) as unique_action_types,
            count(distinct date(created_at)) as days_with_activity
        from task_stories
        group by 1
    ) ts_activity on tb.task_id = ts_activity.target_task_id
),

-- Life cycle stage classification and efficiency analysis
lifecycle_efficiency_analysis as (
    select 
        *,
        
        -- Life cycle efficiency classification
        case 
            when is_completed then
                case 
                    when hours_to_assignment <= 24 and hours_assigned_to_completion <= 168 then 'highly_efficient'  -- 1 day allocated, 1 week to complete
                    when hours_to_assignment <= 72 and hours_assigned_to_completion <= 336 then 'efficient'  -- 3 days allocated, 2 weeks to complete
                    when hours_to_assignment <= 168 and hours_assigned_to_completion <= 720 then 'moderate'  -- 1 week allocated, completed in 1 month
                    when hours_to_assignment <= 336 then 'slow_start'  -- Distributed in 2 weeks
                    when hours_assigned_to_completion > 720 then 'slow_completion'  -- Completed over 1 month
                    else 'inefficient'
                end
            else
                case 
                    when hours_to_assignment is null and total_lifecycle_hours > 168 then 'stalled_unassigned'  -- Not allocated for more than 1 week
                    when hours_to_assignment is not null and total_lifecycle_hours > 720 then 'stalled_assigned'  -- Assigned but not completed for more than 1 month
                    when urgency_score >= 4 and total_lifecycle_hours > 72 then 'urgent_delayed'  -- urgent but delayed
                    else 'in_progress'
                end
        end as lifecycle_efficiency_category,
        
        -- Task activity analysis
        case 
            when avg_daily_activity_rate >= 2.0 then 'very_active'
            when avg_daily_activity_rate >= 1.0 then 'active'
            when avg_daily_activity_rate >= 0.5 then 'moderate_activity'
            when avg_daily_activity_rate >= 0.1 then 'low_activity'
            else 'dormant'
        end as activity_level,
        
        -- life cycle health score
        least(100, greatest(0,
            -- Timeliness score (40%)
            (case 
                when is_completed and delay_days = 0 then 40
                when is_completed and delay_days <= 2 then 30
                when is_completed and delay_days <= 7 then 20
                when is_completed then 10
                when not is_completed and due_date > current_date then 35
                when not is_completed and due_date = current_date then 25
                else 5
            end) +
            -- Responsiveness score (30%)
            (case 
                when response_time_days <= 1 then 30
                when response_time_days <= 3 then 25
                when response_time_days <= 7 then 20
                when response_time_days <= 14 then 15
                when response_time_days is not null then 10
                else 5
            end) +
            -- Activity score (20%)
            (activity_score * 4) +
            -- Complexity adaptability score (10%)
            (case 
                when complexity_score = 1 and total_lifecycle_hours <= 168 then 10  -- Simple tasks within 1 week
                when complexity_score = 2 and total_lifecycle_hours <= 336 then 10  -- Medium tasks within 2 weeks
                when complexity_score = 3 and total_lifecycle_hours <= 720 then 10  -- Complex tasks within 1 month
                when total_lifecycle_hours <= 72 then 8  -- Any task within 3 days
                else 5
            end)
        )) as lifecycle_health_score,
        
        -- Life cycle stage identification
        case 
            when not is_completed and assignee_user_id is null then 'backlog'
            when not is_completed and assignee_user_id is not null and 
                 date_diff('day', coalesce(first_assignment_timestamp, created_at), current_timestamp) <= 1 then 'newly_assigned'
            when not is_completed and assignee_user_id is not null and 
                 date_diff('day', last_modification_timestamp, current_timestamp) <= 7 then 'active_development'
            when not is_completed and assignee_user_id is not null and 
                 date_diff('day', last_modification_timestamp, current_timestamp) > 7 then 'stagnant'
            when is_completed and delay_days = 0 then 'completed_on_time'
            when is_completed and delay_days > 0 then 'completed_delayed'
            else 'unknown_state'
        end as current_lifecycle_stage
        
    from task_lifecycle_stages
),

-- Pattern recognition and anomaly detection
lifecycle_pattern_analysis as (
    select 
        *,
        
        -- Abnormal pattern recognition
        trim(
            case when hours_to_assignment > 336 then 'delayed_assignment, ' else '' end ||
            case when hours_assigned_to_completion > 1440 then 'prolonged_execution, ' else '' end ||
            case when avg_daily_activity_rate < 0.1 and not is_completed then 'dormant_task, ' else '' end ||
            case when complexity_score = 1 and total_lifecycle_hours > 336 then 'overengineered_simple, ' else '' end ||
            case when urgency_score >= 4 and response_time_days > 3 then 'urgent_ignored, ' else '' end ||
            case when parent_task_id is not null and total_lifecycle_hours > 720 then 'blocked_subtask, ' else '' end ||
            case when delay_days > 14 then 'severely_delayed, ' else '' end ||
            case when total_story_events > 50 then 'high_churn, ' else '' end,
            ', '
        ) as anomaly_patterns,
        
        -- successful pattern recognition
        trim(
            case when lifecycle_efficiency_category = 'highly_efficient' then 'fast_track, ' else '' end ||
            case when is_completed and delay_days = 0 and performance_grade = 'excellent' then 'exemplary_execution, ' else '' end ||
            case when avg_daily_activity_rate >= 1.0 and is_completed then 'consistent_progress, ' else '' end ||
            case when response_time_days <= 1 and hours_assigned_to_completion <= 168 then 'rapid_delivery, ' else '' end ||
            case when complexity_score = 3 and lifecycle_health_score >= 80 then 'complex_mastery, ' else '' end ||
            case when urgency_score >= 4 and delay_days = 0 then 'urgent_success, ' else '' end,
            ', '
        ) as success_patterns,
        
        -- Opportunities for improvement
        trim(
            case when hours_to_assignment > 72 then 'faster_assignment, ' else '' end ||
            case when activity_level in ('low_activity', 'dormant') then 'increase_engagement, ' else '' end ||
            case when delay_days > 0 then 'improve_time_management, ' else '' end ||
            case when response_time_days > 3 then 'enhance_responsiveness, ' else '' end ||
            case when lifecycle_health_score < 60 then 'overall_process_improvement, ' else '' end ||
            case when total_story_events < 3 and not is_completed then 'add_progress_updates, ' else '' end,
            ', '
        ) as improvement_opportunities,
        
        -- Matching task complexity with actual execution time
        case 
            when complexity_score = 1 and total_lifecycle_hours <= 72 then 'appropriate_simple'
            when complexity_score = 2 and total_lifecycle_hours between 73 and 336 then 'appropriate_medium'
            when complexity_score = 3 and total_lifecycle_hours between 337 and 720 then 'appropriate_complex'
            when total_lifecycle_hours < complexity_score * 72 then 'faster_than_expected'
            when total_lifecycle_hours > complexity_score * 240 then 'slower_than_expected'
            else 'within_range'
        end as complexity_execution_match
        
    from lifecycle_efficiency_analysis
),

-- Final data validation and benchmark comparison
final_lifecycle_analysis as (
    select 
        lpa.*,
        
        -- Add project and user context
        pi.project_name,
        pi.team_id,
        pi.overall_health_score as project_health_score,
        ui.user_name as assignee_name,
        ui.performance_grade as assignee_performance_grade,
        
        -- Relative performance indicators (compared to project average)
        case 
            when lpa.lifecycle_health_score > pi.overall_health_score + 20 then 'above_project_average'
            when lpa.lifecycle_health_score > pi.overall_health_score + 10 then 'slightly_above_average'
            when lpa.lifecycle_health_score >= pi.overall_health_score - 10 then 'project_average'
            when lpa.lifecycle_health_score >= pi.overall_health_score - 20 then 'slightly_below_average'
            else 'below_project_average'
        end as relative_performance_vs_project,
        
        -- Data quality verification
        case 
            when lpa.task_id is null or lpa.task_name is null then false
            when lpa.lifecycle_health_score < 0 or lpa.lifecycle_health_score > 100 then false
            when lpa.total_lifecycle_hours < 0 then false
            when lpa.hours_to_assignment < 0 then false
            when lpa.hours_assigned_to_completion < 0 then false
            when lpa.avg_daily_activity_rate < 0 then false
            when lpa.is_completed and lpa.completion_timestamp is null and lpa.completed_at is null then false
            else true
        end as is_valid_record
        
    from lifecycle_pattern_analysis lpa
    left join staging.stg_asana__project_task pt on lpa.task_id = pt.task_id
    left join project_info pi on pt.project_id = pi.project_id
    left join user_info ui on cast(lpa.assignee_user_id as varchar) = ui.user_id
)

select *
from final_lifecycle_analysis
where is_valid_record = true
order by lifecycle_health_score desc, total_lifecycle_hours asc, task_id
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 3975 | 3975 | 0 | 0 | 19 | 19 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"task_id":"1001301507647","assignee_user_id":"497986524243","parent_task_id":"null","team_id":"6517144802034"}</code> |
| K2 | <code>{"task_id":"1008996167568","assignee_user_id":"7673674693762","parent_task_id":"null","team_id":"6880279086178"}</code> |
| K3 | <code>{"task_id":"1013090128121","assignee_user_id":"182281855555","parent_task_id":"4882419363991","team_id":"4089666169022"}</code> |
| K4 | <code>{"task_id":"1023238231632","assignee_user_id":"null","parent_task_id":"null","team_id":"6063407318472"}</code> |
| K5 | <code>{"task_id":"1024159933120","assignee_user_id":"17232646697","parent_task_id":"null","team_id":"4517815787122"}</code> |
| K6 | <code>{"task_id":"1040738293584","assignee_user_id":"7354068461379","parent_task_id":"null","team_id":"4177995432076"}</code> |
| K7 | <code>{"task_id":"1040738293584","assignee_user_id":"7354068461379","parent_task_id":"null","team_id":"5216022753601"}</code> |
| K8 | <code>{"task_id":"1027806464447","assignee_user_id":"8285656177499","parent_task_id":"null","team_id":"9827128724268"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| task_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| due_date | 0 | 0 | 0 | TIMESTAMP WITH TIME ZONE | TIMESTAMP WITH TIME ZONE |
| assignee_user_id | 0 | 0 | 0 | BIGINT | BIGINT |
| parent_task_id | 0 | 0 | 0 | BIGINT | BIGINT |
| task_status_category | 0 | 0 | 0 | VARCHAR | VARCHAR |
| performance_grade | 0 | 0 | 0 | VARCHAR | VARCHAR |
| health_score | 0 | 0 | 0 | BIGINT | BIGINT |
| response_time_days | 0 | 0 | 0 | BIGINT | BIGINT |
| delay_days | 0 | 0 | 0 | BIGINT | BIGINT |
| complexity_score | 0 | 0 | 0 | INTEGER | INTEGER |
| urgency_score | 0 | 0 | 0 | INTEGER | INTEGER |
| activity_score | 0 | 0 | 0 | INTEGER | INTEGER |
| creation_timestamp | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| first_assignment_timestamp | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| last_assignment_timestamp | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| last_modification_timestamp | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| completion_timestamp | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| hours_assigned_to_completion | 0 | 0 | 0 | BIGINT | BIGINT |
| total_lifecycle_hours | 2431 | 2431 | 2431 | BIGINT | BIGINT |
| unique_action_types | 722 | 722 | 722 | BIGINT | BIGINT |
| days_with_activity | 722 | 722 | 722 | BIGINT | BIGINT |
| avg_daily_activity_rate | 2727 | 2727 | 2727 | DOUBLE | DOUBLE |
| lifecycle_efficiency_category | 0 | 0 | 0 | VARCHAR | VARCHAR |
| activity_level | 224 | 224 | 224 | VARCHAR | VARCHAR |
| lifecycle_health_score | 0 | 0 | 0 | INTEGER | INTEGER |
| current_lifecycle_stage | 338 | 338 | 338 | VARCHAR | VARCHAR |
| anomaly_patterns | 650 | 650 | 650 | VARCHAR | VARCHAR |
| success_patterns | 0 | 0 | 0 | VARCHAR | VARCHAR |
| improvement_opportunities | 426 | 426 | 426 | VARCHAR | VARCHAR |
| complexity_execution_match | 0 | 0 | 0 | VARCHAR | VARCHAR |
| project_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| team_id | 0 | 0 | 0 | BIGINT | BIGINT |
| project_health_score | 0 | 0 | 0 | INTEGER | INTEGER |
| assignee_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| assignee_performance_grade | 0 | 0 | 0 | VARCHAR | VARCHAR |

total_lifecycle_hours 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 10006 | 887 |
| K2 | 10006 | 887 |
| K3 | 10006 | 887 |

unique_action_types 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0 | null |
| K3 | 0 | null |
| K4 | 0 | null |

days_with_activity 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0 | null |
| K3 | 0 | null |
| K4 | 0 | null |

avg_daily_activity_rate 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0.0 | null |
| K2 | 0.01 | 0.08 |
| K3 | 0.0 | null |

activity_level 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K5 | dormant | low_activity |
| K6 | dormant | low_activity |
| K7 | dormant | low_activity |

current_lifecycle_stage 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | stagnant | unknown_state |
| K3 | stagnant | unknown_state |
| K8 | stagnant | unknown_state |

anomaly_patterns 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | dormant_task | <code></code> |
| K3 | dormant_task, overengineered_simple, blocked_subtask | overengineered_simple, blocked_subtask |
| K5 | dormant_task | <code></code> |

improvement_opportunities 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | increase_engagement, overall_process_improvement, add_progress_updates | increase_engagement, overall_process_improvement |
| K3 | increase_engagement, overall_process_improvement, add_progress_updates | increase_engagement, overall_process_improvement |
| K8 | increase_engagement, overall_process_improvement, add_progress_updates | increase_engagement, overall_process_improvement |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>7列；[{"column":"response_time_days","table_rows":3975},{"column":"creation_timestamp","table_rows":3975},{"column":"first_assignment_timestamp","table_rows":3975}]</code> |
| A3_constant_nonnull_column | <code>2列；[{"column":"activity_score","value":"1"},{"column":"is_valid_record","value":"true"}]</code> |
| A4_equal_columns | <code>1组；[{"columns":["unique_action_types","days_with_activity"],"nonnull_equal_rows":3975,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>1组；[{"columns":["unique_action_types","days_with_activity"],"nonnull_equal_rows":3975,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| C9_agent_runtime_text | <code>S4:3 CURRENT_TIMESTAMP；命中数=7</code> |
| C9_gold_runtime_text | <code>S5:87 current_timestamp；命中数=8</code> |
| C9_contract_runtime_text | <code>S3:1393 current time；命中数=6</code> |
| D10_keyword_in_any_result_field | <code>命中数=2；assistant_trajectory 'asana__task_lifecycle_analysis':'''WITH story_agg AS (SELECT target_task_id,MIN(created_at) FILTER(WHERE action_taken='created') creation_timestamp,MIN(created_at) FILTER(WHERE action_taken='assigned') first_assignment_timestamp,MAX(created_at) FILTER(WHERE action_taken='assigned') last_assignment_timestamp,MAX(created_at) last_modification_timestamp,MIN(created_at) FILTER(WHERE action_taken='completed') completion_timestamp,COUNT(*)::BIGINT total_story_events,COUNT(DISTINCT action_taken)::BIGINT unique_action_types,COUNT(DISTINCT created_at::DATE)::BIGINT days_with_activity FROM intermediate.int_asana__task_story WHERE action_taken IS NOT NULL GROUP BY target_task_id),</code> |

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
'asana__task_lifecycle_analysis':'''WITH story_agg AS (SELECT target_task_id,MIN(created_at) FILTER(WHERE action_taken='created') creation_timestamp,MIN(created_at) FILTER(WHERE action_taken='assigned') first_assignment_timestamp,MAX(created_at) FILTER(WHERE action_taken='assigned') last_assignment_timestamp,MAX(created_at) last_modification_timestamp,MIN(created_at) FILTER(WHERE action_taken='completed') completion_timestamp,COUNT(*)::BIGINT total_story_events,COUNT(DISTINCT action_taken)::BIGINT unique_action_types,COUNT(DISTINCT created_at::DATE)::BIGINT days_with_activity FROM intermediate.int_asana__task_story WHERE action_taken IS NOT NULL GROUP BY target_task_id),
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
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__task_lifecycle_analysis.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/sql/marts/asana__task_lifecycle_analysis.sql`
- S6: `records/006_contract_impl-008.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/result.md`
- S10: `data/021_packages_work/021_impl-008_asana__task_lifecycle_analysis/021_impl-008_asana__task_lifecycle_analysis.json`
- S11: `data/005_cs_work/impl-008/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-008/asana.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions`
