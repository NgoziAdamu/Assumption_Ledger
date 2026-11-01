# impl-008_asana__project_analytics（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**Intent Misreading**；把握：高；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`C`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 472, "cell_scale": 472}, "L1": {"row_scale": 472, "cell_scale": 472}, "L2": {"row_scale": 472, "cell_scale": 472}, "L3": {"row_scale": 472, "cell_scale": 472}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| time_management | Intent Misreading | 主要 | 472 | 472 | 4 |

### 契约原句（所有点共用，逐字回查event1）

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

### 逐点结论

#### time_management

主要；**Intent Misreading**；把握高。

P：time_management_score由完成比例及剩余天数决定。契约明确按schedule_forecast各档映射25/20/15/10/5，其他12；改变算法而非只改标签。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 472 | 0 | 472 | 0 |
| L1 | 472 | 0 | 472 | 0 |
| L2 | 472 | 0 | 472 | 0 |
| L3 | 472 | 0 | 472 | 0 |

重跑：`records/021_reruns_impl-008_asana__project_analytics.json` / `time_management`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__project_analytics.sql` / `SQL.text`（sql）：

```text
CASE WHEN completion_percentage=100 THEN 25 WHEN remaining_days<0 THEN 5 ELSE 12 END time_management_score
```

否定披露的审计范围：finish event 53 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-008/docs/data_contract.yaml`，行[1071, 1214]；材料包 `records/021_packages/021_impl-008_asana__project_analytics.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__project_analytics.sql`；SHA-256 `a2adacb9678a6ece4f6d52d650233bebfcddaaaa95eebf2442d3d76e98ec81cb`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/53.json` / event 53。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共2条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 3，失败=True。
  - `records/021_supplement_queries.json` / index 6，失败=False。

## 不确定或没查到的（含规则问题）

- 未发现需要增改手册的规则问题。没有将未知信息补成数据事实；证据范围以所列契约、交付代码、轨迹及重跑为限。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
