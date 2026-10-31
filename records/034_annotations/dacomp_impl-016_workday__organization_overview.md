# DAComp / impl-016_workday__organization_overview（v3）

## 错在哪里
两个比率漏补0、两个枚举标签与gold约定冲突各117格并列；角色关系和任期连接另有贡献。

证据复用入口：[018_impl-016_workday__organization_overview.md](../018_annotations/018_impl-016_workday__organization_overview.md)。下述分类重新按v3判断；旧结论不充当分类依据。

## annual_zero
- 角色：并列；类别：**Intent Misreading**；把握：中。
- 依据：规格分母0返回0，NULLIF未补0；单改减少117格。
- 是否说出：看到了但没提。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/016_trace_impl-016.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
相关契约原文见下方复用契约；本次已核对event 1对应段，不能用未展示部分推断看过。
event 1 / args.content：
```text
employees ÷ total_positions × 100 when total_positions > 0, else 0. - annual_turnover_rate (%) = departures_last_year ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - avg_current_tenure_years and avg_former_tenure_years = respective average tenure days ÷ 365, rounded to 2; if no data, treated as 0. - management_ratio (%) = (management_role_employees + director_role_employees) ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - high_risk_employee_percentage (%) = high_risk_employees ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - organization_health_score (0–100) = sum of: performance (cap at 30% of average performance), turnover (25/20/15/10/5 by thresholds using annual_turnover_rate and zero departures case), development (cap at 20% of average career development), efficiency (15/12/9/6 by position_fill_rate thresholds), an
```
## management_zero
- 角色：并列；类别：**Intent Misreading**；把握：中。
- 依据：规格分母0返回0；单改减少117格。
- 是否说出：看到了但没提。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/016_trace_impl-016.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
相关契约原文见下方复用契约；本次已核对event 1对应段，不能用未展示部分推断看过。
event 1 / args.content：
```text
 average tenure days ÷ 365, rounded to 2; if no data, treated as 0. - management_ratio (%) = (management_role_employees + director_role_employees) ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - high_risk_employee_percentage (%) = high_risk_employees ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - organization_health_score (0–100) = sum of: performance (cap at 30% of average performance), turnover (25/20/15/10/5 by thresholds using annual_turnover_rate and zero departures case), development (cap at 20% of average career development), efficiency (15/12/9/6 by position_fill_rate thresholds), and risk (10/7/4/2 by high_risk_employee_percentage thresholds); final score rounded to 2 decimals. - performance_category uses a weighted composite with thresholds: Excellent if composite ≥ 80; else Good if ≥ 60; else Average if ≥ 40; otherwise Needs Improvement
```
## maturity_labels
- 角色：并列；类别：**其他**；把握：中。
- 依据：规格明确New/Young/Mature/Legacy，agent遵守，gold长标签；减少117格。
- 是否说出：看到了但没提。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 1 / args.content：
```text
ganization_age_years is that divided by 365, rounded to 2 decimals. - organization_maturity_level by age_days: <1 year New; 1–3 years Young; 3–10 years Mature; 10+ years Legacy. - organizational_level from organization_type: Company/Division/Department/Team mapped to corresponding Level; others to Other Level. - access_level from visibility: Public→Open Access, Private→Restricted Access, others Unknown Access. 6) Final metrics and rules (rates rounded to 2 decimals; missing metrics default to 0 unless noted): - position_fill_rate (%) = current_active_employees ÷ total_positions × 100 when total_positions > 0, else 0. - annual_turnover_rate (%) = departures_last_year ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - avg_current_tenure_years and avg_former_tenure_years = respective average tenure days ÷ 365, rounded to 2; if no data, treated as 0. - management_ratio (%) = (manageme
```
## size_labels
- 角色：并列；类别：**其他**；把握：中。
- 依据：规格明确Empty/Micro等，agent遵守，gold长标签；减少117格。
- 是否说出：看到了但没提。
- 证据在场：不适用；曾经理解对过：不适用；系统提示是否适用：不适用。
event 1 / args.content：
```text
mprovement (weights and constants follow the detailed rules above). - organization_size_category by current_active_employees: 0 Empty; ≤5 Micro; ≤15 Small; ≤50 Medium; ≤200 Large; else Enterprise. - last_activity_date is the most recent assignment start; if none, use organization_created_date. - last_departure_date is the most recent assignment end; if none, use 1900-01-01. - management_recommendation (first match): if no active employees then review necessity; else if turnover > 30% then focus on retention; else if high-risk % > 25% then address risk; else if fill rate < 70% then improve staffing; else if average performance < 50 then enhance performance management; else if management_ratio > 40% then optimize structure; else maintain excellence. - data_quality_flag precedence: missing or blank organization name → ERROR; active employees exceed positions by more than 10 → WARNING; turnover rate > 100% → WA
```
## roles_relationship
- 角色：参与；类别：**Intent Misreading**；把握：中。
- 依据：规格明确worker/source/role/org连接，单改减少106格。
- 是否说出：看到了但没提。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/016_trace_impl-016.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
相关契约原文见下方复用契约；本次已核对event 1对应段，不能用未展示部分推断看过。
event 1 / args.content：
```text
employees ÷ total_positions × 100 when total_positions > 0, else 0. - annual_turnover_rate (%) = departures_last_year ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - avg_current_tenure_years and avg_former_tenure_years = respective average tenure days ÷ 365, rounded to 2; if no data, treated as 0. - management_ratio (%) = (management_role_employees + director_role_employees) ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - high_risk_employee_percentage (%) = high_risk_employees ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - organization_health_score (0–100) = sum of: performance (cap at 30% of average performance), turnover (25/20/15/10/5 by thresholds using annual_turnover_rate and zero departures case), development (cap at 20% of average career development), efficiency (15/12/9/6 by position_fill_rate thresholds), an
```
四档引句为关联证据；本处可见性另按在场栏判断，未将通用策略算成具体披露。
## tenure_join_weight
- 角色：参与；类别：**Intent Misreading**；把握：中。
- 依据：任期均值漏规格指定连接产生的权重，单改减少5格。
- 是否说出：看到了但没提。
- 证据在场：是；曾经理解对过：否；系统提示是否适用：不适用。
- 在场依据：records/016_trace_impl-016.json event 1；完整定位见 `records/034_checks/dacomp_trace_presence.json`。
相关契约原文见下方复用契约；本次已核对event 1对应段，不能用未展示部分推断看过。
event 1 / args.content：
```text
employees ÷ total_positions × 100 when total_positions > 0, else 0. - annual_turnover_rate (%) = departures_last_year ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - avg_current_tenure_years and avg_former_tenure_years = respective average tenure days ÷ 365, rounded to 2; if no data, treated as 0. - management_ratio (%) = (management_role_employees + director_role_employees) ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - high_risk_employee_percentage (%) = high_risk_employees ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - organization_health_score (0–100) = sum of: performance (cap at 30% of average performance), turnover (25/20/15/10/5 by thresholds using annual_turnover_rate and zero departures case), development (cap at 20% of average career development), efficiency (15/12/9/6 by position_fill_rate thresholds), an
```
四档引句为关联证据；本处可见性另按在场栏判断，未将通用策略算成具体披露。

## 规模、证据复用与新做
主要原因：多因并列。行优先；单改行无法区分时按格子。L0–L3、共同固定时间、各单处替换、SQL行号及查询结果复用 [018_impl-016_workday__organization_overview.md](../018_annotations/018_impl-016_workday__organization_overview.md) 第2、4节及其所链接的014/016/017/018重跑JSON。本次没有新执行DAComp SQL。
018试标对象的原重跑主要在014、016、017、018，不误引019–024其他表的重跑。
新增仅核对轨迹引句和event 1契约段。对实际未出现的匹配/唯一性结果，不把契约读取动作算作看过数据反证。

## 契约原句（本次从实际event 1定位）

```yaml
name: workday__organization_overview
      description: Executive-ready overview of each active organization with headcount, roles, tenure, mobility, risk, performance, diversity, compensation tiers, promotions, derived scores, recommendations, and data quality
      grain: One row per active organization_id and source_relation
      source_models:
      - staging.stg_workday__organization (filtered to is_inactive = false)
      - staging.stg_workday__worker_position_organization
      - staging.stg_workday__organization_role_worker
      - staging.stg_workday__organization_role
      - mart.workday__employee_overview (filtered to organization_id != 'Unknown')
      business_logic: '1) Filter organizations to active only and expose attributes and effective_start as the creation date. 2) Build worker–organization–role relationships by left joining worker positions to role-worker and role master on matching worker, role, source_relation, and organization_id. For each assignment: - assignment_status: ''Active Assignment'' if end date is null, else ''Former Assignment''. - assignment_duration_days: days between start and end; if end is null, days between start and current_date. - carry organization_role_id and organization_role_code from the role join. 3) Aggregate organization_employee_stats by (organization_id, source_relation): - total_employees_ever: distinct workers across all assignments. - current_active_employees: distinct workers with Active Assignment. - former_employees: distinct workers with Former Assignment. - total_positions_in_org: distinct positions across all assignments. - active_positions_count: distinct positions with Active Assignment. - new_assignments_last_year: distinct workers with start date in the last year relative to current_date. - departures_last_year: distinct workers with a non-null end date in the last year. - avg_current_tenure_days: average assignment_duration_days for Active Assignments. - avg_former_tenure_days: average assignment_duration_days for Former Assignments. - unique_organization_roles: distinct organization_role_id. - management_role_employees / director_role_employees / lead_role_employees: distinct workers where role code contains ''Manager'' / ''Director'' / ''Lead''. - last_new_assignment_date: most recent start date; last_departure_date: most recent end date. 4) Aggregate organization_performance_metrics from mart.workday__employee_overview by (organization_id, source_relation), excluding organization_id = ''Unknown'': - Averages over currently employed workers only: overall_employee_score and career_development_score rounded to 2 decimals; retention_stability_score rounded to 2 decimals; age rounded to 1 decimal. - Employee value segments: distinct workers by segment (''High Value - High Retention'', ''High Value - Flight Risk'', ''Stable - Development Needed'', ''Development Required''); no employment filter. - Risk distribution: distinct workers by employee_risk_level (High/Medium/Low); no employment filter. - Maturity segments: distinct employed workers where maturity contains ''New Hire'' / ''Junior'' / ''Experienced'' / ''Senior'' / ''Veteran''. - Diversity: distinct ethnicity_codes among employed; military_veterans_count is distinct employed workers flagged for military service. - Compensation tiers: distinct employed workers by compensation_tier (Entry/Mid/Senior/Executive Level). - Promotions among employed: total_promotions summed; high_achievers_count is distinct workers with total_promotions ≥ 2; fast_track_employees_count is distinct workers with fast_promotions > 0. 5) Derive organization attributes per active organization: - organization_created_date from effective_start. - organization_age_days as days from creation to current_date; organization_age_years is that divided by 365, rounded to 2 decimals. - organization_maturity_level by age_days: <1 year New; 1–3 years Young; 3–10 years Mature; 10+ years Legacy. - organizational_level from organization_type: Company/Division/Department/Team mapped to corresponding Level; others to Other Level. - access_level from visibility: Public→Open Access, Private→Restricted Access, others Unknown Access. 6) Final metrics and rules (rates rounded to 2 decimals; missing metrics default to 0 unless noted): - position_fill_rate (%) = current_active_employees ÷ total_positions × 100 when total_positions > 0, else 0. - annual_turnover_rate (%) = departures_last_year ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - avg_current_tenure_years and avg_former_tenure_years = respective average tenure days ÷ 365, rounded to 2; if no data, treated as 0. - management_ratio (%) = (management_role_employees + director_role_employees) ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - high_risk_employee_percentage (%) = high_risk_employees ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - organization_health_score (0–100) = sum of: performance (cap at 30% of average performance), turnover (25/20/15/10/5 by thresholds using annual_turnover_rate and zero departures case), development (cap at 20% of average career development), efficiency (15/12/9/6 by position_fill_rate thresholds), and risk (10/7/4/2 by high_risk_employee_percentage thresholds); final score rounded to 2 decimals. - performance_category uses a weighted composite with thresholds: Excellent if composite ≥ 80; else Good if ≥ 60; else Average if ≥ 40; otherwise Needs Improvement (weights and constants follow the detailed rules above). - organization_size_category by current_active_employees: 0 Empty; ≤5 Micro; ≤15 Small; ≤50 Medium; ≤200 Large; else Enterprise. - last_activity_date is the most recent assignment start; if none, use organization_created_date. - last_departure_date is the most recent assignment end; if none, use 1900-01-01. - management_recommendation (first match): if no active employees then review necessity; else if turnover > 30% then focus on retention; else if high-risk % > 25% then address risk; else if fill rate < 70% then improve staffing; else if average performance < 50 then enhance performance management; else if management_ratio > 40% then optimize structure; else maintain excellence. - data_quality_flag precedence: missing or blank organization name → ERROR; active employees exceed positions by more than 10 → WARNING; turnover rate > 100% → WARNING; negative age days → ERROR; otherwise VALID. - analysis_timestamp is the query execution timestamp. 7) Join logic: left join employee stats and performance metrics to active organizations on (organization_id, source_relation); missing measures default to 0. The final ordering is for presentation only and does not affect grain.'
      columns:
      - name: organization_id
        data_type: VARCHAR
        description: Organization identifier; join key to stats and metrics; one output row per active (organization_id, source_relation)
        tests:
        - not_null
      - name: source_relation
        data_type: VARCHAR
        description: Source system code carried from staging and used in all joins
        tests:
        - not_null
      - name: organization_name
        data_type: VARCHAR
        description: Organization display name from the active organization record
      - name: organization_code
        data_type: VARCHAR
        description: Organization code from the active organization record
      - name: organization_type
        data_type: VARCHAR
        description: Organization type (e.g., Company, Division, Department, Team)
      - name: organization_sub_type
        data_type: VARCHAR
        description: Subtype of the organization if provided in source
      - name: staffing_model
        data_type: VARCHAR
        description: Staffing model from source organization attributes
      - name: visibility
        data_type: VARCHAR
        description: Visibility setting from source; drives access_level mapping
      - name: access_level
        data_type: VARCHAR
        description: 'Derived access control: Public→Open Access, Private→Restricted Access, else Unknown Access'
      - name: organization_created_date
        data_type: DATE
        description: Effective start date of the active organization record
      - name: organization_age_days
        data_type: BIGINT
        description: Days since organization_created_date to current_date at run time
      - name: organization_age_years
        data_type: DOUBLE
        description: Rounded years since creation = round(organization_age_days/365.0, 2)
      - name: organization_maturity_level
        data_type: VARCHAR
        description: 'Age bucket: <1y New; 1–3y Young; 3–10y Mature; 10+y Legacy based on organization_age_days'
      - name: organizational_level
        data_type: VARCHAR
        description: 'Level mapped from organization_type: Company/Division/Department/Team→Corporate/Division/Department/Team Level; else Other Level'
      - name: total_employees_ever
        data_type: BIGINT
        description: Distinct workers ever assigned to the org; defaults to 0 when missing
      - name: current_active_employees
        data_type: BIGINT
        description: Distinct workers with Active Assignment at run time; defaults to 0 when missing
      - name: former_employees
        data_type: BIGINT
        description: Distinct workers with Former Assignment; defaults to 0 when missing
      - name: total_positions
        data_type: BIGINT
        description: Distinct positions ever assigned within the org; defaults to 0 when missing
      - name: active_positions_count
        data_type: BIGINT
        description: Distinct positions with Active Assignment; defaults to 0 when missing
      - name: position_fill_rate
        data_type: DOUBLE
        description: Filled positions % = round(current_active_employees*100.0/total_positions, 2); 0 if total_positions=0
      - name: new_assignments_last_year
        data_type: BIGINT
        description: Distinct workers with assignment start in the last year; defaults to 0 when missing
      - name: departures_last_year
        data_type: BIGINT
        description: Distinct workers with non-null assignment end in the last year; defaults to 0 when missing
      - name: annual_turnover_rate
        data_type: DOUBLE
        description: Departures % = round(departures_last_year*100.0/current_active_employees, 2); 0 if denominator=0
      - name: avg_current_tenure_years
        data_type: DOUBLE
        description: Average tenure (years) for Active Assignments = round(avg_current_tenure_days/365.0, 2) with NULL→0
      - name: avg_former_tenure_years
        data_type: DOUBLE
        description: Average tenure (years) for Former Assignments = round(avg_former_tenure_days/365.0, 2) with NULL→0
      - name: unique_organization_roles
        data_type: BIGINT
        description: Distinct organization_role_id linked to the org; defaults to 0 when missing
      - name: management_role_employees
        data_type: BIGINT
        description: Distinct workers with role code containing 'Manager'; defaults to 0 when missing
      - name: director_role_employees
        data_type: BIGINT
        description: Distinct workers with role code containing 'Director'; defaults to 0 when missing
      - name: lead_role_employees
        data_type: BIGINT
        description: Distinct workers with role code containing 'Lead'; defaults to 0 when missing
      - name: management_ratio
        data_type: DOUBLE
        description: Management share % = round((management_role_employees+director_role_employees)*100.0/current_active_employees, 2); 0 if denominator=0
      - name: avg_employee_performance_score
        data_type: DOUBLE
        description: Avg overall_employee_score among employed, rounded to 2; defaults to 0 when missing; 0–100 scale preserved
      - name: avg_career_development_score
        data_type: DOUBLE
        description: Avg career_development_score among employed, rounded to 2; defaults to 0 when missing; 0–100 scale preserved
      - name: avg_retention_stability_score
        data_type: DOUBLE
        description: Avg retention_stability_score among employed, rounded to 2; defaults to 0 when missing; 0–100 scale preserved
      - name: high_value_stable_employees
        data_type: BIGINT
        description: Distinct workers in 'High Value - High Retention'; defaults to 0 when missing
      - name: high_value_flight_risk_employees
        data_type: BIGINT
        description: Distinct workers in 'High Value - Flight Risk'; defaults to 0 when missing
      - name: stable_development_employees
        data_type: BIGINT
        description: Distinct workers in 'Stable - Development Needed'; defaults to 0 when missing
      - name: development_required_employees
        data_type: BIGINT
        description: Distinct workers in 'Development Required'; defaults to 0 when missing
      - name: high_risk_employees
        data_type: BIGINT
        description: Distinct workers with employee_risk_level = 'High Risk'; defaults to 0 when missing
      - name: medium_risk_employees
        data_type: BIGINT
        description: Distinct workers with employee_risk_level = 'Medium Risk'; defaults to 0 when missing
      - name: low_risk_employees
        data_type: BIGINT
        description: Distinct workers with employee_risk_level = 'Low Risk'; defaults to 0 when missing
      - name: high_risk_employee_percentage
        data_type: DOUBLE
        description: High-risk share % = round(high_risk_employees*100.0/current_active_employees, 2); 0 if denominator=0
      - name: new_hire_employees
        data_type: BIGINT
        description: Distinct employed workers with maturity containing 'New Hire'; defaults to 0 when missing
      - name: junior_employees
        data_type: BIGINT
        description: Distinct employed workers with maturity containing 'Junior'; defaults to 0 when missing
      - name: experienced_employees
        data_type: BIGINT
        description: Distinct employed workers with maturity containing 'Experienced'; defaults to 0 when missing
      - name: senior_employees
        data_type: BIGINT
        description: Distinct employed workers with maturity containing 'Senior'; defaults to 0 when missing
      - name: veteran_employees
        data_type: BIGINT
        description: Distinct employed workers with maturity containing 'Veteran'; defaults to 0 when missing
      - name: ethnic_diversity_count
        data_type: BIGINT
        description: Count of distinct ethnicity_codes among employed; defaults to 0 when missing
      - name: military_veterans_count
        data_type: BIGINT
        description: Distinct employed workers with military service flag; defaults to 0 when missing
      - name: avg_employee_age
        data_type: DOUBLE
        description: Average age among employed, rounded to 1 in source aggregation; defaults to 0 when missing
      - name: entry_level_employees
        data_type: BIGINT
        description: Distinct employed workers in compensation_tier = 'Entry Level'; defaults to 0 when missing
      - name: mid_level_employees
        data_type: BIGINT
        description: Distinct employed workers in compensation_tier = 'Mid Level'; defaults to 0 when missing
      - name: senior_level_employees
        data_type: BIGINT
        description: Distinct employed workers in compensation_tier = 'Senior Level'; defaults to 0 when missing
      - name: executive_level_employees
        data_type: BIGINT
        description: Distinct employed workers in compensation_tier = 'Executive Level'; defaults to 0 when missing
      - name: total_promotions_in_organization
        data_type: HUGEINT
        description: Sum of total_promotions for employed workers in the org; defaults to 0 when missing
      - name: high_achievers_count
        data_type: BIGINT
        description: Distinct employed workers with total_promotions >= 2; defaults to 0 when missing
      - name: fast_track_employees_count
        data_type: BIGINT
        description: Distinct employed workers with fast_promotions > 0; defaults to 0 when missing
      - name: organization_health_score
        data_type: DOUBLE
        description: Composite 0–100 score from performance, turnover, development, fill-rate efficiency, and risk components; rounded to 2
      - name: performance_category
        data_type: VARCHAR
        description: 'Category from the weighted composite: Excellent (>=80), Good (>=60), Average (>=40), else Needs Improvement'
      - name: organization_size_category
        data_type: VARCHAR
        description: 'Size bucket by current_active_employees: Empty, Micro (<=5), Small (<=15), Medium (<=50), Large (<=200), Enterprise (>200)'
      - name: last_activity_date
        data_type: DATE
        description: Most recent assignment start date; if none, falls back to organization_created_date
      - name: last_departure_date
        data_type: DATE
        description: Most recent assignment end date; if none, defaults to 1900-01-01
      - name: management_recommendation
        data_type: VARCHAR
        description: Recommendation based on thresholds of size, turnover, high-risk %, fill rate, performance, and management ratio; first matching rule applies
      - name: data_quality_flag
        data_type: VARCHAR
        description: VALID or specific ERROR/WARNING based on missing name, employee>position anomaly, turnover >100%, or negative age days
      - name: analysis_timestamp
        data_type: TIMESTAMP WITH TIME ZONE
        description: current_timestamp at run time indicating when the analysis was computed
```

## 规则问题
本表的边界及两种读法见总报告；主因规模保留018同口径。额外单改不改善的控制不自动当作错误点；不同修法对应同一前提时只列一次。
## 复用证据精确位置

- [契约原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-016_workday__organization_overview.md:28)
- [SQL行号与原文](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-016_workday__organization_overview.md:240)
- [单项改善概览](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-016_workday__organization_overview.md:778)
- [重跑 baseline](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-016_workday__organization_overview.md:868)
- [重跑 annual_zero](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-016_workday__organization_overview.md:947)
- [重跑 management_zero](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-016_workday__organization_overview.md:1033)
- [重跑 risk_zero](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-016_workday__organization_overview.md:1119)
- [重跑 fill_zero](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-016_workday__organization_overview.md:1205)
- [重跑 maturity_labels](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-016_workday__organization_overview.md:1291)
- [重跑 size_labels](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-016_workday__organization_overview.md:1377)
- [重跑 roles_relationship](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-016_workday__organization_overview.md:1463)
- [重跑 tenure_join_weight](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-016_workday__organization_overview.md:1551)
- [重跑 health_turnover_rule](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-016_workday__organization_overview.md:1645)
- [重跑 health_risk_rule](/home/katherine/Assumption_Ledger/records/018_annotations/018_impl-016_workday__organization_overview.md:1731)
