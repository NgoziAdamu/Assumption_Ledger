# impl-016 / workday__organization_overview（v2定稿）

## 1. 差异描述与判定

两个比率漏补0、两个枚举标签与gold约定冲突各117格并列；角色关系和任期连接另有贡献。

已核实：CS用gold上游，所有重跑固定gold实际analysis_timestamp。基线117行/696格；annual_zero、management_zero、maturity_labels、size_labels各单独减少117格，行数均不变。契约明确分母0时比率0，agent NULLIF后未补0，两个C；契约明确New/Young/Mature/Legacy及Empty/Micro等短标签，agent遵守而gold输出扩展长标签，两个O。roles_relationship按契约worker/source/role/org关系重建，减少106格；tenure_join_weight补相同关系的行重复权重，减少5格，均C参与因素。health两项阈值控制及risk/fill补0在当前整体比较未减少规模，不列参与因素。raw.email在015中gold/初始7284行、agent2448行，但event65→66末次成功运行仍打印raw和staging各7284行；余下事件只有只读查询和报告写入，未找到2448的改动步骤与原因。按用户规则照常评估；这次CS也隔离了agent上游raw差异。

主要原因：**多因并列（C、O）**；把握：**中**。
参与因素：C：角色关系聚合（106格）；C：任期平均的连接权重（5格）。标记：无。

与上一版（016）相比：原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。

## 2. 依据与复用范围

- [手册v2](../../docs/标注手册_v2.md)第3–7节；[上一版逐表记录](../016_annotations/016_impl-016_workday__organization_overview.md)。
- [018执行前指纹](../018_input_before.json)、[018结束后指纹](../018_input_after.json)。
- [四档逐项审计](../018_uncertainty_audit.json)、[复用清单](../018_reuse_manifest.json)。

以下契约、SQL及raw审计摘自016，其中“本轮/本次”指原记录所属任务，旧指纹日期不冒充018新快照。旧归因结论以本文第1、5、6节为准。

- 起点：[013精简材料包](../013_packages/013_impl-016_marts_workday__organization_overview.md)；013官方状态不改。
- 契约：`/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml` 第2024–2230行。
- [原始轨迹转录](../016_trace_impl-016.json)：每个event保留原文及其原始路径，可回查`traces/dacomp_deimpl_prev.tar.gz`。
- [本轮重跑结果](../016_reruns_impl-016.json)；[015三方raw核对](../015_raw_impl-016.json)。
- [本轮原件指纹与历史对照](../016_input_before.json)、[结束后核对](../016_input_after.json)。

### 契约原文

```yaml
    - name: workday__organization_overview
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

### SQL行号与原文

agent：`/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql`
```sql
   1: WITH active_org AS (SELECT * FROM staging.stg_workday__organization WHERE is_inactive=FALSE), rel AS (
   2:  SELECT worker_id,organization_id,source_relation,position_id,effective_start,effective_end,
   3:  date_diff('day',effective_start,coalesce(effective_end,current_date)) duration,
   4:  CASE WHEN effective_end IS NULL THEN 'Active Assignment' ELSE 'Former Assignment' END status
   5:  FROM staging.stg_workday__worker_position_organization
   6: ), stats AS (
   7:  SELECT organization_id,source_relation,count(DISTINCT worker_id) total_employees_ever,count(DISTINCT worker_id) FILTER(WHERE effective_end IS NULL) current_active_employees,count(DISTINCT worker_id) FILTER(WHERE effective_end IS NOT NULL) former_employees,count(DISTINCT position_id) total_positions,count(DISTINCT position_id) FILTER(WHERE effective_end IS NULL) active_positions_count,
   8:  count(DISTINCT worker_id) FILTER(WHERE effective_start>=current_date-INTERVAL '1 year') new_assignments_last_year,count(DISTINCT worker_id) FILTER(WHERE effective_end>=current_date-INTERVAL '1 year') departures_last_year,avg(duration) FILTER(WHERE effective_end IS NULL) avg_current_days,avg(duration) FILTER(WHERE effective_end IS NOT NULL) avg_former_days,max(effective_start) last_activity_date,max(effective_end) last_departure_date
   9:  FROM rel GROUP BY organization_id,source_relation
  10: ), roles AS (
  11:  SELECT ow.organization_id,'workday' source_relation,count(DISTINCT r.organization_role_id) unique_organization_roles,count(DISTINCT ow.organization_worker_code) FILTER(WHERE r.organization_role_code ILIKE '%Manager%') management_role_employees,count(DISTINCT ow.organization_worker_code) FILTER(WHERE r.organization_role_code ILIKE '%Director%') director_role_employees,count(DISTINCT ow.organization_worker_code) FILTER(WHERE r.organization_role_code ILIKE '%Lead%') lead_role_employees FROM staging.stg_workday__organization_role_worker ow LEFT JOIN staging.stg_workday__organization_role r ON ow.organization_id=r.organization_id AND ow.role_id=r.organization_role_id GROUP BY ow.organization_id
  12: ), perf AS (
  13:  SELECT organization_id,source_relation,avg(overall_employee_score) FILTER(WHERE is_employed) avg_employee_performance_score,avg(career_development_score) FILTER(WHERE is_employed) avg_career_development_score,avg(retention_stability_score) FILTER(WHERE is_employed) avg_retention_stability_score,
  14:  count(DISTINCT worker_id) FILTER(WHERE employee_value_segment='High Value - High Retention') high_value_stable_employees,count(DISTINCT worker_id) FILTER(WHERE employee_value_segment='High Value - Flight Risk') high_value_flight_risk_employees,count(DISTINCT worker_id) FILTER(WHERE employee_value_segment='Stable - Development Needed') stable_development_employees,count(DISTINCT worker_id) FILTER(WHERE employee_value_segment='Development Required') development_required_employees,
  15:  count(DISTINCT worker_id) FILTER(WHERE employee_risk_level='High Risk') high_risk_employees,count(DISTINCT worker_id) FILTER(WHERE employee_risk_level='Medium Risk') medium_risk_employees,count(DISTINCT worker_id) FILTER(WHERE employee_risk_level='Low Risk') low_risk_employees,
  16:  count(DISTINCT worker_id) FILTER(WHERE is_employed AND employee_maturity_segment LIKE '%New Hire%') new_hire_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND employee_maturity_segment LIKE '%Junior%') junior_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND employee_maturity_segment LIKE '%Experienced%') experienced_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND employee_maturity_segment LIKE '%Senior%') senior_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND employee_maturity_segment LIKE '%Veteran%') veteran_employees,
  17:  count(DISTINCT ethnicity_codes) FILTER(WHERE is_employed AND ethnicity_codes IS NOT NULL) ethnic_diversity_count,count(DISTINCT worker_id) FILTER(WHERE is_employed AND is_military_service) military_veterans_count,avg(age) FILTER(WHERE is_employed) avg_employee_age,
  18:  count(DISTINCT worker_id) FILTER(WHERE is_employed AND compensation_tier='Entry Level') entry_level_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND compensation_tier='Mid Level') mid_level_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND compensation_tier='Senior Level') senior_level_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND compensation_tier='Executive Level') executive_level_employees,
  19:  sum(total_promotions) FILTER(WHERE is_employed) total_promotions_in_organization,count(DISTINCT worker_id) FILTER(WHERE is_employed AND total_promotions>=2) high_achievers_count,count(DISTINCT worker_id) FILTER(WHERE is_employed AND fast_promotions>0) fast_track_employees_count
  20:  FROM mart.workday__employee_overview WHERE organization_id<>'Unknown' GROUP BY organization_id,source_relation
  21: ), joined AS (SELECT o.*,s.*,r.unique_organization_roles,r.management_role_employees,r.director_role_employees,r.lead_role_employees,p.* EXCLUDE(organization_id,source_relation) FROM active_org o LEFT JOIN stats s USING(organization_id,source_relation) LEFT JOIN roles r USING(organization_id,source_relation) LEFT JOIN perf p USING(organization_id,source_relation))
  22: SELECT organization_id,source_relation,organization_name,organization_code,organization_type,organization_sub_type,staffing_model,visibility,
  23: CASE visibility WHEN 'Public' THEN 'Open Access' WHEN 'Private' THEN 'Restricted Access' ELSE 'Unknown Access' END access_level,effective_start organization_created_date,date_diff('day',effective_start,current_date)::BIGINT organization_age_days,round(date_diff('day',effective_start,current_date)/365.0,2)::DOUBLE organization_age_years,
  24: CASE WHEN date_diff('day',effective_start,current_date)<365 THEN 'New' WHEN date_diff('day',effective_start,current_date)<1095 THEN 'Young' WHEN date_diff('day',effective_start,current_date)<3650 THEN 'Mature' ELSE 'Legacy' END organization_maturity_level,
  25: CASE organization_type WHEN 'Company' THEN 'Corporate Level' WHEN 'Division' THEN 'Division Level' WHEN 'Department' THEN 'Department Level' WHEN 'Team' THEN 'Team Level' ELSE 'Other Level' END organizational_level,
  26: coalesce(total_employees_ever,0)::BIGINT total_employees_ever,coalesce(current_active_employees,0)::BIGINT current_active_employees,coalesce(former_employees,0)::BIGINT former_employees,coalesce(total_positions,0)::BIGINT total_positions,coalesce(active_positions_count,0)::BIGINT active_positions_count,
  27: round(coalesce(current_active_employees,0)*100.0/NULLIF(total_positions,0),2)::DOUBLE position_fill_rate,coalesce(new_assignments_last_year,0)::BIGINT new_assignments_last_year,coalesce(departures_last_year,0)::BIGINT departures_last_year,round(coalesce(departures_last_year,0)*100.0/NULLIF(current_active_employees,0),2)::DOUBLE annual_turnover_rate,
  28: round(coalesce(avg_current_days,0)/365.0,2)::DOUBLE avg_current_tenure_years,round(coalesce(avg_former_days,0)/365.0,2)::DOUBLE avg_former_tenure_years,coalesce(unique_organization_roles,0)::BIGINT unique_organization_roles,coalesce(management_role_employees,0)::BIGINT management_role_employees,coalesce(director_role_employees,0)::BIGINT director_role_employees,coalesce(lead_role_employees,0)::BIGINT lead_role_employees,
  29: round((coalesce(management_role_employees,0)+coalesce(director_role_employees,0))*100.0/NULLIF(current_active_employees,0),2)::DOUBLE management_ratio,coalesce(avg_employee_performance_score,0)::DOUBLE avg_employee_performance_score,coalesce(avg_career_development_score,0)::DOUBLE avg_career_development_score,coalesce(avg_retention_stability_score,0)::DOUBLE avg_retention_stability_score,
  30: coalesce(high_value_stable_employees,0)::BIGINT high_value_stable_employees,coalesce(high_value_flight_risk_employees,0)::BIGINT high_value_flight_risk_employees,coalesce(stable_development_employees,0)::BIGINT stable_development_employees,coalesce(development_required_employees,0)::BIGINT development_required_employees,coalesce(high_risk_employees,0)::BIGINT high_risk_employees,coalesce(medium_risk_employees,0)::BIGINT medium_risk_employees,coalesce(low_risk_employees,0)::BIGINT low_risk_employees,
  31: round(coalesce(high_risk_employees,0)*100.0/NULLIF(current_active_employees,0),2)::DOUBLE high_risk_employee_percentage,coalesce(new_hire_employees,0)::BIGINT new_hire_employees,coalesce(junior_employees,0)::BIGINT junior_employees,coalesce(experienced_employees,0)::BIGINT experienced_employees,coalesce(senior_employees,0)::BIGINT senior_employees,coalesce(veteran_employees,0)::BIGINT veteran_employees,coalesce(ethnic_diversity_count,0)::BIGINT ethnic_diversity_count,coalesce(military_veterans_count,0)::BIGINT military_veterans_count,coalesce(avg_employee_age,0)::DOUBLE avg_employee_age,
  32: coalesce(entry_level_employees,0)::BIGINT entry_level_employees,coalesce(mid_level_employees,0)::BIGINT mid_level_employees,coalesce(senior_level_employees,0)::BIGINT senior_level_employees,coalesce(executive_level_employees,0)::BIGINT executive_level_employees,coalesce(total_promotions_in_organization,0)::HUGEINT total_promotions_in_organization,coalesce(high_achievers_count,0)::BIGINT high_achievers_count,coalesce(fast_track_employees_count,0)::BIGINT fast_track_employees_count,
  33: round(least(30,coalesce(avg_employee_performance_score,0)*.3)+CASE WHEN departures_last_year=0 THEN 25 WHEN annual_turnover_rate<=10 THEN 25 WHEN annual_turnover_rate<=20 THEN 20 WHEN annual_turnover_rate<=30 THEN 15 WHEN annual_turnover_rate<=40 THEN 10 ELSE 5 END+least(20,coalesce(avg_career_development_score,0)*.2)+CASE WHEN position_fill_rate>=90 THEN 15 WHEN position_fill_rate>=75 THEN 12 WHEN position_fill_rate>=60 THEN 9 ELSE 6 END+CASE WHEN high_risk_employee_percentage<=10 THEN 10 WHEN high_risk_employee_percentage<=20 THEN 7 WHEN high_risk_employee_percentage<=30 THEN 4 ELSE 2 END,2)::DOUBLE organization_health_score,
  34: CASE WHEN avg_employee_performance_score>=80 THEN 'Excellent' WHEN avg_employee_performance_score>=60 THEN 'Good' WHEN avg_employee_performance_score>=40 THEN 'Average' ELSE 'Needs Improvement' END performance_category,
  35: CASE WHEN current_active_employees=0 THEN 'Empty' WHEN current_active_employees<=5 THEN 'Micro' WHEN current_active_employees<=15 THEN 'Small' WHEN current_active_employees<=50 THEN 'Medium' WHEN current_active_employees<=200 THEN 'Large' ELSE 'Enterprise' END organization_size_category,
  36: coalesce(last_activity_date,effective_start) last_activity_date,coalesce(last_departure_date,DATE '1900-01-01') last_departure_date,
  37: CASE WHEN current_active_employees=0 THEN 'Review Organization Necessity' WHEN annual_turnover_rate>30 THEN 'Focus on Retention' WHEN high_risk_employee_percentage>25 THEN 'Address Employee Risk' WHEN position_fill_rate<70 THEN 'Improve Staffing' WHEN avg_employee_performance_score<50 THEN 'Enhance Performance Management' WHEN management_ratio>40 THEN 'Optimize Structure' ELSE 'Maintain Excellence' END management_recommendation,
  38: CASE WHEN organization_name IS NULL OR trim(organization_name)='' THEN 'ERROR: Missing organization name' WHEN current_active_employees>total_positions+10 THEN 'WARNING: Employees exceed positions' WHEN annual_turnover_rate>100 THEN 'WARNING: Turnover exceeds 100%' WHEN organization_age_days<0 THEN 'ERROR: Negative organization age' ELSE 'VALID' END data_quality_flag,current_timestamp::TIMESTAMPTZ analysis_timestamp
  39: FROM joined
```

gold（仅用于诊断）：`/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql`
```sql
   1: -- Organizational structure and relationship overview data mart - provides a comprehensive view of organizational hierarchy, role assignments, and employee distribution
   2: -- Support organizational structure analysis, management level optimization, and cross-department collaboration analysis
   3: 
   4: with organization_base as (
   5:     select * 
   6:     from staging.stg_workday__organization
   7:     where not is_inactive  -- Only include active organizations
   8: ),
   9: 
  10: -- Organizational roles and employee relations
  11: organization_employee_relationships as (
  12:     select 
  13:         wpo.organization_id,
  14:         wpo.source_relation,
  15:         wpo.worker_id,
  16:         wpo.position_id,
  17:         wpo.effective_start as assignment_start_date,
  18:         wpo.effective_end as assignment_end_date,
  19:         
  20:         -- current allocation status
  21:         case when wpo.effective_end is null then 'Active Assignment' else 'Former Assignment' end as assignment_status,
  22:         
  23:         -- Assign duration
  24:         case 
  25:             when wpo.effective_end is not null then 
  26:                 date_diff('day', wpo.effective_start, wpo.effective_end)
  27:             else 
  28:                 date_diff('day', wpo.effective_start, current_date)
  29:         end as assignment_duration_days,
  30:         
  31:         -- Organization role information  
  32:         orw.role_id as organization_role_id,
  33:         org_role.organization_role_code
  34:         
  35:     from staging.stg_workday__worker_position_organization wpo
  36:     left join staging.stg_workday__organization_role_worker orw
  37:         on wpo.worker_id = orw.organization_worker_code
  38:         and wpo.source_relation = orw.source_relation
  39:     left join staging.stg_workday__organization_role org_role
  40:         on orw.role_id = org_role.organization_role_id
  41:         and orw.source_relation = org_role.source_relation
  42:         and wpo.organization_id = org_role.organization_id
  43: ),
  44: 
  45: -- Organizational employee statistics and performance summary
  46: organization_employee_stats as (
  47:     select 
  48:         oer.organization_id,
  49:         oer.source_relation,
  50:         
  51:         -- Basic employee statistics
  52:         count(distinct oer.worker_id) as total_employees_ever,
  53:         count(distinct case when oer.assignment_status = 'Active Assignment' then oer.worker_id end) as current_active_employees,
  54:         count(distinct case when oer.assignment_status = 'Former Assignment' then oer.worker_id end) as former_employees,
  55:         count(distinct oer.position_id) as total_positions_in_org,
  56:         count(distinct case when oer.assignment_status = 'Active Assignment' then oer.position_id end) as active_positions_count,
  57:         
  58:         -- Employee turnover statistics
  59:         count(distinct case when oer.assignment_start_date >= current_date - interval '1 year' then oer.worker_id end) as new_assignments_last_year,
  60:         count(distinct case when oer.assignment_end_date >= current_date - interval '1 year' and oer.assignment_end_date is not null then oer.worker_id end) as departures_last_year,
  61:         
  62:         -- Average tenure
  63:         avg(case when oer.assignment_status = 'Active Assignment' then oer.assignment_duration_days end) as avg_current_tenure_days,
  64:         avg(case when oer.assignment_status = 'Former Assignment' then oer.assignment_duration_days end) as avg_former_tenure_days,
  65:         
  66:         -- Organizational role distribution
  67:         count(distinct oer.organization_role_id) as unique_organization_roles,
  68:         count(distinct case when oer.organization_role_code like '%Manager%' then oer.worker_id end) as management_role_employees,
  69:         count(distinct case when oer.organization_role_code like '%Director%' then oer.worker_id end) as director_role_employees,
  70:         count(distinct case when oer.organization_role_code like '%Lead%' then oer.worker_id end) as lead_role_employees,
  71:         
  72:         -- Latest event date
  73:         max(oer.assignment_start_date) as last_new_assignment_date,
  74:         max(oer.assignment_end_date) as last_departure_date
  75:         
  76:     from organization_employee_relationships oer
  77:     group by oer.organization_id, oer.source_relation
  78: ),
  79: 
  80: -- Organizational performance and employee quality indicators (based on employee overview data)
  81: organization_performance_metrics as (
  82:     select 
  83:         eo.organization_id,
  84:         eo.source_relation,
  85:         
  86:         -- employee performance indicators
  87:         round(avg(case when eo.is_employed then eo.overall_employee_score end), 2) as avg_employee_performance,
  88:         round(avg(case when eo.is_employed then eo.career_development_score end), 2) as avg_career_development,
  89:         round(avg(case when eo.is_employed then eo.retention_stability_score end), 2) as avg_retention_stability,
  90:         
  91:         -- Employee value distribution
  92:         count(distinct case when eo.employee_value_segment = 'High Value - High Retention' then eo.worker_id end) as high_value_stable_employees,
  93:         count(distinct case when eo.employee_value_segment = 'High Value - Flight Risk' then eo.worker_id end) as high_value_flight_risk_employees,
  94:         count(distinct case when eo.employee_value_segment = 'Stable - Development Needed' then eo.worker_id end) as stable_development_employees,
  95:         count(distinct case when eo.employee_value_segment = 'Development Required' then eo.worker_id end) as development_required_employees,
  96:         
  97:         -- risk distribution
  98:         count(distinct case when eo.employee_risk_level = 'High Risk' then eo.worker_id end) as high_risk_employees,
  99:         count(distinct case when eo.employee_risk_level = 'Medium Risk' then eo.worker_id end) as medium_risk_employees,
 100:         count(distinct case when eo.employee_risk_level = 'Low Risk' then eo.worker_id end) as low_risk_employees,
 101:         
 102:         -- Employee maturity distribution
 103:         count(distinct case when eo.employee_maturity_segment like '%New Hire%' and eo.is_employed then eo.worker_id end) as new_hire_employees,
 104:         count(distinct case when eo.employee_maturity_segment like '%Junior%' and eo.is_employed then eo.worker_id end) as junior_employees,
 105:         count(distinct case when eo.employee_maturity_segment like '%Experienced%' and eo.is_employed then eo.worker_id end) as experienced_employees,
 106:         count(distinct case when eo.employee_maturity_segment like '%Senior%' and eo.is_employed then eo.worker_id end) as senior_employees,
 107:         count(distinct case when eo.employee_maturity_segment like '%Veteran%' and eo.is_employed then eo.worker_id end) as veteran_employees,
 108:         
 109:         -- diversity index
 110:         count(distinct case when eo.is_employed then eo.ethnicity_codes end) as ethnic_diversity_count,
 111:         count(distinct case when eo.is_employed and eo.is_military_service then eo.worker_id end) as military_veterans_count,
 112:         round(avg(case when eo.is_employed then eo.age end), 1) as avg_employee_age,
 113:         
 114:         -- Salary distribution
 115:         count(distinct case when eo.compensation_tier = 'Entry Level' and eo.is_employed then eo.worker_id end) as entry_level_employees,
 116:         count(distinct case when eo.compensation_tier = 'Mid Level' and eo.is_employed then eo.worker_id end) as mid_level_employees,
 117:         count(distinct case when eo.compensation_tier = 'Senior Level' and eo.is_employed then eo.worker_id end) as senior_level_employees,
 118:         count(distinct case when eo.compensation_tier = 'Executive Level' and eo.is_employed then eo.worker_id end) as executive_level_employees,
 119:         
 120:         -- career development statistics
 121:         sum(case when eo.is_employed then eo.total_promotions end) as total_promotions_in_org,
 122:         count(distinct case when eo.total_promotions >= 2 and eo.is_employed then eo.worker_id end) as high_achievers_count,
 123:         count(distinct case when eo.fast_promotions > 0 and eo.is_employed then eo.worker_id end) as fast_track_employees_count
 124:         
 125:     from mart.workday__employee_overview eo
 126:     where eo.organization_id != 'Unknown'
 127:     group by eo.organization_id, eo.source_relation
 128: ),
 129: 
 130: -- Organizational Hierarchy and Relationship Analysis
 131: organization_hierarchy_analysis as (
 132:     select 
 133:         ob.organization_id,
 134:         ob.source_relation,
 135:         ob.organization_name,
 136:         ob.organization_code,
 137:         ob.organization_type,
 138:         ob.organization_sub_type,
 139:         ob.staffing_model,
 140:         ob.visibility,
 141:         ob.effective_start as organization_created_date,
 142:         
 143:         -- Calculate organization age
 144:         date_diff('day', ob.effective_start, current_date) as organization_age_days,
 145:         case 
 146:             when date_diff('day', ob.effective_start, current_date) < 365 then 'New Organization (<1 year)'
 147:             when date_diff('day', ob.effective_start, current_date) < 365*3 then 'Young Organization (1-3 years)'
 148:             when date_diff('day', ob.effective_start, current_date) < 365*10 then 'Mature Organization (3-10 years)'
 149:             else 'Legacy Organization (10+ years)'
 150:         end as organization_maturity_level,
 151:         
 152:         -- Organization type analysis
 153:         case 
 154:             when ob.organization_type = 'Company' then 'Corporate Level'
 155:             when ob.organization_type = 'Division' then 'Division Level'
 156:             when ob.organization_type = 'Department' then 'Department Level'
 157:             when ob.organization_type = 'Team' then 'Team Level'
 158:             else 'Other Level'
 159:         end as organizational_level,
 160:         
 161:         -- Visibility and access control
 162:         case 
 163:             when ob.visibility = 'Public' then 'Open Access'
 164:             when ob.visibility = 'Private' then 'Restricted Access'
 165:             else 'Unknown Access'
 166:         end as access_level
 167:         
 168:     from organization_base ob
 169: )
 170: 
 171: select 
 172:     oha.organization_id,
 173:     oha.source_relation,
 174:     oha.organization_name,
 175:     oha.organization_code,
 176:     oha.organization_type,
 177:     oha.organization_sub_type,
 178:     oha.staffing_model,
 179:     oha.visibility,
 180:     oha.access_level,
 181:     oha.organization_created_date,
 182:     oha.organization_age_days,
 183:     round(oha.organization_age_days / 365.0, 2) as organization_age_years,
 184:     oha.organization_maturity_level,
 185:     oha.organizational_level,
 186:     
 187:     -- Staff size and distribution
 188:     coalesce(oes.total_employees_ever, 0) as total_employees_ever,
 189:     coalesce(oes.current_active_employees, 0) as current_active_employees,
 190:     coalesce(oes.former_employees, 0) as former_employees,
 191:     coalesce(oes.total_positions_in_org, 0) as total_positions,
 192:     coalesce(oes.active_positions_count, 0) as active_positions_count,
 193:     
 194:     -- Calculate fill and utilization rates
 195:     case 
 196:         when coalesce(oes.total_positions_in_org, 0) > 0 then 
 197:             round(coalesce(oes.current_active_employees, 0) * 100.0 / oes.total_positions_in_org, 2)
 198:         else 0 
 199:     end as position_fill_rate,
 200:     
 201:     -- liquidity indicator
 202:     coalesce(oes.new_assignments_last_year, 0) as new_assignments_last_year,
 203:     coalesce(oes.departures_last_year, 0) as departures_last_year,
 204:     
 205:     -- annual churn rate
 206:     case 
 207:         when coalesce(oes.current_active_employees, 0) > 0 then 
 208:             round(coalesce(oes.departures_last_year, 0) * 100.0 / oes.current_active_employees, 2)
 209:         else 0 
 210:     end as annual_turnover_rate,
 211:     
 212:     -- tenure indicator
 213:     round(coalesce(oes.avg_current_tenure_days, 0) / 365.0, 2) as avg_current_tenure_years,
 214:     round(coalesce(oes.avg_former_tenure_days, 0) / 365.0, 2) as avg_former_tenure_years,
 215:     
 216:     -- organizational role structure
 217:     coalesce(oes.unique_organization_roles, 0) as unique_organization_roles,
 218:     coalesce(oes.management_role_employees, 0) as management_role_employees,
 219:     coalesce(oes.director_role_employees, 0) as director_role_employees,
 220:     coalesce(oes.lead_role_employees, 0) as lead_role_employees,
 221:     
 222:     -- management ratio
 223:     case 
 224:         when coalesce(oes.current_active_employees, 0) > 0 then 
 225:             round((coalesce(oes.management_role_employees, 0) + coalesce(oes.director_role_employees, 0)) * 100.0 / oes.current_active_employees, 2)
 226:         else 0 
 227:     end as management_ratio,
 228:     
 229:     -- Performance and Quality Metrics
 230:     coalesce(opm.avg_employee_performance, 0) as avg_employee_performance_score,
 231:     coalesce(opm.avg_career_development, 0) as avg_career_development_score,
 232:     coalesce(opm.avg_retention_stability, 0) as avg_retention_stability_score,
 233:     
 234:     -- Employee value distribution
 235:     coalesce(opm.high_value_stable_employees, 0) as high_value_stable_employees,
 236:     coalesce(opm.high_value_flight_risk_employees, 0) as high_value_flight_risk_employees,
 237:     coalesce(opm.stable_development_employees, 0) as stable_development_employees,
 238:     coalesce(opm.development_required_employees, 0) as development_required_employees,
 239:     
 240:     -- risk distribution
 241:     coalesce(opm.high_risk_employees, 0) as high_risk_employees,
 242:     coalesce(opm.medium_risk_employees, 0) as medium_risk_employees,
 243:     coalesce(opm.low_risk_employees, 0) as low_risk_employees,
 244:     
 245:     -- risk ratio
 246:     case 
 247:         when coalesce(oes.current_active_employees, 0) > 0 then 
 248:             round(coalesce(opm.high_risk_employees, 0) * 100.0 / oes.current_active_employees, 2)
 249:         else 0 
 250:     end as high_risk_employee_percentage,
 251:     
 252:     -- Employee maturity distribution
 253:     coalesce(opm.new_hire_employees, 0) as new_hire_employees,
 254:     coalesce(opm.junior_employees, 0) as junior_employees,
 255:     coalesce(opm.experienced_employees, 0) as experienced_employees,
 256:     coalesce(opm.senior_employees, 0) as senior_employees,
 257:     coalesce(opm.veteran_employees, 0) as veteran_employees,
 258:     
 259:     -- diversity index
 260:     coalesce(opm.ethnic_diversity_count, 0) as ethnic_diversity_count,
 261:     coalesce(opm.military_veterans_count, 0) as military_veterans_count,
 262:     coalesce(opm.avg_employee_age, 0) as avg_employee_age,
 263:     
 264:     -- Salary level distribution
 265:     coalesce(opm.entry_level_employees, 0) as entry_level_employees,
 266:     coalesce(opm.mid_level_employees, 0) as mid_level_employees,
 267:     coalesce(opm.senior_level_employees, 0) as senior_level_employees,
 268:     coalesce(opm.executive_level_employees, 0) as executive_level_employees,
 269:     
 270:     -- career development indicators
 271:     coalesce(opm.total_promotions_in_org, 0) as total_promotions_in_organization,
 272:     coalesce(opm.high_achievers_count, 0) as high_achievers_count,
 273:     coalesce(opm.fast_track_employees_count, 0) as fast_track_employees_count,
 274:     
 275:     -- Overall organizational health score (0-100)
 276:     round(
 277:         (-- Employee performance (30%)
 278:          least(30, coalesce(opm.avg_employee_performance, 0) * 0.3) +
 279:          -- Retention stability (25%)
 280:          (case when coalesce(oes.departures_last_year, 0) = 0 and coalesce(oes.current_active_employees, 0) > 0 then 25
 281:                when annual_turnover_rate <= 10 then 20
 282:                when annual_turnover_rate <= 20 then 15
 283:                when annual_turnover_rate <= 30 then 10
 284:                else 5 end) +
 285:          -- Employee development (20%)
 286:          least(20, coalesce(opm.avg_career_development, 0) * 0.2) +
 287:          -- Organizational efficiency (15%)
 288:          (case when position_fill_rate >= 90 then 15
 289:                when position_fill_rate >= 80 then 12
 290:                when position_fill_rate >= 70 then 9
 291:                else 6 end) +
 292:          -- Risk Control (10%)
 293:          (case when high_risk_employee_percentage <= 5 then 10
 294:                when high_risk_employee_percentage <= 15 then 7
 295:                when high_risk_employee_percentage <= 25 then 4
 296:                else 2 end))
 297:     , 2) as organization_health_score,
 298:     
 299:     -- Organizational Performance Classification
 300:     case 
 301:         when round(
 302:             (least(30, coalesce(opm.avg_employee_performance, 0) * 0.3) +
 303:              (case when coalesce(oes.departures_last_year, 0) = 0 and coalesce(oes.current_active_employees, 0) > 0 then 25
 304:                    when (case when coalesce(oes.current_active_employees, 0) > 0 then round(coalesce(oes.departures_last_year, 0) * 100.0 / oes.current_active_employees, 2) else 0 end) <= 10 then 20
 305:                    when (case when coalesce(oes.current_active_employees, 0) > 0 then round(coalesce(oes.departures_last_year, 0) * 100.0 / oes.current_active_employees, 2) else 0 end) <= 20 then 15
 306:                    else 10 end) +
 307:              least(20, coalesce(opm.avg_career_development, 0) * 0.2) +
 308:              (case when (case when coalesce(oes.total_positions_in_org, 0) > 0 then round(coalesce(oes.current_active_employees, 0) * 100.0 / oes.total_positions_in_org, 2) else 0 end) >= 90 then 15 else 10 end) +
 309:              10), 2) >= 80 then 'Excellent Performance'
 310:         when round(
 311:             (least(30, coalesce(opm.avg_employee_performance, 0) * 0.3) +
 312:              (case when coalesce(oes.departures_last_year, 0) = 0 and coalesce(oes.current_active_employees, 0) > 0 then 25 else 15 end) +
 313:              least(20, coalesce(opm.avg_career_development, 0) * 0.2) +
 314:              15 + 10), 2) >= 60 then 'Good Performance'
 315:         when round(
 316:             (least(30, coalesce(opm.avg_employee_performance, 0) * 0.3) +
 317:              15 + least(20, coalesce(opm.avg_career_development, 0) * 0.2) +
 318:              10 + 5), 2) >= 40 then 'Average Performance'
 319:         else 'Needs Improvement'
 320:     end as performance_category,
 321:     
 322:     -- Organization size classification
 323:     case 
 324:         when coalesce(oes.current_active_employees, 0) = 0 then 'Empty Organization'
 325:         when coalesce(oes.current_active_employees, 0) <= 5 then 'Micro Team'
 326:         when coalesce(oes.current_active_employees, 0) <= 15 then 'Small Team'
 327:         when coalesce(oes.current_active_employees, 0) <= 50 then 'Medium Team'
 328:         when coalesce(oes.current_active_employees, 0) <= 200 then 'Large Team'
 329:         else 'Enterprise Unit'
 330:     end as organization_size_category,
 331:     
 332:     -- Latest event date
 333:     coalesce(oes.last_new_assignment_date, oha.organization_created_date) as last_activity_date,
 334:     coalesce(oes.last_departure_date, '1900-01-01'::date) as last_departure_date,
 335:     
 336:     -- management advice
 337:     case 
 338:         when coalesce(oes.current_active_employees, 0) = 0 then 'Review Organization Necessity'
 339:         when annual_turnover_rate > 30 then 'Critical: Focus on Retention'
 340:         when high_risk_employee_percentage > 25 then 'Address Employee Risk Factors'
 341:         when position_fill_rate < 70 then 'Improve Recruitment and Staffing'
 342:         when coalesce(opm.avg_employee_performance, 0) < 50 then 'Enhance Performance Management'
 343:         when management_ratio > 40 then 'Optimize Management Structure'
 344:         else 'Maintain Current Excellence'
 345:     end as management_recommendation,
 346:     
 347:     -- Data quality check
 348:     case 
 349:         when oha.organization_name is null or oha.organization_name = '' then 'ERROR: Missing organization name'
 350:         when coalesce(oes.current_active_employees, 0) > coalesce(oes.total_positions_in_org, 0) + 10 then 'WARNING: More employees than positions'
 351:         when annual_turnover_rate > 100 then 'WARNING: Turnover rate exceeds 100%'
 352:         when oha.organization_age_days < 0 then 'ERROR: Invalid organization creation date'
 353:         else 'VALID'
 354:     end as data_quality_flag,
 355:     
 356:     -- Analysis timestamp
 357:     current_timestamp as analysis_timestamp
 358:     
 359: from organization_hierarchy_analysis oha
 360: left join organization_employee_stats oes
 361:     on oha.organization_id = oes.organization_id
 362:     and oha.source_relation = oes.source_relation
 363: left join organization_performance_metrics opm
 364:     on oha.organization_id = opm.organization_id
 365:     and oha.source_relation = opm.source_relation
 366: order by 
 367:     coalesce(oes.current_active_employees, 0) desc,
 368:     coalesce(opm.avg_employee_performance, 0) desc,
 369:     oha.organization_name
```

### 本表原始数据可评估性

按015已保存的SQL、schema、行数及typed完整行哈希核对本表依赖；不是仅凭全题其他raw不同就排除本表。依赖列表来自015静态边，动态引用限制仍见015记录。

|依赖raw|比较|schema/列类型相同|行数相同|有序typed行hash相同|差异原因|
|---|---|---|---|---|---|
|raw.job_family|gold_vs_initial|True|True|True||
|raw.job_family_group|gold_vs_initial|True|True|True||
|raw.job_family_job_family_group|gold_vs_initial|True|True|True||
|raw.job_family_job_profile|gold_vs_initial|True|True|True||
|raw.job_profile|gold_vs_initial|True|True|True||
|raw.military_service|gold_vs_initial|True|True|True||
|raw.organization|gold_vs_initial|True|True|True||
|raw.organization_role|gold_vs_initial|True|True|True||
|raw.organization_role_worker|gold_vs_initial|True|True|True||
|raw.person_contact_email_address|gold_vs_initial|True|True|True||
|raw.person_info_history|gold_vs_initial|True|True|True||
|raw.person_name|gold_vs_initial|True|True|True||
|raw.personal_information_ethnicity|gold_vs_initial|True|True|True||
|raw.position|gold_vs_initial|True|True|True||
|raw.position_job_profile|gold_vs_initial|True|True|True||
|raw.worker_history|gold_vs_initial|True|True|True||
|raw.worker_position_history|gold_vs_initial|True|True|True||
|raw.worker_position_organization_history|gold_vs_initial|True|True|True||
|raw.worker_to_person|gold_vs_initial|True|True|True||
|raw.job_family|gold_vs_agent|True|True|True||
|raw.job_family_group|gold_vs_agent|True|True|True||
|raw.job_family_job_family_group|gold_vs_agent|True|True|True||
|raw.job_family_job_profile|gold_vs_agent|True|True|True||
|raw.job_profile|gold_vs_agent|True|True|True||
|raw.military_service|gold_vs_agent|True|True|True||
|raw.organization|gold_vs_agent|True|True|True||
|raw.organization_role|gold_vs_agent|True|True|True||
|raw.organization_role_worker|gold_vs_agent|True|True|True||
|raw.person_contact_email_address|gold_vs_agent|True|False|None|row_counts_differ|
|raw.person_info_history|gold_vs_agent|True|True|True||
|raw.person_name|gold_vs_agent|True|True|True||
|raw.personal_information_ethnicity|gold_vs_agent|True|True|True||
|raw.position|gold_vs_agent|True|True|True||
|raw.position_job_profile|gold_vs_agent|True|True|True||
|raw.worker_history|gold_vs_agent|True|True|True||
|raw.worker_position_history|gold_vs_agent|True|True|True||
|raw.worker_position_organization_history|gold_vs_agent|True|True|True||
|raw.worker_to_person|gold_vs_agent|True|True|True||

补充诊断与原始事件见[016_raw_diagnostics.json](../016_raw_diagnostics.json)。

## 3. agent实际看到的信息与不确定性四档

event1完整给出组织关系、比率默认0和标签；event25/31/33/35/37/51逐步生成marts，event55修列名；event65→66最终执行，event69/71只读检查，event73之后写报告。不能用当前留存库反推轨迹中必然存在某个删除动作。

四档只记录表述事实，不改变原因类别。同类并列虽折叠表级类别，各独立项仍分别填写。不可评估的两张针对源输入差异填写。普通SQL操作或“已实现清洗”等功能清单不等于说出了相关选择。

|主项/输入差异|类别|不确定性四档|事件|
|---|---|---|---|
|annual_zero|C|看到了但没提|1|
|management_zero|C|看到了但没提|1|
|maturity_labels|O|看到了但没提|1|
|size_labels|O|看到了但没提|1|

### annual_zero：看到了但没提

契约比率默认0和枚举值均可见。最终报告提到当前任职人数为0及另一张performance表为空，但没有说明本表两个比率零分母处理或枚举取值；“handled nulls and categories”只是功能概述。

事件 **1**，字段`args.content`；[轨迹原文](../016_trace_impl-016.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/1.json`。
```text
employees ÷ total_positions × 100 when total_positions > 0, else 0. - annual_turnover_rate (%) = departures_last_year ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - avg_current_tenure_years and avg_former_tenure_years = respective average tenure days ÷ 365, rounded to 2; if no data, treated as 0. - management_ratio (%) = (management_role_employees + director_role_employees) ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - high_risk_employee_percentage (%) = high_risk_employees ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - organization_health_score (0–100) = sum of: performance (cap at 30% of average performance), turnover (25/20/15/10/5 by thresholds using annual_turnover_rate and zero departures case), development (cap at 20% of average career development), efficiency (15/12/9/6 by position_fill_rate thresholds), an
```

### management_zero：看到了但没提

契约比率默认0和枚举值均可见。最终报告提到当前任职人数为0及另一张performance表为空，但没有说明本表两个比率零分母处理或枚举取值；“handled nulls and categories”只是功能概述。

事件 **1**，字段`args.content`；[轨迹原文](../016_trace_impl-016.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/1.json`。
```text
 average tenure days ÷ 365, rounded to 2; if no data, treated as 0. - management_ratio (%) = (management_role_employees + director_role_employees) ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - high_risk_employee_percentage (%) = high_risk_employees ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - organization_health_score (0–100) = sum of: performance (cap at 30% of average performance), turnover (25/20/15/10/5 by thresholds using annual_turnover_rate and zero departures case), development (cap at 20% of average career development), efficiency (15/12/9/6 by position_fill_rate thresholds), and risk (10/7/4/2 by high_risk_employee_percentage thresholds); final score rounded to 2 decimals. - performance_category uses a weighted composite with thresholds: Excellent if composite ≥ 80; else Good if ≥ 60; else Average if ≥ 40; otherwise Needs Improvement
```

### maturity_labels：看到了但没提

契约比率默认0和枚举值均可见。最终报告提到当前任职人数为0及另一张performance表为空，但没有说明本表两个比率零分母处理或枚举取值；“handled nulls and categories”只是功能概述。

事件 **1**，字段`args.content`；[轨迹原文](../016_trace_impl-016.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/1.json`。
```text
ganization_age_years is that divided by 365, rounded to 2 decimals. - organization_maturity_level by age_days: <1 year New; 1–3 years Young; 3–10 years Mature; 10+ years Legacy. - organizational_level from organization_type: Company/Division/Department/Team mapped to corresponding Level; others to Other Level. - access_level from visibility: Public→Open Access, Private→Restricted Access, others Unknown Access. 6) Final metrics and rules (rates rounded to 2 decimals; missing metrics default to 0 unless noted): - position_fill_rate (%) = current_active_employees ÷ total_positions × 100 when total_positions > 0, else 0. - annual_turnover_rate (%) = departures_last_year ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - avg_current_tenure_years and avg_former_tenure_years = respective average tenure days ÷ 365, rounded to 2; if no data, treated as 0. - management_ratio (%) = (manageme
```

### size_labels：看到了但没提

契约比率默认0和枚举值均可见。最终报告提到当前任职人数为0及另一张performance表为空，但没有说明本表两个比率零分母处理或枚举取值；“handled nulls and categories”只是功能概述。

事件 **1**，字段`args.content`；[轨迹原文](../016_trace_impl-016.json)；原文件`data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/1.json`。
```text
mprovement (weights and constants follow the detailed rules above). - organization_size_category by current_active_employees: 0 Empty; ≤5 Micro; ≤15 Small; ≤50 Medium; ≤200 Large; else Enterprise. - last_activity_date is the most recent assignment start; if none, use organization_created_date. - last_departure_date is the most recent assignment end; if none, use 1900-01-01. - management_recommendation (first match): if no active employees then review necessity; else if turnover > 30% then focus on retention; else if high-risk % > 25% then address risk; else if fill rate < 70% then improve staffing; else if average performance < 50 then enhance performance management; else if management_ratio > 40% then optimize structure; else maintain excellence. - data_quality_flag precedence: missing or blank organization name → ERROR; active employees exceed positions by more than 10 → WARNING; turnover rate > 100% → WA
```

已检视85个归档事件、最终报告及写报告命令。thought/args.thought没有非空留存，不推断未归档的内部思考。025复用017脱敏导出，其账户标识脱敏不涉及本次引句。

## 4. 查询、重跑与规模

复用核实查询 **0条**；018新增核实查询 **0条**。核实代价：需要查业务说明。每表累计仍≤5，失败尝试按旧记录计数。
[采用的重跑JSON](../016_reruns_impl-016.json)保存SQL单处替换、基线/干预及L0–L3每列计数。

下面完整复用016的查询与重跑证据；其中“新增/本次”的执行归属仍为016，018没有重复执行。
核实查询合计 **0条**（含014复用；本轮新增0条）；核实代价档：**需要查业务说明**。诊断不计入5条上限。查询失败与重复执行如实保留。

无新增数据核实查询；本表依据契约/SQL和只读诊断或重跑判断。

### 比较口径

L0沿用现有lower/trim/NULL表示，L1数字/布尔归一，L2数值两位小数，L3再宽松日期。评测键固定L0且纳入比较列并集，不因宽松档位重新归一。行规模=独有键行+共同键多出的行+共同键不同配对行；格子规模=独有/多出行×含键比较列数+共同键配对不同格子。没有共同键时每列的共同键差异0不表示整表相同。重复键先抵消完全相同行，016新算结果对剩余元组按字典序固定配对，避免独立逐列最小值无法构成同一行配对；非重复键结果不受影响。先用行规模选择主因，所有单项行改善相同时才用格子；参与因素沿用本表选定口径。

键：`['organization_id']`；比较列（与键取并集）：`['access_level', 'active_positions_count', 'analysis_timestamp', 'annual_turnover_rate', 'avg_career_development_score', 'avg_employee_age', 'avg_employee_performance_score', 'avg_former_tenure_years', 'avg_retention_stability_score', 'current_active_employees', 'data_quality_flag', 'departures_last_year', 'development_required_employees', 'director_role_employees', 'entry_level_employees', 'ethnic_diversity_count', 'executive_level_employees', 'experienced_employees', 'fast_track_employees_count', 'former_employees', 'high_achievers_count', 'high_risk_employees', 'high_value_flight_risk_employees', 'high_value_stable_employees', 'junior_employees', 'last_activity_date', 'last_departure_date', 'lead_role_employees', 'low_risk_employees', 'management_ratio', 'management_recommendation', 'management_role_employees', 'medium_risk_employees', 'mid_level_employees', 'military_veterans_count', 'new_assignments_last_year', 'new_hire_employees', 'organization_age_days', 'organization_age_years', 'organization_code', 'organization_created_date', 'organization_health_score', 'organization_id', 'organization_maturity_level', 'organization_name', 'organization_size_category', 'organization_sub_type', 'organization_type', 'organizational_level', 'performance_category', 'position_fill_rate', 'senior_employees', 'senior_level_employees', 'stable_development_employees', 'staffing_model', 'total_employees_ever', 'total_positions', 'total_promotions_in_organization', 'unique_organization_roles', 'veteran_employees', 'visibility']`。

所有原数据库READ_ONLY；新执行只在`data/016_work/`，014复用结果来自`data/014_work/`。staging使用agent留存raw，intermediate/marts用gold上游CS。每个干预从同一原SQL基线独立产生；替换的原文、新文及offset在JSON和下面给出，未顺序叠加其他修复。

复用说明：本次重新执行；原013留存输出另列

共同时间控制：`[{"pattern": "\\bcurrent_timestamp\\b", "replacement": "TIMESTAMPTZ '2025-10-13 13:18:28.226+08'", "count": 1}, {"pattern": "\\bcurrent_date\\b", "replacement": "DATE '2025-10-13'", "count": 8}]`。013固定候选日、016固定gold实际时刻只作为所有干预共用条件；不是隐藏的因果修复。004的特殊诊断另见正文。

### 单项改善概览

|单项|L0行：前→后|L0格：前→后|首次整表匹配|
|---|---|---|---|
|annual_zero|117→117|696→579|无|
|management_zero|117→117|696→579|无|
|risk_zero|117→117|696→696|无|
|fill_zero|117→117|696→696|无|
|maturity_labels|117→117|696→579|无|
|size_labels|117→117|696→579|无|
|roles_relationship|117→117|696→590|无|
|tenure_join_weight|117→117|696→691|无|
|health_turnover_rule|117→117|696→696|无|
|health_risk_rule|117→117|696→696|无|

### 留存输出基线

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|117|117|0|0|0/0|117|117|813|False|
|L1|117|117|0|0|0/0|117|117|813|False|
|L2|117|117|0|0|0/0|117|117|813|False|
|L3|117|117|0|0|0/0|117|117|696|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|organization_id|0|0|0|0|
|access_level|0|0|0|0|
|active_positions_count|0|0|0|0|
|analysis_timestamp|117|117|117|0|
|annual_turnover_rate|117|117|117|117|
|avg_career_development_score|0|0|0|0|
|avg_employee_age|0|0|0|0|
|avg_employee_performance_score|0|0|0|0|
|avg_former_tenure_years|5|5|5|5|
|avg_retention_stability_score|0|0|0|0|
|current_active_employees|0|0|0|0|
|data_quality_flag|0|0|0|0|
|departures_last_year|0|0|0|0|
|development_required_employees|0|0|0|0|
|director_role_employees|0|0|0|0|
|entry_level_employees|0|0|0|0|
|ethnic_diversity_count|0|0|0|0|
|executive_level_employees|0|0|0|0|
|experienced_employees|0|0|0|0|
|fast_track_employees_count|0|0|0|0|
|former_employees|0|0|0|0|
|high_achievers_count|0|0|0|0|
|high_risk_employees|0|0|0|0|
|high_value_flight_risk_employees|0|0|0|0|
|high_value_stable_employees|0|0|0|0|
|junior_employees|0|0|0|0|
|last_activity_date|0|0|0|0|
|last_departure_date|0|0|0|0|
|lead_role_employees|0|0|0|0|
|low_risk_employees|0|0|0|0|
|management_ratio|117|117|117|117|
|management_recommendation|0|0|0|0|
|management_role_employees|0|0|0|0|
|medium_risk_employees|0|0|0|0|
|mid_level_employees|0|0|0|0|
|military_veterans_count|0|0|0|0|
|new_assignments_last_year|0|0|0|0|
|new_hire_employees|0|0|0|0|
|organization_age_days|0|0|0|0|
|organization_age_years|0|0|0|0|
|organization_code|0|0|0|0|
|organization_created_date|0|0|0|0|
|organization_health_score|117|117|117|117|
|organization_maturity_level|117|117|117|117|
|organization_name|0|0|0|0|
|organization_size_category|117|117|117|117|
|organization_sub_type|0|0|0|0|
|organization_type|0|0|0|0|
|organizational_level|0|0|0|0|
|performance_category|0|0|0|0|
|position_fill_rate|0|0|0|0|
|senior_employees|0|0|0|0|
|senior_level_employees|0|0|0|0|
|stable_development_employees|0|0|0|0|
|staffing_model|0|0|0|0|
|total_employees_ever|0|0|0|0|
|total_positions|0|0|0|0|
|total_promotions_in_organization|0|0|0|0|
|unique_organization_roles|106|106|106|106|
|veteran_employees|0|0|0|0|
|visibility|0|0|0|0|

### 重跑 baseline

SQL：`data/016_work/impl-016/baseline.sql`；SHA-256：`59eb53d91701e95b7e03e4ae18c4fbe6877bbb3ca41f59c38e987e0248e82e4e`。

不增加因果修改的基线。

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|117|117|0|0|0/0|117|117|696|False|
|L1|117|117|0|0|0/0|117|117|696|False|
|L2|117|117|0|0|0/0|117|117|696|False|
|L3|117|117|0|0|0/0|117|117|696|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|organization_id|0|0|0|0|
|access_level|0|0|0|0|
|active_positions_count|0|0|0|0|
|analysis_timestamp|0|0|0|0|
|annual_turnover_rate|117|117|117|117|
|avg_career_development_score|0|0|0|0|
|avg_employee_age|0|0|0|0|
|avg_employee_performance_score|0|0|0|0|
|avg_former_tenure_years|5|5|5|5|
|avg_retention_stability_score|0|0|0|0|
|current_active_employees|0|0|0|0|
|data_quality_flag|0|0|0|0|
|departures_last_year|0|0|0|0|
|development_required_employees|0|0|0|0|
|director_role_employees|0|0|0|0|
|entry_level_employees|0|0|0|0|
|ethnic_diversity_count|0|0|0|0|
|executive_level_employees|0|0|0|0|
|experienced_employees|0|0|0|0|
|fast_track_employees_count|0|0|0|0|
|former_employees|0|0|0|0|
|high_achievers_count|0|0|0|0|
|high_risk_employees|0|0|0|0|
|high_value_flight_risk_employees|0|0|0|0|
|high_value_stable_employees|0|0|0|0|
|junior_employees|0|0|0|0|
|last_activity_date|0|0|0|0|
|last_departure_date|0|0|0|0|
|lead_role_employees|0|0|0|0|
|low_risk_employees|0|0|0|0|
|management_ratio|117|117|117|117|
|management_recommendation|0|0|0|0|
|management_role_employees|0|0|0|0|
|medium_risk_employees|0|0|0|0|
|mid_level_employees|0|0|0|0|
|military_veterans_count|0|0|0|0|
|new_assignments_last_year|0|0|0|0|
|new_hire_employees|0|0|0|0|
|organization_age_days|0|0|0|0|
|organization_age_years|0|0|0|0|
|organization_code|0|0|0|0|
|organization_created_date|0|0|0|0|
|organization_health_score|117|117|117|117|
|organization_maturity_level|117|117|117|117|
|organization_name|0|0|0|0|
|organization_size_category|117|117|117|117|
|organization_sub_type|0|0|0|0|
|organization_type|0|0|0|0|
|organizational_level|0|0|0|0|
|performance_category|0|0|0|0|
|position_fill_rate|0|0|0|0|
|senior_employees|0|0|0|0|
|senior_level_employees|0|0|0|0|
|stable_development_employees|0|0|0|0|
|staffing_model|0|0|0|0|
|total_employees_ever|0|0|0|0|
|total_positions|0|0|0|0|
|total_promotions_in_organization|0|0|0|0|
|unique_organization_roles|106|106|106|106|
|veteran_employees|0|0|0|0|
|visibility|0|0|0|0|

### 重跑 annual_zero

SQL：`data/016_work/impl-016/annual_zero.sql`；SHA-256：`c2ffa744ab0dcba24528e6a8dec02832210cf287f1ece700321f54cbd38b0fab`。

唯一原文位置offset=6714，替换前：
```sql
round(coalesce(departures_last_year,0)*100.0/NULLIF(current_active_employees,0),2)::DOUBLE
```
替换后：
```sql
coalesce(round(coalesce(departures_last_year,0)*100.0/NULLIF(current_active_employees,0),2)::DOUBLE,0)
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|117|117|0|0|0/0|117|117|579|False|
|L1|117|117|0|0|0/0|117|117|579|False|
|L2|117|117|0|0|0/0|117|117|579|False|
|L3|117|117|0|0|0/0|117|117|579|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|organization_id|0|0|0|0|
|access_level|0|0|0|0|
|active_positions_count|0|0|0|0|
|analysis_timestamp|0|0|0|0|
|annual_turnover_rate|0|0|0|0|
|avg_career_development_score|0|0|0|0|
|avg_employee_age|0|0|0|0|
|avg_employee_performance_score|0|0|0|0|
|avg_former_tenure_years|5|5|5|5|
|avg_retention_stability_score|0|0|0|0|
|current_active_employees|0|0|0|0|
|data_quality_flag|0|0|0|0|
|departures_last_year|0|0|0|0|
|development_required_employees|0|0|0|0|
|director_role_employees|0|0|0|0|
|entry_level_employees|0|0|0|0|
|ethnic_diversity_count|0|0|0|0|
|executive_level_employees|0|0|0|0|
|experienced_employees|0|0|0|0|
|fast_track_employees_count|0|0|0|0|
|former_employees|0|0|0|0|
|high_achievers_count|0|0|0|0|
|high_risk_employees|0|0|0|0|
|high_value_flight_risk_employees|0|0|0|0|
|high_value_stable_employees|0|0|0|0|
|junior_employees|0|0|0|0|
|last_activity_date|0|0|0|0|
|last_departure_date|0|0|0|0|
|lead_role_employees|0|0|0|0|
|low_risk_employees|0|0|0|0|
|management_ratio|117|117|117|117|
|management_recommendation|0|0|0|0|
|management_role_employees|0|0|0|0|
|medium_risk_employees|0|0|0|0|
|mid_level_employees|0|0|0|0|
|military_veterans_count|0|0|0|0|
|new_assignments_last_year|0|0|0|0|
|new_hire_employees|0|0|0|0|
|organization_age_days|0|0|0|0|
|organization_age_years|0|0|0|0|
|organization_code|0|0|0|0|
|organization_created_date|0|0|0|0|
|organization_health_score|117|117|117|117|
|organization_maturity_level|117|117|117|117|
|organization_name|0|0|0|0|
|organization_size_category|117|117|117|117|
|organization_sub_type|0|0|0|0|
|organization_type|0|0|0|0|
|organizational_level|0|0|0|0|
|performance_category|0|0|0|0|
|position_fill_rate|0|0|0|0|
|senior_employees|0|0|0|0|
|senior_level_employees|0|0|0|0|
|stable_development_employees|0|0|0|0|
|staffing_model|0|0|0|0|
|total_employees_ever|0|0|0|0|
|total_positions|0|0|0|0|
|total_promotions_in_organization|0|0|0|0|
|unique_organization_roles|106|106|106|106|
|veteran_employees|0|0|0|0|
|visibility|0|0|0|0|

### 重跑 management_zero

SQL：`data/016_work/impl-016/management_zero.sql`；SHA-256：`ad40641f4decbb34c10291933ad8e9974a4a554103930aaf0d517171068dcc73`。

唯一原文位置offset=7252，替换前：
```sql
round((coalesce(management_role_employees,0)+coalesce(director_role_employees,0))*100.0/NULLIF(current_active_employees,0),2)::DOUBLE
```
替换后：
```sql
coalesce(round((coalesce(management_role_employees,0)+coalesce(director_role_employees,0))*100.0/NULLIF(current_active_employees,0),2)::DOUBLE,0)
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|117|117|0|0|0/0|117|117|579|False|
|L1|117|117|0|0|0/0|117|117|579|False|
|L2|117|117|0|0|0/0|117|117|579|False|
|L3|117|117|0|0|0/0|117|117|579|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|organization_id|0|0|0|0|
|access_level|0|0|0|0|
|active_positions_count|0|0|0|0|
|analysis_timestamp|0|0|0|0|
|annual_turnover_rate|117|117|117|117|
|avg_career_development_score|0|0|0|0|
|avg_employee_age|0|0|0|0|
|avg_employee_performance_score|0|0|0|0|
|avg_former_tenure_years|5|5|5|5|
|avg_retention_stability_score|0|0|0|0|
|current_active_employees|0|0|0|0|
|data_quality_flag|0|0|0|0|
|departures_last_year|0|0|0|0|
|development_required_employees|0|0|0|0|
|director_role_employees|0|0|0|0|
|entry_level_employees|0|0|0|0|
|ethnic_diversity_count|0|0|0|0|
|executive_level_employees|0|0|0|0|
|experienced_employees|0|0|0|0|
|fast_track_employees_count|0|0|0|0|
|former_employees|0|0|0|0|
|high_achievers_count|0|0|0|0|
|high_risk_employees|0|0|0|0|
|high_value_flight_risk_employees|0|0|0|0|
|high_value_stable_employees|0|0|0|0|
|junior_employees|0|0|0|0|
|last_activity_date|0|0|0|0|
|last_departure_date|0|0|0|0|
|lead_role_employees|0|0|0|0|
|low_risk_employees|0|0|0|0|
|management_ratio|0|0|0|0|
|management_recommendation|0|0|0|0|
|management_role_employees|0|0|0|0|
|medium_risk_employees|0|0|0|0|
|mid_level_employees|0|0|0|0|
|military_veterans_count|0|0|0|0|
|new_assignments_last_year|0|0|0|0|
|new_hire_employees|0|0|0|0|
|organization_age_days|0|0|0|0|
|organization_age_years|0|0|0|0|
|organization_code|0|0|0|0|
|organization_created_date|0|0|0|0|
|organization_health_score|117|117|117|117|
|organization_maturity_level|117|117|117|117|
|organization_name|0|0|0|0|
|organization_size_category|117|117|117|117|
|organization_sub_type|0|0|0|0|
|organization_type|0|0|0|0|
|organizational_level|0|0|0|0|
|performance_category|0|0|0|0|
|position_fill_rate|0|0|0|0|
|senior_employees|0|0|0|0|
|senior_level_employees|0|0|0|0|
|stable_development_employees|0|0|0|0|
|staffing_model|0|0|0|0|
|total_employees_ever|0|0|0|0|
|total_positions|0|0|0|0|
|total_promotions_in_organization|0|0|0|0|
|unique_organization_roles|106|106|106|106|
|veteran_employees|0|0|0|0|
|visibility|0|0|0|0|

### 重跑 risk_zero

SQL：`data/016_work/impl-016/risk_zero.sql`；SHA-256：`eccda556545e32f9c5b78e92fcec8b96721a703a163f91e182e4f84550b03c21`。

唯一原文位置offset=8149，替换前：
```sql
round(coalesce(high_risk_employees,0)*100.0/NULLIF(current_active_employees,0),2)::DOUBLE
```
替换后：
```sql
coalesce(round(coalesce(high_risk_employees,0)*100.0/NULLIF(current_active_employees,0),2)::DOUBLE,0)
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|117|117|0|0|0/0|117|117|696|False|
|L1|117|117|0|0|0/0|117|117|696|False|
|L2|117|117|0|0|0/0|117|117|696|False|
|L3|117|117|0|0|0/0|117|117|696|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|organization_id|0|0|0|0|
|access_level|0|0|0|0|
|active_positions_count|0|0|0|0|
|analysis_timestamp|0|0|0|0|
|annual_turnover_rate|117|117|117|117|
|avg_career_development_score|0|0|0|0|
|avg_employee_age|0|0|0|0|
|avg_employee_performance_score|0|0|0|0|
|avg_former_tenure_years|5|5|5|5|
|avg_retention_stability_score|0|0|0|0|
|current_active_employees|0|0|0|0|
|data_quality_flag|0|0|0|0|
|departures_last_year|0|0|0|0|
|development_required_employees|0|0|0|0|
|director_role_employees|0|0|0|0|
|entry_level_employees|0|0|0|0|
|ethnic_diversity_count|0|0|0|0|
|executive_level_employees|0|0|0|0|
|experienced_employees|0|0|0|0|
|fast_track_employees_count|0|0|0|0|
|former_employees|0|0|0|0|
|high_achievers_count|0|0|0|0|
|high_risk_employees|0|0|0|0|
|high_value_flight_risk_employees|0|0|0|0|
|high_value_stable_employees|0|0|0|0|
|junior_employees|0|0|0|0|
|last_activity_date|0|0|0|0|
|last_departure_date|0|0|0|0|
|lead_role_employees|0|0|0|0|
|low_risk_employees|0|0|0|0|
|management_ratio|117|117|117|117|
|management_recommendation|0|0|0|0|
|management_role_employees|0|0|0|0|
|medium_risk_employees|0|0|0|0|
|mid_level_employees|0|0|0|0|
|military_veterans_count|0|0|0|0|
|new_assignments_last_year|0|0|0|0|
|new_hire_employees|0|0|0|0|
|organization_age_days|0|0|0|0|
|organization_age_years|0|0|0|0|
|organization_code|0|0|0|0|
|organization_created_date|0|0|0|0|
|organization_health_score|117|117|117|117|
|organization_maturity_level|117|117|117|117|
|organization_name|0|0|0|0|
|organization_size_category|117|117|117|117|
|organization_sub_type|0|0|0|0|
|organization_type|0|0|0|0|
|organizational_level|0|0|0|0|
|performance_category|0|0|0|0|
|position_fill_rate|0|0|0|0|
|senior_employees|0|0|0|0|
|senior_level_employees|0|0|0|0|
|stable_development_employees|0|0|0|0|
|staffing_model|0|0|0|0|
|total_employees_ever|0|0|0|0|
|total_positions|0|0|0|0|
|total_promotions_in_organization|0|0|0|0|
|unique_organization_roles|106|106|106|106|
|veteran_employees|0|0|0|0|
|visibility|0|0|0|0|

### 重跑 fill_zero

SQL：`data/016_work/impl-016/fill_zero.sql`；SHA-256：`f7a6bdbccfde219dc7507fc21b02c6dd0d9cc2b3492e4b695046715178a490f8`。

唯一原文位置offset=6475，替换前：
```sql
round(coalesce(current_active_employees,0)*100.0/NULLIF(total_positions,0),2)::DOUBLE
```
替换后：
```sql
coalesce(round(coalesce(current_active_employees,0)*100.0/NULLIF(total_positions,0),2)::DOUBLE,0)
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|117|117|0|0|0/0|117|117|696|False|
|L1|117|117|0|0|0/0|117|117|696|False|
|L2|117|117|0|0|0/0|117|117|696|False|
|L3|117|117|0|0|0/0|117|117|696|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|organization_id|0|0|0|0|
|access_level|0|0|0|0|
|active_positions_count|0|0|0|0|
|analysis_timestamp|0|0|0|0|
|annual_turnover_rate|117|117|117|117|
|avg_career_development_score|0|0|0|0|
|avg_employee_age|0|0|0|0|
|avg_employee_performance_score|0|0|0|0|
|avg_former_tenure_years|5|5|5|5|
|avg_retention_stability_score|0|0|0|0|
|current_active_employees|0|0|0|0|
|data_quality_flag|0|0|0|0|
|departures_last_year|0|0|0|0|
|development_required_employees|0|0|0|0|
|director_role_employees|0|0|0|0|
|entry_level_employees|0|0|0|0|
|ethnic_diversity_count|0|0|0|0|
|executive_level_employees|0|0|0|0|
|experienced_employees|0|0|0|0|
|fast_track_employees_count|0|0|0|0|
|former_employees|0|0|0|0|
|high_achievers_count|0|0|0|0|
|high_risk_employees|0|0|0|0|
|high_value_flight_risk_employees|0|0|0|0|
|high_value_stable_employees|0|0|0|0|
|junior_employees|0|0|0|0|
|last_activity_date|0|0|0|0|
|last_departure_date|0|0|0|0|
|lead_role_employees|0|0|0|0|
|low_risk_employees|0|0|0|0|
|management_ratio|117|117|117|117|
|management_recommendation|0|0|0|0|
|management_role_employees|0|0|0|0|
|medium_risk_employees|0|0|0|0|
|mid_level_employees|0|0|0|0|
|military_veterans_count|0|0|0|0|
|new_assignments_last_year|0|0|0|0|
|new_hire_employees|0|0|0|0|
|organization_age_days|0|0|0|0|
|organization_age_years|0|0|0|0|
|organization_code|0|0|0|0|
|organization_created_date|0|0|0|0|
|organization_health_score|117|117|117|117|
|organization_maturity_level|117|117|117|117|
|organization_name|0|0|0|0|
|organization_size_category|117|117|117|117|
|organization_sub_type|0|0|0|0|
|organization_type|0|0|0|0|
|organizational_level|0|0|0|0|
|performance_category|0|0|0|0|
|position_fill_rate|0|0|0|0|
|senior_employees|0|0|0|0|
|senior_level_employees|0|0|0|0|
|stable_development_employees|0|0|0|0|
|staffing_model|0|0|0|0|
|total_employees_ever|0|0|0|0|
|total_positions|0|0|0|0|
|total_promotions_in_organization|0|0|0|0|
|unique_organization_roles|106|106|106|106|
|veteran_employees|0|0|0|0|
|visibility|0|0|0|0|

### 重跑 maturity_labels

SQL：`data/016_work/impl-016/maturity_labels.sql`；SHA-256：`5b88e336d11accba6b575ba89385f12650e58c9be3ce33e703f493d4fc888414`。

唯一原文位置offset=5747，替换前：
```sql
THEN 'New' WHEN date_diff('day',effective_start,DATE '2025-10-13')<1095 THEN 'Young' WHEN date_diff('day',effective_start,DATE '2025-10-13')<3650 THEN 'Mature' ELSE 'Legacy'
```
替换后：
```sql
THEN 'New Organization (<1 year)' WHEN date_diff('day',effective_start,DATE '2025-10-13')<1095 THEN 'Young Organization (1-3 years)' WHEN date_diff('day',effective_start,DATE '2025-10-13')<3650 THEN 'Mature Organization (3-10 years)' ELSE 'Legacy Organization (10+ years)'
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|117|117|0|0|0/0|117|117|579|False|
|L1|117|117|0|0|0/0|117|117|579|False|
|L2|117|117|0|0|0/0|117|117|579|False|
|L3|117|117|0|0|0/0|117|117|579|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|organization_id|0|0|0|0|
|access_level|0|0|0|0|
|active_positions_count|0|0|0|0|
|analysis_timestamp|0|0|0|0|
|annual_turnover_rate|117|117|117|117|
|avg_career_development_score|0|0|0|0|
|avg_employee_age|0|0|0|0|
|avg_employee_performance_score|0|0|0|0|
|avg_former_tenure_years|5|5|5|5|
|avg_retention_stability_score|0|0|0|0|
|current_active_employees|0|0|0|0|
|data_quality_flag|0|0|0|0|
|departures_last_year|0|0|0|0|
|development_required_employees|0|0|0|0|
|director_role_employees|0|0|0|0|
|entry_level_employees|0|0|0|0|
|ethnic_diversity_count|0|0|0|0|
|executive_level_employees|0|0|0|0|
|experienced_employees|0|0|0|0|
|fast_track_employees_count|0|0|0|0|
|former_employees|0|0|0|0|
|high_achievers_count|0|0|0|0|
|high_risk_employees|0|0|0|0|
|high_value_flight_risk_employees|0|0|0|0|
|high_value_stable_employees|0|0|0|0|
|junior_employees|0|0|0|0|
|last_activity_date|0|0|0|0|
|last_departure_date|0|0|0|0|
|lead_role_employees|0|0|0|0|
|low_risk_employees|0|0|0|0|
|management_ratio|117|117|117|117|
|management_recommendation|0|0|0|0|
|management_role_employees|0|0|0|0|
|medium_risk_employees|0|0|0|0|
|mid_level_employees|0|0|0|0|
|military_veterans_count|0|0|0|0|
|new_assignments_last_year|0|0|0|0|
|new_hire_employees|0|0|0|0|
|organization_age_days|0|0|0|0|
|organization_age_years|0|0|0|0|
|organization_code|0|0|0|0|
|organization_created_date|0|0|0|0|
|organization_health_score|117|117|117|117|
|organization_maturity_level|0|0|0|0|
|organization_name|0|0|0|0|
|organization_size_category|117|117|117|117|
|organization_sub_type|0|0|0|0|
|organization_type|0|0|0|0|
|organizational_level|0|0|0|0|
|performance_category|0|0|0|0|
|position_fill_rate|0|0|0|0|
|senior_employees|0|0|0|0|
|senior_level_employees|0|0|0|0|
|stable_development_employees|0|0|0|0|
|staffing_model|0|0|0|0|
|total_employees_ever|0|0|0|0|
|total_positions|0|0|0|0|
|total_promotions_in_organization|0|0|0|0|
|unique_organization_roles|106|106|106|106|
|veteran_employees|0|0|0|0|
|visibility|0|0|0|0|

### 重跑 size_labels

SQL：`data/016_work/impl-016/size_labels.sql`；SHA-256：`982a6980fcacbf93d69836d3ca07c9028e753e84a3130b6ee8350712b2fbf6a0`。

唯一原文位置offset=10123，替换前：
```sql
THEN 'Empty' WHEN current_active_employees<=5 THEN 'Micro' WHEN current_active_employees<=15 THEN 'Small' WHEN current_active_employees<=50 THEN 'Medium' WHEN current_active_employees<=200 THEN 'Large' ELSE 'Enterprise'
```
替换后：
```sql
THEN 'Empty Organization' WHEN current_active_employees<=5 THEN 'Micro Team' WHEN current_active_employees<=15 THEN 'Small Team' WHEN current_active_employees<=50 THEN 'Medium Team' WHEN current_active_employees<=200 THEN 'Large Team' ELSE 'Enterprise Unit'
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|117|117|0|0|0/0|117|117|579|False|
|L1|117|117|0|0|0/0|117|117|579|False|
|L2|117|117|0|0|0/0|117|117|579|False|
|L3|117|117|0|0|0/0|117|117|579|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|organization_id|0|0|0|0|
|access_level|0|0|0|0|
|active_positions_count|0|0|0|0|
|analysis_timestamp|0|0|0|0|
|annual_turnover_rate|117|117|117|117|
|avg_career_development_score|0|0|0|0|
|avg_employee_age|0|0|0|0|
|avg_employee_performance_score|0|0|0|0|
|avg_former_tenure_years|5|5|5|5|
|avg_retention_stability_score|0|0|0|0|
|current_active_employees|0|0|0|0|
|data_quality_flag|0|0|0|0|
|departures_last_year|0|0|0|0|
|development_required_employees|0|0|0|0|
|director_role_employees|0|0|0|0|
|entry_level_employees|0|0|0|0|
|ethnic_diversity_count|0|0|0|0|
|executive_level_employees|0|0|0|0|
|experienced_employees|0|0|0|0|
|fast_track_employees_count|0|0|0|0|
|former_employees|0|0|0|0|
|high_achievers_count|0|0|0|0|
|high_risk_employees|0|0|0|0|
|high_value_flight_risk_employees|0|0|0|0|
|high_value_stable_employees|0|0|0|0|
|junior_employees|0|0|0|0|
|last_activity_date|0|0|0|0|
|last_departure_date|0|0|0|0|
|lead_role_employees|0|0|0|0|
|low_risk_employees|0|0|0|0|
|management_ratio|117|117|117|117|
|management_recommendation|0|0|0|0|
|management_role_employees|0|0|0|0|
|medium_risk_employees|0|0|0|0|
|mid_level_employees|0|0|0|0|
|military_veterans_count|0|0|0|0|
|new_assignments_last_year|0|0|0|0|
|new_hire_employees|0|0|0|0|
|organization_age_days|0|0|0|0|
|organization_age_years|0|0|0|0|
|organization_code|0|0|0|0|
|organization_created_date|0|0|0|0|
|organization_health_score|117|117|117|117|
|organization_maturity_level|117|117|117|117|
|organization_name|0|0|0|0|
|organization_size_category|0|0|0|0|
|organization_sub_type|0|0|0|0|
|organization_type|0|0|0|0|
|organizational_level|0|0|0|0|
|performance_category|0|0|0|0|
|position_fill_rate|0|0|0|0|
|senior_employees|0|0|0|0|
|senior_level_employees|0|0|0|0|
|stable_development_employees|0|0|0|0|
|staffing_model|0|0|0|0|
|total_employees_ever|0|0|0|0|
|total_positions|0|0|0|0|
|total_promotions_in_organization|0|0|0|0|
|unique_organization_roles|106|106|106|106|
|veteran_employees|0|0|0|0|
|visibility|0|0|0|0|

### 重跑 roles_relationship

SQL：`data/016_work/impl-016/roles_relationship.sql`；SHA-256：`4f31f78bd5f17e80f71e5487908b5dd589adb633eb80183ff04be876e9d9a7b8`。

唯一原文位置offset=1348，替换前：
```sql
 SELECT ow.organization_id,'workday' source_relation,count(DISTINCT r.organization_role_id) unique_organization_roles,count(DISTINCT ow.organization_worker_code) FILTER(WHERE r.organization_role_code ILIKE '%Manager%') management_role_employees,count(DISTINCT ow.organization_worker_code) FILTER(WHERE r.organization_role_code ILIKE '%Director%') director_role_employees,count(DISTINCT ow.organization_worker_code) FILTER(WHERE r.organization_role_code ILIKE '%Lead%') lead_role_employees FROM staging.stg_workday__organization_role_worker ow LEFT JOIN staging.stg_workday__organization_role r ON ow.organization_id=r.organization_id AND ow.role_id=r.organization_role_id GROUP BY ow.organization_id

```
替换后：
```sql
 SELECT wpo.organization_id,wpo.source_relation,count(DISTINCT ow.role_id) unique_organization_roles,count(DISTINCT wpo.worker_id) FILTER(WHERE r.organization_role_code LIKE '%Manager%') management_role_employees,count(DISTINCT wpo.worker_id) FILTER(WHERE r.organization_role_code LIKE '%Director%') director_role_employees,count(DISTINCT wpo.worker_id) FILTER(WHERE r.organization_role_code LIKE '%Lead%') lead_role_employees FROM staging.stg_workday__worker_position_organization wpo LEFT JOIN staging.stg_workday__organization_role_worker ow ON wpo.worker_id=ow.organization_worker_code AND wpo.source_relation=ow.source_relation LEFT JOIN staging.stg_workday__organization_role r ON ow.role_id=r.organization_role_id AND ow.source_relation=r.source_relation AND wpo.organization_id=r.organization_id GROUP BY wpo.organization_id,wpo.source_relation

```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|117|117|0|0|0/0|117|117|590|False|
|L1|117|117|0|0|0/0|117|117|590|False|
|L2|117|117|0|0|0/0|117|117|590|False|
|L3|117|117|0|0|0/0|117|117|590|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|organization_id|0|0|0|0|
|access_level|0|0|0|0|
|active_positions_count|0|0|0|0|
|analysis_timestamp|0|0|0|0|
|annual_turnover_rate|117|117|117|117|
|avg_career_development_score|0|0|0|0|
|avg_employee_age|0|0|0|0|
|avg_employee_performance_score|0|0|0|0|
|avg_former_tenure_years|5|5|5|5|
|avg_retention_stability_score|0|0|0|0|
|current_active_employees|0|0|0|0|
|data_quality_flag|0|0|0|0|
|departures_last_year|0|0|0|0|
|development_required_employees|0|0|0|0|
|director_role_employees|0|0|0|0|
|entry_level_employees|0|0|0|0|
|ethnic_diversity_count|0|0|0|0|
|executive_level_employees|0|0|0|0|
|experienced_employees|0|0|0|0|
|fast_track_employees_count|0|0|0|0|
|former_employees|0|0|0|0|
|high_achievers_count|0|0|0|0|
|high_risk_employees|0|0|0|0|
|high_value_flight_risk_employees|0|0|0|0|
|high_value_stable_employees|0|0|0|0|
|junior_employees|0|0|0|0|
|last_activity_date|0|0|0|0|
|last_departure_date|0|0|0|0|
|lead_role_employees|0|0|0|0|
|low_risk_employees|0|0|0|0|
|management_ratio|117|117|117|117|
|management_recommendation|0|0|0|0|
|management_role_employees|0|0|0|0|
|medium_risk_employees|0|0|0|0|
|mid_level_employees|0|0|0|0|
|military_veterans_count|0|0|0|0|
|new_assignments_last_year|0|0|0|0|
|new_hire_employees|0|0|0|0|
|organization_age_days|0|0|0|0|
|organization_age_years|0|0|0|0|
|organization_code|0|0|0|0|
|organization_created_date|0|0|0|0|
|organization_health_score|117|117|117|117|
|organization_maturity_level|117|117|117|117|
|organization_name|0|0|0|0|
|organization_size_category|117|117|117|117|
|organization_sub_type|0|0|0|0|
|organization_type|0|0|0|0|
|organizational_level|0|0|0|0|
|performance_category|0|0|0|0|
|position_fill_rate|0|0|0|0|
|senior_employees|0|0|0|0|
|senior_level_employees|0|0|0|0|
|stable_development_employees|0|0|0|0|
|staffing_model|0|0|0|0|
|total_employees_ever|0|0|0|0|
|total_positions|0|0|0|0|
|total_promotions_in_organization|0|0|0|0|
|unique_organization_roles|0|0|0|0|
|veteran_employees|0|0|0|0|
|visibility|0|0|0|0|

### 重跑 tenure_join_weight

SQL：`data/016_work/impl-016/tenure_join_weight.sql`；SHA-256：`fc3a1fa5e5e2304f39bdd0fbeeaf84cb81020fc697ead0b1221678fc77bcd299`。

唯一原文位置offset=103，替换前：
```sql
 SELECT worker_id,organization_id,source_relation,position_id,effective_start,effective_end,
 date_diff('day',effective_start,coalesce(effective_end,DATE '2025-10-13')) duration,
 CASE WHEN effective_end IS NULL THEN 'Active Assignment' ELSE 'Former Assignment' END status
 FROM staging.stg_workday__worker_position_organization

```
替换后：
```sql
 SELECT wpo.worker_id,wpo.organization_id,wpo.source_relation,wpo.position_id,wpo.effective_start,wpo.effective_end,
 date_diff('day',effective_start,coalesce(effective_end,DATE '2025-10-13')) duration,
 CASE WHEN effective_end IS NULL THEN 'Active Assignment' ELSE 'Former Assignment' END status
 FROM staging.stg_workday__worker_position_organization wpo LEFT JOIN staging.stg_workday__organization_role_worker ow ON wpo.worker_id=ow.organization_worker_code AND wpo.source_relation=ow.source_relation LEFT JOIN staging.stg_workday__organization_role r ON ow.role_id=r.organization_role_id AND ow.source_relation=r.source_relation AND wpo.organization_id=r.organization_id

```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|117|117|0|0|0/0|117|117|691|False|
|L1|117|117|0|0|0/0|117|117|691|False|
|L2|117|117|0|0|0/0|117|117|691|False|
|L3|117|117|0|0|0/0|117|117|691|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|organization_id|0|0|0|0|
|access_level|0|0|0|0|
|active_positions_count|0|0|0|0|
|analysis_timestamp|0|0|0|0|
|annual_turnover_rate|117|117|117|117|
|avg_career_development_score|0|0|0|0|
|avg_employee_age|0|0|0|0|
|avg_employee_performance_score|0|0|0|0|
|avg_former_tenure_years|0|0|0|0|
|avg_retention_stability_score|0|0|0|0|
|current_active_employees|0|0|0|0|
|data_quality_flag|0|0|0|0|
|departures_last_year|0|0|0|0|
|development_required_employees|0|0|0|0|
|director_role_employees|0|0|0|0|
|entry_level_employees|0|0|0|0|
|ethnic_diversity_count|0|0|0|0|
|executive_level_employees|0|0|0|0|
|experienced_employees|0|0|0|0|
|fast_track_employees_count|0|0|0|0|
|former_employees|0|0|0|0|
|high_achievers_count|0|0|0|0|
|high_risk_employees|0|0|0|0|
|high_value_flight_risk_employees|0|0|0|0|
|high_value_stable_employees|0|0|0|0|
|junior_employees|0|0|0|0|
|last_activity_date|0|0|0|0|
|last_departure_date|0|0|0|0|
|lead_role_employees|0|0|0|0|
|low_risk_employees|0|0|0|0|
|management_ratio|117|117|117|117|
|management_recommendation|0|0|0|0|
|management_role_employees|0|0|0|0|
|medium_risk_employees|0|0|0|0|
|mid_level_employees|0|0|0|0|
|military_veterans_count|0|0|0|0|
|new_assignments_last_year|0|0|0|0|
|new_hire_employees|0|0|0|0|
|organization_age_days|0|0|0|0|
|organization_age_years|0|0|0|0|
|organization_code|0|0|0|0|
|organization_created_date|0|0|0|0|
|organization_health_score|117|117|117|117|
|organization_maturity_level|117|117|117|117|
|organization_name|0|0|0|0|
|organization_size_category|117|117|117|117|
|organization_sub_type|0|0|0|0|
|organization_type|0|0|0|0|
|organizational_level|0|0|0|0|
|performance_category|0|0|0|0|
|position_fill_rate|0|0|0|0|
|senior_employees|0|0|0|0|
|senior_level_employees|0|0|0|0|
|stable_development_employees|0|0|0|0|
|staffing_model|0|0|0|0|
|total_employees_ever|0|0|0|0|
|total_positions|0|0|0|0|
|total_promotions_in_organization|0|0|0|0|
|unique_organization_roles|106|106|106|106|
|veteran_employees|0|0|0|0|
|visibility|0|0|0|0|

### 重跑 health_turnover_rule

SQL：`data/016_work/impl-016/health_turnover_rule.sql`；SHA-256：`d586d0eba400b15076eccadb89f0d15fc12d59999c71471b1b9146fe0233098d`。

唯一原文位置offset=9292，替换前：
```sql
CASE WHEN departures_last_year=0 THEN 25 WHEN annual_turnover_rate<=10 THEN 25 WHEN annual_turnover_rate<=20 THEN 20 WHEN annual_turnover_rate<=30 THEN 15 WHEN annual_turnover_rate<=40 THEN 10 ELSE 5 END
```
替换后：
```sql
CASE WHEN coalesce(departures_last_year,0)=0 AND coalesce(current_active_employees,0)>0 THEN 25 WHEN annual_turnover_rate<=10 THEN 20 WHEN annual_turnover_rate<=20 THEN 15 WHEN annual_turnover_rate<=30 THEN 10 ELSE 5 END
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|117|117|0|0|0/0|117|117|696|False|
|L1|117|117|0|0|0/0|117|117|696|False|
|L2|117|117|0|0|0/0|117|117|696|False|
|L3|117|117|0|0|0/0|117|117|696|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|organization_id|0|0|0|0|
|access_level|0|0|0|0|
|active_positions_count|0|0|0|0|
|analysis_timestamp|0|0|0|0|
|annual_turnover_rate|117|117|117|117|
|avg_career_development_score|0|0|0|0|
|avg_employee_age|0|0|0|0|
|avg_employee_performance_score|0|0|0|0|
|avg_former_tenure_years|5|5|5|5|
|avg_retention_stability_score|0|0|0|0|
|current_active_employees|0|0|0|0|
|data_quality_flag|0|0|0|0|
|departures_last_year|0|0|0|0|
|development_required_employees|0|0|0|0|
|director_role_employees|0|0|0|0|
|entry_level_employees|0|0|0|0|
|ethnic_diversity_count|0|0|0|0|
|executive_level_employees|0|0|0|0|
|experienced_employees|0|0|0|0|
|fast_track_employees_count|0|0|0|0|
|former_employees|0|0|0|0|
|high_achievers_count|0|0|0|0|
|high_risk_employees|0|0|0|0|
|high_value_flight_risk_employees|0|0|0|0|
|high_value_stable_employees|0|0|0|0|
|junior_employees|0|0|0|0|
|last_activity_date|0|0|0|0|
|last_departure_date|0|0|0|0|
|lead_role_employees|0|0|0|0|
|low_risk_employees|0|0|0|0|
|management_ratio|117|117|117|117|
|management_recommendation|0|0|0|0|
|management_role_employees|0|0|0|0|
|medium_risk_employees|0|0|0|0|
|mid_level_employees|0|0|0|0|
|military_veterans_count|0|0|0|0|
|new_assignments_last_year|0|0|0|0|
|new_hire_employees|0|0|0|0|
|organization_age_days|0|0|0|0|
|organization_age_years|0|0|0|0|
|organization_code|0|0|0|0|
|organization_created_date|0|0|0|0|
|organization_health_score|117|117|117|117|
|organization_maturity_level|117|117|117|117|
|organization_name|0|0|0|0|
|organization_size_category|117|117|117|117|
|organization_sub_type|0|0|0|0|
|organization_type|0|0|0|0|
|organizational_level|0|0|0|0|
|performance_category|0|0|0|0|
|position_fill_rate|0|0|0|0|
|senior_employees|0|0|0|0|
|senior_level_employees|0|0|0|0|
|stable_development_employees|0|0|0|0|
|staffing_model|0|0|0|0|
|total_employees_ever|0|0|0|0|
|total_positions|0|0|0|0|
|total_promotions_in_organization|0|0|0|0|
|unique_organization_roles|106|106|106|106|
|veteran_employees|0|0|0|0|
|visibility|0|0|0|0|

### 重跑 health_risk_rule

SQL：`data/016_work/impl-016/health_risk_rule.sql`；SHA-256：`9389f4786dbeeb09650bc32852b298bf9457a37578fafa688ce91b6f5f41811e`。

唯一原文位置offset=9673，替换前：
```sql
CASE WHEN high_risk_employee_percentage<=10 THEN 10 WHEN high_risk_employee_percentage<=20 THEN 7 WHEN high_risk_employee_percentage<=30 THEN 4 ELSE 2 END
```
替换后：
```sql
CASE WHEN high_risk_employee_percentage<=5 THEN 10 WHEN high_risk_employee_percentage<=15 THEN 7 WHEN high_risk_employee_percentage<=25 THEN 4 ELSE 2 END
```

|档位|agent行|gold行|仅agent键行|仅gold键行|共同键多出A/G|共同键不同配对行|行规模|格子规模|含键整表匹配|
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
|L0|117|117|0|0|0/0|117|117|696|False|
|L1|117|117|0|0|0/0|117|117|696|False|
|L2|117|117|0|0|0/0|117|117|696|False|
|L3|117|117|0|0|0/0|117|117|696|False|

整表首次匹配档位：**L0–L3均不匹配**。

|共同键比较列|L0不同格|L1|L2|L3|
|---|---:|---:|---:|---:|
|organization_id|0|0|0|0|
|access_level|0|0|0|0|
|active_positions_count|0|0|0|0|
|analysis_timestamp|0|0|0|0|
|annual_turnover_rate|117|117|117|117|
|avg_career_development_score|0|0|0|0|
|avg_employee_age|0|0|0|0|
|avg_employee_performance_score|0|0|0|0|
|avg_former_tenure_years|5|5|5|5|
|avg_retention_stability_score|0|0|0|0|
|current_active_employees|0|0|0|0|
|data_quality_flag|0|0|0|0|
|departures_last_year|0|0|0|0|
|development_required_employees|0|0|0|0|
|director_role_employees|0|0|0|0|
|entry_level_employees|0|0|0|0|
|ethnic_diversity_count|0|0|0|0|
|executive_level_employees|0|0|0|0|
|experienced_employees|0|0|0|0|
|fast_track_employees_count|0|0|0|0|
|former_employees|0|0|0|0|
|high_achievers_count|0|0|0|0|
|high_risk_employees|0|0|0|0|
|high_value_flight_risk_employees|0|0|0|0|
|high_value_stable_employees|0|0|0|0|
|junior_employees|0|0|0|0|
|last_activity_date|0|0|0|0|
|last_departure_date|0|0|0|0|
|lead_role_employees|0|0|0|0|
|low_risk_employees|0|0|0|0|
|management_ratio|117|117|117|117|
|management_recommendation|0|0|0|0|
|management_role_employees|0|0|0|0|
|medium_risk_employees|0|0|0|0|
|mid_level_employees|0|0|0|0|
|military_veterans_count|0|0|0|0|
|new_assignments_last_year|0|0|0|0|
|new_hire_employees|0|0|0|0|
|organization_age_days|0|0|0|0|
|organization_age_years|0|0|0|0|
|organization_code|0|0|0|0|
|organization_created_date|0|0|0|0|
|organization_health_score|117|117|117|117|
|organization_maturity_level|117|117|117|117|
|organization_name|0|0|0|0|
|organization_size_category|117|117|117|117|
|organization_sub_type|0|0|0|0|
|organization_type|0|0|0|0|
|organizational_level|0|0|0|0|
|performance_category|0|0|0|0|
|position_fill_rate|0|0|0|0|
|senior_employees|0|0|0|0|
|senior_level_employees|0|0|0|0|
|stable_development_employees|0|0|0|0|
|staffing_model|0|0|0|0|
|total_employees_ever|0|0|0|0|
|total_positions|0|0|0|0|
|total_promotions_in_organization|0|0|0|0|
|unique_organization_roles|106|106|106|106|
|veteran_employees|0|0|0|0|
|visibility|0|0|0|0|

## 5. 逐项类别及U门槛

表级主要原因：**多因并列（C、O）**。

|并列项/主项|类别|单改L0行：前→后|单改L0格：前→后|首次整表匹配|
|---|---|---|---|---|
|annual_zero|C|117→117|696→579|无|
|management_zero|C|117→117|696→579|无|
|maturity_labels|O|117→117|696→579|无|
|size_labels|O|117→117|696→579|无|

重跑是否满足U第4条件：**否：最大单项减少117/696格，不达一半**。

比率补0及连接方式有直接契约规定，归C；枚举标签是契约/gold冲突，归O。raw变化的操作来源无法判定，但不影响本节点CS对照。

主要原因按同一L0尺度先行后格；参与因素沿用该表选定尺度。第5节放宽只用于并列U，第4节放宽只用于U参与因素，不将“满足数值门槛”单独当作U证据。

## 6. 版本对比

原因类别及参与因素不变。上一版未设不确定性字段，本次按v2第6节逐项新增。

与014相比的历史对比沿用原字段：不适用：第二批首次标注。此字段不代替本次与016/017的对比。

## 规则问题

v2保留两个C与两个O并列；不把有关另一张organization_performance空表的说明升级为本表比率/枚举说明。gold=初始≠agent照常标注；raw邮箱缩减步骤仍未找到，CS节点归因不补猜。

v2已冻结：不修改类别定义。保留的操作边界为同表尺度一致、重复键固定完整元组配对、以L0贡献选主因；如将来改变会影响标注的定义，应按手册重标，不能当作不影响结果的操作性补充。
