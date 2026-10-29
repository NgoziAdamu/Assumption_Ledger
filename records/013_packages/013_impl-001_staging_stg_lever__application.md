# impl-001 | staging | stg_lever__application | 差异：S1；日期 原记录

## 契约完整原文

S3:390–428

```yaml
    - name: stg_lever__application
      description: "Cleaned job applications linking candidates to postings with application status and metadata"
      source_table: "raw.application"
      columns:
        - name: application_id
          data_type: VARCHAR(50)
          constraints: [not_null, unique]
        - name: opportunity_id
          data_type: VARCHAR(50)
          constraints: [not_null]
        - name: posting_id
          data_type: VARCHAR(50)
        - name: type
          data_type: VARCHAR(50)
        - name: candidate_id
          data_type: BIGINT
        - name: posting_hiring_manager_user_id
          data_type: VARCHAR(50)
        - name: posting_owner_user_id
          data_type: VARCHAR(50)
        - name: company
          data_type: VARCHAR(255)
        - name: referrer_user_id
          data_type: VARCHAR(50)
        - name: requisition_id
          data_type: VARCHAR(50)
        - name: archived_at
          data_type: TIMESTAMP
          validation_rules:
            - rule: "archived_at IS NULL OR created_at IS NULL OR try_cast(archived_at as timestamp) >= try_cast(created_at as timestamp)"
              on_failure: delete_row
        - name: archived_reason_id
          data_type: VARCHAR(50)
        - name: comments
          data_type: VARCHAR(1000)
        - name: created_at
          data_type: TIMESTAMP
          constraints: [not_null]

```

## agent 最终 SQL

S4

```sql
WITH typed AS (
    SELECT
        try_cast(r."id" AS VARCHAR(50)) AS application_id,
        trim(cast(r."opportunity_id" AS VARCHAR)) AS opportunity_id,
        trim(cast(r."posting_id" AS VARCHAR)) AS posting_id,
        try_cast(r."type" AS VARCHAR(50)) AS type,
        try_cast(r."candidate_id" AS BIGINT) AS candidate_id,
        try_cast(r."posting_hiring_manager_id" AS VARCHAR(50)) AS posting_hiring_manager_user_id,
        try_cast(r."posting_owner_id" AS VARCHAR(50)) AS posting_owner_user_id,
        try_cast(r."company" AS VARCHAR(255)) AS company,
        try_cast(r."referrer_id" AS VARCHAR(50)) AS referrer_user_id,
        trim(cast(r."requisition_for_hire_id" AS VARCHAR)) AS requisition_id,
        try_cast(r."archived_at" AS TIMESTAMP) AS archived_at,
        try_cast(r."archived_reason_id" AS VARCHAR(50)) AS archived_reason_id,
        try_cast(r."comments" AS VARCHAR(1000)) AS comments,
        try_cast(r."created_at" AS TIMESTAMP) AS created_at
    FROM raw.application AS r
),
valid AS (
    SELECT * FROM typed
    WHERE         application_id IS NOT NULL AND
              opportunity_id IS NOT NULL AND
              created_at IS NOT NULL
),
ranked AS (
    SELECT *, row_number() OVER (PARTITION BY application_id ORDER BY application_id) AS _row_num
    FROM valid
)
SELECT application_id, opportunity_id, posting_id, type, candidate_id, posting_hiring_manager_user_id, posting_owner_user_id, company, referrer_user_id, requisition_id, archived_at, archived_reason_id, comments, created_at
FROM ranked
WHERE _row_num = 1
```

## gold SQL（仅供定位差异）

S5

```sql
-- Standardized cleaning of application information (aligned docs/staging_data_specification.yaml)

with cleaned as (
    select
        trim(id) as application_id,
        opportunity_id,
        posting_id,
        type,
        candidate_id,
        posting_hiring_manager_id as posting_hiring_manager_user_id,
        posting_owner_id as posting_owner_user_id,
        trim(company) as company,
        referrer_id as referrer_user_id,
        requisition_for_hire_id as requisition_id,
        try_cast(archived_at as timestamp) as archived_at,
        archived_reason_id,
        comments,
        try_cast(created_at as timestamp) as created_at
    from raw.application
), filtered as (
    select * from cleaned
    where
        -- Delete a row: the primary key is not empty, the opportunity foreign key is not empty, and the creation time is not empty
        length(application_id) > 0
        and opportunity_id is not null
        -- Relax time filtering: do not drop rows because created_at is empty, only compare when comparable
        and (archived_at is null or created_at is null or archived_at >= created_at)
)

select * from filtered
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 0 | 5000 | 0 | 5000 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| application_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| opportunity_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| posting_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| type | 0 | 0 | 0 | VARCHAR | VARCHAR |
| candidate_id | 0 | 0 | 0 | BIGINT | BIGINT |
| posting_hiring_manager_user_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| posting_owner_user_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| company | 0 | 0 | 0 | VARCHAR | VARCHAR |
| referrer_user_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| requisition_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| archived_at | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |
| archived_reason_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| comments | 0 | 0 | 0 | VARCHAR | VARCHAR |
| created_at | 0 | 0 | 0 | TIMESTAMP | TIMESTAMP |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[{"application_id":"APP10000677678"}]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A1_zero_rows | 行数=0 |
| D10_keyword_in_any_result_field | <code>命中数=16；task_instruction_not_agent_report       grain: One row per non-null posting_id with applications in staging.stg_lever__application</code> |

## 轨迹索引（不放输出原文）

本题事件总数：69；归档：S8。

归档事件目录：
- dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions/9cc31938-bae4-46-91fb6609bc30129/events/

| 事件 | 动作 | 命令原文前 200 字符 | 输出字符 | 输出含本表名 | 显式截断 |
|---|---|---|---|---|---|
| 5 | run | <code>pwd &amp;&amp; ls -la &amp;&amp; find sql -maxdepth 3 -type f &#124; sort &#124; head -100 &amp;&amp; cat config/layer_dependencies.yaml</code> | 4500 | true | false |
| 9 | run | <code>sed -n '1,240p' run.py</code> | 9689 | false | false |
| 11 | run | cat lever_start.yaml | 4283 | false | false |
| 17 | run | <code>cat &gt; /tmp/gen.py &lt;&lt;'PY'<br>import yaml, pathlib<br>contract=yaml.safe_load(open('docs/data_contract.yaml'))<br>base=pathlib.Path('sql'); rawmaps={<br>'application':{'application_id':'id','posting_hiring_manager_</code> | 0 | false | false |
| 19 | run | <code>cat &gt; /tmp/models.py &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/intermediate')<br>models={<br>'int_lever__contact_info':'''WITH emails AS (SELECT contact_id, string_agg('&lt;' &#124;&#124; email &#124;&#124; '&gt;', ', ') AS emails</code> | 0 | false | false |
| 21 | run | <code>cat &gt;&gt; /tmp/models.py &lt;&lt;'PY'<br>models={<br>'int_lever__hiring_funnel_metrics':'''WITH sm AS (SELECT stage_id, CASE WHEN lower(stage_name) LIKE '%new%' OR lower(stage_name) LIKE '%lead%' THEN 1 WHEN lower(s</code> | 0 | false | false |
| 25 | run | <code>cat &gt;&gt; /tmp/marts.py &lt;&lt;'PY'<br>models={<br>'lever__candidate_quality_insights':'''WITH cb AS (SELECT ci.*,a.posting_id,a.referrer_user_id,a.type application_type,p.categories_department,p.categories_level,C</code> | 6312 | false | false |
| 27 | run | <code>grep -E 'ERROR -&#124;Executing: staging&#124;STAGING layer complete' /tmp/run.log</code> | 5620 | true | false |
| 35 | run | <code>find sql -type f &#124; sort</code> | 2341 | true | false |
| 37 | run | <code>sed -i "s/) external FROM cb/) external_avg FROM cb/; s/referred&gt;external+10/referred&gt;external_avg+10/; s/internal&gt;external+10/internal&gt;external_avg+10/" sql/marts/lever__candidate_quality_insights.sq</code> | 2929 | false | false |

### agent action 的 thought/message 命中原句

event 19 / message

```text
'int_lever__opportunity_application':'''SELECT o.*, a.application_id, a.comments, a.company, a.posting_hiring_manager_user_id, a.posting_id, a.posting_owner_user_id, a.referrer_user_id, a.requisition_id, a.type AS application_type FROM staging.stg_lever__opportunity o LEFT JOIN staging.stg_lever__application a USING (opportunity_id)''',
```
event 19 / message

```text
'int_lever__posting_applications':'''WITH agg AS (SELECT posting_id, min(created_at) AS first_app_sent_at, count(*) FILTER (WHERE type='referral') AS count_referred_applications, count(*) FILTER (WHERE type IN ('posting','agency')) AS count_posting_applications, count(*) FILTER (WHERE type='user') AS count_manual_user_applications, count(DISTINCT opportunity_id) AS count_opportunities, count(DISTINCT opportunity_id) FILTER (WHERE archived_at IS NULL) AS count_open_opportunities FROM staging.stg_lever__application WHERE posting_id IS NOT NULL GROUP BY posting_id), latest AS (SELECT posting_id, posting_hiring_manager_user_id, row_number() OVER(PARTITION BY posting_id ORDER BY created_at DESC) rn FROM staging.stg_lever__application WHERE posting_id IS NOT NULL) SELECT a.*, l.posting_hiring_manager_user_id FROM agg a JOIN latest l USING(posting_id) WHERE l.rn=1''',
```
event 19 / message

```text
'int_lever__candidate_lifecycle':'''SELECT o.opportunity_id, o.contact_id, a.posting_id, o.stage_id AS current_stage_id, s.stage_name AS current_stage_name, o.archived_at, o.archived_reason_id, o.last_interaction_at, o.last_advanced_at, CASE WHEN o.created_at IS NULL THEN NULL ELSE date_diff('second', o.created_at, coalesce(o.archived_at, current_timestamp)) / 86400.0 END AS total_lifecycle_days, CASE WHEN o.created_at IS NULL THEN NULL ELSE date_diff('second', o.created_at, coalesce(o.last_advanced_at, current_timestamp)) / 86400.0 END AS days_since_last_advancement, 1::INTEGER AS total_stages_passed, CASE WHEN o.created_at IS NULL THEN NULL ELSE date_diff('second',o.created_at,current_timestamp)/86400.0 END AS avg_days_per_stage, 0::INTEGER AS total_interviews, 0::INTEGER AS completed_interviews, 0::INTEGER AS canceled_interviews, 0::INTEGER AS avg_interview_duration_minutes, 0::INTEGER AS total_interview_time_minutes, 0::INTEGER AS total_feedback_count, 0::INTEGER AS completed_feedback_count, NULL::INTEGER AS feedback_completion_rate_pct, NULL::INTEGER AS avg_recommendation_score, NULL::INTEGER AS all_recommendations, CASE WHEN o.archived_at IS NULL THEN 0 ELSE 1 END AS is_archived, CASE WHEN lower(coalesce(s.stage_name,'')) LIKE '%hire%' OR lower(coalesce(s.stage_name,'')) LIKE '%accept%' THEN 1 ELSE 0 END AS is_hired, CASE WHEN lower(coalesce(s.stage_name,'')) LIKE '%offer%' THEN 1 ELSE 0 END AS has_offer, 0::INTEGER AS total_interactions, NULL::INTEGER AS last_interaction_type, 1::INTEGER AS communication_frequency_score, current_timestamp AS calculated_at FROM staging.stg_lever__opportunity o LEFT JOIN staging.stg_lever__application a USING(opportunity_id) LEFT JOIN staging.stg_lever__stage s USING(stage_id)''',
```
event 21 / message

```text
'int_lever__hiring_funnel_metrics':'''WITH sm AS (SELECT stage_id, CASE WHEN lower(stage_name) LIKE '%new%' OR lower(stage_name) LIKE '%lead%' THEN 1 WHEN lower(stage_name) LIKE '%screen%' OR lower(stage_name) LIKE '%phone%' THEN 2 WHEN lower(stage_name) LIKE '%technical%' OR lower(stage_name) LIKE '%coding%' THEN 3 WHEN lower(stage_name) LIKE '%onsite%' OR lower(stage_name) LIKE '%final%' THEN 4 WHEN lower(stage_name) LIKE '%offer%' THEN 5 WHEN lower(stage_name) LIKE '%hire%' OR lower(stage_name) LIKE '%accept%' THEN 6 ELSE 99 END stage_order FROM staging.stg_lever__stage), oh AS (SELECT h.opportunity_id, max(sm.stage_order) max_stage, min(h.updated_at) FILTER(WHERE sm.stage_order=1) t1,min(h.updated_at) FILTER(WHERE sm.stage_order=2) t2,min(h.updated_at) FILTER(WHERE sm.stage_order=3) t3,min(h.updated_at) FILTER(WHERE sm.stage_order=4) t4,min(h.updated_at) FILTER(WHERE sm.stage_order=5) t5,min(h.updated_at) FILTER(WHERE sm.stage_order=6) t6 FROM staging.stg_lever__opportunity_stage_history h JOIN sm USING(stage_id) GROUP BY h.opportunity_id), ag AS (SELECT a.posting_id,p.posting_title,p.categories_department,p.categories_team,p.categories_level,p.categories_location,count(DISTINCT a.opportunity_id) total_applications,count(DISTINCT a.opportunity_id) FILTER(WHERE oh.max_stage>=2) screening,count(DISTINCT a.opportunity_id) FILTER(WHERE oh.max_stage>=3) technical,count(DISTINCT a.opportunity_id) FILTER(WHERE oh.max_stage>=4) final,count(DISTINCT a.opportunity_id) FILTER(WHERE oh.max_stage>=5) offer,count(DISTINCT a.opportunity_id) FILTER(WHERE oh.max_stage>=6) hired,avg(date_diff('microsecond',oh.t1,oh.t2)/86400000000.0) dscreen,avg(date_diff('microsecond',oh.t2,oh.t3)/86400000000.0) dtech,avg(date_diff('microsecond',oh.t1,oh.t6)/86400000000.0) dhire FROM staging.stg_lever__application a JOIN staging.stg_lever__posting p USING(posting_id) LEFT JOIN oh USING(opportunity_id) GROUP BY ALL), rates AS (SELECT *,round(screening*100.0/nullif(total_applications,0),2) r1,round(technical*100.0/nullif(screening,0),2) r2,round(final*100.0/nullif(technical,0),2) r3,round(offer*100.0/nullif(final,0),2) r4,round(hired*100.0/nullif(offer,0),2) r5,round(hired*100.0/nullif(total_applications,0),2) rh FROM ag) SELECT posting_id,posting_title,categories_department,categories_team,categories_level,categories_location,total_applications,screening AS reached_screening_count,technical AS reached_technical_count,final AS reached_final_count,offer AS reached_offer_count,hired AS reached_hired_count,coalesce(r1,0.0) application_to_screening_rate,coalesce(r2,0.0) screening_to_technical_rate,coalesce(r3,0.0) technical_to_final_rate,coalesce(r4,0.0) final_to_offer_rate,coalesce(r5,0.0) offer_to_hired_rate,coalesce(rh,0.0) application_to_hired_rate,round(dscreen,1) avg_days_to_screening,round(dtech,1) avg_days_screening_to_technical,round(dhire,1) avg_total_days_to_hire,CASE WHEN coalesce(rh,0)>=10 THEN 'High Efficiency (≥10%)' WHEN coalesce(rh,0)>=5 THEN 'Medium Efficiency (5–10%)' WHEN coalesce(rh,0)>=2 THEN 'Low Efficiency (2–5%)' ELSE 'Very Low Efficiency (<2%)' END hiring_efficiency_grade,CASE WHEN coalesce(r1,0)<50 THEN 'Initial Screening Bottleneck' WHEN coalesce(r2,0)<60 THEN 'Technical Assessment Bottleneck' WHEN coalesce(r3,0)<70 THEN 'Final Interview Bottleneck' WHEN coalesce(r4,0)<80 THEN 'Offer Decision Bottleneck' WHEN coalesce(r5,0)<70 THEN 'Offer Acceptance Bottleneck' ELSE 'No Major Bottleneck' END primary_bottleneck,current_timestamp calculated_at FROM rates WHERE total_applications>=3''',
```
event 21 / message

```text
'int_lever__posting_analytics':'''SELECT p.posting_id,p.posting_title,p.categories_department,p.categories_team,p.categories_location,p.categories_level,p.categories_commitment,p.state posting_state,p.created_at posting_created_at,p.creator_user_id,p.owner_user_id,count(DISTINCT a.application_id) total_applications,count(DISTINCT a.candidate_id) unique_candidates,count(DISTINCT a.opportunity_id) unique_opportunities,count(DISTINCT a.application_id) FILTER(WHERE a.referrer_user_id IS NOT NULL) referred_applications,count(DISTINCT a.application_id) FILTER(WHERE a.type='user') internal_applications,min(a.created_at) first_application_date,max(a.created_at) last_application_date,0.0 referral_rate_pct,0.0 internal_application_rate_pct,0::BIGINT total_interviews_scheduled,0::BIGINT completed_interviews,0::BIGINT canceled_interviews,0::BIGINT unique_interviewers,0.0 interview_completion_rate_pct,0.0 avg_interview_duration_minutes,0.0 total_interview_time_minutes,0::BIGINT candidates_hired,0::BIGINT offers_extended,0::BIGINT candidates_rejected,0.0 application_to_hire_rate_pct,0.0 offer_acceptance_rate_pct,0.0 avg_days_to_advancement,0.0 avg_days_to_last_contact,0.0 median_days_to_advancement,NULL::DOUBLE days_to_first_application,0::BIGINT posting_effectiveness_score,'No Applications' performance_tier,'No Major Issues' primary_bottleneck,current_timestamp calculated_at FROM staging.stg_lever__posting p LEFT JOIN staging.stg_lever__application a USING(posting_id) GROUP BY ALL''',
```
event 21 / message

```text
'int_lever__posting_performance':'''SELECT p.posting_id,p.posting_title,p.categories_department,p.categories_team,p.categories_location,p.categories_level,p.categories_commitment,p.state posting_state,p.created_at posting_created_at,p.creator_user_id,p.owner_user_id,p.requisition_code,count(DISTINCT a.application_id) total_applications,count(DISTINCT a.candidate_id) unique_candidates,count(DISTINCT a.opportunity_id) unique_opportunities,min(a.created_at) first_application_date,max(a.created_at) last_application_date,count(DISTINCT a.application_id) FILTER(WHERE a.referrer_user_id IS NOT NULL) referred_applications,count(DISTINCT a.application_id) FILTER(WHERE a.type='user') internal_applications,count(DISTINCT a.application_id) FILTER(WHERE a.type='candidate') external_applications,0.0 referral_rate,NULL::DOUBLE days_to_first_application,0::BIGINT candidates_reached_interview,0::BIGINT candidates_reached_offer,0::BIGINT candidates_hired,0::BIGINT active_candidates_30d,0::BIGINT archived_candidates,0::BIGINT candidates_with_email,0::BIGINT candidates_with_phone,0::BIGINT candidates_with_resume,0::BIGINT total_interviews_scheduled,0::BIGINT completed_interviews,0::BIGINT canceled_interviews,0.0 interview_completion_rate,0.0 avg_interviews_per_candidate,0.0 application_to_interview_rate,0.0 application_to_offer_rate,0.0 application_to_hire_rate,0.0 offer_to_hire_rate,NULL::DOUBLE posting_performance_score,'No Applications' performance_tier,'Unknown Status' posting_status_analysis,current_timestamp calculated_at FROM staging.stg_lever__posting p LEFT JOIN staging.stg_lever__application a USING(posting_id) GROUP BY ALL'''
```
event 25 / message

```text
'lever__candidate_quality_insights':'''WITH cb AS (SELECT ci.*,a.posting_id,a.referrer_user_id,a.type application_type,p.categories_department,p.categories_level,CASE WHEN candidate_quality_score>=80 THEN 'Exceptional (80+)' WHEN candidate_quality_score>=60 THEN 'High Quality (60-79)' WHEN candidate_quality_score>=40 THEN 'Good Quality (40-59)' WHEN candidate_quality_score>=20 THEN 'Basic Quality (20-39)' ELSE 'Low Quality (<20)' END quality_segment,CASE WHEN current_stage_order>=5 THEN 'Offer/Hire Stage' WHEN current_stage_order>=3 THEN 'Advanced Interview Stage' WHEN current_stage_order>=2 THEN 'Initial Interview Stage' ELSE 'Early Stage' END funnel_stage_group,CASE WHEN referrer_user_id IS NOT NULL THEN 'Referred' WHEN a.type='user' THEN 'Internal' ELSE 'External' END source_type FROM intermediate.int_lever__candidate_insights ci LEFT JOIN staging.stg_lever__application a USING(opportunity_id) LEFT JOIN staging.stg_lever__posting p USING(posting_id)), src AS (SELECT source_type,avg(candidate_quality_score) avgq,count(*) n,row_number() OVER(ORDER BY avg(candidate_quality_score) DESC) rn FROM cb GROUP BY source_type HAVING count(*)>=5), dep AS (SELECT categories_department,avg(candidate_quality_score) avgq,row_number() OVER(ORDER BY avg(candidate_quality_score) DESC) rn FROM cb WHERE categories_department IS NOT NULL GROUP BY categories_department HAVING count(*)>=5), lvl AS (SELECT categories_level,avg(candidate_quality_score) avgq,row_number() OVER(ORDER BY avg(candidate_quality_score) DESC) rn FROM cb WHERE categories_level IS NOT NULL GROUP BY categories_level HAVING count(*)>=5), summary AS (SELECT count(*) total, count(*) FILTER(WHERE quality_segment='Exceptional (80+)') exceptional,count(*) FILTER(WHERE quality_segment='High Quality (60-79)') highq,count(*) FILTER(WHERE quality_segment='Good Quality (40-59)') goodq,count(*) FILTER(WHERE quality_segment='Basic Quality (20-39)') basicq,count(*) FILTER(WHERE quality_segment='Low Quality (<20)') lowq,round(avg(candidate_quality_score),1) avgq,round(quantile_cont(candidate_quality_score,.5),1) medianq,round(quantile_cont(candidate_quality_score,.75),1) p75,round(avg(total_lifecycle_days) FILTER(WHERE quality_segment IN ('Exceptional (80+)','High Quality (60-79)')),1) highdays,round(avg(total_lifecycle_days) FILTER(WHERE quality_segment IN ('Basic Quality (20-39)','Low Quality (<20)')),1) lowdays,round(avg(interview_completion_rate) FILTER(WHERE quality_segment IN ('Exceptional (80+)','High Quality (60-79)')),1) highrate,round(avg(interview_completion_rate) FILTER(WHERE quality_segment IN ('Basic Quality (20-39)','Low Quality (<20)')),1) lowrate,avg(candidate_quality_score) FILTER(WHERE source_type='Referred') referred,avg(candidate_quality_score) FILTER(WHERE source_type='Internal') internal,avg(candidate_quality_score) FILTER(WHERE source_type='External') external FROM cb) SELECT current_date analysis_date,current_timestamp generated_at,'Candidate Quality Intelligence Report' report_title,total total_candidates_analyzed,exceptional exceptional_candidates,highq high_quality_candidates,goodq good_quality_candidates,basicq basic_quality_candidates,lowq low_quality_candidates,avgq overall_avg_quality_score,medianq median_quality_score,p75 p75_quality_score,(SELECT source_type FROM src WHERE rn=1) best_source_type,round((SELECT avgq FROM src WHERE rn=1),1) best_source_avg_quality,(SELECT categories_department FROM dep WHERE rn=1) best_department,round((SELECT avgq FROM dep WHERE rn=1),1) best_department_avg_quality,(SELECT categories_level FROM lvl WHERE rn=1) best_job_level,round((SELECT avgq FROM lvl WHERE rn=1),1) best_job_level_avg_quality,highdays high_quality_avg_lifecycle_days,lowdays low_quality_avg_lifecycle_days,highrate high_quality_interview_completion_rate,lowrate low_quality_interview_completion_rate,CASE WHEN referred>external+10 THEN 'Referral sources produce higher-quality candidates' WHEN internal>external+10 THEN 'Internal mobility produces higher-quality candidates' ELSE 'No significant source difference' END key_finding_source,CASE WHEN (exceptional+highq)*1.0/nullif(total,0)>=.4 THEN 'Strong candidate quality distribution' WHEN (exceptional+highq)*1.0/nullif(total,0)>=.25 THEN 'Good candidate quality distribution' ELSE 'Opportunity to improve candidate quality' END key_finding_overall,CASE WHEN (SELECT source_type FROM src WHERE rn=1)='Referred' THEN 'Invest in referral programs' WHEN (SELECT source_type FROM src WHERE rn=1)='Internal' THEN 'Promote internal mobility' ELSE 'Optimize external channels' END primary_recommendation,CASE WHEN highdays<lowdays THEN 'Fast-track high-quality candidates' ELSE 'Improve early screening' END process_recommendation FROM summary''',
```
event 25 / message

```text
'lever__hiring_dashboard':'''WITH j AS (SELECT a.*,o.created_at opportunity_created,o.last_interaction_at,o.last_advanced_at,s.stage_name FROM staging.stg_lever__application a LEFT JOIN staging.stg_lever__opportunity o USING(opportunity_id) LEFT JOIN staging.stg_lever__stage s USING(stage_id)), b AS (SELECT current_date report_date,current_timestamp generated_at,'Executive Hiring Dashboard' dashboard_title,count(DISTINCT application_id) FILTER(WHERE created_at>=current_date-INTERVAL '30 days' AND created_at<current_date+INTERVAL '1 day') applications_last_30_days,count(DISTINCT candidate_id) FILTER(WHERE created_at>=current_date-INTERVAL '30 days' AND created_at<current_date+INTERVAL '1 day') candidates_last_30_days,count(DISTINCT opportunity_id) FILTER(WHERE lower(coalesce(stage_name,'')) LIKE '%hire%' AND last_advanced_at>=current_date-INTERVAL '30 days') hires_last_30_days,avg(date_diff('microsecond',opportunity_created,last_interaction_at)/86400000000.0) FILTER(WHERE opportunity_created IS NOT NULL AND last_interaction_at IS NOT NULL) avg_candidate_lifecycle_days FROM j) SELECT * FROM b''',
```
event 25 / message

```text
'lever__hiring_dashboard_simple':'''SELECT current_date report_date,current_timestamp generated_at,'Executive Hiring Dashboard' dashboard_title,count(*) total_applications FROM staging.stg_lever__application''',
```
event 25 / message

```text
'lever__hiring_dashboard_working':'''WITH j AS (SELECT a.*,o.created_at opportunity_created,o.last_interaction_at,o.last_advanced_at,s.stage_name FROM staging.stg_lever__application a LEFT JOIN staging.stg_lever__opportunity o USING(opportunity_id) LEFT JOIN staging.stg_lever__stage s USING(stage_id)) SELECT current_date report_date,current_timestamp generated_at,'Executive Hiring Dashboard' dashboard_title,count(DISTINCT application_id) FILTER(WHERE created_at>=current_date-INTERVAL '30 days') applications_last_30_days,count(DISTINCT candidate_id) FILTER(WHERE created_at>=current_date-INTERVAL '30 days') candidates_last_30_days,count(DISTINCT opportunity_id) FILTER(WHERE lower(coalesce(stage_name,'')) LIKE '%hire%' AND last_advanced_at>=current_date-INTERVAL '30 days') hires_last_30_days,avg(date_diff('microsecond',opportunity_created,last_interaction_at)/86400000000.0) FILTER(WHERE opportunity_created IS NOT NULL AND last_interaction_at IS NOT NULL) avg_candidate_lifecycle_days FROM j''',
```
event 25 / message

```text
'lever__recruitment_analytics_dashboard':'''SELECT current_date report_date,current_timestamp report_generated_at,'Monthly Recruitment Analytics Dashboard' report_title,count(DISTINCT application_id) total_applications,count(DISTINCT candidate_id) total_candidates,count(DISTINCT posting_id) total_postings,100::INTEGER recruitment_health_score,'Good' recruitment_health_grade FROM staging.stg_lever__application''',
```
event 37 / message

```text
    FROM staging.stg_lever__application
```
event 37 / message

```text
    FROM staging.stg_lever__posting p LEFT JOIN staging.stg_lever__application a USING(posting_id)
```

## result.md 本表名原句

原文件未出现本表名。

## 原始文件路径（集中列一次）

仓库相对路径基准：`/home/katherine/Assumption_Ledger`。

- S1: `records/007_tolerance_tables.jsonl`
- S2: `records/004_staging_impl-001.json`
- S3: `/home/katherine/dac/benchmarks/dacomp-de/dacomp-de-impl-001/docs/data_contract.yaml`
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__application.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/sql/staging/stg_lever__application.sql`
- S6: `records/006_contract_impl-001.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/result.md`
- S10: `records/012_packages/012_impl-001_staging_stg_lever__application.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/lever.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/lever.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions`
