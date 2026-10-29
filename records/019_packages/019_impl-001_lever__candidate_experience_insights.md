# impl-001 | marts | lever__candidate_experience_insights | 差异：S1；日期 2025-10-27

## 契约完整原文

S3:1951–2056

```yaml
    - name: lever__candidate_experience_insights
      description: Candidate experience metrics and scores per opportunity derived from lifecycle, interview, communication, and outcome signals
      grain: One row per opportunity_id
      source_models:
      - intermediate.int_lever__candidate_lifecycle
      - staging.stg_lever__opportunity
      - staging.stg_lever__stage
      - staging.stg_lever__archive_reason
      - intermediate.int_lever__contact_info
      business_logic: 'Build candidate_journey by joining: - intermediate.int_lever__candidate_lifecycle (cl) to staging.stg_lever__opportunity (o) on opportunity_id, left join intermediate.int_lever__contact_info (c) on contact_id, join staging.stg_lever__stage (s) on o.stage_id, and left join staging.stg_lever__archive_reason (ar) on o.archived_reason_id. - Derive fields: - activity_status: constant ''Active''. - lifecycle_speed_category: total_lifecycle_days bucketed as ≤14 ''Fast'', ≤30 ''Standard'', ≤60 ''Slow'', else ''Very Slow''. - interview_completion_rate_pct: completed_interviews divided by total_interviews times 100, rounded to 1 decimal; no explicit zero-division guard; NULLs propagate. - Carry through totals (interviews, completed, canceled), avg_interview_duration_minutes, total_interview_time_minutes, avg_recommendation_score, feedback_completion_rate_pct, is_archived, application_date (o.created_at), last_interaction_at, last_advanced_at, current_stage (s.stage_name), archive_reason (ar.archive_reason_title). Compute communication_quality per opportunity_id: - days_from_application_to_last_contact: difference in days between last_interaction_at and application_date; NULL if either is NULL. - days_from_application_to_last_advancement: difference in days between last_advanced_at and application_date; NULL if either is NULL. - response_quality from days_since_last_advancement: ≤1 ''Excellent Response (≤1 day)''; ≤3 ''Good Response (2-3 days)''; ≤7 ''Moderate Response (4-7 days)''; ≤14 ''Slow Response (8-14 days)''; else ''Very Slow Response (>14 days)'' (NULL falls to the else bucket). - transparency_score from feedback_completion_rate_pct: ≥90→5; ≥70→4; ≥50→3; ≥30→2; else 1 (NULL falls to 1). Compute interview_experience per opportunity_id: - interview_experience_score: - If total_interviews = 0 → NULL. - Else if completion rate ≥95 and avg duration in 30–90 minutes → 5. - Else if completion rate ≥80 and avg duration in 20–120 minutes → 4. - Else if completion rate ≥60 → 3; else if ≥40 → 2; else → 1. - interview_burden_category: - If total_interviews = 0 → ''No Interviews''. - Else if total_interviews ≤2 and total_interview_time_minutes ≤120 → ''Light Process''; ≤4 and ≤240 → ''Standard Process''; ≤6 and ≤360 → ''Intensive Process''; else ''Heavy Process''. - interview_consistency_score: - If total_interviews = 0 → NULL. - Else if canceled_interviews = 0 → 5; else if canceled/total ≤10% → 4; ≤20% → 3; ≤30% → 2; else → 1. Compute outcome_fairness per opportunity_id: - outcome_fairness_score: - If not archived → NULL. - Else 5 for stage indicating hire/accept or reason indicating withdrew/declined; 4 for offer stage or skills/qualification mismatch; 3 for culture fit issues or other; 2 if rejected without a stated reason. - process_completeness_assessment: - If not archived → ''In Progress''; else if avg_recommendation_score ≥4 and stage does not indicate hire → ''Potential Mismatch''; else if avg_recommendation_score ≤2 → ''Consistent Outcome''; else if avg_recommendation_score is NULL → ''Incomplete Process''; else → ''Normal Process''. Compute timeline_experience per opportunity_id: - timeline_experience_score compares lifecycle_speed_category to labels ''Fast Track (≤7 days)'', ''Normal (8-30 days)'', ''Extended (31-60 days)'', ''Long Process (>60 days)''; because candidate_journey uses ''Fast''/''Standard''/''Slow''/''Very Slow'', no label matches and the else branch applies, yielding 1 for all rows. - candidate_anxiety_level from activity_status: ''Active'' maps to ''Low Anxiety''. Final projection and derived fields: - overall_candidate_experience_score: weighted average of subscores (transparency 20%, interview experience 25%, interview consistency 15%, outcome fairness 20%, timeline 20%), defaulting missing subscores to 3, rounded to 1 decimal. - experience_grade from the same rounded overall score: ≥4.5 ''Exceptional Experience''; ≥4.0 ''Excellent Experience''; ≥3.5 ''Good Experience''; ≥3.0 ''Average Experience''; ≥2.0 ''Below Average Experience''; else ''Poor Experience''. - improvement_recommendations: concatenate in this order (each fragment ends with ''; '' and no trimming): if transparency_score ≤2 add ''Improve feedback transparency; ''; if interview_experience_score ≤2 add ''Optimize interview process; ''; if timeline_experience_score ≤2 add ''Accelerate decision timeline; ''; if days_since_last_advancement ≥14 add ''Increase communication frequency; ''. - experience_risk_flag (first match): if days_since_last_advancement ≥21 and not archived → ''High Abandonment Risk''; else if canceled_interviews ≥2 → ''Poor Interview Experience''; else if transparency_score ≤2 and total_interviews ≥3 → ''Low Process Transparency''; else if timeline_experience_score ≤2 and total_lifecycle_days ≥60 → ''Extended Timeline Concern''; else ''Normal''. - calculated_at = current timestamp at model execution. - Final result ordered by overall_candidate_experience_score descending, then total_lifecycle_days ascending.'
      columns:
      - name: opportunity_id
        data_type: VARCHAR
        description: Primary key opportunity identifier; one output row per opportunity_id
        tests:
        - not_null
        - unique
      - name: contact_id
        data_type: VARCHAR
        description: Candidate contact identifier from lifecycle data
        tests:
        - not_null
      - name: contact_name
        data_type: VARCHAR
        description: Candidate name from opportunity data
      - name: current_stage
        data_type: VARCHAR
        description: Current pipeline stage name from stage reference
      - name: application_date
        data_type: TIMESTAMP
        description: Opportunity creation timestamp used as application date
      - name: total_lifecycle_days
        data_type: DOUBLE
        description: Total elapsed days the opportunity has been active
      - name: is_archived
        data_type: INTEGER
        description: Archive status from lifecycle (0=active, 1=archived) used as boolean in case logic
      - name: archive_reason
        data_type: VARCHAR
        description: Archive reason title from archive reason reference; may be NULL
      - name: response_quality
        data_type: VARCHAR
        description: 'Bucket by days_since_last_advancement: ≤1 Excellent, 2–3 Good, 4–7 Moderate, 8–14 Slow, >14 Very Slow; NULLs fall to Very Slow'
      - name: transparency_score
        data_type: INTEGER
        description: '1–5 based on feedback_completion_rate_pct: ≥90→5, ≥70→4, ≥50→3, ≥30→2, else 1; NULLs fall to 1'
      - name: interview_experience_score
        data_type: INTEGER
        description: 1–5 using completion rate and average duration; total_interviews=0→NULL; ≥95% and 30–90min→5; ≥80% and 20–120min→4; ≥60%→3; ≥40%→2; else 1
      - name: interview_burden_category
        data_type: VARCHAR
        description: 'Interview load by count and total time: No Interviews; Light (≤2 and ≤120); Standard (≤4 and ≤240); Intensive (≤6 and ≤360); else Heavy'
      - name: interview_consistency_score
        data_type: INTEGER
        description: 1–5 by cancellation ratio; total_interviews=0→NULL; 0 cancels→5; ≤10%→4; ≤20%→3; ≤30%→2; else 1
      - name: outcome_fairness_score
        data_type: INTEGER
        description: '1–5 only if archived: 5 for hire/accept or withdrew/declined, 4 for offer or skills mismatch, 3 for culture/other, 2 if rejected without reason; active→NULL'
      - name: process_completeness_assessment
        data_type: VARCHAR
        description: 'Assessment: In Progress, Potential Mismatch, Consistent Outcome, Incomplete Process, or Normal Process based on archived status and avg_recommendation_score'
      - name: timeline_experience_score
        data_type: INTEGER
        description: Intended 1–5 from lifecycle speed label comparison; due to label mismatch it defaults to 1 for all rows
      - name: candidate_anxiety_level
        data_type: VARCHAR
        description: Derived from activity_status; constant 'Active' maps to 'Low Anxiety'
      - name: total_interviews
        data_type: INTEGER
        description: Total scheduled interviews from lifecycle data
      - name: interview_completion_rate_pct
        data_type: DOUBLE
        description: Completed_interviews/total_interviews*100 rounded to 1 decimal; no explicit zero-division guard; NULLs propagate
      - name: avg_interview_duration_minutes
        data_type: INTEGER
        description: Average interview duration in minutes from lifecycle data
      - name: feedback_completion_rate_pct
        data_type: INTEGER
        description: Percent of interviews with submitted feedback (integer percent) from lifecycle data
      - name: avg_recommendation_score
        data_type: INTEGER
        description: Average interviewer recommendation (integer scale) from lifecycle data
      - name: days_since_last_advancement
        data_type: DOUBLE
        description: Days since the opportunity last advanced stage from lifecycle data
      - name: days_from_application_to_last_contact
        data_type: DOUBLE
        description: Days between application_date and last_interaction_at; NULL if either timestamp is NULL
      - name: days_from_application_to_last_advancement
        data_type: DOUBLE
        description: Days between application_date and last_advanced_at; NULL if either timestamp is NULL
      - name: overall_candidate_experience_score
        data_type: DECIMAL(17,1)
        description: Weighted subscore average (20% transparency, 25% interview experience, 15% consistency, 20% fairness, 20% timeline), missing subscores default to 3, rounded to 1 decimal
      - name: experience_grade
        data_type: VARCHAR
        description: 'Grade from the rounded overall score: ≥4.5 Exceptional, ≥4.0 Excellent, ≥3.5 Good, ≥3.0 Average, ≥2.0 Below Average, else Poor'
      - name: improvement_recommendations
        data_type: VARCHAR
        description: Concatenation of advisory fragments (fixed order, each ends with '; ') for triggered conditions; empty string if none
      - name: experience_risk_flag
        data_type: VARCHAR
        description: 'Precedence: High Abandonment Risk, Poor Interview Experience, Low Process Transparency, Extended Timeline Concern, else Normal'
      - name: calculated_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Execution timestamp set at model run time
```

## agent 最终 SQL

S4

```sql
WITH base AS (SELECT cl.*,o.contact_name,o.created_at application_date,o.last_interaction_at,o.last_advanced_at,s.stage_name current_stage,ar.archive_reason_title archive_reason,CASE WHEN cl.total_lifecycle_days<=14 THEN 'Fast' WHEN cl.total_lifecycle_days<=30 THEN 'Standard' WHEN cl.total_lifecycle_days<=60 THEN 'Slow' ELSE 'Very Slow' END lifecycle_speed_category,round(cl.completed_interviews*100.0/nullif(cl.total_interviews,0),1) completion_rate,CASE WHEN cl.feedback_completion_rate_pct>=90 THEN 5 WHEN cl.feedback_completion_rate_pct>=70 THEN 4 WHEN cl.feedback_completion_rate_pct>=50 THEN 3 WHEN cl.feedback_completion_rate_pct>=30 THEN 2 ELSE 1 END transparency_score,CASE WHEN cl.total_interviews=0 THEN NULL WHEN cl.completed_interviews*100.0/nullif(cl.total_interviews,0)>=95 AND cl.avg_interview_duration_minutes BETWEEN 30 AND 90 THEN 5 WHEN cl.completed_interviews*100.0/nullif(cl.total_interviews,0)>=80 AND cl.avg_interview_duration_minutes BETWEEN 20 AND 120 THEN 4 WHEN cl.completed_interviews*100.0/nullif(cl.total_interviews,0)>=60 THEN 3 WHEN cl.completed_interviews*100.0/nullif(cl.total_interviews,0)>=40 THEN 2 ELSE 1 END interview_experience_score,CASE WHEN cl.total_interviews=0 THEN NULL WHEN cl.canceled_interviews=0 THEN 5 WHEN cl.canceled_interviews*1.0/cl.total_interviews<=.1 THEN 4 WHEN cl.canceled_interviews*1.0/cl.total_interviews<=.2 THEN 3 WHEN cl.canceled_interviews*1.0/cl.total_interviews<=.3 THEN 2 ELSE 1 END interview_consistency_score FROM intermediate.int_lever__candidate_lifecycle cl JOIN staging.stg_lever__opportunity o USING(opportunity_id) LEFT JOIN staging.stg_lever__stage s ON o.stage_id=s.stage_id LEFT JOIN staging.stg_lever__archive_reason ar ON o.archived_reason_id=ar.archive_reason_id), calc AS (SELECT *,date_diff('microsecond',application_date,last_interaction_at)/86400000000.0 days_contact,date_diff('microsecond',application_date,last_advanced_at)/86400000000.0 days_advance,CASE WHEN is_archived=0 THEN NULL WHEN lower(coalesce(current_stage,'')) LIKE '%hire%' OR lower(coalesce(current_stage,'')) LIKE '%accept%' OR lower(coalesce(archive_reason,'')) LIKE '%withdraw%' OR lower(coalesce(archive_reason,'')) LIKE '%declin%' THEN 5 WHEN lower(coalesce(current_stage,'')) LIKE '%offer%' OR lower(coalesce(archive_reason,'')) LIKE '%skill%' OR lower(coalesce(archive_reason,'')) LIKE '%qualification%' THEN 4 WHEN archive_reason IS NULL THEN 2 ELSE 3 END outcome_fairness_score FROM base) SELECT opportunity_id,contact_id,contact_name,current_stage,application_date,total_lifecycle_days,is_archived,archive_reason,CASE WHEN days_since_last_advancement<=1 THEN 'Excellent Response (≤1 day)' WHEN days_since_last_advancement<=3 THEN 'Good Response (2-3 days)' WHEN days_since_last_advancement<=7 THEN 'Moderate Response (4-7 days)' WHEN days_since_last_advancement<=14 THEN 'Slow Response (8-14 days)' ELSE 'Very Slow Response (>14 days)' END response_quality,transparency_score,interview_experience_score,CASE WHEN total_interviews=0 THEN 'No Interviews' WHEN total_interviews<=2 AND total_interview_time_minutes<=120 THEN 'Light Process' WHEN total_interviews<=4 AND total_interview_time_minutes<=240 THEN 'Standard Process' WHEN total_interviews<=6 AND total_interview_time_minutes<=360 THEN 'Intensive Process' ELSE 'Heavy Process' END interview_burden_category,interview_consistency_score,outcome_fairness_score,CASE WHEN is_archived=0 THEN 'In Progress' WHEN avg_recommendation_score>=4 AND lower(coalesce(current_stage,'')) NOT LIKE '%hire%' THEN 'Potential Mismatch' WHEN avg_recommendation_score<=2 THEN 'Consistent Outcome' WHEN avg_recommendation_score IS NULL THEN 'Incomplete Process' ELSE 'Normal Process' END process_completeness_assessment,1::INTEGER timeline_experience_score,'Low Anxiety' candidate_anxiety_level,total_interviews,completion_rate interview_completion_rate_pct,avg_interview_duration_minutes,feedback_completion_rate_pct,avg_recommendation_score,days_since_last_advancement,days_contact days_from_application_to_last_contact,days_advance days_from_application_to_last_advancement,round((coalesce(transparency_score,3)*.2+coalesce(interview_experience_score,3)*.25+coalesce(interview_consistency_score,3)*.15+coalesce(outcome_fairness_score,3)*.2+3*.2),1) overall_candidate_experience_score,CASE WHEN round((coalesce(transparency_score,3)*.2+coalesce(interview_experience_score,3)*.25+coalesce(interview_consistency_score,3)*.15+coalesce(outcome_fairness_score,3)*.2+3*.2),1)>=4.5 THEN 'Exceptional Experience' WHEN round((coalesce(transparency_score,3)*.2+coalesce(interview_experience_score,3)*.25+coalesce(interview_consistency_score,3)*.15+coalesce(outcome_fairness_score,3)*.2+3*.2),1)>=4 THEN 'Excellent Experience' WHEN round((coalesce(transparency_score,3)*.2+coalesce(interview_experience_score,3)*.25+coalesce(interview_consistency_score,3)*.15+coalesce(outcome_fairness_score,3)*.2+3*.2),1)>=3.5 THEN 'Good Experience' WHEN round((coalesce(transparency_score,3)*.2+coalesce(interview_experience_score,3)*.25+coalesce(interview_consistency_score,3)*.15+coalesce(outcome_fairness_score,3)*.2+3*.2),1)>=3 THEN 'Average Experience' WHEN round((coalesce(transparency_score,3)*.2+coalesce(interview_experience_score,3)*.25+coalesce(interview_consistency_score,3)*.15+coalesce(outcome_fairness_score,3)*.2+3*.2),1)>=2 THEN 'Below Average Experience' ELSE 'Poor Experience' END experience_grade,'' improvement_recommendations,CASE WHEN days_since_last_advancement>=21 AND is_archived=0 THEN 'High Abandonment Risk' WHEN canceled_interviews>=2 THEN 'Poor Interview Experience' WHEN transparency_score<=2 AND total_interviews>=3 THEN 'Low Process Transparency' WHEN total_lifecycle_days>=60 THEN 'Extended Timeline Concern' ELSE 'Normal' END experience_risk_flag,current_timestamp calculated_at FROM calc
```

## gold SQL（仅供定位差异）

S5

```sql
-- Candidate experience insight analysis table
-- Analyze user experience and satisfaction metrics of the recruitment process from the candidate's perspective

with candidate_journey as (
    select
        cl.opportunity_id,
        cl.contact_id,
        o.contact_name,
        cl.total_lifecycle_days,
        cl.days_since_last_advancement,
        'Active' as activity_status,
        case
            when cl.total_lifecycle_days <= 14 then 'Fast'
            when cl.total_lifecycle_days <= 30 then 'Standard'
            when cl.total_lifecycle_days <= 60 then 'Slow'
            else 'Very Slow'
        end as lifecycle_speed_category,
        cl.total_interviews,
        cl.completed_interviews,
        cl.canceled_interviews,
        round(cl.completed_interviews::numeric / cl.total_interviews * 100, 1) as interview_completion_rate_pct,
        cl.avg_interview_duration_minutes,
        cl.total_interview_time_minutes,
        cl.avg_recommendation_score,
        cl.feedback_completion_rate_pct,
        cl.is_archived,
        
        o.created_at as application_date,
        o.last_interaction_at,
        o.last_advanced_at,
        o.archived_at,
        o.archived_reason_id,
        
        s.stage_name as current_stage,
        ar.archive_reason_title as archive_reason
        
    from intermediate.int_lever__candidate_lifecycle cl
    join staging.stg_lever__opportunity o on cl.opportunity_id = o.opportunity_id
    left join intermediate.int_lever__contact_info c on cl.contact_id = c.contact_id
    join staging.stg_lever__stage s on o.stage_id = s.stage_id
    left join staging.stg_lever__archive_reason ar on o.archived_reason_id = ar.archive_reason_id
),

communication_quality as (
    select 
        cj.opportunity_id,
        cj.contact_id,
        
        -- Communication frequency analysis
        case
            when cj.last_interaction_at is not null and cj.application_date is not null
            then extract(epoch from (try_cast(cj.last_interaction_at as timestamp) - try_cast(cj.application_date as timestamp))) / 86400.0
            else null
        end as days_from_application_to_last_contact,
        
        case
            when cj.last_advanced_at is not null and cj.application_date is not null
            then extract(epoch from (try_cast(cj.last_advanced_at as timestamp) - try_cast(cj.application_date as timestamp))) / 86400.0
            else null 
        end as days_from_application_to_last_advancement,
        
        -- responsiveness assessment
        case 
            when cj.days_since_last_advancement <= 1 then 'Excellent Response (≤1 day)'
            when cj.days_since_last_advancement <= 3 then 'Good Response (2-3 days)'
            when cj.days_since_last_advancement <= 7 then 'Moderate Response (4-7 days)'
            when cj.days_since_last_advancement <= 14 then 'Slow Response (8-14 days)'
            else 'Very Slow Response (>14 days)'
        end as response_quality,
        
        -- Process transparency score
        case 
            when cj.feedback_completion_rate_pct >= 90 then 5  -- very transparent
            when cj.feedback_completion_rate_pct >= 70 then 4  -- more transparent
            when cj.feedback_completion_rate_pct >= 50 then 3  -- generally
            when cj.feedback_completion_rate_pct >= 30 then 2  -- Less opaque
            else 1  -- opaque
        end as transparency_score
        
    from candidate_journey cj
),

interview_experience as (
    select 
        cj.opportunity_id,
        
        -- Interview experience rating
        case 
            when cj.total_interviews = 0 then null
            when cj.interview_completion_rate_pct >= 95 and cj.avg_interview_duration_minutes between 30 and 90 then 5  -- excellent
            when cj.interview_completion_rate_pct >= 80 and cj.avg_interview_duration_minutes between 20 and 120 then 4  -- good
            when cj.interview_completion_rate_pct >= 60 then 3  -- generally
            when cj.interview_completion_rate_pct >= 40 then 2  -- Poor
            else 1  -- Very bad
        end as interview_experience_score,
        
        -- Interview Burden Assessment
        case 
            when cj.total_interviews = 0 then 'No Interviews'
            when cj.total_interviews <= 2 and cj.total_interview_time_minutes <= 120 then 'Light Process'
            when cj.total_interviews <= 4 and cj.total_interview_time_minutes <= 240 then 'Standard Process'
            when cj.total_interviews <= 6 and cj.total_interview_time_minutes <= 360 then 'Intensive Process'
            else 'Heavy Process'
        end as interview_burden_category,
        
        -- Interview consistency (based on cancellation rate)
        case 
            when cj.total_interviews = 0 then null
            when cj.canceled_interviews = 0 then 5  -- completely consistent
            when cj.canceled_interviews::numeric / cj.total_interviews <= 0.1 then 4  -- Highly consistent
            when cj.canceled_interviews::numeric / cj.total_interviews <= 0.2 then 3  -- Generally consistent
            when cj.canceled_interviews::numeric / cj.total_interviews <= 0.3 then 2  -- less consistent
            else 1  -- Very inconsistent
        end as interview_consistency_score
        
    from candidate_journey cj
),

outcome_fairness as (
    select 
        cj.opportunity_id,
        cj.archive_reason,
        
        -- Outcome fairness assessment
        case 
            when cj.is_archived = false then null  -- The process is not over yet
            when lower(cj.current_stage) like '%hire%' or lower(cj.current_stage) like '%accept%' then 5  -- successful hire
            when lower(cj.current_stage) like '%offer%' then 4  -- Receive an offer
            when cj.archive_reason is null then 2  -- Rejected without clear reason
            when lower(cj.archive_reason) like '%qualif%' or lower(cj.archive_reason) like '%skill%' then 4  -- Skills mismatch, reasonable
            when lower(cj.archive_reason) like '%culture%' or lower(cj.archive_reason) like '%fit%' then 3  -- cultural fit issues
            when lower(cj.archive_reason) like '%withdrew%' or lower(cj.archive_reason) like '%decline%' then 5  -- Candidate withdraws voluntarily
            else 3  -- other reasons
        end as outcome_fairness_score,
        
        -- process integrity
        case 
            when cj.is_archived = false then 'In Progress'
            when cj.avg_recommendation_score >= 4 and cj.is_archived = true and lower(cj.current_stage) not like '%hire%' then 'Potential Mismatch'
            when cj.avg_recommendation_score <= 2 and cj.is_archived = true then 'Consistent Outcome'
            when cj.avg_recommendation_score is null and cj.is_archived = true then 'Incomplete Process'
            else 'Normal Process'
        end as process_completeness_assessment
        
    from candidate_journey cj
),

timeline_experience as (
    select 
        cj.opportunity_id,
        
        -- Time experience rating
        case 
            when cj.lifecycle_speed_category = 'Fast Track (≤7 days)' then 5
            when cj.lifecycle_speed_category = 'Normal (8-30 days)' then 4
            when cj.lifecycle_speed_category = 'Extended (31-60 days)' then 3
            when cj.lifecycle_speed_category = 'Long Process (>60 days)' then 2
            else 1
        end as timeline_experience_score,
        
        -- Waiting for anxiety level assessment
        case 
            when cj.activity_status = 'Very Active' then 'Very Low Anxiety'
            when cj.activity_status = 'Active' then 'Low Anxiety'
            when cj.activity_status = 'Moderately Active' then 'Moderate Anxiety'
            when cj.activity_status = 'Low Activity' then 'High Anxiety'
            when cj.activity_status = 'Stale' then 'Very High Anxiety'
            else 'Unknown'
        end as candidate_anxiety_level
        
    from candidate_journey cj
),

final as (
    select 
        cj.opportunity_id,
        cj.contact_id,
        cj.contact_name,
        cj.current_stage,
        cj.application_date,
        cj.total_lifecycle_days,
        cj.is_archived,
        cj.archive_reason,
        
        -- Experience dimension score
        cq.response_quality,
        cq.transparency_score,
        ie.interview_experience_score,
        ie.interview_burden_category,
        ie.interview_consistency_score,
        of.outcome_fairness_score,
        of.process_completeness_assessment,
        te.timeline_experience_score,
        te.candidate_anxiety_level,
        
        -- Detailed indicators
        cj.total_interviews,
        cj.interview_completion_rate_pct,
        cj.avg_interview_duration_minutes,
        cj.feedback_completion_rate_pct,
        cj.avg_recommendation_score,
        cj.days_since_last_advancement,
        cq.days_from_application_to_last_contact,
        cq.days_from_application_to_last_advancement,
        
        -- Overall candidate experience rating (1-5 point scale)
        round(
            (coalesce(cq.transparency_score, 3) * 0.2 +
             coalesce(ie.interview_experience_score, 3) * 0.25 +
             coalesce(ie.interview_consistency_score, 3) * 0.15 +
             coalesce(of.outcome_fairness_score, 3) * 0.2 +
             coalesce(te.timeline_experience_score, 3) * 0.2)
        , 1) as overall_candidate_experience_score,
        
        -- experience level
        case 
            when round(
                (coalesce(cq.transparency_score, 3) * 0.2 +
                 coalesce(ie.interview_experience_score, 3) * 0.25 +
                 coalesce(ie.interview_consistency_score, 3) * 0.15 +
                 coalesce(of.outcome_fairness_score, 3) * 0.2 +
                 coalesce(te.timeline_experience_score, 3) * 0.2)
            , 1) >= 4.5 then 'Exceptional Experience'
            when round(
                (coalesce(cq.transparency_score, 3) * 0.2 +
                 coalesce(ie.interview_experience_score, 3) * 0.25 +
                 coalesce(ie.interview_consistency_score, 3) * 0.15 +
                 coalesce(of.outcome_fairness_score, 3) * 0.2 +
                 coalesce(te.timeline_experience_score, 3) * 0.2)
            , 1) >= 4.0 then 'Excellent Experience'
            when round(
                (coalesce(cq.transparency_score, 3) * 0.2 +
                 coalesce(ie.interview_experience_score, 3) * 0.25 +
                 coalesce(ie.interview_consistency_score, 3) * 0.15 +
                 coalesce(of.outcome_fairness_score, 3) * 0.2 +
                 coalesce(te.timeline_experience_score, 3) * 0.2)
            , 1) >= 3.5 then 'Good Experience'
            when round(
                (coalesce(cq.transparency_score, 3) * 0.2 +
                 coalesce(ie.interview_experience_score, 3) * 0.25 +
                 coalesce(ie.interview_consistency_score, 3) * 0.15 +
                 coalesce(of.outcome_fairness_score, 3) * 0.2 +
                 coalesce(te.timeline_experience_score, 3) * 0.2)
            , 1) >= 3.0 then 'Average Experience'
            when round(
                (coalesce(cq.transparency_score, 3) * 0.2 +
                 coalesce(ie.interview_experience_score, 3) * 0.25 +
                 coalesce(ie.interview_consistency_score, 3) * 0.15 +
                 coalesce(of.outcome_fairness_score, 3) * 0.2 +
                 coalesce(te.timeline_experience_score, 3) * 0.2)
            , 1) >= 2.0 then 'Below Average Experience'
            else 'Poor Experience'
        end as experience_grade,
        
        -- Improvement suggestions
        case 
            when cq.transparency_score <= 2 then 'Improve feedback transparency; '
            else ''
        end ||
        case 
            when ie.interview_experience_score <= 2 then 'Optimize interview process; '
            else ''
        end ||
        case 
            when te.timeline_experience_score <= 2 then 'Accelerate decision timeline; '
            else ''
        end ||
        case 
            when cj.days_since_last_advancement >= 14 then 'Increase communication frequency; '
            else ''
        end as improvement_recommendations,
        
        -- risk identification
        case 
            when cj.days_since_last_advancement >= 21 and cj.is_archived = false then 'High Abandonment Risk'
            when cj.canceled_interviews >= 2 then 'Poor Interview Experience'
            when cq.transparency_score <= 2 and cj.total_interviews >= 3 then 'Low Process Transparency'
            when te.timeline_experience_score <= 2 and cj.total_lifecycle_days >= 60 then 'Extended Timeline Concern'
            else 'Normal'
        end as experience_risk_flag,
        
        current_timestamp as calculated_at
        
    from candidate_journey cj
    left join communication_quality cq on cj.opportunity_id = cq.opportunity_id
    left join interview_experience ie on cj.opportunity_id = ie.opportunity_id
    left join outcome_fairness of on cj.opportunity_id = of.opportunity_id
    left join timeline_experience te on cj.opportunity_id = te.opportunity_id
)

select * from final
order by overall_candidate_experience_score desc, total_lifecycle_days asc
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 5576 | 764216 | 0 | 0 | 1511 | 1511 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"opportunity_id":"opp10020741500"}</code> |
| K2 | <code>{"opportunity_id":"opp10012841575"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| opportunity_id | 0 | 0 | 758640 | VARCHAR | VARCHAR |
| application_date | 0 | 0 | 758640 | TIMESTAMP | TIMESTAMP |
| archive_reason | 0 | 0 | 758640 | VARCHAR | VARCHAR |
| avg_interview_duration_minutes | 0 | 0 | 758640 | INTEGER | INTEGER |
| avg_recommendation_score | 0 | 0 | 758640 | INTEGER | INTEGER |
| candidate_anxiety_level | 0 | 0 | 758640 | VARCHAR | VARCHAR |
| contact_id | 0 | 0 | 758640 | VARCHAR | VARCHAR |
| contact_name | 0 | 0 | 758640 | VARCHAR | VARCHAR |
| current_stage | 0 | 0 | 758640 | VARCHAR | VARCHAR |
| days_from_application_to_last_advancement | 0 | 0 | 758640 | DOUBLE | DOUBLE |
| days_from_application_to_last_contact | 0 | 0 | 758640 | DOUBLE | DOUBLE |
| days_since_last_advancement | 0 | 0 | 758640 | DOUBLE | DOUBLE |
| experience_grade | 0 | 0 | 758640 | VARCHAR | VARCHAR |
| experience_risk_flag | 0 | 0 | 758640 | VARCHAR | VARCHAR |
| feedback_completion_rate_pct | 0 | 0 | 758640 | INTEGER | INTEGER |
| improvement_recommendations | 5576 | 5576 | 764216 | VARCHAR | VARCHAR |
| interview_burden_category | 0 | 0 | 758640 | VARCHAR | VARCHAR |
| interview_completion_rate_pct | 5576 | 5576 | 764216 | DOUBLE | DOUBLE |
| interview_consistency_score | 0 | 0 | 758640 | INTEGER | INTEGER |
| interview_experience_score | 0 | 0 | 758640 | INTEGER | INTEGER |
| is_archived | 0 | 0 | 758640 | INTEGER | INTEGER |
| outcome_fairness_score | 0 | 0 | 758640 | INTEGER | INTEGER |
| overall_candidate_experience_score | 5576 | 5576 | 764216 | DECIMAL(16,1) | DECIMAL(17,1) |
| process_completeness_assessment | 0 | 0 | 758640 | VARCHAR | VARCHAR |
| response_quality | 0 | 0 | 758640 | VARCHAR | VARCHAR |
| timeline_experience_score | 0 | 0 | 758640 | INTEGER | INTEGER |
| total_interviews | 0 | 0 | 758640 | INTEGER | INTEGER |
| total_lifecycle_days | 0 | 0 | 758640 | DOUBLE | DOUBLE |
| transparency_score | 0 | 0 | 758640 | INTEGER | INTEGER |

opportunity_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"OPP10020741500","rows":3}]</code> | <code>[{"value":"OPP10020741500","rows":243}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

application_date 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":3}]</code> | <code>[{"value":null,"rows":243}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

archive_reason 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":3}]</code> | <code>[{"value":null,"rows":243}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

avg_interview_duration_minutes 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0","rows":3}]</code> | <code>[{"value":"0","rows":243}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

avg_recommendation_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":3}]</code> | <code>[{"value":null,"rows":243}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

candidate_anxiety_level 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Low Anxiety","rows":3}]</code> | <code>[{"value":"Low Anxiety","rows":243}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

contact_id 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"b1f28244-462c-47ee-88b6-8a3afbadf0d3","rows":3}]</code> | <code>[{"value":"b1f28244-462c-47ee-88b6-8a3afbadf0d3","rows":243}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

contact_name 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"William Curry","rows":3}]</code> | <code>[{"value":"William Curry","rows":243}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

current_stage 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Counselling psychologist Interview","rows":3}]</code> | <code>[{"value":"Counselling psychologist Interview","rows":243}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

days_from_application_to_last_advancement 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":3}]</code> | <code>[{"value":null,"rows":243}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

days_from_application_to_last_contact 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":3}]</code> | <code>[{"value":null,"rows":243}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

days_since_last_advancement 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":3}]</code> | <code>[{"value":null,"rows":243}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

experience_grade 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Below Average Experience","rows":3}]</code> | <code>[{"value":"Below Average Experience","rows":243}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

experience_risk_flag 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Normal","rows":3}]</code> | <code>[{"value":"Normal","rows":243}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

feedback_completion_rate_pct 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":3}]</code> | <code>[{"value":null,"rows":243}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

improvement_recommendations 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | <code></code> | <code>Improve feedback transparency; Accelerate decision timeline; </code> |

interview_burden_category 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"No Interviews","rows":3}]</code> | <code>[{"value":"No Interviews","rows":243}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

interview_completion_rate_pct 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | null | -nan |

interview_consistency_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":3}]</code> | <code>[{"value":null,"rows":243}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

interview_experience_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":3}]</code> | <code>[{"value":null,"rows":243}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

is_archived 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0","rows":3}]</code> | <code>[{"value":"0","rows":243}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

outcome_fairness_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":3}]</code> | <code>[{"value":null,"rows":243}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

overall_candidate_experience_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | 2.6 | 2.2 |

process_completeness_assessment 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"In Progress","rows":3}]</code> | <code>[{"value":"In Progress","rows":243}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

response_quality 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"Very Slow Response (&gt;14 days)","rows":3}]</code> | <code>[{"value":"Very Slow Response (&gt;14 days)","rows":243}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

timeline_experience_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"1","rows":3}]</code> | <code>[{"value":"1","rows":243}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

total_interviews 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"0","rows":3}]</code> | <code>[{"value":"0","rows":243}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

total_lifecycle_days 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":null,"rows":3}]</code> | <code>[{"value":null,"rows":243}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

transparency_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | <code>[{"value":"1","rows":3}]</code> | <code>[{"value":"1","rows":243}]</code> |
重复键为同键值/次数，列表位置不是唯一配对。

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>11列；[{"column":"application_date","table_rows":3000}]</code> |
| A3_constant_nonnull_column | <code>14列；[{"column":"is_archived","value":"0"}]</code> |
| A4_equal_columns | <code>2组；[{"columns":["is_archived","total_interviews","avg_interview_duration_minutes"],"nonnull_equal_rows":3000,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>2组；[{"columns":["is_archived","total_interviews","avg_interview_duration_minutes"],"nonnull_equal_rows":3000,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| B6_constant_literal_output | <code>3输出列；[{"column":"timeline_experience_score","expression":["CAST(1 AS INT)"]}]</code> |
| B7_specified_not_read | <code>["intermediate.int_lever__contact_info"]</code> |
| C9_agent_runtime_text | <code>S4:1 current_timestamp；命中数=1</code> |
| C9_gold_runtime_text | <code>S5:282 current_timestamp；命中数=1</code> |
| C9_contract_runtime_text | <code>S3:1960 current timestamp；命中数=1</code> |
| D10_keyword_in_any_result_field | <code>命中数=3；task_instruction_not_agent_report         description: Average overall_candidate_experience_score from lever__candidate_experience_insights across the manager’s candidates; NULL → 0</code> |

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
| 27 | run | <code>grep -E 'ERROR -&#124;Executing: staging&#124;STAGING layer complete' /tmp/run.log</code> | 5620 | true | false |
| 31 | run | <code>sed -n '1,100p' sql/staging/stg_lever__stage.sql; sed -n '1,80p' sql/staging/stg_lever__interview.sql</code> | 2303 | false | false |
| 33 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>for p in Path('sql').rglob('*.sql'):<br> s=p.read_text().replace(' ~* ', ' ~* ')<br> # DuckDB regex case insensitive via regexp_matches(..., 'i')<br> import re<br> s=re.su</code> | 0 | false | false |
| 35 | run | <code>find sql -type f &#124; sort</code> | 2341 | true | false |
| 47 | run | <code>sed -i 's/LEFT JOIN staging.stg_lever__stage s USING(stage_id)/LEFT JOIN staging.stg_lever__stage s ON i.stage_id=s.stage_id/' sql/intermediate/int_lever__interviewer_performance.sql; sed -i 's/GROUP </code> | 1220 | false | false |

### agent action 的 thought/message 命中原句

event 23 / message

```text
'lever__candidate_experience_insights':'''WITH base AS (SELECT cl.*,o.contact_name,o.created_at application_date,o.last_interaction_at,o.last_advanced_at,s.stage_name current_stage,ar.archive_reason_title archive_reason,CASE WHEN cl.total_lifecycle_days<=14 THEN 'Fast' WHEN cl.total_lifecycle_days<=30 THEN 'Standard' WHEN cl.total_lifecycle_days<=60 THEN 'Slow' ELSE 'Very Slow' END lifecycle_speed_category,round(cl.completed_interviews*100.0/nullif(cl.total_interviews,0),1) completion_rate,CASE WHEN cl.feedback_completion_rate_pct>=90 THEN 5 WHEN cl.feedback_completion_rate_pct>=70 THEN 4 WHEN cl.feedback_completion_rate_pct>=50 THEN 3 WHEN cl.feedback_completion_rate_pct>=30 THEN 2 ELSE 1 END transparency_score,CASE WHEN cl.total_interviews=0 THEN NULL WHEN cl.completed_interviews*100.0/nullif(cl.total_interviews,0)>=95 AND cl.avg_interview_duration_minutes BETWEEN 30 AND 90 THEN 5 WHEN cl.completed_interviews*100.0/nullif(cl.total_interviews,0)>=80 AND cl.avg_interview_duration_minutes BETWEEN 20 AND 120 THEN 4 WHEN cl.completed_interviews*100.0/nullif(cl.total_interviews,0)>=60 THEN 3 WHEN cl.completed_interviews*100.0/nullif(cl.total_interviews,0)>=40 THEN 2 ELSE 1 END interview_experience_score,CASE WHEN cl.total_interviews=0 THEN NULL WHEN cl.canceled_interviews=0 THEN 5 WHEN cl.canceled_interviews*1.0/cl.total_interviews<=.1 THEN 4 WHEN cl.canceled_interviews*1.0/cl.total_interviews<=.2 THEN 3 WHEN cl.canceled_interviews*1.0/cl.total_interviews<=.3 THEN 2 ELSE 1 END interview_consistency_score FROM intermediate.int_lever__candidate_lifecycle cl JOIN staging.stg_lever__opportunity o USING(opportunity_id) LEFT JOIN staging.stg_lever__stage s ON o.stage_id=s.stage_id LEFT JOIN staging.stg_lever__archive_reason ar ON o.archived_reason_id=ar.archive_reason_id), calc AS (SELECT *,date_diff('microsecond',application_date,last_interaction_at)/86400000000.0 days_contact,date_diff('microsecond',application_date,last_advanced_at)/86400000000.0 days_advance,CASE WHEN is_archived=0 THEN NULL WHEN lower(coalesce(current_stage,'')) LIKE '%hire%' OR lower(coalesce(current_stage,'')) LIKE '%accept%' OR lower(coalesce(archive_reason,'')) LIKE '%withdraw%' OR lower(coalesce(archive_reason,'')) LIKE '%declin%' THEN 5 WHEN lower(coalesce(current_stage,'')) LIKE '%offer%' OR lower(coalesce(archive_reason,'')) LIKE '%skill%' OR lower(coalesce(archive_reason,'')) LIKE '%qualification%' THEN 4 WHEN archive_reason IS NULL THEN 2 ELSE 3 END outcome_fairness_score FROM base) SELECT opportunity_id,contact_id,contact_name,current_stage,application_date,total_lifecycle_days,is_archived,archive_reason,CASE WHEN days_since_last_advancement<=1 THEN 'Excellent Response (≤1 day)' WHEN days_since_last_advancement<=3 THEN 'Good Response (2-3 days)' WHEN days_since_last_advancement<=7 THEN 'Moderate Response (4-7 days)' WHEN days_since_last_advancement<=14 THEN 'Slow Response (8-14 days)' ELSE 'Very Slow Response (>14 days)' END response_quality,transparency_score,interview_experience_score,CASE WHEN total_interviews=0 THEN 'No Interviews' WHEN total_interviews<=2 AND total_interview_time_minutes<=120 THEN 'Light Process' WHEN total_interviews<=4 AND total_interview_time_minutes<=240 THEN 'Standard Process' WHEN total_interviews<=6 AND total_interview_time_minutes<=360 THEN 'Intensive Process' ELSE 'Heavy Process' END interview_burden_category,interview_consistency_score,outcome_fairness_score,CASE WHEN is_archived=0 THEN 'In Progress' WHEN avg_recommendation_score>=4 AND lower(coalesce(current_stage,'')) NOT LIKE '%hire%' THEN 'Potential Mismatch' WHEN avg_recommendation_score<=2 THEN 'Consistent Outcome' WHEN avg_recommendation_score IS NULL THEN 'Incomplete Process' ELSE 'Normal Process' END process_completeness_assessment,1::INTEGER timeline_experience_score,'Low Anxiety' candidate_anxiety_level,total_interviews,completion_rate interview_completion_rate_pct,avg_interview_duration_minutes,feedback_completion_rate_pct,avg_recommendation_score,days_since_last_advancement,days_contact days_from_application_to_last_contact,days_advance days_from_application_to_last_advancement,round((coalesce(transparency_score,3)*.2+coalesce(interview_experience_score,3)*.25+coalesce(interview_consistency_score,3)*.15+coalesce(outcome_fairness_score,3)*.2+3*.2),1) overall_candidate_experience_score,CASE WHEN round((coalesce(transparency_score,3)*.2+coalesce(interview_experience_score,3)*.25+coalesce(interview_consistency_score,3)*.15+coalesce(outcome_fairness_score,3)*.2+3*.2),1)>=4.5 THEN 'Exceptional Experience' WHEN round((coalesce(transparency_score,3)*.2+coalesce(interview_experience_score,3)*.25+coalesce(interview_consistency_score,3)*.15+coalesce(outcome_fairness_score,3)*.2+3*.2),1)>=4 THEN 'Excellent Experience' WHEN round((coalesce(transparency_score,3)*.2+coalesce(interview_experience_score,3)*.25+coalesce(interview_consistency_score,3)*.15+coalesce(outcome_fairness_score,3)*.2+3*.2),1)>=3.5 THEN 'Good Experience' WHEN round((coalesce(transparency_score,3)*.2+coalesce(interview_experience_score,3)*.25+coalesce(interview_consistency_score,3)*.15+coalesce(outcome_fairness_score,3)*.2+3*.2),1)>=3 THEN 'Average Experience' WHEN round((coalesce(transparency_score,3)*.2+coalesce(interview_experience_score,3)*.25+coalesce(interview_consistency_score,3)*.15+coalesce(outcome_fairness_score,3)*.2+3*.2),1)>=2 THEN 'Below Average Experience' ELSE 'Poor Experience' END experience_grade,'' improvement_recommendations,CASE WHEN days_since_last_advancement>=21 AND is_archived=0 THEN 'High Abandonment Risk' WHEN canceled_interviews>=2 THEN 'Poor Interview Experience' WHEN transparency_score<=2 AND total_interviews>=3 THEN 'Low Process Transparency' WHEN total_lifecycle_days>=60 THEN 'Extended Timeline Concern' ELSE 'Normal' END experience_risk_flag,current_timestamp calculated_at FROM calc''',
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/011_table_alignment.jsonl`
- S2: `records/011_alignment_impl-001.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-001/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/marts/lever__candidate_experience_insights.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/sql/marts/lever__candidate_experience_insights.sql`
- S6: `records/006_contract_impl-001.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/result.md`
- S10: `data/019_packages_work/019_impl-001_lever__candidate_experience_insights/019_impl-001_lever__candidate_experience_insights.json`
- S11: `data/011_agent_alignment/impl-001_attempt_01/lever__candidate_experience_insights_2025-10-27.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/lever.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions`
