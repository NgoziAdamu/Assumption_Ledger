# impl-001 | staging | stg_lever__posting | 差异：S1；日期 原记录

## 契约完整原文

S3:235–303

```yaml
    - name: stg_lever__posting
      description: "Cleaned job postings with validated content, categorization, and publication status"
      source_table: "raw.posting"
      columns:
        - name: posting_id
          data_type: VARCHAR(50)
          constraints: [not_null, unique]
          validation_rules:
            - rule: "posting_id = TRIM(posting_id)"
              on_failure: correct
            - rule: "LENGTH(TRIM(posting_id)) > 0"
              on_failure: delete_row
        - name: posting_title
          data_type: VARCHAR(500)
          constraints: [not_null]
          validation_rules:
            - rule: "posting_title = TRIM(posting_title)"
              on_failure: correct
            - rule: "LENGTH(TRIM(posting_title)) > 0"
              on_failure: delete_row
        - name: state
          data_type: VARCHAR(20)
          constraints: [not_null]
          validation_rules:
            - rule: "state IN ('published', 'draft', 'closed', 'internal')"
              on_failure: delete_row
        - name: requisition_code
          data_type: VARCHAR(20)
          validation_rules:
            - rule: "requisition_code IS NULL OR requisition_code LIKE 'REQ-%'"
              on_failure: nullify_field
        - name: categories_commitment
          data_type: VARCHAR(50)
          validation_rules:
            - rule: "categories_commitment IS NULL OR categories_commitment IN ('full-time', 'part-time', 'contract', 'internship')"
              on_failure: nullify_field
        - name: categories_department
          data_type: VARCHAR(100)
        - name: categories_level
          data_type: VARCHAR(50)
          validation_rules:
            - rule: "categories_level IS NULL OR categories_level IN ('Entry', 'Mid', 'Senior', 'Lead', 'Principal', 'Executive')"
              on_failure: nullify_field
        - name: categories_location
          data_type: VARCHAR(255)
        - name: categories_team
          data_type: VARCHAR(255)
        - name: content_description
          data_type: VARCHAR(5000)
        - name: content_description_html
          data_type: VARCHAR(5000)
        - name: content_closing
          data_type: VARCHAR(5000)
        - name: content_closing_html
          data_type: VARCHAR(5000)
        - name: creator_user_id
          data_type: VARCHAR(50)
          constraints: [not_null]
        - name: owner_user_id
          data_type: VARCHAR(50)
          constraints: [not_null]
        - name: created_at
          data_type: TIMESTAMP
        - name: updated_at
          data_type: TIMESTAMP
          validation_rules:
            - rule: "updated_at IS NULL OR created_at IS NULL OR try_cast(updated_at as timestamp) >= try_cast(created_at as timestamp)"
              on_failure: delete_row

```

## agent 最终 SQL

S4

```sql
WITH typed AS (
    SELECT
        trim(cast(r."id" AS VARCHAR)) AS posting_id,
        trim(cast(r."text" AS VARCHAR)) AS posting_title,
        try_cast(r."state" AS VARCHAR(20)) AS state,
        try_cast(r."requisition_code" AS VARCHAR(20)) AS requisition_code,
        try_cast(r."categories_commitment" AS VARCHAR(50)) AS categories_commitment,
        try_cast(r."categories_department" AS VARCHAR(100)) AS categories_department,
        try_cast(r."categories_level" AS VARCHAR(50)) AS categories_level,
        try_cast(r."categories_location" AS VARCHAR(255)) AS categories_location,
        try_cast(r."categories_team" AS VARCHAR(255)) AS categories_team,
        try_cast(r."content_description" AS VARCHAR(5000)) AS content_description,
        try_cast(r."content_description_html" AS VARCHAR(5000)) AS content_description_html,
        try_cast(r."content_closing" AS VARCHAR(5000)) AS content_closing,
        try_cast(r."content_closing_html" AS VARCHAR(5000)) AS content_closing_html,
        try_cast(r."creator_id" AS VARCHAR(50)) AS creator_user_id,
        try_cast(r."owner_id" AS VARCHAR(50)) AS owner_user_id,
        try_cast(r."created_at" AS TIMESTAMP) AS created_at,
        try_cast(r."updated_at" AS TIMESTAMP) AS updated_at
    FROM raw.posting AS r
),
valid AS (
    SELECT * FROM typed
    WHERE         state IN ('published','draft','closed','internal') AND
              posting_id IS NOT NULL AND
              length(posting_id) > 0 AND
              posting_title IS NOT NULL AND
              state IS NOT NULL AND
              requisition_code LIKE 'REQ-%' AND
              creator_user_id IS NOT NULL AND
              owner_user_id IS NOT NULL
),
ranked AS (
    SELECT *, row_number() OVER (PARTITION BY posting_id ORDER BY posting_id) AS _row_num
    FROM valid
)
SELECT posting_id, posting_title, state, requisition_code, categories_commitment, categories_department, categories_level, categories_location, categories_team, content_description, content_description_html, content_closing, content_closing_html, creator_user_id, owner_user_id, created_at, updated_at
FROM ranked
WHERE _row_num = 1
```

## gold SQL（仅供定位差异）

S5

```sql
-- Standardized cleaning of job posting information (aligned docs/staging_data_specification.yaml)

with cleaned as (
    select
        trim(id) as posting_id,
        trim(text) as posting_title,
        state,
        -- Classification field
        case when categories_commitment in ('full-time','part-time','contract','internship') then categories_commitment else null end as categories_commitment,
        categories_department,
        case when categories_level in ('Entry','Mid','Senior','Lead','Principal','Executive') then categories_level else null end as categories_level,
        categories_location,
        categories_team,

        -- content
        content_description,
        content_description_html,
        content_closing,
        content_closing_html,

        -- foreign key/encoding
        creator_id as creator_user_id,
        owner_id as owner_user_id,
        case when requisition_code is null or requisition_code like 'REQ-%' then requisition_code else null end as requisition_code,

        -- time
        try_cast(created_at as timestamp) as created_at,
        try_cast(updated_at as timestamp) as updated_at
    from raw.posting
), filtered as (
    select * from cleaned
    where
        -- Delete row: primary key/title/creation time
        length(posting_id) > 0
        and length(posting_title) > 0
        -- Relax time filtering: no rows will be lost because created_at is empty
        and state in ('published','draft','closed','internal')
        -- Delete row: foreign key is not empty
        and creator_user_id is not null
        and owner_user_id is not null
        -- Relax time comparisons: only compare when comparable
        and (updated_at is null or created_at is null or updated_at >= created_at)
)

select * from filtered
```

## 差异（L0；沿用 012 选定结果）

| agent 行 | gold 行 | 仅 agent 键 | 仅 gold 键 | agent 重复键组 | gold 重复键组 |
|---|---|---|---|---|---|
| 148 | 148 | 0 | 0 | 0 | 0 |

列值为原始 CAST AS VARCHAR；表格转义仅用于展示换行与分隔符。无共同键的 0 个行对不表示值一致。


样例键映射：

| 键代号 | 完整规范化键 |
|---|---|
| K1 | <code>{"posting_id":"pos15019768628"}</code> |
| K2 | <code>{"posting_id":"pos17599403070"}</code> |

| 列 | 不一致行/最少对数 | agent 未抵消次数 | gold 未抵消次数 | agent 类型 | gold 类型 |
|---|---|---|---|---|---|
| posting_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| posting_title | 0 | 0 | 0 | VARCHAR | VARCHAR |
| state | 0 | 0 | 0 | VARCHAR | VARCHAR |
| categories_commitment | 40 | 40 | 40 | VARCHAR | VARCHAR |
| categories_department | 0 | 0 | 0 | VARCHAR | VARCHAR |
| categories_level | 25 | 25 | 25 | VARCHAR | VARCHAR |
| categories_location | 0 | 0 | 0 | VARCHAR | VARCHAR |
| categories_team | 0 | 0 | 0 | VARCHAR | VARCHAR |
| content_description | 0 | 0 | 0 | VARCHAR | VARCHAR |
| content_description_html | 0 | 0 | 0 | VARCHAR | VARCHAR |
| content_closing | 0 | 0 | 0 | VARCHAR | VARCHAR |
| content_closing_html | 0 | 0 | 0 | VARCHAR | VARCHAR |
| creator_user_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| owner_user_id | 0 | 0 | 0 | VARCHAR | VARCHAR |
| requisition_code | 0 | 0 | 0 | VARCHAR | VARCHAR |

categories_commitment 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K1 | freelance | null |

categories_level 样例：

| 键 | agent 值 | gold 值 |
|---|---|---|
| K2 | Director | null |

独有键样例：

| 仅 agent 原始键 | 仅 gold 原始键 |
|---|---|
| <code>[]</code> | <code>[]</code> |

## 006：仅 agent 违反的约束

未记录违反为 True 的约束。

## 008：仅 True 痕迹与最少证据

| 标记 | 最少证据（多项只列少量例子） |
|---|---|
| A2_all_null_column | <code>2列；[{"column":"created_at","table_rows":148}]</code> |
| D10_keyword_in_any_result_field | <code>命中数=15；task_instruction_not_agent_report         description: Posting state from stg_lever__posting.state; NULL if no posting match.</code> |

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
| 23 | run | <code>cat &gt; /tmp/marts.py &lt;&lt;'PY'<br>from pathlib import Path<br>p=Path('sql/marts')<br>models={<br>'lever__interview_enhanced':'''SELECT iu.canceled_at,iu.created_at,iu.creator_user_id,iu.interview_date,iu.duration,iu.</code> | 0 | false | false |
| 25 | run | <code>cat &gt;&gt; /tmp/marts.py &lt;&lt;'PY'<br>models={<br>'lever__candidate_quality_insights':'''WITH cb AS (SELECT ci.*,a.posting_id,a.referrer_user_id,a.type application_type,p.categories_department,p.categories_level,C</code> | 6312 | true | false |
| 27 | run | <code>grep -E 'ERROR -&#124;Executing: staging&#124;STAGING layer complete' /tmp/run.log</code> | 5620 | true | false |
| 35 | run | <code>find sql -type f &#124; sort</code> | 2341 | true | false |
| 37 | run | <code>sed -i "s/) external FROM cb/) external_avg FROM cb/; s/referred&gt;external+10/referred&gt;external_avg+10/; s/internal&gt;external+10/internal&gt;external_avg+10/" sql/marts/lever__candidate_quality_insights.sq</code> | 2929 | false | false |

### agent action 的 thought/message 命中原句

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
event 23 / message

```text
'lever__posting_enhanced':'''WITH req AS (SELECT posting_id,count(*) count_requisitions FROM staging.stg_lever__requisition_posting GROUP BY posting_id) SELECT p.*,coalesce(r.count_requisitions,0) count_requisitions,coalesce(r.count_requisitions,0)>0 has_requisition,coalesce(a.first_app_sent_at,a.first_app_sent_at) first_app_sent_at,coalesce(a.count_referred_applications,0) count_referred_applications,coalesce(a.count_posting_applications,0) count_posting_applications,coalesce(a.count_manual_user_applications,0) count_manual_user_applications,coalesce(a.count_opportunities,0) count_opportunities,coalesce(a.count_open_opportunities,0) count_open_opportunities,coalesce(i.count_interviews,0) count_interviews,coalesce(i.count_interview_coordinators,0) count_interviewees,t.tags,u.user_name posting_hiring_manager_name FROM staging.stg_lever__posting p LEFT JOIN req r USING(posting_id) LEFT JOIN intermediate.int_lever__posting_applications a USING(posting_id) LEFT JOIN intermediate.int_lever__posting_interviews i USING(posting_id) LEFT JOIN intermediate.int_lever__posting_tags t USING(posting_id) LEFT JOIN staging.stg_lever__user u ON a.posting_hiring_manager_user_id=u.user_id''',
```
event 23 / message

```text
'lever__opportunity_enhanced':'''WITH offer_rank AS (SELECT *,row_number() OVER(PARTITION BY opportunity_id ORDER BY created_at DESC) rn FROM staging.stg_lever__offer) SELECT b.*,s.stage_name current_stage,t.tags,ar.archive_reason_title archive_reason,p.posting_title job_title,p.categories_commitment job_commitment,p.categories_location job_location,p.categories_team job_team,p.state current_state_of_job_posting,(o.offer_id IS NOT NULL) has_offer,o.status current_offer_status FROM intermediate.int_lever__opportunity_contact_info b JOIN staging.stg_lever__stage s USING(stage_id) LEFT JOIN staging.stg_lever__archive_reason ar ON b.archived_reason_id=ar.archive_reason_id LEFT JOIN intermediate.int_lever__opportunity_tags t USING(opportunity_id) LEFT JOIN offer_rank o ON b.opportunity_id=o.opportunity_id AND o.rn=1 LEFT JOIN staging.stg_lever__posting p USING(posting_id)''',
```
event 25 / message

```text
'lever__candidate_quality_insights':'''WITH cb AS (SELECT ci.*,a.posting_id,a.referrer_user_id,a.type application_type,p.categories_department,p.categories_level,CASE WHEN candidate_quality_score>=80 THEN 'Exceptional (80+)' WHEN candidate_quality_score>=60 THEN 'High Quality (60-79)' WHEN candidate_quality_score>=40 THEN 'Good Quality (40-59)' WHEN candidate_quality_score>=20 THEN 'Basic Quality (20-39)' ELSE 'Low Quality (<20)' END quality_segment,CASE WHEN current_stage_order>=5 THEN 'Offer/Hire Stage' WHEN current_stage_order>=3 THEN 'Advanced Interview Stage' WHEN current_stage_order>=2 THEN 'Initial Interview Stage' ELSE 'Early Stage' END funnel_stage_group,CASE WHEN referrer_user_id IS NOT NULL THEN 'Referred' WHEN a.type='user' THEN 'Internal' ELSE 'External' END source_type FROM intermediate.int_lever__candidate_insights ci LEFT JOIN staging.stg_lever__application a USING(opportunity_id) LEFT JOIN staging.stg_lever__posting p USING(posting_id)), src AS (SELECT source_type,avg(candidate_quality_score) avgq,count(*) n,row_number() OVER(ORDER BY avg(candidate_quality_score) DESC) rn FROM cb GROUP BY source_type HAVING count(*)>=5), dep AS (SELECT categories_department,avg(candidate_quality_score) avgq,row_number() OVER(ORDER BY avg(candidate_quality_score) DESC) rn FROM cb WHERE categories_department IS NOT NULL GROUP BY categories_department HAVING count(*)>=5), lvl AS (SELECT categories_level,avg(candidate_quality_score) avgq,row_number() OVER(ORDER BY avg(candidate_quality_score) DESC) rn FROM cb WHERE categories_level IS NOT NULL GROUP BY categories_level HAVING count(*)>=5), summary AS (SELECT count(*) total, count(*) FILTER(WHERE quality_segment='Exceptional (80+)') exceptional,count(*) FILTER(WHERE quality_segment='High Quality (60-79)') highq,count(*) FILTER(WHERE quality_segment='Good Quality (40-59)') goodq,count(*) FILTER(WHERE quality_segment='Basic Quality (20-39)') basicq,count(*) FILTER(WHERE quality_segment='Low Quality (<20)') lowq,round(avg(candidate_quality_score),1) avgq,round(quantile_cont(candidate_quality_score,.5),1) medianq,round(quantile_cont(candidate_quality_score,.75),1) p75,round(avg(total_lifecycle_days) FILTER(WHERE quality_segment IN ('Exceptional (80+)','High Quality (60-79)')),1) highdays,round(avg(total_lifecycle_days) FILTER(WHERE quality_segment IN ('Basic Quality (20-39)','Low Quality (<20)')),1) lowdays,round(avg(interview_completion_rate) FILTER(WHERE quality_segment IN ('Exceptional (80+)','High Quality (60-79)')),1) highrate,round(avg(interview_completion_rate) FILTER(WHERE quality_segment IN ('Basic Quality (20-39)','Low Quality (<20)')),1) lowrate,avg(candidate_quality_score) FILTER(WHERE source_type='Referred') referred,avg(candidate_quality_score) FILTER(WHERE source_type='Internal') internal,avg(candidate_quality_score) FILTER(WHERE source_type='External') external FROM cb) SELECT current_date analysis_date,current_timestamp generated_at,'Candidate Quality Intelligence Report' report_title,total total_candidates_analyzed,exceptional exceptional_candidates,highq high_quality_candidates,goodq good_quality_candidates,basicq basic_quality_candidates,lowq low_quality_candidates,avgq overall_avg_quality_score,medianq median_quality_score,p75 p75_quality_score,(SELECT source_type FROM src WHERE rn=1) best_source_type,round((SELECT avgq FROM src WHERE rn=1),1) best_source_avg_quality,(SELECT categories_department FROM dep WHERE rn=1) best_department,round((SELECT avgq FROM dep WHERE rn=1),1) best_department_avg_quality,(SELECT categories_level FROM lvl WHERE rn=1) best_job_level,round((SELECT avgq FROM lvl WHERE rn=1),1) best_job_level_avg_quality,highdays high_quality_avg_lifecycle_days,lowdays low_quality_avg_lifecycle_days,highrate high_quality_interview_completion_rate,lowrate low_quality_interview_completion_rate,CASE WHEN referred>external+10 THEN 'Referral sources produce higher-quality candidates' WHEN internal>external+10 THEN 'Internal mobility produces higher-quality candidates' ELSE 'No significant source difference' END key_finding_source,CASE WHEN (exceptional+highq)*1.0/nullif(total,0)>=.4 THEN 'Strong candidate quality distribution' WHEN (exceptional+highq)*1.0/nullif(total,0)>=.25 THEN 'Good candidate quality distribution' ELSE 'Opportunity to improve candidate quality' END key_finding_overall,CASE WHEN (SELECT source_type FROM src WHERE rn=1)='Referred' THEN 'Invest in referral programs' WHEN (SELECT source_type FROM src WHERE rn=1)='Internal' THEN 'Promote internal mobility' ELSE 'Optimize external channels' END primary_recommendation,CASE WHEN highdays<lowdays THEN 'Fast-track high-quality candidates' ELSE 'Improve early screening' END process_recommendation FROM summary''',
```
event 37 / message

```text
    FROM staging.stg_lever__posting
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
- S4: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/sql/staging/stg_lever__posting.sql`
- S5: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/sql/staging/stg_lever__posting.sql`
- S6: `records/006_contract_impl-001.json`
- S7: `records/008_table_scan.jsonl`
- S8: `traces/dacomp_deimpl_prev.tar.gz`
- S9: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/result.md`
- S10: `data/019_packages_work/019_impl-001_stg_lever__posting/019_impl-001_stg_lever__posting.json`
- S11: `/home/katherine/dac/runs/20261025_de_official_batch_01/impl-001/agent/dacomp-de-impl-001/lever.duckdb`
- S12: `/home/katherine/dac/benchmarks/dacomp-de-gold/dacomp-de-impl-001/lever.duckdb`
- S13: `data/dacomp_deimpl_prev/runs/20261025_de_official_batch_01/impl-001/agent/.events/sessions`
