# impl-016 / workday__organization_overview

## basic_information

```json
{
  "task": "impl-016",
  "layer": "marts",
  "table": "workday__organization_overview",
  "status": "待标注",
  "difference_source": {
    "kind": "date_aligned_011",
    "record": "records/011_table_alignment.jsonl",
    "detail_record": "records/011_alignment_impl-016.json",
    "candidate_date": "2025-10-13",
    "selection_reason": "011 执行与比较成功，使用该表已验证日期；优先 010 同题候选 / 共同兼容日，再按日期升序"
  },
  "status_record": "records/012_statuses.jsonl",
  "package_scope": "仅原文和机械统计；未概括轨迹、未推测原因"
}
```

## contract_specification

```json
{
  "source_path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
  "source_sha256": "8f0707fc595c6f2f1e46a1983436959278e10315cb723e975c2811858d737c91",
  "parse_mode": "strict",
  "requested_table": "workday__organization_overview",
  "status": "found"
}
```
```json
{
  "yaml_path": [
    "modeling_spec",
    "marts_models",
    4
  ],
  "start_line": 2024,
  "end_line": 2230
}
```
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

## agent_final_SQL

```json
{
  "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
  "sha256": "b59173eeea3ae826802f8b6de9e99a323a7fbc82ab691ec5c31009dc9b51a552",
  "start_line": 1,
  "end_line": 39
}
```
```sql
WITH active_org AS (SELECT * FROM staging.stg_workday__organization WHERE is_inactive=FALSE), rel AS (
 SELECT worker_id,organization_id,source_relation,position_id,effective_start,effective_end,
 date_diff('day',effective_start,coalesce(effective_end,current_date)) duration,
 CASE WHEN effective_end IS NULL THEN 'Active Assignment' ELSE 'Former Assignment' END status
 FROM staging.stg_workday__worker_position_organization
), stats AS (
 SELECT organization_id,source_relation,count(DISTINCT worker_id) total_employees_ever,count(DISTINCT worker_id) FILTER(WHERE effective_end IS NULL) current_active_employees,count(DISTINCT worker_id) FILTER(WHERE effective_end IS NOT NULL) former_employees,count(DISTINCT position_id) total_positions,count(DISTINCT position_id) FILTER(WHERE effective_end IS NULL) active_positions_count,
 count(DISTINCT worker_id) FILTER(WHERE effective_start>=current_date-INTERVAL '1 year') new_assignments_last_year,count(DISTINCT worker_id) FILTER(WHERE effective_end>=current_date-INTERVAL '1 year') departures_last_year,avg(duration) FILTER(WHERE effective_end IS NULL) avg_current_days,avg(duration) FILTER(WHERE effective_end IS NOT NULL) avg_former_days,max(effective_start) last_activity_date,max(effective_end) last_departure_date
 FROM rel GROUP BY organization_id,source_relation
), roles AS (
 SELECT ow.organization_id,'workday' source_relation,count(DISTINCT r.organization_role_id) unique_organization_roles,count(DISTINCT ow.organization_worker_code) FILTER(WHERE r.organization_role_code ILIKE '%Manager%') management_role_employees,count(DISTINCT ow.organization_worker_code) FILTER(WHERE r.organization_role_code ILIKE '%Director%') director_role_employees,count(DISTINCT ow.organization_worker_code) FILTER(WHERE r.organization_role_code ILIKE '%Lead%') lead_role_employees FROM staging.stg_workday__organization_role_worker ow LEFT JOIN staging.stg_workday__organization_role r ON ow.organization_id=r.organization_id AND ow.role_id=r.organization_role_id GROUP BY ow.organization_id
), perf AS (
 SELECT organization_id,source_relation,avg(overall_employee_score) FILTER(WHERE is_employed) avg_employee_performance_score,avg(career_development_score) FILTER(WHERE is_employed) avg_career_development_score,avg(retention_stability_score) FILTER(WHERE is_employed) avg_retention_stability_score,
 count(DISTINCT worker_id) FILTER(WHERE employee_value_segment='High Value - High Retention') high_value_stable_employees,count(DISTINCT worker_id) FILTER(WHERE employee_value_segment='High Value - Flight Risk') high_value_flight_risk_employees,count(DISTINCT worker_id) FILTER(WHERE employee_value_segment='Stable - Development Needed') stable_development_employees,count(DISTINCT worker_id) FILTER(WHERE employee_value_segment='Development Required') development_required_employees,
 count(DISTINCT worker_id) FILTER(WHERE employee_risk_level='High Risk') high_risk_employees,count(DISTINCT worker_id) FILTER(WHERE employee_risk_level='Medium Risk') medium_risk_employees,count(DISTINCT worker_id) FILTER(WHERE employee_risk_level='Low Risk') low_risk_employees,
 count(DISTINCT worker_id) FILTER(WHERE is_employed AND employee_maturity_segment LIKE '%New Hire%') new_hire_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND employee_maturity_segment LIKE '%Junior%') junior_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND employee_maturity_segment LIKE '%Experienced%') experienced_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND employee_maturity_segment LIKE '%Senior%') senior_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND employee_maturity_segment LIKE '%Veteran%') veteran_employees,
 count(DISTINCT ethnicity_codes) FILTER(WHERE is_employed AND ethnicity_codes IS NOT NULL) ethnic_diversity_count,count(DISTINCT worker_id) FILTER(WHERE is_employed AND is_military_service) military_veterans_count,avg(age) FILTER(WHERE is_employed) avg_employee_age,
 count(DISTINCT worker_id) FILTER(WHERE is_employed AND compensation_tier='Entry Level') entry_level_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND compensation_tier='Mid Level') mid_level_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND compensation_tier='Senior Level') senior_level_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND compensation_tier='Executive Level') executive_level_employees,
 sum(total_promotions) FILTER(WHERE is_employed) total_promotions_in_organization,count(DISTINCT worker_id) FILTER(WHERE is_employed AND total_promotions>=2) high_achievers_count,count(DISTINCT worker_id) FILTER(WHERE is_employed AND fast_promotions>0) fast_track_employees_count
 FROM mart.workday__employee_overview WHERE organization_id<>'Unknown' GROUP BY organization_id,source_relation
), joined AS (SELECT o.*,s.*,r.unique_organization_roles,r.management_role_employees,r.director_role_employees,r.lead_role_employees,p.* EXCLUDE(organization_id,source_relation) FROM active_org o LEFT JOIN stats s USING(organization_id,source_relation) LEFT JOIN roles r USING(organization_id,source_relation) LEFT JOIN perf p USING(organization_id,source_relation))
SELECT organization_id,source_relation,organization_name,organization_code,organization_type,organization_sub_type,staffing_model,visibility,
CASE visibility WHEN 'Public' THEN 'Open Access' WHEN 'Private' THEN 'Restricted Access' ELSE 'Unknown Access' END access_level,effective_start organization_created_date,date_diff('day',effective_start,current_date)::BIGINT organization_age_days,round(date_diff('day',effective_start,current_date)/365.0,2)::DOUBLE organization_age_years,
CASE WHEN date_diff('day',effective_start,current_date)<365 THEN 'New' WHEN date_diff('day',effective_start,current_date)<1095 THEN 'Young' WHEN date_diff('day',effective_start,current_date)<3650 THEN 'Mature' ELSE 'Legacy' END organization_maturity_level,
CASE organization_type WHEN 'Company' THEN 'Corporate Level' WHEN 'Division' THEN 'Division Level' WHEN 'Department' THEN 'Department Level' WHEN 'Team' THEN 'Team Level' ELSE 'Other Level' END organizational_level,
coalesce(total_employees_ever,0)::BIGINT total_employees_ever,coalesce(current_active_employees,0)::BIGINT current_active_employees,coalesce(former_employees,0)::BIGINT former_employees,coalesce(total_positions,0)::BIGINT total_positions,coalesce(active_positions_count,0)::BIGINT active_positions_count,
round(coalesce(current_active_employees,0)*100.0/NULLIF(total_positions,0),2)::DOUBLE position_fill_rate,coalesce(new_assignments_last_year,0)::BIGINT new_assignments_last_year,coalesce(departures_last_year,0)::BIGINT departures_last_year,round(coalesce(departures_last_year,0)*100.0/NULLIF(current_active_employees,0),2)::DOUBLE annual_turnover_rate,
round(coalesce(avg_current_days,0)/365.0,2)::DOUBLE avg_current_tenure_years,round(coalesce(avg_former_days,0)/365.0,2)::DOUBLE avg_former_tenure_years,coalesce(unique_organization_roles,0)::BIGINT unique_organization_roles,coalesce(management_role_employees,0)::BIGINT management_role_employees,coalesce(director_role_employees,0)::BIGINT director_role_employees,coalesce(lead_role_employees,0)::BIGINT lead_role_employees,
round((coalesce(management_role_employees,0)+coalesce(director_role_employees,0))*100.0/NULLIF(current_active_employees,0),2)::DOUBLE management_ratio,coalesce(avg_employee_performance_score,0)::DOUBLE avg_employee_performance_score,coalesce(avg_career_development_score,0)::DOUBLE avg_career_development_score,coalesce(avg_retention_stability_score,0)::DOUBLE avg_retention_stability_score,
coalesce(high_value_stable_employees,0)::BIGINT high_value_stable_employees,coalesce(high_value_flight_risk_employees,0)::BIGINT high_value_flight_risk_employees,coalesce(stable_development_employees,0)::BIGINT stable_development_employees,coalesce(development_required_employees,0)::BIGINT development_required_employees,coalesce(high_risk_employees,0)::BIGINT high_risk_employees,coalesce(medium_risk_employees,0)::BIGINT medium_risk_employees,coalesce(low_risk_employees,0)::BIGINT low_risk_employees,
round(coalesce(high_risk_employees,0)*100.0/NULLIF(current_active_employees,0),2)::DOUBLE high_risk_employee_percentage,coalesce(new_hire_employees,0)::BIGINT new_hire_employees,coalesce(junior_employees,0)::BIGINT junior_employees,coalesce(experienced_employees,0)::BIGINT experienced_employees,coalesce(senior_employees,0)::BIGINT senior_employees,coalesce(veteran_employees,0)::BIGINT veteran_employees,coalesce(ethnic_diversity_count,0)::BIGINT ethnic_diversity_count,coalesce(military_veterans_count,0)::BIGINT military_veterans_count,coalesce(avg_employee_age,0)::DOUBLE avg_employee_age,
coalesce(entry_level_employees,0)::BIGINT entry_level_employees,coalesce(mid_level_employees,0)::BIGINT mid_level_employees,coalesce(senior_level_employees,0)::BIGINT senior_level_employees,coalesce(executive_level_employees,0)::BIGINT executive_level_employees,coalesce(total_promotions_in_organization,0)::HUGEINT total_promotions_in_organization,coalesce(high_achievers_count,0)::BIGINT high_achievers_count,coalesce(fast_track_employees_count,0)::BIGINT fast_track_employees_count,
round(least(30,coalesce(avg_employee_performance_score,0)*.3)+CASE WHEN departures_last_year=0 THEN 25 WHEN annual_turnover_rate<=10 THEN 25 WHEN annual_turnover_rate<=20 THEN 20 WHEN annual_turnover_rate<=30 THEN 15 WHEN annual_turnover_rate<=40 THEN 10 ELSE 5 END+least(20,coalesce(avg_career_development_score,0)*.2)+CASE WHEN position_fill_rate>=90 THEN 15 WHEN position_fill_rate>=75 THEN 12 WHEN position_fill_rate>=60 THEN 9 ELSE 6 END+CASE WHEN high_risk_employee_percentage<=10 THEN 10 WHEN high_risk_employee_percentage<=20 THEN 7 WHEN high_risk_employee_percentage<=30 THEN 4 ELSE 2 END,2)::DOUBLE organization_health_score,
CASE WHEN avg_employee_performance_score>=80 THEN 'Excellent' WHEN avg_employee_performance_score>=60 THEN 'Good' WHEN avg_employee_performance_score>=40 THEN 'Average' ELSE 'Needs Improvement' END performance_category,
CASE WHEN current_active_employees=0 THEN 'Empty' WHEN current_active_employees<=5 THEN 'Micro' WHEN current_active_employees<=15 THEN 'Small' WHEN current_active_employees<=50 THEN 'Medium' WHEN current_active_employees<=200 THEN 'Large' ELSE 'Enterprise' END organization_size_category,
coalesce(last_activity_date,effective_start) last_activity_date,coalesce(last_departure_date,DATE '1900-01-01') last_departure_date,
CASE WHEN current_active_employees=0 THEN 'Review Organization Necessity' WHEN annual_turnover_rate>30 THEN 'Focus on Retention' WHEN high_risk_employee_percentage>25 THEN 'Address Employee Risk' WHEN position_fill_rate<70 THEN 'Improve Staffing' WHEN avg_employee_performance_score<50 THEN 'Enhance Performance Management' WHEN management_ratio>40 THEN 'Optimize Structure' ELSE 'Maintain Excellence' END management_recommendation,
CASE WHEN organization_name IS NULL OR trim(organization_name)='' THEN 'ERROR: Missing organization name' WHEN current_active_employees>total_positions+10 THEN 'WARNING: Employees exceed positions' WHEN annual_turnover_rate>100 THEN 'WARNING: Turnover exceeds 100%' WHEN organization_age_days<0 THEN 'ERROR: Negative organization age' ELSE 'VALID' END data_quality_flag,current_timestamp::TIMESTAMPTZ analysis_timestamp
FROM joined
```

## gold_SQL_仅供定位差异

```json
{
  "path": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
  "sha256": "9136e4c5f8b13dee3c505ecfa78716722fea6b404d492a942905c25777d64526",
  "start_line": 1,
  "end_line": 369
}
```
```sql
-- Organizational structure and relationship overview data mart - provides a comprehensive view of organizational hierarchy, role assignments, and employee distribution
-- Support organizational structure analysis, management level optimization, and cross-department collaboration analysis

with organization_base as (
    select * 
    from staging.stg_workday__organization
    where not is_inactive  -- Only include active organizations
),

-- Organizational roles and employee relations
organization_employee_relationships as (
    select 
        wpo.organization_id,
        wpo.source_relation,
        wpo.worker_id,
        wpo.position_id,
        wpo.effective_start as assignment_start_date,
        wpo.effective_end as assignment_end_date,
        
        -- current allocation status
        case when wpo.effective_end is null then 'Active Assignment' else 'Former Assignment' end as assignment_status,
        
        -- Assign duration
        case 
            when wpo.effective_end is not null then 
                date_diff('day', wpo.effective_start, wpo.effective_end)
            else 
                date_diff('day', wpo.effective_start, current_date)
        end as assignment_duration_days,
        
        -- Organization role information  
        orw.role_id as organization_role_id,
        org_role.organization_role_code
        
    from staging.stg_workday__worker_position_organization wpo
    left join staging.stg_workday__organization_role_worker orw
        on wpo.worker_id = orw.organization_worker_code
        and wpo.source_relation = orw.source_relation
    left join staging.stg_workday__organization_role org_role
        on orw.role_id = org_role.organization_role_id
        and orw.source_relation = org_role.source_relation
        and wpo.organization_id = org_role.organization_id
),

-- Organizational employee statistics and performance summary
organization_employee_stats as (
    select 
        oer.organization_id,
        oer.source_relation,
        
        -- Basic employee statistics
        count(distinct oer.worker_id) as total_employees_ever,
        count(distinct case when oer.assignment_status = 'Active Assignment' then oer.worker_id end) as current_active_employees,
        count(distinct case when oer.assignment_status = 'Former Assignment' then oer.worker_id end) as former_employees,
        count(distinct oer.position_id) as total_positions_in_org,
        count(distinct case when oer.assignment_status = 'Active Assignment' then oer.position_id end) as active_positions_count,
        
        -- Employee turnover statistics
        count(distinct case when oer.assignment_start_date >= current_date - interval '1 year' then oer.worker_id end) as new_assignments_last_year,
        count(distinct case when oer.assignment_end_date >= current_date - interval '1 year' and oer.assignment_end_date is not null then oer.worker_id end) as departures_last_year,
        
        -- Average tenure
        avg(case when oer.assignment_status = 'Active Assignment' then oer.assignment_duration_days end) as avg_current_tenure_days,
        avg(case when oer.assignment_status = 'Former Assignment' then oer.assignment_duration_days end) as avg_former_tenure_days,
        
        -- Organizational role distribution
        count(distinct oer.organization_role_id) as unique_organization_roles,
        count(distinct case when oer.organization_role_code like '%Manager%' then oer.worker_id end) as management_role_employees,
        count(distinct case when oer.organization_role_code like '%Director%' then oer.worker_id end) as director_role_employees,
        count(distinct case when oer.organization_role_code like '%Lead%' then oer.worker_id end) as lead_role_employees,
        
        -- Latest event date
        max(oer.assignment_start_date) as last_new_assignment_date,
        max(oer.assignment_end_date) as last_departure_date
        
    from organization_employee_relationships oer
    group by oer.organization_id, oer.source_relation
),

-- Organizational performance and employee quality indicators (based on employee overview data)
organization_performance_metrics as (
    select 
        eo.organization_id,
        eo.source_relation,
        
        -- employee performance indicators
        round(avg(case when eo.is_employed then eo.overall_employee_score end), 2) as avg_employee_performance,
        round(avg(case when eo.is_employed then eo.career_development_score end), 2) as avg_career_development,
        round(avg(case when eo.is_employed then eo.retention_stability_score end), 2) as avg_retention_stability,
        
        -- Employee value distribution
        count(distinct case when eo.employee_value_segment = 'High Value - High Retention' then eo.worker_id end) as high_value_stable_employees,
        count(distinct case when eo.employee_value_segment = 'High Value - Flight Risk' then eo.worker_id end) as high_value_flight_risk_employees,
        count(distinct case when eo.employee_value_segment = 'Stable - Development Needed' then eo.worker_id end) as stable_development_employees,
        count(distinct case when eo.employee_value_segment = 'Development Required' then eo.worker_id end) as development_required_employees,
        
        -- risk distribution
        count(distinct case when eo.employee_risk_level = 'High Risk' then eo.worker_id end) as high_risk_employees,
        count(distinct case when eo.employee_risk_level = 'Medium Risk' then eo.worker_id end) as medium_risk_employees,
        count(distinct case when eo.employee_risk_level = 'Low Risk' then eo.worker_id end) as low_risk_employees,
        
        -- Employee maturity distribution
        count(distinct case when eo.employee_maturity_segment like '%New Hire%' and eo.is_employed then eo.worker_id end) as new_hire_employees,
        count(distinct case when eo.employee_maturity_segment like '%Junior%' and eo.is_employed then eo.worker_id end) as junior_employees,
        count(distinct case when eo.employee_maturity_segment like '%Experienced%' and eo.is_employed then eo.worker_id end) as experienced_employees,
        count(distinct case when eo.employee_maturity_segment like '%Senior%' and eo.is_employed then eo.worker_id end) as senior_employees,
        count(distinct case when eo.employee_maturity_segment like '%Veteran%' and eo.is_employed then eo.worker_id end) as veteran_employees,
        
        -- diversity index
        count(distinct case when eo.is_employed then eo.ethnicity_codes end) as ethnic_diversity_count,
        count(distinct case when eo.is_employed and eo.is_military_service then eo.worker_id end) as military_veterans_count,
        round(avg(case when eo.is_employed then eo.age end), 1) as avg_employee_age,
        
        -- Salary distribution
        count(distinct case when eo.compensation_tier = 'Entry Level' and eo.is_employed then eo.worker_id end) as entry_level_employees,
        count(distinct case when eo.compensation_tier = 'Mid Level' and eo.is_employed then eo.worker_id end) as mid_level_employees,
        count(distinct case when eo.compensation_tier = 'Senior Level' and eo.is_employed then eo.worker_id end) as senior_level_employees,
        count(distinct case when eo.compensation_tier = 'Executive Level' and eo.is_employed then eo.worker_id end) as executive_level_employees,
        
        -- career development statistics
        sum(case when eo.is_employed then eo.total_promotions end) as total_promotions_in_org,
        count(distinct case when eo.total_promotions >= 2 and eo.is_employed then eo.worker_id end) as high_achievers_count,
        count(distinct case when eo.fast_promotions > 0 and eo.is_employed then eo.worker_id end) as fast_track_employees_count
        
    from mart.workday__employee_overview eo
    where eo.organization_id != 'Unknown'
    group by eo.organization_id, eo.source_relation
),

-- Organizational Hierarchy and Relationship Analysis
organization_hierarchy_analysis as (
    select 
        ob.organization_id,
        ob.source_relation,
        ob.organization_name,
        ob.organization_code,
        ob.organization_type,
        ob.organization_sub_type,
        ob.staffing_model,
        ob.visibility,
        ob.effective_start as organization_created_date,
        
        -- Calculate organization age
        date_diff('day', ob.effective_start, current_date) as organization_age_days,
        case 
            when date_diff('day', ob.effective_start, current_date) < 365 then 'New Organization (<1 year)'
            when date_diff('day', ob.effective_start, current_date) < 365*3 then 'Young Organization (1-3 years)'
            when date_diff('day', ob.effective_start, current_date) < 365*10 then 'Mature Organization (3-10 years)'
            else 'Legacy Organization (10+ years)'
        end as organization_maturity_level,
        
        -- Organization type analysis
        case 
            when ob.organization_type = 'Company' then 'Corporate Level'
            when ob.organization_type = 'Division' then 'Division Level'
            when ob.organization_type = 'Department' then 'Department Level'
            when ob.organization_type = 'Team' then 'Team Level'
            else 'Other Level'
        end as organizational_level,
        
        -- Visibility and access control
        case 
            when ob.visibility = 'Public' then 'Open Access'
            when ob.visibility = 'Private' then 'Restricted Access'
            else 'Unknown Access'
        end as access_level
        
    from organization_base ob
)

select 
    oha.organization_id,
    oha.source_relation,
    oha.organization_name,
    oha.organization_code,
    oha.organization_type,
    oha.organization_sub_type,
    oha.staffing_model,
    oha.visibility,
    oha.access_level,
    oha.organization_created_date,
    oha.organization_age_days,
    round(oha.organization_age_days / 365.0, 2) as organization_age_years,
    oha.organization_maturity_level,
    oha.organizational_level,
    
    -- Staff size and distribution
    coalesce(oes.total_employees_ever, 0) as total_employees_ever,
    coalesce(oes.current_active_employees, 0) as current_active_employees,
    coalesce(oes.former_employees, 0) as former_employees,
    coalesce(oes.total_positions_in_org, 0) as total_positions,
    coalesce(oes.active_positions_count, 0) as active_positions_count,
    
    -- Calculate fill and utilization rates
    case 
        when coalesce(oes.total_positions_in_org, 0) > 0 then 
            round(coalesce(oes.current_active_employees, 0) * 100.0 / oes.total_positions_in_org, 2)
        else 0 
    end as position_fill_rate,
    
    -- liquidity indicator
    coalesce(oes.new_assignments_last_year, 0) as new_assignments_last_year,
    coalesce(oes.departures_last_year, 0) as departures_last_year,
    
    -- annual churn rate
    case 
        when coalesce(oes.current_active_employees, 0) > 0 then 
            round(coalesce(oes.departures_last_year, 0) * 100.0 / oes.current_active_employees, 2)
        else 0 
    end as annual_turnover_rate,
    
    -- tenure indicator
    round(coalesce(oes.avg_current_tenure_days, 0) / 365.0, 2) as avg_current_tenure_years,
    round(coalesce(oes.avg_former_tenure_days, 0) / 365.0, 2) as avg_former_tenure_years,
    
    -- organizational role structure
    coalesce(oes.unique_organization_roles, 0) as unique_organization_roles,
    coalesce(oes.management_role_employees, 0) as management_role_employees,
    coalesce(oes.director_role_employees, 0) as director_role_employees,
    coalesce(oes.lead_role_employees, 0) as lead_role_employees,
    
    -- management ratio
    case 
        when coalesce(oes.current_active_employees, 0) > 0 then 
            round((coalesce(oes.management_role_employees, 0) + coalesce(oes.director_role_employees, 0)) * 100.0 / oes.current_active_employees, 2)
        else 0 
    end as management_ratio,
    
    -- Performance and Quality Metrics
    coalesce(opm.avg_employee_performance, 0) as avg_employee_performance_score,
    coalesce(opm.avg_career_development, 0) as avg_career_development_score,
    coalesce(opm.avg_retention_stability, 0) as avg_retention_stability_score,
    
    -- Employee value distribution
    coalesce(opm.high_value_stable_employees, 0) as high_value_stable_employees,
    coalesce(opm.high_value_flight_risk_employees, 0) as high_value_flight_risk_employees,
    coalesce(opm.stable_development_employees, 0) as stable_development_employees,
    coalesce(opm.development_required_employees, 0) as development_required_employees,
    
    -- risk distribution
    coalesce(opm.high_risk_employees, 0) as high_risk_employees,
    coalesce(opm.medium_risk_employees, 0) as medium_risk_employees,
    coalesce(opm.low_risk_employees, 0) as low_risk_employees,
    
    -- risk ratio
    case 
        when coalesce(oes.current_active_employees, 0) > 0 then 
            round(coalesce(opm.high_risk_employees, 0) * 100.0 / oes.current_active_employees, 2)
        else 0 
    end as high_risk_employee_percentage,
    
    -- Employee maturity distribution
    coalesce(opm.new_hire_employees, 0) as new_hire_employees,
    coalesce(opm.junior_employees, 0) as junior_employees,
    coalesce(opm.experienced_employees, 0) as experienced_employees,
    coalesce(opm.senior_employees, 0) as senior_employees,
    coalesce(opm.veteran_employees, 0) as veteran_employees,
    
    -- diversity index
    coalesce(opm.ethnic_diversity_count, 0) as ethnic_diversity_count,
    coalesce(opm.military_veterans_count, 0) as military_veterans_count,
    coalesce(opm.avg_employee_age, 0) as avg_employee_age,
    
    -- Salary level distribution
    coalesce(opm.entry_level_employees, 0) as entry_level_employees,
    coalesce(opm.mid_level_employees, 0) as mid_level_employees,
    coalesce(opm.senior_level_employees, 0) as senior_level_employees,
    coalesce(opm.executive_level_employees, 0) as executive_level_employees,
    
    -- career development indicators
    coalesce(opm.total_promotions_in_org, 0) as total_promotions_in_organization,
    coalesce(opm.high_achievers_count, 0) as high_achievers_count,
    coalesce(opm.fast_track_employees_count, 0) as fast_track_employees_count,
    
    -- Overall organizational health score (0-100)
    round(
        (-- Employee performance (30%)
         least(30, coalesce(opm.avg_employee_performance, 0) * 0.3) +
         -- Retention stability (25%)
         (case when coalesce(oes.departures_last_year, 0) = 0 and coalesce(oes.current_active_employees, 0) > 0 then 25
               when annual_turnover_rate <= 10 then 20
               when annual_turnover_rate <= 20 then 15
               when annual_turnover_rate <= 30 then 10
               else 5 end) +
         -- Employee development (20%)
         least(20, coalesce(opm.avg_career_development, 0) * 0.2) +
         -- Organizational efficiency (15%)
         (case when position_fill_rate >= 90 then 15
               when position_fill_rate >= 80 then 12
               when position_fill_rate >= 70 then 9
               else 6 end) +
         -- Risk Control (10%)
         (case when high_risk_employee_percentage <= 5 then 10
               when high_risk_employee_percentage <= 15 then 7
               when high_risk_employee_percentage <= 25 then 4
               else 2 end))
    , 2) as organization_health_score,
    
    -- Organizational Performance Classification
    case 
        when round(
            (least(30, coalesce(opm.avg_employee_performance, 0) * 0.3) +
             (case when coalesce(oes.departures_last_year, 0) = 0 and coalesce(oes.current_active_employees, 0) > 0 then 25
                   when (case when coalesce(oes.current_active_employees, 0) > 0 then round(coalesce(oes.departures_last_year, 0) * 100.0 / oes.current_active_employees, 2) else 0 end) <= 10 then 20
                   when (case when coalesce(oes.current_active_employees, 0) > 0 then round(coalesce(oes.departures_last_year, 0) * 100.0 / oes.current_active_employees, 2) else 0 end) <= 20 then 15
                   else 10 end) +
             least(20, coalesce(opm.avg_career_development, 0) * 0.2) +
             (case when (case when coalesce(oes.total_positions_in_org, 0) > 0 then round(coalesce(oes.current_active_employees, 0) * 100.0 / oes.total_positions_in_org, 2) else 0 end) >= 90 then 15 else 10 end) +
             10), 2) >= 80 then 'Excellent Performance'
        when round(
            (least(30, coalesce(opm.avg_employee_performance, 0) * 0.3) +
             (case when coalesce(oes.departures_last_year, 0) = 0 and coalesce(oes.current_active_employees, 0) > 0 then 25 else 15 end) +
             least(20, coalesce(opm.avg_career_development, 0) * 0.2) +
             15 + 10), 2) >= 60 then 'Good Performance'
        when round(
            (least(30, coalesce(opm.avg_employee_performance, 0) * 0.3) +
             15 + least(20, coalesce(opm.avg_career_development, 0) * 0.2) +
             10 + 5), 2) >= 40 then 'Average Performance'
        else 'Needs Improvement'
    end as performance_category,
    
    -- Organization size classification
    case 
        when coalesce(oes.current_active_employees, 0) = 0 then 'Empty Organization'
        when coalesce(oes.current_active_employees, 0) <= 5 then 'Micro Team'
        when coalesce(oes.current_active_employees, 0) <= 15 then 'Small Team'
        when coalesce(oes.current_active_employees, 0) <= 50 then 'Medium Team'
        when coalesce(oes.current_active_employees, 0) <= 200 then 'Large Team'
        else 'Enterprise Unit'
    end as organization_size_category,
    
    -- Latest event date
    coalesce(oes.last_new_assignment_date, oha.organization_created_date) as last_activity_date,
    coalesce(oes.last_departure_date, '1900-01-01'::date) as last_departure_date,
    
    -- management advice
    case 
        when coalesce(oes.current_active_employees, 0) = 0 then 'Review Organization Necessity'
        when annual_turnover_rate > 30 then 'Critical: Focus on Retention'
        when high_risk_employee_percentage > 25 then 'Address Employee Risk Factors'
        when position_fill_rate < 70 then 'Improve Recruitment and Staffing'
        when coalesce(opm.avg_employee_performance, 0) < 50 then 'Enhance Performance Management'
        when management_ratio > 40 then 'Optimize Management Structure'
        else 'Maintain Current Excellence'
    end as management_recommendation,
    
    -- Data quality check
    case 
        when oha.organization_name is null or oha.organization_name = '' then 'ERROR: Missing organization name'
        when coalesce(oes.current_active_employees, 0) > coalesce(oes.total_positions_in_org, 0) + 10 then 'WARNING: More employees than positions'
        when annual_turnover_rate > 100 then 'WARNING: Turnover rate exceeds 100%'
        when oha.organization_age_days < 0 then 'ERROR: Invalid organization creation date'
        else 'VALID'
    end as data_quality_flag,
    
    -- Analysis timestamp
    current_timestamp as analysis_timestamp
    
from organization_hierarchy_analysis oha
left join organization_employee_stats oes
    on oha.organization_id = oes.organization_id
    and oha.source_relation = oes.source_relation
left join organization_performance_metrics opm
    on oha.organization_id = opm.organization_id
    and oha.source_relation = opm.source_relation
order by 
    coalesce(oes.current_active_employees, 0) desc,
    coalesce(opm.avg_employee_performance, 0) desc,
    oha.organization_name
```

## differences

```json
{
  "kind": "date_aligned_011",
  "record": "records/011_table_alignment.jsonl",
  "detail_record": "records/011_alignment_impl-016.json",
  "prediction_database": "/home/katherine/Assumption_Ledger/data/011_agent_alignment/impl-016/workday__organization_overview_2025-10-13.duckdb",
  "gold_database": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/workday.duckdb",
  "actual_schema": "mart",
  "table": "workday__organization_overview",
  "candidate_date": "2025-10-13",
  "comparison_columns": [
    "access_level",
    "active_positions_count",
    "analysis_timestamp",
    "annual_turnover_rate",
    "avg_career_development_score",
    "avg_employee_age",
    "avg_employee_performance_score",
    "avg_former_tenure_years",
    "avg_retention_stability_score",
    "current_active_employees",
    "data_quality_flag",
    "departures_last_year",
    "development_required_employees",
    "director_role_employees",
    "entry_level_employees",
    "ethnic_diversity_count",
    "executive_level_employees",
    "experienced_employees",
    "fast_track_employees_count",
    "former_employees",
    "high_achievers_count",
    "high_risk_employees",
    "high_value_flight_risk_employees",
    "high_value_stable_employees",
    "junior_employees",
    "last_activity_date",
    "last_departure_date",
    "lead_role_employees",
    "low_risk_employees",
    "management_ratio",
    "management_recommendation",
    "management_role_employees",
    "medium_risk_employees",
    "mid_level_employees",
    "military_veterans_count",
    "new_assignments_last_year",
    "new_hire_employees",
    "organization_age_days",
    "organization_age_years",
    "organization_code",
    "organization_created_date",
    "organization_health_score",
    "organization_id",
    "organization_maturity_level",
    "organization_name",
    "organization_size_category",
    "organization_sub_type",
    "organization_type",
    "organizational_level",
    "performance_category",
    "position_fill_rate",
    "senior_employees",
    "senior_level_employees",
    "stable_development_employees",
    "staffing_model",
    "total_employees_ever",
    "total_positions",
    "total_promotions_in_organization",
    "unique_organization_roles",
    "veteran_employees",
    "visibility"
  ],
  "key_columns": [
    "organization_id"
  ],
  "prediction_rows": 117,
  "gold_rows": 117,
  "row_delta": 0,
  "key_statistics": {
    "pred_distinct_keys": 117,
    "gold_distinct_keys": 117,
    "pred_duplicate_key_groups": 0,
    "gold_duplicate_key_groups": 0,
    "pred_only_keys": 0,
    "gold_only_keys": 0,
    "shared_keys": 117,
    "shared_nonunique_key_groups": 0
  },
  "l0_column_differences": [
    {
      "column": "organization_id",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "access_level",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "active_positions_count",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "analysis_timestamp",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 117,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 117,
      "pred_unmatched_value_occurrences": 117,
      "gold_unmatched_value_occurrences": 117,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "annual_turnover_rate",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 117,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 117,
      "pred_unmatched_value_occurrences": 117,
      "gold_unmatched_value_occurrences": 117,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "avg_career_development_score",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "avg_employee_age",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "avg_employee_performance_score",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "avg_former_tenure_years",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 5,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 5,
      "pred_unmatched_value_occurrences": 5,
      "gold_unmatched_value_occurrences": 5,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "avg_retention_stability_score",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "current_active_employees",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "data_quality_flag",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "departures_last_year",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "development_required_employees",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "director_role_employees",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "entry_level_employees",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "ethnic_diversity_count",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "executive_level_employees",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "experienced_employees",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "fast_track_employees_count",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "former_employees",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "high_achievers_count",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "high_risk_employees",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "high_value_flight_risk_employees",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "high_value_stable_employees",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "junior_employees",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "last_activity_date",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "last_departure_date",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "lead_role_employees",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "low_risk_employees",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "management_ratio",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 117,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 117,
      "pred_unmatched_value_occurrences": 117,
      "gold_unmatched_value_occurrences": 117,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "management_recommendation",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "management_role_employees",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "medium_risk_employees",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "mid_level_employees",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "military_veterans_count",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "new_assignments_last_year",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "new_hire_employees",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "organization_age_days",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "organization_age_years",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "organization_code",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "organization_created_date",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "organization_health_score",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 117,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 117,
      "pred_unmatched_value_occurrences": 117,
      "gold_unmatched_value_occurrences": 117,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "organization_maturity_level",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 117,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 117,
      "pred_unmatched_value_occurrences": 117,
      "gold_unmatched_value_occurrences": 117,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "organization_name",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "organization_size_category",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 117,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 117,
      "pred_unmatched_value_occurrences": 117,
      "gold_unmatched_value_occurrences": 117,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "organization_sub_type",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "organization_type",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "organizational_level",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "performance_category",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "position_fill_rate",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "senior_employees",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "senior_level_employees",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "stable_development_employees",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "staffing_model",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "total_employees_ever",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "total_positions",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "total_promotions_in_organization",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "unique_organization_roles",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 106,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 106,
      "pred_unmatched_value_occurrences": 106,
      "gold_unmatched_value_occurrences": 106,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "veteran_employees",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "visibility",
      "included_in_official_comparison": true,
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "count_semantics": "exact_one_to_one_rows"
    }
  ],
  "l3_column_differences": [
    {
      "column": "access_level",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "active_positions_count",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "analysis_timestamp",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "annual_turnover_rate",
      "one_to_one_mismatch_rows": 117,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 117,
      "pred_unmatched_value_occurrences": 117,
      "gold_unmatched_value_occurrences": 117,
      "marginal_multisets_equal": false,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "avg_career_development_score",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "avg_employee_age",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "avg_employee_performance_score",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "avg_former_tenure_years",
      "one_to_one_mismatch_rows": 5,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 5,
      "pred_unmatched_value_occurrences": 5,
      "gold_unmatched_value_occurrences": 5,
      "marginal_multisets_equal": false,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "avg_retention_stability_score",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "current_active_employees",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "data_quality_flag",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "departures_last_year",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "development_required_employees",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "director_role_employees",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "entry_level_employees",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "ethnic_diversity_count",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "executive_level_employees",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "experienced_employees",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "fast_track_employees_count",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "former_employees",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "high_achievers_count",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "high_risk_employees",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "high_value_flight_risk_employees",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "high_value_stable_employees",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "junior_employees",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "last_activity_date",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "last_departure_date",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "lead_role_employees",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "low_risk_employees",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "management_ratio",
      "one_to_one_mismatch_rows": 117,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 117,
      "pred_unmatched_value_occurrences": 117,
      "gold_unmatched_value_occurrences": 117,
      "marginal_multisets_equal": false,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "management_recommendation",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "management_role_employees",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "medium_risk_employees",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "mid_level_employees",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "military_veterans_count",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "new_assignments_last_year",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "new_hire_employees",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "organization_age_days",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "organization_age_years",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "organization_code",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "organization_created_date",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "organization_health_score",
      "one_to_one_mismatch_rows": 117,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 117,
      "pred_unmatched_value_occurrences": 117,
      "gold_unmatched_value_occurrences": 117,
      "marginal_multisets_equal": false,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "organization_id",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "organization_maturity_level",
      "one_to_one_mismatch_rows": 117,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 117,
      "pred_unmatched_value_occurrences": 117,
      "gold_unmatched_value_occurrences": 117,
      "marginal_multisets_equal": false,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "organization_name",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "organization_size_category",
      "one_to_one_mismatch_rows": 117,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 117,
      "pred_unmatched_value_occurrences": 117,
      "gold_unmatched_value_occurrences": 117,
      "marginal_multisets_equal": false,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "organization_sub_type",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "organization_type",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "organizational_level",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "performance_category",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "position_fill_rate",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "senior_employees",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "senior_level_employees",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "stable_development_employees",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "staffing_model",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "total_employees_ever",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "total_positions",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "total_promotions_in_organization",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "unique_organization_roles",
      "one_to_one_mismatch_rows": 106,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 106,
      "pred_unmatched_value_occurrences": 106,
      "gold_unmatched_value_occurrences": 106,
      "marginal_multisets_equal": false,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "veteran_employees",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    },
    {
      "column": "visibility",
      "one_to_one_mismatch_rows": 0,
      "nonunique_key_minimum_value_mismatch_pairs": 0,
      "mismatch_rows_or_minimum_pairs": 0,
      "pred_unmatched_value_occurrences": 0,
      "gold_unmatched_value_occurrences": 0,
      "marginal_multisets_equal": true,
      "count_semantics": "exact_one_to_one_rows"
    }
  ],
  "whole_match_level": "仍不匹配",
  "keyed_match_level": "仍不匹配",
  "selection_reason": "011 执行与比较成功，使用该表已验证日期；优先 010 同题候选 / 共同兼容日，再按日期升序",
  "value_representation": "Unmodified DuckDB CAST AS VARCHAR; SQL NULL is JSON null. Keys use the unchanged historical L0 normalization.",
  "new_queries_only_read_existing_results": true,
  "one_side_key_examples": {
    "prediction_only": [],
    "gold_only": []
  },
  "column_details": [
    {
      "column": "organization_id",
      "l0_counts_verbatim": {
        "column": "organization_id",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "organization_id",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "access_level",
      "l0_counts_verbatim": {
        "column": "access_level",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "access_level",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "active_positions_count",
      "l0_counts_verbatim": {
        "column": "active_positions_count",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "active_positions_count",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "analysis_timestamp",
      "l0_counts_verbatim": {
        "column": "analysis_timestamp",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 117,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 117,
        "pred_unmatched_value_occurrences": 117,
        "gold_unmatched_value_occurrences": 117,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "analysis_timestamp",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "organization_id": "org00000006"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000006"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000006"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "2025-10-13 08:00:00+08",
          "gold_value": "2025-10-13 13:18:28.226+08"
        },
        {
          "key_normalized": {
            "organization_id": "org00000008"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000008"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000008"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "2025-10-13 08:00:00+08",
          "gold_value": "2025-10-13 13:18:28.226+08"
        },
        {
          "key_normalized": {
            "organization_id": "org00000009"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000009"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000009"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "2025-10-13 08:00:00+08",
          "gold_value": "2025-10-13 13:18:28.226+08"
        },
        {
          "key_normalized": {
            "organization_id": "org00000010"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000010"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000010"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "2025-10-13 08:00:00+08",
          "gold_value": "2025-10-13 13:18:28.226+08"
        },
        {
          "key_normalized": {
            "organization_id": "org00000012"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000012"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000012"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "2025-10-13 08:00:00+08",
          "gold_value": "2025-10-13 13:18:28.226+08"
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 117,
        "pred_unmatched_value_occurrences": 117,
        "gold_unmatched_value_occurrences": 117
      },
      "agent_actual_type": "TIMESTAMP WITH TIME ZONE",
      "gold_actual_type": "TIMESTAMP WITH TIME ZONE"
    },
    {
      "column": "annual_turnover_rate",
      "l0_counts_verbatim": {
        "column": "annual_turnover_rate",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 117,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 117,
        "pred_unmatched_value_occurrences": 117,
        "gold_unmatched_value_occurrences": 117,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "annual_turnover_rate",
        "one_to_one_mismatch_rows": 117,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 117,
        "pred_unmatched_value_occurrences": 117,
        "gold_unmatched_value_occurrences": 117,
        "marginal_multisets_equal": false,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "organization_id": "org00000006"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000006"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000006"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": null,
          "gold_value": "0.0"
        },
        {
          "key_normalized": {
            "organization_id": "org00000008"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000008"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000008"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": null,
          "gold_value": "0.0"
        },
        {
          "key_normalized": {
            "organization_id": "org00000009"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000009"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000009"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": null,
          "gold_value": "0.0"
        },
        {
          "key_normalized": {
            "organization_id": "org00000010"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000010"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000010"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": null,
          "gold_value": "0.0"
        },
        {
          "key_normalized": {
            "organization_id": "org00000012"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000012"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000012"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": null,
          "gold_value": "0.0"
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 117,
        "pred_unmatched_value_occurrences": 117,
        "gold_unmatched_value_occurrences": 117
      },
      "agent_actual_type": "DOUBLE",
      "gold_actual_type": "DOUBLE"
    },
    {
      "column": "avg_career_development_score",
      "l0_counts_verbatim": {
        "column": "avg_career_development_score",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "avg_career_development_score",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "DOUBLE",
      "gold_actual_type": "DOUBLE"
    },
    {
      "column": "avg_employee_age",
      "l0_counts_verbatim": {
        "column": "avg_employee_age",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "avg_employee_age",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "DOUBLE",
      "gold_actual_type": "DOUBLE"
    },
    {
      "column": "avg_employee_performance_score",
      "l0_counts_verbatim": {
        "column": "avg_employee_performance_score",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "avg_employee_performance_score",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "DOUBLE",
      "gold_actual_type": "DOUBLE"
    },
    {
      "column": "avg_former_tenure_years",
      "l0_counts_verbatim": {
        "column": "avg_former_tenure_years",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 5,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 5,
        "pred_unmatched_value_occurrences": 5,
        "gold_unmatched_value_occurrences": 5,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "avg_former_tenure_years",
        "one_to_one_mismatch_rows": 5,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 5,
        "pred_unmatched_value_occurrences": 5,
        "gold_unmatched_value_occurrences": 5,
        "marginal_multisets_equal": false,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "organization_id": "org00000028"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000028"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000028"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "0.69",
          "gold_value": "0.7"
        },
        {
          "key_normalized": {
            "organization_id": "org00000053"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000053"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000053"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "0.65",
          "gold_value": "0.66"
        },
        {
          "key_normalized": {
            "organization_id": "org00000070"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000070"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000070"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "0.59",
          "gold_value": "0.61"
        },
        {
          "key_normalized": {
            "organization_id": "org00000180"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000180"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000180"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "0.67",
          "gold_value": "0.68"
        },
        {
          "key_normalized": {
            "organization_id": "org00000190"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000190"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000190"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "0.66",
          "gold_value": "0.65"
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 5,
        "pred_unmatched_value_occurrences": 5,
        "gold_unmatched_value_occurrences": 5
      },
      "agent_actual_type": "DOUBLE",
      "gold_actual_type": "DOUBLE"
    },
    {
      "column": "avg_retention_stability_score",
      "l0_counts_verbatim": {
        "column": "avg_retention_stability_score",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "avg_retention_stability_score",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "DOUBLE",
      "gold_actual_type": "DOUBLE"
    },
    {
      "column": "current_active_employees",
      "l0_counts_verbatim": {
        "column": "current_active_employees",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "current_active_employees",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "data_quality_flag",
      "l0_counts_verbatim": {
        "column": "data_quality_flag",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "data_quality_flag",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "departures_last_year",
      "l0_counts_verbatim": {
        "column": "departures_last_year",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "departures_last_year",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "development_required_employees",
      "l0_counts_verbatim": {
        "column": "development_required_employees",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "development_required_employees",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "director_role_employees",
      "l0_counts_verbatim": {
        "column": "director_role_employees",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "director_role_employees",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "entry_level_employees",
      "l0_counts_verbatim": {
        "column": "entry_level_employees",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "entry_level_employees",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "ethnic_diversity_count",
      "l0_counts_verbatim": {
        "column": "ethnic_diversity_count",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "ethnic_diversity_count",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "executive_level_employees",
      "l0_counts_verbatim": {
        "column": "executive_level_employees",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "executive_level_employees",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "experienced_employees",
      "l0_counts_verbatim": {
        "column": "experienced_employees",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "experienced_employees",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "fast_track_employees_count",
      "l0_counts_verbatim": {
        "column": "fast_track_employees_count",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "fast_track_employees_count",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "former_employees",
      "l0_counts_verbatim": {
        "column": "former_employees",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "former_employees",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "high_achievers_count",
      "l0_counts_verbatim": {
        "column": "high_achievers_count",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "high_achievers_count",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "high_risk_employees",
      "l0_counts_verbatim": {
        "column": "high_risk_employees",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "high_risk_employees",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "high_value_flight_risk_employees",
      "l0_counts_verbatim": {
        "column": "high_value_flight_risk_employees",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "high_value_flight_risk_employees",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "high_value_stable_employees",
      "l0_counts_verbatim": {
        "column": "high_value_stable_employees",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "high_value_stable_employees",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "junior_employees",
      "l0_counts_verbatim": {
        "column": "junior_employees",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "junior_employees",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "last_activity_date",
      "l0_counts_verbatim": {
        "column": "last_activity_date",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "last_activity_date",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "DATE",
      "gold_actual_type": "DATE"
    },
    {
      "column": "last_departure_date",
      "l0_counts_verbatim": {
        "column": "last_departure_date",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "last_departure_date",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "DATE",
      "gold_actual_type": "DATE"
    },
    {
      "column": "lead_role_employees",
      "l0_counts_verbatim": {
        "column": "lead_role_employees",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "lead_role_employees",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "low_risk_employees",
      "l0_counts_verbatim": {
        "column": "low_risk_employees",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "low_risk_employees",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "management_ratio",
      "l0_counts_verbatim": {
        "column": "management_ratio",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 117,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 117,
        "pred_unmatched_value_occurrences": 117,
        "gold_unmatched_value_occurrences": 117,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "management_ratio",
        "one_to_one_mismatch_rows": 117,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 117,
        "pred_unmatched_value_occurrences": 117,
        "gold_unmatched_value_occurrences": 117,
        "marginal_multisets_equal": false,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "organization_id": "org00000006"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000006"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000006"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": null,
          "gold_value": "0.0"
        },
        {
          "key_normalized": {
            "organization_id": "org00000008"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000008"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000008"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": null,
          "gold_value": "0.0"
        },
        {
          "key_normalized": {
            "organization_id": "org00000009"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000009"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000009"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": null,
          "gold_value": "0.0"
        },
        {
          "key_normalized": {
            "organization_id": "org00000010"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000010"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000010"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": null,
          "gold_value": "0.0"
        },
        {
          "key_normalized": {
            "organization_id": "org00000012"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000012"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000012"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": null,
          "gold_value": "0.0"
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 117,
        "pred_unmatched_value_occurrences": 117,
        "gold_unmatched_value_occurrences": 117
      },
      "agent_actual_type": "DOUBLE",
      "gold_actual_type": "DOUBLE"
    },
    {
      "column": "management_recommendation",
      "l0_counts_verbatim": {
        "column": "management_recommendation",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "management_recommendation",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "management_role_employees",
      "l0_counts_verbatim": {
        "column": "management_role_employees",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "management_role_employees",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "medium_risk_employees",
      "l0_counts_verbatim": {
        "column": "medium_risk_employees",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "medium_risk_employees",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "mid_level_employees",
      "l0_counts_verbatim": {
        "column": "mid_level_employees",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "mid_level_employees",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "military_veterans_count",
      "l0_counts_verbatim": {
        "column": "military_veterans_count",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "military_veterans_count",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "new_assignments_last_year",
      "l0_counts_verbatim": {
        "column": "new_assignments_last_year",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "new_assignments_last_year",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "new_hire_employees",
      "l0_counts_verbatim": {
        "column": "new_hire_employees",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "new_hire_employees",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "organization_age_days",
      "l0_counts_verbatim": {
        "column": "organization_age_days",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "organization_age_days",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "organization_age_years",
      "l0_counts_verbatim": {
        "column": "organization_age_years",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "organization_age_years",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "DOUBLE",
      "gold_actual_type": "DOUBLE"
    },
    {
      "column": "organization_code",
      "l0_counts_verbatim": {
        "column": "organization_code",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "organization_code",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "organization_created_date",
      "l0_counts_verbatim": {
        "column": "organization_created_date",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "organization_created_date",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "DATE",
      "gold_actual_type": "DATE"
    },
    {
      "column": "organization_health_score",
      "l0_counts_verbatim": {
        "column": "organization_health_score",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 117,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 117,
        "pred_unmatched_value_occurrences": 117,
        "gold_unmatched_value_occurrences": 117,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "organization_health_score",
        "one_to_one_mismatch_rows": 117,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 117,
        "pred_unmatched_value_occurrences": 117,
        "gold_unmatched_value_occurrences": 117,
        "marginal_multisets_equal": false,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "organization_id": "org00000006"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000006"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000006"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "13.0",
          "gold_value": "36.0"
        },
        {
          "key_normalized": {
            "organization_id": "org00000008"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000008"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000008"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "13.0",
          "gold_value": "36.0"
        },
        {
          "key_normalized": {
            "organization_id": "org00000009"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000009"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000009"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "13.0",
          "gold_value": "36.0"
        },
        {
          "key_normalized": {
            "organization_id": "org00000010"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000010"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000010"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "13.0",
          "gold_value": "36.0"
        },
        {
          "key_normalized": {
            "organization_id": "org00000012"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000012"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000012"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "13.0",
          "gold_value": "36.0"
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 117,
        "pred_unmatched_value_occurrences": 117,
        "gold_unmatched_value_occurrences": 117
      },
      "agent_actual_type": "DOUBLE",
      "gold_actual_type": "DOUBLE"
    },
    {
      "column": "organization_maturity_level",
      "l0_counts_verbatim": {
        "column": "organization_maturity_level",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 117,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 117,
        "pred_unmatched_value_occurrences": 117,
        "gold_unmatched_value_occurrences": 117,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "organization_maturity_level",
        "one_to_one_mismatch_rows": 117,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 117,
        "pred_unmatched_value_occurrences": 117,
        "gold_unmatched_value_occurrences": 117,
        "marginal_multisets_equal": false,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "organization_id": "org00000006"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000006"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000006"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "Young",
          "gold_value": "Young Organization (1-3 years)"
        },
        {
          "key_normalized": {
            "organization_id": "org00000008"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000008"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000008"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "New",
          "gold_value": "New Organization (<1 year)"
        },
        {
          "key_normalized": {
            "organization_id": "org00000009"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000009"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000009"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "Mature",
          "gold_value": "Mature Organization (3-10 years)"
        },
        {
          "key_normalized": {
            "organization_id": "org00000010"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000010"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000010"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "New",
          "gold_value": "New Organization (<1 year)"
        },
        {
          "key_normalized": {
            "organization_id": "org00000012"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000012"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000012"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "New",
          "gold_value": "New Organization (<1 year)"
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 117,
        "pred_unmatched_value_occurrences": 117,
        "gold_unmatched_value_occurrences": 117
      },
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "organization_name",
      "l0_counts_verbatim": {
        "column": "organization_name",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "organization_name",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "organization_size_category",
      "l0_counts_verbatim": {
        "column": "organization_size_category",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 117,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 117,
        "pred_unmatched_value_occurrences": 117,
        "gold_unmatched_value_occurrences": 117,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "organization_size_category",
        "one_to_one_mismatch_rows": 117,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 117,
        "pred_unmatched_value_occurrences": 117,
        "gold_unmatched_value_occurrences": 117,
        "marginal_multisets_equal": false,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "organization_id": "org00000006"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000006"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000006"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "Empty",
          "gold_value": "Empty Organization"
        },
        {
          "key_normalized": {
            "organization_id": "org00000008"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000008"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000008"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "Empty",
          "gold_value": "Empty Organization"
        },
        {
          "key_normalized": {
            "organization_id": "org00000009"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000009"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000009"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "Empty",
          "gold_value": "Empty Organization"
        },
        {
          "key_normalized": {
            "organization_id": "org00000010"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000010"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000010"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "Empty",
          "gold_value": "Empty Organization"
        },
        {
          "key_normalized": {
            "organization_id": "org00000012"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000012"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000012"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "Empty",
          "gold_value": "Empty Organization"
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 117,
        "pred_unmatched_value_occurrences": 117,
        "gold_unmatched_value_occurrences": 117
      },
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "organization_sub_type",
      "l0_counts_verbatim": {
        "column": "organization_sub_type",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "organization_sub_type",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "organization_type",
      "l0_counts_verbatim": {
        "column": "organization_type",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "organization_type",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "organizational_level",
      "l0_counts_verbatim": {
        "column": "organizational_level",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "organizational_level",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "performance_category",
      "l0_counts_verbatim": {
        "column": "performance_category",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "performance_category",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "position_fill_rate",
      "l0_counts_verbatim": {
        "column": "position_fill_rate",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "position_fill_rate",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "DOUBLE",
      "gold_actual_type": "DOUBLE"
    },
    {
      "column": "senior_employees",
      "l0_counts_verbatim": {
        "column": "senior_employees",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "senior_employees",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "senior_level_employees",
      "l0_counts_verbatim": {
        "column": "senior_level_employees",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "senior_level_employees",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "stable_development_employees",
      "l0_counts_verbatim": {
        "column": "stable_development_employees",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "stable_development_employees",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "staffing_model",
      "l0_counts_verbatim": {
        "column": "staffing_model",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "staffing_model",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    },
    {
      "column": "total_employees_ever",
      "l0_counts_verbatim": {
        "column": "total_employees_ever",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "total_employees_ever",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "total_positions",
      "l0_counts_verbatim": {
        "column": "total_positions",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "total_positions",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "total_promotions_in_organization",
      "l0_counts_verbatim": {
        "column": "total_promotions_in_organization",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "total_promotions_in_organization",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "HUGEINT",
      "gold_actual_type": "HUGEINT"
    },
    {
      "column": "unique_organization_roles",
      "l0_counts_verbatim": {
        "column": "unique_organization_roles",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 106,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 106,
        "pred_unmatched_value_occurrences": 106,
        "gold_unmatched_value_occurrences": 106,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "unique_organization_roles",
        "one_to_one_mismatch_rows": 106,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 106,
        "pred_unmatched_value_occurrences": 106,
        "gold_unmatched_value_occurrences": 106,
        "marginal_multisets_equal": false,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [
        {
          "key_normalized": {
            "organization_id": "org00000006"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000006"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000006"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "2",
          "gold_value": "7"
        },
        {
          "key_normalized": {
            "organization_id": "org00000008"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000008"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000008"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "1",
          "gold_value": "7"
        },
        {
          "key_normalized": {
            "organization_id": "org00000009"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000009"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000009"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "1",
          "gold_value": "3"
        },
        {
          "key_normalized": {
            "organization_id": "org00000010"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000010"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000010"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "2",
          "gold_value": "4"
        },
        {
          "key_normalized": {
            "organization_id": "org00000012"
          },
          "agent_key_raw_text": {
            "organization_id": "ORG00000012"
          },
          "gold_key_raw_text": {
            "organization_id": "ORG00000012"
          },
          "agent_rows_with_key": 1,
          "gold_rows_with_key": 1,
          "kind": "one_to_one",
          "agent_value": "2",
          "gold_value": "4"
        }
      ],
      "sample_counts_recheck": {
        "mismatch_rows_or_minimum_pairs": 106,
        "pred_unmatched_value_occurrences": 106,
        "gold_unmatched_value_occurrences": 106
      },
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "veteran_employees",
      "l0_counts_verbatim": {
        "column": "veteran_employees",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "veteran_employees",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "BIGINT",
      "gold_actual_type": "BIGINT"
    },
    {
      "column": "visibility",
      "l0_counts_verbatim": {
        "column": "visibility",
        "included_in_official_comparison": true,
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "count_semantics": "exact_one_to_one_rows"
      },
      "l3_counts_verbatim": {
        "column": "visibility",
        "one_to_one_mismatch_rows": 0,
        "nonunique_key_minimum_value_mismatch_pairs": 0,
        "mismatch_rows_or_minimum_pairs": 0,
        "pred_unmatched_value_occurrences": 0,
        "gold_unmatched_value_occurrences": 0,
        "marginal_multisets_equal": true,
        "count_semantics": "exact_one_to_one_rows"
      },
      "sample_level": "L0",
      "sample_key_groups": [],
      "sample_counts_recheck": null,
      "agent_actual_type": "VARCHAR",
      "gold_actual_type": "VARCHAR"
    }
  ]
}
```

## agent_constraints_006

```json
{
  "source_record": "records/006_contract_impl-016.json",
  "declarations": {
    "grain": [
      {
        "raw_text": "One row per active organization_id and source_relation",
        "status": "parsed",
        "columns": [
          "organization_id",
          "source_relation"
        ],
        "qualifier_original": "",
        "policy": "explicit identifiers matched to contract columns; no synonyms or inferred IDs",
        "sources": [
          {
            "yaml_path": [
              "modeling_spec",
              "marts_models",
              4,
              "grain"
            ],
            "start_line": 2026,
            "end_line": 2026,
            "original_excerpt": "      grain: One row per active organization_id and source_relation\n",
            "decoded_value": "One row per active organization_id and source_relation"
          }
        ]
      }
    ],
    "primary_key": [],
    "not_null": [
      {
        "columns": [
          "organization_id"
        ],
        "sources": [
          {
            "yaml_path": [
              "modeling_spec",
              "marts_models",
              4,
              "columns",
              0,
              "tests",
              0
            ],
            "start_line": 2038,
            "end_line": 2040,
            "original_excerpt": "        tests:\n        - not_null\n      - name: source_relation\n",
            "decoded_value": [
              "not_null"
            ]
          }
        ]
      },
      {
        "columns": [
          "source_relation"
        ],
        "sources": [
          {
            "yaml_path": [
              "modeling_spec",
              "marts_models",
              4,
              "columns",
              1,
              "tests",
              0
            ],
            "start_line": 2043,
            "end_line": 2045,
            "original_excerpt": "        tests:\n        - not_null\n      - name: organization_name\n",
            "decoded_value": [
              "not_null"
            ]
          }
        ]
      }
    ],
    "unique": []
  },
  "agent": {
    "table_exists": true,
    "actual_schema": "mart",
    "table_type": "BASE TABLE",
    "same_name_other_schemas": [],
    "row_count": 117,
    "checks": {
      "grain": [
        {
          "columns": [
            "organization_id",
            "source_relation"
          ],
          "status": "checked",
          "violated": false,
          "sql": "SELECT count(*),count(*) FILTER(WHERE \"__ledger_group_count\">1),coalesce(sum(\"__ledger_group_count\") FILTER(WHERE \"__ledger_group_count\">1),0),\n                      coalesce(sum(\"__ledger_group_count\"-1) FILTER(WHERE \"__ledger_group_count\">1),0),coalesce(sum(\"__ledger_group_count\") FILTER(WHERE \"organization_id\" IS NULL OR \"source_relation\" IS NULL),0),\n                      count(*) FILTER(WHERE \"__ledger_group_count\">1 AND NOT (\"organization_id\" IS NULL OR \"source_relation\" IS NULL)),coalesce(sum(\"__ledger_group_count\") FILTER(WHERE \"__ledger_group_count\">1 AND NOT (\"organization_id\" IS NULL OR \"source_relation\" IS NULL)),0),\n                      coalesce(sum(\"__ledger_group_count\"-1) FILTER(WHERE \"__ledger_group_count\">1 AND NOT (\"organization_id\" IS NULL OR \"source_relation\" IS NULL)),0),count(*) FILTER(WHERE \"__ledger_group_count\">1 AND (\"organization_id\" IS NULL OR \"source_relation\" IS NULL)),\n                      coalesce(sum(\"__ledger_group_count\") FILTER(WHERE \"__ledger_group_count\">1 AND (\"organization_id\" IS NULL OR \"source_relation\" IS NULL)),0)\n                      FROM (SELECT \"organization_id\",\"source_relation\",count(*) AS \"__ledger_group_count\" FROM \"mart\".\"workday__organization_overview\" GROUP BY \"organization_id\",\"source_relation\") grouped_keys",
          "sql_key_order": [
            "organization_id",
            "source_relation"
          ],
          "distinct_key_groups": 117,
          "duplicate_key_groups": 0,
          "rows_in_duplicate_groups": 0,
          "excess_duplicate_rows": 0,
          "null_key_rows": 0,
          "nonnull_duplicate_key_groups": 0,
          "nonnull_rows_in_duplicate_groups": 0,
          "nonnull_excess_duplicate_rows": 0,
          "null_containing_duplicate_key_groups": 0,
          "rows_in_null_containing_duplicate_groups": 0
        }
      ],
      "primary_key": [],
      "not_null": [
        {
          "columns": [
            "organization_id"
          ],
          "status": "checked",
          "violated": false,
          "sql_null_rows": 0
        },
        {
          "columns": [
            "source_relation"
          ],
          "status": "checked",
          "violated": false,
          "sql_null_rows": 0
        }
      ],
      "unique": []
    },
    "actual_table": "workday__organization_overview",
    "actual_columns": [
      "organization_id",
      "source_relation",
      "organization_name",
      "organization_code",
      "organization_type",
      "organization_sub_type",
      "staffing_model",
      "visibility",
      "access_level",
      "organization_created_date",
      "organization_age_days",
      "organization_age_years",
      "organization_maturity_level",
      "organizational_level",
      "total_employees_ever",
      "current_active_employees",
      "former_employees",
      "total_positions",
      "active_positions_count",
      "position_fill_rate",
      "new_assignments_last_year",
      "departures_last_year",
      "annual_turnover_rate",
      "avg_current_tenure_years",
      "avg_former_tenure_years",
      "unique_organization_roles",
      "management_role_employees",
      "director_role_employees",
      "lead_role_employees",
      "management_ratio",
      "avg_employee_performance_score",
      "avg_career_development_score",
      "avg_retention_stability_score",
      "high_value_stable_employees",
      "high_value_flight_risk_employees",
      "stable_development_employees",
      "development_required_employees",
      "high_risk_employees",
      "medium_risk_employees",
      "low_risk_employees",
      "high_risk_employee_percentage",
      "new_hire_employees",
      "junior_employees",
      "experienced_employees",
      "senior_employees",
      "veteran_employees",
      "ethnic_diversity_count",
      "military_veterans_count",
      "avg_employee_age",
      "entry_level_employees",
      "mid_level_employees",
      "senior_level_employees",
      "executive_level_employees",
      "total_promotions_in_organization",
      "high_achievers_count",
      "fast_track_employees_count",
      "organization_health_score",
      "performance_category",
      "organization_size_category",
      "last_activity_date",
      "last_departure_date",
      "management_recommendation",
      "data_quality_flag",
      "analysis_timestamp"
    ],
    "missing_declared_columns": [],
    "not_null_count_sql": "SELECT count(*) FILTER(WHERE \"organization_id\" IS NULL),count(*) FILTER(WHERE \"source_relation\" IS NULL) FROM \"mart\".\"workday__organization_overview\"",
    "categories": {
      "grain": {
        "status": "checked_no_violation",
        "violated": false,
        "declared_checks": 1,
        "checked_checks": 1,
        "unknown_checks": 0,
        "complete": true
      },
      "primary_key": {
        "status": "not_declared",
        "violated": null,
        "declared_checks": 0,
        "checked_checks": 0,
        "unknown_checks": 0
      },
      "not_null": {
        "status": "checked_no_violation",
        "violated": false,
        "declared_checks": 2,
        "checked_checks": 2,
        "unknown_checks": 0,
        "complete": true
      },
      "unique": {
        "status": "not_declared",
        "violated": null,
        "declared_checks": 0,
        "checked_checks": 0,
        "unknown_checks": 0
      }
    },
    "any_constraint_violated": false
  }
}
```

## all_markers_and_evidence_008

```json
{
  "source_record": "records/008_table_scan.jsonl",
  "verbatim_record": {
    "task": "impl-016",
    "layer": "marts",
    "table": "workday__organization_overview",
    "logical_contract_table": "workday__organization_overview",
    "delivery_name_mapping_evidence": [],
    "inventory_sources": {
      "retained_database": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/workday.duckdb",
      "present_in_database": true,
      "agent_final_sql_files": [
        "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql"
      ]
    },
    "status_007": {
      "gold_table_exists_in_original_gold": true,
      "whole_level_007": "仍不匹配",
      "007_present": true,
      "004_failed_set_member": false,
      "005_failed_set_member": true,
      "005_current_pred_execution": true,
      "status_sources": [
        {
          "record": "records/007_tolerance_tables.jsonl",
          "scope": "cs",
          "rule": "whole_match_level",
          "value": "仍不匹配",
          "007_prediction_database": "/home/katherine/Assumption_Ledger/data/005_cs_work/impl-016_parallel/node_results.duckdb"
        }
      ],
      "status": "待标注",
      "comparison_lookup_layer": "marts",
      "comparison_lookup_table": "workday__organization_overview",
      "actual_gold_relation_exists": true
    },
    "contract": {
      "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
      "blocks": [
        {
          "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
          "start_line": 2024,
          "end_line": 2230,
          "original_text": "    - name: workday__organization_overview\n      description: Executive-ready overview of each active organization with headcount, roles, tenure, mobility, risk, performance, diversity, compensation tiers, promotions, derived scores, recommendations, and data quality\n      grain: One row per active organization_id and source_relation\n      source_models:\n      - staging.stg_workday__organization (filtered to is_inactive = false)\n      - staging.stg_workday__worker_position_organization\n      - staging.stg_workday__organization_role_worker\n      - staging.stg_workday__organization_role\n      - mart.workday__employee_overview (filtered to organization_id != 'Unknown')\n      business_logic: '1) Filter organizations to active only and expose attributes and effective_start as the creation date. 2) Build worker–organization–role relationships by left joining worker positions to role-worker and role master on matching worker, role, source_relation, and organization_id. For each assignment: - assignment_status: ''Active Assignment'' if end date is null, else ''Former Assignment''. - assignment_duration_days: days between start and end; if end is null, days between start and current_date. - carry organization_role_id and organization_role_code from the role join. 3) Aggregate organization_employee_stats by (organization_id, source_relation): - total_employees_ever: distinct workers across all assignments. - current_active_employees: distinct workers with Active Assignment. - former_employees: distinct workers with Former Assignment. - total_positions_in_org: distinct positions across all assignments. - active_positions_count: distinct positions with Active Assignment. - new_assignments_last_year: distinct workers with start date in the last year relative to current_date. - departures_last_year: distinct workers with a non-null end date in the last year. - avg_current_tenure_days: average assignment_duration_days for Active Assignments. - avg_former_tenure_days: average assignment_duration_days for Former Assignments. - unique_organization_roles: distinct organization_role_id. - management_role_employees / director_role_employees / lead_role_employees: distinct workers where role code contains ''Manager'' / ''Director'' / ''Lead''. - last_new_assignment_date: most recent start date; last_departure_date: most recent end date. 4) Aggregate organization_performance_metrics from mart.workday__employee_overview by (organization_id, source_relation), excluding organization_id = ''Unknown'': - Averages over currently employed workers only: overall_employee_score and career_development_score rounded to 2 decimals; retention_stability_score rounded to 2 decimals; age rounded to 1 decimal. - Employee value segments: distinct workers by segment (''High Value - High Retention'', ''High Value - Flight Risk'', ''Stable - Development Needed'', ''Development Required''); no employment filter. - Risk distribution: distinct workers by employee_risk_level (High/Medium/Low); no employment filter. - Maturity segments: distinct employed workers where maturity contains ''New Hire'' / ''Junior'' / ''Experienced'' / ''Senior'' / ''Veteran''. - Diversity: distinct ethnicity_codes among employed; military_veterans_count is distinct employed workers flagged for military service. - Compensation tiers: distinct employed workers by compensation_tier (Entry/Mid/Senior/Executive Level). - Promotions among employed: total_promotions summed; high_achievers_count is distinct workers with total_promotions ≥ 2; fast_track_employees_count is distinct workers with fast_promotions > 0. 5) Derive organization attributes per active organization: - organization_created_date from effective_start. - organization_age_days as days from creation to current_date; organization_age_years is that divided by 365, rounded to 2 decimals. - organization_maturity_level by age_days: <1 year New; 1–3 years Young; 3–10 years Mature; 10+ years Legacy. - organizational_level from organization_type: Company/Division/Department/Team mapped to corresponding Level; others to Other Level. - access_level from visibility: Public→Open Access, Private→Restricted Access, others Unknown Access. 6) Final metrics and rules (rates rounded to 2 decimals; missing metrics default to 0 unless noted): - position_fill_rate (%) = current_active_employees ÷ total_positions × 100 when total_positions > 0, else 0. - annual_turnover_rate (%) = departures_last_year ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - avg_current_tenure_years and avg_former_tenure_years = respective average tenure days ÷ 365, rounded to 2; if no data, treated as 0. - management_ratio (%) = (management_role_employees + director_role_employees) ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - high_risk_employee_percentage (%) = high_risk_employees ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - organization_health_score (0–100) = sum of: performance (cap at 30% of average performance), turnover (25/20/15/10/5 by thresholds using annual_turnover_rate and zero departures case), development (cap at 20% of average career development), efficiency (15/12/9/6 by position_fill_rate thresholds), and risk (10/7/4/2 by high_risk_employee_percentage thresholds); final score rounded to 2 decimals. - performance_category uses a weighted composite with thresholds: Excellent if composite ≥ 80; else Good if ≥ 60; else Average if ≥ 40; otherwise Needs Improvement (weights and constants follow the detailed rules above). - organization_size_category by current_active_employees: 0 Empty; ≤5 Micro; ≤15 Small; ≤50 Medium; ≤200 Large; else Enterprise. - last_activity_date is the most recent assignment start; if none, use organization_created_date. - last_departure_date is the most recent assignment end; if none, use 1900-01-01. - management_recommendation (first match): if no active employees then review necessity; else if turnover > 30% then focus on retention; else if high-risk % > 25% then address risk; else if fill rate < 70% then improve staffing; else if average performance < 50 then enhance performance management; else if management_ratio > 40% then optimize structure; else maintain excellence. - data_quality_flag precedence: missing or blank organization name → ERROR; active employees exceed positions by more than 10 → WARNING; turnover rate > 100% → WARNING; negative age days → ERROR; otherwise VALID. - analysis_timestamp is the query execution timestamp. 7) Join logic: left join employee stats and performance metrics to active organizations on (organization_id, source_relation); missing measures default to 0. The final ordering is for presentation only and does not affect grain.'\n      columns:\n      - name: organization_id\n        data_type: VARCHAR\n        description: Organization identifier; join key to stats and metrics; one output row per active (organization_id, source_relation)\n        tests:\n        - not_null\n      - name: source_relation\n        data_type: VARCHAR\n        description: Source system code carried from staging and used in all joins\n        tests:\n        - not_null\n      - name: organization_name\n        data_type: VARCHAR\n        description: Organization display name from the active organization record\n      - name: organization_code\n        data_type: VARCHAR\n        description: Organization code from the active organization record\n      - name: organization_type\n        data_type: VARCHAR\n        description: Organization type (e.g., Company, Division, Department, Team)\n      - name: organization_sub_type\n        data_type: VARCHAR\n        description: Subtype of the organization if provided in source\n      - name: staffing_model\n        data_type: VARCHAR\n        description: Staffing model from source organization attributes\n      - name: visibility\n        data_type: VARCHAR\n        description: Visibility setting from source; drives access_level mapping\n      - name: access_level\n        data_type: VARCHAR\n        description: 'Derived access control: Public→Open Access, Private→Restricted Access, else Unknown Access'\n      - name: organization_created_date\n        data_type: DATE\n        description: Effective start date of the active organization record\n      - name: organization_age_days\n        data_type: BIGINT\n        description: Days since organization_created_date to current_date at run time\n      - name: organization_age_years\n        data_type: DOUBLE\n        description: Rounded years since creation = round(organization_age_days/365.0, 2)\n      - name: organization_maturity_level\n        data_type: VARCHAR\n        description: 'Age bucket: <1y New; 1–3y Young; 3–10y Mature; 10+y Legacy based on organization_age_days'\n      - name: organizational_level\n        data_type: VARCHAR\n        description: 'Level mapped from organization_type: Company/Division/Department/Team→Corporate/Division/Department/Team Level; else Other Level'\n      - name: total_employees_ever\n        data_type: BIGINT\n        description: Distinct workers ever assigned to the org; defaults to 0 when missing\n      - name: current_active_employees\n        data_type: BIGINT\n        description: Distinct workers with Active Assignment at run time; defaults to 0 when missing\n      - name: former_employees\n        data_type: BIGINT\n        description: Distinct workers with Former Assignment; defaults to 0 when missing\n      - name: total_positions\n        data_type: BIGINT\n        description: Distinct positions ever assigned within the org; defaults to 0 when missing\n      - name: active_positions_count\n        data_type: BIGINT\n        description: Distinct positions with Active Assignment; defaults to 0 when missing\n      - name: position_fill_rate\n        data_type: DOUBLE\n        description: Filled positions % = round(current_active_employees*100.0/total_positions, 2); 0 if total_positions=0\n      - name: new_assignments_last_year\n        data_type: BIGINT\n        description: Distinct workers with assignment start in the last year; defaults to 0 when missing\n      - name: departures_last_year\n        data_type: BIGINT\n        description: Distinct workers with non-null assignment end in the last year; defaults to 0 when missing\n      - name: annual_turnover_rate\n        data_type: DOUBLE\n        description: Departures % = round(departures_last_year*100.0/current_active_employees, 2); 0 if denominator=0\n      - name: avg_current_tenure_years\n        data_type: DOUBLE\n        description: Average tenure (years) for Active Assignments = round(avg_current_tenure_days/365.0, 2) with NULL→0\n      - name: avg_former_tenure_years\n        data_type: DOUBLE\n        description: Average tenure (years) for Former Assignments = round(avg_former_tenure_days/365.0, 2) with NULL→0\n      - name: unique_organization_roles\n        data_type: BIGINT\n        description: Distinct organization_role_id linked to the org; defaults to 0 when missing\n      - name: management_role_employees\n        data_type: BIGINT\n        description: Distinct workers with role code containing 'Manager'; defaults to 0 when missing\n      - name: director_role_employees\n        data_type: BIGINT\n        description: Distinct workers with role code containing 'Director'; defaults to 0 when missing\n      - name: lead_role_employees\n        data_type: BIGINT\n        description: Distinct workers with role code containing 'Lead'; defaults to 0 when missing\n      - name: management_ratio\n        data_type: DOUBLE\n        description: Management share % = round((management_role_employees+director_role_employees)*100.0/current_active_employees, 2); 0 if denominator=0\n      - name: avg_employee_performance_score\n        data_type: DOUBLE\n        description: Avg overall_employee_score among employed, rounded to 2; defaults to 0 when missing; 0–100 scale preserved\n      - name: avg_career_development_score\n        data_type: DOUBLE\n        description: Avg career_development_score among employed, rounded to 2; defaults to 0 when missing; 0–100 scale preserved\n      - name: avg_retention_stability_score\n        data_type: DOUBLE\n        description: Avg retention_stability_score among employed, rounded to 2; defaults to 0 when missing; 0–100 scale preserved\n      - name: high_value_stable_employees\n        data_type: BIGINT\n        description: Distinct workers in 'High Value - High Retention'; defaults to 0 when missing\n      - name: high_value_flight_risk_employees\n        data_type: BIGINT\n        description: Distinct workers in 'High Value - Flight Risk'; defaults to 0 when missing\n      - name: stable_development_employees\n        data_type: BIGINT\n        description: Distinct workers in 'Stable - Development Needed'; defaults to 0 when missing\n      - name: development_required_employees\n        data_type: BIGINT\n        description: Distinct workers in 'Development Required'; defaults to 0 when missing\n      - name: high_risk_employees\n        data_type: BIGINT\n        description: Distinct workers with employee_risk_level = 'High Risk'; defaults to 0 when missing\n      - name: medium_risk_employees\n        data_type: BIGINT\n        description: Distinct workers with employee_risk_level = 'Medium Risk'; defaults to 0 when missing\n      - name: low_risk_employees\n        data_type: BIGINT\n        description: Distinct workers with employee_risk_level = 'Low Risk'; defaults to 0 when missing\n      - name: high_risk_employee_percentage\n        data_type: DOUBLE\n        description: High-risk share % = round(high_risk_employees*100.0/current_active_employees, 2); 0 if denominator=0\n      - name: new_hire_employees\n        data_type: BIGINT\n        description: Distinct employed workers with maturity containing 'New Hire'; defaults to 0 when missing\n      - name: junior_employees\n        data_type: BIGINT\n        description: Distinct employed workers with maturity containing 'Junior'; defaults to 0 when missing\n      - name: experienced_employees\n        data_type: BIGINT\n        description: Distinct employed workers with maturity containing 'Experienced'; defaults to 0 when missing\n      - name: senior_employees\n        data_type: BIGINT\n        description: Distinct employed workers with maturity containing 'Senior'; defaults to 0 when missing\n      - name: veteran_employees\n        data_type: BIGINT\n        description: Distinct employed workers with maturity containing 'Veteran'; defaults to 0 when missing\n      - name: ethnic_diversity_count\n        data_type: BIGINT\n        description: Count of distinct ethnicity_codes among employed; defaults to 0 when missing\n      - name: military_veterans_count\n        data_type: BIGINT\n        description: Distinct employed workers with military service flag; defaults to 0 when missing\n      - name: avg_employee_age\n        data_type: DOUBLE\n        description: Average age among employed, rounded to 1 in source aggregation; defaults to 0 when missing\n      - name: entry_level_employees\n        data_type: BIGINT\n        description: Distinct employed workers in compensation_tier = 'Entry Level'; defaults to 0 when missing\n      - name: mid_level_employees\n        data_type: BIGINT\n        description: Distinct employed workers in compensation_tier = 'Mid Level'; defaults to 0 when missing\n      - name: senior_level_employees\n        data_type: BIGINT\n        description: Distinct employed workers in compensation_tier = 'Senior Level'; defaults to 0 when missing\n      - name: executive_level_employees\n        data_type: BIGINT\n        description: Distinct employed workers in compensation_tier = 'Executive Level'; defaults to 0 when missing\n      - name: total_promotions_in_organization\n        data_type: HUGEINT\n        description: Sum of total_promotions for employed workers in the org; defaults to 0 when missing\n      - name: high_achievers_count\n        data_type: BIGINT\n        description: Distinct employed workers with total_promotions >= 2; defaults to 0 when missing\n      - name: fast_track_employees_count\n        data_type: BIGINT\n        description: Distinct employed workers with fast_promotions > 0; defaults to 0 when missing\n      - name: organization_health_score\n        data_type: DOUBLE\n        description: Composite 0–100 score from performance, turnover, development, fill-rate efficiency, and risk components; rounded to 2\n      - name: performance_category\n        data_type: VARCHAR\n        description: 'Category from the weighted composite: Excellent (>=80), Good (>=60), Average (>=40), else Needs Improvement'\n      - name: organization_size_category\n        data_type: VARCHAR\n        description: 'Size bucket by current_active_employees: Empty, Micro (<=5), Small (<=15), Medium (<=50), Large (<=200), Enterprise (>200)'\n      - name: last_activity_date\n        data_type: DATE\n        description: Most recent assignment start date; if none, falls back to organization_created_date\n      - name: last_departure_date\n        data_type: DATE\n        description: Most recent assignment end date; if none, defaults to 1900-01-01\n      - name: management_recommendation\n        data_type: VARCHAR\n        description: Recommendation based on thresholds of size, turnover, high-risk %, fill rate, performance, and management ratio; first matching rule applies\n      - name: data_quality_flag\n        data_type: VARCHAR\n        description: VALID or specific ERROR/WARNING based on missing name, employee>position anomaly, turnover >100%, or negative age days\n      - name: analysis_timestamp\n        data_type: TIMESTAMP WITH TIME ZONE\n        description: current_timestamp at run time indicating when the analysis was computed\n",
          "yaml_path": [
            "modeling_spec",
            "marts_models",
            4
          ]
        }
      ]
    },
    "output": {
      "status": "checked",
      "exists": true,
      "row_count": 117,
      "zero_rows": false,
      "columns": [
        {
          "name": "organization_id",
          "type": "VARCHAR",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "source_relation",
          "type": "VARCHAR",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "organization_name",
          "type": "VARCHAR",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "organization_code",
          "type": "VARCHAR",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "organization_type",
          "type": "VARCHAR",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "organization_sub_type",
          "type": "VARCHAR",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "staffing_model",
          "type": "VARCHAR",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "visibility",
          "type": "VARCHAR",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "access_level",
          "type": "VARCHAR",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "organization_created_date",
          "type": "DATE",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "organization_age_days",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "organization_age_years",
          "type": "DOUBLE",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "organization_maturity_level",
          "type": "VARCHAR",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "organizational_level",
          "type": "VARCHAR",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "total_employees_ever",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "current_active_employees",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "former_employees",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "total_positions",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "active_positions_count",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "position_fill_rate",
          "type": "DOUBLE",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "new_assignments_last_year",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "departures_last_year",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "annual_turnover_rate",
          "type": "DOUBLE",
          "nonnull_rows": 0,
          "sql_null_rows": 117
        },
        {
          "name": "avg_current_tenure_years",
          "type": "DOUBLE",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "avg_former_tenure_years",
          "type": "DOUBLE",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "unique_organization_roles",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "management_role_employees",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "director_role_employees",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "lead_role_employees",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "management_ratio",
          "type": "DOUBLE",
          "nonnull_rows": 0,
          "sql_null_rows": 117
        },
        {
          "name": "avg_employee_performance_score",
          "type": "DOUBLE",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "avg_career_development_score",
          "type": "DOUBLE",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "avg_retention_stability_score",
          "type": "DOUBLE",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "high_value_stable_employees",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "high_value_flight_risk_employees",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "stable_development_employees",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "development_required_employees",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "high_risk_employees",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "medium_risk_employees",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "low_risk_employees",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "high_risk_employee_percentage",
          "type": "DOUBLE",
          "nonnull_rows": 0,
          "sql_null_rows": 117
        },
        {
          "name": "new_hire_employees",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "junior_employees",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "experienced_employees",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "senior_employees",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "veteran_employees",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "ethnic_diversity_count",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "military_veterans_count",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "avg_employee_age",
          "type": "DOUBLE",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "entry_level_employees",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "mid_level_employees",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "senior_level_employees",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "executive_level_employees",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "total_promotions_in_organization",
          "type": "HUGEINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "high_achievers_count",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "fast_track_employees_count",
          "type": "BIGINT",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "organization_health_score",
          "type": "DOUBLE",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "performance_category",
          "type": "VARCHAR",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "organization_size_category",
          "type": "VARCHAR",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "last_activity_date",
          "type": "DATE",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "last_departure_date",
          "type": "DATE",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "management_recommendation",
          "type": "VARCHAR",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "data_quality_flag",
          "type": "VARCHAR",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        },
        {
          "name": "analysis_timestamp",
          "type": "TIMESTAMP WITH TIME ZONE",
          "nonnull_rows": 117,
          "sql_null_rows": 0
        }
      ],
      "all_null_columns": [
        {
          "column": "annual_turnover_rate",
          "table_rows": 117
        },
        {
          "column": "management_ratio",
          "table_rows": 117
        },
        {
          "column": "high_risk_employee_percentage",
          "table_rows": 117
        }
      ],
      "constant_nonnull_columns": [
        {
          "column": "source_relation",
          "type": "VARCHAR",
          "value": "workday",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2040,
                "end_line": 2044,
                "original_text": "      - name: source_relation\n        data_type: VARCHAR\n        description: Source system code carried from staging and used in all joins\n        tests:\n        - not_null\n",
                "name": "source_relation",
                "description": "Source system code carried from staging and used in all joins",
                "specification": {
                  "name": "source_relation",
                  "data_type": "VARCHAR",
                  "description": "Source system code carried from staging and used in all joins",
                  "tests": [
                    "not_null"
                  ]
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "current_active_employees",
          "type": "BIGINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2084,
                "end_line": 2086,
                "original_text": "      - name: current_active_employees\n        data_type: BIGINT\n        description: Distinct workers with Active Assignment at run time; defaults to 0 when missing\n",
                "name": "current_active_employees",
                "description": "Distinct workers with Active Assignment at run time; defaults to 0 when missing",
                "specification": {
                  "name": "current_active_employees",
                  "data_type": "BIGINT",
                  "description": "Distinct workers with Active Assignment at run time; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "active_positions_count",
          "type": "BIGINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2093,
                "end_line": 2095,
                "original_text": "      - name: active_positions_count\n        data_type: BIGINT\n        description: Distinct positions with Active Assignment; defaults to 0 when missing\n",
                "name": "active_positions_count",
                "description": "Distinct positions with Active Assignment; defaults to 0 when missing",
                "specification": {
                  "name": "active_positions_count",
                  "data_type": "BIGINT",
                  "description": "Distinct positions with Active Assignment; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "position_fill_rate",
          "type": "DOUBLE",
          "value": "0.0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2096,
                "end_line": 2098,
                "original_text": "      - name: position_fill_rate\n        data_type: DOUBLE\n        description: Filled positions % = round(current_active_employees*100.0/total_positions, 2); 0 if total_positions=0\n",
                "name": "position_fill_rate",
                "description": "Filled positions % = round(current_active_employees*100.0/total_positions, 2); 0 if total_positions=0",
                "specification": {
                  "name": "position_fill_rate",
                  "data_type": "DOUBLE",
                  "description": "Filled positions % = round(current_active_employees*100.0/total_positions, 2); 0 if total_positions=0"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "new_assignments_last_year",
          "type": "BIGINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2099,
                "end_line": 2101,
                "original_text": "      - name: new_assignments_last_year\n        data_type: BIGINT\n        description: Distinct workers with assignment start in the last year; defaults to 0 when missing\n",
                "name": "new_assignments_last_year",
                "description": "Distinct workers with assignment start in the last year; defaults to 0 when missing",
                "specification": {
                  "name": "new_assignments_last_year",
                  "data_type": "BIGINT",
                  "description": "Distinct workers with assignment start in the last year; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "departures_last_year",
          "type": "BIGINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2102,
                "end_line": 2104,
                "original_text": "      - name: departures_last_year\n        data_type: BIGINT\n        description: Distinct workers with non-null assignment end in the last year; defaults to 0 when missing\n",
                "name": "departures_last_year",
                "description": "Distinct workers with non-null assignment end in the last year; defaults to 0 when missing",
                "specification": {
                  "name": "departures_last_year",
                  "data_type": "BIGINT",
                  "description": "Distinct workers with non-null assignment end in the last year; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "avg_current_tenure_years",
          "type": "DOUBLE",
          "value": "0.0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2108,
                "end_line": 2110,
                "original_text": "      - name: avg_current_tenure_years\n        data_type: DOUBLE\n        description: Average tenure (years) for Active Assignments = round(avg_current_tenure_days/365.0, 2) with NULL→0\n",
                "name": "avg_current_tenure_years",
                "description": "Average tenure (years) for Active Assignments = round(avg_current_tenure_days/365.0, 2) with NULL→0",
                "specification": {
                  "name": "avg_current_tenure_years",
                  "data_type": "DOUBLE",
                  "description": "Average tenure (years) for Active Assignments = round(avg_current_tenure_days/365.0, 2) with NULL→0"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "management_role_employees",
          "type": "BIGINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2117,
                "end_line": 2119,
                "original_text": "      - name: management_role_employees\n        data_type: BIGINT\n        description: Distinct workers with role code containing 'Manager'; defaults to 0 when missing\n",
                "name": "management_role_employees",
                "description": "Distinct workers with role code containing 'Manager'; defaults to 0 when missing",
                "specification": {
                  "name": "management_role_employees",
                  "data_type": "BIGINT",
                  "description": "Distinct workers with role code containing 'Manager'; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "director_role_employees",
          "type": "BIGINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2120,
                "end_line": 2122,
                "original_text": "      - name: director_role_employees\n        data_type: BIGINT\n        description: Distinct workers with role code containing 'Director'; defaults to 0 when missing\n",
                "name": "director_role_employees",
                "description": "Distinct workers with role code containing 'Director'; defaults to 0 when missing",
                "specification": {
                  "name": "director_role_employees",
                  "data_type": "BIGINT",
                  "description": "Distinct workers with role code containing 'Director'; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "lead_role_employees",
          "type": "BIGINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2123,
                "end_line": 2125,
                "original_text": "      - name: lead_role_employees\n        data_type: BIGINT\n        description: Distinct workers with role code containing 'Lead'; defaults to 0 when missing\n",
                "name": "lead_role_employees",
                "description": "Distinct workers with role code containing 'Lead'; defaults to 0 when missing",
                "specification": {
                  "name": "lead_role_employees",
                  "data_type": "BIGINT",
                  "description": "Distinct workers with role code containing 'Lead'; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "avg_employee_performance_score",
          "type": "DOUBLE",
          "value": "0.0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2129,
                "end_line": 2131,
                "original_text": "      - name: avg_employee_performance_score\n        data_type: DOUBLE\n        description: Avg overall_employee_score among employed, rounded to 2; defaults to 0 when missing; 0–100 scale preserved\n",
                "name": "avg_employee_performance_score",
                "description": "Avg overall_employee_score among employed, rounded to 2; defaults to 0 when missing; 0–100 scale preserved",
                "specification": {
                  "name": "avg_employee_performance_score",
                  "data_type": "DOUBLE",
                  "description": "Avg overall_employee_score among employed, rounded to 2; defaults to 0 when missing; 0–100 scale preserved"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "avg_career_development_score",
          "type": "DOUBLE",
          "value": "0.0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2132,
                "end_line": 2134,
                "original_text": "      - name: avg_career_development_score\n        data_type: DOUBLE\n        description: Avg career_development_score among employed, rounded to 2; defaults to 0 when missing; 0–100 scale preserved\n",
                "name": "avg_career_development_score",
                "description": "Avg career_development_score among employed, rounded to 2; defaults to 0 when missing; 0–100 scale preserved",
                "specification": {
                  "name": "avg_career_development_score",
                  "data_type": "DOUBLE",
                  "description": "Avg career_development_score among employed, rounded to 2; defaults to 0 when missing; 0–100 scale preserved"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "avg_retention_stability_score",
          "type": "DOUBLE",
          "value": "0.0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2135,
                "end_line": 2137,
                "original_text": "      - name: avg_retention_stability_score\n        data_type: DOUBLE\n        description: Avg retention_stability_score among employed, rounded to 2; defaults to 0 when missing; 0–100 scale preserved\n",
                "name": "avg_retention_stability_score",
                "description": "Avg retention_stability_score among employed, rounded to 2; defaults to 0 when missing; 0–100 scale preserved",
                "specification": {
                  "name": "avg_retention_stability_score",
                  "data_type": "DOUBLE",
                  "description": "Avg retention_stability_score among employed, rounded to 2; defaults to 0 when missing; 0–100 scale preserved"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "high_value_stable_employees",
          "type": "BIGINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2138,
                "end_line": 2140,
                "original_text": "      - name: high_value_stable_employees\n        data_type: BIGINT\n        description: Distinct workers in 'High Value - High Retention'; defaults to 0 when missing\n",
                "name": "high_value_stable_employees",
                "description": "Distinct workers in 'High Value - High Retention'; defaults to 0 when missing",
                "specification": {
                  "name": "high_value_stable_employees",
                  "data_type": "BIGINT",
                  "description": "Distinct workers in 'High Value - High Retention'; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "high_value_flight_risk_employees",
          "type": "BIGINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2141,
                "end_line": 2143,
                "original_text": "      - name: high_value_flight_risk_employees\n        data_type: BIGINT\n        description: Distinct workers in 'High Value - Flight Risk'; defaults to 0 when missing\n",
                "name": "high_value_flight_risk_employees",
                "description": "Distinct workers in 'High Value - Flight Risk'; defaults to 0 when missing",
                "specification": {
                  "name": "high_value_flight_risk_employees",
                  "data_type": "BIGINT",
                  "description": "Distinct workers in 'High Value - Flight Risk'; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "stable_development_employees",
          "type": "BIGINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2144,
                "end_line": 2146,
                "original_text": "      - name: stable_development_employees\n        data_type: BIGINT\n        description: Distinct workers in 'Stable - Development Needed'; defaults to 0 when missing\n",
                "name": "stable_development_employees",
                "description": "Distinct workers in 'Stable - Development Needed'; defaults to 0 when missing",
                "specification": {
                  "name": "stable_development_employees",
                  "data_type": "BIGINT",
                  "description": "Distinct workers in 'Stable - Development Needed'; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "development_required_employees",
          "type": "BIGINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2147,
                "end_line": 2149,
                "original_text": "      - name: development_required_employees\n        data_type: BIGINT\n        description: Distinct workers in 'Development Required'; defaults to 0 when missing\n",
                "name": "development_required_employees",
                "description": "Distinct workers in 'Development Required'; defaults to 0 when missing",
                "specification": {
                  "name": "development_required_employees",
                  "data_type": "BIGINT",
                  "description": "Distinct workers in 'Development Required'; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "high_risk_employees",
          "type": "BIGINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2150,
                "end_line": 2152,
                "original_text": "      - name: high_risk_employees\n        data_type: BIGINT\n        description: Distinct workers with employee_risk_level = 'High Risk'; defaults to 0 when missing\n",
                "name": "high_risk_employees",
                "description": "Distinct workers with employee_risk_level = 'High Risk'; defaults to 0 when missing",
                "specification": {
                  "name": "high_risk_employees",
                  "data_type": "BIGINT",
                  "description": "Distinct workers with employee_risk_level = 'High Risk'; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "medium_risk_employees",
          "type": "BIGINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2153,
                "end_line": 2155,
                "original_text": "      - name: medium_risk_employees\n        data_type: BIGINT\n        description: Distinct workers with employee_risk_level = 'Medium Risk'; defaults to 0 when missing\n",
                "name": "medium_risk_employees",
                "description": "Distinct workers with employee_risk_level = 'Medium Risk'; defaults to 0 when missing",
                "specification": {
                  "name": "medium_risk_employees",
                  "data_type": "BIGINT",
                  "description": "Distinct workers with employee_risk_level = 'Medium Risk'; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "low_risk_employees",
          "type": "BIGINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2156,
                "end_line": 2158,
                "original_text": "      - name: low_risk_employees\n        data_type: BIGINT\n        description: Distinct workers with employee_risk_level = 'Low Risk'; defaults to 0 when missing\n",
                "name": "low_risk_employees",
                "description": "Distinct workers with employee_risk_level = 'Low Risk'; defaults to 0 when missing",
                "specification": {
                  "name": "low_risk_employees",
                  "data_type": "BIGINT",
                  "description": "Distinct workers with employee_risk_level = 'Low Risk'; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "new_hire_employees",
          "type": "BIGINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2162,
                "end_line": 2164,
                "original_text": "      - name: new_hire_employees\n        data_type: BIGINT\n        description: Distinct employed workers with maturity containing 'New Hire'; defaults to 0 when missing\n",
                "name": "new_hire_employees",
                "description": "Distinct employed workers with maturity containing 'New Hire'; defaults to 0 when missing",
                "specification": {
                  "name": "new_hire_employees",
                  "data_type": "BIGINT",
                  "description": "Distinct employed workers with maturity containing 'New Hire'; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "junior_employees",
          "type": "BIGINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2165,
                "end_line": 2167,
                "original_text": "      - name: junior_employees\n        data_type: BIGINT\n        description: Distinct employed workers with maturity containing 'Junior'; defaults to 0 when missing\n",
                "name": "junior_employees",
                "description": "Distinct employed workers with maturity containing 'Junior'; defaults to 0 when missing",
                "specification": {
                  "name": "junior_employees",
                  "data_type": "BIGINT",
                  "description": "Distinct employed workers with maturity containing 'Junior'; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "experienced_employees",
          "type": "BIGINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2168,
                "end_line": 2170,
                "original_text": "      - name: experienced_employees\n        data_type: BIGINT\n        description: Distinct employed workers with maturity containing 'Experienced'; defaults to 0 when missing\n",
                "name": "experienced_employees",
                "description": "Distinct employed workers with maturity containing 'Experienced'; defaults to 0 when missing",
                "specification": {
                  "name": "experienced_employees",
                  "data_type": "BIGINT",
                  "description": "Distinct employed workers with maturity containing 'Experienced'; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "senior_employees",
          "type": "BIGINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2171,
                "end_line": 2173,
                "original_text": "      - name: senior_employees\n        data_type: BIGINT\n        description: Distinct employed workers with maturity containing 'Senior'; defaults to 0 when missing\n",
                "name": "senior_employees",
                "description": "Distinct employed workers with maturity containing 'Senior'; defaults to 0 when missing",
                "specification": {
                  "name": "senior_employees",
                  "data_type": "BIGINT",
                  "description": "Distinct employed workers with maturity containing 'Senior'; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "veteran_employees",
          "type": "BIGINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2174,
                "end_line": 2176,
                "original_text": "      - name: veteran_employees\n        data_type: BIGINT\n        description: Distinct employed workers with maturity containing 'Veteran'; defaults to 0 when missing\n",
                "name": "veteran_employees",
                "description": "Distinct employed workers with maturity containing 'Veteran'; defaults to 0 when missing",
                "specification": {
                  "name": "veteran_employees",
                  "data_type": "BIGINT",
                  "description": "Distinct employed workers with maturity containing 'Veteran'; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "ethnic_diversity_count",
          "type": "BIGINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2177,
                "end_line": 2179,
                "original_text": "      - name: ethnic_diversity_count\n        data_type: BIGINT\n        description: Count of distinct ethnicity_codes among employed; defaults to 0 when missing\n",
                "name": "ethnic_diversity_count",
                "description": "Count of distinct ethnicity_codes among employed; defaults to 0 when missing",
                "specification": {
                  "name": "ethnic_diversity_count",
                  "data_type": "BIGINT",
                  "description": "Count of distinct ethnicity_codes among employed; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "military_veterans_count",
          "type": "BIGINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2180,
                "end_line": 2182,
                "original_text": "      - name: military_veterans_count\n        data_type: BIGINT\n        description: Distinct employed workers with military service flag; defaults to 0 when missing\n",
                "name": "military_veterans_count",
                "description": "Distinct employed workers with military service flag; defaults to 0 when missing",
                "specification": {
                  "name": "military_veterans_count",
                  "data_type": "BIGINT",
                  "description": "Distinct employed workers with military service flag; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "avg_employee_age",
          "type": "DOUBLE",
          "value": "0.0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2183,
                "end_line": 2185,
                "original_text": "      - name: avg_employee_age\n        data_type: DOUBLE\n        description: Average age among employed, rounded to 1 in source aggregation; defaults to 0 when missing\n",
                "name": "avg_employee_age",
                "description": "Average age among employed, rounded to 1 in source aggregation; defaults to 0 when missing",
                "specification": {
                  "name": "avg_employee_age",
                  "data_type": "DOUBLE",
                  "description": "Average age among employed, rounded to 1 in source aggregation; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "entry_level_employees",
          "type": "BIGINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2186,
                "end_line": 2188,
                "original_text": "      - name: entry_level_employees\n        data_type: BIGINT\n        description: Distinct employed workers in compensation_tier = 'Entry Level'; defaults to 0 when missing\n",
                "name": "entry_level_employees",
                "description": "Distinct employed workers in compensation_tier = 'Entry Level'; defaults to 0 when missing",
                "specification": {
                  "name": "entry_level_employees",
                  "data_type": "BIGINT",
                  "description": "Distinct employed workers in compensation_tier = 'Entry Level'; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "mid_level_employees",
          "type": "BIGINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2189,
                "end_line": 2191,
                "original_text": "      - name: mid_level_employees\n        data_type: BIGINT\n        description: Distinct employed workers in compensation_tier = 'Mid Level'; defaults to 0 when missing\n",
                "name": "mid_level_employees",
                "description": "Distinct employed workers in compensation_tier = 'Mid Level'; defaults to 0 when missing",
                "specification": {
                  "name": "mid_level_employees",
                  "data_type": "BIGINT",
                  "description": "Distinct employed workers in compensation_tier = 'Mid Level'; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "senior_level_employees",
          "type": "BIGINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2192,
                "end_line": 2194,
                "original_text": "      - name: senior_level_employees\n        data_type: BIGINT\n        description: Distinct employed workers in compensation_tier = 'Senior Level'; defaults to 0 when missing\n",
                "name": "senior_level_employees",
                "description": "Distinct employed workers in compensation_tier = 'Senior Level'; defaults to 0 when missing",
                "specification": {
                  "name": "senior_level_employees",
                  "data_type": "BIGINT",
                  "description": "Distinct employed workers in compensation_tier = 'Senior Level'; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "executive_level_employees",
          "type": "BIGINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2195,
                "end_line": 2197,
                "original_text": "      - name: executive_level_employees\n        data_type: BIGINT\n        description: Distinct employed workers in compensation_tier = 'Executive Level'; defaults to 0 when missing\n",
                "name": "executive_level_employees",
                "description": "Distinct employed workers in compensation_tier = 'Executive Level'; defaults to 0 when missing",
                "specification": {
                  "name": "executive_level_employees",
                  "data_type": "BIGINT",
                  "description": "Distinct employed workers in compensation_tier = 'Executive Level'; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "total_promotions_in_organization",
          "type": "HUGEINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2198,
                "end_line": 2200,
                "original_text": "      - name: total_promotions_in_organization\n        data_type: HUGEINT\n        description: Sum of total_promotions for employed workers in the org; defaults to 0 when missing\n",
                "name": "total_promotions_in_organization",
                "description": "Sum of total_promotions for employed workers in the org; defaults to 0 when missing",
                "specification": {
                  "name": "total_promotions_in_organization",
                  "data_type": "HUGEINT",
                  "description": "Sum of total_promotions for employed workers in the org; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "high_achievers_count",
          "type": "BIGINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2201,
                "end_line": 2203,
                "original_text": "      - name: high_achievers_count\n        data_type: BIGINT\n        description: Distinct employed workers with total_promotions >= 2; defaults to 0 when missing\n",
                "name": "high_achievers_count",
                "description": "Distinct employed workers with total_promotions >= 2; defaults to 0 when missing",
                "specification": {
                  "name": "high_achievers_count",
                  "data_type": "BIGINT",
                  "description": "Distinct employed workers with total_promotions >= 2; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "fast_track_employees_count",
          "type": "BIGINT",
          "value": "0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2204,
                "end_line": 2206,
                "original_text": "      - name: fast_track_employees_count\n        data_type: BIGINT\n        description: Distinct employed workers with fast_promotions > 0; defaults to 0 when missing\n",
                "name": "fast_track_employees_count",
                "description": "Distinct employed workers with fast_promotions > 0; defaults to 0 when missing",
                "specification": {
                  "name": "fast_track_employees_count",
                  "data_type": "BIGINT",
                  "description": "Distinct employed workers with fast_promotions > 0; defaults to 0 when missing"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "organization_health_score",
          "type": "DOUBLE",
          "value": "33.0",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2207,
                "end_line": 2209,
                "original_text": "      - name: organization_health_score\n        data_type: DOUBLE\n        description: Composite 0–100 score from performance, turnover, development, fill-rate efficiency, and risk components; rounded to 2\n",
                "name": "organization_health_score",
                "description": "Composite 0–100 score from performance, turnover, development, fill-rate efficiency, and risk components; rounded to 2",
                "specification": {
                  "name": "organization_health_score",
                  "data_type": "DOUBLE",
                  "description": "Composite 0–100 score from performance, turnover, development, fill-rate efficiency, and risk components; rounded to 2"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "performance_category",
          "type": "VARCHAR",
          "value": "Needs Improvement",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2210,
                "end_line": 2212,
                "original_text": "      - name: performance_category\n        data_type: VARCHAR\n        description: 'Category from the weighted composite: Excellent (>=80), Good (>=60), Average (>=40), else Needs Improvement'\n",
                "name": "performance_category",
                "description": "Category from the weighted composite: Excellent (>=80), Good (>=60), Average (>=40), else Needs Improvement",
                "specification": {
                  "name": "performance_category",
                  "data_type": "VARCHAR",
                  "description": "Category from the weighted composite: Excellent (>=80), Good (>=60), Average (>=40), else Needs Improvement"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "organization_size_category",
          "type": "VARCHAR",
          "value": "Empty",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2213,
                "end_line": 2215,
                "original_text": "      - name: organization_size_category\n        data_type: VARCHAR\n        description: 'Size bucket by current_active_employees: Empty, Micro (<=5), Small (<=15), Medium (<=50), Large (<=200), Enterprise (>200)'\n",
                "name": "organization_size_category",
                "description": "Size bucket by current_active_employees: Empty, Micro (<=5), Small (<=15), Medium (<=50), Large (<=200), Enterprise (>200)",
                "specification": {
                  "name": "organization_size_category",
                  "data_type": "VARCHAR",
                  "description": "Size bucket by current_active_employees: Empty, Micro (<=5), Small (<=15), Medium (<=50), Large (<=200), Enterprise (>200)"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "last_departure_date",
          "type": "DATE",
          "value": "2025-09-05",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2219,
                "end_line": 2221,
                "original_text": "      - name: last_departure_date\n        data_type: DATE\n        description: Most recent assignment end date; if none, defaults to 1900-01-01\n",
                "name": "last_departure_date",
                "description": "Most recent assignment end date; if none, defaults to 1900-01-01",
                "specification": {
                  "name": "last_departure_date",
                  "data_type": "DATE",
                  "description": "Most recent assignment end date; if none, defaults to 1900-01-01"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "management_recommendation",
          "type": "VARCHAR",
          "value": "Review Organization Necessity",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2222,
                "end_line": 2224,
                "original_text": "      - name: management_recommendation\n        data_type: VARCHAR\n        description: Recommendation based on thresholds of size, turnover, high-risk %, fill rate, performance, and management ratio; first matching rule applies\n",
                "name": "management_recommendation",
                "description": "Recommendation based on thresholds of size, turnover, high-risk %, fill rate, performance, and management ratio; first matching rule applies",
                "specification": {
                  "name": "management_recommendation",
                  "data_type": "VARCHAR",
                  "description": "Recommendation based on thresholds of size, turnover, high-risk %, fill rate, performance, and management ratio; first matching rule applies"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "data_quality_flag",
          "type": "VARCHAR",
          "value": "VALID",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2225,
                "end_line": 2227,
                "original_text": "      - name: data_quality_flag\n        data_type: VARCHAR\n        description: VALID or specific ERROR/WARNING based on missing name, employee>position anomaly, turnover >100%, or negative age days\n",
                "name": "data_quality_flag",
                "description": "VALID or specific ERROR/WARNING based on missing name, employee>position anomaly, turnover >100%, or negative age days",
                "specification": {
                  "name": "data_quality_flag",
                  "data_type": "VARCHAR",
                  "description": "VALID or specific ERROR/WARNING based on missing name, employee>position anomaly, turnover >100%, or negative age days"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        },
        {
          "column": "analysis_timestamp",
          "type": "TIMESTAMP WITH TIME ZONE",
          "value": "2026-10-25 03:10:42.286291+08",
          "value_representation": "DuckDB CAST AS VARCHAR, exact, no normalization",
          "table_rows": 117,
          "contract": {
            "status": "found",
            "definitions": [
              {
                "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                "start_line": 2228,
                "end_line": 2230,
                "original_text": "      - name: analysis_timestamp\n        data_type: TIMESTAMP WITH TIME ZONE\n        description: current_timestamp at run time indicating when the analysis was computed\n",
                "name": "analysis_timestamp",
                "description": "current_timestamp at run time indicating when the analysis was computed",
                "specification": {
                  "name": "analysis_timestamp",
                  "data_type": "TIMESTAMP WITH TIME ZONE",
                  "description": "current_timestamp at run time indicating when the analysis was computed"
                }
              }
            ],
            "meaning_description_status": "explicit_description"
          }
        }
      ],
      "equal_column_groups": [
        {
          "columns": [
            "total_employees_ever",
            "former_employees"
          ],
          "table_rows": 117,
          "nonnull_equal_rows": 117,
          "both_null_rows_ignored": 0,
          "mismatch_rows": 0,
          "column_contracts": {
            "total_employees_ever": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2081,
                  "end_line": 2083,
                  "original_text": "      - name: total_employees_ever\n        data_type: BIGINT\n        description: Distinct workers ever assigned to the org; defaults to 0 when missing\n",
                  "name": "total_employees_ever",
                  "description": "Distinct workers ever assigned to the org; defaults to 0 when missing",
                  "specification": {
                    "name": "total_employees_ever",
                    "data_type": "BIGINT",
                    "description": "Distinct workers ever assigned to the org; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "former_employees": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2087,
                  "end_line": 2089,
                  "original_text": "      - name: former_employees\n        data_type: BIGINT\n        description: Distinct workers with Former Assignment; defaults to 0 when missing\n",
                  "name": "former_employees",
                  "description": "Distinct workers with Former Assignment; defaults to 0 when missing",
                  "specification": {
                    "name": "former_employees",
                    "data_type": "BIGINT",
                    "description": "Distinct workers with Former Assignment; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            }
          },
          "description_pairs": [
            {
              "left": "total_employees_ever",
              "right": "former_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            }
          ],
          "has_pair_with_different_explicit_description": true,
          "meaning_status": "description_texts_differ_no_semantic_judgment"
        },
        {
          "columns": [
            "current_active_employees",
            "active_positions_count",
            "new_assignments_last_year",
            "departures_last_year",
            "management_role_employees",
            "director_role_employees",
            "lead_role_employees",
            "high_value_stable_employees",
            "high_value_flight_risk_employees",
            "stable_development_employees",
            "development_required_employees",
            "high_risk_employees",
            "medium_risk_employees",
            "low_risk_employees",
            "new_hire_employees",
            "junior_employees",
            "experienced_employees",
            "senior_employees",
            "veteran_employees",
            "ethnic_diversity_count",
            "military_veterans_count",
            "entry_level_employees",
            "mid_level_employees",
            "senior_level_employees",
            "executive_level_employees",
            "total_promotions_in_organization",
            "high_achievers_count",
            "fast_track_employees_count"
          ],
          "table_rows": 117,
          "nonnull_equal_rows": 117,
          "both_null_rows_ignored": 0,
          "mismatch_rows": 0,
          "column_contracts": {
            "current_active_employees": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2084,
                  "end_line": 2086,
                  "original_text": "      - name: current_active_employees\n        data_type: BIGINT\n        description: Distinct workers with Active Assignment at run time; defaults to 0 when missing\n",
                  "name": "current_active_employees",
                  "description": "Distinct workers with Active Assignment at run time; defaults to 0 when missing",
                  "specification": {
                    "name": "current_active_employees",
                    "data_type": "BIGINT",
                    "description": "Distinct workers with Active Assignment at run time; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "active_positions_count": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2093,
                  "end_line": 2095,
                  "original_text": "      - name: active_positions_count\n        data_type: BIGINT\n        description: Distinct positions with Active Assignment; defaults to 0 when missing\n",
                  "name": "active_positions_count",
                  "description": "Distinct positions with Active Assignment; defaults to 0 when missing",
                  "specification": {
                    "name": "active_positions_count",
                    "data_type": "BIGINT",
                    "description": "Distinct positions with Active Assignment; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "new_assignments_last_year": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2099,
                  "end_line": 2101,
                  "original_text": "      - name: new_assignments_last_year\n        data_type: BIGINT\n        description: Distinct workers with assignment start in the last year; defaults to 0 when missing\n",
                  "name": "new_assignments_last_year",
                  "description": "Distinct workers with assignment start in the last year; defaults to 0 when missing",
                  "specification": {
                    "name": "new_assignments_last_year",
                    "data_type": "BIGINT",
                    "description": "Distinct workers with assignment start in the last year; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "departures_last_year": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2102,
                  "end_line": 2104,
                  "original_text": "      - name: departures_last_year\n        data_type: BIGINT\n        description: Distinct workers with non-null assignment end in the last year; defaults to 0 when missing\n",
                  "name": "departures_last_year",
                  "description": "Distinct workers with non-null assignment end in the last year; defaults to 0 when missing",
                  "specification": {
                    "name": "departures_last_year",
                    "data_type": "BIGINT",
                    "description": "Distinct workers with non-null assignment end in the last year; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "management_role_employees": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2117,
                  "end_line": 2119,
                  "original_text": "      - name: management_role_employees\n        data_type: BIGINT\n        description: Distinct workers with role code containing 'Manager'; defaults to 0 when missing\n",
                  "name": "management_role_employees",
                  "description": "Distinct workers with role code containing 'Manager'; defaults to 0 when missing",
                  "specification": {
                    "name": "management_role_employees",
                    "data_type": "BIGINT",
                    "description": "Distinct workers with role code containing 'Manager'; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "director_role_employees": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2120,
                  "end_line": 2122,
                  "original_text": "      - name: director_role_employees\n        data_type: BIGINT\n        description: Distinct workers with role code containing 'Director'; defaults to 0 when missing\n",
                  "name": "director_role_employees",
                  "description": "Distinct workers with role code containing 'Director'; defaults to 0 when missing",
                  "specification": {
                    "name": "director_role_employees",
                    "data_type": "BIGINT",
                    "description": "Distinct workers with role code containing 'Director'; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "lead_role_employees": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2123,
                  "end_line": 2125,
                  "original_text": "      - name: lead_role_employees\n        data_type: BIGINT\n        description: Distinct workers with role code containing 'Lead'; defaults to 0 when missing\n",
                  "name": "lead_role_employees",
                  "description": "Distinct workers with role code containing 'Lead'; defaults to 0 when missing",
                  "specification": {
                    "name": "lead_role_employees",
                    "data_type": "BIGINT",
                    "description": "Distinct workers with role code containing 'Lead'; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "high_value_stable_employees": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2138,
                  "end_line": 2140,
                  "original_text": "      - name: high_value_stable_employees\n        data_type: BIGINT\n        description: Distinct workers in 'High Value - High Retention'; defaults to 0 when missing\n",
                  "name": "high_value_stable_employees",
                  "description": "Distinct workers in 'High Value - High Retention'; defaults to 0 when missing",
                  "specification": {
                    "name": "high_value_stable_employees",
                    "data_type": "BIGINT",
                    "description": "Distinct workers in 'High Value - High Retention'; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "high_value_flight_risk_employees": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2141,
                  "end_line": 2143,
                  "original_text": "      - name: high_value_flight_risk_employees\n        data_type: BIGINT\n        description: Distinct workers in 'High Value - Flight Risk'; defaults to 0 when missing\n",
                  "name": "high_value_flight_risk_employees",
                  "description": "Distinct workers in 'High Value - Flight Risk'; defaults to 0 when missing",
                  "specification": {
                    "name": "high_value_flight_risk_employees",
                    "data_type": "BIGINT",
                    "description": "Distinct workers in 'High Value - Flight Risk'; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "stable_development_employees": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2144,
                  "end_line": 2146,
                  "original_text": "      - name: stable_development_employees\n        data_type: BIGINT\n        description: Distinct workers in 'Stable - Development Needed'; defaults to 0 when missing\n",
                  "name": "stable_development_employees",
                  "description": "Distinct workers in 'Stable - Development Needed'; defaults to 0 when missing",
                  "specification": {
                    "name": "stable_development_employees",
                    "data_type": "BIGINT",
                    "description": "Distinct workers in 'Stable - Development Needed'; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "development_required_employees": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2147,
                  "end_line": 2149,
                  "original_text": "      - name: development_required_employees\n        data_type: BIGINT\n        description: Distinct workers in 'Development Required'; defaults to 0 when missing\n",
                  "name": "development_required_employees",
                  "description": "Distinct workers in 'Development Required'; defaults to 0 when missing",
                  "specification": {
                    "name": "development_required_employees",
                    "data_type": "BIGINT",
                    "description": "Distinct workers in 'Development Required'; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "high_risk_employees": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2150,
                  "end_line": 2152,
                  "original_text": "      - name: high_risk_employees\n        data_type: BIGINT\n        description: Distinct workers with employee_risk_level = 'High Risk'; defaults to 0 when missing\n",
                  "name": "high_risk_employees",
                  "description": "Distinct workers with employee_risk_level = 'High Risk'; defaults to 0 when missing",
                  "specification": {
                    "name": "high_risk_employees",
                    "data_type": "BIGINT",
                    "description": "Distinct workers with employee_risk_level = 'High Risk'; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "medium_risk_employees": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2153,
                  "end_line": 2155,
                  "original_text": "      - name: medium_risk_employees\n        data_type: BIGINT\n        description: Distinct workers with employee_risk_level = 'Medium Risk'; defaults to 0 when missing\n",
                  "name": "medium_risk_employees",
                  "description": "Distinct workers with employee_risk_level = 'Medium Risk'; defaults to 0 when missing",
                  "specification": {
                    "name": "medium_risk_employees",
                    "data_type": "BIGINT",
                    "description": "Distinct workers with employee_risk_level = 'Medium Risk'; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "low_risk_employees": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2156,
                  "end_line": 2158,
                  "original_text": "      - name: low_risk_employees\n        data_type: BIGINT\n        description: Distinct workers with employee_risk_level = 'Low Risk'; defaults to 0 when missing\n",
                  "name": "low_risk_employees",
                  "description": "Distinct workers with employee_risk_level = 'Low Risk'; defaults to 0 when missing",
                  "specification": {
                    "name": "low_risk_employees",
                    "data_type": "BIGINT",
                    "description": "Distinct workers with employee_risk_level = 'Low Risk'; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "new_hire_employees": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2162,
                  "end_line": 2164,
                  "original_text": "      - name: new_hire_employees\n        data_type: BIGINT\n        description: Distinct employed workers with maturity containing 'New Hire'; defaults to 0 when missing\n",
                  "name": "new_hire_employees",
                  "description": "Distinct employed workers with maturity containing 'New Hire'; defaults to 0 when missing",
                  "specification": {
                    "name": "new_hire_employees",
                    "data_type": "BIGINT",
                    "description": "Distinct employed workers with maturity containing 'New Hire'; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "junior_employees": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2165,
                  "end_line": 2167,
                  "original_text": "      - name: junior_employees\n        data_type: BIGINT\n        description: Distinct employed workers with maturity containing 'Junior'; defaults to 0 when missing\n",
                  "name": "junior_employees",
                  "description": "Distinct employed workers with maturity containing 'Junior'; defaults to 0 when missing",
                  "specification": {
                    "name": "junior_employees",
                    "data_type": "BIGINT",
                    "description": "Distinct employed workers with maturity containing 'Junior'; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "experienced_employees": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2168,
                  "end_line": 2170,
                  "original_text": "      - name: experienced_employees\n        data_type: BIGINT\n        description: Distinct employed workers with maturity containing 'Experienced'; defaults to 0 when missing\n",
                  "name": "experienced_employees",
                  "description": "Distinct employed workers with maturity containing 'Experienced'; defaults to 0 when missing",
                  "specification": {
                    "name": "experienced_employees",
                    "data_type": "BIGINT",
                    "description": "Distinct employed workers with maturity containing 'Experienced'; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "senior_employees": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2171,
                  "end_line": 2173,
                  "original_text": "      - name: senior_employees\n        data_type: BIGINT\n        description: Distinct employed workers with maturity containing 'Senior'; defaults to 0 when missing\n",
                  "name": "senior_employees",
                  "description": "Distinct employed workers with maturity containing 'Senior'; defaults to 0 when missing",
                  "specification": {
                    "name": "senior_employees",
                    "data_type": "BIGINT",
                    "description": "Distinct employed workers with maturity containing 'Senior'; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "veteran_employees": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2174,
                  "end_line": 2176,
                  "original_text": "      - name: veteran_employees\n        data_type: BIGINT\n        description: Distinct employed workers with maturity containing 'Veteran'; defaults to 0 when missing\n",
                  "name": "veteran_employees",
                  "description": "Distinct employed workers with maturity containing 'Veteran'; defaults to 0 when missing",
                  "specification": {
                    "name": "veteran_employees",
                    "data_type": "BIGINT",
                    "description": "Distinct employed workers with maturity containing 'Veteran'; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "ethnic_diversity_count": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2177,
                  "end_line": 2179,
                  "original_text": "      - name: ethnic_diversity_count\n        data_type: BIGINT\n        description: Count of distinct ethnicity_codes among employed; defaults to 0 when missing\n",
                  "name": "ethnic_diversity_count",
                  "description": "Count of distinct ethnicity_codes among employed; defaults to 0 when missing",
                  "specification": {
                    "name": "ethnic_diversity_count",
                    "data_type": "BIGINT",
                    "description": "Count of distinct ethnicity_codes among employed; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "military_veterans_count": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2180,
                  "end_line": 2182,
                  "original_text": "      - name: military_veterans_count\n        data_type: BIGINT\n        description: Distinct employed workers with military service flag; defaults to 0 when missing\n",
                  "name": "military_veterans_count",
                  "description": "Distinct employed workers with military service flag; defaults to 0 when missing",
                  "specification": {
                    "name": "military_veterans_count",
                    "data_type": "BIGINT",
                    "description": "Distinct employed workers with military service flag; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "entry_level_employees": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2186,
                  "end_line": 2188,
                  "original_text": "      - name: entry_level_employees\n        data_type: BIGINT\n        description: Distinct employed workers in compensation_tier = 'Entry Level'; defaults to 0 when missing\n",
                  "name": "entry_level_employees",
                  "description": "Distinct employed workers in compensation_tier = 'Entry Level'; defaults to 0 when missing",
                  "specification": {
                    "name": "entry_level_employees",
                    "data_type": "BIGINT",
                    "description": "Distinct employed workers in compensation_tier = 'Entry Level'; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "mid_level_employees": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2189,
                  "end_line": 2191,
                  "original_text": "      - name: mid_level_employees\n        data_type: BIGINT\n        description: Distinct employed workers in compensation_tier = 'Mid Level'; defaults to 0 when missing\n",
                  "name": "mid_level_employees",
                  "description": "Distinct employed workers in compensation_tier = 'Mid Level'; defaults to 0 when missing",
                  "specification": {
                    "name": "mid_level_employees",
                    "data_type": "BIGINT",
                    "description": "Distinct employed workers in compensation_tier = 'Mid Level'; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "senior_level_employees": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2192,
                  "end_line": 2194,
                  "original_text": "      - name: senior_level_employees\n        data_type: BIGINT\n        description: Distinct employed workers in compensation_tier = 'Senior Level'; defaults to 0 when missing\n",
                  "name": "senior_level_employees",
                  "description": "Distinct employed workers in compensation_tier = 'Senior Level'; defaults to 0 when missing",
                  "specification": {
                    "name": "senior_level_employees",
                    "data_type": "BIGINT",
                    "description": "Distinct employed workers in compensation_tier = 'Senior Level'; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "executive_level_employees": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2195,
                  "end_line": 2197,
                  "original_text": "      - name: executive_level_employees\n        data_type: BIGINT\n        description: Distinct employed workers in compensation_tier = 'Executive Level'; defaults to 0 when missing\n",
                  "name": "executive_level_employees",
                  "description": "Distinct employed workers in compensation_tier = 'Executive Level'; defaults to 0 when missing",
                  "specification": {
                    "name": "executive_level_employees",
                    "data_type": "BIGINT",
                    "description": "Distinct employed workers in compensation_tier = 'Executive Level'; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "total_promotions_in_organization": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2198,
                  "end_line": 2200,
                  "original_text": "      - name: total_promotions_in_organization\n        data_type: HUGEINT\n        description: Sum of total_promotions for employed workers in the org; defaults to 0 when missing\n",
                  "name": "total_promotions_in_organization",
                  "description": "Sum of total_promotions for employed workers in the org; defaults to 0 when missing",
                  "specification": {
                    "name": "total_promotions_in_organization",
                    "data_type": "HUGEINT",
                    "description": "Sum of total_promotions for employed workers in the org; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "high_achievers_count": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2201,
                  "end_line": 2203,
                  "original_text": "      - name: high_achievers_count\n        data_type: BIGINT\n        description: Distinct employed workers with total_promotions >= 2; defaults to 0 when missing\n",
                  "name": "high_achievers_count",
                  "description": "Distinct employed workers with total_promotions >= 2; defaults to 0 when missing",
                  "specification": {
                    "name": "high_achievers_count",
                    "data_type": "BIGINT",
                    "description": "Distinct employed workers with total_promotions >= 2; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "fast_track_employees_count": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2204,
                  "end_line": 2206,
                  "original_text": "      - name: fast_track_employees_count\n        data_type: BIGINT\n        description: Distinct employed workers with fast_promotions > 0; defaults to 0 when missing\n",
                  "name": "fast_track_employees_count",
                  "description": "Distinct employed workers with fast_promotions > 0; defaults to 0 when missing",
                  "specification": {
                    "name": "fast_track_employees_count",
                    "data_type": "BIGINT",
                    "description": "Distinct employed workers with fast_promotions > 0; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            }
          },
          "description_pairs": [
            {
              "left": "current_active_employees",
              "right": "active_positions_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "current_active_employees",
              "right": "new_assignments_last_year",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "current_active_employees",
              "right": "departures_last_year",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "current_active_employees",
              "right": "management_role_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "current_active_employees",
              "right": "director_role_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "current_active_employees",
              "right": "lead_role_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "current_active_employees",
              "right": "high_value_stable_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "current_active_employees",
              "right": "high_value_flight_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "current_active_employees",
              "right": "stable_development_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "current_active_employees",
              "right": "development_required_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "current_active_employees",
              "right": "high_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "current_active_employees",
              "right": "medium_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "current_active_employees",
              "right": "low_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "current_active_employees",
              "right": "new_hire_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "current_active_employees",
              "right": "junior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "current_active_employees",
              "right": "experienced_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "current_active_employees",
              "right": "senior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "current_active_employees",
              "right": "veteran_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "current_active_employees",
              "right": "ethnic_diversity_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "current_active_employees",
              "right": "military_veterans_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "current_active_employees",
              "right": "entry_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "current_active_employees",
              "right": "mid_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "current_active_employees",
              "right": "senior_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "current_active_employees",
              "right": "executive_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "current_active_employees",
              "right": "total_promotions_in_organization",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "current_active_employees",
              "right": "high_achievers_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "current_active_employees",
              "right": "fast_track_employees_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "active_positions_count",
              "right": "new_assignments_last_year",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "active_positions_count",
              "right": "departures_last_year",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "active_positions_count",
              "right": "management_role_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "active_positions_count",
              "right": "director_role_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "active_positions_count",
              "right": "lead_role_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "active_positions_count",
              "right": "high_value_stable_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "active_positions_count",
              "right": "high_value_flight_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "active_positions_count",
              "right": "stable_development_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "active_positions_count",
              "right": "development_required_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "active_positions_count",
              "right": "high_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "active_positions_count",
              "right": "medium_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "active_positions_count",
              "right": "low_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "active_positions_count",
              "right": "new_hire_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "active_positions_count",
              "right": "junior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "active_positions_count",
              "right": "experienced_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "active_positions_count",
              "right": "senior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "active_positions_count",
              "right": "veteran_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "active_positions_count",
              "right": "ethnic_diversity_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "active_positions_count",
              "right": "military_veterans_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "active_positions_count",
              "right": "entry_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "active_positions_count",
              "right": "mid_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "active_positions_count",
              "right": "senior_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "active_positions_count",
              "right": "executive_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "active_positions_count",
              "right": "total_promotions_in_organization",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "active_positions_count",
              "right": "high_achievers_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "active_positions_count",
              "right": "fast_track_employees_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_assignments_last_year",
              "right": "departures_last_year",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_assignments_last_year",
              "right": "management_role_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_assignments_last_year",
              "right": "director_role_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_assignments_last_year",
              "right": "lead_role_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_assignments_last_year",
              "right": "high_value_stable_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_assignments_last_year",
              "right": "high_value_flight_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_assignments_last_year",
              "right": "stable_development_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_assignments_last_year",
              "right": "development_required_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_assignments_last_year",
              "right": "high_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_assignments_last_year",
              "right": "medium_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_assignments_last_year",
              "right": "low_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_assignments_last_year",
              "right": "new_hire_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_assignments_last_year",
              "right": "junior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_assignments_last_year",
              "right": "experienced_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_assignments_last_year",
              "right": "senior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_assignments_last_year",
              "right": "veteran_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_assignments_last_year",
              "right": "ethnic_diversity_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_assignments_last_year",
              "right": "military_veterans_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_assignments_last_year",
              "right": "entry_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_assignments_last_year",
              "right": "mid_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_assignments_last_year",
              "right": "senior_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_assignments_last_year",
              "right": "executive_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_assignments_last_year",
              "right": "total_promotions_in_organization",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_assignments_last_year",
              "right": "high_achievers_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_assignments_last_year",
              "right": "fast_track_employees_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "departures_last_year",
              "right": "management_role_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "departures_last_year",
              "right": "director_role_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "departures_last_year",
              "right": "lead_role_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "departures_last_year",
              "right": "high_value_stable_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "departures_last_year",
              "right": "high_value_flight_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "departures_last_year",
              "right": "stable_development_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "departures_last_year",
              "right": "development_required_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "departures_last_year",
              "right": "high_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "departures_last_year",
              "right": "medium_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "departures_last_year",
              "right": "low_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "departures_last_year",
              "right": "new_hire_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "departures_last_year",
              "right": "junior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "departures_last_year",
              "right": "experienced_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "departures_last_year",
              "right": "senior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "departures_last_year",
              "right": "veteran_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "departures_last_year",
              "right": "ethnic_diversity_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "departures_last_year",
              "right": "military_veterans_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "departures_last_year",
              "right": "entry_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "departures_last_year",
              "right": "mid_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "departures_last_year",
              "right": "senior_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "departures_last_year",
              "right": "executive_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "departures_last_year",
              "right": "total_promotions_in_organization",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "departures_last_year",
              "right": "high_achievers_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "departures_last_year",
              "right": "fast_track_employees_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "management_role_employees",
              "right": "director_role_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "management_role_employees",
              "right": "lead_role_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "management_role_employees",
              "right": "high_value_stable_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "management_role_employees",
              "right": "high_value_flight_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "management_role_employees",
              "right": "stable_development_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "management_role_employees",
              "right": "development_required_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "management_role_employees",
              "right": "high_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "management_role_employees",
              "right": "medium_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "management_role_employees",
              "right": "low_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "management_role_employees",
              "right": "new_hire_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "management_role_employees",
              "right": "junior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "management_role_employees",
              "right": "experienced_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "management_role_employees",
              "right": "senior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "management_role_employees",
              "right": "veteran_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "management_role_employees",
              "right": "ethnic_diversity_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "management_role_employees",
              "right": "military_veterans_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "management_role_employees",
              "right": "entry_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "management_role_employees",
              "right": "mid_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "management_role_employees",
              "right": "senior_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "management_role_employees",
              "right": "executive_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "management_role_employees",
              "right": "total_promotions_in_organization",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "management_role_employees",
              "right": "high_achievers_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "management_role_employees",
              "right": "fast_track_employees_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "director_role_employees",
              "right": "lead_role_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "director_role_employees",
              "right": "high_value_stable_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "director_role_employees",
              "right": "high_value_flight_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "director_role_employees",
              "right": "stable_development_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "director_role_employees",
              "right": "development_required_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "director_role_employees",
              "right": "high_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "director_role_employees",
              "right": "medium_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "director_role_employees",
              "right": "low_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "director_role_employees",
              "right": "new_hire_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "director_role_employees",
              "right": "junior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "director_role_employees",
              "right": "experienced_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "director_role_employees",
              "right": "senior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "director_role_employees",
              "right": "veteran_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "director_role_employees",
              "right": "ethnic_diversity_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "director_role_employees",
              "right": "military_veterans_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "director_role_employees",
              "right": "entry_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "director_role_employees",
              "right": "mid_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "director_role_employees",
              "right": "senior_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "director_role_employees",
              "right": "executive_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "director_role_employees",
              "right": "total_promotions_in_organization",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "director_role_employees",
              "right": "high_achievers_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "director_role_employees",
              "right": "fast_track_employees_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "lead_role_employees",
              "right": "high_value_stable_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "lead_role_employees",
              "right": "high_value_flight_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "lead_role_employees",
              "right": "stable_development_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "lead_role_employees",
              "right": "development_required_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "lead_role_employees",
              "right": "high_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "lead_role_employees",
              "right": "medium_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "lead_role_employees",
              "right": "low_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "lead_role_employees",
              "right": "new_hire_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "lead_role_employees",
              "right": "junior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "lead_role_employees",
              "right": "experienced_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "lead_role_employees",
              "right": "senior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "lead_role_employees",
              "right": "veteran_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "lead_role_employees",
              "right": "ethnic_diversity_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "lead_role_employees",
              "right": "military_veterans_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "lead_role_employees",
              "right": "entry_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "lead_role_employees",
              "right": "mid_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "lead_role_employees",
              "right": "senior_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "lead_role_employees",
              "right": "executive_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "lead_role_employees",
              "right": "total_promotions_in_organization",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "lead_role_employees",
              "right": "high_achievers_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "lead_role_employees",
              "right": "fast_track_employees_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_stable_employees",
              "right": "high_value_flight_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_stable_employees",
              "right": "stable_development_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_stable_employees",
              "right": "development_required_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_stable_employees",
              "right": "high_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_stable_employees",
              "right": "medium_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_stable_employees",
              "right": "low_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_stable_employees",
              "right": "new_hire_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_stable_employees",
              "right": "junior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_stable_employees",
              "right": "experienced_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_stable_employees",
              "right": "senior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_stable_employees",
              "right": "veteran_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_stable_employees",
              "right": "ethnic_diversity_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_stable_employees",
              "right": "military_veterans_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_stable_employees",
              "right": "entry_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_stable_employees",
              "right": "mid_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_stable_employees",
              "right": "senior_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_stable_employees",
              "right": "executive_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_stable_employees",
              "right": "total_promotions_in_organization",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_stable_employees",
              "right": "high_achievers_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_stable_employees",
              "right": "fast_track_employees_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_flight_risk_employees",
              "right": "stable_development_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_flight_risk_employees",
              "right": "development_required_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_flight_risk_employees",
              "right": "high_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_flight_risk_employees",
              "right": "medium_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_flight_risk_employees",
              "right": "low_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_flight_risk_employees",
              "right": "new_hire_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_flight_risk_employees",
              "right": "junior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_flight_risk_employees",
              "right": "experienced_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_flight_risk_employees",
              "right": "senior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_flight_risk_employees",
              "right": "veteran_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_flight_risk_employees",
              "right": "ethnic_diversity_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_flight_risk_employees",
              "right": "military_veterans_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_flight_risk_employees",
              "right": "entry_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_flight_risk_employees",
              "right": "mid_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_flight_risk_employees",
              "right": "senior_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_flight_risk_employees",
              "right": "executive_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_flight_risk_employees",
              "right": "total_promotions_in_organization",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_flight_risk_employees",
              "right": "high_achievers_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_value_flight_risk_employees",
              "right": "fast_track_employees_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "stable_development_employees",
              "right": "development_required_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "stable_development_employees",
              "right": "high_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "stable_development_employees",
              "right": "medium_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "stable_development_employees",
              "right": "low_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "stable_development_employees",
              "right": "new_hire_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "stable_development_employees",
              "right": "junior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "stable_development_employees",
              "right": "experienced_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "stable_development_employees",
              "right": "senior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "stable_development_employees",
              "right": "veteran_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "stable_development_employees",
              "right": "ethnic_diversity_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "stable_development_employees",
              "right": "military_veterans_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "stable_development_employees",
              "right": "entry_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "stable_development_employees",
              "right": "mid_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "stable_development_employees",
              "right": "senior_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "stable_development_employees",
              "right": "executive_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "stable_development_employees",
              "right": "total_promotions_in_organization",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "stable_development_employees",
              "right": "high_achievers_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "stable_development_employees",
              "right": "fast_track_employees_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "development_required_employees",
              "right": "high_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "development_required_employees",
              "right": "medium_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "development_required_employees",
              "right": "low_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "development_required_employees",
              "right": "new_hire_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "development_required_employees",
              "right": "junior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "development_required_employees",
              "right": "experienced_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "development_required_employees",
              "right": "senior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "development_required_employees",
              "right": "veteran_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "development_required_employees",
              "right": "ethnic_diversity_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "development_required_employees",
              "right": "military_veterans_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "development_required_employees",
              "right": "entry_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "development_required_employees",
              "right": "mid_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "development_required_employees",
              "right": "senior_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "development_required_employees",
              "right": "executive_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "development_required_employees",
              "right": "total_promotions_in_organization",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "development_required_employees",
              "right": "high_achievers_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "development_required_employees",
              "right": "fast_track_employees_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_risk_employees",
              "right": "medium_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_risk_employees",
              "right": "low_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_risk_employees",
              "right": "new_hire_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_risk_employees",
              "right": "junior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_risk_employees",
              "right": "experienced_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_risk_employees",
              "right": "senior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_risk_employees",
              "right": "veteran_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_risk_employees",
              "right": "ethnic_diversity_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_risk_employees",
              "right": "military_veterans_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_risk_employees",
              "right": "entry_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_risk_employees",
              "right": "mid_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_risk_employees",
              "right": "senior_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_risk_employees",
              "right": "executive_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_risk_employees",
              "right": "total_promotions_in_organization",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_risk_employees",
              "right": "high_achievers_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_risk_employees",
              "right": "fast_track_employees_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "medium_risk_employees",
              "right": "low_risk_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "medium_risk_employees",
              "right": "new_hire_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "medium_risk_employees",
              "right": "junior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "medium_risk_employees",
              "right": "experienced_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "medium_risk_employees",
              "right": "senior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "medium_risk_employees",
              "right": "veteran_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "medium_risk_employees",
              "right": "ethnic_diversity_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "medium_risk_employees",
              "right": "military_veterans_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "medium_risk_employees",
              "right": "entry_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "medium_risk_employees",
              "right": "mid_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "medium_risk_employees",
              "right": "senior_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "medium_risk_employees",
              "right": "executive_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "medium_risk_employees",
              "right": "total_promotions_in_organization",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "medium_risk_employees",
              "right": "high_achievers_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "medium_risk_employees",
              "right": "fast_track_employees_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "low_risk_employees",
              "right": "new_hire_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "low_risk_employees",
              "right": "junior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "low_risk_employees",
              "right": "experienced_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "low_risk_employees",
              "right": "senior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "low_risk_employees",
              "right": "veteran_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "low_risk_employees",
              "right": "ethnic_diversity_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "low_risk_employees",
              "right": "military_veterans_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "low_risk_employees",
              "right": "entry_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "low_risk_employees",
              "right": "mid_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "low_risk_employees",
              "right": "senior_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "low_risk_employees",
              "right": "executive_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "low_risk_employees",
              "right": "total_promotions_in_organization",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "low_risk_employees",
              "right": "high_achievers_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "low_risk_employees",
              "right": "fast_track_employees_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_hire_employees",
              "right": "junior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_hire_employees",
              "right": "experienced_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_hire_employees",
              "right": "senior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_hire_employees",
              "right": "veteran_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_hire_employees",
              "right": "ethnic_diversity_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_hire_employees",
              "right": "military_veterans_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_hire_employees",
              "right": "entry_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_hire_employees",
              "right": "mid_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_hire_employees",
              "right": "senior_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_hire_employees",
              "right": "executive_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_hire_employees",
              "right": "total_promotions_in_organization",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_hire_employees",
              "right": "high_achievers_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "new_hire_employees",
              "right": "fast_track_employees_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "junior_employees",
              "right": "experienced_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "junior_employees",
              "right": "senior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "junior_employees",
              "right": "veteran_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "junior_employees",
              "right": "ethnic_diversity_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "junior_employees",
              "right": "military_veterans_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "junior_employees",
              "right": "entry_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "junior_employees",
              "right": "mid_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "junior_employees",
              "right": "senior_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "junior_employees",
              "right": "executive_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "junior_employees",
              "right": "total_promotions_in_organization",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "junior_employees",
              "right": "high_achievers_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "junior_employees",
              "right": "fast_track_employees_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "experienced_employees",
              "right": "senior_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "experienced_employees",
              "right": "veteran_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "experienced_employees",
              "right": "ethnic_diversity_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "experienced_employees",
              "right": "military_veterans_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "experienced_employees",
              "right": "entry_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "experienced_employees",
              "right": "mid_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "experienced_employees",
              "right": "senior_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "experienced_employees",
              "right": "executive_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "experienced_employees",
              "right": "total_promotions_in_organization",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "experienced_employees",
              "right": "high_achievers_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "experienced_employees",
              "right": "fast_track_employees_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "senior_employees",
              "right": "veteran_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "senior_employees",
              "right": "ethnic_diversity_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "senior_employees",
              "right": "military_veterans_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "senior_employees",
              "right": "entry_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "senior_employees",
              "right": "mid_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "senior_employees",
              "right": "senior_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "senior_employees",
              "right": "executive_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "senior_employees",
              "right": "total_promotions_in_organization",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "senior_employees",
              "right": "high_achievers_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "senior_employees",
              "right": "fast_track_employees_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "veteran_employees",
              "right": "ethnic_diversity_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "veteran_employees",
              "right": "military_veterans_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "veteran_employees",
              "right": "entry_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "veteran_employees",
              "right": "mid_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "veteran_employees",
              "right": "senior_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "veteran_employees",
              "right": "executive_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "veteran_employees",
              "right": "total_promotions_in_organization",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "veteran_employees",
              "right": "high_achievers_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "veteran_employees",
              "right": "fast_track_employees_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "ethnic_diversity_count",
              "right": "military_veterans_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "ethnic_diversity_count",
              "right": "entry_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "ethnic_diversity_count",
              "right": "mid_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "ethnic_diversity_count",
              "right": "senior_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "ethnic_diversity_count",
              "right": "executive_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "ethnic_diversity_count",
              "right": "total_promotions_in_organization",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "ethnic_diversity_count",
              "right": "high_achievers_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "ethnic_diversity_count",
              "right": "fast_track_employees_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "military_veterans_count",
              "right": "entry_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "military_veterans_count",
              "right": "mid_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "military_veterans_count",
              "right": "senior_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "military_veterans_count",
              "right": "executive_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "military_veterans_count",
              "right": "total_promotions_in_organization",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "military_veterans_count",
              "right": "high_achievers_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "military_veterans_count",
              "right": "fast_track_employees_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "entry_level_employees",
              "right": "mid_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "entry_level_employees",
              "right": "senior_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "entry_level_employees",
              "right": "executive_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "entry_level_employees",
              "right": "total_promotions_in_organization",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "entry_level_employees",
              "right": "high_achievers_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "entry_level_employees",
              "right": "fast_track_employees_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "mid_level_employees",
              "right": "senior_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "mid_level_employees",
              "right": "executive_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "mid_level_employees",
              "right": "total_promotions_in_organization",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "mid_level_employees",
              "right": "high_achievers_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "mid_level_employees",
              "right": "fast_track_employees_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "senior_level_employees",
              "right": "executive_level_employees",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "senior_level_employees",
              "right": "total_promotions_in_organization",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "senior_level_employees",
              "right": "high_achievers_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "senior_level_employees",
              "right": "fast_track_employees_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "executive_level_employees",
              "right": "total_promotions_in_organization",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "executive_level_employees",
              "right": "high_achievers_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "executive_level_employees",
              "right": "fast_track_employees_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "total_promotions_in_organization",
              "right": "high_achievers_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "total_promotions_in_organization",
              "right": "fast_track_employees_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "high_achievers_count",
              "right": "fast_track_employees_count",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            }
          ],
          "has_pair_with_different_explicit_description": true,
          "meaning_status": "description_texts_differ_no_semantic_judgment"
        },
        {
          "columns": [
            "position_fill_rate",
            "avg_current_tenure_years",
            "avg_employee_performance_score",
            "avg_career_development_score",
            "avg_retention_stability_score",
            "avg_employee_age"
          ],
          "table_rows": 117,
          "nonnull_equal_rows": 117,
          "both_null_rows_ignored": 0,
          "mismatch_rows": 0,
          "column_contracts": {
            "position_fill_rate": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2096,
                  "end_line": 2098,
                  "original_text": "      - name: position_fill_rate\n        data_type: DOUBLE\n        description: Filled positions % = round(current_active_employees*100.0/total_positions, 2); 0 if total_positions=0\n",
                  "name": "position_fill_rate",
                  "description": "Filled positions % = round(current_active_employees*100.0/total_positions, 2); 0 if total_positions=0",
                  "specification": {
                    "name": "position_fill_rate",
                    "data_type": "DOUBLE",
                    "description": "Filled positions % = round(current_active_employees*100.0/total_positions, 2); 0 if total_positions=0"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "avg_current_tenure_years": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2108,
                  "end_line": 2110,
                  "original_text": "      - name: avg_current_tenure_years\n        data_type: DOUBLE\n        description: Average tenure (years) for Active Assignments = round(avg_current_tenure_days/365.0, 2) with NULL→0\n",
                  "name": "avg_current_tenure_years",
                  "description": "Average tenure (years) for Active Assignments = round(avg_current_tenure_days/365.0, 2) with NULL→0",
                  "specification": {
                    "name": "avg_current_tenure_years",
                    "data_type": "DOUBLE",
                    "description": "Average tenure (years) for Active Assignments = round(avg_current_tenure_days/365.0, 2) with NULL→0"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "avg_employee_performance_score": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2129,
                  "end_line": 2131,
                  "original_text": "      - name: avg_employee_performance_score\n        data_type: DOUBLE\n        description: Avg overall_employee_score among employed, rounded to 2; defaults to 0 when missing; 0–100 scale preserved\n",
                  "name": "avg_employee_performance_score",
                  "description": "Avg overall_employee_score among employed, rounded to 2; defaults to 0 when missing; 0–100 scale preserved",
                  "specification": {
                    "name": "avg_employee_performance_score",
                    "data_type": "DOUBLE",
                    "description": "Avg overall_employee_score among employed, rounded to 2; defaults to 0 when missing; 0–100 scale preserved"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "avg_career_development_score": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2132,
                  "end_line": 2134,
                  "original_text": "      - name: avg_career_development_score\n        data_type: DOUBLE\n        description: Avg career_development_score among employed, rounded to 2; defaults to 0 when missing; 0–100 scale preserved\n",
                  "name": "avg_career_development_score",
                  "description": "Avg career_development_score among employed, rounded to 2; defaults to 0 when missing; 0–100 scale preserved",
                  "specification": {
                    "name": "avg_career_development_score",
                    "data_type": "DOUBLE",
                    "description": "Avg career_development_score among employed, rounded to 2; defaults to 0 when missing; 0–100 scale preserved"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "avg_retention_stability_score": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2135,
                  "end_line": 2137,
                  "original_text": "      - name: avg_retention_stability_score\n        data_type: DOUBLE\n        description: Avg retention_stability_score among employed, rounded to 2; defaults to 0 when missing; 0–100 scale preserved\n",
                  "name": "avg_retention_stability_score",
                  "description": "Avg retention_stability_score among employed, rounded to 2; defaults to 0 when missing; 0–100 scale preserved",
                  "specification": {
                    "name": "avg_retention_stability_score",
                    "data_type": "DOUBLE",
                    "description": "Avg retention_stability_score among employed, rounded to 2; defaults to 0 when missing; 0–100 scale preserved"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            },
            "avg_employee_age": {
              "status": "found",
              "definitions": [
                {
                  "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
                  "start_line": 2183,
                  "end_line": 2185,
                  "original_text": "      - name: avg_employee_age\n        data_type: DOUBLE\n        description: Average age among employed, rounded to 1 in source aggregation; defaults to 0 when missing\n",
                  "name": "avg_employee_age",
                  "description": "Average age among employed, rounded to 1 in source aggregation; defaults to 0 when missing",
                  "specification": {
                    "name": "avg_employee_age",
                    "data_type": "DOUBLE",
                    "description": "Average age among employed, rounded to 1 in source aggregation; defaults to 0 when missing"
                  }
                }
              ],
              "meaning_description_status": "explicit_description"
            }
          },
          "description_pairs": [
            {
              "left": "position_fill_rate",
              "right": "avg_current_tenure_years",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "position_fill_rate",
              "right": "avg_employee_performance_score",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "position_fill_rate",
              "right": "avg_career_development_score",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "position_fill_rate",
              "right": "avg_retention_stability_score",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "position_fill_rate",
              "right": "avg_employee_age",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "avg_current_tenure_years",
              "right": "avg_employee_performance_score",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "avg_current_tenure_years",
              "right": "avg_career_development_score",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "avg_current_tenure_years",
              "right": "avg_retention_stability_score",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "avg_current_tenure_years",
              "right": "avg_employee_age",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "avg_employee_performance_score",
              "right": "avg_career_development_score",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "avg_employee_performance_score",
              "right": "avg_retention_stability_score",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "avg_employee_performance_score",
              "right": "avg_employee_age",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "avg_career_development_score",
              "right": "avg_retention_stability_score",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "avg_career_development_score",
              "right": "avg_employee_age",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            },
            {
              "left": "avg_retention_stability_score",
              "right": "avg_employee_age",
              "both_have_explicit_descriptions": true,
              "description_texts_differ": true,
              "semantic_equivalence_evaluated": false
            }
          ],
          "has_pair_with_different_explicit_description": true,
          "meaning_status": "description_texts_differ_no_semantic_judgment"
        }
      ],
      "profile_sql": "SELECT count(*),count(\"organization_id\"),min(CAST(\"organization_id\" AS VARCHAR)),max(CAST(\"organization_id\" AS VARCHAR)),sum(hash(CAST(\"organization_id\" AS VARCHAR))),count(\"source_relation\"),min(CAST(\"source_relation\" AS VARCHAR)),max(CAST(\"source_relation\" AS VARCHAR)),sum(hash(CAST(\"source_relation\" AS VARCHAR))),count(\"organization_name\"),min(CAST(\"organization_name\" AS VARCHAR)),max(CAST(\"organization_name\" AS VARCHAR)),sum(hash(CAST(\"organization_name\" AS VARCHAR))),count(\"organization_code\"),min(CAST(\"organization_code\" AS VARCHAR)),max(CAST(\"organization_code\" AS VARCHAR)),sum(hash(CAST(\"organization_code\" AS VARCHAR))),count(\"organization_type\"),min(CAST(\"organization_type\" AS VARCHAR)),max(CAST(\"organization_type\" AS VARCHAR)),sum(hash(CAST(\"organization_type\" AS VARCHAR))),count(\"organization_sub_type\"),min(CAST(\"organization_sub_type\" AS VARCHAR)),max(CAST(\"organization_sub_type\" AS VARCHAR)),sum(hash(CAST(\"organization_sub_type\" AS VARCHAR))),count(\"staffing_model\"),min(CAST(\"staffing_model\" AS VARCHAR)),max(CAST(\"staffing_model\" AS VARCHAR)),sum(hash(CAST(\"staffing_model\" AS VARCHAR))),count(\"visibility\"),min(CAST(\"visibility\" AS VARCHAR)),max(CAST(\"visibility\" AS VARCHAR)),sum(hash(CAST(\"visibility\" AS VARCHAR))),count(\"access_level\"),min(CAST(\"access_level\" AS VARCHAR)),max(CAST(\"access_level\" AS VARCHAR)),sum(hash(CAST(\"access_level\" AS VARCHAR))),count(\"organization_created_date\"),min(CAST(\"organization_created_date\" AS VARCHAR)),max(CAST(\"organization_created_date\" AS VARCHAR)),sum(hash(CAST(\"organization_created_date\" AS VARCHAR))),count(\"organization_age_days\"),min(CAST(\"organization_age_days\" AS VARCHAR)),max(CAST(\"organization_age_days\" AS VARCHAR)),sum(hash(CAST(\"organization_age_days\" AS VARCHAR))),count(\"organization_age_years\"),min(CAST(\"organization_age_years\" AS VARCHAR)),max(CAST(\"organization_age_years\" AS VARCHAR)),sum(hash(CAST(\"organization_age_years\" AS VARCHAR))),count(\"organization_maturity_level\"),min(CAST(\"organization_maturity_level\" AS VARCHAR)),max(CAST(\"organization_maturity_level\" AS VARCHAR)),sum(hash(CAST(\"organization_maturity_level\" AS VARCHAR))),count(\"organizational_level\"),min(CAST(\"organizational_level\" AS VARCHAR)),max(CAST(\"organizational_level\" AS VARCHAR)),sum(hash(CAST(\"organizational_level\" AS VARCHAR))),count(\"total_employees_ever\"),min(CAST(\"total_employees_ever\" AS VARCHAR)),max(CAST(\"total_employees_ever\" AS VARCHAR)),sum(hash(CAST(\"total_employees_ever\" AS VARCHAR))),count(\"current_active_employees\"),min(CAST(\"current_active_employees\" AS VARCHAR)),max(CAST(\"current_active_employees\" AS VARCHAR)),sum(hash(CAST(\"current_active_employees\" AS VARCHAR))),count(\"former_employees\"),min(CAST(\"former_employees\" AS VARCHAR)),max(CAST(\"former_employees\" AS VARCHAR)),sum(hash(CAST(\"former_employees\" AS VARCHAR))),count(\"total_positions\"),min(CAST(\"total_positions\" AS VARCHAR)),max(CAST(\"total_positions\" AS VARCHAR)),sum(hash(CAST(\"total_positions\" AS VARCHAR))),count(\"active_positions_count\"),min(CAST(\"active_positions_count\" AS VARCHAR)),max(CAST(\"active_positions_count\" AS VARCHAR)),sum(hash(CAST(\"active_positions_count\" AS VARCHAR))),count(\"position_fill_rate\"),min(CAST(\"position_fill_rate\" AS VARCHAR)),max(CAST(\"position_fill_rate\" AS VARCHAR)),sum(hash(CAST(\"position_fill_rate\" AS VARCHAR))),count(\"new_assignments_last_year\"),min(CAST(\"new_assignments_last_year\" AS VARCHAR)),max(CAST(\"new_assignments_last_year\" AS VARCHAR)),sum(hash(CAST(\"new_assignments_last_year\" AS VARCHAR))),count(\"departures_last_year\"),min(CAST(\"departures_last_year\" AS VARCHAR)),max(CAST(\"departures_last_year\" AS VARCHAR)),sum(hash(CAST(\"departures_last_year\" AS VARCHAR))),count(\"annual_turnover_rate\"),min(CAST(\"annual_turnover_rate\" AS VARCHAR)),max(CAST(\"annual_turnover_rate\" AS VARCHAR)),sum(hash(CAST(\"annual_turnover_rate\" AS VARCHAR))),count(\"avg_current_tenure_years\"),min(CAST(\"avg_current_tenure_years\" AS VARCHAR)),max(CAST(\"avg_current_tenure_years\" AS VARCHAR)),sum(hash(CAST(\"avg_current_tenure_years\" AS VARCHAR))),count(\"avg_former_tenure_years\"),min(CAST(\"avg_former_tenure_years\" AS VARCHAR)),max(CAST(\"avg_former_tenure_years\" AS VARCHAR)),sum(hash(CAST(\"avg_former_tenure_years\" AS VARCHAR))),count(\"unique_organization_roles\"),min(CAST(\"unique_organization_roles\" AS VARCHAR)),max(CAST(\"unique_organization_roles\" AS VARCHAR)),sum(hash(CAST(\"unique_organization_roles\" AS VARCHAR))),count(\"management_role_employees\"),min(CAST(\"management_role_employees\" AS VARCHAR)),max(CAST(\"management_role_employees\" AS VARCHAR)),sum(hash(CAST(\"management_role_employees\" AS VARCHAR))),count(\"director_role_employees\"),min(CAST(\"director_role_employees\" AS VARCHAR)),max(CAST(\"director_role_employees\" AS VARCHAR)),sum(hash(CAST(\"director_role_employees\" AS VARCHAR))),count(\"lead_role_employees\"),min(CAST(\"lead_role_employees\" AS VARCHAR)),max(CAST(\"lead_role_employees\" AS VARCHAR)),sum(hash(CAST(\"lead_role_employees\" AS VARCHAR))),count(\"management_ratio\"),min(CAST(\"management_ratio\" AS VARCHAR)),max(CAST(\"management_ratio\" AS VARCHAR)),sum(hash(CAST(\"management_ratio\" AS VARCHAR))),count(\"avg_employee_performance_score\"),min(CAST(\"avg_employee_performance_score\" AS VARCHAR)),max(CAST(\"avg_employee_performance_score\" AS VARCHAR)),sum(hash(CAST(\"avg_employee_performance_score\" AS VARCHAR))),count(\"avg_career_development_score\"),min(CAST(\"avg_career_development_score\" AS VARCHAR)),max(CAST(\"avg_career_development_score\" AS VARCHAR)),sum(hash(CAST(\"avg_career_development_score\" AS VARCHAR))),count(\"avg_retention_stability_score\"),min(CAST(\"avg_retention_stability_score\" AS VARCHAR)),max(CAST(\"avg_retention_stability_score\" AS VARCHAR)),sum(hash(CAST(\"avg_retention_stability_score\" AS VARCHAR))),count(\"high_value_stable_employees\"),min(CAST(\"high_value_stable_employees\" AS VARCHAR)),max(CAST(\"high_value_stable_employees\" AS VARCHAR)),sum(hash(CAST(\"high_value_stable_employees\" AS VARCHAR))),count(\"high_value_flight_risk_employees\"),min(CAST(\"high_value_flight_risk_employees\" AS VARCHAR)),max(CAST(\"high_value_flight_risk_employees\" AS VARCHAR)),sum(hash(CAST(\"high_value_flight_risk_employees\" AS VARCHAR))),count(\"stable_development_employees\"),min(CAST(\"stable_development_employees\" AS VARCHAR)),max(CAST(\"stable_development_employees\" AS VARCHAR)),sum(hash(CAST(\"stable_development_employees\" AS VARCHAR))),count(\"development_required_employees\"),min(CAST(\"development_required_employees\" AS VARCHAR)),max(CAST(\"development_required_employees\" AS VARCHAR)),sum(hash(CAST(\"development_required_employees\" AS VARCHAR))),count(\"high_risk_employees\"),min(CAST(\"high_risk_employees\" AS VARCHAR)),max(CAST(\"high_risk_employees\" AS VARCHAR)),sum(hash(CAST(\"high_risk_employees\" AS VARCHAR))),count(\"medium_risk_employees\"),min(CAST(\"medium_risk_employees\" AS VARCHAR)),max(CAST(\"medium_risk_employees\" AS VARCHAR)),sum(hash(CAST(\"medium_risk_employees\" AS VARCHAR))),count(\"low_risk_employees\"),min(CAST(\"low_risk_employees\" AS VARCHAR)),max(CAST(\"low_risk_employees\" AS VARCHAR)),sum(hash(CAST(\"low_risk_employees\" AS VARCHAR))),count(\"high_risk_employee_percentage\"),min(CAST(\"high_risk_employee_percentage\" AS VARCHAR)),max(CAST(\"high_risk_employee_percentage\" AS VARCHAR)),sum(hash(CAST(\"high_risk_employee_percentage\" AS VARCHAR))),count(\"new_hire_employees\"),min(CAST(\"new_hire_employees\" AS VARCHAR)),max(CAST(\"new_hire_employees\" AS VARCHAR)),sum(hash(CAST(\"new_hire_employees\" AS VARCHAR))),count(\"junior_employees\"),min(CAST(\"junior_employees\" AS VARCHAR)),max(CAST(\"junior_employees\" AS VARCHAR)),sum(hash(CAST(\"junior_employees\" AS VARCHAR))),count(\"experienced_employees\"),min(CAST(\"experienced_employees\" AS VARCHAR)),max(CAST(\"experienced_employees\" AS VARCHAR)),sum(hash(CAST(\"experienced_employees\" AS VARCHAR))),count(\"senior_employees\"),min(CAST(\"senior_employees\" AS VARCHAR)),max(CAST(\"senior_employees\" AS VARCHAR)),sum(hash(CAST(\"senior_employees\" AS VARCHAR))),count(\"veteran_employees\"),min(CAST(\"veteran_employees\" AS VARCHAR)),max(CAST(\"veteran_employees\" AS VARCHAR)),sum(hash(CAST(\"veteran_employees\" AS VARCHAR))),count(\"ethnic_diversity_count\"),min(CAST(\"ethnic_diversity_count\" AS VARCHAR)),max(CAST(\"ethnic_diversity_count\" AS VARCHAR)),sum(hash(CAST(\"ethnic_diversity_count\" AS VARCHAR))),count(\"military_veterans_count\"),min(CAST(\"military_veterans_count\" AS VARCHAR)),max(CAST(\"military_veterans_count\" AS VARCHAR)),sum(hash(CAST(\"military_veterans_count\" AS VARCHAR))),count(\"avg_employee_age\"),min(CAST(\"avg_employee_age\" AS VARCHAR)),max(CAST(\"avg_employee_age\" AS VARCHAR)),sum(hash(CAST(\"avg_employee_age\" AS VARCHAR))),count(\"entry_level_employees\"),min(CAST(\"entry_level_employees\" AS VARCHAR)),max(CAST(\"entry_level_employees\" AS VARCHAR)),sum(hash(CAST(\"entry_level_employees\" AS VARCHAR))),count(\"mid_level_employees\"),min(CAST(\"mid_level_employees\" AS VARCHAR)),max(CAST(\"mid_level_employees\" AS VARCHAR)),sum(hash(CAST(\"mid_level_employees\" AS VARCHAR))),count(\"senior_level_employees\"),min(CAST(\"senior_level_employees\" AS VARCHAR)),max(CAST(\"senior_level_employees\" AS VARCHAR)),sum(hash(CAST(\"senior_level_employees\" AS VARCHAR))),count(\"executive_level_employees\"),min(CAST(\"executive_level_employees\" AS VARCHAR)),max(CAST(\"executive_level_employees\" AS VARCHAR)),sum(hash(CAST(\"executive_level_employees\" AS VARCHAR))),count(\"total_promotions_in_organization\"),min(CAST(\"total_promotions_in_organization\" AS VARCHAR)),max(CAST(\"total_promotions_in_organization\" AS VARCHAR)),sum(hash(CAST(\"total_promotions_in_organization\" AS VARCHAR))),count(\"high_achievers_count\"),min(CAST(\"high_achievers_count\" AS VARCHAR)),max(CAST(\"high_achievers_count\" AS VARCHAR)),sum(hash(CAST(\"high_achievers_count\" AS VARCHAR))),count(\"fast_track_employees_count\"),min(CAST(\"fast_track_employees_count\" AS VARCHAR)),max(CAST(\"fast_track_employees_count\" AS VARCHAR)),sum(hash(CAST(\"fast_track_employees_count\" AS VARCHAR))),count(\"organization_health_score\"),min(CAST(\"organization_health_score\" AS VARCHAR)),max(CAST(\"organization_health_score\" AS VARCHAR)),sum(hash(CAST(\"organization_health_score\" AS VARCHAR))),count(\"performance_category\"),min(CAST(\"performance_category\" AS VARCHAR)),max(CAST(\"performance_category\" AS VARCHAR)),sum(hash(CAST(\"performance_category\" AS VARCHAR))),count(\"organization_size_category\"),min(CAST(\"organization_size_category\" AS VARCHAR)),max(CAST(\"organization_size_category\" AS VARCHAR)),sum(hash(CAST(\"organization_size_category\" AS VARCHAR))),count(\"last_activity_date\"),min(CAST(\"last_activity_date\" AS VARCHAR)),max(CAST(\"last_activity_date\" AS VARCHAR)),sum(hash(CAST(\"last_activity_date\" AS VARCHAR))),count(\"last_departure_date\"),min(CAST(\"last_departure_date\" AS VARCHAR)),max(CAST(\"last_departure_date\" AS VARCHAR)),sum(hash(CAST(\"last_departure_date\" AS VARCHAR))),count(\"management_recommendation\"),min(CAST(\"management_recommendation\" AS VARCHAR)),max(CAST(\"management_recommendation\" AS VARCHAR)),sum(hash(CAST(\"management_recommendation\" AS VARCHAR))),count(\"data_quality_flag\"),min(CAST(\"data_quality_flag\" AS VARCHAR)),max(CAST(\"data_quality_flag\" AS VARCHAR)),sum(hash(CAST(\"data_quality_flag\" AS VARCHAR))),count(\"analysis_timestamp\"),min(CAST(\"analysis_timestamp\" AS VARCHAR)),max(CAST(\"analysis_timestamp\" AS VARCHAR)),sum(hash(CAST(\"analysis_timestamp\" AS VARCHAR))) FROM \"mart\".\"workday__organization_overview\"",
      "equal_column_confirmation_queries": [
        {
          "left": "total_employees_ever",
          "right": "former_employees",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"total_employees_ever\" AS VARCHAR) IS DISTINCT FROM CAST(\"former_employees\" AS VARCHAR)),count(*) FILTER(WHERE \"total_employees_ever\" IS NOT NULL AND \"former_employees\" IS NOT NULL AND CAST(\"total_employees_ever\" AS VARCHAR)=CAST(\"former_employees\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "current_active_employees",
          "right": "active_positions_count",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"current_active_employees\" AS VARCHAR) IS DISTINCT FROM CAST(\"active_positions_count\" AS VARCHAR)),count(*) FILTER(WHERE \"current_active_employees\" IS NOT NULL AND \"active_positions_count\" IS NOT NULL AND CAST(\"current_active_employees\" AS VARCHAR)=CAST(\"active_positions_count\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "current_active_employees",
          "right": "new_assignments_last_year",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"current_active_employees\" AS VARCHAR) IS DISTINCT FROM CAST(\"new_assignments_last_year\" AS VARCHAR)),count(*) FILTER(WHERE \"current_active_employees\" IS NOT NULL AND \"new_assignments_last_year\" IS NOT NULL AND CAST(\"current_active_employees\" AS VARCHAR)=CAST(\"new_assignments_last_year\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "current_active_employees",
          "right": "departures_last_year",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"current_active_employees\" AS VARCHAR) IS DISTINCT FROM CAST(\"departures_last_year\" AS VARCHAR)),count(*) FILTER(WHERE \"current_active_employees\" IS NOT NULL AND \"departures_last_year\" IS NOT NULL AND CAST(\"current_active_employees\" AS VARCHAR)=CAST(\"departures_last_year\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "current_active_employees",
          "right": "management_role_employees",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"current_active_employees\" AS VARCHAR) IS DISTINCT FROM CAST(\"management_role_employees\" AS VARCHAR)),count(*) FILTER(WHERE \"current_active_employees\" IS NOT NULL AND \"management_role_employees\" IS NOT NULL AND CAST(\"current_active_employees\" AS VARCHAR)=CAST(\"management_role_employees\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "current_active_employees",
          "right": "director_role_employees",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"current_active_employees\" AS VARCHAR) IS DISTINCT FROM CAST(\"director_role_employees\" AS VARCHAR)),count(*) FILTER(WHERE \"current_active_employees\" IS NOT NULL AND \"director_role_employees\" IS NOT NULL AND CAST(\"current_active_employees\" AS VARCHAR)=CAST(\"director_role_employees\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "current_active_employees",
          "right": "lead_role_employees",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"current_active_employees\" AS VARCHAR) IS DISTINCT FROM CAST(\"lead_role_employees\" AS VARCHAR)),count(*) FILTER(WHERE \"current_active_employees\" IS NOT NULL AND \"lead_role_employees\" IS NOT NULL AND CAST(\"current_active_employees\" AS VARCHAR)=CAST(\"lead_role_employees\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "current_active_employees",
          "right": "high_value_stable_employees",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"current_active_employees\" AS VARCHAR) IS DISTINCT FROM CAST(\"high_value_stable_employees\" AS VARCHAR)),count(*) FILTER(WHERE \"current_active_employees\" IS NOT NULL AND \"high_value_stable_employees\" IS NOT NULL AND CAST(\"current_active_employees\" AS VARCHAR)=CAST(\"high_value_stable_employees\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "current_active_employees",
          "right": "high_value_flight_risk_employees",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"current_active_employees\" AS VARCHAR) IS DISTINCT FROM CAST(\"high_value_flight_risk_employees\" AS VARCHAR)),count(*) FILTER(WHERE \"current_active_employees\" IS NOT NULL AND \"high_value_flight_risk_employees\" IS NOT NULL AND CAST(\"current_active_employees\" AS VARCHAR)=CAST(\"high_value_flight_risk_employees\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "current_active_employees",
          "right": "stable_development_employees",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"current_active_employees\" AS VARCHAR) IS DISTINCT FROM CAST(\"stable_development_employees\" AS VARCHAR)),count(*) FILTER(WHERE \"current_active_employees\" IS NOT NULL AND \"stable_development_employees\" IS NOT NULL AND CAST(\"current_active_employees\" AS VARCHAR)=CAST(\"stable_development_employees\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "current_active_employees",
          "right": "development_required_employees",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"current_active_employees\" AS VARCHAR) IS DISTINCT FROM CAST(\"development_required_employees\" AS VARCHAR)),count(*) FILTER(WHERE \"current_active_employees\" IS NOT NULL AND \"development_required_employees\" IS NOT NULL AND CAST(\"current_active_employees\" AS VARCHAR)=CAST(\"development_required_employees\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "current_active_employees",
          "right": "high_risk_employees",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"current_active_employees\" AS VARCHAR) IS DISTINCT FROM CAST(\"high_risk_employees\" AS VARCHAR)),count(*) FILTER(WHERE \"current_active_employees\" IS NOT NULL AND \"high_risk_employees\" IS NOT NULL AND CAST(\"current_active_employees\" AS VARCHAR)=CAST(\"high_risk_employees\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "current_active_employees",
          "right": "medium_risk_employees",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"current_active_employees\" AS VARCHAR) IS DISTINCT FROM CAST(\"medium_risk_employees\" AS VARCHAR)),count(*) FILTER(WHERE \"current_active_employees\" IS NOT NULL AND \"medium_risk_employees\" IS NOT NULL AND CAST(\"current_active_employees\" AS VARCHAR)=CAST(\"medium_risk_employees\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "current_active_employees",
          "right": "low_risk_employees",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"current_active_employees\" AS VARCHAR) IS DISTINCT FROM CAST(\"low_risk_employees\" AS VARCHAR)),count(*) FILTER(WHERE \"current_active_employees\" IS NOT NULL AND \"low_risk_employees\" IS NOT NULL AND CAST(\"current_active_employees\" AS VARCHAR)=CAST(\"low_risk_employees\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "current_active_employees",
          "right": "new_hire_employees",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"current_active_employees\" AS VARCHAR) IS DISTINCT FROM CAST(\"new_hire_employees\" AS VARCHAR)),count(*) FILTER(WHERE \"current_active_employees\" IS NOT NULL AND \"new_hire_employees\" IS NOT NULL AND CAST(\"current_active_employees\" AS VARCHAR)=CAST(\"new_hire_employees\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "current_active_employees",
          "right": "junior_employees",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"current_active_employees\" AS VARCHAR) IS DISTINCT FROM CAST(\"junior_employees\" AS VARCHAR)),count(*) FILTER(WHERE \"current_active_employees\" IS NOT NULL AND \"junior_employees\" IS NOT NULL AND CAST(\"current_active_employees\" AS VARCHAR)=CAST(\"junior_employees\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "current_active_employees",
          "right": "experienced_employees",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"current_active_employees\" AS VARCHAR) IS DISTINCT FROM CAST(\"experienced_employees\" AS VARCHAR)),count(*) FILTER(WHERE \"current_active_employees\" IS NOT NULL AND \"experienced_employees\" IS NOT NULL AND CAST(\"current_active_employees\" AS VARCHAR)=CAST(\"experienced_employees\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "current_active_employees",
          "right": "senior_employees",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"current_active_employees\" AS VARCHAR) IS DISTINCT FROM CAST(\"senior_employees\" AS VARCHAR)),count(*) FILTER(WHERE \"current_active_employees\" IS NOT NULL AND \"senior_employees\" IS NOT NULL AND CAST(\"current_active_employees\" AS VARCHAR)=CAST(\"senior_employees\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "current_active_employees",
          "right": "veteran_employees",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"current_active_employees\" AS VARCHAR) IS DISTINCT FROM CAST(\"veteran_employees\" AS VARCHAR)),count(*) FILTER(WHERE \"current_active_employees\" IS NOT NULL AND \"veteran_employees\" IS NOT NULL AND CAST(\"current_active_employees\" AS VARCHAR)=CAST(\"veteran_employees\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "current_active_employees",
          "right": "ethnic_diversity_count",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"current_active_employees\" AS VARCHAR) IS DISTINCT FROM CAST(\"ethnic_diversity_count\" AS VARCHAR)),count(*) FILTER(WHERE \"current_active_employees\" IS NOT NULL AND \"ethnic_diversity_count\" IS NOT NULL AND CAST(\"current_active_employees\" AS VARCHAR)=CAST(\"ethnic_diversity_count\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "current_active_employees",
          "right": "military_veterans_count",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"current_active_employees\" AS VARCHAR) IS DISTINCT FROM CAST(\"military_veterans_count\" AS VARCHAR)),count(*) FILTER(WHERE \"current_active_employees\" IS NOT NULL AND \"military_veterans_count\" IS NOT NULL AND CAST(\"current_active_employees\" AS VARCHAR)=CAST(\"military_veterans_count\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "current_active_employees",
          "right": "entry_level_employees",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"current_active_employees\" AS VARCHAR) IS DISTINCT FROM CAST(\"entry_level_employees\" AS VARCHAR)),count(*) FILTER(WHERE \"current_active_employees\" IS NOT NULL AND \"entry_level_employees\" IS NOT NULL AND CAST(\"current_active_employees\" AS VARCHAR)=CAST(\"entry_level_employees\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "current_active_employees",
          "right": "mid_level_employees",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"current_active_employees\" AS VARCHAR) IS DISTINCT FROM CAST(\"mid_level_employees\" AS VARCHAR)),count(*) FILTER(WHERE \"current_active_employees\" IS NOT NULL AND \"mid_level_employees\" IS NOT NULL AND CAST(\"current_active_employees\" AS VARCHAR)=CAST(\"mid_level_employees\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "current_active_employees",
          "right": "senior_level_employees",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"current_active_employees\" AS VARCHAR) IS DISTINCT FROM CAST(\"senior_level_employees\" AS VARCHAR)),count(*) FILTER(WHERE \"current_active_employees\" IS NOT NULL AND \"senior_level_employees\" IS NOT NULL AND CAST(\"current_active_employees\" AS VARCHAR)=CAST(\"senior_level_employees\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "current_active_employees",
          "right": "executive_level_employees",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"current_active_employees\" AS VARCHAR) IS DISTINCT FROM CAST(\"executive_level_employees\" AS VARCHAR)),count(*) FILTER(WHERE \"current_active_employees\" IS NOT NULL AND \"executive_level_employees\" IS NOT NULL AND CAST(\"current_active_employees\" AS VARCHAR)=CAST(\"executive_level_employees\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "current_active_employees",
          "right": "total_promotions_in_organization",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"current_active_employees\" AS VARCHAR) IS DISTINCT FROM CAST(\"total_promotions_in_organization\" AS VARCHAR)),count(*) FILTER(WHERE \"current_active_employees\" IS NOT NULL AND \"total_promotions_in_organization\" IS NOT NULL AND CAST(\"current_active_employees\" AS VARCHAR)=CAST(\"total_promotions_in_organization\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "current_active_employees",
          "right": "high_achievers_count",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"current_active_employees\" AS VARCHAR) IS DISTINCT FROM CAST(\"high_achievers_count\" AS VARCHAR)),count(*) FILTER(WHERE \"current_active_employees\" IS NOT NULL AND \"high_achievers_count\" IS NOT NULL AND CAST(\"current_active_employees\" AS VARCHAR)=CAST(\"high_achievers_count\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "current_active_employees",
          "right": "fast_track_employees_count",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"current_active_employees\" AS VARCHAR) IS DISTINCT FROM CAST(\"fast_track_employees_count\" AS VARCHAR)),count(*) FILTER(WHERE \"current_active_employees\" IS NOT NULL AND \"fast_track_employees_count\" IS NOT NULL AND CAST(\"current_active_employees\" AS VARCHAR)=CAST(\"fast_track_employees_count\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "position_fill_rate",
          "right": "avg_current_tenure_years",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"position_fill_rate\" AS VARCHAR) IS DISTINCT FROM CAST(\"avg_current_tenure_years\" AS VARCHAR)),count(*) FILTER(WHERE \"position_fill_rate\" IS NOT NULL AND \"avg_current_tenure_years\" IS NOT NULL AND CAST(\"position_fill_rate\" AS VARCHAR)=CAST(\"avg_current_tenure_years\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "position_fill_rate",
          "right": "avg_employee_performance_score",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"position_fill_rate\" AS VARCHAR) IS DISTINCT FROM CAST(\"avg_employee_performance_score\" AS VARCHAR)),count(*) FILTER(WHERE \"position_fill_rate\" IS NOT NULL AND \"avg_employee_performance_score\" IS NOT NULL AND CAST(\"position_fill_rate\" AS VARCHAR)=CAST(\"avg_employee_performance_score\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "position_fill_rate",
          "right": "avg_career_development_score",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"position_fill_rate\" AS VARCHAR) IS DISTINCT FROM CAST(\"avg_career_development_score\" AS VARCHAR)),count(*) FILTER(WHERE \"position_fill_rate\" IS NOT NULL AND \"avg_career_development_score\" IS NOT NULL AND CAST(\"position_fill_rate\" AS VARCHAR)=CAST(\"avg_career_development_score\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "position_fill_rate",
          "right": "avg_retention_stability_score",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"position_fill_rate\" AS VARCHAR) IS DISTINCT FROM CAST(\"avg_retention_stability_score\" AS VARCHAR)),count(*) FILTER(WHERE \"position_fill_rate\" IS NOT NULL AND \"avg_retention_stability_score\" IS NOT NULL AND CAST(\"position_fill_rate\" AS VARCHAR)=CAST(\"avg_retention_stability_score\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        },
        {
          "left": "position_fill_rate",
          "right": "avg_employee_age",
          "sql": "SELECT count(*) FILTER(WHERE CAST(\"position_fill_rate\" AS VARCHAR) IS DISTINCT FROM CAST(\"avg_employee_age\" AS VARCHAR)),count(*) FILTER(WHERE \"position_fill_rate\" IS NOT NULL AND \"avg_employee_age\" IS NOT NULL AND CAST(\"position_fill_rate\" AS VARCHAR)=CAST(\"avg_employee_age\" AS VARCHAR)) FROM \"mart\".\"workday__organization_overview\"",
          "mismatch_rows": 0,
          "nonnull_equal_rows": 117
        }
      ],
      "equality_policy": "exact CAST AS VARCHAR per row; no trim/case/numeric/date normalization; both NULL ignored; at least one nonnull equal row; one-sided NULL differs",
      "actual_schema": "mart",
      "actual_table": "workday__organization_overview",
      "relation_type": "BASE TABLE"
    },
    "agent_sql": [
      {
        "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
        "status": "parsed",
        "parser": "30.25.0",
        "sources": [
          {
            "name": "staging.stg_workday__organization",
            "canonical": "staging.stg_workday__organization",
            "locations": [
              {
                "line": 1,
                "end_line": 1
              }
            ]
          },
          {
            "name": "staging.stg_workday__worker_position_organization",
            "canonical": "staging.stg_workday__worker_position_organization",
            "locations": [
              {
                "line": 5,
                "end_line": 5
              }
            ]
          },
          {
            "name": "staging.stg_workday__organization_role_worker",
            "canonical": "staging.stg_workday__organization_role_worker",
            "locations": [
              {
                "line": 11,
                "end_line": 11
              }
            ]
          },
          {
            "name": "staging.stg_workday__organization_role",
            "canonical": "staging.stg_workday__organization_role",
            "locations": [
              {
                "line": 11,
                "end_line": 11
              }
            ]
          },
          {
            "name": "mart.workday__employee_overview",
            "canonical": "marts.workday__employee_overview",
            "locations": [
              {
                "line": 20,
                "end_line": 20
              }
            ]
          }
        ],
        "unresolved_source_expressions": [],
        "row_generator_expressions": [],
        "outputs": [
          {
            "name": "organization_id",
            "alternatives": [
              {
                "expression_sql": "organization_id",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 22,
                "end_line": 22,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "organization_id",
            "retained_output_ordinal": 1
          },
          {
            "name": "source_relation",
            "alternatives": [
              {
                "expression_sql": "source_relation",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 22,
                "end_line": 22,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "source_relation",
            "retained_output_ordinal": 2
          },
          {
            "name": "organization_name",
            "alternatives": [
              {
                "expression_sql": "organization_name",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 22,
                "end_line": 22,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "organization_name",
            "retained_output_ordinal": 3
          },
          {
            "name": "organization_code",
            "alternatives": [
              {
                "expression_sql": "organization_code",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 22,
                "end_line": 22,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "organization_code",
            "retained_output_ordinal": 4
          },
          {
            "name": "organization_type",
            "alternatives": [
              {
                "expression_sql": "organization_type",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 22,
                "end_line": 22,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "organization_type",
            "retained_output_ordinal": 5
          },
          {
            "name": "organization_sub_type",
            "alternatives": [
              {
                "expression_sql": "organization_sub_type",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 22,
                "end_line": 22,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "organization_sub_type",
            "retained_output_ordinal": 6
          },
          {
            "name": "staffing_model",
            "alternatives": [
              {
                "expression_sql": "staffing_model",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 22,
                "end_line": 22,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "staffing_model",
            "retained_output_ordinal": 7
          },
          {
            "name": "visibility",
            "alternatives": [
              {
                "expression_sql": "visibility",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 22,
                "end_line": 22,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "visibility",
            "retained_output_ordinal": 8
          },
          {
            "name": "access_level",
            "alternatives": [
              {
                "expression_sql": "CASE visibility WHEN 'Public' THEN 'Open Access' WHEN 'Private' THEN 'Restricted Access' ELSE 'Unknown Access' END",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 23,
                "end_line": 23,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "access_level",
            "retained_output_ordinal": 9
          },
          {
            "name": "organization_created_date",
            "alternatives": [
              {
                "expression_sql": "effective_start",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 23,
                "end_line": 23,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "organization_created_date",
            "retained_output_ordinal": 10
          },
          {
            "name": "organization_age_days",
            "alternatives": [
              {
                "expression_sql": "CAST(DATE_DIFF('DAY', effective_start, CURRENT_DATE) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 23,
                "end_line": 23,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "organization_age_days",
            "retained_output_ordinal": 11
          },
          {
            "name": "organization_age_years",
            "alternatives": [
              {
                "expression_sql": "CAST(ROUND(DATE_DIFF('DAY', effective_start, CURRENT_DATE) / 365.0, 2) AS DOUBLE)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 23,
                "end_line": 23,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "organization_age_years",
            "retained_output_ordinal": 12
          },
          {
            "name": "organization_maturity_level",
            "alternatives": [
              {
                "expression_sql": "CASE WHEN DATE_DIFF('DAY', effective_start, CURRENT_DATE) < 365 THEN 'New' WHEN DATE_DIFF('DAY', effective_start, CURRENT_DATE) < 1095 THEN 'Young' WHEN DATE_DIFF('DAY', effective_start, CURRENT_DATE) < 3650 THEN 'Mature' ELSE 'Legacy' END",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 24,
                "end_line": 24,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "organization_maturity_level",
            "retained_output_ordinal": 13
          },
          {
            "name": "organizational_level",
            "alternatives": [
              {
                "expression_sql": "CASE organization_type WHEN 'Company' THEN 'Corporate Level' WHEN 'Division' THEN 'Division Level' WHEN 'Department' THEN 'Department Level' WHEN 'Team' THEN 'Team Level' ELSE 'Other Level' END",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 25,
                "end_line": 25,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "organizational_level",
            "retained_output_ordinal": 14
          },
          {
            "name": "total_employees_ever",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(total_employees_ever, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 26,
                "end_line": 26,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "total_employees_ever",
            "retained_output_ordinal": 15
          },
          {
            "name": "current_active_employees",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(current_active_employees, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 26,
                "end_line": 26,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "current_active_employees",
            "retained_output_ordinal": 16
          },
          {
            "name": "former_employees",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(former_employees, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 26,
                "end_line": 26,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "former_employees",
            "retained_output_ordinal": 17
          },
          {
            "name": "total_positions",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(total_positions, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 26,
                "end_line": 26,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "total_positions",
            "retained_output_ordinal": 18
          },
          {
            "name": "active_positions_count",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(active_positions_count, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 26,
                "end_line": 26,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "active_positions_count",
            "retained_output_ordinal": 19
          },
          {
            "name": "position_fill_rate",
            "alternatives": [
              {
                "expression_sql": "CAST(ROUND(COALESCE(current_active_employees, 0) * 100.0 / NULLIF(total_positions, 0), 2) AS DOUBLE)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 27,
                "end_line": 27,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "position_fill_rate",
            "retained_output_ordinal": 20
          },
          {
            "name": "new_assignments_last_year",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(new_assignments_last_year, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 27,
                "end_line": 27,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "new_assignments_last_year",
            "retained_output_ordinal": 21
          },
          {
            "name": "departures_last_year",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(departures_last_year, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 27,
                "end_line": 27,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "departures_last_year",
            "retained_output_ordinal": 22
          },
          {
            "name": "annual_turnover_rate",
            "alternatives": [
              {
                "expression_sql": "CAST(ROUND(COALESCE(departures_last_year, 0) * 100.0 / NULLIF(current_active_employees, 0), 2) AS DOUBLE)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 27,
                "end_line": 27,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "annual_turnover_rate",
            "retained_output_ordinal": 23
          },
          {
            "name": "avg_current_tenure_years",
            "alternatives": [
              {
                "expression_sql": "CAST(ROUND(COALESCE(avg_current_days, 0) / 365.0, 2) AS DOUBLE)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 28,
                "end_line": 28,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "avg_current_tenure_years",
            "retained_output_ordinal": 24
          },
          {
            "name": "avg_former_tenure_years",
            "alternatives": [
              {
                "expression_sql": "CAST(ROUND(COALESCE(avg_former_days, 0) / 365.0, 2) AS DOUBLE)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 28,
                "end_line": 28,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "avg_former_tenure_years",
            "retained_output_ordinal": 25
          },
          {
            "name": "unique_organization_roles",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(unique_organization_roles, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 28,
                "end_line": 28,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "unique_organization_roles",
            "retained_output_ordinal": 26
          },
          {
            "name": "management_role_employees",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(management_role_employees, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 28,
                "end_line": 28,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "management_role_employees",
            "retained_output_ordinal": 27
          },
          {
            "name": "director_role_employees",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(director_role_employees, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 28,
                "end_line": 28,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "director_role_employees",
            "retained_output_ordinal": 28
          },
          {
            "name": "lead_role_employees",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(lead_role_employees, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 28,
                "end_line": 28,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "lead_role_employees",
            "retained_output_ordinal": 29
          },
          {
            "name": "management_ratio",
            "alternatives": [
              {
                "expression_sql": "CAST(ROUND((COALESCE(management_role_employees, 0) + COALESCE(director_role_employees, 0)) * 100.0 / NULLIF(current_active_employees, 0), 2) AS DOUBLE)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 29,
                "end_line": 29,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "management_ratio",
            "retained_output_ordinal": 30
          },
          {
            "name": "avg_employee_performance_score",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(avg_employee_performance_score, 0) AS DOUBLE)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 29,
                "end_line": 29,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "avg_employee_performance_score",
            "retained_output_ordinal": 31
          },
          {
            "name": "avg_career_development_score",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(avg_career_development_score, 0) AS DOUBLE)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 29,
                "end_line": 29,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "avg_career_development_score",
            "retained_output_ordinal": 32
          },
          {
            "name": "avg_retention_stability_score",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(avg_retention_stability_score, 0) AS DOUBLE)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 29,
                "end_line": 29,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "avg_retention_stability_score",
            "retained_output_ordinal": 33
          },
          {
            "name": "high_value_stable_employees",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(high_value_stable_employees, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 30,
                "end_line": 30,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "high_value_stable_employees",
            "retained_output_ordinal": 34
          },
          {
            "name": "high_value_flight_risk_employees",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(high_value_flight_risk_employees, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 30,
                "end_line": 30,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "high_value_flight_risk_employees",
            "retained_output_ordinal": 35
          },
          {
            "name": "stable_development_employees",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(stable_development_employees, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 30,
                "end_line": 30,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "stable_development_employees",
            "retained_output_ordinal": 36
          },
          {
            "name": "development_required_employees",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(development_required_employees, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 30,
                "end_line": 30,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "development_required_employees",
            "retained_output_ordinal": 37
          },
          {
            "name": "high_risk_employees",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(high_risk_employees, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 30,
                "end_line": 30,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "high_risk_employees",
            "retained_output_ordinal": 38
          },
          {
            "name": "medium_risk_employees",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(medium_risk_employees, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 30,
                "end_line": 30,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "medium_risk_employees",
            "retained_output_ordinal": 39
          },
          {
            "name": "low_risk_employees",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(low_risk_employees, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 30,
                "end_line": 30,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "low_risk_employees",
            "retained_output_ordinal": 40
          },
          {
            "name": "high_risk_employee_percentage",
            "alternatives": [
              {
                "expression_sql": "CAST(ROUND(COALESCE(high_risk_employees, 0) * 100.0 / NULLIF(current_active_employees, 0), 2) AS DOUBLE)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 31,
                "end_line": 31,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "high_risk_employee_percentage",
            "retained_output_ordinal": 41
          },
          {
            "name": "new_hire_employees",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(new_hire_employees, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 31,
                "end_line": 31,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "new_hire_employees",
            "retained_output_ordinal": 42
          },
          {
            "name": "junior_employees",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(junior_employees, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 31,
                "end_line": 31,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "junior_employees",
            "retained_output_ordinal": 43
          },
          {
            "name": "experienced_employees",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(experienced_employees, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 31,
                "end_line": 31,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "experienced_employees",
            "retained_output_ordinal": 44
          },
          {
            "name": "senior_employees",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(senior_employees, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 31,
                "end_line": 31,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "senior_employees",
            "retained_output_ordinal": 45
          },
          {
            "name": "veteran_employees",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(veteran_employees, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 31,
                "end_line": 31,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "veteran_employees",
            "retained_output_ordinal": 46
          },
          {
            "name": "ethnic_diversity_count",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(ethnic_diversity_count, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 31,
                "end_line": 31,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "ethnic_diversity_count",
            "retained_output_ordinal": 47
          },
          {
            "name": "military_veterans_count",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(military_veterans_count, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 31,
                "end_line": 31,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "military_veterans_count",
            "retained_output_ordinal": 48
          },
          {
            "name": "avg_employee_age",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(avg_employee_age, 0) AS DOUBLE)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 31,
                "end_line": 31,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "avg_employee_age",
            "retained_output_ordinal": 49
          },
          {
            "name": "entry_level_employees",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(entry_level_employees, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 32,
                "end_line": 32,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "entry_level_employees",
            "retained_output_ordinal": 50
          },
          {
            "name": "mid_level_employees",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(mid_level_employees, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 32,
                "end_line": 32,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "mid_level_employees",
            "retained_output_ordinal": 51
          },
          {
            "name": "senior_level_employees",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(senior_level_employees, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 32,
                "end_line": 32,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "senior_level_employees",
            "retained_output_ordinal": 52
          },
          {
            "name": "executive_level_employees",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(executive_level_employees, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 32,
                "end_line": 32,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "executive_level_employees",
            "retained_output_ordinal": 53
          },
          {
            "name": "total_promotions_in_organization",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(total_promotions_in_organization, 0) AS INT128)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 32,
                "end_line": 32,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "total_promotions_in_organization",
            "retained_output_ordinal": 54
          },
          {
            "name": "high_achievers_count",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(high_achievers_count, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 32,
                "end_line": 32,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "high_achievers_count",
            "retained_output_ordinal": 55
          },
          {
            "name": "fast_track_employees_count",
            "alternatives": [
              {
                "expression_sql": "CAST(COALESCE(fast_track_employees_count, 0) AS BIGINT)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 32,
                "end_line": 32,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "fast_track_employees_count",
            "retained_output_ordinal": 56
          },
          {
            "name": "organization_health_score",
            "alternatives": [
              {
                "expression_sql": "CAST(ROUND(LEAST(30, COALESCE(avg_employee_performance_score, 0) * 0.3) + CASE WHEN departures_last_year = 0 THEN 25 WHEN annual_turnover_rate <= 10 THEN 25 WHEN annual_turnover_rate <= 20 THEN 20 WHEN annual_turnover_rate <= 30 THEN 15 WHEN annual_turnover_rate <= 40 THEN 10 ELSE 5 END + LEAST(20, COALESCE(avg_career_development_score, 0) * 0.2) + CASE WHEN position_fill_rate >= 90 THEN 15 WHEN position_fill_rate >= 75 THEN 12 WHEN position_fill_rate >= 60 THEN 9 ELSE 6 END + CASE WHEN high_risk_employee_percentage <= 10 THEN 10 WHEN high_risk_employee_percentage <= 20 THEN 7 WHEN high_risk_employee_percentage <= 30 THEN 4 ELSE 2 END, 2) AS DOUBLE)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 33,
                "end_line": 33,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "organization_health_score",
            "retained_output_ordinal": 57
          },
          {
            "name": "performance_category",
            "alternatives": [
              {
                "expression_sql": "CASE WHEN avg_employee_performance_score >= 80 THEN 'Excellent' WHEN avg_employee_performance_score >= 60 THEN 'Good' WHEN avg_employee_performance_score >= 40 THEN 'Average' ELSE 'Needs Improvement' END",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 34,
                "end_line": 34,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "performance_category",
            "retained_output_ordinal": 58
          },
          {
            "name": "organization_size_category",
            "alternatives": [
              {
                "expression_sql": "CASE WHEN current_active_employees = 0 THEN 'Empty' WHEN current_active_employees <= 5 THEN 'Micro' WHEN current_active_employees <= 15 THEN 'Small' WHEN current_active_employees <= 50 THEN 'Medium' WHEN current_active_employees <= 200 THEN 'Large' ELSE 'Enterprise' END",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 35,
                "end_line": 35,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "organization_size_category",
            "retained_output_ordinal": 59
          },
          {
            "name": "last_activity_date",
            "alternatives": [
              {
                "expression_sql": "COALESCE(last_activity_date, effective_start)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 36,
                "end_line": 36,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "last_activity_date",
            "retained_output_ordinal": 60
          },
          {
            "name": "last_departure_date",
            "alternatives": [
              {
                "expression_sql": "COALESCE(last_departure_date, CAST('1900-01-01' AS DATE))",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 36,
                "end_line": 36,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "last_departure_date",
            "retained_output_ordinal": 61
          },
          {
            "name": "management_recommendation",
            "alternatives": [
              {
                "expression_sql": "CASE WHEN current_active_employees = 0 THEN 'Review Organization Necessity' WHEN annual_turnover_rate > 30 THEN 'Focus on Retention' WHEN high_risk_employee_percentage > 25 THEN 'Address Employee Risk' WHEN position_fill_rate < 70 THEN 'Improve Staffing' WHEN avg_employee_performance_score < 50 THEN 'Enhance Performance Management' WHEN management_ratio > 40 THEN 'Optimize Structure' ELSE 'Maintain Excellence' END",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 37,
                "end_line": 37,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "management_recommendation",
            "retained_output_ordinal": 62
          },
          {
            "name": "data_quality_flag",
            "alternatives": [
              {
                "expression_sql": "CASE WHEN organization_name IS NULL OR TRIM(organization_name) = '' THEN 'ERROR: Missing organization name' WHEN current_active_employees > total_positions + 10 THEN 'WARNING: Employees exceed positions' WHEN annual_turnover_rate > 100 THEN 'WARNING: Turnover exceeds 100%' WHEN organization_age_days < 0 THEN 'ERROR: Negative organization age' ELSE 'VALID' END",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 38,
                "end_line": 38,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "data_quality_flag",
            "retained_output_ordinal": 63
          },
          {
            "name": "analysis_timestamp",
            "alternatives": [
              {
                "expression_sql": "CAST(CURRENT_TIMESTAMP AS TIMESTAMPTZ)",
                "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
                "line": 38,
                "end_line": 38,
                "kind": "nonliteral"
              }
            ],
            "sql_projection_name": "analysis_timestamp",
            "retained_output_ordinal": 64
          }
        ],
        "null_literal_outputs": [],
        "constant_literal_outputs": [],
        "runtime_hits": [
          {
            "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
            "line": 3,
            "column": 57,
            "matched_text": "current_date",
            "line_text": " date_diff('day',effective_start,coalesce(effective_end,current_date)) duration,",
            "context": "code"
          },
          {
            "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
            "line": 8,
            "column": 58,
            "matched_text": "current_date",
            "line_text": " count(DISTINCT worker_id) FILTER(WHERE effective_start>=current_date-INTERVAL '1 year') new_assignments_last_year,count(DISTINCT worker_id) FILTER(WHERE effective_end>=current_date-INTERVAL '1 year') departures_last_year,avg(duration) FILTER(WHERE effective_end IS NULL) avg_current_days,avg(duration) FILTER(WHERE effective_end IS NOT NULL) avg_former_days,max(effective_start) last_activity_date,max(effective_end) last_departure_date",
            "context": "code"
          },
          {
            "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
            "line": 8,
            "column": 170,
            "matched_text": "current_date",
            "line_text": " count(DISTINCT worker_id) FILTER(WHERE effective_start>=current_date-INTERVAL '1 year') new_assignments_last_year,count(DISTINCT worker_id) FILTER(WHERE effective_end>=current_date-INTERVAL '1 year') departures_last_year,avg(duration) FILTER(WHERE effective_end IS NULL) avg_current_days,avg(duration) FILTER(WHERE effective_end IS NOT NULL) avg_former_days,max(effective_start) last_activity_date,max(effective_end) last_departure_date",
            "context": "code"
          },
          {
            "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
            "line": 23,
            "column": 203,
            "matched_text": "current_date",
            "line_text": "CASE visibility WHEN 'Public' THEN 'Open Access' WHEN 'Private' THEN 'Restricted Access' ELSE 'Unknown Access' END access_level,effective_start organization_created_date,date_diff('day',effective_start,current_date)::BIGINT organization_age_days,round(date_diff('day',effective_start,current_date)/365.0,2)::DOUBLE organization_age_years,",
            "context": "code"
          },
          {
            "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
            "line": 23,
            "column": 285,
            "matched_text": "current_date",
            "line_text": "CASE visibility WHEN 'Public' THEN 'Open Access' WHEN 'Private' THEN 'Restricted Access' ELSE 'Unknown Access' END access_level,effective_start organization_created_date,date_diff('day',effective_start,current_date)::BIGINT organization_age_days,round(date_diff('day',effective_start,current_date)/365.0,2)::DOUBLE organization_age_years,",
            "context": "code"
          },
          {
            "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
            "line": 24,
            "column": 43,
            "matched_text": "current_date",
            "line_text": "CASE WHEN date_diff('day',effective_start,current_date)<365 THEN 'New' WHEN date_diff('day',effective_start,current_date)<1095 THEN 'Young' WHEN date_diff('day',effective_start,current_date)<3650 THEN 'Mature' ELSE 'Legacy' END organization_maturity_level,",
            "context": "code"
          },
          {
            "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
            "line": 24,
            "column": 109,
            "matched_text": "current_date",
            "line_text": "CASE WHEN date_diff('day',effective_start,current_date)<365 THEN 'New' WHEN date_diff('day',effective_start,current_date)<1095 THEN 'Young' WHEN date_diff('day',effective_start,current_date)<3650 THEN 'Mature' ELSE 'Legacy' END organization_maturity_level,",
            "context": "code"
          },
          {
            "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
            "line": 24,
            "column": 178,
            "matched_text": "current_date",
            "line_text": "CASE WHEN date_diff('day',effective_start,current_date)<365 THEN 'New' WHEN date_diff('day',effective_start,current_date)<1095 THEN 'Young' WHEN date_diff('day',effective_start,current_date)<3650 THEN 'Mature' ELSE 'Legacy' END organization_maturity_level,",
            "context": "code"
          },
          {
            "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
            "line": 38,
            "column": 371,
            "matched_text": "current_timestamp",
            "line_text": "CASE WHEN organization_name IS NULL OR trim(organization_name)='' THEN 'ERROR: Missing organization name' WHEN current_active_employees>total_positions+10 THEN 'WARNING: Employees exceed positions' WHEN annual_turnover_rate>100 THEN 'WARNING: Turnover exceeds 100%' WHEN organization_age_days<0 THEN 'ERROR: Negative organization age' ELSE 'VALID' END data_quality_flag,current_timestamp::TIMESTAMPTZ analysis_timestamp",
            "context": "code"
          }
        ]
      }
    ],
    "source_comparison": {
      "contract": {
        "status": "specified",
        "references": [
          {
            "name": "staging.stg_workday__organization (filtered to is_inactive = false)",
            "canonical": "staging.stg_workday__organization (filtered to is_inactive = false)",
            "basis": "source_models",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
            "block_start_line": 2024
          },
          {
            "name": "staging.stg_workday__worker_position_organization",
            "canonical": "staging.stg_workday__worker_position_organization",
            "basis": "source_models",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
            "block_start_line": 2024
          },
          {
            "name": "staging.stg_workday__organization_role_worker",
            "canonical": "staging.stg_workday__organization_role_worker",
            "basis": "source_models",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
            "block_start_line": 2024
          },
          {
            "name": "staging.stg_workday__organization_role",
            "canonical": "staging.stg_workday__organization_role",
            "basis": "source_models",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
            "block_start_line": 2024
          },
          {
            "name": "mart.workday__employee_overview (filtered to organization_id != 'Unknown')",
            "canonical": "marts.workday__employee_overview (filtered to organization_id != 'unknown')",
            "basis": "source_models",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
            "block_start_line": 2024
          },
          {
            "name": "staging.stg_workday__organization",
            "canonical": "staging.stg_workday__organization",
            "basis": "explicit_schema_qualified_reference_in_original_block",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
            "line": 2028,
            "line_text": "      - staging.stg_workday__organization (filtered to is_inactive = false)"
          },
          {
            "name": "staging.stg_workday__worker_position_organization",
            "canonical": "staging.stg_workday__worker_position_organization",
            "basis": "explicit_schema_qualified_reference_in_original_block",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
            "line": 2029,
            "line_text": "      - staging.stg_workday__worker_position_organization"
          },
          {
            "name": "staging.stg_workday__organization_role_worker",
            "canonical": "staging.stg_workday__organization_role_worker",
            "basis": "explicit_schema_qualified_reference_in_original_block",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
            "line": 2030,
            "line_text": "      - staging.stg_workday__organization_role_worker"
          },
          {
            "name": "staging.stg_workday__organization_role",
            "canonical": "staging.stg_workday__organization_role",
            "basis": "explicit_schema_qualified_reference_in_original_block",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
            "line": 2031,
            "line_text": "      - staging.stg_workday__organization_role"
          },
          {
            "name": "mart.workday__employee_overview",
            "canonical": "marts.workday__employee_overview",
            "basis": "explicit_schema_qualified_reference_in_original_block",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
            "line": 2032,
            "line_text": "      - mart.workday__employee_overview (filtered to organization_id != 'Unknown')"
          },
          {
            "name": "mart.workday__employee_overview",
            "canonical": "marts.workday__employee_overview",
            "basis": "explicit_schema_qualified_reference_in_original_block",
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
            "line": 2033,
            "line_text": "      business_logic: '1) Filter organizations to active only and expose attributes and effective_start as the creation date. 2) Build worker–organization–role relationships by left joining worker positions to role-worker and role master on matching worker, role, source_relation, and organization_id. For each assignment: - assignment_status: ''Active Assignment'' if end date is null, else ''Former Assignment''. - assignment_duration_days: days between start and end; if end is null, days between start and current_date. - carry organization_role_id and organization_role_code from the role join. 3) Aggregate organization_employee_stats by (organization_id, source_relation): - total_employees_ever: distinct workers across all assignments. - current_active_employees: distinct workers with Active Assignment. - former_employees: distinct workers with Former Assignment. - total_positions_in_org: distinct positions across all assignments. - active_positions_count: distinct positions with Active Assignment. - new_assignments_last_year: distinct workers with start date in the last year relative to current_date. - departures_last_year: distinct workers with a non-null end date in the last year. - avg_current_tenure_days: average assignment_duration_days for Active Assignments. - avg_former_tenure_days: average assignment_duration_days for Former Assignments. - unique_organization_roles: distinct organization_role_id. - management_role_employees / director_role_employees / lead_role_employees: distinct workers where role code contains ''Manager'' / ''Director'' / ''Lead''. - last_new_assignment_date: most recent start date; last_departure_date: most recent end date. 4) Aggregate organization_performance_metrics from mart.workday__employee_overview by (organization_id, source_relation), excluding organization_id = ''Unknown'': - Averages over currently employed workers only: overall_employee_score and career_development_score rounded to 2 decimals; retention_stability_score rounded to 2 decimals; age rounded to 1 decimal. - Employee value segments: distinct workers by segment (''High Value - High Retention'', ''High Value - Flight Risk'', ''Stable - Development Needed'', ''Development Required''); no employment filter. - Risk distribution: distinct workers by employee_risk_level (High/Medium/Low); no employment filter. - Maturity segments: distinct employed workers where maturity contains ''New Hire'' / ''Junior'' / ''Experienced'' / ''Senior'' / ''Veteran''. - Diversity: distinct ethnicity_codes among employed; military_veterans_count is distinct employed workers flagged for military service. - Compensation tiers: distinct employed workers by compensation_tier (Entry/Mid/Senior/Executive Level). - Promotions among employed: total_promotions summed; high_achievers_count is distinct workers with total_promotions ≥ 2; fast_track_employees_count is distinct workers with fast_promotions > 0. 5) Derive organization attributes per active organization: - organization_created_date from effective_start. - organization_age_days as days from creation to current_date; organization_age_years is that divided by 365, rounded to 2 decimals. - organization_maturity_level by age_days: <1 year New; 1–3 years Young; 3–10 years Mature; 10+ years Legacy. - organizational_level from organization_type: Company/Division/Department/Team mapped to corresponding Level; others to Other Level. - access_level from visibility: Public→Open Access, Private→Restricted Access, others Unknown Access. 6) Final metrics and rules (rates rounded to 2 decimals; missing metrics default to 0 unless noted): - position_fill_rate (%) = current_active_employees ÷ total_positions × 100 when total_positions > 0, else 0. - annual_turnover_rate (%) = departures_last_year ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - avg_current_tenure_years and avg_former_tenure_years = respective average tenure days ÷ 365, rounded to 2; if no data, treated as 0. - management_ratio (%) = (management_role_employees + director_role_employees) ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - high_risk_employee_percentage (%) = high_risk_employees ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - organization_health_score (0–100) = sum of: performance (cap at 30% of average performance), turnover (25/20/15/10/5 by thresholds using annual_turnover_rate and zero departures case), development (cap at 20% of average career development), efficiency (15/12/9/6 by position_fill_rate thresholds), and risk (10/7/4/2 by high_risk_employee_percentage thresholds); final score rounded to 2 decimals. - performance_category uses a weighted composite with thresholds: Excellent if composite ≥ 80; else Good if ≥ 60; else Average if ≥ 40; otherwise Needs Improvement (weights and constants follow the detailed rules above). - organization_size_category by current_active_employees: 0 Empty; ≤5 Micro; ≤15 Small; ≤50 Medium; ≤200 Large; else Enterprise. - last_activity_date is the most recent assignment start; if none, use organization_created_date. - last_departure_date is the most recent assignment end; if none, use 1900-01-01. - management_recommendation (first match): if no active employees then review necessity; else if turnover > 30% then focus on retention; else if high-risk % > 25% then address risk; else if fill rate < 70% then improve staffing; else if average performance < 50 then enhance performance management; else if management_ratio > 40% then optimize structure; else maintain excellence. - data_quality_flag precedence: missing or blank organization name → ERROR; active employees exceed positions by more than 10 → WARNING; turnover rate > 100% → WARNING; negative age days → ERROR; otherwise VALID. - analysis_timestamp is the query execution timestamp. 7) Join logic: left join employee stats and performance metrics to active organizations on (organization_id, source_relation); missing measures default to 0. The final ordering is for presentation only and does not affect grain.'"
          }
        ],
        "canonical_names": [
          "marts.workday__employee_overview",
          "marts.workday__employee_overview (filtered to organization_id != 'unknown')",
          "staging.stg_workday__organization",
          "staging.stg_workday__organization (filtered to is_inactive = false)",
          "staging.stg_workday__organization_role",
          "staging.stg_workday__organization_role_worker",
          "staging.stg_workday__worker_position_organization"
        ]
      },
      "agent_direct_read_sources": [
        "marts.workday__employee_overview",
        "staging.stg_workday__organization",
        "staging.stg_workday__organization_role",
        "staging.stg_workday__organization_role_worker",
        "staging.stg_workday__worker_position_organization"
      ],
      "scope": "direct physical relation references through reachable local CTE/subqueries; no transitive expansion through other output tables or stored views",
      "complete": true,
      "specified_but_not_read": [
        "marts.workday__employee_overview (filtered to organization_id != 'unknown')",
        "staging.stg_workday__organization (filtered to is_inactive = false)"
      ],
      "read_but_not_specified": []
    },
    "time_dependencies": {
      "agent_sql": {
        "available": true,
        "appears": true,
        "hits": [
          {
            "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
            "line": 3,
            "column": 57,
            "matched_text": "current_date",
            "line_text": " date_diff('day',effective_start,coalesce(effective_end,current_date)) duration,",
            "context": "code"
          },
          {
            "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
            "line": 8,
            "column": 58,
            "matched_text": "current_date",
            "line_text": " count(DISTINCT worker_id) FILTER(WHERE effective_start>=current_date-INTERVAL '1 year') new_assignments_last_year,count(DISTINCT worker_id) FILTER(WHERE effective_end>=current_date-INTERVAL '1 year') departures_last_year,avg(duration) FILTER(WHERE effective_end IS NULL) avg_current_days,avg(duration) FILTER(WHERE effective_end IS NOT NULL) avg_former_days,max(effective_start) last_activity_date,max(effective_end) last_departure_date",
            "context": "code"
          },
          {
            "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
            "line": 8,
            "column": 170,
            "matched_text": "current_date",
            "line_text": " count(DISTINCT worker_id) FILTER(WHERE effective_start>=current_date-INTERVAL '1 year') new_assignments_last_year,count(DISTINCT worker_id) FILTER(WHERE effective_end>=current_date-INTERVAL '1 year') departures_last_year,avg(duration) FILTER(WHERE effective_end IS NULL) avg_current_days,avg(duration) FILTER(WHERE effective_end IS NOT NULL) avg_former_days,max(effective_start) last_activity_date,max(effective_end) last_departure_date",
            "context": "code"
          },
          {
            "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
            "line": 23,
            "column": 203,
            "matched_text": "current_date",
            "line_text": "CASE visibility WHEN 'Public' THEN 'Open Access' WHEN 'Private' THEN 'Restricted Access' ELSE 'Unknown Access' END access_level,effective_start organization_created_date,date_diff('day',effective_start,current_date)::BIGINT organization_age_days,round(date_diff('day',effective_start,current_date)/365.0,2)::DOUBLE organization_age_years,",
            "context": "code"
          },
          {
            "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
            "line": 23,
            "column": 285,
            "matched_text": "current_date",
            "line_text": "CASE visibility WHEN 'Public' THEN 'Open Access' WHEN 'Private' THEN 'Restricted Access' ELSE 'Unknown Access' END access_level,effective_start organization_created_date,date_diff('day',effective_start,current_date)::BIGINT organization_age_days,round(date_diff('day',effective_start,current_date)/365.0,2)::DOUBLE organization_age_years,",
            "context": "code"
          },
          {
            "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
            "line": 24,
            "column": 43,
            "matched_text": "current_date",
            "line_text": "CASE WHEN date_diff('day',effective_start,current_date)<365 THEN 'New' WHEN date_diff('day',effective_start,current_date)<1095 THEN 'Young' WHEN date_diff('day',effective_start,current_date)<3650 THEN 'Mature' ELSE 'Legacy' END organization_maturity_level,",
            "context": "code"
          },
          {
            "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
            "line": 24,
            "column": 109,
            "matched_text": "current_date",
            "line_text": "CASE WHEN date_diff('day',effective_start,current_date)<365 THEN 'New' WHEN date_diff('day',effective_start,current_date)<1095 THEN 'Young' WHEN date_diff('day',effective_start,current_date)<3650 THEN 'Mature' ELSE 'Legacy' END organization_maturity_level,",
            "context": "code"
          },
          {
            "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
            "line": 24,
            "column": 178,
            "matched_text": "current_date",
            "line_text": "CASE WHEN date_diff('day',effective_start,current_date)<365 THEN 'New' WHEN date_diff('day',effective_start,current_date)<1095 THEN 'Young' WHEN date_diff('day',effective_start,current_date)<3650 THEN 'Mature' ELSE 'Legacy' END organization_maturity_level,",
            "context": "code"
          },
          {
            "path": "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
            "line": 38,
            "column": 371,
            "matched_text": "current_timestamp",
            "line_text": "CASE WHEN organization_name IS NULL OR trim(organization_name)='' THEN 'ERROR: Missing organization name' WHEN current_active_employees>total_positions+10 THEN 'WARNING: Employees exceed positions' WHEN annual_turnover_rate>100 THEN 'WARNING: Turnover exceeds 100%' WHEN organization_age_days<0 THEN 'ERROR: Negative organization age' ELSE 'VALID' END data_quality_flag,current_timestamp::TIMESTAMPTZ analysis_timestamp",
            "context": "code"
          }
        ]
      },
      "gold_sql": {
        "available": true,
        "appears": true,
        "hits": [
          {
            "path": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
            "line": 28,
            "column": 55,
            "matched_text": "current_date",
            "line_text": "                date_diff('day', wpo.effective_start, current_date)",
            "context": "code"
          },
          {
            "path": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
            "line": 59,
            "column": 63,
            "matched_text": "current_date",
            "line_text": "        count(distinct case when oer.assignment_start_date >= current_date - interval '1 year' then oer.worker_id end) as new_assignments_last_year,",
            "context": "code"
          },
          {
            "path": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
            "line": 60,
            "column": 61,
            "matched_text": "current_date",
            "line_text": "        count(distinct case when oer.assignment_end_date >= current_date - interval '1 year' and oer.assignment_end_date is not null then oer.worker_id end) as departures_last_year,",
            "context": "code"
          },
          {
            "path": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
            "line": 144,
            "column": 46,
            "matched_text": "current_date",
            "line_text": "        date_diff('day', ob.effective_start, current_date) as organization_age_days,",
            "context": "code"
          },
          {
            "path": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
            "line": 146,
            "column": 55,
            "matched_text": "current_date",
            "line_text": "            when date_diff('day', ob.effective_start, current_date) < 365 then 'New Organization (<1 year)'",
            "context": "code"
          },
          {
            "path": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
            "line": 147,
            "column": 55,
            "matched_text": "current_date",
            "line_text": "            when date_diff('day', ob.effective_start, current_date) < 365*3 then 'Young Organization (1-3 years)'",
            "context": "code"
          },
          {
            "path": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
            "line": 148,
            "column": 55,
            "matched_text": "current_date",
            "line_text": "            when date_diff('day', ob.effective_start, current_date) < 365*10 then 'Mature Organization (3-10 years)'",
            "context": "code"
          },
          {
            "path": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
            "line": 357,
            "column": 5,
            "matched_text": "current_timestamp",
            "line_text": "    current_timestamp as analysis_timestamp",
            "context": "code"
          }
        ],
        "paths": [
          "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql"
        ]
      },
      "contract": {
        "available": true,
        "appears": true,
        "hits": [
          {
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
            "line": 2033,
            "column": 511,
            "matched_text": "current_date",
            "line_text": "      business_logic: '1) Filter organizations to active only and expose attributes and effective_start as the creation date. 2) Build worker–organization–role relationships by left joining worker positions to role-worker and role master on matching worker, role, source_relation, and organization_id. For each assignment: - assignment_status: ''Active Assignment'' if end date is null, else ''Former Assignment''. - assignment_duration_days: days between start and end; if end is null, days between start and current_date. - carry organization_role_id and organization_role_code from the role join. 3) Aggregate organization_employee_stats by (organization_id, source_relation): - total_employees_ever: distinct workers across all assignments. - current_active_employees: distinct workers with Active Assignment. - former_employees: distinct workers with Former Assignment. - total_positions_in_org: distinct positions across all assignments. - active_positions_count: distinct positions with Active Assignment. - new_assignments_last_year: distinct workers with start date in the last year relative to current_date. - departures_last_year: distinct workers with a non-null end date in the last year. - avg_current_tenure_days: average assignment_duration_days for Active Assignments. - avg_former_tenure_days: average assignment_duration_days for Former Assignments. - unique_organization_roles: distinct organization_role_id. - management_role_employees / director_role_employees / lead_role_employees: distinct workers where role code contains ''Manager'' / ''Director'' / ''Lead''. - last_new_assignment_date: most recent start date; last_departure_date: most recent end date. 4) Aggregate organization_performance_metrics from mart.workday__employee_overview by (organization_id, source_relation), excluding organization_id = ''Unknown'': - Averages over currently employed workers only: overall_employee_score and career_development_score rounded to 2 decimals; retention_stability_score rounded to 2 decimals; age rounded to 1 decimal. - Employee value segments: distinct workers by segment (''High Value - High Retention'', ''High Value - Flight Risk'', ''Stable - Development Needed'', ''Development Required''); no employment filter. - Risk distribution: distinct workers by employee_risk_level (High/Medium/Low); no employment filter. - Maturity segments: distinct employed workers where maturity contains ''New Hire'' / ''Junior'' / ''Experienced'' / ''Senior'' / ''Veteran''. - Diversity: distinct ethnicity_codes among employed; military_veterans_count is distinct employed workers flagged for military service. - Compensation tiers: distinct employed workers by compensation_tier (Entry/Mid/Senior/Executive Level). - Promotions among employed: total_promotions summed; high_achievers_count is distinct workers with total_promotions ≥ 2; fast_track_employees_count is distinct workers with fast_promotions > 0. 5) Derive organization attributes per active organization: - organization_created_date from effective_start. - organization_age_days as days from creation to current_date; organization_age_years is that divided by 365, rounded to 2 decimals. - organization_maturity_level by age_days: <1 year New; 1–3 years Young; 3–10 years Mature; 10+ years Legacy. - organizational_level from organization_type: Company/Division/Department/Team mapped to corresponding Level; others to Other Level. - access_level from visibility: Public→Open Access, Private→Restricted Access, others Unknown Access. 6) Final metrics and rules (rates rounded to 2 decimals; missing metrics default to 0 unless noted): - position_fill_rate (%) = current_active_employees ÷ total_positions × 100 when total_positions > 0, else 0. - annual_turnover_rate (%) = departures_last_year ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - avg_current_tenure_years and avg_former_tenure_years = respective average tenure days ÷ 365, rounded to 2; if no data, treated as 0. - management_ratio (%) = (management_role_employees + director_role_employees) ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - high_risk_employee_percentage (%) = high_risk_employees ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - organization_health_score (0–100) = sum of: performance (cap at 30% of average performance), turnover (25/20/15/10/5 by thresholds using annual_turnover_rate and zero departures case), development (cap at 20% of average career development), efficiency (15/12/9/6 by position_fill_rate thresholds), and risk (10/7/4/2 by high_risk_employee_percentage thresholds); final score rounded to 2 decimals. - performance_category uses a weighted composite with thresholds: Excellent if composite ≥ 80; else Good if ≥ 60; else Average if ≥ 40; otherwise Needs Improvement (weights and constants follow the detailed rules above). - organization_size_category by current_active_employees: 0 Empty; ≤5 Micro; ≤15 Small; ≤50 Medium; ≤200 Large; else Enterprise. - last_activity_date is the most recent assignment start; if none, use organization_created_date. - last_departure_date is the most recent assignment end; if none, use 1900-01-01. - management_recommendation (first match): if no active employees then review necessity; else if turnover > 30% then focus on retention; else if high-risk % > 25% then address risk; else if fill rate < 70% then improve staffing; else if average performance < 50 then enhance performance management; else if management_ratio > 40% then optimize structure; else maintain excellence. - data_quality_flag precedence: missing or blank organization name → ERROR; active employees exceed positions by more than 10 → WARNING; turnover rate > 100% → WARNING; negative age days → ERROR; otherwise VALID. - analysis_timestamp is the query execution timestamp. 7) Join logic: left join employee stats and performance metrics to active organizations on (organization_id, source_relation); missing measures default to 0. The final ordering is for presentation only and does not affect grain.'",
            "context": "contract_text"
          },
          {
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
            "line": 2033,
            "column": 1105,
            "matched_text": "current_date",
            "line_text": "      business_logic: '1) Filter organizations to active only and expose attributes and effective_start as the creation date. 2) Build worker–organization–role relationships by left joining worker positions to role-worker and role master on matching worker, role, source_relation, and organization_id. For each assignment: - assignment_status: ''Active Assignment'' if end date is null, else ''Former Assignment''. - assignment_duration_days: days between start and end; if end is null, days between start and current_date. - carry organization_role_id and organization_role_code from the role join. 3) Aggregate organization_employee_stats by (organization_id, source_relation): - total_employees_ever: distinct workers across all assignments. - current_active_employees: distinct workers with Active Assignment. - former_employees: distinct workers with Former Assignment. - total_positions_in_org: distinct positions across all assignments. - active_positions_count: distinct positions with Active Assignment. - new_assignments_last_year: distinct workers with start date in the last year relative to current_date. - departures_last_year: distinct workers with a non-null end date in the last year. - avg_current_tenure_days: average assignment_duration_days for Active Assignments. - avg_former_tenure_days: average assignment_duration_days for Former Assignments. - unique_organization_roles: distinct organization_role_id. - management_role_employees / director_role_employees / lead_role_employees: distinct workers where role code contains ''Manager'' / ''Director'' / ''Lead''. - last_new_assignment_date: most recent start date; last_departure_date: most recent end date. 4) Aggregate organization_performance_metrics from mart.workday__employee_overview by (organization_id, source_relation), excluding organization_id = ''Unknown'': - Averages over currently employed workers only: overall_employee_score and career_development_score rounded to 2 decimals; retention_stability_score rounded to 2 decimals; age rounded to 1 decimal. - Employee value segments: distinct workers by segment (''High Value - High Retention'', ''High Value - Flight Risk'', ''Stable - Development Needed'', ''Development Required''); no employment filter. - Risk distribution: distinct workers by employee_risk_level (High/Medium/Low); no employment filter. - Maturity segments: distinct employed workers where maturity contains ''New Hire'' / ''Junior'' / ''Experienced'' / ''Senior'' / ''Veteran''. - Diversity: distinct ethnicity_codes among employed; military_veterans_count is distinct employed workers flagged for military service. - Compensation tiers: distinct employed workers by compensation_tier (Entry/Mid/Senior/Executive Level). - Promotions among employed: total_promotions summed; high_achievers_count is distinct workers with total_promotions ≥ 2; fast_track_employees_count is distinct workers with fast_promotions > 0. 5) Derive organization attributes per active organization: - organization_created_date from effective_start. - organization_age_days as days from creation to current_date; organization_age_years is that divided by 365, rounded to 2 decimals. - organization_maturity_level by age_days: <1 year New; 1–3 years Young; 3–10 years Mature; 10+ years Legacy. - organizational_level from organization_type: Company/Division/Department/Team mapped to corresponding Level; others to Other Level. - access_level from visibility: Public→Open Access, Private→Restricted Access, others Unknown Access. 6) Final metrics and rules (rates rounded to 2 decimals; missing metrics default to 0 unless noted): - position_fill_rate (%) = current_active_employees ÷ total_positions × 100 when total_positions > 0, else 0. - annual_turnover_rate (%) = departures_last_year ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - avg_current_tenure_years and avg_former_tenure_years = respective average tenure days ÷ 365, rounded to 2; if no data, treated as 0. - management_ratio (%) = (management_role_employees + director_role_employees) ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - high_risk_employee_percentage (%) = high_risk_employees ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - organization_health_score (0–100) = sum of: performance (cap at 30% of average performance), turnover (25/20/15/10/5 by thresholds using annual_turnover_rate and zero departures case), development (cap at 20% of average career development), efficiency (15/12/9/6 by position_fill_rate thresholds), and risk (10/7/4/2 by high_risk_employee_percentage thresholds); final score rounded to 2 decimals. - performance_category uses a weighted composite with thresholds: Excellent if composite ≥ 80; else Good if ≥ 60; else Average if ≥ 40; otherwise Needs Improvement (weights and constants follow the detailed rules above). - organization_size_category by current_active_employees: 0 Empty; ≤5 Micro; ≤15 Small; ≤50 Medium; ≤200 Large; else Enterprise. - last_activity_date is the most recent assignment start; if none, use organization_created_date. - last_departure_date is the most recent assignment end; if none, use 1900-01-01. - management_recommendation (first match): if no active employees then review necessity; else if turnover > 30% then focus on retention; else if high-risk % > 25% then address risk; else if fill rate < 70% then improve staffing; else if average performance < 50 then enhance performance management; else if management_ratio > 40% then optimize structure; else maintain excellence. - data_quality_flag precedence: missing or blank organization name → ERROR; active employees exceed positions by more than 10 → WARNING; turnover rate > 100% → WARNING; negative age days → ERROR; otherwise VALID. - analysis_timestamp is the query execution timestamp. 7) Join logic: left join employee stats and performance metrics to active organizations on (organization_id, source_relation); missing measures default to 0. The final ordering is for presentation only and does not affect grain.'",
            "context": "contract_text"
          },
          {
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
            "line": 2033,
            "column": 3086,
            "matched_text": "current_date",
            "line_text": "      business_logic: '1) Filter organizations to active only and expose attributes and effective_start as the creation date. 2) Build worker–organization–role relationships by left joining worker positions to role-worker and role master on matching worker, role, source_relation, and organization_id. For each assignment: - assignment_status: ''Active Assignment'' if end date is null, else ''Former Assignment''. - assignment_duration_days: days between start and end; if end is null, days between start and current_date. - carry organization_role_id and organization_role_code from the role join. 3) Aggregate organization_employee_stats by (organization_id, source_relation): - total_employees_ever: distinct workers across all assignments. - current_active_employees: distinct workers with Active Assignment. - former_employees: distinct workers with Former Assignment. - total_positions_in_org: distinct positions across all assignments. - active_positions_count: distinct positions with Active Assignment. - new_assignments_last_year: distinct workers with start date in the last year relative to current_date. - departures_last_year: distinct workers with a non-null end date in the last year. - avg_current_tenure_days: average assignment_duration_days for Active Assignments. - avg_former_tenure_days: average assignment_duration_days for Former Assignments. - unique_organization_roles: distinct organization_role_id. - management_role_employees / director_role_employees / lead_role_employees: distinct workers where role code contains ''Manager'' / ''Director'' / ''Lead''. - last_new_assignment_date: most recent start date; last_departure_date: most recent end date. 4) Aggregate organization_performance_metrics from mart.workday__employee_overview by (organization_id, source_relation), excluding organization_id = ''Unknown'': - Averages over currently employed workers only: overall_employee_score and career_development_score rounded to 2 decimals; retention_stability_score rounded to 2 decimals; age rounded to 1 decimal. - Employee value segments: distinct workers by segment (''High Value - High Retention'', ''High Value - Flight Risk'', ''Stable - Development Needed'', ''Development Required''); no employment filter. - Risk distribution: distinct workers by employee_risk_level (High/Medium/Low); no employment filter. - Maturity segments: distinct employed workers where maturity contains ''New Hire'' / ''Junior'' / ''Experienced'' / ''Senior'' / ''Veteran''. - Diversity: distinct ethnicity_codes among employed; military_veterans_count is distinct employed workers flagged for military service. - Compensation tiers: distinct employed workers by compensation_tier (Entry/Mid/Senior/Executive Level). - Promotions among employed: total_promotions summed; high_achievers_count is distinct workers with total_promotions ≥ 2; fast_track_employees_count is distinct workers with fast_promotions > 0. 5) Derive organization attributes per active organization: - organization_created_date from effective_start. - organization_age_days as days from creation to current_date; organization_age_years is that divided by 365, rounded to 2 decimals. - organization_maturity_level by age_days: <1 year New; 1–3 years Young; 3–10 years Mature; 10+ years Legacy. - organizational_level from organization_type: Company/Division/Department/Team mapped to corresponding Level; others to Other Level. - access_level from visibility: Public→Open Access, Private→Restricted Access, others Unknown Access. 6) Final metrics and rules (rates rounded to 2 decimals; missing metrics default to 0 unless noted): - position_fill_rate (%) = current_active_employees ÷ total_positions × 100 when total_positions > 0, else 0. - annual_turnover_rate (%) = departures_last_year ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - avg_current_tenure_years and avg_former_tenure_years = respective average tenure days ÷ 365, rounded to 2; if no data, treated as 0. - management_ratio (%) = (management_role_employees + director_role_employees) ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - high_risk_employee_percentage (%) = high_risk_employees ÷ current_active_employees × 100 when current_active_employees > 0, else 0. - organization_health_score (0–100) = sum of: performance (cap at 30% of average performance), turnover (25/20/15/10/5 by thresholds using annual_turnover_rate and zero departures case), development (cap at 20% of average career development), efficiency (15/12/9/6 by position_fill_rate thresholds), and risk (10/7/4/2 by high_risk_employee_percentage thresholds); final score rounded to 2 decimals. - performance_category uses a weighted composite with thresholds: Excellent if composite ≥ 80; else Good if ≥ 60; else Average if ≥ 40; otherwise Needs Improvement (weights and constants follow the detailed rules above). - organization_size_category by current_active_employees: 0 Empty; ≤5 Micro; ≤15 Small; ≤50 Medium; ≤200 Large; else Enterprise. - last_activity_date is the most recent assignment start; if none, use organization_created_date. - last_departure_date is the most recent assignment end; if none, use 1900-01-01. - management_recommendation (first match): if no active employees then review necessity; else if turnover > 30% then focus on retention; else if high-risk % > 25% then address risk; else if fill rate < 70% then improve staffing; else if average performance < 50 then enhance performance management; else if management_ratio > 40% then optimize structure; else maintain excellence. - data_quality_flag precedence: missing or blank organization name → ERROR; active employees exceed positions by more than 10 → WARNING; turnover rate > 100% → WARNING; negative age days → ERROR; otherwise VALID. - analysis_timestamp is the query execution timestamp. 7) Join logic: left join employee stats and performance metrics to active organizations on (organization_id, source_relation); missing measures default to 0. The final ordering is for presentation only and does not affect grain.'",
            "context": "contract_text"
          },
          {
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
            "line": 2071,
            "column": 62,
            "matched_text": "current_date",
            "line_text": "        description: Days since organization_created_date to current_date at run time",
            "context": "contract_text"
          },
          {
            "path": "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
            "line": 2230,
            "column": 22,
            "matched_text": "current_timestamp",
            "line_text": "        description: current_timestamp at run time indicating when the analysis was computed",
            "context": "contract_text"
          }
        ]
      }
    },
    "trace_flags": {
      "A1_zero_rows": false,
      "A2_all_null_column": true,
      "A3_constant_nonnull_column": true,
      "A4_equal_columns": true,
      "A4_equal_columns_different_description_texts": true,
      "B5_null_literal_output": false,
      "B6_constant_literal_output": false,
      "B7_specified_not_read": true,
      "B7_read_not_specified": false,
      "B8_shared_single_source": false,
      "C9_agent_runtime_text": true,
      "C9_gold_runtime_text": true,
      "C9_contract_runtime_text": true,
      "D10_keyword_in_final_report": false,
      "D10_keyword_in_any_result_field": false
    }
  }
}
```

## trace_excerpts

```json
{
  "archive": "/home/katherine/Assumption_Ledger/traces/dacomp_deimpl_prev.tar.gz",
  "event_source_root": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent",
  "actual_read_sources_from_008_B7": [
    "marts.workday__employee_overview",
    "staging.stg_workday__organization",
    "staging.stg_workday__organization_role",
    "staging.stg_workday__organization_role_worker",
    "staging.stg_workday__worker_position_organization"
  ],
  "name_match_policy": "Case-insensitive complete identifier-name boundaries; source names include qualified form and bare leaf name. No semantic association inferred.",
  "matched_step_count": 23,
  "full_original_characters_before_budget": 128773,
  "budget_triggered": true,
  "source_only_steps_indexed": 12,
  "retained_full_original_characters": 50982,
  "full_target_steps_exceed_60000": false,
  "budget_policy": "If total command/output text exceeds 60000 characters, keep every target-table step complete and retain only id/location/first line for source-only steps. Do not rewrite or truncate a kept original step."
}
```

### event 7

```json
{
  "event_id": 7,
  "agent_command_sequence": 2,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/7.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1733,
    "decoded_characters": 73
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/7.json",
  "timestamp": "2026-10-25T02:49:16.004667",
  "target_table_name_hits": [
    "workday__organization_overview"
  ],
  "source_table_name_hits": [
    "stg_workday__worker_position_organization",
    "stg_workday__organization_role_worker",
    "stg_workday__organization_role",
    "workday__employee_overview",
    "stg_workday__organization"
  ],
  "full_original_characters": 3474,
  "retention": "full_original"
}
```
```bash
cat config/layer_dependencies.yaml && find sql -type f -maxdepth 3 -print
```
```json
{
  "event_id": 8,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/8.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1418,
    "decoded_characters": 3401
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/8.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
layers:
  staging:
    description: "Standardize Raw Data Layer - cleans and normalizes raw data imported from source systems"
    tables:
      - stg_workday__worker
      - stg_workday__personal_information
      - stg_workday__person_name
      - stg_workday__person_contact_email_address
      - stg_workday__personal_information_ethnicity
      - stg_workday__military_service
      - stg_workday__worker_position
      - stg_workday__position
      - stg_workday__job_profile
      - stg_workday__organization
      - stg_workday__job_family
      - stg_workday__job_family_group
      - stg_workday__job_family_job_profile
      - stg_workday__job_family_job_family_group
      - stg_workday__organization_job_family
      - stg_workday__organization_role
      - stg_workday__organization_role_worker
      - stg_workday__position_job_profile
      - stg_workday__position_organization
      - stg_workday__worker_leave_status
      - stg_workday__worker_position_organization
    dependencies: []

  intermediate:
    description: "Intermediate processing layer - business logic processing and data aggregation"
    tables:
      - int_workday__worker_details
      - int_workday__personal_details
      - int_workday__worker_position_enriched
      - int_workday__worker_employee_enhanced
      - int_workday__employee_lifecycle
      - int_workday__organization_metrics
      - int_workday__career_progression
    dependencies: ["staging"]

  marts:
    description: "Data Mart Layer - Final Data Table for Analysis"
    tables:
      - workday__employee_overview
      - workday__job_overview
      - workday__position_overview
      - workday__organization_overview
      - workday__workforce_analytics
      - workday__organization_performance
    dependencies: ["intermediate"]

execution_order:
  staging:
    - stg_workday__worker
    - stg_workday__personal_information
    - stg_workday__person_name
    - stg_workday__person_contact_email_address
    - stg_workday__personal_information_ethnicity
    - stg_workday__military_service
    - stg_workday__worker_position
    - stg_workday__position
    - stg_workday__job_profile
    - stg_workday__organization
    - stg_workday__job_family
    - stg_workday__job_family_group
    - stg_workday__job_family_job_profile
    - stg_workday__job_family_job_family_group
    - stg_workday__organization_job_family
    - stg_workday__organization_role
    - stg_workday__organization_role_worker
    - stg_workday__position_job_profile
    - stg_workday__position_organization
    - stg_workday__worker_leave_status
    - stg_workday__worker_position_organization

  intermediate:
    - int_workday__worker_details
    - int_workday__personal_details
    - int_workday__worker_position_enriched
    - int_workday__worker_employee_enhanced
    - int_workday__employee_lifecycle
    - int_workday__organization_metrics
    - int_workday__career_progression

  marts:
    - workday__employee_overview
    - workday__job_overview
    - workday__position_overview
    - workday__organization_overview
    - workday__workforce_analytics
    - workday__organization_performancefind: warning: you have specified the global option -maxdepth after the argument -type, but global options are not positional, i.e., -maxdepth affects tests specified before it as well as those specified after it.  Please specify global options before other arguments.
```

### event 13

```json
{
  "event_id": 13,
  "agent_command_sequence": 5,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/13.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1463,
    "decoded_characters": 114
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/13.json",
  "timestamp": "2026-10-25T02:49:19.645655",
  "target_table_name_hits": [],
  "source_table_name_hits": [
    "stg_workday__organization"
  ],
  "full_original_characters": 8063,
  "retention": "index_and_first_line_only",
  "first_line_original": "find sql -type f -printf '%p %s bytes\\n' | sort; sed -n '240,420p' run.py; sed -n '1,100p' docs/data_contract.yaml"
}
```
```json
{
  "event_id": 14,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/14.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1148,
    "decoded_characters": 7949
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/14.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```

### event 17

```json
{
  "event_id": 17,
  "agent_command_sequence": 7,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/17.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 2007,
    "decoded_characters": 377
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/17.json",
  "timestamp": "2026-10-25T02:49:29.622629",
  "target_table_name_hits": [
    "workday__organization_overview"
  ],
  "source_table_name_hits": [
    "stg_workday__worker_position_organization",
    "stg_workday__organization_role_worker",
    "stg_workday__organization_role",
    "workday__employee_overview",
    "stg_workday__organization"
  ],
  "full_original_characters": 4319,
  "retention": "full_original"
}
```
```bash
python3 - <<'PY'
import yaml
x=yaml.safe_load(open('docs/data_contract.yaml'))
print(x.keys(),len(x['staging_contract']['tables']))
print([m['name'] for m in x['modeling_spec']['intermediate_models']])
print([m['name'] for m in x['modeling_spec']['marts_models']])
for t in x['staging_contract']['tables']:print(t['name'],t['source_table'],[c['name'] for c in t['columns']])
PY
```
```json
{
  "event_id": 18,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/18.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1692,
    "decoded_characters": 3942
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/18.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
dict_keys(['version', 'metadata', 'staging_contract', 'modeling_spec']) 21
['int_workday__employee_lifecycle', 'int_workday__organization_metrics', 'int_workday__career_progression', 'int_workday__personal_details', 'int_workday__worker_details', 'int_workday__worker_employee_enhanced', 'int_workday__worker_position_enriched']
['workday__employee_overview', 'workday__organization_performance', 'workday__workforce_analytics', 'workday__job_overview', 'workday__organization_overview', 'workday__position_overview']
stg_workday__worker raw.worker_history ['worker_id', 'source_relation', 'worker_history_id', 'event_type', 'effective_start', 'effective_end']
stg_workday__personal_information raw.person_info_history ['personal_info_history_id', 'worker_id', 'source_relation', 'date_of_birth', 'marital_status', 'political_affiliation', 'city_of_birth', 'country_of_birth', 'last_medical_exam_date']
stg_workday__organization raw.organization ['organization_id', 'source_relation', 'organization_name', 'organization_code', 'organization_type', 'organization_sub_type', 'staffing_model', 'visibility', 'effective_start', 'is_inactive']
stg_workday__position raw.position ['position_id', 'source_relation', 'business_title', 'employee_type', 'default_weekly_hours', 'effective_start']
stg_workday__job_profile raw.job_profile ['job_profile_id', 'source_relation', 'job_profile_title', 'job_profile_summary', 'job_profile_code', 'management_level', 'compensation_grade_id', 'is_work_shift_required', 'is_union_eligible']
stg_workday__job_family raw.job_family ['job_family_id', 'source_relation', 'job_family_code', 'job_family_name', 'effective_start', 'is_inactive']
stg_workday__job_family_group raw.job_family_group ['job_family_group_id', 'source_relation', 'job_family_group_code', 'job_family_group_name', 'effective_start', 'is_inactive']
stg_workday__job_family_job_family_group raw.job_family_job_family_group ['job_family_id', 'job_family_group_id', 'source_relation']
stg_workday__job_family_job_profile raw.job_family_job_profile ['job_family_id', 'job_profile_id', 'source_relation']
stg_workday__military_service raw.military_service ['worker_id', 'source_relation', 'service', 'rank', 'military_status', 'status_begin_date', 'discharge_date']
stg_workday__organization_job_family raw.organization_job_family ['source_relation', 'job_family_group_id', 'job_family_id', 'organization_id']
stg_workday__organization_role raw.organization_role ['source_relation', 'organization_id', 'organization_role_id', 'organization_role_code']
stg_workday__organization_role_worker raw.organization_role_worker ['source_relation', 'organization_worker_code', 'organization_id', 'role_id']
stg_workday__person_contact_email_address raw.person_contact_email_address ['worker_id', 'source_relation', 'email_id', 'email_address', 'email_code', 'email_comment']
stg_workday__person_name raw.person_name ['worker_id', 'source_relation', 'name_id', 'person_name_type', 'country', 'first_name', 'last_name', 'full_name']
stg_workday__personal_information_ethnicity raw.personal_information_ethnicity ['worker_id', 'source_relation', 'ethnicity', 'ethnicity_group', 'is_hispanic_or_latino', 'record_type', 'verification_source']
stg_workday__position_job_profile raw.position_job_profile ['source_relation', 'position_id', 'job_profile_id']
stg_workday__position_organization raw.position_organization ['source_relation', 'position_id', 'organization_id', 'effective_start', 'effective_end']
stg_workday__worker_leave_status raw.worker_leave_status ['worker_id', 'source_relation', 'leave_type', 'leave_status', 'start_date', 'end_date']
stg_workday__worker_position raw.worker_position ['worker_id', 'position_id', 'source_relation', 'effective_start', 'effective_end']
stg_workday__worker_position_organization raw.worker_position_organization ['worker_id', 'position_id', 'organization_id', 'source_relation', 'effective_start', 'effective_end']
```

### event 25

```json
{
  "event_id": 25,
  "agent_command_sequence": 11,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/25.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 19861,
    "decoded_characters": 9207
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/25.json",
  "timestamp": "2026-10-25T02:50:32.619991",
  "target_table_name_hits": [],
  "source_table_name_hits": [
    "staging.stg_workday__worker_position_organization",
    "stg_workday__worker_position_organization",
    "staging.stg_workday__organization",
    "stg_workday__organization"
  ],
  "full_original_characters": 9207,
  "retention": "index_and_first_line_only",
  "first_line_original": "cat > sql/intermediate/int_workday__organization_metrics.sql <<'SQL'\n"
}
```
```json
{
  "event_id": 26,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/26.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 19545,
    "decoded_characters": 0
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/26.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```

### event 29

```json
{
  "event_id": 29,
  "agent_command_sequence": 13,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/29.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1691,
    "decoded_characters": 218
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/29.json",
  "timestamp": "2026-10-25T02:50:53.783028",
  "target_table_name_hits": [
    "workday__organization_overview"
  ],
  "source_table_name_hits": [
    "workday__employee_overview"
  ],
  "full_original_characters": 9003,
  "retention": "full_original"
}
```
```bash
python3 - <<'PY'
import yaml
x=yaml.safe_load(open('docs/data_contract.yaml'))
for m in x['modeling_spec']['marts_models']:
 print('\n',m['name'],len(m['columns']))
 print(', '.join(c['name'] for c in m['columns']))
PY
```
```json
{
  "event_id": 30,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/30.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1375,
    "decoded_characters": 8785
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/30.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text

 workday__employee_overview 79
employee_id, worker_id, source_relation, position_id, position_start_date, worker_history_id, event_type, is_employed, hire_date, departure_date, days_as_worker, first_name, last_name, full_name, date_of_birth, marital_status, city_of_birth, country_of_birth, email_address, ethnicity_codes, is_military_service, military_status, business_title, employee_type, default_weekly_hours, position_end_date, days_in_position, is_employed_one_year, is_employed_five_years, is_employed_ten_years, is_current_employee_one_year, is_current_employee_five_years, is_current_employee_ten_years, age, tenure_group, retained_30_days, retained_90_days, retained_1_year, retained_3_years, churn_risk_category, employee_maturity_segment, departure_category, tenure_years, hire_quarter_cohort, hire_year_cohort, retention_stability_score, hire_month, hire_season, total_positions_held, total_promotions, total_demotions, lateral_moves, fast_promotions, management_positions_held, highest_management_level_reached, career_stability_category, career_growth_pace, career_development_score, career_phase, organization_id, organization_name, organization_type, organization_sub_type, dept_size, dept_health_score, dept_turnover_rate, dept_management_ratio, dept_performance_category, dept_size_category, compensation_grade_id, compensation_tier, is_work_shift_required, is_union_eligible, work_conditions_score, overall_employee_score, employee_risk_level, employee_value_segment, comprehensive_data_quality_flag, analysis_timestamp

 workday__organization_performance 66
organization_id, source_relation, organization_name, organization_code, organization_type, organization_sub_type, staffing_model, current_employee_count, total_positions, position_fill_rate, organization_size_category, regular_employees, contingent_employees, intern_employees, regular_employee_percentage, avg_weekly_hours, total_weekly_hours, avg_weekly_hours_per_employee, managers_count, senior_managers_count, directors_count, individual_contributors, management_ratio, span_of_control, new_hires_last_year, departures_last_year, internal_transfers_in, internal_transfers_out, annual_turnover_rate, avg_tenure_days, avg_tenure_years, organization_maturity, unique_compensation_grades, most_common_grade, unique_job_families, unique_job_family_groups, talent_density_ratio, high_value_retained_count, high_value_flight_risk_count, stable_development_count, development_required_count, high_value_retention_rate, talent_flight_risk_rate, avg_career_development_score, high_achievers_count, fast_track_count, high_achiever_percentage, high_risk_employees, medium_risk_employees, low_risk_employees, high_risk_percentage, avg_employee_satisfaction_proxy, ethnic_diversity_count, military_veterans_count, avg_employee_age, young_professionals_count, mid_career_professionals_count, senior_professionals_count, pre_retirement_professionals_count, organization_health_score, performance_category, enhanced_organization_effectiveness_score, organization_risk_level, recommended_action, data_quality_flag, analysis_timestamp

 workday__workforce_analytics 59
source_relation, analysis_date, active_employees, former_employees, total_employees_all_time, total_positions, position_utilization_rate, regular_employees, contingent_employees, intern_employees, regular_employee_percentage, avg_weekly_hours, total_weekly_hours, part_time_employees, full_time_employees, full_time_percentage, ethnic_diversity_count, military_veterans, veteran_percentage, avg_employee_age, gen_z_employees, millennial_employees, gen_x_employees, boomer_employees, retention_rate_30_days, retention_rate_90_days, retention_rate_1_year, retention_rate_3_years, annual_turnover_rate, avg_tenure_years, avg_tenure_departed_years, high_risk_employees, medium_risk_employees, low_risk_employees, stable_employees, high_risk_percentage, early_terminations, short_term_departures, mid_term_departures, long_term_departures, avg_career_development_score, high_achievers, fast_track_employees, high_achiever_percentage, directors_and_above, senior_managers, managers, individual_contributors, management_percentage, early_career_employees, mid_career_employees, senior_career_employees, high_value_retained, high_value_flight_risk, stable_development_needed, development_required, workforce_health_score, workforce_status_flag, analysis_timestamp

 workday__job_overview 60
job_profile_id, source_relation, job_profile_code, job_title, job_summary, management_level, compensation_grade_id, is_work_shift_required, is_union_eligible, job_family_codes, job_family_names, job_family_group_codes, job_family_group_names, associated_job_families_count, associated_job_family_groups_count, total_positions_count, active_positions_count, inactive_positions_count, current_employees_count, total_employees_ever_count, avg_weekly_hours, min_weekly_hours, max_weekly_hours, regular_employees_count, contingent_employees_count, intern_employees_count, organizations_using_job_count, primary_organization_id, avg_career_development_score, high_achievers_count, fast_track_employees_count, high_risk_employees_count, medium_risk_employees_count, stable_employees_count, new_hires_count, junior_employees_count, experienced_employees_count, senior_employees_count, veteran_employees_count, avg_employee_age, young_professionals_count, mid_career_professionals_count, senior_professionals_count, high_value_retained_count, high_value_flight_risk_count, entry_level_employees_count, mid_level_employees_count, senior_level_employees_count, executive_level_employees_count, job_rarity_level, talent_competition_level, job_maturity_level, retention_difficulty_level, high_performer_percentage, career_growth_potential_percentage, job_health_score, job_value_tier, talent_management_recommendation, data_quality_flag, analysis_timestamp

 workday__organization_overview 64
organization_id, source_relation, organization_name, organization_code, organization_type, organization_sub_type, staffing_model, visibility, access_level, organization_created_date, organization_age_days, organization_age_years, organization_maturity_level, organizational_level, total_employees_ever, current_active_employees, former_employees, total_positions, active_positions_count, position_fill_rate, new_assignments_last_year, departures_last_year, annual_turnover_rate, avg_current_tenure_years, avg_former_tenure_years, unique_organization_roles, management_role_employees, director_role_employees, lead_role_employees, management_ratio, avg_employee_performance_score, avg_career_development_score, avg_retention_stability_score, high_value_stable_employees, high_value_flight_risk_employees, stable_development_employees, development_required_employees, high_risk_employees, medium_risk_employees, low_risk_employees, high_risk_employee_percentage, new_hire_employees, junior_employees, experienced_employees, senior_employees, veteran_employees, ethnic_diversity_count, military_veterans_count, avg_employee_age, entry_level_employees, mid_level_employees, senior_level_employees, executive_level_employees, total_promotions_in_organization, high_achievers_count, fast_track_employees_count, organization_health_score, performance_category, organization_size_category, last_activity_date, last_departure_date, management_recommendation, data_quality_flag, analysis_timestamp

 workday__position_overview 58
position_id, source_relation, business_title, employee_type, default_weekly_hours, position_created_date, position_age_days, position_age_category, total_workers_ever_assigned, current_workers_assigned, former_workers_assigned, position_occupancy_status, avg_tenure_years_in_position, last_assignment_date, last_departure_date, new_assignments_last_year, departures_last_year, position_turnover_rate, organization_id, organization_name, organization_type, organization_sub_type, staffing_model, department_total_employees, department_health_score, department_turnover_rate, department_performance_level, department_size_category, similar_positions_in_department, job_profile_id, job_profile_title, management_level, compensation_grade_id, compensation_tier, is_work_shift_required, is_union_eligible, challenging_work_conditions_score, management_level_numeric, avg_employee_performance_score, avg_career_development_score, avg_retention_score, high_risk_employees_count, medium_risk_employees_count, low_risk_employees_count, high_value_employees_count, flight_risk_employees_count, new_employees_count, veteran_employees_count, avg_employee_age, ethnic_diversity_count, military_veterans_count, position_efficiency_score, position_performance_category, management_priority, cost_performance_analysis, strategic_recommendation, data_quality_flag, analysis_timestamp
```

### event 31

```json
{
  "event_id": 31,
  "agent_command_sequence": 14,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/31.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 18924,
    "decoded_characters": 8759
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/31.json",
  "timestamp": "2026-10-25T02:51:13.147187",
  "target_table_name_hits": [],
  "source_table_name_hits": [
    "staging.stg_workday__worker_position_organization",
    "stg_workday__worker_position_organization",
    "workday__employee_overview"
  ],
  "full_original_characters": 8759,
  "retention": "index_and_first_line_only",
  "first_line_original": "cat > sql/marts/workday__employee_overview.sql <<'SQL'\n"
}
```
```json
{
  "event_id": 32,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/32.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 18607,
    "decoded_characters": 0
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/32.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```

### event 33

```json
{
  "event_id": 33,
  "agent_command_sequence": 15,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/33.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 13489,
    "decoded_characters": 6091
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/33.json",
  "timestamp": "2026-10-25T02:51:27.917444",
  "target_table_name_hits": [],
  "source_table_name_hits": [
    "workday__employee_overview"
  ],
  "full_original_characters": 6091,
  "retention": "index_and_first_line_only",
  "first_line_original": "cat > sql/marts/workday__workforce_analytics.sql <<'SQL'\n"
}
```
```json
{
  "event_id": 34,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/34.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 13172,
    "decoded_characters": 0
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/34.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```

### event 35

```json
{
  "event_id": 35,
  "agent_command_sequence": 16,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/35.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 15844,
    "decoded_characters": 7261
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/35.json",
  "timestamp": "2026-10-25T02:51:45.395931",
  "target_table_name_hits": [],
  "source_table_name_hits": [
    "workday__employee_overview"
  ],
  "full_original_characters": 7261,
  "retention": "index_and_first_line_only",
  "first_line_original": "cat > sql/marts/workday__organization_performance.sql <<'SQL'\n"
}
```
```json
{
  "event_id": 36,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/36.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 15527,
    "decoded_characters": 0
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/36.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```

### event 37

```json
{
  "event_id": 37,
  "agent_command_sequence": 17,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/37.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 23975,
    "decoded_characters": 11310
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/37.json",
  "timestamp": "2026-10-25T02:52:08.825574",
  "target_table_name_hits": [
    "workday__organization_overview"
  ],
  "source_table_name_hits": [
    "staging.stg_workday__worker_position_organization",
    "staging.stg_workday__organization_role_worker",
    "stg_workday__worker_position_organization",
    "staging.stg_workday__organization_role",
    "stg_workday__organization_role_worker",
    "staging.stg_workday__organization",
    "stg_workday__organization_role",
    "workday__employee_overview",
    "stg_workday__organization"
  ],
  "full_original_characters": 11310,
  "retention": "full_original"
}
```
```bash
cat > sql/marts/workday__organization_overview.sql <<'SQL'
WITH active_org AS (SELECT * FROM staging.stg_workday__organization WHERE is_inactive=FALSE), rel AS (
 SELECT worker_id,organization_id,source_relation,position_id,effective_start,effective_end,
 date_diff('day',effective_start,coalesce(effective_end,current_date)) duration,
 CASE WHEN effective_end IS NULL THEN 'Active Assignment' ELSE 'Former Assignment' END status
 FROM staging.stg_workday__worker_position_organization
), stats AS (
 SELECT organization_id,source_relation,count(DISTINCT worker_id) total_employees_ever,count(DISTINCT worker_id) FILTER(WHERE effective_end IS NULL) current_active_employees,count(DISTINCT worker_id) FILTER(WHERE effective_end IS NOT NULL) former_employees,count(DISTINCT position_id) total_positions,count(DISTINCT position_id) FILTER(WHERE effective_end IS NULL) active_positions_count,
 count(DISTINCT worker_id) FILTER(WHERE effective_start>=current_date-INTERVAL '1 year') new_assignments_last_year,count(DISTINCT worker_id) FILTER(WHERE effective_end>=current_date-INTERVAL '1 year') departures_last_year,avg(duration) FILTER(WHERE effective_end IS NULL) avg_current_days,avg(duration) FILTER(WHERE effective_end IS NOT NULL) avg_former_days,max(effective_start) last_activity_date,max(effective_end) last_departure_date
 FROM rel GROUP BY organization_id,source_relation
), roles AS (
 SELECT ow.organization_id,'workday' source_relation,count(DISTINCT r.role_id) unique_organization_roles,count(DISTINCT ow.worker_id) FILTER(WHERE r.org_role_code ILIKE '%Manager%') management_role_employees,count(DISTINCT ow.worker_id) FILTER(WHERE r.org_role_code ILIKE '%Director%') director_role_employees,count(DISTINCT ow.worker_id) FILTER(WHERE r.org_role_code ILIKE '%Lead%') lead_role_employees FROM staging.stg_workday__organization_role_worker ow LEFT JOIN staging.stg_workday__organization_role r ON ow.organization_id=r.organization_id AND ow.role_id=r.organization_role_id GROUP BY ow.organization_id
), perf AS (
 SELECT organization_id,source_relation,avg(overall_employee_score) FILTER(WHERE is_employed) avg_employee_performance_score,avg(career_development_score) FILTER(WHERE is_employed) avg_career_development_score,avg(retention_stability_score) FILTER(WHERE is_employed) avg_retention_stability_score,
 count(DISTINCT worker_id) FILTER(WHERE employee_value_segment='High Value - High Retention') high_value_stable_employees,count(DISTINCT worker_id) FILTER(WHERE employee_value_segment='High Value - Flight Risk') high_value_flight_risk_employees,count(DISTINCT worker_id) FILTER(WHERE employee_value_segment='Stable - Development Needed') stable_development_employees,count(DISTINCT worker_id) FILTER(WHERE employee_value_segment='Development Required') development_required_employees,
 count(DISTINCT worker_id) FILTER(WHERE employee_risk_level='High Risk') high_risk_employees,count(DISTINCT worker_id) FILTER(WHERE employee_risk_level='Medium Risk') medium_risk_employees,count(DISTINCT worker_id) FILTER(WHERE employee_risk_level='Low Risk') low_risk_employees,
 count(DISTINCT worker_id) FILTER(WHERE is_employed AND employee_maturity_segment LIKE '%New Hire%') new_hire_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND employee_maturity_segment LIKE '%Junior%') junior_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND employee_maturity_segment LIKE '%Experienced%') experienced_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND employee_maturity_segment LIKE '%Senior%') senior_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND employee_maturity_segment LIKE '%Veteran%') veteran_employees,
 count(DISTINCT ethnicity_codes) FILTER(WHERE is_employed AND ethnicity_codes IS NOT NULL) ethnic_diversity_count,count(DISTINCT worker_id) FILTER(WHERE is_employed AND is_military_service) military_veterans_count,avg(age) FILTER(WHERE is_employed) avg_employee_age,
 count(DISTINCT worker_id) FILTER(WHERE is_employed AND compensation_tier='Entry Level') entry_level_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND compensation_tier='Mid Level') mid_level_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND compensation_tier='Senior Level') senior_level_employees,count(DISTINCT worker_id) FILTER(WHERE is_employed AND compensation_tier='Executive Level') executive_level_employees,
 sum(total_promotions) FILTER(WHERE is_employed) total_promotions_in_organization,count(DISTINCT worker_id) FILTER(WHERE is_employed AND total_promotions>=2) high_achievers_count,count(DISTINCT worker_id) FILTER(WHERE is_employed AND fast_promotions>0) fast_track_employees_count
 FROM mart.workday__employee_overview WHERE organization_id<>'Unknown' GROUP BY organization_id,source_relation
), joined AS (SELECT o.*,s.*,r.unique_organization_roles,r.management_role_employees,r.director_role_employees,r.lead_role_employees,p.* EXCLUDE(organization_id,source_relation) FROM active_org o LEFT JOIN stats s USING(organization_id,source_relation) LEFT JOIN roles r USING(organization_id,source_relation) LEFT JOIN perf p USING(organization_id,source_relation))
SELECT organization_id,source_relation,organization_name,organization_code,organization_type,organization_sub_type,staffing_model,visibility,
CASE visibility WHEN 'Public' THEN 'Open Access' WHEN 'Private' THEN 'Restricted Access' ELSE 'Unknown Access' END access_level,effective_start organization_created_date,date_diff('day',effective_start,current_date)::BIGINT organization_age_days,round(date_diff('day',effective_start,current_date)/365.0,2)::DOUBLE organization_age_years,
CASE WHEN date_diff('day',effective_start,current_date)<365 THEN 'New' WHEN date_diff('day',effective_start,current_date)<1095 THEN 'Young' WHEN date_diff('day',effective_start,current_date)<3650 THEN 'Mature' ELSE 'Legacy' END organization_maturity_level,
CASE organization_type WHEN 'Company' THEN 'Corporate Level' WHEN 'Division' THEN 'Division Level' WHEN 'Department' THEN 'Department Level' WHEN 'Team' THEN 'Team Level' ELSE 'Other Level' END organizational_level,
coalesce(total_employees_ever,0)::BIGINT total_employees_ever,coalesce(current_active_employees,0)::BIGINT current_active_employees,coalesce(former_employees,0)::BIGINT former_employees,coalesce(total_positions,0)::BIGINT total_positions,coalesce(active_positions_count,0)::BIGINT active_positions_count,
round(coalesce(current_active_employees,0)*100.0/NULLIF(total_positions,0),2)::DOUBLE position_fill_rate,coalesce(new_assignments_last_year,0)::BIGINT new_assignments_last_year,coalesce(departures_last_year,0)::BIGINT departures_last_year,round(coalesce(departures_last_year,0)*100.0/NULLIF(current_active_employees,0),2)::DOUBLE annual_turnover_rate,
round(coalesce(avg_current_days,0)/365.0,2)::DOUBLE avg_current_tenure_years,round(coalesce(avg_former_days,0)/365.0,2)::DOUBLE avg_former_tenure_years,coalesce(unique_organization_roles,0)::BIGINT unique_organization_roles,coalesce(management_role_employees,0)::BIGINT management_role_employees,coalesce(director_role_employees,0)::BIGINT director_role_employees,coalesce(lead_role_employees,0)::BIGINT lead_role_employees,
round((coalesce(management_role_employees,0)+coalesce(director_role_employees,0))*100.0/NULLIF(current_active_employees,0),2)::DOUBLE management_ratio,coalesce(avg_employee_performance_score,0)::DOUBLE avg_employee_performance_score,coalesce(avg_career_development_score,0)::DOUBLE avg_career_development_score,coalesce(avg_retention_stability_score,0)::DOUBLE avg_retention_stability_score,
coalesce(high_value_stable_employees,0)::BIGINT high_value_stable_employees,coalesce(high_value_flight_risk_employees,0)::BIGINT high_value_flight_risk_employees,coalesce(stable_development_employees,0)::BIGINT stable_development_employees,coalesce(development_required_employees,0)::BIGINT development_required_employees,coalesce(high_risk_employees,0)::BIGINT high_risk_employees,coalesce(medium_risk_employees,0)::BIGINT medium_risk_employees,coalesce(low_risk_employees,0)::BIGINT low_risk_employees,
round(coalesce(high_risk_employees,0)*100.0/NULLIF(current_active_employees,0),2)::DOUBLE high_risk_employee_percentage,coalesce(new_hire_employees,0)::BIGINT new_hire_employees,coalesce(junior_employees,0)::BIGINT junior_employees,coalesce(experienced_employees,0)::BIGINT experienced_employees,coalesce(senior_employees,0)::BIGINT senior_employees,coalesce(veteran_employees,0)::BIGINT veteran_employees,coalesce(ethnic_diversity_count,0)::BIGINT ethnic_diversity_count,coalesce(military_veterans_count,0)::BIGINT military_veterans_count,coalesce(avg_employee_age,0)::DOUBLE avg_employee_age,
coalesce(entry_level_employees,0)::BIGINT entry_level_employees,coalesce(mid_level_employees,0)::BIGINT mid_level_employees,coalesce(senior_level_employees,0)::BIGINT senior_level_employees,coalesce(executive_level_employees,0)::BIGINT executive_level_employees,coalesce(total_promotions_in_organization,0)::HUGEINT total_promotions_in_organization,coalesce(high_achievers_count,0)::BIGINT high_achievers_count,coalesce(fast_track_employees_count,0)::BIGINT fast_track_employees_count,
round(least(30,coalesce(avg_employee_performance_score,0)*.3)+CASE WHEN departures_last_year=0 THEN 25 WHEN annual_turnover_rate<=10 THEN 25 WHEN annual_turnover_rate<=20 THEN 20 WHEN annual_turnover_rate<=30 THEN 15 WHEN annual_turnover_rate<=40 THEN 10 ELSE 5 END+least(20,coalesce(avg_career_development_score,0)*.2)+CASE WHEN position_fill_rate>=90 THEN 15 WHEN position_fill_rate>=75 THEN 12 WHEN position_fill_rate>=60 THEN 9 ELSE 6 END+CASE WHEN high_risk_employee_percentage<=10 THEN 10 WHEN high_risk_employee_percentage<=20 THEN 7 WHEN high_risk_employee_percentage<=30 THEN 4 ELSE 2 END,2)::DOUBLE organization_health_score,
CASE WHEN avg_employee_performance_score>=80 THEN 'Excellent' WHEN avg_employee_performance_score>=60 THEN 'Good' WHEN avg_employee_performance_score>=40 THEN 'Average' ELSE 'Needs Improvement' END performance_category,
CASE WHEN current_active_employees=0 THEN 'Empty' WHEN current_active_employees<=5 THEN 'Micro' WHEN current_active_employees<=15 THEN 'Small' WHEN current_active_employees<=50 THEN 'Medium' WHEN current_active_employees<=200 THEN 'Large' ELSE 'Enterprise' END organization_size_category,
coalesce(last_activity_date,effective_start) last_activity_date,coalesce(last_departure_date,DATE '1900-01-01') last_departure_date,
CASE WHEN current_active_employees=0 THEN 'Review Organization Necessity' WHEN annual_turnover_rate>30 THEN 'Focus on Retention' WHEN high_risk_employee_percentage>25 THEN 'Address Employee Risk' WHEN position_fill_rate<70 THEN 'Improve Staffing' WHEN avg_employee_performance_score<50 THEN 'Enhance Performance Management' WHEN management_ratio>40 THEN 'Optimize Structure' ELSE 'Maintain Excellence' END management_recommendation,
CASE WHEN organization_name IS NULL OR trim(organization_name)='' THEN 'ERROR: Missing organization name' WHEN current_active_employees>total_positions+10 THEN 'WARNING: Employees exceed positions' WHEN annual_turnover_rate>100 THEN 'WARNING: Turnover exceeds 100%' WHEN organization_age_days<0 THEN 'ERROR: Negative organization age' ELSE 'VALID' END data_quality_flag,current_timestamp::TIMESTAMPTZ analysis_timestamp
FROM joined
SQL
```
```json
{
  "event_id": 38,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/38.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 23658,
    "decoded_characters": 0
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/38.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text

```

### event 39

```json
{
  "event_id": 39,
  "agent_command_sequence": 18,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/39.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1590,
    "decoded_characters": 164
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/39.json",
  "timestamp": "2026-10-25T02:52:12.517162",
  "target_table_name_hits": [],
  "source_table_name_hits": [
    "staging.stg_workday__worker_position_organization",
    "staging.stg_workday__organization_role_worker",
    "stg_workday__worker_position_organization",
    "staging.stg_workday__organization_role",
    "stg_workday__organization_role_worker",
    "staging.stg_workday__organization",
    "stg_workday__organization_role",
    "stg_workday__organization"
  ],
  "full_original_characters": 10290,
  "retention": "index_and_first_line_only",
  "first_line_original": "python3 - <<'PY'\n"
}
```
```json
{
  "event_id": 40,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/40.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1273,
    "decoded_characters": 10126
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/40.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```

### event 43

```json
{
  "event_id": 43,
  "agent_command_sequence": 20,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/43.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 2458,
    "decoded_characters": 598
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/43.json",
  "timestamp": "2026-10-25T02:58:00.085058",
  "target_table_name_hits": [],
  "source_table_name_hits": [
    "stg_workday__worker_position_organization"
  ],
  "full_original_characters": 1708,
  "retention": "index_and_first_line_only",
  "first_line_original": "sed -i 's/FROM raw.worker_position AS r/FROM raw.worker_position_history AS r/' sql/staging/stg_workday__worker_position.sql; sed -i 's/FROM raw.worker_position_organization AS r/FROM raw.worker_position_organization_history AS r/' sql/staging/stg_workday__worker_position_organization.sql; sed -i \"s/THEN 20 ELSE 0)>=/THEN 20 ELSE 0 END)>=/g\" sql/intermediate/int_workday__organization_metrics.sql; sed -i \"s/THEN 20 ELSE 0)\\(>=\\)/THEN 20 ELSE 0 END)\\1/g\" sql/intermediate/int_workday__organization_metrics.sql; grep -n 'performance_category' sql/intermediate/int_workday__organization_metrics.sql"
}
```
```json
{
  "event_id": 44,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/44.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 2141,
    "decoded_characters": 1110
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/44.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```

### event 47

```json
{
  "event_id": 47,
  "agent_command_sequence": 22,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/47.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 2525,
    "decoded_characters": 617
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/47.json",
  "timestamp": "2026-10-25T02:58:06.922983",
  "target_table_name_hits": [],
  "source_table_name_hits": [
    "stg_workday__worker_position_organization"
  ],
  "full_original_characters": 771,
  "retention": "index_and_first_line_only",
  "first_line_original": "python3 - <<'PY'\n"
}
```
```json
{
  "event_id": 48,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/48.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 2207,
    "decoded_characters": 154
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/48.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```

### event 49

```json
{
  "event_id": 49,
  "agent_command_sequence": 23,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/49.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 25997,
    "decoded_characters": 12316
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/49.json",
  "timestamp": "2026-10-25T02:58:31.673058",
  "target_table_name_hits": [],
  "source_table_name_hits": [
    "staging.stg_workday__worker_position_organization",
    "stg_workday__worker_position_organization",
    "workday__employee_overview"
  ],
  "full_original_characters": 12316,
  "retention": "index_and_first_line_only",
  "first_line_original": "cat > sql/marts/workday__job_overview.sql <<'SQL'\n"
}
```
```json
{
  "event_id": 50,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/50.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 25679,
    "decoded_characters": 0
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/50.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```

### event 51

```json
{
  "event_id": 51,
  "agent_command_sequence": 24,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/51.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 24471,
    "decoded_characters": 11550
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/51.json",
  "timestamp": "2026-10-25T02:58:50.915115",
  "target_table_name_hits": [],
  "source_table_name_hits": [
    "workday__employee_overview"
  ],
  "full_original_characters": 11550,
  "retention": "index_and_first_line_only",
  "first_line_original": "cat > sql/marts/workday__position_overview.sql <<'SQL'\n"
}
```
```json
{
  "event_id": 52,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/52.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 24153,
    "decoded_characters": 0
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/52.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```

### event 53

```json
{
  "event_id": 53,
  "agent_command_sequence": 25,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/53.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1561,
    "decoded_characters": 149
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/53.json",
  "timestamp": "2026-10-25T02:59:07.386827",
  "target_table_name_hits": [
    "workday__organization_overview"
  ],
  "source_table_name_hits": [
    "staging.stg_workday__worker_position_organization",
    "staging.stg_workday__organization_role_worker",
    "stg_workday__worker_position_organization",
    "staging.stg_workday__organization_role",
    "stg_workday__organization_role_worker",
    "staging.stg_workday__organization",
    "stg_workday__organization_role",
    "workday__employee_overview",
    "stg_workday__organization"
  ],
  "full_original_characters": 10736,
  "retention": "full_original"
}
```
```bash
python3 - <<'PY'
from run import WorkdayDataPipeline
p=WorkdayDataPipeline(target_db_path='/tmp/check2.duckdb'); print('SUCCESS',p.run_pipeline())
PY
```
```json
{
  "event_id": 54,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/54.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1243,
    "decoded_characters": 10587
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/54.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
2026-10-25 02:59:07,509 - INFO - 🚀 Starting Workday data pipeline execution
2026-10-25 02:59:07,509 - INFO - Source database: workday_start.duckdb
2026-10-25 02:59:07,509 - INFO - Target database: /tmp/check2.duckdb
2026-10-25 02:59:07,509 - INFO - 📥 Creating new layered database: /tmp/check2.duckdb
2026-10-25 02:59:07,522 - INFO - 🏗️ Creating Schema layered architecture
2026-10-25 02:59:07,527 - INFO -   ✓ Created schema: raw
2026-10-25 02:59:07,531 - INFO -   ✓ Created schema: staging
2026-10-25 02:59:07,534 - INFO -   ✓ Created schema: intermediate
2026-10-25 02:59:07,538 - INFO -   ✓ Created schema: mart
2026-10-25 02:59:07,538 - INFO - 📥 Importing raw data into the raw schema
2026-10-25 02:59:07,552 - INFO - Found 27 raw tables
2026-10-25 02:59:08,234 - INFO -   ✓ raw.job_family: 120 rows
2026-10-25 02:59:08,311 - INFO -   ✓ raw.job_family_group: 24 rows
2026-10-25 02:59:08,676 - INFO -   ✓ raw.job_family_to_group: 120 rows
2026-10-25 02:59:11,310 - INFO -   ✓ raw.job_family_to_profile: 900 rows
2026-10-25 02:59:14,131 - INFO -   ✓ raw.job_profile: 900 rows
2026-10-25 02:59:14,863 - INFO -   ✓ raw.organization: 230 rows
2026-10-25 02:59:19,584 - INFO -   ✓ raw.organization_job_family: 1516 rows
2026-10-25 02:59:20,847 - INFO -   ✓ raw.organization_role: 407 rows
2026-10-25 02:59:22,218 - INFO -   ✓ raw.organization_role_worker: 418 rows
2026-10-25 02:59:45,610 - INFO -   ✓ raw.person_email: 7284 rows
2026-10-25 03:00:01,921 - INFO -   ✓ raw.person_ethnicity: 5200 rows
2026-10-25 03:00:18,793 - INFO -   ✓ raw.person_info_history: 5200 rows
2026-10-25 03:00:20,432 - INFO -   ✓ raw.person_military_service: 520 rows
2026-10-25 03:00:37,097 - INFO -   ✓ raw.person_name: 5200 rows
2026-10-25 03:00:50,667 - INFO -   ✓ raw.position: 4000 rows
2026-10-25 03:01:04,181 - INFO -   ✓ raw.position_job_profile: 4000 rows
2026-10-25 03:01:17,794 - INFO -   ✓ raw.position_organization: 4000 rows
2026-10-25 03:02:00,017 - INFO -   ✓ raw.worker_history: 10417 rows
2026-10-25 03:02:04,620 - INFO -   ✓ raw.worker_leave_status: 1327 rows
2026-10-25 03:02:40,243 - INFO -   ✓ raw.worker_position_history: 10317 rows
2026-10-25 03:03:20,576 - INFO -   ✓ raw.worker_position_organization_history: 10317 rows
2026-10-25 03:03:40,354 - INFO -   ✓ raw.worker_to_person: 5200 rows
2026-10-25 03:03:40,737 - INFO -   ✓ raw.job_family_job_family_group: 120 rows
2026-10-25 03:03:43,555 - INFO -   ✓ raw.job_family_job_profile: 900 rows
2026-10-25 03:03:45,253 - INFO -   ✓ raw.military_service: 520 rows
2026-10-25 03:04:04,912 - INFO -   ✓ raw.personal_information_ethnicity: 5200 rows
2026-10-25 03:04:30,442 - INFO -   ✓ raw.person_contact_email_address: 7284 rows
2026-10-25 03:04:30,447 - INFO - ✓ Raw data import complete
2026-10-25 03:04:30,447 - INFO - ✓ Layered database initialization complete: /tmp/check2.duckdb
2026-10-25 03:04:30,448 - INFO - 🧼 Cleaning up previously generated schemas and tables...
2026-10-25 03:04:30,452 - INFO - ✓ Dropped schema: staging
2026-10-25 03:04:30,456 - INFO - ✓ Dropped schema: intermediate
2026-10-25 03:04:30,460 - INFO - ✓ Dropped schema: mart
2026-10-25 03:04:30,461 - INFO - Cleanup complete
2026-10-25 03:04:30,461 - INFO - 🏗️ Creating Schema layered architecture
2026-10-25 03:04:30,461 - INFO -   ✓ Created schema: raw
2026-10-25 03:04:30,464 - INFO -   ✓ Created schema: staging
2026-10-25 03:04:30,467 - INFO -   ✓ Created schema: intermediate
2026-10-25 03:04:30,470 - INFO -   ✓ Created schema: mart
2026-10-25 03:04:30,470 - INFO - 
=== Executing STAGING Layer ===
2026-10-25 03:04:30,470 - INFO - Description: Standardize Raw Data Layer - cleans and normalizes raw data imported from source systems
2026-10-25 03:04:30,470 - INFO - Executing: staging.stg_workday__worker
2026-10-25 03:04:30,482 - INFO - ✓ staging.stg_workday__worker: 10,414 rows
2026-10-25 03:04:30,482 - INFO - Executing: staging.stg_workday__personal_information
2026-10-25 03:04:30,497 - INFO - ✓ staging.stg_workday__personal_information: 5,196 rows
2026-10-25 03:04:30,497 - INFO - Executing: staging.stg_workday__person_name
2026-10-25 03:04:30,511 - INFO - ✓ staging.stg_workday__person_name: 5,200 rows
2026-10-25 03:04:30,511 - INFO - Executing: staging.stg_workday__person_contact_email_address
2026-10-25 03:04:30,527 - INFO - ✓ staging.stg_workday__person_contact_email_address: 7,284 rows
2026-10-25 03:04:30,528 - INFO - Executing: staging.stg_workday__personal_information_ethnicity
2026-10-25 03:04:30,541 - INFO - ✓ staging.stg_workday__personal_information_ethnicity: 5,200 rows
2026-10-25 03:04:30,542 - INFO - Executing: staging.stg_workday__military_service
2026-10-25 03:04:30,549 - INFO - ✓ staging.stg_workday__military_service: 520 rows
2026-10-25 03:04:30,550 - INFO - Executing: staging.stg_workday__worker_position
2026-10-25 03:04:30,559 - INFO - ✓ staging.stg_workday__worker_position: 10,317 rows
2026-10-25 03:04:30,560 - INFO - Executing: staging.stg_workday__position
2026-10-25 03:04:30,569 - INFO - ✓ staging.stg_workday__position: 4,000 rows
2026-10-25 03:04:30,569 - INFO - Executing: staging.stg_workday__job_profile
2026-10-25 03:04:30,585 - INFO - ✓ staging.stg_workday__job_profile: 900 rows
2026-10-25 03:04:30,585 - INFO - Executing: staging.stg_workday__organization
2026-10-25 03:04:30,593 - INFO - ✓ staging.stg_workday__organization: 228 rows
2026-10-25 03:04:30,593 - INFO - Executing: staging.stg_workday__job_family
2026-10-25 03:04:30,598 - INFO - ✓ staging.stg_workday__job_family: 120 rows
2026-10-25 03:04:30,599 - INFO - Executing: staging.stg_workday__job_family_group
2026-10-25 03:04:30,603 - INFO - ✓ staging.stg_workday__job_family_group: 24 rows
2026-10-25 03:04:30,603 - INFO - Executing: staging.stg_workday__job_family_job_profile
2026-10-25 03:04:30,608 - INFO - ✓ staging.stg_workday__job_family_job_profile: 900 rows
2026-10-25 03:04:30,609 - INFO - Executing: staging.stg_workday__job_family_job_family_group
2026-10-25 03:04:30,614 - INFO - ✓ staging.stg_workday__job_family_job_family_group: 120 rows
2026-10-25 03:04:30,615 - INFO - Executing: staging.stg_workday__organization_job_family
2026-10-25 03:04:30,621 - INFO - ✓ staging.stg_workday__organization_job_family: 1,516 rows
2026-10-25 03:04:30,621 - INFO - Executing: staging.stg_workday__organization_role
2026-10-25 03:04:30,626 - INFO - ✓ staging.stg_workday__organization_role: 407 rows
2026-10-25 03:04:30,626 - INFO - Executing: staging.stg_workday__organization_role_worker
2026-10-25 03:04:30,631 - INFO - ✓ staging.stg_workday__organization_role_worker: 418 rows
2026-10-25 03:04:30,631 - INFO - Executing: staging.stg_workday__position_job_profile
2026-10-25 03:04:30,638 - INFO - ✓ staging.stg_workday__position_job_profile: 4,000 rows
2026-10-25 03:04:30,638 - INFO - Executing: staging.stg_workday__position_organization
2026-10-25 03:04:30,644 - INFO - ✓ staging.stg_workday__position_organization: 4,000 rows
2026-10-25 03:04:30,644 - INFO - Executing: staging.stg_workday__worker_leave_status
2026-10-25 03:04:30,649 - INFO - ✓ staging.stg_workday__worker_leave_status: 1,327 rows
2026-10-25 03:04:30,650 - INFO - Executing: staging.stg_workday__worker_position_organization
2026-10-25 03:04:30,664 - INFO - ✓ staging.stg_workday__worker_position_organization: 10,317 rows
2026-10-25 03:04:30,664 - INFO - STAGING layer complete: 21/21 tables created successfully
2026-10-25 03:04:30,665 - INFO - 
=== Executing INTERMEDIATE Layer ===
2026-10-25 03:04:30,665 - INFO - Description: Intermediate processing layer - business logic processing and data aggregation
2026-10-25 03:04:30,665 - INFO - Executing: intermediate.int_workday__worker_details
2026-10-25 03:04:30,676 - INFO - ✓ intermediate.int_workday__worker_details: 10,414 rows
2026-10-25 03:04:30,676 - INFO - Executing: intermediate.int_workday__personal_details
2026-10-25 03:04:30,703 - INFO - ✓ intermediate.int_workday__personal_details: 5,722 rows
2026-10-25 03:04:30,703 - INFO - Executing: intermediate.int_workday__worker_position_enriched
2026-10-25 03:04:30,720 - INFO - ✓ intermediate.int_workday__worker_position_enriched: 10,317 rows
2026-10-25 03:04:30,720 - INFO - Executing: intermediate.int_workday__worker_employee_enhanced
2026-10-25 03:04:30,801 - INFO - ✓ intermediate.int_workday__worker_employee_enhanced: 22,849 rows
2026-10-25 03:04:30,801 - INFO - Executing: intermediate.int_workday__employee_lifecycle
2026-10-25 03:04:30,827 - INFO - ✓ intermediate.int_workday__employee_lifecycle: 10,414 rows
2026-10-25 03:04:30,827 - INFO - Executing: intermediate.int_workday__organization_metrics
2026-10-25 03:04:30,871 - INFO - ✓ intermediate.int_workday__organization_metrics: 117 rows
2026-10-25 03:04:30,871 - INFO - Executing: intermediate.int_workday__career_progression
2026-10-25 03:04:31,223 - INFO - ✓ intermediate.int_workday__career_progression: 10,317 rows
2026-10-25 03:04:31,223 - INFO - INTERMEDIATE layer complete: 7/7 tables created successfully
2026-10-25 03:04:31,223 - INFO - 
=== Executing MARTS Layer ===
2026-10-25 03:04:31,223 - INFO - Description: Data Mart Layer - Final Data Table for Analysis
2026-10-25 03:04:31,223 - INFO - Executing: mart.workday__employee_overview
2026-10-25 03:04:31,944 - INFO - ✓ mart.workday__employee_overview: 57,411 rows
2026-10-25 03:04:31,944 - INFO - Executing: mart.workday__job_overview
2026-10-25 03:04:32,009 - INFO - ✓ mart.workday__job_overview: 900 rows
2026-10-25 03:04:32,009 - INFO - Executing: mart.workday__position_overview
2026-10-25 03:04:32,009 - ERROR - ✗ mart.workday__position_overview: Parser Error: syntax error at or near "similar"

LINE 12: ), similar AS (
            ^
2026-10-25 03:04:32,010 - INFO - Executing: mart.workday__organization_overview
2026-10-25 03:04:32,012 - ERROR - ✗ mart.workday__organization_overview: Binder Error: Table "r" does not have a column named "role_id"

Candidate bindings: : "source_relation"

LINE 11: ... ow.organization_id,'workday' source_relation,count(DISTINCT r.role_id) unique_organization_roles,count(DISTINCT ow.work...
                                                                         ^
2026-10-25 03:04:32,012 - INFO - Executing: mart.workday__workforce_analytics
2026-10-25 03:04:32,076 - INFO - ✓ mart.workday__workforce_analytics: 1 rows
2026-10-25 03:04:32,076 - INFO - Executing: mart.workday__organization_performance
2026-10-25 03:04:32,091 - INFO - ✓ mart.workday__organization_performance: 0 rows
2026-10-25 03:04:32,092 - INFO - MARTS layer complete: 4/6 tables created successfully
2026-10-25 03:04:32,092 - ERROR - 
❌ Errors occurred during data pipeline execution
SUCCESS False
```

### event 55

```json
{
  "event_id": 55,
  "agent_command_sequence": 26,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/55.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 3351,
    "decoded_characters": 1025
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/55.json",
  "timestamp": "2026-10-25T03:04:39.498277",
  "target_table_name_hits": [
    "workday__organization_overview"
  ],
  "source_table_name_hits": [
    "staging.stg_workday__worker_position_organization",
    "stg_workday__worker_position_organization",
    "workday__employee_overview"
  ],
  "full_original_characters": 1509,
  "retention": "full_original"
}
```
```bash
sed -i 's/), similar AS (/), similar_positions AS (/' sql/marts/workday__position_overview.sql; sed -i 's/LEFT JOIN similar s /LEFT JOIN similar_positions s /' sql/marts/workday__position_overview.sql; sed -i "s/count(DISTINCT r.role_id)/count(DISTINCT r.organization_role_id)/" sql/marts/workday__organization_overview.sql; sed -i "s/ow.role_id=r.organization_role_id/ow.role_id=r.organization_role_id/" sql/marts/workday__organization_overview.sql; python3 - <<'PY'
import duckdb
c=duckdb.connect('/tmp/check2.duckdb')
for q in ["select count(*) from staging.stg_workday__worker_position_organization where effective_end is null", "select organization_id,count(*) from intermediate.int_workday__organization_metrics group by 1 order by 2 desc limit 2", "select organization_id,count(*) from mart.workday__employee_overview group by 1 order by 2 desc limit 5", "select count(*) from mart.workday__employee_overview where organization_id<>'Unknown'"]:
 try: print(q,c.execute(q).fetchall())
 except Exception as e:print(e)
PY
```
```json
{
  "event_id": 56,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/56.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 3033,
    "decoded_characters": 484
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/56.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
select count(*) from staging.stg_workday__worker_position_organization where effective_end is null [(0,)]
select organization_id,count(*) from intermediate.int_workday__organization_metrics group by 1 order by 2 desc limit 2 [('ORG00000160', 1), ('ORG00000216', 1)]
select organization_id,count(*) from mart.workday__employee_overview group by 1 order by 2 desc limit 5 [('Unknown', 57411)]
select count(*) from mart.workday__employee_overview where organization_id<>'Unknown' [(0,)]
```

### event 57

```json
{
  "event_id": 57,
  "agent_command_sequence": 27,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/57.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 2022,
    "decoded_characters": 375
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/57.json",
  "timestamp": "2026-10-25T03:04:45.843342",
  "target_table_name_hits": [
    "workday__organization_overview"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 768,
  "retention": "full_original"
}
```
```bash
python3 - <<'PY'
import duckdb,pathlib
c=duckdb.connect('/tmp/check2.duckdb')
for n in ['workday__position_overview','workday__organization_overview']:
 try:
  c.execute(f'create or replace table mart.{n} as ({pathlib.Path("sql/marts/"+n+".sql").read_text()})');print('OK',n,c.execute(f'select count(*) from mart.{n}').fetchone())
 except Exception as e: print('FAIL',n,e)
PY
```
```json
{
  "event_id": 58,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/58.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1704,
    "decoded_characters": 393
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/58.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
OK workday__position_overview (4000,)
FAIL workday__organization_overview Binder Error: Table "r" does not have a column named "org_role_code"

Candidate bindings: : "organization_id"

LINE 11: ...ganization_roles,count(DISTINCT ow.worker_id) FILTER(WHERE r.org_role_code ILIKE '%Manager%') management_role_employees...
                                                                       ^
```

### event 59

```json
{
  "event_id": 59,
  "agent_command_sequence": 28,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/59.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 2166,
    "decoded_characters": 458
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/59.json",
  "timestamp": "2026-10-25T03:04:49.324962",
  "target_table_name_hits": [
    "workday__organization_overview"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 763,
  "retention": "full_original"
}
```
```bash
sed -i 's/r.org_role_code/r.organization_role_code/g' sql/marts/workday__organization_overview.sql; python3 - <<'PY'
import duckdb,pathlib
c=duckdb.connect('/tmp/check2.duckdb')
try:c.execute('create or replace table mart.workday__organization_overview as ('+pathlib.Path('sql/marts/workday__organization_overview.sql').read_text()+')');print(c.execute('select count(*) from mart.workday__organization_overview').fetchone())
except Exception as e:print(e)
PY
```
```json
{
  "event_id": 60,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/60.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1848,
    "decoded_characters": 305
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/60.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
Binder Error: Table "ow" does not have a column named "worker_id"

Candidate bindings: : "role_id"

LINE 11: ...nization_role_id) unique_organization_roles,count(DISTINCT ow.worker_id) FILTER(WHERE r.organization_role_code ILIKE...
                                                                       ^
```

### event 61

```json
{
  "event_id": 61,
  "agent_command_sequence": 29,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/61.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 2166,
    "decoded_characters": 458
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/61.json",
  "timestamp": "2026-10-25T03:04:54.196677",
  "target_table_name_hits": [
    "workday__organization_overview"
  ],
  "source_table_name_hits": [],
  "full_original_characters": 465,
  "retention": "full_original"
}
```
```bash
sed -i 's/ow.worker_id/ow.organization_worker_code/g' sql/marts/workday__organization_overview.sql; python3 - <<'PY'
import duckdb,pathlib
c=duckdb.connect('/tmp/check2.duckdb')
try:c.execute('create or replace table mart.workday__organization_overview as ('+pathlib.Path('sql/marts/workday__organization_overview.sql').read_text()+')');print(c.execute('select count(*) from mart.workday__organization_overview').fetchone())
except Exception as e:print(e)
PY
```
```json
{
  "event_id": 62,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/62.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1848,
    "decoded_characters": 7
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/62.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
(117,)
```

### event 63

```json
{
  "event_id": 63,
  "agent_command_sequence": 30,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/63.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 3179,
    "decoded_characters": 954
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/63.json",
  "timestamp": "2026-10-25T03:05:01.454550",
  "target_table_name_hits": [
    "workday__organization_overview"
  ],
  "source_table_name_hits": [
    "workday__employee_overview"
  ],
  "full_original_characters": 1447,
  "retention": "full_original"
}
```
```bash
python3 - <<'PY'
import duckdb,pathlib,yaml
c=duckdb.connect('/tmp/check2.duckdb')
for n in ['workday__employee_overview','workday__job_overview','workday__position_overview','workday__organization_overview','workday__workforce_analytics','workday__organization_performance']:
 try:
  if n not in ['workday__employee_overview','workday__job_overview','workday__workforce_analytics']:
   c.execute(f'create or replace table mart.{n} as ('+pathlib.Path(f'sql/marts/{n}.sql').read_text()+')')
  cols=[r[0] for r in c.execute(f'describe mart.{n}').fetchall()]
  spec=next(m for m in yaml.safe_load(open('docs/data_contract.yaml'))['modeling_spec']['marts_models'] if m['name']==n)
  expected=[x['name'] for x in spec['columns']]
  print(n,'cols',len(cols),'expect',len(expected),'missing',set(expected)-set(cols),'extra',set(cols)-set(expected),'count',c.execute(f'select count(*) from mart.{n}').fetchone()[0])
 except Exception as e: print('FAILED',n,e)
PY
```
```json
{
  "event_id": 64,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/64.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 2861,
    "decoded_characters": 493
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/64.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
workday__employee_overview cols 79 expect 79 missing set() extra set() count 57411
workday__job_overview cols 60 expect 60 missing set() extra set() count 900
workday__position_overview cols 58 expect 58 missing set() extra set() count 4000
workday__organization_overview cols 64 expect 64 missing set() extra set() count 117
workday__workforce_analytics cols 59 expect 59 missing set() extra set() count 1
workday__organization_performance cols 66 expect 66 missing set() extra set() count 0
```

### event 65

```json
{
  "event_id": 65,
  "agent_command_sequence": 31,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/65.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1420,
    "decoded_characters": 83
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/65.json",
  "timestamp": "2026-10-25T03:05:11.434160",
  "target_table_name_hits": [
    "workday__organization_overview"
  ],
  "source_table_name_hits": [
    "staging.stg_workday__worker_position_organization",
    "staging.stg_workday__organization_role_worker",
    "stg_workday__worker_position_organization",
    "staging.stg_workday__organization_role",
    "stg_workday__organization_role_worker",
    "staging.stg_workday__organization",
    "stg_workday__organization_role",
    "workday__employee_overview",
    "stg_workday__organization"
  ],
  "full_original_characters": 7188,
  "retention": "full_original"
}
```
```bash
python3 run.py > /tmp/run.log 2>&1; status=$?; tail -100 /tmp/run.log; exit $status
```
```json
{
  "event_id": 66,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/66.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 1102,
    "decoded_characters": 7105
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/66.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```
```text
2026-10-25 03:10:41,439 - INFO - 
=== Executing MARTS Layer ===
2026-10-25 03:10:41,440 - INFO - Description: Data Mart Layer - Final Data Table for Analysis
2026-10-25 03:10:41,440 - INFO - Executing: mart.workday__employee_overview
2026-10-25 03:10:42,149 - INFO - ✓ mart.workday__employee_overview: 57,411 rows
2026-10-25 03:10:42,149 - INFO - Executing: mart.workday__job_overview
2026-10-25 03:10:42,213 - INFO - ✓ mart.workday__job_overview: 900 rows
2026-10-25 03:10:42,214 - INFO - Executing: mart.workday__position_overview
2026-10-25 03:10:42,285 - INFO - ✓ mart.workday__position_overview: 4,000 rows
2026-10-25 03:10:42,285 - INFO - Executing: mart.workday__organization_overview
2026-10-25 03:10:42,329 - INFO - ✓ mart.workday__organization_overview: 117 rows
2026-10-25 03:10:42,329 - INFO - Executing: mart.workday__workforce_analytics
2026-10-25 03:10:42,393 - INFO - ✓ mart.workday__workforce_analytics: 1 rows
2026-10-25 03:10:42,393 - INFO - Executing: mart.workday__organization_performance
2026-10-25 03:10:42,407 - INFO - ✓ mart.workday__organization_performance: 0 rows
2026-10-25 03:10:42,407 - INFO - MARTS layer complete: 6/6 tables created successfully
2026-10-25 03:10:42,408 - INFO - 
🎉 Workday data pipeline execution completed successfully!
2026-10-25 03:10:42,408 - INFO - ✨ The complete data warehouse has been generated: workday.duckdb
2026-10-25 03:10:42,408 - INFO - 
=== Final Data Statistics (by Schema Layer) ===
2026-10-25 03:10:42,411 - INFO - 
RAW Layer (Schema: raw):
2026-10-25 03:10:42,411 - INFO -   ✓ raw.job_family: 120 rows
2026-10-25 03:10:42,412 - INFO -   ✓ raw.job_family_group: 24 rows
2026-10-25 03:10:42,412 - INFO -   ✓ raw.job_family_job_family_group: 120 rows
2026-10-25 03:10:42,413 - INFO -   ✓ raw.job_family_job_profile: 900 rows
2026-10-25 03:10:42,414 - INFO -   ✓ raw.job_family_to_group: 120 rows
2026-10-25 03:10:42,414 - INFO -   ✓ raw.job_family_to_profile: 900 rows
2026-10-25 03:10:42,415 - INFO -   ✓ raw.job_profile: 900 rows
2026-10-25 03:10:42,416 - INFO -   ✓ raw.military_service: 520 rows
2026-10-25 03:10:42,416 - INFO -   ✓ raw.organization: 230 rows
2026-10-25 03:10:42,417 - INFO -   ✓ raw.organization_job_family: 1,516 rows
2026-10-25 03:10:42,417 - INFO -   ✓ raw.organization_role: 407 rows
2026-10-25 03:10:42,418 - INFO -   ✓ raw.organization_role_worker: 418 rows
2026-10-25 03:10:42,419 - INFO -   ✓ raw.person_contact_email_address: 7,284 rows
2026-10-25 03:10:42,419 - INFO -   ✓ raw.person_email: 7,284 rows
2026-10-25 03:10:42,420 - INFO -   ✓ raw.person_ethnicity: 5,200 rows
2026-10-25 03:10:42,420 - INFO -   ✓ raw.person_info_history: 5,200 rows
2026-10-25 03:10:42,421 - INFO -   ✓ raw.person_military_service: 520 rows
2026-10-25 03:10:42,421 - INFO -   ✓ raw.person_name: 5,200 rows
2026-10-25 03:10:42,422 - INFO -   ✓ raw.personal_information_ethnicity: 5,200 rows
2026-10-25 03:10:42,422 - INFO -   ✓ raw.position: 4,000 rows
2026-10-25 03:10:42,423 - INFO -   ✓ raw.position_job_profile: 4,000 rows
2026-10-25 03:10:42,424 - INFO -   ✓ raw.position_organization: 4,000 rows
2026-10-25 03:10:42,424 - INFO -   ✓ raw.worker_history: 10,417 rows
2026-10-25 03:10:42,425 - INFO -   ✓ raw.worker_leave_status: 1,327 rows
2026-10-25 03:10:42,425 - INFO -   ✓ raw.worker_position_history: 10,317 rows
2026-10-25 03:10:42,426 - INFO -   ✓ raw.worker_position_organization_history: 10,317 rows
2026-10-25 03:10:42,426 - INFO -   ✓ raw.worker_to_person: 5,200 rows
2026-10-25 03:10:42,428 - INFO - 
STAGING Layer (Schema: staging):
2026-10-25 03:10:42,429 - INFO -   ✓ staging.stg_workday__job_family: 120 rows
2026-10-25 03:10:42,430 - INFO -   ✓ staging.stg_workday__job_family_group: 24 rows
2026-10-25 03:10:42,430 - INFO -   ✓ staging.stg_workday__job_family_job_family_group: 120 rows
2026-10-25 03:10:42,431 - INFO -   ✓ staging.stg_workday__job_family_job_profile: 900 rows
2026-10-25 03:10:42,431 - INFO -   ✓ staging.stg_workday__job_profile: 900 rows
2026-10-25 03:10:42,432 - INFO -   ✓ staging.stg_workday__military_service: 520 rows
2026-10-25 03:10:42,433 - INFO -   ✓ staging.stg_workday__organization: 228 rows
2026-10-25 03:10:42,433 - INFO -   ✓ staging.stg_workday__organization_job_family: 1,516 rows
2026-10-25 03:10:42,434 - INFO -   ✓ staging.stg_workday__organization_role: 407 rows
2026-10-25 03:10:42,435 - INFO -   ✓ staging.stg_workday__organization_role_worker: 418 rows
2026-10-25 03:10:42,435 - INFO -   ✓ staging.stg_workday__person_contact_email_address: 7,284 rows
2026-10-25 03:10:42,436 - INFO -   ✓ staging.stg_workday__person_name: 5,200 rows
2026-10-25 03:10:42,436 - INFO -   ✓ staging.stg_workday__personal_information: 5,196 rows
2026-10-25 03:10:42,437 - INFO -   ✓ staging.stg_workday__personal_information_ethnicity: 5,200 rows
2026-10-25 03:10:42,437 - INFO -   ✓ staging.stg_workday__position: 4,000 rows
2026-10-25 03:10:42,438 - INFO -   ✓ staging.stg_workday__position_job_profile: 4,000 rows
2026-10-25 03:10:42,439 - INFO -   ✓ staging.stg_workday__position_organization: 4,000 rows
2026-10-25 03:10:42,439 - INFO -   ✓ staging.stg_workday__worker: 10,414 rows
2026-10-25 03:10:42,440 - INFO -   ✓ staging.stg_workday__worker_leave_status: 1,327 rows
2026-10-25 03:10:42,440 - INFO -   ✓ staging.stg_workday__worker_position: 10,317 rows
2026-10-25 03:10:42,441 - INFO -   ✓ staging.stg_workday__worker_position_organization: 10,317 rows
2026-10-25 03:10:42,443 - INFO - 
INTERMEDIATE Layer (Schema: intermediate):
2026-10-25 03:10:42,443 - INFO -   ✓ intermediate.int_workday__career_progression: 10,317 rows
2026-10-25 03:10:42,444 - INFO -   ✓ intermediate.int_workday__employee_lifecycle: 10,414 rows
2026-10-25 03:10:42,444 - INFO -   ✓ intermediate.int_workday__organization_metrics: 117 rows
2026-10-25 03:10:42,445 - INFO -   ✓ intermediate.int_workday__personal_details: 5,722 rows
2026-10-25 03:10:42,446 - INFO -   ✓ intermediate.int_workday__worker_details: 10,414 rows
2026-10-25 03:10:42,446 - INFO -   ✓ intermediate.int_workday__worker_employee_enhanced: 22,849 rows
2026-10-25 03:10:42,447 - INFO -   ✓ intermediate.int_workday__worker_position_enriched: 10,317 rows
2026-10-25 03:10:42,449 - INFO - 
MARTS Layer (Schema: mart):
2026-10-25 03:10:42,450 - INFO -   ✓ mart.workday__employee_overview: 57,411 rows
2026-10-25 03:10:42,451 - INFO -   ✓ mart.workday__job_overview: 900 rows
2026-10-25 03:10:42,451 - INFO -   ✓ mart.workday__organization_overview: 117 rows
2026-10-25 03:10:42,452 - INFO -   ✓ mart.workday__organization_performance: 0 rows
2026-10-25 03:10:42,452 - INFO -   ✓ mart.workday__position_overview: 4,000 rows
2026-10-25 03:10:42,453 - INFO -   ✓ mart.workday__workforce_analytics: 1 rows

✅ Workday data transformation completed successfully!
📋 Transformation Results:
  📥 Source Database: workday_start.duckdb (raw tables only)
  📤 Target Database: workday.duckdb (full layered architecture)

🏗️ Data Architecture:
  📊 Staging Layer - Standardized raw Workday data
  🔄 Intermediate Layer - Business logic for employees and positions
  🎯 Mart Layer - Analysis-ready data for employees, positions, and organizations
```

### event 69

```json
{
  "event_id": 69,
  "agent_command_sequence": 33,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/69.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 2396,
    "decoded_characters": 570
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/69.json",
  "timestamp": "2026-10-25T03:11:04.211896",
  "target_table_name_hits": [],
  "source_table_name_hits": [
    "stg_workday__organization"
  ],
  "full_original_characters": 900,
  "retention": "index_and_first_line_only",
  "first_line_original": "python3 - <<'PY'\n"
}
```
```json
{
  "event_id": 70,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/70.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 2078,
    "decoded_characters": 330
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/70.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 1
}
```

### event 71

```json
{
  "event_id": 71,
  "agent_command_sequence": 34,
  "action_location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/71.json",
    "json_path": [
      "args",
      "command"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 2668,
    "decoded_characters": 702
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/71.json",
  "timestamp": "2026-10-25T03:11:10.163042",
  "target_table_name_hits": [],
  "source_table_name_hits": [
    "staging.stg_workday__worker_position_organization",
    "stg_workday__worker_position_organization",
    "workday__employee_overview",
    "stg_workday__organization"
  ],
  "full_original_characters": 875,
  "retention": "index_and_first_line_only",
  "first_line_original": "python3 - <<'PY'\n"
}
```
```json
{
  "event_id": 72,
  "observation": "run",
  "location": {
    "file": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/72.json",
    "json_path": [
      "content"
    ],
    "file_line": 1,
    "json_string_token_start_offset": 2350,
    "decoded_characters": 173
  },
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/72.json",
  "truncation": {
    "explicit_metadata_flags": {},
    "marker_lines": [],
    "status": "未见显式截断标记"
  },
  "exit_code": 0
}
```

## result_md_table_sentences

```json
{
  "present": true,
  "path": "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/result.md",
  "archive_member": "dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/result.md",
  "sha256": "d6b47ab04a907ddae482636e6e13e106756442ce906b221544a7116ea77ed5bc",
  "sentences": [],
  "policy": "All sentences naming the table; includes sentences without 008 keywords. Existing D10 ids attached where applicable."
}
```

## original_files

```json
{
  "paths": [
    "/home/katherine/Assumption_Ledger/data/011_agent_alignment/impl-016/workday__organization_overview_2025-10-13.duckdb",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/13.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/14.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/17.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/18.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/25.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/26.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/29.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/30.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/31.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/32.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/33.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/34.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/35.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/36.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/37.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/38.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/39.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/40.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/43.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/44.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/47.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/48.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/49.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/50.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/51.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/52.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/53.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/54.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/55.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/56.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/57.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/58.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/59.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/60.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/61.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/62.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/63.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/64.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/65.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/66.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/69.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/7.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/70.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/71.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/72.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/8.json",
    "/home/katherine/Assumption_Ledger/data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/result.md",
    "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql",
    "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/workday.duckdb",
    "/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml",
    "/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql"
  ],
  "archive": "/home/katherine/Assumption_Ledger/traces/dacomp_deimpl_prev.tar.gz",
  "gold_SQL_search_root": "/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/sql",
  "gold_SQL_search_names": [
    "workday__organization_overview",
    "workday__organization_overview"
  ],
  "source_fingerprints": "records/012_input_before.json"
}
```
