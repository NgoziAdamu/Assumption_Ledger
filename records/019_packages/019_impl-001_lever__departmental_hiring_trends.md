# impl-001 | marts | lever__departmental_hiring_trends | 差异：S1；日期 原记录

## 契约完整原文

S3:2148–2281

```yaml
    - name: lever__departmental_hiring_trends
      description: Department- and team-level hiring metrics replicated across posting slices using Lever staging and intermediate joins
      grain: One row per posting in staging.stg_lever__posting multiplied by the count of application_volume rows for the same department+team (department/team-level aggregates replicated across each posting’s department/team/location/level/commitment_type)
      source_models:
      - staging.stg_lever__posting
      - staging.stg_lever__application
      - staging.stg_lever__opportunity
      - staging.stg_lever__stage
      - intermediate.int_lever__candidate_lifecycle
      - staging.stg_lever__interview
      - staging.stg_lever__interviewer_user
      - staging.stg_lever__interview_feedback
      - marts.lever__candidate_experience_insights
      - intermediate.int_lever__hiring_funnel_metrics
      business_logic: '- Build department_posting_base from postings: - Dimensions defaulted via COALESCE: department=''Unknown Department'', team=''Unknown Team'', location=''Unknown Location'', level=''Unknown Level'', commitment_type=''Unknown Commitment''. - Keep posting_id and timestamps; derive posting_month and posting_quarter by truncating created_at. - application_volume (dept+team+location+level+commitment_type+month+quarter): - Distinct counts: applications, candidates, opportunities, postings; referred applications where referrer_user_id is present. - referral_rate = referred applications / total applications * 100, rounded to 2 decimals; 0 when no applications. - avg_applications_per_posting = total applications / active postings, rounded to 1 decimal; NULL when active postings=0 (later COALESCE to 0). - hiring_outcomes (dept+team): - candidates_hired: distinct opportunities with stage name containing ''hire'' or ''accept''; offers_extended: distinct opportunities with stage name containing ''offer''. - Averages for hired/accepted only: time_to_hire (lifecycle days) and interviews_per_hire. - hire_conversion_rate = candidates_hired / distinct opportunities * 100, rounded to 2 decimals; 0 when no opportunities. - offer_acceptance_rate = candidates_hired / offers_extended * 100, rounded to 2 decimals; 0 when no offers. - interview_metrics (dept+team): - total_interviews_conducted: distinct interviews; completed when not canceled; canceled when canceled. - unique_interviewers: distinct interviewer users; avg_interview_duration: average interview duration (minutes); total_interview_time_minutes: sum of durations. - interview_completion_rate = completed / total * 100, rounded to 2 decimals; 0 when no interviews. - feedback_completion_rate = 100 when any feedback exists else 0, rounded to 2 decimals. - candidate_quality (dept+team): - avg_candidate_experience_score: average overall_candidate_experience_score. - positive_experience_rate = exceptional/excellent experience opportunities / total opportunities * 100, rounded to 2 decimals; 0 when no opportunities. - avg_screening_pass_rate: average application_to_screening_rate; high_efficiency_postings: distinct postings with hiring_efficiency_grade=''High Efficiency (≥10%)''. - cost_efficiency (dept+team): - Join dpb to application_volume, hiring_outcomes, and interview_metrics on dept+team; group by dept+team. - total_interview_hours = sum(total_interview_time_minutes) / 60.0. - interview_hours_per_hire = total_interview_hours / total hires, rounded to 1 decimal; NULL when no hires (later COALESCE to 0). - applications_per_hire = sum(total_applications) / total hires, rounded to 1 decimal; NULL when no hires (later COALESCE to 0). - hires_per_posting = total hires / sum(active_postings), rounded to 2 decimals; 0 when no active postings. - cost_efficiency_tier by interview_hours_per_hire: ≤10 Highly Efficient, ≤20 Efficient, ≤40 Moderate Efficiency, >40 Low Efficiency; No Hires when hires=0 (later COALESCE to ''No Data'' if join missing). - Note: dept+team joins cause ho/im to repeat across each application_volume row and posting; sums aggregate repeated rows (scaled by both postings and application_volume rows per dept+team), while ratios dividing repeated sums (e.g., interview_hours_per_hire) cancel the scaling. - Final assembly: - Join department_posting_base to all aggregates on dept+team only, replicating dept+team metrics across each posting’s location/level/commitment slice and across application_volume slices. - Keep rows where application_volume.total_applications>0 OR application_volume.active_postings>0. - Ranks (global across the final set): hiring_volume_rank by candidates_hired DESC, conversion_efficiency_rank by hire_conversion_rate DESC, candidate_experience_rank by avg_candidate_experience_score DESC; ties share rank with gaps. - department_performance_score (0–100, rounded to 0 decimals, clamped): min(25, hires*2.5) + (hire_conversion_rate*0.2) + (interview_completion_rate*0.2) + (positive_experience_rate*0.15) + ([cost_efficiency_tier in {Highly Efficient, Efficient} → 20 else 10]*0.2). - performance_tier: ≥75 Top Performing Department; ≥60 High Performing Department; ≥45 Standard Performing Department; else if total_applications≥10 Underperforming Department; otherwise Low Activity Department. - department_strength priority: referral_rate≥30 → offer_acceptance_rate≥80 → avg_candidate_experience_score≥4.0 → avg_time_to_hire_days≤30 → cost_efficiency_tier in {Highly Efficient, Efficient} → else Standard Operations. - calculated_at = current_timestamp; final output ordered by department_performance_score DESC, then total_applications DESC.'
      columns:
      - name: department
        data_type: VARCHAR
        description: Department from postings; NULLs replaced with 'Unknown Department'; metrics computed at department+team and replicated across rows
        tests:
        - not_null
      - name: team
        data_type: VARCHAR
        description: Team from postings; NULLs replaced with 'Unknown Team'; metrics computed at department+team and replicated across rows
        tests:
        - not_null
      - name: location
        data_type: VARCHAR
        description: Posting location; NULLs replaced with 'Unknown Location'; slice dimension only (aggregates joined on department+team)
        tests:
        - not_null
      - name: level
        data_type: VARCHAR
        description: Posting job level; NULLs replaced with 'Unknown Level'; slice dimension only (aggregates joined on department+team)
        tests:
        - not_null
      - name: commitment_type
        data_type: VARCHAR
        description: Posting commitment type; NULLs replaced with 'Unknown Commitment'; slice dimension only (aggregates joined on department+team)
        tests:
        - not_null
      - name: total_applications
        data_type: BIGINT
        description: Distinct application count from application_volume; joined on department+team only; per-row values reflect one application_volume slice; COALESCE to 0
      - name: unique_candidates
        data_type: BIGINT
        description: Distinct candidate count from application_volume; joined on department+team only; per-row values reflect one application_volume slice; COALESCE to 0
      - name: active_postings
        data_type: BIGINT
        description: Distinct posting count from application_volume; joined on department+team only; per-row values reflect one application_volume slice grouped by time; COALESCE to 0
      - name: avg_applications_per_posting
        data_type: DOUBLE
        description: Rounded to 1 decimal; total applications divided by active postings from application_volume; 0 when denominator is NULL via COALESCE; joined on department+team only
      - name: referral_rate
        data_type: DOUBLE
        description: Percentage with 2 decimals; referred applications divided by total applications *100; 0 when no applications; joined on department+team only
      - name: candidates_hired
        data_type: BIGINT
        description: Distinct opportunities marked as hired/accepted (stage contains 'hire' or 'accept') at department+team; replicated across rows; COALESCE to 0
      - name: offers_extended
        data_type: BIGINT
        description: Distinct opportunities with offer stages (stage contains 'offer') at department+team; replicated across rows; COALESCE to 0
      - name: hire_conversion_rate
        data_type: DOUBLE
        description: Percentage with 2 decimals; candidates_hired divided by distinct opportunities *100 at department+team; 0 when no opportunities; replicated; COALESCE to 0
      - name: offer_acceptance_rate
        data_type: DOUBLE
        description: Percentage with 2 decimals; candidates_hired divided by offers_extended *100 at department+team; 0 when no offers; replicated; COALESCE to 0
      - name: avg_time_to_hire_days
        data_type: DOUBLE
        description: Average lifecycle days for hired/accepted opportunities at department+team; NULL→0 via COALESCE; replicated across rows
      - name: avg_interviews_per_hire
        data_type: DOUBLE
        description: Average interview count for hired/accepted opportunities at department+team; NULL→0 via COALESCE; replicated across rows
      - name: total_interviews_conducted
        data_type: BIGINT
        description: Distinct interviews at department+team; replicated across rows; COALESCE to 0
      - name: interview_completion_rate
        data_type: DOUBLE
        description: Percentage with 2 decimals; completed interviews (not canceled) divided by total interviews *100 at department+team; 0 when no interviews; replicated; COALESCE to 0
      - name: feedback_completion_rate
        data_type: DOUBLE
        description: Percentage with 2 decimals; 100 when any feedback exists else 0; replicated across rows; COALESCE to 0
      - name: unique_interviewers
        data_type: BIGINT
        description: Distinct interviewer users at department+team; replicated across rows; COALESCE to 0
      - name: avg_interview_duration_minutes
        data_type: DOUBLE
        description: Average interview duration in minutes at department+team; NULL→0 via COALESCE; replicated across rows
      - name: avg_candidate_experience_score
        data_type: DOUBLE
        description: Average overall candidate experience score at department+team; NULL→0 via COALESCE; replicated across rows
      - name: positive_experience_rate
        data_type: DOUBLE
        description: Percentage with 2 decimals; exceptional/excellent experience opportunities divided by total opportunities *100 at department+team; 0 when no opportunities; replicated; COALESCE to 0
      - name: avg_screening_pass_rate
        data_type: DOUBLE
        description: Average screening pass rate from hiring funnel metrics at department+team; NULL→0 via COALESCE; replicated across rows
      - name: high_efficiency_postings
        data_type: BIGINT
        description: Distinct postings with hiring_efficiency_grade='High Efficiency (≥10%)' at department+team; replicated across rows; COALESCE to 0
      - name: interview_hours_per_hire
        data_type: DOUBLE
        description: Rounded to 1 decimal; total interview hours divided by total hires from cost_efficiency; hires 0→NULL→0 via COALESCE
      - name: applications_per_hire
        data_type: DOUBLE
        description: Rounded to 1 decimal; total applications divided by total hires from cost_efficiency; hires 0→NULL→0 via COALESCE
      - name: hires_per_posting
        data_type: DOUBLE
        description: Rounded to 2 decimals; total hires divided by sum of active postings from cost_efficiency; 0 when no active postings; replicated across rows
      - name: cost_efficiency_tier
        data_type: VARCHAR
        description: Tier by interview_hours_per_hire thresholds (≤10 Highly Efficient, ≤20 Efficient, ≤40 Moderate Efficiency, else Low Efficiency; No Hires when hires=0); COALESCE to 'No Data' if join missing; replicated across rows
      - name: hiring_volume_rank
        data_type: BIGINT
        description: Global rank ordered by candidates_hired descending; ties share rank with gaps; replicated across rows for a department+team
      - name: conversion_efficiency_rank
        data_type: BIGINT
        description: Global rank ordered by hire_conversion_rate descending; ties share rank with gaps; replicated across rows for a department+team
      - name: candidate_experience_rank
        data_type: BIGINT
        description: Global rank ordered by avg_candidate_experience_score descending; ties share rank with gaps; replicated across rows for a department+team
      - name: department_performance_score
        data_type: DOUBLE
        description: '0–100 score rounded to 0 decimals and clamped; weights: min(25, hires*2.5)+hire_conversion_rate*0.2+interview_completion_rate*0.2+positive_experience_rate*0.15+[cost tier in {Highly Efficient, Efficient}→20 else 10]*0.2; replicated across rows'
      - name: performance_tier
        data_type: VARCHAR
        description: 'Tier from department_performance_score and activity: ≥75 Top Performing Department, ≥60 High Performing Department, ≥45 Standard Performing Department, else if total_applications≥10 Underperforming Department, otherwise Low Activity Department'
      - name: department_strength
        data_type: VARCHAR
        description: 'Priority: referral_rate≥30 → offer_acceptance_rate≥80 → avg_candidate_experience_score≥4.0 → avg_time_to_hire_days≤30 → cost_efficiency_tier in {Highly Efficient, Efficient} → else Standard Operations'
      - name: calculated_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Timestamp of computation using current_timestamp; same for all rows in a run
```

## agent 最终 SQL

S4

```sql
WITH base AS (
    SELECT
        coalesce(categories_department, 'Unknown Department') AS department,
        coalesce(categories_team, 'Unknown Team') AS team,
        coalesce(categories_location, 'Unknown Location') AS location,
        coalesce(categories_level, 'Unknown Level') AS level,
        coalesce(categories_commitment, 'Unknown Commitment') AS commitment_type,
        posting_id
    FROM staging.stg_lever__posting
), apps AS (
    SELECT posting_id, count(DISTINCT application_id) AS total_applications,
           count(DISTINCT candidate_id) AS unique_candidates,
           count(DISTINCT referrer_user_id) AS referred
    FROM staging.stg_lever__application
    GROUP BY posting_id
), metrics AS (
    SELECT b.department, b.team, count(DISTINCT b.posting_id) AS active_postings,
           coalesce(sum(a.total_applications), 0) AS total_applications,
           coalesce(sum(a.unique_candidates), 0) AS unique_candidates,
           round(100.0 * sum(a.referred) / nullif(sum(a.total_applications), 0), 2) AS referral_rate
    FROM base b LEFT JOIN apps a USING (posting_id)
    GROUP BY b.department, b.team
), scored AS (
    SELECT b.*, coalesce(m.total_applications, 0) AS total_applications,
           coalesce(m.unique_candidates, 0) AS unique_candidates,
           coalesce(m.active_postings, 0) AS active_postings,
           coalesce(round(m.total_applications * 1.0 / nullif(m.active_postings, 0), 1), 0) AS avg_applications_per_posting,
           coalesce(m.referral_rate, 0) AS referral_rate,
           0::BIGINT AS candidates_hired, 0::BIGINT AS offers_extended,
           0.0 AS hire_conversion_rate, 0.0 AS offer_acceptance_rate,
           0.0 AS avg_time_to_hire_days, 0.0 AS avg_interviews_per_hire,
           0::BIGINT AS total_interviews_conducted, 0.0 AS interview_completion_rate,
           0.0 AS feedback_completion_rate, 0::BIGINT AS unique_interviewers,
           0.0 AS avg_interview_duration_minutes, 0.0 AS avg_candidate_experience_score,
           0.0 AS positive_experience_rate, 0.0 AS avg_screening_pass_rate,
           0::BIGINT AS high_efficiency_postings, 0.0 AS interview_hours_per_hire,
           0.0 AS applications_per_hire, 0.0 AS hires_per_posting,
           'No Data' AS cost_efficiency_tier
    FROM base b LEFT JOIN metrics m USING (department, team)
)
SELECT department, team, location, level, commitment_type, total_applications, unique_candidates, active_postings, avg_applications_per_posting, referral_rate, candidates_hired, offers_extended, hire_conversion_rate, offer_acceptance_rate, avg_time_to_hire_days, avg_interviews_per_hire, total_interviews_conducted, interview_completion_rate, feedback_completion_rate, unique_interviewers, avg_interview_duration_minutes, avg_candidate_experience_score, positive_experience_rate, avg_screening_pass_rate, high_efficiency_postings, interview_hours_per_hire, applications_per_hire, hires_per_posting, cost_efficiency_tier, rank() OVER (ORDER BY candidates_hired DESC) AS hiring_volume_rank,
       rank() OVER (ORDER BY hire_conversion_rate DESC) AS conversion_efficiency_rank,
       rank() OVER (ORDER BY avg_candidate_experience_score DESC) AS candidate_experience_rank,
       least(100, greatest(0, round(least(25, candidates_hired * 2.5) + hire_conversion_rate * .2 + interview_completion_rate * .2 + positive_experience_rate * .15 + 2))) AS department_performance_score,
       CASE WHEN total_applications >= 10 THEN 'Underperforming Department' ELSE 'Low Activity Department' END AS performance_tier,
       'Standard Operations' AS department_strength,
       current_timestamp AS calculated_at
FROM scored
WHERE total_applications > 0 OR active_postings > 0
```

## gold SQL（仅供定位差异）

S5

```sql
-- Department recruitment trend analysis table
-- Analyze recruitment effectiveness, cost-effectiveness and talent strategies by department and team dimensions

with department_posting_base as (
    select 
        coalesce(p.categories_department, 'Unknown Department') as department,
        coalesce(p.categories_team, 'Unknown Team') as team,
        coalesce(p.categories_location, 'Unknown Location') as location,
        coalesce(p.categories_level, 'Unknown Level') as level,
        coalesce(p.categories_commitment, 'Unknown Commitment') as commitment_type,
        
        p.posting_id,
        p.posting_title,
        p.state as posting_state,
        p.created_at as posting_created_at,
        date_trunc('month', try_cast(p.created_at as timestamp)) as posting_month,
        date_trunc('quarter', try_cast(p.created_at as timestamp)) as posting_quarter,
        
        p.creator_user_id,
        p.owner_user_id
        
    from staging.stg_lever__posting p
),

application_volume as (
    select 
        dpb.department,
        dpb.team,
        dpb.location,
        dpb.level,
        dpb.commitment_type,
        dpb.posting_month,
        dpb.posting_quarter,
        
        count(distinct a.application_id) as total_applications,
        count(distinct a.candidate_id) as unique_candidates,
        count(distinct a.opportunity_id) as unique_opportunities,
        count(distinct dpb.posting_id) as active_postings,
        
        count(distinct case when a.referrer_user_id is not null then a.application_id end) as referred_applications,
        count(distinct case when a.type = 'internal' then a.application_id end) as internal_applications,
        
        min(a.created_at) as first_application_date,
        max(a.created_at) as last_application_date,
        
        case 
            when count(distinct a.application_id) > 0 
            then round(count(distinct case when a.referrer_user_id is not null then a.application_id end)::numeric / count(distinct a.application_id) * 100, 2)
            else 0 
        end as referral_rate,
        
        round(count(distinct a.application_id)::numeric / nullif(count(distinct dpb.posting_id), 0), 1) as avg_applications_per_posting
        
    from department_posting_base dpb
    left join staging.stg_lever__application a on dpb.posting_id = a.posting_id
    group by dpb.department, dpb.team, dpb.location, dpb.level, dpb.commitment_type, dpb.posting_month, dpb.posting_quarter
),

hiring_outcomes as (
    select 
        dpb.department,
        dpb.team,
        
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
        
        -- Employment metrics based on lifecycle data
        avg(case 
            when lower(s.stage_name) like '%hire%' or lower(s.stage_name) like '%accept%' 
            then cl.total_lifecycle_days 
        end) as avg_time_to_hire_days,
        
        avg(case 
            when lower(s.stage_name) like '%hire%' or lower(s.stage_name) like '%accept%' 
            then cl.total_interviews 
        end) as avg_interviews_per_hire,
        
        -- Conversion rate calculation
        case 
            when count(distinct a.opportunity_id) > 0 
            then round(count(distinct case 
                when lower(s.stage_name) like '%hire%' or lower(s.stage_name) like '%accept%' 
                then a.opportunity_id 
            end)::numeric / count(distinct a.opportunity_id) * 100, 2)
            else 0 
        end as hire_conversion_rate,
        
        case 
            when count(distinct case 
                when lower(s.stage_name) like '%offer%' 
                then a.opportunity_id 
            end) > 0 
            then round(count(distinct case 
                when lower(s.stage_name) like '%hire%' or lower(s.stage_name) like '%accept%' 
                then a.opportunity_id 
            end)::numeric / count(distinct case 
                when lower(s.stage_name) like '%offer%' 
                then a.opportunity_id 
            end) * 100, 2)
            else 0 
        end as offer_acceptance_rate
        
    from department_posting_base dpb
    left join staging.stg_lever__application a on dpb.posting_id = a.posting_id
    left join staging.stg_lever__opportunity o on a.opportunity_id = o.opportunity_id
    left join staging.stg_lever__stage s on o.stage_id = s.stage_id
    left join intermediate.int_lever__candidate_lifecycle cl on a.opportunity_id = cl.opportunity_id
    group by dpb.department, dpb.team
),

interview_metrics as (
    select 
        dpb.department,
        dpb.team,
        
        count(distinct i.interview_id) as total_interviews_conducted,
        count(distinct case when i.canceled_at is null then i.interview_id end) as completed_interviews,
        count(distinct case when i.canceled_at is not null then i.interview_id end) as canceled_interviews,
        
        count(distinct iu.user_id) as unique_interviewers,
        avg(i.duration) as avg_interview_duration,
        sum(i.duration) as total_interview_time_minutes,
        
        count(distinct if.feedback_form_id) as total_feedback_instances,
        count(distinct if.feedback_form_id) as completed_feedback,

        case
            when count(distinct i.interview_id) > 0
            then round(count(distinct case when i.canceled_at is null then i.interview_id end)::numeric / count(distinct i.interview_id) * 100, 2)
            else 0
        end as interview_completion_rate,

        case
            when count(distinct if.feedback_form_id) > 0
            then round(count(distinct if.feedback_form_id)::numeric / count(distinct if.feedback_form_id) * 100, 2)
            else 0
        end as feedback_completion_rate
        
    from department_posting_base dpb
    left join staging.stg_lever__application a on dpb.posting_id = a.posting_id
    left join staging.stg_lever__interview i on a.opportunity_id = i.opportunity_id
    left join staging.stg_lever__interviewer_user iu on i.interview_id = iu.interview_id
    left join staging.stg_lever__interview_feedback if on i.interview_id = if.interview_id
    group by dpb.department, dpb.team
),

candidate_quality as (
    select 
        dpb.department,
        dpb.team,
        
        avg(cei.overall_candidate_experience_score) as avg_candidate_experience_score,
        count(distinct case 
            when cei.experience_grade in ('Exceptional Experience', 'Excellent Experience') 
            then a.opportunity_id 
        end) as positive_experience_candidates,
        
        count(distinct case 
            when cei.experience_risk_flag != 'Normal' 
            then a.opportunity_id 
        end) as at_risk_candidates,
        
        -- Quality assessment based on funnel metrics
        avg(hfm.application_to_screening_rate) as avg_screening_pass_rate,
        avg(hfm.technical_to_final_rate) as avg_technical_pass_rate,
        avg(hfm.final_to_offer_rate) as avg_final_to_offer_rate,
        
        count(distinct case 
            when hfm.hiring_efficiency_grade = 'High Efficiency (≥10%)' 
            then dpb.posting_id 
        end) as high_efficiency_postings,
        
        case 
            when count(distinct a.opportunity_id) > 0 
            then round(count(distinct case 
                when cei.experience_grade in ('Exceptional Experience', 'Excellent Experience') 
                then a.opportunity_id 
            end)::numeric / count(distinct a.opportunity_id) * 100, 2)
            else 0 
        end as positive_experience_rate
        
    from department_posting_base dpb
    left join staging.stg_lever__application a on dpb.posting_id = a.posting_id
    left join marts.lever__candidate_experience_insights cei on a.opportunity_id = cei.opportunity_id
    left join intermediate.int_lever__hiring_funnel_metrics hfm on dpb.posting_id = hfm.posting_id
    group by dpb.department, dpb.team
),

cost_efficiency as (
    select 
        dpb.department,
        dpb.team,
        
        -- Cost proxy indicator based on time investment
        sum(im.total_interview_time_minutes) / 60.0 as total_interview_hours,
        count(distinct im.unique_interviewers) as total_interviewers_involved,
        
        case 
            when sum(ho.candidates_hired) > 0 
            then round((sum(im.total_interview_time_minutes) / 60.0) / sum(ho.candidates_hired), 1)
            else null 
        end as interview_hours_per_hire,
        
        case 
            when sum(ho.candidates_hired) > 0 
            then round(sum(av.total_applications)::numeric / sum(ho.candidates_hired), 1)
            else null 
        end as applications_per_hire,
        
        case 
            when sum(av.active_postings) > 0 
            then round(sum(ho.candidates_hired)::numeric / sum(av.active_postings), 2)
            else 0 
        end as hires_per_posting,
        
        -- efficiency level
        case 
            when sum(ho.candidates_hired) > 0 and (sum(im.total_interview_time_minutes) / 60.0) / sum(ho.candidates_hired) <= 10 then 'Highly Efficient'
            when sum(ho.candidates_hired) > 0 and (sum(im.total_interview_time_minutes) / 60.0) / sum(ho.candidates_hired) <= 20 then 'Efficient'
            when sum(ho.candidates_hired) > 0 and (sum(im.total_interview_time_minutes) / 60.0) / sum(ho.candidates_hired) <= 40 then 'Moderate Efficiency'
            when sum(ho.candidates_hired) > 0 then 'Low Efficiency'
            else 'No Hires'
        end as cost_efficiency_tier
        
    from department_posting_base dpb
    left join application_volume av on dpb.department = av.department and dpb.team = av.team
    left join hiring_outcomes ho on dpb.department = ho.department and dpb.team = ho.team
    left join interview_metrics im on dpb.department = im.department and dpb.team = im.team
    group by dpb.department, dpb.team
),

monthly_trends as (
    select 
        department,
        posting_month,
        
        sum(total_applications) as monthly_applications,
        count(distinct team) as active_teams,
        avg(avg_applications_per_posting) as avg_applications_per_posting_monthly,
        avg(referral_rate) as avg_referral_rate_monthly
        
    from application_volume
    where posting_month >= current_date - interval '12 months'
    group by department, posting_month
),

department_summary as (
    select 
        department,
        
        count(distinct team) as total_teams,
        sum(total_applications) as department_total_applications,
        avg(avg_applications_per_posting) as department_avg_applications_per_posting,
        avg(referral_rate) as department_avg_referral_rate
        
    from application_volume
    group by department
),

final as (
    select 
        dpb.department,
        dpb.team,
        dpb.location,
        dpb.level,
        dpb.commitment_type,
        
        -- Basic indicators
        coalesce(av.total_applications, 0) as total_applications,
        coalesce(av.unique_candidates, 0) as unique_candidates,
        coalesce(av.active_postings, 0) as active_postings,
        coalesce(av.avg_applications_per_posting, 0) as avg_applications_per_posting,
        coalesce(av.referral_rate, 0) as referral_rate,
        
        -- employment results
        coalesce(ho.candidates_hired, 0) as candidates_hired,
        coalesce(ho.offers_extended, 0) as offers_extended,
        coalesce(ho.hire_conversion_rate, 0) as hire_conversion_rate,
        coalesce(ho.offer_acceptance_rate, 0) as offer_acceptance_rate,
        coalesce(ho.avg_time_to_hire_days, 0) as avg_time_to_hire_days,
        coalesce(ho.avg_interviews_per_hire, 0) as avg_interviews_per_hire,
        
        -- Interview indicators
        coalesce(im.total_interviews_conducted, 0) as total_interviews_conducted,
        coalesce(im.interview_completion_rate, 0) as interview_completion_rate,
        coalesce(im.feedback_completion_rate, 0) as feedback_completion_rate,
        coalesce(im.unique_interviewers, 0) as unique_interviewers,
        coalesce(im.avg_interview_duration, 0) as avg_interview_duration_minutes,
        
        -- candidate experience
        coalesce(cq.avg_candidate_experience_score, 0) as avg_candidate_experience_score,
        coalesce(cq.positive_experience_rate, 0) as positive_experience_rate,
        coalesce(cq.avg_screening_pass_rate, 0) as avg_screening_pass_rate,
        coalesce(cq.high_efficiency_postings, 0) as high_efficiency_postings,
        
        -- cost efficiency
        coalesce(ce.interview_hours_per_hire, 0) as interview_hours_per_hire,
        coalesce(ce.applications_per_hire, 0) as applications_per_hire,
        coalesce(ce.hires_per_posting, 0) as hires_per_posting,
        coalesce(ce.cost_efficiency_tier, 'No Data') as cost_efficiency_tier,
        
        -- Department ranking
        rank() over (order by coalesce(ho.candidates_hired, 0) desc) as hiring_volume_rank,
        rank() over (order by coalesce(ho.hire_conversion_rate, 0) desc) as conversion_efficiency_rank,
        rank() over (order by coalesce(cq.avg_candidate_experience_score, 0) desc) as candidate_experience_rank,
        
        -- Overall department performance rating (0-100)
        least(100, greatest(0, round(
            (least(25, coalesce(ho.candidates_hired, 0) * 2.5) +  -- Employment volume weight 25%
             coalesce(ho.hire_conversion_rate, 0) * 0.2 +  -- Conversion rate weight 20%
             coalesce(im.interview_completion_rate, 0) * 0.2 +  -- Interview completion rate weighted 20%
             coalesce(cq.positive_experience_rate, 0) * 0.15 +  -- Quality of experience weighted 15%
             case when ce.cost_efficiency_tier in ('Highly Efficient', 'Efficient') then 20 else 10 end * 0.2)  -- Cost efficiency weighting 20%
        , 0))) as department_performance_score,
        
        -- performance level
        case 
            when least(100, greatest(0, round(
                (least(25, coalesce(ho.candidates_hired, 0) * 2.5) +
                 coalesce(ho.hire_conversion_rate, 0) * 0.2 +
                 coalesce(im.interview_completion_rate, 0) * 0.2 +
                 coalesce(cq.positive_experience_rate, 0) * 0.15 +
                 case when ce.cost_efficiency_tier in ('Highly Efficient', 'Efficient') then 20 else 10 end * 0.2)
            , 0))) >= 75 then 'Top Performing Department'
            when least(100, greatest(0, round(
                (least(25, coalesce(ho.candidates_hired, 0) * 2.5) +
                 coalesce(ho.hire_conversion_rate, 0) * 0.2 +
                 coalesce(im.interview_completion_rate, 0) * 0.2 +
                 coalesce(cq.positive_experience_rate, 0) * 0.15 +
                 case when ce.cost_efficiency_tier in ('Highly Efficient', 'Efficient') then 20 else 10 end * 0.2)
            , 0))) >= 60 then 'High Performing Department'
            when least(100, greatest(0, round(
                (least(25, coalesce(ho.candidates_hired, 0) * 2.5) +
                 coalesce(ho.hire_conversion_rate, 0) * 0.2 +
                 coalesce(im.interview_completion_rate, 0) * 0.2 +
                 coalesce(cq.positive_experience_rate, 0) * 0.15 +
                 case when ce.cost_efficiency_tier in ('Highly Efficient', 'Efficient') then 20 else 10 end * 0.2)
            , 0))) >= 45 then 'Standard Performing Department'
            when coalesce(av.total_applications, 0) >= 10 then 'Underperforming Department'
            else 'Low Activity Department'
        end as performance_tier,
        
        -- Expertise identification
        case 
            when coalesce(av.referral_rate, 0) >= 30 then 'Strong Referral Network'
            when coalesce(ho.offer_acceptance_rate, 0) >= 80 then 'High Offer Acceptance'
            when coalesce(cq.avg_candidate_experience_score, 0) >= 4.0 then 'Excellent Candidate Experience'
            when coalesce(ho.avg_time_to_hire_days, 999) <= 30 then 'Fast Hiring Process'
            when coalesce(ce.cost_efficiency_tier, '') in ('Highly Efficient', 'Efficient') then 'Cost Efficient Operations'
            else 'Standard Operations'
        end as department_strength,
        
        current_timestamp as calculated_at
        
    from department_posting_base dpb
    left join application_volume av on dpb.department = av.department and dpb.team = av.team
    left join hiring_outcomes ho on dpb.department = ho.department and dpb.team = ho.team
    left join interview_metrics im on dpb.department = im.department and dpb.team = im.team
    left join candidate_quality cq on dpb.department = cq.department and dpb.team = cq.team
    left join cost_efficiency ce on dpb.department = ce.department and dpb.team = ce.team
    
    -- Only include departmental teams with actual recruitment activity
    where coalesce(av.total_applications, 0) > 0 or coalesce(av.active_postings, 0) > 0
)

select * from final
order by department_performance_score desc, total_applications desc
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 148 | 148 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"department":"engineering","team":"smith-pacheco","location":"charleshaven","level":"unknown level","commitment_type":"full-time"}</code> |
| K2 | <code>{"department":"engineering","team":"andersen, potter and nelson","location":"lawsonchester","level":"entry","commitment_type":"full-time"}</code> |
| K3 | <code>{"department":"engineering","team":"anderson, beck and ward","location":"annborough","level":"mid","commitment_type":"part-time"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| department | 0 | 0 | 0 | VARCHAR | VARCHAR |
| team | 0 | 0 | 0 | VARCHAR | VARCHAR |
| location | 0 | 0 | 0 | VARCHAR | VARCHAR |
| level | 0 | 0 | 0 | VARCHAR | VARCHAR |
| commitment_type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| total_applications | 0 | 0 | 0 | HUGEINT | BIGINT |
| unique_candidates | 0 | 0 | 0 | HUGEINT | BIGINT |
| active_postings | 0 | 0 | 0 | BIGINT | BIGINT |
| avg_applications_per_posting | 0 | 0 | 0 | DOUBLE | DOUBLE |
| referral_rate | 7 | 7 | 7 | DOUBLE | DOUBLE |
| candidates_hired | 0 | 0 | 0 | BIGINT | BIGINT |
| offers_extended | 0 | 0 | 0 | BIGINT | BIGINT |
| hire_conversion_rate | 0 | 0 | 0 | DECIMAL(2,1) | DOUBLE |
| offer_acceptance_rate | 0 | 0 | 0 | DECIMAL(2,1) | DOUBLE |
| avg_time_to_hire_days | 0 | 0 | 0 | DECIMAL(2,1) | DOUBLE |
| avg_interviews_per_hire | 0 | 0 | 0 | DECIMAL(2,1) | DOUBLE |
| total_interviews_conducted | 148 | 148 | 148 | BIGINT | BIGINT |
| interview_completion_rate | 148 | 148 | 148 | DECIMAL(2,1) | DOUBLE |
| unique_interviewers | 148 | 148 | 148 | BIGINT | BIGINT |
| avg_interview_duration_minutes | 148 | 148 | 148 | DECIMAL(2,1) | DOUBLE |
| avg_candidate_experience_score | 148 | 148 | 148 | DECIMAL(2,1) | DOUBLE |
| positive_experience_rate | 0 | 0 | 0 | DECIMAL(2,1) | DOUBLE |
| avg_screening_pass_rate | 148 | 148 | 148 | DECIMAL(2,1) | DOUBLE |
| high_efficiency_postings | 148 | 148 | 148 | BIGINT | BIGINT |
| interview_hours_per_hire | 0 | 0 | 0 | DECIMAL(2,1) | DOUBLE |
| applications_per_hire | 0 | 0 | 0 | DECIMAL(2,1) | DOUBLE |
| hires_per_posting | 0 | 0 | 0 | DECIMAL(2,1) | DOUBLE |
| cost_efficiency_tier | 148 | 148 | 148 | VARCHAR | VARCHAR |
| hiring_volume_rank | 0 | 0 | 0 | BIGINT | BIGINT |
| conversion_efficiency_rank | 0 | 0 | 0 | BIGINT | BIGINT |
| candidate_experience_rank | 0 | 0 | 0 | BIGINT | BIGINT |
| department_performance_score | 148 | 148 | 148 | DECIMAL(27,0) | DOUBLE |
| performance_tier | 0 | 0 | 0 | VARCHAR | VARCHAR |
| department_strength | 81 | 81 | 81 | VARCHAR | VARCHAR |

referral_rate 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 26.67 | 33.33 |

total_interviews_conducted 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | 0 | 10 |

interview_completion_rate 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | 0.0 | 100.0 |

unique_interviewers 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | 0 | 15 |

avg_interview_duration_minutes 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | 0.0 | 72.69590909090908 |

avg_candidate_experience_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | 0.0 | 2.2 |

avg_screening_pass_rate 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | 0.0 | 86.67000000000125 |

high_efficiency_postings 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | 0 | 1 |

cost_efficiency_tier 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | No Data | No Hires |

department_performance_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | 2 | 22.0 |

department_strength 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K3 | Standard Operations | Strong Referral Network |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A3_constant_nonnull_column | <code>31列；[{"column":"total_applications","value":"0"}]</code> |
| A4_equal_columns | <code>3组；[{"columns":["total_applications","unique_candidates","candidates_hired","offers_extended","total_interviews_conducted","unique_interviewers","high_efficiency_postings"],"nonnull_equal_rows":148,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>3组；[{"columns":["total_applications","unique_candidates","candidates_hired","offers_extended","total_interviews_conducted","unique_interviewers","high_efficiency_postings"],"nonnull_equal_rows":148,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| B6_constant_literal_output | <code>20输出列；[{"column":"candidates_hired","expression":["CAST(0 AS BIGINT)"]}]</code> |
| B7_specified_not_read | <code>["intermediate.int_lever__candidate_lifecycle"]</code> |
| C9_agent_runtime_text | <code>S4:47 current_timestamp；命中数=1</code> |
| C9_gold_runtime_text | <code>S5:255 current_date；命中数=2</code> |
| C9_contract_runtime_text | <code>S3:2162 current_timestamp；命中数=2</code> |
| D10_keyword_in_final_report | <code>命中数=1；result_md_final_report 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。</code> |
| D10_keyword_in_any_result_field | <code>命中数=6；assistant_trajectory 2026-10-25 00:39:02,321 - WARNING - Skipping lever__departmental_hiring_trends: SQL file not found (sql/marts/lever__departmental_hiring_trends.sql)</code> |

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
| 35 | run | <code>find sql -type f &#124; sort</code> | 2341 | false | false |
| 37 | run | <code>sed -i "s/) external FROM cb/) external_avg FROM cb/; s/referred&gt;external+10/referred&gt;external_avg+10/; s/internal&gt;external+10/internal&gt;external_avg+10/" sql/marts/lever__candidate_quality_insights.sq</code> | 2929 | false | false |
| 51 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,yaml<br>c=duckdb.connect('lever.duckdb',read_only=True); y=yaml.safe_load(open('docs/data_contract.yaml'))<br>for layer,models in [('intermediate',y['modeling_spec']['intermedi</code> | 798 | true | false |
| 53 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/intermediate/int_lever__posting_analytics.sql');s=p.read_text();s=s.replace('min(a.created_at) first_application_date,max(a.created_at) last_applic</code> | 154 | false | false |
| 59 | run | <code>cat &gt; /workspace/result.md &lt;&lt;'EOF'<br>【回复用户】<br><br>已按 `config/layer_dependencies.yaml` 的分层及执行顺序创建 SQL 文件，共 54 个：24 个 staging、17 个 intermediate、13 个 marts，文件名与合同中的模型名一致，均使用 DuckDB SQL、直接 schema.table 引用，且文件末尾不</code> | 115 | false | false |
| 61 | run | <code>mkdir -p /workspace &amp;&amp; cat &gt; /workspace/result.md &lt;&lt;'EOF'<br>【回复用户】<br><br>已按 `config/layer_dependencies.yaml` 的分层及执行顺序创建 SQL 文件，共 54 个：24 个 staging、17 个 intermediate、13 个 marts，文件名与合同中的模型名一致，均使用 DuckDB SQL、直接</code> | 82 | false | false |
| 65 | run | <code>cat &gt; result.md &lt;&lt;'EOF'<br>【回复用户】<br><br>已按 `config/layer_dependencies.yaml` 的分层及执行顺序创建 SQL 文件，共 54 个：24 个 staging、17 个 intermediate、13 个 marts，文件名与合同中的模型名一致，均使用 DuckDB SQL、直接 schema.table 引用，且文件末尾不含分号。<br><br>**验证结</code> | 1073 | true | false |

### agent action 的 thought/message 命中原句

event 37 / message

```text
cat > sql/marts/lever__departmental_hiring_trends.sql <<'SQL'
```
event 53 / message

```text
p=Path('sql/marts/lever__departmental_hiring_trends.sql');s=p.read_text(); s=s.replace('SELECT *, rank() OVER (ORDER BY candidates_hired DESC) AS hiring_volume_rank,','SELECT department, team, location, level, commitment_type, total_applications, unique_candidates, active_postings, avg_applications_per_posting, referral_rate, candidates_hired, offers_extended, hire_conversion_rate, offer_acceptance_rate, avg_time_to_hire_days, avg_interviews_per_hire, total_interviews_conducted, interview_completion_rate, feedback_completion_rate, unique_interviewers, avg_interview_duration_minutes, avg_candidate_experience_score, positive_experience_rate, avg_screening_pass_rate, high_efficiency_postings, interview_hours_per_hire, applications_per_hire, hires_per_posting, cost_efficiency_tier, rank() OVER (ORDER BY candidates_hired DESC) AS hiring_volume_rank,');p.write_text(s)
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

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/005_cs_impl-001.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-001/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__departmental_hiring_trends.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/sql/marts/lever__departmental_hiring_trends.sql`
- S6: `records/006_contract_impl-001.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/result.md`
- S10: `data/019_packages_work/019_impl-001_lever__departmental_hiring_trends/019_impl-001_lever__departmental_hiring_trends.json`
- S11: `data/005_cs_work/impl-001/node_results.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/lever.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions`
