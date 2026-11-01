# impl-011_jira__project_risk_assessment（039，v3.2正式表）

## 任务

按冻结手册第3～8节复核本表；中间层及以后使用gold上游的CS口径。021旧标签仅留档，不是新类别依据。

## 结论

主要原因：**其他**；把握：高；只能组合修复：否。
021旧主要原因（含025更正）原样保留：`O`。

## 详细发现

### 范围、基线与排序

按整表L0（含评测键）先比行数减少量，行相同再比格子减少量。L1～L3仅作诊断。每项从同一基线独立修复；减少量重叠，不相加。只有所有单项在行和格均不减少才考虑组合修复。
共同基线：`{"L0": {"row_scale": 193, "cell_scale": 2525}, "L1": {"row_scale": 193, "cell_scale": 2525}, "L2": {"row_scale": 193, "cell_scale": 2525}, "L3": {"row_scale": 193, "cell_scale": 2525}}`。

| 点/组 | 类别 | 角色 | 减少行 | 减少格 | 五档 |
|---|---|---|---:|---:|---:|
| type_id_instead_name | 其他 | 主要 | 0 | 578 | 4 |
| unique_issue_types | 已说出的降级 | 参与 | 0 | 193 | 1 |
| unique_components | 已说出的降级 | 参与 | 0 | 186 | 1 |
| total_external_links | 已说出的降级 | 参与 | 0 | 193 | 1 |
| sprint_adoption_rate | 已说出的降级 | 参与 | 0 | 193 | 1 |
| complexity_risk_score | 已说出的降级 | 参与 | 0 | 189 | 1 |
| scope_risk_score | 已说出的降级 | 参与 | 0 | 193 | 1 |
| recommended_intervention | 已说出的降级 | 参与 | 0 | 193 | 1 |
| strategic_priority_recommendation | 已说出的降级 | 参与 | 0 | 61 | 1 |

### 契约原句（所有点共用，逐字回查event1）

```yaml
    - name: jira__project_risk_assessment
      description: Project risk assessment with computed risk scores, probabilities, and recommendations derived from Jira issues, project metrics, and sprint/activity signals
      grain: One row per project_id
      source_models:
      - intermediate.int_jira__project_metrics
      - staging.stg_jira__project
      - staging.stg_jira__issue
      - staging.stg_jira__issue_link
      - staging.stg_jira__component
      - raw.issue_sprint_history
      - staging.stg_jira__sprint
      business_logic: 'Build deterministic risk metrics and recommendations per project_id from Jira data: - project_health_base: - Join intermediate.int_jira__project_metrics (pm) to staging.stg_jira__project (p) on project_id. - Select project_id, project_key, project_name. - Compute total_issues = pm.count_open_issues + pm.count_closed_issues (used for downstream thresholds). - Set overall_health_score = 75.0 (fixed), primary_risk_factor = ''Normal'', trajectory_status = ''Stable''. - project_financial_impact (left join on project_id): - Estimate project value points per issue by type: epic = 8.0; story = 3.0; task = 2.0; bug = 1.5; other or null = 2.0; sum across joined rows as estimated_project_value_points. - total_hours_invested = sum of time_spent_seconds converted to hours with nulls treated as zero. - delivered_value_points = sum of the same value weights but only for issues with a resolution timestamp. - high_delay_cost_issues = count of unresolved issues older than 90 days based on the difference between now and created_at. - project_trend_analysis (left join on project_id): - 30-day windows relative to current_date: - issues_created_30d = count of issues created in the last 30 days. - issues_resolved_30d = count of issues resolved in the last 30 days. - issues_created_prev_30d and issues_resolved_prev_30d = counts for the window 60 to 30 days ago. - Team activity: - active_assignees_30d = distinct assignees on issues created in the last 30 days. - active_assignees_90d = distinct assignees on issues created in the last 90 days. - High-priority trend (not surfaced in final columns but computed): counts constrained to high/critical priorities within the same windows. - project_complexity_analysis (left join on project_id): - unique_issue_types = distinct issue_type_id count (nulls excluded). - total_external_links = distinct count of issue links touching project issues, summing distinct source and distinct related issue IDs. - unique_components = distinct component_name count. - sprint_adoption_rate = average of a 1/0 indicator where 1 means an issue appears in any sprint; range 0–1. - Additional complexity signals (not all surfaced): unique_priorities, unique_statuses, sprints_involved, epic_count, child_issue_count, unique_reporters, unique_creators. - risk_factor_scoring: - value_delivery_percentage = delivered_value_points divided by estimated_project_value_points, multiplied by 100 and rounded to 1 decimal; if estimated_project_value_points is zero, set to 0.0. - net_issue_growth_30d = issues_created_30d minus issues_resolved_30d (may be negative). - resolution_velocity_change_percent = percent change in issues resolved in the last 30 days vs the prior 30 days, rounded to 1 decimal; if there were no resolutions in the prior window, set to 0.0. - team_stability_percentage = active_assignees_30d divided by active_assignees_90d, multiplied by 100 and rounded to 1 decimal; if there were no active assignees in the last 90 days, set to 100.0. - Risk scores (each 0–20, exact buckets): - health_risk_score: - overall_health_score <= 40 → 20; <= 60 → 15; <= 75 → 10; <= 85 → 5; else → 0. - schedule_risk_score (relative to total_issues): - high_delay_cost_issues > total_issues × 30% → 20; > 20% → 15; > 10% → 10; > 0 → 5; else → 0. - resource_risk_score (by active_assignees_30d): - < 2 → 20; < 3 → 15; < 5 → 10; else → 0. - complexity_risk_score (using unique_components and total_external_links): - unique_components > 10 and total_external_links > 20 → 20; unique_components > 8 or total_external_links > 15 → 15; unique_components > 5 or total_external_links > 10 → 10; unique_components > 3 or total_external_links > 5 → 5; else → 0. - scope_risk_score (by net_issue_growth_30d relative to total_issues): - net growth > total_issues × 20% → 20; > 10% → 15; > 0 → 10; > −10% → 5; else → 0. - predictive_modeling: - total_risk_score = sum of the five risk scores (0–100). - success_probability (ordered rules; first match applies): - overall_health_score ≥ 85 and total_risk_score ≤ 20 → 0.95; - overall_health_score ≥ 75 and total_risk_score ≤ 40 → 0.80; - overall_health_score ≥ 60 and total_risk_score ≤ 60 → 0.65; - overall_health_score ≥ 50 and total_risk_score ≤ 80 → 0.40; - else → 0.20. - timeline_prediction (ordered rules; first match applies): - trajectory_status = ''Accelerating'' and total_risk_score ≤ 30 → ''Within Target Timeline''; - trajectory_status = ''Improving'' and total_risk_score ≤ 50 → ''Minor Delay Expected''; - trajectory_status = ''Stable'' and total_risk_score ≤ 70 → ''Moderate Delay Risk''; - trajectory_status in {''Declining'',''Critical Decline''} or total_risk_score > 70 → ''Significant Delay Risk''; - else → ''Timeline Uncertain''. - budget_impact_prediction (ordered rules; first match applies): - total_hours_invested > 0 and value_delivery_percentage < 50 → ''High Budget Overrun Risk''; - schedule_risk_score ≥ 15 → ''Moderate Budget Impact''; - total_risk_score ≤ 30 → ''Within Budget Expectations''; - else → ''Budget Risk Moderate''. - final_risk_assessment: - risk_category thresholds (first match applies): total_risk_score ≥ 80 → ''Critical Risk''; ≥ 60 → ''High Risk''; ≥ 40 → ''Medium Risk''; ≥ 20 → ''Low Risk''; else → ''Minimal Risk''. - primary_risk_driver = label of the maximum among the five risk scores with tie-break order: Project Health, then Schedule Delays, then Resource Constraints, then Technical Complexity, else Scope Management. - recommended_intervention thresholds: ≥ 80 → ''Immediate Executive Review Required''; ≥ 60 → ''Project Manager Intervention Needed''; ≥ 40 → ''Team Lead Review and Action Plan''; ≥ 20 → ''Regular Monitoring and Minor Adjustments''; else → ''Continue Current Approach''. - strategic_priority_recommendation: - success_probability ≥ 0.8 and estimated_project_value_points > 50 → ''High Priority - High Success''; - success_probability ≥ 0.6 and estimated_project_value_points > 30 → ''Medium Priority - Good Prospects''; - success_probability < 0.4 and total_risk_score > 60 → ''Low Priority - Consider Restructuring''; - success_probability < 0.3 → ''Consider Project Termination''; - else → ''Standard Priority''. - Output one row per project_id. When viewed directly from the SQL, rows are ordered by total_risk_score descending, then success_probability ascending; ordering does not affect computed values.'
      columns:
      - name: project_id
        data_type: VARCHAR
        description: Project identifier; grouping key for the output; exactly one row per project_id
        tests:
        - not_null
        - unique
      - name: project_key
        data_type: VARCHAR
        description: Human-readable project key from Jira (joined from stg_jira__project)
        tests:
        - not_null
      - name: project_name
        data_type: VARCHAR
        description: Project name from Jira (joined from stg_jira__project)
        tests:
        - not_null
      - name: overall_health_score
        data_type: DECIMAL(3,1)
        description: Project health score used for risk bucketing; currently fixed to 75.0; scale 0–100
        tests:
        - overall_health_score BETWEEN 0 AND 100
      - name: primary_risk_factor
        data_type: VARCHAR
        description: Text label from project_health_base indicating the primary risk factor (currently 'Normal')
      - name: trajectory_status
        data_type: VARCHAR
        description: Text label of project trajectory (e.g., Accelerating/Improving/Stable/Declining); drives timeline prediction
      - name: estimated_project_value_points
        data_type: DECIMAL(38,1)
        description: 'Sum of issue value points by type (epic=8, story=3, task=2, bug=1.5, other or null=2); unit: points'
        tests:
        - estimated_project_value_points >= 0
      - name: delivered_value_points
        data_type: DECIMAL(38,1)
        description: 'Sum of value points for issues that are resolved using the same weights; unit: points'
        tests:
        - delivered_value_points >= 0
      - name: total_hours_invested
        data_type: DOUBLE
        description: 'Sum of time_spent_seconds converted to hours; nulls treated as 0; unit: hours'
        tests:
        - total_hours_invested >= 0
      - name: high_delay_cost_issues
        data_type: HUGEINT
        description: Count of unresolved issues older than 90 days based on created_at; non-negative
        tests:
        - high_delay_cost_issues >= 0
      - name: value_delivery_percentage
        data_type: DOUBLE
        description: Delivered value as a percentage of estimated value, rounded to 1 decimal; 0 when estimated is 0; range 0–100
        tests:
        - value_delivery_percentage BETWEEN 0 AND 100
      - name: net_issue_growth_30d
        data_type: BIGINT
        description: Issues created in the last 30 days minus issues resolved in the last 30 days; may be negative
      - name: resolution_velocity_change_percent
        data_type: DOUBLE
        description: Percent change in issues resolved vs the prior 30-day window, rounded to 1 decimal; 0 when no prior resolutions; may be negative
      - name: team_stability_percentage
        data_type: DOUBLE
        description: Active assignees in last 30 days divided by those in last 90 days, times 100 and rounded to 1 decimal; 100 when 90-day denominator is 0
        tests:
        - team_stability_percentage BETWEEN 0 AND 100
      - name: unique_issue_types
        data_type: BIGINT
        description: Distinct count of issue_type_id per project; nulls excluded
        tests:
        - unique_issue_types >= 0
      - name: unique_components
        data_type: BIGINT
        description: Distinct count of component_name per project; nulls excluded
        tests:
        - unique_components >= 0
      - name: total_external_links
        data_type: BIGINT
        description: Distinct issue links touching project issues, summed from distinct source and related issue IDs
        tests:
        - total_external_links >= 0
      - name: sprint_adoption_rate
        data_type: DOUBLE
        description: Average of a 1/0 indicator for issues appearing in any sprint across joined sprint history; range 0–1
        tests:
        - sprint_adoption_rate BETWEEN 0 AND 1
      - name: health_risk_score
        data_type: INTEGER
        description: 'Risk bucket 0–20 based on overall_health_score: <=40→20, <=60→15, <=75→10, <=85→5, else→0'
        tests:
        - health_risk_score BETWEEN 0 AND 20
      - name: schedule_risk_score
        data_type: INTEGER
        description: 'Risk bucket 0–20 using high_delay_cost_issues relative to total_issues: >30%→20, >20%→15, >10%→10, >0→5, else→0'
        tests:
        - schedule_risk_score BETWEEN 0 AND 20
      - name: resource_risk_score
        data_type: INTEGER
        description: 'Risk bucket 0–20 by active_assignees_30d: <2→20, <3→15, <5→10, else→0'
        tests:
        - resource_risk_score BETWEEN 0 AND 20
      - name: complexity_risk_score
        data_type: INTEGER
        description: 'Risk bucket 0–20 using unique_components and total_external_links: (>10 and >20)→20; (>8 or >15)→15; (>5 or >10)→10; (>3 or >5)→5; else→0'
        tests:
        - complexity_risk_score BETWEEN 0 AND 20
      - name: scope_risk_score
        data_type: INTEGER
        description: 'Risk bucket 0–20 by net_issue_growth_30d vs total_issues: >20%→20; >10%→15; >0→10; >-10%→5; else→0'
        tests:
        - scope_risk_score BETWEEN 0 AND 20
      - name: total_risk_score
        data_type: INTEGER
        description: Sum of the five risk scores (health + schedule + resource + complexity + scope); range 0–100
        tests:
        - total_risk_score BETWEEN 0 AND 100
      - name: success_probability
        data_type: DECIMAL(3,2)
        description: Fixed probabilities (0.95/0.80/0.65/0.40/0.20) from ordered rules using overall_health_score and total_risk_score; range 0–1
        tests:
        - success_probability BETWEEN 0 AND 1
      - name: timeline_prediction
        data_type: VARCHAR
        description: Time-to-completion label from ordered rules combining trajectory_status and total_risk_score
      - name: budget_impact_prediction
        data_type: VARCHAR
        description: Budget impact label from ordered rules using hours invested, delivery percentage, schedule risk, and total risk
      - name: risk_category
        data_type: VARCHAR
        description: 'Overall risk label from total_risk_score thresholds: Critical/High/Medium/Low/Minimal'
        tests:
        - risk_category IN ('Low Risk', 'Medium Risk', 'High Risk', 'Critical Risk', 'Minimal Risk')
      - name: primary_risk_driver
        data_type: VARCHAR
        description: 'Dominant risk dimension chosen by the highest of the five risk scores with tie-break order: Health > Schedule > Resource > Complexity > Scope'
      - name: recommended_intervention
        data_type: VARCHAR
        description: 'Action guidance from total_risk_score thresholds: Executive Review/PM Intervention/Team Lead Action/Monitoring/Continue'
      - name: strategic_priority_recommendation
        data_type: VARCHAR
        description: Priority advice based on success_probability and estimated value, with overrides for low success and high total risk
```

### 逐点结论

#### type_id_instead_name

主要；**其他**；把握高。

agent以issue type名称判断epic/bug符合契约；gold用类型ID与这些单词比，实际ID无一为这些词。021诊断8000条成功匹配类型、4180非默认名称、ID匹配0，证明差异来自gold实现。

是否说出：第4档——看到了相关信息，但没有意识到的迹象。完整finish及交付SQL已核读（本批交付SQL无注释）。未找到针对本点或同类处理的相关交付说明；完整契约在event1实际可见。未发现比较备选/点出冲突的本点迹象，代码仅体现采用的做法，故第4档。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 193 | 193 | 2525 | 1947 |
| L1 | 193 | 193 | 2525 | 1947 |
| L2 | 193 | 193 | 2525 | 1947 |
| L3 | 193 | 193 | 2525 | 1947 |

重跑：`records/021_detailed_reruns_impl-011_jira__project_risk_assessment.json` / `type_id_instead_name`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__project_risk_assessment.sql` / `SQL.text`（sql）：

```text
sum(case lower(t.issue_type_name) when 'epic' then 8.0 when 'story' then 3.0 when 'bug' then 1.5 else 2.0 end) estimated
```

否定披露的审计范围：finish event 55 的完整 `args.final_thought`，见 `records/039_checks/delivery_sources.json`；不是以SQL无注释替代最终报告审查。

#### unique_issue_types

参与；**已说出的降级**；把握高。

unique_issue_types以固定计数/分数/分类替代契约计算；所需issue、components、links及sprint输入在CS可用。finish明确点名project risk assessment详细计算简化，故第1档。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 193 | 193 | 2525 | 2332 |
| L1 | 193 | 193 | 2525 | 2332 |
| L2 | 193 | 193 | 2525 | 2332 |
| L3 | 193 | 193 | 2525 | 2332 |

重跑：`records/021_extra_reruns_impl-011_jira__project_risk_assessment.json` / `unique_issue_types`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__project_risk_assessment.sql` / `SQL.text`（sql）：

```text
0::bigint unique_issue_types
```

#### unique_components

参与；**已说出的降级**；把握高。

unique_components以固定计数/分数/分类替代契约计算；所需issue、components、links及sprint输入在CS可用。finish明确点名project risk assessment详细计算简化，故第1档。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 193 | 193 | 2525 | 2339 |
| L1 | 193 | 193 | 2525 | 2339 |
| L2 | 193 | 193 | 2525 | 2339 |
| L3 | 193 | 193 | 2525 | 2339 |

重跑：`records/021_extra_reruns_impl-011_jira__project_risk_assessment.json` / `unique_components`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__project_risk_assessment.sql` / `SQL.text`（sql）：

```text
0::bigint unique_components
```

#### total_external_links

参与；**已说出的降级**；把握高。

total_external_links以固定计数/分数/分类替代契约计算；所需issue、components、links及sprint输入在CS可用。finish明确点名project risk assessment详细计算简化，故第1档。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 193 | 193 | 2525 | 2332 |
| L1 | 193 | 193 | 2525 | 2332 |
| L2 | 193 | 193 | 2525 | 2332 |
| L3 | 193 | 193 | 2525 | 2332 |

重跑：`records/021_extra_reruns_impl-011_jira__project_risk_assessment.json` / `total_external_links`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__project_risk_assessment.sql` / `SQL.text`（sql）：

```text
0::bigint total_external_links
```

#### sprint_adoption_rate

参与；**已说出的降级**；把握高。

sprint_adoption_rate以固定计数/分数/分类替代契约计算；所需issue、components、links及sprint输入在CS可用。finish明确点名project risk assessment详细计算简化，故第1档。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 193 | 193 | 2525 | 2332 |
| L1 | 193 | 193 | 2525 | 2332 |
| L2 | 193 | 193 | 2525 | 2332 |
| L3 | 193 | 193 | 2525 | 2332 |

重跑：`records/021_extra_reruns_impl-011_jira__project_risk_assessment.json` / `sprint_adoption_rate`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__project_risk_assessment.sql` / `SQL.text`（sql）：

```text
0.0::double sprint_adoption_rate
```

#### complexity_risk_score

参与；**已说出的降级**；把握高。

complexity_risk_score以固定计数/分数/分类替代契约计算；所需issue、components、links及sprint输入在CS可用。finish明确点名project risk assessment详细计算简化，故第1档。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 193 | 193 | 2525 | 2336 |
| L1 | 193 | 193 | 2525 | 2336 |
| L2 | 193 | 193 | 2525 | 2336 |
| L3 | 193 | 193 | 2525 | 2336 |

重跑：`records/021_extra_reruns_impl-011_jira__project_risk_assessment.json` / `complexity_risk_score`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__project_risk_assessment.sql` / `SQL.text`（sql）：

```text
0::integer complexity_risk_score
```

#### scope_risk_score

参与；**已说出的降级**；把握高。

scope_risk_score以固定计数/分数/分类替代契约计算；所需issue、components、links及sprint输入在CS可用。finish明确点名project risk assessment详细计算简化，故第1档。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 193 | 193 | 2525 | 2332 |
| L1 | 193 | 193 | 2525 | 2332 |
| L2 | 193 | 193 | 2525 | 2332 |
| L3 | 193 | 193 | 2525 | 2332 |

重跑：`records/021_extra_reruns_impl-011_jira__project_risk_assessment.json` / `scope_risk_score`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__project_risk_assessment.sql` / `SQL.text`（sql）：

```text
0::integer scope_risk_score
```

#### recommended_intervention

参与；**已说出的降级**；把握高。

recommended_intervention以固定计数/分数/分类替代契约计算；所需issue、components、links及sprint输入在CS可用。finish明确点名project risk assessment详细计算简化，故第1档。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 193 | 193 | 2525 | 2332 |
| L1 | 193 | 193 | 2525 | 2332 |
| L2 | 193 | 193 | 2525 | 2332 |
| L3 | 193 | 193 | 2525 | 2332 |

重跑：`records/021_extra_reruns_impl-011_jira__project_risk_assessment.json` / `recommended_intervention`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__project_risk_assessment.sql` / `SQL.text`（sql）：

```text
'Regular Monitoring and Minor Adjustments' recommended_intervention
```

#### strategic_priority_recommendation

参与；**已说出的降级**；把握高。

strategic_priority_recommendation以固定计数/分数/分类替代契约计算；所需issue、components、links及sprint输入在CS可用。finish明确点名project risk assessment详细计算简化，故第1档。

是否说出：第1档——交付物里针对本处说明了。报告点名本表/一一对应功能，且说明本处类型的占位、简化或来源选择；不推广到其他表。
证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。初始契约事件1完整未截断，以上契约原句为判断依据。

| 口径 | 基线行 | 单改行 | 基线格 | 单改格 |
|---|---:|---:|---:|---:|
| L0 | 193 | 193 | 2525 | 2464 |
| L1 | 193 | 193 | 2525 | 2464 |
| L2 | 193 | 193 | 2525 | 2464 |
| L3 | 193 | 193 | 2525 | 2464 |

重跑：`records/021_extra_reruns_impl-011_jira__project_risk_assessment.json` / `strategic_priority_recommendation`。准确old/new、共同clock_control及CS/agent-raw源见该JSON；039单输出恢复另保留完整baseline_sql/recovery_sql/单改SQL及hash，不复制gold目标输出。

原句 `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / `55.args.final_thought`（delivery）：

```text
尤其 project health scoring、sprint performance analytics 的部分趋势/评分，以及 stakeholder/team dashboard 和 project risk assessment 的详细业务计算使用了简化或默认值。这些模型结果在这些字段上可能为 NULL、默认值或简化分类，不应视为完整的业务分析指标。
```

原句 `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__project_risk_assessment.sql` / `SQL.text`（sql）：

```text
'Standard Priority' strategic_priority_recommendation
```


## 证据来源

- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-011/docs/data_contract.yaml`，行[2718, 2868]；材料包 `records/021_packages/021_impl-011_jira__project_risk_assessment.md`。
- 交付SQL：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-011/agent/dacomp-de-impl-011/sql/marts/jira__project_risk_assessment.sql`；SHA-256 `8c35c82677fdafd686cddcf429cb022be23ca2100ded9f071acd9f872fd92500`。
- 初始完整提示：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/1.json`；finish：`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-011/agent/.events/sessions/566d076e-c2fb-41-b4d07af20aac87c/events/55.json` / event 55。
- 轨迹/披露审计：`records/039_checks/process_review.json`、`disclosure_audit.json`、`quote_checks.json`。
- 复用核实查询含失败共3条，新核实0条（总数≤5）。诊断/单改不计作核实查询：

  - `records/021_queries.json` / index 27，失败=True。
  - `records/021_supplement_queries.json` / index 20，失败=False。
  - `records/021_final_diagnostics.json` / index 0，失败=False。

## 不确定或没查到的（含规则问题）

- 未发现需要增改手册的规则问题。没有将未知信息补成数据事实；证据范围以所列契约、交付代码、轨迹及重跑为限。

## 建议的下一步

纳入本批汇总；后续批次沿用冻结v3.2。本任务不处理其他批次。
