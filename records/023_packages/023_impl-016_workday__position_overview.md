# impl-016 | marts | workday__position_overview | 差异：S1；日期 2025-10-13

## 契约完整原文

S3:2231–2477

```yaml
    - name: workday__position_overview
      description: Position-level overview with occupancy history, organizational context, compensation/job profile attributes, current-employee metrics, and derived scores/flags
      grain: One row per position_id and source_relation
      source_models:
      - staging.stg_workday__position
      - staging.stg_workday__worker_position
      - staging.stg_workday__position_organization
      - staging.stg_workday__organization
      - intermediate.int_workday__organization_metrics
      - staging.stg_workday__position_job_profile
      - staging.stg_workday__job_profile
      - mart.workday__employee_overview
      business_logic: '- Base: Start from positions. Compute position_age_days as the days from effective_start to today. Bucket position_age_category by age: <90 days "New Position (<3 months)"; <365 days "Recent Position (3-12 months)"; <2 years "Established Position (1-2 years)"; <5 years "Mature Position (2-5 years)"; otherwise "Legacy Position (5+ years)". - Utilization history: Join worker-position assignments by position and source. Count distinct workers ever assigned (total), with open end date (current), and with closed end date (former). Set position_occupancy_status to "Occupied" if current>0; else "Vacant (Previously Occupied)" if total>0; else "Vacant (Never Occupied)". Average tenure days uses assignment start-to-end when ended, or start-to-today when still open. Take the most recent assignment start as last_assignment_date and most recent end as last_departure_date. New assignments last year count distinct workers with assignment start within the past 12 months; departures last year count distinct workers with assignment end within the past 12 months. - Organizational context: Link positions to organizations and organization metrics. Also link to job profile. similar_positions_in_department is the count of positions sharing the same organization_id and job_profile_id across the dataset. - Compensation and job profile: Derive compensation_tier from the first number found in compensation_grade_id: missing or not numeric → "Ungraded"; ≤5 → "Entry Level"; ≤10 → "Mid Level"; ≤15 → "Senior Level"; >15 → "Executive Level". challenging_work_conditions_score is the sum of three indicators (shift required, union eligible, weekly hours>40), range 0–3. Map management_level to a numeric scale: Director 4, Senior Manager 3, Manager 2, Individual Contributor 1, otherwise 0. - Current employee metrics: From employee overview by position and source. Averages (overall performance, career development, retention stability) are computed only for currently employed workers. Risk counts (High/Medium/Low Risk) are distinct worker counts by risk level without restricting to current employment. Value segments (High Value - High Retention, High Value - Flight Risk) are distinct worker counts by segment. New and veteran counts include only currently employed workers with maturity containing "New Hire" or "Veteran". Average age and ethnic diversity use only currently employed workers; military_veterans_count counts currently employed workers with military service. - Final projection and defaults: If any numeric metric is missing, default to 0; booleans default to false; text dimensions default to "Unknown"; compensation grade/tier default to "Ungraded". last_assignment_date falls back to position_created_date when no assignments; last_departure_date remains null when none. - Rounding: avg_tenure_years_in_position is average tenure days divided by 365, rounded to two decimals. Average employee scores are rounded to two decimals. Average employee age is rounded to one decimal. position_turnover_rate and position_efficiency_score are rounded to two decimals. - Derived metrics: position_turnover_rate is 0 if total ever assigned is 0; otherwise departures in the last year divided by total ever assigned, expressed as a percentage. position_efficiency_score (0–100) is the sum of: 25 if occupied; a tenure bucket (25 if tenure≥2 years, 20 if ≥1 year, 15 if ≥180 days, else 10); up to 30 points from employee performance (performance score × 0.3, capped at 30); up to 20 points from department health (health score × 0.2, capped at 20); then rounded. - Categorization rules (first-match wins): position_performance_category: Vacant Position; High-Performance Stable Position (performance≥80 and tenure≥2 years); High-Performance Position (performance≥70); Stable Position (tenure≥2 years); High-Turnover Position (departures_last_year>1); else Standard Position. management_priority: Review Position Necessity (vacant and age>180 days); Focus on Retention (any high risk employees); Performance Improvement Needed (performance<50); Department Support Needed (department health<50); Maintain Excellence (performance≥80); else Standard Management. cost_performance_analysis: No Current Cost (vacant); High Cost - Low Performance (weekly hours>40 and performance<60); High Cost - High Performance (weekly hours>40 and performance≥80); Optimal Cost-Performance (weekly hours≤40 and performance≥80); else Standard Cost-Performance. strategic_recommendation: Consider Position Elimination (vacant and age>365 days); Consider Position Consolidation (similar positions>5); Develop Succession Plan (any flight risk employees); Consider Position Expansion (performance≥90); else Maintain Current Structure. - Data quality: Mark as ERROR when title is missing/blank, weekly hours≤0, or position_age_days<0; mark as WARNING when weekly hours>80 or current assignments>3; otherwise VALID. - Output ordering: Sort rows by current_workers_assigned descending, then average employee performance descending, then position_age_days descending. - Analysis timestamp: Set to the current timestamp at query execution (time zone aware).'
      columns:
      - name: position_id
        data_type: VARCHAR
        description: Unique position identifier; primary key with source_relation; exactly one output row per (position_id, source_relation)
        tests:
        - not_null
        - unique
      - name: source_relation
        data_type: VARCHAR
        description: Source system identifier associated with the position_id
        tests:
        - not_null
      - name: business_title
        data_type: VARCHAR
        description: Business title from position source; may be NULL/empty and is validated in data_quality_flag
      - name: employee_type
        data_type: VARCHAR
        description: Employee type as stored on the position record
      - name: default_weekly_hours
        data_type: BIGINT
        description: Default scheduled weekly hours from position; used in cost and work-conditions scoring; may be <=0 or >80 (flagged in data_quality_flag)
      - name: position_created_date
        data_type: DATE
        description: Position effective_start date from the source, treated as the created date
      - name: position_age_days
        data_type: BIGINT
        description: Days between effective_start and today; can be negative for future-dated positions
      - name: position_age_category
        data_type: VARCHAR
        description: 'Age bucket based on position_age_days: <90 New; <365 Recent; <730 Established; <1825 Mature; else Legacy'
      - name: total_workers_ever_assigned
        data_type: BIGINT
        description: Distinct worker count ever assigned to the position; defaults to 0 when no history
        tests:
        - total_workers_ever_assigned >= 0
      - name: current_workers_assigned
        data_type: BIGINT
        description: Distinct worker count with an open assignment (no end date); defaults to 0
        tests:
        - current_workers_assigned >= 0
      - name: former_workers_assigned
        data_type: BIGINT
        description: Distinct worker count with a closed assignment (has end date); defaults to 0
        tests:
        - former_workers_assigned >= 0
      - name: position_occupancy_status
        data_type: VARCHAR
        description: Occupied if current_workers_assigned>0; else Vacant (Previously Occupied) if total>0; else Vacant (Never Occupied); defaults to 'Unknown' if missing
      - name: avg_tenure_years_in_position
        data_type: DOUBLE
        description: Average tenure in years based on assignment days/365, rounded to 2 decimals; open assignments use today; defaults to 0.00
        tests:
        - avg_tenure_years_in_position >= 0
      - name: last_assignment_date
        data_type: DATE
        description: Most recent assignment start date; falls back to position_created_date when none
      - name: last_departure_date
        data_type: DATE
        description: Most recent assignment end date; NULL when none
      - name: new_assignments_last_year
        data_type: BIGINT
        description: Distinct worker count with assignment start within the past 12 months; defaults to 0
        tests:
        - new_assignments_last_year >= 0
      - name: departures_last_year
        data_type: BIGINT
        description: Distinct worker count with assignment end within the past 12 months; defaults to 0
        tests:
        - departures_last_year >= 0
      - name: position_turnover_rate
        data_type: DOUBLE
        description: If total_workers_ever_assigned=0 then 0; otherwise departures_last_year divided by total_workers_ever_assigned as a percentage, rounded to 2 decimals
        tests:
        - position_turnover_rate >= 0
      - name: organization_id
        data_type: VARCHAR
        description: Organization identifier for the position; defaults to 'Unknown' when absent
      - name: organization_name
        data_type: VARCHAR
        description: Organization name; defaults to 'Unknown' when absent
      - name: organization_type
        data_type: VARCHAR
        description: Organization type; defaults to 'Unknown' when absent
      - name: organization_sub_type
        data_type: VARCHAR
        description: Organization sub-type; defaults to 'Unknown' when absent
      - name: staffing_model
        data_type: VARCHAR
        description: Organization staffing model; defaults to 'Unknown' when absent
      - name: department_total_employees
        data_type: BIGINT
        description: Current employee count for the organization from org metrics; defaults to 0
        tests:
        - department_total_employees >= 0
      - name: department_health_score
        data_type: INTEGER
        description: Organization health score (0–100) from org metrics; defaults to 0
        tests:
        - department_health_score BETWEEN 0 AND 100
      - name: department_turnover_rate
        data_type: DOUBLE
        description: Annual turnover rate from org metrics; defaults to 0.0
        tests:
        - department_turnover_rate >= 0
      - name: department_performance_level
        data_type: VARCHAR
        description: Organization performance category from org metrics; defaults to 'Unknown'
      - name: department_size_category
        data_type: VARCHAR
        description: Organization size category from org metrics; defaults to 'Unknown'
      - name: similar_positions_in_department
        data_type: BIGINT
        description: Count of positions with the same organization_id and job_profile_id across the dataset; defaults to 0
        tests:
        - similar_positions_in_department >= 0
      - name: job_profile_id
        data_type: VARCHAR
        description: Job profile identifier linked to the position; defaults to 'Unknown'
      - name: job_profile_title
        data_type: VARCHAR
        description: Job profile title; defaults to 'Unknown'
      - name: management_level
        data_type: VARCHAR
        description: Management level from job profile; defaults to 'Unknown'
      - name: compensation_grade_id
        data_type: VARCHAR
        description: Compensation grade identifier from job profile; defaults to 'Ungraded'
      - name: compensation_tier
        data_type: VARCHAR
        description: 'Tier derived from compensation_grade_id digits: Entry ≤5; Mid ≤10; Senior ≤15; Executive >15; ''Ungraded'' when NULL or not numeric'
      - name: is_work_shift_required
        data_type: BOOLEAN
        description: True if work shift is required per job profile; defaults to false when NULL
      - name: is_union_eligible
        data_type: BOOLEAN
        description: True if union eligible per job profile; defaults to false when NULL
      - name: challenging_work_conditions_score
        data_type: INTEGER
        description: Sum of indicators (shift required, union eligible, weekly hours>40); range 0–3; defaults to 0
        tests:
        - challenging_work_conditions_score BETWEEN 0 AND 3
      - name: management_level_numeric
        data_type: INTEGER
        description: 'Numeric mapping of management_level: Director=4, Senior Manager=3, Manager=2, Individual Contributor=1, else 0'
        tests:
        - management_level_numeric >= 0
      - name: avg_employee_performance_score
        data_type: DOUBLE
        description: Average overall_employee_score for currently employed workers; rounded to 2 decimals; defaults to 0.00
        tests:
        - avg_employee_performance_score BETWEEN 0 AND 100
      - name: avg_career_development_score
        data_type: DOUBLE
        description: Average career_development_score for currently employed workers; rounded to 2 decimals; defaults to 0.00
        tests:
        - avg_career_development_score BETWEEN 0 AND 100
      - name: avg_retention_score
        data_type: DOUBLE
        description: Average retention_stability_score for currently employed workers; rounded to 2 decimals; defaults to 0.00
        tests:
        - avg_retention_score BETWEEN 0 AND 100
      - name: high_risk_employees_count
        data_type: BIGINT
        description: Distinct count of workers flagged 'High Risk' regardless of current employment; defaults to 0
        tests:
        - high_risk_employees_count >= 0
      - name: medium_risk_employees_count
        data_type: BIGINT
        description: Distinct count of workers flagged 'Medium Risk' regardless of current employment; defaults to 0
        tests:
        - medium_risk_employees_count >= 0
      - name: low_risk_employees_count
        data_type: BIGINT
        description: Distinct count of workers flagged 'Low Risk' regardless of current employment; defaults to 0
        tests:
        - low_risk_employees_count >= 0
      - name: high_value_employees_count
        data_type: BIGINT
        description: Distinct count of workers in 'High Value - High Retention' segment; defaults to 0
        tests:
        - high_value_employees_count >= 0
      - name: flight_risk_employees_count
        data_type: BIGINT
        description: Distinct count of workers in 'High Value - Flight Risk' segment; defaults to 0
        tests:
        - flight_risk_employees_count >= 0
      - name: new_employees_count
        data_type: BIGINT
        description: Distinct count of currently employed workers with maturity like '%New Hire%'; defaults to 0
        tests:
        - new_employees_count >= 0
      - name: veteran_employees_count
        data_type: BIGINT
        description: Distinct count of currently employed workers with maturity like '%Veteran%'; defaults to 0
        tests:
        - veteran_employees_count >= 0
      - name: avg_employee_age
        data_type: DOUBLE
        description: Average age of currently employed workers; rounded to 1 decimal; defaults to 0.0
        tests:
        - avg_employee_age >= 0
      - name: ethnic_diversity_count
        data_type: BIGINT
        description: Distinct count of ethnicity_codes among currently employed workers; defaults to 0
        tests:
        - ethnic_diversity_count >= 0
      - name: military_veterans_count
        data_type: BIGINT
        description: Distinct count of currently employed workers with military service; defaults to 0
        tests:
        - military_veterans_count >= 0
      - name: position_efficiency_score
        data_type: DOUBLE
        description: Composite score (0–100) of occupancy, tenure, employee performance, and department health; rounded to 2 decimals
        tests:
        - position_efficiency_score BETWEEN 0 AND 100
      - name: position_performance_category
        data_type: VARCHAR
        description: Position classification by vacancy, performance, tenure, and turnover using ordered rules; see business_logic for precedence
      - name: management_priority
        data_type: VARCHAR
        description: Recommended management focus based on vacancy, risk, performance, and department health; ordered rule evaluation
      - name: cost_performance_analysis
        data_type: VARCHAR
        description: Cost-performance label based on default_weekly_hours and current employee performance; ordered rule evaluation
      - name: strategic_recommendation
        data_type: VARCHAR
        description: Forward-looking recommendation using vacancy age, similar roles count, flight risk, and performance; ordered rule evaluation
      - name: data_quality_flag
        data_type: VARCHAR
        description: Row-level quality status based on title presence, hours sanity, over-assignment, and age consistency; ordered checks return first match
      - name: analysis_timestamp
        data_type: TIMESTAMP WITH TIME ZONE
        description: Query execution timestamp (time zone aware) for when the analysis was generated
```

## agent 最终 SQL

S4

```sql
WITH base AS (SELECT * FROM staging.stg_workday__position), history AS (
 SELECT position_id,source_relation,count(DISTINCT worker_id) total_workers_ever_assigned,count(DISTINCT worker_id) FILTER(WHERE effective_end IS NULL) current_workers_assigned,count(DISTINCT worker_id) FILTER(WHERE effective_end IS NOT NULL) former_workers_assigned,
 avg(date_diff('day',effective_start,coalesce(effective_end,current_date))) avg_tenure_days,max(effective_start) last_assignment_date,max(effective_end) last_departure_date,
 count(DISTINCT worker_id) FILTER(WHERE effective_start>=current_date-INTERVAL '1 year') new_assignments_last_year,count(DISTINCT worker_id) FILTER(WHERE effective_end>=current_date-INTERVAL '1 year') departures_last_year
 FROM staging.stg_workday__worker_position GROUP BY position_id,source_relation
), po AS (
 SELECT position_id,source_relation,organization_id,effective_end,row_number() over(partition by position_id,source_relation order by effective_start desc) rn FROM staging.stg_workday__position_organization
), profiles AS (
 SELECT pjp.position_id,pjp.source_relation,pjp.job_profile_id,jp.job_profile_title,jp.management_level,jp.compensation_grade_id,jp.is_work_shift_required,jp.is_union_eligible FROM staging.stg_workday__position_job_profile pjp LEFT JOIN staging.stg_workday__job_profile jp USING(job_profile_id,source_relation)
), orgs AS (
 SELECT organization_id,source_relation,organization_name,organization_type,organization_sub_type,staffing_model,current_employee_count,organization_health_score,annual_turnover_rate,performance_category,organization_size_category FROM intermediate.int_workday__organization_metrics
), similar_positions AS (
 SELECT po.organization_id,pr.job_profile_id,count(DISTINCT b.position_id) similar_positions_in_department FROM base b LEFT JOIN po ON b.position_id=po.position_id AND b.source_relation=po.source_relation AND po.rn=1 LEFT JOIN profiles pr ON b.position_id=pr.position_id AND b.source_relation=pr.source_relation GROUP BY po.organization_id,pr.job_profile_id
), emp AS (
 SELECT position_id,source_relation,avg(overall_employee_score) FILTER(WHERE is_employed) avg_employee_performance_score,avg(career_development_score) FILTER(WHERE is_employed) avg_career_development_score,avg(retention_stability_score) FILTER(WHERE is_employed) avg_retention_score,
 count(DISTINCT worker_id) FILTER(WHERE employee_risk_level='High Risk') high_risk_employees_count,count(DISTINCT worker_id) FILTER(WHERE employee_risk_level='Medium Risk') medium_risk_employees_count,count(DISTINCT worker_id) FILTER(WHERE employee_risk_level='Low Risk') low_risk_employees_count,count(DISTINCT worker_id) FILTER(WHERE employee_value_segment='High Value - High Retention') high_value_employees_count,count(DISTINCT worker_id) FILTER(WHERE employee_value_segment='High Value - Flight Risk') flight_risk_employees_count,
 count(DISTINCT worker_id) FILTER(WHERE is_employed AND employee_maturity_segment LIKE '%New Hire%') new_employees_count,count(DISTINCT worker_id) FILTER(WHERE is_employed AND employee_maturity_segment LIKE '%Veteran%') veteran_employees_count,avg(age) FILTER(WHERE is_employed) avg_employee_age,count(DISTINCT ethnicity_codes) FILTER(WHERE is_employed AND ethnicity_codes IS NOT NULL) ethnic_diversity_count,count(DISTINCT worker_id) FILTER(WHERE is_employed AND is_military_service) military_veterans_count
 FROM mart.workday__employee_overview GROUP BY position_id,source_relation
), joined AS (
 SELECT b.*,coalesce(h.total_workers_ever_assigned,0) total_workers_ever_assigned,coalesce(h.current_workers_assigned,0) current_workers_assigned,coalesce(h.former_workers_assigned,0) former_workers_assigned,coalesce(h.avg_tenure_days,0) avg_tenure_days,h.last_assignment_date,h.last_departure_date,coalesce(h.new_assignments_last_year,0) new_assignments_last_year,coalesce(h.departures_last_year,0) departures_last_year,
 coalesce(po.organization_id,'Unknown') organization_id,coalesce(o.organization_name,'Unknown') organization_name,coalesce(o.organization_type,'Unknown') organization_type,coalesce(o.organization_sub_type,'Unknown') organization_sub_type,coalesce(o.staffing_model,'Unknown') staffing_model,coalesce(o.current_employee_count,0) department_total_employees,coalesce(o.organization_health_score,0) department_health_score,coalesce(o.annual_turnover_rate,0) department_turnover_rate,coalesce(o.performance_category,'Unknown') department_performance_level,coalesce(o.organization_size_category,'Unknown') department_size_category,
 coalesce(pr.job_profile_id,'Unknown') job_profile_id,coalesce(pr.job_profile_title,'Unknown') job_profile_title,coalesce(pr.management_level,'Unknown') management_level,coalesce(pr.compensation_grade_id,'Ungraded') compensation_grade_id,coalesce(pr.is_work_shift_required,FALSE) is_work_shift_required,coalesce(pr.is_union_eligible,FALSE) is_union_eligible,
 coalesce(s.similar_positions_in_department,0) similar_positions_in_department,coalesce(e.avg_employee_performance_score,0) avg_employee_performance_score,coalesce(e.avg_career_development_score,0) avg_career_development_score,coalesce(e.avg_retention_score,0) avg_retention_score,coalesce(e.high_risk_employees_count,0) high_risk_employees_count,coalesce(e.medium_risk_employees_count,0) medium_risk_employees_count,coalesce(e.low_risk_employees_count,0) low_risk_employees_count,coalesce(e.high_value_employees_count,0) high_value_employees_count,coalesce(e.flight_risk_employees_count,0) flight_risk_employees_count,coalesce(e.new_employees_count,0) new_employees_count,coalesce(e.veteran_employees_count,0) veteran_employees_count,coalesce(e.avg_employee_age,0) avg_employee_age,coalesce(e.ethnic_diversity_count,0) ethnic_diversity_count,coalesce(e.military_veterans_count,0) military_veterans_count
 FROM base b LEFT JOIN history h USING(position_id,source_relation) LEFT JOIN po ON b.position_id=po.position_id AND b.source_relation=po.source_relation AND po.rn=1 LEFT JOIN orgs o ON po.organization_id=o.organization_id AND po.source_relation=o.source_relation LEFT JOIN profiles pr USING(position_id,source_relation) LEFT JOIN similar_positions s ON po.organization_id=s.organization_id AND pr.job_profile_id=s.job_profile_id LEFT JOIN emp e USING(position_id,source_relation)
), final AS (
 SELECT *,date_diff('day',effective_start,current_date)::BIGINT position_age_days,coalesce(last_assignment_date,effective_start) last_assignment_date_out,
 CASE WHEN regexp_extract(compensation_grade_id,'([0-9]+)',1)='' THEN 'Ungraded' WHEN try_cast(regexp_extract(compensation_grade_id,'([0-9]+)',1) AS INTEGER)<=5 THEN 'Entry Level' WHEN try_cast(regexp_extract(compensation_grade_id,'([0-9]+)',1) AS INTEGER)<=10 THEN 'Mid Level' WHEN try_cast(regexp_extract(compensation_grade_id,'([0-9]+)',1) AS INTEGER)<=15 THEN 'Senior Level' ELSE 'Executive Level' END compensation_tier
 FROM joined
)
SELECT position_id,source_relation,business_title,employee_type,default_weekly_hours,effective_start position_created_date,position_age_days,
CASE WHEN position_age_days<90 THEN 'New Position (<3 months)' WHEN position_age_days<365 THEN 'Recent Position (3-12 months)' WHEN position_age_days<730 THEN 'Established Position (1-2 years)' WHEN position_age_days<1825 THEN 'Mature Position (2-5 years)' ELSE 'Legacy Position (5+ years)' END position_age_category,
total_workers_ever_assigned,current_workers_assigned,former_workers_assigned,CASE WHEN current_workers_assigned>0 THEN 'Occupied' WHEN total_workers_ever_assigned>0 THEN 'Vacant (Previously Occupied)' ELSE 'Vacant (Never Occupied)' END position_occupancy_status,round(avg_tenure_days/365.0,2)::DOUBLE avg_tenure_years_in_position,last_assignment_date_out last_assignment_date,last_departure_date,new_assignments_last_year,departures_last_year,CASE WHEN total_workers_ever_assigned=0 THEN 0 ELSE round(departures_last_year*100.0/total_workers_ever_assigned,2) END::DOUBLE position_turnover_rate,
organization_id,organization_name,organization_type,organization_sub_type,staffing_model,department_total_employees,department_health_score,department_turnover_rate,department_performance_level,department_size_category,similar_positions_in_department,job_profile_id,job_profile_title,management_level,compensation_grade_id,compensation_tier,is_work_shift_required,is_union_eligible,
(CASE WHEN is_work_shift_required THEN 1 ELSE 0 END+CASE WHEN is_union_eligible THEN 1 ELSE 0 END+CASE WHEN default_weekly_hours>40 THEN 1 ELSE 0 END)::INTEGER challenging_work_conditions_score,
CASE management_level WHEN 'Director' THEN 4 WHEN 'Senior Manager' THEN 3 WHEN 'Manager' THEN 2 WHEN 'Individual Contributor' THEN 1 ELSE 0 END::INTEGER management_level_numeric,round(avg_employee_performance_score,2)::DOUBLE avg_employee_performance_score,round(avg_career_development_score,2)::DOUBLE avg_career_development_score,round(avg_retention_score,2)::DOUBLE avg_retention_score,
high_risk_employees_count,medium_risk_employees_count,low_risk_employees_count,high_value_employees_count,flight_risk_employees_count,new_employees_count,veteran_employees_count,round(avg_employee_age,1)::DOUBLE avg_employee_age,ethnic_diversity_count,military_veterans_count,
round((CASE WHEN current_workers_assigned>0 THEN 25 ELSE 0 END+CASE WHEN avg_tenure_days>=730 THEN 25 WHEN avg_tenure_days>=365 THEN 20 WHEN avg_tenure_days>=180 THEN 15 ELSE 10 END+least(30,avg_employee_performance_score*.3)+least(20,department_health_score*.2)),2)::DOUBLE position_efficiency_score,
CASE WHEN current_workers_assigned=0 THEN 'Vacant Position' WHEN avg_employee_performance_score>=80 AND avg_tenure_days>=730 THEN 'High-Performance Stable Position' WHEN avg_employee_performance_score>=70 THEN 'High-Performance Position' WHEN avg_tenure_days>=730 THEN 'Stable Position' WHEN departures_last_year>1 THEN 'High-Turnover Position' ELSE 'Standard Position' END position_performance_category,
CASE WHEN current_workers_assigned=0 AND position_age_days>180 THEN 'Review Position Necessity' WHEN high_risk_employees_count>0 THEN 'Focus on Retention' WHEN avg_employee_performance_score<50 THEN 'Performance Improvement Needed' WHEN department_health_score<50 THEN 'Department Support Needed' WHEN avg_employee_performance_score>=80 THEN 'Maintain Excellence' ELSE 'Standard Management' END management_priority,
CASE WHEN current_workers_assigned=0 THEN 'No Current Cost' WHEN default_weekly_hours>40 AND avg_employee_performance_score<60 THEN 'High Cost - Low Performance' WHEN default_weekly_hours>40 AND avg_employee_performance_score>=80 THEN 'High Cost - High Performance' WHEN default_weekly_hours<=40 AND avg_employee_performance_score>=80 THEN 'Optimal Cost-Performance' ELSE 'Standard Cost-Performance' END cost_performance_analysis,
CASE WHEN current_workers_assigned=0 AND position_age_days>365 THEN 'Consider Position Elimination' WHEN similar_positions_in_department>5 THEN 'Consider Position Consolidation' WHEN flight_risk_employees_count>0 THEN 'Develop Succession Plan' WHEN avg_employee_performance_score>=90 THEN 'Consider Position Expansion' ELSE 'Maintain Current Structure' END strategic_recommendation,
CASE WHEN business_title IS NULL OR trim(business_title)='' THEN 'ERROR: Missing title' WHEN default_weekly_hours<=0 THEN 'ERROR: Invalid weekly hours' WHEN position_age_days<0 THEN 'ERROR: Future position date' WHEN default_weekly_hours>80 OR current_workers_assigned>3 THEN 'WARNING: Position anomaly' ELSE 'VALID' END data_quality_flag,current_timestamp::TIMESTAMPTZ analysis_timestamp
FROM final
```

## gold SQL（仅供定位差异）

S5

```sql
-- Position configuration and efficiency analysis data mart - Provides position utilization, efficiency, and cost analysis
-- Support human resource allocation optimization and organizational structure design decisions

with position_base_info as (
    select 
        p.*,
        -- Position age calculation
        date_diff('day', p.effective_start, current_date) as position_age_days,
        case 
            when date_diff('day', p.effective_start, current_date) < 90 then 'New Position (<3 months)'
            when date_diff('day', p.effective_start, current_date) < 365 then 'Recent Position (3-12 months)'
            when date_diff('day', p.effective_start, current_date) < 365*2 then 'Established Position (1-2 years)'
            when date_diff('day', p.effective_start, current_date) < 365*5 then 'Mature Position (2-5 years)'
            else 'Legacy Position (5+ years)'
        end as position_age_category
    from staging.stg_workday__position p
),

-- Job history and usage
position_utilization_history as (
    select 
        p.position_id,
        p.source_relation,
        
        -- Historical resume statistics
        count(distinct wph.worker_id) as total_workers_ever_assigned,
        count(distinct case when wph.effective_end is null then wph.worker_id end) as current_workers_assigned,
        count(distinct case when wph.effective_end is not null then wph.worker_id end) as former_workers_assigned,
        
        -- Position utilization calculation
        case 
            when count(distinct case when wph.effective_end is null then wph.worker_id end) > 0 then 'Occupied'
            when count(distinct wph.worker_id) > 0 then 'Vacant (Previously Occupied)'
            else 'Vacant (Never Occupied)'
        end as position_occupancy_status,
        
        -- Average tenure
        avg(case when wph.effective_end is not null 
            then date_diff('day', wph.effective_start, wph.effective_end)
            else date_diff('day', wph.effective_start, current_date)
        end) as avg_tenure_days_in_position,
        
        -- last change
        max(wph.effective_start) as last_assignment_date,
        max(wph.effective_end) as last_departure_date,
        
        -- liquidity indicator
        count(distinct case when wph.effective_start >= current_date - interval '1 year' then wph.worker_id end) as new_assignments_last_year,
        count(distinct case when wph.effective_end >= current_date - interval '1 year' and wph.effective_end is not null then wph.worker_id end) as departures_last_year
        
    from staging.stg_workday__position p
    left join staging.stg_workday__worker_position wph
        on p.position_id = wph.position_id
        and p.source_relation = wph.source_relation
    group by p.position_id, p.source_relation
),

-- Position organizational relationships and geographical distribution
position_organizational_context as (
    select 
        p.position_id,
        p.source_relation,
        
        -- organize information
        o.organization_id,
        o.organization_name,
        o.organization_type,
        o.organization_sub_type,
        o.staffing_model,
        
        -- organizational performance indicators
        om.current_employee_count as dept_total_employees,
        om.organization_health_score as dept_health_score,
        om.annual_turnover_rate as dept_turnover_rate,
        om.performance_category as dept_performance_level,
        om.organization_size_category as dept_size_category,
        
        -- Number of similar positions in the organization
        count(*) over (partition by o.organization_id, jp.job_profile_id) as similar_positions_in_dept
        
    from staging.stg_workday__position p
    left join staging.stg_workday__position_organization po
        on p.position_id = po.position_id
        and p.source_relation = po.source_relation
    left join staging.stg_workday__organization o
        on po.organization_id = o.organization_id
        and po.source_relation = o.source_relation
    left join intermediate.int_workday__organization_metrics om
        on o.organization_id = om.organization_id
        and o.source_relation = om.source_relation
    left join staging.stg_workday__position_job_profile pjp
        on p.position_id = pjp.position_id
        and p.source_relation = pjp.source_relation
    left join staging.stg_workday__job_profile jp
        on pjp.job_profile_id = jp.job_profile_id
        and pjp.source_relation = jp.source_relation
),

-- Job Compensation and Benefits Information
position_compensation_benefits as (
    select 
        p.position_id,
        p.source_relation,
        
        -- Position information
        jp.job_profile_id,
        jp.job_profile_title,
        jp.management_level,
        jp.compensation_grade_id,
        jp.is_work_shift_required,
        jp.is_union_eligible,
        
        -- Pay grade analysis
        case 
            when jp.compensation_grade_id is null then 'Ungraded'
            when try_cast(regexp_extract(jp.compensation_grade_id, '\\d+', 0) as int) <= 5 then 'Entry Level'
            when try_cast(regexp_extract(jp.compensation_grade_id, '\\d+', 0) as int) <= 10 then 'Mid Level'
            when try_cast(regexp_extract(jp.compensation_grade_id, '\\d+', 0) as int) <= 15 then 'Senior Level'
            when try_cast(regexp_extract(jp.compensation_grade_id, '\\d+', 0) as int) > 15 then 'Executive Level'
            else 'Ungraded'
        end as compensation_tier,
        
        -- working conditions rating
        (case when jp.is_work_shift_required then 1 else 0 end +
         case when jp.is_union_eligible then 1 else 0 end +
         case when p.default_weekly_hours > 40 then 1 else 0 end) as challenging_work_conditions_score,
        
        -- Digitizing management levels
        case 
            when jp.management_level = 'Director' then 4
            when jp.management_level = 'Senior Manager' then 3
            when jp.management_level = 'Manager' then 2
            when jp.management_level = 'Individual Contributor' then 1
            else 0
        end as management_level_numeric
        
    from staging.stg_workday__position p
    left join staging.stg_workday__position_job_profile pjp
        on p.position_id = pjp.position_id
        and p.source_relation = pjp.source_relation
    left join staging.stg_workday__job_profile jp
        on pjp.job_profile_id = jp.job_profile_id
        and pjp.source_relation = jp.source_relation
),

-- Performance data of current employees
current_employee_performance as (
    select 
        p.position_id,
        p.source_relation,
        
        -- Current employee performance indicators
        avg(case when eo.is_employed then eo.overall_employee_score end) as avg_employee_performance_score,
        avg(case when eo.is_employed then eo.career_development_score end) as avg_career_development_score,
        avg(case when eo.is_employed then eo.retention_stability_score end) as avg_retention_score,
        
        -- Employee risk distribution
        count(distinct case when eo.employee_risk_level = 'High Risk' then eo.worker_id end) as high_risk_employees_count,
        count(distinct case when eo.employee_risk_level = 'Medium Risk' then eo.worker_id end) as medium_risk_employees_count,
        count(distinct case when eo.employee_risk_level = 'Low Risk' then eo.worker_id end) as low_risk_employees_count,
        
        -- employee value segments
        count(distinct case when eo.employee_value_segment = 'High Value - High Retention' then eo.worker_id end) as high_value_employees_count,
        count(distinct case when eo.employee_value_segment = 'High Value - Flight Risk' then eo.worker_id end) as flight_risk_employees_count,
        
        -- Employee maturity distribution
        count(distinct case when eo.employee_maturity_segment like '%New Hire%' and eo.is_employed then eo.worker_id end) as new_employees_count,
        count(distinct case when eo.employee_maturity_segment like '%Veteran%' and eo.is_employed then eo.worker_id end) as veteran_employees_count,
        
        -- age and diversity
        avg(case when eo.is_employed then eo.age end) as avg_employee_age,
        count(distinct case when eo.is_employed then eo.ethnicity_codes end) as ethnic_diversity_count,
        count(distinct case when eo.is_employed and eo.is_military_service then eo.worker_id end) as military_veterans_count
        
    from staging.stg_workday__position p
    left join mart.workday__employee_overview eo
        on p.position_id = eo.position_id
        and p.source_relation = eo.source_relation
    group by p.position_id, p.source_relation
)

select 
    pbi.position_id,
    pbi.source_relation,
    pbi.business_title,
    pbi.employee_type,
    pbi.default_weekly_hours,
    pbi.effective_start as position_created_date,
    pbi.position_age_days,
    pbi.position_age_category,
    
    -- Utilization and occupancy
    coalesce(puh.total_workers_ever_assigned, 0) as total_workers_ever_assigned,
    coalesce(puh.current_workers_assigned, 0) as current_workers_assigned,
    coalesce(puh.former_workers_assigned, 0) as former_workers_assigned,
    coalesce(puh.position_occupancy_status, 'Unknown') as position_occupancy_status,
    
    -- efficiency index
    round(coalesce(puh.avg_tenure_days_in_position, 0) / 365.0, 2) as avg_tenure_years_in_position,
    coalesce(puh.last_assignment_date, pbi.effective_start) as last_assignment_date,
    coalesce(puh.last_departure_date, null) as last_departure_date,
    coalesce(puh.new_assignments_last_year, 0) as new_assignments_last_year,
    coalesce(puh.departures_last_year, 0) as departures_last_year,
    
    -- liquidity indicator
    case 
        when coalesce(puh.total_workers_ever_assigned, 0) = 0 then 0
        else round(coalesce(puh.departures_last_year, 0) * 100.0 / puh.total_workers_ever_assigned, 2)
    end as position_turnover_rate,
    
    -- organizational context
    coalesce(poc.organization_id, 'Unknown') as organization_id,
    coalesce(poc.organization_name, 'Unknown') as organization_name,
    coalesce(poc.organization_type, 'Unknown') as organization_type,
    coalesce(poc.organization_sub_type, 'Unknown') as organization_sub_type,
    coalesce(poc.staffing_model, 'Unknown') as staffing_model,
    coalesce(poc.dept_total_employees, 0) as department_total_employees,
    coalesce(poc.dept_health_score, 0) as department_health_score,
    coalesce(poc.dept_turnover_rate, 0) as department_turnover_rate,
    coalesce(poc.dept_performance_level, 'Unknown') as department_performance_level,
    coalesce(poc.dept_size_category, 'Unknown') as department_size_category,
    coalesce(poc.similar_positions_in_dept, 0) as similar_positions_in_department,
    
    -- Salary and position information
    coalesce(pcb.job_profile_id, 'Unknown') as job_profile_id,
    coalesce(pcb.job_profile_title, 'Unknown') as job_profile_title,
    coalesce(pcb.management_level, 'Unknown') as management_level,
    coalesce(pcb.compensation_grade_id, 'Ungraded') as compensation_grade_id,
    coalesce(pcb.compensation_tier, 'Ungraded') as compensation_tier,
    coalesce(pcb.is_work_shift_required, false) as is_work_shift_required,
    coalesce(pcb.is_union_eligible, false) as is_union_eligible,
    coalesce(pcb.challenging_work_conditions_score, 0) as challenging_work_conditions_score,
    coalesce(pcb.management_level_numeric, 0) as management_level_numeric,
    
    -- Current employee performance
    round(coalesce(cep.avg_employee_performance_score, 0), 2) as avg_employee_performance_score,
    round(coalesce(cep.avg_career_development_score, 0), 2) as avg_career_development_score,
    round(coalesce(cep.avg_retention_score, 0), 2) as avg_retention_score,
    
    -- risk distribution
    coalesce(cep.high_risk_employees_count, 0) as high_risk_employees_count,
    coalesce(cep.medium_risk_employees_count, 0) as medium_risk_employees_count,
    coalesce(cep.low_risk_employees_count, 0) as low_risk_employees_count,
    
    -- value segment
    coalesce(cep.high_value_employees_count, 0) as high_value_employees_count,
    coalesce(cep.flight_risk_employees_count, 0) as flight_risk_employees_count,
    
    -- Staff composition
    coalesce(cep.new_employees_count, 0) as new_employees_count,
    coalesce(cep.veteran_employees_count, 0) as veteran_employees_count,
    round(coalesce(cep.avg_employee_age, 0), 1) as avg_employee_age,
    coalesce(cep.ethnic_diversity_count, 0) as ethnic_diversity_count,
    coalesce(cep.military_veterans_count, 0) as military_veterans_count,
    
    -- Job effectiveness rating (0-100)
    round(
        (-- Occupancy (25%)
         case when coalesce(puh.current_workers_assigned, 0) > 0 then 25 else 0 end +
         -- Retention stability (25%)
         case when coalesce(puh.avg_tenure_days_in_position, 0) >= 365*2 then 25
              when coalesce(puh.avg_tenure_days_in_position, 0) >= 365 then 20
              when coalesce(puh.avg_tenure_days_in_position, 0) >= 180 then 15
              else 10 end +
         -- Employee performance (30%)
         least(30, coalesce(cep.avg_employee_performance_score, 0) * 0.3) +
         -- Department Health (20%)
         least(20, coalesce(poc.dept_health_score, 0) * 0.2))
    , 2) as position_efficiency_score,
    
    -- Job type classification
    case 
        when coalesce(puh.current_workers_assigned, 0) = 0 then 'Vacant Position'
        when coalesce(cep.avg_employee_performance_score, 0) >= 80 and coalesce(puh.avg_tenure_days_in_position, 0) >= 365*2 then 'High-Performance Stable Position'
        when coalesce(cep.avg_employee_performance_score, 0) >= 70 then 'High-Performance Position'
        when coalesce(puh.avg_tenure_days_in_position, 0) >= 365*2 then 'Stable Position'
        when coalesce(puh.departures_last_year, 0) > 1 then 'High-Turnover Position'
        else 'Standard Position'
    end as position_performance_category,
    
    -- investment priorities
    case 
        when coalesce(puh.current_workers_assigned, 0) = 0 and pbi.position_age_days > 180 then 'Review Position Necessity'
        when coalesce(cep.high_risk_employees_count, 0) > 0 then 'Focus on Retention'
        when coalesce(cep.avg_employee_performance_score, 0) < 50 then 'Performance Improvement Needed'
        when coalesce(poc.dept_health_score, 0) < 50 then 'Department Support Needed'
        when coalesce(cep.avg_employee_performance_score, 0) >= 80 then 'Maintain Excellence'
        else 'Standard Management'
    end as management_priority,
    
    -- cost benefit analysis
    case 
        when coalesce(puh.current_workers_assigned, 0) = 0 then 'No Current Cost'
        when pbi.default_weekly_hours > 40 and coalesce(cep.avg_employee_performance_score, 0) < 60 then 'High Cost - Low Performance'
        when pbi.default_weekly_hours > 40 and coalesce(cep.avg_employee_performance_score, 0) >= 80 then 'High Cost - High Performance'
        when pbi.default_weekly_hours <= 40 and coalesce(cep.avg_employee_performance_score, 0) >= 80 then 'Optimal Cost-Performance'
        else 'Standard Cost-Performance'
    end as cost_performance_analysis,
    
    -- Suggestions for future planning
    case 
        when coalesce(puh.current_workers_assigned, 0) = 0 and pbi.position_age_days > 365 then 'Consider Position Elimination'
        when coalesce(poc.similar_positions_in_dept, 0) > 5 then 'Consider Position Consolidation'
        when coalesce(cep.flight_risk_employees_count, 0) > 0 then 'Develop Succession Plan'
        when coalesce(cep.avg_employee_performance_score, 0) >= 90 then 'Consider Position Expansion'
        else 'Maintain Current Structure'
    end as strategic_recommendation,
    
    -- Data quality check
    case 
        when pbi.business_title is null or pbi.business_title = '' then 'ERROR: Missing position title'
        when pbi.default_weekly_hours <= 0 then 'ERROR: Invalid working hours'
        when pbi.default_weekly_hours > 80 then 'WARNING: Excessive working hours'
        when coalesce(puh.current_workers_assigned, 0) > 3 then 'WARNING: Position may be over-assigned'
        when pbi.position_age_days < 0 then 'ERROR: Invalid position creation date'
        else 'VALID'
    end as data_quality_flag,
    
    -- Analysis timestamp
    current_timestamp as analysis_timestamp
    
from position_base_info pbi
left join position_utilization_history puh
    on pbi.position_id = puh.position_id
    and pbi.source_relation = puh.source_relation
left join position_organizational_context poc
    on pbi.position_id = poc.position_id
    and pbi.source_relation = poc.source_relation
left join position_compensation_benefits pcb
    on pbi.position_id = pcb.position_id
    and pbi.source_relation = pcb.source_relation
left join current_employee_performance cep
    on pbi.position_id = cep.position_id
    and pbi.source_relation = cep.source_relation
order by 
    coalesce(puh.current_workers_assigned, 0) desc,
    coalesce(cep.avg_employee_performance_score, 0) desc,
    pbi.position_age_days desc
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 4000 | 4000 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"position_id":"pos00000001"}</code> |
| K2 | <code>{"position_id":"pos00000464"}</code> |
| K3 | <code>{"position_id":"pos00000004"}</code> |
| K4 | <code>{"position_id":"pos00000620"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| position_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| avg_career_development_score | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_employee_age | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_employee_performance_score | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_retention_score | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_tenure_years_in_position | 0 | 0 | 0 | DOUBLE | DOUBLE |
| business_title | 0 | 0 | 0 | VARCHAR | VARCHAR |
| challenging_work_conditions_score | 0 | 0 | 0 | INTEGER | INTEGER |
| compensation_grade_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| compensation_tier | 4000 | 4000 | 4000 | VARCHAR | VARCHAR |
| cost_performance_analysis | 0 | 0 | 0 | VARCHAR | VARCHAR |
| current_workers_assigned | 0 | 0 | 0 | BIGINT | BIGINT |
| data_quality_flag | 0 | 0 | 0 | VARCHAR | VARCHAR |
| default_weekly_hours | 0 | 0 | 0 | BIGINT | BIGINT |
| department_health_score | 0 | 0 | 0 | INTEGER | INTEGER |
| department_performance_level | 0 | 0 | 0 | VARCHAR | VARCHAR |
| department_size_category | 0 | 0 | 0 | VARCHAR | VARCHAR |
| department_total_employees | 0 | 0 | 0 | BIGINT | BIGINT |
| department_turnover_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| departures_last_year | 0 | 0 | 0 | BIGINT | BIGINT |
| employee_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| ethnic_diversity_count | 0 | 0 | 0 | BIGINT | BIGINT |
| flight_risk_employees_count | 0 | 0 | 0 | BIGINT | BIGINT |
| former_workers_assigned | 0 | 0 | 0 | BIGINT | BIGINT |
| high_risk_employees_count | 0 | 0 | 0 | BIGINT | BIGINT |
| high_value_employees_count | 0 | 0 | 0 | BIGINT | BIGINT |
| is_union_eligible | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| is_work_shift_required | 0 | 0 | 0 | BOOLEAN | BOOLEAN |
| job_profile_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| job_profile_title | 0 | 0 | 0 | VARCHAR | VARCHAR |
| last_assignment_date | 0 | 0 | 0 | DATE | DATE |
| last_departure_date | 0 | 0 | 0 | DATE | DATE |
| low_risk_employees_count | 0 | 0 | 0 | BIGINT | BIGINT |
| management_level | 0 | 0 | 0 | VARCHAR | VARCHAR |
| management_level_numeric | 0 | 0 | 0 | INTEGER | INTEGER |
| management_priority | 0 | 0 | 0 | VARCHAR | VARCHAR |
| medium_risk_employees_count | 0 | 0 | 0 | BIGINT | BIGINT |
| military_veterans_count | 0 | 0 | 0 | BIGINT | BIGINT |
| new_assignments_last_year | 0 | 0 | 0 | BIGINT | BIGINT |
| new_employees_count | 0 | 0 | 0 | BIGINT | BIGINT |
| organization_id | 30 | 30 | 30 | VARCHAR | VARCHAR |
| organization_name | 1946 | 1946 | 1946 | VARCHAR | VARCHAR |
| organization_sub_type | 1946 | 1946 | 1946 | VARCHAR | VARCHAR |
| organization_type | 1946 | 1946 | 1946 | VARCHAR | VARCHAR |
| position_age_category | 0 | 0 | 0 | VARCHAR | VARCHAR |
| position_age_days | 0 | 0 | 0 | BIGINT | BIGINT |
| position_created_date | 0 | 0 | 0 | DATE | DATE |
| position_efficiency_score | 0 | 0 | 0 | DOUBLE | DOUBLE |
| position_occupancy_status | 0 | 0 | 0 | VARCHAR | VARCHAR |
| position_performance_category | 0 | 0 | 0 | VARCHAR | VARCHAR |
| position_turnover_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| similar_positions_in_department | 2 | 2 | 2 | BIGINT | BIGINT |
| staffing_model | 1946 | 1946 | 1946 | VARCHAR | VARCHAR |
| strategic_recommendation | 0 | 0 | 0 | VARCHAR | VARCHAR |
| total_workers_ever_assigned | 0 | 0 | 0 | BIGINT | BIGINT |
| veteran_employees_count | 0 | 0 | 0 | BIGINT | BIGINT |

compensation_tier 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | Executive Level | Ungraded |

organization_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | ORG00000002 | Unknown |

organization_name 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K3 | Unknown | Org 18 |

organization_sub_type 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K3 | Unknown | Business_Unit |

organization_type 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K3 | Unknown | Company |

similar_positions_in_department 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K4 | 1 | 2 |

staffing_model 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K3 | Unknown | Job_Management |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>27列；[{"column":"source_relation","value":"workday"}]</code> |
| A4_equal_columns | <code>3组；[{"columns":["total_workers_ever_assigned","former_workers_assigned"],"nonnull_equal_rows":4000,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>3组；[{"columns":["total_workers_ever_assigned","former_workers_assigned"],"nonnull_equal_rows":4000,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| B7_specified_not_read | <code>["staging.stg_workday__organization"]</code> |
| C9_agent_runtime_text | <code>S4:3 current_date；命中数=5</code> |
| C9_gold_runtime_text | <code>S5:8 current_date；命中数=9</code> |
| C9_contract_runtime_text | <code>S3:2243 today；命中数=5</code> |

## 轨迹索引（不放输出原文）

本题事件总数：85；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; find sql -type f -maxdepth 3 -print</code> | 3401 | true | false |
| 17 | run | <code>python3 - &lt;&lt;'PY'<br>import yaml<br>x=yaml.safe_load(open('docs/data_contract.yaml'))<br>print(x.keys(),len(x['staging_contract']['tables']))<br>print([m['name'] for m in x['modeling_spec']['intermediate_models']]</code> | 3942 | true | false |
| 23 | run | <code>cat &gt; sql/intermediate/int_workday__worker_details.sql &lt;&lt;'SQL'<br>SELECT<br>    worker_id,<br>    source_relation,<br>    worker_history_id,<br>    event_type,<br>    effective_start AS hire_date,<br>    effective_end AS </code> | 0 | false | false |
| 25 | run | <code>cat &gt; sql/intermediate/int_workday__organization_metrics.sql &lt;&lt;'SQL'<br>WITH active_org AS (<br>    SELECT * FROM staging.stg_workday__organization WHERE is_inactive = FALSE<br>), assignments AS (<br>    SELECT w</code> | 0 | false | false |
| 27 | run | <code>cat &gt; sql/intermediate/int_workday__career_progression.sql &lt;&lt;'SQL'<br>WITH timeline AS (<br> SELECT wp.worker_id,wp.source_relation,wp.position_id,wp.effective_start,wp.effective_end,<br> row_number() over(par</code> | 0 | false | false |
| 29 | run | <code>python3 - &lt;&lt;'PY'<br>import yaml<br>x=yaml.safe_load(open('docs/data_contract.yaml'))<br>for m in x['modeling_spec']['marts_models']:<br> print('\n',m['name'],len(m['columns']))<br> print(', '.join(c['name'] for c in</code> | 8785 | true | false |
| 31 | run | <code>cat &gt; sql/marts/workday__employee_overview.sql &lt;&lt;'SQL'<br>WITH base AS (<br> SELECT e.*, md5(coalesce(cast(worker_id as varchar),'_dbt_utils_surrogate_key_null_')&#124;&#124;'-'&#124;&#124;coalesce(source_relation,'_dbt_utils_</code> | 0 | false | false |
| 33 | run | <code>cat &gt; sql/marts/workday__workforce_analytics.sql &lt;&lt;'SQL'<br>WITH base AS (SELECT * FROM mart.workday__employee_overview), metrics AS (<br> SELECT 'workday'::VARCHAR source_relation,current_date::DATE analys</code> | 0 | false | false |
| 35 | run | <code>cat &gt; sql/marts/workday__organization_performance.sql &lt;&lt;'SQL'<br>WITH org AS (SELECT * FROM intermediate.int_workday__organization_metrics), emp AS (<br> SELECT organization_id,source_relation,<br> count(DISTI</code> | 0 | false | false |
| 37 | run | <code>cat &gt; sql/marts/workday__organization_overview.sql &lt;&lt;'SQL'<br>WITH active_org AS (SELECT * FROM staging.stg_workday__organization WHERE is_inactive=FALSE), rel AS (<br> SELECT worker_id,organization_id,sour</code> | 0 | false | false |
| 39 | run | <code>python3 - &lt;&lt;'PY'<br>from run import WorkdayDataPipeline<br>p=WorkdayDataPipeline(target_db_path='/tmp/check.duckdb'); print(p.run_pipeline(['staging','intermediate']))<br>PY</code> | 10126 | false | false |
| 41 | run | <code>nl -ba sql/intermediate/int_workday__organization_metrics.sql &#124; sed -n '58,72p'; grep 'FROM raw' sql/staging/stg_workday__worker_position.sql</code> | 3360 | false | false |
| 43 | run | <code>sed -i 's/FROM raw.worker_position AS r/FROM raw.worker_position_history AS r/' sql/staging/stg_workday__worker_position.sql; sed -i 's/FROM raw.worker_position_organization AS r/FROM raw.worker_posit</code> | 1110 | false | false |
| 45 | run | <code>sed -n '64,65p' sql/intermediate/int_workday__organization_metrics.sql</code> | 1544 | false | false |
| 47 | run | <code>python3 - &lt;&lt;'PY'<br>import duckdb, pathlib<br>c=duckdb.connect('/tmp/check.duckdb')<br>for n in ['stg_workday__worker_position','stg_workday__worker_position_organization']:<br> c.execute(f'create or replace tabl</code> | 154 | false | false |
| 49 | run | <code>cat &gt; sql/marts/workday__job_overview.sql &lt;&lt;'SQL'<br>WITH family AS (<br> SELECT jfjp.job_profile_id,jf.source_relation,count(DISTINCT jf.job_family_id) associated_job_families_count,count(DISTINCT jfg.job_</code> | 0 | false | false |
| 51 | run | <code>cat &gt; sql/marts/workday__position_overview.sql &lt;&lt;'SQL'<br>WITH base AS (SELECT * FROM staging.stg_workday__position), history AS (<br> SELECT position_id,source_relation,count(DISTINCT worker_id) total_work</code> | 0 | false | false |
| 53 | run | <code>python3 - &lt;&lt;'PY'<br>from run import WorkdayDataPipeline<br>p=WorkdayDataPipeline(target_db_path='/tmp/check2.duckdb'); print('SUCCESS',p.run_pipeline())<br>PY</code> | 10587 | true | false |
| 55 | run | <code>sed -i 's/), similar AS (/), similar_positions AS (/' sql/marts/workday__position_overview.sql; sed -i 's/LEFT JOIN similar s /LEFT JOIN similar_positions s /' sql/marts/workday__position_overview.sql</code> | 484 | false | false |
| 57 | run | <code>python3 - &lt;&lt;'PY'<br>import duckdb,pathlib<br>c=duckdb.connect('/tmp/check2.duckdb')<br>for n in ['workday__position_overview','workday__organization_overview']:<br> try:<br>  c.execute(f'create or replace table mart</code> | 393 | true | false |
| 63 | run | <code>python3 - &lt;&lt;'PY'<br>import duckdb,pathlib,yaml<br>c=duckdb.connect('/tmp/check2.duckdb')<br>for n in ['workday__employee_overview','workday__job_overview','workday__position_overview','workday__organization_ov</code> | 493 | true | false |
| 65 | run | <code>python3 run.py &gt; /tmp/run.log 2&gt;&amp;1; status=$?; tail -100 /tmp/run.log; exit $status</code> | 7105 | true | false |
| 69 | run | <code>python3 - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('workday.duckdb',read_only=True)<br>for t, col in [('stg_workday__worker','worker_history_id'),('stg_workday__organization','organization_id'),('stg_workda</code> | 330 | false | false |
| 71 | run | <code>python3 - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('workday.duckdb',read_only=True)<br>for t, col in [('stg_workday__worker','worker_history_id'),('stg_workday__organization','organization_id'),('stg_workda</code> | 173 | false | false |

### agent action 的 thought/message 命中原句

event 51 / message

```text
Running command: cat > sql/marts/workday__position_overview.sql <<'SQL'
```
event 55 / message

```text
Running command: sed -i 's/), similar AS (/), similar_positions AS (/' sql/marts/workday__position_overview.sql; sed -i 's/LEFT JOIN similar s /LEFT JOIN similar_positions s /' sql/marts/workday__position_overview.sql; sed -i "s/count(DISTINCT r.role_id)/count(DISTINCT r.organization_role_id)/" sql/marts/workday__organization_overview.sql; sed -i "s/ow.role_id=r.organization_role_id/ow.role_id=r.organization_role_id/" sql/marts/workday__organization_overview.sql; python3 - <<'PY'
```
event 57 / message

```text
for n in ['workday__position_overview','workday__organization_overview']:
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
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/marts/workday__position_overview.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/sql/marts/workday__position_overview.sql`
- S6: `records/006_contract_impl-016.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/result.md`
- S10: `data/023_packages_work/023_impl-016_workday__position_overview/023_impl-016_workday__position_overview.json`
- S11: `data/011_agent_alignment/impl-016/workday__position_overview_2025-10-13.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/workday.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions`
