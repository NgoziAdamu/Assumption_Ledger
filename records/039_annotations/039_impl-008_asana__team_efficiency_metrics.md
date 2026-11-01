# impl-008_asana__team_efficiency_metrics（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**多因并列**；把握：高；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`多因并列（C、D）`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 44, "cell_scale": 396}, "L1": {"row_scale": 44, "cell_scale": 396}, "L2": {"row_scale": 44, "cell_scale": 396}, "L3": {"row_scale": 44, "cell_scale": 396}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| medium_projects | Intent Misreading | 并列 | 0 | 44 | 4 |
| small_projects | Intent Misreading | 并列 | 0 | 44 | 4 |
| developing_performers | Quiet Downgrade | 并列 | 0 | 44 | 4 |
| avg_tasks_per_member | Quiet Downgrade | 并列 | 0 | 44 | 4 |
| collaboration_efficiency_score | Quiet Downgrade | 并列 | 0 | 44 | 4 |
| resource_optimization_score | Quiet Downgrade | 并列 | 0 | 44 | 4 |
| overall_team_efficiency_score | Quiet Downgrade | 并列 | 0 | 44 | 4 |
| improvement_recommendations | Quiet Downgrade | 并列 | 0 | 44 | 4 |
| team_strengths | Quiet Downgrade | 并列 | 0 | 44 | 4 |

### 契约原句（所有点共用，逐字回查event1）

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

### 逐点结论

#### medium_projects

并列；**Intent Misreading**；把握高。

P：medium_projects按实际任务量分桶。契约本层project_size_category固定medium，分类来源与该规则不符。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 44 | 44 | 396 | 352 |
| L1 | 44 | 44 | 396 | 352 |
| L2 | 44 | 44 | 396 | 352 |
| L3 | 44 | 44 | 396 | 352 |

重跑：`records/021_detailed_reruns_impl-008_asana__team_efficiency_metrics.json` / `medium_projects`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__team_efficiency_metrics.sql` / `SQL.text`（sql）：

```text
COALESCE(ps.medium_projects,0)::BIGINT medium_projects
```

否定披露的审计范围：finish event 53 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### small_projects

并列；**Intent Misreading**；把握高。

P：small_projects按实际任务量分桶。契约本层project_size_category固定medium，分类来源与该规则不符。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 44 | 44 | 396 | 352 |
| L1 | 44 | 44 | 396 | 352 |
| L2 | 44 | 44 | 396 | 352 |
| L3 | 44 | 44 | 396 | 352 |

重跑：`records/021_detailed_reruns_impl-008_asana__team_efficiency_metrics.json` / `small_projects`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__team_efficiency_metrics.sql` / `SQL.text`（sql）：

```text
COALESCE(ps.small_projects,0)::BIGINT small_projects
```

否定披露的审计范围：finish event 53 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### developing_performers

并列；**Quiet Downgrade**；把握高。

developing_performers使用固定0、NULL、空串或不足的评分分量，省略契约要求的统计/分类；CS上游含所需项目和任务事实。候选输入存在而未计算，不能归缺源Choice。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 44 | 44 | 396 | 352 |
| L1 | 44 | 44 | 396 | 352 |
| L2 | 44 | 44 | 396 | 352 |
| L3 | 44 | 44 | 396 | 352 |

重跑：`records/021_detailed_reruns_impl-008_asana__team_efficiency_metrics.json` / `developing_performers`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__team_efficiency_metrics.sql` / `SQL.text`（sql）：

```text
0::BIGINT developing_performers
```

否定披露的审计范围：finish event 53 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### avg_tasks_per_member

并列；**Quiet Downgrade**；把握高。

avg_tasks_per_member使用固定0、NULL、空串或不足的评分分量，省略契约要求的统计/分类；CS上游含所需项目和任务事实。候选输入存在而未计算，不能归缺源Choice。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 44 | 44 | 396 | 352 |
| L1 | 44 | 44 | 396 | 352 |
| L2 | 44 | 44 | 396 | 352 |
| L3 | 44 | 44 | 396 | 352 |

重跑：`records/021_detailed_reruns_impl-008_asana__team_efficiency_metrics.json` / `avg_tasks_per_member`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__team_efficiency_metrics.sql` / `SQL.text`（sql）：

```text
NULL::DOUBLE avg_tasks_per_member
```

否定披露的审计范围：finish event 53 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### collaboration_efficiency_score

并列；**Quiet Downgrade**；把握高。

collaboration_efficiency_score使用固定0、NULL、空串或不足的评分分量，省略契约要求的统计/分类；CS上游含所需项目和任务事实。候选输入存在而未计算，不能归缺源Choice。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 44 | 44 | 396 | 352 |
| L1 | 44 | 44 | 396 | 352 |
| L2 | 44 | 44 | 396 | 352 |
| L3 | 44 | 44 | 396 | 352 |

重跑：`records/021_detailed_reruns_impl-008_asana__team_efficiency_metrics.json` / `collaboration_efficiency_score`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__team_efficiency_metrics.sql` / `SQL.text`（sql）：

```text
0::INTEGER collaboration_efficiency_score
```

否定披露的审计范围：finish event 53 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### resource_optimization_score

并列；**Quiet Downgrade**；把握高。

resource_optimization_score使用固定0、NULL、空串或不足的评分分量，省略契约要求的统计/分类；CS上游含所需项目和任务事实。候选输入存在而未计算，不能归缺源Choice。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 44 | 44 | 396 | 352 |
| L1 | 44 | 44 | 396 | 352 |
| L2 | 44 | 44 | 396 | 352 |
| L3 | 44 | 44 | 396 | 352 |

重跑：`records/021_detailed_reruns_impl-008_asana__team_efficiency_metrics.json` / `resource_optimization_score`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__team_efficiency_metrics.sql` / `SQL.text`（sql）：

```text
0::INTEGER resource_optimization_score
```

否定披露的审计范围：finish event 53 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### overall_team_efficiency_score

并列；**Quiet Downgrade**；把握高。

overall_team_efficiency_score使用固定0、NULL、空串或不足的评分分量，省略契约要求的统计/分类；CS上游含所需项目和任务事实。候选输入存在而未计算，不能归缺源Choice。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 44 | 44 | 396 | 352 |
| L1 | 44 | 44 | 396 | 352 |
| L2 | 44 | 44 | 396 | 352 |
| L3 | 44 | 44 | 396 | 352 |

重跑：`records/021_detailed_reruns_impl-008_asana__team_efficiency_metrics.json` / `overall_team_efficiency_score`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__team_efficiency_metrics.sql` / `SQL.text`（sql）：

```text
(CASE WHEN COALESCE(ps.on_schedule_rate_pct,0)>=90 THEN 25 WHEN ps.on_schedule_rate_pct>=75 THEN 20 WHEN ps.on_schedule_rate_pct>=60 THEN 15 WHEN ps.on_schedule_rate_pct>=40 THEN 10 ELSE 5 END+CASE WHEN COALESCE(ps.avg_quality_rate,0)>=85 THEN 25 WHEN ps.avg_quality_rate>=70 THEN 20 WHEN ps.avg_quality_rate>=55 THEN 15 WHEN ps.avg_quality_rate>=40 THEN 10 ELSE 5 END)::INTEGER overall_team_efficiency_score
```

否定披露的审计范围：finish event 53 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### improvement_recommendations

并列；**Quiet Downgrade**；把握高。

improvement_recommendations使用固定0、NULL、空串或不足的评分分量，省略契约要求的统计/分类；CS上游含所需项目和任务事实。候选输入存在而未计算，不能归缺源Choice。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 44 | 44 | 396 | 352 |
| L1 | 44 | 44 | 396 | 352 |
| L2 | 44 | 44 | 396 | 352 |
| L3 | 44 | 44 | 396 | 352 |

重跑：`records/021_detailed_reruns_impl-008_asana__team_efficiency_metrics.json` / `improvement_recommendations`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__team_efficiency_metrics.sql` / `SQL.text`（sql）：

```text
''::VARCHAR improvement_recommendations
```

否定披露的审计范围：finish event 53 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### team_strengths

并列；**Quiet Downgrade**；把握高。

team_strengths使用固定0、NULL、空串或不足的评分分量，省略契约要求的统计/分类；CS上游含所需项目和任务事实。候选输入存在而未计算，不能归缺源Choice。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 44 | 44 | 396 | 352 |
| L1 | 44 | 44 | 396 | 352 |
| L2 | 44 | 44 | 396 | 352 |
| L3 | 44 | 44 | 396 | 352 |

重跑：`records/021_detailed_reruns_impl-008_asana__team_efficiency_metrics.json` / `team_strengths`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__team_efficiency_metrics.sql` / `SQL.text`（sql）：

```text
''::VARCHAR team_strengths
```

否定披露的审计范围：finish event 53 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-008/docs/data_contract.yaml`，行[1547, 1717]；材料包 `records/021_packages/021_impl-008_asana__team_efficiency_metrics.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-008/agent/dacomp-de-impl-008/sql/marts/asana__team_efficiency_metrics.sql`；SHA-256 `7d2e37f9ba8f26446f850760f2eed58ec9650c52a8a3620b982c3d05249614d9`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-008/agent/.events/sessions/e09988bd-ad17-48-73c30c81028a18b/events/53.json` / event 53。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共2条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 5，失败=True。
  - `records/021_supplement_queries.json` / index 8，失败=False。

## 不确定或没查到的（含规则问题）

- 未发现需要增改手册的规则问题。没有将未知信息补成数据事实；证据范围以所列契约、交付代码、轨迹及重跑为限。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
