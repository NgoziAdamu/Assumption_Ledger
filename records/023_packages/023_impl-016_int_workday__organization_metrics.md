# impl-016 | intermediate | int_workday__organization_metrics | 差异：S1；日期 2025-10-13

## 契约完整原文

S3:599–777

```yaml
    - name: int_workday__organization_metrics
      description: Organizational health and efficiency metrics aggregated for active Workday organizations
      grain: One row per (organization_id, source_relation) for active organizations (is_inactive = false)
      source_models:
      - staging.stg_workday__organization
      - staging.stg_workday__worker_position_organization
      - staging.stg_workday__position
      - staging.stg_workday__position_job_profile
      - staging.stg_workday__job_profile
      - staging.stg_workday__job_family_job_profile
      - staging.stg_workday__job_family
      - staging.stg_workday__job_family_job_family_group
      - staging.stg_workday__job_family_group
      business_logic: 'Build the base set from organizations marked active. Derive current employee distribution from worker-position-organization joined to position and job profile, restricted to current assignments (no end date): count distinct workers and positions; count distinct current workers by employee type (Regular, Contingent, Intern); compute average and total weekly hours treating missing weekly hours as 40 before aggregation; count distinct current workers by management level (Manager, Senior Manager, Director, Individual Contributor). Derive mobility from all assignments (historical and current), grouped by organization and source: new_hires_last_year counts distinct workers whose assignment started in the past year; departures_last_year counts distinct workers whose assignment ended in the past year; internal_transfers_in counts distinct workers who started in the past year and had any earlier assignment in a different organization within the same source; internal_transfers_out counts distinct workers who ended in the past year and had any later assignment in a different organization within the same source; avg_tenure_days averages days between start and end (or start and today if still active). Derive compensation distribution from current assignments: count distinct compensation grades, job families, and job family groups; most_common_grade is the most frequent compensation grade with ties resolved to the smallest grade ID; count distinct current workers whose job requires shift work or is union eligible. Left join all aggregates to the active organizations and apply defaults: counts to 0, most_common_grade to ''Unknown'', avg_weekly_hours to 40 if no current positions, total_weekly_hours to 0. Compute metrics: organization_health_score (0–100) is 0 when there are no current employees; otherwise sum five 20-point checks capped at 100: has employees; turnover (departures_last_year/current employees) below 20%; management share (managers/current employees) between 10% and 30% inclusive; at least two job families; average tenure at least 365 days. Compute ratios rounded to two decimals: position_fill_rate is current employees divided by total positions times 100 when positions exist, else 0; annual_turnover_rate is departures_last_year divided by current employees times 100 when employees exist, else 0; management_ratio is managers divided by current employees times 100 when employees exist, else 0. Classify performance by health score: ≥80 High Performance, ≥60 Good Performance, ≥40 Average Performance, ≥20 Below Average, else Needs Attention. Classify size by current employee count: 0 Empty, ≤10 Small Team, ≤50 Medium Team, ≤200 Large Team, else Enterprise Unit. Set data_quality_flag with precedence: ERROR if employee count is negative; else WARNING if employees exceed positions, or turnover rate >100%, or management ratio >50%; else VALID.'
      columns:
      - name: organization_id
        data_type: VARCHAR
        description: Primary grouping key from stg_workday__organization; one row per organization_id + source_relation
        tests:
        - not_null
      - name: source_relation
        data_type: VARCHAR
        description: Source system identifier propagated from staging tables
        tests:
        - not_null
      - name: organization_name
        data_type: VARCHAR
        description: Display name copied from stg_workday__organization (may be NULL)
      - name: organization_code
        data_type: VARCHAR
        description: Organization code copied from stg_workday__organization (may be NULL)
      - name: organization_type
        data_type: VARCHAR
        description: Type copied from stg_workday__organization (may be NULL)
      - name: organization_sub_type
        data_type: VARCHAR
        description: Sub-type copied from stg_workday__organization (may be NULL)
      - name: staffing_model
        data_type: VARCHAR
        description: Staffing model copied from stg_workday__organization (may be NULL)
      - name: current_employee_count
        data_type: BIGINT
        description: Distinct current workers per organization (assignments with no end date); defaults to 0
        tests:
        - not_null
      - name: total_positions
        data_type: BIGINT
        description: Distinct current positions per organization (assignments with no end date); defaults to 0
        tests:
        - not_null
      - name: regular_employees
        data_type: BIGINT
        description: Distinct current workers in positions labeled Regular; defaults to 0
        tests:
        - not_null
      - name: contingent_employees
        data_type: BIGINT
        description: Distinct current workers in positions labeled Contingent; defaults to 0
        tests:
        - not_null
      - name: intern_employees
        data_type: BIGINT
        description: Distinct current workers in positions labeled Intern; defaults to 0
        tests:
        - not_null
      - name: avg_weekly_hours
        data_type: DOUBLE
        description: Average weekly hours over current positions, treating missing hours as 40; defaults to 40 when no current positions
        tests:
        - not_null
      - name: total_weekly_hours
        data_type: HUGEINT
        description: Total weekly hours over current positions, treating missing hours as 40; defaults to 0
        tests:
        - not_null
      - name: managers_count
        data_type: BIGINT
        description: Distinct current workers with management level Manager; defaults to 0
        tests:
        - not_null
      - name: senior_managers_count
        data_type: BIGINT
        description: Distinct current workers with management level Senior Manager; defaults to 0
        tests:
        - not_null
      - name: directors_count
        data_type: BIGINT
        description: Distinct current workers with management level Director; defaults to 0
        tests:
        - not_null
      - name: individual_contributors
        data_type: BIGINT
        description: Distinct current workers with management level Individual Contributor; defaults to 0
        tests:
        - not_null
      - name: new_hires_last_year
        data_type: BIGINT
        description: Distinct workers whose assignment started within the past year; defaults to 0
        tests:
        - not_null
      - name: departures_last_year
        data_type: BIGINT
        description: Distinct workers whose assignment ended within the past year; defaults to 0
        tests:
        - not_null
      - name: internal_transfers_in
        data_type: BIGINT
        description: Distinct workers who started within the past year and had any earlier assignment in a different organization; defaults to 0
        tests:
        - not_null
      - name: internal_transfers_out
        data_type: BIGINT
        description: Distinct workers who ended within the past year and had any later assignment in a different organization; defaults to 0
        tests:
        - not_null
      - name: avg_tenure_days
        data_type: DOUBLE
        description: Average days from assignment start to end (or to today if active) across all assignments; defaults to 0
        tests:
        - not_null
      - name: unique_compensation_grades
        data_type: BIGINT
        description: Distinct compensation grades across current positions; defaults to 0
        tests:
        - not_null
      - name: most_common_grade
        data_type: VARCHAR
        description: Most frequent compensation grade across current positions, breaking ties to the smallest grade ID; defaults to 'Unknown'
        tests:
        - not_null
      - name: unique_job_families
        data_type: BIGINT
        description: Distinct job families across current positions; defaults to 0
        tests:
        - not_null
      - name: unique_job_family_groups
        data_type: BIGINT
        description: Distinct job family groups across current positions; defaults to 0
        tests:
        - not_null
      - name: shift_required_positions
        data_type: BIGINT
        description: Distinct current workers whose job profile requires shift work; defaults to 0
        tests:
        - not_null
      - name: union_eligible_positions
        data_type: BIGINT
        description: Distinct current workers whose job profile is union eligible; defaults to 0
        tests:
        - not_null
      - name: organization_health_score
        data_type: INTEGER
        description: Five 20-point checks summed and capped at 100, or 0 when there are no current employees
        tests:
        - not_null
      - name: position_fill_rate
        data_type: DOUBLE
        description: Current employees as a percentage of total positions when positions exist, else 0, rounded to two decimals
      - name: annual_turnover_rate
        data_type: DOUBLE
        description: Departures in the past year as a percentage of current employees when employees exist, else 0, rounded to two decimals
        tests:
        - not_null
      - name: management_ratio
        data_type: DOUBLE
        description: Managers as a percentage of current employees when employees exist, else 0, rounded to two decimals
        tests:
        - not_null
      - name: performance_category
        data_type: VARCHAR
        description: 'Bucketed from organization_health_score: ≥80 High Performance, ≥60 Good Performance, ≥40 Average Performance, ≥20 Below Average, else Needs Attention'
        tests:
        - performance_category IN ('High Performance','Good Performance','Average Performance','Below Average','Needs Attention')
      - name: organization_size_category
        data_type: VARCHAR
        description: 'Size by current_employee_count: 0 Empty, ≤10 Small Team, ≤50 Medium Team, ≤200 Large Team, else Enterprise Unit'
      - name: data_quality_flag
        data_type: VARCHAR
        description: 'Precedence: ERROR if negative employees; else WARNING if employees exceed positions or turnover >100% or management ratio >50%; else VALID'
```

## agent 最终 SQL

S4

```sql
WITH active_org AS (
    SELECT * FROM staging.stg_workday__organization WHERE is_inactive = FALSE
), assignments AS (
    SELECT wpo.worker_id, wpo.position_id, wpo.organization_id, wpo.source_relation,
           wpo.effective_start, wpo.effective_end,
           p.employee_type, p.default_weekly_hours, jp.management_level, jp.compensation_grade_id,
           jp.is_work_shift_required, jp.is_union_eligible, jf.job_family_id, jfg.job_family_group_id
    FROM staging.stg_workday__worker_position_organization AS wpo
    LEFT JOIN staging.stg_workday__position AS p ON wpo.position_id=p.position_id
    LEFT JOIN staging.stg_workday__position_job_profile AS pjp ON p.position_id=pjp.position_id AND p.source_relation=pjp.source_relation
    LEFT JOIN staging.stg_workday__job_profile AS jp ON pjp.job_profile_id=jp.job_profile_id AND pjp.source_relation=jp.source_relation
    LEFT JOIN staging.stg_workday__job_family_job_profile AS jfjp ON jp.job_profile_id=jfjp.job_profile_id AND jp.source_relation=jfjp.source_relation
    LEFT JOIN staging.stg_workday__job_family AS jf ON jfjp.job_family_id=jf.job_family_id AND jfjp.source_relation=jf.source_relation
    LEFT JOIN staging.stg_workday__job_family_job_family_group AS jfjg ON jf.job_family_id=jfjg.job_family_id AND jf.source_relation=jfjg.source_relation
    LEFT JOIN staging.stg_workday__job_family_group AS jfg ON jfjg.job_family_group_id=jfg.job_family_group_id AND jfjg.source_relation=jfg.source_relation
), current_stats AS (
 SELECT organization_id, source_relation, count(DISTINCT worker_id) current_employee_count,
 count(DISTINCT position_id) total_positions,
 count(DISTINCT worker_id) FILTER(WHERE employee_type='Regular') regular_employees,
 count(DISTINCT worker_id) FILTER(WHERE employee_type='Contingent') contingent_employees,
 count(DISTINCT worker_id) FILTER(WHERE employee_type='Intern') intern_employees,
 coalesce(avg(coalesce(default_weekly_hours,40)),40)::DOUBLE avg_weekly_hours,
 coalesce(sum(coalesce(default_weekly_hours,40)),0)::HUGEINT total_weekly_hours,
 count(DISTINCT worker_id) FILTER(WHERE management_level='Manager') managers_count,
 count(DISTINCT worker_id) FILTER(WHERE management_level='Senior Manager') senior_managers_count,
 count(DISTINCT worker_id) FILTER(WHERE management_level='Director') directors_count,
 count(DISTINCT worker_id) FILTER(WHERE management_level='Individual Contributor') individual_contributors,
 count(DISTINCT compensation_grade_id) unique_compensation_grades,
 count(DISTINCT job_family_id) unique_job_families,count(DISTINCT job_family_group_id) unique_job_family_groups,
 count(DISTINCT worker_id) FILTER(WHERE is_work_shift_required) shift_required_positions,
 count(DISTINCT worker_id) FILTER(WHERE is_union_eligible) union_eligible_positions,
 avg(date_diff('day',effective_start,coalesce(effective_end,current_date))) avg_tenure_days
 FROM assignments WHERE effective_end IS NULL GROUP BY organization_id,source_relation
), mobility AS (
 SELECT a.organization_id,a.source_relation,
 count(DISTINCT worker_id) FILTER(WHERE effective_start >= current_date - INTERVAL '1 year') new_hires_last_year,
 count(DISTINCT worker_id) FILTER(WHERE effective_end >= current_date - INTERVAL '1 year') departures_last_year,
 count(DISTINCT worker_id) FILTER(WHERE effective_start >= current_date - INTERVAL '1 year' AND EXISTS (SELECT 1 FROM assignments x WHERE x.worker_id=a.worker_id AND x.source_relation=a.source_relation AND x.organization_id<>a.organization_id AND x.effective_start<a.effective_start)) internal_transfers_in,
 count(DISTINCT worker_id) FILTER(WHERE effective_end >= current_date - INTERVAL '1 year' AND EXISTS (SELECT 1 FROM assignments x WHERE x.worker_id=a.worker_id AND x.source_relation=a.source_relation AND x.organization_id<>a.organization_id AND x.effective_start>a.effective_end)) internal_transfers_out
 FROM assignments a GROUP BY organization_id,source_relation
), grade_freq AS (
 SELECT organization_id,source_relation,compensation_grade_id,
 row_number() over(partition by organization_id,source_relation order by count(*) desc, compensation_grade_id asc) rn
 FROM assignments WHERE effective_end IS NULL AND compensation_grade_id IS NOT NULL
 GROUP BY organization_id,source_relation,compensation_grade_id
)
SELECT o.organization_id,o.source_relation,o.organization_name,o.organization_code,o.organization_type,o.organization_sub_type,o.staffing_model,
 coalesce(c.current_employee_count,0)::BIGINT current_employee_count,coalesce(c.total_positions,0)::BIGINT total_positions,
 coalesce(c.regular_employees,0)::BIGINT regular_employees,coalesce(c.contingent_employees,0)::BIGINT contingent_employees,coalesce(c.intern_employees,0)::BIGINT intern_employees,
 coalesce(c.avg_weekly_hours,40)::DOUBLE avg_weekly_hours,coalesce(c.total_weekly_hours,0)::HUGEINT total_weekly_hours,
 coalesce(c.managers_count,0)::BIGINT managers_count,coalesce(c.senior_managers_count,0)::BIGINT senior_managers_count,coalesce(c.directors_count,0)::BIGINT directors_count,coalesce(c.individual_contributors,0)::BIGINT individual_contributors,
 coalesce(m.new_hires_last_year,0)::BIGINT new_hires_last_year,coalesce(m.departures_last_year,0)::BIGINT departures_last_year,
 coalesce(m.internal_transfers_in,0)::BIGINT internal_transfers_in,coalesce(m.internal_transfers_out,0)::BIGINT internal_transfers_out,
 coalesce(c.avg_tenure_days,0)::DOUBLE avg_tenure_days,coalesce(c.unique_compensation_grades,0)::BIGINT unique_compensation_grades,
 coalesce(g.compensation_grade_id,'Unknown')::VARCHAR most_common_grade,coalesce(c.unique_job_families,0)::BIGINT unique_job_families,coalesce(c.unique_job_family_groups,0)::BIGINT unique_job_family_groups,
 coalesce(c.shift_required_positions,0)::BIGINT shift_required_positions,coalesce(c.union_eligible_positions,0)::BIGINT union_eligible_positions,
 CASE WHEN coalesce(c.current_employee_count,0)=0 THEN 0 ELSE
 (20 + CASE WHEN coalesce(m.departures_last_year,0)*1.0/c.current_employee_count<0.2 THEN 20 ELSE 0 END+
 CASE WHEN c.managers_count*1.0/c.current_employee_count BETWEEN .1 AND .3 THEN 20 ELSE 0 END+
 CASE WHEN c.unique_job_families>=2 THEN 20 ELSE 0 END+CASE WHEN c.avg_tenure_days>=365 THEN 20 ELSE 0 END)::INTEGER END organization_health_score,
 CASE WHEN coalesce(c.total_positions,0)>0 THEN round(c.current_employee_count*100.0/c.total_positions,2) ELSE 0 END::DOUBLE position_fill_rate,
 CASE WHEN coalesce(c.current_employee_count,0)>0 THEN round(coalesce(m.departures_last_year,0)*100.0/c.current_employee_count,2) ELSE 0 END::DOUBLE annual_turnover_rate,
 CASE WHEN coalesce(c.current_employee_count,0)>0 THEN round(coalesce(c.managers_count,0)*100.0/c.current_employee_count,2) ELSE 0 END::DOUBLE management_ratio,
 CASE WHEN coalesce(c.current_employee_count,0)=0 THEN 'Needs Attention' WHEN c.current_employee_count>0 AND (20+CASE WHEN coalesce(m.departures_last_year,0)*1.0/c.current_employee_count<.2 THEN 20 ELSE 0 END+CASE WHEN c.managers_count*1.0/c.current_employee_count BETWEEN .1 AND .3 THEN 20 ELSE 0 END+CASE WHEN c.unique_job_families>=2 THEN 20 ELSE 0 END+CASE WHEN c.avg_tenure_days>=365 THEN 20 ELSE 0 END)>=80 THEN 'High Performance'
 WHEN coalesce(c.current_employee_count,0)>0 THEN CASE WHEN (20+CASE WHEN coalesce(m.departures_last_year,0)*1.0/c.current_employee_count<.2 THEN 20 ELSE 0 END+CASE WHEN c.managers_count*1.0/c.current_employee_count BETWEEN .1 AND .3 THEN 20 ELSE 0 END+CASE WHEN c.unique_job_families>=2 THEN 20 ELSE 0 END+CASE WHEN c.avg_tenure_days>=365 THEN 20 ELSE 0 END)>=60 THEN 'Good Performance' WHEN (20+CASE WHEN coalesce(m.departures_last_year,0)*1.0/c.current_employee_count<.2 THEN 20 ELSE 0 END+CASE WHEN c.managers_count*1.0/c.current_employee_count BETWEEN .1 AND .3 THEN 20 ELSE 0 END+CASE WHEN c.unique_job_families>=2 THEN 20 ELSE 0 END+CASE WHEN c.avg_tenure_days>=365 THEN 20 ELSE 0 END)>=40 THEN 'Average Performance' WHEN (20+CASE WHEN coalesce(m.departures_last_year,0)*1.0/c.current_employee_count<.2 THEN 20 ELSE 0 END+CASE WHEN c.managers_count*1.0/c.current_employee_count BETWEEN .1 AND .3 THEN 20 ELSE 0 END+CASE WHEN c.unique_job_families>=2 THEN 20 ELSE 0 END+CASE WHEN c.avg_tenure_days>=365 THEN 20 ELSE 0 END)>=20 THEN 'Below Average' ELSE 'Needs Attention' END END performance_category,
 CASE WHEN coalesce(c.current_employee_count,0)=0 THEN 'Empty' WHEN c.current_employee_count<=10 THEN 'Small Team' WHEN c.current_employee_count<=50 THEN 'Medium Team' WHEN c.current_employee_count<=200 THEN 'Large Team' ELSE 'Enterprise Unit' END organization_size_category,
 CASE WHEN c.current_employee_count<0 THEN 'ERROR' WHEN c.current_employee_count>c.total_positions OR (c.current_employee_count>0 AND coalesce(m.departures_last_year,0)*100.0/c.current_employee_count>100) OR (c.current_employee_count>0 AND coalesce(c.managers_count,0)*100.0/c.current_employee_count>50) THEN 'WARNING' ELSE 'VALID' END data_quality_flag
FROM active_org o LEFT JOIN current_stats c USING(organization_id,source_relation)
LEFT JOIN mobility m USING(organization_id,source_relation)
LEFT JOIN grade_freq g ON o.organization_id=g.organization_id AND o.source_relation=g.source_relation AND g.rn=1
```

## gold SQL（仅供定位差异）

S5

```sql
-- Intermediate table of organizational health and efficiency indicators
-- Calculate complex indicators such as department allocation efficiency, management level distribution, cross-department mobility, etc.

with organization_base as (
    select 
        o.organization_id,
        o.source_relation,
        o.organization_name,
        o.organization_code,
        o.organization_type,
        o.organization_sub_type,
        o.staffing_model,
        o.is_inactive
    from staging.stg_workday__organization o
    where not o.is_inactive
),

-- Current employee distribution statistics
current_employee_distribution as (
    select 
        wpo.organization_id,
        wpo.source_relation,
        count(distinct wpo.worker_id) as current_employee_count,
        count(distinct wpo.position_id) as total_positions,
        
        -- Statistics by employee type
        count(distinct case when p.employee_type = 'Regular' then wpo.worker_id end) as regular_employees,
        count(distinct case when p.employee_type = 'Contingent' then wpo.worker_id end) as contingent_employees,
        count(distinct case when p.employee_type = 'Intern' then wpo.worker_id end) as intern_employees,
        
        -- Distribution of working hours
        avg(coalesce(p.default_weekly_hours, 40)) as avg_weekly_hours,
        sum(coalesce(p.default_weekly_hours, 40)) as total_weekly_hours,
        
        -- Management level analysis
        count(distinct case when jp.management_level = 'Manager' then wpo.worker_id end) as managers_count,
        count(distinct case when jp.management_level = 'Senior Manager' then wpo.worker_id end) as senior_managers_count,
        count(distinct case when jp.management_level = 'Director' then wpo.worker_id end) as directors_count,
        count(distinct case when jp.management_level = 'Individual Contributor' then wpo.worker_id end) as individual_contributors
        
    from staging.stg_workday__worker_position_organization wpo
    inner join staging.stg_workday__position p 
        on wpo.position_id = p.position_id 
        and wpo.source_relation = p.source_relation
    left join staging.stg_workday__position_job_profile pjp
        on p.position_id = pjp.position_id
        and p.source_relation = pjp.source_relation
    left join staging.stg_workday__job_profile jp
        on pjp.job_profile_id = jp.job_profile_id
        and pjp.source_relation = jp.source_relation
    where wpo.effective_end is null  -- Currently active positions
    group by wpo.organization_id, wpo.source_relation
),

-- Historical employee turnover analysis
employee_mobility_analysis as (
    select 
        wpo.organization_id,
        wpo.source_relation,
        
        -- Inflow and outflow statistics
        count(distinct case when wpo.effective_start >= current_date - interval '1 year' 
              then wpo.worker_id end) as new_hires_last_year,
        count(distinct case when wpo.effective_end >= current_date - interval '1 year' 
              and wpo.effective_end is not null then wpo.worker_id end) as departures_last_year,
        
        -- internal mobility statistics
        count(distinct case when wpo.effective_start >= current_date - interval '1 year'
              and exists (
                  select 1 from staging.stg_workday__worker_position_organization wpo2
                  where wpo2.worker_id = wpo.worker_id 
                  and wpo2.source_relation = wpo.source_relation
                  and wpo2.organization_id != wpo.organization_id
                  and wpo2.effective_start < wpo.effective_start
              ) then wpo.worker_id end) as internal_transfers_in,
              
        count(distinct case when wpo.effective_end >= current_date - interval '1 year'
              and wpo.effective_end is not null
              and exists (
                  select 1 from staging.stg_workday__worker_position_organization wpo3
                  where wpo3.worker_id = wpo.worker_id 
                  and wpo3.source_relation = wpo.source_relation
                  and wpo3.organization_id != wpo.organization_id
                  and wpo3.effective_start > wpo.effective_end
              ) then wpo.worker_id end) as internal_transfers_out,
              
        -- Average tenure
        avg(case when wpo.effective_end is not null 
            then date_diff('day', wpo.effective_start, wpo.effective_end)
            else date_diff('day', wpo.effective_start, current_date)
        end) as avg_tenure_days
        
    from staging.stg_workday__worker_position_organization wpo
    group by wpo.organization_id, wpo.source_relation
),

-- Salary grade distribution analysis
compensation_distribution as (
    select 
        wpo.organization_id,
        wpo.source_relation,
        
        -- Pay grade distribution
        count(distinct jp.compensation_grade_id) as unique_compensation_grades,
        mode() within group (order by jp.compensation_grade_id) as most_common_grade,
        
        -- career family diversity
        count(distinct jf.job_family_id) as unique_job_families,
        count(distinct jfg.job_family_group_id) as unique_job_family_groups,
        
        -- Special request statistics
        count(distinct case when jp.is_work_shift_required then wpo.worker_id end) as shift_required_positions,
        count(distinct case when jp.is_union_eligible then wpo.worker_id end) as union_eligible_positions
        
    from staging.stg_workday__worker_position_organization wpo
    inner join staging.stg_workday__position p 
        on wpo.position_id = p.position_id 
        and wpo.source_relation = p.source_relation
    left join staging.stg_workday__position_job_profile pjp
        on p.position_id = pjp.position_id
        and p.source_relation = pjp.source_relation
    left join staging.stg_workday__job_profile jp
        on pjp.job_profile_id = jp.job_profile_id
        and pjp.source_relation = jp.source_relation
    left join staging.stg_workday__job_family_job_profile jfjp
        on jp.job_profile_id = jfjp.job_profile_id
        and jp.source_relation = jfjp.source_relation
    left join staging.stg_workday__job_family jf
        on jfjp.job_family_id = jf.job_family_id
        and jfjp.source_relation = jf.source_relation
    left join staging.stg_workday__job_family_job_family_group jfjfg
        on jf.job_family_id = jfjfg.job_family_id
        and jf.source_relation = jfjfg.source_relation
    left join staging.stg_workday__job_family_group jfg
        on jfjfg.job_family_group_id = jfg.job_family_group_id
        and jfjfg.source_relation = jfg.source_relation
    where wpo.effective_end is null  -- Currently active positions
    group by wpo.organization_id, wpo.source_relation
),

-- Overall organizational health score
organization_health_metrics as (
    select 
        ob.organization_id,
        ob.source_relation,
        ob.organization_name,
        ob.organization_code,
        ob.organization_type,
        ob.organization_sub_type,
        ob.staffing_model,
        
        -- Staff size indicator
        coalesce(ced.current_employee_count, 0) as current_employee_count,
        coalesce(ced.total_positions, 0) as total_positions,
        coalesce(ced.regular_employees, 0) as regular_employees,
        coalesce(ced.contingent_employees, 0) as contingent_employees,
        coalesce(ced.intern_employees, 0) as intern_employees,
        
        -- Workload Metrics
        coalesce(ced.avg_weekly_hours, 40) as avg_weekly_hours,
        coalesce(ced.total_weekly_hours, 0) as total_weekly_hours,
        
        -- management level indicators
        coalesce(ced.managers_count, 0) as managers_count,
        coalesce(ced.senior_managers_count, 0) as senior_managers_count,
        coalesce(ced.directors_count, 0) as directors_count,
        coalesce(ced.individual_contributors, 0) as individual_contributors,
        
        -- liquidity indicator
        coalesce(ema.new_hires_last_year, 0) as new_hires_last_year,
        coalesce(ema.departures_last_year, 0) as departures_last_year,
        coalesce(ema.internal_transfers_in, 0) as internal_transfers_in,
        coalesce(ema.internal_transfers_out, 0) as internal_transfers_out,
        coalesce(ema.avg_tenure_days, 0) as avg_tenure_days,
        
        -- diversity index
        coalesce(cd.unique_compensation_grades, 0) as unique_compensation_grades,
        coalesce(cd.most_common_grade, 'Unknown') as most_common_grade,
        coalesce(cd.unique_job_families, 0) as unique_job_families,
        coalesce(cd.unique_job_family_groups, 0) as unique_job_family_groups,
        coalesce(cd.shift_required_positions, 0) as shift_required_positions,
        coalesce(cd.union_eligible_positions, 0) as union_eligible_positions,
        
        -- Calculate health score (0-100)
        case 
            when coalesce(ced.current_employee_count, 0) = 0 then 0
            else least(100, 
                (case when coalesce(ced.current_employee_count, 0) > 0 then 20 else 0 end) +  -- Have employee base points
                (case when coalesce(ema.departures_last_year, 0) / nullif(coalesce(ced.current_employee_count, 1), 0) < 0.2 then 20 else 0 end) +  -- low churn rate
                (case when coalesce(ced.managers_count, 0) / nullif(coalesce(ced.current_employee_count, 1), 0) between 0.1 and 0.3 then 20 else 0 end) +  -- Reasonable management ratio
                (case when coalesce(cd.unique_job_families, 0) >= 2 then 20 else 0 end) +  -- functional diversity
                (case when coalesce(ema.avg_tenure_days, 0) >= 365 then 20 else 0 end)  -- employee stability
            )
        end as organization_health_score,
        
        -- Efficiency Ratio Calculation
        case 
            when coalesce(ced.total_positions, 0) > 0 then 
                round(coalesce(ced.current_employee_count, 0) * 100.0 / ced.total_positions, 2)
            else 0 
        end as position_fill_rate,
        
        case 
            when coalesce(ced.current_employee_count, 0) > 0 then 
                round(coalesce(ema.departures_last_year, 0) * 100.0 / ced.current_employee_count, 2)
            else 0 
        end as annual_turnover_rate,
        
        case 
            when coalesce(ced.current_employee_count, 0) > 0 then 
                round(coalesce(ced.managers_count, 0) * 100.0 / ced.current_employee_count, 2)
            else 0 
        end as management_ratio
        
    from organization_base ob
    left join current_employee_distribution ced
        on ob.organization_id = ced.organization_id
        and ob.source_relation = ced.source_relation
    left join employee_mobility_analysis ema
        on ob.organization_id = ema.organization_id
        and ob.source_relation = ema.source_relation
    left join compensation_distribution cd
        on ob.organization_id = cd.organization_id
        and ob.source_relation = cd.source_relation
)

select 
    *,
    -- Organization type classification
    case 
        when organization_health_score >= 80 then 'High Performance'
        when organization_health_score >= 60 then 'Good Performance'
        when organization_health_score >= 40 then 'Average Performance'
        when organization_health_score >= 20 then 'Below Average'
        else 'Needs Attention'
    end as performance_category,
    
    -- Size classification
    case 
        when current_employee_count = 0 then 'Empty'
        when current_employee_count <= 10 then 'Small Team'
        when current_employee_count <= 50 then 'Medium Team'
        when current_employee_count <= 200 then 'Large Team'
        else 'Enterprise Unit'
    end as organization_size_category,
    
    -- Data quality check
    case 
        when current_employee_count < 0 then 'ERROR: Negative employee count'
        when total_positions < current_employee_count then 'WARNING: More employees than positions'
        when annual_turnover_rate > 100 then 'WARNING: Turnover rate exceeds 100%'
        when management_ratio > 50 then 'WARNING: High management ratio'
        else 'VALID'
    end as data_quality_flag
    
from organization_health_metrics
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
| K2 | <code>{"organization_id":"org00000008"}</code> |
| K3 | <code>{"organization_id":"org00000009"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| organization_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| annual_turnover_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_tenure_days | 117 | 117 | 117 | DOUBLE | DOUBLE |
| contingent_employees | 0 | 0 | 0 | BIGINT | BIGINT |
| current_employee_count | 0 | 0 | 0 | BIGINT | BIGINT |
| data_quality_flag | 0 | 0 | 0 | VARCHAR | VARCHAR |
| departures_last_year | 0 | 0 | 0 | BIGINT | BIGINT |
| directors_count | 0 | 0 | 0 | BIGINT | BIGINT |
| individual_contributors | 0 | 0 | 0 | BIGINT | BIGINT |
| intern_employees | 0 | 0 | 0 | BIGINT | BIGINT |
| internal_transfers_in | 0 | 0 | 0 | BIGINT | BIGINT |
| internal_transfers_out | 0 | 0 | 0 | BIGINT | BIGINT |
| management_ratio | 0 | 0 | 0 | DOUBLE | DOUBLE |
| managers_count | 0 | 0 | 0 | BIGINT | BIGINT |
| most_common_grade | 0 | 0 | 0 | VARCHAR | VARCHAR |
| new_hires_last_year | 0 | 0 | 0 | BIGINT | BIGINT |
| organization_code | 0 | 0 | 0 | VARCHAR | VARCHAR |
| organization_health_score | 0 | 0 | 0 | INTEGER | INTEGER |
| organization_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| organization_size_category | 0 | 0 | 0 | VARCHAR | VARCHAR |
| organization_sub_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| organization_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| performance_category | 0 | 0 | 0 | VARCHAR | VARCHAR |
| position_fill_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| regular_employees | 0 | 0 | 0 | BIGINT | BIGINT |
| senior_managers_count | 0 | 0 | 0 | BIGINT | BIGINT |
| shift_required_positions | 0 | 0 | 0 | BIGINT | BIGINT |
| staffing_model | 0 | 0 | 0 | VARCHAR | VARCHAR |
| total_positions | 0 | 0 | 0 | BIGINT | BIGINT |
| union_eligible_positions | 0 | 0 | 0 | BIGINT | BIGINT |
| unique_compensation_grades | 0 | 0 | 0 | BIGINT | BIGINT |
| unique_job_families | 0 | 0 | 0 | BIGINT | BIGINT |
| unique_job_family_groups | 0 | 0 | 0 | BIGINT | BIGINT |

avg_tenure_days 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0.0 | 259.7894736842105 |
| K2 | 0.0 | 270.6 |
| K3 | 0.0 | 227.25 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>30列；[{"column":"source_relation","value":"workday"},{"column":"current_employee_count","value":"0"},{"column":"total_positions","value":"0"}]</code> |
| A4_equal_columns | <code>2组；[{"columns":["current_employee_count","total_positions","regular_employees","contingent_employees","intern_employees","total_weekly_hours","managers_count","senior_managers_count","directors_count","individual_contributors","new_hires_last_year","departures_last_year","internal_transfers_in","internal_transfers_out","unique_compensation_grades","unique_job_families","unique_job_family_groups","shift_required_positions","union_eligible_positions","organization_health_score"],"nonnull_equal_rows":117,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["avg_tenure_days","position_fill_rate","annual_turnover_rate","management_ratio"],"nonnull_equal_rows":117,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>2组；[{"columns":["current_employee_count","total_positions","regular_employees","contingent_employees","intern_employees","total_weekly_hours","managers_count","senior_managers_count","directors_count","individual_contributors","new_hires_last_year","departures_last_year","internal_transfers_in","internal_transfers_out","unique_compensation_grades","unique_job_families","unique_job_family_groups","shift_required_positions","union_eligible_positions","organization_health_score"],"nonnull_equal_rows":117,"meaning_status":"description_texts_differ_no_semantic_judgment"},{"columns":["avg_tenure_days","position_fill_rate","annual_turnover_rate","management_ratio"],"nonnull_equal_rows":117,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| C9_agent_runtime_text | <code>S4:32 current_date；命中数=5</code> |
| C9_gold_runtime_text | <code>S5:62 current_date；命中数=5</code> |
| C9_contract_runtime_text | <code>S3:612 today；命中数=2</code> |
| D10_keyword_in_any_result_field | <code>命中数=2；task_instruction_not_agent_report       business_logic: 'Build organization-level performance by: - Start with intermediate.int_workday__organization_metrics (om) and derive: - avg_weekly_hours_per_employee: when current employees exist, divide total weekly hours by current employees and round to 2 decimals; else 0; if total weekly hours is missing, the result is null.</code> |

## 轨迹索引（不放输出原文）

本题事件总数：85；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions/c4c2f83a-7bb7-4e-9abf5af634f1071/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 7 | run | <code>cat config/layer_dependencies.yaml &amp;&amp; find sql -type f -maxdepth 3 -print</code> | 3401 | true | false |
| 13 | run | <code>find sql -type f -printf '%p %s bytes\n' &#124; sort; sed -n '240,420p' run.py; sed -n '1,100p' docs/data_contract.yaml</code> | 7949 | false | false |
| 17 | run | <code>python3 - &lt;&lt;'PY'<br>import yaml<br>x=yaml.safe_load(open('docs/data_contract.yaml'))<br>print(x.keys(),len(x['staging_contract']['tables']))<br>print([m['name'] for m in x['modeling_spec']['intermediate_models']]</code> | 3942 | true | false |
| 23 | run | <code>cat &gt; sql/intermediate/int_workday__worker_details.sql &lt;&lt;'SQL'<br>SELECT<br>    worker_id,<br>    source_relation,<br>    worker_history_id,<br>    event_type,<br>    effective_start AS hire_date,<br>    effective_end AS </code> | 0 | false | false |
| 25 | run | <code>cat &gt; sql/intermediate/int_workday__organization_metrics.sql &lt;&lt;'SQL'<br>WITH active_org AS (<br>    SELECT * FROM staging.stg_workday__organization WHERE is_inactive = FALSE<br>), assignments AS (<br>    SELECT w</code> | 0 | false | false |
| 27 | run | <code>cat &gt; sql/intermediate/int_workday__career_progression.sql &lt;&lt;'SQL'<br>WITH timeline AS (<br> SELECT wp.worker_id,wp.source_relation,wp.position_id,wp.effective_start,wp.effective_end,<br> row_number() over(par</code> | 0 | false | false |
| 31 | run | <code>cat &gt; sql/marts/workday__employee_overview.sql &lt;&lt;'SQL'<br>WITH base AS (<br> SELECT e.*, md5(coalesce(cast(worker_id as varchar),'_dbt_utils_surrogate_key_null_')&#124;&#124;'-'&#124;&#124;coalesce(source_relation,'_dbt_utils_</code> | 0 | false | false |
| 35 | run | <code>cat &gt; sql/marts/workday__organization_performance.sql &lt;&lt;'SQL'<br>WITH org AS (SELECT * FROM intermediate.int_workday__organization_metrics), emp AS (<br> SELECT organization_id,source_relation,<br> count(DISTI</code> | 0 | false | false |
| 37 | run | <code>cat &gt; sql/marts/workday__organization_overview.sql &lt;&lt;'SQL'<br>WITH active_org AS (SELECT * FROM staging.stg_workday__organization WHERE is_inactive=FALSE), rel AS (<br> SELECT worker_id,organization_id,sour</code> | 0 | false | false |
| 39 | run | <code>python3 - &lt;&lt;'PY'<br>from run import WorkdayDataPipeline<br>p=WorkdayDataPipeline(target_db_path='/tmp/check.duckdb'); print(p.run_pipeline(['staging','intermediate']))<br>PY</code> | 10126 | true | false |
| 41 | run | <code>nl -ba sql/intermediate/int_workday__organization_metrics.sql &#124; sed -n '58,72p'; grep 'FROM raw' sql/staging/stg_workday__worker_position.sql</code> | 3360 | false | false |
| 43 | run | <code>sed -i 's/FROM raw.worker_position AS r/FROM raw.worker_position_history AS r/' sql/staging/stg_workday__worker_position.sql; sed -i 's/FROM raw.worker_position_organization AS r/FROM raw.worker_posit</code> | 1110 | false | false |
| 45 | run | <code>sed -n '64,65p' sql/intermediate/int_workday__organization_metrics.sql</code> | 1544 | false | false |
| 47 | run | <code>python3 - &lt;&lt;'PY'<br>import duckdb, pathlib<br>c=duckdb.connect('/tmp/check.duckdb')<br>for n in ['stg_workday__worker_position','stg_workday__worker_position_organization']:<br> c.execute(f'create or replace tabl</code> | 154 | true | false |
| 49 | run | <code>cat &gt; sql/marts/workday__job_overview.sql &lt;&lt;'SQL'<br>WITH family AS (<br> SELECT jfjp.job_profile_id,jf.source_relation,count(DISTINCT jf.job_family_id) associated_job_families_count,count(DISTINCT jfg.job_</code> | 0 | false | false |
| 51 | run | <code>cat &gt; sql/marts/workday__position_overview.sql &lt;&lt;'SQL'<br>WITH base AS (SELECT * FROM staging.stg_workday__position), history AS (<br> SELECT position_id,source_relation,count(DISTINCT worker_id) total_work</code> | 0 | false | false |
| 53 | run | <code>python3 - &lt;&lt;'PY'<br>from run import WorkdayDataPipeline<br>p=WorkdayDataPipeline(target_db_path='/tmp/check2.duckdb'); print('SUCCESS',p.run_pipeline())<br>PY</code> | 10587 | true | false |
| 55 | run | <code>sed -i 's/), similar AS (/), similar_positions AS (/' sql/marts/workday__position_overview.sql; sed -i 's/LEFT JOIN similar s /LEFT JOIN similar_positions s /' sql/marts/workday__position_overview.sql</code> | 484 | true | false |
| 65 | run | <code>python3 run.py &gt; /tmp/run.log 2&gt;&amp;1; status=$?; tail -100 /tmp/run.log; exit $status</code> | 7105 | true | false |
| 69 | run | <code>python3 - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('workday.duckdb',read_only=True)<br>for t, col in [('stg_workday__worker','worker_history_id'),('stg_workday__organization','organization_id'),('stg_workda</code> | 330 | false | false |
| 71 | run | <code>python3 - &lt;&lt;'PY'<br>import duckdb<br>c=duckdb.connect('workday.duckdb',read_only=True)<br>for t, col in [('stg_workday__worker','worker_history_id'),('stg_workday__organization','organization_id'),('stg_workda</code> | 173 | false | false |

### agent action 的 thought/message 命中原句

event 25 / message

```text
Running command: cat > sql/intermediate/int_workday__organization_metrics.sql <<'SQL'
```
event 31 / message

```text
 LEFT JOIN intermediate.int_workday__organization_metrics o ON w.organization_id=o.organization_id AND w.source_relation=o.source_relation
```
event 35 / message

```text
WITH org AS (SELECT * FROM intermediate.int_workday__organization_metrics), emp AS (
```
event 41 / message

```text
Running command: nl -ba sql/intermediate/int_workday__organization_metrics.sql | sed -n '58,72p'; grep 'FROM raw' sql/staging/stg_workday__worker_position.sql
```
event 43 / message

```text
Running command: sed -i 's/FROM raw.worker_position AS r/FROM raw.worker_position_history AS r/' sql/staging/stg_workday__worker_position.sql; sed -i 's/FROM raw.worker_position_organization AS r/FROM raw.worker_position_organization_history AS r/' sql/staging/stg_workday__worker_position_organization.sql; sed -i "s/THEN 20 ELSE 0)>=/THEN 20 ELSE 0 END)>=/g" sql/intermediate/int_workday__organization_metrics.sql; sed -i "s/THEN 20 ELSE 0)\(>=\)/THEN 20 ELSE 0 END)\1/g" sql/intermediate/int_workday__organization_metrics.sql; grep -n 'performance_category' sql/intermediate/int_workday__organization_metrics.sql
```
event 45 / message

```text
Running command: sed -n '64,65p' sql/intermediate/int_workday__organization_metrics.sql
```
event 47 / message

```text
for n in ['int_workday__worker_position_enriched','int_workday__worker_employee_enhanced','int_workday__organization_metrics','int_workday__career_progression']:
```
event 51 / message

```text
 SELECT organization_id,source_relation,organization_name,organization_type,organization_sub_type,staffing_model,current_employee_count,organization_health_score,annual_turnover_rate,performance_category,organization_size_category FROM intermediate.int_workday__organization_metrics
```
event 55 / message

```text
for q in ["select count(*) from staging.stg_workday__worker_position_organization where effective_end is null", "select organization_id,count(*) from intermediate.int_workday__organization_metrics group by 1 order by 2 desc limit 2", "select organization_id,count(*) from mart.workday__employee_overview group by 1 order by 2 desc limit 5", "select count(*) from mart.workday__employee_overview where organization_id<>'Unknown'"]:
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/011_table_alignment.jsonl`
- S2: `records/011_alignment_impl-016.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-016/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/sql/intermediate/int_workday__organization_metrics.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/sql/intermediate/int_workday__organization_metrics.sql`
- S6: `records/006_contract_impl-016.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/dacomp-de-impl-016/result.md`
- S10: `data/023_packages_work/023_impl-016_int_workday__organization_metrics/023_impl-016_int_workday__organization_metrics.json`
- S11: `data/011_agent_alignment/impl-016/int_workday__organization_metrics_2025-10-13.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-016/workday.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-016/agent/.events/sessions`
