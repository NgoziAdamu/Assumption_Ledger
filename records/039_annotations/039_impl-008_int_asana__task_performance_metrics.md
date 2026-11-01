# impl-008_int_asana__task_performance_metrics（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**Intent Misreading**；把握：高；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`C`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 91, "cell_scale": 91}, "L1": {"row_scale": 91, "cell_scale": 91}, "L2": {"row_scale": 91, "cell_scale": 91}, "L3": {"row_scale": 91, "cell_scale": 91}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| timestamp_status | Intent Misreading | 主要 | 91 | 91 | 4 |

### 契约原句（所有点共用，逐字回查event1）

```yaml
    - name: int_asana__task_performance_metrics
      description: Task performance metrics with lifecycle status, response/delay days, activity/urgency/complexity scores, validity flag, performance grade, and health score; only valid records are output.
      grain: One row per task_id (only records with is_valid_record = true)
      source_models:
      - staging.stg_asana__task
      - intermediate.int_asana__task_open_length
      - intermediate.int_asana__task_story
      business_logic: 'Data preparation: - Use tasks where created_at is present from staging.stg_asana__task. - Bring per-task durations from intermediate.int_asana__task_open_length (days_open, days_since_first_assignment, days_since_last_assignment). - Use stories from intermediate.int_asana__task_story where action_taken is present. Timeline and status: - For each task_id, left join open-length metrics. - Assign task_status_category using ordered rules: - unassigned: no assignee and not completed - assigned_active: has assignee and not completed - completed_on_time: completed_at on or before due_date - completed_late: completed_at after due_date - overdue: not completed and today is after the due_date’s calendar date - otherwise active - first_assigned_at: the earliest story timestamp where action_taken = ''assigned'' for this task; null if none. - last_activity_at: the later of modified_at and the latest story timestamp for the task; if no story exists, use created_at. Metrics: - response_time_days: number of days from created_at to first_assigned_at when first_assigned_at exists; otherwise null (expected non-negative). - delay_days: - If due_date exists and the task is completed late: days between due_date and completed_at. - If due_date exists and the task is still open and past due today: days between due_date and today. - Otherwise 0 (never negative). - activity_score (1–5) based on days since last_activity_at: - 0–1 days → 5; 2–3 → 4; 4–7 → 3; 8–14 → 2; else 1. - urgency_score (1–5) only when due_date exists and the task is not completed: - due in 0–1 days → 5; 2–3 → 4; 4–7 → 3; 8–30 → 2; else 1; otherwise 1. - complexity_score (1–3) from description length (treat missing description as empty): - >500 chars → 3; >100 → 2; else 1. Constraints and classifications: - is_valid_record is true only if task_name is not blank, created_at is present, days_open ≥ 0, response_time_days is not negative (null allowed), and delay_days ≥ 0. - performance_grade: - completed with delay_days = 0 and response_time_days ≤ 1 → excellent - completed with delay_days ≤ 2 and response_time_days ≤ 2 → good - completed with delay_days ≤ 5 → fair - completed with delay_days > 5 → poor - not completed and status is overdue → at_risk - otherwise pending. Health score: - Start from 0 and add components, then clamp to [0,100]: - Activity: add 20 points per activity_score unit (1–5). - Timeliness: add 25 if delay_days = 0; otherwise subtract 5 points per day of delay down to 0. - Responsiveness: add 25 if response_time_days ≤ 1; otherwise subtract 3 points per day down to 0. - Assignment: add 15 if an assignee is present; else 0. - Description: add 15 if description is present; else 0. Output: - Return rows with is_valid_record = true. - Sort by health_score (descending), then urgency_score (descending), then task_id.'
      columns:
      - name: task_id
        data_type: VARCHAR
        description: Unique task identifier; exactly one output row per task_id that passes validity checks
        tests:
        - not_null
        - unique
      - name: task_name
        data_type: VARCHAR
        description: Task display name/title sourced from stg_asana__task; must be non-null and non-blank
      - name: task_description
        data_type: VARCHAR
        description: Task description text from stg_asana__task; presence contributes to health_score
      - name: created_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Original task creation timestamp; non-null by filter and used in multiple day-based calculations
        tests:
        - not_null
      - name: modified_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Most recent task modification timestamp used to determine last_activity_at; may be null
      - name: completed_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Timestamp when the task was completed; used to label completed_on_time vs completed_late and to compute delay_days
      - name: due_date
        data_type: TIMESTAMP WITH TIME ZONE
        description: Target due timestamp used for status, urgency_score, and delay_days; overdue checks compare the due date’s calendar date to today
      - name: is_completed
        data_type: BOOLEAN
        description: Completion flag from stg_asana__task used in status, delay_days, urgency_score, and performance_grade
      - name: assignee_user_id
        data_type: BIGINT
        description: Assigned user id (nullable); presence affects status and adds +15 to health_score
      - name: task_status_category
        data_type: VARCHAR
        description: 'Lifecycle status from ordered rules: unassigned, assigned_active, completed_on_time, completed_late, overdue, or active'
      - name: first_assigned_at
        data_type: TIMESTAMP
        description: Earliest story timestamp where action_taken='assigned' for this task; null if never assigned
      - name: last_activity_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Later of modified_at and the latest story timestamp; if no story exists, uses created_at
      - name: days_open
        data_type: BIGINT
        description: Non-negative days the task has been open sourced from int_asana__task_open_length
      - name: days_since_first_assignment
        data_type: BIGINT
        description: Days since the first assignment sourced from int_asana__task_open_length
      - name: days_since_last_assignment
        data_type: BIGINT
        description: Days since the most recent assignment sourced from int_asana__task_open_length
      - name: response_time_days
        data_type: BIGINT
        description: Days from created_at to first_assigned_at; null if never assigned; must not be negative
      - name: delay_days
        data_type: BIGINT
        description: Days overdue (0 if due_date absent or on time); completed late uses days between due_date and completed_at; open overdue uses days between due_date and today
      - name: activity_score
        data_type: INTEGER
        description: 1–5 score based on days since last_activity_at vs now (≤1→5, ≤3→4, ≤7→3, ≤14→2, else 1)
      - name: urgency_score
        data_type: INTEGER
        description: 1–5 score when due_date present and not completed, based on days until due_date thresholds; otherwise 1
      - name: complexity_score
        data_type: INTEGER
        description: '1–3 score based on description length: >500→3, >100→2, else 1'
      - name: is_valid_record
        data_type: BOOLEAN
        description: True only if task_name not blank, created_at present, and days_open/response_time_days/delay_days are not negative
        tests:
        - accepted_values:
            values:
            - true
      - name: performance_grade
        data_type: VARCHAR
        description: 'Classification: excellent, good, fair, poor, at_risk, or pending per rules combining completion, delay_days, and response_time_days'
      - name: health_score
        data_type: BIGINT
        description: Overall 0–100 score from weighted components (activity, timeliness, responsiveness, assignment, description) clamped to [0,100]
```

### 逐点结论

#### timestamp_status

主要；**Intent Misreading**；把握高。

P：完成是否及时可把completed_at与due_date都截为DATE。契约在完成状态使用时间戳比较，只有overdue使用日历日。截日会把同日迟交算成及时；按明文算法归Intent。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 91 | 0 | 91 | 0 |
| L1 | 91 | 0 | 91 | 0 |
| L2 | 91 | 0 | 91 | 0 |
| L3 | 91 | 0 | 91 | 0 |

重跑：`records/021_reruns_impl-008_int_asana__task_performance_metrics.json` / `timestamp_status`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/intermediate/int_asana__task_performance_metrics.sql` / `SQL.text`（sql）：

```text
WHEN is_completed AND completed_at::DATE <= due_date::DATE THEN 'completed_on_time'
 WHEN is_completed AND completed_at::DATE > due_date::DATE THEN 'completed_late'
```

否定披露的审计范围：finish event 53 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-008/docs/data_contract.yaml`，行[688, 774]；材料包 `records/021_packages/021_impl-008_int_asana__task_performance_metrics.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/intermediate/int_asana__task_performance_metrics.sql`；SHA-256 `91df3c8e5530cf06cd6a1a3934963ff5911ea1b506bfeb58d8ce4a2659021c6a`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/53.json` / event 53。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共2条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 1，失败=True。
  - `records/021_supplement_queries.json` / index 5，失败=False。

## 不确定或没查到的（含规则问题）

- 未发现需要增改手册的规则问题。没有将未知信息补成数据事实；证据范围以所列契约、交付代码、轨迹及重跑为限。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
