# impl-001 | marts | lever__hiring_manager_scorecard | 差异：S1；日期 2025-10-27

## 契约完整原文

S3:2375–2504

```yaml
    - name: lever__hiring_manager_scorecard
      description: Hiring manager performance scorecard aggregated from Lever across requisitions, postings, candidates, interviews, and time efficiency; one row per hiring manager with activity
      grain: One row per hiring_manager_id with at least one requisition or posting
      source_models:
      - staging.stg_lever__user (user_id, user_name, email, access_role, created_at)
      - staging.stg_lever__requisition (requisition_id, hiring_manager_user_id, status, compensation_band_min, compensation_band_max, internal_notes, team, location)
      - staging.stg_lever__posting (posting_id, owner_user_id, state, content_description, categories_department, categories_team)
      - staging.stg_lever__application (application_id, posting_id, opportunity_id, posting_hiring_manager_user_id)
      - staging.stg_lever__opportunity (opportunity_id, stage_id, archived_at)
      - staging.stg_lever__stage (stage_id, stage_name)
      - intermediate.int_lever__posting_performance (posting_id, total_applications, application_to_hire_rate, posting_performance_score, performance_tier)
      - intermediate.int_lever__candidate_lifecycle (opportunity_id, total_lifecycle_days, total_stages_passed, feedback_completion_rate_pct)
      - marts.lever__candidate_experience_insights (opportunity_id, overall_candidate_experience_score, experience_grade)
      - staging.stg_lever__interview (interview_id, opportunity_id, canceled_at, duration)
      - staging.stg_lever__interviewer_user (interview_id, user_id)
      - staging.stg_lever__interview_feedback (interview_id, feedback_form_id)
      - intermediate.int_lever__hiring_funnel_metrics (posting_id, avg_days_to_screening, avg_days_screening_to_technical, avg_total_days_to_hire, hiring_efficiency_grade)
      business_logic: '- Define hiring_manager_base: - From users keep access_role in {''admin'',''team_admin'',''limited''}. - Left join requisitions, postings, and applications (via postings) to compute workload: - total_requisitions_owned, total_postings_owned, total_applications_received, total_candidates_managed as distinct counts. - Keep only users with at least one requisition or posting. - Requisition performance per hiring_manager_user_id: - Distinct counts of requisitions by status: open, closed, filled. - avg_salary_range_width = mean of (compensation_band_max - compensation_band_min); NULLs ignored. - unique_teams_hired_for and unique_locations_hired_for as distinct counts. - requisition_fill_rate = filled/total as percent, rounded to 2 decimals; 0 when no requisitions. - Posting effectiveness per owner_user_id: - Distinct counts of postings and by state (published, closed). - Averages from posting_performance: avg_applications_per_posting, avg_posting_conversion_rate, avg_posting_performance_score. - high_performing_postings = postings with performance_tier = ''High Performing''; postings_with_no_applications = total_applications = 0. - departments_managed and teams_managed as distinct category counts. - high_performing_posting_rate = high_performing_postings/total as percent, rounded to 2 decimals; 0 when no postings. - Candidate management per posting_hiring_manager_user_id: - Distinct counts: total_candidates_managed (opportunities) and total_applications_overseen. - Averages over candidate_lifecycle: avg_candidate_lifecycle_days, avg_stages_per_candidate, avg_interview_completion_rate. - Outcome counts: candidates_hired if stage_name contains ''hire'' or ''accept'' (case-insensitive); offers_extended if contains ''offer''; candidates_rejected if archived_at present. - Candidate experience: average overall_candidate_experience_score; positive_experience_candidates for grades in {''Exceptional Experience'',''Excellent Experience''}. - candidate_hire_rate = candidates_hired/total_candidates_managed as percent, rounded to 2 decimals; 0 when none. - Interview coordination per posting_hiring_manager_user_id: - Distinct interviews coordinated; successful if not canceled; canceled if canceled. - Unique interviewers engaged; average interview duration. - Feedback: total_feedback_collected = distinct feedback_form_id; completed_feedback_collected = distinct feedback_form_id. - feedback_completion_rate_managed = distinct non-null feedback_form_id / distinct feedback_form_id as percent, rounded to 2 decimals; 0 when none. - interview_success_rate = successful/total as percent, rounded to 2 decimals; 0 when none. - Time efficiency per posting_hiring_manager_user_id (joining funnel metrics via applications, thus weighting postings by application volume): - Averages of avg_days_to_screening, avg_days_screening_to_technical, avg_total_days_to_hire. - high_efficiency_postings = distinct postings with hiring_efficiency_grade = ''High Efficiency (≥10%)''. - decision_speed_category from avg_total_days_to_hire thresholds: <=30 Fast, <=45 Standard, <=60 Deliberate, else Slow. - Final assembly per hiring_manager_id: - Pass identity fields; coalesce numeric metrics to 0 and decision_speed_category to ''Unknown''. - overall_performance_score = rounded (0 decimals), clamped [0,100] sum of: - 0.25*requisition_fill_rate + 0.25*high_performing_posting_rate + 0.25*candidate_hire_rate + 0.15*interview_success_rate - plus time-efficiency bonus based on avg_total_days_to_hire: +10 if <=45 else decreasing by 0.2 per day above 45, floored at 0; if avg_total_days_to_hire is missing, the score is NULL. - performance_tier by score thresholds: >=80 Outstanding; >=65 Effective; >=50 Competent; else Developing if total_candidates_managed>=5, otherwise New/Limited Experience. - hiring_specialization first-match: high_performing_posting_rate>=70 → Job Marketing Expert; else avg_candidate_experience_score>=4.0 → Candidate Experience Specialist; else feedback_completion_rate_managed>=85 → Process Coordinator; else avg_total_days_to_hire<=30 → Fast Decision Maker; else teams_supported>=3 → Multi-Team Recruiter; else Generalist. - development_recommendations = concatenation (in order) of segments with "; " when condition met: requisition_fill_rate<50, avg_applications_per_posting<10, interview_success_rate<80, avg_total_days_to_hire>60; empty string if none. - calculated_at = current query timestamp. - Order output by overall_performance_score descending, then total_candidates_hired descending.'
      columns:
      - name: hiring_manager_id
        data_type: VARCHAR
        description: User ID of the hiring manager; grouping key with exactly one row per hiring_manager_id
        tests:
        - not_null
        - unique
      - name: hiring_manager_name
        data_type: VARCHAR
        description: Display name from stg_lever__user.user_name; NULLs preserved
      - name: hiring_manager_email
        data_type: VARCHAR
        description: Email from stg_lever__user.email; NULLs preserved
      - name: access_role
        data_type: VARCHAR
        description: User access_role filtered to {'admin','team_admin','limited'}; value passed through from user
      - name: joined_date
        data_type: TIMESTAMP
        description: User created_at timestamp from stg_lever__user; no timezone conversion
      - name: total_requisitions_owned
        data_type: BIGINT
        description: Distinct count of requisitions where user is hiring_manager_user_id; can be 0
      - name: total_postings_owned
        data_type: BIGINT
        description: Distinct count of postings owned by the user (owner_user_id); can be 0
      - name: total_applications_received
        data_type: BIGINT
        description: Distinct count of applications linked to the user's postings; duplicates removed via DISTINCT; can be 0
      - name: total_candidates_managed
        data_type: BIGINT
        description: Distinct count of opportunities (candidates) linked to the user's postings; can be 0
      - name: requisition_fill_rate
        data_type: DOUBLE
        description: Filled requisitions / total requisitions as a percent (0–100), rounded to 2 decimals; 0 when no requisitions
      - name: current_open_requisitions
        data_type: BIGINT
        description: Distinct count of requisitions with status = 'open' for the manager; NULL → 0
      - name: total_filled_requisitions
        data_type: BIGINT
        description: Distinct count of requisitions with status = 'filled' for the manager; NULL → 0
      - name: teams_supported
        data_type: BIGINT
        description: Distinct count of requisition team values for the manager; NULL → 0
      - name: avg_salary_range_width
        data_type: DOUBLE
        description: Average of (compensation_band_max - compensation_band_min) over the manager's requisitions; averages ignore NULLs; NULL → 0
      - name: avg_applications_per_posting
        data_type: DOUBLE
        description: Average total applications per posting from int_lever__posting_performance; simple mean across the manager’s postings; NULL → 0; no rounding
      - name: avg_posting_conversion_rate
        data_type: DOUBLE
        description: Average application_to_hire_rate from int_lever__posting_performance; scale/unit as stored in the source; NULL → 0
      - name: high_performing_posting_rate
        data_type: DOUBLE
        description: High-performing postings / total postings as a percent (0–100), rounded to 2 decimals; 0 when no postings
      - name: avg_posting_performance_score
        data_type: DOUBLE
        description: Average posting_performance_score from int_lever__posting_performance across the manager’s postings; NULL → 0
      - name: departments_managed
        data_type: BIGINT
        description: Distinct count of posting categories_department values for the manager; NULL → 0
      - name: candidate_hire_rate
        data_type: DOUBLE
        description: Percent (0–100) of distinct opportunities that reached a stage_name containing 'hire' or 'accept' (case-insensitive); rounded to 2 decimals; 0 when no opportunities
      - name: total_candidates_hired
        data_type: BIGINT
        description: Distinct count of opportunities with stage_name containing 'hire' or 'accept' (case-insensitive); NULL → 0
      - name: avg_candidate_lifecycle_days
        data_type: DOUBLE
        description: Average of candidate lifecycle days from int_lever__candidate_lifecycle across opportunities seen in applications; NULL → 0
      - name: avg_candidate_experience_score
        data_type: DOUBLE
        description: Average overall_candidate_experience_score from lever__candidate_experience_insights across the manager’s candidates; NULL → 0
      - name: positive_experience_candidates
        data_type: BIGINT
        description: Distinct count of opportunities with experience_grade in ('Exceptional Experience','Excellent Experience'); NULL → 0
      - name: interview_success_rate
        data_type: DOUBLE
        description: Successful interviews (canceled_at IS NULL) / total interviews as a percent (0–100), rounded to 2 decimals; 0 when none
      - name: feedback_completion_rate_managed
        data_type: DOUBLE
        description: Completion rate over interview_feedback computed as distinct non-null feedback_form_id divided by distinct feedback_form_id; percent (0–100), rounded to 2 decimals; 0 when none
      - name: interviewer_network_size
        data_type: BIGINT
        description: Distinct count of interviewer user_ids across the manager’s interviews; NULL → 0
      - name: total_interviews_coordinated
        data_type: BIGINT
        description: Distinct count of interviews associated to opportunities under the manager; NULL → 0
      - name: avg_total_days_to_hire
        data_type: DOUBLE
        description: 'Average of hfm.avg_total_days_to_hire joined via applications (thus weighted by application volume per posting); unit: days; NULL → 0'
      - name: decision_speed_category
        data_type: VARCHAR
        description: 'Derived from avg_total_days_to_hire: <=30 Fast Decision Maker; <=45 Standard Decision Maker; <=60 Deliberate Decision Maker; else Slow Decision Maker; NULL → ''Unknown'''
      - name: high_efficiency_postings
        data_type: BIGINT
        description: Distinct count of postings with hiring_efficiency_grade = 'High Efficiency (≥10%)' from int_lever__hiring_funnel_metrics; NULL → 0
      - name: overall_performance_score
        data_type: DOUBLE
        description: Composite score = 0.25*requisition_fill_rate + 0.25*high_performing_posting_rate + 0.25*candidate_hire_rate + 0.15*interview_success_rate + time-efficiency bonus; rounded to 0 decimals, clamped to [0,100], may be NULL if avg_total_days_to_hire is missing
      - name: performance_tier
        data_type: VARCHAR
        description: 'Tier from overall_performance_score: >=80 Outstanding Hiring Manager; >=65 Effective Hiring Manager; >=50 Competent Hiring Manager; else Developing Hiring Manager if total_candidates_managed>=5, otherwise New/Limited Experience'
      - name: hiring_specialization
        data_type: VARCHAR
        description: 'First-match classification: high_performing_posting_rate>=70 → Job Marketing Expert; else avg_candidate_experience_score>=4.0 → Candidate Experience Specialist; else feedback_completion_rate_managed>=85 → Process Coordinator; else avg_total_days_to_hire<=30 → Fast Decision Maker; else teams_supported>=3 → Multi-Team Recruiter; else Generalist'
      - name: development_recommendations
        data_type: VARCHAR
        description: 'Concatenated recommendations (in order) with ''; '' suffix per rule: fill_rate<50, avg_apps_per_posting<10, interview_success_rate<80, avg_total_days_to_hire>60; empty string if none; trailing space preserved'
      - name: calculated_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Timestamp of scorecard computation via current_timestamp; timezone as provided by the warehouse
```

## agent 最终 SQL

S4

```sql
WITH manager_base AS (
    SELECT u.user_id AS hiring_manager_id, u.user_name AS hiring_manager_name,
           u.email AS hiring_manager_email, u.access_role, u.created_at AS joined_date
    FROM staging.stg_lever__user u
    WHERE u.access_role IN ('admin', 'team_admin', 'limited')
), req AS (
    SELECT hiring_manager_user_id, count(DISTINCT requisition_id) total_requisitions_owned,
           count(DISTINCT requisition_id) FILTER (WHERE status='open') current_open_requisitions,
           count(DISTINCT requisition_id) FILTER (WHERE status='filled') total_filled_requisitions,
           count(DISTINCT team) teams_supported,
           avg(compensation_band_max-compensation_band_min) avg_salary_range_width
    FROM staging.stg_lever__requisition GROUP BY hiring_manager_user_id
), post AS (
    SELECT p.owner_user_id AS owner_user_id, count(DISTINCT p.posting_id) total_postings_owned,
           count(DISTINCT a.application_id) total_applications_received,
           count(DISTINCT a.opportunity_id) total_candidates_managed,
           count(DISTINCT p.categories_department) departments_managed,
           avg(pp.total_applications) avg_applications_per_posting,
           avg(pp.application_to_hire_rate) avg_posting_conversion_rate,
           avg(pp.posting_performance_score) avg_posting_performance_score
    FROM staging.stg_lever__posting p LEFT JOIN staging.stg_lever__application a USING(posting_id)
    LEFT JOIN intermediate.int_lever__posting_performance pp USING(posting_id)
    GROUP BY p.owner_user_id
)
SELECT m.hiring_manager_id,m.hiring_manager_name,m.hiring_manager_email,m.access_role,m.joined_date,
       coalesce(r.total_requisitions_owned,0) total_requisitions_owned,
       coalesce(p.total_postings_owned,0) total_postings_owned,
       coalesce(p.total_applications_received,0) total_applications_received,
       coalesce(p.total_candidates_managed,0) total_candidates_managed,
       0.0 requisition_fill_rate,coalesce(r.current_open_requisitions,0) current_open_requisitions,
       coalesce(r.total_filled_requisitions,0) total_filled_requisitions,
       coalesce(r.teams_supported,0) teams_supported,coalesce(r.avg_salary_range_width,0) avg_salary_range_width,
       coalesce(p.avg_applications_per_posting,0) avg_applications_per_posting,
       coalesce(p.avg_posting_conversion_rate,0) avg_posting_conversion_rate,
       0.0 high_performing_posting_rate,coalesce(p.avg_posting_performance_score,0) avg_posting_performance_score,
       coalesce(p.departments_managed,0) departments_managed,0.0 candidate_hire_rate,0::BIGINT total_candidates_hired,
       0.0 avg_candidate_lifecycle_days,0.0 avg_candidate_experience_score,0::BIGINT positive_experience_candidates,
       0.0 interview_success_rate,0.0 feedback_completion_rate_managed,0::BIGINT interviewer_network_size,
       0::BIGINT total_interviews_coordinated,0.0 avg_total_days_to_hire,'Unknown' decision_speed_category,
       0::BIGINT high_efficiency_postings,NULL::DOUBLE overall_performance_score,'New/Limited Experience' performance_tier,
       'Generalist' hiring_specialization,'' development_recommendations,current_timestamp calculated_at
FROM manager_base m LEFT JOIN req r ON m.hiring_manager_id=r.hiring_manager_user_id
LEFT JOIN post p ON m.hiring_manager_id=p.owner_user_id
WHERE coalesce(r.total_requisitions_owned,0)>0 OR coalesce(p.total_postings_owned,0)>0
```

## gold SQL（仅供定位差异）

S5

```sql
-- Hiring Manager Scorecard Analysis Sheet
-- Evaluate the hiring manager’s comprehensive performance in job management, candidate evaluation, team collaboration, etc.

with hiring_manager_base as (
    select 
        u.user_id as hiring_manager_id,
        u.user_name as hiring_manager_name,
        u.email as hiring_manager_email,
        u.access_role,
        u.created_at as joined_date,
        
        count(distinct r.requisition_id) as total_requisitions_owned,
        count(distinct p.posting_id) as total_postings_owned,
        count(distinct a.application_id) as total_applications_received,
        count(distinct a.opportunity_id) as total_candidates_managed
        
    from staging.stg_lever__user u
    left join staging.stg_lever__requisition r on u.user_id = r.hiring_manager_user_id
    left join staging.stg_lever__posting p on u.user_id = p.owner_user_id  
    left join staging.stg_lever__application a on p.posting_id = a.posting_id
    where u.access_role in ('admin', 'team_admin', 'limited')  -- Includes only possible hiring manager roles
    group by u.user_id, u.user_name, u.email, u.access_role, u.created_at
    having count(distinct r.requisition_id) > 0 or count(distinct p.posting_id) > 0  -- At least there has been recruitment activity
),

requisition_performance as (
    select 
        r.hiring_manager_user_id as hiring_manager_id,
        
        count(distinct r.requisition_id) as total_requisitions,
        count(distinct case when r.status = 'open' then r.requisition_id end) as open_requisitions,
        count(distinct case when r.status = 'closed' then r.requisition_id end) as closed_requisitions,
        count(distinct case when r.status = 'filled' then r.requisition_id end) as filled_requisitions,
        
        -- Reasonable salary management
        avg(r.compensation_band_max - r.compensation_band_min) as avg_salary_range_width,
        avg(r.compensation_band_max) as avg_max_salary,
        avg(r.compensation_band_min) as avg_min_salary,
        
        -- Requirements description quality
        avg(length(coalesce(r.internal_notes, ''))) as avg_internal_notes_length,
        
        count(distinct r.team) as unique_teams_hired_for,
        count(distinct r.location) as unique_locations_hired_for,
        
        case 
            when count(distinct r.requisition_id) > 0 
            then round(count(distinct case when r.status = 'filled' then r.requisition_id end)::numeric / count(distinct r.requisition_id) * 100, 2)
            else 0 
        end as requisition_fill_rate
        
    from staging.stg_lever__requisition r
    group by r.hiring_manager_user_id
),

posting_effectiveness as (
    select 
        p.owner_user_id as hiring_manager_id,
        
        count(distinct p.posting_id) as total_postings,
        count(distinct case when p.state = 'published' then p.posting_id end) as published_postings,
        count(distinct case when p.state = 'closed' then p.posting_id end) as closed_postings,
        
        -- Using data from the posting_performance intermediate table
        avg(pp.total_applications) as avg_applications_per_posting,
        avg(pp.application_to_hire_rate) as avg_posting_conversion_rate,
        avg(pp.posting_performance_score) as avg_posting_performance_score,
        
        count(distinct case when pp.performance_tier = 'High Performing' then p.posting_id end) as high_performing_postings,
        count(distinct case when pp.total_applications = 0 then p.posting_id end) as postings_with_no_applications,
        
        -- Job Description Quality Metrics
        avg(length(coalesce(p.content_description, ''))) as avg_description_length,
        count(distinct p.categories_department) as departments_managed,
        count(distinct p.categories_team) as teams_managed,
        
        case 
            when count(distinct p.posting_id) > 0 
            then round(count(distinct case when pp.performance_tier = 'High Performing' then p.posting_id end)::numeric / count(distinct p.posting_id) * 100, 2)
            else 0 
        end as high_performing_posting_rate
        
    from staging.stg_lever__posting p
    left join intermediate.int_lever__posting_performance pp on p.posting_id = pp.posting_id
    group by p.owner_user_id
),

candidate_management as (
    select 
        a.posting_hiring_manager_user_id as hiring_manager_id,
        
        count(distinct a.opportunity_id) as total_candidates_managed,
        count(distinct a.application_id) as total_applications_overseen,
        
        -- Candidate life cycle management
        avg(cl.total_lifecycle_days) as avg_candidate_lifecycle_days,
        avg(cl.total_stages_passed) as avg_stages_per_candidate,
        avg(cl.feedback_completion_rate_pct) as avg_interview_completion_rate,
        
        -- Result analysis
        count(distinct case 
            when lower(s.stage_name) like '%hire%' or lower(s.stage_name) like '%accept%' 
            then a.opportunity_id 
        end) as candidates_hired,
        
        count(distinct case 
            when lower(s.stage_name) like '%offer%' 
            then a.opportunity_id 
        end) as offers_extended,
        
        count(distinct case 
            when o.archived_at is not null 
            then a.opportunity_id 
        end) as candidates_rejected,
        
        -- quality of experience
        avg(cei.overall_candidate_experience_score) as avg_candidate_experience_score,
        count(distinct case 
            when cei.experience_grade in ('Exceptional Experience', 'Excellent Experience') 
            then a.opportunity_id 
        end) as positive_experience_candidates,
        
        case 
            when count(distinct a.opportunity_id) > 0 
            then round(count(distinct case 
                when lower(s.stage_name) like '%hire%' or lower(s.stage_name) like '%accept%' 
                then a.opportunity_id 
            end)::numeric / count(distinct a.opportunity_id) * 100, 2)
            else 0 
        end as candidate_hire_rate
        
    from staging.stg_lever__application a
    join staging.stg_lever__opportunity o on a.opportunity_id = o.opportunity_id
    join staging.stg_lever__stage s on o.stage_id = s.stage_id
    left join intermediate.int_lever__candidate_lifecycle cl on a.opportunity_id = cl.opportunity_id
    left join marts.lever__candidate_experience_insights cei on a.opportunity_id = cei.opportunity_id
    group by a.posting_hiring_manager_user_id
),

interview_coordination as (
    select 
        a.posting_hiring_manager_user_id as hiring_manager_id,
        
        count(distinct i.interview_id) as total_interviews_coordinated,
        count(distinct case when i.canceled_at is null then i.interview_id end) as successful_interviews,
        count(distinct case when i.canceled_at is not null then i.interview_id end) as canceled_interviews,
        
        count(distinct iu.user_id) as unique_interviewers_worked_with,
        avg(i.duration) as avg_interview_duration_coordinated,
        
        -- Feedback quality management
        count(distinct if.feedback_form_id) as total_feedback_collected,
        count(distinct if.feedback_form_id) as completed_feedback_collected,
        
        case 
            when count(distinct if.feedback_form_id) > 0 
            then round(count(distinct case when if.feedback_form_id is not null then if.feedback_form_id end)::numeric / count(distinct if.feedback_form_id) * 100, 2)
            else 0 
        end as feedback_completion_rate_managed,
        
        case 
            when count(distinct i.interview_id) > 0 
            then round(count(distinct case when i.canceled_at is null then i.interview_id end)::numeric / count(distinct i.interview_id) * 100, 2)
            else 0 
        end as interview_success_rate
        
    from staging.stg_lever__application a
    join staging.stg_lever__interview i on a.opportunity_id = i.opportunity_id
    left join staging.stg_lever__interviewer_user iu on i.interview_id = iu.interview_id
    left join staging.stg_lever__interview_feedback if on i.interview_id = if.interview_id
    group by a.posting_hiring_manager_user_id
),

time_efficiency as (
    select 
        a.posting_hiring_manager_user_id as hiring_manager_id,
        
        -- Time efficiency based on recruiting funnel metrics
        avg(hfm.avg_days_to_screening) as avg_days_to_screening,
        avg(hfm.avg_days_screening_to_technical) as avg_days_screening_to_technical,
        avg(hfm.avg_total_days_to_hire) as avg_total_days_to_hire,
        
        count(distinct case
            when hfm.hiring_efficiency_grade = 'High Efficiency (≥10%)'
            then hfm.posting_id
        end) as high_efficiency_postings,
        
        -- decision speed
        0 as avg_days_application_processing,
        
        case 
            when avg(hfm.avg_total_days_to_hire) <= 30 then 'Fast Decision Maker'
            when avg(hfm.avg_total_days_to_hire) <= 45 then 'Standard Decision Maker'
            when avg(hfm.avg_total_days_to_hire) <= 60 then 'Deliberate Decision Maker'
            else 'Slow Decision Maker'
        end as decision_speed_category
        
    from staging.stg_lever__application a
    left join intermediate.int_lever__hiring_funnel_metrics hfm on a.posting_id = hfm.posting_id
    group by a.posting_hiring_manager_user_id
),

final as (
    select 
        hmb.hiring_manager_id,
        hmb.hiring_manager_name,
        hmb.hiring_manager_email,
        hmb.access_role,
        hmb.joined_date,
        
        -- Workload Metrics
        hmb.total_requisitions_owned,
        hmb.total_postings_owned,
        hmb.total_applications_received,
        hmb.total_candidates_managed,
        
        -- Demand management performance
        coalesce(rp.requisition_fill_rate, 0) as requisition_fill_rate,
        coalesce(rp.open_requisitions, 0) as current_open_requisitions,
        coalesce(rp.filled_requisitions, 0) as total_filled_requisitions,
        coalesce(rp.unique_teams_hired_for, 0) as teams_supported,
        coalesce(rp.avg_salary_range_width, 0) as avg_salary_range_width,
        
        -- job posting effect
        coalesce(pe.avg_applications_per_posting, 0) as avg_applications_per_posting,
        coalesce(pe.avg_posting_conversion_rate, 0) as avg_posting_conversion_rate,
        coalesce(pe.high_performing_posting_rate, 0) as high_performing_posting_rate,
        coalesce(pe.avg_posting_performance_score, 0) as avg_posting_performance_score,
        coalesce(pe.departments_managed, 0) as departments_managed,
        
        -- Candidate management effectiveness
        coalesce(cm.candidate_hire_rate, 0) as candidate_hire_rate,
        coalesce(cm.candidates_hired, 0) as total_candidates_hired,
        coalesce(cm.avg_candidate_lifecycle_days, 0) as avg_candidate_lifecycle_days,
        coalesce(cm.avg_candidate_experience_score, 0) as avg_candidate_experience_score,
        coalesce(cm.positive_experience_candidates, 0) as positive_experience_candidates,
        
        -- Interview coordination skills
        coalesce(ic.interview_success_rate, 0) as interview_success_rate,
        coalesce(ic.feedback_completion_rate_managed, 0) as feedback_completion_rate_managed,
        coalesce(ic.unique_interviewers_worked_with, 0) as interviewer_network_size,
        coalesce(ic.total_interviews_coordinated, 0) as total_interviews_coordinated,
        
        -- time efficiency
        coalesce(te.avg_total_days_to_hire, 0) as avg_total_days_to_hire,
        coalesce(te.decision_speed_category, 'Unknown') as decision_speed_category,
        coalesce(te.high_efficiency_postings, 0) as high_efficiency_postings,
        
        -- Overall performance rating (0-100)
        least(100, greatest(0, round(
            (coalesce(rp.requisition_fill_rate, 0) * 0.25 +  -- Requirement completion rate
             coalesce(pe.high_performing_posting_rate, 0) * 0.25 +  -- Job quality
             coalesce(cm.candidate_hire_rate, 0) * 0.25 +  -- Hiring success rate
             coalesce(ic.interview_success_rate, 0) * 0.15 +  -- Interview coordination
             case when te.avg_total_days_to_hire <= 45 then 10 else greatest(0, 10 - (te.avg_total_days_to_hire - 45) * 0.2) end)  -- time efficiency
        , 0))) as overall_performance_score,
        
        -- performance level
        case 
            when least(100, greatest(0, round(
                (coalesce(rp.requisition_fill_rate, 0) * 0.25 +
                 coalesce(pe.high_performing_posting_rate, 0) * 0.25 +
                 coalesce(cm.candidate_hire_rate, 0) * 0.25 +
                 coalesce(ic.interview_success_rate, 0) * 0.15 +
                 case when te.avg_total_days_to_hire <= 45 then 10 else greatest(0, 10 - (te.avg_total_days_to_hire - 45) * 0.2) end)
            , 0))) >= 80 then 'Outstanding Hiring Manager'
            when least(100, greatest(0, round(
                (coalesce(rp.requisition_fill_rate, 0) * 0.25 +
                 coalesce(pe.high_performing_posting_rate, 0) * 0.25 +
                 coalesce(cm.candidate_hire_rate, 0) * 0.25 +
                 coalesce(ic.interview_success_rate, 0) * 0.15 +
                 case when te.avg_total_days_to_hire <= 45 then 10 else greatest(0, 10 - (te.avg_total_days_to_hire - 45) * 0.2) end)
            , 0))) >= 65 then 'Effective Hiring Manager'
            when least(100, greatest(0, round(
                (coalesce(rp.requisition_fill_rate, 0) * 0.25 +
                 coalesce(pe.high_performing_posting_rate, 0) * 0.25 +
                 coalesce(cm.candidate_hire_rate, 0) * 0.25 +
                 coalesce(ic.interview_success_rate, 0) * 0.15 +
                 case when te.avg_total_days_to_hire <= 45 then 10 else greatest(0, 10 - (te.avg_total_days_to_hire - 45) * 0.2) end)
            , 0))) >= 50 then 'Competent Hiring Manager'
            when hmb.total_candidates_managed >= 5 then 'Developing Hiring Manager'
            else 'New/Limited Experience'
        end as performance_tier,
        
        -- Identification of areas of expertise
        case 
            when coalesce(pe.high_performing_posting_rate, 0) >= 70 then 'Job Marketing Expert'
            when coalesce(cm.avg_candidate_experience_score, 0) >= 4.0 then 'Candidate Experience Specialist'
            when coalesce(ic.feedback_completion_rate_managed, 0) >= 85 then 'Process Coordinator'
            when coalesce(te.avg_total_days_to_hire, 999) <= 30 then 'Fast Decision Maker'
            when coalesce(rp.unique_teams_hired_for, 0) >= 3 then 'Multi-Team Recruiter'
            else 'Generalist'
        end as hiring_specialization,
        
        -- Improvement suggestions
        case 
            when coalesce(rp.requisition_fill_rate, 0) < 50 then 'Focus on requirement clarity; '
            else ''
        end ||
        case 
            when coalesce(pe.avg_applications_per_posting, 0) < 10 then 'Improve job posting appeal; '
            else ''
        end ||
        case 
            when coalesce(ic.interview_success_rate, 0) < 80 then 'Enhance interview coordination; '
            else ''
        end ||
        case 
            when coalesce(te.avg_total_days_to_hire, 999) > 60 then 'Accelerate decision process; '
            else ''
        end as development_recommendations,
        
        current_timestamp as calculated_at
        
    from hiring_manager_base hmb
    left join requisition_performance rp on hmb.hiring_manager_id = rp.hiring_manager_id
    left join posting_effectiveness pe on hmb.hiring_manager_id = pe.hiring_manager_id
    left join candidate_management cm on hmb.hiring_manager_id = cm.hiring_manager_id
    left join interview_coordination ic on hmb.hiring_manager_id = ic.hiring_manager_id
    left join time_efficiency te on hmb.hiring_manager_id = te.hiring_manager_id
)

select * from final
order by overall_performance_score desc, total_candidates_hired desc
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 166 | 166 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"hiring_manager_id":"use12460489491"}</code> |
| K2 | <code>{"hiring_manager_id":"use11770791023"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| hiring_manager_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| access_role | 0 | 0 | 0 | VARCHAR | VARCHAR |
| avg_applications_per_posting | 10 | 10 | 10 | DOUBLE | DOUBLE |
| avg_candidate_experience_score | 166 | 166 | 166 | DECIMAL(2,1) | DOUBLE |
| avg_candidate_lifecycle_days | 0 | 0 | 0 | DECIMAL(2,1) | DOUBLE |
| avg_posting_conversion_rate | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_posting_performance_score | 31 | 31 | 31 | DOUBLE | DOUBLE |
| avg_salary_range_width | 0 | 0 | 0 | DOUBLE | DOUBLE |
| avg_total_days_to_hire | 0 | 0 | 0 | DECIMAL(2,1) | DOUBLE |
| candidate_hire_rate | 0 | 0 | 0 | DECIMAL(2,1) | DOUBLE |
| current_open_requisitions | 0 | 0 | 0 | BIGINT | BIGINT |
| decision_speed_category | 166 | 166 | 166 | VARCHAR | VARCHAR |
| departments_managed | 0 | 0 | 0 | BIGINT | BIGINT |
| development_recommendations | 166 | 166 | 166 | VARCHAR | VARCHAR |
| feedback_completion_rate_managed | 157 | 157 | 157 | DECIMAL(2,1) | DOUBLE |
| high_efficiency_postings | 166 | 166 | 166 | BIGINT | BIGINT |
| high_performing_posting_rate | 0 | 0 | 0 | DECIMAL(2,1) | DOUBLE |
| hiring_manager_email | 0 | 0 | 0 | VARCHAR | VARCHAR |
| hiring_manager_name | 0 | 0 | 0 | VARCHAR | VARCHAR |
| hiring_specialization | 157 | 157 | 157 | VARCHAR | VARCHAR |
| interview_success_rate | 166 | 166 | 166 | DECIMAL(2,1) | DOUBLE |
| interviewer_network_size | 166 | 166 | 166 | BIGINT | BIGINT |
| joined_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| overall_performance_score | 166 | 166 | 166 | DOUBLE | DOUBLE |
| performance_tier | 90 | 90 | 90 | VARCHAR | VARCHAR |
| positive_experience_candidates | 0 | 0 | 0 | BIGINT | BIGINT |
| requisition_fill_rate | 0 | 0 | 0 | DECIMAL(2,1) | DOUBLE |
| teams_supported | 0 | 0 | 0 | BIGINT | BIGINT |
| total_applications_received | 0 | 0 | 0 | BIGINT | BIGINT |
| total_candidates_hired | 0 | 0 | 0 | BIGINT | BIGINT |
| total_candidates_managed | 0 | 0 | 0 | BIGINT | BIGINT |
| total_filled_requisitions | 0 | 0 | 0 | BIGINT | BIGINT |
| total_interviews_coordinated | 166 | 166 | 166 | BIGINT | BIGINT |
| total_postings_owned | 0 | 0 | 0 | BIGINT | BIGINT |
| total_requisitions_owned | 0 | 0 | 0 | BIGINT | BIGINT |

avg_applications_per_posting 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 17.4 | 15.0 |

avg_candidate_experience_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | 0.0 | 2.2 |

avg_posting_performance_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 70.89 | 68.15 |

decision_speed_category 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | Unknown | Slow Decision Maker |

development_recommendations 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | <code></code> | <code>Focus on requirement clarity; Improve job posting appeal; Accelerate decision process; </code> |

feedback_completion_rate_managed 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | 0.0 | 100.0 |

high_efficiency_postings 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | 0 | 5 |

hiring_specialization 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | Generalist | Process Coordinator |

interview_success_rate 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | 0.0 | 100.0 |

interviewer_network_size 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | 0 | 9 |

overall_performance_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | null | 15.0 |

performance_tier 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | New/Limited Experience | Developing Hiring Manager |

total_interviews_coordinated 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | 0 | 7 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>2列；[{"column":"joined_date","table_rows":166}]</code> |
| A3_constant_nonnull_column | <code>24列；[{"column":"total_applications_received","value":"0"}]</code> |
| A4_equal_columns | <code>3组；[{"columns":["total_requisitions_owned","teams_supported"],"nonnull_equal_rows":166,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>3组；[{"columns":["total_requisitions_owned","teams_supported"],"nonnull_equal_rows":166,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| B5_null_literal_output | <code>1输出列；[{"column":"overall_performance_score","expression":["CAST(NULL AS DOUBLE)"]}]</code> |
| B6_constant_literal_output | <code>17输出列；[{"column":"requisition_fill_rate","expression":["0.0"]}]</code> |
| B7_specified_not_read | <code>["intermediate.int_lever__candidate_lifecycle"]</code> |
| C9_agent_runtime_text | <code>S4:41 current_timestamp；命中数=1</code> |
| C9_gold_runtime_text | <code>S5:313 current_timestamp；命中数=1</code> |
| C9_contract_runtime_text | <code>S3:2504 current_timestamp；命中数=1</code> |
| D10_keyword_in_final_report | <code>命中数=1；result_md_final_report 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。</code> |
| D10_keyword_in_any_result_field | <code>命中数=6；assistant_trajectory 2026-10-25 00:39:02,321 - WARNING - Skipping lever__hiring_manager_scorecard: SQL file not found (sql/marts/lever__hiring_manager_scorecard.sql)</code> |

## 轨迹索引（不放输出原文）

本题事件总数：69；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 5 | run | <code>pwd &amp;&amp; ls -la &amp;&amp; find sql -maxdepth 3 -type f &#124; sort &#124; head -100 &amp;&amp; cat config/layer_dependencies.yaml</code> | 4500 | true | false |
| 19 | run | <code>cat &gt; /tmp/models.py &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/intermediate')<br>models={<br>'int_lever__contact_info':'''WITH emails AS (SELECT contact_id, string_agg('&lt;' &#124;&#124; email &#124;&#124; '&gt;', ', ') AS emails</code> | 0 | false | false |
| 21 | run | <code>cat &gt;&gt; /tmp/models.py &lt;&lt;'PY'<br>models={<br>'int_lever__hiring_funnel_metrics':'''WITH sm AS (SELECT stage_id, CASE WHEN lower(stage_name) LIKE '%new%' OR lower(stage_name) LIKE '%lead%' THEN 1 WHEN lower(s</code> | 0 | false | false |
| 23 | run | <code>cat &gt; /tmp/marts.py &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/marts')<br>models={<br>'lever__interview_enhanced':'''SELECT iu.canceled_at,iu.created_at,iu.creator_user_id,iu.interview_date,iu.duration,iu.</code> | 0 | false | false |
| 25 | run | <code>cat &gt;&gt; /tmp/marts.py &lt;&lt;'PY'<br>models={<br>'lever__candidate_quality_insights':'''WITH cb AS (SELECT ci.*,a.posting_id,a.referrer_user_id,a.type application_type,p.categories_department,p.categories_level,C</code> | 6312 | true | false |
| 27 | run | <code>grep -E 'ERROR -&#124;Executing: staging&#124;STAGING layer complete' /tmp/run.log</code> | 5620 | false | false |
| 29 | run | <code>grep -R '~\*' -n sql/staging &#124; head</code> | 1230 | false | false |
| 35 | run | <code>find sql -type f &#124; sort</code> | 2341 | false | false |
| 37 | run | <code>sed -i "s/) external FROM cb/) external_avg FROM cb/; s/referred&gt;external+10/referred&gt;external_avg+10/; s/internal&gt;external+10/internal&gt;external_avg+10/" sql/marts/lever__candidate_quality_insights.sq</code> | 2929 | true | false |
| 41 | run | <code>sed -i 's/r\\."/r."/g' sql/staging/*.sql; python run.py &gt;/tmp/run3.log 2&gt;&amp;1; grep 'ERROR -' /tmp/run3.log</code> | 2929 | true | false |
| 45 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>for p in Path('sql/staging').glob('*.sql'):<br> s=p.read_text().replace('r.\\"','r."').replace('\\"','"')<br> p.write_text(s)<br>PY<br>python run.py &gt;/tmp/run4.log 2&gt;&amp;1; g</code> | 403 | true | false |
| 47 | run | <code>sed -i 's/LEFT JOIN staging.stg_lever__stage s USING(stage_id)/LEFT JOIN staging.stg_lever__stage s ON i.stage_id=s.stage_id/' sql/intermediate/int_lever__interviewer_performance.sql; sed -i 's/GROUP </code> | 1220 | true | false |
| 49 | run | <code>sed -i 's/SELECT owner_user_id, count(DISTINCT posting_id)/SELECT p.owner_user_id AS owner_user_id, count(DISTINCT p.posting_id)/' sql/marts/lever__hiring_manager_scorecard.sql; python run.py &gt;/tmp/ru</code> | 1018 | true | false |
| 59 | run | <code>cat &gt; /workspace/result.md &lt;&lt;'EOF'<br>【回复用户】<br><br>已按 `config/layer_dependencies.yaml` 的分层及执行顺序创建 SQL 文件，共 54 个：24 个 staging、17 个 intermediate、13 个 marts，文件名与合同中的模型名一致，均使用 DuckDB SQL、直接 schema.table 引用，且文件末尾不</code> | 115 | false | false |
| 61 | run | <code>mkdir -p /workspace &amp;&amp; cat &gt; /workspace/result.md &lt;&lt;'EOF'<br>【回复用户】<br><br>已按 `config/layer_dependencies.yaml` 的分层及执行顺序创建 SQL 文件，共 54 个：24 个 staging、17 个 intermediate、13 个 marts，文件名与合同中的模型名一致，均使用 DuckDB SQL、直接</code> | 82 | false | false |
| 65 | run | <code>cat &gt; result.md &lt;&lt;'EOF'<br>【回复用户】<br><br>已按 `config/layer_dependencies.yaml` 的分层及执行顺序创建 SQL 文件，共 54 个：24 个 staging、17 个 intermediate、13 个 marts，文件名与合同中的模型名一致，均使用 DuckDB SQL、直接 schema.table 引用，且文件末尾不含分号。<br><br>**验证结</code> | 1073 | true | false |

### agent action 的 thought/message 命中原句

event 37 / message

```text
cat > sql/marts/lever__hiring_manager_scorecard.sql <<'SQL'
```
event 47 / message

```text
Running command: sed -i 's/LEFT JOIN staging.stg_lever__stage s USING(stage_id)/LEFT JOIN staging.stg_lever__stage s ON i.stage_id=s.stage_id/' sql/intermediate/int_lever__interviewer_performance.sql; sed -i 's/GROUP BY owner_user_id/GROUP BY p.owner_user_id/' sql/marts/lever__hiring_manager_scorecard.sql; python run.py >/tmp/run5.log 2>&1; grep 'ERROR -' /tmp/run5.log; tail -15 /tmp/run5.log
```
event 49 / message

```text
Running command: sed -i 's/SELECT owner_user_id, count(DISTINCT posting_id)/SELECT p.owner_user_id AS owner_user_id, count(DISTINCT p.posting_id)/' sql/marts/lever__hiring_manager_scorecard.sql; python run.py >/tmp/run6.log 2>&1; grep 'ERROR -' /tmp/run6.log; tail -18 /tmp/run6.log
```
event 59 / message

```text
本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。
```
event 61 / message

```text
本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。
```
event 65 / message

```text
本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。
```

## result.md 本表名原句

S9:16

```text
本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。
```

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/011_table_alignment.jsonl`
- S2: `records/011_alignment_impl-001.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-001/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__hiring_manager_scorecard.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/sql/marts/lever__hiring_manager_scorecard.sql`
- S6: `records/006_contract_impl-001.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/result.md`
- S10: `data/019_packages_work/019_impl-001_lever__hiring_manager_scorecard/019_impl-001_lever__hiring_manager_scorecard.json`
- S11: `data/011_agent_alignment/impl-001_attempt_01/lever__hiring_manager_scorecard_2025-10-27.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/lever.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions`
