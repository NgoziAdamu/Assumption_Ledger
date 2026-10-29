# impl-016 | marts | workday__organization_overview | 差异：S1；日期 2025-10-13

## 契约完整原文

S3:2024–2230

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

## agent 最终 SQL

S4

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

## gold SQL（仅供定位差异）

S5

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

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 117 | 117 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"organization_id":"org00000006"}</code> |
| K2 | <code>{"organization_id":"org00000028"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| organization_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| access_level | 0 | 0 | 0 | VARCHAR | VARCHAR |
| active_positions_count | 0 | 0 | 0 | BIGINT | BIGINT |
| analysis_timestamp | 117 | 117 | 117 | TIMESTAMP WITH TIME ZONE | TIMESTAMP WITH TIME ZONE |
| annual_turnover_rate | 117 | 117 | 117 | DOUBLE | DOUBLE |
| avg_career_development_score | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_employee_age | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_employee_performance_score | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_former_tenure_years | 5 | 5 | 5 | DOUBLE | DOUBLE |
| avg_retention_stability_score | 0 | 0 | 0 | DOUBLE | DOUBLE |
| current_active_employees | 0 | 0 | 0 | BIGINT | BIGINT |
| data_quality_flag | 0 | 0 | 0 | VARCHAR | VARCHAR |
| departures_last_year | 0 | 0 | 0 | BIGINT | BIGINT |
| development_required_employees | 0 | 0 | 0 | BIGINT | BIGINT |
| director_role_employees | 0 | 0 | 0 | BIGINT | BIGINT |
| entry_level_employees | 0 | 0 | 0 | BIGINT | BIGINT |
| ethnic_diversity_count | 0 | 0 | 0 | BIGINT | BIGINT |
| executive_level_employees | 0 | 0 | 0 | BIGINT | BIGINT |
| experienced_employees | 0 | 0 | 0 | BIGINT | BIGINT |
| fast_track_employees_count | 0 | 0 | 0 | BIGINT | BIGINT |
| former_employees | 0 | 0 | 0 | BIGINT | BIGINT |
| high_achievers_count | 0 | 0 | 0 | BIGINT | BIGINT |
| high_risk_employees | 0 | 0 | 0 | BIGINT | BIGINT |
| high_value_flight_risk_employees | 0 | 0 | 0 | BIGINT | BIGINT |
| high_value_stable_employees | 0 | 0 | 0 | BIGINT | BIGINT |
| junior_employees | 0 | 0 | 0 | BIGINT | BIGINT |
| last_activity_date | 0 | 0 | 0 | DATE | DATE |
| last_departure_date | 0 | 0 | 0 | DATE | DATE |
| lead_role_employees | 0 | 0 | 0 | BIGINT | BIGINT |
| low_risk_employees | 0 | 0 | 0 | BIGINT | BIGINT |
| management_ratio | 117 | 117 | 117 | DOUBLE | DOUBLE |
| management_recommendation | 0 | 0 | 0 | VARCHAR | VARCHAR |
| management_role_employees | 0 | 0 | 0 | BIGINT | BIGINT |
| medium_risk_employees | 0 | 0 | 0 | BIGINT | BIGINT |
| mid_level_employees | 0 | 0 | 0 | BIGINT | BIGINT |
| military_veterans_count | 0 | 0 | 0 | BIGINT | BIGINT |
| new_assignments_last_year | 0 | 0 | 0 | BIGINT | BIGINT |
| new_hire_employees | 0 | 0 | 0 | BIGINT | BIGINT |
| organization_age_days | 0 | 0 | 0 | BIGINT | BIGINT |
| organization_age_years | 0 | 0 | 0 | DOUBLE | DOUBLE |
| organization_code | 0 | 0 | 0 | VARCHAR | VARCHAR |
| organization_created_date | 0 | 0 | 0 | DATE | DATE |
| organization_health_score | 117 | 117 | 117 | DOUBLE | DOUBLE |
| organization_maturity_level | 117 | 117 | 117 | VARCHAR | VARCHAR |
| organization_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| organization_size_category | 117 | 117 | 117 | VARCHAR | VARCHAR |
| organization_sub_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| organization_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| organizational_level | 0 | 0 | 0 | VARCHAR | VARCHAR |
| performance_category | 0 | 0 | 0 | VARCHAR | VARCHAR |
| position_fill_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| senior_employees | 0 | 0 | 0 | BIGINT | BIGINT |
| senior_level_employees | 0 | 0 | 0 | BIGINT | BIGINT |
| stable_development_employees | 0 | 0 | 0 | BIGINT | BIGINT |
| staffing_model | 0 | 0 | 0 | VARCHAR | VARCHAR |
| total_employees_ever | 0 | 0 | 0 | BIGINT | BIGINT |
| total_positions | 0 | 0 | 0 | BIGINT | BIGINT |
| total_promotions_in_organization | 0 | 0 | 0 | HUGEINT | HUGEINT |
| unique_organization_roles | 106 | 106 | 106 | BIGINT | BIGINT |
| veteran_employees | 0 | 0 | 0 | BIGINT | BIGINT |
| visibility | 0 | 0 | 0 | VARCHAR | VARCHAR |

analysis_timestamp 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 2025-10-13 08:00:00+08 | 2025-10-13 13:18:28.226+08 |

annual_turnover_rate 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0.0 |

avg_former_tenure_years 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | 0.69 | 0.7 |

management_ratio 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 0.0 |

organization_health_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 13.0 | 36.0 |

organization_maturity_level 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | Young | Young Organization (1-3 years) |

organization_size_category 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | Empty | Empty Organization |

unique_organization_roles 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 2 | 7 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>3列；[{"column":"annual_turnover_rate","table_rows":117}]</code> |
| A3_constant_nonnull_column | <code>42列；[{"column":"source_relation","value":"workday"}]</code> |
| A4_equal_columns | <code>3组；[{"columns":["total_employees_ever","former_employees"],"nonnull_equal_rows":117,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>3组；[{"columns":["total_employees_ever","former_employees"],"nonnull_equal_rows":117,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| B7_specified_not_read | <code>["marts.workday__employee_overview (filtered to organization_id != 'unknown')"]</code> |
| C9_agent_runtime_text | <code>S4:3 current_date；命中数=9</code> |
| C9_gold_runtime_text | <code>S5:28 current_date；命中数=8</code> |
| C9_contract_runtime_text | <code>S3:2033 current_date；命中数=5</code> |

## 轨迹索引（不放输出原文）

本题事件总数：85；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; find sql -type f -maxdepth 3 -print</code> | 3401 | true | false |
| 13 | run | <code>find sql -type f -printf '%p %s bytes\n' &#124; sort; sed -n '240,420p' run.py; sed -n '1,100p' docs/data_contract.yaml</code> | 7949 | false | false |
| 17 | run | <code>python3 - &lt;&lt;'PY'<br>import yaml<br>x=yaml.safe_load(open('docs/data_contract.yaml'))<br>print(x.keys(),len(x['staging_contract']['tables']))<br>print([m['name'] for m in x['modeling_spec']['intermediate_models']]</code> | 3942 | true | false |
| 25 | run | <code>cat &gt; sql/intermediate/int_workday__organization_metrics.sql &lt;&lt;'SQL'<br>WITH active_org AS (<br>    SELECT * FROM staging.stg_workday__organization WHERE is_inactive = FALSE<br>), assignments AS (<br>    SELECT w</code> | 0 | false | false |
| 29 | run | <code>python3 - &lt;&lt;'PY'<br>import yaml<br>x=yaml.safe_load(open('docs/data_contract.yaml'))<br>for m in x['modeling_spec']['marts_models']:<br> print('\n',m['name'],len(m['columns']))<br> print(', '.join(c['name'] for c in</code> | 8785 | true | false |
| 31 | run | <code>cat &gt; sql/marts/workday__employee_overview.sql &lt;&lt;'SQL'<br>WITH base AS (<br> SELECT e.*, md5(coalesce(cast(worker_id as varchar),'_dbt_utils_surrogate_key_null_')&#124;&#124;'-'&#124;&#124;coalesce(source_relation,'_dbt_utils_</code> | 0 | false | false |
| 33 | run | <code>cat &gt; sql/marts/workday__workforce_analytics.sql &lt;&lt;'SQL'<br>WITH base AS (SELECT * FROM mart.workday__employee_overview), metrics AS (<br> SELECT 'workday'::VARCHAR source_relation,current_date::DATE analys</code> | 0 | false | false |
| 35 | run | <code>cat &gt; sql/marts/workday__organization_performance.sql &lt;&lt;'SQL'<br>WITH org AS (SELECT * FROM intermediate.int_workday__organization_metrics), emp AS (<br> SELECT organization_id,source_relation,<br> count(DISTI</code> | 0 | false | false |
| 37 | run | <code>cat &gt; sql/marts/workday__organization_overview.sql &lt;&lt;'SQL'<br>WITH active_org AS (SELECT * FROM staging.stg_workday__organization WHERE is_inactive=FALSE), rel AS (<br> SELECT worker_id,organization_id,sour</code> | 0 | false | false |
| 39 | run | <code>python3 - &lt;&lt;'PY'<br>from run import WorkdayDataPipeline<br>p=WorkdayDataPipeline(target_db_path='/tmp/check.duckdb'); print(p.run_pipeline(['staging','intermediate']))<br>PY</code> | 10126 | false | false |
| 43 | run | <code>sed -i 's/FROM raw.worker_position AS r/FROM raw.worker_position_history AS r/' sql/staging/stg_workday__worker_position.sql; sed -i 's/FROM raw.worker_position_organization AS r/FROM raw.worker_posit</code> | 1110 | false | false |
| 47 | run | <code>python3 - &lt;&lt;'PY'<br>import duckdb, pathlib<br>c=duckdb.connect('/tmp/check.duckdb')<br>for n in ['stg_workday__worker_position','stg_workday__worker_position_organization']:<br> c.execute(f'create or replace tabl</code> | 154 | false | false |
| 49 | run | <code>cat &gt; sql/marts/workday__job_overview.sql &lt;&lt;'SQL'<br>WITH family AS (<br> SELECT jfjp.job_profile_id,jf.source_relation,count(DISTINCT jf.job_family_id) associated_job_families_count,count(DISTINCT jfg.job_</code> | 0 | false | false |
| 51 | run | <code>cat &gt; sql/marts/workday__position_overview.sql &lt;&lt;'SQL'<br>WITH base AS (SELECT * FROM staging.stg_workday__position), history AS (<br> SELECT position_id,source_relation,count(DISTINCT worker_id) total_work</code> | 0 | false | false |
| 53 | run | <code>python3 - &lt;&lt;'PY'<br>from run import WorkdayDataPipeline<br>p=WorkdayDataPipeline(target_db_path='/tmp/check2.duckdb'); print('SUCCESS',p.run_pipeline())<br>PY</code> | 10587 | true | false |
| 55 | run | <code>sed -i 's/), similar AS (/), similar_positions AS (/' sql/marts/workday__position_overview.sql; sed -i 's/LEFT JOIN similar s /LEFT JOIN similar_positions s /' sql/marts/workday__position_overview.sql</code> | 484 | false | false |
| 57 | run | <code>python3 - &lt;&lt;'PY'<br>import duckdb,pathlib<br>c=duckdb.connect('/tmp/check2.duckdb')<br>for n in ['workday__position_overview','workday__organization_overview']:<br> try:<br>  c.execute(f'create or replace table mart</code> | 393 | true | false |
| 59 | run | <code>sed -i 's/r.org_role_code/r.organization_role_code/g' sql/marts/workday__organization_overview.sql; python3 - &lt;&lt;'PY'<br>import duckdb,pathlib<br>c=duckdb.connect('/tmp/check2.duckdb')<br>try:c.execute('create </code> | 305 | false | false |
| 61 | run | <code>sed -i 's/ow.worker_id/ow.organization_worker_code/g' sql/marts/workday__organization_overview.sql; python3 - &lt;&lt;'PY'<br>import duckdb,pathlib<br>c=duckdb.connect('/tmp/check2.duckdb')<br>try:c.execute('create </code> | 7 | false | false |
| 63 | run | <code>python3 - &lt;&lt;'PY'<br>import duckdb,pathlib,yaml<br>c=duckdb.connect('/tmp/check2.duckdb')<br>for n in ['workday__employee_overview','workday__job_overview','workday__position_overview','workday__organization_ov</code> | 493 | true | false |
| 65 | run | <code>python3 run.py &gt; /tmp/run.log 2&gt;&amp;1; status=$?; tail -100 /tmp/run.log; exit $status</code> | 7105 | true | false |
| 69 | run | <code>python3 - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('workday.duckdb',read_only=True)<br>for t, col in [('stg_workday__worker','worker_history_id'),('stg_workday__organization','organization_id'),('stg_workda</code> | 330 | false | false |
| 71 | run | <code>python3 - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('workday.duckdb',read_only=True)<br>for t, col in [('stg_workday__worker','worker_history_id'),('stg_workday__organization','organization_id'),('stg_workda</code> | 173 | false | false |

### agent action 的 thought/message 命中原句

event 37 / message

```text
Running command: cat > sql/marts/workday__organization_overview.sql <<'SQL'
```
event 55 / message

```text
Running command: sed -i 's/), similar AS (/), similar_positions AS (/' sql/marts/workday__position_overview.sql; sed -i 's/LEFT JOIN similar s /LEFT JOIN similar_positions s /' sql/marts/workday__position_overview.sql; sed -i "s/count(DISTINCT r.role_id)/count(DISTINCT r.organization_role_id)/" sql/marts/workday__organization_overview.sql; sed -i "s/ow.role_id=r.organization_role_id/ow.role_id=r.organization_role_id/" sql/marts/workday__organization_overview.sql; python3 - <<'PY'
```
event 57 / message

```text
for n in ['workday__position_overview','workday__organization_overview']:
```
event 59 / message

```text
Running command: sed -i 's/r.org_role_code/r.organization_role_code/g' sql/marts/workday__organization_overview.sql; python3 - <<'PY'
```
event 59 / message

```text
try:c.execute('create or replace table mart.workday__organization_overview as ('+pathlib.Path('sql/marts/workday__organization_overview.sql').read_text()+')');print(c.execute('select count(*) from mart.workday__organization_overview').fetchone())
```
event 61 / message

```text
Running command: sed -i 's/ow.worker_id/ow.organization_worker_code/g' sql/marts/workday__organization_overview.sql; python3 - <<'PY'
```
event 61 / message

```text
try:c.execute('create or replace table mart.workday__organization_overview as ('+pathlib.Path('sql/marts/workday__organization_overview.sql').read_text()+')');print(c.execute('select count(*) from mart.workday__organization_overview').fetchone())
```
event 63 / message

```text
for n in ['workday__employee_overview','workday__job_overview','workday__position_overview','workday__organization_overview','workday__workforce_analytics','workday__organization_performance']:
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/011_table_alignment.jsonl`
- S2: `records/011_alignment_impl-016.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/sql/marts/workday__organization_overview.sql`
- S6: `records/006_contract_impl-016.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/result.md`
- S10: `records/012_packages/012_impl-016_marts_workday__organization_overview.json`
- S11: `data/011_agent_alignment/impl-016/workday__organization_overview_2025-10-13.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/workday.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions`
