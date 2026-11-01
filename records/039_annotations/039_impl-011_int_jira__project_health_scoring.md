# impl-011_int_jira__project_health_scoring（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**已说出的降级**；把握：高；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`D`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 193, "cell_scale": 193}, "L1": {"row_scale": 193, "cell_scale": 193}, "L2": {"row_scale": 193, "cell_scale": 193}, "L3": {"row_scale": 193, "cell_scale": 193}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| overall_health_score | 已说出的降级 | 主要 | 193 | 193 | 1 |

### 契约原句（所有点共用，逐字回查event1）

```yaml
    - name: int_jira__project_health_scoring
      description: Multi-dimensional Jira project health scoring with binary risk flags and composite scores
      grain: One row per project_id
      source_models:
      - staging.stg_jira__project
      - staging.stg_jira__issue
      - staging.stg_jira__issue_field_history
      - staging.stg_jira__comment
      - staging.stg_jira__issue_link
      - staging.stg_jira__sprint
      business_logic: 'Build base metrics per project by left-joining issues to projects and aggregating: - total_issues counts all issues; resolved_issues counts issues with a resolution timestamp; open_issues counts issues without one. - avg_resolution_days averages days from creation to resolution over resolved issues; NULL if none. - high_priority_issues counts issues with any priority_id present (proxy for “has priority,” not true severity). - unique_assignees counts distinct non-null assignee IDs. Derive velocity trends per project: - issues_resolved_30d counts issues resolved in the last 30 days; issues_created_30d counts issues created in the last 30 days. - issues_resolved_7d counts issues resolved in the last 7 days. - issues_resolved_prev_30d counts issues resolved 60–30 days before today. Compute quality indicators: - bug_issues counts issues with a non-null issue_type_id; feature_issues uses the same proxy and equals bug_issues. - reopened_issues_count counts all history records whose field value contains “reopen” (case-insensitive). - avg_comments_per_issue averages per-issue comment counts over issues that have at least one comment; NULL if none. Compute team dynamics: - workload_distribution_stddev and max_user_issues are derived from per-assignee issue counts on assigned issues; NULL if no assigned issues. - total_issue_links equals 1 if any project issue participates in any issue link, else 0. - sprints_participated equals the number of distinct sprints in the sprint source and is the same for all projects. Assemble risk flags (0/1): - backlog_risk = 1 if open_issues > 2 × resolved_issues else 0. - velocity_risk = 1 if avg_resolution_days > 30 else 0; NULL avg does not trigger the flag. - quality_risk = 1 if bug_issues > 30% of total_issues else 0. - resource_risk = 1 if unique_assignees < 2 else 0. - throughput_risk = 1 if issues_created_30d > 1.5 × issues_resolved_30d else 0. Compute health scores (each bounded to 0–25): - delivery_health_score starts at 25 and deducts 8 for backlog_risk, 10 for velocity_risk, 7 for throughput_risk. - quality_health_score starts at 25 and deducts 12 for quality_risk, 8 if reopened_issues_count > 10% of total_issues, 5 if avg_comments_per_issue < 1. - team_health_score starts at 25 and deducts 15 for resource_risk, 5 if workload_distribution_stddev > 10, 5 if unique_assignees = 0. - process_health_score starts at 25 and deducts 10 if sprints_participated = 0, 5 if total_issue_links = 0, 10 if high_priority_issues > 50% of total_issues. - velocity_change_percent is the percent change in resolved count vs the prior 30 days; if the prior is 0 then 0; otherwise rounded to one decimal place. Final outputs: - overall_health_score = sum of the four health scores (0–100). - health_grade: A+ (≥90), A (≥80), B (≥70), C (≥60), D (≥50), else F. - primary_risk_factor: dimension with the lowest health score; ties resolve in order Delivery → Quality → Team → Process. - trajectory_status from velocity_change_percent: >20 Accelerating; >5 Improving; >-5 Stable; >-20 Declining; else Critical Decline. - Final result is ordered by overall_health_score descending.'
      columns:
      - name: project_id
        data_type: VARCHAR
        description: Project identifier; grouping key with exactly one row per project_id
        tests:
        - not_null
        - unique
      - name: project_key
        data_type: VARCHAR
        description: Project key copied from the project source
        tests:
        - not_null
      - name: total_issues
        data_type: BIGINT
        description: Total number of issues linked to the project
      - name: open_issues
        data_type: BIGINT
        description: Number of issues without a resolution timestamp
      - name: resolved_issues
        data_type: BIGINT
        description: Number of issues with a resolution timestamp
      - name: avg_resolution_days
        data_type: DOUBLE
        description: Average days from creation to resolution over resolved issues; NULL if none
      - name: high_priority_issues
        data_type: BIGINT
        description: Number of issues with a present priority_id (proxy for 'has priority')
      - name: unique_assignees
        data_type: BIGINT
        description: Distinct count of non-null assignee IDs across project issues
      - name: issues_resolved_30d
        data_type: BIGINT
        description: Number of issues resolved in the last 30 days based on resolution date
      - name: issues_created_30d
        data_type: BIGINT
        description: Number of issues created in the last 30 days based on creation date
      - name: issues_resolved_7d
        data_type: BIGINT
        description: Number of issues resolved in the last 7 days
      - name: issues_resolved_prev_30d
        data_type: BIGINT
        description: Number of issues resolved 60–30 days before today
      - name: bug_issues
        data_type: BIGINT
        description: Number of issues with a non-null issue_type_id (used as bug proxy)
      - name: feature_issues
        data_type: BIGINT
        description: Number of issues with a non-null issue_type_id (same as bug_issues)
      - name: reopened_issues_count
        data_type: BIGINT
        description: Count of history records whose field value contains 'reopen' (case-insensitive) across project issues
      - name: avg_comments_per_issue
        data_type: DOUBLE
        description: Average comments per issue over issues with at least one comment; NULL if none
      - name: workload_distribution_stddev
        data_type: DOUBLE
        description: Standard deviation of issues per assignee within the project; NULL if none
      - name: max_user_issues
        data_type: BIGINT
        description: Maximum issues assigned to any single user; NULL if none
      - name: total_issue_links
        data_type: BIGINT
        description: 'Indicator: 1 if any project issue participates in any issue link, else 0'
      - name: sprints_participated
        data_type: BIGINT
        description: Number of distinct sprints in the sprint source (same for all projects)
      - name: backlog_risk
        data_type: INTEGER
        description: 'Flag (0/1): 1 when open_issues > 2 × resolved_issues, else 0'
      - name: velocity_risk
        data_type: INTEGER
        description: 'Flag (0/1): 1 when avg_resolution_days > 30, else 0; NULL avg does not trigger'
      - name: quality_risk
        data_type: INTEGER
        description: 'Flag (0/1): 1 when bug_issues > 30% of total_issues, else 0'
      - name: resource_risk
        data_type: INTEGER
        description: 'Flag (0/1): 1 when unique_assignees < 2, else 0'
      - name: throughput_risk
        data_type: INTEGER
        description: 'Flag (0/1): 1 when issues_created_30d > 1.5 × issues_resolved_30d, else 0'
      - name: delivery_health_score
        data_type: INTEGER
        description: 0–25 after deducting 8 for backlog_risk, 10 for velocity_risk, 7 for throughput_risk; bounded to 0–25
      - name: quality_health_score
        data_type: INTEGER
        description: 0–25 after deducting 12 for quality_risk, 8 if reopened_issues_count > 10% of total_issues, 5 if avg_comments_per_issue < 1; bounded to 0–25
      - name: team_health_score
        data_type: INTEGER
        description: 0–25 after deducting 15 for resource_risk, 5 if workload_distribution_stddev > 10, 5 if unique_assignees = 0; bounded to 0–25
      - name: process_health_score
        data_type: INTEGER
        description: 0–25 after deducting 10 if sprints_participated = 0, 5 if total_issue_links = 0, 10 if high_priority_issues > 50% of total_issues; bounded to 0–25
      - name: velocity_change_percent
        data_type: DOUBLE
        description: Percent change in resolved count vs prior 30 days; if prior is 0 then 0; otherwise rounded to 1 decimal
        tests:
        - not_null
      - name: overall_health_score
        data_type: INTEGER
        description: Sum of the four health scores, range 0–100
      - name: health_grade
        data_type: VARCHAR
        description: 'Letter grade from overall_health_score: A+ (≥90), A (≥80), B (≥70), C (≥60), D (≥50), else F'
      - name: primary_risk_factor
        data_type: VARCHAR
        description: Dimension with the lowest health score; ties resolve in order Delivery, Quality, Team, Process
      - name: trajectory_status
        data_type: VARCHAR
        description: 'Label from velocity_change_percent: >20 Accelerating; >5 Improving; >-5 Stable; >-20 Declining; else Critical Decline'
```

### 逐点结论

#### overall_health_score

主要；**已说出的降级**；把握高。

overall_health_score固定常量，未把契约分项统计汇总为项目健康分。已有CS项目/issue输入。finish明确点名project health scoring并披露简化评分。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 193 | 0 | 193 | 0 |
| L1 | 193 | 0 | 193 | 0 |
| L2 | 193 | 0 | 193 | 0 |
| L3 | 193 | 0 | 193 | 0 |

重跑：`records/021_extra_reruns_impl-011_int_jira__project_health_scoring.json` / `overall_health_score`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__project_health_scoring.sql` / `SQL.text`（sql）：

```text
100::integer overall_health_score
```


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml`，行[800, 920]；材料包 `records/021_packages/021_impl-011_int_jira__project_health_scoring.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/intermediate/int_jira__project_health_scoring.sql`；SHA-256 `2e155d28ebfd1af614936864783c43191c046a0042b0521b99f79e833cd6dcd5`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / event 55。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共2条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 24，失败=True。
  - `records/021_supplement_queries.json` / index 17，失败=False。

## 不确定或没查到的（含规则问题）

- 未发现需要增改手册的规则问题。没有将未知信息补成数据事实；证据范围以所列契约、交付代码、轨迹及重跑为限。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
