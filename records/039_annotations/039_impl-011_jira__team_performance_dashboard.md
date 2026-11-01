# impl-011_jira__team_performance_dashboard（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**Intent Misreading**；把握：高；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`C`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 6000, "cell_scale": 79365}, "L1": {"row_scale": 6000, "cell_scale": 79365}, "L2": {"row_scale": 6000, "cell_scale": 79365}, "L3": {"row_scale": 6000, "cell_scale": 79365}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| user_metrics_driver | Intent Misreading | 主要 | 1626 | 52032 | 4 |
| avg_daily_activity_score | Intent Misreading | 参与 | 0 | 3315 | 4 |
| avg_weekly_activity_score | Intent Misreading | 参与 | 0 | 3315 | 4 |
| projects_contributed_to | 已说出的降级 | 参与 | 0 | 4374 | 1 |
| issue_types_worked_on | 已说出的降级 | 参与 | 0 | 4374 | 1 |
| days_since_first_issue | 已说出的降级 | 参与 | 0 | 4374 | 1 |
| leadership_indicator | 已说出的降级 | 参与 | 0 | 3207 | 1 |
| overall_performance_score | 已说出的降级 | 参与 | 0 | 4374 | 1 |

### 契约原句（所有点共用，逐字回查event1）

```yaml
    - name: jira__team_performance_dashboard
      description: Team performance dashboard per user aggregated across all projects with activity, delivery, collaboration, growth, risk, and scoring metrics
      grain: One row per user_id (project_id='all_projects')
      source_models:
      - intermediate.int_jira__user_metrics
      - staging.stg_jira__user
      - staging.stg_jira__issue
      - staging.stg_jira__issue_link
      - staging.stg_jira__comment
      - staging.stg_jira__sprint
      - staging.stg_jira__issue_field_history
      - staging.stg_jira__field
      - raw.issue_sprint_history
      business_logic: '- Build user_activity_summary: - Join user metrics to users on user_id; emit one row per user with project_id=''all_projects'' and project_name=''All Projects''. - Set current_engagement_tier=''Standard User'', current_pattern_type=''Regular User'', current_lifecycle_stage=''Stable''. - Set avg_daily_activity_score and avg_weekly_activity_score from average close time days; avg_consistency_score=0.7; last_active_date=current_date; active_days_count=30; churn_risk_days=0; productive_days=count_closed_issues; highly_active_days=count_closed_issues if >10 else 0. - Build team_collaboration_metrics from issues created in the last 90 days and with a non-null assignee: - Group by project_id and assignee_user_id. - total_assigned_issues counts assigned issues. - resolved_issues counts assigned issues with a resolution date. - avg_resolution_days averages the days between creation and resolution over resolved issues. - high_priority_issues counts assigned issues with a non-null priority. - bug_issues counts assigned issues with a non-null issue type (label is generic, not limited to “Bug”). - epic_issues counts assigned issues with a non-null parent issue. - Join issue links and count distinct linked issue references on both sides; join comments and count distinct non-assignee comment authors. - estimate_accuracy_ratio averages the absolute relative difference between time spent and original estimate over issues where both values are present and >0. - Build sprint_participation_analysis from recent sprints (started within 180 days), issues, and derived story points: - Parse numeric story points from active field history where the field name contains “story” and “point”; default to 1 when no number is found. - Group by sprint_id, sprint_name, assignee user_id, and project_id. - Measure issues_in_sprint, issues_completed_in_sprint (resolved within sprint window), total_story_points, story_points_completed_in_sprint, and avg_completion_day_in_sprint (days from sprint start to resolution when resolved on/before sprint end). - Build user_growth_metrics by left joining user_activity_summary to issues and comments: - Consider issues where the user is assignee, reporter, or creator; and comments authored by the user. - first_issue_date is the earliest issue creation date; last_resolved_date is the latest resolution date. - days_since_first_issue is the days from current_date to first_issue_date. - issue_types_worked_on counts distinct issue types; priority_levels_handled counts distinct priorities; projects_contributed_to counts distinct projects. - issues_reported counts issues reported by the user; issues_commented_on counts distinct issues the user commented on. - Build team_performance_scoring by left joining user_activity_summary to team_collaboration_metrics, user_growth_metrics, and aggregated sprint metrics: - Aggregate sprint metrics per user and project: sprint_count (distinct sprints), avg_sprint_completion_rate (average of per-sprint completed/issues; sprints with zero issues are excluded), total_story_points_delivered (sum of completed story points). - Rounding and units: - avg_daily_activity_score and avg_weekly_activity_score are computed to two decimals but stored without fractional part due to column type. - consistency_percentage = avg_consistency_score × 100 rounded to one decimal. - resolution_rate_percentage = percentage of assigned issues resolved, rounded to one decimal; NULL if no assigned issues. - avg_resolution_days rounded to one decimal; NULL if no resolved issues. - estimate_accuracy_percentage = estimate_accuracy_ratio × 100 rounded to one decimal; NULL if no eligible issues. - Risk flags: at_churn_risk is true when churn_risk_days > 7; inactive_recently is true when current_date − last_active_date > 7 days; poor_estimation is true when estimate accuracy ratio > 2; all flags are always populated (no NULLs). - Note: Joins to collaboration and sprint metrics use (user_id, project_id); because project_id=''all_projects'', these often remain NULL. - Final scoring and tiering: - overall_performance_score clamps to 0–100 and sums components: - Delivery (40%): 40/30/20/10/0 points at resolution rate ≥90/≥75/≥60/≥40/else. - Activity (30%): 30/20/10/0 points for engagement tier Highly/Moderately/Lightly Active/else. - Quality (20%): 20/15/10/5 points for estimate accuracy in [80,120]/[70,130]/[60,140]/else. - Collaboration (10%): 10/7/5/0 points at unique collaborators ≥5/≥3/≥1/else. - performance_tier: Top Performer (score ≥85), Strong Performer (≥70), Average Performer (≥50), else Needs Improvement. - Final output is ordered by overall_performance_score descending, then project_name, then user_display_name.'
      columns:
      - name: user_id
        data_type: VARCHAR
        description: User identifier; grouping key; exactly one output row per user_id
        tests:
        - not_null
        - unique
      - name: user_display_name
        data_type: VARCHAR
        description: Display name from staging.stg_jira__user for the user_id
        tests:
        - not_null
      - name: email
        data_type: VARCHAR
        description: Email from staging.stg_jira__user; may be NULL if not present
      - name: project_id
        data_type: VARCHAR
        description: Constant 'all_projects' emitted for every user row
        tests:
        - not_null
      - name: project_name
        data_type: VARCHAR
        description: Constant 'All Projects' emitted for every user row
        tests:
        - not_null
      - name: current_engagement_tier
        data_type: VARCHAR
        description: Engagement tier label set to 'Standard User'; used in scoring only when equal to 'Highly Active', 'Moderately Active', or 'Lightly Active'
      - name: current_pattern_type
        data_type: VARCHAR
        description: Activity pattern label; constant 'Regular User'
      - name: current_lifecycle_stage
        data_type: VARCHAR
        description: Lifecycle stage label; constant 'Stable'
      - name: avg_daily_activity_score
        data_type: DECIMAL(18,0)
        description: Derived from average close time days; computed to two decimals then stored without fractional part
      - name: avg_weekly_activity_score
        data_type: DECIMAL(18,0)
        description: Derived from average close time days; computed to two decimals then stored without fractional part
      - name: consistency_percentage
        data_type: DECIMAL(12,1)
        description: Activity consistency expressed as a percentage rounded to one decimal; constant 70.0 in current logic
      - name: total_assigned_issues
        data_type: BIGINT
        description: Count of issues assigned to the user in the last 90 days; NULL when no (user_id, project_id) match to collaboration metrics due to project_id='all_projects'
      - name: resolved_issues
        data_type: BIGINT
        description: Count of assigned issues with a resolution date in the last 90 days; NULL when no (user_id, project_id) match to collaboration metrics
      - name: resolution_rate_percentage
        data_type: DOUBLE
        description: Percentage of assigned issues resolved in the last 90 days, rounded to one decimal; NULL if no assigned issues
      - name: avg_resolution_days
        data_type: DOUBLE
        description: Average days from issue creation to resolution for resolved issues in the last 90 days, rounded to one decimal; NULL if none
      - name: high_priority_issues
        data_type: BIGINT
        description: Count of assigned issues with a non-null priority in the last 90 days; NULL when no (user_id, project_id) match to collaboration metrics
      - name: performance_tier
        data_type: VARCHAR
        description: 'Tier based on overall_performance_score: Top Performer (≥85), Strong Performer (≥70), Average Performer (≥50), else Needs Improvement'
      - name: bug_issues
        data_type: BIGINT
        description: Count of assigned issues with a non-null issue type in the last 90 days (generic, not limited to 'Bug'); NULL when no match
      - name: epic_issues
        data_type: BIGINT
        description: Count of assigned issues with a non-null parent issue in the last 90 days; NULL when no match
      - name: estimate_accuracy_percentage
        data_type: DOUBLE
        description: Average relative deviation between time spent and original estimate over issues with both values >0, expressed as a percentage and rounded to one decimal; higher is worse; NULL if no eligible issues
      - name: linked_issues
        data_type: BIGINT
        description: Total distinct linked issue references (issue_id plus related_issue_id) for the user's assigned issues in the last 90 days; NULL when no match
      - name: unique_collaborators_on_issues
        data_type: BIGINT
        description: Distinct non-assignee comment authors on the user's assigned issues in the last 90 days; NULL when no match
      - name: projects_contributed_to
        data_type: BIGINT
        description: Distinct projects across issues where the user is assignee, reporter, or creator; 0 if none
      - name: issue_types_worked_on
        data_type: BIGINT
        description: Distinct issue types across issues where the user is assignee, reporter, or creator; 0 if none
      - name: sprint_count
        data_type: BIGINT
        description: Distinct sprint count aggregated per (user_id, project_id); NULL when no match because project_id='all_projects'
      - name: avg_sprint_completion_rate
        data_type: DOUBLE
        description: Average per-sprint completion ratio (completed issues divided by issues in sprint), excluding sprints with zero issues; NULL when no matching sprint data for the user and project
      - name: total_story_points_delivered
        data_type: DECIMAL(38,3)
        description: Sum of story points completed within sprints per (user_id, project_id); NULL when no match because project_id='all_projects'
      - name: days_since_first_issue
        data_type: DOUBLE
        description: Days between current_date and the user's first observed issue creation date; NULL if the user has no issues
      - name: leadership_indicator
        data_type: BIGINT
        description: Count of issues reported by the user; 0 if none
      - name: at_churn_risk
        data_type: BOOLEAN
        description: True when churn_risk_days > 7; False otherwise; always populated
        tests:
        - not_null
      - name: inactive_recently
        data_type: BOOLEAN
        description: True when current_date minus last_active_date exceeds 7 days; False otherwise; always populated
        tests:
        - not_null
      - name: poor_estimation
        data_type: BOOLEAN
        description: True when the estimate accuracy ratio exceeds 2; False otherwise or when unavailable; always populated
        tests:
        - not_null
      - name: overall_performance_score
        data_type: INTEGER
        description: Composite score (0–100) from delivery, activity, quality, and collaboration components; clamped to 0–100 using defined thresholds
        tests:
        - not_null
```

### 逐点结论

#### user_metrics_driver

主要；**Intent Misreading**；把握高。

P：以所有user为驱动并LEFT JOIN活动即可。契约明确从user metrics驱动并连接用户，agent多出无活动用户；范围由条款决定。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 6000 | 4374 | 79365 | 27333 |
| L1 | 6000 | 4374 | 79365 | 27333 |
| L2 | 6000 | 4374 | 79365 | 27333 |
| L3 | 6000 | 4374 | 79365 | 27333 |

重跑：`records/021_detailed_reruns_impl-011_jira__team_performance_dashboard.json` / `user_metrics_driver`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__team_performance_dashboard.sql` / `SQL.text`（sql）：

```text
from staging.stg_jira__user u left join intermediate.int_jira__user_metrics m using(user_id)
```

否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### avg_daily_activity_score

参与；**Intent Misreading**；把握高。

avg_daily_activity_score对契约未COALESCE的nullable平均值额外补0；这是明文计算链的改动，不能被“团队dashboard简化”泛化为披露此NULL政策。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 6000 | 6000 | 79365 | 76050 |
| L1 | 6000 | 6000 | 79365 | 76050 |
| L2 | 6000 | 6000 | 79365 | 76050 |
| L3 | 6000 | 6000 | 79365 | 76050 |

重跑：`records/021_detailed_reruns_impl-011_jira__team_performance_dashboard.json` / `avg_daily_activity_score`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__team_performance_dashboard.sql` / `SQL.text`（sql）：

```text
coalesce(m.avg_close_time_days,0)::decimal(18,0) avg_daily_activity_score
```

否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### avg_weekly_activity_score

参与；**Intent Misreading**；把握高。

avg_weekly_activity_score对契约未COALESCE的nullable平均值额外补0；这是明文计算链的改动，不能被“团队dashboard简化”泛化为披露此NULL政策。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 6000 | 6000 | 79365 | 76050 |
| L1 | 6000 | 6000 | 79365 | 76050 |
| L2 | 6000 | 6000 | 79365 | 76050 |
| L3 | 6000 | 6000 | 79365 | 76050 |

重跑：`records/021_detailed_reruns_impl-011_jira__team_performance_dashboard.json` / `avg_weekly_activity_score`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__team_performance_dashboard.sql` / `SQL.text`（sql）：

```text
coalesce(m.avg_close_time_days,0)::decimal(18,0) avg_weekly_activity_score
```

否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### projects_contributed_to

参与；**已说出的降级**；把握高。

projects_contributed_to使用固定0/NULL/默认值，省略已有user/issue活动上的统计、时间或评分。finish明确点名team dashboard详细计算简化，适用第1档。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 6000 | 6000 | 79365 | 74991 |
| L1 | 6000 | 6000 | 79365 | 74991 |
| L2 | 6000 | 6000 | 79365 | 74991 |
| L3 | 6000 | 6000 | 79365 | 74991 |

重跑：`records/021_detailed_reruns_impl-011_jira__team_performance_dashboard.json` / `projects_contributed_to`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__team_performance_dashboard.sql` / `SQL.text`（sql）：

```text
0::bigint projects_contributed_to
```

#### issue_types_worked_on

参与；**已说出的降级**；把握高。

issue_types_worked_on使用固定0/NULL/默认值，省略已有user/issue活动上的统计、时间或评分。finish明确点名team dashboard详细计算简化，适用第1档。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 6000 | 6000 | 79365 | 74991 |
| L1 | 6000 | 6000 | 79365 | 74991 |
| L2 | 6000 | 6000 | 79365 | 74991 |
| L3 | 6000 | 6000 | 79365 | 74991 |

重跑：`records/021_detailed_reruns_impl-011_jira__team_performance_dashboard.json` / `issue_types_worked_on`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__team_performance_dashboard.sql` / `SQL.text`（sql）：

```text
0::bigint issue_types_worked_on
```

#### days_since_first_issue

参与；**已说出的降级**；把握高。

days_since_first_issue使用固定0/NULL/默认值，省略已有user/issue活动上的统计、时间或评分。finish明确点名team dashboard详细计算简化，适用第1档。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 6000 | 6000 | 79365 | 74991 |
| L1 | 6000 | 6000 | 79365 | 74991 |
| L2 | 6000 | 6000 | 79365 | 74991 |
| L3 | 6000 | 6000 | 79365 | 74991 |

重跑：`records/021_detailed_reruns_impl-011_jira__team_performance_dashboard.json` / `days_since_first_issue`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__team_performance_dashboard.sql` / `SQL.text`（sql）：

```text
null::double days_since_first_issue
```

#### leadership_indicator

参与；**已说出的降级**；把握高。

leadership_indicator使用固定0/NULL/默认值，省略已有user/issue活动上的统计、时间或评分。finish明确点名team dashboard详细计算简化，适用第1档。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 6000 | 6000 | 79365 | 76158 |
| L1 | 6000 | 6000 | 79365 | 76158 |
| L2 | 6000 | 6000 | 79365 | 76158 |
| L3 | 6000 | 6000 | 79365 | 76158 |

重跑：`records/021_detailed_reruns_impl-011_jira__team_performance_dashboard.json` / `leadership_indicator`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__team_performance_dashboard.sql` / `SQL.text`（sql）：

```text
0::bigint leadership_indicator
```

#### overall_performance_score

参与；**已说出的降级**；把握高。

overall_performance_score使用固定0/NULL/默认值，省略已有user/issue活动上的统计、时间或评分。finish明确点名team dashboard详细计算简化，适用第1档。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 6000 | 6000 | 79365 | 74991 |
| L1 | 6000 | 6000 | 79365 | 74991 |
| L2 | 6000 | 6000 | 79365 | 74991 |
| L3 | 6000 | 6000 | 79365 | 74991 |

重跑：`records/021_detailed_reruns_impl-011_jira__team_performance_dashboard.json` / `overall_performance_score`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__team_performance_dashboard.sql` / `SQL.text`（sql）：

```text
0::integer overall_performance_score
```


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml`，行[2475, 2605]；材料包 `records/021_packages/021_impl-011_jira__team_performance_dashboard.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__team_performance_dashboard.sql`；SHA-256 `98bb8b5cf3879fa0fe51948a50322ab06c8d8053c501669a93969bc0c2d5d9b4`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / event 55。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共2条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 30，失败=True。
  - `records/021_supplement_queries.json` / index 23，失败=False。

## 不确定或没查到的（含规则问题）

- 未发现需要增改手册的规则问题。没有将未知信息补成数据事实；证据范围以所列契约、交付代码、轨迹及重跑为限。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
