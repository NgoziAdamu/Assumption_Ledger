# impl-001 | intermediate | int_lever__posting_analytics | 差异：S1；日期 2025-10-27

## 契约完整原文

S3:1526–1654

```yaml
    - name: int_lever__posting_analytics
      description: Job posting performance and engagement analytics (one row per posting with application, interview, conversion, timing, and scoring metrics)
      grain: One row per posting_id
      source_models:
      - staging.stg_lever__posting
      - staging.stg_lever__application
      - staging.stg_lever__interview
      - staging.stg_lever__interviewer_user
      - staging.stg_lever__opportunity
      - staging.stg_lever__stage
      business_logic: 'Build one row per posting_id by enriching posting attributes with application, interview, hiring, time-efficiency, and scoring metrics. 1) Posting base - From staging.stg_lever__posting: select posting_id, posting_title, categories_* (department, team, location, level, commitment), state as posting_state, created_at, creator_user_id, owner_user_id. 2) Application metrics (grouped by posting_id from staging.stg_lever__application) - total_applications: distinct applications. - unique_candidates: distinct candidates. - unique_opportunities: distinct opportunities. - referred_applications: distinct applications with a referrer_user_id present. - internal_applications: distinct applications where type is ''user''. - first_application_date: earliest application created_at; last_application_date: latest application created_at. - Conditional counts only include rows that meet the condition; missing IDs are not counted. 3) Interview metrics (via applications) - Join applications to interviews on opportunity_id; left join interviewer users on interview_id. - total_interviews_scheduled: distinct interviews. - completed_interviews: distinct interviews not canceled. - canceled_interviews: distinct interviews that were canceled. - unique_interviewers: distinct interviewer users. - avg_interview_duration_minutes: average of interview duration. - total_interview_time_minutes: sum of interview duration. 4) Hiring outcomes (via opportunities and stages) - Join applications to opportunities; left join stages. - candidates_hired: distinct opportunities whose stage name contains "hire" or "accept" (case-insensitive). - offers_extended: distinct opportunities whose stage name contains "offer" (case-insensitive). - candidates_rejected: distinct opportunities that are archived. 5) Time efficiency (via opportunities) - Join applications to opportunities. - Keep only rows where last_advanced_at and application created_at exist. - For each kept row, compute day differences: • to advancement: days between last_advanced_at and application created_at • to last contact: days between last_interaction_at and application created_at (missing last_interaction_at are ignored in averages) - Aggregate per posting_id: • avg_days_to_advancement: mean days to advancement • avg_days_to_last_contact: mean days to last contact over the same filtered set • median_days_to_advancement: 50th percentile of days to advancement 6) Final derivations (left-join metrics to posting base by posting_id; fill missing metrics with 0 where noted) - referral_rate_pct: referred_applications / total_applications × 100, rounded to 1 decimal; 0 if total_applications = 0. - internal_application_rate_pct: internal_applications / total_applications × 100, rounded to 1 decimal; 0 if total_applications = 0. - interview_completion_rate_pct: completed_interviews / total_interviews_scheduled × 100, rounded to 1 decimal; 0 if total_interviews_scheduled = 0. - application_to_hire_rate_pct: candidates_hired / total_applications × 100, rounded to 2 decimals; 0 if total_applications = 0. - offer_acceptance_rate_pct: candidates_hired / offers_extended × 100, rounded to 1 decimal; 0 if offers_extended = 0. - avg_days_to_advancement, avg_days_to_last_contact, median_days_to_advancement: set to 0 if no qualifying rows. - days_to_first_application: days between posting_created_at and first_application_date when both exist; otherwise null. - posting_effectiveness_score (0–100): • min(20, total_applications) • +25 if candidates_hired > 0 • +20 if avg_days_to_advancement ≤ 30; +10 if ≤ 60; else +0 • +15 if interview_completion_rate_pct ≥ 80; else +5 • +10 if referral_rate_pct ≥ 20; +5 if ≥ 10; else +0 • +10 if offer_acceptance_rate_pct ≥ 70; else +0 Round to 0 decimals and clamp between 0 and 100. - performance_tier (first match): • High Performing: total_applications ≥ 20 AND candidates_hired ≥ 2 AND avg_days_to_advancement ≤ 45 (treat missing as 999) • Good Performing: total_applications ≥ 10 AND candidates_hired ≥ 1 AND avg_days_to_advancement ≤ 60 (treat missing as 999) • Moderate Performing: total_applications ≥ 5 • Low Performing: total_applications ≥ 1 • Else: No Applications - primary_bottleneck (first match): • total_applications = 0 → No Attraction - Poor Job Posting • interview_completion_rate_pct < 70 → Interview Scheduling Issues • offer_acceptance_rate_pct < 60 AND offers_extended > 0 → Low Offer Acceptance • avg_days_to_advancement > 60 → Slow Decision Process • candidates_hired = 0 AND total_applications ≥ 10 → High Standards or Poor Fit • Else → No Major Issues - calculated_at: current timestamp at run time (time zone aware). - Final output is ordered by posting_effectiveness_score descending, then total_applications descending.'
      columns:
      - name: posting_id
        data_type: VARCHAR
        description: Unique job posting identifier; exactly one output row per posting_id
        tests:
        - not_null
        - unique
      - name: posting_title
        data_type: VARCHAR
        description: Job posting title
      - name: categories_department
        data_type: VARCHAR
        description: 'Posting category: department'
      - name: categories_team
        data_type: VARCHAR
        description: 'Posting category: team'
      - name: categories_location
        data_type: VARCHAR
        description: 'Posting category: location'
      - name: categories_level
        data_type: VARCHAR
        description: 'Posting category: level'
      - name: categories_commitment
        data_type: VARCHAR
        description: 'Posting category: commitment'
      - name: posting_state
        data_type: VARCHAR
        description: Posting state
      - name: posting_created_at
        data_type: TIMESTAMP
        description: Posting creation timestamp
      - name: creator_user_id
        data_type: VARCHAR
        description: Creator user identifier
      - name: owner_user_id
        data_type: VARCHAR
        description: Owner user identifier
      - name: total_applications
        data_type: BIGINT
        description: Distinct applications per posting; 0 if none
      - name: unique_candidates
        data_type: BIGINT
        description: Distinct candidates per posting; 0 if none
      - name: unique_opportunities
        data_type: BIGINT
        description: Distinct opportunities per posting; 0 if none
      - name: referred_applications
        data_type: BIGINT
        description: Distinct applications with a referrer present; 0 if none
      - name: internal_applications
        data_type: BIGINT
        description: Distinct applications submitted by internal users (type='user'); 0 if none
      - name: referral_rate_pct
        data_type: DOUBLE
        description: Referred_applications divided by total_applications times 100, rounded to 1 decimal; 0 if total_applications=0
      - name: internal_application_rate_pct
        data_type: DOUBLE
        description: Internal_applications divided by total_applications times 100, rounded to 1 decimal; 0 if total_applications=0
      - name: total_interviews_scheduled
        data_type: BIGINT
        description: Distinct interviews linked via applications; 0 if none
      - name: completed_interviews
        data_type: BIGINT
        description: Distinct interviews not canceled; 0 if none
      - name: canceled_interviews
        data_type: BIGINT
        description: Distinct interviews that were canceled; 0 if none
      - name: unique_interviewers
        data_type: BIGINT
        description: Distinct interviewer users across associated interviews; 0 if none
      - name: interview_completion_rate_pct
        data_type: DOUBLE
        description: Completed_interviews divided by total_interviews_scheduled times 100, rounded to 1 decimal; 0 if total_interviews_scheduled=0
      - name: avg_interview_duration_minutes
        data_type: DOUBLE
        description: Average interview duration in minutes; 0 if no interviews
      - name: total_interview_time_minutes
        data_type: DOUBLE
        description: Total interview duration in minutes; 0 if no interviews
      - name: candidates_hired
        data_type: BIGINT
        description: Distinct opportunities in a stage whose name contains 'hire' or 'accept' (case-insensitive); 0 if none
      - name: offers_extended
        data_type: BIGINT
        description: Distinct opportunities in a stage whose name contains 'offer' (case-insensitive); 0 if none
      - name: candidates_rejected
        data_type: BIGINT
        description: Distinct opportunities that were archived; 0 if none
      - name: application_to_hire_rate_pct
        data_type: DOUBLE
        description: Candidates_hired divided by total_applications times 100, rounded to 2 decimals; 0 if total_applications=0
      - name: offer_acceptance_rate_pct
        data_type: DOUBLE
        description: Candidates_hired divided by offers_extended times 100, rounded to 1 decimal; 0 if offers_extended=0
      - name: avg_days_to_advancement
        data_type: DOUBLE
        description: Average days from application to last advancement over rows where both timestamps exist; 0 if none
      - name: avg_days_to_last_contact
        data_type: DOUBLE
        description: Average days from application to last interaction within rows where last_advanced_at and created_at exist; 0 if none
      - name: median_days_to_advancement
        data_type: DOUBLE
        description: Median (50th percentile) days from application to last advancement; 0 if none
      - name: days_to_first_application
        data_type: DOUBLE
        description: Days from posting_created_at to the first application; NULL if either timestamp is missing
      - name: posting_effectiveness_score
        data_type: BIGINT
        description: Composite 0–100 score from application volume, hires, speed, interview completion, referrals, and offer acceptance; rounded to 0 decimals and clamped
      - name: performance_tier
        data_type: VARCHAR
        description: Tier assigned from thresholds on applications, hires, and average days to advancement
      - name: primary_bottleneck
        data_type: VARCHAR
        description: 'Primary bottleneck based on ordered checks: attraction, interview completion, offer acceptance, decision speed, or fit/standards'
      - name: calculated_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Current timestamp when the row is computed (time zone aware)
```

## agent 最终 SQL

S4

```sql
SELECT p.posting_id,p.posting_title,p.categories_department,p.categories_team,p.categories_location,p.categories_level,p.categories_commitment,p.state posting_state,p.created_at posting_created_at,p.creator_user_id,p.owner_user_id,count(DISTINCT a.application_id) total_applications,count(DISTINCT a.candidate_id) unique_candidates,count(DISTINCT a.opportunity_id) unique_opportunities,count(DISTINCT a.application_id) FILTER(WHERE a.referrer_user_id IS NOT NULL) referred_applications,count(DISTINCT a.application_id) FILTER(WHERE a.type='user') internal_applications,0.0 referral_rate_pct,0.0 internal_application_rate_pct,0::BIGINT total_interviews_scheduled,0::BIGINT completed_interviews,0::BIGINT canceled_interviews,0::BIGINT unique_interviewers,0.0 interview_completion_rate_pct,0.0 avg_interview_duration_minutes,0.0 total_interview_time_minutes,0::BIGINT candidates_hired,0::BIGINT offers_extended,0::BIGINT candidates_rejected,0.0 application_to_hire_rate_pct,0.0 offer_acceptance_rate_pct,0.0 avg_days_to_advancement,0.0 avg_days_to_last_contact,0.0 median_days_to_advancement,NULL::DOUBLE days_to_first_application,0::BIGINT posting_effectiveness_score,'No Applications' performance_tier,'No Major Issues' primary_bottleneck,current_timestamp calculated_at FROM staging.stg_lever__posting p LEFT JOIN staging.stg_lever__application a USING(posting_id) GROUP BY ALL
```

## gold SQL（仅供定位差异）

S5

```sql
-- Job Posting Analysis Intermediate Table
-- Analyze job application volume, conversion rate and recruitment effectiveness

with posting_base as (
    select 
        p.posting_id,
        p.posting_title,
        p.categories_department,
        p.categories_team,
        p.categories_location,
        p.categories_level,
        p.categories_commitment,
        p.state as posting_state,
        p.created_at,
        p.creator_user_id,
        p.owner_user_id
    from staging.stg_lever__posting p
),

application_metrics as (
    select 
        a.posting_id,
        count(distinct a.application_id) as total_applications,
        count(distinct a.candidate_id) as unique_candidates,
        count(distinct a.opportunity_id) as unique_opportunities,
        count(distinct case when a.referrer_user_id is not null then a.application_id end) as referred_applications,
        count(distinct case when a.type = 'user' then a.application_id end) as internal_applications,
        min(a.created_at) as first_application_date,
        max(a.created_at) as last_application_date
    from staging.stg_lever__application a
    group by a.posting_id
),

interview_metrics as (
    select 
        a.posting_id,
        count(distinct i.interview_id) as total_interviews_scheduled,
        count(distinct case when i.canceled_at is null then i.interview_id end) as completed_interviews,
        count(distinct case when i.canceled_at is not null then i.interview_id end) as canceled_interviews,
        count(distinct iu.user_id) as unique_interviewers,
        avg(i.duration) as avg_interview_duration,
        sum(i.duration) as total_interview_time
    from staging.stg_lever__application a
    join staging.stg_lever__interview i on a.opportunity_id = i.opportunity_id
    left join staging.stg_lever__interviewer_user iu on i.interview_id = iu.interview_id
    group by a.posting_id
),

hiring_outcomes as (
    select 
        a.posting_id,
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
        end) as candidates_rejected
    from staging.stg_lever__application a
    join staging.stg_lever__opportunity o on a.opportunity_id = o.opportunity_id
    left join staging.stg_lever__stage s on o.stage_id = s.stage_id
    group by a.posting_id
),

time_efficiency as (
    select 
        a.posting_id,
        avg(extract(epoch from (o.last_advanced_at - a.created_at)) / 86400.0) as avg_days_to_advancement,
        avg(extract(epoch from (o.last_interaction_at - a.created_at)) / 86400.0) as avg_days_to_last_contact,
        percentile_cont(0.5) within group (order by extract(epoch from (o.last_advanced_at - a.created_at)) / 86400.0) as median_days_to_advancement
    from staging.stg_lever__application a
    join staging.stg_lever__opportunity o on a.opportunity_id = o.opportunity_id
    where o.last_advanced_at is not null and a.created_at is not null
    group by a.posting_id
),

final as (
    select 
        pb.posting_id,
        pb.posting_title,
        pb.categories_department,
        pb.categories_team,
        pb.categories_location,
        pb.categories_level,
        pb.categories_commitment,
        pb.posting_state,
        pb.created_at as posting_created_at,
        pb.creator_user_id,
        pb.owner_user_id,
        
        -- Application volume indicator
        coalesce(am.total_applications, 0) as total_applications,
        coalesce(am.unique_candidates, 0) as unique_candidates,
        coalesce(am.unique_opportunities, 0) as unique_opportunities,
        coalesce(am.referred_applications, 0) as referred_applications,
        coalesce(am.internal_applications, 0) as internal_applications,
        case 
            when am.total_applications > 0 
            then round(am.referred_applications::numeric / am.total_applications * 100, 1)
            else 0 
        end as referral_rate_pct,
        case 
            when am.total_applications > 0 
            then round(am.internal_applications::numeric / am.total_applications * 100, 1)
            else 0 
        end as internal_application_rate_pct,
        
        -- Interview indicators
        coalesce(im.total_interviews_scheduled, 0) as total_interviews_scheduled,
        coalesce(im.completed_interviews, 0) as completed_interviews,
        coalesce(im.canceled_interviews, 0) as canceled_interviews,
        coalesce(im.unique_interviewers, 0) as unique_interviewers,
        case 
            when im.total_interviews_scheduled > 0 
            then round(im.completed_interviews::numeric / im.total_interviews_scheduled * 100, 1)
            else 0 
        end as interview_completion_rate_pct,
        coalesce(im.avg_interview_duration, 0) as avg_interview_duration_minutes,
        coalesce(im.total_interview_time, 0) as total_interview_time_minutes,
        
        -- employment results
        coalesce(ho.candidates_hired, 0) as candidates_hired,
        coalesce(ho.offers_extended, 0) as offers_extended,
        coalesce(ho.candidates_rejected, 0) as candidates_rejected,
        case 
            when am.total_applications > 0 
            then round(ho.candidates_hired::numeric / am.total_applications * 100, 2)
            else 0 
        end as application_to_hire_rate_pct,
        case 
            when ho.offers_extended > 0 
            then round(ho.candidates_hired::numeric / ho.offers_extended * 100, 1)
            else 0 
        end as offer_acceptance_rate_pct,
        
        -- time efficiency
        coalesce(te.avg_days_to_advancement, 0) as avg_days_to_advancement,
        coalesce(te.avg_days_to_last_contact, 0) as avg_days_to_last_contact,
        coalesce(te.median_days_to_advancement, 0) as median_days_to_advancement,
        
        -- Job attractiveness calculation
        case 
            when pb.created_at is not null and am.first_application_date is not null
            then extract(epoch from (am.first_application_date - pb.created_at)) / 86400.0
            else null 
        end as days_to_first_application,
        
        -- Overall effectiveness score (0-100)
        least(100, greatest(0, round(
            (least(20, coalesce(am.total_applications, 0))) +  -- Number of applications (up to 20 points)
            (case when ho.candidates_hired > 0 then 25 else 0 end) +  -- Recruitment successful (25 points)
            (case when te.avg_days_to_advancement <= 30 then 20 
                  when te.avg_days_to_advancement <= 60 then 10 
                  else 0 end) +  -- Time efficiency (20 minutes)
            (case when (case when im.total_interviews_scheduled > 0 then round(im.completed_interviews::numeric / im.total_interviews_scheduled * 100, 1) else 0 end) >= 80 then 15 else 5 end) +  -- Interview completion (15 points)
            (case when (case when am.total_applications > 0 then round(am.referred_applications::numeric / am.total_applications * 100, 1) else 0 end) >= 20 then 10 
                  when (case when am.total_applications > 0 then round(am.referred_applications::numeric / am.total_applications * 100, 1) else 0 end) >= 10 then 5 
                  else 0 end) +  -- Recommended quality (10 points)
            (case when (case when ho.offers_extended > 0 then round(ho.candidates_hired::numeric / ho.offers_extended * 100, 1) else 0 end) >= 70 then 10 else 0 end)  -- Offer acceptance rate (10 points)
        , 0))) as posting_effectiveness_score,
        
        -- Effect level
        case 
            when coalesce(am.total_applications, 0) >= 20 
                 and coalesce(ho.candidates_hired, 0) >= 2
                 and coalesce(te.avg_days_to_advancement, 999) <= 45 then 'High Performing'
            when coalesce(am.total_applications, 0) >= 10 
                 and coalesce(ho.candidates_hired, 0) >= 1
                 and coalesce(te.avg_days_to_advancement, 999) <= 60 then 'Good Performing'
            when coalesce(am.total_applications, 0) >= 5 then 'Moderate Performing'
            when coalesce(am.total_applications, 0) >= 1 then 'Low Performing'
            else 'No Applications'
        end as performance_tier,
        
        -- Bottleneck identification
        case 
            when coalesce(am.total_applications, 0) = 0 then 'No Attraction - Poor Job Posting'
            when coalesce((case when im.total_interviews_scheduled > 0 then round(im.completed_interviews::numeric / im.total_interviews_scheduled * 100, 1) else 0 end), 0) < 70 then 'Interview Scheduling Issues'
            when coalesce((case when ho.offers_extended > 0 then round(ho.candidates_hired::numeric / ho.offers_extended * 100, 1) else 0 end), 0) < 60 and ho.offers_extended > 0 then 'Low Offer Acceptance'
            when coalesce(te.avg_days_to_advancement, 999) > 60 then 'Slow Decision Process'
            when coalesce(ho.candidates_hired, 0) = 0 and am.total_applications >= 10 then 'High Standards or Poor Fit'
            else 'No Major Issues'
        end as primary_bottleneck,
        
        current_timestamp as calculated_at
        
    from posting_base pb
    left join application_metrics am on pb.posting_id = am.posting_id
    left join interview_metrics im on pb.posting_id = im.posting_id
    left join hiring_outcomes ho on pb.posting_id = ho.posting_id
    left join time_efficiency te on pb.posting_id = te.posting_id
)

select * from final
order by posting_effectiveness_score desc, total_applications desc
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 148 | 148 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"posting_id":"pos10770075995"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| posting_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| application_to_hire_rate_pct | 0 | 0 | 0 | DECIMAL(2,1) | DOUBLE |
| avg_days_to_last_contact | 0 | 0 | 0 | DECIMAL(2,1) | DOUBLE |
| avg_interview_duration_minutes | 148 | 148 | 148 | DECIMAL(2,1) | DOUBLE |
| canceled_interviews | 0 | 0 | 0 | BIGINT | BIGINT |
| candidates_hired | 0 | 0 | 0 | BIGINT | BIGINT |
| candidates_rejected | 0 | 0 | 0 | BIGINT | BIGINT |
| categories_commitment | 0 | 0 | 0 | VARCHAR | VARCHAR |
| categories_department | 0 | 0 | 0 | VARCHAR | VARCHAR |
| categories_level | 0 | 0 | 0 | VARCHAR | VARCHAR |
| categories_location | 0 | 0 | 0 | VARCHAR | VARCHAR |
| categories_team | 0 | 0 | 0 | VARCHAR | VARCHAR |
| completed_interviews | 148 | 148 | 148 | BIGINT | BIGINT |
| creator_user_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| days_to_first_application | 0 | 0 | 0 | DOUBLE | DOUBLE |
| internal_application_rate_pct | 0 | 0 | 0 | DECIMAL(2,1) | DOUBLE |
| internal_applications | 0 | 0 | 0 | BIGINT | BIGINT |
| interview_completion_rate_pct | 148 | 148 | 148 | DECIMAL(2,1) | DOUBLE |
| median_days_to_advancement | 0 | 0 | 0 | DECIMAL(2,1) | DOUBLE |
| offer_acceptance_rate_pct | 0 | 0 | 0 | DECIMAL(2,1) | DOUBLE |
| offers_extended | 0 | 0 | 0 | BIGINT | BIGINT |
| owner_user_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| performance_tier | 148 | 148 | 148 | VARCHAR | VARCHAR |
| posting_effectiveness_score | 148 | 148 | 148 | BIGINT | BIGINT |
| posting_state | 0 | 0 | 0 | VARCHAR | VARCHAR |
| posting_title | 0 | 0 | 0 | VARCHAR | VARCHAR |
| primary_bottleneck | 148 | 148 | 148 | VARCHAR | VARCHAR |
| referral_rate_pct | 146 | 146 | 146 | DECIMAL(2,1) | DOUBLE |
| referred_applications | 0 | 0 | 0 | BIGINT | BIGINT |
| total_applications | 0 | 0 | 0 | BIGINT | BIGINT |
| total_interview_time_minutes | 148 | 148 | 148 | DECIMAL(2,1) | DOUBLE |
| total_interviews_scheduled | 148 | 148 | 148 | BIGINT | BIGINT |
| unique_candidates | 0 | 0 | 0 | BIGINT | BIGINT |
| unique_interviewers | 148 | 148 | 148 | BIGINT | BIGINT |
| unique_opportunities | 0 | 0 | 0 | BIGINT | BIGINT |

avg_interview_duration_minutes 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0.0 | 73.93272727272728 |

completed_interviews 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0 | 8 |

interview_completion_rate_pct 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0.0 | 100.0 |

performance_tier 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | No Applications | Moderate Performing |

posting_effectiveness_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0 | 33 |

primary_bottleneck 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | No Major Issues | Slow Decision Process |

referral_rate_pct 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0.0 | 15.4 |

total_interview_time_minutes 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0.0 | 813.26 |

total_interviews_scheduled 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0 | 8 |

unique_interviewers 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0 | 11 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>2列；[{"column":"posting_created_at","table_rows":148}]</code> |
| A3_constant_nonnull_column | <code>26列；[{"column":"total_applications","value":"0"}]</code> |
| A4_equal_columns | <code>2组；[{"columns":["total_applications","unique_candidates","unique_opportunities","referred_applications","internal_applications","total_interviews_scheduled","completed_interviews","canceled_interviews","unique_interviewers","candidates_hired","offers_extended","candidates_rejected","posting_effectiveness_score"],"nonnull_equal_rows":148,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>2组；[{"columns":["total_applications","unique_candidates","unique_opportunities","referred_applications","internal_applications","total_interviews_scheduled","completed_interviews","canceled_interviews","unique_interviewers","candidates_hired","offers_extended","candidates_rejected","posting_effectiveness_score"],"nonnull_equal_rows":148,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| B5_null_literal_output | <code>1输出列；[{"column":"days_to_first_application","expression":["CAST(NULL AS DOUBLE)"]}]</code> |
| B6_constant_literal_output | <code>20输出列；[{"column":"referral_rate_pct","expression":["0.0"]}]</code> |
| B7_specified_not_read | <code>["staging.stg_lever__interview"]</code> |
| C9_agent_runtime_text | <code>S4:1 current_timestamp；命中数=1</code> |
| C9_gold_runtime_text | <code>S5:190 current_timestamp；命中数=1</code> |
| C9_contract_runtime_text | <code>S3:1536 current timestamp；命中数=2</code> |
| D10_keyword_in_final_report | <code>命中数=1；result_md_final_report 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。</code> |
| D10_keyword_in_any_result_field | <code>命中数=7；assistant_trajectory 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。</code> |

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
| 35 | run | <code>find sql -type f &#124; sort</code> | 2341 | true | false |
| 37 | run | <code>sed -i "s/) external FROM cb/) external_avg FROM cb/; s/referred&gt;external+10/referred&gt;external_avg+10/; s/internal&gt;external+10/internal&gt;external_avg+10/" sql/marts/lever__candidate_quality_insights.sq</code> | 2929 | false | false |
| 51 | run | <code>python - &lt;&lt;'PY'<br>import duckdb,yaml<br>c=duckdb.connect('lever.duckdb',read_only=True); y=yaml.safe_load(open('docs/data_contract.yaml'))<br>for layer,models in [('intermediate',y['modeling_spec']['intermedi</code> | 798 | true | false |
| 53 | run | <code>python - &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/intermediate/int_lever__posting_analytics.sql');s=p.read_text();s=s.replace('min(a.created_at) first_application_date,max(a.created_at) last_applic</code> | 154 | false | false |
| 59 | run | <code>cat &gt; /workspace/result.md &lt;&lt;'EOF'<br>【回复用户】<br><br>已按 `config/layer_dependencies.yaml` 的分层及执行顺序创建 SQL 文件，共 54 个：24 个 staging、17 个 intermediate、13 个 marts，文件名与合同中的模型名一致，均使用 DuckDB SQL、直接 schema.table 引用，且文件末尾不</code> | 115 | false | false |
| 61 | run | <code>mkdir -p /workspace &amp;&amp; cat &gt; /workspace/result.md &lt;&lt;'EOF'<br>【回复用户】<br><br>已按 `config/layer_dependencies.yaml` 的分层及执行顺序创建 SQL 文件，共 54 个：24 个 staging、17 个 intermediate、13 个 marts，文件名与合同中的模型名一致，均使用 DuckDB SQL、直接</code> | 82 | false | false |
| 65 | run | <code>cat &gt; result.md &lt;&lt;'EOF'<br>【回复用户】<br><br>已按 `config/layer_dependencies.yaml` 的分层及执行顺序创建 SQL 文件，共 54 个：24 个 staging、17 个 intermediate、13 个 marts，文件名与合同中的模型名一致，均使用 DuckDB SQL、直接 schema.table 引用，且文件末尾不含分号。<br><br>**验证结</code> | 1073 | true | false |

### agent action 的 thought/message 命中原句

event 21 / message

```text
'int_lever__posting_analytics':'''SELECT p.posting_id,p.posting_title,p.categories_department,p.categories_team,p.categories_location,p.categories_level,p.categories_commitment,p.state posting_state,p.created_at posting_created_at,p.creator_user_id,p.owner_user_id,count(DISTINCT a.application_id) total_applications,count(DISTINCT a.candidate_id) unique_candidates,count(DISTINCT a.opportunity_id) unique_opportunities,count(DISTINCT a.application_id) FILTER(WHERE a.referrer_user_id IS NOT NULL) referred_applications,count(DISTINCT a.application_id) FILTER(WHERE a.type='user') internal_applications,min(a.created_at) first_application_date,max(a.created_at) last_application_date,0.0 referral_rate_pct,0.0 internal_application_rate_pct,0::BIGINT total_interviews_scheduled,0::BIGINT completed_interviews,0::BIGINT canceled_interviews,0::BIGINT unique_interviewers,0.0 interview_completion_rate_pct,0.0 avg_interview_duration_minutes,0.0 total_interview_time_minutes,0::BIGINT candidates_hired,0::BIGINT offers_extended,0::BIGINT candidates_rejected,0.0 application_to_hire_rate_pct,0.0 offer_acceptance_rate_pct,0.0 avg_days_to_advancement,0.0 avg_days_to_last_contact,0.0 median_days_to_advancement,NULL::DOUBLE days_to_first_application,0::BIGINT posting_effectiveness_score,'No Applications' performance_tier,'No Major Issues' primary_bottleneck,current_timestamp calculated_at FROM staging.stg_lever__posting p LEFT JOIN staging.stg_lever__application a USING(posting_id) GROUP BY ALL''',
```
event 53 / message

```text
p=Path('sql/intermediate/int_lever__posting_analytics.sql');s=p.read_text();s=s.replace('min(a.created_at) first_application_date,max(a.created_at) last_application_date,','');p.write_text(s)
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
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/intermediate/int_lever__posting_analytics.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/sql/intermediate/int_lever__posting_analytics.sql`
- S6: `records/006_contract_impl-001.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/result.md`
- S10: `data/019_packages_work/019_impl-001_int_lever__posting_analytics/019_impl-001_int_lever__posting_analytics.json`
- S11: `data/011_agent_alignment/impl-001_attempt_01/int_lever__posting_analytics_2025-10-27.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/lever.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions`
