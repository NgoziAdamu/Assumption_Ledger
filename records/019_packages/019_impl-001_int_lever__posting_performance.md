# impl-001 | intermediate | int_lever__posting_performance | 差异：S1；日期 2025-10-27

## 契约完整原文

S3:1712–1857

```yaml
    - name: int_lever__posting_performance
      description: Job posting performance metrics by posting, including applications, candidates, interviews, conversion rates, score, and status
      grain: One row per posting_id
      source_models:
      - staging.stg_lever__posting
      - staging.stg_lever__application
      - staging.stg_lever__opportunity
      - staging.stg_lever__stage
      - staging.stg_lever__contact_email
      - staging.stg_lever__contact_phone
      - staging.stg_lever__resume
      - staging.stg_lever__interview
      business_logic: 'For each posting in staging.stg_lever__posting: - Left join applications on posting_id; left join opportunities on application.opportunity_id; left join contact_email/phone on opportunity.contact_id; left join resume on application.opportunity_id; left join interview on application.opportunity_id. - All counting metrics use unique counts to avoid double-counting from joins. - Application metrics: - total_applications = unique applications; unique_candidates = unique candidates; unique_opportunities = unique opportunities. - first_application_date = earliest application.created_at; last_application_date = latest application.created_at; both null when no applications. - referred_applications = unique applications with a referrer. - internal_applications = unique applications where type is user; external_applications = unique applications where type is candidate. - referral_rate = if total_applications > 0 then referred_applications ÷ total_applications × 100, rounded to 2 decimals; otherwise 0. - Time metric: - days_to_first_application = fractional days between posting_created_at and first_application_date; computed only when both timestamps can be parsed; otherwise null. - Stage-based candidate metrics (stage membership determined by stage_name keywords, case-insensitive): - Interview-like: stage_name contains interview, technical, or onsite; Offer-like: contains offer; Hire-like: contains hire or accept. - candidates_reached_interview/offer/hired = unique opportunities currently in the corresponding stage group. - active_candidates_30d = unique opportunities with last_interaction_at within the last 30 days relative to the query date (unparsable timestamps are ignored). - archived_candidates = unique opportunities with archived_at present. - candidates_with_email/phone/resume = unique opportunities where the linked contact has an email/phone, or a resume exists, respectively. - Interview efficiency: - total_interviews_scheduled = unique interviews; completed_interviews = unique interviews not canceled; canceled_interviews = unique interviews canceled. - interview_completion_rate = if any interviews then completed ÷ scheduled × 100, rounded to 1 decimal; otherwise 0. - avg_interviews_per_candidate = if any opportunities then scheduled interviews ÷ unique_opportunities, rounded to 1 decimal; otherwise 0. - Conversion rates: - application_to_interview/offer/hire_rate = if total_applications > 0 then (unique opportunities reaching interview/offer/hire ÷ total_applications) × 100, rounded to 2 decimals; otherwise 0. - offer_to_hire_rate = if any offers then (unique opportunities reaching hire ÷ unique opportunities reaching offer) × 100, rounded to 2 decimals; otherwise 0. - Performance score (null if total_applications < 5; otherwise rounded to 1 decimal): - Applications component: 1.25 points per application capped at 25. - Hire presence: +25 if any hire-like opportunity exists; else +0. - Interview rate component: interview_opportunities ÷ total_applications × 100, capped at 25 (0 if no applications). - Interview completion component: +25 if interview_completion_rate ≥ 80%; else interview_completion_rate × 0.3125. - Sum the four components and round to 1 decimal. - Performance tier: - If total_applications = 0 → No Applications. - Else if total_applications < 5 → Low Volume. - Else if any hire-like opportunity and total_applications ≥ 10 → High Performing. - Else if any offer-like opportunity and total_applications ≥ 5 → Moderate Performing. - Else if any interview-like opportunity → Building Pipeline. - Else → Needs Attention. - Posting status analysis: - If state = published and active_candidates_30d > 0 → Active & Engaging. - Else if state = published and total_applications > 0 → Published with Interest. - Else if state = published → Published but No Interest. - Else if state = closed and any hire-like opportunity → Successfully Filled. - Else if state = closed → Closed without Hire. - Else → Unknown Status. - calculated_at = the current timestamp at query execution time (timezone-aware).'
      columns:
      - name: posting_id
        data_type: VARCHAR
        description: Posting identifier; grouping key with exactly one output row per posting_id
        tests:
        - not_null
        - unique
      - name: posting_title
        data_type: VARCHAR
        description: Posting title from stg_lever__posting.posting_title
      - name: categories_department
        data_type: VARCHAR
        description: Department category from stg_lever__posting.categories_department
      - name: categories_team
        data_type: VARCHAR
        description: Team category from stg_lever__posting.categories_team
      - name: categories_location
        data_type: VARCHAR
        description: Location category from stg_lever__posting.categories_location
      - name: categories_level
        data_type: VARCHAR
        description: Level category from stg_lever__posting.categories_level
      - name: categories_commitment
        data_type: VARCHAR
        description: Commitment category from stg_lever__posting.categories_commitment
      - name: posting_state
        data_type: VARCHAR
        description: Posting state from stg_lever__posting.state with no transformation
      - name: posting_created_at
        data_type: TIMESTAMP
        description: Posting creation timestamp from stg_lever__posting.created_at
      - name: creator_user_id
        data_type: VARCHAR
        description: Creator user identifier from stg_lever__posting.creator_user_id
      - name: owner_user_id
        data_type: VARCHAR
        description: Owner user identifier from stg_lever__posting.owner_user_id
      - name: requisition_code
        data_type: VARCHAR
        description: Requisition code from stg_lever__posting.requisition_code
      - name: total_applications
        data_type: BIGINT
        description: Number of unique applications linked to the posting; join duplicates do not inflate the count
      - name: unique_candidates
        data_type: BIGINT
        description: Number of unique candidates across applications for the posting
      - name: unique_opportunities
        data_type: BIGINT
        description: Number of unique opportunities across applications for the posting
      - name: first_application_date
        data_type: TIMESTAMP
        description: Earliest application.created_at for the posting; null if no applications
      - name: last_application_date
        data_type: TIMESTAMP
        description: Latest application.created_at for the posting; null if no applications
      - name: referred_applications
        data_type: BIGINT
        description: Number of unique applications with a non-null referrer
      - name: internal_applications
        data_type: BIGINT
        description: Number of unique applications where application type is user
      - name: external_applications
        data_type: BIGINT
        description: Number of unique applications where application type is candidate
      - name: referral_rate
        data_type: DOUBLE
        description: Percentage of applications that were referred, rounded to 2 decimals; returns 0 when there are no applications
      - name: days_to_first_application
        data_type: DOUBLE
        description: Fractional days between posting_created_at and first_application_date; null when either timestamp is missing or unparsable
      - name: candidates_reached_interview
        data_type: BIGINT
        description: Unique opportunities in an interview-like stage (stage_name contains interview, technical, or onsite; case-insensitive)
      - name: candidates_reached_offer
        data_type: BIGINT
        description: Unique opportunities in an offer-like stage (stage_name contains offer; case-insensitive)
      - name: candidates_hired
        data_type: BIGINT
        description: Unique opportunities in a hire-like stage (stage_name contains hire or accept; case-insensitive)
      - name: active_candidates_30d
        data_type: BIGINT
        description: Unique opportunities with last_interaction_at within the last 30 days relative to the query date; unparsable timestamps are ignored
      - name: archived_candidates
        data_type: BIGINT
        description: Unique opportunities where archived_at is present
      - name: candidates_with_email
        data_type: BIGINT
        description: Unique opportunities whose linked contact has a non-null email
      - name: candidates_with_phone
        data_type: BIGINT
        description: Unique opportunities whose linked contact has a non-null phone number
      - name: candidates_with_resume
        data_type: BIGINT
        description: Unique opportunities with a non-null resume
      - name: total_interviews_scheduled
        data_type: BIGINT
        description: Number of unique interviews linked via opportunity_id
      - name: completed_interviews
        data_type: BIGINT
        description: Unique interviews that were not canceled
      - name: canceled_interviews
        data_type: BIGINT
        description: Unique interviews that were canceled
      - name: interview_completion_rate
        data_type: DOUBLE
        description: Percentage of scheduled interviews that were completed, rounded to 1 decimal; returns 0 when none are scheduled
      - name: avg_interviews_per_candidate
        data_type: DOUBLE
        description: Average interviews per opportunity (scheduled interviews ÷ unique_opportunities), rounded to 1 decimal; returns 0 when none
      - name: application_to_interview_rate
        data_type: DOUBLE
        description: Percentage of applications that reached an interview-like stage, rounded to 2 decimals; returns 0 when there are no applications
      - name: application_to_offer_rate
        data_type: DOUBLE
        description: Percentage of applications that reached an offer-like stage, rounded to 2 decimals; returns 0 when there are no applications
      - name: application_to_hire_rate
        data_type: DOUBLE
        description: Percentage of applications that reached a hire-like stage, rounded to 2 decimals; returns 0 when there are no applications
      - name: offer_to_hire_rate
        data_type: DOUBLE
        description: Percentage of offered opportunities that converted to hire, rounded to 2 decimals; returns 0 when there are no offers
      - name: posting_performance_score
        data_type: DOUBLE
        description: 'Null when total_applications < 5; otherwise sum of: applications (1.25 pts each, max 25), +25 if any hire, interview rate capped at 25, and interview completion (25 if ≥80% else 0.3125 per percentage point), rounded to 1 decimal'
      - name: performance_tier
        data_type: VARCHAR
        description: 'Tier by thresholds: No Applications, Low Volume, High Performing, Moderate Performing, Building Pipeline, or Needs Attention'
      - name: posting_status_analysis
        data_type: VARCHAR
        description: Status derived from posting_state, recent activity, applications, and hire presence using the stated rules
      - name: calculated_at
        data_type: TIMESTAMP WITH TIME ZONE
        description: Timestamp when the row was computed at query time (timezone-aware)
```

## agent 最终 SQL

S4

```sql
SELECT p.posting_id,p.posting_title,p.categories_department,p.categories_team,p.categories_location,p.categories_level,p.categories_commitment,p.state posting_state,p.created_at posting_created_at,p.creator_user_id,p.owner_user_id,p.requisition_code,count(DISTINCT a.application_id) total_applications,count(DISTINCT a.candidate_id) unique_candidates,count(DISTINCT a.opportunity_id) unique_opportunities,min(a.created_at) first_application_date,max(a.created_at) last_application_date,count(DISTINCT a.application_id) FILTER(WHERE a.referrer_user_id IS NOT NULL) referred_applications,count(DISTINCT a.application_id) FILTER(WHERE a.type='user') internal_applications,count(DISTINCT a.application_id) FILTER(WHERE a.type='candidate') external_applications,0.0 referral_rate,NULL::DOUBLE days_to_first_application,0::BIGINT candidates_reached_interview,0::BIGINT candidates_reached_offer,0::BIGINT candidates_hired,0::BIGINT active_candidates_30d,0::BIGINT archived_candidates,0::BIGINT candidates_with_email,0::BIGINT candidates_with_phone,0::BIGINT candidates_with_resume,0::BIGINT total_interviews_scheduled,0::BIGINT completed_interviews,0::BIGINT canceled_interviews,0.0 interview_completion_rate,0.0 avg_interviews_per_candidate,0.0 application_to_interview_rate,0.0 application_to_offer_rate,0.0 application_to_hire_rate,0.0 offer_to_hire_rate,NULL::DOUBLE posting_performance_score,'No Applications' performance_tier,'Unknown Status' posting_status_analysis,current_timestamp calculated_at FROM staging.stg_lever__posting p LEFT JOIN staging.stg_lever__application a USING(posting_id) GROUP BY ALL
```

## gold SQL（仅供定位差异）

S5

```sql
-- Simplified posting performance analysis table
-- Analyzes each posting's recruitment effectiveness

select
    p.posting_id,
    p.posting_title,
    p.categories_department,
    p.categories_team,
    p.categories_location,
    p.categories_level,
    p.categories_commitment,
    p.state as posting_state,
    p.created_at as posting_created_at,
    p.creator_user_id,
    p.owner_user_id,
    p.requisition_code,

    -- Application metrics
    count(distinct a.application_id) as total_applications,
    count(distinct a.candidate_id) as unique_candidates,
    count(distinct a.opportunity_id) as unique_opportunities,
    min(a.created_at) as first_application_date,
    max(a.created_at) as last_application_date,
    count(distinct case when a.referrer_user_id is not null then a.application_id end) as referred_applications,
    count(distinct case when a.type = 'user' then a.application_id end) as internal_applications,
    count(distinct case when a.type = 'candidate' then a.application_id end) as external_applications,
    case
        when count(distinct a.application_id) > 0
        then round(count(distinct case when a.referrer_user_id is not null then a.application_id end)::numeric / count(distinct a.application_id) * 100, 2)
        else 0
    end as referral_rate,

    -- Time metrics
    case
        when p.created_at is not null and min(a.created_at) is not null
        then extract(epoch from (try_cast(min(a.created_at) as timestamp) - try_cast(p.created_at as timestamp))) / 86400.0
        else null
    end as days_to_first_application,

    -- Candidate quality metrics
    count(distinct case when o.stage_id in (
        select stage_id from staging.stg_lever__stage
        where lower(stage_name) like '%interview%'
           or lower(stage_name) like '%technical%'
           or lower(stage_name) like '%onsite%'
    ) then a.opportunity_id end) as candidates_reached_interview,

    count(distinct case when o.stage_id in (
        select stage_id from staging.stg_lever__stage
        where lower(stage_name) like '%offer%'
    ) then a.opportunity_id end) as candidates_reached_offer,

    count(distinct case when o.stage_id in (
        select stage_id from staging.stg_lever__stage
        where lower(stage_name) like '%hire%'
           or lower(stage_name) like '%accept%'
    ) then a.opportunity_id end) as candidates_hired,

    count(distinct case when try_cast(o.last_interaction_at as timestamp) >= current_date - interval '30 days' then a.opportunity_id end) as active_candidates_30d,
    count(distinct case when o.archived_at is not null then a.opportunity_id end) as archived_candidates,

    count(distinct case when ce.email is not null then a.opportunity_id end) as candidates_with_email,
    count(distinct case when cph.phone_number is not null then a.opportunity_id end) as candidates_with_phone,
    count(distinct case when r.resume_id is not null then a.opportunity_id end) as candidates_with_resume,

    -- Interview efficiency metrics
    count(distinct i.interview_id) as total_interviews_scheduled,
    count(distinct case when i.canceled_at is null then i.interview_id end) as completed_interviews,
    count(distinct case when i.canceled_at is not null then i.interview_id end) as canceled_interviews,
    case
        when count(distinct i.interview_id) > 0
        then round(count(distinct case when i.canceled_at is null then i.interview_id end)::numeric / count(distinct i.interview_id) * 100, 1)
        else 0
    end as interview_completion_rate,
    case
        when count(distinct a.opportunity_id) > 0
        then round(count(distinct i.interview_id)::numeric / count(distinct a.opportunity_id), 1)
        else 0
    end as avg_interviews_per_candidate,

    -- Conversion rates
    case
        when count(distinct a.application_id) > 0
        then round(count(distinct case when o.stage_id in (
            select stage_id from staging.stg_lever__stage
            where lower(stage_name) like '%interview%'
               or lower(stage_name) like '%technical%'
               or lower(stage_name) like '%onsite%'
        ) then a.opportunity_id end)::numeric / count(distinct a.application_id) * 100, 2)
        else 0
    end as application_to_interview_rate,

    case
        when count(distinct a.application_id) > 0
        then round(count(distinct case when o.stage_id in (
            select stage_id from staging.stg_lever__stage
            where lower(stage_name) like '%offer%'
        ) then a.opportunity_id end)::numeric / count(distinct a.application_id) * 100, 2)
        else 0
    end as application_to_offer_rate,

    case
        when count(distinct a.application_id) > 0
        then round(count(distinct case when o.stage_id in (
            select stage_id from staging.stg_lever__stage
            where lower(stage_name) like '%hire%'
               or lower(stage_name) like '%accept%'
        ) then a.opportunity_id end)::numeric / count(distinct a.application_id) * 100, 2)
        else 0
    end as application_to_hire_rate,

    case
        when count(distinct case when o.stage_id in (
            select stage_id from staging.stg_lever__stage
            where lower(stage_name) like '%offer%'
        ) then a.opportunity_id end) > 0
        then round(count(distinct case when o.stage_id in (
            select stage_id from staging.stg_lever__stage
            where lower(stage_name) like '%hire%'
               or lower(stage_name) like '%accept%'
        ) then a.opportunity_id end)::numeric / count(distinct case when o.stage_id in (
            select stage_id from staging.stg_lever__stage
            where lower(stage_name) like '%offer%'
        ) then a.opportunity_id end) * 100, 2)
        else 0
    end as offer_to_hire_rate,

    -- Performance scoring
    case
        when count(distinct a.application_id) >= 5
        then round(
            (case when count(distinct a.application_id) >= 20 then 25 else count(distinct a.application_id) * 1.25 end) +
            (case when count(distinct case when o.stage_id in (
                select stage_id from staging.stg_lever__stage
                where lower(stage_name) like '%hire%'
                   or lower(stage_name) like '%accept%'
            ) then a.opportunity_id end) > 0 then 25 else 0 end) +
            (case when count(distinct a.application_id) > 0 then least(25, (count(distinct case when o.stage_id in (
                select stage_id from staging.stg_lever__stage
                where lower(stage_name) like '%interview%'
                   or lower(stage_name) like '%technical%'
                   or lower(stage_name) like '%onsite%'
            ) then a.opportunity_id end)::numeric / count(distinct a.application_id) * 100)) else 0 end) +
            (case when count(distinct i.interview_id) > 0 and round(count(distinct case when i.canceled_at is null then i.interview_id end)::numeric / count(distinct i.interview_id) * 100, 1) >= 80 then 25 else round(count(distinct case when i.canceled_at is null then i.interview_id end)::numeric / count(distinct i.interview_id) * 100, 1) * 0.3125 end), 1)
        else null
    end as posting_performance_score,

    -- Performance tier
    case
        when count(distinct a.application_id) = 0 then 'No Applications'
        when count(distinct a.application_id) < 5 then 'Low Volume'
        when count(distinct case when o.stage_id in (
            select stage_id from staging.stg_lever__stage
            where lower(stage_name) like '%hire%'
               or lower(stage_name) like '%accept%'
        ) then a.opportunity_id end) > 0 and count(distinct a.application_id) >= 10 then 'High Performing'
        when count(distinct case when o.stage_id in (
            select stage_id from staging.stg_lever__stage
            where lower(stage_name) like '%offer%'
        ) then a.opportunity_id end) > 0 and count(distinct a.application_id) >= 5 then 'Moderate Performing'
        when count(distinct case when o.stage_id in (
            select stage_id from staging.stg_lever__stage
            where lower(stage_name) like '%interview%'
               or lower(stage_name) like '%technical%'
               or lower(stage_name) like '%onsite%'
        ) then a.opportunity_id end) > 0 then 'Building Pipeline'
        else 'Needs Attention'
    end as performance_tier,

    -- Posting status analysis
    case
        when p.state = 'published' and count(distinct case when try_cast(o.last_interaction_at as timestamp) >= current_date - interval '30 days' then a.opportunity_id end) > 0 then 'Active & Engaging'
        when p.state = 'published' and count(distinct a.application_id) > 0 then 'Published with Interest'
        when p.state = 'published' then 'Published but No Interest'
        when p.state = 'closed' and count(distinct case when o.stage_id in (
            select stage_id from staging.stg_lever__stage
            where lower(stage_name) like '%hire%'
               or lower(stage_name) like '%accept%'
        ) then a.opportunity_id end) > 0 then 'Successfully Filled'
        when p.state = 'closed' then 'Closed without Hire'
        else 'Unknown Status'
    end as posting_status_analysis,

    current_timestamp as calculated_at

from staging.stg_lever__posting p
left join staging.stg_lever__application a on p.posting_id = a.posting_id
left join staging.stg_lever__opportunity o on a.opportunity_id = o.opportunity_id
left join staging.stg_lever__contact_email ce on o.contact_id = ce.contact_id
left join staging.stg_lever__contact_phone cph on o.contact_id = cph.contact_id
left join staging.stg_lever__resume r on a.opportunity_id = r.opportunity_id
left join staging.stg_lever__interview i on a.opportunity_id = i.opportunity_id
group by p.posting_id, p.posting_title, p.categories_department, p.categories_team, p.categories_location, p.categories_level, p.categories_commitment, p.state, p.created_at, p.creator_user_id, p.owner_user_id, p.requisition_code
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
| active_candidates_30d | 0 | 0 | 0 | BIGINT | BIGINT |
| application_to_hire_rate | 0 | 0 | 0 | DECIMAL(2,1) | DOUBLE |
| application_to_interview_rate | 148 | 148 | 148 | DECIMAL(2,1) | DOUBLE |
| application_to_offer_rate | 0 | 0 | 0 | DECIMAL(2,1) | DOUBLE |
| archived_candidates | 0 | 0 | 0 | BIGINT | BIGINT |
| canceled_interviews | 0 | 0 | 0 | BIGINT | BIGINT |
| candidates_hired | 0 | 0 | 0 | BIGINT | BIGINT |
| candidates_reached_interview | 148 | 148 | 148 | BIGINT | BIGINT |
| candidates_reached_offer | 0 | 0 | 0 | BIGINT | BIGINT |
| candidates_with_email | 148 | 148 | 148 | BIGINT | BIGINT |
| candidates_with_phone | 148 | 148 | 148 | BIGINT | BIGINT |
| candidates_with_resume | 148 | 148 | 148 | BIGINT | BIGINT |
| categories_commitment | 0 | 0 | 0 | VARCHAR | VARCHAR |
| categories_department | 0 | 0 | 0 | VARCHAR | VARCHAR |
| categories_level | 0 | 0 | 0 | VARCHAR | VARCHAR |
| categories_location | 0 | 0 | 0 | VARCHAR | VARCHAR |
| categories_team | 0 | 0 | 0 | VARCHAR | VARCHAR |
| completed_interviews | 148 | 148 | 148 | BIGINT | BIGINT |
| creator_user_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| days_to_first_application | 0 | 0 | 0 | DOUBLE | DOUBLE |
| external_applications | 0 | 0 | 0 | BIGINT | BIGINT |
| first_application_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| internal_applications | 0 | 0 | 0 | BIGINT | BIGINT |
| interview_completion_rate | 148 | 148 | 148 | DECIMAL(2,1) | DOUBLE |
| last_application_date | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| offer_to_hire_rate | 0 | 0 | 0 | DECIMAL(2,1) | DOUBLE |
| owner_user_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| performance_tier | 148 | 148 | 148 | VARCHAR | VARCHAR |
| posting_performance_score | 148 | 148 | 148 | DOUBLE | DOUBLE |
| posting_state | 0 | 0 | 0 | VARCHAR | VARCHAR |
| posting_status_analysis | 80 | 80 | 80 | VARCHAR | VARCHAR |
| posting_title | 0 | 0 | 0 | VARCHAR | VARCHAR |
| referral_rate | 146 | 146 | 146 | DECIMAL(2,1) | DOUBLE |
| referred_applications | 0 | 0 | 0 | BIGINT | BIGINT |
| requisition_code | 0 | 0 | 0 | VARCHAR | VARCHAR |
| total_applications | 0 | 0 | 0 | BIGINT | BIGINT |
| total_interviews_scheduled | 148 | 148 | 148 | BIGINT | BIGINT |
| unique_candidates | 0 | 0 | 0 | BIGINT | BIGINT |
| unique_opportunities | 0 | 0 | 0 | BIGINT | BIGINT |

application_to_interview_rate 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0.0 | 100.0 |

candidates_reached_interview 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0 | 13 |

candidates_with_email 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0 | 13 |

candidates_with_phone 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0 | 13 |

candidates_with_resume 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0 | 9 |

completed_interviews 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0 | 8 |

interview_completion_rate 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0.0 | 100.0 |

performance_tier 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | No Applications | Building Pipeline |

posting_performance_score 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | null | 66.3 |

posting_status_analysis 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | Unknown Status | Published with Interest |

referral_rate 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0.0 | 15.38 |

total_interviews_scheduled 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | 0 | 8 |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>5列；[{"column":"posting_created_at","table_rows":148}]</code> |
| A3_constant_nonnull_column | <code>27列；[{"column":"total_applications","value":"0"}]</code> |
| A4_equal_columns | <code>2组；[{"columns":["total_applications","unique_candidates","unique_opportunities","referred_applications","internal_applications","external_applications","candidates_reached_interview","candidates_reached_offer","candidates_hired","active_candidates_30d","archived_candidates","candidates_with_email","candidates_with_phone","candidates_with_resume","total_interviews_scheduled","completed_interviews","canceled_interviews"],"nonnull_equal_rows":148,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| A4_equal_columns_different_description_texts | <code>2组；[{"columns":["total_applications","unique_candidates","unique_opportunities","referred_applications","internal_applications","external_applications","candidates_reached_interview","candidates_reached_offer","candidates_hired","active_candidates_30d","archived_candidates","candidates_with_email","candidates_with_phone","candidates_with_resume","total_interviews_scheduled","completed_interviews","canceled_interviews"],"nonnull_equal_rows":148,"meaning_status":"description_texts_differ_no_semantic_judgment"}]</code> |
| B5_null_literal_output | <code>2输出列；[{"column":"days_to_first_application","expression":["CAST(NULL AS DOUBLE)"]}]</code> |
| B6_constant_literal_output | <code>20输出列；[{"column":"referral_rate","expression":["0.0"]}]</code> |
| B7_specified_not_read | <code>["staging.stg_lever__contact_email"]</code> |
| C9_agent_runtime_text | <code>S4:1 current_timestamp；命中数=1</code> |
| C9_gold_runtime_text | <code>S5:59 current_date；命中数=3</code> |
| C9_contract_runtime_text | <code>S3:1724 current timestamp；命中数=1</code> |
| D10_keyword_in_final_report | <code>命中数=1；result_md_final_report 本版本已经可以完整运行，但并非每个复杂指标都完全实现了合同的全部业务逻辑：`int_lever__posting_analytics`、`int_lever__posting_performance`、`int_lever__interviewer_performance`、`lever__departmental_hiring_trends` 和 `lever__hiring_manager_scorecard` 中部分复杂关联、指标及分类使用了简化逻辑或占位值。</code> |
| D10_keyword_in_any_result_field | <code>命中数=10；task_instruction_not_agent_report         description: Average posting_performance_score from int_lever__posting_performance across the manager’s postings; NULL → 0</code> |

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
| 59 | run | <code>cat &gt; /workspace/result.md &lt;&lt;'EOF'<br>【回复用户】<br><br>已按 `config/layer_dependencies.yaml` 的分层及执行顺序创建 SQL 文件，共 54 个：24 个 staging、17 个 intermediate、13 个 marts，文件名与合同中的模型名一致，均使用 DuckDB SQL、直接 schema.table 引用，且文件末尾不</code> | 115 | false | false |
| 61 | run | <code>mkdir -p /workspace &amp;&amp; cat &gt; /workspace/result.md &lt;&lt;'EOF'<br>【回复用户】<br><br>已按 `config/layer_dependencies.yaml` 的分层及执行顺序创建 SQL 文件，共 54 个：24 个 staging、17 个 intermediate、13 个 marts，文件名与合同中的模型名一致，均使用 DuckDB SQL、直接</code> | 82 | false | false |
| 65 | run | <code>cat &gt; result.md &lt;&lt;'EOF'<br>【回复用户】<br><br>已按 `config/layer_dependencies.yaml` 的分层及执行顺序创建 SQL 文件，共 54 个：24 个 staging、17 个 intermediate、13 个 marts，文件名与合同中的模型名一致，均使用 DuckDB SQL、直接 schema.table 引用，且文件末尾不含分号。<br><br>**验证结</code> | 1073 | true | false |

### agent action 的 thought/message 命中原句

event 21 / message

```text
'int_lever__posting_performance':'''SELECT p.posting_id,p.posting_title,p.categories_department,p.categories_team,p.categories_location,p.categories_level,p.categories_commitment,p.state posting_state,p.created_at posting_created_at,p.creator_user_id,p.owner_user_id,p.requisition_code,count(DISTINCT a.application_id) total_applications,count(DISTINCT a.candidate_id) unique_candidates,count(DISTINCT a.opportunity_id) unique_opportunities,min(a.created_at) first_application_date,max(a.created_at) last_application_date,count(DISTINCT a.application_id) FILTER(WHERE a.referrer_user_id IS NOT NULL) referred_applications,count(DISTINCT a.application_id) FILTER(WHERE a.type='user') internal_applications,count(DISTINCT a.application_id) FILTER(WHERE a.type='candidate') external_applications,0.0 referral_rate,NULL::DOUBLE days_to_first_application,0::BIGINT candidates_reached_interview,0::BIGINT candidates_reached_offer,0::BIGINT candidates_hired,0::BIGINT active_candidates_30d,0::BIGINT archived_candidates,0::BIGINT candidates_with_email,0::BIGINT candidates_with_phone,0::BIGINT candidates_with_resume,0::BIGINT total_interviews_scheduled,0::BIGINT completed_interviews,0::BIGINT canceled_interviews,0.0 interview_completion_rate,0.0 avg_interviews_per_candidate,0.0 application_to_interview_rate,0.0 application_to_offer_rate,0.0 application_to_hire_rate,0.0 offer_to_hire_rate,NULL::DOUBLE posting_performance_score,'No Applications' performance_tier,'Unknown Status' posting_status_analysis,current_timestamp calculated_at FROM staging.stg_lever__posting p LEFT JOIN staging.stg_lever__application a USING(posting_id) GROUP BY ALL'''
```
event 37 / message

```text
    LEFT JOIN intermediate.int_lever__posting_performance pp USING(posting_id)
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
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/intermediate/int_lever__posting_performance.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/sql/intermediate/int_lever__posting_performance.sql`
- S6: `records/006_contract_impl-001.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/result.md`
- S10: `data/019_packages_work/019_impl-001_int_lever__posting_performance/019_impl-001_int_lever__posting_performance.json`
- S11: `data/011_agent_alignment/impl-001_attempt_01/int_lever__posting_performance_2025-10-27.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/lever.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions`
