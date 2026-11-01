# impl-008_int_asana__project_health_indicators（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**代码写错**；把握：高；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`C`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 43, "cell_scale": 1190}, "L1": {"row_scale": 43, "cell_scale": 1190}, "L2": {"row_scale": 43, "cell_scale": 1190}, "L3": {"row_scale": 43, "cell_scale": 1190}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| count_joined_tasks | Unstated Choice | 参与 | 20 | 132 | 4 |
| zero_denominator_policy | 代码写错 | 主要 | 23 | 1058 | 4 |

### 契约原句（所有点共用，逐字回查event1）

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

### 逐点结论

#### count_joined_tasks

参与；**Unstated Choice**；把握高。

P：total_tasks按关系表中的关联任务计数，包括未匹配task实体的关系。契约写all linked tasks并LEFT JOIN实体，没有规定孤立关系是否仍是任务；026的021-3指出这一歧义。改为有效task计数是另一可行读法，不把gold读法当数据事实。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 43 | 23 | 1190 | 1058 |
| L1 | 43 | 23 | 1190 | 1058 |
| L2 | 43 | 23 | 1190 | 1058 |
| L3 | 43 | 23 | 1190 | 1058 |

重跑：`records/021_reruns_impl-008_int_asana__project_health_indicators.json` / `count_joined_tasks`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/intermediate/int_asana__project_health_indicators.sql` / `SQL.text`（sql）：

```text
pt.task_id,t.is_completed
```

否定披露的审计范围：finish event 53 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### zero_denominator_policy

主要；**代码写错**；把握高。

原代码已写CASE WHEN total_tasks=0 THEN 0及六个最终COALESCE(...,0)，明确表达零分母补0的正确意图；但is_valid_record和部分标签仍用补0之前的NULL百分比，WHERE提前排除了23个项目。修复将同一零分母政策放回百分比计算层并沿原链重算，属于正确意图未连到校验的代码错误。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 43 | 20 | 1190 | 132 |
| L1 | 43 | 20 | 1190 | 132 |
| L2 | 43 | 20 | 1190 | 132 |
| L3 | 43 | 20 | 1190 | 132 |

重跑：`records/021_reruns_impl-008_int_asana__project_health_indicators.json` / `zero_denominator_policy`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/intermediate/int_asana__project_health_indicators.sql` / `SQL.text`（sql）：

```text
SELECT *,ROUND(100.0*completed_tasks/NULLIF(total_tasks,0),2) completion_percentage,ROUND(100.0*assigned_tasks/NULLIF(total_tasks,0),2) assignment_percentage,
 ROUND(100.0*overdue_tasks/NULLIF(total_tasks,0),2) overdue_percentage,ROUND(100.0*quality_tasks/NULLIF(completed_tasks,0),2) quality_percentage,
 ROUND(100.0*(overdue_tasks+poor_performance_tasks+delayed_tasks)/NULLIF(total_tasks,0),2) risk_percentage,
 ROUND(100.0*(recent_task_creation+recent_task_completion)/NULLIF(total_tasks,0),2) activity_percentage,
```

否定披露的审计范围：finish event 53 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-008/docs/data_contract.yaml`，行[295, 445]；材料包 `records/021_packages/021_impl-008_int_asana__project_health_indicators.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/intermediate/int_asana__project_health_indicators.sql`；SHA-256 `ffa172c3308a69b841e9d68348fd4c6b1cdf5323bd3e738667dadb34f8ea2879`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/53.json` / event 53。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共1条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 0，失败=False。

## 不确定或没查到的（含规则问题）

- 规则问题：零分母可读为Intent（契约明文补0）；本次选代码写错，因为交付代码自身反复明确补0，错误在计算链应用位置。
- count_joined_tasks不是Data Misconception；缺少能裁定孤立关系语义的契约条款。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
