# impl-008_asana__task_lifecycle_analysis（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**Unstated Choice**；把握：高；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`A`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 722, "cell_scale": 3356}, "L1": {"row_scale": 722, "cell_scale": 3356}, "L2": {"row_scale": 722, "cell_scale": 3356}, "L3": {"row_scale": 722, "cell_scale": 3356}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| unique_action_types | Unstated Choice | 参与 | 0 | 722 | 4 |
| days_with_activity | Unstated Choice | 参与 | 0 | 722 | 4 |
| missing_activity_null_policy | Unstated Choice | 主要 | 0 | 1148 | 4 |
| modification_source | Intent Misreading | 参与 | 0 | 338 | 4 |

### 契约原句（所有点共用，逐字回查event1）

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

### 逐点结论

#### unique_action_types

参与；**Unstated Choice**；把握高。

P：distinct action_taken计算正确；没有故事匹配时unique_action_types补0，gold保留NULL。契约没有缺组默认值。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 722 | 722 | 3356 | 2634 |
| L1 | 722 | 722 | 3356 | 2634 |
| L2 | 722 | 722 | 3356 | 2634 |
| L3 | 722 | 722 | 3356 | 2634 |

重跑：`records/021_supplement_reruns_impl-008_asana__task_lifecycle_analysis.json` / `unique_action_types`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__task_lifecycle_analysis.sql` / `SQL.text`（sql）：

```text
COALESCE(s.unique_action_types,0)
```

否定披露的审计范围：finish event 53 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### days_with_activity

参与；**Unstated Choice**；把握高。

P：distinct calendar dates计算正确；没有故事匹配时days_with_activity补0，gold保留NULL。契约没有缺组默认值。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 722 | 722 | 3356 | 2634 |
| L1 | 722 | 722 | 3356 | 2634 |
| L2 | 722 | 722 | 3356 | 2634 |
| L3 | 722 | 722 | 3356 | 2634 |

重跑：`records/021_supplement_reruns_impl-008_asana__task_lifecycle_analysis.json` / `days_with_activity`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__task_lifecycle_analysis.sql` / `SQL.text`（sql）：

```text
COALESCE(s.days_with_activity,0)
```

否定披露的审计范围：finish event 53 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### missing_activity_null_policy

主要；**Unstated Choice**；把握高。

P：没有故事时活动计数、强度及校验使用0而非NULL；契约没有缺组默认政策。修复同一缺失政策沿指标/过滤链重算，不把多个互不相关的字段合并。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 722 | 722 | 3356 | 2208 |
| L1 | 722 | 722 | 3356 | 2208 |
| L2 | 722 | 722 | 3356 | 2208 |
| L3 | 722 | 722 | 3356 | 2208 |

重跑：`records/021_supplement_reruns_impl-008_asana__task_lifecycle_analysis.json` / `missing_activity_null_policy`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__task_lifecycle_analysis.sql` / `SQL.text`（sql）：

```text
AND avg_daily_activity_rate>=0 AND
```

否定披露的审计范围：finish event 53 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### modification_source

参与；**Intent Misreading**；把握高。

P：latest modification可直接取task.modified_at。契约要求最近故事活动时间；已有候选源，偏差在明文来源限定而非解析。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 722 | 722 | 3356 | 3018 |
| L1 | 722 | 722 | 3356 | 3018 |
| L2 | 722 | 722 | 3356 | 3018 |
| L3 | 722 | 722 | 3356 | 3018 |

重跑：`records/021_supplement_reruns_impl-008_asana__task_lifecycle_analysis.json` / `modification_source`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__task_lifecycle_analysis.sql` / `SQL.text`（sql）：

```text
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

否定披露的审计范围：finish event 53 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-008/docs/data_contract.yaml`，行[1382, 1523]；材料包 `records/021_packages/021_impl-008_asana__task_lifecycle_analysis.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__task_lifecycle_analysis.sql`；SHA-256 `115d619f2c2289942217104e31a419195aff722667530f48a205e51f7b569567`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/53.json` / event 53。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共2条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 4，失败=True。
  - `records/021_supplement_queries.json` / index 7，失败=False。

## 不确定或没查到的（含规则问题）

- 未发现需要增改手册的规则问题。没有将未知信息补成数据事实；证据范围以所列契约、交付代码、轨迹及重跑为限。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
